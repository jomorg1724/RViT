"""
Smoke tests for RViT+ v12_part3 — an EMA codebook WRITTEN by a gated image-content
stream. A transformer+LSTM ("stream 3", Q=codebook, K=H3, V=X) produces a gated
write that is added to the codebook (C_t = C_base + gate⊙H3); the readout reads C_t;
and C_base (a buffer, no gradient, init ZERO) is consolidated by a slow VQ-VAE EMA
toward C_t.

Run:  .venv/bin/python -m RViT_plus_v12_part3.tests.test_v12_part3
"""
from __future__ import annotations

import copy
import os
import sys

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v12_part3.env import ChangeDetectionEnv
from RViT_plus_v12_part3.tx_lstm_encoder import VQAttnEncoder
from RViT_plus_v12_part3.model import RViTPlusV12Part3Model
from RViT_plus_v12_part3.ppo import (
    PPOConfig, collect_episodes, concat_batches, ppo_update, train,
)

DEVICE = torch.device("cpu")
torch.manual_seed(0)


def _model(**over):
    kw = dict(patch_size=5, d_model=64, d_mem=64, tx_heads=1, tx_layers=1, n_lstm=1,
              conv_channels=32, n_conv_layers=3, conv_kernel=5, n_actions=2, n_quantiles=8,
              init_action_bias=[0.0, -1.5], seq_len=29, temperature=1.0)
    kw.update(over)
    return RViTPlusV12Part3Model(**kw).to(DEVICE)


def _state(B, N=100, d=64):
    """State = (Hs=[H2, H3], Cs=[C2, C3]). H3 nonzero so the write stream is active."""
    z = lambda: torch.randn(B, N, d)
    return [z(), z()], [z(), z()]


def test_patch_embed_shapes():
    m = _model()
    tok = m.patch_embed(torch.randn(3, 3, 50, 50))
    assert tok.shape == (3, 100, 64) and m.n_tokens == 100
    print("✓ patch_embed: (3,3,50,50) → (3,100,64); n_tokens=100")


def test_codebook_is_ema_buffer_init_zero():
    m = _model()
    pnames = dict(m.encoder.named_parameters()); bnames = dict(m.encoder.named_buffers())
    assert "codebook" in bnames and "codebook" not in pnames, "codebook must be a buffer, not a Parameter"
    assert not m.encoder.codebook.requires_grad
    assert float(m.encoder.codebook.abs().sum()) == 0.0, "codebook must init at ZERO (built only by the EMA)"
    assert any(k.endswith("codebook") for k in m.state_dict()), "codebook must be in the state_dict"
    print("✓ codebook is an EMA buffer, init ZERO, in state_dict, not a gradient parameter")


def test_structure_gated_write_stream():
    m = _model(); enc = m.encoder
    assert isinstance(enc, VQAttnEncoder)
    for nm in ("W_q3", "W_k3", "W_v3", "W_o3", "W_gate", "ffn3", "cell3"):
        assert hasattr(enc, nm), f"missing write-stream component {nm}"
    for nm in ("W_q", "W_k", "W_o", "cell2"):
        assert hasattr(enc, nm), f"missing readout component {nm}"
    assert not hasattr(enc, "W_v"), "readout has no W_v — values ARE the codebook C_t"
    assert len(enc.cells) == 2, "two LSTMs: LSTM2 (readout) + LSTM3 (write stream)"
    assert hasattr(enc, "ema_update_codebook")
    print("✓ structure: write stream (Q3/K3/V3/O3 + gate + LSTM3) + readout (LSTM2) + EMA buffer")


def test_state_two_lstms():
    Hs, Cs = _model().init_states(2, device=DEVICE)
    assert len(Hs) == 2 and len(Cs) == 2, "state = [H2,H3]/[C2,C3]"
    assert all(h.shape == (2, 100, 64) for h in Hs)
    print("✓ init state: two LSTM states [H2, H3] / [C2, C3]")


