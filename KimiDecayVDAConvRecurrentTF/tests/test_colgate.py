"""Column-gate (softmax_mode='colgate'): per-position stream gate from column sums.

Per key position j: c_X = sum_i A_X[i,j], c_H = sum_i A_H[i,j] (column sums of the
split attention). Gate g = softmax([c_X, c_H] / 0.5) -> (g_X, g_H) per position.
att_i = sum_j A_X[i,j]*g_X[j]*V_X[j] + sum_j A_H[i,j]*g_H[j]*V_H[j].
"""
import torch

from kda_conv_memory_model import (KDAConvMemoryModel,
                                   _two_stream_token_attn, _nchw_to_tokens)


def _mk(C=8, B=2):
    return (torch.randn(B, C, 4, 4), torch.randn(B, C, 4, 4),
            torch.randn(B, C, 4, 4), torch.randn(B, C, 4, 4), torch.randn(B, C, 4, 4))


def test_colgate_matches_manual():
    torch.manual_seed(0)
    Q, Kx, Kh, Vx, Vh = _mk()
    att, _ = _two_stream_token_attn(Q, Kx, Kh, Vx, Vh, 8 ** -0.5, mode="colgate")
    q, Hh, W = _nchw_to_tokens(Q)
    kx, _, _ = _nchw_to_tokens(Kx)
    kh, _, _ = _nchw_to_tokens(Kh)
    vx, _, _ = _nchw_to_tokens(Vx)
    vh, _, _ = _nchw_to_tokens(Vh)
    q, kx, kh = q.float(), kx.float(), kh.float()
    Ax = torch.softmax(q @ kx.transpose(-2, -1) * (8 ** -0.5), dim=-1)
    Ah = torch.softmax(q @ kh.transpose(-2, -1) * (8 ** -0.5), dim=-1)
    cx, ch = Ax.sum(dim=1), Ah.sum(dim=1)               # (B,N) column sums
    g = torch.softmax(torch.stack([cx, ch], dim=-1) / 0.5, dim=-1)  # (B,N,2)
    ref = (Ax * g[..., 0:1]) @ vx + (Ah * g[..., 1:2]) @ vh
    ref = ref.view(2, Hh, W, -1).permute(0, 3, 1, 2)
    assert torch.allclose(att.float(), ref.float(), atol=1e-4)


def test_colgate_gate_is_positionwise_binary():
    # a position whose H column sum dominates gets g_H -> 1, g_X -> 0
    torch.manual_seed(1)
    C, B = 8, 2
    Q, Kx, Kh, Vx, Vh = _mk(C, B)
    # make H keys huge for position 5 only
    Kh[:, :, 0, 1] += 100.0     # position (0,1) = token index 1
    att, _ = _two_stream_token_attn(Q, Kx, Kh, Vx, Vh, 8 ** -0.5, mode="colgate")
    q, _, _ = _nchw_to_tokens(Q)
    kx, _, _ = _nchw_to_tokens(Kx)
    kh, _, _ = _nchw_to_tokens(Kh)
    Ax = torch.softmax(q.float() @ kx.float().transpose(-2, -1) * (8 ** -0.5), dim=-1)
    Ah = torch.softmax(q.float() @ kh.float().transpose(-2, -1) * (8 ** -0.5), dim=-1)
    g = torch.softmax(torch.stack([Ax.sum(1), Ah.sum(1)], dim=-1) / 0.5, dim=-1)
    assert (g[:, 1, 1] > 0.99).all() and (g[:, 1, 0] < 0.01).all()


def test_colgate_differs_from_split():
    torch.manual_seed(0)
    Q, Kx, Kh, Vx, Vh = _mk()
    att_s, _ = _two_stream_token_attn(Q, Kx, Kh, Vx, Vh, 8 ** -0.5, split=True)
    att_c, _ = _two_stream_token_attn(Q, Kx, Kh, Vx, Vh, 8 ** -0.5, mode="colgate")
    assert not torch.allclose(att_s, att_c, atol=1e-4)


def test_colgate_in_both_blocks_and_runs():
    m = KDAConvMemoryModel(n_channels=8, proto_dim=16, map_size=4, frame_window=1,
                           accum_mode="kda", kda_heads=2, kda_head_dim=4,
                           attn_mode="token", readout="h2", v_mode="learned",
                           cls_head="conv", softmax_mode="colgate",
                           memory_noise_std=0.0)
    assert m.vision.softmax_mode == "colgate" and m.memory.softmax_mode == "colgate"
    R, _ = m.step(torch.randn(1, 8, 4, 4),
                  m.init_state(1, torch.device("cpu"), torch.float32))
    R.sum().backward()
    assert m.vision.V_X.grad is not None and m.vision.V_X.grad.abs().sum() > 0
    assert m.vision.V_H.grad is not None and m.vision.V_H.grad.abs().sum() > 0
