"""
Plot V6 training curves from the trainer's history.jsonl.

    .venv/bin/python v6_VizdoomArena/analysis/plot_training.py \
        [--history ~/rvit_plus_checkpoints/v6_vizdoom_arena/history.jsonl]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np


def _smooth(x, w=51):
    x = np.asarray(x, dtype=np.float64)
    if len(x) < 3:
        return x
    w = min(w, max(3, (len(x) // 10) | 1))
    k = np.ones(w) / w
    pad = np.pad(x, (w // 2, w // 2), mode="edge")
    return np.convolve(pad, k, mode="valid")[: len(x)]


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--history", default=os.path.expanduser(
        "~/rvit_plus_checkpoints/v6_vizdoom_arena/history.jsonl"))
    p.add_argument("--out", default=None, help="output PNG (default: alongside history)")
    args = p.parse_args(argv)

    rows = []
    with open(args.history) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    if not rows:
        print("history is empty")
        return 1

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    it = [r["iter"] for r in rows]
    panels = [
        ("rollout/ep_kills", "kills / episode"),
        ("rollout/ep_return", "shaped return / episode"),
        ("rollout/ep_length", "episode length"),
        ("loss_value", "critic quantile-Huber"),
        ("loss_policy", "PAC actor loss"),
        ("loss_entropy", "−entropy"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(15, 7))
    for ax, (key, title) in zip(axes.flat, panels):
        y = np.array([r.get(key, np.nan) for r in rows], dtype=np.float64)
        m = np.isfinite(y)
        if m.any():
            ax.plot(np.array(it)[m], y[m], alpha=0.25, lw=0.8)
            ax.plot(np.array(it)[m], _smooth(y[m]), lw=1.8)
        ax.set_title(title)
        ax.set_xlabel("iteration")
        ax.grid(alpha=0.3)
    fig.suptitle(f"V6 arena training — {len(rows)} iterations, "
                 f"{rows[-1].get('rollout/env_steps', 0):,.0f} env steps")
    fig.tight_layout()
    out = args.out or os.path.join(os.path.dirname(args.history), "training_curves.png")
    fig.savefig(out, dpi=130)
    print(f"[plot] → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
