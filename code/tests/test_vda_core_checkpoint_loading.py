from __future__ import annotations

from pathlib import Path

import pytest
import torch

from model import RViTPaperModel
from experiments.vda_stream_factorial.stream_model import StreamFactorialModel, build_stream_factorial_model
from vda_sweep import vda_core


def _schema_checkpoint(path: Path, *, task: str = "vda1", iteration: int = 19999) -> Path:
    model_kwargs = {
        "n_actions": 2,
        "n_quantiles": 5,
        "init_action_bias": [0.0, -1.5],
        "seq_len": 7,
        "feedback": "crossattn1",
        "two_lstm": False,
        "cell": "xlstm",
        "mem_heads": 4,
        "vae_in_channels": 1,
        "jepa_n_heads": 0,
        "jepa_proto_dim": 256,
        "frame_repeat": 1,
        "d_mem": 16,
        "memory_decay": 1.0,
        "conv_frontend": True,
        "grid_rows": 2,
        "grid_cols": 2,
        "image_size": 50,
    }
    model = RViTPaperModel(**model_kwargs)
    torch.save(
        {
            "checkpoint_schema_version": 3,
            "task": task,
            "iter": iteration,
            "model_kwargs": model_kwargs,
            "model_state_dict": model.state_dict(),
            "producer_sha256": {"train_rl.py": "a" * 64},
        },
        path,
    )
    return path


def _stream_factorial_checkpoint(
    path: Path,
    *,
    visual_streams: int = 4,
    memory_streams: int = 100,
    feedback: str = "crossattn1",
    iteration: int = 19999,
) -> tuple[Path, StreamFactorialModel]:
    model_kwargs = {
        "n_actions": 2,
        "n_quantiles": 5,
        "init_action_bias": [0.0, -1.5],
        "seq_len": 7,
        "feedback": feedback,
        "two_lstm": False,
        "cell": "xlstm",
        "jepa_n_heads": 4,
        "jepa_proto_dim": 256,
        "frame_repeat": 1,
        "d_mem": 16,
        "memory_decay": 1.0,
        "memory_noise_std": 0.0,
        "conv_frontend": True,
        "grid_rows": 10,
        "grid_cols": 10,
        "image_size": 50,
    }
    factory_kwargs = {
        key: value
        for key, value in model_kwargs.items()
        if key not in {
            "feedback", "two_lstm", "cell", "d_mem", "conv_frontend",
            "grid_rows", "grid_cols", "image_size",
        }
    }
    model = build_stream_factorial_model(
        visual_streams,
        memory_streams,
        feedback,
        d_mem=16,
        image_size=50,
        **factory_kwargs,
    )
    torch.save(
        {
            "checkpoint_schema_version": 3,
            "task": "vda4",
            "iter": iteration,
            "model_factory": {
                "kind": "stream_factorial_v1",
                "effective_visual_streams": visual_streams,
                "effective_memory_streams": memory_streams,
                "carrier_grid": [10, 10],
            },
            "model_kwargs": model_kwargs,
            "model_state_dict": model.state_dict(),
            "producer_sha256": {"train_rl.py": "a" * 64},
        },
        path,
    )
    return path, model


def test_schema_checkpoint_uses_embedded_model_kwargs_and_identity(tmp_path, monkeypatch):
    checkpoint = _schema_checkpoint(tmp_path / "checkpoint.pt")
    monkeypatch.setattr(vda_core, "DEVICE", "cpu")
    digest = vda_core.sha256_file(checkpoint)

    model, iteration = vda_core.load(
        "vda1",
        "crossattn1",
        16,
        checkpoint_path=checkpoint,
        expected_checkpoint_sha256=digest,
        require_iteration=19999,
    )

    assert iteration == 19999
    assert model.n_tokens == 4
    assert model.encoder.d_mem == 16
    assert model.encoder.memory_decay == 1.0
    assert model.analysis_checkpoint_path == str(checkpoint.resolve())
    assert model.analysis_checkpoint_sha256 == digest


@pytest.mark.parametrize(
    ("field", "requested", "message"),
    [
        ("task", ("vda4", "crossattn1", 16), "checkpoint task"),
        ("feedback", ("vda1", "affine_ew", 16), "checkpoint feedback"),
        ("width", ("vda1", "crossattn1", 32), "checkpoint d_mem"),
    ],
)
def test_schema_checkpoint_rejects_requested_identity_mismatch(
    tmp_path, monkeypatch, field, requested, message
):
    del field
    checkpoint = _schema_checkpoint(tmp_path / "checkpoint.pt")
    monkeypatch.setattr(vda_core, "DEVICE", "cpu")

    with pytest.raises(ValueError, match=message):
        vda_core.load(*requested, checkpoint_path=checkpoint)


def test_schema_checkpoint_rejects_hash_and_iteration_mismatch(tmp_path, monkeypatch):
    checkpoint = _schema_checkpoint(tmp_path / "checkpoint.pt", iteration=123)
    monkeypatch.setattr(vda_core, "DEVICE", "cpu")

    with pytest.raises(RuntimeError, match="SHA-256 mismatch"):
        vda_core.load(
            "vda1",
            "crossattn1",
            16,
            checkpoint_path=checkpoint,
            expected_checkpoint_sha256="0" * 64,
        )
    with pytest.raises(ValueError, match="checkpoint iteration is 123"):
        vda_core.load(
            "vda1",
            "crossattn1",
            16,
            checkpoint_path=checkpoint,
            require_iteration=19999,
        )


@pytest.mark.parametrize("feedback", ("crossattn1", "affine_ew"))
def test_stream_factorial_checkpoint_round_trips_through_registered_factory(
    tmp_path, monkeypatch, feedback
):
    checkpoint, original = _stream_factorial_checkpoint(
        tmp_path / "factorial.pt", feedback=feedback
    )
    monkeypatch.setattr(vda_core, "DEVICE", "cpu")
    digest = vda_core.sha256_file(checkpoint)

    loaded, iteration = vda_core.load(
        "vda4",
        feedback,
        16,
        checkpoint_path=checkpoint,
        expected_checkpoint_sha256=digest,
        require_iteration=19999,
    )

    assert iteration == 19999
    assert isinstance(loaded, StreamFactorialModel)
    assert loaded.n_tokens == 100
    assert loaded.effective_visual_streams == 4
    assert loaded.effective_memory_streams == 100
    assert loaded.encoder.feedback == feedback
    assert set(loaded.state_dict()) == set(original.state_dict())
    for key, expected in original.state_dict().items():
        assert torch.equal(loaded.state_dict()[key], expected), key


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda payload: payload["model_factory"].update(kind="unknown"), "unsupported.*kind"),
        (lambda payload: payload["model_factory"].update(carrier_grid=[4, 4]), "carrier_grid"),
        (
            lambda payload: payload["model_factory"].update(effective_visual_streams=16),
            "effective_visual_streams must be 4 or 100",
        ),
    ],
)
def test_stream_factorial_checkpoint_rejects_unregistered_factory(
    tmp_path, monkeypatch, mutation, message
):
    checkpoint, _ = _stream_factorial_checkpoint(tmp_path / "factorial.pt")
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    mutation(payload)
    torch.save(payload, checkpoint)
    monkeypatch.setattr(vda_core, "DEVICE", "cpu")

    with pytest.raises(ValueError, match=message):
        vda_core.load("vda4", "crossattn1", 16, checkpoint_path=checkpoint)
