"""Refresh VDA4 cross-attention event maps without collapsing key sources.

The admitted spatial-scaling cache retained trialwise visual-plus-memory
location mass, but retained source-resolved query/key attention only after
averaging trials.  That is sufficient for a descriptive mean map, but not for
the requested trialwise visual-key and recurrent-memory-key quadrant maxima.

This producer replays only the original 128 event-attention trials for each
valid/invalid condition.  It discovers the five admitted cross-attention
checkpoint manifests, verifies their file hashes, regenerates the exact fixed
trial banks, and stores query-averaged visual and recurrent-memory maps before
any source summation.  It does not run psychometrics or interventions and it
refuses to overwrite an existing output directory.

For raw attention ``A[..., i, k]`` with ``N`` visual queries and ``2N`` keys,
keys ``0..N-1`` are visual and ``N..2N-1`` are recurrent memory.  The retained
source score is

    p[..., source, j] = (1 / N) * sum_i A[..., i, source, j].

These are unconditional masses under the original joint ``2N``-key softmax.
They are deliberately not normalized within source.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = (
    ROOT
    / "reports"
    / "vda_series"
    / "spatial_scaling_evaluation_production_20260727"
)

SOURCE_RE = re.compile(
    r"^vda4_crossattn1_grid(?P<rows>2|4|10)x(?P<cols>2|4|10)_seed(?P<seed>[01])$"
)
ADMITTED_LABELS = frozenset(
    {
        "vda4_crossattn1_grid2x2_seed0",
        "vda4_crossattn1_grid2x2_seed1",
        "vda4_crossattn1_grid4x4_seed0",
        "vda4_crossattn1_grid10x10_seed0",
        "vda4_crossattn1_grid10x10_seed1",
    }
)
CONDITIONS = ("valid", "invalid")
SOURCE_NAMES = ("visual", "memory")
CHANGE_INDICES = (0, 3)
CUE_INDEX = 0
FOCAL_VALIDITY = 1.0
FOCAL_MAGNITUDE = 30.0
ATTENTION_TRIALS = 128
ATTENTION_SEED = 202707360
TIMESTEPS = 7
CHECKPOINT_ITERATION = 19999
SOURCE_RTOL = 1e-5
SOURCE_ATOL = 2e-5


@dataclass(frozen=True)
class Source:
    label: str
    grid_rows: int
    grid_cols: int
    n_tokens: int
    seed: int
    directory: Path
    manifest_path: Path
    config_path: Path
    event_path: Path
    checkpoint_path: Path
    checkpoint_sha256: str
    manifest_sha256: str
    event_sha256: str
    source_producer_path: Path
    source_producer_sha256: str


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def finite_array(value: Any, label: str) -> np.ndarray:
    array = np.asarray(value)
    require(bool(np.all(np.isfinite(array))), f"{label} contains non-finite values")
    return array


def quadrant_indices(grid_rows: int, grid_cols: int) -> tuple[tuple[int, ...], ...]:
    """Partition an even native grid into four row-major physical quadrants."""
    if grid_rows <= 0 or grid_cols <= 0 or grid_rows % 2 or grid_cols % 2:
        raise ValueError(
            f"expected positive even grid dimensions, got {grid_rows}x{grid_cols}"
        )
    regions: list[tuple[int, ...]] = []
    half_rows, half_cols = grid_rows // 2, grid_cols // 2
    for quadrant_row in range(2):
        for quadrant_col in range(2):
            regions.append(
                tuple(
                    row * grid_cols + col
                    for row in range(
                        quadrant_row * half_rows,
                        (quadrant_row + 1) * half_rows,
                    )
                    for col in range(
                        quadrant_col * half_cols,
                        (quadrant_col + 1) * half_cols,
                    )
                )
            )
    flat = sorted(token for region in regions for token in region)
    require(
        flat == list(range(grid_rows * grid_cols)),
        "quadrants do not partition native tokens",
    )
    return tuple(regions)


def query_averaged_source_mass(
    raw_attention: np.ndarray,
    n_tokens: int,
) -> np.ndarray:
    """Split visual/memory keys and average queries without source renormalization.

    The input must end in ``(query=N, key=2N)``.  The output ends in
    ``(source=2, spatial_key=N)`` with source order ``visual, memory``.
    Leading axes, such as trial and time, are preserved.
    """
    raw = finite_array(raw_attention, "raw attention").astype(np.float64)
    require(raw.ndim >= 2, f"raw attention lacks query/key axes: {raw.shape}")
    require(raw.shape[-2] == n_tokens, f"expected {n_tokens} queries, got {raw.shape[-2]}")
    require(raw.shape[-1] == 2 * n_tokens, f"expected {2*n_tokens} keys, got {raw.shape[-1]}")
    require(bool(np.all(raw >= 0.0)), "raw attention contains negative mass")
    require(
        bool(np.allclose(raw.sum(axis=-1), 1.0, rtol=1e-5, atol=1e-6)),
        "raw cross-attention rows are not normalized over 2N keys",
    )
    separated = np.stack(
        (raw[..., :n_tokens], raw[..., n_tokens:]),
        axis=-2,
    )
    source_mass = separated.mean(axis=-3)
    require(source_mass.shape[-2:] == (2, n_tokens), "source mass shape mismatch")
    require(
        bool(np.allclose(source_mass.sum(axis=(-2, -1)), 1.0, rtol=1e-5, atol=1e-6)),
        "query-averaged source mass is not globally normalized",
    )
    return source_mass


def source_quadrant_statistics(
    source_token_mass: np.ndarray,
    grid_rows: int,
    grid_cols: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return source-specific quadrant total and peak on the original mass scale."""
    source = finite_array(source_token_mass, "source token mass").astype(np.float64)
    n_tokens = grid_rows * grid_cols
    require(source.ndim >= 2, "source token mass lacks source/token axes")
    require(source.shape[-2:] == (2, n_tokens), f"unexpected source mass shape {source.shape}")
    require(bool(np.all(source >= 0.0)), "source token mass contains negative values")
    regions = quadrant_indices(grid_rows, grid_cols)
    total = np.stack(
        [source[..., list(region)].sum(axis=-1) for region in regions],
        axis=-1,
    )
    peak = np.stack(
        [source[..., list(region)].max(axis=-1) for region in regions],
        axis=-1,
    )
    require(total.shape[-2:] == (2, 4), "source quadrant total shape mismatch")
    require(peak.shape[-2:] == (2, 4), "source quadrant peak shape mismatch")
    return total, peak


