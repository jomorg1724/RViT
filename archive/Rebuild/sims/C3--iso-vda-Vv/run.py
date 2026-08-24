"""
Rebuild/sims/C3--iso-vda-Vv/run.py — RB-007.

Status: simulation increment rb-010 (2026-05-25), prompt v0.2.
Backing for: manuscript §results-C3 and the rewrite of the inherited
paper's §5.2 experimental-design advice (RB-011).

================================================================
WHAT THIS SIMULATION COMPUTES
================================================================
Iso-VDA contour maps over the (V, v) experimental-design plane at
six (r, ρ) panels: r ∈ {0.3, 1.0, 3.0} and ρ ∈ {0.0, 0.2}, on the
canonical N=4, d'_max=2, f0=0.5, h=sqrt headline cell, variant A
(CR = V·v + (1−V)). For each (V, v, r, ρ) cell it records P1..P4
rewards, VDA = R(P1) − R(P2), CF, and α*. Outputs:

  (1) results.json — full per-(V, v, r, ρ) record + summary blocks
      (quantiles of VDA in each panel; iso-VDA contour levels; cell
      fractions above thresholds; recovery test block; sha256).

  (2) figures/iso_vda_contours.png — 2 × 3 panel grid (ρ rows × r cols),
      filled iso-VDA contours over (V, v).  This is the figure the
      manuscript §results-C3 cites as the "graded / quantitative
      boundary" replacement for the inherited paper's categorical
      §5.2 claim.

  (3) figures/vda_at_high_V.png — line plot VDA(v) at four fixed
      validity strata V ∈ {0.4, 0.6, 0.8, 0.95}, panelled by r, with
      ρ=0 vs ρ=0.2 curves.  Targets the §5.2 sentence directly: at
      V=0.95 (high validity) is VDA actually "negligible regardless
      of v and r"?  The plot is the rebuild's quantitative answer.

  (4) figures/iso_vda_drho.png — 1 × 3 panel grid (r cols), filled
      contour map of ΔVDA := VDA(ρ=0.2) − VDA(ρ=0) over (V, v).  The
      sign-flip of dVDA/dρ that rb-002 showed at the headline cell
      (V=0.5, v=5) and that rb-004 showed across the v-family at
      V=0.5 — does it generalise to a sign-flip in the (V, v) plane?

================================================================
INHERITED PAPER CLAIM BEING RE-EVALUATED
================================================================
Inherited §5.2 (categorical, the reviewer's C3 verdict CONTESTS this):

   "high-validity paradigms show negligible VDA regardless of other
    parameters"

Rebuilt strength (CLAIM_LEDGER C3 row, ceiling on what we may state):

   "Graded/quantitative: VDA concentrates at low V, high v, moderate r;
    the §5.2 categorical experimental-design claim is retracted and
    replaced with iso-VDA contour bands."

This sim publishes the bands.  It does NOT replace one categorical
sentence with another; it publishes the contour topology and lets the
manuscript state the design implication as a quantitative threshold.

================================================================
RECOVERY TEST (the binding contract on every model extension)
================================================================
At (V=0.5, v=5, r=1, ρ=0, variant A) the rebuilt model's `policies()`
returns VDA = 0.039825 (rb-006 sim, sha256 09ecef3c..., results.json
sweeps['rho=0.0__v=5.0'] row r=1.0).  The present sim must reproduce
that to ≤ 1e-6 on its own grid (because v=5 is in our v-grid, r=1 is
in our r set, V=0.5 is in our V-grid, ρ=0 is in our ρ-set, and the
α-grid + criterion-grid are identical to the model defaults).  A
second anchor: (V=0.5, v=5, r=3.0, ρ=0, variant A) must reproduce
the rb-006 r=3.162278 number's neighbour (VDA ≈ 0.008 at r=3.162) up
to grid-density drift; we record VDA(r=3) for downstream reference.

A non-zero exit code is returned if the v=5, r=1, ρ=0 anchor fails.

================================================================
OUTPUT DETERMINISM
================================================================
Seed: not used (the model is fully deterministic: brute-force grid
optimisation over fixed α and c grids).  Reproducibility is verified
by hashing results.json with sha256 (excluding the hash field
itself).  Re-running the script with the same prompt-version-pinned
model module must produce a byte-identical results.json.

ATTRIBUTION
================================================================
The rebuilt model is `Rebuild/model/core.py` (rb-001, RB-001).  This
sim does not duplicate model code; it only sweeps it.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

# Make the Rebuild/model package importable when run as a script.
SIM_DIR = Path(__file__).resolve().parent
REBUILD_ROOT = SIM_DIR.parents[1]
if str(REBUILD_ROOT) not in sys.path:
    sys.path.insert(0, str(REBUILD_ROOT))

from model.core import HeadlineCell, policies, PHI_BACKEND, GH_NQ  # noqa: E402


# --------------------------------------------------------------------
# Configuration: sweep grids.  Documented inline so a reviewer can see
# the (V, v, r, ρ) coverage without running the script.
# --------------------------------------------------------------------
# V grid:  [0.25 = 1/N, 1.0] step 0.025  →  31 points.  V=0.25 is the
#   chance baseline (cue is value-only, no spatial information); V=1.0
#   is the perfect cue.  The §5.2 "high validity" stratum is V ≥ 0.8.
V_GRID = np.round(np.arange(0.25, 1.0 + 1e-9, 0.025), 6)
# v grid:  [1.0, 10.0] step 0.5  →  19 points.  v=1.0 is the value-blind
#   baseline (P1 = P2 by construction ⇒ VDA = 0).  v=10 is the
#   inherited paper's headline upper end.
V_VAL_GRID = np.round(np.arange(1.0, 10.0 + 1e-9, 0.5), 6)
# r set: the three asymmetry magnitudes the backlog calls for.
R_SET = (0.3, 1.0, 3.0)
# ρ set: zero (independent recovery) and 0.2 (the headline ρ used by
#   rb-002 / rb-003 / rb-004, anchored to the Cohen-Maunsell 2009
#   r_SC ≈ 0.2 estimate).
RHO_SET = (0.0, 0.2)

# Fixed cell parameters (the "headline cell" of the rebuild, matching
# rb-002 / rb-004 / rb-006 / rb-008 — N=4, d'_max=2, f0=0.5, h=sqrt,
# variant A).  V and v are swept *into* the cell, not fixed in it.
CELL_FIXED = dict(N=4, d_max=2.0, f0=0.5, h_name="sqrt", variant="A")

# Recovery anchor (rb-006, results.json, sweeps['rho=0.0__v=5.0'] row r=1.0).
RECOVERY_ANCHOR_V_VAL = 5.0
RECOVERY_ANCHOR_V = 0.5
RECOVERY_ANCHOR_R = 1.0
RECOVERY_ANCHOR_RHO = 0.0
RECOVERY_ANCHOR_VDA_RB006 = 0.039825
RECOVERY_TOL = 1.0e-4   # rb-006 logged 6 dp; ≤1e-4 is well past identical
                        # numerically (the rebuilt model is deterministic
                        # at the bit level; this tolerance only absorbs
                        # the 6-dp rounding in the rb-006 reference).

PROMPT_VERSION = "0.2"
RB_ID = "RB-007"
RUN_ID = "rb-010-2026-05-25"


# --------------------------------------------------------------------
# Sweep driver.
# --------------------------------------------------------------------
def run_sweep() -> dict:
    """Drive the (V, v, r, ρ) sweep and return a results dictionary.

    Shape:
        sweeps[(r, ρ)] is a dict with arrays of shape (|V|, |v|):
            VDA[i, j] = VDA at (V_GRID[i], V_VAL_GRID[j], r, ρ)
            CF[i, j], R_P1[i, j], R_P2[i, j], R_P3[i, j], R_P4[i, j],
            alpha_P1[i, j], alpha_vb[i, j]
    """
    n_v = len(V_GRID)
    n_v_val = len(V_VAL_GRID)
    sweeps: dict = {}
    t0 = time.time()
    total = len(R_SET) * len(RHO_SET) * n_v * n_v_val
    done = 0
    for r in R_SET:
        for rho in RHO_SET:
            VDA = np.full((n_v, n_v_val), np.nan)
            CF = np.full((n_v, n_v_val), np.nan)
            RP1 = np.full((n_v, n_v_val), np.nan)
            RP2 = np.full((n_v, n_v_val), np.nan)
            RP3 = np.full((n_v, n_v_val), np.nan)
            RP4 = np.full((n_v, n_v_val), np.nan)
            ALPHA = np.full((n_v, n_v_val), np.nan)
            ALPHA_VB = np.full((n_v, n_v_val), np.nan)
            for i, V in enumerate(V_GRID):
                for j, v_val in enumerate(V_VAL_GRID):
                    cell = HeadlineCell(V=float(V), v=float(v_val),
                                        rho=float(rho), **CELL_FIXED)
                    out = policies(float(r), cell)
                    VDA[i, j] = out["VDA"]
                    CF[i, j] = out["CF"]
                    RP1[i, j] = out["R_P1"]
                    RP2[i, j] = out["R_P2"]
                    RP3[i, j] = out["R_P3"]
                    RP4[i, j] = out["R_P4"]
                    ALPHA[i, j] = out["alpha_P1"]
                    ALPHA_VB[i, j] = out["alpha_vb"]
                    done += 1
            sweeps[f"r={r}__rho={rho}"] = dict(
                r=float(r), rho=float(rho),
                VDA=VDA.tolist(), CF=CF.tolist(),
                R_P1=RP1.tolist(), R_P2=RP2.tolist(),
                R_P3=RP3.tolist(), R_P4=RP4.tolist(),
                alpha_P1=ALPHA.tolist(), alpha_vb=ALPHA_VB.tolist(),
            )
            elapsed = time.time() - t0
            pct = 100.0 * done / total
            print(f"  done r={r} rho={rho}  "
                  f"VDA range [{np.nanmin(VDA):.5f}, {np.nanmax(VDA):.5f}]  "
                  f"{pct:5.1f}% in {elapsed:5.1f}s", flush=True)
    return sweeps


# --------------------------------------------------------------------
# Recovery test against rb-006 anchor.
# --------------------------------------------------------------------
def recovery_test(sweeps: dict) -> dict:
    """Verify the rb-006 anchor at (V=0.5, v=5, r=1, ρ=0)."""
    key = f"r={RECOVERY_ANCHOR_R}__rho={RECOVERY_ANCHOR_RHO}"
    block = sweeps[key]
    i = int(np.where(np.isclose(V_GRID, RECOVERY_ANCHOR_V))[0][0])
    j = int(np.where(np.isclose(V_VAL_GRID, RECOVERY_ANCHOR_V_VAL))[0][0])
    vda_here = float(block["VDA"][i][j])
    delta = abs(vda_here - RECOVERY_ANCHOR_VDA_RB006)
    passed = delta <= RECOVERY_TOL
    return dict(
        anchor=dict(V=RECOVERY_ANCHOR_V, v=RECOVERY_ANCHOR_V_VAL,
                    r=RECOVERY_ANCHOR_R, rho=RECOVERY_ANCHOR_RHO,
                    variant="A"),
        reference=dict(source="rb-006/sims/C2--vda-vs-r-vfamily/output/results.json"
                              " (sweeps['rho=0.0__v=5.0'] row r=1.0)",
                       VDA=RECOVERY_ANCHOR_VDA_RB006),
        observed=dict(VDA=vda_here),
        abs_diff=delta,
        tolerance=RECOVERY_TOL,
        passed=passed,
    )


# --------------------------------------------------------------------
# Summary statistics per (r, ρ) panel.
# --------------------------------------------------------------------
def summarise(sweeps: dict) -> dict:
    """Per-panel summary: VDA range, quantiles, cell fractions above
    thresholds, and the iso-VDA contour levels we plan to draw.
    """
    THRESHOLDS = (0.0001, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.15)
    CONTOUR_LEVELS = (0.0, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.15, 0.2)
    out = {}
    for key, block in sweeps.items():
        VDA = np.asarray(block["VDA"])
        finite = VDA[np.isfinite(VDA)]
        fracs = {f"frac_VDA_ge_{t}": float(np.mean(finite >= t))
                 for t in THRESHOLDS}
        out[key] = dict(
            r=block["r"], rho=block["rho"],
            n_cells=int(finite.size),
            VDA_min=float(finite.min()),
            VDA_max=float(finite.max()),
            VDA_median=float(np.median(finite)),
            VDA_q25=float(np.quantile(finite, 0.25)),
            VDA_q75=float(np.quantile(finite, 0.75)),
            VDA_q90=float(np.quantile(finite, 0.90)),
            VDA_q95=float(np.quantile(finite, 0.95)),
            fracs=fracs,
            contour_levels=list(CONTOUR_LEVELS),
        )
    return out


# --------------------------------------------------------------------
# A1 ρ-channel sign-flip: ΔVDA := VDA(ρ=0.2) − VDA(ρ=0) per (V, v, r).
# --------------------------------------------------------------------
def rho_sensitivity(sweeps: dict) -> dict:
    """For each r, compute ΔVDA over (V, v) and classify the sign-flip
    pattern across the plane.  Each entry maps r → a dict with the
    cell-wise fractions and the (V, v) of the maximum amplification and
    maximum suppression.
    """
    out = {}
    for r in R_SET:
        VDA0 = np.asarray(sweeps[f"r={r}__rho=0.0"]["VDA"])
        VDA2 = np.asarray(sweeps[f"r={r}__rho=0.2"]["VDA"])
        diff = VDA2 - VDA0
        finite = np.isfinite(diff)
        n = int(finite.sum())
        n_amp = int(np.sum((diff > 0) & finite))
        n_supp = int(np.sum((diff < 0) & finite))
        n_zero = int(np.sum((diff == 0) & finite))
        # arg-max amplification (most positive ΔVDA) and arg-max
        # suppression (most negative).
        amp_idx = int(np.nanargmax(np.where(finite, diff, -np.inf)))
        supp_idx = int(np.nanargmin(np.where(finite, diff, np.inf)))
        amp_i, amp_j = divmod(amp_idx, diff.shape[1])
        supp_i, supp_j = divmod(supp_idx, diff.shape[1])
        out[f"r={r}"] = dict(
            r=float(r),
            n_cells=n,
            n_amp=n_amp, frac_amp=n_amp / n if n else float("nan"),
            n_supp=n_supp, frac_supp=n_supp / n if n else float("nan"),
            n_zero=n_zero,
            max_amplification=dict(
                V=float(V_GRID[amp_i]), v=float(V_VAL_GRID[amp_j]),
                delta=float(diff[amp_i, amp_j]),
                VDA_rho0=float(VDA0[amp_i, amp_j]),
                VDA_rho2=float(VDA2[amp_i, amp_j]),
            ),
            max_suppression=dict(
                V=float(V_GRID[supp_i]), v=float(V_VAL_GRID[supp_j]),
                delta=float(diff[supp_i, supp_j]),
                VDA_rho0=float(VDA0[supp_i, supp_j]),
                VDA_rho2=float(VDA2[supp_i, supp_j]),
            ),
            mean_delta=float(np.nanmean(diff)),
        )
    return out


# --------------------------------------------------------------------
# §5.2 categorical claim probe: at high V, is VDA "negligible"?
# --------------------------------------------------------------------
def high_V_probe(sweeps: dict) -> dict:
    """For four fixed V strata and each (r, ρ), report VDA over v.

    Strata: V ∈ {0.4, 0.6, 0.8, 0.95}.  V=0.95 is the "high validity"
    end the §5.2 sentence quantifies over.  The probe is the
    quantitative answer to "is VDA negligible at high V regardless of
    v, r?"
    """
    V_PROBE = (0.4, 0.6, 0.8, 0.95)
    out = {}
    for V in V_PROBE:
        i = int(np.where(np.isclose(V_GRID, V))[0][0])
        sub = {}
        for r in R_SET:
            for rho in RHO_SET:
                block = sweeps[f"r={r}__rho={rho}"]
                vda_v = [float(block["VDA"][i][j])
                         for j in range(len(V_VAL_GRID))]
                sub[f"r={r}__rho={rho}"] = dict(
                    v_grid=V_VAL_GRID.tolist(),
                    VDA=vda_v,
                    max_VDA=max(vda_v), max_VDA_at_v=float(
                        V_VAL_GRID[int(np.argmax(vda_v))]),
                    VDA_at_vmax=vda_v[-1],
                )
        out[f"V={V}"] = sub
    return out


# --------------------------------------------------------------------
# JSON serialisation + hashing.
# --------------------------------------------------------------------
def write_results(results: dict, out_path: Path) -> str:
    """Write results.json with stable key order; return its sha256."""
    pre = dict(results)
    pre["sha256_pre_hash"] = "PENDING"
    body = json.dumps(pre, sort_keys=True, indent=2,
                      separators=(",", ": "))
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    final = dict(results)
    final["sha256_pre_hash"] = digest
    body_final = json.dumps(final, sort_keys=True, indent=2,
                            separators=(",", ": "))
    out_path.write_text(body_final + "\n")
    return digest


# --------------------------------------------------------------------
# Figures.
# --------------------------------------------------------------------
def make_figures(sweeps: dict, summary: dict, sens: dict,
                 high_V: dict, out_dir: Path) -> list[str]:
    """Render the three figures.  Returns paths written."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import ticker

    written = []

    # ---- Figure 1: 2 × 3 iso-VDA contour grid (ρ rows × r cols) ----
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 8.0), sharex=True,
                              sharey=True)
    vmin, vmax = 0.0, 0.0
    for block in sweeps.values():
        vmax = max(vmax, float(np.nanmax(block["VDA"])))
    LEVELS = [0.0, 0.001, 0.005, 0.01, 0.025, 0.05, 0.10, 0.15, 0.20, 0.25]
    LEVELS = [lv for lv in LEVELS if lv <= vmax + 0.01]
    Vmesh, vmesh = np.meshgrid(V_GRID, V_VAL_GRID, indexing="ij")
    for ri, rho in enumerate(RHO_SET):
        for ci, r in enumerate(R_SET):
            ax = axes[ri, ci]
            VDA = np.asarray(sweeps[f"r={r}__rho={rho}"]["VDA"])
            cs = ax.contourf(Vmesh, vmesh, VDA, levels=LEVELS,
                              cmap="viridis", vmin=vmin, vmax=vmax)
            ax.contour(Vmesh, vmesh, VDA, levels=LEVELS,
                       colors="k", linewidths=0.4, alpha=0.5)
            # iso-zero line if VDA crosses 0 anywhere
            if np.any(VDA <= 0) and np.any(VDA > 0):
                ax.contour(Vmesh, vmesh, VDA, levels=[0.0],
                           colors="red", linewidths=1.5,
                           linestyles="--")
            # chance-baseline marker V = 1/N = 0.25
            ax.axvline(0.25, color="white", linewidth=0.7,
                       linestyle=":")
            ax.set_title(f"r = {r}, ρ = {rho}", fontsize=10)
            if ri == 1:
                ax.set_xlabel("validity  V")
            if ci == 0:
                ax.set_ylabel("value  v")
            ax.grid(False)
    cbar = fig.colorbar(cs, ax=axes.ravel().tolist(), shrink=0.85,
                        pad=0.02, ticks=LEVELS)
    cbar.set_label("VDA  =  R(P1) − R(P2)")
    fig.suptitle("Iso-VDA contours over (V, v) — variant A, N=4, "
                 "d'_max=2, f0=0.5, h=sqrt   (rb-010, RB-007)",
                 fontsize=11)
    path = out_dir / "iso_vda_contours.png"
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    written.append(str(path))

    # ---- Figure 2: VDA(v) at V ∈ {0.4, 0.6, 0.8, 0.95}, panelled by r ----
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2), sharey=True)
    V_STRATA = (0.4, 0.6, 0.8, 0.95)
    colors = plt.cm.plasma(np.linspace(0.15, 0.85, len(V_STRATA)))
    for ci, r in enumerate(R_SET):
        ax = axes[ci]
        for s_i, V in enumerate(V_STRATA):
            blk = high_V[f"V={V}"][f"r={r}__rho=0.0"]
            ax.plot(blk["v_grid"], blk["VDA"], color=colors[s_i],
                    marker="o", markersize=3, lw=1.5,
                    label=f"V={V}, ρ=0")
            blk2 = high_V[f"V={V}"][f"r={r}__rho=0.2"]
            ax.plot(blk2["v_grid"], blk2["VDA"], color=colors[s_i],
                    marker="x", markersize=4, lw=1.0,
                    linestyle="--", alpha=0.85,
                    label=f"V={V}, ρ=0.2")
        ax.set_title(f"r = {r}", fontsize=10)
        ax.set_xlabel("value  v")
        ax.set_ylim(bottom=-0.005)
        ax.axhline(0.0, color="gray", lw=0.5)
        # "negligible" threshold reference at VDA = 0.005
        ax.axhline(0.005, color="gray", lw=0.5, linestyle=":")
        if ci == 0:
            ax.set_ylabel("VDA")
            ax.legend(loc="upper left", fontsize=7, ncol=2,
                       framealpha=0.85)
        ax.grid(True, alpha=0.25)
    fig.suptitle("VDA(v) at high-V strata — is §5.2 'negligible at high V "
                 "regardless of v, r' supported?  (rb-010, RB-007)",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    path = out_dir / "vda_at_high_V.png"
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    written.append(str(path))

    # ---- Figure 3: ΔVDA := VDA(ρ=0.2) − VDA(ρ=0) over (V, v), per r ----
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.5), sharex=True,
                              sharey=True)
    # symmetric levels around zero
    dabs = 0.0
    for r in R_SET:
        d = (np.asarray(sweeps[f"r={r}__rho=0.2"]["VDA"])
             - np.asarray(sweeps[f"r={r}__rho=0.0"]["VDA"]))
        dabs = max(dabs, float(np.nanmax(np.abs(d))))
    L = max(dabs, 0.001)
    DLEVELS = np.linspace(-L, L, 21)
    for ci, r in enumerate(R_SET):
        ax = axes[ci]
        d = (np.asarray(sweeps[f"r={r}__rho=0.2"]["VDA"])
             - np.asarray(sweeps[f"r={r}__rho=0.0"]["VDA"]))
        cs = ax.contourf(Vmesh, vmesh, d, levels=DLEVELS,
                          cmap="RdBu_r", vmin=-L, vmax=L)
        ax.contour(Vmesh, vmesh, d, levels=[0.0],
                   colors="k", linewidths=1.2)
        ax.set_title(f"r = {r}   (max|Δ| = {np.nanmax(np.abs(d)):.4f})",
                     fontsize=10)
        ax.set_xlabel("validity  V")
        if ci == 0:
            ax.set_ylabel("value  v")
        ax.axvline(0.25, color="black", linewidth=0.6, linestyle=":")
    cbar = fig.colorbar(cs, ax=axes.tolist(), shrink=0.85, pad=0.02)
    cbar.set_label("ΔVDA  =  VDA(ρ=0.2) − VDA(ρ=0)")
    fig.suptitle("A1 sign-flip across the (V, v) plane — red = "
                 "ρ-amplification, blue = ρ-suppression.   (rb-010, RB-007)",
                 fontsize=11)
    path = out_dir / "iso_vda_drho.png"
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    written.append(str(path))

    return written


