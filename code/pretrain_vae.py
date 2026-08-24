"""
Pretrain the paper's patch VAE on the task's own image patches, then save the encoder
weights so the RL model's front-end can load them (frozen) — the user's hypothesis:
a reconstruction-pretrained VAE gives an orientation-informative front-end that sparse
RL reward can't teach, which may be the missing ingredient on the 7-step task.

    python RViT_plus_paper_softmaxhead/pretrain_vae.py --device cpu          # → ~/rvit_plus_checkpoints/paper_vae/vae.pt

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


def sample_patches(n_episodes: int, noise: float = 5.0, task: str = "validity4",
                   color: bool = False) -> torch.Tensor:
    """Roll out full episodes (forced wait) and collect every 25×25 quadrant.
    color=False → grayscale (1ch, paper-faithful, value-blind);
    color=True  → keep RGB (3ch) so the colour value cue is preserved. Use task='vda4' for colour."""
    env = make_env(task, noise_multiplier=noise)
    patches = []
    for _ in range(n_episodes):
        o = env.reset(); done = False
        while not done:
            f = np.asarray(o, dtype=np.float32)                          # (50,50,3) RGB
            if not color:
                f = f.mean(axis=2, keepdims=True)                        # (50,50,1) grayscale
            for (r0, r1, c0, c1) in [(0, 25, 0, 25), (0, 25, 25, 50), (25, 50, 0, 25), (25, 50, 25, 50)]:
                patches.append(f[r0:r1, c0:c1])                          # (25,25,C)
            o, _, done, _ = env.step(0)                                  # wait → see all 7 frames
    X = torch.from_numpy(np.stack(patches)).permute(0, 3, 1, 2).contiguous()   # (N,C,25,25)
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
    p.add_argument("--task", default="validity4", help="env to sample patches from (colour task = vda4).")
    p.add_argument("--color", action="store_true",
                   help="COLOUR VAE: keep RGB (3ch) so the value cue is visible. Default = grayscale (1ch).")
    p.add_argument("--device", default="cpu")
    p.add_argument("--out", default=None, help="default: paper_vae/vae.pt (grayscale) or paper_vae_color/vae_color.pt (colour)")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    if args.out is None:
        args.out = os.path.expanduser("~/rvit_plus_checkpoints/"
                                      + ("paper_vae_color/vae_color.pt" if args.color else "paper_vae/vae.pt"))
    in_ch = 3 if args.color else 1

    torch.manual_seed(args.seed); np.random.seed(args.seed)
    dev = torch.device(args.device)
    X = sample_patches(args.episodes, noise=args.noise, task=args.task, color=args.color)
    print(f"[vae] mode={'COLOUR(3ch)' if args.color else 'grayscale(1ch)'} task={args.task} "
          f"sampled {X.shape[0]:,} patches (C={X.shape[1]}); value range [{X.min():.3f}, {X.max():.3f}]")
    # env renders in ~[-1,1]; map to [0,1] for the sigmoid decoder so the FULL Gabor
    # waveform (incl. negative lobes) is reconstructed → orientation-rich features.
    # (The ENCODER still sees raw X, matching RL time, so the front-end stays consistent.)
    target = ((X + 1.0) / 2.0).clamp(0.0, 1.0)                           # sigmoid decoder target

    vae = PatchVAE(d_latent=args.d_latent, in_channels=in_ch).to(dev)
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
                "n_patches": int(N),
                # provenance so the two VAEs are NEVER confused:
                "in_channels": in_ch, "color": bool(args.color), "task": args.task,
                "kind": "COLOUR" if args.color else "grayscale"}, args.out)
    print(f"[vae] saved {('COLOUR(3ch)' if args.color else 'grayscale(1ch)')} VAE (task={args.task}) → {args.out}")
    print(f"[vae] encoder keys: {list(vae.encoder_state_dict().keys())}")


if __name__ == "__main__":
    main()
