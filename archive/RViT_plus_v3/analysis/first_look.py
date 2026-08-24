"""
FIRST LOOK — standardized first-pass analysis of a trained RViT+ model.

One command runs the full "first look" battery on a checkpoint and drops every
figure + CSV into a single folder, then prints a short digest you can read at a
glance. This is the SOP for the first inspection of any freshly-trained model
(see FIRST_LOOK_SOP.md).

What it runs
------------
1. Psychometric / chronometric behavior (psychometric_chronometric.py):
     - EXP1 signal-strength: P(hit) & RT vs |Δθ|, valid vs invalid  → the cueing/validity effect
     - EXP2 validity scaling: cued accuracy & RT vs displayed ring validity
     - EXP3 value scaling:    cued accuracy & RT vs cue value (blue/green/red)
2. Averaged attention maps (avg_attention_maps.py):
     - channel/head-summed attention heatmap per layer, averaged over trials,
       for several cue conditions, with a fixed easily-detectable change.

Checkpoint selection
--------------------
Defaults to `<pkg>/checkpoints/rvit_plus_rl_final.pt` (the completed run); falls
back to `..._latest.pt` if final is absent. Always prints which file + iter it
loaded so there is never ambiguity about what was analyzed.

Usage
-----
    .venv/bin/python RViT_plus_v3/analysis/first_look.py            # final.pt, defaults
    .venv/bin/python RViT_plus_v3/analysis/first_look.py --checkpoint <path> --open
    .venv/bin/python RViT_plus_v3/analysis/first_look.py --thorough # more trials/bins
"""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from typing import List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_PKG_DIR = os.path.dirname(_HERE)                       # RViT_plus_v3/
_PKG_NAME = os.path.basename(_PKG_DIR)                  # "RViT_plus_v3"
_PROJECT_ROOT = os.path.dirname(_PKG_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# Import the two analysis drivers from THIS package's analysis module.
import importlib
psychometric = importlib.import_module(f"{_PKG_NAME}.analysis.psychometric_chronometric")
attention = importlib.import_module(f"{_PKG_NAME}.analysis.avg_attention_maps")


def _resolve_checkpoint(arg: Optional[str]) -> str:
    if arg:
        return arg
    ckdir = os.path.join(_PKG_DIR, "checkpoints")
    final = os.path.join(ckdir, "rvit_plus_rl_final.pt")
    latest = os.path.join(ckdir, "rvit_plus_rl_latest.pt")
    if os.path.exists(final):
        return final
    if os.path.exists(latest):
        return latest
    raise FileNotFoundError(f"no checkpoint found in {ckdir} (looked for final/latest)")


# ─────────────────────────────────────────────────────────────────────────────
# Digest — read the CSVs the scripts wrote and print the headline numbers
# ─────────────────────────────────────────────────────────────────────────────


def _read_csv(path: str) -> List[dict]:
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return list(csv.DictReader(f))


def _digest(out_dir: str) -> None:
    print("\n" + "=" * 72)
    print("FIRST-LOOK DIGEST")
    print("=" * 72)

    # EXP1 — signal-strength psychometric, valid vs invalid.
    sig = _read_csv(os.path.join(out_dir, "psychometric_signal.csv"))
    if sig:
        valid = {float(r["mag"]): r for r in sig if r["condition"] == "valid"}
        invalid = {float(r["mag"]): r for r in sig if r["condition"] == "invalid"}
        mags = sorted(valid)
        print("\n[Psychometric] P(hit) vs |Δθ|   (valid = change at cued loc.)")
        print("   |Δθ|   valid  invalid   gap")
        max_gap, max_gap_mag = -1.0, None
        for m in mags:
            hv, hi = float(valid[m]["hit_rate"]), float(invalid[m]["hit_rate"])
            gap = hv - hi
            if gap > max_gap:
                max_gap, max_gap_mag = gap, m
            print(f"  {m:5.0f}   {hv:5.3f}   {hi:5.3f}   {gap:+.3f}")

        def _thresh(d):  # first magnitude crossing 0.5 hit rate (linear interp)
            xs = mags
            for i in range(1, len(xs)):
                y0, y1 = float(d[xs[i-1]]["hit_rate"]), float(d[xs[i]]["hit_rate"])
                if y0 < 0.5 <= y1:
                    f = (0.5 - y0) / (y1 - y0) if y1 > y0 else 0.0
                    return xs[i-1] + f * (xs[i] - xs[i-1])
            return float("nan")
        tv, ti = _thresh(valid), _thresh(invalid)
        print(f"   → 50% threshold: valid ≈ {tv:.1f}°, invalid ≈ {ti:.1f}°  "
              f"(benefit {ti - tv:+.1f}°);  max P(hit) gap {max_gap:+.3f} @ |Δθ|={max_gap_mag:.0f}°")
        verdict = "PRESENT" if max_gap > 0.05 else "absent/weak"
        print(f"   → spatial cueing/validity effect: {verdict}")

    # EXP2 — validity scaling.
    val = _read_csv(os.path.join(out_dir, "psychometric_validity.csv"))
    if val:
        print("\n[Validity scaling] cued P(hit) & RT vs displayed ring validity")
        for r in val:
            print(f"   validity={float(r['validity']):.2f}  hit={float(r['hit_rate']):.3f}  rt={float(r['median_rt']):.2f}")
        hrs = [float(r["hit_rate"]) for r in val]
        trend = hrs[-1] - hrs[0]
        print(f"   → accuracy trend (1.0 − 0.25): {trend:+.3f} "
              f"({'scales with validity' if trend > 0.05 else 'flat/null'})")

    # EXP3 — value scaling.
    valu = _read_csv(os.path.join(out_dir, "psychometric_value.csv"))
    if valu:
        print("\n[Value scaling] cued P(hit) & RT vs cue value")
        for r in valu:
            print(f"   {r['color']:5s} (v={r['value']})  hit={float(r['hit_rate']):.3f}  rt={float(r['median_rt']):.2f}")
        hrs = [float(r["hit_rate"]) for r in valu]
        spread = max(hrs) - min(hrs)
        print(f"   → accuracy spread across value: {spread:.3f} "
              f"({'value modulation' if spread > 0.05 else 'flat/null'})")

    print("\n[Attention] channel/head-summed heatmaps written:")
    figs = sorted(f for f in os.listdir(out_dir) if f.startswith("avg_attn_") and f.endswith(".png"))
    for f in figs:
        print(f"   {f}")
    print("=" * 72)
    print(f"All figures + CSVs: {out_dir}")
    print("=" * 72)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Standardized first-look analysis of a trained RViT+ model.")
    ap.add_argument("--checkpoint", default=None,
                    help="checkpoint path (default: <pkg>/checkpoints/rvit_plus_rl_final.pt, "
                         "fallback latest.pt)")
    ap.add_argument("--config", default=None)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--out-dir", default=os.path.join(_HERE, "figures", "first_look"))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=None,
                    help="trials per cell (default 200; --thorough bumps to 384)")
    ap.add_argument("--thorough", action="store_true",
                    help="more trials + finer magnitude bins (slower, smoother curves)")
    ap.add_argument("--skip-psychometric", action="store_true")
    ap.add_argument("--skip-attention", action="store_true")
    ap.add_argument("--open", action="store_true", help="open the output folder in Finder (macOS)")
    args = ap.parse_args(argv)

    ckpt = _resolve_checkpoint(args.checkpoint)
    os.makedirs(args.out_dir, exist_ok=True)
    n_trials = args.n_trials if args.n_trials is not None else (384 if args.thorough else 200)
    att_trials = max(120, n_trials - 64)

    print("#" * 72)
    print(f"# FIRST LOOK  ·  {_PKG_NAME}")
    print(f"# checkpoint : {ckpt}")
    print(f"# device     : {args.device}   n_trials: {n_trials}   out: {args.out_dir}")
    print("#" * 72)

    common = ["--checkpoint", ckpt, "--device", args.device,
              "--out-dir", args.out_dir, "--seed", str(args.seed)]
    if args.config:
        common += ["--config", args.config]

    if not args.skip_psychometric:
        print("\n>>> [1/2] psychometric / chronometric")
        pc_args = common + ["--n-trials", str(n_trials)]
        if args.thorough:
            pc_args += ["--mag-bins", "2", "4", "7", "10", "14", "18", "24", "32", "44", "64"]
        psychometric.main(pc_args)

    if not args.skip_attention:
        print("\n>>> [2/2] averaged attention maps")
        att_args = common + ["--n-trials", str(att_trials)]
        attention.main(att_args)

    _digest(args.out_dir)

    if args.open:
        try:
            subprocess.run(["open", args.out_dir], check=False)
        except Exception as e:  # pragma: no cover
            print(f"[open] could not open Finder: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