def test_ema_update_codebook_toward_target():
    """C_base ← (1−r)·C_base + r·target (target = C_t); no grad; rate 0 freezes."""
    enc = _model().encoder.eval()
    with torch.no_grad():                      # codebook starts at 0; give it a value to test the blend
        enc.codebook.copy_(torch.randn_like(enc.codebook))
    before = enc.codebook.clone()
    target = torch.randn(100, 64)
    inc = enc.ema_update_codebook(target, rate=0.01)
    assert torch.allclose(enc.codebook, 0.99 * before + 0.01 * target.unsqueeze(0), atol=1e-6), \
        "EMA must move C_base to (1−r)·C_base + r·target"
    assert torch.allclose(inc, 0.01 * (target.unsqueeze(0) - before), atol=1e-6), "increment = r·(target − C_base)"
    assert not enc.codebook.requires_grad
    b2 = enc.codebook.clone()
    enc.ema_update_codebook(target, rate=0.0)
    assert torch.allclose(enc.codebook, b2), "rate 0 freezes C_base"
    print("✓ ema_update_codebook: C_base ← (1−r)C_base + r·target (toward C_t); rate 0 freezes")


def test_write_stream_reads_X_and_H3():
    """The gated write depends on X (via V3=W_v3·X) and H3 (via K3 + LSTM3 input)."""
    m = _model().eval()
    states = _state(2); tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    with torch.no_grad():
        m.encoder.forward_step(tok, states); w0 = m.encoder.last_write
        tok_b = m.patch_embed(torch.randn(2, 3, 50, 50))
        m.encoder.forward_step(tok_b, states); wX = m.encoder.last_write
        assert not torch.allclose(w0, wX), "X must move the write (V3 = W_v3·X)"
        st_h3 = ([states[0][0], torch.randn(2, 100, 64)], states[1])
        m.encoder.forward_step(tok, st_h3); wH3 = m.encoder.last_write
        assert not torch.allclose(w0, wH3), "H3 must move the write (K3 = W_k3·H3 + LSTM3 input)"
    print("✓ write stream: write responds to BOTH X (V3) and H3 (K3/LSTM3)")


def test_gate_in_unit_interval_and_Ct():
    m = _model().eval()
    states = _state(2); tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    with torch.no_grad():
        m.encoder.forward_step(tok, states)
        gate, write, Ct = m.encoder.last_gate, m.encoder.last_write, m.encoder.last_Ct
        assert (gate > 0).all() and (gate < 1).all(), "gate ∈ (0,1)"
        C_base = m.encoder.codebook
        assert torch.allclose(Ct, C_base + write, atol=1e-6), "C_t must equal C_base + gate⊙H3"
    print(f"✓ gate ∈ (0,1) (mean≈{float(gate.mean()):.2f}); C_t = C_base + gate⊙H3")


def test_readout_reads_Ct():
    """Holding X and H2 fixed, changing H3 (→ write → C_t) changes Z but NOT the
    readout weights — so the readout reads C_t as its VALUES."""
    m = _model().eval()
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    H2 = torch.randn(2, 100, 64); C2 = torch.randn(2, 100, 64); C3 = torch.randn(2, 100, 64)
    s_a = ([H2, torch.randn(2, 100, 64)], [C2, C3])
    s_b = ([H2, torch.randn(2, 100, 64)], [C2, C3])     # different H3 only
    with torch.no_grad():
        (_a, _ca), rec_a, attn_a = m.encoder.forward_step(tok, s_a, return_attn=True)
        (_b, _cb), rec_b, attn_b = m.encoder.forward_step(tok, s_b, return_attn=True)
        assert torch.allclose(attn_a[0], attn_b[0], atol=1e-6), "readout weights depend on X,H2 only"
        assert not torch.allclose(rec_a[0], rec_b[0]), "Z must change with H3 (values = C_t)"
    print("✓ readout: Z reads C_t as VALUES (H3→write→C_t changes Z, not the readout weights)")


