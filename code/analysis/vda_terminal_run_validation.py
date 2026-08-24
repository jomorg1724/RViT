"""Fail-closed validation for fresh terminal VDA endpoint training runs.

This validator is deliberately separate from held-out evaluation.  It admits
only a complete training artifact set; it makes no behavioral or attention
claim.  Remote/local byte comparison remains a transfer-layer responsibility.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import math
import numbers
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
FINAL_ITERATION = 19_999
TRAINING_ITERATIONS = 20_000
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_PRODUCER_IDENTITIES = {
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
    "scripts/launch_vda16_fresh.sh",
    "experiments/vda4_spatial_discretization/grid_10x10/launch_20k.sh",
    "resolved_config",
    "experiment_launcher",
}


@dataclass(frozen=True)
class TerminalRunSpec:
    task: str
    final_checkpoint_name: str
    grid_rows: int = 4
    grid_cols: int = 4
    image_size: int = 100
    feedback: str = "crossattn1"
    d_mem: int = 128
    memory_decay: float = 1.0


RUN_SPECS = {
    task: TerminalRunSpec(task, f"rvit_paper_{task}_final.pt")
    for task in ("vda16", "vda_fixed9")
}
FACTORIAL_TASK = "vda4"
FACTORIAL_SPEC = TerminalRunSpec(
    FACTORIAL_TASK,
    "rvit_paper_vda4_final.pt",
    grid_rows=10,
    grid_cols=10,
    image_size=50,
)
FACTORIAL_FACTORY_KEYS = frozenset((
    "kind",
    "effective_visual_streams",
    "effective_memory_streams",
    "carrier_grid",
))
FACTORIAL_STREAM_LEVELS = frozenset((4, 100))


def _install_numpy_pickle_compat() -> None:
    """Permit NumPy-2 checkpoint metadata to load under NumPy 1.x.

    NumPy 2 serializes some scalar metadata through ``numpy._core`` while the
    equivalent modules live under ``numpy.core`` in NumPy 1.x.  Mapping only
    those module names preserves the underlying objects and all subsequent
    finite/equality checks; it does not relax checkpoint validation.
    """
    try:
        importlib.import_module("numpy._core")
        return
    except ModuleNotFoundError:
        pass
    legacy_core = importlib.import_module("numpy.core")
    sys.modules.setdefault("numpy._core", legacy_core)
    for suffix in ("multiarray", "_multiarray_umath", "numeric", "umath"):
        try:
            module = importlib.import_module(f"numpy.core.{suffix}")
        except ModuleNotFoundError:
            continue
        sys.modules.setdefault(f"numpy._core.{suffix}", module)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_metrics(path: str | Path) -> dict[str, Any]:
    """Validate an exact finite ledger with global iterations 0..19999."""
    path = Path(path)
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != TRAINING_ITERATIONS:
        raise ValueError(
            f"metrics contain {len(rows)} rows; expected {TRAINING_ITERATIONS}"
        )
    if not rows or "iter" not in rows[0]:
        raise ValueError("metrics are missing the iter column")
    iterations = np.asarray([int(row["iter"]) for row in rows], dtype=np.int64)
    np.testing.assert_array_equal(iterations, np.arange(TRAINING_ITERATIONS))
    for field in rows[0]:
        if field == "iter":
            continue
        values = np.asarray([float(row[field]) for row in rows], dtype=np.float64)
        if not np.isfinite(values).all():
            raise ValueError(f"metrics column {field!r} contains non-finite values")
    return {
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
        "rows": len(rows),
        "first_iteration": int(iterations[0]),
        "last_iteration": int(iterations[-1]),
        "columns": list(rows[0]),
    }


def _require_mapping_value(mapping: dict[str, Any], key: str, expected: Any, label: str) -> None:
    actual = mapping.get(key)
    if isinstance(expected, float):
        matched = isinstance(actual, numbers.Real) and math.isclose(
            float(actual), expected, rel_tol=0.0, abs_tol=1e-12
        )
    else:
        matched = actual == expected
    if not matched:
        raise ValueError(f"{label} {key}={actual!r}, expected {expected!r}")


def _assert_finite_tree(value: Any, label: str) -> int:
    """Return the number of numeric leaves after rejecting non-finite state."""
    try:
        import torch
    except ImportError:  # pragma: no cover - checkpoint loading already requires torch
        torch = None
    if torch is not None and isinstance(value, torch.Tensor):
        if value.is_floating_point() or value.is_complex():
            if not bool(torch.isfinite(value).all()):
                raise ValueError(f"{label} contains a non-finite tensor")
        return int(value.numel())
    if isinstance(value, np.ndarray):
        if np.issubdtype(value.dtype, np.inexact) and not np.isfinite(value).all():
            raise ValueError(f"{label} contains a non-finite array")
        return int(value.size)
    if isinstance(value, dict):
        return sum(_assert_finite_tree(item, f"{label}.{key}") for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return sum(_assert_finite_tree(item, f"{label}[{index}]") for index, item in enumerate(value))
    if isinstance(value, numbers.Real) and not isinstance(value, bool):
        if not math.isfinite(float(value)):
            raise ValueError(f"{label} contains non-finite scalar {value!r}")
        return 1
    return 0


def _assert_semantically_equal(left: Any, right: Any, label: str = "checkpoint") -> int:
    """Compare two deserialized checkpoint trees independently of pickle bytes."""
    _install_numpy_pickle_compat()
    import torch

    if isinstance(left, torch.Tensor) or isinstance(right, torch.Tensor):
        if not isinstance(left, torch.Tensor) or not isinstance(right, torch.Tensor):
            raise ValueError(f"{label} tensor type mismatch")
        if left.dtype != right.dtype or left.shape != right.shape or not torch.equal(left, right):
            raise ValueError(f"{label} tensor mismatch")
        return int(left.numel())
    if isinstance(left, np.ndarray) or isinstance(right, np.ndarray):
        if not isinstance(left, np.ndarray) or not isinstance(right, np.ndarray):
            raise ValueError(f"{label} array type mismatch")
        if left.dtype != right.dtype or left.shape != right.shape or not np.array_equal(
            left, right, equal_nan=True
        ):
            raise ValueError(f"{label} array mismatch")
        return int(left.size)
    if isinstance(left, dict) or isinstance(right, dict):
        if not isinstance(left, dict) or not isinstance(right, dict) or left.keys() != right.keys():
            raise ValueError(f"{label} mapping inventory mismatch")
        return sum(
            _assert_semantically_equal(left[key], right[key], f"{label}.{key}")
            for key in left
        )
    if isinstance(left, (list, tuple)) or isinstance(right, (list, tuple)):
        if type(left) is not type(right) or len(left) != len(right):
            raise ValueError(f"{label} sequence mismatch")
        return sum(
            _assert_semantically_equal(a, b, f"{label}[{index}]")
            for index, (a, b) in enumerate(zip(left, right, strict=True))
        )
    if isinstance(left, float) and isinstance(right, float) and math.isnan(left) and math.isnan(right):
        return 1
    if left != right:
        raise ValueError(f"{label} scalar mismatch: {left!r} != {right!r}")
    return 1 if isinstance(left, numbers.Number) else 0


def _validate_stream_level(value: Any, field: str) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"{field} must be an integer (not bool)")
    value = int(value)
    if value not in FACTORIAL_STREAM_LEVELS:
        raise ValueError(f"{field} must be 4 or 100")
    return value


def _expected_projector_buffers(streams: int) -> tuple[np.ndarray, np.ndarray]:
    """Construct the exact registered 10x10 mean-and-broadcast projector."""
    streams = _validate_stream_level(streams, "effective streams")
    effective_rows, effective_cols = ((2, 2) if streams == 4 else (10, 10))
    row_group = np.arange(10, dtype=np.int64) // (10 // effective_rows)
    col_group = np.arange(10, dtype=np.int64) // (10 // effective_cols)
    group_ids = (
        row_group[:, None] * effective_cols + col_group[None, :]
    ).reshape(-1)
    matrix = np.zeros((100, 100), dtype=np.float32)
    for group in range(streams):
        members = np.flatnonzero(group_ids == group)
        matrix[np.ix_(members, members)] = np.float32(1.0 / len(members))
    return group_ids, matrix


def _validate_projector_buffers(
    state: Any, *, visual_streams: int, memory_streams: int, label: str
) -> None:
    """Require exact persistent buffers for both factorial bottlenecks."""
    _install_numpy_pickle_compat()
    import torch

    if not isinstance(state, dict):
        raise ValueError(f"{label} must be a mapping")
    for prefix, streams in (
        ("front.projector", visual_streams),
        ("encoder.memory_projector", memory_streams),
    ):
        expected_ids, expected_matrix = _expected_projector_buffers(streams)
        group_key = f"{prefix}.group_ids"
        matrix_key = f"{prefix}.matrix"
        group_ids = state.get(group_key)
        matrix = state.get(matrix_key)
        if not isinstance(group_ids, torch.Tensor) or not isinstance(matrix, torch.Tensor):
            raise ValueError(
                f"{label} lacks tensor projector buffers {group_key!r}/{matrix_key!r}"
            )
        if not torch.equal(group_ids.detach().cpu(), torch.from_numpy(expected_ids)):
            raise ValueError(f"{label} {group_key!r} does not match the registered projector")
        if not torch.equal(matrix.detach().cpu(), torch.from_numpy(expected_matrix)):
            raise ValueError(f"{label} {matrix_key!r} does not match the registered projector")


def _validate_model_factory(
    payload: dict[str, Any],
    *,
    expected_visual_streams: int | None,
    expected_memory_streams: int | None,
    label: str,
) -> dict[str, Any] | None:
    """Validate an explicit factorial factory, rejecting ambiguous contracts."""
    factory = payload.get("model_factory")
    factorial_requested = (
        expected_visual_streams is not None or expected_memory_streams is not None
    )
    if not factorial_requested:
        if factory is not None:
            raise ValueError(f"{label} unexpectedly declares model_factory")
        return None
    if expected_visual_streams is None or expected_memory_streams is None:
        raise ValueError("both expected visual and memory stream levels are required")
    visual = _validate_stream_level(
        expected_visual_streams, "expected_visual_streams"
    )
    memory = _validate_stream_level(
        expected_memory_streams, "expected_memory_streams"
    )
    if not isinstance(factory, dict):
        raise ValueError(f"{label} lacks model_factory mapping")
    if set(factory) != FACTORIAL_FACTORY_KEYS:
        raise ValueError(
            f"{label} model_factory inventory mismatch: got {sorted(factory)}, "
            f"expected {sorted(FACTORIAL_FACTORY_KEYS)}"
        )
    expected = {
        "kind": "stream_factorial_v1",
        "effective_visual_streams": visual,
        "effective_memory_streams": memory,
        "carrier_grid": [10, 10],
    }
    for key, value in expected.items():
        _require_mapping_value(factory, key, value, f"{label} model_factory")
    if not isinstance(factory["carrier_grid"], list):
        raise ValueError(f"{label} model_factory carrier_grid must be the exact list [10, 10]")
    return expected


def _validate_checkpoint_payload(
    payload: dict[str, Any],
    spec: TerminalRunSpec,
    *,
    expected_seed: int,
    label: str,
    expected_visual_streams: int | None = None,
    expected_memory_streams: int | None = None,
) -> dict[str, Any]:
    if int(payload.get("checkpoint_schema_version", -1)) < 3:
        raise ValueError(f"{label} must use checkpoint schema 3 or later")
    _require_mapping_value(payload, "iter", FINAL_ITERATION, label)
    _require_mapping_value(payload, "task", spec.task, label)
    model = payload.get("model_kwargs")
    training = payload.get("training_args")
    initialization = payload.get("initialization_contract")
    if not isinstance(model, dict) or not isinstance(training, dict):
        raise ValueError(f"{label} lacks embedded model_kwargs/training_args")
    if not isinstance(initialization, dict):
        raise ValueError(f"{label} lacks initialization_contract")
    model_factory = _validate_model_factory(
        payload,
        expected_visual_streams=expected_visual_streams,
        expected_memory_streams=expected_memory_streams,
        label=label,
    )
    expected_model = {
        "feedback": spec.feedback,
        "d_mem": spec.d_mem,
        "memory_decay": spec.memory_decay,
        "conv_frontend": True,
        "grid_rows": spec.grid_rows,
        "grid_cols": spec.grid_cols,
        "image_size": spec.image_size,
        "seq_len": 7,
    }
    expected_training = {
        "task": spec.task,
        "feedback": spec.feedback,
        "d_mem": spec.d_mem,
        "memory_decay": spec.memory_decay,
        "patch_grid_rows": spec.grid_rows,
        "patch_grid_cols": spec.grid_cols,
        "curriculum": True,
        "seed": expected_seed,
        "iters": TRAINING_ITERATIONS,
        "schedule_final_iteration": FINAL_ITERATION,
        "episodes_per_iter": 8,
        "init_mode": "fresh",
    }
    if model_factory is not None:
        expected_model.update({
            "memory_noise_std": 0.0,
            "cell": "xlstm",
            "two_lstm": False,
            "jepa_n_heads": 4,
            "jepa_proto_dim": 256,
            "frame_repeat": 1,
        })
        expected_training.update({
            "T": 7,
            "frame_repeat": 1,
            "memory_noise_std": 0.0,
            "cell": "xlstm",
            "two_lstm": False,
            "conv_frontend": True,
            "jepa_coef": 0.5,
            "jepa_heads": 4,
            "jepa_proto_dim": 256,
            "start_iteration": 0,
            "effective_visual_streams": expected_visual_streams,
            "effective_memory_streams": expected_memory_streams,
        })
    for key, expected in expected_model.items():
        _require_mapping_value(model, key, expected, f"{label} model_kwargs")
    for key, expected in expected_training.items():
        _require_mapping_value(training, key, expected, f"{label} training_args")
    _require_mapping_value(initialization, "mode", "fresh", f"{label} initialization_contract")
    _require_mapping_value(payload, "replay_buffer_persisted", False, label)
    _require_mapping_value(
        payload, "resume_fidelity", "replay_excluded_trainer_state", label
    )
    for key in (
        "model_state_dict",
        "optimizer_state_dict",
        "target_model_state_dict",
        "jepa_teacher_state_dict",
        "environment_state",
        "rolling_correct",
        "rolling_return",
    ):
        if key not in payload or payload[key] is None:
            raise ValueError(f"{label} lacks required state {key!r}")
    if model_factory is not None:
        for state_name in ("model_state_dict", "target_model_state_dict"):
            _validate_projector_buffers(
                payload[state_name],
                visual_streams=model_factory["effective_visual_streams"],
                memory_streams=model_factory["effective_memory_streams"],
                label=f"{label}.{state_name}",
            )
    finite_leaves = sum(
        _assert_finite_tree(payload[key], f"{label}.{key}")
        for key in (
            "model_state_dict",
            "optimizer_state_dict",
            "target_model_state_dict",
            "jepa_teacher_state_dict",
            "environment_state",
            "rolling_correct",
            "rolling_return",
        )
    )
    if finite_leaves <= 0:
        raise ValueError(f"{label} contains no finite numeric state")
    producer = payload.get("producer_sha256")
    if not isinstance(producer, dict) or not producer:
        raise ValueError(f"{label} lacks producer SHA-256 provenance")
    missing_producers = REQUIRED_PRODUCER_IDENTITIES - set(producer)
    if missing_producers:
        raise ValueError(
            f"{label} producer map lacks required identities: {sorted(missing_producers)}"
        )
    for identity, digest in producer.items():
        if not isinstance(digest, str) or not HEX_SHA256.fullmatch(digest.lower()):
            raise ValueError(f"{label} producer hash is invalid for {identity!r}")
    return {
        "finite_numeric_leaves": finite_leaves,
        "producer_sha256": producer,
        "model_factory": model_factory,
    }


def _verify_producer_hashes(
    producer: dict[str, str], *, project_root: Path, launcher: Path, config: Path
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for identity, expected in sorted(producer.items()):
        if identity == "experiment_launcher":
            path = launcher
        elif identity == "resolved_config":
            path = config
        else:
            path = project_root / identity
        if not path.is_file():
            raise FileNotFoundError(f"producer source is missing for {identity!r}: {path}")
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(
                f"producer SHA-256 mismatch for {identity!r}: {actual} != {expected}"
            )
        checks.append({
            "identity": identity,
            "path": str(path.resolve()),
            "sha256": actual,
            "bytes": path.stat().st_size,
        })
    return checks


def validate_terminal_run(
    run_dir: str | Path,
    *,
    task: str,
    expected_seed: int,
    project_root: str | Path,
    launcher: str | Path,
    config: str | Path,
    log: str | Path,
    expected_final_sha256: str | None = None,
    expected_visual_streams: int | None = None,
    expected_memory_streams: int | None = None,
) -> dict[str, Any]:
    """Validate one local, already-pulled run directory without evaluating behavior."""
    if task == FACTORIAL_TASK:
        if expected_visual_streams is None or expected_memory_streams is None:
            raise ValueError(
                "vda4 terminal validation is reserved for the stream factorial and requires "
                "explicit expected_visual_streams and expected_memory_streams"
            )
        _validate_stream_level(expected_visual_streams, "expected_visual_streams")
        _validate_stream_level(expected_memory_streams, "expected_memory_streams")
        spec = FACTORIAL_SPEC
    else:
        if expected_visual_streams is not None or expected_memory_streams is not None:
            raise ValueError("stream-level expectations are valid only for task 'vda4'")
        try:
            spec = RUN_SPECS[task]
        except KeyError as exc:
            supported = sorted((*RUN_SPECS, FACTORIAL_TASK))
            raise ValueError(
                f"unsupported terminal run task {task!r}; expected {supported}"
            ) from exc
    run_dir = Path(run_dir).resolve()
    project_root = Path(project_root).resolve()
    launcher = Path(launcher).resolve()
    config = Path(config).resolve()
    log = Path(log).resolve()
    final_path = run_dir / spec.final_checkpoint_name
    latest_path = run_dir / "rvit_plus_rl_latest.pt"
    metrics_path = run_dir / "metrics.csv"
    for path in (run_dir, final_path, latest_path, metrics_path, launcher, config, log):
        if not path.exists():
            raise FileNotFoundError(path)
    final_sha = sha256_file(final_path)
    latest_sha = sha256_file(latest_path)
    if expected_final_sha256 is not None and final_sha.lower() != expected_final_sha256.lower():
        raise RuntimeError(
            f"final checkpoint SHA-256 mismatch: {final_sha} != {expected_final_sha256}"
        )
    metrics = load_metrics(metrics_path)
    log_text = log.read_text(encoding="utf-8-sig", errors="replace")
    if "Traceback" in log_text:
        raise RuntimeError("training log contains a traceback")
    for marker in (
        "[checkpoint] saved replay-excluded trainer state to",
        "iters logged=20000",
    ):
        if marker not in log_text:
            raise RuntimeError(f"training log lacks terminal marker {marker!r}")

    _install_numpy_pickle_compat()
    import torch

    final_payload = torch.load(final_path, map_location="cpu", weights_only=False)
    latest_payload = torch.load(latest_path, map_location="cpu", weights_only=False)
    if not isinstance(final_payload, dict) or not isinstance(latest_payload, dict):
        raise ValueError("final/latest checkpoint payload must be mappings")
    final_validation = _validate_checkpoint_payload(
        final_payload,
        spec,
        expected_seed=expected_seed,
        label="final checkpoint",
        expected_visual_streams=expected_visual_streams,
        expected_memory_streams=expected_memory_streams,
    )
    latest_validation = _validate_checkpoint_payload(
        latest_payload,
        spec,
        expected_seed=expected_seed,
        label="latest checkpoint",
        expected_visual_streams=expected_visual_streams,
        expected_memory_streams=expected_memory_streams,
    )
    compared_numeric_leaves = _assert_semantically_equal(
        final_payload, latest_payload, "final/latest"
    )
    if final_validation["producer_sha256"] != latest_validation["producer_sha256"]:
        raise ValueError("final/latest producer maps differ")
    producer_checks = _verify_producer_hashes(
        final_validation["producer_sha256"],
        project_root=project_root,
        launcher=launcher,
        config=config,
    )
    result = {
        "schema_version": 1,
        "status": "validated_terminal_training_artifacts_only",
        "scientific_behavior_evaluated": False,
        "spec": asdict(spec),
        "seed": int(expected_seed),
        "run_dir": str(run_dir),
        "metrics": metrics,
        "log": {
            "path": str(log),
            "sha256": sha256_file(log),
            "bytes": log.stat().st_size,
            "terminal_markers_present": True,
            "traceback_absent": True,
        },
        "final_checkpoint": {
            "path": str(final_path),
            "sha256": final_sha,
            "bytes": final_path.stat().st_size,
        },
        "latest_checkpoint": {
            "path": str(latest_path),
            "sha256": latest_sha,
            "bytes": latest_path.stat().st_size,
        },
        "final_latest_semantically_equal": True,
        "compared_numeric_leaves": compared_numeric_leaves,
        "finite_numeric_leaves": final_validation["finite_numeric_leaves"],
        "producer_checks": producer_checks,
        "claim_boundary": (
            "Terminal training integrity only. Held-out behavior, attention organization, "
            "and causal dependence require the separate production evaluator."
        ),
    }
    if final_validation["model_factory"] is not None:
        result["model_factory"] = final_validation["model_factory"]
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument(
        "--task", choices=tuple(sorted((*RUN_SPECS, FACTORIAL_TASK))), required=True
    )
    parser.add_argument("--expected-seed", type=int, required=True)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--launcher", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "default.json")
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--expected-final-sha256")
    parser.add_argument("--expected-visual-streams", type=int, choices=(4, 100))
    parser.add_argument("--expected-memory-streams", type=int, choices=(4, 100))
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_terminal_run(
        args.run_dir,
        task=args.task,
        expected_seed=args.expected_seed,
        project_root=args.project_root,
        launcher=args.launcher,
        config=args.config,
        log=args.log,
        expected_final_sha256=args.expected_final_sha256,
        expected_visual_streams=args.expected_visual_streams,
        expected_memory_streams=args.expected_memory_streams,
    )
    text = json.dumps(result, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(
        f"VALID|task={args.task}|seed={args.expected_seed}|"
        f"iter={FINAL_ITERATION}|rows={TRAINING_ITERATIONS}|"
        f"checkpoint_sha256={result['final_checkpoint']['sha256']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
