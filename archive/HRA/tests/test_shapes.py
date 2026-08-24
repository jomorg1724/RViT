"""
Stage 0 gate: scaffold shape tests.

Verifies that every module produces tensors of the expected shape and that
the full HRAModel.forward_step wires the pieces together correctly. Does not
check learning, gradient flow, or convergence — those come in later stages.

Run:
    cd /Users/jonathanmorgan/AttentionManuscript
    python3 HRA/tests/test_shapes.py
"""
from __future__ import annotations

import os
import sys
import traceback

import torch

# Allow running this file as a script from anywhere by ensuring the project
# root (parent of HRA/) is on sys.path.
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from HRA.attention import FeedbackTransformer
from HRA.decoder import FeatureDecoder, PixelDecoder
from HRA.losses import predictive_coding_loss, quantile_huber_loss
from HRA.memory import GridCellRNNCell
from HRA.model import HRAModel
from HRA.readout import ActorHead, CriticHead, DecisionReadout, DistributionalQHead
from HRA.stem import V1Stem


# --- Assertion helpers --------------------------------------------------------


_PASSED = 0
_FAILED = 0


def _check(name: str, condition: bool, detail: str = "") -> None:
    global _PASSED, _FAILED
    if condition:
        _PASSED += 1
        print(f"  PASS  {name}")
    else:
        _FAILED += 1
        msg = f"  FAIL  {name}"
        if detail:
            msg += f"  ({detail})"
        print(msg)


# --- Per-module tests ---------------------------------------------------------


def test_stem() -> None:
    print("\n[1] V1Stem ---")
    stem = V1Stem(in_channels=3, mid_channels=16, out_channels=32)
    x = torch.randn(2, 3, 50, 50)
    V = stem(x)
    _check("V1Stem output shape (B, 32, 12, 12)", tuple(V.shape) == (2, 32, 12, 12),
           detail=str(tuple(V.shape)))


def test_attention() -> None:
    print("\n[2] FeedbackTransformer ---")
    B, N, D = 2, 144, 32  # 12*12 grid, 32-dim
    ft = FeedbackTransformer(d_model=D, n_heads=4, n_feedback=2)

    sensory = torch.randn(B, N, D)
    fb_a = torch.randn(B, N, D)
    fb_b = torch.randn(B, N, D)

    # With no feedback (None).
    out = ft(sensory, feedback_list=None)
    _check("FT.out shape", tuple(out["out"].shape) == (B, N, D))
    _check("FT.attn shape", tuple(out["attn"].shape) == (B, 4, N, N))
    _check("FT no-feedback reduces to identity gates",
           torch.allclose(out["q_gate"], torch.ones_like(out["q_gate"]))
           and torch.allclose(out["k_gate"], torch.ones_like(out["k_gate"])))

    # With two feedback sources.
    out = ft(sensory, feedback_list=[fb_a, fb_b])
    _check("FT.out shape with feedback", tuple(out["out"].shape) == (B, N, D))
    # At init, feedback_init_scale=0 → projections are zeroed but bias is also
    # zeroed, so feedback Q/K/V contributions ARE zero → gates still ≈ 1.
    _check("FT with zero-init feedback → gates ≈ 1",
           torch.allclose(out["q_gate"], torch.ones_like(out["q_gate"]), atol=1e-5))


def test_gridcell_cell() -> None:
    print("\n[3] GridCellRNNCell ---")
    B, in_ch, st_ch, H, W = 2, 32, 32, 12, 12
    cell = GridCellRNNCell(
        in_channels=in_ch, state_channels=st_ch, grid_h=H, grid_w=W,
        n_heads=4, n_feedback=2,
    )

    z = torch.randn(B, in_ch, H, W)
    C_prev = torch.zeros(B, st_ch, H, W)
    fb1 = torch.randn(B, st_ch, H, W)
    fb2 = torch.randn(B, st_ch, H, W)

    out = cell(z, C_prev, feedback_list=[fb1, fb2])
    _check("Cell.C_new shape", tuple(out["C_new"].shape) == (B, st_ch, H, W))
    _check("Cell.attn shape", tuple(out["attn"].shape) == (B, 4, H * W, H * W))
    _check("Cell.u_gate shape", tuple(out["u_gate"].shape) == (B, st_ch, H, W))
    _check("Cell.r_gate shape", tuple(out["r_gate"].shape) == (B, st_ch, H, W))
    _check("Cell.sip shape", tuple(out["sip"].shape) == (B, st_ch, H, W))

    # Without feedback (cell still has self-recurrent feedback internally).
    out = cell(z, C_prev, feedback_list=None)
    _check("Cell forward without external feedback", tuple(out["C_new"].shape) == (B, st_ch, H, W))


