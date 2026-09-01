"""Left-hemisphere lesion psychometric on the completed VDA16 KDA seed-0.

Protocol (matches Block B of psychometric_kda.py):
  cue pinned on S1 (cell 0), proportion 1.0, change pinned on S4 (cell 3).

Lesion: every recurrent step, zero the 4x4-px patches of the LEFT 8 stimulus
cells (grid columns 0 and 1: cells 0,1,4,5,8,9,12,13) on X_t, acc_read, KDA
state S, Z, att_vis, H1, H2. S1 (cued) is silenced; S4 (change) is intact.

This is a cortical/map lesion, not a pixel scotoma — the stem still sees the
left Gabors, then those map locations are forced to 0 so they cannot compete.

Comparison curves loaded from the existing psychometric_kda.json (valid S1,
invalid S4) and, if present, the A_H1[S4]:=1 recovery.

Usage:
  python psychometric_kda_hemilesion.py <checkpoint> <out_dir> [--device cuda]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import torch

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kda_conv_memory_model import KDAConvMemoryModel
from envs import make_env
from train_rl import pick_device, seed_training_rngs

T = 7
THETAS = np.linspace(0.0, 65.0, 30)
S1, S4 = 0, 3
CELL = 4
# 4x4 grid, row-major. Left hemisphere = columns 0 and 1.
LEFT_CELLS = (0, 1, 4, 5, 8, 9, 12, 13)
RIGHT_CELLS = (2, 3, 6, 7, 10, 11, 14, 15)
assert S1 in LEFT_CELLS and S4 in RIGHT_CELLS


def cell_slice(idx: int):
    r, c = divmod(idx, 4)
    return slice(r * CELL, (r + 1) * CELL), slice(c * CELL, (c + 1) * CELL)


def spatial_keep_mask(map_size: int, device, dtype, silenced):
    m = torch.ones(1, 1, map_size, map_size, device=device, dtype=dtype)
    for idx in silenced:
        rs, cs = cell_slice(idx)
        m[:, :, rs, cs] = 0.0
    return m


def build_model(ckpt: dict, device) -> KDAConvMemoryModel:
    model = KDAConvMemoryModel(
        n_channels=ckpt["n_channels"], proto_dim=ckpt["proto_dim"],
        map_size=ckpt["map_size"], memory_noise_std=0.05,
        frame_window=ckpt.get("frame_window", 1),
        frame_stride=ckpt.get("frame_stride", 1),
        mem_every=ckpt.get("mem_every", 1),
        accum_mode=ckpt["accum_mode"], accum_decay=ckpt["accum_decay"],
        kda_heads=ckpt["kda_heads"], kda_head_dim=ckpt["kda_head_dim"],
    ).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    return model


def lesion_acc(ACC: torch.Tensor, keep_flat: torch.Tensor) -> torch.Tensor:
    """Zero silenced pixels in EMA/gated (B,C,H,W) or KDA (B,h,dk,dv,P) state."""
    if ACC.dim() == 4:
        return ACC * keep_flat.view(1, 1, ACC.shape[-2], ACC.shape[-1])
    if ACC.dim() == 5:
        return ACC * keep_flat.view(1, 1, 1, 1, -1)
    raise ValueError(f"unexpected ACC rank {ACC.dim()}")


def forward_seq_lesion(model, obs, keep):
    """forward_seq with left-hemisphere map patches zeroed every step."""
    B, Tt = obs.shape[:2]
    W, S = model.frame_window, model.frame_stride
    ends = list(range(W - 1, Tt, S))
    if ends[-1] != Tt - 1:
        ends.append(Tt - 1)
    H1, H2, ACC = model.init_state(B, obs.device, obs.dtype)
    keep_flat = keep.reshape(-1)
    Rs = []
    for k, e in enumerate(ends):
        win = obs[:, e - W + 1: e + 1]
        x = win.permute(0, 1, 4, 2, 3).flatten(1, 2).contiguous()
        X_t = model.stem(x) * keep
        ACC, acc_read, _ = model._accumulate(X_t, H1, ACC)
        ACC = lesion_acc(ACC, keep_flat)
        acc_read = acc_read * keep
        Xin = torch.cat([X_t, acc_read], dim=1)
        Z, att_vis = model.vision(Xin, H1, H2)
        Z = Z * keep
        att_vis = att_vis * keep
        if (k + 1) % model.mem_every == 0:
            H1, H2 = model.memory(Z, H1)
            H1 = H1 * keep
            H2 = H2 * keep
        R = torch.cat([H1, H2, Z, att_vis], dim=1)
        Rs.append(R)
    return torch.stack(Rs, dim=1)


def make_trials(env, n, theta, change_true, change_index):
    obs_list = []
    for _ in range(n):
        env.reset()
        env.cue_index = 0
        env.cue_color = "red"
        env.proportion = 1.0
        env.change_true = int(change_true)
        if change_true:
            env.change_index = int(change_index)
            env.orientation_change = float(theta) * float(np.random.choice([-1.0, 1.0]))
        frames = [env.step(0)[0] for _ in range(T)]
        obs_list.append(np.stack(frames))
    return torch.from_numpy(np.stack(obs_list)).float()


def thresh_deg(thetas, counts, n_trials, fa):
    """First |Δθ| that reaches FA + 50% of remaining headroom (atlas convention)."""
    bar = fa * n_trials + 0.5 * (n_trials - fa * n_trials)
    above = thetas[np.asarray(counts) >= bar]
    return float(above[0]) if len(above) else float("nan")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("checkpoint")
    ap.add_argument("out_dir")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--n-trials", type=int, default=100)
    ap.add_argument("--n-theta", type=int, default=30)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    seed_training_rngs(0)
    device = pick_device(args.device)

    thetas = THETAS if args.n_theta == 30 else np.linspace(0.0, 65.0, args.n_theta)
    ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    assert ckpt["accum_mode"] == "kda"
    model = build_model(ckpt, device)
    keep = spatial_keep_mask(model.map_size, device, torch.float32, LEFT_CELLS)

    env = make_env("vda16", T=T, frame_repeat=1, min_change_time=5, max_change_time=5,
                   noise_multiplier=5.0, curriculum=False, theta=65.0)

    counts_lesion = np.zeros(len(thetas), dtype=np.int64)
    counts_lesion_valid = np.zeros(len(thetas), dtype=np.int64)
    with torch.no_grad():
        for ti, theta in enumerate(thetas):
            obs = make_trials(env, args.n_trials, theta, 1, S4).to(device)
            R = forward_seq_lesion(model, obs, keep)
            counts_lesion[ti] = int((model.classify(R[:, -1]).argmax(-1) == 1).sum().item())
            obs_v = make_trials(env, args.n_trials, theta, 1, S1).to(device)
            Rv = forward_seq_lesion(model, obs_v, keep)
            counts_lesion_valid[ti] = int((model.classify(Rv[:, -1]).argmax(-1) == 1).sum().item())
            print(f"[hemilesion] θ={theta:5.1f}  invalid+L-lesion "
                  f"{counts_lesion[ti]:3d}/{args.n_trials}  "
                  f"valid+L-lesion {counts_lesion_valid[ti]:3d}/{args.n_trials}",
                  flush=True)
        obs_fa = make_trials(env, 2 * args.n_trials, 0.0, 0, -1).to(device)
        Rfa = forward_seq_lesion(model, obs_fa, keep)
        fa_lesion = int((model.classify(Rfa[:, -1]).argmax(-1) == 1).sum().item())
    print(f"[hemilesion] no-change + left lesion FA: {fa_lesion}/{2 * args.n_trials}")

    ref_path = os.path.join(os.path.dirname(os.path.abspath(args.out_dir)),
                            "psychometric", "psychometric_kda.json")
    ah1_path = os.path.join(os.path.dirname(os.path.abspath(args.out_dir)),
                            "microstim_s4_ah1", "microstim_kda.json")
    ref = json.load(open(ref_path)) if os.path.exists(ref_path) else None
    ah1 = json.load(open(ah1_path)) if os.path.exists(ah1_path) else None

    n = args.n_trials
    fa_ref = (ref["counts_pinned_s1"][0][0] / ref["n_trials"]) if ref else fa_lesion / (2 * n)
    t_les = thresh_deg(thetas, counts_lesion, n, fa_lesion / (2 * n))
    t_les_v = thresh_deg(thetas, counts_lesion_valid, n, fa_lesion / (2 * n))
    t_v = t_i = t_ah1 = float("nan")
    if ref:
        t_v = thresh_deg(np.array(ref["thetas"]), ref["counts_pinned_s1"][0],
                         ref["n_trials"], fa_ref)
        t_i = thresh_deg(np.array(ref["thetas"]), ref["counts_pinned_s4"][0],
                         ref["n_trials"], fa_ref)
    if ah1:
        t_ah1 = thresh_deg(np.array(ah1["thetas"]), ah1["counts_stim_invalid"],
                           ah1["n_trials"], fa_ref)

    summary = {
        "thetas": thetas.tolist(),
        "left_cells": list(LEFT_CELLS),
        "right_cells": list(RIGHT_CELLS),
        "counts_invalid_left_lesion": counts_lesion.tolist(),
        "counts_valid_left_lesion": counts_lesion_valid.tolist(),
        "fa_lesion": fa_lesion,
        "n_trials": n,
        "thresholds_deg": {
            "valid_no_lesion": t_v,
            "invalid_no_lesion": t_i,
            "invalid_left_lesion": t_les,
            "valid_left_lesion": t_les_v,
            "invalid_ah1_s4_stim": t_ah1,
        },
        "asymptote": {
            "invalid_left_lesion": float(counts_lesion[-5:].mean() / n),
            "valid_left_lesion": float(counts_lesion_valid[-5:].mean() / n),
        },
    }
    np.savez(os.path.join(args.out_dir, "hemilesion_kda.npz"),
             thetas=thetas, counts_invalid_left_lesion=counts_lesion,
             counts_valid_left_lesion=counts_lesion_valid,
             fa_lesion=fa_lesion, n_trials=n)
    with open(os.path.join(args.out_dir, "hemilesion_kda.json"), "w") as f:
        json.dump(summary, f, indent=2)

    fig, ax = plt.subplots(figsize=(8, 5.2))
    if ref:
        ax.plot(ref["thetas"], np.array(ref["counts_pinned_s1"][0]), marker="o", ms=3,
                lw=1.5, color="tab:green",
                label=f"valid (cue S1, change S1)  thr={t_v:.1f}°")
        ax.plot(ref["thetas"], np.array(ref["counts_pinned_s4"][0]), marker="s", ms=3,
                lw=1.5, color="tab:red",
                label=f"invalid (cue S1, change S4)  thr={t_i:.1f}°")
    if ah1:
        ax.plot(ah1["thetas"], np.array(ah1["counts_stim_invalid"]), marker="^", ms=3,
                lw=1.2, color="tab:purple", alpha=0.85,
                label=f"invalid + A_H1[S4]:=1  thr={t_ah1:.1f}°")
    ax.plot(thetas, counts_lesion, marker="D", ms=4, lw=1.8, color="tab:blue",
            label=f"invalid + left-8 lesion  thr={t_les:.1f}°")
    ax.plot(thetas, counts_lesion_valid, marker="x", ms=4, lw=1.2, color="tab:orange",
            label=f"valid + left-8 lesion (S1 silenced)  thr={t_les_v:.1f}°")
    ax.axhline(fa_lesion / 2.0, color="tab:blue", ls=":", lw=1.0,
               label=f"left-lesion FA floor ({fa_lesion}/{2 * n})")
    ax.set_xlabel("change magnitude |Δθ| (degrees)")
    ax.set_ylabel(f'"change" declarations (out of {n})')
    ax.set_title("VDA16 KDA seed-0 — left-hemisphere lesion\n"
                 "cue S1 100%, change S4; left 8 cells (incl. S1) zeroed every step")
    ax.set_ylim(0, n + 4)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    out_png = os.path.join(args.out_dir, "hemilesion_kda_psychometric.png")
    fig.savefig(out_png, dpi=140)
    plt.close(fig)
    print(f"[hemilesion] saved {out_png}")
    print(f"[hemilesion] thresholds: valid={t_v:.1f} invalid={t_i:.1f} "
          f"invalid+L-lesion={t_les:.1f} valid+L-lesion={t_les_v:.1f} "
          f"A_H1[S4]={t_ah1:.1f}")
    print("[hemilesion] DONE")


if __name__ == "__main__":
    main()
