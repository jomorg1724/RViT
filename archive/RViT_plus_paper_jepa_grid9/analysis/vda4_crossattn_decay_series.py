#!/usr/bin/env python3
"""Three-checkpoint VDA4 cross-attention memory-decay comparison.

This producer extends the established two-checkpoint analysis to completed no-decay
(lambda=1.0), light-decay (lambda=0.8), and heavy-decay (lambda=0.5) checkpoints.
All models receive common deterministic CPU-generated trials. The primary attention
motion descriptor is frame-to-frame total variation over every 4x8 attention row.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import tempfile
from typing import Any

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from analysis import vda4_decay_comparison as base  # noqa: E402


MODEL_ROLES = ("no_decay", "light_decay", "heavy_decay")
MODEL_DECAYS = np.array([1.0, 0.8, 0.5], dtype=np.float64)
MODEL_LABELS = ("No decay λ=1.0", "Light decay λ=0.8", "Heavy decay λ=0.5")
MODEL_SHORT_LABELS = ("No decay", "Light decay", "Heavy decay")
MODEL_COLORS = ("#0072B2", "#E69F00", "#CC79A7")
PAIR_SPECS = (
    ("light_minus_no", 1, 0, "Light − no decay"),
    ("heavy_minus_no", 2, 0, "Heavy − no decay"),
    ("heavy_minus_light", 2, 1, "Heavy − light decay"),
)
EVENT_CONDITIONS = base.EVENT_CONDITIONS
DISPLAYED_VALIDITIES = base.DISPLAYED_VALIDITIES
CHANGE_MAGNITUDES = base.CHANGE_MAGNITUDES
TIMESTEPS = base.TIMESTEPS
QUERY_COUNT = base.QUERY_COUNT
KEY_COUNT = base.KEY_COUNT
CUE_INDEX = base.CUE_INDEX
VALID_CHANGE_INDEX = base.VALID_CHANGE_INDEX
INVALID_CHANGE_INDEX = base.INVALID_CHANGE_INDEX
EVENT_MAGNITUDE = base.EVENT_MAGNITUDE
EVENT_DISPLAYED_VALIDITY = base.EVENT_DISPLAYED_VALIDITY
QUALIFYING_RESPONSE_FRAME = base.QUALIFYING_RESPONSE_FRAME
SOURCE_DEPENDENCIES = base.SOURCE_DEPENDENCIES
FIGURE_STEMS = (
    "attention_event_query_averaged",
    "attention_query_level_valid_image_keys",
    "attention_query_level_valid_memory_keys",
    "attention_query_level_forced_invalid_image_keys",
    "attention_query_level_forced_invalid_memory_keys",
    "attention_nochange_image_keys",
    "attention_nochange_memory_keys",
    "attention_metrics_and_response_strata",
    "psychometric_valid_invalid_comparison",
    "psychometric_pairwise_differences",
)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_path(path: str | Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def _write_json_exclusive(path: Path, payload: Any) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite JSON artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def resolved_model_kwargs(checkpoint: dict, *, role: str) -> dict:
    """Validate the common model contract and role-specific decay."""
    if role not in MODEL_ROLES:
        raise ValueError(f"role must be one of {MODEL_ROLES}; got {role!r}")
    if checkpoint.get("task") != "vda4":
        raise ValueError(f"task must be 'vda4'; got {checkpoint.get('task')!r}")
    kwargs = dict(checkpoint.get("model_kwargs") or {})
    for field, expected in base.MODEL_CONTRACT.items():
        if kwargs.get(field) != expected:
            raise ValueError(f"{field} must be {expected!r}; got {kwargs.get(field)!r}")
    resolved_decay = float(kwargs.get("memory_decay", 1.0))
    expected_decay = float(MODEL_DECAYS[MODEL_ROLES.index(role)])
    if resolved_decay != expected_decay:
        raise ValueError(
            f"memory_decay must resolve to {expected_decay} for {role}; got {resolved_decay}"
        )
    kwargs["memory_decay"] = resolved_decay
    return kwargs


def _freeze_checkpoint(source: Path, destination: Path, *, role: str) -> dict[str, Any]:
    source = source.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"checkpoint does not exist: {source}")
    content = source.read_bytes()
    source_sha = sha256_bytes(content)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"frozen checkpoint already exists: {destination}")
    destination.write_bytes(content)
    if destination.read_bytes() != content or sha256_path(destination) != source_sha:
        raise RuntimeError(f"checkpoint freeze verification failed: {source}")

    import torch

    checkpoint = torch.load(io.BytesIO(content), map_location="cpu", weights_only=False)
    kwargs = resolved_model_kwargs(checkpoint, role=role)
    iteration = int(checkpoint["iter"])
    environment_state = checkpoint.get("environment_state") or {}
    training_args = checkpoint.get("training_args") or {}
    resume_contract = checkpoint.get("resume_contract") or {}
    return {
        "role": role,
        "source_path": str(source),
        "snapshot_path": str(destination.resolve()),
        "bytes": len(content),
        "sha256": source_sha,
        "checkpoint_iteration": iteration,
        "checkpoint_task": checkpoint.get("task"),
        "checkpoint_schema_version": checkpoint.get("checkpoint_schema_version"),
        "resolved_memory_decay": float(kwargs["memory_decay"]),
        "training_seed": training_args.get("seed"),
        "curriculum_theta": environment_state.get("theta"),
        "schedule_final_iteration": resume_contract.get("schedule_final_iteration"),
        "resume_fidelity": checkpoint.get("resume_fidelity"),
        "replay_buffer_persisted": checkpoint.get("replay_buffer_persisted"),
        "resume_compatibility_transition": checkpoint.get(
            "resume_compatibility_transition"
        ),
        "parent_checkpoint_sha256": checkpoint.get("parent_checkpoint_sha256"),
        "model_kwargs": kwargs,
    }


def freeze_inputs(
    run_root: Path,
    *,
    no_decay_checkpoint: Path,
    light_decay_checkpoint: Path,
    heavy_decay_checkpoint: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    sources = {
        "no_decay": no_decay_checkpoint,
        "light_decay": light_decay_checkpoint,
        "heavy_decay": heavy_decay_checkpoint,
    }
    records = []
    for role in MODEL_ROLES:
        destination = run_root / "snapshots" / f"{role}.pt"
        records.append(_freeze_checkpoint(sources[role], destination, role=role))
    manifest = {
        "schema_version": 2,
        "status": "frozen_inputs_only",
        "comparison": "VDA4 crossattn1 no/light/heavy carried-cell memory decay series",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": run_root.name,
        "checkpoints": records,
    }
    _write_json_exclusive(run_root / "frozen_inputs.json", manifest)
    return manifest, {record["role"]: record for record in records}


def capture_executable_sources() -> dict[str, bytes]:
    paths = {
        "analysis/vda4_crossattn_decay_series.py": Path(__file__).resolve(),
        "analysis/vda4_decay_comparison.py": Path(base.__file__).resolve(),
    }
    paths.update({relative: PROJECT_ROOT / relative for relative in SOURCE_DEPENDENCIES})
    return {relative: path.read_bytes() for relative, path in paths.items()}


def assert_sources_unchanged(captured: dict[str, bytes]) -> None:
    for relative, expected in captured.items():
        path = PROJECT_ROOT / relative
        if path.read_bytes() != expected:
            raise RuntimeError(f"executable source changed during analysis: {path}")


def _scalar(payload: Any, field: str) -> Any:
    value = np.asarray(payload[field])
    if value.ndim != 0:
        raise ValueError(f"cache field {field!r} must be scalar")
    return value.item()


def validate_comparison_cache(
    cache_path: Path,
    *,
    expected_attention_trials: int | None = None,
    expected_nochange_trials: int | None = None,
    expected_psychometric_trials: int | None = None,
) -> dict[str, Any]:
    """Fail closed on the three-model cache schema, reductions, and lineage."""
    content = cache_path.read_bytes()
    with np.load(io.BytesIO(content), allow_pickle=False) as payload:
        np.testing.assert_array_equal(payload["model_roles"], np.asarray(MODEL_ROLES))
        np.testing.assert_array_equal(payload["event_conditions"], np.asarray(EVENT_CONDITIONS))
        np.testing.assert_allclose(payload["displayed_validities"], DISPLAYED_VALIDITIES)
        np.testing.assert_allclose(payload["change_magnitudes"], CHANGE_MAGNITUDES)
        np.testing.assert_allclose(payload["resolved_memory_decay"], MODEL_DECAYS)
        attention_trials = int(_scalar(payload, "attention_trials"))
        nochange_trials = int(_scalar(payload, "nochange_trials"))
        psychometric_trials = int(_scalar(payload, "psychometric_trials"))
        for actual, expected, label in (
            (attention_trials, expected_attention_trials, "attention_trials"),
            (nochange_trials, expected_nochange_trials, "nochange_trials"),
            (psychometric_trials, expected_psychometric_trials, "psychometric_trials"),
        ):
            if actual <= 0 or (expected is not None and actual != expected):
                raise ValueError(f"cache {label}={actual}, expected {expected}")

        model_count = len(MODEL_ROLES)
        raw_event = np.asarray(payload["event_raw_attention"], dtype=np.float64)
        expected_event_shape = (
            model_count,
            len(EVENT_CONDITIONS),
            attention_trials,
            TIMESTEPS,
            QUERY_COUNT,
            KEY_COUNT,
        )
        if raw_event.shape != expected_event_shape:
            raise ValueError(f"event attention shape {raw_event.shape}, expected {expected_event_shape}")
        sources = base.source_resolved_attention(raw_event)
        np.testing.assert_allclose(payload["event_source_attention"], sources, rtol=1e-5, atol=1e-6)
        np.testing.assert_allclose(
            payload["event_query_averaged_attention"], sources.mean(axis=-3), rtol=1e-5, atol=1e-6
        )
        logits = np.asarray(payload["event_actor_logits"], dtype=np.float64)
        if logits.shape != (model_count, len(EVENT_CONDITIONS), attention_trials, TIMESTEPS, 2):
            raise ValueError(f"event actor-logit shape is invalid: {logits.shape}")
        stored_first = np.asarray(payload["event_first_press"], dtype=np.int64)
        stored_qualifying = np.asarray(payload["event_qualifying_response"], dtype=bool)
        metric_names = (
            "temporal_motion",
            "selectivity",
            "image_mass",
            "memory_mass",
            "peak_key_mass",
            "spatial_mass",
        )
        for model_index in range(model_count):
            for condition_index in range(len(EVENT_CONDITIONS)):
                first, qualifying = base.first_press_from_logits(
                    logits[model_index, condition_index],
                    qualifying_frame=QUALIFYING_RESPONSE_FRAME,
                )
                np.testing.assert_array_equal(stored_first[model_index, condition_index], first)
                np.testing.assert_array_equal(
                    stored_qualifying[model_index, condition_index], qualifying
                )
                metrics = base.attention_metrics(raw_event[model_index, condition_index])
                for name in metric_names:
                    np.testing.assert_allclose(
                        payload[f"event_{name}"][model_index, condition_index],
                        metrics[name],
                        rtol=1e-5,
                        atol=1e-6,
                    )

        raw_nochange = np.asarray(payload["nochange_raw_attention"], dtype=np.float64)
        expected_nochange_shape = (
            model_count,
            len(DISPLAYED_VALIDITIES),
            nochange_trials,
            TIMESTEPS,
            QUERY_COUNT,
            KEY_COUNT,
        )
        if raw_nochange.shape != expected_nochange_shape:
            raise ValueError(
                f"no-change attention shape {raw_nochange.shape}, expected {expected_nochange_shape}"
            )
        for model_index in range(model_count):
            for validity_index in range(len(DISPLAYED_VALIDITIES)):
                metrics = base.attention_metrics(raw_nochange[model_index, validity_index])
                for name in metric_names:
                    np.testing.assert_allclose(
                        payload[f"nochange_{name}"][model_index, validity_index],
                        metrics[name],
                        rtol=1e-5,
                        atol=1e-6,
                    )

        psych_count = np.asarray(payload["psychometric_response_count"], dtype=np.int64)
        psych_rate = np.asarray(payload["psychometric_response_rate"], dtype=np.float64)
        psych_histogram = np.asarray(payload["psychometric_press_histogram"], dtype=np.int64)
        psych_shape = (
            model_count,
            len(DISPLAYED_VALIDITIES),
            len(CHANGE_MAGNITUDES),
            len(EVENT_CONDITIONS),
        )
        if psych_count.shape != psych_shape or psych_rate.shape != psych_shape:
            raise ValueError("psychometric count/rate shapes do not satisfy the series contract")
        if psych_histogram.shape != psych_shape + (TIMESTEPS + 1,):
            raise ValueError("psychometric press-histogram shape is invalid")
        np.testing.assert_array_equal(psych_histogram.sum(axis=-1), psychometric_trials)
        np.testing.assert_array_equal(
            psych_count,
            psych_histogram[..., QUALIFYING_RESPONSE_FRAME + 1 :].sum(axis=-1),
        )
        np.testing.assert_allclose(
            psych_rate, psych_count / float(psychometric_trials), rtol=0.0, atol=1e-12
        )
        checkpoint_hashes = [str(value) for value in payload["checkpoint_sha256"].tolist()]
        checkpoint_iterations = [int(value) for value in payload["checkpoint_iterations"].tolist()]
        if len(checkpoint_hashes) != model_count or any(len(value) != 64 for value in checkpoint_hashes):
            raise ValueError("cache checkpoint hashes are malformed")
    return {
        "cache_path": str(cache_path.resolve()),
        "cache_sha256": sha256_bytes(content),
        "attention_trials": attention_trials,
        "nochange_trials": nochange_trials,
        "psychometric_trials": psychometric_trials,
        "checkpoint_iterations": checkpoint_iterations,
        "checkpoint_sha256": checkpoint_hashes,
        "device": "cpu",
    }


def _pairwise_estimates(values: np.ndarray, *, seed_base: int) -> dict[str, Any]:
    array = np.asarray(values, dtype=np.float64)
    if array.shape[0] != len(MODEL_ROLES):
        raise ValueError(f"model axis must have length {len(MODEL_ROLES)}; got {array.shape}")
    result = {
        "model_means": {
            role: float(array[index].mean()) for index, role in enumerate(MODEL_ROLES)
        },
        "pairwise": {},
    }
    for pair_index, (name, minuend, subtrahend, label) in enumerate(PAIR_SPECS):
        estimate = base.paired_mean_difference(
            array[minuend],
            array[subtrahend],
            seed=seed_base + pair_index * 97,
            bootstrap_samples=10_000,
        )
        estimate["label"] = label
        estimate["minuend_role"] = MODEL_ROLES[minuend]
        estimate["subtrahend_role"] = MODEL_ROLES[subtrahend]
        result["pairwise"][name] = estimate
    return result


def build_numeric_summary(payload: Any) -> dict[str, Any]:
    motion = np.asarray(payload["event_temporal_motion"], dtype=np.float64)
    selectivity = np.asarray(payload["event_selectivity"], dtype=np.float64)
    peak = np.asarray(payload["event_peak_key_mass"], dtype=np.float64)
    image_mass = np.asarray(payload["event_image_mass"], dtype=np.float64)
    spatial = np.asarray(payload["event_spatial_mass"], dtype=np.float64)
    nochange_motion = np.asarray(payload["nochange_temporal_motion"], dtype=np.float64)
    nochange_spatial = np.asarray(payload["nochange_spatial_mass"], dtype=np.float64)
    qualifying = np.asarray(payload["event_qualifying_response"], dtype=np.float64)

    metric_values: dict[str, np.ndarray] = {
        "primary_event_attention_motion": motion.mean(axis=(1, 3)),
        "event_selectivity": selectivity.mean(axis=(1, 3)),
        "event_peak_key_mass": peak.mean(axis=(1, 3)),
        "event_image_key_mass": image_mass.mean(axis=(1, 3)),
        "nochange_attention_motion": nochange_motion.mean(axis=(1, 3)),
        "cue_orienting_t1_minus_t0": (
            nochange_spatial[:, :, :, 1, CUE_INDEX]
            - nochange_spatial[:, :, :, 0, CUE_INDEX]
        ).mean(axis=1),
    }
    for condition_index, condition_name in enumerate(EVENT_CONDITIONS):
        location = VALID_CHANGE_INDEX if condition_index == 0 else INVALID_CHANGE_INDEX
        metric_values[f"{condition_name}_attention_motion"] = motion[
            :, condition_index
        ].mean(axis=2)
        metric_values[f"{condition_name}_change_reorientation_t5_minus_t4"] = (
            spatial[:, condition_index, :, 5, location]
            - spatial[:, condition_index, :, 4, location]
        )
        metric_values[f"{condition_name}_qualifying_response"] = qualifying[
            :, condition_index
        ]

    metrics = {
        name: _pairwise_estimates(values, seed_base=7300 + index * 313)
        for index, (name, values) in enumerate(metric_values.items())
    }
    primary_means = metrics["primary_event_attention_motion"]["model_means"]
    ordered = [primary_means[role] for role in MODEL_ROLES]
    if ordered[0] < ordered[1] < ordered[2]:
        order = "monotonic_increase_with_decay_strength"
    elif ordered[0] > ordered[1] > ordered[2]:
        order = "monotonic_decrease_with_decay_strength"
    else:
        order = "nonmonotonic"

    counts = np.asarray(payload["psychometric_response_count"], dtype=np.int64)
    rates = np.asarray(payload["psychometric_response_rate"], dtype=np.float64)
    validity_index = int(np.where(np.isclose(DISPLAYED_VALIDITIES, 1.0))[0][0])
    magnitude_index = int(np.where(np.isclose(CHANGE_MAGNITUDES, EVENT_MAGNITUDE))[0][0])
    anchor = {
        role: {
            condition: {
                "response_count": int(counts[model, validity_index, magnitude_index, cond]),
                "trials": int(_scalar(payload, "psychometric_trials")),
                "response_rate": float(rates[model, validity_index, magnitude_index, cond]),
            }
            for cond, condition in enumerate(EVENT_CONDITIONS)
        }
        for model, role in enumerate(MODEL_ROLES)
    }
    return {
        "schema_version": 2,
        "model_roles": list(MODEL_ROLES),
        "model_labels": list(MODEL_LABELS),
        "resolved_memory_decay": MODEL_DECAYS.tolist(),
        "checkpoint_iterations": [int(value) for value in payload["checkpoint_iterations"].tolist()],
        "checkpoint_sha256": [str(value) for value in payload["checkpoint_sha256"].tolist()],
        "primary_definition": (
            "Mean frame-to-frame total variation over the complete 4-query × 8-key "
            "cross-attention distribution, averaged within matched trials across valid and "
            "forced-invalid conditions, transitions, and query rows."
        ),
        "primary_order": order,
        "metrics": metrics,
        "psychometric_anchor_100pct_15deg": anchor,
        "event_condition": {
            "displayed_validity": EVENT_DISPLAYED_VALIDITY,
            "orientation_change_degrees": EVENT_MAGNITUDE,
            "cue_location": "S1",
            "valid_change_location": "S1",
            "forced_invalid_change_location": "S4",
            "attention_trials": int(_scalar(payload, "attention_trials")),
            "nochange_trials": int(_scalar(payload, "nochange_trials")),
            "psychometric_trials": int(_scalar(payload, "psychometric_trials")),
        },
        "interpretation_boundary": (
            "One completed checkpoint per decay setting and no between-seed replication; "
            "uncertainty intervals resample matched evaluation trials only. The no- and "
            "light-decay checkpoints are "
            "approximately iteration-matched near 20,000, whereas the heavy-decay checkpoint "
            "continued statefully to iteration 22,799 beyond its original schedule endpoint "
            "of 19,999. Its replay buffer was intentionally excluded from persisted trainer "
            "state and restarted empty; saturated schedules remained capped. Results are "
            "checkpoint comparisons, not a causal or population-level decay effect."
        ),
    }


def _save_figure(figure: Any, output_dir: Path, stem: str) -> None:
    base.configure_matplotlib_for_artifacts(sys.modules["matplotlib"])
    for suffix, kwargs in ((".pdf", {}), (".svg", {}), (".png", {"dpi": 240})):
        figure.savefig(output_dir / f"{stem}{suffix}", bbox_inches="tight", **kwargs)


def _draw_location_map(axis: Any, values: np.ndarray, *, vmax: float, cue: bool, change: int | None):
    return base._draw_location_map(
        axis,
        values,
        vmax=vmax,
        cue=cue,
        change_index=change,
    )


def _build_event_map_figure(payload: Any, output_dir: Path) -> None:
    import matplotlib.pyplot as plt

    maps = np.asarray(payload["event_query_averaged_attention"], dtype=np.float64).mean(axis=2)
    vmax = max(float(maps.max()), 1e-8)
    rows = [
        (model, condition, source)
        for model in range(len(MODEL_ROLES))
        for condition in range(len(EVENT_CONDITIONS))
        for source in range(2)
    ]
    figure, axes = plt.subplots(len(rows), TIMESTEPS, figsize=(14.8, 20.0))
    source_labels = ("image keys", "memory keys")
    condition_labels = ("valid S1 change", "forced-invalid S4 change")
    time_labels = ("t0 blank", "t1 cue", "t2 delay", "t3 array", "t4 maintain", "t5 change", "t6 response")
    image = None
    for row, (model, condition, source) in enumerate(rows):
        for timestep in range(TIMESTEPS):
            change = (
                VALID_CHANGE_INDEX if condition == 0 else INVALID_CHANGE_INDEX
            ) if timestep == 5 else None
            image = _draw_location_map(
                axes[row, timestep],
                maps[model, condition, timestep, source],
                vmax=vmax,
                cue=timestep == 1,
                change=change,
            )
            if row == 0:
                axes[row, timestep].set_title(time_labels[timestep], fontsize=8.5)
            if timestep == 0:
                axes[row, timestep].set_ylabel(
                    f"{MODEL_LABELS[model]}\n{condition_labels[condition]}\n{source_labels[source]}",
                    rotation=0,
                    ha="right",
                    va="center",
                    fontsize=7.4,
                )
    figure.subplots_adjust(left=0.22, right=0.92, top=0.96, bottom=0.035, wspace=0.06, hspace=0.12)
    figure.suptitle(
        "VDA4 event-locked cross-attention · query-averaged source maps · common scale",
        fontweight="bold",
    )
    figure.colorbar(image, ax=axes.ravel().tolist(), fraction=0.012, pad=0.015, label="attention mass")
    _save_figure(figure, output_dir, "attention_event_query_averaged")
    plt.close(figure)


def _build_query_level_figures(payload: Any, output_dir: Path) -> None:
    import matplotlib.pyplot as plt

    source_mean = np.asarray(payload["event_source_attention"], dtype=np.float64).mean(axis=2)
    vmax = max(float(source_mean.max()), 1e-8)
    row_count = 2 * QUERY_COUNT + 1
    column_count = 2 * TIMESTEPS
    placements = ((0, 0), (0, TIMESTEPS), (QUERY_COUNT + 1, 3))
    for condition, condition_name in enumerate(EVENT_CONDITIONS):
        for source, source_name in enumerate(("image_keys", "memory_keys")):
            figure, axes = plt.subplots(
                row_count,
                column_count,
                figsize=(18.0, 10.4),
            )
            for axis in axes.ravel():
                axis.set_visible(False)
            image = None
            visible_axes = []
            for model in range(len(MODEL_ROLES)):
                row_start, column_start = placements[model]
                for query in range(QUERY_COUNT):
                    for timestep in range(TIMESTEPS):
                        row = row_start + query
                        column = column_start + timestep
                        axis = axes[row, column]
                        axis.set_visible(True)
                        visible_axes.append(axis)
                        change = (
                            VALID_CHANGE_INDEX if condition == 0 else INVALID_CHANGE_INDEX
                        ) if timestep == 5 else None
                        image = _draw_location_map(
                            axis,
                            source_mean[model, condition, timestep, query, source],
                            vmax=vmax,
                            cue=timestep == 1,
                            change=change,
                        )
                        if query == 0:
                            axis.set_title(
                                f"t{timestep}",
                                fontsize=7.2,
                            )
                        if model in (0, 2) and timestep == 0:
                            axis.set_ylabel(
                                f"query S{query + 1}",
                                rotation=0,
                                ha="right",
                                va="center",
                                fontsize=8.0,
                            )
            figure.subplots_adjust(
                left=0.075,
                right=0.93,
                top=0.82,
                bottom=0.045,
                wspace=0.05,
                hspace=0.12,
            )
            figure.suptitle(
                f"VDA4 query-level {source_name.replace('_', ' ')} · {condition_name.replace('_', ' ')} · common scale",
                fontweight="bold",
                y=0.98,
            )
            figure.text(0.285, 0.875, MODEL_LABELS[0], ha="center", fontweight="bold")
            figure.text(0.715, 0.875, MODEL_LABELS[1], ha="center", fontweight="bold")
            figure.text(0.500, 0.455, MODEL_LABELS[2], ha="center", fontweight="bold")
            figure.colorbar(
                image,
                ax=visible_axes,
                fraction=0.012,
                pad=0.015,
                label="attention mass",
            )
            _save_figure(
                figure,
                output_dir,
                f"attention_query_level_{condition_name}_{source_name}",
            )
            plt.close(figure)


def _build_nochange_figures(payload: Any, output_dir: Path) -> None:
    import matplotlib.pyplot as plt

    raw = np.asarray(payload["nochange_raw_attention"], dtype=np.float64)
    source_maps = base.source_resolved_attention(raw).mean(axis=2).mean(axis=-3)
    vmax = max(float(source_maps.max()), 1e-8)
    row_count = len(MODEL_ROLES) * len(DISPLAYED_VALIDITIES)
    for source, source_name in enumerate(("image_keys", "memory_keys")):
        figure, axes = plt.subplots(row_count, TIMESTEPS, figsize=(14.8, 19.0))
        image = None
        for model in range(len(MODEL_ROLES)):
            for validity_index, validity in enumerate(DISPLAYED_VALIDITIES):
                row = model * len(DISPLAYED_VALIDITIES) + validity_index
                for timestep in range(TIMESTEPS):
                    image = _draw_location_map(
                        axes[row, timestep],
                        source_maps[model, validity_index, timestep, source],
                        vmax=vmax,
                        cue=timestep == 1,
                        change=None,
                    )
                    if row == 0:
                        axes[row, timestep].set_title(f"t{timestep}", fontsize=8.5)
                    if timestep == 0:
                        axes[row, timestep].set_ylabel(
                            f"{MODEL_LABELS[model]}\n{int(validity * 100)}% cue",
                            rotation=0,
                            ha="right",
                            va="center",
                            fontsize=7.3,
                        )
        figure.subplots_adjust(left=0.20, right=0.92, top=0.95, bottom=0.035, wspace=0.06, hspace=0.10)
        figure.suptitle(
            f"VDA4 no-change cue-proportion sweep · {source_name.replace('_', ' ')} · query-averaged · common scale",
            fontweight="bold",
        )
        figure.colorbar(image, ax=axes.ravel().tolist(), fraction=0.012, pad=0.015, label="attention mass")
        _save_figure(figure, output_dir, f"attention_nochange_{source_name}")
        plt.close(figure)


def _plot_trial_series(axis: Any, x: np.ndarray, values: np.ndarray, *, label: str, color: str, linestyle: str):
    mean, low, high = base._mean_interval(values)
    axis.plot(x, mean, color=color, linestyle=linestyle, linewidth=1.9, label=label)
    axis.fill_between(x, low, high, color=color, alpha=0.08, linewidth=0)


def _build_metric_figure(payload: Any, output_dir: Path, summary: dict[str, Any]) -> None:
    import matplotlib.pyplot as plt

    motion = np.asarray(payload["event_temporal_motion"], dtype=np.float64)
    selectivity = np.asarray(payload["event_selectivity"], dtype=np.float64)
    image_mass = np.asarray(payload["event_image_mass"], dtype=np.float64)
    spatial = np.asarray(payload["event_spatial_mass"], dtype=np.float64)
    qualifying = np.asarray(payload["event_qualifying_response"], dtype=bool)
    figure, axes = plt.subplots(2, 3, figsize=(15.2, 9.2), constrained_layout=True)
    line_styles = ("-", "--")
    condition_labels = ("valid", "forced invalid")
    for model in range(len(MODEL_ROLES)):
        for condition in range(len(EVENT_CONDITIONS)):
            label = f"{MODEL_SHORT_LABELS[model]} · {condition_labels[condition]}"
            for axis, x, values in (
                (axes[0, 0], np.arange(1, TIMESTEPS), motion[model, condition]),
                (axes[0, 1], np.arange(TIMESTEPS), selectivity[model, condition]),
                (axes[0, 2], np.arange(TIMESTEPS), image_mass[model, condition]),
                (axes[1, 0], np.arange(TIMESTEPS), spatial[model, condition, :, :, CUE_INDEX]),
                (
                    axes[1, 1],
                    np.arange(TIMESTEPS),
                    spatial[
                        model,
                        condition,
                        :,
                        :,
                        VALID_CHANGE_INDEX if condition == 0 else INVALID_CHANGE_INDEX,
                    ],
                ),
            ):
                _plot_trial_series(
                    axis,
                    x,
                    values,
                    label=label,
                    color=MODEL_COLORS[model],
                    linestyle=line_styles[condition],
                )
    for model in range(len(MODEL_ROLES)):
        for condition in range(len(EVENT_CONDITIONS)):
            location = VALID_CHANGE_INDEX if condition == 0 else INVALID_CHANGE_INDEX
            for responded, marker, alpha, suffix in (
                (True, "o", 1.0, "response"),
                (False, "s", 0.58, "no response"),
            ):
                mask = qualifying[model, condition] == responded
                if not np.any(mask):
                    continue
                values = spatial[model, condition, mask, :, location]
                axes[1, 2].plot(
                    np.arange(TIMESTEPS),
                    values.mean(axis=0),
                    color=MODEL_COLORS[model],
                    linestyle=line_styles[condition],
                    marker=marker,
                    markersize=2.8,
                    alpha=alpha,
                    label=f"{MODEL_SHORT_LABELS[model]} · {condition_labels[condition]} · {suffix} (n={mask.sum()})",
                )
    titles = (
        "A  Temporal attention motion (primary)",
        "B  Attention selectivity (1 − normalized entropy)",
        "C  Image-key source mass",
        "D  Combined attention to cued S1",
        "E  Combined attention to condition change location",
        "F  Change-location attention by qualifying response",
    )
    for axis, title in zip(axes.ravel(), titles):
        axis.set_title(title, loc="left", fontweight="bold")
        axis.grid(alpha=0.18)
        axis.axvline(5, color="0.5", linestyle=":", linewidth=1)
        axis.set_xlabel("logical frame" if axis is not axes[0, 0] else "transition ending at frame")
    for axis in axes.ravel():
        axis.set_ylabel("total variation" if axis is axes[0, 0] else "attention mass")
    axes[0, 1].set_ylabel("selectivity")
    axes[0, 0].legend(fontsize=6.5, frameon=False, ncol=2)
    axes[1, 2].legend(fontsize=5.1, frameon=False, ncol=2)
    primary = summary["metrics"]["primary_event_attention_motion"]
    light_no = primary["pairwise"]["light_minus_no"]
    heavy_no = primary["pairwise"]["heavy_minus_no"]
    figure.suptitle(
        "VDA4 cross-attention dynamics across carried-cell decay\n"
        f"motion: light−no {light_no['mean_difference']:+.4f}; heavy−no {heavy_no['mean_difference']:+.4f}",
        fontweight="bold",
    )
    _save_figure(figure, output_dir, "attention_metrics_and_response_strata")
    plt.close(figure)


def _build_psychometric_figures(payload: Any, output_dir: Path) -> None:
    import matplotlib.pyplot as plt

    counts = np.asarray(payload["psychometric_response_count"], dtype=np.int64)
    rates = np.asarray(payload["psychometric_response_rate"], dtype=np.float64)
    trials = int(_scalar(payload, "psychometric_trials"))
    condition_styles = ("-", "--")
    condition_markers = ("o", "s")
    figure, axes = plt.subplots(2, 2, figsize=(13.4, 9.5), constrained_layout=True)
    for validity_index, validity in enumerate(DISPLAYED_VALIDITIES):
        axis = axes.ravel()[validity_index]
        for model in range(len(MODEL_ROLES)):
            for condition in range(len(EVENT_CONDITIONS)):
                lower, upper = base._wilson_interval(
                    counts[model, validity_index, :, condition], trials
                )
                axis.fill_between(
                    CHANGE_MAGNITUDES,
                    lower,
                    upper,
                    color=MODEL_COLORS[model],
                    alpha=0.055,
                    linewidth=0,
                )
                axis.plot(
                    CHANGE_MAGNITUDES,
                    rates[model, validity_index, :, condition],
                    color=MODEL_COLORS[model],
                    linestyle=condition_styles[condition],
                    marker=condition_markers[condition],
                    markersize=3.2,
                    linewidth=1.7,
                    label=(
                        f"{MODEL_SHORT_LABELS[model]} · "
                        f"{'valid' if condition == 0 else 'forced invalid'}"
                    ),
                )
        axis.set_title(
            f"{chr(65 + validity_index)}  {int(validity * 100)}% displayed cue",
            loc="left",
            fontweight="bold",
        )
        axis.set_ylim(-0.02, 1.02)
        axis.set_xlabel("orientation change (degrees)")
        axis.set_ylabel("P(qualifying response)")
        axis.grid(alpha=0.18)
    axes[0, 0].legend(fontsize=6.5, frameon=False, ncol=2)
    figure.suptitle(
        f"VDA4 paired psychometrics · n={trials} shared trials/point · first press at frame ≥5 qualifies\n"
        "Wilson 95% evaluation-trial bands; forced-invalid curves are analysis interventions.",
        fontweight="bold",
    )
    _save_figure(figure, output_dir, "psychometric_valid_invalid_comparison")
    plt.close(figure)

    difference_figure, difference_axes = plt.subplots(2, 3, figsize=(14.5, 7.7), constrained_layout=True)
    images = []
    all_differences = [rates[right] - rates[left] for _, right, left, _ in PAIR_SPECS]
    vmax = max(float(np.max(np.abs(all_differences))), 1e-6)
    for column, (_, right, left, label) in enumerate(PAIR_SPECS):
        differences = rates[right] - rates[left]
        for condition in range(len(EVENT_CONDITIONS)):
            axis = difference_axes[condition, column]
            image = axis.imshow(
                differences[:, :, condition],
                aspect="auto",
                origin="lower",
                cmap="coolwarm",
                vmin=-vmax,
                vmax=vmax,
                interpolation="nearest",
            )
            images.append(image)
            axis.set_yticks(
                range(len(DISPLAYED_VALIDITIES)),
                [f"{int(value * 100)}%" for value in DISPLAYED_VALIDITIES],
            )
            axis.set_xticks(
                range(len(CHANGE_MAGNITUDES)),
                [str(int(value)) for value in CHANGE_MAGNITUDES],
                rotation=45,
            )
            axis.set_xlabel("orientation change (degrees)")
            axis.set_ylabel("displayed cue proportion")
            axis.set_title(
                f"{label}\n{'valid' if condition == 0 else 'forced invalid'}",
                fontweight="bold",
            )
    difference_figure.colorbar(
        images[-1],
        ax=difference_axes.ravel().tolist(),
        fraction=0.02,
        pad=0.02,
        label="response-rate difference",
    )
    difference_figure.suptitle(
        "Pairwise psychometric response-rate differences · one common diverging scale",
        fontweight="bold",
    )
    _save_figure(difference_figure, output_dir, "psychometric_pairwise_differences")
    plt.close(difference_figure)


def build_figures(payload: Any, output_dir: Path, summary: dict[str, Any]) -> None:
    import matplotlib

    base.configure_matplotlib_for_artifacts(matplotlib)
    output_dir.mkdir(parents=True, exist_ok=True)
    _build_event_map_figure(payload, output_dir)
    _build_query_level_figures(payload, output_dir)
    _build_nochange_figures(payload, output_dir)
    _build_metric_figure(payload, output_dir, summary)
    _build_psychometric_figures(payload, output_dir)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_tables(payload: Any, summary: dict[str, Any], output_dir: Path) -> None:
    metric_rows = []
    for metric, record in summary["metrics"].items():
        for pair_name, estimate in record["pairwise"].items():
            metric_rows.append(
                {
                    "metric": metric,
                    "pair": pair_name,
                    "pair_label": estimate["label"],
                    "no_decay_mean": f"{record['model_means']['no_decay']:.10g}",
                    "light_decay_mean": f"{record['model_means']['light_decay']:.10g}",
                    "heavy_decay_mean": f"{record['model_means']['heavy_decay']:.10g}",
                    "mean_difference": f"{estimate['mean_difference']:.10g}",
                    "paired_ci_low": f"{estimate['ci_low']:.10g}",
                    "paired_ci_high": f"{estimate['ci_high']:.10g}",
                    "paired_n": int(estimate["n"]),
                    "bootstrap_samples": int(estimate["bootstrap_samples"]),
                    "bootstrap_seed": int(estimate["seed"]),
                }
            )
    _write_csv(output_dir / "paired_attention_and_response_estimates.csv", metric_rows)

    counts = np.asarray(payload["psychometric_response_count"], dtype=np.int64)
    rates = np.asarray(payload["psychometric_response_rate"], dtype=np.float64)
    trials = int(_scalar(payload, "psychometric_trials"))
    psych_rows = []
    for model, role in enumerate(MODEL_ROLES):
        for validity_index, validity in enumerate(DISPLAYED_VALIDITIES):
            for magnitude_index, magnitude in enumerate(CHANGE_MAGNITUDES):
                for condition, condition_name in enumerate(EVENT_CONDITIONS):
                    low, high = base._wilson_interval(
                        counts[model, validity_index, magnitude_index, condition], trials
                    )
                    psych_rows.append(
                        {
                            "model": role,
                            "memory_decay": MODEL_DECAYS[model],
                            "displayed_validity": float(validity),
                            "orientation_change_degrees": float(magnitude),
                            "condition": condition_name,
                            "response_count": int(counts[model, validity_index, magnitude_index, condition]),
                            "trials": trials,
                            "response_rate": f"{rates[model, validity_index, magnitude_index, condition]:.10g}",
                            "wilson_ci_low": f"{float(low):.10g}",
                            "wilson_ci_high": f"{float(high):.10g}",
                        }
                    )
    _write_csv(output_dir / "psychometric_response_rates.csv", psych_rows)

    time_rows = []
    for prefix in (
        "event_temporal_motion",
        "event_selectivity",
        "event_image_mass",
        "event_memory_mass",
        "event_peak_key_mass",
    ):
        values = np.asarray(payload[prefix], dtype=np.float64)
        for model, role in enumerate(MODEL_ROLES):
            for condition, condition_name in enumerate(EVENT_CONDITIONS):
                for timestep in range(values.shape[-1]):
                    sample = values[model, condition, :, timestep]
                    time_rows.append(
                        {
                            "metric": prefix.removeprefix("event_"),
                            "model": role,
                            "memory_decay": MODEL_DECAYS[model],
                            "condition": condition_name,
                            "logical_index": timestep + (1 if prefix == "event_temporal_motion" else 0),
                            "mean": f"{sample.mean():.10g}",
                            "standard_error": f"{sample.std(ddof=1) / np.sqrt(sample.size):.10g}",
                            "trials": sample.size,
                        }
                    )
    _write_csv(output_dir / "event_attention_timecourses.csv", time_rows)


def _interval(record: dict[str, Any]) -> str:
    return f"[{record['ci_low']:+.4f}, {record['ci_high']:+.4f}]"


def write_report(run_root: Path, summary: dict[str, Any], records: dict[str, dict[str, Any]]) -> None:
    primary = summary["metrics"]["primary_event_attention_motion"]
    lines = [
        "# VDA4 cross-attention memory-decay series",
        "",
        "## Result",
        "",
        f"Primary attention-motion ordering: **{summary['primary_order']}**.",
        "",
        "| model | decay | iteration | mean attention motion |",
        "|---|---:|---:|---:|",
    ]
    for index, role in enumerate(MODEL_ROLES):
        lines.append(
            f"| {MODEL_SHORT_LABELS[index]} | {MODEL_DECAYS[index]:.2f} | "
            f"{records[role]['checkpoint_iteration']} | {primary['model_means'][role]:.4f} |"
        )
    lines += ["", "| contrast | difference | paired 95% interval |", "|---|---:|---:|"]
    for pair_name, _, _, label in PAIR_SPECS:
        estimate = primary["pairwise"][pair_name]
        lines.append(
            f"| {label} | {estimate['mean_difference']:+.4f} | {_interval(estimate)} |"
        )
    lines += [
        "",
        "The intervals resample matched evaluation trials. They do not represent training-seed uncertainty.",
        "",
        "## Checkpoints",
        "",
        "| role | iteration | decay | SHA-256 |",
        "|---|---:|---:|---|",
    ]
    for index, role in enumerate(MODEL_ROLES):
        lines.append(
            f"| {role} | {records[role]['checkpoint_iteration']} | {MODEL_DECAYS[index]:.2f} | "
            f"`{records[role]['sha256']}` |"
        )
    lines += [
        "",
        "## Protocol",
        "",
        f"- Event attention: {summary['event_condition']['attention_trials']} shared trials per valid/forced-invalid condition.",
        f"- No-change attention: {summary['event_condition']['nochange_trials']} trials per displayed cue proportion.",
        f"- Psychometrics: {summary['event_condition']['psychometric_trials']} shared trials per point.",
        "- Attention topology: four query rows × eight keys (four image keys plus four recurrent-memory keys).",
        "- Primary descriptor: " + summary["primary_definition"],
        "- Execution: CPU only, with common random numbers across models.",
        "",
        "## Evidence boundary",
        "",
        summary["interpretation_boundary"],
        "",
        "## Outputs",
        "",
        "- `data/comparison_evidence.npz`: validated raw logits, attention tensors, and reductions.",
        "- `tables/`: exact metric, psychometric, and time-course values.",
        "- `figures/`: ten figure triplets (PDF, SVG, PNG), extending every prior plot class.",
        "- `writeup/VDA4_crossattn_decay_series_comparison.pdf`: compiled merged paper.",
    ]
    (run_root / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _hash_tex(value: str) -> str:
    chunks = [value[index : index + 8] for index in range(0, len(value), 8)]
    return r"{\footnotesize\texttt{" + r"\allowbreak{}".join(chunks) + "}}"


def render_tex(summary: dict[str, Any], records: dict[str, dict[str, Any]], run_name: str) -> str:
    primary = summary["metrics"]["primary_event_attention_motion"]
    valid_motion = summary["metrics"]["valid_attention_motion"]
    invalid_motion = summary["metrics"]["forced_invalid_attention_motion"]
    selectivity = summary["metrics"]["event_selectivity"]
    image_mass = summary["metrics"]["event_image_key_mass"]
    anchor = summary["psychometric_anchor_100pct_15deg"]
    budget = summary["event_condition"]

    def pair(metric: dict[str, Any], name: str) -> dict[str, Any]:
        return metric["pairwise"][name]

    model_rows = "\n".join(
        f"{MODEL_SHORT_LABELS[index]} & {records[role]['checkpoint_iteration']:,} & {MODEL_DECAYS[index]:.2f} & "
        f"{_hash_tex(records[role]['sha256'])}\\\\"
        for index, role in enumerate(MODEL_ROLES)
    )
    primary_rows = "\n".join(
        f"{MODEL_SHORT_LABELS[index]} & {primary['model_means'][role]:.4f} & "
        f"{valid_motion['model_means'][role]:.4f} & {invalid_motion['model_means'][role]:.4f} & "
        f"{selectivity['model_means'][role]:.4f} & {image_mass['model_means'][role]:.4f}\\\\"
        for index, role in enumerate(MODEL_ROLES)
    )
    contrast_rows = "\n".join(
        f"{label} & {pair(primary, name)['mean_difference']:+.4f} & "
        f"[{pair(primary, name)['ci_low']:+.4f}, {pair(primary, name)['ci_high']:+.4f}]\\\\"
        for name, _, _, label in PAIR_SPECS
    )
    anchor_rows = "\n".join(
        f"{MODEL_SHORT_LABELS[index]} & "
        f"{anchor[role]['valid']['response_count']}/{anchor[role]['valid']['trials']} "
        f"({anchor[role]['valid']['response_rate']:.3f}) & "
        f"{anchor[role]['forced_invalid']['response_count']}/{anchor[role]['forced_invalid']['trials']} "
        f"({anchor[role]['forced_invalid']['response_rate']:.3f})\\\\"
        for index, role in enumerate(MODEL_ROLES)
    )
    trend_text = {
        "monotonic_increase_with_decay_strength": "increased monotonically with stronger decay",
        "monotonic_decrease_with_decay_strength": "decreased monotonically with stronger decay",
        "nonmonotonic": "was nonmonotonic across the three decay settings",
    }[summary["primary_order"]]
    light_no = pair(primary, "light_minus_no")
    heavy_no = pair(primary, "heavy_minus_no")
    heavy_light = pair(primary, "heavy_minus_light")

    return rf"""\documentclass[11pt]{{article}}
