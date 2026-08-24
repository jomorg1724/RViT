"""
Post-training analysis of the conv-memory model.

Part 1 — FRESH probe: is the change (and the cue) decodable from the FROZEN
         representation R at the last timestep? (fresh linear + MLP probes, 80/20 split)
Part 2 — Gate heatmaps: A_X and A_H (16x16 per-pixel gates of the vision conv-attention)
         for every timestep t=0..6, averaged over N trials, for six controlled
         conditions (RED cue on S1, with/without change on S1/S4, and validity 100/75/50/25).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import torch
import torch.nn as nn

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from conv_memory_model import ConvMemoryModel
from envs import make_env
from train_rl import pick_device, seed_training_rngs

T = 7
MAP = 16


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Conv-memory post-training analysis")
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--probe-trials", type=int, default=6000)
    p.add_argument("--heatmap-trials", type=int, default=100)
    p.add_argument("--out-dir", default=None)
    return p


def probe(X, y, n_classes, device, mlp=False, epochs=120, lr=1e-3):
    X = torch.as_tensor(X, dtype=torch.float32)
    y = torch.as_tensor(y, dtype=torch.long)
    n = X.shape[0]
    perm = torch.randperm(n)
    tr, te = perm[: int(0.8 * n)], perm[int(0.8 * n):]
    if mlp:
        net = nn.Sequential(nn.Linear(X.shape[1], 256), nn.ReLU(),
                            nn.Linear(256, n_classes)).to(device)
    else:
        net = nn.Linear(X.shape[1], n_classes).to(device)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    ce = nn.CrossEntropyLoss()
    Xt, yt, Xe, ye = X[tr].to(device), y[tr].to(device), X[te].to(device), y[te].to(device)
    for _ in range(epochs):
        opt.zero_grad()
        ce(net(Xt), yt).backward()
        opt.step()
    with torch.no_grad():
        return float((net(Xe).argmax(-1) == ye).float().mean().item())


def main() -> None:
    args = build_parser().parse_args()
    seed_training_rngs(0)
    device = pick_device("cuda")
    out_dir = args.out_dir or os.path.dirname(args.checkpoint)
    os.makedirs(out_dir, exist_ok=True)

    ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    model = ConvMemoryModel(n_channels=ckpt["n_channels"], proto_dim=ckpt["proto_dim"],
                            map_size=ckpt["map_size"]).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    env = make_env("vda4", T=7, frame_repeat=1, min_change_time=5, max_change_time=5,
                   noise_multiplier=5.0, curriculum=False, theta=65.0)

    # ---------------- Part 1: fresh probe on frozen R@last ----------------
    print("[analysis] Part 1: fresh probe on frozen R@last ...")
    X_feat, y_chg, y_cue = [], [], []
    with torch.no_grad():
        for _ in range(args.probe_trials):
            env.reset()
            frames = [env.step(0)[0] for _ in range(T)]
            obs = torch.from_numpy(np.stack(frames)).unsqueeze(0).float().to(device)
            R = model.forward_seq(obs)
            r = R[:, -1].mean(dim=(2, 3)).cpu().numpy()[0]      # (512,)
            X_feat.append(r)
            y_chg.append(int(env.change_true))
            y_cue.append(int(env.cue_index))
    Xf = np.stack(X_feat)
    y_chg = np.array(y_chg)
    y_cue = np.array(y_cue)
    results = {
        "change_linear": probe(Xf, y_chg, 2, device, mlp=False),
        "change_mlp": probe(Xf, y_chg, 2, device, mlp=True),
        "cue_linear": probe(Xf, y_cue, 4, device, mlp=False),
        "cue_mlp": probe(Xf, y_cue, 4, device, mlp=True),
    }
    print(f"[analysis]   change: linear={results['change_linear']:.3f}  mlp={results['change_mlp']:.3f}  (chance 0.50)")
    print(f"[analysis]   cue:    linear={results['cue_linear']:.3f}  mlp={results['cue_mlp']:.3f}  (chance 0.25)")
    with open(os.path.join(out_dir, "probe_results.json"), "w") as f:
        json.dump(results, f, indent=2)

    # ---------------- Part 2: gate heatmaps ----------------
    print("[analysis] Part 2: gate heatmaps (A_X, A_H; 16x16; per timestep) ...")
    conditions = [
        ("cueS1_100p_nochange", 1.0, 0, -1),
        ("cueS1_100p_changeS1", 1.0, 1, 0),
        ("cueS1_100p_changeS4", 1.0, 1, 3),
        ("cueS1_75p_nochange", 0.75, 0, -1),
        ("cueS1_50p_nochange", 0.50, 0, -1),
        ("cueS1_25p_nochange", 0.25, 0, -1),
    ]
    Ax = np.zeros((len(conditions), T, MAP, MAP), dtype=np.float64)
    Ah = np.zeros_like(Ax)
    with torch.no_grad():
        for ci, (name, prop, change, cidx) in enumerate(conditions):
            for tr in range(args.heatmap_trials):
                obs0 = env.reset()
                env.cue_index = 0          # S1
                env.proportion = float(prop)
                env.cue_color = "red"
                env.change_true = int(change)
                env.change_index = int(cidx)
                frames = [obs0] + [env.step(0)[0] for _ in range(T - 1)]
                obs = torch.from_numpy(np.stack(frames)).unsqueeze(0).float().to(device)
                state = model.init_state(1, device, obs.dtype)
                for t in range(T):
                    frame = obs[:, t].permute(0, 3, 1, 2).contiguous()
                    X_t = model.stem(frame)
                    H1, H2 = state
                    Z, att, A = model.vision(X_t, H1, H2, return_attn=True)
                    H1n, H2n = model.memory(Z, H1)
                    state = (H1n, H2n)
                    Ax[ci, t] += A[0, 0].cpu().numpy()
                    Ah[ci, t] += A[0, 1].cpu().numpy()
            print(f"[analysis]   {name}: done")
    Ax /= args.heatmap_trials
    Ah /= args.heatmap_trials
    np.savez(os.path.join(out_dir, "gate_maps.npz"),
             Ax=Ax, Ah=Ah, conditions=np.array([c[0] for c in conditions]))

    # plot: one figure per condition, 2 rows (A_X, A_H) x 7 timesteps
    for ci, (name, prop, change, cidx) in enumerate(conditions):
        fig, axes = plt.subplots(2, T, figsize=(2.6 * T, 5.4))
        for t in range(T):
            for row, (arr, label) in enumerate(((Ax, r"$A_X$ (visual)"), (Ah, r"$A_H$ (memory)"))):
                ax = axes[row, t]
                im = ax.imshow(arr[ci, t], vmin=0.0, vmax=1.0, cmap="viridis", origin="upper")
                ax.set_xticks([]); ax.set_yticks([])
                if t == 0:
                    ax.set_ylabel(label, fontsize=10)
                if row == 0:
                    ax.set_title(f"t={t}", fontsize=10)
                for b in (8,):
                    ax.axhline(b - 0.5, color="w", lw=0.6, alpha=0.5)
                    ax.axvline(b - 0.5, color="w", lw=0.6, alpha=0.5)
        fig.colorbar(im, ax=axes, fraction=0.02, label="gate value")
        fig.suptitle(f"{name}  (red cue on S1)", fontsize=12)
        fig.tight_layout(rect=[0, 0, 0.97, 0.95])
        out_png = os.path.join(out_dir, f"gates_{name}.png")
        fig.savefig(out_png, dpi=120)
        plt.close(fig)
        print(f"[analysis]   saved {out_png}")

    print(f"[analysis] DONE. outputs in {out_dir}")


if __name__ == "__main__":
    main()
