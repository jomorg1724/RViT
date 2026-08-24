"""
Content-preserving trunk pretraining — memory → observation reconstruction.

Phase 1 (fixed objective). The temporal-JEPA pretrain proved CONTENT-BLIND: the memory
learned the task timeline, not the stimulus content, so cue/change were undecodable. This
script forces content retention by training a decoder to reconstruct each frame from the
H2 memory output (the same layer the RL actor/critic read):

    H2 (binary FSQ, + N(0, std) noise)  --decoder-->  reconstructed frame      (MSE vs true frame)

A decoder pressure means the only way to minimize loss is for H2 to actually retain the
cue (position/validity/colour) and the change (orientation step). Same denoising setup as
before: the noisy student memory must reconstruct the CLEAN observation.

Actor and critic heads stay frozen. No labels are used — reconstruction is self-supervised.
"""
from __future__ import annotations

import argparse
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
from train_rl import pick_device, resolve_patch_grid, seed_training_rngs  # noqa: E402


class ReconDecoder(nn.Module):
    """Decode a full colour frame from the flattened H2 memory output."""

    def __init__(self, d_mem: int, n_tokens: int = 4, image_size: int = 50):
        super().__init__()
        in_dim = n_tokens * d_mem
        out_dim = 3 * image_size * image_size
        self.image_size = image_size
        self.net = nn.Sequential(
            nn.Linear(in_dim, 1024), nn.GELU(),
            nn.Linear(1024, out_dim),
        )

    def forward(self, h2: torch.Tensor) -> torch.Tensor:
        # h2: (..., n_tokens, d_mem) -> (..., 3, H, W)
        h = h2.flatten(-2)
        return self.net(h).view(*h.shape[:-1], 3, self.image_size, self.image_size)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Memory->observation reconstruction pretraining")
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
    p.add_argument("--fsq-levels", type=int, default=2)
    p.add_argument("--n-actions", type=int, default=2)
    p.add_argument("--n-quantiles", type=int, default=5)
    p.add_argument("--init-action-bias", type=float, nargs=2, default=[0.0, -1.5])
    p.add_argument("--jepa-heads", type=int, default=4)
    p.add_argument("--jepa-proto-dim", type=int, default=256)
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

    decoder = ReconDecoder(d_mem=args.d_mem, n_tokens=model.n_tokens, image_size=image_size).to(device)

    optimizer = torch.optim.Adam(
        list(model.parameters()) + list(decoder.parameters()), lr=args.lr, eps=1e-5,
    )

    n_params = sum(p.numel() for p in model.parameters())
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[recon] task={args.task} cell={args.cell} fsq_levels={args.fsq_levels} "
          f"d_mem={args.d_mem} params={n_params:,} (trainable trunk {n_train:,}) device={device}")
    print(f"[recon] n_trials={args.n_trials} batch={args.batch_size} T={T} "
          f"memory_output_noise_std={args.memory_output_noise_std} lr={args.lr}")
    print(f"[recon] decoder: H2({model.n_tokens}x{args.d_mem}) -> {image_size}x{image_size}x3 MSE")

    ckpt_dir = args.checkpoint_dir or os.path.join(_HERE, "recon_pretrain_checkpoints")
    os.makedirs(ckpt_dir, exist_ok=True)
    metrics_path = os.path.join(ckpt_dir, "metrics.csv")
    fieldnames = ["step", "n_trials", "loss_recon", "elapsed_s"]
    with open(metrics_path, "w", newline="") as f:
        csv.writer(f).writerow(fieldnames)

    n_steps = (args.n_trials + args.batch_size - 1) // args.batch_size
    t_start = time.time()
    for step in range(n_steps):
        obs_list = []
        for _ in range(args.batch_size):
            env.reset()
            frames = [env.step(0)[0] for _ in range(T)]
            obs_list.append(np.stack(frames))  # (T, S, S, 3)
        obs = torch.from_numpy(np.stack(obs_list)).to(device, torch.float32)  # (B,T,S,S,3)

        out = model.forward_rl_sequence(obs, return_cell=True, inject_memory_noise=True)
        h2 = out["cell_seq"][:, :, 1]  # (B,T,4,d_mem) noisy binary H2
        recon = decoder(h2)            # (B,T,3,S,S)
        target = obs.permute(0, 1, 4, 2, 3).contiguous()  # (B,T,3,S,S)
        loss = F.mse_loss(recon, target)

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=args.grad_clip)
        torch.nn.utils.clip_grad_norm_(decoder.parameters(), max_norm=args.grad_clip)
        optimizer.step()

        row = dict(step=step, n_trials=(step + 1) * args.batch_size,
                   loss_recon=float(loss.detach().item()), elapsed_s=time.time() - t_start)
        with open(metrics_path, "a", newline="") as f:
            csv.writer(f).writerow([row[k] for k in fieldnames])

        if step % args.log_every == 0 or step == n_steps - 1:
            print(f"[recon {step}/{n_steps}] trials={(step + 1) * args.batch_size} "
                  f"loss={row['loss_recon']:.4f} ({row['elapsed_s']:.0f}s)")

        if (step + 1) % args.save_every == 0 or step == n_steps - 1:
            ckpt_path = os.path.join(ckpt_dir, "recon_pretrain_latest.pt")
            torch.save({
                "model_state_dict": model.state_dict(),
                "decoder_state_dict": decoder.state_dict(),
                "step": step,
                "n_trials": (step + 1) * args.batch_size,
                "model_kwargs": model_kwargs,
                "fsq_levels": args.fsq_levels,
                "memory_output_noise_std": args.memory_output_noise_std,
            }, ckpt_path)
            print(f"[recon] checkpoint saved: {ckpt_path}")

    print(f"[recon] DONE. total trials={n_steps * args.batch_size} "
          f"elapsed={time.time() - t_start:.0f}s; checkpoint in {ckpt_dir}")


if __name__ == "__main__":
    main()
