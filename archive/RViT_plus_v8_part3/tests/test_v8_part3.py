"""
Smoke tests for RViT+ v8_part3 — v8's H1-residual cross-attention encoder + a
PREDICTIVE-COMPARATOR write gate + learnable-gain H1 residual + H1‖H2 readout.

Proves: v8 attention topology intact (Q=X, 3N keys, H1-residual no-bypass);
comparator reduces to v8 at init (g≈0, h1_res_gain=1); the gate is monotone in
gate_scale and the predictor MSE (last_aux) is finite & trainable; heads read BOTH
H1 and H2; the self-supervised aux loss + harbor penalty train without breaking
the PER/PAC/burn-in trainer.

Run:  .venv/bin/python -m RViT_plus_v8_part3.tests.test_v8_part3
"""
from __future__ import annotations

import copy
import math
import os
import sys

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v8_part3.env import ChangeDetectionEnv
from RViT_plus_v8_part3.tx_lstm_encoder import ComparatorEncoder
from RViT_plus_v8_part3.model import RViTPlusV8Part3Model
from RViT_plus_v8_part3.ppo import (
    PPOConfig, collect_episodes, concat_batches, ppo_update, train,
)

DEVICE = torch.device("cpu")
torch.manual_seed(0)


def _model(**over):
    kw = dict(patch_size=5, d_model=64, d_mem=64, tx_heads=4, tx_layers=1, n_lstm=2,
              conv_channels=32, n_conv_layers=3, conv_kernel=5, n_actions=2, n_quantiles=8,
              init_action_bias=[0.0, -1.5], seq_len=29)
    kw.update(over)
    return RViTPlusV8Part3Model(**kw).to(DEVICE)


def test_patch_embed_shapes():
    m = _model()
    x = torch.randn(3, 3, 50, 50)
    tok = m.patch_embed(x)
    assert tok.shape == (3, 100, 64), tok.shape
    assert m.n_tokens == 100
    print("✓ patch_embed: (3,3,50,50) → (3,100,64); n_tokens=100")


def test_comparator_structure():
    """Encoder = v8 cross-attn block + 2 LSTMs + the comparator side-car
    (predictor + gate scalars + learnable H1-residual gain)."""
    m = _model(tx_heads=4, n_lstm=2)
    enc = m.encoder
    assert isinstance(enc, ComparatorEncoder)
    assert len(enc.blocks) == 1 and enc.blocks[0].attn.num_heads == 4
    assert enc.mem_tag.shape == (2, 1, 64) and enc.mem_pos_emb.shape == (1, 100, 64)
    assert len(enc.cells) == 2 and enc.cells[0].input_size == 64 and enc.cells[1].input_size == 64
    # comparator side-car
    assert enc.predictor.in_features == 64 and enc.predictor.out_features == 64, "predictor d_mem→d_model"
    assert enc.gate_scale.item() == 0.0, "gate_scale must init to 0 (g≈0 = v8 at init)"
    assert abs(enc.gate_bias.item() + 4.0) < 1e-6, "gate_bias must init to -4"
    assert abs(enc.h1_res_gain.item() - 1.0) < 1e-6, "h1_res_gain must init to 1.0 (= exact v8)"
    for p in (enc.gate_scale, enc.gate_bias, enc.h1_res_gain):
        assert p.requires_grad, "comparator/residual params must be learnable"
    try:
        ComparatorEncoder(n_tokens=100, d_model=64, d_mem=64, n_heads=4, n_lstm=3)
        raise AssertionError("n_lstm=3 should raise")
    except ValueError:
        pass
    print("✓ structure: v8 block + 2 LSTMs + predictor(64→64) + gate(0,-4) + h1_res_gain(1.0)")


def test_v8_attention_and_no_bypass():
    """v8 topology intact: Q=X over [X++H1++H2] = 3N keys, weights (B,heads,N,3N).
    H1-residual no-bypass: silence the attention out_proj and the recurrent update
    must be INDEPENDENT of the image (only route for visual content is the values)."""
    m = _model().eval()
    states = m.init_states(2, device=DEVICE)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    with torch.no_grad():
        (_Hs, _Cs), _rec, attn = m.encoder.forward_step(tok, states, return_attn=True)
        assert len(attn) == 1 and attn[0].shape == (2, 4, 100, 300), \
            f"attn shape {tuple(attn[0].shape)}, expected (2,4,100,300) = (B,heads,N,3N)"
    enc_cut = copy.deepcopy(m.encoder).eval()
    with torch.no_grad():
        enc_cut.blocks[0].attn.out_proj.weight.zero_()
        enc_cut.blocks[0].attn.out_proj.bias.zero_()
    tok_a = m.patch_embed(torch.randn(2, 3, 50, 50))
    tok_b = m.patch_embed(torch.randn(2, 3, 50, 50) * 3.0 + 1.0)
    with torch.no_grad():
        (_h, _c), rec_a = enc_cut.forward_step(tok_a, enc_cut.init_states(2))
        (_h2, _c2), rec_b = enc_cut.forward_step(tok_b, enc_cut.init_states(2))
        for ra, rb in zip(rec_a, rec_b):
            assert torch.allclose(ra, rb, atol=1e-6), "visual info leaked past silenced attention"
        (_h3, _c3), rec_c = m.encoder.forward_step(tok_a, m.init_states(2))
        (_h4, _c4), rec_d = m.encoder.forward_step(tok_b, m.init_states(2))
        assert not torch.allclose(rec_c[0], rec_d[0]), "intact attention should transmit the image"
    print("✓ v8 topology: Q=X over 3N=300 keys; H1-residual no-bypass holds")


