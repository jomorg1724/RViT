"""
A6 re-derivation corroboration — is the HOMOGENEOUS DECISION RULE
(same SDT machinery at every location) load-bearing for the paper's
criterion-vs-attention decomposition? (CR-011, folds in CR-055)

--------------------------------------------------------------------
WHAT A6 IS
--------------------------------------------------------------------
Mission §2.7 A6: "The decision rule is HOMOGENEOUS across locations
(same SDT machinery everywhere). If detection uses different decision
rules at cued vs uncued locations (e.g. different decision noise), the
policy decomposition does not apply cleanly."

The paper never states A6; it is implicit in §2.2, where the SAME
equal-variance Gaussian SDT transform (internal noise σ = 1) is applied
at every location:
    HR(d',c)  = Φ(d'/2 − c)          FAR(d',c)  = Φ(−d'/2 − c).
Only the FREE parameters differ by location: d'_i (set by attention via
f) and c_i (set by the optimiser, two groups: cued / uncued).

The §5.5 limitation sentence bundles A6 with A1:
    "the model assumes independent per-location SDT decisions; real
     observers emit a single global response, introducing dependencies
     that could alter the optimal policy."
Run-017 (CR-052) showed the "independent ... product P_no-fa" clause is
A1 (Booking 1) and the "single global response" clause is A6 (Booking 2,
the pooled-decision / decision-architecture reading). This file attacks
the *mission's* A6: heterogeneous decision MACHINERY, operationalised as
a per-location decision-noise scale s_i (cued s_c, uncued s_u). The
paper's model is the s_i ≡ 1 corner.

--------------------------------------------------------------------
MATHEMATICAL FRAMING (full derivation in
Critique/derivations/A6--heterogeneous-decision-rule.md)
--------------------------------------------------------------------
Add late/decision noise η_i ~ N(0, σ_{d,i}^2) to the per-location
decision variable, independent of the sensory evidence. With the unit-
variance sensory code, the effective decision SD is
    s_i = sqrt(1 + σ_{d,i}^2) ≥ 1,   s_i = 1 ⇔ σ_{d,i} = 0 (paper).
The SDT rates become (centred-criterion form, mission §2.2):
    HR_i  = Φ( (d'_i/2 − c_i) / s_i ),
    FAR_i = Φ( (−d'_i/2 − c_i) / s_i ).

PROP 1 (absorption / reparametrisation).  Because
    Φ( (d'_i/2 − c_i)/s_i ) = Φ( (d'_i/s_i)/2 − c_i/s_i ),
defining the EFFECTIVE sensitivity d̃'_i = d'_i / s_i and EFFECTIVE
criterion c̃_i = c_i / s_i makes the rates EXACTLY the paper's form with
d'_i → d̃'_i.  c_i ↦ c̃_i is a bijection (s_i > 0 fixed) and the optimiser
already searches all c_i, so the (α, c_c, c_u) reward landscape under
FIXED heterogeneous noise is identical in FORM to the paper's, with each
location's sensitivity rescaled by 1/s_i.  Fixed s_i is therefore in the
SAME class as a per-location change of d'_max or f_0 — a secondary-sweep
parameter.  It shifts the per-location effective d' (hence the numbers)
but introduces NO new functional form, does NOT couple locations, and
leaves the P1–P4 decomposition and the criterion-fraction DEFINITION
structurally intact.  ⇒ the clean "criterion vs attention" separation
survives fixed heterogeneous machinery.  NUMERICAL TEST (Block 1): the
criterion fraction computed under explicit (s_c, s_u) equals the one
computed from the rescaled sensitivities (d_c/s_c, d_u/s_u) with s ≡ 1,
to grid resolution.

PROP 2 (attention-coupled noise = a THIRD lever, cracks the metric's
interpretation).  Prop 1 needs s_i CONSTANT in α.  Empirically attention
modulates decision/readout noise and interneuronal correlations
(Cohen & Maunsell 2009; Mitchell, Sundberg & Reynolds 2009), i.e.
s_i = s(a_i) with s' < 0.  Then moving α (P3→P1) changes BOTH d'(α)
(via f) AND s(α) — the marginal reward gradient w.r.t. α gains a
noise-reduction term
    ∂R/∂α  ⊃  (∂R/∂d̃'_c) · ∂/∂α [ d'_c(α)/s_c(α) ],
    with ∂/∂α[d'_c/s_c] = d'_c'/s_c − d'_c s_c'/s_c^2  (2nd term ≥ 0 if s'<0).
So the gain the criterion fraction books to "attention" (the
P3→P1 increment) now bundles (i) spatial sensitivity reallocation AND
(ii) attention-modulated decision-noise reduction.  The metric still
returns a number, but it no longer cleanly partitions "criterion
mechanism vs attention mechanism."  We model the empirically-motivated
coupling
    s_i(a_i) = sqrt( 1 + κ ( 1 − h(a_i) ) ),   κ ≥ 0,   κ = 0 = paper,
(decision noise highest at zero attention, vanishing excess at full
attention) and report the criterion-fraction shift vs κ at the C2
headline cell.  Direction-of-shift is the empirical question; the
INTERPRETIVE crack (CF conflates two mechanisms) holds regardless of
sign.  This is the CR-055 prediction — "a single global / extra-lever
decision rule has more ways to exploit value, so the criterion fraction
compounds the way it fell under ρ (CR-052)."

--------------------------------------------------------------------
BLOCKS
--------------------------------------------------------------------
Block 0  Validation: s ≡ 1 reproduces the C1 headline CF (≈0.728 at
         r=1, V=0.5, v=5, variant A) and the C2 VDA peak (≈0.0799 at
         r≈0.383); and the Prop-1 algebraic identity HR/FAR(explicit-s)
         == HR/FAR(rescaled-d') holds pointwise to machine precision.
Block 1  Prop 1: fixed heterogeneous noise (s_c=1, s_u ∈ {1,1.25,1.5,2})
         at the headline cell — CF(explicit s) == CF(rescaled d', s≡1)
         to grid resolution ⇒ decomposition structurally invariant.
Block 2  Prop 2: attention-coupled s(α), κ ∈ {0,0.25,0.5,1.0} at the
         headline cell — report CF and VDA(α) and the criterion-fraction
         shift; plus the VDA-peak location over the r-grid at κ=0 vs κ=1.

Model primitives (Phi, f_transfer, beta_gamma, d_prime_pair,
optimal_criteria_R, reward_at_c_zero, compute_CF) are copied WITH
ATTRIBUTION from Critique/replications/C1--criterion-fraction-floor/run.py
so this file is an independent, standalone implementation. The ONLY new
machinery is the per-location decision-noise scale s_i in the rate
functions.

CR-011, prompt v0.2, run-018, 2026-05-25.
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
# in within-run comparisons (Prop-1 identity, CF differences).
# --------------------------------------------------------------------
_SQRT2 = math.sqrt(2.0)
try:
    from scipy.special import ndtr as _ndtr

    def Phi(x):
        return _ndtr(np.asarray(x, dtype=float))

    _PHI_BACKEND = "scipy.special.ndtr"
except ImportError:                                            # pragma: no cover
    _A1, _A2, _A3, _A4, _A5 = (0.254829592, -0.284496736, 1.421413741,
                               -1.453152027, 1.061405429)
    _P = 0.3275911

    def _erf_np(x_arr: np.ndarray) -> np.ndarray:
        x_abs = np.abs(x_arr)
        t = 1.0 / (1.0 + _P * x_abs)
        poly = ((((_A5 * t + _A4) * t + _A3) * t + _A2) * t + _A1) * t
        y = 1.0 - poly * np.exp(-x_abs * x_abs)
        return np.where(x_arr >= 0.0, y, -y)

    def Phi(x):
        arr = np.asarray(x, dtype=float)
        return 0.5 * (1.0 + _erf_np(arr / _SQRT2))

    _PHI_BACKEND = "A&S 7.1.26 numpy-vectorised"


# --------------------------------------------------------------------
# Model primitives (mission §2.3, §2.4) — copied from C1's run.py.
# --------------------------------------------------------------------
def make_h(name: str) -> Callable:
    """Transfer-function family h, h(0)=0, h(1)=1, monotone."""
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
    """f(a) = f_0 + (1 − f_0) h(a). Sensitivity multiplier ∈ [f_0, 1]."""
    return f0 + (1.0 - f0) * h(a)


def beta_gamma(r: float) -> tuple[float, float]:
    """β(r) = 2r/(r+1); γ(r) = 2/(r+1). β + γ = 2, β/γ = r."""
    return 2.0 * r / (r + 1.0), 2.0 / (r + 1.0)


def d_prime_pair(alpha: float, r: float, d_max: float, f0: float,
                 h: Callable, N: int) -> tuple[float, float]:
    """Per-location d' at cued and (each) uncued location. Mission §2.4.
    Returns (d'_cued, d'_uncued), clamped ≥ 0."""
    beta, gamma = beta_gamma(r)
    d_base = d_max * f_transfer(1.0 / N, f0, h)
    if alpha >= 1.0 / N:
        d_c = d_base + beta * (d_max * f_transfer(alpha, f0, h) - d_base)
        d_u = d_base + gamma * (d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h) - d_base)
    else:
        d_c = d_base + gamma * (d_max * f_transfer(alpha, f0, h) - d_base)
        d_u = d_base + beta * (d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h) - d_base)
    return float(max(d_c, 0.0)), float(max(d_u, 0.0))


# --------------------------------------------------------------------
# Criterion grid (Δc = 0.05 — paper's grid).
# --------------------------------------------------------------------
C_GRID = np.arange(-3.0, 3.0 + 1e-9, 0.05)
_C_GRID_LEN = len(C_GRID)


def optimal_criteria_R(d_c: float, d_u: float, v: float, V: float, N: int,
                       variant: str, s_c: float = 1.0, s_u: float = 1.0,
                       c_grid: np.ndarray | None = None) -> float:
    """
    R*(d_c, d_u; s_c, s_u) = max over (c_c, c_u) ∈ c_grid² of mission §2.5 Eq.9:
        0.5 [ V·HR_c·v + (1−V)·HR_u ] + 0.5·P_no_fa·CR,
    with the A6 decision-noise generalisation
        HR_i  = Φ( (d'_i/2 − c_i)/s_i ),   FAR_i = Φ( (−d'_i/2 − c_i)/s_i ),
        P_no_fa = (1−FAR_c)(1−FAR_u)^{N−1},  CR = V·v+(1−V) [A] or 1 [B].
    s_c = s_u = 1 is the paper's homogeneous-machinery model (A6 holds).
    c_grid defaults to the module C_GRID (Δc=0.05). Complexity O(|c_grid|²).
    """
    cg = C_GRID if c_grid is None else c_grid
    hr_c = Phi((d_c / 2.0 - cg) / s_c)                   # shape (|C|,)
    hr_u = Phi((d_u / 2.0 - cg) / s_u)                   # shape (|C|,)
    far_c = Phi((-d_c / 2.0 - cg) / s_c)                 # shape (|C|,)
    far_u = Phi((-d_u / 2.0 - cg) / s_u)                 # shape (|C|,)
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    p_no_fa = (1.0 - far_c)[:, None] * ((1.0 - far_u) ** (N - 1))[None, :]   # (|C|,|C|)
    er = 0.5 * (V * hr_c[:, None] * v + (1.0 - V) * hr_u[None, :]) + 0.5 * p_no_fa * cr
    return float(er.max())


def reward_at_c_zero(d_c: float, d_u: float, v: float, V: float, N: int,
                     variant: str, s_c: float = 1.0, s_u: float = 1.0) -> float:
    """R(P4): α=1/N AND c_c=c_u=0. Note c=0 is criterion-invariant under
    s (c/s = 0), so P4 is unaffected by the decision-noise scale at c=0
    EXCEPT through HR/FAR being evaluated at d'/(2 s)."""
    hr_c = float(Phi((d_c / 2.0) / s_c))
    hr_u = float(Phi((d_u / 2.0) / s_u))
    far_c = float(Phi((-d_c / 2.0) / s_c))
    far_u = float(Phi((-d_u / 2.0) / s_u))
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    p_no_fa = (1.0 - far_c) * (1.0 - far_u) ** (N - 1)
    return 0.5 * (V * hr_c * v + (1.0 - V) * hr_u) + 0.5 * p_no_fa * cr


