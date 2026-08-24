"""
Shape and identity-at-init tests for PRISM v2.

Validates: stem shapes, FiLM identity at init, multi-head decoder partition,
multi-head saliency shape, GRU shapes, inner-loop identity at init,
hierarchical readout output dim, end-to-end forward step + episode shapes,
parameter budget in expected window.
"""
from __future__ import annotations

import os
import sys

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from decoder import (  # noqa: E402
    MultiHeadFeatureDecoder, PixelDecoder,
    multi_head_saliency, pixel_saliency_map,
)
from film import HierarchicalFiLM  # noqa: E402
from losses import multi_head_pc_loss, predictive_coding_loss, quantile_huber_loss  # noqa: E402
from memory import (  # noqa: E402
    CrossLevelErrorPool, FastConvGRU, InnerWMLoop, SlowConvGRU, pool_cross_level_error,
)
from model import PrismV2Model  # noqa: E402
from readout import (  # noqa: E402
    ActorHead, CriticHead, HeadCompressionBackbone, HierarchicalDecisionReadout,
)
from stem import V1Stem, V2Stem  # noqa: E402


def _ok(name): print(f"  [OK] {name}")


def test_stems():
    s1 = V1Stem(in_channels=3, mid_channels=32, out_channels=64)
    s2 = V2Stem(in_channels=64, out_channels=128)
    for B in (1, 4):
        x = torch.randn(B, 3, 50, 50)
        v1 = s1(x); assert v1.shape == (B, 64, 12, 12), f"V1: {v1.shape}"
        v2 = s2(v1); assert v2.shape == (B, 128, 6, 6), f"V2: {v2.shape}"
    _ok("V1Stem (3,50,50)→(64,12,12), V2Stem (64,12,12)→(128,6,6)")


def test_film_identity():
    f = HierarchicalFiLM()
    Mf = torch.randn(4, 32, 12, 12)
    Ms = torch.randn(4, 64, 6, 6)
    V1 = torch.randn(4, 64, 12, 12)
    P1 = f(Mf, Ms, V1)
    assert P1.shape == V1.shape
    err = (P1 - V1).abs().max().item()
    # γ-bias=1, β-bias=0; small Gaussian conv weights → near-identity at init.
    assert err < 1e-1, f"FiLM not near-identity at init: {err}"
    _ok(f"HierarchicalFiLM near-identity at init: max|P-V|={err:.2e}")


def test_pixel_decoder_zero_init():
    d = PixelDecoder(memory_channels=32)
    M = torch.randn(4, 32, 12, 12)
    x_hat, x_hat_grid = d(M)
    assert x_hat.shape == (4, 3, 50, 50), f"x_hat shape: {x_hat.shape}"
    assert x_hat_grid.shape == (4, 3, 12, 12), f"x_hat_grid shape: {x_hat_grid.shape}"
    assert x_hat.abs().max().item() < 1e-3, "PixelDecoder x_hat not zero at init"
    assert x_hat_grid.abs().max().item() < 1e-3, "PixelDecoder x_hat_grid not zero at init"
    _ok("PixelDecoder zero-init: x̂(50×50) and x̂_grid(12×12) both < 1e-3")


def test_multi_head_decoder():
    d = MultiHeadFeatureDecoder(memory_channels=32, feature_channels=64, n_heads=4,
                                spatial_h=12, spatial_w=12)
    M = torch.randn(4, 32, 12, 12)
    out = d(M)
    assert out.shape == (4, 4, 16, 12, 12), f"got {out.shape}"
    # Zero-init on per-head output convs.
    assert out.abs().max().item() < 1e-3, "MultiHeadFeatureDecoder not zero at init"
    _ok(f"MultiHeadFeatureDecoder shape (B,K,C/K,H,W) = {tuple(out.shape)}, zero at init")


def test_multi_head_saliency():
    V = torch.randn(4, 64, 12, 12)
    V_hat = torch.zeros(4, 4, 16, 12, 12)
    E, S = multi_head_saliency(V, V_hat)
    assert E.shape == (4, 4, 16, 12, 12)
    assert S.shape == (4, 4, 12, 12)
    assert (S >= 0).all().item()
    _ok(f"multi_head_saliency: E {tuple(E.shape)}, S {tuple(S.shape)}, all S ≥ 0")


