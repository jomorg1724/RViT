"""
CR-008 — A3 second attack vector (replication).  Does CRITERION DOMINANCE
(criterion fraction CF > 0.5) survive the multiplicative conservation rule
beta*gamma = 1 in the cells where it is *already* most fragile under the
paper's additive rule beta + gamma = 2 ?

--------------------------------------------------------------------------
TARGET CLAIM  (paper Sec. 5.5, p.8, verbatim)
--------------------------------------------------------------------------
    "Third, the beta + gamma = 2 constraint conserves total attention
     magnitude; alternative constraints (e.g., multiplicative beta*gamma = 1)
     could yield quantitatively different results, though the qualitative
     findings -- non-monotonic VDA, no inversion, criterion dominance --
     should be robust."

A3 (mission Sec. 2.7) is the additive-conservation assumption.  Run-010
(CR-040, re-derivation) left A3 = WEAKLY-SUPPORTED: on the V=0.5, v=5,
variant-A *reference slice* the beta*gamma=1 swap preserved all three named
findings, but criterion dominance ERODED to a thin margin (CF floor
0.601 -> 0.507).  The decisive open question, and the reason A3 is not yet
CONFIRMED-CONDITIONAL, is whether that erosion pushes CF strictly below 0.5
in the low-V / high-v / variant-B corner where C1 is ALREADY contested
(run-003 found additive CF as low as 0.304 there).  This script settles it.

--------------------------------------------------------------------------
WHY THIS IS THE RIGHT SLICE  (mission Sec. 8.5 -- one focused replication)
--------------------------------------------------------------------------
CF = [R(P3) - R(P4)] / [R(P1) - R(P4)].  Mission Sec. 2.5:
  * R(P3), R(P4) are evaluated at uniform attention alpha = 1/N, where the
    asymmetric scaling multiplies a ZERO bracket (d'_max f(1/N) - d'_base = 0),
    so R(P3) and R(P4) are IDENTICAL across the two conservation families
    by construction.  Only the denominator R(P1) (the joint optimum, which
    reallocates alpha away from 1/N) depends on the family.
  * beta*gamma=1 is the additive pair rescaled by a common factor
    kappa(r) = (r+1)/(2 sqrt r) = cosh(0.5 ln r) >= 1 (proved in
    Critique/derivations/A3--multiplicative-conservation.md), so it amplifies
    BOTH the cued benefit (beta) and the uncued cost (gamma).  Wherever
    reallocation already helps (R(P1) > R(P3)), beta*gamma=1 makes it help
    MORE => R(P1)_mult >= R(P1)_add => CF_mult <= CF_add.
  Hence the cells most at risk of dropping below 0.5 under beta*gamma=1 are
  exactly the cells with the SMALLEST additive CF.  Restricting the
  multiplicative sweep to the run-003 cells with additive CF < 0.60 captures
  every cell that could plausibly newly fall below 0.5 (a cell with additive
  CF >> 0.60 has too large a margin for the bounded erosion to cross 0.5;
  Block C below verifies this bound empirically on the full grid).

--------------------------------------------------------------------------
HONEST DECOMPOSITION  (mission Sec. 3, Sec. 6 -- do not overclaim)
--------------------------------------------------------------------------
The literal CR-008 rule ("any CF_mult < 0.5 => A3 -> CONTESTED") is too blunt,
because some additive-CF<0.60 cells ALREADY have additive CF < 0.5 (C1's
contested corner).  CF_mult < 0.5 in *those* cells is not attributable to the
constraint swap -- criterion dominance already failed there under the rule the
paper uses.  The constraint-ATTRIBUTABLE signal for A3 is:
  (i) NEW FLIPS  -- cells with CF_add >= 0.5 but CF_mult < 0.5.  These are
      cells the paper would call criterion-dominant under its own rule that
      become criterion-SUBORDINATE only because of the beta*gamma=1 swap.
      A non-trivial population of new flips => the constraint choice changes
      the qualitative conclusion => A3 -> CONTESTED.
  (ii) GLOBAL FRACTION -- the share of the full 4,410-cell grid with CF < 0.5
      under each rule, and the median CF under each rule.  If the median stays
      well above 0.5 and the failure region merely deepens/enlarges within the
      SAME low-V/high-v/variant-B corner C1 already flagged, the qualitative
      "criterion dominates in the bulk, fails in a corner" picture is preserved
      => A3 -> CONFIRMED-CONDITIONAL (robust within the grid, two vectors),
      with a sharpened conditional.

--------------------------------------------------------------------------
MODEL PROVENANCE
--------------------------------------------------------------------------
The model primitives below are an independent re-implementation that MATCHES
run-003's C1 code (Critique/replications/C1--criterion-fraction-floor/run.py)
exactly: same A&S 7.1.26 Phi (scipy is unavailable in this sandbox), same
c-grid (Delta c = 0.05 on [-3,3]), same alpha-grid (Delta alpha = 0.02 plus
the 1/N point), same R(P1..P4) and CF definitions.  Matching the config makes
the recomputed ADDITIVE CF reproduce run-003's stored CF (cross-check in
Block A), which validates that the multiplicative CF is computed on the same
footing.  The only moving part is the beta/gamma map.  The
beta_gamma_multiplicative used here is asserted bit-identical to the one in
the parent run-010 script (../run.py) on the r-grid (Block 0).

CR-008, prompt v0.2, run-011, 2026-05-24.
"""

