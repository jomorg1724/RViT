"""Stimulus-space attention maps for the token-attention KDA trunk.

The raw attention matrix at each block is (H*W) x (H*W) per stream
(256 x 256 at H=W=16): rows are query positions, columns are key
positions. To project attention back onto the visual scene we sum down
the columns over all rows (queries) and divide by H*W, leaving a 1x256
"attention received" vector per stream, reshaped to the 16x16 stimulus
grid. Every element lies in [0, 1]; each stream map sums to the average
mass that stream receives.

Four maps per step:
  vision block:  A_X (input-stream keys),  A_H (memory-stream keys)
  memory block:  A_Z (current-obs keys),   A_H1 (persistent-state keys)

Conditions (cue pinned at S1, proportion 1.0, theta = change magnitude):
  nochange, changeS1 (valid), changeS4 (invalid).

Usage:
  python attn_colsum_maps.py --checkpoint ckpt.pt --out-dir DIR \
      [--theta 55] [--trials 200] [--device cuda]
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import torch

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from kda_conv_memory_model import KDAConvMemoryModel, _nchw_to_tokens
from envs import make_env
from train_rl import pick_device, seed_training_rngs

T = 7
MAP = 16
CELL = 4                       # 4x4 map pixels per stimulus cell (100px img -> 16px map)
S_TL, S_BR = 0, 15             # top-left / bottom-right of the 4x4 stimulus grid
CHANGE_CONDS = [("nochange", 0, -1), ("changeTL", 1, S_TL), ("changeBR", 1, S_BR)]

# 16x16 map -> 4x4 grid of 4x4-pixel cells; cell idx -> (row0, col0)
def cell_origin(idx: int) -> tuple[int, int]:
    return (idx // 4) * CELL, (idx % 4) * CELL


def raw_A(Q, Kx, Kh, scale, split=False, mode=""):
    """Token-mode raw attention per stream. joint: one softmax over [Sx|Sh]
    (streams compete). split: softmax each stream separately (each sums to 1)."""
    q, H, W = _nchw_to_tokens(Q)
    kx, _, _ = _nchw_to_tokens(Kx)
    kh, _, _ = _nchw_to_tokens(Kh)
    q, kx, kh = q.float(), kx.float(), kh.float()
    Sx = torch.matmul(q, kx.transpose(-2, -1)) * scale
    Sh = torch.matmul(q, kh.transpose(-2, -1)) * scale
    if split:
        Ax, Ah = torch.softmax(Sx, dim=-1), torch.softmax(Sh, dim=-1)
        if mode == "colgate":
            g = torch.softmax(torch.stack([Ax.sum(1), Ah.sum(1)], dim=-1) / 0.5, dim=-1)
            Ax, Ah = Ax * g[..., 0:1], Ah * g[..., 1:2]
        return Ax, Ah
    A = torch.softmax(torch.cat([Sx, Sh], dim=-1), dim=-1)  # (B,N,2N)
    N = H * W
    return A[..., :N], A[..., N:]


def colsum_map(A: torch.Tensor) -> np.ndarray:
    """Sum over query rows, divide by N, reshape to (MAP, MAP)."""
    N = A.shape[-1]
    v = A.sum(dim=-2)[0] / N          # (N,) attention received per key position
    return v.view(MAP, MAP).cpu().numpy()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--theta", type=float, default=55.0, help="change magnitude (deg)")
    ap.add_argument("--trials", type=int, default=200)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    seed_training_rngs(0)
    device = pick_device(args.device)

    ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    assert ckpt["accum_mode"] == "kda"
    attn_mode = ckpt.get("attn_mode", "pixel_gate")
    assert attn_mode == "token", f"column-sum maps are defined for token attention, got {attn_mode}"
    model = KDAConvMemoryModel(
        n_channels=ckpt["n_channels"], proto_dim=ckpt["proto_dim"],
        map_size=ckpt["map_size"],
        memory_noise_std=0.05,
        frame_window=ckpt.get("frame_window", 1),
        frame_stride=ckpt.get("frame_stride", 1),
        mem_every=ckpt.get("mem_every", 1),
        accum_mode=ckpt["accum_mode"], accum_decay=ckpt["accum_decay"],
        kda_heads=ckpt["kda_heads"], kda_head_dim=ckpt["kda_head_dim"],
        attn_mode=attn_mode,
        readout=ckpt.get("readout", "full"),
        cls_head=ckpt.get("cls_head", "pool"),
        v_mode=ckpt.get("v_mode", "state"),
        softmax_mode=ckpt.get("softmax_mode", "joint"),
    ).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    env = make_env("vda16", T=T, frame_repeat=1, min_change_time=5, max_change_time=5,
                   noise_multiplier=5.0, curriculum=False, theta=args.theta)

    keys = ("Ax", "Ah", "Az", "Ah1")
    akeys = ("acc_decay", "acc_write", "acc_gate", "acc_surprise")
    NC = len(CHANGE_CONDS)
    N = MAP * MAP
    maps = {k: np.zeros((NC, T, MAP, MAP), dtype=np.float64) for k in keys}
    raw = {k: np.zeros((NC, T, N, N), dtype=np.float64) for k in keys}
    amaps = {k: np.zeros((NC, T, MAP, MAP), dtype=np.float64) for k in akeys}
    mem_every = ckpt.get("mem_every", 1)
    v_mode = ckpt.get("v_mode", "state")
    smode = ckpt.get("softmax_mode", "joint")
    split = smode in ("split", "colgate")
    accum = model.accumulator

    def accum_gate_maps(X_t, H1, ACC_pre):
        """Accumulator 'attention': per-pixel gate fields + surprise, each (MAP,MAP).

        a = decay (h*dk -> mean), b = write (h -> mean), g = readout gate
        (h*dv -> mean), surprise = ||v - (a*S)^T k|| per pixel (mean over h).
        Mirrors KDAVisualAccumulator.forward against the PRE-update state.
        """
        B, _, H, W = X_t.shape
        h, dk, dv, P = accum.h, accum.dk, accum.dv, H * W
        inp = torch.cat([X_t, H1], dim=1)
        def shp(t):
            return t.view(B, h, -1, P)
        k = torch.nn.functional.normalize(shp(accum.W_k(inp)).float(), dim=2)
        v = shp(accum.W_v(inp)).float()
        a = torch.sigmoid(accum.W_a(inp)).view(B, h, dk, 1, P).float()
        b = torch.sigmoid(accum.W_b(inp)).view(B, h, 1, 1, P).float()
        g = torch.sigmoid(accum.W_g(inp)).view(B, h, dv, P).float()
        S_dec = a * ACC_pre.float()
        v_hat = torch.einsum("bhikp,bhip->bhkp", S_dec, k)
        err = (v - v_hat).norm(dim=2)                 # (B,h,P)
        am = a.mean(dim=(1, 2)).view(B, H, W)         # (B,H,W)
        bm = b.mean(dim=1).view(B, H, W)
        gm = g.mean(dim=(1, 2)).view(B, H, W)
        em = err.mean(dim=1).view(B, H, W)
        return (am[0].cpu().numpy(), bm[0].cpu().numpy(),
                gm[0].cpu().numpy(), em[0].cpu().numpy())

    print(f"[colsum] cue S1 @100%, theta={args.theta}, {args.trials} trials x {NC} conditions")
    with torch.no_grad():
        for ci, (name, change, cidx) in enumerate(CHANGE_CONDS):
            for _ in range(args.trials):
                obs0 = env.reset()
                env.cue_index = 0
                env.cue_color = "red"
                env.proportion = 1.0
                env.change_true = int(change)
                if change:
                    env.change_index = int(cidx)
                frames = [obs0] + [env.step(0)[0] for _ in range(T - 1)]
                obs = torch.from_numpy(np.stack(frames)).unsqueeze(0).float().to(device)
                H1, H2, ACC = model.init_state(1, device, obs.dtype)
                for t in range(T):
                    frame = obs[:, t].permute(0, 3, 1, 2).contiguous()
                    X_t = model.stem(frame)
                    ga, gb, gg, ge = accum_gate_maps(X_t, H1, ACC)
                    amaps["acc_decay"][ci, t] += ga
                    amaps["acc_write"][ci, t] += gb
                    amaps["acc_gate"][ci, t] += gg
                    amaps["acc_surprise"][ci, t] += ge
                    ACC, acc_read, _ = model._accumulate(X_t, H1, ACC)
                    Xin = torch.cat([X_t, acc_read], dim=1)

                    # --- vision block: raw A over [X | H] key streams ---
                    Z, att = model.vision(Xin, H1, H2)
                    Ax, Ah = raw_A(model.vision.W_q(Xin), model.vision.W_kx(Xin),
                                   model.vision.W_kh(H1), model.vision.scale, split=split,
                                   mode=smode)
                    maps["Ax"][ci, t] += colsum_map(Ax)
                    maps["Ah"][ci, t] += colsum_map(Ah)
                    raw["Ax"][ci, t] += Ax[0].cpu().numpy()
                    raw["Ah"][ci, t] += Ah[0].cpu().numpy()

                    # --- memory block: raw A over [Z | H1] key streams ---
                    if model.memory is not None:
                        mem = model.memory
                        Az, Ah1 = raw_A(mem.W_q(H1), mem.W_kz(Z), mem.W_kh(H1), mem.scale,
                                        split=split, mode=smode)
                        maps["Az"][ci, t] += colsum_map(Az)
                        maps["Ah1"][ci, t] += colsum_map(Ah1)
                        raw["Az"][ci, t] += Az[0].cpu().numpy()
                        raw["Ah1"][ci, t] += Ah1[0].cpu().numpy()

                    # --- mirror step() exactly: cadence + v_mode branch ---
                    update_memory = ((t + 1) % mem_every == 0)
                    if v_mode == "learned":
                        H2 = att
                        if update_memory:
                            H1, _ = model.memory(Z, H1)
                    elif v_mode == "learned_z":
                        H2 = att
                        H1 = Z
                        if model.memory_noise_std > 0.0:
                            H1 = H1 + model.memory_noise_std * torch.randn_like(H1)
                    elif v_mode == "learned_mem":
                        # vision already used H1 as value source in the model's
                        # step(); here Z/att came from model.vision(Xin, H1, H2)
                        # with H2 ignored only when learned_v. For learned_mem the
                        # vision block uses H1 for V_h, so recompute faithfully:
                        Z, att = model.vision(Xin, H1, H1)
                        H1_new, att_mem = model.memory(Z, H1)
                        H2 = att_mem
                        if update_memory:
                            H1 = H1_new
                    else:
                        if update_memory:
                            H1, H2 = model.memory(Z, H1)
            print(f"[colsum]   {name}: done", flush=True)

    for k in keys:
        maps[k] /= args.trials
        raw[k] /= args.trials
    for k in akeys:
        amaps[k] /= args.trials
    np.savez(os.path.join(args.out_dir, "attn_colsum_maps.npz"),
             conditions=np.array([c[0] for c in CHANGE_CONDS]),
             theta=np.array([args.theta]),
             **{k: maps[k] for k in keys},
             **{f"raw_{k}": raw[k] for k in keys},
             **{k: amaps[k] for k in akeys})

    row_labels = {"Ax": r"$A_X$ received (vision: input keys)",
                  "Ah": r"$A_H$ received (vision: memory keys)",
                  "Az": r"$A_Z$ received (memory: obs keys)",
                  "Ah1": r"$A_{H1}$ received (memory: persistent keys)"}
    cue_r0, cue_c0 = cell_origin(S_TL)

    def fmt_cbar(fig, im, cax):
        cb = fig.colorbar(im, cax=cax, format="%.2f", ticks=[0.0, 0.25, 0.5, 0.75, 1.0])
        cb.ax.tick_params(labelsize=11)
        return cb

    ch_names = {"nochange": "no change", "changeTL": f"change @top-left (+{args.theta:.0f}°, valid)",
                "changeBR": f"change @bottom-right (+{args.theta:.0f}°, invalid)"}

    # ---- figure set 1: column-sum maps projected to the 16x16 scene ----
    for ci, (name, change, cidx) in enumerate(CHANGE_CONDS):
        fig = plt.figure(figsize=(2.0 * T + 1.2, 2.4 * len(keys)))
        gs = fig.add_gridspec(len(keys), T + 1, width_ratios=[1.0] * T + [0.09],
                              wspace=0.05, hspace=0.15)
        for ri, k in enumerate(keys):
            norm = maps[k][ci] / max(float(maps[k][ci].max()), 1e-9)   # [0,1] per row
            im = None
            for t in range(T):
                ax = fig.add_subplot(gs[ri, t])
                im = ax.imshow(norm[t], vmin=0.0, vmax=1.0, cmap="viridis")
                ax.set_xticks([]); ax.set_yticks([])
                ax.add_patch(Rectangle((cue_c0 - 0.5, cue_r0 - 0.5), CELL, CELL,
                                       fill=False, edgecolor="red", lw=1.5))
                if change and cidx >= 0:
                    r0, c0 = cell_origin(cidx)
                    ax.add_patch(Rectangle((c0 - 0.5, r0 - 0.5), CELL, CELL,
                                           fill=False, edgecolor="cyan", lw=1.5, linestyle="--"))
                if ri == 0:
                    ax.set_title(f"t={t}", fontsize=11)
                if t == 0:
                    ax.set_ylabel(f"{row_labels[k]}\n[0, 1]", fontsize=9)
            fmt_cbar(fig, im, fig.add_subplot(gs[ri, T]))
        fig.suptitle(f"Column-sum attention received (16x16 scene) — cue top-left 100%, {ch_names[name]}",
                     fontsize=12)
        fig.subplots_adjust(left=0.14, right=0.94, top=0.93, bottom=0.02)
        out = os.path.join(args.out_dir, f"attn_colsum_cueTL_100p_{name}.png")
        fig.savefig(out, dpi=130, bbox_inches="tight")
        plt.close(fig)
        print(f"[colsum]   wrote {out}", flush=True)

    # ---- figure set 2: raw 256x256 attention matrices (rows=queries, cols=keys) ----
    for ci, (name, change, cidx) in enumerate(CHANGE_CONDS):
        fig = plt.figure(figsize=(2.0 * T + 1.2, 2.4 * len(keys)))
        gs = fig.add_gridspec(len(keys), T + 1, width_ratios=[1.0] * T + [0.09],
                              wspace=0.05, hspace=0.15)
        for ri, k in enumerate(keys):
            rnorm = raw[k][ci] / max(float(raw[k][ci].max()), 1e-9)   # [0,1] per row
            im = None
            for t in range(T):
                ax = fig.add_subplot(gs[ri, t])
                im = ax.imshow(rnorm[t], vmin=0.0, vmax=1.0, cmap="viridis",
                               interpolation="nearest")
                ax.set_xticks([]); ax.set_yticks([])
                # cue-cell band on both axes (keys = cols, queries = rows)
                ax.axvline(cue_c0 - 0.5, color="red", lw=0.8)
                ax.axvline(cue_c0 + CELL - 0.5, color="red", lw=0.8)
                ax.axhline(cue_r0 - 0.5, color="red", lw=0.8)
                ax.axhline(cue_r0 + CELL - 0.5, color="red", lw=0.8)
                if ri == 0:
                    ax.set_title(f"t={t}", fontsize=11)
                if t == 0:
                    ax.set_ylabel(f"{row_labels[k].replace('received', 'raw')}\n[0, 1]", fontsize=9)
            fmt_cbar(fig, im, fig.add_subplot(gs[ri, T]))
        fig.suptitle(f"Raw attention (256 queries x 256 keys) — cue top-left 100%, {ch_names[name]}",
                     fontsize=12)
        fig.subplots_adjust(left=0.14, right=0.94, top=0.93, bottom=0.02)
        out = os.path.join(args.out_dir, f"attn_raw_cueTL_100p_{name}.png")
        fig.savefig(out, dpi=130, bbox_inches="tight")
        plt.close(fig)
        print(f"[colsum]   wrote {out}", flush=True)

    # ---- figure set 3: accumulator gate fields (16x16, per step) ----
    arow_labels = {"acc_decay": "accum decay a",
                   "acc_write": "accum write b",
                   "acc_gate": "accum readout gate g",
                   "acc_surprise": "accum surprise ||v-v̂||"}
    for ci, (name, change, cidx) in enumerate(CHANGE_CONDS):
        fig = plt.figure(figsize=(2.0 * T + 1.2, 2.4 * len(akeys)))
        gs = fig.add_gridspec(len(akeys), T + 1, width_ratios=[1.0] * T + [0.09],
                              wspace=0.05, hspace=0.15)
        for ri, k in enumerate(akeys):
            anorm = amaps[k][ci] / max(float(amaps[k][ci].max()), 1e-9)   # [0,1] per row
            im = None
            for t in range(T):
                ax = fig.add_subplot(gs[ri, t])
                im = ax.imshow(anorm[t], vmin=0.0, vmax=1.0, cmap="viridis")
                ax.set_xticks([]); ax.set_yticks([])
                ax.add_patch(Rectangle((cue_c0 - 0.5, cue_r0 - 0.5), CELL, CELL,
                                       fill=False, edgecolor="red", lw=1.5))
                if change and cidx >= 0:
                    r0, c0 = cell_origin(cidx)
                    ax.add_patch(Rectangle((c0 - 0.5, r0 - 0.5), CELL, CELL,
                                           fill=False, edgecolor="cyan", lw=1.5, linestyle="--"))
                if ri == 0:
                    ax.set_title(f"t={t}", fontsize=11)
                if t == 0:
                    ax.set_ylabel(f"{arow_labels[k]}\n[0, 1]", fontsize=9)
            fmt_cbar(fig, im, fig.add_subplot(gs[ri, T]))
        fig.suptitle(f"KDA accumulator gate fields (16x16) — cue top-left 100%, {ch_names[name]}",
                     fontsize=12)
        fig.subplots_adjust(left=0.14, right=0.94, top=0.93, bottom=0.02)
        out = os.path.join(args.out_dir, f"attn_accum_cueTL_100p_{name}.png")
        fig.savefig(out, dpi=130, bbox_inches="tight")
        plt.close(fig)
        print(f"[colsum]   wrote {out}", flush=True)

    # print the cue/change-cell received attention for quick numeric read
    print("\n[colsum] mean received attention in cued cell (top-left, 4x4):")
    for ci, (name, change, cidx) in enumerate(CHANGE_CONDS):
        r = []
        for k in keys:
            cell = maps[k][ci, :, cue_r0:cue_r0 + CELL, cue_c0:cue_c0 + CELL].mean(axis=(1, 2))
            r.append(f"{k}: " + " ".join(f"{v:.4f}" for v in cell))
        print(f"  {name}: " + " | ".join(r))


if __name__ == "__main__":
    main()
