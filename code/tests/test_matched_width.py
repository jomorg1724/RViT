from __future__ import annotations

import json

import numpy as np
import pytest

from vda_sweep import matched_width as M


def test_registry_admits_exact_matched_geometry_scope_and_blocks_vda2():
    specs = M.admissible_specs()
    assert len(specs) == 12
    assert {(spec.task, spec.feedback, spec.width) for spec in specs} == {
        (task, feedback, width)
        for task in ("vda1", "vda4", "vda9")
        for feedback in ("affine_ew", "crossattn1")
        for width in (128, 256)
    }
    assert M.BLOCKED_TASKS == {
        "vda2": {
            "status": "blocked",
            "reason": "no canonical d_mem=256 2x2 checkpoint; available d256 checkpoint has two tokens",
            "canonical_d128_tokens": 4,
            "available_d256_tokens": 2,
        }
    }
    blocked = M.blocked_cells()
    assert blocked == [
        {
            "task": "vda2",
            "widths": [128, 256],
            "feedbacks": ["affine_ew", "crossattn1"],
            **M.BLOCKED_TASKS["vda2"],
        }
    ]
    assert M.COMPETENCE_FLAGS == [
        {
            "task": "vda9",
            "feedback": "crossattn1",
            "width": 256,
            "status": "competence_gated",
            "last_correct": 0.48,
            "late50_mean_correct": 0.45935,
            "best_correct": 0.5825,
            "last_theta": 65.0,
            "interpretation": (
                "retain in declared scope, but interpret mechanistic estimates as possible "
                "floor-policy diagnostics rather than controlled-attention evidence"
            ),
            "evidence_identity": "__metrics_inventory__",
            "evidence_row": 41,
        }
    ]


def test_registry_binds_existing_distinct_iteration_19999_checkpoints():
    records = M.validate_checkpoint_registry()
    assert len(records) == 12
    assert len({record["sha256"] for record in records}) == 12
    assert all(record["iteration"] == 19999 for record in records)
    assert all(record["nlink"] >= 1 for record in records)


def test_protocol_is_identical_across_width_and_routing_within_task():
    for task in M.TASKS:
        protocols = [M.protocol_for(spec) for spec in M.admissible_specs() if spec.task == task]
        assert protocols == [protocols[0]] * 4
        assert protocols[0]["psychometric_trials_per_point"] == 300
        assert protocols[0]["decoder_n"] == 900
        assert protocols[0]["clamp_trials"] == 250
        assert "clamp_alphas" not in protocols[0]
        assert protocols[0]["clamp_logit_scale"] == 6.0
        assert protocols[0]["clamp_key_logit_biases"] == (-6.0, -3.0, 0.0, 3.0, 6.0)
        assert protocols[0]["clamp_intervention_semantics"] == (
            "additive bias to the cued location's attention-key logits; not achieved attention mass"
        )
        assert protocols[0]["clamp_target_keys_by_routing"] == {
            "affine_ew": "cued image/self key",
            "crossattn1": "cued image key and corresponding memory key",
        }
        assert protocols[0]["clamp_false_alarm_definition"] == (
            "any declaration frame 0-6 on a no-change trial"
        )
        assert protocols[0]["common_random_numbers_across_width_and_routing"] is True


def test_shard_schema_is_exact_and_covers_all_required_estimands():
    keys = M.expected_shard_keys()
    assert "metadata_json" in keys
    assert {
        "psychometric_response_count_valid",
        "psychometric_response_count_invalid",
        "psychometric_nochange_response_count",
        "psychometric_press_histogram_valid",
    } <= keys
    assert {
        f"decoder_{space}_{name}"
        for space in ("native", "matched128")
        for name in M.DECODED_VARIABLES
    } <= keys
    assert {
        "clamp_hit_count_valid",
        "clamp_hit_count_invalid",
        "clamp_false_alarm_count",
        "clamp_dprime_valid",
        "clamp_criterion_invalid",
    } <= keys
    assert {f"decoder_sample_label_{name}" for name in M.SAMPLE_LABELS} <= keys
    assert {f"decoder_fold_id_{name}" for name in M.DECODED_VARIABLES} <= keys