def combined_location_mass(source_token_mass: np.ndarray) -> np.ndarray:
    """Sum visual and memory source maps only after retaining source results."""
    source = finite_array(source_token_mass, "source token mass").astype(np.float64)
    require(source.ndim >= 2 and source.shape[-2] == 2, "expected a two-source axis")
    combined = source.sum(axis=-2)
    require(
        bool(np.allclose(combined.sum(axis=-1), 1.0, rtol=1e-5, atol=1e-6)),
        "combined location mass is not normalized",
    )
    return combined


def _load_json(path: Path, label: str) -> dict[str, Any]:
    require(path.is_file(), f"{label} not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), f"{label} must contain a JSON object")
    return payload


def _validate_source_artifact_inventory(directory: Path, manifest: dict[str, Any]) -> None:
    declared = manifest.get("artifact_hashes")
    require(isinstance(declared, dict) and declared, f"{directory.name}: missing artifact hashes")
    actual = {
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file() and path.name != "MANIFEST.json"
    }
    require(
        actual == set(declared),
        f"{directory.name}: source manifest inventory mismatch; "
        f"undeclared={sorted(actual-set(declared))}, missing={sorted(set(declared)-actual)}",
    )
    for relative, expected in declared.items():
        path = directory / Path(relative)
        require(
            sha256_file(path) == str(expected),
            f"{directory.name}: source artifact hash mismatch for {relative}",
        )


def discover_sources(source_root: Path) -> list[Source]:
    """Discover and fail-closed validate the five admitted cross-attention cells."""
    require(source_root.is_dir(), f"source root not found: {source_root}")
    found: dict[str, Source] = {}
    for directory in sorted(source_root.iterdir()):
        if not directory.is_dir():
            continue
        match = SOURCE_RE.fullmatch(directory.name)
        if match is None or directory.name not in ADMITTED_LABELS:
            continue
        label = directory.name
        rows, cols, seed = (
            int(match.group("rows")),
            int(match.group("cols")),
            int(match.group("seed")),
        )
        n_tokens = rows * cols
        manifest_path = directory / "MANIFEST.json"
        config_path = directory / "analysis_config.json"
        event_path = directory / "data" / "event_attention.npz"
        manifest = _load_json(manifest_path, f"{label} manifest")
        config = _load_json(config_path, f"{label} config")
        require(manifest.get("schema_version") == 1, f"{label}: source manifest schema")
        require(manifest.get("status") == "complete", f"{label}: source manifest is not complete")
        _validate_source_artifact_inventory(directory, manifest)
        model = manifest.get("model")
        require(isinstance(model, dict), f"{label}: source manifest lacks model record")
        exact_model = {
            "label": label,
            "task": "vda4",
            "feedback": "crossattn1",
            "grid_rows": rows,
            "grid_cols": cols,
            "n_tokens": n_tokens,
            "checkpoint_iteration": CHECKPOINT_ITERATION,
        }
        for key, expected in exact_model.items():
            require(model.get(key) == expected, f"{label}: model {key} contract mismatch")
        checkpoint_path = Path(str(model.get("checkpoint_path", ""))).expanduser().resolve()
        checkpoint_sha256 = str(model.get("checkpoint_sha256", ""))
        require(checkpoint_path.is_file(), f"{label}: checkpoint not found: {checkpoint_path}")
        require(len(checkpoint_sha256) == 64, f"{label}: invalid checkpoint hash")
        require(
            sha256_file(checkpoint_path) == checkpoint_sha256,
            f"{label}: checkpoint SHA-256 mismatch",
        )
        source_producer_path = Path(str(model.get("producer_path", ""))).resolve()
        source_producer_sha256 = str(model.get("producer_sha256", ""))
        require(source_producer_path.is_file(), f"{label}: source producer missing")
        require(
            sha256_file(source_producer_path) == source_producer_sha256,
            f"{label}: source producer SHA-256 mismatch",
        )
        exact_config = {
            "label": label,
            "task": "vda4",
            "feedback": "crossattn1",
            "grid_rows": rows,
            "grid_cols": cols,
            "n_tokens": n_tokens,
            "checkpoint_iteration": CHECKPOINT_ITERATION,
            "checkpoint_sha256": checkpoint_sha256,
            "attention_trials": ATTENTION_TRIALS,
            "focal_validity": FOCAL_VALIDITY,
            "focal_magnitude": FOCAL_MAGNITUDE,
        }
        for key, expected in exact_config.items():
            require(config.get(key) == expected, f"{label}: config {key} contract mismatch")
        artifacts = manifest["artifact_hashes"]
        event_sha256 = str(artifacts.get("data/event_attention.npz", ""))
        require(event_path.is_file(), f"{label}: event cache missing")
        require(sha256_file(event_path) == event_sha256, f"{label}: event cache hash mismatch")
        require(label not in found, f"duplicate admitted source: {label}")
        found[label] = Source(
            label=label,
            grid_rows=rows,
            grid_cols=cols,
            n_tokens=n_tokens,
            seed=seed,
            directory=directory.resolve(),
            manifest_path=manifest_path.resolve(),
            config_path=config_path.resolve(),
            event_path=event_path.resolve(),
            checkpoint_path=checkpoint_path,
            checkpoint_sha256=checkpoint_sha256,
            manifest_sha256=sha256_file(manifest_path),
            event_sha256=event_sha256,
            source_producer_path=source_producer_path,
            source_producer_sha256=source_producer_sha256,
        )
    require(
        set(found) == ADMITTED_LABELS,
        f"admitted source set mismatch; found={sorted(found)}, expected={sorted(ADMITTED_LABELS)}",
    )
    return sorted(found.values(), key=lambda source: (source.n_tokens, source.seed))


def load_verified_event_cache(source: Source) -> dict[str, np.ndarray]:
    with np.load(source.event_path, allow_pickle=False) as payload:
        required = {"press", "token_mass", "region_mass", "raw_attention_mean"}
        require(required.issubset(payload.files), f"{source.label}: event cache fields missing")
        press = np.asarray(payload["press"], dtype=np.int64)
        token_mass = finite_array(payload["token_mass"], f"{source.label}/token_mass").astype(np.float64)
        region_mass = finite_array(payload["region_mass"], f"{source.label}/region_mass").astype(np.float64)
        raw_mean = finite_array(payload["raw_attention_mean"], f"{source.label}/raw_attention_mean").astype(np.float64)
        metadata = {
            key: np.asarray(payload[key]).item()
            for key in (
                "meta_label",
                "meta_task",
                "meta_feedback",
                "meta_grid_rows",
                "meta_grid_cols",
                "meta_n_tokens",
                "meta_checkpoint_iteration",
                "meta_checkpoint_sha256",
            )
        }
    expected_token = (2, ATTENTION_TRIALS, TIMESTEPS, source.n_tokens)
    expected_raw = (2, TIMESTEPS, source.n_tokens, 2 * source.n_tokens)
    require(press.shape == (2, ATTENTION_TRIALS), f"{source.label}: press shape {press.shape}")
    require(token_mass.shape == expected_token, f"{source.label}: token mass shape {token_mass.shape}")
    require(region_mass.shape == (2, ATTENTION_TRIALS, TIMESTEPS, 4), f"{source.label}: region mass shape")
    require(raw_mean.shape == expected_raw, f"{source.label}: raw mean shape {raw_mean.shape}")
    require(bool(np.allclose(token_mass.sum(axis=-1), 1.0, atol=SOURCE_ATOL)), f"{source.label}: token mass normalization")
    require(bool(np.allclose(raw_mean.sum(axis=-1), 1.0, atol=SOURCE_ATOL)), f"{source.label}: raw mean normalization")
    expected_metadata = {
        "meta_label": source.label,
        "meta_task": "vda4",
        "meta_feedback": "crossattn1",
        "meta_grid_rows": source.grid_rows,
        "meta_grid_cols": source.grid_cols,
        "meta_n_tokens": source.n_tokens,
        "meta_checkpoint_iteration": CHECKPOINT_ITERATION,
        "meta_checkpoint_sha256": source.checkpoint_sha256,
    }
    require(metadata == expected_metadata, f"{source.label}: event cache metadata mismatch")
    rebuilt_source = query_averaged_source_mass(raw_mean, source.n_tokens)
    rebuilt_combined = combined_location_mass(rebuilt_source)
    require(
        bool(np.allclose(rebuilt_combined, token_mass.mean(axis=1), rtol=SOURCE_RTOL, atol=SOURCE_ATOL)),
        f"{source.label}: raw mean does not reconstruct cached trial-mean location mass",
    )
    return {
        "press": press,
        "token_mass": token_mass,
        "region_mass": region_mass,
        "raw_attention_mean": raw_mean,
    }


def first_press_from_logits(logits: np.ndarray) -> np.ndarray:
    actions = np.asarray(logits).argmax(axis=-1)
    press = np.full(actions.shape[0], -1, dtype=np.int64)
    for frame in range(actions.shape[1]):
        new = (actions[:, frame] == 1) & (press < 0)
        press[new] = frame
    return press


def rollout_attention(model: Any, videos: Any, core: Any) -> tuple[np.ndarray, np.ndarray]:
    """Run one deterministic event bank and retain every raw attention trial."""
    import torch

    batch = int(videos.shape[0])
    state = model.init_states(batch, device=core.DEVICE)
    logits: list[np.ndarray] = []
    attention: list[np.ndarray] = []
    for frame in range(TIMESTEPS):
        with torch.no_grad():
            step = model.rl_step(videos[:, frame], state, return_attn=True)
        state = step["new_states"]
        logits.append(step["actor_logits"].detach().cpu().numpy())
        step_attention = step["attn"]
        while isinstance(step_attention, (list, tuple)) and len(step_attention) == 1:
            step_attention = step_attention[0]
        if isinstance(step_attention, (list, tuple)) or step_attention is None:
            raise RuntimeError("source refresh expects one concrete attention tensor")
        attention.append(step_attention.detach().cpu().numpy().astype(np.float32))
    logits_array = np.stack(logits, axis=1)
    return first_press_from_logits(logits_array), np.stack(attention, axis=1)


def _validate_checkpoint_contract(source: Source, torch: Any) -> None:
    checkpoint = torch.load(source.checkpoint_path, map_location="cpu", weights_only=False)
    require(isinstance(checkpoint, dict), f"{source.label}: checkpoint is not a mapping")
    require("model_state_dict" in checkpoint, f"{source.label}: checkpoint lacks model_state_dict")
    require(checkpoint.get("task") == "vda4", f"{source.label}: checkpoint task")
    require(int(checkpoint.get("iter", -1)) == CHECKPOINT_ITERATION, f"{source.label}: checkpoint iteration")
    require(int(checkpoint.get("checkpoint_schema_version", -1)) >= 3, f"{source.label}: checkpoint schema")
    model_kwargs = checkpoint.get("model_kwargs")
    require(isinstance(model_kwargs, dict), f"{source.label}: checkpoint lacks model_kwargs")
    expected = {
        "feedback": "crossattn1",
        "d_mem": 128,
        "grid_rows": source.grid_rows,
        "grid_cols": source.grid_cols,
        "image_size": 50,
    }
    for key, value in expected.items():
        actual = model_kwargs.get(key)
        actual = str(actual) if isinstance(value, str) else int(actual)
        require(actual == value, f"{source.label}: checkpoint model_kwargs[{key}]={actual!r}")
    producer = checkpoint.get("producer_sha256")
    require(isinstance(producer, dict) and producer, f"{source.label}: checkpoint producer provenance")


def _save_npz(
    path: Path,
    source: Source,
    press: np.ndarray,
    source_token_mass: np.ndarray,
    source_share: np.ndarray,
    source_quadrant_total: np.ndarray,
    source_quadrant_peak: np.ndarray,
    raw_attention_mean: np.ndarray,
) -> None:
    np.savez_compressed(
        path,
        press=np.asarray(press, dtype=np.int64),
        source_token_mass=np.asarray(source_token_mass, dtype=np.float32),
        source_share=np.asarray(source_share, dtype=np.float32),
        source_quadrant_total=np.asarray(source_quadrant_total, dtype=np.float32),
        source_quadrant_peak=np.asarray(source_quadrant_peak, dtype=np.float32),
        raw_attention_mean=np.asarray(raw_attention_mean, dtype=np.float32),
        conditions=np.asarray(CONDITIONS),
        source_names=np.asarray(SOURCE_NAMES),
        meta_schema_version=np.asarray(1, dtype=np.int64),
        meta_label=np.asarray(source.label),
        meta_task=np.asarray("vda4"),
        meta_feedback=np.asarray("crossattn1"),
        meta_grid_rows=np.asarray(source.grid_rows, dtype=np.int64),
        meta_grid_cols=np.asarray(source.grid_cols, dtype=np.int64),
        meta_n_tokens=np.asarray(source.n_tokens, dtype=np.int64),
        meta_seed=np.asarray(source.seed, dtype=np.int64),
        meta_checkpoint_iteration=np.asarray(CHECKPOINT_ITERATION, dtype=np.int64),
        meta_checkpoint_sha256=np.asarray(source.checkpoint_sha256),
        meta_source_manifest_sha256=np.asarray(source.manifest_sha256),
        meta_source_event_sha256=np.asarray(source.event_sha256),
        meta_attention_trials=np.asarray(ATTENTION_TRIALS, dtype=np.int64),
        meta_attention_seed=np.asarray(ATTENTION_SEED, dtype=np.int64),
        meta_source_normalization=np.asarray("unconditional global 2N-key softmax mass"),
    )


def _package_version(distribution: str) -> str:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def runtime_versions(torch: Any) -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "torch": str(torch.__version__),
        "gymnasium": _package_version("gymnasium"),
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_version": str(torch.version.cuda),
    }


