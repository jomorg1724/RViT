#!/usr/bin/env python3
"""Validate one terminal native-2x2 VDA4 memory-noise training artifact set.

This is a training-integrity validator only. It deliberately does not inspect
cueing, attention allocation, causal effects, training accuracy, or curriculum
theta. Paired scientific evaluation is admissible only after this validator
passes independently for both registered noise conditions.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import sys
from dataclasses import asdict
from typing import Any


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
EXPERIMENT_DIR = pathlib.Path(__file__).resolve().parent
EXPECTED_CONFIG_SHA256 = "01971fd731e030ed377f0c7db1164f0cf8c01285fbb57e7eda7381aed2414eb7"
EXPECTED_DESIGN_SHA256 = "1ae15e32b35687501554463a714074b6774e70aed524780ff14a733d832ec97b"
NOISE_LEVELS = (0.0, 0.5)
SEED = 0
FINAL_ITERATION = 19_999
TRAINING_ITERATIONS = 20_000
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _require(mapping: dict[str, Any], dotted_key: str, expected: Any, label: str) -> None:
    current: Any = mapping
    for component in dotted_key.split("."):
        if not isinstance(current, dict) or component not in current:
            raise ValueError(f"{label} lacks {dotted_key!r}")
        current = current[component]
    if current != expected:
        raise ValueError(
            f"{label} {dotted_key!r}: expected {expected!r}, got {current!r}"
        )


def _condition_id(noise_std: float) -> str:
    if noise_std == 0.0:
        return "noise0p0"
    if noise_std == 0.5:
        return "noise0p5"
    raise ValueError(f"expected_memory_noise_std must be one of {NOISE_LEVELS}")


def _validate_exact_checkpoint_contract(
    payload: dict[str, Any], *, expected_noise_std: float, label: str
) -> None:
    model = payload.get("model_kwargs")
    training = payload.get("training_args")
    resume = payload.get("resume_contract")
    if not isinstance(model, dict) or not isinstance(training, dict) or not isinstance(resume, dict):
        raise ValueError(f"{label} lacks model/training/resume contract mappings")
    expected_model = {
        "n_actions": 2,
        "n_quantiles": 5,
        "init_action_bias": [0.0, -1.5],
        "seq_len": 7,
        "feedback": "crossattn1",
        "two_lstm": False,
        "cell": "xlstm",
        "jepa_n_heads": 4,
        "jepa_proto_dim": 256,
        "frame_repeat": 1,
        "d_mem": 128,
        "memory_decay": 1.0,
        "memory_noise_std": expected_noise_std,
        "conv_frontend": True,
        "grid_rows": 2,
        "grid_cols": 2,
        "image_size": 50,
    }
    expected_training = {
        "task": "vda4",
        "T": 7,
        "frame_repeat": 1,
        "min_change_time": 5,
        "max_change_time": 5,
        "noise": 5.0,
        "patch_grid_rows": 2,
        "patch_grid_cols": 2,
        "effective_visual_streams": None,
        "effective_memory_streams": None,
        "cell": "xlstm",
        "two_lstm": False,
        "feedback": "crossattn1",
        "d_mem": 128,
        "memory_decay": 1.0,
        "memory_noise_std": expected_noise_std,
        "conv_frontend": True,
        "n_actions": 2,
        "n_quantiles": 5,
        "init_action_bias": [0.0, -1.5],
        "jepa_coef": 0.5,
        "jepa_heads": 4,
        "jepa_proto_dim": 256,
        "jepa_same_time": False,
        "jepa_tau_student": 0.1,
        "jepa_tau_teacher_start": 0.04,
        "jepa_tau_teacher_end": 0.07,
        "jepa_tau_warmup": 300,
        "jepa_center_momentum": 0.9,
        "jepa_ema_decay": 0.996,
        "curriculum": True,
        "theta_start": 65.0,
        "curr_window": 1000,
        "curr_threshold": 0.85,
        "curr_step": 3.0,
        "curr_floor": 8.0,
        "lr": 0.0003,
        "gamma": 0.95,
        "entropy_coef": 0.01,
        "ema_decay": 0.995,
        "buffer_capacity": 1000,
        "qr_kappa": 1.0,
        "mpo_temperature": 0.1,
        "init_mode": "fresh",
        "start_iteration": 0,
        "iters": TRAINING_ITERATIONS,
        "schedule_final_iteration": FINAL_ITERATION,
        "episodes_per_iter": 8,
        "save_every": 50,
        "log_every": 1,
        "seed": SEED,
        "device": "cuda",
        "checkpoint_path": None,
        "expected_parent_sha256": None,
        "allow_schedule_overrun_resume": False,
    }
    for key, expected in expected_model.items():
        _require(model, key, expected, f"{label}.model_kwargs")
    for key, expected in expected_training.items():
        _require(training, key, expected, f"{label}.training_args")
    _require(payload, "initialization_contract.mode", "fresh", label)
    _require(resume, "task", "vda4", f"{label}.resume_contract")
    _require(resume, "episodes_per_iter", 8, f"{label}.resume_contract")
    _require(
        resume,
        "schedule_final_iteration",
        FINAL_ITERATION,
        f"{label}.resume_contract",
    )
    if resume.get("model_kwargs") != model:
        raise ValueError(f"{label} resume model_kwargs differ from checkpoint model_kwargs")
    if resume.get("producer_sha256") != payload.get("producer_sha256"):
        raise ValueError(f"{label} resume producer map differs from checkpoint producer map")
    if payload.get("model_factory") is not None:
        raise ValueError(f"{label} must use the native model path, not a custom model_factory")


def _validate_launch_contract(
    path: pathlib.Path,
    *,
    expected_noise_std: float,
    project_root: pathlib.Path,
    launcher: pathlib.Path,
    config: pathlib.Path,
    design: pathlib.Path,
) -> dict[str, Any]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    condition = _condition_id(expected_noise_std)
    _require(contract, "schema_version", 1, "launch contract")
    _require(contract, "status", "preflight_passed", "launch contract")
    _require(contract, "request.condition_id", condition, "launch contract")
    _require(
        contract,
        "request.memory_noise_std",
        expected_noise_std,
        "launch contract",
    )
    _require(contract, "request.seed", SEED, "launch contract")
    _require(contract, "request.run_kind", "production", "launch contract")
    _require(contract, "request.iterations", TRAINING_ITERATIONS, "launch contract")
    _require(contract, "request.terminal_iteration", FINAL_ITERATION, "launch contract")

    from analysis.vda_terminal_run_validation import sha256_file

    actual_hashes = {
        "config": sha256_file(config),
        "design": sha256_file(design),
        "launcher": sha256_file(launcher),
        "preflight": sha256_file(EXPERIMENT_DIR / "preflight_contract_v1.py"),
    }
    if actual_hashes["config"] != EXPECTED_CONFIG_SHA256:
        raise RuntimeError("config no longer matches the frozen pilot SHA-256")
    if actual_hashes["design"] != EXPECTED_DESIGN_SHA256:
        raise RuntimeError("design no longer matches the frozen pilot SHA-256")
    for key, actual in actual_hashes.items():
        _require(contract, f"sha256.{key}", actual, "launch contract")
    env_trace = contract.get("sha256", {}).get("initial_environment_reset_diagnostic")
    trainable = contract.get("sha256", {}).get("trainable_initialization")
    if not isinstance(env_trace, str) or not HEX_SHA256.fullmatch(env_trace):
        raise ValueError("launch contract has an invalid initial reset diagnostic hash")
    if not isinstance(trainable, str) or not HEX_SHA256.fullmatch(trainable):
        raise ValueError("launch contract has an invalid trainable-initialization hash")
    design_payload = json.loads(design.read_text(encoding="utf-8"))
    _require(
        design_payload,
        "initial_environment_reset_diagnostic.expected_sha256",
        env_trace,
        "design manifest",
    )
    source_contract = design_payload.get("source_contract", {}).get("required_sha256", {})
    if contract.get("source_sha256") != source_contract:
        raise ValueError("launch contract source inventory differs from the frozen design")
    claimed_project_root = pathlib.PurePath(contract.get("project_root", ""))
    if not claimed_project_root.name or claimed_project_root.name != project_root.name:
        raise ValueError("launch contract project_root identity differs from validation project_root")
    return contract


def _validate_runtime_identity(path: pathlib.Path) -> dict[str, Any]:
    identity = json.loads(path.read_text(encoding="utf-8"))
    _require(identity, "schema_version", 1, "runtime identity")
    pair_id = identity.get("pair_id")
    runtime_sha = identity.get("runtime_sha256")
    gpu_uuid = identity.get("gpu_uuid")
    if not isinstance(pair_id, str) or not re.fullmatch(
        r"production_[0-9]{8}T[0-9]{6}Z_[0-9a-f]{12}", pair_id
    ):
        raise ValueError(f"runtime identity has invalid production pair_id {pair_id!r}")
    if not isinstance(runtime_sha, str) or not HEX_SHA256.fullmatch(runtime_sha):
        raise ValueError("runtime identity has invalid runtime_sha256")
    if not isinstance(gpu_uuid, str) or not gpu_uuid.startswith("GPU-"):
        raise ValueError("runtime identity has invalid physical GPU UUID")
    return identity


def validate_terminal(
    run_dir: str | pathlib.Path,
    *,
    expected_memory_noise_std: float,
    project_root: str | pathlib.Path,
    launcher: str | pathlib.Path,
    config: str | pathlib.Path,
    design: str | pathlib.Path,
    log: str | pathlib.Path | None = None,
    expected_final_sha256: str | None = None,
) -> dict[str, Any]:
    """Fail closed unless one production condition is exactly terminal and bound."""
    condition = _condition_id(float(expected_memory_noise_std))
    run_dir = pathlib.Path(run_dir).resolve()
    project_root = pathlib.Path(project_root).resolve()
    launcher = pathlib.Path(launcher).resolve()
    config = pathlib.Path(config).resolve()
    design = pathlib.Path(design).resolve()
    log = pathlib.Path(log).resolve() if log is not None else run_dir / "train.log"
    final_path = run_dir / "rvit_paper_vda4_final.pt"
    latest_path = run_dir / "rvit_plus_rl_latest.pt"
    metrics_path = run_dir / "metrics.csv"
    launch_contract_path = run_dir / "launch_contract.json"
    runtime_identity_path = run_dir / "runtime_identity.json"
    for path in (
        run_dir,
        final_path,
        latest_path,
        metrics_path,
        launch_contract_path,
        runtime_identity_path,
        launcher,
        config,
        design,
        log,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    if condition not in run_dir.name or "seed0_production_v1" not in run_dir.name:
        raise ValueError("run directory name does not bind the expected condition/seed/run kind")

    if project_root not in (launcher.parents[0], *launcher.parents):
        raise ValueError("launcher is outside the requested project root")

    sys.path.insert(0, str(project_root))
    from analysis.vda_terminal_run_validation import (
        TerminalRunSpec,
        _assert_semantically_equal,
        _install_numpy_pickle_compat,
        _validate_checkpoint_payload,
        _verify_producer_hashes,
        load_metrics,
        sha256_file,
    )

    final_sha = sha256_file(final_path)
    latest_sha = sha256_file(latest_path)
    if expected_final_sha256 is not None and final_sha != expected_final_sha256.lower():
        raise RuntimeError(
            f"final checkpoint SHA-256 mismatch: {final_sha} != {expected_final_sha256}"
        )
    metrics = load_metrics(metrics_path)
    if metrics.get("rows") != TRAINING_ITERATIONS:
        raise ValueError("terminal metrics row count is not exactly 20000")
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
        raise ValueError("final/latest checkpoint payloads must be mappings")
    spec = TerminalRunSpec(
        task="vda4",
        final_checkpoint_name="rvit_paper_vda4_final.pt",
        grid_rows=2,
        grid_cols=2,
        image_size=50,
        feedback="crossattn1",
        d_mem=128,
        memory_decay=1.0,
    )
    final_validation = _validate_checkpoint_payload(
        final_payload, spec, expected_seed=SEED, label="final checkpoint"
    )
    latest_validation = _validate_checkpoint_payload(
        latest_payload, spec, expected_seed=SEED, label="latest checkpoint"
    )
    _validate_exact_checkpoint_contract(
        final_payload,
        expected_noise_std=float(expected_memory_noise_std),
        label="final checkpoint",
    )
    _validate_exact_checkpoint_contract(
        latest_payload,
        expected_noise_std=float(expected_memory_noise_std),
        label="latest checkpoint",
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

    launch_contract = _validate_launch_contract(
        launch_contract_path,
        expected_noise_std=float(expected_memory_noise_std),
        project_root=project_root,
        launcher=launcher,
        config=config,
        design=design,
    )
    if launch_contract.get("producer_sha256") != final_validation["producer_sha256"]:
        raise ValueError("launch/checkpoint producer SHA-256 maps differ")
    runtime_identity = _validate_runtime_identity(runtime_identity_path)
    # Checkpoints are validated both on the worker and after a hash-verified stage
    # pull. Absolute worker paths cannot equal local Windows paths after transfer,
    # so bind their identities and bytes rather than requiring path equality.
    training_launcher = pathlib.PurePath(
        final_payload.get("training_args", {}).get("experiment_launcher", "")
    )
    if training_launcher.name != launcher.name:
        raise ValueError("checkpoint experiment_launcher identity differs from validated launcher")
    training_config = pathlib.PurePath(
        final_payload.get("training_args", {}).get("config", "")
    )
    if training_config.name != config.name:
        raise ValueError("checkpoint config identity differs from validated config")
    checkpoint_dir = pathlib.PurePath(
        final_payload.get("training_args", {}).get("checkpoint_dir", "")
    )
    if checkpoint_dir.name != run_dir.name:
        raise ValueError("checkpoint_dir identity differs from run-directory identity")

    return {
        "schema_version": 1,
        "status": "validated_terminal_training_artifacts_only",
        "scientific_behavior_evaluated": False,
        "condition_id": condition,
        "memory_noise_std": float(expected_memory_noise_std),
        "seed": SEED,
        "spec": asdict(spec),
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
        "launch_contract": {
            "path": str(launch_contract_path),
            "sha256": sha256_file(launch_contract_path),
            "validated": True,
        },
        "runtime_identity": runtime_identity,
        "claim_boundary": (
            "Terminal training integrity only. This is not cueing, attention-allocation, "
            "causal-mechanism, or signal-coherence evidence."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=pathlib.Path, required=True)
    parser.add_argument(
        "--expected-memory-noise-std", type=float, choices=NOISE_LEVELS, required=True
    )
    parser.add_argument("--project-root", type=pathlib.Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--launcher",
        type=pathlib.Path,
        default=EXPERIMENT_DIR / "launch_production_v1.sh",
    )
    parser.add_argument(
        "--config", type=pathlib.Path, default=EXPERIMENT_DIR / "config_v1.json"
    )
    parser.add_argument(
        "--design", type=pathlib.Path, default=EXPERIMENT_DIR / "design_manifest.json"
    )
    parser.add_argument("--log", type=pathlib.Path)
    parser.add_argument("--expected-final-sha256")
    parser.add_argument("--output", type=pathlib.Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_terminal(
        args.run_dir,
        expected_memory_noise_std=args.expected_memory_noise_std,
        project_root=args.project_root,
        launcher=args.launcher,
        config=args.config,
        design=args.design,
        log=args.log,
        expected_final_sha256=args.expected_final_sha256,
    )
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(
        f"VALID|condition={result['condition_id']}|noise={result['memory_noise_std']}|"
        f"seed=0|iter={FINAL_ITERATION}|rows={TRAINING_ITERATIONS}|"
        f"checkpoint_sha256={result['final_checkpoint']['sha256']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
