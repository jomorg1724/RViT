"""Paired held-out evaluator for the native-2x2 VDA4 memory-noise pilot.

This is a scientific producer, not a training monitor.  It admits only the two
terminal, independently validated seed-0 checkpoints registered by this
experiment and evaluates the complete 2 x 2 factorial

    training memory noise SD in {0.0, 0.5}
        x evaluation memory noise SD in {0.0, 0.5}.

The evaluator deliberately differs from older VDA convenience scripts in four
important ways:

* actions are sampled (the default and only supported policy rule), using one
  recorded common-random-number uniform bank for every paired model condition;
* evaluation-time mnemonic noise is explicitly enabled in ``rl_step`` and is
  supplied by a dedicated, recorded standard-normal stream rather than the
  policy RNG or PyTorch's process-global RNG;
* cross-attention is never fused for primary measurement: the full 4x4 visual
  matrix and full 4x4 recurrent-memory matrix are retained separately; and
* a disjoint competence/nonsaturation calibration is locked before the frozen
  psychometric, attention, and causal-intervention banks are generated.

Outputs are first written to a unique staging directory and atomically promoted
only after internal validation.  Existing output roots are never overwritten.
The resulting JSON, NPZ, and CSV artifacts are bound by SHA-256 in MANIFEST.json.

Training metrics, checkpoint validation, calibration, and GPU health are not
behavioral or mechanistic evidence.  This evaluator labels those boundaries in
its artifacts.  One seed is a pilot and cannot establish population-level seed
replication.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import json
import math
import os
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from unittest import mock

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT_DIR = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SCHEMA_VERSION = 1
TASK = "vda4"
FEEDBACK = "crossattn1"
GRID_ROWS = 2
GRID_COLS = 2
N_PATCHES = 4
D_MEM = 128
TRAIN_NOISE_LEVELS = (0.0, 0.5)
EVAL_NOISE_LEVELS = (0.0, 0.5)
T = 7
VALIDITIES = np.asarray([0.25, 0.50, 0.75, 1.00], dtype=np.float64)
PRIMARY_VALIDITY = 0.75
PRIMARY_VALIDITY_INDEX = 2
LOCATIONS = tuple(range(N_PATCHES))
ORDERED_INVALID_PAIRS = tuple(
    (cue_index, change_index)
    for cue_index in LOCATIONS
    for change_index in LOCATIONS
    if change_index != cue_index
)
COLOR = "red"
QUALIFYING_FRAMES = (5, 6)
MAGNITUDES = np.asarray(
    [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 22.0, 26.0, 30.0],
    dtype=np.float64,
)
CALIBRATION_MAGNITUDES = np.asarray(
    [3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 22.0, 26.0, 30.0],
    dtype=np.float64,
)
CONDITIONS = ("valid", "invalid")
SOURCES = ("visual", "memory")
CLAMP_FROM = 5
CLAMP_LOGIT_BIAS = 6.0
INTERVENTION_ROLES = ("true_change", "cued_wrong", "neutral_control")
INTERVENTION_SOURCES = ("visual", "memory", "both")
INTERVENTION_DOSES = np.asarray([0.0, 0.25, 0.50, 0.75, 1.00], dtype=np.float64)
FIGURE_STEMS = {
    "psychometric_sdt": "psychometric_rt_sdt",
    "visual_maps": "attention_visual_column_score_maps",
    "memory_maps": "attention_memory_column_score_maps",
    "source_timecourses": "attention_source_timecourses",
    "interventions": "causal_intervention_dose_response",
}

# These bases are labels only.  Every actual bank seed is derived from a stable
# SHA-256 namespace, so adding a bank cannot shift any existing random stream.
RNG_NAMESPACE = "vda4_memory_noise_paired_eval_v1"
CALIBRATION_NAMESPACE = "calibration_v1"
FROZEN_NAMESPACE = "frozen_evaluation_v1"
PROBE_NAMESPACE = "noise_activation_probe_v1"


@dataclass(frozen=True)
class ModelSpec:
    label: str
    train_noise_std: float
    run_dir: Path
    checkpoint: Path
    expected_checkpoint_sha256: str
    log: Path | None


@dataclass(frozen=True)
class EvaluationCell:
    label: str
    model_label: str
    train_noise_std: float
    eval_noise_std: float


@dataclass
class TrialBank:
    bank_id: str
    videos: Any
    policy_uniforms: np.ndarray
    memory_noise_seed: int
    registry: dict[str, Any]


def allocate_spatial_strata(
    total_trials: int, condition: str
) -> tuple[tuple[int, int, int], ...]:
    """Return exactly balanced ``(cue, change, n)`` spatial strata.

    Invalid conditions use all 12 ordered cue-to-uncued-target pairs.  Valid and
    no-change conditions balance across the four cue locations.  Requiring the
    aggregate budget to be divisible by 12 makes every comparison have the same
    total trial count while preserving exact location balance.
    """
    if isinstance(total_trials, (bool, np.bool_)) or not isinstance(
        total_trials, (int, np.integer)
    ):
        raise TypeError("total_trials must be an integer (not bool)")
    total_trials = int(total_trials)
    if total_trials <= 0 or total_trials % len(ORDERED_INVALID_PAIRS):
        raise ValueError(
            f"total_trials must be positive and divisible by 12; got {total_trials}"
        )
    if condition == "invalid":
        per = total_trials // len(ORDERED_INVALID_PAIRS)
        return tuple((cue, change, per) for cue, change in ORDERED_INVALID_PAIRS)
    if condition in {"valid", "nochange"}:
        per = total_trials // len(LOCATIONS)
        return tuple((cue, cue, per) for cue in LOCATIONS)
    raise ValueError(f"unsupported spatial condition {condition!r}")


def expected_figure_paths(root: str | Path) -> tuple[Path, ...]:
    """Return the deterministic PNG/PDF figure inventory."""
    figure_root = Path(root) / "figures"
    return tuple(
        figure_root / f"{stem}.{suffix}"
        for stem in FIGURE_STEMS.values()
        for suffix in ("png", "pdf")
    )


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def stable_seed(*parts: Any, bits: int = 63) -> int:
    """Derive a deterministic seed without depending on Python's salted hash."""
    material = "|".join((RNG_NAMESPACE, *(str(part) for part in parts))).encode("utf-8")
    value = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    return value & ((1 << bits) - 1)


def jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _finite_array(name: str, value: Any) -> np.ndarray:
    array = np.asarray(value)
    if np.issubdtype(array.dtype, np.inexact) and not np.isfinite(array).all():
        raise ValueError(f"{name} contains non-finite values")
    return array


def split_source_attention(raw_attention: Any) -> tuple[np.ndarray, np.ndarray]:
    """Split (..., 4 queries, 8 keys) into visual and memory 4x4 maps."""
    raw = _finite_array("raw_attention", raw_attention)
    if raw.ndim < 2 or raw.shape[-2:] != (N_PATCHES, 2 * N_PATCHES):
        raise ValueError(
            "cross-attention must end in (4 visual queries, 8 visual+memory keys); "
            f"got {raw.shape}"
        )
    if np.any(raw < -1e-7) or not np.allclose(raw.sum(axis=-1), 1.0, atol=2e-5):
        raise ValueError("cross-attention rows are not non-negative normalized probabilities")
    return raw[..., :N_PATCHES], raw[..., N_PATCHES:]


def column_averaged_patch_scores(source_attention: Any) -> np.ndarray:
    """Incoming key score: sum down a key column and divide by four queries."""
    source = _finite_array("source_attention", source_attention).astype(np.float64, copy=False)
    if source.ndim < 2 or source.shape[-2:] != (N_PATCHES, N_PATCHES):
        raise ValueError(f"source attention must end in a 4x4 matrix; got {source.shape}")
    if np.any(source < -1e-7):
        raise ValueError("source attention contains negative weights")
    return source.mean(axis=-2)


def source_attention_metrics(source_attention: Any, target_index: int) -> dict[str, np.ndarray]:
    """Return exact per-trial/per-frame source-separated allocation measures.

    Because this pilot's native discretization is already 2x2, every physical
    region contains exactly one patch.  Therefore ``patch_score`` is also the
    requested maximum-patch score within that region.  It is still kept under a
    patch name so the estimator remains explicit rather than silently changing
    across discretizations.
    """
    if target_index not in range(N_PATCHES):
        raise ValueError(f"target_index must be in 0..3; got {target_index}")
    patch = column_averaged_patch_scores(source_attention)
    share = patch.sum(axis=-1)
    if np.any(share <= 0.0):
        raise ValueError("source share must be strictly positive for conditional metrics")
    conditional = patch / share[..., None]
    if not np.allclose(conditional.sum(axis=-1), 1.0, atol=2e-6):
        raise RuntimeError("conditional source allocation failed normalization")
    distractors = [index for index in range(N_PATCHES) if index != target_index]
    target_raw = patch[..., target_index]
    target_conditional = conditional[..., target_index]
    distractor_mean = conditional[..., distractors].mean(axis=-1)
    max_raw = patch.max(axis=-1)
    max_conditional = conditional.max(axis=-1)
    entropy_nats = -(conditional * np.log(np.clip(conditional, 1e-12, 1.0))).sum(axis=-1)
    return {
        "patch_score": patch.astype(np.float32),
        "source_share": share.astype(np.float32),
        "conditional_patch_score": conditional.astype(np.float32),
        "target_raw": target_raw.astype(np.float32),
        "target_conditional": target_conditional.astype(np.float32),
        "distractor_conditional_mean": distractor_mean.astype(np.float32),
        "target_selectivity": (target_conditional - distractor_mean).astype(np.float32),
        "max_raw_patch": max_raw.astype(np.float32),
        "max_conditional_patch": max_conditional.astype(np.float32),
        "normalized_max_conditional": (N_PATCHES * max_conditional).astype(np.float32),
        "normalized_entropy": (entropy_nats / math.log(N_PATCHES)).astype(np.float32),
        "effective_locations": np.exp(entropy_nats).astype(np.float32),
    }


def source_attention_metrics_by_trial(
    source_attention: Any,
    target_indices: Any,
    cue_indices: Any,
) -> dict[str, np.ndarray]:
    """Trial-specific target/cue metrics for counterbalanced spatial banks.

    The input must be ``(trials, frames, 4 queries, 4 source keys)``.  Cue and
    target identities are retained rather than replaced by a fixed exemplar.
    Prechange frames (t1--t4) are interpreted only with cue-aligned measures;
    target localization and cue-to-target reorientation are interpreted only
    after the change appears at t5--t6.
    """
    source = _finite_array("source_attention", source_attention)
    targets = np.asarray(target_indices, dtype=np.int64)
    cues = np.asarray(cue_indices, dtype=np.int64)
    if source.ndim != 4 or source.shape[1:] != (T, N_PATCHES, N_PATCHES):
        raise ValueError(f"source attention must be (trials,{T},4,4); got {source.shape}")
    if targets.shape != (source.shape[0],) or cues.shape != targets.shape:
        raise ValueError("trial-specific cue/target indices do not match attention trials")
    if np.any((targets < 0) | (targets >= N_PATCHES) | (cues < 0) | (cues >= N_PATCHES)):
        raise ValueError("cue/target indices must lie in the native 2x2 grid")
    patch = column_averaged_patch_scores(source)
    share = patch.sum(axis=-1)
    if np.any(share <= 0.0):
        raise ValueError("source share must be strictly positive")
    conditional = patch / share[..., None]
    target = np.take_along_axis(
        conditional, targets[:, None, None], axis=-1
    ).squeeze(-1)
    cue = np.take_along_axis(
        conditional, cues[:, None, None], axis=-1
    ).squeeze(-1)
    target_raw = np.take_along_axis(patch, targets[:, None, None], axis=-1).squeeze(-1)
    cue_raw = np.take_along_axis(patch, cues[:, None, None], axis=-1).squeeze(-1)
    distractor_mean = (1.0 - target) / float(N_PATCHES - 1)
    max_raw = patch.max(axis=-1)
    max_conditional = conditional.max(axis=-1)
    entropy_nats = -(conditional * np.log(np.clip(conditional, 1e-12, 1.0))).sum(axis=-1)
    return {
        "patch_score": patch.astype(np.float32),
        "source_share": share.astype(np.float32),
        "conditional_patch_score": conditional.astype(np.float32),
        "target_raw": target_raw.astype(np.float32),
        "cue_raw": cue_raw.astype(np.float32),
        "target_conditional": target.astype(np.float32),
        "cue_conditional": cue.astype(np.float32),
        "distractor_conditional_mean": distractor_mean.astype(np.float32),
        "target_selectivity": (target - distractor_mean).astype(np.float32),
        "target_minus_cue": (target - cue).astype(np.float32),
        "max_raw_patch": max_raw.astype(np.float32),
        "max_conditional_patch": max_conditional.astype(np.float32),
        "normalized_max_conditional": (N_PATCHES * max_conditional).astype(np.float32),
        "normalized_entropy": (entropy_nats / math.log(N_PATCHES)).astype(np.float32),
        "effective_locations": np.exp(entropy_nats).astype(np.float32),
    }


def sample_actions_from_logits(logits: Any, uniforms: Any) -> np.ndarray:
    """Sample binary policy actions with externally supplied common uniforms."""
    values = _finite_array("logits", logits).astype(np.float64, copy=False)
    draws = _finite_array("policy_uniforms", uniforms).astype(np.float64, copy=False)
    if values.shape[-1] != 2 or values.shape[:-1] != draws.shape:
        raise ValueError(f"logits/uniform shape mismatch: {values.shape} versus {draws.shape}")
    if np.any((draws < 0.0) | (draws >= 1.0)):
        raise ValueError("policy uniforms must lie in [0, 1)")
    shifted = values - values.max(axis=-1, keepdims=True)
    exp_values = np.exp(shifted)
    p_action_1 = exp_values[..., 1] / exp_values.sum(axis=-1)
    return (draws < p_action_1).astype(np.int64)


