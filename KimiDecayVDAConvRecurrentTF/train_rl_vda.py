"""Train KDA conv-memory + PAC/QR heads on VDA16 (wait/declare).

Scientific contract:
  task            vda16 (4x4, 100x100, cue + change at t=5)
  timeline        T=7
  curriculum      shrinking θ 65°→8°, −3° at ≥85% / 1000-trial window
  heads           PAC actor + QR distributional critic (same harness as Luo)
  buffer          PER, same ppo.py replay
  budget          250_000 episodes = 31_250 iters × 8
  width           C=128, KDA 4×32 (VDA, not Luo C=64)
  from scratch    (does not load the killed supervised KDA weights)
"""
from __future__ import annotations

import argparse
import os
import sys

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from envs import make_env, task_grid  # noqa: E402
from kda_rl_model import KDARLModel  # noqa: E402
from ppo import PPOConfig, train  # noqa: E402
from train_rl import pick_device, seed_training_rngs  # noqa: E402


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="KDA VDA16 PAC/QR trainer")
    p.add_argument("--task", default="vda16", choices=["vda16"])
    p.add_argument("--curriculum", action="store_true")
    p.add_argument("--theta-start", type=float, default=65.0)
    p.add_argument("--curr-window", type=int, default=1000)
    p.add_argument("--curr-threshold", type=float, default=0.85)
    p.add_argument("--curr-step", type=float, default=3.0)
    p.add_argument("--curr-floor", type=float, default=8.0)
    p.add_argument("--T", type=int, default=7)
    p.add_argument("--frame-repeat", type=int, default=1)
    p.add_argument("--noise", type=float, default=5.0)
    p.add_argument("--n-channels", type=int, default=128)
    p.add_argument("--map-size", type=int, default=16)
    p.add_argument("--proto-dim", type=int, default=256)
    p.add_argument("--memory-noise-std", type=float, default=0.05)
    p.add_argument("--mem-every", type=int, default=1)
    p.add_argument("--accum-mode", default="kda", choices=["ema", "gated", "kda"])
    p.add_argument("--accum-decay", type=float, default=0.5)
    p.add_argument("--kda-heads", type=int, default=4)
    p.add_argument("--kda-head-dim", type=int, default=32)
    p.add_argument("--attn-mode", choices=["pixel_gate", "token"], default="pixel_gate")
    p.add_argument("--n-actions", type=int, default=2)
    p.add_argument("--n-quantiles", type=int, default=5)
    p.add_argument("--init-action-bias", type=float, nargs=2, default=[0.0, -1.5])
    p.add_argument("--iters", type=int, default=31250)
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
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--resume", default=None,
                   help="path to rvit_plus_rl_latest.pt; continue from checkpoint iter+1")
    return p


def main() -> None:
    args = build_arg_parser().parse_args()
    if not args.curriculum:
        raise SystemExit("VDA RL contract is shrinking-θ; pass --curriculum")
    n_ep = args.iters * args.episodes_per_iter
    print("[kda-vda-rl] contract:")
    print(f"  task={args.task}  T={args.T}  seed={args.seed}  episodes={n_ep}")
    print(f"  curriculum ON: θ {args.theta_start}→{args.curr_floor}  "
          f"window={args.curr_window}  bar={args.curr_threshold}  step=-{args.curr_step}")
    print(f"  accum={args.accum_mode} {args.kda_heads}x{args.kda_head_dim}  "
          f"C={args.n_channels}  map={args.map_size}  mem_every={args.mem_every}  "
          f"σ_mem={args.memory_noise_std}  attn={args.attn_mode}")
    print(f"  objectives: critic={args.value_coef}  actor={args.actor_coef}  "
          f"JEPA={args.jepa_coef}  BC={args.bc_alpha}  teacher EMA={args.jepa_ema_decay}")
    print(f"  grid={task_grid(args.task)}  sensory noise={args.noise}  "
          f"iters={args.iters} × {args.episodes_per_iter} eps")
    if args.dry_run:
        print("[kda-vda-rl] dry-run: exiting before env/model construction")
        return

    seed_training_rngs(args.seed)
    device = pick_device(args.device)
    env = make_env(
        args.task,
        T=args.T,
        frame_repeat=args.frame_repeat,
        noise_multiplier=args.noise,
        curriculum=True,
        theta=args.theta_start,
        curr_window=args.curr_window,
        curr_threshold=args.curr_threshold,
        curr_step=args.curr_step,
        theta_floor=args.curr_floor,
        min_change_time=5,
        max_change_time=5,
    )
    print(f"[vda-rl] S={getattr(env, 'S', getattr(env, 'image_size', None))}  "
          f"n_stim={env.n_stim}  device={device}")

    model = KDARLModel(
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
        attn_mode=args.attn_mode,
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
        _HERE, "runs", f"vda16_kda_rl_c{args.n_channels}_seed{args.seed}", "checkpoints",
    )
    os.makedirs(ckpt_dir, exist_ok=True)
    metadata = {
        "training_args": {
            "task": args.task,
            "accum_mode": args.accum_mode,
            "kda_heads": args.kda_heads,
            "kda_head_dim": args.kda_head_dim,
            "n_channels": args.n_channels,
            "map_size": args.map_size,
            "memory_noise_std": args.memory_noise_std,
            "mem_every": args.mem_every,
            "attn_mode": args.attn_mode,
            "theta_start": args.theta_start,
            "seed": args.seed,
            "curriculum": True,
            "iters": args.iters,
            "episodes_per_iter": args.episodes_per_iter,
        }
    }
    resume_ckpt = None
    start_iteration = 0
    n_iterations = args.iters
    schedule_final = args.iters - 1
    if args.resume:
        resume_ckpt = torch.load(args.resume, map_location="cpu", weights_only=False)
        last = int(resume_ckpt["iter"])
        start_iteration = last + 1
        n_iterations = args.iters - start_iteration
        if n_iterations <= 0:
            raise SystemExit(f"checkpoint iter {last} already at/past planned {args.iters}")
        print(f"[kda-vda-rl] RESUME from {args.resume} iter={last} "
              f"-> start={start_iteration} remaining={n_iterations} "
              f"(schedule_final={schedule_final}); replay buffer starts empty")
    train(
        model, env,
        n_iterations=n_iterations,
        episodes_per_iter=args.episodes_per_iter,
        cfg=cfg,
        device=device,
        log_every=args.log_every,
        checkpoint_dir=ckpt_dir,
        save_every=args.save_every,
        checkpoint_metadata=metadata,
        start_iteration=start_iteration,
        schedule_final_iteration=schedule_final,
        resume_checkpoint=resume_ckpt,
    )


if __name__ == "__main__":
    main()
