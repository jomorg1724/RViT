from __future__ import annotations

import copy
import hashlib
from pathlib import Path

import pytest

from model import RViTPaperModel
from train_rl import (
    STREAM_FACTORIAL_KIND,
    _persist_model_factory_metadata,
    _producer_hashes,
    _validate_checkpoint_model_factory,
    build_arg_parser,
    build_training_model,
    resolve_stream_factorial_model_factory,
)

from experiments.vda_stream_factorial.stream_model import StreamFactorialModel


ROOT = Path(__file__).resolve().parents[2]
EXACT_FACTORY = {
    "kind": STREAM_FACTORIAL_KIND,
    "effective_visual_streams": 4,
    "effective_memory_streams": 100,
    "carrier_grid": [10, 10],
}


def valid_args():
    return build_arg_parser().parse_args(
        [
            "--task", "vda4",
            "--patch-grid-rows", "10",
            "--patch-grid-cols", "10",
            "--conv-frontend",
            "--cell", "xlstm",
            "--feedback", "crossattn1",
            "--d-mem", "128",
            "--memory-decay", "1.0",
            "--effective-visual-streams", "4",
            "--effective-memory-streams", "100",
        ]
    )


def model_kwargs():
    return {
        "n_actions": 2,
        "n_quantiles": 5,
        "init_action_bias": [0.0, -1.5],
        "seq_len": 7,
        "feedback": "crossattn1",
        "two_lstm": False,
        "cell": "xlstm",
        "mem_heads": 4,
        "vae_in_channels": 1,
        "jepa_n_heads": 4,
        "jepa_proto_dim": 256,
        "frame_repeat": 1,
        "d_mem": 128,
        "memory_decay": 1.0,
        "memory_noise_std": 0.0,
        "conv_frontend": True,
        "grid_rows": 10,
        "grid_cols": 10,
        "image_size": 50,
    }


def test_cli_stream_flags_are_paired_and_emit_exact_versioned_factory():
    args = valid_args()
    assert resolve_stream_factorial_model_factory(
        args, grid_rows=10, grid_cols=10
    ) == EXACT_FACTORY

    missing_memory = copy.copy(args)
    missing_memory.effective_memory_streams = None
    with pytest.raises(ValueError, match="must be provided together"):
        resolve_stream_factorial_model_factory(
            missing_memory, grid_rows=10, grid_cols=10
        )

    inactive = build_arg_parser().parse_args(["--task", "vda4"])
    assert resolve_stream_factorial_model_factory(
        inactive, grid_rows=2, grid_cols=2
    ) is None


@pytest.mark.parametrize(
    "field,value,grid,match",
    [
        ("task", "vda16", (10, 10), "--task vda4"),
        (None, None, (4, 4), "--patch-grid-rows 10"),
        ("conv_frontend", False, (10, 10), "--conv-frontend"),
        ("cell", "layernorm_lstm", (10, 10), "--cell xlstm"),
        ("two_lstm", True, (10, 10), "one xLSTM"),
        ("d_mem", 64, (10, 10), "--d-mem 128"),
        ("feedback", "film", (10, 10), "--feedback crossattn1"),
        ("memory_decay", 0.8, (10, 10), "--memory-decay 1.0"),
    ],
)
def test_stream_factorial_contract_fails_closed(field, value, grid, match):
    args = copy.copy(valid_args())
    if field is not None:
        setattr(args, field, value)
    with pytest.raises(ValueError, match=match):
        resolve_stream_factorial_model_factory(
            args, grid_rows=grid[0], grid_cols=grid[1]
        )


def test_model_factory_constructs_stream_model_and_preserves_ordinary_path():
    stream = build_training_model(model_kwargs(), EXACT_FACTORY)
    assert isinstance(stream, StreamFactorialModel)
    assert stream.effective_visual_streams == 4
    assert stream.effective_memory_streams == 100
    assert stream.n_tokens == 100
    assert sum(parameter.numel() for parameter in stream.parameters()) == 8_682_948

    ordinary_kwargs = model_kwargs()
    ordinary = build_training_model(ordinary_kwargs)
    assert type(ordinary) is RViTPaperModel
    assert ordinary.n_tokens == 100


def test_stream_factory_metadata_is_persisted_exactly_in_both_contracts():
    resume_contract = {"task": "vda4"}
    checkpoint_metadata = {"resume_contract": resume_contract}
    _persist_model_factory_metadata(
        resume_contract, checkpoint_metadata, EXACT_FACTORY
    )
    assert resume_contract["model_factory"] == EXACT_FACTORY
    assert checkpoint_metadata["model_factory"] == EXACT_FACTORY
    assert set(resume_contract["model_factory"]) == set(EXACT_FACTORY)
    assert set(checkpoint_metadata["model_factory"]) == set(EXACT_FACTORY)

    ordinary_resume = {"task": "vda4"}
    ordinary_checkpoint = {"resume_contract": ordinary_resume}
    _persist_model_factory_metadata(ordinary_resume, ordinary_checkpoint, None)
    assert "model_factory" not in ordinary_resume
    assert "model_factory" not in ordinary_checkpoint


def test_checkpoint_factory_identity_cannot_cross_same_shape_conditions():
    _validate_checkpoint_model_factory({"model_factory": EXACT_FACTORY}, EXACT_FACTORY)
    mismatched = {**EXACT_FACTORY, "effective_visual_streams": 100}
    with pytest.raises(ValueError, match="model_factory mismatch"):
        _validate_checkpoint_model_factory(
            {"model_factory": mismatched}, EXACT_FACTORY
        )
    with pytest.raises(ValueError, match="requested model path"):
        _validate_checkpoint_model_factory({"model_factory": EXACT_FACTORY}, None)


def test_stream_producer_hashes_include_factory_sources_only_when_active():
    ordinary = _producer_hashes()
    stream = _producer_hashes(model_factory=EXACT_FACTORY)
    expected_paths = (
        "experiments/vda_stream_factorial/stream_model.py",
        "experiments/vda_stream_factorial/design_matrix.py",
        "experiments/vda_stream_factorial/design_manifest.json",
        "experiments/vda_stream_factorial/preflight_contract_v1.py",
    )
    for relative in expected_paths:
        assert relative not in ordinary
        assert stream[relative] == hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
