import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from torch.utils.data import DataLoader, TensorDataset
from ml_model import create_model


def train_local(dataset_path, model=None, epochs=10, lr=0.001, batch_size=32):
    """
    Train the heart disease model on a local CSV dataset.

    Args:
        dataset_path: path to CSV file with 13 features + target column.
        model: optional pre-existing model to continue training. If None, creates a new one.
        epochs: number of training epochs.
        lr: learning rate.
        batch_size: mini-batch size.

    Returns:
        (trained_model, accuracy) tuple.
    """
    if model is None:
        model = create_model()

    # Load and prepare data
    df = pd.read_csv(dataset_path)
    X = df.drop("target", axis=1).values.astype(np.float32)
    y = df["target"].values.astype(np.float32).reshape(-1, 1)

    # Simple min-max normalization
    X = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-8)

    X_tensor = torch.tensor(X)
    y_tensor = torch.tensor(y)

    dataset = TensorDataset(X_tensor, y_tensor)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Training
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    model.train()
    for epoch in range(epochs):
        for batch_X, batch_y in loader:
            optimizer.zero_grad()
            predictions = model(batch_X)
            loss = criterion(predictions, batch_y)
            loss.backward()
            optimizer.step()

    # Calculate accuracy
    model.eval()
    with torch.no_grad():
        all_preds = model(X_tensor)
        predicted_labels = (all_preds >= 0.5).float()
        accuracy = (predicted_labels == y_tensor).float().mean().item()

    return model, accuracy


def extract_weights(model):
    """
    Extract model weights as a JSON-serializable dict.
    Converts tensors → nested Python lists.

    Args:
        model: a PyTorch nn.Module.

    Returns:
        dict mapping layer names to weight values as lists.
    """
    weights = {}
    for name, param in model.state_dict().items():
        weights[name] = param.cpu().tolist()
    return weights


def add_dp_noise(weights_dict, epsilon=0.8):
    """
    Add calibrated Gaussian noise to model weights to simulate
    differential privacy.

    The noise scale is inversely proportional to epsilon:
        sigma = 1.0 / epsilon

    Args:
        weights_dict: dict of weight name → list of floats (serialized).
        epsilon: privacy budget. Lower = more noise = more privacy.

    Returns:
        New weights dict with noise added.
    """
    sigma = 1.0 / epsilon
    noisy_weights = {}
    for name, values in weights_dict.items():
        tensor = torch.tensor(values, dtype=torch.float32)
        noise = torch.randn_like(tensor) * sigma
        noisy_weights[name] = (tensor + noise).tolist()
    return noisy_weights
