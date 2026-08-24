from __future__ import annotations

import torch

from model import RViTPaperModel


def _make_model(fsq_levels: int = 2) -> RViTPaperModel:
    return RViTPaperModel(
        n_actions=2, n_quantiles=1,
        cell="transformer_memory_2layer_softmax_modern",
        feedback="crossattn1",
        d_mem=128, mem_heads=4,
        n_patch=4, d_token=128,
        jepa_n_heads=4, jepa_proto_dim=16,
        conv_frontend=True,
        grid_rows=2, grid_cols=2, image_size=50,
    )


def test_fsq_produces_discrete_memory_outputs():
    torch.manual_seed(42)
    model = _make_model(fsq_levels=2)
    model.encoder.fsq_levels = 2
    model.eval()
    with torch.no_grad():
        obs = torch.randn(1, 3, 3, 50, 50)  # (B,T,C,H,W)
        out = model.forward_rl_sequence(obs, return_cell=True)
    H2 = out["cell_seq"][:, :, 1]  # (B, T, 4, 128)
    # With levels=2 every coordinate should be 0.0 or 1.0.
    assert H2.shape == (1, 3, 4, 128)
    unique_vals = set(torch.round(H2.flatten(), decimals=6).tolist())
    assert unique_vals <= {0.0, 1.0}, f"got non-binary values: {unique_vals}"


def test_fsq_disabled_falls_back_to_softmax():
    torch.manual_seed(42)
    model = _make_model(fsq_levels=1)
    model.eval()
    with torch.no_grad():
        obs = torch.randn(1, 3, 3, 50, 50)
        out = model.forward_rl_sequence(obs, return_cell=True)
    H2 = out["cell_seq"][:, :, 1]  # (B, T, 4, 128)
    # Softmax output: sums to 1 per token, values in (0,1).
    sums = H2.sum(dim=-1)
    assert torch.allclose(sums, torch.ones_like(sums), atol=1e-6)
    # Should NOT be all binary.
    unique_vals = set(torch.round(H2.flatten(), decimals=6).tolist())
    assert not unique_vals <= {0.0, 1.0}


def test_fsq_gradient_flows_to_encoder():
    model = _make_model(fsq_levels=2)
    model.encoder.fsq_levels = 2
    obs = torch.randn(1, 2, 3, 50, 50)
    out = model.forward_rl_sequence(obs, return_cell=True)
    H2 = out["cell_seq"][:, :, 1]
    H2.square().sum().backward()
    # Encoder parameters should have non-zero gradients.
    enc_grads = [p.grad for p in model.encoder.parameters() if p.grad is not None]
    assert len(enc_grads) > 0
    assert any(g.abs().sum() > 0 for g in enc_grads)


def test_fsq_five_levels():
    torch.manual_seed(7)
    model = _make_model(fsq_levels=5)
    model.encoder.fsq_levels = 5
    model.eval()
    with torch.no_grad():
        obs = torch.randn(1, 3, 3, 50, 50)
        out = model.forward_rl_sequence(obs, return_cell=True)
    H2 = out["cell_seq"][:, :, 1]
    allowed = {0.0, 0.25, 0.5, 0.75, 1.0}
    for val in torch.round(H2.flatten(), decimals=6).tolist():
        assert min(abs(val - a) for a in allowed) < 1e-7
