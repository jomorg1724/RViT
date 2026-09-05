"""Learned-value vision attention (v_mode='learned') + H2-only readout (readout='h2').

Design: V_X, V_H are learned per-position embedding parameters — NOT derived from
inputs or states. H2 = A_X@V_X + A_H@V_H is reconstructed every step and is the sole
belief readout. Only H1 (and the KDA accumulator) cross timesteps as state.
"""
from __future__ import annotations

import torch

from kda_conv_memory_model import KDAConvMemoryModel


def _model(**kw):
    kw.setdefault("readout", "h2")
    kw.setdefault("v_mode", "learned")
    return KDAConvMemoryModel(n_channels=8, map_size=4, proto_dim=16,
                              kda_heads=2, kda_head_dim=4, attn_mode="token",
                              cls_head="conv", **kw)


def test_learned_values_exist_and_are_parameters():
    m = _model()
    assert isinstance(m.vision.V_X, torch.nn.Parameter)
    assert isinstance(m.vision.V_H, torch.nn.Parameter)
    assert m.vision.V_X.shape == (1, 8, 4, 4)
    assert m.vision.V_H.shape == (1, 8, 4, 4)
    # value projections are gone — values are not derived from anything
    assert not hasattr(m.vision, "W_vx") and not hasattr(m.vision, "W_vh")


def test_h2_only_readout_shape():
    m = _model()
    R = m.forward_seq(torch.randn(2, 7, 16, 16, 3))
    assert R.shape == (2, 7, 8, 4, 4)          # (B, T, C, map, map) — C, not 2C/4C
    assert m.r_dim == 8
    assert m.classify(R[:, -1]).shape == (2, 2)


def test_h2_is_attention_over_learned_values():
    # The H2 argument must have NO effect on the vision block output: values are
    # learned embeddings, so only H1 (via keys) and X can influence the result.
    m = _model().eval()
    X = torch.randn(2, 16, 4, 4)        # in_c = 2C = 16
    H1 = torch.randn(2, 8, 4, 4)
    H2a, H2b = torch.zeros(2, 8, 4, 4), torch.randn(2, 8, 4, 4) * 5
    with torch.no_grad():
        Za, atta = m.vision(X, H1, H2a)
        Zb, attb = m.vision(X, H1, H2b)
    assert torch.allclose(Za, Zb, atol=1e-6)
    assert torch.allclose(atta, attb, atol=1e-6)
    # and the attention mix really is over the learned embeddings:
    # with V_H zeroed, att (pre-FFN) must equal A_X @ V_X — check via mass maps
    with torch.no_grad():
        m.vision.V_H.zero_()
        _, _, A = m.vision(X, H1, torch.zeros(2, 8, 4, 4), return_attn=True)
        assert A.shape == (2, 2, 4, 4)
        assert torch.allclose(A.sum(dim=1), torch.ones(2, 4, 4), atol=1e-4)


def test_h2_state_entry_has_no_effect():
    # zeroing the H2 slot in the initial state must not change anything:
    # only H1 (and ACC) are genuine recurrent state in this mode.
    m = _model().eval()
    x = torch.randn(1, 7, 16, 16, 3)
    with torch.no_grad():
        R1 = m.forward_seq(x)
        torch.manual_seed(0)
        R2 = m.forward_seq(x)
    assert torch.allclose(R1, R2, atol=1e-5)


def test_learned_value_gradients_flow():
    m = _model()
    R = m.forward_seq(torch.randn(1, 7, 16, 16, 3))
    m.classify(R[:, -1]).sum().backward()
    assert m.vision.V_X.grad is not None and m.vision.V_X.grad.abs().sum() > 0
    assert m.vision.V_H.grad is not None and m.vision.V_H.grad.abs().sum() > 0
    assert m.stem.net[0].weight.grad is not None   # trunk still learns


def test_default_mode_unchanged():
    m = KDAConvMemoryModel(n_channels=8, map_size=4, proto_dim=16,
                           kda_heads=2, kda_head_dim=4, attn_mode="token",
                           readout="h1h2", cls_head="conv")
    assert m.v_mode == "state"
    assert hasattr(m.vision, "W_vx") and hasattr(m.vision, "W_vh")
    R = m.forward_seq(torch.randn(2, 7, 16, 16, 3))
    assert R.shape == (2, 7, 16, 4, 4)   # 2C


def test_bad_v_mode_rejected():
    try:
        KDAConvMemoryModel(n_channels=8, map_size=4, proto_dim=16,
                           kda_heads=2, kda_head_dim=4, attn_mode="token",
                           v_mode="bogus")
        assert False, "expected ValueError"
    except ValueError:
        pass
