from __future__ import annotations

import torch

from model import RViTPaperModel
from paper_encoder import RecurrentViTxLSTM
from train_rl import build_arg_parser


MODERN_CELL = "transformer_memory_2layer_softmax_modern"


def _assert_token_simplex(x: torch.Tensor) -> None:
    assert torch.all(x >= 0)
    torch.testing.assert_close(x.sum(dim=-1), torch.ones_like(x[..., 0]))


def test_cli_accepts_distinct_modern_softmax_memory_selector() -> None:
    args = build_arg_parser().parse_args(
        ["--cell", MODERN_CELL, "--feedback", "crossattn1", "--mem-heads", "4"]
    )
    assert args.cell == MODERN_CELL
    assert args.mem_heads == 4


def test_modern_selector_builds_four_head_normalized_gated_memories() -> None:
    encoder = RecurrentViTxLSTM(
        d_token=12,
        d_mem=16,
        n_patch=4,
        feedback="crossattn1",
        cell=MODERN_CELL,
        mem_heads=4,
    )
    h1_prev, h2_prev = encoder.init_states(2)
    (h1, h2), readout, visual_attention = encoder.forward_step(
        torch.randn(2, 4, 12), (h1_prev, h2_prev), return_attn=True
    )

    assert encoder.memory_transformer1.n_heads == 4
    assert encoder.memory_transformer2.n_heads == 4
    assert encoder.memory_transformer1.head_dim == 4
    assert hasattr(encoder.memory_transformer1, "source_norm")
    assert hasattr(encoder.memory_transformer1, "query_key_norm")
    assert hasattr(encoder.memory_transformer1, "W_g")
    _assert_token_simplex(h1_prev)
    _assert_token_simplex(h2_prev)
    _assert_token_simplex(h1)
    _assert_token_simplex(h2)
    torch.testing.assert_close(readout, h2)
    assert visual_attention.shape == (2, 4, 8)


def test_modern_memory_attention_is_scale_stable_and_exposes_gate_routing() -> None:
    torch.manual_seed(7)
    encoder = RecurrentViTxLSTM(
        d_token=12,
        d_mem=16,
        n_patch=4,
        feedback="crossattn1",
        cell=MODERN_CELL,
        mem_heads=4,
    ).eval()
    block = encoder.memory_transformer1
    z = torch.randn(2, 4, 12)
    h, _ = encoder.init_states(2)

    output, attention = block(z, h, return_attn=True)
    scaled_output, scaled_attention = block(10.0 * z, h, return_attn=True)

    assert attention.shape == (2, 4, 4, 8)
    torch.testing.assert_close(
        attention.sum(dim=-1), torch.ones_like(attention[..., 0]), atol=1e-6, rtol=1e-6
    )
    torch.testing.assert_close(scaled_attention, attention, atol=2e-5, rtol=2e-5)
    torch.testing.assert_close(scaled_output, output, atol=2e-5, rtol=2e-5)
    assert block.last_gate.shape == (2, 4, 4, 4)
    assert torch.all((block.last_gate >= 0) & (block.last_gate <= 1))
    assert block.last_source_contribution.shape == (2, 4, 4, 2)
    assert torch.isfinite(block.last_source_contribution).all()


def test_modern_selector_normalizes_visual_and_memory_feedback_sources() -> None:
    encoder = RecurrentViTxLSTM(
        d_token=12,
        d_mem=16,
        n_patch=4,
        feedback="crossattn1",
        cell=MODERN_CELL,
        mem_heads=4,
    )
    assert hasattr(encoder.attn, "visual_norm")
    assert hasattr(encoder.attn, "memory_norm")
    assert hasattr(encoder.attn, "query_key_norm")


def test_modern_model_preserves_dual_jepa_student_softmax_and_exposes_routing() -> None:
    model = RViTPaperModel(
        n_actions=2,
        n_quantiles=5,
        seq_len=3,
        feedback="crossattn1",
        cell=MODERN_CELL,
        mem_heads=4,
        d_mem=16,
        jepa_n_heads=2,
        jepa_proto_dim=7,
    )
    sequence = model.forward_rl_sequence(
        torch.randn(2, 3, 1, 50, 50), return_cell=True, return_attn=True
    )
    student_logits = model.jepa_logits(sequence["cell_seq"])
    student_probabilities = torch.softmax(student_logits, dim=-1)

    assert sequence["cell_seq"].shape == (2, 3, 2, 4, 16)
    assert student_logits.shape == (2, 3, 2, 4, 2, 7)
    torch.testing.assert_close(
        student_probabilities.sum(dim=-1),
        torch.ones_like(student_probabilities[..., 0]),
        atol=1e-6,
        rtol=1e-6,
    )
    assert sequence["memory_attn_seq"].shape == (2, 3, 2, 4, 4, 8)
    assert sequence["memory_gate_seq"].shape == (2, 3, 2, 4, 4, 4)
    assert sequence["memory_source_contribution_seq"].shape == (2, 3, 2, 4, 4, 2)
