"""
Prepare the UCI Heart Disease (Cleveland) dataset for FedCure.

Downloads the dataset, handles missing values, converts the target to binary,
and saves a clean CSV ready for training.
"""

import os
import urllib.request
import pandas as pd
import numpy as np

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

DATA_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "heart-disease/processed.cleveland.data"
)

COLUMN_NAMES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs",
    "restecg", "thalach", "exang", "oldpeak", "slope",
    "ca", "thal", "target",
]

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "heart_disease_clean.csv")
RAW_PATH = os.path.join(OUTPUT_DIR, "processed.cleveland.data")


def download_dataset():
    """Download the raw Cleveland dataset if not already present."""
    if os.path.exists(RAW_PATH):
        print(f"[INFO] Raw file already exists at {RAW_PATH}, skipping download.")
        return RAW_PATH

    print(f"[DOWNLOAD] Fetching dataset from:\n  {DATA_URL}")
    urllib.request.urlretrieve(DATA_URL, RAW_PATH)
    print(f"[DOWNLOAD] Saved to {RAW_PATH}")
    return RAW_PATH


def prepare_dataset(raw_path):
    """Load, clean, and save the dataset."""

    # Load with column names
    df = pd.read_csv(raw_path, header=None, names=COLUMN_NAMES, na_values="?")

    print(f"\n[RAW] Shape: {df.shape}")
    print(f"[RAW] Missing values per column:\n{df.isnull().sum()}")

    # ── Handle missing values: fill with column median ──
    for col in df.columns:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"  Filled {col} missing values with median = {median_val:.2f}")

    # ── Convert target to binary (0 = no disease, 1-4 = disease present) ──
    df["target"] = (df["target"] > 0).astype(int)

    # ── Ensure all columns are numeric ──
    # -- Ensure all columns are numeric --
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna()  # Drop any remaining non-numeric rows

    # -- Save clean CSV --
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n[SAVED] Clean dataset -> {OUTPUT_PATH}")

    # -- Print dataset statistics --
    print("\n" + "=" * 60)
    print("  DATASET STATISTICS")
    print("=" * 60)
    print(f"  Shape:              {df.shape[0]} samples x {df.shape[1]} features")
    print(f"  Class distribution:")
    print(f"    No disease (0):   {(df['target'] == 0).sum()} ({(df['target'] == 0).mean() * 100:.1f}%)")
    print(f"    Disease    (1):   {(df['target'] == 1).sum()} ({(df['target'] == 1).mean() * 100:.1f}%)")
    print(f"\n  Feature ranges:")
    for col in COLUMN_NAMES[:-1]:  # Exclude target
        print(f"    {col:>10s}:  [{df[col].min():.1f}, {df[col].max():.1f}]  (mean={df[col].mean():.2f})")
    print("=" * 60)

    return df


if __name__ == "__main__":
    raw = download_dataset()
    prepare_dataset(raw)
