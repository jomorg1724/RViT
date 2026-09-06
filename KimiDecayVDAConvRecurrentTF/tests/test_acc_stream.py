"""Triplet attention (acc_stream=True): accumulator readout becomes a THIRD
key/value stream instead of being concatenated to X.

Vision block: Q,K_x from X only (in_c=C, no concat); K_a = W_ka(acc_read);
V_A learned per-position embeddings. Joint softmax over [S_x | S_h | S_a];
H2 = A_X@V_X + A_H@V_H + A_A@V_A. A_maps carry 3 stream masses summing to 1.
"""
import torch

from kda_conv_memory_model import KDAConvMemoryModel, _nchw_to_tokens


def _model(**kw):
    return KDAConvMemoryModel(n_channels=8, proto_dim=16, map_size=4,
                              frame_window=1, accum_mode="kda", kda_heads=2,
                              kda_head_dim=4, attn_mode="token",
                              readout="h2", v_mode="learned_z",
                              cls_head="conv", acc_stream=True, **kw)


def test_no_concat_vision_input_is_x_only():
    m = _model()
    assert m.vision.W_q.in_channels == 8      # X only, NOT 2C
    assert m.vision.W_kx.in_channels == 8


def test_third_stream_params_exist():
    m = _model()
    assert isinstance(m.vision.W_ka, torch.nn.Conv2d)
    assert m.vision.W_ka.in_channels == 8     # keys from accumulator readout
    assert isinstance(m.vision.V_A, torch.nn.Parameter)
    assert m.vision.V_A.shape == (1, 8, 4, 4)  # learned per-position values


def test_triplet_softmax_masses_sum_to_one():
    m = _model().eval()
    with torch.no_grad():
        _, _, stats = m.step(torch.randn(2, 8, 4, 4),
                             m.init_state(2, torch.device("cpu"), torch.float32),
                             return_stats=True)
    A = stats["A_vis"]                         # (B, 3, H, W) stream masses
    assert A.shape == (2, 3, 4, 4)
    tot = A.sum(dim=1)
    assert torch.allclose(tot, torch.ones_like(tot), atol=1e-4)


def test_accumulator_stream_receives_gradient():
    m = _model()
    m.zero_grad()
    s = m.init_state(1, torch.device("cpu"), torch.float32)
    loss = 0.0
    for _ in range(2):
        R, s = m.step(torch.randn(1, 8, 4, 4), s)
        loss = loss + R.sum()
    loss.backward()
    assert m.vision.V_A.grad is not None and m.vision.V_A.grad.abs().sum() > 0
    assert m.vision.W_ka.weight.grad is not None and m.vision.W_ka.weight.grad.abs().sum() > 0


def test_forward_seq_shape():
    m = _model().eval()
    with torch.no_grad():
        R = m.forward_seq(torch.randn(1, 3, 100, 100, 3))
    assert R.shape == (1, 3, 8, 4, 4)


def test_default_unchanged():
    m = KDAConvMemoryModel(n_channels=8, proto_dim=16, map_size=4, frame_window=1,
                           accum_mode="kda", kda_heads=2, kda_head_dim=4,
                           attn_mode="token", readout="h2", v_mode="learned_z",
                           cls_head="conv")
    assert m.vision.W_q.in_channels == 16     # concat path preserved
    assert not hasattr(m.vision, "V_A")
    R, st, stats = m.step(torch.randn(1, 8, 4, 4),
                          m.init_state(1, torch.device("cpu"), torch.float32),
                          return_stats=True)
    assert stats["A_vis"].shape == (1, 2, 4, 4)
