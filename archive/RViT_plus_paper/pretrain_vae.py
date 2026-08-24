"""
Pretrain the paper's patch VAE on the task's own image patches, then save the encoder
weights so the RL model's front-end can load them (frozen) — the user's hypothesis:
a reconstruction-pretrained VAE gives an orientation-informative front-end that sparse
RL reward can't teach, which may be the missing ingredient on the 7-step task.

    python RViT_plus_paper/pretrain_vae.py --device cpu          # → ~/rvit_plus_checkpoints/paper_vae/vae.pt

Patches are sampled EXACTLY as the front-end sees them: grayscale (mean over RGB), four
25×25 quadrants in order [TL, TR, BL, BR], from real env frames (blanks, cues, Gabors).
The encoder is scale-agnostic; the decoder's sigmoid targets the patch clamped to [0,1].
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from envs import make_env                # noqa: E402
from vae import PatchVAE                  # noqa: E402


def sample_patches(n_episodes: int, noise: float = 5.0) -> torch.Tensor:
    """Roll out full episodes (forced wait) and collect every 25×25 grayscale quadrant."""
    env = make_env("validity4", noise_multiplier=noise)
    patches = []
    for _ in range(n_episodes):
        o = env.reset(); done = False
        while not done:
            g = np.asarray(o, dtype=np.float32).mean(axis=2)             # (50,50) grayscale
            for (r0, r1, c0, c1) in [(0, 25, 0, 25), (0, 25, 25, 50), (25, 50, 0, 25), (25, 50, 25, 50)]:
                patches.append(g[r0:r1, c0:c1])
            o, _, done, _ = env.step(0)                                  # wait → see all 7 frames
    X = torch.from_numpy(np.stack(patches)).unsqueeze(1)                 # (N,1,25,25)
    return X


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--episodes", type=int, default=2000)
    p.add_argument("--epochs", type=int, default=15)
    p.add_argument("--batch", type=int, default=256)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--beta", type=float, default=1e-3)
    p.add_argument("--d-latent", type=int, default=32)
    p.add_argument("--noise", type=float, default=5.0, help="orientation noise σ for the sampled patches")
    p.add_argument("--device", default="cpu")
    p.add_argument("--out", default=os.path.expanduser("~/rvit_plus_checkpoints/paper_vae/vae.pt"))
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    torch.manual_seed(args.seed); np.random.seed(args.seed)
    dev = torch.device(args.device)
    X = sample_patches(args.episodes, noise=args.noise)
    print(f"[vae] sampled {X.shape[0]:,} patches at σ={args.noise}; value range [{X.min():.3f}, {X.max():.3f}]")
    # env renders in ~[-1,1]; map to [0,1] for the sigmoid decoder so the FULL Gabor
    # waveform (incl. negative lobes) is reconstructed → orientation-rich features.
    # (The ENCODER still sees raw X, matching RL time, so the front-end stays consistent.)
    target = ((X + 1.0) / 2.0).clamp(0.0, 1.0)                           # sigmoid decoder target

    vae = PatchVAE(d_latent=args.d_latent).to(dev)
    opt = torch.optim.Adam(vae.parameters(), lr=args.lr)
    N = X.shape[0]
    for ep in range(args.epochs):
        perm = torch.randperm(N)
        tot = rec = klsum = 0.0; nb = 0
        for i in range(0, N, args.batch):
            idx = perm[i:i + args.batch]
            o_in = X[idx].to(dev); o_tgt = target[idx].to(dev)
            recon, mu, logvar, _ = vae(o_in)
            loss, rl, kl = PatchVAE.loss(o_tgt, recon, mu, logvar, beta=args.beta)
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item(); rec += rl; klsum += kl; nb += 1
        print(f"[vae] epoch {ep+1:2d}/{args.epochs}  loss={tot/nb:.5f}  recon={rec/nb:.5f}  kl={klsum/nb:.3f}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    torch.save({"vae_state": vae.state_dict(),
                "encoder_state": vae.encoder_state_dict(),
                "d_latent": args.d_latent, "beta": args.beta,
                "n_patches": int(N)}, args.out)
    print(f"[vae] saved encoder + full VAE → {args.out}")
    print(f"[vae] encoder keys: {list(vae.encoder_state_dict().keys())}")


if __name__ == "__main__":
    main()
