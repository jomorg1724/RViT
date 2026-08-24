#!/usr/bin/env python3
"""Fail-closed static preflight for the VDA fixed-9 canary v1 launcher."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from datetime import datetime, timezone


EXPECTED = {
    "task": "vda_fixed9",
    "set_size": 9,
    "grid": [4, 4],
    "tokens": 16,
    "image_size": 100,
    "seed": 0,
    "iterations": 20000,
    "terminal_iteration": 19999,
    "feedback": "crossattn1",
    "cell": "xlstm",
    "d_mem": 128,
    "memory_decay": 1.0,
    "memory_noise_std": 0.0,
}

REQUIRED_LAUNCH_FRAGMENTS = (
    "--task vda_fixed9", "--T 7", "--frame-repeat 1",
    "--patch-grid-rows 4", "--patch-grid-cols 4", "--cell xlstm",
    "--feedback crossattn1", "--d-mem 128", "--memory-decay 1.0",
    "--memory-noise-std 0.0", "--conv-frontend", "--curriculum",
    "--init-mode fresh", "--start-iteration 0", "--iters 20000",
    "--schedule-final-iteration 19999", "--episodes-per-iter 8",
    "--save-every 50", "--log-every 1", "--seed 0", "--device cuda",
    "--config \"$CONFIG\"", "--experiment-launcher \"$LAUNCHER\"",
)

FORBIDDEN_LAUNCH_FRAGMENTS = (
    "--checkpoint-path", "--expected-parent-sha256",
    "--allow-schedule-overrun-resume", "--two-lstm", "--jepa-same-time",
)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"PREFLIGHT_FAIL: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=pathlib.Path, required=True)
    parser.add_argument("--config", type=pathlib.Path, required=True)
    parser.add_argument("--launcher", type=pathlib.Path, required=True)
    parser.add_argument("--run-dir", type=pathlib.Path)
    parser.add_argument("--emit-json", action="store_true")
    args = parser.parse_args()

    root = args.project_root.resolve()
    config_path = args.config.resolve()
    launcher_path = args.launcher.resolve()
    for path in (root / "train_rl.py", config_path, launcher_path):
        if not path.is_file():
            fail(f"missing required file: {path}")

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    contract = raw.get("contract", {})
    for key, expected in (
        ("schema_version", 1), ("task", EXPECTED["task"]),
        ("set_size", EXPECTED["set_size"]), ("stimulus_grid", EXPECTED["grid"]),
        ("patch_memory_grid", EXPECTED["grid"]), ("tokens", EXPECTED["tokens"]),
        ("image_size", EXPECTED["image_size"]), ("seed", EXPECTED["seed"]),
        ("iterations", EXPECTED["iterations"]),
        ("terminal_iteration", EXPECTED["terminal_iteration"]),
    ):
        if contract.get(key) != expected:
            fail(f"config contract {key!r}: expected {expected!r}, got {contract.get(key)!r}")

    launcher_text = launcher_path.read_text(encoding="utf-8")
    normalized_launcher = re.sub(r"\\\s*\n\s*", " ", launcher_text)
    for fragment in REQUIRED_LAUNCH_FRAGMENTS:
        if fragment not in normalized_launcher:
            fail(f"launcher missing exact fragment: {fragment}")
    for fragment in FORBIDDEN_LAUNCH_FRAGMENTS:
        if fragment in normalized_launcher:
            fail(f"launcher contains forbidden resume/ablation fragment: {fragment}")
    if "${SEED:-" in launcher_text or "${ITERS:-" in launcher_text:
        fail("scientific seed/iteration values must not be environment-overridable")

    sys.path.insert(0, str(root))
    from envs import make_env, task_grid  # pylint: disable=import-outside-toplevel
    from train_rl import _producer_hashes, resolve_patch_grid  # pylint: disable=import-outside-toplevel

    if list(task_grid(EXPECTED["task"])) != EXPECTED["grid"]:
        fail("task registry is not the fixed 4x4 geometry")
    if list(resolve_patch_grid(EXPECTED["task"], 4, 4)) != EXPECTED["grid"]:
        fail("resolved patch/memory grid is not 4x4")

    env = make_env(
        EXPECTED["task"], T=7, frame_repeat=1, min_change_time=5,
        max_change_time=5, noise_multiplier=5.0, curriculum=True,
        theta=65.0, curr_window=1000, curr_threshold=0.85,
        curr_step=3.0, theta_floor=8.0,
    )
    if (env.grid_rows, env.grid_cols, env.n_stim, env.S, env.T, env.set_size) != (4, 4, 16, 100, 7, 9):
        fail("constructed environment geometry/timeline/set size is wrong")
    if tuple(env.observation_space.shape) != (100, 100, 3):
        fail("observation shape is not 100x100x3")
    for _ in range(64):
        observation = env.reset()
        if observation.shape != (100, 100, 3) or len(env.active) != 9:
            fail("reset did not realize exactly nine active locations")
        if len(set(env.active)) != 9 or not set(env.active).issubset(range(16)):
            fail("active-location sample is invalid")
        if env.cue_index not in env.active:
            fail("cue is not on an active item")
        if env.change_true and env.change_index not in env.active:
            fail("realized change is not on an active item")
        if env.change_true and env.change_index != env.cue_index and env.valid:
            fail("invalid target was mislabeled valid")

    producer_hashes = _producer_hashes(str(config_path), str(launcher_path))
    required_hash_keys = {
        "train_rl.py", "ppo.py", "model.py", "paper_encoder.py", "paper_heads.py",
        "conv_frontend.py", "envs/base.py", "envs/tasks.py", "envs/__init__.py",
        "config/loader.py", "resolved_config", "experiment_launcher",
    }
    if not required_hash_keys.issubset(producer_hashes):
        fail(f"producer hash set is incomplete: {sorted(required_hash_keys - producer_hashes.keys())}")
    if producer_hashes["resolved_config"] != sha256(config_path):
        fail("resolved config hash mismatch")
    if producer_hashes["experiment_launcher"] != sha256(launcher_path):
        fail("launcher hash mismatch")

    result = {
        "schema_version": 1,
        "status": "preflight_passed",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "contract": EXPECTED,
        "project_root": str(root),
        "config": str(config_path),
        "launcher": str(launcher_path),
        "run_dir": str(args.run_dir) if args.run_dir else None,
        "config_sha256": sha256(config_path),
        "launcher_sha256": sha256(launcher_path),
        "producer_sha256": producer_hashes,
        "evidence_boundary": contract.get("evidence_boundary"),
    }
    if args.emit_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            "PREFLIGHT_PASS|task=vda_fixed9|grid=4x4|active=9|tokens=16|"
            "feedback=crossattn1|d_mem=128|decay=1|seed=0|iters=20000|fresh"
        )


if __name__ == "__main__":
    main()
