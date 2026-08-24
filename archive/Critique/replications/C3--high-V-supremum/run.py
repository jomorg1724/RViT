"""
CR-026 — Re-derivation attack on C3b (high-V VDA negligibility).

Numerical companion to Critique/derivations/C3--high-V-supremum.md.

Claim under attack (paper §4.4, §5.2):
  "At V ≥ 0.75, optimal α* is near 1.0 and VDA is negligible
   (< 0.005 reward units) regardless of r." (§4.4)
  "Standard spatial cueing paradigms with high validity (V ≥ 0.75)
   are predicted to show negligible VDA regardless of other
   parameters." (§5.2)

What this script computes:
  sup_{r ∈ [0.1, 10],  v ∈ {1, 2, 3, 4, 5}} [R(P1) - R(P2)]
  at V = 0.75 with the paper's reference parameters
  (N = 4, d'_max = 2.0, f_0 = 0.5, h = sqrt, Variant A).

The decision rule per mission §3.1 + CR-026 task definition:
  sup < 0.005          → C3b is a theorem of the model →
                         C3 verdict elevates to CONFIRMED-CONDITIONAL.
  sup in [0.005, 0.020] → §5.2 categorical wording too strong →
                         verdict stays WEAKLY-SUPPORTED with
                         proposed weaker reformulation.
  sup > 0.020          → §4.4's "hot zone" boundary itself
                         crossed at V=0.75 → verdict moves to
                         CONTESTED.

Implementation notes:
  - Model is *identical* to Critique/replications/C2--non-monotonic-vda/run.py
    (CR-001). We re-implement here rather than importing to keep the
    replication file self-contained, per mission §5.4 convention.
  - α-grid: Δα = 0.01 (matches CR-001). A refinement pass at
    Δα = 0.005 (matches paper) is run around the empirical peak to
    rule out grid-resolution artefacts.
  - c-grid: Δc = 0.05 (matches paper, matches CR-001/CR-002).
  - For each (r, v) we compute R(P1) by jointly optimising
    (α, c_cued, c_uncued); R(P2) by fixing α at α*(v=1) and
    re-optimising (c_cued, c_uncued) at the operative v. This is the
    exact mission §2.5 policy decomposition.

NB: scipy is not assumed available (CR-001 sandbox lacked it). Phi
implemented via math.erf, vectorised over the c-grid.
"""

from __future__ import annotations

import math
import json
import os
from typing import Callable

import numpy as np


# ---------------------------------------------------------------
# Normal CDF.
# ---------------------------------------------------------------

_SQRT2 = math.sqrt(2.0)


def Phi(x):
    """Standard normal CDF. Vectorised via elementwise math.erf."""
    if np.isscalar(x):
        return 0.5 * (1.0 + math.erf(float(x) / _SQRT2))
    x_arr = np.asarray(x, dtype=float)
    out = np.empty_like(x_arr)
    flat = x_arr.ravel()
    flat_out = out.ravel()
    for i, xi in enumerate(flat):
        flat_out[i] = 0.5 * (1.0 + math.erf(float(xi) / _SQRT2))
    return out


# ---------------------------------------------------------------
# Model primitives (mission §2). Identical to CR-001 replication.
# ---------------------------------------------------------------

H_FORMS: dict[str, Callable] = {
    "sqrt": lambda a: np.sqrt(a),
    "linear": lambda a: a,
    "p0_3": lambda a: np.power(a, 0.3),
    "p2": lambda a: np.power(a, 2.0),
}


def f_transfer(a, f0: float, h: Callable):
    """f(a) = f_0 + (1 - f_0) * h(a). Mission §2.3."""
    return f0 + (1.0 - f0) * h(a)


def beta_gamma(r: float) -> tuple[float, float]:
    """beta(r) = 2r/(r+1); gamma(r) = 2/(r+1). Mission §2.4."""
    return 2.0 * r / (r + 1.0), 2.0 / (r + 1.0)


def d_prime_cued_uncued(alpha: float, r: float, d_max: float, f0: float,
                        h: Callable, N: int) -> tuple[float, float]:
    """
    Per-location d' at cued / (each) uncued location for allocation α.
    Mission §2.4 Eqs (7)-(8); clamped at ≥ 0.

    For α ≥ 1/N the cued gains (β-scaled) and uncued loses (γ-scaled).
    For α < 1/N the roles reverse (inversion branch).

    Defensive clamp on α: np.arange with non-integer step occasionally
    produces α = 1 + ε, which makes (1 - α)/(N-1) slightly negative and
    sqrt(neg) → NaN. We clip to [0, 1] up front so the analytic domain is
    respected; this does not perturb the physics because the model is
    defined for α ∈ [0, 1].
    """
    alpha = float(np.clip(alpha, 0.0, 1.0))
    beta, gamma = beta_gamma(r)
    d_base = d_max * f_transfer(1.0 / N, f0, h)
    if alpha >= 1.0 / N:
        d_c = d_base + beta * (d_max * f_transfer(alpha, f0, h) - d_base)
        d_u = d_base + gamma * (d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h) - d_base)
    else:
        d_c = d_base + gamma * (d_max * f_transfer(alpha, f0, h) - d_base)
        d_u = d_base + beta * (d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h) - d_base)
    return float(max(d_c, 0.0)), float(max(d_u, 0.0))


