"""
E5 — behaviour broken down by validity / proportion (James's explicit 2026-06-09 ask:
"I would love to see this broken down by the validities ... maybe it's driven a lot by
the higher validity?").

For a trained FiLM model on a task, reports per proportion (cue validity):
  • hit rate, false-alarm rate, d', criterion          (SDT)
  • cueing effect = hit_rate(valid) − hit_rate(invalid) on change trials
  • mean reaction time (declare_t − change_time) for hits
  • if the task has value cues, the same split by cue value/colour (the "reward effect")

    python RViT_plus_battery/analysis/e5_validity_breakdown.py \
        --checkpoint ~/rvit_plus_checkpoints/film_validity4/rvit_plus_validity4_final.pt \
        --task validity4 --n-trials 4000 --out reports/e5_validity4.csv

DO NOT run while the live MPS training jobs are going (CPU safety).
"""
from __future__ import annotations

import argparse
import csv
import os

import numpy as np

from common import load_model, rollout, sdt, make_env


def summarize(rec, by_value: bool = False):
    rows = []
    props = sorted(set(rec["proportion"].tolist()))
    groups = [("all", np.ones_like(rec["change"], dtype=bool))]
    if by_value:
        for col in sorted(set(rec["cue_color"].tolist())):
            groups.append((f"cue={col}", rec["cue_color"] == col))
    for gname, gmask in groups:
        for p in props:
            m = gmask & (rec["proportion"] == p)
            chg = m & (rec["change"] == 1)
            noc = m & (rec["change"] == 0)
            if chg.sum() == 0 or noc.sum() == 0:
                continue
            hr = rec["hit"][chg].mean()
            far = rec["fa"][noc].mean()
            valid_chg = chg & (rec["valid"] == 1)
            invalid_chg = chg & (rec["valid"] == 0)
            hr_v = rec["hit"][valid_chg].mean() if valid_chg.sum() else np.nan
            hr_iv = rec["hit"][invalid_chg].mean() if invalid_chg.sum() else np.nan
            rt = np.nanmean(rec["rt"][chg]) if chg.sum() else np.nan
            s = sdt(hr, far)
            rows.append(dict(group=gname, proportion=p, n_change=int(chg.sum()),
                             hit_rate=round(float(hr), 4), fa_rate=round(float(far), 4),
                             dprime=round(s["dprime"], 4), criterion=round(s["criterion"], 4),
                             cueing_effect=round(float(hr_v - hr_iv), 4)
                             if not np.isnan(hr_v) and not np.isnan(hr_iv) else np.nan,
                             mean_rt=round(float(rt), 3) if not np.isnan(rt) else np.nan))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--n-trials", type=int, default=4000)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    model = load_model(args.checkpoint, task=args.task, device=args.device)
    env = make_env(args.task)
    rec = rollout(model, env, n_trials=args.n_trials, device=args.device, greedy=True)
    by_value = getattr(env, "value_cues", False)
    rows = summarize(rec, by_value=by_value)

    cols = ["group", "proportion", "n_change", "hit_rate", "fa_rate", "dprime",
            "criterion", "cueing_effect", "mean_rt"]
    print("\nE5 — behaviour by validity (task=%s, n=%d):" % (args.task, args.n_trials))
    print("  " + " | ".join(f"{c:>12}" for c in cols))
    for r in rows:
        print("  " + " | ".join(f"{str(r[c]):>12}" for c in cols))
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader(); w.writerows(rows)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
