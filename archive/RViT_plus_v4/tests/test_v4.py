"""
Smoke tests for RViT+ v4: shapes through the conv-free patch + FiLM FEEDBACK
encoder + transformer-decoder actor-critic, plus one end-to-end PAC/QR-DQN
update and one full training iteration on the real env.

v4 is IDENTICAL to v5 except the encoder (FiLM feedback transformer instead of
memory-as-tokens), so most tests are shared; only the two encoder-structure
tests differ.

Run:  .venv/bin/python -m RViT_plus_v4.tests.test_v4
"""
from __future__ import annotations

import os
import sys

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v4.env import ChangeDetectionEnv
from RViT_plus_v4.feedback_transformer import FeedbackTransformerEncoder
from RViT_plus_v4.model import RViTPlusV4Model
from RViT_plus_v4.ppo import (
    PPOConfig, collect_episodes, concat_batches, ppo_update, train,
)

DEVICE = torch.device("cpu")
torch.manual_seed(0)


def _model(**over):
    kw = dict(patch_size=5, d_model=64, d_mem=64, enc_heads=4, enc_layers=2,
              dec_heads=4, dec_layers=2, n_actions=2, n_quantiles=8,
              init_action_bias=[0.0, -1.5], seq_len=29)
    kw.update(over)
    return RViTPlusV4Model(**kw).to(DEVICE)


def test_patch_embed_shapes():
    m = _model()
    x = torch.randn(3, 3, 50, 50)
    tok = m.patch_embed(x)
    assert tok.shape == (3, 100, 64), tok.shape
    assert m.n_tokens == 100
    print("✓ patch_embed: (3,3,50,50) → (3,100,64); n_tokens=100 (10×10 grid)")


def test_film_structure():
    """The encoder must be the FiLM feedback transformer: each block has FiLM
    gates fq/fk/fv (producing gain,bias from the memory projection), sensory
    projections qx/kx/vx, a shared LSTMCell memory updater, and the gain is
    CENTERED AT 1 (the +1 fix) so the attention gate starts OPEN at init."""
    m = _model()
    enc = m.encoder
    assert isinstance(enc, FeedbackTransformerEncoder)
    assert len(enc.blocks) == enc.n_layers
    blk = enc.blocks[0]
    for proj in ("qx", "kx", "vx", "qh", "kh", "vh", "fq", "fk", "fv"):
        assert hasattr(blk, proj), f"FiLM block missing projection {proj}"
    assert isinstance(blk.cell, torch.nn.LSTMCell), "expected a shared LSTMCell memory updater per block"
    # FiLM gain centered at 1: with near-zero `film` init, the effective gate
    # (1+g) is ~1 (OPEN), not ~0 (closed → uniform-attention collapse).
    Hm = torch.randn(2, m.n_tokens, enc.d_mem)
    g, _b = blk.fq(blk.qh(Hm)).chunk(2, dim=-1)
    gate = (1.0 + g).mean().item()
    assert 0.8 < gate < 1.2, f"FiLM gate (1+g) mean ≈ {gate:.3f}, expected ~1.0 (gate open at init)"
    print(f"✓ FiLM structure: fq/fk/fv gates + qx/qh proj + shared LSTMCell; gain centered at 1 (gate≈{gate:.3f})")


def test_encoder_attends_over_N():
    """v4's FiLM attention is token×token over the N patch tokens ONLY (memory
    enters through the FiLM gate, not as extra key/value tokens). Verify the
    per-head attention matrix is (B, heads, N, N)."""
    m = _model()
    states = m.init_states(2, device=DEVICE)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    (_Hs, _Cs), _rec, attn = m.encoder.forward_step(tok, states, return_attn=True)
    assert len(attn) == m.enc_layers, "one attention map per layer"
    assert attn[0].shape == (2, 4, 100, 100), \
        f"FiLM attention shape {tuple(attn[0].shape)}, expected (2,4,100,100) = (B,heads,N,N)"
    print(f"✓ encoder attends over N=100 patch tokens (memory via FiLM gate); attn {tuple(attn[0].shape)}")


def test_encoder_recurrence_shapes():
    m = _model()
    B = 4
    states = m.init_states(B, device=DEVICE)
    Hs, Cs = states
    assert len(Hs) == 2 and len(Cs) == 2
    for H in Hs:
        assert H.shape == (B, 100, 64), H.shape
    tok = m.patch_embed(torch.randn(B, 3, 50, 50))
    new_states, rec = m.encoder.forward_step(tok, states)
    assert len(rec) == 2, "2-layer encoder → 2 recurrent states"
    for H in rec:
        assert H.shape == (B, 100, 64)
    assert not torch.allclose(new_states[0][0], states[0][0]), "layer-1 memory did not update"
    print("✓ encoder: 2 recurrent memories, each (B,100,64); memory updates per step")


