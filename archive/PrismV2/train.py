#!/usr/bin/env python3
"""
PRISM v2 training entry point.

Usage:
    cd /Users/jonathanmorgan/AttentionManuscript/PrismV2
    python3 train.py
    python3 train.py --config config/prism_v2_config.json --seed 0
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import torch

_BASE = os.path.dirname(os.path.abspath(__file__))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from env import ChangeDetectionEnv  # noqa: E402
from model import PrismV2Model  # noqa: E402
from ppo import PPOConfig, train  # noqa: E402


def _device() -> torch.device:
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
    if path is None:
        path = os.path.join(_BASE, "config", "prism_v2_config.json")
    with open(path, "r") as f:
        return json.load(f)


def build_model(cm: dict, device: torch.device) -> PrismV2Model:
    iab = cm.get("init_action_logit_bias", None)
    if iab is not None:
        iab = [float(v) for v in iab]
    model = PrismV2Model(
        in_channels=int(cm.get("in_channels", 3)),
        image_h=int(cm.get("image_h", 50)),
        image_w=int(cm.get("image_w", 50)),
        feature_channels_V1=int(cm.get("feature_channels_V1", 64)),
        feature_channels_V2=int(cm.get("feature_channels_V2", 128)),
        memory_channels_fast=int(cm.get("memory_channels_fast", 32)),
        memory_channels_slow=int(cm.get("memory_channels_slow", 64)),
        n_heads_fast=int(cm.get("n_heads_fast", 4)),
        n_heads_slow=int(cm.get("n_heads_slow", 4)),
        inner_K_fast=int(cm.get("inner_K_fast", 2)),
        inner_K_slow=int(cm.get("inner_K_slow", 4)),
        inner_eps=float(cm.get("inner_eps", 0.1)),
        update_gate_bias_fast=float(cm.get("update_gate_bias_fast", -1.0)),
        update_gate_bias_slow=float(cm.get("update_gate_bias_slow", -3.0)),
        decision_channels=int(cm.get("decision_channels", 8)),
        decision_coarse_grid_fast=int(cm.get("decision_coarse_grid_fast", 2)),
        actor_hidden=int(cm.get("actor_hidden", 128)),
        critic_hidden=int(cm.get("critic_hidden", 128)),
        n_quantiles=int(cm.get("n_quantiles", 51)),
        n_actions=int(cm.get("n_actions", 2)),
        init_action_logit_bias=iab,
        pc_pixel_coef=float(cm.get("pc_pixel_coef", 1.0)),
        pc_pixel_autoenc_coef=float(cm.get("pc_pixel_autoenc_coef", 1.0)),
        pc_pixel_grid_coef=float(cm.get("pc_pixel_grid_coef", 0.1)),
        pc_pixel_grid_autoenc_coef=float(cm.get("pc_pixel_grid_autoenc_coef", 0.1)),
        pc_V1_feat_coef=float(cm.get("pc_V1_feat_coef", 0.1)),
        pc_V2_feat_coef=float(cm.get("pc_V2_feat_coef", 0.5)),
        pc_V2_feat_autoenc_coef=float(cm.get("pc_V2_feat_autoenc_coef", 0.5)),
    ).to(device)
    return model


def build_env(env_cfg: dict) -> ChangeDetectionEnv:
    return ChangeDetectionEnv(
        theta=float(env_cfg.get("theta_start", 65.0)),
        noise_multiplier=float(env_cfg.get("noise_multiplier", 10.0)),
        min_change_time=int(env_cfg.get("min_change_time", 11)),
        max_change_time=int(env_cfg.get("max_change_time", 25)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train PRISM v2 with recurrent PPO + PC.")
    parser.add_argument("--config", type=str, default=None)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    cfg = load_config(args.config)
    seed = int(cfg.get("run", {}).get("seed", args.seed))
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    device = _device()
    print(f"Using device: {device} ({_device_name(device)})")

    chkpt_dir = os.path.join(_BASE, cfg["run"].get("checkpoint_dir", "checkpoints"))
    os.makedirs(chkpt_dir, exist_ok=True)

    env = build_env(cfg["environment"])
    model = build_model(cfg["model"], device)

    resume = bool(cfg["run"].get("resume_from_checkpoint", False))
    if resume:
        latest = os.path.join(chkpt_dir, "prism_v2_latest.pt")
        if os.path.isfile(latest):
            ckpt = torch.load(latest, map_location=device)
            model.load_state_dict(ckpt["model_state_dict"])
            print(f"resume_from_checkpoint=true: loaded {latest} (iter {ckpt.get('iter', '?')})")
        else:
            print(f"resume_from_checkpoint=true: no checkpoint at {latest}, starting from init.")
    else:
        print("resume_from_checkpoint=false: training from random init.")

    pcfg_d = cfg["training"]
    pcfg = PPOConfig(
        lr=float(pcfg_d.get("lr", 3e-4)),
        n_epochs=int(pcfg_d.get("n_epochs", 4)),
        clip_range=float(pcfg_d.get("clip_range", 0.2)),
        value_coef=float(pcfg_d.get("value_coef", 0.5)),
        entropy_coef=float(pcfg_d.get("entropy_coef", 0.005)),
        pc_coef=float(pcfg_d.get("pc_coef", 1.0)),
        slow_coef=float(pcfg_d.get("slow_coef", 0.0)),
        grad_clip=float(pcfg_d.get("grad_clip", 0.5)),
        gamma=float(pcfg_d.get("gamma", 0.95)),
        gae_lambda=float(pcfg_d.get("gae_lambda", 0.95)),
        bptt_truncation=int(pcfg_d.get("bptt_truncation", 16)),
        value_huber_kappa=float(pcfg_d.get("value_huber_kappa", 1.0)),
        inner_K_warmup_iters=int(pcfg_d.get("inner_K_warmup_iters", 0)),
        pc_pretrain_iters=int(pcfg_d.get("pc_pretrain_iters", 0)),
    )

    print("\nParameter budget:")
    for k, v in model.count_parameters().items():
        print(f"  {k:<18s} {v:>10,}")

    n_iters = int(cfg["run"].get("n_iterations", 1000))
    eps_per_iter = int(cfg["run"].get("episodes_per_iter", 8))
    save_every = int(cfg["training"].get("save_interval_iterations", 500))

    print(
        f"\nTraining: {n_iters} iterations × {eps_per_iter} episodes/iter "
        f"= {n_iters * eps_per_iter} total episodes\n"
    )

    history = train(
        model=model, env=env,
        n_iterations=n_iters, episodes_per_iter=eps_per_iter,
        cfg=pcfg, device=device,
        log_every=int(cfg["run"].get("log_every", 10)),
        checkpoint_dir=chkpt_dir, save_every=save_every,
    )

    chkpt_path = os.path.join(chkpt_dir, "prism_v2_final.pt")
    torch.save({
        "model_state_dict": model.state_dict(), "iter": n_iters - 1,
        "config": cfg, "history_tail": history[-100:] if len(history) > 100 else history,
    }, chkpt_path)
    print(f"\nSaved final checkpoint to {chkpt_path}")


if __name__ == "__main__":
    main()
