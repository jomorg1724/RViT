"""H2 from the MEMORY block with learned value embeddings (v_mode='learned_mem').

Design: the memory block's values V_Z, V_H1 are learned per-position parameters;
H2 = A_Z@V_Z + A_H1@V_H1, computed EVERY step (fast belief). H1 is still written
only on memory ticks (mem_every) — slow tick preserved. The vision block reverts
to derived values, reading H1 as its memory-value source (only H1/ACC persist).
"""
import torch

from kda_conv_memory_model import KDAConvMemoryModel


def _model(v_mode="learned_mem", readout="h2", **kw):
    return KDAConvMemoryModel(n_channels=8, proto_dim=16, map_size=4,
                              frame_window=1, accum_mode="kda", kda_heads=2,
                              kda_head_dim=4, attn_mode="token",
                              readout=readout, v_mode=v_mode, cls_head="conv", **kw)


def test_learned_params_live_in_memory_block():
    m = _model()
    # memory block: learned value embeddings, no value projections
    assert m.memory.learned_v and hasattr(m.memory, "V_X") and hasattr(m.memory, "V_H")
    assert not hasattr(m.memory, "W_vx") and not hasattr(m.memory, "W_vh")
    # vision block: derived values restored
    assert not m.vision.learned_v and hasattr(m.vision, "W_vx") and hasattr(m.vision, "W_vh")


def test_h2_not_carried_as_state():
    # H2's state slot must be irrelevant: same H1/ACC, different H2 -> same R.
    m = _model().eval()
    X = torch.randn(1, 8, 4, 4)
    H1, H2a, ACC = m.init_state(1, torch.device("cpu"), torch.float32)
    H2b = torch.randn_like(H2a)
    with torch.no_grad():
        Ra, _ = m.step(X, (H1, H2a, ACC), update_memory=False)
        Rb, _ = m.step(X, (H1, H2b, ACC), update_memory=False)
    assert torch.allclose(Ra, Rb, atol=1e-5)


def test_h1_static_between_ticks():
    # Without a memory tick, H1 must be untouched; H2 still recomputed.
    m = _model().eval()
    X = torch.randn(1, 8, 4, 4)
    H1, H2, ACC = m.init_state(1, torch.device("cpu"), torch.float32)
    with torch.no_grad():
        _, (H1a, H2a, ACCa) = m.step(X, (H1, H2, ACC), update_memory=False)
    assert torch.equal(H1a, H1)
    assert not torch.equal(ACCa, ACC)          # accumulator ticks every step


def test_h2_depends_on_h1_and_z():
    m = _model().eval()
    X = torch.randn(1, 8, 4, 4)
    H1, H2, ACC = m.init_state(1, torch.device("cpu"), torch.float32)
    H1b = torch.randn_like(H1)
    with torch.no_grad():
        Ra, _ = m.step(X, (H1, H2, ACC), update_memory=False)
        Rb, _ = m.step(X, (H1b, H2, ACC), update_memory=False)
    assert not torch.allclose(Ra, Rb, atol=1e-5)


def test_learned_value_params_get_gradients():
    m = _model()
    m.zero_grad()
    R, _ = m.step(torch.randn(1, 8, 4, 4),
                  m.init_state(1, torch.device("cpu"), torch.float32))
    R.sum().backward()
    assert m.memory.V_X.grad is not None and m.memory.V_X.grad.abs().sum() > 0
    assert m.memory.V_H.grad is not None and m.memory.V_H.grad.abs().sum() > 0


def test_r_shape_and_forward_seq():
    m = _model().eval()
    with torch.no_grad():
        R = m.forward_seq(torch.randn(1, 3, 100, 100, 3))
    assert R.shape == (1, 3, 8, 4, 4)          # r_dim = C = n_channels


def test_default_mode_untouched():
    m = KDAConvMemoryModel(n_channels=8, proto_dim=16, map_size=4, frame_window=1,
                           accum_mode="kda", kda_heads=2, kda_head_dim=4)
    assert m.v_mode == "state" and m.vision.learned_v is False and m.memory.learned_v is False
