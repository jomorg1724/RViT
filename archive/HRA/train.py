"""
HRA training entry point.

Usage:
    cd /Users/jonathanmorgan/AttentionManuscript
    python3 HRA/train.py                              # default config + checkpoint dir
    python3 HRA/train.py --config HRA/config/hra_config.json --seed 42

The Stage 1 gate (MODEL_DESIGN.md §8): single-layer-equivalent HRA converges
on the Posner cued change-detection task with meaningful learning curves
(reward >> never-press baseline of 1.47), the policy entropy decreases, and
per-layer attention maps show structure aligned to cue location. The PRISM v1
reward profile is a reference but not a hard target.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from typing import Optional

import numpy as np
import torch

# Allow running this file as a script.
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from HRA.env import ChangeDetectionEnv
from HRA.model import HRAModel
from HRA.ppo import PPOConfig, train


def _select_device() -> torch.device:
    """Select CUDA → MPS → CPU."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def _set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _load_config(path: Optional[str]) -> dict:
    if path is None:
        path = os.path.join(_HERE, "config", "hra_config.json")
    with open(path) as f:
        return json.load(f)


def _soft_policy_reset(model: HRAModel, *,
                       actor_weight_scale: float = 0.1,
                       actor_bias: list[float] | None = None,
                       critic_weight_scale: float = 0.3) -> None:
    """
    Surgical intervention to recover from a collapsed policy.

    Used when resuming from a checkpoint where the actor has driven its logits
    to extreme values (|logit_wait − logit_press| >> 10) so that random
    sampling produces ~0 press probability, freezing exploration. This:

      * Scales `actor.fc2.weight` down by `actor_weight_scale` — preserves
        the *direction* the actor learned (which states correlate with which
        action) but compresses the logits back toward zero.
      * Sets `actor.fc2.bias` to `actor_bias` (e.g. [0.0, -2.0] for ~12 %
        press probability instead of [0.0, -4.0]'s 1.8 %).
      * Scales `critic.fc2.weight` down by `critic_weight_scale` — softens
        the critic's confident wrong-direction Q estimates so on-policy
        re-exploration can re-shape Q without fighting a strong prior.

    Backbone weights (stem, GridCell cells, FeedbackTransformer, decoders,
    DecisionReadout, actor.fc1) are *not* touched — those encode the slow,
    successful perceptual learning.
    """
    with torch.no_grad():
        model.actor.fc2.weight.mul_(actor_weight_scale)
        if actor_bias is not None:
            bias_t = torch.as_tensor(actor_bias, dtype=model.actor.fc2.bias.dtype,
                                     device=model.actor.fc2.bias.device)
            model.actor.fc2.bias.copy_(bias_t)
        if hasattr(model.critic, "fc2"):
            model.critic.fc2.weight.mul_(critic_weight_scale)
    print(f"[soft-policy-reset] actor.fc2.weight *= {actor_weight_scale}; "
          f"actor.fc2.bias = {model.actor.fc2.bias.detach().cpu().tolist()}; "
          f"critic.fc2.weight *= {critic_weight_scale}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Train HRA on the cued change-detection env.")
    parser.add_argument("--config", default=None, help="Path to a JSON config (defaults to HRA/config/hra_config.json).")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--iters", type=int, default=None, help="Override iteration count.")
    parser.add_argument("--episodes-per-iter", type=int, default=8)
    parser.add_argument("--checkpoint-dir", default=os.path.join(_HERE, "checkpoints"))
    parser.add_argument("--device", default=None, choices=[None, "cpu", "mps", "cuda"])
    parser.add_argument("--pc-pretrain-iters", type=int, default=0,
                        help="Number of iterations to run PC-only pretrain (force action=0). "
                             "Useful when the env is sparse-reward; PRISM v1 uses ~20–50 here.")

    # Resume + recovery flags.
    parser.add_argument("--resume", default=None,
                        help="Path to a checkpoint .pt to load before training. Continues from those weights.")
    parser.add_argument("--soft-policy-reset", action="store_true",
                        help="After --resume, apply soft policy reset (scale actor/critic fc2 weights, "
                             "reset actor.fc2.bias to --actor-bias). Use when policy has collapsed to "
                             "deterministic single-action. See _soft_policy_reset docstring.")
    parser.add_argument("--actor-bias", type=float, nargs="+", default=[0.0, -2.0],
                        help="If --soft-policy-reset, set actor.fc2.bias to this. Default [0.0, -2.0] "
                             "→ initial P(press) ≈ 0.12 (vs [0.0, -4.0]'s 0.018).")
    parser.add_argument("--actor-weight-scale", type=float, default=0.1)
    parser.add_argument("--critic-weight-scale", type=float, default=0.3)

    # PPO knob overrides.
    parser.add_argument("--entropy-coef", type=float, default=None,
                        help="Override entropy coefficient. Default from config (typically 0.01). "
                             "Raise to 0.03–0.05 to escape exploration collapse.")
    parser.add_argument("--gamma", type=float, default=None, help="Override discount factor.")
    parser.add_argument("--lr", type=float, default=None, help="Override learning rate.")

    # Checkpoint naming for the new run.
    parser.add_argument("--checkpoint-name", default="hra_latest.pt",
                        help="Filename to save checkpoints under (in --checkpoint-dir). Use a distinct "
                             "name when continuing from a previous run to avoid overwriting.")
    args = parser.parse_args(argv)

    _set_seed(args.seed)
    device = torch.device(args.device) if args.device else _select_device()
    print(f"[setup] device = {device}, seed = {args.seed}")

    cfg_json = _load_config(args.config)
    model_kwargs = {k: v for k, v in cfg_json.get("model", {}).items() if not k.startswith("_")}
    training_kwargs = {k: v for k, v in cfg_json.get("training", {}).items() if not k.startswith("_")}
    run_kwargs = {k: v for k, v in cfg_json.get("run", {}).items() if not k.startswith("_")}

    model = HRAModel(**model_kwargs).to(device)

    # --- Resume from checkpoint ---
    # Three sources, in priority order: explicit --resume CLI > config's
    # resume_from_checkpoint flag + default hra_latest.pt path > no resume.
    resume_path: str | None = args.resume
    if resume_path is None and run_kwargs.get("resume_from_checkpoint", False):
        default_resume = os.path.join(args.checkpoint_dir, "hra_latest.pt")
        if os.path.exists(default_resume):
            resume_path = default_resume
            print(f"[resume] config has resume_from_checkpoint=true; using {resume_path}")
        else:
            print(f"[resume] resume_from_checkpoint=true but {default_resume} not found — starting from scratch")

    if resume_path is not None:
        if not os.path.exists(resume_path):
            print(f"[resume] ERROR: checkpoint not found at {resume_path}")
            return 1
        state = torch.load(resume_path, map_location=device, weights_only=False)
        model.load_state_dict(state["model_state_dict"])
        prev_iter = state.get("iter", -1)
        print(f"[resume] loaded weights from {resume_path} (prev iter = {prev_iter})")
        if args.soft_policy_reset:
            _soft_policy_reset(
                model,
                actor_weight_scale=args.actor_weight_scale,
                actor_bias=list(args.actor_bias),
                critic_weight_scale=args.critic_weight_scale,
            )

    # --- PPO config (JSON-driven; CLI flags override) ---
    cfg = PPOConfig()
    # Read every field that maps onto PPOConfig from the JSON training block.
    for key in (
        "lr", "n_epochs", "clip_range", "value_coef", "entropy_coef",
        "pc_coef", "slow_coef", "grad_clip", "value_huber_kappa",
        "gamma", "gae_lambda", "bptt_truncation", "pc_pretrain_iters",
        "return_clip", "kl_early_stop", "actor_logit_clamp",
    ):
        if key in training_kwargs:
            setattr(cfg, key, training_kwargs[key])

    # CLI overrides — only if the user explicitly passed them.
    if args.lr is not None:
        cfg.lr = args.lr
    if args.entropy_coef is not None:
        cfg.entropy_coef = args.entropy_coef
    if args.gamma is not None:
        cfg.gamma = args.gamma
    # --pc-pretrain-iters: 0 is a valid value, so respect it only if the user
    # explicitly passed it. We detect this via argparse `default=0` not being
    # the same as the JSON value. If the user wants JSON's pretrain value,
    # they should NOT pass --pc-pretrain-iters; if they do, CLI wins.
    if "--pc-pretrain-iters" in (argv if argv is not None else sys.argv):
        cfg.pc_pretrain_iters = args.pc_pretrain_iters

    print(f"[cfg] lr={cfg.lr}, entropy_coef={cfg.entropy_coef}, value_coef={cfg.value_coef}, "
          f"gamma={cfg.gamma}, pc_pretrain_iters={cfg.pc_pretrain_iters}, "
          f"bptt_truncation={cfg.bptt_truncation}, n_epochs={cfg.n_epochs}")
    print(f"[cfg] stability: huber_kappa={cfg.value_huber_kappa}, return_clip={cfg.return_clip}, "
          f"kl_early_stop={cfg.kl_early_stop}, actor_logit_clamp={cfg.actor_logit_clamp}, "
          f"grad_clip={cfg.grad_clip}")

    env = ChangeDetectionEnv()

    # Resolve iteration count + episodes-per-iter: CLI > JSON > hard default.
    n_iterations = args.iters if args.iters is not None else run_kwargs.get("n_iterations", 1000)
    episodes_per_iter = args.episodes_per_iter if args.episodes_per_iter != 8 else run_kwargs.get("episodes_per_iter", 8)
    save_every = run_kwargs.get("save_every", 500)

    history = train(
        model=model,
        env=env,
        n_iterations=n_iterations,
        episodes_per_iter=episodes_per_iter,
        cfg=cfg,
        device=device,
        checkpoint_dir=args.checkpoint_dir,
        save_every=save_every,
    )

    # Always save the final state under the requested filename so it's there
    # even for short runs that don't trigger the save_every autosave.
    os.makedirs(args.checkpoint_dir, exist_ok=True)
    final_path = os.path.join(args.checkpoint_dir, args.checkpoint_name)
    from HRA.ppo import _model_kwargs_from
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "model_kwargs": _model_kwargs_from(model),
            "iter": len(history) - 1,
        },
        final_path,
    )
    print(f"[done] final checkpoint saved to {final_path}")
    print(f"[done] {len(history)} iterations completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
