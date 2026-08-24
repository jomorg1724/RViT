"""
Psychometric & chronometric curves for RViT+ v11, swept over EVERY cue proportion
(displayed reliability) and split valid vs invalid.

For each displayed cue reliability p in {0.25, 0.5, 0.75, 1.0} and each cueing
condition (valid = change at the cued location S1; invalid = change at an uncued
location) we sweep the change magnitude |Δθ| and record hit rate, median reaction
time, and premature-press rate. The cue side is FIXED left (cued quadrant = S1)
so the valid/invalid and proportion contrasts are not diluted by cue-position
randomization; cue colour is randomized so value marginalizes out.

Outputs (to --out-dir):
  CSV  psychometric_by_proportion.csv  (proportion, cond, mag, n, hit_rate, hit_sem,
                                        median_rt, rt_sem, premature_rate)
  FIG  psycho_valid_all_proportions.png   valid only, 4 proportions overlaid (hit+RT)
  FIG  psycho_valid_vs_invalid_grid.png   one column per proportion, valid vs invalid (hit row, RT row)
  FIG  psycho_proportion1.0_valid_vs_invalid.png  the headline 1.0 valid-vs-invalid (hit+RT)

Usage:
  .venv/bin/python RViT_plus_v11/analysis/psychometric_by_proportion.py \
      --checkpoint <ckpt> --device cpu --n-trials 250
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from RViT_plus_v11.analysis import _behav_utils as bu


def _binom_sem(p, n):
    return float(np.sqrt(max(p * (1 - p), 0.0) / n)) if n > 0 else 0.0


def cell(model, device, env_kwargs, *, proportion, cond, mag, change_time, n_trials, seed):
    mode = "cued" if cond == "valid" else "uncued"
    rng = np.random.default_rng(seed)
    spec = bu.ForcedTrialSpec(cue_position="left", proportion=proportion, change_true=1,
                              change_time=change_time, change_index_mode=mode,
                              orientation_mag=float(mag))
    envs, obs0 = bu.build_env_batch(spec, n_trials, rng, env_kwargs=env_kwargs,
                                    randomize_cue_position=False, randomize_color=True)
    out = bu.batched_behavior_rollout(model, envs, obs0, device)
    hit = out["hit"]; n = int(hit.size)
    hr = float(hit.mean())
    rtv = out["rt"][~np.isnan(out["rt"])]
    mrt = float(np.median(rtv)) if rtv.size else float("nan")
    rt_sem = float(1.2533 * rtv.std() / np.sqrt(rtv.size)) if rtv.size > 1 else 0.0
    return {"proportion": proportion, "cond": cond, "mag": float(mag), "n": n,
            "hit_rate": hr, "hit_sem": _binom_sem(hr, n), "median_rt": mrt,
            "rt_sem": rt_sem, "premature_rate": float(out["premature"].mean())}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default="/Users/jonathanmorgan/rvit_plus_checkpoints/v11/v11_analysis_snapshot.pt")
    ap.add_argument("--config", default=None)
    ap.add_argument("--out-dir", default="RViT_plus_v11/analysis/figures")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=250)
    ap.add_argument("--change-time", type=int, default=15)
    ap.add_argument("--mag-bins", type=float, nargs="+", default=[2, 5, 9, 14, 20, 30, 44, 64])
    ap.add_argument("--proportions", type=float, nargs="+", default=[0.25, 0.5, 0.75, 1.0])
    args = ap.parse_args(argv)

    os.makedirs(args.out_dir, exist_ok=True)
    device = bu.select_device(args.device)
    cfg = bu.load_config(args.config)
    model = bu.build_model(cfg, device)
    it = bu.load_checkpoint(model, args.checkpoint, device)
    env_kwargs = dict(min_change_time=int(cfg["environment"]["min_change_time"]),
                      max_change_time=int(cfg["environment"]["max_change_time"]))
    print(f"[loaded] {args.checkpoint} (iter={it}) device={device}")
    print(f"[setup] cue=left (cued=S1), change@t={args.change_time}, colour randomized, "
          f"n={args.n_trials}/cell, proportions={args.proportions}")

    rows = []
    for p in args.proportions:
        for cond in ("valid", "invalid"):
            for mag in args.mag_bins:
                seed = args.seed + int(p * 1000) + (0 if cond == "valid" else 5) + int(mag * 3)
                r = cell(model, device, env_kwargs, proportion=p, cond=cond, mag=mag,
                         change_time=args.change_time, n_trials=args.n_trials, seed=seed)
                rows.append(r)
            v = [x for x in rows if x["proportion"] == p and x["cond"] == cond]
            print(f"  p={p:.2f} {cond:7s}: hit@14={[x['hit_rate'] for x in v if x['mag']==14][0]:.3f} "
                  f"hit@max={max(x['hit_rate'] for x in v):.3f}")

    # CSV
    fields = ["proportion", "cond", "mag", "n", "hit_rate", "hit_sem", "median_rt", "rt_sem", "premature_rate"]
    with open(os.path.join(args.out_dir, "psychometric_by_proportion.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"[saved] {args.out_dir}/psychometric_by_proportion.csv")

    # ── plots ──
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9})
    props = args.proportions
    pcols = {0.25: "#1f77b4", 0.5: "#2ca02c", 0.75: "#ff7f0e", 1.0: "#d62728"}

    def sub(p, cond):
        s = sorted([x for x in rows if x["proportion"] == p and x["cond"] == cond], key=lambda z: z["mag"])
        return ([x["mag"] for x in s], [x["hit_rate"] for x in s], [x["hit_sem"] for x in s],
                [x["median_rt"] for x in s], [x["rt_sem"] for x in s])

    # (a) valid only, all proportions overlaid
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    for p in props:
        m, h, he, rt, re = sub(p, "valid")
        ax[0].errorbar(m, h, yerr=he, marker="o", color=pcols[p], lw=2, capsize=2, label=f"ring {p}")
        ax[1].errorbar(m, rt, yerr=re, marker="o", color=pcols[p], lw=2, capsize=2, label=f"ring {p}")
    ax[0].set(xlabel=r"$|\Delta\theta|$ (deg)", ylabel="P(hit)", title="Valid cues: psychometric by cue reliability", ylim=(-.02, 1.02))
    ax[1].set(xlabel=r"$|\Delta\theta|$ (deg)", ylabel="median RT (frames)", title="Valid cues: chronometric by cue reliability")
    for a in ax:
        a.grid(alpha=.3); a.legend(fontsize=8)
    fig.suptitle("Valid-cue psychometrics / chronometrics across all cue proportions (change at cued S1)", y=1.02)
    fig.tight_layout(); fig.savefig(os.path.join(args.out_dir, "psycho_valid_all_proportions.png"), dpi=140, bbox_inches="tight"); plt.close(fig)
    print("[saved] psycho_valid_all_proportions.png")

    # (b) valid vs invalid, one column per proportion (hit row, RT row)
    fig, axes = plt.subplots(2, len(props), figsize=(3.6 * len(props), 8), sharex=True)
    for j, p in enumerate(props):
        for cond, c in (("valid", "tab:blue"), ("invalid", "tab:red")):
            m, h, he, rt, re = sub(p, cond)
            axes[0, j].errorbar(m, h, yerr=he, marker="o", color=c, lw=2, capsize=2, label=cond)
            axes[1, j].errorbar(m, rt, yerr=re, marker="o", color=c, lw=2, capsize=2, label=cond)
        axes[0, j].set_title(f"ring {p}"); axes[0, j].set_ylim(-.02, 1.02)
        axes[0, j].grid(alpha=.3); axes[1, j].grid(alpha=.3)
        axes[1, j].set_xlabel(r"$|\Delta\theta|$ (deg)")
    axes[0, 0].set_ylabel("P(hit)"); axes[1, 0].set_ylabel("median RT (frames)")
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Valid vs invalid within each cue proportion (cue left=S1; invalid = change at an uncued quadrant)", y=1.0)
    fig.tight_layout(); fig.savefig(os.path.join(args.out_dir, "psycho_valid_vs_invalid_grid.png"), dpi=140, bbox_inches="tight"); plt.close(fig)
    print("[saved] psycho_valid_vs_invalid_grid.png")

    # (c) the headline ring 1.0 valid vs invalid
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    for cond, c in (("valid", "tab:blue"), ("invalid", "tab:red")):
        m, h, he, rt, re = sub(1.0, cond)
        ax[0].errorbar(m, h, yerr=he, marker="o", color=c, lw=2.2, capsize=3, label=cond)
        ax[1].errorbar(m, rt, yerr=re, marker="o", color=c, lw=2.2, capsize=3, label=cond)
    ax[0].set(xlabel=r"$|\Delta\theta|$ (deg)", ylabel="P(hit)", title="Ring 1.0: P(hit), valid vs invalid", ylim=(-.02, 1.02))
    ax[1].set(xlabel=r"$|\Delta\theta|$ (deg)", ylabel="median RT (frames)", title="Ring 1.0: RT, valid vs invalid")
    for a in ax:
        a.grid(alpha=.3); a.legend(fontsize=9)
    fig.suptitle("Fully-valid cue (ring 1.0): the spatial cueing benefit, valid vs invalid", y=1.02)
    fig.tight_layout(); fig.savefig(os.path.join(args.out_dir, "psycho_proportion1.0_valid_vs_invalid.png"), dpi=140, bbox_inches="tight"); plt.close(fig)
    print("[saved] psycho_proportion1.0_valid_vs_invalid.png")
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
