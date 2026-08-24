"""
Stage 1 training: VIDEO-COMPRESSION pretraining for RViT+.

The model encodes the entire input video into a final compressed hidden
state, samples a VAE latent from that state, then unrolls the decoder T
times to reconstruct the full video. This is genuine compression — the
encoder MUST retain information across time into the final state, and the
decoder MUST unpack it. Attention has real work to do because spatial info
from early frames has to propagate to the final state.

Per the owner's clarification (which corrected the per-frame autoencoding
failure mode): "the video autoencoder watches the video until the very end,
compressing along the way, then decodes from the last time step backwards."
Direction (forward vs backward decode) is implementation-equivalent; we
decode forward (recons[τ] = predicted x_τ) because the temporal-embedding
math is cleaner.

Usage:
    .venv/bin/python RViT_plus/train.py
    .venv/bin/python RViT_plus/train.py --iters 100 --batch-size 4   # smoke
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from collections import deque
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus.config.loader import (
    DEFAULT_CONFIG_PATH, cfg_get, load_checkpoint_weights, load_config,
    print_resolved_config,
)
from RViT_plus.data import MovingMNIST
from RViT_plus.model import RViTPlusModel


def _select_device(override: Optional[str] = None) -> torch.device:
    if override:
        return torch.device(override)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _set_seed(seed: int) -> None:
    import random
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def compute_loss(
    out: "CompressionOutput",
    video: torch.Tensor,
    kl_coef: float = 0.0,                    # run-13: VAE skipped, KL term unused
    *,
    recon_kind: str = "l1",
    free_bits: float = 2.0,
    content_weight: float = 10.0,
    content_threshold: float = 0.5,
) -> dict:
    """Reconstruction loss (content-weighted L1 or MSE per timestep) + free-bits KL.

    Run-7 changes (2026-05-20):
      • recon_kind defaults to "l1". MSE is still reported as a secondary metric.
      • Free-bits KL: don't penalize KL below `free_bits` nats per dim. Prevents
        posterior collapse.

    Run-8 changes (2026-05-20) after run-7 demonstrated that both MSE and L1
    have the same trivial-constant trap on background-dominant data
    (recon=-1 everywhere achieves L1=0.013 ≈ 1 + mean(input)):
      • Content weighting. Pixels where |input| > content_threshold are
        weighted `content_weight`× over background pixels. The weighted loss is
        normalized so its expected value matches the unweighted version's
        scale, but the per-pixel gradient is sharply biased toward digit
        pixels. This breaks the trivial-constant minimum: predicting -1
        everywhere now produces L1 dominated by the digit-pixel residual
        (which has weight `content_weight`), so the model can no longer
        achieve a low loss by ignoring digit content.
    """
    B, T = video.shape[:2]
    recon = torch.stack(out.recons, dim=1)  # (B, T, 3, H, W)

    # ── Content-weight mask ────────────────────────────────────────────────
    # MovingMNIST: background = -1 everywhere, digit strokes are +1 in their
    # colored channel. `(video > 0.5).any(dim=2)` flags positions where at
    # least one channel is bright (i.e. digit-stroke positions). The whole
    # RGB triple at digit positions is weighted up; background gets weight 1.
    with torch.no_grad():
        digit_mask = (video > content_threshold).any(dim=2, keepdim=True).float()
        weight = 1.0 + (content_weight - 1.0) * digit_mask
        weight = weight / weight.mean().clamp(min=1e-6)

    # ── Reconstruction loss (per-timestep) ─────────────────────────────────
    if recon_kind == "l1":
        per_pix_err = (recon - video).abs()
    elif recon_kind == "mse":
        per_pix_err = (recon - video).pow(2)
    else:
        raise ValueError(f"unknown recon_kind={recon_kind}")
    weighted_err = weight * per_pix_err
    per_t_recon = weighted_err.mean(dim=(0, 2, 3, 4))  # (T,)
    recon_loss = per_t_recon.mean()

    # Also report MSE (always) for cross-run sanity even when we train on L1.
    with torch.no_grad():
        per_t_mse = F.mse_loss(recon, video, reduction="none").mean(dim=(0, 2, 3, 4))

    # ── KL (skipped in run-13 — no VAE bottleneck) ─────────────────────────
    if out.kl_per_dim is not None:
        # Latent path is back in scope; original Kingma-2016 free-bits hinge.
        kl_per_dim_batch = out.kl_per_dim.mean(dim=0)
        kl_hinge = torch.clamp(kl_per_dim_batch - free_bits, min=0.0).sum()
        kl_loss = kl_hinge
        kl_raw = out.kl
    else:
        # Run-13: no VAE; KL contributes nothing to the gradient.
        kl_loss = torch.zeros((), device=recon_loss.device, dtype=recon_loss.dtype)
        kl_raw = kl_loss

    total = recon_loss + kl_coef * kl_loss
    return {
        "recon": recon_loss,
        "kl": kl_loss,
        "kl_raw": kl_raw,
        "total": total,
        "per_t_mse": per_t_mse.detach(),
        "per_t_recon": per_t_recon.detach(),
    }


def train_one_batch(
    model: RViTPlusModel,
    batch: torch.Tensor,
    optimizer: torch.optim.Optimizer,
    *,
    kl_coef: float,
    grad_clip: float,
    recon_kind: str = "l1",
    free_bits: float = 2.0,
    content_weight: float = 10.0,
) -> dict:
    """One full encode-decode pass + loss + step."""
    model.train()
    out = model.compress_and_reconstruct(batch)
    losses = compute_loss(out, batch, kl_coef=kl_coef, recon_kind=recon_kind,
                          free_bits=free_bits, content_weight=content_weight)

    optimizer.zero_grad(set_to_none=True)
    losses["total"].backward()
    grad_norm = nn.utils.clip_grad_norm_(model.parameters(), max_norm=grad_clip)

    base_stats = {
        "recon": float(losses["recon"].detach().item()),
        "kl_hinge": float(losses["kl"].detach().item()),
        "kl_raw": float(losses["kl_raw"].detach().item()),
        "total": float(losses["total"].detach().item()),
        "per_t_mse_first": float(losses["per_t_mse"][0].item()),
        "per_t_mse_last": float(losses["per_t_mse"][-1].item()),
    }
    if not torch.isfinite(grad_norm):
        optimizer.zero_grad(set_to_none=True)
        return {**base_stats, "grad_norm": float("inf"), "skipped": 1}
    optimizer.step()
    return {
        **base_stats,
        "grad_norm": float(grad_norm.detach().item() if hasattr(grad_norm, "detach") else float(grad_norm)),
        "skipped": 0,
    }


def main(argv=None) -> int:
    # Two-stage parsing: load config first, use as argparse defaults.
    cfg_parser = argparse.ArgumentParser(add_help=False)
    cfg_parser.add_argument("--config", default=DEFAULT_CONFIG_PATH,
                             help="Path to TOML config file.")
    cfg_args, _ = cfg_parser.parse_known_args(argv)
    cfg = load_config(cfg_args.config)

    p = argparse.ArgumentParser(parents=[cfg_parser])

    # Loading / resumption — shared across AE and RL training.
    # See config/rvit_plus_config.json _note_init_mode for full semantics.
    p.add_argument("--init-mode",
                   choices=["fresh", "warm_start", "resume"],
                   default=cfg_get(cfg, "run.init_mode", "fresh"),
                   help="fresh = random init (ignore checkpoint_path); "
                        "warm_start = partial load (skip mismatches silently); "
                        "resume = strict load (fail on any mismatch).")
    p.add_argument("--checkpoint-path",
                   default=cfg_get(cfg, "run.checkpoint_path", None),
                   help="Path to a checkpoint to load when init_mode is warm_start or resume.")

    # Training schedule (AE section in config)
    p.add_argument("--iters", type=int, default=cfg_get(cfg, "ae.iters", 2000))
    p.add_argument("--batch-size", type=int, default=cfg_get(cfg, "ae.batch_size", 8))
    p.add_argument("--seq-len", type=int, default=cfg_get(cfg, "ae.seq_len", 10))
    p.add_argument("--lr", type=float, default=cfg_get(cfg, "ae.lr", 3e-4))
    p.add_argument("--warmup-iters", type=int, default=cfg_get(cfg, "ae.warmup_iters", 0),
                   help="Progressive T curriculum (0 = disabled).")
    p.add_argument("--kl-coef", type=float, default=cfg_get(cfg, "ae.kl_coef", 0.001))
    p.add_argument("--free-bits", type=float, default=cfg_get(cfg, "ae.free_bits", 2.0))
    p.add_argument("--recon-kind", default=cfg_get(cfg, "ae.recon_kind", "l1"),
                   choices=["l1", "mse"])
    p.add_argument("--content-weight", type=float, default=cfg_get(cfg, "ae.content_weight", 10.0))
    p.add_argument("--grad-clip", type=float, default=cfg_get(cfg, "ae.grad_clip", 0.5))
    p.add_argument("--n-FR", type=int, default=cfg_get(cfg, "model.n_FR", 4))

    # I/O
    p.add_argument("--seed", type=int, default=cfg_get(cfg, "run.seed", 0))
    p.add_argument("--device", default=cfg_get(cfg, "run.device", None),
                   choices=[None, "cpu", "mps", "cuda"])
    p.add_argument("--checkpoint-dir",
                   default=cfg_get(cfg, "run.checkpoint_dir", os.path.join(_HERE, "checkpoints")))
    p.add_argument("--save-every", type=int, default=cfg_get(cfg, "run.save_every", 250))
    p.add_argument("--log-every", type=int, default=cfg_get(cfg, "run.log_every", 20))
    args = p.parse_args(argv)

    print_resolved_config(cfg, used_keys=[
        "run.init_mode", "run.checkpoint_path", "run.seed", "run.device",
        "run.checkpoint_dir", "run.save_every", "run.log_every",
        "ae.iters", "ae.batch_size", "ae.seq_len", "ae.lr",
        "ae.warmup_iters", "ae.kl_coef", "ae.free_bits", "ae.recon_kind",
        "ae.content_weight", "ae.grad_clip", "model.n_FR",
    ])

    _set_seed(args.seed)
    device = _select_device(args.device)
    print(f"[setup] device = {device}, seed = {args.seed}")

    model = RViTPlusModel(
        in_channels=3, image_h=50, image_w=50,
        stem_out_channels=64, state_channels=(64, 96, 128),
        n_FR=args.n_FR, n_heads=4,
        seq_len=args.seq_len,
        upsample_out_channels=32, cnn_hidden=64,
        enable_skips=True, skip_scale=0.3,
        max_T=max(args.seq_len, 32),
    ).to(device)

    # ── Checkpoint load (driven by init_mode) ────────────────────────────
    if args.init_mode == "fresh":
        print(f"[init] init_mode=fresh — random init, checkpoint_path ignored")
    elif not args.checkpoint_path:
        print(f"[init] WARNING: init_mode={args.init_mode} but no checkpoint_path "
              f"given; falling back to random init")
    elif not os.path.exists(args.checkpoint_path):
        print(f"[init] WARNING: init_mode={args.init_mode} but checkpoint_path "
              f"'{args.checkpoint_path}' does not exist; falling back to random init")
    else:
        strict = (args.init_mode == "resume")
        info = load_checkpoint_weights(model, args.checkpoint_path,
                                        strict=strict, device=device)
        if strict:
            print(f"[init] RESUME (strict) from {args.checkpoint_path} "
                  f"(iter={info['ckpt_iter']}, {info['loaded']} tensors restored)")
        else:
            print(f"[init] WARM_START (partial) from {args.checkpoint_path}:")
            print(f"[init]   restored from ckpt:       {info['loaded']} tensors")
            print(f"[init]   ckpt tensors discarded:   {info['skipped']} "
                  f"(extra/shape-mismatch — not present in current model)")
            print(f"[init]   model tensors stayed RANDOM: {info['n_random_init']} "
                  f"(missing from ckpt or shape changed)")
            rand_keys = info.get("random_init_keys", [])
            if rand_keys:
                preview = rand_keys[:8]
                more = f"  (+{len(rand_keys) - 8} more)" if len(rand_keys) > 8 else ""
                print(f"[init]   random-init preview: {', '.join(preview)}{more}")

    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[diag] params = {n_params:,}")
    print(f"[diag] n_FR = {args.n_FR}, batch = {args.batch_size}, T = {args.seq_len}")
    print(f"[diag] losses: recon={args.recon_kind} (content_weight={args.content_weight}), kl_coef={args.kl_coef} (no VAE in run-13)")
    print(f"[diag] mode  : VIDEO COMPRESSION (encode full sequence → latent → decode T frames)")

    dataset = MovingMNIST(
        n_sequences=max(args.batch_size, 1000),
        seq_len=args.seq_len, frame_hw=50, digit_hw=14, n_digits=2,
        seed_base=args.seed * 10000,
    )

    def sample_batch() -> torch.Tensor:
        items = [dataset[np.random.randint(0, dataset.n_sequences)] for _ in range(args.batch_size)]
        return torch.stack(items, dim=0).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, eps=1e-5)
    recon_buf = deque(maxlen=50)
    kl_buf = deque(maxlen=50)
    os.makedirs(args.checkpoint_dir, exist_ok=True)
    t_start = time.time()
    n_skipped = 0

    # Run-11 progressive curriculum: T=1 → T=2 → … → T=seq_len, each stage
    # gets warmup_iters / seq_len iters; after warmup_iters, stay at T=seq_len.
    # T must increment by 1 — a jump T=1 → T=10 isn't a curriculum, it's a
    # hard switch.
    if args.warmup_iters > 0 and args.seq_len > 1:
        stage_iters = max(1, args.warmup_iters // args.seq_len)
    else:
        stage_iters = 0

    def _T_at_iter(it: int) -> int:
        if stage_iters == 0:
            return args.seq_len
        if it >= args.warmup_iters:
            return args.seq_len
        # Stage k (0-indexed) covers iters [k*stage_iters, (k+1)*stage_iters).
        # T at stage k = k + 1 (so first stage is T=1, second T=2, ...).
        stage = it // stage_iters
        return min(stage + 1, args.seq_len)

    last_T = None
    for it in range(args.iters):
        T_now = _T_at_iter(it)
        if T_now != last_T:
            print(f"[curriculum] iter {it}: T = {T_now}")
            last_T = T_now

        batch_full = sample_batch()           # (B, args.seq_len, 3, H, W)
        batch = batch_full[:, :T_now]         # truncate to current T
        stats = train_one_batch(model, batch, optimizer,
                                 kl_coef=args.kl_coef, grad_clip=args.grad_clip,
                                 recon_kind=args.recon_kind, free_bits=args.free_bits,
                                 content_weight=args.content_weight)
        n_skipped += int(stats["skipped"])
        recon_buf.append(stats["recon"])
        kl_buf.append(stats["kl_raw"])

        if (it + 1) % args.log_every == 0:
            elapsed = time.time() - t_start
            roll_recon = sum(recon_buf) / max(len(recon_buf), 1)
            roll_kl = sum(kl_buf) / max(len(kl_buf), 1)
            print(
                f"[iter {it:5d} | {elapsed:6.1f}s] "
                f"recon={stats['recon']:.4f} (50avg {roll_recon:.4f}) "
                f"kl_raw={stats['kl_raw']:.4f} (50avg {roll_kl:.4f}) "
                f"kl_hinge={stats['kl_hinge']:.4f} "
                f"mse_t0={stats['per_t_mse_first']:.4f} "
                f"mse_tT={stats['per_t_mse_last']:.4f} "
                f"gn={stats['grad_norm']:.3f} "
                f"skipped={n_skipped}"
            )

        if (it + 1) % args.save_every == 0:
            ckpt_path = os.path.join(args.checkpoint_dir, "rvit_plus_latest.pt")
            torch.save({
                "iter": it,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "model_kwargs": {
                    "in_channels": 3, "image_h": 50, "image_w": 50,
                    "stem_out_channels": 64,
                    "state_channels": (64, 96, 128),
                    "n_FR": args.n_FR, "n_heads": 4, "seq_len": args.seq_len,
                    "upsample_out_channels": 32, "cnn_hidden": 64,
                    "enable_skips": True, "skip_scale": 0.3,
                    "max_T": max(args.seq_len, 32),
                },
            }, ckpt_path)
            print(f"[checkpoint] saved to {ckpt_path}")

    # Final save.
    final_path = os.path.join(args.checkpoint_dir, "rvit_plus_latest.pt")
    torch.save({
        "iter": args.iters - 1,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "model_kwargs": {
            "in_channels": 3, "image_h": 50, "image_w": 50,
            "stem_out_channels": 64,
            "state_channels": (64, 96, 128),
            "n_FR": args.n_FR, "n_heads": 4, "latent_channels": 16,
            "enable_skips": True, "skip_scale": 0.3,
            "max_T": max(args.seq_len, 32),
        },
    }, final_path)
    print(f"[done] final checkpoint at {final_path}")
    print(f"[done] {args.iters} iterations, {n_skipped} grad-skips")
    return 0


if __name__ == "__main__":
    sys.exit(main())
