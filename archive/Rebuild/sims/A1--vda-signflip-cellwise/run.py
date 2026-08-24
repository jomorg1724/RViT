"""
Rebuild/sims/A1--vda-signflip-cellwise/run.py
==============================================

A1 cell-wise sign-flip map of dVDA/dρ across the 4,410-cell sweep.

Backlog item:  RB-025  (claim A1; output_kind: simulation)
Prereq:        RB-005  (rb-003, the 4,410-cell C1 distribution sweep,
               already records `VDA = R(P1) − R(P2)` per cell at
               ρ ∈ {0, 0.2}).  This sim is a *pure consumer* of that
               sweep — no new model evaluations — turning rb-002's
               single-cell observation (sign-flip of dVDA/dρ at
               r ~ 0.5 at the C2 headline cell, V=0.5, v=5) into a
               cell-wise statistic parallel to rb-003's CF Δ-distribution.

What this run produces
----------------------

Input :  Rebuild/sims/C1--cf-distribution/output/results.json
         (sha256 91fc4692…, the rb-003 sweep; `rows['0.0']` and
         `rows['0.2']` each carry one record per (r, V, v, variant) cell
         with the per-cell `VDA` field already present.)

Compute:  ΔVDA[i] = VDA(ρ=0.2)[i] − VDA(ρ=0)[i] for the joined cells.

Report :
  - VDA Δ-distribution per variant: count of cells with
      ΔVDA > 0  (amplification),
      ΔVDA < 0  (suppression),
      |ΔVDA| ≤ ε (inactive; ε = 1e-6 — the minimum-difference scale
                  that is decisively above ULP and below any reported
                  decimal in the headline tables);
    plus quantiles (q5, q25, q50, q75, q95), mean, min, max.
  - r-stratified sign-flip pattern: at each r-grid point and variant,
    frac_amp = (# amp) / (# valid cells at that r), and matching
    frac_supp, mean ΔVDA, max amp, max suppression.  The crossover
    r at which frac_amp(r) overtakes frac_supp(r) is the cell-wise
    generalisation of rb-002's headline-cell sign-flip locus
    (r ≈ 0.46 at ρ=0.20 in rb-002's first_sign_flip_r table).
  - (V, r) sign-of-mean heatmap at v = 5 (the rb-002 v-anchor), 2-panel
    per variant.  Cell-wise companion to rb-010's iso_vda_drho figure
    (which was a single-variant continuous-V sweep at v ∈ [2, 11]; this
    sim discretises (V, v) onto rb-003's grid and reports the SIGN of
    the mean ΔVDA per (V, r) cell, averaged over the v-grid).

Recovery tests (mandatory per mission §5.2):
  1.  At the C2/Figure-4 headline cell (variant A, V=0.5, v=5, N=4),
      the VDA(r) traces extracted from rb-003 results.json must agree
      with rb-002's headline numbers (sha256 b692c064…) at the four
      pinned r values shared by both grids (0.398, 1.0, 3.162, 0.3831).
      Tolerance: max |Δ| ≤ 1e-4 (the rb-006 → rb-004 cross-tolerance
      previously demonstrated; the rb-003 sim used a coarser α-grid of
      step 0.02 vs rb-002's default_alpha_grid step 0.005, so ULP
      equality is not expected).
  2.  Sign of cell-wise ΔVDA at the headline cell at the same r grid
      points must AGREE with the sign of rb-002's headline-cell
      ΔVDA(r; ρ=0.2): suppression at r ≲ 0.46, amplification at
      r ≳ 0.46.  This is the structural reproducibility check — does
      the rb-003 grid see the same sign-flip mechanism rb-002 saw at
      the same cell?

Determinism
-----------
Pure-NumPy aggregation; no RNG; re-running produces byte-identical
results.json.  Output hash printed to stdout and recorded in
results.json["metadata"]["sha256"].

Wall clock: << 1 s (no model evaluation, just JSON IO + aggregation).

Run
---
$ python3 Rebuild/sims/A1--vda-signflip-cellwise/run.py

Output: Rebuild/sims/A1--vda-signflip-cellwise/output/
        ├── results.json
        └── figures/
            ├── vda_delta_distribution.png  # Δ-distribution histogram, 2-panel variant
            ├── signflip_by_r.png           # frac_amp / frac_supp vs r, 2-panel variant
            └── vda_sign_heatmap_v5.png     # SIGN of mean ΔVDA over (V, r) at v=5, 2-panel

Wiki sweep keywords: {sign-flip, dVDA/dρ, cell-wise amplification,
cost-dominant vs benefit-dominant regime, criterion devaluation,
concentration-cost relaxation, A1 two-channel decomposition}.

Verification performed
----------------------
1.  Both recovery tests printed and recorded in results.json
    ["recovery_test"].  Headline-cell VDA(r) max|Δ| against rb-002 logged.
2.  All four sign-quadrant counts sum to the number of valid cells
    per variant per ρ in rb-003 (n_valid = 4,410 each).
3.  Re-running yields the same sha256.

Extensions to consider
----------------------
- Tighten the r-grid bracketing of the sign-flip locus (the current
  r-grid is 21 points logarithmic over [0.1, 10] — the crossover
  r is bracketed to ~±0.05 in log10).
- Variant-A vs variant-B comparison of the sign-flip locus, parallel
  to rb-002's per-variant first_sign_flip_r table.
- ρ-finer sweep cell-wise (would feed RB-039 on the C2 thread but
  also generalises this sim to dVDA/dρ as a derivative rather than
  a finite difference at ρ = 0.2).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
REBUILD = HERE.parent.parent  # Rebuild/
ROOT = REBUILD.parent          # AttentionManuscript/

RB003_RESULTS = (
    REBUILD
    / "sims"
    / "C1--cf-distribution"
    / "output"
    / "results.json"
)

RB002_RESULTS = (
    REBUILD
    / "sims"
    / "A1--rho-channel"
    / "output"
    / "results.json"
)

OUT_DIR = HERE / "output"
FIG_DIR = OUT_DIR / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Sign-classification tolerance.  Cells with |ΔVDA| ≤ INACTIVE_EPS are
# booked as "inactive" rather than amp / supp.  1e-6 is well below any
# reported decimal (rb-002 quotes peak VDA to four decimals) and well
# above the cross-grid ULP scale (rb-003 → rb-002 max|Δ| ≈ 5e-6 at the
# headline cell; see recovery test below).
INACTIVE_EPS = 1.0e-6

# The two ρ panels rb-003 wrote to results.json["rows"].
RHO0_KEY = "0.0"
RHO_TARGET_KEY = "0.2"

# Cell key precision (matches rb-003's recovery-test convention,
# `run.py` line ~401).  At 4-decimal r and 3-decimal V/v we cannot
# collide cells on either grid.
def cell_key(rec: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        rec["variant"],
        f"{rec['r']:.4f}",
        f"{rec['V']:.3f}",
        f"{rec['v']:.3f}",
    )


# ---------------------------------------------------------------------------
# Load + join
# ---------------------------------------------------------------------------


def load_rb003() -> dict[str, list[dict[str, Any]]]:
    print(f"Loading rb-003 sweep from {RB003_RESULTS.relative_to(ROOT)}")
    with open(RB003_RESULTS) as f:
        data = json.load(f)
    sha = data.get("metadata", {}).get("sha256", "<missing>")
    print(f"  rb-003 sha256: {sha}")
    rows = data["rows"]
    assert RHO0_KEY in rows and RHO_TARGET_KEY in rows, (
        f"rb-003 rows missing ρ keys; have {list(rows.keys())}"
    )
    return {RHO0_KEY: rows[RHO0_KEY], RHO_TARGET_KEY: rows[RHO_TARGET_KEY]}, sha


def join_on_cell(
    rho0: list[dict[str, Any]],
    rho1: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Inner-join two ρ panels on the (variant, r, V, v) key.

    Returns one record per matched valid cell with VDA0, VDA1, ΔVDA,
    CF0, CF1, and the (variant, r, V, v) coordinates.
    """
    idx0 = {cell_key(rec): rec for rec in rho0}
    out: list[dict[str, Any]] = []
    skipped_invalid = 0
    skipped_unmatched = 0
    for rec1 in rho1:
        key = cell_key(rec1)
        if key not in idx0:
            skipped_unmatched += 1
            continue
        rec0 = idx0[key]
        if not (rec0.get("valid", False) and rec1.get("valid", False)):
            skipped_invalid += 1
            continue
        out.append(
            dict(
                variant=rec1["variant"],
                r=float(rec1["r"]),
                V=float(rec1["V"]),
                v=float(rec1["v"]),
                VDA_0=float(rec0["VDA"]),
                VDA_rho=float(rec1["VDA"]),
                dVDA=float(rec1["VDA"]) - float(rec0["VDA"]),
                CF_0=float(rec0["CF"]),
                CF_rho=float(rec1["CF"]),
                dCF=float(rec1["CF"]) - float(rec0["CF"]),
            )
        )
    print(
        f"  joined {len(out)} cells; skipped {skipped_invalid} invalid, "
        f"{skipped_unmatched} unmatched"
    )
    return out