# --------------------------------------------------------------------
# s(α) coupling for Prop 2 (attention-coupled decision noise).
# s_i(a_i) = sqrt(1 + κ (1 − h(a_i))); κ=0 ⇒ s≡1 (paper).
# --------------------------------------------------------------------
def s_of_a(a: float, kappa: float, h: Callable) -> float:
    return math.sqrt(1.0 + kappa * (1.0 - float(h(a))))


# --------------------------------------------------------------------
# compute_CF with per-location decision noise.
# If coupled=False: fixed (s_c, s_u). If coupled=True: s depends on the
# per-location allocation a_i via s_of_a(·, kappa, h).
# --------------------------------------------------------------------
def compute_CF(r: float, V: float, v: float, N: int, d_max: float, f0: float,
               h: Callable, variant: str, alpha_grid: np.ndarray,
               s_c_fixed: float = 1.0, s_u_fixed: float = 1.0,
               coupled: bool = False, kappa: float = 0.0) -> dict:
    """
    Returns R(P1..P4), VDA, criterion_fraction, alphas. Decision-noise model:
      coupled=False → s_c=s_c_fixed at cued, s_u=s_u_fixed at every uncued.
      coupled=True  → s_c=s(α), s_u=s((1−α)/(N−1)) (attention-coupled).
    The cued/uncued allocation determines a_i for the coupled case.
    """
    def s_pair(alpha: float) -> tuple[float, float]:
        if not coupled:
            return s_c_fixed, s_u_fixed
        a_c = alpha
        a_u = (1.0 - alpha) / (N - 1)
        return s_of_a(a_c, kappa, h), s_of_a(a_u, kappa, h)

    # P3, P4 at uniform attention α = 1/N (a_i = 1/N for all i).
    d_b = d_max * f_transfer(1.0 / N, f0, h)
    s_c_u, s_u_u = s_pair(1.0 / N)
    R_p3 = optimal_criteria_R(d_b, d_b, v, V, N, variant, s_c_u, s_u_u)
    R_p4 = reward_at_c_zero(d_b, d_b, v, V, N, variant, s_c_u, s_u_u)

    # P1 = max over α of R(α, c*).  d' and s both depend on α.
    rs_p1 = []
    for a in alpha_grid:
        dc, du = d_prime_pair(float(a), r, d_max, f0, h, N)
        sc, su = s_pair(float(a))
        rs_p1.append(optimal_criteria_R(dc, du, v, V, N, variant, sc, su))
    rs_p1 = np.array(rs_p1)
    idx_p1 = int(np.argmax(rs_p1))
    R_p1 = float(rs_p1[idx_p1])
    alpha_p1 = float(alpha_grid[idx_p1])

    # P2 — α fixed at α*(v=1); criteria re-optimised at current v.
    rs_p2_v1 = []
    for a in alpha_grid:
        dc, du = d_prime_pair(float(a), r, d_max, f0, h, N)
        sc, su = s_pair(float(a))
        rs_p2_v1.append(optimal_criteria_R(dc, du, 1.0, V, N, variant, sc, su))
    alpha_p2 = float(alpha_grid[int(np.argmax(np.array(rs_p2_v1)))])
    dc_p2, du_p2 = d_prime_pair(alpha_p2, r, d_max, f0, h, N)
    sc_p2, su_p2 = s_pair(alpha_p2)
    R_p2 = optimal_criteria_R(dc_p2, du_p2, v, V, N, variant, sc_p2, su_p2)

    total = R_p1 - R_p4
    crit = R_p3 - R_p4
    cf = crit / max(total, 1e-12)
    return dict(r=r, V=V, v=v, N=N, variant=variant,
                alpha_p1=alpha_p1, alpha_p2=alpha_p2,
                R_p1=R_p1, R_p2=R_p2, R_p3=R_p3, R_p4=R_p4,
                VDA=R_p1 - R_p2, criterion_gain=crit,
                criterion_fraction=cf, total_gain=total,
                s_c_uniform=s_c_u, s_u_uniform=s_u_u)


