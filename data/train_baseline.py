"""
Train a centralized baseline model on the full UCI Heart Disease dataset.

This serves as a comparison point for the federated learning approach.
The model uses the same HeartDiseaseModel architecture (13 -> 128 -> 64 -> 32 -> 1).
"""

import os
import sys
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

# Add project root to path so we can import the shared model
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ml_model import HeartDiseaseModel

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(DATA_DIR, "heart_disease_clean.csv")
MODELS_DIR = os.path.join(os.path.dirname(DATA_DIR), "models")
MODEL_PATH = os.path.join(MODELS_DIR, "baseline_model.pt")
ACCURACY_PATH = os.path.join(DATA_DIR, "baseline_accuracy.txt")

EPOCHS = 20
BATCH_SIZE = 32
LEARNING_RATE = 0.001
TEST_SPLIT = 0.2
RANDOM_SEED = 42


def main():
    # ── Load dataset ──
    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] Clean dataset not found at {DATASET_PATH}")
        print("        Run prepare_dataset.py first.")
        sys.exit(1)

    df = pd.read_csv(DATASET_PATH)
    print(f"[DATA] Loaded {len(df)} samples from {DATASET_PATH}")

    X = df.drop("target", axis=1).values.astype(np.float32)
    y = df["target"].values.astype(np.float32).reshape(-1, 1)

    # ── Train/Test split ──
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SPLIT, random_state=RANDOM_SEED, stratify=y
    )
    print(f"[SPLIT] Train: {len(X_train)} | Test: {len(X_test)}")

    # ── Standardize features ──
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # ── Create DataLoaders ──
    train_dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32),
    )
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

    X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
    y_test_tensor = torch.tensor(y_test, dtype=torch.float32)

    # ── Initialize model ──
    model = HeartDiseaseModel()
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # ── Training loop ──
    print(f"\n{'='*60}")
    print("  CENTRALIZED BASELINE TRAINING")
    print(f"{'='*60}")
    print(f"  Architecture:  13 -> 128 -> 64 -> 32 -> 1 (Sigmoid)")
    print(f"  Epochs:        {EPOCHS}")
    print(f"  Batch size:    {BATCH_SIZE}")
    print(f"  Learning rate: {LEARNING_RATE}")
    print(f"{'='*60}\n")

    for epoch in range(1, EPOCHS + 1):
        model.train()
        epoch_loss = 0.0
        batches = 0

        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            preds = model(batch_X)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            batches += 1

        avg_loss = epoch_loss / batches

        # Evaluate on test set every 5 epochs
        if epoch % 5 == 0 or epoch == 1:
            model.eval()
            with torch.no_grad():
                test_preds = model(X_test_tensor)
                test_labels = (test_preds >= 0.5).float()
                test_acc = (test_labels == y_test_tensor).float().mean().item()
            print(f"  Epoch {epoch:>2d}/{EPOCHS}  |  Loss: {avg_loss:.4f}  |  Test Acc: {test_acc:.4f}")

    # ── Final evaluation ──
    model.eval()
    with torch.no_grad():
        test_preds = model(X_test_tensor)
        test_labels = (test_preds >= 0.5).float()
        final_accuracy = (test_labels == y_test_tensor).float().mean().item()

    print(f"\n{'='*60}")
    print(f"  Centralized Baseline Accuracy: {final_accuracy:.4f}")
    print(f"{'='*60}")

    # ── Save model ──
    os.makedirs(MODELS_DIR, exist_ok=True)
    torch.save(model.state_dict(), MODEL_PATH)
    print(f"\n[SAVED] Model  -> {MODEL_PATH}")

    # ── Save accuracy ──
    with open(ACCURACY_PATH, "w") as f:
        f.write(f"{final_accuracy:.4f}\n")
    print(f"[SAVED] Accuracy -> {ACCURACY_PATH}")


if __name__ == "__main__":
    main()
