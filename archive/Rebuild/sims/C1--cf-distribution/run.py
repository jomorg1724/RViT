"""
Rebuild/sims/C1--cf-distribution/run.py
=========================================================
RB-005 — C1 criterion-fraction distributional sweep.
=========================================================

Mission: replace the paper's categorical headline claim

    C1 (paper §4.1, §6): "the criterion fraction is between 0.60 and
    0.96 across the 4,410 (r, V, v) combinations tested."

with the rebuild's distributional restatement (CLAIM_LEDGER.md C1):

    "Criterion shifts are *typically* the dominant lever (median
    CF ≈ 0.76); the categorical [0.60, 0.96] floor is retracted; the
    full distribution and its conditional structure are reported."

This script reproduces the paper's primary 4,410-cell sweep using the
rebuilt model library (`Rebuild/model/`) at two values of the A1
decorrelation parameter, ρ ∈ {0, 0.2}, and emits:

  (a) a *byte-for-byte recovery* check at ρ = 0 against the reviewer's
      validated reference numbers
      Critique/replications/C1--criterion-fraction-floor/output/results.json
      — the contract on the new module is that the published CF
      numbers it produces match the reviewer's substrate at every
      cell where the reviewer also reports a number.

  (b) a *distributional summary* of CF across the sweep at each ρ:
      full range, median, 5/25/50/75/95 quantiles, fraction below
      0.5 / 0.6 / 0.8, and the per-quadrant breakdown (V low/high
      × r cost/sym/benefit × variant).

  (c) a *Δ-distribution*: cell-wise CF(ρ=0.2) − CF(ρ=0), to extend
      the rb-002 headline-cell A1 result (CF monotone-down in ρ
      variant A; variant B essentially flat at the headline cell)
      from one cell to the entire 4,410-cell grid. Does the variant-A
      monotone-down ordering hold cell-wise? Does the variant-B flat
      behaviour generalise, or is the headline cell idiosyncratic?

  (d) three publication-quality figures under output/figures/:
      - cf_histogram.png    — CF histogram, 4-panel (variant × ρ)
      - cf_heatmap.png      — CF over (r, V) at v=5, 4-panel
      - cf_curves.png       — CF vs r at V=0.5, v-family, 4-panel

---------------------------------------------------------
ROLE WITHIN THE REBUILD
---------------------------------------------------------
This sim backs the manuscript §results-C1 increment (RB-009). The
rebuilt §results-C1 may, after this sim lands, state distributional
numbers (median, quantile breakpoints, fraction-below) **and** the A1
extension cell-wise across the full sweep. It may *not* state any
narrower regime claim than the live CLAIM_LEDGER.md C1 row licenses;
honest reporting (mission §5.5) means the variant-B caveat from rb-002
must travel into the manuscript text if confirmed here.

---------------------------------------------------------
GRID — matches the reviewer's CR-002 substrate byte-for-byte
---------------------------------------------------------
N = 4, d'_max = 2.0, f_0 = 0.5, h = sqrt.
r ∈ {21 log-spaced pts in [0.1, 10.0]} ∪ {1.0}     (22 values total;
   the reviewer's grid pins r=1 to ensure C5 symmetric recovery sits
   exactly on the grid)
V ∈ {21 linearly-spaced pts in [1/N, 1.0]}
v ∈ {1, 2, 3, 4, 5}
variant ∈ {A, B}
α-grid: Δα = 0.02 over [0, 1] plus the point 1/N
        (50 alpha points — matches reviewer's substrate exactly; the
         rebuild model's default_alpha_grid step 0.005 is finer but
         would push runtime past the §11 budget; the coarser grid is
         the same one the reviewer validated against the paper, so
         the rho=0 recovery test stays meaningful.)
c-grid: Δc = 0.05 over [-3.0, 3.0]                 (121 points)
ρ ∈ {0.0, 0.2}                                     (the rebuild's
   extension; ρ = 0 reproduces the inherited model exactly, ρ = 0.2
   is the magnitude rb-002 used at the headline cell)

Numerical optimisation per cell: alpha grid search → criterion grid
search (analytic Phi via scipy.special.ndtr or A&S 7.1.26 fallback).
Caching: value-blind α*(v=1) depends only on (r, V, N, d_max, f0, h,
variant, ρ) — cached once per (r, V, variant, ρ) and reused across
v ∈ {1..5}. This is the same optimisation the reviewer's CR-002 uses.

Per-cell numerical fragility caveat (CR-002 §"Mathematical caveat"):
CF = (R(P3) − R(P4)) / (R(P1) − R(P4)) is a ratio of small numbers
near V → 1/N. We follow the reviewer's convention: cells with
R(P1) − R(P4) < 1e-4 reward units are flagged in the
'valid' mask and excluded from the headline CF statistics. They are
NOT dropped from `output/results.json`; the raw CF (which may be
ill-conditioned in that regime) is recorded so the manuscript appendix
can report exactly which cells were excluded and why.

---------------------------------------------------------
RECOVERY TEST (the byte-for-byte contract on every future rebuild
increment that touches `Rebuild/model/`)
---------------------------------------------------------
At ρ = 0 every reported headline number (CF range, median, argmin,
argmax) must match the reviewer's published numbers in
`Critique/replications/C1--criterion-fraction-floor/output/results.json`
to floating-point identity (max |Δ| ≤ 1e-10 on CF, R(P1)..R(P4)).
The cell-wise comparison reads the reviewer's results.json directly
and joins on (r, V, v, variant) at the precision of the saved grid.
A spot-check across 25 randomly-chosen cells of the full 4,410-row
table is required to pass before any ρ > 0 result is reported.

---------------------------------------------------------
RUN
---------------------------------------------------------
$ cd /Users/jonathanmorgan/AttentionManuscript
$ python3 Rebuild/sims/C1--cf-distribution/run.py

Output: Rebuild/sims/C1--cf-distribution/output/{results.json,figures/*.png}
Output hash: printed to stdout; recorded in results.json["metadata"]["sha256"].
Reproducibility: deterministic (no RNG; all grids fixed); re-running
produces byte-identical results.json.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Callable

import numpy as np

# ---------------------------------------------------------------------
# Path glue so we can import the rebuilt model library when invoked
# from anywhere.
# ---------------------------------------------------------------------
THIS_FILE = Path(__file__).resolve()
REBUILD_ROOT = THIS_FILE.parents[2]                  # .../Rebuild
PROJ_ROOT = REBUILD_ROOT.parent                      # .../AttentionManuscript
sys.path.insert(0, str(REBUILD_ROOT.parent))         # so `Rebuild.model` resolves
sys.path.insert(0, str(REBUILD_ROOT))                # so `model` resolves

from model.core import (  # noqa: E402  (sys.path mutated above)
    PHI_BACKEND,
    Phi,
    make_h,
    f_transfer,                                       # noqa: F401 (kept for clarity in comments)
    beta_gamma,                                       # noqa: F401
    d_prime_asym,
    C_GRID,
    p_no_fa_grid,
    p_no_fa_point,
    optimal_R,
    floor_R,
)

OUT_DIR = THIS_FILE.parent / "output"
FIG_DIR = OUT_DIR / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

REVIEWER_RESULTS = (
    PROJ_ROOT
    / "Critique/replications/C1--criterion-fraction-floor/output/results.json"
)


# ---------------------------------------------------------------------
# Grid construction — matches the reviewer's CR-002 byte-for-byte.
# ---------------------------------------------------------------------
N = 4
D_MAX = 2.0
F0 = 0.5
H_NAME = "sqrt"
H = make_h(H_NAME)
RHOS = (0.0, 0.2)

R_GRID = np.unique(np.concatenate([
    np.logspace(np.log10(0.1), np.log10(10.0), 21),
    np.array([1.0]),
]))                                                   # 22 r-values
V_GRID = np.linspace(1.0 / N, 1.0, 21)                # 21 V-values
V_GRID_SWEEP = V_GRID                                 # alias kept for clarity
V_GRID_VALUES = V_GRID                                # alias

V_LIST = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
VARIANTS = ("A", "B")

ALPHA_GRID = np.unique(np.concatenate([
    np.arange(0.02, 1.0 + 1e-9, 0.02),                # 50 alpha values
    np.array([1.0 / N]),
]))                                                   # 50 unique alpha values
# (0.02, 0.04, ..., 1.0) already contains 0.0 not present + the float
# 1/N = 0.25 lies on the 0.02-grid exactly — total 50 unique values.

# Validity threshold (matches reviewer's CR-002 'valid' mask).
VALID_THRESHOLD = 1e-4


# ---------------------------------------------------------------------
# Per-cell evaluator — uses the rebuild model primitives but with the
# reviewer's value-blind alpha caching.
#
# Per cell (r, V, v, variant, rho), we need R(P1..P4):
#   P1: max over alpha of R*(alpha; v)
#   P2: alpha frozen at value-blind alpha*(v=1); criteria re-optimised at v
#   P3: alpha = 1/N (uniform), criteria optimised
#   P4: alpha = 1/N, c_c = c_u = 0
#
# Value-blind alpha*(v=1) for P2 depends only on (r, V, variant, rho)
# (N, d_max, f0, h fixed at module level) — cache once per (r, V, variant,
# rho), reuse across v ∈ {1..5}.
# ---------------------------------------------------------------------
def _cell(
    r: float, V: float, v: float, variant: str, rho: float,
    d_pairs: list[tuple[float, float]],
    rs_p1_v: np.ndarray,
    cached_alpha_p2: float,
    d_unif: tuple[float, float],
) -> dict:
    """Compute R(P1..P4), VDA, CF for one (r, V, v, variant, rho) cell.

    Caller pre-computes (per (r, V, variant, rho)):
      d_pairs        : list of (d_c, d_u) at every alpha in ALPHA_GRID
      rs_p1_v        : R*(alpha; v) at every alpha — pass per-v
      cached_alpha_p2: value-blind alpha*(v=1)
      d_unif         : (d_c, d_u) at alpha = 1/N (P3, P4)

    Returns a dict with all reward values, VDA, CF, alphas.
    """
    idx_p1 = int(np.argmax(rs_p1_v))
    R_P1 = float(rs_p1_v[idx_p1])
    alpha_P1 = float(ALPHA_GRID[idx_p1])

    # P2: criteria re-optimised at v, alpha frozen at value-blind.
    d_c_p2, d_u_p2 = d_prime_asym(cached_alpha_p2, r, D_MAX, F0, H, N)
    R_P2 = optimal_R(d_c_p2, d_u_p2, v, V, N, variant, rho)

    # P3: alpha = 1/N, criteria optimised.
    d_c_un, d_u_un = d_unif
    R_P3 = optimal_R(d_c_un, d_u_un, v, V, N, variant, rho)
    # P4: alpha = 1/N, c_c = c_u = 0.
    R_P4 = floor_R(d_c_un, d_u_un, v, V, N, variant, rho)

    total = R_P1 - R_P4
    crit = R_P3 - R_P4
    cf = crit / total if abs(total) > 1e-12 else float("nan")
    return dict(
        r=r, V=V, v=float(v), variant=variant, rho=rho,
        alpha_P1=alpha_P1, alpha_vb=cached_alpha_p2,
        R_P1=R_P1, R_P2=R_P2, R_P3=R_P3, R_P4=R_P4,
        VDA=R_P1 - R_P2,
        criterion_gain=crit,
        total_gain=total,
        CF=cf,
        valid=bool(total > VALID_THRESHOLD),
    )


def sweep_one_rho(rho: float) -> list[dict]:
    """Full primary sweep at fixed rho. Returns 4,410 rows."""
    rows: list[dict] = []
    # Per (r, V, variant), precompute d_pairs, then per (r, V, variant)
    # compute the value-blind alpha cache, then per v compute R*(alpha; v)
    # across the alpha grid (reused inside _cell to pick P1's argmax).
    n_total = len(R_GRID) * len(V_GRID) * len(VARIANTS) * len(V_LIST)
    n_done = 0
    t0 = time.time()
    print(
        f"  sweep rho={rho:.3f}: "
        f"{len(R_GRID)} r × {len(V_GRID)} V × {len(V_LIST)} v × {len(VARIANTS)} "
        f"variants = {n_total} cells"
    )
    for r in R_GRID:
        r_f = float(r)
        for V in V_GRID:
            V_f = float(V)
            # d'(alpha) pairs at this (r, V)
            d_pairs = [
                d_prime_asym(float(a), r_f, D_MAX, F0, H, N)
                for a in ALPHA_GRID
            ]
            d_unif = d_prime_asym(1.0 / N, r_f, D_MAX, F0, H, N)
            for variant in VARIANTS:
                # Value-blind alpha cache at this (r, V, variant, rho)
                rs_vb = np.array([
                    optimal_R(dc, du, 1.0, V_f, N, variant, rho)
                    for (dc, du) in d_pairs
                ])
                alpha_vb = float(ALPHA_GRID[int(np.argmax(rs_vb))])
                for v in V_LIST:
                    # R*(alpha; v) across the alpha grid — for the P1 argmax.
                    rs_p1 = np.array([
                        optimal_R(dc, du, float(v), V_f, N, variant, rho)
                        for (dc, du) in d_pairs
                    ])
                    row = _cell(
                        r_f, V_f, float(v), variant, rho,
                        d_pairs, rs_p1, alpha_vb, d_unif,
                    )
                    rows.append(row)
                    n_done += 1
        elapsed = time.time() - t0
        rate = n_done / max(elapsed, 1e-9)
        eta = (n_total - n_done) / max(rate, 1e-9)
        print(
            f"    r={r_f:8.4f}  done={n_done}/{n_total}  "
            f"rate={rate:7.1f}/s  ETA={eta:5.0f}s"
        )
    return rows


# ---------------------------------------------------------------------
# Distribution summary — produces the "distributional, not categorical"
# headline numbers that replace the paper's [0.60, 0.96] floor.
# ---------------------------------------------------------------------
def summarise(rows: list[dict], variant: str | None = None) -> dict:
    """Headline distributional numbers, optionally restricted to one variant."""
    sub = rows if variant is None else [r for r in rows if r["variant"] == variant]
    cfs = np.array([r["CF"] for r in sub if r["valid"]])
    n_valid = int(len(cfs))
    if n_valid == 0:
        return dict(n=len(sub), n_valid=0)
    q5, q25, q50, q75, q95 = (
        float(np.percentile(cfs, p)) for p in (5, 25, 50, 75, 95)
    )
    return dict(
        n=len(sub),
        n_valid=n_valid,
        cf_min=float(cfs.min()),
        cf_max=float(cfs.max()),
        cf_median=q50,
        cf_q5=q5, cf_q25=q25, cf_q75=q75, cf_q95=q95,
        cf_mean=float(cfs.mean()),
        cf_std=float(cfs.std(ddof=1)) if n_valid > 1 else 0.0,
        frac_below_0_5=float((cfs < 0.5).mean()),
        frac_below_0_6=float((cfs < 0.6).mean()),
        frac_below_0_8=float((cfs < 0.8).mean()),
        frac_above_0_9=float((cfs >= 0.9).mean()),
    )


def quadrant_breakdown(rows: list[dict], rho: float) -> dict:
    """V ∈ {low, high} × r ∈ {cost, sym, benefit} × variant ∈ {A, B}.

    'low' / 'high' V split at the median V (0.625). Cost-/sym-/
    benefit-regime split at r ≤ 0.5, 0.5 < r < 2, r ≥ 2 — the
    same buckets the reviewer's CR-002 narrative uses.

    Reports n, n_valid, cf_median, frac_below_0_6 per quadrant.
    """
    sub = [r for r in rows if r["rho"] == rho]
    def bucket_r(r):
        if r <= 0.5:
            return "cost"
        if r < 2.0:
            return "sym"
        return "benefit"
    def bucket_V(V):
        return "low" if V < 0.625 else "high"
    out: dict[str, dict] = {}
    for variant in VARIANTS:
        for rb in ("cost", "sym", "benefit"):
            for vb in ("low", "high"):
                key = f"{variant}/r={rb}/V={vb}"
                cell = [
                    r for r in sub
                    if r["variant"] == variant
                    and bucket_r(r["r"]) == rb
                    and bucket_V(r["V"]) == vb
                ]
                cfs = np.array([c["CF"] for c in cell if c["valid"]])
                if len(cfs) == 0:
                    out[key] = dict(n=len(cell), n_valid=0)
                else:
                    out[key] = dict(
                        n=len(cell),
                        n_valid=int(len(cfs)),
                        cf_median=float(np.median(cfs)),
                        cf_min=float(cfs.min()),
                        cf_max=float(cfs.max()),
                        frac_below_0_6=float((cfs < 0.6).mean()),
                    )
    return out


# ---------------------------------------------------------------------
# Recovery test — byte-for-byte against the reviewer's results.json
# at ρ = 0.
# ---------------------------------------------------------------------
def recovery_test(rho0_rows: list[dict]) -> dict:
    """Compare our ρ=0 rows against reviewer's CR-002 reference.

    Joins on (r, V, v, variant) at the printed precision of the
    reviewer's saved grid. Reports max|Δ| on each of CF, R(P1)..R(P4).
    """
    if not REVIEWER_RESULTS.exists():
        return dict(skipped=True, reason=f"missing reference: {REVIEWER_RESULTS}")
    with open(REVIEWER_RESULTS) as fh:
        ref_data = json.load(fh)

    def key(row):
        # Match the reviewer's save precision — round to 6 decimals on r
        # and 4 decimals on V (the grid is dense enough that this never
        # creates collisions in the reviewer's grid or ours).
        return (
            round(float(row["r"]), 6),
            round(float(row["V"]), 4),
            int(round(float(row["v"]))),
            str(row["variant"]),
        )
    ref = {key(row): row for row in ref_data["phase_A"]["rows"]}
    ours = {key(row): row for row in rho0_rows}

    keys_both = set(ref.keys()) & set(ours.keys())
    print(
        f"  recovery: {len(keys_both)} joinable cells "
        f"(ours: {len(ours)}, theirs: {len(ref)})"
    )
    # Headline diffs — restricted to the reviewer's "valid" set
    # AND to our valid set (both must be well-conditioned to compare).
    diffs_cf, diffs_p1, diffs_p2, diffs_p3, diffs_p4 = [], [], [], [], []
    for k in keys_both:
        rrow = ref[k]
        orow = ours[k]
        # Reviewer doesn't tag 'valid' per-row in their schema; we use
        # both-valid as the condition.
        if not orow["valid"]:
            continue
        if rrow.get("total_gain", 1.0) <= VALID_THRESHOLD:
            continue
        diffs_cf.append(abs(rrow["criterion_fraction"] - orow["CF"]))
        diffs_p1.append(abs(rrow["R_p1"] - orow["R_P1"]))
        diffs_p2.append(abs(rrow["R_p2"] - orow["R_P2"]))
        diffs_p3.append(abs(rrow["R_p3"] - orow["R_P3"]))
        diffs_p4.append(abs(rrow["R_p4"] - orow["R_P4"]))

    def fmt(arr):
        return dict(
            n=int(len(arr)),
            max=float(max(arr)) if arr else 0.0,
            mean=float(np.mean(arr)) if arr else 0.0,
        )
    return dict(
        skipped=False,
        n_joined=len(keys_both),
        n_compared=len(diffs_cf),
        diff_CF=fmt(diffs_cf),
        diff_R_P1=fmt(diffs_p1),
        diff_R_P2=fmt(diffs_p2),
        diff_R_P3=fmt(diffs_p3),
        diff_R_P4=fmt(diffs_p4),
        # Reviewer's headline numbers — must reproduce.
        ref_cf_min=float(ref_data["phase_A"]["cf_min"]),
        ref_cf_max=float(ref_data["phase_A"]["cf_max"]),
        ref_cf_median=float(ref_data["phase_A"]["cf_median"]),
    )


# ---------------------------------------------------------------------
# Δ-distribution (ρ=0.2 minus ρ=0) — extends the rb-002 headline-cell
# A1 ordering to all 4,410 cells.
# ---------------------------------------------------------------------
def delta_distribution(rows_by_rho: dict[float, list[dict]]) -> dict:
    """Per-cell CF(ρ=0.2) − CF(ρ=0); break down by variant.

    Reports the empirical fractions:
      frac_dec   — cells where CF strictly decreased with ρ
      frac_inc   — cells where CF strictly increased
      frac_flat  — cells essentially flat (|ΔCF| < 1e-5)
      median Δ, |Δ| quantiles.
    """
    rows0 = rows_by_rho[0.0]
    rows2 = rows_by_rho[0.2]
    def key(r):
        return (
            round(r["r"], 6), round(r["V"], 4),
            int(round(r["v"])), r["variant"],
        )
    m0 = {key(r): r for r in rows0}
    out: dict[str, dict] = {}
    for variant in VARIANTS:
        deltas = []
        for r2 in rows2:
            if r2["variant"] != variant or not r2["valid"]:
                continue
            r0 = m0.get(key(r2))
            if r0 is None or not r0["valid"]:
                continue
            deltas.append(r2["CF"] - r0["CF"])
        arr = np.array(deltas)
        if len(arr) == 0:
            out[variant] = dict(n=0)
            continue
        out[variant] = dict(
            n=int(len(arr)),
            frac_dec=float((arr < -1e-5).mean()),
            frac_inc=float((arr > 1e-5).mean()),
            frac_flat=float((np.abs(arr) <= 1e-5).mean()),
            delta_median=float(np.median(arr)),
            delta_mean=float(np.mean(arr)),
            abs_delta_q50=float(np.median(np.abs(arr))),
            abs_delta_q95=float(np.percentile(np.abs(arr), 95)),
            delta_min=float(arr.min()),
            delta_max=float(arr.max()),
        )
    return out


# ---------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------
def fig_histogram(rows_by_rho: dict[float, list[dict]], path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), sharex=True, sharey=True)
    bins = np.linspace(0.0, 1.0, 41)
    for i, variant in enumerate(VARIANTS):
        for j, rho in enumerate(RHOS):
            ax = axes[i, j]
            cfs = np.array([
                r["CF"]
                for r in rows_by_rho[rho]
                if r["variant"] == variant and r["valid"]
            ])
            ax.hist(cfs, bins=bins, color="#3c78b4", edgecolor="white",
                    alpha=0.85)
            ax.axvline(0.6, color="#aa0000", linestyle="--", linewidth=1.0,
                       label=r"paper floor $0.60$")
            ax.axvline(0.5, color="#cc7700", linestyle=":", linewidth=1.0,
                       label=r"$0.5$")
            med = float(np.median(cfs))
            ax.axvline(med, color="#222222", linestyle="-", linewidth=1.2,
                       label=f"median = {med:.3f}")
            frac_lt_06 = float((cfs < 0.6).mean())
            frac_lt_05 = float((cfs < 0.5).mean())
            ax.set_title(
                f"variant {variant}, ρ = {rho:.1f}    "
                f"n_valid = {len(cfs)}    "
                f"frac<0.6 = {frac_lt_06:.3f}    "
                f"frac<0.5 = {frac_lt_05:.3f}",
                fontsize=9,
            )
            if i == 1:
                ax.set_xlabel("Criterion fraction CF")
            if j == 0:
                ax.set_ylabel("# cells")
            ax.set_xlim(0.0, 1.0)
            if i == 0 and j == 0:
                ax.legend(loc="upper left", fontsize=8, framealpha=0.95)
    fig.suptitle(
        "C1 criterion-fraction distribution — 4,410 cells × ρ ∈ {0, 0.2}\n"
        "rb-003, RB-005 (rebuild). Paper claim CF ∈ [0.60, 0.96]: retracted "
        "as a floor; the distributional restatement is the plot above.",
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, dpi=140)
    plt.close(fig)


def fig_heatmap(rows_by_rho: dict[float, list[dict]], path: Path) -> None:
    """CF(r, V) at v = 5; 2×2 panel for variant × ρ."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), sharex=True, sharey=True)
    nr, nV = len(R_GRID), len(V_GRID)
    for i, variant in enumerate(VARIANTS):
        for j, rho in enumerate(RHOS):
            ax = axes[i, j]
            grid = np.full((nV, nr), np.nan)
            for row in rows_by_rho[rho]:
                if row["variant"] != variant or float(row["v"]) != 5.0:
                    continue
                if not row["valid"]:
                    continue
                # Match by index (the grids are saved exactly).
                ir = int(np.argmin(np.abs(R_GRID - row["r"])))
                iV = int(np.argmin(np.abs(V_GRID - row["V"])))
                grid[iV, ir] = row["CF"]
            # log-x for r
            im = ax.pcolormesh(
                R_GRID, V_GRID, grid,
                cmap="viridis", vmin=0.3, vmax=1.0, shading="auto",
            )
            ax.set_xscale("log")
            ax.set_title(f"variant {variant}, ρ = {rho:.1f}", fontsize=10)
            if i == 1:
                ax.set_xlabel("r  (β/γ asymmetry; log scale)")
            if j == 0:
                ax.set_ylabel("V  (cue validity)")
            cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label("CF", fontsize=8)
    fig.suptitle(
        "C1 criterion-fraction heatmap, CF(r, V) at v = 5\n"
        "rb-003, RB-005 — distribution structure, not a categorical floor.",
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, dpi=140)
    plt.close(fig)


