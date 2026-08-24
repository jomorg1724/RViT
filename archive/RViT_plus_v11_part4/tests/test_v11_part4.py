"""
Smoke tests for RViT+ v11_part4 — TWO PERFECTLY PARALLEL recurrent cross-attention
modules (NO cross-talk), split readout, single head each.

  μ SALIENCE: Q=X, K=V=Hμ, residual=X ; Hμ←LSTM_μ(Zμ)  → ACTOR
  Q TOP-DOWN: Q=X, K=V=HQ, residual=HQ; HQ←LSTM_Q(ZQ)  → CRITIC
  The two modules share ONLY X — neither reads/writes the other's memory.

Run:  .venv/bin/python -m RViT_plus_v11_part4.tests.test_v11_part4
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

from RViT_plus_v11_part4.env import ChangeDetectionEnv
from RViT_plus_v11_part4.tx_lstm_encoder import DualStreamEncoder
from RViT_plus_v11_part4.model import RViTPlusV11Part4Model
from RViT_plus_v11_part4.ppo import (
    PPOConfig, collect_episodes, concat_batches, ppo_update, train,
)

DEVICE = torch.device("cpu")
torch.manual_seed(0)


def _model(**over):
    kw = dict(patch_size=5, d_model=64, d_mem=64, tx_heads=1, tx_layers=1, n_lstm=2,
              conv_channels=32, n_conv_layers=3, conv_kernel=5, n_actions=2, n_quantiles=8,
              init_action_bias=[0.0, -1.5], seq_len=29)
    kw.update(over)
    return RViTPlusV11Part4Model(**kw).to(DEVICE)


def test_patch_embed_shapes():
    m = _model()
    tok = m.patch_embed(torch.randn(3, 3, 50, 50))
    assert tok.shape == (3, 100, 64) and m.n_tokens == 100
    print("✓ patch_embed: (3,3,50,50) → (3,100,64); n_tokens=100")


def test_parallel_module_structure():
    m = _model(tx_heads=1)
    enc = m.encoder
    assert isinstance(enc, DualStreamEncoder)
    assert enc.mu_block.attn.num_heads == 1 and enc.q_block.attn.num_heads == 1, "single head per module"
    assert enc.mu_pos_emb.shape == (1, 100, 64) and enc.q_pos_emb.shape == (1, 100, 64), "each module has its OWN pos emb"
    assert not hasattr(enc, "sal_tag"), "no shared salience source-tags (each module reads a single memory)"
    assert enc.stream_dim == 64
    assert len(enc.cells) == 2 and enc.cell_mu.input_size == 64 and enc.cell_q.input_size == 64
    try:
        DualStreamEncoder(n_tokens=100, d_model=64, d_mem=64, n_heads=1, n_lstm=3)
        raise AssertionError("n_lstm=3 should raise")
    except ValueError:
        pass
    print("✓ structure: two independent modules (single head, own pos-emb, own LSTM), no sal_tag")


def test_no_cross_talk_attention():
    """The headline property: each module attends over ONLY its own memory, so
    changing Hμ moves ONLY μ's weights and changing HQ moves ONLY Q's weights.
    Both attn maps are (B,1,N,N) — each module reads N keys (its own memory)."""
    m = _model().eval()
    states = m.init_states(2, device=DEVICE)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    with torch.no_grad():
        (Hs, Cs), rec, attn = m.encoder.forward_step(tok, states, return_attn=True)
        assert rec[0].shape == (2, 100, 64) and rec[1].shape == (2, 100, 64)
        assert attn[0].shape == (2, 1, 100, 100) and attn[1].shape == (2, 1, 100, 100), \
            f"each module reads its own N keys; got {tuple(attn[0].shape)},{tuple(attn[1].shape)}"
        # change Hμ only → μ weights move, Q weights UNCHANGED
        st_mu = ([torch.randn(2, 100, 64), states[0][1]], [states[1][0], states[1][1]])
        _s, _r, attn_mu = m.encoder.forward_step(tok, st_mu, return_attn=True)
        assert not torch.allclose(attn[0], attn_mu[0]), "Hμ change did not move μ weights"
        assert torch.allclose(attn[1], attn_mu[1]), "Hμ change leaked into Q weights — cross-talk!"
        # change HQ only → Q weights move, μ weights UNCHANGED
        st_q = ([states[0][0], torch.randn(2, 100, 64)], [states[1][0], states[1][1]])
        _s, _r, attn_q = m.encoder.forward_step(tok, st_q, return_attn=True)
        assert not torch.allclose(attn[1], attn_q[1]), "HQ change did not move Q weights"
        assert torch.allclose(attn[0], attn_q[0]), "HQ change leaked into μ weights — cross-talk!"
    print("✓ NO cross-talk (attention): Hμ→μ only, HQ→Q only; each reads its own N keys")


def test_no_cross_talk_memory_updates():
    """Each memory is written by its OWN output: changing one module's previous
    memory changes ONLY that module's new memory, never the other's."""
    m = _model().eval()
    B = 3
    tok = m.patch_embed(torch.randn(B, 3, 50, 50))
    states = m.init_states(B, device=DEVICE)
    with torch.no_grad():
        (Hs, Cs), _rec = m.encoder.forward_step(tok, states)
        # change Hμ_prev only → new Hμ changes, new HQ UNCHANGED
        st_mu = ([torch.randn(B, 100, 64), states[0][1]], [states[1][0], states[1][1]])
        (Hs_mu, _), _ = m.encoder.forward_step(tok, st_mu)
        assert not torch.allclose(Hs[0], Hs_mu[0]), "new Hμ unaffected by Hμ_prev"
        assert torch.allclose(Hs[1], Hs_mu[1]), "new HQ moved when only Hμ_prev changed — cross-talk!"
        # change HQ_prev only → new HQ changes, new Hμ UNCHANGED
        st_q = ([states[0][0], torch.randn(B, 100, 64)], [states[1][0], states[1][1]])
        (Hs_q, _), _ = m.encoder.forward_step(tok, st_q)
        assert not torch.allclose(Hs[1], Hs_q[1]), "new HQ unaffected by HQ_prev"
        assert torch.allclose(Hs[0], Hs_q[0]), "new Hμ moved when only HQ_prev changed — cross-talk!"
        # shared input X moves BOTH
        tok_b = m.patch_embed(torch.randn(B, 3, 50, 50))
        (Hs_b, _), _ = m.encoder.forward_step(tok_b, states)
        assert not torch.allclose(Hs[0], Hs_b[0]) and not torch.allclose(Hs[1], Hs_b[1])
    print("✓ NO cross-talk (memory): Hμ←Zμ, HQ←ZQ independently; X moves both")


def test_mu_grounded_q_gating_only():
    m = _model().eval()
    enc_cut = copy.deepcopy(m.encoder).eval()
    with torch.no_grad():
        for blk in (enc_cut.mu_block, enc_cut.q_block):
            blk.attn.out_proj.weight.zero_(); blk.attn.out_proj.bias.zero_()
    tok_a = m.patch_embed(torch.randn(2, 3, 50, 50))
    tok_b = m.patch_embed(torch.randn(2, 3, 50, 50) * 3.0 + 1.0)
    with torch.no_grad():
        st0 = enc_cut.init_states(2)
        (_h, _c), rec_a = enc_cut.forward_step(tok_a, st0)
        (_h2, _c2), rec_b = enc_cut.forward_step(tok_b, st0)
        assert not torch.allclose(rec_a[0], rec_b[0]), "μ Zμ image-invariant with attention off — residual=X missing"
        assert torch.allclose(rec_a[1], rec_b[1], atol=1e-6), "Q ZQ changed with image despite silenced attention"
        (_h3, _c3), rec_c = m.encoder.forward_step(tok_a, m.init_states(2))
        (_h4, _c4), rec_d = m.encoder.forward_step(tok_b, m.init_states(2))
        assert not torch.allclose(rec_c[1], rec_d[1]), "intact attention should let the image gate Q"
    print("✓ μ stays image-grounded (residual=X); Q is gating-only (residual=HQ)")


def test_split_readout():
    m = _model().eval()
    B = 4
    zmu, zq = torch.randn(B, 100, 64), torch.randn(B, 100, 64)
    with torch.no_grad():
        al, q, _, _ = m._run_heads([zmu, zq])
        assert al.shape == (B, 2) and q.shape == (B, 2, 8)
        al2, q2, _, _ = m._run_heads([torch.randn(B, 100, 64), zq])
        assert not torch.allclose(al, al2) and torch.allclose(q, q2), "actor must read Zμ only"
        al3, q3, _, _ = m._run_heads([zmu, torch.randn(B, 100, 64)])
        assert torch.allclose(al, al3) and not torch.allclose(q, q3), "critic must read ZQ only"
    print("✓ split readout: actor←Zμ, critic←ZQ; each ignores the other module")


def test_conv_heads_single_stream():
    import torch.nn as nn
    m = _model(n_conv_layers=3, conv_channels=32)
    for name, dec in (("actor", m.actor_head), ("critic", m.critic_head)):
        convs = [mod for mod in dec.trunk if isinstance(mod, nn.Conv1d)]
        assert len(convs) == 3 and convs[0].in_channels == 64, f"{name}: single-stream in_ch=d_model=64, 3 convs"
    assert m.actor_head.out.out_features == 2 and m.critic_head.out.out_features == 2 * 8
    print("✓ conv heads: single-stream (in_ch=d_model=64), 3 stride-2 Conv1d each")


def test_init_action_bias():
    m = _model(init_action_bias=[0.0, -1.5])
    p_press = torch.softmax(m.actor_head([torch.zeros(8, 100, 64)]), dim=-1)[:, 1].mean().item()
    assert 0.05 < p_press < 0.35, f"P(press)≈{p_press:.3f} not in expected band"
    print(f"✓ init_action_bias: initial P(press) ≈ {p_press:.3f}")


def test_rl_step_and_sequence():
    m = _model()
    step = m.rl_step(torch.randn(1, 3, 50, 50), m.init_states(1, device=DEVICE))
    assert step["actor_logits"].shape == (1, 2) and step["critic_q_dist"].shape == (1, 2, 8)
    B, T = 3, 29
    out = m.forward_rl_sequence(torch.randn(B, T, 3, 50, 50))
    assert out["actor_logits_seq"].shape == (B, T, 2) and out["q_dist_seq"].shape == (B, T, 2, 8)
    assert out["V_dist_seq"].shape == (B, T, 8) and out["V_scalar_seq"].shape == (B, T)
    print("✓ rl_step + forward_rl_sequence: all RL-interface shapes correct")


def test_grad_flows_through_stack():
    m = _model()
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    out = m.forward_rl_sequence(batch.observations)
    loss = out["actor_logits_seq"].pow(2).mean() + out["q_dist_seq"].pow(2).mean()
    m.zero_grad(); loss.backward()
    assert m.patch_embed.proj[0].weight.grad.abs().sum() > 0, "no grad to patch embed"
    assert m.encoder.mu_block.attn.in_proj_weight.grad.abs().sum() > 0, "no grad to μ attention"
    assert m.encoder.q_block.attn.in_proj_weight.grad.abs().sum() > 0, "no grad to Q attention"
    assert m.encoder.mu_pos_emb.grad is not None and m.encoder.mu_pos_emb.grad.abs().sum() > 0, "no grad to μ pos-emb"
    assert m.encoder.q_pos_emb.grad is not None and m.encoder.q_pos_emb.grad.abs().sum() > 0, "no grad to Q pos-emb"
    for nm, cell in (("μ", m.encoder.cell_mu), ("Q", m.encoder.cell_q)):
        assert cell.weight_ih.grad is not None and cell.weight_ih.grad.abs().sum() > 0, f"no grad to LSTM_{nm}"
    assert m.actor_head.trunk[0].weight.grad.abs().sum() > 0 and m.critic_head.trunk[0].weight.grad.abs().sum() > 0
    print("✓ gradient reaches patch_embed + BOTH modules' attn/pos/LSTM + both heads")


def test_ppo_update_changes_params_and_is_finite():
    m = _model()
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    before = [p.detach().clone() for p in m.parameters()]
    res = ppo_update(m, torch.optim.Adam(m.parameters(), lr=1e-3), concat_batches([batch]),
                     PPOConfig(n_epochs=2, per_n_replay=0))
    for k in ("loss_policy", "loss_value", "loss_entropy", "loss_total"):
        assert torch.isfinite(torch.tensor(res[k])), f"{k} not finite: {res[k]}"
    changed = sum(not torch.allclose(a, b.detach()) for a, b in zip(before, m.parameters()))
    assert changed > 0
    print(f"✓ ppo_update: finite losses, {changed} param tensors moved")


def test_pac_target_network_and_burn_in():
    env = ChangeDetectionEnv()
    m2 = _model()
    actor_before = {k: v.clone() for k, v in m2.actor_head.state_dict().items()}
    critic_before = {k: v.clone() for k, v in m2.critic_head.state_dict().items()}
    hist = train(m2, env, n_iterations=2, episodes_per_iter=4,
                 cfg=PPOConfig(n_epochs=2, per_n_replay=0, burn_in_iters=2, target_update_period=0),
                 device=DEVICE, log_every=1, save_every=999)
    assert all(h["rollout/mean_length"] == 29.0 for h in hist), "forced-wait episodes must run full length"
    assert all(torch.allclose(actor_before[k], m2.actor_head.state_dict()[k]) for k in actor_before), \
        "actor changed during burn-in (must be frozen)"
    assert any(not torch.allclose(critic_before[k], m2.critic_head.state_dict()[k]) for k in critic_before), \
        "critic did not move during burn-in"
    print("✓ PAC target network + burn-in: burn-in freezes actor, trains critic")


def test_end_to_end_train_iteration():
    m = _model()
    env = ChangeDetectionEnv()
    cfg = PPOConfig(n_epochs=2, per_n_replay=2, buffer_capacity=16, burn_in_iters=0)
    hist = train(m, env, n_iterations=2, episodes_per_iter=4, cfg=cfg,
                 device=DEVICE, log_every=1, save_every=999)
    assert len(hist) == 2 and hist[-1]["per_n_replay_used"] == 2
    print("✓ end-to-end train(): 2 iters incl. PER replay sampling")


if __name__ == "__main__":
    tests = [
        test_patch_embed_shapes,
        test_parallel_module_structure,
        test_no_cross_talk_attention,
        test_no_cross_talk_memory_updates,
        test_mu_grounded_q_gating_only,
        test_split_readout,
        test_conv_heads_single_stream,
        test_init_action_bias,
        test_rl_step_and_sequence,
        test_grad_flows_through_stack,
        test_ppo_update_changes_params_and_is_finite,
        test_pac_target_network_and_burn_in,
        test_end_to_end_train_iteration,
    ]
    for t in tests:
        t()
    print(f"\nAll {len(tests)} v11_part4 smoke tests passed (incl. the NO-cross-talk proofs).")
