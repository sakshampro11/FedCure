import os
import copy
import torch
from ml_model import HeartDiseaseModel, create_model

# Directory to store global model versions
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Track the current global model version
_current_version = 0


def initialize_global_model():
    """
    Create and save an initial global model with random weights (v0).
    Only runs if no model file exists yet.
    """
    global _current_version
    v0_path = os.path.join(MODELS_DIR, "global_model_v0.pt")
    if not os.path.exists(v0_path):
        model = create_model()
        torch.save(model.state_dict(), v0_path)
        _current_version = 0
        print("[FedCure] Initialized global model v0 with random weights.")
    else:
        # Find the latest version
        existing = [f for f in os.listdir(MODELS_DIR) if f.startswith("global_model_v") and f.endswith(".pt")]
        if existing:
            versions = [int(f.replace("global_model_v", "").replace(".pt", "")) for f in existing]
            _current_version = max(versions)
        print(f"[FedCure] Loaded existing global model v{_current_version}.")


def aggregate_weights(weight_updates_list):
    """
    Federated Averaging (FedAvg): average corresponding weight tensors
    across all hospital submissions.

    Args:
        weight_updates_list: list of state_dict-like dicts
            (keys → list of floats, as received from API)

    Returns:
        Averaged state_dict (with torch tensors) ready to load into a model.
    """
    if not weight_updates_list:
        raise ValueError("No weight updates to aggregate.")

    num_clients = len(weight_updates_list)

    # Convert list-of-floats back to tensors
    tensor_dicts = []
    for w in weight_updates_list:
        tensor_dicts.append({k: torch.tensor(v, dtype=torch.float32) for k, v in w.items()})

    # Average all weights
    avg_weights = {}
    for key in tensor_dicts[0].keys():
        stacked = torch.stack([td[key] for td in tensor_dicts])
        avg_weights[key] = torch.mean(stacked, dim=0)

    return avg_weights


def save_global_model(avg_weights, version=None):
    """
    Save a new global model version to disk.

    Args:
        avg_weights: state_dict with averaged tensors.
        version: optional version number. If None, auto-increments.

    Returns:
        (version, file_path) tuple.
    """
    global _current_version
    if version is None:
        version = _current_version + 1

    file_path = os.path.join(MODELS_DIR, f"global_model_v{version}.pt")
    torch.save(avg_weights, file_path)
    _current_version = version
    print(f"[FedCure] Saved global model v{version} → {file_path}")
    return version, file_path


def load_global_model():
    """
    Load the current (latest) global model for inference.

    Returns:
        A HeartDiseaseModel instance with loaded weights.
    """
    global _current_version
    file_path = os.path.join(MODELS_DIR, f"global_model_v{_current_version}.pt")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Global model v{_current_version} not found at {file_path}")

    model = create_model()
    model.load_state_dict(torch.load(file_path, weights_only=True))
    model.eval()
    return model


def get_current_version():
    """Return the current global model version number."""
    return _current_version
