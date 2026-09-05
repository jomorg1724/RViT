"""No memory block: H1 IS the vision block's Z output (v_mode='learned_z').

step(): H2 = A_X@V_X + A_H@V_H (learned embeddings, vision block) every step;
H1 <- Z = proj(SE([Xin||att])) + noise every step (no ticks, no memory block).
R = H2. Only H1 and ACC cross timesteps.
"""
import torch

from kda_conv_memory_model import KDAConvMemoryModel


def _model(**kw):
    return KDAConvMemoryModel(n_channels=8, proto_dim=16, map_size=4,
                              frame_window=1, accum_mode="kda", kda_heads=2,
                              kda_head_dim=4, attn_mode="token",
                              readout="h2", v_mode="learned_z",
                              cls_head="conv", memory_noise_std=0.0, **kw)


def test_no_memory_block():
    m = _model()
    assert m.memory is None
    assert m.vision.learned_v


def test_h1_updates_every_step_without_ticks():
    m = _model().eval()
    X = torch.randn(1, 8, 4, 4)
    H1, H2, ACC = m.init_state(1, torch.device("cpu"), torch.float32)
    with torch.no_grad():
        _, (H1a, _, _) = m.step(X, (H1, H2, ACC), update_memory=False)
    # no memory block => no tick gating: H1 is rewritten even when update_memory=False
    assert not torch.equal(H1a, H1)


def test_h1_is_z_output():
    m = _model().eval()
    X = torch.randn(1, 8, 4, 4)
    H1, H2, ACC = m.init_state(1, torch.device("cpu"), torch.float32)
    with torch.no_grad():
        ACC2, acc_read, _ = m._accumulate(X, H1, ACC)
        Xin = torch.cat([X, acc_read], dim=1)
        Z, att = m.vision(Xin, H1, H2)
        _, (H1n, H2n, _) = m.step(X, (H1, H2, ACC), update_memory=False)
    assert torch.allclose(H1n, Z, atol=1e-6)
    assert torch.allclose(H2n, att, atol=1e-6)


def test_h2_state_slot_inert():
    m = _model().eval()
    X = torch.randn(1, 8, 4, 4)
    H1, H2a, ACC = m.init_state(1, torch.device("cpu"), torch.float32)
    H2b = torch.randn_like(H2a)
    with torch.no_grad():
        Ra, _ = m.step(X, (H1, H2a, ACC), update_memory=False)
        Rb, _ = m.step(X, (H1, H2b, ACC), update_memory=False)
    assert torch.allclose(Ra, Rb, atol=1e-5)


def test_learned_value_params_get_gradients():
    m = _model()
    m.zero_grad()
    R, _ = m.step(torch.randn(1, 8, 4, 4),
                  m.init_state(1, torch.device("cpu"), torch.float32))
    R.sum().backward()
    assert m.vision.V_X.grad is not None and m.vision.V_X.grad.abs().sum() > 0
    assert m.vision.V_H.grad is not None and m.vision.V_H.grad.abs().sum() > 0


def test_r_shape_and_forward_seq():
    m = _model().eval()
    with torch.no_grad():
        R = m.forward_seq(torch.randn(1, 3, 100, 100, 3))
    assert R.shape == (1, 3, 8, 4, 4)


def test_other_modes_untouched():
    m = KDAConvMemoryModel(n_channels=8, proto_dim=16, map_size=4, frame_window=1,
                           accum_mode="kda", kda_heads=2, kda_head_dim=4)
    assert m.v_mode == "state" and m.memory is not None
