"""
Smoke tests for RViT+ v12 — codebook attention with a STATIC LEARNABLE codebook
(nn.Parameter table; only recurrent state = keys H2). Default mode is SOFT attention
(no sampling); vq_mode='sample'/'argmax' give the hard straight-through variants.
  Q=W_q·X, K=W_k·H2, V=codebook; Z = W_o·(weights @ codebook) + FFN (no X-residual);
  H2←LSTM(X+Z); actor AND critic read Z.

Run:  .venv/bin/python -m RViT_plus_v12.tests.test_v12
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

from RViT_plus_v12.env import ChangeDetectionEnv
from RViT_plus_v12.tx_lstm_encoder import VQAttnEncoder
from RViT_plus_v12.model import RViTPlusV12Model
from RViT_plus_v12.ppo import (
    PPOConfig, collect_episodes, concat_batches, ppo_update, train,
)

DEVICE = torch.device("cpu")
torch.manual_seed(0)


def _model(**over):
    kw = dict(patch_size=5, d_model=64, d_mem=64, tx_heads=1, tx_layers=1, n_lstm=1,
              conv_channels=32, n_conv_layers=3, conv_kernel=5, n_actions=2, n_quantiles=8,
              init_action_bias=[0.0, -1.5], seq_len=29, vq_mode="soft", vq_temperature=1.0)
    kw.update(over)
    return RViTPlusV12Model(**kw).to(DEVICE)


def _state(B, N=100, d=64):
    """The ONLY recurrent state is the key-memory H2 (one entry)."""
    return [torch.randn(B, N, d)], [torch.randn(B, N, d)]


def test_patch_embed_shapes():
    m = _model()
    tok = m.patch_embed(torch.randn(3, 3, 50, 50))
    assert tok.shape == (3, 100, 64) and m.n_tokens == 100
    print("✓ patch_embed: (3,3,50,50) → (3,100,64); n_tokens=100")


def test_structure_static_codebook():
    m = _model(tx_heads=1)
    enc = m.encoder
    assert isinstance(enc, VQAttnEncoder)
    assert enc.vq_mode == "soft", "default mode is SOFT attention (no sampling)"
    assert enc.codebook.shape == (1, 100, 64), "values are a STATIC learnable codebook table (1,N,d)"
    assert isinstance(enc.codebook, torch.nn.Parameter)
    assert not hasattr(enc, "W_v"), "no value projection — values ARE the codebook"
    assert enc.mem_pos_emb.shape == (1, 100, 64)
    assert len(enc.cells) == 1 and enc.cell.input_size == 64, "ONE LSTM (the keys H2)"
    for bad in (dict(n_lstm=2), dict(n_heads=5), dict(vq_mode="gumbel")):
        try:
            VQAttnEncoder(n_tokens=100, d_model=64, d_mem=64, **bad)
            raise AssertionError(f"{bad} should raise")
        except ValueError:
            pass
    print("✓ structure: SOFT default, static codebook (1,N,d), no W_v, ONE LSTM, guards on n_lstm/heads/mode")


def test_soft_weights_not_onehot():
    """In soft mode the attention weights are a smooth distribution (sum to 1, NOT
    one-hot) — the whole codebook is read as a convex combination."""
    m = _model(vq_mode="soft").eval()
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    with torch.no_grad():
        m.encoder.forward_step(tok, _state(2))
        w = m.encoder.last_weights
        assert w.shape == (2, 1, 100, 100)
        assert torch.allclose(w.sum(-1), torch.ones(2, 1, 100), atol=1e-5), "soft weights must sum to 1"
        assert (w.max(-1).values < 0.999).any(), "soft weights collapsed to one-hot — not soft"
        assert m.encoder.last_hard is None, "no hard selection in soft mode"
    print("✓ soft mode: weights are a smooth distribution (sum=1, not one-hot), last_hard=None")


def test_onehot_selection_hard_modes():
    for mode in ("sample", "argmax"):
        m = _model(vq_mode=mode).eval()
        tok = m.patch_embed(torch.randn(2, 3, 50, 50))
        with torch.no_grad():
            m.encoder.forward_step(tok, _state(2))
            hard = m.encoder.last_hard
            assert hard is not None and hard.shape == (2, 1, 100, 100)
            assert torch.allclose(hard.sum(-1), torch.ones(2, 1, 100))
            assert ((hard == 1).sum(-1) == 1).all(), f"{mode}: exactly one slot per (head,query)"
    print("✓ hard modes (sample/argmax): exactly one codebook slot per (head,query)")


def test_routing_q_x_k_h2_v_codebook():
    """Q←X, K←H2, V←codebook. Changing X or H2 moves the soft attention; changing the
    CODEBOOK (values) does NOT move the attention but DOES change the readout Z."""
    m = _model(vq_mode="soft").eval()
    states = _state(2)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    with torch.no_grad():
        (_s, _c), rec, attn = m.encoder.forward_step(tok, states, return_attn=True)
        soft, Z = attn[0], rec[0]
        st_h2 = ([torch.randn(2, 100, 64)], states[1])
        (_s2, _c2), _r2, attn_h2 = m.encoder.forward_step(tok, st_h2, return_attn=True)
        assert not torch.allclose(soft, attn_h2[0]), "H2 (keys) must move the attention"
        tok_b = m.patch_embed(torch.randn(2, 3, 50, 50))
        (_s3, _c3), _r3, attn_x = m.encoder.forward_step(tok_b, states, return_attn=True)
        assert not torch.allclose(soft, attn_x[0]), "X (queries) must move the attention"
        enc2 = copy.deepcopy(m.encoder).eval()
        with torch.no_grad():
            enc2.codebook.copy_(torch.randn_like(enc2.codebook))
        (_s4, _c4), rec_cb, attn_cb = enc2.forward_step(tok, states, return_attn=True)
        assert torch.allclose(soft, attn_cb[0]), "codebook (values) moved the attention — it must not"
        assert not torch.allclose(Z, rec_cb[0]), "codebook (values) must change the readout Z"
    print("✓ routing: Q←X, K←H2, V←static codebook (codebook changes Z not attention; X/H2 move attention)")


def test_x_only_as_queries_and_h2_grounding():
    m = _model(vq_mode="soft").eval()
    enc = copy.deepcopy(m.encoder).eval()
    with torch.no_grad():
        enc.W_q.weight.zero_(); enc.W_q.bias.zero_()
    states = _state(2)
    tok_a = m.patch_embed(torch.randn(2, 3, 50, 50))
    tok_b = m.patch_embed(torch.randn(2, 3, 50, 50) * 3.0 + 1.0)
    with torch.no_grad():
        (Hs_a, _), rec_a = enc.forward_step(tok_a, states)
        (Hs_b, _), rec_b = enc.forward_step(tok_b, states)
        assert torch.allclose(rec_a[0], rec_b[0], atol=1e-6), "X reached Z with queries silenced — content leak"
        assert not torch.allclose(Hs_a[0], Hs_b[0]), "new H2 (←X+Z) must change with the image (X grounds the keys)"
    print("✓ X only as queries + into H2: queries off → Z image-blind, H2 still grounded in X")


def test_Z_to_both_heads_and_rec():
    m = _model(vq_mode="soft").eval()
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


def test_mode_determinism():
    tok = torch.randn(2, 3, 50, 50)
    for mode in ("soft", "argmax"):
        m = _model(vq_mode=mode).eval()
        x = m.patch_embed(tok); st = _state(2)
        with torch.no_grad():
            (_a, _b), r1 = m.encoder.forward_step(x, st)
            (_c, _d), r2 = m.encoder.forward_step(x, st)
            assert torch.allclose(r1[0], r2[0]), f"{mode} must be deterministic"
    ms = _model(vq_mode="sample").eval()
    xs = ms.patch_embed(tok); sts = _state(2)
    idxs = []
    with torch.no_grad():
        for _ in range(12):
            ms.encoder.forward_step(xs, sts)
            idxs.append(ms.encoder.last_hard.argmax(-1).flatten())
    assert any(not torch.equal(idxs[0], idxs[i]) for i in range(1, len(idxs))), "sample mode not sampling"
    print("✓ soft & argmax deterministic; sample stochastic")


def test_soft_gradients():
    """Soft mode is fully differentiable: gradient on Z reaches W_q/W_k (through the
    softmax), W_o, and the static codebook."""
    m = _model(vq_mode="soft")
    (_s, _c), rec = m.encoder.forward_step(m.patch_embed(torch.randn(2, 3, 50, 50)), _state(2))
    m.zero_grad(); rec[0].sum().backward()
    assert m.encoder.W_q.weight.grad.abs().sum() > 0, "no grad to W_q"
    assert m.encoder.W_k.weight.grad.abs().sum() > 0, "no grad to W_k (softmax path)"
    assert m.encoder.W_o.weight.grad.abs().sum() > 0, "no grad to W_o"
    assert m.encoder.codebook.grad is not None and m.encoder.codebook.grad.abs().sum() > 0, "no grad to the codebook"
    print("✓ soft gradients: Z → W_q, W_k (softmax), W_o, and the static codebook")


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
    print("✓ rl_step + forward_rl_sequence: shapes correct (single recurrent state)")


def test_grad_flows_through_stack():
    m = _model()
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    out = m.forward_rl_sequence(batch.observations)
    loss = out["actor_logits_seq"].pow(2).mean() + out["q_dist_seq"].pow(2).mean()
    m.zero_grad(); loss.backward()
    assert m.patch_embed.proj[0].weight.grad.abs().sum() > 0, "no grad to patch embed"
    for nm, p in (("W_q", m.encoder.W_q), ("W_k", m.encoder.W_k), ("W_o", m.encoder.W_o)):
        assert p.weight.grad is not None and p.weight.grad.abs().sum() > 0, f"no grad to {nm}"
    assert m.encoder.cell.weight_ih.grad.abs().sum() > 0, "no grad to the H2 LSTM"
    assert m.encoder.codebook.grad is not None and m.encoder.codebook.grad.abs().sum() > 0, "no grad to the codebook"
    assert m.actor_head.trunk[0].weight.grad.abs().sum() > 0 and m.critic_head.trunk[0].weight.grad.abs().sum() > 0
    print("✓ gradient reaches patch_embed + W_q/W_k/W_o + H2 LSTM + codebook + both heads (full episode)")


def test_ppo_update_and_train():
    m = _model()
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    before = [p.detach().clone() for p in m.parameters()]
    res = ppo_update(m, torch.optim.Adam(m.parameters(), lr=1e-3), concat_batches([batch]),
                     PPOConfig(n_epochs=2, per_n_replay=0))
    for k in ("loss_policy", "loss_value", "loss_entropy", "loss_total"):
        assert torch.isfinite(torch.tensor(res[k])), f"{k} not finite: {res[k]}"
    assert sum(not torch.allclose(a, b.detach()) for a, b in zip(before, m.parameters())) > 0
    hist = train(m, env, n_iterations=2, episodes_per_iter=4,
                 cfg=PPOConfig(n_epochs=2, per_n_replay=2, buffer_capacity=16, burn_in_iters=1),
                 device=DEVICE, log_every=1, save_every=999)
    assert len(hist) == 2
    print("✓ ppo_update + train(): finite losses, params move, 2 end-to-end iters")


if __name__ == "__main__":
    tests = [
        test_patch_embed_shapes,
        test_structure_static_codebook,
        test_soft_weights_not_onehot,
        test_onehot_selection_hard_modes,
        test_routing_q_x_k_h2_v_codebook,
        test_x_only_as_queries_and_h2_grounding,
        test_Z_to_both_heads_and_rec,
        test_mode_determinism,
        test_soft_gradients,
        test_init_action_bias,
        test_rl_step_and_sequence,
        test_grad_flows_through_stack,
        test_ppo_update_and_train,
    ]
    for t in tests:
        t()
    print(f"\nAll {len(tests)} v12 smoke tests passed (default SOFT attention over a static codebook).")
