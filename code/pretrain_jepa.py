"""
JEPA-only trunk pretraining — Phase 1 of the "pretrain JEPA targets first" plan.

    python pretrain_jepa.py --n-trials 100000 --memory-output-noise-std 0.01

What it does:
  * Shows the trunk ~n_trials FULL-LENGTH VDA4 trials (always-wait policy -> complete
    7-frame episodes, so the cue at t=1 and the change at t=5 are always observed).
  * Does NOTHING with the actor/critic heads: they are frozen (requires_grad=False) and
    excluded from the optimizer.
  * Injects independent N(0, memory_output_noise_std) noise into the H1/H2 memory outputs
    of the STUDENT only; the EMA teacher stays clean, so the student learns a denoising
    temporal self-distillation objective (student@t predicts EMA-teacher@t+1).
  * Uses the exact JEPA objective from ppo.py: structured DINO cross-entropy + VICReg-style
    variance/covariance, DINO teacher-centering, and teacher EMA.

The saved checkpoint carries the trunk + JEPA-head weights (and the clean EMA teacher),
ready for Phase 2 (decode cues/changes from H1/H2) and Phase 3 (RL heads with tiny trunk lr).
"""
from __future__ import annotations

import argparse
import copy
import csv
import os
import time

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in __import__("sys").path:
    __import__("sys").path.insert(0, _HERE)