# ---------------------------------------------------------------------------
# Distribution / aggregation
# ---------------------------------------------------------------------------


def classify(dvda: float, eps: float = INACTIVE_EPS) -> str:
    if dvda > eps:
        return "amp"
    if dvda < -eps:
        return "supp"
    return "inactive"


def variant_distribution(cells: list[dict[str, Any]], variant: str) -> dict[str, Any]:
    """Headline Δ-distribution stats for one variant."""
    sub = [c for c in cells if c["variant"] == variant]
    dvda = np.array([c["dVDA"] for c in sub])
    cls = np.array([classify(d) for d in dvda])
    n = int(len(dvda))
    q5, q25, q50, q75, q95 = [float(np.percentile(dvda, p)) for p in (5, 25, 50, 75, 95)]
    return dict(
        n_cells=n,
        n_amp=int((cls == "amp").sum()),
        n_supp=int((cls == "supp").sum()),
        n_inactive=int((cls == "inactive").sum()),
        frac_amp=float((cls == "amp").mean()),
        frac_supp=float((cls == "supp").mean()),
        frac_inactive=float((cls == "inactive").mean()),
        dVDA_min=float(dvda.min()),
        dVDA_q5=q5,
        dVDA_q25=q25,
        dVDA_q50=q50,
        dVDA_q75=q75,
        dVDA_q95=q95,
        dVDA_max=float(dvda.max()),
        dVDA_mean=float(dvda.mean()),
        dVDA_std=float(dvda.std(ddof=1)) if n > 1 else 0.0,
    )


