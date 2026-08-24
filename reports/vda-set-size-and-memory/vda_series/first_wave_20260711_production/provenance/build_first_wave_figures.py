#!/usr/bin/env python3
"""Build the first-wave VDA4/VDA9 environment, attention, and psychometric figures."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIRST_WAVE_TASKS = ("vda4", "vda9")
FIRST_WAVE_FEEDBACK = ("affine_ew", "crossattn1")
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
    "vda_series/__init__.py",
    "vda_series/task_figures.py",
    "vda_series/architecture_figures.py",
    "vda_series/behavior_figures.py",
)


def capture_executable_sources() -> dict[str, bytes]:
    """Freeze every local executable source before importing scientific modules."""
    paths = {
        "__builder__": Path(__file__).resolve(),
        "__producer__": ROOT / "vda_series/first_wave_figures.py",
        **{relative: ROOT / relative for relative in PRODUCER_DEPENDENCIES},
    }
    return {identity: path.read_bytes() for identity, path in paths.items()}


def load_scientific_modules(startup_sources: dict[str, bytes]) -> None:
    """Import only after capture, then prove disk bytes still match the frozen graph."""
    global first_wave_module, core
    global build_attention_figure, build_environment_figure, build_psychometric_figure
    global compute_attention_cache, compute_psychometric_cache
    global producer_dependency_hashes, validate_attention_cache, validate_psychometric_cache

    sys.dont_write_bytecode = True
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    first_wave_module = importlib.import_module("vda_series.first_wave_figures")
    core = importlib.import_module("vda_sweep.vda_core")
    if tuple(first_wave_module.PRODUCER_DEPENDENCIES) != PRODUCER_DEPENDENCIES:
        raise RuntimeError("builder and producer dependency closures disagree")
    for name in (
        "build_attention_figure",
        "build_environment_figure",
        "build_psychometric_figure",
        "compute_attention_cache",
        "compute_psychometric_cache",
        "producer_dependency_hashes",
        "validate_attention_cache",
        "validate_psychometric_cache",
    ):
        globals()[name] = getattr(first_wave_module, name)
    assert_executable_sources_unchanged(startup_sources)


def assert_executable_sources_unchanged(startup_sources: dict[str, bytes]) -> None:
    paths = {
        "__builder__": Path(__file__).resolve(),
        "__producer__": ROOT / "vda_series/first_wave_figures.py",
        **{relative: ROOT / relative for relative in PRODUCER_DEPENDENCIES},
    }
    for identity, path in paths.items():
        if path.read_bytes() != startup_sources[identity]:
            raise RuntimeError(f"executable source changed after startup capture: {path}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def require_exact_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an exact integer; got {value!r}")
    return value


def tree_identity(root: Path) -> tuple[tuple[str, int, str], ...]:
    """Return a framed identity for every file in a completed run, including its manifest."""
    if not root.is_dir():
        raise FileNotFoundError(f"completed run root does not exist: {root}")
    return tuple(
        (str(path.relative_to(root)), path.stat().st_size, sha256(path))
        for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file())
    )


def write_frozen_snapshot(path: Path, startup_bytes: bytes, expected_sha256: str) -> None:
    """Write startup-captured bytes and prove their digest before publication."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(startup_bytes)
    actual_sha256 = sha256(path)
    if actual_sha256 != expected_sha256:
        raise RuntimeError(
            f"snapshot digest {actual_sha256} does not match frozen startup digest {expected_sha256}"
        )


def prepare_fresh_run(root: Path) -> tuple[Path, Path]:
    """Create a unique run root; never mix recomputation with an older tree."""
    if root.exists():
        raise FileExistsError(
            f"output root already exists: {root}; choose a fresh versioned root or use "
            "--reuse-validated-cache for a read-only audit"
        )
    root.mkdir(parents=True)
    return root / "MANIFEST.json", root / ".MANIFEST.json.tmp"


