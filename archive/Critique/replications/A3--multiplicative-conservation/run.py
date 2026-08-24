"""
A3 re-derivation cross-check (focused replication slice) — does the
paper's §5.5 robustness claim hold when the additive conservation
constraint β + γ = 2 is replaced by the multiplicative βγ = 1?  (CR-040)

--------------------------------------------------------------------
TARGET CLAIM (paper §5.5, p.8, verbatim)
--------------------------------------------------------------------
    "Third, the β + γ = 2 constraint conserves total attention
     magnitude; alternative constraints (e.g., multiplicative βγ = 1)
     could yield quantitatively different results, though the
     qualitative findings—non-monotonic VDA, no inversion, criterion
     dominance—should be robust."

A3 (mission §2.7) is the assumption that the benefit/cost asymmetry
is governed by the ADDITIVE conservation rule β + γ = 2.  The paper
itself names the multiplicative alternative βγ = 1 but does not run
it.  This script runs it, on a FOCUSED slice (mission §8.5: one
slice, not the full 4,410-row sweep).

--------------------------------------------------------------------
MATHEMATICAL FRAMING  (full derivation: Critique/derivations/A3--*.md)
--------------------------------------------------------------------
Both weight families are pinned by the SAME ratio constraint β/γ = r:

    additive   (β+γ=2):  β_add(r) = 2r/(r+1),   γ_add(r) = 2/(r+1)
    multiplic. (βγ =1):  β_mul(r) = √r,         γ_mul(r) = 1/√r

Both give β = γ = 1 at r = 1 (so C5 symmetric recovery is
constraint-AGNOSTIC; the families AGREE exactly at r=1).

CENTRAL STRUCTURAL FACT (proved in the derivation, verified in
Block 0 below): the multiplicative pair is the additive pair scaled
by a common factor

    κ(r) := β_mul/β_add = γ_mul/γ_add = (r+1)/(2√r)
          = ½(√r + 1/√r) = cosh(½ ln r)  ≥  1,   equality iff r=1.

Hence (β_mul, γ_mul) = κ(r)·(β_add, γ_add); κ is symmetric under
r ↦ 1/r and → ∞ at both extremes.  Consequences the slice tests:
  • β_mul + γ_mul = 2κ(r) ≥ 2 — multiplicative does NOT conserve the
    L1 magnitude; the paper's "conserves total attention magnitude"
    is an ADDITIVE-ONLY property.  βγ=1 inflates total gain magnitude
    as |ln r| grows.
  • At a fixed r, the multiplicative map amplifies BOTH the cued
    benefit (β) and the uncued cost (γ) by κ(r).

The d'(α) maps (mission §2.4) are otherwise identical:
    d'_cued (α) = d'_base + β·[d'_max f(α)            − d'_base]
    d'_uncued(α)= d'_base + γ·[d'_max f((1−α)/(N−1))  − d'_base]
with d'_base = d'_max f(1/N), clamped ≥ 0, and the β/γ roles swapping
across the α = 1/N kink (so inversion α < 1/N is representable).

--------------------------------------------------------------------
ATTACK DESIGN (mission §3.2 — re-derivation, numerically corroborated)
--------------------------------------------------------------------
Block 0  Verify the κ(r) rescaling identity to machine precision and
         tabulate β,γ for both families across the r-grid.
Block 1  C2 probe — VDA(r) = R(P1) − R(P2) across log-r ∈ [0.1,10]
         at the paper's reference regime (N=4, d'_max=2, f_0=0.5, √,
         V=0.5, v=5, Variant A) under BOTH families.  Report peak
         location, peak magnitude, and the two-extreme limits.  The
         qualitative claim is "non-monotonic, →0 at both extremes".
Block 2  C1 probe — criterion fraction CF(r) =
         [R(P3)−R(P4)]/[R(P1)−R(P4)] across the same r-grid under
         both families.  P3,P4 sit at α=1/N (β,γ irrelevant there) so
         R(P3),R(P4) are IDENTICAL across families by construction;
         only R(P1) (the denominator) moves.  Report the CF curve and
         min CF over the slice for each family.
Block 3  C4 probe — no-inversion spot check.  Re-optimise α over a
         grid that INCLUDES α<1/N at the reference regime r-grid and
         at the most-adversarial V≥1/N cells from CR-004 (r=10), under
         the multiplicative map.  Report min α*_P1 (inversion ⇔ <1/N).

Model primitives are an INDEPENDENT re-implementation in the spirit
of the C5 substrate (Critique/replications/C5--symmetric-recovery/
run.py) and the C2 policy decomposition
(Critique/replications/C2--non-monotonic-vda/run.py); the only change
is the swappable β/γ map.

CR-040, prompt v0.2, run-010, 2026-05-22.
"""

