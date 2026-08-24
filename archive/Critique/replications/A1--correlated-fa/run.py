"""
A1 SECOND VECTOR (re-derivation, numerical corroboration) — CR-052, run-017.

Does relaxing the per-location SDT *independence* assumption (A1) lower the
paper's reported VDA benefit, as §5.5 asserts ("our results therefore
represent an upper bound on VDA benefit")?

====================================================================
MATHEMATICAL FORMULATION
====================================================================
The paper's expected reward (mission §2.5, paper Eq. 9) is

    E[R] = 0.5 [ V·HR_c·v + (1−V)·HR_u ]            (change trial)
         + 0.5 · P_no-fa · CR                       (no-change trial)

with, per location, the equal-variance Gaussian SDT decision variable
X_i on a NO-CHANGE trial distributed N(−d'_i/2, 1), and a false alarm
at location i being the event {X_i > c_i}.  Hence

    HR(d',c)  = Φ(d'/2 − c),   FAR(d',c) = Φ(−d'/2 − c),
    1 − FAR_i = Φ(c_i + d'_i/2) =: Φ(b_i),   b_i := c_i + d'_i/2.

INDEPENDENCE (A1) enters the reward in EXACTLY ONE place: the joint
no-false-alarm probability on a no-change trial,

    P_no-fa^indep = (1 − FAR_c)(1 − FAR_u)^{N−1} = Φ(b_c) Φ(b_u)^{N−1}.   (Eq. 9)

The change-trial term is LINEAR in the marginal hit rates HR_c, HR_u — on a
change trial the change is at exactly one location, so the detection reward
never forms a cross-location product.  Therefore replacing the Eq. 9 product
with the correlated joint orthant probability is the FAITHFUL, COMPLETE
relaxation of A1 within this reward structure (Booking 1).  (Booking 2 —
correlation also changing a *pooled* d' — requires a global detection rule,
which is assumption A6, NOT A1; see the derivation file.)

CORRELATED MODEL (equicorrelated Gaussian, correlation ρ ∈ [0,1)).
One-factor representation of the no-change decision variables:

    X_i = −d'_i/2 + √ρ · Z + √(1−ρ) · ε_i,   Z, ε_i ~ N(0,1) iid.

Then Var(X_i)=1, Corr(X_i,X_j)=ρ.  Conditioning on the shared factor Z=z, the
locations are independent, so

    P_no-fa(ρ) = ∫ Φ((b_c − √ρ z)/√(1−ρ)) · Φ((b_u − √ρ z)/√(1−ρ))^{N−1} φ(z) dz.

This is a 1-D quadrature — NO multivariate-normal CDF needed; the
equicorrelation reduction is EXACT (not an approximation).  At ρ=0 it
collapses to Φ(b_c)Φ(b_u)^{N−1}, recovering Eq. 9 bit-for-bit (validated).

SLEPIAN MONOTONICITY.  For a Gaussian orthant probability P(∀i: X_i ≤ c_i),
raising any off-diagonal correlation raises the probability (Slepian 1962).
For equicorrelation, P_no-fa(ρ) is non-decreasing in ρ and
P_no-fa(ρ) ≥ P_no-fa(0) for ρ ≥ 0 — the INDEPENDENT corner is the
no-FA-MINIMISING (equivalently FA-penalty-MAXIMISING) corner.  Positive ρ
RELAXES the aggregate false-alarm penalty.

THE TEST.  VDA benefit = R(P1) − R(P2):  P1 jointly optimises (α, c_c, c_u) at
value v; P2 freezes α at α*(v=1) (value-blind attention) and re-optimises
criteria at v.  We recompute the VDA(r) curve and the criterion fraction
CF = [R(P3)−R(P4)] / [R(P1)−R(P4)] under P_no-fa(ρ), at the C2/Figure-4
headline cell (V=0.5, v=5, N=4, d'_max=2.0, f_0=0.5, h=√), for
ρ ∈ {0, 0.1, 0.2, 0.3, 0.4} bracketing the Cohen & Maunsell (2009) r_SC≈0.2.

DECISION RULE (mission CR-052):
    peak VDA RISES materially with ρ  → "upper bound on VDA" FAILS → A1 CONTESTED
    peak VDA FALLS or is flat in ρ     → claim holds in scope     → A1 CONFIRMED-CONDITIONAL

Two competing channels make the sign a genuine empirical question:
  (a) ρ↑ relaxes the FA penalty → the criterion lever is cheaper/more
      effective → criterion absorbs more value-reward → LESS residual for
      value-directed attention → VDA falls.
  (b) ρ↑ relaxes the cost of the uncued locations' degraded FAR when attention
      concentrates on the cued location → concentrating attention is cheaper
      → value-directed attention more attractive → VDA rises.
The computation adjudicates; the derivation file explains the winner.

Model primitives (Φ, h, f, β/γ, d'_asym, the criterion grid) are reused with
attribution from Critique/replications/C5--symmetric-recovery/run.py and
C1--criterion-fraction-floor/run.py so the ρ=0 path is identical to the
independent-model code the prior runs validated.

CR-052, prompt v0.2, run-017, 2026-05-25.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
from typing import Callable

import numpy as np

# --------------------------------------------------------------------
# Φ (standard normal CDF). scipy.special.ndtr if present (full double
# precision); A&S 7.1.26 numpy fallback otherwise.  Both ρ=0 and ρ>0
# call the SAME Φ, so any Φ approximation error is common-mode and
# cancels in the ρ-trend that the verdict turns on.
# --------------------------------------------------------------------
_SQRT2 = math.sqrt(2.0)
try:
    from scipy.special import ndtr as _ndtr

    def Phi(x):
        return _ndtr(np.asarray(x, dtype=float))

    _PHI_BACKEND = "scipy.special.ndtr"
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

    def Phi(x):
        arr = np.asarray(x, dtype=float)
        return 0.5 * (1.0 + _erf_np(arr / _SQRT2))

    _PHI_BACKEND = "A&S 7.1.26 numpy-vectorised"


# --------------------------------------------------------------------
# Transfer function and asymmetry weights (mission §2.3, §2.4).
# Copied with attribution from C5/C1 run.py.
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
    """f(a) = f_0 + (1 − f_0) h(a) ∈ [f_0, 1]."""
    return f0 + (1.0 - f0) * h(a)


def beta_gamma(r: float) -> tuple[float, float]:
    """β(r)=2r/(r+1); γ(r)=2/(r+1).  β+γ=2, β/γ=r (additive conservation, A3)."""
    return 2.0 * r / (r + 1.0), 2.0 / (r + 1.0)


def d_prime_asym(alpha: float, r: float, d_max: float, f0: float,
                 h: Callable, N: int) -> tuple[float, float]:
    """ASYMMETRIC d'(α) map (mission §2.4), clamped ≥ 0.  α<1/N branch swap is
    a no-op at r=1 (β=γ) and irrelevant here since we grid α ≥ 1/N (C4)."""
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
# Criterion grid (mission §2.5; paper Δc = 0.05).
# --------------------------------------------------------------------
C_GRID = np.arange(-3.0, 3.0 + 1e-9, 0.05)            # 121 points
_NC = len(C_GRID)

# --------------------------------------------------------------------
# Gauss–Hermite quadrature for ∫ g(z) φ(z) dz.
#   ∫_{-∞}^{∞} g(z) φ(z) dz, φ(z)=e^{−z²/2}/√(2π).
# Substituting z = √2 t maps the standard physicists' Hermite rule
#   ∫ e^{−t²} f(t) dt ≈ Σ_k w_k f(t_k)   (np.polynomial.hermite.hermgauss)
# to   ∫ g(z) φ(z) dz ≈ (1/√π) Σ_k w_k g(√2 t_k).
# Products of Φ are smooth ⇒ nq=64 is far past convergence (checked vs 128).
# --------------------------------------------------------------------
def gauss_hermite(nq: int = 64):
    t, w = np.polynomial.hermite.hermgauss(nq)        # weight e^{−t²}
    z = _SQRT2 * t                                    # nodes for φ(z)
    wn = w / math.sqrt(math.pi)                       # Σ wn = 1 exactly
    return z, wn


_GH_Z, _GH_W = gauss_hermite(64)


# --------------------------------------------------------------------
# Correlated no-false-alarm probability on the FULL (c_c, c_u) grid.
#   P_no-fa(ρ)[i,j] for c_c=C_GRID[i], c_u=C_GRID[j].
# b_c[i] = c_c[i] + d_c/2,  b_u[j] = c_u[j] + d_u/2  (z-score thresholds).
#   P[i,j] = ∫ Φ((b_c[i]−√ρ z)/√(1−ρ)) Φ((b_u[j]−√ρ z)/√(1−ρ))^{N−1} φ(z) dz
# Vectorised: Gc (n_c × nq), Gu (n_c × nq), then P = (Gc·w) @ Gu^T.
# --------------------------------------------------------------------
def p_no_fa_grid(d_c: float, d_u: float, N: int, rho: float) -> np.ndarray:
    b_c = C_GRID + d_c / 2.0                            # (n_c,)
    b_u = C_GRID + d_u / 2.0                            # (n_c,)
    if rho <= 0.0:
        # Exact independent product (Eq. 9). Outer product over the grid.
        return Phi(b_c)[:, None] * (Phi(b_u)[None, :] ** (N - 1))
    s = math.sqrt(1.0 - rho)
    rs = math.sqrt(rho)
    z = _GH_Z[None, :]                                  # (1, nq)
    Gc = Phi((b_c[:, None] - rs * z) / s)               # (n_c, nq)
    Gu = Phi((b_u[:, None] - rs * z) / s) ** (N - 1)     # (n_c, nq)
    # Σ_k w_k Gc[i,k] Gu[j,k] :
    return (Gc * _GH_W[None, :]) @ Gu.T                 # (n_c, n_c)


# --------------------------------------------------------------------
# R*(d_c, d_u) = max over (c_c, c_u) of expected reward, under P_no-fa(ρ).
# Hit terms are ρ-independent (marginal). CR variant A: V·v+(1−V); B: 1.
# --------------------------------------------------------------------
def optimal_R(d_c: float, d_u: float, v: float, V: float, N: int,
              variant: str, rho: float) -> float:
    hr_c = Phi(d_c / 2.0 - C_GRID)                      # (n_c,)
    hr_u = Phi(d_u / 2.0 - C_GRID)                      # (n_c,)
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    p_nofa = p_no_fa_grid(d_c, d_u, N, rho)             # (n_c, n_c)
    er = (0.5 * (V * v * hr_c[:, None] + (1.0 - V) * hr_u[None, :])
          + 0.5 * cr * p_nofa)
    return float(er.max())


def floor_R(d_c: float, d_u: float, v: float, V: float, N: int,
            variant: str, rho: float) -> float:
    """P4 reward: α=1/N is set by the caller (via d_c,d_u), criteria FIXED at 0."""
    hr_c = float(Phi(d_c / 2.0 - 0.0))
    hr_u = float(Phi(d_u / 2.0 - 0.0))
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    # single (c_c=c_u=0) cell of the correlated grid:
    b_c = np.array([0.0 + d_c / 2.0])
    b_u = np.array([0.0 + d_u / 2.0])
    if rho <= 0.0:
        p_nofa = float(Phi(b_c[0]) * Phi(b_u[0]) ** (N - 1))
    else:
        s = math.sqrt(1.0 - rho); rs = math.sqrt(rho)
        gc = Phi((b_c[0] - rs * _GH_Z) / s)
        gu = Phi((b_u[0] - rs * _GH_Z) / s) ** (N - 1)
        p_nofa = float(np.sum(_GH_W * gc * gu))
    return 0.5 * (V * v * hr_c + (1.0 - V) * hr_u) + 0.5 * cr * p_nofa


# --------------------------------------------------------------------
# Policy helpers over an α grid (α ≥ 1/N per C4 no-inversion, V≥1/N here).
# --------------------------------------------------------------------
def alpha_opt(r: float, v: float, V: float, N: int, d_max: float, f0: float,
              h: Callable, variant: str, rho: float,
              alpha_grid: np.ndarray) -> tuple[float, float]:
    rs = np.empty(len(alpha_grid))
    for k, a in enumerate(alpha_grid):
        d_c, d_u = d_prime_asym(float(a), r, d_max, f0, h, N)
        rs[k] = optimal_R(d_c, d_u, v, V, N, variant, rho)
    idx = int(np.argmax(rs))
    return float(alpha_grid[idx]), float(rs[idx])


def policies(r: float, v: float, V: float, N: int, d_max: float, f0: float,
             h: Callable, variant: str, rho: float,
             alpha_grid: np.ndarray) -> dict:
    """Return R(P1),R(P2),R(P3),R(P4), VDA, CF at (r,ρ) for value v.
    P2 freezes α at α*(v=1) (value-blind attention)."""
    # P1: joint optimum at v
    a1, R_P1 = alpha_opt(r, v, V, N, d_max, f0, h, variant, rho, alpha_grid)
    # value-blind reference α*(v=1):
    a_vb, _ = alpha_opt(r, 1.0, V, N, d_max, f0, h, variant, rho, alpha_grid)
    # P2: criteria re-optimised at v, α frozen at a_vb
    d_c_vb, d_u_vb = d_prime_asym(a_vb, r, d_max, f0, h, N)
    R_P2 = optimal_R(d_c_vb, d_u_vb, v, V, N, variant, rho)
    # P3: α = 1/N, criteria optimised
    d_c_u, d_u_u = d_prime_asym(1.0 / N, r, d_max, f0, h, N)
    R_P3 = optimal_R(d_c_u, d_u_u, v, V, N, variant, rho)
    # P4: α = 1/N, c = 0
    R_P4 = floor_R(d_c_u, d_u_u, v, V, N, variant, rho)
    vda = R_P1 - R_P2
    denom = R_P1 - R_P4
    cf = (R_P3 - R_P4) / denom if abs(denom) > 1e-12 else float("nan")
    return dict(alpha_P1=a1, alpha_vb=a_vb, R_P1=R_P1, R_P2=R_P2,
                R_P3=R_P3, R_P4=R_P4, VDA=vda, CF=cf)


# ====================================================================
# BLOCKS
# ====================================================================
HEAD = dict(N=4, d_max=2.0, f0=0.5, h_name="sqrt", V=0.5, v_hi=5.0)
RHOS = [0.0, 0.1, 0.2, 0.3, 0.4]


def r_grid_log(lo=0.1, hi=10.0, n=25):
    g = np.geomspace(lo, hi, n)
    # ensure the C2 reference points are represented for cross-checks:
    for extra in (0.316, 0.398, 1.0, 3.162):
        if not np.any(np.isclose(g, extra, rtol=1e-3)):
            g = np.append(g, extra)
    return np.unique(np.round(g, 6))


def block_slepian() -> dict:
    """Sanity: P_no-fa(ρ) non-decreasing in ρ and ≥ product, at a fixed cell."""
    N = 4
    d_c, d_u = 1.8, 1.2
    i = int(np.argmin(np.abs(C_GRID - 0.5)))            # c_c = c_u = 0.5 cell
    vals = []
    for rho in [0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8]:
        P = p_no_fa_grid(d_c, d_u, N, rho)
        vals.append((rho, float(P[i, i])))
    monotone = all(vals[k + 1][1] >= vals[k][1] - 1e-12 for k in range(len(vals) - 1))
    ge_product = vals[0][1] <= min(v for _, v in vals[1:]) + 1e-12
    # quadrature normalisation check (Σ w = 1) and ρ=0 == product:
    prod_exact = float(Phi(C_GRID[i] + d_c / 2.0) * Phi(C_GRID[i] + d_u / 2.0) ** (N - 1))
    q0 = float(p_no_fa_grid(d_c, d_u, N, 1e-9)[i, i]) if False else vals[0][1]
    return dict(curve=vals, monotone_in_rho=monotone, indep_is_minimum=ge_product,
                rho0_equals_product=abs(vals[0][1] - prod_exact) < 1e-15,
                gh_weight_sum=float(np.sum(_GH_W)))


def block_vda_curve(variant: str, alpha_grid: np.ndarray) -> dict:
    h = make_h(HEAD["h_name"])
    rg = r_grid_log()
    out = {}
    for rho in RHOS:
        vdas = []
        for r in rg:
            p = policies(float(r), HEAD["v_hi"], HEAD["V"], HEAD["N"],
                         HEAD["d_max"], HEAD["f0"], h, variant, rho, alpha_grid)
            vdas.append(p["VDA"])
        vdas = np.array(vdas)
        pk = int(np.argmax(vdas))
        out[f"{rho:.2f}"] = dict(peak_VDA=float(vdas[pk]),
                                 peak_r=float(rg[pk]),
                                 vda=vdas.tolist())
    # Pointwise upper-bound test: is VDA(r;ρ) ≤ VDA(r;0) for all r, all ρ>0?
    base = np.array(out["0.00"]["vda"])
    ub_holds = {}
    max_excess = {}
    for rho in RHOS[1:]:
        cur = np.array(out[f"{rho:.2f}"]["vda"])
        excess = cur - base                       # >0 means VDA rose (claim fails)
        ub_holds[f"{rho:.2f}"] = bool(np.all(excess <= 1e-9))
        max_excess[f"{rho:.2f}"] = float(np.max(excess))
    return dict(variant=variant, r_grid=rg.tolist(), by_rho=out,
                upper_bound_holds_pointwise=ub_holds,
                max_excess_over_rho0=max_excess)


def block_cf(variant: str, alpha_grid: np.ndarray) -> dict:
    """Criterion fraction CF(ρ) at representative r (cost-dominant peak, symmetric,
    benefit-dominant) for the headline cell."""
    h = make_h(HEAD["h_name"])
    rows = {}
    for r in (0.398, 1.0, 3.162):
        rows[f"r={r}"] = {}
        for rho in RHOS:
            p = policies(r, HEAD["v_hi"], HEAD["V"], HEAD["N"],
                         HEAD["d_max"], HEAD["f0"], h, variant, rho, alpha_grid)
            rows[f"r={r}"][f"{rho:.2f}"] = dict(CF=p["CF"], R_P1=p["R_P1"],
                                                R_P3=p["R_P3"], R_P4=p["R_P4"],
                                                VDA=p["VDA"], alpha_P1=p["alpha_P1"])
    return dict(variant=variant, rows=rows)


def block_validation(alpha_grid: np.ndarray) -> dict:
    """ρ=0 must reproduce the independent model: peak VDA(r) ~0.077–0.080 @ r~0.3–0.4
    (C2 / CR-001 / CR-036), and quadrature-at-tiny-ρ → product."""
    h = make_h(HEAD["h_name"])
    rg = r_grid_log()
    vdas = []
    for r in rg:
        p = policies(float(r), HEAD["v_hi"], HEAD["V"], HEAD["N"], HEAD["d_max"],
                     HEAD["f0"], h, "A", 0.0, alpha_grid)
        vdas.append(p["VDA"])
    vdas = np.array(vdas); pk = int(np.argmax(vdas))
    # quadrature continuity: P_no-fa(ρ→0) → product
    d_c, d_u = 1.8, 1.2
    prod = float(Phi(C_GRID[60] + d_c / 2) * Phi(C_GRID[60] + d_u / 2) ** 3)
    q_small = float(p_no_fa_grid(d_c, d_u, 4, 1e-6)[60, 60])
    return dict(peak_VDA_rho0=float(vdas[pk]), peak_r_rho0=float(rg[pk]),
                quad_to_product_gap_at_1em6=abs(q_small - prod),
                gh64_vs_gh128_maxdiff=_gh_convergence(d_c, d_u))


def _gh_convergence(d_c, d_u) -> float:
    z64, w64 = gauss_hermite(64); z128, w128 = gauss_hermite(128)
    b = C_GRID + d_c / 2.0; bu = C_GRID + d_u / 2.0
    rho = 0.3; s = math.sqrt(1 - rho); rs = math.sqrt(rho)

    def quad(z, w):
        Gc = Phi((b[:, None] - rs * z[None, :]) / s)
        Gu = Phi((bu[:, None] - rs * z[None, :]) / s) ** 3
        return (Gc * w[None, :]) @ Gu.T

    return float(np.max(np.abs(quad(z64, w64) - quad(z128, w128))))


def main():
    t0 = time.time()
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(here, "output")
    os.makedirs(out_dir, exist_ok=True)

    alpha_grid = np.round(np.arange(1.0 / HEAD["N"], 1.0 + 1e-9, 0.005), 6)

    results = dict(
        meta=dict(phi_backend=_PHI_BACKEND, nq=len(_GH_Z),
                  alpha_step=0.005, c_step=0.05, head=HEAD, rhos=RHOS,
                  generated="run-017 / CR-052"),
        validation=block_validation(alpha_grid),
        slepian=block_slepian(),
        vda_curve_A=block_vda_curve("A", alpha_grid),
        vda_curve_B=block_vda_curve("B", alpha_grid),
        cf_A=block_cf("A", alpha_grid),
        cf_B=block_cf("B", alpha_grid),
    )
    # Determinism digest hashes the NUMERIC content only (exclude wall-clock
    # runtime, which is the sole source of run-to-run variation).
    digest = hashlib.sha256(
        json.dumps(results, indent=2, sort_keys=True).encode()).hexdigest()
    results["meta"]["runtime_s"] = round(time.time() - t0, 2)
    results["meta"]["sha256_numeric"] = digest
    with open(os.path.join(out_dir, "results.json"), "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    # ---- console summary ----
    val = results["validation"]
    sl = results["slepian"]
    print(f"[Φ backend] {_PHI_BACKEND}  | nq={len(_GH_Z)} | runtime={results['meta']['runtime_s']}s")
    print(f"[validation] ρ=0 peak VDA = {val['peak_VDA_rho0']:.5f} at r={val['peak_r_rho0']:.4f} "
          f"(C2 target ~0.077-0.080 @ r~0.3-0.4)")
    print(f"[validation] quad(ρ=1e-6) vs product gap = {val['quad_to_product_gap_at_1em6']:.2e}; "
          f"GH64 vs GH128 maxdiff = {val['gh64_vs_gh128_maxdiff']:.2e}")
    print(f"[Slepian] P_no-fa monotone↑ in ρ: {sl['monotone_in_rho']}; "
          f"indep is minimum: {sl['indep_is_minimum']}; ρ0==product: {sl['rho0_equals_product']}; "
          f"Σw={sl['gh_weight_sum']:.12f}")
    for var in ("A", "B"):
        vc = results[f"vda_curve_{var}"]
        print(f"\n[VDA(r) peak vs ρ — variant {var}]")
        for rho in RHOS:
            d = vc["by_rho"][f"{rho:.2f}"]
            print(f"   ρ={rho:.2f}:  peak VDA = {d['peak_VDA']:.5f} at r = {d['peak_r']:.4f}")
        print(f"   upper-bound holds pointwise (VDA(r;ρ) ≤ VDA(r;0) ∀r): {vc['upper_bound_holds_pointwise']}")
        print(f"   max excess over ρ=0 curve: {vc['max_excess_over_rho0']}")
    for var in ("A", "B"):
        print(f"\n[Criterion fraction CF vs ρ — variant {var}]")
        for rk, byrho in results[f"cf_{var}"]["rows"].items():
            line = "   " + rk + ":  " + "  ".join(
                f"ρ{rho:.1f}→CF={byrho[f'{rho:.2f}']['CF']:.4f}" for rho in RHOS)
            print(line)
    print(f"\n[sha256] {digest}")


if __name__ == "__main__":
    main()
