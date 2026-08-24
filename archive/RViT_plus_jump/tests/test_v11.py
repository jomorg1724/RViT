"""
Smoke tests for RViT+ v11 — PARALLEL DUAL-STREAM attention.

  SALIENCE (bottom-up):  Q=X, K=V=H1, residual=X  → grounded image stream.
  TOP-DOWN (gating-only): Q=X, K=V=H2, residual=H2 → image can only RE-GATE H2.
  H1=LSTM1(X), H2=LSTM2(Z_sal); the heads read [Z_sal ++ Z_td] (transformer outputs).

Run:  .venv/bin/python -m RViT_plus_jump.tests.test_v11
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

from RViT_plus_jump.env import ChangeDetectionEnv
from RViT_plus_jump.tx_lstm_encoder import DualStreamEncoder
from RViT_plus_jump.model import RViTPlusJumpModel
from RViT_plus_jump.ppo import (
    PPOConfig, collect_episodes, concat_batches, ppo_update, train,
)

DEVICE = torch.device("cpu")
torch.manual_seed(0)


def _model(**over):
    kw = dict(patch_size=5, d_model=64, d_mem=64, tx_heads=4, tx_layers=1, n_lstm=2,
              conv_channels=32, n_conv_layers=3, conv_kernel=5, n_actions=2, n_quantiles=8,
              init_action_bias=[0.0, -1.5], seq_len=29)
    kw.update(over)
    return RViTPlusJumpModel(**kw).to(DEVICE)


def test_patch_embed_shapes():
    m = _model()
    x = torch.randn(3, 3, 50, 50)
    tok = m.patch_embed(x)
    assert tok.shape == (3, 100, 64), tok.shape
    assert m.n_tokens == 100
    print("✓ patch_embed: (3,3,50,50) → (3,100,64); n_tokens=100 (10×10 grid)")


def test_dual_stream_structure():
    """Encoder = two parallel cross-attention blocks (salience + top-down) + two
    per-token LSTMCells + a shared memory positional embedding. The readout width
    (stream_dim) is 2·d_model = the concatenated [Z_sal ++ Z_td]."""
    m = _model(tx_heads=4, n_lstm=2)
    enc = m.encoder
    assert isinstance(enc, DualStreamEncoder)
    assert enc.sal_block.attn.num_heads == 4 and enc.td_block.attn.num_heads == 4, "tx_heads not wired"
    assert enc.mem_pos_emb.shape == (1, 100, 64), "shared memory positional embedding"
    assert enc.stream_dim == 128, "stream_dim must be 2*d_model (Z_sal ++ Z_td)"
    assert len(enc.cells) == 2, "two LSTMs (H1, H2)"
    assert enc.cell1.input_size == 64 and enc.cell1.hidden_size == 64, "LSTM1 ingests X (d_model)"
    assert enc.cell2.input_size == 64, "LSTM2 ingests Z_sal (d_model)"
    assert len(enc.H0) == 2 and enc.H0[0].shape == (1, 100, 64), "per-token learned initial state"
    # n_lstm != 2 must be rejected
    try:
        DualStreamEncoder(n_tokens=100, d_model=64, d_mem=64, n_heads=4, n_lstm=3)
        raise AssertionError("n_lstm=3 should have raised")
    except ValueError:
        pass
    print("✓ structure: salience + top-down blocks (4 heads each), 2 LSTMs, stream_dim=128")


def test_two_streams_shapes_and_routing():
    """forward_step returns rec=[Z_sal, Z_td] (each B,N,d) and attn=[aw_sal, aw_td]
    (each B,heads,N,N). Both streams query with X; salience reads H1, top-down reads
    H2 — so changing H1 moves ONLY the salience weights, changing H2 moves ONLY the
    top-down weights, and changing the image moves BOTH."""
    m = _model().eval()
    states = m.init_states(2, device=DEVICE)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    with torch.no_grad():
        (Hs, Cs), rec, attn = m.encoder.forward_step(tok, states, return_attn=True)
        assert len(rec) == 2 and rec[0].shape == (2, 100, 64) and rec[1].shape == (2, 100, 64), \
            "rec must be [Z_sal, Z_td], each (B,N,d)"
        assert len(attn) == 2, "two streams → two attention maps"
        assert attn[0].shape == (2, 4, 100, 100) and attn[1].shape == (2, 4, 100, 100), \
            f"attention shapes {tuple(attn[0].shape)},{tuple(attn[1].shape)}; expected (2,4,100,100) each"
        # change H1 only → salience weights move, top-down weights do NOT
        st_h1 = ([torch.randn(2, 100, 64), states[0][1]], [states[1][0], states[1][1]])
        _s, _r, attn_h1 = m.encoder.forward_step(tok, st_h1, return_attn=True)
        assert not torch.allclose(attn[0], attn_h1[0]), "H1 change did not move salience weights"
        assert torch.allclose(attn[1], attn_h1[1]), "H1 change leaked into top-down weights (reads H2 only)"
        # change H2 only → top-down weights move, salience weights do NOT
        st_h2 = ([states[0][0], torch.randn(2, 100, 64)], [states[1][0], states[1][1]])
        _s, _r, attn_h2 = m.encoder.forward_step(tok, st_h2, return_attn=True)
        assert not torch.allclose(attn[1], attn_h2[1]), "H2 change did not move top-down weights"
        assert torch.allclose(attn[0], attn_h2[0]), "H2 change leaked into salience weights (reads H1 only)"
        # change image → BOTH stream weights move (both query with X)
        tok_b = m.patch_embed(torch.randn(2, 3, 50, 50))
        _s, _r, attn_b = m.encoder.forward_step(tok_b, states, return_attn=True)
        assert not torch.allclose(attn[0], attn_b[0]) and not torch.allclose(attn[1], attn_b[1]), \
            "image change must move BOTH stream weights (X is the query for both)"
    print("✓ routing: salience reads H1, top-down reads H2, both queried by X; weights (B,4,100,100)")


def test_salience_grounded_topdown_gating_only():
    """The decisive structural proof. Silence each stream's attention (out_proj=0):
      • SALIENCE keeps image content (residual=X) → Z_sal still tracks the image.
      • TOP-DOWN has NO image content (residual=H2) → Z_td is image-BLIND without
        attention; the image's only route into Z_td is the gating it performs."""
    m = _model().eval()
    enc_cut = copy.deepcopy(m.encoder).eval()
    with torch.no_grad():
        for blk in (enc_cut.sal_block, enc_cut.td_block):
            blk.attn.out_proj.weight.zero_()
            blk.attn.out_proj.bias.zero_()
    tok_a = m.patch_embed(torch.randn(2, 3, 50, 50))
    tok_b = m.patch_embed(torch.randn(2, 3, 50, 50) * 3.0 + 1.0)
    with torch.no_grad():
        st0 = enc_cut.init_states(2)
        (_h, _c), rec_a = enc_cut.forward_step(tok_a, st0)
        (_h2, _c2), rec_b = enc_cut.forward_step(tok_b, st0)
        # salience (rec[0]): grounded — different images give different Z_sal even with attention off
        assert not torch.allclose(rec_a[0], rec_b[0]), \
            "salience Z_sal image-invariant with attention off — residual=X bypass missing"
        # top-down (rec[1]): image-blind — same memory ⇒ identical Z_td regardless of the image
        assert torch.allclose(rec_a[1], rec_b[1], atol=1e-6), \
            "top-down Z_td changed with the image despite silenced attention — residual is leaking X"
        # with attention INTACT, the image DOES move the top-down output (gating transmits)
        (_h3, _c3), rec_c = m.encoder.forward_step(tok_a, m.init_states(2))
        (_h4, _c4), rec_d = m.encoder.forward_step(tok_b, m.init_states(2))
        assert not torch.allclose(rec_c[1], rec_d[1]), "intact attention should let the image gate top-down"
    print("✓ salience stays image-grounded; top-down is gating-only (image-blind without attention)")


