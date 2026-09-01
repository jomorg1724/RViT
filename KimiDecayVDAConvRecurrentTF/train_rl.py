"""Minimal training utilities shim for the motion-dmc experiment folder.

Only the two helpers used by pretrain_conv_memory.py, extracted verbatim from
the main RViT project's train_rl.py so this folder does not need to import the
full RL stack (which drags in model.py / vae_frontend / etc.).
"""
from __future__ import annotations

import random

import numpy as np
import torch


def pick_device(name: str) -> torch.device:
    if name in ("mps", "cuda", "cpu"):
        return torch.device(name)
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def seed_training_rngs(seed: int) -> None:
    """Seed model and environment RNGs before environment construction."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
