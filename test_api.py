"""Quick test of the inference API with the retrained model."""
import requests

API = "http://127.0.0.1:8000/api/inference/predict"

# Healthy patient (typical of target=0 in dataset)
healthy = {
    "age": 56, "sex": 1, "cp": 0, "trestbps": 132, "chol": 251,
    "fbs": 0, "restecg": 0, "thalach": 139, "exang": 0,
    "oldpeak": 1.6, "slope": 1, "ca": 1, "thal": 2
}

# Diseased patient (typical of target=1 in dataset)
sick = {
    "age": 52, "sex": 0, "cp": 1, "trestbps": 129, "chol": 242,
    "fbs": 0, "restecg": 0, "thalach": 158, "exang": 0,
    "oldpeak": 0.6, "slope": 1, "ca": 0, "thal": 2
}

# The user's original test case
user_test = {
    "age": 54, "sex": 1, "cp": 1, "trestbps": 120, "chol": 120,
    "fbs": 1, "restecg": 0, "thalach": 90, "exang": 0,
    "oldpeak": 0.8, "slope": 1, "ca": 0, "thal": 1
}

for label, data in [("Healthy (avg target=0)", healthy), ("Diseased (avg target=1)", sick), ("User screenshot test", user_test)]:
    res = requests.post(API, json=data)
    r = res.json()
    print(f"{label}: score={r['risk_score']:.4f}, level={r['risk_level']}")