def test_memory_update_sources():
    """H1 is written from the raw image X (independent of H2); H2 is written from the
    salience output Z_sal (so it depends on X and H1)."""
    m = _model().eval()
    B = 3
    tok = m.patch_embed(torch.randn(B, 3, 50, 50))
    states = m.init_states(B, device=DEVICE)
    with torch.no_grad():
        (Hs, Cs), _rec = m.encoder.forward_step(tok, states)
        # changing ONLY H2_prev must not change the new H1 (H1 = LSTM1(X, H1_prev))
        st_h2 = ([states[0][0], torch.randn(B, 100, 64)], [states[1][0], torch.randn(B, 100, 64)])
        (Hs2, _), _ = m.encoder.forward_step(tok, st_h2)
        assert torch.allclose(Hs[0], Hs2[0], atol=1e-6), "new H1 depends on H2_prev — it must not"
        assert not torch.allclose(Hs[1], Hs2[1]), "new H2 should depend on H2_prev"
        # changing the image changes BOTH new memories (H1←X directly, H2←Z_sal←X)
        tok_b = m.patch_embed(torch.randn(B, 3, 50, 50))
        (Hsb, _), _ = m.encoder.forward_step(tok_b, states)
        assert not torch.allclose(Hs[0], Hsb[0]), "new H1 unchanged by the image — must be written from X"
        assert not torch.allclose(Hs[1], Hsb[1]), "new H2 unchanged by the image — Z_sal feeds it"
    print("✓ memory writes: H1←X (H2-independent), H2←Z_sal (image- and H1-dependent)")


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
    assert len(rec) == 2, "two transformer-output streams"
    for Z in rec:
        assert Z.shape == (B, 100, 64)
    assert not torch.allclose(new_states[0][0], states[0][0]), "H1 did not update"
    assert not torch.allclose(new_states[0][1], states[0][1]), "H2 did not update"
    print("✓ recurrence: 2 carried memories (B,100,64); both update; rec = 2 stream outputs")


