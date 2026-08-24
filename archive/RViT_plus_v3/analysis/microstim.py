"""
Microstim-analog perturbation experiment for RViT+.

This is the public API for the Herman & Morgan 2025-style attention-perturbation
experiment. It lets you bias the FeedbackTransformer's attention logits at any
(layer, iteration, target-location) tuple of your choosing, then measure the
downstream behavioural effect.

Two perturbation modes provided:
    - point: Gaussian-shaped bias centered at a target patch.
    - row  : add a bias to all key columns at a target location (forces the
             model to over-attend to that location).

Behavioural measurements:
    - For Stage 1/2 (reconstruction): MSE delta between baseline and perturbed
      reconstructions per timestep + per-spatial-location heatmap.
    - For Stage 4 (RL, future): policy action / Q distribution / reward delta.

Cortical analog (the "why"):
    - This is the architecture-level analog of FEF / SC microstimulation
      (`moore_armstrong2003_fef_microstim`, `cavanaugh_wurtz2004_sc_change_blindness`).
    - The perturbation magnitude maps onto stimulation current.
    - The (layer, iter) tuple maps onto stimulation site + onset timing.
    - The behavioural delta is the analog of the macaque psychophysics output.

Usage:
    .venv/bin/python RViT_plus/analysis/microstim.py
    .venv/bin/python RViT_plus/analysis/microstim.py \\
        --layer 0 --iter 2 --target-i 5 --target-j 6 --magnitude 5.0
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Optional, Tuple

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v3.data import MovingMNIST
from RViT_plus_v3.encoder import RViTPlusEncoder
from RViT_plus_v3.model import RViTPlusModel


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
    kw.setdefault("in_channels", 3)
    kw.setdefault("image_h", 50)
    kw.setdefault("image_w", 50)
    kw.setdefault("stem_out_channels", 64)
    kw.setdefault("state_channels", (64, 96, 128))
    kw.setdefault("n_FR", 4)
    kw.setdefault("n_BR", 4)
    kw.setdefault("n_heads", 4)
    kw.setdefault("latent_channels", 16)
    kw.pop("latent_dim", None)  # legacy kwarg from pre-run-8 checkpoints
    kw.setdefault("enable_skips", True)
    kw.setdefault("skip_scale", 0.3)
    model = RViTPlusModel(**kw).to(device)
    model.load_state_dict(state["model_state_dict"])
    model.eval()
    return model


def _layer_grid_hw(model: RViTPlusModel, layer_idx: int) -> Tuple[int, int]:
    return RViTPlusEncoder.GRID_HW[layer_idx]


def gaussian_attention_bias(
    n_heads: int,
    grid_h: int,
    grid_w: int,
    target_i: int,
    target_j: int,
    magnitude: float = 5.0,
    sigma: float = 1.5,
    *,
    batch_size: int = 1,
    device: torch.device = torch.device("cpu"),
) -> torch.Tensor:
    """Construct a (B, n_heads, N, N) attention-logit bias with a Gaussian bump
    at one key location, broadcast over all query positions.

    The bump is centered at key-grid position (target_i, target_j), with the
    given std-dev `sigma` (in patch units). All query positions get the same
    bias toward this key — i.e. attention is pulled toward (i, j) regardless
    of which query is asking.
    """
    N = grid_h * grid_w
    ii, jj = np.meshgrid(np.arange(grid_h), np.arange(grid_w), indexing="ij")
    sq = (ii - target_i) ** 2 + (jj - target_j) ** 2
    bump = np.exp(-sq / (2.0 * sigma ** 2))  # (H, W) in [0, 1]
    bump_flat = bump.flatten()  # (N,)
    bias_key = magnitude * bump_flat  # (N,)
    # Broadcast: every query gets the same per-key bias.
    bias = np.broadcast_to(bias_key[None, :], (N, N)).copy()  # (N_query, N_key)
    t = torch.from_numpy(bias).float().to(device)
    return t.unsqueeze(0).unsqueeze(0).expand(batch_size, n_heads, -1, -1).contiguous()


def run_microstim_episode(
    model: RViTPlusModel,
    sequence: torch.Tensor,             # (T, 3, H, W) on device
    *,
    layer_idx: int,
    iter_idx: int,
    target_loc: Tuple[int, int],
    magnitude: float,
    sigma: float = 1.5,
    autoencode: bool = True,
) -> dict:
    """Run one sequence through the model twice — baseline and perturbed.

    Returns a dict with per-timestep tensors for both runs plus deltas.
    """
    device = sequence.device
    T = sequence.shape[0]
    h, w = _layer_grid_hw(model, layer_idx)
    n_heads = model.encoder.n_heads

    bias = gaussian_attention_bias(
        n_heads, h, w,
        target_i=target_loc[0], target_j=target_loc[1],
        magnitude=magnitude, sigma=sigma,
        batch_size=1, device=device,
    )

    baseline = {"recons": [], "attn": []}
    perturbed = {"recons": [], "attn": []}

    # Two separate forward passes through the same sequence.
    states_b = model.init_states(1, device=device)
    states_p = model.init_states(1, device=device)

    with torch.no_grad():
        for t in range(T):
            x_t = sequence[t:t + 1]
            x_target = x_t if autoencode else (sequence[t + 1:t + 2] if t + 1 < T else x_t)

            out_b = model.forward_step(x_t, states_b, x_target=x_target)
            states_b = out_b.layer_states_new

            out_p = model.forward_step(
                x_t, states_p, x_target=x_target,
                attn_biases={(layer_idx, iter_idx): bias},
            )
            states_p = out_p.layer_states_new

            baseline["recons"].append(out_b.recon_final[0].cpu().numpy())
            perturbed["recons"].append(out_p.recon_final[0].cpu().numpy())

            # Capture the attention map at the perturbed (layer, iter).
            baseline["attn"].append(out_b.attn_per_iter[iter_idx][layer_idx][0].cpu().numpy())
            perturbed["attn"].append(out_p.attn_per_iter[iter_idx][layer_idx][0].cpu().numpy())

    baseline["recons"] = np.stack(baseline["recons"])     # (T, 3, H, W)
    baseline["attn"] = np.stack(baseline["attn"])         # (T, n_heads, N, N)
    perturbed["recons"] = np.stack(perturbed["recons"])
    perturbed["attn"] = np.stack(perturbed["attn"])

    # Per-timestep reconstruction-MSE delta.
    recon_mse_per_t = ((perturbed["recons"] - baseline["recons"]) ** 2).mean(axis=(1, 2, 3))
    # Per-timestep attention-distribution delta (mean head, mean query).
    attn_delta_per_t = (
        perturbed["attn"].mean(axis=(1, 2))
        - baseline["attn"].mean(axis=(1, 2))
    )  # (T, N_key)

    return {
        "baseline": baseline,
        "perturbed": perturbed,
        "recon_mse_per_t": recon_mse_per_t,
        "attn_delta_per_t": attn_delta_per_t,
        "config": {
            "layer_idx": layer_idx,
            "iter_idx": iter_idx,
            "target_loc": target_loc,
            "magnitude": magnitude,
            "sigma": sigma,
            "grid_hw": (h, w),
        },
    }


def render_microstim_figure(result: dict, out_path: str, *, n_show: int = 6) -> None:
    """Save a figure with baseline / perturbed / delta reconstructions per timestep."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available; skipping figure render.")
        return

    B_recons = result["baseline"]["recons"]   # (T, 3, H, W)
    P_recons = result["perturbed"]["recons"]
    T = min(n_show, B_recons.shape[0])
    cfg = result["config"]

    fig, axes = plt.subplots(T, 4, figsize=(4 * 2.4, T * 2.2), squeeze=False)
    fig.suptitle(
        f"Microstim @ layer={cfg['layer_idx']}, iter={cfg['iter_idx']}, "
        f"loc={cfg['target_loc']}, mag={cfg['magnitude']}",
        fontsize=10, y=0.995,
    )

    def _to_uint(arr):
        a = (arr + 1.0) / 2.0
        a = np.clip(np.transpose(a, (1, 2, 0)), 0, 1)
        return a

    for t in range(T):
        # Col 0 — input recon (baseline reconstruction)
        axes[t, 0].imshow(_to_uint(B_recons[t]))
        axes[t, 0].set_title(f"t{t} baseline recon", fontsize=7)
        axes[t, 0].axis("off")

        axes[t, 1].imshow(_to_uint(P_recons[t]))
        axes[t, 1].set_title(f"t{t} perturbed recon", fontsize=7)
        axes[t, 1].axis("off")

        # Col 2 — absolute delta image
        delta = np.abs(P_recons[t] - B_recons[t])
        delta_disp = (delta / max(delta.max(), 1e-9))  # normalize for viz
        axes[t, 2].imshow(np.transpose(delta_disp, (1, 2, 0)))
        axes[t, 2].set_title(f"t{t} |Δ| (mse={result['recon_mse_per_t'][t]:.4f})", fontsize=7)
        axes[t, 2].axis("off")

        # Col 3 — attention-key delta heatmap (reshape (N,) → (h, w))
        h, w = cfg["grid_hw"]
        attn_delta = result["attn_delta_per_t"][t].reshape(h, w)
        im = axes[t, 3].imshow(attn_delta, cmap="seismic",
                                vmin=-np.abs(attn_delta).max(),
                                vmax=np.abs(attn_delta).max())
        axes[t, 3].set_title(f"t{t} Δattn (key map)", fontsize=7)
        axes[t, 3].axis("off")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.tight_layout()
    plt.subplots_adjust(top=0.985)
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[microstim] figure → {out_path}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Microstim-analog perturbation experiment.")
    parser.add_argument("--ckpt", default=os.path.join(
        _PROJECT_ROOT, "RViT_plus", "checkpoints", "rvit_plus_latest.pt"
    ))
    parser.add_argument("--out", default=os.path.join(_HERE, "figures", "microstim.png"))
    parser.add_argument("--layer", type=int, default=0,
                        help="Which layer to perturb: 0=C₁ (V1, 12×12), 1=C₂ (V4, 12×12), 2=C₃ (IT, 6×6)")
    parser.add_argument("--iter", type=int, default=2, dest="iter_idx",
                        help="Which inner iteration (0..n_FR-1) to perturb")
    parser.add_argument("--target-i", type=int, default=5)
    parser.add_argument("--target-j", type=int, default=5)
    parser.add_argument("--magnitude", type=float, default=5.0)
    parser.add_argument("--sigma", type=float, default=1.5)
    parser.add_argument("--seq-len", type=int, default=8)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    if not os.path.exists(args.ckpt):
        print(f"[microstim] checkpoint not found: {args.ckpt}")
        return 1

    device = _select_device()
    print(f"[microstim] loading {args.ckpt} on {device}")
    model = _load_model(args.ckpt, device)

    ds = MovingMNIST(n_sequences=2, seq_len=args.seq_len, seed_base=args.seed)
    seq = ds[0].to(device)
    print(f"[microstim] sequence shape {tuple(seq.shape)}")

    print(f"[microstim] perturb layer={args.layer} iter={args.iter_idx} "
          f"loc=({args.target_i},{args.target_j}) mag={args.magnitude}")

    result = run_microstim_episode(
        model, seq,
        layer_idx=args.layer,
        iter_idx=args.iter_idx,
        target_loc=(args.target_i, args.target_j),
        magnitude=args.magnitude,
        sigma=args.sigma,
        autoencode=True,
    )

    # Quantitative summary.
    print("\n[microstim] per-timestep reconstruction-MSE delta (perturbed vs baseline):")
    for t, mse in enumerate(result["recon_mse_per_t"]):
        print(f"   t={t:>2d}  recon-Δ²MSE={mse:.6f}")
    print(f"[microstim] mean MSE delta = {result['recon_mse_per_t'].mean():.6f}")
    print(f"[microstim] max attention-key shift at perturbed location: "
          f"{result['attn_delta_per_t'].max():+.4f}")

    render_microstim_figure(result, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
