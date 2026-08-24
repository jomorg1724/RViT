"""
Per-layer attention-map visualizer for HRA.

Loads a checkpoint, runs a single rollout on ChangeDetectionEnv, and saves a
figure showing how attention evolves over the trial and across the three
GridCell layers (C₁ 12×12, C₂ 6×6, C₃ 3×3).

This is the first MODEL_DESIGN.md §7 interpretability analysis: per-layer
attention dynamics, the multi-layer analog of the Herman & Morgan 2025
recurrent-ViT attention-trajectory visualisations.

The attention map shown is the *final-iteration* (k = n_FR − 1) C_ℓ map,
mean-pooled over heads, and then mean-pooled over query positions — i.e. the
"per-key" attention distribution showing which patches got attended *to* on
average across all queries.

Usage:
    /usr/bin/python3 HRA/analysis/attention_maps.py
        [--ckpt HRA/checkpoints/hra_latest.pt]
        [--out HRA/analysis/figures/attention_maps_iter499.png]
        [--n-steps 29]
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

from HRA.analysis._load import load_checkpoint, select_device
from HRA.env import ChangeDetectionEnv


def collect_one_rollout(model, env, device, force_action=None):
    """Run one episode, returning per-timestep frames and StepOutputs."""
    model.eval()
    from torch.distributions import Categorical

    frames = []
    step_outs = []
    actions = []
    rewards = []

    with torch.no_grad():
        obs = env.reset()
        if isinstance(obs, tuple):
            obs = obs[0]
        states = model.init_states(1, device=device)
        done = False
        while not done:
            frames.append(np.asarray(obs, dtype=np.float32).copy())
            x = (
                torch.from_numpy(np.ascontiguousarray(frames[-1].transpose(2, 0, 1)))
                .to(device)
                .unsqueeze(0)
            )
            step = model.forward_step(x, states)
            step_outs.append(step)

            if force_action is not None:
                a = int(force_action)
            else:
                a = int(Categorical(logits=step.action_logits[0]).sample().item())
            actions.append(a)

            step_result = env.step(a)
            if len(step_result) == 5:
                obs, r, terminated, truncated, _ = step_result
                done = bool(terminated or truncated)
            else:
                obs, r, done, _ = step_result
            rewards.append(float(r))
            states = step.layer_states_new

    return frames, step_outs, actions, rewards, env.change_time, env.cue_position


def attention_per_key(attn: torch.Tensor, layer_grid: int) -> np.ndarray:
    """
    Reduce an attention map (B=1, n_heads, N, N) to a (H, W) heatmap showing
    where attention 'lands' on average (mean over heads, mean over queries).
    """
    a = attn[0]                              # (n_heads, N, N)
    a = a.mean(dim=0)                        # (N, N)  mean over heads
    per_key = a.mean(dim=0)                  # (N,)    mean over queries
    return per_key.detach().cpu().numpy().reshape(layer_grid, layer_grid)


def render_figure(frames, step_outs, actions, rewards, change_time, cue_pos, out_path):
    """Save a grid: rows = timesteps, columns = [input, C₁ attn, C₂ attn, C₃ attn]."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[attention-maps] matplotlib not available; saving raw arrays instead.")
        np.savez_compressed(
            out_path.replace(".png", ".npz"),
            frames=np.stack(frames),
            attn_c1=np.stack([attention_per_key(s.attn_per_layer[-1][0], 12) for s in step_outs]),
            attn_c2=np.stack([attention_per_key(s.attn_per_layer[-1][1], 6) for s in step_outs]),
            attn_c3=np.stack([attention_per_key(s.attn_per_layer[-1][2], 3) for s in step_outs]),
            actions=np.array(actions),
            rewards=np.array(rewards),
            change_time=change_time,
        )
        return

    T = len(frames)
    fig, axes = plt.subplots(T, 4, figsize=(12, 1.7 * T))
    fig.suptitle(
        f"HRA attention dynamics — trial of length {T}, change_time={change_time}, "
        f"cue={cue_pos}, total_reward={sum(rewards):.2f}, "
        f"pressed_at={'never' if 1 not in actions else actions.index(1)}",
        fontsize=10, y=0.995,
    )

    for t in range(T):
        # Column 0 — input frame (RGB, env range [-1, 1] → [0, 1] for display).
        ax = axes[t, 0]
        img = (frames[t] + 1.0) / 2.0
        img = np.clip(img, 0, 1)
        ax.imshow(img)
        cue_marker = "•" if t < 3 else ""  # cue is shown briefly at start
        title = f"t={t:>2d}"
        if t == change_time:
            title += " ←CHANGE"
        if actions[t] == 1:
            title += " (PRESS)"
        ax.set_title(title, fontsize=7)
        ax.axis("off")

        # Columns 1, 2, 3 — C₁, C₂, C₃ attention maps (final iteration).
        for col, (layer_idx, grid_h, name) in enumerate([(0, 12, "C₁"), (1, 6, "C₂"), (2, 3, "C₃")]):
            ax = axes[t, col + 1]
            attn = step_outs[t].attn_per_layer[-1][layer_idx]  # final iter, layer
            h = attention_per_key(attn, grid_h)
            ax.imshow(h, cmap="viridis", interpolation="nearest")
            ax.set_title(f"{name} attn  μ={h.mean():.3f} σ={h.std():.3f}", fontsize=7)
            ax.axis("off")

    plt.tight_layout()
    plt.subplots_adjust(top=0.985)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"[attention-maps] figure saved to {out_path}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Visualize HRA per-layer attention maps over a trial.")
    parser.add_argument("--ckpt", default=os.path.join(_PROJECT_ROOT, "HRA", "checkpoints", "hra_latest.pt"))
    parser.add_argument("--out", default=os.path.join(_HERE, "figures", "attention_maps.png"))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--force-action", type=int, default=None,
                        help="If set (0 or 1), force this action every step. Useful for diagnosing "
                             "attention dynamics on collapsed checkpoints.")
    parser.add_argument("--cross-layer-via", default=None, choices=[None, "input", "ft"],
                        help="Override the cross_layer_via inference. Use if auto-detection fails.")
    args = parser.parse_args(argv)

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    if not os.path.exists(args.ckpt):
        print(f"[attention-maps] checkpoint not found: {args.ckpt}")
        return 1

    device = select_device()
    override = {"cross_layer_via": args.cross_layer_via} if args.cross_layer_via else None
    model, kwargs_used, ckpt_iter = load_checkpoint(args.ckpt, device, override_kwargs=override)
    print(f"[attention-maps] loaded {args.ckpt}")
    print(f"                 device={device}, ckpt_iter={ckpt_iter}, "
          f"cross_layer_via={kwargs_used['cross_layer_via']}")

    env = ChangeDetectionEnv()
    frames, step_outs, actions, rewards, change_time, cue_pos = collect_one_rollout(
        model, env, device, force_action=args.force_action,
    )
    print(f"[attention-maps] rollout: length={len(frames)} change_time={change_time} "
          f"cue={cue_pos} total_reward={sum(rewards):.3f} "
          f"pressed_at={'never' if 1 not in actions else actions.index(1)}")
    render_figure(frames, step_outs, actions, rewards, change_time, cue_pos, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