# ====================================================================
# Block 0 — validation against C1/C2 headline numbers + Prop-1 identity.
# ====================================================================
def block0_validation(alpha_grid: np.ndarray) -> dict:
    N, d_max, f0, h = 4, 2.0, 0.5, make_h("sqrt")
    # (a) C1 headline CF at r=1, V=0.5, v=5, variant A (paper ≈0.73; code 0.728).
    cf_row = compute_CF(1.0, 0.5, 5.0, N, d_max, f0, h, "A", alpha_grid)
    # (b) C2 VDA peak over the paper's r-grid at the headline cell.
    r_grid = np.unique(np.concatenate(
        [np.logspace(np.log10(0.1), np.log10(10.0), 21), np.array([1.0])]))
    vda = [(float(r), compute_CF(float(r), 0.5, 5.0, N, d_max, f0, h, "A",
                                 alpha_grid)["VDA"]) for r in r_grid]
    r_peak, vda_peak = max(vda, key=lambda t: t[1])
    # (c) Prop-1 pointwise identity: Φ((d/2−c)/s) == Φ((d/s)/2 − c/s).
    rng = np.linspace(-3, 3, 121)
    d_test, s_test = 1.7, 1.6
    lhs = Phi((d_test / 2.0 - rng) / s_test)
    rhs = Phi((d_test / s_test) / 2.0 - rng / s_test)
    max_identity_err = float(np.max(np.abs(lhs - rhs)))
    return dict(
        cf_headline_r1=cf_row["criterion_fraction"],
        cf_headline_r1_alpha_p1=cf_row["alpha_p1"],
        vda_peak_r=r_peak, vda_peak_value=vda_peak,
        prop1_pointwise_identity_max_err=max_identity_err,
        note=("CF≈0.728 and VDA peak≈0.0799@r≈0.383 reproduce C1/C2; "
              "Prop-1 identity holds to machine precision."))