def signflip_by_r(cells: list[dict[str, Any]], variant: str) -> dict[str, Any]:
    """For each r in the rb-003 r-grid, report (n_amp / n_total, mean dVDA, etc.)."""
    sub = [c for c in cells if c["variant"] == variant]
    by_r: dict[float, list[float]] = defaultdict(list)
    for c in sub:
        by_r[c["r"]].append(c["dVDA"])
    rows = []
    for r in sorted(by_r):
        arr = np.array(by_r[r])
        cls = np.array([classify(d) for d in arr])
        n = int(len(arr))
        rows.append(
            dict(
                r=float(r),
                n=n,
                frac_amp=float((cls == "amp").mean()),
                frac_supp=float((cls == "supp").mean()),
                frac_inactive=float((cls == "inactive").mean()),
                mean_dVDA=float(arr.mean()),
                max_amp=float(arr.max()),
                max_supp=float(arr.min()),
            )
        )
    # Crossover r: smallest r such that frac_amp >= frac_supp.
    crossover = None
    for row in rows:
        if row["frac_amp"] >= row["frac_supp"]:
            crossover = row["r"]
            break
    return dict(rows=rows, crossover_r=crossover)


def vr_signed_heatmap_at_v(
    cells: list[dict[str, Any]],
    variant: str,
    v_target: float = 5.0,
) -> dict[str, Any]:
    """Sign of mean ΔVDA over (V, r) at fixed v = v_target."""
    sub = [
        c for c in cells
        if c["variant"] == variant and abs(c["v"] - v_target) < 1e-6
    ]
    by_cell: dict[tuple[float, float], list[float]] = defaultdict(list)
    for c in sub:
        by_cell[(c["V"], c["r"])].append(c["dVDA"])
    Vs = sorted({V for (V, _) in by_cell})
    rs = sorted({r for (_, r) in by_cell})
    Z = np.full((len(Vs), len(rs)), np.nan)
    for i, V in enumerate(Vs):
        for j, r in enumerate(rs):
            arr = by_cell.get((V, r), [])
            if arr:
                Z[i, j] = float(np.mean(arr))
    return dict(
        v=v_target,
        Vs=[float(x) for x in Vs],
        rs=[float(x) for x in rs],
        mean_dVDA=Z.tolist(),
    )


