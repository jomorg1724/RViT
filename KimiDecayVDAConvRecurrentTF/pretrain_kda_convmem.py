"""
Training the KDA visual-accumulator conv recurrent transformer on VDA16
(4x4 grid, 16 Gabors, 100x100 px frames).

Identical objectives and training scheme to the conv-memory trainer
(pretrain_conv_memory.py in the motion-dmc experiment):

  1. JEPA temporal self-distillation on the per-step representation R (ONE per-pixel
     head: map x map prototype CE targets per frame). Student@t predicts the
     EMA-teacher@t+1 one-hot-ish targets; DINO centering kept; teacher EMA + tau
     schedule + Sinkhorn balancing as before.
  2. Change classifier: global-mean-pool R at the LAST timestep -> 2 logits, CE vs the
     change label, with gradients flowing ALL the way back through the recurrence.
  3. Anti-collapse (as before): variance floor + covariance decorrelation on the JEPA
     projection features.

Training scheme: collect a FRESH training set of `collection-size` trials, then train
`epochs` epochs over it (shuffled minibatches of `batch-size`), then collect a fresh
set again. Teacher EMA and DINO-centre updates happen after every optimizer step.

The only new flags select the visual accumulator:
  --accum-mode {ema,gated,kda}   (default kda)
  --accum-decay                  init decay for the accumulator gates (default 0.5)
  --kda-heads / --kda-head-dim   KDA state geometry; heads*head_dim must == n-channels

DO NOT RUN YET — smoke test and RunPod launch come later.
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

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in __import__("sys").path:
    __import__("sys").path.insert(0, _HERE)

from kda_conv_memory_model import KDAConvMemoryModel  # noqa: E402
from envs import make_env  # noqa: E402
from ppo import (  # noqa: E402
    masked_jepa_center,
    structured_jepa_loss,
    jepa_variance_covariance_loss,
)
from train_rl import pick_device, seed_training_rngs  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="KDA conv-memory JEPA + change classifier training (VDA16)")
    p.add_argument("--task", default="vda16")
    p.add_argument("--label", choices=["change", "valid"], default="change",
                   help="classifier target: 'change' = any change anywhere (vda default); "
                        "'valid' = REPORTABLE change at the cued location (go/no-go tasks)")
    p.add_argument("--amp", action="store_true",
                   help="mixed precision: autocast the recurrent forward (fp16) + GradScaler; "
                        "JEPA heads/losses stay fp32. The KDA state update itself is fp32 "
                        "regardless (precision-sensitive recurrence)")
    p.add_argument("--T", type=int, default=7)
    p.add_argument("--frame-repeat", type=int, default=1)
    p.add_argument("--frame-window", type=int, default=1,
                   help="frames per agent step, stacked as input channels (default 1 = original)")
    p.add_argument("--frame-stride", type=int, default=1,
                   help="frames advanced per agent step (default 1 = original)")
    p.add_argument("--mem-every", type=int, default=1,
                   help="run the memory block (H1/H2 update) every N agent steps (default 1); "
                        "the visual accumulator updates every step regardless")
    p.add_argument("--accum-mode", choices=["ema", "gated", "kda"], default="kda",
                   help="visual accumulator variant: ema = static per-channel EMA (the "
                        "in-flight baseline); gated = dynamic decay field + decoupled write "
                        "(vector state); kda = gated delta-rule matrix state per pixel")
    p.add_argument("--accum-decay", type=float, default=0.5,
                   help="initial accumulator decay (gate bias init; all modes start life "
                        "as the static EMA with this decay)")
    p.add_argument("--kda-heads", type=int, default=4)
    p.add_argument("--kda-head-dim", type=int, default=32,
                   help="KDA key/value head dim; heads*head_dim must equal --n-channels")
    p.add_argument("--attn-mode", choices=["pixel_gate", "token"], default="pixel_gate",
                   help="pixel_gate: per-pixel channel inner-product 2-way softmax. "
                        "token: flatten to (HW,C), QK^T over space, softmax over both "
                        "streams' keys, reshape back for conv residual.")
    p.add_argument("--min-change-time", type=int, default=5)
    p.add_argument("--max-change-time", type=int, default=5)
    p.add_argument("--noise", type=float, default=5.0)
    p.add_argument("--n-channels", type=int, default=128)
    p.add_argument("--map-size", type=int, default=16,
                   help="accumulator/memory map resolution; 16 = 4x4 px per VDA16 cell")
    p.add_argument("--proto-dim", type=int, default=256)
    p.add_argument("--memory-noise-std", type=float, default=0.05,
                   help="std of Gaussian noise added to the H1 memory OUTPUT every "
                        "iteration (the persistent state is corrupted as it is written; "
                        "H2 and the visual accumulator stay clean)")
    p.add_argument("--jepa-tau-student", type=float, default=0.1)
    p.add_argument("--jepa-tau-teacher-start", type=float, default=0.03)
    p.add_argument("--jepa-tau-teacher-end", type=float, default=0.05)
    p.add_argument("--jepa-tau-warmup", type=int, default=300)
    p.add_argument("--jepa-center-momentum", type=float, default=0.9)
    p.add_argument("--jepa-ema-decay", type=float, default=0.996)
    p.add_argument("--jepa-sinkhorn-iters", type=int, default=3)
    p.add_argument("--jepa-var-coef", type=float, default=1.0)
    p.add_argument("--jepa-cov-coef", type=float, default=0.01)
    p.add_argument("--jepa-coef", type=float, default=1.0)
    p.add_argument("--change-coef", type=float, default=1.0)
    p.add_argument("--theta-start", type=float, default=65.0,
                   help="starting max |orientation change| (degrees)")
    p.add_argument("--curr-threshold", type=float, default=0.85,
                   help="collection change-accuracy above which theta is reduced")
    p.add_argument("--curr-step", type=float, default=3.0,
                   help="degrees to subtract from theta per cleared collection")
    p.add_argument("--curr-floor", type=float, default=8.0,
                   help="theta never drops below this")
    p.add_argument("--n-trials", type=int, default=500000)
    p.add_argument("--collection-size", type=int, default=1024,
                   help="fresh training set collected before each epoch sweep")
    p.add_argument("--epochs", type=int, default=5,
                   help="epochs of updates over each fresh collection")
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--lr", type=float, default=0.0003)
    p.add_argument("--grad-clip", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--device", default="cuda")
    p.add_argument("--save-every", type=int, default=10,
                   help="checkpoint every this many collections")
    p.add_argument("--checkpoint-dir", default=None)
    p.add_argument("--log-every", type=int, default=1,
                   help="log every this many collections")
    p.add_argument("--resume", action="store_true",
                   help="resume from <checkpoint-dir>/kda_convmem_latest.pt (model + EMA "
                        "teacher + curriculum theta); appends to metrics.csv")
    return p


def main() -> None:
    args = build_parser().parse_args()
    seed_training_rngs(args.seed)
    device = pick_device(args.device)

    env = make_env(
        args.task, T=args.T, frame_repeat=args.frame_repeat,
        min_change_time=args.min_change_time, max_change_time=args.max_change_time,
        noise_multiplier=args.noise, curriculum=False, theta=args.theta_start,
    )
    T = int(env.T)
    if args.collection_size % args.batch_size != 0:
        raise SystemExit("--collection-size must be a multiple of --batch-size")

    model = KDAConvMemoryModel(n_channels=args.n_channels, proto_dim=args.proto_dim,
                               map_size=args.map_size,
                               memory_noise_std=args.memory_noise_std,
                               frame_window=args.frame_window,
                               frame_stride=args.frame_stride,
                               mem_every=args.mem_every,
                               accum_mode=args.accum_mode,
                               accum_decay=args.accum_decay,
                               kda_heads=args.kda_heads,
                               kda_head_dim=args.kda_head_dim,
                               attn_mode=args.attn_mode).to(device)
    jepa_teacher = copy.deepcopy(model)
    for p_ in jepa_teacher.parameters():
        p_.requires_grad_(False)
    jepa_teacher.eval()

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr, eps=1e-5)
    use_amp = bool(args.amp) and device.type == "cuda"
    amp_ctx = lambda: torch.autocast(device.type, dtype=torch.float16, enabled=use_amp)  # noqa: E731
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
    n_params = sum(p_.numel() for p_ in model.parameters())
    n_collections = (args.n_trials + args.collection_size - 1) // args.collection_size
    n_mb = args.collection_size // args.batch_size
    print(f"[kda-convmem] task={args.task} n_channels={args.n_channels} map={args.map_size} "
          f"proto={args.proto_dim} params={n_params:,} device={device} "
          f"| frame_window={args.frame_window} stride={args.frame_stride} mem_every={args.mem_every} "
          f"| accum_mode={args.accum_mode}(d0={args.accum_decay}) "
          f"kda={args.kda_heads}x{args.kda_head_dim} attn={args.attn_mode}")
    print(f"[kda-convmem] collections={n_collections} x {args.collection_size} trials x "
          f"{args.epochs} epochs x {n_mb} minibatches({args.batch_size}) = "
          f"{n_collections * args.collection_size} trials, "
          f"{n_collections * args.epochs * n_mb} updates")
    print(f"[kda-convmem] objectives: JEPA temporal per-pixel (coef {args.jepa_coef}) "
          f"+ change classifier on pool(R@last), full BPTT (coef {args.change_coef}), "
          f"label={args.label}; "
          f"teacher EMA={args.jepa_ema_decay}, centering momentum={args.jepa_center_momentum}, "
          f"JEPA-head input LayerNorm ON, memory noise sigma={args.memory_noise_std} "
          f"(on the H1 output every iteration; H2 and H_VA stay clean)")
    print(f"[kda-convmem] curriculum: theta starts {args.theta_start}, -{args.curr_step} when a "
          f"collection's change acc > {args.curr_threshold}, floor {args.curr_floor}")

    ckpt_dir = args.checkpoint_dir or os.path.join(_HERE, "kda_convmem_checkpoints")
    os.makedirs(ckpt_dir, exist_ok=True)

    # ---- optional resume: model + EMA teacher + curriculum state ----
    start_col = 0
    prev_elapsed = 0.0
    if args.resume:
        ckpt_path = os.path.join(ckpt_dir, "kda_convmem_latest.pt")
        ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
        model.load_state_dict(ckpt["model_state_dict"])
        jepa_teacher.load_state_dict(ckpt["jepa_teacher_state_dict"])
        start_col = int(ckpt["collection"]) + 1
        env.theta = float(ckpt.get("theta", env.theta))
        mp = os.path.join(ckpt_dir, "metrics.csv")
        if os.path.exists(mp):
            with open(mp) as f:
                rows = [r for r in csv.reader(f) if r]
            if len(rows) > 1:
                prev_elapsed = float(rows[-1][10])   # last row's elapsed_s
        print(f"[kda-convmem] RESUMING from {ckpt_path}: collection {start_col}, "
              f"theta={env.theta}, prior elapsed={prev_elapsed:.0f}s "
              f"(optimizer state resets — brief Adam transient expected)")

    metrics_path = os.path.join(ckpt_dir, "metrics.csv")
    fieldnames = ["collection", "n_trials", "loss_total", "loss_jepa_ce", "loss_jepa_var",
                  "loss_jepa_cov", "loss_change", "change_acc", "grad_norm", "theta", "elapsed_s"]
    if not (args.resume and os.path.exists(metrics_path)):
        with open(metrics_path, "w", newline="") as f:
            csv.writer(f).writerow(fieldnames)

    ce_loss = nn.CrossEntropyLoss()
    t_start = time.time() - prev_elapsed
    total_updates = start_col * args.epochs * n_mb
    for col in range(start_col, n_collections):
        # ---- collect a FRESH training set ----
        obs_list, change_list = [], []
        for _ in range(args.collection_size):
            env.reset()
            change_list.append(int(env.valid) if args.label == "valid" else int(env.change_true))
            frames = [env.step(0)[0] for _ in range(T)]
            obs_list.append(np.stack(frames))
        obs = torch.from_numpy(np.stack(obs_list))  # (N,T,S,S,3) — stays on CPU;
        # minibatches are transferred per update to avoid a device-resident block
        # (VDA16 100x100 frames: a full collection is ~2.4 GB fp32)
        change = torch.tensor(change_list, dtype=torch.long)

        acc = {k: 0.0 for k in ("loss_total", "loss_jepa_ce", "loss_jepa_var",
                                "loss_jepa_cov", "loss_change", "change_acc", "grad_norm")}
        n_upd = 0
        n_skipped = 0
        for epoch in range(args.epochs):
            order = torch.randperm(args.collection_size)
            for mb in range(n_mb):
                bidx = order[mb * args.batch_size:(mb + 1) * args.batch_size]
                obs_mb = obs[bidx].to(device, torch.float32, non_blocking=True)
                change_mb = change[bidx].to(device, non_blocking=True)

                # Teacher (clean, EMA).
                jepa_teacher.eval()
                with torch.no_grad(), amp_ctx():
                    R_t = jepa_teacher.forward_seq(obs_mb)
                z_t = jepa_teacher.jepa_logits(R_t.float())         # (B,T,map,map,P)
                frac = min(float(total_updates) / max(1, args.jepa_tau_warmup), 1.0)
                tau_t = args.jepa_tau_teacher_start + frac * (args.jepa_tau_teacher_end - args.jepa_tau_teacher_start)

                # Student. Recurrent forward under autocast (fp16); heads/losses in fp32.
                with amp_ctx():
                    R_s = model.forward_seq(obs_mb)                 # (B,T,4C,map,map)
                R_s = R_s.float()
                z_s = model.jepa_logits(R_s)

                m = torch.ones(obs_mb.shape[0], R_s.shape[1], device=device)
                ce, _ = structured_jepa_loss(
                    z_t[:, 1:], z_s[:, :-1], model.jepa_center, m[:, 1:] * m[:, :-1],
                    tau_teacher=tau_t, tau_student=args.jepa_tau_student,
                    sinkhorn_iters=args.jepa_sinkhorn_iters,
                )
                feats = model.jepa_features(R_s)[:, :-1]
                var, cov = jepa_variance_covariance_loss(feats, m[:, 1:] * m[:, :-1])
                jepa_loss = ce + args.jepa_var_coef * var + args.jepa_cov_coef * cov

                logits = model.classify(R_s[:, -1])
                change_loss = ce_loss(logits, change_mb)
                with torch.no_grad():
                    ch_acc = float((logits.argmax(-1) == change_mb).float().mean().item())

                loss = args.jepa_coef * jepa_loss + args.change_coef * change_loss

                # Hygiene only: one non-finite minibatch must not poison the
                # collection mean, GradScaler, teacher EMA, or DINO centre.
                # Architecture, JEPA, and VICReg are unchanged.
                if not torch.isfinite(loss).item():
                    optimizer.zero_grad(set_to_none=True)
                    n_skipped += 1
                    continue

                optimizer.zero_grad(set_to_none=True)
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(),
                                                           max_norm=args.grad_clip)
                if not torch.isfinite(grad_norm):
                    optimizer.zero_grad(set_to_none=True)
                    scaler.update()
                    n_skipped += 1
                    continue
                scaler.step(optimizer)
                scaler.update()

                # Teacher EMA + DINO centre update (per optimizer step).
                with torch.no_grad():
                    dj = args.jepa_ema_decay
                    for tp, p_ in zip(jepa_teacher.parameters(), model.parameters()):
                        tp.data.mul_(dj).add_(p_.data, alpha=1.0 - dj)
                    batch_center = masked_jepa_center(z_t, m)
                    model.jepa_center.mul_(args.jepa_center_momentum).add_(
                        batch_center, alpha=1.0 - args.jepa_center_momentum)

                acc["loss_total"] += float(loss.detach().item())
                acc["loss_jepa_ce"] += float(ce.detach().item())
                acc["loss_jepa_var"] += float(var.detach().item())
                acc["loss_jepa_cov"] += float(cov.detach().item())
                acc["loss_change"] += float(change_loss.detach().item())
                acc["change_acc"] += ch_acc
                acc["grad_norm"] += float(grad_norm)
                n_upd += 1
                total_updates += 1

        # ---- curriculum: shrink theta when this collection's change acc clears the bar ----
        if n_upd == 0:
            print(f"[kda-convmem c{col}/{n_collections}] skipped entire collection "
                  f"({n_skipped} non-finite minibatches); no metrics row, theta unchanged")
            continue
        coll_acc = acc["change_acc"] / n_upd
        if coll_acc > args.curr_threshold and env.theta > args.curr_floor:
            env.theta = max(args.curr_floor, env.theta - args.curr_step)

        row = {k: acc[k] / n_upd for k in acc}
        row.update(collection=col, n_trials=(col + 1) * args.collection_size,
                   theta=float(env.theta), elapsed_s=time.time() - t_start)
        with open(metrics_path, "a", newline="") as f:
            csv.writer(f).writerow([row[k] for k in fieldnames])

        if col % args.log_every == 0 or col == n_collections - 1:
            skip_note = f" skip={n_skipped}" if n_skipped else ""
            print(f"[kda-convmem c{col}/{n_collections}] trials={(col + 1) * args.collection_size} "
                  f"jepa={row['loss_jepa_ce']:.3f} var={row['loss_jepa_var']:.3f} "
                  f"cov={row['loss_jepa_cov']:.2f} change={row['loss_change']:.3f} "
                  f"acc={row['change_acc']:.3f} theta={row['theta']:.1f} "
                  f"gnorm={row['grad_norm']:.2f} ({row['elapsed_s']:.0f}s){skip_note}")

        if (col + 1) % args.save_every == 0 or col == n_collections - 1:
            ckpt_path = os.path.join(ckpt_dir, "kda_convmem_latest.pt")
            torch.save({
                "model_state_dict": model.state_dict(),
                "jepa_teacher_state_dict": jepa_teacher.state_dict(),
                "collection": col,
                "n_trials": (col + 1) * args.collection_size,
                "theta": float(env.theta),
                "n_channels": args.n_channels,
                "map_size": args.map_size,
                "proto_dim": args.proto_dim,
                "frame_window": args.frame_window,
                "frame_stride": args.frame_stride,
                "mem_every": args.mem_every,
                "accum_mode": args.accum_mode,
                "accum_decay": float(args.accum_decay),
                "kda_heads": args.kda_heads,
                "kda_head_dim": args.kda_head_dim,
                "attn_mode": args.attn_mode,
            }, ckpt_path)
            print(f"[kda-convmem] checkpoint saved: {ckpt_path}")

    print(f"[kda-convmem] DONE. total trials={n_collections * args.collection_size} "
          f"updates={total_updates} elapsed={time.time() - t_start:.0f}s; checkpoint in {ckpt_dir}")


if __name__ == "__main__":
    main()