from __future__ import annotations

import importlib.util
import json
import math
import os
import sys
import time
from typing import Callable

import numpy as np

# --------------------------------------------------------------------------
# Phi (standard normal CDF).  A&S 7.1.26 numpy-vectorised -- IDENTICAL to the
# run-003 C1 fallback path (scipy.special.ndtr is unavailable in this sandbox).
# Both conservation families call the SAME Phi, so any approximation error
# (max abs ~1.5e-7) cancels in the cross-family CF comparison.
# --------------------------------------------------------------------------
_SQRT2 = math.sqrt(2.0)
_A1, _A2, _A3c, _A4, _A5 = (0.254829592, -0.284496736, 1.421413741,
                            -1.453152027, 1.061405429)
_P = 0.3275911


def _erf_np(x_arr: np.ndarray) -> np.ndarray:
    """Vectorised A&S 7.1.26 erf approximation on |x| with sign fold."""
    x_abs = np.abs(x_arr)
    t = 1.0 / (1.0 + _P * x_abs)
    poly = ((((_A5 * t + _A4) * t + _A3c) * t + _A2) * t + _A1) * t
    y = 1.0 - poly * np.exp(-x_abs * x_abs)
    return np.where(x_arr >= 0.0, y, -y)


def Phi(x):
    """Phi(x) = 0.5 (1 + erf(x/sqrt2)).  Shape-preserving over numpy arrays."""
    arr = np.asarray(x, dtype=float)
    return 0.5 * (1.0 + _erf_np(arr / _SQRT2))


_PHI_BACKEND = "A&S 7.1.26 numpy-vectorised"


# --------------------------------------------------------------------------
# Transfer function f(a) = f_0 + (1 - f_0) h(a)  (mission Sec. 2.3).
# --------------------------------------------------------------------------
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
    return f0 + (1.0 - f0) * h(a)


# --------------------------------------------------------------------------
# The TWO conservation families, both pinned by the shared ratio beta/gamma=r.
#   additive   (beta+gamma=2):  beta=2r/(r+1),  gamma=2/(r+1)
#   multiplic. (beta*gamma=1):  beta=sqrt(r),   gamma=1/sqrt(r)
# Both give beta=gamma=1 at r=1 (C5 constraint-agnosticism).
# --------------------------------------------------------------------------
def beta_gamma_additive(r: float) -> tuple[float, float]:
    return 2.0 * r / (r + 1.0), 2.0 / (r + 1.0)


def beta_gamma_multiplicative(r: float) -> tuple[float, float]:
    s = math.sqrt(r)
    return s, 1.0 / s


WEIGHT_MAPS = {"additive": beta_gamma_additive,
               "multiplicative": beta_gamma_multiplicative}