def _valid_shard_payload(
    spec: M.CheckpointSpec,
    *,
    source_hashes: dict[str, str] | None = None,
    runtime: dict[str, str] | None = None,
) -> dict[str, np.ndarray]:
    protocol = M.protocol_for(spec)
    psych_shape = (len(M.DISPLAYED_VALIDITIES), len(M.CHANGE_MAGNITUDES))
    invalid_defined = bool(protocol["invalid_defined"])
    invalid_count = np.full(psych_shape, 150 if invalid_defined else -1, dtype=np.int64)
    invalid_rate = np.full(psych_shape, 0.5 if invalid_defined else np.nan)
    invalid_hist = np.full(psych_shape + (8,), -1, dtype=np.int64)
    if invalid_defined:
        invalid_hist.fill(0)
        invalid_hist[..., 0] = 150
        invalid_hist[..., 6] = 150
    metadata = {
        "task": spec.task,
        "feedback": spec.feedback,
        "width": spec.width,
        "checkpoint_path": str(spec.path.resolve()),
        "checkpoint_sha256": spec.sha256,
        "checkpoint_iteration": 19999,
        "protocol": protocol,
        "source_hashes": source_hashes or {"vda_sweep/matched_width.py": "a" * 64},
        "runtime": runtime or {
            "python": "test",
            "numpy": "test",
            "torch": "test",
            "scipy": "test",
            "sklearn": "test",
            "device": "cpu",
        },
    }
    payload: dict[str, np.ndarray] = {
        "metadata_json": np.asarray(json.dumps(metadata, sort_keys=True)),
        "displayed_validities": np.asarray(M.DISPLAYED_VALIDITIES),
        "change_magnitudes": np.asarray(M.CHANGE_MAGNITUDES),
        "psychometric_response_count_valid": np.full(psych_shape, 150, dtype=np.int64),
        "psychometric_response_count_invalid": invalid_count,
        "psychometric_response_rate_valid": np.full(psych_shape, 0.5),
        "psychometric_response_rate_invalid": invalid_rate,
        "psychometric_press_histogram_valid": np.zeros(psych_shape + (8,), dtype=np.int64),
        "psychometric_press_histogram_invalid": invalid_hist,
        "psychometric_nochange_response_count": np.full(len(M.DISPLAYED_VALIDITIES), 150, dtype=np.int64),
        "psychometric_nochange_response_rate": np.full(len(M.DISPLAYED_VALIDITIES), 0.5),
        "psychometric_nochange_press_histogram": np.zeros(
            (len(M.DISPLAYED_VALIDITIES), 8), dtype=np.int64
        ),
        "decoder_sample_change_index": np.zeros(M.DECODER_N, dtype=np.int64),
        "clamp_dose_parameters": np.asarray(M.CLAMP_DOSE_PARAMETERS),
        "clamp_key_logit_biases": np.asarray(M.CLAMP_KEY_LOGIT_BIASES),
        "clamp_press_histogram_valid": np.zeros(
            (len(M.CLAMP_DOSE_PARAMETERS), 8), dtype=np.int64
        ),
        "clamp_press_histogram_invalid": np.full(
            (len(M.CLAMP_DOSE_PARAMETERS), 8), -1, dtype=np.int64
        ),
        "clamp_press_histogram_nochange": np.zeros(
            (len(M.CLAMP_DOSE_PARAMETERS), 8), dtype=np.int64
        ),
        "clamp_hit_count_valid": np.full(len(M.CLAMP_DOSE_PARAMETERS), 125, dtype=np.int64),
        "clamp_hit_count_invalid": np.full(
            len(M.CLAMP_DOSE_PARAMETERS), 125 if invalid_defined else -1, dtype=np.int64
        ),
        "clamp_false_alarm_count": np.full(len(M.CLAMP_DOSE_PARAMETERS), 125, dtype=np.int64),
        "clamp_hit_rate_valid": np.full(len(M.CLAMP_DOSE_PARAMETERS), 0.5),
        "clamp_hit_rate_invalid": np.full(
            len(M.CLAMP_DOSE_PARAMETERS), 0.5 if invalid_defined else np.nan
        ),
        "clamp_false_alarm_rate": np.full(len(M.CLAMP_DOSE_PARAMETERS), 0.5),
        "clamp_dprime_valid": np.zeros(len(M.CLAMP_DOSE_PARAMETERS)),
        "clamp_dprime_invalid": np.full(
            len(M.CLAMP_DOSE_PARAMETERS), 0.0 if invalid_defined else np.nan
        ),
        "clamp_criterion_valid": np.zeros(len(M.CLAMP_DOSE_PARAMETERS)),
        "clamp_criterion_invalid": np.full(
            len(M.CLAMP_DOSE_PARAMETERS), 0.0 if invalid_defined else np.nan
        ),
    }
    payload["psychometric_press_histogram_valid"][..., 0] = 150
    payload["psychometric_press_histogram_valid"][..., 6] = 150
    payload["psychometric_nochange_press_histogram"][:, 0] = 150
    payload["psychometric_nochange_press_histogram"][:, 6] = 150
    payload["clamp_press_histogram_valid"][:, 0] = 125
    payload["clamp_press_histogram_valid"][:, 6] = 125
    payload["clamp_press_histogram_nochange"][:, 0] = 125
    payload["clamp_press_histogram_nochange"][:, 6] = 125
    if invalid_defined:
        payload["clamp_press_histogram_invalid"].fill(0)
        payload["clamp_press_histogram_invalid"][:, 0] = 125
        payload["clamp_press_histogram_invalid"][:, 6] = 125
    for name in M.DECODED_VARIABLES:
        defined = name not in ("change_location", "cued_change") or invalid_defined
        for space in ("native", "matched128"):
            payload[f"decoder_{space}_{name}"] = np.full(7, 0.5 if defined else np.nan)
        payload[f"decoder_fold_id_{name}"] = np.full(
            M.DECODER_N, 0 if defined else -1, dtype=np.int64
        )
    for name in M.SAMPLE_LABELS:
        payload[f"decoder_sample_label_{name}"] = np.zeros(M.DECODER_N, dtype=np.int64)
    return payload