def test_comparator_gate_and_aux():
    """At init g≈σ(-4)≈0.018 (≈v8). The gate is monotone in gate_scale, and the
    predictor MSE (last_aux) is a finite (B,) tensor with a gradient to the predictor."""
    m = _model().eval()
    states = m.init_states(4, device=DEVICE)
    tok = m.patch_embed(torch.randn(4, 3, 50, 50))
    with torch.no_grad():
        m.encoder.forward_step(tok, states)
        g0 = m.encoder.last_gate
        assert g0.shape == (4, 100, 1), g0.shape
        assert abs(float(g0.mean()) - 1.0 / (1.0 + math.exp(4.0))) < 0.02, "init gate must be ≈σ(-4)"
        assert m.encoder.last_surprise.min() >= 0.0, "surprise is a squared error ≥ 0"
        assert m.encoder.last_aux.shape == (4,) and torch.isfinite(m.encoder.last_aux).all()
        # monotone in gate_scale (surprise is generically > 0)
        m.encoder.gate_scale.copy_(torch.tensor([8.0]))
        m.encoder.forward_step(tok, states)
        g_hi = float(m.encoder.last_gate.mean())
        m.encoder.gate_scale.copy_(torch.tensor([0.0]))
    assert g_hi > float(g0.mean()), "raising gate_scale must open the gate for positive surprise"
    # predictor trains from the self-supervised aux loss — needs a NON-zero carried
    # H2 (at the init state H2=0, so predictor reads zeros and only its bias moves).
    m2 = _model()
    st2 = m2.init_states(2)
    st2 = ([st2[0][0], torch.randn(2, 100, 64)], [st2[1][0], st2[1][1]])
    (_s, _r) = m2.encoder.forward_step(m2.patch_embed(torch.randn(2, 3, 50, 50)), st2)
    m2.zero_grad(); m2.encoder.last_aux.mean().backward()
    assert m2.encoder.predictor.weight.grad is not None and m2.encoder.predictor.weight.grad.abs().sum() > 0, \
        "predictor gets no gradient from the self-supervised aux loss"
    print("✓ comparator: init g≈0.018, monotone in gate_scale, aux MSE finite & trains the predictor")


def test_learnable_h1_residual_gain():
    """h1_res_gain scales the carried-H1 skip; changing it changes the recurrent
    update (and gain=0 removes the residual entirely)."""
    m = _model().eval()
    tok = m.patch_embed(torch.randn(3, 3, 50, 50))
    st = m.init_states(3, device=DEVICE)
    # use a non-zero carried H1 so the residual is actually present
    st = ([torch.randn(3, 100, 64), st[0][1]], [st[1][0], st[1][1]])
    with torch.no_grad():
        (_a, _b), rec1 = m.encoder.forward_step(tok, st)
        m.encoder.h1_res_gain.copy_(torch.tensor([0.0]))
        (_c, _d), rec0 = m.encoder.forward_step(tok, st)
        m.encoder.h1_res_gain.copy_(torch.tensor([1.0]))
    assert not torch.allclose(rec1[0], rec0[0]), "h1_res_gain has no effect — residual not gained"
    print("✓ learnable H1-residual gain: scales the skip (init 1.0 = exact v8; 0.0 removes it)")


def test_decoders_read_both_states():
    """Heads run a Conv1d-over-tokens trunk on [H1 ‖ H2]: output depends on BOTH
    states and is token-permutation SENSITIVE; first conv ingests 2·d_mem channels."""
    import torch.nn as nn
    m = _model().eval()
    B = 4
    H1, H2 = torch.randn(B, 100, 64), torch.randn(B, 100, 64)
    with torch.no_grad():
        logits = m.actor_head([H1, H2])
        q = m.critic_head([H1, H2])
        assert logits.shape == (B, 2) and q.shape == (B, 2, 8)
        assert not torch.allclose(logits, m.actor_head([torch.randn(B, 100, 64), H2])), "actor ignores H1"
        assert not torch.allclose(logits, m.actor_head([H1, torch.randn(B, 100, 64)])), "actor ignores H2"
        perm = torch.randperm(100)
        assert not torch.allclose(logits, m.actor_head([H1[:, perm], H2[:, perm]]), atol=1e-5), \
            "conv output permutation-invariant — spatial layout not used"
    convs = [mod for mod in m.actor_head.trunk if isinstance(mod, nn.Conv1d)]
    assert convs[0].in_channels == 128, "first conv must ingest 2*d_mem=128 (H1 ‖ H2)"
    print("✓ heads conv over [H1‖H2]: both-state-sensitive, permutation-SENSITIVE, in_ch=128")


