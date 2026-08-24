"""Mechanics tests for the fully-convolutional recurrent ViT."""
from __future__ import annotations

import os
import sys

import torch

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from model import (ConvStem, ConvAttention2D, ConvLSTMCell, ConvRViTModel,  # noqa: E402
                   C_GRID, GRID)


def test_stem_reduces_50_to_10():
    s = ConvStem(3, C_GRID)
    y = s(torch.randn(2, 3, 50, 50))
    assert y.shape == (2, C_GRID, GRID, GRID) == (2, 64, 10, 10)


def test_conv_attention_shape_and_spatial_softmax():
    a = ConvAttention2D(C_GRID)
    X = torch.randn(2, C_GRID, 10, 10)
    H = torch.randn(2, C_GRID, 10, 10)
    Z, attn = a(X, H, return_attn=True)
    assert Z.shape == X.shape                                   # residual preserves shape
    assert attn.shape == (2, 1, 10, 10)
    # softmax is over the whole grid → each map sums to 1
    s = attn.view(2, -1).sum(dim=1)
    assert torch.allclose(s, torch.ones(2), atol=1e-5)


def test_attention_is_channel_inner_product():
    """logits[h,w] = Σ_c Q[c,h,w]·K[c,h,w] — verify against a manual computation."""
    a = ConvAttention2D(C_GRID)
    X = torch.randn(1, C_GRID, 10, 10); H = torch.randn(1, C_GRID, 10, 10)
    inp = a.norm_in(torch.cat([X, H], 1))
    Q, K = a.q(inp), a.k(inp)
    manual = (Q * K).sum(1) * a.scale                           # (1,10,10)
    manual_attn = torch.softmax(manual.view(1, -1), 1).view(1, 1, 10, 10)
    _, attn = a(X, H, return_attn=True)
    assert torch.allclose(attn, manual_attn, atol=1e-5)


def test_convlstm_shapes():
    c = ConvLSTMCell(C_GRID)
    z = torch.zeros(2, C_GRID, 10, 10)
    H, Cc = c(torch.randn(2, C_GRID, 10, 10), z, z)
    assert H.shape == Cc.shape == (2, C_GRID, 10, 10)


def test_model_contract():
    m = ConvRViTModel(n_quantiles=5)
    assert m.n_tokens == 100 and m.n_quantiles == 5
    s = m.init_states(2)
    out = m.rl_step(torch.randn(2, 3, 50, 50), s)
    assert out["actor_logits"].shape == (2, 2)
    assert out["critic_q_dist"].shape == (2, 2, 5)
    assert out["V_dist"].shape == (2, 5) and out["V_scalar"].shape == (2,)
    so = m.forward_rl_sequence(torch.randn(2, 7, 50, 50, 3))    # channels-last (harness layout)
    assert so["actor_logits_seq"].shape == (2, 7, 2)
    assert so["q_dist_seq"].shape == (2, 7, 2, 5)


def test_init_action_bias_and_taus():
    m = ConvRViTModel(init_action_bias=[0.0, -1.5], n_quantiles=5)
    assert torch.allclose(m.actor_head.out.bias.detach(), torch.tensor([0.0, -1.5]))
    assert m.critic_head.taus.shape == (5,)
