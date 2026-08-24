#!/usr/bin/env python3
"""Standalone VDA4 cross-attention decay comparison producer.

The completed producer compares immutable standard and high carried-cell-decay
checkpoints on shared CPU-generated trials. Attention activity is defined as
frame-to-frame total variation over the full query-to-key softmax map; total
attention mass is not an activity measure because each row is normalized.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import shlex
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
KEY_COUNT = 8
CUE_INDEX = 0
VALID_CHANGE_INDEX = 0
INVALID_CHANGE_INDEX = 3
EVENT_MAGNITUDE = 15.0
EVENT_DISPLAYED_VALIDITY = 1.0
EVENT_SEED = 4101
NOCHANGE_SEED = 1701
PSYCHOMETRIC_SEED = 2801
QUALIFYING_RESPONSE_FRAME = 5
SOURCE_DEPENDENCIES = (
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
    "feedback": "crossattn1",
    "cell": "xlstm",
    "d_mem": 128,
    "conv_frontend": True,
    "grid_rows": 2,
    "grid_cols": 2,
    "image_size": 50,
}


def resolved_model_kwargs(checkpoint: dict, *, role: str) -> dict:
    """Validate one frozen checkpoint and resolve its functional decay value."""
    if role not in {"standard", "high_decay"}:
        raise ValueError(f"role must be 'standard' or 'high_decay'; got {role!r}")
    if checkpoint.get("task") != "vda4":
        raise ValueError(f"task must be 'vda4'; got {checkpoint.get('task')!r}")
    kwargs = dict(checkpoint.get("model_kwargs") or {})
    for field, expected in MODEL_CONTRACT.items():
        if kwargs.get(field) != expected:
            raise ValueError(f"{field} must be {expected!r}; got {kwargs.get(field)!r}")
    resolved_decay = float(kwargs.get("memory_decay", 1.0))
    expected_decay = 1.0 if role == "standard" else 0.8
    if resolved_decay != expected_decay:
        raise ValueError(
            f"memory_decay must resolve to {expected_decay} for {role}; got {resolved_decay}"
        )
    kwargs["memory_decay"] = resolved_decay
    return kwargs


def checkpoint_iteration(record: dict[str, Any], *, expected: int) -> int:
    """Read and verify the frozen-input manifest's checkpoint iteration field."""
    if "checkpoint_iteration" not in record:
        raise ValueError("frozen checkpoint record is missing checkpoint_iteration")
    iteration = int(record["checkpoint_iteration"])
    if iteration != expected:
        raise ValueError(f"checkpoint iteration mismatch: got {iteration}, expected {expected}")
    return iteration


def first_press_from_logits(
    actor_logits: np.ndarray, *, qualifying_frame: int = 5
) -> tuple[np.ndarray, np.ndarray]:
    """Return first argmax change-action frame and the established qualification mask."""
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
    bootstrap_samples: int = 10_000,
) -> dict[str, float | int]:
    """Estimate a deterministic paired high-minus-standard mean and percentile CI."""
    high_values = np.asarray(high, dtype=np.float64)
    standard_values = np.asarray(standard, dtype=np.float64)
    if high_values.shape != standard_values.shape:
        raise ValueError(
            f"paired arrays must have the same shape; got {high_values.shape} and {standard_values.shape}"
        )
    differences = (high_values - standard_values).reshape(-1)
    if differences.size == 0:
        raise ValueError("paired arrays must be nonempty")
    if not np.isfinite(differences).all():
        raise ValueError("paired differences must be finite")
    if (
        isinstance(bootstrap_samples, bool)
        or int(bootstrap_samples) != bootstrap_samples
        or bootstrap_samples <= 0
    ):
        raise ValueError("bootstrap_samples must be a positive integer")
    rng = np.random.default_rng(seed)
    indices = rng.integers(
        0, differences.size, size=(int(bootstrap_samples), differences.size)
    )
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


def attention_metrics(raw_attention: np.ndarray) -> dict[str, np.ndarray]:
    """Return trial-level activity and allocation metrics for cross-attention.

    Parameters
    ----------
    raw_attention:
        Array shaped ``(trial, time, query, key)`` with ``key = 2 * query``.
        Keys are ordered as image locations followed by recurrent-memory locations.
    """
    raw = np.asarray(raw_attention, dtype=np.float64)
    if raw.ndim != 4:
        raise ValueError(f"raw attention must have shape (trial,time,query,key); got {raw.shape}")
    queries, keys = raw.shape[-2:]
    if queries <= 0 or keys != 2 * queries:
        raise ValueError(f"cross-attention requires K=2Q; got Q={queries}, K={keys}")
    if not np.isfinite(raw).all() or np.any(raw < 0.0):
        raise ValueError("attention must be finite and nonnegative")
    if not np.allclose(raw.sum(axis=-1), 1.0, rtol=1e-5, atol=1e-6):
        raise ValueError("attention rows must sum to one")

    eps = np.finfo(np.float64).tiny
    entropy = -(raw * np.log(np.clip(raw, eps, 1.0))).sum(axis=-1)
    selectivity = 1.0 - entropy.mean(axis=-1) / np.log(keys)
    temporal_motion = 0.5 * np.abs(np.diff(raw, axis=1)).sum(axis=-1).mean(axis=-1)
    image_mass = raw[..., :queries].sum(axis=-1).mean(axis=-1)
    memory_mass = raw[..., queries:].sum(axis=-1).mean(axis=-1)
    peak_key_mass = raw.max(axis=-1).mean(axis=-1)
    spatial_mass = (raw[..., :queries] + raw[..., queries:]).mean(axis=-2)
    return {
        "temporal_motion": temporal_motion,
        "selectivity": selectivity,
        "image_mass": image_mass,
        "memory_mass": memory_mass,
        "peak_key_mass": peak_key_mass,
        "spatial_mass": spatial_mass,
    }


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_path(path: str | Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def capture_executable_sources() -> dict[str, bytes]:
    paths = {"analysis/vda4_decay_comparison.py": Path(__file__).resolve()}
    paths.update({relative: PROJECT_ROOT / relative for relative in SOURCE_DEPENDENCIES})
    return {relative: path.read_bytes() for relative, path in paths.items()}


def assert_sources_unchanged(captured: dict[str, bytes]) -> None:
    for relative, expected in captured.items():
        path = Path(__file__).resolve() if relative == "analysis/vda4_decay_comparison.py" else PROJECT_ROOT / relative
        if path.read_bytes() != expected:
            raise RuntimeError(f"executable source changed during analysis: {path}")


def source_resolved_attention(raw_attention: np.ndarray) -> np.ndarray:
    """Split cross-attention into image and memory source arrays without collapsing queries."""
    raw = np.asarray(raw_attention, dtype=np.float64)
    if raw.shape[-2:] != (QUERY_COUNT, KEY_COUNT):
        raise ValueError(f"expected attention axes (Q,K)=(4,8); got {raw.shape[-2:]}")
    if not np.allclose(raw.sum(axis=-1), 1.0, rtol=1e-5, atol=1e-6):
        raise ValueError("attention rows must sum to one")
    return np.stack((raw[..., :QUERY_COUNT], raw[..., QUERY_COUNT:]), axis=-2)


def _runtime_versions(torch_module: Any) -> dict[str, str]:
    import matplotlib
    import scipy
    from PIL import __version__ as pillow_version

    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "scipy": scipy.__version__,
        "pillow": pillow_version,
        "torch": torch_module.__version__,
        "python_executable": str(Path(sys.executable).resolve()),
    }


