"""Smoke tests for affine2lstm JEPA variant."""
from __future__ import annotations

import copy
import os
import sys

import torch

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PAPER = os.path.join(os.path.dirname(_ROOT), "RViT_plus_paper")
for p in (_PAPER, _ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from model import Affine2LSTMJEPAModel, sequential_jepa_loss  # noqa: E402


def test_conv_frontend_and_rl_contract():
    model = Affine2LSTMJEPAModel(seq_len=7)
    x = torch.randn(2, 3, 50, 50)
    X = model.front(x, 1)
    assert X.shape == (2, 16, 140)
    s = model.init_states(2)
    out = model.rl_step(x, s, return_attn=True)
    assert out["actor_logits"].shape == (2, 2)
    assert out["critic_q_dist"].shape == (2, 2, 5)
    assert out["h2"].shape == (2, 16, 1024)
    assert out["attn"][0].shape == (2, 16, 16)


def test_sequence_outputs_and_jepa_loss():
    model = Affine2LSTMJEPAModel(seq_len=7)
    teacher = copy.deepcopy(model)
    video = torch.randn(2, 7, 3, 50, 50)
    out = model.forward_rl_sequence(video)
    with torch.no_grad():
        tout = teacher.forward_rl_sequence(video)
    valid = torch.ones(2, 7)
    loss = sequential_jepa_loss(model, teacher, out, tout, valid)
    assert out["h2_seq"].shape == (2, 7, 16, 1024)
    assert torch.isfinite(loss)
