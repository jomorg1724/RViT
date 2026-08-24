"""
Averaged attention-map heatmaps for the RViT+ V2 model.

V2's attention block produces a per-channel spatial softmax A ∈ (B, C, H, W):
every channel is its own head, each with a softmax over the H·W grid. There are
MANY heads (64 / 96 / 128 channels at layers 1 / 2 / 3) and each is a near-sparse
probability map, so any single channel is mostly small/zero values. To get an
interpretable picture we SUM all channels (heads) into one (H, W) heatmap per
layer per timestep:

    S_L,t(h, w) = Σ_c A_L,t[c, h, w]

then AVERAGE over trials sharing a cue condition. This is the V2 analog of the
Prism `avg_saliency` analysis ("like before").

Design (per the request):
  * The change is held FIXED across all conditions: same quadrant, same time,
    same (large, easily-detectable) magnitude. We do NOT vary the change.
  * We sweep several CUE conditions (cue side × ring validity).
  * Action is forced to 0 (wait) so every trial runs the full episode and the
    post-change "change-detection" dynamics are visible in the average.
  * Cue color is randomized per trial (marginalized).

For each layer we emit a per-timestep heatmap strip (one block per condition,
shared color scale) and a per-quadrant aggregate-attention trajectory plot
α_i(t) = Σ_{(h,w) ∈ quadrant i} S_L,t(h, w).

Usage:
    .venv/bin/python RViT_plus_v3/analysis/avg_attention_maps.py \
        --checkpoint RViT_plus_v3/checkpoints/rvit_plus_rl_latest.pt \
        --n-trials 200 --device cpu
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List, Tuple

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v3.analysis import _behav_utils as bu

# Quadrant pixel layout matches the env observation:
#   top-left = S1, bottom-left = S2, top-right = S3, bottom-right = S4
QUAD_LABELS = ["S1 top-left", "S2 bottom-left", "S3 top-right", "S4 bottom-right"]
CHANGE_LABEL = {0: "S1 top-left", 1: "S2 bottom-left", 2: "S3 top-right", 3: "S4 bottom-right"}


def quad_aggregate(strip: np.ndarray) -> np.ndarray:
    """(T, H, W) → (T, 4) summed over each spatial quadrant.

    Quadrant split is the H/2 × W/2 partition (works for 12, 6 — and for odd
    grids like 3 the middle row/col is shared, which is acceptable for a coarse
    aggregate)."""
    T, H, W = strip.shape
    hh, ww = H // 2, W // 2
    s1 = strip[:, :hh, :ww].sum(axis=(1, 2))   # top-left
    s2 = strip[:, hh:, :ww].sum(axis=(1, 2))   # bottom-left
    s3 = strip[:, :hh, ww:].sum(axis=(1, 2))   # top-right
    s4 = strip[:, hh:, ww:].sum(axis=(1, 2))   # bottom-right
    return np.stack([s1, s2, s3, s4], axis=-1)


def plot_heatmap_strip(strip: np.ndarray, obs_example: np.ndarray, out_path: str,
                       *, title: str, change_frame: int) -> None:
    """One condition, one layer: a strip of per-timestep heatmaps over the
    averaged channel-summed attention, with the example input frames above."""
    import matplotlib.pyplot as plt
    from matplotlib import gridspec

    T, H, W = strip.shape
    vmin, vmax = float(strip.min()), float(strip.max())
    ncols = T
    fig = plt.figure(figsize=(0.7 * ncols + 1, 3.2))
    gs = gridspec.GridSpec(2, ncols + 1, height_ratios=[1, 1],
                           width_ratios=[1] * ncols + [0.08], wspace=0.1, hspace=0.05)

    last_im = None
    for t in range(T):
        # top row: input frame
        axo = fig.add_subplot(gs[0, t])
        frame = obs_example[t]
        fmin, fmax = float(frame.min()), float(frame.max())
        fr = (frame - fmin) / (fmax - fmin) if fmax > fmin else np.zeros_like(frame)
        axo.imshow(fr)
        ttl = f"{t}"
        if t == change_frame:
            axo.set_title(ttl, fontsize=7, color="orange", fontweight="bold")
        else:
            axo.set_title(ttl, fontsize=7)
        axo.axis("off")
        # bottom row: attention heatmap
        axh = fig.add_subplot(gs[1, t])
        last_im = axh.imshow(strip[t], cmap="viridis", vmin=vmin, vmax=vmax, interpolation="nearest")
        axh.axhline(H / 2 - 0.5, color="white", lw=0.4, alpha=0.4)
        axh.axvline(W / 2 - 0.5, color="white", lw=0.4, alpha=0.4)
        axh.set_xticks([]); axh.set_yticks([])

    cax = fig.add_subplot(gs[1, ncols])
    fig.colorbar(last_im, cax=cax, label=r"$\sum_c A[c]$")
    fig.suptitle(title, fontsize=10, y=1.06)
    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {out_path}")


def plot_alpha_trajectories(strips: List[np.ndarray], cond_labels: List[str],
                            out_path: str, *, layer_idx: int, change_frame: int,
                            change_index: int) -> None:
    """Per-quadrant aggregate attention α_i(t), one panel per condition."""
    import matplotlib.pyplot as plt

    n = len(strips)
    fig, axes = plt.subplots(1, n, figsize=(5.0 * n, 4.2), sharey=True, squeeze=False)
    axes = axes[0]
    colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]
    for ax, strip, lab in zip(axes, strips, cond_labels):
        alpha = quad_aggregate(strip)  # (T, 4)
        times = np.arange(strip.shape[0])
        for q in range(4):
            star = "  ◄ change" if q == change_index else ""
            ax.plot(times, alpha[:, q], color=colors[q], lw=2, label=QUAD_LABELS[q] + star)
        ax.axvline(1, color="black", ls=":", alpha=0.5)
        ax.axvline(3, color="grey", ls=":", alpha=0.4)
        ax.axvline(change_frame, color="orange", ls="--", alpha=0.7)
        ax.set_xlabel("timestep t")
        ax.set_title(lab, fontsize=10)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8, loc="upper left")
    axes[0].set_ylabel(r"$\alpha_i(t)=\sum_{(h,w)\in S_i}\sum_c A[c,h,w]$")
    fig.suptitle(
        f"Layer {layer_idx+1} per-quadrant aggregate attention  ·  "
        f"change at {CHANGE_LABEL[change_index]} @ t={change_frame}  "
        f"(cue=black ·, gabor onset=grey ·, change=orange --)",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {out_path}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default="RViT_plus_v3/checkpoints/rvit_plus_rl_latest.pt")
    ap.add_argument("--config", default=None)
    ap.add_argument("--out-dir", default="RViT_plus_v3/analysis/figures")
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=200)
    ap.add_argument("--change-time", type=int, default=15, help="fixed frame the change appears")
    ap.add_argument("--change-index", type=int, default=0,
                    help="fixed change quadrant: 0=top-left,1=bottom-left,2=top-right,3=bottom-right")
    ap.add_argument("--change-mag", type=float, default=64.0,
                    help="fixed |Δθ| — large = easily detectable")
    ap.add_argument("--conditions", nargs="+",
                    default=["left:1.0", "right:1.0", "left:0.25", "right:0.25"],
                    help="cue conditions as 'side:ring', e.g. left:1.0 right:0.25")
    args = ap.parse_args(argv)

    os.makedirs(args.out_dir, exist_ok=True)
    device = bu.select_device(args.device)
    cfg = bu.load_config(args.config)
    model = bu.build_model(cfg, device)
    it = bu.load_checkpoint(model, args.checkpoint, device)
    env_kwargs = dict(
        min_change_time=int(cfg["environment"]["min_change_time"]),
        max_change_time=int(cfg["environment"]["max_change_time"]),
    )
    print(f"[loaded] {args.checkpoint} (iter={it})  device={device}")
    print(f"[fixed change] quadrant={CHANGE_LABEL[args.change_index]}  t={args.change_time}  |Δθ|={args.change_mag}")

    # Parse conditions.
    conds: List[Tuple[str, float]] = []
    for c in args.conditions:
        side, ring = c.split(":")
        conds.append((side, float(ring)))

    n_layers = len(cfg["model"]["state_channels"])
    # collect[L] = list of (label, strip(T,H,W)); obs kept once per condition
    per_layer_strips: List[List[np.ndarray]] = [[] for _ in range(n_layers)]
    cond_labels: List[str] = []
    obs_examples = []

    for side, ring in conds:
        rng = np.random.default_rng(args.seed + (0 if side == "left" else 1000) + int(ring * 100))
        spec = bu.ForcedTrialSpec(
            cue_position=side, proportion=ring, change_true=1,
            change_time=args.change_time, change_index_mode=int(args.change_index),
            orientation_mag=float(args.change_mag),
        )
        envs, obs0 = bu.build_env_batch(
            spec, args.n_trials, rng, env_kwargs=env_kwargs,
            randomize_cue_position=False, randomize_color=True,
        )
        valid_tag = "VALID" if bu.CUED_QUADRANT[side] == args.change_index else "INVALID"
        label = f"cue {side} · ring {ring} ({valid_tag})"
        cond_labels.append(label)
        mean_attn, obs_ex = bu.batched_attention_rollout(model, envs, obs0, device, n_layers=n_layers)
        obs_examples.append(obs_ex)
        for L in range(n_layers):
            per_layer_strips[L].append(mean_attn[L])
        print(f"  [{label}] done  (layer ranges: "
              + ", ".join(f"L{L+1}=[{m.min():.2f},{m.max():.2f}]" for L, m in enumerate(mean_attn)) + ")")

    # Per-layer outputs.
    suffix = f"chg{args.change_index}_t{args.change_time}"
    for L in range(n_layers):
        for ci, (label, strip) in enumerate(zip(cond_labels, per_layer_strips[L])):
            safe = label.replace(" ", "").replace("·", "_").replace("(", "").replace(")", "")
            plot_heatmap_strip(
                strip, obs_examples[ci],
                os.path.join(args.out_dir, f"avg_attn_L{L+1}_{safe}_{suffix}.png"),
                title=f"layer {L+1}  ·  Σ-head attention (all heads summed)  ·  {label}  ·  n={args.n_trials}",
                change_frame=args.change_time,
            )
        plot_alpha_trajectories(
            per_layer_strips[L], cond_labels,
            os.path.join(args.out_dir, f"avg_attn_alpha_L{L+1}_{suffix}.png"),
            layer_idx=L, change_frame=args.change_time, change_index=args.change_index,
        )

    # Save raw arrays.
    npz_path = os.path.join(args.out_dir, f"avg_attn_{suffix}.npz")
    save = {"cond_labels": np.array(cond_labels, dtype=object),
            "change_index": args.change_index, "change_time": args.change_time,
            "change_mag": args.change_mag, "n_trials": args.n_trials}
    for L in range(n_layers):
        save[f"layer{L+1}"] = np.stack(per_layer_strips[L], axis=0)  # (n_cond, T, H, W)
    np.savez(npz_path, **save)
    print(f"[saved] {npz_path}")
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
