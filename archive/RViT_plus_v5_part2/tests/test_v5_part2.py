"""
Smoke tests for RViT+ v5_part2: shapes through the conv-free patch + SINGLE
transformer encoder + STACKED per-token LSTMs + tiny 3-layer FF actor/critic
heads, plus one end-to-end PAC/QR-DQN update and a full training iteration.

Run:  .venv/bin/python -m RViT_plus_v5_part2.tests.test_v5_part2
"""
from __future__ import annotations

import os
import sys

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v5_part2.env import ChangeDetectionEnv
from RViT_plus_v5_part2.tx_lstm_encoder import TxLSTMEncoder
from RViT_plus_v5_part2.model import RViTPlusV5Part2Model
from RViT_plus_v5_part2.ppo import (
    PPOConfig, collect_episodes, concat_batches, ppo_update, train,
)

DEVICE = torch.device("cpu")
torch.manual_seed(0)


def _model(**over):
    kw = dict(patch_size=5, d_model=64, d_mem=64, tx_heads=4, tx_layers=1, n_lstm=2,
              conv_channels=32, n_conv_layers=3, conv_kernel=5, n_actions=2, n_quantiles=8,
              init_action_bias=[0.0, -1.5], seq_len=29)
    kw.update(over)
    return RViTPlusV5Part2Model(**kw).to(DEVICE)


def test_patch_embed_shapes():
    m = _model()
    x = torch.randn(3, 3, 50, 50)
    tok = m.patch_embed(x)
    assert tok.shape == (3, 100, 64), tok.shape
    assert m.n_tokens == 100
    print("✓ patch_embed: (3,3,50,50) → (3,100,64); n_tokens=100 (10×10 grid)")


def test_tx_lstm_structure():
    """Encoder = tx_layers cross-attention block(s) (tx_heads heads) + n_lstm
    stacked LSTMCells, with memory source tags + a memory positional embedding.
    cell0 ingests d_model, later cells ingest d_mem."""
    m = _model(tx_heads=4, tx_layers=1, n_lstm=2)
    enc = m.encoder
    assert isinstance(enc, TxLSTMEncoder)
    assert len(enc.blocks) == 1, "single cross-attention block"
    assert enc.blocks[0].attn.num_heads == 4, "tx_heads not wired"
    assert enc.mem_tag.shape == (2, 1, 64), "one source tag per memory state"
    assert enc.mem_pos_emb.shape == (1, 100, 64), "shared memory positional embedding"
    assert len(enc.cells) == 2, "two stacked LSTMs"
    assert enc.cells[0].input_size == 64 and enc.cells[0].hidden_size == 64, "LSTM1 ingests d_model"
    assert enc.cells[1].input_size == 64, "LSTM2 ingests the previous LSTM's d_mem hidden"
    assert len(enc.H0) == 2 and enc.H0[0].shape == (1, 100, 64), "per-token learned initial state"
    print("✓ structure: 1 cross-attn block (4 heads) + mem tags/pos-emb → 2 stacked per-token LSTMCells")


def test_encoder_cross_attends_over_memory():
    """Cross-attention: N patch QUERIES attend over [X ++ H1 ++ H2] = (1+n_lstm)·N
    keys (memory-as-tokens). Weights are (B, heads, N, 3N), and carried memory
    actually changes the output."""
    m = _model().eval()
    states = m.init_states(2, device=DEVICE)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    with torch.no_grad():
        (_Hs, _Cs), _rec, attn = m.encoder.forward_step(tok, states, return_attn=True)
        assert len(attn) == 1, "single cross-attention block → one attention map"
        assert attn[0].shape == (2, 4, 100, 300), \
            f"attention shape {tuple(attn[0].shape)}, expected (2,4,100,300) = (B,heads,N,3N)"
        # carried memory feeds the attention: random memory → different Z than zero-init
        rand = ([torch.randn(2, 100, 64), torch.randn(2, 100, 64)],
                [torch.zeros(2, 100, 64), torch.zeros(2, 100, 64)])
        (_a, _b), rec_rand = m.encoder.forward_step(tok, rand)
        (_c, _d), rec_zero = m.encoder.forward_step(tok, m.init_states(2))
        assert not torch.allclose(rec_rand[0], rec_zero[0]), "carried memory does not affect the output"
    print("✓ cross-attention: N=100 queries over 3N=300 keys (X++H1++H2); memory-as-tokens active")


def test_lstm_recurrence_shapes():
    m = _model()
    B = 4
    states = m.init_states(B, device=DEVICE)
    Hs, Cs = states
    assert len(Hs) == 2 and len(Cs) == 2
    for H in Hs:
        assert H.shape == (B, 100, 64), H.shape
    tok = m.patch_embed(torch.randn(B, 3, 50, 50))
    new_states, rec = m.encoder.forward_step(tok, states)
    assert len(rec) == 2, "2 stacked LSTMs → 2 recurrent states"
    for H in rec:
        assert H.shape == (B, 100, 64)
    assert not torch.allclose(new_states[0][0], states[0][0]), "LSTM1 hidden did not update"
    assert not torch.allclose(new_states[0][1], states[0][1]), "LSTM2 hidden did not update"
    print("✓ stacked LSTMs: 2 per-token memories, each (B,100,64); both update per step")


