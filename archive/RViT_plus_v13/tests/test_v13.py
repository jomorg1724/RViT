"""
Smoke tests for RViT+ v13 — a frozen self-supervised PREDICTIVE-CODING encoder
repurposed for RL by an ENERGY-MODULATION stream.

  Phase 1: predictive_forward → JEPA loss (H2_t predicts H1_{t+1}) trains PART A.
  Phase 2: freeze_pc(), then RL with use_energy=True — the energy stream (LSTM3+T2)
           perturbs the FROZEN encoder's V path; only PART B + heads train.

Run:  .venv/bin/python -m RViT_plus_v13.tests.test_v13
"""
from __future__ import annotations

import os
import sys

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v13.env import ChangeDetectionEnv
from RViT_plus_v13.tx_lstm_encoder import VQAttnEncoder
from RViT_plus_v13.model import RViTPlusV13Model
from RViT_plus_v13.ppo import PPOConfig, collect_episodes, concat_batches, ppo_update, train

DEVICE = torch.device("cpu")
torch.manual_seed(0)


def _model(**over):
    kw = dict(patch_size=5, d_model=64, d_mem=64, tx_heads=1, n_lstm=1, conv_channels=32,
              n_conv_layers=3, conv_kernel=5, n_actions=2, n_quantiles=8,
              init_action_bias=[0.0, -1.5], seq_len=29, d_latent=64)
    kw.update(over)
    return RViTPlusV13Model(**kw).to(DEVICE)


def _state(B, N=100, d=64):
    z = lambda: torch.randn(B, N, d)
    return [z(), z(), z()], [z(), z(), z()]


def test_patch_embed_shapes():
    m = _model()
    assert m.patch_embed(torch.randn(3, 3, 50, 50)).shape == (3, 100, 64) and m.n_tokens == 100
    print("✓ patch_embed: (3,3,50,50) → (3,100,64)")


def test_structure_two_parts():
    enc = _model().encoder
    assert isinstance(enc, VQAttnEncoder)
    for nm in ("T1", "lstm1", "lstm2", "proj1", "proj2", "predictor"):   # PART A
        assert hasattr(enc, nm), f"missing PART A {nm}"
    for nm in ("T2", "lstm3"):                                            # PART B
        assert hasattr(enc, nm), f"missing PART B {nm}"
    assert len(enc.cells) == 3, "three LSTMs (LSTM1/2/3)"
    pc = set(id(p) for mod in enc.pc_modules() for p in ([mod] if isinstance(mod, torch.nn.Parameter) else mod.parameters()))
    en = set(id(p) for mod in enc.energy_modules() for p in ([mod] if isinstance(mod, torch.nn.Parameter) else mod.parameters()))
    assert pc.isdisjoint(en), "PART A and PART B parameter groups must be disjoint"
    print("✓ structure: PART A (T1+LSTM1+LSTM2+predictor) ⟂ PART B (LSTM3+T2)")


def test_phase1_step_no_energy():
    m = _model().eval()
    st = m.init_states(2, device=DEVICE)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    (Hs, _Cs), rec = m.encoder.forward_step(tok, st, use_energy=False)
    assert rec[0].shape == (2, 100, 64), "Z1 shape"
    assert m.encoder.last_Zenergy is None, "no energy computed in Phase 1"
    assert torch.allclose(Hs[2], st[0][2]), "H3 untouched in Phase 1 (no energy)"
    print("✓ Phase 1 step: T1 over V=H2, H1/H2 update, H3 untouched, no energy")


def test_phase2_energy_modulates_Z1():
    """use_energy=True computes Z_energy and changes Z1 (the energy modulates T1's V)."""
    m = _model().eval()
    st = _state(2)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    with torch.no_grad():
        (_a, _b), rec_off = m.encoder.forward_step(tok, st, use_energy=False)
        (Hs, _c), rec_on = m.encoder.forward_step(tok, st, use_energy=True)
    assert m.encoder.last_Zenergy is not None and m.encoder.last_Zenergy.shape == (2, 100, 64)
    assert not torch.allclose(rec_off[0], rec_on[0]), "energy must modulate Z1 (via T1's V path)"
    assert not torch.allclose(Hs[2], st[0][2]), "H3 must update under energy (LSTM3)"
    print("✓ Phase 2 step: energy stream computes Z_energy and modulates Z1; H3 updates")


