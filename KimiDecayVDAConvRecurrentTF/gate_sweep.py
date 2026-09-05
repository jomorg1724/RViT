"""Spatial microstim sweep: every attention map x every 4x4 cell x {stim, inhib}.

For each intervention target (att_vis channel, A_H1 / A_Z memory gates, A_H
vision gate) and each of the 16 stimulus cells, clamp the gate/channel at that
cell for the whole trial — stimulation (:=1) and inhibition (:=0) — and measure
behavior on three arms at a fixed near-threshold theta:
  invalid : cue S1(cell 0), change at S4(cell 3)   -> hit rate
  valid   : cue S1(cell 0), change at S1(cell 0)   -> hit rate
  fa      : cue S1(cell 0), no change              -> false-alarm rate

Gate pairs are 2-way softmaxes: inhibiting A_H1 == stimulating A_Z and vice
versa (same for A_H/A_X); att_vis := 0 is a true channel suppression.

Outputs: gate_sweep.json / .npz + three figures (invalid hits, valid hits, FA),
each laid out as maps x {stim, inhib} 4x4 heatmaps in stimulus-grid position.

Usage: python gate_sweep.py <checkpoint> <out_dir> [--theta 15] [--n-trials 200]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import torch

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from psychometric_kda_microstim import (
    build_model, forward_seq_stim, make_trials, cell_slice, S1, S4, T,
)
from envs import make_env
from train_rl import pick_device, seed_training_rngs

TARGETS = ["att_vis", "ah1", "az", "ah"]
MODES = [("stim", 1.0), ("inhib", 0.0)]
ARMS = ["invalid", "valid", "fa"]


def hit_rate(model, obs, device, classify_at_last=True, **stim_kw) -> float:
    hits, n = 0, 0
    with torch.no_grad():
        for i in range(0, len(obs), 100):
            R = forward_seq_stim(model, obs[i:i + 100].to(device), **stim_kw)
            logits = model.classify(R[:, -1])
            hits += int((logits.argmax(-1) == 1).sum().item())
            n += logits.shape[0]
    return hits / max(n, 1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("checkpoint")
    ap.add_argument("out_dir")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--theta", type=float, default=15.0,
                    help="fixed theta (between valid/invalid thresholds)")
    ap.add_argument("--n-trials", type=int, default=200)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    seed_training_rngs(0)
    device = pick_device(args.device)

    ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    assert ckpt["accum_mode"] == "kda"
    model = build_model(ckpt, device)

    env = make_env("vda16", T=T, frame_repeat=1, min_change_time=5, max_change_time=5,
                   noise_multiplier=5.0, curriculum=False, theta=args.theta)

    # Shared trial sets (clamp-independent): generated once, reused everywhere.
    obs = {
        "invalid": make_trials(env, args.n_trials, args.theta, 1, S4),
        "valid":   make_trials(env, args.n_trials, args.theta, 1, S1),
        "fa":      make_trials(env, args.n_trials, args.theta, 0, S1),
    }

    base = {arm: hit_rate(model, obs[arm], device, stim_cell=None) for arm in ARMS}
    print(f"[sweep] baselines @theta={args.theta}: "
          + "  ".join(f"{a}={base[a]:.3f}" for a in ARMS), flush=True)

    rates = {t: {m: {a: np.zeros((4, 4)) for a in ARMS} for m, _ in MODES}
             for t in TARGETS}
    for target in TARGETS:
        for mode, val in MODES:
            for cell in range(16):
                kw = dict(stim_cell=cell, target=target, stim_value=val)
                r, c = divmod(cell, 4)
                for arm in ARMS:
                    rates[target][mode][arm][r, c] = hit_rate(model, obs[arm], device, **kw)
            done = {a: rates[target][mode][a] for a in ARMS}
            print(f"[sweep] {target:8s} {mode:6s} done  invalid max={done['invalid'].max():.2f} "
                  f"min={done['invalid'].min():.2f}  fa max={done['fa'].max():.2f}", flush=True)

    out = {"theta": args.theta, "n_trials": args.n_trials, "targets": TARGETS,
           "baseline": base,
           "rates": {t: {m: {a: rates[t][m][a].tolist() for a in ARMS}
                         for m, _ in MODES} for t in TARGETS}}
    with open(os.path.join(args.out_dir, "gate_sweep.json"), "w") as f:
        json.dump(out, f, indent=2)
    np.savez(os.path.join(args.out_dir, "gate_sweep.npz"),
             **{f"{t}|{m}|{a}": rates[t][m][a]
                for t in TARGETS for m, _ in MODES for a in ARMS},
             **{f"baseline_{a}": base[a] for a in ARMS})

    for arm, ttl, cmap in [("invalid", "hit rate — change at UNCUED cell (S4)", "viridis"),
                           ("valid",   "hit rate — change at CUED cell (S1)",   "viridis"),
                           ("fa",      "false-alarm rate — no change",          "magma")]:
        fig, axes = plt.subplots(len(TARGETS), len(MODES), figsize=(7.2, 13.5),
                                 constrained_layout=True)
        for i, target in enumerate(TARGETS):
            for j, (mode, _) in enumerate(MODES):
                ax = axes[i][j]
                im = ax.imshow(rates[target][mode][arm], vmin=0, vmax=1, cmap=cmap)
                ax.set_title(f"{target} — {mode}", fontsize=10)
                for cell in range(16):
                    r, c = divmod(cell, 4)
                    ax.text(c, r, f"{rates[target][mode][arm][r, c]:.2f}",
                            ha="center", va="center", fontsize=7,
                            color="w" if rates[target][mode][arm][r, c] < 0.6 else "k")
                # mark cue (S1) and invalid-change (S4) positions
                for idx, mk in [(S1, "C"), (S4, "X")]:
                    r, c = divmod(idx, 4)
                    ax.add_patch(plt.Rectangle((c - .5, r - .5), 1, 1, fill=False,
                                               edgecolor="red" if mk == "C" else "cyan",
                                               lw=1.5))
                ax.set_xticks([]); ax.set_yticks([])
                fig.colorbar(im, ax=ax, shrink=0.8)
        fig.suptitle(f"gate sweep @ theta={args.theta}, n={args.n_trials} — {ttl}\n"
                     f"baseline {arm}={base[arm]:.2f}   (red=cue S1, cyan=invalid change S4)",
                     fontsize=11)
        fig.savefig(os.path.join(args.out_dir, f"gate_sweep_{arm}.png"), dpi=150)
        plt.close(fig)
        print(f"[sweep] wrote gate_sweep_{arm}.png", flush=True)

    print("[sweep] done", flush=True)


if __name__ == "__main__":
    main()
