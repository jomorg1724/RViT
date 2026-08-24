#!/usr/bin/env python3
"""Standalone VDA4 affine_ew memory-decay comparison producer.

This is the affine-topology counterpart to ``vda4_decay_comparison.py``.
It compares two immutable affine_ew checkpoints on common CPU-generated trials.
Affine attention has one spatial key per query location (4x4), so the analysis
preserves the query axis and reports spatial routing without inventing image-vs-
memory source groups that do not exist in this model.
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
MODEL_ROLES = ("standard", "high_decay")
EVENT_CONDITIONS = ("valid", "forced_invalid")
DISPLAYED_VALIDITIES = np.array([0.25, 0.5, 0.75, 1.0], dtype=np.float64)
CHANGE_MAGNITUDES = np.array([0, 3, 6, 9, 12, 15, 18, 22, 26, 30], dtype=np.float64)
TIMESTEPS = 7
QUERY_COUNT = 4
KEY_COUNT = 4
CUE_INDEX = 0
VALID_CHANGE_INDEX = 0
INVALID_CHANGE_INDEX = 3
EVENT_MAGNITUDE = 15.0
EVENT_DISPLAYED_VALIDITY = 1.0
EVENT_SEED = 4101
NOCHANGE_SEED = 1701
PSYCHOMETRIC_SEED = 2801
QUALIFYING_RESPONSE_FRAME = 5
BOOTSTRAP_SAMPLES = 10_000
SOURCE_DEPENDENCIES = (
    "analysis/vda4_decay_comparison.py",
    "model.py",
    "conv_frontend.py",
    "vae_frontend.py",
    "paper_encoder.py",
    "paper_heads.py",
    "envs/__init__.py",
    "envs/base.py",
    "envs/tasks.py",
    "envs/luo2015.py",
    "vda_sweep/vda_core.py",
)
MODEL_CONTRACT = {
    "feedback": "affine_ew",
    "cell": "xlstm",
    "d_mem": 128,
    "conv_frontend": True,
    "grid_rows": 2,
    "grid_cols": 2,
    "image_size": 50,
}


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_path(path: str | Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def _scalar(payload: Any, field: str) -> Any:
    value = np.asarray(payload[field])
    if value.ndim != 0:
        raise ValueError(f"cache field {field!r} must be scalar")
    return value.item()


def resolved_model_kwargs(checkpoint: dict[str, Any], *, role: str) -> dict[str, Any]:
    if role not in MODEL_ROLES:
        raise ValueError(f"unknown model role: {role!r}")
    if checkpoint.get("task") != "vda4":
        raise ValueError(f"task must be 'vda4'; got {checkpoint.get('task')!r}")
    kwargs = dict(checkpoint.get("model_kwargs") or {})
    for field, expected in MODEL_CONTRACT.items():
        if kwargs.get(field) != expected:
            raise ValueError(f"{field} must be {expected!r}; got {kwargs.get(field)!r}")
    expected_decay = 1.0 if role == "standard" else 0.8
    resolved_decay = float(kwargs.get("memory_decay", 1.0))
    if resolved_decay != expected_decay:
        raise ValueError(
            f"memory_decay must resolve to {expected_decay} for {role}; got {resolved_decay}"
        )
    kwargs["memory_decay"] = resolved_decay
    return kwargs


def first_press_from_logits(
    actor_logits: np.ndarray, *, qualifying_frame: int = QUALIFYING_RESPONSE_FRAME
) -> tuple[np.ndarray, np.ndarray]:
    logits = np.asarray(actor_logits)
    if logits.ndim != 3 or logits.shape[-1] != 2:
        raise ValueError(f"actor logits must have shape (trial,time,2); got {logits.shape}")
    if not np.isfinite(logits).all():
        raise ValueError("actor logits must be finite")
    change_action = logits.argmax(axis=-1) == 1
    first = np.where(change_action.any(axis=1), change_action.argmax(axis=1), -1).astype(np.int64)
    return first, first >= int(qualifying_frame)


def paired_mean_difference(
    high: np.ndarray,
    standard: np.ndarray,
    *,
    seed: int,
    bootstrap_samples: int = BOOTSTRAP_SAMPLES,
) -> dict[str, float | int]:
    high_values = np.asarray(high, dtype=np.float64)
    standard_values = np.asarray(standard, dtype=np.float64)
    if high_values.shape != standard_values.shape or high_values.size == 0:
        raise ValueError(f"paired arrays must match and be nonempty: {high_values.shape}, {standard_values.shape}")
    differences = (high_values - standard_values).reshape(-1)
    if not np.isfinite(differences).all():
        raise ValueError("paired differences must be finite")
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, differences.size, size=(int(bootstrap_samples), differences.size))
    bootstrap_means = differences[indices].mean(axis=1)
    low, high_ci = np.quantile(bootstrap_means, [0.025, 0.975])
    return {
        "mean_difference": float(differences.mean()),
        "ci_low": float(low),
        "ci_high": float(high_ci),
        "n": int(differences.size),
        "bootstrap_samples": int(bootstrap_samples),
        "seed": int(seed),
    }


def affine_attention_metrics(raw_attention: np.ndarray) -> dict[str, np.ndarray]:
    """Return trial-level descriptors for raw affine attention (trial,time,query,key)."""
    raw = np.asarray(raw_attention, dtype=np.float64)
    if raw.ndim != 4:
        raise ValueError(f"raw attention must have shape (trial,time,query,key); got {raw.shape}")
    queries, keys = raw.shape[-2:]
    if queries != QUERY_COUNT or keys != KEY_COUNT or queries != keys:
        raise ValueError(f"affine attention requires Q=K=4; got Q={queries}, K={keys}")
    if not np.isfinite(raw).all() or np.any(raw < 0.0):
        raise ValueError("attention must be finite and nonnegative")
    if not np.allclose(raw.sum(axis=-1), 1.0, rtol=1e-5, atol=1e-6):
        raise ValueError("attention rows must sum to one")
    eps = np.finfo(np.float64).tiny
    entropy = -(raw * np.log(np.clip(raw, eps, 1.0))).sum(axis=-1)
    selectivity = 1.0 - entropy.mean(axis=-1) / np.log(keys)
    temporal_motion = 0.5 * np.abs(np.diff(raw, axis=1)).sum(axis=-1).mean(axis=-1)
    peak_key_mass = raw.max(axis=-1).mean(axis=-1)
    spatial_mass = raw.mean(axis=-2)
    return {
        "temporal_motion": temporal_motion,
        "selectivity": selectivity,
        "peak_key_mass": peak_key_mass,
        "spatial_mass": spatial_mass,
    }


def capture_executable_sources() -> dict[str, bytes]:
    paths = {"analysis/vda4_affine_decay_comparison.py": Path(__file__).resolve()}
    paths.update({relative: PROJECT_ROOT / relative for relative in SOURCE_DEPENDENCIES})
    return {relative: path.read_bytes() for relative, path in paths.items()}


def assert_sources_unchanged(captured: dict[str, bytes]) -> None:
    for relative, expected in captured.items():
        path = (
            Path(__file__).resolve()
            if relative == "analysis/vda4_affine_decay_comparison.py"
            else PROJECT_ROOT / relative
        )
        if path.read_bytes() != expected:
            raise RuntimeError(f"executable source changed during analysis: {path}")


def _copy_frozen_checkpoint(source: Path, destination: Path) -> dict[str, Any]:
    source = source.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"checkpoint does not exist: {source}")
    content = source.read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"frozen checkpoint destination already exists: {destination}")
    destination.write_bytes(content)
    copied = destination.read_bytes()
    if copied != content:
        raise RuntimeError(f"checkpoint copy changed bytes: {source} -> {destination}")
    import torch
    checkpoint = torch.load(io.BytesIO(content), map_location="cpu", weights_only=False)
    return {
        "source_path": str(source),
        "snapshot_path": str(destination),
        "bytes": len(content),
        "sha256": sha256_bytes(content),
        "checkpoint_iteration": int(checkpoint["iter"]),
        "task": checkpoint.get("task"),
        "model_kwargs": checkpoint.get("model_kwargs"),
    }


def _load_frozen_inputs(run_root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest = json.loads((run_root / "frozen_inputs.json").read_text(encoding="utf-8"))
    records = {str(record["role"]): record for record in manifest.get("checkpoints", [])}
    if set(records) != set(MODEL_ROLES):
        raise ValueError(f"frozen input roles must be {MODEL_ROLES}; got {sorted(records)}")
    for role, record in records.items():
        checkpoint = (run_root / str(record["snapshot_path"])).resolve()
        if run_root.resolve() not in checkpoint.parents:
            raise ValueError(f"frozen {role} checkpoint escapes run root: {checkpoint}")
        content = checkpoint.read_bytes()
        if len(content) != int(record["bytes"]) or sha256_bytes(content) != str(record["sha256"]):
            raise RuntimeError(f"frozen {role} checkpoint identity mismatch")
        record["snapshot_path"] = str(checkpoint)
    return manifest, records


def _load_model(record: dict[str, Any], *, role: str, torch_module: Any):
    from model import RViTPaperModel

    checkpoint_path = Path(str(record["snapshot_path"]))
    content = checkpoint_path.read_bytes()
    if sha256_bytes(content) != str(record["sha256"]):
        raise RuntimeError(f"{role} checkpoint changed before model load")
    checkpoint = torch_module.load(io.BytesIO(content), map_location="cpu", weights_only=False)
    kwargs = resolved_model_kwargs(checkpoint, role=role)
    model = RViTPaperModel(**kwargs)
    state = checkpoint["model_state_dict"]
    if "front.out_norm.bias" in state and not isinstance(model.front.out_norm, torch_module.nn.LayerNorm):
        model.front.out_norm = torch_module.nn.LayerNorm(128)
    result = model.load_state_dict(state, strict=True)
    if result.missing_keys or result.unexpected_keys:
        raise RuntimeError(f"strict {role} load failed: {result}")
    model.to("cpu").eval()
    return model, checkpoint, kwargs


def _run_model_batch(model: Any, videos: Any, torch_module: Any) -> tuple[np.ndarray, np.ndarray]:
    with torch_module.inference_mode():
        output = model.forward_rl_sequence(videos, return_attn=True)
    logits = output["actor_logits_seq"].detach().cpu().numpy().astype(np.float32)
    attention = output["attn_seq"].detach().cpu().numpy().astype(np.float32)
    if attention.shape[1:] != (TIMESTEPS, QUERY_COUNT, KEY_COUNT):
        raise RuntimeError(f"unexpected affine attention shape {attention.shape}")
    if logits.shape[1:] != (TIMESTEPS, 2):
        raise RuntimeError(f"unexpected actor-logit shape {logits.shape}")
    return logits, attention


def _press_histogram(first_press: np.ndarray) -> np.ndarray:
    values = np.asarray(first_press, dtype=np.int64)
    if np.any(values < -1) or np.any(values >= TIMESTEPS):
        raise ValueError("first press must be -1 or a valid timestep")
    return np.bincount(values + 1, minlength=TIMESTEPS + 1).astype(np.int64)


def _atomic_savez(path: Path, **payload: Any) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite analysis cache: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.npz")
    np.savez_compressed(temporary, **payload)
    temporary.replace(path)


def compute_comparison_cache(
    run_root: Path,
    records: dict[str, dict[str, Any]],
    *,
    attention_trials: int,
    nochange_trials: int,
    psychometric_trials: int,
    torch_module: Any,
) -> Path:
    from vda_sweep import vda_core as core

    if any(value <= 0 for value in (attention_trials, nochange_trials, psychometric_trials)):
        raise ValueError("all trial budgets must be positive")
    if str(core.DEVICE) != "cpu":
        raise RuntimeError(f"analysis must run on CPU; vda_core.DEVICE={core.DEVICE!r}")

    models = []
    checkpoint_iterations = []
    resolved_decays = []
    checkpoint_hashes = []
    for role in MODEL_ROLES:
        model, checkpoint, kwargs = _load_model(records[role], role=role, torch_module=torch_module)
        models.append(model)
        checkpoint_iterations.append(int(checkpoint["iter"]))
        resolved_decays.append(float(kwargs["memory_decay"]))
        checkpoint_hashes.append(str(records[role]["sha256"]))

    event_logits = np.empty((2, 2, attention_trials, TIMESTEPS, 2), dtype=np.float32)
    event_raw = np.empty(
        (2, 2, attention_trials, TIMESTEPS, QUERY_COUNT, KEY_COUNT), dtype=np.float32
    )
    event_first = np.empty((2, 2, attention_trials), dtype=np.int64)
    event_qualifying = np.empty_like(event_first, dtype=bool)
    event_videos = []
    for condition_index, change_index in enumerate((VALID_CHANGE_INDEX, INVALID_CHANGE_INDEX)):
        videos = core.make_video_batch(
            "vda4", CUE_INDEX, EVENT_DISPLAYED_VALIDITY, "red", 1, change_index,
            EVENT_MAGNITUDE, B=attention_trials, seed=EVENT_SEED
        ).cpu()
        event_videos.append(videos)
        for model_index, model in enumerate(models):
            logits, raw = _run_model_batch(model, videos, torch_module)
            first, qualifying = first_press_from_logits(logits)
            event_logits[model_index, condition_index] = logits
            event_raw[model_index, condition_index] = raw
            event_first[model_index, condition_index] = first
            event_qualifying[model_index, condition_index] = qualifying
    if not torch_module.equal(event_videos[0][:, :5], event_videos[1][:, :5]):
        raise RuntimeError("paired valid/invalid event videos differ before the change frame")

    nochange_raw = np.empty((2, len(DISPLAYED_VALIDITIES), nochange_trials, TIMESTEPS, QUERY_COUNT, KEY_COUNT), dtype=np.float32)
    for validity_index, displayed_validity in enumerate(DISPLAYED_VALIDITIES):
        videos = core.make_video_batch(
            "vda4", CUE_INDEX, float(displayed_validity), "red", 0, -1, 0.0,
            B=nochange_trials, seed=NOCHANGE_SEED
        ).cpu()
        for model_index, model in enumerate(models):
            _, raw = _run_model_batch(model, videos, torch_module)
            nochange_raw[model_index, validity_index] = raw

    psych_shape = (2, len(DISPLAYED_VALIDITIES), len(CHANGE_MAGNITUDES), 2)
    psych_count = np.zeros(psych_shape, dtype=np.int64)
    psych_histogram = np.zeros(psych_shape + (TIMESTEPS + 1,), dtype=np.int64)
    point_seeds = np.zeros((len(DISPLAYED_VALIDITIES), len(CHANGE_MAGNITUDES)), dtype=np.int64)
    for validity_index, displayed_validity in enumerate(DISPLAYED_VALIDITIES):
        for magnitude_index, magnitude in enumerate(CHANGE_MAGNITUDES):
            point_seed = PSYCHOMETRIC_SEED + magnitude_index * 101
            point_seeds[validity_index, magnitude_index] = point_seed
            for condition_index, change_index in enumerate((VALID_CHANGE_INDEX, INVALID_CHANGE_INDEX)):
                videos = core.make_video_batch(
                    "vda4", CUE_INDEX, float(displayed_validity), "red", 1, change_index,
                    float(magnitude), B=psychometric_trials, seed=int(point_seed)
                ).cpu()
                for model_index, model in enumerate(models):
                    logits, _ = _run_model_batch(model, videos, torch_module)
                    first, qualifying = first_press_from_logits(logits)
                    psych_count[model_index, validity_index, magnitude_index, condition_index] = int(
                        np.count_nonzero(qualifying)
                    )
                    psych_histogram[model_index, validity_index, magnitude_index, condition_index] = _press_histogram(first)

    psych_rate = psych_count / float(psychometric_trials)
    event_metrics: dict[str, np.ndarray] = {}
    nochange_metrics: dict[str, np.ndarray] = {}
    for model_index in range(2):
        for condition_index in range(2):
            metrics = affine_attention_metrics(event_raw[model_index, condition_index])
            for name, values in metrics.items():
                event_metrics.setdefault(
                    f"event_{name}", np.empty((2, 2) + values.shape, dtype=np.float32)
                )[model_index, condition_index] = values
        for validity_index in range(len(DISPLAYED_VALIDITIES)):
            metrics = affine_attention_metrics(nochange_raw[model_index, validity_index])
            for name, values in metrics.items():
                nochange_metrics.setdefault(
                    f"nochange_{name}", np.empty((2, len(DISPLAYED_VALIDITIES)) + values.shape, dtype=np.float32)
                )[model_index, validity_index] = values

    cache_path = run_root / "data" / "comparison_evidence.npz"
    _atomic_savez(
        cache_path,
        model_roles=np.asarray(MODEL_ROLES),
        event_conditions=np.asarray(EVENT_CONDITIONS),
        displayed_validities=DISPLAYED_VALIDITIES,
        change_magnitudes=CHANGE_MAGNITUDES,
        checkpoint_iterations=np.asarray(checkpoint_iterations, dtype=np.int64),
        checkpoint_sha256=np.asarray(checkpoint_hashes),
        resolved_memory_decay=np.asarray(resolved_decays, dtype=np.float64),
        attention_trials=np.array(attention_trials, dtype=np.int64),
        nochange_trials=np.array(nochange_trials, dtype=np.int64),
        psychometric_trials=np.array(psychometric_trials, dtype=np.int64),
        event_seed=np.array(EVENT_SEED, dtype=np.int64),
        nochange_seed=np.array(NOCHANGE_SEED, dtype=np.int64),
        psychometric_seed=np.array(PSYCHOMETRIC_SEED, dtype=np.int64),
        point_seeds=point_seeds,
        cue_index=np.array(CUE_INDEX, dtype=np.int64),
        valid_change_index=np.array(VALID_CHANGE_INDEX, dtype=np.int64),
        invalid_change_index=np.array(INVALID_CHANGE_INDEX, dtype=np.int64),
        event_magnitude=np.array(EVENT_MAGNITUDE, dtype=np.float64),
        event_displayed_validity=np.array(EVENT_DISPLAYED_VALIDITY, dtype=np.float64),
        qualifying_response_frame=np.array(QUALIFYING_RESPONSE_FRAME, dtype=np.int64),
        grid_rows=np.array(2, dtype=np.int64),
        grid_cols=np.array(2, dtype=np.int64),
        query_count=np.array(QUERY_COUNT, dtype=np.int64),
        key_count=np.array(KEY_COUNT, dtype=np.int64),
        attention_topology=np.array("affine_ew spatial self-attention; raw axes trial,time,query,key"),
        device=np.array("cpu"),
        event_actor_logits=event_logits,
        event_raw_attention=event_raw,
        event_spatial_attention=event_raw,
        event_query_averaged_attention=event_raw.mean(axis=-2).astype(np.float32),
        event_first_press=event_first,
        event_qualifying_response=event_qualifying,
        nochange_raw_attention=nochange_raw,
        nochange_spatial_attention=nochange_raw,
        psychometric_response_count=psych_count,
        psychometric_response_rate=psych_rate,
        psychometric_press_histogram=psych_histogram,
        seed_policy=np.array("common random numbers matched across models, displayed cue proportions, and valid/forced-invalid locations at each magnitude"),
        **event_metrics,
        **nochange_metrics,
    )
    for role, record in records.items():
        if sha256_path(record["snapshot_path"]) != str(record["sha256"]):
            raise RuntimeError(f"frozen {role} checkpoint changed during computation")
    return cache_path


def validate_comparison_cache(cache_path: Path, *, expected_attention_trials: int, expected_nochange_trials: int, expected_psychometric_trials: int) -> dict[str, Any]:
    content = cache_path.read_bytes()
    cache_sha256 = sha256_bytes(content)
    checkpoint_iterations = None
    checkpoint_hashes = None
    with np.load(io.BytesIO(content), allow_pickle=False) as payload:
        np.testing.assert_array_equal(payload["model_roles"], np.asarray(MODEL_ROLES))
        np.testing.assert_array_equal(payload["event_conditions"], np.asarray(EVENT_CONDITIONS))
        np.testing.assert_allclose(payload["displayed_validities"], DISPLAYED_VALIDITIES)
        np.testing.assert_allclose(payload["change_magnitudes"], CHANGE_MAGNITUDES)
        np.testing.assert_allclose(payload["resolved_memory_decay"], [1.0, 0.8])
        attention_trials = int(_scalar(payload, "attention_trials"))
        nochange_trials = int(_scalar(payload, "nochange_trials"))
        psychometric_trials = int(_scalar(payload, "psychometric_trials"))
        if (attention_trials, nochange_trials, psychometric_trials) != (expected_attention_trials, expected_nochange_trials, expected_psychometric_trials):
            raise ValueError("realized trial budgets do not match requested budgets")
        for field, expected in {
            "event_seed": EVENT_SEED,
            "nochange_seed": NOCHANGE_SEED,
            "psychometric_seed": PSYCHOMETRIC_SEED,
            "cue_index": CUE_INDEX,
            "valid_change_index": VALID_CHANGE_INDEX,
            "invalid_change_index": INVALID_CHANGE_INDEX,
            "qualifying_response_frame": QUALIFYING_RESPONSE_FRAME,
            "query_count": QUERY_COUNT,
            "key_count": KEY_COUNT,
        }.items():
            if _scalar(payload, field) != expected:
                raise ValueError(f"cache {field} does not satisfy the contract")
        raw_event = np.asarray(payload["event_raw_attention"], dtype=np.float64)
        raw_nochange = np.asarray(payload["nochange_raw_attention"], dtype=np.float64)
        if raw_event.shape != (2, 2, attention_trials, TIMESTEPS, QUERY_COUNT, KEY_COUNT):
            raise ValueError(f"invalid event raw shape: {raw_event.shape}")
        if raw_nochange.shape != (2, 4, nochange_trials, TIMESTEPS, QUERY_COUNT, KEY_COUNT):
            raise ValueError(f"invalid no-change raw shape: {raw_nochange.shape}")
        for raw, spatial_field, query_field, metric_prefix in (
            (raw_event, "event_spatial_attention", "event_query_averaged_attention", "event"),
            (raw_nochange, "nochange_spatial_attention", None, "nochange"),
        ):
            if not np.isfinite(raw).all() or np.any(raw < 0.0) or not np.allclose(raw.sum(axis=-1), 1.0, rtol=1e-5, atol=1e-6):
                raise ValueError(f"{metric_prefix} raw attention violates normalized finite nonnegative contract")
            np.testing.assert_allclose(payload[spatial_field], raw, rtol=0.0, atol=0.0)
            if query_field is not None:
                np.testing.assert_allclose(payload[query_field], raw.mean(axis=-2), rtol=1e-6, atol=1e-7)
            for model_index in range(raw.shape[0]):
                for condition_index in range(raw.shape[1]):
                    metrics = affine_attention_metrics(raw[model_index, condition_index])
                    for name, values in metrics.items():
                        np.testing.assert_allclose(payload[f"{metric_prefix}_{name}"][model_index, condition_index], values, rtol=1e-5, atol=1e-6)
        logits = np.asarray(payload["event_actor_logits"], dtype=np.float64)
        first_stored = np.asarray(payload["event_first_press"], dtype=np.int64)
        qualifying_stored = np.asarray(payload["event_qualifying_response"], dtype=bool)
        for model_index in range(2):
            for condition_index in range(2):
                first, qualifying = first_press_from_logits(logits[model_index, condition_index])
                np.testing.assert_array_equal(first_stored[model_index, condition_index], first)
                np.testing.assert_array_equal(qualifying_stored[model_index, condition_index], qualifying)
        psych_shape = (2, 4, len(CHANGE_MAGNITUDES), 2)
        counts = np.asarray(payload["psychometric_response_count"], dtype=np.int64)
        rates = np.asarray(payload["psychometric_response_rate"], dtype=np.float64)
        histogram = np.asarray(payload["psychometric_press_histogram"], dtype=np.int64)
        if counts.shape != psych_shape or rates.shape != psych_shape or histogram.shape != psych_shape + (TIMESTEPS + 1,):
            raise ValueError("psychometric cache shapes do not satisfy the contract")
        np.testing.assert_array_equal(histogram.sum(axis=-1), psychometric_trials)
        np.testing.assert_array_equal(counts, histogram[..., QUALIFYING_RESPONSE_FRAME + 1:].sum(axis=-1))
        np.testing.assert_allclose(rates, counts / psychometric_trials, rtol=0.0, atol=1e-12)
        checkpoint_iterations = [int(v) for v in payload["checkpoint_iterations"].tolist()]
        checkpoint_hashes = [str(v) for v in payload["checkpoint_sha256"].tolist()]
    assert checkpoint_iterations is not None
    assert checkpoint_hashes is not None
    return {
        "cache_path": str(cache_path.resolve()),
        "cache_sha256": cache_sha256,
        "attention_trials": attention_trials,
        "nochange_trials": nochange_trials,
        "psychometric_trials": psychometric_trials,
        "checkpoint_iterations": checkpoint_iterations,
        "checkpoint_sha256": checkpoint_hashes,
        "device": "cpu",
        "attention_topology": "affine_ew 4x4 spatial self-attention",
    }


def _mean_interval(values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    array = np.asarray(values, dtype=np.float64)
    mean = array.mean(axis=0)
    if array.shape[0] <= 1:
        return mean, mean, mean
    half = 1.96 * array.std(axis=0, ddof=1) / np.sqrt(array.shape[0])
    return mean, mean - half, mean + half


def _wilson_interval(count: np.ndarray, trials: int) -> tuple[np.ndarray, np.ndarray]:
    count = np.asarray(count, dtype=np.float64)
    z = 1.96
    proportion = count / trials
    denominator = 1.0 + z * z / trials
    center = (proportion + z * z / (2 * trials)) / denominator
    half = z * np.sqrt(proportion * (1 - proportion) / trials + z * z / (4 * trials * trials)) / denominator
    return center - half, center + half


def _save_figure(figure: Any, base: Path) -> list[Path]:
    outputs = []
    for suffix, kwargs in ((".pdf", {}), (".svg", {}), (".png", {"dpi": 300})):
        path = base.with_suffix(suffix)
        figure.savefig(path, bbox_inches="tight", **kwargs)
        outputs.append(path)
    return outputs


def _draw_location_map(axis: Any, values: np.ndarray, *, vmax: float, cue: bool, change_index: int | None):
    import matplotlib.pyplot as plt
    image = axis.imshow(np.asarray(values).reshape(2, 2), cmap="cividis", vmin=0.0, vmax=vmax, interpolation="nearest")
    axis.set_xticks([])
    axis.set_yticks([])
    if cue:
        axis.plot(-0.32, -0.32, marker="o", markersize=4, color="#D55E00", clip_on=False)
    if change_index is not None:
        row, column = divmod(change_index, 2)
        axis.add_patch(plt.Rectangle((column - 0.48, row - 0.48), 0.96, 0.96, fill=False, edgecolor="#CC79A7", linewidth=1.5))
    return image


def _build_event_map_figure(payload: Any, output_dir: Path) -> list[Path]:
    import matplotlib.pyplot as plt
    maps = np.asarray(payload["event_query_averaged_attention"], dtype=np.float64).mean(axis=2)
    figure, axes = plt.subplots(4, TIMESTEPS, figsize=(14.8, 8.4), squeeze=False)
    image = None
    model_labels = ("standard affine_ew λ=1.0", "high-decay affine_ew λ=0.8")
    condition_labels = ("valid S1 change", "forced-invalid S4 change")
    time_labels = ("t0 blank", "t1 cue", "t2 delay", "t3 array", "t4 maintain", "t5 change", "t6 response")
    for row in range(4):
        model, condition = divmod(row, 2)
        for timestep in range(TIMESTEPS):
            change = (VALID_CHANGE_INDEX if condition == 0 else INVALID_CHANGE_INDEX) if timestep == 5 else None
            image = _draw_location_map(axes[row, timestep], maps[model, condition, timestep], vmax=1.0, cue=timestep == 1, change_index=change)
            if row == 0:
                axes[row, timestep].set_title(time_labels[timestep], fontsize=9)
            if timestep == 0:
                axes[row, timestep].set_ylabel(f"{model_labels[model]}\n{condition_labels[condition]}", rotation=0, ha="right", va="center", fontsize=8.5)
    figure.subplots_adjust(left=0.20, right=0.92, top=0.88, bottom=0.08, wspace=0.06, hspace=0.22)
    figure.suptitle("VDA4 affine_ew event-locked attention · query-averaged spatial maps · 100% cue · Δ=15°", fontweight="bold")
    figure.text(0.5, 0.025, "Orange dot marks cue S1; magenta border marks the forced change. Shared [0,1] scale; uniform spatial baseline is 1/4.", ha="center", fontsize=9)
    figure.colorbar(image, ax=axes.ravel().tolist(), fraction=0.012, pad=0.015, label="attention mass")
    outputs = _save_figure(figure, output_dir / "attention_event_query_averaged")
    plt.close(figure)
    return outputs


def _build_query_level_figures(payload: Any, output_dir: Path) -> list[Path]:
    import matplotlib.pyplot as plt
    query_mean = np.asarray(payload["event_raw_attention"], dtype=np.float64).mean(axis=2)
    outputs = []
    for condition, condition_name in enumerate(EVENT_CONDITIONS):
        figure, axes = plt.subplots(8, TIMESTEPS, figsize=(14.8, 13.0), squeeze=False)
        image = None
        for model in range(2):
            for query in range(QUERY_COUNT):
                row = model * QUERY_COUNT + query
                for timestep in range(TIMESTEPS):
                    change = (VALID_CHANGE_INDEX if condition == 0 else INVALID_CHANGE_INDEX) if timestep == 5 else None
                    image = _draw_location_map(axes[row, timestep], query_mean[model, condition, timestep, query], vmax=1.0, cue=timestep == 1, change_index=change)
                    if row == 0:
                        axes[row, timestep].set_title(f"t{timestep}", fontsize=9)
                    if timestep == 0:
                        label = "standard λ=1.0" if model == 0 else "high decay λ=0.8"
                        axes[row, timestep].set_ylabel(f"{label}\nquery S{query + 1}", rotation=0, ha="right", va="center", fontsize=8.5)
        figure.subplots_adjust(left=0.18, right=0.92, top=0.90, bottom=0.06, wspace=0.06, hspace=0.14)
        figure.suptitle(f"VDA4 affine_ew query-level spatial attention · {condition_name.replace('_', ' ')} · common [0,1] scale", fontweight="bold")
        figure.colorbar(image, ax=axes.ravel().tolist(), fraction=0.012, pad=0.015, label="attention mass")
        outputs.extend(_save_figure(figure, output_dir / f"attention_query_level_{condition_name}"))
        plt.close(figure)
    return outputs


def _build_nochange_figure(payload: Any, output_dir: Path) -> list[Path]:
    import matplotlib.pyplot as plt
    raw = np.asarray(payload["nochange_raw_attention"], dtype=np.float64)
    maps = raw.mean(axis=2).mean(axis=-2)
    figure, axes = plt.subplots(8, TIMESTEPS, figsize=(14.8, 13.0), squeeze=False)
    image = None
    for model in range(2):
        for validity_index, validity in enumerate(DISPLAYED_VALIDITIES):
            row = model * len(DISPLAYED_VALIDITIES) + validity_index
            for timestep in range(TIMESTEPS):
                image = _draw_location_map(axes[row, timestep], maps[model, validity_index, timestep], vmax=1.0, cue=timestep == 1, change_index=None)
                if row == 0:
                    axes[row, timestep].set_title(f"t{timestep}", fontsize=9)
                if timestep == 0:
                    label = "standard λ=1.0" if model == 0 else "high decay λ=0.8"
                    axes[row, timestep].set_ylabel(f"{label}\n{int(validity * 100)}% cue", rotation=0, ha="right", va="center", fontsize=8.5)
    figure.subplots_adjust(left=0.18, right=0.92, top=0.90, bottom=0.06, wspace=0.06, hspace=0.14)
    figure.suptitle("VDA4 affine_ew no-change cue-proportion sweep · query-averaged spatial attention", fontweight="bold")
    figure.colorbar(image, ax=axes.ravel().tolist(), fraction=0.012, pad=0.015, label="attention mass")
    outputs = _save_figure(figure, output_dir / "attention_nochange_spatial")
    plt.close(figure)
    return outputs


def _plot_trial_series(axis: Any, x: np.ndarray, values: np.ndarray, *, label: str, color: str, linestyle: str):
    mean, low, high = _mean_interval(values)
    axis.plot(x, mean, color=color, linestyle=linestyle, linewidth=2, label=label)
    axis.fill_between(x, low, high, color=color, alpha=0.10, linewidth=0)


def _build_metric_figure(payload: Any, output_dir: Path, summary: dict[str, Any]) -> list[Path]:
    import matplotlib.pyplot as plt
    motion = np.asarray(payload["event_temporal_motion"], dtype=np.float64)
    selectivity = np.asarray(payload["event_selectivity"], dtype=np.float64)
    peak = np.asarray(payload["event_peak_key_mass"], dtype=np.float64)
    spatial = np.asarray(payload["event_spatial_mass"], dtype=np.float64)
    qualifying = np.asarray(payload["event_qualifying_response"], dtype=bool)
    figure, axes = plt.subplots(2, 3, figsize=(15.2, 8.8), constrained_layout=True)
    colors = ("#0072B2", "#D55E00")
    line_styles = ("-", "--")
    model_labels = ("standard λ=1.0", "high decay λ=0.8")
    condition_labels = ("valid", "forced invalid")
    for model in range(2):
        for condition in range(2):
            label = f"{model_labels[model]} · {condition_labels[condition]}"
            _plot_trial_series(axes[0, 0], np.arange(1, TIMESTEPS), motion[model, condition], label=label, color=colors[model], linestyle=line_styles[condition])
            _plot_trial_series(axes[0, 1], np.arange(TIMESTEPS), selectivity[model, condition], label=label, color=colors[model], linestyle=line_styles[condition])
            _plot_trial_series(axes[0, 2], np.arange(TIMESTEPS), peak[model, condition], label=label, color=colors[model], linestyle=line_styles[condition])
            location = VALID_CHANGE_INDEX if condition == 0 else INVALID_CHANGE_INDEX
            _plot_trial_series(axes[1, 0], np.arange(TIMESTEPS), spatial[model, condition, :, :, CUE_INDEX], label=label, color=colors[model], linestyle=line_styles[condition])
            _plot_trial_series(axes[1, 1], np.arange(TIMESTEPS), spatial[model, condition, :, :, location], label=label, color=colors[model], linestyle=line_styles[condition])
            for responded, marker, alpha, suffix in ((True, "o", 1.0, "response"), (False, "s", 0.65, "no response")):
                mask = qualifying[model, condition] == responded
                if np.any(mask):
                    values = spatial[model, condition, mask, :, location]
                    axes[1, 2].plot(np.arange(TIMESTEPS), values.mean(axis=0), color=colors[model], linestyle=line_styles[condition], marker=marker, markersize=3, alpha=alpha, label=f"{model_labels[model]} · {condition_labels[condition]} · {suffix} (n={mask.sum()})")
    titles = (
        "A  Temporal attention motion (primary)",
        "B  Attention selectivity (1 − normalized entropy)",
        "C  Peak-key mass",
        "D  Combined attention to cued S1",
        "E  Attention to condition change location",
        "F  Change-location attention by qualifying response",
    )
    for axis, title in zip(axes.ravel(), titles):
        axis.set_title(title, loc="left", fontweight="bold")
        axis.grid(alpha=0.18)
        axis.axvline(5, color="0.5", linestyle=":", linewidth=1)
        axis.set_xlabel("logical frame" if axis is not axes[0, 0] else "transition ending at frame")
    axes[0, 0].set_ylabel("total variation")
    axes[0, 1].set_ylabel("selectivity")
    axes[0, 2].set_ylabel("attention mass")
    axes[1, 0].set_ylabel("attention mass")
    axes[1, 1].set_ylabel("attention mass")
    axes[1, 2].set_ylabel("attention mass")
    axes[0, 0].legend(fontsize=7, frameon=False)
    axes[1, 2].legend(fontsize=6.2, frameon=False)
    primary = summary["primary_event_attention_motion"]
    figure.suptitle("VDA4 affine_ew spatial-attention dynamics · high decay versus standard\n" + f"Primary high−standard motion difference = {primary['mean_difference']:+.4f} (paired 95% bootstrap CI {primary['ci_low']:+.4f}, {primary['ci_high']:+.4f})", fontweight="bold")
    outputs = _save_figure(figure, output_dir / "attention_metrics_and_response_strata")
    plt.close(figure)
    return outputs


def _build_psychometric_figure(payload: Any, output_dir: Path) -> list[Path]:
    import matplotlib.pyplot as plt
    counts = np.asarray(payload["psychometric_response_count"], dtype=np.int64)
    rates = np.asarray(payload["psychometric_response_rate"], dtype=np.float64)
    trials = int(_scalar(payload, "psychometric_trials"))
    figure, axes = plt.subplots(2, 3, figsize=(15.4, 9.2), constrained_layout=True)
    model_colors = ("#0072B2", "#D55E00")
    condition_styles = ("-", "--")
    condition_markers = ("o", "s")
    for validity_index, validity in enumerate(DISPLAYED_VALIDITIES):
        axis = axes.ravel()[validity_index]
        for model in range(2):
            for condition in range(2):
                lower, upper = _wilson_interval(counts[model, validity_index, :, condition], trials)
                label = ("standard λ=1.0" if model == 0 else "high decay λ=0.8") + (" · valid" if condition == 0 else " · forced invalid")
                axis.fill_between(CHANGE_MAGNITUDES, lower, upper, color=model_colors[model], alpha=0.08, linewidth=0)
                axis.plot(CHANGE_MAGNITUDES, rates[model, validity_index, :, condition], color=model_colors[model], linestyle=condition_styles[condition], marker=condition_markers[condition], markersize=3.5, linewidth=1.8, label=label)
        axis.set_title(f"{chr(65 + validity_index)}  {int(validity * 100)}% displayed cue", loc="left", fontweight="bold")
        axis.set_ylim(-0.02, 1.02)
        axis.set_xlabel("orientation change (degrees)")
        axis.set_ylabel("P(qualifying response)")
        axis.grid(alpha=0.18)
    axes[0, 0].legend(fontsize=7, frameon=False)
    differences = rates[1] - rates[0]
    vmax = max(float(np.abs(differences).max()), 1e-6)
    images = []
    for condition in range(2):
        axis = axes[1, 1 + condition]
        images.append(axis.imshow(differences[:, :, condition], aspect="auto", origin="lower", cmap="coolwarm", vmin=-vmax, vmax=vmax, interpolation="nearest"))
        axis.set_yticks(range(len(DISPLAYED_VALIDITIES)), [f"{int(v * 100)}%" for v in DISPLAYED_VALIDITIES])
        axis.set_xticks(range(len(CHANGE_MAGNITUDES)), [str(int(v)) for v in CHANGE_MAGNITUDES], rotation=45)
        axis.set_xlabel("orientation change (degrees)")
        axis.set_ylabel("displayed cue proportion")
        axis.set_title(f"{'E' if condition == 0 else 'F'}  High−standard response rate · {'valid' if condition == 0 else 'forced invalid'}", loc="left", fontweight="bold")
    figure.colorbar(images[-1], ax=[axes[1, 1], axes[1, 2]], fraction=0.025, pad=0.02, label="response-rate difference")
    figure.suptitle(f"VDA4 affine_ew paired psychometrics · n={trials} shared trials/point · first press at frame ≥5 qualifies\nBands are Wilson 95% evaluation-trial intervals; invalid at 100% displayed cue is a forced intervention.", fontweight="bold")
    outputs = _save_figure(figure, output_dir / "psychometric_valid_invalid_comparison")
    plt.close(figure)
    return outputs


def _paired_summary(high: np.ndarray, standard: np.ndarray, *, seed: int) -> dict[str, Any]:
    result = paired_mean_difference(high, standard, seed=seed)
    result["standard_mean"] = float(np.asarray(standard, dtype=np.float64).mean())
    result["high_decay_mean"] = float(np.asarray(high, dtype=np.float64).mean())
    return result


def build_numeric_summary(payload: Any) -> tuple[dict[str, Any], dict[str, tuple[np.ndarray, np.ndarray]]]:
    motion = np.asarray(payload["event_temporal_motion"], dtype=np.float64)
    selectivity = np.asarray(payload["event_selectivity"], dtype=np.float64)
    peak = np.asarray(payload["event_peak_key_mass"], dtype=np.float64)
    spatial = np.asarray(payload["event_spatial_mass"], dtype=np.float64)
    nochange_motion = np.asarray(payload["nochange_temporal_motion"], dtype=np.float64)
    nochange_spatial = np.asarray(payload["nochange_spatial_mass"], dtype=np.float64)
    qualifying = np.asarray(payload["event_qualifying_response"], dtype=np.float64)
    metric_pairs: dict[str, tuple[np.ndarray, np.ndarray]] = {
        "primary_event_attention_motion": (motion[1].mean(axis=(0, 2)), motion[0].mean(axis=(0, 2))),
        "event_selectivity": (selectivity[1].mean(axis=(0, 2)), selectivity[0].mean(axis=(0, 2))),
        "event_peak_key_mass": (peak[1].mean(axis=(0, 2)), peak[0].mean(axis=(0, 2))),
        "event_cue_location_mass": (spatial[1, :, :, :, CUE_INDEX].mean(axis=(0, 2)), spatial[0, :, :, :, CUE_INDEX].mean(axis=(0, 2))),
        "nochange_attention_motion": (nochange_motion[1].mean(axis=(0, 2)), nochange_motion[0].mean(axis=(0, 2))),
        "cue_orienting_t1_minus_t0": ((nochange_spatial[1, :, :, 1, CUE_INDEX] - nochange_spatial[1, :, :, 0, CUE_INDEX]).mean(axis=0), (nochange_spatial[0, :, :, 1, CUE_INDEX] - nochange_spatial[0, :, :, 0, CUE_INDEX]).mean(axis=0)),
    }
    for condition, condition_name in enumerate(EVENT_CONDITIONS):
        location = VALID_CHANGE_INDEX if condition == 0 else INVALID_CHANGE_INDEX
        metric_pairs[f"{condition_name}_attention_motion"] = (motion[1, condition].mean(axis=1), motion[0, condition].mean(axis=1))
        metric_pairs[f"{condition_name}_change_reorientation_t5_minus_t4"] = (spatial[1, condition, :, 5, location] - spatial[1, condition, :, 4, location], spatial[0, condition, :, 5, location] - spatial[0, condition, :, 4, location])
        metric_pairs[f"{condition_name}_qualifying_response"] = (qualifying[1, condition], qualifying[0, condition])
    estimates = {name: _paired_summary(high, standard, seed=7200 + index * 37) for index, (name, (high, standard)) in enumerate(metric_pairs.items())}
    primary = estimates["primary_event_attention_motion"]
    primary["hypothesis_verdict"] = "supported" if primary["ci_low"] > 0 else "opposite" if primary["ci_high"] < 0 else "inconclusive"
    counts = np.asarray(payload["psychometric_response_count"], dtype=np.int64)
    rates = np.asarray(payload["psychometric_response_rate"], dtype=np.float64)
    validity_index = int(np.where(np.isclose(DISPLAYED_VALIDITIES, 1.0))[0][0])
    magnitude_index = int(np.where(np.isclose(CHANGE_MAGNITUDES, EVENT_MAGNITUDE))[0][0])
    summary = {
        "model_family": "affine_ew",
        "hypothesis_definition": "High decay is more active if its paired mean frame-to-frame total variation over the full 4-query × 4-key affine attention map is larger. Total mass is not used because every query row is softmax-normalized to one.",
        "primary_event_attention_motion": primary,
        "secondary_estimates": {name: value for name, value in estimates.items() if name != "primary_event_attention_motion"},
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
        "psychometric_anchor_100pct_15deg": {
            MODEL_ROLES[model]: {
                EVENT_CONDITIONS[condition]: {
                    "response_count": int(counts[model, validity_index, magnitude_index, condition]),
                    "trials": int(_scalar(payload, "psychometric_trials")),
                    "response_rate": float(rates[model, validity_index, magnitude_index, condition]),
                }
                for condition in range(2)
            }
            for model in range(2)
        },
        "interpretation_boundary": "This is a frozen-checkpoint comparison: standard affine_ew iteration 20000 versus high-decay affine_ew iteration 17949. The estimates do not isolate memory decay from training maturity and do not quantify training-seed uncertainty.",
    }
    return summary, metric_pairs


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_tables(payload: Any, summary: dict[str, Any], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    estimates = {"primary_event_attention_motion": summary["primary_event_attention_motion"]}
    estimates.update(summary["secondary_estimates"])
    metric_rows = []
    for metric, estimate in estimates.items():
        metric_rows.append({"metric": metric, "standard_mean": f"{estimate['standard_mean']:.10g}", "high_decay_mean": f"{estimate['high_decay_mean']:.10g}", "high_minus_standard": f"{estimate['mean_difference']:.10g}", "paired_ci_low": f"{estimate['ci_low']:.10g}", "paired_ci_high": f"{estimate['ci_high']:.10g}", "paired_n": int(estimate["n"]), "bootstrap_samples": int(estimate["bootstrap_samples"]), "bootstrap_seed": int(estimate["seed"])})
    metric_path = output_dir / "paired_attention_and_response_estimates.csv"
    _write_csv(metric_path, list(metric_rows[0]), metric_rows)

    counts = np.asarray(payload["psychometric_response_count"], dtype=np.int64)
    rates = np.asarray(payload["psychometric_response_rate"], dtype=np.float64)
    trials = int(_scalar(payload, "psychometric_trials"))
    psych_rows = []
    for model in range(2):
        for validity_index, validity in enumerate(DISPLAYED_VALIDITIES):
            for magnitude_index, magnitude in enumerate(CHANGE_MAGNITUDES):
                for condition in range(2):
                    low, high = _wilson_interval(counts[model, validity_index, magnitude_index, condition], trials)
                    psych_rows.append({"model": MODEL_ROLES[model], "memory_decay": 1.0 if model == 0 else 0.8, "displayed_validity": float(validity), "orientation_change_degrees": float(magnitude), "condition": EVENT_CONDITIONS[condition], "response_count": int(counts[model, validity_index, magnitude_index, condition]), "trials": trials, "response_rate": f"{rates[model, validity_index, magnitude_index, condition]:.10g}", "wilson_ci_low": f"{float(low):.10g}", "wilson_ci_high": f"{float(high):.10g}"})
    psych_path = output_dir / "psychometric_response_rates.csv"
    _write_csv(psych_path, list(psych_rows[0]), psych_rows)

    time_rows = []
    for prefix in ("event_temporal_motion", "event_selectivity", "event_peak_key_mass", "event_spatial_mass"):
        values = np.asarray(payload[prefix], dtype=np.float64)
        for model in range(2):
            for condition in range(2):
                location = VALID_CHANGE_INDEX if condition == 0 else INVALID_CHANGE_INDEX
                if prefix == "event_spatial_mass":
                    series = values[model, condition, :, :, location]
                    metric_name = "change_location_mass"
                else:
                    series = values[model, condition]
                    metric_name = prefix.removeprefix("event_")
                for timestep in range(series.shape[-1]):
                    sample = series[..., timestep]
                    time_rows.append({"metric": metric_name, "model": MODEL_ROLES[model], "condition": EVENT_CONDITIONS[condition], "logical_index": timestep + (1 if prefix == "event_temporal_motion" else 0), "mean": f"{sample.mean():.10g}", "standard_error": f"{sample.std(ddof=1) / np.sqrt(sample.size):.10g}", "trials": sample.size})
    time_path = output_dir / "event_attention_timecourses.csv"
    _write_csv(time_path, list(time_rows[0]), time_rows)
    return [metric_path, psych_path, time_path]


def write_report(run_root: Path, summary: dict[str, Any], records: dict[str, dict[str, Any]]) -> Path:
    primary = summary["primary_event_attention_motion"]
    verdict_text = {"supported": "supported for this frozen checkpoint pair", "opposite": "contradicted for this frozen checkpoint pair", "inconclusive": "not resolved for this frozen checkpoint pair"}[primary["hypothesis_verdict"]]
    secondary = summary["secondary_estimates"]
    anchor = summary["psychometric_anchor_100pct_15deg"]
    budgets = summary["event_condition"]
    report = f"""# Standalone VDA4 affine_ew memory-decay comparison

