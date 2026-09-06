"""All values learned (v_mode='learned_all'): champion wiring, but the memory
block's values V_Z / V_H1 are ALSO learned embeddings (like the vision block's
V_X / V_H). H2 still from the vision block; H1 written on ticks via the memory
block whose attention mix now reads learned tables only.
"""
import torch

from kda_conv_memory_model import KDAConvMemoryModel


def _model(**kw):
    return KDAConvMemoryModel(n_channels=8, proto_dim=16, map_size=4,
                              frame_window=1, accum_mode="kda", kda_heads=2,
                              kda_head_dim=4, attn_mode="token",
                              readout="h2", v_mode="learned_all",
                              cls_head="conv", memory_noise_std=0.0, **kw)


def test_both_blocks_have_learned_values():
    m = _model()
    assert m.vision.learned_v and m.memory.learned_v
    assert isinstance(m.vision.V_X, torch.nn.Parameter)
    assert isinstance(m.memory.V_X, torch.nn.Parameter)  # V_Z
    assert isinstance(m.memory.V_H, torch.nn.Parameter)  # V_H1
    assert not hasattr(m.memory, "W_vz") and not hasattr(m.memory, "W_vh")


def test_memory_value_params_get_gradients_on_tick():
    m = _model()
    m.zero_grad()
    s = m.init_state(1, torch.device("cpu"), torch.float32)
    loss = 0.0
    for t in range(3):
        R, s = m.step(torch.randn(1, 8, 4, 4), s, update_memory=(t == 0))
        loss = loss + R.sum()
    # H1 (written at t=0 via the learned-value memory mix) enters later steps'
    # H2 through K_h, so grads must flow back to the memory block's V params.
    loss.backward()
    assert m.memory.V_X.grad is not None and m.memory.V_X.grad.abs().sum() > 0
    assert m.memory.V_H.grad is not None and m.memory.V_H.grad.abs().sum() > 0


def test_champion_semantics_kept():
    # H2 = vision-block att (not memory), every step, inert H2 state slot
    m = _model().eval()
    X = torch.randn(1, 8, 4, 4)
    H1, H2a, ACC = m.init_state(1, torch.device("cpu"), torch.float32)
    with torch.no_grad():
        ACC2, acc_read, _ = m._accumulate(X, H1, ACC)
        Xin = torch.cat([X, acc_read], dim=1)
        _, att = m.vision(Xin, H1, H2a)
        _, (H1n, H2n, _) = m.step(X, (H1, H2a, ACC), update_memory=False)
    assert torch.allclose(H2n, att, atol=1e-6)
    assert torch.allclose(H1n, H1)  # no tick: H1 unchanged
    # H2 slot inert
    with torch.no_grad():
        Ra, _ = m.step(X, (H1, H2a, ACC), update_memory=False)
        Rb, _ = m.step(X, (H1, torch.randn_like(H2a), ACC), update_memory=False)
    assert torch.allclose(Ra, Rb, atol=1e-5)


def test_h1_written_on_tick():
    m = _model().eval()
    X = torch.randn(1, 8, 4, 4)
    s0 = m.init_state(1, torch.device("cpu"), torch.float32)
    with torch.no_grad():
        _, (H1n, _, _) = m.step(X, s0, update_memory=True)
    assert not torch.equal(H1n, s0[0])


def test_forward_seq_and_r_shape():
    m = _model().eval()
    with torch.no_grad():
        R = m.forward_seq(torch.randn(1, 3, 100, 100, 3))
    assert R.shape == (1, 3, 8, 4, 4)


def test_other_modes_untouched():
    m = KDAConvMemoryModel(n_channels=8, proto_dim=16, map_size=4, frame_window=1,
                           accum_mode="kda", kda_heads=2, kda_head_dim=4)
    assert m.v_mode == "state" and not m.memory.learned_v and hasattr(m.memory, "W_vz")
    m2 = _model.__wrapped__() if hasattr(_model, "__wrapped__") else None
