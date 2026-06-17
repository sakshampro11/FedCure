"""
One-time dataset preparation for FedCure.

Cleans the combined Heart Disease Kaggle dataset and splits it into
4 non-overlapping hospital subsets for federated learning.

Source: https://www.kaggle.com/datasets/sid321axn/heart-statlog-cleveland-hungary-final
Samples: ~1190  |  Features: 11 + target

Usage:
    python temp_scripts/prepare_dataset.py <path-to-kaggle-csv>

Example:
    python temp_scripts/prepare_dataset.py ../heart_statlog_cleveland_hungary_final.csv
"""

import os
import sys
import numpy as np
import pandas as pd

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

NUM_HOSPITALS = 4
RANDOM_SEED = 42

# Column mapping: Kaggle name → FedCure name
COLUMN_MAP = {
    "age": "age",
    "sex": "sex",
    "chest pain type": "cp",
    "resting bp s": "trestbps",
    "cholesterol": "chol",
    "fasting blood sugar": "fbs",
    "resting ecg": "restecg",
    "max heart rate": "thalach",
    "exercise angina": "exang",
    "oldpeak": "oldpeak",
    "ST slope": "slope",
    "target": "target",
}

FEATURE_COLS = ["age", "sex", "cp", "trestbps", "chol", "fbs",
                "restecg", "thalach", "exang", "oldpeak", "slope"]
ALL_COLS = FEATURE_COLS + ["target"]


def clean_dataset(raw_csv_path):
    """Load, clean, and return the dataset as a DataFrame."""

    df = pd.read_csv(raw_csv_path)
    print(f"[LOAD] Read {len(df)} rows × {len(df.columns)} columns from raw CSV")
    print(f"       Columns: {list(df.columns)}")

    # ── Rename columns ──
    df = df.rename(columns=COLUMN_MAP)

    # Verify all expected columns exist
    missing = [c for c in ALL_COLS if c not in df.columns]
    if missing:
        print(f"[ERROR] Missing columns after rename: {missing}")
        print(f"        Available: {list(df.columns)}")
        sys.exit(1)

    # Keep only the columns we need, in canonical order
    df = df[ALL_COLS]

    # ── Handle missing values ──
    df = df.replace("?", np.nan).replace("", np.nan)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    n_missing = df.isna().sum().sum()
    if n_missing > 0:
        print(f"[CLEAN] Filling {n_missing} missing values with column medians")
        df = df.fillna(df.median())

    # ── Handle outliers ──
    # Some records have cholesterol = 0 (placeholder for missing data)
    n_zero_chol = (df["chol"] == 0).sum()
    if n_zero_chol > 0:
        chol_median = df.loc[df["chol"] > 0, "chol"].median()
        df.loc[df["chol"] == 0, "chol"] = chol_median
        print(f"[CLEAN] Replaced {n_zero_chol} zero-cholesterol values with median ({chol_median:.0f})")

    # Some records have trestbps = 0 (same issue)
    n_zero_bp = (df["trestbps"] == 0).sum()
    if n_zero_bp > 0:
        bp_median = df.loc[df["trestbps"] > 0, "trestbps"].median()
        df.loc[df["trestbps"] == 0, "trestbps"] = bp_median
        print(f"[CLEAN] Replaced {n_zero_bp} zero-BP values with median ({bp_median:.0f})")

    # Clip extreme values to physiologically reasonable ranges
    df["trestbps"] = df["trestbps"].clip(lower=80, upper=220)
    df["chol"] = df["chol"].clip(lower=100, upper=600)
    df["thalach"] = df["thalach"].clip(lower=50, upper=220)

    # ── Validate binary target ──
    df["target"] = (df["target"] >= 1).astype(int)
    assert df["target"].isin([0, 1]).all(), "Target must be binary (0/1)"

    return df


def print_statistics(df):
    """Print a data quality report with means/stds for server inference."""

    print(f"\n{'='*65}")
    print(f"  DATA QUALITY REPORT  —  {len(df)} samples × {len(FEATURE_COLS)} features")
    print(f"{'='*65}")

    # Class distribution
    n_healthy = (df["target"] == 0).sum()
    n_disease = (df["target"] == 1).sum()
    print(f"\n  Class Distribution:")
    print(f"    Healthy (0): {n_healthy:>4d}  ({100*n_healthy/len(df):.1f}%)")
    print(f"    Disease (1): {n_disease:>4d}  ({100*n_disease/len(df):.1f}%)")

    # Feature ranges
    print(f"\n  Feature Statistics:")
    print(f"  {'Feature':<12s} {'Min':>8s} {'Max':>8s} {'Mean':>8s} {'Std':>8s} {'Median':>8s}")
    print(f"  {'-'*56}")
    for col in FEATURE_COLS:
        print(f"  {col:<12s} {df[col].min():>8.2f} {df[col].max():>8.2f} "
              f"{df[col].mean():>8.3f} {df[col].std():>8.3f} {df[col].median():>8.2f}")

    # Print means and stds for hardcoding in server/main.py
    print(f"\n  +---------------------------------------------------------+")
    print(f"  |  COPY THESE INTO server/main.py for inference scaling:  |")
    print(f"  +---------------------------------------------------------+")
    means = [f"{df[c].mean():.3f}" for c in FEATURE_COLS]
    print(f"  means = [{', '.join(means)}]")
    stds = [f"{df[c].std():.3f}" for c in FEATURE_COLS]
    print(f"  stds  = [{', '.join(stds)}]")

    # Missing values check
    n_remaining = df.isna().sum().sum()
    print(f"\n  Missing values: {n_remaining}")
    print(f"{'='*65}")


def split_for_hospitals(df):
    """Split the dataset into NUM_HOSPITALS non-overlapping subsets."""

    os.makedirs(DATA_DIR, exist_ok=True)

    # Shuffle the dataset
    df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    # Split into non-overlapping subsets
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


def main():
    if len(sys.argv) < 2:
        print("Usage: python temp_scripts/prepare_dataset.py <path-to-kaggle-csv>")
        print("\nExample:")
        print("  python temp_scripts/prepare_dataset.py ../heart_statlog_cleveland_hungary_final.csv")
        sys.exit(1)

    raw_csv_path = sys.argv[1]
    if not os.path.exists(raw_csv_path):
        print(f"[ERROR] File not found: {raw_csv_path}")
        print("        Download from: https://www.kaggle.com/datasets/sid321axn/heart-statlog-cleveland-hungary-final")
        sys.exit(1)

    # Step 1: Clean the dataset
    print("\n[STEP 1/3] Cleaning dataset...")
    df = clean_dataset(raw_csv_path)

    # Step 2: Print statistics
    print("\n[STEP 2/3] Data quality report...")
    print_statistics(df)

    # Step 3: Split for hospitals
    print("\n[STEP 3/3] Splitting for hospitals...")
    split_for_hospitals(df)

    print("\n" + "=" * 60)
    print("  All done! Next steps:")
    print("  1. Start the server:  uvicorn server.main:app --reload")
    print("  2. Run FL clients:    docker run fedcure-client (x4)")
    print("=" * 60)


if __name__ == "__main__":
    main()
