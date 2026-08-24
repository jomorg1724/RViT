"""
Robust HRA checkpoint loading for analysis tools.

Handles checkpoints with or without saved model_kwargs (older runs only saved
the state_dict). When model_kwargs is absent, falls back to a sensible
default config and probes whether the state-dict shapes imply
cross_layer_via='ft' or 'input' (cells in 'ft' mode have extra Q/K/V feedback
projections in their FeedbackTransformer).
"""
from __future__ import annotations

import os
from typing import Tuple

import torch

from HRA.model import HRAModel


_FALLBACK_KWARGS = {
    "in_channels": 3,
    "image_h": 50,
    "image_w": 50,
    "state_channels": (32, 64, 128),
    "n_FR": 5,
    "n_heads": 4,
    "n_actions": 2,
    "init_action_logit_bias": [0.0, -2.0],
    "critic_kind": "distributional",
    "n_quantiles": 51,
    "pc_coef": 1.0,
}


def _infer_cross_layer_via(state_dict: dict) -> str:
    """
    Look at cell1.ft's qkv_feedback ModuleList depth to infer cross_layer_via.

    In 'ft' mode cell1 has n_feedback=2 external feedback sources (plus self),
    so cell1.ft.qkv_feedback has 3 entries (indices 0,1,2). In 'input' mode
    cell1 has n_feedback=0, so cell1.ft.qkv_feedback has 1 entry (just self).
    """
    fb_keys = [k for k in state_dict if k.startswith("cell1.ft.qkv_feedback.")]
    # Pull the maximum module-index ("cell1.ft.qkv_feedback.<i>.weight").
    indices = set()
    for k in fb_keys:
        parts = k.split(".")
        try:
            idx = int(parts[3])
            indices.add(idx)
        except (IndexError, ValueError):
            continue
    n_modules = (max(indices) + 1) if indices else 0
    # 'ft' → 1 (self) + 2 (cross-layer) = 3 modules. 'input' → 1 module.
    return "ft" if n_modules >= 3 else "input"


def load_checkpoint(
    ckpt_path: str,
    device: torch.device,
    override_kwargs: dict | None = None,
) -> Tuple[HRAModel, dict, int]:
    """
    Load a checkpoint and return (model, kwargs_used, iter).

    Priority for kwargs (highest first):
      1. override_kwargs (caller can pin specific values)
      2. checkpoint's saved model_kwargs (if present)
      3. _FALLBACK_KWARGS + inferred cross_layer_via from state_dict
    """
    state = torch.load(ckpt_path, map_location=device, weights_only=False)
    sd = state["model_state_dict"]

    if "model_kwargs" in state:
        kwargs = dict(state["model_kwargs"])
    else:
        kwargs = dict(_FALLBACK_KWARGS)
        kwargs["cross_layer_via"] = _infer_cross_layer_via(sd)

    if override_kwargs:
        kwargs.update(override_kwargs)

    # state_channels comes back as a list from JSON; HRAModel takes either.
    if "state_channels" in kwargs and not isinstance(kwargs["state_channels"], tuple):
        kwargs["state_channels"] = tuple(kwargs["state_channels"])

    model = HRAModel(**kwargs).to(device)
    model.load_state_dict(sd)
    model.eval()
    return model, kwargs, int(state.get("iter", -1))


def select_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")
