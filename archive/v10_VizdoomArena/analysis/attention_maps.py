"""
Attention interpretability suite for a trained V10 arena model.

Three things, all from one rollout pass with the labels buffer on:

  1. ATTENTION OVERLAYS — for the most enemy-visible frames, render the RGB
     frame with (a) each encoder layer's patch-position attention (averaged
     over heads and queries; patch + memory keys at the same grid position
     summed), and (b) the actor decoder's final-layer CLS attention over the
     H₁/H₂ token grids ("what the decision reads"). PNGs → --out-dir.

  2. ATTENTION-ON-ENEMIES METRIC — using ViZDoom's labels buffer (per-object
     bounding boxes), every frame with a visible monster contributes
        mass(enemy patches) / area(enemy patches)        (a ratio of 1.0 = no
     preference; >1 = attention concentrates on enemies). Reported per
     encoder layer and for the actor CLS readout, plus the key-GROUP
     decomposition (patch / H₁ / H₂ / vitals / weapon / last_action).

  3. CAUSAL PROBE (--causal) — at frames with visible monsters, re-run the
     SAME step from the SAME recurrent state with an additive pre-softmax
     bias ±β on the enemy-patch keys of every encoder layer, and measure the
     change in p(attack-family actions) and in V(s). Attention is steerable
     by construction (the bias rides the model's own attn_mask path); this
     quantifies how much the *policy* follows it.

Usage:
    .venv/bin/python v10_VizdoomArena/analysis/attention_maps.py \
        --checkpoint ~/rvit_plus_checkpoints/v10_vizdoom_arena/v10_latest.pt \
        --episodes 3 --max-steps 400 --causal
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import torch
from torch.distributions import Categorical

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from v10_VizdoomArena.env import OBS_H, OBS_W, VizdoomArenaEnv
from v10_VizdoomArena.model import V10ArenaModel

ATTACK_ACTIONS = (1, 3, 11, 12)     # any combo containing ATTACK


def _enemy_patch_mask(labels: list, grid_h: int, grid_w: int) -> np.ndarray:
    """Monster bboxes (already scaled to the 60×80 obs) → bool (grid_h, grid_w)
    mask of overlapped patches."""
    ph, pw = OBS_H // grid_h, OBS_W // grid_w
    mask = np.zeros((grid_h, grid_w), dtype=bool)
    for l in labels:
        if not l["is_monster"]:
            continue
        x0, y0 = l["x"], l["y"]
        x1, y1 = x0 + max(l["w"], 1.0), y0 + max(l["h"], 1.0)
        c0, c1 = int(np.clip(x0 // pw, 0, grid_w - 1)), int(np.clip((x1 - 1e-6) // pw, 0, grid_w - 1))
        r0, r1 = int(np.clip(y0 // ph, 0, grid_h - 1)), int(np.clip((y1 - 1e-6) // ph, 0, grid_h - 1))
        mask[r0:r1 + 1, c0:c1 + 1] = True
    return mask


def _grid_attention(attn_layer: torch.Tensor, layout: dict, grid_h: int, grid_w: int):
    """One encoder layer's attention (1, heads, N, n_keys) → dict:
    per-position map (grid) = patch+H keys at that position, summed; plus
    per-group scalar masses. Averaged over heads and queries."""
    a = attn_layer[0].mean(dim=0).mean(dim=0)          # (n_keys,)
    groups = {name: float(a[lo:hi].sum()) for name, (lo, hi) in layout.items()}
    grid = torch.zeros(grid_h * grid_w)
    for name, (lo, hi) in layout.items():
        if hi - lo == grid_h * grid_w:                 # patch-aligned spans
            grid = grid + a[lo:hi]
    return grid.reshape(grid_h, grid_w).numpy(), groups


def _cls_grids(actor_attn: list, token_layout: dict, grid_h: int, grid_w: int):
    """Actor decoder final-layer CLS row → one (grid_h, grid_w) map per H_k."""
    a = actor_attn[-1][0].mean(dim=0)[0]               # (S,) CLS query row
    out = {}
    for name, (lo, hi) in token_layout.items():
        if name.startswith("H"):
            out[name] = a[lo:hi].reshape(grid_h, grid_w).numpy()
    return out


def _ratio(att_grid: np.ndarray, mask: np.ndarray) -> float:
    """Attention concentration on masked patches: mass share / area share."""
    total = float(att_grid.sum())
    if total <= 0 or not mask.any():
        return float("nan")
    mass_share = float(att_grid[mask].sum()) / total
    area_share = float(mask.sum()) / mask.size
    return mass_share / area_share


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", default=os.path.expanduser(
        "~/rvit_plus_checkpoints/v10_vizdoom_arena/v10_latest.pt"))
    p.add_argument("--episodes", type=int, default=2)
    p.add_argument("--max-steps", type=int, default=400)
    p.add_argument("--n-figs", type=int, default=6)
    p.add_argument("--device", default="cpu")
    p.add_argument("--out-dir", default=os.path.join(_HERE, "figs"))
    p.add_argument("--causal", action="store_true")
    p.add_argument("--bias", type=float, default=3.0)
    p.add_argument("--seed", type=int, default=123)
    args = p.parse_args(argv)

    device = torch.device(args.device)
    ckpt = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model = V10ArenaModel(**ckpt["model_kwargs"]).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    gh, gw = model.patch_embed.grid_h, model.patch_embed.grid_w
    L = model.enc_layers
    enc_layouts = [model.encoder.key_layout(k) for k in range(L)]
    dec_layout = model.actor_head.token_layout()
    print(f"[load] iter={ckpt.get('iter')} env_steps={ckpt.get('env_steps')} "
          f"params={sum(q.numel() for q in model.parameters()):,}")

    env = VizdoomArenaEnv(enable_labels=True, seed=args.seed)
    os.makedirs(args.out_dir, exist_ok=True)

    ratios = {f"enc_L{k+1}": [] for k in range(L)}
    ratios["actor_cls"] = []
    group_mass = {f"enc_L{k+1}": {} for k in range(L)}
    causal_rows = []
    snapshots = []          # (enemy_area, frame_rgb, enc_grids, cls_grids, mask)

    with torch.no_grad():
        for _ep in range(args.episodes):
            obs, feats = env.reset()
            states = model.init_states(1, device=device)
            for _t in range(args.max_steps):
                x = torch.from_numpy(obs).to(device).float().div_(255.0).unsqueeze(0)
                f = torch.from_numpy(feats).to(device).unsqueeze(0)
                prev_states = ([h.clone() for h in states[0]],
                               [c.clone() for c in states[1]])
                out = model.rl_step(x, f, states, return_attn=True)
                states = out["new_states"]

                mask = _enemy_patch_mask(env.labels, gh, gw)
                enc_grids = []
                for k in range(L):
                    grid, groups = _grid_attention(out["enc_attn"][k].cpu(), enc_layouts[k], gh, gw)
                    enc_grids.append(grid)
                    for gname, gval in groups.items():
                        group_mass[f"enc_L{k+1}"].setdefault(gname, []).append(gval)
                    if mask.any():
                        ratios[f"enc_L{k+1}"].append(_ratio(grid, mask))
                cls_grids = _cls_grids([a.cpu() for a in out["actor_attn"]], dec_layout, gh, gw)
                if mask.any():
                    cls_mean = np.mean([g for g in cls_grids.values()], axis=0)
                    ratios["actor_cls"].append(_ratio(cls_mean, mask))
                    snapshots.append((float(mask.sum()), obs.copy(), enc_grids,
                                      cls_grids, mask.copy()))

                    # ── causal probe: ±β on enemy-patch keys, same state ────
                    if args.causal:
                        flat = torch.from_numpy(mask.reshape(-1)).bool()
                        p0 = torch.softmax(out["actor_logits"][0], -1)
                        row = {"p_attack_base": float(p0[list(ATTACK_ACTIONS)].sum()),
                               "V_base": float(out["V_scalar"][0])}
                        for sign, tag in ((+1.0, "boost"), (-1.0, "suppress")):
                            biases = []
                            for k in range(L):
                                bv = torch.zeros(model.encoder.n_keys_for(k), device=device)
                                for name, (lo, hi) in enc_layouts[k].items():
                                    if hi - lo == gh * gw:      # patch-aligned spans
                                        bv[lo:hi][flat] = sign * args.bias
                                biases.append(bv)
                            outb = model.rl_step(
                                x, f, prev_states, attn_bias={"enc": biases})
                            pb = torch.softmax(outb["actor_logits"][0], -1)
                            row[f"p_attack_{tag}"] = float(pb[list(ATTACK_ACTIONS)].sum())
                            row[f"V_{tag}"] = float(outb["V_scalar"][0])
                        causal_rows.append(row)

                a = int(Categorical(logits=out["actor_logits"][0]).sample().item())
                obs, feats, r, done, info = env.step(a)
                if done:
                    break
    env.close()

    # ── report ───────────────────────────────────────────────────────────────
    print("\n── attention-on-enemies (mass share / area share; 1.0 = no preference) ──")
    report = {}
    for k, vals in ratios.items():
        if vals:
            arr = np.array(vals)
            report[k] = {"mean": float(np.nanmean(arr)), "median": float(np.nanmedian(arr)),
                         "n_frames": int(len(arr))}
            print(f"  {k:10s}: mean {np.nanmean(arr):5.2f}  median {np.nanmedian(arr):5.2f}  "
                  f"(n={len(arr)} monster-visible frames)")
    print("\n── key-group attention decomposition (mean mass) ──")
    for lk, groups in group_mass.items():
        parts = "  ".join(f"{g}={np.mean(v):.3f}" for g, v in groups.items())
        print(f"  {lk}: {parts}")
        report[f"groups_{lk}"] = {g: float(np.mean(v)) for g, v in groups.items()}

    if causal_rows:
        print(f"\n── causal probe (±{args.bias} pre-softmax on enemy-patch keys, n={len(causal_rows)}) ──")
        for tag in ("boost", "suppress"):
            dp = np.mean([r[f"p_attack_{tag}"] - r["p_attack_base"] for r in causal_rows])
            dv = np.mean([r[f"V_{tag}"] - r["V_base"] for r in causal_rows])
            print(f"  {tag:9s}: Δp(attack) = {dp:+.4f}   ΔV = {dv:+.4f}")
            report[f"causal_{tag}"] = {"dp_attack": float(dp), "dV": float(dv)}

    with open(os.path.join(args.out_dir, "attention_report.json"), "w") as fjson:
        json.dump(report, fjson, indent=2)

    # ── overlay figures for the most enemy-visible frames ────────────────────
    if snapshots:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        snapshots.sort(key=lambda s: -s[0])
        for i, (_, frame, enc_grids, cls_grids, mask) in enumerate(snapshots[:args.n_figs]):
            n_panels = 1 + L + len(cls_grids)
            fig, axes = plt.subplots(1, n_panels, figsize=(3.2 * n_panels, 3.2))
            rgb = np.transpose(frame, (1, 2, 0))
            axes[0].imshow(rgb)
            ys, xs = np.where(mask)
            ph, pw = OBS_H // gh, OBS_W // gw
            for yy, xx in zip(ys, xs):
                axes[0].add_patch(plt.Rectangle((xx * pw, yy * ph), pw, ph,
                                                fill=False, edgecolor="red", lw=1.2))
            axes[0].set_title("frame (red = enemy patches)")
            panels = [(f"enc L{k+1}", enc_grids[k]) for k in range(L)]
            panels += [(f"actor CLS {n}", g) for n, g in sorted(cls_grids.items())]
            for ax, (name, grid) in zip(axes[1:], panels):
                ax.imshow(rgb, alpha=0.45)
                up = np.kron(grid, np.ones((ph, pw)))
                ax.imshow(up, cmap="inferno", alpha=0.55,
                          vmin=0.0, vmax=max(float(grid.max()), 1e-8))
                ax.set_title(name)
            for ax in axes:
                ax.set_xticks([]); ax.set_yticks([])
            fig.tight_layout()
            path = os.path.join(args.out_dir, f"attn_overlay_{i:02d}.png")
            fig.savefig(path, dpi=130)
            plt.close(fig)
        print(f"\n[figs] {min(len(snapshots), args.n_figs)} overlays + report.json → {args.out_dir}")
    else:
        print("\n[figs] no monster-visible frames captured — train longer or raise --max-steps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
