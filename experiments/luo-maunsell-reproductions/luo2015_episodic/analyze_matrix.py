#!/usr/bin/env python3
"""Evaluate paired episodic Luo--Maunsell agents with counterphased contrasts."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
import torch

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from luo2015_analysis.luo2015_core import (  # noqa: E402
    _env,
    _reset_to,
    _rollout_video,
    _tens,
    load_model,
    press_times,
    summarize_sdt,
)


def balanced_trial_bank(
    *,
    magnitude: float,
    trials_per_location: int,
    seed: int,
    task: str = "luo2015_sensitivity",
    noise_multiplier: float = 5.0,
    spatial_grid_size: int = 2,
):
    """Build one deterministic trial bank shared by every policy.

    Every trial independently samples both initial orientations from Uniform[0°, 180°).
    Global NumPy state is restored so analysis cannot perturb training or another evaluation.
    """
    if trials_per_location <= 0:
        raise ValueError("trials_per_location must be positive")
    rng_state = np.random.get_state()
    try:
        np.random.seed(int(seed))
        environment = _env(
            task,
            float(magnitude),
            spatial_grid_size=int(spatial_grid_size),
            noise_multiplier=float(noise_multiplier),
        )
        videos: dict[int, list] = {1: [], 0: []}
        locations: dict[int, list[int]] = {1: [], 0: []}
        for change_true in (1, 0):
            for test_loc in (0, 3):
                for _ in range(int(trials_per_location)):
                    _reset_to(environment, change_true, test_loc)
                    videos[change_true].append(_rollout_video(environment))
                    locations[change_true].append(test_loc)
        return (
            _tens(videos[1]),
            _tens(videos[0]),
            np.asarray(locations[1], dtype=np.int64),
            np.asarray(locations[0], dtype=np.int64),
        )
    finally:
        np.random.set_state(rng_state)


def _location_difference(record: dict, metric: str) -> float:
    metrics = record["metrics"]
    loc0 = metrics.get("0", metrics.get(0))
    loc3 = metrics.get("3", metrics.get(3))
    if loc0 is None or loc3 is None:
        raise ValueError("each record must contain metrics for locations 0 and 3")
    return float(loc0[metric]) - float(loc3[metric])


def counterphased_effects(records: Iterable[dict]) -> list[dict]:
    """Compute seed-paired condition-location difference-in-differences.

    For each session and metric, the contrast is
        0.5 * ((loc0 - loc3) when condition_loc=0
             - (loc0 - loc3) when condition_loc=3).
    Expected primary signs are positive sensitivity d-prime and negative
    criterion c. The other two outputs are specificity checks, not effects that
    can be declared absent merely because they are nonsignificant.
    """
    indexed: dict[tuple[int, str, int], dict] = {}
    seeds: set[int] = set()
    for record in records:
        seed = int(record["seed"])
        session = str(record["session"])
        condition_loc = int(record["condition_loc"])
        key = (seed, session, condition_loc)
        if key in indexed:
            raise ValueError(f"duplicate result for {key}")
        indexed[key] = record
        seeds.add(seed)

    effects: list[dict] = []
    for seed in sorted(seeds):
        missing = [
            (session, condition_loc)
            for session in ("sensitivity", "criterion")
            for condition_loc in (0, 3)
            if (seed, session, condition_loc) not in indexed
        ]
        if missing:
            raise ValueError(f"seed {seed} is missing cells: {missing}")

        output: dict[str, float | int] = {"seed": seed}
        for session in ("sensitivity", "criterion"):
            loc0_condition = indexed[(seed, session, 0)]
            loc3_condition = indexed[(seed, session, 3)]
            for metric, suffix in (("dprime", "dprime_did"), ("criterion", "criterion_did")):
                contrast = 0.5 * (
                    _location_difference(loc0_condition, metric)
                    - _location_difference(loc3_condition, metric)
                )
                output[f"{session}_{suffix}"] = contrast
        effects.append(output)
    return effects


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _press_times_batched(
    model,
    videos: torch.Tensor,
    batch_size: int,
    *,
    inject_memory_noise: bool = False,
    sample_actions: bool = False,
) -> np.ndarray:
    outputs = [
        press_times(
            model,
            videos[start:start + batch_size],
            inject_memory_noise=inject_memory_noise,
            sample_actions=sample_actions,
        )
        for start in range(0, len(videos), batch_size)
    ]
    return np.concatenate(outputs)


def _checkpoint_contract(record: dict) -> tuple[Path, dict]:
    from experiments.luo2015_episodic.run_matrix import (
        ExperimentCell,
        validate_child_checkpoint_contract,
    )

    checkpoint_path = Path(record["final_checkpoint"])
    if not checkpoint_path.is_file():
        raise FileNotFoundError(checkpoint_path)
    actual_hash = _sha256(checkpoint_path)
    if actual_hash != record.get("final_checkpoint_sha256"):
        raise ValueError(f"checkpoint hash mismatch for {record['id']}")
    cell = ExperimentCell(
        role=record["role"],
        seed=int(record["seed"]),
        task=record["task"],
        condition_loc=int(record["condition_loc"]),
        output_dir=Path(record["output_dir"]),
        command=tuple(record["command"]),
        parent_checkpoint=Path(record["parent_checkpoint"]),
    )
    checkpoint = validate_child_checkpoint_contract(
        checkpoint_path, cell, record["parent_checkpoint_sha256"]
    )
    return checkpoint_path, checkpoint


def validate_analysis_manifest(manifest: dict) -> None:
    if manifest.get("run_mode") != "full":
        raise RuntimeError("canary manifests are plumbing-only and cannot produce SDT evidence")
    incomplete = [
        record.get("id", "unknown")
        for record in manifest.get("cells", [])
        if record.get("role") == "fixed_condition" and record.get("status") != "complete"
    ]
    if incomplete:
        raise RuntimeError(f"incomplete fixed-condition cells: {', '.join(incomplete)}")

    parents: dict[int, dict] = {}
    children_by_seed: dict[int, list[dict]] = {}
    for record in manifest.get("cells", []):
        seed = int(record.get("seed", -1))
        if record.get("role") == "neutral_parent":
            if seed in parents:
                raise RuntimeError(f"duplicate neutral parent for seed {seed}")
            parents[seed] = record
        elif record.get("role") == "fixed_condition":
            children_by_seed.setdefault(seed, []).append(record)

    expected_conditions = {
        ("luo2015_sensitivity", 0), ("luo2015_sensitivity", 3),
        ("luo2015_criterion", 0), ("luo2015_criterion", 3),
    }
    for seed, children in children_by_seed.items():
        parent = parents.get(seed)
        if not parent or parent.get("status") != "complete":
            raise RuntimeError(f"missing complete neutral parent for seed {seed}")
        if parent.get("parent_gate", {}).get("status") != "passed":
            raise RuntimeError(f"neutral parent gate did not pass for seed {seed}")
        parent_path = Path(parent.get("final_checkpoint", ""))
        if (
            not parent_path.is_file()
            or _sha256(parent_path) != parent.get("final_checkpoint_sha256")
        ):
            raise RuntimeError(f"parent checkpoint hash mismatch for seed {seed}")
        observed = {
            (child.get("task"), int(child.get("condition_loc", -1)))
            for child in children
        }
        if observed != expected_conditions or len(children) != 4:
            raise RuntimeError(f"incomplete or duplicate condition matrix for seed {seed}")
        parent_hash = parent.get("final_checkpoint_sha256")
        if any(child.get("parent_checkpoint_sha256") != parent_hash for child in children):
            raise RuntimeError(f"parent checkpoint lineage mismatch for seed {seed}")


def _validate_parent_checkpoint_record(record: dict) -> None:
    from experiments.luo2015_episodic.run_matrix import (
        ExperimentCell,
        validate_parent_checkpoint_contract,
    )

    cell = ExperimentCell(
        role=record["role"],
        seed=int(record["seed"]),
        task=record["task"],
        condition_loc=None,
        output_dir=Path(record["output_dir"]),
        command=tuple(record["command"]),
        parent_checkpoint=None,
    )
    validate_parent_checkpoint_contract(Path(record["final_checkpoint"]), cell)


def evaluate_manifest(
    manifest: dict,
    *,
    magnitudes: Iterable[float],
    trials_per_location: int,
    eval_seed: int,
    batch_size: int,
) -> list[dict]:
    """Evaluate every child on identical balanced stimuli at each magnitude."""
    children = [record for record in manifest["cells"] if record["role"] == "fixed_condition"]
    if not children or any(record.get("status") != "complete" for record in children):
        raise ValueError("all fixed-condition cells must be complete before evaluation")
    for parent in (
        record for record in manifest["cells"] if record["role"] == "neutral_parent"
    ):
        _validate_parent_checkpoint_record(parent)
    banks = {
        float(magnitude): balanced_trial_bank(
            magnitude=float(magnitude),
            trials_per_location=trials_per_location,
            seed=eval_seed + index,
        )
        for index, magnitude in enumerate(magnitudes)
    }

    records: list[dict] = []
    for cell in children:
        checkpoint_path, _checkpoint = _checkpoint_contract(cell)
        model, iteration = load_model(str(checkpoint_path))
        session = cell["task"].removeprefix("luo2015_")
        for magnitude, bank in banks.items():
            change_videos, no_change_videos, change_locs, no_change_locs = bank
            # Match the stochastic policy dynamics used during training.  Deterministic
            # argmax with mnemonic noise disabled is a different evaluation contract.
            change_press = _press_times_batched(
                model, change_videos, batch_size,
                inject_memory_noise=True, sample_actions=True,
            )
            no_change_press = _press_times_batched(
                model, no_change_videos, batch_size,
                inject_memory_noise=True, sample_actions=True,
            )
            summary = summarize_sdt(change_press, no_change_press, change_locs, no_change_locs)
            metrics = {}
            for loc in (0, 3):
                local = summary.get(f"loc{loc}")
                if local is None:
                    raise ValueError(f"{cell['id']} has no valid SDT trials at location {loc}")
                metrics[str(loc)] = {
                    "n_change": local["n_change"],
                    "n_no_change": local["n_no_change"],
                    "hit_rate": local["HR"],
                    "false_alarm_rate": local["FA"],
                    "dprime": local["dprime"],
                    "criterion": local["c"],
                }
            records.append({
                "seed": int(cell["seed"]),
                "session": session,
                "condition_loc": int(cell["condition_loc"]),
                "magnitude": magnitude,
                "checkpoint": str(checkpoint_path),
                "checkpoint_sha256": cell["final_checkpoint_sha256"],
                "checkpoint_iteration": iteration,
                "parent_checkpoint_sha256": cell["parent_checkpoint_sha256"],
                "excluded_change": summary["excluded_change"],
                "excluded_no_change": summary["excluded_no_change"],
                "metrics": metrics,
            })
        del model
    return records


def summarize_effects(seed_effects: list[dict], *, bootstrap_seed: int = 2026) -> dict:
    if not seed_effects:
        raise ValueError("no seed effects to summarize")
    keys = [key for key in seed_effects[0] if key != "seed"]
    rng = np.random.default_rng(bootstrap_seed)
    output = {}
    for key in keys:
        values = np.asarray([row[key] for row in seed_effects], dtype=float)
        if len(values) >= 2:
            draws = rng.choice(values, size=(10_000, len(values)), replace=True).mean(axis=1)
            ci95 = [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]
        else:
            ci95 = None
        output[key] = {
            "n_paired_seeds": len(values),
            "mean": float(values.mean()),
            "sample_sd": float(values.std(ddof=1)) if len(values) >= 2 else None,
            "bootstrap_ci95": ci95,
        }
    return output


def analyze_run(
    run_root: Path,
    *,
    magnitudes: Iterable[float],
    trials_per_location: int,
    eval_seed: int,
    batch_size: int,
) -> dict:
    manifest_path = run_root / "experiment_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_analysis_manifest(manifest)
    records = evaluate_manifest(
        manifest,
        magnitudes=magnitudes,
        trials_per_location=trials_per_location,
        eval_seed=eval_seed,
        batch_size=batch_size,
    )
    per_magnitude = {}
    for magnitude in sorted({record["magnitude"] for record in records}):
        selected = [record for record in records if record["magnitude"] == magnitude]
        seed_effects = counterphased_effects(selected)
        per_magnitude[str(magnitude)] = {
            "seed_effects": seed_effects,
            "summary": summarize_effects(seed_effects),
        }
    return {
        "schema_version": 1,
        "design": manifest["design"],
        "claim_scope": manifest["claim_scope"],
        "primary_estimands": {
            "sensitivity": "sensitivity_dprime_did > 0",
            "criterion": "criterion_criterion_did < 0",
        },
        "specificity_estimands": {
            "sensitivity": "sensitivity_criterion_did near 0; use an equivalence bound",
            "criterion": "criterion_dprime_did near 0; use an equivalence bound",
        },
        "trials_per_change_status_per_location": trials_per_location,
        "evaluation_seed": eval_seed,
        "records": records,
        "effects_by_magnitude": per_magnitude,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate a completed paired episodic Luo--Maunsell experiment."
    )
    parser.add_argument("run_root", type=Path)
    parser.add_argument("--magnitudes", type=float, nargs="+", default=[18.0])
    parser.add_argument("--trials-per-location", type=int, default=200)
    parser.add_argument("--eval-seed", type=int, default=20260717)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    run_root = args.run_root.resolve()
    try:
        result = analyze_run(
            run_root,
            magnitudes=args.magnitudes,
            trials_per_location=args.trials_per_location,
            eval_seed=args.eval_seed,
            batch_size=args.batch_size,
        )
    except (RuntimeError, ValueError) as exc:
        print(f"[blocked] {exc}", file=sys.stderr)
        return 2
    output_path = args.output or (run_root / "episodic_evaluation.json")
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[complete] {output_path}")
    for magnitude, block in result["effects_by_magnitude"].items():
        summary = block["summary"]
        print(
            f"|Δ|={magnitude}: sensitivity Δd'={summary['sensitivity_dprime_did']['mean']:.4f}; "
            f"criterion Δc={summary['criterion_criterion_did']['mean']:.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
