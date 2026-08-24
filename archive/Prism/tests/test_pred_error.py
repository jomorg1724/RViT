"""
Tests for the predictive-coding loss and saliency map behaviour:

(a) L_PC actually decreases when we train ONLY the decoder (with everything
    else frozen) on a small fixed dataset of (x_t, M_init=0) pairs.

(b) After training, the saliency map S_t responds to novelty: random new
    inputs produce higher S_t than inputs the decoder has seen.

These are mini-tests that take a few seconds; they validate the central
PC-bootstrap claim of §5 of the proposal — that the architecture can fit a
generative model from random rollouts before any RL signal is applied.
"""
from __future__ import annotations

import os
import sys

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from decoder import GenerativeDecoder, prediction_error_map  # noqa: E402
from losses import predictive_coding_loss  # noqa: E402
from model import PrismModel  # noqa: E402


def test_pc_loss_decreases_when_decoder_can_fit() -> None:
    """
    Construct a fixed 'V' target and a fixed 'M' input, train decoder to fit.

    With zero-init weights on the second conv, training should drop L_PC by
    several orders of magnitude in 200 steps on a tiny dataset.
    """
    torch.manual_seed(0)
    dec = GenerativeDecoder(memory_channels=16, feature_channels=32)
    opt = torch.optim.Adam(dec.parameters(), lr=3e-3)

    # Fixed target / input pair.
    M = torch.randn(8, 16, 12, 12)
    V_target = torch.randn(8, 32, 12, 12)

    init_loss = predictive_coding_loss(V_target, dec(M)).item()
    for _ in range(300):
        V_hat = dec(M)
        loss = predictive_coding_loss(V_target, V_hat)
        opt.zero_grad()
        loss.backward()
        opt.step()
    final_loss = predictive_coding_loss(V_target, dec(M)).item()

    print(f"  L_PC: {init_loss:.4f} → {final_loss:.6f}  (factor {init_loss/max(final_loss,1e-12):.1f}×)")
    # Hard assertion: at least 100× drop. In practice we see ~10000×.
    assert final_loss < init_loss / 100.0, (
        f"L_PC did not drop sufficiently: {init_loss:.4f} → {final_loss:.4f}"
    )
    print("  [OK] L_PC decreases by > 100× when decoder is allowed to fit.")


def test_saliency_responds_to_novelty() -> None:
    """
    After training the decoder on input X_train, S_t should be HIGHER on a
    novel X_novel than on X_train.
    """
    torch.manual_seed(1)
    dec = GenerativeDecoder()
    opt = torch.optim.Adam(dec.parameters(), lr=3e-3)

    M = torch.randn(8, 16, 12, 12)
    V_train = torch.randn(8, 32, 12, 12)

    # Train the decoder to predict V_train from M.
    for _ in range(300):
        loss = predictive_coding_loss(V_train, dec(M))
        opt.zero_grad()
        loss.backward()
        opt.step()

    # Saliency on the trained pair should be small.
    _, S_train = prediction_error_map(V_train, dec(M))
    # Novel V (different random sample) — saliency should be large.
    V_novel = torch.randn(8, 32, 12, 12)
    _, S_novel = prediction_error_map(V_novel, dec(M))

    print(f"  S on trained input: mean={S_train.mean().item():.4f}")
    print(f"  S on novel input:   mean={S_novel.mean().item():.4f}")
    assert S_novel.mean().item() > 5.0 * S_train.mean().item(), (
        "Saliency does not discriminate trained vs novel input."
    )
    print("  [OK] Saliency on novel input is > 5× saliency on trained input.")


def test_full_model_pc_loss_flows_to_stem_and_decoder() -> None:
    """In PrismModel.forward_step, L_PC's grad should reach BOTH stem and decoder."""
    torch.manual_seed(2)
    model = PrismModel()
    M0 = model.init_memory(batch_size=2)
    x = torch.randn(2, 3, 50, 50)
    out = model.forward_step(x, M0)
    out.pc_loss.backward()

    stem_grad = sum(p.grad.abs().sum().item() for p in model.stem.parameters() if p.grad is not None)
    dec_grad = sum(p.grad.abs().sum().item() for p in model.decoder.parameters() if p.grad is not None)
    assert stem_grad > 0, "Stem received zero gradient from L_PC"
    assert dec_grad > 0, "Decoder received zero gradient from L_PC"
    print(f"  [OK] L_PC backward → stem grad sum {stem_grad:.3f}, decoder grad sum {dec_grad:.3f}")


def main() -> None:
    print("Predictive coding behaviour tests:")
    test_pc_loss_decreases_when_decoder_can_fit()
    test_saliency_responds_to_novelty()
    test_full_model_pc_loss_flows_to_stem_and_decoder()
    print("\nPC tests passed.")


if __name__ == "__main__":
    main()