def test_decoders() -> None:
    print("\n[4] Decoders ---")
    pix = PixelDecoder(in_channels=32, in_h=12, in_w=12, out_h=50, out_w=50)
    C = torch.randn(2, 32, 12, 12)
    out = pix(C)
    _check("PixelDecoder output shape (B, 3, 50, 50)", tuple(out.shape) == (2, 3, 50, 50))

    feat = FeatureDecoder(in_channels=64, in_h=6, in_w=6, out_channels=32, out_h=12, out_w=12)
    C2 = torch.randn(2, 64, 6, 6)
    out = feat(C2)
    _check("FeatureDecoder output shape (B, 32, 12, 12)", tuple(out.shape) == (2, 32, 12, 12))


def test_readout_heads() -> None:
    print("\n[5] Readout heads ---")
    layer_states = [
        torch.randn(2, 32, 12, 12),
        torch.randn(2, 64, 6, 6),
        torch.randn(2, 128, 3, 3),
    ]
    readout = DecisionReadout(
        layer_specs=[(32, 12, 12), (64, 6, 6), (128, 3, 3)],
        decision_dim=64,
    )
    h = readout(layer_states)
    _check("DecisionReadout output (B, 64)", tuple(h.shape) == (2, 64))
    # Per-layer contribution interface should also work for ablation use.
    contribs = readout.per_layer_contributions(layer_states)
    _check("per_layer_contributions length = 3", len(contribs) == 3)
    _check("per_layer_contributions[0] shape (B, 64)", tuple(contribs[0].shape) == (2, 64))

    actor = ActorHead(64, hidden_dim=64, n_actions=2)
    logits = actor(h)
    _check("ActorHead output (B, 2)", tuple(logits.shape) == (2, 2))

    # Scalar critic (ablation).
    critic = CriticHead(64, hidden_dim=64)
    v = critic(h)
    _check("CriticHead (scalar) output (B,)", tuple(v.shape) == (2,))

    # Distributional Q critic (default).
    qhead = DistributionalQHead(64, hidden_dim=64, n_actions=2, n_quantiles=51)
    q_out = qhead(h, logits)
    _check("DistributionalQHead.q_dist shape (B, |A|, N)",
           tuple(q_out["q_dist"].shape) == (2, 2, 51))
    _check("DistributionalQHead.q_values shape (B, |A|)",
           tuple(q_out["q_values"].shape) == (2, 2))
    _check("DistributionalQHead.value shape (B,)",
           tuple(q_out["value"].shape) == (2,))

    # Test the V = Σ sg[π] · Q identity numerically.
    with torch.no_grad():
        probs = torch.softmax(logits, dim=-1)
        expected_v = (probs * q_out["q_values"]).sum(dim=-1)
        _check("V = Σ π · Q identity", torch.allclose(q_out["value"], expected_v, atol=1e-6))

    # Test stop-gradient on π: gradient w.r.t. action_logits should NOT flow
    # through value when V is the only loss.
    logits_diff = torch.randn(2, 2, requires_grad=True)
    h_diff = torch.randn(2, 64)
    q_out2 = qhead(h_diff, logits_diff)
    q_out2["value"].sum().backward()
    grad_present = logits_diff.grad is not None and logits_diff.grad.abs().sum().item() > 0
    _check("DistributionalQHead V is detached from actor (no grad through π)", not grad_present)


def test_quantile_huber_loss() -> None:
    print("\n[5b] quantile_huber_loss ---")
    B, N = 4, 51
    preds = torch.zeros(B, N, requires_grad=True)
    targets = torch.ones(B)
    loss = quantile_huber_loss(preds, targets, kappa=1.0)
    _check("quantile_huber_loss returns scalar", loss.dim() == 0)
    _check("quantile_huber_loss positive on nonzero residual", loss.item() > 0)
    # Loss should be zero when predictions equal targets at every quantile.
    preds_eq = targets.view(B, 1).expand(B, N).clone()
    loss_zero = quantile_huber_loss(preds_eq, targets, kappa=1.0)
    _check("quantile_huber_loss == 0 at perfect prediction",
           torch.isclose(loss_zero, torch.zeros(()), atol=1e-7))
    # Gradient flows back to predictions.
    loss.backward()
    _check("quantile_huber_loss has gradient w.r.t. predictions",
           preds.grad is not None and preds.grad.abs().sum().item() > 0)


