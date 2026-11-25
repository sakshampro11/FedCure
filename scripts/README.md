# Dataset preparation

prepare_dataset.py is a development/demo utility. It cleans the Kaggle heart-disease dataset and creates four local CSV splits for federated-learning demonstrations.

It is not part of the deployed API or Vercel build. Never run it on production patient data, and never commit its generated CSVs.

## Usage

    python scripts/prepare_dataset.py <path-to-kaggle-csv>

The script writes data/hospital_1.csv through data/hospital_4.csv. The files contain sensitive data and are ignored by Git.

The script prints the feature means and standard deviations it calculated. If you train with a different dataset, update the matching inference normalization constants in backend/app/main.py before deploying.