def test_gate_cost_differentiable_codebook_no_grad():
    m = _model().eval()
    with torch.no_grad():                      # codebook inits at 0 (then Q3=W_q3·0 has no weight-grad);
        m.encoder.codebook.copy_(torch.randn_like(m.encoder.codebook))   # use a consolidated C_base
    states = _state(2); tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    m.encoder.forward_step(tok, states)
    cost = m.encoder.last_gate_cost
    assert cost.shape == (2,)
    assert torch.allclose(cost, m.encoder.last_gate.mean(dim=(1, 2)), atol=1e-6), "cost = mean(gate)"
    m.zero_grad(); cost.sum().backward()
    for nm in ("W_gate", "W_q3", "W_k3", "W_v3", "W_o3"):
        g = getattr(m.encoder, nm).weight.grad
        assert g is not None and g.abs().sum() > 0, f"gate cost must reach {nm}"
    assert m.encoder.codebook.grad is None, "codebook is a buffer — NO gradient"
    print("✓ gate cost = mean(gate) → grad into the write stream + gate; codebook gets NO grad")


def test_sequence_exposes_Ct_and_gate():
    m = _model()
    out = m.forward_rl_sequence(torch.randn(3, 29, 3, 50, 50))
    g = out["gate_seq"]; ct = out["Ct_seq"]
    assert g.shape == (3, 29) and g.requires_grad, "gate_seq (B,T) differentiable"
    assert ct.shape == (3, 29, 100, 64) and not ct.requires_grad, "Ct_seq (B,T,N,d) detached (EMA target)"
    m.zero_grad(); g.sum().backward()
    assert m.encoder.W_gate.weight.grad.abs().sum() > 0, "gate_seq grad must reach the gate"
    print("✓ forward_rl_sequence: differentiable gate_seq + detached Ct_seq (EMA target)")


def test_Z_to_both_heads_and_rec():
    m = _model().eval(); B = 4
    Z1, Z2 = torch.randn(B, 100, 64), torch.randn(B, 100, 64)
    with torch.no_grad():
        al1, q1, _, _ = m._run_heads([Z1]); al2, q2, _, _ = m._run_heads([Z2])
        assert al1.shape == (B, 2) and q1.shape == (B, 2, 8)
        assert not torch.allclose(al1, al2) and not torch.allclose(q1, q2)
    (_s, _c), rec = m.encoder.forward_step(m.patch_embed(torch.randn(B, 3, 50, 50)), _state(B))
    assert len(rec) == 1 and rec[0].shape == (B, 100, 64), "rec must be [Z]"
    print("✓ readout: rec=[Z]; actor AND critic both read Z")


def test_init_action_bias():
    m = _model(init_action_bias=[0.0, -1.5])
    p_press = torch.softmax(m.actor_head([torch.zeros(8, 100, 64)]), dim=-1)[:, 1].mean().item()
    assert 0.05 < p_press < 0.35, f"P(press)≈{p_press:.3f}"
    print(f"✓ init_action_bias: initial P(press) ≈ {p_press:.3f}")


def test_rl_step_and_sequence():
    m = _model()
    step = m.rl_step(torch.randn(1, 3, 50, 50), m.init_states(1, device=DEVICE))
    assert step["actor_logits"].shape == (1, 2) and step["critic_q_dist"].shape == (1, 2, 8)
    out = m.forward_rl_sequence(torch.randn(3, 29, 3, 50, 50))
    assert out["actor_logits_seq"].shape == (3, 29, 2) and out["Ct_seq"].shape == (3, 29, 100, 64)
    print("✓ rl_step + forward_rl_sequence: shapes correct")


