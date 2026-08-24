#!/usr/bin/env python3
"""Frozen-policy SDT assay for the rescued d_mem=128 curriculum sensitivity pair.

These two checkpoints are PARTIAL (training was terminated for cost before the
20,000-iteration contract), so the terminal-iteration validators in
evaluate_selected_replication.validate_checkpoint do not apply. Everything else
follows the repo's vetted measurement contract: the same balanced trial bank
shared by both policies, trained mnemonic noise on, sampled categorical actions,
SDT denominators after fixation/second-test exclusions, and 5,000-draw bootstrap
CIs.

Three branches:
  own_theta      -- each policy at its own terminal curriculum theta
  common_theta   -- both policies on one shared bank (enables the counterphased DiD)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

# Checkpoints were written under NumPy 2; this controller runs NumPy 1.
sys.modules.setdefault("numpy._core", np.core)
sys.modules.setdefault("numpy._core.multiarray", np.core.multiarray)
sys.modules.setdefault("numpy._core.numeric", np.core.numeric)

import torch

_TREE = Path(__file__).resolve().parent
if str(_TREE) not in sys.path:
    sys.path.insert(0, str(_TREE))

from experiments.luo2015_episodic.analyze_matrix import balanced_trial_bank
from experiments.luo2015_episodic.evaluate_selected_replication import (
    _dc,
    _location_metrics,
    summarize_policy,
)
from luo2015_analysis import luo2015_core as core

EQUIVALENCE_BOUND = 0.2


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checkpoint_facts(path: Path) -> dict:
    ck = torch.load(path, map_location="cpu", weights_only=False)
    env_state = ck.get("environment_state", {})
    env_cfg = env_state.get("environment_config", {})
    args = ck.get("training_args", {}) or {}
    return {
        "path": str(path),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "iter": int(ck.get("iter", -1)),
        "terminal_theta": float(env_state.get("theta", -1)),
        "curriculum": bool(env_state.get("curriculum", False)),
        "curr_threshold": env_state.get("curr_threshold"),
        "curr_step": env_state.get("curr_step"),
        "curr_window": env_state.get("curr_window"),
        "theta_floor": env_state.get("theta_floor"),
        "high_loc": args.get("high_loc", env_cfg.get("condition_loc")),
        "memory_noise_std": ck.get("model_kwargs", {}).get("memory_noise_std"),
        "d_mem": ck.get("model_kwargs", {}).get("d_mem"),
        "dual_streams": args.get("dual_actor_critic_streams"),
        "gamma": ck.get("ppo_config", {}).get("gamma"),
        "bc_alpha": ck.get("ppo_config", {}).get("bc_alpha"),
        "orientation_sampling": env_cfg.get("orientation_sampling"),
        "orientation_period_degrees": env_cfg.get("orientation_period_degrees"),
        "init_mode": ck.get("initialization_contract", {}).get("mode"),
        "run_started_at_utc": ck.get("run_started_at_utc"),
        "training_args_present": bool(args),
    }


def press_batched(model, videos, batch_size, device, **kwargs) -> np.ndarray:
    out = []
    for start in range(0, len(videos), batch_size):
        chunk = videos[start:start + batch_size].to(device)
        out.append(core.press_times(model, chunk, **kwargs))
    return np.concatenate(out)


def _valid_arrays(change_press, no_change_press, change_locs, no_change_locs, loc):
    """Return (hit_indicator, fa_indicator) for one location, post-exclusion."""
    _, hit, fa = _location_metrics(
        np.asarray(change_press), np.asarray(no_change_press),
        np.asarray(change_locs), np.asarray(no_change_locs), loc)
    return hit, fa


def did_bootstrap(cells: dict, metric: str, draws: int, seed: int) -> dict:
    """Bootstrap the counterphased difference-in-differences.

    cells[(condition_loc, loc)] = (hit_indicator, fa_indicator)
    DiD = 0.5 * ((loc0 - loc3 | model_hi0) - (loc0 - loc3 | model_hi3))
    """
    rng = np.random.default_rng(seed)
    per_cell = {}
    for key, (hit, fa) in cells.items():
        n_h, n_f = len(hit), len(fa)
        hr = hit[rng.integers(0, n_h, size=(draws, n_h))].mean(axis=1)
        far = fa[rng.integers(0, n_f, size=(draws, n_f))].mean(axis=1)
        values = np.empty(draws)
        for i, (h, f) in enumerate(zip(hr, far)):
            d, c = _dc(float(h), float(f), n_h, n_f)
            values[i] = d if metric == "dprime" else c
        per_cell[key] = values
    did = 0.5 * ((per_cell[(0, 0)] - per_cell[(0, 3)])
                 - (per_cell[(3, 0)] - per_cell[(3, 3)]))
    return {
        "point": float(0.5 * ((_point(cells, 0, 0, metric) - _point(cells, 0, 3, metric))
                              - (_point(cells, 3, 0, metric) - _point(cells, 3, 3, metric)))),
        "bootstrap_mean": float(did.mean()),
        "ci95": [float(np.quantile(did, 0.025)), float(np.quantile(did, 0.975))],
        "draws": int(draws),
    }


def _point(cells, condition_loc, loc, metric):
    hit, fa = cells[(condition_loc, loc)]
    d, c = _dc(float(hit.mean()), float(fa.mean()), len(hit), len(fa))
    return d if metric == "dprime" else c


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rescue-root", type=Path,
                        default=Path(r"C:\Users\jomor\runpod_rescue\20260817"))
    parser.add_argument("--output", type=Path, default=_TREE / "results" / "partial_sdt_results.json")
    parser.add_argument("--trials", type=int, default=2000,
                        help="trials per change-status per location")
    parser.add_argument("--common-thetas", type=float, nargs="+", default=[47.0, 50.0])
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--bootstrap-draws", type=int, default=5000)
    parser.add_argument("--eval-seed", type=int, default=20260818)
    parser.add_argument("--sensory-noise", type=float, default=5.0)
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args(argv)

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("PyTorch CUDA unavailable")
    core.DEVICE = device
    args.output.parent.mkdir(parents=True, exist_ok=True)

    specs = [
        {"id": "dmem128_sensitivity_loc0", "condition_loc": 0,
         "checkpoint": args.rescue_root / "loc0" / "run" / "rvit_plus_rl_latest.pt"},
        {"id": "dmem128_sensitivity_loc3", "condition_loc": 3,
         "checkpoint": args.rescue_root / "loc3" / "run" / "rvit_plus_rl_latest.pt"},
    ]

    print("== checkpoint provenance ==")
    for spec in specs:
        spec["facts"] = checkpoint_facts(spec["checkpoint"])
        f = spec["facts"]
        print(f"  {spec['id']}: iter={f['iter']} theta={f['terminal_theta']} "
              f"high_loc={f['high_loc']} d_mem={f['d_mem']} noise={f['memory_noise_std']} "
              f"gamma={f['gamma']} dual={f['dual_streams']}")

    thetas = sorted({float(s["facts"]["terminal_theta"]) for s in specs}
                    | {float(t) for t in args.common_thetas})
    print(f"\n== building {len(thetas)} trial banks at theta={thetas} "
          f"({args.trials} trials/status/location) ==")
    banks = {}
    for index, theta in enumerate(thetas):
        t0 = time.time()
        banks[theta] = balanced_trial_bank(
            magnitude=float(theta), trials_per_location=int(args.trials),
            seed=int(args.eval_seed) + index, task="luo2015_sensitivity",
            noise_multiplier=float(args.sensory_noise), spatial_grid_size=2)
        print(f"  theta={theta}: {time.time() - t0:.1f}s")

    conditions = {
        "trained_noise": {"inject_memory_noise": True, "sample_actions": True},
        "zero_mnemonic_noise": {"inject_memory_noise": False, "sample_actions": True},
    }

    results = {"own_theta": [], "common_theta": {str(t): [] for t in args.common_thetas}}
    did_cells = {str(t): {} for t in args.common_thetas}

    for model_index, spec in enumerate(specs):
        print(f"\n== {spec['id']} ==")
        model, iteration = core.load_model(str(spec["checkpoint"]))
        own_theta = float(spec["facts"]["terminal_theta"])

        for condition_index, (condition, kwargs) in enumerate(conditions.items()):
            seed = int(args.eval_seed) + model_index * 100 + condition_index
            torch.manual_seed(seed)
            if device.type == "cuda":
                torch.cuda.manual_seed_all(seed)
            cv, nv, cl, nl = banks[own_theta]
            cp = press_batched(model, cv, args.batch_size, device, **kwargs)
            npress = press_batched(model, nv, args.batch_size, device, **kwargs)
            summary = summarize_policy(cp, npress, cl, nl,
                                       condition_loc=int(spec["condition_loc"]),
                                       session="sensitivity",
                                       bootstrap_draws=args.bootstrap_draws,
                                       bootstrap_seed=seed)
            summary.update({
                "id": spec["id"], "measurement_condition": condition,
                "evaluation_theta": own_theta, "checkpoint_iteration": iteration,
                "checkpoint_provenance": spec["facts"], "policy_seed": seed,
                "claim_scope": "partial_checkpoint_matched_terminal_difficulty",
            })
            results["own_theta"].append(summary)
            contrast = summary["contrasts"]["condition_minus_control"]
            ci = summary["contrasts"]["bootstrap_ci95"]
            print(f"  own theta={own_theta} [{condition}] "
                  f"dd'={contrast['dprime']:+.4f} CI[{ci['dprime'][0]:+.3f},{ci['dprime'][1]:+.3f}] "
                  f"dc={contrast['criterion']:+.4f} CI[{ci['criterion'][0]:+.3f},{ci['criterion'][1]:+.3f}] "
                  f"strict={summary['paper_like_tests']['strict_behavioral_dissociation']}")

        for theta in args.common_thetas:
            theta = float(theta)
            seed = int(args.eval_seed) + 10_000 + model_index * 10 + int(theta)
            torch.manual_seed(seed)
            if device.type == "cuda":
                torch.cuda.manual_seed_all(seed)
            cv, nv, cl, nl = banks[theta]
            kwargs = conditions["trained_noise"]
            cp = press_batched(model, cv, args.batch_size, device, **kwargs)
            npress = press_batched(model, nv, args.batch_size, device, **kwargs)
            summary = summarize_policy(cp, npress, cl, nl,
                                       condition_loc=int(spec["condition_loc"]),
                                       session="sensitivity",
                                       bootstrap_draws=args.bootstrap_draws,
                                       bootstrap_seed=seed)
            summary.update({
                "id": spec["id"], "measurement_condition": "trained_noise",
                "evaluation_theta": theta, "checkpoint_iteration": iteration,
                "checkpoint_provenance": spec["facts"], "policy_seed": seed,
                "claim_scope": "partial_checkpoint_common_theta_shared_bank",
            })
            results["common_theta"][str(theta)].append(summary)
            for loc in (0, 3):
                did_cells[str(theta)][(int(spec["condition_loc"]), loc)] = _valid_arrays(
                    cp, npress, cl, nl, loc)
            contrast = summary["contrasts"]["condition_minus_control"]
            print(f"  common theta={theta} dd'={contrast['dprime']:+.4f} "
                  f"dc={contrast['criterion']:+.4f}")

        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    print("\n== counterphased difference-in-differences ==")
    did_out = {}
    for theta_key, cells in did_cells.items():
        entry = {}
        for metric in ("dprime", "criterion"):
            entry[metric] = did_bootstrap(cells, metric, args.bootstrap_draws,
                                          int(args.eval_seed) + 777)
        primary = entry["dprime"]
        specificity = entry["criterion"]
        entry["tests"] = {
            "primary_metric": "dprime",
            "primary_expected_sign": "positive",
            "primary_point_positive": bool(primary["point"] > 0),
            "primary_ci_excludes_zero_positive": bool(primary["ci95"][0] > 0),
            "specificity_metric": "criterion",
            "specificity_equivalence_bound": EQUIVALENCE_BOUND,
            "specificity_ci_inside_bound": bool(
                specificity["ci95"][0] > -EQUIVALENCE_BOUND
                and specificity["ci95"][1] < EQUIVALENCE_BOUND),
            "strict_counterphased_dissociation": bool(
                primary["ci95"][0] > 0
                and specificity["ci95"][0] > -EQUIVALENCE_BOUND
                and specificity["ci95"][1] < EQUIVALENCE_BOUND),
        }
        did_out[theta_key] = entry
        print(f"  theta={theta_key}: "
              f"DiD d'={primary['point']:+.4f} CI[{primary['ci95'][0]:+.3f},{primary['ci95'][1]:+.3f}]  "
              f"DiD c={specificity['point']:+.4f} CI[{specificity['ci95'][0]:+.3f},{specificity['ci95'][1]:+.3f}]  "
              f"strict={entry['tests']['strict_counterphased_dissociation']}")

    output = {
        "schema_version": 1,
        "design": "dmem128_dualstream_sensitivity_counterphase_PARTIAL_checkpoints",
        "claim_scope": ("partial (non-terminal) checkpoints rescued before pod termination; "
                        "measurement contract matches the repo frozen-policy SDT assay but the "
                        "20000-iteration training contract was not met"),
        "paper_targets": {
            "sensitivity": "positive counterphased dprime difference-in-differences",
            "specificity": "criterion cross-effect CI inside abs 0.2 equivalence bound",
            "equivalence_bound_abs": EQUIVALENCE_BOUND,
        },
        "evaluation_contract": {
            "trials_per_status_per_location": int(args.trials),
            "bootstrap_draws": int(args.bootstrap_draws),
            "evaluation_seed": int(args.eval_seed),
            "sensory_orientation_noise_sd": float(args.sensory_noise),
            "policy_action_semantics": "sampled_categorical",
            "balanced_change_status_and_locations": True,
            "initial_orientations": "iid_uniform_axial_0_180",
            "change_distribution": "signed_delta_uniform(-theta,+theta)",
            "timeline_frames": core.T,
            "device": str(device),
            "torch": torch.__version__,
            "numpy": np.__version__,
            "source_tree": "rescued pod project (exact training source)",
        },
        "own_theta": results["own_theta"],
        "common_theta": results["common_theta"],
        "counterphased_did": did_out,
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True, default=str) + "\n",
                           encoding="utf-8")
    print(f"\nwrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
