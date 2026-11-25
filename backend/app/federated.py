"""Model serialization, validation, and FedAvg operations."""

from __future__ import annotations

import io
from collections.abc import Mapping, Sequence
from typing import Any

import torch

from .nn_model import create_model


def initial_state_dict() -> dict[str, torch.Tensor]:
    """Create CPU-only initial model weights."""
    return {
        name: value.detach().cpu().clone()
        for name, value in create_model().state_dict().items()
    }


def serialize_state_dict(state_dict: Mapping[str, torch.Tensor]) -> bytes:
    buffer = io.BytesIO()
    torch.save(dict(state_dict), buffer)
    return buffer.getvalue()


def deserialize_state_dict(payload: bytes) -> dict[str, torch.Tensor]:
    state_dict = torch.load(io.BytesIO(payload), map_location="cpu", weights_only=True)
    if not isinstance(state_dict, dict):
        raise ValueError("Stored model weights are invalid.")
    return state_dict


def model_from_state_dict(state_dict: Mapping[str, torch.Tensor]):
    model = create_model()
    model.load_state_dict(dict(state_dict), strict=True)
    model.eval()
    return model


def state_dict_as_json(state_dict: Mapping[str, torch.Tensor]) -> dict[str, Any]:
    return {name: value.detach().cpu().tolist() for name, value in state_dict.items()}


def validate_submitted_weights(weights: Mapping[str, Any]) -> dict[str, torch.Tensor]:
    """Validate a client update against the exact model architecture."""
    expected = create_model().state_dict()
    if set(weights) != set(expected):
        raise ValueError("Weight keys do not match the FedCure model architecture.")

    validated: dict[str, torch.Tensor] = {}
    for name, expected_tensor in expected.items():
        try:
            received = torch.as_tensor(weights[name])
        except (TypeError, ValueError, RuntimeError) as exc:
            raise ValueError(f"Invalid tensor value for '{name}'.") from exc

        if tuple(received.shape) != tuple(expected_tensor.shape):
            raise ValueError(f"Invalid tensor shape for '{name}'.")

        if expected_tensor.is_floating_point():
            received = received.to(dtype=expected_tensor.dtype)
            if not torch.isfinite(received).all():
                raise ValueError(f"Non-finite values are not allowed in '{name}'.")
        else:
            received_as_float = received.to(dtype=torch.float32)
            if not torch.isfinite(received_as_float).all():
                raise ValueError(f"Non-finite values are not allowed in '{name}'.")
            if not torch.equal(received_as_float, received_as_float.round()):
                raise ValueError(f"'{name}' must contain integer values.")
            received = received.to(dtype=expected_tensor.dtype)

        validated[name] = received.detach().cpu()

    return validated


def aggregate_weights(weight_updates: Sequence[Mapping[str, Any]]) -> dict[str, torch.Tensor]:
    """FedAvg aggregate validated model updates, preserving buffer dtypes."""
    if not weight_updates:
        raise ValueError("No client updates were supplied.")

    validated_updates = [validate_submitted_weights(update) for update in weight_updates]
    aggregated: dict[str, torch.Tensor] = {}

    for name, first_tensor in validated_updates[0].items():
        stacked = torch.stack([update[name] for update in validated_updates])
        if first_tensor.is_floating_point():
            aggregated[name] = stacked.mean(dim=0)
        else:
            aggregated[name] = stacked.to(torch.float32).mean(dim=0).round().to(first_tensor.dtype)

    return aggregated