# --- End-to-end model test ---------------------------------------------------


def test_full_model() -> None:
    print("\n[6] HRAModel — full forward_step (distributional critic) ---")
    model = HRAModel(
        in_channels=3, image_h=50, image_w=50,
        state_channels=(32, 64, 128),
        n_FR=5, n_heads=4,
        init_action_logit_bias=[0.0, -4.0],
        critic_kind="distributional",
        n_quantiles=51,
    )

    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"     trainable params: {n_params:,}")

    B = 2
    x = torch.randn(B, 3, 50, 50)
    prev_states = model.init_states(B)
    _check("init_states[0] shape", tuple(prev_states[0].shape) == (B, 32, 12, 12))
    _check("init_states[1] shape", tuple(prev_states[1].shape) == (B, 64, 6, 6))
    _check("init_states[2] shape", tuple(prev_states[2].shape) == (B, 128, 3, 3))

    out = model.forward_step(x, prev_states)

    _check("StepOutput.action_logits shape", tuple(out.action_logits.shape) == (B, 2))
    _check("StepOutput.value shape", tuple(out.value.shape) == (B,))
    _check("StepOutput.q_dist shape (B, |A|, N)", tuple(out.q_dist.shape) == (B, 2, 51))
    _check("StepOutput.q_values shape (B, |A|)", tuple(out.q_values.shape) == (B, 2))
    _check("StepOutput.layer_states_new lengths", len(out.layer_states_new) == 3)
    _check("StepOutput.layer_states_new[0] shape", tuple(out.layer_states_new[0].shape) == (B, 32, 12, 12))
    _check("StepOutput.layer_states_new[1] shape", tuple(out.layer_states_new[1].shape) == (B, 64, 6, 6))
    _check("StepOutput.layer_states_new[2] shape", tuple(out.layer_states_new[2].shape) == (B, 128, 3, 3))
    _check("StepOutput.pc_pred shape", tuple(out.pc_pred.shape) == (B, 3, 50, 50))
    _check("StepOutput.pc_loss is scalar", out.pc_loss.dim() == 0)

    # V = Σ sg[π] · Q identity at the model level.
    with torch.no_grad():
        probs = torch.softmax(out.action_logits, dim=-1)
        expected_v = (probs * out.q_values).sum(dim=-1)
        _check("Model-level V = Σ π · Q identity", torch.allclose(out.value, expected_v, atol=1e-6))

    # Interpretability hooks.
    _check("attn_per_layer has n_FR entries", len(out.attn_per_layer) == 5)
    _check("attn_per_layer[k] has 3 layer entries", len(out.attn_per_layer[0]) == 3)
    _check("attn_per_layer[0][0] shape (B, 4, 144, 144)",
           tuple(out.attn_per_layer[0][0].shape) == (B, 4, 144, 144))
    _check("attn_per_layer[0][1] shape (B, 4, 36, 36)",
           tuple(out.attn_per_layer[0][1].shape) == (B, 4, 36, 36))
    _check("attn_per_layer[0][2] shape (B, 4, 9, 9)",
           tuple(out.attn_per_layer[0][2].shape) == (B, 4, 9, 9))

    _check("state_per_layer has n_FR entries", len(out.state_per_layer) == 5)
    _check("state_per_layer[-1][0] matches final C_1",
           torch.equal(out.state_per_layer[-1][0], out.layer_states_new[0]))

    _check("feedback_projections has n_FR entries", len(out.feedback_projections) == 5)
    fbk = out.feedback_projections[0]
    _check("feedback_projections keys complete",
           set(fbk.keys()) == {"ascend_2to1", "ascend_3to1", "ascend_3to2",
                                "descend_1to2", "descend_2to3"})
    _check("ascend_2to1 shape", tuple(fbk["ascend_2to1"].shape) == (B, 32, 12, 12))
    _check("ascend_3to1 shape", tuple(fbk["ascend_3to1"].shape) == (B, 32, 12, 12))
    _check("ascend_3to2 shape", tuple(fbk["ascend_3to2"].shape) == (B, 64, 6, 6))
    _check("descend_1to2 shape", tuple(fbk["descend_1to2"].shape) == (B, 64, 6, 6))
    _check("descend_2to3 shape", tuple(fbk["descend_2to3"].shape) == (B, 128, 3, 3))

    # Round-trip: feed the new states back in as prev_states (episode step).
    out2 = model.forward_step(x, out.layer_states_new)
    _check("Second forward_step produces same shape", tuple(out2.action_logits.shape) == (B, 2))

    # The default model has skips ON (V→C₂, V→C₃, C₁→C₃; retinotectal +
    # cortical-bypass biological motivation). Verify.
    _check("default enable_skips=True (skip modules populated)",
           model.skip_stem_to_c2 is not None
           and model.skip_stem_to_c3 is not None
           and model.skip_c1_to_c3 is not None)
    # Build a separate model with skips disabled for the ablation case.
    model_no_skips = HRAModel(state_channels=(32, 64, 128), n_FR=5, enable_skips=False).to(x.device)
    _check("enable_skips=False removes skip modules",
           model_no_skips.skip_stem_to_c2 is None
           and model_no_skips.skip_stem_to_c3 is None
           and model_no_skips.skip_c1_to_c3 is None)
    out3 = model_no_skips.forward_step(x, model_no_skips.init_states(B))
    _check("enable_skips=False forward_step works", tuple(out3.action_logits.shape) == (B, 2))


