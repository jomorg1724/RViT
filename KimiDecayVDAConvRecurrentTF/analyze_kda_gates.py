"""Post-training analysis of the KDA conv-memory model — VDA16 (4x4 grid).

Ported from analyze_convmem_gates_vda16.py with two changes:

  1. The unrolled recurrence inserts the visual accumulator (the kda run's
     state is (H1, H2, ACC); vision consumes [X_t || acc_read]).
  2. Every attention-like quantity gets a map, for EVERY cue proportion
     (k/16 ring levels) crossed with THREE change conditions:
     no-change, change at S1 (valid/cued), change at S4 (invalid).
     In addition to the eight established maps (vision gates A_X/A_H, memory
     gates A_Z/A_H1, and the four A.V energy maps), the KDA accumulator
     contributes three new per-pixel maps, recomputed exactly from its
     convs (the model file is NOT modified):
       alpha    — decay field a_t,     mean over heads x channels
       beta     — write gate b_t,      mean over heads
       surprise — ||v - S~^T k||_2,    per-pixel delta-rule prediction error
     The scientific question: does the delta-rule write gate / surprise
     localize to the changed cell, and does it differ valid vs invalid?

Part 1 — frozen probes on R@last (change 2-way, cue 16-way; linear + MLP).
Part 2 — maps: 48 conditions x n-trials, saved to gate_maps_kda.npz plus
         one vision, one memory, and one accumulator figure per condition.

Usage:
  python analyze_kda_gates.py --checkpoint ckpt.pt --out-dir DIR [--device cuda]
  quick smoke: --probe-trials 20 --heatmap-trials 3 --n-props 2
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import torch
import torch.nn as nn

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from kda_conv_memory_model import KDAConvMemoryModel
from envs import make_env
from train_rl import pick_device, seed_training_rngs

T = 7
MAP = 16
PROPS_FULL = [i / 16 for i in range(1, 17)]
S1, S4 = 0, 3

# (suffix, change_true, pinned change cell)
CHANGE_CONDS = [("nochange", 0, -1), ("changeS1", 1, S1), ("changeS4", 1, S4)]


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
    Xt, yt = X[tr].to(device), y[tr].to(device)
    Xe, ye = X[te].to(device), y[te].to(device)
    for _ in range(epochs):
        opt.zero_grad()
        ce(net(Xt), yt).backward()
        opt.step()
    with torch.no_grad():
        return float((net(Xe).argmax(-1) == ye).float().mean().item())


def nice_ceil(v: float) -> float:
    for nice in (1, 2, 5, 10, 12, 20, 25, 50, 100, 150, 200, 250, 500, 1000):
        if v <= nice:
            return float(nice)
    return float(np.ceil(v / 1000) * 1000)


def render_grid(arr, rows, suptitle, out_png):
    """rows: tuple of (array_key, label, vmin, vmax); one figure: len(rows) x T."""
    fig, axes = plt.subplots(len(rows), T, figsize=(2.6 * T, 2.7 * len(rows)))
    for t in range(T):
        for row, (key, label, vmin, vmax) in enumerate(rows):
            ax = axes[row, t]
            im = ax.imshow(arr[key][t], vmin=vmin, vmax=vmax, cmap="viridis", origin="upper")
            ax.set_xticks([]); ax.set_yticks([])
            if t == 0:
                ax.set_ylabel(label, fontsize=10)
            if row == 0:
                ax.set_title(f"t={t}", fontsize=10)
            for b in (4, 8, 12):
                ax.axhline(b - 0.5, color="w", lw=0.6, alpha=0.5)
                ax.axvline(b - 0.5, color="w", lw=0.6, alpha=0.5)
    fig.colorbar(im, ax=axes, fraction=0.02, label="gate value / energy")
    fig.suptitle(suptitle, fontsize=12)
    fig.tight_layout(rect=[0, 0, 0.97, 0.95])
    fig.savefig(out_png, dpi=120)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description="KDA conv-memory post-training analysis (vda16)")
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--probe-trials", type=int, default=6000)
    ap.add_argument("--heatmap-trials", type=int, default=100)
    ap.add_argument("--n-props", type=int, default=16)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    seed_training_rngs(0)
    device = pick_device(args.device)

    ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    assert ckpt["accum_mode"] == "kda", f"expected a kda checkpoint, got {ckpt['accum_mode']}"
    model = KDAConvMemoryModel(
        n_channels=ckpt["n_channels"], proto_dim=ckpt["proto_dim"],
        map_size=ckpt["map_size"],
        memory_noise_std=0.05,          # matches kda seed-0 training contract
        frame_window=ckpt.get("frame_window", 1),
        frame_stride=ckpt.get("frame_stride", 1),
        mem_every=ckpt.get("mem_every", 1),
        accum_mode=ckpt["accum_mode"], accum_decay=ckpt["accum_decay"],
        kda_heads=ckpt["kda_heads"], kda_head_dim=ckpt["kda_head_dim"],
    ).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    acc = model.accumulator
    h, dk, dv = acc.h, acc.dk, acc.dv

    env = make_env("vda16", T=T, frame_repeat=1, min_change_time=5, max_change_time=5,
                   noise_multiplier=5.0, curriculum=False, theta=65.0)

    # ---------------- Part 1: fresh probes on frozen R@last ----------------
    print("[analysis-kda] Part 1: fresh probes on frozen R@last ...")
    X_feat, y_chg, y_cue = [], [], []
    with torch.no_grad():
        for _ in range(args.probe_trials):
            env.reset()
            frames = [env.step(0)[0] for _ in range(T)]
            obs = torch.from_numpy(np.stack(frames)).unsqueeze(0).float().to(device)
            R = model.forward_seq(obs)
            r = R[:, -1].mean(dim=(2, 3)).cpu().numpy()[0]      # (4C,)
            X_feat.append(r)
            y_chg.append(int(env.change_true))
            y_cue.append(int(env.cue_index))
    Xf = np.stack(X_feat)
    y_chg, y_cue = np.array(y_chg), np.array(y_cue)
    results = {
        "change_linear": probe(Xf, y_chg, 2, device, mlp=False),
        "change_mlp": probe(Xf, y_chg, 2, device, mlp=True),
        "cue_linear": probe(Xf, y_cue, 16, device, mlp=False),
        "cue_mlp": probe(Xf, y_cue, 16, device, mlp=True),
    }
    print(f"[analysis-kda]   change: linear={results['change_linear']:.3f}  "
          f"mlp={results['change_mlp']:.3f}  (chance 0.50)")
    print(f"[analysis-kda]   cue:    linear={results['cue_linear']:.3f}  "
          f"mlp={results['cue_mlp']:.3f}  (chance 0.0625)")
    with open(os.path.join(args.out_dir, "probe_results_kda.json"), "w") as f:
        json.dump(results, f, indent=2)

    # ---------------- Part 2: full map battery ----------------
    props = PROPS_FULL[: args.n_props]
    conditions = [(f"cueS1_{k}of16_{suffix}", k / 16, ch, cidx)
                  for k in range(1, args.n_props + 1)
                  for (suffix, ch, cidx) in CHANGE_CONDS]
    NC = len(conditions)
    keys = ("Ax", "Ah", "eX", "eH", "Az", "Ah1", "eZ", "eH1", "alpha", "beta", "surprise")
    maps = {k: np.zeros((NC, T, MAP, MAP), dtype=np.float64) for k in keys}

    print(f"[analysis-kda] Part 2: {NC} conditions x {args.heatmap_trials} trials x {T} steps ...")
    with torch.no_grad():
        for ci, (name, prop, change, cidx) in enumerate(conditions):
            for _ in range(args.heatmap_trials):
                obs0 = env.reset()
                env.cue_index = 0
                env.cue_color = "red"
                env.proportion = float(prop)
                env.change_true = int(change)
                if change:
                    env.change_index = int(cidx)
                frames = [obs0] + [env.step(0)[0] for _ in range(T - 1)]
                obs = torch.from_numpy(np.stack(frames)).unsqueeze(0).float().to(device)
                H1, H2, ACC = model.init_state(1, device, obs.dtype)
                for t in range(T):
                    frame = obs[:, t].permute(0, 3, 1, 2).contiguous()
                    X_t = model.stem(frame)

                    # --- accumulator maps recomputed exactly (pre-update state) ---
                    inp = torch.cat([X_t, H1], dim=1)
                    a = torch.sigmoid(acc.W_a(inp)).view(1, h, dk, 1, MAP * MAP).float()
                    b = torch.sigmoid(acc.W_b(inp)).view(1, h, 1, 1, MAP * MAP).float()
                    k_ = torch.nn.functional.normalize(
                        acc.W_k(inp).view(1, h, dk, MAP * MAP).float(), dim=2)
                    v = acc.W_v(inp).view(1, h, dv, MAP * MAP).float()
                    S_dec = a * ACC.float()
                    v_hat = torch.einsum("bhikp,bhip->bhkp", S_dec, k_)
                    err = v - v_hat
                    maps["alpha"][ci, t] += a.mean(dim=(1, 2, 3))[0].view(MAP, MAP).cpu().numpy()
                    maps["beta"][ci, t] += b.mean(dim=(1, 2, 3))[0].view(MAP, MAP).cpu().numpy()
                    maps["surprise"][ci, t] += err.norm(dim=2).mean(dim=1)[0].view(MAP, MAP).cpu().numpy()

                    # --- true accumulator update (state advance) ---
                    ACC, acc_read, _ = model._accumulate(X_t, H1, ACC)
                    Xin = torch.cat([X_t, acc_read], dim=1)

                    # --- vision gates/energies ---
                    Z, att, A = model.vision(Xin, H1, H2, return_attn=True)
                    Vx = model.vision.W_vx(Xin)
                    Vh = model.vision.W_vh(H2)
                    maps["Ax"][ci, t] += A[0, 0].cpu().numpy()
                    maps["Ah"][ci, t] += A[0, 1].cpu().numpy()
                    maps["eX"][ci, t] += (A[:, 0:1] * Vx).pow(2).sum(dim=1).sqrt()[0].cpu().numpy()
                    maps["eH"][ci, t] += (A[:, 1:2] * Vh).pow(2).sum(dim=1).sqrt()[0].cpu().numpy()

                    # --- memory gates/energies recomputed exactly ---
                    mem = model.memory
                    Qm = mem.W_q(H1)
                    Sz = (Qm * mem.W_kz(Z)).sum(dim=1, keepdim=True) * mem.scale
                    Sh = (Qm * mem.W_kh(H1)).sum(dim=1, keepdim=True) * mem.scale
                    Am = torch.softmax(torch.cat([Sz, Sh], dim=1), dim=1)
                    Vz = mem.W_vz(Z)
                    Vh1 = mem.W_vh(H1)
                    maps["Az"][ci, t] += Am[0, 0].cpu().numpy()
                    maps["Ah1"][ci, t] += Am[0, 1].cpu().numpy()
                    maps["eZ"][ci, t] += (Am[:, 0:1] * Vz).pow(2).sum(dim=1).sqrt()[0].cpu().numpy()
                    maps["eH1"][ci, t] += (Am[:, 0:1] * Vh1).pow(2).sum(dim=1).sqrt()[0].cpu().numpy()

                    H1, H2 = model.memory(Z, H1)
            print(f"[analysis-kda]   {name}: done", flush=True)

    for k in keys:
        maps[k] /= args.heatmap_trials
    np.savez(os.path.join(args.out_dir, "gate_maps_kda.npz"),
             conditions=np.array([c[0] for c in conditions]),
             **{k: maps[k] for k in keys})

    # ---- figures: vision, memory, accumulator per condition ----
    eZ_max = nice_ceil(float(maps["eZ"].max()) or 1.0)
    eH1_max = nice_ceil(float(maps["eH1"].max()) or 1.0)
    surp_max = nice_ceil(float(maps["surprise"].max()) or 1.0)
    vis_rows = (("Ax", r"$A_X$ (visual)", 0.0, 1.0),
                ("Ah", r"$A_H$ (memory)", 0.0, 1.0),
                ("eX", r"$\|A_X V_X\|$ (visual energy)", 0.0, 12.0),
                ("eH", r"$\|A_H V_H\|$ (memory energy)", 0.0, 100.0))
    mem_rows = (("Az", r"$A_Z$ (current obs)", 0.0, 1.0),
                ("Ah1", r"$A_{H1}$ (persistent)", 0.0, 1.0),
                ("eZ", r"$\|A_Z V_Z\|$ (obs energy)", 0.0, eZ_max),
                ("eH1", r"$\|A_{H1} V_{H1}\|$ (persistent energy)", 0.0, eH1_max))
    acc_rows = (("alpha", r"$\alpha_t$ (decay field)", 0.0, 1.0),
                ("beta", r"$\beta_t$ (write gate)", 0.0, 1.0),
                ("surprise", r"$\|v - \tilde{S}^\top k\|$ (surprise)", 0.0, surp_max))

    for ci, (name, prop, change, cidx) in enumerate(conditions):
        sub = {k: maps[k][ci] for k in keys}
        tag = f"{name}  (red cue on S1)"
        render_grid(sub, vis_rows, tag, os.path.join(args.out_dir, f"kda_vis_{name}.png"))
        render_grid(sub, mem_rows, tag + "  —  memory layer",
                    os.path.join(args.out_dir, f"kda_mem_{name}.png"))
        render_grid(sub, acc_rows, tag + "  —  KDA accumulator",
                    os.path.join(args.out_dir, f"kda_acc_{name}.png"))
    print(f"[analysis-kda] DONE. {3 * NC} figures + npz + probes in {args.out_dir}")


if __name__ == "__main__":
    main()
