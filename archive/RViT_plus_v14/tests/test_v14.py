"""
Smoke tests for RViT+ v14 — TWO coupled recurrent modules trained CONCURRENTLY:
Module 1 (T1+LSTM1) by self-supervised predictive coding, Module 2 (T2+LSTM2) by RL,
with cross-detachments that FIREWALL the gradients.

  forward:  Z2=T2(H1.detach,H2); H2=LSTM2(Z2);  Z1=T1(X,Z2.detach,H1); H1=LSTM1(Z1)
  RL loss   → Module 2 (T2,LSTM2) + heads only      (H1 detached in T2)
  SS loss   → Module 1 (T1,LSTM1,proj,predictor,patch_embed) only  (Z2 detached in T1)

Run:  .venv/bin/python -m RViT_plus_v14.tests.test_v14
"""
from __future__ import annotations

import os
import sys

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v14.env import ChangeDetectionEnv
from RViT_plus_v14.tx_lstm_encoder import VQAttnEncoder
from RViT_plus_v14.model import RViTPlusV14Model
from RViT_plus_v14.ppo import PPOConfig, collect_episodes, concat_batches, ppo_update, train

DEVICE = torch.device("cpu")
torch.manual_seed(0)


def _model(**over):
    kw = dict(patch_size=5, d_model=64, d_mem=64, tx_heads=1, n_lstm=1, conv_channels=32,
              n_conv_layers=3, conv_kernel=5, n_actions=2, n_quantiles=8,
              init_action_bias=[0.0, -1.5], seq_len=29, d_latent=64, pc_horizon=1)
    kw.update(over)
    return RViTPlusV14Model(**kw).to(DEVICE)


def test_patch_embed_shapes():
    m = _model()
    assert m.patch_embed(torch.randn(3, 3, 50, 50)).shape == (3, 100, 64) and m.n_tokens == 100
    print("✓ patch_embed: (3,3,50,50) → (3,100,64)")


def test_structure_two_modules():
    enc = _model().encoder
    assert isinstance(enc, VQAttnEncoder)
    for nm in ("T1", "lstm1", "proj", "predictor"):       # Module 1
        assert hasattr(enc, nm), f"missing Module 1 {nm}"
    for nm in ("T2", "lstm2"):                              # Module 2
        assert hasattr(enc, nm), f"missing Module 2 {nm}"
    m1 = set(id(p) for mod in enc.module1_params() for p in ([mod] if isinstance(mod, torch.nn.Parameter) else mod.parameters()))
    m2 = set(id(p) for mod in enc.module2_params() for p in ([mod] if isinstance(mod, torch.nn.Parameter) else mod.parameters()))
    assert m1.isdisjoint(m2), "Module 1 / Module 2 parameter groups must be disjoint"
    print("✓ structure: Module 1 (T1+LSTM1+predictor) ⟂ Module 2 (T2+LSTM2)")


def test_forward_step_rec_is_H2():
    m = _model().eval()
    st = m.init_states(2, device=DEVICE)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    (Hs, _Cs), rec = m.encoder.forward_step(tok, st)
    assert len(Hs) == 2 and rec[0].shape == (2, 100, 64), "state=[H1,H2]; rec=[H2]"
    assert torch.allclose(rec[0], Hs[1]), "rec must be H2 (Module 2 state the heads read)"
    print("✓ forward_step: state=[H1,H2], rec=[H2] (actor/critic read Module 2's H2)")


def test_firewall_RL_loss_only_module2():
    """The RL loss (on H2 via the heads) trains ONLY Module 2 + heads — H1 is detached
    in T2, so NO gradient reaches Module 1 (or patch_embed)."""
    m = _model()
    out = m.forward_rl_sequence(torch.randn(3, 29, 3, 50, 50))
    L_rl = out["actor_logits_seq"].pow(2).mean() + out["q_dist_seq"].pow(2).mean()   # NO H1/SS term
    m.zero_grad(); L_rl.backward()
    # Module 2 + heads train
    assert m.encoder.T2.W_q.weight.grad.abs().sum() > 0, "T2 (Module 2) must get RL grad"
    assert m.encoder.lstm2.weight_ih.grad.abs().sum() > 0, "LSTM2 (Module 2) must get RL grad"
    assert m.actor_head.trunk[0].weight.grad.abs().sum() > 0 and m.critic_head.trunk[0].weight.grad.abs().sum() > 0
    # Module 1 + patch_embed FIREWALLED
    assert m.encoder.T1.W_q.weight.grad is None, "T1 (Module 1) must get NO RL grad"
    assert m.encoder.lstm1.weight_ih.grad is None, "LSTM1 (Module 1) must get NO RL grad"
    assert m.encoder.predictor[0].weight.grad is None, "predictor must get NO RL grad"
    assert m.patch_embed.proj[0].weight.grad is None, "patch_embed must get NO RL grad (only via detached H1)"
    print("✓ FIREWALL: RL loss → Module 2 (T2,LSTM2) + heads only; Module 1 + patch_embed get NO RL grad")


