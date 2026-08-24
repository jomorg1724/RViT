"""VDA4 cross-attention experiment with explicit xLSTM cell-memory decay."""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import pytest
import torch

_ENGINE_ROOT = Path(__file__).resolve().parents[1]
_WORKSPACE_ROOT = _ENGINE_ROOT.parent
if str(_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_ENGINE_ROOT))

from model import RViTPaperModel  # noqa: E402
from paper_encoder import ElementwiseAffineSelfAttention, SpatialXLSTM  # noqa: E402
from train_rl import _producer_hashes, build_arg_parser  # noqa: E402


def test_spatial_xlstm_decays_only_carried_cell_content_before_new_write():
    torch.manual_seed(7)
    decay = 0.80
    cell = SpatialXLSTM(input_dim=3, d_mem=2, memory_decay=decay)
    Z = torch.randn(1, 4, 3)
    H_prev = torch.randn(1, 4, 2)
    C_prev = torch.randn(1, 4, 2)
    N_prev = torch.rand(1, 4, 2)
    M_prev = torch.randn(1, 4, 2)

    H, C, N, M = cell(Z, H_prev, C_prev, N_prev, M_prev)

    i_tilde = cell.W_i(Z) + cell.R_i(H_prev)
    f_tilde = cell.W_f(Z) + cell.R_f(H_prev)
    o_tilde = cell.W_o(Z) + cell.R_o(H_prev)
    u_tilde = cell.W_u(Z) + cell.R_z(H_prev)
    expected_M = torch.maximum(f_tilde + M_prev, i_tilde)
    expected_I = torch.exp(i_tilde - expected_M)
    expected_F = torch.exp(f_tilde + M_prev - expected_M)
    expected_U = torch.tanh(u_tilde)
    expected_N = expected_F * N_prev + expected_I
    expected_C = decay * (expected_F * C_prev) + expected_I * expected_U
    expected_H = torch.sigmoid(o_tilde) * (expected_C / (expected_N + 1e-8))

    assert torch.allclose(M, expected_M)
    assert torch.allclose(N, expected_N)
    assert torch.allclose(C, expected_C)
    assert torch.allclose(H, expected_H)


@pytest.mark.parametrize("bad_decay", [-0.01, 1.01])
def test_spatial_xlstm_rejects_memory_decay_outside_closed_unit_interval(bad_decay):
    with pytest.raises(ValueError, match="memory_decay"):
        SpatialXLSTM(memory_decay=bad_decay)


def test_memory_decay_cli_reaches_four_patch_cross_attention_model():
    args = build_arg_parser().parse_args(
        ["--task", "vda4", "--cell", "xlstm", "--feedback", "crossattn1",
         "--memory-decay", "0.80"]
    )
    assert args.memory_decay == pytest.approx(0.80)

    model = RViTPaperModel(
        feedback=args.feedback,
        cell=args.cell,
        memory_decay=args.memory_decay,
        d_mem=128,
        conv_frontend=True,
        grid_rows=2,
        grid_cols=2,
        image_size=50,
    )
    assert model.n_tokens == 4
    assert model.encoder.memory_decay == pytest.approx(0.80)
    assert model.encoder.lstm.memory_decay == pytest.approx(0.80)
    assert model.encoder.two_lstm is False

    state = model.init_states(1)
    output = model.rl_step(torch.randn(1, 3, 50, 50), state, return_attn=True)
    assert output["new_states"][0][0].shape == (1, 4, 128)
    assert output["attn"][0].shape == (1, 4, 8)


