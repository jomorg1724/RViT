"""Tokenwise two-stream attention: QK^T over space, softmax over both streams."""
from __future__ import annotations

import torch

from kda_conv_memory_model import ConvAttentionBlock, ConvMemoryBlock


def test_token_attention_shapes_and_stream_mass():
    blk = ConvAttentionBlock(c=8, in_c=8, attn_mode="token")
    B, C, H, W = 2, 8, 4, 4
    X = torch.randn(B, C, H, W)
    H1 = torch.randn(B, C, H, W)
    H2 = torch.randn(B, C, H, W)
    Z, att, A = blk(X, H1, H2, return_attn=True)
    assert Z.shape == (B, C, H, W)
    assert att.shape == (B, C, H, W)
    assert A.shape == (B, 2, H, W)
    assert torch.allclose(A.sum(dim=1), torch.ones(B, H, W), atol=1e-5)


def test_token_attention_mixes_space_pixel_gate_does_not():
    """A query at (1,0) whose K matches a key at (0,0) should read that V only in token mode."""
    torch.manual_seed(0)
    B, C, H, W = 1, 4, 2, 2
    N = H * W
    blk_tok = ConvAttentionBlock(c=C, in_c=C, attn_mode="token")
    blk_pix = ConvAttentionBlock(c=C, in_c=C, attn_mode="pixel_gate")
    with torch.no_grad():
        for blk in (blk_tok, blk_pix):
            blk.W_q.weight.copy_(torch.eye(C).view(C, C, 1, 1))
            blk.W_kx.weight.copy_(torch.eye(C).view(C, C, 1, 1))
            blk.W_kh.weight.zero_()
            blk.W_vx.weight.copy_(torch.eye(C).view(C, C, 1, 1))
            blk.W_vh.weight.zero_()
            for p in blk.ffn.parameters():
                p.zero_()
            # identity FFN second conv would zero; replace ffn with identity via bypass:
            blk.ffn = torch.nn.Identity()

    X = torch.zeros(B, C, H, W)
    # unique value only at spatial (0,0)
    X[0, :, 0, 0] = torch.tensor([1.0, 2.0, 3.0, 4.0])
    # query/key at (1,0) matches the (0,0) content so token QK^T attends there
    X[0, :, 1, 0] = torch.tensor([1.0, 2.0, 3.0, 4.0])
    H1 = torch.zeros_like(X)
    H2 = torch.zeros_like(X)

    Zt, at, _ = blk_tok(X, H1, H2, return_attn=True)
    Zp, ap, _ = blk_pix(X, H1, H2, return_attn=True)
    # token mode: query at (1,0) can read V from (0,0)
    assert at[0, :, 1, 0].abs().sum() > 0.5
    # pixel gate is strictly local: empty pixel (0,1) cannot receive (0,0)'s value
    assert ap[0, :, 0, 1].abs().sum() < 1e-5


def test_memory_token_attention_shapes():
    blk = ConvMemoryBlock(c=8, attn_mode="token")
    B, C, H, W = 2, 8, 4, 4
    Z = torch.randn(B, C, H, W)
    H1 = torch.randn(B, C, H, W)
    H1n, H2n = blk(Z, H1)
    assert H1n.shape == (B, C, H, W)
    assert H2n.shape == (B, C, H, W)
