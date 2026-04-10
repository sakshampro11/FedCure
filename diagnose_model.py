"""Diagnose why all predictions saturate to 1.0 after federated training."""
import torch
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from ml_model import create_model

# Load dataset
df = pd.read_csv('heart_disease_data.csv').replace('?', np.nan)
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.fillna(df.median())

X = df.drop('target', axis=1).values.astype(np.float32)
y = df['target'].values.astype(np.float32)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_tensor = torch.tensor(X_scaled, dtype=torch.float32)

print("=== Dataset Stats ===")
print(f"Total samples: {len(y)}, Healthy(0): {(y==0).sum()}, Diseased(1): {(y==1).sum()}")
print()

# Test each model version
for v in range(0, 15):
    fpath = f'models/global_model_v{v}.pt'
    if not os.path.exists(fpath):
        continue
    model = create_model()
    model.load_state_dict(torch.load(fpath, weights_only=True))
    model.eval()
    
    with torch.no_grad():
        preds = model(X_tensor).numpy().flatten()
        raw_logits = model.network[:-1](X_tensor).numpy().flatten()
    
    acc = ((preds >= 0.5) == y).mean()
    
    healthy_preds = preds[y == 0]
    diseased_preds = preds[y == 1]
    healthy_logits = raw_logits[y == 0]
    diseased_logits = raw_logits[y == 1]
    
    print(f"--- Model v{v} ---")
    print(f"  Accuracy: {acc:.3f}")
    print(f"  Healthy  preds: min={healthy_preds.min():.6f} max={healthy_preds.max():.6f} mean={healthy_preds.mean():.6f}")
    print(f"  Diseased preds: min={diseased_preds.min():.6f} max={diseased_preds.max():.6f} mean={diseased_preds.mean():.6f}")
    print(f"  Healthy  logits: min={healthy_logits.min():.2f} max={healthy_logits.max():.2f} mean={healthy_logits.mean():.2f}")
    print(f"  Diseased logits: min={diseased_logits.min():.2f} max={diseased_logits.max():.2f} mean={diseased_logits.mean():.2f}")
    print(f"  Saturated to 1.0: {(preds >= 0.9999).sum()}/{len(preds)}")
    print(f"  Saturated to 0.0: {(preds <= 0.0001).sum()}/{len(preds)}")
    
    # Weight magnitude
    max_w = max(p.abs().max().item() for p in model.parameters())
    print(f"  Max |weight|: {max_w:.3f}")
    print()
