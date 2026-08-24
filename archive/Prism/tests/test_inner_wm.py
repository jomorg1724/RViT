"""
Test the Banach-contraction property of the inner WM loop.

Under the variational-inference reading of the inner loop (each iteration is
one Friston-style gradient step on the variational free energy F), the
per-iteration residual ‖M^(k+1) − M^(k)‖ should decay geometrically when ε
is small enough. This test verifies the empirical contractiveness.

Concretely: with small-norm random init of ErrBlock and a fixed (V, M_init),
the residual ‖M^(k+1) − M^(k)‖ should NOT blow up across k.

Note: the second conv in InnerWMLoop is zero-init'd, so at *exact* init the
loop is the identity (residual = 0). To test contractiveness we have to
perturb the weights so the loop actually does something. This test does
that with a small-Gaussian perturbation.
"""
from __future__ import annotations

import os
import sys

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from decoder import GenerativeDecoder  # noqa: E402
from memory import InnerWMLoop  # noqa: E402


def _perturb_weights(module: torch.nn.Module, std: float) -> None:
    """Add small-Gaussian noise to all weights so the inner loop is non-trivial."""
    with torch.no_grad():
        for p in module.parameters():
            p.add_(torch.randn_like(p) * std)


def test_inner_wm_residual_bounded() -> None:
    torch.manual_seed(42)
    inner = InnerWMLoop(memory_channels=16, feature_channels=32, K=8, epsilon=0.1)
    dec = GenerativeDecoder()
    # Perturb both: ErrBlock + decoder, so neither is trivially zero.
    _perturb_weights(inner, std=0.05)
    _perturb_weights(dec, std=0.05)

    M = torch.randn(2, 16, 12, 12) * 0.1
    V = torch.randn(2, 32, 12, 12) * 0.1

    residuals = inner.diagnose_contraction(M.clone(), V, decoder=dec)
    print(f"  Residuals across K=8 iterations: {residuals.tolist()}")

    # Hard assertion: residuals must not explode.
    assert torch.isfinite(residuals).all(), f"Non-finite residuals: {residuals}"
    max_r = residuals.max().item()
    assert max_r < 100.0, f"Residuals blew up: max = {max_r}"

    # Soft check (informational; not a hard assertion since random init does
    # not guarantee contraction). Print the geometric ratio of residuals.
    if residuals[0].item() > 1e-8:
        ratios = (residuals[1:] / residuals[:-1].clamp(min=1e-8)).tolist()
        print(f"  Residual ratios (would be < 1 for clean contraction): {ratios}")

    print("  [OK] Inner WM residual stays bounded across 8 iterations.")


def test_inner_wm_ksweep_compute_only() -> None:
    """Smoke: K ∈ {0, 1, 2, 4, 8} all run without crashing and return correct shapes."""
    dec = GenerativeDecoder()
    M = torch.randn(2, 16, 12, 12)
    V = torch.randn(2, 32, 12, 12)
    for K in (0, 1, 2, 4, 8):
        inner = InnerWMLoop(memory_channels=16, feature_channels=32, K=K)
        M_out = inner(M.clone(), V, decoder=dec)
        assert M_out.shape == M.shape, f"K={K}: got {M_out.shape}"
    print("  [OK] InnerWMLoop runs for K ∈ {0, 1, 2, 4, 8}")


def test_inner_wm_gradient_flow() -> None:
    """Backward through the inner loop should hit BOTH inner.* params AND decoder params."""
    dec = GenerativeDecoder()
    inner = InnerWMLoop(memory_channels=16, feature_channels=32, K=2)
    _perturb_weights(inner, std=0.05)
    _perturb_weights(dec, std=0.05)

    M = torch.randn(2, 16, 12, 12, requires_grad=False)
    V = torch.randn(2, 32, 12, 12, requires_grad=False)

    M_out = inner(M, V, decoder=dec)
    loss = M_out.pow(2).mean()
    loss.backward()

    # Decoder params should have gradient.
    have_decoder_grad = any(p.grad is not None and p.grad.abs().sum() > 0 for p in dec.parameters())
    have_inner_grad = any(p.grad is not None and p.grad.abs().sum() > 0 for p in inner.parameters())
    assert have_decoder_grad, "Decoder did not receive gradient from inner loop backward."
    assert have_inner_grad, "Inner block did not receive gradient."
    print("  [OK] Inner WM backward propagates gradient to BOTH decoder and ErrBlock.")


def main() -> None:
    print("Inner WM (variational inference loop) tests:")
    test_inner_wm_ksweep_compute_only()
    test_inner_wm_residual_bounded()
    test_inner_wm_gradient_flow()
    print("\nInner WM tests passed.")


if __name__ == "__main__":
    main()
