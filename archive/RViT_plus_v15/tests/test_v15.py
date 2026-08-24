"""
Smoke tests for RViT+ v15 — v12's gradient-learned codebook + a VQ-VAE-style ENERGY
term. Z = C + energy(C,H2); the v12 soft readout reads Z; three-way loss = RL task +
commitment penalty mean‖energy‖² + EMA C toward Z. REDUCES TO v12 when energy → 0.

Run:  .venv/bin/python -m RViT_plus_v15.tests.test_v15
"""
from __future__ import annotations

import os
import sys

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v15.env import ChangeDetectionEnv
from RViT_plus_v15.tx_lstm_encoder import VQAttnEncoder
from RViT_plus_v15.model import RViTPlusV15Model
from RViT_plus_v15.ppo import PPOConfig, collect_episodes, concat_batches, ppo_update, train

DEVICE = torch.device("cpu")
torch.manual_seed(0)


def _model(**over):
    kw = dict(patch_size=5, d_model=64, d_mem=64, tx_heads=1, n_lstm=1, conv_channels=32,
              n_conv_layers=3, conv_kernel=5, n_actions=2, n_quantiles=8,
              init_action_bias=[0.0, -1.5], seq_len=29)
    kw.update(over)
    return RViTPlusV15Model(**kw).to(DEVICE)


def _state(B, N=100, d=64):
    return [torch.randn(B, N, d)], [torch.randn(B, N, d)]


def test_patch_embed_shapes():
    m = _model()
    assert m.patch_embed(torch.randn(3, 3, 50, 50)).shape == (3, 100, 64) and m.n_tokens == 100
    print("✓ patch_embed: (3,3,50,50) → (3,100,64)")


def test_structure_codebook_param_plus_energy():
    enc = _model().encoder
    assert isinstance(enc, VQAttnEncoder)
    assert "codebook" in dict(enc.named_parameters()), "codebook must be a GRADIENT parameter (v12 core)"
    assert enc.codebook.shape == (1, 100, 64) and enc.codebook.requires_grad
    assert hasattr(enc, "T_E"), "energy transformer T_E"
    for nm in ("W_q", "W_k", "W_o", "cell"):
        assert hasattr(enc, nm), f"readout {nm}"
    print("✓ structure: codebook = gradient Parameter (v12 core) + energy transformer T_E")


def test_energy_small_at_init_reduces_to_v12():
    """Zero-init of T_E's output ⇒ energy ≈ 0 at init ⇒ Z ≈ C ⇒ the readout reads the
    codebook = byte-for-byte v12."""
    m = _model().eval()
    st = m.init_states(2, device=DEVICE)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    m.encoder.forward_step(tok, st)
    e = m.encoder.last_energy
    edev = float(m.encoder.last_energy_cost.max())
    assert e.abs().max() < 0.2 and edev < 0.05, f"energy must be ~0 at init (reduce to v12); got dev={edev:.4f}"
    print(f"✓ reduce-to-v12: energy ≈ 0 at init (mean‖energy‖²≈{edev:.4f}) → readout reads codebook = v12")


def test_forward_step_rec_and_energy():
    m = _model().eval()
    st = _state(2)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    (Hs, _Cs), rec = m.encoder.forward_step(tok, st)
    assert len(Hs) == 1 and rec[0].shape == (2, 100, 64), "state=[H2]; rec=[Z_read]"
    assert m.encoder.last_energy.shape == (2, 100, 64) and m.encoder.last_energy_cost.shape == (2,)
    print("✓ forward_step: state=[H2], rec=[Z_read]; energy (B,N,d) + cost (B,) exposed")


def test_codebook_is_gradient_learned():
    """The codebook is trained by the TASK gradient (the v12 core) — via Z = C + energy."""
    m = _model()
    out = m.forward_rl_sequence(torch.randn(3, 29, 3, 50, 50))
    loss = out["actor_logits_seq"].pow(2).mean() + out["q_dist_seq"].pow(2).mean()
    m.zero_grad(); loss.backward()
    assert m.encoder.codebook.grad is not None and m.encoder.codebook.grad.abs().sum() > 0, \
        "codebook must get TASK gradient (it's the v12 gradient-learned core)"
    assert m.encoder.T_E.W_q.weight.grad.abs().sum() > 0, "energy transformer T_E gets task grad too"
    assert m.actor_head.trunk[0].weight.grad.abs().sum() > 0
    print("✓ codebook is GRADIENT-learned by the task (v12 core); T_E + heads also train")


def test_commitment_cost_differentiable_into_energy():
    m = _model().eval()
    st = _state(2)
    tok = m.patch_embed(torch.randn(2, 3, 50, 50))
    m.encoder.forward_step(tok, st)
    cost = m.encoder.last_energy_cost
    assert cost.shape == (2,)
    m.zero_grad(); cost.sum().backward()
    for nm in ("W_q", "W_k", "W_v", "W_o"):
        g = getattr(m.encoder.T_E, nm).weight.grad
        assert g is not None and g.abs().sum() > 0, f"commitment cost must reach T_E.{nm}"
    print("✓ commitment cost mean‖energy‖² → grad into the energy transformer (shrinks energy)")


