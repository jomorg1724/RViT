"""Microstimulation of the visual-attention readout (att_vis) — KDA model, VDA16.

Intervention: during every step of the recurrent rollout, clamp the S1 block
(4x4 px, top-left cell of the 4x4 stimulus grid on the 16x16 map) of the
att_vis channel block of R to 1.0. R = [H1 || H2 || Z || att_vis], so att_vis
is channels 3C:4C. att_vis feeds ONLY the heads' readout (the recurrence
consumes Z), so this is a pure readout-level stimulation: it tests whether
the classifier's "change" decision is gated by the strength of the
visual-attention channel at the cued location.

Blocks (cue on S1, proportion 1.0, change pinned at S4 unless stated):
  stim_invalid    — change at S4 (invalid) + S1 att_vis clamp. THE test.
  stim_nochange   — no change + clamp. Decisive control: if the clamp alone
                    drives "change" declarations, recovery is an artifact.
  nostim_natural  — diagnostic: natural att_vis magnitude at S1/S4 on invalid
                    trials (is 1.0 actually a boost?).

Comparison curves already on disk (psychometric_kda.json): valid (change S1)
and invalid (change S4) without stimulation.

Usage:
  python psychometric_kda_microstim.py <checkpoint> <out_dir> [--device cuda]
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
STIM_VALUE = 1.0
CELL = 4  # 4x4 px per stimulus cell on the 16x16 map


def cell_slice(idx: int):
    r, c = divmod(idx, 4)
    return slice(r * CELL, (r + 1) * CELL), slice(c * CELL, (c + 1) * CELL)


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


def forward_seq_stim(model, obs, stim_cell=None, target="att_vis",
                     t_start=None, t_end=None):
    """forward_seq with a per-step clamp at stim_cell.

    t_start/t_end: inclusive step indices to apply the clamp (None = whole trial).

    target="att_vis": clamp the att_vis block of R (channels 3C:4C) to 1.0 —
        readout-only (att_vis feeds only the heads).
    target="ah1": clamp the memory gate A_H1 to 1.0 (A_Z to 0.0) at stim_cell.
    target="az":   clamp the memory gate A_Z to 1.0 (A_H1 to 0.0) — the mirror
        regime of ah1.
    target="ah":   clamp the VISION gate A_H to 1.0 (A_X to 0.0) at stim_cell —
        vision readout at the cell comes entirely from V_H(H2), none from V_X.
    The gate targets recompute their block exactly with the overridden gates,
    so the intervention propagates through the recurrence.
    """
    C = model.n_channels
    B, Tt = obs.shape[:2]
    t0 = 0 if t_start is None else int(t_start)
    t1 = Tt - 1 if t_end is None else int(t_end)
    H1, H2, ACC = model.init_state(B, obs.device, obs.dtype)
    Rs = []
    for k in range(Tt):
        stim_now = stim_cell is not None and (t0 <= k <= t1)
        x = obs[:, k].permute(0, 3, 1, 2).contiguous()
        X_t = model.stem(x)
        ACC, acc_read, _ = model._accumulate(X_t, H1, ACC)
        Xin = torch.cat([X_t, acc_read], dim=1)
        if target == "ah" and stim_now:
            vis = model.vision
            Q = vis.W_q(Xin)
            Sx = (Q * vis.W_kx(Xin)).sum(dim=1, keepdim=True) * vis.scale
            Sh = (Q * vis.W_kh(H1)).sum(dim=1, keepdim=True) * vis.scale
            A = torch.softmax(torch.cat([Sx, Sh], dim=1), dim=1)
            rs, cs = cell_slice(stim_cell)
            A = A.clone()
            A[:, 1:2, rs, cs] = 1.0
            A[:, 0:1, rs, cs] = 0.0
            att_vis = A[:, 0:1] * vis.W_vx(Xin) + A[:, 1:2] * vis.W_vh(H2)
            att_vis = vis.ffn(att_vis)
            Z = vis.proj(vis.se(torch.cat([Xin, att_vis], dim=1)))
        else:
            Z, att_vis = model.vision(Xin, H1, H2)
        if (k + 1) % model.mem_every == 0:
            if target in ("ah1", "az") and stim_now:
                mem = model.memory
                Q = mem.W_q(H1)
                Sz = (Q * mem.W_kz(Z)).sum(dim=1, keepdim=True) * mem.scale
                Sh = (Q * mem.W_kh(H1)).sum(dim=1, keepdim=True) * mem.scale
                A = torch.softmax(torch.cat([Sz, Sh], dim=1), dim=1)
                rs, cs = cell_slice(stim_cell)
                A = A.clone()
                if target == "ah1":
                    A[:, 1:2, rs, cs] = 1.0
                    A[:, 0:1, rs, cs] = 0.0
                else:  # az
                    A[:, 0:1, rs, cs] = 1.0
                    A[:, 1:2, rs, cs] = 0.0
                att = A[:, 0:1] * mem.W_vz(Z) + A[:, 1:2] * mem.W_vh(H1)
                att = mem.ffn(att)
                H1_new = mem.proj(mem.se(torch.cat([H1, att], dim=1)))
                if mem.memory_noise_std > 0.0:
                    H1_new = H1_new + mem.memory_noise_std * torch.randn_like(H1_new)
                H1, H2 = H1_new, att
            else:
                H1, H2 = model.memory(Z, H1)
        R = torch.cat([H1, H2, Z, att_vis], dim=1)
        if target == "att_vis" and stim_now:
            rs, cs = cell_slice(stim_cell)
            R = R.clone()
            R[:, 3 * C: 4 * C, rs, cs] = STIM_VALUE
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("checkpoint")
    ap.add_argument("out_dir")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--n-trials", type=int, default=100)
    ap.add_argument("--n-theta", type=int, default=30)
    ap.add_argument("--target", choices=["att_vis", "ah1", "az", "ah"], default="att_vis",
                    help="what to clamp: att_vis readout channel (readout-only) or "
                         "the A_H1 memory gate (propagates through recurrence)")
    ap.add_argument("--stim-cell", type=int, default=S4,
                    help="cell to clamp att_vis to 1.0 (default S4 = the uncued change "
                         "location on invalid trials; S1 = cued cell)")
    ap.add_argument("--t-start", type=int, default=None,
                    help="first step index to clamp (inclusive). Default: whole trial.")
    ap.add_argument("--t-end", type=int, default=None,
                    help="last step index to clamp (inclusive). Default: whole trial.")
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    seed_training_rngs(0)
    device = pick_device(args.device)

    thetas = THETAS if args.n_theta == 30 else np.linspace(0.0, 65.0, args.n_theta)
    ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    assert ckpt["accum_mode"] == "kda"
    model = build_model(ckpt, device)
    C = model.n_channels

    env = make_env("vda16", T=T, frame_repeat=1, min_change_time=5, max_change_time=5,
                   noise_multiplier=5.0, curriculum=False, theta=65.0)

    # ---- diagnostic: natural att_vis magnitudes on invalid trials ----
    with torch.no_grad():
        obs = make_trials(env, 20, 45.0, 1, S4).to(device)
        R = model.forward_seq(obs)
        av = R[:, -1, 3 * C: 4 * C]                      # att_vis at decision time
        s1r, s1c = cell_slice(S1)
        s4r, s4c = cell_slice(S4)
        s1m = av[:, :, s1r, s1c].mean().item()
        s4m = av[:, :, s4r, s4c].mean().item()
        gm = av.mean().item()
        gmax = av.abs().max().item()
    print(f"[microstim] natural att_vis@last (invalid trials): "
          f"S1={s1m:.3f} S4={s4m:.3f} global={gm:.3f} |max|={gmax:.3f} "
          f"-> stim value {STIM_VALUE} is {'a boost' if STIM_VALUE > abs(s1m) else 'NOT a boost'}")

    # ---- Block 1: invalid + stim (THE test) ----
    counts_stim = np.zeros(len(thetas), dtype=np.int64)
    # ---- Block 2: no-change + stim (FA control) ----
    fa_stim = 0
    with torch.no_grad():
        for ti, theta in enumerate(thetas):
            obs = make_trials(env, args.n_trials, theta, 1, S4).to(device)
            R = forward_seq_stim(model, obs, stim_cell=args.stim_cell, target=args.target,
                                 t_start=args.t_start, t_end=args.t_end)
            logits = model.classify(R[:, -1])
            counts_stim[ti] = int((logits.argmax(-1) == 1).sum().item())
            print(f"[microstim] stim+invalid theta={theta:.1f}: {counts_stim[ti]}/{args.n_trials}",
                  flush=True)
        obs = make_trials(env, 2 * args.n_trials, 0.0, 0, -1).to(device)
        R = forward_seq_stim(model, obs, stim_cell=args.stim_cell, target=args.target,
                             t_start=args.t_start, t_end=args.t_end)
        logits = model.classify(R[:, -1])
        fa_stim = int((logits.argmax(-1) == 1).sum().item())
    print(f"[microstim] no-change + stim FA: {fa_stim}/{2 * args.n_trials}")

    np.savez(os.path.join(args.out_dir, "microstim_kda.npz"),
             thetas=thetas, counts_stim_invalid=counts_stim,
             fa_stim=fa_stim, n_trials=args.n_trials,
             natural_attvis=dict(S1=s1m, S4=s4m, global_mean=gm, abs_max=gmax))
    with open(os.path.join(args.out_dir, "microstim_kda.json"), "w") as f:
        json.dump({"thetas": thetas.tolist(), "counts_stim_invalid": counts_stim.tolist(),
                   "fa_stim": fa_stim, "n_trials": args.n_trials,
                   "target": args.target, "stim_cell": args.stim_cell,
                   "t_start": args.t_start, "t_end": args.t_end,
                   "natural_attvis": {"S1": s1m, "S4": s4m, "global_mean": gm,
                                      "abs_max": gmax}}, f, indent=2)

    window = ("whole trial" if args.t_start is None and args.t_end is None
              else f"t={args.t_start}→{args.t_end}")
    # ---- comparison figure against the no-stim valid/invalid curves ----
    ref_path = os.path.join(os.path.dirname(os.path.abspath(args.out_dir)),
                            "psychometric", "psychometric_kda.json")
    whole_path = os.path.join(os.path.dirname(os.path.abspath(args.out_dir)),
                              "microstim_s4_ah1", "microstim_kda.json")
    fig, ax = plt.subplots(figsize=(7.5, 5))
    if os.path.exists(ref_path):
        ref = json.load(open(ref_path))
        ax.plot(ref["thetas"], np.array(ref["counts_pinned_s1"][0]), marker="o", ms=3,
                lw=1.4, color="tab:green", label="valid (cue S1, change S1), no stim")
        ax.plot(ref["thetas"], np.array(ref["counts_pinned_s4"][0]), marker="s", ms=3,
                lw=1.4, color="tab:red", label="invalid (change S4), no stim")
    if os.path.exists(whole_path) and (args.t_start is not None or args.t_end is not None):
        whole = json.load(open(whole_path))
        ax.plot(whole["thetas"], np.array(whole["counts_stim_invalid"]), marker="^", ms=3,
                lw=1.2, color="tab:purple", alpha=0.85,
                label=f"invalid + {args.target}[S{args.stim_cell + 1}]:=1 whole trial")
    ax.plot(thetas, counts_stim, marker="D", ms=3.5, lw=1.6, color="tab:blue",
            label=f"invalid + {args.target}[S{args.stim_cell + 1}]:=1 {window}")
    ax.axhline(fa_stim / 2.0, color="tab:blue", ls=":", lw=1.0,
               label=f"windowed stim FA floor ({fa_stim}/{2 * args.n_trials})")
    ax.set_xlabel("change magnitude |Δθ| (degrees)")
    ax.set_ylabel(f'"change" declarations (out of {args.n_trials})')
    ax.set_title(f"Microstimulation of {args.target} at cell S{args.stim_cell + 1} ({window})\n"
                 "does it rescue detection of an uncued change at S4?")
    ax.set_ylim(0, args.n_trials + 4)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    out_png = os.path.join(args.out_dir, "microstim_kda_valid_vs_invalid_stim.png")
    fig.savefig(out_png, dpi=140)
    plt.close(fig)
    print(f"[microstim] saved {out_png}")
    print("[microstim] DONE")


if __name__ == "__main__":
    main()