\usepackage[margin=20mm,headheight=15pt,footskip=11mm]{{geometry}}
\usepackage{{fontspec}}
\setmainfont{{Avenir Next}}
\setsansfont{{Avenir Next}}
\usepackage{{microtype}}
\usepackage{{graphicx}}
\usepackage{{booktabs,tabularx,array}}
\usepackage{{ragged2e}}
\usepackage{{pdflscape}}
\usepackage{{caption}}
\usepackage{{xcolor}}
\usepackage{{hyperref}}
\usepackage{{fancyhdr}}
\usepackage{{amsmath}}
\usepackage{{enumitem}}
\definecolor{{VdaBlue}}{{HTML}}{{1F6FB2}}
\definecolor{{VdaLight}}{{HTML}}{{F1F5F8}}
\hypersetup{{colorlinks=true,linkcolor=VdaBlue,urlcolor=VdaBlue,pdftitle={{Memory decay across learned cross-attention dynamics}},pdfauthor={{AttentionManuscript}}}}
\graphicspath{{{{../figures/}}}}
\captionsetup{{font=small,labelfont=bf,justification=justified,singlelinecheck=false,hypcap=false}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.55em}}
\setlist{{nosep,leftmargin=1.3em}}
\emergencystretch=2em
\raggedbottom
\widowpenalty=10000
\clubpenalty=10000
\newcolumntype{{Y}}{{>{{\RaggedRight\arraybackslash}}X}}
\newcommand{{\boundary}}[1]{{\par\smallskip\noindent\colorbox{{VdaLight}}{{\parbox{{0.96\linewidth}}{{\textbf{{Evidence boundary.}} #1}}}}\par\smallskip}}
\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[L]{{\small VDA4 cross-attention decay series}}
\fancyhead[R]{{\small \nouppercase{{\rightmark}}}}
\fancyfoot[C]{{\small \thepage}}
\renewcommand{{\headrulewidth}}{{0.3pt}}

\begin{{document}}
\begin{{titlepage}}
\thispagestyle{{empty}}
\vspace*{{16mm}}
{{\color{{VdaBlue}}\rule{{\textwidth}}{{2.2pt}}}}\\[10mm]
{{\fontsize{{27}}{{32}}\selectfont\bfseries Memory decay across learned\\ cross-attention dynamics\par}}
\vspace{{4mm}}
{{\fontsize{{16}}{{21}}\selectfont A three-checkpoint comparison in the four-location value-directed-attention task\par}}
\vspace{{15mm}}
{{\large AttentionManuscript --- merged VDA4 analysis\par}}
\vfill
\begin{{tabularx}}{{\textwidth}}{{@{{}}p{{4.0cm}}Y@{{}}}}
\toprule
\textbf{{Comparison}} & Completed no-decay ($\lambda=1.00$), light-decay ($\lambda=0.80$), and heavy-decay ($\lambda=0.50$) cross-attention checkpoints.\\
\textbf{{Primary descriptor}} & Frame-to-frame total variation over complete learned $4\times8$ attention distributions.\\
\textbf{{Primary result}} & Attention motion {trend_text}. Light minus no decay was {light_no['mean_difference']:+.4f} ({_interval(light_no)}); heavy minus no decay was {heavy_no['mean_difference']:+.4f} ({_interval(heavy_no)}); heavy minus light decay was {heavy_light['mean_difference']:+.4f} ({_interval(heavy_light)}).\\
\textbf{{Run identity}} & \path{{{run_name}}}.\\
\bottomrule
\end{{tabularx}}
\vfill
{{\color{{VdaBlue}}\rule{{\textwidth}}{{2.2pt}}}}
\end{{titlepage}}

\begin{{abstract}}
The prior frozen-checkpoint paper compared the no-decay VDA4 cross-attention model with an unfinished light-decay snapshot. We extend that analysis to the completed light-decay checkpoint and a newly completed heavy-decay checkpoint, preserving the shared deterministic trial battery, behavioral response rule, full query-level attention topology, and all earlier plot classes. Mean event attention motion was {primary['model_means']['no_decay']:.4f} without decay, {primary['model_means']['light_decay']:.4f} with light decay, and {primary['model_means']['heavy_decay']:.4f} with heavy decay; the three-point ordering {trend_text}. Psychometric curves, image-versus-memory allocation, selectivity, change-location reorientation, response-stratified traces, event maps, and no-change maps describe where this ordering comes from. These are one-checkpoint-per-setting comparisons: trial-bootstrap intervals do not quantify training-seed uncertainty, and the heavy-decay checkpoint received 2,800 more iterations than the light-decay checkpoint.
\end{{abstract}}

\section{{Question, estimand, and evidence boundary}}
For each query row $q$ and consecutive frames $t-1,t$, attention motion is
\[
D_{{t,q}}=\tfrac12\sum_{{k=1}}^8\left|A_{{t,q,k}}-A_{{t-1,q,k}}\right|.
\]
The primary trial-level descriptor averages this total-variation distance over transitions, query rows, and the matched valid and forced-invalid event conditions. It is zero for an unchanged row and one for a complete shift between disjoint keys. Total attention mass is not an activity measure because every row is softmax-normalized to one.

\boundary{{{summary['interpretation_boundary']}}}

\section{{Frozen checkpoints and matched protocol}}
\begin{{center}}
\small
\captionof{{table}}{{Frozen model identities. Every checkpoint validates as VDA4, xLSTM, \texttt{{crossattn1}}, $d_{{mem}}=128$, convolutional front end, and $2\times2$ geometry.}}
\begin{{tabularx}}{{\textwidth}}{{@{{}}p{{2.5cm}}p{{1.5cm}}p{{1.4cm}}Y@{{}}}}
\toprule
Role & Iteration & Decay & Frozen SHA-256\\
\midrule
{model_rows}
\bottomrule
\end{{tabularx}}
\end{{center}}

Each event trial has seven logical frames: blank, cue at frame 1, delay, stimulus array at frames 3--6, and an orientation change at frame 5. The cue is fixed at S1. In the valid condition the $15^\circ$ change occurs at S1; in the forced-invalid condition it occurs at S4. Paired videos are identical through frame 4. The 100\%-cue invalid condition is an analysis intervention, not a sample from the natural 100\%-valid environment.

Event attention uses {budget['attention_trials']} matched trials per condition. No-change attention uses {budget['nochange_trials']} trials at each displayed cue proportion (25, 50, 75, and 100\%). Psychometric curves use {budget['psychometric_trials']} shared trials at every combination of four cue proportions, ten change magnitudes, and valid or forced-invalid location. A first greedy change action at frame 5 or 6 qualifies. Pairwise intervals use 10,000 deterministic bootstrap resamples of matched evaluation trials; psychometric rate bands are Wilson intervals.

\section{{Results}}
\subsection{{Attention motion and secondary descriptors}}
\begin{{center}}
\small
\captionof{{table}}{{Model-level attention descriptors on matched event trials.}}
\begin{{tabular}}{{lrrrrr}}
\toprule
Model & Overall motion & Valid motion & Invalid motion & Selectivity & Image-key mass\\
\midrule
{primary_rows}
\bottomrule
\end{{tabular}}
\end{{center}}

\begin{{center}}
\small
\captionof{{table}}{{Paired primary attention-motion contrasts. Intervals resample evaluation trials, not training runs.}}
\begin{{tabular}}{{lrr}}
\toprule
Contrast & Difference & Paired 95\% interval\\
\midrule
{contrast_rows}
\bottomrule
\end{{tabular}}
\end{{center}}

\begin{{center}}
\includegraphics[width=0.98\textwidth,height=0.68\textheight,keepaspectratio]{{attention_metrics_and_response_strata.pdf}}
\captionof{{figure}}{{\textbf{{Dynamic and spatial attention descriptors.}} The original motion, selectivity, image-versus-memory allocation, cued-location, change-location, and response-stratified views now include all three completed checkpoints. Color identifies decay setting; solid and dashed traces identify valid and forced-invalid conditions.}}
\label{{fig:metrics}}
\end{{center}}

\clearpage
\subsection{{Behavior at valid and forced-invalid locations}}
At the matched 100\%-cue, $15^\circ$ anchor, response counts and rates were:
\begin{{center}}
\small
\begin{{tabular}}{{lrr}}
\toprule
Model & Valid & Forced invalid\\
\midrule
{anchor_rows}
\bottomrule
\end{{tabular}}
\end{{center}}
These are change-response probabilities, not sensitivity estimates; no signal-detection decomposition separates discriminability from criterion.

\begin{{center}}
\includegraphics[width=0.98\textwidth,height=0.68\textheight,keepaspectratio]{{psychometric_valid_invalid_comparison.pdf}}
\captionof{{figure}}{{\textbf{{Behavioral curves.}} Qualifying response probability across orientation-change magnitude at every displayed cue proportion. All models receive common trials.}}
\end{{center}}

\clearpage
\begin{{center}}
\includegraphics[width=0.98\textwidth,height=0.64\textheight,keepaspectratio]{{psychometric_pairwise_differences.pdf}}
\captionof{{figure}}{{\textbf{{Pairwise behavioral differences.}} Light-minus-no, heavy-minus-no, and heavy-minus-light response-rate differences for valid and forced-invalid changes, shown on one common diverging scale.}}
\end{{center}}

\clearpage
\subsection{{Where the attention moves}}
Image keys and recurrent-memory keys are shown separately because they partition each normalized eight-key row. The overview averages over query rows; the following landscape plates preserve all four queries. Every map in a figure uses one common scale across models, event conditions, sources, and frames.

\begin{{center}}
\includegraphics[width=0.98\textwidth,height=0.72\textheight,keepaspectratio]{{attention_event_query_averaged.pdf}}
\captionof{{figure}}{{\textbf{{Query-averaged event maps.}} No-, light-, and heavy-decay attention under matched valid and forced-invalid videos, with image and recurrent-memory keys separated across all seven frames.}}
\label{{fig:event-maps}}
\end{{center}}

\clearpage
\begin{{landscape}}
\thispagestyle{{plain}}
\begin{{center}}
\includegraphics[width=0.96\linewidth,height=0.63\linewidth,keepaspectratio]{{attention_query_level_valid_image_keys.pdf}}
\captionof{{figure}}{{\textbf{{Valid condition, image keys.}} Full query-to-image routing for all three models; cue and change are both at S1.}}
\end{{center}}
\end{{landscape}}

\begin{{landscape}}
\thispagestyle{{plain}}
\begin{{center}}
\includegraphics[width=0.96\linewidth,height=0.63\linewidth,keepaspectratio]{{attention_query_level_valid_memory_keys.pdf}}
\captionof{{figure}}{{\textbf{{Valid condition, recurrent-memory keys.}} Full query-to-memory routing on the same valid trials.}}
\end{{center}}
\end{{landscape}}

\begin{{landscape}}
\thispagestyle{{plain}}
\begin{{center}}
\includegraphics[width=0.96\linewidth,height=0.63\linewidth,keepaspectratio]{{attention_query_level_forced_invalid_image_keys.pdf}}
\captionof{{figure}}{{\textbf{{Forced-invalid condition, image keys.}} The cue remains at S1 while the change is forced to S4.}}
\end{{center}}
\end{{landscape}}

\begin{{landscape}}
\thispagestyle{{plain}}
\begin{{center}}
\includegraphics[width=0.96\linewidth,height=0.63\linewidth,keepaspectratio]{{attention_query_level_forced_invalid_memory_keys.pdf}}
\captionof{{figure}}{{\textbf{{Forced-invalid condition, recurrent-memory keys.}} Query-preserving memory routing after a change outside the cued location.}}
\end{{center}}
\end{{landscape}}

\clearpage
\section{{No-change cue-proportion sweep}}
These plates preserve the previous no-change analysis and add the heavy-decay model. They separate image and recurrent-memory routing while varying only the displayed cue proportion.

\begin{{center}}
\includegraphics[width=0.98\textwidth,height=0.72\textheight,keepaspectratio]{{attention_nochange_image_keys.pdf}}
\captionof{{figure}}{{\textbf{{No-change image-key attention.}} Query-averaged source maps for all three models and four cue proportions.}}
\end{{center}}

\clearpage
\begin{{center}}
\includegraphics[width=0.98\textwidth,height=0.72\textheight,keepaspectratio]{{attention_nochange_memory_keys.pdf}}
\captionof{{figure}}{{\textbf{{No-change recurrent-memory attention.}} The matched memory-key view of the same no-change trials.}}
\end{{center}}

\section{{Interpretation}}
The three-point comparison shows that primary attention motion {trend_text}. This statement is deliberately narrower than ``more'' or ``less attention'': all attention rows carry unit mass, and selectivity, peak mass, source allocation, spatial routing, and behavior can move in different directions. The query-preserving plates are therefore part of the result rather than decorative examples.

The completed light-decay checkpoint supersedes the unfinished iteration-14,649 snapshot used in the previous paper. That improves maturity matching against the no-decay checkpoint. It does not make this a controlled decay experiment: each setting has one seed, and the newly completed heavy-decay model continued to iteration 22,799 while the other checkpoints ended near 20,000. Pairwise intervals quantify matched evaluation-trial sampling only.

The heavy-decay checkpoint was resumed statefully from iteration 16,799 through 22,799 under the recorded \texttt{{schedule\_overrun\_with\_saturated\_schedules}} compatibility transition. Its original schedule endpoint remained 19,999; saturated schedules stayed capped thereafter. The optimizer, target model, JEPA teacher, RNG, and environment state were preserved, but replay was explicitly excluded from persisted trainer state and therefore restarted empty. A later \texttt{{SIGTERM}} concerned only a deliberately stopped completion watcher after independent checkpoint verification, not the trainer. The legacy no-decay artifact contains only model-state metadata, so its trainer-state lineage is less complete than the two decay checkpoints.

\section{{Reproducibility record}}
The numerical source is \texttt{{SUMMARY.json}}, derived from the validated \texttt{{data/comparison\_evidence.npz}} cache. Figures were generated in PDF, SVG, and PNG from that cache. Frozen checkpoint bytes, executable source snapshots, exact command, runtime versions, tables, rendered-output verification, and cryptographic hashes are retained under the run root.

\begin{{itemize}}
\item Analysis run: \path{{{run_name}}}.
\item Primary definition: {summary['primary_definition']}
\item Evidence boundary: {summary['interpretation_boundary']}
\end{{itemize}}

\end{{document}}
"""


def compile_paper(run_root: Path, summary: dict[str, Any], records: dict[str, dict[str, Any]]) -> Path:
    writeup = run_root / "writeup"
    build = writeup / "build"
    writeup.mkdir(parents=True, exist_ok=True)
    build.mkdir(parents=True, exist_ok=True)
    tex_path = writeup / "main.tex"
    tex_path.write_text(render_tex(summary, records, run_root.name), encoding="utf-8")
    environment = dict(__import__("os").environ)
    environment["SOURCE_DATE_EPOCH"] = "1784000000"
    for pass_index in (1, 2):
        result = subprocess.run(
            [
                "xelatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={build}",
                str(tex_path),
            ],
            cwd=writeup,
            env=environment,
            capture_output=True,
            text=True,
        )
        (build / f"pass{pass_index}.stdout").write_text(
            result.stdout + result.stderr, encoding="utf-8"
        )
        if result.returncode != 0:
            raise RuntimeError(f"xelatex pass {pass_index} failed; see {build / f'pass{pass_index}.stdout'}")
    source_pdf = build / "main.pdf"
    destination = writeup / "VDA4_crossattn_decay_series_comparison.pdf"
    shutil.copy2(source_pdf, destination)
    if sha256_path(source_pdf) != sha256_path(destination):
        raise RuntimeError("compiled manuscript copy hash mismatch")
    return destination


def verify_rendered_outputs(run_root: Path, manuscript: Path) -> dict[str, Any]:
    from PIL import Image

    figure_dir = run_root / "figures"
    for suffix in ("pdf", "png", "svg"):
        names = sorted(path.stem for path in figure_dir.glob(f"*.{suffix}"))
        if names != sorted(FIGURE_STEMS):
            raise RuntimeError(f"{suffix} figure inventory mismatch: {names}")
    figure_records = []
    with tempfile.TemporaryDirectory(prefix="vda4-series-verify-") as temporary:
        temporary_root = Path(temporary)
        for index, stem in enumerate(FIGURE_STEMS):
            pdf = figure_dir / f"{stem}.pdf"
            info = subprocess.run(
                ["pdfinfo", str(pdf)], check=True, capture_output=True, text=True
            ).stdout
            pages = [line for line in info.splitlines() if line.startswith("Pages:")]
            if len(pages) != 1 or int(pages[0].split(":", 1)[1].strip()) != 1:
                raise RuntimeError(f"figure PDF must have one page: {pdf}")
            raster_base = temporary_root / f"figure_{index}"
            subprocess.run(
                ["pdftoppm", "-singlefile", "-r", "100", "-png", str(pdf), str(raster_base)],
                check=True,
                capture_output=True,
            )
            with Image.open(raster_base.with_suffix(".png")) as image:
                if image.width < 700 or image.height < 400:
                    raise RuntimeError(f"rendered figure is unexpectedly small: {pdf}")
                dimensions = [image.width, image.height]
            png = figure_dir / f"{stem}.png"
            with Image.open(png) as image:
                image.verify()
            svg = (figure_dir / f"{stem}.svg").read_text(encoding="utf-8")
            if "<svg" not in svg or len(svg) < 1000:
                raise RuntimeError(f"SVG failed structural validation: {stem}")
            figure_records.append({"stem": stem, "render_dimensions": dimensions})

        manuscript_info = subprocess.run(
            ["pdfinfo", str(manuscript)], check=True, capture_output=True, text=True
        ).stdout
        manuscript_pages = int(
            [line for line in manuscript_info.splitlines() if line.startswith("Pages:")][0]
            .split(":", 1)[1]
            .strip()
        )
        if manuscript_pages < 10:
            raise RuntimeError(f"compiled manuscript is unexpectedly short: {manuscript_pages} pages")
        raster_root = temporary_root / "paper"
        subprocess.run(
            ["pdftoppm", "-r", "80", "-png", str(manuscript), str(raster_root)],
            check=True,
            capture_output=True,
        )
        rendered_pages = sorted(temporary_root.glob("paper-*.png"))
        if len(rendered_pages) != manuscript_pages:
            raise RuntimeError("manuscript raster page count mismatch")
        for page in rendered_pages:
            with Image.open(page) as image:
                if image.width < 500 or image.height < 500:
                    raise RuntimeError(f"manuscript page render is too small: {page}")
    extracted = subprocess.run(
        ["pdftotext", str(manuscript), "-"], check=True, capture_output=True, text=True
    ).stdout
    for required in (
        "Memory decay across learned",
        "No decay",
        "Light decay",
        "Heavy decay",
        "Reproducibility record",
    ):
        if required not in extracted:
            raise RuntimeError(f"compiled manuscript is missing extractable text: {required!r}")
    return {
        "figure_triplets": len(FIGURE_STEMS),
        "figure_records": figure_records,
        "manuscript_path": str(manuscript.relative_to(run_root)),
        "manuscript_sha256": sha256_path(manuscript),
        "manuscript_pages": manuscript_pages,
        "extractable_text_chars": len(extracted),
    }


def snapshot_sources(run_root: Path, captured: dict[str, bytes]) -> dict[str, Any]:
    records = {}
    for relative, content in captured.items():
        destination = run_root / "provenance" / "source_snapshot" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        if destination.read_bytes() != content:
            raise RuntimeError(f"source snapshot mismatch: {relative}")
        records[relative] = {
            "path": str(destination.relative_to(run_root)),
            "bytes": len(content),
            "sha256": sha256_bytes(content),
        }
    return records


def build_manifest(
    run_root: Path,
    *,
    started_at: str,
    cache_metadata: dict[str, Any],
    frozen_inputs: dict[str, Any],
    source_records: dict[str, Any],
    verification: dict[str, Any],
    runtime_versions: dict[str, Any],
) -> Path:
    manifest_path = run_root / "MANIFEST.json"
    inventory = []
    for path in sorted(run_root.rglob("*")):
        if not path.is_file() or path == manifest_path or path.name == ".DS_Store":
            continue
        inventory.append(
            {
                "path": str(path.relative_to(run_root)),
                "bytes": path.stat().st_size,
                "sha256": sha256_path(path),
            }
        )
    manifest = {
        "schema_version": 2,
        "status": "complete",
        "analysis": "vda4_crossattn1_memory_decay_series",
        "started_at_utc": started_at,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "cache": cache_metadata,
        "frozen_inputs": frozen_inputs,
        "source_snapshot": source_records,
        "runtime_versions": runtime_versions,
        "verification": verification,
        "artifact_inventory": inventory,
        "interpretation_boundary": (
            "single completed checkpoint per decay setting; evaluation-trial uncertainty only; "
            "heavy-decay checkpoint has 2,800 more iterations than light decay and continued "
            "beyond its original schedule endpoint with replay excluded from persisted state"
        ),
    }
    _write_json_exclusive(manifest_path, manifest)
    loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
    for record in loaded["artifact_inventory"]:
        artifact = run_root / record["path"]
        if artifact.stat().st_size != record["bytes"] or sha256_path(artifact) != record["sha256"]:
            raise RuntimeError(f"manifest inventory verification failed: {artifact}")
    return manifest_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--no-decay-checkpoint", type=Path, required=True)
    parser.add_argument("--light-decay-checkpoint", type=Path, required=True)
    parser.add_argument("--heavy-decay-checkpoint", type=Path, required=True)
    parser.add_argument("--attention-trials", type=int, default=256)
    parser.add_argument("--nochange-trials", type=int, default=128)
    parser.add_argument("--psychometric-trials", type=int, default=300)
    parser.add_argument("--threads", type=int, default=3)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_root = args.run_root.expanduser().resolve()
    if run_root.exists():
        raise FileExistsError(f"run root already exists: {run_root}")
    if min(args.attention_trials, args.nochange_trials, args.psychometric_trials, args.threads) <= 0:
        raise ValueError("trial budgets and thread count must be positive")
    run_root.mkdir(parents=True)
    started_at = datetime.now(timezone.utc).isoformat()
    captured_sources = capture_executable_sources()
    frozen_inputs, records = freeze_inputs(
        run_root,
        no_decay_checkpoint=args.no_decay_checkpoint,
        light_decay_checkpoint=args.light_decay_checkpoint,
        heavy_decay_checkpoint=args.heavy_decay_checkpoint,
    )

    import matplotlib
    import scipy
    import torch
    from PIL import __version__ as pillow_version

    runtime_versions = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "scipy": scipy.__version__,
        "pillow": pillow_version,
        "torch": torch.__version__,
        "python_executable": str(Path(sys.executable).resolve()),
    }
    torch.set_num_threads(args.threads)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        pass

    base.MODEL_ROLES = MODEL_ROLES
    base.resolved_model_kwargs = resolved_model_kwargs
    cache_path = base.compute_comparison_cache(
        run_root,
        records,
        attention_trials=args.attention_trials,
        nochange_trials=args.nochange_trials,
        psychometric_trials=args.psychometric_trials,
        torch_module=torch,
    )
    cache_metadata = validate_comparison_cache(
        cache_path,
        expected_attention_trials=args.attention_trials,
        expected_nochange_trials=args.nochange_trials,
        expected_psychometric_trials=args.psychometric_trials,
    )
    with np.load(cache_path, allow_pickle=False) as payload:
        summary = build_numeric_summary(payload)
        build_figures(payload, run_root / "figures", summary)
        write_tables(payload, summary, run_root / "tables")
    _write_json_exclusive(run_root / "SUMMARY.json", summary)
    write_report(run_root, summary, records)

    command = " ".join(
        shlex.quote(value)
        for value in [str(Path(sys.executable).resolve()), str(Path(__file__).resolve())]
        + (argv if argv is not None else sys.argv[1:])
    )
    provenance = run_root / "provenance"
    provenance.mkdir(parents=True, exist_ok=True)
    (provenance / "COMMAND.txt").write_text(command + "\n", encoding="utf-8")
    _write_json_exclusive(provenance / "runtime_versions.json", runtime_versions)
    source_records = snapshot_sources(run_root, captured_sources)
    manuscript = compile_paper(run_root, summary, records)
    verification = verify_rendered_outputs(run_root, manuscript)
    _write_json_exclusive(provenance / "render_verification.json", verification)
    assert_sources_unchanged(captured_sources)
    for role, record in records.items():
        if sha256_path(record["snapshot_path"]) != record["sha256"]:
            raise RuntimeError(f"frozen checkpoint changed during analysis: {role}")
    manifest = build_manifest(
        run_root,
        started_at=started_at,
        cache_metadata=cache_metadata,
        frozen_inputs=frozen_inputs,
        source_records=source_records,
        verification=verification,
        runtime_versions=runtime_versions,
    )
    primary = summary["metrics"]["primary_event_attention_motion"]
    print(
        json.dumps(
            {
                "status": "complete",
                "run_root": str(run_root),
                "manifest": str(manifest),
                "manuscript": str(manuscript),
                "primary_order": summary["primary_order"],
                "primary_model_means": primary["model_means"],
                "primary_pairwise": primary["pairwise"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
