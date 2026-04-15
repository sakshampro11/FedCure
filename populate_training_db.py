"""
Populate the FedCure database with training rounds by submitting hospital
weights through the actual REST API.

simulate_training.py only saves .pt files - it skips the API entirely so
the database never gets TrainingRound records. This script fixes that by:
  1. Loading the global model on each round
  2. Training it locally on each hospital's CSV split
  3. Submitting weights through /api/training/submit-weights (x4 per round)
     - the server runs FedAvg + writes TrainingRound + ModelVersion to DB

Run once. The server must be running at localhost:8000.
"""

import numpy as np
import pandas as pd
import requests
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

SERVER_URL = "http://localhost:8000"
NUM_ROUNDS = 10
EPOCHS_PER_ROUND = 3
HOSPITAL_DATA = [
    "data/hospital_1.csv",
    "data/hospital_2.csv",
    "data/hospital_3.csv",
    "data/hospital_4.csv",
]


class HeartDiseaseModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(11, 32), nn.BatchNorm1d(32), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(32, 16), nn.BatchNorm1d(16), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(16, 1), nn.Sigmoid()
        )

    def forward(self, x):
        return self.network(x)


def load_hospital_data(path):
    df = pd.read_csv(path)
    X = df.drop("target", axis=1).values.astype(np.float32)
    y = df["target"].values.astype(np.float32).reshape(-1, 1)
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    return X, y


def train_local(model, X, y, epochs=3):
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)
    loader = DataLoader(TensorDataset(X_t, y_t), batch_size=32, shuffle=True)
    opt = optim.Adam(model.parameters(), lr=0.0005, weight_decay=0.01)
    criterion = nn.BCELoss()
    model.train()
    for _ in range(epochs):
        for bx, by in loader:
            opt.zero_grad()
            loss = criterion(model(bx), by)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
    model.eval()
    with torch.no_grad():
        preds = model(X_t)
        acc = ((preds >= 0.5).float() == y_t).float().mean().item()
    return acc


def get_global_weights():
    r = requests.get(f"{SERVER_URL}/api/training/global-model", timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["weights"], data["version"]


def submit_weights(hospital_id, weights, accuracy):
    payload = {
        "hospital_id": hospital_id,
        "weights": weights,
        "local_accuracy": accuracy,
    }
    r = requests.post(
        f"{SERVER_URL}/api/training/submit-weights",
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def main():
    print("=" * 60)
    print("  FedCure - Populate Training DB via API")
    print(f"  {NUM_ROUNDS} rounds x {len(HOSPITAL_DATA)} hospitals")
    print("=" * 60)

    hospital_datasets = []
    for path in HOSPITAL_DATA:
        X, y = load_hospital_data(path)
        hospital_datasets.append((X, y))
        print(f"[DATA] {path}: {len(X)} samples")

    print()

    for round_num in range(1, NUM_ROUNDS + 1):
        print(f"--- Round {round_num}/{NUM_ROUNDS} ---")

        global_weights, version = get_global_weights()
        print(f"  Global model: {version}")

        for h_idx, (X_h, y_h) in enumerate(hospital_datasets):
            hospital_id = h_idx + 1

            model = HeartDiseaseModel()
            state = {k: torch.tensor(v, dtype=torch.float32)
                     for k, v in global_weights.items()}
            for k, v in model.state_dict().items():
                if not v.is_floating_point() and k in state:
                    state[k] = state[k].long()
            model.load_state_dict(state)

            acc = train_local(model, X_h, y_h, epochs=EPOCHS_PER_ROUND)

            weights = {}
            for name, param in model.state_dict().items():
                if param.is_floating_point():
                    weights[name] = (param + torch.randn_like(param) * 0.01).tolist()
                else:
                    weights[name] = param.tolist()

            result = submit_weights(hospital_id, weights, acc)
            status = result.get("status", "?")
            print(f"  Hospital {hospital_id}: acc={acc:.4f}  [{status}]")

            if status == "aggregated":
                msg = result.get("message", "")
                print(f"  [OK] FedAvg complete: {msg}")

        print()

    print("=" * 60)
    print("  Done! Training rounds are now in the database.")
    print("  Refresh your dashboard to see the accuracy chart.")
    print("=" * 60)


if __name__ == "__main__":
    main()
