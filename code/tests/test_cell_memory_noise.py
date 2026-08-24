"""Tests for explicit Gaussian perturbations of the xLSTM cell state C."""

import math

import numpy as np
import pytest
import torch

from model import RViTPaperModel
from paper_encoder import SpatialXLSTM
from ppo import collect_episodes
from train_rl import build_arg_parser


def _zero_state(batch: int = 2, patches: int = 4, d_mem: int = 8):
    return tuple(torch.zeros(batch, patches, d_mem) for _ in range(4))


def test_zero_memory_noise_preserves_deterministic_xlstm_update():
    torch.manual_seed(11)
    baseline = SpatialXLSTM(input_dim=3, d_mem=8, memory_noise_std=0.0)
    compatible = SpatialXLSTM(input_dim=3, d_mem=8, memory_noise_std=0.0)
    compatible.load_state_dict(baseline.state_dict())
    z = torch.randn(2, 4, 3)
    state = _zero_state()

    expected = baseline(z, *state)
    actual = compatible(z, *state)

    for expected_tensor, actual_tensor in zip(expected, actual):
        torch.testing.assert_close(actual_tensor, expected_tensor)


def test_memory_noise_is_added_after_c_update_and_before_h(monkeypatch):
    torch.manual_seed(12)
    baseline = SpatialXLSTM(input_dim=3, d_mem=8, memory_noise_std=0.0)
    perturbed = SpatialXLSTM(input_dim=3, d_mem=8, memory_noise_std=0.01)
    perturbed.load_state_dict(baseline.state_dict())
    z = torch.randn(2, 4, 3)
    state = _zero_state()
    _, c_clean, n_clean, m_clean = baseline(z, *state)

    monkeypatch.setattr(torch, "randn_like", lambda tensor: torch.full_like(tensor, 2.0))
    h_noisy, c_noisy, n_noisy, m_noisy = perturbed(
        z, *state, inject_memory_noise=True
    )

    torch.testing.assert_close(c_noisy, c_clean + 0.02 * (n_clean + 1e-8))
    torch.testing.assert_close(n_noisy, n_clean)
    torch.testing.assert_close(m_noisy, m_clean)
    with torch.no_grad():
        output_gate = torch.sigmoid(perturbed.W_o(z) + perturbed.R_o(state[0]))
        expected_h = output_gate * (c_noisy / (n_noisy + 1e-8))
    torch.testing.assert_close(h_noisy, expected_h)


def test_memory_noise_requires_explicit_injection_even_in_eval_mode(monkeypatch):
    cell = SpatialXLSTM(input_dim=3, d_mem=8, memory_noise_std=0.01).eval()
    z = torch.zeros(1, 4, 3)
    state = _zero_state(batch=1)

    baseline = SpatialXLSTM(input_dim=3, d_mem=8, memory_noise_std=0.0)
    baseline.load_state_dict(cell.state_dict())
    _, c_clean, n_clean, _ = baseline(z, *state)

    monkeypatch.setattr(
        torch,
        "randn_like",
        lambda tensor: (_ for _ in ()).throw(AssertionError("noise RNG was consumed")),
    )
    _, c_disabled, _, _ = cell(z, *state)
    torch.testing.assert_close(c_disabled, c_clean)

    monkeypatch.setattr(torch, "randn_like", lambda tensor: torch.ones_like(tensor))
    _, c_noisy, _, _ = cell(z, *state, inject_memory_noise=True)
    torch.testing.assert_close(c_noisy, c_clean + 0.01 * (n_clean + 1e-8))


@pytest.mark.parametrize("bad_std", [-0.01, math.inf, math.nan])
def test_memory_noise_rejects_invalid_standard_deviation(bad_std):
    with pytest.raises(ValueError, match="memory_noise_std"):
        SpatialXLSTM(memory_noise_std=bad_std)


def test_memory_noise_cli_reaches_cross_attention_model():
    args = build_arg_parser().parse_args(
        [
            "--task", "luo2015_criterion",
            "--cell", "xlstm",
            "--feedback", "crossattn1",
            "--d-mem", "8",
            "--memory-decay", "1.0",
            "--memory-noise-std", "0.01",
        ]
    )
    model = RViTPaperModel(
        cell=args.cell,
        feedback=args.feedback,
        d_mem=args.d_mem,
        memory_decay=args.memory_decay,
        memory_noise_std=args.memory_noise_std,
    )

    assert args.memory_noise_std == pytest.approx(0.01)
    assert model.encoder.d_mem == 8
    assert model.encoder.memory_noise_std == pytest.approx(0.01)
    assert model.encoder.lstm.memory_noise_std == pytest.approx(0.01)


def test_softmax_head_rejects_xlstm_memory_noise():
    with pytest.raises(ValueError, match="memory_noise_std"):
        RViTPaperModel(cell="softmax_head", d_mem=8, memory_noise_std=0.01)


def test_rollout_explicitly_activates_memory_noise_despite_eval_mode():
    class RecordingModel(torch.nn.Module):
        n_quantiles = 2
        seq_len = 1

        def __init__(self):
            super().__init__()
            self.inject_flags = []

        def init_states(self, batch_size, device):
            return None

        def rl_step(self, x_t, states, inject_memory_noise=False):
            self.inject_flags.append(inject_memory_noise)
            return {
                "new_states": None,
                "actor_logits": torch.zeros(1, 2, device=x_t.device),
                "V_scalar": torch.zeros(1, device=x_t.device),
                "V_dist": torch.zeros(1, self.n_quantiles, device=x_t.device),
            }

    class OneStepEnv:
        observation = np.zeros((50, 50, 3), dtype=np.float32)

        def reset(self):
            return self.observation

        def step(self, action):
            return self.observation, 1.0, True, {}

    model = RecordingModel()
    collect_episodes(model, OneStepEnv(), n_episodes=1, device=torch.device("cpu"))

    assert model.training is False
    assert model.inject_flags == [True]
