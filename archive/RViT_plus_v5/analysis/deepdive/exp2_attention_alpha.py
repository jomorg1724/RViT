"""
EXP 2 — Per-head, per-layer attention for EVERY transformer + the α projection.

The v5 model contains four transformer stacks:
    encoder  L1, L2  (memory-as-tokens, self-attn over [patch ++ H1 ++ H2] = 3N)
    actor    decoder L1, L2  (CLS over [CLS ++ H1 ++ H2])
    critic   decoder L1, L2  (same, action=press injected)

For each we extract per-HEAD attention (heads are NOT averaged — they specialise)
and reduce to the project's α statistic:

    α_j = (Σ_queries A[:, j]) / (#queries)        ← summed column attention / #tokens

i.e. the mean incoming attention to patch-key j. For the encoder the queries are
all 3N tokens and the keys j run over the N image-patch columns; for the decoders
the query is the CLS readout (row 0) and α_j sums the H1 and H2 blocks for patch
position j. α over the 10×10 patch grid is then **projected back onto a 50×50 box**
(each patch → a 5×5 block) and overlaid on the stimulus — the intuitive view.

Outputs (figs/, tables/):
  * exp2_alpha_overlay_<transformer>_<cond>.png — α-on-image overlay, rows=heads,
    cols = key frames {cue, pre-change, change-onset, post-change}.
  * exp2_alpha_traj_<transformer>_<cond>.png — per-head quadrant α_i(t) trajectories.
  * exp2_budget.png — patch-vs-memory attention budget over time, per layer.
  * exp2_alpha.npz — every α map (T,H,gh,gw) per transformer per condition.

Usage:
  .venv/bin/python -m RViT_plus_v5.analysis.deepdive.exp2_attention_alpha \
      --n-trials 160 --device cpu
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, List

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from RViT_plus_v5.analysis import _behav_utils as bu
from RViT_plus_v5.analysis.deepdive import dd_core as dd

FIGS = os.path.join(_HERE, "figs")
TABS = os.path.join(_HERE, "tables")
QUAD_NAMES = dd.QUAD_NAMES


@torch.no_grad()
def attention_rollout(model, envs, obs0, device):
    """Forced-wait rollout; returns per-transformer per-head α maps (T,H,gh,gw),
    the patch-attention budget per encoder layer (T,H), and an obs example."""
    B = len(envs)
    model.eval()
    states = model.init_states(B, device=device)
    gh, gw, N = model.patch_embed.grid_h, model.patch_embed.grid_w, model.n_tokens
    nEnc = model.encoder.n_layers
    nDec = model.actor_head.tx.num_layers
    keys = ([f"enc_L{l+1}" for l in range(nEnc)]
            + [f"actor_L{l+1}" for l in range(nDec)]
            + [f"critic_L{l+1}" for l in range(nDec)])
    frames: Dict[str, List[np.ndarray]] = {k: [] for k in keys}
    budget: Dict[str, List[np.ndarray]] = {f"enc_L{l+1}": [] for l in range(nEnc)}
    obs_ex: List[np.ndarray] = []
    obs = list(obs0)
    T = envs[0].T
    t = 0; done = np.zeros(B, dtype=bool)
    while t <= T and not done.all():
        x = dd._obs_to_tensor(obs, device)
        obs_ex.append(np.asarray(obs[0], dtype=np.float32).copy())
        tokens = model.patch_embed(x)
        states, rec, enc_attn = dd.memtok_forward_step(model.encoder, tokens, states, return_attn=True)
        _, _, a_attn = dd.actor_decode(model.actor_head, rec, return_attn=True)
        _, _, c_attn = dd.critic_decode(model.critic_head, rec, 1, return_attn=True)
        # encoder: mean over all queries of attention to the N patch keys
        for l in range(nEnc):
            aw = enc_attn[l]                                  # (B,H,3N,3N)
            patch_cols = aw[:, :, :, :N]                      # to patch keys
            alpha = patch_cols.mean(dim=2)                    # mean over queries (B,H,N)
            frames[f"enc_L{l+1}"].append(
                alpha.mean(0).view(aw.shape[1], gh, gw).cpu().numpy())
            # budget: total attention paid to patch tokens (vs memory), per head
            budget[f"enc_L{l+1}"].append(
                aw[:, :, :, :N].sum(-1).mean(dim=(0, 2)).cpu().numpy())  # (H,)
        # decoders: CLS query → per-patch (sum H1,H2 blocks)
        for tag, att in (("actor", a_attn), ("critic", c_attn)):
            for l in range(nDec):
                aw = att[l]                                   # (B,H,1+2N,1+2N)
                cls = aw[:, :, 0, 1:]                          # (B,H,2N)
                pos = cls[:, :, :N] + cls[:, :, N:2 * N]       # (B,H,N)
                frames[f"{tag}_L{l+1}"].append(
                    pos.mean(0).view(aw.shape[1], gh, gw).cpu().numpy())
        for i in range(B):
            if done[i]:
                continue
            o, r, d, _ = envs[i].step(0)
            obs[i] = o
            if d:
                done[i] = True
        t += 1
    maps = {k: np.stack(v, 0) for k, v in frames.items()}     # (T,H,gh,gw)
    bud = {k: np.stack(v, 0) for k, v in budget.items()}      # (T,H)
    return maps, bud, np.stack(obs_ex, 0)


def quad_alpha(strip):
    """(T,H,gh,gw) → (T,H,4) summed within each env quadrant."""
    T, H, gh, gw = strip.shape
    hh, ww = gh // 2, gw // 2
    s1 = strip[:, :, :hh, :ww].sum((2, 3)); s2 = strip[:, :, hh:, :ww].sum((2, 3))
    s3 = strip[:, :, :hh, ww:].sum((2, 3)); s4 = strip[:, :, hh:, ww:].sum((2, 3))
    return np.stack([s1, s2, s3, s4], -1)


def plot_alpha_overlay(strip, obs_ex, out, *, title, frames, change_frame):
    """Rows = heads; cols = selected frames. Each cell: α projected to 50×50 (kron)
    overlaid (alpha-blended) on the stimulus."""
    import matplotlib.pyplot as plt
    T, H, gh, gw = strip.shape
    fr = [f for f in frames if f < T]
    fig, axes = plt.subplots(H, len(fr), figsize=(2.2 * len(fr), 2.2 * H), squeeze=False)
    vmax = float(strip[fr].max())
    for h in range(H):
        for ci, f in enumerate(fr):
            ax = axes[h][ci]
            frame = obs_ex[f]
            fmin, fmax = float(frame.min()), float(frame.max())
            base = (frame - fmin) / (fmax - fmin) if fmax > fmin else np.zeros_like(frame)
            ax.imshow(base)
            amap = dd.grid_to_image(strip[f, h], patch=5)        # 50×50
            ax.imshow(amap, cmap="inferno", alpha=0.55, vmin=0, vmax=vmax)
            ax.axhline(24.5, color="white", lw=.4, alpha=.4); ax.axvline(24.5, color="white", lw=.4, alpha=.4)
            ax.set_xticks([]); ax.set_yticks([])
            if h == 0:
                ax.set_title(f"t={f}" + ("  (chg)" if f == change_frame else ""), fontsize=8,
                             color=("orange" if f == change_frame else "black"))
            if ci == 0:
                ax.set_ylabel(f"head {h}", fontsize=9)
    fig.suptitle(title, fontsize=10, y=1.005)
    fig.tight_layout(); fig.savefig(out, dpi=130, bbox_inches="tight"); plt.close(fig)


def plot_alpha_traj(strip, out, *, title, change_frame, change_index):
    import matplotlib.pyplot as plt
    T, H, gh, gw = strip.shape
    qa = quad_alpha(strip)                                    # (T,H,4)
    fig, axes = plt.subplots(1, H, figsize=(3.6 * H, 3.3), squeeze=False)
    axes = axes[0]
    cols = ["tab:blue", "tab:orange", "tab:green", "tab:red"]
    for h in range(H):
        ax = axes[h]
        for q in range(4):
            star = " ◄chg" if q == change_index else ""
            ax.plot(np.arange(T), qa[:, h, q], color=cols[q], lw=1.7, label=QUAD_NAMES[q] + star)
        ax.axvline(1, color="k", ls=":", alpha=.4); ax.axvline(3, color="grey", ls=":", alpha=.3)
        ax.axvline(change_frame, color="orange", ls="--", alpha=.6)
        ax.set_title(f"head {h}", fontsize=10); ax.set_xlabel("t"); ax.grid(alpha=.3)
        if h == 0:
            ax.set_ylabel(r"$\alpha_i(t)$ (quadrant)"); ax.legend(fontsize=6, loc="upper left")
    fig.suptitle(title, fontsize=10)
    fig.tight_layout(); fig.savefig(out, dpi=120, bbox_inches="tight"); plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=dd.DEFAULT_CKPT)
    ap.add_argument("--config", default=None)
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=160)
    ap.add_argument("--change-time", type=int, default=15)
    ap.add_argument("--change-mag", type=float, default=64.0)
    args = ap.parse_args(argv)

    os.makedirs(FIGS, exist_ok=True); os.makedirs(TABS, exist_ok=True)
    device = dd.select_device(args.device)
    cfg = dd.load_config(args.config)
    model = dd.build_model(cfg, device)
    it = dd.load_checkpoint(model, args.checkpoint, device)
    env_kwargs = dict(min_change_time=int(cfg["environment"]["min_change_time"]),
                      max_change_time=int(cfg["environment"]["max_change_time"]))
    print(f"[loaded] {args.checkpoint} (iter={it}) device={device}")

    # cue side × validity; change at S1 (cued) for VALID, uncued for INVALID.
    conds = [
        ("left", bu.CUED_QUADRANT["left"], "VALID_cueLeft_chgS1"),
        ("left", 3, "INVALID_cueLeft_chgS4"),
        ("right", bu.CUED_QUADRANT["right"], "VALID_cueRight_chgS4"),
        ("right", 0, "INVALID_cueRight_chgS1"),
    ]
    probe_frames = [1, 8, args.change_time, min(args.change_time + 3, 28)]
    save = {"probe_frames": np.array(probe_frames), "change_time": args.change_time}
    budget_store = {}
    for side, chg_idx, tag in conds:
        rng = np.random.default_rng(args.seed + hash(tag) % 9973)
        spec = bu.ForcedTrialSpec(
            cue_position=side, proportion=1.0, change_true=1, change_time=args.change_time,
            change_index_mode=int(chg_idx), orientation_mag=float(args.change_mag))
        envs, obs0 = bu.build_env_batch(spec, args.n_trials, rng, env_kwargs=env_kwargs,
                                        randomize_cue_position=False, randomize_color=True)
        maps, bud, obs_ex = attention_rollout(model, envs, obs0, device)
        budget_store[tag] = bud
        print(f"[{tag}] peaks: " + "  ".join(f"{k}={v.max():.3f}" for k, v in maps.items()))
        for tname, strip in maps.items():
            save[f"{tag}__{tname}"] = strip
            plot_alpha_overlay(
                strip, obs_ex, os.path.join(FIGS, f"exp2_overlay_{tname}_{tag}.png"),
                title=f"{tname} · α projected on stimulus · {tag} · change@{QUAD_NAMES[chg_idx]} t={args.change_time}",
                frames=probe_frames, change_frame=args.change_time)
            plot_alpha_traj(
                strip, os.path.join(FIGS, f"exp2_traj_{tname}_{tag}.png"),
                title=f"{tname} · per-head quadrant α(t) · {tag}",
                change_frame=args.change_time, change_index=chg_idx)

    # budget figure
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, len(budget_store), figsize=(4 * len(budget_store), 3.4), squeeze=False)
    axes = axes[0]
    for ax, (tag, bud) in zip(axes, budget_store.items()):
        for lk, arr in bud.items():
            for h in range(arr.shape[1]):
                ax.plot(np.arange(arr.shape[0]), arr[:, h], lw=1.2,
                        label=f"{lk} h{h}" if ax is axes[0] else None)
        ax.axvline(args.change_time, color="orange", ls="--", alpha=.5)
        ax.set_title(tag, fontsize=8); ax.set_xlabel("t"); ax.set_ylim(0, 1); ax.grid(alpha=.3)
        ax.set_ylabel("Σ patch-key attention (budget)")
    axes[0].legend(fontsize=6, ncol=2)
    fig.suptitle("Encoder patch-vs-memory attention budget over time (per head)")
    fig.tight_layout(); fig.savefig(f"{FIGS}/exp2_budget.png", dpi=130, bbox_inches="tight"); plt.close(fig)

    np.savez_compressed(f"{TABS}/exp2_alpha.npz", **save)
    print(f"[saved] {TABS}/exp2_alpha.npz  + overlays/trajectories to {FIGS}")
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
