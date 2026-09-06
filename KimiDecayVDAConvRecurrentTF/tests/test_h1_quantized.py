"""Quantized H1 (v_mode='learned_zq'): H1 = Z discretized per position.

Per grid position: p = softmax over the channel dim of Z; sample a one-hot
channel index; H1 = onehot - p.detach() + p (straight-through estimator).
Aux entropy penalty = mean over positions of -sum_c p log p (stored for the
trainer). No Gaussian noise (H1 is discrete). H2 readout unchanged (learned
values, vision block).
"""
import math
import torch

from kda_conv_memory_model import KDAConvMemoryModel


def _model(**kw):
    return KDAConvMemoryModel(n_channels=8, proto_dim=16, map_size=4,
                              frame_window=1, accum_mode="kda", kda_heads=2,
                              kda_head_dim=4, attn_mode="token",
                              readout="h2", v_mode="learned_zq",
                              cls_head="conv", memory_noise_std=0.05, **kw)


def test_h1_is_onehot_per_position():
    m = _model().eval()
    with torch.no_grad():
        _, (H1, _, _) = m.step(torch.randn(2, 8, 4, 4),
                               m.init_state(2, torch.device("cpu"), torch.float32))
    vals = H1.unique()
    assert set(vals.tolist()) <= {0.0, 1.0}
    assert torch.allclose(H1.sum(dim=1), torch.ones(2, 4, 4))  # one channel per position


def test_straight_through_gradients_flow():
    m = _model()
    m.zero_grad()
    s = m.init_state(1, torch.device("cpu"), torch.float32)
    loss = 0.0
    for t in range(2):  # H1 of t=0 feeds keys at t=1
        R, s = m.step(torch.randn(1, 8, 4, 4), s)
        loss = loss + R.sum()
    loss.backward()
    # gradient must reach the weights that produce Z (through p, via STE)
    g = m.vision.proj.weight.grad  # proj conv weight (produces Z)
    assert g is not None and g.abs().sum() > 0
    assert m.vision.V_X.grad is not None and m.vision.V_X.grad.abs().sum() > 0


def test_entropy_aux_tracked():
    m = _model()
    assert m.aux_entropy is None
    m.step(torch.randn(1, 8, 4, 4),
           m.init_state(1, torch.device("cpu"), torch.float32))
    e = m.aux_entropy
    assert e is not None and torch.isfinite(e)
    assert 0.0 <= float(e) <= math.log(8) + 1e-5  # entropy of 8-way dist


def test_h1_quantized_every_step():
    # H1 rewrites every step (no memory block, no ticks) and is discrete
    m = _model().eval()
    s = m.init_state(1, torch.device("cpu"), torch.float32)
    with torch.no_grad():
        _, s1 = m.step(torch.randn(1, 8, 4, 4), s)
        _, s2 = m.step(torch.randn(1, 8, 4, 4), s1)
    assert not torch.equal(s1[0], s2[0])
    assert set(s2[0].unique().tolist()) <= {0.0, 1.0}


def test_forward_seq_shape():
    m = _model().eval()
    with torch.no_grad():
        R = m.forward_seq(torch.randn(1, 3, 100, 100, 3))
    assert R.shape == (1, 3, 8, 4, 4)
    assert m.aux_entropy is not None


def test_other_modes_have_no_aux_entropy():
    m = KDAConvMemoryModel(n_channels=8, proto_dim=16, map_size=4, frame_window=1,
                           accum_mode="kda", kda_heads=2, kda_head_dim=4,
                           attn_mode="token", readout="h2", v_mode="learned_z",
                           cls_head="conv")
    m.step(torch.randn(1, 8, 4, 4),
           m.init_state(1, torch.device("cpu"), torch.float32))
    assert m.aux_entropy is None


def test_h1_keys_use_learned_embedding_not_conv():
    m = _model()
    # one-hot H1 -> key retrieval must be a learned per-channel embedding
    # lookup (linear over channels), NOT a conv layer
    assert hasattr(m.vision, "W_kh_emb") and isinstance(m.vision.W_kh_emb, torch.nn.Parameter)
    assert m.vision.W_kh_emb.shape == (8, 8)
    assert not hasattr(m.vision, "W_kh")
    # and it must equal the embedding gather of the one-hot indices
    m.eval()
    X = torch.randn(1, 8, 4, 4)
    s = m.init_state(1, torch.device("cpu"), torch.float32)
    with torch.no_grad():
        _, s1 = m.step(X, s)
        H1 = s1[0]                                   # one-hot (B,C,H,W)
        idx = H1.argmax(dim=1)                       # (B,H,W)
        # einsum("bchw,dc->bdhw") selects COLUMN idx of the embedding table
        K_ref = m.vision.W_kh_emb.t()[idx.flatten(1)]  # (B,N,C) lookup
        K_ref = K_ref.view(1, 4, 4, 8).permute(0, 3, 1, 2)
        ACC2, acc_read, _ = m._accumulate(X, H1, s1[2])
        Xin = torch.cat([X, acc_read], dim=1)
        Q = m.vision.W_q(Xin)
        from kda_conv_memory_model import _nchw_to_tokens
        qt, _, _ = _nchw_to_tokens(Q)
        kref, _, _ = _nchw_to_tokens(K_ref)
        s_ref = qt @ kref.transpose(-2, -1)
        # model's internal K_h must match the embedding lookup
        Kh_model = m.vision._keys_h(H1)
        km, _, _ = _nchw_to_tokens(Kh_model)
        s_mod = qt @ km.transpose(-2, -1)
        assert torch.allclose(s_mod, s_ref, atol=1e-5)