@pytest.mark.parametrize("task", ["vda1", "vda4"])
def test_shard_validator_accepts_defined_and_explicitly_undefined_cells(task):
    spec = next(spec for spec in M.admissible_specs() if spec.task == task)
    metadata = M.validate_shard_payload(_valid_shard_payload(spec), spec)
    assert metadata["task"] == task


def test_shard_validator_rejects_unmanifested_fields_and_rate_drift():
    spec = next(spec for spec in M.admissible_specs() if spec.task == "vda4")
    payload = _valid_shard_payload(spec)
    payload["extra"] = np.asarray(1)
    with pytest.raises(ValueError, match="key inventory"):
        M.validate_shard_payload(payload, spec)
    del payload["extra"]
    payload["psychometric_response_rate_valid"][0, 0] = 0.7
    with pytest.raises(AssertionError):
        M.validate_shard_payload(payload, spec)

    payload = _valid_shard_payload(spec)
    payload["clamp_press_histogram_nochange"][0, 0] -= 1
    payload["clamp_press_histogram_nochange"][0, 2] += 1
    with pytest.raises(AssertionError):
        M.validate_shard_payload(payload, spec)


def test_singleton_undefined_clamp_histogram_requires_integer_sentinel():
    spec = next(spec for spec in M.admissible_specs() if spec.task == "vda1")
    payload = _valid_shard_payload(spec)
    payload["clamp_press_histogram_invalid"] = payload[
        "clamp_press_histogram_invalid"
    ].astype(float)
    with pytest.raises(ValueError, match="explicitly undefined"):
        M.validate_shard_payload(payload, spec)
