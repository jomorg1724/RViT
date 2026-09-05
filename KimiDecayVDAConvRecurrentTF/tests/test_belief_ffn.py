"""FFN belief head: per-pixel channel-FFN (r_dim->16), flatten, FFN -> 2 logits.

Contrasts with the legacy mean-pool Linear head (cls_head="pool").
"""
from __future__ import annotations

import torch

from kda_conv_memory_model import KDAConvMemoryModel


def _model(cls_head, **kw):
    kw.setdefault("n_channels", 8)
    kw.setdefault("map_size", 4)
    kw.setdefault("proto_dim", 16)
    kw.setdefault("kda_heads", 2)
    kw.setdefault("kda_head_dim", 4)
    kw.setdefault("attn_mode", "token")
    kw.setdefault("readout", "h1h2")
    return KDAConvMemoryModel(cls_head=cls_head, **kw)


def test_ffn_head_structure():
    m = _model("ffn")
    r_dim, S = m.r_dim, m.map_size
    assert isinstance(m.cls_chan, torch.nn.Linear)
    assert m.cls_chan.in_features == r_dim and m.cls_chan.out_features == 16
    assert isinstance(m.cls_out, torch.nn.Linear)
    assert m.cls_out.in_features == 16 * S * S and m.cls_out.out_features == 2
    # legacy pool head must not exist in ffn mode
    assert not hasattr(m, "classifier")


def test_pool_head_structure():
    m = _model("pool")
    assert isinstance(m.classifier, torch.nn.Linear)
    assert m.classifier.in_features == m.r_dim
    assert not hasattr(m, "cls_chan")


def test_ffn_classify_runs_end_to_end():
    m = _model("ffn")
    R = m.forward_seq(torch.randn(2, 7, 16, 16, 3))
    logits = m.classify(R[:, -1])
    assert logits.shape == (2, 2)
    # per-step decode (belief mode) works on every step
    all_logits = torch.stack([m.classify(R[:, t]) for t in range(R.shape[1])], dim=1)
    assert all_logits.shape == (2, 7, 2)


def test_ffn_head_is_spatially_sensitive():
    # mean-pool invariant under permutation; the flatten FFN must NOT be
    m = _model("ffn").eval()
    R = torch.randn(1, m.r_dim, m.map_size, m.map_size)
    perm = torch.randperm(m.map_size * m.map_size)
    Rp = R.flatten(2)[:, :, perm].view_as(R)
    with torch.no_grad():
        d = (m.classify(R) - m.classify(Rp)).abs().max().item()
    assert d > 1e-4


def test_ffn_gradient_flows_to_trunk():
    m = _model("ffn")
    R = m.forward_seq(torch.randn(1, 7, 16, 16, 3))
    loss = m.classify(R[:, -1]).sum()
    loss.backward()
    g = m.stem.net[0].weight.grad
    assert g is not None and g.abs().sum().item() > 0


def test_bad_cls_head_rejected():
    try:
        _model("bogus")
    except ValueError:
        return
    raise AssertionError("cls_head='bogus' should raise ValueError")