from __future__ import annotations

import json
import math
import os
import time
from typing import Callable

import numpy as np

# --------------------------------------------------------------------
# Φ (standard normal CDF). scipy preferred; A&S 7.1.26 numpy fallback.
# Both code paths call the SAME Φ, so any Φ approximation error cancels
# in cross-family differences and in the P1−P2 / P3−P4 reward gaps.
# --------------------------------------------------------------------
_SQRT2 = math.sqrt(2.0)
try:
    from scipy.special import ndtr as _ndtr

    def Phi(x):
        return _ndtr(np.asarray(x, dtype=float))

    _PHI_BACKEND = "scipy.special.ndtr"
except ImportError:
    _A1, _A2, _A3c, _A4, _A5 = (0.254829592, -0.284496736, 1.421413741,
                                -1.453152027, 1.061405429)
    _P = 0.3275911

    def _erf_np(x_arr: np.ndarray) -> np.ndarray:
        x_abs = np.abs(x_arr)
        t = 1.0 / (1.0 + _P * x_abs)
        poly = ((((_A5 * t + _A4) * t + _A3c) * t + _A2) * t + _A1) * t
        y = 1.0 - poly * np.exp(-x_abs * x_abs)
        return np.where(x_arr >= 0.0, y, -y)

    def Phi(x):
        arr = np.asarray(x, dtype=float)
        return 0.5 * (1.0 + _erf_np(arr / _SQRT2))

    _PHI_BACKEND = "A&S 7.1.26 numpy-vectorised"


# --------------------------------------------------------------------
# Transfer function and the TWO asymmetry-weight families.
# --------------------------------------------------------------------
def make_h(name: str) -> Callable:
    if name == "sqrt":
        return lambda a: np.sqrt(a)
    if name == "linear":
        return lambda a: a
    if name == "p0_3":
        return lambda a: np.power(a, 0.3)
    if name == "p2":
        return lambda a: np.power(a, 2.0)
    raise ValueError(name)


def f_transfer(a, f0: float, h: Callable):
    """f(a) = f_0 + (1 − f_0) h(a)."""
    return f0 + (1.0 - f0) * h(a)


def beta_gamma_additive(r: float) -> tuple[float, float]:
    """A3 (model's choice): β+γ=2, β/γ=r ⟹ β=2r/(r+1), γ=2/(r+1)."""
    return 2.0 * r / (r + 1.0), 2.0 / (r + 1.0)


def beta_gamma_multiplicative(r: float) -> tuple[float, float]:
    """§5.5 alternative: βγ=1, β/γ=r ⟹ β=√r, γ=1/√r."""
    s = math.sqrt(r)
    return s, 1.0 / s


WEIGHT_MAPS = {
    "additive": beta_gamma_additive,
    "multiplicative": beta_gamma_multiplicative,
}


