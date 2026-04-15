import torch
import os
import numpy as np
from ml_model import create_model

# 11-feature means/stds from the combined Heart Statlog Cleveland Hungary dataset (~1190 samples)
means = np.array([53.720, 0.764, 3.233, 132.263, 245.063, 0.213, 0.698, 139.733, 0.387, 0.923, 1.624])
stds = np.array([9.358, 0.425, 0.935, 17.964, 52.930, 0.410, 0.870, 25.518, 0.487, 1.086, 0.610])

# Healthy User (11 features: age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope)
features = [29, 0, 0, 110, 200, 0, 0, 180, 0, 0.0, 2]
X_scaled = (np.array(features) - means) / (stds + 1e-8)
X_tensor = torch.tensor([X_scaled], dtype=torch.float32)

print("Healthy Patient Predictions:")
model = create_model()
for v in range(0, 15):
    file = f'models/global_model_v{v}.pt'
    if os.path.exists(file):
        model.load_state_dict(torch.load(file, weights_only=True))
        print(f'v{v}:', model(X_tensor).item())
