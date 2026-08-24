from __future__ import annotations

import csv
import json

import numpy as np
from PIL import Image
import pytest

from vda_series import vda16_integration as integration


def test_qualifying_mean_rt_uses_only_frames_five_and_six():
    histogram = np.zeros((2, 8), dtype=np.int64)
    histogram[0, 0] = 7
    histogram[0, 6] = 3
    histogram[0, 7] = 1
    histogram[1, 0] = 10

    result = integration.qualifying_mean_rt(histogram)

    assert result[0] == pytest.approx(5.25)
    assert np.isnan(result[1])


def test_training_summary_competence_gates_unfinished_curriculum():
    metrics = {
        "iter": np.arange(20_000),
        "rolling/correct_rate": np.linspace(0.5, 0.8, 20_000),
        "env/theta": np.full(20_000, 65.0),
    }

    summary = integration.training_summary(metrics)

    assert summary["status"] == "competence_gated"
    assert summary["curriculum_completed"] is False
    assert summary["final_theta_degrees"] == 65.0


def test_achieved_attention_cache_requires_trials_and_reconstructable_means(tmp_path):
    path = tmp_path / "achieved.npz"
    trials = np.full((3, 5, 7, 250), 0.25, dtype=np.float32)
    metadata = {
        "checkpoint_sha256": "b" * 64,
        "checkpoint_iteration": 19_999,
        "task": "vda16",
        "feedback": "crossattn1",
        "width": 128,
        "memory_decay": 1.0,
        "device": "cpu",
        "runtime": {
            "python": "test",
            "python_executable": "python",
            "numpy": "test",
            "torch": "test",
            "platform": "test",
        },
        "source_hashes": {"producer": "a" * 64},
    }
    np.savez_compressed(
        path,
        metadata_json=np.asarray(json.dumps(metadata)),
        conditions=np.asarray(["valid", "invalid", "nochange"]),
        clamp_dose_parameters=np.asarray([0.0, 0.25, 0.5, 0.75, 1.0]),
        clamp_key_logit_biases=np.asarray([-6.0, -3.0, 0.0, 3.0, 6.0]),
        achieved_cued_attention_mass_trials=trials,
        achieved_cued_attention_mass_mean=trials.mean(axis=-1),
        achieved_cued_attention_mass_sem=trials.std(axis=-1, ddof=1) / np.sqrt(250),
    )

    result = integration.validate_achieved_clamp_attention(
        path,
        expected_checkpoint_sha256="b" * 64,
        expected_device="cpu",
        expected_source_hashes={"producer": "a" * 64},
    )

    assert result["checkpoint_iteration"] == 19_999
    with pytest.raises(ValueError, match="checkpoint hash mismatch"):
        integration.validate_achieved_clamp_attention(
            path, expected_checkpoint_sha256="c" * 64
        )
    np.savez_compressed(
        path,
        metadata_json=np.asarray(json.dumps(metadata)),
        conditions=np.asarray(["valid", "invalid", "nochange"]),
        clamp_dose_parameters=np.asarray([0.0, 0.25, 0.5, 0.75, 1.0]),
        clamp_key_logit_biases=np.asarray([-6.0, -3.0, 0.0, 3.0, 6.0]),
        achieved_cued_attention_mass_trials=trials,
        achieved_cued_attention_mass_mean=trials.mean(axis=-1),
        achieved_cued_attention_mass_sem=np.ones((3, 5, 7)),
    )
    with pytest.raises(AssertionError):
        integration.validate_achieved_clamp_attention(
            path,
            expected_checkpoint_sha256="b" * 64,
            expected_device="cpu",
            expected_source_hashes={"producer": "a" * 64},
        )


