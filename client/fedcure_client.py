"""
FedCure FL Client — Hospital-side federated learning client.

Hospitals run this script to participate in federated training rounds.
On each round, the client:
  1. Downloads the current global model from the FedCure server
  2. Trains locally on its own data subset
  3. Adds differential privacy noise to the weights
  4. Submits updated weights back to the server

Configuration via environment variables:
  SERVER_URL     — FedCure API base URL (default: http://localhost:8000)
  API_KEY        — Hospital API key (required)
  HOSPITAL_ID    — Hospital identifier (required)
  NUM_ROUNDS     — Number of FL rounds to participate in (default: 5)
  EPOCHS_PER_ROUND — Local training epochs per round (default: 3)

Usage:
  set API_KEY=your-api-key
  set HOSPITAL_ID=1
  python fedcure_client.py
"""

import os
import sys
import time
import requests
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY")
HOSPITAL_ID = os.getenv("HOSPITAL_ID")
NUM_ROUNDS = int(os.getenv("NUM_ROUNDS", "5"))
EPOCHS_PER_ROUND = int(os.getenv("EPOCHS_PER_ROUND", "3"))

# ──────────────────────────────────────────────
# Model (must match server's HeartDiseaseModel)
# ──────────────────────────────────────────────

class HeartDiseaseModel(nn.Module):
    """Same architecture as the server — 13 → 128 → 64 → 32 → 1 with Sigmoid."""

    def __init__(self):
        super(HeartDiseaseModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(13, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.network(x)


# ──────────────────────────────────────────────
# Data Loading & Preprocessing
# ──────────────────────────────────────────────

def load_and_preprocess_data(data_path=None):
    """
    Load the UCI Heart Disease dataset, preprocess it, and return a
    random 25% subset to simulate a single hospital's local data.
    """
    if data_path and os.path.exists(data_path):
        df = pd.read_csv(data_path)
    else:
        # Try common paths
        for path in ["../heart_disease_data.csv", "heart_disease_data.csv"]:
            if os.path.exists(path):
                df = pd.read_csv(path)
                break
        else:
            print("[ERROR] heart_disease_data.csv not found. Place it alongside the script or in the parent directory.")
            sys.exit(1)

    # Handle missing values — replace '?' with NaN then fill with median
    df = df.replace("?", np.nan)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.fillna(df.median())

    # Split features and target
    X = df.drop("target", axis=1).values.astype(np.float32)
    y = df["target"].values.astype(np.float32).reshape(-1, 1)

    # Normalize features with StandardScaler
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Simulate hospital data: take a random 25% subset
    n_samples = len(X)
    subset_size = max(1, n_samples // 4)
    indices = np.random.choice(n_samples, size=subset_size, replace=False)
    X_subset = X[indices]
    y_subset = y[indices]

    print(f"[DATA] Loaded {n_samples} total samples, using {subset_size} for this hospital.")
    return X_subset, y_subset


# ──────────────────────────────────────────────
# API Helpers
# ──────────────────────────────────────────────

def download_global_model():
    """Download current global model weights from the server."""
    url = f"{SERVER_URL}/api/training/global-model"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["weights"], data["version"]


def submit_weights(hospital_id, weights, local_accuracy):
    """Submit locally trained weights to the server for aggregation."""
    url = f"{SERVER_URL}/api/training/submit-weights"
    payload = {
        "hospital_id": int(hospital_id),
        "weights": weights,
        "local_accuracy": local_accuracy,
    }
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


# ──────────────────────────────────────────────
# Local Training
# ──────────────────────────────────────────────

def train_local(model, X, y, epochs, lr=0.001, batch_size=32):
    """Train the model on local hospital data and return accuracy."""
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)

    dataset = TensorDataset(X_tensor, y_tensor)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    model.train()
    for epoch in range(epochs):
        for batch_X, batch_y in loader:
            optimizer.zero_grad()
            preds = model(batch_X)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()

    # Calculate accuracy
    model.eval()
    with torch.no_grad():
        all_preds = model(X_tensor)
        predicted_labels = (all_preds >= 0.5).float()
        accuracy = (predicted_labels == y_tensor).float().mean().item()

    return accuracy


def extract_weights(model):
    """Extract model weights as JSON-serializable dict."""
    weights = {}
    for name, param in model.state_dict().items():
        weights[name] = param.cpu().tolist()
    return weights


def add_dp_noise(weights, sigma=0.01):
    """Add Gaussian noise to weights for differential privacy simulation."""
    noisy = {}
    for name, values in weights.items():
        tensor = torch.tensor(values, dtype=torch.float32)
        noise = torch.randn_like(tensor) * sigma
        noisy[name] = (tensor + noise).tolist()
    return noisy


# ──────────────────────────────────────────────
# Main FL Loop
# ──────────────────────────────────────────────

def main():
    # Validate config
    if not API_KEY:
        print("[ERROR] API_KEY environment variable is required.")
        print("  Usage: set API_KEY=your-key && python fedcure_client.py")
        sys.exit(1)
    if not HOSPITAL_ID:
        print("[ERROR] HOSPITAL_ID environment variable is required.")
        print("  Usage: set HOSPITAL_ID=1 && python fedcure_client.py")
        sys.exit(1)

    print("=" * 60)
    print("  FedCure FL Client")
    print("=" * 60)
    print(f"  Server:         {SERVER_URL}")
    print(f"  Hospital ID:    {HOSPITAL_ID}")
    print(f"  Rounds:         {NUM_ROUNDS}")
    print(f"  Epochs/Round:   {EPOCHS_PER_ROUND}")
    print("=" * 60)

    # Load data
    X, y = load_and_preprocess_data()

    for round_num in range(1, NUM_ROUNDS + 1):
        print(f"\n--- Round {round_num}/{NUM_ROUNDS} ---")

        # Step 1: Download global model
        print("[1/4] Downloading global model...")
        try:
            global_weights, version = download_global_model()
            print(f"      Downloaded model {version}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to download model: {e}")
            print("        Retrying in 10 seconds...")
            time.sleep(10)
            continue

        # Step 2: Load weights into local model and train
        model = HeartDiseaseModel()
        state_dict = {k: torch.tensor(v, dtype=torch.float32) for k, v in global_weights.items()}
        model.load_state_dict(state_dict)

        print(f"[2/4] Training locally for {EPOCHS_PER_ROUND} epochs...")
        accuracy = train_local(model, X, y, epochs=EPOCHS_PER_ROUND)

        # Step 3: Extract weights and add DP noise
        print("[3/4] Extracting weights and adding DP noise (σ=0.01)...")
        local_weights = extract_weights(model)
        noisy_weights = add_dp_noise(local_weights, sigma=0.01)

        # Step 4: Submit to server
        print("[4/4] Submitting weights to server...")
        try:
            result = submit_weights(HOSPITAL_ID, noisy_weights, accuracy)
            print(f"      Server response: {result['status']} — {result['message']}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to submit weights: {e}")

        print(f"Round {round_num}: Local accuracy = {accuracy:.4f}, submitted to server")

        # Wait between rounds
        if round_num < NUM_ROUNDS:
            print(f"\nSleeping 10 seconds before next round...")
            time.sleep(10)

    print("\n" + "=" * 60)
    print("  All rounds complete! Thank you for participating.")
    print("=" * 60)


if __name__ == "__main__":
    main()
