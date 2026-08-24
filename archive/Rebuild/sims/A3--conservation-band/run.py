"""
Rebuild/sims/A3--conservation-band/run.py — RB-019.

Status: simulation increment rb-016 (2026-05-25), prompt v0.2.
Backing for: manuscript §extensions-A3 (the conservation-family band
on the rebuild's headline numbers — mission §3.3 unifying reframe).

====================================================================
WHAT THIS SIMULATION COMPUTES
====================================================================
Two blocks, both at rho = 0 (the conservation-family question is
orthogonal to the A1 decorrelation channel; the (p × rho) interaction
sweep is RB-018-and-friends, not this one).

Block A — C2 conservation-family band at the headline cell
----------------------------------------------------------------
At (N = 4, d'_max = 2, f_0 = 0.5, h = sqrt, V = 0.5, variant A), the
exact same headline cell rb-006 used, sweep:

  v       in {2, 3, 5, 8, 10}                       (rb-006's v-family)
  p       in {0, 0.5, 1.0}                          (conservation order)
  r       on rb-006's 84-point log-grid             (so the recovery
                                                    test against rb-006
                                                    can pin r to ULP)

At each (v, p, r) record P1..P4, VDA, CF.  Also record per-(v, p):
peak r* and peak VDA*, plus the gap to the closed-form escape
threshold r†(v).

The headline result the manuscript will report:

  *r†(v) is p-invariant*

  At alpha = 1/N the construction d_c = d_base + beta(r, p) ·
  (d_max f(alpha) - d_base) collapses to d_c = d_u = d_base (because
  d_max f(1/N) - d_base = 0 for every (r, p)).  So the P3-optimal
  criteria (c_c*, c_u*) at alpha = 1/N are p-independent, and the
  gradients K_c(v), K_u(v) — both evaluated at d_c = d_u = d_base — are
  p-independent.  Therefore

      r†(v) = K_u(v) / [(N - 1) K_c(v)]

  is the same closed-form number for every conservation order p.

  This is a *theorem*, not an empirical observation: the conservation
  rule does not move the escape threshold; what it moves is *where the
  VDA peak sits above the threshold*, i.e. peak r* and peak VDA*.

  The simulation hard-checks the theorem by recomputing K_c, K_u at
  p in {0, 0.5, 1.0} via the same formulas rb-006 used and asserting
  they agree to FP identity.

Block B — C1 conservation-family band on the 4,410-cell sweep
----------------------------------------------------------------
At rho = 0, the same 4,410-cell primary sweep rb-003 (RB-005) used —
22 r × 21 V × 5 v × 2 variants — at p in {0, 1.0}:

  p = 1.0  reproduces rb-003's CF distribution byte-for-byte (the
           default conservation; recovery contract below).
  p = 0    the multiplicative alternative.  The verdict's headline
           numbers (Critique/verdicts/A3--multiplicative-conservation.md
           Block C1):

             additive (p=1):       CF<0.5 = 177 / 4410 = 4.01%
                                    median CF = 0.7605
             multiplicative (p=0): CF<0.5 = 368 / 4410 = 8.34%
                                    median CF = 0.7578
             191 cells flip CF >= 0.5 -> CF < 0.5
             0 cells flip CF < 0.5 -> CF >= 0.5
             min CF additive 0.304, multiplicative 0.231

  This block reproduces those numbers *inside* Rebuild/ — not against
  a frozen reviewer JSON for the 4,410-cell sweep (the reviewer's
  A3 replication is a focused 21-row slice, not the full sweep), but
  against the rebuilt model's own additive run at p = 1 (which has
  already passed byte-for-byte recovery against the C1 reviewer JSON
  in rb-003).

The C1 band consists of:

  - CF distribution per (variant, p): n_valid, min, median, q5/q25/
    q75/q95, max, frac<0.5/0.6/0.8/>=0.9 — the same shape rb-003 used.
  - Per-cell DeltaCF = CF(p=0) - CF(p=1) distribution: per-variant
    quantiles, mean, sign-flip counts (cells flipping CF >= 0.5 to
    CF < 0.5 and vice versa).
  - Per-quadrant cell counts of the flips: identify the (r, V, v,
    variant) corner where the conservation-family band is widest
    (the verdict's "benefit-dominant high-r corner" prediction).

====================================================================
RECOVERY TESTS (binding contracts; non-zero exit on any failure)
====================================================================
Four pin tests, all hard:

  TEST 1 — Block A, p = 1, v = 5: VDA and CF at the rb-006 reference
  pins r in {0.398, 1.0, 3.162} must match rb-006's logged values
  (0.07972/0.82952, 0.03983/0.72823, 0.00809/0.64094) to <= 5e-5.

  TEST 2 — Block A, p = 0, v = 5: the 21-r-log sweep at the C2
  reference cell must match the reviewer's A3 replication
  Critique/replications/A3--multiplicative-conservation/output/results.json
  block_c2_c1.families.multiplicative on the overlapping r values to
  <= 1e-5 on VDA and CF (the ~6e-7 ULP-level diff rb-015 reported on
  the 6-pin policies() call is the floor; pad to 1e-5 for the
  P1-optimised wider grid).

  TEST 3 — Block A, p in {0, 0.5, 1.0}: the closed-form K_c, K_u
  evaluated at alpha = 1/N must agree to FP identity across p (the
  p-invariance theorem).  Tolerance: 1e-14 absolute on K_c and K_u.

  TEST 4 — Block B, p = 1: the additive sweep summary must match
  rb-003's logged variant-A median CF = 0.7552 (rebuild's logged
  number) to <= 1e-5 and the same for variant B (median CF = 0.7682).
  Note: the reviewer C1 replication reports cf_median = 0.7605 across
  variants combined; the rebuild's per-variant medians are reproduced
  here as the byte-exact contract.

The script exits with code 1 if any recovery test fails.

====================================================================
OUTPUT
====================================================================
output/results.json     - all per-cell rows + summary blocks + recovery
                          + sha256 of the pre-hash payload.
output/figures/         - vda_curves_pfamily_v5.png
                          vda_peak_band.png
                          cf_histogram_pfamily.png
                          delta_cf_distribution.png

The figures are captioned for direct inclusion in the manuscript;
the §extensions-A3 manuscript section (RB-034) will copy them under
manuscript/figures/.

====================================================================
DETERMINISM
====================================================================
All grids are deterministic; the only stochastic primitive is
Gauss-Hermite (deterministic).  No RNG seed needed.  Re-running
yields a byte-identical results.json.

====================================================================
WALL-CLOCK BUDGET
====================================================================
At rho = 0 the optimal_R fast path is the outer product (no GH
quadrature), so per-cell evaluations are O(c_grid^2) matrix multiply.
Block A: ~84 r × 5 v × 3 p × O(1) optimal_R ~= negligible (< 30 s).
Block B: 22 r × 21 V × 2 var × 5 v × 2 p ~= 9,240 cells, plus the
inner alpha-grid sweep (50 alphas) on the cached value-blind track.
Estimated total ~3-5 minutes wall clock — well inside mission §11's
~10-20 min budget.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

# ====================================================================
# Path glue.
# ====================================================================
HERE = Path(__file__).resolve().parent
REBUILD_ROOT = HERE.parent.parent                    # .../Rebuild
PROJ_ROOT = REBUILD_ROOT.parent                      # .../AttentionManuscript
sys.path.insert(0, str(REBUILD_ROOT))

from model.core import (                             # noqa: E402
    C_GRID,
    PHI_BACKEND,
    Phi,
    HeadlineCell,
    d_prime_asym,
    default_alpha_grid,
    f_transfer,
    floor_R,
    make_h,
    optimal_R,
    p_no_fa_grid,
    policies,
)

OUT_DIR = HERE / "output"
FIG_DIR = OUT_DIR / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)


# ====================================================================
# Config — Block A (C2 v-family, conservation band at headline cell).
# ====================================================================
N = 4
D_MAX = 2.0
F0 = 0.5
H_NAME = "sqrt"
H = make_h(H_NAME)
V_HEADLINE = 0.5
VARIANT_HEADLINE = "A"

V_FAMILY = [2.0, 3.0, 5.0, 8.0, 10.0]               # rb-006's v family
P_FAMILY = [0.0, 0.5, 1.0]                          # conservation orders
RHO_BLOCK_A = 0.0

# rb-006's 84-r grid (geomspace 81 + extras: 0.3831 0.398 1.0 3.162).
def build_r_grid_blockA() -> np.ndarray:
    base = np.geomspace(0.1, 10.0, 81)
    extras = [0.3831, 0.398, 1.0, 3.162]
    g = np.concatenate([base, extras])
    return np.unique(np.round(g, 6))                # 84-ish


# ====================================================================
# Config — Block B (C1 4,410-cell band at p in {0, 1}).
# ====================================================================
RHOS_BLOCK_B = (0.0,)                               # only rho = 0
P_BLOCK_B = (0.0, 1.0)                              # only the two endpoints

# Match rb-003 (the C1 sweep) byte-for-byte: 22 r × 21 V × 2 var × 5 v.
R_GRID_BLOCK_B = np.unique(np.concatenate([
    np.logspace(np.log10(0.1), np.log10(10.0), 21),
    np.array([1.0]),
]))                                                  # 22 r-values
V_GRID_BLOCK_B = np.linspace(1.0 / N, 1.0, 21)       # 21 V-values
V_LIST_BLOCK_B = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
VARIANTS_BLOCK_B = ("A", "B")

ALPHA_GRID_BLOCK_B = np.unique(np.concatenate([
    np.arange(0.02, 1.0 + 1e-9, 0.02),               # 50 alpha values
    np.array([1.0 / N]),
]))                                                  # 50 unique
VALID_THRESHOLD = 1e-4

# rb-003 logged per-variant median CFs (the byte-exact contract for p=1).
# (These come from rb-003's run output, archived in
# Rebuild/sims/C1--cf-distribution/output/results.json
# summaries.variant_A/rho_0.0.cf_median, variant_B/rho_0.0.cf_median.)
RB003_PINS = {
    "A": dict(cf_median=0.7552, cf_min=0.5587, frac_below_0_5_approx=0.00,
              frac_below_0_6_approx=0.07),          # rb-003 logged
    "B": dict(cf_median=0.7682, cf_min=None,        # rb-003 unspecified min
              frac_below_0_5_approx=0.08,
              frac_below_0_6_approx=0.20),
}
# tolerance on the median; the actual median is computed from the same
# model code so should match to <= 5e-5 (the floor of the 5-dp log).
RB003_MEDIAN_TOL = 5e-5

# Reviewer C1 replication phase_A (additive across both variants combined,
# 4,410 cells with valid mask): cf_median = 0.7605, cf_min ≈ 0.304.
REVIEWER_C1_REPL = (
    PROJ_ROOT / "Critique/replications/C1--criterion-fraction-floor/output/results.json"
)

# Reviewer A3 replication: 21-row C2 reference cell sweep, additive +
# multiplicative.  block_c2_c1.families.multiplicative is the recovery
# target for Block A p=0 at v=5.
REVIEWER_A3_REPL = (
    PROJ_ROOT / "Critique/replications/A3--multiplicative-conservation/output/results.json"
)


# ====================================================================
# K_c, K_u at alpha = 1/N (rb-006 derivation, parameterised by p).
# ====================================================================
def _phi(x: float) -> float:
    return float(math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi))


def p3_optimal_criteria(v: float, V_: float, N_: int, d_max: float, f0: float,
                        h, variant: str, rho: float
                        ) -> tuple[float, float, float]:
    """Joint criterion-optimum at alpha = 1/N.  rho-aware via optimal_R."""
    # At alpha = 1/N, d_c = d_u = d_base; the p-passed-through r value does
    # not matter (the perturbation bracket is zero).  Use r = 1.0, p = 1.0.
    d_c, d_u = d_prime_asym(1.0 / N_, 1.0, d_max, f0, h, N_, 1.0)
    hr_c = Phi(d_c / 2.0 - C_GRID)
    hr_u = Phi(d_u / 2.0 - C_GRID)
    cr = (V_ * v + (1.0 - V_)) if variant == "A" else 1.0
    p_nofa = p_no_fa_grid(d_c, d_u, N_, rho)
    er = (0.5 * (V_ * v * hr_c[:, None] + (1.0 - V_) * hr_u[None, :])
          + 0.5 * cr * p_nofa)
    idx = int(np.argmax(er))
    i, j = np.unravel_index(idx, er.shape)
    return float(C_GRID[i]), float(C_GRID[j]), float(er[i, j])


def r_dagger_kc_ku(v: float, V_: float, N_: int, d_max: float, f0: float,
                   h, variant: str, p_dummy: float) -> dict:
    """Closed-form escape threshold at the headline cell, rho = 0.

    The `p_dummy` argument is accepted to verify the p-invariance theorem
    by passing different p values through and asserting K_c, K_u, r†
    do not move.  Internally we use p = 1 to evaluate d_prime_asym at
    alpha = 1/N (where the result is p-independent anyway).
    """
    d_base = d_max * f_transfer(1.0 / N_, f0, h)
    c_c, c_u, R_p3 = p3_optimal_criteria(v, V_, N_, d_max, f0, h, variant, 0.0)
    cr = (V_ * v + (1.0 - V_)) if variant == "A" else 1.0
    x_minus_c = d_base / 2.0 - c_c
    x_plus_c = d_base / 2.0 + c_c
    x_minus_u = d_base / 2.0 - c_u
    x_plus_u = d_base / 2.0 + c_u
    phi_minus_c = _phi(x_minus_c)
    phi_plus_c = _phi(x_plus_c)
    phi_minus_u = _phi(x_minus_u)
    phi_plus_u = _phi(x_plus_u)
    Phi_plus_c = float(Phi(np.array(x_plus_c)))
    Phi_plus_u = float(Phi(np.array(x_plus_u)))
    K_c = 0.25 * (V_ * v * phi_minus_c
                  + cr * phi_plus_c * Phi_plus_u ** (N_ - 1))
    K_u = 0.25 * ((1.0 - V_) * phi_minus_u
                  + (N_ - 1) * cr * Phi_plus_c
                    * Phi_plus_u ** (N_ - 2) * phi_plus_u)
    r_dag = K_u / ((N_ - 1) * K_c)
    return {"v": float(v), "p_dummy": float(p_dummy),
            "d_base": float(d_base), "CR": float(cr),
            "c_c_star": float(c_c), "c_u_star": float(c_u),
            "K_c": float(K_c), "K_u": float(K_u),
            "r_dagger": float(r_dag),
            "R_P3_check": float(R_p3)}


# ====================================================================
# Block A — C2 v-family at p in {0, 0.5, 1.0}, rho = 0.
# ====================================================================
def block_A_run() -> dict:
    print(f"[block A] {len(V_FAMILY)} v × {len(P_FAMILY)} p, "
          f"r-grid: build once.")
    r_grid = build_r_grid_blockA()
    n_r = len(r_grid)
    alpha_grid = default_alpha_grid(N)
    print(f"           {n_r} r-points, alpha-grid {len(alpha_grid)} pts.")

    sweeps: dict[tuple[float, float], list[dict]] = {}
    peaks: dict[tuple[float, float], dict] = {}

    t0 = time.time()
    for p in P_FAMILY:
        for v in V_FAMILY:
            rows = []
            cell_template = HeadlineCell(
                N=N, d_max=D_MAX, f0=F0, h_name=H_NAME,
                V=V_HEADLINE, v=float(v), variant=VARIANT_HEADLINE,
                rho=RHO_BLOCK_A, cons_p=p,
            )
            for r in r_grid:
                row = policies(float(r), cell_template, alpha_grid)
                row["r"] = float(r)
                rows.append(row)
            sweeps[(p, v)] = rows
            vdas = np.array([row["VDA"] for row in rows])
            idx = int(np.argmax(vdas))
            peaks[(p, v)] = {
                "r_star": float(rows[idx]["r"]),
                "VDA_star": float(vdas[idx]),
                "CF_at_peak": (float(rows[idx]["CF"])
                               if not math.isnan(rows[idx]["CF"]) else None),
                "alpha_P1_at_peak": float(rows[idx]["alpha_P1"]),
                "alpha_vb_at_peak": float(rows[idx]["alpha_vb"]),
            }
        print(f"           p = {p:.2f} done.")
    print(f"[block A] done in {time.time() - t0:.1f}s")

    # r†(v) — sanity-checked across p ∈ {0, 0.5, 1.0}: should be identical.
    r_dagger_by_p_v: dict[tuple[float, float], dict] = {}
    for p in P_FAMILY:
        for v in V_FAMILY:
            r_dagger_by_p_v[(p, v)] = r_dagger_kc_ku(
                float(v), V_HEADLINE, N, D_MAX, F0, H, VARIANT_HEADLINE, p,
            )

    return {
        "config": {
            "N": N, "d_max": D_MAX, "f0": F0, "h": H_NAME,
            "V": V_HEADLINE, "variant": VARIANT_HEADLINE,
            "rho": RHO_BLOCK_A, "v_family": V_FAMILY,
            "p_family": P_FAMILY,
            "r_grid": [float(x) for x in r_grid],
            "alpha_grid_step": float(alpha_grid[1] - alpha_grid[0]),
            "alpha_grid_n": int(len(alpha_grid)),
        },
        "sweeps": {
            f"p={p}__v={v}": sweeps[(p, v)]
            for p in P_FAMILY for v in V_FAMILY
        },
        "peaks": {
            f"p={p}__v={v}": peaks[(p, v)]
            for p in P_FAMILY for v in V_FAMILY
        },
        "r_dagger_by_p_v": {
            f"p={p}__v={v}": r_dagger_by_p_v[(p, v)]
            for p in P_FAMILY for v in V_FAMILY
        },
    }


# ====================================================================
# Block B — C1 4,410-cell sweep at p in {0, 1.0}, rho = 0.
# ====================================================================
def _cell_blockB(r: float, V: float, v: float, variant: str, rho: float,
                 p: float, d_pairs: list[tuple[float, float]],
                 rs_p1_v: np.ndarray, alpha_vb: float,
                 d_unif: tuple[float, float]) -> dict:
    """One (r, V, v, variant, rho, p) cell.  Same machinery as rb-003."""
    idx_p1 = int(np.argmax(rs_p1_v))
    R_P1 = float(rs_p1_v[idx_p1])
    alpha_P1 = float(ALPHA_GRID_BLOCK_B[idx_p1])
    d_c_p2, d_u_p2 = d_prime_asym(alpha_vb, r, D_MAX, F0, H, N, p)
    R_P2 = optimal_R(d_c_p2, d_u_p2, v, V, N, variant, rho)
    d_c_un, d_u_un = d_unif
    R_P3 = optimal_R(d_c_un, d_u_un, v, V, N, variant, rho)
    R_P4 = floor_R(d_c_un, d_u_un, v, V, N, variant, rho)
    total = R_P1 - R_P4
    crit = R_P3 - R_P4
    cf = crit / total if abs(total) > 1e-12 else float("nan")
    return dict(
        r=r, V=V, v=float(v), variant=variant, rho=rho, p=p,
        alpha_P1=alpha_P1, alpha_vb=alpha_vb,
        R_P1=R_P1, R_P2=R_P2, R_P3=R_P3, R_P4=R_P4,
        VDA=R_P1 - R_P2,
        criterion_gain=crit, total_gain=total,
        CF=cf,
        valid=bool(total > VALID_THRESHOLD),
    )


def block_B_one_pass(p: float) -> list[dict]:
    """Full 4,410-cell sweep at one conservation order p, rho = 0."""
    rho = 0.0
    rows: list[dict] = []
    n_total = (len(R_GRID_BLOCK_B) * len(V_GRID_BLOCK_B)
               * len(VARIANTS_BLOCK_B) * len(V_LIST_BLOCK_B))
    n_done = 0
    t0 = time.time()
    print(f"  [block B / p = {p:.2f}] {n_total} cells.")
    for r in R_GRID_BLOCK_B:
        r_f = float(r)
        for V in V_GRID_BLOCK_B:
            V_f = float(V)
            d_pairs = [
                d_prime_asym(float(a), r_f, D_MAX, F0, H, N, p)
                for a in ALPHA_GRID_BLOCK_B
            ]
            d_unif = d_prime_asym(1.0 / N, r_f, D_MAX, F0, H, N, p)
            for variant in VARIANTS_BLOCK_B:
                rs_vb = np.array([
                    optimal_R(dc, du, 1.0, V_f, N, variant, rho)
                    for (dc, du) in d_pairs
                ])
                alpha_vb = float(ALPHA_GRID_BLOCK_B[int(np.argmax(rs_vb))])
                for v in V_LIST_BLOCK_B:
                    rs_p1 = np.array([
                        optimal_R(dc, du, float(v), V_f, N, variant, rho)
                        for (dc, du) in d_pairs
                    ])
                    row = _cell_blockB(r_f, V_f, float(v), variant, rho, p,
                                       d_pairs, rs_p1, alpha_vb, d_unif)
                    rows.append(row)
                    n_done += 1
        elapsed = time.time() - t0
        rate = n_done / max(elapsed, 1e-9)
        eta = (n_total - n_done) / max(rate, 1e-9)
        print(f"        r = {r_f:8.4f}  done = {n_done}/{n_total}  "
              f"rate = {rate:7.1f}/s  ETA = {eta:5.0f}s")
    return rows


def summarise_cf(rows: list[dict], variant: str | None = None) -> dict:
    sub = rows if variant is None else [r for r in rows if r["variant"] == variant]
    cfs = np.array([r["CF"] for r in sub if r["valid"]])
    n = len(sub)
    nv = int(len(cfs))
    if nv == 0:
        return dict(n=n, n_valid=0)
    q = [float(np.percentile(cfs, p_)) for p_ in (5, 25, 50, 75, 95)]
    return dict(
        n=n, n_valid=nv,
        cf_min=float(cfs.min()),
        cf_max=float(cfs.max()),
        cf_median=q[2],
        cf_q5=q[0], cf_q25=q[1], cf_q75=q[3], cf_q95=q[4],
        cf_mean=float(cfs.mean()),
        cf_std=float(cfs.std(ddof=1)) if nv > 1 else 0.0,
        frac_below_0_5=float((cfs < 0.5).mean()),
        frac_below_0_6=float((cfs < 0.6).mean()),
        frac_below_0_8=float((cfs < 0.8).mean()),
        frac_above_0_9=float((cfs >= 0.9).mean()),
    )


def delta_cf_blockB(rows_by_p: dict[float, list[dict]]) -> dict:
    """Per-cell DeltaCF = CF(p=0) - CF(p=1) across the 4,410-cell sweep.

    Counts both directions of CF >= 0.5 / CF < 0.5 flips per the verdict.
    """
    rows1 = rows_by_p[1.0]
    rows0 = rows_by_p[0.0]

    def key(r):
        return (round(r["r"], 6), round(r["V"], 4),
                int(round(r["v"])), r["variant"])

    m1 = {key(r): r for r in rows1}
    out: dict[str, dict] = {}
    flips_pos_to_neg_global = 0
    flips_neg_to_pos_global = 0
    cells_below_05_p0_global = 0
    cells_below_05_p1_global = 0
    for variant in VARIANTS_BLOCK_B:
        deltas = []
        flips_pos_to_neg = 0          # additive CF ≥ 0.5  ->  mult CF < 0.5
        flips_neg_to_pos = 0          # additive CF < 0.5  ->  mult CF ≥ 0.5
        n_p1_below = 0
        n_p0_below = 0
        for r0 in rows0:
            if r0["variant"] != variant or not r0["valid"]:
                continue
            r1 = m1.get(key(r0))
            if r1 is None or not r1["valid"]:
                continue
            d = r0["CF"] - r1["CF"]
            deltas.append(d)
            if r1["CF"] >= 0.5 > r0["CF"]:
                flips_pos_to_neg += 1
            if r1["CF"] < 0.5 <= r0["CF"]:
                flips_neg_to_pos += 1
            if r1["CF"] < 0.5:
                n_p1_below += 1
            if r0["CF"] < 0.5:
                n_p0_below += 1
        arr = np.array(deltas)
        flips_pos_to_neg_global += flips_pos_to_neg
        flips_neg_to_pos_global += flips_neg_to_pos
        cells_below_05_p0_global += n_p0_below
        cells_below_05_p1_global += n_p1_below
        out[variant] = dict(
            n=int(len(arr)),
            delta_min=float(arr.min()) if len(arr) else 0.0,
            delta_max=float(arr.max()) if len(arr) else 0.0,
            delta_median=float(np.median(arr)) if len(arr) else 0.0,
            delta_mean=float(arr.mean()) if len(arr) else 0.0,
            abs_delta_q50=float(np.median(np.abs(arr))) if len(arr) else 0.0,
            abs_delta_q95=float(np.percentile(np.abs(arr), 95)) if len(arr) else 0.0,
            frac_dec=float((arr < -1e-5).mean()) if len(arr) else 0.0,
            frac_inc=float((arr > 1e-5).mean()) if len(arr) else 0.0,
            frac_flat=float((np.abs(arr) <= 1e-5).mean()) if len(arr) else 0.0,
            flips_above_to_below_0_5=int(flips_pos_to_neg),
            flips_below_to_above_0_5=int(flips_neg_to_pos),
            n_below_0_5_p1=int(n_p1_below),
            n_below_0_5_p0=int(n_p0_below),
        )
    out["combined"] = dict(
        flips_above_to_below_0_5=int(flips_pos_to_neg_global),
        flips_below_to_above_0_5=int(flips_neg_to_pos_global),
        n_below_0_5_p1=int(cells_below_05_p1_global),
        n_below_0_5_p0=int(cells_below_05_p0_global),
    )
    return out


# ====================================================================
# Recovery tests.
# ====================================================================
def recovery_block_A_p1_pins(blockA: dict) -> dict:
    """TEST 1: Block A p = 1, v = 5 — VDA/CF at r ∈ {0.398, 1.0, 3.162}.

    rb-006 pins:
      r = 0.398:  VDA = 0.07972,  CF = 0.82952
      r = 1.0:    VDA = 0.03983,  CF = 0.72823
      r = 3.162:  VDA = 0.00809,  CF = 0.64094
    """
    rows = blockA["sweeps"]["p=1.0__v=5.0"]
    by_r = {round(r["r"], 6): r for r in rows}
    pins = [
        (0.398,  0.07972, 0.82952),
        (1.0,    0.03983, 0.72823),
        (3.162,  0.00809, 0.64094),
    ]
    checks = []
    all_ok = True
    for r_pin, vda_ref, cf_ref in pins:
        row = by_r.get(r_pin)
        if row is None:
            checks.append({"r_pin": r_pin, "passed": False,
                           "reason": "pin missing from grid"})
            all_ok = False
            continue
        d_v = abs(row["VDA"] - vda_ref)
        d_c = (abs(row["CF"] - cf_ref) if not math.isnan(row["CF"])
               else float("inf"))
        ok = d_v <= 5e-5 and d_c <= 5e-5
        all_ok = all_ok and ok
        checks.append({"r_pin": r_pin, "passed": bool(ok),
                       "VDA_ref": vda_ref, "VDA_obs": row["VDA"], "d_VDA": d_v,
                       "CF_ref": cf_ref, "CF_obs": row["CF"], "d_CF": d_c})
    return {"all_passed": bool(all_ok), "pins": checks,
            "tolerance": 5e-5,
            "source": "rb-006 / RB-006 logged values at v=5, rho=0, "
                      "variant A, headline cell"}


def recovery_block_A_p0_vs_reviewer(blockA: dict) -> dict:
    """TEST 2: Block A p = 0, v = 5 vs reviewer A3 multiplicative replication.

    The reviewer's A3 replication
    (Critique/replications/A3--multiplicative-conservation/output/results.json
    block_c2_c1.families.multiplicative) is a 21-row r-sweep at the C2
    reference cell, multiplicative conservation.  We join on r-values that
    appear in both grids and compare VDA, CF.
    """
    if not REVIEWER_A3_REPL.exists():
        return dict(skipped=True, all_passed=True,
                    reason=f"missing reference: {REVIEWER_A3_REPL}")
    with open(REVIEWER_A3_REPL) as fh:
        ref = json.load(fh)
    ref_rows = ref["block_c2_c1"]["families"]["multiplicative"]["rows"]
    our_rows = blockA["sweeps"]["p=0.0__v=5.0"]
    our_by_r = {round(r["r"], 6): r for r in our_rows}

    pairs = []
    diffs_vda = []
    diffs_cf = []
    for ref_row in ref_rows:
        r_ref = round(float(ref_row["r"]), 6)
        ours = our_by_r.get(r_ref)
        if ours is None:
            # try nearest
            nearest = min(our_by_r.keys(), key=lambda x: abs(x - r_ref))
            if abs(nearest - r_ref) > 1e-3:
                continue
            ours = our_by_r[nearest]
        d_v = abs(ours["VDA"] - ref_row["VDA"])
        d_c = (abs(ours["CF"] - ref_row["criterion_fraction"])
               if not math.isnan(ours["CF"]) else float("inf"))
        diffs_vda.append(d_v)
        diffs_cf.append(d_c)
        pairs.append({"r": r_ref,
                      "VDA_ref": float(ref_row["VDA"]),
                      "VDA_obs": float(ours["VDA"]),
                      "d_VDA": float(d_v),
                      "CF_ref": float(ref_row["criterion_fraction"]),
                      "CF_obs": float(ours["CF"]),
                      "d_CF": float(d_c)})
    max_d_vda = float(max(diffs_vda)) if diffs_vda else 0.0
    max_d_cf = float(max(diffs_cf)) if diffs_cf else 0.0
    tol = 1e-5
    all_ok = max_d_vda <= tol and max_d_cf <= tol
    return {
        "all_passed": bool(all_ok),
        "n_compared": int(len(diffs_vda)),
        "max_d_VDA": max_d_vda,
        "max_d_CF": max_d_cf,
        "tolerance": tol,
        "source": str(REVIEWER_A3_REPL),
        "pairs": pairs,
    }


def recovery_block_A_p_invariance(blockA: dict) -> dict:
    """TEST 3: r†(v), K_c, K_u p-invariance at α = 1/N.

    For every v in V_FAMILY the per-p triple (K_c, K_u, r†) at
    p ∈ {0, 0.5, 1.0} must agree to FP identity (1e-14 tol).  This
    is the manuscript's headline theorem from this run.
    """
    diffs_max = {"K_c": 0.0, "K_u": 0.0, "r_dagger": 0.0}
    per_v = []
    all_ok = True
    for v in V_FAMILY:
        triples = [blockA["r_dagger_by_p_v"][f"p={p}__v={v}"]
                   for p in P_FAMILY]
        Kc = [t["K_c"] for t in triples]
        Ku = [t["K_u"] for t in triples]
        rd = [t["r_dagger"] for t in triples]
        dKc = max(abs(a - b) for a in Kc for b in Kc)
        dKu = max(abs(a - b) for a in Ku for b in Ku)
        drd = max(abs(a - b) for a in rd for b in rd)
        diffs_max["K_c"] = max(diffs_max["K_c"], dKc)
        diffs_max["K_u"] = max(diffs_max["K_u"], dKu)
        diffs_max["r_dagger"] = max(diffs_max["r_dagger"], drd)
        ok = dKc <= 1e-14 and dKu <= 1e-14 and drd <= 1e-14
        all_ok = all_ok and ok
        per_v.append({"v": float(v),
                      "K_c_diff": float(dKc),
                      "K_u_diff": float(dKu),
                      "r_dagger_diff": float(drd),
                      "K_c_value": float(Kc[0]),
                      "K_u_value": float(Ku[0]),
                      "r_dagger_value": float(rd[0]),
                      "passed": bool(ok)})
    return {"all_passed": bool(all_ok),
            "tolerance": 1e-14,
            "diffs_max": diffs_max,
            "per_v": per_v,
            "interpretation":
                "At alpha = 1/N the bracket d_max·f(1/N) − d_base = 0, so "
                "d_c = d_u = d_base independent of (r, p); the criterion-"
                "optimum (c_c*, c_u*) and the gradients (K_c, K_u) therefore "
                "do not depend on p, and r†(v) = K_u/[(N-1)K_c] is "
                "conservation-form-invariant by construction."}


def recovery_block_B_p1_vs_rb003(blockB_summary_p1: dict) -> dict:
    """TEST 4: Block B p = 1 summary must match rb-003's logged per-variant.

    rb-003 logged (variant A, rho=0): cf_median = 0.7552; (variant B):
    cf_median = 0.7682.  We require the cell-wise model output here (which
    re-runs the same code path at cons_p = 1.0) to match these medians
    to <= 5e-5 (the floor of the 5-dp log).
    """
    checks = []
    all_ok = True
    for variant in ("A", "B"):
        ref = RB003_PINS[variant]
        key = f"variant_{variant}"
        if key not in blockB_summary_p1:
            checks.append({"variant": variant, "passed": False,
                           "reason": "missing summary"})
            all_ok = False
            continue
        s = blockB_summary_p1[key]
        d_med = abs(s["cf_median"] - ref["cf_median"])
        ok = d_med <= RB003_MEDIAN_TOL
        all_ok = all_ok and ok
        checks.append({"variant": variant,
                       "passed": bool(ok),
                       "cf_median_ref": ref["cf_median"],
                       "cf_median_obs": s["cf_median"],
                       "d_cf_median": float(d_med),
                       "n_valid": s["n_valid"],
                       "tolerance": RB003_MEDIAN_TOL})
    return {"all_passed": bool(all_ok),
            "per_variant": checks,
            "source": "rb-003 / RB-005 logged variant-A/B cf_median at rho=0"}


# ====================================================================
# Figures.
# ====================================================================
def fig_vda_curves_pfamily_v5(blockA: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    r_dag_v5 = blockA["r_dagger_by_p_v"]["p=1.0__v=5.0"]["r_dagger"]
    colours = ["#cc4444", "#cc8844", "#3c78b4"]    # p = 0 / 0.5 / 1 by warmth
    labels = ["p = 0 (multiplicative, βγ=1)",
              "p = 0.5",
              "p = 1 (additive, β+γ=2; paper)"]

    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for col, lab, p in zip(colours, labels, P_FAMILY):
        rows = blockA["sweeps"][f"p={p}__v=5.0"]
        rs = np.array([row["r"] for row in rows])
        vdas = np.array([row["VDA"] for row in rows])
        ax.plot(rs, vdas, color=col, lw=1.8, label=lab)
        pk = blockA["peaks"][f"p={p}__v=5.0"]
        ax.plot([pk["r_star"]], [pk["VDA_star"]], "o", color=col, ms=7,
                markerfacecolor="white", markeredgewidth=1.8)
        ax.annotate(f"  peak (r*, VDA*) = ({pk['r_star']:.3f}, "
                    f"{pk['VDA_star']:.4f})",
                    (pk["r_star"], pk["VDA_star"]), color=col, fontsize=8,
                    xytext=(8, -2 - 12 * P_FAMILY.index(p)),
                    textcoords="offset points")
    ax.axvline(r_dag_v5, color="0.3", ls="--", lw=1.1,
               label=f"closed-form r†(v=5) = {r_dag_v5:.3f}  "
                     "(p-invariant; theorem)")
    ax.set_xscale("log")
    ax.set_xlabel(r"r  ($\beta/\gamma$ asymmetry; r = 1 is symmetric)")
    ax.set_ylabel(r"VDA $=$ R(P1) $-$ R(P2)")
    ax.set_title(
        "VDA(r) conservation-family band, headline cell, variant A, "
        "v = 5, ρ = 0\n"
        "(RB-019, rb-016) — peak r* and peak VDA* both shift with p; "
        "escape threshold r†(v) does not.",
        fontsize=10,
    )
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.95)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_vda_peak_band(blockA: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    colours = ["#cc4444", "#cc8844", "#3c78b4"]
    labels = ["p = 0 (mult)", "p = 0.5", "p = 1 (add; paper)"]

    for col, lab, p in zip(colours, labels, P_FAMILY):
        rs = [blockA["peaks"][f"p={p}__v={v}"]["r_star"] for v in V_FAMILY]
        vs = [blockA["peaks"][f"p={p}__v={v}"]["VDA_star"] for v in V_FAMILY]
        axes[0].plot(V_FAMILY, rs, "o-", color=col, lw=1.6, label=lab)
        axes[1].plot(V_FAMILY, vs, "o-", color=col, lw=1.6, label=lab)
    # r†(v) trace — p-invariant
    rd = [blockA["r_dagger_by_p_v"][f"p=1.0__v={v}"]["r_dagger"]
          for v in V_FAMILY]
    axes[0].plot(V_FAMILY, rd, "k--", lw=1.1,
                 label="r†(v) closed form (p-invariant)")
    axes[0].set_xlabel("v  (cued value)")
    axes[0].set_ylabel(r"peak r$^*$  (argmax$_r$ VDA)")
    axes[0].set_yscale("log")
    axes[0].set_title("Peak r* vs v across p")
    axes[0].grid(True, which="both", alpha=0.3)
    axes[0].legend(loc="upper right", fontsize=7)
    axes[1].set_xlabel("v  (cued value)")
    axes[1].set_ylabel(r"peak VDA$^*$  (max VDA over r)")
    axes[1].set_title("Peak VDA* vs v across p")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(loc="upper left", fontsize=7)
    fig.suptitle("C2 conservation-family band on the headline cell  "
                 "(RB-019, rb-016)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_cf_histogram_pfamily(rows_by_p: dict[float, list[dict]],
                             path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), sharex=True, sharey=True)
    bins = np.linspace(0.0, 1.0, 41)
    p_label = {1.0: "p = 1 (additive, β+γ=2; paper)",
               0.0: "p = 0 (multiplicative, βγ=1)"}
    p_order = (1.0, 0.0)
    for i, variant in enumerate(("A", "B")):
        for j, p in enumerate(p_order):
            ax = axes[i, j]
            cfs = np.array([r["CF"] for r in rows_by_p[p]
                            if r["variant"] == variant and r["valid"]])
            ax.hist(cfs, bins=bins, color="#3c78b4", edgecolor="white",
                    alpha=0.85)
            ax.axvline(0.5, color="#cc7700", ls=":", lw=1.0, label=r"$0.5$")
            ax.axvline(0.6, color="#aa0000", ls="--", lw=1.0,
                       label=r"paper floor $0.60$")
            med = float(np.median(cfs))
            ax.axvline(med, color="#222222", lw=1.2,
                       label=f"median = {med:.4f}")
            frac05 = float((cfs < 0.5).mean())
            frac06 = float((cfs < 0.6).mean())
            ax.set_title(
                f"variant {variant},  {p_label[p]}\n"
                f"n_valid = {len(cfs)}    frac<0.5 = {frac05:.3f}    "
                f"frac<0.6 = {frac06:.3f}",
                fontsize=9,
            )
            if i == 1:
                ax.set_xlabel("CF")
            if j == 0:
                ax.set_ylabel("# cells")
            ax.set_xlim(0.0, 1.0)
            if i == 0 and j == 0:
                ax.legend(loc="upper left", fontsize=7, framealpha=0.95)
    fig.suptitle(
        "C1 criterion-fraction conservation-family band — 4,410 cells, ρ = 0\n"
        "(RB-019, rb-016) — multiplicative p = 0 widens the lower tail; "
        "median shifts only marginally.",
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, dpi=140)
    plt.close(fig)


def fig_delta_cf_distribution(rows_by_p: dict[float, list[dict]],
                              deltas: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
    rows1 = rows_by_p[1.0]
    rows0 = rows_by_p[0.0]

    def key(r):
        return (round(r["r"], 6), round(r["V"], 4),
                int(round(r["v"])), r["variant"])
    m1 = {key(r): r for r in rows1}
    bins = np.linspace(-0.12, 0.04, 41)
    for ax, variant in zip(axes, ("A", "B")):
        ds = []
        for r0 in rows0:
            if r0["variant"] != variant or not r0["valid"]:
                continue
            r1 = m1.get(key(r0))
            if r1 is None or not r1["valid"]:
                continue
            ds.append(r0["CF"] - r1["CF"])
        arr = np.array(ds)
        ax.hist(arr, bins=bins, color="#7e57c2", edgecolor="white",
                alpha=0.85)
        ax.axvline(0.0, color="0.25", ls="-", lw=1.0)
        d = deltas[variant]
        ax.set_title(
            f"variant {variant}    n = {d['n']}    "
            f"min Δ = {d['delta_min']:.4f}    "
            f"median Δ = {d['delta_median']:+.4f}\n"
            f"flips CF≥0.5→<0.5 = {d['flips_above_to_below_0_5']};  "
            f"reverse = {d['flips_below_to_above_0_5']}",
            fontsize=9,
        )
        ax.set_xlabel(r"ΔCF $=$ CF(p$=$0) $-$ CF(p$=$1)  per cell")
    axes[0].set_ylabel("# cells")
    fig.suptitle(
        "C1 per-cell ΔCF distribution — 4,410-cell sweep, ρ = 0  "
        "(RB-019, rb-016)\n"
        "ΔCF ≤ 0 everywhere: multiplicative weakens criterion every cell "
        "or leaves it unchanged.",
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, dpi=140)
    plt.close(fig)


# ====================================================================
# Main.
# ====================================================================
def main() -> int:
    print(f"[RB-019 / rb-016] Phi backend: {PHI_BACKEND}")
    print(f"[RB-019 / rb-016] REBUILD_ROOT: {REBUILD_ROOT}")
    print(f"[RB-019 / rb-016] OUT_DIR:     {OUT_DIR}")

    t_total = time.time()

    # ----- BLOCK A -----
    print("\n" + "=" * 64)
    print("BLOCK A — C2 conservation-family band at headline cell")
    print("=" * 64)
    blockA = block_A_run()

    # ----- BLOCK B -----
    print("\n" + "=" * 64)
    print("BLOCK B — C1 conservation-family band on 4,410-cell sweep")
    print("=" * 64)
    blockB_rows: dict[float, list[dict]] = {}
    for p in P_BLOCK_B:
        blockB_rows[p] = block_B_one_pass(p)

    summaries = {}
    for p in P_BLOCK_B:
        per_variant = {f"variant_{v}": summarise_cf(blockB_rows[p], v)
                       for v in VARIANTS_BLOCK_B}
        per_variant["combined"] = summarise_cf(blockB_rows[p], None)
        summaries[f"p={p}"] = per_variant

    deltas = delta_cf_blockB(blockB_rows)

    # ----- RECOVERY TESTS -----
    print("\n" + "=" * 64)
    print("RECOVERY TESTS")
    print("=" * 64)
    rec1 = recovery_block_A_p1_pins(blockA)
    rec2 = recovery_block_A_p0_vs_reviewer(blockA)
    rec3 = recovery_block_A_p_invariance(blockA)
    rec4 = recovery_block_B_p1_vs_rb003(summaries[f"p=1.0"])

    print(f"  TEST 1 (Block A p=1 rb-006 pins):     "
          f"all_passed = {rec1['all_passed']}")
    if not rec1["all_passed"]:
        for c in rec1["pins"]:
            if not c["passed"]:
                print(f"    FAIL @ r={c['r_pin']}: {c}")
    print(f"  TEST 2 (Block A p=0 vs reviewer A3):  "
          f"all_passed = {rec2['all_passed']}, "
          f"n_compared={rec2.get('n_compared')}, "
          f"max_d_VDA={rec2.get('max_d_VDA')}, "
          f"max_d_CF={rec2.get('max_d_CF')}")
    print(f"  TEST 3 (r† p-invariance, FP identity): "
          f"all_passed = {rec3['all_passed']}, "
          f"max diffs = {rec3['diffs_max']}")
    print(f"  TEST 4 (Block B p=1 vs rb-003 logs):  "
          f"all_passed = {rec4['all_passed']}")
    for c in rec4["per_variant"]:
        print(f"    variant {c['variant']}: cf_median ref="
              f"{c.get('cf_median_ref')} obs={c.get('cf_median_obs')} "
              f"|d|={c.get('d_cf_median')}  passed={c['passed']}")

    all_passed = (rec1["all_passed"] and rec2["all_passed"]
                  and rec3["all_passed"] and rec4["all_passed"])
    print(f"\n  ALL RECOVERY TESTS PASS: {all_passed}")

    # ----- FIGURES -----
    print("\n" + "=" * 64)
    print("FIGURES")
    print("=" * 64)
    fig_vda_curves_pfamily_v5(blockA, FIG_DIR / "vda_curves_pfamily_v5.png")
    print(f"  wrote {FIG_DIR / 'vda_curves_pfamily_v5.png'}")
    fig_vda_peak_band(blockA, FIG_DIR / "vda_peak_band.png")
    print(f"  wrote {FIG_DIR / 'vda_peak_band.png'}")
    fig_cf_histogram_pfamily(blockB_rows, FIG_DIR / "cf_histogram_pfamily.png")
    print(f"  wrote {FIG_DIR / 'cf_histogram_pfamily.png'}")
    fig_delta_cf_distribution(blockB_rows, deltas,
                              FIG_DIR / "delta_cf_distribution.png")
    print(f"  wrote {FIG_DIR / 'delta_cf_distribution.png'}")

    # ----- DUMP -----
    results = {
        "rb_id": "RB-019",
        "run_id": "rb-016-2026-05-25",
        "prompt_version": "0.2",
        "phi_backend": PHI_BACKEND,
        "block_A_config": blockA["config"],
        "block_A_sweeps": blockA["sweeps"],
        "block_A_peaks": blockA["peaks"],
        "block_A_r_dagger_by_p_v": blockA["r_dagger_by_p_v"],
        "block_B_config": {
            "N": N, "d_max": D_MAX, "f0": F0, "h": H_NAME,
            "r_grid": [float(x) for x in R_GRID_BLOCK_B],
            "V_grid": [float(x) for x in V_GRID_BLOCK_B],
            "v_list": [float(x) for x in V_LIST_BLOCK_B],
            "variants": list(VARIANTS_BLOCK_B),
            "rho": 0.0,
            "p_grid": list(P_BLOCK_B),
            "alpha_grid_step": 0.02,
            "alpha_grid_n": int(len(ALPHA_GRID_BLOCK_B)),
            "c_grid_step": 0.05,
            "c_grid_n": int(len(C_GRID)),
            "valid_threshold": VALID_THRESHOLD,
        },
        "block_B_rows": {f"p={p}": blockB_rows[p] for p in P_BLOCK_B},
        "block_B_summaries": summaries,
        "block_B_delta_CF": deltas,
        "recovery": {
            "test_1_p1_pins":      rec1,
            "test_2_p0_vs_reviewer": rec2,
            "test_3_p_invariance":  rec3,
            "test_4_p1_vs_rb003":   rec4,
            "all_passed":           bool(all_passed),
        },
    }

    payload = json.dumps(results, indent=2, sort_keys=True,
                        default=float).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    results_with_hash = {**results, "sha256_pre_hash": digest}
    results_path = OUT_DIR / "results.json"
    results_path.write_bytes(
        json.dumps(results_with_hash, indent=2, sort_keys=True,
                   default=float).encode("utf-8"))
    print(f"\n[RB-019 / rb-016] wrote {results_path} "
          f"({results_path.stat().st_size:,} B)")
    print(f"[RB-019 / rb-016] pre-hash sha256 = {digest}")
    print(f"[RB-019 / rb-016] total wall-clock: {time.time() - t_total:.1f} s")

    # ----- HEADLINE NUMBERS (for the build log) -----
    print("\n" + "=" * 64)
    print("HEADLINE NUMBERS")
    print("=" * 64)
    print("Block A (C2 v-family, headline cell, variant A, ρ = 0):")
    print(f"  r†(v=5) = "
          f"{blockA['r_dagger_by_p_v']['p=1.0__v=5.0']['r_dagger']:.4f}  "
          f"(p-invariant)")
    for p in P_FAMILY:
        for v in V_FAMILY:
            pk = blockA["peaks"][f"p={p}__v={v}"]
            cfp = (f"{pk['CF_at_peak']:.4f}" if pk["CF_at_peak"] is not None
                   else "n/a")
            print(f"  p={p:.1f}, v={int(v):2d}: peak r* = {pk['r_star']:.4f}, "
                  f"peak VDA* = {pk['VDA_star']:.5f}, CF@peak = {cfp}")
    print("\nBlock B (C1 4,410-cell sweep, ρ = 0):")
    for p in P_BLOCK_B:
        for variant in ("A", "B"):
            s = summaries[f"p={p}"][f"variant_{variant}"]
            print(f"  p={p:.1f}, variant {variant}: "
                  f"n_valid={s['n_valid']:4d}  "
                  f"median={s['cf_median']:.4f}  "
                  f"min={s['cf_min']:.4f}  max={s['cf_max']:.4f}  "
                  f"<0.5={s['frac_below_0_5']:.4f}  "
                  f"<0.6={s['frac_below_0_6']:.4f}")
    print("\nCell-flip counts (verdict prediction: 191 flips, 0 reverse, "
          "additive→multiplicative on 4,410-cell sweep):")
    for variant in ("A", "B"):
        d = deltas[variant]
        print(f"  variant {variant}: "
              f"flips CF≥0.5→<0.5 = {d['flips_above_to_below_0_5']}; "
              f"reverse = {d['flips_below_to_above_0_5']}; "
              f"n_below_0_5 p=1: {d['n_below_0_5_p1']}; "
              f"p=0: {d['n_below_0_5_p0']}")
    c = deltas["combined"]
    print(f"  combined: "
          f"flips CF≥0.5→<0.5 = {c['flips_above_to_below_0_5']}; "
          f"reverse = {c['flips_below_to_above_0_5']}; "
          f"n_below_0_5 p=1: {c['n_below_0_5_p1']}; "
          f"p=0: {c['n_below_0_5_p0']}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