## Result

The prespecified activity hypothesis is **{verdict_text}**. Mean frame-to-frame total variation over the complete 4-query × 4-key affine attention map was {primary['standard_mean']:.4f} for the standard checkpoint and {primary['high_decay_mean']:.4f} for the high-decay checkpoint. The paired high-minus-standard difference was {primary['mean_difference']:+.4f} (95% bootstrap CI {primary['ci_low']:+.4f} to {primary['ci_high']:+.4f}; n={primary['n']} matched trial-level estimates).

“More active” means greater frame-to-frame total variation over the complete normalized spatial attention map. It is not total attention mass. Affine_ew has one spatial key per location; there is no separate image-key versus recurrent-memory-key source block to report.

## Important boundary

This is a **frozen-checkpoint comparison, not a decay-only causal estimate**. The standard affine_ew checkpoint is iteration {int(records['standard']['checkpoint_iteration'])}; the high-decay affine_ew checkpoint is iteration {int(records['high_decay']['checkpoint_iteration'])}. The models differ in memory decay and training maturity. There is one training seed per model, so confidence intervals describe paired evaluation-trial uncertainty only.

The 100%-cue invalid condition is a deliberate forced intervention (cue S1, change S4), not a trial that the 100%-valid environment would naturally sample.

## Checkpoints