def policy_action1_probability(logits: Any) -> np.ndarray:
    values = _finite_array("logits", logits).astype(np.float64, copy=False)
    shifted = values - values.max(axis=-1, keepdims=True)
    exp_values = np.exp(shifted)
    return (exp_values[..., 1] / exp_values.sum(axis=-1)).astype(np.float32)


def first_press(actions: Any) -> np.ndarray:
    values = np.asarray(actions, dtype=np.int64)
    if values.ndim != 2 or values.shape[1] != T:
        raise ValueError(f"actions must have shape (trials, {T}); got {values.shape}")
    presses = np.full(values.shape[0], -1, dtype=np.int64)
    for frame in range(T):
        new = (values[:, frame] == 1) & (presses < 0)
        presses[new] = frame
    return presses


def press_histogram(presses: Any) -> np.ndarray:
    values = np.asarray(presses, dtype=np.int64)
    return np.asarray([(values == frame).sum() for frame in (-1, 0, 1, 2, 3, 4, 5, 6)], dtype=np.int64)


def qualifying_stats(presses: Any, *, nochange: bool) -> dict[str, Any]:
    values = np.asarray(presses, dtype=np.int64)
    detected = values >= 0 if nochange else np.isin(values, QUALIFYING_FRAMES)
    qualifying = int(detected.sum())
    return {
        "response_count": qualifying,
        "response_rate": qualifying / float(values.size),
        "mean_rt": float(values[detected].mean()) if qualifying else float("nan"),
        "press_histogram": press_histogram(values),
        "early_response_count": int(np.isin(values, (0, 1, 2, 3, 4)).sum()),
        "no_response_count": int((values < 0).sum()),
    }


def hautus_sdt(hit_count: int, false_alarm_count: int, n_hit: int, n_fa: int) -> tuple[float, float]:
    from scipy.stats import norm

    if min(hit_count, false_alarm_count, n_hit, n_fa) < 0 or hit_count > n_hit or false_alarm_count > n_fa:
        raise ValueError("invalid SDT counts")
    hit_rate = (float(hit_count) + 0.5) / (float(n_hit) + 1.0)
    false_alarm_rate = (float(false_alarm_count) + 0.5) / (float(n_fa) + 1.0)
    z_hit = float(norm.ppf(hit_rate))
    z_false_alarm = float(norm.ppf(false_alarm_rate))
    return z_hit - z_false_alarm, -0.5 * (z_hit + z_false_alarm)


def threshold50(magnitudes: Any, response_rates: Any) -> float:
    """Monotone-envelope linear crossing; NaN when 0.5 is not bracketed."""
    x = _finite_array("magnitudes", magnitudes).astype(np.float64, copy=False)
    y = _finite_array("response_rates", response_rates).astype(np.float64, copy=False)
    if x.ndim != 1 or y.shape != x.shape or np.any(np.diff(x) <= 0):
        raise ValueError("threshold inputs must be aligned increasing one-dimensional arrays")
    monotone = np.maximum.accumulate(y)
    if monotone[0] > 0.5 or monotone[-1] < 0.5:
        return float("nan")
    upper = int(np.searchsorted(monotone, 0.5, side="left"))
    if upper == 0:
        return float(x[0])
    lower = upper - 1
    if monotone[upper] == monotone[lower]:
        return float((x[lower] + x[upper]) / 2.0)
    fraction = (0.5 - monotone[lower]) / (monotone[upper] - monotone[lower])
    return float(x[lower] + fraction * (x[upper] - x[lower]))


def choose_common_focal_magnitude(
    magnitudes: Any,
    invalid_rates: Any,
    *,
    target: float = 0.60,
    bounds: tuple[float, float] = (0.20, 0.80),
) -> dict[str, Any]:
    """Choose one common angle across all four cells before frozen evaluation."""
    x = _finite_array("magnitudes", magnitudes).astype(np.float64, copy=False)
    rates = _finite_array("invalid_rates", invalid_rates).astype(np.float64, copy=False)
    if x.ndim != 1 or rates.ndim != 2 or rates.shape[1] != x.size:
        raise ValueError(f"expected invalid_rates shape (cells, {x.size}); got {rates.shape}")
    lower, upper = map(float, bounds)
    if not (0.0 <= lower < target < upper <= 1.0):
        raise ValueError("nonsaturation bounds must contain target inside [0,1]")
    admitted = np.all((rates >= lower) & (rates <= upper), axis=0)
    squared = np.mean((rates - target) ** 2, axis=0)
    if admitted.any():
        candidates = np.flatnonzero(admitted)
        index = int(candidates[np.argmin(squared[candidates])])
        passed = True
        reason = "all four factorial cells lie inside the preregistered nonsaturation interval"
    else:
        # Retain diagnostics at the least saturated common angle, but fail the
        # mechanistic interpretation gate.  Distance outside the interval has
        # priority over closeness to the target.
        outside = np.maximum(lower - rates, 0.0) + np.maximum(rates - upper, 0.0)
        score = np.max(outside, axis=0) * 100.0 + squared
        index = int(np.argmin(score))
        passed = False
        reason = (
            "no angle placed all four cells inside the nonsaturation interval; "
            "frozen maps/interventions are retained as gated diagnostics"
        )
    return {
        "index": index,
        "magnitude_degrees": float(x[index]),
        "invalid_response_rates_by_cell": rates[:, index],
        "target_response_rate": float(target),
        "nonsaturation_bounds": [lower, upper],
        "common_nonsaturation_pass": passed,
        "selection_reason": reason,
    }


def set_runtime_memory_noise(model: Any, eval_noise_std: float) -> dict[str, Any]:
    """Set the evaluation dose on the actual recurrent cell and verify it."""
    dose = float(eval_noise_std)
    if dose not in EVAL_NOISE_LEVELS:
        raise ValueError(f"evaluation memory noise must be one of {EVAL_NOISE_LEVELS}; got {dose}")
    encoder = getattr(model, "encoder", None)
    if encoder is None or str(getattr(encoder, "feedback", "")) != FEEDBACK:
        raise ValueError("model is not a crossattn1 recurrent encoder")
    if str(getattr(encoder, "cell", "")) != "xlstm" or bool(getattr(encoder, "two_lstm", True)):
        raise ValueError("pilot evaluation requires one xLSTM")
    lstm = getattr(encoder, "lstm", None)
    if lstm is None or not hasattr(lstm, "memory_noise_std"):
        raise ValueError("encoder.lstm does not expose memory_noise_std")
    encoder.memory_noise_std = dose
    lstm.memory_noise_std = dose
    observed = float(lstm.memory_noise_std)
    if not math.isclose(observed, dose, rel_tol=0.0, abs_tol=0.0):
        raise RuntimeError(f"runtime memory-noise assignment failed: {observed} != {dose}")
    return {
        "encoder_memory_noise_std": float(encoder.memory_noise_std),
        "lstm_memory_noise_std": observed,
        "inject_memory_noise": bool(dose > 0.0),
    }


class ControlledMnemonicNoise:
    """Dedicated NumPy-generated standard-normal stream for ``randn_like``.

    The production cell calls ``torch.randn_like(C)`` once per recurrent update.
    This controller supplies those values without touching the global PyTorch RNG
    and fingerprints the exact standard-normal arrays.  It fails closed if the
    model calls the random primitive an unexpected number of times.
    """

    def __init__(self, seed: int) -> None:
        self.seed = int(seed)
        self.rng = np.random.default_rng(self.seed)
        self.calls = 0
        self._digest = hashlib.sha256()

    def randn_like(self, tensor: Any, *args: Any, **kwargs: Any) -> Any:
        import torch

        if args or any(key not in {"dtype", "device", "layout", "requires_grad", "memory_format"} for key in kwargs):
            raise RuntimeError("unexpected torch.randn_like signature in mnemonic-noise path")
        dtype = kwargs.get("dtype") or tensor.dtype
        device = kwargs.get("device") or tensor.device
        if not tensor.is_floating_point() or tuple(tensor.shape[-2:]) != (N_PATCHES, D_MEM):
            raise RuntimeError(f"unexpected mnemonic noise target shape/dtype: {tuple(tensor.shape)} {tensor.dtype}")
        standard = self.rng.standard_normal(tuple(int(v) for v in tensor.shape)).astype(np.float32)
        self._digest.update(self.calls.to_bytes(4, "little"))
        self._digest.update(np.asarray(standard.shape, dtype=np.int64).tobytes())
        self._digest.update(standard.tobytes(order="C"))
        self.calls += 1
        result = torch.from_numpy(standard).to(device=device, dtype=dtype)
        if bool(kwargs.get("requires_grad", False)):
            result.requires_grad_(True)
        return result

    @property
    def sha256(self) -> str:
        return self._digest.hexdigest()

    @contextlib.contextmanager
    def installed(self) -> Iterable[None]:
        import torch

        with mock.patch.object(torch, "randn_like", side_effect=self.randn_like):
            yield


def _unwrap_attention(value: Any) -> Any:
    while isinstance(value, (list, tuple)) and len(value) == 1:
        value = value[0]
    if isinstance(value, (list, tuple)) or value is None:
        raise RuntimeError("expected exactly one cross-attention tensor")
    return value


def rollout_sampled(
    model: Any,
    bank: TrialBank,
    *,
    eval_noise_std: float,
    clamp: dict[str, float] | None = None,
    clamp_from: int = CLAMP_FROM,
    return_attention: bool = False,
    return_recurrent: bool = False,
) -> dict[str, Any]:
    import torch

    runtime = set_runtime_memory_noise(model, eval_noise_std)
    videos = bank.videos
    batch = int(videos.shape[0])
    if bank.policy_uniforms.shape != (batch, T):
        raise ValueError("trial bank policy uniforms do not match video batch")
    state = model.init_states(batch, device=videos.device)
    noise = ControlledMnemonicNoise(bank.memory_noise_seed)
    logits: list[np.ndarray] = []
    attention: list[np.ndarray] = []
    recurrent: list[np.ndarray] = []
    inject = bool(eval_noise_std > 0.0)
    for frame in range(T):
        active_clamp = clamp if clamp is not None and frame >= int(clamp_from) else None
        context = noise.installed() if inject else contextlib.nullcontext()
        with torch.no_grad(), context:
            step = model.rl_step(
                videos[:, frame],
                state,
                return_attn=return_attention,
                attn_clamp=active_clamp,
                inject_memory_noise=inject,
            )
        state = step["new_states"]
        logits.append(step["actor_logits"].detach().cpu().numpy().astype(np.float32))
        if return_attention:
            raw = _unwrap_attention(step["attn"])
            attention.append(raw.detach().cpu().numpy().astype(np.float32))
        if return_recurrent:
            recurrent.append(step["rec"].detach().cpu().numpy().astype(np.float32))
    expected_calls = T if inject else 0
    if noise.calls != expected_calls:
        raise RuntimeError(
            f"evaluation memory-noise activation contract failed: {noise.calls} randn_like calls, "
            f"expected {expected_calls}"
        )
    logits_array = np.stack(logits, axis=1)
    actions = sample_actions_from_logits(logits_array, bank.policy_uniforms)
    result: dict[str, Any] = {
        "logits": logits_array,
        "action1_probability": policy_action1_probability(logits_array),
        "actions": actions,
        "press": first_press(actions),
        "runtime_noise_contract": runtime,
        "memory_noise_seed": int(bank.memory_noise_seed),
        "memory_noise_draw_calls": int(noise.calls),
        "memory_noise_schedule_sha256": noise.sha256 if inject else "disabled",
    }
    if return_attention:
        result["attention"] = np.stack(attention, axis=1)
    if return_recurrent:
        result["recurrent"] = np.stack(recurrent, axis=1)
    return result


def make_trial_bank(
    core: Any,
    registry: dict[str, dict[str, Any]],
    *,
    namespace: str,
    assay: str,
    condition: str,
    trials: int,
    displayed_validity: float,
    cue_index: int,
    changed: int,
    change_index: int,
    magnitude: float,
) -> TrialBank:
    if trials <= 0:
        raise ValueError("trial count must be positive")
    bank_id = (
        f"{namespace}|{assay}|{condition}|validity={float(displayed_validity):g}|"
        f"cue={int(cue_index)}|changed={int(changed)}|"
        f"index={int(change_index)}|magnitude={float(magnitude):g}|n={int(trials)}"
    )
    sensory_seed = stable_seed(bank_id, "sensory", bits=32)
    policy_seed = stable_seed(bank_id, "policy", bits=63)
    memory_seed = stable_seed(bank_id, "mnemonic", bits=63)
    videos = core.make_video_batch(
        TASK,
        int(cue_index),
        float(displayed_validity),
        COLOR,
        int(changed),
        int(change_index),
        float(magnitude),
        B=int(trials),
        seed=int(sensory_seed),
    )
    policy_uniforms = np.random.default_rng(policy_seed).random((int(trials), T)).astype(np.float32)
    video_cpu = videos.detach().cpu().numpy()
    record = {
        "bank_id": bank_id,
        "namespace": namespace,
        "assay": assay,
        "condition": condition,
        "trials": int(trials),
        "task": TASK,
        "cue_index": int(cue_index),
        "displayed_validity": float(displayed_validity),
        "color": COLOR,
        "changed": int(changed),
        "change_index": int(change_index),
        "magnitude_degrees": float(magnitude),
        "sensory_seed": int(sensory_seed),
        "policy_uniform_seed": int(policy_seed),
        "memory_noise_seed": int(memory_seed),
        "video_shape": list(video_cpu.shape),
        "video_dtype": str(video_cpu.dtype),
        "video_sha256": sha256_bytes(video_cpu.tobytes(order="C")),
        "policy_uniform_shape": list(policy_uniforms.shape),
        "policy_uniform_sha256": sha256_bytes(policy_uniforms.tobytes(order="C")),
    }
    existing = registry.get(bank_id)
    if existing is not None and existing != record:
        raise RuntimeError(f"trial-bank identity collision for {bank_id}")
    registry[bank_id] = record
    return TrialBank(bank_id, videos, policy_uniforms, int(memory_seed), record)