def test_memory_decay_experiment_launcher_is_top_level_isolated_and_fully_specified():
    experiment_dir = _WORKSPACE_ROOT / "VDA4_memory_decay" / "c_decay_080_crossattn1"
    launcher = experiment_dir / "launch_20k.sh"
    readme = experiment_dir / "README.md"

    content = launcher.read_text(encoding="utf-8")
    assert readme.is_file()
    assert 'source "$WORKSPACE_ROOT/.venv/bin/activate"' in content
    assert 'mkdir "$CHECKPOINT_DIR"' in content
    assert '--checkpoint-dir "$CHECKPOINT_DIR"' in content
    assert "uuid.uuid4().hex" in content
    for expected in (
        "--task vda4",
        "--patch-grid-rows 2",
        "--patch-grid-cols 2",
        "--cell xlstm",
        "--feedback crossattn1",
        "--memory-decay 0.80",
        '--experiment-launcher "$WORKSPACE_ROOT/VDA4_memory_decay/c_decay_080_crossattn1/launch_20k.sh"',
        "--conv-frontend",
        "--jepa-coef 0.5",
        "--d-mem 128",
        "--curriculum",
        "--init-mode fresh",
        "--iters 20000",
        "--schedule-final-iteration 19999",
        "--episodes-per-iter 8",
        "--save-every 50",
        "--log-every 1",
        "--seed 0",
        "--device mps",
    ):
        assert expected in content

    hashes = _producer_hashes(experiment_launcher=str(launcher))
    assert hashes["experiment_launcher"] == hashlib.sha256(launcher.read_bytes()).hexdigest()


def test_affine_ew_memory_decay_project_is_matched_and_fully_specified():
    experiment_dir = _WORKSPACE_ROOT / "VDA4_memory_decay" / "c_decay_080_affine_ew"
    launcher = experiment_dir / "launch_20k.sh"
    readme = experiment_dir / "README.md"

    assert readme.is_file()
    assert launcher.is_file()
    content = launcher.read_text(encoding="utf-8")
    specification = readme.read_text(encoding="utf-8")
    assert 'source "$WORKSPACE_ROOT/.venv/bin/activate"' in content
    assert 'mkdir "$CHECKPOINT_DIR"' in content
    assert '--checkpoint-dir "$CHECKPOINT_DIR"' in content
    assert "uuid.uuid4().hex" in content
    assert "vda4_affine_ew_cdecay080_d128_replay_excluded_seed0_" in content
    for expected in (
        "--task vda4",
        "--T 7",
        "--min-change-time 5",
        "--max-change-time 5",
        "--patch-grid-rows 2",
        "--patch-grid-cols 2",
        "--cell xlstm",
        "--feedback affine_ew",
        "--memory-decay 0.80",
        '--experiment-launcher "$WORKSPACE_ROOT/VDA4_memory_decay/c_decay_080_affine_ew/launch_20k.sh"',
        "--conv-frontend",
        "--jepa-coef 0.5",
        "--d-mem 128",
        "--curriculum",
        "--init-mode fresh",
        "--iters 20000",
        "--schedule-final-iteration 19999",
        "--episodes-per-iter 8",
        "--save-every 50",
        "--log-every 1",
        "--seed 0",
        "--device mps",
    ):
        assert expected in content
    assert "X' = gamma * X + beta" in specification
    assert "C_t = 0.80 * (F_t * C_{t-1}) + I_t * U_t" in specification

    args = build_arg_parser().parse_args(
        ["--task", "vda4", "--cell", "xlstm", "--feedback", "affine_ew",
         "--memory-decay", "0.80"]
    )
    model = RViTPaperModel(
        feedback=args.feedback,
        cell=args.cell,
        memory_decay=args.memory_decay,
        d_mem=128,
        conv_frontend=True,
        grid_rows=2,
        grid_cols=2,
        image_size=50,
    )
    assert model.n_tokens == 4
    assert model.encoder.memory_decay == pytest.approx(0.80)
    assert model.encoder.lstm.memory_decay == pytest.approx(0.80)
    assert isinstance(model.encoder.attn, ElementwiseAffineSelfAttention)
    state = model.init_states(1)
    output = model.rl_step(torch.randn(1, 3, 50, 50), state, return_attn=True)
    assert output["new_states"][0][0].shape == (1, 4, 128)
    assert output["attn"][0].shape == (1, 4, 4)

    hashes = _producer_hashes(experiment_launcher=str(launcher))
    assert hashes["experiment_launcher"] == hashlib.sha256(launcher.read_bytes()).hexdigest()
