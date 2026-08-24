"""
Attention-entropy diagnostic for the RViT+ video-compression model.

Tests falsifiable prediction P1 from RVIT_PLUS_DESIGN.md §2:

    P1 — Reconstruction shapes attention. After pretraining, per-layer
    attention entropy will drop below 80% of max-entropy on at least 50%
    of (layer, iter, frame) cells.

Computes for both encoder (per-frame) and decoder (per-step):
  - Per-query entropy of the attention distribution over keys
  - Gini coefficient
  - Frac of cells with entropy < 80% / < 95% of max

Usage:
    .venv/bin/python RViT_plus/analysis/attention_entropy.py
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

from RViT_plus_v2.data import MovingMNIST
from RViT_plus_v2.model import RViTPlusModel


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
    kw.setdefault("n_heads", 4)
    kw.setdefault("latent_channels", 16)
    kw.pop("latent_dim", None)  # legacy kwarg from pre-run-8 checkpoints
    kw.setdefault("enable_skips", True)
    kw.setdefault("skip_scale", 0.3)
    kw.setdefault("max_T", 32)
    kw.pop("n_BR", None)
    model = RViTPlusModel(**kw).to(device)
    model.load_state_dict(state["model_state_dict"])
    model.eval()
    return model


def entropy_per_query(attn: torch.Tensor) -> torch.Tensor:
    """attn: (B, n_heads, N_q, N_k) post-softmax. Returns (B, n_heads, N_q) entropy in nats."""
    eps = 1e-12
    return -(attn * (attn + eps).log()).sum(dim=-1)


def summarize(label: str, attn_per_iter_per_step: list, model) -> None:
    """
    attn_per_iter_per_step: list of S items; each item is a list of n_FR per-iter
    lists of three (B, n_heads, N, N) layer attention tensors.
    """
    n_FR = model.n_FR
    layer_grid = [(12, 12), (6, 6), (3, 3)]

    per_layer_iter = {(L, k): [] for L in range(3) for k in range(n_FR)}

    for step in attn_per_iter_per_step:
        for k in range(n_FR):
            for L in range(3):
                attn = step[k][L]
                ent = entropy_per_query(attn).mean().item()
                max_ent = float(np.log(attn.shape[-1]))
                per_layer_iter[(L, k)].append(ent / max_ent)

    print(f"\n=== {label} attention entropy (1.0 = uniform; lower = sharper) ===")
    print(f"{'layer':<6s}{'iter':<6s}{'mean_ent/max':>14s}{'frac<0.80':>12s}{'frac<0.95':>12s}")
    print("-" * 50)
    for L in range(3):
        for k in range(n_FR):
            arr = np.array(per_layer_iter[(L, k)])
            print(f"C_{L+1:<4d}{k:<6d}{arr.mean():>14.4f}{(arr<0.80).mean():>12.2%}{(arr<0.95).mean():>12.2%}")

    all_ent = np.concatenate([per_layer_iter[(L, k)] for L in range(3) for k in range(n_FR)])
    overall_below_80 = float((all_ent < 0.80).mean())
    overall_below_95 = float((all_ent < 0.95).mean())
    print(f"OVERALL {label}: frac<0.80 = {overall_below_80:.1%}, frac<0.95 = {overall_below_95:.1%}")
    return overall_below_80, overall_below_95


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", default=os.path.join(_PROJECT_ROOT, "RViT_plus", "checkpoints", "rvit_plus_latest.pt"))
    p.add_argument("--n-sequences", type=int, default=8)
    p.add_argument("--seq-len", type=int, default=10)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args(argv)

    if not os.path.exists(args.ckpt):
        print(f"checkpoint not found: {args.ckpt}")
        return 1
    device = _select_device()
    print(f"[entropy] {args.ckpt} on {device}")
    model = _load_model(args.ckpt, device)

    dataset = MovingMNIST(n_sequences=args.n_sequences, seq_len=args.seq_len,
                          frame_hw=50, digit_hw=14, n_digits=2, seed_base=args.seed)

    # Aggregate attention maps across multiple sequences.
    encoder_attns_all = []  # list of (S_total) per-step lists
    decoder_attns_all = []

    with torch.no_grad():
        for s in range(args.n_sequences):
            seq = dataset[s].to(device).unsqueeze(0)
            out = model.compress_and_reconstruct(seq)
            for fr in out.encoder_attn_per_frame:
                encoder_attns_all.append(fr)
            for st in out.decoder_attn_per_step:
                decoder_attns_all.append(st)

    enc_p1, enc_p2 = summarize("ENCODER (per-frame)", encoder_attns_all, model)
    dec_p1, dec_p2 = summarize("DECODER (per-step)", decoder_attns_all, model)

    print("\n=== P1 verdict ===")
    print(f"  Encoder: frac<0.80 = {enc_p1:.1%}  (target ≥ 50% to confirm P1)")
    print(f"  Decoder: frac<0.80 = {dec_p1:.1%}  (target ≥ 50% to confirm P1)")
    if enc_p1 >= 0.50 or dec_p1 >= 0.50:
        print("  P1: ✓ at least one side has emergent attention structure")
    elif enc_p2 < 0.50 and dec_p2 < 0.50:
        print("  P1: ✗ attention essentially uniform across both encoder and decoder")
    else:
        print("  P1: ~ partial — attention emerging but not yet sharp")
    return 0


if __name__ == "__main__":
    sys.exit(main())
