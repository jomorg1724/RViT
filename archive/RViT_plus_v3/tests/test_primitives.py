"""
Stage 0b gate: shape tests for the RViT+ primitives (stem, FT, GridCell RNN).

Run:
    /usr/bin/python3 RViT_plus/tests/test_primitives.py
"""
from __future__ import annotations

import os
import sys
import traceback

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v3.attention import FeedbackTransformer
from RViT_plus_v3.memory import GridCellRNN_LSTM
from RViT_plus_v3.stem import V1Stem


_PASSED = 0
_FAILED = 0


def _check(name, condition, detail=""):
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


def test_stem():
    print("\n[1] V1Stem ---")
    stem = V1Stem(in_channels=3, mid_channels=32, out_channels=64)
    x = torch.randn(2, 3, 50, 50)
    V = stem(x)
    _check("V1Stem output shape (B, 64, 12, 12)", tuple(V.shape) == (2, 64, 12, 12),
           detail=str(tuple(V.shape)))


def test_feedback_transformer():
    print("\n[2] FeedbackTransformer (V3b: multi-head spatial-softmax attention) ---")
    B, D, H, W = 2, 64, 12, 12
    NH = 32   # head count; each head owns D/NH = 2 channels
    # Two feedback sources at d_model channels each → c_feedback = 2 * D.
    ft = FeedbackTransformer(d_model=D, n_heads=NH, c_feedback=2 * D, n_feedback=2)

    sensory = torch.randn(B, D, H, W)
    fb_a = torch.randn(B, D, H, W)
    fb_b = torch.randn(B, D, H, W)

    # No feedback → pure self-attention path.
    out = ft(sensory, feedback_list=None)
    _check("FT.out shape (B, C, H, W)", tuple(out["out"].shape) == (B, D, H, W))
    _check("FT.attn shape (B, n_heads, H, W) — per-head spatial softmax maps",
           tuple(out["attn"].shape) == (B, NH, H, W))
    _check("FT.attn_spatial shape (B, C, H, W) — A·V residual contribution",
           tuple(out["attn_spatial"].shape) == (B, D, H, W))
    _check("FT no-feedback fusion gates are None (Z-only path)",
           out["q_gate"] is None and out["k_gate"] is None and out["v_gate"] is None)

    # With feedback (gated Z↔H fusion).
    out = ft(sensory, feedback_list=[fb_a, fb_b])
    _check("FT with feedback: out shape (B, C, H, W)",
           tuple(out["out"].shape) == (B, D, H, W))
    _check("FT gate shapes (B, C, H, W)",
           tuple(out["q_gate"].shape) == (B, D, H, W)
           and tuple(out["k_gate"].shape) == (B, D, H, W)
           and tuple(out["v_gate"].shape) == (B, D, H, W))
    # Z↔H fusion gates pass through sigmoid → values in [0, 1].
    _check("FT fusion gates are in [0, 1]",
           bool((out["q_gate"] >= 0).all() and (out["q_gate"] <= 1).all()))

    # V3b attention is a per-head SPATIAL SOFTMAX: each head's (H,W) map is a
    # probability distribution over the grid (sums to 1, competition over space).
    print("\n[3] FT per-head spatial softmax ---")
    A = out["attn"]                  # (B, NH, H, W)
    _check("attn values are non-negative", bool((A >= 0).all()))
    sums = A.reshape(B, NH, H * W).sum(dim=-1)
    _check("each head's spatial map sums to 1 (softmax over grid)",
           torch.allclose(sums, torch.ones_like(sums), atol=1e-5),
           detail=f"per-head spatial sum mean={sums.mean().item():.4f}")