| role | iteration | resolved decay | frozen SHA-256 |
|---|---:|---:|---|
| standard affine_ew | {int(records['standard']['checkpoint_iteration'])} | 1.00 | `{records['standard']['sha256']}` |
| high-decay affine_ew | {int(records['high_decay']['checkpoint_iteration'])} | 0.80 | `{records['high_decay']['sha256']}` |

Both checkpoints validate as VDA4, xLSTM, `affine_ew`, `d_mem=128`, convolutional frontend, and 2×2/four-patch geometry.

## Event-locked findings (100% displayed cue, Δ=15°)

| measure | high minus standard | paired 95% CI |
|---|---:|---:|
| attention motion, valid | {secondary['valid_attention_motion']['mean_difference']:+.4f} | [{secondary['valid_attention_motion']['ci_low']:+.4f}, {secondary['valid_attention_motion']['ci_high']:+.4f}] |
| attention motion, forced invalid | {secondary['forced_invalid_attention_motion']['mean_difference']:+.4f} | [{secondary['forced_invalid_attention_motion']['ci_low']:+.4f}, {secondary['forced_invalid_attention_motion']['ci_high']:+.4f}] |
| selectivity | {secondary['event_selectivity']['mean_difference']:+.4f} | [{secondary['event_selectivity']['ci_low']:+.4f}, {secondary['event_selectivity']['ci_high']:+.4f}] |
| peak-key mass | {secondary['event_peak_key_mass']['mean_difference']:+.4f} | [{secondary['event_peak_key_mass']['ci_low']:+.4f}, {secondary['event_peak_key_mass']['ci_high']:+.4f}] |
| cue-location mass | {secondary['event_cue_location_mass']['mean_difference']:+.4f} | [{secondary['event_cue_location_mass']['ci_low']:+.4f}, {secondary['event_cue_location_mass']['ci_high']:+.4f}] |
| valid change reorientation, t5−t4 | {secondary['valid_change_reorientation_t5_minus_t4']['mean_difference']:+.4f} | [{secondary['valid_change_reorientation_t5_minus_t4']['ci_low']:+.4f}, {secondary['valid_change_reorientation_t5_minus_t4']['ci_high']:+.4f}] |
| invalid change reorientation, t5−t4 | {secondary['forced_invalid_change_reorientation_t5_minus_t4']['mean_difference']:+.4f} | [{secondary['forced_invalid_change_reorientation_t5_minus_t4']['ci_low']:+.4f}, {secondary['forced_invalid_change_reorientation_t5_minus_t4']['ci_high']:+.4f}] |