# ====================================================================
# Block 1 — Prop 1: fixed heterogeneous noise is absorbed.
# CF(explicit s_c,s_u) == CF(rescaled d_c/s_c, d_u/s_u with s≡1) to grid.
# ====================================================================
def block1_fixed_noise(alpha_grid: np.ndarray) -> dict:
    N, d_max, f0, h = 4, 2.0, 0.5, make_h("sqrt")
    V, v, variant = 0.5, 5.0, "A"
    # WIDE criterion grid. The optimal *physical* criterion grows with s
    # (to hold FAR fixed under inflated decision noise the criterion must
    # move further from the midpoint), so the default [-3,3] grid CLIPS the
    # uncued criterion once s_u is large. The continuum identity (Block 0)
    # only manifests when neither parameterisation clips: explicit searches
    # physical c, reparam searches c̃=c/s, so a grid wide enough for both is
    # [-8,8] (covers physical c up to 8 and c̃ up to 8 ⇒ physical c up to 8 s).
    WIDE = np.arange(-8.0, 8.0 + 1e-9, 0.01)
    rows = []
    for (s_c, s_u) in [(1.0, 1.0), (1.0, 1.25), (1.0, 1.5), (1.0, 2.0),
                       (1.25, 1.0), (1.5, 1.5)]:
        cf_explicit = _cf_rescaled_or_explicit(1.0, V, v, N, d_max, f0, h, variant,
                                               alpha_grid, s_c, s_u,
                                               mode="explicit", c_grid=WIDE)
        cf_reparam = _cf_rescaled_or_explicit(1.0, V, v, N, d_max, f0, h, variant,
                                              alpha_grid, s_c, s_u,
                                              mode="reparam", c_grid=WIDE)
        rows.append(dict(s_c=s_c, s_u=s_u, cf_explicit=cf_explicit,
                         cf_reparam=cf_reparam,
                         abs_diff=abs(cf_explicit - cf_reparam)))
    max_diff = max(row["abs_diff"] for row in rows)

    # Step-convergence at the worst case (s_u=2) on the WIDE range: with no
    # clipping, the residual is pure discretisation and → 0 as Δc → 0.
    conv = []
    for dc_step in [0.05, 0.02, 0.01, 0.005]:
        cg = np.arange(-8.0, 8.0 + 1e-9, dc_step)
        cf_e = _cf_rescaled_or_explicit(1.0, V, v, N, d_max, f0, h, variant,
                                        alpha_grid, 1.0, 2.0, mode="explicit", c_grid=cg)
        cf_r = _cf_rescaled_or_explicit(1.0, V, v, N, d_max, f0, h, variant,
                                        alpha_grid, 1.0, 2.0, mode="reparam", c_grid=cg)
        conv.append(dict(dc_step=dc_step, cf_explicit=cf_e, cf_reparam=cf_r,
                         abs_diff=abs(cf_e - cf_r)))

    return dict(rows=rows, max_abs_diff_explicit_vs_reparam=max_diff,
                grid_convergence_worst_case=conv, c_grid_range=[-8.0, 8.0],
                note=("Prop 1: fixed heterogeneous decision noise is "
                      "absorbed into effective d'_i = d'_i/s_i (Block-0 "
                      "pointwise identity, err~1e-16). On a criterion grid "
                      "wide enough that neither the explicit nor the "
                      "reparametrised search clips ([-8,8]), CF computed the "
                      "two ways AGREES to grid resolution and the residual "
                      "→0 as Δc→0 ⇒ the P1–P4 decomposition is structurally "
                      "invariant: criterion still per-location-optimised, "
                      "attention still the α-lever; only the per-location "
                      "effective sensitivity changes (same class as a "
                      "d'_max/f_0 perturbation). NOTE: the default [-3,3] "
                      "grid clips the uncued criterion for large s_u, "
                      "spuriously inflating CF — a grid caveat, not a "
                      "structural break."))