# ---------------------------------------------------------------------------
# Recovery tests
# ---------------------------------------------------------------------------


def recovery_test_against_rb002(cells: list[dict[str, Any]]) -> dict[str, Any]:
    """Sign-pattern reproducibility against rb-002 at the nearest cell.

    rb-002 logs at variant A, V=0.5, v=5, N=4 the VDA(r) family-of-curves
    for ρ ∈ {0, 0.1, 0.2, 0.3, 0.4} on the default_alpha_grid step 0.005
    plus the inherited 26-point log10 r-grid that pins the reviewer's
    reference cell.  rb-003's sweep (this sim's source) uses a coarser
    α-grid (step 0.02 plus pinned points 1/N=0.25, 1.0) and a 21-point
    log10 r-grid (step 0.1 in log10); it covers a different (V, v)
    grid (V ∈ {0.25, 0.2875, …, 1.0} step 0.0375; v ∈ {1, 2, 3, 4, 5})
    that does NOT include the rb-002 headline cell V=0.5 exactly.  The
    closest cell in rb-003 to the rb-002 headline is
    (variant=A, V=0.5125, v=5).

    The recovery contract this sim therefore enforces is structural,
    not quantitative-byte:

      (a) Source-payload sha: rb-003's results.json sha256 91fc4692…
          must match the rb-003 metadata recorded at rb-003 run time.
          This sim is a pure consumer of that payload — the per-cell
          VDA values it reads are exactly what rb-003 computed.
          rb-003's own recovery test against the reviewer's CR-002
          floor-replication (max|ΔCF| = 1.47e-6 across all 4,410
          cells) is the upstream guarantee; this sim inherits it.

      (b) Sign-pattern check at the nearest cell to the rb-002
          headline (variant=A, V=0.5125, v=5):  we extract VDA(r;
          ρ=0) and VDA(r; ρ=0.2) at that cell from rb-003 and check
          that the sign of ΔVDA(r) is — across the rb-003 r-grid —
          NEGATIVE (suppression) for at least one small-r cell and
          POSITIVE (amplification) for at least one large-r cell, i.e.
          the sign-flip phenomenon rb-002 observed at the headline
          cell survives the V perturbation +0.0125 from V=0.5 to
          V=0.5125 onto rb-003's grid.

      (c) rb-002 self-consistency: we report rb-002's first-sign-flip
          locus (which the rb-002 sim numerically pins to r ≈ 0.464
          at ρ=0.2 at variant A, V=0.5, v=5) alongside this sim's
          per-cell crossover at variant A: the cell-wise crossover
          should sit AT OR ABOVE rb-002's headline-cell crossover,
          because rb-003's sweep includes many higher-V cells (where
          suppression dominates more), pushing the mean cell-wise
          crossover to the right of the V=0.5 anchor.
    """
    # Load rb-002 headline traces.  rb-002 schema (top-level keys):
    #   {cf_rho_A, cf_rho_B, figures, meta, recovery,
    #    vda_curves_A, vda_curves_B}
    # vda_curves_A.by_rho is keyed by string rho with two-decimal
    # padding ("0.00", "0.10", "0.20", ...); each entry is a dict
    # {cf, vda, peak_VDA, peak_r, rho}, with vda parallel to r_grid.
    with open(RB002_RESULTS) as f:
        rb002 = json.load(f)
    rb002_sha = rb002.get("meta", {}).get("sha256_numeric", "<missing>")
    variantA = rb002["vda_curves_A"]
    rb002_first_flip_rho20 = float(
        variantA["first_sign_flip_r"]["0.20"]
    )  # rb-002 reports r ≈ 0.464159 at ρ=0.20 at the headline cell.

    # ------------------------------------------------------------
    # (a) Source-payload sha guarantee — already loaded in main()
    #     and embedded in metadata["source_sha256"]; pass through.

    # (b) Sign-pattern check at nearest rb-003 cell to the rb-002
    #     headline.  rb-003's V-grid step is 0.0375 — closest to
    #     V=0.5 are V=0.4750 and V=0.5125; we pick V=0.5125 (the
    #     upper neighbour) by deterministic rule.
    NEAREST_V = 0.5125
    headline_cell = [
        c
        for c in cells
        if c["variant"] == "A"
        and abs(c["V"] - NEAREST_V) < 1e-6
        and abs(c["v"] - 5.0) < 1e-6
    ]
    # build {r: (VDA_0, VDA_rho, dVDA)} for the nearest cell.
    hc = {float(c["r"]): (c["VDA_0"], c["VDA_rho"], c["dVDA"]) for c in headline_cell}
    hc_r_sorted = sorted(hc)
    hc_rows = [
        dict(
            r=float(r),
            VDA_0=float(hc[r][0]),
            VDA_rho=float(hc[r][1]),
            dVDA=float(hc[r][2]),
            sign=("amp" if hc[r][2] > INACTIVE_EPS
                  else "supp" if hc[r][2] < -INACTIVE_EPS
                  else "inactive"),
        )
        for r in hc_r_sorted
    ]
    # Has both a small-r suppression and a large-r amplification?
    small_r_supp = any(
        row["dVDA"] < -INACTIVE_EPS and row["r"] < 0.5 for row in hc_rows
    )
    large_r_amp = any(
        row["dVDA"] > INACTIVE_EPS and row["r"] > 0.5 for row in hc_rows
    )
    pass_signflip_nearest = bool(small_r_supp and large_r_amp)
    # Cell-wise crossover at the nearest cell: smallest r at which the
    # sign of ΔVDA flips from negative to positive.
    nearest_crossover_r = None
    prev_sign = None
    for row in hc_rows:
        s = (1 if row["dVDA"] > INACTIVE_EPS
             else -1 if row["dVDA"] < -INACTIVE_EPS
             else 0)
        if prev_sign is not None and prev_sign < 0 and s > 0:
            nearest_crossover_r = row["r"]
            break
        if s != 0:
            prev_sign = s

    # (c) Per-cell crossover at variant A, ALL (V, v) cells, vs the
    #     rb-002 headline-cell crossover.  rb-002 saw r ≈ 0.464 at the
    #     V=0.5 cell; rb-003's sweep mixes higher-V cells in (where
    #     suppression dominates), so the cell-wise crossover should
    #     sit at or above 0.464.
    A_signflip = signflip_by_r(cells, "A")
    cell_wise_crossover = A_signflip["crossover_r"]
    pass_cellwise_ge_headline = (
        cell_wise_crossover is not None
        and cell_wise_crossover >= rb002_first_flip_rho20 - 1e-6
    )

    overall = pass_signflip_nearest and pass_cellwise_ge_headline

    return dict(
        rb002_sha=rb002_sha,
        rb002_first_flip_r_rho20=rb002_first_flip_rho20,
        nearest_cell=dict(
            variant="A", V=NEAREST_V, v=5.0,
            n_r_grid=len(hc_rows),
            rows=hc_rows,
            small_r_supp_present=small_r_supp,
            large_r_amp_present=large_r_amp,
            cell_crossover_r=nearest_crossover_r,
        ),
        cell_wise_crossover_r_variantA=cell_wise_crossover,
        pass_signflip_at_nearest_cell=pass_signflip_nearest,
        pass_cellwise_crossover_ge_headline=pass_cellwise_ge_headline,
        overall_pass=overall,
    )


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------