def test_init_action_bias():
    m = _model(init_action_bias=[0.0, -1.5])
    H1 = torch.zeros(8, 100, 64); H2 = torch.zeros(8, 100, 64)
    p_press = torch.softmax(m.actor_head([H1, H2]), dim=-1)[:, 1].mean().item()
    assert 0.05 < p_press < 0.35, f"P(press)≈{p_press:.3f} not in expected init band"
    print(f"✓ init_action_bias: initial P(press) ≈ {p_press:.3f} (mostly-wait)")


def test_rl_step_and_sequence():
    m = _model()
    states = m.init_states(1, device=DEVICE)
    step = m.rl_step(torch.randn(1, 3, 50, 50), states)
    for k in ("new_states", "actor_logits", "critic_q_dist", "V_dist", "V_scalar"):
        assert k in step, k
    assert step["actor_logits"].shape == (1, 2) and step["critic_q_dist"].shape == (1, 2, 8)
    B, T = 3, 29
    out = m.forward_rl_sequence(torch.randn(B, T, 3, 50, 50))
    assert out["actor_logits_seq"].shape == (B, T, 2)
    assert out["q_dist_seq"].shape == (B, T, 2, 8)
    assert out["aux_pred_seq"].shape == (B, T), "comparator aux loss must be exposed per (B,T)"
    assert torch.isfinite(out["aux_pred_seq"]).all()
    print("✓ rl_step + forward_rl_sequence: shapes correct; aux_pred_seq (B,T) finite")


def test_grad_flows_through_stack():
    """Reward + aux gradient must reach the patch MLP, attention, both LSTMs, the
    conv heads, the predictor, the gate scalars, and the H1-residual gain."""
    m = _model()
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    out = m.forward_rl_sequence(batch.observations)
    loss = (out["actor_logits_seq"].pow(2).mean() + out["q_dist_seq"].pow(2).mean()
            + out["aux_pred_seq"].mean())
    m.zero_grad(); loss.backward()
    assert m.patch_embed.proj[0].weight.grad.abs().sum() > 0, "no grad to patch embed"
    assert m.encoder.blocks[0].attn.in_proj_weight.grad.abs().sum() > 0, "no grad to attention"
    for li, cell in enumerate(m.encoder.cells):
        assert cell.weight_ih.grad is not None and cell.weight_ih.grad.abs().sum() > 0, f"no grad to LSTM{li+1}"
    assert m.encoder.predictor.weight.grad.abs().sum() > 0, "no grad to predictor"
    assert m.encoder.gate_scale.grad is not None and m.encoder.gate_scale.grad.abs().item() > 0, "no grad to gate_scale"
    assert m.encoder.h1_res_gain.grad is not None and m.encoder.h1_res_gain.grad.abs().item() > 0, "no grad to h1_res_gain"
    assert m.actor_head.trunk[0].weight.grad.abs().sum() > 0 and m.critic_head.trunk[0].weight.grad.abs().sum() > 0
    print("✓ gradient reaches patch_embed + attn + both LSTMs + heads + predictor + gate_scale + h1_res_gain")


def test_ppo_update_with_aux_and_harbor():
    m = _model()
    env = ChangeDetectionEnv()
    cfg = PPOConfig(n_epochs=2, per_n_replay=0, pred_loss_coef=0.1, harbor_coef=0.01)
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    before = [p.detach().clone() for p in m.parameters()]
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    res = ppo_update(m, opt, concat_batches([batch]), cfg)
    for k in ("loss_policy", "loss_value", "loss_entropy", "loss_pred", "loss_harbor", "loss_total"):
        assert torch.isfinite(torch.tensor(res[k])), f"{k} not finite: {res[k]}"
    assert res["loss_pred"] > 0.0, "comparator predictor loss should be > 0 before training"
    assert res["loss_harbor"] > 0.0, "harbor term should be > 0 in the actor phase"
    changed = sum(not torch.allclose(a, b.detach()) for a, b in zip(before, m.parameters()))
    assert changed > 0
    print(f"✓ ppo_update: finite incl. loss_pred={res['loss_pred']:.3f} loss_harbor={res['loss_harbor']:.3f}; {changed} tensors moved")


def test_pac_target_network_and_burn_in():
    env = ChangeDetectionEnv()
    m = _model()
    assert not any("target" in k for k in m.state_dict()), "target net must NOT be in state_dict"
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
    print("✓ PAC target network + burn-in: burn-in freezes actor (harbor off), trains critic")


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
        test_comparator_structure,
        test_v8_attention_and_no_bypass,
        test_comparator_gate_and_aux,
        test_learnable_h1_residual_gain,
        test_decoders_read_both_states,
        test_init_action_bias,
        test_rl_step_and_sequence,
        test_grad_flows_through_stack,
        test_ppo_update_with_aux_and_harbor,
        test_pac_target_network_and_burn_in,
        test_end_to_end_train_iteration,
    ]
    for t in tests:
        t()
    print(f"\nAll {len(tests)} v8_part3 smoke tests passed "
          f"(incl. comparator-write + learnable-residual + H1‖H2 readout proofs).")
