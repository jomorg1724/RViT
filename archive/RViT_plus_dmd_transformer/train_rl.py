"""
Train the DMD-feature transformer.

    python RViT_plus_dmd_transformer/train_rl.py --device mps
    python RViT_plus_dmd_transformer/train_rl.py --iters 2 --device cpu
"""
from __future__ import annotations

import argparse
import glob
import os
import sys

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PAPER = os.path.join(os.path.dirname(_HERE), "RViT_plus_paper")
for p in (_PAPER, _HERE):
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)

from config.loader import cfg_get, load_checkpoint_weights, load_config  # noqa: E402
from envs import TASKS, make_env                                         # noqa: E402
from model import DMDTransformerModel                                    # noqa: E402
from ppo import PPOConfig, train                                         # noqa: E402


def pick_device(name: str) -> torch.device:
    if name in ("mps", "cuda", "cpu"):
        return torch.device(name)
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Train DMD-feature transformer")
    p.add_argument("--task", default="validity4", choices=sorted(TASKS))
    p.add_argument("--T", type=int, default=7)
    p.add_argument("--min-change-time", type=int, default=5)
    p.add_argument("--max-change-time", type=int, default=5)
    p.add_argument("--noise", type=float, default=5.0)
    p.add_argument("--config", default=os.path.join(_HERE, "config", "default.json"))
    p.add_argument("--init-mode", choices=["fresh", "warm_start", "resume"], default=None)
    p.add_argument("--checkpoint-path", default=None)
    p.add_argument("--checkpoint-dir", default=None)
    p.add_argument("--iters", type=int, default=None)
    p.add_argument("--episodes-per-iter", type=int, default=None)
    p.add_argument("--n-quantiles", type=int, default=None)
    p.add_argument("--lr", type=float, default=None)
    p.add_argument("--gamma", type=float, default=None)
    p.add_argument("--entropy-coef", type=float, default=None)
    p.add_argument("--ema-decay", type=float, default=None)
    p.add_argument("--buffer-capacity", type=int, default=None)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--device", default="")
    p.add_argument("--save-every", type=int, default=200)
    p.add_argument("--log-every", type=int, default=5)
    return p


def main() -> None:
    args = build_arg_parser().parse_args()
    cfg = load_config(args.config) if os.path.exists(args.config) else {}
    torch.manual_seed(args.seed)
    device = pick_device(args.device or cfg_get(cfg, "run.device", ""))

    env = make_env(args.task, T=args.T, min_change_time=args.min_change_time,
                   max_change_time=args.max_change_time, noise_multiplier=args.noise)
    seq_len = int(env.T)

    n_quantiles = args.n_quantiles if args.n_quantiles is not None \
        else int(cfg_get(cfg, "model.rl.n_quantiles", 5))
    init_action_bias = list(cfg_get(cfg, "model.rl.init_action_bias", [0.0, -1.5]))
    model_kwargs = dict(
        n_actions=2, n_quantiles=n_quantiles, init_action_bias=init_action_bias,
        seq_len=seq_len,
        d_model=int(cfg_get(cfg, "model.d_model", 128)),
        n_heads=int(cfg_get(cfg, "model.n_heads", 4)),
        n_layers=int(cfg_get(cfg, "model.n_layers", 2)),
    )
    model = DMDTransformerModel(**model_kwargs).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[dmd_transformer] task={args.task} tokens={model.n_tokens} "
          f"params={n_params:,} device={device}")

    ckpt_dir = (args.checkpoint_dir or cfg_get(cfg, "run.checkpoint_dir", "")
                or os.path.expanduser("~/rvit_plus_checkpoints/dmd_transformer"))
    os.makedirs(ckpt_dir, exist_ok=True)

    init_mode = args.init_mode or cfg_get(cfg, "run.init_mode", "fresh")
    if init_mode in ("warm_start", "resume"):
        ckpt_path = args.checkpoint_path or cfg_get(cfg, "run.checkpoint_path", "")
        if not ckpt_path:
            found = sorted(glob.glob(os.path.join(ckpt_dir, "*.pt")), key=os.path.getmtime, reverse=True)
            ckpt_path = found[0] if found else ""
        if not ckpt_path or not os.path.exists(ckpt_path):
            raise FileNotFoundError(f"init_mode={init_mode!r}, but no checkpoint found in {ckpt_dir}")
        info = load_checkpoint_weights(model, ckpt_path, strict=(init_mode == "resume"), device=device)
        print(f"[dmd_transformer] {init_mode} LOADED {ckpt_path}\n[dmd_transformer] -> {info}")
    else:
        print("[dmd_transformer] init_mode=fresh")

    g = lambda k, d: cfg_get(cfg, f"ppo.{k}", d)
    ppo_cfg = PPOConfig(
        lr=args.lr if args.lr is not None else float(g("lr", 3e-4)),
        gamma=args.gamma if args.gamma is not None else float(g("gamma", 0.95)),
        entropy_coef=args.entropy_coef if args.entropy_coef is not None else float(g("entropy_coef", 0.01)),
        mpo_temperature=float(g("mpo_temperature", 0.1)),
        bc_alpha=float(g("bc_alpha", 0.1)),
        value_coef=float(g("value_coef", 0.5)),
        qr_kappa=float(g("qr_kappa", 1.0)),
        burn_in_iters=int(g("burn_in_iters", 20)),
        target_update_period=int(g("target_update_period", 0)),
        ema_decay=args.ema_decay if args.ema_decay is not None else float(g("ema_decay", 0.0)),
        buffer_capacity=args.buffer_capacity if args.buffer_capacity is not None else int(g("buffer_capacity", 1000)),
        per_n_replay=int(g("per_n_replay", 4)),
        per_alpha=float(g("per_alpha", 0.6)),
        per_beta_start=float(g("per_beta_start", 0.4)),
        per_beta_end=float(g("per_beta_end", 1.0)),
        per_priority_clip=float(g("per_priority_clip", 50.0)),
        grad_value_clip=float(g("grad_value_clip", 1.0e6)),
    )
    iters = args.iters if args.iters is not None else int(g("iters", 18750))
    eps = args.episodes_per_iter if args.episodes_per_iter is not None else int(g("episodes_per_iter", 8))
    print(f"[dmd_transformer] {iters} iters x {eps} episodes/iter = {iters * eps:,} episodes")

    history = train(
        model=model, env=env, n_iterations=iters, episodes_per_iter=eps,
        cfg=ppo_cfg, device=device, log_every=args.log_every,
        checkpoint_dir=ckpt_dir, save_every=args.save_every,
    )
    final = os.path.join(ckpt_dir, f"rvit_dmd_transformer_{args.task}_final.pt")
    torch.save({"iter": iters, "model_state_dict": model.state_dict(),
                "model_kwargs": model_kwargs, "task": args.task}, final)
    print(f"[dmd_transformer] saved {final}; iters logged={len(history)}")


if __name__ == "__main__":
    main()
