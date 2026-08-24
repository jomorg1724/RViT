"""
C5 replication attack — does the r = 1 model EXACTLY recover the
symmetric special case (β = γ = 1)? (CR-005)

Mission claim C5 (paper Appendix A "Validation: Symmetric Special
Case", p.8; mission §2.6):

    "At r = 1, the model's independent benefit and cost scaling
    reduces to a symmetric special case (β = γ = 1) where a single
    shared transfer function governs both benefit and cost. We
    validated this by comparing the r = 1 results against an
    independent implementation of the symmetric model across all
    210 matched parameter combinations (N = 4, d'_max = 2.0,
    f_0 = 0.5, √· form). Optimal α* and R* values are identical to
    machine precision (maximum difference: 0.0; Figure 7)."

--------------------------------------------------------------------
MATHEMATICAL FRAMING
--------------------------------------------------------------------
The asymmetric per-location sensitivities (mission §2.4) are

    d'_cued (α)   = d'_base + β(r) [ d'_max f(α)            − d'_base ]
    d'_uncued(α)  = d'_base + γ(r) [ d'_max f((1−α)/(N−1))  − d'_base ]

with d'_base = d'_max f(1/N), β(r) = 2r/(r+1), γ(r) = 2/(r+1).

At r = 1:  β(1) = 2·1/(1+1) = 1  and  γ(1) = 2/(1+1) = 1, and BOTH
are representable EXACTLY in IEEE-754 binary64 (2.0*1.0/2.0 = 1.0,
2.0/2.0 = 1.0; no rounding). Substituting β = γ = 1 collapses the
asymmetric map to

    d'_cued (α)   = d'_base + ( d'_max f(α)           − d'_base )   (★)
    d'_uncued(α)  = d'_base + ( d'_max f((1−α)/(N−1)) − d'_base )

whereas the SYMMETRIC special case the paper compares against is the
"single shared transfer function" form with NO reference-point
bookkeeping:

    d'_cued (α)   = d'_max f(α)                                     (☆)
    d'_uncued(α)  = d'_max f((1−α)/(N−1)).

(★) and (☆) are equal as REAL numbers. The question C5 actually
tests is whether they are equal as FLOATS — i.e. whether the round
trip  a + (x − a)  returns x bit-for-bit, where a = d'_base and
x = d'_max f(·).

Sterbenz's lemma. If a/2 ≤ x ≤ 2a then fl(x − a) = x − a EXACTLY
(no rounding). When the subtraction is exact, δ := x − a is an exact
float, and a + δ = x as reals; since x is itself a representable
float, fl(a + δ) = x. Hence (★) == (☆) bit-for-bit WHENEVER every
swept x = d'_max f(·) lies in the Sterbenz band [d'_base/2, 2 d'_base].

At the paper's validation config (N=4, d'_max=2.0, f_0=0.5, √):
    d'_base = 2.0·f(0.25) = 2.0·(0.5 + 0.5·√0.25) = 2.0·0.75 = 1.5,
    x = 2.0·f(·) ∈ [2.0·0.5, 2.0·1.0] = [1.0, 2.0],
    Sterbenz band = [0.75, 3.0]  ⊇  [1.0, 2.0].
So EVERY x is inside the band → (★)==(☆) bit-for-bit → d' arrays,
Φ tables, rewards, and grid argmaxima are all identical → max|Δα*| =
max|ΔR*| = 0.0 EXACTLY. This run verifies that prediction and then
asks how robust the "exactly 0.0" claim is: under model configs
whose d'_base/x ratio leaves the Sterbenz band, the recovery should
degrade from exact-0 to ~1 ulp (still "machine precision", but no
longer literally 0.0).

--------------------------------------------------------------------
ATTACK DESIGN (mission §3.2 — replication vector)
--------------------------------------------------------------------
Block 1 (primary replication, the paper's headline number):
    Sweep the 210 matched combinations
        V ∈ {21 pts in [1/N, 1]}, v ∈ {1..5}, variant ∈ {A,B}
    at r = 1, N = 4, d'_max = 2.0, f_0 = 0.5, h = √.  For each combo
    compute (α*_P1, R*_P1) under the asymmetric-at-r=1 map (★) and
    under the independent symmetric map (☆); report max|Δα*|,
    max|ΔR*|, and the BIT-identity of the d' arrays.

Block 2 (mechanism check): confirm the Sterbenz prediction by
    reporting, at the paper config, np.array_equal on the cued/uncued
    d' arrays and the worst-case ulp gap.

Block 3 (robustness probe — the replication's "assumption sweep"):
    vary (f_0, d'_max) off the validation config and report where the
    bit-exact recovery (max|Δd'| == 0) gives way to a ~1-ulp gap,
    i.e. where the swept x = d'_max f(·) leaves the Sterbenz band
    [d'_base/2, 2 d'_base]. This characterises C5's "max diff 0.0" as
    a property of the chosen validation config, not a universal
    guarantee. (One focused extension; not a multi-assumption sweep —
    mission §8.5.)

Block 4 (continuity probe): confirm r = 1 is the smooth limit, not a
    knife-edge — compute max|Δα*|, max|ΔR*| vs the symmetric model at
    r ∈ {1±1e-3, 1±1e-6, 1} on a handful of combos and show the gap
    shrinks continuously to 0 at r = 1.

Model primitives are copied (with attribution) from
Critique/replications/C1--criterion-fraction-floor/run.py so this
file is a standalone, INDEPENDENT implementation per the C5 spirit
(the symmetric map ☆ is written from scratch, not derived from the
asymmetric code path).

CR-005, prompt v0.2, run-008, 2026-05-20.
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
# Identical backend logic to C1's run.py so the comparison inherits the
# same Φ on both code paths.  (max abs error of the fallback ~1.5e-7,
# but that is IRRELEVANT to C5: both models call the SAME Φ, so any Φ
# error cancels in the asymmetric−symmetric difference.)
# --------------------------------------------------------------------
_SQRT2 = math.sqrt(2.0)

try:
    from scipy.special import ndtr as _ndtr

    def Phi(x):
        return _ndtr(np.asarray(x, dtype=float))

    _PHI_BACKEND = "scipy.special.ndtr"
except ImportError:
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
# --------------------------------------------------------------------
def make_h(name: str) -> Callable:
    """Transfer-function family h, with h(0)=0, h(1)=1, monotone."""
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
    """f(a) = f_0 + (1 − f_0) h(a).  Sensitivity multiplier ∈ [f_0, 1]."""
    return f0 + (1.0 - f0) * h(a)


def beta_gamma(r: float) -> tuple[float, float]:
    """β(r) = 2r/(r+1); γ(r) = 2/(r+1).  β + γ = 2, β/γ = r."""
    return 2.0 * r / (r + 1.0), 2.0 / (r + 1.0)


# --------------------------------------------------------------------
# The two d'(α) maps under comparison.
# --------------------------------------------------------------------
def d_prime_asym(alpha: float, r: float, d_max: float, f0: float,
                 h: Callable, N: int) -> tuple[float, float]:
    """
    ASYMMETRIC map (★) — the paper's general model (mission §2.4),
    copied from C1's d_prime_pair (incl. the α<1/N branch swap, which
    is a no-op at r=1 because β=γ).  Returns (d'_cued, d'_uncued),
    clamped ≥ 0.
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