def d_prime_pair(alpha: float, r: float, d_max: float, f0: float,
                 h: Callable, N: int, weight_map: Callable) -> tuple[float, float]:
    """
    (d'_cued, d'_uncued) at allocation alpha under the chosen family
    (mission Sec. 2.4).  beta scales the OVER-allocated location's departure
    from d'_base, gamma the UNDER-allocated; roles swap across the alpha=1/N
    kink so inversion alpha<1/N is representable.  Clamped at >= 0.
    """
    beta, gamma = weight_map(r)
    d_base = d_max * f_transfer(1.0 / N, f0, h)        # d'_base = d'_max f(1/N)
    if alpha >= 1.0 / N:
        d_c = d_base + beta * (d_max * f_transfer(alpha, f0, h) - d_base)
        d_u = d_base + gamma * (d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h) - d_base)
    else:
        d_c = d_base + gamma * (d_max * f_transfer(alpha, f0, h) - d_base)
        d_u = d_base + beta * (d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h) - d_base)
    return float(max(d_c, 0.0)), float(max(d_u, 0.0))


# --------------------------------------------------------------------------
# Criterion grid -- IDENTICAL to run-003 (Delta c = 0.05 on [-3, 3], 121 pts).
# --------------------------------------------------------------------------
C_GRID = np.arange(-3.0, 3.0 + 1e-9, 0.05)


def optimal_criteria_R(d_c: float, d_u: float, v: float, V: float, N: int,
                       variant: str) -> float:
    """
    R*(d_c, d_u) = max over (c_cued, c_uncued) in C_GRID x C_GRID of the
    expected reward, mission Sec. 2.5 Eq. (9):
        E[R] = 0.5 [ V HR_c v + (1-V) HR_u ] + 0.5 P_nofa CR
    HR(d',c)=Phi(d'/2 - c), FAR(d',c)=Phi(-d'/2 - c),
    P_nofa=(1-FAR_c)(1-FAR_u)^{N-1}, CR = V v + (1-V) [variant A] or 1 [B].
    Shapes: hr_c,far_c indexed by c_cued (axis 0); hr_u,far_u by c_uncued (1).
    """
    hr_c = Phi(d_c / 2.0 - C_GRID)                      # (121,)
    hr_u = Phi(d_u / 2.0 - C_GRID)                      # (121,)
    far_c = Phi(-d_c / 2.0 - C_GRID)                    # (121,)
    far_u = Phi(-d_u / 2.0 - C_GRID)                    # (121,)
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    p_no_fa = (1.0 - far_c)[:, None] * ((1.0 - far_u) ** (N - 1))[None, :]   # (121,121)
    er = 0.5 * (V * hr_c[:, None] * v + (1.0 - V) * hr_u[None, :]) + 0.5 * p_no_fa * cr
    return float(er.max())


def reward_at_c_zero(d_c: float, d_u: float, v: float, V: float, N: int,
                     variant: str) -> float:
    """R(P4): alpha=1/N AND c_cued=c_uncued=0 (the unbiased floor)."""
    hr_c = float(Phi(d_c / 2.0))
    hr_u = float(Phi(d_u / 2.0))
    far_c = float(Phi(-d_c / 2.0))
    far_u = float(Phi(-d_u / 2.0))
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    p_no_fa = (1.0 - far_c) * (1.0 - far_u) ** (N - 1)
    return 0.5 * (V * hr_c * v + (1.0 - V) * hr_u) + 0.5 * p_no_fa * cr


