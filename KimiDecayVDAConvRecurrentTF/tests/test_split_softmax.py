"""Split softmax (softmax_mode='split'): each key stream softmaxed separately.

Champion variant change: instead of ONE softmax over [S_x || S_h] (streams
compete for total mass 1), compute A_X = softmax(S_x) and A_H = softmax(S_h)
independently (each row sums to 1 per stream), then att = A_X@V_X + A_H@V_H.
Applied in BOTH the vision block and the memory block.
"""
import torch

from kda_conv_memory_model import (KDAConvMemoryModel, ConvAttentionBlock,
                                   _two_stream_token_attn, _nchw_to_tokens)


def _mk(C=8, P=16, B=2):
    return (torch.randn(B, C, 4, 4), torch.randn(B, C, 4, 4),
            torch.randn(B, C, 4, 4), torch.randn(B, C, 4, 4), torch.randn(B, C, 4, 4))


def test_split_rows_sum_to_one_per_stream():
    # split: each stream's mass per query is exactly 1 (no competition)
    Q, Kx, Kh, Vx, Vh = _mk()
    _, A_maps = _two_stream_token_attn(Q, Kx, Kh, Vx, Vh, 8 ** -0.5, split=True)
    assert torch.allclose(A_maps[:, 0], torch.ones_like(A_maps[:, 0]), atol=1e-5)
    assert torch.allclose(A_maps[:, 1], torch.ones_like(A_maps[:, 1]), atol=1e-5)


def test_joint_rows_sum_to_one_combined():
    # joint: stream masses sum to 1 (streams compete)
    Q, Kx, Kh, Vx, Vh = _mk()
    _, A_maps = _two_stream_token_attn(Q, Kx, Kh, Vx, Vh, 8 ** -0.5, split=False)
    tot = A_maps[:, 0] + A_maps[:, 1]
    assert torch.allclose(tot, torch.ones_like(tot), atol=1e-5)


def test_split_output_is_sum_of_separate_mixes():
    torch.manual_seed(0)
    Q, Kx, Kh, Vx, Vh = _mk()
    att, _ = _two_stream_token_attn(Q, Kx, Kh, Vx, Vh, 8 ** -0.5, split=True)
    q, Hh, W = _nchw_to_tokens(Q)
    kx, _, _ = _nchw_to_tokens(Kx)
    kh, _, _ = _nchw_to_tokens(Kh)
    vx, _, _ = _nchw_to_tokens(Vx)
    vh, _, _ = _nchw_to_tokens(Vh)
    q, kx, kh = q.float(), kx.float(), kh.float()
    Ax = torch.softmax(q @ kx.transpose(-2, -1) * (8 ** -0.5), dim=-1)
    Ah = torch.softmax(q @ kh.transpose(-2, -1) * (8 ** -0.5), dim=-1)
    ref = (Ax @ vx + Ah @ vh).view(2, Hh, W, -1).permute(0, 3, 1, 2)
    assert torch.allclose(att.float(), ref.float(), atol=1e-4)


def test_split_differs_from_joint():
    torch.manual_seed(0)
    Q, Kx, Kh, Vx, Vh = _mk()
    att_j, _ = _two_stream_token_attn(Q, Kx, Kh, Vx, Vh, 8 ** -0.5, split=False)
    att_s, _ = _two_stream_token_attn(Q, Kx, Kh, Vx, Vh, 8 ** -0.5, split=True)
    assert not torch.allclose(att_j, att_s, atol=1e-4)


def test_both_blocks_split_in_model():
    m = KDAConvMemoryModel(n_channels=8, proto_dim=16, map_size=4, frame_window=1,
                           accum_mode="kda", kda_heads=2, kda_head_dim=4,
                           attn_mode="token", readout="h2", v_mode="learned",
                           cls_head="conv", softmax_mode="split")
    assert m.vision.softmax_mode == "split" and m.memory.softmax_mode == "split"


def test_split_model_runs_and_grads():
    m = KDAConvMemoryModel(n_channels=8, proto_dim=16, map_size=4, frame_window=1,
                           accum_mode="kda", kda_heads=2, kda_head_dim=4,
                           attn_mode="token", readout="h2", v_mode="learned",
                           cls_head="conv", softmax_mode="split", memory_noise_std=0.0)
    R, _ = m.step(torch.randn(1, 8, 4, 4),
                  m.init_state(1, torch.device("cpu"), torch.float32))
    R.sum().backward()
    assert m.vision.V_X.grad is not None and m.vision.V_X.grad.abs().sum() > 0


def test_default_is_joint():
    m = KDAConvMemoryModel(n_channels=8, proto_dim=16, map_size=4, frame_window=1,
                           accum_mode="kda", kda_heads=2, kda_head_dim=4)
    assert m.softmax_mode == "joint"
