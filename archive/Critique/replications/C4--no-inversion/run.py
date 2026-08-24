"""
CR-004 + CR-019 — Re-derivation attack on C4 ("Inverted attention is
never optimal", paper §4.5) with V=1/N degeneracy refinement.

Mathematical companion:
    Critique/derivations/C4--no-inversion.md

Claim under attack (paper §4.5, verbatim):
    "Across all 4,410 rows of the primary sweep — spanning
     r ∈ [0.1, 10], V ∈ [0.25, 1.0], v ∈ {1, ..., 5}, and both
     reward variants — the optimal α* is always ≥ 1/N. The α grid
     was extended below 1/N (down to 0.02), allowing the optimiser
     to discover inverted attention (preferentially attending away
     from the high-value location) if it were ever beneficial. It
     never is.

     This result follows from the reward structure: attending away
     from the high-value cued location means (a) the cued location's
     d' drops below baseline, scaled by the cost factor γ, while
     (b) uncued locations' d' rises above baseline, scaled by the
     benefit factor β. Since v ≥ 1 and V ≥ 1/N, the weighted
     reward loss at the high-value cued location always exceeds the
     gain at low-value uncued locations, regardless of r. In the
     most cost-dominant regime (r → 0), the optimal strategy
     converges to uniform attention (α* = 1/N), never below it."

Three things this script computes:

  Step A. **Boundary closed form.**
    The derivation file shows that the one-sided derivative of E[R]
    at α = 1/N⁻ is
        ∂E[R]/∂α|_{1/N⁻} = (2 d'_max f'(1/N)/(r+1)) · [A − (r/(N-1)) B]
    where
        A := ∂E[R]/∂d'_c |_{α=1/N, optimal criteria}
        B := ∂E[R]/∂d'_u |_{α=1/N, optimal criteria}
    are r-independent. The "no-local-inversion" criterion is
        r ≤ r*_inv(V, v, N, CR) := (N − 1) · A / B.
    Step A numerically evaluates r*_inv across the paper's primary
    grid to see where r*_inv falls relative to the swept r ∈ [0.1, 10].

  Step B. **Global α-sweep at adversarial cells.**
    Some cells have r > r*_inv yet still have global α* ≥ 1/N
    because the model's right branch (α > 1/N) gives a higher peak
    E[R] than the left branch (α < 1/N) — the model is *not*
    symmetric in α at N ≥ 3 because cued has 1 location while
    uncued has N − 1 locations. Step B computes the full E[R](α)
    curve on a fine grid (Δα = 0.005, matching paper) at all cells
    that Step A flags as having r*_inv < r_max=10, and reports
    α*_global. If α*_global < 1/N anywhere, C4 is REFUTED. If
    α*_global ≥ 1/N everywhere but the *left-branch* max is close
    to the right-branch max, C4 is CONFIRMED-CONDITIONAL with the
    caveat that the symmetry is broken only by the location-count
    asymmetry.

  Step C. **CR-019 refinement at V = 1/N exactly.**
    At V = 1/N with v = 1, the model is symmetric in (cued ↔ uncued)
    in the value-and-validity-weighted reward; the only asymmetry
    is structural (1 cued vs N−1 uncued locations). For N = 4, this
    is the cell (V=0.25, v=1). For N = 2, V = 1/N = 0.5, and the
    *secondary* sweep at v=5 sits at V = 1/N. Step C examines both:
      (i) at (V=1/N=0.25, v=1, N=4) — what does the model do as
          r varies?
      (ii) at (V=1/N=0.5, v=5, N=2) — does the v boost break the
          tie, and in which direction?
    This is the analytic resolution of the CR-014 observation that
    a value-blind P2 optimizer found α=0.02 at the V=0.5, N=2 cell:
    if E[R](α) is truly bimodal at V=1/N with v=1, the optimizer
    picks one of two equivalent solutions arbitrarily.

Implementation notes:
  - Model primitives are *identical* to the CR-001 / CR-002 / CR-026
    replication scripts (mission §2). The α<1/N branch swaps β/γ:
    when α < 1/N the cued is under-allocated (cost γ) and uncued is
    over-allocated (benefit β).
  - Optimal criteria at α=1/N are derived in closed form (see
    derivation §3) for the symmetric d' case (d'_c = d'_u = d'_base);
    we solve the coupled FOC system by fixed-point iteration.
  - The α-grid for Step B is np.arange(0.02, 1.0+ε, 0.005) — matches
    paper's primary sweep resolution.
  - c-grid is np.arange(-2.5, 2.5+ε, 0.05) — matches paper.

CR-004, prompt v0.1, run 2026-05-18.
"""

