"""Per-step change classifier aux: head identical to supervised, decoded every step."""
from __future__ import annotations

import torch

from kda_rl_model import KDARLModel
from ppo import per_step_change_labels


def test_labels_change_trial():
    # change at logical 5, T=7: 0 until the change frame, 1 from there on
    assert per_step_change_labels(1, 5, 7) == [0, 0, 0, 0, 0, 1, 1]


def test_labels_no_change_trial():
    assert per_step_change_labels(0, 5, 7) == [0] * 7


def test_labels_frame_repeat():
    # frame_repeat=2, change at logical 3: physical steps 6,7 are >= change
    assert per_step_change_labels(1, 3, 8, frame_repeat=2) == [0] * 6 + [1, 1]


def test_change_logits_every_step_shape_and_head():
    model = KDARLModel(n_channels=8, map_size=4, proto_dim=16,
                       kda_heads=2, kda_head_dim=4, attn_mode="token")
    # identical to the supervised classifier: a single Linear(4C, 2) on pooled R
    assert isinstance(model.change_head, torch.nn.Linear)
    assert model.change_head.in_features == 4 * 8
    assert model.change_head.out_features == 2
    cell_seq = torch.randn(3, 7, 4 * 8, 4, 4)
    logits = model.change_logits_seq(cell_seq)
    assert logits.shape == (3, 7, 2)
    ref = model.change_head(cell_seq.mean(dim=(3, 4)))
    assert torch.allclose(logits, ref)


def test_change_ce_backward_reaches_trunk():
    model = KDARLModel(n_channels=8, map_size=4, proto_dim=16,
                       kda_heads=2, kda_head_dim=4, attn_mode="token")
    x = torch.randn(2, 7, 50, 50, 3)
    out = model.forward_rl_sequence(x, return_cell=True, inject_memory_noise=False)
    logits = model.change_logits_seq(out["cell_seq"])           # (B,T,2)
    labels = torch.tensor([per_step_change_labels(1, 5, 7),
                           per_step_change_labels(0, 5, 7)])
    ce = torch.nn.functional.cross_entropy(
        logits.reshape(-1, 2), labels.reshape(-1).long())
    assert torch.isfinite(ce)
    ce.backward()
    g = next(model.backbone.stem.parameters()).grad
    assert g is not None and torch.isfinite(g).all() and g.abs().max() > 0
