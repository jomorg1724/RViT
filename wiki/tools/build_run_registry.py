"""Build a deterministic, read-only registry of metrics-backed training runs.

The builder discovers runs solely from ``metrics.csv`` files and never imports
or deserializes PyTorch checkpoints. Optional hashes stream raw bytes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import importlib.util
import json
import math
import os
import re
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any


METRICS_ROOTS = (
    Path("RViT_plus_paper_jepa_conv/battery_sweep_results"),
    Path("battery_sweep_results"),
)
# Deterministic producer-source scope.  Training provenance covers only the
# root training/model modules and launch scripts plus the runtime ``config``
# and ``envs`` packages.  Tests, analyses, figures, result trees, logs,
# checkpoints, caches, PDFs, bytecode, and OS metadata are intentionally
# outside this allowlist, even when they have a source-like suffix.
PRODUCER_ROOT_SOURCE_FILES = {
    "__init__.py",
    "conv_frontend.py",
    "model.py",
    "paper_encoder.py",
    "paper_heads.py",
    "patch_embed.py",
    "ppo.py",
    "pretrain_vae.py",
    "train_rl.py",
    "vae.py",
    "vae_frontend.py",
}
PRODUCER_ROOT_SOURCE_SUFFIXES = {".sh"}
PRODUCER_SOURCE_SUBTREES = {"config", "envs"}
PRODUCER_SOURCE_SUFFIXES = {".py", ".json", ".toml", ".yaml", ".yml", ".sh"}

# Full-match launch-name allowlist. A task and budget are recognized together;
# merely beginning with a known task token is not provenance evidence.
RECOGNIZED_LAUNCHES = (
    (
        re.compile(r"motion_convrec_(?:affine_ew|crossattn1)_twolstm_mps"),
        "motion_zk",
        36_000,
        "recognized_twolstm_mps_36k_launch",
    ),
    (
        re.compile(r"motion_(?:affine_ew|crossattn1)_twolstm_mps"),
        "motion_zk",
        36_000,
        "recognized_twolstm_mps_36k_launch",
    ),
    (
        re.compile(r"baruni_(?:affine_ew|crossattn1)(?:_mn\d+)?"),
        "baruni",
        20_000,
        "recognized_battery_sweep_20k_launch",
    ),
    (
        re.compile(r"krauzlis_(?:affine_ew|crossattn1)"),
        "krauzlis",
        20_000,
        "recognized_battery_sweep_20k_launch",
    ),
    (
        re.compile(r"luo_maunsell_sensitivity_(?:affine_ew|crossattn1)"),
        "luo2015_sensitivity",
        20_000,
        "recognized_battery_sweep_20k_launch",
    ),
    (
        re.compile(r"luo_maunsell_criterion_(?:affine_ew|crossattn1)"),
        "luo2015_criterion",
        20_000,
        "recognized_battery_sweep_20k_launch",
    ),
    (
        re.compile(r"validity4_(?:affine_ew|crossattn1)"),
        "validity4",
        20_000,
        "recognized_battery_sweep_20k_launch",
    ),
    (
        re.compile(r"motion_zk_(?:affine_ew|crossattn1)_d\d+(?:_rew\d+(?:\.\d+)?)?"),
        "motion_zk",
        20_000,
        "recognized_battery_sweep_20k_launch",
    ),
    *(
        (
            re.compile(
                rf"{task}_(?:affine_ew|crossattn1)_d\d+(?:_rew\d+(?:\.\d+)?)?"
                + (r"(?:_2x2)?" if task == "vda2" else "")
            ),
            task,
            20_000,
            "recognized_battery_sweep_20k_launch",
        )
        for task in ("vda_excl", "vda16", "vda9", "vda4", "vda2", "vda1")
    ),
)


def _recognized_launch(run_name: str) -> tuple[str, int, str] | None:
    for pattern, task, planned, inference in RECOGNIZED_LAUNCHES:
        if pattern.fullmatch(run_name):
            return task, planned, inference
    return None


def _require_safe_open_support() -> None:
    """Fail closed unless this platform supports component-wise no-follow opens."""
    if (
        not hasattr(os, "O_NOFOLLOW")
        or not hasattr(os, "O_DIRECTORY")
        or os.open not in os.supports_dir_fd
        or os.scandir not in os.supports_fd
    ):
        raise ValueError("component-wise no-follow file opening is unavailable on this platform")


def _directory_flags() -> int:
    return os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)


def _open_safe_directory(path: Path, *, label: str) -> int:
    """Open an absolute directory by walking every component without symlinks."""
    _require_safe_open_support()
    absolute = Path(os.path.abspath(path))
    descriptor = os.open(absolute.anchor, _directory_flags())
    walked = Path(absolute.anchor)
    try:
        for part in absolute.parts[1:]:
            walked /= part
            metadata = os.stat(part, dir_fd=descriptor, follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode):
                raise ValueError(f"{label} must not contain a symlink: {walked}")
            next_descriptor = os.open(part, _directory_flags(), dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _discover_metrics_below(root: Path, root_descriptor: int) -> list[Path]:
    candidates: list[Path] = []

    def visit(directory: Path, descriptor: int) -> None:
        try:
            with os.scandir(descriptor) as entries:
                for entry in entries:
                    candidate = directory / entry.name
                    if entry.name == "metrics.csv" and entry.is_symlink():
                        raise ValueError(f"metrics candidate must not be a symlink: {candidate}")
                    if entry.name == "metrics.csv" and entry.is_file(follow_symlinks=False):
                        candidates.append(candidate)
                    elif entry.is_dir(follow_symlinks=False):
                        child = os.open(entry.name, _directory_flags(), dir_fd=descriptor)
                        visit(candidate, child)
        finally:
            os.close(descriptor)

    visit(root, root_descriptor)
    return candidates


def discover_metrics(workspace: Path) -> list[Path]:
    """Return metrics-backed run candidates from the two approved roots."""
    workspace = Path(os.path.abspath(workspace))
    candidates: list[Path] = []
    for relative_root in METRICS_ROOTS:
        root = workspace / relative_root
        try:
            metadata = root.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"discovery root must not be a symlink: {root}")
        if not stat.S_ISDIR(metadata.st_mode):
            continue
        descriptor = _open_safe_directory(root, label="discovery root")
        candidates.extend(_discover_metrics_below(root, descriptor))
    return sorted(candidates, key=lambda path: path.relative_to(workspace).as_posix())


def _open_safe_file(path: Path, allowed_root: Path, *, label: str = "file"):
    """Open a contained regular file using component-wise no-follow traversal."""
    root = Path(os.path.abspath(allowed_root))
    candidate = Path(os.path.abspath(path))
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label} is outside allowed root {allowed_root}: {path}") from exc
    if not relative.parts:
        raise ValueError(f"{label} is not a file beneath allowed root: {path}")

    directory_descriptor = _open_safe_directory(root, label=f"{label} root")
    try:
        for part in relative.parts[:-1]:
            metadata = os.stat(part, dir_fd=directory_descriptor, follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode):
                raise ValueError(f"{label} path must not contain a symlink: {path}")
            next_descriptor = os.open(part, _directory_flags(), dir_fd=directory_descriptor)
            os.close(directory_descriptor)
            directory_descriptor = next_descriptor

        filename = relative.parts[-1]
        metadata = os.stat(filename, dir_fd=directory_descriptor, follow_symlinks=False)
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"{label} must not be a symlink: {path}")
        descriptor = os.open(
            filename,
            os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0),
            dir_fd=directory_descriptor,
        )
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            os.close(descriptor)
            raise ValueError(f"{label} is not a regular file: {path}")
        return os.fdopen(descriptor, "rb")
    finally:
        os.close(directory_descriptor)


def sha256_file(
    path: Path,
    chunk_size: int = 1024 * 1024,
    *,
    allowed_root: Path | None = None,
) -> str:
    """Hash contained regular-file bytes without interpreting their contents."""
    digest = hashlib.sha256()
    with _open_safe_file(path, allowed_root or path.parent) as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_source_tree(root: Path) -> str | None:
    """Hash the documented producer-source allowlist by name and raw bytes."""
    try:
        root_metadata = root.lstat()
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(root_metadata.st_mode):
        raise ValueError(f"producer root must not be a symlink: {root}")
    if not stat.S_ISDIR(root_metadata.st_mode):
        return None
    root_descriptor = _open_safe_directory(root, label="producer root")
    os.close(root_descriptor)
    for subtree_name in PRODUCER_SOURCE_SUBTREES:
        subtree = root / subtree_name
        try:
            subtree_metadata = subtree.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(subtree_metadata.st_mode):
            raise ValueError(f"source subtree must not be a symlink: {subtree}")
    paths = sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file()
            and (
                (
                    path.parent == root
                    and (
                        path.name in PRODUCER_ROOT_SOURCE_FILES
                        or path.suffix.lower() in PRODUCER_ROOT_SOURCE_SUFFIXES
                    )
                )
                or (
                    path.relative_to(root).parts[0] in PRODUCER_SOURCE_SUBTREES
                    and path.suffix.lower() in PRODUCER_SOURCE_SUFFIXES
                    and "__pycache__" not in path.parts
                )
            )
        ),
        key=lambda path: path.relative_to(root).as_posix(),
    )
    if not paths:
        return None
    digest = hashlib.sha256()
    for path in paths:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        file_digest = bytes.fromhex(sha256_file(path, allowed_root=root))
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(file_digest)
    return digest.hexdigest()


def _relative(path: Path, workspace: Path) -> str:
    return path.relative_to(workspace).as_posix()


def _approved_metrics_root(workspace: Path, metrics_path: Path) -> Path:
    """Return the one approved lexical discovery root containing metrics_path."""
    workspace = Path(os.path.abspath(workspace))
    candidate = Path(os.path.abspath(metrics_path))
    for relative_root in METRICS_ROOTS:
        root = workspace / relative_root
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        try:
            metadata = root.lstat()
        except FileNotFoundError as exc:
            raise ValueError(f"approved discovery root does not exist: {root}") from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"discovery root must not be a symlink: {root}")
        if not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"approved discovery root is not a directory: {root}")
        descriptor = _open_safe_directory(root, label="discovery root")
        os.close(descriptor)
        return root
    raise ValueError(f"metrics candidate is outside approved discovery roots: {metrics_path}")


def _run_evidence_files(run_dir: Path, suffixes: set[str], *, label: str) -> list[Path]:
    """List regular top-level run evidence while rejecting matching symlinks."""
    descriptor = _open_safe_directory(run_dir, label="run root")
    paths: list[Path] = []
    try:
        with os.scandir(descriptor) as entries:
            for entry in entries:
                if Path(entry.name).suffix.lower() not in suffixes:
                    continue
                candidate = run_dir / entry.name
                if entry.is_symlink():
                    raise ValueError(f"{label} must not be a symlink: {candidate}")
                if entry.is_file(follow_symlinks=False):
                    paths.append(candidate)
    finally:
        os.close(descriptor)
    return sorted(paths, key=lambda path: path.name)


def _run_id(metrics_path: Path, workspace: Path) -> str:
    parts = metrics_path.parent.relative_to(workspace).parts
    slug_parts = [re.sub(r"[^a-z0-9]+", "-", part.lower()).strip("-") for part in parts]
    return "run-" + "--".join(slug_parts)


def _task(run_name: str) -> str:
    recognized = _recognized_launch(run_name)
    return recognized[0] if recognized is not None else "unknown"


def _producer(metrics_path: Path, workspace: Path, task: str) -> str | None:
    relative = _relative(metrics_path, workspace)
    if relative.startswith("RViT_plus_paper_jepa_conv/"):
        return "RViT_plus_paper_jepa_conv"
    if "/pod1/" in f"/{relative}" or task.startswith("vda"):
        return "RViT_plus_paper_jepa_grid9"
    if task in {"baruni", "motion_zk", "krauzlis"}:
        return "RViT_plus_paper_jepa_conv"
    return None


def _metrics_summary(path: Path, allowed_root: Path) -> tuple[int, int | None, int]:
    row_count = 0
    maximum: int | None = None
    resets = 0
    previous: int | None = None
    binary_stream = _open_safe_file(path, allowed_root, label="metrics candidate")
    with io.TextIOWrapper(binary_stream, newline="", encoding="utf-8-sig") as stream:
        for line_number, row in enumerate(csv.DictReader(stream), start=2):
            raw = row.get("iter")
            try:
                numeric_iteration = float(raw) if raw is not None else None
            except ValueError:
                numeric_iteration = None
            if numeric_iteration is not None and not math.isfinite(numeric_iteration):
                raise ValueError(
                    f"{path}:{line_number}: non-finite iter metric {raw!r} is not allowed"
                )
            iteration = int(numeric_iteration) if numeric_iteration is not None else None
            if iteration is None:
                continue
            row_count += 1
            maximum = iteration if maximum is None else max(maximum, iteration)
            if previous is not None and iteration < previous:
                resets += 1
            previous = iteration
    return row_count, maximum, resets


def _feedback(run_name: str) -> str | None:
    match = re.search(r"(?:^|_)(affine_ew|crossattn1)(?:_|$)", run_name)
    return match.group(1) if match else None


def _d_mem(run_name: str) -> int | None:
    match = re.search(r"(?:^|_)d(\d+)(?:_|$)", run_name)
    if match:
        return int(match.group(1))
    # These battery sweeps were launched at width 128; the path omits the default.
    if _feedback(run_name):
        return 128
    return None


def _reward_scale(run_name: str, task: str) -> float | None:
    match = re.search(r"(?:^|_)rew(\d+(?:\.\d+)?)(?:_|$)", run_name)
    if match:
        return float(match.group(1))
    if task != "unknown":
        return 1.0
    return None


def _memory_noise(run_name: str) -> float | None:
    match = re.search(r"(?:^|_)mn(\d+)(?:_|$)", run_name)
    if not match:
        return 0.0
    # Sweep names encode sigma in tenths: mn05 -> 0.5, mn10 -> 1.0.
    return int(match.group(1)) / 10


def _planned_iterations(run_name: str, task: str) -> tuple[int | None, str | None]:
    recognized = _recognized_launch(run_name)
    if recognized is None or recognized[0] != task:
        return None, None
    _, planned, inference = recognized
    return planned, inference


def _device(run_dir: Path, run_name: str) -> str | None:
    log_paths = _run_evidence_files(run_dir, {".log"}, label="log")
    if run_name.endswith("_mps"):
        return "mps"
    for log_path in log_paths:
        try:
            binary_stream = _open_safe_file(log_path, run_dir, label="log")
            with io.TextIOWrapper(binary_stream, encoding="utf-8", errors="replace") as stream:
                text = stream.read()
        except OSError:
            continue
        match = re.search(r"\bdevice=(cpu|mps|cuda)\b", text)
        if match:
            return match.group(1)
    return None


def build_run(
    workspace: Path,
    metrics_path: Path,
    *,
    hash_checkpoints: bool = False,
    hash_source: bool = True,
    source_hash_cache: dict[str, str | None] | None = None,
) -> dict[str, Any]:
    """Build one JSON-safe run manifest without loading model tensors."""
    workspace = Path(os.path.abspath(workspace))
    metrics_path = Path(os.path.abspath(metrics_path))
    discovery_root = _approved_metrics_root(workspace, metrics_path)
    run_dir = metrics_path.parent
    run_name = run_dir.name
    task = _task(run_name)
    producer = _producer(metrics_path, workspace, task)
    feedback = _feedback(run_name)
    d_mem = _d_mem(run_name)
    reward_scale = _reward_scale(run_name, task)
    memory_noise = _memory_noise(run_name)
    planned, planned_inference = _planned_iterations(run_name, task)
    row_count, max_iteration, resets = _metrics_summary(metrics_path, discovery_root)
    logged_complete = planned is not None and row_count >= planned

    checkpoint_files = _run_evidence_files(run_dir, {".pt"}, label="checkpoint")
    checkpoint_paths = [_relative(path, workspace) for path in checkpoint_files]
    checkpoint_hashes = {
        relative: sha256_file(path, allowed_root=run_dir) if hash_checkpoints else None
        for path, relative in zip(checkpoint_files, checkpoint_paths)
    }
    analysis_suffixes = {".json", ".npz", ".pdf", ".png", ".svg"}
    analysis_paths = [
        _relative(path, workspace)
        for path in _run_evidence_files(run_dir, analysis_suffixes, label="analysis artifact")
    ]

    caveats: list[str] = []
    if logged_complete:
        caveats.append(
            f"{planned:,} metrics rows establish logged-phase budget completion, "
            "not convergence or learning success."
        )
    if planned_inference:
        caveats.append(
            f"planned_iterations={planned:,} is inferred from the recognized "
            f"{planned_inference} convention, not an archived command."
        )
    else:
        caveats.append(
            "No recognized launch convention establishes planned_iterations; budget completion is not inferred."
        )
    if resets or "twolstm_mps" in run_name:
        caveats.append(
            "Resume or burst counters may reset; max_logged_iteration is not a lifetime-update counter."
        )
    if d_mem == 128 and not re.search(r"(?:^|_)d128(?:_|$)", run_name):
        caveats.append("d_mem=128 is inferred from the battery-sweep launch convention, not encoded in this path.")
    if not logged_complete:
        caveats.append("The available artifacts do not establish why this logged phase stopped.")

    source_hash = None
    if hash_source and producer:
        if source_hash_cache is None:
            source_hash = sha256_source_tree(workspace / producer)
        else:
            if producer not in source_hash_cache:
                source_hash_cache[producer] = sha256_source_tree(workspace / producer)
            source_hash = source_hash_cache[producer]

    producer_id = (
        "rvit-plus-paper-jepa-grid9"
        if producer == "RViT_plus_paper_jepa_grid9"
        else "rvit-plus-paper-jepa-conv"
        if producer == "RViT_plus_paper_jepa_conv"
        else "unknown-producer"
    )
    config = {
        "memory_noise": memory_noise,
        "two_lstm": True if "twolstm" in run_name else False,
        "conv_recurrent": True if "convrec" in run_name else False,
        "planned_iterations_inference": planned_inference,
        "path_inferred": True,
    }
    return {
        "run_id": _run_id(metrics_path, workspace),
        "experiment_id": f"{producer_id}:{task}",
        "task": task,
        "producer_path": producer,
        "source_tree_sha256": source_hash,
        "command": None,
        "config": config,
        "feedback": feedback,
        "d_mem": d_mem,
        "reward_scale": reward_scale,
        "seed": None,
        "device": _device(run_dir, run_name),
        "start_time": None,
        "end_time": None,
        "planned_iterations": planned,
        "max_logged_iteration": max_iteration,
        "completion_reason": "budget_complete" if logged_complete else "unknown",
        "status": "logged_phase_complete" if logged_complete else "partial",
        "metrics_path": _relative(metrics_path, workspace),
        "checkpoint_paths": checkpoint_paths,
        "checkpoint_sha256": checkpoint_hashes,
        "analysis_paths": analysis_paths,
        "parent_run_id": None,
        "caveats": caveats,
    }


def _load_auditor():
    """Load the sibling auditor when this file is run or imported directly."""
    module_path = Path(__file__).with_name("audit_runs.py")
    spec = importlib.util.spec_from_file_location("registry_audit_runs", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load registry auditor: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _stage_bytes(output_dir: Path, target_name: str, content: bytes) -> Path:
    """Durably stage bytes beside their target for same-filesystem replacement."""
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target_name}.", dir=output_dir)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise
    return temporary_path


def _existing_checkpoint_hashes(registry_path: Path) -> dict[tuple[str, str], str]:
    """Return non-null checkpoint hashes keyed by their exact run and path."""
    hashes: dict[tuple[str, str], str] = {}
    if not registry_path.is_file():
        return hashes
    for record in _load_auditor().load_jsonl(registry_path):
        if not isinstance(record.get("run_id"), str):
            continue
        checkpoint_hashes = record.get("checkpoint_sha256")
        if not isinstance(checkpoint_hashes, dict):
            continue
        for checkpoint_path, digest in checkpoint_hashes.items():
            if isinstance(checkpoint_path, str) and isinstance(digest, str):
                hashes[(record["run_id"], checkpoint_path)] = digest
    return hashes


def _validate_projects_catalog(path: Path) -> None:
    """Validate the staged project catalog before either canonical file moves."""

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON constant {value}")

    try:
        with _open_safe_file(path, path.parent, label="staged projects catalog") as handle:
            catalog = json.load(handle, parse_constant=reject_constant)
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        raise ValueError(f"generated projects validation failed: {exc}") from exc

    if not isinstance(catalog, dict) or catalog.get("schema_version") != 1:
        raise ValueError("generated projects validation failed: schema_version must equal 1")
    projects = catalog.get("projects")
    if not isinstance(projects, list):
        raise ValueError("generated projects validation failed: projects must be a list")

    seen_ids: set[str] = set()
    for index, project in enumerate(projects):
        prefix = f"generated projects validation failed: projects[{index}]"
        if not isinstance(project, dict):
            raise ValueError(f"{prefix} must be an object")
        project_id = project.get("project_id")
        producer_path = project.get("producer_path")
        description = project.get("description")
        if not isinstance(project_id, str) or not project_id.strip():
            raise ValueError(f"{prefix}.project_id must be a non-empty string")
        if project_id in seen_ids:
            raise ValueError(f"{prefix}.project_id is duplicated: {project_id}")
        seen_ids.add(project_id)
        if not isinstance(producer_path, str) or not producer_path.strip():
            raise ValueError(f"{prefix}.producer_path must be a non-empty string")
        producer = Path(producer_path)
        if producer.is_absolute() or any(part in {"", ".", ".."} for part in producer.parts):
            raise ValueError(f"{prefix}.producer_path must be a safe relative path")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"{prefix}.description must be a non-empty string")


def write_registry(
    workspace: Path,
    output_dir: Path,
    *,
    hash_checkpoints: bool = False,
    drop_checkpoint_hashes: bool = False,
    hash_source: bool = True,
) -> list[dict[str, Any]]:
    """Build and write deterministic project and JSONL run registries."""
    if hash_checkpoints and drop_checkpoint_hashes:
        raise ValueError("checkpoint hash recompute and drop modes are mutually exclusive")
    workspace = Path(os.path.abspath(workspace))
    candidates = discover_metrics(workspace)
    run_sources: dict[str, list[str]] = {}
    for metrics_path in candidates:
        run_sources.setdefault(_run_id(metrics_path, workspace), []).append(
            _relative(metrics_path, workspace)
        )
    collisions = {run_id: paths for run_id, paths in run_sources.items() if len(paths) > 1}
    if collisions:
        details = "; ".join(
            f"{run_id}: {', '.join(paths)}" for run_id, paths in sorted(collisions.items())
        )
        raise ValueError(f"normalized run_id collision: {details}")

    source_hash_cache: dict[str, str | None] = {}
    runs = [
        build_run(
            workspace,
            metrics_path,
            hash_checkpoints=hash_checkpoints,
            hash_source=hash_source,
            source_hash_cache=source_hash_cache,
        )
        for metrics_path in candidates
    ]
    runs.sort(key=lambda run: run["run_id"])
    preserved_hashes = (
        _existing_checkpoint_hashes(output_dir / "artifacts.jsonl")
        if not hash_checkpoints and not drop_checkpoint_hashes
        else {}
    )
    for run in runs:
        for checkpoint_path in run["checkpoint_paths"]:
            preserved = preserved_hashes.get((run["run_id"], checkpoint_path))
            if preserved is not None:
                run["checkpoint_sha256"][checkpoint_path] = preserved
    projects = {
        "schema_version": 1,
        "projects": [
            {
                "project_id": "rvit-plus-paper-jepa-conv",
                "producer_path": "RViT_plus_paper_jepa_conv",
                "description": "Convolutional-front-end and memory-noise battery runs.",
            },
            {
                "project_id": "rvit-plus-paper-jepa-grid9",
                "producer_path": "RViT_plus_paper_jepa_grid9",
                "description": "Value-directed attention and behavioral battery runs.",
            },
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    projects_bytes = (json.dumps(projects, indent=2, sort_keys=True) + "\n").encode("utf-8")
    artifacts_bytes = "".join(
        json.dumps(run, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
        for run in runs
    ).encode("utf-8")
    staged: dict[Path, Path | None] = {}
    backups: dict[Path, Path | None] = {}
    replaced: list[Path] = []
    projects_target = output_dir / "projects.json"
    artifacts_target = output_dir / "artifacts.jsonl"
    try:
        staged[projects_target] = _stage_bytes(output_dir, "projects.json", projects_bytes)
        staged[artifacts_target] = _stage_bytes(output_dir, "artifacts.jsonl", artifacts_bytes)
        _validate_projects_catalog(staged[projects_target])
        auditor = _load_auditor()
        staged_runs = auditor.load_jsonl(staged[artifacts_target])
        report = auditor.audit_records(staged_runs, workspace)
        if report["errors"]:
            details = "; ".join(
                f"{issue['run_id']}:{issue['field']}: {issue['message']}"
                for issue in report["errors"][:5]
            )
            if len(report["errors"]) > 5:
                details += f"; ... ({len(report['errors'])} errors total)"
            raise ValueError(f"generated registry validation failed: {details}")
        for target in (projects_target, artifacts_target):
            backups[target] = (
                _stage_bytes(output_dir, f"{target.name}.backup", target.read_bytes())
                if target.is_file()
                else None
            )
        for target in (projects_target, artifacts_target):
            os.replace(staged[target], target)
            staged[target] = None
            replaced.append(target)
    except BaseException:
        for target in reversed(replaced):
            backup = backups[target]
            if backup is None:
                target.unlink(missing_ok=True)
            else:
                os.replace(backup, target)
                backups[target] = None
        raise
    finally:
        for temporary_path in (*staged.values(), *backups.values()):
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
    return runs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_workspace = Path(__file__).resolve().parents[2]
    parser.add_argument("--workspace", type=Path, default=default_workspace)
    parser.add_argument(
        "--registry-dir",
        type=Path,
        default=default_workspace / "research_db" / "registry",
    )
    parser.add_argument("--expected-count", type=int, default=44)
    checkpoint_hash_mode = parser.add_mutually_exclusive_group()
    checkpoint_hash_mode.add_argument(
        "--hash-checkpoints",
        action="store_true",
        help="recompute every checkpoint hash from safe raw-byte streams",
    )
    checkpoint_hash_mode.add_argument(
        "--drop-checkpoint-hashes",
        action="store_true",
        help="replace every checkpoint hash with null",
    )
    parser.add_argument("--no-hash-source", action="store_true")
    args = parser.parse_args(argv)

    count = len(discover_metrics(args.workspace))
    if count != args.expected_count:
        print(
            f"ERROR: discovered {count} metrics-backed runs; expected {args.expected_count}",
            file=sys.stderr,
        )
        return 1
    try:
        runs = write_registry(
            args.workspace,
            args.registry_dir,
            hash_checkpoints=args.hash_checkpoints,
            drop_checkpoint_hashes=args.drop_checkpoint_hashes,
            hash_source=not args.no_hash_source,
        )
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {len(runs)} runs to {args.registry_dir / 'artifacts.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
