"""Verify one complete four-cell stream-factorial engineering canary block.

This verifier is intentionally narrower than production terminal validation.
It accepts only the registered seed-0, 50-iteration cross-attention canary and
emits engineering evidence about checkpoint/provenance integrity.  Training
metrics and successful canaries are never scientific attention evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import numbers
import re
import sys
from pathlib import Path
from typing import Any, Sequence

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis.vda_terminal_run_validation import (
    _assert_finite_tree,
    _assert_semantically_equal,
    _install_numpy_pickle_compat,
    _validate_projector_buffers,
    sha256_file,
)
from experiments.vda_stream_factorial.preflight_contract_v1 import (
    environment_rng_trace,
)


CANARY_ITERATIONS = 50
CANARY_FINAL_ITERATION = 49
PRODUCTION_SCHEDULE_FINAL_ITERATION = 19_999
EXPECTED_SEED = 0
EXPECTED_CELLS = frozenset(((4, 4), (4, 100), (100, 4), (100, 100)))
CELL_IDS = {
    cell: f"visual{cell[0]}_memory{cell[1]}" for cell in EXPECTED_CELLS
}
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
FACTORY_KEYS = frozenset((
    "kind",
    "effective_visual_streams",
    "effective_memory_streams",
    "carrier_grid",
))
CONFIG_RELATIVE = "experiments/vda_stream_factorial/config_crossattn1_v1.json"
DESIGN_RELATIVE = "experiments/vda_stream_factorial/design_manifest.json"
PREFLIGHT_RELATIVE = "experiments/vda_stream_factorial/preflight_contract_v1.py"
LAUNCHER_RELATIVE = "experiments/vda_stream_factorial/launch_crossattn1_canary_v1.sh"
REQUIRED_PRODUCER_IDENTITIES = frozenset((
    "train_rl.py",
    "ppo.py",
    "model.py",
    "paper_encoder.py",
    "paper_heads.py",
    "conv_frontend.py",
    "envs/base.py",
    "envs/luo2015.py",
    "envs/tasks.py",
    "envs/__init__.py",
    "config/loader.py",
    "experiments/vda_stream_factorial/stream_model.py",
    "experiments/vda_stream_factorial/design_matrix.py",
    DESIGN_RELATIVE,
    PREFLIGHT_RELATIVE,
    "resolved_config",
    "experiment_launcher",
))
REQUIRED_STATE_KEYS = (
    "model_state_dict",
    "optimizer_state_dict",
    "target_model_state_dict",
    "jepa_teacher_state_dict",
    "environment_state",
    "rolling_correct",
    "rolling_return",
)


def _require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def _exact(mapping: dict[str, Any], key: str, expected: Any, label: str) -> None:
    actual = mapping.get(key)
    if isinstance(expected, float):
        matched = isinstance(actual, numbers.Real) and not isinstance(actual, bool)
        matched = matched and math.isclose(
            float(actual), expected, rel_tol=0.0, abs_tol=1e-12
        )
    else:
        matched = actual == expected
    if not matched:
        raise ValueError(f"{label} {key}={actual!r}, expected {expected!r}")


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {label} JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object: {path}")
    return payload


def _validate_metrics(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != CANARY_ITERATIONS:
        raise ValueError(
            f"metrics contain {len(rows)} rows; expected {CANARY_ITERATIONS}"
        )
    if not rows or "iter" not in rows[0]:
        raise ValueError("metrics are missing the iter column")
    iterations = np.asarray([int(row["iter"]) for row in rows], dtype=np.int64)
    if not np.array_equal(iterations, np.arange(CANARY_ITERATIONS)):
        raise ValueError("metrics iterations are not exactly contiguous 0..49")
    for field in rows[0]:
        if field == "iter":
            continue
        values = np.asarray([float(row[field]) for row in rows], dtype=np.float64)
        if not np.isfinite(values).all():
            raise ValueError(f"metrics column {field!r} contains non-finite values")
    return {
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "rows": len(rows),
        "first_iteration": int(iterations[0]),
        "last_iteration": int(iterations[-1]),
        "columns": list(rows[0]),
    }


def _factory_for_cell(visual: int, memory: int) -> dict[str, Any]:
    return {
        "kind": "stream_factorial_v1",
        "effective_visual_streams": int(visual),
        "effective_memory_streams": int(memory),
        "carrier_grid": [10, 10],
    }


def _validate_factory(factory: Any, visual: int, memory: int, label: str) -> None:
    expected = _factory_for_cell(visual, memory)
    if not isinstance(factory, dict) or set(factory) != FACTORY_KEYS:
        raise ValueError(f"{label} lacks the exact model_factory inventory")
    if factory != expected:
        raise ValueError(f"{label} model_factory={factory!r}, expected {expected!r}")


def _validate_payload(
    payload: Any,
    *,
    visual: int,
    memory: int,
    expected_producers: dict[str, str],
    label: str,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError(f"{label} checkpoint payload must be a mapping")
    _exact(payload, "checkpoint_schema_version", 3, label)
    _exact(payload, "iter", CANARY_FINAL_ITERATION, label)
    _exact(payload, "task", "vda4", label)
    _validate_factory(payload.get("model_factory"), visual, memory, label)

    model = payload.get("model_kwargs")
    training = payload.get("training_args")
    initialization = payload.get("initialization_contract")
    if not isinstance(model, dict) or not isinstance(training, dict):
        raise ValueError(f"{label} lacks model_kwargs/training_args")
    if not isinstance(initialization, dict):
        raise ValueError(f"{label} lacks initialization_contract")
    for key, expected in {
        "feedback": "crossattn1",
        "cell": "xlstm",
        "two_lstm": False,
        "d_mem": 128,
        "memory_decay": 1.0,
        "memory_noise_std": 0.0,
        "conv_frontend": True,
        "grid_rows": 10,
        "grid_cols": 10,
        "image_size": 50,
        "seq_len": 7,
    }.items():
        _exact(model, key, expected, f"{label} model_kwargs")
    for key, expected in {
        "task": "vda4",
        "feedback": "crossattn1",
        "cell": "xlstm",
        "two_lstm": False,
        "d_mem": 128,
        "memory_decay": 1.0,
        "memory_noise_std": 0.0,
        "patch_grid_rows": 10,
        "patch_grid_cols": 10,
        "curriculum": True,
        "seed": EXPECTED_SEED,
        "start_iteration": 0,
        "iters": CANARY_ITERATIONS,
        "schedule_final_iteration": PRODUCTION_SCHEDULE_FINAL_ITERATION,
        "episodes_per_iter": 8,
        "init_mode": "fresh",
    }.items():
        _exact(training, key, expected, f"{label} training_args")
    _exact(initialization, "mode", "fresh", f"{label} initialization_contract")
    _exact(payload, "replay_buffer_persisted", False, label)
    _exact(payload, "resume_fidelity", "replay_excluded_trainer_state", label)

    for key in REQUIRED_STATE_KEYS:
        if key not in payload or payload[key] is None:
            raise ValueError(f"{label} lacks required state {key!r}")
    for state_name in ("model_state_dict", "target_model_state_dict"):
        _validate_projector_buffers(
            payload[state_name],
            visual_streams=visual,
            memory_streams=memory,
            label=f"{label}.{state_name}",
        )
    finite_numeric_leaves = sum(
        _assert_finite_tree(payload[key], f"{label}.{key}")
        for key in REQUIRED_STATE_KEYS
    )
    if finite_numeric_leaves <= 0:
        raise ValueError(f"{label} contains no finite numeric state")

    producer = payload.get("producer_sha256")
    if not isinstance(producer, dict) or not producer:
        raise ValueError(f"{label} lacks producer_sha256")
    if not REQUIRED_PRODUCER_IDENTITIES.issubset(producer):
        missing = sorted(REQUIRED_PRODUCER_IDENTITIES - set(producer))
        raise ValueError(f"{label} producer map lacks required identities: {missing}")
    for identity, digest in producer.items():
        if not isinstance(digest, str) or not HEX_SHA256.fullmatch(digest.lower()):
            raise ValueError(f"{label} producer hash is invalid for {identity!r}")
    if producer != expected_producers:
        raise ValueError(f"{label} producer map differs from launch_contract")

    resume = payload.get("resume_contract")
    if not isinstance(resume, dict):
        raise ValueError(f"{label} lacks resume_contract")
    _exact(resume, "task", "vda4", f"{label} resume_contract")
    _exact(resume, "episodes_per_iter", 8, f"{label} resume_contract")
    _exact(
        resume,
        "schedule_final_iteration",
        PRODUCTION_SCHEDULE_FINAL_ITERATION,
        f"{label} resume_contract",
    )
    _validate_factory(resume.get("model_factory"), visual, memory, f"{label} resume_contract")
    if resume.get("producer_sha256") != producer:
        raise ValueError(f"{label} resume_contract producer map differs")
    return {
        "finite_numeric_leaves": finite_numeric_leaves,
        "producer_sha256": producer,
    }


def _verify_producer_hashes(
    producer: dict[str, str], *, project_root: Path
) -> list[dict[str, Any]]:
    config = project_root / CONFIG_RELATIVE
    launcher = project_root / LAUNCHER_RELATIVE
    checks: list[dict[str, Any]] = []
    for identity, expected in sorted(producer.items()):
        if identity == "resolved_config":
            path = config
        elif identity == "experiment_launcher":
            path = launcher
        else:
            path = project_root / identity
        if not path.is_file():
            raise FileNotFoundError(f"producer source is missing for {identity!r}: {path}")
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError(
                f"producer SHA-256 mismatch for {identity!r}: {actual} != {expected}"
            )
        checks.append({
            "identity": identity,
            "path": str(path.resolve()),
            "sha256": actual,
            "bytes": path.stat().st_size,
        })
    return checks


def _validate_launch_contract(
    path: Path, *, project_root: Path
) -> tuple[tuple[int, int], dict[str, Any]]:
    contract = _load_json(path, "launch contract")
    request = contract.get("request")
    hashes = contract.get("sha256")
    if not isinstance(request, dict) or not isinstance(hashes, dict):
        raise ValueError("launch contract lacks request/sha256 mappings")
    visual = request.get("visual_streams")
    memory = request.get("memory_streams")
    cell = (visual, memory)
    if cell not in EXPECTED_CELLS:
        raise ValueError(f"launch contract has unregistered cell {cell!r}")
    for key, expected in {
        "seed": EXPECTED_SEED,
        "run_kind": "canary",
        "iterations": CANARY_ITERATIONS,
        "terminal_iteration": CANARY_FINAL_ITERATION,
    }.items():
        _exact(request, key, expected, "launch contract request")
    _exact(contract, "status", "preflight_passed", "launch contract")
    _exact(
        contract,
        "evidence_class",
        "engineering_only_not_scientific_evidence",
        "launch contract",
    )
    _validate_factory(contract.get("model_factory"), visual, memory, "launch contract")

    local_paths = {
        "config": project_root / CONFIG_RELATIVE,
        "design": project_root / DESIGN_RELATIVE,
        "preflight": project_root / PREFLIGHT_RELATIVE,
        "launcher": project_root / LAUNCHER_RELATIVE,
    }
    for key, local_path in local_paths.items():
        if not local_path.is_file():
            raise FileNotFoundError(local_path)
        actual = sha256_file(local_path)
        if hashes.get(key) != actual:
            raise ValueError(
                f"launch contract {key} SHA-256 mismatch: {hashes.get(key)} != {actual}"
            )
    for key in ("trainable_initialization", "environment_rng_trace"):
        value = hashes.get(key)
        if not isinstance(value, str) or not HEX_SHA256.fullmatch(value.lower()):
            raise ValueError(f"launch contract has invalid {key} SHA-256")

    paired = contract.get("paired_trainable_initialization_sha256_by_cell")
    expected_ids = set(CELL_IDS.values())
    if not isinstance(paired, dict) or set(paired) != expected_ids:
        raise ValueError("launch contract lacks exact four-cell paired initialization map")
    if set(paired.values()) != {hashes["trainable_initialization"]}:
        raise ValueError("launch contract paired initialization hashes are not identical")

    producer = contract.get("producer_sha256")
    if not isinstance(producer, dict):
        raise ValueError("launch contract lacks producer_sha256 mapping")
    if producer.get("resolved_config") != hashes["config"]:
        raise ValueError("launch contract config and producer hashes differ")
    if producer.get("experiment_launcher") != hashes["launcher"]:
        raise ValueError("launch contract launcher and producer hashes differ")
    if producer.get(DESIGN_RELATIVE) != hashes["design"]:
        raise ValueError("launch contract design and producer hashes differ")
    if producer.get(PREFLIGHT_RELATIVE) != hashes["preflight"]:
        raise ValueError("launch contract preflight and producer hashes differ")
    return cell, contract


def _validate_log(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    for forbidden in ("Traceback", "RuntimeError", "Exception:"):
        if forbidden in text:
            raise ValueError(f"training log contains failure marker {forbidden!r}")
    final_pattern = re.compile(
        r"\[checkpoint\] saved replay-excluded trainer state to .*rvit_paper_vda4_final\.pt"
    )
    if not final_pattern.search(text):
        raise ValueError("training log lacks the final vda4 checkpoint-save marker")
    if "iters logged=50" not in text:
        raise ValueError("training log lacks the exact 'iters logged=50' marker")
    return {
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "traceback_absent": True,
        "terminal_markers_present": True,
    }


def verify_canary_block(
    run_dirs: Sequence[str | Path],
    logs: Sequence[str | Path],
    *,
    project_root: str | Path,
) -> dict[str, Any]:
    """Verify four paired seed-0 canaries and return a JSON-ready manifest."""
    if len(run_dirs) != 4 or len(logs) != 4:
        raise ValueError("exactly four run directories and four paired logs are required")
    project_root = Path(project_root).resolve()
    resolved_runs = [Path(path).resolve() for path in run_dirs]
    resolved_logs = [Path(path).resolve() for path in logs]
    if len(set(resolved_runs)) != 4:
        raise ValueError("the four run directories must be distinct")
    for path in (project_root, *resolved_runs, *resolved_logs):
        if not path.exists():
            raise FileNotFoundError(path)

    design_path = project_root / DESIGN_RELATIVE
    design = _load_json(design_path, "design manifest")
    trace_spec = design.get("environment_rng_trace")
    if not isinstance(trace_spec, dict):
        raise ValueError("design manifest lacks environment_rng_trace")
    trial_count = trace_spec.get("trial_count")
    frozen_trace = trace_spec.get("expected_sha256_by_seed", {}).get(str(EXPECTED_SEED))
    if not isinstance(frozen_trace, str) or not HEX_SHA256.fullmatch(frozen_trace):
        raise ValueError("design manifest lacks a valid frozen seed-0 RNG trace")
    recomputed_trace = environment_rng_trace(project_root, EXPECTED_SEED, trial_count)
    if recomputed_trace != frozen_trace:
        raise ValueError(
            f"local seed-0 environment RNG trace {recomputed_trace} != frozen {frozen_trace}"
        )

    _install_numpy_pickle_compat()
    import torch

    cells: dict[tuple[int, int], dict[str, Any]] = {}
    launch_contracts: list[dict[str, Any]] = []
    common_producer: dict[str, str] | None = None
    common_producer_checks: list[dict[str, Any]] | None = None
    for run_dir, log_path in zip(resolved_runs, resolved_logs, strict=True):
        final_path = run_dir / "rvit_paper_vda4_final.pt"
        latest_path = run_dir / "rvit_plus_rl_latest.pt"
        metrics_path = run_dir / "metrics.csv"
        contract_path = run_dir / "launch_contract.json"
        for path in (final_path, latest_path, metrics_path, contract_path):
            if not path.is_file():
                raise FileNotFoundError(path)

        cell, launch_contract = _validate_launch_contract(
            contract_path, project_root=project_root
        )
        if cell in cells:
            raise ValueError(f"duplicate canary cell {CELL_IDS[cell]}")
        visual, memory = cell
        producer = launch_contract["producer_sha256"]
        if common_producer is None:
            common_producer = producer
            common_producer_checks = _verify_producer_hashes(
                producer, project_root=project_root
            )
        elif producer != common_producer:
            raise ValueError("producer SHA-256 maps differ across canary cells")

        final_payload = torch.load(final_path, map_location="cpu", weights_only=False)
        latest_payload = torch.load(latest_path, map_location="cpu", weights_only=False)
        final_validation = _validate_payload(
            final_payload,
            visual=visual,
            memory=memory,
            expected_producers=producer,
            label=f"{CELL_IDS[cell]} final checkpoint",
        )
        latest_validation = _validate_payload(
            latest_payload,
            visual=visual,
            memory=memory,
            expected_producers=producer,
            label=f"{CELL_IDS[cell]} latest checkpoint",
        )
        compared = _assert_semantically_equal(
            final_payload, latest_payload, f"{CELL_IDS[cell]} final/latest"
        )
        if final_validation["producer_sha256"] != latest_validation["producer_sha256"]:
            raise ValueError(f"{CELL_IDS[cell]} final/latest producer maps differ")

        metrics = _validate_metrics(metrics_path)
        log = _validate_log(log_path)
        cells[cell] = {
            "cell_id": CELL_IDS[cell],
            "effective_visual_streams": visual,
            "effective_memory_streams": memory,
            "seed": EXPECTED_SEED,
            "run_dir": str(run_dir),
            "metrics": metrics,
            "log": log,
            "launch_contract": {
                "path": str(contract_path),
                "sha256": sha256_file(contract_path),
                "bytes": contract_path.stat().st_size,
            },
            "final_checkpoint": {
                "path": str(final_path),
                "sha256": sha256_file(final_path),
                "bytes": final_path.stat().st_size,
            },
            "latest_checkpoint": {
                "path": str(latest_path),
                "sha256": sha256_file(latest_path),
                "bytes": latest_path.stat().st_size,
            },
            "final_latest_semantically_equal": True,
            "compared_numeric_leaves": compared,
            "finite_numeric_leaves": final_validation["finite_numeric_leaves"],
            "model_factory": _factory_for_cell(visual, memory),
        }
        launch_contracts.append(launch_contract)

    if set(cells) != EXPECTED_CELLS:
        missing = sorted(EXPECTED_CELLS - set(cells))
        raise ValueError(f"canary block lacks exact four-cell coverage; missing={missing}")
    init_hashes = {
        contract["sha256"]["trainable_initialization"] for contract in launch_contracts
    }
    trace_hashes = {
        contract["sha256"]["environment_rng_trace"] for contract in launch_contracts
    }
    if len(init_hashes) != 1:
        raise ValueError("common trainable-initialization SHA-256 differs across cells")
    if trace_hashes != {frozen_trace}:
        raise ValueError(
            "launch-contract environment RNG trace is not common and equal to the frozen seed-0 trace"
        )

    verifier_path = Path(__file__).resolve()
    return {
        "schema_version": 1,
        "status": "complete_verified_engineering_canary_block",
        "evidence_class": "engineering_only_not_scientific_evidence",
        "scientific_evidence": False,
        "scientific_behavior_evaluated": False,
        "design_id": design.get("design_id"),
        "seed": EXPECTED_SEED,
        "iterations": CANARY_ITERATIONS,
        "terminal_iteration": CANARY_FINAL_ITERATION,
        "schedule_final_iteration": PRODUCTION_SCHEDULE_FINAL_ITERATION,
        "cells": {
            CELL_IDS[cell]: cells[cell] for cell in sorted(cells)
        },
        "common_trainable_initialization_sha256": next(iter(init_hashes)),
        "common_environment_rng_trace_sha256": frozen_trace,
        "producer_checks": common_producer_checks,
        "verifier": {
            "path": str(verifier_path),
            "sha256": sha256_file(verifier_path),
        },
        "claim_boundary": (
            "Engineering canary integrity only. Fifty-iteration training metrics, "
            "checkpoint state, and projector checks are not behavioral, attention, "
            "mechanism, scaling, or scientific evidence."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument(
        "--run-dir",
        type=Path,
        action="append",
        required=True,
        help="repeat exactly four times; paired positionally with --log",
    )
    parser.add_argument(
        "--log",
        type=Path,
        action="append",
        required=True,
        help="repeat exactly four times in the same cell order as --run-dir",
    )
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = verify_canary_block(
        args.run_dir,
        args.log,
        project_root=args.project_root,
    )
    text = json.dumps(result, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(
            "VERIFIED|kind=engineering_canary|cells=4|seed=0|iters=50|"
            "scientific_evidence=false",
            flush=True,
        )
    else:
        print(text, end="", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