def d_prime_sym(alpha: float, d_max: float, f0: float,
                h: Callable, N: int) -> tuple[float, float]:
    """
    SYMMETRIC special case (☆) — "a single shared transfer function
    governs both benefit and cost" (paper App. A).  Written
    INDEPENDENTLY of d_prime_asym: no β/γ, no d'_base reference point.
    This is what the paper's "independent implementation" means.
    """
    d_c = d_max * f_transfer(alpha, f0, h)
    d_u = d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h)
    return float(max(d_c, 0.0)), float(max(d_u, 0.0))


# --------------------------------------------------------------------
# Criterion grid + reward (mission §2.5 Eq. 9). Same machinery for
# both models — the model difference lives ONLY in the d'(α) map.
# --------------------------------------------------------------------
C_GRID = np.arange(-3.0, 3.0 + 1e-9, 0.05)          # Δc = 0.05 (paper)
_C_GRID_LEN = len(C_GRID)


def optimal_criteria_R(d_c: float, d_u: float, v: float, V: float, N: int,
                       variant: str = "A") -> float:
    """
    R*(d_c, d_u) = max over (c_c, c_u) ∈ C_GRID² of expected reward
        0.5 [ V·HR_c·v + (1−V)·HR_u ] + 0.5·P_no_fa·CR,
    HR(d',c)=Φ(d'/2−c), FAR(d',c)=Φ(−d'/2−c),
    P_no_fa = (1−FAR_c)(1−FAR_u)^{N−1},
    CR = V·v+(1−V) (variant A) or 1 (variant B).
    Complexity O(|C_GRID|²) space and time per call.
    """
    hr_c = Phi(d_c / 2.0 - C_GRID)
    hr_u = Phi(d_u / 2.0 - C_GRID)
    far_c = Phi(-d_c / 2.0 - C_GRID)
    far_u = Phi(-d_u / 2.0 - C_GRID)
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    p_no_fa = (1.0 - far_c)[:, None] * ((1.0 - far_u) ** (N - 1))[None, :]
    er = 0.5 * (V * hr_c[:, None] * v + (1.0 - V) * hr_u[None, :]) + 0.5 * p_no_fa * cr
    return float(er.max())


