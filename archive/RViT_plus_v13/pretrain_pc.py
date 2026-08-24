"""
RViT+ v13 — PHASE 1: self-supervised predictive-coding pretraining.

Trains the encoder (PART A: T1 + LSTM1 + LSTM2 + the JEPA predictor) so that H2_t
predicts H1_{t+1} (VICReg-style, quantified surprise), on frame sequences rolled
out from the env. NO reward, NO energy stream. Saves the pretrained model so that
train_rl.py can freeze PART A and train the energy stream (PART B) for the RL task.

Usage:
    .venv/bin/python RViT_plus_v13/pretrain_pc.py --iters 3000
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v13.env import ChangeDetectionEnv
from RViT_plus_v13.model import RViTPlusV13Model
from RViT_plus_v13.ppo import collect_episodes


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--iters", type=int, default=3000)
    p.add_argument("--episodes-per-iter", type=int, default=16)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--grad-clip", type=float, default=1.0)
    p.add_argument("--d-model", type=int, default=128)
    p.add_argument("--d-latent", type=int, default=128)
    p.add_argument("--tx-heads", type=int, default=1)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--log-every", type=int, default=25)
    p.add_argument("--save-every", type=int, default=500)
    p.add_argument("--out", default="/Users/jonathanmorgan/rvit_plus_checkpoints/v13/pc_pretrained.pt")
    args = p.parse_args(argv)

    torch.manual_seed(args.seed); np.random.seed(args.seed)
    import random; random.seed(args.seed)
    device = torch.device("cpu")

    model = RViTPlusV13Model(d_model=args.d_model, d_mem=args.d_model, tx_heads=args.tx_heads,
                             d_latent=args.d_latent).to(device)
    n_pc = sum(p_.numel() for mod in [model.patch_embed, *model.encoder.pc_modules()]
               for p_ in ([mod] if isinstance(mod, torch.nn.Parameter) else mod.parameters()))
    print(f"[diag] PART A (predictive-coding encoder + patch_embed) params: {n_pc:,}")
    print(f"[diag] training PHASE 1 (self-supervised): H2_t predicts H1_(t+1), VICReg anti-collapse")

    opt = torch.optim.Adam([p_ for p_ in model.parameters() if p_.requires_grad], lr=args.lr, eps=1e-5)
    env = ChangeDetectionEnv()
    t0 = time.time()
    roll = []
    for it in range(args.iters):
        # full-length frame sequences (force wait so episodes run to T).
        batch, _ = collect_episodes(model, env, n_episodes=args.episodes_per_iter,
                                    device=device, force_action=0)
        model.train()
        out = model.predictive_forward(batch.observations)
        loss = out["loss"]
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_([p_ for p_ in model.parameters() if p_.requires_grad], args.grad_clip)
        opt.step()
        roll.append(float(out["surprise_seq"].mean()))
        if (it + 1) % args.log_every == 0:
            r = sum(roll[-args.log_every:]) / min(len(roll), args.log_every)
            pr = out["parts"]
            print(f"[pc {it+1:5d} | {time.time()-t0:6.1f}s] surprise(mean)={r:.4f}  "
                  f"L={float(loss):.4f}  pred={pr['pred']:.4f}  var={pr['var']:.4f}  cov={pr['cov']:.4f}")
        if (it + 1) % args.save_every == 0:
            os.makedirs(os.path.dirname(args.out), exist_ok=True)
            torch.save({"iter": it, "model_state_dict": model.state_dict(),
                        "phase": "pc_pretrained"}, args.out)
            print(f"[checkpoint] {args.out}")
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    torch.save({"iter": args.iters - 1, "model_state_dict": model.state_dict(),
                "phase": "pc_pretrained"}, args.out)
    print(f"[done] PHASE 1 pretrained encoder saved to {args.out}\n"
          f"       Next: train_rl.py --pc-checkpoint {args.out}  (freezes PART A, trains the energy stream)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
