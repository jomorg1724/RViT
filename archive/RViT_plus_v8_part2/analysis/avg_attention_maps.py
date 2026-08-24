"""
PER-HEAD averaged attention-map heatmaps for the RViT+ v5 model.

IMPORTANT: we do NOT average over attention heads. Heads frequently specialize —
two heads can attend to opposite locations — so a head-average can look flat/
uniform even when every individual head is sharply structured. Each head is kept
separate throughout.

For each memtok layer we extract the per-head attention TO the image-patch keys,
reduce to a per-head per-patch saliency (mean over QUERIES only), reshape to the
(grid_h, grid_w) patch grid, and average over trials sharing a cue condition.
Outputs per layer per condition:
  * a heatmap strip with rows = [input frames, head 0, head 1, …] × timestep cols
  * a per-head per-quadrant aggregate-attention trajectory (one subplot per head)

The change is held FIXED (same quadrant/time/large magnitude); we sweep cue side
× ring validity; action is forced to wait so every trial runs the full episode.

Usage:
    .venv/bin/python RViT_plus_v8_part2/analysis/avg_attention_maps.py \
        --checkpoint <ckpt> --n-trials 200 --device cpu
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

from RViT_plus_v8_part2.analysis import _behav_utils as bu

QUAD_LABELS = ["S1 top-left", "S2 bottom-left", "S3 top-right", "S4 bottom-right"]
CHANGE_LABEL = {0: "S1 top-left", 1: "S2 bottom-left", 2: "S3 top-right", 3: "S4 bottom-right"}


def quad_aggregate(strip: np.ndarray) -> np.ndarray:
    """(T, H, W) → (T, 4) summed over each spatial quadrant (H/2 × W/2 split)."""
    T, H, W = strip.shape
    hh, ww = H // 2, W // 2
    s1 = strip[:, :hh, :ww].sum(axis=(1, 2))   # top-left
    s2 = strip[:, hh:, :ww].sum(axis=(1, 2))   # bottom-left
    s3 = strip[:, :hh, ww:].sum(axis=(1, 2))   # top-right
    s4 = strip[:, hh:, ww:].sum(axis=(1, 2))   # bottom-right
    return np.stack([s1, s2, s3, s4], axis=-1)


def plot_head_strip(strip4: np.ndarray, obs_example: np.ndarray, out_path: str,
                    *, title: str, change_frame: int) -> None:
    """strip4: (T, n_heads, gh, gw). Rows = [input frames, head 0 … head H-1];
    cols = timesteps. Shared colour scale across heads so relative magnitudes are
    comparable; per-head rows reveal head specialization a head-average would hide."""
    import matplotlib.pyplot as plt
    from matplotlib import gridspec

    T, H, gh, gw = strip4.shape
    vmin, vmax = float(strip4.min()), float(strip4.max())
    nrows = H + 1
    fig = plt.figure(figsize=(0.55 * T + 1.4, 1.0 * nrows + 0.8))
    gs = gridspec.GridSpec(nrows, T + 1, width_ratios=[1] * T + [0.06], wspace=0.06, hspace=0.12)
    for t in range(T):                                   # top row: input frames
        axo = fig.add_subplot(gs[0, t])
        frame = obs_example[t]
        fmin, fmax = float(frame.min()), float(frame.max())
        axo.imshow((frame - fmin) / (fmax - fmin) if fmax > fmin else np.zeros_like(frame))
        axo.set_title(f"{t}", fontsize=6, color=("orange" if t == change_frame else "black"))
        axo.axis("off")
    last_im = None
    for h in range(H):
        for t in range(T):
            ax = fig.add_subplot(gs[h + 1, t])
            last_im = ax.imshow(strip4[t, h], cmap="viridis", vmin=vmin, vmax=vmax,
                                interpolation="nearest")
            ax.axhline(gh / 2 - 0.5, color="white", lw=0.3, alpha=0.35)
            ax.axvline(gw / 2 - 0.5, color="white", lw=0.3, alpha=0.35)
            ax.set_xticks([]); ax.set_yticks([])
            if t == 0:
                ax.set_ylabel(f"head {h}", fontsize=7)
    cax = fig.add_subplot(gs[1:, T])
    fig.colorbar(last_im, cax=cax, label="attention to patch")
    fig.suptitle(title, fontsize=9, y=1.01)
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {out_path}")


def plot_head_alpha(strip4: np.ndarray, out_path: str, *, layer_idx: int,
                    change_frame: int, change_index: int, cond_label: str) -> None:
    """strip4: (T, n_heads, gh, gw). One subplot per head; each shows the 4
    per-quadrant aggregate-attention trajectories α_i(t) for THAT head."""
    import matplotlib.pyplot as plt

    T, H, gh, gw = strip4.shape
    fig, axes = plt.subplots(1, H, figsize=(3.8 * H, 3.6), squeeze=False)
    axes = axes[0]
    colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]
    for h in range(H):
        ax = axes[h]
        alpha = quad_aggregate(strip4[:, h])             # (T, 4)
        times = np.arange(T)
        for q in range(4):
            star = "  ◄chg" if q == change_index else ""
            ax.plot(times, alpha[:, q], color=colors[q], lw=1.8, label=QUAD_LABELS[q] + star)
        ax.axvline(1, color="black", ls=":", alpha=0.4)
        ax.axvline(3, color="grey", ls=":", alpha=0.3)
        ax.axvline(change_frame, color="orange", ls="--", alpha=0.6)
        ax.set_title(f"head {h}", fontsize=10)
        ax.set_xlabel("timestep t"); ax.grid(alpha=0.3)
        if h == 0:
            ax.set_ylabel(r"$\alpha_i(t)=\sum_{(h,w)\in S_i} A_{\,head}$")
            ax.legend(fontsize=7, loc="upper left")
    fig.suptitle(
        f"Layer {layer_idx+1} per-HEAD quadrant attention  ·  {cond_label}  ·  "
        f"change at {CHANGE_LABEL[change_index]} @ t={change_frame}  "
        f"(cue=black·, gabor=grey·, change=orange--)",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {out_path}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default="RViT_plus_v8_part2/checkpoints/rvit_plus_rl_latest.pt")
    ap.add_argument("--config", default=None)
    ap.add_argument("--out-dir", default="RViT_plus_v8_part2/analysis/figures")
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=200)
    ap.add_argument("--change-time", type=int, default=15)
    ap.add_argument("--change-index", type=int, default=0,
                    help="fixed change quadrant: 0=top-left,1=bottom-left,2=top-right,3=bottom-right")
    ap.add_argument("--change-mag", type=float, default=64.0)
    ap.add_argument("--conditions", nargs="+",
                    default=["left:1.0", "right:1.0", "left:0.25", "right:0.25"],
                    help="cue conditions as 'side:ring'")
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

    conds: List[Tuple[str, float]] = []
    for c in args.conditions:
        side, ring = c.split(":")
        conds.append((side, float(ring)))

    # v5_part2: the attention is the cross-attention block(s), not the LSTM count.
    n_layers = int(cfg["model"].get("tx_layers", 1))
    per_layer_strips: List[List[np.ndarray]] = [[] for _ in range(n_layers)]   # [L] -> list over conds of (T,H,gh,gw)
    cond_labels: List[str] = []
    obs_examples = []
    suffix = f"chg{args.change_index}_t{args.change_time}"

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
            per_layer_strips[L].append(mean_attn[L])     # (T, H, gh, gw)
        rng_txt = ", ".join(f"L{L+1}=[{m.min():.3f},{m.max():.3f}]" for L, m in enumerate(mean_attn))
        print(f"  [{label}] done  (per-head ranges: {rng_txt})")

    # Per-layer, per-condition outputs (heads kept separate).
    for L in range(n_layers):
        for ci, (label, strip4) in enumerate(zip(cond_labels, per_layer_strips[L])):
            safe = label.replace(" ", "").replace("·", "_").replace("(", "").replace(")", "")
            plot_head_strip(
                strip4, obs_examples[ci],
                os.path.join(args.out_dir, f"avg_attn_L{L+1}_{safe}_{suffix}.png"),
                title=f"layer {L+1}  ·  per-HEAD attention  ·  {label}  ·  n={args.n_trials}",
                change_frame=args.change_time,
            )
            plot_head_alpha(
                strip4,
                os.path.join(args.out_dir, f"avg_attn_alpha_L{L+1}_{safe}_{suffix}.png"),
                layer_idx=L, change_frame=args.change_time, change_index=args.change_index,
                cond_label=label,
            )

    npz_path = os.path.join(args.out_dir, f"avg_attn_{suffix}.npz")
    save = {"cond_labels": np.array(cond_labels, dtype=object),
            "change_index": args.change_index, "change_time": args.change_time,
            "change_mag": args.change_mag, "n_trials": args.n_trials}
    for L in range(n_layers):
        save[f"layer{L+1}"] = np.stack(per_layer_strips[L], axis=0)  # (n_cond, T, H, gh, gw)
    np.savez(npz_path, **save)
    print(f"[saved] {npz_path}")
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
