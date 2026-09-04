#!/usr/bin/env python3
"""Counterphased difference-in-differences across the ratio-1 sensitivity sweep.

Runs after the sweep, on the JSON/NPZ that each training job wrote. It touches no model
and needs no GPU -- every number here is post-processing of recorded measurements.

The difference-in-differences needs BOTH lineages, so it cannot live inside a single
training job (each job trains one policy). It is therefore the one step that is
deliberately outside the train-and-measure job.

    DiD = 0.5 * [ (loc0 - loc3 | high=loc0) - (loc0 - loc3 | high=loc3) ]

Two error terms are reported, and the distinction is the reason the sweep runs five
seeds per lineage rather than one:

  seed_level   -- the DiD is formed WITHIN each seed by pairing that seed's two
                  lineages, then averaged across seeds. The interval is over seeds, so
                  it carries a between-model error term and supports a claim about the
                  architecture rather than about two particular policies. This is the
                  primary result.

  trial_level  -- the August procedure: pool trials across seeds and bootstrap over
                  trials. Reported only for comparability with the August numbers. It
                  has no between-model term and its interval will be narrower for that
                  reason alone, not because the estimate is better determined.

Primary endpoint: counterphased delta-d' between locations, expected positive.
Specificity check: |delta-c| <= 0.2.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_TREE = Path(__file__).resolve().parent
if str(_TREE) not in sys.path:
    sys.path.insert(0, str(_TREE))

# Import the assay's own d'/c rather than reimplementing it. The clamp is applied to the
# RATE, not to a rounded success count, and getting that detail wrong would quietly make
# these numbers non-comparable with both the assay output and the August report.
from experiments.luo2015_episodic.evaluate_selected_replication import _dc

EQUIVALENCE_BOUND = 0.2

# Two-sided 97.5th-percentile t critical values by degrees of freedom. The sweep runs five
# seeds per lineage, so df = 4 and t = 2.776 -- against 1.96 for a normal approximation.
# Using the normal here would make every interval about 30% too narrow, which is enough on
# its own to turn a failed primary endpoint into a passing one. Tabulated rather than taken
# from scipy so the analysis has no dependency beyond numpy.
_T_CRIT_975 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306,
    9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080, 22: 2.074,
    23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045,
    30: 2.042,
}


def t_critical(df: int) -> float:
    """Two-sided 95% t critical value, falling back to the normal limit for large df."""
    if df <= 0:
        return float("nan")
    return _T_CRIT_975.get(int(df), 1.959963984540054)


def load_runs(result_dir: Path) -> list[dict]:
    runs = []
    for path in sorted(result_dir.glob("*.json")):
        if path.name.endswith(".indicators.json"):
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if "summaries" not in payload:
            continue
        payload["_json_path"] = path
        indicators = path.with_suffix(".indicators.npz")
        payload["_indicator_path"] = indicators if indicators.exists() else None
        runs.append(payload)
    if not runs:
        raise SystemExit(f"no assay result JSON found in {result_dir}")
    return runs


def seed_level_did(runs: list[dict], condition: str) -> dict:
    """Pair the two lineages within each seed, then average the DiD across seeds."""
    # cells[theta][seed][condition_loc][loc] = {"dprime": .., "criterion": ..}
    cells: dict[float, dict[int, dict[int, dict[int, dict]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(dict)))
    for run in runs:
        seed = run["checkpoint_provenance"].get("seed")
        condition_loc = int(run["condition_loc"])
        for summary in run["summaries"]:
            if summary["measurement_condition"] != condition:
                continue
            theta = float(summary["evaluation_theta"])
            for loc in (0, 3):
                metrics = summary["locations"][str(loc)]
                cells[theta][int(seed)][condition_loc][loc] = {
                    "dprime": float(metrics["dprime"]),
                    "criterion": float(metrics["criterion"]),
                }

    out: dict[str, dict] = {}
    for theta in sorted(cells):
        per_metric: dict[str, list[float]] = {"dprime": [], "criterion": []}
        seeds_used = []
        for seed in sorted(cells[theta]):
            by_condition = cells[theta][seed]
            if set(by_condition) != {0, 3}:
                continue  # this seed is missing one lineage; it cannot form a DiD
            seeds_used.append(seed)
            for metric in per_metric:
                hi0 = by_condition[0][0][metric] - by_condition[0][3][metric]
                hi3 = by_condition[3][0][metric] - by_condition[3][3][metric]
                per_metric[metric].append(0.5 * (hi0 - hi3))

        entry: dict[str, object] = {"seeds": seeds_used, "n_seeds": len(seeds_used)}
        for metric, values in per_metric.items():
            arr = np.asarray(values, dtype=float)
            if arr.size == 0:
                entry[metric] = None
                continue
            mean = float(arr.mean())
            if arr.size > 1:
                df = arr.size - 1
                sem = float(arr.std(ddof=1) / np.sqrt(arr.size))
                half = t_critical(df) * sem
                ci = [mean - half, mean + half]
            else:
                df, sem, ci = 0, float("nan"), [float("nan"), float("nan")]
            entry[metric] = {
                "mean": mean, "sem": sem, "df": int(df),
                "t_crit": t_critical(df) if arr.size > 1 else float("nan"),
                "ci95_t": ci,
                "per_seed": [float(v) for v in arr],
            }
        if entry.get("dprime") and entry.get("criterion"):
            d_ci = entry["dprime"]["ci95_t"]
            c_ci = entry["criterion"]["ci95_t"]
            entry["tests"] = {
                "primary_metric": "dprime",
                "primary_point_positive": entry["dprime"]["mean"] > 0,
                "primary_ci_excludes_zero_positive": bool(d_ci[0] > 0),
                "specificity_metric": "criterion",
                "specificity_equivalence_bound": EQUIVALENCE_BOUND,
                "specificity_point_inside_bound": bool(abs(entry["criterion"]["mean"]) <= EQUIVALENCE_BOUND),
                "specificity_ci_inside_bound": bool(
                    c_ci[0] > -EQUIVALENCE_BOUND and c_ci[1] < EQUIVALENCE_BOUND),
            }
            entry["tests"]["strict_counterphased_dissociation"] = bool(
                entry["tests"]["primary_ci_excludes_zero_positive"]
                and entry["tests"]["specificity_ci_inside_bound"])
        out[f"{theta:g}"] = entry
    return out


def trial_level_did(runs: list[dict], condition: str, draws: int, seed: int) -> dict:
    """August's procedure: pool trials across seeds, bootstrap over trials."""
    pooled: dict[float, dict[tuple[int, int], dict[str, list[np.ndarray]]]] = defaultdict(
        lambda: defaultdict(lambda: {"hit": [], "fa": []}))
    for run in runs:
        if run["_indicator_path"] is None:
            continue
        condition_loc = int(run["condition_loc"])
        with np.load(run["_indicator_path"]) as handle:
            for key in handle.files:
                cond, theta_token, loc_token, kind = key.split("|")
                if cond != condition:
                    continue
                theta = float(theta_token.removeprefix("theta"))
                loc = int(loc_token.removeprefix("loc"))
                pooled[theta][(condition_loc, loc)][kind].append(handle[key])

    rng = np.random.default_rng(seed)
    out: dict[str, dict] = {}
    for theta in sorted(pooled):
        cells = pooled[theta]
        if set(cells) != {(0, 0), (0, 3), (3, 0), (3, 3)}:
            continue
        draws_by_cell: dict[tuple[int, int], dict[str, np.ndarray]] = {}
        point_by_cell: dict[tuple[int, int], tuple[float, float]] = {}
        for key, parts in cells.items():
            hit = np.concatenate(parts["hit"]).astype(float)
            fa = np.concatenate(parts["fa"]).astype(float)
            n_h, n_f = len(hit), len(fa)
            hr = hit[rng.integers(0, n_h, size=(draws, n_h))].mean(axis=1)
            far = fa[rng.integers(0, n_f, size=(draws, n_f))].mean(axis=1)
            d = np.empty(draws)
            c = np.empty(draws)
            for i in range(draws):
                d[i], c[i] = _dc(float(hr[i]), float(far[i]), n_h, n_f)
            draws_by_cell[key] = {"dprime": d, "criterion": c}
            point_by_cell[key] = _dc(float(hit.mean()), float(fa.mean()), n_h, n_f)

        entry: dict[str, object] = {}
        for index, metric in enumerate(("dprime", "criterion")):
            b = {k: v[metric] for k, v in draws_by_cell.items()}
            did = 0.5 * ((b[(0, 0)] - b[(0, 3)]) - (b[(3, 0)] - b[(3, 3)]))
            point = 0.5 * ((point_by_cell[(0, 0)][index] - point_by_cell[(0, 3)][index])
                           - (point_by_cell[(3, 0)][index] - point_by_cell[(3, 3)][index]))
            entry[metric] = {
                "point": float(point),
                "bootstrap_mean": float(did.mean()),
                "ci95": [float(np.quantile(did, 0.025)), float(np.quantile(did, 0.975))],
                "draws": int(draws),
            }
        out[f"{theta:g}"] = entry
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results", type=Path, required=True,
                        help="directory holding the per-run assay JSON and .npz files")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--condition", default="trained_noise",
                        choices=("trained_noise", "zero_mnemonic_noise"))
    parser.add_argument("--bootstrap-draws", type=int, default=5000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260902)
    parser.add_argument("--skip-trial-level", action="store_true")
    args = parser.parse_args(argv)

    runs = load_runs(args.results)
    lineages = defaultdict(list)
    for run in runs:
        lineages[int(run["condition_loc"])].append(run["checkpoint_provenance"].get("seed"))
    print("== runs found ==")
    for condition_loc in sorted(lineages):
        print(f"  high_loc={condition_loc}: {len(lineages[condition_loc])} runs, "
              f"seeds {sorted(s for s in lineages[condition_loc] if s is not None)}")

    ratios = {(r["checkpoint_provenance"].get("high_hit_cr_ratio"),
               r["checkpoint_provenance"].get("low_hit_cr_ratio")) for r in runs}
    print(f"  H:CR ratios across runs: {sorted(ratios, key=str)}")
    if len(ratios) > 1:
        print("  WARNING: runs do not share one reward table; the DiD mixes conditions")

    seed_level = seed_level_did(runs, args.condition)
    print(f"\n== seed-level counterphased DiD [{args.condition}] ==")
    print("  (primary; interval is over seeds and carries a between-model error term)")
    for theta, entry in seed_level.items():
        if not entry.get("dprime"):
            print(f"  theta={theta:>5}: only {entry['n_seeds']} paired seed(s); skipped")
            continue
        d, c = entry["dprime"], entry["criterion"]
        tests = entry["tests"]
        print(f"  theta={theta:>5} n={entry['n_seeds']}  "
              f"dd'={d['mean']:+.4f} CI[{d['ci95_t'][0]:+.3f},{d['ci95_t'][1]:+.3f}]  "
              f"dc={c['mean']:+.4f} CI[{c['ci95_t'][0]:+.3f},{c['ci95_t'][1]:+.3f}]  "
              f"primary={'PASS' if tests['primary_ci_excludes_zero_positive'] else 'fail'} "
              f"specificity={'PASS' if tests['specificity_ci_inside_bound'] else 'fail'}")

    payload = {
        "measurement_condition": args.condition,
        "equivalence_bound": EQUIVALENCE_BOUND,
        "n_runs": len(runs),
        "lineages": {str(k): sorted(s for s in v if s is not None) for k, v in lineages.items()},
        "hit_cr_ratios": sorted((list(r) for r in ratios), key=str),
        "seed_level_did": seed_level,
        "source_files": [str(r["_json_path"].name) for r in runs],
    }

    if not args.skip_trial_level:
        trial_level = trial_level_did(runs, args.condition,
                                      args.bootstrap_draws, args.bootstrap_seed)
        payload["trial_level_did"] = trial_level
        print(f"\n== trial-level DiD [{args.condition}] (August-comparable; no between-model term) ==")
        for theta, entry in trial_level.items():
            d, c = entry["dprime"], entry["criterion"]
            print(f"  theta={theta:>5}  dd'={d['point']:+.4f} CI[{d['ci95'][0]:+.3f},{d['ci95'][1]:+.3f}]  "
                  f"dc={c['point']:+.4f} CI[{c['ci95'][0]:+.3f},{c['ci95'][1]:+.3f}]")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\n[analysis] -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