def test_method_comparison_renders_competence_gated_vda16_without_clamp_metric(
    tmp_path, monkeypatch
):
    def payload(task="vda4"):
        invalid = np.full((4, 1), 0.2)
        if task == "vda1":
            invalid[:] = np.nan
        return {
            "displayed_validities": np.asarray([0.25, 0.5, 0.75, 1.0]),
            "change_magnitudes": np.asarray([18.0]),
            "psychometric_response_rate_valid": np.full((4, 1), 0.7),
            "psychometric_response_rate_invalid": invalid,
            "psychometric_nochange_response_rate": np.full(4, 0.1),
            "decoder_matched128_change": np.full(7, 0.75),
            "decoder_matched128_cued_change": (
                np.full(7, np.nan) if task == "vda1" else np.full(7, 0.7)
            ),
        }

    monkeypatch.setattr(
        integration,
        "_historical_shard",
        lambda root, task, feedback: payload(task),
    )
    monkeypatch.setattr(integration, "_load_npz", lambda path: payload("vda16"))

    outputs = integration.build_method_comparison_figure(
        tmp_path / "vda16.npz",
        tmp_path,
        tmp_path / "method_comparison",
        vda16_competence_status="competence_gated",
        vda16_final_theta=65.0,
    )

    assert set(outputs) == {"pdf", "svg", "png"}
    assert all(path.is_file() and path.stat().st_size > 0 for path in outputs.values())
    with Image.open(outputs["png"]) as image:
        width, height = image.size
    assert height < width


def _write_metrics(path, rows=20_000):
    fields = [
        "iter",
        "rolling/correct_rate",
        "rolling/mean_return",
        "rollout/correct_rate",
        "env/theta",
        "loss_policy",
        "loss_value",
        "loss_jepa",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for iteration in range(rows):
            writer.writerow(
                {
                    "iter": iteration,
                    "rolling/correct_rate": 0.8,
                    "rolling/mean_return": 2.0,
                    "rollout/correct_rate": 0.75,
                    "env/theta": 65.0,
                    "loss_policy": 0.1,
                    "loss_value": 0.2,
                    "loss_jepa": 2.0,
                }
            )


def test_checkpoint_admission_requires_final_identity_and_complete_ledger(
    tmp_path, monkeypatch
):
    checkpoint = tmp_path / "rvit_paper_vda16_final.pt"
    checkpoint.write_bytes(b"schema-three-checkpoint")
    metrics = tmp_path / "metrics.csv"
    _write_metrics(metrics)
    launcher = tmp_path / "launcher.ps1"
    launcher.write_text("Write-Output launch", encoding="utf-8")
    launch = {
        "task": "vda16",
        "feedback": "crossattn1",
        "memory_decay": 1.0,
        "d_mem": 128,
        "patch_grid_rows": 4,
        "patch_grid_cols": 4,
        "initialization": "fresh",
        "curriculum": True,
        "seed": 0,
        "iterations": 20_000,
        "schedule_final_iteration": 19_999,
        "launcher": str(launcher),
    }
    launch_path = tmp_path / "launch_manifest.json"
    launch_path.write_text(json.dumps(launch), encoding="utf-8")
    payload = {
        "checkpoint_schema_version": 3,
        "iter": 19_999,
        "task": "vda16",
        "model_kwargs": {
            "feedback": "crossattn1",
            "d_mem": 128,
            "memory_decay": 1.0,
            "conv_frontend": True,
            "grid_rows": 4,
            "grid_cols": 4,
            "image_size": 100,
            "seq_len": 7,
        },
        "training_args": {
            "task": "vda16",
            "feedback": "crossattn1",
            "d_mem": 128,
            "memory_decay": 1.0,
            "patch_grid_rows": 4,
            "patch_grid_cols": 4,
            "init_mode": "fresh",
            "curriculum": True,
            "seed": 0,
            "iters": 20_000,
            "schedule_final_iteration": 19_999,
        },
        "producer_sha256": {"resolved_config": "a" * 64},
        "runtime_versions": {"python": "test"},
        "resume_fidelity": "replay_excluded_trainer_state",
        "replay_buffer_persisted": False,
    }
    monkeypatch.setattr(integration.torch, "load", lambda *args, **kwargs: payload)

    admitted = integration.validate_checkpoint_admission(
        checkpoint, launch_path, metrics, project_root=tmp_path
    )

    assert admitted["checkpoint_iteration"] == 19_999
    assert admitted["training"]["status"] == "competence_gated"
    assert admitted["replay_buffer_persisted"] is False

    _write_metrics(metrics, rows=19_999)
    with pytest.raises(ValueError, match="metrics contain 19999 rows"):
        integration.validate_checkpoint_admission(
            checkpoint, launch_path, metrics, project_root=tmp_path
        )
