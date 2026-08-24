"""
Psychometric & chronometric curves for the RViT+ model.

Replicates the behavioral signatures of the published change-detection paper
(Morgan, Albanna & Herman 2025, arXiv:2502.10955): "improved accuracy and
faster responses for cued stimuli that scale with cue validity."

Three experiments (each → a 2-panel figure: accuracy left, reaction time right):

  EXP 1 — Signal-strength psychometric / chronometric (valid vs invalid)
      x = |Δθ| orientation-change magnitude, swept over `--mag-bins`.
      Two conditions at a FIXED displayed ring validity (`--valid-ring`):
        VALID   = the change occurs at the cued quadrant
        INVALID = the change occurs at a random uncued quadrant
      y(left)  = P(hit) = fraction of trials where the model presses at t≥Tc.
      y(right) = median reaction time RT = press_index − Tc (hits only).
      The classic psychometric function; the cueing/validity effect is the
      vertical gap (and leftward threshold shift) between VALID and INVALID.

  EXP 2 — Validity scaling (cued performance vs displayed cue validity)
      x = ring validity ∈ {0.25, 0.5, 0.75, 1.0}.
      Change always at the cued quadrant; |Δθ| fixed near-threshold
      (`--scaling-mag`). Tests the paper's "scales with cue validity" claim:
      cued accuracy should rise and RT should fall as validity increases.

  EXP 3 — Value scaling (cued performance vs cue value/color) [VDA]
      x = cue value ∈ {blue=1, green=3, red=5}.
      Change always at the cued quadrant; ring validity and |Δθ| fixed.
      The value-directed-attention angle: does higher reward magnitude buy
      better / faster detection?

All trials: change_true=1, change_time fixed (`--change-time`), cue side and
(unless swept) cue color randomized per trial so those nuisance factors
marginalize out. Reaction time is press_index − change_time, defined on hits.

Usage:
    .venv/bin/python RViT_plus_v3/analysis/psychometric_chronometric.py \
        --checkpoint RViT_plus_v3/checkpoints/rvit_plus_rl_latest.pt \
        --n-trials 256 --device cpu
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from typing import Dict, List

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v3.analysis import _behav_utils as bu


# ─────────────────────────────────────────────────────────────────────────────
# Aggregation helpers
# ─────────────────────────────────────────────────────────────────────────────


def _binom_sem(p: float, n: int) -> float:
    if n <= 0:
        return 0.0
    return float(np.sqrt(max(p * (1.0 - p), 0.0) / n))


def _summarize(out: Dict[str, np.ndarray]) -> Dict[str, float]:
    hit = out["hit"]
    n = int(hit.size)
    hit_rate = float(hit.mean()) if n else float("nan")
    rt_vals = out["rt"][~np.isnan(out["rt"])]
    median_rt = float(np.median(rt_vals)) if rt_vals.size else float("nan")
    # RT spread: bootstrap-free SEM of the median ≈ 1.253 · std / sqrt(n)
    rt_sem = float(1.2533 * rt_vals.std() / np.sqrt(rt_vals.size)) if rt_vals.size > 1 else 0.0
    return {
        "n": n,
        "hit_rate": hit_rate,
        "hit_sem": _binom_sem(hit_rate, n),
        "median_rt": median_rt,
        "rt_sem": rt_sem,
        "premature_rate": float(out["premature"].mean()) if n else float("nan"),
        "n_hits": int(rt_vals.size),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Experiments
# ─────────────────────────────────────────────────────────────────────────────


def run_exp1(model, device, args, env_kwargs) -> Dict[str, List[Dict[str, float]]]:
    """Signal-strength psychometric/chronometric, valid vs invalid."""
    results = {"valid": [], "invalid": []}
    for mag in args.mag_bins:
        for cond, mode in (("valid", "cued"), ("invalid", "uncued")):
            rng = np.random.default_rng(args.seed + int(mag * 1000) + (0 if cond == "valid" else 7))
            spec = bu.ForcedTrialSpec(
                proportion=args.valid_ring, change_true=1, change_time=args.change_time,
                change_index_mode=mode, orientation_mag=float(mag),
            )
            envs, obs0 = bu.build_env_batch(
                spec, args.n_trials, rng, env_kwargs=env_kwargs,
                randomize_cue_position=True, randomize_color=True,
            )
            out = bu.batched_behavior_rollout(model, envs, obs0, device)
            s = _summarize(out)
            s["mag"] = float(mag)
            results[cond].append(s)
        v, iv = results["valid"][-1], results["invalid"][-1]
        print(f"  |Δθ|={mag:5.1f}  VALID hit={v['hit_rate']:.3f} rt={v['median_rt']:.2f} "
              f"| INVALID hit={iv['hit_rate']:.3f} rt={iv['median_rt']:.2f}")
    return results


def run_exp2(model, device, args, env_kwargs) -> List[Dict[str, float]]:
    """Cued performance vs displayed cue validity (ring proportion)."""
    rows = []
    for val in (0.25, 0.5, 0.75, 1.0):
        rng = np.random.default_rng(args.seed + int(val * 1000) + 11)
        spec = bu.ForcedTrialSpec(
            proportion=val, change_true=1, change_time=args.change_time,
            change_index_mode="cued", orientation_mag=float(args.scaling_mag),
        )
        envs, obs0 = bu.build_env_batch(
            spec, args.n_trials, rng, env_kwargs=env_kwargs,
            randomize_cue_position=True, randomize_color=True,
        )
        out = bu.batched_behavior_rollout(model, envs, obs0, device)
        s = _summarize(out)
        s["validity"] = float(val)
        rows.append(s)
        print(f"  validity={val:.2f}  hit={s['hit_rate']:.3f}  rt={s['median_rt']:.2f}")
    return rows


def run_exp3(model, device, args, env_kwargs) -> List[Dict[str, float]]:
    """Cued performance vs cue value (color)."""
    rows = []
    for color in ("blue", "green", "red"):
        rng = np.random.default_rng(args.seed + hash(color) % 9973 + 23)
        spec = bu.ForcedTrialSpec(
            cue_color=color, proportion=args.valid_ring, change_true=1,
            change_time=args.change_time, change_index_mode="cued",
            orientation_mag=float(args.scaling_mag),
        )
        envs, obs0 = bu.build_env_batch(
            spec, args.n_trials, rng, env_kwargs=env_kwargs,
            randomize_cue_position=True, randomize_color=False,
        )
        out = bu.batched_behavior_rollout(model, envs, obs0, device)
        s = _summarize(out)
        s["color"] = color
        s["value"] = bu.COLOR_VALUE[color]
        rows.append(s)
        print(f"  value={bu.COLOR_VALUE[color]} ({color:5s})  hit={s['hit_rate']:.3f}  rt={s['median_rt']:.2f}")
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Plotting
# ─────────────────────────────────────────────────────────────────────────────


def plot_exp1(results, out_path, args):
    import matplotlib.pyplot as plt
    fig, (axA, axR) = plt.subplots(1, 2, figsize=(12, 4.8))
    colors = {"valid": "tab:blue", "invalid": "tab:red"}
    labels = {"valid": "Valid (change at cued loc.)", "invalid": "Invalid (change at uncued loc.)"}
    for cond in ("valid", "invalid"):
        rows = results[cond]
        x = [r["mag"] for r in rows]
        hr = [r["hit_rate"] for r in rows]
        he = [r["hit_sem"] for r in rows]
        rt = [r["median_rt"] for r in rows]
        re = [r["rt_sem"] for r in rows]
        axA.errorbar(x, hr, yerr=he, marker="o", capsize=3, color=colors[cond], label=labels[cond], lw=2)
        axR.errorbar(x, rt, yerr=re, marker="o", capsize=3, color=colors[cond], label=labels[cond], lw=2)
    axA.set_xlabel(r"orientation-change magnitude  $|\Delta\theta|$  (deg)")
    axA.set_ylabel("P(hit)")
    axA.set_title("Psychometric")
    axA.set_ylim(-0.02, 1.02)
    axA.axhline(0.5, color="grey", ls=":", alpha=0.5)
    axA.grid(alpha=0.3); axA.legend(fontsize=9)
    axR.set_xlabel(r"orientation-change magnitude  $|\Delta\theta|$  (deg)")
    axR.set_ylabel("median reaction time  (frames after change)")
    axR.set_title("Chronometric")
    axR.grid(alpha=0.3); axR.legend(fontsize=9)
    fig.suptitle(
        f"signal-strength psychometric / chronometric  ·  ring validity={args.valid_ring}  ·  "
        f"change@t={args.change_time}  ·  n={args.n_trials}/cell",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {out_path}")


def plot_exp2(rows, out_path, args):
    import matplotlib.pyplot as plt
    fig, (axA, axR) = plt.subplots(1, 2, figsize=(11, 4.6))
    x = [r["validity"] for r in rows]
    axA.errorbar(x, [r["hit_rate"] for r in rows], yerr=[r["hit_sem"] for r in rows],
                 marker="o", capsize=3, color="tab:green", lw=2)
    axA.set_xlabel("displayed cue validity (ring proportion)")
    axA.set_ylabel("P(hit), cued location")
    axA.set_title("Accuracy vs validity")
    axA.set_ylim(-0.02, 1.02); axA.grid(alpha=0.3)
    axR.errorbar(x, [r["median_rt"] for r in rows], yerr=[r["rt_sem"] for r in rows],
                 marker="o", capsize=3, color="tab:green", lw=2)
    axR.set_xlabel("displayed cue validity (ring proportion)")
    axR.set_ylabel("median reaction time (frames after change)")
    axR.set_title("RT vs validity")
    axR.grid(alpha=0.3)
    fig.suptitle(
        f"validity scaling (cued)  ·  |Δθ|={args.scaling_mag}  ·  change@t={args.change_time}  ·  n={args.n_trials}/cell",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {out_path}")


def plot_exp3(rows, out_path, args):
    import matplotlib.pyplot as plt
    fig, (axA, axR) = plt.subplots(1, 2, figsize=(11, 4.6))
    x = [r["value"] for r in rows]
    labels = [f"{r['color']}\n(v={r['value']})" for r in rows]
    axA.errorbar(x, [r["hit_rate"] for r in rows], yerr=[r["hit_sem"] for r in rows],
                 marker="s", capsize=3, color="tab:purple", lw=2)
    axA.set_xticks(x); axA.set_xticklabels(labels)
    axA.set_xlabel("cue value (reward on correct hit)")
    axA.set_ylabel("P(hit), cued location")
    axA.set_title("Accuracy vs value")
    axA.set_ylim(-0.02, 1.02); axA.grid(alpha=0.3)
    axR.errorbar(x, [r["median_rt"] for r in rows], yerr=[r["rt_sem"] for r in rows],
                 marker="s", capsize=3, color="tab:purple", lw=2)
    axR.set_xticks(x); axR.set_xticklabels(labels)
    axR.set_xlabel("cue value (reward on correct hit)")
    axR.set_ylabel("median reaction time (frames after change)")
    axR.set_title("RT vs value")
    axR.grid(alpha=0.3)
    fig.suptitle(
        f"value scaling (cued)  ·  ring={args.valid_ring}  ·  |Δθ|={args.scaling_mag}  ·  n={args.n_trials}/cell",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {out_path}")


def write_csv(path, fieldnames, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"[saved] {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default="RViT_plus_v3/checkpoints/rvit_plus_rl_latest.pt")
    ap.add_argument("--config", default=None)
    ap.add_argument("--out-dir", default="RViT_plus_v3/analysis/figures")
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=256, help="trials per condition cell")
    ap.add_argument("--change-time", type=int, default=15, help="fixed frame at which the change appears")
    ap.add_argument("--valid-ring", type=float, default=0.75,
                    help="displayed ring validity for exp1/exp3 (kept within the trained distribution)")
    ap.add_argument("--scaling-mag", type=float, default=14.0,
                    help="fixed near-threshold |Δθ| for exp2/exp3 (so validity/value have room to modulate)")
    ap.add_argument("--mag-bins", type=float, nargs="+",
                    default=[2, 5, 9, 14, 20, 30, 44, 64],
                    help="|Δθ| magnitudes for the exp1 sweep")
    ap.add_argument("--experiments", nargs="+", default=["1", "2", "3"],
                    choices=["1", "2", "3"], help="which experiments to run")
    args = ap.parse_args(argv)

    os.makedirs(args.out_dir, exist_ok=True)
    device = bu.select_device(args.device)
    cfg = bu.load_config(args.config)
    model = bu.build_model(cfg, device)
    it = bu.load_checkpoint(model, args.checkpoint, device)
    env_kwargs = dict(
        min_change_time=int(cfg["environment"]["min_change_time"]),
        max_change_time=int(cfg["environment"]["max_change_time"]),
    )
    print(f"[loaded] {args.checkpoint} (iter={it})  device={device}")

    fields = ["mag", "validity", "color", "value", "n", "n_hits",
              "hit_rate", "hit_sem", "median_rt", "rt_sem", "premature_rate"]

    if "1" in args.experiments:
        print("\n[EXP 1] signal-strength psychometric / chronometric (valid vs invalid)")
        res1 = run_exp1(model, device, args, env_kwargs)
        plot_exp1(res1, os.path.join(args.out_dir, "psychometric_chronometric_signal.png"), args)
        flat = ([{**r, "condition": "valid"} for r in res1["valid"]]
                + [{**r, "condition": "invalid"} for r in res1["invalid"]])
        write_csv(os.path.join(args.out_dir, "psychometric_signal.csv"),
                  ["condition"] + fields, flat)

    if "2" in args.experiments:
        print("\n[EXP 2] validity scaling (cued)")
        res2 = run_exp2(model, device, args, env_kwargs)
        plot_exp2(res2, os.path.join(args.out_dir, "psychometric_chronometric_validity.png"), args)
        write_csv(os.path.join(args.out_dir, "psychometric_validity.csv"), fields, res2)

    if "3" in args.experiments:
        print("\n[EXP 3] value scaling (cued)")
        res3 = run_exp3(model, device, args, env_kwargs)
        plot_exp3(res3, os.path.join(args.out_dir, "psychometric_chronometric_value.png"), args)
        write_csv(os.path.join(args.out_dir, "psychometric_value.csv"), fields, res3)

    print("\n[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
