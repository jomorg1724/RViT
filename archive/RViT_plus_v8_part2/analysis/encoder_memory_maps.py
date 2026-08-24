"""
Encoder cross-attention MEMORY-key spatial maps for RViT+ v5_part2.

`avg_attention_maps.py` maps where the patch QUERIES attend among the PATCH keys
— but in v5_part2 only ~10% of the cross-attention budget lands on patch keys;
~90% lands on the memory keys (H1, H2). This script maps that dominant part:
the per-head attention from the patch queries onto the H1 and H2 memory rows
(memory row i ↔ patch position i), reshaped to the (grid_h, grid_w) grid, so we
can see whether the memory reads orient spatially (to the cue / the change).

Reduction: mean over the N patch queries of attention to memory-key i → per-row
saliency → grid; per head, over time, averaged over trials. Sweeps cue side with
the change held fixed (VALID vs INVALID).
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v8_part2.analysis import _behav_utils as bu
from RViT_plus_v8_part2.analysis.avg_attention_maps import CHANGE_LABEL, plot_head_alpha, plot_head_strip


@torch.no_grad()
def mem_map_rollout(model, envs, obs0, device, which: str):
    """which ∈ {'H1','H2'}: per-head spatial map of patch-query attention onto that
    memory state's rows. Returns (T, heads, gh, gw), obs_example."""
    B = len(envs); model.eval()
    gh, gw, N = model.patch_embed.grid_h, model.patch_embed.grid_w, model.n_tokens
    off = N if which == "H1" else 2 * N
    states = model.init_states(B, device=device); obs = list(obs0); T = envs[0].T
    frames: List[np.ndarray] = []; obs_ex: List[np.ndarray] = []
    t = 0; done = np.zeros(B, dtype=bool)
    while t <= T and not done.all():
        x = bu._obs_to_tensor(obs, device); obs_ex.append(np.asarray(obs[0], dtype=np.float32).copy())
        tok = model.patch_embed(x)
        states, _rec, attn = model.encoder.forward_step(tok, states, return_attn=True)
        aw = attn[0]                                   # (B, heads, N, 3N)
        keys = aw[:, :, :, off:off + N]                # attention to this memory's rows
        sal = keys.mean(dim=2)                          # mean over patch queries → (B, heads, N)
        grid = sal.view(B, sal.shape[1], gh, gw)
        frames.append(grid.mean(dim=0).cpu().numpy())
        for i in range(B):
            if done[i]: continue
            o, r, d, _ = envs[i].step(0); obs[i] = o
            if d: done[i] = True
        t += 1
    return np.stack(frames, 0), np.stack(obs_ex, 0)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default="RViT_plus_v8_part2/checkpoints/rvit_plus_rl_latest.pt")
    ap.add_argument("--config", default=None)
    ap.add_argument("--out-dir", default="RViT_plus_v8_part2/analysis/figures_memkeys")
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=128)
    ap.add_argument("--change-time", type=int, default=15)
    ap.add_argument("--change-index", type=int, default=0)
    ap.add_argument("--change-mag", type=float, default=64.0)
    ap.add_argument("--conditions", nargs="+", default=["left:1.0", "right:1.0"])
    args = ap.parse_args(argv)

    os.makedirs(args.out_dir, exist_ok=True)
    device = bu.select_device(args.device)
    cfg = bu.load_config(args.config)
    model = bu.build_model(cfg, device)
    it = bu.load_checkpoint(model, args.checkpoint, device)
    env_kwargs = dict(min_change_time=int(cfg["environment"]["min_change_time"]),
                      max_change_time=int(cfg["environment"]["max_change_time"]))
    print(f"[loaded] {args.checkpoint} (iter={it})  device={device}")
    suffix = f"chg{args.change_index}_t{args.change_time}"

    for which in ("H1", "H2"):
        for cond in args.conditions:
            side, ring = cond.split(":"); ring = float(ring)
            rng = np.random.default_rng(args.seed + (0 if side == "left" else 1000) + int(ring * 100))
            spec = bu.ForcedTrialSpec(cue_position=side, proportion=ring, change_true=1,
                                      change_time=args.change_time, change_index_mode=int(args.change_index),
                                      orientation_mag=float(args.change_mag))
            envs, obs0 = bu.build_env_batch(spec, args.n_trials, rng, env_kwargs=env_kwargs,
                                            randomize_cue_position=False, randomize_color=True)
            tag = "VALID" if bu.CUED_QUADRANT[side] == args.change_index else "INVALID"
            label = f"{which} · cue {side} · ring {ring} ({tag})"
            strip, obs_ex = mem_map_rollout(model, envs, obs0, device, which)
            safe = f"{which}_cue{side}_ring{ring}{tag}"
            print(f"  [{label}] range=[{strip.min():.3f},{strip.max():.3f}]")
            plot_head_strip(strip, obs_ex,
                            os.path.join(args.out_dir, f"memkey_{safe}_{suffix}.png"),
                            title=f"patch-query → {which} memory-key attention · cue {side} ({tag}) · n={args.n_trials}",
                            change_frame=args.change_time)
            plot_head_alpha(strip,
                            os.path.join(args.out_dir, f"memkey_alpha_{safe}_{suffix}.png"),
                            layer_idx=0, change_frame=args.change_time, change_index=args.change_index,
                            cond_label=label)
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