def test_decoder_reads_both_states():
    m = _model()
    B = 4
    H1 = torch.randn(B, 100, 64)
    H2 = torch.randn(B, 100, 64)
    logits = m.actor_head([H1, H2])
    q = m.critic_head([H1, H2])
    assert logits.shape == (B, 2), logits.shape
    assert q.shape == (B, 2, 8), q.shape
    assert m.actor_head.n_input == 200, "decoder should ingest 2×n_tokens content tokens"
    V_dist, V_scalar = m.critic_head.derive_V(q, logits)
    assert V_dist.shape == (B, 8) and V_scalar.shape == (B,)
    print("✓ decoders read BOTH states: 2×100=200 (+CLS) tokens → actor (B,2), critic (B,2,8)")


def test_mlp_heads():
    """Each decoder must decode the CLS through a >=2-layer feed-forward MLP,
    not a single Linear; head_layers is configurable."""
    import torch.nn as nn
    m = _model()  # default head_layers=2
    for name, dec in (("actor", m.actor_head), ("critic", m.critic_head)):
        n_lin = sum(isinstance(mod, nn.Linear) for mod in dec.head)
        assert n_lin == 2, f"{name} head has {n_lin} Linear layers; expected 2"
    m3 = _model(head_layers=3, head_hidden=96)
    n_lin3 = sum(isinstance(mod, nn.Linear) for mod in m3.actor_head.head)
    assert n_lin3 == 3, f"head_layers=3 should give 3 Linear layers; got {n_lin3}"
    lins = [mod for mod in m3.actor_head.head if isinstance(mod, nn.Linear)]
    assert lins[0].in_features == 64 and lins[0].out_features == 96
    assert lins[-1].out_features == 2
    print("✓ MLP heads: actor & critic decode CLS through 2 FF layers (configurable: head_layers=3 → 3)")


def test_critic_action_as_input_encoding():
    """Critic conditions on the action at the INPUT via a learned
    (n_actions, n_tokens, d_mem) positional-style encoding, run once per action."""
    m = _model()  # n_actions=2, n_quantiles=8, d_mem=64, n_tokens=100
    crit = m.critic_head
    assert hasattr(crit, "action_emb"), "critic missing action_emb"
    assert crit.action_emb.shape == (2, 100, 64), crit.action_emb.shape
    H1, H2 = torch.randn(4, 100, 64), torch.randn(4, 100, 64)
    q = crit([H1, H2])
    assert q.shape == (4, 2, 8), q.shape
    # Zeroing the action encoding ⇒ both actions see identical input ⇒ identical Q.
    crit.eval()
    with torch.no_grad():
        saved = crit.action_emb.clone()
        crit.action_emb.zero_()
        q0 = crit([H1, H2])
        assert torch.allclose(q0[:, 0], q0[:, 1], atol=1e-5), \
            "actions differ with zero action_emb — conditioning isn't coming from it"
        crit.action_emb.copy_(saved)
    crit.train()
    crit([H1, H2]).pow(2).mean().backward()
    assert crit.action_emb.grad is not None and crit.action_emb.grad.abs().sum() > 0
    print("✓ critic action-encoding: action_emb (2,100,64) added at input; zeroing ⇒ Q equal across actions; grad flows")


def test_init_action_bias():
    m = _model(init_action_bias=[0.0, -1.5])
    H1 = torch.zeros(8, 100, 64)
    H2 = torch.zeros(8, 100, 64)
    logits = m.actor_head([H1, H2])
    p_press = torch.softmax(logits, dim=-1)[:, 1].mean().item()
    assert 0.05 < p_press < 0.35, f"P(press)≈{p_press:.3f} not in expected init band"
    print(f"✓ init_action_bias: initial P(press) ≈ {p_press:.3f} (mostly-wait)")


def test_rl_step_and_sequence():
    m = _model()
    states = m.init_states(1, device=DEVICE)
    step = m.rl_step(torch.randn(1, 3, 50, 50), states)
    for k in ("new_states", "actor_logits", "critic_q_dist", "V_dist", "V_scalar"):
        assert k in step, k
    assert step["actor_logits"].shape == (1, 2)
    assert step["critic_q_dist"].shape == (1, 2, 8)
    B, T = 3, 29
    out = m.forward_rl_sequence(torch.randn(B, T, 3, 50, 50))
    assert out["actor_logits_seq"].shape == (B, T, 2)
    assert out["q_dist_seq"].shape == (B, T, 2, 8)
    assert out["V_dist_seq"].shape == (B, T, 8)
    assert out["V_scalar_seq"].shape == (B, T)
    assert len(out["states_seq"]) == T
    print("✓ rl_step + forward_rl_sequence: all RL-interface shapes correct")


