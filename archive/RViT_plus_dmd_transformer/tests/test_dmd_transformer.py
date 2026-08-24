"""Smoke tests for the DMD transformer variant."""
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

from model import DMDTransformerModel  # noqa: E402


def test_dmd_frontend_and_rl_contract():
    model = DMDTransformerModel(seq_len=7)
    x = torch.randn(2, 3, 50, 50)
    s = model.init_states(2)
    out = model.rl_step(x, s)
    assert out["actor_logits"].shape == (2, 2)
    assert out["critic_q_dist"].shape == (2, 2, 5)
    assert out["rec"].shape == (2, 256)
    assert out["dmd_tokens"].shape == (2, 5, 256)


def test_sequence_contract():
    model = DMDTransformerModel(seq_len=7)
    video = torch.randn(2, 7, 3, 50, 50)
    out = model.forward_rl_sequence(video)
    assert out["actor_logits_seq"].shape == (2, 7, 2)
    assert out["q_dist_seq"].shape == (2, 7, 2, 5)
    assert out["dmd_token_seq"].shape == (2, 7, 5, 256)


def test_mps_contract_if_available():
    if not torch.backends.mps.is_available():
        return
    model = DMDTransformerModel(seq_len=7).to("mps")
    x = torch.randn(1, 3, 50, 50, device="mps")
    s = model.init_states(1, device=torch.device("mps"))
    out = model.rl_step(x, s)
    assert out["actor_logits"].device.type == "mps"
    assert out["dmd_tokens"].shape == (1, 5, 256)
