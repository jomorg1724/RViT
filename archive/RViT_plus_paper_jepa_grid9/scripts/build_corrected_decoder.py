#!/usr/bin/env python3
"""Build and validate a provenance-closed corrected VDA decoding archive."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DECODER_TASKS = ("vda1", "vda2", "vda4", "vda9")
FEEDBACKS = ("crossattn1", "affine_ew")
DECODED_VARIABLES = ("colour", "validity", "change", "chg_loc")
SAMPLE_LABELS = ("colour", "validity", "change", "chg_loc", "cued_change")
ACTIVE_LOCATIONS = {
    "vda1": (0,),
    "vda2": (0, 3),
    "vda4": (0, 1, 2, 3),
    "vda9": tuple(range(9)),
}
CV_FOLDS = 4
TIMESTEPS = 7
PRODUCER_DEPENDENCIES = (
    "vda_sweep/vda_core.py",
    "model.py",
    "conv_frontend.py",
    "vae_frontend.py",
    "paper_encoder.py",
    "paper_heads.py",
    "envs/__init__.py",
    "envs/base.py",
    "envs/tasks.py",
    "envs/luo2015.py",
)


def _source_paths() -> dict[str, Path]:
    return {
        "__builder__": Path(__file__).resolve(),
        "__producer__": ROOT / "vda_sweep/vda_fig_decode.py",
        **{relative: ROOT / relative for relative in PRODUCER_DEPENDENCIES},
    }


def capture_executable_sources() -> dict[str, bytes]:
    """Freeze every local executable source before scientific imports."""
    return {identity: path.read_bytes() for identity, path in _source_paths().items()}


def assert_executable_sources_unchanged(startup_sources: dict[str, bytes]) -> None:
    paths = _source_paths()
    if set(startup_sources) != set(paths):
        raise RuntimeError("startup executable source inventory changed")
    for identity, path in paths.items():
        if path.read_bytes() != startup_sources[identity]:
            raise RuntimeError(f"executable source changed after startup capture: {path}")


def sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_checkpoint_records(
    records: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Rehash the exact eight selected checkpoints after model execution."""
    expected = {(task, feedback) for task in DECODER_TASKS for feedback in FEEDBACKS}
    actual = {(str(record.get("task")), str(record.get("feedback"))) for record in records}
    if actual != expected or len(records) != len(expected):
        raise ValueError("checkpoint record scope is incomplete or duplicated")
    normalized: list[dict[str, object]] = []
    paths: set[Path] = set()
    inodes: set[tuple[int, int]] = set()
    digests: set[str] = set()
    for record in records:
        path = Path(str(record.get("checkpoint_path_absolute")))
        if path.is_symlink() or not path.is_file():
            raise FileNotFoundError(f"checkpoint is not a regular file: {path}")
        path = path.resolve()
        metadata = path.stat()
        digest = sha256(path)
        if digest != record.get("checkpoint_sha256"):
            raise RuntimeError(f"checkpoint changed during decoding: {path}")
        if record.get("loaded_iteration") != 19999:
            raise ValueError(f"checkpoint loaded_iteration is not 19999: {path}")
        inode = (metadata.st_dev, metadata.st_ino)
        if path in paths or inode in inodes or digest in digests:
            raise RuntimeError(f"checkpoint identities are not distinct: {path}")
        paths.add(path)
        inodes.add(inode)
        digests.add(digest)
        normalized.append(
            {
                **record,
                "checkpoint_path_absolute": str(path),
                "checkpoint_bytes": metadata.st_size,
                "checkpoint_device": metadata.st_dev,
                "checkpoint_inode": metadata.st_ino,
                "checkpoint_nlink": metadata.st_nlink,
            }
        )
    return sorted(normalized, key=lambda item: (str(item["task"]), str(item["feedback"])))


def regular_run_files(root: str | Path) -> set[Path]:
    """Inventory lexical regular files; reject links, specials, and inode aliases."""
    root = Path(os.path.abspath(root))
    if root.is_symlink() or not root.is_dir():
        raise FileNotFoundError(f"run root is not a regular directory: {root}")
    files: set[Path] = set()
    inode_owner: dict[tuple[int, int], Path] = {}
    for path in root.rglob("*"):
        metadata = path.lstat()
        if stat.S_ISDIR(metadata.st_mode):
            continue
        if not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(f"run tree contains a symlink or special entry: {path}")
        identity = (metadata.st_dev, metadata.st_ino)
        if identity in inode_owner:
            raise RuntimeError(
                f"run tree contains a hard-link alias: {inode_owner[identity]} and {path}"
            )
        inode_owner[identity] = path
        files.add(path)
    return files


def prepare_fresh_run(root: str | Path) -> tuple[Path, Path]:
    """Create a unique output root without dereferencing its lexical boundary."""
    root = Path(os.path.abspath(root))
    if os.path.lexists(root):
        raise FileExistsError(
            f"output root already exists: {root}; choose a fresh versioned root"
        )
    root.mkdir(parents=True)
    return root / "MANIFEST.json", root / ".MANIFEST.json.tmp"


def _require_exact_file_inventory(root: Path, expected_files: set[Path]) -> None:
    root = Path(os.path.abspath(root))
    expected = {Path(os.path.abspath(path)) for path in expected_files}
    if any(root not in path.parents for path in expected):
        raise RuntimeError("prospective run file escapes output root")
    actual = regular_run_files(root)
    if actual != expected:
        raise RuntimeError(
            "prospective run file inventory mismatch; "
            f"missing={sorted(map(str, expected - actual))}, "
            f"unmanifested={sorted(map(str, actual - expected))}"
        )


