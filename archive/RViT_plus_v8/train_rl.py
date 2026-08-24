"""
RL training entry point for RViT+ v5 on Posner change-detection.

v5 is conv-free and RL-only: a patch embedding feeds a 2-layer MEMORY-AS-TOKENS
transformer (each layer self-attends over [patch tokens ++ H₁ ++ H₂] = 3·N
tokens, no FiLM; a per-layer LSTMCell updates that layer's memory from the
patch-token outputs). The two recurrent states are read by 2-layer transformer
actor/critic decoders (CLS-token readout). The trainer is PAC (MPO+BC) +
distributional QR-DQN critic + prioritized episode replay — no reconstruction,
no predictive coding, no JEPA.

Usage:
    .venv/bin/python RViT_plus_v8/train_rl.py
    .venv/bin/python RViT_plus_v8/train_rl.py --iters 500 --patch-size 5
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

from RViT_plus_v8.config.loader import (
    DEFAULT_CONFIG_PATH, cfg_get, load_checkpoint_weights, load_config,
    print_resolved_config,
)
from RViT_plus_v8.env import ChangeDetectionEnv
from RViT_plus_v8.model import RViTPlusV5Part2Model
from RViT_plus_v8.ppo import PPOConfig, train


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
    cfg_parser = argparse.ArgumentParser(add_help=False)
    cfg_parser.add_argument("--config", default=DEFAULT_CONFIG_PATH,
                            help="Path to JSON config file.")
    cfg_args, _remaining = cfg_parser.parse_known_args(argv)
    cfg = load_config(cfg_args.config)

    p = argparse.ArgumentParser(parents=[cfg_parser])

    # ── Loading / resumption ──
    p.add_argument("--init-mode", choices=["fresh", "warm_start", "resume"],
                   default=cfg_get(cfg, "run.init_mode", "fresh"),
                   help="fresh = random init; warm_start = partial load; resume = strict load.")
    p.add_argument("--checkpoint-path", default=cfg_get(cfg, "run.checkpoint_path", None))

    # ── Training schedule ──
    p.add_argument("--iters", type=int, default=cfg_get(cfg, "ppo.iters", 500))
    p.add_argument("--episodes-per-iter", type=int, default=cfg_get(cfg, "ppo.episodes_per_iter", 8))
    p.add_argument("--seq-len", type=int, default=cfg_get(cfg, "ppo.seq_len", 29))
    # FRAME-REPEAT short-task experiment: hold each of --n-frames logical frames for
    # --frame-repeat physical steps (FROZEN pixels); change at logical --change-frame.
    p.add_argument("--frame-repeat", type=int, default=1,
                   help="Hold each logical frame for this many physical steps (1 = original).")
    p.add_argument("--n-frames", type=int, default=None,
                   help="Number of LOGICAL frames (task length). Default = env default (29).")
    p.add_argument("--change-frame", type=int, default=None,
                   help="Fixed LOGICAL change frame (sets min=max change time). Default = random.")

    # ── Model architecture (conv-free patch + single transformer encoder + stacked LSTMs) ──
    p.add_argument("--patch-size", type=int, default=cfg_get(cfg, "model.patch_size", 5))
    p.add_argument("--patch-hidden", type=int, default=cfg_get(cfg, "model.patch_hidden", 128),
                   help="Hidden width of the per-patch expansion MLP (raw patch ≈75 → patch_hidden → d_model).")
    p.add_argument("--d-model", type=int, default=cfg_get(cfg, "model.d_model", 128))
    p.add_argument("--d-mem", type=int, default=cfg_get(cfg, "model.d_mem", 128))
    p.add_argument("--tx-heads", type=int, default=cfg_get(cfg, "model.tx_heads", 8),
                   help="Attention heads in the single transformer encoder.")
    p.add_argument("--tx-layers", type=int, default=cfg_get(cfg, "model.tx_layers", 1),
                   help="Transformer-encoder depth (default 1 — a single encoder).")
    p.add_argument("--n-lstm", type=int, default=cfg_get(cfg, "model.n_lstm", 2),
                   help="Number of stacked per-token LSTMs = number of recurrent states.")
    p.add_argument("--conv-channels", type=int, default=cfg_get(cfg, "model.conv_channels", 64),
                   help="Channels in each decoder Conv1d layer.")
    p.add_argument("--n-conv-layers", type=int, default=cfg_get(cfg, "model.n_conv_layers", 3),
                   help="Number of stride-2 Conv1d layers per decoder head.")
    p.add_argument("--conv-kernel", type=int, default=cfg_get(cfg, "model.conv_kernel", 5),
                   help="Conv1d kernel size in the decoder heads.")
    p.add_argument("--n-quantiles", type=int, default=cfg_get(cfg, "model.rl.n_quantiles", 51))
    p.add_argument("--n-actions", type=int, default=cfg_get(cfg, "model.rl.n_actions", 2))
    p.add_argument("--init-action-bias", type=float, nargs="+",
                   default=list(cfg_get(cfg, "model.rl.init_action_bias", [0.0, -1.5])),
                   help="Per-action initial logit bias for the actor.")

    # ── PAC + QR-DQN hyperparameters ──
    p.add_argument("--lr", type=float, default=cfg_get(cfg, "ppo.lr", 3e-4))
    p.add_argument("--gamma", type=float, default=cfg_get(cfg, "ppo.gamma", 0.95))
    p.add_argument("--n-epochs", type=int, default=cfg_get(cfg, "ppo.n_epochs", 4))
    p.add_argument("--grad-clip", type=float, default=cfg_get(cfg, "ppo.grad_clip", 0.5))
    p.add_argument("--value-coef", type=float, default=cfg_get(cfg, "ppo.value_coef", 0.5))
    p.add_argument("--entropy-coef", type=float, default=cfg_get(cfg, "ppo.entropy_coef", 0.1))
    p.add_argument("--qr-kappa", type=float, default=cfg_get(cfg, "ppo.qr_kappa", 1.0))
    p.add_argument("--mpo-temperature", type=float, default=cfg_get(cfg, "ppo.mpo_temperature", 0.1),
                   help="η in the PAC/MPO E-step: q(a|s) ∝ π_old(a|s)·exp(Q̄(s,a)/η).")
    p.add_argument("--bc-alpha", type=float, default=cfg_get(cfg, "ppo.bc_alpha", 0.1),
                   help="BC blend in the PAC actor loss: 0=pure MPO, 1=pure BC.")
    p.add_argument("--target-update-period", type=int, default=cfg_get(cfg, "ppo.target_update_period", 100),
                   help="PAC target network: hard-copy θ→θ' every N optimizer steps (critic TD target + "
                        "E-step reference π_θ'). 0 disables (online bootstrap).")
    p.add_argument("--burn-in-iters", type=int, default=cfg_get(cfg, "ppo.burn_in_iters", 20),
                   help="Force the agent to wait (action=0) for the first N iters; train critic only "
                        "(actor frozen) to warm up value/representation on full episodes. 0 disables.")

    # ── PER buffer ──
    p.add_argument("--buffer-capacity", type=int, default=cfg_get(cfg, "ppo.buffer_capacity", 200))
    p.add_argument("--per-n-replay", type=int, default=cfg_get(cfg, "ppo.per_n_replay", 4))
    p.add_argument("--per-alpha", type=float, default=cfg_get(cfg, "ppo.per_alpha", 0.6))
    p.add_argument("--per-beta-start", type=float, default=cfg_get(cfg, "ppo.per_beta_start", 0.4))
    p.add_argument("--per-beta-end", type=float, default=cfg_get(cfg, "ppo.per_beta_end", 1.0))
    p.add_argument("--per-priority-clip", type=float, default=cfg_get(cfg, "ppo.per_priority_clip", 50.0))

    # ── I/O ──
    p.add_argument("--seed", type=int, default=cfg_get(cfg, "run.seed", 0))
    p.add_argument("--device", default=cfg_get(cfg, "run.device", None),
                   choices=[None, "cpu", "mps", "cuda"])
    p.add_argument("--checkpoint-dir",
                   default=cfg_get(cfg, "run.checkpoint_dir", os.path.join(_HERE, "checkpoints")))
    p.add_argument("--save-every", type=int, default=cfg_get(cfg, "run.save_every", 200))
    p.add_argument("--log-every", type=int, default=cfg_get(cfg, "run.log_every", 1))

    args = p.parse_args(argv)
    # frame-repeat: the model temporal embedding must cover the PHYSICAL episode length
    if args.frame_repeat > 1 or args.n_frames is not None:
        _nf = args.n_frames if args.n_frames is not None else 29
        args.seq_len = _nf * args.frame_repeat
        print(f"[frame-repeat] n_frames(logical)={_nf} x repeat={args.frame_repeat} "
              f"-> physical seq_len={args.seq_len}; change_frame={args.change_frame}")
    print_resolved_config(cfg, used_keys=[
        "run.init_mode", "run.checkpoint_path", "run.seed", "run.device",
        "run.checkpoint_dir", "run.save_every", "run.log_every",
        "ppo.iters", "ppo.episodes_per_iter", "ppo.seq_len",
        "model.patch_size", "model.patch_hidden", "model.d_model", "model.d_mem",
        "model.tx_heads", "model.tx_layers", "model.n_lstm",
        "model.conv_channels", "model.n_conv_layers", "model.conv_kernel",
        "model.rl.n_quantiles", "model.rl.n_actions", "model.rl.init_action_bias",
        "ppo.lr", "ppo.gamma", "ppo.n_epochs", "ppo.grad_clip",
        "ppo.value_coef", "ppo.entropy_coef", "ppo.qr_kappa",
        "ppo.mpo_temperature", "ppo.bc_alpha", "ppo.target_update_period", "ppo.burn_in_iters",
        "ppo.buffer_capacity", "ppo.per_n_replay", "ppo.per_alpha",
        "ppo.per_beta_start", "ppo.per_beta_end", "ppo.per_priority_clip",
    ])

    _set_seed(args.seed)
    device = _select_device(args.device)

    model_kwargs = dict(
        in_channels=3, image_h=50, image_w=50,
        patch_size=args.patch_size, patch_hidden=args.patch_hidden,
        d_model=args.d_model, d_mem=args.d_mem,
        tx_heads=args.tx_heads, tx_layers=args.tx_layers, n_lstm=args.n_lstm,
        conv_channels=args.conv_channels, n_conv_layers=args.n_conv_layers, conv_kernel=args.conv_kernel,
        n_actions=args.n_actions, n_quantiles=args.n_quantiles,
        init_action_bias=list(args.init_action_bias), seq_len=args.seq_len,
    )
    model = RViTPlusV5Part2Model(**model_kwargs).to(device)

    print(f"[diag] patch_size={args.patch_size} → n_tokens={model.n_tokens} "
          f"(raw patch {model.patch_embed.patch_dim} → MLP {args.patch_hidden} → d_model; "
          f"conv heads over H2 (B,{args.d_mem},{model.n_tokens}) → flat {model.actor_head.out.in_features})")
    print(f"[diag] d_model={args.d_model} d_mem={args.d_mem} tx[{args.tx_heads}h×{args.tx_layers}L] "
          f"+ {args.n_lstm}×LSTM → Conv1d head[{args.n_conv_layers}×{args.conv_channels}ch k{args.conv_kernel}]")
    print(f"[diag] actor init bias: {list(args.init_action_bias)}")
    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[diag] total params: {n_params:,}")

    # ── Checkpoint load ──
    if args.init_mode == "fresh":
        print("[init] init_mode=fresh — random init, checkpoint_path ignored")
    elif not args.checkpoint_path:
        print(f"[init] WARNING: init_mode={args.init_mode} but no checkpoint_path; random init")
    elif not os.path.exists(args.checkpoint_path):
        print(f"[init] WARNING: checkpoint_path '{args.checkpoint_path}' missing; random init")
    else:
        strict = (args.init_mode == "resume")
        info = load_checkpoint_weights(model, args.checkpoint_path, strict=strict, device=device)
        if strict:
            print(f"[init] RESUME (strict) from {args.checkpoint_path} "
                  f"(iter={info['ckpt_iter']}, {info['loaded']} tensors)")
        else:
            print(f"[init] WARM_START (partial) from {args.checkpoint_path}: "
                  f"{info['loaded']} restored, {info['n_random_init']} stayed random")

    # ── Env ──
    env_kwargs = {}
    if args.n_frames is not None:
        env_kwargs["n_frames"] = args.n_frames
    if args.frame_repeat > 1:
        env_kwargs["frame_repeat"] = args.frame_repeat
    if args.change_frame is not None:
        env_kwargs["min_change_time"] = args.change_frame
        env_kwargs["max_change_time"] = args.change_frame
    env = ChangeDetectionEnv(**env_kwargs)
    if env.T != args.seq_len:
        print(f"[setup] WARNING: env.T = {env.T} but --seq-len = {args.seq_len}.")

    # ── PPO/PAC config ──
    ppo_cfg = PPOConfig(
        lr=args.lr, n_epochs=args.n_epochs, grad_clip=args.grad_clip,
        value_coef=args.value_coef, entropy_coef=args.entropy_coef,
        qr_kappa=args.qr_kappa, gamma=args.gamma,
        mpo_temperature=args.mpo_temperature, bc_alpha=args.bc_alpha,
        target_update_period=args.target_update_period,
        burn_in_iters=args.burn_in_iters,
        buffer_capacity=args.buffer_capacity, per_n_replay=args.per_n_replay,
        per_alpha=args.per_alpha, per_beta_start=args.per_beta_start,
        per_beta_end=args.per_beta_end, per_priority_clip=args.per_priority_clip,
    )

    history = train(
        model=model, env=env, n_iterations=args.iters,
        episodes_per_iter=args.episodes_per_iter, cfg=ppo_cfg,
        device=device, log_every=args.log_every,
        checkpoint_dir=args.checkpoint_dir, save_every=args.save_every,
    )

    os.makedirs(args.checkpoint_dir, exist_ok=True)
    final_path = os.path.join(args.checkpoint_dir, "rvit_plus_v8_rl_final.pt")
    torch.save({"iter": args.iters - 1, "model_state_dict": model.state_dict(),
                "model_kwargs": model_kwargs}, final_path)
    print(f"[done] final checkpoint at {final_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
