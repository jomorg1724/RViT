"""Train KDA conv-memory + PAC/QR heads on Luo–Maunsell 2015 (sensitivity).

Scientific contract (held fixed from the last Luo campaign):
  task            luo2015_sensitivity
  timeline        T=7 (sample 0-1, delay 2, first test 3-4, gap 5, second test 6)
  locations       logical {0, 3} = S1 top-left / S4 bottom-right; no visual cue
  orientations    iid U[0°, 180°); signed Δ ~ U(-θ, θ)
  curriculum      shrinking θ: start 65°, −3° when ≥85% over a non-overlapping
                  1,000 valid-SDT-trial window, floor 8°
  condition       --high-loc {0,3} written through to checkpoint training_args
  criterion cells are NOT launched (sensitivity variants only)

Changed vs the Aug-18 dual-stream RViT agent: the recurrent backbone is the
KDA conv-memory model (same architecture as the VDA16/motion KDA runs).
"""
from __future__ import annotations

import argparse
import os
import random
import sys

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from envs import make_env, task_grid  # noqa: E402
from kda_rl_model import KDALuoRLModel  # noqa: E402
from ppo import PPOConfig, train  # noqa: E402


def pick_device(name: str) -> torch.device:
    if name in ("mps", "cuda", "cpu"):
        return torch.device(name)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def seed_training_rngs(seed: int) -> None:
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="KDA Luo–Maunsell 2015 sensitivity trainer")
    p.add_argument("--task", default="luo2015_sensitivity",
                   choices=["luo2015_sensitivity", "luo2015_criterion"])
    p.add_argument("--curriculum", action="store_true",
                   help="enable shrinking-θ (required for the Luo contract unless explicitly withheld)")
    p.add_argument("--theta-start", type=float, default=65.0)
    p.add_argument("--curr-window", type=int, default=1000)
    p.add_argument("--curr-threshold", type=float, default=0.85)
    p.add_argument("--curr-step", type=float, default=3.0)
    p.add_argument("--curr-floor", type=float, default=8.0)
    p.add_argument("--T", type=int, default=7)
    p.add_argument("--frame-repeat", type=int, default=1)
    p.add_argument("--noise", type=float, default=5.0)
    p.add_argument("--high-loc", type=int, required=True, choices=[0, 3],
                   help="counterphased high-value location; persisted as training_args.high_loc")
    p.add_argument("--high-reward", type=float, default=5.0)
    p.add_argument("--low-reward", type=float, default=1.0)
    p.add_argument("--reward-scale", type=float, default=1.0)
    p.add_argument("--n-channels", type=int, default=64)
    p.add_argument("--map-size", type=int, default=16)
    p.add_argument("--proto-dim", type=int, default=256)
    p.add_argument("--memory-noise-std", type=float, default=0.05,
                   help="H1 mnemonic noise; zero-noise Luo is not an informative diagnostic")
    p.add_argument("--mem-every", type=int, default=1)
    p.add_argument("--accum-mode", default="kda", choices=["ema", "gated", "kda"])
    p.add_argument("--accum-decay", type=float, default=0.5)
    p.add_argument("--kda-heads", type=int, default=4)
    p.add_argument("--kda-head-dim", type=int, default=16)
    p.add_argument("--n-actions", type=int, default=2)
    p.add_argument("--n-quantiles", type=int, default=5)
    p.add_argument("--init-action-bias", type=float, nargs=2, default=[0.0, -1.5])
    p.add_argument("--iters", type=int, default=19999)
    p.add_argument("--episodes-per-iter", type=int, default=8)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--actor-coef", type=float, default=0.5)
    p.add_argument("--value-coef", type=float, default=1.0)
    p.add_argument("--jepa-coef", type=float, default=0.01)
    p.add_argument("--entropy-coef", type=float, default=0.1)
    p.add_argument("--bc-alpha", type=float, default=0.0)
    p.add_argument("--jepa-ema-decay", type=float, default=0.996)
    p.add_argument("--jepa-tau-student", type=float, default=0.1)
    p.add_argument("--jepa-tau-teacher-start", type=float, default=0.03)
    p.add_argument("--jepa-tau-teacher-end", type=float, default=0.05)
    p.add_argument("--jepa-tau-warmup", type=int, default=300)
    p.add_argument("--jepa-center-momentum", type=float, default=0.9)
    p.add_argument("--jepa-var-coef", type=float, default=1.0)
    p.add_argument("--jepa-cov-coef", type=float, default=0.01)
    p.add_argument("--jepa-sinkhorn-iters", type=int, default=3)
    p.add_argument("--burn-in-iters", type=int, default=20)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--device", default="")
    p.add_argument("--checkpoint-dir", default=None)
    p.add_argument("--save-every", type=int, default=200)
    p.add_argument("--log-every", type=int, default=5)
    p.add_argument("--dry-run", action="store_true",
                   help="print the frozen contract and exit (no env/model/training)")
    return p