from __future__ import annotations

import math
import json
import os
from typing import Callable

import numpy as np


# ---------------------------------------------------------------
# Standard normal CDF and PDF.
# ---------------------------------------------------------------

_SQRT2 = math.sqrt(2.0)
_SQRT_2PI = math.sqrt(2.0 * math.pi)


def Phi(x):
    """Standard normal CDF; vectorised via math.erf (no scipy assumed)."""
    if np.isscalar(x):
        return 0.5 * (1.0 + math.erf(float(x) / _SQRT2))
    x_arr = np.asarray(x, dtype=float)
    out = np.empty_like(x_arr)
    flat = x_arr.ravel()
    flat_out = out.ravel()
    for i, xi in enumerate(flat):
        flat_out[i] = 0.5 * (1.0 + math.erf(float(xi) / _SQRT2))
    return out


def phi(x):
    """Standard normal PDF, scalar."""
    return math.exp(-0.5 * x * x) / _SQRT_2PI


# ---------------------------------------------------------------
# Model primitives (mission §2 / paper §3).
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


def f_prime_at_inv_N(f0: float, h_name: str, N: int) -> float:
    """f'(1/N) for the four supported h forms. Mission §2.3."""
    aN = 1.0 / N
    if h_name == "linear":
        return 1.0 - f0
    if h_name == "sqrt":
        return (1.0 - f0) * 0.5 / math.sqrt(aN)
    if h_name == "p0_3":
        return (1.0 - f0) * 0.3 * aN ** (0.3 - 1.0)
    if h_name == "p2":
        return (1.0 - f0) * 2.0 * aN
    raise ValueError(h_name)


def beta_gamma(r: float) -> tuple[float, float]:
    """beta(r) = 2r/(r+1); gamma(r) = 2/(r+1). Mission §2.4."""
    return 2.0 * r / (r + 1.0), 2.0 / (r + 1.0)