def p1_optimum(d_pairs: list[tuple[float, float]], alpha_grid: np.ndarray,
               v: float, V: float, N: int, variant: str) -> tuple[float, float]:
    """
    P1 joint optimum: α* = argmax_α R*(d'(α)), R* = max value.
    d_pairs[i] is the (d_c, d_u) at alpha_grid[i] for the relevant model.
    Returns (alpha_star, R_star).
    """
    rs = np.array([optimal_criteria_R(dc, du, v, V, N, variant)
                   for dc, du in d_pairs])
    idx = int(np.argmax(rs))
    return float(alpha_grid[idx]), float(rs[idx])


# --------------------------------------------------------------------
# Block 1 — primary 210-combination replication at r = 1.
# --------------------------------------------------------------------
def block1_primary(alpha_grid: np.ndarray) -> dict:
    N, d_max, f0, h = 4, 2.0, 0.5, make_h("sqrt")
    r = 1.0
    V_grid = np.linspace(1.0 / N, 1.0, 21)          # 21 validity points
    v_grid = [1, 2, 3, 4, 5]
    variants = ["A", "B"]

    # d'(α) depends only on α (r,N,d_max,f0,h fixed) → precompute ONCE,
    # shared across all 210 combos.  Two independent precomputations.
    d_pairs_asym = [d_prime_asym(float(a), r, d_max, f0, h, N) for a in alpha_grid]
    d_pairs_sym = [d_prime_sym(float(a), d_max, f0, h, N) for a in alpha_grid]

    # Bit-identity of the d' arrays (the crux — see module docstring).
    asym_c = np.array([p[0] for p in d_pairs_asym])
    asym_u = np.array([p[1] for p in d_pairs_asym])
    sym_c = np.array([p[0] for p in d_pairs_sym])
    sym_u = np.array([p[1] for p in d_pairs_sym])
    dprime_bit_identical = bool(np.array_equal(asym_c, sym_c) and
                                np.array_equal(asym_u, sym_u))
    max_abs_dc = float(np.max(np.abs(asym_c - sym_c)))
    max_abs_du = float(np.max(np.abs(asym_u - sym_u)))

    rows = []
    max_dalpha = 0.0
    max_dR = 0.0
    argmax_dalpha = None
    argmax_dR = None
    for V in V_grid:
        for v in v_grid:
            for variant in variants:
                a_as, R_as = p1_optimum(d_pairs_asym, alpha_grid, float(v),
                                        float(V), N, variant)
                a_sy, R_sy = p1_optimum(d_pairs_sym, alpha_grid, float(v),
                                        float(V), N, variant)
                da = abs(a_as - a_sy)
                dR = abs(R_as - R_sy)
                rows.append(dict(V=float(V), v=v, variant=variant,
                                 alpha_asym=a_as, alpha_sym=a_sy,
                                 R_asym=R_as, R_sym=R_sy,
                                 d_alpha=da, d_R=dR))
                if da > max_dalpha:
                    max_dalpha, argmax_dalpha = da, (float(V), v, variant)
                if dR > max_dR:
                    max_dR, argmax_dR = dR, (float(V), v, variant)

    return dict(
        n_combos=len(rows),
        dprime_bit_identical=dprime_bit_identical,
        max_abs_d_dc=max_abs_dc,
        max_abs_d_du=max_abs_du,
        max_d_alpha=max_dalpha,
        max_d_R=max_dR,
        argmax_d_alpha=argmax_dalpha,
        argmax_d_R=argmax_dR,
        rows=rows,
        config=dict(N=N, d_max=d_max, f0=f0, h="sqrt", r=r,
                    alpha_grid_step=float(alpha_grid[1] - alpha_grid[0]),
                    alpha_grid_len=int(len(alpha_grid))),
    )


