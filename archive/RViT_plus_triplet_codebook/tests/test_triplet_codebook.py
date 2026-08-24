"""Smoke tests for triplet-codebook variant."""
from __future__ import annotations

import os
import sys

import torch

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PAPER = os.path.join(os.path.dirname(_ROOT), "RViT_plus_paper")
for p in (_PAPER, _ROOT):
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)

from model import TripletCodebookModel  # noqa: E402
from ppo import PPOConfig, codebook_contrastive_loss  # noqa: E402


def test_frontend_attention_and_rl_contract():
    model = TripletCodebookModel(seq_len=7)
    x = torch.randn(2, 3, 50, 50)
    X = model.front(x, 1)
    assert X.shape == (2, 16, 140)
    s = model.init_states(2)
    out = model.rl_step(x, s, return_attn=True)
    assert out["actor_logits"].shape == (2, 2)
    assert out["critic_q_dist"].shape == (2, 2, 5)
    assert out["codebook_z"].shape == (2, 16, 140)
    assert out["attn"][0].shape == (2, 16, 48)


def test_sequence_contract():
    model = TripletCodebookModel(seq_len=7)
    video = torch.randn(2, 7, 3, 50, 50)
    out = model.forward_rl_sequence(video, return_attn=True)
    assert out["actor_logits_seq"].shape == (2, 7, 2)
    assert out["q_dist_seq"].shape == (2, 7, 2, 5)
    assert out["codebook_z_seq"].shape == (2, 7, 16, 140)
    assert out["attn_seq"].shape == (2, 7, 16, 48)


def test_codebook_regularizer_contract():
    model = TripletCodebookModel(seq_len=7)
    loss, stats = codebook_contrastive_loss(model, PPOConfig())
    assert torch.isfinite(loss)
    assert stats["loss_codebook_inter"] >= 0.0
    assert stats["loss_codebook_intra"] >= 0.0
    assert stats["codebook_mean_norm"] > 0.0
