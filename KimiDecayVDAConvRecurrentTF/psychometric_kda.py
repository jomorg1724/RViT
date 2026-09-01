"""Psychometric curves for the KDA conv-memory model on vda16.

Two experiment blocks, one figure each (plus raw npz/json):

Block A — validity gradient (identical protocol to the ConvMemoryModel suite):
  30 signed change magnitudes |Δθ| in [0, 65] deg × 16 cue proportions k/16
  × n-trials. Cue fixed on cell S1 (index 0, red). Every trial is a change
  trial; the change lands on the cued cell with probability = proportion,
  else a uniformly random other cell. θ=0 is an effective no-change trial
  (false-alarm floor).

Block B — pinned-location cueing comparison (the headline cueing-effect test):
  same θ sweep, cue on S1 at 100% validity (proportion 1.0), but the change
  location is PINNED: S1 (valid, cued) vs S4 (invalid; index 3, top row far
  from S1). If cueing works, the valid curve shifts left of the invalid one.

Declaration = classifier argmax on R@last == 1 ("change").

Usage:
  python psychometric_kda.py <checkpoint> <out_dir> [--device cuda]
  python psychometric_kda.py <ckpt> <out> --n-trials 5 --n-theta 3 --n-props 2   # smoke
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
from kda_conv_memory_model import KDAConvMemoryModel
from envs import make_env
from train_rl import pick_device, seed_training_rngs

T = 7
THETAS_FULL = np.linspace(0.0, 65.0, 30)
PROPS_FULL = [i / 16 for i in range(1, 17)]   # all 16 ring levels
S1, S4 = 0, 3                                  # pinned cells: cued vs invalid top-row


def build_model(ckpt: dict, device) -> KDAConvMemoryModel:
    model = KDAConvMemoryModel(
        n_channels=ckpt["n_channels"], proto_dim=ckpt["proto_dim"],
        map_size=ckpt["map_size"],
        memory_noise_std=0.05,          # matches kda seed-0 training contract
        frame_window=ckpt.get("frame_window", 1),
        frame_stride=ckpt.get("frame_stride", 1),
        mem_every=ckpt.get("mem_every", 1),
        accum_mode=ckpt["accum_mode"], accum_decay=ckpt["accum_decay"],
        kda_heads=ckpt["kda_heads"], kda_head_dim=ckpt["kda_head_dim"],
    ).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    return model


def run_block(model, env, props, thetas, n_trials, device, pin_change=None):
    """counts[pi, ti] = 'change' declarations. pin_change: None (env's natural
    placement) or a cell index forced on every trial."""
    counts = np.zeros((len(props), len(thetas)), dtype=np.int64)
    with torch.no_grad():
        for pi, prop in enumerate(props):
            for ti, theta in enumerate(thetas):
                obs_list = []
                for _ in range(n_trials):
                    env.reset()
                    env.cue_index = 0
                    env.cue_color = "red"
                    env.proportion = float(prop)
                    env.change_true = 1
                    if pin_change is None:
                        env.change_index = int(env._draw_change_index())
                    else:
                        env.change_index = int(pin_change)
                    env.orientation_change = float(theta) * float(np.random.choice([-1.0, 1.0]))
                    frames = [env.step(0)[0] for _ in range(T)]
                    obs_list.append(np.stack(frames))
                obs = torch.from_numpy(np.stack(obs_list)).float().to(device)
                R = model.forward_seq(obs)
                logits = model.classify(R[:, -1])
                counts[pi, ti] = int((logits.argmax(-1) == 1).sum().item())
            tag = "natural" if pin_change is None else f"pinned S{pin_change + 1}"
            print(f"[psychometric-kda] prop={prop:.3f} ({tag}): done", flush=True)
    return counts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("checkpoint")
    ap.add_argument("out_dir")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--n-trials", type=int, default=100)
    ap.add_argument("--n-theta", type=int, default=30)
    ap.add_argument("--n-props", type=int, default=16)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    seed_training_rngs(0)
    device = pick_device(args.device)

    thetas = THETAS_FULL if args.n_theta == 30 else np.linspace(0.0, 65.0, args.n_theta)
    props = PROPS_FULL if args.n_props == 16 else PROPS_FULL[: args.n_props]

    ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    assert ckpt["accum_mode"] == "kda", f"expected a kda checkpoint, got {ckpt['accum_mode']}"
    model = build_model(ckpt, device)

    env = make_env("vda16", T=T, frame_repeat=1, min_change_time=5, max_change_time=5,
                   noise_multiplier=5.0, curriculum=False, theta=65.0)

    # ---- Block A: validity gradient (natural change placement) ----
    counts_a = run_block(model, env, props, thetas, args.n_trials, device)

    # ---- Block B: pinned S1 (valid) vs pinned S4 (invalid), 100% validity ----
    counts_s1 = run_block(model, env, [1.0], thetas, args.n_trials, device, pin_change=S1)
    counts_s4 = run_block(model, env, [1.0], thetas, args.n_trials, device, pin_change=S4)

    np.savez(os.path.join(args.out_dir, "psychometric_kda.npz"),
             thetas=thetas, proportions=np.array(props), counts=counts_a,
             counts_pinned_s1=counts_s1, counts_pinned_s4=counts_s4,
             n_trials=args.n_trials)
    with open(os.path.join(args.out_dir, "psychometric_kda.json"), "w") as f:
        json.dump({"thetas": thetas.tolist(), "proportions": props,
                   "counts": counts_a.tolist(),
                   "counts_pinned_s1": counts_s1.tolist(),
                   "counts_pinned_s4": counts_s4.tolist(),
                   "n_trials": args.n_trials}, f, indent=2)

    # Figure A: validity gradient
    fig, ax = plt.subplots(figsize=(8, 5.5))
    cmap = plt.get_cmap("viridis")
    for pi, prop in enumerate(props):
        ax.plot(thetas, counts_a[pi], marker="o", ms=2.5, lw=1.2,
                color=cmap(pi / max(len(props) - 1, 1)), label=f"{prop:.3f}")
    ax.set_xlabel("change magnitude |Δθ| (degrees)")
    ax.set_ylabel(f'"change" declarations (out of {args.n_trials})')
    ax.set_title("vda16 psychometric curves — KDA accumulator\n"
                 "(change trials only; θ=0 = effective no-change; cue on S1)")
    ax.set_ylim(0, args.n_trials + 4)
    ax.grid(alpha=0.3)
    ax.legend(title="cue proportion", fontsize=7, ncol=2, title_fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(args.out_dir, "psychometric_kda.png"), dpi=140)
    plt.close(fig)

    # Figure B: the cueing-effect comparison (valid vs invalid at 100%)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(thetas, counts_s1[0], marker="o", ms=3.5, lw=1.6, color="tab:green",
            label="valid: cue S1, change S1")
    ax.plot(thetas, counts_s4[0], marker="s", ms=3.5, lw=1.6, color="tab:red",
            label="invalid: cue S1, change S4")
    ax.set_xlabel("change magnitude |Δθ| (degrees)")
    ax.set_ylabel(f'"change" declarations (out of {args.n_trials})')
    ax.set_title("vda16 cueing effect — KDA accumulator (100% validity)\n"
                 "valid vs invalid change location, cue pinned on S1")
    ax.set_ylim(0, args.n_trials + 4)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(args.out_dir, "psychometric_kda_valid_vs_invalid.png"), dpi=140)
    plt.close(fig)

    print(f"[psychometric-kda] DONE. outputs in {args.out_dir}")


if __name__ == "__main__":
    main()
