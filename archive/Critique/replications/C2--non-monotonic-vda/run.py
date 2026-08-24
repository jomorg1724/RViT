"""
Re-derivation cross-check for C2 (non-monotonic VDA in r).

Mission §2.4 specifies the model; mission §2.6 C2 states the claim:
"VDA benefit is non-monotonic in r, peaking near r ≈ 0.3 in the
cost-dominant regime, and approaching 0 at both extremes."

Reference regime (paper Figure 4):
    N=4, d'_max=2.0, f_0=0.5, h(a)=sqrt(a), V=0.5, v=5, Variant A.

This script implements the policy decomposition P1, P2, P3, P4
from mission §2.5, sweeps r across [0.1, 10.0] log-spaced (21 pts),
and reports VDA(r) = R(P1) - R(P2). The goal is *not* to reproduce
Figure 4 pixel-for-pixel — that is a separate full replication
task (spawned as follow-up). The goal here is to corroborate the
analytic re-derivation: that VDA is non-monotonic, with a peak
in the cost-dominant regime (r < 1) and asymptotes to 0 at both
extremes.

For Variant A: CR = V*v + (1-V).

NB: scipy not installed in the sandbox (disk full). We use
numpy + a hand-rolled normal CDF via math.erf.
"""

from __future__ import annotations

import math
import json
import os
from typing import Callable

import numpy as np


# ---------------------------------------------------------------
# Normal CDF (Phi) and pdf (phi).
# Phi(x) = 0.5 * (1 + erf(x / sqrt(2))).
# Vectorized via np.vectorize for clarity, since N is small.
# For inner loops we want a numpy-native implementation:
# numpy >= 1.24 ships np.erf? Not standard. Use math.erf elementwise.
# ---------------------------------------------------------------

_SQRT2 = math.sqrt(2.0)
_SQRT_2PI = math.sqrt(2.0 * math.pi)


def Phi(x):
    """Standard normal CDF. Vectorized over array-or-scalar."""
    if np.isscalar(x):
        return 0.5 * (1.0 + math.erf(float(x) / _SQRT2))
    x_arr = np.asarray(x, dtype=float)
    # Vectorize math.erf elementwise.
    out = np.empty_like(x_arr)
    flat = x_arr.ravel()
    flat_out = out.ravel()
    for i, xi in enumerate(flat):
        flat_out[i] = 0.5 * (1.0 + math.erf(float(xi) / _SQRT2))
    return out


