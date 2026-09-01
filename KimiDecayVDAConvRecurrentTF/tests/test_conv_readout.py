"""Conv spatial readout for RL heads: no global mean-pool."""
from __future__ import annotations

import torch

from kda_rl_model import KDARLModel, SpatialConvReadout


def test_spatial_conv_readout_shape():
    r = SpatialConvReadout(in_ch=512, map_size=16)
    x = torch.randn(3, 512, 16, 16)
    y = r(x)
    assert y.dim() == 2 and y.shape[0] == 3
    assert y.shape[1] == r.out_dim
    assert r.out_dim < 512 * 16 * 16


def test_rl_heads_use_conv_not_mean_pool():
    torch.manual_seed(0)
    m = KDARLModel(n_channels=128, attn_mode="token", map_size=16)
    B = 2
    x = torch.randn(B, 3, 100, 100)
    st = m.init_states(B, device="cpu", dtype=torch.float32)
    out = m.rl_step(x, st, inject_memory_noise=False)
    assert out["actor_logits"].shape == (B, 2)
    assert out["critic_q_dist"].shape == (B, 2, 5)
    assert out["rec"].dim() == 2
    # rec is conv-decoded, not (B, 4C) mean-pool
    assert out["rec"].shape[-1] != 4 * 128
