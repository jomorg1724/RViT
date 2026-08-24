#!/usr/bin/env python3
"""Recover a fully computed corrected-decoder run blocked by Finder metadata."""
from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import build_corrected_decoder as builder
from scripts import run_corrected_decoder as runner


def validate_finder_metadata_files(paths: set[Path]) -> list[Path]:
    """Accept only empty, single-link, regular Finder ``Icon\r`` sidecars."""
    validated: list[Path] = []
    for path in sorted(paths):
        metadata = path.lstat()
        if (
            path.name != "Icon\r"
            or not stat.S_ISREG(metadata.st_mode)
            or metadata.st_size != 0
            or metadata.st_nlink != 1
        ):
            raise RuntimeError(f"unsafe unmanifested entry: {path}")
        validated.append(path)
    return validated


def validate_legacy_identity(
    recorded: dict[str, object], current: dict[str, object]
) -> dict[str, int]:
    """Require stable artifact identity while allowing external alias removal."""
    for key in ("path_absolute", "sha256", "bytes", "device", "inode"):
        if current.get(key) != recorded.get(key):
            raise RuntimeError(f"legacy artifact {key} changed")
    current_nlink = current.get("nlink")
    recorded_nlink = recorded.get("nlink")
    if not isinstance(current_nlink, int) or current_nlink < 1:
        raise RuntimeError("legacy artifact has no remaining filesystem link")
    if not isinstance(recorded_nlink, int) or recorded_nlink < 1:
        raise ValueError("temporary manifest legacy nlink is invalid")
    return {"recorded_nlink": recorded_nlink, "current_nlink": current_nlink}


def clear_finder_info(directory: Path) -> None:
    result = subprocess.run(
        ["/usr/bin/xattr", "-d", "com.apple.FinderInfo", str(directory)],
        text=True,
        capture_output=True,
    )
    if result.returncode == 0 or "No such xattr" in result.stderr:
        return
    raise RuntimeError(f"failed to clear FinderInfo from {directory}: {result.stderr.strip()}")


def _expected_files(root: Path, document: dict[str, object], temporary: Path) -> set[Path]:
    artifact = document.get("artifact")
    sources = document.get("sources")
    if not isinstance(artifact, dict) or not isinstance(sources, list):
        raise ValueError("temporary manifest artifact/source schema is invalid")
    return {
        root / str(artifact["path"]),
        temporary,
        *(root / str(record["snapshot_path"]) for record in sources),
    }


def _validate_temporary_run(
    root: Path, temporary: Path, *, expected_n: int, expected_seed: int
) -> tuple[dict[str, object], set[Path], dict[str, int]]:
    document = json.loads(temporary.read_text(encoding="utf-8"))
    if document.get("schema_version") != 1:
        raise ValueError("unsupported temporary manifest schema")

    artifact_record = document["artifact"]
    if not isinstance(artifact_record, dict):
        raise ValueError("temporary manifest artifact record is invalid")
    archive = root / str(artifact_record["path"])
    archive_identity = runner._regular_identity(archive)
    for key in ("sha256", "bytes", "device", "inode", "nlink"):
        if archive_identity[key] != artifact_record.get(key):
            raise RuntimeError(f"computed archive {key} differs from temporary manifest")

    summary = builder.validate_decode_archive(
        archive, expected_n=expected_n, expected_seed=expected_seed
    )
    if runner._without_checkpoint_records(summary) != document.get("decoder_summary"):
        raise RuntimeError("computed archive summary differs from temporary manifest")
    checkpoints = builder.validate_checkpoint_records(list(summary["checkpoint_records"]))
    if checkpoints != document.get("checkpoints"):
        raise RuntimeError("checkpoint identities differ from temporary manifest")
    recorded_legacy = document.get("legacy_artifact_preserved")
    if not isinstance(recorded_legacy, dict):
        raise ValueError("temporary manifest legacy identity is invalid")
    legacy_link_counts = validate_legacy_identity(
        recorded_legacy, runner._legacy_identity()
    )

    source_paths = runner._source_paths()
    source_records = document.get("sources")
    if not isinstance(source_records, list):
        raise ValueError("temporary manifest sources must be a list")
    identities = {str(record.get("identity")) for record in source_records}
    if identities != set(source_paths) or len(source_records) != len(source_paths):
        raise RuntimeError("temporary manifest source closure is incomplete or duplicated")
    for record in source_records:
        identity = str(record["identity"])
        digest = str(record["sha256"])
        if runner.sha256(source_paths[identity]) != digest:
            raise RuntimeError(f"current source differs from frozen run source: {identity}")
        snapshot = root / str(record["snapshot_path"])
        if runner.sha256(snapshot) != digest:
            raise RuntimeError(f"source snapshot differs from temporary manifest: {snapshot}")

    return document, _expected_files(root, document, temporary), legacy_link_counts