At the matched psychometric anchor (100% displayed cue, Δ=15°, {budgets['psychometric_trials']} trials/point), standard response rates were {anchor['standard']['valid']['response_rate']:.3f} valid and {anchor['standard']['forced_invalid']['response_rate']:.3f} forced invalid; high-decay rates were {anchor['high_decay']['valid']['response_rate']:.3f} valid and {anchor['high_decay']['forced_invalid']['response_rate']:.3f} forced invalid.

## Design

- Event attention: {budgets['attention_trials']} matched valid and forced-invalid trials, identical latent videos through t4, change at t5.
- No-change attention: {budgets['nochange_trials']} trials at 25%, 50%, 75%, and 100% displayed cue proportions.
- Psychometrics: {budgets['psychometric_trials']} shared trials at each of 4 displayed cue proportions × 10 magnitudes × 2 change locations.
- Response: first argmax change action; a first press at frame 5 or 6 qualifies.
- Inference: deterministic paired bootstrap over evaluation trials (10,000 resamples); Wilson intervals for psychometric rates.
- Execution: CPU only; the comparison did not use MPS.

## Figures

- `figures/attention_event_query_averaged.pdf`: direct standard/high-decay, valid/invalid, query-averaged spatial maps.
- `figures/attention_query_level_valid.pdf` and `figures/attention_query_level_forced_invalid.pdf`: query-preserving spatial maps; no query-axis collapse.
- `figures/attention_nochange_spatial.pdf`: cue-proportion attentional patterns without physical changes.
- `figures/attention_metrics_and_response_strata.pdf`: activity, selectivity, peak-key mass, cue/change location mass, and response-stratified traces.
- `figures/psychometric_valid_invalid_comparison.pdf`: valid/forced-invalid response curves and high-minus-standard heatmaps.