def publish_manifest_with_inventory(
    root: Path,
    temporary: Path,
    manifest: Path,
    expected_without_manifest: set[Path],
) -> None:
    """Atomically admit a manifest only after exact lexical-tree validation."""
    _require_exact_file_inventory(root, expected_without_manifest | {temporary})
    temporary.replace(manifest)
    try:
        _require_exact_file_inventory(root, expected_without_manifest | {manifest})
    except Exception:
        manifest.unlink(missing_ok=True)
        raise


def expected_archive_keys() -> set[str]:
    keys: set[str] = set()
    for task in DECODER_TASKS:
        keys.add(f"{task}_sample_config_json")
        keys.add(f"{task}_sample_change_index")
        keys.update(f"{task}_sample_label_{name}" for name in SAMPLE_LABELS)
        for feedback in FEEDBACKS:
            keys.add(f"{task}_{feedback}_provenance_json")
            keys.update(
                f"{task}_{feedback}_{variable}" for variable in DECODED_VARIABLES
            )
    return keys


def _json_scalar(data: np.lib.npyio.NpzFile, key: str) -> dict[str, object]:
    value = np.asarray(data[key])
    if value.shape != ():
        raise ValueError(f"{key} must be a scalar JSON string")
    parsed = json.loads(str(value))
    if not isinstance(parsed, dict):
        raise ValueError(f"{key} must decode to an object")
    return parsed


def _class_counts(values: np.ndarray) -> dict[str, int]:
    labels, counts = np.unique(values, return_counts=True)
    return {str(int(label)): int(count) for label, count in zip(labels, counts)}


def validate_decode_archive(
    path: str | Path, *, expected_n: int, expected_seed: int
) -> dict[str, object]:
    """Fail closed unless a decoder NPZ has the complete corrected schema."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    expected = expected_archive_keys()
    with np.load(path, allow_pickle=False) as data:
        actual = set(data.files)
        if actual != expected:
            raise ValueError(
                "decoder archive exact key inventory mismatch; "
                f"missing={sorted(expected - actual)}, unmanifested={sorted(actual - expected)}"
            )
        location_counts: dict[str, dict[str, int]] = {}
        provenance_records: list[dict[str, object]] = []
        for task in DECODER_TASKS:
            config = _json_scalar(data, f"{task}_sample_config_json")
            if config.get("task") != task:
                raise ValueError(f"{task} sample config task mismatch")
            if config.get("n") != expected_n or config.get("seed") != expected_seed:
                raise ValueError(f"{task} sample config n/seed mismatch")
            if config.get("cv_folds") != CV_FOLDS:
                raise ValueError(f"{task} sample config cv_folds mismatch")
            if tuple(config.get("active_locations", ())) != ACTIVE_LOCATIONS[task]:
                raise ValueError(f"{task} active location semantics mismatch")
            location_defined = bool(config.get("location_decode_defined"))
            if location_defined != (task != "vda1"):
                raise ValueError(f"{task} location-defined semantic mismatch")

            labels: dict[str, np.ndarray] = {}
            for name in SAMPLE_LABELS:
                values = np.asarray(data[f"{task}_sample_label_{name}"])
                if values.shape != (expected_n,) or values.dtype.kind not in "iu":
                    raise ValueError(f"{task}/{name} labels must be integer shape ({expected_n},)")
                labels[name] = values
            change_index = np.asarray(data[f"{task}_sample_change_index"])
            if change_index.shape != (expected_n,) or change_index.dtype.kind not in "iu":
                raise ValueError(f"{task} change_index must be integer shape ({expected_n},)")
            if not np.array_equal(change_index, np.where(labels["change"] == 1, labels["chg_loc"] - 1, -1)):
                raise ValueError(f"{task} change_index and chg_loc labels disagree")
            counts = _class_counts(labels["chg_loc"])
            location_counts[task] = counts
            if task != "vda1" and min(counts.values()) < CV_FOLDS:
                raise ValueError(f"{task} location classes do not support cv={CV_FOLDS}: {counts}")

            for feedback in FEEDBACKS:
                for variable in DECODED_VARIABLES:
                    values = np.asarray(data[f"{task}_{feedback}_{variable}"], dtype=float)
                    if values.shape != (TIMESTEPS,):
                        raise ValueError(f"{task}/{feedback}/{variable} must have seven timesteps")
                    if task == "vda1" and variable == "chg_loc":
                        if not np.isnan(values).all():
                            raise ValueError("vda1 location decode must be explicitly undefined")
                    elif not np.isfinite(values).all() or np.any((values < 0) | (values > 1)):
                        raise ValueError(f"{task}/{feedback}/{variable} scores must be finite in [0,1]")
                provenance = _json_scalar(data, f"{task}_{feedback}_provenance_json")
                required = {
                    "task": task,
                    "feedback": feedback,
                    "n": expected_n,
                    "seed": expected_seed,
                    "d_mem": 128,
                }
                if any(provenance.get(key) != value for key, value in required.items()):
                    raise ValueError(f"{task}/{feedback} provenance identity mismatch")
                if provenance.get("replay_config") != config:
                    raise ValueError(f"{task}/{feedback} replay config mismatch")
                digest = provenance.get("checkpoint_sha256")
                if not isinstance(digest, str) or len(digest) != 64:
                    raise ValueError(f"{task}/{feedback} checkpoint digest is invalid")
                provenance_records.append(provenance)

    return {
        "key_count": len(expected),
        "tasks": list(DECODER_TASKS),
        "feedbacks": list(FEEDBACKS),
        "decoded_variables": list(DECODED_VARIABLES),
        "timesteps": TIMESTEPS,
        "n": int(expected_n),
        "seed": int(expected_seed),
        "location_class_counts": location_counts,
        "checkpoint_records": provenance_records,
    }
