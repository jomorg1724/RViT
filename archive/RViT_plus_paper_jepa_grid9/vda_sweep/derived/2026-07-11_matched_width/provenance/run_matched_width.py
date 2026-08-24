#!/usr/bin/env python3
"""Build, resume, finalize, or audit the matched-width VDA battery."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "vda_sweep/derived/2026-07-11_matched_width"
CLAIM_BOUNDARY = (
    "Width is an architectural recurrent-state intervention. Results are checkpoint-specific "
    "associations, not replicated causal width effects or human capacity estimates."
)
VALIDATION_GATE = {
    "command": (
        "../.venv/bin/python -m pytest -q tests/test_matched_width.py "
        "tests/test_matched_width_compute.py tests/test_matched_width_producer.py "
        "tests/test_matched_width_runner.py"
    ),
    "result_recorded_after_build": None,
}
PRODUCER_DEPENDENCIES = (
    "vda_sweep/vda_core.py",
    "vda_sweep/vda_fig_decode.py",
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
    "tests/test_matched_width.py",
    "tests/test_matched_width_compute.py",
    "tests/test_matched_width_producer.py",
    "tests/test_matched_width_runner.py",
)
MATCHED_SOURCES = (
    "vda_sweep/matched_width.py",
    "vda_sweep/matched_width_compute.py",
    "vda_sweep/matched_width_producer.py",
)
EVIDENCE_SOURCES = {
    "__metrics_inventory__": (
        ROOT.parent / "reports/research_state/2026-07-11_battery_metrics_inventory.csv"
    )
}


def _source_paths() -> dict[str, Path]:
    return {
        "__runner__": Path(__file__).resolve(),
        **EVIDENCE_SOURCES,
        **{
            relative: ROOT / relative
            for relative in (*MATCHED_SOURCES, *PRODUCER_DEPENDENCIES, *VALIDATION_SOURCES)
        },
    }


def capture_executable_sources() -> dict[str, bytes]:
    return {identity: path.read_bytes() for identity, path in _source_paths().items()}


def assert_executable_sources_unchanged(startup_sources: dict[str, bytes]) -> None:
    paths = _source_paths()
    if set(startup_sources) != set(paths):
        raise RuntimeError("matched-width startup source inventory changed")
    for identity, path in paths.items():
        if path.read_bytes() != startup_sources[identity]:
            raise RuntimeError(f"matched-width executable source changed: {path}")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256(path: str | Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def source_hashes(startup_sources: dict[str, bytes]) -> dict[str, str]:
    return {identity: sha256_bytes(content) for identity, content in startup_sources.items()}


def validate_competence_evidence(startup_sources: dict[str, bytes], matched: Any) -> None:
    rows = list(
        csv.DictReader(
            io.StringIO(startup_sources["__metrics_inventory__"].decode("utf-8-sig"))
        )
    )
    for flag in matched.COMPETENCE_FLAGS:
        line_number = int(flag["evidence_row"])
        row = rows[line_number - 2]
        expected = {
            "task": str(flag["task"]),
            "feedback": str(flag["feedback"]),
            "d_mem": str(flag["width"]),
            "last_correct": f"{float(flag['last_correct']):.6f}",
            "late50_mean_correct": f"{float(flag['late50_mean_correct']):.6f}",
            "best_correct": f"{float(flag['best_correct']):.6f}",
            "last_theta": f"{float(flag['last_theta']):.6f}",
        }
        if any(row.get(field) != value for field, value in expected.items()):
            raise RuntimeError(f"competence evidence mismatch at CSV line {line_number}")


def _load_modules(startup_sources: dict[str, bytes]):
    sys.dont_write_bytecode = True
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    matched = importlib.import_module("vda_sweep.matched_width")
    producer = importlib.import_module("vda_sweep.matched_width_producer")
    assert_executable_sources_unchanged(startup_sources)
    return matched, producer


def shard_name(spec: object) -> str:
    return f"{spec.task}_{spec.feedback}_d{spec.width}.npz"


def expected_shard_names(matched: Any) -> set[str]:
    return {shard_name(spec) for spec in matched.admissible_specs()}


def regular_run_files(root: str | Path) -> set[Path]:
    root = Path(os.path.abspath(root))
    if root.is_symlink() or not root.is_dir():
        raise FileNotFoundError(f"run root is not a regular directory: {root}")
    files: set[Path] = set()
    inodes: dict[tuple[int, int], Path] = {}
    for path in root.rglob("*"):
        metadata = path.lstat()
        if stat.S_ISDIR(metadata.st_mode):
            continue
        if not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(f"run tree contains a symlink or special entry: {path}")
        identity = (metadata.st_dev, metadata.st_ino)
        if identity in inodes:
            raise RuntimeError(f"run tree contains a hard-link alias: {inodes[identity]} and {path}")
        inodes[identity] = path
        files.add(path)
    return files


def require_exact_inventory(root: Path, expected: set[Path]) -> None:
    root = Path(os.path.abspath(root))
    normalized = {Path(os.path.abspath(path)) for path in expected}
    if any(root not in path.parents for path in normalized):
        raise RuntimeError("prospective matched-width file escapes output root")
    actual = regular_run_files(root)
    if actual != normalized:
        raise RuntimeError(
            "matched-width run inventory mismatch; "
            f"missing={sorted(map(str, normalized - actual))}, "
            f"unmanifested={sorted(map(str, actual - normalized))}"
        )


def remove_known_finder_metadata(root: Path) -> list[str]:
    removed: list[str] = []
    for path in root.rglob("Icon\r"):
        metadata = path.lstat()
        if (
            not stat.S_ISREG(metadata.st_mode)
            or metadata.st_size != 0
            or metadata.st_nlink != 1
        ):
            raise RuntimeError(f"refusing to remove non-empty or linked Finder sidecar: {path}")
        removed.append(str(path.relative_to(root)))
        path.unlink()
    xattr = Path("/usr/bin/xattr")
    if xattr.is_file():
        for directory in (root, *(path for path in root.rglob("*") if path.is_dir())):
            subprocess.run(
                [str(xattr), "-d", "com.apple.FinderInfo", str(directory)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
    return sorted(removed)


def require_clean_exact_inventory(root: Path, expected: set[Path]) -> None:
    remove_known_finder_metadata(root)
    require_exact_inventory(root, expected)


def _snapshot_path(root: Path, identity: str) -> Path:
    if identity == "__runner__":
        return root / "provenance/run_matched_width.py"
    if identity in EVIDENCE_SOURCES:
        return root / "provenance/evidence/battery_metrics_inventory.csv"
    category = "validation" if identity in VALIDATION_SOURCES else "execution"
    return root / "provenance" / category / identity


def _source_role(identity: str) -> str:
    if identity in EVIDENCE_SOURCES:
        return "interpretation_evidence"
    return "validation" if identity in VALIDATION_SOURCES else "execution"


def expected_source_records(
    root: Path, startup_sources: dict[str, bytes]
) -> list[dict[str, object]]:
    source_paths = _source_paths()
    records = []
    for identity, content in startup_sources.items():
        destination = _snapshot_path(root, identity)
        records.append(
            {
                "identity": identity,
                "role": _source_role(identity),
                "source_path_absolute": str(source_paths[identity]),
                "snapshot_path": str(destination.relative_to(root)),
                "sha256": sha256_bytes(content),
                "bytes": len(content),
            }
        )
    return sorted(records, key=lambda item: str(item["identity"]))


def write_source_snapshots(
    root: Path, startup_sources: dict[str, bytes]
) -> tuple[list[dict[str, object]], set[Path]]:
    records: list[dict[str, object]] = []
    paths: set[Path] = set()
    source_paths = _source_paths()
    for identity, content in startup_sources.items():
        destination = _snapshot_path(root, identity)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(content)
        digest = sha256_bytes(content)
        if sha256(destination) != digest:
            raise RuntimeError(f"source snapshot changed during write: {destination}")
        records.append(
            {
                "identity": identity,
                "role": _source_role(identity),
                "source_path_absolute": str(source_paths[identity]),
                "snapshot_path": str(destination.relative_to(root)),
                "sha256": digest,
                "bytes": len(content),
            }
        )
        paths.add(destination)
    records = sorted(records, key=lambda item: str(item["identity"]))
    if records != expected_source_records(root, startup_sources):
        raise RuntimeError("written source records differ from the canonical source contract")
    return records, paths


def _checkpoint_records(matched: Any) -> list[dict[str, object]]:
    records = [
        {key: value for key, value in record.items() if key != "nlink"}
        for record in matched.validate_checkpoint_registry()
    ]
    return sorted(
        records,
        key=lambda item: (str(item["task"]), str(item["feedback"]), int(item["width"])),
    )


def _write_json_exclusive(path: Path, document: dict[str, object]) -> None:
    with path.open("x") as stream:
        json.dump(document, stream, indent=2, sort_keys=True)
        stream.write("\n")


def _json_normalized(value: object) -> object:
    return json.loads(json.dumps(value, sort_keys=True))


def initialize_run(
    root: Path,
    startup_sources: dict[str, bytes],
    matched: Any,
    runtime: dict[str, str],
) -> tuple[dict[str, object], set[Path]]:
    root = Path(os.path.abspath(root))
    validate_competence_evidence(startup_sources, matched)
    if os.path.lexists(root):
        raise FileExistsError(f"output root already exists: {root}")
    root.mkdir(parents=True)
    (root / "shards").mkdir()
    source_records, snapshots = write_source_snapshots(root, startup_sources)
    run_spec = {
        "schema_version": 1,
        "artifact_class": "staged matched-width VDA checkpoint battery",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_hashes": source_hashes(startup_sources),
        "sources": source_records,
        "runtime": dict(runtime),
        "checkpoints": _checkpoint_records(matched),
        "blocked_cells": matched.blocked_cells(),
        "competence_flags": matched.COMPETENCE_FLAGS,
        "expected_shards": sorted(expected_shard_names(matched)),
        "protocols": {
            shard_name(spec): _json_normalized(matched.protocol_for(spec))
            for spec in matched.admissible_specs()
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }
    run_spec_path = root / "RUN_SPEC.json"
    _write_json_exclusive(run_spec_path, run_spec)
    return run_spec, snapshots | {run_spec_path}


def _source_snapshot_paths(root: Path, run_spec: dict[str, object]) -> set[Path]:
    return {root / str(record["snapshot_path"]) for record in run_spec["sources"]}  # type: ignore[index]


def validate_source_snapshots(root: Path, document: dict[str, object]) -> set[Path]:
    records = document.get("sources")
    hashes = document.get("source_hashes")
    if not isinstance(records, list) or not isinstance(hashes, dict):
        raise ValueError("source provenance records are malformed")
    seen: set[str] = set()
    snapshots: set[Path] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("source provenance record is malformed")
        identity = str(record.get("identity"))
        relative = Path(str(record.get("snapshot_path")))
        if identity in seen or relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError("source provenance contains a duplicate or escaping path")
        seen.add(identity)
        snapshot = root / relative
        if snapshot.is_symlink() or not snapshot.is_file():
            raise FileNotFoundError(f"missing regular source snapshot: {snapshot}")
        if sha256(snapshot) != record.get("sha256") or snapshot.stat().st_size != record.get("bytes"):
            raise RuntimeError(f"source snapshot identity changed: {snapshot}")
        if hashes.get(identity) != record.get("sha256"):
            raise RuntimeError(f"source hash index disagrees for {identity}")
        snapshots.add(snapshot)
    if seen != set(hashes):
        raise RuntimeError("source record inventory differs from source-hash inventory")
    return snapshots


def validate_run_spec(
    root: Path,
    startup_sources: dict[str, bytes],
    matched: Any,
    runtime: dict[str, str],
) -> tuple[dict[str, object], set[Path]]:
    path = root / "RUN_SPEC.json"
    validate_competence_evidence(startup_sources, matched)
    document = json.loads(path.read_text())
    expected_keys = {
        "schema_version", "artifact_class", "created_at_utc", "source_hashes",
        "sources", "runtime", "checkpoints", "blocked_cells", "competence_flags",
        "expected_shards", "protocols", "claim_boundary",
    }
    if set(document) != expected_keys:
        raise RuntimeError("staged run-spec key inventory differs from the canonical contract")
    if document.get("schema_version") != 1:
        raise ValueError("unsupported matched-width run-spec schema")
    if document.get("artifact_class") != "staged matched-width VDA checkpoint battery":
        raise RuntimeError("staged artifact class differs from the canonical contract")
    try:
        created_at = datetime.fromisoformat(str(document["created_at_utc"]))
    except ValueError as error:
        raise RuntimeError("staged creation timestamp is not ISO-8601") from error
    if created_at.tzinfo is None:
        raise RuntimeError("staged creation timestamp must include a timezone")
    if document.get("claim_boundary") != CLAIM_BOUNDARY:
        raise RuntimeError("staged claim boundary differs from the canonical contract")
    if document.get("runtime") != runtime:
        raise RuntimeError("live numerical runtime differs from the staged run")
    if document.get("source_hashes") != source_hashes(startup_sources):
        raise RuntimeError("live executable sources differ from the staged run")
    if document.get("sources") != expected_source_records(root, startup_sources):
        raise RuntimeError("staged source records differ from the canonical source contract")
    if document.get("expected_shards") != sorted(expected_shard_names(matched)):
        raise RuntimeError("staged shard scope differs from the registered scope")
    expected_protocols = {
        shard_name(spec): _json_normalized(matched.protocol_for(spec))
        for spec in matched.admissible_specs()
    }
    if document.get("protocols") != expected_protocols:
        raise RuntimeError("staged protocols differ from the registered protocols")
    if document.get("blocked_cells") != matched.blocked_cells():
        raise RuntimeError("staged blocked-cell scope differs from the registry")
    if document.get("competence_flags") != matched.COMPETENCE_FLAGS:
        raise RuntimeError("staged competence flags differ from the registry")
    if document.get("checkpoints") != _checkpoint_records(matched):
        raise RuntimeError("registered checkpoints differ from the staged run")
    snapshots = validate_source_snapshots(root, document)
    return document, snapshots | {path}


def _spec_by_name(matched: Any) -> dict[str, object]:
    return {shard_name(spec): spec for spec in matched.admissible_specs()}


def validate_existing_shards(
    root: Path,
    matched: Any,
    expected_hashes: dict[str, str],
    expected_runtime: dict[str, str],
) -> set[Path]:
    paths: set[Path] = set()
    for path in sorted((root / "shards").glob("*.npz")):
        spec = _spec_by_name(matched).get(path.name)
        if spec is None:
            raise RuntimeError(f"unregistered matched-width shard: {path}")
        with np.load(path, allow_pickle=False) as data:
            metadata = matched.validate_shard_payload(data, spec)
        if metadata.get("source_hashes") != expected_hashes:
            raise RuntimeError(f"shard source binding mismatch: {path}")
        if metadata.get("runtime") != expected_runtime:
            raise RuntimeError(f"shard numerical runtime mismatch: {path}")
        paths.add(path)
    return paths


def validate_cross_shard_replay(root: Path, matched: Any) -> None:
    by_task: dict[str, list[Path]] = {}
    for spec in matched.admissible_specs():
        by_task.setdefault(spec.task, []).append(root / "shards" / shard_name(spec))
    replay_keys = {
        "displayed_validities", "change_magnitudes", "clamp_dose_parameters",
        "clamp_key_logit_biases",
        "decoder_sample_change_index",
        *{f"decoder_sample_label_{name}" for name in matched.SAMPLE_LABELS},
        *{f"decoder_fold_id_{name}" for name in matched.DECODED_VARIABLES},
    }
    for task, paths in by_task.items():
        with np.load(paths[0], allow_pickle=False) as first:
            reference = {key: np.asarray(first[key]).copy() for key in replay_keys}
        for path in paths[1:]:
            with np.load(path, allow_pickle=False) as data:
                for key, expected in reference.items():
                    if not np.array_equal(np.asarray(data[key]), expected, equal_nan=True):
                        raise RuntimeError(f"common-random-number replay mismatch for {task}/{key}: {path}")


def _artifact_identity(root: Path, path: Path) -> dict[str, object]:
    metadata = path.stat()
    return {
        "path": str(path.relative_to(root)),
        "sha256": sha256(path),
        "bytes": metadata.st_size,
        "device": metadata.st_dev,
        "inode": metadata.st_ino,
    }


def finalize_run(
    root: Path,
    run_spec: dict[str, object],
    admitted: set[Path],
    matched: Any,
    startup_sources: dict[str, bytes],
    runtime: dict[str, str],
) -> Path:
    manifest = root / "MANIFEST.json"
    temporary = root / ".MANIFEST.json.tmp"
    if manifest.exists() or temporary.exists():
        raise FileExistsError("matched-width manifest already exists")
    expected_names = expected_shard_names(matched)
    shard_paths = {root / "shards" / name for name in expected_names}
    if not all(path.is_file() and not path.is_symlink() for path in shard_paths):
        missing = sorted(path.name for path in shard_paths if not path.is_file())
        raise RuntimeError(f"cannot finalize incomplete matched-width run: {missing}")
    existing = validate_existing_shards(
        root, matched, dict(run_spec["source_hashes"]), runtime
    )
    if existing != shard_paths:
        raise RuntimeError("validated shard scope is incomplete")
    validate_cross_shard_replay(root, matched)
    removed = remove_known_finder_metadata(root)
    document = {
        **run_spec,
        "artifact_class": "completed matched-width VDA checkpoint battery",
        "finalized_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_spec_artifact": _artifact_identity(root, root / "RUN_SPEC.json"),
        "shards": [
            _artifact_identity(root, root / "shards" / name)
            for name in sorted(expected_names)
        ],
        "finder_metadata_removed_at_finalization": removed,
        "validation_gate": dict(VALIDATION_GATE),
    }
    temporary.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    expected_without_manifest = admitted | shard_paths
    require_clean_exact_inventory(root, expected_without_manifest | {temporary})
    temporary.replace(manifest)
    try:
        require_clean_exact_inventory(root, expected_without_manifest | {manifest})
        audit_existing_run(
            root, startup_sources=startup_sources, matched=matched, runtime=runtime
        )
    except BaseException:
        manifest.unlink(missing_ok=True)
        raise
    return manifest


def audit_existing_run(
    root: Path,
    *,
    startup_sources: dict[str, bytes],
    matched: Any,
    runtime: dict[str, str],
) -> Path:
    root = Path(os.path.abspath(root))
    before = tuple(
        sorted(
            (str(path.relative_to(root)), path.stat().st_size, sha256(path))
            for path in regular_run_files(root)
        )
    )
    manifest = root / "MANIFEST.json"
    document = json.loads(manifest.read_text())
    run_spec_path = root / "RUN_SPEC.json"
    run_spec_artifact = document.get("run_spec_artifact")
    if (
        not isinstance(run_spec_artifact, dict)
        or _artifact_identity(root, run_spec_path) != run_spec_artifact
    ):
        raise RuntimeError("published RUN_SPEC.json byte identity changed")
    run_spec, staged_admitted = validate_run_spec(
        root, startup_sources, matched, runtime
    )
    if (
        document.get("schema_version") != 1
        or document.get("artifact_class")
        != "completed matched-width VDA checkpoint battery"
    ):
        raise ValueError("unsupported or incomplete matched-width manifest")
    expected_manifest_keys = set(run_spec) | {
        "finalized_at_utc",
        "run_spec_artifact",
        "shards",
        "finder_metadata_removed_at_finalization",
        "validation_gate",
    }
    if set(document) != expected_manifest_keys:
        raise RuntimeError("published manifest key inventory differs from the canonical contract")
    try:
        finalized_at = datetime.fromisoformat(str(document["finalized_at_utc"]))
    except ValueError as error:
        raise RuntimeError("finalization timestamp is not ISO-8601") from error
    if finalized_at.tzinfo is None:
        raise RuntimeError("finalization timestamp must include a timezone")
    created_at = datetime.fromisoformat(str(run_spec["created_at_utc"]))
    if finalized_at < created_at:
        raise RuntimeError("finalization timestamp precedes run creation")
    if document.get("validation_gate") != VALIDATION_GATE:
        raise RuntimeError("published validation-gate record differs from the canonical contract")
    removed = document.get("finder_metadata_removed_at_finalization")
    if (
        not isinstance(removed, list)
        or any(not isinstance(value, str) for value in removed)
        or removed != sorted(set(removed))
    ):
        raise RuntimeError("published Finder-removal record is not canonical")
    for value in removed:
        relative = Path(value)
        if relative.is_absolute() or ".." in relative.parts or relative.name != "Icon\r":
            raise RuntimeError("published Finder-removal path violates the canonical contract")
    for key, value in run_spec.items():
        if key == "artifact_class":
            if value != "staged matched-width VDA checkpoint battery":
                raise RuntimeError("published run has an invalid staged artifact class")
        elif document.get(key) != value:
            raise RuntimeError(f"published manifest differs from RUN_SPEC.json for {key}")
    snapshots = validate_source_snapshots(root, document)
    if staged_admitted != snapshots | {root / "RUN_SPEC.json"}:
        raise RuntimeError("staged and published source inventories differ")
    expected = {manifest, run_spec_path, *snapshots}
    shard_records = document.get("shards")
    if not isinstance(shard_records, list):
        raise RuntimeError("published shard records are malformed")
    expected_shard_paths = [
        root / "shards" / name for name in sorted(expected_shard_names(matched))
    ]
    canonical_shard_records = [
        _artifact_identity(root, path) for path in expected_shard_paths
    ]
    if shard_records != canonical_shard_records:
        raise RuntimeError(
            "published shard records differ from the canonical ordered identities"
        )
    shard_paths = set(expected_shard_paths)
    expected |= shard_paths
    require_exact_inventory(root, expected)
    validate_existing_shards(
        root, matched, dict(document["source_hashes"]), runtime
    )
    validate_cross_shard_replay(root, matched)
    if document.get("checkpoints") != _checkpoint_records(matched):
        raise RuntimeError("published checkpoint identities changed")
    after = tuple(
        sorted(
            (str(path.relative_to(root)), path.stat().st_size, sha256(path))
            for path in regular_run_files(root)
        )
    )
    if after != before:
        raise RuntimeError("read-only matched-width audit changed the run tree")
    return manifest


def _parse_cell(value: str, matched: Any) -> object:
    parts = value.split(",")
    if len(parts) != 3:
        raise ValueError("--cell must be task,feedback,width")
    key = (parts[0], parts[1], int(parts[2]))
    for spec in matched.admissible_specs():
        if (spec.task, spec.feedback, spec.width) == key:
            return spec
    raise ValueError(f"unregistered or blocked matched-width cell: {value}")


def run(args: argparse.Namespace) -> Path:
    startup_sources = capture_executable_sources()
    matched, producer = _load_modules(startup_sources)
    runtime = producer.numerical_runtime()
    root = Path(os.path.abspath(args.output_root))
    if args.audit:
        return audit_existing_run(
            root, startup_sources=startup_sources, matched=matched, runtime=runtime
        )
    if root.exists():
        if (root / "MANIFEST.json").exists():
            return audit_existing_run(
                root, startup_sources=startup_sources, matched=matched, runtime=runtime
            )
        run_spec, admitted = validate_run_spec(
            root, startup_sources, matched, runtime
        )
    else:
        run_spec, admitted = initialize_run(
            root, startup_sources, matched, runtime
        )
    remove_known_finder_metadata(root)
    existing = validate_existing_shards(
        root, matched, dict(run_spec["source_hashes"]), runtime
    )
    allowed = admitted | existing
    require_clean_exact_inventory(root, allowed)
    selected = [_parse_cell(args.cell, matched)] if args.cell else list(matched.admissible_specs())
    for spec in selected:
        path = root / "shards" / shard_name(spec)
        if path in existing:
            continue
        assert_executable_sources_unchanged(startup_sources)
        try:
            producer.write_shard(spec, path, source_hashes=dict(run_spec["source_hashes"]))
            assert_executable_sources_unchanged(startup_sources)
            with np.load(path, allow_pickle=False) as data:
                metadata = matched.validate_shard_payload(data, spec)
            if metadata.get("runtime") != runtime:
                raise RuntimeError(f"new shard numerical runtime mismatch: {path}")
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        existing.add(path)
        require_clean_exact_inventory(root, admitted | existing)
    assert_executable_sources_unchanged(startup_sources)
    if args.no_finalize or existing != {root / "shards" / name for name in expected_shard_names(matched)}:
        return root / "RUN_SPEC.json"
    return finalize_run(
        root, run_spec, admitted, matched, startup_sources, runtime
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--cell", help="optional task,feedback,width cell; incomplete runs remain staged")
    parser.add_argument("--no-finalize", action="store_true")
    parser.add_argument("--audit", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    path = run(parse_args(argv))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
