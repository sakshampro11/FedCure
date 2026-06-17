# temp_scripts/

These scripts are for **one-time initial setup only**. They are NOT part of the live FedCure system.

Run these once before deploying the project to prepare the hospital data splits from the raw Kaggle dataset.

## Scripts

### `prepare_dataset.py`
Cleans the raw Kaggle CSV (`heart_statlog_cleveland_hungary_final.csv`) and splits it into 4 hospital-specific datasets.

**Usage:**
```bash
python temp_scripts/prepare_dataset.py <path-to-kaggle-csv>
```

**What it does:**
1. Loads the raw Kaggle CSV (must be provided as a CLI argument — it lives outside the git repo)
2. Renames columns to match FedCure conventions
3. Handles missing values (median fill) and outliers (clips extreme values)
4. Validates binary target (0/1)
5. Splits into 4 non-overlapping hospital subsets
6. Saves `data/hospital_1.csv` through `data/hospital_4.csv`
7. Prints dataset statistics including means/stds (used for inference scaling in `server/main.py`)

**After running this script, you can delete the `temp_scripts/` folder entirely.** The 4 hospital CSV files in `data/` are all the project needs.
