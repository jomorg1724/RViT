"""
Attention-map visualization for RViT+ — in-depth interpretability analysis.

Where `attention_entropy.py` reports scalar summary statistics, this script
generates per-(layer, frame, iter) spatial attention maps and aligns them
with the input video and reconstruction so you can SEE what each layer
attends to and how attention evolves over inner iterations.

Three figure types produced:

  1. recon_grid.png      — input | recon | per-layer attention-received,
                            one row per frame, for the first N sequences.

  2. attention_dynamics.png  — for a single frame, evolution of attention
                            across n_FR inner iterations, per layer.

  3. attention_summary.png   — heatmaps of mean attention received per
                            (layer, iter) cell, aggregated over all
                            sequences and frames.

Attention is summarized per-key as "attention received":
    attn_received(k) = mean over (batch, heads, queries) of attn[..., q, k]
This is the per-key marginal of the softmax — i.e., on average how much
attention does this key position receive? High values = "looked at."

Usage:
    .venv/bin/python RViT_plus/analysis/attention_maps.py
    .venv/bin/python RViT_plus/analysis/attention_maps.py --n-sequences 4
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


def _load_model(ckpt_path: str, device: torch.device) -> RViTPlusModel:
    state = torch.load(ckpt_path, map_location=device, weights_only=False)
    kw = dict(state.get("model_kwargs", {}))
    if "state_channels" in kw and not isinstance(kw["state_channels"], tuple):
        kw["state_channels"] = tuple(kw["state_channels"])
    # Defaults for older checkpoints.
    kw.setdefault("in_channels", 3)
    kw.setdefault("image_h", 50)
    kw.setdefault("image_w", 50)
    kw.setdefault("stem_out_channels", 64)
    kw.setdefault("state_channels", (64, 96, 128))
    kw.setdefault("n_FR", 4)
    kw.setdefault("n_heads", 4)
    kw.setdefault("enable_skips", True)
    kw.setdefault("skip_scale", 0.3)
    kw.setdefault("seq_len", 10)
    kw.setdefault("upsample_out_channels", 32)
    kw.setdefault("cnn_hidden", 64)
    kw.pop("latent_dim", None)
    kw.pop("latent_channels", None)
    kw.pop("max_T", None)
    kw.pop("n_BR", None)
    model = RViTPlusModel(**kw).to(device)
    model.load_state_dict(state["model_state_dict"])
    model.eval()
    return model


def attention_received(attn: torch.Tensor) -> np.ndarray:
    """attn: (B, n_heads, N, N).
    Returns numpy array (B, N) of mean attention received per key
    (averaged over heads + queries).
    """
    # mean over heads (dim 1) and queries (dim 2) → (B, N)
    return attn.mean(dim=(1, 2)).cpu().numpy()


def reshape_to_grid(arr: np.ndarray, H: int, W: int) -> np.ndarray:
    """arr (..., N) → (..., H, W). N must equal H*W."""
    assert arr.shape[-1] == H * W
    return arr.reshape(arr.shape[:-1] + (H, W))


def figure_recon_grid(model: RViTPlusModel, dataset: MovingMNIST,
                       n_sequences: int, device: torch.device, out_path: str):
    """Per-frame layout: input | recon | attn(C₁) | attn(C₂) | attn(C₃).

    One block per sequence (one column-cluster per frame). Visualises how
    attention received aligns with where the digits are in each input frame.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    layer_grids = [(12, 12), (6, 6), (3, 3)]
    n_layers = 3
    T = model.seq_len
    panels_per_frame = 2 + n_layers   # input + recon + 3 attention layers
    n_cols = T
    n_rows = n_sequences * panels_per_frame

    fig, axes = plt.subplots(n_rows, n_cols,
                              figsize=(n_cols * 1.6, n_rows * 1.6),
                              squeeze=False)

    with torch.no_grad():
        for s in range(n_sequences):
            seq = dataset[s].to(device).unsqueeze(0)   # (1, T, 3, H, W)
            out = model.compress_and_reconstruct(seq)
            recons = torch.stack(out.recons, dim=1)[0].cpu().numpy()   # (T, 3, H, W)
            seq_np = seq[0].cpu().numpy()

            # Attention received per (frame, layer) at the LAST inner iteration.
            # encoder_attn_per_frame[t][k][L] : (B, n_heads, N_L, N_L)
            attn_by_frame_layer = [
                [
                    attention_received(out.encoder_attn_per_frame[t][model.n_FR - 1][L])[0]
                    for L in range(n_layers)
                ]
                for t in range(T)
            ]

            row_base = s * panels_per_frame
            for t in range(T):
                # 1) Input
                a_in = (seq_np[t] + 1.0) / 2.0
                a_in = np.clip(np.transpose(a_in, (1, 2, 0)), 0, 1)
                ax = axes[row_base, t]
                ax.imshow(a_in)
                ax.axis("off")
                if t == 0:
                    ax.set_ylabel(f"s{s} input", fontsize=8)
                if s == 0:
                    ax.set_title(f"t={t}", fontsize=8)

                # 2) Recon
                a_rec = (recons[t] + 1.0) / 2.0
                a_rec = np.clip(np.transpose(a_rec, (1, 2, 0)), 0, 1)
                ax = axes[row_base + 1, t]
                ax.imshow(a_rec)
                ax.axis("off")
                if t == 0:
                    ax.set_ylabel(f"s{s} recon", fontsize=8)

                # 3-5) Per-layer attention received
                for L in range(n_layers):
                    H_l, W_l = layer_grids[L]
                    attn_map = reshape_to_grid(attn_by_frame_layer[t][L], H_l, W_l)
                    ax = axes[row_base + 2 + L, t]
                    im = ax.imshow(attn_map, cmap="viridis",
                                   vmin=attn_map.min(), vmax=attn_map.max())
                    ax.axis("off")
                    if t == 0:
                        ax.set_ylabel(f"s{s} attn C{L+1}", fontsize=8)

    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[attn-map] recon_grid → {out_path}")


