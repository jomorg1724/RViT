"""
Smoke tests for RViT+ v12_part2 — an ADAPTIVE codebook with an energetic
maintenance cost. The static learnable codebook C_base is deformed each frame by
an energy-modulation transformer (Q=codebook, K=V=[X‖H2], codebook = residual),
the deformation D decays back toward 0 (a leaky integrator), and the readout
attends over the ADAPTED codebook C_t = C_base + D_t. The maintenance cost
mean‖D_t‖² is exposed as energy_seq for the energetic-cost loss term.

Run:  .venv/bin/python -m RViT_plus_v12_part2.tests.test_v12_part2
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

from RViT_plus_v12_part2.env import ChangeDetectionEnv
from RViT_plus_v12_part2.tx_lstm_encoder import VQAttnEncoder
from RViT_plus_v12_part2.model import RViTPlusV12Part2Model
from RViT_plus_v12_part2.ppo import (
    PPOConfig, collect_episodes, concat_batches, ppo_update, train,
)

DEVICE = torch.device("cpu")
torch.manual_seed(0)


def _model(**over):
    kw = dict(patch_size=5, d_model=64, d_mem=64, tx_heads=1, tx_layers=1, n_lstm=1,
              conv_channels=32, n_conv_layers=3, conv_kernel=5, n_actions=2, n_quantiles=8,
              init_action_bias=[0.0, -1.5], seq_len=29, codebook_decay=0.9, temperature=1.0)
    kw.update(over)
    return RViTPlusV12Part2Model(**kw).to(DEVICE)


def _state(B, N=100, d=64, D=None):
    """State = (Hs=[H2, D], Cs=[C2, 0]). D defaults to zeros (codebook = static)."""
    H2 = torch.randn(B, N, d)
    C2 = torch.randn(B, N, d)
    Dt = torch.zeros(B, N, d) if D is None else D
    return [H2, Dt], [C2, torch.zeros_like(Dt)]


def _activate_energy(m, std=0.1):
    """The energy branch's output (E_W_o + the FFN's last layer) is zero-initialized
    so the block starts as identity (energy≡0, D stays 0 at init). Re-init those
    output weights to nonzero to simulate a trained/ACTIVE energy module, so routing
    and gradient WIRING can be exercised — otherwise the zero output legitimately
    blocks the path that feeds E_W_q/E_W_k/E_W_v."""
    with torch.no_grad():
        torch.nn.init.normal_(m.encoder.E_W_o.weight, std=std)
        torch.nn.init.normal_(m.encoder.E_W_o.bias, std=std)
        torch.nn.init.normal_(m.encoder.E_ffn[-1].weight, std=std)
        torch.nn.init.normal_(m.encoder.E_ffn[-1].bias, std=std)
    return m


def test_patch_embed_shapes():
    m = _model()
    tok = m.patch_embed(torch.randn(3, 3, 50, 50))
    assert tok.shape == (3, 100, 64) and m.n_tokens == 100
    print("✓ patch_embed: (3,3,50,50) → (3,100,64); n_tokens=100")


def test_structure_adaptive_codebook():
    m = _model(tx_heads=1)
    enc = m.encoder
    assert isinstance(enc, VQAttnEncoder)
    assert enc.codebook.shape == (1, 100, 64) and isinstance(enc.codebook, torch.nn.Parameter)
    # energy-modulation transformer present (Q/K/V/O + FFN)
    for nm in ("E_W_q", "E_W_k", "E_W_v", "E_W_o"):
        assert hasattr(enc, nm), f"missing energy projection {nm}"
    assert hasattr(enc, "E_ffn") and hasattr(enc, "src_emb")
    assert enc.src_emb.shape == (3, 64), "modality tags: codebook-query / X-key / H2-key"
    # readout block: NO value projection (values ARE the adapted codebook)
    assert not hasattr(enc, "W_v"), "readout has no W_v — values are the codebook"
    assert len(enc.cells) == 1 and enc.cell.input_size == 64, "ONE LSTM (the keys H2)"
    assert abs(enc.codebook_decay - 0.9) < 1e-9
    for bad in (dict(n_lstm=2), dict(n_heads=5), dict(codebook_decay=1.5), dict(codebook_decay=1.0)):
        try:
            VQAttnEncoder(n_tokens=100, d_model=64, d_mem=64, **bad)
            raise AssertionError(f"{bad} should raise")
        except ValueError:
            pass
    print("✓ structure: static codebook + energy transformer (Q/K/V/O+FFN+src tags), ONE LSTM, guards (decay<1)")


def test_state_starts_static():
    m = _model()
    Hs, Cs = m.init_states(2, device=DEVICE)
    assert len(Hs) == 2 and len(Cs) == 2, "state carries [H2, D] / [C2, 0]"
    H2_0, D_0 = Hs
    assert torch.count_nonzero(D_0) == 0, "deviation D starts at 0 — codebook begins exactly static"
    assert D_0.shape == (2, 100, 64)
    print("✓ init state: D_0 = 0 (codebook starts static); state = [H2, D] / [C2, 0]")


def test_codebook_decays_to_static():
    """With the energy block forced to inject nothing, D is a pure leaky integrator
    D_t = decay·D_{t-1} → the codebook relaxes back to the static table."""
    m = _model(codebook_decay=0.8).eval()
    enc = copy.deepcopy(m.encoder).eval()
    with torch.no_grad():                       # silence the energy block: energy ≡ 0
        enc.E_W_o.weight.zero_(); enc.E_W_o.bias.zero_()
        enc.E_ffn[3].weight.zero_(); enc.E_ffn[3].bias.zero_()
    D_prev = torch.randn(2, 100, 64)
    states = _state(2, D=D_prev)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    with torch.no_grad():
        (Hs, _Cs), _rec = enc.forward_step(tok, states)
        D_t = Hs[1]
        assert torch.allclose(D_t, 0.8 * D_prev, atol=1e-5), "no energy ⇒ D_t must equal decay·D_prev"
        # iterate: D → decay^k · D_prev → 0
        st = states; last = D_prev
        for _ in range(20):
            st, _r = enc.forward_step(tok, st)      # st = full (Hs, Cs) state
            last = st[0][1]                         # D_t = Hs[1]
        assert last.abs().max() < D_prev.abs().max(), "deviation must shrink toward 0"
        assert last.abs().mean() < 0.1 * D_prev.abs().mean(), "deviation must largely decay away"
    print("✓ decay: with no energy, D_t = decay·D_{t-1} → codebook relaxes to the static table")


def test_energy_zero_at_init():
    """Zero-init of the energy branch ⇒ at init the block injects nothing: from the
    resting state (D_0=0) the deviation stays 0 and the maintenance cost is 0, so the
    model begins EXACTLY as the static-codebook readout and only adapts once trained."""
    m = _model().eval()
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    (Hs, _c), _rec = m.encoder.forward_step(tok, m.init_states(2, device=DEVICE))
    assert Hs[1].abs().max() < 1e-6, "energy branch must inject 0 at init → D_t stays 0"
    assert float(m.encoder.last_energy_cost.max()) < 1e-10, "maintenance cost must be 0 at init"
    print("✓ zero-init: energy ≡ 0 at init → D stays 0 (model starts as the static-codebook readout)")


def test_energy_block_reads_X_and_H2():
    """The energy that deforms the codebook depends on BOTH X and H2 (K=V=[X‖H2])."""
    m = _activate_energy(_model().eval())   # energy branch is zero-init; activate to test routing
    states = _state(2)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    with torch.no_grad():
        (Hs0, _c0), _r0 = m.encoder.forward_step(tok, states)
        D0 = Hs0[1]
        # perturb H2 only (D_prev and X held)
        st_h2 = ([torch.randn(2, 100, 64), states[0][1]], states[1])
        (Hs1, _c1), _r1 = m.encoder.forward_step(tok, st_h2)
        assert not torch.allclose(D0, Hs1[1]), "H2 must move the injected energy (energy K/V include H2)"
        # perturb X only
        tok_b = m.patch_embed(torch.randn(2, 3, 50, 50))
        (Hs2, _c2), _r2 = m.encoder.forward_step(tok_b, states)
        assert not torch.allclose(D0, Hs2[1]), "X must move the injected energy (energy K/V include X)"
    print("✓ energy block: deformation D responds to BOTH X and H2 (K=V=[X‖H2])")


def test_readout_reads_adapted_codebook():
    """Holding the readout queries/keys fixed (same X, same H2), changing the
    codebook deviation D changes the readout output Z but NOT the readout weights —
    so Z reads the ADAPTED codebook as its VALUES."""
    m = _model().eval()
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    H2 = torch.randn(2, 100, 64); C2 = torch.randn(2, 100, 64)
    s_a = ([H2, torch.zeros(2, 100, 64)], [C2, torch.zeros(2, 100, 64)])
    s_b = ([H2, torch.randn(2, 100, 64)], [C2, torch.zeros(2, 100, 64)])   # different D only
    with torch.no_grad():
        (_a, _ca), rec_a, attn_a = m.encoder.forward_step(tok, s_a, return_attn=True)
        (_b, _cb), rec_b, attn_b = m.encoder.forward_step(tok, s_b, return_attn=True)
        assert torch.allclose(attn_a[0], attn_b[0], atol=1e-6), "readout weights depend on X,H2 only — not D"
        assert not torch.allclose(rec_a[0], rec_b[0]), "Z must change with D (values = adapted codebook)"
        # the static codebook param is also a value source
        enc2 = copy.deepcopy(m.encoder).eval()
        with torch.no_grad():
            enc2.codebook.copy_(torch.randn_like(enc2.codebook))
        (_c, _cc), rec_c = enc2.forward_step(tok, s_a)
        assert not torch.allclose(rec_a[0], rec_c[0]), "the static codebook must change Z too"
    print("✓ readout: Z reads the ADAPTED codebook as VALUES (D changes Z, not the readout weights)")


def test_energy_cost_exposed_and_differentiable():
    m = _activate_energy(_model().eval())   # activate so grad can reach E_W_q/k/v through E_W_o
    states = _state(2, D=torch.randn(2, 100, 64))
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    (Hs, _c), _rec = m.encoder.forward_step(tok, states)
    cost = m.encoder.last_energy_cost                 # (B,) mean‖D_t‖²
    assert cost.shape == (2,)
    assert torch.allclose(cost, Hs[1].pow(2).mean(dim=(1, 2)), atol=1e-6), "cost must be mean‖D_t‖²"
    m.zero_grad(); cost.sum().backward()
    for nm in ("E_W_q", "E_W_k", "E_W_v", "E_W_o"):
        g = getattr(m.encoder, nm).weight.grad
        assert g is not None and g.abs().sum() > 0, f"energy cost must push gradient into {nm}"
    # The maintenance penalty must shrink the DEVIATION, not edit the static table
    # it decays toward (C_base is detached in the energy block).
    cg = m.encoder.codebook.grad
    assert cg is None or cg.abs().sum() == 0, "maintenance penalty leaked into the static codebook C_base"
    print("✓ energy cost: mean‖D_t‖² (B,) → grad into the energy transformer, NOT into static C_base")


def test_energy_seq_in_sequence():
    m = _activate_energy(_model())   # zero-init energy gives energy_seq≡0; activate to test the grad path
    out = m.forward_rl_sequence(torch.randn(3, 29, 3, 50, 50))
    es = out["energy_seq"]
    assert es.shape == (3, 29), "energy_seq must be (B, T)"
    assert es.requires_grad, "energy_seq must be differentiable"
    m.zero_grad(); es.sum().backward()
    assert m.encoder.E_W_q.weight.grad.abs().sum() > 0, "energy_seq grad must reach the energy block"
    print("✓ forward_rl_sequence: returns differentiable energy_seq (B,T) wired to the energy block")


def test_Z_to_both_heads_and_rec():
    m = _model().eval()
    B = 4
    Z1, Z2 = torch.randn(B, 100, 64), torch.randn(B, 100, 64)
    with torch.no_grad():
        al1, q1, _, _ = m._run_heads([Z1])
        al2, q2, _, _ = m._run_heads([Z2])
        assert al1.shape == (B, 2) and q1.shape == (B, 2, 8)
        assert not torch.allclose(al1, al2) and not torch.allclose(q1, q2), "both heads must read Z"
    (_s, _c), rec = m.encoder.forward_step(m.patch_embed(torch.randn(B, 3, 50, 50)), _state(B))
    assert len(rec) == 1 and rec[0].shape == (B, 100, 64), "rec must be [Z]"
    print("✓ readout: rec=[Z]; actor AND critic both read Z")


def test_init_action_bias():
    m = _model(init_action_bias=[0.0, -1.5])
    p_press = torch.softmax(m.actor_head([torch.zeros(8, 100, 64)]), dim=-1)[:, 1].mean().item()
    assert 0.05 < p_press < 0.35, f"P(press)≈{p_press:.3f} not in expected band"
    print(f"✓ init_action_bias: initial P(press) ≈ {p_press:.3f}")


def test_rl_step_and_sequence():
    m = _model()
    step = m.rl_step(torch.randn(1, 3, 50, 50), m.init_states(1, device=DEVICE))
    assert step["actor_logits"].shape == (1, 2) and step["critic_q_dist"].shape == (1, 2, 8)
    out = m.forward_rl_sequence(torch.randn(3, 29, 3, 50, 50))
    assert out["actor_logits_seq"].shape == (3, 29, 2) and out["q_dist_seq"].shape == (3, 29, 2, 8)
    assert out["energy_seq"].shape == (3, 29)
    print("✓ rl_step + forward_rl_sequence: shapes correct (+ energy_seq)")


def test_grad_flows_through_stack():
    m = _activate_energy(_model())   # activate the energy branch so grad reaches E_W_q/k/v
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    out = m.forward_rl_sequence(batch.observations)
    loss = (out["actor_logits_seq"].pow(2).mean() + out["q_dist_seq"].pow(2).mean()
            + out["energy_seq"].mean())
    m.zero_grad(); loss.backward()
    assert m.patch_embed.proj[0].weight.grad.abs().sum() > 0, "no grad to patch embed"
    for nm, p in (("E_W_q", m.encoder.E_W_q), ("E_W_k", m.encoder.E_W_k), ("E_W_v", m.encoder.E_W_v),
                  ("W_q", m.encoder.W_q), ("W_k", m.encoder.W_k), ("W_o", m.encoder.W_o)):
        assert p.weight.grad is not None and p.weight.grad.abs().sum() > 0, f"no grad to {nm}"
    assert m.encoder.cell.weight_ih.grad.abs().sum() > 0, "no grad to the H2 LSTM"
    assert m.encoder.codebook.grad is not None and m.encoder.codebook.grad.abs().sum() > 0, "no grad to codebook"
    assert m.actor_head.trunk[0].weight.grad.abs().sum() > 0 and m.critic_head.trunk[0].weight.grad.abs().sum() > 0
    print("✓ gradient reaches patch_embed + energy block + readout + H2 LSTM + codebook + both heads")


def test_ppo_update_includes_energy():
    m = _activate_energy(_model())   # active energy branch → nonzero deviation to penalize
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    before = [p.detach().clone() for p in m.parameters()]
    res = ppo_update(m, torch.optim.Adam(m.parameters(), lr=1e-3), concat_batches([batch]),
                     PPOConfig(n_epochs=2, per_n_replay=0, energy_coef=0.05))
    for k in ("loss_policy", "loss_value", "loss_entropy", "loss_energy", "loss_total"):
        assert torch.isfinite(torch.tensor(res[k])), f"{k} not finite: {res[k]}"
    assert res["loss_energy"] > 0.0, "energy term should be positive at random init (D≠0 after a step)"
    assert sum(not torch.allclose(a, b.detach()) for a, b in zip(before, m.parameters())) > 0
    print(f"✓ ppo_update: energy term present (L_eng={res['loss_energy']:.4f}), finite losses, params move")


def test_train_loop():
    m = _model()
    env = ChangeDetectionEnv()
    hist = train(m, env, n_iterations=2, episodes_per_iter=4,
                 cfg=PPOConfig(n_epochs=2, per_n_replay=2, buffer_capacity=16,
                               burn_in_iters=1, energy_coef=0.02),
                 device=DEVICE, log_every=1, save_every=999)
    assert len(hist) == 2 and "loss_energy" in hist[-1]
    print("✓ train(): 2 end-to-end iters with the energetic-cost term")


if __name__ == "__main__":
    tests = [
        test_patch_embed_shapes,
        test_structure_adaptive_codebook,
        test_state_starts_static,
        test_codebook_decays_to_static,
        test_energy_zero_at_init,
        test_energy_block_reads_X_and_H2,
        test_readout_reads_adapted_codebook,
        test_energy_cost_exposed_and_differentiable,
        test_energy_seq_in_sequence,
        test_Z_to_both_heads_and_rec,
        test_init_action_bias,
        test_rl_step_and_sequence,
        test_grad_flows_through_stack,
        test_ppo_update_includes_energy,
        test_train_loop,
    ]
    for t in tests:
        t()
    print(f"\nAll {len(tests)} v12_part2 smoke tests passed "
          f"(adaptive codebook: energy modulation + decay + energetic-cost loss).")
