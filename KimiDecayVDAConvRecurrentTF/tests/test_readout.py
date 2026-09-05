"""Readout-stream variants: R = [H1‖H2‖Z‖att_vis] (full, 4C) vs [H1‖H2] (h1h2, 2C)."""
from __future__ import annotations

import torch

from kda_conv_memory_model import KDAConvMemoryModel
from kda_rl_model import KDARLModel


def _obs(B=2, T=7, S=16):
    return torch.randn(B, T, S, S, 3)


def test_default_readout_is_full_4c():
    m = KDAConvMemoryModel(n_channels=8, map_size=4, proto_dim=16,
                           kda_heads=2, kda_head_dim=4, attn_mode="token")
    assert m.readout == "full"
    R = m.forward_seq(_obs())
    assert R.shape == (2, 7, 4 * 8, 4, 4)
    logits = m.classify(R[:, -1])
    assert logits.shape == (2, 2)


def test_h1h2_readout_is_2c_and_heads_match():
    m = KDAConvMemoryModel(n_channels=8, map_size=4, proto_dim=16,
                           kda_heads=2, kda_head_dim=4, attn_mode="token",
                           readout="h1h2")
    assert m.readout == "h1h2"
    # heads built on 2C
    assert m.classifier.in_features == 2 * 8
    assert m.jepa_norm.normalized_shape == (2 * 8,)
    assert m.jepa_feat[0].in_channels == 2 * 8
    R = m.forward_seq(_obs())
    assert R.shape == (2, 7, 2 * 8, 4, 4)
    logits = m.classify(R[:, -1])
    assert logits.shape == (2, 2)
    jl = m.jepa_logits(R)
    assert jl.shape[:2] == (2, 7) and jl.shape[-1] == 16


def test_h1h2_readout_drops_z_and_attvis():
    # R must equal concat([H1, H2]) exactly: with zeroed init state at t=0 the
    # memory block is skipped (mem_every large) so H1=H2=0 -> R == 0.
    m = KDAConvMemoryModel(n_channels=8, map_size=4, proto_dim=16,
                           kda_heads=2, kda_head_dim=4, attn_mode="token",
                           mem_every=10**9, readout="h1h2")
    R = m.forward_seq(_obs())
    assert torch.allclose(R[:, 0], torch.zeros_like(R[:, 0]))


def test_bad_readout_rejected():
    try:
        KDAConvMemoryModel(n_channels=8, map_size=4, proto_dim=16,
                           kda_heads=2, kda_head_dim=4, readout="bogus")
    except ValueError:
        return
    raise AssertionError("readout='bogus' should raise ValueError")


def test_rl_model_h1h2_change_head_matches():
    m = KDARLModel(n_channels=8, map_size=4, proto_dim=16,
                   kda_heads=2, kda_head_dim=4, attn_mode="token",
                   readout="h1h2")
    assert m.change_head.in_features == 2 * 8
    assert m.readout.net[0].in_channels == 2 * 8