def d_prime_pair(alpha: float, r: float, d_max: float, f0: float,
                 h: Callable, N: int, weight_map: Callable) -> tuple[float, float]:
    """
    (d'_cued, d'_uncued) at allocation α under the chosen β/γ family.
    Mission §2.4. β scales the OVER-allocated location's departure,
    γ the UNDER-allocated; the roles swap across the α=1/N kink so
    α<1/N (inversion) is representable.  Clamped ≥ 0.
    """
    beta, gamma = weight_map(r)
    d_base = d_max * f_transfer(1.0 / N, f0, h)
    if alpha >= 1.0 / N:
        d_c = d_base + beta * (d_max * f_transfer(alpha, f0, h) - d_base)
        d_u = d_base + gamma * (d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h) - d_base)
    else:
        d_c = d_base + gamma * (d_max * f_transfer(alpha, f0, h) - d_base)
        d_u = d_base + beta * (d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h) - d_base)
    return float(max(d_c, 0.0)), float(max(d_u, 0.0))


# --------------------------------------------------------------------
# Inner optimisation over criteria (mission §2.5 Eq. 9) + policies.
# --------------------------------------------------------------------
C_GRID = np.arange(-3.0, 3.0 + 1e-9, 0.05)


def optimal_criteria_R(d_c: float, d_u: float, v: float, V: float, N: int,
                       variant: str = "A") -> float:
    """R*(d_c,d_u) = max over (c_c,c_u) of expected reward (Eq. 9)."""
    hr_c = Phi(d_c / 2.0 - C_GRID)
    hr_u = Phi(d_u / 2.0 - C_GRID)
    far_c = Phi(-d_c / 2.0 - C_GRID)
    far_u = Phi(-d_u / 2.0 - C_GRID)
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    p_no_fa = (1.0 - far_c)[:, None] * ((1.0 - far_u) ** (N - 1))[None, :]
    er = 0.5 * (V * hr_c[:, None] * v + (1.0 - V) * hr_u[None, :]) + 0.5 * p_no_fa * cr
    return float(er.max())


def policy_rewards(v: float, V: float, N: int, d_max: float, f0: float,
                   h: Callable, r: float, weight_map: Callable,
                   variant: str, alpha_grid: np.ndarray) -> dict:
    """R(P1..P4), VDA, criterion gain/fraction at (v,V,r,...)."""
    d_pairs = [d_prime_pair(float(a), r, d_max, f0, h, N, weight_map) for a in alpha_grid]

    # P3, P4 at α = 1/N (β,γ multiply a zero bracket ⟹ family-independent).
    alpha_u = 1.0 / N
    d_c_u, d_u_u = d_prime_pair(alpha_u, r, d_max, f0, h, N, weight_map)
    r_p3 = optimal_criteria_R(d_c_u, d_u_u, v, V, N, variant)
    hr = Phi(d_c_u / 2.0 - 0.0)
    far = Phi(-d_c_u / 2.0 - 0.0)
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    r_p4 = float(0.5 * (V * hr * v + (1.0 - V) * hr) + 0.5 * (1.0 - far) ** N * cr)

    # P1 joint optimum over α.
    rs_p1 = np.array([optimal_criteria_R(dc, du, v, V, N, variant) for dc, du in d_pairs])
    idx_p1 = int(np.argmax(rs_p1))
    alpha_p1 = float(alpha_grid[idx_p1])
    r_p1 = float(rs_p1[idx_p1])

    # P2 value-blind: α fixed at α*(v=1), criteria re-opt at this v.
    rs_p2_v1 = np.array([optimal_criteria_R(dc, du, 1.0, V, N, variant) for dc, du in d_pairs])
    alpha_p2 = float(alpha_grid[int(np.argmax(rs_p2_v1))])
    dc_p2, du_p2 = d_prime_pair(alpha_p2, r, d_max, f0, h, N, weight_map)
    r_p2 = optimal_criteria_R(dc_p2, du_p2, float(v), V, N, variant)

    return dict(r=r, alpha_p1=alpha_p1, alpha_p2=alpha_p2,
                R_p1=r_p1, R_p2=r_p2, R_p3=r_p3, R_p4=r_p4,
                VDA=r_p1 - r_p2,
                criterion_gain=r_p3 - r_p4,
                validity_attention_gain=r_p2 - r_p3,
                criterion_fraction=(r_p3 - r_p4) / max(r_p1 - r_p4, 1e-12))


