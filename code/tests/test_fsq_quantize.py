from __future__ import annotations

import torch

from paper_encoder import fsq_quantize


def test_fsq_produces_discrete_levels():
    x = torch.linspace(-0.5, 1.5, steps=17).reshape(1, 1, 1, -1).requires_grad_(True)
    q = fsq_quantize(x, levels=5)
    # Every output coordinate must be exactly one of {0, 0.25, 0.5, 0.75, 1.0}.
    allowed = torch.tensor([0.0, 0.25, 0.5, 0.75, 1.0])
    for val in q.detach().flatten():
        assert (allowed - val).abs().min() < 1e-7
    assert q.shape == x.shape


def test_fsq_gradient_is_identity_through_ste():
    x = torch.tensor([[0.3, 0.7, 1.2, -0.1]], requires_grad=True)
    q = fsq_quantize(x, levels=5)
    q.sum().backward()
    # STE: identity gradient where 0 ≤ x ≤ 1; zero gradient outside (clamp kills it).
    expected = torch.tensor([[1.0, 1.0, 0.0, 0.0]])
    assert torch.equal(x.grad, expected)


def test_fsq_forward_is_rounded():
    x = torch.tensor([[0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]])
    q = fsq_quantize(x, levels=5)
    expected = torch.tensor([[0.0, 0.0, 0.25, 0.5, 0.75, 1.0, 1.0]])
    assert torch.allclose(q, expected, atol=1e-7)


def test_fsq_two_levels_is_binary():
    x = torch.tensor([[0.2, 0.4, 0.6, 0.8]])
    q = fsq_quantize(x, levels=2)
    expected = torch.tensor([[0.0, 0.0, 1.0, 1.0]])
    assert torch.allclose(q, expected, atol=1e-7)


def test_fsq_levels_one_passthrough():
    x = torch.tensor([[0.3, 0.7]])
    q = fsq_quantize(x, levels=1)
    assert torch.equal(q, x)


def test_fsq_invalid_levels_raises():
    x = torch.tensor([[0.5]])
    try:
        fsq_quantize(x, levels=0)
        assert False, "should have raised"
    except ValueError:
        pass
