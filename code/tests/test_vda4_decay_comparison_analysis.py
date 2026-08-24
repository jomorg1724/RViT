from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "analysis" / "vda4_decay_comparison.py"
SPEC = importlib.util.spec_from_file_location("vda4_decay_comparison", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def test_artifact_matplotlib_configuration_uses_extractable_vector_fonts():
    class FakeMatplotlib:
        def __init__(self):
            self.backend_calls = []
            self.rcParams = {}

        def use(self, backend, *, force):
            self.backend_calls.append((backend, force))

    fake = FakeMatplotlib()
    M.configure_matplotlib_for_artifacts(fake)

    assert fake.backend_calls == [("Agg", True)]
    assert fake.rcParams["pdf.fonttype"] == 42
    assert fake.rcParams["ps.fonttype"] == 42
    assert fake.rcParams["svg.fonttype"] == "none"


def test_attention_metrics_define_activity_selectivity_and_source_mass_exactly():
    # One trial, three frames, two queries, and image+memory keys for two locations.
    raw = np.array(
        [[
            [[0.25, 0.25, 0.25, 0.25], [0.25, 0.25, 0.25, 0.25]],
            [[0.50, 0.00, 0.25, 0.25], [0.00, 0.50, 0.25, 0.25]],
            [[0.00, 0.50, 0.25, 0.25], [0.50, 0.00, 0.25, 0.25]],
        ]],
        dtype=np.float64,
    )

    metrics = M.attention_metrics(raw)

    assert metrics["temporal_motion"].shape == (1, 2)
    np.testing.assert_allclose(metrics["temporal_motion"], [[0.25, 0.5]])
    np.testing.assert_allclose(metrics["image_mass"], [[0.5, 0.5, 0.5]])
    np.testing.assert_allclose(metrics["memory_mass"], [[0.5, 0.5, 0.5]])
    np.testing.assert_allclose(metrics["peak_key_mass"], [[0.25, 0.5, 0.5]])
    assert metrics["selectivity"][0, 0] == pytest.approx(0.0)
    assert np.all(metrics["selectivity"][0, 1:] > 0.0)
    assert metrics["spatial_mass"].shape == (1, 3, 2)
    np.testing.assert_allclose(metrics["spatial_mass"].sum(axis=-1), 1.0)


def test_attention_metrics_reject_non_normalized_or_wrong_cross_attention():
    with pytest.raises(ValueError, match="K=2Q"):
        M.attention_metrics(np.full((2, 7, 4, 4), 0.25))
    malformed = np.full((2, 7, 4, 8), 0.2)
    with pytest.raises(ValueError, match="sum to one"):
        M.attention_metrics(malformed)


def test_resolved_model_kwargs_bind_legacy_standard_and_explicit_high_decay():
    base = {
        "feedback": "crossattn1",
        "cell": "xlstm",
        "d_mem": 128,
        "conv_frontend": True,
        "grid_rows": 2,
        "grid_cols": 2,
        "image_size": 50,
    }
    standard = {"task": "vda4", "model_kwargs": dict(base)}
    high = {"task": "vda4", "model_kwargs": {**base, "memory_decay": 0.8}}

    standard_kwargs = M.resolved_model_kwargs(standard, role="standard")
    high_kwargs = M.resolved_model_kwargs(high, role="high_decay")

    assert standard_kwargs["memory_decay"] == 1.0
    assert high_kwargs["memory_decay"] == 0.8
    assert standard["model_kwargs"].get("memory_decay") is None


@pytest.mark.parametrize(
    ("role", "field", "value"),
    [
        ("standard", "feedback", "affine_ew"),
        ("standard", "grid_cols", 10),
        ("standard", "memory_decay", 0.8),
        ("high_decay", "memory_decay", 1.0),
    ],
)
def test_resolved_model_kwargs_reject_mismatched_comparison(role, field, value):
    kwargs = {
        "feedback": "crossattn1",
        "cell": "xlstm",
        "d_mem": 128,
        "conv_frontend": True,
        "grid_rows": 2,
        "grid_cols": 2,
        "image_size": 50,
    }
    kwargs[field] = value
    checkpoint = {"task": "vda4", "model_kwargs": kwargs}
    with pytest.raises(ValueError, match=field):
        M.resolved_model_kwargs(checkpoint, role=role)


def test_first_press_uses_first_action_and_frame_five_qualification():
    logits = np.zeros((4, 7, 2), dtype=np.float64)
    logits[..., 0] = 1.0
    logits[0, 4, 1] = 2.0
    logits[0, 6, 1] = 3.0
    logits[1, 5, 1] = 2.0
    logits[2, 6, 1] = 2.0

    first, qualifying = M.first_press_from_logits(logits, qualifying_frame=5)

    np.testing.assert_array_equal(first, [4, 5, 6, -1])
    np.testing.assert_array_equal(qualifying, [False, True, True, False])


def test_paired_mean_difference_is_high_minus_standard_and_deterministic():
    standard = np.array([0.0, 1.0, 2.0, 3.0])
    high = standard + np.array([1.0, 1.0, 3.0, 3.0])

    first = M.paired_mean_difference(high, standard, seed=9, bootstrap_samples=2000)
    second = M.paired_mean_difference(high, standard, seed=9, bootstrap_samples=2000)

    assert first == second
    assert first["mean_difference"] == pytest.approx(2.0)
    assert first["ci_low"] <= first["mean_difference"] <= first["ci_high"]
    assert first["n"] == 4


def test_paired_mean_difference_rejects_unpaired_or_nonfinite_values():
    with pytest.raises(ValueError, match="same shape"):
        M.paired_mean_difference(np.ones(3), np.ones(4), seed=1, bootstrap_samples=10)
    with pytest.raises(ValueError, match="finite"):
        M.paired_mean_difference(np.array([1.0, np.nan]), np.ones(2), seed=1, bootstrap_samples=10)


def _synthetic_comparison_payload(attention_trials=2, nochange_trials=1, psychometric_trials=3):
    raw_event = np.full((2, 2, attention_trials, 7, 4, 8), 1.0 / 8, dtype=np.float32)
    raw_nochange = np.full((2, 4, nochange_trials, 7, 4, 8), 1.0 / 8, dtype=np.float32)
    logits = np.zeros((2, 2, attention_trials, 7, 2), dtype=np.float32)
    logits[..., 0] = 1.0
    sources = M.source_resolved_attention(raw_event).astype(np.float32)
    payload = {
        "model_roles": np.asarray(M.MODEL_ROLES),
        "event_conditions": np.asarray(M.EVENT_CONDITIONS),
        "displayed_validities": M.DISPLAYED_VALIDITIES,
        "change_magnitudes": M.CHANGE_MAGNITUDES,
        "checkpoint_iterations": np.array([20000, 14649]),
        "checkpoint_sha256": np.asarray(["a" * 64, "b" * 64]),
        "resolved_memory_decay": np.array([1.0, 0.8]),
        "attention_trials": np.array(attention_trials),
        "nochange_trials": np.array(nochange_trials),
        "psychometric_trials": np.array(psychometric_trials),
        "event_seed": np.array(M.EVENT_SEED),
        "nochange_seed": np.array(M.NOCHANGE_SEED),
        "psychometric_seed": np.array(M.PSYCHOMETRIC_SEED),
        "point_seeds": np.tile(
            M.PSYCHOMETRIC_SEED + np.arange(len(M.CHANGE_MAGNITUDES)) * 101,
            (len(M.DISPLAYED_VALIDITIES), 1),
        ),
        "cue_index": np.array(0),
        "valid_change_index": np.array(0),
        "invalid_change_index": np.array(3),
        "event_magnitude": np.array(15.0),
        "event_displayed_validity": np.array(1.0),
        "qualifying_response_frame": np.array(5),
        "device": np.array("cpu"),
        "event_actor_logits": logits,
        "event_raw_attention": raw_event,
        "event_source_attention": sources,
        "event_query_averaged_attention": sources.mean(axis=-3),
        "event_first_press": np.full((2, 2, attention_trials), -1),
        "event_qualifying_response": np.zeros((2, 2, attention_trials), dtype=bool),
        "nochange_raw_attention": raw_nochange,
        "psychometric_response_count": np.zeros((2, 4, 10, 2), dtype=np.int64),
        "psychometric_response_rate": np.zeros((2, 4, 10, 2), dtype=np.float64),
        "psychometric_press_histogram": np.zeros((2, 4, 10, 2, 8), dtype=np.int64),
        "seed_policy": np.array(
            "common random numbers matched across models, displayed cue proportions, and valid/forced-invalid locations at each magnitude"
        ),
    }
    payload["psychometric_press_histogram"][..., 0] = psychometric_trials
    for model_index in range(2):
        for condition_index in range(2):
            for name, values in M.attention_metrics(raw_event[model_index, condition_index]).items():
                payload.setdefault(
                    f"event_{name}", np.empty((2, 2) + values.shape, dtype=np.float32)
                )[model_index, condition_index] = values
        for validity_index in range(4):
            for name, values in M.attention_metrics(raw_nochange[model_index, validity_index]).items():
                payload.setdefault(
                    f"nochange_{name}", np.empty((2, 4) + values.shape, dtype=np.float32)
                )[model_index, validity_index] = values
    return payload


def test_comparison_cache_validation_recomputes_attention_and_response_contract(tmp_path):
    cache = tmp_path / "comparison.npz"
    np.savez_compressed(cache, **_synthetic_comparison_payload())

    metadata = M.validate_comparison_cache(
        cache, expected_attention_trials=2, expected_nochange_trials=1, expected_psychometric_trials=3
    )

    assert metadata["attention_trials"] == 2
    assert metadata["device"] == "cpu"
    assert len(metadata["cache_sha256"]) == 64

    with np.load(cache, allow_pickle=False) as stored:
        corrupt = {name: stored[name] for name in stored.files}
    corrupt["psychometric_response_rate"] = corrupt["psychometric_response_rate"].copy()
    corrupt["psychometric_response_rate"][0, 0, 0, 0] = 0.5
    np.savez_compressed(cache, **corrupt)
    with pytest.raises(AssertionError):
        M.validate_comparison_cache(cache)


def test_checkpoint_iteration_uses_frozen_manifest_schema_and_rejects_mismatch():
    assert M.checkpoint_iteration({"checkpoint_iteration": 14649}, expected=14649) == 14649
    with pytest.raises(ValueError, match="iteration mismatch"):
        M.checkpoint_iteration({"checkpoint_iteration": 14649}, expected=20000)
    with pytest.raises(ValueError, match="checkpoint_iteration"):
        M.checkpoint_iteration({}, expected=14649)