def test_fast_gru():
    gru = FastConvGRU(memory_channels=32, feature_channels=64, pixel_channels=3, n_heads=4)
    Mp = torch.randn(2, 32, 12, 12)
    P = torch.randn(2, 64, 12, 12)
    E_ph = torch.randn(2, 4, 16, 12, 12)
    S_ph = torch.rand(2, 4, 12, 12)
    E_pix = torch.randn(2, 3, 12, 12)
    M, u = gru(Mp, P, E_ph, S_ph, E_pix)
    assert M.shape == Mp.shape
    assert u.shape == Mp.shape
    _ok("FastConvGRU forward: M, u shapes correct")


def test_slow_gru():
    gru = SlowConvGRU(memory_channels=64, feature_channels=128, cross_in_channels=64, n_heads=4)
    Mp = torch.randn(2, 64, 6, 6)
    V2 = torch.randn(2, 128, 6, 6)
    E_ph = torch.randn(2, 4, 32, 6, 6)
    S_ph = torch.rand(2, 4, 6, 6)
    Ev1 = torch.randn(2, 64, 6, 6)
    M, u = gru(Mp, V2, E_ph, S_ph, Ev1)
    assert M.shape == Mp.shape
    assert u.shape == Mp.shape
    # Conservative bias: u_base ≈ σ(-3) ≈ 0.05; even with amplification u should be small.
    assert u.mean().item() < 0.3, f"SlowConvGRU u_t too large at init: {u.mean().item()}"
    _ok(f"SlowConvGRU forward: u_mean={u.mean().item():.3f} (conservative)")


def test_inner_loop_identity():
    inner = InnerWMLoop(memory_channels=32, feature_channels=64, n_heads=4, K=4)
    dec = MultiHeadFeatureDecoder(memory_channels=32, feature_channels=64, n_heads=4,
                                  spatial_h=12, spatial_w=12)
    M = torch.randn(2, 32, 12, 12)
    V = torch.randn(2, 64, 12, 12)
    M_after = inner(M, V, decoder=dec)
    err = (M_after - M).abs().max().item()
    assert err < 1e-6, f"InnerWMLoop should be identity at init; got {err}"
    _ok(f"InnerWMLoop identity at init: max|ΔM| = {err:.2e}")


def test_pool_cross_level_error():
    E_ph = torch.randn(2, 4, 16, 12, 12)
    pooled = pool_cross_level_error(E_ph, target_h=6, target_w=6)
    assert pooled.shape == (2, 64, 6, 6)
    _ok(f"pool_cross_level_error (legacy): (B,K,C/K,12,12)→(B,C,6,6) = {tuple(pooled.shape)}")


def test_learned_cross_level_pool():
    pool = CrossLevelErrorPool(cross_in_channels=64)
    E_ph = torch.randn(2, 4, 16, 12, 12)
    pooled = pool(E_ph)
    assert pooled.shape == (2, 64, 6, 6)
    # Init: uniform 1/4 kernel, so output should match unweighted average pool
    # of the flattened input at random init.
    expected = torch.nn.functional.adaptive_avg_pool2d(E_ph.reshape(2, 64, 12, 12), (6, 6))
    err = (pooled - expected).abs().max().item()
    assert err < 1e-5, f"CrossLevelErrorPool not mean-equivalent at init: max err {err}"
    _ok(f"CrossLevelErrorPool (learned): mean-equivalent at init, max err {err:.2e}")


def test_head_compression_backbone():
    bb = HeadCompressionBackbone(
        fast_memory_channels=32, slow_memory_channels=64,
        readout_dim=208, hidden_channels=32, output_dim=256,
    )
    Mf = torch.randn(2, 32, 12, 12)
    Ms = torch.randn(2, 64, 6, 6)
    s_readout = torch.randn(2, 208)
    out = bb(Mf, Ms, s_readout)
    assert out.shape == (2, 256), f"got {out.shape}"
    _ok(f"HeadCompressionBackbone: (M_fast, M_slow, s_readout) → (B, 256)")