def test_ema_codebook_toward_Z():
    """EMA C += r·mean(energy) (toward Z); no grad; rate 0 freezes. (Parameter, but
    EMA-nudged in-place under no_grad — on top of the gradient learning.)"""
    enc = _model().encoder.eval()
    before = enc.codebook.detach().clone()
    mean_energy = torch.randn(100, 64)
    inc = enc.ema_update_codebook(mean_energy, rate=0.01)
    assert torch.allclose(enc.codebook, before + 0.01 * mean_energy.unsqueeze(0), atol=1e-6), \
        "C must move by r·mean(energy) (EMA toward Z = C + energy)"
    b2 = enc.codebook.detach().clone()
    enc.ema_update_codebook(mean_energy, rate=0.0)
    assert torch.allclose(enc.codebook, b2), "rate 0 freezes (no consolidation)"
    print("✓ EMA: C += r·mean(energy) toward Z (no grad); rate 0 freezes")


def test_sequence_exposes_energy():
    m = _model()
    out = m.forward_rl_sequence(torch.randn(3, 29, 3, 50, 50))
    assert out["energy_cost_seq"].shape == (3, 29) and out["energy_cost_seq"].requires_grad
    assert out["energy_seq"].shape == (3, 29, 100, 64) and not out["energy_seq"].requires_grad
    print("✓ forward_rl_sequence: energy_cost_seq (B,T diff) + energy_seq (B,T,N,d detached)")


def test_init_action_bias():
    m = _model(init_action_bias=[0.0, -1.5])
    p_press = torch.softmax(m.actor_head([torch.zeros(8, 100, 64)]), dim=-1)[:, 1].mean().item()
    assert 0.05 < p_press < 0.35
    print(f"✓ init_action_bias: initial P(press) ≈ {p_press:.3f}")


def test_rl_step_and_sequence():
    m = _model()
    step = m.rl_step(torch.randn(1, 3, 50, 50), m.init_states(1, device=DEVICE))
    assert step["actor_logits"].shape == (1, 2) and step["critic_q_dist"].shape == (1, 2, 8)
    out = m.forward_rl_sequence(torch.randn(3, 29, 3, 50, 50))
    assert out["actor_logits_seq"].shape == (3, 29, 2)
    print("✓ rl_step + forward_rl_sequence: shapes correct")


def test_ppo_update_energy_and_ema():
    m = _model()
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(m, env, n_episodes=4, device=DEVICE)
    cb_before = m.encoder.codebook.detach().clone()
    before = [p.detach().clone() for p in m.parameters()]
    res = ppo_update(m, torch.optim.Adam(m.parameters(), lr=1e-3), concat_batches([batch]),
                     PPOConfig(n_epochs=2, per_n_replay=0, energy_coef=0.01, codebook_ema_rate=0.1))
    for k in ("loss_policy", "loss_value", "loss_energy", "loss_total"):
        assert torch.isfinite(torch.tensor(res[k])), f"{k} not finite"
    assert sum(not torch.allclose(a, b.detach()) for a, b in zip(before, m.parameters())) > 0
    assert not torch.allclose(m.encoder.codebook, cb_before), "codebook must move (gradient + EMA)"
    hist = train(m, env, n_iterations=2, episodes_per_iter=4,
                 cfg=PPOConfig(n_epochs=2, per_n_replay=2, buffer_capacity=16, burn_in_iters=1,
                               energy_coef=0.01, codebook_ema_rate=0.001),
                 device=DEVICE, log_every=1, save_every=999)
    assert len(hist) == 2 and "loss_energy" in hist[-1] and "codebook_drift" in hist[-1]
    print(f"✓ ppo_update: energy term + EMA active (L_eng={res['loss_energy']:.4f}, cbΔ={res['codebook_drift']:.2e}); 2-iter train")


if __name__ == "__main__":
    tests = [
        test_patch_embed_shapes,
        test_structure_codebook_param_plus_energy,
        test_energy_small_at_init_reduces_to_v12,
        test_forward_step_rec_and_energy,
        test_codebook_is_gradient_learned,
        test_commitment_cost_differentiable_into_energy,
        test_ema_codebook_toward_Z,
        test_sequence_exposes_energy,
        test_init_action_bias,
        test_rl_step_and_sequence,
        test_ppo_update_energy_and_ema,
    ]
    for t in tests:
        t()
    print(f"\nAll {len(tests)} v15 smoke tests passed "
          f"(v12 gradient codebook + VQ-VAE energy term + commitment + EMA; reduces to v12).")