def paired_rollouts(
    bank: TrialBank,
    models: Mapping[str, Any],
    cells: Sequence[EvaluationCell],
    *,
    clamp: dict[str, float] | None = None,
    return_attention: bool = False,
    return_recurrent: bool = False,
) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for cell in cells:
        result = rollout_sampled(
            models[cell.model_label],
            bank,
            eval_noise_std=cell.eval_noise_std,
            clamp=clamp,
            return_attention=return_attention,
            return_recurrent=return_recurrent,
        )
        results[cell.label] = result
    noisy_fingerprints = {
        result["memory_noise_schedule_sha256"]
        for cell, result in ((cell, results[cell.label]) for cell in cells)
        if cell.eval_noise_std > 0.0
    }
    if len(noisy_fingerprints) != 1:
        raise RuntimeError(
            f"paired cells did not receive the same mnemonic standard-normal schedule: {noisy_fingerprints}"
        )
    return results


def _concatenate_rollout_parts(
    parts: Sequence[dict[str, Any]], spatial_records: Sequence[tuple[int, int, int]]
) -> dict[str, Any]:
    if not parts or len(parts) != len(spatial_records):
        raise ValueError("rollout parts and spatial records must be nonempty and aligned")
    concatenated: dict[str, Any] = {}
    for key in ("logits", "action1_probability", "actions", "press", "attention", "recurrent"):
        present = [key in part for part in parts]
        if any(present) and not all(present):
            raise RuntimeError(f"rollout part inventory mismatch for {key!r}")
        if all(present):
            concatenated[key] = np.concatenate([np.asarray(part[key]) for part in parts], axis=0)
    concatenated["cue_index"] = np.concatenate(
        [np.full(count, cue, dtype=np.int64) for cue, _change, count in spatial_records]
    )
    concatenated["change_index"] = np.concatenate(
        [np.full(count, change, dtype=np.int64) for _cue, change, count in spatial_records]
    )
    concatenated["stratum_index"] = np.concatenate(
        [np.full(count, index, dtype=np.int64) for index, (_cue, _change, count) in enumerate(spatial_records)]
    )
    concatenated["memory_noise_seed_by_stratum"] = [int(part["memory_noise_seed"]) for part in parts]
    concatenated["memory_noise_draw_calls_by_stratum"] = [
        int(part["memory_noise_draw_calls"]) for part in parts
    ]
    concatenated["memory_noise_schedule_sha256_by_stratum"] = [
        str(part["memory_noise_schedule_sha256"]) for part in parts
    ]
    concatenated["runtime_noise_contract"] = dict(parts[-1]["runtime_noise_contract"])
    expected = sum(count for _cue, _change, count in spatial_records)
    if concatenated["press"].shape[0] != expected:
        raise RuntimeError("counterbalanced rollout concatenation changed total trial count")
    return concatenated


def counterbalanced_rollouts(
    core: Any,
    registry: dict[str, dict[str, Any]],
    models: Mapping[str, Any],
    cells: Sequence[EvaluationCell],
    *,
    namespace: str,
    assay: str,
    condition: str,
    total_trials: int,
    displayed_validity: float,
    magnitude: float,
    intervention_role: str = "natural",
    intervention_source: str = "both",
    intervention_dose: float = 0.5,
    return_attention: bool = False,
) -> dict[str, dict[str, Any]]:
    """Run a balanced aggregate bank and retain every trial's spatial stratum."""
    spatial = allocate_spatial_strata(total_trials, condition)
    per_cell_parts: dict[str, list[dict[str, Any]]] = {cell.label: [] for cell in cells}
    for stratum_index, (cue_index, change_index, count) in enumerate(spatial):
        bank = make_trial_bank(
            core,
            registry,
            namespace=namespace,
            assay=assay,
            condition=f"{condition}|stratum={stratum_index}",
            trials=count,
            displayed_validity=float(displayed_validity),
            cue_index=cue_index,
            changed=0 if condition == "nochange" else 1,
            change_index=change_index,
            magnitude=0.0 if condition == "nochange" else float(magnitude),
        )
        clamp = intervention_clamp(
            intervention_role,
            cue_index=cue_index,
            change_index=change_index,
            source=intervention_source,
            dose=intervention_dose,
        )
        results = paired_rollouts(
            bank,
            models,
            cells,
            clamp=clamp,
            return_attention=return_attention,
        )
        for cell in cells:
            per_cell_parts[cell.label].append(results[cell.label])
    aggregate = {
        cell.label: _concatenate_rollout_parts(per_cell_parts[cell.label], spatial)
        for cell in cells
    }
    # Exact model-pair CRN check for every noisy-evaluation stratum.
    noisy_cells = [cell for cell in cells if cell.eval_noise_std > 0.0]
    if len(noisy_cells) >= 2:
        schedules = [
            aggregate[cell.label]["memory_noise_schedule_sha256_by_stratum"]
            for cell in noisy_cells
        ]
        if any(schedule != schedules[0] for schedule in schedules[1:]):
            raise RuntimeError("counterbalanced noisy-evaluation cells received different noise schedules")
    return aggregate


def intervention_clamp(
    role: str,
    *,
    cue_index: int,
    change_index: int,
    source: str = "both",
    dose: float = 0.5,
) -> dict[str, float] | None:
    """Build a graded, spatially specific additive key-logit intervention.

    ``dose`` alpha maps to bias ``6 * (2*alpha - 1)``: alpha=0 suppresses,
    alpha=.5 is an explicit zero-bias control, and alpha=1 boosts.  The natural
    baseline is separate because a zero-bias dictionary is not the same
    provenance condition as no hook.  The current model exposes additive
    per-key biases; it does not expose a valid routing-disabled intervention.
    """
    if role == "natural":
        return None
    if cue_index not in LOCATIONS or change_index not in LOCATIONS:
        raise ValueError("intervention locations must lie in the native 2x2 grid")
    if role not in INTERVENTION_ROLES:
        raise ValueError(f"unknown intervention role {role!r}")
    if source not in INTERVENTION_SOURCES:
        raise ValueError(f"unknown intervention source {source!r}")
    dose = float(dose)
    if not any(math.isclose(dose, float(item), abs_tol=1e-12) for item in INTERVENTION_DOSES):
        raise ValueError(f"unregistered intervention dose {dose}")
    wrong_location = int(cue_index) if cue_index != change_index else (int(cue_index) + 1) % N_PATCHES
    remaining = [index for index in LOCATIONS if index not in {cue_index, change_index, wrong_location}]
    neutral_location = remaining[0] if remaining else (int(change_index) + 2) % N_PATCHES
    location = {
        "true_change": int(change_index),
        "cued_wrong": wrong_location,
        "neutral_control": neutral_location,
    }[role]
    keys: tuple[int, ...]
    if source == "visual":
        keys = (location,)
    elif source == "memory":
        keys = (N_PATCHES + location,)
    else:
        keys = (location, N_PATCHES + location)
    bias = CLAMP_LOGIT_BIAS * (2.0 * dose - 1.0)
    return {str(key): float(bias) for key in keys}