def main() -> None:
    args = build_arg_parser().parse_args()
    if args.task != "luo2015_sensitivity":
        raise SystemExit(
            "criterion cells are out of scope; pass --task luo2015_sensitivity"
        )
    if not args.curriculum:
        raise SystemExit(
            "Luo contract is shrinking-θ; pass --curriculum "
            "(fixed θ requires explicit user authorization)"
        )

    print("[kda-luo] contract:")
    print(f"  task={args.task}  high_loc={args.high_loc}  T={args.T}  seed={args.seed}")
    print(f"  curriculum ON: θ {args.theta_start}→{args.curr_floor}  "
          f"window={args.curr_window}  bar={args.curr_threshold}  step=-{args.curr_step}")
    print(f"  accum={args.accum_mode} {args.kda_heads}x{args.kda_head_dim}  "
          f"C={args.n_channels}  map={args.map_size}  mem_every={args.mem_every}  "
          f"σ_mem={args.memory_noise_std}")
    print(f"  objectives: critic={args.value_coef}  actor={args.actor_coef}  "
          f"JEPA={args.jepa_coef}  BC={args.bc_alpha}  teacher EMA={args.jepa_ema_decay}")
    print(f"  grid={task_grid(args.task)}  sensory noise={args.noise}")
    if args.dry_run:
        print("[kda-luo] dry-run: exiting before env/model construction")
        return

    seed_training_rngs(args.seed)
    device = pick_device(args.device)
    env = make_env(
        args.task,
        T=args.T,
        frame_repeat=args.frame_repeat,
        noise_multiplier=args.noise,
        reward_scale=args.reward_scale,
        curriculum=True,
        theta=args.theta_start,
        curr_window=args.curr_window,
        curr_threshold=args.curr_threshold,
        curr_step=args.curr_step,
        theta_floor=args.curr_floor,
        high_loc=args.high_loc,
        high_reward=args.high_reward,
        low_reward=args.low_reward,
    )
    print(f"[luo] high_loc={env.high_loc}  reward_table={env.reward_table}  S={env.S}")

    model = KDALuoRLModel(
        n_actions=args.n_actions,
        n_quantiles=args.n_quantiles,
        seq_len=int(env.T),
        init_action_bias=list(args.init_action_bias),
        n_channels=args.n_channels,
        map_size=args.map_size,
        proto_dim=args.proto_dim,
        memory_noise_std=args.memory_noise_std,
        mem_every=args.mem_every,
        accum_mode=args.accum_mode,
        accum_decay=args.accum_decay,
        kda_heads=args.kda_heads,
        kda_head_dim=args.kda_head_dim,
    ).to(device)

    cfg = PPOConfig(
        lr=args.lr,
        actor_coef=args.actor_coef,
        value_coef=args.value_coef,
        entropy_coef=args.entropy_coef,
        bc_alpha=args.bc_alpha,
        jepa_coef=args.jepa_coef,
        jepa_ema_decay=args.jepa_ema_decay,
        jepa_tau_student=args.jepa_tau_student,
        jepa_tau_teacher_start=args.jepa_tau_teacher_start,
        jepa_tau_teacher_end=args.jepa_tau_teacher_end,
        jepa_tau_teacher_warmup_iters=args.jepa_tau_warmup,
        jepa_center_momentum=args.jepa_center_momentum,
        jepa_var_coef=args.jepa_var_coef,
        jepa_cov_coef=args.jepa_cov_coef,
        jepa_sinkhorn_iters=args.jepa_sinkhorn_iters,
        burn_in_iters=args.burn_in_iters,
    )

    ckpt_dir = args.checkpoint_dir or os.path.join(
        _HERE, "runs", f"luo2015_kda_c{args.n_channels}_loc{args.high_loc}_seed{args.seed}",
        "checkpoints",
    )
    os.makedirs(ckpt_dir, exist_ok=True)
    metadata = {
        "training_args": {
            "task": args.task,
            "high_loc": int(args.high_loc),
            "accum_mode": args.accum_mode,
            "kda_heads": args.kda_heads,
            "kda_head_dim": args.kda_head_dim,
            "n_channels": args.n_channels,
            "map_size": args.map_size,
            "memory_noise_std": args.memory_noise_std,
            "mem_every": args.mem_every,
            "theta_start": args.theta_start,
            "seed": args.seed,
            "curriculum": True,
        }
    }
    train(
        model, env,
        n_iterations=args.iters,
        episodes_per_iter=args.episodes_per_iter,
        cfg=cfg,
        device=device,
        log_every=args.log_every,
        checkpoint_dir=ckpt_dir,
        save_every=args.save_every,
        checkpoint_metadata=metadata,
    )


if __name__ == "__main__":
    main()
