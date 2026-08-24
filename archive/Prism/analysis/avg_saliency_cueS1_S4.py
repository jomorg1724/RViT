#!/usr/bin/env python3
"""
P4.2-precursor — Average saliency map S_t over 500 trials per cueing condition.

Conditions (both with no change, |Δ| = 0):
  A: Cue S_1 (top-left),     Validity = 1.0
  B: Cue S_4 (bottom-right), Validity = 1.0

For each condition we:
  1. Reset the env, OVERRIDE its random fields to force the desired condition,
     keeping baseline orientations and cue color random per trial.
  2. Run the trained model forward step-by-step, FORCING action=0 (wait) so
     every trial runs the full 30 timesteps. (For Δ=0 / no-change trials,
     action=0 is also the optimal trained behavior, so this is a benign override.)
  3. Capture the saliency map S_t ∈ ℝ^(1,12,12) at every timestep.

Outputs:
  figures/avg_saliency_heatmap_cueS1_cueS4.pdf — per-timestep heatmap strip,
      one section per cueing condition.
  figures/avg_alpha_trajectories_cueS1_cueS4.pdf — α_i(t) line plot, one panel
      per cueing condition. α_i is the per-quadrant aggregated saliency.
  analysis/avg_saliency_cueS1_S4.npz — raw arrays for re-plotting.

Usage:
  cd /Users/jonathanmorgan/AttentionManuscript/Prism
  python3 analysis/avg_saliency_cueS1_S4.py \
      --checkpoint checkpoints/prism_latest.pt \
      --n_trials 500
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import torch
import matplotlib.pyplot as plt

# Make the Prism root importable so `from model import PrismModel` works.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from env import ChangeDetectionEnv  # noqa: E402
from model import PrismModel  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def build_model_from_config(cfg_model: dict, device: torch.device) -> PrismModel:
    """Mirror of train.py::build_model so we instantiate exactly the same architecture."""
    iab = cfg_model.get("init_action_logit_bias", None)
    if iab is not None:
        iab = [float(v) for v in iab]
    model = PrismModel(
        in_channels=int(cfg_model.get("in_channels", 3)),
        image_h=int(cfg_model.get("image_h", 50)),
        image_w=int(cfg_model.get("image_w", 50)),
        feature_channels=int(cfg_model.get("feature_channels", 32)),
        memory_channels=int(cfg_model.get("memory_channels", 16)),
        n_actions=int(cfg_model.get("n_actions", 2)),
        inner_K=int(cfg_model.get("inner_K", 2)),
        inner_eps=float(cfg_model.get("inner_eps", 0.1)),
        actor_hidden=int(cfg_model.get("actor_hidden", 64)),
        critic_hidden=int(cfg_model.get("critic_hidden", 64)),
        decision_channels=int(cfg_model.get("decision_channels", 4)),
        decision_coarse_grid=int(cfg_model.get("decision_coarse_grid", 2)),
        init_action_logit_bias=iab,
        pc_pixel_coef=float(cfg_model.get("pc_pixel_coef", 1.0)),
        pc_feature_coef=float(cfg_model.get("pc_feature_coef", 0.1)),
        pc_autoenc_coef=float(cfg_model.get("pc_autoenc_coef", 1.0)),
    ).to(device)
    return model


def force_trial_conditions(env: ChangeDetectionEnv, cue_position: str, validity: float, change_true: int) -> None:
    """Override the env's random fields AFTER reset() to fix the cueing condition.

    The env reads cue_position and proportion at t=1 inside _next_observation, so
    overriding right after reset (which only computed the t=0 blank) is in time.
    Other fields (orientations, cue_color, change_time) remain trial-randomized so
    averaging across trials marginalizes over them.

    Note on terminology: env.cue_position uses {'left', 'right'} which map to S_1
    (top-left) and S_4 (bottom-right) respectively in the canonical S_i naming.
    """
    if cue_position not in ("left", "right"):
        raise ValueError(f"cue_position must be 'left' (S_1) or 'right' (S_4); got {cue_position}")
    env.cue_position = cue_position
    env.proportion = float(validity)
    env.change_true = int(change_true)


def collect_saliency(
    model: PrismModel,
    env: ChangeDetectionEnv,
    cue_position: str,
    n_trials: int,
    n_steps: int,
    device: torch.device,
    seed_base: int = 0,
):
    """Run n_trials episodes with the forced cueing condition; return per-timestep saliency stack.

    Returns
    -------
    saliencies : (n_trials, n_steps, 12, 12)   float32
    obs_example : (n_steps, 50, 50, 3)         float32 — first trial's frames, for diagnostic display
    """
    saliencies = np.zeros((n_trials, n_steps, 12, 12), dtype=np.float32)
    obs_example = None

    model.eval()
    with torch.no_grad():
        for trial in range(n_trials):
            # Per-trial reproducibility: each trial gets a deterministic seed.
            np.random.seed(seed_base + trial)

            obs = env.reset()
            force_trial_conditions(
                env, cue_position=cue_position, validity=1.0, change_true=0
            )

            M = model.init_memory(batch_size=1, device=device)

            obs_this_trial = []
            for t in range(n_steps):
                obs_this_trial.append(obs.astype(np.float32, copy=True))

                # Forward the model on the current observation.
                x_t = torch.from_numpy(obs.astype(np.float32, copy=False)).to(device)
                # env returns HWC; the V1 stem expects CHW. .contiguous() is required for MPS.
                x_t = x_t.permute(2, 0, 1).unsqueeze(0).contiguous()  # (1, 3, 50, 50)
                step = model.forward_step(x_t, M, return_aux=False)

                # Saliency S_t ∈ ℝ^(1, 1, 12, 12) — drop batch and channel dims for storage.
                saliencies[trial, t] = step.saliency[0, 0].detach().cpu().numpy()

                # Step the env with action=0 ("wait") to keep the trial alive.
                obs, _, done, _ = env.step(0)
                M = step.M_next

                if done:
                    # Should only fire at t = n_steps - 1 for our T=30-step env.
                    # Pad remaining timesteps with NaN if we exit early (rare).
                    if t + 1 < n_steps:
                        saliencies[trial, t + 1 :] = np.nan
                    break

            if obs_example is None:
                obs_example = np.array(obs_this_trial, dtype=np.float32)

            if (trial + 1) % 50 == 0:
                print(f"  [{cue_position}] trial {trial+1}/{n_trials}")

    return saliencies, obs_example


def alpha_per_quadrant(s_map: np.ndarray) -> np.ndarray:
    """Aggregate saliency over 6×6 sub-grids into per-quadrant scalars.

    s_map  : (..., 12, 12)
    Returns: (..., 4)   axes are [S_1, S_2, S_3, S_4]

    Quadrant layout (matches env):
      S_1 = top-left      (rows 0..5, cols 0..5)
      S_2 = bottom-left   (rows 6..11, cols 0..5)
      S_3 = top-right     (rows 0..5, cols 6..11)
      S_4 = bottom-right  (rows 6..11, cols 6..11)
    """
    a1 = s_map[..., :6, :6].sum(axis=(-1, -2))
    a2 = s_map[..., 6:, :6].sum(axis=(-1, -2))
    a3 = s_map[..., :6, 6:].sum(axis=(-1, -2))
    a4 = s_map[..., 6:, 6:].sum(axis=(-1, -2))
    return np.stack([a1, a2, a3, a4], axis=-1)


# ─────────────────────────────────────────────────────────────────────────────
# Plotting
# ─────────────────────────────────────────────────────────────────────────────

def plot_heatmap_strip(
    mean_S1: np.ndarray,  # (T, 12, 12)
    mean_S4: np.ndarray,  # (T, 12, 12)
    out_path: str,
    n_trials: int,
) -> None:
    """Two stacked 5×6 grids of heatmaps, one per cueing condition. Shared color scale."""
    T = mean_S1.shape[0]
    nrows_per_block = 5
    ncols = 6
    assert nrows_per_block * ncols >= T, "Need a bigger grid for T > 30."

    # Shared color scale across both conditions for direct visual comparison.
    vmin = 0.0
    vmax = float(max(np.nanmax(mean_S1), np.nanmax(mean_S4)))

    # Two stacked condition blocks plus a colorbar column.
    fig = plt.figure(figsize=(12, 14))
    gs = fig.add_gridspec(
        nrows=2 * nrows_per_block + 2,  # +2 for the two title rows
        ncols=ncols + 1,                # +1 for the colorbar
        width_ratios=[1] * ncols + [0.05],
        height_ratios=[0.2] + [1] * nrows_per_block + [0.2] + [1] * nrows_per_block,
        hspace=0.25,
        wspace=0.15,
    )

    fig.suptitle(
        f"Mean saliency map $S_t$ over {n_trials} trials  ·  $|\\Delta|=0$ (no change)  ·  Validity = 1.0",
        fontsize=14, y=0.995,
    )

    def _draw_block(mean_block: np.ndarray, row_offset: int, title: str) -> None:
        # Title row spans all columns.
        ax_title = fig.add_subplot(gs[row_offset, :ncols])
        ax_title.text(0.5, 0.5, title, ha="center", va="center", fontsize=13, fontweight="bold")
        ax_title.axis("off")

        last_im = None
        for t in range(T):
            r, c = divmod(t, ncols)
            ax = fig.add_subplot(gs[row_offset + 1 + r, c])
            last_im = ax.imshow(
                mean_block[t], cmap="viridis", vmin=vmin, vmax=vmax, interpolation="nearest"
            )
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(f"$t={t}$", fontsize=9)

            # Draw faint quadrant boundaries for visual reference.
            ax.axhline(5.5, color="white", lw=0.5, alpha=0.4)
            ax.axvline(5.5, color="white", lw=0.5, alpha=0.4)
        return last_im

    im_top = _draw_block(mean_S1, row_offset=0, title="Cue $S_1$ (top-left)")
    im_bot = _draw_block(mean_S4, row_offset=nrows_per_block + 1, title="Cue $S_4$ (bottom-right)")

    # Single shared colorbar on the right.
    cax = fig.add_subplot(gs[1 : 1 + nrows_per_block, ncols])
    fig.colorbar(im_top, cax=cax, label="$S_t$")
    cax2 = fig.add_subplot(gs[nrows_per_block + 2 : 2 * nrows_per_block + 2, ncols])
    fig.colorbar(im_bot, cax=cax2, label="$S_t$")

    fig.savefig(out_path, bbox_inches="tight", dpi=120)
    plt.close(fig)
    print(f"  saved: {out_path}")


def plot_alpha_trajectories(
    mean_S1: np.ndarray,  # (T, 12, 12)
    mean_S4: np.ndarray,  # (T, 12, 12)
    out_path: str,
    n_trials: int,
) -> None:
    """α_i(t) line plot, one panel per cueing condition."""
    T = mean_S1.shape[0]
    times = np.arange(T)

    alpha_S1 = alpha_per_quadrant(mean_S1)  # (T, 4)
    alpha_S4 = alpha_per_quadrant(mean_S4)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    fig.suptitle(
        f"Per-quadrant aggregated saliency $\\alpha_i(t)$  ·  averaged over {n_trials} trials  ·  $|\\Delta|=0$",
        fontsize=14, y=1.02,
    )

    quadrant_labels = [r"$\alpha_{S_1}$ (top-left)",
                       r"$\alpha_{S_2}$ (bottom-left)",
                       r"$\alpha_{S_3}$ (top-right)",
                       r"$\alpha_{S_4}$ (bottom-right)"]
    colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]

    for ax, alpha_block, cue_label in [
        (axes[0], alpha_S1, "Cue $S_1$ (Validity = 1.0)"),
        (axes[1], alpha_S4, "Cue $S_4$ (Validity = 1.0)"),
    ]:
        for q in range(4):
            ax.plot(times, alpha_block[:, q], label=quadrant_labels[q],
                    color=colors[q], linewidth=2)
        ax.set_xlabel("Timestep $t$")
        ax.set_ylabel(r"$\alpha_i(t) = \sum_{(h,w) \in S_i} S_t(h,w)$")
        ax.set_title(cue_label)
        ax.axvline(1, color="black", linestyle=":", alpha=0.5, label="cue frame ($t=1$)")
        ax.axvline(3, color="grey", linestyle=":", alpha=0.4, label="Gabor onset ($t=3$)")
        ax.legend(fontsize=9, loc="upper right")
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", dpi=120)
    plt.close(fig)
    print(f"  saved: {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Avg saliency over 500 trials, Cue S_1 vs Cue S_4.")
    parser.add_argument("--config", type=str,
                        default=os.path.join(_ROOT, "config", "prism_config.json"))
    parser.add_argument("--checkpoint", type=str,
                        default=os.path.join(_ROOT, "checkpoints", "prism_latest.pt"))
    parser.add_argument("--n_trials", type=int, default=500)
    parser.add_argument("--n_steps", type=int, default=30,
                        help="Maximum steps per trial. The env's T=29 means actual length is 30 obs.")
    parser.add_argument("--out_heatmap", type=str,
                        default=os.path.join(_ROOT, "figures", "avg_saliency_heatmap_cueS1_cueS4.pdf"))
    parser.add_argument("--out_alpha", type=str,
                        default=os.path.join(_ROOT, "figures", "avg_alpha_trajectories_cueS1_cueS4.pdf"))
    parser.add_argument("--out_data", type=str,
                        default=os.path.join(_ROOT, "analysis", "avg_saliency_cueS1_S4.npz"))
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out_heatmap), exist_ok=True)
    os.makedirs(os.path.dirname(args.out_data), exist_ok=True)

    cfg = json.load(open(args.config))
    device = _device()
    print(f"device: {device}")

    # ── Build model and load checkpoint ────────────────────────────────────
    model = build_model_from_config(cfg["model"], device)
    print(f"loading checkpoint: {args.checkpoint}")
    ckpt = torch.load(args.checkpoint, map_location=device)
    state_dict = ckpt["model_state_dict"] if "model_state_dict" in ckpt else ckpt
    missing, unexpected = model.load_state_dict(state_dict, strict=False)
    if missing:
        print(f"  WARNING: missing keys (init from random): {missing}")
    if unexpected:
        print(f"  WARNING: unexpected keys (ignored): {unexpected}")
    model.eval()

    # Quick sanity: print actor bias (Fix-1 verification).
    with torch.no_grad():
        bias = model.actor.fc2.bias.detach().cpu().tolist()
    print(f"  actor.fc2.bias = {bias}  (expect ≈ [0.0, -4.0] if Fix-1 was applied)")

    # ── Build env ──────────────────────────────────────────────────────────
    env_cfg = cfg["environment"]
    env = ChangeDetectionEnv(
        theta=float(env_cfg.get("theta_start", 65.0)),
        noise_multiplier=float(env_cfg.get("noise_multiplier", 10.0)),
        min_change_time=int(env_cfg.get("min_change_time", 11)),
        max_change_time=int(env_cfg.get("max_change_time", 25)),
    )

    # ── Collect saliency for each condition ────────────────────────────────
    print(f"\nCollecting saliency for Cue S_1, Validity 1.0, |Δ|=0 ({args.n_trials} trials)...")
    sal_S1, obs_S1 = collect_saliency(
        model, env, cue_position="left",
        n_trials=args.n_trials, n_steps=args.n_steps,
        device=device, seed_base=1000,
    )

    print(f"\nCollecting saliency for Cue S_4, Validity 1.0, |Δ|=0 ({args.n_trials} trials)...")
    sal_S4, obs_S4 = collect_saliency(
        model, env, cue_position="right",
        n_trials=args.n_trials, n_steps=args.n_steps,
        device=device, seed_base=2000,
    )

    mean_S1 = np.nanmean(sal_S1, axis=0)  # (T, 12, 12)
    mean_S4 = np.nanmean(sal_S4, axis=0)
    print(f"\nmean S_1 saliency: shape={mean_S1.shape}, range=[{mean_S1.min():.4g}, {mean_S1.max():.4g}]")
    print(f"mean S_4 saliency: shape={mean_S4.shape}, range=[{mean_S4.min():.4g}, {mean_S4.max():.4g}]")

    # ── Save raw arrays ────────────────────────────────────────────────────
    np.savez(
        args.out_data,
        mean_S1=mean_S1, mean_S4=mean_S4,
        sal_S1=sal_S1, sal_S4=sal_S4,
        obs_S1_example=obs_S1, obs_S4_example=obs_S4,
        config=json.dumps(cfg), n_trials=args.n_trials,
    )
    print(f"\nsaved raw arrays: {args.out_data}")

    # ── Plot ───────────────────────────────────────────────────────────────
    print("\nrendering figures...")
    plot_heatmap_strip(mean_S1, mean_S4, args.out_heatmap, n_trials=args.n_trials)
    plot_alpha_trajectories(mean_S1, mean_S4, args.out_alpha, n_trials=args.n_trials)

    print("\ndone.")


if __name__ == "__main__":
    main()
