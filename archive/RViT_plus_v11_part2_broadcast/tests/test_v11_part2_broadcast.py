"""Smoke tests for v11_part2_BROADCAST: the v11_part2 split structure with the
Herman/Morgan multiplicative self-attention in the FiLM form:
    Q = Q_X(X) ⊙ (1 + Q_H(H)),  K = ...,  V = ...   ;  Z = X + softmax(QKᵀ/√d)V + FFN
both streams read the top-down memory H = [H1‖H2] and use X as the residual.

Run:  .venv/bin/python -m RViT_plus_v11_part2_broadcast.tests.test_v11_part2_broadcast
"""
from __future__ import annotations
import os, sys
import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from RViT_plus_v11_part2_broadcast.env import ChangeDetectionEnv
from RViT_plus_v11_part2_broadcast.model import RViTPlusV11Part2BroadcastModel as Model
from RViT_plus_v11_part2_broadcast.tx_lstm_encoder import _MultFeedbackBlock, DualStreamEncoder
from RViT_plus_v11_part2_broadcast.ppo import PPOConfig, train

DEVICE = torch.device("cpu")
torch.manual_seed(0)


def test_film_form_qx_times_one_plus_qh():
    """Q/K/V are each a SEPARATE bottom-up (from X) and top-down (from H) projection,
    combined as Q_X ⊙ (1 + Q_H) — the FiLM gate."""
    b = _MultFeedbackBlock(64, 1, d_mem_in=128, drop=0.0)
    for nm in ("W_XQ", "W_XK", "W_XV", "W_HQ", "W_HK", "W_HV"):
        assert hasattr(b, nm), f"missing projection {nm}"
    # top-down projections are zero-initialised (identity gate)
    assert b.W_HQ.weight.abs().sum() == 0 and b.W_HQ.bias.abs().sum() == 0
    print("✓ FiLM form: separate Q_X(X) and Q_H(H); top-down zero-init (gate = 1 at init)")


def test_identity_init_feedback_off():
    """Zero-init top-down ⇒ (1 + W_H·H) = 1 ⇒ output is independent of the memory H at
    init (= plain self-attention over X)."""
    b = _MultFeedbackBlock(64, 1, d_mem_in=128, drop=0.0).eval()
    X = torch.randn(2, 100, 64)
    z0, _ = b(X, torch.zeros(2, 100, 128), residual=X)
    zB, _ = b(X, torch.randn(2, 100, 128) * 10, residual=X)
    assert torch.allclose(z0, zB, atol=1e-6), "FiLM feedback must be OFF at init"
    assert torch.isfinite(zB).all() and zB.abs().max() < 50
    print("✓ identity-init: feedback off at init → block == self-attention over X (no explosion)")


def test_topdown_trainable_engages():
    b = _MultFeedbackBlock(32, 1, d_mem_in=32, drop=0.0)
    X = torch.randn(4, 20, 32); H = torch.randn(4, 20, 32)
    z, _ = b(X, H, residual=X)
    z.pow(2).mean().backward()
    assert b.W_HQ.weight.grad is not None and b.W_HQ.weight.grad.abs().sum() > 0, \
        "top-down FiLM projection must receive gradient (feedback can engage)"
    print("✓ top-down FiLM projection is trainable (feedback engages with experience)")


def test_encoder_both_streams_read_both_memories_residual_X():
    enc = DualStreamEncoder(n_tokens=100, d_model=64, d_mem=64, n_heads=1, n_lstm=2)
    # both streams' top-down reads H = [H1‖H2] → in-dim = 2*d_mem
    assert enc.priority_block.W_HQ.in_features == 128 and enc.value_block.W_HQ.in_features == 128
    st = enc.init_states(2, device=DEVICE)
    (Hs, Cs), rec = enc.forward_step(torch.randn(2, 100, 64), st)
    assert len(Hs) == 2 and rec[0].shape == (2, 100, 64) and rec[1].shape == (2, 100, 64)
    print("✓ encoder: both streams read [H1‖H2] (residual X); rec=[Z_priority, Z_value]")


def test_split_readout_preserved():
    m = Model(d_model=64, d_mem=64, tx_heads=1, n_lstm=2, conv_channels=32, n_quantiles=8)
    out = m.rl_step(torch.randn(2, 3, 50, 50), m.init_states(2, device=DEVICE))
    assert out["actor_logits"].shape == (2, 2) and out["critic_q_dist"].shape == (2, 2, 8)
    seq = m.forward_rl_sequence(torch.randn(2, 29, 3, 50, 50))
    assert seq["actor_logits_seq"].shape == (2, 29, 2)
    print("✓ split readout preserved: actor←Z_priority, critic←Z_value")


def test_train_runs_stable():
    m = Model(d_model=64, d_mem=64, tx_heads=1, n_lstm=2, conv_channels=32, n_quantiles=8)
    hist = train(m, ChangeDetectionEnv(), n_iterations=2, episodes_per_iter=4,
                 cfg=PPOConfig(n_epochs=2, per_n_replay=2, buffer_capacity=16, burn_in_iters=1),
                 device=DEVICE, log_every=1, save_every=999)
    assert len(hist) == 2 and all(np.isfinite(h["loss_total"]) for h in hist)
    print("✓ ppo: 2-iter train runs, losses finite (no explosion)")


if __name__ == "__main__":
    tests = [test_film_form_qx_times_one_plus_qh, test_identity_init_feedback_off,
             test_topdown_trainable_engages, test_encoder_both_streams_read_both_memories_residual_X,
             test_split_readout_preserved, test_train_runs_stable]
    for t in tests:
        t()
    print(f"\nAll {len(tests)} v11_part2_broadcast (FiLM multiplicative self-attention) tests passed.")