def test_readout_shape():
    rd = HierarchicalDecisionReadout(
        fast_memory_channels=32, slow_memory_channels=64,
        decision_channels=8, n_heads_fast=4, n_heads_slow=4, coarse_grid_fast=2,
    )
    Mf = torch.randn(2, 32, 12, 12)
    Sf = torch.rand(2, 4, 12, 12)
    Ms = torch.randn(2, 64, 6, 6)
    Ss = torch.rand(2, 4, 6, 6)
    s = rd(Mf, Sf, Ms, Ss)
    assert s.shape == (2, rd.output_dim)
    expected = 8 + 4*8 + 4*8*4 + 8 + 4*8  # 8 + 32 + 128 + 8 + 32 = 208
    assert rd.output_dim == expected, f"output_dim={rd.output_dim}, expected {expected}"
    _ok(f"HierarchicalDecisionReadout: output_dim = {rd.output_dim}")


def test_critic_head_action_conditional_distributional():
    """CriticHead now outputs (B, n_actions, n_quantiles).

    Verifies:
      * forward shape is (B, |A|, N)
      * q_values is (B, |A|) and equals mean over quantile axis
      * state_value(q, logits) is (B,) and equals Σ π Q
      * state_value with detach_policy=True does NOT propagate gradient
        into the action_logits (the actor stays clean of value supervision)
    """
    n_actions, N = 3, 51
    cr = CriticHead(input_dim=256, hidden_dim=128, n_actions=n_actions, n_quantiles=N)
    s = torch.randn(4, 256)
    q_dist = cr(s)
    assert q_dist.shape == (4, n_actions, N), f"expected (4, {n_actions}, {N}), got {q_dist.shape}"

    q_vals = cr.q_values(s)
    assert q_vals.shape == (4, n_actions), f"q_values expected (4, {n_actions}), got {q_vals.shape}"
    assert torch.allclose(q_vals, q_dist.mean(dim=-1))

    # V(s) = Σ π Q. Logits with grad enabled to test the stop-gradient.
    logits = torch.randn(4, n_actions, requires_grad=True)
    v = CriticHead.state_value(q_vals.detach(), logits, detach_policy=True)
    assert v.shape == (4,), f"state_value expected (4,), got {v.shape}"
    # With detach_policy=True, the gradient of v wrt logits should be zero.
    g = torch.autograd.grad(v.sum(), logits, retain_graph=False, allow_unused=True)[0]
    if g is not None:
        # If autograd returns a tensor (because logits is in graph), it should be all zeros.
        assert torch.allclose(g, torch.zeros_like(g)), \
            "state_value(detach_policy=True) leaked gradient into actor logits"

    # Sanity: with detach_policy=False, V does carry gradient into logits.
    logits2 = torch.randn(4, n_actions, requires_grad=True)
    v2 = CriticHead.state_value(q_vals.detach(), logits2, detach_policy=False)
    g2 = torch.autograd.grad(v2.sum(), logits2)[0]
    assert g2.abs().sum() > 0, "state_value(detach_policy=False) should backprop into logits"

    _ok("CriticHead action-conditional distributional: shapes + state_value gradient routing OK")


def test_quantile_huber_loss():
    B, T, N = 4, 10, 51
    quantiles = torch.randn(B, T, N)
    targets   = torch.randn(B, T)
    mask      = torch.ones(B, T)
    loss = quantile_huber_loss(quantiles, targets, mask, kappa=1.0)
    assert loss.dim() == 0, "loss must be scalar"
    assert loss.item() >= 0.0, "quantile Huber loss must be non-negative"
    # Zero loss when all quantiles equal the target.
    q_exact = targets.unsqueeze(-1).expand(B, T, N)
    loss_zero = quantile_huber_loss(q_exact, targets, mask)
    assert loss_zero.item() < 1e-6, f"expected ~0 loss for exact prediction, got {loss_zero.item()}"
    # Masking: zeroing the mask should give zero loss.
    loss_masked = quantile_huber_loss(quantiles, targets, torch.zeros(B, T))
    assert loss_masked.item() == 0.0, "fully-masked loss should be 0"
    _ok("quantile_huber_loss: scalar, non-negative, zero at exact pred, zero under full mask")


