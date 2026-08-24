"""
RL training entry point for RViT+ on Posner change-detection.

Trains the shared encoder + actor + distributional critic + decoder
auxiliary jointly. Three gradient sources flow into the encoder:
policy gradient (PPO), distributional value gradient (quantile-Huber),
and reconstruction (content-weighted MSE).

Usage:
    .venv/bin/python RViT_plus/train_rl.py
    .venv/bin/python RViT_plus/train_rl.py --iters 500 --pretrain 50
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

from RViT_plus.config.loader import (
    DEFAULT_CONFIG_PATH, cfg_get, load_checkpoint_weights, load_config,
    print_resolved_config,
)
from RViT_plus.env import ChangeDetectionEnv
from RViT_plus.model import RViTPlusModel
from RViT_plus.ppo import PPOConfig, train


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


def main(argv=None) -> int:
    # ── Step 1: parse just --config to figure out which config file to load. ──
    cfg_parser = argparse.ArgumentParser(add_help=False)
    cfg_parser.add_argument("--config", default=DEFAULT_CONFIG_PATH,
                             help="Path to TOML config file. Default: RViT_plus/config/rvit_plus_config.toml")
    cfg_args, _remaining = cfg_parser.parse_known_args(argv)
    cfg = load_config(cfg_args.config)

    # ── Step 2: build the main parser, using config values as defaults. ──
    # `cfg_get(cfg, key, fallback)` returns the config value if present
    # (and non-empty), else the script-hardcoded fallback.
    p = argparse.ArgumentParser(parents=[cfg_parser])

    # ── Loading / resumption ──
    # init_mode determines what happens with checkpoint_path:
    #   'fresh'      → random init, checkpoint_path ignored.
    #   'warm_start' → load matching tensors from checkpoint_path; skip the rest.
    #   'resume'     → strict load; fail if any tensor missing/extra/shape-mismatched.
    p.add_argument("--init-mode",
                   choices=["fresh", "warm_start", "resume"],
                   default=cfg_get(cfg, "run.init_mode", "fresh"),
                   help="fresh = random init (ignore checkpoint_path); "
                        "warm_start = partial load (skip mismatches silently); "
                        "resume = strict load (fail on any mismatch).")
    p.add_argument("--checkpoint-path",
                   default=cfg_get(cfg, "run.checkpoint_path", None),
                   help="Path to a checkpoint to load when init_mode is warm_start or resume.")

    # ── Training schedule ──
    p.add_argument("--iters", type=int, default=cfg_get(cfg, "ppo.iters", 500))
    p.add_argument("--episodes-per-iter", type=int, default=cfg_get(cfg, "ppo.episodes_per_iter", 8))
    p.add_argument("--seq-len", type=int, default=cfg_get(cfg, "ppo.seq_len", 29))

    # ── Model architecture ──
    p.add_argument("--n-FR", type=int, default=cfg_get(cfg, "model.n_FR", 4))
    p.add_argument("--n-quantiles", type=int, default=cfg_get(cfg, "model.rl.n_quantiles", 51))
    p.add_argument("--n-actions", type=int, default=cfg_get(cfg, "model.rl.n_actions", 2))
    p.add_argument("--split-c3", action="store_true",
                   default=bool(cfg_get(cfg, "model.rl.split_c3", False)),
                   help="Use separate C3 specialist cells per task (AE / actor / critic).")
    p.add_argument("--init-action-bias", type=float, nargs="+",
                   default=list(cfg_get(cfg, "model.rl.init_action_bias", [0.0, -4.0])),
                   help="Per-action initial logit bias for the actor.")
    p.add_argument("--contrastive-projection-dim", type=int,
                   default=cfg_get(cfg, "model.rl.contrastive_projection_dim", 128),
                   help="Output dim of the SimCLR-style projection head used by the "
                        "contrastive auxiliary losses.")

    # ── PPO hyperparameters ──
    p.add_argument("--lr", type=float, default=cfg_get(cfg, "ppo.lr", 3e-4))
    p.add_argument("--gamma", type=float, default=cfg_get(cfg, "ppo.gamma", 0.95))
    p.add_argument("--gae-lambda", type=float, default=cfg_get(cfg, "ppo.gae_lambda", 0.95))
    p.add_argument("--clip-range", type=float, default=cfg_get(cfg, "ppo.clip_range", 0.2))
    p.add_argument("--n-epochs", type=int, default=cfg_get(cfg, "ppo.n_epochs", 4))

    # ── Loss coefficients ──
    p.add_argument("--value-coef", type=float, default=cfg_get(cfg, "ppo.value_coef", 0.5))
    p.add_argument("--entropy-coef", type=float, default=cfg_get(cfg, "ppo.entropy_coef", 0.01))
    p.add_argument("--recon-coef", type=float, default=cfg_get(cfg, "ppo.recon_coef", 0.5))
    p.add_argument("--content-weight", type=float, default=cfg_get(cfg, "ppo.content_weight", 100.0))
    p.add_argument("--recon-pretrain-iters", type=int,
                   default=cfg_get(cfg, "ppo.recon_pretrain_iters", 0))
    p.add_argument("--contrastive-actor-coef", type=float,
                   default=cfg_get(cfg, "ppo.contrastive_actor_coef", 0.1),
                   help="Weight on the actor contrastive loss (same action AND same reward → "
                        "attract; otherwise repel below cosine margin).")
    p.add_argument("--contrastive-critic-coef", type=float,
                   default=cfg_get(cfg, "ppo.contrastive_critic_coef", 0.1),
                   help="Weight on the critic contrastive loss (Q-similarity-weighted attract, "
                        "per-step error-difference-weighted repel).")
    p.add_argument("--contrastive-margin", type=float,
                   default=cfg_get(cfg, "ppo.contrastive_margin", 0.5),
                   help="Cosine margin for the repulsive term in both contrastive losses.")
    p.add_argument("--pc-actor-coef", type=float,
                   default=cfg_get(cfg, "ppo.pc_actor_coef", 0.1),
                   help="Weight on the actor predictive-coding loss: "
                        "1 − cos(P_actor(C_{3,actor,t-1}), C_{2,t}.detach()).")
    p.add_argument("--pc-critic-coef", type=float,
                   default=cfg_get(cfg, "ppo.pc_critic_coef", 0.1),
                   help="Weight on the critic predictive-coding loss.")
    p.add_argument("--mpo-temperature", type=float,
                   default=cfg_get(cfg, "ppo.mpo_temperature", 1.0),
                   help="η in the PAC/MPO E-step: q(a|s) ∝ π_old(a|s)·exp(Q̄(s,a)/η).")
    p.add_argument("--bc-alpha", type=float,
                   default=cfg_get(cfg, "ppo.bc_alpha", 0.1),
                   help="BC blend in the PAC actor loss: 0=pure MPO, 1=pure BC.")

    # ── PER buffer ──
    p.add_argument("--buffer-capacity", type=int,
                   default=cfg_get(cfg, "ppo.buffer_capacity", 200),
                   help="Capacity of the episode replay buffer (in episodes).")
    p.add_argument("--per-n-replay", type=int,
                   default=cfg_get(cfg, "ppo.per_n_replay", 4),
                   help="How many replay episodes to append to the fresh batch each PPO update. 0 = pure on-policy.")
    p.add_argument("--per-alpha", type=float,
                   default=cfg_get(cfg, "ppo.per_alpha", 0.6),
                   help="PER priority exponent: p_i ∝ priority_i^α. 0 = uniform.")
    p.add_argument("--per-beta-start", type=float,
                   default=cfg_get(cfg, "ppo.per_beta_start", 0.4),
                   help="PER importance-sampling exponent at training start.")
    p.add_argument("--per-beta-end", type=float,
                   default=cfg_get(cfg, "ppo.per_beta_end", 1.0),
                   help="PER importance-sampling exponent at training end (linear anneal).")
    p.add_argument("--per-priority-clip", type=float,
                   default=cfg_get(cfg, "ppo.per_priority_clip", 50.0),
                   help="Cap priorities at this multiple of the median (prevents outliers dominating).")

    # ── I/O ──
    p.add_argument("--seed", type=int, default=cfg_get(cfg, "run.seed", 0))
    p.add_argument("--device", default=cfg_get(cfg, "run.device", None),
                   choices=[None, "cpu", "mps", "cuda"])
    p.add_argument("--checkpoint-dir",
                   default=cfg_get(cfg, "run.checkpoint_dir", os.path.join(_HERE, "checkpoints")))
    p.add_argument("--save-every", type=int, default=cfg_get(cfg, "run.save_every", 200))
    p.add_argument("--log-every", type=int, default=cfg_get(cfg, "run.log_every", 1))

    args = p.parse_args(argv)
    print_resolved_config(cfg, used_keys=[
        "run.init_mode", "run.checkpoint_path", "run.seed", "run.device",
        "run.checkpoint_dir", "run.save_every", "run.log_every",
        "ppo.iters", "ppo.episodes_per_iter", "ppo.seq_len",
        "model.n_FR", "model.rl.n_quantiles", "model.rl.n_actions",
        "model.rl.split_c3", "model.rl.init_action_bias",
        "model.rl.contrastive_projection_dim",
        "ppo.lr", "ppo.gamma", "ppo.gae_lambda", "ppo.clip_range", "ppo.n_epochs",
        "ppo.value_coef", "ppo.entropy_coef",
        "ppo.recon_coef", "ppo.content_weight", "ppo.recon_pretrain_iters",
        "ppo.contrastive_actor_coef", "ppo.contrastive_critic_coef",
        "ppo.contrastive_margin",
        "ppo.pc_actor_coef", "ppo.pc_critic_coef",
        "ppo.mpo_temperature", "ppo.bc_alpha",
        "ppo.buffer_capacity", "ppo.per_n_replay", "ppo.per_alpha",
        "ppo.per_beta_start", "ppo.per_beta_end", "ppo.per_priority_clip",
    ])

    _set_seed(args.seed)
    device = _select_device(args.device)

    # ── Model ────────────────────────────────────────────────────────────
    # seq_len must cover the full episode (T=29 for ChangeDetectionEnv) so the
    # decoder's output channel partition is correct.
    model = RViTPlusModel(
        in_channels=3, image_h=50, image_w=50,
        stem_out_channels=64, state_channels=(64, 96, 128),
        n_FR=args.n_FR, n_heads=4,
        seq_len=args.seq_len,
        upsample_out_channels=32, cnn_hidden=64,
        enable_skips=True, skip_scale=0.3,
        enable_actor=True, enable_critic=True,
        n_actions=args.n_actions, n_quantiles=args.n_quantiles,
        rl_per_state_channels=32, rl_cnn_hidden=64,
        init_action_bias=list(args.init_action_bias),
        split_c3=args.split_c3,
        contrastive_projection_dim=args.contrastive_projection_dim,
    ).to(device)
    print(f"[diag] actor init bias: {list(args.init_action_bias)}")
    print(f"[diag] split_c3: {args.split_c3}")
    print(f"[diag] contrastive: actor_coef={args.contrastive_actor_coef}, "
          f"critic_coef={args.contrastive_critic_coef}, margin={args.contrastive_margin}")
    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[diag] total params: {n_params:,}")
    print(f"[diag] n_actions={args.n_actions}, n_quantiles={args.n_quantiles}, seq_len={args.seq_len}")

    # ── Checkpoint load (driven by init_mode) ────────────────────────────
    #   'fresh'      → skip loading entirely.
    #   'warm_start' → partial load (silently skip missing/shape-mismatched).
    #   'resume'     → strict load (fail loudly on any mismatch).
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

    # ── Env ─────────────────────────────────────────────────────────────
    env = ChangeDetectionEnv()
    # Verify env max length matches seq_len.
    if env.T != args.seq_len:
        print(f"[setup] WARNING: env.T = {env.T} but --seq-len = {args.seq_len}. "
              f"Episodes longer than seq_len will cause padding issues.")

    # ── PPO config ──────────────────────────────────────────────────────
    cfg = PPOConfig(
        lr=args.lr, n_epochs=args.n_epochs, clip_range=args.clip_range,
        value_coef=args.value_coef, entropy_coef=args.entropy_coef,
        recon_coef=args.recon_coef, content_weight=args.content_weight,
        gamma=args.gamma, gae_lambda=args.gae_lambda,
        recon_pretrain_iters=args.recon_pretrain_iters,
        contrastive_actor_coef=args.contrastive_actor_coef,
        contrastive_critic_coef=args.contrastive_critic_coef,
        contrastive_margin=args.contrastive_margin,
        pc_actor_coef=args.pc_actor_coef,
        pc_critic_coef=args.pc_critic_coef,
        mpo_temperature=args.mpo_temperature,
        bc_alpha=args.bc_alpha,
        buffer_capacity=args.buffer_capacity,
        per_n_replay=args.per_n_replay,
        per_alpha=args.per_alpha,
        per_beta_start=args.per_beta_start,
        per_beta_end=args.per_beta_end,
        per_priority_clip=args.per_priority_clip,
    )

    # ── Train ───────────────────────────────────────────────────────────
    history = train(
        model=model, env=env, n_iterations=args.iters,
        episodes_per_iter=args.episodes_per_iter, cfg=cfg,
        device=device, log_every=args.log_every,
        checkpoint_dir=args.checkpoint_dir, save_every=args.save_every,
    )

    # Final save.
    os.makedirs(args.checkpoint_dir, exist_ok=True)
    final_path = os.path.join(args.checkpoint_dir, "rvit_plus_rl_final.pt")
    torch.save({
        "iter": args.iters - 1,
        "model_state_dict": model.state_dict(),
        "model_kwargs": {
            "in_channels": 3, "image_h": 50, "image_w": 50,
            "stem_out_channels": 64, "state_channels": (64, 96, 128),
            "n_FR": args.n_FR, "n_heads": 4, "seq_len": args.seq_len,
            "upsample_out_channels": 32, "cnn_hidden": 64,
            "enable_skips": True, "skip_scale": 0.3,
            "enable_actor": True, "enable_critic": True,
            "n_actions": args.n_actions, "n_quantiles": args.n_quantiles,
            "split_c3": args.split_c3,
            "contrastive_projection_dim": args.contrastive_projection_dim,
        },
    }, final_path)
    print(f"[done] final checkpoint at {final_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