# ---------------------------------------------------------------
# Inner optimisation over (c_cued, c_uncued).
# ---------------------------------------------------------------

C_GRID = np.arange(-2.5, 2.5 + 1e-9, 0.05)


def optimal_criteria_R(d_c: float, d_u: float, v: float, V: float, N: int,
                       variant: str = "A") -> float:
    """
    Grid-search (c_c, c_u) over C_GRID × C_GRID; return max E[R].

    Variant A: CR = V*v + (1-V).  Variant B: CR = 1.
    """
    hr_c_grid = Phi(d_c / 2.0 - C_GRID)
    hr_u_grid = Phi(d_u / 2.0 - C_GRID)
    far_c_grid = Phi(-d_c / 2.0 - C_GRID)
    far_u_grid = Phi(-d_u / 2.0 - C_GRID)
    cr = V * v + (1.0 - V) if variant == "A" else 1.0
    p_no_fa = (1.0 - far_c_grid)[:, None] * ((1.0 - far_u_grid) ** (N - 1))[None, :]
    er = 0.5 * (V * hr_c_grid[:, None] * v + (1.0 - V) * hr_u_grid[None, :]) \
       + 0.5 * p_no_fa * cr
    return float(er.max())


# ---------------------------------------------------------------
# Policy decomposition at one (r, v).
# ---------------------------------------------------------------

def policy_rewards(v: float, V: float, N: int, d_max: float, f0: float,
                   h: Callable, r: float, variant: str = "A",
                   alpha_grid: np.ndarray | None = None) -> dict:
    """
    R(P1), R(P2), R(P3), R(P4) at given (v, V, r, ...).

    P1: jointly optimise (α, c_c, c_u).
    P2: α fixed at α*(v=1); criteria re-optimised at operative v.
    P3: α = 1/N; criteria optimised.
    P4: α = 1/N AND c = 0 at both.
    """
    if alpha_grid is None:
        alpha_grid = np.arange(0.02, 1.0 + 1e-9, 0.01)

    # Precompute (d_c, d_u) per α (depends on r, not on v).
    d_pairs = [d_prime_cued_uncued(float(a), r, d_max, f0, h, N) for a in alpha_grid]

    # P3, P4
    alpha_uniform = 1.0 / N
    d_c_u, d_u_u = d_prime_cued_uncued(alpha_uniform, r, d_max, f0, h, N)
    r_p3 = optimal_criteria_R(d_c_u, d_u_u, v, V, N, variant)
    hr = Phi(d_c_u / 2.0 - 0.0)
    far = Phi(-d_c_u / 2.0 - 0.0)
    cr = V * v + (1.0 - V) if variant == "A" else 1.0
    r_p4 = 0.5 * (V * hr * v + (1.0 - V) * hr) + 0.5 * (1.0 - far) ** N * cr

    # P1: jointly optimise α + criteria at operative v.
    rs_p1 = np.array([optimal_criteria_R(dc, du, v, V, N, variant)
                      for dc, du in d_pairs])
    idx_p1 = int(np.argmax(rs_p1))
    alpha_p1 = float(alpha_grid[idx_p1])
    r_p1 = float(rs_p1[idx_p1])

    # P2: α fixed at α*(v=1), criteria re-optimised at operative v.
    rs_p2_v1 = np.array([optimal_criteria_R(dc, du, 1.0, V, N, variant)
                         for dc, du in d_pairs])
    alpha_p2 = float(alpha_grid[int(np.argmax(rs_p2_v1))])
    dc_p2, du_p2 = d_prime_cued_uncued(alpha_p2, r, d_max, f0, h, N)
    r_p2 = optimal_criteria_R(dc_p2, du_p2, v, V, N, variant)

    return {
        "r": r, "v": v,
        "alpha_p1": alpha_p1, "alpha_p2": alpha_p2,
        "R_p1": r_p1, "R_p2": r_p2, "R_p3": r_p3, "R_p4": r_p4,
        "VDA": r_p1 - r_p2,
        "criterion_gain": r_p3 - r_p4,
        "validity_attention_gain": r_p2 - r_p3,
        "criterion_fraction": (r_p3 - r_p4) / max(r_p1 - r_p4, 1e-12),
    }