PDF, SVG, and 300-dpi PNG versions accompany every figure. Exact rates and estimates are in `tables/`; raw evidence is in `data/comparison_evidence.npz`; executable source snapshots and runtime metadata are in `provenance/`.
"""
    report_path = run_root / "REPORT.md"
    if report_path.exists():
        raise FileExistsError(f"refusing to overwrite report: {report_path}")
    report_path.write_text(report, encoding="utf-8")
    return report_path


def verify_rendered_outputs(run_root: Path) -> dict[str, Any]:
    from PIL import Image
    figure_dir = run_root / "figures"
    pdfs = sorted(figure_dir.glob("*.pdf"))
    pngs = sorted(figure_dir.glob("*.png"))
    svgs = sorted(figure_dir.glob("*.svg"))
    if not (len(pdfs) == len(pngs) == len(svgs) == 6):
        raise RuntimeError(f"expected 6 PDF/PNG/SVG figure triplets; got {len(pdfs)}/{len(pngs)}/{len(svgs)}")
    pdf_records = []
    with tempfile.TemporaryDirectory(prefix="vda4-affine-pdf-verify-") as temporary_directory:
        temporary_root = Path(temporary_directory)
        for index, path in enumerate(pdfs):
            info = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True).stdout
            page_lines = [line for line in info.splitlines() if line.startswith("Pages:")]
            if len(page_lines) != 1 or int(page_lines[0].split(":", 1)[1].strip()) != 1:
                raise RuntimeError(f"figure PDF must be exactly one page: {path}")
            raster_base = temporary_root / f"figure_{index}"
            subprocess.run(["pdftoppm", "-f", "1", "-singlefile", "-r", "120", "-png", str(path), str(raster_base)], check=True, capture_output=True)
            with Image.open(raster_base.with_suffix(".png")) as raster:
                width, height = raster.size
            if width < 700 or height < 400:
                raise RuntimeError(f"rendered PDF is unexpectedly small: {path}")
            pdf_records.append({"path": str(path.relative_to(run_root)), "pages": 1, "render_width": width, "render_height": height})
    for path in pngs:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            if image.width < 1000 or image.height < 600:
                raise RuntimeError(f"PNG is unexpectedly small: {path} ({image.size})")
    for path in svgs:
        text = path.read_text(encoding="utf-8")
        if "<svg" not in text or len(text) < 1000:
            raise RuntimeError(f"SVG failed structural validation: {path}")
    expected_tables = {"paired_attention_and_response_estimates.csv": 12, "psychometric_response_rates.csv": 161, "event_attention_timecourses.csv": 70}
    table_lines = {}
    for name, minimum_lines in expected_tables.items():
        path = run_root / "tables" / name
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) < minimum_lines:
            raise RuntimeError(f"table {path} has {len(lines)} lines, expected at least {minimum_lines}")
        table_lines[name] = len(lines)
    return {"figure_triplets": len(pdfs), "pdf_records": pdf_records, "table_lines": table_lines}


def _runtime_versions(torch_module: Any) -> dict[str, str]:
    import matplotlib
    import scipy
    from PIL import __version__ as pillow_version
    return {"python": platform.python_version(), "platform": platform.platform(), "numpy": np.__version__, "matplotlib": matplotlib.__version__, "scipy": scipy.__version__, "pillow": pillow_version, "torch": torch_module.__version__, "python_executable": str(Path(sys.executable).resolve())}


def configure_matplotlib_for_artifacts(matplotlib_module: Any) -> None:
    matplotlib_module.use("Agg", force=True)
    matplotlib_module.rcParams["pdf.fonttype"] = 42
    matplotlib_module.rcParams["ps.fonttype"] = 42
    matplotlib_module.rcParams["svg.fonttype"] = "none"


def _snapshot_sources(run_root: Path, captured: dict[str, bytes]) -> dict[str, dict[str, Any]]:
    records = {}
    root = run_root / "provenance" / "source_snapshot"
    for relative, content in captured.items():
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        records[relative] = {"snapshot_path": str(destination.relative_to(run_root)), "sha256": sha256_bytes(content), "bytes": len(content)}
    return records


def _write_json_exclusive(path: Path, payload: Any) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite JSON artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--standard-checkpoint", type=Path, required=True)
    parser.add_argument("--high-decay-checkpoint", type=Path, required=True)
    parser.add_argument("--attention-trials", type=int, default=256)
    parser.add_argument("--nochange-trials", type=int, default=128)
    parser.add_argument("--psychometric-trials", type=int, default=300)
    parser.add_argument("--threads", type=int, default=3)
    args = parser.parse_args(argv)
    run_root = args.run_root.expanduser().resolve()
    if run_root.exists():
        raise FileExistsError(f"analysis output already exists: {run_root}")
    if args.threads <= 0:
        raise ValueError("--threads must be positive")

    captured_sources = capture_executable_sources()
    run_root.mkdir(parents=True)
    checkpoint_dir = run_root / "provenance" / "checkpoints"
    frozen_records = []
    for role, source in (("standard", args.standard_checkpoint), ("high_decay", args.high_decay_checkpoint)):
        destination = checkpoint_dir / f"{role}.pt"
        record = _copy_frozen_checkpoint(source, destination)
        record["role"] = role
        record["snapshot_path"] = str(destination.relative_to(run_root))
        frozen_records.append(record)
    frozen_manifest = {"schema_version": 1, "checkpoints": frozen_records}
    _write_json_exclusive(run_root / "frozen_inputs.json", frozen_manifest)

    sys.dont_write_bytecode = True
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    import torch
    import matplotlib
    torch.set_num_threads(args.threads)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        pass
    configure_matplotlib_for_artifacts(matplotlib)
    _, records = _load_frozen_inputs(run_root)
    runtime_versions = _runtime_versions(torch)
    command = " ".join(shlex.quote(value) for value in ([str(Path(sys.executable).resolve()), str(Path(__file__).resolve())] + (argv if argv is not None else sys.argv[1:])))
    _write_json_exclusive(run_root / "provenance" / "analysis_config.json", {"attention_trials": args.attention_trials, "nochange_trials": args.nochange_trials, "psychometric_trials": args.psychometric_trials, "threads": args.threads, "device": "cpu", "feedback": "affine_ew", "primary_activity_metric": "mean frame-to-frame total variation over the full 4x4 attention map", "response_rule": "first argmax change action at frame >= 5"})
    started_at = datetime.now(timezone.utc).isoformat()
    cache_path = compute_comparison_cache(run_root, records, attention_trials=args.attention_trials, nochange_trials=args.nochange_trials, psychometric_trials=args.psychometric_trials, torch_module=torch)
    cache_metadata = validate_comparison_cache(cache_path, expected_attention_trials=args.attention_trials, expected_nochange_trials=args.nochange_trials, expected_psychometric_trials=args.psychometric_trials)
    with np.load(cache_path, allow_pickle=False) as payload:
        summary, _ = build_numeric_summary(payload)
        figure_dir = run_root / "figures"
        table_dir = run_root / "tables"
        figure_dir.mkdir(parents=True, exist_ok=True)
        _build_event_map_figure(payload, figure_dir)
        _build_query_level_figures(payload, figure_dir)
        _build_nochange_figure(payload, figure_dir)
        _build_metric_figure(payload, figure_dir, summary)
        _build_psychometric_figure(payload, figure_dir)
        write_tables(payload, summary, table_dir)
    _write_json_exclusive(run_root / "SUMMARY.json", summary)
    write_report(run_root, summary, records)
    source_records = _snapshot_sources(run_root, captured_sources)
    _write_json_exclusive(run_root / "provenance" / "runtime_versions.json", runtime_versions)
    (run_root / "provenance" / "COMMAND.txt").write_text(command + "\n", encoding="utf-8")
    verification = verify_rendered_outputs(run_root)
    _write_json_exclusive(run_root / "provenance" / "render_verification.json", verification)
    assert_sources_unchanged(captured_sources)
    for role, record in records.items():
        if sha256_path(record["snapshot_path"]) != str(record["sha256"]):
            raise RuntimeError(f"frozen {role} checkpoint changed before finalization")
    inventory = []
    for path in sorted(run_root.rglob("*")):
        if path.is_file() and path.name != "MANIFEST.json":
            inventory.append({"path": str(path.relative_to(run_root)), "bytes": path.stat().st_size, "sha256": sha256_path(path)})
    completed_at = datetime.now(timezone.utc).isoformat()
    manifest = {"schema_version": 1, "status": "complete", "analysis": "standalone_vda4_affine_ew_memory_decay_comparison", "started_at_utc": started_at, "completed_at_utc": completed_at, "cache": cache_metadata, "frozen_inputs": frozen_manifest, "source_snapshot": source_records, "runtime_versions": runtime_versions, "verification": verification, "artifact_inventory": inventory, "interpretation_boundary": summary["interpretation_boundary"]}
    _write_json_exclusive(run_root / "MANIFEST.json", manifest)
    primary = summary["primary_event_attention_motion"]
    print(json.dumps({"status": "complete", "run_root": str(run_root), "manifest": str(run_root / "MANIFEST.json"), "hypothesis_verdict": primary["hypothesis_verdict"], "primary_high_minus_standard": primary["mean_difference"], "primary_ci": [primary["ci_low"], primary["ci_high"]]}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