def revalidate_cache_record(record: dict[str, object]) -> None:
    """Rebind a cache to the checkpoint selected at the instant of validation."""
    task = str(record["task"])
    feedback = str(record["feedback"])
    selected_checkpoint = Path(core.ckpt(task, feedback, 128)).resolve()
    selected_checkpoint_sha256 = sha256(selected_checkpoint)
    if selected_checkpoint != Path(str(record["checkpoint_path"])).resolve():
        raise RuntimeError(
            f"selected checkpoint changed during build for {task}/{feedback}: {selected_checkpoint}"
        )
    if selected_checkpoint_sha256 != str(record["checkpoint_sha256"]):
        raise RuntimeError(
            f"selected checkpoint bytes changed during build for {task}/{feedback}"
        )
    common = {
        "expected_task": task,
        "expected_feedback": feedback,
        "expected_checkpoint_path": selected_checkpoint,
        "expected_checkpoint_sha256": selected_checkpoint_sha256,
        "expected_device": str(core.DEVICE),
        "expected_cache_sha256": str(record["cache_sha256"]),
    }
    if record["stage"] == "attention":
        validate_attention_cache(
            record["cache_path"],
            expected_trials=require_exact_int(record["trials"], "attention cache trials"),
            expected_seed=1701,
            **common,
        )
    else:
        validate_psychometric_cache(
            record["cache_path"],
            expected_trials_per_point=require_exact_int(
                record["trials_per_point"], "psychometric cache trials_per_point"
            ),
            expected_seed=2801,
            **common,
        )


def audit_existing_build(root: Path, args: argparse.Namespace) -> Path:
    """Strictly validate an existing completed run without rewriting any byte."""
    manifest_path = root / "MANIFEST.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"completed manifest does not exist: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 3:
        raise ValueError("existing build does not use manifest schema version 3")
    if require_exact_int(
        manifest.get("requested_attention_trials"), "manifest requested_attention_trials"
    ) != args.attention_trials:
        raise ValueError("existing build attention trial request does not match")
    if require_exact_int(
        manifest.get("requested_psychometric_trials_per_point"),
        "manifest requested_psychometric_trials_per_point",
    ) != args.psychometric_trials:
        raise ValueError("existing build psychometric trial request does not match")

    records = manifest.get("validated_caches")
    if not isinstance(records, list):
        raise ValueError("manifest validated_caches must be a list")
    expected_keys = {
        (stage, task, feedback)
        for task in args.tasks
        for feedback in args.feedbacks
        for stage in ("attention", "psychometric")
    }
    actual_keys = {
        (str(record.get("stage")), str(record.get("task")), str(record.get("feedback")))
        for record in records
    }
    if actual_keys != expected_keys or len(records) != len(expected_keys):
        raise ValueError("existing build cache scope does not exactly match the requested scope")
    if manifest.get("realized_attention_trials") != [args.attention_trials]:
        raise ValueError("existing realized attention trials do not match the request")
    if manifest.get("realized_psychometric_trials_per_point") != [args.psychometric_trials]:
        raise ValueError("existing realized psychometric trials do not match the request")
    runtime_versions = manifest.get("runtime_versions")
    for record in records:
        cache_path = Path(str(record["cache_path"])).resolve()
        if root not in cache_path.parents:
            raise ValueError(f"cache path escapes the completed run root: {cache_path}")
        if record.get("runtime_versions") != runtime_versions:
            raise ValueError("manifest and cache runtime identities disagree")
        revalidate_cache_record(record)

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("manifest artifacts must be a list")
    expected_artifact_keys = {
        ("environment", task, None, kind)
        for task in args.tasks
        for kind in ("pdf", "svg", "png", "metadata")
    }
    expected_artifact_keys.update({
        (stage, task, feedback, kind)
        for task in args.tasks
        for feedback in args.feedbacks
        for stage in ("attention", "psychometric")
        for kind in ("cache", "pdf", "svg", "png", "metadata")
    })
    actual_artifact_keys = {
        (
            str(artifact.get("stage")),
            str(artifact.get("task")),
            None if artifact.get("feedback") is None else str(artifact.get("feedback")),
            str(artifact.get("kind")),
        )
        for artifact in artifacts
    }
    if actual_artifact_keys != expected_artifact_keys or len(artifacts) != len(expected_artifact_keys):
        raise ValueError("existing build artifact scope is incomplete or duplicated")
    artifact_paths: set[Path] = set()
    cache_artifact_paths: dict[tuple[str, str, str], Path] = {}
    for artifact in artifacts:
        path = Path(str(artifact["path"])).resolve()
        if root not in path.parents or path in artifact_paths:
            raise ValueError(f"artifact path escapes the run root or is duplicated: {path}")
        artifact_paths.add(path)
        if not path.is_file() or sha256(path) != str(artifact["sha256"]):
            raise RuntimeError(f"existing artifact is missing or changed: {path}")
        if artifact["kind"] == "cache":
            cache_artifact_paths[(str(artifact["stage"]), str(artifact["task"]), str(artifact["feedback"]))] = path
    for record in records:
        key = (str(record["stage"]), str(record["task"]), str(record["feedback"]))
        if Path(str(record["cache_path"])).resolve() != cache_artifact_paths[key]:
            raise ValueError(f"validated cache and cache artifact paths disagree for {key}")

    producer = manifest["producer"]
    build_script = manifest["build_script"]
    provenance_snapshot_paths: set[Path] = set()
    for record, current_path, label in (
        (producer, Path(first_wave_module.__file__).resolve(), "producer"),
        (build_script, Path(__file__).resolve(), "build script"),
    ):
        if Path(str(record["path"])).resolve() != current_path or sha256(current_path) != str(record["sha256"]):
            raise RuntimeError(f"existing {label} identity does not match current source")
        snapshot = Path(str(record["snapshot"])).resolve()
        if root not in snapshot.parents:
            raise ValueError(f"existing {label} snapshot escapes the run root")
        provenance_snapshot_paths.add(snapshot)
        if str(record.get("snapshot_sha256")) != str(record["sha256"]):
            raise ValueError(f"existing {label} snapshot metadata is internally inconsistent")
        if not snapshot.is_file() or sha256(snapshot) != str(record["sha256"]):
            raise RuntimeError(f"existing {label} snapshot is missing or changed")

    current_dependencies = producer_dependency_hashes()
    dependency_records = manifest.get("producer_dependencies", [])
    expected_dependency_identities = {
        str((ROOT / relative_path).resolve()): digest
        for relative_path, digest in current_dependencies.items()
    }
    actual_dependency_identities = {
        str(Path(str(record["path"])).resolve()): str(record["sha256"])
        for record in dependency_records
    }
    if (
        actual_dependency_identities != expected_dependency_identities
        or len(dependency_records) != len(expected_dependency_identities)
    ):
        raise RuntimeError("existing dependency identities do not match current executable graph")
    for record in dependency_records:
        snapshot = Path(str(record["snapshot"])).resolve()
        if root not in snapshot.parents or snapshot in provenance_snapshot_paths:
            raise ValueError(f"dependency snapshot escapes the run root or is duplicated: {snapshot}")
        provenance_snapshot_paths.add(snapshot)
        if str(record.get("snapshot_sha256")) != str(record["sha256"]):
            raise ValueError("dependency snapshot metadata is internally inconsistent")
        if not snapshot.is_file() or sha256(snapshot) != str(record["sha256"]):
            raise RuntimeError(f"existing dependency snapshot is missing or changed: {snapshot}")

    expected_files = artifact_paths | provenance_snapshot_paths | {manifest_path.resolve()}
    actual_files = {path.resolve() for path in root.rglob("*") if path.is_file()}
    if actual_files != expected_files:
        missing = sorted(str(path) for path in expected_files - actual_files)
        unmanifested = sorted(str(path) for path in actual_files - expected_files)
        raise ValueError(
            f"completed run file inventory mismatch; missing={missing}, unmanifested={unmanifested}"
        )
    return manifest_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=Path("../reports/vda_series/first_wave"))
    parser.add_argument("--tasks", nargs="+", choices=FIRST_WAVE_TASKS, default=list(FIRST_WAVE_TASKS))
    parser.add_argument("--feedbacks", nargs="+", choices=FIRST_WAVE_FEEDBACK, default=list(FIRST_WAVE_FEEDBACK))
    parser.add_argument("--attention-trials", type=int, default=96)
    parser.add_argument("--psychometric-trials", type=int, default=300)
    parser.add_argument(
        "--reuse-validated-cache",
        action="store_true",
        help="Read-only audit of a completed build; no cache, figure, or manifest is rewritten.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Deprecated compatibility flag; recomputation is already the default.",
    )
    return parser.parse_args()