def test_grad_flows_through_stack_not_codebook():
    m = _model()
    with torch.no_grad():                      # consolidated C_base so Q3=W_q3·C_base carries grad to W_q3
        m.encoder.codebook.copy_(torch.randn_like(m.encoder.codebook))
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    out = m.forward_rl_sequence(batch.observations)
    loss = out["actor_logits_seq"].pow(2).mean() + out["q_dist_seq"].pow(2).mean() + out["gate_seq"].mean()
    m.zero_grad(); loss.backward()
    assert m.patch_embed.proj[0].weight.grad.abs().sum() > 0, "no grad to patch embed"
    for nm, p in (("W_q3", m.encoder.W_q3), ("W_k3", m.encoder.W_k3), ("W_v3", m.encoder.W_v3),
                  ("W_gate", m.encoder.W_gate), ("W_q", m.encoder.W_q), ("W_k", m.encoder.W_k)):
        assert p.weight.grad is not None and p.weight.grad.abs().sum() > 0, f"no grad to {nm}"
    assert m.encoder.cell2.weight_ih.grad.abs().sum() > 0, "no grad to LSTM2"
    assert m.encoder.cell3.weight_ih.grad.abs().sum() > 0, "no grad to LSTM3"
    assert m.encoder.codebook.grad is None, "codebook is a buffer — NO grad (EMA only)"
    assert m.actor_head.trunk[0].weight.grad.abs().sum() > 0 and m.critic_head.trunk[0].weight.grad.abs().sum() > 0
    print("✓ grad reaches patch_embed + write stream + readout + BOTH LSTMs + heads (NOT the codebook)")


def test_ppo_update_consolidates_Ct():
    """The EMA moves C_base (init 0) toward C_t = C_base + gate⊙H3 — nonzero, so the
    codebook fills with the gated write. rate 0 freezes it."""
    m = _model(); env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    before = m.encoder.codebook.clone()
    params_before = [p.detach().clone() for p in m.parameters()]
    res = ppo_update(m, torch.optim.Adam(m.parameters(), lr=1e-3), concat_batches([batch]),
                     PPOConfig(n_epochs=2, per_n_replay=0, codebook_ema_rate=0.1))
    for k in ("loss_gate", "loss_total", "codebook_drift"):
        assert torch.isfinite(torch.tensor(res[k])), f"{k} not finite: {res[k]}"
    assert res["codebook_drift"] > 0.0, "EMA must move C_base toward C_t"
    assert not torch.allclose(m.encoder.codebook, before), "the EMA must move the codebook buffer"
    assert sum(not torch.allclose(a, b.detach()) for a, b in zip(params_before, m.parameters())) > 0
    m2 = _model(); batch2, _ = collect_episodes(m2, env, n_episodes=4, device=DEVICE)
    before2 = m2.encoder.codebook.clone()
    ppo_update(m2, torch.optim.Adam(m2.parameters(), lr=1e-3), concat_batches([batch2]),
               PPOConfig(n_epochs=2, per_n_replay=0, codebook_ema_rate=0.0))
    assert torch.allclose(m2.encoder.codebook, before2), "codebook_ema_rate=0 must freeze the codebook"
    print(f"✓ ppo_update: EMA consolidates C_t into C_base (cbΔ={res['codebook_drift']:.3e}); rate 0 freezes")


def test_train_loop():
    m = _model(); env = ChangeDetectionEnv()
    hist = train(m, env, n_iterations=2, episodes_per_iter=4,
                 cfg=PPOConfig(n_epochs=2, per_n_replay=2, buffer_capacity=16,
                               burn_in_iters=1, gate_coef=0.001, codebook_ema_rate=0.01),
                 device=DEVICE, log_every=1, save_every=999)
    assert len(hist) == 2
    for k in ("loss_gate", "codebook_drift"):
        assert k in hist[-1], f"missing {k}"
    print("✓ train(): 2 end-to-end iters with the gated write + content EMA")


if __name__ == "__main__":
    tests = [
        test_patch_embed_shapes,
        test_codebook_is_ema_buffer_init_zero,
        test_structure_gated_write_stream,
        test_state_two_lstms,
        test_ema_update_codebook_toward_target,
        test_write_stream_reads_X_and_H3,
        test_gate_in_unit_interval_and_Ct,
        test_readout_reads_Ct,
        test_gate_cost_differentiable_codebook_no_grad,
        test_sequence_exposes_Ct_and_gate,
        test_Z_to_both_heads_and_rec,
        test_init_action_bias,
        test_rl_step_and_sequence,
        test_grad_flows_through_stack_not_codebook,
        test_ppo_update_consolidates_Ct,
        test_train_loop,
    ]
    for t in tests:
        t()
    print(f"\nAll {len(tests)} v12_part3 smoke tests passed "
          f"(gated image-content write stream + VQ-VAE EMA codebook toward C_t).")