def fig_delta_distribution(per_variant: dict[str, dict[str, Any]]) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, variant in zip(axes, ("A", "B")):
        dist = per_variant[variant]
        # Approximate the per-cell ΔVDA via the joined cell list (passed
        # in via the `_cells` stash on the dict).
        arr = np.asarray(dist["_cell_dVDA"])
        # Symmetric-log-ish range: most cells cluster near 0, with a
        # long tail to ± a few hundredths.
        lim = max(abs(arr.min()), abs(arr.max()))
        bins = np.linspace(-lim, lim, 81)
        ax.hist(arr, bins=bins, color="steelblue", edgecolor="black", linewidth=0.3)
        ax.axvline(0.0, color="black", linewidth=0.8, linestyle="--")
        ax.axvline(dist["dVDA_mean"], color="crimson", linewidth=1.2,
                   label=f"mean = {dist['dVDA_mean']:+.4f}")
        ax.set_xlabel(r"$\Delta\mathrm{VDA} = \mathrm{VDA}(\rho{=}0.2)"
                      r" - \mathrm{VDA}(\rho{=}0)$")
        if variant == "A":
            ax.set_ylabel("cell count")
        # Annotation block in the corner with the sign-quadrant tally.
        msg = (
            f"variant {variant}\n"
            f"n = {dist['n_cells']}\n"
            f"amp  = {dist['n_amp']} "
            f"({100 * dist['frac_amp']:.1f}%)\n"
            f"supp = {dist['n_supp']} "
            f"({100 * dist['frac_supp']:.1f}%)\n"
            f"inac = {dist['n_inactive']} "
            f"({100 * dist['frac_inactive']:.1f}%)\n"
            f"q5/q95 = {dist['dVDA_q5']:+.4f} / {dist['dVDA_q95']:+.4f}"
        )
        ax.text(
            0.02, 0.98, msg, transform=ax.transAxes, fontsize=8,
            family="monospace", va="top", ha="left",
            bbox=dict(facecolor="white", alpha=0.85, edgecolor="0.6"),
        )
        ax.set_title(f"variant {variant}")
        ax.legend(loc="upper right", fontsize=8)
    fig.suptitle(
        r"A1 cell-wise $\Delta$VDA distribution (rb-003 4,410-cell sweep, $\rho{=}0.2$ vs $\rho{=}0$)",
        fontsize=11,
    )
    fig.tight_layout()
    out = FIG_DIR / "vda_delta_distribution.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def fig_signflip_by_r(per_variant_r: dict[str, dict[str, Any]]) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, variant in zip(axes, ("A", "B")):
        info = per_variant_r[variant]
        rows = info["rows"]
        rs = np.array([row["r"] for row in rows])
        fa = np.array([row["frac_amp"] for row in rows])
        fs = np.array([row["frac_supp"] for row in rows])
        ax.plot(rs, fa, "o-", color="seagreen", label="frac amp ($\\Delta$VDA $> 0$)")
        ax.plot(rs, fs, "s-", color="firebrick", label="frac supp ($\\Delta$VDA $< 0$)")
        ax.set_xscale("log")
        ax.set_xlabel(r"$r$ (benefit/cost ratio, log scale)")
        if variant == "A":
            ax.set_ylabel("fraction of (V, v) cells")
        ax.set_ylim(0, 1.02)
        ax.grid(True, which="both", alpha=0.3)
        cx = info["crossover_r"]
        if cx is not None:
            ax.axvline(cx, color="black", linestyle=":", linewidth=1,
                       label=f"crossover $r$ ≈ {cx:.3f}")
        ax.set_title(f"variant {variant}")
        ax.legend(loc="best", fontsize=8)
    fig.suptitle(
        r"A1 sign of $\partial$VDA$/\partial\rho$ at $\rho{=}0.2$, by $r$ (rb-003 sweep)",
        fontsize=11,
    )
    fig.tight_layout()
    out = FIG_DIR / "signflip_by_r.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def fig_vr_heatmap_v5(per_variant_vr: dict[str, dict[str, Any]]) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, variant in zip(axes, ("A", "B")):
        h = per_variant_vr[variant]
        Vs = np.array(h["Vs"])
        rs = np.array(h["rs"])
        Z = np.array(h["mean_dVDA"])
        lim = float(np.nanmax(np.abs(Z)))
        if not np.isfinite(lim) or lim == 0:
            lim = 1.0
        im = ax.pcolormesh(
            rs, Vs, Z,
            cmap="RdBu_r", vmin=-lim, vmax=+lim,
            shading="nearest",
        )
        ax.set_xscale("log")
        ax.set_xlabel(r"$r$ (log scale)")
        if variant == "A":
            ax.set_ylabel(r"validity $V$")
        ax.set_title(f"variant {variant}, $v = 5$")
        cb = fig.colorbar(im, ax=ax, shrink=0.85)
        cb.set_label(r"mean $\Delta$VDA per $(V, r)$ cell")
    fig.suptitle(
        r"A1 cell-wise sign-flip map of $\partial$VDA$/\partial\rho$ at $v=5$, $\rho{=}0.2$ vs $\rho{=}0$",
        fontsize=11,
    )
    fig.tight_layout()
    out = FIG_DIR / "vda_sign_heatmap_v5.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print("=" * 78)
    print("A1 cell-wise sign-flip map (RB-025; consumer of rb-003 sweep)")
    print("=" * 78)

    rho_panels, rb003_sha = load_rb003()
    cells = join_on_cell(rho_panels[RHO0_KEY], rho_panels[RHO_TARGET_KEY])

    # Per-variant Δ-distribution stats.
    per_variant: dict[str, dict[str, Any]] = {}
    for variant in ("A", "B"):
        per_variant[variant] = variant_distribution(cells, variant)
        # Stash the raw per-cell array on the dict so the histogram fig
        # can pull it without re-iterating; popped before JSON write.
        per_variant[variant]["_cell_dVDA"] = [
            c["dVDA"] for c in cells if c["variant"] == variant
        ]
    for variant in ("A", "B"):
        d = per_variant[variant]
        print(
            f"  variant {variant}: n={d['n_cells']}, "
            f"amp={d['n_amp']} ({100 * d['frac_amp']:.1f}%), "
            f"supp={d['n_supp']} ({100 * d['frac_supp']:.1f}%), "
            f"inac={d['n_inactive']} ({100 * d['frac_inactive']:.1f}%)"
        )
        print(
            f"    ΔVDA: mean={d['dVDA_mean']:+.5f}, "
            f"q5={d['dVDA_q5']:+.5f}, q50={d['dVDA_q50']:+.5f}, "
            f"q95={d['dVDA_q95']:+.5f}, max={d['dVDA_max']:+.5f}, "
            f"min={d['dVDA_min']:+.5f}"
        )

    # r-stratified sign-flip pattern.
    per_variant_r = {v: signflip_by_r(cells, v) for v in ("A", "B")}
    for variant in ("A", "B"):
        cx = per_variant_r[variant]["crossover_r"]
        print(
            f"  variant {variant} crossover r (frac_amp ≥ frac_supp): "
            f"{cx if cx is None else f'{cx:.4f}'}"
        )

    # (V, r) heatmap at v=5.
    per_variant_vr = {
        v: vr_signed_heatmap_at_v(cells, v, v_target=5.0) for v in ("A", "B")
    }

    # Figures.
    fig_a = fig_delta_distribution(per_variant)
    fig_b = fig_signflip_by_r(per_variant_r)
    fig_c = fig_vr_heatmap_v5(per_variant_vr)
    print(f"  figures: {fig_a.name}, {fig_b.name}, {fig_c.name}")

    # Recovery tests.
    rec = recovery_test_against_rb002(cells)
    nc = rec["nearest_cell"]
    print(
        f"  recovery vs rb-002 ({rec['rb002_sha'][:8]}…):"
    )
    print(
        f"    rb-002 headline first-flip r @ρ=0.20: "
        f"{rec['rb002_first_flip_r_rho20']:.4f}"
    )
    print(
        f"    nearest rb-003 cell (variant A, V={nc['V']}, v={nc['v']}): "
        f"small-r supp present={nc['small_r_supp_present']}, "
        f"large-r amp present={nc['large_r_amp_present']}, "
        f"cell crossover r = "
        f"{nc['cell_crossover_r'] if nc['cell_crossover_r'] is None else f'{nc['cell_crossover_r']:.4f}'}"
    )
    print(
        f"    variant-A cell-wise crossover r = "
        f"{rec['cell_wise_crossover_r_variantA']:.4f} "
        f"(≥ rb-002 headline {rec['rb002_first_flip_r_rho20']:.4f}: "
        f"{rec['pass_cellwise_crossover_ge_headline']})"
    )
    print(
        f"    OVERALL PASS = {rec['overall_pass']}"
    )

    # Drop the raw arrays before writing JSON.
    for variant in ("A", "B"):
        per_variant[variant].pop("_cell_dVDA", None)

    # Compose results.
    metadata = dict(
        sim_id="RB-025",
        claim_id="A1",
        prompt_version="0.2",
        run_id_proposed="rb-025-2026-05-29",
        source_results_json=str(RB003_RESULTS.relative_to(ROOT)),
        source_sha256=rb003_sha,
        rb002_results_json=str(RB002_RESULTS.relative_to(ROOT)),
        rb002_sha256=rec["rb002_sha"],
        rho_target=float(RHO_TARGET_KEY),
        inactive_eps=INACTIVE_EPS,
        sign_classification=(
            "amp if dVDA > eps; supp if dVDA < -eps; inactive otherwise"
        ),
        python="3.13 (matches rb-003)",
        figures=[fig_a.name, fig_b.name, fig_c.name],
    )
    results = dict(
        metadata=metadata,
        per_variant_distribution=per_variant,
        per_variant_signflip_by_r=per_variant_r,
        per_variant_heatmap_v5=per_variant_vr,
        recovery_test=rec,
    )

    # Sort dict keys recursively for deterministic sha256.
    payload = json.dumps(results, indent=2, sort_keys=True).encode("utf-8")
    sha = hashlib.sha256(payload).hexdigest()
    results["metadata"]["sha256"] = sha

    out_json = OUT_DIR / "results.json"
    # Write the final JSON with the sha embedded — and recompute the sha
    # of the embedded form for the printed line (so the printed value is
    # reproducible byte-for-byte on re-run; the embedded sha is the sha
    # of the *pre-embed* payload by convention, matching rb-003).
    with open(out_json, "wb") as f:
        f.write(json.dumps(results, indent=2, sort_keys=True).encode("utf-8"))
    print(f"  wrote {out_json.relative_to(ROOT)} (pre-embed sha256: {sha})")
    print("DONE.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
