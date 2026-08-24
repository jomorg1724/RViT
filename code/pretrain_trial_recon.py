"""
Whole-trial reconstruction pretraining — from each frame's softmax JEPA student output.

The previous objectives were too local: temporal JEPA is content-blind (timeline, not
stimulus), and current-frame→current-frame reconstruction only forces per-frame content.
This script forces the representation to be a TRIAL-LEVEL summary: for EVERY frame t, a
lightweight transformer+conv decoder reconstructs the ENTIRE T-frame trial from that
frame's softmax JEPA student output z_t = softmax(jepa_logits(memory_t)).

The decoder literally cannot see the future from an early frame, but the objective pushes
each frame's representation to encode the trial's generative structure — the cue, the
Gabors, and the change — so cue/change become decodable from the memory (Phase 2).

    z_t = softmax(JEPA_head(H1_t, H2_t))          # (2 layers x 4 tokens x 4 heads x 256)
    decoder(z_t)  ->  all T frames                 # MSE against the true trial, summed over t

Actor/critic stay frozen. Denoising: the noisy student memory must reconstruct the clean trial.
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


class TrialDecoder(nn.Module):
    """Reconstruct the whole T-frame trial from ONE frame's softmax JEPA output.

    A lightweight transformer: the single frame's projected output attends to T learned
    frame-slot queries; each slot then decodes (small conv upsample) to one frame.
    """

    def __init__(self, in_dim: int, n_frames: int = 7, image_size: int = 50,
                 recon_size: int = 25, d: int = 192):
        super().__init__()
        self.n_frames = n_frames
        self.image_size = recon_size
        self.project = nn.Linear(in_dim, d)
        self.slots = nn.Parameter(torch.empty(1, n_frames, d))
        nn.init.normal_(self.slots, std=0.02)
        self.attn = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=d, nhead=8, dim_feedforward=512,
                                       batch_first=True, dropout=0.0),
            num_layers=1,
        )
        self.fc = nn.Linear(d, 48 * 10 * 10)
        self.c1 = nn.Conv2d(48, 48, 3, padding=1)
        self.c2 = nn.Conv2d(48, 24, 3, padding=1)
        self.c3 = nn.Conv2d(24, 3, 3, padding=1)

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        # z: (B, in_dim) — a single frame's flattened softmax JEPA student output.
        B = z.shape[0]
        x = self.project(z).unsqueeze(1)                       # (B, 1, d)
        seq = torch.cat([x, self.slots.expand(B, -1, -1)], dim=1)  # (B, 1+T, d)
        out = self.attn(seq)[:, 1:]                            # (B, T, d)
        h = self.fc(out).view(B * self.n_frames, 48, 10, 10)
        h = F.interpolate(h, scale_factor=2, mode="bilinear", align_corners=False)  # 20
        h = F.gelu(self.c1(h))
        h = F.interpolate(h, size=(self.image_size, self.image_size), mode="bilinear",
                          align_corners=False)                 # recon_size
        h = F.gelu(self.c2(h))
        img = self.c3(h)                                       # (B*T, 3, S, S)
        return img.view(B, self.n_frames, 3, self.image_size, self.image_size)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Whole-trial reconstruction from softmax JEPA outputs")
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
    p.add_argument("--recon-size", type=int, default=25,
                   help="spatial resolution to reconstruct the trial at (target is downsampled "
                        "to this; content like cue/change is still visible).")
    p.add_argument("--change-weight", type=float, default=3.0,
                   help="multiplier on the reconstruction loss from POST-CHANGE source frames "
                        "(t >= min_change_time). The change is only observable there, so this "
                        "forces the change into the representation instead of diluting it 2/7.")
    p.add_argument("--n-trials", type=int, default=100000)
    p.add_argument("--batch-size", type=int, default=32)
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

    # in_dim = flattened softmax JEPA student output per frame: 2 layers x 4 tokens x H heads x P proto
    in_dim = 2 * model.n_tokens * args.jepa_heads * args.jepa_proto_dim
    decoder = TrialDecoder(in_dim=in_dim, n_frames=T, image_size=image_size,
                           recon_size=args.recon_size).to(device)

    optimizer = torch.optim.Adam(
        list(model.parameters()) + list(decoder.parameters()), lr=args.lr, eps=1e-5,
    )

    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[trial-recon] task={args.task} cell={args.cell} fsq_levels={args.fsq_levels} "
          f"d_mem={args.d_mem} trainable_trunk={n_train:,} decoder={sum(p.numel() for p in decoder.parameters()):,} "
          f"device={device}")
    print(f"[trial-recon] n_trials={args.n_trials} batch={args.batch_size} T={T} "
          f"memory_output_noise_std={args.memory_output_noise_std} lr={args.lr}")
    print(f"[trial-recon] decode: softmax JEPA output ({in_dim}) @ each frame t -> full {T}-frame trial")

    ckpt_dir = args.checkpoint_dir or os.path.join(_HERE, "trial_recon_checkpoints")
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
            obs_list.append(np.stack(frames))
        obs = torch.from_numpy(np.stack(obs_list)).to(device, torch.float32)  # (B,T,S,S,3)

        out = model.forward_rl_sequence(obs, return_cell=True, inject_memory_noise=True)
        z = model.jepa_logits(out["cell_seq"])           # (B,T,2,4,H,P) logits
        z = z.softmax(dim=-1).flatten(2)                 # (B,T, in_dim) softmax student outputs

        target = obs.permute(0, 1, 4, 2, 3).contiguous()  # (B,T,3,S,S)
        if args.recon_size != image_size:
            target = F.interpolate(
                target.view(-1, 3, image_size, image_size),
                size=(args.recon_size, args.recon_size),
                mode="bilinear", align_corners=False,
            ).view(args.batch_size, T, 3, args.recon_size, args.recon_size)

        loss = torch.zeros((), device=device)
        wsum = 0.0
        for t in range(T):
            w = args.change_weight if t >= args.min_change_time else 1.0
            recon = decoder(z[:, t])                     # (B,T,3,S,S) whole trial from frame t
            loss = loss + w * F.mse_loss(recon, target)
            wsum += w
        loss = loss / wsum

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
            print(f"[trial-recon {step}/{n_steps}] trials={(step + 1) * args.batch_size} "
                  f"loss={row['loss_recon']:.4f} ({row['elapsed_s']:.0f}s)")

        if (step + 1) % args.save_every == 0 or step == n_steps - 1:
            ckpt_path = os.path.join(ckpt_dir, "trial_recon_latest.pt")
            torch.save({
                "model_state_dict": model.state_dict(),
                "decoder_state_dict": decoder.state_dict(),
                "step": step,
                "n_trials": (step + 1) * args.batch_size,
                "model_kwargs": model_kwargs,
                "fsq_levels": args.fsq_levels,
                "memory_output_noise_std": args.memory_output_noise_std,
            }, ckpt_path)
            print(f"[trial-recon] checkpoint saved: {ckpt_path}")

    print(f"[trial-recon] DONE. total trials={n_steps * args.batch_size} "
          f"elapsed={time.time() - t_start:.0f}s; checkpoint in {ckpt_dir}")


if __name__ == "__main__":
    main()