def test_decoders_read_both_streams():
    """Heads run a Conv1d-over-tokens trunk on [Z_sal ++ Z_td]. Output must depend
    on BOTH streams and be token-permutation SENSITIVE (spatial layout preserved)."""
    m = _model().eval()
    B = 4
    Zsal, Ztd = torch.randn(B, 100, 64), torch.randn(B, 100, 64)
    with torch.no_grad():
        logits = m.actor_head([Zsal, Ztd])
        q = m.critic_head([Zsal, Ztd])
        assert logits.shape == (B, 2), logits.shape
        assert q.shape == (B, 2, 8), q.shape
        V_dist, V_scalar = m.critic_head.derive_V(q, logits)
        assert V_dist.shape == (B, 8) and V_scalar.shape == (B,)
        # depends on BOTH streams
        assert not torch.allclose(logits, m.actor_head([torch.randn(B, 100, 64), Ztd])), \
            "actor ignores the salience stream"
        assert not torch.allclose(logits, m.actor_head([Zsal, torch.randn(B, 100, 64)])), \
            "actor ignores the top-down stream"
        # conv over tokens is permutation SENSITIVE (permute both streams in lockstep)
        perm = torch.randperm(100)
        assert not torch.allclose(logits, m.actor_head([Zsal[:, perm], Ztd[:, perm]]), atol=1e-5), \
            "conv output permutation-invariant — spatial layout not used"
    print("✓ heads conv over [Z_sal++Z_td] token axis: both-stream-sensitive, permutation-SENSITIVE")


def test_conv_heads():
    import torch.nn as nn
    m = _model(n_conv_layers=3, conv_channels=32)
    for name, dec in (("actor", m.actor_head), ("critic", m.critic_head)):
        n_conv = sum(isinstance(mod, nn.Conv1d) for mod in dec.trunk)
        assert n_conv == 3, f"{name} trunk has {n_conv} Conv1d layers; expected 3"
    convs = [mod for mod in m.actor_head.trunk if isinstance(mod, nn.Conv1d)]
    assert convs[0].in_channels == 128, "first conv must ingest 2*d_model=128 (Z_sal ++ Z_td)"
    assert convs[0].out_channels == 32 and convs[0].stride == (2,), "conv_channels / stride-2"
    assert m.actor_head.out.out_features == 2, "actor final Linear → n_actions"
    assert m.critic_head.out.out_features == 2 * 8, "critic final Linear → n_actions*n_quantiles"
    print("✓ conv heads: 3 stride-2 Conv1d (2*d_model→conv_channels) → flatten → Linear")


def test_init_action_bias():
    m = _model(init_action_bias=[0.0, -1.5])
    Zsal = torch.zeros(8, 100, 64)
    Ztd = torch.zeros(8, 100, 64)
    logits = m.actor_head([Zsal, Ztd])
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
    """Reward-driven gradient must reach the patch MLP, BOTH attention streams, BOTH
    LSTMCells, and BOTH conv heads — the whole conv-free stack trains by RL."""
    m = _model()
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    out = m.forward_rl_sequence(batch.observations)
    loss = out["actor_logits_seq"].pow(2).mean() + out["q_dist_seq"].pow(2).mean()
    m.zero_grad(); loss.backward()
    assert m.patch_embed.proj[0].weight.grad.abs().sum() > 0, "no grad to patch embed MLP"
    assert m.encoder.sal_block.attn.in_proj_weight.grad.abs().sum() > 0, "no grad to salience attention"
    assert m.encoder.td_block.attn.in_proj_weight.grad.abs().sum() > 0, "no grad to top-down attention"
    for li, cell in enumerate(m.encoder.cells):
        assert cell.weight_ih.grad is not None and cell.weight_ih.grad.abs().sum() > 0, f"no grad to LSTM{li+1}"
    assert m.actor_head.trunk[0].weight.grad.abs().sum() > 0, "no grad to actor conv trunk"
    assert m.critic_head.trunk[0].weight.grad.abs().sum() > 0, "no grad to critic conv trunk"
    print("✓ gradient reaches patch_embed + BOTH attention streams + both LSTMs + both conv heads")


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
    """PAC target network θ' + force-wait burn-in (identical trainer to v8/v9)."""
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
        test_dual_stream_structure,
        test_two_streams_shapes_and_routing,
        test_salience_grounded_topdown_gating_only,
        test_memory_update_sources,
        test_lstm_recurrence_shapes,
        test_decoders_read_both_streams,
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
    print(f"\nAll {len(tests)} v11 smoke tests passed "
          f"(incl. salience-grounded + top-down-gating-only proofs).")