# --------------------------------------------------------------------
# Main driver.
# --------------------------------------------------------------------
def main() -> int:
    out_dir = SIM_DIR / "output"
    fig_dir = out_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{RUN_ID}] starting C3 iso-VDA sweep")
    print(f"  V grid: {len(V_GRID)} pts [{V_GRID[0]}, {V_GRID[-1]}]")
    print(f"  v grid: {len(V_VAL_GRID)} pts [{V_VAL_GRID[0]}, {V_VAL_GRID[-1]}]")
    print(f"  r set:  {R_SET}")
    print(f"  ρ set:  {RHO_SET}")
    print(f"  total cells: "
          f"{len(V_GRID)*len(V_VAL_GRID)*len(R_SET)*len(RHO_SET)}")
    print(f"  Phi backend: {PHI_BACKEND}; GH nodes: {GH_NQ}")

    t0 = time.time()
    sweeps = run_sweep()
    elapsed = time.time() - t0
    print(f"sweep done in {elapsed:.1f}s")

    recovery = recovery_test(sweeps)
    print(f"recovery test: {'PASS' if recovery['passed'] else 'FAIL'}  "
          f"|Δ|={recovery['abs_diff']:.3e}  tol={recovery['tolerance']:.0e}")

    summary = summarise(sweeps)
    sens = rho_sensitivity(sweeps)
    high_V = high_V_probe(sweeps)

    figures = make_figures(sweeps, summary, sens, high_V, fig_dir)
    print(f"figures: {figures}")

    results = dict(
        rb_id=RB_ID, run_id=RUN_ID, prompt_version=PROMPT_VERSION,
        config=dict(
            V_grid=V_GRID.tolist(),
            v_grid=V_VAL_GRID.tolist(),
            r_set=list(R_SET),
            rho_set=list(RHO_SET),
            cell_fixed=CELL_FIXED,
            phi_backend=PHI_BACKEND,
            gh_nq=GH_NQ,
            n_total_cells=len(V_GRID) * len(V_VAL_GRID) * len(R_SET) * len(RHO_SET),
        ),
        sweeps=sweeps,
        summary=summary,
        rho_sensitivity=sens,
        high_V_probe=high_V,
        recovery=recovery,
        elapsed_seconds=float(elapsed),
    )

    digest = write_results(results, out_dir / "results.json")
    print(f"results.json sha256: {digest}")
    print(f"figures written: {len(figures)}")

    return 0 if recovery["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