def figure_attention_dynamics(model: RViTPlusModel, dataset: MovingMNIST,
                               seq_idx: int, frame_idx: int, device: torch.device,
                               out_path: str):
    """For a single (sequence, frame), show the per-layer attention map at each
    of n_FR inner iterations. Reveals how attention dynamics evolve within a
    single frame's processing.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    layer_grids = [(12, 12), (6, 6), (3, 3)]
    n_layers = 3
    n_iters = model.n_FR
    n_rows = 1 + n_layers    # input on top, 3 layers below
    n_cols = max(n_iters, 1)

    fig, axes = plt.subplots(n_rows, n_cols,
                              figsize=(n_cols * 2.0, n_rows * 2.0),
                              squeeze=False)

    with torch.no_grad():
        seq = dataset[seq_idx].to(device).unsqueeze(0)
        out = model.compress_and_reconstruct(seq)
        seq_np = seq[0].cpu().numpy()

        # Top row: input frame, replicated in first column; other cols are
        # the recurrent iterations, but the input doesn't evolve — so leave
        # them blank with a note.
        a_in = (seq_np[frame_idx] + 1.0) / 2.0
        a_in = np.clip(np.transpose(a_in, (1, 2, 0)), 0, 1)
        axes[0, 0].imshow(a_in)
        axes[0, 0].set_title(f"input t={frame_idx}", fontsize=9)
        axes[0, 0].axis("off")
        for c in range(1, n_cols):
            axes[0, c].axis("off")

        # Per-layer rows: attention map at each iteration.
        for L in range(n_layers):
            H_l, W_l = layer_grids[L]
            for k in range(n_iters):
                attn = out.encoder_attn_per_frame[frame_idx][k][L]
                attn_recv = attention_received(attn)[0]
                attn_map = reshape_to_grid(attn_recv, H_l, W_l)
                ax = axes[L + 1, k]
                im = ax.imshow(attn_map, cmap="viridis",
                               vmin=attn_map.min(), vmax=attn_map.max())
                ax.axis("off")
                if k == 0:
                    ax.set_ylabel(f"C{L+1} {H_l}×{W_l}", fontsize=9, rotation=0, labelpad=30)
                if L == 0:
                    ax.set_title(f"iter k={k}", fontsize=9)

    plt.suptitle(f"Attention dynamics (sequence {seq_idx}, frame {frame_idx})", fontsize=11)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[attn-map] dynamics → {out_path}")


def figure_attention_summary(model: RViTPlusModel, dataset: MovingMNIST,
                              n_sequences: int, device: torch.device, out_path: str):
    """Aggregated attention-received maps: average over batch, sequence, frame
    at each (layer, iter) cell. Reveals which spatial positions get attended
    to ON AVERAGE — independent of any specific frame's content. If attention
    is uniform, all maps look flat. If structured (e.g., center bias, edge
    bias), the structure shows up here.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    layer_grids = [(12, 12), (6, 6), (3, 3)]
    n_layers = 3
    n_iters = model.n_FR
    T = model.seq_len

    # Accumulate attention received over sequences and frames.
    accum = [[np.zeros(np.prod(layer_grids[L])) for _ in range(n_iters)]
             for L in range(n_layers)]
    count = 0

    with torch.no_grad():
        for s in range(n_sequences):
            seq = dataset[s].to(device).unsqueeze(0)
            out = model.compress_and_reconstruct(seq)
            for t in range(T):
                for k in range(n_iters):
                    for L in range(n_layers):
                        attn_recv = attention_received(out.encoder_attn_per_frame[t][k][L])[0]
                        accum[L][k] += attn_recv
                        # count incremented once per (s, t) since L and k are nested
            count += T

    fig, axes = plt.subplots(n_layers, n_iters,
                              figsize=(n_iters * 2.0, n_layers * 2.0),
                              squeeze=False)
    for L in range(n_layers):
        H_l, W_l = layer_grids[L]
        for k in range(n_iters):
            mean = accum[L][k] / max(count, 1)
            grid = mean.reshape(H_l, W_l)
            ax = axes[L, k]
            ax.imshow(grid, cmap="viridis", vmin=grid.min(), vmax=grid.max())
            ax.axis("off")
            ax.set_title(f"C{L+1} k={k}\nrange [{grid.min():.4f}, {grid.max():.4f}]",
                          fontsize=8)
    plt.suptitle(f"Mean attention received per (layer, iter) — over {n_sequences} sequences × {T} frames",
                 fontsize=10)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[attn-map] summary → {out_path}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", default=os.path.join(_PROJECT_ROOT, "RViT_plus", "checkpoints",
                                                   "rvit_plus_latest.pt"))
    p.add_argument("--out-dir", default=os.path.join(_HERE, "figures"))
    p.add_argument("--n-sequences", type=int, default=2,
                   help="Number of sequences to render in the recon-grid figure (default 2).")
    p.add_argument("--n-summary-sequences", type=int, default=16,
                   help="Number of sequences to aggregate in the summary figure (default 16).")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args(argv)

    if not os.path.exists(args.ckpt):
        print(f"checkpoint not found: {args.ckpt}")
        return 1
    os.makedirs(args.out_dir, exist_ok=True)

    device = _select_device()
    print(f"[attn-map] checkpoint {args.ckpt}")
    print(f"[attn-map] device {device}")
    model = _load_model(args.ckpt, device)

    dataset = MovingMNIST(n_sequences=max(args.n_summary_sequences, args.n_sequences),
                           seq_len=model.seq_len, frame_hw=50, digit_hw=14, n_digits=2,
                           seed_base=args.seed)

    # Figure 1: per-frame input + recon + per-layer attention received
    figure_recon_grid(model, dataset, args.n_sequences, device,
                      out_path=os.path.join(args.out_dir, "attn_recon_grid.png"))

    # Figure 2: attention dynamics within a single frame (across n_FR inner iters)
    figure_attention_dynamics(model, dataset, seq_idx=0, frame_idx=model.seq_len // 2,
                               device=device,
                               out_path=os.path.join(args.out_dir, "attn_dynamics.png"))

    # Figure 3: mean attention received across the dataset
    figure_attention_summary(model, dataset, args.n_summary_sequences, device,
                              out_path=os.path.join(args.out_dir, "attn_summary.png"))

    return 0


if __name__ == "__main__":
    sys.exit(main())