def compute_CF(r: float, V: float, v: float, N: int, d_max: float, f0: float,
               h: Callable, variant: str, alpha_grid: np.ndarray,
               weight_map: Callable, need_p2: bool = False) -> dict:
    """
    R(P1,P3,P4) and criterion fraction CF = (R(P3)-R(P4))/(R(P1)-R(P4)) at one
    cell under `weight_map`.  P1 = max_alpha R(alpha, c*); P3 = uniform
    alpha=1/N with optimal criteria; P4 = uniform alpha=1/N with c=0.

    CR-008 only needs CF, which does NOT involve P2 -- so P2/VDA are computed
    only when need_p2=True (~halves the per-cell cost).  P2 = value-blind
    (alpha fixed at alpha*(v=1), criteria re-optimised at v).
    """
    d_pairs = [d_prime_pair(float(a), r, d_max, f0, h, N, weight_map)
               for a in alpha_grid]

    # P3, P4 at uniform attention (family-INDEPENDENT: zero bracket at 1/N).
    d_b = d_max * f_transfer(1.0 / N, f0, h)
    R_p3 = optimal_criteria_R(d_b, d_b, v, V, N, variant)
    R_p4 = reward_at_c_zero(d_b, d_b, v, V, N, variant)

    # P1 = joint optimum over alpha.
    rs_p1 = np.array([optimal_criteria_R(dc, du, v, V, N, variant)
                      for dc, du in d_pairs])
    idx_p1 = int(np.argmax(rs_p1))
    R_p1 = float(rs_p1[idx_p1])
    alpha_p1 = float(alpha_grid[idx_p1])

    R_p2 = None
    alpha_p2 = None
    if need_p2:
        # P2 value-blind: alpha fixed at alpha*(v=1) under THIS family.
        rs_p2_v1 = np.array([optimal_criteria_R(dc, du, 1.0, V, N, variant)
                             for dc, du in d_pairs])
        alpha_p2 = float(alpha_grid[int(np.argmax(rs_p2_v1))])
        dc_p2, du_p2 = d_prime_pair(alpha_p2, r, d_max, f0, h, N, weight_map)
        R_p2 = optimal_criteria_R(dc_p2, du_p2, v, V, N, variant)

    total = R_p1 - R_p4
    crit = R_p3 - R_p4
    cf = crit / max(total, 1e-12)
    return dict(r=r, V=V, v=v, N=N, d_max=d_max, f0=f0, variant=variant,
                alpha_p1=alpha_p1, alpha_p2=alpha_p2,
                R_p1=R_p1, R_p2=R_p2, R_p3=R_p3, R_p4=R_p4,
                VDA=(R_p1 - R_p2) if R_p2 is not None else None,
                criterion_gain=crit, total_gain=total,
                criterion_fraction=cf)


# --------------------------------------------------------------------------
# Paths.  This script lives at
#   Critique/replications/A3--multiplicative-conservation/cr008_cf_floor/
# Parent run-010 script:  ../run.py    C1 results:  ../../C1--.../output/...
# --------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
A3_DIR = os.path.dirname(HERE)
REPL_DIR = os.path.dirname(A3_DIR)
C1_RESULTS = os.path.join(REPL_DIR, "C1--criterion-fraction-floor", "output", "results.json")
PARENT_RUN = os.path.join(A3_DIR, "run.py")


def assert_parent_map_identical(r_grid: np.ndarray) -> float:
    """
    Provenance check: import the parent (run-010) beta_gamma_multiplicative
    and assert it returns bit-identical (beta,gamma) to our local copy across
    the r-grid.  Returns the max abs deviation (should be exactly 0.0).
    """
    spec = importlib.util.spec_from_file_location("parent_a3_run", PARENT_RUN)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["parent_a3_run"] = mod
    spec.loader.exec_module(mod)
    max_dev = 0.0
    for r in r_grid:
        b_loc, g_loc = beta_gamma_multiplicative(float(r))
        b_par, g_par = mod.beta_gamma_multiplicative(float(r))
        max_dev = max(max_dev, abs(b_loc - b_par), abs(g_loc - g_par))
    return float(max_dev)


