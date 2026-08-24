#!/usr/bin/env python3
"""
PRISM training entry point.

Usage:
    python3 train.py
    python3 train.py --config config/prism_config.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import torch

# Make sibling modules importable when invoked from anywhere.
_BASE = os.path.dirname(os.path.abspath(__file__))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from env import ChangeDetectionEnv  # noqa: E402
from model import PrismModel  # noqa: E402
from ppo import PPOConfig, train  # noqa: E402


def _device() -> torch.device:
    """Pick the best available device (CUDA → MPS → CPU)."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _device_name(d: torch.device) -> str:
    if d.type == "cuda":
        return torch.cuda.get_device_name(d)
    if d.type == "mps":
        return "Apple Silicon (MPS)"
    return "CPU"


def load_config(path: str | None = None) -> dict:
    """Load JSON config; default to config/prism_config.json next to this file."""
    if path is None:
        path = os.path.join(_BASE, "config", "prism_config.json")
    with open(path, "r") as f:
        return json.load(f)


def build_model(cfg_model: dict, device: torch.device) -> PrismModel:
    # Optional list of per-action initial logit biases. If absent, defaults to None
    # (zero bias, near-uniform initial policy). For ChangeDetectionEnv we strongly
    # recommend [0.0, -4.0] to prevent the bootstrapping starvation described in
    # the proposal: σ(-4) ≈ 0.018 makes the terminate-action vanishingly likely
    # at init, so episodes survive long enough for any signal to land.
    init_action_logit_bias = cfg_model.get("init_action_logit_bias", None)
    if init_action_logit_bias is not None:
        init_action_logit_bias = [float(v) for v in init_action_logit_bias]

    model = PrismModel(
        in_channels=int(cfg_model.get("in_channels", 3)),
        image_h=int(cfg_model.get("image_h", 50)),
        image_w=int(cfg_model.get("image_w", 50)),
        feature_channels=int(cfg_model.get("feature_channels", 32)),
        memory_channels=int(cfg_model.get("memory_channels", 16)),
        n_actions=int(cfg_model.get("n_actions", 2)),
        inner_K=int(cfg_model.get("inner_K", 2)),
        inner_eps=float(cfg_model.get("inner_eps", 0.1)),
        actor_hidden=int(cfg_model.get("actor_hidden", 64)),
        critic_hidden=int(cfg_model.get("critic_hidden", 64)),
        decision_channels=int(cfg_model.get("decision_channels", 4)),
        decision_coarse_grid=int(cfg_model.get("decision_coarse_grid", 2)),
        init_action_logit_bias=init_action_logit_bias,
        pc_pixel_coef=float(cfg_model.get("pc_pixel_coef", 1.0)),
        pc_feature_coef=float(cfg_model.get("pc_feature_coef", 0.1)),
        pc_autoenc_coef=float(cfg_model.get("pc_autoenc_coef", 1.0)),
    ).to(device)
    return model


def build_env(cfg_env: dict) -> ChangeDetectionEnv:
    return ChangeDetectionEnv(
        theta=float(cfg_env.get("theta_start", 65.0)),
        noise_multiplier=float(cfg_env.get("noise_multiplier", 10.0)),
        min_change_time=int(cfg_env.get("min_change_time", 11)),
        max_change_time=int(cfg_env.get("max_change_time", 25)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train PRISM with recurrent PPO + L_PC.")
    parser.add_argument("--config", type=str, default=None, help="Path to JSON config")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    args = parser.parse_args()

    cfg = load_config(args.config)

    # Reproducibility.
    seed = int(cfg.get("run", {}).get("seed", args.seed))
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    device = _device()
    print(f"Using device: {device} ({_device_name(device)})")

    # Build env, model, ppo cfg.
    chkpt_dir = os.path.join(_BASE, cfg["run"].get("checkpoint_dir", "checkpoints"))
    os.makedirs(chkpt_dir, exist_ok=True)

    env = build_env(cfg["environment"])
    model = build_model(cfg["model"], device)

    # Optionally resume from the latest checkpoint.
    resume = bool(cfg["run"].get("resume_from_checkpoint", False))
    if resume:
        latest = os.path.join(chkpt_dir, "prism_latest.pt")
        if os.path.isfile(latest):
            ckpt = torch.load(latest, map_location=device)
            model.load_state_dict(ckpt["model_state_dict"])
            print(f"resume_from_checkpoint=true: loaded {latest} (iter {ckpt.get('iter', '?')})")
        else:
            print(f"resume_from_checkpoint=true: no checkpoint found at {latest}, starting from init.")
    else:
        print("resume_from_checkpoint=false: training from randomly initialized weights.")

    pcfg_d = cfg["training"]
    pcfg = PPOConfig(
        lr=float(pcfg_d.get("lr", 3e-4)),
        n_epochs=int(pcfg_d.get("n_epochs", 4)),
        clip_range=float(pcfg_d.get("clip_range", 0.2)),
        value_coef=float(pcfg_d.get("value_coef", 0.5)),
        entropy_coef=float(pcfg_d.get("entropy_coef", 0.01)),
        pc_coef=float(pcfg_d.get("pc_coef", 1.0)),
        slow_coef=float(pcfg_d.get("slow_coef", 0.0)),
        grad_clip=float(pcfg_d.get("grad_clip", 0.5)),
        gamma=float(pcfg_d.get("gamma", 0.95)),
        gae_lambda=float(pcfg_d.get("gae_lambda", 0.95)),
        bptt_truncation=int(pcfg_d.get("bptt_truncation", 16)),
        inner_K_warmup_iters=int(pcfg_d.get("inner_K_warmup_iters", 0)),
        pc_pretrain_iters=int(pcfg_d.get("pc_pretrain_iters", 0)),
    )

    # Print parameter budget.
    print("\nParameter budget:")
    for k, v in model.count_parameters().items():
        print(f"  {k:<10s} {v:>8,}")

    # Train.
    n_iters = int(cfg["run"].get("n_iterations", 1000))
    eps_per_iter = int(cfg["run"].get("episodes_per_iter", 8))

    print(
        f"\nTraining: {n_iters} iterations × {eps_per_iter} episodes/iter "
        f"= {n_iters * eps_per_iter} total episodes\n"
    )
    save_every = int(cfg["training"].get("save_interval_iterations", 500))
    history = train(
        model=model,
        env=env,
        n_iterations=n_iters,
        episodes_per_iter=eps_per_iter,
        cfg=pcfg,
        device=device,
        log_every=int(cfg["run"].get("log_every", 10)),
        checkpoint_dir=chkpt_dir,
        save_every=save_every,
    )

    # Final save (separate file so the latest periodic save is never clobbered).
    chkpt_path = os.path.join(chkpt_dir, "prism_final.pt")
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "iter": n_iters - 1,
            "config": cfg,
            "history_tail": history[-100:] if len(history) > 100 else history,
        },
        chkpt_path,
    )
    print(f"\nSaved final checkpoint to {chkpt_path}")


if __name__ == "__main__":
    main()