def test_predictive_loss_trains_partA_only():
    m = _model()
    out = m.predictive_forward(torch.randn(2, 12, 3, 50, 50))
    assert out["surprise_seq"].shape == (2, 12), "surprise is quantified per step (B,T)"
    assert out["loss"].requires_grad
    m.zero_grad(); out["loss"].backward()
    # PART A + patch_embed get gradient...
    assert m.patch_embed.proj[0].weight.grad.abs().sum() > 0, "patch_embed should train in Phase 1"
    for nm, w in (("T1.W_q", m.encoder.T1.W_q.weight), ("lstm1", m.encoder.lstm1.weight_ih),
                  ("lstm2", m.encoder.lstm2.weight_ih), ("proj1", m.encoder.proj1[0].weight),
                  ("proj2", m.encoder.proj2[0].weight), ("predictor", m.encoder.predictor[0].weight)):
        assert w.grad is not None and w.grad.abs().sum() > 0, f"PART A {nm} must train in Phase 1"
    # ...PART B (energy) gets NONE (not used in Phase 1)
    assert m.encoder.lstm3.weight_ih.grad is None and m.encoder.T2.W_q.weight.grad is None, \
        "PART B must NOT train in Phase 1 (energy unused)"
    print(f"✓ predictive loss: quantified surprise (mean={float(out['surprise_seq'].mean()):.4f}); "
          f"trains PART A (incl. proj1 target), NOT PART B")


def test_freeze_pc_then_rl_trains_only_energy():
    m = _model()
    n_frozen = m.freeze_pc()
    assert m.use_energy is True and n_frozen > 0
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    out = m.forward_rl_sequence(batch.observations)
    loss = out["actor_logits_seq"].pow(2).mean() + out["q_dist_seq"].pow(2).mean()
    m.zero_grad(); loss.backward()
    # PART B (energy) + heads train
    assert m.encoder.lstm3.weight_ih.grad.abs().sum() > 0, "LSTM3 (energy) must train in Phase 2"
    assert m.encoder.T2.W_q.weight.grad.abs().sum() > 0, "T2 (energy) must train in Phase 2"
    assert m.actor_head.trunk[0].weight.grad.abs().sum() > 0 and m.critic_head.trunk[0].weight.grad.abs().sum() > 0
    # PART A + patch_embed are FROZEN (no grad)
    assert m.encoder.T1.W_q.weight.grad is None, "T1 must be FROZEN in Phase 2"
    assert m.encoder.lstm1.weight_ih.grad is None and m.encoder.lstm2.weight_ih.grad is None, "LSTM1/2 frozen"
    assert m.patch_embed.proj[0].weight.grad is None, "patch_embed frozen"
    print(f"✓ freeze_pc → Phase 2: trains ONLY energy (LSTM3,T2) + heads; PART A frozen ({n_frozen:,} params)")


def test_rl_step_and_sequence():
    m = _model(); m.freeze_pc()
    step = m.rl_step(torch.randn(1, 3, 50, 50), m.init_states(1, device=DEVICE))
    assert step["actor_logits"].shape == (1, 2) and step["critic_q_dist"].shape == (1, 2, 8)
    out = m.forward_rl_sequence(torch.randn(3, 29, 3, 50, 50))
    assert out["actor_logits_seq"].shape == (3, 29, 2) and out["q_dist_seq"].shape == (3, 29, 2, 8)
    print("✓ rl_step + forward_rl_sequence (Phase 2): shapes correct")


def test_init_action_bias():
    m = _model(init_action_bias=[0.0, -1.5])
    p_press = torch.softmax(m.actor_head([torch.zeros(8, 100, 64)]), dim=-1)[:, 1].mean().item()
    assert 0.05 < p_press < 0.35
    print(f"✓ init_action_bias: initial P(press) ≈ {p_press:.3f}")


def test_ppo_update_and_train_phase2():
    m = _model(); m.freeze_pc()
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    before = [p.detach().clone() for p in m.parameters() if p.requires_grad]
    res = ppo_update(m, torch.optim.Adam([p for p in m.parameters() if p.requires_grad], lr=1e-3),
                     concat_batches([batch]), PPOConfig(n_epochs=2, per_n_replay=0))
    for k in ("loss_policy", "loss_value", "loss_total"):
        assert torch.isfinite(torch.tensor(res[k])), f"{k} not finite"
    assert sum(not torch.allclose(a, b.detach()) for a, b in zip(before, [p for p in m.parameters() if p.requires_grad])) > 0
    hist = train(m, env, n_iterations=2, episodes_per_iter=4,
                 cfg=PPOConfig(n_epochs=2, per_n_replay=2, buffer_capacity=16, burn_in_iters=1),
                 device=DEVICE, log_every=1, save_every=999)
    assert len(hist) == 2
    print("✓ ppo_update + train() Phase 2: finite losses, trainable params move, 2 iters")


if __name__ == "__main__":
    tests = [
        test_patch_embed_shapes,
        test_structure_two_parts,
        test_phase1_step_no_energy,
        test_phase2_energy_modulates_Z1,
        test_predictive_loss_trains_partA_only,
        test_freeze_pc_then_rl_trains_only_energy,
        test_rl_step_and_sequence,
        test_init_action_bias,
        test_ppo_update_and_train_phase2,
    ]
    for t in tests:
        t()
    print(f"\nAll {len(tests)} v13 smoke tests passed "
          f"(frozen predictive-coding encoder + energy-modulation RL).")
