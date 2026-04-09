"""
Split the clean UCI Heart Disease dataset into 4 non-overlapping subsets
to simulate 4 hospitals participating in federated learning.

Each hospital receives approximately 25% of the total data (shuffled).
"""

import os
import sys
import numpy as np
import pandas as pd

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(DATA_DIR, "heart_disease_clean.csv")
NUM_HOSPITALS = 4
RANDOM_SEED = 42


def main():
    # ── Load dataset ──
    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] Clean dataset not found at {DATASET_PATH}")
        print("        Run prepare_dataset.py first.")
        sys.exit(1)

    df = pd.read_csv(DATASET_PATH)
    print(f"[DATA] Loaded {len(df)} samples from {DATASET_PATH}")

    # ── Shuffle the dataset ──
    df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    # ── Split into NUM_HOSPITALS non-overlapping subsets ──
    indices = np.array_split(range(len(df)), NUM_HOSPITALS)

    print(f"\n{'='*60}")
    print(f"  HOSPITAL DATA SPLIT ({NUM_HOSPITALS} hospitals)")
    print(f"{'='*60}")

    for i, idx in enumerate(indices, start=1):
        split_df = df.iloc[idx]
        output_path = os.path.join(DATA_DIR, f"hospital_{i}.csv")
        split_df.to_csv(output_path, index=False)

        n_disease = (split_df["target"] == 1).sum()
        n_healthy = (split_df["target"] == 0).sum()

        print(f"  Hospital {i}:  {len(split_df):>3d} samples  "
              f"(disease={n_disease}, healthy={n_healthy})  -> {output_path}")

    print(f"{'='*60}")
    print(f"\n[DONE] {NUM_HOSPITALS} hospital CSV files created in {DATA_DIR}")


if __name__ == "__main__":
    main()