# ---------------------------------------------------------------
# Model primitives (mission §2)
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
    Per-location d' at cued and (each) uncued location given allocation alpha.
    Mission §2.4 Eqs (7)–(8). Clamped at >= 0.

    For alpha >= 1/N: cued gains (scaled by beta), uncued loses (scaled by gamma).
    For alpha <  1/N: roles reverse.
    """
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
# Inner optimisation: given (alpha, v, r, V, N), find optimal (c_c, c_u).
# ---------------------------------------------------------------

C_GRID = np.arange(-2.5, 2.5 + 1e-9, 0.05)


def optimal_criteria_R(d_c: float, d_u: float, v: float, V: float, N: int,
                       variant: str = "A") -> float:
    """
    Grid-search optimal (c_c, c_u) given fixed d_c, d_u. Returns R*.
    Vectorized using only numpy (Phi computed via math.erf).
    """
    # Compute Phi values once per grid via vectorized loop.
    hr_c_grid = Phi(d_c / 2.0 - C_GRID)
    hr_u_grid = Phi(d_u / 2.0 - C_GRID)
    far_c_grid = Phi(-d_c / 2.0 - C_GRID)
    far_u_grid = Phi(-d_u / 2.0 - C_GRID)
    if variant == "A":
        cr = V * v + (1.0 - V)
    else:
        cr = 1.0
    # Broadcast: c_c on axis 0, c_u on axis 1.
    p_no_fa = (1.0 - far_c_grid)[:, None] * ((1.0 - far_u_grid) ** (N - 1))[None, :]
    er = 0.5 * (V * hr_c_grid[:, None] * v + (1.0 - V) * hr_u_grid[None, :]) \
       + 0.5 * p_no_fa * cr
    return float(er.max())


def policy_rewards(v: float, V: float, N: int, d_max: float, f0: float,
                   h: Callable, r: float, variant: str = "A",
                   alpha_grid: np.ndarray | None = None) -> dict:
    """
    Compute R(P1), R(P2), R(P3), R(P4) at given (v, V, r, ...).
    P2 fixes alpha at alpha*(v=1) — the value-blind allocation.
    """
    if alpha_grid is None:
        # Coarser than paper's 0.005 for sandbox speed; refine later if needed.
        alpha_grid = np.arange(0.02, 1.0 + 1e-9, 0.01)

    # Precompute (d_c, d_u) per alpha.
    d_pairs = [d_prime_cued_uncued(float(a), r, d_max, f0, h, N) for a in alpha_grid]

    # P3, P4: alpha = 1/N
    alpha_uniform = 1.0 / N
    d_c_u, d_u_u = d_prime_cued_uncued(alpha_uniform, r, d_max, f0, h, N)
    r_p3 = optimal_criteria_R(d_c_u, d_u_u, v, V, N, variant)
    # P4: alpha = 1/N AND c = 0 at both
    hr = Phi(d_c_u / 2.0 - 0.0)
    far = Phi(-d_c_u / 2.0 - 0.0)
    cr = V * v + (1.0 - V) if variant == "A" else 1.0
    r_p4 = 0.5 * (V * hr * v + (1.0 - V) * hr) + 0.5 * (1.0 - far) ** N * cr

    # P1: jointly optimise alpha and criteria.
    rs_p1 = np.array([optimal_criteria_R(dc, du, v, V, N, variant)
                      for dc, du in d_pairs])
    idx_p1 = int(np.argmax(rs_p1))
    alpha_p1 = float(alpha_grid[idx_p1])
    r_p1 = float(rs_p1[idx_p1])

    # P2: alpha fixed at alpha*(v=1).
    rs_p2_v1 = np.array([optimal_criteria_R(dc, du, 1.0, V, N, variant)
                         for dc, du in d_pairs])
    alpha_p2 = float(alpha_grid[int(np.argmax(rs_p2_v1))])
    dc_p2, du_p2 = d_prime_cued_uncued(alpha_p2, r, d_max, f0, h, N)
    r_p2 = optimal_criteria_R(dc_p2, du_p2, v, V, N, variant)

    return {
        "r": r,
        "alpha_p1": alpha_p1,
        "alpha_p2": alpha_p2,
        "R_p1": r_p1,
        "R_p2": r_p2,
        "R_p3": r_p3,
        "R_p4": r_p4,
        "VDA": r_p1 - r_p2,
        "criterion_gain": r_p3 - r_p4,
        "validity_attention_gain": r_p2 - r_p3,
        "criterion_fraction": (r_p3 - r_p4) / max(r_p1 - r_p4, 1e-12),
    }


# ---------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------

def main():
    N = 4
    d_max = 2.0
    f0 = 0.5
    h = H_FORMS["sqrt"]
    V = 0.5
    v = 5.0
    variant = "A"

    # Log-spaced r grid covering the paper's [0.1, 10.0]; 21 points like the paper.
    r_grid = np.logspace(np.log10(0.1), np.log10(10.0), 21)

    rows = []
    for r in r_grid:
        row = policy_rewards(v, V, N, d_max, f0, h, float(r), variant)
        rows.append(row)
        print(f"r={r:8.4f}  alpha_P1={row['alpha_p1']:.3f}  alpha_P2={row['alpha_p2']:.3f}  "
              f"R(P1)={row['R_p1']:.5f}  R(P2)={row['R_p2']:.5f}  VDA={row['VDA']:.5f}  "
              f"crit_frac={row['criterion_fraction']:.3f}")

    # Locate the peak of VDA across the swept r.
    vdas = np.array([row["VDA"] for row in rows])
    peak_idx = int(np.argmax(vdas))
    print()
    print(f"Peak VDA across swept r: {vdas[peak_idx]:.5f} at r = {r_grid[peak_idx]:.4f}")
    print(f"VDA at r=0.1: {vdas[0]:.5f}")
    print(f"VDA at r=10.0: {vdas[-1]:.5f}")
    print(f"Paper claim (C2): peak VDA ~ 0.080 at r ~ 0.3.")

    # Save results.
    os.makedirs("output", exist_ok=True)
    with open("output/vda_vs_r.json", "w") as fh:
        json.dump({
            "rows": rows,
            "peak_r": float(r_grid[peak_idx]),
            "peak_vda": float(vdas[peak_idx]),
            "reference_regime": {"N": N, "d_max": d_max, "f0": f0,
                                  "h": "sqrt", "V": V, "v": v,
                                  "variant": variant}
        }, fh, indent=2)


if __name__ == "__main__":
    main()
