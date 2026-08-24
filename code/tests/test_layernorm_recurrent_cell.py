import torch

from model import RViTPaperModel
from paper_encoder import LayerNormDecayLSTM, RecurrentViTxLSTM
from train_rl import build_arg_parser


def test_layernorm_decay_cell_carries_only_h_and_c_with_exact_decay():
    cell = LayerNormDecayLSTM(
        input_dim=3,
        d_mem=4,
        memory_decay=0.01,
        memory_noise_std=0.0,
    )
    with torch.no_grad():
        for parameter in cell.parameters():
            parameter.zero_()
        cell.state_norm.weight.fill_(1.0)

    z = torch.zeros(2, 4, 3)
    h_prev = torch.zeros(2, 4, 4)
    c_prev = torch.tensor([1.0, 2.0, 3.0, 4.0]).view(1, 1, 4).expand(2, 4, 4)
    h, c = cell(z, h_prev, c_prev)

    # With zero logits, F=0.5 and U=0, so only 0.01 * 0.5 of C_prev remains.
    torch.testing.assert_close(c, 0.005 * c_prev)
    assert h.shape == c.shape == (2, 4, 4)
    assert torch.isfinite(h).all()


def test_layernorm_recurrent_encoder_state_has_no_n_or_m_tensors():
    encoder = RecurrentViTxLSTM(
        d_token=6,
        d_mem=8,
        n_patch=4,
        feedback="crossattn1",
        cell="layernorm_lstm",
        memory_decay=0.01,
        memory_noise_std=0.05,
    )
    state = encoder.init_states(batch_size=2)
    assert len(state) == 2
    assert all(value.shape == (2, 4, 8) for value in state)

    x = torch.randn(2, 4, 6)
    next_state, readout, _ = encoder.forward_step(
        x,
        state,
        inject_memory_noise=True,
    )
    assert len(next_state) == 2
    assert readout.shape == (2, 4, 8)
    assert all(torch.isfinite(value).all() for value in next_state)


def test_layernorm_memory_noise_uses_instantaneous_state_scale():
    cell = LayerNormDecayLSTM(
        input_dim=3,
        d_mem=4,
        memory_decay=0.01,
        memory_noise_std=0.05,
    )
    with torch.no_grad():
        for parameter in cell.parameters():
            parameter.zero_()
        cell.state_norm.weight.fill_(1.0)

    z = torch.zeros(1, 1, 3)
    h_prev = torch.zeros(1, 1, 4)
    c_prev = torch.zeros(1, 1, 4)
    torch.manual_seed(123)
    expected_noise = torch.randn_like(c_prev)
    torch.manual_seed(123)
    _, c = cell(z, h_prev, c_prev, inject_memory_noise=True)
    expected = 0.05 * (cell.state_norm.eps ** 0.5) * expected_noise
    torch.testing.assert_close(c, expected)


def test_cli_and_full_model_accept_layernorm_lstm_doubled_frames():
    args = build_arg_parser().parse_args(
        [
            "--cell", "layernorm_lstm",
            "--T", "7",
            "--frame-repeat", "2",
            "--memory-decay", "0.01",
            "--memory-noise-std", "0.05",
        ]
    )
    assert args.cell == "layernorm_lstm"
    assert args.T == 7
    assert args.frame_repeat == 2
    assert args.memory_decay == 0.01

    model = RViTPaperModel(
        seq_len=14,
        frame_repeat=2,
        feedback="crossattn1",
        cell="layernorm_lstm",
        d_mem=8,
        memory_decay=0.01,
        memory_noise_std=0.05,
        conv_frontend=True,
        grid_rows=4,
        grid_cols=4,
        image_size=100,
    )
    state, timestep = model.init_states(batch_size=1)
    assert timestep == 0
    assert len(state) == 2
    output = model.rl_step(
        torch.zeros(1, 100, 100, 3),
        (state, timestep),
        inject_memory_noise=True,
    )
    next_state, next_timestep = output["new_states"]
    assert len(next_state) == 2
    assert next_timestep == 1
    assert torch.isfinite(output["actor_logits"]).all()


def test_existing_xlstm_state_shape_is_unchanged():
    encoder = RecurrentViTxLSTM(
        d_token=6,
        d_mem=8,
        n_patch=4,
        feedback="crossattn1",
        cell="xlstm",
    )
    state = encoder.init_states(batch_size=1)
    assert len(state) == 4