# --------------------------------------------------------------------
# Block 0 — κ(r) rescaling identity verification.
# --------------------------------------------------------------------
def block0_kappa(r_grid: np.ndarray) -> dict:
    rows = []
    max_dev = 0.0
    for r in r_grid:
        ba, ga = beta_gamma_additive(float(r))
        bm, gm = beta_gamma_multiplicative(float(r))
        kappa = (r + 1.0) / (2.0 * math.sqrt(r))
        kappa_cosh = math.cosh(0.5 * math.log(r))
        # both ratios should equal κ(r)
        dev_b = abs(bm / ba - kappa)
        dev_g = abs(gm / ga - kappa)
        dev_cosh = abs(kappa - kappa_cosh)
        sum_mul = bm + gm                       # = 2κ
        prod_add = ba * ga                       # = 1/κ²
        max_dev = max(max_dev, dev_b, dev_g, dev_cosh,
                      abs(sum_mul - 2.0 * kappa),
                      abs(prod_add - 1.0 / kappa ** 2))
        rows.append(dict(r=float(r), beta_add=ba, gamma_add=ga,
                         beta_mul=bm, gamma_mul=gm, kappa=kappa,
                         sum_mul=sum_mul, sum_add=ba + ga,
                         prod_add=prod_add, prod_mul=bm * gm))
    return dict(rows=rows, max_identity_deviation=float(max_dev))


# --------------------------------------------------------------------
# Block 1 (C2) & Block 2 (C1) — VDA and CF vs r under both families.
# --------------------------------------------------------------------
def block_c2_c1(r_grid: np.ndarray, alpha_grid: np.ndarray) -> dict:
    N, d_max, f0, h = 4, 2.0, 0.5, make_h("sqrt")
    V, v, variant = 0.5, 5.0, "A"
    out = {}
    for fam_name, wmap in WEIGHT_MAPS.items():
        rows = [policy_rewards(v, V, N, d_max, f0, h, float(r), wmap, variant, alpha_grid)
                for r in r_grid]
        vdas = np.array([row["VDA"] for row in rows])
        cfs = np.array([row["criterion_fraction"] for row in rows])
        peak_idx = int(np.argmax(vdas))
        out[fam_name] = dict(
            rows=rows,
            peak_r=float(r_grid[peak_idx]), peak_vda=float(vdas[peak_idx]),
            vda_at_rmin=float(vdas[0]), vda_at_rmax=float(vdas[-1]),
            cf_min=float(cfs.min()), cf_min_r=float(r_grid[int(np.argmin(cfs))]),
            cf_max=float(cfs.max()), cf_at_peak=float(cfs[peak_idx]),
        )
    return dict(reference_regime=dict(N=N, d_max=d_max, f0=f0, h="sqrt",
                                      V=V, v=v, variant=variant),
                families=out)


# --------------------------------------------------------------------
# Block 3 (C4) — no-inversion spot check under the multiplicative map.
# --------------------------------------------------------------------
def block_c4(r_grid: np.ndarray, alpha_grid: np.ndarray) -> dict:
    N, d_max, f0, h = 4, 2.0, 0.5, make_h("sqrt")
    inv_thresh = 1.0 / N
    # (a) reference regime across r.
    ref = []
    for r in r_grid:
        row = policy_rewards(5.0, 0.5, N, d_max, f0, h, float(r),
                             beta_gamma_multiplicative, "A", alpha_grid)
        ref.append(dict(r=float(r), alpha_p1=row["alpha_p1"], alpha_p2=row["alpha_p2"]))
    # (b) most-adversarial V≥1/N cells from CR-004 at r=10, multiplicative.
    adversarial = []
    for V in [0.25, 0.30, 0.40, 0.55]:
        for v in [1, 2, 5]:
            for variant in ["A", "B"]:
                row = policy_rewards(float(v), float(V), N, d_max, f0, h, 10.0,
                                     beta_gamma_multiplicative, variant, alpha_grid)
                adversarial.append(dict(V=float(V), v=v, variant=variant,
                                        r=10.0, alpha_p1=row["alpha_p1"],
                                        alpha_p2=row["alpha_p2"]))
    all_alpha = ([x["alpha_p1"] for x in ref] + [x["alpha_p2"] for x in ref]
                 + [x["alpha_p1"] for x in adversarial]
                 + [x["alpha_p2"] for x in adversarial])
    min_alpha = float(min(all_alpha))
    return dict(inversion_threshold=inv_thresh, min_alpha_observed=min_alpha,
                inversion_detected=bool(min_alpha < inv_thresh - 1e-9),
                reference_r_sweep=ref, adversarial_cells=adversarial)


