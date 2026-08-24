"""
Shape tests for every PRISM module.

Per the proposal's "Verification suggestions":
    1. Stem shape: (B, 3, 50, 50) -> (B, 32, 12, 12)
    2. FiLM identity at init
    3. Decoder ≈ 0 at init
    4. Saliency map ≥ 0
    5. ConvGRU identity at init with extreme bias
    6. Inner WM is contractive at small init
    7. PC loss decreases on a fixed dataset (separate test, slower)
"""
from __future__ import annotations

import os
import sys

import torch

# Add Prism root to path so `import stem`, `import model` etc. work.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from decoder import GenerativeDecoder, prediction_error_map  # noqa: E402
from film import FiLM  # noqa: E402
from losses import predictive_coding_loss, slowness_loss  # noqa: E402
from memory import ErrorGatedConvGRU, InnerWMLoop  # noqa: E402
from model import PrismModel  # noqa: E402
from readout import ActorHead, CriticHead, DecisionReadout  # noqa: E402
from stem import V1Stem  # noqa: E402


def _ok(name: str) -> None:
    print(f"  [OK] {name}")


def test_stem_shape() -> None:
    """V1Stem: (B, 3, 50, 50) -> (B, 32, 12, 12)."""
    stem = V1Stem()
    for B in (1, 4, 32):
        x = torch.randn(B, 3, 50, 50)
        v = stem(x)
        assert v.shape == (B, 32, 12, 12), f"Got {v.shape}"
    _ok("V1Stem shape (B, 3, 50, 50) -> (B, 32, 12, 12)")


def test_film_identity_at_init() -> None:
    """With small-init FiLM and random M, P_t ≈ V_t (γ ≈ 1, β ≈ 0)."""
    film = FiLM(memory_channels=16, feature_channels=32, init_weight_std=1e-4)
    M = torch.randn(4, 16, 12, 12)
    V = torch.randn(4, 32, 12, 12)
    P = film(M, V)
    err = (P - V).abs().max().item()
    # Bound: |P - V| ≤ |γ - 1| · |V| + |β|. With γ - 1 ~ N(0, 1e-4) and β ~ N(0, 1e-4),
    # both random over a 16-wide sum, the error is roughly 4×|V|·1e-4 + 1e-4 ≈ 1e-3.
    assert err < 1e-2, f"FiLM not near-identity at init: max |P-V| = {err}"
    _ok(f"FiLM identity-at-init: max|P-V|={err:.2e} (< 1e-2)")


def test_decoder_near_zero_at_init() -> None:
    """Decoder is zero-init'd on its output conv → V̂ ≈ 0."""
    dec = GenerativeDecoder()
    M = torch.randn(4, 16, 12, 12)
    V_hat = dec(M)
    assert V_hat.shape == (4, 32, 12, 12)
    max_v = V_hat.abs().max().item()
    assert max_v < 1e-3, f"Decoder not near-zero at init: max|V̂| = {max_v}"
    _ok(f"Decoder near-zero-at-init: max|V̂|={max_v:.2e} (< 1e-3)")


def test_saliency_nonnegative() -> None:
    """S_t = sqrt(mean(E²) + eps) is ≥ 0 by construction; sanity-check."""
    V = torch.randn(4, 32, 12, 12)
    V_hat = torch.randn(4, 32, 12, 12)
    E, S = prediction_error_map(V, V_hat)
    assert E.shape == V.shape
    assert S.shape == (4, 1, 12, 12)
    assert (S >= 0).all().item(), "Saliency must be non-negative"
    # When V == V_hat exactly, S should be ~ sqrt(eps) (≈ 1e-3).
    E0, S0 = prediction_error_map(V, V.clone())
    assert E0.abs().max().item() < 1e-7
    assert S0.max().item() < 1e-2
    _ok("Saliency non-negative; equal-input → near-zero saliency")


def test_gru_identity_at_extreme_negative_bias() -> None:
    """Force u_t^base ≈ 0 by overriding bias → M_t should ≈ M_prev."""
    gru = ErrorGatedConvGRU(memory_channels=16, feature_channels=32)
    # Override the update-gate bias to a very negative value: σ(−20) ≈ 2e-9.
    with torch.no_grad():
        gru.u_conv.bias.fill_(-20.0)
        # Also zero λ_tilde so the error amplification is small.
        gru.lambda_tilde.fill_(-10.0)  # softplus(-10) ≈ 4.5e-5

    M_prev = torch.randn(4, 16, 12, 12)
    P = torch.randn(4, 32, 12, 12)
    E = torch.randn(4, 32, 12, 12)
    S = E.pow(2).mean(dim=1, keepdim=True).sqrt()

    M_next, u = gru(M_prev, P, E, S)
    assert M_next.shape == M_prev.shape
    err = (M_next - M_prev).abs().max().item()
    assert err < 1e-3, f"With u_base ≈ 0 and λ ≈ 0, expected M_next ≈ M_prev; got max err {err}"
    _ok(f"GRU identity at u_bias=-20, λ̃=-10: max|M_next - M_prev|={err:.2e}")