# --------------------------------------------------------------------
# Block 2 — Sterbenz mechanism check at the paper config.
# --------------------------------------------------------------------
def block2_sterbenz() -> dict:
    N, d_max, f0, h = 4, 2.0, 0.5, make_h("sqrt")
    d_base = d_max * f_transfer(1.0 / N, f0, h)
    # x = d'_max f(·) ranges over α ∈ (0,1]; sample densely.
    a = np.linspace(1e-6, 1.0, 100001)
    x_cued = d_max * f_transfer(a, f0, h)
    x_unc = d_max * f_transfer((1.0 - a) / (N - 1), f0, h)
    x_all = np.concatenate([x_cued, x_unc])
    band_lo, band_hi = d_base / 2.0, 2.0 * d_base
    inside = bool(np.all((x_all >= band_lo) & (x_all <= band_hi)))
    return dict(
        d_base=float(d_base),
        x_min=float(x_all.min()), x_max=float(x_all.max()),
        sterbenz_band=[float(band_lo), float(band_hi)],
        all_x_inside_band=inside,
        note=("Sterbenz: a/2 ≤ x ≤ 2a ⟹ fl(x−a) exact ⟹ "
              "a+(x−a)==x bit-for-bit ⟹ asymmetric(r=1)==symmetric."),
    )


# --------------------------------------------------------------------
# Block 3 — robustness of "exactly 0.0" across (f_0, d'_max).
# Cheap: only the d'(α) arrays are needed to decide bit-identity.
# --------------------------------------------------------------------
def block3_robustness() -> dict:
    N, h = 4, make_h("sqrt")
    a = np.linspace(1e-6, 1.0, 20001)
    out = []
    for d_max in [1.0, 2.0, 3.0]:
        for f0 in [0.1, 0.3, 0.5, 0.7, 0.9]:
            d_base = d_max * f_transfer(1.0 / N, f0, h)
            # Asymmetric-at-r=1 d' (β=γ=1 substituted; same float ops as model).
            beta, gamma = beta_gamma(1.0)
            xc = d_max * f_transfer(a, f0, h)
            xu = d_max * f_transfer((1.0 - a) / (N - 1), f0, h)
            dc_as = d_base + beta * (xc - d_base)
            du_as = d_base + gamma * (xu - d_base)
            dc_sy = xc       # symmetric (☆)
            du_sy = xu
            max_dc = float(np.max(np.abs(dc_as - dc_sy)))
            max_du = float(np.max(np.abs(du_as - du_sy)))
            band_lo, band_hi = d_base / 2.0, 2.0 * d_base
            x_all = np.concatenate([xc, xu])
            inside = bool(np.all((x_all >= band_lo) & (x_all <= band_hi)))
            out.append(dict(
                d_max=d_max, f0=f0, d_base=float(d_base),
                x_min=float(x_all.min()), x_max=float(x_all.max()),
                sterbenz_band=[float(band_lo), float(band_hi)],
                all_x_inside_band=inside,
                max_abs_d_dc=max_dc, max_abs_d_du=max_du,
                bit_identical=bool(max_dc == 0.0 and max_du == 0.0),
            ))
    return dict(grid=out,
                paper_config="(d_max=2.0, f0=0.5) is the validation config")


