"""Regression tests for the 20x20/no-decay/noisy-memory Luo experiment."""
from __future__ import annotations

import sys
from pathlib import Path

import torch

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from conv_frontend import ConvPatchFrontEnd  # noqa: E402
from model import RViTPaperModel  # noqa: E402
from paper_encoder import SpatialXLSTM  # noqa: E402


def test_grid20_partitions_the_unchanged_50px_scene_once_per_pixel():
    front = ConvPatchFrontEnd(grid_rows=20, grid_cols=20, image_size=50)
    coverage = torch.zeros(50, 50, dtype=torch.int64)
    shapes = set()
    for r0, r1, c0, c1 in front._bounds:
        coverage[r0:r1, c0:c1] += 1
        shapes.add((r1 - r0, c1 - c0))

    assert len(front._bounds) == 400
    assert shapes == {(2, 2), (2, 3), (3, 2), (3, 3)}
    assert torch.equal(coverage, torch.ones_like(coverage))


def test_grid20_cross_attention_has_400_visual_and_memory_tokens_at_dmem32():
    model = RViTPaperModel(
        n_actions=2,
        n_quantiles=5,
        seq_len=7,
        feedback="crossattn1",
        cell="xlstm",
        jepa_n_heads=4,
        jepa_proto_dim=256,
        d_mem=32,
        memory_decay=1.0,
        memory_noise_std=0.01,
        conv_frontend=True,
        grid_rows=20,
        grid_cols=20,
        image_size=50,
    )

    state = model.init_states(1)
    assert model.n_tokens == 400
    assert model.front.token_dim == 128 + 400 + 8
    assert model.encoder.readout_dim == 400 * 32
    assert all(tensor.shape == (1, 400, 32) for tensor in state[0])

    output = model.rl_step(
        torch.randn(1, 3, 50, 50),
        state,
        return_attn=True,
        inject_memory_noise=True,
    )
    assert output["attn"][0].shape == (1, 400, 800)
    assert output["actor_logits"].shape == (1, 2)
    assert output["critic_q_dist"].shape == (1, 2, 5)


def test_every_memory_scalar_receives_its_own_noise_draw(monkeypatch):
    torch.manual_seed(20260728)
    clean = SpatialXLSTM(input_dim=3, d_mem=32, memory_decay=1.0, memory_noise_std=0.0)
    noisy = SpatialXLSTM(input_dim=3, d_mem=32, memory_decay=1.0, memory_noise_std=0.01)
    noisy.load_state_dict(clean.state_dict())
    z = torch.randn(1, 400, 3)
    state = tuple(torch.zeros(1, 400, 32) for _ in range(4))
    _, c_clean, n_clean, _ = clean(z, *state)

    independent_draws = torch.arange(c_clean.numel(), dtype=c_clean.dtype).reshape_as(c_clean)
    monkeypatch.setattr(torch, "randn_like", lambda tensor: independent_draws.to(tensor))
    _, c_noisy, _, _ = noisy(z, *state, inject_memory_noise=True)

    expected_delta = 0.01 * (n_clean + 1e-8) * independent_draws
    torch.testing.assert_close(c_noisy - c_clean, expected_delta)