def _remove_finder_metadata(root: Path, files: list[Path]) -> list[str]:
    directories = sorted(
        (path for path in root.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    directories.append(root)
    for directory in directories:
        clear_finder_info(directory)
    removed: list[str] = []
    for path in files:
        removed.append(str(path.relative_to(root)))
        path.unlink()
    return removed


def _audit_published_run(
    root: Path, manifest: Path, *, expected_n: int, expected_seed: int
) -> dict[str, int]:
    initial_identity = runner._tree_identity(builder, root)
    _document, expected, legacy_link_counts = _validate_temporary_run(
        root, manifest, expected_n=expected_n, expected_seed=expected_seed
    )
    builder._require_exact_file_inventory(root, expected)
    if runner._tree_identity(builder, root) != initial_identity:
        raise RuntimeError("published run tree changed during read-only recovery audit")
    return legacy_link_counts


def recover_run(root: str | Path, *, expected_n: int, expected_seed: int) -> tuple[Path, Path]:
    root = Path(os.path.abspath(root))
    manifest = root / "MANIFEST.json"
    temporary = root / ".MANIFEST.json.tmp"
    if manifest.exists():
        raise FileExistsError(f"completed manifest already exists: {manifest}")
    if not temporary.is_file():
        raise FileNotFoundError(f"temporary manifest does not exist: {temporary}")

    temporary_sha256 = runner.sha256(temporary)
    document, expected, legacy_link_counts = _validate_temporary_run(
        root, temporary, expected_n=expected_n, expected_seed=expected_seed
    )
    actual = builder.regular_run_files(root)
    finder_files = validate_finder_metadata_files(actual - expected)
    removed = _remove_finder_metadata(root, finder_files)
    builder.publish_manifest_with_inventory(
        root,
        temporary,
        manifest,
        expected - {temporary},
    )
    post_audit_link_counts = _audit_published_run(
        root, manifest, expected_n=expected_n, expected_seed=expected_seed
    )
    if post_audit_link_counts != legacy_link_counts:
        raise RuntimeError("legacy link count changed during publication recovery")
    if runner.sha256(manifest) != temporary_sha256:
        raise RuntimeError("published manifest bytes differ from validated temporary manifest")

    attestation = root.parent / f"{root.name}.PUBLICATION_RECOVERY.json"
    if attestation.exists():
        raise FileExistsError(f"recovery attestation already exists: {attestation}")
    record = {
        "schema_version": 1,
        "action": "removed empty Finder Icon\\r metadata and atomically promoted pre-existing manifest",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_root": str(root),
        "removed_files": removed,
        "removed_directory_xattr": "com.apple.FinderInfo",
        "manifest_sha256_before_promotion": temporary_sha256,
        "manifest_sha256_after_promotion": runner.sha256(manifest),
        "artifact_sha256": document["artifact"]["sha256"],
        "legacy_link_count_drift": legacy_link_counts,
        "recovery_script": str(Path(__file__).resolve()),
        "recovery_script_sha256": runner.sha256(Path(__file__)),
        "post_recovery_read_only_audit": "passed",
    }
    attestation.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest, attestation


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=runner.DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--n", type=int, default=runner.DEFAULT_N)
    parser.add_argument("--seed", type=int, default=runner.DEFAULT_SEED)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    manifest, attestation = recover_run(
        args.output_root, expected_n=args.n, expected_seed=args.seed
    )
    print(f"[recovered publication] {manifest}")
    print(f"[recovery attestation] {attestation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
