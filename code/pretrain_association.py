"""
Association-learning pretraining (no RL): make the memory naturally care about changes.

Three objectives, exactly as specified:
  1. JEPA temporal self-distillation on H1/H2          (KEPT, unchanged)
  2. Change report: H2 at TRIAL END -> change vs no-change (binary cross-entropy)
  3. Association: the third memory layer (Q=K=V=[H1,H2]) predicts the NEXT [H1_hat,H2_hat];
     trained by direct next-state MSE. A change is naturally a break in predictability.

The agent always waits (action=0), so every trial is observed in full. Actor and critic
heads are frozen and never touched. No reconstruction hacks — the learning emerges from
prediction + report.
"""
from __future__ import annotations

import argparse
import copy
import csv
import os
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in __import__("sys").path:
    __import__("sys").path.insert(0, _HERE)

from envs import make_env  # noqa: E402
from model import RViTPaperModel  # noqa: E402
from paper_heads import JEPAStructuredHead  # noqa: E402
from ppo import (  # noqa: E402
    masked_jepa_center,
    structured_jepa_loss,
    jepa_variance_covariance_loss,
)
from train_rl import pick_device, resolve_patch_grid, seed_training_rngs  # noqa: E402


class ChangeHead(nn.Module):
    """Report head: flattened H2 at trial end -> binary change vs no-change."""

    def __init__(self, d_mem: int, n_tokens: int = 4):
        super().__init__()
        self.fc = nn.Linear(n_tokens * d_mem, 2)

    def forward(self, h2_end: torch.Tensor) -> torch.Tensor:
        return self.fc(h2_end.flatten(-2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Association-learning pretraining (JEPA + change report + next-state prediction)")
    p.add_argument("--task", default="vda4")
    p.add_argument("--T", type=int, default=7)
    p.add_argument("--frame-repeat", type=int, default=1)
    p.add_argument("--min-change-time", type=int, default=5)
    p.add_argument("--max-change-time", type=int, default=5)
    p.add_argument("--noise", type=float, default=5.0)
    p.add_argument("--patch-grid-rows", type=int, default=2)
    p.add_argument("--patch-grid-cols", type=int, default=2)
    p.add_argument("--cell", default="transformer_memory_2layer_softmax_modern")
    p.add_argument("--feedback", default="crossattn1")
    p.add_argument("--d-mem", type=int, default=128)
    p.add_argument("--mem-heads", type=int, default=4)
    p.add_argument("--conv-frontend", action="store_true")
    p.add_argument("--fsq-levels", type=int, default=1,
                   help="memory nonlinearity: 1 = softmax (this phase, no binary collapse); >=2 = FSQ")
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
    p.add_argument("--no-center", action="store_true",
                   help="disable DINO teacher-centering (center is zeros, never updated); "
                        "prevents the center from canceling the distillation targets into uniformity")
    p.add_argument("--jepa-ema-decay", type=float, default=0.996)
    p.add_argument("--jepa-sinkhorn-iters", type=int, default=3)
    p.add_argument("--jepa-var-coef", type=float, default=1.0)
    p.add_argument("--jepa-cov-coef", type=float, default=0.01)
    p.add_argument("--mem-var-coef", type=float, default=1.0,
                   help="variance-floor penalty applied DIRECTLY to the raw (pre-nonlinearity, "
                        "noise-free) memory H1/H2 — prevents the input-blind constant-memory collapse")
    p.add_argument("--mem-cov-coef", type=float, default=0.01,
                   help="covariance-decorrelation penalty on the raw memory H1/H2")
    p.add_argument("--jepa-coef", type=float, default=0.1)
    p.add_argument("--change-coef", type=float, default=1.0)
    p.add_argument("--pred-coef", type=float, default=0.1,
                   help="weight on the predictive head's next-TEACHER-representation objective")
    p.add_argument("--memory-output-noise-std", type=float, default=0.01)
    p.add_argument("--n-trials", type=int, default=100000)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--lr", type=float, default=0.0003)
    p.add_argument("--grad-clip", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--device", default="cuda")
    p.add_argument("--save-every", type=int, default=250)
    p.add_argument("--checkpoint-dir", default=None)
    p.add_argument("--log-every", type=int, default=25)
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

    for p in model.actor_head.parameters():
        p.requires_grad_(False)
    for p in model.critic_head.parameters():
        p.requires_grad_(False)

    change_head = ChangeHead(d_mem=args.d_mem, n_tokens=model.n_tokens).to(device)
    # Predictive head's output projections: [H1_hat, H2_hat] -> JEPA prototype logits,
    # so the predictor learns to predict the NEXT TEACHER representation (one-hot-ish
    # under the low teacher temperature), not the raw next memory.
    pred_head1 = JEPAStructuredHead(d_mem=args.d_mem, n_heads=args.jepa_heads,
                                    proto_dim=args.jepa_proto_dim).to(device)
    pred_head2 = JEPAStructuredHead(d_mem=args.d_mem, n_heads=args.jepa_heads,
                                    proto_dim=args.jepa_proto_dim).to(device)

    optimizer = torch.optim.Adam(
        [p for p in model.parameters() if p.requires_grad]
        + list(change_head.parameters()) + list(pred_head1.parameters()) + list(pred_head2.parameters()),
        lr=args.lr, eps=1e-5,
    )

    jepa_teacher = copy.deepcopy(model)
    for p in jepa_teacher.parameters():
        p.requires_grad_(False)
    jepa_teacher.eval()

    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[assoc] task={args.task} cell={args.cell} fsq_levels={args.fsq_levels} d_mem={args.d_mem} "
          f"trainable={n_train:,} (actor/critic frozen) device={device}")
    print(f"[assoc] n_trials={args.n_trials} batch={args.batch_size} T={T} "
          f"memory_output_noise_std={args.memory_output_noise_std} lr={args.lr}")
    print(f"[assoc] objectives: JEPA({args.jepa_coef}) + change_report({args.change_coef}, H2@end -> 2-way) "
          f"+ next-state_prediction({args.pred_coef}, third layer [H1,H2]->[H1_hat,H2_hat])")

    ckpt_dir = args.checkpoint_dir or os.path.join(_HERE, "assoc_pretrain_checkpoints")
    os.makedirs(ckpt_dir, exist_ok=True)
    metrics_path = os.path.join(ckpt_dir, "metrics.csv")
    fieldnames = ["step", "n_trials", "loss_total", "loss_jepa_ce", "loss_jepa_var", "loss_jepa_cov",
                  "loss_change", "change_acc", "loss_pred", "loss_mem_var", "loss_mem_cov",
                  "grad_norm", "elapsed_s"]
    with open(metrics_path, "w", newline="") as f:
        csv.writer(f).writerow(fieldnames)

    ce_loss = nn.CrossEntropyLoss()
    n_steps = (args.n_trials + args.batch_size - 1) // args.batch_size
    t_start = time.time()
    for step in range(n_steps):
        obs_list, change_list = [], []
        for _ in range(args.batch_size):
            env.reset()
            change_list.append(int(env.change_true))
            frames = [env.step(0)[0] for _ in range(T)]
            obs_list.append(np.stack(frames))
        obs = torch.from_numpy(np.stack(obs_list)).to(device, torch.float32)
        change = torch.tensor(change_list, dtype=torch.long, device=device)

        # 1) JEPA teacher targets (clean).
        jepa_teacher.eval()
        with torch.no_grad():
            jout = jepa_teacher.forward_rl_sequence(obs, return_cell=True)
            z_teacher = jepa_teacher.jepa_logits(jout["cell_seq"])
        frac = min(float(step) / max(1, args.jepa_tau_warmup), 1.0)
        tau_t = args.jepa_tau_teacher_start + frac * (args.jepa_tau_teacher_end - args.jepa_tau_teacher_start)

        # 2) Student (noisy) + third-layer prediction.
        out = model.forward_rl_sequence(obs, return_cell=True, return_prediction=True,
                                        return_raw_memory=True, inject_memory_noise=True)
        cell = out["cell_seq"]                      # (B,T,2,4,d_mem)
        z_s = model.jepa_logits(cell)

        m = torch.ones(obs.shape[0], T, device=device)
        center = torch.zeros_like(model.jepa_center) if args.no_center else model.jepa_center
        ce, layer_losses = structured_jepa_loss(
            z_teacher[:, 1:], z_s[:, :-1], center, m[:, 1:] * m[:, :-1],
            tau_teacher=tau_t, tau_student=args.jepa_tau_student,
            sinkhorn_iters=args.jepa_sinkhorn_iters,
        )
        features = model.jepa_features(cell)[:, :-1]
        var, cov = jepa_variance_covariance_loss(features, m[:, 1:] * m[:, :-1])
        jepa_loss = ce + args.jepa_var_coef * var + args.jepa_cov_coef * cov

        # 3) Change report from H2 at the LAST timestep, with ALL earlier gradients
        #    DETACHED: the classifier objective only shapes the final forward pass.
        state_detached = (out["cell_seq"][:, T - 2, 0].detach(),
                          out["cell_seq"][:, T - 2, 1].detach())
        X_last = model.front(model._to_bchw(obs[:, T - 1]), (T - 1) // model.frame_repeat)
        _, H2_last, _ = model.encoder.forward_step(X_last, state_detached,
                                                   inject_memory_noise=True)
        logits = change_head(H2_last)
        change_loss = ce_loss(logits, change)
        with torch.no_grad():
            change_acc = float((logits.argmax(-1) == change).float().mean().item())

        # 4) Association: the predictive head predicts the NEXT TEACHER representation
        #    (one-hot-ish under the low teacher temperature), not the raw next memory.
        pred = out["prediction_seq"]                # (B,T,2,4,d_mem)
        z_pred = torch.stack([pred_head1(pred[:, :, 0]), pred_head2(pred[:, :, 1])], dim=2)
        pred_loss, _ = structured_jepa_loss(
            z_teacher[:, 1:], z_pred[:, :-1], center, m[:, 1:] * m[:, :-1],
            tau_teacher=tau_t, tau_student=args.jepa_tau_student,
            sinkhorn_iters=args.jepa_sinkhorn_iters,
        )

        loss = args.jepa_coef * jepa_loss + args.change_coef * change_loss + args.pred_coef * pred_loss

        # 5) Anti-collapse applied DIRECTLY to the memory: variance floor + covariance
        #    decorrelation on the RAW (pre-nonlinearity, noise-free) H1/H2. This is the
        #    real fix for the input-blind one-hot memory collapse — the noise cannot fake
        #    it because raw memory carries no injected noise.
        raw_mem = out["raw_memory_seq"]             # (B,T,2,4,d_mem) clean
        mem_var, mem_cov = jepa_variance_covariance_loss(raw_mem, m)
        loss = loss + args.mem_var_coef * mem_var + args.mem_cov_coef * mem_cov

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=args.grad_clip)
        torch.nn.utils.clip_grad_norm_(change_head.parameters(), max_norm=args.grad_clip)
        torch.nn.utils.clip_grad_norm_(pred_head1.parameters(), max_norm=args.grad_clip)
        torch.nn.utils.clip_grad_norm_(pred_head2.parameters(), max_norm=args.grad_clip)
        optimizer.step()

        # Teacher EMA + DINO center update.
        with torch.no_grad():
            dj = args.jepa_ema_decay
            for tp, p in zip(jepa_teacher.parameters(), model.parameters()):
                tp.data.mul_(dj).add_(p.data, alpha=1.0 - dj)
            if not args.no_center:
                batch_center = masked_jepa_center(z_teacher, m)
                model.jepa_center.mul_(args.jepa_center_momentum).add_(
                    batch_center, alpha=1.0 - args.jepa_center_momentum)

        row = dict(
            step=step, n_trials=(step + 1) * args.batch_size,
            loss_total=float(loss.detach().item()), loss_jepa_ce=float(ce.detach().item()),
            loss_jepa_var=float(var.detach().item()), loss_jepa_cov=float(cov.detach().item()),
            loss_change=float(change_loss.detach().item()), change_acc=change_acc,
            loss_pred=float(pred_loss.detach().item()),
            loss_mem_var=float(mem_var.detach().item()), loss_mem_cov=float(mem_cov.detach().item()),
            grad_norm=float(grad_norm),
            elapsed_s=time.time() - t_start,
        )
        with open(metrics_path, "a", newline="") as f:
            csv.writer(f).writerow([row[k] for k in fieldnames])

        if step % args.log_every == 0 or step == n_steps - 1:
            h1 = float(layer_losses[0].detach().item())
            h2 = float(layer_losses[1].detach().item()) if layer_losses.numel() > 1 else float("nan")
            print(f"[assoc {step}/{n_steps}] trials={(step + 1) * args.batch_size} "
                  f"jepa={row['loss_jepa_ce']:.3f} (h1={h1:.2f} h2={h2:.2f}) "
                  f"change={row['loss_change']:.3f} acc={row['change_acc']:.3f} "
                  f"pred={row['loss_pred']:.3f} mem_var={row['loss_mem_var']:.3f} "
                  f"mem_cov={row['loss_mem_cov']:.2f} gnorm={row['grad_norm']:.2f} ({row['elapsed_s']:.0f}s)")

        if (step + 1) % args.save_every == 0 or step == n_steps - 1:
            ckpt_path = os.path.join(ckpt_dir, "assoc_pretrain_latest.pt")
            torch.save({
                "model_state_dict": model.state_dict(),
                "jepa_teacher_state_dict": jepa_teacher.state_dict(),
                "change_head_state_dict": change_head.state_dict(),
                "step": step,
                "n_trials": (step + 1) * args.batch_size,
                "model_kwargs": model_kwargs,
                "fsq_levels": args.fsq_levels,
                "memory_output_noise_std": args.memory_output_noise_std,
            }, ckpt_path)
            print(f"[assoc] checkpoint saved: {ckpt_path}")

    print(f"[assoc] DONE. total trials={n_steps * args.batch_size} "
          f"elapsed={time.time() - t_start:.0f}s; checkpoint in {ckpt_dir}")


if __name__ == "__main__":
    main()