def test_firewall_SS_loss_only_module1():
    """The self-supervised predictive loss (on H1) trains ONLY Module 1 (+ patch_embed)
    — Z2 is detached in T1, so NO gradient reaches Module 2 or the heads."""
    m = _model()
    out = m.forward_rl_sequence(torch.randn(3, 29, 3, 50, 50))
    L_ss, surprise, parts = m.encoder.predictive_loss(out["H1_seq"], torch.ones(3, 29))
    assert surprise.shape == (3, 29) and L_ss.requires_grad
    m.zero_grad(); L_ss.backward()
    # Module 1 + patch_embed train
    assert m.encoder.T1.W_q.weight.grad.abs().sum() > 0, "T1 (Module 1) must get SS grad"
    assert m.encoder.lstm1.weight_ih.grad.abs().sum() > 0, "LSTM1 (Module 1) must get SS grad"
    assert m.encoder.proj[0].weight.grad.abs().sum() > 0 and m.encoder.predictor[0].weight.grad.abs().sum() > 0
    assert m.patch_embed.proj[0].weight.grad.abs().sum() > 0, "patch_embed must get SS grad (Module 1)"
    # Module 2 + heads FIREWALLED
    assert m.encoder.T2.W_q.weight.grad is None, "T2 (Module 2) must get NO SS grad (Z2 detached in T1)"
    assert m.encoder.lstm2.weight_ih.grad is None, "LSTM2 (Module 2) must get NO SS grad"
    assert m.actor_head.trunk[0].weight.grad is None and m.critic_head.trunk[0].weight.grad is None, \
        "heads must get NO SS grad"
    print(f"✓ FIREWALL: SS loss → Module 1 + patch_embed only (surprise={float(surprise.mean()):.4f}); "
          f"Module 2 + heads get NO SS grad")


def test_rl_step_and_sequence():
    m = _model()
    step = m.rl_step(torch.randn(1, 3, 50, 50), m.init_states(1, device=DEVICE))
    assert step["actor_logits"].shape == (1, 2) and step["critic_q_dist"].shape == (1, 2, 8)
    out = m.forward_rl_sequence(torch.randn(3, 29, 3, 50, 50))
    assert out["actor_logits_seq"].shape == (3, 29, 2) and out["H1_seq"].shape == (3, 29, 100, 64)
    print("✓ rl_step + forward_rl_sequence: shapes correct (+ H1_seq for the SS loss)")


def test_init_action_bias():
    m = _model(init_action_bias=[0.0, -1.5])
    p_press = torch.softmax(m.actor_head([torch.zeros(8, 100, 64)]), dim=-1)[:, 1].mean().item()
    assert 0.05 < p_press < 0.35
    print(f"✓ init_action_bias: initial P(press) ≈ {p_press:.3f}")


def test_concurrent_ppo_trains_both_modules():
    """One ppo_update with ss_coef>0 moves BOTH a Module-1 param (via SS) and a
    Module-2 param (via RL) — concurrent training from a single loss."""
    m = _model()
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    m1_before = m.encoder.T1.W_q.weight.detach().clone()    # Module 1
    m2_before = m.encoder.T2.W_q.weight.detach().clone()    # Module 2
    res = ppo_update(m, torch.optim.Adam(m.parameters(), lr=1e-3), concat_batches([batch]),
                     PPOConfig(n_epochs=2, per_n_replay=0, ss_coef=1.0))
    for k in ("loss_policy", "loss_value", "loss_ss", "loss_total"):
        assert torch.isfinite(torch.tensor(res[k])), f"{k} not finite"
    assert res["loss_ss"] > 0.0, "the self-supervised loss must be active"
    assert not torch.allclose(m.encoder.T1.W_q.weight, m1_before), "Module 1 must train (via SS)"
    assert not torch.allclose(m.encoder.T2.W_q.weight, m2_before), "Module 2 must train (via RL)"
    print(f"✓ concurrent ppo_update: L_ss={res['loss_ss']:.3f}; BOTH Module 1 (SS) and Module 2 (RL) train")


def test_train_loop():
    m = _model()
    env = ChangeDetectionEnv()
    hist = train(m, env, n_iterations=2, episodes_per_iter=4,
                 cfg=PPOConfig(n_epochs=2, per_n_replay=2, buffer_capacity=16, burn_in_iters=1, ss_coef=1.0),
                 device=DEVICE, log_every=1, save_every=999)
    assert len(hist) == 2 and "loss_ss" in hist[-1]
    print("✓ train(): 2 end-to-end iters with concurrent RL + self-supervised PC")


if __name__ == "__main__":
    tests = [
        test_patch_embed_shapes,
        test_structure_two_modules,
        test_forward_step_rec_is_H2,
        test_firewall_RL_loss_only_module2,
        test_firewall_SS_loss_only_module1,
        test_rl_step_and_sequence,
        test_init_action_bias,
        test_concurrent_ppo_trains_both_modules,
        test_train_loop,
    ]
    for t in tests:
        t()
    print(f"\nAll {len(tests)} v14 smoke tests passed "
          f"(two coupled modules, concurrent RL + self-supervised, firewalled gradients).")
