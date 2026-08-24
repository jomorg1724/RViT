#!/usr/bin/env python3
"""Full matched behavioral battery for the latest Luo--Maunsell checkpoints.

Primary: matched signed-Uniform(-65,+65) episodes under trained mnemonic noise.
Manipulations: the same primary bank at zero mnemonic noise, plus exact-|Delta|
psychometric/chronometric trials balanced over sign and location. Policy actions
remain sampled in every condition.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

import numpy as np
import torch

from experiments.luo2015_episodic.analyze_matrix import balanced_trial_bank
from experiments.luo2015_episodic.evaluate_selected_replication import (
    _location_metrics,
    summarize_policy,
    validate_checkpoint,
)
from luo2015_analysis import luo2015_core as core


def evaluation_conditions() -> dict[str, dict[str, bool]]:
    return {
        "trained_noise": {"inject_memory_noise": True, "sample_actions": True},
        "zero_mnemonic_noise": {"inject_memory_noise": False, "sample_actions": True},
    }


def _configure_trial(environment, *, change_true: int, test_loc: int,
                     signed_delta: float) -> None:
    environment.t = 0
    environment._frame_cache = None
    environment.test_loc = int(test_loc)
    environment.change_true = int(change_true)
    environment.orientation_change = float(signed_delta)
    environment.test_ori = (
        environment.samp[test_loc] + signed_delta
        if change_true else environment.samp[test_loc]
    )
    environment.second_test_ori = environment.samp[test_loc] + signed_delta


def exact_magnitude_trial_bank(*, magnitude: float, trials_per_sign_per_location: int,
                               seed: int, sensory_noise_sd: float,
                               second_test_magnitude: float) -> dict[str, np.ndarray | torch.Tensor]:
    """Changed trials with exact |Delta|, balanced sign/location, iid axial samples."""
    del second_test_magnitude  # no second test is shown on changed trials
    if magnitude <= 0 or magnitude > 90:
        raise ValueError("magnitude must be in (0, 90]")
    if trials_per_sign_per_location <= 0:
        raise ValueError("trials_per_sign_per_location must be positive")
    state = np.random.get_state()
    try:
        np.random.seed(int(seed))
        environment = core._env("luo2015_sensitivity", 65.0, noise_multiplier=float(sensory_noise_sd))
        videos, locations, signs, deltas, samples = [], [], [], [], []
        for loc in (0, 3):
            for sign in (-1, 1):
                for _ in range(int(trials_per_sign_per_location)):
                    environment.reset()
                    delta = float(sign * magnitude)
                    _configure_trial(environment, change_true=1, test_loc=loc, signed_delta=delta)
                    videos.append(core._rollout_video(environment))
                    locations.append(loc); signs.append(sign); deltas.append(delta)
                    samples.append([environment.samp[0], environment.samp[3]])
        return {
            "videos": core._tens(videos),
            "locations": np.asarray(locations, dtype=np.int64),
            "signs": np.asarray(signs, dtype=np.int8),
            "signed_deltas": np.asarray(deltas, dtype=np.float64),
            "sample_orientations": np.asarray(samples, dtype=np.float64),
        }
    finally:
        np.random.set_state(state)


def exact_no_change_bank(*, trials_per_sign_per_location: int, seed: int,
                         sensory_noise_sd: float,
                         second_test_magnitude: float) -> dict[str, np.ndarray | torch.Tensor]:
    """No-change first tests with an exact, easy, sign-balanced second test."""
    if not (0 < second_test_magnitude <= 90):
        raise ValueError("second_test_magnitude must be in (0, 90]")
    if trials_per_sign_per_location <= 0:
        raise ValueError("trials_per_sign_per_location must be positive")
    state = np.random.get_state()
    try:
        np.random.seed(int(seed))
        environment = core._env("luo2015_sensitivity", 65.0, noise_multiplier=float(sensory_noise_sd))
        videos, locations, signs, deltas, samples = [], [], [], [], []
        for loc in (0, 3):
            for sign in (-1, 1):
                for _ in range(int(trials_per_sign_per_location)):
                    environment.reset()
                    delta = float(sign * second_test_magnitude)
                    _configure_trial(environment, change_true=0, test_loc=loc, signed_delta=delta)
                    videos.append(core._rollout_video(environment))
                    locations.append(loc); signs.append(sign); deltas.append(delta)
                    samples.append([environment.samp[0], environment.samp[3]])
        return {
            "videos": core._tens(videos),
            "locations": np.asarray(locations, dtype=np.int64),
            "signs": np.asarray(signs, dtype=np.int8),
            "second_test_signed_deltas": np.asarray(deltas, dtype=np.float64),
            "sample_orientations": np.asarray(samples, dtype=np.float64),
        }
    finally:
        np.random.set_state(state)


def counterphased_did(summaries: list[dict], session: str, metric: str) -> float:
    indexed = {int(row["condition_loc"]): row for row in summaries if row["session"] == session}
    if set(indexed) != {0, 3}:
        raise ValueError(f"{session} requires condition-loc 0 and 3 summaries")
    loc0 = indexed[0]["locations"]
    loc3 = indexed[3]["locations"]
    return float(0.5 * (
        (float(loc0["0"][metric]) - float(loc0["3"][metric]))
        - (float(loc3["0"][metric]) - float(loc3["3"][metric]))
    ))


def _press_on_device(device: torch.device) -> Callable:
    def run(model, videos, batch_size, **kwargs):
        outputs = []
        for start in range(0, len(videos), batch_size):
            outputs.append(core.press_times(model, videos[start:start + batch_size].to(device), **kwargs))
        return np.concatenate(outputs)
    return run


def _seed_policy(seed: int, device: torch.device) -> None:
    torch.manual_seed(int(seed))
    if device.type == "cuda":
        torch.cuda.manual_seed_all(int(seed))


def _evaluate_bank(model, bank, *, condition_loc: int, session: str, batch_size: int,
                   bootstrap_draws: int, bootstrap_seed: int, press: Callable,
                   kwargs: dict[str, bool]) -> tuple[dict, dict[str, np.ndarray]]:
    change_videos, no_change_videos, change_locs, no_change_locs = bank
    change_press = press(model, change_videos, batch_size, **kwargs)
    no_change_press = press(model, no_change_videos, batch_size, **kwargs)
    summary = summarize_policy(
        change_press, no_change_press, change_locs, no_change_locs,
        condition_loc=condition_loc, session=session,
        bootstrap_draws=bootstrap_draws, bootstrap_seed=bootstrap_seed,
    )
    summary["evaluation_contract"] = dict(kwargs)
    return summary, {
        "change_press": change_press, "no_change_press": no_change_press,
        "change_locations": change_locs, "no_change_locations": no_change_locs,
    }


def _psychometric_metrics(change_press: np.ndarray, no_change_press: np.ndarray,
                          change_locs: np.ndarray, no_change_locs: np.ndarray,
                          signs: np.ndarray) -> dict:
    output = {}
    for loc in (0, 3):
        metrics, _, _ = _location_metrics(
            change_press, no_change_press, change_locs, no_change_locs, loc)
        sign_metrics = {}
        for sign in (-1, 1):
            selected = (change_locs == loc) & (signs == sign)
            presses = change_press[selected]
            outcomes = np.asarray([core.classify_trial(1, int(x)) for x in presses])
            valid = np.isin(outcomes, ("hit", "miss"))
            sign_metrics[str(sign)] = {
                "n_total": int(len(presses)), "n_valid": int(valid.sum()),
                "hit_rate": float((outcomes[valid] == "hit").mean()) if valid.any() else None,
                "fixation_breaks": int((outcomes == "fixation_break").sum()),
                "mean_hit_frame": float(presses[outcomes == "hit"].mean()) if np.any(outcomes == "hit") else None,
            }
        metrics["by_change_sign"] = sign_metrics
        output[str(loc)] = metrics
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--checkpoint-root", type=Path, default=None)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--primary-trials-per-status-per-location", type=int, default=None)
    parser.add_argument("--psychometric-trials-per-sign-per-location", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--bootstrap-draws", type=int, default=5000)
    args = parser.parse_args(argv)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    contract = manifest["evaluation_contract"]
    primary_n = args.primary_trials_per_status_per_location or int(contract["primary_trials_per_status_per_location"])
    psych_n = args.psychometric_trials_per_sign_per_location or int(contract["psychometric_trials_per_sign_per_location"])
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("PyTorch CUDA unavailable")
    core.DEVICE = device
    args.output_dir.mkdir(parents=True, exist_ok=True)
    press = _press_on_device(device)

    primary_bank = balanced_trial_bank(
        magnitude=float(contract["theta"]), trials_per_location=primary_n,
        seed=int(contract["evaluation_seed"]), task="luo2015_sensitivity",
        noise_multiplier=float(contract["sensory_orientation_noise_sd"]), spatial_grid_size=2,
    )
    no_change = exact_no_change_bank(
        trials_per_sign_per_location=psych_n,
        seed=int(contract["evaluation_seed"]) + 10_000,
        sensory_noise_sd=float(contract["sensory_orientation_noise_sd"]),
        second_test_magnitude=float(contract["psychometric_second_test_magnitude"]),
    )
    no_change_videos = no_change["videos"]
    no_change_locs = no_change["locations"]

    primary_results: dict[str, list[dict]] = {name: [] for name in evaluation_conditions()}
    psychometric_records = []
    for model_index, spec in enumerate(manifest["models"]):
        checkpoint = args.checkpoint_root / f"{spec['id']}.pt" if args.checkpoint_root else Path(spec["checkpoint"])
        provenance = validate_checkpoint(checkpoint, spec, contract)
        model, iteration = core.load_model(str(checkpoint))
        for condition_index, (condition, kwargs) in enumerate(evaluation_conditions().items()):
            policy_seed = int(contract["evaluation_seed"]) + model_index * 100 + condition_index
            _seed_policy(policy_seed, device)
            summary, raw = _evaluate_bank(
                model, primary_bank, condition_loc=int(spec["condition_loc"]), session=spec["session"],
                batch_size=args.batch_size, bootstrap_draws=args.bootstrap_draws,
                bootstrap_seed=policy_seed, press=press, kwargs=kwargs,
            )
            summary.update({"id": spec["id"], "task": spec["task"], "gamma": spec["gamma"],
                            "checkpoint": str(checkpoint), "checkpoint_iteration": iteration,
                            "checkpoint_provenance": provenance, "policy_seed": policy_seed,
                            "measurement_condition": condition})
            primary_results[condition].append(summary)
            np.savez_compressed(args.output_dir / f"{spec['id']}_{condition}_primary_outcomes.npz", **raw)

        trained_kwargs = evaluation_conditions()["trained_noise"]
        _seed_policy(int(contract["evaluation_seed"]) + model_index * 1000 + 500, device)
        no_change_press = press(model, no_change_videos, args.batch_size, **trained_kwargs)
        model_raw: dict[str, np.ndarray] = {
            "no_change_press": no_change_press,
            "no_change_locations": no_change_locs,
            "no_change_signs": no_change["signs"],
        }
        for magnitude_index, magnitude in enumerate(contract["psychometric_magnitudes"]):
            bank = exact_magnitude_trial_bank(
                magnitude=float(magnitude), trials_per_sign_per_location=psych_n,
                seed=int(contract["evaluation_seed"]) + 20_000 + magnitude_index,
                sensory_noise_sd=float(contract["sensory_orientation_noise_sd"]),
                second_test_magnitude=float(contract["psychometric_second_test_magnitude"]),
            )
            _seed_policy(int(contract["evaluation_seed"]) + model_index * 1000 + magnitude_index, device)
            change_press = press(model, bank["videos"], args.batch_size, **trained_kwargs)
            psychometric_records.append({
                "id": spec["id"], "session": spec["session"],
                "condition_loc": int(spec["condition_loc"]), "magnitude": float(magnitude),
                "signed_change_design": "exact_abs_delta_balanced_signs",
                "locations": _psychometric_metrics(
                    change_press, no_change_press, bank["locations"], no_change_locs, bank["signs"]),
            })
            key = str(magnitude).replace(".", "p")
            model_raw[f"change_press_mag_{key}"] = change_press
            model_raw[f"change_locations_mag_{key}"] = bank["locations"]
            model_raw[f"change_signs_mag_{key}"] = bank["signs"]
            model_raw[f"change_signed_deltas_mag_{key}"] = bank["signed_deltas"]
        np.savez_compressed(args.output_dir / f"{spec['id']}_psychometric_outcomes.npz", **model_raw)
        del model
        if device.type == "cuda": torch.cuda.empty_cache()

    did = {}
    for condition, rows in primary_results.items():
        did[condition] = {
            "sensitivity_dprime_did": counterphased_did(rows, "sensitivity", "dprime"),
            "sensitivity_criterion_cross_did": counterphased_did(rows, "sensitivity", "criterion"),
            "criterion_criterion_did": counterphased_did(rows, "criterion", "criterion"),
            "criterion_dprime_cross_did": counterphased_did(rows, "criterion", "dprime"),
        }
    output = {
        "schema_version": 1, "design": manifest["design"], "claim_scope": manifest["claim_scope"],
        "evaluation_contract": {**contract, "device": str(device),
                                "primary_trials_per_status_per_location": primary_n,
                                "psychometric_trials_per_sign_per_location": psych_n,
                                "bootstrap_draws": args.bootstrap_draws,
                                "policy_action_semantics": "sampled_categorical"},
        "paper_targets": manifest["paper_targets"],
        "primary_results": primary_results, "counterphased_effects": did,
        "psychometric_records": psychometric_records,
    }
    out = args.output_dir / "latest_full_battery_results.json"
    out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out)
    for condition, effects in did.items(): print(condition, json.dumps(effects, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
