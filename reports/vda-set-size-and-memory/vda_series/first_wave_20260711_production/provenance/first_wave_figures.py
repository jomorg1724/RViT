"""First-wave VDA4/VDA9 figure specifications and deterministic pipelines.

The focused figures keep historical task geometry separate from the controlled
fixed-grid tasks: VDA4 is a fully occupied 2x2 display and VDA9 is a fully
occupied 3x3 display. Compute functions write NPZ/JSON evidence; plot functions
consume only those caches.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


FIRST_WAVE_TASKS = ("vda4", "vda9")
FIRST_WAVE_FEEDBACK = ("affine_ew", "crossattn1")
CHANGE_MAGNITUDES = np.array([0, 3, 6, 9, 12, 15, 18, 22, 26, 30], dtype=np.float64)
DISPLAYED_VALIDITIES = np.array([0.25, 0.5, 0.75, 1.0], dtype=np.float64)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
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


def producer_dependency_hashes() -> dict[str, str]:
    """Return the executable producer dependency set bound into every cache."""
    return {
        relative: hashlib.sha256((PROJECT_ROOT / relative).read_bytes()).hexdigest()
        for relative in PRODUCER_DEPENDENCIES
    }


def _dependency_hashes_json() -> str:
    return json.dumps(producer_dependency_hashes(), sort_keys=True, separators=(",", ":"))


def producer_runtime_versions() -> dict[str, str]:
    """Return runtime versions that can change numerical or rendered outputs."""
    import gymnasium
    from PIL import __version__ as pillow_version
    import scipy
    import torch

    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "torch": torch.__version__,
        "scipy": scipy.__version__,
        "gymnasium": gymnasium.__version__,
        "pillow": pillow_version,
        "python_executable": str(Path(sys.executable).resolve()),
    }


def _runtime_versions_json() -> str:
    return json.dumps(producer_runtime_versions(), sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class FirstWaveSpec:
    task: str
    grid: tuple[int, int]
    image_size: int
    token_count: int
    active_indices: tuple[int, ...]
    cue_index: int
    invalid_change_index: int


@dataclass(frozen=True)
class FigureOutputs:
    pdf: Path
    svg: Path
    png: Path
    metadata: Path


_SPECS = {
    "vda4": FirstWaveSpec("vda4", (2, 2), 50, 4, tuple(range(4)), 0, 3),
    "vda9": FirstWaveSpec("vda9", (3, 3), 75, 9, tuple(range(9)), 0, 8),
}


def first_wave_spec(task: str) -> FirstWaveSpec:
    try:
        return _SPECS[task]
    except KeyError as exc:
        raise ValueError(f"unknown first-wave task {task!r}; expected one of {FIRST_WAVE_TASKS}") from exc


def attention_condition(task: str) -> dict[str, Any]:
    spec = first_wave_spec(task)
    return {
        "cue_index": spec.cue_index,
        "change_index": spec.cue_index,
        "displayed_validity": 1.0,
        "cue_color": "red",
        "change_magnitude_degrees": 56.0,
        "change_present": True,
        "change_frame": 5,
        "timesteps": 7,
    }


def build_environment_figure(task: str, output_dir: str | Path, seed: int = 1701) -> FigureOutputs:
    """Render the focused historical geometry and requested forced locations."""
    spec = first_wave_spec(task)
    from vda_series.task_figures import (
        _render_stimuli,
        render_cue_frame,
        task_spec,
    )

    source_spec = task_spec(task)
    active = tuple(range(spec.token_count))
    rng = np.random.default_rng(seed)
    baseline = {index: float(rng.uniform(0.0, 180.0)) for index in active}
    valid_orientations = dict(baseline)
    invalid_orientations = dict(baseline)
    valid_orientations[spec.cue_index] = (valid_orientations[spec.cue_index] + 56.0) % 180.0
    invalid_orientations[spec.invalid_change_index] = (
        invalid_orientations[spec.invalid_change_index] + 56.0
    ) % 180.0
    panels = (
        render_cue_frame(source_spec, spec.cue_index, 1.0),
        _render_stimuli(source_spec, active, baseline),
        _render_stimuli(source_spec, active, valid_orientations),
        _render_stimuli(source_spec, active, invalid_orientations),
    )
    panel_titles = (
        "A  Red cue at S1",
        f"B  Fully occupied {spec.grid[0]}×{spec.grid[1]} array",
        "C  Valid change at S1",
        f"D  Invalid change at S{spec.invalid_change_index + 1}",
    )
    highlights = (
        (spec.cue_index, "#D55E00", "cue"),
        (None, "#000000", ""),
        (spec.cue_index, "#0072B2", "change"),
        (spec.invalid_change_index, "#CC79A7", "change"),
    )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"first_wave_environment_{task}"
    outputs = FigureOutputs(
        pdf=output_dir / f"{stem}.pdf",
        svg=output_dir / f"{stem}.svg",
        png=output_dir / f"{stem}.png",
        metadata=output_dir / f"{stem}.json",
    )
    figure, axes = plt.subplots(1, 4, figsize=(13.8, 4.0), constrained_layout=True)
    rows, cols = spec.grid
    cell_height = spec.image_size / rows
    cell_width = spec.image_size / cols
    for axis, image, title, highlight in zip(axes, panels, panel_titles, highlights):
        axis.imshow(np.clip(image, 0.0, 1.0), interpolation="nearest")
        axis.set_title(title, loc="left", fontweight="bold", fontsize=11)
        axis.set_xticks([])
        axis.set_yticks([])
        for row in range(rows):
            for column in range(cols):
                index = row * cols + column
                axis.text(
                    column * cell_width + 2,
                    row * cell_height + 3,
                    f"S{index + 1}",
                    ha="left",
                    va="top",
                    fontsize=7.5,
                    color="white",
                    bbox={"facecolor": "black", "edgecolor": "none", "alpha": 0.62, "pad": 1.2},
                )
        for boundary in range(1, rows):
            axis.axhline(boundary * cell_height - 0.5, color="white", linewidth=0.7, alpha=0.55)
        for boundary in range(1, cols):
            axis.axvline(boundary * cell_width - 0.5, color="white", linewidth=0.7, alpha=0.55)
        index, color, label = highlight
        if index is not None:
            row, column = divmod(index, cols)
            axis.add_patch(
                plt.Rectangle(
                    (column * cell_width - 0.35, row * cell_height - 0.35),
                    cell_width - 0.3,
                    cell_height - 0.3,
                    fill=False,
                    edgecolor=color,
                    linewidth=2.7,
                )
            )
            axis.text(
                column * cell_width + cell_width - 2,
                row * cell_height + cell_height - 2,
                label,
                ha="right",
                va="bottom",
                fontsize=8,
                color="white",
                bbox={"facecolor": color, "edgecolor": "none", "alpha": 0.88, "pad": 1.4},
            )
    figure.suptitle(
        f"{task.upper()} historical environment · {rows}×{cols} grid · {spec.token_count} active stimuli",
        fontsize=14,
        fontweight="bold",
    )
    figure.supxlabel(
        "S-labels and borders are explanatory overlays. The cue is spatially presented in S1; change panels differ from the shared array at the bordered location.",
        fontsize=9.5,
    )
    figure.savefig(outputs.pdf, bbox_inches="tight")
    figure.savefig(outputs.svg, bbox_inches="tight")
    figure.savefig(outputs.png, dpi=300, bbox_inches="tight")
    plt.close(figure)

    metadata = {
        "schema_version": 1,
        "artifact": "first-wave historical environment schematic",
        "task": task,
        "lineage": "historical task specification",
        "grid": list(spec.grid),
        "model_tokens": spec.token_count,
        "active_items": spec.token_count,
        "cue_index": spec.cue_index,
        "valid_change_index": spec.cue_index,
        "invalid_change_index": spec.invalid_change_index,
        "cue_color": "red",
        "change_magnitude_degrees": 56.0,
        "panels": [
            "red cue at S1",
            "fully occupied array",
            "valid change at S1",
            "invalid change at bottom-right",
        ],
        "seed": seed,
        "overlay_disclosure": "S-labels and colored borders are explanatory overlays, not observation pixels",
        "outputs": {"pdf": outputs.pdf.name, "svg": outputs.svg.name, "png": outputs.png.name},
    }
    outputs.metadata.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return outputs


def spatial_attention_maps(raw_attention: np.ndarray, *, feedback: str) -> np.ndarray:
    """Map raw attention to ``(..., time, query patch, spatial key location)``.

    Affine feedback exposes N spatial keys. Cross-attention exposes N image and
    N recurrent-memory keys; paired image/memory keys are summed by location.
    The query-patch axis is preserved so a figure can have N rows and T columns.
    """
    raw = np.asarray(raw_attention, dtype=np.float64)
    if raw.ndim not in (3, 4):
        raise ValueError(
            "raw attention must have shape (time, query, key) or "
            f"(trial, time, query, key); got {raw.shape}"
        )
    if not np.isfinite(raw).all():
        raise ValueError("raw attention must contain only finite values")
    if np.any(raw < 0.0):
        raise ValueError("raw attention mass must be nonnegative")
    queries, keys = raw.shape[-2:]
    expected_keys = {"affine_ew": queries, "crossattn1": 2 * queries}
    if feedback not in expected_keys:
        raise ValueError(f"unknown feedback family {feedback!r}")
    if keys != expected_keys[feedback]:
        raise ValueError(
            f"{feedback} attention requires K={expected_keys[feedback]} for N={queries}; got K={keys}"
        )
    if keys == queries:
        spatial = raw.copy()
    elif keys == 2 * queries:
        spatial = raw[..., :queries] + raw[..., queries:]
    else:
        raise ValueError(f"attention key count must equal N or 2N; got N={queries}, K={keys}")
    row_mass = spatial.sum(axis=-1)
    if not np.allclose(row_mass, 1.0, rtol=1e-5, atol=1e-6):
        raise ValueError("raw attention rows must sum to one before spatial interpretation")
    return spatial


def attention_reduction_note(feedback: str) -> str:
    """Return the self-contained spatial-key contract displayed on attention figures."""
    if feedback == "affine_ew":
        return "Affine attention uses one spatial key per location."
    if feedback == "crossattn1":
        return "Cross-attention image and memory keys are paired and summed by spatial location."
    raise ValueError(f"unknown feedback family {feedback!r}")


def _npz_scalar(payload: Any, key: str) -> Any:
    if key not in payload:
        raise ValueError(f"attention cache is missing required field {key!r}")
    value = np.asarray(payload[key])
    if value.ndim != 0:
        raise ValueError(f"attention cache field {key!r} must be scalar")
    return value.item()


def _npz_integer_scalar(payload: Any, key: str) -> int:
    """Return an exact integer scalar without truncating floats or accepting booleans."""
    value = _npz_scalar(payload, key)
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"cache {key} must be an integer scalar; got {value!r}")
    return int(value)


def _frozen_cache_bytes(cache_path: Path, expected_sha256: str | None = None) -> tuple[bytes, str]:
    """Read one immutable cache snapshot and optionally bind it to an expected digest."""
    content = cache_path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise RuntimeError(
            f"cache SHA-256 {digest} does not match expected immutable digest {expected_sha256}"
        )
    return content, digest


def _location_label(index: int, spec: FirstWaveSpec) -> str:
    row, col = divmod(index, spec.grid[1])
    if index == 0:
        return "S1 / top-left"
    if index == spec.invalid_change_index:
        return f"S{index + 1} / bottom-right"
    return f"S{index + 1} / r{row + 1}c{col + 1}"


def _require_npz_fields(payload: Any, fields: tuple[str, ...], cache_path: Path) -> None:
    missing = sorted(set(fields) - set(payload.files))
    if missing:
        raise ValueError(f"cache {cache_path} is missing required fields: {missing}")


def _validate_common_cache(
    payload: Any,
    cache_path: Path,
    *,
    expected_task: str | None,
    expected_feedback: str | None,
    expected_checkpoint_path: str | Path | None,
    expected_checkpoint_sha256: str | None,
    expected_device: str | None,
) -> dict[str, Any]:
    required = (
        "task",
        "feedback",
        "checkpoint_iteration",
        "checkpoint_path",
        "checkpoint_sha256",
        "producer_path",
        "producer_sha256",
        "dependency_hashes_json",
        "runtime_versions_json",
        "device",
        "grid",
    )
    _require_npz_fields(payload, required, cache_path)
    task = str(_npz_scalar(payload, "task"))
    feedback = str(_npz_scalar(payload, "feedback"))
    if task not in FIRST_WAVE_TASKS:
        raise ValueError(f"cache task must be one of {FIRST_WAVE_TASKS}; got {task!r}")
    if feedback not in FIRST_WAVE_FEEDBACK:
        raise ValueError(f"cache feedback must be one of {FIRST_WAVE_FEEDBACK}; got {feedback!r}")
    if expected_task is not None and task != expected_task:
        raise ValueError(f"cache task is {task!r}, expected {expected_task!r}")
    if expected_feedback is not None and feedback != expected_feedback:
        raise ValueError(f"cache feedback is {feedback!r}, expected {expected_feedback!r}")

    producer_path = Path(str(_npz_scalar(payload, "producer_path"))).resolve()
    current_producer_path = Path(__file__).resolve()
    if producer_path != current_producer_path:
        raise ValueError(f"cache producer path {producer_path} does not match {current_producer_path}")
    producer_sha = str(_npz_scalar(payload, "producer_sha256"))
    current_producer_sha = _sha256(current_producer_path)
    if producer_sha != current_producer_sha:
        raise ValueError(
            f"cache producer SHA-256 {producer_sha} does not match current producer {current_producer_sha}"
        )
    stored_dependencies = str(_npz_scalar(payload, "dependency_hashes_json"))
    current_dependencies = _dependency_hashes_json()
    if stored_dependencies != current_dependencies:
        raise ValueError("cache dependency digests do not match the current executable producer graph")
    stored_runtime = str(_npz_scalar(payload, "runtime_versions_json"))
    current_runtime = _runtime_versions_json()
    if stored_runtime != current_runtime:
        raise ValueError("cache runtime versions do not match the current scientific runtime")

    checkpoint_path = Path(str(_npz_scalar(payload, "checkpoint_path")))
    if not checkpoint_path.is_file():
        raise ValueError(f"cache checkpoint does not exist: {checkpoint_path}")
    checkpoint_sha = str(_npz_scalar(payload, "checkpoint_sha256"))
    actual_checkpoint_sha = _sha256(checkpoint_path)
    if checkpoint_sha != actual_checkpoint_sha:
        raise ValueError(
            f"cache checkpoint SHA-256 {checkpoint_sha} does not match {actual_checkpoint_sha}"
        )
    resolved_checkpoint = checkpoint_path.resolve()
    if expected_checkpoint_path is not None:
        selected_checkpoint = Path(expected_checkpoint_path).resolve()
        if resolved_checkpoint != selected_checkpoint:
            raise ValueError(
                f"cache checkpoint path {resolved_checkpoint} does not match "
                f"selected checkpoint path {selected_checkpoint}"
            )
    if expected_checkpoint_sha256 is not None and checkpoint_sha != expected_checkpoint_sha256:
        raise ValueError(
            f"cache checkpoint SHA-256 {checkpoint_sha} does not match "
            f"selected checkpoint SHA-256 {expected_checkpoint_sha256}"
        )
    iteration = _npz_integer_scalar(payload, "checkpoint_iteration")
    if iteration < 0:
        raise ValueError("cache checkpoint iteration must be nonnegative")
    device = str(_npz_scalar(payload, "device"))
    if not device:
        raise ValueError("cache device must be nonempty")
    if expected_device is not None and device != expected_device:
        raise ValueError(f"cache device is {device!r}, expected {expected_device!r}")
    spec = first_wave_spec(task)
    grid = np.asarray(payload["grid"], dtype=np.int64)
    np.testing.assert_array_equal(grid, np.asarray(spec.grid, dtype=np.int64))
    return {
        "task": task,
        "feedback": feedback,
        "checkpoint_iteration": iteration,
        "checkpoint_path": str(resolved_checkpoint),
        "checkpoint_sha256": checkpoint_sha,
        "producer_sha256": producer_sha,
        "dependency_hashes": json.loads(stored_dependencies),
        "runtime_versions": json.loads(stored_runtime),
        "device": device,
        "grid": list(spec.grid),
    }


def validate_attention_cache(
    cache_path: str | Path,
    *,
    expected_task: str | None = None,
    expected_feedback: str | None = None,
    expected_trials: int | None = None,
    expected_seed: int | None = None,
    expected_device: str | None = None,
    expected_checkpoint_path: str | Path | None = None,
    expected_checkpoint_sha256: str | None = None,
    expected_cache_sha256: str | None = None,
) -> dict[str, Any]:
    """Fail closed unless an attention cache satisfies the complete contract."""
    cache_path = Path(cache_path)
    cache_bytes, cache_sha256 = _frozen_cache_bytes(cache_path, expected_cache_sha256)
    required = (
        "raw_attention_trials",
        "raw_attention_mean",
        "spatial_attention_trials",
        "spatial_attention",
        "trials",
        "seed",
        "cue_index",
        "change_index",
        "displayed_validity",
        "cue_color",
        "change_magnitude_degrees",
        "change_frame",
        "change_present",
        "timesteps",
        "model_width",
    )
    with np.load(io.BytesIO(cache_bytes), allow_pickle=False) as payload:
        _require_npz_fields(payload, required, cache_path)
        metadata = _validate_common_cache(
            payload,
            cache_path,
            expected_task=expected_task,
            expected_feedback=expected_feedback,
            expected_checkpoint_path=expected_checkpoint_path,
            expected_checkpoint_sha256=expected_checkpoint_sha256,
            expected_device=expected_device,
        )
        spec = first_wave_spec(metadata["task"])
        feedback = metadata["feedback"]
        trials = _npz_integer_scalar(payload, "trials")
        if trials <= 0:
            raise ValueError("attention cache trials must be positive")
        if expected_trials is not None and trials != expected_trials:
            raise ValueError(f"attention cache has {trials} trials, expected {expected_trials}")
        seed = _npz_integer_scalar(payload, "seed")
        if expected_seed is not None and seed != expected_seed:
            raise ValueError(f"attention cache seed is {seed}, expected {expected_seed}")
        condition = attention_condition(metadata["task"])
        scalar_expectations = {
            "cue_index": condition["cue_index"],
            "change_index": condition["change_index"],
            "displayed_validity": condition["displayed_validity"],
            "cue_color": condition["cue_color"],
            "change_magnitude_degrees": condition["change_magnitude_degrees"],
            "change_frame": condition["change_frame"],
            "change_present": condition["change_present"],
            "timesteps": condition["timesteps"],
            "model_width": 128,
        }
        for field, expected in scalar_expectations.items():
            actual = _npz_scalar(payload, field)
            if actual != expected:
                raise ValueError(f"attention cache {field} is {actual!r}, expected {expected!r}")
        raw_trials = np.asarray(payload["raw_attention_trials"], dtype=np.float64)
        raw_mean = np.asarray(payload["raw_attention_mean"], dtype=np.float64)
        spatial_trials = np.asarray(payload["spatial_attention_trials"], dtype=np.float64)
        spatial = np.asarray(payload["spatial_attention"], dtype=np.float64)
        expected_spatial = (7, spec.token_count, spec.token_count)
        if spatial.shape != expected_spatial:
            raise ValueError(f"spatial attention has shape {spatial.shape}, expected {expected_spatial}")
        if spatial_trials.shape != (trials,) + expected_spatial:
            raise ValueError(
                f"trial-level spatial attention has shape {spatial_trials.shape}, "
                f"expected {(trials,) + expected_spatial}"
            )
        expected_keys = spec.token_count if feedback == "affine_ew" else 2 * spec.token_count
        expected_raw = (7, spec.token_count, expected_keys)
        if raw_mean.shape != expected_raw or raw_trials.shape != (trials,) + expected_raw:
            raise ValueError(
                f"raw attention shapes {raw_trials.shape} and {raw_mean.shape} do not satisfy "
                f"{feedback} contract {(trials,) + expected_raw}"
            )
        reduced_trials = spatial_attention_maps(raw_trials, feedback=feedback)
        reduced_mean = spatial_attention_maps(raw_mean, feedback=feedback)
        np.testing.assert_allclose(raw_mean, raw_trials.mean(axis=0), rtol=1e-5, atol=1e-6)
        np.testing.assert_allclose(spatial_trials, reduced_trials, rtol=1e-5, atol=1e-6)
        np.testing.assert_allclose(spatial, reduced_mean, rtol=1e-5, atol=1e-6)
        np.testing.assert_allclose(spatial, spatial_trials.mean(axis=0), rtol=1e-5, atol=1e-6)
        metadata.update({"trials": trials, "seed": seed, "cache_sha256": cache_sha256})
        return metadata


def validate_psychometric_cache(
    cache_path: str | Path,
    *,
    expected_task: str | None = None,
    expected_feedback: str | None = None,
    expected_trials_per_point: int | None = None,
    expected_seed: int | None = None,
    expected_device: str | None = None,
    expected_checkpoint_path: str | Path | None = None,
    expected_checkpoint_sha256: str | None = None,
    expected_cache_sha256: str | None = None,
) -> dict[str, Any]:
    """Fail closed unless a psychometric cache satisfies the complete contract."""
    cache_path = Path(cache_path)
    cache_bytes, cache_sha256 = _frozen_cache_bytes(cache_path, expected_cache_sha256)
    required = (
        "response_rate_valid",
        "response_rate_invalid",
        "response_count_valid",
        "response_count_invalid",
        "change_magnitudes",
        "displayed_validities",
        "point_seeds",
        "seed",
        "seed_policy",
        "trials_per_point",
        "cue_index",
        "valid_change_index",
        "invalid_change_index",
        "cue_color",
        "qualifying_response_frame",
        "change_present",
        "timesteps",
        "model_width",
    )
    with np.load(io.BytesIO(cache_bytes), allow_pickle=False) as payload:
        _require_npz_fields(payload, required, cache_path)
        metadata = _validate_common_cache(
            payload,
            cache_path,
            expected_task=expected_task,
            expected_feedback=expected_feedback,
            expected_checkpoint_path=expected_checkpoint_path,
            expected_checkpoint_sha256=expected_checkpoint_sha256,
            expected_device=expected_device,
        )
        condition = psychometric_conditions(metadata["task"])
        trials = _npz_integer_scalar(payload, "trials_per_point")
        if trials <= 0:
            raise ValueError("psychometric trials_per_point must be positive")
        if expected_trials_per_point is not None and trials != expected_trials_per_point:
            raise ValueError(
                f"psychometric cache has {trials} trials/point, expected {expected_trials_per_point}"
            )
        for field, expected in (
            ("cue_index", condition["cue_index"]),
            ("valid_change_index", condition["valid_change_index"]),
            ("invalid_change_index", condition["invalid_change_index"]),
            ("cue_color", condition["cue_color"]),
            ("qualifying_response_frame", 5),
            ("change_present", True),
            ("timesteps", 7),
            ("model_width", 128),
        ):
            actual = _npz_scalar(payload, field)
            if actual != expected:
                raise ValueError(f"psychometric cache {field} is {actual!r}, expected {expected!r}")
        np.testing.assert_allclose(
            np.asarray(payload["change_magnitudes"], dtype=np.float64),
            CHANGE_MAGNITUDES,
        )
        np.testing.assert_allclose(
            np.asarray(payload["displayed_validities"], dtype=np.float64),
            DISPLAYED_VALIDITIES,
        )
        shape = (len(DISPLAYED_VALIDITIES), len(CHANGE_MAGNITUDES))
        valid_count = np.asarray(payload["response_count_valid"])
        invalid_count = np.asarray(payload["response_count_invalid"])
        valid_rate = np.asarray(payload["response_rate_valid"], dtype=np.float64)
        invalid_rate = np.asarray(payload["response_rate_invalid"], dtype=np.float64)
        for name, values in (
            ("response_count_valid", valid_count),
            ("response_count_invalid", invalid_count),
            ("response_rate_valid", valid_rate),
            ("response_rate_invalid", invalid_rate),
        ):
            if values.shape != shape:
                raise ValueError(f"{name} has shape {values.shape}, expected {shape}")
        if not np.issubdtype(valid_count.dtype, np.integer) or not np.issubdtype(invalid_count.dtype, np.integer):
            raise ValueError("psychometric response counts must be integer arrays")
        if np.any(valid_count < 0) or np.any(valid_count > trials) or np.any(invalid_count < 0) or np.any(invalid_count > trials):
            raise ValueError("psychometric response counts must lie between zero and trials_per_point")
        np.testing.assert_allclose(valid_rate, valid_count / trials, rtol=0.0, atol=1e-12)
        np.testing.assert_allclose(invalid_rate, invalid_count / trials, rtol=0.0, atol=1e-12)
        seed = _npz_integer_scalar(payload, "seed")
        if expected_seed is not None and seed != expected_seed:
            raise ValueError(f"psychometric cache seed is {seed}, expected {expected_seed}")
        point_seeds = np.asarray(payload["point_seeds"], dtype=np.int64)
        expected_seeds = np.tile(
            seed + np.arange(len(CHANGE_MAGNITUDES), dtype=np.int64) * 101,
            (len(DISPLAYED_VALIDITIES), 1),
        )
        np.testing.assert_array_equal(point_seeds, expected_seeds)
        seed_policy = str(_npz_scalar(payload, "seed_policy"))
        expected_policy = (
            "common random numbers matched across displayed cue proportions and "
            "valid/invalid locations at each magnitude"
        )
        if seed_policy != expected_policy:
            raise ValueError(f"psychometric seed policy is {seed_policy!r}, expected {expected_policy!r}")
        metadata.update({
            "trials_per_point": trials,
            "seed": seed,
            "seed_policy": seed_policy,
            "cache_sha256": cache_sha256,
        })
        return metadata


def build_attention_figure(
    cache_path: str | Path,
    output_dir: str | Path,
    *,
    expected_cache_sha256: str | None = None,
) -> FigureOutputs:
    """Plot one cached attention tensor as N query rows by seven time columns."""
    cache_path = Path(cache_path)
    cache_bytes, cache_sha256 = _frozen_cache_bytes(cache_path, expected_cache_sha256)
    validated_cache = validate_attention_cache(cache_path, expected_cache_sha256=cache_sha256)
    with np.load(io.BytesIO(cache_bytes), allow_pickle=False) as payload:
        task = str(_npz_scalar(payload, "task"))
        feedback = str(_npz_scalar(payload, "feedback"))
        iteration = _npz_integer_scalar(payload, "checkpoint_iteration")
        trials = _npz_integer_scalar(payload, "trials")
        spatial = np.asarray(payload["spatial_attention"], dtype=np.float64)
        raw = np.asarray(payload["raw_attention_mean"], dtype=np.float64)
        spatial_trials = (
            np.asarray(payload["spatial_attention_trials"], dtype=np.float64)
            if "spatial_attention_trials" in payload.files
            else None
        )
    spec = first_wave_spec(task)
    if feedback not in FIRST_WAVE_FEEDBACK:
        raise ValueError(f"unknown feedback family {feedback!r}")
    expected = (7, spec.token_count, spec.token_count)
    if spatial.shape != expected:
        raise ValueError(f"spatial attention has shape {spatial.shape}, expected {expected}")
    if not np.isfinite(spatial).all():
        raise ValueError("spatial attention must contain only finite values")
    np.testing.assert_allclose(
        spatial,
        spatial_attention_maps(raw, feedback=feedback),
        rtol=1e-6,
        atol=1e-7,
    )
    if spatial_trials is not None:
        expected_trials = (trials,) + expected
        if spatial_trials.shape != expected_trials:
            raise ValueError(
                f"trial-level spatial attention has shape {spatial_trials.shape}, expected {expected_trials}"
            )
        np.testing.assert_allclose(spatial, spatial_trials.mean(axis=0), rtol=1e-5, atol=1e-6)

    mean_attention_to_s1 = spatial[:, :, spec.cue_index].mean(axis=1)
    cue_onset_delta = float(mean_attention_to_s1[1] - mean_attention_to_s1[0])
    change_onset_delta = float(mean_attention_to_s1[5] - mean_attention_to_s1[4])

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"first_wave_attention_{task}_{feedback}"
    outputs = FigureOutputs(
        pdf=output_dir / f"{stem}.pdf",
        svg=output_dir / f"{stem}.svg",
        png=output_dir / f"{stem}.png",
        metadata=output_dir / f"{stem}.json",
    )

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    })
    nrows, ncols = spec.token_count, 7
    figure, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(14.5, 2.0 + 1.65 * nrows),
        constrained_layout=True,
        squeeze=False,
    )
    observed_max = float(spatial.max())
    vmax = 1.0
    column_titles = (
        "t0 · blank",
        "t1 · cue at S1",
        "t2 · delay",
        "t3 · array",
        "t4 · maintain",
        "t5 · change at S1",
        "t6 · response",
    )
    image = None
    for query in range(nrows):
        for timestep in range(ncols):
            axis = axes[query, timestep]
            location_map = spatial[timestep, query].reshape(spec.grid)
            image = axis.imshow(location_map, cmap="cividis", vmin=0.0, vmax=vmax, interpolation="nearest")
            axis.set_xticks([])
            axis.set_yticks([])
            if query == 0:
                axis.set_title(column_titles[timestep], fontsize=9.2)
            if timestep == 0:
                axis.set_ylabel(
                    f"query {_location_label(query, spec)}",
                    fontsize=9.2,
                    rotation=0,
                    ha="right",
                    va="center",
                )
            border = "#009E73" if timestep == 1 else ("#D55E00" if timestep == 5 else "#B0B0B0")
            axis.add_patch(plt.Rectangle((-0.48, -0.48), 0.96, 0.96, fill=False, edgecolor=border, linewidth=1.7))
    assert image is not None
    figure.colorbar(
        image,
        ax=axes,
        location="right",
        shrink=0.62,
        pad=0.015,
        label="attention mass to spatial key",
    )
    figure.suptitle(
        f"{task.upper()} {spec.grid[0]}×{spec.grid[1]} · {feedback} · red cue and valid change at S1",
        fontsize=14,
        fontweight="bold",
    )
    reduction_note = attention_reduction_note(feedback)
    figure.supxlabel(
        f"Rows preserve query patches; columns are logical timesteps. S1 is bordered at every time. "
        f"Green marks cue onset and orange marks change onset. {reduction_note} "
        f"Uniform attention = {1.0 / spec.token_count:.3f}.",
        fontsize=9.5,
    )
    figure.savefig(outputs.pdf, bbox_inches="tight")
    figure.savefig(outputs.svg, bbox_inches="tight")
    figure.savefig(outputs.png, dpi=300, bbox_inches="tight")
    plt.close(figure)

    condition = attention_condition(task)
    metadata = {
        "schema_version": 1,
        "artifact": "first-wave spatial attention map",
        "task": task,
        "feedback": feedback,
        "grid": list(spec.grid),
        "token_count": spec.token_count,
        "figure_rows": nrows,
        "figure_columns": ncols,
        "row_semantics": "query patch",
        "column_semantics": "logical timestep",
        "cue_index": condition["cue_index"],
        "change_index": condition["change_index"],
        "displayed_validity": condition["displayed_validity"],
        "cue_color": condition["cue_color"],
        "change_frame": condition["change_frame"],
        "change_magnitude_degrees": condition["change_magnitude_degrees"],
        "checkpoint_iteration": iteration,
        "checkpoint_path": validated_cache["checkpoint_path"],
        "checkpoint_sha256": validated_cache["checkpoint_sha256"],
        "producer_sha256": validated_cache["producer_sha256"],
        "dependency_hashes": validated_cache["dependency_hashes"],
        "runtime_versions": validated_cache["runtime_versions"],
        "device": validated_cache["device"],
        "evaluation_trials": trials,
        "observed_max_attention_mass": observed_max,
        "color_scale": [0.0, 1.0],
        "uniform_attention_baseline": 1.0 / spec.token_count,
        "mean_attention_to_s1_by_timestep": mean_attention_to_s1.tolist(),
        "descriptive_s1_delta_cue_minus_blank": cue_onset_delta,
        "descriptive_s1_delta_change_minus_maintenance": change_onset_delta,
        "trial_level_attention_saved": spatial_trials is not None,
        "source_cache": str(cache_path.resolve()),
        "source_cache_sha256": cache_sha256,
        "spatial_collapse": reduction_note,
        "inference_boundary": "descriptive checkpoint attention; temporal changes do not by themselves establish causal cue modulation",
        "outputs": {"pdf": outputs.pdf.name, "svg": outputs.svg.name, "png": outputs.png.name},
    }
    _frozen_cache_bytes(cache_path, cache_sha256)
    outputs.metadata.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    _frozen_cache_bytes(cache_path, cache_sha256)
    return outputs


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalized_npz_path(path: str | Path) -> Path:
    output_path = Path(path)
    if output_path.suffix != ".npz":
        output_path = Path(f"{output_path}.npz")
    return output_path


def compute_attention_cache(
    task: str,
    feedback: str,
    output_path: str | Path,
    *,
    width: int = 128,
    trials: int = 96,
    seed: int = 1701,
    checkpoint_path: str | Path | None = None,
    expected_checkpoint_sha256: str | None = None,
) -> Path:
    """Compute a checkpoint-verified attention cache for one focused condition."""
    if feedback not in FIRST_WAVE_FEEDBACK:
        raise ValueError(f"unknown feedback family {feedback!r}")
    spec = first_wave_spec(task)
    if trials <= 0:
        raise ValueError("trials must be positive")
    output_path = _normalized_npz_path(output_path)

    import torch
    from vda_sweep import vda_core as core

    checkpoint = Path(
        checkpoint_path if checkpoint_path is not None else core.ckpt(task, feedback, width)
    ).resolve()
    checkpoint_sha256 = _sha256(checkpoint)
    if expected_checkpoint_sha256 is not None and checkpoint_sha256 != expected_checkpoint_sha256:
        raise RuntimeError(
            f"selected checkpoint SHA-256 {checkpoint_sha256} does not match "
            f"expected {expected_checkpoint_sha256}"
        )
    model, iteration = core.load(task, feedback, width, checkpoint_path=str(checkpoint))
    condition = attention_condition(task)
    videos = core.make_video_batch(
        task,
        condition["cue_index"],
        condition["displayed_validity"],
        condition["cue_color"],
        1,
        condition["change_index"],
        condition["change_magnitude_degrees"],
        B=trials,
        seed=seed,
    )
    with torch.no_grad():
        raw_trials = (
            model.forward_rl_sequence(videos, return_attn=True)["attn_seq"]
            .detach()
            .cpu()
            .numpy()
        )
    raw = raw_trials.mean(axis=0)
    spatial_trials = spatial_attention_maps(raw_trials, feedback=feedback)
    spatial = spatial_attention_maps(raw, feedback=feedback)
    expected = (7, spec.token_count, spec.token_count)
    if spatial.shape != expected:
        raise RuntimeError(f"computed spatial attention has shape {spatial.shape}, expected {expected}")
    expected_trials = (trials,) + expected
    if spatial_trials.shape != expected_trials:
        raise RuntimeError(
            f"computed trial-level spatial attention has shape {spatial_trials.shape}, "
            f"expected {expected_trials}"
        )
    if _sha256(checkpoint) != checkpoint_sha256:
        raise RuntimeError("checkpoint changed during attention computation")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        raw_attention_trials=raw_trials.astype(np.float32),
        raw_attention_mean=raw.astype(np.float32),
        spatial_attention_trials=spatial_trials.astype(np.float32),
        spatial_attention=spatial.astype(np.float32),
        task=np.array(task),
        feedback=np.array(feedback),
        checkpoint_iteration=np.array(iteration, dtype=np.int64),
        checkpoint_path=np.array(str(checkpoint.resolve())),
        checkpoint_sha256=np.array(checkpoint_sha256),
        producer_path=np.array(str(Path(__file__).resolve())),
        producer_sha256=np.array(_sha256(Path(__file__))),
        dependency_hashes_json=np.array(_dependency_hashes_json()),
        runtime_versions_json=np.array(_runtime_versions_json()),
        device=np.array(str(core.DEVICE)),
        trials=np.array(trials, dtype=np.int64),
        seed=np.array(seed, dtype=np.int64),
        cue_index=np.array(condition["cue_index"], dtype=np.int64),
        change_index=np.array(condition["change_index"], dtype=np.int64),
        displayed_validity=np.array(condition["displayed_validity"], dtype=np.float64),
        cue_color=np.array(condition["cue_color"]),
        change_magnitude_degrees=np.array(condition["change_magnitude_degrees"], dtype=np.float64),
        change_frame=np.array(condition["change_frame"], dtype=np.int64),
        change_present=np.array(condition["change_present"]),
        timesteps=np.array(condition["timesteps"], dtype=np.int64),
        model_width=np.array(width, dtype=np.int64),
        grid=np.array(spec.grid, dtype=np.int64),
    )
    return output_path


def psychometric_conditions(task: str) -> dict[str, Any]:
    spec = first_wave_spec(task)
    return {
        "cue_index": spec.cue_index,
        "valid_change_index": spec.cue_index,
        "invalid_change_index": spec.invalid_change_index,
        "cue_color": "red",
    }


def _wilson_interval(counts: np.ndarray, trials: int, z: float = 1.96) -> tuple[np.ndarray, np.ndarray]:
    counts = np.asarray(counts, dtype=np.float64)
    proportion = counts / trials
    denominator = 1.0 + z * z / trials
    center = (proportion + z * z / (2.0 * trials)) / denominator
    half = z * np.sqrt(proportion * (1.0 - proportion) / trials + z * z / (4.0 * trials * trials)) / denominator
    return center - half, center + half


def build_psychometric_figure(
    cache_path: str | Path,
    output_dir: str | Path,
    *,
    expected_cache_sha256: str | None = None,
) -> FigureOutputs:
    """Render the three requested response-rate panels from one fresh cache."""
    cache_path = Path(cache_path)
    cache_bytes, cache_sha256 = _frozen_cache_bytes(cache_path, expected_cache_sha256)
    validated_cache = validate_psychometric_cache(cache_path, expected_cache_sha256=cache_sha256)
    with np.load(io.BytesIO(cache_bytes), allow_pickle=False) as payload:
        task = str(_npz_scalar(payload, "task"))
        feedback = str(_npz_scalar(payload, "feedback"))
        iteration = _npz_integer_scalar(payload, "checkpoint_iteration")
        trials = _npz_integer_scalar(payload, "trials_per_point")
        cue_index = _npz_integer_scalar(payload, "cue_index")
        valid_index = _npz_integer_scalar(payload, "valid_change_index")
        invalid_index = _npz_integer_scalar(payload, "invalid_change_index")
        seed_policy = (
            str(_npz_scalar(payload, "seed_policy"))
            if "seed_policy" in payload.files
            else "not recorded"
        )
        cue_color = str(_npz_scalar(payload, "cue_color"))
        magnitudes = np.asarray(payload["change_magnitudes"], dtype=np.float64)
        validities = np.asarray(payload["displayed_validities"], dtype=np.float64)
        valid_rate = np.asarray(payload["response_rate_valid"], dtype=np.float64)
        invalid_rate = np.asarray(payload["response_rate_invalid"], dtype=np.float64)
        valid_count = np.asarray(payload["response_count_valid"], dtype=np.int64)
        invalid_count = np.asarray(payload["response_count_invalid"], dtype=np.int64)
    spec = first_wave_spec(task)
    if feedback not in FIRST_WAVE_FEEDBACK:
        raise ValueError(f"unknown feedback family {feedback!r}")
    expected = (len(validities), len(magnitudes))
    for name, array in {
        "response_rate_valid": valid_rate,
        "response_rate_invalid": invalid_rate,
        "response_count_valid": valid_count,
        "response_count_invalid": invalid_count,
    }.items():
        if array.shape != expected:
            raise ValueError(f"{name} has shape {array.shape}, expected {expected}")
    if cue_index != 0 or valid_index != 0 or invalid_index != spec.invalid_change_index:
        raise ValueError("psychometric cache location semantics do not match the first-wave specification")
    np.testing.assert_allclose(valid_rate, valid_count / trials, atol=0.5 / trials)
    np.testing.assert_allclose(invalid_rate, invalid_count / trials, atol=0.5 / trials)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"first_wave_psychometric_{task}_{feedback}"
    outputs = FigureOutputs(
        pdf=output_dir / f"{stem}.pdf",
        svg=output_dir / f"{stem}.svg",
        png=output_dir / f"{stem}.png",
        metadata=output_dir / f"{stem}.json",
    )

    colors = ("#0072B2", "#009E73", "#E69F00", "#CC79A7")
    markers = ("o", "s", "^", "D")
    line_styles = ("-", "--", "-.", ":")
    figure, axes = plt.subplots(1, 3, figsize=(15.4, 4.8), constrained_layout=True, sharex=True, sharey=True)
    for index, validity in enumerate(validities):
        label = f"{int(round(100 * validity))}% displayed"
        for axis, rate, count in (
            (axes[0], valid_rate[index], valid_count[index]),
            (axes[1], invalid_rate[index], invalid_count[index]),
        ):
            lower, upper = _wilson_interval(count, trials)
            axis.fill_between(magnitudes, lower, upper, color=colors[index], alpha=0.11, linewidth=0)
            axis.plot(
                magnitudes,
                rate,
                marker=markers[index],
                linestyle=line_styles[index],
                markersize=4,
                linewidth=2,
                color=colors[index],
                label=label,
            )

    hundred = int(np.flatnonzero(np.isclose(validities, 1.0))[0])
    for label, rate, count, color, marker in (
        ("valid change at S1", valid_rate[hundred], valid_count[hundred], "#0072B2", "o"),
        ("invalid change at bottom-right", invalid_rate[hundred], invalid_count[hundred], "#D55E00", "s"),
    ):
        lower, upper = _wilson_interval(count, trials)
        axes[2].fill_between(magnitudes, lower, upper, color=color, alpha=0.12, linewidth=0)
        axes[2].plot(magnitudes, rate, marker=marker, markersize=4.5, linewidth=2.2, color=color, label=label)

    titles = (
        "A  Valid: cue S1 → change S1",
        f"B  Invalid: cue S1 → change S{invalid_index + 1}",
        "C  100% displayed validity · forced locations",
    )
    for axis, title in zip(axes, titles):
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_ylim(-0.02, 1.02)
        axis.set_xticks(magnitudes)
        axis.grid(alpha=0.18, linewidth=0.6)
        axis.set_xlabel("orientation change (degrees)")
    axes[0].set_ylabel("P(qualifying change response)\n(frame ≥5; all trials in denominator)")
    axes[0].legend(title="cue proportion", frameon=False, fontsize=8.5)
    axes[2].legend(frameon=False, fontsize=8.5)
    figure.suptitle(
        f"{task.upper()} {spec.grid[0]}×{spec.grid[1]} · {feedback} · red cue at S1 · n={trials} trials/point\n"
        "Bands are Wilson 95% evaluation-trial intervals from one checkpoint; they are not training-seed uncertainty.",
        fontsize=13.5,
        fontweight="bold",
    )
    figure.savefig(outputs.pdf, bbox_inches="tight")
    figure.savefig(outputs.svg, bbox_inches="tight")
    figure.savefig(outputs.png, dpi=300, bbox_inches="tight")
    plt.close(figure)

    panels = [
        "all cue proportions: valid change at S1",
        "all cue proportions: invalid change at bottom-right",
        "100% displayed validity: forced valid versus forced invalid change",
    ]
    metadata = {
        "schema_version": 1,
        "artifact": "first-wave psychometric response-rate curves",
        "task": task,
        "feedback": feedback,
        "grid": list(spec.grid),
        "panel_count": 3,
        "panels": panels,
        "forced_location_intervention": True,
        "condition_boundary": "the invalid curve at 100% displayed validity is forced and is not naturally sampled under the task policy",
        "cue_color": cue_color,
        "cue_index": cue_index,
        "valid_change_index": valid_index,
        "invalid_change_index": invalid_index,
        "displayed_validities": validities.tolist(),
        "change_magnitudes_degrees": magnitudes.tolist(),
        "checkpoint_iteration": iteration,
        "checkpoint_path": validated_cache["checkpoint_path"],
        "checkpoint_sha256": validated_cache["checkpoint_sha256"],
        "producer_sha256": validated_cache["producer_sha256"],
        "dependency_hashes": validated_cache["dependency_hashes"],
        "runtime_versions": validated_cache["runtime_versions"],
        "device": validated_cache["device"],
        "trials_per_point": trials,
        "interval": "Wilson 95% binomial interval",
        "response_definition": "first change declaration at logical frame 5 or later; all evaluation trials form the denominator",
        "uncertainty_boundary": "evaluation-trial binomial interval for one checkpoint; not independent training-seed uncertainty",
        "seed_policy": seed_policy,
        "source_cache": str(cache_path.resolve()),
        "source_cache_sha256": cache_sha256,
        "outputs": {"pdf": outputs.pdf.name, "svg": outputs.svg.name, "png": outputs.png.name},
    }
    _frozen_cache_bytes(cache_path, cache_sha256)
    outputs.metadata.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    _frozen_cache_bytes(cache_path, cache_sha256)
    return outputs


def compute_psychometric_cache(
    task: str,
    feedback: str,
    output_path: str | Path,
    *,
    width: int = 128,
    trials_per_point: int = 300,
    seed: int = 2801,
    checkpoint_path: str | Path | None = None,
    expected_checkpoint_sha256: str | None = None,
) -> Path:
    """Compute focused valid/opposite-corner response rates from one checkpoint."""
    if feedback not in FIRST_WAVE_FEEDBACK:
        raise ValueError(f"unknown feedback family {feedback!r}")
    if trials_per_point <= 0:
        raise ValueError("trials_per_point must be positive")
    output_path = _normalized_npz_path(output_path)
    spec = first_wave_spec(task)
    condition = psychometric_conditions(task)

    from vda_sweep import vda_core as core

    checkpoint = Path(
        checkpoint_path if checkpoint_path is not None else core.ckpt(task, feedback, width)
    ).resolve()
    checkpoint_sha256 = _sha256(checkpoint)
    if expected_checkpoint_sha256 is not None and checkpoint_sha256 != expected_checkpoint_sha256:
        raise RuntimeError(
            f"selected checkpoint SHA-256 {checkpoint_sha256} does not match "
            f"expected {expected_checkpoint_sha256}"
        )
    model, iteration = core.load(task, feedback, width, checkpoint_path=str(checkpoint))
    shape = (len(DISPLAYED_VALIDITIES), len(CHANGE_MAGNITUDES))
    valid_count = np.zeros(shape, dtype=np.int64)
    invalid_count = np.zeros(shape, dtype=np.int64)
    seeds = np.zeros(shape, dtype=np.int64)

    for validity_index, displayed_validity in enumerate(DISPLAYED_VALIDITIES):
        for magnitude_index, magnitude in enumerate(CHANGE_MAGNITUDES):
            # Reuse the same latent trial stream across cue proportions and
            # valid/invalid locations so visual differences are controlled.
            point_seed = seed + magnitude_index * 101
            seeds[validity_index, magnitude_index] = point_seed
            for location, counts in (
                (condition["valid_change_index"], valid_count),
                (condition["invalid_change_index"], invalid_count),
            ):
                videos = core.make_video_batch(
                    task,
                    condition["cue_index"],
                    float(displayed_validity),
                    condition["cue_color"],
                    1,
                    location,
                    float(magnitude),
                    B=trials_per_point,
                    seed=int(point_seed),
                )
                responses = core.press_times_clamp(
                    model,
                    task,
                    condition["cue_index"],
                    float(displayed_validity),
                    condition["cue_color"],
                    1,
                    location,
                    float(magnitude),
                    videos=videos,
                )
                counts[validity_index, magnitude_index] = int(np.count_nonzero(responses >= 5))

    if _sha256(checkpoint) != checkpoint_sha256:
        raise RuntimeError("checkpoint changed during psychometric computation")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        response_rate_valid=valid_count / trials_per_point,
        response_rate_invalid=invalid_count / trials_per_point,
        response_count_valid=valid_count,
        response_count_invalid=invalid_count,
        change_magnitudes=CHANGE_MAGNITUDES,
        displayed_validities=DISPLAYED_VALIDITIES,
        point_seeds=seeds,
        seed_policy=np.array(
            "common random numbers matched across displayed cue proportions and valid/invalid locations at each magnitude"
        ),
        task=np.array(task),
        feedback=np.array(feedback),
        checkpoint_iteration=np.array(iteration, dtype=np.int64),
        checkpoint_path=np.array(str(checkpoint.resolve())),
        checkpoint_sha256=np.array(checkpoint_sha256),
        producer_path=np.array(str(Path(__file__).resolve())),
        producer_sha256=np.array(_sha256(Path(__file__))),
        dependency_hashes_json=np.array(_dependency_hashes_json()),
        runtime_versions_json=np.array(_runtime_versions_json()),
        device=np.array(str(core.DEVICE)),
        trials_per_point=np.array(trials_per_point, dtype=np.int64),
        seed=np.array(seed, dtype=np.int64),
        cue_index=np.array(condition["cue_index"], dtype=np.int64),
        valid_change_index=np.array(condition["valid_change_index"], dtype=np.int64),
        invalid_change_index=np.array(condition["invalid_change_index"], dtype=np.int64),
        cue_color=np.array(condition["cue_color"]),
        qualifying_response_frame=np.array(5, dtype=np.int64),
        change_present=np.array(True),
        timesteps=np.array(7, dtype=np.int64),
        model_width=np.array(width, dtype=np.int64),
        grid=np.array(spec.grid, dtype=np.int64),
    )
    return output_path
