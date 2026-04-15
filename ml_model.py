import torch
import torch.nn as nn


class HeartDiseaseModel(nn.Module):
    """
    PyTorch neural network for heart disease prediction.
    Input: 11 clinical features from the combined Heart Disease dataset
           (Cleveland + Hungarian + Switzerland + Long Beach VA + Statlog).
    Output: Risk score between 0 and 1 (sigmoid).

    Architecture is intentionally compact (11→32→16→1) with BatchNorm
    and Dropout so that it stays well-calibrated when each hospital
    fine-tunes on only ~300 samples during federated rounds.
    """

    def __init__(self):
        super(HeartDiseaseModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(11, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 16),
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.network(x)


def create_model():
    """Create a fresh HeartDiseaseModel instance."""
    return HeartDiseaseModel()