def test_full_model_step():
    """forward_step now exposes the action-conditional distributional Q.

    Shapes:
      action_logits : (B, |A|)
      value         : (B,)              V(s) = Σ sg[π] Q
      q_values      : (B, |A|)          mean over quantiles
      q_dist        : (B, |A|, N)       distributional Q
    """
    m = PrismV2Model()
    Mf, Ms = m.init_memory(batch_size=2)
    x = torch.randn(2, 3, 50, 50)
    out = m.forward_step(x, Mf, Ms, return_aux=True)
    assert out.action_logits.shape == (2, 2)
    assert out.value.shape == (2,), f"value expected (2,), got {out.value.shape}"
    assert out.q_values.shape == (2, 2), f"q_values expected (2, 2), got {out.q_values.shape}"
    assert out.q_dist.shape == (2, 2, 51), f"q_dist expected (2, 2, 51), got {out.q_dist.shape}"
    # value should equal Σ π(a|s) Q(s,a) with the policy from action_logits.
    import torch.nn.functional as _F
    expected_v = (_F.softmax(out.action_logits, dim=-1).detach() * out.q_values.detach()).sum(dim=-1)
    assert torch.allclose(out.value.detach(), expected_v, atol=1e-5), \
        "value != Σ π Q (state_value contract violated)"
    assert out.M_fast_next.shape == (2, 32, 12, 12)
    assert out.M_slow_next.shape == (2, 64, 6, 6)
    assert out.S_V1_per_head.shape == (2, 4, 12, 12)
    assert out.S_V2_per_head.shape == (2, 4, 6, 6)
    assert out.S_V1_pix.shape == (2, 1, 12, 12)
    assert out.pc_loss.dim() == 0
    assert "V1" in out.aux and "V2" in out.aux
    _ok("PrismV2Model.forward_step: action-conditional Q shapes + V = Σ π Q")


def test_full_model_episode():
    m = PrismV2Model()
    x = torch.randn(2, 5, 3, 50, 50)
    ep = m.forward_episode(x)
    assert ep.action_logits.shape == (2, 5, 2)
    assert ep.values.shape == (2, 5), f"values expected (2, 5), got {ep.values.shape}"
    assert ep.q_values_seq.shape == (2, 5, 2), f"q_values_seq expected (2, 5, 2), got {ep.q_values_seq.shape}"
    assert ep.q_dist_seq.shape == (2, 5, 2, 51), f"q_dist_seq expected (2, 5, 2, 51), got {ep.q_dist_seq.shape}"
    assert ep.M_fast_seq.shape == (2, 6, 32, 12, 12)
    assert ep.M_slow_seq.shape == (2, 6, 64, 6, 6)
    assert ep.S_V1_per_head_seq.shape == (2, 5, 4, 12, 12)
    assert ep.S_V2_per_head_seq.shape == (2, 5, 4, 6, 6)
    assert ep.pc_loss_seq.shape == (5,)
    _ok("PrismV2Model.forward_episode: end-to-end shapes correct")


def test_param_count():
    m = PrismV2Model()
    counts = m.count_parameters()
    print(f"     Per-module: {counts}")
    # After learned-pool refactor + head-compression backbone, expect ~1.4–1.7M.
    assert 800_000 < counts["total"] < 2_500_000, f"total={counts['total']}"
    _ok(f"Parameter budget: {counts['total']:,} (expected ~1.4–1.7M after learned-pool + head backbone)")


