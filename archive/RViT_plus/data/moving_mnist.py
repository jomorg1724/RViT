"""
MovingMNIST dataset for RViT+ Stage 1 pretraining.

Generates sequences of two MNIST digits bouncing around a 50×50 frame at
random initial positions and velocities. Frames are 3-channel (each digit
rendered in a different color channel for richer spatial structure).

Inputs to the model are normalized to [-1, 1] matching ChangeDetectionEnv.

Each item is a sequence (T, 3, 50, 50). The dataset is "generated on the
fly" — each __getitem__ creates a fresh sequence, so epoch-size is virtual
and we control total training data via the iter count and batch size.

Backed by `torchvision.datasets.MNIST` for the digit images.
"""
from __future__ import annotations

import os
import random
from typing import Tuple

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import datasets, transforms


# Default frame and sequence dimensions.
FRAME_HW = 50      # ChangeDetectionEnv-compatible
DIGIT_HW = 14      # we resize MNIST 28→14 to fit two digits in 50×50
SEQ_LEN = 10       # 10 frames per training sequence


def _load_mnist_images(root: str | None = None) -> np.ndarray:
    """Load MNIST training images as a (60000, 28, 28) uint8 array."""
    if root is None:
        # Default location alongside the project, downloaded on first use.
        root = os.path.expanduser("~/.cache/rvit_plus_data")
        os.makedirs(root, exist_ok=True)
    ds = datasets.MNIST(root=root, train=True, download=True)
    # ds.data is a (60000, 28, 28) tensor of uint8.
    return ds.data.numpy()


class MovingMNIST(Dataset):
    """Each item is a fresh sequence of two bouncing MNIST digits.

    Args
    ----
    n_sequences  : virtual dataset length (each __getitem__ is procedural).
    seq_len      : frames per sequence (default 10).
    frame_hw     : output frame size in pixels (default 50, matches env).
    digit_hw     : digit size after resize (default 14).
    n_digits     : digits per sequence (default 2 — the canonical setting).
    seed_base    : RNG seed offset for reproducibility per-item.
    mnist_root   : optional cache directory for torchvision MNIST.

    Returns from __getitem__
    ------------------------
    sequence : torch.float32 (seq_len, 3, frame_hw, frame_hw), in [-1, 1].
    """

    def __init__(
        self,
        n_sequences: int = 10000,
        seq_len: int = SEQ_LEN,
        frame_hw: int = FRAME_HW,
        digit_hw: int = DIGIT_HW,
        n_digits: int = 2,
        seed_base: int = 0,
        mnist_root: str | None = None,
    ) -> None:
        super().__init__()
        self.n_sequences = int(n_sequences)
        self.seq_len = int(seq_len)
        self.frame_hw = int(frame_hw)
        self.digit_hw = int(digit_hw)
        self.n_digits = int(n_digits)
        self.seed_base = int(seed_base)

        # Load MNIST and pre-resize all digits.
        raw = _load_mnist_images(root=mnist_root)
        # Pre-resize all digits to digit_hw via PIL (one-time cost).
        # Use torch's bilinear resize to keep it dependency-free.
        # Shape: (60000, digit_hw, digit_hw) float32 in [0, 1].
        t = torch.from_numpy(raw).float().unsqueeze(1) / 255.0  # (60000, 1, 28, 28)
        t = torch.nn.functional.interpolate(
            t, size=(digit_hw, digit_hw), mode="bilinear", align_corners=False
        )
        self._digits = t.squeeze(1).numpy()  # (60000, digit_hw, digit_hw)

    def __len__(self) -> int:
        return self.n_sequences

    def __getitem__(self, idx: int) -> torch.Tensor:
        # Per-item RNG for reproducibility under multi-worker loading.
        rng = np.random.RandomState(self.seed_base + idx)

        H = self.frame_hw
        D = self.digit_hw
        # Choose n_digits random digits.
        digit_indices = rng.randint(0, self._digits.shape[0], size=self.n_digits)
        sprites = [self._digits[i] for i in digit_indices]  # each (D, D) in [0,1]

        # Channel assignment: each digit goes into one of the 3 color channels.
        # For 2 digits: ch 0 (red) and ch 1 (green). Background black.
        channels = list(range(self.n_digits))[:3]
        # If n_digits > 3, wrap. (Two-digit MovingMNIST is the standard.)

        # Random initial positions and velocities.
        # Position range: digit can be anywhere fully inside the frame.
        # Velocity in pixels-per-frame; bounce off walls.
        pos = rng.uniform(0, H - D, size=(self.n_digits, 2))   # (xy)
        vel = rng.uniform(-2.5, 2.5, size=(self.n_digits, 2))  # px per frame

        seq = np.zeros((self.seq_len, 3, H, H), dtype=np.float32)
        for t in range(self.seq_len):
            for d_idx in range(self.n_digits):
                px, py = pos[d_idx]
                ch = channels[d_idx % len(channels)]
                ix, iy = int(round(px)), int(round(py))
                ix = max(0, min(H - D, ix))
                iy = max(0, min(H - D, iy))
                seq[t, ch, iy:iy + D, ix:ix + D] += sprites[d_idx]
            # Advance positions; bounce off walls.
            pos += vel
            for d_idx in range(self.n_digits):
                for axis in range(2):
                    if pos[d_idx, axis] < 0:
                        pos[d_idx, axis] = -pos[d_idx, axis]
                        vel[d_idx, axis] = -vel[d_idx, axis]
                    elif pos[d_idx, axis] > H - D:
                        pos[d_idx, axis] = 2 * (H - D) - pos[d_idx, axis]
                        vel[d_idx, axis] = -vel[d_idx, axis]

        # Clip and normalize to [-1, 1].
        seq = np.clip(seq, 0.0, 1.0)
        seq = seq * 2.0 - 1.0
        return torch.from_numpy(seq)


def generate_moving_mnist_batch(
    batch_size: int,
    seq_len: int = SEQ_LEN,
    frame_hw: int = FRAME_HW,
    digit_hw: int = DIGIT_HW,
    n_digits: int = 2,
    rng_seed: int | None = None,
    dataset: MovingMNIST | None = None,
) -> torch.Tensor:
    """Convenience: build a (B, T, 3, H, W) batch directly.

    If `dataset` is passed, it is reused (cheaper for repeated calls);
    otherwise a fresh dataset is constructed (lazy, costs ~5s the first time
    MNIST is downloaded).
    """
    if dataset is None:
        dataset = MovingMNIST(
            n_sequences=batch_size,
            seq_len=seq_len,
            frame_hw=frame_hw,
            digit_hw=digit_hw,
            n_digits=n_digits,
            seed_base=rng_seed if rng_seed is not None else 0,
        )
    if rng_seed is None:
        # Random sampling per batch element.
        items = [dataset[random.randint(0, dataset.n_sequences - 1)] for _ in range(batch_size)]
    else:
        items = [dataset[rng_seed + i] for i in range(batch_size)]
    return torch.stack(items, dim=0)  # (B, T, 3, H, W)


# Keep the older name as an alias too (in case other modules already import it).
MovingBlobsDataset = MovingMNIST
generate_moving_blobs_batch = generate_moving_mnist_batch