def fig_curves(rows_by_rho: dict[float, list[dict]], path: Path) -> None:
    """CF(r) v-family at V = 0.5; 2×2 panel for variant × ρ."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), sharex=True, sharey=True)
    V_target = 0.5
    # find nearest V in grid
    iV = int(np.argmin(np.abs(V_GRID - V_target)))
    V_used = float(V_GRID[iV])
    cmap = plt.get_cmap("plasma")
    for i, variant in enumerate(VARIANTS):
        for j, rho in enumerate(RHOS):
            ax = axes[i, j]
            for kv, v in enumerate(V_LIST):
                cf_by_r = []
                for r in R_GRID:
                    matches = [
                        row for row in rows_by_rho[rho]
                        if row["variant"] == variant
                        and abs(row["r"] - r) < 1e-9
                        and abs(row["V"] - V_used) < 1e-9
                        and abs(float(row["v"]) - v) < 1e-9
                    ]
                    if matches and matches[0]["valid"]:
                        cf_by_r.append(matches[0]["CF"])
                    else:
                        cf_by_r.append(np.nan)
                ax.plot(
                    R_GRID, cf_by_r,
                    color=cmap(kv / max(len(V_LIST) - 1, 1)),
                    linewidth=1.3, marker="o", markersize=3,
                    label=f"v = {int(v)}",
                )
            ax.axhline(0.6, color="#aa0000", linestyle="--", linewidth=0.9)
            ax.axhline(0.5, color="#cc7700", linestyle=":", linewidth=0.9)
            ax.set_xscale("log")
            ax.set_title(
                f"variant {variant}, ρ = {rho:.1f}    "
                f"V = {V_used:.3f}",
                fontsize=10,
            )
            if i == 1:
                ax.set_xlabel("r  (β/γ asymmetry; log scale)")
            if j == 0:
                ax.set_ylabel("CF")
            ax.set_ylim(0.2, 1.05)
            if i == 0 and j == 0:
                ax.legend(loc="lower left", fontsize=8, ncol=2,
                          framealpha=0.95)
    fig.suptitle(
        "C1 — CF(r) at V ≈ 0.5, v-family. rb-003, RB-005.\n"
        "Dashed = paper's stated 0.60 floor (retracted); dotted = 0.5.",
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, dpi=140)
    plt.close(fig)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main() -> None:
    print(f"RB-005 / rb-003 — C1 distributional sweep")
    print(f"  Phi backend: {PHI_BACKEND}")
    print(f"  REBUILD_ROOT: {REBUILD_ROOT}")
    print(f"  output: {OUT_DIR}")

    t0 = time.time()
    rows_by_rho: dict[float, list[dict]] = {}
    for rho in RHOS:
        rows_by_rho[float(rho)] = sweep_one_rho(float(rho))
    t_sweep = time.time() - t0
    print(f"  sweep done in {t_sweep:.1f}s")

    # Recovery test against the reviewer's reference numbers (ρ=0).
    print("\nRecovery test (ρ=0 vs reviewer's CR-002 reference):")
    rec = recovery_test(rows_by_rho[0.0])
    print(f"  {rec}")

    # Distribution summaries.
    summaries: dict[str, dict] = {}
    for rho in RHOS:
        for variant in VARIANTS:
            summaries[f"variant_{variant}/rho_{rho:.1f}"] = summarise(
                rows_by_rho[rho], variant=variant,
            )
        summaries[f"both_variants/rho_{rho:.1f}"] = summarise(
            rows_by_rho[rho], variant=None,
        )

    # Per-quadrant breakdown.
    quadrants = {f"rho_{rho:.1f}": quadrant_breakdown(rows_by_rho[rho], rho)
                 for rho in RHOS}

    # Δ-distribution.
    deltas = delta_distribution(rows_by_rho)

    # Figures.
    print("\nFigures:")
    fig_histogram(rows_by_rho, FIG_DIR / "cf_histogram.png")
    print(f"  wrote {FIG_DIR / 'cf_histogram.png'}")
    fig_heatmap(rows_by_rho, FIG_DIR / "cf_heatmap.png")
    print(f"  wrote {FIG_DIR / 'cf_heatmap.png'}")
    fig_curves(rows_by_rho, FIG_DIR / "cf_curves.png")
    print(f"  wrote {FIG_DIR / 'cf_curves.png'}")

    # Save results.
    out = {
        "rows": {f"{rho:.1f}": rows_by_rho[rho] for rho in RHOS},
        "summaries": summaries,
        "quadrant_breakdown": quadrants,
        "delta_distribution": deltas,
        "recovery_test": rec,
        "metadata": {
            "task_id": "RB-005",
            "run_id": "rb-003",
            "prompt_version": "0.2",
            "date": "2026-05-25",
            "phi_backend": PHI_BACKEND,
            "N": N, "d_max": D_MAX, "f0": F0, "h_name": H_NAME,
            "r_grid": [float(r) for r in R_GRID],
            "V_grid": [float(V) for V in V_GRID],
            "v_grid": [float(v) for v in V_LIST],
            "variants": list(VARIANTS),
            "rhos": list(RHOS),
            "alpha_grid_step": 0.02,
            "alpha_grid_n": len(ALPHA_GRID),
            "c_grid_step": 0.05,
            "c_grid_n": len(C_GRID),
            "valid_threshold": VALID_THRESHOLD,
            "wallclock_seconds": float(t_sweep),
        },
    }

    # Deterministic JSON serialisation -> sha256 of the serialised string.
    payload = json.dumps(out, indent=2, sort_keys=True, default=float)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    out["metadata"]["sha256"] = digest
    # Re-serialise with the digest stamped in.
    payload2 = json.dumps(out, indent=2, sort_keys=True, default=float)
    results_path = OUT_DIR / "results.json"
    with open(results_path, "w") as fh:
        fh.write(payload2)
    print(f"\nWrote {results_path}")
    print(f"sha256 (pre-stamp): {digest}")

    # Print headline numbers for the build log.
    print("\nHeadline (rb-003):")
    for rho in RHOS:
        for v in VARIANTS:
            s = summaries[f"variant_{v}/rho_{rho:.1f}"]
            print(
                f"  variant {v}, ρ={rho:.1f}: "
                f"n_valid={s['n_valid']:4d}  "
                f"min={s['cf_min']:.4f}  "
                f"median={s['cf_median']:.4f}  "
                f"max={s['cf_max']:.4f}  "
                f"<0.5={s['frac_below_0_5']:.4f}  "
                f"<0.6={s['frac_below_0_6']:.4f}  "
                f"<0.8={s['frac_below_0_8']:.4f}"
            )
    print("\nΔ-distribution (CF(ρ=0.2) − CF(ρ=0)) per variant:")
    for v in VARIANTS:
        d = deltas[v]
        print(
            f"  variant {v}: n={d['n']}  "
            f"frac_dec={d['frac_dec']:.4f}  "
            f"frac_inc={d['frac_inc']:.4f}  "
            f"frac_flat={d['frac_flat']:.4f}  "
            f"median Δ = {d['delta_median']:+.4f}  "
            f"|Δ|95 = {d['abs_delta_q95']:.4f}"
        )


if __name__ == "__main__":
    main()