# --------------------------------------------------------------------
# Block 4 — continuity of recovery as r → 1.
# --------------------------------------------------------------------
def block4_continuity(alpha_grid: np.ndarray) -> dict:
    N, d_max, f0, h = 4, 2.0, 0.5, make_h("sqrt")
    # A few representative combos spanning the value/validity space.
    combos = [(0.25, 5, "A"), (0.5, 5, "A"), (0.5, 1, "B"), (0.85, 3, "A")]
    d_pairs_sym = [d_prime_sym(float(a), d_max, f0, h, N) for a in alpha_grid]
    out = []
    for r in [1.0 - 1e-3, 1.0 - 1e-6, 1.0, 1.0 + 1e-6, 1.0 + 1e-3]:
        d_pairs_as = [d_prime_asym(float(a), r, d_max, f0, h, N) for a in alpha_grid]
        max_da = 0.0
        max_dR = 0.0
        for (V, v, variant) in combos:
            a_as, R_as = p1_optimum(d_pairs_as, alpha_grid, float(v), V, N, variant)
            a_sy, R_sy = p1_optimum(d_pairs_sym, alpha_grid, float(v), V, N, variant)
            max_da = max(max_da, abs(a_as - a_sy))
            max_dR = max(max_dR, abs(R_as - R_sy))
        out.append(dict(r=r, max_d_alpha=max_da, max_d_R=max_dR))
    return dict(combos=combos, sweep=out)


def main():
    t0 = time.time()
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(outdir, exist_ok=True)

    # α grid: Δα = 0.005 (paper's stated resolution) plus the 1/N point.
    alpha_grid = np.unique(np.concatenate(
        [np.arange(0.005, 1.0 + 1e-9, 0.005), np.array([1.0 / 4])]))

    print(f"C5 symmetric-recovery replication (CR-005)")
    print(f"  Φ backend: {_PHI_BACKEND}")
    print(f"  α-grid: {len(alpha_grid)} pts (Δα=0.005 + 1/N); c-grid: {_C_GRID_LEN} pts")

    print("\n[Block 1] primary 210-combination replication at r=1 ...")
    b1 = block1_primary(alpha_grid)
    print(f"  combos                : {b1['n_combos']}")
    print(f"  d' arrays bit-identical: {b1['dprime_bit_identical']}")
    print(f"  max|Δd'_cued|          : {b1['max_abs_d_dc']:.3e}")
    print(f"  max|Δd'_uncued|        : {b1['max_abs_d_du']:.3e}")
    print(f"  max|Δα*| (210 combos)  : {b1['max_d_alpha']:.3e}  at {b1['argmax_d_alpha']}")
    print(f"  max|ΔR*| (210 combos)  : {b1['max_d_R']:.3e}  at {b1['argmax_d_R']}")
    print(f"  paper claim            : max diff 0.0 on all 210")

    print("\n[Block 2] Sterbenz mechanism check (paper config) ...")
    b2 = block2_sterbenz()
    print(f"  d'_base                : {b2['d_base']}")
    print(f"  swept x ∈ [{b2['x_min']:.4f}, {b2['x_max']:.4f}]")
    print(f"  Sterbenz band          : {b2['sterbenz_band']}")
    print(f"  all x inside band      : {b2['all_x_inside_band']}")

    print("\n[Block 3] robustness of exact-0 across (f_0, d'_max) ...")
    b3 = block3_robustness()
    for g in b3["grid"]:
        print(f"  d_max={g['d_max']:.1f} f0={g['f0']:.1f}  "
              f"x∈[{g['x_min']:.3f},{g['x_max']:.3f}] band={[round(z,3) for z in g['sterbenz_band']]}  "
              f"inside={g['all_x_inside_band']!s:5}  "
              f"max|Δd'|=({g['max_abs_d_dc']:.1e},{g['max_abs_d_du']:.1e})  "
              f"bit_id={g['bit_identical']}")

    print("\n[Block 4] continuity as r → 1 ...")
    b4 = block4_continuity(alpha_grid)
    for s in b4["sweep"]:
        print(f"  r={s['r']:.6f}  max|Δα*|={s['max_d_alpha']:.3e}  max|ΔR*|={s['max_d_R']:.3e}")

    result = dict(block1_primary=b1, block2_sterbenz=b2,
                  block3_robustness=b3, block4_continuity=b4,
                  metadata=dict(phi_backend=_PHI_BACKEND,
                                c_grid_step=0.05, alpha_grid_step=0.005,
                                claim_id="C5", attack_vector="replication",
                                run_id="run-008", task_id="CR-005",
                                prompt_version="0.2", date="2026-05-20",
                                elapsed_s=round(time.time() - t0, 2)))
    out_path = os.path.join(outdir, "results.json")
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2, default=float)
    print(f"\nSaved {out_path}  (elapsed {result['metadata']['elapsed_s']}s)")


if __name__ == "__main__":
    main()