def test_pc_grad_flow():
    m = PrismV2Model()
    Mf, Ms = m.init_memory(batch_size=2)
    x = torch.randn(2, 3, 50, 50)
    out = m.forward_step(x, Mf, Ms)
    out.pc_loss.backward()
    stem_grad = sum(p.grad.abs().sum().item() for p in m.stem_V1.parameters() if p.grad is not None)
    pix_grad  = sum(p.grad.abs().sum().item() for p in m.pixel_decoder.parameters() if p.grad is not None)
    v2_dec_grad = sum(p.grad.abs().sum().item() for p in m.feature_decoder_V2.parameters() if p.grad is not None)
    assert stem_grad > 0, "V1 stem received no gradient from L_PC"
    assert pix_grad > 0, "Pixel decoder received no gradient from L_PC"
    # V2 decoder gets gradient from autoencoding term (since M_slow depends on V2 via GRU).
    assert v2_dec_grad > 0, "V2 feature decoder received no gradient from L_PC"
    _ok("L_PC gradient reaches V1 stem, pixel decoder, V2 feature decoder")


def test_action_conditional_critic_grad_routing():
    """Action-conditional critic loss: gradient should be CONCENTRATED on the
    action-taken column of critic.fc2.weight.

    Setup:
      * Single timestep, batch B=8, action a_t = 1 for every example.
      * Loss = quantile_huber_loss(Q(s, a_t=1; ·), G_t).
      * Inspect critic.fc2.weight grad shape (n_actions·N_q, hidden):
        rows [:N_q] correspond to a=0, rows [N_q:2N_q] correspond to a=1.

    Assertion: ‖grad on a=1 rows‖ >> ‖grad on a=0 rows‖.
    The a=0 rows should get NO gradient because Q(s, a=0; ·) was never used
    in the loss (it's a different output slot of the same Linear layer).
    """
    import torch.nn.functional as _F
    from losses import quantile_huber_loss

    m = PrismV2Model()
    m.train()
    Mf, Ms = m.init_memory(batch_size=8)
    x = torch.randn(8, 3, 50, 50)
    out = m.forward_step(x, Mf, Ms)

    n_actions, N = m.n_actions, m.n_quantiles
    actions = torch.ones(8, 1, dtype=torch.long)               # all pick a=1

    # Gather Q(s, a_t=1; ·): shape (8, N).
    act_idx = actions.view(8, 1, 1).expand(8, 1, N)            # (8, 1, N)
    q_at = out.q_dist.gather(1, act_idx).squeeze(1)            # (8, N)

    # Single-step "GAE return" target.
    targets = torch.randn(8, 1)                                # (B, T=1) shape
    mask = torch.ones(8, 1)
    loss = quantile_huber_loss(q_at.unsqueeze(1), targets, mask, kappa=1.0)
    loss.backward()

    # critic.fc2.weight has shape (n_actions * n_quantiles, hidden_dim).
    # Output rows are organised as [a=0 quantiles | a=1 quantiles | ...].
    g = m.critic.fc2.weight.grad
    assert g is not None, "critic.fc2.weight got no grad"
    rows_a0 = g[0:N].abs().sum().item()
    rows_a1 = g[N:2 * N].abs().sum().item()
    assert rows_a1 > 1e-6, f"a=1 (taken) rows should have nonzero grad, got {rows_a1}"
    assert rows_a0 < 1e-9, (
        f"a=0 (not taken) rows should have ZERO grad on critic.fc2.weight; "
        f"got {rows_a0}. This means the action-conditional gating is broken."
    )
    _ok(
        f"Critic loss is action-conditional: grad on a_t=1 rows = {rows_a1:.3e}, "
        f"grad on a≠a_t rows = {rows_a0:.3e}"
    )


def main():
    print("PRISM v2 shape + identity tests:")
    test_stems()
    test_film_identity()
    test_pixel_decoder_zero_init()
    test_multi_head_decoder()
    test_multi_head_saliency()
    test_fast_gru()
    test_slow_gru()
    test_inner_loop_identity()
    test_pool_cross_level_error()
    test_learned_cross_level_pool()
    test_head_compression_backbone()
    test_readout_shape()
    test_critic_head_action_conditional_distributional()
    test_quantile_huber_loss()
    test_full_model_step()
    test_full_model_episode()
    test_param_count()
    test_pc_grad_flow()
    test_action_conditional_critic_grad_routing()
    print("\nAll PRISM v2 shape tests passed.")


if __name__ == "__main__":
    main()
