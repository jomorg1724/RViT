from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import torch

from model import RViTPaperModel
from paper_encoder import (
    CrossAttentionTransformerMemory,
    CrossAttentionXH,
    RecurrentViTxLSTM,
)
from train_rl import build_arg_parser


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "vda4_transformer_memory"
    / "grid2x2_crossattn1_seed0_v1"
)


def test_cli_accepts_transformer_memory_cell() -> None:
    args = build_arg_parser().parse_args(
        ["--task", "vda4", "--cell", "transformer_memory", "--feedback", "crossattn1"]
    )

    assert args.cell == "transformer_memory"
    assert args.feedback == "crossattn1"


def test_memory_transformer_queries_h_and_jointly_attends_h_then_z() -> None:
    memory = CrossAttentionTransformerMemory(d_token=6, d_mem=8, n_heads=2, dropout=0.0)
    h_prev = torch.randn(2, 4, 8, requires_grad=True)
    z = torch.randn(2, 4, 6, requires_grad=True)

    h_new, attention = memory(z, h_prev, return_attn=True)

    assert h_new.shape == (2, 4, 8)
    assert attention.shape == (2, 2, 4, 8)
    torch.testing.assert_close(attention.sum(dim=-1), torch.ones(2, 2, 4))
    h_new.square().mean().backward()
    assert h_prev.grad is not None and torch.count_nonzero(h_prev.grad) > 0
    assert z.grad is not None and torch.count_nonzero(z.grad) > 0


def test_memory_transformer_requires_head_divisibility() -> None:
    with pytest.raises(ValueError, match="divisible"):
        CrossAttentionTransformerMemory(d_token=6, d_mem=7, n_heads=2)


def test_encoder_uses_crossattn1_vision_and_h_only_transformer_memory() -> None:
    encoder = RecurrentViTxLSTM(
        d_token=6,
        d_mem=8,
        n_patch=4,
        feedback="crossattn1",
        cell="transformer_memory",
        mem_heads=2,
    )
    state = encoder.init_states(2)

    assert isinstance(encoder.attn, CrossAttentionXH)
    assert isinstance(encoder.memory_transformer, CrossAttentionTransformerMemory)
    assert len(state) == 1
    assert state[0].shape == (2, 4, 8)

    next_state, h_new, vision_attention = encoder.forward_step(
        torch.randn(2, 4, 6), state, return_attn=True
    )

    assert len(next_state) == 1
    torch.testing.assert_close(next_state[0], h_new)
    assert vision_attention.shape == (2, 4, 8)


def test_transformer_memory_initializes_distinct_learned_query_slots() -> None:
    encoder = RecurrentViTxLSTM(
        d_token=6,
        d_mem=8,
        n_patch=4,
        feedback="crossattn1",
        cell="transformer_memory",
        mem_heads=2,
    )

    (initial_h,) = encoder.init_states(3)

    assert isinstance(encoder.initial_memory, torch.nn.Parameter)
    torch.testing.assert_close(initial_h[0], initial_h[1])
    assert not torch.allclose(initial_h[:, 0], initial_h[:, 1])
    assert not torch.allclose(initial_h[:, 1], initial_h[:, 2])


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"feedback": "film"}, "requires feedback='crossattn1'"),
        ({"two_lstm": True}, "single H-only state"),
        ({"memory_decay": 0.9}, "memory_decay=1.0"),
        ({"memory_noise_std": 0.1}, "memory_noise_std=0.0"),
    ],
)
def test_transformer_memory_rejects_inapplicable_recurrent_options(overrides, message) -> None:
    kwargs = dict(
        d_token=6,
        d_mem=8,
        n_patch=4,
        feedback="crossattn1",
        cell="transformer_memory",
        mem_heads=2,
    )
    kwargs.update(overrides)
    with pytest.raises(ValueError, match=message):
        RecurrentViTxLSTM(**kwargs)


def test_actor_value_and_jepa_read_the_transformer_memory_state() -> None:
    model = RViTPaperModel(
        n_actions=2,
        n_quantiles=5,
        seq_len=3,
        feedback="crossattn1",
        cell="transformer_memory",
        mem_heads=2,
        d_mem=8,
        jepa_n_heads=2,
        jepa_proto_dim=4,
    )
    video = torch.randn(2, 3, 1, 50, 50)

    sequence = model.forward_rl_sequence(video, return_cell=True, return_attn=True)

    assert sequence["actor_logits_seq"].shape == (2, 3, 2)
    assert sequence["V_scalar_seq"].shape == (2, 3)
    assert sequence["cell_seq"].shape == (2, 3, 4, 8)
    assert sequence["attn_seq"].shape == (2, 3, 4, 8)
    assert model.jepa_logits(sequence["cell_seq"]).shape == (2, 3, 4, 2, 4)


def test_local_vda4_manifest_freezes_the_new_architecture_and_standard_task() -> None:
    manifest = json.loads((EXPERIMENT / "design_manifest.json").read_text(encoding="utf-8"))

    assert manifest["status"] == "local_seed0_experiment_registered"
    assert manifest["task_contract"] == {
        "task": "vda4",
        "active_items": 4,
        "timeline_frames": 7,
        "change_time": 5,
        "sensory_noise_std": 5.0,
        "signed_change_sampling": "uniform(-theta,+theta)",
        "action_semantics": "0=wait, 1=declare; sampled policy",
    }
    assert manifest["architecture"] == {
        "visual_feedback": "crossattn1: Q=X; K/V=[X,H_prev]; residual=X",
        "memory": "single transformer: Q=H_prev; K/V=[H_prev,Z]; residual=H_prev; H-only state",
        "initial_memory": "learned slot-distinct H0 tokens",
        "memory_key_order": ["H_prev", "Z"],
        "patch_grid": [2, 2],
        "tokens": 4,
        "d_mem": 128,
        "memory_heads": 4,
        "actor_and_value_source": "H",
        "visual_feedback_source": "H",
        "jepa_teacher": "EMA teacher over H with temporal t-to-t+1 distillation",
    }
    assert manifest["training"]["iterations"] == 20_000
    assert manifest["training"]["seed"] == 0
    assert manifest["training"]["device"] == "local_cuda"


def test_local_launcher_is_explicit_and_contains_no_runpod_path() -> None:
    launcher = (EXPERIMENT / "launch_local_v1.sh").read_text(encoding="utf-8")
    normalized = re.sub(r"\\\s*\n\s*", " ", launcher)

    for required in (
        "--task vda4",
        "--cell transformer_memory",
        "--feedback crossattn1",
        "--d-mem 128",
        "--mem-heads 4",
        "--memory-noise-std 0.0",
        "--conv-frontend",
        "--jepa-coef 0.5",
        "--jepa-heads 4",
        "--iters \"$ITERS\"",
        "--device \"$DEVICE\"",
    ):
        assert required in normalized
    assert "RUN_ROOT" in launcher
    assert "runpod" not in launcher.lower()
    assert "/workspace" not in launcher


def test_local_launcher_converts_msys_paths_for_native_windows_python() -> None:
    launcher = (EXPERIMENT / "launch_local_v1.sh").read_text(encoding="utf-8")

    assert "PY_PROJECT_ROOT" in launcher
    assert "cygpath -w" in launcher
    assert '"$PY_PROJECT_ROOT/train_rl.py"' in launcher
    assert '"$PY_LAUNCHER"' in launcher