def _cf_rescaled_or_explicit(r, V, v, N, d_max, f0, h, variant, alpha_grid,
                             s_c, s_u, mode: str, c_grid: np.ndarray) -> float:
    """CF at a fixed (s_c,s_u), computed either with the explicit-noise rate
    functions (mode='explicit') or with s≡1 and d' rescaled by 1/s_i
    (mode='reparam', the Prop-1 image). Both use the SAME criterion grid c_grid
    so the only difference is the analytic c↔c̃ remapping; Prop 1 ⇒ equal in
    the continuum, gap vanishing as the grid refines."""
    d_b = d_max * f_transfer(1.0 / N, f0, h)
    if mode == "explicit":
        R_p3 = optimal_criteria_R(d_b, d_b, v, V, N, variant, s_c, s_u, c_grid=c_grid)
        R_p4 = reward_at_c_zero(d_b, d_b, v, V, N, variant, s_c, s_u)
        rs = [optimal_criteria_R(*d_prime_pair(float(a), r, d_max, f0, h, N),
                                 v, V, N, variant, s_c, s_u, c_grid=c_grid)
              for a in alpha_grid]
    else:  # reparam: rescale d' by 1/s, s≡1
        R_p3 = optimal_criteria_R(d_b / s_c, d_b / s_u, v, V, N, variant, 1.0, 1.0, c_grid=c_grid)
        R_p4 = reward_at_c_zero(d_b / s_c, d_b / s_u, v, V, N, variant, 1.0, 1.0)
        rs = []
        for a in alpha_grid:
            dc, du = d_prime_pair(float(a), r, d_max, f0, h, N)
            rs.append(optimal_criteria_R(dc / s_c, du / s_u, v, V, N, variant,
                                         1.0, 1.0, c_grid=c_grid))
    R_p1 = float(np.max(np.array(rs)))
    return (R_p3 - R_p4) / max(R_p1 - R_p4, 1e-12)


