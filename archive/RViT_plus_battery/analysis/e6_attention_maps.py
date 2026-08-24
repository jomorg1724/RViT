"""
E6 — FIXED attention-map visualization + fixed-change-time ramp (James's 2026-06-09
asks: the quadrant-averaging viz "doesn't look like it adds up to 1"; and the ramp may
be a variable-change-time averaging artifact, so re-run on a fixed change-time subset).

The FIX: attention is read as ONE value per stimulus token (mean over heads & queries
of the softmax weight PAID TO that token), which sums to 1 across the K stimuli by
construction — no 5×5 quadrant averaging, no border sub-patches. Outputs, per cue
validity (proportion):
  • attn_to_cued(t)  and  attn_to_uncued_mean(t)   over the trial   (the time-course)
  • the same restricted to a SINGLE fixed change_time (disambiguates evidence-
    integration from the averaging artifact)
Saves an .npz (and a .png if matplotlib is available).

    python RViT_plus_battery/analysis/e6_attention_maps.py \
        --checkpoint ~/rvit_plus_checkpoints/film_validity4/rvit_plus_validity4_final.pt \
        --task validity4 --n-trials 4000 --fixed-change-time 18 --out reports/e6_validity4

DO NOT run while the live MPS training jobs are going (CPU safety).
"""
from __future__ import annotations

import argparse
import os

import numpy as np

from common import load_model, rollout, make_env


def time_courses(attn_by_t, n_tokens, props, fixed_ct=None, change_times=None):
    """attn_by_t: t -> list[(cue_index, proportion, per_stim(N,))].
    Returns dict prop -> (attn_cued[T], attn_uncued_mean[T])."""
    T = max(attn_by_t) + 1
    out = {}
    for p in props:
        cued = np.full(T, np.nan); unc = np.full(T, np.nan)
        for t in range(T):
            entries = attn_by_t.get(t, [])
            cs, us = [], []
            for (cue_idx, prop, per_stim) in entries:
                if abs(prop - p) > 1e-6:
                    continue
                cs.append(per_stim[cue_idx])
                mask = np.ones(n_tokens, dtype=bool); mask[cue_idx] = False
                us.append(per_stim[mask].mean())
            if cs:
                cued[t] = np.mean(cs); unc[t] = np.mean(us)
        out[p] = (cued, unc)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--n-trials", type=int, default=4000)
    ap.add_argument("--fixed-change-time", type=int, default=None)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    model = load_model(args.checkpoint, task=args.task, device=args.device)
    env = make_env(args.task)
    rec = rollout(model, env, n_trials=args.n_trials, device=args.device,
                  greedy=True, collect_attn=True)
    attn_by_t = rec.pop("_attn_by_t")
    N = model.n_tokens
    props = sorted(set(rec["proportion"].tolist()))

    # sanity: per-frame per-stimulus attention should sum to ~1 across the K stimuli
    sums = [per_stim.sum() for entries in attn_by_t.values() for (_, _, per_stim) in entries]
    print(f"[E6] per-stimulus attention sums to mean={np.mean(sums):.3f} "
          f"(±{np.std(sums):.3f}) across {len(sums)} frames — should be ≈1.0")

    tc_all = time_courses(attn_by_t, N, props)
    print("\nE6 — attention to cued vs uncued by validity (all change-times):")
    for p in props:
        cued, unc = tc_all[p]
        peak = np.nanmax(cued)
        print(f"  proportion {p:>4}: peak attn_to_cued={peak:.3f}  "
              f"(mean uncued={np.nanmean(unc):.3f})")

    payload = {f"all_cued_{p}": tc_all[p][0] for p in props}
    payload.update({f"all_uncued_{p}": tc_all[p][1] for p in props})

    if args.fixed_change_time is not None:
        # restrict the attention records to trials with this change_time. We re-run a
        # rollout filtered post-hoc is not possible (attn lacks change_time), so re-run
        # a dedicated rollout where the env is pinned to the fixed change time.
        env.min_change_time = args.fixed_change_time
        env.max_change_time = args.fixed_change_time
        rec2 = rollout(model, env, n_trials=args.n_trials, device=args.device,
                       greedy=True, collect_attn=True)
        attn2 = rec2.pop("_attn_by_t")
        tc_fixed = time_courses(attn2, N, props)
        print(f"\nE6 — attention ramp at FIXED change_time={args.fixed_change_time}:")
        for p in props:
            cued, _ = tc_fixed[p]
            print(f"  proportion {p:>4}: attn_to_cued ramp = "
                  + " ".join(f"{v:.2f}" for v in cued))
        payload.update({f"fixed_cued_{p}": tc_fixed[p][0] for p in props})
        payload.update({f"fixed_uncued_{p}": tc_fixed[p][1] for p in props})

    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
        np.savez(args.out + ".npz", **payload)
        print(f"\nwrote {args.out}.npz")
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(1, 1, figsize=(6, 4))
            for p in props:
                ax.plot(tc_all[p][0], label=f"cued p={p}")
            ax.set_xlabel("time step"); ax.set_ylabel("attention to cued stimulus")
            ax.set_title(f"{args.task}: attention to cued vs validity")
            ax.legend(fontsize=7)
            fig.tight_layout(); fig.savefig(args.out + ".png", dpi=140)
            print(f"wrote {args.out}.png")
        except Exception as e:  # pragma: no cover
            print(f"(matplotlib unavailable: {e})")


if __name__ == "__main__":
    main()
