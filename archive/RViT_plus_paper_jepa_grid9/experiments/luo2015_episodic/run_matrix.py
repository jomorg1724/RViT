#!/usr/bin/env python3
"""Paired episodic Luo--Maunsell optimization experiment.

Each seed first trains one neutral, perceptually competent parent. The exact parent
weights are then forked into four fixed-condition agents: sensitivity/criterion
by counterphased location 0/3. This tests condition-specific policy optima without
requiring reward-block inference or recurrent state across trials.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


@dataclass(frozen=True)
class ExperimentCell:
    role: str
    seed: int
    task: str
    condition_loc: int | None
    output_dir: Path
    command: tuple[str, ...]
    parent_checkpoint: Path | None = None


def _common_training_args(
    *,
    project_root: Path,
    python_executable: Path,
    output_dir: Path,
    iterations: int,
    seed: int,
    device: str,
    feedback: str,
    memory_decay: float,
    noise: float,
) -> list[str]:
    launcher = Path(__file__).resolve()
    return [
        str(python_executable),
        str((project_root / "train_rl.py").resolve()),
        "--T", "7",
        "--patch-grid-rows", "2",
        "--patch-grid-cols", "2",
        "--cell", "xlstm",
        "--feedback", feedback,
        "--memory-decay", str(float(memory_decay)),
        "--noise", str(float(noise)),
        "--conv-frontend",
        "--jepa-coef", "0.5",
        "--d-mem", "128",
        "--episodes-per-iter", "8",
        "--gamma", "1.0",
        "--save-every", "50",
        "--log-every", "1",
        "--seed", str(seed),
        "--device", device,
        "--iters", str(iterations),
        "--schedule-final-iteration", str(iterations - 1),
        "--checkpoint-dir", str(output_dir.resolve()),
        "--experiment-launcher", str(launcher),
    ]


def build_cells(
    *,
    project_root: Path,
    run_root: Path,
    python_executable: Path,
    seeds: Iterable[int],
    parent_iterations: int,
    child_iterations: int,
    device: str,
    theta: float,
    feedback: str = "affine_ew",
    memory_decay: float = 1.0,
    noise: float = 5.0,
) -> list[ExperimentCell]:
    """Build the neutral-parent plus four paired child runs for every seed."""
    project_root = Path(project_root).resolve()
    run_root = Path(run_root).resolve()
    # Keep a virtualenv executable as a virtualenv executable. Resolving its
    # symlink can select the base interpreter and lose installed packages.
    python_executable = Path(python_executable).absolute()
    if parent_iterations <= 0 or child_iterations <= 0:
        raise ValueError("parent_iterations and child_iterations must be positive")

    cells: list[ExperimentCell] = []
    for seed in tuple(int(value) for value in seeds):
        seed_root = run_root / f"seed{seed:03d}"
        parent_dir = seed_root / "neutral_parent"
        parent_checkpoint = parent_dir / "rvit_paper_luo2015_criterion_final.pt"
        parent_command = _common_training_args(
            project_root=project_root,
            python_executable=python_executable,
            output_dir=parent_dir,
            iterations=parent_iterations,
            seed=seed,
            device=device,
            feedback=feedback,
            memory_decay=memory_decay,
            noise=noise,
        )
        parent_command.extend([
            "--task", "luo2015_criterion",
            "--init-mode", "fresh",
            "--r-hit", "1.0",
            "--r-cr", "1.0",
            "--high-loc", "0",
            "--reward-scale", "1.0",
            "--theta-start", "65.0",
            "--curriculum",
            "--curr-floor", str(float(theta)),
        ])
        cells.append(ExperimentCell(
            role="neutral_parent",
            seed=seed,
            task="luo2015_criterion",
            condition_loc=None,
            output_dir=parent_dir,
            command=tuple(parent_command),
        ))

        for task, session_scale in (
            ("luo2015_sensitivity", 1.0 / 3.0),
            ("luo2015_criterion", 1.0 / 0.95),
        ):
            for condition_loc in (0, 3):
                session = task.removeprefix("luo2015_")
                output_dir = seed_root / f"{session}_loc{condition_loc}"
                command = _common_training_args(
                    project_root=project_root,
                    python_executable=python_executable,
                    output_dir=output_dir,
                    iterations=child_iterations,
                    seed=seed,
                    device=device,
                    feedback=feedback,
                    memory_decay=memory_decay,
                    noise=noise,
                )
                command.extend([
                    "--task", task,
                    "--init-mode", "warm_start",
                    "--checkpoint-path", str(parent_checkpoint),
                    "--high-loc", str(condition_loc),
                    "--reward-scale", str(session_scale),
                    "--theta-start", str(float(theta)),
                ])
                cells.append(ExperimentCell(
                    role="fixed_condition",
                    seed=seed,
                    task=task,
                    condition_loc=condition_loc,
                    output_dir=output_dir,
                    command=tuple(command),
                    parent_checkpoint=parent_checkpoint,
                ))
    return cells


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the paired episodic fixed-condition Luo--Maunsell optimization matrix."
    )
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    parser.add_argument("--parent-iters", type=int, default=20_000)
    parser.add_argument("--child-iters", type=int, default=20_000)
    parser.add_argument("--theta", type=float, default=18.0)
    parser.add_argument("--device", default="mps")
    parser.add_argument(
        "--feedback", choices=("affine_ew", "crossattn1"), default="affine_ew"
    )
    parser.add_argument("--memory-decay", type=float, default=1.0)
    parser.add_argument(
        "--noise", type=float, default=5.0,
        help="orientation-jitter standard deviation in degrees",
    )
    parser.add_argument("--parent-min-accuracy", type=float, default=0.75)
    parser.add_argument("--parent-min-valid-fraction", type=float, default=0.9)
    parser.add_argument("--parent-gate-trials", type=int, default=100,
                        help="held-out trials per change status and location")
    parser.add_argument("--parent-gate-seed", type=int, default=20260717)
    parser.add_argument("--parent-gate-batch-size", type=int, default=64)
    parser.add_argument(
        "--canary", action="store_true",
        help="exercise plumbing only; explicitly bypass the neutral-parent competence gate",
    )
    parser.add_argument("--execute", action="store_true")
    return parser


def _validate_args(args: argparse.Namespace) -> None:
    if not math.isfinite(args.theta) or args.theta <= 0:
        raise ValueError("--theta must be finite and positive")
    if not math.isfinite(args.memory_decay) or not 0.0 <= args.memory_decay <= 1.0:
        raise ValueError("--memory-decay must be finite and between 0 and 1")
    if not math.isfinite(args.noise) or args.noise < 0.0:
        raise ValueError("--noise must be finite and nonnegative")
    for flag, value in (
        ("--parent-min-accuracy", args.parent_min_accuracy),
        ("--parent-min-valid-fraction", args.parent_min_valid_fraction),
    ):
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"{flag} must be finite and between 0 and 1")
    for flag, value in (
        ("--parent-iters", args.parent_iters),
        ("--child-iters", args.child_iters),
        ("--parent-gate-trials", args.parent_gate_trials),
        ("--parent-gate-batch-size", args.parent_gate_batch_size),
    ):
        if value <= 0:
            raise ValueError(f"{flag} must be positive")
    if not args.seeds or len(set(args.seeds)) != len(args.seeds):
        raise ValueError("--seeds must contain unique values")


def _validate_torch_runtime() -> None:
    try:
        import torch  # noqa: F401
    except ImportError as exc:
        project_python = _REPO.parent / ".venv" / "bin" / "python"
        hint = (
            f" Use {project_python} to launch this matrix."
            if project_python.is_file()
            else " Activate a Python environment that provides Torch."
        )
        raise RuntimeError(
            f"Training requires Torch, but {sys.executable} cannot import it.{hint}"
        ) from exc


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _final_checkpoint(cell: ExperimentCell) -> Path:
    return cell.output_dir / f"rvit_paper_{cell.task}_final.pt"


def _cell_id(cell: ExperimentCell) -> str:
    return f"{cell.output_dir.parent.name}/{cell.output_dir.name}"


def _cell_record(cell: ExperimentCell) -> dict:
    return {
        "id": _cell_id(cell),
        "role": cell.role,
        "seed": cell.seed,
        "task": cell.task,
        "condition_loc": cell.condition_loc,
        "output_dir": str(cell.output_dir),
        "command": list(cell.command),
        "parent_checkpoint": str(cell.parent_checkpoint) if cell.parent_checkpoint else None,
        "status": "pending",
    }


def _write_manifest(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _checkpoint_iteration(path: Path) -> int:
    import torch

    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    return int(checkpoint["iter"])


def _checkpoint_initialization_parent_hash(path: Path) -> str:
    import torch

    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    contract = checkpoint.get("initialization_contract", {})
    if contract.get("mode") != "warm_start" or not contract.get("checkpoint_sha256"):
        raise RuntimeError(f"{path} has no embedded warm-start parent checkpoint lineage")
    return str(contract["checkpoint_sha256"])


def _command_arg(command: tuple[str, ...], flag: str) -> str:
    return command[command.index(flag) + 1]


def _validate_checkpoint_producers(
    checkpoint: dict,
    cell: ExperimentCell,
    fail,
) -> None:
    stored = checkpoint.get("producer_sha256", checkpoint.get("producer_hashes", {}))
    expected = {
        relative: _sha256(_REPO / relative)
        for relative in (
            "train_rl.py", "ppo.py", "model.py", "paper_encoder.py",
            "paper_heads.py", "conv_frontend.py", "envs/base.py",
            "envs/luo2015.py", "envs/tasks.py", "envs/__init__.py",
            "config/loader.py",
        )
    }
    expected["experiment_launcher"] = _sha256(
        Path(_command_arg(cell.command, "--experiment-launcher"))
    )
    for source, expected_hash in expected.items():
        if stored.get(source) != expected_hash:
            fail(f"producer hash mismatch for {source}")


def validate_parent_checkpoint_contract(
    checkpoint_path: Path,
    cell: ExperimentCell,
) -> dict:
    """Fail closed unless a parent proves neutral perceptual pretraining."""
    import torch

    from envs import make_env

    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)

    def fail(detail: str) -> None:
        raise RuntimeError(f"{_cell_id(cell)} checkpoint {detail}")

    if int(checkpoint.get("iter", -1)) != int(
        _command_arg(cell.command, "--schedule-final-iteration")
    ):
        fail("iteration does not match the planned parent budget")
    if checkpoint.get("task") != "luo2015_criterion":
        fail("task does not match neutral criterion pretraining")
    if checkpoint.get("initialization_contract", {}).get("mode") != "fresh":
        fail("initialization lineage is not a fresh neutral parent")
    if not math.isclose(
        float(checkpoint.get("ppo_config", {}).get("gamma", float("nan"))), 1.0
    ):
        fail("gamma must equal 1.0 for event-reward ratio fidelity")
    _validate_checkpoint_producers(checkpoint, cell, fail)

    args = checkpoint.get("training_args", {})
    expected_floor = float(_command_arg(cell.command, "--curr-floor"))
    expected_args = {
        "seed": cell.seed,
        "high_loc": 0,
        "reward_scale": 1.0,
        "theta_start": 65.0,
        "curr_floor": expected_floor,
        "curriculum": True,
        "T": 7,
        "r_hit": 1.0,
        "r_cr": 1.0,
    }
    for key, expected in expected_args.items():
        actual = args.get(key)
        if isinstance(expected, float):
            valid = isinstance(actual, (int, float)) and math.isclose(
                float(actual), expected
            )
        else:
            valid = actual == expected
        if not valid:
            if key in ("r_hit", "r_cr", "reward_scale"):
                fail("does not use the neutral reward objective")
            fail(f"training argument {key} does not match neutral pretraining")

    expected_env = make_env(
        cell.task,
        T=7,
        min_change_time=5,
        max_change_time=5,
        noise_multiplier=5.0,
        reward_scale=1.0,
        curriculum=True,
        theta=65.0,
        theta_floor=expected_floor,
        high_loc=0,
        r_hit=1.0,
        r_cr=1.0,
    )
    expected_config = expected_env.training_state_dict()["environment_config"]
    actual_config = checkpoint.get("environment_state", {}).get(
        "environment_config", {}
    )
    for key in (
        "session", "condition_loc", "reward_scale", "T", "value_cues",
        "min_change_time", "max_change_time", "first_test_onset",
        "first_test_end", "second_test_onset",
    ):
        if actual_config.get(key) != expected_config.get(key):
            fail(f"environment {key} does not match neutral pretraining")
    for location in (0, 3):
        actual_pair = actual_config.get("reward_table", {}).get(location)
        if actual_pair is None or not all(
            math.isclose(float(actual), 1.0) for actual in actual_pair
        ):
            fail("does not use the neutral reward objective")
    return checkpoint


def validate_child_checkpoint_contract(
    checkpoint_path: Path,
    cell: ExperimentCell,
    expected_parent_sha256: str,
) -> dict:
    """Fail closed unless a child independently proves the planned fixed protocol."""
    import torch

    from envs import make_env

    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)

    def fail(detail: str) -> None:
        raise RuntimeError(f"{_cell_id(cell)} checkpoint {detail}")

    expected_iteration = int(_command_arg(cell.command, "--schedule-final-iteration"))
    if int(checkpoint.get("iter", -1)) != expected_iteration:
        fail("iteration does not match the planned training budget")
    if checkpoint.get("task") != cell.task:
        fail("task does not match the planned condition")

    initialization = checkpoint.get("initialization_contract", {})
    if (
        initialization.get("mode") != "warm_start"
        or initialization.get("strict") is not True
    ):
        fail("does not contain a strict warm-start initialization contract")
    if initialization.get("checkpoint_sha256") != expected_parent_sha256:
        fail("parent checkpoint lineage does not match the immutable neutral parent")

    ppo_config = checkpoint.get("ppo_config", {})
    if not math.isclose(float(ppo_config.get("gamma", float("nan"))), 1.0):
        fail("gamma must equal 1.0 for event-reward ratio fidelity")
    _validate_checkpoint_producers(checkpoint, cell, fail)

    expected_scale = float(_command_arg(cell.command, "--reward-scale"))
    expected_theta = float(_command_arg(cell.command, "--theta-start"))
    training_args = checkpoint.get("training_args", {})
    if int(training_args.get("seed", -1)) != cell.seed:
        fail("seed does not match the planned paired replicate")
    if int(training_args.get("high_loc", -1)) != cell.condition_loc:
        fail("condition location does not match the planned counterphase")
    if not math.isclose(
        float(training_args.get("reward_scale", float("nan"))), expected_scale
    ):
        fail("reward scale does not match the planned objective")
    if not math.isclose(
        float(training_args.get("theta_start", float("nan"))), expected_theta
    ):
        fail("theta does not match the planned fixed difficulty")
    if training_args.get("curriculum") is not False:
        fail("curriculum must remain disabled in fixed-condition children")
    if int(training_args.get("T", -1)) != 7:
        fail("trial length does not match the seven-frame protocol")
    if training_args.get("expected_parent_sha256") != expected_parent_sha256:
        fail("launch arguments are not bound to the immutable neutral parent")

    expected_env = make_env(
        cell.task,
        T=7,
        min_change_time=5,
        max_change_time=5,
        noise_multiplier=5.0,
        reward_scale=expected_scale,
        curriculum=False,
        theta=expected_theta,
        high_loc=cell.condition_loc,
    )
    expected_config = expected_env.training_state_dict()["environment_config"]
    environment_state = checkpoint.get("environment_state", {})
    environment_config = environment_state.get("environment_config", {})
    if not math.isclose(
        float(environment_state.get("theta", float("nan"))), expected_theta
    ):
        fail("saved environment theta does not match the fixed difficulty")
    for key in (
        "session", "condition_loc", "reward_scale", "T", "value_cues",
        "min_change_time", "max_change_time", "first_test_onset",
        "first_test_end", "second_test_onset",
    ):
        if environment_config.get(key) != expected_config.get(key):
            fail(f"environment {key} does not match the planned protocol")
    actual_table = environment_config.get("reward_table", {})
    expected_table = expected_config["reward_table"]
    for location in (0, 3):
        actual_pair = actual_table.get(location)
        expected_pair = expected_table[location]
        if (
            actual_pair is None
            or len(actual_pair) != 2
            or not all(
                math.isclose(float(actual), float(expected))
                for actual, expected in zip(actual_pair, expected_pair)
            )
        ):
            fail(f"reward table at location {location} does not match the objective")
    return checkpoint


def _bind_child_lineage(
    record: dict,
    checkpoint: Path,
    expected_parent_hash: str,
    cell: ExperimentCell,
) -> None:
    validate_child_checkpoint_contract(checkpoint, cell, expected_parent_hash)
    embedded_parent_hash = _checkpoint_initialization_parent_hash(checkpoint)
    recorded_parent_hash = record.get("parent_checkpoint_sha256")
    if embedded_parent_hash != expected_parent_hash or (
        recorded_parent_hash is not None and recorded_parent_hash != embedded_parent_hash
    ):
        raise RuntimeError(
            f"parent checkpoint lineage mismatch for {record['id']}: "
            f"embedded={embedded_parent_hash}, expected={expected_parent_hash}, "
            f"recorded={recorded_parent_hash}"
        )
    record["parent_checkpoint_sha256"] = embedded_parent_hash


def evaluate_parent_gate_metrics(
    checkpoint_path: Path,
    *,
    target_theta: float,
    trials_per_status_per_location: int,
    eval_seed: int,
    batch_size: int,
) -> dict:
    import numpy as np

    from experiments.luo2015_episodic.analyze_matrix import (
        _press_times_batched,
        balanced_trial_bank,
    )
    from luo2015_analysis.luo2015_core import classify_trial, load_model

    model, _iteration = load_model(str(checkpoint_path))
    change_videos, no_change_videos, change_locs, no_change_locs = balanced_trial_bank(
        magnitude=target_theta,
        trials_per_location=trials_per_status_per_location,
        seed=eval_seed,
    )
    change_press = _press_times_batched(model, change_videos, batch_size)
    no_change_press = _press_times_batched(model, no_change_videos, batch_size)
    locations = {}
    for location in (0, 3):
        change_outcomes = np.asarray([
            classify_trial(1, press)
            for press in change_press[change_locs == location]
        ])
        no_change_outcomes = np.asarray([
            classify_trial(0, press)
            for press in no_change_press[no_change_locs == location]
        ])
        valid_change = np.isin(change_outcomes, ("hit", "miss"))
        valid_no_change = np.isin(
            no_change_outcomes, ("false_alarm", "correct_rejection")
        )
        locations[str(location)] = {
            "change_accuracy": float(
                (change_outcomes[valid_change] == "hit").mean()
            ) if valid_change.any() else 0.0,
            "no_change_accuracy": float(
                (no_change_outcomes[valid_no_change] == "correct_rejection").mean()
            ) if valid_no_change.any() else 0.0,
            "change_valid_fraction": float(valid_change.mean()),
            "no_change_valid_fraction": float(valid_no_change.mean()),
        }
    return {
        "theta": float(target_theta),
        "trials_per_status_per_location": int(trials_per_status_per_location),
        "evaluation_seed": int(eval_seed),
        "locations": locations,
    }


def validate_parent_gate(
    checkpoint_path: Path,
    *,
    target_theta: float,
    min_accuracy: float,
    min_valid_fraction: float,
    gate_metrics: dict | None = None,
    trials_per_status_per_location: int = 100,
    eval_seed: int = 20260717,
    batch_size: int = 64,
) -> dict:
    """Require balanced held-out competence at target theta before branching."""
    import torch

    if not math.isfinite(target_theta) or target_theta <= 0:
        raise ValueError("target theta must be finite and positive")
    for name, value in (
        ("min_accuracy", min_accuracy),
        ("min_valid_fraction", min_valid_fraction),
    ):
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be finite and between 0 and 1")
    if trials_per_status_per_location <= 0 or batch_size <= 0:
        raise ValueError("parent gate trial count and batch size must be positive")
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    theta = float(checkpoint.get("environment_state", {}).get("theta", float("inf")))
    if not math.isfinite(theta) or theta > float(target_theta) + 1e-9:
        raise RuntimeError(
            f"neutral parent did not reach target theta: {theta:g} > {float(target_theta):g}"
        )
    metrics = gate_metrics
    if metrics is None:
        metrics = evaluate_parent_gate_metrics(
            checkpoint_path,
            target_theta=target_theta,
            trials_per_status_per_location=trials_per_status_per_location,
            eval_seed=eval_seed,
            batch_size=batch_size,
        )
    if not math.isclose(float(metrics.get("theta", float("nan"))), target_theta):
        raise RuntimeError("neutral parent gate was not evaluated at target theta")
    if metrics.get("trials_per_status_per_location") != trials_per_status_per_location:
        raise RuntimeError(
            "neutral parent gate trial count does not match the preregistered contract"
        )
    for location in (0, 3):
        local = metrics.get("locations", {}).get(str(location), {})
        for label in ("change_accuracy", "no_change_accuracy"):
            value = float(local.get(label, float("nan")))
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise RuntimeError(f"location {location} {label} is not a valid probability")
            if value < min_accuracy:
                display = label.replace("_", " ").replace("no change", "no-change")
                raise RuntimeError(
                    f"location {location} {display} is below the hard gate: "
                    f"{value:.3f} < {min_accuracy:.3f}"
                )
        for label in ("change_valid_fraction", "no_change_valid_fraction"):
            value = float(local.get(label, float("nan")))
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise RuntimeError(f"location {location} {label} is not a valid probability")
            if value < min_valid_fraction:
                display = label.replace("_", " ").replace("no change", "no-change")
                raise RuntimeError(
                    f"location {location} {display} is below the engagement gate: "
                    f"{value:.3f} < {min_valid_fraction:.3f}"
                )
    return metrics


def _replace_flag(command: list[str], flag: str, value: str) -> None:
    if flag in command:
        command[command.index(flag) + 1] = value
    else:
        command.extend([flag, value])


def _resume_command(cell: ExperimentCell, target_iterations: int) -> tuple[str, ...]:
    latest = cell.output_dir / "rvit_plus_rl_latest.pt"
    if not latest.is_file():
        return cell.command
    completed_iteration = _checkpoint_iteration(latest)
    remaining = target_iterations - completed_iteration - 1
    if remaining <= 0:
        raise RuntimeError(
            f"{latest} reached iteration {completed_iteration} but no valid final checkpoint exists"
        )
    command = list(cell.command)
    _replace_flag(command, "--init-mode", "resume")
    _replace_flag(command, "--checkpoint-path", str(latest))
    _replace_flag(command, "--iters", str(remaining))
    return tuple(command)


def _new_manifest(args: argparse.Namespace, cells: list[ExperimentCell]) -> dict:
    return {
        "schema_version": 2,
        "design": "paired_episodic_fixed_condition_optimization",
        "claim_scope": "condition_specific_policy_optima_not_online_block_adaptation",
        "run_mode": "canary" if args.canary else "full",
        "protocol": {
            "neutral_parent": "equal hit and correct-rejection rewards with curriculum",
            "fork": "four agents per seed inherit the exact same neutral-parent weights",
            "fixed_children": "sensitivity/criterion crossed with counterphased locations 0/3",
            "visible_reward_cue": False,
            "cross_trial_recurrent_state_required": False,
            "theta": float(args.theta),
            "discount_factor": 1.0,
            "feedback": args.feedback,
            "memory_decay": float(args.memory_decay),
            "orientation_noise_degrees": float(args.noise),
            "parent_hard_gate": None if args.canary else {
                "theta_at_most": float(args.theta),
                "held_out_accuracy_at_each_location_and_status_at_least": float(
                    args.parent_min_accuracy
                ),
                "held_out_valid_fraction_at_each_location_and_status_at_least": float(
                    args.parent_min_valid_fraction
                ),
                "trials_per_status_per_location": int(args.parent_gate_trials),
                "evaluation_seed_base": int(args.parent_gate_seed),
            },
            "reward_normalization": {
                "sensitivity": 1.0 / 3.0,
                "criterion": 1.0 / 0.95,
            },
        },
        "seeds": list(args.seeds),
        "parent_iterations": int(args.parent_iters),
        "child_iterations": int(args.child_iters),
        "device": args.device,
        "cells": [_cell_record(cell) for cell in cells],
    }


def _verify_existing_contract(existing: dict, proposed: dict) -> None:
    keys = (
        "schema_version", "design", "claim_scope", "run_mode", "protocol", "seeds",
        "parent_iterations", "child_iterations", "device",
    )
    if any(existing.get(key) != proposed.get(key) for key in keys):
        raise RuntimeError("existing experiment manifest does not match the requested contract")
    existing_commands = {record["id"]: record["command"] for record in existing["cells"]}
    proposed_commands = {record["id"]: record["command"] for record in proposed["cells"]}
    if existing_commands != proposed_commands:
        raise RuntimeError("existing experiment commands do not match the requested contract")


def _record_parent_gate(record: dict, checkpoint: Path, args: argparse.Namespace) -> None:
    if args.canary:
        record["parent_gate"] = {"status": "bypassed_for_canary"}
        return
    result = validate_parent_gate(
        checkpoint,
        target_theta=args.theta,
        min_accuracy=args.parent_min_accuracy,
        min_valid_fraction=args.parent_min_valid_fraction,
        trials_per_status_per_location=args.parent_gate_trials,
        eval_seed=args.parent_gate_seed + int(record["seed"]),
        batch_size=args.parent_gate_batch_size,
    )
    record["parent_gate"] = {"status": "passed", **result}


def execute_cells(
    *,
    project_root: Path,
    run_root: Path,
    args: argparse.Namespace,
    cells: list[ExperimentCell],
    runner,
) -> None:
    manifest_path = run_root / "experiment_manifest.json"
    proposed = _new_manifest(args, cells)
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        _verify_existing_contract(manifest, proposed)
    else:
        manifest = proposed
        _write_manifest(manifest_path, manifest)

    records = {record["id"]: record for record in manifest["cells"]}
    parent_hashes: dict[int, str] = {}
    for cell in cells:
        record = records[_cell_id(cell)]
        target = args.parent_iters if cell.role == "neutral_parent" else args.child_iters
        final_checkpoint = _final_checkpoint(cell)
        if final_checkpoint.is_file() and _checkpoint_iteration(final_checkpoint) == target - 1:
            final_hash = _sha256(final_checkpoint)
            record.update(status="complete", final_checkpoint=str(final_checkpoint),
                          final_checkpoint_sha256=final_hash)
            if cell.role == "neutral_parent":
                validate_parent_checkpoint_contract(final_checkpoint, cell)
                parent_hashes[cell.seed] = final_hash
                _record_parent_gate(record, final_checkpoint, args)
            else:
                _bind_child_lineage(
                    record, final_checkpoint, parent_hashes[cell.seed], cell
                )
            _write_manifest(manifest_path, manifest)
            continue

        if cell.role == "fixed_condition":
            if not cell.parent_checkpoint or not cell.parent_checkpoint.is_file():
                raise RuntimeError(f"neutral parent is missing for {_cell_id(cell)}")
            parent_hashes.setdefault(cell.seed, _sha256(cell.parent_checkpoint))
            recorded_parent = record.get("parent_checkpoint_sha256")
            if (
                recorded_parent is not None
                and recorded_parent != parent_hashes[cell.seed]
            ):
                raise RuntimeError(
                    f"parent checkpoint lineage mismatch for {_cell_id(cell)}: "
                    f"recorded={recorded_parent}, expected={parent_hashes[cell.seed]}"
                )
            record.setdefault("parent_checkpoint_sha256", parent_hashes[cell.seed])

        cell.output_dir.mkdir(parents=True, exist_ok=True)
        command = list(_resume_command(cell, target))
        if cell.role == "fixed_condition":
            _replace_flag(
                command, "--expected-parent-sha256", parent_hashes[cell.seed]
            )
        command = tuple(command)
        record.update(status="running", effective_command=list(command))
        _write_manifest(manifest_path, manifest)
        runner(command, cwd=str(project_root), check=True)
        if not final_checkpoint.is_file():
            raise RuntimeError(f"training exited without {final_checkpoint}")
        final_iteration = _checkpoint_iteration(final_checkpoint)
        if final_iteration != target - 1:
            raise RuntimeError(
                f"{final_checkpoint} ended at iteration {final_iteration}; expected {target - 1}"
            )
        final_hash = _sha256(final_checkpoint)
        record.update(status="complete", final_checkpoint=str(final_checkpoint),
                      final_checkpoint_sha256=final_hash)
        if cell.role == "neutral_parent":
            validate_parent_checkpoint_contract(final_checkpoint, cell)
            parent_hashes[cell.seed] = final_hash
            _record_parent_gate(record, final_checkpoint, args)
        else:
            _bind_child_lineage(record, final_checkpoint, parent_hashes[cell.seed], cell)
        _write_manifest(manifest_path, manifest)


def main(argv: list[str] | None = None, *, runner=subprocess.run) -> int:
    args = build_arg_parser().parse_args(argv)
    _validate_args(args)
    if args.execute:
        _validate_torch_runtime()
    project_root = Path(__file__).resolve().parents[2]
    cells = build_cells(
        project_root=project_root,
        run_root=args.run_root,
        python_executable=Path(sys.executable),
        seeds=args.seeds,
        parent_iterations=args.parent_iters,
        child_iterations=args.child_iters,
        device=args.device,
        theta=args.theta,
        feedback=args.feedback,
        memory_decay=args.memory_decay,
        noise=args.noise,
    )
    print("paired episodic fixed-condition optimization")
    if args.execute:
        execute_cells(
            project_root=project_root,
            run_root=Path(args.run_root).resolve(),
            args=args,
            cells=cells,
            runner=runner,
        )
        print(f"[complete] {Path(args.run_root).resolve() / 'experiment_manifest.json'}")
        return 0
    for cell in cells:
        print(f"[dry-run] {cell.output_dir.name}: {shlex.join(cell.command)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