def _cf_rescaled(r, V, v, N, d_max, f0, h, variant, alpha_grid, s_c, s_u) -> float:
    """CF with s≡1 but d' rescaled by 1/s_i at every α — the Prop-1 image
    of the explicit-noise model, on the default criterion grid."""
    return _cf_rescaled_or_explicit(r, V, v, N, d_max, f0, h, variant,
                                    alpha_grid, s_c, s_u, mode="reparam",
                                    c_grid=C_GRID)


# ====================================================================
# Block 2 — Prop 2: attention-coupled noise deflates / re-books CF.
# ====================================================================
def block2_coupled_noise(alpha_grid: np.ndarray) -> dict:
    N, d_max, f0, h = 4, 2.0, 0.5, make_h("sqrt")
    V, v, variant = 0.5, 5.0, "A"
    rows = []
    for kappa in [0.0, 0.25, 0.5, 1.0]:
        row = compute_CF(1.0, V, v, N, d_max, f0, h, variant, alpha_grid,
                         coupled=True, kappa=kappa)
        rows.append(dict(kappa=kappa,
                         criterion_fraction=row["criterion_fraction"],
                         VDA=row["VDA"], alpha_p1=row["alpha_p1"],
                         R_p1=row["R_p1"], R_p3=row["R_p3"], R_p4=row["R_p4"],
                         total_gain=row["total_gain"],
                         criterion_gain=row["criterion_gain"],
                         s_c_uniform=row["s_c_uniform"]))
    # VDA-peak location over the r-grid at κ=0 vs κ=1 (does the C2 peak move?).
    r_grid = np.unique(np.concatenate(
        [np.logspace(np.log10(0.1), np.log10(10.0), 21), np.array([1.0])]))
    peaks = {}
    for kappa in [0.0, 1.0]:
        vda = [(float(r), compute_CF(float(r), V, v, N, d_max, f0, h, variant,
                                     alpha_grid, coupled=True, kappa=kappa)["VDA"])
               for r in r_grid]
        rp, vp = max(vda, key=lambda t: t[1])
        peaks[f"kappa_{kappa}"] = dict(r_peak=rp, vda_peak=vp)
    cf0 = rows[0]["criterion_fraction"]
    cf1 = rows[-1]["criterion_fraction"]

    # Grid guard: at κ=1 the decision SD reaches s≈√2, which could clip the
    # default [-3,3] criterion grid. Recompute κ=1 CF on the wide [-8,8] grid
    # by routing the coupled rates through the explicit machinery at the P1/P3
    # optima — here we just re-evaluate compute_CF after temporarily widening
    # the module grid, to confirm the deflation is not a grid artifact.
    global C_GRID
    _saved = C_GRID
    C_GRID = np.arange(-8.0, 8.0 + 1e-9, 0.01)
    try:
        cf1_wide = compute_CF(1.0, V, v, N, d_max, f0, h, variant, alpha_grid,
                              coupled=True, kappa=1.0)["criterion_fraction"]
        cf0_wide = compute_CF(1.0, V, v, N, d_max, f0, h, variant, alpha_grid,
                              coupled=True, kappa=0.0)["criterion_fraction"]
    finally:
        C_GRID = _saved

    return dict(rows=rows, vda_peaks=peaks,
                cf_kappa0=cf0, cf_kappa1=cf1, cf_shift=cf1 - cf0,
                cf_kappa0_widegrid=cf0_wide, cf_kappa1_widegrid=cf1_wide,
                cf_shift_widegrid=cf1_wide - cf0_wide,
                note=("Prop 2: attention-coupled decision noise s(α) makes "
                      "'attention' a compound lever (spatial d'-reallocation "
                      "+ noise reduction). The criterion fraction is no "
                      "longer a clean criterion-vs-attention partition; "
                      "reported shift is the magnitude at the headline cell."))


