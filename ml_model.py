import torch
import torch.nn as nn


class HeartDiseaseModel(nn.Module):
    """
    PyTorch neural network for heart disease prediction.
    Input: 13 clinical features from the UCI Heart Disease dataset.
    Output: Risk score between 0 and 1 (sigmoid).
    """

    def __init__(self):
        super(HeartDiseaseModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(13, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.network(x)


def create_model():
    """Create a fresh HeartDiseaseModel instance."""
    return HeartDiseaseModel()
