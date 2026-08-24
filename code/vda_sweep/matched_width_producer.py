"""Produce one fail-closed matched-width VDA checkpoint shard."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import platform

import numpy as np

from vda_sweep import matched_width as M
from vda_sweep import matched_width_compute as compute
from vda_sweep import vda_core as core
from vda_sweep import vda_fig_decode as decoder


def numerical_runtime() -> dict[str, str]:
    import scipy
    import sklearn
    import torch

    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "torch": torch.__version__,
        "scipy": scipy.__version__,
        "sklearn": sklearn.__version__,
        "device": core.DEVICE,
    }


def _press(model: object, spec: M.CheckpointSpec, *, validity: float, change: int,
           change_index: int, magnitude: float, seed: int, trials: int) -> np.ndarray:
    videos = core.make_video_batch(
        spec.task, spec.active_locations[0], validity, "red", change, change_index,
        magnitude, B=trials, seed=seed,
    )
    return core.press_times_clamp(
        model, spec.task, spec.active_locations[0], validity, "red", change,
        change_index, magnitude, videos=videos,
    )


def psychometric_payload(model: object, spec: M.CheckpointSpec) -> dict[str, np.ndarray]:
    shape = (len(M.DISPLAYED_VALIDITIES), len(M.CHANGE_MAGNITUDES))
    valid_hist = np.zeros(shape + (8,), dtype=np.int64)
    invalid_defined = len(spec.active_locations) > 1
    invalid_hist = np.full(shape + (8,), -1, dtype=np.int64)
    nochange_hist = np.zeros((len(M.DISPLAYED_VALIDITIES), 8), dtype=np.int64)
    cue, invalid = spec.active_locations[0], spec.active_locations[-1]
    for validity_index, validity in enumerate(M.DISPLAYED_VALIDITIES):
        for magnitude_index, magnitude in enumerate(M.CHANGE_MAGNITUDES):
            point_seed = M.PSYCHOMETRIC_SEED + magnitude_index * 101
            valid_hist[validity_index, magnitude_index] = compute.press_histogram(
                _press(
                    model, spec, validity=validity, change=1, change_index=cue,
                    magnitude=magnitude, seed=point_seed,
                    trials=M.PSYCHOMETRIC_TRIALS_PER_POINT,
                )
            )
            if invalid_defined:
                invalid_hist[validity_index, magnitude_index] = compute.press_histogram(
                    _press(
                        model, spec, validity=validity, change=1, change_index=invalid,
                        magnitude=magnitude, seed=point_seed,
                        trials=M.PSYCHOMETRIC_TRIALS_PER_POINT,
                    )
                )
        nochange_hist[validity_index] = compute.press_histogram(
            _press(
                model, spec, validity=validity, change=0, change_index=-1,
                magnitude=18.0, seed=M.PSYCHOMETRIC_SEED + 991,
                trials=M.PSYCHOMETRIC_TRIALS_PER_POINT,
            )
        )

    valid_count = valid_hist[..., 6:].sum(axis=-1)
    nochange_count = nochange_hist[..., 6:].sum(axis=-1)
    if invalid_defined:
        invalid_count = invalid_hist[..., 6:].sum(axis=-1)
        invalid_rate = invalid_count / M.PSYCHOMETRIC_TRIALS_PER_POINT
    else:
        invalid_count = np.full(shape, -1, dtype=np.int64)
        invalid_rate = np.full(shape, np.nan)
    return {
        "psychometric_response_count_valid": valid_count,
        "psychometric_response_count_invalid": invalid_count,
        "psychometric_response_rate_valid": valid_count / M.PSYCHOMETRIC_TRIALS_PER_POINT,
        "psychometric_response_rate_invalid": invalid_rate,
        "psychometric_press_histogram_valid": valid_hist,
        "psychometric_press_histogram_invalid": invalid_hist,
        "psychometric_nochange_response_count": nochange_count,
        "psychometric_nochange_response_rate": nochange_count / M.PSYCHOMETRIC_TRIALS_PER_POINT,
        "psychometric_nochange_press_histogram": nochange_hist,
    }


def decoder_payload(model: object, spec: M.CheckpointSpec) -> dict[str, np.ndarray]:
    design = compute.decoder_design(spec.task)
    cells, _, conditions, config = decoder.collect(
        model, spec.task, n=M.DECODER_N, seed=M.DECODER_SEED
    )
    expected_conditions = design["conditions"]
    for field in ("colour", "proportion", "change_true", "change_index"):
        np.testing.assert_array_equal(conditions[field], expected_conditions[field])  # type: ignore[index]
    if config != design["config"]:
        raise RuntimeError("decoder replay config drifted from the registered design")
    labels = design["labels"]
    fold_ids = design["fold_ids"]
    out: dict[str, np.ndarray] = {
        "decoder_sample_change_index": np.asarray(conditions["change_index"], dtype=np.int64)
    }
    for name in M.SAMPLE_LABELS:
        out[f"decoder_sample_label_{name}"] = np.asarray(labels[name], dtype=np.int64)  # type: ignore[index]
    for name in M.DECODED_VARIABLES:
        label = np.asarray(labels[name], dtype=np.int64)  # type: ignore[index]
        folds = np.asarray(fold_ids[name], dtype=np.int64)  # type: ignore[index]
        out[f"decoder_fold_id_{name}"] = folds
        out[f"decoder_native_{name}"] = compute.decode_timecourses(
            cells, label, folds, matched_dimensions=None
        )
        out[f"decoder_matched128_{name}"] = compute.decode_timecourses(
            cells, label, folds, matched_dimensions=128
        )
    return out


def clamp_payload(model: object, spec: M.CheckpointSpec) -> dict[str, np.ndarray]:
    cue, invalid = spec.active_locations[0], spec.active_locations[-1]
    invalid_defined = len(spec.active_locations) > 1
    validity = 0.75
    valid_videos = core.make_video_batch(
        spec.task, cue, validity, "red", 1, cue, 18.0,
        B=M.CLAMP_TRIALS, seed=M.CLAMP_SEED,
    )
    false_alarm_videos = core.make_video_batch(
        spec.task, cue, validity, "red", 0, -1, 18.0,
        B=M.CLAMP_TRIALS, seed=M.CLAMP_SEED + 1,
    )
    invalid_videos = None
    if invalid_defined:
        invalid_videos = core.make_video_batch(
            spec.task, cue, validity, "red", 1, invalid, 18.0,
            B=M.CLAMP_TRIALS, seed=M.CLAMP_SEED,
        )
    keys = 2 * model.n_tokens if spec.feedback == "crossattn1" else model.n_tokens  # type: ignore[attr-defined]
    valid_histograms: list[np.ndarray] = []
    invalid_histograms: list[np.ndarray] = []
    nochange_histograms: list[np.ndarray] = []
    for dose in M.CLAMP_DOSE_PARAMETERS:
        clamp = core.clamp_alpha(
            keys,
            model.n_tokens,  # type: ignore[attr-defined]
            cue,
            dose,
            scale=M.CLAMP_LOGIT_SCALE,
        )
        valid_press = core.press_times_clamp(
            model, spec.task, cue, validity, "red", 1, cue, 18.0,
            clamp=clamp, clamp_from=5, videos=valid_videos,
        )
        false_alarm_press = core.press_times_clamp(
            model, spec.task, cue, validity, "red", 0, -1, 18.0,
            clamp=clamp, clamp_from=5, videos=false_alarm_videos,
        )
        valid_histograms.append(compute.press_histogram(valid_press))
        nochange_histograms.append(compute.press_histogram(false_alarm_press))
        if invalid_defined:
            invalid_press = core.press_times_clamp(
                model, spec.task, cue, validity, "red", 1, invalid, 18.0,
                clamp=clamp, clamp_from=5, videos=invalid_videos,
            )
            invalid_histograms.append(compute.press_histogram(invalid_press))
    valid_histogram_array = np.asarray(valid_histograms, dtype=np.int64)
    nochange_histogram_array = np.asarray(nochange_histograms, dtype=np.int64)
    valid_count_array = valid_histogram_array[:, 6:].sum(axis=-1)
    false_alarm_count_array = nochange_histogram_array[:, 1:].sum(axis=-1)
    valid_dprime, valid_criterion = M._sdt_from_counts(
        valid_count_array, false_alarm_count_array, M.CLAMP_TRIALS
    )
    if invalid_defined:
        invalid_histogram_array = np.asarray(invalid_histograms, dtype=np.int64)
        invalid_count_array = invalid_histogram_array[:, 6:].sum(axis=-1)
        invalid_dprime, invalid_criterion = M._sdt_from_counts(
            invalid_count_array, false_alarm_count_array, M.CLAMP_TRIALS
        )
        invalid_rate = invalid_count_array / M.CLAMP_TRIALS
    else:
        invalid_histogram_array = np.full(
            (len(M.CLAMP_DOSE_PARAMETERS), 8), -1, dtype=np.int64
        )
        invalid_count_array = np.full(len(M.CLAMP_DOSE_PARAMETERS), -1, dtype=np.int64)
        invalid_rate = np.full(len(M.CLAMP_DOSE_PARAMETERS), np.nan)
        invalid_dprime = np.full(len(M.CLAMP_DOSE_PARAMETERS), np.nan)
        invalid_criterion = np.full(len(M.CLAMP_DOSE_PARAMETERS), np.nan)
    return {
        "clamp_press_histogram_valid": valid_histogram_array,
        "clamp_press_histogram_invalid": invalid_histogram_array,
        "clamp_press_histogram_nochange": nochange_histogram_array,
        "clamp_hit_count_valid": valid_count_array,
        "clamp_hit_count_invalid": invalid_count_array,
        "clamp_false_alarm_count": false_alarm_count_array,
        "clamp_hit_rate_valid": valid_count_array / M.CLAMP_TRIALS,
        "clamp_hit_rate_invalid": invalid_rate,
        "clamp_false_alarm_rate": false_alarm_count_array / M.CLAMP_TRIALS,
        "clamp_dprime_valid": valid_dprime,
        "clamp_dprime_invalid": invalid_dprime,
        "clamp_criterion_valid": valid_criterion,
        "clamp_criterion_invalid": invalid_criterion,
    }


def compute_shard_payload(
    spec: M.CheckpointSpec, *, source_hashes: dict[str, str]
) -> dict[str, np.ndarray]:
    checkpoint_before = M.sha256_file(spec.path)
    if checkpoint_before != spec.sha256:
        raise RuntimeError("checkpoint changed before matched-width computation")
    model, iteration = core.load(
        spec.task, spec.feedback, spec.width, checkpoint_path=str(spec.path.resolve())
    )
    if iteration != 19999:
        raise RuntimeError("loaded checkpoint iteration is not 19999")
    payload: dict[str, np.ndarray] = {
        "displayed_validities": np.asarray(M.DISPLAYED_VALIDITIES, dtype=float),
        "change_magnitudes": np.asarray(M.CHANGE_MAGNITUDES, dtype=float),
        "clamp_dose_parameters": np.asarray(M.CLAMP_DOSE_PARAMETERS, dtype=float),
        "clamp_key_logit_biases": np.asarray(M.CLAMP_KEY_LOGIT_BIASES, dtype=float),
    }
    payload.update(psychometric_payload(model, spec))
    payload.update(decoder_payload(model, spec))
    payload.update(clamp_payload(model, spec))
    checkpoint_after = M.sha256_file(spec.path)
    if checkpoint_after != checkpoint_before:
        raise RuntimeError("checkpoint changed during matched-width computation")
    metadata = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "task": spec.task,
        "feedback": spec.feedback,
        "width": spec.width,
        "checkpoint_path": str(spec.path.resolve()),
        "checkpoint_sha256": spec.sha256,
        "checkpoint_iteration": iteration,
        "protocol": M.protocol_for(spec),
        "source_hashes": source_hashes,
        "runtime": numerical_runtime(),
        "claim_boundary": (
            "checkpoint-specific width-associated comparison; not a replicated causal width effect "
            "or a human working-memory-capacity measure"
        ),
    }
    payload["metadata_json"] = np.asarray(json.dumps(metadata, sort_keys=True))
    M.validate_shard_payload(payload, spec)
    return payload


def write_shard(
    spec: M.CheckpointSpec,
    output_path: str | Path,
    *,
    source_hashes: dict[str, str],
) -> Path:
    output_path = Path(output_path).resolve()
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError(f"matched-width shard already exists: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = compute_shard_payload(spec, source_hashes=source_hashes)
    temporary = output_path.with_name(f".{output_path.name}.tmp")
    if temporary.exists() or temporary.is_symlink():
        raise FileExistsError(f"temporary matched-width shard already exists: {temporary}")
    try:
        with temporary.open("xb") as stream:
            np.savez_compressed(stream, **payload)
        with np.load(temporary, allow_pickle=False) as stored:
            M.validate_shard_payload(stored, spec)
        temporary.replace(output_path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return output_path