def test_decoders_conv_over_H2():
    """Both heads run a Conv1d-over-tokens trunk on the TOP state H2 (rec[-1]).
    H1 must NOT affect the output; H2 must; and unlike pooling the conv is
    token-permutation SENSITIVE (it preserves the spatial layout)."""
    m = _model().eval()                          # eval → dropout off, deterministic
    B = 4
    H1, H2 = torch.randn(B, 100, 64), torch.randn(B, 100, 64)
    with torch.no_grad():
        logits = m.actor_head([H1, H2])
        q = m.critic_head([H1, H2])
        assert logits.shape == (B, 2), logits.shape
        assert q.shape == (B, 2, 8), q.shape
        V_dist, V_scalar = m.critic_head.derive_V(q, logits)
        assert V_dist.shape == (B, 8) and V_scalar.shape == (B,)
        # changing H1 leaves output unchanged (heads read only the top state H2)
        l_h1 = m.actor_head([torch.randn(B, 100, 64), H2])
        assert torch.allclose(logits, l_h1, atol=1e-6), "actor output depends on H1 — should read only H2"
        # changing H2 changes output
        l_h2 = m.actor_head([H1, torch.randn(B, 100, 64)])
        assert not torch.allclose(logits, l_h2), "actor output unchanged when H2 changes"
        # conv over the token axis is NOT permutation-invariant (it uses spatial layout)
        perm = torch.randperm(100)
        l_perm = m.actor_head([H1, H2[:, perm]])
        assert not torch.allclose(logits, l_perm, atol=1e-5), \
            "conv output permutation-invariant — spatial layout not being used"
    print("✓ heads conv over H2's token axis: H1-invariant, H2-sensitive, token-permutation-SENSITIVE")


def test_conv_heads():
    import torch.nn as nn
    m = _model(n_conv_layers=3, conv_channels=32)
    for name, dec in (("actor", m.actor_head), ("critic", m.critic_head)):
        n_conv = sum(isinstance(mod, nn.Conv1d) for mod in dec.trunk)
        assert n_conv == 3, f"{name} trunk has {n_conv} Conv1d layers; expected 3"
    convs = [mod for mod in m.actor_head.trunk if isinstance(mod, nn.Conv1d)]
    assert convs[0].in_channels == 64, "first conv ingests d_mem=64 channels"
    assert convs[0].out_channels == 32 and convs[0].stride == (2,), "conv_channels / stride-2"
    assert m.actor_head.out.out_features == 2, "actor final Linear → n_actions"
    assert m.critic_head.out.out_features == 2 * 8, "critic final Linear → n_actions*n_quantiles"
    print("✓ conv heads: actor & critic each = 3 stride-2 Conv1d (d_mem→conv_channels) → flatten → Linear")


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


def test_grad_flows_through_stack():
    """Reward-driven gradient must reach the patch MLP, the transformer self-attn,
    BOTH LSTMCells, and the FF heads — the whole conv-free stack trains by RL."""
    m = _model()
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    out = m.forward_rl_sequence(batch.observations)
    loss = out["actor_logits_seq"].pow(2).mean() + out["q_dist_seq"].pow(2).mean()
    m.zero_grad(); loss.backward()
    assert m.patch_embed.proj[0].weight.grad.abs().sum() > 0, "no grad to patch embed MLP"
    assert m.encoder.blocks[0].attn.in_proj_weight.grad.abs().sum() > 0, "no grad to cross-attention"
    for li, cell in enumerate(m.encoder.cells):
        assert cell.weight_ih.grad is not None and cell.weight_ih.grad.abs().sum() > 0, f"no grad to LSTM{li+1}"
    assert m.actor_head.trunk[0].weight.grad.abs().sum() > 0, "no grad to actor conv trunk"
    assert m.critic_head.trunk[0].weight.grad.abs().sum() > 0, "no grad to critic conv trunk"
    print("✓ gradient reaches patch_embed + transformer attn + both LSTMs + both conv heads")


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
    print(f"✓ ppo_update: finite losses, {int(res['n_updates'])} steps, {changed} param tensors moved")


def test_pac_target_network_and_burn_in():
    """PAC target network θ' + force-wait burn-in (identical trainer to v5)."""
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
    print("✓ PAC target network + burn-in: finite with θ'; burn-in freezes actor, trains critic")


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
        test_tx_lstm_structure,
        test_encoder_cross_attends_over_memory,
        test_lstm_recurrence_shapes,
        test_decoders_conv_over_H2,
        test_conv_heads,
        test_init_action_bias,
        test_rl_step_and_sequence,
        test_grad_flows_through_stack,
        test_ppo_update_changes_params_and_is_finite,
        test_pac_target_network_and_burn_in,
        test_end_to_end_train_iteration,
    ]
    for t in tests:
        t()
    print(f"\nAll {len(tests)} v5_part2 smoke tests passed.")
