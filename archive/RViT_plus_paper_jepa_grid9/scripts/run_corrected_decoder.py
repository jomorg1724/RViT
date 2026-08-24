#!/usr/bin/env python3
"""Publish or read-only audit a provenance-closed corrected VDA decoder run."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
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
VALIDATION_SOURCES = (
    "tests/test_vda_correctness.py",
    "tests/test_corrected_decoder_build.py",
    "tests/test_corrected_decoder_runner.py",
)
DEFAULT_OUTPUT_ROOT = ROOT / "vda_sweep/derived/2026-07-11_corrected"
DEFAULT_N = 900
DEFAULT_SEED = 20260711


def _source_paths() -> dict[str, Path]:
    return {
        "__runner__": Path(__file__).resolve(),
        "__builder__": ROOT / "scripts/build_corrected_decoder.py",
        "__producer__": ROOT / "vda_sweep/vda_fig_decode.py",
        **{
            relative: ROOT / relative
            for relative in (*PRODUCER_DEPENDENCIES, *VALIDATION_SOURCES)
        },
    }


def capture_executable_sources() -> dict[str, bytes]:
    """Freeze producer, dependency, runner, and validator bytes before imports."""
    return {identity: path.read_bytes() for identity, path in _source_paths().items()}


def assert_executable_sources_unchanged(startup_sources: dict[str, bytes]) -> None:
    paths = _source_paths()
    if set(startup_sources) != set(paths):
        raise RuntimeError("startup source inventory changed")
    for identity, path in paths.items():
        if path.read_bytes() != startup_sources[identity]:
            raise RuntimeError(f"source changed after startup capture: {path}")


def sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _regular_identity(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise FileNotFoundError(f"path is not a regular file: {path}")
    metadata = path.stat()
    return {
        "path_absolute": str(path.resolve()),
        "sha256": sha256(path),
        "bytes": metadata.st_size,
        "device": metadata.st_dev,
        "inode": metadata.st_ino,
        "nlink": metadata.st_nlink,
    }


def _legacy_identity() -> dict[str, object]:
    return _regular_identity(ROOT / "vda_sweep/figs/decode.npz")


def _load_modules(startup_sources: dict[str, bytes]):
    """Import validation and scientific modules only after byte capture."""
    sys.dont_write_bytecode = True
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    builder = importlib.import_module("scripts.build_corrected_decoder")
    if tuple(builder.PRODUCER_DEPENDENCIES) != PRODUCER_DEPENDENCIES:
        raise RuntimeError("runner and builder dependency closures disagree")
    decoder = importlib.import_module("vda_sweep.vda_fig_decode")
    contracts = (
        (tuple(decoder.DECODER_TASKS), tuple(builder.DECODER_TASKS), "tasks"),
        (tuple(decoder.FEEDBACKS), tuple(builder.FEEDBACKS), "feedbacks"),
        (
            tuple(decoder.DECODED_VARIABLES),
            tuple(builder.DECODED_VARIABLES),
            "decoded variables",
        ),
    )
    for actual, expected, label in contracts:
        if actual != expected:
            raise RuntimeError(f"producer and builder disagree about {label}")
    active = {task: tuple(values) for task, values in decoder.ACTIVE_LOCATIONS.items()}
    if active != builder.ACTIVE_LOCATIONS:
        raise RuntimeError("producer and builder disagree about active locations")
    assert_executable_sources_unchanged(startup_sources)
    return builder, decoder


def _snapshot_path(root: Path, identity: str) -> Path:
    if identity == "__runner__":
        return root / "provenance/run_corrected_decoder.py"
    if identity == "__builder__":
        return root / "provenance/build_corrected_decoder.py"
    if identity == "__producer__":
        return root / "provenance/vda_fig_decode.py"
    category = "validation" if identity in VALIDATION_SOURCES else "dependencies"
    return root / "provenance" / category / identity


def _write_source_snapshots(
    root: Path, startup_sources: dict[str, bytes]
) -> tuple[list[dict[str, object]], set[Path]]:
    source_paths = _source_paths()
    records: list[dict[str, object]] = []
    snapshots: set[Path] = set()
    for identity, content in startup_sources.items():
        snapshot = _snapshot_path(root, identity)
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(content)
        digest = hashlib.sha256(content).hexdigest()
        if sha256(snapshot) != digest:
            raise RuntimeError(f"source snapshot write changed bytes: {snapshot}")
        records.append(
            {
                "identity": identity,
                "role": "validation" if identity in VALIDATION_SOURCES else "execution",
                "source_path_absolute": str(source_paths[identity]),
                "snapshot_path": str(snapshot.relative_to(root)),
                "sha256": digest,
                "bytes": len(content),
            }
        )
        snapshots.add(snapshot)
    return sorted(records, key=lambda record: str(record["identity"])), snapshots


def _runtime_versions() -> dict[str, str]:
    import numpy
    import sklearn
    import torch

    core = importlib.import_module("vda_sweep.vda_core")
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": numpy.__version__,
        "scikit_learn": sklearn.__version__,
        "torch": torch.__version__,
        "device": str(core.DEVICE),
    }


def _without_checkpoint_records(summary: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in summary.items() if key != "checkpoint_records"}


def _tree_identity(builder: Any, root: Path) -> tuple[tuple[str, int, str], ...]:
    return tuple(
        sorted(
            (str(path.relative_to(root)), path.stat().st_size, sha256(path))
            for path in builder.regular_run_files(root)
        )
    )


def build_run(root: str | Path, *, n: int, seed: int) -> Path:
    """Compute a fresh run and publish MANIFEST.json only after exact validation."""
    if n < 128:
        raise ValueError("n must be at least 128 for registered class-support minima")
    startup_sources = capture_executable_sources()
    legacy_at_start = _legacy_identity()
    builder, decoder = _load_modules(startup_sources)
    root = Path(os.path.abspath(root))
    manifest, temporary = builder.prepare_fresh_run(root)
    archive = root / "data/decode.npz"
    archive.parent.mkdir(parents=True)

    produced = Path(
        decoder.main(["--out", str(archive), "--n", str(n), "--seed", str(seed)])
    )
    if produced.resolve() != archive.resolve():
        raise RuntimeError(f"producer returned an unexpected output path: {produced}")
    summary = builder.validate_decode_archive(
        archive, expected_n=n, expected_seed=seed
    )
    checkpoints = builder.validate_checkpoint_records(
        list(summary["checkpoint_records"])
    )
    assert_executable_sources_unchanged(startup_sources)
    if _legacy_identity() != legacy_at_start:
        raise RuntimeError("legacy decoder artifact changed during corrected build")
    archive_identity = _regular_identity(archive)
    if (
        archive_identity["device"],
        archive_identity["inode"],
    ) == (legacy_at_start["device"], legacy_at_start["inode"]):
        raise RuntimeError("corrected archive aliases the preserved legacy artifact")

    source_records, snapshot_paths = _write_source_snapshots(root, startup_sources)
    document = {
        "schema_version": 1,
        "artifact_class": "corrected checkpoint-recomputed VDA decoder",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": [
            sys.executable,
            str(Path(__file__).resolve()),
            "--output-root",
            str(root),
            "--n",
            str(n),
            "--seed",
            str(seed),
        ],
        "artifact": {
            "path": str(archive.relative_to(root)),
            **{key: value for key, value in archive_identity.items() if key != "path_absolute"},
        },
        "decoder_summary": _without_checkpoint_records(summary),
        "checkpoints": checkpoints,
        "sources": source_records,
        "runtime_versions": _runtime_versions(),
        "legacy_artifact_preserved": legacy_at_start,
        "validation_gate": {
            "command": (
                "../.venv/bin/python -m pytest -q tests/test_vda_correctness.py "
                "tests/test_corrected_decoder_build.py tests/test_corrected_decoder_runner.py"
            ),
            "result_recorded_after_build": None,
        },
        "claim_boundary": (
            "Scores are single-checkpoint descriptive cross-validated decoding estimates. "
            "They are not training-seed uncertainty, causal mechanism evidence, or capacity estimates."
        ),
    }
    temporary.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    builder.publish_manifest_with_inventory(
        root, temporary, manifest, {archive, *snapshot_paths}
    )
    audit_existing_run(root, expected_n=n, expected_seed=seed)
    return manifest


def audit_existing_run(root: str | Path, *, expected_n: int, expected_seed: int) -> Path:
    """Read-only exact-tree audit of a completed corrected-decoding run."""
    startup_sources = capture_executable_sources()
    builder, _decoder = _load_modules(startup_sources)
    root = Path(os.path.abspath(root))
    initial_identity = _tree_identity(builder, root)
    manifest = root / "MANIFEST.json"
    document = json.loads(manifest.read_text())
    if document.get("schema_version") != 1:
        raise ValueError("unsupported corrected decoder manifest schema")

    artifact_record = document["artifact"]
    archive = root / str(artifact_record["path"])
    archive_identity = _regular_identity(archive)
    for key in ("sha256", "bytes", "device", "inode", "nlink"):
        if archive_identity[key] != artifact_record.get(key):
            raise RuntimeError(f"corrected archive {key} changed after publication")
    summary = builder.validate_decode_archive(
        archive, expected_n=expected_n, expected_seed=expected_seed
    )
    if _without_checkpoint_records(summary) != document.get("decoder_summary"):
        raise RuntimeError("manifest summary does not match archive semantics")
    checkpoints = builder.validate_checkpoint_records(
        list(summary["checkpoint_records"])
    )
    if checkpoints != document.get("checkpoints"):
        raise RuntimeError("checkpoint identities do not match completed manifest")
    if _legacy_identity() != document.get("legacy_artifact_preserved"):
        raise RuntimeError("legacy decoder identity changed after publication")

    source_paths = _source_paths()
    source_records = document.get("sources", [])
    if not isinstance(source_records, list):
        raise ValueError("manifest sources must be a list")
    identities = {str(record.get("identity")) for record in source_records}
    if identities != set(source_paths) or len(source_records) != len(source_paths):
        raise RuntimeError("manifest source closure is incomplete or duplicated")
    expected_files = {archive, manifest}
    for record in source_records:
        identity = str(record["identity"])
        source = source_paths[identity]
        if sha256(source) != record.get("sha256"):
            raise RuntimeError(f"current source does not match manifest: {identity}")
        snapshot = root / str(record["snapshot_path"])
        if sha256(snapshot) != record.get("sha256"):
            raise RuntimeError(f"source snapshot does not match manifest: {snapshot}")
        expected_files.add(snapshot)
    builder._require_exact_file_inventory(root, expected_files)
    assert_executable_sources_unchanged(startup_sources)
    if _tree_identity(builder, root) != initial_identity:
        raise RuntimeError("completed run tree changed during read-only audit")
    return manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--n", type=int, default=DEFAULT_N)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--reuse-validated-run",
        action="store_true",
        help="Read-only audit of a completed run; no byte is rewritten.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.reuse_validated_run:
        manifest = audit_existing_run(
            args.output_root, expected_n=args.n, expected_seed=args.seed
        )
        print(f"[validated reuse] {manifest}", flush=True)
        return 0
    manifest = build_run(args.output_root, n=args.n, seed=args.seed)
    print(f"[published] {manifest}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