def test_inner_wm_identity_at_init() -> None:
    """InnerWMLoop's second conv is zero-init → no update at init."""
    inner = InnerWMLoop(memory_channels=16, feature_channels=32, K=4)
    dec = GenerativeDecoder()
    M = torch.randn(4, 16, 12, 12)
    V = torch.randn(4, 32, 12, 12)
    M_after = inner(M, V, decoder=dec)
    assert M_after.shape == M.shape
    err = (M_after - M).abs().max().item()
    assert err < 1e-6, f"Inner WM should be identity at init; got max err {err}"
    _ok(f"InnerWMLoop identity at init: max|ΔM|={err:.2e}")


def test_decision_readout_shape() -> None:
    rd = DecisionReadout()
    M = torch.randn(4, 16, 12, 12)
    S = torch.rand(4, 1, 12, 12)  # ≥ 0
    s = rd(M, S)
    assert s.shape == (4, 8), f"Got {s.shape}"
    _ok("DecisionReadout: (M, S) → s_t of shape (B, 8)")


def test_actor_critic_shapes() -> None:
    actor = ActorHead(input_dim=8, n_actions=2)
    critic = CriticHead(input_dim=8)
    s = torch.randn(4, 8)
    logits = actor(s)
    value = critic(s)
    assert logits.shape == (4, 2)
    assert value.shape == (4,)
    _ok("Actor → (B, n_actions); Critic → (B,)")


def test_full_model_step() -> None:
    model = PrismModel()
    M0 = model.init_memory(batch_size=4)
    x = torch.randn(4, 3, 50, 50)
    out = model.forward_step(x, M0, return_aux=True)
    assert out.action_logits.shape == (4, 2)
    assert out.value.shape == (4,)
    assert out.M_next.shape == M0.shape
    assert out.saliency.shape == (4, 1, 12, 12)
    assert out.pc_loss.dim() == 0  # scalar
    assert "V_t" in out.aux
    _ok("PrismModel.forward_step: end-to-end shapes")


def test_full_model_episode() -> None:
    model = PrismModel()
    x_seq = torch.randn(2, 5, 3, 50, 50)
    ep = model.forward_episode(x_seq)
    assert ep.action_logits.shape == (2, 5, 2)
    assert ep.values.shape == (2, 5)
    assert ep.M_seq.shape == (2, 6, 16, 12, 12)  # T+1
    assert ep.saliency_seq.shape == (2, 5, 1, 12, 12)
    assert ep.pc_loss_seq.shape == (5,)
    _ok("PrismModel.forward_episode: end-to-end shapes")


def test_param_count_matches_proposal() -> None:
    """Sanity-check that the parameter count is in the ~50–60K ballpark from §7."""
    model = PrismModel()
    counts = model.count_parameters()
    print(f"     Per-module: {counts}")
    assert 40_000 < counts["total"] < 80_000, (
        f"Total params {counts['total']} outside expected ~50–60K window"
    )
    _ok(f"Parameter budget: {counts['total']:,} total (expected ~50–60K)")


def test_pc_loss_basics() -> None:
    """L_PC is a scalar, ≥ 0, and 0 iff V == V̂."""
    V = torch.randn(4, 32, 12, 12)
    L0 = predictive_coding_loss(V, V.clone())
    assert L0.dim() == 0
    assert L0.item() < 1e-10
    Lpos = predictive_coding_loss(V, torch.zeros_like(V))
    assert Lpos.item() > 0
    _ok(f"L_PC: scalar; equal=0 ({L0.item():.2e}); zero-pred>0 ({Lpos.item():.3f})")


def test_slowness_loss_basics() -> None:
    M = torch.randn(4, 16, 12, 12)
    L0 = slowness_loss(M, M.clone())
    assert L0.item() < 1e-10
    L1 = slowness_loss(M, torch.zeros_like(M))
    assert L1.item() > 0
    _ok(f"L_slow: scalar; identical=0; nonidentical>0 ({L1.item():.3f})")


def main() -> None:
    print("Running shape and identity tests:")
    test_stem_shape()
    test_film_identity_at_init()
    test_decoder_near_zero_at_init()
    test_saliency_nonnegative()
    test_gru_identity_at_extreme_negative_bias()
    test_inner_wm_identity_at_init()
    test_decision_readout_shape()
    test_actor_critic_shapes()
    test_full_model_step()
    test_full_model_episode()
    test_param_count_matches_proposal()
    test_pc_loss_basics()
    test_slowness_loss_basics()
    print("\nAll shape tests passed.")


if __name__ == "__main__":
    main()
