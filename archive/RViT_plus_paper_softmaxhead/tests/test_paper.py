"""Equation-faithfulness tests for the exact paper Recurrent ViT."""
from __future__ import annotations

import os
import sys

import torch

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from vae_frontend import VAEPatchFrontEnd, TOKEN_DIM, O_FLAT2, POS_DIM      # noqa: E402
from paper_encoder import MultiplicativeSelfAttention, SpatialXLSTM, RecurrentViTxLSTM  # noqa: E402
from model import RViTPaperModel                                            # noqa: E402


def test_frontend_token_shape_and_encodings():
    fe = VAEPatchFrontEnd()
    x = torch.randn(2, 3, 50, 50)
    X = fe(x, t=3)
    assert X.shape == (2, 4, TOKEN_DIM) == (2, 4, 140)
    # positional one-hot block is the 4x4 identity per batch
    pos = X[0, :, O_FLAT2:O_FLAT2 + POS_DIM]
    assert torch.allclose(pos, torch.eye(4))
    # temporal one-hot has a single 1 at index t (=3)
    tau = X[0, 0, O_FLAT2 + POS_DIM:]
    assert tau.argmax().item() == 3 and tau.sum().item() == 1.0


def test_vit_multiplicative_gate_off_when_memory_zero():
    """Pure Hadamard gate: H=0 ⇒ Q=K=V=0 ⇒ V_filtered=0 ⇒ Z=X (Eq 620)."""
    sa = MultiplicativeSelfAttention()
    X = torch.randn(2, 4, 140)
    H0 = torch.zeros(2, 4, 1024)
    Z, attn = sa(X, H0, return_attn=True)
    assert torch.allclose(Z, X, atol=1e-6)            # Z = X when memory is empty
    assert attn.shape == (2, 4, 4)
    # with nonzero memory the gate engages → Z deviates from X
    Z2, _ = sa(X, torch.randn(2, 4, 1024))
    assert not torch.allclose(Z2, X, atol=1e-4)


def test_xlstm_shapes_and_init_reduces_to_O_times_U():
    """At the pre-initial state (C=N=M=0): N=I, C=U⊙I ⇒ H = O⊙(U⊙I / I) = O⊙U."""
    lstm = SpatialXLSTM()
    Z = torch.randn(2, 4, 140)
    z = torch.zeros(2, 4, 1024)
    H, C, N, M = lstm(Z, z, z, z, z)
    for t in (H, C, N, M):
        assert t.shape == (2, 4, 1024) and torch.isfinite(t).all()
    # reconstruct O⊙U from the gate pre-activations and compare
    O = torch.sigmoid(lstm.W_o(Z) + lstm.R_o(z))
    U = torch.tanh(lstm.W_u(Z) + lstm.R_z(z))
    assert torch.allclose(H, O * U, atol=1e-5)


def test_model_rl_step_and_sequence_contract():
    m = RViTPaperModel(n_quantiles=5)
    assert m.n_tokens == 4 and m.n_quantiles == 5
    s = m.init_states(2)
    out = m.rl_step(torch.randn(2, 3, 50, 50), s)
    assert out["actor_logits"].shape == (2, 2)
    assert out["critic_q_dist"].shape == (2, 2, 5)
    assert out["V_dist"].shape == (2, 5) and out["V_scalar"].shape == (2,)
    # sequence path (B,T,50,50,3) channels-last, as the harness stores observations
    vid = torch.randn(2, 7, 50, 50, 3)
    so = m.forward_rl_sequence(vid)
    assert so["actor_logits_seq"].shape == (2, 7, 2)
    assert so["q_dist_seq"].shape == (2, 7, 2, 5)
    assert so["V_dist_seq"].shape == (2, 7, 5)


def test_init_action_bias_applied():
    m = RViTPaperModel(init_action_bias=[0.0, -1.5])
    assert torch.allclose(m.actor_head.out.bias.detach(), torch.tensor([0.0, -1.5]))


def test_ema_config_field_exists():
    from ppo import PPOConfig
    c = PPOConfig(ema_decay=0.995, target_update_period=0)
    assert c.ema_decay == 0.995 and c.target_update_period == 0


def test_affine_cascade_two_transformers_split_readout():
    """affine_cascade: T1(X,fb=H1)->Z1->H1 ; T2(Z1,fb=H2)->Z2->H2 ; actor<-H2, critic<-H1.
    Two affine transformers + two xLSTMs, TWO attention maps, and the critic readout (H1)
    is structurally independent of the second stage (a critic-only gradient cannot reach
    attn2/lstm2)."""
    m = RViTPaperModel(n_quantiles=5, seq_len=7, feedback="affine_cascade")
    assert hasattr(m.encoder, "attn2") and hasattr(m.encoder, "lstm2") and m.encoder.two_lstm
    s = m.init_states(2)
    assert isinstance(s[0], tuple) and len(s[0]) == 2          # two-LSTM state
    out = m.rl_step(torch.randn(2, 3, 50, 50), s, return_attn=True)
    assert out["actor_logits"].shape == (2, 2)
    assert out["critic_q_dist"].shape == (2, 2, 5)
    assert len(out["attn"][0]) == 2                            # two affine maps (T1, T2)
    assert all(a.shape == (2, 4, 4) for a in out["attn"][0])

    def gnorm(mod):
        return sum(p.grad.abs().sum().item() for p in mod.parameters() if p.grad is not None)

    vid = torch.randn(2, 7, 3, 50, 50)
    m.zero_grad(set_to_none=True)
    m.forward_rl_sequence(vid)["q_dist_seq"].sum().backward()
    assert gnorm(m.encoder.attn2) == 0.0 and gnorm(m.encoder.lstm2) == 0.0   # critic H1 ⟂ stage 2
    assert gnorm(m.encoder.lstm) > 0.0                                       # but drives stage 1
    m.zero_grad(set_to_none=True)
    m.forward_rl_sequence(vid)["actor_logits_seq"].sum().backward()
    assert gnorm(m.encoder.lstm2) > 0.0 and gnorm(m.encoder.attn2) > 0.0     # actor H2 uses stage 2
