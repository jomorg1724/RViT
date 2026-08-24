#!/usr/bin/env python3
"""
P4.2-precursor (with-change variant) — Average saliency map S_t over 500 trials
per cueing condition, with a forced change at S_1, Δ = +45°, t* = 15.

Conditions:
  A: Cue S_1 (top-left),     Validity = 1.0, Change S_1, Δ=+45°, t*=15  — VALID
  B: Cue S_4 (bottom-right), Validity = 1.0, Change S_1, Δ=+45°, t*=15  — INVALID

This is the canonical valid-vs-invalid comparison the user flagged as the most
diagnostic in PROJECT_PLAN.md (P2.2 / P4.2). With a strong change (Δ=45° vs
σ_noise=10°) the prediction-error signature at the change location should be
unmistakable; what differs between the two conditions is the *prior* attentional
state at S_1 set by the cue.

Same machinery as analysis/avg_saliency_cueS1_S4.py: force conditions after env
reset, force action=0 so trials always run the full 30 timesteps, capture
S_t at every step, average across trials, plot heatmap strip + α_i trajectories.

Outputs:
  figures/avg_saliency_heatmap_changeS1.pdf
  figures/avg_alpha_trajectories_changeS1.pdf
  analysis/avg_saliency_changeS1.npz

Usage:
  cd /Users/jonathanmorgan/AttentionManuscript/Prism
  python3 analysis/avg_saliency_change_S1.py
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import torch
import matplotlib.pyplot as plt

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from env import ChangeDetectionEnv  # noqa: E402
from model import PrismModel  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Helpers (mirror those in avg_saliency_cueS1_S4.py for parity)
# ─────────────────────────────────────────────────────────────────────────────

def _device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def build_model_from_config(cfg_model: dict, device: torch.device) -> PrismModel:
    iab = cfg_model.get("init_action_logit_bias", None)
    if iab is not None:
        iab = [float(v) for v in iab]
    return PrismModel(
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


def force_trial_conditions(
    env: ChangeDetectionEnv,
    cue_position: str,
    validity: float,
    change_index: int,      # 0=S_1, 1=S_2, 2=S_3, 3=S_4 (env's gabor1..gabor4 indexing)
    delta_degrees: float,
    change_time: int,
) -> None:
    """Force a fully-specified change trial AFTER env.reset().

    Mapping reminder (from env.py):
      change_index == 0 → gabor1 → observation[0:25, 0:25] = top-left      = S_1
      change_index == 1 → gabor2 → observation[25:50, 0:25] = bottom-left  = S_2
      change_index == 2 → gabor3 → observation[0:25, 25:50] = top-right    = S_3
      change_index == 3 → gabor4 → observation[25:50, 25:50] = bottom-right = S_4
    """
    if cue_position not in ("left", "right"):
        raise ValueError(f"cue_position must be 'left' or 'right'; got {cue_position}")
    env.cue_position = cue_position
    env.proportion = float(validity)
    env.change_true = 1
    env.change_index = int(change_index)
    env.orientation_change = float(delta_degrees)
    env.change_time = int(change_time)


def collect_saliency_with_change(
    model: PrismModel,
    env: ChangeDetectionEnv,
    cue_position: str,
    n_trials: int,
    n_steps: int,
    device: torch.device,
    seed_base: int = 0,
):
    """Collect per-step saliency for n_trials with the change at S_1, Δ=+45°, t*=15."""
    saliencies = np.zeros((n_trials, n_steps, 12, 12), dtype=np.float32)
    obs_example = None

    model.eval()
    with torch.no_grad():
        for trial in range(n_trials):
            np.random.seed(seed_base + trial)

            obs = env.reset()
            force_trial_conditions(
                env,
                cue_position=cue_position,
                validity=1.0,
                change_index=0,           # S_1 (top-left)
                delta_degrees=45.0,
                change_time=15,
            )

            M = model.init_memory(batch_size=1, device=device)
            obs_this_trial = []
            for t in range(n_steps):
                obs_this_trial.append(obs.astype(np.float32, copy=True))

                x_t = torch.from_numpy(obs.astype(np.float32, copy=False)).to(device)
                x_t = x_t.permute(2, 0, 1).unsqueeze(0).contiguous()  # (1, 3, 50, 50)
                step = model.forward_step(x_t, M, return_aux=False)

                saliencies[trial, t] = step.saliency[0, 0].detach().cpu().numpy()

                # Force action=0 ("wait") so we observe the full natural saliency
                # trajectory rather than terminating early on a hit.
                obs, _, done, _ = env.step(0)
                M = step.M_next
                if done:
                    if t + 1 < n_steps:
                        saliencies[trial, t + 1 :] = np.nan
                    break

            if obs_example is None:
                obs_example = np.array(obs_this_trial, dtype=np.float32)

            if (trial + 1) % 50 == 0:
                print(f"  [{cue_position}] trial {trial+1}/{n_trials}")

    return saliencies, obs_example


def alpha_per_quadrant(s_map: np.ndarray) -> np.ndarray:
    """(..., 12, 12) → (..., 4) per-quadrant saliency mass [S_1, S_2, S_3, S_4]."""
    a1 = s_map[..., :6, :6].sum(axis=(-1, -2))  # S_1 top-left
    a2 = s_map[..., 6:, :6].sum(axis=(-1, -2))  # S_2 bottom-left
    a3 = s_map[..., :6, 6:].sum(axis=(-1, -2))  # S_3 top-right
    a4 = s_map[..., 6:, 6:].sum(axis=(-1, -2))  # S_4 bottom-right
    return np.stack([a1, a2, a3, a4], axis=-1)


# ─────────────────────────────────────────────────────────────────────────────
# Plotting
# ─────────────────────────────────────────────────────────────────────────────

def plot_heatmap_strip(
    mean_valid: np.ndarray,    # (T, 12, 12) — Cue S_1, Change S_1
    mean_invalid: np.ndarray,  # (T, 12, 12) — Cue S_4, Change S_1
    out_path: str,
    n_trials: int,
    change_time: int,
) -> None:
    T = mean_valid.shape[0]
    nrows_per_block = 5
    ncols = 6

    vmin = 0.0
    vmax = float(max(np.nanmax(mean_valid), np.nanmax(mean_invalid)))

    fig = plt.figure(figsize=(12, 14))
    gs = fig.add_gridspec(
        nrows=2 * nrows_per_block + 2,
        ncols=ncols + 1,
        width_ratios=[1] * ncols + [0.05],
        height_ratios=[0.2] + [1] * nrows_per_block + [0.2] + [1] * nrows_per_block,
        hspace=0.25,
        wspace=0.15,
    )

    fig.suptitle(
        f"Mean saliency map $S_t$ over {n_trials} trials  ·  "
        f"Change $S_1$ at $t^*={change_time}$, $\\Delta=+45°$  ·  Validity = 1.0",
        fontsize=14, y=0.995,
    )

    def _draw_block(mean_block: np.ndarray, row_offset: int, title: str) -> None:
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
            # Highlight the change frame and immediately after.
            border_color = "red" if t in (change_time, change_time + 1, change_time + 2) else None
            if border_color:
                for spine in ax.spines.values():
                    spine.set_edgecolor(border_color)
                    spine.set_linewidth(1.5)
            ax.set_title(f"$t={t}$", fontsize=9,
                         color="red" if border_color else "black")
            # Faint quadrant boundary.
            ax.axhline(5.5, color="white", lw=0.5, alpha=0.4)
            ax.axvline(5.5, color="white", lw=0.5, alpha=0.4)
        return last_im

    im_top = _draw_block(
        mean_valid, row_offset=0,
        title="VALID  ·  Cue $S_1$, Change $S_1$",
    )
    im_bot = _draw_block(
        mean_invalid, row_offset=nrows_per_block + 1,
        title="INVALID  ·  Cue $S_4$, Change $S_1$",
    )

    cax = fig.add_subplot(gs[1 : 1 + nrows_per_block, ncols])
    fig.colorbar(im_top, cax=cax, label="$S_t$")
    cax2 = fig.add_subplot(gs[nrows_per_block + 2 : 2 * nrows_per_block + 2, ncols])
    fig.colorbar(im_bot, cax=cax2, label="$S_t$")

    fig.savefig(out_path, bbox_inches="tight", dpi=120)
    plt.close(fig)
    print(f"  saved: {out_path}")


def plot_alpha_trajectories(
    mean_valid: np.ndarray,
    mean_invalid: np.ndarray,
    out_path: str,
    n_trials: int,
    change_time: int,
) -> None:
    T = mean_valid.shape[0]
    times = np.arange(T)

    alpha_valid = alpha_per_quadrant(mean_valid)
    alpha_invalid = alpha_per_quadrant(mean_invalid)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    fig.suptitle(
        f"Per-quadrant aggregated saliency $\\alpha_i(t)$  ·  averaged over {n_trials} trials  ·  "
        f"Change $S_1$, $\\Delta=+45°$, $t^*={change_time}$",
        fontsize=14, y=1.02,
    )

    quadrant_labels = [r"$\alpha_{S_1}$ (top-left, CHANGE)",
                       r"$\alpha_{S_2}$ (bottom-left)",
                       r"$\alpha_{S_3}$ (top-right)",
                       r"$\alpha_{S_4}$ (bottom-right)"]
    colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]

    for ax, alpha_block, cue_label in [
        (axes[0], alpha_valid,   "VALID  ·  Cue $S_1$ (Validity = 1.0)"),
        (axes[1], alpha_invalid, "INVALID  ·  Cue $S_4$ (Validity = 1.0)"),
    ]:
        for q in range(4):
            lw = 2.5 if q == 0 else 1.8  # bold the change-location line
            ax.plot(times, alpha_block[:, q], label=quadrant_labels[q],
                    color=colors[q], linewidth=lw)
        ax.set_xlabel("Timestep $t$")
        ax.set_ylabel(r"$\alpha_i(t) = \sum_{(h,w) \in S_i} S_t(h,w)$")
        ax.set_title(cue_label)
        ax.axvline(1, color="black", linestyle=":", alpha=0.5, label="cue ($t=1$)")
        ax.axvline(3, color="grey", linestyle=":", alpha=0.4, label="Gabor onset ($t=3$)")
        ax.axvspan(change_time, change_time + 2, color="red", alpha=0.08, label=f"change window ($t \\geq {change_time}$)")
        ax.legend(fontsize=8, loc="upper left")
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", dpi=120)
    plt.close(fig)
    print(f"  saved: {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Avg saliency, Change S_1 at t*=15, Δ=+45°.")
    parser.add_argument("--config", type=str,
                        default=os.path.join(_ROOT, "config", "prism_config.json"))
    parser.add_argument("--checkpoint", type=str,
                        default=os.path.join(_ROOT, "checkpoints", "prism_latest.pt"))
    parser.add_argument("--n_trials", type=int, default=500)
    parser.add_argument("--n_steps", type=int, default=30)
    parser.add_argument("--out_heatmap", type=str,
                        default=os.path.join(_ROOT, "figures", "avg_saliency_heatmap_changeS1.pdf"))
    parser.add_argument("--out_alpha", type=str,
                        default=os.path.join(_ROOT, "figures", "avg_alpha_trajectories_changeS1.pdf"))
    parser.add_argument("--out_data", type=str,
                        default=os.path.join(_ROOT, "analysis", "avg_saliency_changeS1.npz"))
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out_heatmap), exist_ok=True)
    os.makedirs(os.path.dirname(args.out_data), exist_ok=True)

    cfg = json.load(open(args.config))
    device = _device()
    print(f"device: {device}")

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

    with torch.no_grad():
        bias = model.actor.fc2.bias.detach().cpu().tolist()
    print(f"  actor.fc2.bias = {bias}  (expect ≈ [0.0, -4.0])")

    env_cfg = cfg["environment"]
    env = ChangeDetectionEnv(
        theta=float(env_cfg.get("theta_start", 65.0)),
        noise_multiplier=float(env_cfg.get("noise_multiplier", 10.0)),
        min_change_time=int(env_cfg.get("min_change_time", 11)),
        max_change_time=int(env_cfg.get("max_change_time", 25)),
    )

    print(f"\nVALID condition: Cue S_1 + Change S_1 ({args.n_trials} trials, t*=15, Δ=+45°)...")
    sal_valid, obs_valid = collect_saliency_with_change(
        model, env, cue_position="left",
        n_trials=args.n_trials, n_steps=args.n_steps, device=device, seed_base=3000,
    )

    print(f"\nINVALID condition: Cue S_4 + Change S_1 ({args.n_trials} trials, t*=15, Δ=+45°)...")
    sal_invalid, obs_invalid = collect_saliency_with_change(
        model, env, cue_position="right",
        n_trials=args.n_trials, n_steps=args.n_steps, device=device, seed_base=4000,
    )

    mean_valid = np.nanmean(sal_valid, axis=0)
    mean_invalid = np.nanmean(sal_invalid, axis=0)
    print(f"\nmean S_t (VALID):   shape={mean_valid.shape}, "
          f"range=[{mean_valid.min():.4g}, {mean_valid.max():.4g}]")
    print(f"mean S_t (INVALID): shape={mean_invalid.shape}, "
          f"range=[{mean_invalid.min():.4g}, {mean_invalid.max():.4g}]")

    # Quick numerical summary of the change-frame saliency, to print to stdout.
    a_valid = alpha_per_quadrant(mean_valid)
    a_invalid = alpha_per_quadrant(mean_invalid)
    print("\nα_S_1 trajectory at the change window:")
    for t in range(13, 19):
        print(f"  t={t}:  VALID α_S1={a_valid[t,0]:.3f},  "
              f"INVALID α_S1={a_invalid[t,0]:.3f},  "
              f"diff={a_valid[t,0]-a_invalid[t,0]:+.3f}")

    np.savez(
        args.out_data,
        mean_valid=mean_valid, mean_invalid=mean_invalid,
        sal_valid=sal_valid, sal_invalid=sal_invalid,
        obs_valid_example=obs_valid, obs_invalid_example=obs_invalid,
        config=json.dumps(cfg), n_trials=args.n_trials,
        change_time=15, delta_degrees=45.0, change_index=0,
    )
    print(f"\nsaved raw arrays: {args.out_data}")

    print("\nrendering figures...")
    plot_heatmap_strip(mean_valid, mean_invalid, args.out_heatmap,
                       n_trials=args.n_trials, change_time=15)
    plot_alpha_trajectories(mean_valid, mean_invalid, args.out_alpha,
                            n_trials=args.n_trials, change_time=15)

    print("\ndone.")


if __name__ == "__main__":
    main()
