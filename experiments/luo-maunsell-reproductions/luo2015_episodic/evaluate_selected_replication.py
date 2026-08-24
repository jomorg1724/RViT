#!/usr/bin/env python3
"""Matched frozen-policy behavioral assay for selected Luo--Maunsell agents.

Primary evaluation uses the exact training task distribution: iid axial sample
orientations, signed Delta ~ Uniform(-65, 65), sensory jitter 5 deg, checkpoint-
configured mnemonic noise enabled, and sampled categorical policy actions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import NormalDist
from typing import Callable

import numpy as np
import torch

from experiments.luo2015_episodic.analyze_matrix import balanced_trial_bank
from luo2015_analysis import luo2015_core as core


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rate(value: float, n: int) -> float:
    return min(max(float(value), 1.0 / (2 * n)), 1.0 - 1.0 / (2 * n))


def _dc(hit_rate: float, false_alarm_rate: float, n_hit: int, n_fa: int) -> tuple[float, float]:
    normal = NormalDist()
    zh = normal.inv_cdf(_rate(hit_rate, n_hit))
    zf = normal.inv_cdf(_rate(false_alarm_rate, n_fa))
    return float(zh - zf), float(-0.5 * (zh + zf))


def _wilson(successes: int, total: int, z: float = 1.959963984540054) -> list[float]:
    p = successes / total
    denom = 1.0 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half = z * ((p * (1 - p) / total + z * z / (4 * total * total)) ** 0.5) / denom
    return [float(center - half), float(center + half)]


def _outcomes(change_true: int, press: np.ndarray) -> np.ndarray:
    return np.asarray([core.classify_trial(change_true, int(value)) for value in press])


def _histogram(values: np.ndarray) -> dict[str, int]:
    return {**{str(frame): int((values == frame).sum()) for frame in range(core.T)},
            "no_declaration": int((values < 0).sum())}


def _location_metrics(change_press: np.ndarray, no_change_press: np.ndarray,
                      change_locs: np.ndarray, no_change_locs: np.ndarray, loc: int) -> tuple[dict, np.ndarray, np.ndarray]:
    cp = change_press[change_locs == loc]
    np_ = no_change_press[no_change_locs == loc]
    co = _outcomes(1, cp)
    no = _outcomes(0, np_)
    valid_c = np.isin(co, ("hit", "miss"))
    valid_n = np.isin(no, ("false_alarm", "correct_rejection"))
    hit = co[valid_c] == "hit"
    fa = no[valid_n] == "false_alarm"
    if not len(hit) or not len(fa):
        raise RuntimeError(f"location {loc} has no valid SDT denominator")
    hr, far = float(hit.mean()), float(fa.mean())
    dprime, criterion = _dc(hr, far, len(hit), len(fa))
    metrics = {
        "total_change": int(len(cp)), "total_no_change": int(len(np_)),
        "n_change": int(len(hit)), "n_no_change": int(len(fa)),
        "excluded_change": int((~valid_c).sum()), "excluded_no_change": int((~valid_n).sum()),
        "valid_fraction_change": float(valid_c.mean()), "valid_fraction_no_change": float(valid_n.mean()),
        "hit_rate": hr, "hit_rate_ci95_wilson": _wilson(int(hit.sum()), len(hit)),
        "false_alarm_rate": far, "false_alarm_rate_ci95_wilson": _wilson(int(fa.sum()), len(fa)),
        "change_accuracy": hr, "no_change_accuracy": float(1.0 - far),
        "balanced_accuracy": float(0.5 * (hr + 1.0 - far)),
        "dprime": dprime, "criterion": criterion,
        "change_press_histogram": _histogram(cp), "no_change_press_histogram": _histogram(np_),
        "mean_hit_frame": float(cp[co == "hit"].mean()) if np.any(co == "hit") else None,
        "mean_false_alarm_frame": float(np_[no == "false_alarm"].mean()) if np.any(no == "false_alarm") else None,
        "mean_correct_rejection_frame": float(np_[no == "correct_rejection"].mean()) if np.any(no == "correct_rejection") else None,
        "fixation_break_change": int((co == "fixation_break").sum()),
        "fixation_break_no_change": int((no == "fixation_break").sum()),
        "second_test_miss_no_change": int((no == "second_test_miss").sum()),
    }
    return metrics, hit.astype(np.int8), fa.astype(np.int8)


def _bootstrap(hit_by_loc: dict[int, np.ndarray], fa_by_loc: dict[int, np.ndarray],
               condition_loc: int, draws: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    sampled: dict[int, dict[str, np.ndarray]] = {}
    for loc in (0, 3):
        hit, fa = hit_by_loc[loc], fa_by_loc[loc]
        hr = hit[rng.integers(0, len(hit), size=(draws, len(hit)))].mean(axis=1)
        far = fa[rng.integers(0, len(fa), size=(draws, len(fa)))].mean(axis=1)
        d = np.empty(draws); c = np.empty(draws)
        for index, (h, f) in enumerate(zip(hr, far)):
            d[index], c[index] = _dc(float(h), float(f), len(hit), len(fa))
        sampled[loc] = {"dprime": d, "criterion": c}
    control = 3 if condition_loc == 0 else 0
    output = {}
    for metric in ("dprime", "criterion"):
        delta = sampled[condition_loc][metric] - sampled[control][metric]
        output[metric] = [float(np.quantile(delta, 0.025)), float(np.quantile(delta, 0.975))]
    return output


def summarize_policy(change_press: np.ndarray, no_change_press: np.ndarray,
                     change_locs: np.ndarray, no_change_locs: np.ndarray, *,
                     condition_loc: int, session: str, bootstrap_draws: int,
                     bootstrap_seed: int) -> dict:
    metrics: dict[str, dict] = {}
    hits: dict[int, np.ndarray] = {}; fas: dict[int, np.ndarray] = {}
    for loc in (0, 3):
        metrics[str(loc)], hits[loc], fas[loc] = _location_metrics(
            np.asarray(change_press), np.asarray(no_change_press),
            np.asarray(change_locs), np.asarray(no_change_locs), loc)
    control = 3 if condition_loc == 0 else 0
    contrasts = {
        "dprime": float(metrics[str(condition_loc)]["dprime"] - metrics[str(control)]["dprime"]),
        "criterion": float(metrics[str(condition_loc)]["criterion"] - metrics[str(control)]["criterion"]),
        "hit_rate": float(metrics[str(condition_loc)]["hit_rate"] - metrics[str(control)]["hit_rate"]),
        "false_alarm_rate": float(metrics[str(condition_loc)]["false_alarm_rate"] - metrics[str(control)]["false_alarm_rate"]),
        "balanced_accuracy": float(metrics[str(condition_loc)]["balanced_accuracy"] - metrics[str(control)]["balanced_accuracy"]),
    }
    cis = _bootstrap(hits, fas, condition_loc, bootstrap_draws, bootstrap_seed)
    primary_metric = "dprime" if session == "sensitivity" else "criterion"
    primary_sign_ok = contrasts[primary_metric] > 0 if session == "sensitivity" else contrasts[primary_metric] < 0
    primary_ci_ok = cis[primary_metric][0] > 0 if session == "sensitivity" else cis[primary_metric][1] < 0
    specificity_metric = "criterion" if session == "sensitivity" else "dprime"
    equivalence_bound = 0.2
    specificity_equivalent = cis[specificity_metric][0] > -equivalence_bound and cis[specificity_metric][1] < equivalence_bound
    return {
        "condition_loc": condition_loc, "control_loc": control, "session": session,
        "locations": metrics,
        "contrasts": {"condition_minus_control": contrasts, "bootstrap_ci95": cis},
        "paper_like_tests": {
            "primary_metric": primary_metric, "primary_expected_sign": "positive" if session == "sensitivity" else "negative",
            "primary_sign_observed": bool(primary_sign_ok), "primary_ci_excludes_zero_in_expected_direction": bool(primary_ci_ok),
            "specificity_metric": specificity_metric, "specificity_equivalence_bound": equivalence_bound,
            "specificity_ci_inside_equivalence_bound": bool(specificity_equivalent),
            "strict_behavioral_dissociation": bool(primary_ci_ok and specificity_equivalent),
        },
    }


def evaluate_model(model, bank, *, condition_loc: int, session: str, batch_size: int,
                   bootstrap_draws: int, bootstrap_seed: int,
                   press_function: Callable) -> tuple[dict, dict[str, np.ndarray]]:
    cv, nv, cl, nl = bank
    cp = press_function(model, cv, batch_size, inject_memory_noise=True, sample_actions=True)
    np_ = press_function(model, nv, batch_size, inject_memory_noise=True, sample_actions=True)
    result = summarize_policy(cp, np_, cl, nl, condition_loc=condition_loc, session=session,
                              bootstrap_draws=bootstrap_draws, bootstrap_seed=bootstrap_seed)
    result["evaluation_contract"] = {"memory_noise_enabled": True, "sample_actions": True}
    return result, {"change_press": cp, "no_change_press": np_,
                    "change_locations": cl, "no_change_locations": nl}


def _press_on_device(device: torch.device):
    def run(model, videos, batch_size, **kwargs):
        outputs = []
        for start in range(0, len(videos), batch_size):
            outputs.append(core.press_times(model, videos[start:start + batch_size].to(device), **kwargs))
        return np.concatenate(outputs)
    return run


def validate_checkpoint(path: Path, spec: dict, contract: dict) -> dict:
    if path.stat().st_size != int(spec["checkpoint_bytes"]):
        raise RuntimeError(f"checkpoint byte mismatch: {spec['id']}")
    actual = sha256(path)
    if actual != spec["checkpoint_sha256"]:
        raise RuntimeError(f"checkpoint SHA-256 mismatch: {spec['id']}")
    ck = torch.load(path, map_location="cpu", weights_only=False)
    env = ck.get("environment_state", {}).get("environment_config", {})
    args = ck.get("training_args", {})
    if int(ck.get("iter", -1)) != 19999 or ck.get("task") != spec["task"]:
        raise RuntimeError(f"terminal task/iteration mismatch: {spec['id']}")
    if float(ck.get("ppo_config", {}).get("gamma", -1)) != float(spec["gamma"]):
        raise RuntimeError(f"gamma mismatch: {spec['id']}")
    if int(args.get("high_loc", -1)) != int(spec["condition_loc"]):
        raise RuntimeError(f"condition location mismatch: {spec['id']}")
    if ck.get("initialization_contract", {}).get("mode") != "fresh":
        raise RuntimeError(f"checkpoint is not fresh-initialized: {spec['id']}")
    if env.get("orientation_sampling") != "independent_uniform_axial_0_180" or float(env.get("orientation_period_degrees", -1)) != 180.0:
        raise RuntimeError(f"invalid orientation contract: {spec['id']}")
    memory_values = [ck.get("model_kwargs", {}).get("memory_noise_std"), args.get("memory_noise_std")]
    if not any(value is not None and abs(float(value) - float(contract["mnemonic_noise_sd"])) < 1e-12 for value in memory_values):
        raise RuntimeError(f"mnemonic-noise mismatch: {spec['id']}")
    return {"iteration": 19999, "actual_sha256": actual, "validated": True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--checkpoint-root", type=Path, default=None,
                        help="optional directory containing checkpoints named <model-id>.pt")
    parser.add_argument("--trials-per-status-per-location", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--bootstrap-draws", type=int, default=5000)
    args = parser.parse_args(argv)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    contract = manifest["evaluation_contract"]
    n = args.trials_per_status_per_location or int(contract["trials_per_status_per_location"])
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("PyTorch CUDA unavailable")
    core.DEVICE = device
    args.output_dir.mkdir(parents=True, exist_ok=True)
    bank = balanced_trial_bank(magnitude=float(contract["theta"]), trials_per_location=n,
                               seed=int(contract["evaluation_seed"]), task="luo2015_sensitivity",
                               noise_multiplier=float(contract["sensory_orientation_noise_sd"]), spatial_grid_size=2)
    results = []
    for index, spec in enumerate(manifest["models"]):
        path = (
            args.checkpoint_root / f"{spec['id']}.pt"
            if args.checkpoint_root is not None else Path(spec["checkpoint"])
        )
        provenance = validate_checkpoint(path, spec, contract)
        torch.manual_seed(int(contract["evaluation_seed"]))
        if device.type == "cuda": torch.cuda.manual_seed_all(int(contract["evaluation_seed"]))
        model, iteration = core.load_model(str(path))
        summary, raw = evaluate_model(model, bank, condition_loc=int(spec["condition_loc"]), session=spec["session"],
                                      batch_size=args.batch_size, bootstrap_draws=args.bootstrap_draws,
                                      bootstrap_seed=int(contract["evaluation_seed"]) + index,
                                      press_function=_press_on_device(device))
        summary.update({"id": spec["id"], "task": spec["task"], "gamma": spec["gamma"],
                        "checkpoint": str(path), "checkpoint_iteration": iteration,
                        "checkpoint_provenance": provenance})
        results.append(summary)
        np.savez_compressed(args.output_dir / f"{spec['id']}_trial_outcomes.npz", **raw)
        del model
        if device.type == "cuda": torch.cuda.empty_cache()
    output = {"schema_version": 1, "design": manifest["design"], "claim_scope": manifest["claim_scope"],
              "evaluation_contract": {**contract, "trials_per_status_per_location": n,
                                      "bootstrap_draws": args.bootstrap_draws, "device": str(device)},
              "paper_targets": manifest["paper_targets"], "models": results}
    out = args.output_dir / "selected_replication_results.json"
    out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out)
    for row in results:
        d = row["contrasts"]["condition_minus_control"]
        print(f"{row['id']}: delta dprime={d['dprime']:.4f}; delta c={d['criterion']:.4f}; strict={row['paper_like_tests']['strict_behavioral_dissociation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