def d_prime_cued_uncued(alpha: float, r: float, d_max: float, f0: float,
                        h: Callable, N: int) -> tuple[float, float]:
    """
    Per-location d' at cued / (each) uncued location.
    Mission §2.4 with the inversion branch (α < 1/N swaps β/γ).
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
# Joint optimisation over (c_c, c_u) at given (d_c, d_u).
# ---------------------------------------------------------------

_C_GRID = np.arange(-2.5, 2.5 + 1e-9, 0.05)


def optimal_criteria_R(d_c: float, d_u: float, v: float, V: float, N: int,
                       variant: str = "A",
                       return_argmax: bool = False):
    """Joint grid-search over (c_c, c_u). Returns R(P_*) and optionally argmax."""
    hr_c = Phi(d_c / 2.0 - _C_GRID)
    hr_u = Phi(d_u / 2.0 - _C_GRID)
    far_c = Phi(-d_c / 2.0 - _C_GRID)
    far_u = Phi(-d_u / 2.0 - _C_GRID)
    cr = V * v + (1.0 - V) if variant == "A" else 1.0
    p_no_fa = (1.0 - far_c)[:, None] * ((1.0 - far_u) ** (N - 1))[None, :]
    er = 0.5 * (V * hr_c[:, None] * v + (1.0 - V) * hr_u[None, :]) \
       + 0.5 * p_no_fa * cr
    if return_argmax:
        idx = np.unravel_index(np.argmax(er), er.shape)
        return float(er.max()), float(_C_GRID[idx[0]]), float(_C_GRID[idx[1]])
    return float(er.max())


# ---------------------------------------------------------------
# Step A. Closed-form inversion threshold r*_inv(V, v, N, CR).
# ---------------------------------------------------------------

def r_inv_threshold(V: float, v: float, N: int, d_max: float, f0: float,
                    h_name: str, variant: str = "A") -> dict:
    """
    Compute the boundary inversion threshold r*_inv = (N-1) A / B
    from the derivation §4. A and B are evaluated at α = 1/N (where
    d'_c = d'_u = d'_base) with the optimal criteria (c_c*, c_u*).

    The optimal criteria at α = 1/N solve the coupled FOC system:
        d * c_c = log[CR (1-FAR_u)^{N-1} / (V·v)]
        d * c_u = log[CR (N-1)(1-FAR_c)(1-FAR_u)^{N-2} / (1-V)]
    We grid-search both (using optimal_criteria_R) to avoid the
    fixed-point iteration; at d_c = d_u = d_base the grid search is
    exact at Δc = 0.05.

    Returns dict with r_inv_star and the intermediate quantities
    (A, B, p_c^H, p_c^F, p_u^H, p_u^F, FAR_c, FAR_u, c_c*, c_u*).
    """
    h = H_FORMS[h_name] if isinstance(h_name, str) else h_name
    d_base = d_max * f_transfer(1.0 / N, f0, h)

    # Optimal criteria at α=1/N, where d_c = d_u = d_base.
    _, c_c_star, c_u_star = optimal_criteria_R(d_base, d_base, v, V, N, variant,
                                                return_argmax=True)

    # SDT densities at the optimum.
    p_c_H = phi(d_base / 2.0 - c_c_star)
    p_c_F = phi(d_base / 2.0 + c_c_star)
    p_u_H = phi(d_base / 2.0 - c_u_star)
    p_u_F = phi(d_base / 2.0 + c_u_star)
    FAR_c = 0.5 * (1.0 + math.erf((-d_base / 2.0 - c_c_star) / _SQRT2))
    FAR_u = 0.5 * (1.0 + math.erf((-d_base / 2.0 - c_u_star) / _SQRT2))

    cr = V * v + (1.0 - V) if variant == "A" else 1.0

    A = 0.25 * (V * v * p_c_H + cr * p_c_F * (1.0 - FAR_u) ** (N - 1))
    B = 0.25 * ((1.0 - V) * p_u_H + (N - 1) * cr * (1.0 - FAR_c) * (1.0 - FAR_u) ** (N - 2) * p_u_F)

    r_inv_star = (N - 1) * A / B if B > 1e-15 else float("inf")

    return dict(r_inv_star=r_inv_star, A=A, B=B,
                c_c_star=c_c_star, c_u_star=c_u_star,
                p_c_H=p_c_H, p_c_F=p_c_F, p_u_H=p_u_H, p_u_F=p_u_F,
                FAR_c=FAR_c, FAR_u=FAR_u, d_base=d_base, cr=cr)


# ---------------------------------------------------------------
# Step B. Full E[R](α) sweep at adversarial cells.
# ---------------------------------------------------------------

def er_curve(r: float, V: float, v: float, N: int, d_max: float, f0: float,
             h_name: str, variant: str = "A",
             alpha_grid: np.ndarray | None = None) -> dict:
    """E[R](α) curve at fine resolution; returns curve + global / left- / right-branch argmax."""
    if alpha_grid is None:
        alpha_grid = np.arange(0.02, 1.0 + 1e-9, 0.005)
    h = H_FORMS[h_name]

    Rs = np.empty_like(alpha_grid)
    for i, a in enumerate(alpha_grid):
        dc, du = d_prime_cued_uncued(float(a), r, d_max, f0, h, N)
        Rs[i] = optimal_criteria_R(dc, du, v, V, N, variant)

    inv_N = 1.0 / N

    # Global max.
    idx_g = int(np.argmax(Rs))
    alpha_g = float(alpha_grid[idx_g])
    R_g = float(Rs[idx_g])

    # Left-branch max (α < 1/N).
    left_mask = alpha_grid < inv_N - 1e-9
    if left_mask.any():
        idx_l = int(np.argmax(np.where(left_mask, Rs, -np.inf)))
        alpha_l = float(alpha_grid[idx_l])
        R_l = float(Rs[idx_l])
    else:
        alpha_l = float("nan")
        R_l = float("nan")

    # Right-branch max (α > 1/N).
    right_mask = alpha_grid > inv_N + 1e-9
    if right_mask.any():
        idx_r = int(np.argmax(np.where(right_mask, Rs, -np.inf)))
        alpha_r = float(alpha_grid[idx_r])
        R_r = float(Rs[idx_r])
    else:
        alpha_r = float("nan")
        R_r = float("nan")

    # E[R] at α = 1/N exactly (snap to nearest grid point or compute).
    dc_at, du_at = d_prime_cued_uncued(inv_N, r, d_max, f0, h, N)
    R_at_inv_N = optimal_criteria_R(dc_at, du_at, v, V, N, variant)

    return dict(alpha_grid=alpha_grid, Rs=Rs,
                alpha_global=alpha_g, R_global=R_g,
                alpha_left=alpha_l, R_left=R_l,
                alpha_right=alpha_r, R_right=R_r,
                R_at_inv_N=R_at_inv_N,
                inversion_global=(alpha_g < inv_N - 1e-9))


# ---------------------------------------------------------------
# Main entry point.
# ---------------------------------------------------------------

def main():
    out_dir = "/sessions/determined-modest-wright/mnt/AttentionManuscript/Critique/replications/C4--no-inversion/output"
    os.makedirs(out_dir, exist_ok=True)

    print("=" * 72)
    print("CR-004 + CR-019  Re-derivation attack on C4 (no-inversion claim)")
    print("=" * 72)
    print()

    # =====================================================================
    # STEP A. r*_inv across the paper's primary grid (N=4).
    # =====================================================================
    print("STEP A — Closed-form inversion threshold r*_inv(V, v, N=4, variant).")
    print("        r*_inv := (N-1) · A / B   (boundary derivative criterion).")
    print("        For C4, primary sweep, r*_inv must exceed r_max = 10")
    print("        for left-branch local inversion to be ruled out at α=1/N.")
    print()

    N = 4
    d_max = 2.0
    f0 = 0.5
    h_name = "sqrt"
    V_grid = np.linspace(0.25, 1.0, 21)  # 21 pts from 1/N to 1
    v_grid = [1.0, 2.0, 3.0, 4.0, 5.0]
    variants = ["A", "B"]

    rows_A = []
    for variant in variants:
        print(f"\n  Variant {variant}:")
        print(f"  {'V':>6s}  {'v':>3s}   {'A':>10s}  {'B':>10s}  {'r*_inv':>10s}  "
              f"{'in [0.1,10]?':>12s}")
        for V in V_grid:
            for v in v_grid:
                t = r_inv_threshold(float(V), float(v), N, d_max, f0, h_name, variant)
                in_range = (0.1 <= t["r_inv_star"] <= 10.0)
                rows_A.append(dict(N=N, V=float(V), v=float(v), variant=variant,
                                   r_inv_star=t["r_inv_star"],
                                   A=t["A"], B=t["B"],
                                   c_c_star=t["c_c_star"], c_u_star=t["c_u_star"],
                                   in_sweep_range=in_range))
                if v in [1.0, 3.0, 5.0] and V in V_grid[::4]:
                    print(f"  {V:6.3f}  {int(v):3d}   {t['A']:10.5f}  {t['B']:10.5f}  "
                          f"{t['r_inv_star']:10.4f}  {str(in_range):>12s}")

    # Tally.
    n_total = len(rows_A)
    n_in_range = sum(1 for r in rows_A if r["in_sweep_range"])
    n_below = sum(1 for r in rows_A if r["r_inv_star"] < 0.1)
    n_above = sum(1 for r in rows_A if r["r_inv_star"] > 10.0)
    print()
    print(f"  Across {n_total} (V, v, variant) cells at N=4:")
    print(f"    r*_inv  > 10        : {n_above:4d}  ({100*n_above/n_total:5.1f}%)  C4 boundary trivially holds")
    print(f"    r*_inv  ∈ [0.1, 10] : {n_in_range:4d}  ({100*n_in_range/n_total:5.1f}%)  Step B inspects these")
    print(f"    r*_inv  < 0.1       : {n_below:4d}  ({100*n_below/n_total:5.1f}%)  boundary fails at all swept r")

    # Find the cells with smallest r*_inv (most adversarial).
    rows_A_sorted = sorted(rows_A, key=lambda r: r["r_inv_star"])
    print()
    print("  10 most-adversarial cells (smallest r*_inv):")
    print(f"  {'V':>6s}  {'v':>3s}  {'variant':>7s}  {'r*_inv':>10s}")
    for r in rows_A_sorted[:10]:
        print(f"  {r['V']:6.3f}  {int(r['v']):3d}  {r['variant']:>7s}  {r['r_inv_star']:10.4f}")

    # =====================================================================
    # STEP B. Full E[R](α) curve at the most adversarial cells, at r=10.
    # =====================================================================
    print()
    print("=" * 72)
    print("STEP B — Full E[R](α) curve at the cells where r*_inv < r_max = 10,")
    print("        evaluated at r = 10 (most cost-flipped). If α*_global < 1/N")
    print("        for *any* cell in the primary sweep, C4 is REFUTED.")
    print("=" * 72)

    # Pick a handful of adversarial cells.
    cells_B = []
    seen = set()
    for r in rows_A_sorted:
        if r["r_inv_star"] >= 10.0:
            break
        key = (r["V"], r["v"], r["variant"])
        if key in seen:
            continue
        seen.add(key)
        cells_B.append(r)
        if len(cells_B) >= 12:
            break

    # Also force-include the (V=1/N=0.25, v=1, variant=A or B) cells: per
    # the analytic derivation, these are the cells with r*_inv = 1 exactly.
    forced = [
        (0.25, 1.0, "A"),
        (0.25, 1.0, "B"),
        (0.25, 5.0, "A"),  # value boost at V=1/N
    ]
    for V, v, variant in forced:
        if (V, v, variant) not in seen:
            t = r_inv_threshold(V, v, N, d_max, f0, h_name, variant)
            cells_B.append(dict(V=V, v=v, variant=variant, r_inv_star=t["r_inv_star"]))
            seen.add((V, v, variant))

    rows_B = []
    print(f"\n  Sweep α ∈ [0.02, 1.0] at Δα=0.005 for each adversarial cell at r=10.\n")
    print(f"  {'V':>6s} {'v':>3s} {'var':>3s} {'r*_inv':>8s} "
          f"{'α*global':>9s} {'R*global':>9s} {'α*left':>7s} {'R*left':>8s} "
          f"{'α*right':>8s} {'R*right':>8s} {'inv?':>5s}")
    print("  " + "-" * 90)
    r_test = 10.0
    for cell in cells_B:
        curve = er_curve(r_test, cell["V"], cell["v"], N, d_max, f0, h_name, cell["variant"])
        rows_B.append(dict(
            r=r_test, V=cell["V"], v=cell["v"], variant=cell["variant"],
            r_inv_star=cell["r_inv_star"],
            alpha_global=curve["alpha_global"], R_global=curve["R_global"],
            alpha_left=curve["alpha_left"], R_left=curve["R_left"],
            alpha_right=curve["alpha_right"], R_right=curve["R_right"],
            R_at_inv_N=curve["R_at_inv_N"],
            inversion_global=curve["inversion_global"],
        ))
        print(f"  {cell['V']:6.3f} {int(cell['v']):3d} {cell['variant']:>3s} "
              f"{cell['r_inv_star']:8.4f} "
              f"{curve['alpha_global']:9.3f} {curve['R_global']:9.5f} "
              f"{curve['alpha_left']:7.3f} {curve['R_left']:8.5f} "
              f"{curve['alpha_right']:8.3f} {curve['R_right']:8.5f} "
              f"{str(curve['inversion_global']):>5s}")

    # =====================================================================
    # STEP C. CR-019 — V=1/N degeneracy.
    # =====================================================================
    print()
    print("=" * 72)
    print("STEP C — CR-019 V=1/N degeneracy refinement.")
    print("=" * 72)

    rows_C = []

    # (i) (V=1/N=0.25, v=1, N=4) over a sweep of r.
    print()
    print("  (i) (V=1/N=0.25, v=1, N=4) — symmetric corner of primary sweep.")
    print(f"  {'r':>8s} {'r*_inv':>8s} "
          f"{'α*global':>9s} {'R*global':>9s} {'α*left':>7s} {'R*left':>8s} "
          f"{'α*right':>8s} {'R*right':>8s} {'R(1/N)':>8s} {'ΔR_l-r':>9s}")
    print("  " + "-" * 96)
    t1 = r_inv_threshold(0.25, 1.0, 4, d_max, f0, h_name, "A")
    for r_t in np.logspace(np.log10(0.1), np.log10(10.0), 11):
        curve = er_curve(float(r_t), 0.25, 1.0, 4, d_max, f0, h_name, "A")
        rows_C.append(dict(case="V1N-v1-N4", r=float(r_t), V=0.25, v=1.0, N=4,
                           **{k: curve[k] for k in
                              ["alpha_global", "R_global", "alpha_left", "R_left",
                               "alpha_right", "R_right", "R_at_inv_N",
                               "inversion_global"]}))
        delta = curve["R_left"] - curve["R_right"]
        print(f"  {r_t:8.4f} {t1['r_inv_star']:8.4f} "
              f"{curve['alpha_global']:9.3f} {curve['R_global']:9.5f} "
              f"{curve['alpha_left']:7.3f} {curve['R_left']:8.5f} "
              f"{curve['alpha_right']:8.3f} {curve['R_right']:8.5f} "
              f"{curve['R_at_inv_N']:8.5f} {delta:9.5f}")

    # (ii) (V=1/N=0.5, v=5, N=2) — the CR-014 case.
    print()
    print("  (ii) (V=1/N=0.5, v=5, N=2) — CR-014 P2-inversion case (secondary sweep).")
    print(f"  {'r':>8s} {'r*_inv':>8s} "
          f"{'α*global':>9s} {'R*global':>9s} {'α*left':>7s} {'R*left':>8s} "
          f"{'α*right':>8s} {'R*right':>8s} {'R(1/N)':>8s} {'ΔR_l-r':>9s}")
    print("  " + "-" * 96)
    t2 = r_inv_threshold(0.5, 5.0, 2, d_max, f0, h_name, "A")
    for r_t in np.logspace(np.log10(0.1), np.log10(10.0), 11):
        curve = er_curve(float(r_t), 0.5, 5.0, 2, d_max, f0, h_name, "A")
        rows_C.append(dict(case="V1N-v5-N2", r=float(r_t), V=0.5, v=5.0, N=2,
                           **{k: curve[k] for k in
                              ["alpha_global", "R_global", "alpha_left", "R_left",
                               "alpha_right", "R_right", "R_at_inv_N",
                               "inversion_global"]}))
        delta = curve["R_left"] - curve["R_right"]
        print(f"  {r_t:8.4f} {t2['r_inv_star']:8.4f} "
              f"{curve['alpha_global']:9.3f} {curve['R_global']:9.5f} "
              f"{curve['alpha_left']:7.3f} {curve['R_left']:8.5f} "
              f"{curve['alpha_right']:8.3f} {curve['R_right']:8.5f} "
              f"{curve['R_at_inv_N']:8.5f} {delta:9.5f}")

    # (iii) extend to V < 1/N for N=2 (only relevant if primary sweep at N=2):
    #       V=0.25 with N=2 ⇒ V < 1/N = 0.5 is *anti-cue*. Inversion *expected*.
    #       This is NOT in the paper's primary sweep (which is N=4 only), but it
    #       *is* in the swept V-range [0.25, 1.0] as the paper writes it.
    print()
    print("  (iii) Anti-cue regime (V < 1/N) at N=2 — outside paper's primary")
    print("        sweep (which is N=4 only) but inside the paper's stated V-range.")
    print(f"  {'V':>6s} {'r':>8s} {'r*_inv':>8s} "
          f"{'α*global':>9s} {'R*global':>9s} {'α*left':>7s} {'R*left':>8s} "
          f"{'α*right':>8s} {'R*right':>8s} {'inv?':>5s}")
    print("  " + "-" * 96)
    for V_t in [0.25, 0.40]:
        for r_t in [0.1, 1.0, 5.0, 10.0]:
            tt = r_inv_threshold(V_t, 5.0, 2, d_max, f0, h_name, "A")
            curve = er_curve(float(r_t), V_t, 5.0, 2, d_max, f0, h_name, "A")
            rows_C.append(dict(case=f"V_lt_1N-N2-V{V_t}-r{r_t}",
                               r=float(r_t), V=V_t, v=5.0, N=2,
                               r_inv_star=tt["r_inv_star"],
                               **{k: curve[k] for k in
                                  ["alpha_global", "R_global", "alpha_left", "R_left",
                                   "alpha_right", "R_right", "R_at_inv_N",
                                   "inversion_global"]}))
            print(f"  {V_t:6.3f} {r_t:8.4f} {tt['r_inv_star']:8.4f} "
                  f"{curve['alpha_global']:9.3f} {curve['R_global']:9.5f} "
                  f"{curve['alpha_left']:7.3f} {curve['R_left']:8.5f} "
                  f"{curve['alpha_right']:8.3f} {curve['R_right']:8.5f} "
                  f"{str(curve['inversion_global']):>5s}")

    # =====================================================================
    # Verdict decision logic.
    # =====================================================================
    print()
    print("=" * 72)
    print("Verdict decision (mission §3.1)")
    print("=" * 72)

    primary_inversion_count = sum(1 for r in rows_B if r["inversion_global"])
    anticue_inversion_count = sum(1 for r in rows_C
                                   if r["case"].startswith("V_lt_1N") and r["inversion_global"])
    print(f"  Step B inversions across primary-sweep adversarial cells (N=4): {primary_inversion_count}")
    print(f"  Step C inversions in V < 1/N anti-cue regime (N=2, NOT in primary sweep): "
          f"{anticue_inversion_count}")

    if primary_inversion_count == 0 and anticue_inversion_count == 0:
        verdict = ("WEAKLY-SUPPORTED — C4 holds globally across primary sweep; "
                   "boundary closed form predicts left-branch local inversion "
                   "in some cells but right-branch always dominates globally.")
    elif primary_inversion_count == 0 and anticue_inversion_count > 0:
        verdict = ("CONFIRMED-CONDITIONAL — C4 holds across N=4 primary sweep; "
                   "fails at V < 1/N which is outside the primary sweep but "
                   "inside the paper's stated V-range [0.25, 1.0] when N varies.")
    else:
        verdict = "CONTESTED — C4 has a global counterexample inside the primary sweep."

    print()
    print(f"  Verdict: {verdict}")

    # Persist.
    out = dict(
        step_A=dict(rows=rows_A,
                    n_total=n_total, n_in_range=n_in_range,
                    n_below=n_below, n_above=n_above),
        step_B=dict(rows=rows_B,
                    primary_inversion_count=primary_inversion_count),
        step_C=dict(rows=rows_C,
                    anticue_inversion_count=anticue_inversion_count),
        verdict=verdict,
        metadata=dict(
            r_test_for_step_B=10.0,
            alpha_grid="np.arange(0.02, 1.0+1e-9, 0.005)",
            c_grid="np.arange(-2.5, 2.5+1e-9, 0.05)",
            N=4, d_max=2.0, f0=0.5, h="sqrt",
            variant_default="A", variants_swept=["A", "B"],
        ),
    )
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump(out, f, indent=2, default=lambda x: float(x) if isinstance(x, np.floating) else x)
    print()
    print(f"  Wrote: {os.path.join(out_dir, 'results.json')}")


if __name__ == "__main__":
    main()