from envs import make_env, task_grid  # noqa: E402
from model import RViTPaperModel  # noqa: E402
from ppo import (  # noqa: E402
    masked_jepa_center,
    structured_jepa_loss,
    jepa_variance_covariance_loss,
)
from train_rl import pick_device, resolve_patch_grid, seed_training_rngs  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="JEPA-only trunk pretraining on the VDA4 stream")
    p.add_argument("--task", default="vda4")
    p.add_argument("--T", type=int, default=7)
    p.add_argument("--frame-repeat", type=int, default=1)
    p.add_argument("--min-change-time", type=int, default=5)
    p.add_argument("--max-change-time", type=int, default=5)
    p.add_argument("--noise", type=float, default=5.0, help="sensory orientation noise multiplier")
    p.add_argument("--patch-grid-rows", type=int, default=2)
    p.add_argument("--patch-grid-cols", type=int, default=2)
    p.add_argument("--cell", default="transformer_memory_2layer_softmax_modern")
    p.add_argument("--feedback", default="crossattn1")
    p.add_argument("--d-mem", type=int, default=128)
    p.add_argument("--mem-heads", type=int, default=4)
    p.add_argument("--conv-frontend", action="store_true")
    p.add_argument("--fsq-levels", type=int, default=2, help="1=softmax, 2=binary FSQ on H1/H2")
    p.add_argument("--n-actions", type=int, default=2)
    p.add_argument("--n-quantiles", type=int, default=5)
    p.add_argument("--init-action-bias", type=float, nargs=2, default=[0.0, -1.5])
    p.add_argument("--jepa-heads", type=int, default=4)
    p.add_argument("--jepa-proto-dim", type=int, default=256)
    p.add_argument("--jepa-tau-student", type=float, default=0.1)
    p.add_argument("--jepa-tau-teacher-start", type=float, default=0.03)
    p.add_argument("--jepa-tau-teacher-end", type=float, default=0.05)
    p.add_argument("--jepa-tau-warmup", type=int, default=300)
    p.add_argument("--jepa-center-momentum", type=float, default=0.9)
    p.add_argument("--jepa-ema-decay", type=float, default=0.996)
    p.add_argument("--jepa-sinkhorn-iters", type=int, default=3)
    p.add_argument("--jepa-var-coef", type=float, default=1.0)
    p.add_argument("--jepa-cov-coef", type=float, default=0.01)
    p.add_argument("--memory-output-noise-std", type=float, default=0.01)
    p.add_argument("--n-trials", type=int, default=100000)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=0.0003)
    p.add_argument("--grad-clip", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--device", default="cuda")
    p.add_argument("--save-every", type=int, default=250)
    p.add_argument("--checkpoint-dir", default=None)
    p.add_argument("--log-every", type=int, default=10)
    return p


def main() -> None:
    args = build_parser().parse_args()
    seed_training_rngs(args.seed)
    device = pick_device(args.device)

    env = make_env(
        args.task, T=args.T, frame_repeat=args.frame_repeat,
        min_change_time=args.min_change_time, max_change_time=args.max_change_time,
        noise_multiplier=args.noise, curriculum=False, theta=65.0,
    )
    T = int(env.T)
    grid_rows, grid_cols = resolve_patch_grid(args.task, args.patch_grid_rows, args.patch_grid_cols)
    image_size = int(env.S)

    model_kwargs = dict(
        n_actions=args.n_actions, n_quantiles=args.n_quantiles,
        init_action_bias=list(args.init_action_bias), seq_len=T,
        feedback=args.feedback, two_lstm=False, cell=args.cell, mem_heads=args.mem_heads,
        vae_in_channels=1, jepa_n_heads=args.jepa_heads, jepa_proto_dim=args.jepa_proto_dim,
        frame_repeat=args.frame_repeat, d_mem=args.d_mem, memory_decay=1.0, memory_noise_std=0.0,
        memory_output_noise_std=args.memory_output_noise_std,
        dual_actor_critic_streams=False, conv_frontend=args.conv_frontend,
        grid_rows=grid_rows, grid_cols=grid_cols, image_size=image_size,
    )
    model = RViTPaperModel(**model_kwargs).to(device)
    if args.fsq_levels >= 2:
        model.encoder.fsq_levels = args.fsq_levels

    # Freeze the actor/critic heads: Phase 1 does nothing with them.
    for p in model.actor_head.parameters():
        p.requires_grad_(False)
    for p in model.critic_head.parameters():
        p.requires_grad_(False)

    optimizer = torch.optim.Adam(
        [p for p in model.parameters() if p.requires_grad], lr=args.lr, eps=1e-5,
    )

    # EMA teacher (clean targets; not noised).
    jepa_teacher = copy.deepcopy(model)
    for p in jepa_teacher.parameters():
        p.requires_grad_(False)
    jepa_teacher.eval()

    n_params = sum(p.numel() for p in model.parameters())
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[pretrain] task={args.task} cell={args.cell} fsq_levels={args.fsq_levels} "
          f"d_mem={args.d_mem} params={n_params:,} (trainable {n_train:,}) device={device}")
    print(f"[pretrain] n_trials={args.n_trials} batch={args.batch_size} T={T} "
          f"memory_output_noise_std={args.memory_output_noise_std} lr={args.lr}")
    print(f"[pretrain] JEPA: temporal t->t+1, {args.jepa_heads} heads x {args.jepa_proto_dim} "
          f"per token, tau_s={args.jepa_tau_student}, tau_t={args.jepa_tau_teacher_start}->"
          f"{args.jepa_tau_teacher_end}, ema={args.jepa_ema_decay}, center={args.jepa_center_momentum}, "
          f"sinkhorn={args.jepa_sinkhorn_iters}, var={args.jepa_var_coef}, cov={args.jepa_cov_coef}")

    ckpt_dir = args.checkpoint_dir or os.path.join(_HERE, "jepa_pretrain_checkpoints")
    os.makedirs(ckpt_dir, exist_ok=True)
    metrics_path = os.path.join(ckpt_dir, "metrics.csv")
    fieldnames = [
        "step", "n_trials", "loss_jepa", "loss_jepa_ce", "loss_jepa_h1", "loss_jepa_h2",
        "loss_jepa_var", "loss_jepa_cov", "tau_teacher", "grad_norm", "teacher_student_h2_mse",
        "elapsed_s",
    ]
    with open(metrics_path, "w", newline="") as f:
        csv.writer(f).writerow(fieldnames)

    n_steps = (args.n_trials + args.batch_size - 1) // args.batch_size
    t_start = time.time()
    for step in range(n_steps):
        # Collect a batch of full-length trials (always-wait -> done only at t>=T).
        obs_list = []
        for _ in range(args.batch_size):
            env.reset()
            frames = []
            for _ in range(T):
                o, _r, _d, _i = env.step(0)
                frames.append(o)
            obs_list.append(np.stack(frames))  # (T, S, S, 3)
        obs = torch.from_numpy(np.stack(obs_list)).to(device, torch.float32)  # (B,T,S,S,3)

        # Clean EMA-teacher targets.
        jepa_teacher.eval()
        with torch.no_grad():
            jout = jepa_teacher.forward_rl_sequence(obs, return_cell=True)
            z_teacher = jepa_teacher.jepa_logits(jout["cell_seq"])  # (B,T,2,4,heads,proto)

        frac = min(float(step) / max(1, args.jepa_tau_warmup), 1.0)
        tau_t = args.jepa_tau_teacher_start + frac * (args.jepa_tau_teacher_end - args.jepa_tau_teacher_start)

        # Noisy student.
        out = model.forward_rl_sequence(obs, return_cell=True, inject_memory_noise=True)
        z_s = model.jepa_logits(out["cell_seq"])

        m = torch.ones(obs.shape[0], T, device=device)
        zt = z_teacher[:, 1:]
        zs = z_s[:, :-1]
        vmask = m[:, 1:] * m[:, :-1]

        ce, layer_losses = structured_jepa_loss(
            zt, zs, model.jepa_center, vmask,
            tau_teacher=tau_t, tau_student=args.jepa_tau_student,
            sinkhorn_iters=args.jepa_sinkhorn_iters,
        )
        student_features = model.jepa_features(out["cell_seq"])[:, :-1]
        var, cov = jepa_variance_covariance_loss(student_features, vmask)
        loss = ce + args.jepa_var_coef * var + args.jepa_cov_coef * cov

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=args.grad_clip)
        optimizer.step()

        # Teacher EMA + DINO center update.
        with torch.no_grad():
            dj = args.jepa_ema_decay
            for tp, p in zip(jepa_teacher.parameters(), model.parameters()):
                tp.data.mul_(dj).add_(p.data, alpha=1.0 - dj)
            batch_center = masked_jepa_center(z_teacher, m)
            model.jepa_center.mul_(args.jepa_center_momentum).add_(
                batch_center, alpha=1.0 - args.jepa_center_momentum)

        h1 = float(layer_losses[0].detach().item())
        h2 = float(layer_losses[1].detach().item()) if layer_losses.numel() > 1 else float("nan")
        with torch.no_grad():
            student_h2 = out["cell_seq"][:, :, 1]
            teacher_h2 = jout["cell_seq"][:, :, 1]
            h2_mse = torch.nn.functional.mse_loss(student_h2, teacher_h2).item()

        row = dict(
            step=step, n_trials=(step + 1) * args.batch_size,
            loss_jepa=float(loss.detach().item()), loss_jepa_ce=float(ce.detach().item()),
            loss_jepa_h1=h1, loss_jepa_h2=h2,
            loss_jepa_var=float(var.detach().item()), loss_jepa_cov=float(cov.detach().item()),
            tau_teacher=tau_t, grad_norm=float(grad_norm), teacher_student_h2_mse=h2_mse,
            elapsed_s=time.time() - t_start,
        )
        with open(metrics_path, "a", newline="") as f:
            csv.writer(f).writerow([row[k] for k in fieldnames])

        if step % args.log_every == 0 or step == n_steps - 1:
            print(f"[pretrain {step}/{n_steps}] trials={(step + 1) * args.batch_size} "
                  f"L_jepa={row['loss_jepa']:.4f} ce={row['loss_jepa_ce']:.4f} "
                  f"h1={h1:.3f} h2={h2:.3f} var={row['loss_jepa_var']:.3f} "
                  f"cov={row['loss_jepa_cov']:.4f} gnorm={row['grad_norm']:.2f} "
                  f"mse={h2_mse:.4f} tau_t={tau_t:.3f} ({row['elapsed_s']:.0f}s)")

        if (step + 1) % args.save_every == 0 or step == n_steps - 1:
            ckpt_path = os.path.join(ckpt_dir, "jepa_pretrain_latest.pt")
            torch.save({
                "model_state_dict": model.state_dict(),
                "jepa_teacher_state_dict": jepa_teacher.state_dict(),
                "jepa_center": model.jepa_center.detach().cpu(),
                "step": step,
                "n_trials": (step + 1) * args.batch_size,
                "model_kwargs": model_kwargs,
                "fsq_levels": args.fsq_levels,
                "memory_output_noise_std": args.memory_output_noise_std,
            }, ckpt_path)
            print(f"[pretrain] checkpoint saved: {ckpt_path}")

    print(f"[pretrain] DONE. total trials={(n_steps) * args.batch_size} "
          f"elapsed={time.time() - t_start:.0f}s; checkpoint in {ckpt_dir}")


if __name__ == "__main__":
    main()