def test_scalar_critic_ablation() -> None:
    print("\n[6b] HRAModel — scalar critic ablation ---")
    model = HRAModel(
        state_channels=(32, 64, 128),
        n_FR=5, n_heads=4,
        critic_kind="scalar",
    )
    B = 2
    x = torch.randn(B, 3, 50, 50)
    out = model.forward_step(x, model.init_states(B))
    _check("Scalar-critic value shape (B,)", tuple(out.value.shape) == (B,))
    _check("Scalar-critic q_dist sentinel shape (B, n_a, 1)", tuple(out.q_dist.shape) == (B, 2, 1))
    _check("Scalar-critic q_values sentinel shape (B, n_a)", tuple(out.q_values.shape) == (B, 2))


def test_env_compatibility() -> None:
    """The env produces (50, 50, 3) numpy obs in [-1, 1]. The model expects
    (B, 3, 50, 50) torch tensors. Verify the transform path works."""
    print("\n[7] env ↔ model compatibility ---")
    import numpy as np

    from HRA.env import ChangeDetectionEnv

    env = ChangeDetectionEnv()
    obs = env.reset()
    if isinstance(obs, tuple):
        obs = obs[0]  # gymnasium may return (obs, info)
    _check("env obs shape (50, 50, 3)", tuple(obs.shape) == (50, 50, 3))

    # numpy (H, W, C) → torch (B=1, C, H, W)
    x = torch.from_numpy(np.transpose(obs, (2, 0, 1)).copy()).float().unsqueeze(0)
    _check("transformed obs shape (1, 3, 50, 50)", tuple(x.shape) == (1, 3, 50, 50))

    model = HRAModel(init_action_logit_bias=[0.0, -4.0])
    prev = model.init_states(1)
    out = model.forward_step(x, prev)
    _check("forward_step on env obs runs", out.action_logits.shape == (1, 2))


# --- Main --------------------------------------------------------------------


def main() -> int:
    print("HRA Stage 0 — scaffold shape tests")
    print("=" * 60)
    try:
        test_stem()
        test_attention()
        test_gridcell_cell()
        test_decoders()
        test_readout_heads()
        test_quantile_huber_loss()
        test_full_model()
        test_scalar_critic_ablation()
        test_env_compatibility()
    except Exception:
        traceback.print_exc()
        print("\nUNEXPECTED EXCEPTION — see traceback above.")
        return 2

    print("=" * 60)
    print(f"  passed: {_PASSED}    failed: {_FAILED}")
    if _FAILED == 0:
        print("  STAGE 0 GATE: PASS")
        return 0
    print("  STAGE 0 GATE: FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
