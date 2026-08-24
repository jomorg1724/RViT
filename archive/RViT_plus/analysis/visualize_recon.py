"""Reconstruction visualization for a video-compression RViT+ checkpoint.

Loads a checkpoint, samples a few MovingMNIST sequences, runs full
compress-and-reconstruct, and saves a figure showing input frames vs
reconstructed frames per timestep.

Usage:
    .venv/bin/python RViT_plus/analysis/visualize_recon.py
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus.data import MovingMNIST
from RViT_plus.model import RViTPlusModel


def _select_device(override=None):
    if override:
        return torch.device(override)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def load_model(ckpt_path: str, device: torch.device) -> RViTPlusModel:
    state = torch.load(ckpt_path, map_location=device, weights_only=False)
    kw = dict(state.get("model_kwargs", {}))
    if "state_channels" in kw and not isinstance(kw["state_channels"], tuple):
        kw["state_channels"] = tuple(kw["state_channels"])
    kw.setdefault("in_channels", 3)
    kw.setdefault("image_h", 50)
    kw.setdefault("image_w", 50)
    kw.setdefault("stem_out_channels", 64)
    kw.setdefault("state_channels", (64, 96, 128))
    kw.setdefault("n_FR", 4)
    kw.setdefault("n_heads", 4)
    kw.setdefault("latent_channels", 16)
    kw.pop("latent_dim", None)  # legacy kwarg from pre-run-8 checkpoints
    kw.setdefault("enable_skips", True)
    kw.setdefault("skip_scale", 0.3)
    kw.setdefault("max_T", 32)
    kw.pop("n_BR", None)  # accepted by model.py but ignored
    model = RViTPlusModel(**kw).to(device)
    model.load_state_dict(state["model_state_dict"])
    model.eval()
    return model


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", default=os.path.join(_PROJECT_ROOT, "RViT_plus", "checkpoints", "rvit_plus_latest.pt"))
    p.add_argument("--out", default=os.path.join(_HERE, "figures", "recon.png"))
    p.add_argument("--n-sequences", type=int, default=2)
    p.add_argument("--seq-len", type=int, default=10)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args(argv)

    if not os.path.exists(args.ckpt):
        print(f"checkpoint not found: {args.ckpt}")
        return 1
    device = _select_device()
    print(f"[recon] {args.ckpt} on {device}")
    model = load_model(args.ckpt, device)

    dataset = MovingMNIST(n_sequences=args.n_sequences, seq_len=args.seq_len,
                          frame_hw=50, digit_hw=14, n_digits=2, seed_base=args.seed)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available; aborting.")
        return 1

    # One row per timestep; columns interleave (input, recon, err) per sequence.
    fig, axes = plt.subplots(args.seq_len, 3 * args.n_sequences,
                              figsize=(3 * args.n_sequences * 2.2, args.seq_len * 2.2),
                              squeeze=False)

    with torch.no_grad():
        for s in range(args.n_sequences):
            seq = dataset[s].to(device).unsqueeze(0)  # (1, T, 3, H, W)
            out = model.compress_and_reconstruct(seq)
            recons = torch.stack(out.recons, dim=1)[0].cpu().numpy()  # (T, 3, H, W)
            seq_np = seq[0].cpu().numpy()
            for t in range(args.seq_len):
                def _show(arr, ax, title):
                    a = (arr + 1.0) / 2.0
                    a = np.clip(np.transpose(a, (1, 2, 0)), 0, 1)
                    ax.imshow(a)
                    ax.set_title(title, fontsize=7)
                    ax.axis("off")
                col0 = 3 * s
                _show(seq_np[t], axes[t, col0], f"s{s} t{t} input")
                _show(recons[t], axes[t, col0 + 1], f"s{s} t{t} recon")
                _show(seq_np[t] - recons[t], axes[t, col0 + 2], f"s{s} t{t} err")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    plt.tight_layout()
    plt.savefig(args.out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[recon] figure → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