# ---------------------------------------------------------------
# Main: sweep (r, v) at V = 0.75; locate sup VDA.
# ---------------------------------------------------------------

def main():
    # Paper's reference regime at high V.
    N = 4
    d_max = 2.0
    f0 = 0.5
    h_name = "sqrt"
    h = H_FORMS[h_name]
    V = 0.75
    variant = "A"

    # Grid: r matches paper's primary log-spaced [0.1, 10] × 21 pts;
    # v matches paper's primary linear {1, 2, 3, 4, 5}.
    r_grid = np.logspace(np.log10(0.1), np.log10(10.0), 21)
    v_grid = [1.0, 2.0, 3.0, 4.0, 5.0]

    print("CR-026  C3 high-V supremum  V=0.75  N=4  d'_max=2  f0=0.5  h=sqrt  Variant A")
    print(f"r-grid: {len(r_grid)} log-pts in [0.1, 10]")
    print(f"v-grid: {v_grid}")
    print()
    print(f"{'r':>8s}  {'v':>3s}  {'αP1':>6s}  {'αP2':>6s}  {'R(P1)':>8s}  {'R(P2)':>8s}  {'VDA':>8s}  {'CF':>5s}")
    print("-" * 70)

    rows = []
    for v in v_grid:
        for r in r_grid:
            row = policy_rewards(v, V, N, d_max, f0, h, float(r), variant)
            rows.append(row)
            print(f"{r:8.4f}  {int(v):3d}  {row['alpha_p1']:6.3f}  {row['alpha_p2']:6.3f}  "
                  f"{row['R_p1']:8.5f}  {row['R_p2']:8.5f}  {row['VDA']:8.5f}  "
                  f"{row['criterion_fraction']:5.3f}")
        print()

    # Locate sup VDA across the (r, v) grid.
    vdas = np.array([row["VDA"] for row in rows])
    idx = int(np.argmax(vdas))
    sup_vda = float(vdas[idx])
    sup_r = rows[idx]["r"]
    sup_v = rows[idx]["v"]

    print()
    print(f"sup_{{r,v}} VDA = {sup_vda:.5f}  at  (r={sup_r:.4f}, v={sup_v})")
    print()
    print(f"Decision per CR-026 task definition:")
    if sup_vda < 0.005:
        verdict_movement = "C3b is a THEOREM of the model (sup < paper's 0.005 'negligible' threshold)."
        verdict_label = "CONFIRMED-CONDITIONAL"
    elif sup_vda < 0.020:
        verdict_movement = ("§5.2 categorical wording too strong; sup in [0.005, 0.020]. "
                            "Weaker reformulation operational; verdict stays WEAKLY-SUPPORTED.")
        verdict_label = "WEAKLY-SUPPORTED"
    else:
        verdict_movement = ("§5.2 wording wrong internal to the model; sup > 0.020 "
                            "(crosses §4.4's hot-zone boundary at V=0.75).")
        verdict_label = "CONTESTED"
    print(f"  → {verdict_label}")
    print(f"  → {verdict_movement}")

    # Refinement pass at the empirical peak: Δα = 0.005, Δc = 0.025.
    # This is to rule out grid-resolution artefacts at the sup.
    refine_alpha = np.arange(0.02, 1.0 + 1e-9, 0.005)
    refine_C = np.arange(-2.5, 2.5 + 1e-9, 0.025)

    print()
    print(f"Refinement pass at (r={sup_r:.4f}, v={sup_v}) with Δα=0.005, Δc=0.025:")
    # Override global C_GRID for this measurement only.
    global C_GRID
    saved = C_GRID
    C_GRID = refine_C
    refined = policy_rewards(sup_v, V, N, d_max, f0, h, float(sup_r), variant, alpha_grid=refine_alpha)
    C_GRID = saved
    print(f"  refined α*P1 = {refined['alpha_p1']:.4f}")
    print(f"  refined α*P2 = {refined['alpha_p2']:.4f}")
    print(f"  refined R(P1) = {refined['R_p1']:.6f}")
    print(f"  refined R(P2) = {refined['R_p2']:.6f}")
    print(f"  refined VDA   = {refined['VDA']:.6f}  (coarse: {sup_vda:.6f})")
    print(f"  refined CF    = {refined['criterion_fraction']:.4f}")

    # Comparison row: V = 0.5 at the same (r, v) — the well-known "hot zone".
    print()
    print("Comparison: same (r, v) at V = 0.5 (the paper's reference 'hot zone'):")
    cmp_row = policy_rewards(sup_v, 0.5, N, d_max, f0, h, float(sup_r), variant)
    print(f"  V=0.50: αP1={cmp_row['alpha_p1']:.3f}  αP2={cmp_row['alpha_p2']:.3f}  "
          f"R(P1)={cmp_row['R_p1']:.5f}  R(P2)={cmp_row['R_p2']:.5f}  "
          f"VDA={cmp_row['VDA']:.5f}  CF={cmp_row['criterion_fraction']:.3f}")
    print(f"  V=0.75: αP1={refined['alpha_p1']:.3f}  αP2={refined['alpha_p2']:.3f}  "
          f"R(P1)={refined['R_p1']:.5f}  R(P2)={refined['R_p2']:.5f}  "
          f"VDA={refined['VDA']:.5f}  CF={refined['criterion_fraction']:.3f}")
    ratio = refined['VDA'] / max(cmp_row['VDA'], 1e-12)
    print(f"  VDA ratio V=0.75 / V=0.5 = {ratio:.4f}")

    # Also probe V = 0.75 ± 0.01 to confirm the V=0.75 boundary is not a knife-edge.
    print()
    print("Boundary check: sup VDA at V ∈ {0.75, 0.80, 0.90, 0.95}:")
    boundary_coarse = {}
    for V_try in [0.75, 0.80, 0.90, 0.95]:
        max_vda = 0.0
        max_loc = (None, None)
        for v_try in v_grid:
            for r_try in r_grid:
                rrow = policy_rewards(v_try, V_try, N, d_max, f0, h, float(r_try), variant)
                if rrow["VDA"] > max_vda:
                    max_vda = rrow["VDA"]
                    max_loc = (rrow["r"], rrow["v"])
        print(f"  V={V_try:.2f}:  sup VDA = {max_vda:.5f}  at (r={max_loc[0]:.4f}, v={max_loc[1]})")
        boundary_coarse[V_try] = {"sup_vda": max_vda,
                                   "at_r": max_loc[0], "at_v": max_loc[1]}

    # Fine V-grid in [0.75, 0.80] to locate V_critical(r=0.1, v=5).
    print()
    print("Fine V-grid in [0.75, 0.80]  at (r=0.1, v=5)  to locate V_critical:")
    V_fine = np.arange(0.75, 0.805, 0.005)
    boundary_fine = []
    for V_try in V_fine:
        rrow = policy_rewards(5.0, float(V_try), N, d_max, f0, h, 0.1, variant)
        print(f"  V={V_try:.3f}:  αP1={rrow['alpha_p1']:.3f}  αP2={rrow['alpha_p2']:.3f}  "
              f"R(P1)={rrow['R_p1']:.5f}  R(P2)={rrow['R_p2']:.5f}  "
              f"VDA={rrow['VDA']:.5f}")
        boundary_fine.append({"V": float(V_try),
                              "alpha_p1": rrow["alpha_p1"],
                              "alpha_p2": rrow["alpha_p2"],
                              "VDA": rrow["VDA"]})

    # Sub-coarse r-grid in [0.05, 0.20] at (V=0.75, v=5) to verify sup is at the
    # paper's r-grid corner r=0.1 and not at smaller r.
    print()
    print("Fine r-grid in [0.05, 0.20]  at (V=0.75, v=5)  to verify sup is interior:")
    r_fine = np.array([0.05, 0.063, 0.079, 0.10, 0.126, 0.158, 0.20])
    r_below_grid = []
    for r_try in r_fine:
        rrow = policy_rewards(5.0, 0.75, N, d_max, f0, h, float(r_try), variant)
        print(f"  r={r_try:.4f}:  αP1={rrow['alpha_p1']:.3f}  αP2={rrow['alpha_p2']:.3f}  "
              f"R(P1)={rrow['R_p1']:.5f}  R(P2)={rrow['R_p2']:.5f}  "
              f"VDA={rrow['VDA']:.5f}")
        r_below_grid.append({"r": float(r_try),
                             "alpha_p1": rrow["alpha_p1"],
                             "alpha_p2": rrow["alpha_p2"],
                             "VDA": rrow["VDA"]})

    # Save results.
    os.makedirs("output", exist_ok=True)
    with open("output/sup_vda_at_V075.json", "w") as fh:
        json.dump({
            "rows": rows,
            "sup_vda_coarse": sup_vda,
            "sup_at": {"r": sup_r, "v": sup_v},
            "sup_vda_refined": float(refined["VDA"]),
            "refined_alpha_p1": float(refined["alpha_p1"]),
            "refined_alpha_p2": float(refined["alpha_p2"]),
            "comparison_V05_at_sup_loc": cmp_row,
            "boundary_coarse": boundary_coarse,
            "boundary_fine_V": boundary_fine,
            "r_below_grid": r_below_grid,
            "paper_negligible_threshold": 0.005,
            "paper_hot_zone_threshold": 0.020,
            "verdict_label": verdict_label,
            "regime": {"N": N, "d_max": d_max, "f0": f0, "h": h_name,
                       "V": V, "variant": variant}
        }, fh, indent=2)


if __name__ == "__main__":
    main()
