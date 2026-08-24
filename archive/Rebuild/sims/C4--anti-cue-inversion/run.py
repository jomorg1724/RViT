"""
Rebuild/sims/C4--anti-cue-inversion/run.py — RB-008.

Status: simulation increment rb-012 (2026-05-25), prompt v0.2.
Backing for: manuscript §results-C4 + the anti-cue inversion prediction
(RB-012, §results-C4 redraft as a conditional theorem with the explicit
V ≥ 1/N condition and the new falsifiable anti-cue prediction).

================================================================
WHAT THIS SIMULATION COMPUTES
================================================================

The inherited paper's §4.5 C4 claim — "inverted attention (α* < 1/N) is
never optimal" — is CONFIRMED-CONDITIONAL in the live ledger.  It holds
across the 4,410-cell primary sweep at N=4, V ∈ [1/N, 1.0] (the cued
regime), but the wording "regardless of r" is wrong as a local statement
(left one-sided derivative at α=1/N is r-linear, sign-flips at the
closed-form boundary r†_inv := (N-1) A_0/B_0), and the categorical
strength "never below it" fails OUTSIDE the V ≥ 1/N condition (the model
DOES produce α* < 1/N in the anti-cue regime V < 1/N — verified by the
reviewer's CR-004 at N=2 only).

This simulation publishes the rebuilt model's C4 evidence at *defensible
strength*:

  Step A.  Closed-form r†_inv(V, v, N, CR, ρ) across the paper's primary
           (V, v, variant) grid at N=4, at ρ ∈ {0, 0.2}.  Tabulate where
           r†_inv falls relative to the swept r ∈ [0.1, 10].  At ρ=0
           this reproduces the reviewer's Step A table (CR-004) to
           machine tolerance (the formula is identical; only the C_GRID
           differs slightly, [-2.5, 2.5] vs [-3, 3], which can shift the
           optimal criterion by at most one grid step).  At ρ=0.2 this
           is NEW: the closed form generalises with ρ-aware partial
           derivatives ∂P_no-fa(ρ)/∂d'_c and ∂P_no-fa(ρ)/∂d'_u computed
           by the same one-factor Gauss-Hermite quadrature that
           `Rebuild/model/core.py` uses for P_no-fa(ρ) itself.

  Step B.  Full E[R](α) sweep on Δα=0.005 grid (matching the paper) at
           the most-adversarial primary-sweep cells (smallest r†_inv) at
           r=10, both ρ ∈ {0, 0.2}.  Confirm zero global inversions
           across the primary sweep — the inherited empirical claim
           survives at ρ=0 and is robust under A1 (ρ=0.2 perturbation).

  Step C.  *Anti-cue regime at N=4* — the rebuild's new contribution.
           The reviewer's CR-004 ran anti-cue only at N=2 (V ∈ {0.25,
           0.40} with N=2, i.e. V < 1/N = 0.5).  The paper's primary
           topology is N=4, so the natural rebuild question is: does
           inversion onset at V < 1/N also occur at N=4?  We sweep
           V ∈ {0.05, 0.10, 0.15, 0.20} (all < 1/N=0.25 at N=4) at
           v ∈ {1, 3, 5}, r ∈ {0.1, 0.5, 1, 3, 5, 10}, ρ ∈ {0, 0.2}.

  Step D.  α*(V, r) map at fixed v=5, N=4, ρ ∈ {0, 0.2}, V ∈ [0.05, 1.0],
           r ∈ [0.1, 10].  Shows the inversion onset as V crosses 1/N
           from above; the figure used by the manuscript §results-C4 to
           anchor the conditional theorem with a single visual.

  Recovery test.  Reproduce the reviewer's CR-004 derivation §5 Step C(i)
           table (V=0.25, v=1, N=4, variant A, ρ=0): at r ∈ {0.1, 1.0,
           1.585, 2.512, 3.981, 10.0} the global α* and R* match the
           reviewer's reported {0.250/0.62946, 0.250/0.62946, 0.460/
           0.63156, 0.660/0.63745, 0.805/0.64519, 0.955/0.65936} to a
           tolerance set by the C_GRID width discrepancy.

================================================================
INHERITED CLAIM, REBUILT STRENGTH, AND THE NEW PREDICTION
================================================================

Inherited paper §4.5 (verbatim, categorical):
  "Across all 4,410 rows of the primary sweep — spanning r ∈ [0.1, 10],
   V ∈ [0.25, 1.0], v ∈ {1, …, 5}, and both reward variants — the
   optimal α* is always ≥ 1/N. … In the most cost-dominant regime
   (r → 0), the optimal strategy converges to uniform attention
   (α* = 1/N), never below it."

Rebuilt strength (CLAIM_LEDGER C4 row, the ceiling this sim respects):
  CONFIRMED-CONDITIONAL.  Under V ≥ 1/N and v ≥ 1, the empirical claim
  holds across the 4,410-cell primary sweep — globally, not via local
  cost-vs-benefit balance.  The mechanism is the location-count
  asymmetry (1 cued, N-1 uncued) combined with the value-weight
  inequality w_c ≥ w_u.  The closed-form r†_inv = (N-1) A_0/B_0 governs
  the LOCAL left-derivative at α=1/N; it falls inside [0.1, 10] in
  ≈49% of swept cells at N=4, but the right-branch global maximum
  dominates throughout, so no GLOBAL inversion occurs in the primary
  sweep.

New falsifiable prediction (the rebuilt model's positive claim):
  Below V = 1/N (anti-cue regime), the value-weight inequality flips
  (w_c < w_u), the location-count argument reverses, and the model's
  global optimum becomes α* < 1/N.  The reviewer established this at
  N=2 only; we now establish it at N=4, the paper's primary topology,
  and show that the A1 decorrelation channel ρ DOES NOT abolish the
  inversion (ρ=0.2 leaves the inversion onset and global α* < 1/N
  intact, with second-order shifts in magnitude — the cross-axis
  generalisation of the rb-002 / rb-004 / rb-010 A1-sensitivity
  pattern onto the inversion axis).

================================================================
COMPUTATION
================================================================

All primitives drive `Rebuild/model/core.py`.  No model code is
reimplemented in this sim — we use `d_prime_asym`, `optimal_R`,
`p_no_fa_grid` directly.  The `d_prime_asym` function already handles
the α < 1/N branch with the β/γ swap (paper §2.4 inversion branch);
the rebuilt model's `policies()` default α-grid is [1/N, 1], but for
the inversion question we override with the full grid [0.02, 1.0].

The closed-form r†_inv(ρ) requires ρ-aware partials A_0(ρ), B_0(ρ).
We compute them by the one-factor Gauss-Hermite quadrature (same nq=64
nodes as `core.gauss_hermite`):

  ∂P_no-fa(ρ)/∂d'_c = 0.5/√(1-ρ) · ∫ φ((b_c - √ρ z)/√(1-ρ))
                                     · Φ((b_u - √ρ z)/√(1-ρ))^(N-1) φ(z) dz
  ∂P_no-fa(ρ)/∂d'_u = (N-1)·0.5/√(1-ρ) · ∫ Φ((b_c - √ρ z)/√(1-ρ))
                                     · Φ((b_u - √ρ z)/√(1-ρ))^(N-2)
                                     · φ((b_u - √ρ z)/√(1-ρ)) φ(z) dz

At ρ=0 these collapse bit-for-bit to the reviewer's analytic formulae
(derivation §2.2): A_0 = 0.25 [V·v·p^H_c + CR·p^F_c·(1-FAR_u)^(N-1)],
B_0 = 0.25 [(1-V)·p^H_u + (N-1)·CR·(1-FAR_c)·(1-FAR_u)^(N-2)·p^F_u].

DETERMINISM AND REPRODUCIBILITY.  No RNG.  All output is a pure
function of `Rebuild/model/core.py` + grid parameters listed at the
top of `main()`.  Output sha256 recorded in `output/results.json` →
`metadata.output_sha256` and reported in the run-log entry.

ATTRIBUTION.  Step A boundary closed form is the reviewer's
(`Critique/derivations/C4--no-inversion.md` §2-3).  Step B method is
the reviewer's (`Critique/replications/C4--no-inversion/run.py`
Step B), reimplemented against the rebuilt model.  Step C is partial
overlap with the reviewer's Step C(iii) but at N=4 instead of N=2;
the ρ>0 sensitivity within Step C is new.  Step D and the α*(V, r)
heatmap are new.  The recovery test cites the reviewer's CR-004
derivation §5 Step C(i) table verbatim.

RB-008, prompt v0.2, run 2026-05-25.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt

# ---- import the rebuilt model -----------------------------------------------
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]  # Rebuild/
sys.path.insert(0, str(ROOT))

from model.core import (  # noqa: E402
    C_GRID,
    _GH_W,
    _GH_Z,
    PHI_BACKEND,
    Phi,
    beta_gamma,
    d_prime_asym,
    f_transfer,
    floor_R,
    make_h,
    optimal_R,
    p_no_fa_grid,
    p_no_fa_point,
)


# =============================================================================
# Closed-form boundary inversion threshold r†_inv with ρ awareness.
# =============================================================================

_SQRT_2PI = math.sqrt(2.0 * math.pi)


def _phi_pdf(x: np.ndarray | float) -> np.ndarray | float:
    """Standard normal PDF (vectorised)."""
    arr = np.asarray(x, dtype=float)
    return np.exp(-0.5 * arr * arr) / _SQRT_2PI


def _optimal_criteria_at_uniform(d_base: float, v: float, V: float, N: int,
                                 variant: str, rho: float) -> tuple[float, float]:
    """Return (c_c*, c_u*) maximising E[R] at α=1/N (d_c = d_u = d_base).

    Joint grid search over C_GRID × C_GRID (same as the reviewer's
    procedure and what `optimal_R` does internally).
    """
    hr_c = Phi(d_base / 2.0 - C_GRID)  # (n_c,)
    hr_u = Phi(d_base / 2.0 - C_GRID)  # identical, but kept for clarity
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    p_nofa = p_no_fa_grid(d_base, d_base, N, rho)  # (n_c, n_c)
    er = (
        0.5 * (V * v * hr_c[:, None] + (1.0 - V) * hr_u[None, :])
        + 0.5 * cr * p_nofa
    )
    idx_flat = int(np.argmax(er))
    i, j = np.unravel_index(idx_flat, er.shape)
    return float(C_GRID[i]), float(C_GRID[j])


def _A0_B0(V: float, v: float, N: int, d_base: float, c_c: float, c_u: float,
           variant: str, rho: float) -> tuple[float, float]:
    """Boundary partials A_0 = ∂E[R]/∂d'_c and B_0 = ∂E[R]/∂d'_u at α=1/N.

    Closed form for ρ=0 (matches reviewer derivation §2.2 bit-for-bit);
    one-factor Gauss-Hermite for ρ>0.
    """
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    b_c = c_c + d_base / 2.0
    b_u = c_u + d_base / 2.0
    p_c_H = float(_phi_pdf(d_base / 2.0 - c_c))   # = HR-density at c_c*
    p_u_H = float(_phi_pdf(d_base / 2.0 - c_u))   # = HR-density at c_u*

    if rho <= 0.0:
        p_c_F = float(_phi_pdf(b_c))              # = FA-density (same as φ(-b_c))
        p_u_F = float(_phi_pdf(b_u))
        one_minus_FAR_c = float(Phi(b_c))
        one_minus_FAR_u = float(Phi(b_u))
        A_0 = 0.25 * (V * v * p_c_H
                      + cr * p_c_F * (one_minus_FAR_u ** (N - 1)))
        B_0 = 0.25 * ((1.0 - V) * p_u_H
                      + (N - 1) * cr * (1.0 - 0.0)  # spacer for readability
                      * one_minus_FAR_c * (one_minus_FAR_u ** (N - 2)) * p_u_F)
        return A_0, B_0

    # ρ > 0: one-factor GH quadrature for ∂P_no-fa/∂d'_c and ∂P_no-fa/∂d'_u.
    # P_no-fa(ρ) = ∫ Φ((b_c - √ρ z)/s) · Φ((b_u - √ρ z)/s)^(N-1) φ(z) dz,  s = √(1-ρ).
    # ∂/∂d'_c    = ∫ (1/2s) φ((b_c - √ρ z)/s) · Φ((b_u - √ρ z)/s)^(N-1) φ(z) dz.
    # ∂/∂d'_u    = ∫ Φ((b_c - √ρ z)/s) · (N-1)·(1/2s) φ((b_u - √ρ z)/s) · Φ(·)^(N-2) φ(z) dz.
    s = math.sqrt(1.0 - rho)
    rs = math.sqrt(rho)
    z = _GH_Z                                       # (nq,)
    arg_c = (b_c - rs * z) / s                      # (nq,)
    arg_u = (b_u - rs * z) / s                      # (nq,)
    Phi_c = Phi(arg_c)                              # (nq,)
    Phi_u = Phi(arg_u)                              # (nq,)
    phi_c = _phi_pdf(arg_c)                         # (nq,)
    phi_u = _phi_pdf(arg_u)                         # (nq,)

    integrand_c = (0.5 / s) * phi_c * (Phi_u ** (N - 1))
    integrand_u = (N - 1) * (0.5 / s) * Phi_c * (Phi_u ** (N - 2)) * phi_u

    dP_dc = float(np.sum(_GH_W * integrand_c))
    dP_du = float(np.sum(_GH_W * integrand_u))

    A_0 = 0.25 * V * v * p_c_H + 0.5 * cr * dP_dc
    B_0 = 0.25 * (1.0 - V) * p_u_H + 0.5 * cr * dP_du
    return A_0, B_0


def r_inv_threshold(V: float, v: float, N: int, d_max: float, f0: float,
                    h_name: str, variant: str, rho: float) -> dict:
    """Closed-form r†_inv(V, v, N, CR, ρ) := (N-1) · A_0(ρ) / B_0(ρ).

    Returns the threshold plus diagnostic intermediates.
    """
    h = make_h(h_name)
    d_base = float(d_max * f_transfer(1.0 / N, f0, h))
    c_c_star, c_u_star = _optimal_criteria_at_uniform(d_base, v, V, N, variant, rho)
    A_0, B_0 = _A0_B0(V, v, N, d_base, c_c_star, c_u_star, variant, rho)
    r_inv = (N - 1) * A_0 / B_0 if B_0 > 1e-15 else float("inf")
    return {
        "r_inv_star": float(r_inv),
        "A_0": float(A_0),
        "B_0": float(B_0),
        "c_c_star": c_c_star,
        "c_u_star": c_u_star,
        "d_base": d_base,
    }


# =============================================================================
# Full α-sweep (including the α < 1/N inversion branch).
# =============================================================================

ALPHA_GRID_FULL = np.round(np.arange(0.02, 1.0 + 1e-9, 0.005), 6)  # 197 pts


def er_curve_full(r: float, V: float, v: float, N: int, d_max: float, f0: float,
                  h_name: str, variant: str, rho: float,
                  alpha_grid: np.ndarray = ALPHA_GRID_FULL) -> dict:
    """E[R](α) on the full α grid including α < 1/N; returns curve + branch argmaxes."""
    h = make_h(h_name)
    Rs = np.empty(len(alpha_grid), dtype=float)
    for k, a in enumerate(alpha_grid):
        d_c, d_u = d_prime_asym(float(a), r, d_max, f0, h, N)
        Rs[k] = optimal_R(d_c, d_u, v, V, N, variant, rho)

    inv_N = 1.0 / N

    idx_g = int(np.argmax(Rs))
    alpha_g = float(alpha_grid[idx_g])
    R_g = float(Rs[idx_g])

    left_mask = alpha_grid < inv_N - 1e-9
    if left_mask.any():
        idx_l = int(np.argmax(np.where(left_mask, Rs, -np.inf)))
        alpha_l = float(alpha_grid[idx_l])
        R_l = float(Rs[idx_l])
    else:
        alpha_l = float("nan")
        R_l = float("nan")

    right_mask = alpha_grid > inv_N + 1e-9
    if right_mask.any():
        idx_r = int(np.argmax(np.where(right_mask, Rs, -np.inf)))
        alpha_r = float(alpha_grid[idx_r])
        R_r = float(Rs[idx_r])
    else:
        alpha_r = float("nan")
        R_r = float("nan")

    # R at α=1/N exactly (use d' at that boundary).
    d_c_at, d_u_at = d_prime_asym(inv_N, r, d_max, f0, h, N)
    R_at_inv_N = optimal_R(d_c_at, d_u_at, v, V, N, variant, rho)

    return {
        "alpha_grid": alpha_grid,
        "Rs": Rs,
        "alpha_global": alpha_g,
        "R_global": R_g,
        "alpha_left": alpha_l,
        "R_left": R_l,
        "alpha_right": alpha_r,
        "R_right": R_r,
        "R_at_inv_N": float(R_at_inv_N),
        "inversion_global": bool(alpha_g < inv_N - 1e-9),
    }


# =============================================================================
# Reproducibility helpers.
# =============================================================================


def _digest(obj) -> str:
    """sha256 of canonical-JSON-serialised obj (floats rounded to 12 dp)."""
    def _norm(o):
        if isinstance(o, dict):
            return {k: _norm(o[k]) for k in sorted(o)}
        if isinstance(o, (list, tuple)):
            return [_norm(x) for x in o]
        if isinstance(o, (np.floating, float)):
            v = float(o)
            if math.isnan(v):
                return "nan"
            if math.isinf(v):
                return "inf" if v > 0 else "-inf"
            return round(v, 12)
        if isinstance(o, (np.integer, int)):
            return int(o)
        if isinstance(o, bool):
            return bool(o)
        if isinstance(o, np.ndarray):
            return _norm(o.tolist())
        return o
    s = json.dumps(_norm(obj), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# =============================================================================
# Main.
# =============================================================================

def main() -> None:
    out_dir = HERE / "output"
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # Headline cell params (matching rb-002 / rb-004 / rb-007 / rb-010).
    N = 4
    d_max = 2.0
    f0 = 0.5
    h_name = "sqrt"

    t0 = time.time()
    print("=" * 76)
    print("RB-008 — C4 anti-cue inversion sim (Rebuild)")
    print("=" * 76)
    print(f"Phi backend: {PHI_BACKEND}")
    print(f"C_GRID: [{C_GRID[0]:.2f}, {C_GRID[-1]:.2f}] step {C_GRID[1]-C_GRID[0]:.3f} "
          f"(n={len(C_GRID)})")
    print(f"ALPHA_GRID_FULL: [{ALPHA_GRID_FULL[0]:.3f}, {ALPHA_GRID_FULL[-1]:.3f}] "
          f"step 0.005 (n={len(ALPHA_GRID_FULL)})")
    print(f"GH nodes: {len(_GH_Z)}")
    print(f"Cell: N={N}, d'_max={d_max}, f0={f0}, h={h_name}")
    print()

    rng_log: list = []  # plain Python list of dict rows

    # ----------------------------------------------------------------
    # STEP A — closed-form r†_inv(V, v, variant, ρ) across primary grid.
    # ----------------------------------------------------------------
    print("-" * 76)
    print("STEP A — Closed-form r†_inv(V, v, N=4, variant, ρ) on primary grid.")
    print("-" * 76)

    V_grid_A = np.linspace(0.25, 1.0, 21)  # 1/N=0.25 to 1, 21 points
    v_grid_A = [1.0, 2.0, 3.0, 4.0, 5.0]
    variants = ["A", "B"]
    rhos_A = [0.0, 0.2]

    step_A_rows = []
    for variant in variants:
        for rho in rhos_A:
            for V in V_grid_A:
                for v in v_grid_A:
                    t = r_inv_threshold(float(V), float(v), N, d_max, f0,
                                        h_name, variant, float(rho))
                    in_range = (0.1 <= t["r_inv_star"] <= 10.0)
                    step_A_rows.append({
                        "N": N, "V": float(V), "v": float(v),
                        "variant": variant, "rho": float(rho),
                        "r_inv_star": t["r_inv_star"],
                        "A_0": t["A_0"], "B_0": t["B_0"],
                        "c_c_star": t["c_c_star"], "c_u_star": t["c_u_star"],
                        "in_sweep_range": bool(in_range),
                    })

    # Tally per (variant, ρ) panel.
    print(f"  {'variant':>7s} {'ρ':>5s}  {'in [0.1,10]':>12s} {'> 10':>6s} {'< 0.1':>6s} "
          f"{'min r†':>9s} {'median r†':>11s}")
    step_A_tally = {}
    for variant in variants:
        for rho in rhos_A:
            cells = [r for r in step_A_rows
                     if r["variant"] == variant and r["rho"] == rho]
            n_total = len(cells)
            n_in = sum(1 for c in cells if c["in_sweep_range"])
            n_above = sum(1 for c in cells if c["r_inv_star"] > 10.0)
            n_below = sum(1 for c in cells if c["r_inv_star"] < 0.1)
            r_inv_vals = np.array([c["r_inv_star"] for c in cells])
            r_inv_vals = r_inv_vals[np.isfinite(r_inv_vals)]
            min_r = float(np.min(r_inv_vals)) if len(r_inv_vals) else float("nan")
            med_r = float(np.median(r_inv_vals)) if len(r_inv_vals) else float("nan")
            step_A_tally[f"variant_{variant}__rho_{rho}"] = {
                "n_total": int(n_total),
                "n_in_range": int(n_in),
                "n_above_10": int(n_above),
                "n_below_0_1": int(n_below),
                "min_r_inv": min_r,
                "median_r_inv": med_r,
            }
            print(f"  {variant:>7s} {rho:>5.2f}  "
                  f"{n_in:>4d}/{n_total:<4d}    {n_above:>6d} {n_below:>6d} "
                  f"{min_r:>9.4f} {med_r:>11.4f}")

    # The 10 most-adversarial cells overall.
    step_A_sorted = sorted(step_A_rows, key=lambda r: r["r_inv_star"])
    print("\n  10 most-adversarial cells across all (variant, ρ):")
    print(f"  {'V':>6s} {'v':>3s} {'var':>4s} {'ρ':>4s} {'r†_inv':>9s}")
    for r in step_A_sorted[:10]:
        print(f"  {r['V']:6.3f} {int(r['v']):3d} {r['variant']:>4s} "
              f"{r['rho']:>4.2f} {r['r_inv_star']:9.4f}")

    # Recovery test #1 against the reviewer's ρ=0 numbers from
    # Critique/derivations/C4--no-inversion.md §4: 49% of (V, v, variant)
    # cells at N=4 have r†_inv in [0.1, 10] under ρ=0.
    rho0_cells = [r for r in step_A_rows if r["rho"] == 0.0]
    n_rho0_total = len(rho0_cells)
    n_rho0_in_range = sum(1 for c in rho0_cells if c["in_sweep_range"])
    pct_rho0_in_range = 100.0 * n_rho0_in_range / n_rho0_total
    recovery_A_pct = abs(pct_rho0_in_range - 49.0)
    print(f"\n  Recovery check (Critique/derivations/C4 §4):")
    print(f"    Reviewer reports 49.0% of (V, v, variant) cells at N=4, ρ=0 with "
          f"r†_inv ∈ [0.1, 10].")
    print(f"    This run finds {pct_rho0_in_range:.1f}% — Δ = {recovery_A_pct:.1f} pp.")
    recovery_A_pass = recovery_A_pct < 1.0
    print(f"    Recovery {'PASS' if recovery_A_pass else 'FAIL'} (tolerance 1.0 pp).")

    # ----------------------------------------------------------------
    # STEP B — Full E[R](α) sweep at adversarial primary-sweep cells at r=10.
    # ----------------------------------------------------------------
    print()
    print("-" * 76)
    print("STEP B — Full α-sweep at adversarial primary-sweep cells (V ≥ 1/N) at r=10.")
    print("-" * 76)

    # Pick the 6 distinct (V, v, variant) cells with the smallest r†_inv at ρ=0.
    seen = set()
    adversarial_cells = []
    for r in step_A_sorted:
        if r["rho"] != 0.0:
            continue
        key = (r["V"], r["v"], r["variant"])
        if key in seen:
            continue
        seen.add(key)
        adversarial_cells.append({
            "V": r["V"], "v": r["v"], "variant": r["variant"],
            "r_inv_star": r["r_inv_star"],
        })
        if len(adversarial_cells) >= 6:
            break

    step_B_rows = []
    r_test = 10.0
    print(f"  α-sweep step Δα=0.005 over [{ALPHA_GRID_FULL[0]:.3f}, {ALPHA_GRID_FULL[-1]:.3f}] "
          f"at r=10 — both ρ ∈ {{0, 0.2}}.")
    print()
    print(f"  {'V':>6s} {'v':>3s} {'var':>3s} {'ρ':>4s} {'r†_inv':>8s} "
          f"{'α*global':>9s} {'R*global':>9s} {'α*left':>7s} {'R*left':>8s} "
          f"{'α*right':>8s} {'R*right':>8s} {'inv?':>5s}")
    print("  " + "-" * 100)
    for cell in adversarial_cells:
        for rho in [0.0, 0.2]:
            curve = er_curve_full(r_test, cell["V"], cell["v"], N, d_max, f0,
                                  h_name, cell["variant"], rho)
            row = {
                "r": r_test, "V": cell["V"], "v": cell["v"],
                "variant": cell["variant"], "rho": rho,
                "r_inv_star_rho0": cell["r_inv_star"],
                "alpha_global": curve["alpha_global"],
                "R_global": curve["R_global"],
                "alpha_left": curve["alpha_left"], "R_left": curve["R_left"],
                "alpha_right": curve["alpha_right"], "R_right": curve["R_right"],
                "R_at_inv_N": curve["R_at_inv_N"],
                "inversion_global": curve["inversion_global"],
            }
            step_B_rows.append(row)
            print(f"  {cell['V']:6.3f} {int(cell['v']):3d} {cell['variant']:>3s} "
                  f"{rho:>4.2f} {cell['r_inv_star']:8.4f} "
                  f"{curve['alpha_global']:9.3f} {curve['R_global']:9.5f} "
                  f"{curve['alpha_left']:7.3f} {curve['R_left']:8.5f} "
                  f"{curve['alpha_right']:8.3f} {curve['R_right']:8.5f} "
                  f"{str(curve['inversion_global']):>5s}")

    primary_inversion_count = sum(1 for r in step_B_rows if r["inversion_global"])
    print(f"\n  Step B primary-sweep inversions across {len(step_B_rows)} (cell, ρ) probes: "
          f"{primary_inversion_count}")

    # ----------------------------------------------------------------
    # STEP C — Anti-cue regime at N=4 (V < 1/N), the rebuild's new evidence.
    # ----------------------------------------------------------------
    print()
    print("-" * 76)
    print("STEP C — Anti-cue regime at N=4 (V < 1/N = 0.25): the rebuild's new evidence.")
    print("-" * 76)

    V_anticue = [0.05, 0.10, 0.15, 0.20]
    v_anticue = [1.0, 3.0, 5.0]
    r_anticue = [0.1, 0.5, 1.0, 3.0, 5.0, 10.0]
    rhos_C = [0.0, 0.2]
    variant_C = "A"  # variant A only to keep wall-clock under budget

    step_C_rows = []
    print(f"  Variant {variant_C}, N=4, ρ ∈ {{0, 0.2}}.")
    print(f"  Sweep V ∈ {V_anticue}, v ∈ {v_anticue}, r ∈ {r_anticue}.")
    print()
    print(f"  {'V':>5s} {'v':>3s} {'r':>6s} {'ρ':>5s} {'r†_inv':>9s} "
          f"{'α*global':>9s} {'R*global':>9s} {'inv?':>5s} {'ΔR_R-L':>9s}")
    print("  " + "-" * 80)
    n_cells_C = 0
    for V in V_anticue:
        for v in v_anticue:
            for rho in rhos_C:
                t = r_inv_threshold(V, v, N, d_max, f0, h_name, variant_C, rho)
                for r in r_anticue:
                    curve = er_curve_full(r, V, v, N, d_max, f0, h_name, variant_C, rho)
                    delta_RL = float(curve["R_right"] - curve["R_left"])
                    row = {
                        "V": V, "v": v, "r": r, "rho": rho,
                        "variant": variant_C,
                        "r_inv_star": t["r_inv_star"],
                        "alpha_global": curve["alpha_global"],
                        "R_global": curve["R_global"],
                        "alpha_left": curve["alpha_left"], "R_left": curve["R_left"],
                        "alpha_right": curve["alpha_right"], "R_right": curve["R_right"],
                        "R_at_inv_N": curve["R_at_inv_N"],
                        "inversion_global": curve["inversion_global"],
                        "delta_R_right_minus_left": delta_RL,
                    }
                    step_C_rows.append(row)
                    n_cells_C += 1
                    print(f"  {V:5.2f} {int(v):3d} {r:6.2f} {rho:5.2f} "
                          f"{t['r_inv_star']:9.4f} "
                          f"{curve['alpha_global']:9.3f} {curve['R_global']:9.5f} "
                          f"{str(curve['inversion_global']):>5s} "
                          f"{delta_RL:9.5f}")
    anticue_inversion_count = sum(1 for r in step_C_rows if r["inversion_global"])
    anticue_inv_rho0 = sum(1 for r in step_C_rows
                           if r["rho"] == 0.0 and r["inversion_global"])
    anticue_inv_rho02 = sum(1 for r in step_C_rows
                            if r["rho"] == 0.2 and r["inversion_global"])
    print(f"\n  Step C anti-cue inversions: total {anticue_inversion_count} / {n_cells_C}")
    print(f"    ρ=0.0   : {anticue_inv_rho0} / {n_cells_C // 2} "
          f"({100*anticue_inv_rho0/(n_cells_C//2):.1f}%)")
    print(f"    ρ=0.2   : {anticue_inv_rho02} / {n_cells_C // 2} "
          f"({100*anticue_inv_rho02/(n_cells_C//2):.1f}%)")

    # The "where does inversion happen" stratification by r.
    print("\n  Inversion incidence stratified by r (ρ=0, all (V, v) combined):")
    r_inv_incidence: dict[float, dict[str, int]] = {}
    for r in r_anticue:
        cells_r = [c for c in step_C_rows if c["r"] == r and c["rho"] == 0.0]
        n = len(cells_r)
        n_inv = sum(1 for c in cells_r if c["inversion_global"])
        r_inv_incidence[r] = {"n_total": n, "n_inv": n_inv}
        print(f"    r={r:5.2f}: {n_inv:2d} / {n:2d} ({100*n_inv/n:5.1f}%)")

    # ----------------------------------------------------------------
    # STEP D — α*(V, r) map at fixed v=5, N=4, both ρ ∈ {0, 0.2}.
    # ----------------------------------------------------------------
    print()
    print("-" * 76)
    print("STEP D — α*(V, r) map at fixed v=5, N=4, ρ ∈ {0, 0.2} (heatmap for §results-C4).")
    print("-" * 76)

    # Geometric V grid covering both anti-cue (V<0.25) and cued (V≥0.25)
    # regions; geometric r grid matching the paper's sweep.
    V_grid_D = np.array(sorted(set(
        np.round(np.linspace(0.05, 0.20, 4).tolist()
                 + np.linspace(0.25, 1.0, 13).tolist(), 6)
    )))
    r_grid_D = np.geomspace(0.1, 10.0, 16)
    # round for hash stability
    r_grid_D = np.round(r_grid_D, 6)

    print(f"  V grid: n={len(V_grid_D)} from {V_grid_D[0]:.3f} to {V_grid_D[-1]:.3f}")
    print(f"  r grid: n={len(r_grid_D)} (geometric)")
    v_D = 5.0
    variant_D = "A"

    step_D = {}
    for rho in [0.0, 0.2]:
        alpha_map = np.full((len(V_grid_D), len(r_grid_D)), np.nan)
        R_map = np.full((len(V_grid_D), len(r_grid_D)), np.nan)
        inv_map = np.zeros((len(V_grid_D), len(r_grid_D)), dtype=int)
        for i, V in enumerate(V_grid_D):
            for j, r in enumerate(r_grid_D):
                curve = er_curve_full(float(r), float(V), v_D, N, d_max, f0,
                                      h_name, variant_D, rho)
                alpha_map[i, j] = curve["alpha_global"]
                R_map[i, j] = curve["R_global"]
                inv_map[i, j] = int(curve["inversion_global"])
        step_D[f"rho_{rho}"] = {
            "V_grid": V_grid_D.tolist(),
            "r_grid": r_grid_D.tolist(),
            "alpha_map": alpha_map.tolist(),
            "R_map": R_map.tolist(),
            "inv_map": inv_map.tolist(),
            "frac_inversion": float(np.mean(inv_map)),
        }
        print(f"  ρ={rho}: fraction of (V, r) cells with α* < 1/N: "
              f"{100*np.mean(inv_map):.1f}% of {inv_map.size}")
        # All inversions should sit at V < 1/N=0.25 (sanity).
        n_cued_inv = int(np.sum(inv_map[V_grid_D >= 1.0 / N - 1e-9]))
        print(f"     of which at V ≥ 1/N: {n_cued_inv} (should be 0)")

    # ----------------------------------------------------------------
    # Recovery test #2 — reviewer derivation §5 Step C(i) numbers.
    # ----------------------------------------------------------------
    print()
    print("-" * 76)
    print("Recovery test #2 — reviewer Step C(i) table (V=0.25, v=1, N=4, variant A, ρ=0).")
    print("-" * 76)
    # From derivation §5 of Critique/derivations/C4--no-inversion.md:
    ref_step_Ci = [
        # (r,         alpha*,  R*)
        (0.10,        0.250,   0.62946),
        (1.00,        0.250,   0.62946),
        (1.585,       0.460,   0.63156),
        (2.512,       0.660,   0.63745),
        (3.981,       0.805,   0.64519),
        (10.00,       0.955,   0.65936),
    ]
    print(f"  {'r':>7s} {'α* ref':>7s} {'α* rebuild':>11s} {'Δα':>8s} "
          f"{'R* ref':>9s} {'R* rebuild':>11s} {'ΔR':>10s}")
    rb_step_Ci = []
    max_dalpha = 0.0
    max_dR = 0.0
    for r, alpha_ref, R_ref in ref_step_Ci:
        curve = er_curve_full(r, 0.25, 1.0, N, d_max, f0, h_name, "A", 0.0)
        d_alpha = curve["alpha_global"] - alpha_ref
        d_R = curve["R_global"] - R_ref
        max_dalpha = max(max_dalpha, abs(d_alpha))
        max_dR = max(max_dR, abs(d_R))
        rb_step_Ci.append({
            "r": float(r),
            "alpha_ref": alpha_ref, "alpha_rebuild": curve["alpha_global"],
            "delta_alpha": float(d_alpha),
            "R_ref": R_ref, "R_rebuild": curve["R_global"],
            "delta_R": float(d_R),
        })
        print(f"  {r:7.3f} {alpha_ref:7.3f} {curve['alpha_global']:11.3f} "
              f"{d_alpha:8.4f} {R_ref:9.5f} {curve['R_global']:11.5f} "
              f"{d_R:10.6f}")
    # Tolerance is set by the C_GRID discrepancy: reviewer's c-grid is
    # [-2.5, 2.5] step 0.05; rebuild's is [-3, 3] step 0.05 — extra range
    # may shift the optimum, but only for very high d', and the reference
    # cells are at low d' (d'_base ≈ 1.41 for these settings) so the
    # broader grid shouldn't matter.  Tolerance 5e-4 in α and 5e-5 in R.
    recovery_C_pass_alpha = max_dalpha < 5e-4
    recovery_C_pass_R = max_dR < 5e-5
    print(f"\n  Max |Δα|: {max_dalpha:.6f}  (tol 5e-4): "
          f"{'PASS' if recovery_C_pass_alpha else 'FAIL'}")
    print(f"  Max |ΔR|: {max_dR:.6f}  (tol 5e-5): "
          f"{'PASS' if recovery_C_pass_R else 'FAIL'}")

    # ----------------------------------------------------------------
    # FIGURES.
    # ----------------------------------------------------------------
    print()
    print("-" * 76)
    print("FIGURES.")
    print("-" * 76)

    # ---- Figure 1: E[R](α) at an anti-cue cell, multiple r, ρ overlay -----
    # Cell: V=0.15, v=1, N=4, variant A.  v=1 is the worst-case for the
    # value-weight inequality w_c >= w_u, which collapses to V >= 1/N at v=1.
    # At v > 1 the inversion onset shifts to V < 1/[(N-1)v+1] < 1/N, so v=1 is
    # the cleanest demonstration that anti-cue (V < 1/N) really does invert.
    fig1_cell = {"V": 0.15, "v": 1.0, "variant": "A"}
    fig1_rs = [0.5, 1.0, 3.0, 10.0]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), sharey=True)
    for ax, rho in zip(axes, [0.0, 0.2]):
        for r in fig1_rs:
            curve = er_curve_full(r, fig1_cell["V"], fig1_cell["v"], N, d_max, f0,
                                  h_name, fig1_cell["variant"], rho)
            ax.plot(curve["alpha_grid"], curve["Rs"], lw=1.5, label=f"$r = {r:g}$")
            ax.axvline(curve["alpha_global"], color=ax.get_lines()[-1].get_color(),
                       ls=":", lw=0.8, alpha=0.6)
        ax.axvline(1.0 / N, color="k", lw=1, alpha=0.4)
        ax.text(1.0 / N + 0.01, ax.get_ylim()[0] + 0.02, r"$\alpha = 1/N$",
                fontsize=8, color="k", alpha=0.6)
        ax.set_xlabel(r"$\alpha$ (allocation to cued)")
        ax.set_title(rf"$\rho = {rho}$")
        ax.set_xlim(0.0, 1.0)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", fontsize=8)
    axes[0].set_ylabel(r"$\mathbb{E}[R]$")
    fig.suptitle(
        rf"Anti-cue $\mathbb{{E}}[R](\alpha)$ at "
        rf"$V = {fig1_cell['V']} < 1/N = 0.25$, "
        rf"$v = {fig1_cell['v']:g}$, $N = 4$, variant A",
        fontsize=11)
    fig.tight_layout()
    p1 = fig_dir / "er_vs_alpha_anticue.png"
    fig.savefig(p1, dpi=150)
    plt.close(fig)
    print(f"  wrote {p1}")

    # ---- Figure 2: α*(V, r) heatmap, both ρ ----------
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), sharey=True)
    for ax, rho in zip(axes, [0.0, 0.2]):
        d = step_D[f"rho_{rho}"]
        alpha_map = np.array(d["alpha_map"])
        # Plot as imshow with V on y-axis, r on x-axis (log)
        # Use pcolormesh for log r grid.
        Vg = np.array(d["V_grid"])
        rg = np.array(d["r_grid"])
        # Build cell edges
        log_rg = np.log10(rg)
        log_edges = np.concatenate([
            [log_rg[0] - (log_rg[1] - log_rg[0]) / 2],
            (log_rg[:-1] + log_rg[1:]) / 2,
            [log_rg[-1] + (log_rg[-1] - log_rg[-2]) / 2],
        ])
        V_edges = np.concatenate([
            [Vg[0] - (Vg[1] - Vg[0]) / 2],
            (Vg[:-1] + Vg[1:]) / 2,
            [Vg[-1] + (Vg[-1] - Vg[-2]) / 2],
        ])
        rg_edges = 10 ** log_edges
        pcm = ax.pcolormesh(rg_edges, V_edges, alpha_map, cmap="viridis",
                            vmin=0.02, vmax=1.0, shading="flat")
        ax.set_xscale("log")
        ax.axhline(1.0 / N, color="white", lw=1.5, alpha=0.9)
        ax.text(0.12, 1.0 / N + 0.01, r"$V = 1/N$", color="white", fontsize=8,
                alpha=0.95)
        # Mark inversion cells (α* < 1/N) with hatching outline
        inv_map = np.array(d["inv_map"])
        # contour at boundary
        ax.contour(rg, Vg, inv_map, levels=[0.5], colors=["red"], linewidths=1.5)
        ax.set_xlabel("$r$")
        ax.set_title(rf"$\rho = {rho}$  (red contour: $\alpha^\star < 1/N$ region)")
        if ax is axes[0]:
            ax.set_ylabel("$V$ (validity)")
        ax.set_xlim(rg[0], rg[-1])
        ax.set_ylim(V_edges[0], V_edges[-1])
    cbar = fig.colorbar(pcm, ax=axes, shrink=0.85, pad=0.02)
    cbar.set_label(r"global $\alpha^\star$")
    fig.suptitle(
        rf"Global $\alpha^\star(V, r)$ at $v = 5$, $N = 4$, variant A — "
        rf"anti-cue inversion onset below $V = 1/N$",
        fontsize=11)
    p2 = fig_dir / "alpha_star_V_r_map.png"
    fig.savefig(p2, dpi=150)
    plt.close(fig)
    print(f"  wrote {p2}")

    # ---- Figure 3: r†_inv closed-form contour over (V, v) at ρ=0, variants A/B ---
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), sharey=True)
    # Build a dense grid for the contour.
    V_dense = np.linspace(0.05, 1.0, 49)
    v_dense = np.linspace(1.0, 10.0, 19)
    for ax, variant in zip(axes, ["A", "B"]):
        Z = np.full((len(V_dense), len(v_dense)), np.nan)
        for i, V in enumerate(V_dense):
            for j, v in enumerate(v_dense):
                t = r_inv_threshold(float(V), float(v), N, d_max, f0, h_name,
                                    variant, 0.0)
                Z[i, j] = float(t["r_inv_star"])
        Z_clipped = np.clip(Z, 0.05, 50.0)
        VV, vv = np.meshgrid(v_dense, V_dense)
        levels = [0.1, 0.3, 1.0, 3.0, 10.0]
        c = ax.contourf(VV, vv, np.log10(Z_clipped),
                        levels=np.log10([0.05, 0.1, 0.3, 1.0, 3.0, 10.0, 50.0]),
                        cmap="RdYlBu_r", alpha=0.85)
        cs = ax.contour(VV, vv, Z_clipped, levels=levels,
                        colors="black", linewidths=0.8)
        ax.clabel(cs, fmt="%g", fontsize=7)
        ax.axhline(1.0 / N, color="white", lw=1.2, alpha=0.9, ls="-")
        ax.text(9.5, 1.0 / N + 0.01, r"$V = 1/N$", color="white", fontsize=8,
                ha="right", alpha=0.95)
        ax.set_xlabel("$v$ (value)")
        ax.set_title(rf"variant {variant} ($\rho = 0$)")
        if ax is axes[0]:
            ax.set_ylabel("$V$ (validity)")
        ax.set_ylim(0.05, 1.0)
        ax.set_xlim(1.0, 10.0)
    cb = fig.colorbar(c, ax=axes, shrink=0.85, pad=0.02)
    cb.set_label(r"$\log_{10} r^\dagger_{\mathrm{inv}}$")
    fig.suptitle(
        rf"Closed-form local inversion threshold $r^\dagger_{{\mathrm{{inv}}}}(V, v; N=4, \rho=0)$",
        fontsize=11)
    p3 = fig_dir / "r_inv_closed_form.png"
    fig.savefig(p3, dpi=150)
    plt.close(fig)
    print(f"  wrote {p3}")

    # ----------------------------------------------------------------
    # Persist results.
    # ----------------------------------------------------------------
    elapsed = time.time() - t0

    out = {
        "meta": {
            "task_id": "RB-008",
            "run_id": "rb-012-2026-05-25",
            "prompt_version": "0.2",
            "claim_id": "C4",
            "headline_cell": {"N": N, "d_max": d_max, "f0": f0, "h": h_name},
            "alpha_grid": {
                "lo": float(ALPHA_GRID_FULL[0]),
                "hi": float(ALPHA_GRID_FULL[-1]),
                "step": 0.005,
                "n": int(len(ALPHA_GRID_FULL)),
            },
            "c_grid": {
                "lo": float(C_GRID[0]),
                "hi": float(C_GRID[-1]),
                "step": 0.05,
                "n": int(len(C_GRID)),
            },
            "Phi_backend": PHI_BACKEND,
            "GH_nq": int(len(_GH_Z)),
            "elapsed_seconds": round(elapsed, 2),
        },
        "step_A": {
            "rows": step_A_rows,
            "tally": step_A_tally,
            "recovery_rho0_pct_in_range": float(pct_rho0_in_range),
            "recovery_rho0_diff_pp": float(recovery_A_pct),
            "recovery_rho0_pass": bool(recovery_A_pass),
        },
        "step_B": {
            "r_test": float(r_test),
            "adversarial_cells": adversarial_cells,
            "rows": step_B_rows,
            "primary_inversion_count": int(primary_inversion_count),
        },
        "step_C": {
            "V_anticue": V_anticue,
            "v_anticue": v_anticue,
            "r_anticue": r_anticue,
            "rhos": rhos_C,
            "variant": variant_C,
            "rows": step_C_rows,
            "anticue_inversion_count_total": int(anticue_inversion_count),
            "anticue_inversion_count_rho0": int(anticue_inv_rho0),
            "anticue_inversion_count_rho02": int(anticue_inv_rho02),
            "incidence_by_r_rho0": r_inv_incidence,
        },
        "step_D": step_D,
        "recovery_step_Ci": {
            "rows": rb_step_Ci,
            "max_abs_delta_alpha": float(max_dalpha),
            "max_abs_delta_R": float(max_dR),
            "tol_alpha": 5e-4,
            "tol_R": 5e-5,
            "pass": bool(recovery_C_pass_alpha and recovery_C_pass_R),
        },
    }

    # Compute output sha256 of the hashable portion (everything except the
    # 'meta.elapsed_seconds' field, which is wall-clock dependent).
    hashable = {k: v for k, v in out.items() if k != "meta"}
    hashable["meta_static"] = {k: v for k, v in out["meta"].items()
                               if k != "elapsed_seconds"}
    sha = _digest(hashable)
    out["meta"]["output_sha256"] = sha

    res_path = out_dir / "results.json"
    with open(res_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\n  wrote {res_path}")
    print(f"  output sha256: {sha}")
    print(f"  elapsed: {elapsed:.1f} s")

    # ----------------------------------------------------------------
    # Verdict summary.
    # ----------------------------------------------------------------
    print()
    print("=" * 76)
    print("VERDICT SUMMARY (this sim's contribution to the C4 row of CLAIM_LEDGER)")
    print("=" * 76)
    print(f"  Step B primary-sweep inversions (V ≥ 1/N, r=10, both ρ): "
          f"{primary_inversion_count}")
    print(f"  Step C anti-cue inversions at N=4 (V < 1/N):")
    print(f"    ρ=0   : {anticue_inv_rho0} / {n_cells_C // 2}")
    print(f"    ρ=0.2 : {anticue_inv_rho02} / {n_cells_C // 2}")
    print(f"  Step D inversion cells at V ≥ 1/N (should be 0 at both ρ): "
          f"{int(np.sum(np.array(step_D['rho_0.0']['inv_map'])[V_grid_D >= 1.0/N - 1e-9]))}, "
          f"{int(np.sum(np.array(step_D['rho_0.2']['inv_map'])[V_grid_D >= 1.0/N - 1e-9]))}")
    print(f"  Recovery rho0 r†_inv 49% in [0.1, 10]: "
          f"{'PASS' if recovery_A_pass else 'FAIL'} "
          f"({pct_rho0_in_range:.1f}%)")
    print(f"  Recovery Step C(i) reviewer numbers: "
          f"{'PASS' if (recovery_C_pass_alpha and recovery_C_pass_R) else 'FAIL'}")
    print()


if __name__ == "__main__":
    main()