def _load_frozen_inputs(run_root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest_path = run_root / "frozen_inputs.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = {str(record["role"]): record for record in manifest.get("checkpoints", [])}
    if set(records) != set(MODEL_ROLES):
        raise ValueError(f"frozen input roles must be {MODEL_ROLES}; got {sorted(records)}")
    for role, record in records.items():
        checkpoint = Path(str(record["snapshot_path"])).resolve()
        if run_root.resolve() not in checkpoint.parents:
            raise ValueError(f"frozen {role} checkpoint escapes run root: {checkpoint}")
        content = checkpoint.read_bytes()
        if len(content) != int(record["bytes"]) or sha256_bytes(content) != str(record["sha256"]):
            raise RuntimeError(f"frozen {role} checkpoint identity mismatch")
    return manifest, records


def _load_model(record: dict[str, Any], *, role: str, torch_module: Any):
    from model import RViTPaperModel

    checkpoint_path = Path(str(record["snapshot_path"])).resolve()
    checkpoint_bytes = checkpoint_path.read_bytes()
    if sha256_bytes(checkpoint_bytes) != str(record["sha256"]):
        raise RuntimeError(f"{role} checkpoint changed before model load")
    checkpoint = torch_module.load(io.BytesIO(checkpoint_bytes), map_location="cpu", weights_only=False)
    kwargs = resolved_model_kwargs(checkpoint, role=role)
    model = RViTPaperModel(**kwargs)
    state = checkpoint["model_state_dict"]
    if "front.out_norm.bias" in state and not isinstance(model.front.out_norm, torch_module.nn.LayerNorm):
        model.front.out_norm = torch_module.nn.LayerNorm(128)
    result = model.load_state_dict(state, strict=True)
    if result.missing_keys or result.unexpected_keys:
        raise RuntimeError(
            f"strict {role} load failed: missing={result.missing_keys}, unexpected={result.unexpected_keys}"
        )
    model.to("cpu").eval()
    return model, checkpoint, kwargs


def _run_model_batch(model: Any, videos: Any, torch_module: Any) -> tuple[np.ndarray, np.ndarray]:
    with torch_module.inference_mode():
        output = model.forward_rl_sequence(videos, return_attn=True)
    logits = output["actor_logits_seq"].detach().cpu().numpy().astype(np.float32)
    attention = output["attn_seq"].detach().cpu().numpy().astype(np.float32)
    if attention.shape[1:] != (TIMESTEPS, QUERY_COUNT, KEY_COUNT):
        raise RuntimeError(f"unexpected attention shape {attention.shape}")
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
    if temporary.exists():
        raise FileExistsError(f"temporary cache already exists: {temporary}")
    np.savez_compressed(temporary, **payload)
    with temporary.open("rb") as handle:
        os.fsync(handle.fileno())
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
    """Compute all two-model evidence from shared CPU trial tensors."""
    from vda_sweep import vda_core as core

    if any(value <= 0 for value in (attention_trials, nochange_trials, psychometric_trials)):
        raise ValueError("all trial budgets must be positive")
    if str(core.DEVICE) != "cpu":
        raise RuntimeError(f"analysis must run on CPU; vda_core.DEVICE={core.DEVICE!r}")
    models: list[Any] = []
    checkpoint_iterations = []
    resolved_decays = []
    checkpoint_hashes = []
    for role in MODEL_ROLES:
        model, checkpoint, kwargs = _load_model(records[role], role=role, torch_module=torch_module)
        models.append(model)
        checkpoint_iterations.append(int(checkpoint["iter"]))
        resolved_decays.append(float(kwargs["memory_decay"]))
        checkpoint_hashes.append(str(records[role]["sha256"]))

    event_logits = np.empty(
        (len(MODEL_ROLES), len(EVENT_CONDITIONS), attention_trials, TIMESTEPS, 2),
        dtype=np.float32,
    )
    event_raw = np.empty(
        (
            len(MODEL_ROLES),
            len(EVENT_CONDITIONS),
            attention_trials,
            TIMESTEPS,
            QUERY_COUNT,
            KEY_COUNT,
        ),
        dtype=np.float32,
    )
    event_first = np.empty(
        (len(MODEL_ROLES), len(EVENT_CONDITIONS), attention_trials), dtype=np.int64
    )
    event_qualifying = np.empty_like(event_first, dtype=bool)
    event_videos = []
    for condition_index, change_index in enumerate((VALID_CHANGE_INDEX, INVALID_CHANGE_INDEX)):
        videos = core.make_video_batch(
            "vda4",
            CUE_INDEX,
            EVENT_DISPLAYED_VALIDITY,
            "red",
            1,
            change_index,
            EVENT_MAGNITUDE,
            B=attention_trials,
            seed=EVENT_SEED,
        ).cpu()
        event_videos.append(videos)
        for model_index, model in enumerate(models):
            logits, raw = _run_model_batch(model, videos, torch_module)
            first, qualifying = first_press_from_logits(
                logits, qualifying_frame=QUALIFYING_RESPONSE_FRAME
            )
            event_logits[model_index, condition_index] = logits
            event_raw[model_index, condition_index] = raw
            event_first[model_index, condition_index] = first
            event_qualifying[model_index, condition_index] = qualifying
    if not torch_module.equal(event_videos[0][:, :5], event_videos[1][:, :5]):
        raise RuntimeError("paired valid/invalid event videos differ before the change frame")
    del event_videos

    nochange_raw = np.empty(
        (
            len(MODEL_ROLES),
            len(DISPLAYED_VALIDITIES),
            nochange_trials,
            TIMESTEPS,
            QUERY_COUNT,
            KEY_COUNT,
        ),
        dtype=np.float32,
    )
    for validity_index, displayed_validity in enumerate(DISPLAYED_VALIDITIES):
        videos = core.make_video_batch(
            "vda4",
            CUE_INDEX,
            float(displayed_validity),
            "red",
            0,
            -1,
            0.0,
            B=nochange_trials,
            seed=NOCHANGE_SEED,
        ).cpu()
        for model_index, model in enumerate(models):
            _, raw = _run_model_batch(model, videos, torch_module)
            nochange_raw[model_index, validity_index] = raw

    psych_shape = (
        len(MODEL_ROLES),
        len(DISPLAYED_VALIDITIES),
        len(CHANGE_MAGNITUDES),
        len(EVENT_CONDITIONS),
    )
    psych_count = np.zeros(psych_shape, dtype=np.int64)
    psych_histogram = np.zeros(psych_shape + (TIMESTEPS + 1,), dtype=np.int64)
    point_seeds = np.zeros((len(DISPLAYED_VALIDITIES), len(CHANGE_MAGNITUDES)), dtype=np.int64)
    for validity_index, displayed_validity in enumerate(DISPLAYED_VALIDITIES):
        for magnitude_index, magnitude in enumerate(CHANGE_MAGNITUDES):
            point_seed = PSYCHOMETRIC_SEED + magnitude_index * 101
            point_seeds[validity_index, magnitude_index] = point_seed
            for condition_index, change_index in enumerate(
                (VALID_CHANGE_INDEX, INVALID_CHANGE_INDEX)
            ):
                videos = core.make_video_batch(
                    "vda4",
                    CUE_INDEX,
                    float(displayed_validity),
                    "red",
                    1,
                    change_index,
                    float(magnitude),
                    B=psychometric_trials,
                    seed=int(point_seed),
                ).cpu()
                for model_index, model in enumerate(models):
                    logits, _ = _run_model_batch(model, videos, torch_module)
                    first, qualifying = first_press_from_logits(
                        logits, qualifying_frame=QUALIFYING_RESPONSE_FRAME
                    )
                    psych_count[
                        model_index, validity_index, magnitude_index, condition_index
                    ] = int(np.count_nonzero(qualifying))
                    psych_histogram[
                        model_index, validity_index, magnitude_index, condition_index
                    ] = _press_histogram(first)
    psych_rate = psych_count / float(psychometric_trials)

    event_sources = source_resolved_attention(event_raw).astype(np.float32)
    event_query_averaged = event_sources.mean(axis=-3).astype(np.float32)
    event_metrics: dict[str, np.ndarray] = {}
    for model_index in range(len(MODEL_ROLES)):
        for condition_index in range(len(EVENT_CONDITIONS)):
            metrics = attention_metrics(event_raw[model_index, condition_index])
            for name, values in metrics.items():
                event_metrics.setdefault(
                    f"event_{name}",
                    np.empty((len(MODEL_ROLES), len(EVENT_CONDITIONS)) + values.shape, dtype=np.float32),
                )[model_index, condition_index] = values
    nochange_metrics: dict[str, np.ndarray] = {}
    for model_index in range(len(MODEL_ROLES)):
        for validity_index in range(len(DISPLAYED_VALIDITIES)):
            metrics = attention_metrics(nochange_raw[model_index, validity_index])
            for name, values in metrics.items():
                nochange_metrics.setdefault(
                    f"nochange_{name}",
                    np.empty((len(MODEL_ROLES), len(DISPLAYED_VALIDITIES)) + values.shape, dtype=np.float32),
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
        device=np.array("cpu"),
        event_actor_logits=event_logits,
        event_raw_attention=event_raw,
        event_source_attention=event_sources,
        event_query_averaged_attention=event_query_averaged,
        event_first_press=event_first,
        event_qualifying_response=event_qualifying,
        nochange_raw_attention=nochange_raw,
        psychometric_response_count=psych_count,
        psychometric_response_rate=psych_rate,
        psychometric_press_histogram=psych_histogram,
        seed_policy=np.array(
            "common random numbers matched across models, displayed cue proportions, and valid/forced-invalid locations at each magnitude"
        ),
        **event_metrics,
        **nochange_metrics,
    )
    for role, record in records.items():
        if sha256_path(record["snapshot_path"]) != str(record["sha256"]):
            raise RuntimeError(f"frozen {role} checkpoint changed during computation")
    return cache_path


def _scalar(payload: Any, field: str) -> Any:
    value = np.asarray(payload[field])
    if value.ndim != 0:
        raise ValueError(f"cache field {field!r} must be scalar")
    return value.item()


def validate_comparison_cache(
    cache_path: str | Path,
    *,
    expected_attention_trials: int | None = None,
    expected_nochange_trials: int | None = None,
    expected_psychometric_trials: int | None = None,
) -> dict[str, Any]:
    """Recompute all cache reductions and fail closed on schema or lineage drift."""
    cache_path = Path(cache_path)
    content = cache_path.read_bytes()
    cache_sha256 = sha256_bytes(content)
    metric_names = (
        "temporal_motion",
        "selectivity",
        "image_mass",
        "memory_mass",
        "peak_key_mass",
        "spatial_mass",
    )
    required = {
        "model_roles",
        "event_conditions",
        "displayed_validities",
        "change_magnitudes",
        "checkpoint_iterations",
        "checkpoint_sha256",
        "resolved_memory_decay",
        "attention_trials",
        "nochange_trials",
        "psychometric_trials",
        "event_seed",
        "nochange_seed",
        "psychometric_seed",
        "point_seeds",
        "cue_index",
        "valid_change_index",
        "invalid_change_index",
        "event_magnitude",
        "event_displayed_validity",
        "qualifying_response_frame",
        "device",
        "event_actor_logits",
        "event_raw_attention",
        "event_source_attention",
        "event_query_averaged_attention",
        "event_first_press",
        "event_qualifying_response",
        "nochange_raw_attention",
        "psychometric_response_count",
        "psychometric_response_rate",
        "psychometric_press_histogram",
        "seed_policy",
    } | {f"{prefix}_{name}" for prefix in ("event", "nochange") for name in metric_names}
    with np.load(io.BytesIO(content), allow_pickle=False) as payload:
        missing = sorted(required - set(payload.files))
        if missing:
            raise ValueError(f"comparison cache missing fields: {missing}")
        np.testing.assert_array_equal(payload["model_roles"], np.asarray(MODEL_ROLES))
        np.testing.assert_array_equal(payload["event_conditions"], np.asarray(EVENT_CONDITIONS))
        np.testing.assert_allclose(payload["displayed_validities"], DISPLAYED_VALIDITIES)
        np.testing.assert_allclose(payload["change_magnitudes"], CHANGE_MAGNITUDES)
        np.testing.assert_allclose(payload["resolved_memory_decay"], [1.0, 0.8])
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
        scalar_contract = {
            "event_seed": EVENT_SEED,
            "nochange_seed": NOCHANGE_SEED,
            "psychometric_seed": PSYCHOMETRIC_SEED,
            "cue_index": CUE_INDEX,
            "valid_change_index": VALID_CHANGE_INDEX,
            "invalid_change_index": INVALID_CHANGE_INDEX,
            "event_magnitude": EVENT_MAGNITUDE,
            "event_displayed_validity": EVENT_DISPLAYED_VALIDITY,
            "qualifying_response_frame": QUALIFYING_RESPONSE_FRAME,
            "device": "cpu",
        }
        for field, expected in scalar_contract.items():
            actual = _scalar(payload, field)
            if actual != expected:
                raise ValueError(f"cache {field}={actual!r}, expected {expected!r}")
        expected_seeds = np.tile(
            PSYCHOMETRIC_SEED + np.arange(len(CHANGE_MAGNITUDES)) * 101,
            (len(DISPLAYED_VALIDITIES), 1),
        )
        np.testing.assert_array_equal(payload["point_seeds"], expected_seeds)

        raw_event = np.asarray(payload["event_raw_attention"], dtype=np.float64)
        expected_event_shape = (2, 2, attention_trials, TIMESTEPS, QUERY_COUNT, KEY_COUNT)
        if raw_event.shape != expected_event_shape:
            raise ValueError(f"event attention shape {raw_event.shape}, expected {expected_event_shape}")
        sources = source_resolved_attention(raw_event)
        np.testing.assert_allclose(payload["event_source_attention"], sources, rtol=1e-5, atol=1e-6)
        np.testing.assert_allclose(
            payload["event_query_averaged_attention"], sources.mean(axis=-3), rtol=1e-5, atol=1e-6
        )
        logits = np.asarray(payload["event_actor_logits"], dtype=np.float64)
        if logits.shape != (2, 2, attention_trials, TIMESTEPS, 2):
            raise ValueError(f"event actor-logit shape is invalid: {logits.shape}")
        stored_first = np.asarray(payload["event_first_press"], dtype=np.int64)
        stored_qualifying = np.asarray(payload["event_qualifying_response"], dtype=bool)
        for model_index in range(2):
            for condition_index in range(2):
                first, qualifying = first_press_from_logits(
                    logits[model_index, condition_index],
                    qualifying_frame=QUALIFYING_RESPONSE_FRAME,
                )
                np.testing.assert_array_equal(stored_first[model_index, condition_index], first)
                np.testing.assert_array_equal(
                    stored_qualifying[model_index, condition_index], qualifying
                )
                metrics = attention_metrics(raw_event[model_index, condition_index])
                for name, values in metrics.items():
                    np.testing.assert_allclose(
                        payload[f"event_{name}"][model_index, condition_index],
                        values,
                        rtol=1e-5,
                        atol=1e-6,
                    )

        raw_nochange = np.asarray(payload["nochange_raw_attention"], dtype=np.float64)
        expected_nochange_shape = (
            2,
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
        for model_index in range(2):
            for validity_index in range(len(DISPLAYED_VALIDITIES)):
                metrics = attention_metrics(raw_nochange[model_index, validity_index])
                for name, values in metrics.items():
                    np.testing.assert_allclose(
                        payload[f"nochange_{name}"][model_index, validity_index],
                        values,
                        rtol=1e-5,
                        atol=1e-6,
                    )

        psych_count = np.asarray(payload["psychometric_response_count"], dtype=np.int64)
        psych_rate = np.asarray(payload["psychometric_response_rate"], dtype=np.float64)
        psych_histogram = np.asarray(payload["psychometric_press_histogram"], dtype=np.int64)
        psych_shape = (2, len(DISPLAYED_VALIDITIES), len(CHANGE_MAGNITUDES), 2)
        if psych_count.shape != psych_shape or psych_rate.shape != psych_shape:
            raise ValueError("psychometric count/rate shapes do not satisfy the comparison contract")
        if psych_histogram.shape != psych_shape + (TIMESTEPS + 1,):
            raise ValueError("psychometric press-histogram shape does not satisfy the comparison contract")
        np.testing.assert_array_equal(psych_histogram.sum(axis=-1), psychometric_trials)
        np.testing.assert_array_equal(
            psych_count,
            psych_histogram[..., QUALIFYING_RESPONSE_FRAME + 1 :].sum(axis=-1),
        )
        np.testing.assert_allclose(psych_rate, psych_count / psychometric_trials, rtol=0.0, atol=1e-12)
        checkpoint_hashes = [str(value) for value in payload["checkpoint_sha256"].tolist()]
        if len(checkpoint_hashes) != 2 or any(len(value) != 64 for value in checkpoint_hashes):
            raise ValueError("cache checkpoint hashes are malformed")
        iterations = [int(value) for value in payload["checkpoint_iterations"].tolist()]

    return {
        "cache_path": str(cache_path.resolve()),
        "cache_sha256": cache_sha256,
        "attention_trials": attention_trials,
        "nochange_trials": nochange_trials,
        "psychometric_trials": psychometric_trials,
        "checkpoint_iterations": iterations,
        "checkpoint_sha256": checkpoint_hashes,
        "device": "cpu",
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
    for suffix, kwargs in ((".pdf", {}), (".svg", {}), (".png", {"dpi": 240})):
        path = base.with_suffix(suffix)
        figure.savefig(path, bbox_inches="tight", **kwargs)
        outputs.append(path)
    return outputs


def _draw_location_map(
    axis: Any,
    values: np.ndarray,
    *,
    vmax: float,
    cue: bool,
    change_index: int | None,
):
    import matplotlib.pyplot as plt

    image = axis.imshow(
        np.asarray(values).reshape(2, 2),
        cmap="cividis",
        vmin=0.0,
        vmax=vmax,
        interpolation="nearest",
    )
    axis.set_xticks([])
    axis.set_yticks([])
    if cue:
        axis.plot(-0.32, -0.32, marker="o", markersize=4, color="#D55E00", clip_on=False)
    if change_index is not None:
        row, column = divmod(change_index, 2)
        axis.add_patch(
            plt.Rectangle(
                (column - 0.48, row - 0.48),
                0.96,
                0.96,
                fill=False,
                edgecolor="#CC79A7",
                linewidth=1.5,
            )
        )
    return image


def _build_event_map_figure(payload: Any, output_dir: Path) -> list[Path]:
    import matplotlib.pyplot as plt

    maps = np.asarray(payload["event_query_averaged_attention"], dtype=np.float64).mean(axis=2)
    vmax = max(float(maps.max()), 1e-8)
    row_specs = [
        (model, condition, source)
        for model in range(2)
        for condition in range(2)
        for source in range(2)
    ]
    figure, axes = plt.subplots(len(row_specs), TIMESTEPS, figsize=(14.8, 14.0))
    source_labels = ("image keys", "memory keys")
    model_labels = ("standard λ=1.0", "high decay λ=0.8")
    condition_labels = ("valid S1 change", "forced-invalid S4 change")
    time_labels = ("t0 blank", "t1 cue", "t2 delay", "t3 array", "t4 maintain", "t5 change", "t6 response")
    image = None
    for row, (model, condition, source) in enumerate(row_specs):
        for timestep in range(TIMESTEPS):
            change = (VALID_CHANGE_INDEX if condition == 0 else INVALID_CHANGE_INDEX) if timestep == 5 else None
            image = _draw_location_map(
                axes[row, timestep],
                maps[model, condition, timestep, source],
                vmax=vmax,
                cue=timestep == 1,
                change_index=change,
            )
            if row == 0:
                axes[row, timestep].set_title(time_labels[timestep], fontsize=9)
            if timestep == 0:
                axes[row, timestep].set_ylabel(
                    f"{model_labels[model]}\n{condition_labels[condition]}\n{source_labels[source]}",
                    rotation=0,
                    ha="right",
                    va="center",
                    fontsize=8.5,
                )
    figure.subplots_adjust(left=0.20, right=0.92, top=0.92, bottom=0.06, wspace=0.06, hspace=0.16)
    figure.suptitle(
        "VDA4 event-locked cross-attention · query-averaged source maps · 100% displayed cue · Δ=15°",
        fontweight="bold",
    )
    figure.text(
        0.5,
        0.02,
        "Orange dot marks the cue at S1; magenta border marks the forced change. One shared scale across both models, conditions, sources, and frames.",
        ha="center",
        fontsize=9,
    )
    figure.colorbar(image, ax=axes.ravel().tolist(), fraction=0.012, pad=0.015, label="attention mass")
    outputs = _save_figure(figure, output_dir / "attention_event_query_averaged")
    plt.close(figure)
    return outputs


def _build_query_level_figures(payload: Any, output_dir: Path) -> list[Path]:
    import matplotlib.pyplot as plt

    source_mean = np.asarray(payload["event_source_attention"], dtype=np.float64).mean(axis=2)
    vmax = max(float(source_mean.max()), 1e-8)
    outputs: list[Path] = []
    for condition, condition_name in enumerate(EVENT_CONDITIONS):
        for source, source_name in enumerate(("image_keys", "memory_keys")):
            figure, axes = plt.subplots(8, TIMESTEPS, figsize=(14.8, 13.0))
            image = None
            for model in range(2):
                for query in range(QUERY_COUNT):
                    row = model * QUERY_COUNT + query
                    for timestep in range(TIMESTEPS):
                        change = (
                            VALID_CHANGE_INDEX if condition == 0 else INVALID_CHANGE_INDEX
                        ) if timestep == 5 else None
                        image = _draw_location_map(
                            axes[row, timestep],
                            source_mean[model, condition, timestep, query, source],
                            vmax=vmax,
                            cue=timestep == 1,
                            change_index=change,
                        )
                        if row == 0:
                            axes[row, timestep].set_title(f"t{timestep}", fontsize=9)
                        if timestep == 0:
                            model_label = "standard λ=1.0" if model == 0 else "high decay λ=0.8"
                            axes[row, timestep].set_ylabel(
                                f"{model_label}\nquery S{query + 1}",
                                rotation=0,
                                ha="right",
                                va="center",
                                fontsize=8.5,
                            )
            figure.subplots_adjust(left=0.18, right=0.92, top=0.92, bottom=0.06, wspace=0.06, hspace=0.13)
            figure.suptitle(
                f"VDA4 query-level {source_name.replace('_', ' ')} · {condition_name.replace('_', ' ')} · common scale",
                fontweight="bold",
            )
            figure.colorbar(image, ax=axes.ravel().tolist(), fraction=0.012, pad=0.015, label="attention mass")
            outputs.extend(
                _save_figure(figure, output_dir / f"attention_query_level_{condition_name}_{source_name}")
            )
            plt.close(figure)
    return outputs


def _build_nochange_figures(payload: Any, output_dir: Path) -> list[Path]:
    import matplotlib.pyplot as plt

    raw = np.asarray(payload["nochange_raw_attention"], dtype=np.float64)
    source_maps = source_resolved_attention(raw).mean(axis=2).mean(axis=-3)
    vmax = max(float(source_maps.max()), 1e-8)
    outputs: list[Path] = []
    for source, source_name in enumerate(("image_keys", "memory_keys")):
        figure, axes = plt.subplots(8, TIMESTEPS, figsize=(14.8, 13.0))
        image = None
        for model in range(2):
            for validity_index, validity in enumerate(DISPLAYED_VALIDITIES):
                row = model * len(DISPLAYED_VALIDITIES) + validity_index
                for timestep in range(TIMESTEPS):
                    image = _draw_location_map(
                        axes[row, timestep],
                        source_maps[model, validity_index, timestep, source],
                        vmax=vmax,
                        cue=timestep == 1,
                        change_index=None,
                    )
                    if row == 0:
                        axes[row, timestep].set_title(f"t{timestep}", fontsize=9)
                    if timestep == 0:
                        model_label = "standard λ=1.0" if model == 0 else "high decay λ=0.8"
                        axes[row, timestep].set_ylabel(
                            f"{model_label}\n{int(validity * 100)}% cue",
                            rotation=0,
                            ha="right",
                            va="center",
                            fontsize=8.5,
                        )
        figure.subplots_adjust(left=0.18, right=0.92, top=0.92, bottom=0.06, wspace=0.06, hspace=0.13)
        figure.suptitle(
            f"VDA4 no-change cue-proportion sweep · {source_name.replace('_', ' ')} · query-averaged",
            fontweight="bold",
        )
        figure.colorbar(image, ax=axes.ravel().tolist(), fraction=0.012, pad=0.015, label="attention mass")
        outputs.extend(_save_figure(figure, output_dir / f"attention_nochange_{source_name}"))
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
    image_mass = np.asarray(payload["event_image_mass"], dtype=np.float64)
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
            _plot_trial_series(
                axes[0, 0],
                np.arange(1, TIMESTEPS),
                motion[model, condition],
                label=label,
                color=colors[model],
                linestyle=line_styles[condition],
            )
            _plot_trial_series(
                axes[0, 1],
                np.arange(TIMESTEPS),
                selectivity[model, condition],
                label=label,
                color=colors[model],
                linestyle=line_styles[condition],
            )
            _plot_trial_series(
                axes[0, 2],
                np.arange(TIMESTEPS),
                image_mass[model, condition],
                label=label,
                color=colors[model],
                linestyle=line_styles[condition],
            )
            location = VALID_CHANGE_INDEX if condition == 0 else INVALID_CHANGE_INDEX
            _plot_trial_series(
                axes[1, 0],
                np.arange(TIMESTEPS),
                spatial[model, condition, :, :, CUE_INDEX],
                label=label,
                color=colors[model],
                linestyle=line_styles[condition],
            )
            _plot_trial_series(
                axes[1, 1],
                np.arange(TIMESTEPS),
                spatial[model, condition, :, :, location],
                label=label,
                color=colors[model],
                linestyle=line_styles[condition],
            )
    for model in range(2):
        for condition in range(2):
            location = VALID_CHANGE_INDEX if condition == 0 else INVALID_CHANGE_INDEX
            for responded, marker, alpha, suffix in ((True, "o", 1.0, "response"), (False, "s", 0.65, "no response")):
                mask = qualifying[model, condition] == responded
                if not np.any(mask):
                    continue
                values = spatial[model, condition, mask, :, location]
                axes[1, 2].plot(
                    np.arange(TIMESTEPS),
                    values.mean(axis=0),
                    color=colors[model],
                    linestyle=line_styles[condition],
                    marker=marker,
                    markersize=3,
                    alpha=alpha,
                    label=f"{model_labels[model]} · {condition_labels[condition]} · {suffix} (n={mask.sum()})",
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
    axes[0, 0].set_ylabel("total variation")
    axes[0, 1].set_ylabel("selectivity")
    axes[0, 2].set_ylabel("attention mass")
    axes[1, 0].set_ylabel("attention mass")
    axes[1, 1].set_ylabel("attention mass")
    axes[1, 2].set_ylabel("attention mass")
    axes[0, 0].legend(fontsize=7, frameon=False)
    axes[1, 2].legend(fontsize=6.2, frameon=False, ncol=1)
    primary = summary["primary_event_attention_motion"]
    figure.suptitle(
        "VDA4 cross-attention dynamics · high decay versus standard\n"
        f"Primary high−standard motion difference = {primary['mean_difference']:+.4f} "
        f"(paired 95% bootstrap CI {primary['ci_low']:+.4f}, {primary['ci_high']:+.4f})",
        fontweight="bold",
    )
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
                label = (
                    ("standard λ=1.0" if model == 0 else "high decay λ=0.8")
                    + (" · valid" if condition == 0 else " · forced invalid")
                )
                axis.fill_between(
                    CHANGE_MAGNITUDES,
                    lower,
                    upper,
                    color=model_colors[model],
                    alpha=0.08,
                    linewidth=0,
                )
                axis.plot(
                    CHANGE_MAGNITUDES,
                    rates[model, validity_index, :, condition],
                    color=model_colors[model],
                    linestyle=condition_styles[condition],
                    marker=condition_markers[condition],
                    markersize=3.5,
                    linewidth=1.8,
                    label=label,
                )
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
        images.append(
            axis.imshow(
                differences[:, :, condition],
                aspect="auto",
                origin="lower",
                cmap="coolwarm",
                vmin=-vmax,
                vmax=vmax,
                interpolation="nearest",
            )
        )
        axis.set_yticks(range(len(DISPLAYED_VALIDITIES)), [f"{int(v * 100)}%" for v in DISPLAYED_VALIDITIES])
        axis.set_xticks(range(len(CHANGE_MAGNITUDES)), [str(int(v)) for v in CHANGE_MAGNITUDES], rotation=45)
        axis.set_xlabel("orientation change (degrees)")
        axis.set_ylabel("displayed cue proportion")
        axis.set_title(
            f"{'E' if condition == 0 else 'F'}  High−standard response rate · {'valid' if condition == 0 else 'forced invalid'}",
            loc="left",
            fontweight="bold",
        )
    figure.colorbar(images[-1], ax=[axes[1, 1], axes[1, 2]], fraction=0.025, pad=0.02, label="response-rate difference")
    figure.suptitle(
        f"VDA4 paired psychometrics · n={trials} shared trials/point · first press at frame ≥5 qualifies\n"
        "Bands are Wilson 95% evaluation-trial intervals; invalid at 100% displayed cue is a forced intervention.",
        fontweight="bold",
    )
    outputs = _save_figure(figure, output_dir / "psychometric_valid_invalid_comparison")
    plt.close(figure)
    return outputs


def _paired_summary(
    high: np.ndarray,
    standard: np.ndarray,
    *,
    seed: int,
) -> dict[str, Any]:
    result = paired_mean_difference(high, standard, seed=seed, bootstrap_samples=10_000)
    result["standard_mean"] = float(np.asarray(standard, dtype=np.float64).mean())
    result["high_decay_mean"] = float(np.asarray(high, dtype=np.float64).mean())
    return result


def build_numeric_summary(payload: Any) -> tuple[dict[str, Any], dict[str, tuple[np.ndarray, np.ndarray]]]:
    motion = np.asarray(payload["event_temporal_motion"], dtype=np.float64)
    selectivity = np.asarray(payload["event_selectivity"], dtype=np.float64)
    peak = np.asarray(payload["event_peak_key_mass"], dtype=np.float64)
    image_mass = np.asarray(payload["event_image_mass"], dtype=np.float64)
    spatial = np.asarray(payload["event_spatial_mass"], dtype=np.float64)
    nochange_motion = np.asarray(payload["nochange_temporal_motion"], dtype=np.float64)
    nochange_spatial = np.asarray(payload["nochange_spatial_mass"], dtype=np.float64)
    qualifying = np.asarray(payload["event_qualifying_response"], dtype=np.float64)

    metric_pairs: dict[str, tuple[np.ndarray, np.ndarray]] = {
        "primary_event_attention_motion": (
            motion[1].mean(axis=(0, 2)),
            motion[0].mean(axis=(0, 2)),
        ),
        "event_selectivity": (
            selectivity[1].mean(axis=(0, 2)),
            selectivity[0].mean(axis=(0, 2)),
        ),
        "event_peak_key_mass": (
            peak[1].mean(axis=(0, 2)),
            peak[0].mean(axis=(0, 2)),
        ),
        "event_image_key_mass": (
            image_mass[1].mean(axis=(0, 2)),
            image_mass[0].mean(axis=(0, 2)),
        ),
        "nochange_attention_motion": (
            nochange_motion[1].mean(axis=(0, 2)),
            nochange_motion[0].mean(axis=(0, 2)),
        ),
        "cue_orienting_t1_minus_t0": (
            (nochange_spatial[1, :, :, 1, CUE_INDEX] - nochange_spatial[1, :, :, 0, CUE_INDEX]).mean(axis=0),
            (nochange_spatial[0, :, :, 1, CUE_INDEX] - nochange_spatial[0, :, :, 0, CUE_INDEX]).mean(axis=0),
        ),
    }
    for condition, condition_name in enumerate(EVENT_CONDITIONS):
        location = VALID_CHANGE_INDEX if condition == 0 else INVALID_CHANGE_INDEX
        metric_pairs[f"{condition_name}_attention_motion"] = (
            motion[1, condition].mean(axis=1),
            motion[0, condition].mean(axis=1),
        )
        metric_pairs[f"{condition_name}_change_reorientation_t5_minus_t4"] = (
            spatial[1, condition, :, 5, location] - spatial[1, condition, :, 4, location],
            spatial[0, condition, :, 5, location] - spatial[0, condition, :, 4, location],
        )
        metric_pairs[f"{condition_name}_qualifying_response"] = (
            qualifying[1, condition],
            qualifying[0, condition],
        )

    estimates = {
        name: _paired_summary(high, standard, seed=7200 + index * 37)
        for index, (name, (high, standard)) in enumerate(metric_pairs.items())
    }
    primary = estimates["primary_event_attention_motion"]
    if primary["ci_low"] > 0.0:
        verdict = "supported"
    elif primary["ci_high"] < 0.0:
        verdict = "opposite"
    else:
        verdict = "inconclusive"
    estimates["primary_event_attention_motion"]["hypothesis_verdict"] = verdict

    counts = np.asarray(payload["psychometric_response_count"], dtype=np.int64)
    rates = np.asarray(payload["psychometric_response_rate"], dtype=np.float64)
    validity_index = int(np.where(np.isclose(DISPLAYED_VALIDITIES, 1.0))[0][0])
    magnitude_index = int(np.where(np.isclose(CHANGE_MAGNITUDES, EVENT_MAGNITUDE))[0][0])
    summary = {
        "hypothesis_definition": (
            "High decay is more active if its paired mean frame-to-frame total variation over the full 4×8 attention map is larger. "
            "Total mass is not used because every query row is softmax-normalized to one."
        ),
        "primary_event_attention_motion": estimates["primary_event_attention_motion"],
        "secondary_estimates": {
            name: value for name, value in estimates.items() if name != "primary_event_attention_motion"
        },
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
        "interpretation_boundary": (
            "This is a frozen-checkpoint comparison: standard iteration 20000 versus high-decay iteration 14649. "
            "The estimates do not isolate memory decay from training maturity and do not quantify training-seed uncertainty."
        ),
    }
    return summary, metric_pairs


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing to overwrite table: {path}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_tables(
    payload: Any,
    summary: dict[str, Any],
    metric_pairs: dict[str, tuple[np.ndarray, np.ndarray]],
    output_dir: Path,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    estimates = {"primary_event_attention_motion": summary["primary_event_attention_motion"]}
    estimates.update(summary["secondary_estimates"])
    metric_rows = []
    for metric, estimate in estimates.items():
        metric_rows.append(
            {
                "metric": metric,
                "standard_mean": f"{estimate['standard_mean']:.10g}",
                "high_decay_mean": f"{estimate['high_decay_mean']:.10g}",
                "high_minus_standard": f"{estimate['mean_difference']:.10g}",
                "paired_ci_low": f"{estimate['ci_low']:.10g}",
                "paired_ci_high": f"{estimate['ci_high']:.10g}",
                "paired_n": int(estimate["n"]),
                "bootstrap_samples": int(estimate["bootstrap_samples"]),
                "bootstrap_seed": int(estimate["seed"]),
            }
        )
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
                    low, high = _wilson_interval(
                        counts[model, validity_index, magnitude_index, condition], trials
                    )
                    psych_rows.append(
                        {
                            "model": MODEL_ROLES[model],
                            "memory_decay": 1.0 if model == 0 else 0.8,
                            "displayed_validity": float(validity),
                            "orientation_change_degrees": float(magnitude),
                            "condition": EVENT_CONDITIONS[condition],
                            "response_count": int(counts[model, validity_index, magnitude_index, condition]),
                            "trials": trials,
                            "response_rate": f"{rates[model, validity_index, magnitude_index, condition]:.10g}",
                            "wilson_ci_low": f"{float(low):.10g}",
                            "wilson_ci_high": f"{float(high):.10g}",
                        }
                    )
    psych_path = output_dir / "psychometric_response_rates.csv"
    _write_csv(psych_path, list(psych_rows[0]), psych_rows)

    time_rows = []
    for prefix in ("event_temporal_motion", "event_selectivity", "event_image_mass", "event_memory_mass", "event_peak_key_mass"):
        values = np.asarray(payload[prefix], dtype=np.float64)
        for model in range(2):
            for condition in range(2):
                for timestep in range(values.shape[-1]):
                    sample = values[model, condition, :, timestep]
                    time_rows.append(
                        {
                            "metric": prefix.removeprefix("event_"),
                            "model": MODEL_ROLES[model],
                            "condition": EVENT_CONDITIONS[condition],
                            "logical_index": timestep + (1 if prefix == "event_temporal_motion" else 0),
                            "mean": f"{sample.mean():.10g}",
                            "standard_error": f"{sample.std(ddof=1) / np.sqrt(sample.size):.10g}",
                            "trials": sample.size,
                        }
                    )
    time_path = output_dir / "event_attention_timecourses.csv"
    _write_csv(time_path, list(time_rows[0]), time_rows)
    return [metric_path, psych_path, time_path]


def write_report(
    run_root: Path,
    summary: dict[str, Any],
    records: dict[str, dict[str, Any]],
) -> Path:
    primary = summary["primary_event_attention_motion"]
    verdict_text = {
        "supported": "supported for this frozen checkpoint pair",
        "opposite": "contradicted for this frozen checkpoint pair",
        "inconclusive": "not resolved for this frozen checkpoint pair",
    }[primary["hypothesis_verdict"]]
    secondary = summary["secondary_estimates"]
    anchor = summary["psychometric_anchor_100pct_15deg"]
    budgets = summary["event_condition"]
    standard_iteration = checkpoint_iteration(records["standard"], expected=20_000)
    high_decay_iteration = checkpoint_iteration(records["high_decay"], expected=14_649)
    report = f"""# Standalone VDA4 cross-attention decay comparison

## Result

The hypothesis is **{verdict_text}** under the prespecified activity metric. Mean frame-to-frame total variation was {primary['standard_mean']:.4f} for the standard model and {primary['high_decay_mean']:.4f} for the high-decay model. The paired high-minus-standard difference was {primary['mean_difference']:+.4f} (95% bootstrap CI {primary['ci_low']:+.4f} to {primary['ci_high']:+.4f}; n={primary['n']} matched event trials).

“More active” is defined as greater frame-to-frame total variation over the complete 4-query × 8-key attention distribution. It is not defined as total attention mass because each query row is softmax-normalized to one. Selectivity, peak-key mass, image-versus-memory allocation, cue orienting, and change reorientation are reported as secondary descriptors.

## Important boundary

This is a **frozen-checkpoint comparison, not a decay-only causal estimate**. The standard model is complete at iteration 20,000; the high-decay snapshot was frozen at iteration 14,649 while its MPS trainer continued. The models differ in memory decay and training maturity. There is one training seed per model, so confidence intervals describe paired evaluation-trial uncertainty only.

The 100%-cue invalid condition is a deliberate forced intervention (cue S1, change S4), not a trial that the 100%-valid environment would naturally sample.

## Checkpoints

| role | iteration | resolved decay | frozen SHA-256 |
|---|---:|---:|---|
| standard crossattn1 | {standard_iteration} | 1.00 (legacy absent field resolves to default) | `{records['standard']['sha256']}` |
| high-decay crossattn1 | {high_decay_iteration} | 0.80 | `{records['high_decay']['sha256']}` |

Both checkpoints validate as VDA4, xLSTM, `crossattn1`, `d_mem=128`, convolutional frontend, and 2×2/four-patch geometry. The standard final checkpoint has model tensors identical to its iteration-19,999 rolling checkpoint used by the prior VDA4 report.

## Event-locked findings (100% displayed cue, Δ=15°)

| measure | high minus standard | paired 95% CI |
|---|---:|---:|
| attention motion, valid | {secondary['valid_attention_motion']['mean_difference']:+.4f} | [{secondary['valid_attention_motion']['ci_low']:+.4f}, {secondary['valid_attention_motion']['ci_high']:+.4f}] |
| attention motion, forced invalid | {secondary['forced_invalid_attention_motion']['mean_difference']:+.4f} | [{secondary['forced_invalid_attention_motion']['ci_low']:+.4f}, {secondary['forced_invalid_attention_motion']['ci_high']:+.4f}] |
| selectivity | {secondary['event_selectivity']['mean_difference']:+.4f} | [{secondary['event_selectivity']['ci_low']:+.4f}, {secondary['event_selectivity']['ci_high']:+.4f}] |
| peak-key mass | {secondary['event_peak_key_mass']['mean_difference']:+.4f} | [{secondary['event_peak_key_mass']['ci_low']:+.4f}, {secondary['event_peak_key_mass']['ci_high']:+.4f}] |
| image-key mass | {secondary['event_image_key_mass']['mean_difference']:+.4f} | [{secondary['event_image_key_mass']['ci_low']:+.4f}, {secondary['event_image_key_mass']['ci_high']:+.4f}] |
| valid change reorientation, t5−t4 | {secondary['valid_change_reorientation_t5_minus_t4']['mean_difference']:+.4f} | [{secondary['valid_change_reorientation_t5_minus_t4']['ci_low']:+.4f}, {secondary['valid_change_reorientation_t5_minus_t4']['ci_high']:+.4f}] |
| invalid change reorientation, t5−t4 | {secondary['forced_invalid_change_reorientation_t5_minus_t4']['mean_difference']:+.4f} | [{secondary['forced_invalid_change_reorientation_t5_minus_t4']['ci_low']:+.4f}, {secondary['forced_invalid_change_reorientation_t5_minus_t4']['ci_high']:+.4f}] |

At the matched psychometric anchor (100% displayed cue, Δ=15°, {budgets['psychometric_trials']} trials/point), standard response rates were {anchor['standard']['valid']['response_rate']:.3f} valid and {anchor['standard']['forced_invalid']['response_rate']:.3f} forced invalid; high-decay rates were {anchor['high_decay']['valid']['response_rate']:.3f} valid and {anchor['high_decay']['forced_invalid']['response_rate']:.3f} forced invalid.

## Design

- Event attention: {budgets['attention_trials']} matched valid and forced-invalid trials, identical latent videos through t4, change at t5.
- No-change attention: {budgets['nochange_trials']} trials at 25%, 50%, 75%, and 100% displayed cue proportions.
- Psychometrics: {budgets['psychometric_trials']} shared trials at each of 4 displayed cue proportions × 10 magnitudes × 2 change locations.
- Response: first argmax change action; a first press at frame 5 or 6 qualifies.
- Inference: deterministic paired bootstrap over evaluation trials (10,000 resamples). No training-seed inference is claimed.
- Execution: CPU only; the comparison did not use MPS.

## Figures

- `figures/attention_event_query_averaged.pdf`: direct standard/high-decay, valid/invalid, image/memory map comparison.
- `figures/attention_query_level_*.pdf`: query-preserving source maps; no query-axis collapse.
- `figures/attention_nochange_*.pdf`: cue-proportion attentional patterns without change events.
- `figures/attention_metrics_and_response_strata.pdf`: activity, selectivity, source allocation, cue/change location, and response-stratified traces.
- `figures/psychometric_valid_invalid_comparison.pdf`: valid/forced-invalid response curves and high-minus-standard heatmaps.

PNG and SVG versions accompany every PDF. Exact rates and estimates are in `tables/`; raw evidence is in `data/comparison_evidence.npz`; executable source snapshots and runtime metadata are in `provenance/`.
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
    if not (len(pdfs) == len(pngs) == len(svgs) == 9):
        raise RuntimeError(
            f"expected 9 PDF/PNG/SVG figure triplets; got {len(pdfs)}/{len(pngs)}/{len(svgs)}"
        )
    pdf_records = []
    with tempfile.TemporaryDirectory(prefix="vda4-pdf-verify-") as temporary_directory:
        temporary_root = Path(temporary_directory)
        for index, path in enumerate(pdfs):
            info = subprocess.run(
                ["pdfinfo", str(path)],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            page_lines = [line for line in info.splitlines() if line.startswith("Pages:")]
            if len(page_lines) != 1:
                raise RuntimeError(f"could not determine PDF page count: {path}")
            page_count = int(page_lines[0].split(":", 1)[1].strip())
            if page_count != 1:
                raise RuntimeError(f"figure must be one page: {path}")
            raster_base = temporary_root / f"figure_{index}"
            subprocess.run(
                [
                    "pdftoppm",
                    "-f",
                    "1",
                    "-singlefile",
                    "-r",
                    "120",
                    "-png",
                    str(path),
                    str(raster_base),
                ],
                check=True,
                capture_output=True,
            )
            raster_path = raster_base.with_suffix(".png")
            with Image.open(raster_path) as raster:
                render_width, render_height = raster.size
            if render_width < 700 or render_height < 400:
                raise RuntimeError(f"rendered PDF is unexpectedly small: {path}")
            pdf_records.append(
                {
                    "path": str(path.relative_to(run_root)),
                    "pages": page_count,
                    "render_width": render_width,
                    "render_height": render_height,
                }
            )
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
    table_dir = run_root / "tables"
    expected_tables = {
        "paired_attention_and_response_estimates.csv": 13,
        "psychometric_response_rates.csv": 161,
        "event_attention_timecourses.csv": 133,
    }
    table_lines = {}
    for name, minimum_lines in expected_tables.items():
        path = table_dir / name
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) < minimum_lines:
            raise RuntimeError(f"table {path} has {len(lines)} lines, expected at least {minimum_lines}")
        table_lines[name] = len(lines)
    return {
        "figure_triplets": len(pdfs),
        "pdf_records": pdf_records,
        "table_lines": table_lines,
    }


def _write_json_exclusive(path: Path, payload: Any) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite JSON artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _snapshot_sources(run_root: Path, captured: dict[str, bytes]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    snapshot_root = run_root / "provenance" / "source_snapshot"
    for relative, content in captured.items():
        destination = snapshot_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError(f"refusing to overwrite source snapshot: {destination}")
        destination.write_bytes(content)
        records[relative] = {
            "snapshot_path": str(destination.relative_to(run_root)),
            "sha256": sha256_bytes(content),
            "bytes": len(content),
        }
    return records


def _build_manifest(
    run_root: Path,
    *,
    cache_metadata: dict[str, Any],
    frozen_manifest: dict[str, Any],
    source_records: dict[str, dict[str, Any]],
    verification: dict[str, Any],
    runtime_versions: dict[str, str],
    started_at: str,
    completed_at: str,
) -> Path:
    manifest_path = run_root / "MANIFEST.json"
    if manifest_path.exists():
        raise FileExistsError(f"refusing to overwrite manifest: {manifest_path}")
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
        "schema_version": 1,
        "status": "complete",
        "analysis": "standalone_vda4_crossattn1_memory_decay_comparison",
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "cache": cache_metadata,
        "frozen_inputs": frozen_manifest,
        "source_snapshot": source_records,
        "runtime_versions": runtime_versions,
        "verification": verification,
        "artifact_inventory": inventory,
        "interpretation_boundary": (
            "standard iter 20000 versus high-decay iter 14649; checkpoint comparison only, "
            "evaluation-trial uncertainty only"
        ),
    }
    _write_json_exclusive(manifest_path, manifest)
    loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
    if loaded["status"] != "complete":
        raise RuntimeError("manifest round-trip failed")
    for record in loaded["artifact_inventory"]:
        artifact = run_root / record["path"]
        if artifact.stat().st_size != record["bytes"] or sha256_path(artifact) != record["sha256"]:
            raise RuntimeError(f"artifact changed while finalizing manifest: {artifact}")
    return manifest_path


def build_artifacts(
    run_root: Path,
    cache_path: Path,
    records: dict[str, dict[str, Any]],
    *,
    captured_sources: dict[str, bytes],
    command: str,
    runtime_versions: dict[str, str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    import matplotlib

    matplotlib.use("Agg", force=True)
    figure_dir = run_root / "figures"
    table_dir = run_root / "tables"
    provenance_dir = run_root / "provenance"
    for directory in (figure_dir, table_dir, provenance_dir):
        directory.mkdir(parents=True, exist_ok=True)
    with np.load(cache_path, allow_pickle=False) as payload:
        summary, metric_pairs = build_numeric_summary(payload)
        _build_event_map_figure(payload, figure_dir)
        _build_query_level_figures(payload, figure_dir)
        _build_nochange_figures(payload, figure_dir)
        _build_metric_figure(payload, figure_dir, summary)
        _build_psychometric_figure(payload, figure_dir)
        write_tables(payload, summary, metric_pairs, table_dir)
    _write_json_exclusive(run_root / "SUMMARY.json", summary)
    write_report(run_root, summary, records)
    source_records = _snapshot_sources(run_root, captured_sources)
    _write_json_exclusive(provenance_dir / "runtime_versions.json", runtime_versions)
    command_path = provenance_dir / "COMMAND.txt"
    if command_path.exists():
        raise FileExistsError(f"refusing to overwrite command provenance: {command_path}")
    command_path.write_text(command + "\n", encoding="utf-8")
    verification = verify_rendered_outputs(run_root)
    _write_json_exclusive(provenance_dir / "render_verification.json", verification)
    return summary, {"source_records": source_records, "render_verification": verification}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--attention-trials", type=int, default=256)
    parser.add_argument("--nochange-trials", type=int, default=128)
    parser.add_argument("--psychometric-trials", type=int, default=300)
    parser.add_argument("--threads", type=int, default=3)
    parser.add_argument(
        "--reuse-cache",
        action="store_true",
        help="validate and reuse an existing immutable cache after a rendering-only failure",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_root = args.run_root.expanduser().resolve()
    if not run_root.is_dir():
        raise FileNotFoundError(f"run root does not exist: {run_root}")
    if (run_root / "MANIFEST.json").exists():
        raise FileExistsError(f"analysis is already complete: {run_root / 'MANIFEST.json'}")
    if args.threads <= 0:
        raise ValueError("--threads must be positive")
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    captured_sources = capture_executable_sources()
    started_at = datetime.now(timezone.utc).isoformat()

    import torch

    torch.set_num_threads(args.threads)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        pass
    frozen_manifest, records = _load_frozen_inputs(run_root)
    runtime_versions = _runtime_versions(torch)
    command = " ".join(
        shlex.quote(value)
        for value in ([str(Path(sys.executable).resolve()), str(Path(__file__).resolve())] + (argv if argv is not None else sys.argv[1:]))
    )
    configuration = {
        "attention_trials": args.attention_trials,
        "nochange_trials": args.nochange_trials,
        "psychometric_trials": args.psychometric_trials,
        "threads": args.threads,
        "device": "cpu",
        "event_seed": EVENT_SEED,
        "nochange_seed": NOCHANGE_SEED,
        "psychometric_seed": PSYCHOMETRIC_SEED,
        "primary_activity_metric": "mean frame-to-frame total variation over the full 4x8 attention map",
        "response_rule": "first argmax change action at frame >= 5",
    }
    _write_json_exclusive(run_root / "provenance" / "analysis_config.json", configuration)
    cache_path = run_root / "data" / "comparison_evidence.npz"
    if args.reuse_cache:
        if not cache_path.is_file():
            raise FileNotFoundError(f"--reuse-cache requested but cache is absent: {cache_path}")
    else:
        cache_path = compute_comparison_cache(
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
    summary, artifact_state = build_artifacts(
        run_root,
        cache_path,
        records,
        captured_sources=captured_sources,
        command=command,
        runtime_versions=runtime_versions,
    )
    assert_sources_unchanged(captured_sources)
    for role, record in records.items():
        if sha256_path(record["snapshot_path"]) != str(record["sha256"]):
            raise RuntimeError(f"frozen {role} checkpoint changed before finalization")
    completed_at = datetime.now(timezone.utc).isoformat()
    manifest_path = _build_manifest(
        run_root,
        cache_metadata=cache_metadata,
        frozen_manifest=frozen_manifest,
        source_records=artifact_state["source_records"],
        verification=artifact_state["render_verification"],
        runtime_versions=runtime_versions,
        started_at=started_at,
        completed_at=completed_at,
    )
    primary = summary["primary_event_attention_motion"]
    print(
        json.dumps(
            {
                "status": "complete",
                "run_root": str(run_root),
                "manifest": str(manifest_path),
                "hypothesis_verdict": primary["hypothesis_verdict"],
                "primary_high_minus_standard": primary["mean_difference"],
                "primary_ci": [primary["ci_low"], primary["ci_high"]],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
