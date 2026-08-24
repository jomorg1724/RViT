"""
Training entry point for V6 — Multi-Layer Feedback Transformer on the ViZDoom
deathmatch arena.

Usage:
    .venv/bin/python v6_VizdoomArena/train_rl.py                 # full run (MPS auto)
    .venv/bin/python v6_VizdoomArena/train_rl.py --iters 50 --warmup-iters 5
    .venv/bin/python v6_VizdoomArena/train_rl.py --device cpu --seg-len 16
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from v6_VizdoomArena.config.loader import (
    DEFAULT_CONFIG_PATH, cfg_get, load_checkpoint_weights, load_config,
    print_resolved_config,
)
from v6_VizdoomArena.env import FEAT_DIM, FEAT_GROUPS, N_ACTIONS, VizdoomArenaEnv
from v6_VizdoomArena.model import V6ArenaModel
from v6_VizdoomArena.trainer import PACConfig, train


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


def main(argv=None) -> int:
    cfg_parser = argparse.ArgumentParser(add_help=False)
    cfg_parser.add_argument("--config", default=DEFAULT_CONFIG_PATH)
    cfg_args, _ = cfg_parser.parse_known_args(argv)
    cfg = load_config(cfg_args.config)

    p = argparse.ArgumentParser(parents=[cfg_parser])

    # ── Loading / resumption ──
    p.add_argument("--init-mode", choices=["fresh", "warm_start", "resume"],
                   default=cfg_get(cfg, "run.init_mode", "fresh"))
    p.add_argument("--checkpoint-path", default=cfg_get(cfg, "run.checkpoint_path", None))

    # ── Schedule ──
    p.add_argument("--iters", type=int, default=cfg_get(cfg, "trainer.iters", 20000))
    p.add_argument("--seg-len", type=int, default=cfg_get(cfg, "trainer.seg_len", 64))
    p.add_argument("--segments-per-iter", type=int,
                   default=cfg_get(cfg, "trainer.segments_per_iter", 4))

    # ── Environment ──
    p.add_argument("--frame-skip", type=int, default=cfg_get(cfg, "environment.frame_skip", 4))
    p.add_argument("--reward-kill", type=float, default=cfg_get(cfg, "environment.reward_kill", 1.0))
    p.add_argument("--reward-damage", type=float, default=cfg_get(cfg, "environment.reward_damage", 0.02))
    p.add_argument("--reward-hit", type=float, default=cfg_get(cfg, "environment.reward_hit", 0.5))
    p.add_argument("--reward-taken", type=float, default=cfg_get(cfg, "environment.reward_taken", 0.005))
    p.add_argument("--reward-ammo-spent", type=float,
                   default=cfg_get(cfg, "environment.reward_ammo_spent", 0.01))
    p.add_argument("--reward-health-gain", type=float,
                   default=cfg_get(cfg, "environment.reward_health_gain", 0.01))
    p.add_argument("--reward-death", type=float, default=cfg_get(cfg, "environment.reward_death", 1.0))
    p.add_argument("--reward-clip", type=float, default=cfg_get(cfg, "environment.reward_clip", 5.0))

    # ── Model ──
    p.add_argument("--patch-size", type=int, default=cfg_get(cfg, "model.patch_size", 10))
    p.add_argument("--patch-hidden", type=int, default=cfg_get(cfg, "model.patch_hidden", 128))
    p.add_argument("--d-model", type=int, default=cfg_get(cfg, "model.d_model", 128))
    p.add_argument("--d-mem", type=int, default=cfg_get(cfg, "model.d_mem", 128))
    p.add_argument("--enc-heads", type=int, default=cfg_get(cfg, "model.enc_heads", 8))
    p.add_argument("--enc-layers", type=int, default=cfg_get(cfg, "model.enc_layers", 2))
    p.add_argument("--dec-heads", type=int, default=cfg_get(cfg, "model.dec_heads", 8))
    p.add_argument("--dec-layers", type=int, default=cfg_get(cfg, "model.dec_layers", 2))
    p.add_argument("--head-hidden", type=int, default=cfg_get(cfg, "model.head_hidden", 128))
    p.add_argument("--head-layers", type=int, default=cfg_get(cfg, "model.head_layers", 2))
    p.add_argument("--drop", type=float, default=cfg_get(cfg, "model.drop", 0.1))
    p.add_argument("--n-quantiles", type=int, default=cfg_get(cfg, "model.rl.n_quantiles", 51))

    # ── PAC + QR-DQN ──
    p.add_argument("--lr", type=float, default=cfg_get(cfg, "trainer.lr", 3e-4))
    p.add_argument("--gamma", type=float, default=cfg_get(cfg, "trainer.gamma", 0.99))
    p.add_argument("--n-step", type=int, default=cfg_get(cfg, "trainer.n_step", 3))
    p.add_argument("--n-epochs", type=int, default=cfg_get(cfg, "trainer.n_epochs", 1))
    p.add_argument("--grad-clip", type=float, default=cfg_get(cfg, "trainer.grad_clip", 0.5))
    p.add_argument("--value-coef", type=float, default=cfg_get(cfg, "trainer.value_coef", 0.5))
    p.add_argument("--entropy-coef", type=float, default=cfg_get(cfg, "trainer.entropy_coef", 0.1))
    p.add_argument("--qr-kappa", type=float, default=cfg_get(cfg, "trainer.qr_kappa", 1.0))
    p.add_argument("--mpo-temperature", type=float, default=cfg_get(cfg, "trainer.mpo_temperature", 1.0))
    p.add_argument("--bc-alpha", type=float, default=cfg_get(cfg, "trainer.bc_alpha", 0.05))
    p.add_argument("--ref-uniform-mix", type=float,
                   default=cfg_get(cfg, "trainer.ref_uniform_mix", 0.05))
    p.add_argument("--explore-eps", type=float, default=cfg_get(cfg, "trainer.explore_eps", 0.05))
    p.add_argument("--ema-tau", type=float, default=cfg_get(cfg, "trainer.ema_tau", 0.01))
    p.add_argument("--warmup-iters", type=int, default=cfg_get(cfg, "trainer.warmup_iters", 50))
    p.add_argument("--replay-burn-in", type=int, default=cfg_get(cfg, "trainer.replay_burn_in", 8))

    # ── PER ──
    p.add_argument("--buffer-capacity", type=int, default=cfg_get(cfg, "trainer.buffer_capacity", 512))
    p.add_argument("--per-n-replay", type=int, default=cfg_get(cfg, "trainer.per_n_replay", 4))
    p.add_argument("--per-alpha", type=float, default=cfg_get(cfg, "trainer.per_alpha", 0.6))
    p.add_argument("--per-beta-start", type=float, default=cfg_get(cfg, "trainer.per_beta_start", 0.4))
    p.add_argument("--per-beta-end", type=float, default=cfg_get(cfg, "trainer.per_beta_end", 1.0))
    p.add_argument("--per-priority-clip", type=float, default=cfg_get(cfg, "trainer.per_priority_clip", 50.0))

    # ── I/O ──
    p.add_argument("--seed", type=int, default=cfg_get(cfg, "run.seed", 0))
    p.add_argument("--device", default=cfg_get(cfg, "run.device", None),
                   choices=[None, "cpu", "mps", "cuda"])
    p.add_argument("--checkpoint-dir", default=cfg_get(
        cfg, "run.checkpoint_dir",
        os.path.expanduser("~/rvit_plus_checkpoints/v6_vizdoom_arena")))
    p.add_argument("--save-every", type=int, default=cfg_get(cfg, "run.save_every", 100))
    p.add_argument("--log-every", type=int, default=cfg_get(cfg, "run.log_every", 5))

    args = p.parse_args(argv)
    print_resolved_config(cfg, used_keys=sorted(cfg.keys()))

    _set_seed(args.seed)
    device = _select_device(args.device)

    model_kwargs = dict(
        in_channels=3, image_h=60, image_w=80,
        patch_size=args.patch_size, patch_hidden=args.patch_hidden,
        d_model=args.d_model, d_mem=args.d_mem,
        enc_heads=args.enc_heads, enc_layers=args.enc_layers,
        dec_heads=args.dec_heads, dec_layers=args.dec_layers,
        head_hidden=args.head_hidden, head_layers=args.head_layers,
        n_actions=N_ACTIONS, n_quantiles=args.n_quantiles,
        feat_dim=FEAT_DIM, state_groups=dict(FEAT_GROUPS), drop=args.drop,
    )
    model = V6ArenaModel(**model_kwargs).to(device)

    n_params = sum(p_.numel() for p_ in model.parameters() if p_.requires_grad)
    print(f"[diag] patch {args.patch_size}px → {model.n_tokens} tokens "
          f"({model.patch_embed.grid_h}×{model.patch_embed.grid_w}); "
          f"encoder keys/layer = {model.encoder.n_keys}; "
          f"key layout = {model.encoder.key_layout()}")
    print(f"[diag] total params: {n_params:,}")

    if args.init_mode == "fresh":
        print("[init] fresh — random init")
    elif not args.checkpoint_path or not os.path.exists(args.checkpoint_path):
        print(f"[init] WARNING: init_mode={args.init_mode} but checkpoint missing; random init")
    else:
        strict = (args.init_mode == "resume")
        info = load_checkpoint_weights(model, args.checkpoint_path, strict=strict, device=device)
        print(f"[init] {'RESUME (strict)' if strict else 'WARM_START (partial)'} "
              f"from {args.checkpoint_path} (iter={info['ckpt_iter']}, {info['loaded']} tensors)")

    env = VizdoomArenaEnv(
        frame_skip=args.frame_skip,
        reward_kill=args.reward_kill, reward_damage=args.reward_damage,
        reward_hit=args.reward_hit, reward_taken=args.reward_taken,
        reward_ammo_spent=args.reward_ammo_spent,
        reward_health_gain=args.reward_health_gain,
        reward_death=args.reward_death,
        reward_clip=args.reward_clip, seed=args.seed,
    )

    pac_cfg = PACConfig(
        lr=args.lr, n_epochs=args.n_epochs, grad_clip=args.grad_clip,
        mpo_temperature=args.mpo_temperature, bc_alpha=args.bc_alpha,
        ref_uniform_mix=args.ref_uniform_mix, explore_eps=args.explore_eps,
        ema_tau=args.ema_tau, warmup_iters=args.warmup_iters,
        seg_len=args.seg_len, segments_per_iter=args.segments_per_iter,
        replay_burn_in=args.replay_burn_in,
        buffer_capacity=args.buffer_capacity, per_n_replay=args.per_n_replay,
        per_alpha=args.per_alpha, per_beta_start=args.per_beta_start,
        per_beta_end=args.per_beta_end, per_priority_clip=args.per_priority_clip,
        value_coef=args.value_coef, entropy_coef=args.entropy_coef,
        qr_kappa=args.qr_kappa, gamma=args.gamma, n_step=args.n_step,
    )

    try:
        train(
            model=model, env=env, n_iterations=args.iters, cfg=pac_cfg,
            device=device, log_every=args.log_every,
            checkpoint_dir=args.checkpoint_dir, save_every=args.save_every,
            model_kwargs=model_kwargs,
        )
    finally:
        env.close()

    os.makedirs(args.checkpoint_dir, exist_ok=True)
    final_path = os.path.join(args.checkpoint_dir, "v6_final.pt")
    torch.save({"iter": args.iters - 1, "model_state_dict": model.state_dict(),
                "model_kwargs": model_kwargs}, final_path)
    print(f"[done] final checkpoint at {final_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