def main() -> int:
    startup_sources = capture_executable_sources()
    args = parse_args()
    load_scientific_modules(startup_sources)
    root = args.output_root.resolve()
    if args.force and args.reuse_validated_cache:
        raise ValueError("--force and --reuse-validated-cache are mutually exclusive")
    if args.reuse_validated_cache:
        audit_identity_at_entry = tree_identity(root)
        manifest_path = audit_existing_build(root, args)
        if tree_identity(root) != audit_identity_at_entry:
            raise RuntimeError("completed run tree changed during read-only audit")
        assert_executable_sources_unchanged(startup_sources)
        print(f"[validated reuse] {manifest_path}", flush=True)
        return 0
    manifest_path, manifest_temporary = prepare_fresh_run(root)
    producer_path = Path(first_wave_module.__file__).resolve()
    build_script_path = Path(__file__).resolve()
    producer_bytes_at_start = startup_sources["__producer__"]
    build_script_bytes_at_start = startup_sources["__builder__"]
    producer_sha256_at_start = sha256_bytes(producer_bytes_at_start)
    build_script_sha256_at_start = sha256_bytes(build_script_bytes_at_start)
    dependency_bytes_at_start = {
        relative_path: startup_sources[relative_path]
        for relative_path in PRODUCER_DEPENDENCIES
    }
    dependency_hashes_at_start = {
        relative_path: sha256_bytes(content)
        for relative_path, content in dependency_bytes_at_start.items()
    }
    if dependency_hashes_at_start != producer_dependency_hashes():
        raise RuntimeError("an executable producer dependency changed during startup capture")
    data = root / "data"
    provenance = root / "provenance"
    environment_figures = root / "figures" / "environment"
    attention_figures = root / "figures" / "attention"
    psychometric_figures = root / "figures" / "psychometrics"
    for directory in (data, provenance, environment_figures, attention_figures, psychometric_figures):
        directory.mkdir(parents=True, exist_ok=True)

    artifacts: list[dict[str, object]] = []
    validated_caches: list[dict[str, object]] = []
    for task in args.tasks:
        print(f"[environment] {task}", flush=True)
        environment = build_environment_figure(task, environment_figures, seed=1701)
        for kind, path in (
            ("pdf", environment.pdf),
            ("svg", environment.svg),
            ("png", environment.png),
            ("metadata", environment.metadata),
        ):
            artifacts.append({"stage": "environment", "task": task, "kind": kind, "path": str(path), "sha256": sha256(path)})

        for feedback in args.feedbacks:
            selected_checkpoint = Path(core.ckpt(task, feedback, 128)).resolve()
            selected_checkpoint_sha256 = sha256(selected_checkpoint)
            attention_cache = data / f"attention_{task}_{feedback}.npz"
            print(f"[attention compute] {task} {feedback}", flush=True)
            compute_attention_cache(
                task,
                feedback,
                attention_cache,
                trials=args.attention_trials,
                seed=1701,
                checkpoint_path=selected_checkpoint,
                expected_checkpoint_sha256=selected_checkpoint_sha256,
            )
            attention_cache_metadata = validate_attention_cache(
                attention_cache,
                expected_task=task,
                expected_feedback=feedback,
                expected_trials=args.attention_trials,
                expected_seed=1701,
                expected_device=str(core.DEVICE),
                expected_checkpoint_path=selected_checkpoint,
                expected_checkpoint_sha256=selected_checkpoint_sha256,
            )
            validated_caches.append({
                "stage": "attention",
                "cache_path": str(attention_cache.resolve()),
                **attention_cache_metadata,
            })
            print(f"[attention plot] {task} {feedback}", flush=True)
            attention = build_attention_figure(
                attention_cache,
                attention_figures,
                expected_cache_sha256=str(attention_cache_metadata["cache_sha256"]),
            )
            for kind, path in (
                ("cache", attention_cache),
                ("pdf", attention.pdf),
                ("svg", attention.svg),
                ("png", attention.png),
                ("metadata", attention.metadata),
            ):
                artifacts.append({
                    "stage": "attention",
                    "task": task,
                    "feedback": feedback,
                    "kind": kind,
                    "path": str(path),
                    "sha256": sha256(path),
                })

            psychometric_cache = data / f"psychometric_{task}_{feedback}.npz"
            print(f"[psychometric compute] {task} {feedback}", flush=True)
            compute_psychometric_cache(
                task,
                feedback,
                psychometric_cache,
                trials_per_point=args.psychometric_trials,
                seed=2801,
                checkpoint_path=selected_checkpoint,
                expected_checkpoint_sha256=selected_checkpoint_sha256,
            )
            psychometric_cache_metadata = validate_psychometric_cache(
                psychometric_cache,
                expected_task=task,
                expected_feedback=feedback,
                expected_trials_per_point=args.psychometric_trials,
                expected_seed=2801,
                expected_device=str(core.DEVICE),
                expected_checkpoint_path=selected_checkpoint,
                expected_checkpoint_sha256=selected_checkpoint_sha256,
            )
            validated_caches.append({
                "stage": "psychometric",
                "cache_path": str(psychometric_cache.resolve()),
                **psychometric_cache_metadata,
            })
            print(f"[psychometric plot] {task} {feedback}", flush=True)
            psychometric = build_psychometric_figure(
                psychometric_cache,
                psychometric_figures,
                expected_cache_sha256=str(psychometric_cache_metadata["cache_sha256"]),
            )
            for kind, path in (
                ("cache", psychometric_cache),
                ("pdf", psychometric.pdf),
                ("svg", psychometric.svg),
                ("png", psychometric.png),
                ("metadata", psychometric.metadata),
            ):
                artifacts.append({
                    "stage": "psychometric",
                    "task": task,
                    "feedback": feedback,
                    "kind": kind,
                    "path": str(path),
                    "sha256": sha256(path),
                })

    for record in validated_caches:
        revalidate_cache_record(record)
    for artifact in artifacts:
        path = Path(str(artifact["path"]))
        if not path.is_file() or sha256(path) != artifact["sha256"]:
            raise RuntimeError(f"artifact changed or disappeared during build: {path}")

    if sha256(producer_path) != producer_sha256_at_start:
        raise RuntimeError("first_wave_figures.py changed while the build was running; artifacts are not frozen")
    if sha256(build_script_path) != build_script_sha256_at_start:
        raise RuntimeError("build_first_wave_figures.py changed while the build was running; artifacts are not frozen")
    if producer_dependency_hashes() != dependency_hashes_at_start:
        raise RuntimeError("an executable producer dependency changed while the build was running; artifacts are not frozen")
    producer_snapshot = provenance / "first_wave_figures.py"
    build_script_snapshot = provenance / "build_first_wave_figures.py"
    write_frozen_snapshot(producer_snapshot, producer_bytes_at_start, producer_sha256_at_start)
    write_frozen_snapshot(build_script_snapshot, build_script_bytes_at_start, build_script_sha256_at_start)
    dependency_snapshots = []
    for relative_path, dependency_sha256 in dependency_hashes_at_start.items():
        source = ROOT / relative_path
        snapshot = provenance / "dependencies" / relative_path
        write_frozen_snapshot(
            snapshot,
            dependency_bytes_at_start[relative_path],
            dependency_sha256,
        )
        dependency_snapshots.append({
            "path": str(source),
            "sha256": dependency_sha256,
            "snapshot": str(snapshot),
            "snapshot_sha256": sha256(snapshot),
        })

    realized_attention_trials = sorted({
        int(record["trials"])
        for record in validated_caches
        if record["stage"] == "attention"
    })
    realized_psychometric_trials = sorted({
        int(record["trials_per_point"])
        for record in validated_caches
        if record["stage"] == "psychometric"
    })

    manifest = {
        "schema_version": 3,
        "scope": "first-wave VDA4/VDA9 corrections",
        "environment_geometry": {"vda4": "2x2 fully occupied", "vda9": "3x3 fully occupied"},
        "attention_condition": "red cue at S1; valid change at S1; rows=query patches; columns=logical timesteps",
        "psychometric_panels": [
            "all cue proportions with valid change at S1",
            "all cue proportions with invalid change at bottom-right",
            "100% displayed validity with forced valid and forced invalid changes",
        ],
        "requested_attention_trials": args.attention_trials,
        "requested_psychometric_trials_per_point": args.psychometric_trials,
        "realized_attention_trials": realized_attention_trials,
        "realized_psychometric_trials_per_point": realized_psychometric_trials,
        "runtime_versions": validated_caches[0]["runtime_versions"],
        "producer": {
            "path": str(producer_path),
            "sha256": producer_sha256_at_start,
            "snapshot": str(producer_snapshot),
            "snapshot_sha256": sha256(producer_snapshot),
        },
        "build_script": {
            "path": str(build_script_path),
            "sha256": build_script_sha256_at_start,
            "snapshot": str(build_script_snapshot),
            "snapshot_sha256": sha256(build_script_snapshot),
        },
        "producer_dependencies": dependency_snapshots,
        "validated_caches": validated_caches,
        "artifacts": artifacts,
    }
    manifest_temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # Final fail-closed gate immediately before atomic manifest publication.
    for record in validated_caches:
        revalidate_cache_record(record)
    for artifact in artifacts:
        path = Path(str(artifact["path"]))
        if not path.is_file() or sha256(path) != artifact["sha256"]:
            raise RuntimeError(f"artifact changed or disappeared before publication: {path}")
    if sha256(producer_path) != producer_sha256_at_start:
        raise RuntimeError("first_wave_figures.py changed before manifest publication")
    if sha256(build_script_path) != build_script_sha256_at_start:
        raise RuntimeError("build_first_wave_figures.py changed before manifest publication")
    if producer_dependency_hashes() != dependency_hashes_at_start:
        raise RuntimeError("an executable dependency changed before manifest publication")
    for path, expected_sha256 in (
        (producer_snapshot, producer_sha256_at_start),
        (build_script_snapshot, build_script_sha256_at_start),
        *((Path(record["snapshot"]), str(record["sha256"])) for record in dependency_snapshots),
    ):
        if sha256(path) != expected_sha256:
            raise RuntimeError(f"frozen snapshot changed before manifest publication: {path}")
    manifest_temporary.replace(manifest_path)
    print(f"[complete] {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