def test_gridcell_rnn():
    print("\n[4] GridCellRNN_LSTM ---")
    B, in_ch, st_ch, H, W = 2, 64, 64, 12, 12
    cell = GridCellRNN_LSTM(
        in_channels=in_ch, state_channels=st_ch, grid_h=H, grid_w=W,
        n_heads=32, n_feedback=2,
    )

    z = torch.randn(B, in_ch, H, W)
    C_prev = torch.zeros(B, st_ch, H, W)
    fb1 = torch.randn(B, st_ch, H, W)
    fb2 = torch.randn(B, st_ch, H, W)

    out = cell(z, C_prev, feedback_list=[fb1, fb2])
    _check("Cell.C_new shape", tuple(out["C_new"].shape) == (B, st_ch, H, W))
    _check("Cell.attn shape (B, n_heads, H, W) — V3b per-head spatial softmax",
           tuple(out["attn"].shape) == (B, 32, H, W))
    _check("Cell.tilde_C shape", tuple(out["tilde_C"].shape) == (B, st_ch, H, W))
    _check("Cell.u_gate shape", tuple(out["u_gate"].shape) == (B, st_ch, H, W))

    # Without external feedback (cell still has self-recurrent C_prev internally).
    out = cell(z, C_prev, feedback_list=None)
    _check("Cell forward without external feedback",
           tuple(out["C_new"].shape) == (B, st_ch, H, W))


def test_reactive_gates():
    """Update-gate bias = 0 → reactive cells. Verify σ(0) ≈ 0.5 baseline."""
    print("\n[6] Reactive gates (update_gate bias = 0) ---")
    cell = GridCellRNN_LSTM(in_channels=64, state_channels=64, grid_h=12, grid_w=12)
    # The update-gate bias should be initialised to 0; sigmoid(0) = 0.5.
    with torch.no_grad():
        bias_mean = float(cell.conv_update.bias.mean().item())
    _check("update_gate_bias init ≈ 0", abs(bias_mean) < 1e-6,
           detail=f"{bias_mean:.6f}")

    # Cell should be responsive at random init.
    z = torch.randn(2, 64, 12, 12)
    C_prev = torch.randn(2, 64, 12, 12) * 0.1  # small prev state
    out1 = cell(z, C_prev, feedback_list=None)
    out2 = cell(z * 2.0, C_prev, feedback_list=None)  # different input
    delta = float((out1["C_new"] - out2["C_new"]).abs().mean().item())
    _check("Cell is reactive to input changes at init", delta > 0.01,
           detail=f"|C_new(z) − C_new(2z)| mean = {delta:.4f}")


def test_param_count():
    """Sanity check: small param count for individual primitives."""
    print("\n[7] Param-count budget check ---")
    stem = V1Stem(out_channels=64)
    p_stem = sum(p.numel() for p in stem.parameters())
    print(f"     stem params: {p_stem:,}")
    _check("stem params < 100K", p_stem < 100_000)

    ft = FeedbackTransformer(d_model=64, n_heads=4, c_feedback=2 * 64, n_feedback=2)
    p_ft = sum(p.numel() for p in ft.parameters())
    print(f"     FT (n_fb=2, d=64) params: {p_ft:,}")
    # Conv-spatial FT with 3x3-everywhere convs is much bigger than the old
    # flatten-and-linear FT. Budget reflects the new architecture.
    _check("FT params < 2M", p_ft < 2_000_000)

    cell = GridCellRNN_LSTM(in_channels=64, state_channels=64, grid_h=12, grid_w=12, n_feedback=2)
    p_cell = sum(p.numel() for p in cell.parameters())
    print(f"     GridCell (in=64, st=64, n_fb=2) params: {p_cell:,}")
    _check("Cell params < 2M", p_cell < 2_000_000)


def main():
    print("RViT+ Stage 0b — primitive shape tests")
    print("=" * 60)
    try:
        test_stem()
        test_feedback_transformer()
        test_gridcell_rnn()
        test_reactive_gates()
        test_param_count()
    except Exception:
        traceback.print_exc()
        print("\nUNEXPECTED EXCEPTION — see traceback above.")
        return 2

    print("=" * 60)
    print(f"  passed: {_PASSED}    failed: {_FAILED}")
    if _FAILED == 0:
        print("  STAGE 0b GATE: PASS")
        return 0
    print("  STAGE 0b GATE: FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
