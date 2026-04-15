"""
Prepare the combined Heart Disease dataset (Cleveland + Hungarian + Switzerland +
Long Beach VA + Statlog) for FedCure federated learning.

Source: https://www.kaggle.com/datasets/sid321axn/heart-statlog-cleveland-hungary-final
Samples: ~1190  |  Features: 11 + target

This script:
  1. Loads the raw Kaggle CSV
  2. Renames columns to match FedCure code conventions
  3. Handles missing values (median fill) and outliers (clip extreme values)
  4. Validates binary target
  5. Prints a data quality report
  6. Saves the cleaned dataset for downstream use
"""

import os
import sys
import numpy as np
import pandas as pd

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

RAW_CSV = os.path.join(PROJECT_ROOT, "heart_statlog_cleveland_hungary_final.csv")
OUTPUT_CSV = os.path.join(PROJECT_ROOT, "heart_disease_data.csv")
CLEAN_CSV = os.path.join(SCRIPT_DIR, "heart_disease_clean.csv")

# ──────────────────────────────────────────────
# Column mapping: Kaggle name → FedCure name
# ──────────────────────────────────────────────

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

# Expected column order after renaming
FEATURE_COLS = ["age", "sex", "cp", "trestbps", "chol", "fbs",
                "restecg", "thalach", "exang", "oldpeak", "slope"]
ALL_COLS = FEATURE_COLS + ["target"]


def main():
    # ── Load raw CSV ──
    if not os.path.exists(RAW_CSV):
        print(f"[ERROR] Raw dataset not found at {RAW_CSV}")
        print("        Download from: https://www.kaggle.com/datasets/sid321axn/heart-statlog-cleveland-hungary-final")
        print(f"        Place it at: {RAW_CSV}")
        sys.exit(1)

    df = pd.read_csv(RAW_CSV)
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
    # Replace any '?' or empty strings with NaN
    df = df.replace("?", np.nan).replace("", np.nan)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    n_missing = df.isna().sum().sum()
    if n_missing > 0:
        print(f"[CLEAN] Filling {n_missing} missing values with column medians")
        df = df.fillna(df.median())

    # ── Handle outliers ──
    # Some records from the Hungarian/Swiss datasets have cholesterol = 0,
    # which is a known placeholder for missing data. Replace 0 chol with median.
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
    # Ensure target is strictly 0 or 1
    df["target"] = (df["target"] >= 1).astype(int)
    assert df["target"].isin([0, 1]).all(), "Target must be binary (0/1)"

    # ── Data quality report ──
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

    # Print means and stds for hardcoding in main.py
    print(f"\n  Means for main.py (copy-paste):")
    means = [f"{df[c].mean():.3f}" for c in FEATURE_COLS]
    print(f"    [{', '.join(means)}]")
    print(f"\n  Stds for main.py (copy-paste):")
    stds = [f"{df[c].std():.3f}" for c in FEATURE_COLS]
    print(f"    [{', '.join(stds)}]")

    # Missing values check
    n_remaining = df.isna().sum().sum()
    print(f"\n  Missing values: {n_remaining}")
    print(f"{'='*65}")

    # ── Save ──
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[SAVED] {OUTPUT_CSV}  ({len(df)} rows)")

    df.to_csv(CLEAN_CSV, index=False)
    print(f"[SAVED] {CLEAN_CSV}  ({len(df)} rows)")

    print("\n[DONE] Dataset preparation complete. Next steps:")
    print("  1. Run  data/split_for_hospitals.py   to create hospital subsets")
    print("  2. Run  simulate_training.py          to train the global model")


if __name__ == "__main__":
    main()