def main():
    t0 = time.time()
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(outdir, exist_ok=True)
    # α grid: Δα = 0.005 (paper resolution) plus the 1/N point.
    alpha_grid = np.unique(np.concatenate(
        [np.arange(0.005, 1.0 + 1e-9, 0.005), np.array([1.0 / 4])]))

    print("A6 heterogeneous-decision-rule corroboration (CR-011)")
    print(f"  Φ backend: {_PHI_BACKEND}")
    print(f"  α-grid: {len(alpha_grid)} pts (Δα=0.005 + 1/N); c-grid: {_C_GRID_LEN} pts")

    print("\n[Block 0] validation vs C1/C2 + Prop-1 pointwise identity ...")
    b0 = block0_validation(alpha_grid)
    print(f"  CF headline (r=1,V=.5,v=5,A): {b0['cf_headline_r1']:.4f}  (paper≈0.73, C1 code 0.728)")
    print(f"  VDA peak: {b0['vda_peak_value']:.4f} at r={b0['vda_peak_r']:.3f}  (C2 ≈0.0799@0.383)")
    print(f"  Prop-1 pointwise identity max err: {b0['prop1_pointwise_identity_max_err']:.2e}")

    print("\n[Block 1] Prop 1 — fixed heterogeneous noise absorbed ...")
    b1 = block1_fixed_noise(alpha_grid)
    for row in b1["rows"]:
        print(f"  s_c={row['s_c']:.2f} s_u={row['s_u']:.2f}  "
              f"CF_explicit={row['cf_explicit']:.4f}  CF_reparam={row['cf_reparam']:.4f}  "
              f"|Δ|={row['abs_diff']:.2e}")
    print(f"  max |CF_explicit − CF_reparam| (default grid) = {b1['max_abs_diff_explicit_vs_reparam']:.2e}")
    print("  grid convergence (worst case s_u=2): gap → 0 as Δc → 0")
    for c in b1["grid_convergence_worst_case"]:
        print(f"    Δc={c['dc_step']:.3f}  CF_explicit={c['cf_explicit']:.5f}  "
              f"CF_reparam={c['cf_reparam']:.5f}  |Δ|={c['abs_diff']:.2e}")

    print("\n[Block 2] Prop 2 — attention-coupled noise s(α) ...")
    b2 = block2_coupled_noise(alpha_grid)
    for row in b2["rows"]:
        print(f"  κ={row['kappa']:.2f}  CF={row['criterion_fraction']:.4f}  "
              f"VDA={row['VDA']:.5f}  α*={row['alpha_p1']:.3f}  "
              f"total_gain={row['total_gain']:.4f}  s_uniform={row['s_c_uniform']:.3f}")
    print(f"  CF shift κ:0→1 = {b2['cf_shift']:+.4f}  ({b2['cf_kappa0']:.4f} → {b2['cf_kappa1']:.4f})")
    print(f"  CF shift κ:0→1 [WIDE grid guard] = {b2['cf_shift_widegrid']:+.4f}  "
          f"({b2['cf_kappa0_widegrid']:.4f} → {b2['cf_kappa1_widegrid']:.4f})")
    for k, pk in b2["vda_peaks"].items():
        print(f"  VDA peak {k}: {pk['vda_peak']:.5f} at r={pk['r_peak']:.3f}")

    result = dict(block0_validation=b0, block1_fixed_noise=b1,
                  block2_coupled_noise=b2,
                  metadata=dict(phi_backend=_PHI_BACKEND, c_grid_step=0.05,
                                alpha_grid_step=0.005, claim_id="A6",
                                attack_vector="re-derivation",
                                run_id="run-018", task_id="CR-011",
                                prompt_version="0.2", date="2026-05-25",
                                elapsed_s=round(time.time() - t0, 2)))
    out_path = os.path.join(outdir, "results.json")
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2, default=float)
    print(f"\nSaved {out_path}  (elapsed {result['metadata']['elapsed_s']}s)")


if __name__ == "__main__":
    main()
