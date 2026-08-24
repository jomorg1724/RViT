from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "vda4_crossattn_decay_series.py"
)
SPEC = importlib.util.spec_from_file_location("vda4_crossattn_decay_series", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def _model_kwargs(decay: float | None) -> dict:
    kwargs = {
        "feedback": "crossattn1",
        "cell": "xlstm",
        "d_mem": 128,
        "conv_frontend": True,
        "grid_rows": 2,
        "grid_cols": 2,
        "image_size": 50,
    }
    if decay is not None:
        kwargs["memory_decay"] = decay
    return kwargs


def test_model_roles_and_decay_contract_are_exact():
    assert M.MODEL_ROLES == ("no_decay", "light_decay", "heavy_decay")
    np.testing.assert_allclose(M.MODEL_DECAYS, [1.0, 0.8, 0.5])
    checkpoints = {
        "no_decay": {"task": "vda4", "model_kwargs": _model_kwargs(None)},
        "light_decay": {"task": "vda4", "model_kwargs": _model_kwargs(0.8)},
        "heavy_decay": {"task": "vda4", "model_kwargs": _model_kwargs(0.5)},
    }
    for role, checkpoint in checkpoints.items():
        resolved = M.resolved_model_kwargs(checkpoint, role=role)
        assert resolved["memory_decay"] == pytest.approx(
            M.MODEL_DECAYS[M.MODEL_ROLES.index(role)]
        )


@pytest.mark.parametrize(
    ("role", "decay"),
    [("no_decay", 0.8), ("light_decay", 0.5), ("heavy_decay", 0.8)],
)
def test_model_contract_rejects_role_decay_mismatch(role, decay):
    checkpoint = {"task": "vda4", "model_kwargs": _model_kwargs(decay)}
    with pytest.raises(ValueError, match="memory_decay"):
        M.resolved_model_kwargs(checkpoint, role=role)


def _synthetic_payload(trials: int = 8) -> dict:
    rng = np.random.default_rng(11)
    motion = np.empty((3, 2, trials, 6), dtype=np.float32)
    selectivity = np.empty((3, 2, trials, 7), dtype=np.float32)
    peak = np.empty_like(selectivity)
    image = np.empty_like(selectivity)
    spatial = np.empty((3, 2, trials, 7, 4), dtype=np.float32)
    nochange_motion = np.empty((3, 4, trials, 6), dtype=np.float32)
    nochange_spatial = np.empty((3, 4, trials, 7, 4), dtype=np.float32)
    for model, offset in enumerate((0.0, 0.1, 0.2)):
        motion[model] = 0.2 + offset + rng.normal(0, 0.001, motion[model].shape)
        selectivity[model] = 0.3 + offset + rng.normal(0, 0.001, selectivity[model].shape)
        peak[model] = 0.4 + offset + rng.normal(0, 0.001, peak[model].shape)
        image[model] = 0.5 - offset + rng.normal(0, 0.001, image[model].shape)
        spatial[model] = 0.25
        nochange_motion[model] = 0.15 + offset
        nochange_spatial[model] = 0.25
    qualifying = np.zeros((3, 2, trials), dtype=bool)
    qualifying[1, :, :4] = True
    qualifying[2, :, :6] = True
    counts = np.zeros((3, 4, 10, 2), dtype=np.int64)
    counts[0] = 1
    counts[1] = 2
    counts[2] = 3
    rates = counts / 10.0
    return {
        "event_temporal_motion": motion,
        "event_selectivity": selectivity,
        "event_peak_key_mass": peak,
        "event_image_mass": image,
        "event_spatial_mass": spatial,
        "nochange_temporal_motion": nochange_motion,
        "nochange_spatial_mass": nochange_spatial,
        "event_qualifying_response": qualifying,
        "psychometric_response_count": counts,
        "psychometric_response_rate": rates,
        "psychometric_trials": np.array(10),
        "attention_trials": np.array(trials),
        "nochange_trials": np.array(trials),
        "checkpoint_iterations": np.array([20000, 19999, 22799]),
        "checkpoint_sha256": np.asarray(["a" * 64, "b" * 64, "c" * 64]),
    }


def test_summary_reports_all_pairwise_contrasts_and_monotonic_order():
    summary = M.build_numeric_summary(_synthetic_payload())
    primary = summary["metrics"]["primary_event_attention_motion"]
    assert summary["primary_order"] == "monotonic_increase_with_decay_strength"
    assert set(primary["model_means"]) == set(M.MODEL_ROLES)
    assert set(primary["pairwise"]) == {
        "light_minus_no",
        "heavy_minus_no",
        "heavy_minus_light",
    }
    assert primary["pairwise"]["light_minus_no"]["mean_difference"] == pytest.approx(
        0.1, abs=0.002
    )
    assert primary["pairwise"]["heavy_minus_no"]["mean_difference"] == pytest.approx(
        0.2, abs=0.002
    )


def test_tex_merges_old_plot_classes_and_names_all_models():
    summary = M.build_numeric_summary(_synthetic_payload())
    records = {
        role: {
            "checkpoint_iteration": iteration,
            "sha256": character * 64,
        }
        for role, iteration, character in zip(
            M.MODEL_ROLES, (20000, 19999, 22799), ("a", "b", "c")
        )
    }
    tex = M.render_tex(summary, records, "synthetic_run")
    for text in ("No decay", "Light decay", "Heavy decay"):
        assert text in tex
    for stem in M.FIGURE_STEMS:
        assert stem in tex
    assert "iteration 22,799" in tex
    assert "14,649" in tex
    assert "supersedes" in tex
