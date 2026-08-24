"""
Rebuild/model/core.py — the rebuilt VDA model (v2).

Status: bootstrap increment, run rb-001 (2026-05-25), prompt v0.2.

This module is the rebuilt paper's *canonical* model implementation.  It
extends the inherited Herman-Lab model (Critique/source/main.pdf,
2026-04-09) along the single axis the skeptical reviewer's A1 verdict
identified as the most consequential: **per-location decision
independence is promoted to a tunable equicorrelation parameter rho**.
The inherited model (independent SDT decisions, paper Eq. 9) is exactly
recovered as the rho=0 limit, to machine tolerance — this is the
recovery test in tests/test_recovery.py, the contract on every future
extension of this module.

The reviewer validated the same numerical machinery in
    Critique/replications/A1--correlated-fa/run.py   (run-017, CR-052)
producing the headline numbers (peak VDA ~ 0.0797 at r ~ 0.398, rho=0;
CF(r=0.398, rho=0) = 0.8295) that the inherited paper reports.  The
present file lifts that validated code out of a one-off script into a
library that the rebuild's simulations, derivations, and (eventually)
manuscript figures will share.  Per the mission's simulation mandate
(agents/paper_rebuilder_prompt.md sec.5) we never reimplement what has
already been validated; we copy with attribution and extend.

====================================================================
MATHEMATICAL FORMULATION (inherited model + rho channel)
====================================================================

N spatial locations.  One ("cued", index c) is cued with value v >= 1 and
validity V in [1/N, 1] — i.e. P(change at the cued slot | change trial) =
V.  The remaining N-1 ("uncued", index u) split the residual probability
1-V uniformly.

Per-location signal-detection theory (paper sec.2.1, Eqs. 1-2):

    HR(d', c)  = Phi(d'/2 - c)
    FAR(d', c) = Phi(-d'/2 - c)

with equal-variance Gaussian decision variables and a per-location
decision criterion c.  On a NO-CHANGE trial the decision variable X_i is
distributed N(-d'_i / 2, 1) and a false alarm at location i is the event
{X_i > c_i}, so

    1 - FAR_i = Phi(c_i + d'_i / 2) =: Phi(b_i),
    b_i := c_i + d'_i / 2     (z-score threshold, no-FA-side)

ATTENTION ALLOCATION.  A scalar alpha in [1/N, 1] is the proportion of
attention placed on the cued location; (1-alpha)/(N-1) is the per-
location uncued share.  A transfer function f maps allocation to
per-location sensitivity scale,

    f(a) = f_0 + (1 - f_0) h(a),   f_0 in [0, 1],  h: [0,1] -> [0,1]

with h the family parameter (sqrt, linear, p^0.3, p^2 reported in the
paper).  An asymmetric mapping (paper sec.2.4) lets attentional benefit
and cost differ:

    d'_c = d'_base + beta(r) * (d'_max f(alpha)        - d'_base)
    d'_u = d'_base + gamma(r) * (d'_max f((1-alpha)/(N-1)) - d'_base)
    d'_base := d'_max f(1/N)

with beta(r) = 2r/(r+1), gamma(r) = 2/(r+1), so beta + gamma = 2 (paper's
additive conservation, assumption A3) and beta/gamma = r is the
benefit-to-cost asymmetry ratio.  r > 1 is benefit-dominant, r < 1 is
cost-dominant, r = 1 is symmetric.

CONSERVATION FAMILY (this module's A3 upgrade, rb-015).  The paper fixes
the conservation rule once and for all (beta + gamma = 2).  The reviewer
(verdict A3, CONTESTED) shows that swapping it for the multiplicative
form beta*gamma = 1 quantitatively shifts the criterion-fraction
distribution — the criterion-subordinate fraction roughly doubles
(4.0%->8.3% of 4,410 cells).  The rebuild therefore treats conservation
as a tunable parameter rather than a fixed assumption.

We use the **power-mean conservation family** of order p, defined by

    M_p(beta, gamma) := ((beta^p + gamma^p) / 2)^(1/p)  =  1      (p != 0)
    M_0(beta, gamma) := sqrt(beta * gamma)              =  1      (p = 0)

together with beta/gamma = r > 0.  Closed-form solution:

    gamma(r, p) = (2 / (r^p + 1))^(1/p),   beta(r, p) = r * gamma  (p != 0)
    gamma(r, 0) = 1 / sqrt(r),             beta(r, 0) = sqrt(r)    (p = 0)

Special cases recovered exactly:

    p =  1: M_1 is the arithmetic mean ==> beta + gamma = 2  (additive, paper)
            -> gamma = 2/(r+1), beta = 2r/(r+1).
    p =  0: M_0 is the geometric mean  ==> beta * gamma = 1  (multiplicative)
            -> gamma = 1/sqrt(r),  beta = sqrt(r).
    p = -1: M_{-1} is the harmonic mean ==> 2 beta gamma / (beta + gamma) = 1.
    p ->  +inf: M_inf is the max ==> max(beta, gamma) = 1.
    p -> -inf: M_-inf is the min ==> min(beta, gamma) = 1.

p = 1 is the rebuilt model's *default* (back-compat with the inherited
paper; the recovery contract for cons_p=1.0 is byte-for-byte against the
old beta_gamma(r) shortcut).  p = 0 is the reviewer's multiplicative
alternative.  Intermediate p values trace a smooth one-parameter band of
conservation rules between the two; the rebuilt manuscript reports
headline numbers as a band across p (A3 row of the claim ledger).

Invariants for all p:
  - beta(r, p) / gamma(r, p) = r exactly (ratio fixed by definition).
  - beta(1, p) = gamma(1, p) = 1 for all p (symmetric corner unaffected).
  - At r = 1, M_p(1, 1) = 1 for all p.  Conservation choice is invisible
    at r = 1 — the C5 symmetric-recovery result is conservation-form
    -invariant by construction.

EXPECTED REWARD (paper sec.2.5, Eq. 9):

    E[R] = 0.5 [ V * HR_c * v + (1 - V) * HR_u ]      (change-trial term)
         + 0.5 * P_no-fa * CR                          (no-change term)

where CR is the correct-rejection reward.  Two reward conventions:

    variant A:  CR = V * v + (1 - V)     (value-scaled CR)
    variant B:  CR = 1                   (uniform CR)

The change-trial term is *linear* in the marginal hit rates HR_c, HR_u —
on a change trial the change is at exactly one location, so the
detection reward never forms a cross-location product.  INDEPENDENCE
(A1) therefore enters E[R] in EXACTLY ONE place: the joint no-false-
alarm probability P_no-fa on a no-change trial, which the paper writes
as the product

    P_no-fa^indep = Phi(b_c) * Phi(b_u)^(N-1).         (paper Eq. 9)

CORRELATED EXTENSION (this module's headline upgrade).  Promote the
no-change-trial decision variables to an EQUICORRELATED Gaussian with
common pairwise correlation rho in [0, 1):

    X_i = -d'_i/2 + sqrt(rho) * Z + sqrt(1 - rho) * eps_i,
    Z, eps_i ~ N(0, 1) i.i.d.

This is a one-factor representation: a single shared latent Z carries
all cross-location covariance, conditional on which the locations are
independent (the standard equicorrelated-Gaussian reduction).  Then

    P_no-fa(rho) = INT  Phi((b_c - sqrt(rho) z) / sqrt(1 - rho))
                       * Phi((b_u - sqrt(rho) z) / sqrt(1 - rho))^(N-1)
                       * phi(z) dz                                   (*)

i.e. a 1-D quadrature over the shared latent.  No multivariate-normal
CDF is needed; (*) is *exact*, not an approximation.  At rho = 0 the
integrand factorises and (*) collapses bit-for-bit to Phi(b_c) Phi(b_u)
^(N-1) — the paper's Eq. 9 — which is the recovery test (see
tests/test_recovery.py).

SLEPIAN MONOTONICITY (Slepian 1962).  For a Gaussian orthant probability
P(forall i: X_i <= c_i), raising any off-diagonal correlation raises the
probability.  In equicorrelation this gives

    rho_1 <= rho_2  ==>  P_no-fa(rho_1) <= P_no-fa(rho_2)

so the independent corner rho = 0 is the FA-penalty-maximising corner.
This is a sanity check exposed by core_slepian_curve() and reused by
sims/A1--*.

CRITERION GRID.  The paper uses a coarse grid (Delta c = 0.05) over c in
[-3, 3] for the inner per-location criterion optimisation; we keep the
same grid for byte-level continuity with the reviewer's replication
substrate.  The outer alpha optimisation is a 0.005-step grid over
[1/N, 1].  Both grids are exposed as module-level constants so callers
can swap them out without forking.

CONVENTIONS, SHAPES, NUMERICS.
- All shapes commented inline as (n_c, n_c) etc.  No hidden broadcasts.
- Gauss-Hermite quadrature at nq=64 nodes (Sigma w_n = 1 exactly to
  double precision; checked vs nq=128 in the reviewer's run-017 to
  ~1e-16 max diff — products of Phi are smooth, so 64 is way past
  convergence).
- d'_i clamped at 0 (the inherited model already does this; "negative
  d'" is unphysical, and the asymmetric mapping can drive d'_c < 0 at
  alpha < 1/N when r < 1).
- Phi via scipy.special.ndtr if available (full double precision); A&S
  7.1.26 numpy fallback otherwise.  Both rho = 0 and rho > 0 call the
  same Phi so any approximation error is common-mode and cancels in
  rho-trend comparisons.

ATTRIBUTION.  All primitives lifted with attribution from
Critique/replications/A1--correlated-fa/run.py (CR-052, run-017) and the
upstream
    Critique/replications/C1--criterion-fraction-floor/run.py
    Critique/replications/C5--symmetric-recovery/run.py
which the reviewer's verdict ledger already validates byte-for-byte
against the inherited paper's headline numbers.  We do not re-derive
what has been validated; we re-expose it as a library and add the
recovery contract (tests/test_recovery.py).

Extensions to consider (later rebuild increments, queued in
Rebuild/REBUILD_BACKLOG.md):
- Heterogeneous r_i (A2/A8): allow per-location r_i in d_prime_asym(),
  and an N-dimensional uncued allocation in place of homogeneous
  (1-alpha)/(N-1).
- Attention-coupled decision noise (A6, if it lands): per-location
  decision-noise scaling sigma_i(alpha) that the criterion-fraction
  metric currently mis-books to attention.
- Structured Sigma (run-017 follow-up): non-equicorrelated covariance
  (block / cued-vs-uncued / signed-rho) to bracket the run-017
  benefit-dominant amplification magnitude.

Done so far:
- A1 rho channel (rb-001).
- A3 conservation family (rb-015): power-mean parameter cons_p; p=1
  reproduces inherited additive form byte-for-byte (back-compat), p=0
  recovers multiplicative beta*gamma=1 to ULP tolerance against the
  reviewer's A3 numbers (tests/test_conservation_family.py).
- A2 heterogeneous-r d'-map (rb-019): d_prime_hetero(alloc, r_vec, ...)
  returns an N-vector of per-location d'_i under a per-location ratio
  vector r_i.  The single-r asymmetric mapping is recovered byte-for-
  byte when r_vec is uniform and alloc is the canonical homogeneous
  form (alpha, (1-alpha)/(N-1), ..., (1-alpha)/(N-1)) — see
  tests/test_heterogeneous_r.py.  Downstream pipeline (P_no-fa,
  optimal_R, policies) remains scalar in (d_c, d_u); promoting it to
  the heterogeneous regime is a separate increment (RB-017).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np

# --------------------------------------------------------------------
# Phi (standard normal CDF).  scipy when present; A&S 7.1.26 fallback.
# --------------------------------------------------------------------
_SQRT2 = math.sqrt(2.0)

try:
    from scipy.special import ndtr as _ndtr

    def Phi(x):  # type: ignore[no-redef]
        return _ndtr(np.asarray(x, dtype=float))

    PHI_BACKEND = "scipy.special.ndtr"
except ImportError:  # pragma: no cover
    _A1, _A2, _A3, _A4, _A5 = (0.254829592, -0.284496736, 1.421413741,
                               -1.453152027, 1.061405429)
    _P = 0.3275911

    def _erf_np(x_arr: np.ndarray) -> np.ndarray:
        x_abs = np.abs(x_arr)
        t = 1.0 / (1.0 + _P * x_abs)
        poly = ((((_A5 * t + _A4) * t + _A3) * t + _A2) * t + _A1) * t
        y = 1.0 - poly * np.exp(-x_abs * x_abs)
        return np.where(x_arr >= 0.0, y, -y)

    def Phi(x):  # type: ignore[no-redef]
        arr = np.asarray(x, dtype=float)
        return 0.5 * (1.0 + _erf_np(arr / _SQRT2))

    PHI_BACKEND = "A&S 7.1.26 numpy-vectorised"


# --------------------------------------------------------------------
# Transfer function family h: [0,1] -> [0,1].  (paper Table for sec.2.3)
# --------------------------------------------------------------------
def make_h(name: str) -> Callable:
    """Family member by name.  Domain a in [0, 1]."""
    if name == "sqrt":
        return lambda a: np.sqrt(a)
    if name == "linear":
        return lambda a: a
    if name == "p0_3":
        return lambda a: np.power(a, 0.3)
    if name == "p2":
        return lambda a: np.power(a, 2.0)
    raise ValueError(f"unknown transfer-function name: {name!r}")


def f_transfer(a, f0: float, h: Callable):
    """f(a) = f_0 + (1 - f_0) h(a) in [f_0, 1]."""
    return f0 + (1.0 - f0) * h(a)


def beta_gamma(r: float, p: float = 1.0) -> tuple[float, float]:
    """Power-mean conservation family (A3 generalisation).

    Constraint: M_p(beta, gamma) = 1, with M_p the generalised mean of
    order p (see module docstring "CONSERVATION FAMILY"); beta/gamma = r.

    Parameters
    ----------
    r : float
        Benefit/cost asymmetry ratio, beta/gamma.  r > 0.
    p : float
        Order of the generalised mean.  p = 1 (default) is the paper's
        additive conservation (beta + gamma = 2); p = 0 is the
        multiplicative alternative (beta * gamma = 1); p < 0 is admitted
        as a continuous extension (harmonic at p = -1).  At p = 1 the
        evaluation reduces to the inherited closed form, byte-for-byte.

    Returns
    -------
    beta, gamma : float
        Asymmetric scaling factors satisfying M_p(beta, gamma) = 1 and
        beta/gamma = r.

    Numerics
    --------
    The p = 1 branch is a literal return of the paper's expressions (no
    `**` operator), so additive recovery is *binary* identical to the
    pre-rb-015 model output.  The p = 0 branch uses math.sqrt, also exact
    in IEEE 754 for finite positive r.  General p uses two `**`s; small
    |p| is handled by a tolerance branch (|p| < 1e-12) routing to the
    geometric-mean closed form to avoid the 1/p blow-up.
    """
    if p == 1.0:
        # Additive (paper A3): byte-for-byte recovery of the inherited form.
        return 2.0 * r / (r + 1.0), 2.0 / (r + 1.0)
    if abs(p) < 1e-12:
        # Geometric mean (multiplicative beta*gamma = 1).
        sqrt_r = math.sqrt(r)
        return sqrt_r, 1.0 / sqrt_r
    # General power-mean: gamma^p (r^p + 1) = 2  =>  gamma = (2/(r^p+1))^(1/p).
    gamma = (2.0 / (r ** p + 1.0)) ** (1.0 / p)
    return r * gamma, gamma


def d_prime_asym(alpha: float, r: float, d_max: float, f0: float,
                 h: Callable, N: int, p: float = 1.0) -> tuple[float, float]:
    """Asymmetric d'(alpha) map (paper sec.2.4), clamped >= 0.

    Returns (d'_c, d'_u).  At alpha < 1/N the role of (beta, gamma) flips
    (paper sec.2.4); the rebuild keeps this branch for completeness but
    operates on alpha >= 1/N in every reported sim (cf. C4 no-inversion).

    Parameters
    ----------
    alpha, r, d_max, f0, h, N : as before.
    p : conservation order (A3 generalisation; see beta_gamma).  Default
        1.0 reproduces the inherited additive form.
    """
    beta, gamma = beta_gamma(r, p)
    d_base = d_max * f_transfer(1.0 / N, f0, h)
    if alpha >= 1.0 / N:
        d_c = d_base + beta * (d_max * f_transfer(alpha, f0, h) - d_base)
        d_u = d_base + gamma * (
            d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h) - d_base)
    else:
        d_c = d_base + gamma * (d_max * f_transfer(alpha, f0, h) - d_base)
        d_u = d_base + beta * (
            d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h) - d_base)
    return float(max(d_c, 0.0)), float(max(d_u, 0.0))


# --------------------------------------------------------------------
# A2 / A8 heterogeneous-r d' map (rb-019).
#
# The inherited paper governs the benefit/cost asymmetry by a SINGLE
# GLOBAL ratio `r` (A2).  The reviewer's verdict A2 (CONFIRMED-
# CONDITIONAL) decomposes this into two readings:
#   - BETWEEN-PREPARATION:  one effective `r` per fixed preparation —
#     what the published r-sweep operationalises.  Benign.
#   - WITHIN-DISPLAY:       one `r` for all locations / features / time
#     at once.  Empirically false (CR-007: within-display heterogeneity
#     R2 is real); rebuild action is to admit per-location r_i as a
#     model EXTENSION with its own analysis.
#
# The natural generalisation, fixed by paper Eqs. (7)-(8) and the §2.3
# reversal note (with the global r promoted to a vector r_i), is
#
#     d'_i = max( d'_base + s_i (d'_max f(a_i) - d'_base),  0 )
#     s_i  = beta(r_i, p)   if a_i >= 1/N   (gain branch)
#          = gamma(r_i, p)  if a_i <  1/N   (loss branch)
#
# Notes:
#   - d'_base = d'_max f(1/N) is r-INDEPENDENT, so a per-location r_i
#     changes only the per-location SCALING s_i of the departure, never
#     the common baseline (matches the reviewer's CR-048 derivation).
#   - The per-slot gain/loss branch criterion `a_i >= 1/N` is the
#     correct generalisation of d_prime_asym's `alpha >= 1/N`:
#       * Homogeneous alloc, alpha > 1/N: cued (a_0 > 1/N) -> beta;
#         uncued (a_i < 1/N) -> gamma  (matches d_prime_asym's if-branch).
#       * Homogeneous alloc, alpha < 1/N: cued (a_0 < 1/N) -> gamma;
#         uncued (a_i > 1/N) -> beta  (matches the else-branch).
#       * Homogeneous alloc, alpha = 1/N: every a_i = 1/N exactly, the
#         departure d'_max f(1/N) - d'_base = 0 vanishes identically,
#         and the choice of s_i is irrelevant.
#   - The conservation order `p` propagates through beta_gamma(r_i, p)
#     unchanged: at p=1 (additive, paper) the recovery is byte-for-byte
#     against d_prime_asym; at any other p the per-location (beta_i,
#     gamma_i) trace the same conservation family in r_i.
#
# Recovery contract (tests/test_heterogeneous_r.py):
#   For uniform r_vec = (r, r, ..., r) and canonical homogeneous alloc
#   (alpha, (1-alpha)/(N-1), ..., (1-alpha)/(N-1)), d_prime_hetero
#   returns (d_c, d_u, d_u, ..., d_u) where (d_c, d_u) equals the legacy
#   d_prime_asym(alpha, r, ...) output to BINARY equality, across the
#   full alpha grid, r in {0.1, 0.3, 0.398, 1, 3.162, 10}, and
#   p in {0, 0.5, 1}.  This is the contract every A2/A8 sim is built
#   against.
# --------------------------------------------------------------------
def d_prime_hetero(alloc: Sequence[float],
                   r_vec: Sequence[float] | float,
                   d_max: float, f0: float, h: Callable, N: int,
                   p: float = 1.0) -> np.ndarray:
    """Per-location asymmetric d'(a_i) map under heterogeneous r_i.

    Parameters
    ----------
    alloc : length-N sequence of floats
        Per-location attention allocation a_i.  Should satisfy
        sum(alloc) ~ 1 with each a_i in [0, 1]; callers enforce the
        simplex.  Index convention: slot 0 = cued, slots 1..N-1 = uncued
        (matching the inherited paper's notation, but no slot is
        privileged by this function — every a_i / r_i is treated
        symmetrically).
    r_vec : length-N sequence of floats, OR a scalar
        Per-location benefit/cost asymmetry ratio.  A scalar is
        broadcast to a uniform vector (homogeneous-r reduction).  Each
        r_i > 0.
    d_max, f0, h, N : as in d_prime_asym.
    p : conservation order (A3 generalisation; default 1.0 = paper
        additive).  Forwarded to beta_gamma(r_i, p) at each location.

    Returns
    -------
    d_prime : ndarray of shape (N,)
        Per-location d'_i, clamped >= 0.  Float dtype.

    Numerics
    --------
    Each d'_i is computed in scalar (python-float) arithmetic, with the
    same operand order as d_prime_asym for the homogeneous-r reduction,
    so the recovery against (d_c, d_u) is binary-exact (no numpy-type
    coercion in the intermediate steps).
    """
    alloc_arr = np.asarray(alloc, dtype=float)
    if alloc_arr.shape != (N,):
        raise ValueError(
            f"alloc must have shape ({N},); got {alloc_arr.shape}")
    r_arr = np.asarray(r_vec, dtype=float)
    if r_arr.ndim == 0:
        r_arr = np.full(N, float(r_arr))
    elif r_arr.shape != (N,):
        raise ValueError(
            f"r_vec must be a scalar or shape ({N},); got {r_arr.shape}")
    d_base = d_max * f_transfer(1.0 / N, f0, h)
    out = np.empty(N, dtype=float)
    inv_N = 1.0 / N
    for i in range(N):
        a_i = float(alloc_arr[i])
        r_i = float(r_arr[i])
        beta_i, gamma_i = beta_gamma(r_i, p)
        s_i = beta_i if a_i >= inv_N else gamma_i
        # Match d_prime_asym operand order EXACTLY for byte-for-byte recovery.
        d_i = d_base + s_i * (d_max * f_transfer(a_i, f0, h) - d_base)
        out[i] = max(d_i, 0.0)
    return out


def canonical_alloc(alpha: float, N: int) -> np.ndarray:
    """Build the length-N canonical homogeneous-allocation vector.

    Convention: slot 0 cued (a_0 = alpha), slots 1..N-1 uncued each
    holding (1 - alpha) / (N - 1).  Used to test the homogeneous-r
    recovery contract and as a starting point for A8 N-dim uncued
    allocation sweeps.
    """
    a = np.empty(N, dtype=float)
    a[0] = float(alpha)
    a[1:] = (1.0 - float(alpha)) / (N - 1)
    return a


# --------------------------------------------------------------------
# Criterion grid (paper Delta c = 0.05; reviewer's substrate uses the
# same grid byte-for-byte, so we inherit it).
# --------------------------------------------------------------------
C_GRID = np.arange(-3.0, 3.0 + 1e-9, 0.05)          # 121 points


# --------------------------------------------------------------------
# Gauss-Hermite quadrature for INT g(z) phi(z) dz, phi(z) = e^{-z^2/2}/sqrt(2 pi).
# Substituting z = sqrt(2) t maps the physicists' Hermite rule
#     INT e^{-t^2} f(t) dt ~= sum_k w_k f(t_k)       (np.polynomial.hermite.hermgauss)
# to  INT g(z) phi(z) dz ~= (1/sqrt(pi)) sum_k w_k g(sqrt(2) t_k).
# Products of Phi are smooth ==> nq=64 is far past convergence (see
# reviewer's run-017 GH64 vs GH128 maxdiff ~ 1e-16).
# --------------------------------------------------------------------
def gauss_hermite(nq: int = 64):
    """Return (z_nodes, weights) for INT g(z) phi(z) dz, Sigma weights = 1."""
    t, w = np.polynomial.hermite.hermgauss(nq)        # weight e^{-t^2}
    z = _SQRT2 * t                                    # nodes for phi(z)
    wn = w / math.sqrt(math.pi)                       # Sigma wn = 1 exactly
    return z, wn


_GH_Z, _GH_W = gauss_hermite(64)
GH_NQ = len(_GH_Z)


# --------------------------------------------------------------------
# P_no-fa(rho) on the full (c_c, c_u) criterion grid.
#
# Shapes:
#   b_c[i] = C_GRID[i] + d_c / 2          (n_c,)
#   b_u[j] = C_GRID[j] + d_u / 2          (n_c,)
# Output:
#   P[i, j] = INT Phi((b_c[i] - sqrt(rho) z) / sqrt(1-rho))
#               * Phi((b_u[j] - sqrt(rho) z) / sqrt(1-rho))^(N-1)
#               * phi(z) dz
# Vectorised path: Gc (n_c, nq), Gu (n_c, nq), then P = (Gc * w) @ Gu.T.
# At rho = 0 the integrand factorises and we shortcut to the outer
# product Phi(b_c)[:, None] * Phi(b_u)[None, :]^(N-1) — the exact paper
# Eq. 9 expression.
# --------------------------------------------------------------------
def p_no_fa_grid(d_c: float, d_u: float, N: int, rho: float) -> np.ndarray:
    """Correlated no-FA probability over the (c_c, c_u) grid; rho in [0, 1)."""
    b_c = C_GRID + d_c / 2.0                          # (n_c,)
    b_u = C_GRID + d_u / 2.0                          # (n_c,)
    if rho <= 0.0:
        # Exact independent product (paper Eq. 9).
        return Phi(b_c)[:, None] * (Phi(b_u)[None, :] ** (N - 1))
    s = math.sqrt(1.0 - rho)
    rs = math.sqrt(rho)
    z = _GH_Z[None, :]                                # (1, nq)
    Gc = Phi((b_c[:, None] - rs * z) / s)             # (n_c, nq)
    Gu = Phi((b_u[:, None] - rs * z) / s) ** (N - 1)   # (n_c, nq)
    return (Gc * _GH_W[None, :]) @ Gu.T               # (n_c, n_c)


def p_no_fa_point(d_c: float, d_u: float, N: int, rho: float,
                  c_c: float, c_u: float) -> float:
    """Single-cell version (used by floor_R for the P4 policy)."""
    b_c = c_c + d_c / 2.0
    b_u = c_u + d_u / 2.0
    if rho <= 0.0:
        return float(Phi(b_c) * Phi(b_u) ** (N - 1))
    s = math.sqrt(1.0 - rho)
    rs = math.sqrt(rho)
    gc = Phi((b_c - rs * _GH_Z) / s)
    gu = Phi((b_u - rs * _GH_Z) / s) ** (N - 1)
    return float(np.sum(_GH_W * gc * gu))


# --------------------------------------------------------------------
# R*(d_c, d_u) — expected reward maximised over (c_c, c_u) on the grid.
# Hit terms are rho-independent (marginal); only P_no-fa carries rho.
# --------------------------------------------------------------------
def optimal_R(d_c: float, d_u: float, v: float, V: float, N: int,
              variant: str, rho: float) -> float:
    """Maximise E[R] over the criterion grid; return the optimum value."""
    hr_c = Phi(d_c / 2.0 - C_GRID)                    # (n_c,)
    hr_u = Phi(d_u / 2.0 - C_GRID)                    # (n_c,)
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    p_nofa = p_no_fa_grid(d_c, d_u, N, rho)           # (n_c, n_c)
    er = (0.5 * (V * v * hr_c[:, None] + (1.0 - V) * hr_u[None, :])
          + 0.5 * cr * p_nofa)
    return float(er.max())


def floor_R(d_c: float, d_u: float, v: float, V: float, N: int,
            variant: str, rho: float) -> float:
    """P4 floor reward: alpha = 1/N (set by caller via d_c, d_u), c_c = c_u = 0."""
    hr_c = float(Phi(d_c / 2.0 - 0.0))
    hr_u = float(Phi(d_u / 2.0 - 0.0))
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    p_nofa = p_no_fa_point(d_c, d_u, N, rho, 0.0, 0.0)
    return 0.5 * (V * v * hr_c + (1.0 - V) * hr_u) + 0.5 * cr * p_nofa


# --------------------------------------------------------------------
# Policy structure (P1 - P4) and the headline metrics VDA, CF.
# --------------------------------------------------------------------
@dataclass(frozen=True)
class HeadlineCell:
    """Parameters of one (V, v, N, ...) cell at which to evaluate policies.

    `cons_p` selects the conservation family member (A3 generalisation;
    see beta_gamma).  Default 1.0 = additive (paper's A3), preserving
    byte-for-byte recovery against the inherited model.  cons_p = 0.0 =
    multiplicative; intermediate values trace a smooth band of
    conservation rules between the two.
    """
    N: int = 4
    d_max: float = 2.0
    f0: float = 0.5
    h_name: str = "sqrt"
    V: float = 0.5
    v: float = 5.0
    variant: str = "A"
    rho: float = 0.0
    cons_p: float = 1.0


def default_alpha_grid(N: int) -> np.ndarray:
    """alpha grid: [1/N, 1] step 0.005, rounded to 6 dp for hash stability."""
    return np.round(np.arange(1.0 / N, 1.0 + 1e-9, 0.005), 6)


def _alpha_opt(r: float, v: float, V: float, N: int, d_max: float, f0: float,
               h: Callable, variant: str, rho: float,
               alpha_grid: np.ndarray, p: float = 1.0
               ) -> tuple[float, float]:
    """Brute-force outer optimisation over the alpha grid.

    `p` is the A3 conservation order (default 1.0 = additive = paper).
    """
    rs = np.empty(len(alpha_grid))
    for k, a in enumerate(alpha_grid):
        d_c, d_u = d_prime_asym(float(a), r, d_max, f0, h, N, p)
        rs[k] = optimal_R(d_c, d_u, v, V, N, variant, rho)
    idx = int(np.argmax(rs))
    return float(alpha_grid[idx]), float(rs[idx])


def policies(r: float, cell: HeadlineCell,
             alpha_grid: np.ndarray | None = None) -> dict:
    """Evaluate P1-P4 + headline metrics at (r, cell).

    P1: jointly optimal (alpha, c_c, c_u) at the cell's v.
    P2: alpha frozen at the value-blind alpha*(v=1); criteria re-optimised at v.
    P3: alpha = 1/N (uniform attention); criteria optimised.
    P4: alpha = 1/N, c_c = c_u = 0.

    VDA   := R(P1) - R(P2)         (value-directed-attention benefit)
    CF    := [R(P3) - R(P4)] / [R(P1) - R(P4)]  (criterion fraction)

    Returns a dict of all four rewards, VDA, CF, and the optimising
    alpha values.  Conservation order is taken from `cell.cons_p`
    (default 1.0 = additive A3 = paper).
    """
    h = make_h(cell.h_name)
    N = cell.N
    p = cell.cons_p
    if alpha_grid is None:
        alpha_grid = default_alpha_grid(N)

    # P1: joint optimum at v
    a1, R_P1 = _alpha_opt(r, cell.v, cell.V, N, cell.d_max, cell.f0,
                          h, cell.variant, cell.rho, alpha_grid, p)
    # value-blind alpha*(v=1) reference
    a_vb, _ = _alpha_opt(r, 1.0, cell.V, N, cell.d_max, cell.f0,
                         h, cell.variant, cell.rho, alpha_grid, p)
    # P2: criteria re-optimised at v, alpha frozen at value-blind a_vb
    d_c_vb, d_u_vb = d_prime_asym(a_vb, r, cell.d_max, cell.f0, h, N, p)
    R_P2 = optimal_R(d_c_vb, d_u_vb, cell.v, cell.V, N, cell.variant, cell.rho)
    # P3: alpha = 1/N, criteria optimised
    d_c_u, d_u_u = d_prime_asym(1.0 / N, r, cell.d_max, cell.f0, h, N, p)
    R_P3 = optimal_R(d_c_u, d_u_u, cell.v, cell.V, N, cell.variant, cell.rho)
    # P4: alpha = 1/N, c = 0
    R_P4 = floor_R(d_c_u, d_u_u, cell.v, cell.V, N, cell.variant, cell.rho)

    vda = R_P1 - R_P2
    denom = R_P1 - R_P4
    cf = (R_P3 - R_P4) / denom if abs(denom) > 1e-12 else float("nan")
    return dict(alpha_P1=a1, alpha_vb=a_vb,
                R_P1=R_P1, R_P2=R_P2, R_P3=R_P3, R_P4=R_P4,
                VDA=vda, CF=cf)


# --------------------------------------------------------------------
# Convenience sweeps used by tests/sims.
# --------------------------------------------------------------------
def r_grid_log(lo: float = 0.1, hi: float = 10.0, n: int = 25,
               include: Sequence[float] = (0.316, 0.398, 1.0, 3.162)
               ) -> np.ndarray:
    """Log-spaced r grid with the C2 reference points pinned in."""
    g = np.geomspace(lo, hi, n)
    for extra in include:
        if not np.any(np.isclose(g, extra, rtol=1e-3)):
            g = np.append(g, extra)
    return np.unique(np.round(g, 6))


def vda_curve(cell: HeadlineCell, r_grid: np.ndarray | None = None
              ) -> tuple[np.ndarray, np.ndarray]:
    """Return (r_grid, VDA(r)) at the given cell.  Sweeps r at fixed rho."""
    if r_grid is None:
        r_grid = r_grid_log()
    out = np.empty_like(r_grid, dtype=float)
    for k, r in enumerate(r_grid):
        out[k] = policies(float(r), cell)["VDA"]
    return r_grid, out


def slepian_curve(d_c: float = 1.8, d_u: float = 1.2, N: int = 4,
                  c_c: float = 0.5, c_u: float = 0.5,
                  rhos: Sequence[float] = (0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8)
                  ) -> list[tuple[float, float]]:
    """Slepian sanity: P_no-fa(rho) at a fixed (d_c, d_u, c_c, c_u) cell.

    Should be non-decreasing in rho, with rho=0 the minimum.  Returns
    [(rho, P_no-fa(rho)), ...] in caller-supplied order.
    """
    out = []
    for rho in rhos:
        P = p_no_fa_point(d_c, d_u, N, rho, c_c, c_u)
        out.append((float(rho), P))
    return out


# ====================================================================
# A8 / A2 GENERAL POLICY LAYER — N-dim heterogeneous (alloc, valid, r_vec).
#
# Added rb-020 (RB-017).  The functions above assume a 1-D allocation
# space (alpha for the cued slot, uniform (1-alpha)/(N-1) on each uncued
# slot).  The reviewer's A8 verdict (CONFIRMED-CONDITIONAL) makes the
# homogeneity *conditional on* A2 (single global r) and on the cued
# slot's value-weight dominance — under unequal validity or per-location
# r_i, homogeneity stops being the unconstrained optimum, and the
# rebuilt paper's §extensions must score policies over a wider space.
#
# This block lifts the reviewer's A8 grouped-criterion optimiser
# (Critique/replications/A8--heterogeneous-uncued/run.py, run-012) into
# the rebuilt module with three structural extensions:
#
#   1) **rho channel preserved** (A1).  The reviewer's A8 substrate uses
#      rho = 0 only (independent product Pi_i (1 - FAR_i)).  Here we
#      promote that product to the equicorrelated joint no-FA integral
#      from the rb-001 A1 channel — same one-factor Gauss-Hermite
#      reduction the homogeneous `p_no_fa_grid` uses — so any policy can
#      be scored at any rho in [0, 1).
#
#   2) **conservation order p preserved** (A3).  Per-location d'_i are
#      computed via `d_prime_hetero(alloc, r_vec, ..., p)` (rb-019), so
#      the conservation family threads cleanly through the heterogeneous
#      pipeline; p = 1 is the paper's additive form (back-compat).
#
#   3) **heterogeneous r_i ALSO supported** (A2).  Because the d'-map is
#      already RB-014's `d_prime_hetero`, the general optimiser accepts
#      an N-vector r_vec at no extra cost.  This means A2-only sweeps
#      (RB-018, fixed-shape alloc, heterogeneous r) and A8-only sweeps
#      (RB-021, heterogeneous alloc, scalar r) share one driver.
#
# MATHEMATICAL FORMULATION (general N).
#
# Locations i = 0..N-1, slot 0 cued (convention).  An allocation vector
# a in R_+^N with sum_i a_i = 1 (callers enforce the simplex); a
# validity vector w in R_+^N with sum_i w_i = 1 and w_i = P(change at i
# | change trial); a value vector u_i = v if i = 0 else 1; and a
# per-location ratio vector r_vec.  Per-location d' via
# `d_prime_hetero(a, r_vec, d_max, f0, h, N, p)` (rb-019, §2.4 of the
# rebuilt model with the global r promoted to a vector r_i and the
# global p the A3 conservation order).
#
# Expected reward (generalises paper Eq. 9):
#
#   E[R] = 0.5 sum_i w_i u_i HR(d'_i, c_i)
#        + 0.5 CR * INT prod_i Phi((c_i + d'_i/2 - sqrt(rho) z) / sqrt(1-rho))
#                       phi(z) dz                                       (*)
#
# with CR = sum_i w_i u_i (variant A) or 1 (variant B).  At rho = 0 the
# integrand factorises and (*) collapses to prod_i Phi(c_i + d'_i / 2).
#
# GROUPING.  When two locations share the same (d'_i, w_i u_i), they
# also share the same optimal c_i by symmetry of the reward.  Grouping
# turns the N-D inner criterion problem into a G-D one with G <= N.
# Homogeneous alloc + uniform validity + scalar r ==> G = 2 (cued vs
# uncued); equal-uncued-but-heterogeneous-r ==> G can grow up to N.
# We always represent the inner problem as a group tuple (d_vec,
# wu_vec, n_vec) with sum n_vec = N.
#
# CRITERION OPTIMISATION (`optimal_ER_general`).
#  - G = 1:  exact 1-D argmax over `C_GRID`.
#  - G = 2:  exact 2-D argmax over `C_GRID x C_GRID` (same machinery as
#            the homogeneous `optimal_R`, with the n_g exponents).
#  - G >= 3: multi-restart coordinate ascent.  Each restart is exact at
#            grid resolution (1-D argmax per group, holding others
#            fixed), seeded from the 2^G corner seeds (per-group HR-side
#            vs no-FA-side standalone argmax) plus the all-zero seed.
#            The objective is bimodal per-group (a "liberal/detect"
#            attractor maxing HR vs a "conservative/avoid-FA" attractor
#            maxing the no-FA product), so multi-restart is needed; the
#            joint 2-D grid validates restart sufficiency at G = 2.
#
# RECOVERY CONTRACT (tests/test_general_policy.py).  For homogeneous
# alloc canonical_alloc(alpha, N), uniform validity (V, (1-V)/(N-1),
# ...), scalar r broadcast, and conservation p = 1, the general optimiser
# returns the same R as the legacy `optimal_R(d_c, d_u, v, V, N,
# variant, rho)` to *floating-point identity* at rho = 0 (the inner
# c-grid and the product are bit-for-bit equivalent) and to GH-64
# quadrature identity at rho > 0 (the same Phi backend, the same
# quadrature nodes/weights, identical operand order in `p_no_fa_grid`).
#
# ATTRIBUTION.  Lifted from Critique/replications/A8--heterogeneous-
# uncued/run.py (CR-036, run-012, validated by reviewer's A8 verdict)
# with the rho extension and conservation-family threading added.
# ====================================================================
def _hr_omf_grids(d: float) -> tuple[np.ndarray, np.ndarray]:
    """Per-group HR and (1 - FAR) on `C_GRID` for sensitivity d.

    Shapes: each (n_c,).  HR(c) = Phi(d/2 - c); 1 - FAR(c) = Phi(d/2 + c).
    """
    return Phi(d / 2.0 - C_GRID), Phi(d / 2.0 + C_GRID)


def _omf_grid_correlated(d: float, rho: float) -> np.ndarray:
    """Per-group (1 - FAR(c, z)) on `C_GRID x z_nodes` for the one-factor
    Gauss-Hermite reduction.  Shape: (n_c, nq).  Reduces to a 1-D vector
    Phi(d/2 + c) at rho = 0 (handled outside this helper to avoid the
    spurious (n_c, nq) allocation).
    """
    s = math.sqrt(1.0 - rho)
    rs = math.sqrt(rho)
    # b = c + d/2; the (1 - FAR) integrand is Phi((b - rs z) / s).
    b = C_GRID + d / 2.0                              # (n_c,)
    z = _GH_Z[None, :]                                # (1, nq)
    return Phi((b[:, None] - rs * z) / s)             # (n_c, nq)


def optimal_ER_general(d_vec: Sequence[float],
                       wu_vec: Sequence[float],
                       n_vec: Sequence[int],
                       CR: float,
                       rho: float,
                       max_sweeps: int = 80) -> dict:
    """Maximise E[R] over per-group criteria c_g given group structure.

    Parameters
    ----------
    d_vec, wu_vec : length-G sequences
        Group sensitivity d'_g and weight wu_g = w_g u_g.
    n_vec : length-G sequence of ints
        Group multiplicities; sum(n_vec) = N total locations.
    CR : float
        Correct-rejection reward (variant A: sum_i w_i u_i; variant B: 1).
    rho : float
        Equicorrelated noise correlation in [0, 1).  At rho = 0 the no-FA
        product factorises into prod_g (1 - FAR_g)^{n_g}.

    Returns
    -------
    dict(R=optimum, c_vals=list[float] of optimal criteria, c_idx=list[int]
          of indices into C_GRID, method=str).

    Numerics
    --------
    For G <= 2 the optimum is the exact argmax over an explicit 1- or 2-D
    grid (same machinery as `optimal_R`).  For G >= 3 multi-restart
    coordinate ascent — exact 1-D argmax per group per sweep — runs from
    2**G + 1 seeds.  All paths use the rebuilt module's `Phi` backend
    (`scipy.special.ndtr` when available) and the rb-001 GH-64 nodes
    `_GH_Z, _GH_W`, so rho = 0 and rho > 0 results share quadrature
    state.
    """
    G = len(d_vec)
    if G != len(wu_vec) or G != len(n_vec):
        raise ValueError("d_vec, wu_vec, n_vec must share length")
    # Per-group HR vectors (always 1-D, shape (n_c,)).
    hr_grids = [_hr_omf_grids(d)[0] for d in d_vec]
    # Per-group (1 - FAR) — 1-D at rho=0, 2-D (c, z) at rho>0.
    if rho <= 0.0:
        omf_grids = [_hr_omf_grids(d)[1] for d in d_vec]  # each (n_c,)
    else:
        omf_grids = [_omf_grid_correlated(d, rho) for d in d_vec]  # each (n_c, nq)

    # ---- G == 1: exact 1-D maximisation ----------------------------
    if G == 1:
        hr0 = hr_grids[0]
        if rho <= 0.0:
            omf0 = omf_grids[0]                      # (n_c,)
            prod = omf0 ** n_vec[0]                  # (n_c,)
        else:
            omf0 = omf_grids[0]                      # (n_c, nq)
            # prod[i] = INT omf0[i, z]^{n_0} phi(z) dz = sum_k w_k omf0[i, k]^{n_0}
            prod = (omf0 ** n_vec[0]) @ _GH_W        # (n_c,)
        er = 0.5 * n_vec[0] * wu_vec[0] * hr0 + 0.5 * CR * prod
        bi = int(np.argmax(er))
        return dict(R=float(er[bi]), c_idx=[bi],
                    c_vals=[float(C_GRID[bi])], method="grid_1d")

    # ---- G == 2: exact 2-D maximisation ----------------------------
    if G == 2:
        hr0, hr1 = hr_grids[0], hr_grids[1]
        change = (0.5 * n_vec[0] * wu_vec[0] * hr0[:, None]
                  + 0.5 * n_vec[1] * wu_vec[1] * hr1[None, :])    # (n_c, n_c)
        if rho <= 0.0:
            omf0, omf1 = omf_grids[0], omf_grids[1]
            prod = (omf0[:, None] ** n_vec[0]) * (omf1[None, :] ** n_vec[1])
        else:
            # prod[i, j] = sum_k w_k omf0[i, k]^{n_0} omf1[j, k]^{n_1}
            G0 = (omf_grids[0] ** n_vec[0]) * _GH_W[None, :]      # (n_c, nq)
            G1 = (omf_grids[1] ** n_vec[1])                       # (n_c, nq)
            prod = G0 @ G1.T                                      # (n_c, n_c)
        er = change + 0.5 * CR * prod
        flat = int(np.argmax(er))
        i0, i1 = int(flat // er.shape[1]), int(flat % er.shape[1])
        return dict(R=float(er[i0, i1]), c_idx=[i0, i1],
                    c_vals=[float(C_GRID[i0]), float(C_GRID[i1])],
                    method="grid_2d")

    # ---- G >= 3: multi-restart coordinate ascent -------------------
    # Per-group standalone argmaxes for the two attractors.
    if rho <= 0.0:
        omf_pow_n_1d = [omf_grids[g] ** n_vec[g] for g in range(G)]  # (n_c,) each
        change_arg = [int(np.argmax(hr_grids[g])) for g in range(G)]
        cr_arg = [int(np.argmax(omf_pow_n_1d[g])) for g in range(G)]
    else:
        omf_pow_n_z = [omf_grids[g] ** n_vec[g] for g in range(G)]   # (n_c, nq) each
        # Standalone marginal (integrated over z) for the cr_arg seed.
        omf_pow_n_marg = [omf_pow_n_z[g] @ _GH_W for g in range(G)]   # (n_c,) each
        change_arg = [int(np.argmax(hr_grids[g])) for g in range(G)]
        cr_arg = [int(np.argmax(omf_pow_n_marg[g])) for g in range(G)]
    zero_idx = int(np.argmin(np.abs(C_GRID)))

    seeds: list[list[int]] = []
    for mask in range(1 << G):
        seeds.append([change_arg[g] if (mask >> g) & 1 else cr_arg[g]
                      for g in range(G)])
    seeds.append([zero_idx] * G)

    def _total_R(idx: list[int]) -> float:
        change = 0.0
        if rho <= 0.0:
            prod = 1.0
            for g in range(G):
                change += n_vec[g] * wu_vec[g] * hr_grids[g][idx[g]]
                prod *= omf_pow_n_1d[g][idx[g]]
            return 0.5 * change + 0.5 * CR * prod
        # rho > 0: joint no-FA integrates the product over z.
        joint_z = np.ones(GH_NQ)
        for g in range(G):
            change += n_vec[g] * wu_vec[g] * hr_grids[g][idx[g]]
            joint_z = joint_z * omf_pow_n_z[g][idx[g]]
        return 0.5 * change + 0.5 * CR * float(_GH_W @ joint_z)

    def _coord_ascent(seed: list[int]) -> list[int]:
        idx = list(seed)
        for _ in range(max_sweeps):
            changed = False
            for g in range(G):
                if rho <= 0.0:
                    # Multiply out the (1-FAR)^{n} product over all g' != g.
                    p_minus_g = 1.0
                    for g2 in range(G):
                        if g2 == g:
                            continue
                        p_minus_g *= omf_pow_n_1d[g2][idx[g2]]
                    obj = (0.5 * n_vec[g] * wu_vec[g] * hr_grids[g]
                           + 0.5 * CR * p_minus_g * omf_pow_n_1d[g])
                else:
                    # P_{-g}(z) = prod_{g' != g} omf_{g'}_z[idx[g'], :]^{n_{g'}}.
                    p_minus_g_z = np.ones(GH_NQ)
                    for g2 in range(G):
                        if g2 == g:
                            continue
                        p_minus_g_z = p_minus_g_z * omf_pow_n_z[g2][idx[g2]]
                    # int_z w(z) omf_g^{n_g}(c, z) P_{-g}(z) — vectorised over c.
                    integrand = omf_pow_n_z[g] * (p_minus_g_z * _GH_W)[None, :]
                    prod_c = integrand.sum(axis=1)                # (n_c,)
                    obj = (0.5 * n_vec[g] * wu_vec[g] * hr_grids[g]
                           + 0.5 * CR * prod_c)
                best = int(np.argmax(obj))
                if best != idx[g]:
                    idx[g] = best
                    changed = True
            if not changed:
                break
        return idx

    best_R = -float("inf")
    best_idx: list[int] | None = None
    for seed in seeds:
        idx = _coord_ascent(seed)
        R = _total_R(idx)
        if R > best_R:
            best_R = R
            best_idx = idx
    assert best_idx is not None
    return dict(R=float(best_R), c_idx=list(best_idx),
                c_vals=[float(C_GRID[i]) for i in best_idx],
                method="coord_ascent_multi_restart")


def er_full_policy(alloc: Sequence[float],
                   valid: Sequence[float],
                   v: float,
                   r_vec: Sequence[float] | float,
                   cell: HeadlineCell,
                   group_round_dp: int = 9) -> dict:
    """E[R] at a fully-specified (alloc, valid, r_vec) with criteria optimised.

    Convention: slot 0 = cued (value v); slots 1..N-1 uncued (value 1).

    Parameters
    ----------
    alloc, valid : length-N sequences of floats
        Per-location allocation a_i and validity w_i.  Callers enforce
        sum(alloc) ~= 1 and sum(valid) ~= 1.
    v : float
        Cued value (>= 1 in the inherited model).
    r_vec : length-N sequence OR scalar
        Per-location benefit/cost asymmetry ratio.  Forwarded to
        `d_prime_hetero` (rb-019); a scalar is broadcast.
    cell : HeadlineCell
        Carries N, d_max, f0, h_name, variant, rho, cons_p.

    Returns
    -------
    dict
        Keys: R (float, optimal reward), d_arr (length-N d'_i), wu_arr
        (length-N w_i u_i), CR (float), groups (list of (d, wu, n)
        tuples), c_vals (length-G optimal per-group criteria), c_idx
        (length-G indices), method (str), N (int).

    Numerics
    --------
    d'_i comes from `d_prime_hetero` (rb-019, byte-for-byte against
    `d_prime_asym` in the homogeneous case).  Group formation rounds
    (d, wu) to `group_round_dp` decimal places (default 9) to fold
    floating-point ties; this is the same tolerance the reviewer's A8
    substrate uses and is below any practical signal in the headline
    numbers.  Criterion optimisation routed through `optimal_ER_general`.
    """
    h = make_h(cell.h_name)
    N = cell.N
    p = cell.cons_p
    d_arr = d_prime_hetero(alloc, r_vec, cell.d_max, cell.f0, h, N, p)
    value = np.ones(N, dtype=float)
    value[0] = float(v)
    valid_arr = np.asarray(valid, dtype=float)
    if valid_arr.shape != (N,):
        raise ValueError(
            f"valid must have shape ({N},); got {valid_arr.shape}")
    wu_arr = valid_arr * value
    CR = float(np.sum(wu_arr)) if cell.variant == "A" else 1.0

    # Group locations by (d', wu).
    groups: dict[tuple, int] = {}
    for i in range(N):
        key = (round(float(d_arr[i]), group_round_dp),
               round(float(wu_arr[i]), group_round_dp + 3))
        groups[key] = groups.get(key, 0) + 1
    d_list = [k[0] for k in groups]
    wu_list = [k[1] for k in groups]
    n_list = [groups[k] for k in groups]

    opt = optimal_ER_general(d_list, wu_list, n_list, CR, cell.rho)
    return dict(R=opt["R"],
                d_arr=d_arr.tolist(),
                wu_arr=wu_arr.tolist(),
                CR=CR,
                groups=[(d_list[g], wu_list[g], n_list[g]) for g in range(len(d_list))],
                c_vals=opt["c_vals"],
                c_idx=opt["c_idx"],
                method=opt["method"],
                N=N)


def homogeneous_validity(V: float, N: int) -> np.ndarray:
    """Build the canonical homogeneous validity vector (V, (1-V)/(N-1), ...).

    Useful as a starting point for any A8 sim that wants to vary
    `alloc` against the inherited homogeneous validity.
    """
    w = np.empty(N, dtype=float)
    w[0] = float(V)
    w[1:] = (1.0 - float(V)) / (N - 1)
    return w
