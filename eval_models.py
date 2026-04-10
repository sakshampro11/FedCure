import torch
import os
import numpy as np
from ml_model import create_model

means = np.array([54.366, 0.683, 0.967, 131.624, 246.264, 0.149, 0.528, 149.647, 0.327, 1.040, 1.399, 0.729, 2.314])
stds = np.array([9.067, 0.465, 1.030, 17.509, 51.745, 0.356, 0.525, 22.867, 0.469, 1.159, 0.615, 1.021, 0.611])

# Healthy User (row target=0 from dataset)
features = [48, 1, 0, 130, 256, 1, 0, 150, 1, 0, 2, 2, 3]
X_scaled = (np.array(features) - means) / (stds + 1e-8)
X_tensor = torch.tensor([X_scaled], dtype=torch.float32)

print("Healthy Patient Predictions:")
model = create_model()
for v in range(0, 15):
    file = f'models/global_model_v{v}.pt'
    if os.path.exists(file):
        model.load_state_dict(torch.load(file, weights_only=True))
        print(f'v{v}:', model(X_tensor).item())