def refresh_source(
    source: Source,
    output_root: Path,
    *,
    core: Any,
    torch: Any,
    device: str,
    threads: int,
    producer_sha256: str,
    versions: dict[str, Any],
) -> dict[str, Any]:
    existing = load_verified_event_cache(source)
    _validate_checkpoint_contract(source, torch)
    model, iteration = core.load(
        "vda4",
        "crossattn1",
        128,
        checkpoint_path=str(source.checkpoint_path),
        expected_checkpoint_sha256=source.checkpoint_sha256,
        require_iteration=CHECKPOINT_ITERATION,
        validate_metadata=False,
    )
    require(iteration == CHECKPOINT_ITERATION, f"{source.label}: loaded iteration mismatch")
    require(int(model.n_tokens) == source.n_tokens, f"{source.label}: loaded token count mismatch")
    require(str(model.encoder.feedback) == "crossattn1", f"{source.label}: loaded feedback mismatch")

    presses: list[np.ndarray] = []
    source_masses: list[np.ndarray] = []
    raw_means: list[np.ndarray] = []
    started = time.time()
    for condition_index, change_index in enumerate(CHANGE_INDICES):
        videos = core.make_video_batch(
            "vda4",
            CUE_INDEX,
            FOCAL_VALIDITY,
            "red",
            1,
            change_index,
            FOCAL_MAGNITUDE,
            B=ATTENTION_TRIALS,
            seed=ATTENTION_SEED + condition_index,
        )
        press, raw = rollout_attention(model, videos, core)
        expected_raw = (ATTENTION_TRIALS, TIMESTEPS, source.n_tokens, 2 * source.n_tokens)
        require(raw.shape == expected_raw, f"{source.label}: refreshed raw shape {raw.shape}")
        presses.append(press)
        source_masses.append(query_averaged_source_mass(raw, source.n_tokens))
        raw_means.append(raw.astype(np.float64).mean(axis=0))
    press_array = np.stack(presses, axis=0)
    source_token_mass = np.stack(source_masses, axis=0)
    raw_attention_mean = np.stack(raw_means, axis=0)
    expected_source = (2, ATTENTION_TRIALS, TIMESTEPS, 2, source.n_tokens)
    require(source_token_mass.shape == expected_source, f"{source.label}: refreshed source shape")
    source_share = source_token_mass.sum(axis=-1)
    source_quadrant_total, source_quadrant_peak = source_quadrant_statistics(
        source_token_mass,
        source.grid_rows,
        source.grid_cols,
    )
    require(source_share.shape == (2, ATTENTION_TRIALS, TIMESTEPS, 2), f"{source.label}: share shape")
    require(source_quadrant_total.shape == (2, ATTENTION_TRIALS, TIMESTEPS, 2, 4), f"{source.label}: quadrant total shape")
    require(source_quadrant_peak.shape == (2, ATTENTION_TRIALS, TIMESTEPS, 2, 4), f"{source.label}: quadrant peak shape")
    require(
        bool(np.allclose(source_share.sum(axis=-1), 1.0, rtol=1e-5, atol=1e-6)),
        f"{source.label}: source shares do not sum to one",
    )

    combined = combined_location_mass(source_token_mass)
    press_match = bool(np.array_equal(press_array, existing["press"]))
    combined_match = bool(
        np.allclose(combined, existing["token_mass"], rtol=SOURCE_RTOL, atol=SOURCE_ATOL)
    )
    raw_mean_match = bool(
        np.allclose(
            raw_attention_mean,
            existing["raw_attention_mean"],
            rtol=SOURCE_RTOL,
            atol=SOURCE_ATOL,
        )
    )
    require(press_match, f"{source.label}: refreshed presses differ from verified cache")
    require(combined_match, f"{source.label}: source sum differs from verified token mass")
    require(raw_mean_match, f"{source.label}: refreshed raw mean differs from verified cache")
    comparisons = {
        "press_exact_match": press_match,
        "source_sum_matches_verified_token_mass": combined_match,
        "raw_mean_matches_verified_raw_mean": raw_mean_match,
        "source_sum_max_abs_error": float(np.max(np.abs(combined - existing["token_mass"]))),
        "raw_mean_max_abs_error": float(
            np.max(np.abs(raw_attention_mean - existing["raw_attention_mean"]))
        ),
        "rtol": SOURCE_RTOL,
        "atol": SOURCE_ATOL,
    }

    model_root = output_root / source.label
    model_root.mkdir()
    data_root = model_root / "data"
    data_root.mkdir()
    data_path = data_root / "source_attention.npz"
    config_path = model_root / "config.json"
    manifest_path = model_root / "MANIFEST.json"
    config = {
        "schema_version": 1,
        "artifact": "VDA4 source-resolved held-out event-attention refresh",
        "scientific_evidence_boundary": (
            "held-out routing measurement for one fixed checkpoint; trial intervals do not "
            "estimate training-seed or population uncertainty"
        ),
        "model": {
            "label": source.label,
            "task": "vda4",
            "feedback": "crossattn1",
            "grid_rows": source.grid_rows,
            "grid_cols": source.grid_cols,
            "n_tokens": source.n_tokens,
            "seed": source.seed,
            "checkpoint_iteration": CHECKPOINT_ITERATION,
            "checkpoint_path": source.checkpoint_path,
            "checkpoint_sha256": source.checkpoint_sha256,
        },
        "source_artifacts": {
            "evaluation_manifest": source.manifest_path,
            "evaluation_manifest_sha256": source.manifest_sha256,
            "event_cache": source.event_path,
            "event_cache_sha256": source.event_sha256,
            "evaluation_producer": source.source_producer_path,
            "evaluation_producer_sha256": source.source_producer_sha256,
        },
        "refresh_producer": {
            "path": Path(__file__).resolve(),
            "sha256": producer_sha256,
        },
        "runtime": versions,
        "device": device,
        "threads": threads,
        "conditions": CONDITIONS,
        "change_indices": CHANGE_INDICES,
        "cue_index": CUE_INDEX,
        "focal_validity": FOCAL_VALIDITY,
        "focal_magnitude_degrees": FOCAL_MAGNITUDE,
        "attention_trials_per_condition": ATTENTION_TRIALS,
        "attention_trial_seeds": [ATTENTION_SEED, ATTENTION_SEED + 1],
        "timesteps": TIMESTEPS,
        "source_axis": SOURCE_NAMES,
        "source_normalization": "unconditional global 2N-key softmax mass",
        "source_token_mass_formula": "p[source,j] = mean_query A[query,source,j]",
        "source_quadrant_total_formula": "sum of source_token_mass over native keys in one fixed physical quadrant",
        "source_quadrant_peak_formula": "max of source_token_mass over native keys in one fixed physical quadrant",
        "uniform_raw_key_baseline": f"1/(2N) = {1.0/(2.0*source.n_tokens):.17g}",
        "comparisons_to_verified_cache": comparisons,
    }
    write_json(config_path, config)
    _save_npz(
        data_path,
        source,
        press_array,
        source_token_mass,
        source_share,
        source_quadrant_total,
        source_quadrant_peak,
        raw_attention_mean,
    )
    artifacts = {
        "config.json": sha256_file(config_path),
        "data/source_attention.npz": sha256_file(data_path),
    }
    manifest = {
        "schema_version": 1,
        "status": "complete",
        "label": source.label,
        "producer_path": Path(__file__).resolve(),
        "producer_sha256": producer_sha256,
        "source_manifest_sha256": source.manifest_sha256,
        "source_event_sha256": source.event_sha256,
        "checkpoint_sha256": source.checkpoint_sha256,
        "comparisons_to_verified_cache": comparisons,
        "elapsed_seconds": time.time() - started,
        "artifact_hashes": artifacts,
    }
    write_json(manifest_path, manifest)
    result = {
        "label": source.label,
        "manifest_path": manifest_path.resolve(),
        "manifest_sha256": sha256_file(manifest_path),
        "data_sha256": artifacts["data/source_attention.npz"],
        "comparisons": comparisons,
    }
    del model
    if device == "cuda":
        torch.cuda.empty_cache()
    return result