def test_grad_flows_to_encoder_and_patch_embed():
    """Reward-driven gradient must reach the patch MLP, each FiLM block's sensory
    projection (qx), FiLM gate (fq) and shared LSTMCell — the whole conv-free
    FiLM feedback stack is trained by RL alone."""
    m = _model()
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    out = m.forward_rl_sequence(batch.observations)
    loss = out["actor_logits_seq"].pow(2).mean() + out["q_dist_seq"].pow(2).mean()
    m.zero_grad(); loss.backward()
    g_patch = m.patch_embed.proj[0].weight.grad
    assert g_patch is not None and g_patch.abs().sum() > 0, "no grad to patch embed MLP"
    for li in range(m.enc_layers):
        blk = m.encoder.blocks[li]
        for proj in ("qx", "fq"):
            g = getattr(blk, proj).weight.grad
            assert g is not None and g.abs().sum() > 0, f"no grad to block {li}.{proj}"
        assert blk.cell.weight_ih.grad is not None and blk.cell.weight_ih.grad.abs().sum() > 0, \
            f"no grad to block {li} LSTMCell"
    print("✓ gradient reaches patch_embed + FiLM proj/gate (qx, fq) + LSTMCell, both layers")


def test_ppo_update_changes_params_and_is_finite():
    m = _model()
    env = ChangeDetectionEnv()
    cfg = PPOConfig(n_epochs=2, per_n_replay=0)
    batch, stats = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    combined = concat_batches([batch])
    before = [p.detach().clone() for p in m.parameters()]
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    res = ppo_update(m, opt, combined, cfg)
    for k in ("loss_policy", "loss_value", "loss_entropy", "loss_total"):
        assert torch.isfinite(torch.tensor(res[k])), f"{k} not finite: {res[k]}"
    assert res["n_updates"] >= 1 and res["n_skipped"] == 0
    changed = sum(not torch.allclose(a, b.detach()) for a, b in zip(before, m.parameters()))
    assert changed > 0, "no parameters changed after ppo_update"
    print(f"✓ ppo_update: finite losses, {int(res['n_updates'])} steps, "
          f"{changed} param tensors moved (return={stats['rollout/mean_return']:.2f})")


def test_pac_target_network_and_burn_in():
    """v4's PAC target network θ' + force-wait burn-in (identical to v5). ppo_update
    runs finite on the FiLM model with a target; during burn-in the actor is frozen
    and only the critic trains on forced-wait (full-length) episodes."""
    import copy
    env = ChangeDetectionEnv()
    m = _model()
    assert not any("target" in k for k in m.state_dict()), "target net must NOT be in model state_dict"
    batch, _ = collect_episodes(m, env, n_episodes=6, device=DEVICE)
    target = copy.deepcopy(m)
    for p in target.parameters():
        p.requires_grad_(False)
    res = ppo_update(m, torch.optim.Adam(m.parameters(), lr=1e-3), concat_batches([batch]),
                     PPOConfig(n_epochs=2, per_n_replay=0), target_model=target)
    assert torch.isfinite(torch.tensor(res["loss_total"])) and res["n_updates"] >= 1
    # Burn-in: actor frozen, full-length episodes, critic trains.
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
    print("✓ PAC target network + burn-in: ppo_update finite with θ'; burn-in freezes actor, trains critic")


def test_end_to_end_train_iteration():
    m = _model()
    env = ChangeDetectionEnv()
    cfg = PPOConfig(n_epochs=2, per_n_replay=2, buffer_capacity=16, burn_in_iters=0)
    hist = train(m, env, n_iterations=2, episodes_per_iter=4, cfg=cfg,
                 device=DEVICE, log_every=1, save_every=999)
    assert len(hist) == 2
    assert hist[-1]["per_n_replay_used"] == 2, "replay episodes not used on iter 2"
    print("✓ end-to-end train(): 2 iters incl. PER replay sampling")


if __name__ == "__main__":
    tests = [
        test_patch_embed_shapes,
        test_film_structure,
        test_encoder_attends_over_N,
        test_encoder_recurrence_shapes,
        test_decoder_reads_both_states,
        test_mlp_heads,
        test_critic_action_as_input_encoding,
        test_init_action_bias,
        test_rl_step_and_sequence,
        test_grad_flows_to_encoder_and_patch_embed,
        test_ppo_update_changes_params_and_is_finite,
        test_pac_target_network_and_burn_in,
        test_end_to_end_train_iteration,
    ]
    for t in tests:
        t()
    print(f"\nAll {len(tests)} v4 smoke tests passed.")