def validate_noise_activation(
    core: Any,
    models: Mapping[str, Any],
    model_specs: Sequence[ModelSpec],
    registry: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    bank = make_trial_bank(
        core,
        registry,
        namespace=PROBE_NAMESPACE,
        assay="runtime_activation",
        condition="invalid",
        trials=4,
        displayed_validity=PRIMARY_VALIDITY,
        cue_index=0,
        changed=1,
        change_index=3,
        magnitude=18.0,
    )
    records: dict[str, Any] = {}
    for spec in model_specs:
        clean = rollout_sampled(
            models[spec.label], bank, eval_noise_std=0.0, return_recurrent=True
        )
        noisy = rollout_sampled(
            models[spec.label], bank, eval_noise_std=0.5, return_recurrent=True
        )
        recurrent_delta = float(np.max(np.abs(noisy["recurrent"] - clean["recurrent"])))
        logit_delta = float(np.max(np.abs(noisy["logits"] - clean["logits"])))
        if noisy["memory_noise_draw_calls"] != T or recurrent_delta <= 0.0 or logit_delta <= 0.0:
            raise RuntimeError(
                f"eval-noise activation probe failed for {spec.label}: calls="
                f"{noisy['memory_noise_draw_calls']} recurrent_delta={recurrent_delta} "
                f"logit_delta={logit_delta}"
            )
        records[spec.label] = {
            "train_noise_std": spec.train_noise_std,
            "probe_bank_id": bank.bank_id,
            "clean_draw_calls": clean["memory_noise_draw_calls"],
            "noisy_draw_calls": noisy["memory_noise_draw_calls"],
            "noisy_schedule_sha256": noisy["memory_noise_schedule_sha256"],
            "max_abs_recurrent_delta": recurrent_delta,
            "max_abs_actor_logit_delta": logit_delta,
            "eval_noise_demonstrably_active": True,
        }
    if len({record["noisy_schedule_sha256"] for record in records.values()}) != 1:
        raise RuntimeError("activation probes did not share the exact mnemonic noise schedule")
    return records


def run_calibration(
    core: Any,
    models: Mapping[str, Any],
    cells: Sequence[EvaluationCell],
    registry: dict[str, dict[str, Any]],
    trials: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    n_cells = len(cells)
    n_magnitudes = len(CALIBRATION_MAGNITUDES)
    counts = np.zeros((n_cells, n_magnitudes, 2), dtype=np.int64)
    rates = np.zeros_like(counts, dtype=np.float64)
    mean_rt = np.full_like(rates, np.nan)
    histograms = np.zeros((n_cells, n_magnitudes, 2, 8), dtype=np.int64)
    action_counts = np.zeros((n_cells, 2), dtype=np.int64)

    nochange_rollouts = counterbalanced_rollouts(
        core, registry, models, cells,
        namespace=CALIBRATION_NAMESPACE,
        assay="competence",
        condition="nochange",
        total_trials=trials,
        displayed_validity=PRIMARY_VALIDITY,
        magnitude=0.0,
    )
    false_alarm_count = np.zeros(n_cells, dtype=np.int64)
    false_alarm_rate = np.zeros(n_cells, dtype=np.float64)
    false_alarm_histogram = np.zeros((n_cells, 8), dtype=np.int64)
    for cell_index, cell in enumerate(cells):
        result = nochange_rollouts[cell.label]
        stats = qualifying_stats(result["press"], nochange=True)
        false_alarm_count[cell_index] = stats["response_count"]
        false_alarm_rate[cell_index] = stats["response_rate"]
        false_alarm_histogram[cell_index] = stats["press_histogram"]
        action_counts[cell_index] += np.bincount(result["actions"].ravel(), minlength=2)[:2]

    for magnitude_index, magnitude in enumerate(CALIBRATION_MAGNITUDES):
        for condition_index, condition in enumerate(CONDITIONS):
            rollouts = counterbalanced_rollouts(
                core, registry, models, cells,
                namespace=CALIBRATION_NAMESPACE,
                assay="competence",
                condition=condition,
                total_trials=trials,
                displayed_validity=PRIMARY_VALIDITY,
                magnitude=float(magnitude),
            )
            for cell_index, cell in enumerate(cells):
                result = rollouts[cell.label]
                stats = qualifying_stats(result["press"], nochange=False)
                counts[cell_index, magnitude_index, condition_index] = stats["response_count"]
                rates[cell_index, magnitude_index, condition_index] = stats["response_rate"]
                mean_rt[cell_index, magnitude_index, condition_index] = stats["mean_rt"]
                histograms[cell_index, magnitude_index, condition_index] = stats["press_histogram"]
                action_counts[cell_index] += np.bincount(result["actions"].ravel(), minlength=2)[:2]

    dprime = np.zeros_like(rates)
    criterion = np.zeros_like(rates)
    for cell_index in range(n_cells):
        for magnitude_index in range(n_magnitudes):
            for condition_index in range(2):
                dprime[cell_index, magnitude_index, condition_index], criterion[
                    cell_index, magnitude_index, condition_index
                ] = hautus_sdt(
                    int(counts[cell_index, magnitude_index, condition_index]),
                    int(false_alarm_count[cell_index]),
                    trials,
                    trials,
                )

    focal = choose_common_focal_magnitude(
        CALIBRATION_MAGNITUDES, rates[:, :, CONDITIONS.index("invalid")]
    )
    competence: list[dict[str, Any]] = []
    for cell_index, cell in enumerate(cells):
        easy_index = int(np.where(CALIBRATION_MAGNITUDES == 30.0)[0][0])
        invalid_slope = float(rates[cell_index, -1, 1] - rates[cell_index, 0, 1])
        gates = {
            "false_alarm_at_most_0p20": bool(false_alarm_rate[cell_index] <= 0.20),
            "easy_valid_response_at_least_0p50": bool(rates[cell_index, easy_index, 0] >= 0.50),
            "easy_invalid_response_at_least_0p50": bool(rates[cell_index, easy_index, 1] >= 0.50),
            "both_policy_actions_present": bool(np.all(action_counts[cell_index] > 0)),
            "positive_invalid_endpoint_slope": bool(invalid_slope > 0.0),
            "easy_invalid_dprime_positive": bool(dprime[cell_index, easy_index, 1] > 0.0),
        }
        competence.append({
            "cell": cell.label,
            "train_noise_std": cell.train_noise_std,
            "eval_noise_std": cell.eval_noise_std,
            "false_alarm_rate": float(false_alarm_rate[cell_index]),
            "easy_valid_response_rate_30deg": float(rates[cell_index, easy_index, 0]),
            "easy_invalid_response_rate_30deg": float(rates[cell_index, easy_index, 1]),
            "easy_invalid_dprime_30deg": float(dprime[cell_index, easy_index, 1]),
            "invalid_endpoint_slope_3_to_30deg": invalid_slope,
            "policy_action_counts": action_counts[cell_index],
            "gates": gates,
            "competence_pass": bool(all(gates.values())),
        })

    payload = {
        "cell_labels": np.asarray([cell.label for cell in cells]),
        "magnitudes": CALIBRATION_MAGNITUDES,
        "conditions": np.asarray(CONDITIONS),
        "response_count": counts,
        "response_rate": rates,
        "mean_rt": mean_rt,
        "press_histogram": histograms,
        "false_alarm_count": false_alarm_count,
        "false_alarm_rate": false_alarm_rate,
        "false_alarm_histogram": false_alarm_histogram,
        "dprime": dprime,
        "criterion": criterion,
        "policy_action_counts": action_counts,
    }
    lock = {
        "schema_version": SCHEMA_VERSION,
        "stage": "competence_and_nonsaturation_calibration_only",
        "scientific_evidence_status": "interpretation_gate_not_primary_result",
        "calibration_namespace": CALIBRATION_NAMESPACE,
        "trials_per_bank": int(trials),
        "displayed_validity": PRIMARY_VALIDITY,
        "spatial_counterbalancing": "valid/nochange four cues; invalid all 12 ordered cue-target pairs",
        "cells": [cell.__dict__ for cell in cells],
        "competence": competence,
        "all_cells_competent": bool(all(item["competence_pass"] for item in competence)),
        "focal_selection": focal,
        "frozen_evaluation_namespace": FROZEN_NAMESPACE,
        "rule": (
            "The common focal magnitude was selected once from disjoint calibration banks, "
            "then frozen for all four train-noise x eval-noise cells and all natural/intervention assays."
        ),
    }
    return payload, lock


def run_psychometrics(
    core: Any,
    models: Mapping[str, Any],
    cells: Sequence[EvaluationCell],
    registry: dict[str, dict[str, Any]],
    trials: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    n_cells, n_validities, n_magnitudes = len(cells), len(VALIDITIES), len(MAGNITUDES)
    shape = (n_cells, n_validities, n_magnitudes, len(CONDITIONS))
    counts = np.zeros(shape, dtype=np.int64)
    rates = np.zeros(shape, dtype=np.float64)
    mean_rt = np.full(shape, np.nan, dtype=np.float64)
    histograms = np.zeros(shape + (8,), dtype=np.int64)
    early_counts = np.zeros(shape, dtype=np.int64)
    presses = np.zeros(shape + (trials,), dtype=np.int64)
    cue_indices = np.zeros((n_validities, n_magnitudes, len(CONDITIONS), trials), dtype=np.int64)
    change_indices = np.zeros_like(cue_indices)
    nochange_press = np.zeros((n_cells, n_validities, trials), dtype=np.int64)
    nochange_cue = np.zeros((n_validities, trials), dtype=np.int64)
    false_alarm_count = np.zeros((n_cells, n_validities), dtype=np.int64)
    false_alarm_rate = np.zeros((n_cells, n_validities), dtype=np.float64)
    false_alarm_histogram = np.zeros((n_cells, n_validities, 8), dtype=np.int64)

    for validity_index, validity in enumerate(VALIDITIES):
        nochange = counterbalanced_rollouts(
            core, registry, models, cells,
            namespace=FROZEN_NAMESPACE, assay="psychometrics",
            condition="nochange", total_trials=trials,
            displayed_validity=float(validity), magnitude=0.0,
        )
        for cell_index, cell in enumerate(cells):
            result = nochange[cell.label]
            stats = qualifying_stats(result["press"], nochange=True)
            nochange_press[cell_index, validity_index] = result["press"]
            false_alarm_count[cell_index, validity_index] = stats["response_count"]
            false_alarm_rate[cell_index, validity_index] = stats["response_rate"]
            false_alarm_histogram[cell_index, validity_index] = stats["press_histogram"]
        nochange_cue[validity_index] = nochange[cells[0].label]["cue_index"]

        for magnitude_index, magnitude in enumerate(MAGNITUDES):
            for condition_index, condition in enumerate(CONDITIONS):
                rollouts = counterbalanced_rollouts(
                    core, registry, models, cells,
                    namespace=FROZEN_NAMESPACE, assay="psychometrics",
                    condition=condition, total_trials=trials,
                    displayed_validity=float(validity), magnitude=float(magnitude),
                )
                reference = rollouts[cells[0].label]
                cue_indices[validity_index, magnitude_index, condition_index] = reference["cue_index"]
                change_indices[validity_index, magnitude_index, condition_index] = reference["change_index"]
                for cell_index, cell in enumerate(cells):
                    result = rollouts[cell.label]
                    stats = qualifying_stats(result["press"], nochange=False)
                    presses[cell_index, validity_index, magnitude_index, condition_index] = result["press"]
                    counts[cell_index, validity_index, magnitude_index, condition_index] = stats["response_count"]
                    rates[cell_index, validity_index, magnitude_index, condition_index] = stats["response_rate"]
                    mean_rt[cell_index, validity_index, magnitude_index, condition_index] = stats["mean_rt"]
                    histograms[cell_index, validity_index, magnitude_index, condition_index] = stats["press_histogram"]
                    early_counts[cell_index, validity_index, magnitude_index, condition_index] = stats["early_response_count"]

    dprime = np.zeros(shape, dtype=np.float64)
    criterion = np.zeros(shape, dtype=np.float64)
    for cell_index in range(n_cells):
        for validity_index in range(n_validities):
            for magnitude_index in range(n_magnitudes):
                for condition_index in range(len(CONDITIONS)):
                    dprime[cell_index, validity_index, magnitude_index, condition_index], criterion[
                        cell_index, validity_index, magnitude_index, condition_index
                    ] = hautus_sdt(
                        int(counts[cell_index, validity_index, magnitude_index, condition_index]),
                        int(false_alarm_count[cell_index, validity_index]), trials, trials,
                    )

    rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for cell_index, cell in enumerate(cells):
        for validity_index, validity in enumerate(VALIDITIES):
            valid_threshold = threshold50(MAGNITUDES, rates[cell_index, validity_index, :, 0])
            invalid_threshold = threshold50(MAGNITUDES, rates[cell_index, validity_index, :, 1])
            summaries.append({
                "cell": cell.label,
                "train_noise_std": cell.train_noise_std,
                "eval_noise_std": cell.eval_noise_std,
                "displayed_validity": float(validity),
                "validity_scope": "ood_forced_invalid_probe" if validity == 1.0 else "in_distribution",
                "threshold50_valid_degrees": valid_threshold,
                "threshold50_invalid_degrees": invalid_threshold,
                "cueing_threshold_cost_invalid_minus_valid_degrees": invalid_threshold - valid_threshold,
                "false_alarm_rate": float(false_alarm_rate[cell_index, validity_index]),
            })
            for magnitude_index, magnitude in enumerate(MAGNITUDES):
                for condition_index, condition in enumerate(CONDITIONS):
                    base = {
                        "cell": cell.label,
                        "train_noise_std": cell.train_noise_std,
                        "eval_noise_std": cell.eval_noise_std,
                        "displayed_validity": float(validity),
                        "validity_scope": "ood_forced_invalid_probe" if validity == 1.0 else "in_distribution",
                        "magnitude_degrees": float(magnitude),
                        "condition": condition,
                    }
                    rows.append({
                        **base, "aggregation": "spatially_marginal",
                        "cue_index": "", "change_index": "", "trials": int(trials),
                        "response_count": int(counts[cell_index, validity_index, magnitude_index, condition_index]),
                        "response_rate": float(rates[cell_index, validity_index, magnitude_index, condition_index]),
                        "conditional_mean_rt_frame": float(mean_rt[cell_index, validity_index, magnitude_index, condition_index]),
                        "early_response_count": int(early_counts[cell_index, validity_index, magnitude_index, condition_index]),
                        "false_alarm_count": int(false_alarm_count[cell_index, validity_index]),
                        "false_alarm_trials": int(trials),
                        "false_alarm_rate": float(false_alarm_rate[cell_index, validity_index]),
                        "dprime": float(dprime[cell_index, validity_index, magnitude_index, condition_index]),
                        "criterion": float(criterion[cell_index, validity_index, magnitude_index, condition_index]),
                    })
                    cues = cue_indices[validity_index, magnitude_index, condition_index]
                    changes = change_indices[validity_index, magnitude_index, condition_index]
                    for cue_index, change_index, _count in allocate_spatial_strata(trials, condition):
                        mask = (cues == cue_index) & (changes == change_index)
                        fa_mask = nochange_cue[validity_index] == cue_index
                        local_stats = qualifying_stats(
                            presses[cell_index, validity_index, magnitude_index, condition_index, mask],
                            nochange=False,
                        )
                        fa_stats = qualifying_stats(nochange_press[cell_index, validity_index, fa_mask], nochange=True)
                        local_dprime, local_criterion = hautus_sdt(
                            int(local_stats["response_count"]), int(fa_stats["response_count"]),
                            int(mask.sum()), int(fa_mask.sum()),
                        )
                        rows.append({
                            **base, "aggregation": "spatial_stratum",
                            "cue_index": cue_index, "change_index": change_index,
                            "trials": int(mask.sum()),
                            "response_count": int(local_stats["response_count"]),
                            "response_rate": float(local_stats["response_rate"]),
                            "conditional_mean_rt_frame": float(local_stats["mean_rt"]),
                            "early_response_count": int(local_stats["early_response_count"]),
                            "false_alarm_count": int(fa_stats["response_count"]),
                            "false_alarm_trials": int(fa_mask.sum()),
                            "false_alarm_rate": float(fa_stats["response_rate"]),
                            "dprime": float(local_dprime), "criterion": float(local_criterion),
                        })
    payload = {
        "cell_labels": np.asarray([cell.label for cell in cells]),
        "validities": VALIDITIES,
        "magnitudes": MAGNITUDES,
        "conditions": np.asarray(CONDITIONS),
        "response_count": counts, "response_rate": rates, "mean_rt": mean_rt,
        "press_histogram": histograms, "early_response_count": early_counts,
        "false_alarm_count": false_alarm_count, "false_alarm_rate": false_alarm_rate,
        "false_alarm_histogram": false_alarm_histogram,
        "dprime": dprime, "criterion": criterion,
        "press": presses, "nochange_press": nochange_press,
        "cue_index": cue_indices, "change_index": change_indices,
        "nochange_cue_index": nochange_cue,
    }
    return payload, rows, summaries


def _mean_sem(values: np.ndarray, axis: int = 0) -> tuple[np.ndarray, np.ndarray]:
    array = np.asarray(values, dtype=np.float64)
    mean = array.mean(axis=axis)
    if array.shape[axis] <= 1:
        sem = np.full_like(mean, np.nan, dtype=np.float64)
    else:
        sem = array.std(axis=axis, ddof=1) / math.sqrt(array.shape[axis])
    return mean, sem


def _qualifying_binary(press: np.ndarray, *, nochange: bool) -> np.ndarray:
    values = np.asarray(press, dtype=np.int64)
    return (values >= 0) if nochange else np.isin(values, QUALIFYING_FRAMES)


def _paired_stratified_resample_indices(
    cue: np.ndarray,
    change: np.ndarray,
    condition: str,
    rng: np.random.Generator,
) -> np.ndarray:
    selected: list[np.ndarray] = []
    for cue_index, change_index, _count in allocate_spatial_strata(int(cue.size), condition):
        indices = np.flatnonzero((cue == cue_index) & (change == change_index))
        if indices.size == 0:
            raise RuntimeError("empty spatial stratum during bootstrap")
        selected.append(rng.choice(indices, size=indices.size, replace=True))
    return np.concatenate(selected)


def _slope_over_registered_validities(values: Sequence[float]) -> float:
    array = np.asarray(values, dtype=np.float64)
    x = VALIDITIES[:3]
    y = array[:3]
    if not np.isfinite(y).all():
        return float("nan")
    return float(np.polyfit(x, y, 1)[0])


def bootstrap_primary_contrasts(
    psych_payload: Mapping[str, Any],
    cells: Sequence[EvaluationCell],
    focal_magnitude: float,
    replicates: int,
) -> list[dict[str, Any]]:
    """Deterministic paired bootstrap over spatial strata and held-out trials.

    The same resampled trial indices are used for every model cell, preserving
    CRN pairing.  Intervals quantify finite held-out-trial/noise-draw uncertainty
    conditional on seed 0; they are not between-training-seed intervals.
    """
    if replicates <= 0:
        raise ValueError("bootstrap replicates must be positive")
    press = np.asarray(psych_payload["press"], dtype=np.int64)
    nochange = np.asarray(psych_payload["nochange_press"], dtype=np.int64)
    cues = np.asarray(psych_payload["cue_index"], dtype=np.int64)
    changes = np.asarray(psych_payload["change_index"], dtype=np.int64)
    nochange_cues = np.asarray(psych_payload["nochange_cue_index"], dtype=np.int64)
    focal_index = int(np.argmin(np.abs(MAGNITUDES - float(focal_magnitude))))
    n_cells = len(cells)
    estimands = (
        "threshold_cost_vs_validity_slope",
        "focal_response_cue_effect_vs_validity_slope",
        "focal_dprime_cue_effect_vs_validity_slope",
    )
    cell_draws = {name: np.full((replicates, n_cells), np.nan) for name in estimands}
    rng = np.random.default_rng(stable_seed("bootstrap_primary", bits=63))
    for replicate in range(replicates):
        metric_by_cell = {
            name: np.full((n_cells, len(VALIDITIES)), np.nan) for name in estimands
        }
        for validity_index in range(len(VALIDITIES)):
            nochange_index = _paired_stratified_resample_indices(
                nochange_cues[validity_index], nochange_cues[validity_index], "nochange", rng
            )
            fa_binary = _qualifying_binary(nochange[:, validity_index, nochange_index], nochange=True)
            valid_indices: dict[int, np.ndarray] = {}
            invalid_indices: dict[int, np.ndarray] = {}
            for magnitude_index in range(len(MAGNITUDES)):
                valid_indices[magnitude_index] = _paired_stratified_resample_indices(
                    cues[validity_index, magnitude_index, 0],
                    changes[validity_index, magnitude_index, 0], "valid", rng,
                )
                invalid_indices[magnitude_index] = _paired_stratified_resample_indices(
                    cues[validity_index, magnitude_index, 1],
                    changes[validity_index, magnitude_index, 1], "invalid", rng,
                )
            for cell_index in range(n_cells):
                valid_curve: list[float] = []
                invalid_curve: list[float] = []
                for magnitude_index in range(len(MAGNITUDES)):
                    valid_curve.append(float(_qualifying_binary(
                        press[cell_index, validity_index, magnitude_index, 0, valid_indices[magnitude_index]],
                        nochange=False,
                    ).mean()))
                    invalid_curve.append(float(_qualifying_binary(
                        press[cell_index, validity_index, magnitude_index, 1, invalid_indices[magnitude_index]],
                        nochange=False,
                    ).mean()))
                valid_threshold = threshold50(MAGNITUDES, np.asarray(valid_curve))
                invalid_threshold = threshold50(MAGNITUDES, np.asarray(invalid_curve))
                metric_by_cell["threshold_cost_vs_validity_slope"][cell_index, validity_index] = (
                    invalid_threshold - valid_threshold
                )
                valid_hits = _qualifying_binary(
                    press[cell_index, validity_index, focal_index, 0, valid_indices[focal_index]],
                    nochange=False,
                )
                invalid_hits = _qualifying_binary(
                    press[cell_index, validity_index, focal_index, 1, invalid_indices[focal_index]],
                    nochange=False,
                )
                metric_by_cell["focal_response_cue_effect_vs_validity_slope"][cell_index, validity_index] = (
                    float(valid_hits.mean() - invalid_hits.mean())
                )
                fa = fa_binary[cell_index]
                valid_dp, _ = hautus_sdt(int(valid_hits.sum()), int(fa.sum()), valid_hits.size, fa.size)
                invalid_dp, _ = hautus_sdt(int(invalid_hits.sum()), int(fa.sum()), invalid_hits.size, fa.size)
                metric_by_cell["focal_dprime_cue_effect_vs_validity_slope"][cell_index, validity_index] = (
                    valid_dp - invalid_dp
                )
        for estimand in estimands:
            for cell_index in range(n_cells):
                cell_draws[estimand][replicate, cell_index] = _slope_over_registered_validities(
                    metric_by_cell[estimand][cell_index]
                )

    comparisons = {
        "ecological_total_train0p5_eval0p5_minus_train0_eval0": (3, 0),
        "learned_adaptation_train0p5_minus_train0_at_eval0p5": (3, 1),
        "acute_interference_train0_eval0p5_minus_eval0": (1, 0),
        "acute_interference_train0p5_eval0p5_minus_eval0": (3, 2),
    }
    rows: list[dict[str, Any]] = []
    for estimand in estimands:
        for comparison, (left, right) in comparisons.items():
            values = cell_draws[estimand][:, left] - cell_draws[estimand][:, right]
            finite = values[np.isfinite(values)]
            estimate = float(np.nanmean(values)) if finite.size else float("nan")
            low, high = (
                np.percentile(finite, [2.5, 97.5]) if finite.size else (float("nan"), float("nan"))
            )
            rows.append({
                "estimand": estimand,
                "comparison": comparison,
                "bootstrap_mean": estimate,
                "ci_2p5": float(low), "ci_97p5": float(high),
                "finite_replicates": int(finite.size), "requested_replicates": int(replicates),
                "interval_scope": "seed0_conditional_paired_trial_and_single_mnemonic_draw_uncertainty",
                "validities_used_for_slope": "0.25,0.5,0.75",
                "validity1_handling": "excluded_ood_expectancy_violation_probe",
            })
    return rows


def run_attention(
    core: Any,
    models: Mapping[str, Any],
    cells: Sequence[EvaluationCell],
    registry: dict[str, dict[str, Any]],
    trials: int,
    focal_magnitude: float,
) -> tuple[
    dict[str, Any], list[dict[str, Any]], list[dict[str, Any]],
    list[dict[str, Any]], list[dict[str, Any]],
]:
    visual = np.zeros((len(cells), 2, trials, T, N_PATCHES, N_PATCHES), dtype=np.float32)
    memory = np.zeros_like(visual)
    presses = np.zeros((len(cells), 2, trials), dtype=np.int64)
    action1_probability = np.zeros((len(cells), 2, trials, T), dtype=np.float32)
    cue_indices = np.zeros((2, trials), dtype=np.int64)
    change_indices = np.zeros_like(cue_indices)
    schedule_hashes = np.empty((len(cells), 2), dtype="U64")

    for condition_index, condition in enumerate(CONDITIONS):
        rollouts = counterbalanced_rollouts(
            core, registry, models, cells,
            namespace=FROZEN_NAMESPACE, assay="attention", condition=condition,
            total_trials=trials, displayed_validity=PRIMARY_VALIDITY,
            magnitude=focal_magnitude, return_attention=True,
        )
        reference = rollouts[cells[0].label]
        cue_indices[condition_index] = reference["cue_index"]
        change_indices[condition_index] = reference["change_index"]
        for cell_index, cell in enumerate(cells):
            result = rollouts[cell.label]
            visual_map, memory_map = split_source_attention(result["attention"])
            visual[cell_index, condition_index] = visual_map
            memory[cell_index, condition_index] = memory_map
            presses[cell_index, condition_index] = result["press"]
            action1_probability[cell_index, condition_index] = result["action1_probability"]
            joined = "|".join(result["memory_noise_schedule_sha256_by_stratum"])
            schedule_hashes[cell_index, condition_index] = sha256_bytes(joined.encode("ascii"))

    metric_rows: list[dict[str, Any]] = []
    patch_rows: list[dict[str, Any]] = []
    matrix_rows: list[dict[str, Any]] = []
    reorientation_rows: list[dict[str, Any]] = []
    for cell_index, cell in enumerate(cells):
        for condition_index, condition in enumerate(CONDITIONS):
            cue_vector = cue_indices[condition_index]
            target_vector = change_indices[condition_index]
            spatial_masks: list[tuple[str, int | str, int | str, np.ndarray]] = [
                ("spatially_marginal", "", "", np.ones(trials, dtype=bool))
            ]
            for cue_index, change_index, _count in allocate_spatial_strata(trials, condition):
                spatial_masks.append((
                    "spatial_stratum", cue_index, change_index,
                    (cue_vector == cue_index) & (target_vector == change_index),
                ))
            for source_name, source_array in (("visual", visual), ("memory", memory)):
                maps = source_array[cell_index, condition_index]
                metrics = source_attention_metrics_by_trial(maps, target_vector, cue_vector)
                for aggregation, cue_value, target_value, mask in spatial_masks:
                    pre_reorientation = float(metrics["target_minus_cue"][mask, 1:5].mean())
                    post_reorientation = float(metrics["target_minus_cue"][mask, 5:7].mean())
                    reorientation_rows.append({
                        "cell": cell.label, "train_noise_std": cell.train_noise_std,
                        "eval_noise_std": cell.eval_noise_std, "condition": condition,
                        "source": source_name, "aggregation": aggregation,
                        "cue_index": cue_value, "change_index": target_value,
                        "trials": int(mask.sum()),
                        "prechange_t1_t4_target_minus_cue": pre_reorientation,
                        "postchange_t5_t6_target_minus_cue": post_reorientation,
                        "cue_to_target_reorientation_post_minus_pre": post_reorientation - pre_reorientation,
                        "interpretation": (
                            "postchange target localization and reorientation" if condition == "invalid"
                            else "valid cue and target coincide; reorientation contrast is algebraically zero"
                        ),
                    })
                    for frame in range(T):
                        event_phase = (
                            "baseline" if frame == 0 else
                            "prechange_cue_aligned" if frame <= 4 else
                            "postchange_target_aligned"
                        )
                        row: dict[str, Any] = {
                            "cell": cell.label, "train_noise_std": cell.train_noise_std,
                            "eval_noise_std": cell.eval_noise_std, "condition": condition,
                            "displayed_validity": PRIMARY_VALIDITY,
                            "source": source_name, "aggregation": aggregation,
                            "cue_index": cue_value, "change_index": target_value,
                            "frame": frame, "event_phase": event_phase, "trials": int(mask.sum()),
                            "target_localization_interpretable": bool(frame >= 5),
                        }
                        for key in (
                            "source_share", "cue_raw", "cue_conditional", "target_raw",
                            "target_conditional", "distractor_conditional_mean",
                            "target_selectivity", "target_minus_cue", "max_raw_patch",
                            "max_conditional_patch", "normalized_max_conditional",
                            "normalized_entropy", "effective_locations",
                        ):
                            mean, sem = _mean_sem(metrics[key][mask, frame])
                            row[f"{key}_mean"] = float(mean)
                            row[f"{key}_sem"] = float(sem)
                        metric_rows.append(row)
                        for patch_index in range(N_PATCHES):
                            raw_mean, raw_sem = _mean_sem(metrics["patch_score"][mask, frame, patch_index])
                            conditional_mean, conditional_sem = _mean_sem(
                                metrics["conditional_patch_score"][mask, frame, patch_index]
                            )
                            patch_rows.append({
                                "cell": cell.label, "train_noise_std": cell.train_noise_std,
                                "eval_noise_std": cell.eval_noise_std, "condition": condition,
                                "displayed_validity": PRIMARY_VALIDITY, "source": source_name,
                                "aggregation": aggregation, "cue_index": cue_value,
                                "change_index": target_value, "frame": frame,
                                "event_phase": event_phase, "trials": int(mask.sum()),
                                "patch_index": patch_index, "physical_region": patch_index,
                                "column_averaged_patch_score_mean": float(raw_mean),
                                "column_averaged_patch_score_sem": float(raw_sem),
                                "conditional_patch_score_mean": float(conditional_mean),
                                "conditional_patch_score_sem": float(conditional_sem),
                                "region_max_patch_score_mean": float(raw_mean),
                                "region_max_patch_score_sem": float(raw_sem),
                                "note": "native 2x2: one patch per region, so region max equals patch score",
                            })
                        for query_index in range(N_PATCHES):
                            for key_index in range(N_PATCHES):
                                matrix_mean, matrix_sem = _mean_sem(
                                    maps[mask, frame, query_index, key_index]
                                )
                                matrix_rows.append({
                                    "cell": cell.label, "train_noise_std": cell.train_noise_std,
                                    "eval_noise_std": cell.eval_noise_std, "condition": condition,
                                    "displayed_validity": PRIMARY_VALIDITY, "source": source_name,
                                    "aggregation": aggregation, "cue_index": cue_value,
                                    "change_index": target_value, "frame": frame,
                                    "event_phase": event_phase, "trials": int(mask.sum()),
                                    "query_patch": query_index, "key_patch": key_index,
                                    "attention_weight_mean": float(matrix_mean),
                                    "attention_weight_sem": float(matrix_sem),
                                })
    payload = {
        "cell_labels": np.asarray([cell.label for cell in cells]),
        "conditions": np.asarray(CONDITIONS),
        "sources": np.asarray(SOURCES),
        "focal_magnitude_degrees": np.asarray(focal_magnitude),
        "displayed_validity": np.asarray(PRIMARY_VALIDITY),
        "visual_attention_full_4x4": visual,
        "memory_attention_full_4x4": memory,
        "press": presses,
        "action1_probability": action1_probability,
        "cue_index": cue_indices,
        "change_index": change_indices,
        "memory_noise_schedule_sha256": schedule_hashes,
    }
    return payload, metric_rows, patch_rows, matrix_rows, reorientation_rows


def run_interventions(
    core: Any,
    models: Mapping[str, Any],
    cells: Sequence[EvaluationCell],
    registry: dict[str, dict[str, Any]],
    trials: int,
    focal_magnitude: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    condition_names = ("valid", "invalid", "nochange")
    intervention_specs: list[tuple[str, str, str, float, float]] = [
        ("natural", "natural", "natural", -1.0, 0.0)
    ]
    for role in INTERVENTION_ROLES:
        for source in INTERVENTION_SOURCES:
            for dose in INTERVENTION_DOSES:
                bias = CLAMP_LOGIT_BIAS * (2.0 * float(dose) - 1.0)
                label = f"{role}|{source}|alpha={float(dose):g}"
                intervention_specs.append((label, role, source, float(dose), bias))
    labels = tuple(item[0] for item in intervention_specs)
    shape = (len(cells), len(intervention_specs), len(condition_names))
    counts = np.zeros(shape, dtype=np.int64)
    rates = np.zeros(shape, dtype=np.float64)
    mean_rt = np.full(shape, np.nan)
    histograms = np.zeros(shape + (8,), dtype=np.int64)
    early = np.zeros(shape, dtype=np.int64)
    presses = np.zeros(shape + (trials,), dtype=np.int64)
    action1_probability = np.zeros(shape + (trials, T), dtype=np.float32)
    schedule_hashes = np.empty(shape, dtype="U64")
    cue_indices = np.zeros((len(condition_names), trials), dtype=np.int64)
    change_indices = np.zeros_like(cue_indices)

    for mode_index, (_label, role, source, dose, _bias) in enumerate(intervention_specs):
        for condition_index, condition in enumerate(condition_names):
            rollouts = counterbalanced_rollouts(
                core, registry, models, cells,
                namespace=FROZEN_NAMESPACE, assay="intervention",
                condition=condition, total_trials=trials,
                displayed_validity=PRIMARY_VALIDITY,
                magnitude=0.0 if condition == "nochange" else focal_magnitude,
                intervention_role=role,
                intervention_source=source,
                intervention_dose=0.5 if role == "natural" else dose,
            )
            reference = rollouts[cells[0].label]
            cue_indices[condition_index] = reference["cue_index"]
            change_indices[condition_index] = reference["change_index"]
            for cell_index, cell in enumerate(cells):
                result = rollouts[cell.label]
                stats = qualifying_stats(result["press"], nochange=condition == "nochange")
                counts[cell_index, mode_index, condition_index] = stats["response_count"]
                rates[cell_index, mode_index, condition_index] = stats["response_rate"]
                mean_rt[cell_index, mode_index, condition_index] = stats["mean_rt"]
                histograms[cell_index, mode_index, condition_index] = stats["press_histogram"]
                early[cell_index, mode_index, condition_index] = stats["early_response_count"]
                presses[cell_index, mode_index, condition_index] = result["press"]
                action1_probability[cell_index, mode_index, condition_index] = result["action1_probability"]
                joined = "|".join(result["memory_noise_schedule_sha256_by_stratum"])
                schedule_hashes[cell_index, mode_index, condition_index] = sha256_bytes(joined.encode("ascii"))

    dprime = np.zeros((len(cells), len(intervention_specs), 2), dtype=np.float64)
    criterion = np.zeros_like(dprime)
    rows: list[dict[str, Any]] = []
    for cell_index, cell in enumerate(cells):
        for mode_index, (label, role, source, dose, bias) in enumerate(intervention_specs):
            fa_count = int(counts[cell_index, mode_index, 2])
            for condition_index in range(2):
                dprime[cell_index, mode_index, condition_index], criterion[
                    cell_index, mode_index, condition_index
                ] = hautus_sdt(
                    int(counts[cell_index, mode_index, condition_index]),
                    fa_count,
                    trials,
                    trials,
                )
            for condition_index, condition in enumerate(condition_names):
                base = {
                    "cell": cell.label, "train_noise_std": cell.train_noise_std,
                    "eval_noise_std": cell.eval_noise_std,
                    "displayed_validity": PRIMARY_VALIDITY,
                    "focal_magnitude_degrees": focal_magnitude,
                    "intervention": label, "role": role, "source": source,
                    "dose_alpha": "" if role == "natural" else dose,
                    "clamp_from_frame": CLAMP_FROM,
                    "clamp_logit_bias": bias,
                    "condition": condition,
                }
                rows.append({
                    **base, "aggregation": "spatially_marginal",
                    "cue_index": "", "change_index": "", "trials": trials,
                    "response_count": int(counts[cell_index, mode_index, condition_index]),
                    "response_rate": float(rates[cell_index, mode_index, condition_index]),
                    "conditional_mean_rt_frame": float(mean_rt[cell_index, mode_index, condition_index]),
                    "early_response_count": int(early[cell_index, mode_index, condition_index]),
                    "false_alarm_rate": float(rates[cell_index, mode_index, 2]),
                    "dprime": float(dprime[cell_index, mode_index, condition_index]) if condition_index < 2 else "",
                    "criterion": float(criterion[cell_index, mode_index, condition_index]) if condition_index < 2 else "",
                    "memory_noise_schedule_sha256": schedule_hashes[cell_index, mode_index, condition_index],
                })
                cues = cue_indices[condition_index]
                changes = change_indices[condition_index]
                for cue_index, change_index, _count in allocate_spatial_strata(trials, condition):
                    mask = (cues == cue_index) & (changes == change_index)
                    local = qualifying_stats(
                        presses[cell_index, mode_index, condition_index, mask],
                        nochange=condition == "nochange",
                    )
                    if condition != "nochange":
                        fa_mask = cue_indices[2] == cue_index
                        fa_local = qualifying_stats(
                            presses[cell_index, mode_index, 2, fa_mask], nochange=True
                        )
                        local_dp, local_c = hautus_sdt(
                            int(local["response_count"]), int(fa_local["response_count"]),
                            int(mask.sum()), int(fa_mask.sum()),
                        )
                    else:
                        fa_local, local_dp, local_c = local, float("nan"), float("nan")
                    rows.append({
                        **base, "aggregation": "spatial_stratum",
                        "cue_index": cue_index, "change_index": change_index,
                        "trials": int(mask.sum()),
                        "response_count": int(local["response_count"]),
                        "response_rate": float(local["response_rate"]),
                        "conditional_mean_rt_frame": float(local["mean_rt"]),
                        "early_response_count": int(local["early_response_count"]),
                        "false_alarm_rate": float(fa_local["response_rate"]),
                        "dprime": float(local_dp) if condition != "nochange" else "",
                        "criterion": float(local_c) if condition != "nochange" else "",
                        "memory_noise_schedule_sha256": schedule_hashes[cell_index, mode_index, condition_index],
                    })
    payload = {
        "cell_labels": np.asarray([cell.label for cell in cells]),
        "intervention_labels": np.asarray(labels),
        "intervention_roles": np.asarray([item[1] for item in intervention_specs]),
        "intervention_sources": np.asarray([item[2] for item in intervention_specs]),
        "intervention_doses": np.asarray([item[3] for item in intervention_specs]),
        "intervention_logit_bias": np.asarray([item[4] for item in intervention_specs]),
        "conditions": np.asarray(condition_names),
        "focal_magnitude_degrees": np.asarray(focal_magnitude),
        "response_count": counts,
        "response_rate": rates,
        "mean_rt": mean_rt,
        "press_histogram": histograms,
        "early_response_count": early,
        "dprime": dprime,
        "criterion": criterion,
        "press": presses,
        "action1_probability": action1_probability,
        "cue_index": cue_indices,
        "change_index": change_indices,
        "memory_noise_schedule_sha256": schedule_hashes,
    }
    return payload, rows


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    if any(list(row) != fields for row in rows):
        raise ValueError(f"CSV rows for {path} do not share one ordered schema")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "" if isinstance(value, float) and not math.isfinite(value) else value for key, value in row.items()})


def save_npz(path: Path, payload: Mapping[str, Any], metadata: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays = {str(key): np.asarray(value) for key, value in payload.items()}
    arrays.update({f"meta_{key}": np.asarray(value) for key, value in metadata.items()})
    for key, value in arrays.items():
        if np.issubdtype(value.dtype, np.inexact) and not np.isfinite(value).all():
            # Mean RT and undefined psychometric thresholds are intentionally
            # allowed to be NaN; all other numeric arrays must be finite.
            if key not in {"mean_rt"}:
                raise ValueError(f"NPZ array {key!r} contains non-finite values")
    np.savez_compressed(path, **arrays)


def calibration_rows(payload: Mapping[str, Any], cells: Sequence[EvaluationCell]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cell_index, cell in enumerate(cells):
        for magnitude_index, magnitude in enumerate(payload["magnitudes"]):
            for condition_index, condition in enumerate(CONDITIONS):
                rows.append({
                    "cell": cell.label,
                    "train_noise_std": cell.train_noise_std,
                    "eval_noise_std": cell.eval_noise_std,
                    "magnitude_degrees": float(magnitude),
                    "condition": condition,
                    "response_count": int(payload["response_count"][cell_index, magnitude_index, condition_index]),
                    "response_rate": float(payload["response_rate"][cell_index, magnitude_index, condition_index]),
                    "conditional_mean_rt_frame": float(payload["mean_rt"][cell_index, magnitude_index, condition_index]),
                    "false_alarm_rate": float(payload["false_alarm_rate"][cell_index]),
                    "dprime": float(payload["dprime"][cell_index, magnitude_index, condition_index]),
                    "criterion": float(payload["criterion"][cell_index, magnitude_index, condition_index]),
                })
    return rows


def primary_summary(
    cells: Sequence[EvaluationCell],
    psych_payload: Mapping[str, Any],
    psych_summaries: Sequence[Mapping[str, Any]],
    attention_payload: Mapping[str, Any],
    intervention_payload: Mapping[str, Any],
    calibration_lock: Mapping[str, Any],
    bootstrap_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    focal = float(calibration_lock["focal_selection"]["magnitude_degrees"])
    focal_index = int(np.where(MAGNITUDES == focal)[0][0])
    summary_lookup = {
        (str(item["cell"]), float(item["displayed_validity"])): item
        for item in psych_summaries
    }
    intervention_labels = [str(item) for item in intervention_payload["intervention_labels"]]
    natural_index = intervention_labels.index("natural")
    true_suppress_index = intervention_labels.index("true_change|both|alpha=0")
    true_boost_index = intervention_labels.index("true_change|both|alpha=1")
    wrong_suppress_index = intervention_labels.index("cued_wrong|both|alpha=0")
    neutral_suppress_index = intervention_labels.index("neutral_control|both|alpha=0")
    estimates: list[dict[str, Any]] = []
    for cell_index, cell in enumerate(cells):
        validity_estimates: list[dict[str, Any]] = []
        for validity_index, validity in enumerate(VALIDITIES):
            item = summary_lookup[(cell.label, float(validity))]
            validity_estimates.append({
                **dict(item),
                "focal_valid_minus_invalid_response_rate": float(
                    psych_payload["response_rate"][cell_index, validity_index, focal_index, 0]
                    - psych_payload["response_rate"][cell_index, validity_index, focal_index, 1]
                ),
                "focal_valid_minus_invalid_dprime": float(
                    psych_payload["dprime"][cell_index, validity_index, focal_index, 0]
                    - psych_payload["dprime"][cell_index, validity_index, focal_index, 1]
                ),
                "focal_invalid_minus_valid_criterion": float(
                    psych_payload["criterion"][cell_index, validity_index, focal_index, 1]
                    - psych_payload["criterion"][cell_index, validity_index, focal_index, 0]
                ),
                "focal_invalid_minus_valid_rt_frames": float(
                    psych_payload["mean_rt"][cell_index, validity_index, focal_index, 1]
                    - psych_payload["mean_rt"][cell_index, validity_index, focal_index, 0]
                ),
            })
        slopes = {
            "threshold_cost_vs_validity_slope": _slope_over_registered_validities([
                item["cueing_threshold_cost_invalid_minus_valid_degrees"]
                for item in validity_estimates
            ]),
            "focal_response_cue_effect_vs_validity_slope": _slope_over_registered_validities([
                item["focal_valid_minus_invalid_response_rate"] for item in validity_estimates
            ]),
            "focal_dprime_cue_effect_vs_validity_slope": _slope_over_registered_validities([
                item["focal_valid_minus_invalid_dprime"] for item in validity_estimates
            ]),
        }
        cue_vector = attention_payload["cue_index"][1]
        target_vector = attention_payload["change_index"][1]
        source_attention: dict[str, Any] = {}
        for source_name, array_name in (
            ("visual", "visual_attention_full_4x4"),
            ("memory", "memory_attention_full_4x4"),
        ):
            metrics = source_attention_metrics_by_trial(
                attention_payload[array_name][cell_index, 1], target_vector, cue_vector
            )
            pre = float(metrics["target_minus_cue"][:, 1:5].mean())
            post = float(metrics["target_minus_cue"][:, 5:7].mean())
            source_attention[source_name] = {
                "prechange_t1_t4_cue_conditional_mass": float(
                    metrics["cue_conditional"][:, 1:5].mean()
                ),
                "postchange_t5_t6_target_conditional_mass": float(
                    metrics["target_conditional"][:, 5:7].mean()
                ),
                "postchange_t5_t6_target_minus_cued_wrong": post,
                "cue_to_target_reorientation_post_minus_pre": post - pre,
                "prechange_target_localization_claim_allowed": False,
            }
        invalid_index = CONDITIONS.index("invalid")
        natural_dprime = float(intervention_payload["dprime"][cell_index, natural_index, invalid_index])
        true_suppress = float(intervention_payload["dprime"][cell_index, true_suppress_index, invalid_index])
        true_boost = float(intervention_payload["dprime"][cell_index, true_boost_index, invalid_index])
        wrong_suppress = float(intervention_payload["dprime"][cell_index, wrong_suppress_index, invalid_index])
        neutral_suppress = float(intervention_payload["dprime"][cell_index, neutral_suppress_index, invalid_index])
        estimates.append({
            "cell": cell.label,
            "train_noise_std": cell.train_noise_std,
            "eval_noise_std": cell.eval_noise_std,
            "focal_magnitude_degrees": focal,
            "validity_estimates": validity_estimates,
            "primary_validity_slopes_in_distribution_0p25_to_0p75": slopes,
            "validity1_forced_invalid": validity_estimates[3],
            "validity1_scope": "OOD expectancy-violation probe; excluded from primary slopes",
            "source_separated_invalid_attention": source_attention,
            "intervention_invalid_dprime": {
                "natural": natural_dprime,
                "true_both_alpha0_suppress": true_suppress,
                "true_both_alpha1_boost": true_boost,
                "cued_wrong_both_alpha0_suppress": wrong_suppress,
                "neutral_both_alpha0_suppress": neutral_suppress,
                "true_boost_minus_suppress": true_boost - true_suppress,
                "true_suppression_loss_minus_wrong": (natural_dprime - true_suppress) - (natural_dprime - wrong_suppress),
                "true_suppression_loss_minus_neutral": (natural_dprime - true_suppress) - (natural_dprime - neutral_suppress),
            },
        })
    by_label = {item["cell"]: item for item in estimates}
    def delta(left: str, right: str, key: str) -> float:
        return float(
            by_label[left]["primary_validity_slopes_in_distribution_0p25_to_0p75"][key]
            - by_label[right]["primary_validity_slopes_in_distribution_0p25_to_0p75"][key]
        )
    ecological = {
        "comparison": "train0p5_eval0p5 minus train0_eval0",
        **{key: delta("train0p5_eval0p5", "train0_eval0", key) for key in (
            "threshold_cost_vs_validity_slope",
            "focal_response_cue_effect_vs_validity_slope",
            "focal_dprime_cue_effect_vs_validity_slope",
        )},
    }
    adaptation = {
        "comparison": "train0p5_eval0p5 minus train0_eval0p5",
        **{key: delta("train0p5_eval0p5", "train0_eval0p5", key) for key in (
            "threshold_cost_vs_validity_slope",
            "focal_response_cue_effect_vs_validity_slope",
            "focal_dprime_cue_effect_vs_validity_slope",
        )},
    }
    acute: list[dict[str, Any]] = []
    for train_label in ("train0", "train0p5"):
        noisy = by_label[f"{train_label}_eval0p5"]
        clean = by_label[f"{train_label}_eval0"]
        acute.append({
            "training_condition": train_label,
            "comparison": "eval0p5 minus eval0",
            **{
                key: float(
                    noisy["primary_validity_slopes_in_distribution_0p25_to_0p75"][key]
                    - clean["primary_validity_slopes_in_distribution_0p25_to_0p75"][key]
                )
                for key in (
                    "threshold_cost_vs_validity_slope",
                    "focal_response_cue_effect_vs_validity_slope",
                    "focal_dprime_cue_effect_vs_validity_slope",
                )
            },
        })
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "completed_heldout_seed0_pilot",
        "cells": estimates,
        "planned_factorial_contrasts": {
            "ecological_total_effect": ecological,
            "learned_adaptation_at_common_noisy_evaluation": adaptation,
            "acute_interference_within_checkpoint": acute,
        },
        "bootstrap_intervals": [dict(item) for item in bootstrap_rows],
        "attention_timing_rule": (
            "t1-t4 quantify cue-aligned allocation; t5-t6 quantify true-change allocation. "
            "Prechange target selectivity is not localization evidence."
        ),
        "interpretation_gates": {
            "all_cells_competent": calibration_lock["all_cells_competent"],
            "common_nonsaturation_pass": calibration_lock["focal_selection"]["common_nonsaturation_pass"],
            "terminal_training_integrity_required": True,
            "single_seed_pilot_only": True,
        },
        "claim_boundary": (
            "These are disjoint held-out seed-0 pilot estimates. Attention weights are descriptive; "
            "only spatially specific interventions support model-causal routing claims. One seed cannot "
            "establish a population-level training-noise effect or biological mechanism."
        ),
    }


def _save_figure_pair(figure: Any, root: Path, stem: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    png = root / f"{stem}.png"
    pdf = root / f"{stem}.pdf"
    figure.savefig(
        png, dpi=180, bbox_inches="tight",
        metadata={"Software": "evaluate_paired_v1.py"},
    )
    figure.savefig(
        pdf, bbox_inches="tight",
        metadata={"Creator": "evaluate_paired_v1.py", "CreationDate": None, "ModDate": None},
    )
    if png.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"invalid PNG figure {png}")
    if pdf.read_bytes()[:5] != b"%PDF-":
        raise RuntimeError(f"invalid PDF figure {pdf}")


def create_figures(
    root: Path,
    psych_payload: Mapping[str, Any],
    attention_payload: Mapping[str, Any],
    intervention_payload: Mapping[str, Any],
    cells: Sequence[EvaluationCell],
    focal_magnitude: float,
) -> None:
    """Create the deterministic, source-separated figure inventory."""
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8,
        "legend.fontsize": 6, "figure.dpi": 100, "savefig.facecolor": "white",
    })
    colors = ("#333333", "#377eb8", "#e41a1c", "#984ea3")
    linestyles = ("-", "--")
    validity_index = PRIMARY_VALIDITY_INDEX

    figure, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
    metric_specs = (
        ("response_rate", "Response probability", "Probability"),
        ("mean_rt", "Conditional response frame", "Frame"),
        ("dprime", "Sensitivity", "d prime"),
        ("criterion", "Criterion", "criterion"),
    )
    for axis, (array_name, title, ylabel) in zip(axes.ravel(), metric_specs, strict=True):
        values = psych_payload[array_name]
        for cell_index, cell in enumerate(cells):
            for condition_index, condition in enumerate(CONDITIONS):
                axis.plot(
                    MAGNITUDES,
                    values[cell_index, validity_index, :, condition_index],
                    color=colors[cell_index], linestyle=linestyles[condition_index],
                    marker="o", markersize=2.5,
                    label=f"{cell.label} {condition}",
                )
        axis.axvline(float(focal_magnitude), color="#999999", lw=.7, alpha=.6)
        axis.set(title=f"{title}; displayed validity=.75", xlabel="Change magnitude (deg)", ylabel=ylabel)
        axis.grid(alpha=.2)
    axes[0, 0].legend(ncol=2, loc="best")
    figure.suptitle("Held-out sampled-policy psychometrics, RT, and SDT (seed-0 pilot)")
    _save_figure_pair(figure, root, FIGURE_STEMS["psychometric_sdt"])
    plt.close(figure)

    for source_name, payload_name, figure_key in (
        ("visual", "visual_attention_full_4x4", "visual_maps"),
        ("memory", "memory_attention_full_4x4", "memory_maps"),
    ):
        arrays = np.asarray(attention_payload[payload_name])
        frames = (4, 6)
        figure, axes = plt.subplots(len(cells), len(CONDITIONS) * len(frames), figsize=(10, 9))
        patch_scores = arrays.mean(axis=-2)
        vmax = float(np.percentile(patch_scores, 99.5))
        vmax = max(vmax, 1e-6)
        image = None
        for cell_index, cell in enumerate(cells):
            column = 0
            for condition_index, condition in enumerate(CONDITIONS):
                for frame in frames:
                    axis = axes[cell_index, column]
                    grid = patch_scores[cell_index, condition_index, :, frame].mean(axis=0).reshape(2, 2)
                    image = axis.imshow(grid, vmin=0.0, vmax=vmax, cmap="magma")
                    for row in range(2):
                        for col in range(2):
                            axis.text(col, row, f"{grid[row, col]:.3f}", ha="center", va="center", color="white")
                    axis.set_xticks([]); axis.set_yticks([])
                    axis.set_title(f"{condition}, t{frame}")
                    if column == 0:
                        axis.set_ylabel(cell.label)
                    column += 1
        if image is not None:
            figure.colorbar(image, ax=axes.ravel().tolist(), shrink=.65, label="column mean raw mass")
        figure.suptitle(
            f"{source_name.capitalize()}-key 2x2 column-score maps; spatially counterbalanced marginal\n"
            "t4 is cue-aligned prechange; t6 is target-aligned postchange"
        )
        figure.subplots_adjust(top=.90, right=.88, hspace=.35, wspace=.25)
        _save_figure_pair(figure, root, FIGURE_STEMS[figure_key])
        plt.close(figure)

    figure, axes = plt.subplots(2, 3, figsize=(14, 7), constrained_layout=True)
    cue = attention_payload["cue_index"][1]
    target = attention_payload["change_index"][1]
    for source_index, (source_name, payload_name) in enumerate((
        ("visual", "visual_attention_full_4x4"),
        ("memory", "memory_attention_full_4x4"),
    )):
        for cell_index, cell in enumerate(cells):
            metrics = source_attention_metrics_by_trial(
                attention_payload[payload_name][cell_index, 1], target, cue
            )
            axes[source_index, 0].plot(
                range(T), metrics["source_share"].mean(axis=0),
                color=colors[cell_index], marker="o", label=cell.label,
            )
            axes[source_index, 1].plot(
                range(T), metrics["cue_conditional"].mean(axis=0),
                color=colors[cell_index], marker="o", label=cell.label,
            )
            axes[source_index, 1].plot(
                range(T), metrics["target_conditional"].mean(axis=0),
                color=colors[cell_index], linestyle="--", marker=".", alpha=.85,
            )
            axes[source_index, 2].plot(
                range(T), metrics["target_selectivity"].mean(axis=0),
                color=colors[cell_index], marker="o", label=cell.label,
            )
            axes[source_index, 2].plot(
                range(T), metrics["target_minus_cue"].mean(axis=0),
                color=colors[cell_index], linestyle="--", marker=".", alpha=.85,
            )
        for column in range(3):
            axes[source_index, column].axvline(5, color="#666666", ls=":")
            axes[source_index, column].grid(alpha=.2)
        axes[source_index, 0].set(
            title=f"{source_name}: source share", xlabel="Frame", ylabel="raw source mass"
        )
        axes[source_index, 1].set(
            title=f"{source_name}: cue solid, target dashed", xlabel="Frame", ylabel="source-conditional mass"
        )
        axes[source_index, 2].set(
            title=f"{source_name}: target selectivity solid, target-cue dashed",
            xlabel="Frame", ylabel="allocation contrast",
        )
    axes[0, 0].legend(ncol=2)
    figure.suptitle("Source-separated attention timing; target localization begins only at t5")
    _save_figure_pair(figure, root, FIGURE_STEMS["source_timecourses"])
    plt.close(figure)

    labels = [str(item) for item in intervention_payload["intervention_labels"]]
    figure, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
    for cell_index, (cell, axis) in enumerate(zip(cells, axes.ravel(), strict=True)):
        natural = float(intervention_payload["dprime"][cell_index, labels.index("natural"), 1])
        axis.axhline(natural, color="#111111", ls=":", label="natural")
        for source_index, source in enumerate(INTERVENTION_SOURCES):
            indices = [labels.index(f"true_change|{source}|alpha={float(dose):g}") for dose in INTERVENTION_DOSES]
            axis.plot(
                INTERVENTION_DOSES, intervention_payload["dprime"][cell_index, indices, 1],
                marker="o", label=f"true {source}", color=colors[source_index + 1],
            )
        for role, linestyle in (("cued_wrong", "--"), ("neutral_control", "-.")):
            indices = [labels.index(f"{role}|both|alpha={float(dose):g}") for dose in INTERVENTION_DOSES]
            axis.plot(
                INTERVENTION_DOSES, intervention_payload["dprime"][cell_index, indices, 1],
                color="#777777", linestyle=linestyle, marker=".", label=f"{role} both",
            )
        axis.set(title=cell.label, xlabel="Dose alpha (bias = 6(2alpha-1))", ylabel="Invalid d prime")
        axis.grid(alpha=.2); axis.legend(ncol=2)
    figure.suptitle("Spatially controlled causal routing dose responses at t5-t6")
    _save_figure_pair(figure, root, FIGURE_STEMS["interventions"])
    plt.close(figure)

    expected = set(expected_figure_paths(root.parent))
    if expected != set(root.glob("*")):
        raise RuntimeError("figure inventory differs from the registered deterministic inventory")


def validate_npz_roundtrip(path: Path, required: Sequence[str]) -> None:
    with np.load(path, allow_pickle=False) as payload:
        missing = set(required) - set(payload.files)
        if missing:
            raise ValueError(f"{path} lacks required arrays {sorted(missing)}")
        for name in payload.files:
            value = payload[name]
            if np.issubdtype(value.dtype, np.inexact) and name != "mean_rt" and not np.isfinite(value).all():
                raise ValueError(f"{path}:{name} contains non-finite values")


def build_manifest(root: Path, extra: Mapping[str, Any]) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name in {"MANIFEST.json", "MANIFEST.sha256"}:
            continue
        files.append({
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "immutable_hash_bound_heldout_artifacts",
        "root_name": root.name,
        "files": files,
        **jsonable(extra),
    }


def _load_models(
    core: Any,
    specs: Sequence[ModelSpec],
) -> dict[str, Any]:
    models: dict[str, Any] = {}
    for spec in specs:
        model, iteration = core.load(
            TASK,
            FEEDBACK,
            D_MEM,
            checkpoint_path=str(spec.checkpoint),
            expected_checkpoint_sha256=spec.expected_checkpoint_sha256,
            require_iteration=19_999,
            validate_metadata=True,
        )
        if iteration != 19_999 or int(model.n_tokens) != N_PATCHES:
            raise RuntimeError("loaded model violates terminal/native-grid contract")
        embedded_train_noise = float(model.encoder.lstm.memory_noise_std)
        if not math.isclose(embedded_train_noise, spec.train_noise_std, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(
                f"{spec.label} loaded memory_noise_std={embedded_train_noise}, "
                f"expected training level {spec.train_noise_std}"
            )
        models[spec.label] = model
    return models


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean-run-dir", type=Path, required=True)
    parser.add_argument("--clean-checkpoint", type=Path, required=True)
    parser.add_argument("--clean-expected-sha256", required=True)
    parser.add_argument("--clean-log", type=Path)
    parser.add_argument("--noisy-run-dir", type=Path, required=True)
    parser.add_argument("--noisy-checkpoint", type=Path, required=True)
    parser.add_argument("--noisy-expected-sha256", required=True)
    parser.add_argument("--noisy-log", type=Path)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--launcher", type=Path, default=EXPERIMENT_DIR / "launch_production_v1.sh"
    )
    parser.add_argument("--config", type=Path, default=EXPERIMENT_DIR / "config_v1.json")
    parser.add_argument(
        "--design", type=Path, default=EXPERIMENT_DIR / "design_manifest.json"
    )
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    parser.add_argument("--threads", type=int, default=3)
    parser.add_argument("--calibration-trials", type=int, default=120)
    parser.add_argument("--psychometric-trials", type=int, default=300)
    parser.add_argument("--attention-trials", type=int, default=240)
    parser.add_argument("--intervention-trials", type=int, default=240)
    parser.add_argument("--bootstrap-replicates", type=int, default=2000)
    return parser


def _resolve_spec(
    label: str,
    train_noise_std: float,
    run_dir: Path,
    checkpoint: Path,
    expected_sha256: str,
    log: Path | None,
) -> ModelSpec:
    resolved_run = run_dir.expanduser().resolve()
    resolved_checkpoint = checkpoint.expanduser().resolve()
    if resolved_checkpoint != resolved_run / "rvit_paper_vda4_final.pt":
        raise ValueError(
            f"{label} checkpoint must be the run's exact rvit_paper_vda4_final.pt path; "
            f"got {resolved_checkpoint}"
        )
    if not resolved_checkpoint.is_file():
        raise FileNotFoundError(resolved_checkpoint)
    actual = sha256_file(resolved_checkpoint)
    if actual.lower() != expected_sha256.lower():
        raise RuntimeError(f"{label} checkpoint SHA-256 mismatch: {actual} != {expected_sha256}")
    return ModelSpec(
        label,
        float(train_noise_std),
        resolved_run,
        resolved_checkpoint,
        actual,
        log.expanduser().resolve() if log is not None else None,
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    for name in (
        "threads", "calibration_trials", "psychometric_trials", "attention_trials",
        "intervention_trials", "bootstrap_replicates",
    ):
        if int(getattr(args, name)) <= 0:
            raise ValueError(f"--{name.replace('_', '-')} must be positive")
    for name in (
        "calibration_trials", "psychometric_trials", "attention_trials", "intervention_trials"
    ):
        if int(getattr(args, name)) % len(ORDERED_INVALID_PAIRS):
            raise ValueError(f"--{name.replace('_', '-')} must be divisible by 12")
    output_root = args.output_root.expanduser().resolve()
    if output_root.exists():
        raise FileExistsError(f"refusing to overwrite output root: {output_root}")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    staging = output_root.parent / f".{output_root.name}.partial-{uuid.uuid4().hex}"
    if staging.exists():
        raise FileExistsError(staging)
    staging.mkdir()

    specs = (
        _resolve_spec(
            "train0", 0.0, args.clean_run_dir, args.clean_checkpoint,
            args.clean_expected_sha256, args.clean_log,
        ),
        _resolve_spec(
            "train0p5", 0.5, args.noisy_run_dir, args.noisy_checkpoint,
            args.noisy_expected_sha256, args.noisy_log,
        ),
    )
    cells = (
        EvaluationCell("train0_eval0", "train0", 0.0, 0.0),
        EvaluationCell("train0_eval0p5", "train0", 0.0, 0.5),
        EvaluationCell("train0p5_eval0", "train0p5", 0.5, 0.0),
        EvaluationCell("train0p5_eval0p5", "train0p5", 0.5, 0.5),
    )
    started = time.time()
    try:
        project_root = args.project_root.expanduser().resolve()
        launcher = args.launcher.expanduser().resolve()
        config = args.config.expanduser().resolve()
        design = args.design.expanduser().resolve()
        for path in (project_root, launcher, config, design):
            if not path.exists():
                raise FileNotFoundError(path)

        # The experiment-specific validator checks both final/latest terminal
        # checkpoint trees, 20,000 contiguous finite metric rows, clean save
        # markers, launch/source hashes, fresh initialization, and exact train
        # noise identity before any held-out trial is produced.
        from experiments.vda4_memory_noise.grid2x2_crossattn1_pilot_v1.validate_terminal_v1 import (
            validate_terminal,
        )

        validations: dict[str, Any] = {}
        for spec in specs:
            validations[spec.label] = validate_terminal(
                spec.run_dir,
                expected_memory_noise_std=spec.train_noise_std,
                project_root=project_root,
                launcher=launcher,
                config=config,
                design=design,
                log=spec.log,
                expected_final_sha256=spec.expected_checkpoint_sha256,
            )
        write_json(staging / "provenance" / "checkpoint_validation.json", validations)

        os.environ["RVIT_DEVICE"] = args.device
        sys.modules.setdefault("numpy._core", np.core)
        sys.modules.setdefault("numpy._core.multiarray", np.core.multiarray)
        import torch

        torch.set_num_threads(int(args.threads))
        if args.device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA evaluation requested but torch.cuda.is_available() is false")
        from vda_sweep import vda_core as core

        models = _load_models(core, specs)
        bank_registry: dict[str, dict[str, Any]] = {}
        activation = validate_noise_activation(core, models, specs, bank_registry)
        write_json(staging / "provenance" / "eval_noise_activation.json", activation)

        calibration_payload, calibration_lock = run_calibration(
            core, models, cells, bank_registry, int(args.calibration_trials)
        )
        save_npz(
            staging / "data" / "calibration.npz",
            calibration_payload,
            {"schema_version": SCHEMA_VERSION, "stage": "calibration"},
        )
        write_csv(staging / "tables" / "calibration.csv", calibration_rows(calibration_payload, cells))
        write_json(staging / "CALIBRATION_LOCK.json", calibration_lock)
        calibration_lock_sha256 = sha256_file(staging / "CALIBRATION_LOCK.json")
        focal_magnitude = float(calibration_lock["focal_selection"]["magnitude_degrees"])

        psych_payload, psych_rows, psych_summaries = run_psychometrics(
            core, models, cells, bank_registry, int(args.psychometric_trials)
        )
        attention_payload, attention_rows, patch_rows, matrix_rows, reorientation_rows = run_attention(
            core, models, cells, bank_registry, int(args.attention_trials), focal_magnitude
        )
        intervention_payload, intervention_rows = run_interventions(
            core, models, cells, bank_registry, int(args.intervention_trials), focal_magnitude
        )
        bootstrap_rows = bootstrap_primary_contrasts(
            psych_payload, cells, focal_magnitude, int(args.bootstrap_replicates)
        )

        common_metadata = {
            "schema_version": SCHEMA_VERSION,
            "task": TASK,
            "feedback": FEEDBACK,
            "grid_rows": GRID_ROWS,
            "grid_cols": GRID_COLS,
            "d_mem": D_MEM,
            "displayed_validities": ",".join(str(float(value)) for value in VALIDITIES),
            "primary_in_distribution_validities": "0.25,0.5,0.75",
            "policy_rule": "sampled_with_recorded_common_uniforms",
            "calibration_lock_sha256": calibration_lock_sha256,
            "producer_sha256": sha256_file(Path(__file__).resolve()),
        }
        save_npz(staging / "data" / "psychometrics.npz", psych_payload, common_metadata)
        save_npz(staging / "data" / "attention.npz", attention_payload, common_metadata)
        save_npz(staging / "data" / "interventions.npz", intervention_payload, common_metadata)
        write_csv(staging / "tables" / "psychometrics.csv", psych_rows)
        write_csv(staging / "tables" / "attention_metrics.csv", attention_rows)
        write_csv(staging / "tables" / "attention_patch_scores.csv", patch_rows)
        write_csv(staging / "tables" / "attention_matrices.csv", matrix_rows)
        write_csv(staging / "tables" / "attention_reorientation.csv", reorientation_rows)
        write_csv(staging / "tables" / "interventions.csv", intervention_rows)
        write_csv(staging / "tables" / "bootstrap_primary_contrasts.csv", bootstrap_rows)

        create_figures(
            staging / "figures", psych_payload, attention_payload,
            intervention_payload, cells, focal_magnitude,
        )

        summary = primary_summary(
            cells, psych_payload, psych_summaries, attention_payload,
            intervention_payload, calibration_lock, bootstrap_rows,
        )
        write_json(staging / "SUMMARY.json", summary)
        write_json(
            staging / "analysis_config.json",
            {
                **common_metadata,
                "experiment_dir": EXPERIMENT_DIR,
                "device": args.device,
                "threads": int(args.threads),
                "train_noise_levels": TRAIN_NOISE_LEVELS,
                "eval_noise_levels": EVAL_NOISE_LEVELS,
                "cells": [cell.__dict__ for cell in cells],
                "checkpoint_sha256": {spec.label: spec.expected_checkpoint_sha256 for spec in specs},
                "calibration_trials": int(args.calibration_trials),
                "psychometric_trials": int(args.psychometric_trials),
                "attention_trials": int(args.attention_trials),
                "intervention_trials": int(args.intervention_trials),
                "bootstrap_replicates": int(args.bootstrap_replicates),
                "fixed_psychometric_magnitudes_degrees": MAGNITUDES,
                "adaptive_focal_magnitude_degrees": focal_magnitude,
                "qualifying_frames": QUALIFYING_FRAMES,
                "intervention_roles": INTERVENTION_ROLES,
                "intervention_sources": INTERVENTION_SOURCES,
                "intervention_doses": INTERVENTION_DOSES,
                "intervention_clamp_from_frame": CLAMP_FROM,
                "intervention_logit_bias_magnitude": CLAMP_LOGIT_BIAS,
                "visual_attention_definition": "A[..., 4 queries, visual keys 0:4]",
                "memory_attention_definition": "A[..., 4 queries, recurrent-memory keys 4:8]",
                "patch_score_definition": "mean over four query rows for each key column",
                "regional_max_definition": "native 2x2 has one patch per region, so regional max equals patch score",
                "mnemonic_draw_policy": "one independent realization per unique sensory trial; no repeated draws of one sensory trial",
                "attention_timing": "t1-t4 cue aligned; t5-t6 target aligned; prechange target selectivity is not localization evidence",
            },
        )
        write_json(
            staging / "provenance" / "trial_bank_registry.json",
            {
                "schema_version": SCHEMA_VERSION,
                "rng_namespace": RNG_NAMESPACE,
                "banks": [bank_registry[key] for key in sorted(bank_registry)],
                "mnemonic_rng": (
                    "Dedicated NumPy PCG64 standard-normal schedules patch only torch.randn_like "
                    "inside each recurrent update; policy sampling uses separate recorded uniforms."
                ),
            },
        )

        validate_npz_roundtrip(
            staging / "data" / "psychometrics.npz",
            ("response_rate", "dprime", "criterion", "press_histogram"),
        )
        validate_npz_roundtrip(
            staging / "data" / "attention.npz",
            ("visual_attention_full_4x4", "memory_attention_full_4x4", "press"),
        )
        validate_npz_roundtrip(
            staging / "data" / "interventions.npz",
            ("response_rate", "dprime", "criterion", "intervention_labels"),
        )
        for figure_path in expected_figure_paths(staging):
            if not figure_path.is_file() or figure_path.stat().st_size < 1000:
                raise RuntimeError(f"missing or implausibly small registered figure {figure_path}")
        manifest = build_manifest(
            staging,
            {
                "producer": str(Path(__file__).resolve()),
                "producer_sha256": sha256_file(Path(__file__).resolve()),
                "calibration_lock_sha256": calibration_lock_sha256,
                "checkpoint_sha256": {spec.label: spec.expected_checkpoint_sha256 for spec in specs},
                "elapsed_seconds": time.time() - started,
                "claim_boundary": summary["claim_boundary"],
            },
        )
        write_json(staging / "MANIFEST.json", manifest)
        manifest_sha = sha256_file(staging / "MANIFEST.json")
        (staging / "MANIFEST.sha256").write_text(
            f"{manifest_sha}  MANIFEST.json\n", encoding="ascii"
        )
        os.replace(staging, output_root)
        print(
            f"COMPLETE|output={output_root}|manifest_sha256={manifest_sha}|"
            f"focal_magnitude={focal_magnitude:g}|"
            f"nonsaturation={calibration_lock['focal_selection']['common_nonsaturation_pass']}",
            flush=True,
        )
        return 0
    except Exception:
        # Preserve the partial directory for forensic diagnosis; never promote it
        # and never mutate a prior output root.
        failure = {
            "schema_version": SCHEMA_VERSION,
            "status": "failed_before_atomic_promotion",
            "staging_directory": str(staging),
            "elapsed_seconds": time.time() - started,
        }
        with contextlib.suppress(Exception):
            write_json(staging / "FAILED.json", failure)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
