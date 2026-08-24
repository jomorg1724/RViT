"""Smoke tests for affine + dual-xLSTM variant."""
from __future__ import annotations

import os
import sys

import torch

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PAPER = os.path.join(os.path.dirname(_ROOT), "RViT_plus_paper")
for p in (_ROOT, _PAPER):
    if p not in sys.path:
        sys.path.insert(0, p)

from model import RViTPaperModel  # noqa: E402
from paper_encoder import AffineModulatedSelfAttention, RecurrentViTxLSTM  # noqa: E402


def test_affine_two_lstm_encoder():
    enc = RecurrentViTxLSTM(feedback="affine", two_lstm=True)
    assert enc.two_lstm and enc.lstm2_from == "H1"
    assert isinstance(enc.attn, AffineModulatedSelfAttention)
    s = enc.init_states(2)
    assert len(s) == 2  # (LSTM1 state, LSTM2 state)
    X = torch.randn(2, 4, 140)
    new_s, H2, attn = enc.forward_step(X, s, return_attn=True)
    assert H2.shape == (2, 4, 1024)
    assert attn.shape == (2, 4, 4)


def test_model_rl_contract():
    m = RViTPaperModel(feedback="affine", two_lstm=True, n_quantiles=5, seq_len=7)
    assert m.feedback == "affine" and m.two_lstm and m.enc_layers == 2
    s = m.init_states(2)
    out = m.rl_step(torch.randn(2, 3, 50, 50), s, return_attn=True)
    assert out["actor_logits"].shape == (2, 2)
    assert out["attn"] is not None


def test_affine_modulation_hook():
    attn = AffineModulatedSelfAttention()
    X = torch.randn(1, 4, 140)
    H = torch.randn(1, 4, 1024)
    Z, aw, mod = attn(X, H, return_attn=True, return_modulation=True)
    assert mod["Xp"].shape == X.shape
    assert mod["beta"].shape == X.shape
    aw_raw = attn.attention_on(X)
    assert aw_raw.shape == aw.shape
