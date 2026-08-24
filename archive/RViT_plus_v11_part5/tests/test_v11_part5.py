"""
Smoke tests for RViT+ v11_part5 — v11_part2's CROSS-TALK split-readout dual-stream
architecture (Tμ salience reads [H1‖H2]→actor; TQ top-down reads H2→critic; H2 shared
between the streams) on the v7 DISTRACTOR environment (cued-SIDE task; the uncued side
may change — a distractor to IGNORE; pressing on it = false alarm).

Run:  .venv/bin/python -m RViT_plus_v11_part5.tests.test_v11_part5
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

from RViT_plus_v11_part5.env import ChangeDetectionEnv, SIDE_QUADRANTS
from RViT_plus_v11_part5.tx_lstm_encoder import DualStreamEncoder
from RViT_plus_v11_part5.model import RViTPlusV11Part5Model
from RViT_plus_v11_part5.ppo import (
    PPOConfig, collect_episodes, concat_batches, ppo_update, train,
)

DEVICE = torch.device("cpu")
torch.manual_seed(0)


def _model(**over):
    kw = dict(patch_size=5, d_model=64, d_mem=64, tx_heads=1, tx_layers=1, n_lstm=2,
              conv_channels=32, n_conv_layers=3, conv_kernel=5, n_actions=2, n_quantiles=8,
              init_action_bias=[0.0, -1.5], seq_len=29)
    kw.update(over)
    return RViTPlusV11Part5Model(**kw).to(DEVICE)


# ── DISTRACTOR ENVIRONMENT (the v11_part5 change vs v11_part2) ─────────────────
def test_distractor_env():
    env = ChangeDetectionEnv()
    assert env.distractor_prob == 0.5, "default distractor_prob should be 0.5"
    assert env.action_space.n == 2 and env.T == 29
    for _ in range(40):
        env.reset()
        side = SIDE_QUADRANTS[env.cue_position]
        cued = {side["primary"], side["secondary"]}
        uncued = set(side["distractor"])
        if env.change_true == 1:
            assert env.change_index in cued, "target must be on the cued side"
        if env.distractor_true == 1:
            assert env.distractor_index in uncued, "distractor must be on the UNCUED side"
    env.reset()
    _obs, reward, done, _info = env.step(1)   # press at t=0 < change_time
    assert reward == 0 and done, "a press before the target change must give 0 and end (false-alarm branch)"
    env0 = ChangeDetectionEnv(distractor_prob=0.0)
    for _ in range(20):
        env0.reset()
        assert env0.distractor_true == 0, "distractor_prob=0 must disable distractors"
    print("✓ distractor env: target on cued side, distractor on uncued side, early-press=false-alarm, p=0 disables")


# ── ARCHITECTURE = v11_part2 (CROSS-TALK split readout) ───────────────────────
def test_patch_embed_shapes():
    m = _model()
    tok = m.patch_embed(torch.randn(3, 3, 50, 50))
    assert tok.shape == (3, 100, 64) and m.n_tokens == 100
    print("✓ patch_embed: (3,3,50,50) → (3,100,64); n_tokens=100")


def test_structure_single_head_and_tags():
    m = _model(tx_heads=1)
    enc = m.encoder
    assert isinstance(enc, DualStreamEncoder)
    assert enc.sal_block.attn.num_heads == 1 and enc.td_block.attn.num_heads == 1, "single head per stream"
    assert enc.sal_tag.shape == (2, 1, 64), "salience K/V needs 2 source tags (H1, H2) — cross-talk reads both"
    assert enc.stream_dim == 64 and len(enc.cells) == 2
    print("✓ structure: cross-talk dual-stream — single head, salience source-tags (2,1,64) for [H1‖H2]")


def test_crosstalk_routing():
    """v11_part2 wiring: Tμ reads [H1‖H2] (2N keys) so changing H1 OR H2 moves salience;
    TQ reads H2 (N keys) so only H2 moves top-down. H2 is SHARED → cross-talk."""
    m = _model().eval()
    states = m.init_states(2, device=DEVICE)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    with torch.no_grad():
        (Hs, Cs), rec, attn = m.encoder.forward_step(tok, states, return_attn=True)
        assert attn[0].shape == (2, 1, 100, 200), f"salience attn {tuple(attn[0].shape)}, expected (2,1,100,200) over [H1‖H2]"
        assert attn[1].shape == (2, 1, 100, 100), f"top-down attn {tuple(attn[1].shape)}, expected (2,1,100,100) over H2"
        st_h1 = ([torch.randn(2, 100, 64), states[0][1]], [states[1][0], states[1][1]])
        _s, _r, attn_h1 = m.encoder.forward_step(tok, st_h1, return_attn=True)
        assert not torch.allclose(attn[0], attn_h1[0]) and torch.allclose(attn[1], attn_h1[1]), "H1→salience only"
        st_h2 = ([states[0][0], torch.randn(2, 100, 64)], [states[1][0], states[1][1]])
        _s, _r, attn_h2 = m.encoder.forward_step(tok, st_h2, return_attn=True)
        assert not torch.allclose(attn[0], attn_h2[0]) and not torch.allclose(attn[1], attn_h2[1]), \
            "H2 (SHARED) must move BOTH streams — that is the cross-talk"
    print("✓ cross-talk routing: Tμ reads [H1‖H2], TQ reads H2; H2 shared moves both streams")


def test_salience_grounded_topdown_gating_only():
    m = _model().eval()
    enc_cut = copy.deepcopy(m.encoder).eval()
    with torch.no_grad():
        for blk in (enc_cut.sal_block, enc_cut.td_block):
            blk.attn.out_proj.weight.zero_(); blk.attn.out_proj.bias.zero_()
    tok_a = m.patch_embed(torch.randn(2, 3, 50, 50))
    tok_b = m.patch_embed(torch.randn(2, 3, 50, 50) * 3.0 + 1.0)
    with torch.no_grad():
        st0 = enc_cut.init_states(2)
        (_h, _c), rec_a = enc_cut.forward_step(tok_a, st0)
        (_h2, _c2), rec_b = enc_cut.forward_step(tok_b, st0)
        assert not torch.allclose(rec_a[0], rec_b[0]), "salience Z_sal image-invariant with attention off"
        assert torch.allclose(rec_a[1], rec_b[1], atol=1e-6), "top-down Z_td changed with image despite silenced attention"
    print("✓ salience image-grounded (residual=X); top-down gating-only (residual=H2)")


def test_split_readout():
    m = _model().eval()
    B = 4
    zs, zt = torch.randn(B, 100, 64), torch.randn(B, 100, 64)
    with torch.no_grad():
        al, q, _, _ = m._run_heads([zs, zt])
        al2, q2, _, _ = m._run_heads([torch.randn(B, 100, 64), zt])
        assert not torch.allclose(al, al2) and torch.allclose(q, q2), "actor must read Z_sal only"
        al3, q3, _, _ = m._run_heads([zs, torch.randn(B, 100, 64)])
        assert torch.allclose(al, al3) and not torch.allclose(q, q3), "critic must read Z_td only"
    print("✓ split readout: actor←Z_sal (Tμ), critic←Z_td (TQ)")


def test_memory_update_sources():
    m = _model().eval()
    B = 3
    tok = m.patch_embed(torch.randn(B, 3, 50, 50))
    states = m.init_states(B, device=DEVICE)
    with torch.no_grad():
        (Hs, Cs), _rec = m.encoder.forward_step(tok, states)
        st_h2 = ([states[0][0], torch.randn(B, 100, 64)], [states[1][0], torch.randn(B, 100, 64)])
        (Hs2, _), _ = m.encoder.forward_step(tok, st_h2)
        assert torch.allclose(Hs[0], Hs2[0], atol=1e-6), "new H1 depends on H2_prev — it must not (H1=LSTM1(X))"
        assert not torch.allclose(Hs[1], Hs2[1]), "new H2 should depend on H2_prev"
    print("✓ memory writes: H1←X (H2-independent), H2←Z_sal")


def test_conv_heads_single_stream():
    import torch.nn as nn
    m = _model(n_conv_layers=3, conv_channels=32)
    for name, dec in (("actor", m.actor_head), ("critic", m.critic_head)):
        convs = [mod for mod in dec.trunk if isinstance(mod, nn.Conv1d)]
        assert len(convs) == 3 and convs[0].in_channels == 64, f"{name}: single-stream in_ch=64"
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
    out = m.forward_rl_sequence(torch.randn(3, 29, 3, 50, 50))
    assert out["actor_logits_seq"].shape == (3, 29, 2) and out["q_dist_seq"].shape == (3, 29, 2, 8)
    print("✓ rl_step + forward_rl_sequence: shapes correct")


def test_grad_flows_through_stack():
    m = _model()
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    out = m.forward_rl_sequence(batch.observations)
    loss = out["actor_logits_seq"].pow(2).mean() + out["q_dist_seq"].pow(2).mean()
    m.zero_grad(); loss.backward()
    assert m.patch_embed.proj[0].weight.grad.abs().sum() > 0
    assert m.encoder.sal_block.attn.in_proj_weight.grad.abs().sum() > 0, "no grad to salience attention"
    assert m.encoder.td_block.attn.in_proj_weight.grad.abs().sum() > 0, "no grad to top-down attention"
    assert m.encoder.sal_tag.grad is not None and m.encoder.sal_tag.grad.abs().sum() > 0, "no grad to salience tags"
    for cell in (m.encoder.cell1, m.encoder.cell2):
        assert cell.weight_ih.grad is not None and cell.weight_ih.grad.abs().sum() > 0
    assert m.actor_head.trunk[0].weight.grad.abs().sum() > 0 and m.critic_head.trunk[0].weight.grad.abs().sum() > 0
    print("✓ gradient reaches patch_embed + both streams + sal_tag + both LSTMs + both heads (distractor env)")


def test_ppo_update_changes_params_and_is_finite():
    m = _model()
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    before = [p.detach().clone() for p in m.parameters()]
    res = ppo_update(m, torch.optim.Adam(m.parameters(), lr=1e-3), concat_batches([batch]),
                     PPOConfig(n_epochs=2, per_n_replay=0))
    for k in ("loss_policy", "loss_value", "loss_entropy", "loss_total"):
        assert torch.isfinite(torch.tensor(res[k])), f"{k} not finite: {res[k]}"
    assert sum(not torch.allclose(a, b.detach()) for a, b in zip(before, m.parameters())) > 0
    print("✓ ppo_update on distractor env: finite losses, params move")


def test_pac_target_network_and_burn_in():
    env = ChangeDetectionEnv()
    m2 = _model()
    actor_before = {k: v.clone() for k, v in m2.actor_head.state_dict().items()}
    critic_before = {k: v.clone() for k, v in m2.critic_head.state_dict().items()}
    hist = train(m2, env, n_iterations=2, episodes_per_iter=4,
                 cfg=PPOConfig(n_epochs=2, per_n_replay=0, burn_in_iters=2, target_update_period=0),
                 device=DEVICE, log_every=1, save_every=999)
    assert all(h["rollout/mean_length"] == 29.0 for h in hist), "forced-wait episodes must run full length"
    assert all(torch.allclose(actor_before[k], m2.actor_head.state_dict()[k]) for k in actor_before), "actor frozen in burn-in"
    assert any(not torch.allclose(critic_before[k], m2.critic_head.state_dict()[k]) for k in critic_before), "critic moves in burn-in"
    print("✓ PAC target network + burn-in on distractor env")


def test_end_to_end_train_iteration():
    m = _model()
    env = ChangeDetectionEnv()
    cfg = PPOConfig(n_epochs=2, per_n_replay=2, buffer_capacity=16, burn_in_iters=0)
    hist = train(m, env, n_iterations=2, episodes_per_iter=4, cfg=cfg,
                 device=DEVICE, log_every=1, save_every=999)
    assert len(hist) == 2 and hist[-1]["per_n_replay_used"] == 2
    print("✓ end-to-end train() on distractor env: 2 iters incl. PER replay")


if __name__ == "__main__":
    tests = [
        test_distractor_env,
        test_patch_embed_shapes,
        test_structure_single_head_and_tags,
        test_crosstalk_routing,
        test_salience_grounded_topdown_gating_only,
        test_split_readout,
        test_memory_update_sources,
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
    print(f"\nAll {len(tests)} v11_part5 smoke tests passed (v11_part2 cross-talk arch on the v7 distractor env).")
