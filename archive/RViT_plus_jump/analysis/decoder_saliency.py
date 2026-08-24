"""
DECODER gradient-saliency for RViT+ v5_part2.

v5's decoder finding ("the actor CLS attention is a bottom-up change detector")
was read off attention weights. v5_part2's decoder is a 1D-CONV head with NO
attention, so we use the model-agnostic analog: the gradient of the press
decision w.r.t. the top recurrent state H2's token positions.

    s_i(t) = || ∂(press readout_t) / ∂(H2_t[:, i, :]) ||_1        (per token i)

reshaped to the (grid_h, grid_w) patch grid. If the conv decoder is a change
detector, s should snap onto the CHANGED quadrant at change onset (t≈Tc),
mirroring v5. We compute it for the actor (press logit) and the critic (mean
press Q), holding the change fixed and sweeping cue side, so VALID vs INVALID
tells us whether the readout is change-driven (locks to the change) or
cue-driven (locks to the cue).

Usage:
    .venv/bin/python RViT_plus_jump/analysis/decoder_saliency.py \
        --checkpoint <ckpt> --n-trials 96 --device cpu
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

from RViT_plus_jump.analysis import _behav_utils as bu
from RViT_plus_jump.analysis.avg_attention_maps import (
    CHANGE_LABEL, plot_head_alpha, plot_head_strip,
)


def _detach_state(state):
    Hs, Cs = state
    return ([h.detach() for h in Hs], [c.detach() for c in Cs])


def saliency_rollout(model, envs, obs0, device):
    """Forced-wait rollout; per frame compute the decision's sensitivity to each
    readout token position. v11's heads read BOTH transformer outputs [Z_sal, Z_td],
    so per token i we sum the L1 gradient over the two streams:
        s_i = ||∂press/∂Z_sal[:,i,:]||_1 + ||∂press/∂Z_td[:,i,:]||_1
    Returns (T, 2, gh, gw) [row0=actor press-logit, row1=critic press-Q] mean over
    trials, an obs example, and a per-frame salience-vs-top-down split
    frac_sal[t] = ||∂/∂Z_sal|| / (||∂/∂Z_sal|| + ||∂/∂Z_td||) for the actor."""
    B = len(envs)
    model.eval()
    gh, gw, N = model.patch_embed.grid_h, model.patch_embed.grid_w, model.n_tokens
    states = model.init_states(B, device=device)
    obs = list(obs0)
    T = envs[0].T
    frames: List[np.ndarray] = []
    obs_example: List[np.ndarray] = []
    frac_sal: List[float] = []
    t = 0
    done = np.zeros(B, dtype=bool)
    while t <= T and not done.all():
        x = bu._obs_to_tensor(obs, device)
        obs_example.append(np.asarray(obs[0], dtype=np.float32).copy())
        tokens = model.patch_embed(x)
        states, rec = model.encoder.forward_step(tokens, states)
        Z_sal, Z_td = rec[0], rec[1]                            # (B, N, d), in graph
        logits = model.actor_head(rec)                          # (B, 2)
        q = model.critic_head(rec)                              # (B, 2, n_quantiles)
        press = logits[:, 1].sum()
        q_press = q[:, 1, :].mean(dim=1).sum()
        g_a_sal, g_a_td = torch.autograd.grad(press, [Z_sal, Z_td], retain_graph=True)
        g_c_sal, g_c_td = torch.autograd.grad(q_press, [Z_sal, Z_td], retain_graph=True)
        sal_a = (g_a_sal.abs().sum(-1) + g_a_td.abs().sum(-1)).mean(0)   # (N,)
        sal_c = (g_c_sal.abs().sum(-1) + g_c_td.abs().sum(-1)).mean(0)
        tot_sal = float(g_a_sal.abs().sum()); tot_td = float(g_a_td.abs().sum())
        frac_sal.append(tot_sal / (tot_sal + tot_td + 1e-9))
        grid = np.stack([sal_a.view(gh, gw).detach().cpu().numpy(),
                         sal_c.view(gh, gw).detach().cpu().numpy()], axis=0)  # (2, gh, gw)
        frames.append(grid)
        states = _detach_state(states)                         # local saliency: cut graph between frames
        for i in range(B):
            if done[i]:
                continue
            o, r, d, _ = envs[i].step(0)
            obs[i] = o
            if d:
                done[i] = True
        t += 1
    return (np.stack(frames, axis=0), np.stack(obs_example, axis=0),
            np.asarray(frac_sal, dtype=np.float32))   # (T,2,gh,gw), (T,50,50,3), (T,)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default="RViT_plus_jump/checkpoints/rvit_plus_rl_latest.pt")
    ap.add_argument("--config", default=None)
    ap.add_argument("--out-dir", default="RViT_plus_jump/analysis/figures_decoder")
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=96)
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
    print(f"[fixed change] quadrant={CHANGE_LABEL[args.change_index]}  t={args.change_time}  |Δθ|={args.change_mag}")
    suffix = f"chg{args.change_index}_t{args.change_time}"

    for cond in args.conditions:
        side, ring = cond.split(":"); ring = float(ring)
        rng = np.random.default_rng(args.seed + (0 if side == "left" else 1000) + int(ring * 100))
        spec = bu.ForcedTrialSpec(cue_position=side, proportion=ring, change_true=1,
                                  change_time=args.change_time, change_index_mode=int(args.change_index),
                                  orientation_mag=float(args.change_mag))
        envs, obs0 = bu.build_env_batch(spec, args.n_trials, rng, env_kwargs=env_kwargs,
                                        randomize_cue_position=False, randomize_color=True)
        valid_tag = "VALID" if bu.CUED_QUADRANT[side] == args.change_index else "INVALID"
        label = f"cue {side} · ring {ring} ({valid_tag})"
        strip, obs_ex, frac_sal = saliency_rollout(model, envs, obs0, device)
        safe = label.replace(" ", "").replace("·", "_").replace("(", "").replace(")", "")
        # peak quadrant of the actor saliency in the post-change window
        from RViT_plus_jump.analysis.avg_attention_maps import quad_aggregate
        a_quad = quad_aggregate(strip[:, 0])                    # (T,4) actor
        post = a_quad[args.change_time:].mean(0)
        fs_post = float(np.nanmean(frac_sal[args.change_time:]))
        print(f"  [{label}] actor saliency post-change quad means [S1,S2,S3,S4] = "
              f"[{post[0]:.3f},{post[1]:.3f},{post[2]:.3f},{post[3]:.3f}]  "
              f"(change at {CHANGE_LABEL[args.change_index]})  "
              f"| readout split: salience={fs_post:.2f} top-down={1-fs_post:.2f}")
        plot_head_strip(strip, obs_ex,
                        os.path.join(args.out_dir, f"saliency_{safe}_{suffix}.png"),
                        title=f"decoder ∂press/∂[Z_sal,Z_td] saliency (row0=actor, row1=critic) · {label} · "
                              f"salience-frac(post)={fs_post:.2f} · n={args.n_trials}",
                        change_frame=args.change_time)
        plot_head_alpha(strip,
                        os.path.join(args.out_dir, f"saliency_alpha_{safe}_{suffix}.png"),
                        layer_idx=0, change_frame=args.change_time, change_index=args.change_index,
                        cond_label=f"saliency (h0=actor,h1=critic) · {label}")
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