def run(args: argparse.Namespace) -> Path:
    source_root = Path(args.source_root).expanduser().resolve()
    output_root = Path(args.output_root).expanduser().resolve()
    require(args.threads > 0, "--threads must be positive")
    require(not output_root.exists(), f"refusing to overwrite output root: {output_root}")
    sources = discover_sources(source_root)

    os.environ["RVIT_DEVICE"] = args.device
    os.environ.setdefault("RVIT_PROJECT_ROOT", str(ROOT))
    sys.modules.setdefault("numpy._core", np.core)
    sys.modules.setdefault("numpy._core.multiarray", np.core.multiarray)
    import torch

    torch.set_num_threads(args.threads)
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but torch.cuda.is_available() is false")
    from vda_sweep import vda_core as core

    require(str(core.DEVICE) == args.device, f"vda_core device is {core.DEVICE}, expected {args.device}")
    producer_path = Path(__file__).resolve()
    producer_sha256 = sha256_file(producer_path)
    versions = runtime_versions(torch)
    output_root.mkdir(parents=True)
    started = time.time()
    results = []
    for source in sources:
        print(f"[refresh] {source.label}", flush=True)
        results.append(
            refresh_source(
                source,
                output_root,
                core=core,
                torch=torch,
                device=args.device,
                threads=args.threads,
                producer_sha256=producer_sha256,
                versions=versions,
            )
        )
    root_manifest = {
        "schema_version": 1,
        "status": "complete",
        "artifact": "VDA4 cross-attention source-resolved held-out refresh",
        "producer_path": producer_path,
        "producer_sha256": producer_sha256,
        "source_root": source_root,
        "admitted_labels": sorted(ADMITTED_LABELS),
        "device": args.device,
        "threads": args.threads,
        "runtime": versions,
        "elapsed_seconds": time.time() - started,
        "models": results,
    }
    root_manifest_path = output_root / "MANIFEST.json"
    write_json(root_manifest_path, root_manifest)
    print(
        json.dumps(
            {
                "status": "complete",
                "output_root": str(output_root),
                "models": len(results),
                "manifest_sha256": sha256_file(root_manifest_path),
            },
            indent=2,
        ),
        flush=True,
    )
    return output_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--device", choices=("cuda", "cpu"), default="cuda")
    parser.add_argument("--threads", type=int, default=3)
    return parser


def main(argv: list[str] | None = None) -> int:
    run(build_parser().parse_args(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