def main():
    t0 = time.time()
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(outdir, exist_ok=True)

    # r-grid: log-spaced [0.1,10], 21 pts (paper / C2).  α-grid: Δα=0.005 + 1/N.
    r_grid = np.logspace(np.log10(0.1), np.log10(10.0), 21)
    alpha_grid = np.unique(np.concatenate(
        [np.arange(0.005, 1.0 + 1e-9, 0.005), np.array([1.0 / 4])]))

    print(f"A3 multiplicative-conservation slice (CR-040)")
    print(f"  Φ backend: {_PHI_BACKEND}")
    print(f"  r-grid: {len(r_grid)} log pts [0.1,10]; α-grid: {len(alpha_grid)} pts; c-grid: {len(C_GRID)} pts")

    print("\n[Block 0] κ(r) rescaling identity ...")
    b0 = block0_kappa(r_grid)
    print(f"  max |identity deviation| over grid: {b0['max_identity_deviation']:.3e}")
    for row in b0["rows"][::4]:
        print(f"  r={row['r']:7.3f}  add(β,γ)=({row['beta_add']:.3f},{row['gamma_add']:.3f})"
              f"  mul(β,γ)=({row['beta_mul']:.3f},{row['gamma_mul']:.3f})"
              f"  κ={row['kappa']:.4f}  Σ_mul={row['sum_mul']:.3f}")

    print("\n[Block 1+2] C2 VDA(r) and C1 CF(r), reference regime, both families ...")
    bc = block_c2_c1(r_grid, alpha_grid)
    for fam, d in bc["families"].items():
        print(f"  [{fam:14s}] peak VDA={d['peak_vda']:.5f} @ r={d['peak_r']:.4f}"
              f" | VDA(r=0.1)={d['vda_at_rmin']:.5f} VDA(r=10)={d['vda_at_rmax']:.5f}"
              f" | CF∈[{d['cf_min']:.3f},{d['cf_max']:.3f}] (min@r={d['cf_min_r']:.3f})")

    print("\n[Block 3] C4 no-inversion spot check (multiplicative) ...")
    b3 = block_c4(r_grid, alpha_grid)
    print(f"  inversion threshold 1/N = {b3['inversion_threshold']}")
    print(f"  min α*_P1/P2 observed   = {b3['min_alpha_observed']:.4f}")
    print(f"  inversion detected?     = {b3['inversion_detected']}")

    result = dict(block0_kappa=b0, block_c2_c1=bc, block_c4=b3,
                  metadata=dict(phi_backend=_PHI_BACKEND, c_grid_step=0.05,
                                alpha_grid_step=0.005, r_grid_pts=len(r_grid),
                                claim_id="A3", attack_vector="re-derivation",
                                run_id="run-010", task_id="CR-040",
                                prompt_version="0.2", date="2026-05-22",
                                elapsed_s=round(time.time() - t0, 2)))
    out_path = os.path.join(outdir, "results.json")
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2, default=float)
    print(f"\nSaved {out_path}  (elapsed {result['metadata']['elapsed_s']}s)")


if __name__ == "__main__":
    main()
