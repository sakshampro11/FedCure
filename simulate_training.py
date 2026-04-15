"""
Simulate a complete federated training session (4 hospitals × 5 rounds)
to produce a well-trained global model for demo/inference.

Run this once after resetting client model weights.
"""
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

import federated
from ml_model import create_model

# ── Load dataset ──
df = pd.read_csv("heart_disease_data.csv").replace("?", np.nan)
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.fillna(df.median())

X = df.drop("target", axis=1).values.astype(np.float32)
y = df["target"].values.astype(np.float32).reshape(-1, 1)

scaler = StandardScaler()
X = scaler.fit_transform(X)

NUM_HOSPITALS = 4
NUM_ROUNDS = 10
EPOCHS_PER_ROUND = 3

# ── Initialize global model ──
federated.initialize_global_model()


def train_local(model, X_local, y_local, epochs=3, lr=0.0005):
    X_tensor = torch.tensor(X_local, dtype=torch.float32)
    y_tensor = torch.tensor(y_local, dtype=torch.float32)
    dataset = TensorDataset(X_tensor, y_tensor)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=0.01)

    model.train()
    for _ in range(epochs):
        for batch_X, batch_y in loader:
            optimizer.zero_grad()
            preds = model(batch_X)
            loss = criterion(preds, batch_y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

    model.eval()
    with torch.no_grad():
        all_preds = model(X_tensor)
        acc = ((all_preds >= 0.5).float() == y_tensor).float().mean().item()
    return acc


print(f"Simulating {NUM_HOSPITALS} hospitals x {NUM_ROUNDS} rounds\n")

for round_num in range(1, NUM_ROUNDS + 1):
    print(f"--- Round {round_num}/{NUM_ROUNDS} ---")

    # Load current global model
    global_model = federated.load_global_model()
    global_state = global_model.state_dict()

    weight_updates = []
    accuracies = []

    for h in range(NUM_HOSPITALS):
        # Each hospital gets a random 25% subset
        n = len(X)
        subset = np.random.choice(n, size=n // 4, replace=False)
        X_h = X[subset]
        y_h = y[subset]

        # Clone global model and train locally
        local_model = create_model()
        local_model.load_state_dict({k: v.clone() for k, v in global_state.items()})

        acc = train_local(local_model, X_h, y_h, epochs=EPOCHS_PER_ROUND)
        accuracies.append(acc)

        # Extract weights (with small DP noise)
        weights = {}
        for name, param in local_model.state_dict().items():
            if param.is_floating_point():
                noisy = param + torch.randn_like(param) * 0.01
                weights[name] = noisy.tolist()
            else:
                weights[name] = param.tolist()
        weight_updates.append(weights)

        print(f"  Hospital {h+1}: local accuracy = {acc:.4f}")

    # FedAvg aggregation
    aggregated = federated.aggregate_weights(weight_updates)
    new_version, path = federated.save_global_model(aggregated)

    avg_acc = sum(accuracies) / len(accuracies)
    print(f"  -> Aggregated -> v{new_version}, avg accuracy = {avg_acc:.4f}\n")

# ── Final evaluation ──
print("=" * 50)
print("Final model evaluation on FULL dataset:")
model = federated.load_global_model()
X_tensor = torch.tensor(X, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.float32)

with torch.no_grad():
    preds = model(X_tensor).numpy().flatten()
    raw_logits = model.network[:-1](X_tensor).numpy().flatten()

predicted_labels = (preds >= 0.5).astype(float)
accuracy = (predicted_labels == y.flatten()).mean()

print(f"  Accuracy: {accuracy:.4f}")
print(f"  Healthy  preds: min={preds[y.flatten()==0].min():.4f}  max={preds[y.flatten()==0].max():.4f}  mean={preds[y.flatten()==0].mean():.4f}")
print(f"  Diseased preds: min={preds[y.flatten()==1].min():.4f}  max={preds[y.flatten()==1].max():.4f}  mean={preds[y.flatten()==1].mean():.4f}")
print(f"  Logit range: [{raw_logits.min():.2f}, {raw_logits.max():.2f}]")
print(f"  Saturated (>0.9999): {(preds > 0.9999).sum()}/{len(preds)}")
print(f"  Saturated (<0.0001): {(preds < 0.0001).sum()}/{len(preds)}")

# Test a healthy-looking patient (11 features: age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope)
print("\n-- Demo predictions --")
healthy = np.array([[29, 0, 0, 110, 200, 0, 0, 180, 0, 0.0, 2]])
sick    = np.array([[65, 1, 3, 160, 330, 1, 2, 100, 1, 4.0, 0]])

healthy_scaled = torch.tensor(scaler.transform(healthy), dtype=torch.float32)
sick_scaled    = torch.tensor(scaler.transform(sick), dtype=torch.float32)

with torch.no_grad():
    h_score = model(healthy_scaled).item()
    s_score = model(sick_scaled).item()

print(f"  Young healthy female:  {h_score:.4f} -> {'Low' if h_score < 0.3 else 'Moderate' if h_score <= 0.7 else 'High'}")
print(f"  Elderly high-risk male: {s_score:.4f} -> {'Low' if s_score < 0.3 else 'Moderate' if s_score <= 0.7 else 'High'}")