def main():
    t0 = time.time()
    outdir = os.path.join(HERE, "output")
    os.makedirs(outdir, exist_ok=True)

    N, d_max, f0 = 4, 2.0, 0.5
    h = make_h("sqrt")
    variant_map = {"A": "A", "B": "B"}
    VALID_THRESH = 1e-4         # run-003's mask for the fragile V->1/N ratio.

    # Grids -- IDENTICAL to run-003 phase_A.
    alpha_grid = np.unique(np.concatenate(
        [np.arange(0.02, 1.0 + 1e-9, 0.02), np.array([1.0 / N])]))
    r_grid_for_map_check = np.unique(np.concatenate(
        [np.logspace(np.log10(0.1), np.log10(10.0), 21), np.array([1.0])]))

    print("CR-008  A3 second vector -- multiplicative CF on additive-CF<0.60 cells")
    print(f"  Phi backend: {_PHI_BACKEND}")
    print(f"  config: N={N}, d'_max={d_max}, f0={f0}, h=sqrt;  Delta_c=0.05, "
          f"alpha-grid={len(alpha_grid)} pts (Delta_alpha=0.02 + 1/N)")

    # --- Block 0: provenance -- our beta*gamma map == parent run-010's. ----
    map_dev = assert_parent_map_identical(r_grid_for_map_check)
    print(f"\n[Block 0] beta_gamma_multiplicative vs parent ../run.py: "
          f"max|dev| = {map_dev:.3e}  ({'IDENTICAL' if map_dev == 0.0 else 'DIFFERS'})")

    # --- Load run-003 phase_A rows and select the at-risk cells. -----------
    with open(C1_RESULTS) as fh:
        c1 = json.load(fh)
    rows003 = c1["phase_A"]["rows"]
    print(f"\n[Load] run-003 phase_A rows: {len(rows003)}  "
          f"(backend={c1['metadata']['phi_backend']}, "
          f"Delta_alpha={c1['metadata']['alpha_grid_step']}, "
          f"Delta_c={c1['metadata']['c_grid_step']})")

    # At-risk set S: valid (total_gain>1e-4) AND additive CF < 0.60.
    S = [row for row in rows003
         if row["total_gain"] > VALID_THRESH and row["criterion_fraction"] < 0.60]
    print(f"[Select] valid cells with additive CF < 0.60: |S| = {len(S)} "
          f"of {len(rows003)} ({100.0*len(S)/len(rows003):.1f}%)")

    # --- Block A: recompute additive CF on S; cross-check vs stored. -------
    #     Then compute multiplicative CF on the same cells.
    print(f"\n[Block A] recomputing additive (cross-check) + multiplicative CF "
          f"on {len(S)} cells ...")
    cells = []
    max_add_xcheck = 0.0
    for row in S:
        r, V, v, variant = row["r"], row["V"], row["v"], variant_map[row["variant"]]
        add = compute_CF(r, V, v, N, d_max, f0, h, variant, alpha_grid,
                         beta_gamma_additive)
        mul = compute_CF(r, V, v, N, d_max, f0, h, variant, alpha_grid,
                         beta_gamma_multiplicative)
        xchk = abs(add["criterion_fraction"] - row["criterion_fraction"])
        max_add_xcheck = max(max_add_xcheck, xchk)
        # family-independence of R(P3),R(P4): must be bit-equal across families.
        p3p4_dev = max(abs(add["R_p3"] - mul["R_p3"]), abs(add["R_p4"] - mul["R_p4"]))
        cells.append(dict(
            r=r, V=V, v=v, variant=row["variant"],
            cf_add_stored=row["criterion_fraction"],
            cf_add_recomputed=add["criterion_fraction"],
            cf_mult=mul["criterion_fraction"],
            delta_cf=mul["criterion_fraction"] - add["criterion_fraction"],
            R_p1_add=add["R_p1"], R_p1_mult=mul["R_p1"],
            R_p3=add["R_p3"], R_p4=add["R_p4"],
            alpha_p1_add=add["alpha_p1"], alpha_p1_mult=mul["alpha_p1"],
            p3p4_family_dev=p3p4_dev))
    print(f"  max|CF_add_recomputed - CF_add_stored| over S = {max_add_xcheck:.3e}")
    print(f"  max|R(P3),R(P4) additive-vs-multiplicative| over S = "
          f"{max(c['p3p4_family_dev'] for c in cells):.3e}  (expect 0.0: family-indep)")

    # --- Honest decomposition. ---------------------------------------------
    cf_add = np.array([c["cf_add_recomputed"] for c in cells])
    cf_mul = np.array([c["cf_mult"] for c in cells])
    n_add_below = int((cf_add < 0.50).sum())          # already-failed under additive
    n_mul_below = int((cf_mul < 0.50).sum())          # failed under multiplicative
    new_flip_mask = (cf_add >= 0.50) & (cf_mul < 0.50)
    recovered_mask = (cf_add < 0.50) & (cf_mul >= 0.50)
    n_new_flips = int(new_flip_mask.sum())
    n_recovered = int(recovered_mask.sum())
    i_min_mul = int(np.argmin(cf_mul))
    i_min_add = int(np.argmin(cf_add))

    print(f"\n[Decompose] over S (additive-CF<0.60 cells):")
    print(f"  additive  CF<0.5 (C1's pre-existing failures): {n_add_below}")
    print(f"  mult.     CF<0.5                              : {n_mul_below}")
    print(f"  NEW FLIPS (CF_add>=0.5 -> CF_mult<0.5)        : {n_new_flips}  "
          f"<-- constraint-attributable A3 signal")
    print(f"  recovered (CF_add<0.5 -> CF_mult>=0.5)        : {n_recovered}")
    print(f"  min CF_add = {cf_add[i_min_add]:.4f} @ "
          f"(r={cells[i_min_add]['r']:.3f}, V={cells[i_min_add]['V']:.4f}, "
          f"v={cells[i_min_add]['v']:.0f}, {cells[i_min_add]['variant']})")
    print(f"  min CF_mul = {cf_mul[i_min_mul]:.4f} @ "
          f"(r={cells[i_min_mul]['r']:.3f}, V={cells[i_min_mul]['V']:.4f}, "
          f"v={cells[i_min_mul]['v']:.0f}, {cells[i_min_mul]['variant']})")
    print(f"  Delta CF = CF_mult - CF_add over S: "
          f"mean={float(np.mean(cf_mul-cf_add)):.4f}, "
          f"median={float(np.median(cf_mul-cf_add)):.4f}, "
          f"min={float(np.min(cf_mul-cf_add)):.4f}, "
          f"max={float(np.max(cf_mul-cf_add)):.4f}")
    if n_new_flips > 0:
        flips = [cells[i] for i in np.where(new_flip_mask)[0]]
        print(f"  NEW-FLIP cells ({n_new_flips}):")
        for c in flips:
            print(f"    r={c['r']:.3f} V={c['V']:.4f} v={c['v']:.0f} {c['variant']}"
                  f" | CF_add={c['cf_add_recomputed']:.4f} -> CF_mult={c['cf_mult']:.4f}"
                  f" (dCF={c['delta_cf']:.4f})")

    # --- Block C: full-grid multiplicative cross-check (global statistic). --
    # Cheap (~45s); gives the honest "fraction of ALL 4,410 cells with CF<0.5
    # under each rule" and bounds new-flips OUTSIDE S (a cell with additive
    # CF>=0.60 cannot newly flip if max erosion over the grid < 0.10).
    print(f"\n[Block C] full-grid multiplicative sweep (4,410 cells) for the "
          f"global CF<0.5 fraction ...")
    r_grid = np.unique(np.concatenate(
        [np.logspace(np.log10(0.1), np.log10(10.0), 21), np.array([1.0])]))
    V_grid = np.linspace(1.0 / N, 1.0, 21)
    v_grid = [1, 2, 3, 4, 5]
    variants = ["A", "B"]

    # Index run-003 additive CF by (r,V,v,variant) for paired comparison.
    def key(r, V, v, variant):
        return (round(float(r), 9), round(float(V), 9), int(v), variant)
    add_lookup = {key(x["r"], x["V"], x["v"], x["variant"]):
                  (x["criterion_fraction"], x["total_gain"]) for x in rows003}

    mul_cfs, add_cfs_valid, paired = [], [], []
    n_valid = 0
    worst_erosion = 0.0
    worst_cell = None
    for r in r_grid:
        for V in V_grid:
            for variant in variants:
                for v in v_grid:
                    mul = compute_CF(float(r), float(V), float(v), N, d_max, f0,
                                     h, variant, alpha_grid,
                                     beta_gamma_multiplicative)
                    if mul["total_gain"] <= VALID_THRESH:
                        continue
                    n_valid += 1
                    mul_cfs.append(mul["criterion_fraction"])
                    a_cf, a_tg = add_lookup.get(key(r, V, v, variant), (None, None))
                    if a_cf is not None and a_tg is not None and a_tg > VALID_THRESH:
                        add_cfs_valid.append(a_cf)
                        d = mul["criterion_fraction"] - a_cf
                        paired.append(d)
                        if -d > worst_erosion:    # most negative dCF = worst erosion
                            worst_erosion = -d
                            worst_cell = dict(r=float(r), V=float(V), v=int(v),
                                              variant=variant, cf_add=a_cf,
                                              cf_mult=mul["criterion_fraction"])
    mul_cfs = np.array(mul_cfs)
    add_cfs_valid = np.array(add_cfs_valid)
    paired = np.array(paired)
    print(f"  valid cells (mult): {n_valid}")
    print(f"  additive : CF<0.5 = {int((add_cfs_valid<0.5).sum())}/{len(add_cfs_valid)} "
          f"({100.0*(add_cfs_valid<0.5).mean():.2f}%), median CF = {np.median(add_cfs_valid):.4f}")
    print(f"  mult.    : CF<0.5 = {int((mul_cfs<0.5).sum())}/{len(mul_cfs)} "
          f"({100.0*(mul_cfs<0.5).mean():.2f}%), median CF = {np.median(mul_cfs):.4f}")
    print(f"  paired Delta CF (mult-add): mean={paired.mean():.4f}, "
          f"median={np.median(paired):.4f}, min={paired.min():.4f}, max={paired.max():.4f}")
    print(f"  worst CF erosion over full grid: dCF={-worst_erosion:.4f} at {worst_cell}")

    # --- Save. -------------------------------------------------------------
    result = dict(
        block0_parent_map_max_dev=map_dev,
        selection=dict(n_total_rows=len(rows003), n_at_risk_S=len(S),
                       valid_threshold=VALID_THRESH, cf_cut=0.60),
        block_A=dict(
            max_add_crosscheck=max_add_xcheck,
            max_p3p4_family_dev=max(c["p3p4_family_dev"] for c in cells),
            n_add_below_050=n_add_below, n_mult_below_050=n_mul_below,
            n_new_flips=n_new_flips, n_recovered=n_recovered,
            min_cf_add=float(cf_add[i_min_add]), min_cf_add_cell=cells[i_min_add],
            min_cf_mult=float(cf_mul[i_min_mul]), min_cf_mult_cell=cells[i_min_mul],
            delta_cf_mean=float(np.mean(cf_mul - cf_add)),
            delta_cf_median=float(np.median(cf_mul - cf_add)),
            delta_cf_min=float(np.min(cf_mul - cf_add)),
            delta_cf_max=float(np.max(cf_mul - cf_add)),
            new_flip_cells=[cells[i] for i in np.where(new_flip_mask)[0]],
            cells=cells),
        block_C=dict(
            n_valid_mult=n_valid,
            additive_frac_below_050=float((add_cfs_valid < 0.5).mean()),
            additive_n_below_050=int((add_cfs_valid < 0.5).sum()),
            additive_median_cf=float(np.median(add_cfs_valid)),
            mult_frac_below_050=float((mul_cfs < 0.5).mean()),
            mult_n_below_050=int((mul_cfs < 0.5).sum()),
            mult_median_cf=float(np.median(mul_cfs)),
            paired_delta_cf_mean=float(paired.mean()),
            paired_delta_cf_median=float(np.median(paired)),
            paired_delta_cf_min=float(paired.min()),
            paired_delta_cf_max=float(paired.max()),
            worst_erosion_dcf=float(-worst_erosion), worst_erosion_cell=worst_cell),
        metadata=dict(phi_backend=_PHI_BACKEND, c_grid_step=0.05,
                      alpha_grid_step=0.02, N=N, d_max=d_max, f0=f0, h="sqrt",
                      claim_id="A3", attack_vector="replication",
                      run_id="run-011", task_id="CR-008", prompt_version="0.2",
                      date="2026-05-24", elapsed_s=round(time.time() - t0, 2)))
    out_path = os.path.join(outdir, "results.json")
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2, default=float)
    print(f"\nSaved {out_path}  (elapsed {result['metadata']['elapsed_s']}s)")


if __name__ == "__main__":
    main()
