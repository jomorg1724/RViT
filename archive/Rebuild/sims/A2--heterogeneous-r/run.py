#!/usr/bin/env python3
# =====================================================================
# RB-018 (rb-021) — A2 heterogeneous-r sweep (simulation increment)
#
# QUESTION (mission §3.2 A2, paper §2.4). The inherited model governs
# the benefit/cost asymmetry by a *single global ratio* r. The reviewer
# settled the verdict at CONFIRMED-CONDITIONAL: under the between-
# preparation reading the simplification is safe; under the within-
# display reading it is empirically false but its consequence for
# C1–C5 is bounded (CR-048 / run-015).
#
# This script extends the reviewer's CR-048 verification harness in two
# rebuild-specific directions:
#
#   (i)  the rho channel (A1) is preserved end-to-end — every policy is
#        scored through `Rebuild/model/core.er_full_policy`, which
#        composes `d_prime_hetero` (rb-019, RB-014) with the joint
#        correlated no-FA quadrature (rb-001, RB-001). We can therefore
#        probe the A2 × A1 interaction the reviewer's harness could
#        not.
#   (ii) we report the recovery contract — spread=0 must reproduce the
#        homogeneous-r single-r model to 1e-9 absolute (the rb-020
#        recovery tolerance) — at every (rho, r) probed.
#
# Variant A primary. Additive conservation p=1 only (the conservation-
# family band is RB-019/RB-034's job, already shipped). rho ∈ {0, 0.2}.
#
# Reference cell (mission §2 / paper Fig. 4): N=4, d'_max=2, f0=0.5,
# h=sqrt. Headline cell V=0.5, v=5.
#
# OUTPUT.
#   results.json      — all numeric results, fully reproducible
#   figures/
#     vda_curves_spread.png    — VDA(r_cued) per (spread, rho) panel
#     vda_peak_band.png        — peak (r*, VDA*) vs spread, both rhos
#     cf_contested_corner.png  — variant-B C1 corner CF vs spread, rho
# =====================================================================

import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

# Local module: the rebuilt VDA model with rho channel and N-dim policy.
HERE = Path("/Users/jonathanmorgan/AttentionManuscript/Rebuild")
sys.path.insert(0, str(HERE))

from model.core import (  # noqa: E402
    HeadlineCell,
    Phi,
    PHI_BACKEND,
    canonical_alloc,
    d_prime_hetero,
    er_full_policy,
    floor_R,
    homogeneous_validity,
    make_h,
    optimal_R,
    policies,
)

# Reference regime (paper Fig. 4).
N = 4
D_MAX = 2.0
F0 = 0.5
H_NAME = "sqrt"
H = make_h(H_NAME)

# Sweep grids ---------------------------------------------------------
# r grid: 21-point geometric, matches CR-048's grid + rebuild C2 reference pins.
R_GRID = np.array(sorted(set(np.round(np.geomspace(0.1, 10.0, 21), 6).tolist()
                             + [0.398, 1.0, 3.162]).difference({0.398107}))).astype(float)
# Pull the "0.398" the C2 reference uses (geomspace gives 0.398107)
# and the symmetric corner.
R_GRID = np.unique(np.round(R_GRID, 6))

# Allocation grid: step 0.02 (CR-048's grid). Coarser than the rb-006
# step-0.005 to keep G=4 × rho>0 wall-clock manageable; recovery is
# checked at THIS grid against the legacy `policies()` reduced to the
# same grid (apples-to-apples).
ALPHA_GRID = np.round(np.arange(0.02, 1.0 + 1e-9, 0.02), 4)

# Uncued-r spreads probed.
SPREADS = (0.0, 0.1, 0.2, 0.3)

# rho values probed.
RHOS = (0.0, 0.2)

# C1 contested corner (variant B, v=4, V=0.25, r=10 — the rb-003 minimum
# CF cell).
C1_CORNER = dict(V=0.25, v=4.0, r=10.0, variant="B")

# Headline cell for criticality / allocation deviation / C2 reframe.
HEAD_V, HEAD_v = 0.5, 5.0


# ---------------------------------------------------------------------
# 0. Sweep helpers.
# ---------------------------------------------------------------------
def uncued_r_spread(r_cued, spread):
    """Build the (N,)-vector r_vec with cued = r_cued and the (N-1)=3
    uncued spread linearly around r_cued by factors {1-s, 1, 1+s}.
    spread=0 ⇒ homogeneous, reduces to the inherited single-r model
    exactly.
    """
    facs = np.array([1.0 - spread, 1.0, 1.0 + spread])
    return np.concatenate(([r_cued], r_cued * facs))


def homog_alloc(alpha):
    """Canonical homogeneous allocation: (alpha, (1-alpha)/(N-1), ...)."""
    return canonical_alloc(alpha, N)


def best_alpha_R(V, v, r_cued, spread, rho, variant="A",
                 alpha_grid=ALPHA_GRID):
    """P1 under A8-imposed equal-uncued split, per-location r, with the
    rho channel.  Returns (R*, alpha*).
    """
    r_vec = uncued_r_spread(r_cued, spread)
    valid = homogeneous_validity(V, N)
    cell = HeadlineCell(N=N, d_max=D_MAX, f0=F0, h_name=H_NAME,
                        V=V, v=v, variant=variant, rho=rho, cons_p=1.0)
    best_R, best_a = -np.inf, float("nan")
    for a in alpha_grid:
        res = er_full_policy(homog_alloc(a), valid, v, r_vec, cell)
        if res["R"] > best_R:
            best_R, best_a = res["R"], float(a)
    return best_R, best_a


def vda_cf_hetero(V, v, r_cued, spread, rho, variant="A",
                  alpha_grid=ALPHA_GRID):
    """Headline metrics under heterogeneous r, A8 imposed (equal uncued).

    VDA = R(P1) - R(P2),  CF = (R(P3) - R(P4)) / (R(P1) - R(P4)).

    P2 fixes alpha at alpha*(v=1).
    P3 fixes alpha = 1/N (uniform attention), criteria optimised.
    P4 fixes alpha = 1/N, criteria = 0.
    """
    r_vec = uncued_r_spread(r_cued, spread)
    valid = homogeneous_validity(V, N)
    cell = HeadlineCell(N=N, d_max=D_MAX, f0=F0, h_name=H_NAME,
                        V=V, v=v, variant=variant, rho=rho, cons_p=1.0)

    R_P1, a_star = best_alpha_R(V, v, r_cued, spread, rho, variant, alpha_grid)
    _, a_vb = best_alpha_R(V, 1.0, r_cued, spread, rho, variant, alpha_grid)
    R_P2 = er_full_policy(homog_alloc(a_vb), valid, v, r_vec, cell)["R"]
    R_P3 = er_full_policy(homog_alloc(1.0 / N), valid, v, r_vec, cell)["R"]
    # P4: alpha=1/N, criteria forced to zero. We can reuse `er_full_policy`
    # but we need criteria pinned at 0 — instead, recompute the closed
    # form directly using the rebuilt module's `floor_R` analogue on the
    # heterogeneous d' vector.
    alloc_p3 = homog_alloc(1.0 / N)
    d_arr = d_prime_hetero(alloc_p3, r_vec, D_MAX, F0, H, N, 1.0)
    wu = valid * np.where(np.arange(N) == 0, v, 1.0)  # value vector
    CR = float(np.sum(wu)) if variant == "A" else 1.0
    # HR(c=0) = Phi(d/2);  (1 - FAR)(c=0) = Phi(d/2).  Joint no-FA at
    # rho > 0 uses the equicorrelated reduction.
    if rho <= 0.0:
        prod_no_fa = float(np.prod(Phi(d_arr / 2.0)))
    else:
        # one-factor reduction: Phi((d/2 - sqrt(rho) z) / sqrt(1 - rho))
        # integrated over z ~ N(0,1).  Reuse the rb-001 GH-64 nodes.
        from model.core import _GH_Z, _GH_W  # noqa: F401  (test-internal use)
        z = _GH_Z; w = _GH_W
        # Phi((d/2 - sqrt(rho) z) / sqrt(1 - rho)) per location
        srho = math.sqrt(rho); s1mr = math.sqrt(1.0 - rho)
        # shape: (N, len(z))
        cols = (d_arr[:, None] / 2.0 - srho * z[None, :]) / s1mr
        per_loc = Phi(cols)  # (N, nq)
        prod_no_fa = float(np.sum(w * np.prod(per_loc, axis=0)))
    HR = Phi(d_arr / 2.0)
    R_P4 = 0.5 * float(np.sum(wu * HR)) + 0.5 * CR * prod_no_fa

    vda = R_P1 - R_P2
    denom = R_P1 - R_P4
    cf = (R_P3 - R_P4) / denom if abs(denom) > 1e-12 else float("nan")
    return dict(VDA=vda, CF=cf, alpha=a_star, alpha_vb=a_vb,
                R_P1=R_P1, R_P2=R_P2, R_P3=R_P3, R_P4=R_P4)


# ---------------------------------------------------------------------
# 1. Validation: spread=0 byte-for-byte recovery vs the inherited
#    single-r model (`policies()`).
#
# The recovery contract (rb-020 RB-017) guarantees that for homogeneous
# alloc + uniform validity + scalar r, the general optimiser returns
# the same R as `optimal_R` to 1e-9 absolute. We verify this here on the
# 21-point r-grid × 2 rhos = 42 cells of the headline (V, v).
# ---------------------------------------------------------------------
def validation_spread0_recovery():
    rows = []
    max_d_VDA = 0.0
    max_d_CF = 0.0
    for rho in RHOS:
        cell_legacy = HeadlineCell(N=N, d_max=D_MAX, f0=F0, h_name=H_NAME,
                                   V=HEAD_V, v=HEAD_v, variant="A", rho=rho,
                                   cons_p=1.0)
        for r in R_GRID:
            # Hetero path (spread=0).
            d_h = vda_cf_hetero(HEAD_V, HEAD_v, float(r), 0.0, rho, "A",
                                alpha_grid=ALPHA_GRID)
            # Legacy path on the SAME alpha grid (apples-to-apples).
            leg = policies(float(r), cell_legacy, alpha_grid=ALPHA_GRID)
            d_VDA = float(d_h["VDA"] - leg["VDA"])
            d_CF = float(d_h["CF"] - leg["CF"])
            max_d_VDA = max(max_d_VDA, abs(d_VDA))
            max_d_CF = max(max_d_CF, abs(d_CF))
            rows.append(dict(rho=rho, r=float(r),
                             VDA_hetero=d_h["VDA"], VDA_legacy=leg["VDA"],
                             d_VDA=d_VDA,
                             CF_hetero=d_h["CF"], CF_legacy=leg["CF"],
                             d_CF=d_CF))
    return dict(max_d_VDA=max_d_VDA, max_d_CF=max_d_CF,
                tol=1e-9, passed=(max_d_VDA <= 1e-9 and max_d_CF <= 1e-9),
                rows=rows)


# ---------------------------------------------------------------------
# 2. Criticality of equal-split on the uncued simplex (mission §3.2 /
#    CR-048 §(a)).
#
# At fixed cued alpha, compute g_j = ∂R/∂a_j for j ∈ uncued slots via
# central differences (criteria re-optimised at each). The tangent
# gradient on the uncued simplex is t_j = g_j - mean(g_uncued); zero iff
# equal-split is a critical point of the uncued sub-problem.
# Derivation: t = 0 iff r_i are equal across the uncued slots (the
# exchange-symmetry argument the reviewer's CR-045 §1 uses for A8
# requires A2 = single global r).
# ---------------------------------------------------------------------
def tangent_gradient(alpha, V, v, r_vec, rho, variant="A", eps=1e-4):
    valid = homogeneous_validity(V, N)
    cell = HeadlineCell(N=N, d_max=D_MAX, f0=F0, h_name=H_NAME,
                        V=V, v=v, variant=variant, rho=rho, cons_p=1.0)
    a_bar = (1.0 - alpha) / (N - 1)
    # Cap eps so finite-difference probes stay strictly inside (0, 1);
    # f_transfer uses sqrt and produces NaN for negative a_i. We
    # require a_bar - eps > 0 and a_bar + eps < 1.
    eps_safe = float(max(1e-8, min(eps, 0.45 * a_bar, 0.45 * (1.0 - a_bar))))
    base = np.concatenate(([alpha], np.full(N - 1, a_bar)))
    g = np.zeros(N - 1)
    for j in range(1, N):
        ap = base.copy(); ap[j] += eps_safe
        am = base.copy(); am[j] -= eps_safe
        # Numerical caveat: ap and am no longer sum to 1 exactly; we
        # use them as off-simplex finite-difference probes since the
        # reward formula does not require a strict simplex constraint
        # (it just uses the per-location a_i to score d'_i). The
        # tangent projection g - mean(g) cancels any common-mode
        # drift this introduces.
        Rp = er_full_policy(ap, valid, v, r_vec, cell)["R"]
        Rm = er_full_policy(am, valid, v, r_vec, cell)["R"]
        g[j - 1] = (Rp - Rm) / (2.0 * eps_safe)
    t = g - g.mean()
    return g, t, eps_safe


def criticality_test():
    """Criticality probed at an INTERIOR-alpha cost-dominant cell.

    At the rb-006 headline cell (V=0.5, v=5) every r in [0.1, 3.2] hits
    cued-absorption alpha*=1, leaving no uncued budget to perturb. We
    therefore probe at (V=0.5, v=2, r=0.3) where alpha*≈0.66 leaves
    B≈0.34 distributed equally across the three uncued slots — the same
    "cost-dominant with large uncued budget" regime the reviewer's
    CR-048 used (his model found alpha*≈0.74 at V=0.5, v=5, r=0.4; the
    rebuilt model's wider c-grid + continuous criterion search lifts
    that cell into cued-absorption, so we use a v=2 analogue).
    """
    out = {}
    crit_V, crit_v, r_cd = 0.5, 2.0, 0.3
    # First, find alpha* at the homogeneous cell (variant A, ρ=0).
    _, a_cd = best_alpha_R(crit_V, crit_v, r_cd, 0.0, 0.0, "A",
                           alpha_grid=ALPHA_GRID)
    out["cell"] = dict(V=crit_V, v=crit_v, r=r_cd)
    out["alpha_at_test"] = a_cd
    for rho in RHOS:
        for spread in (0.0, 0.3):
            r_vec = uncued_r_spread(r_cd, spread)
            g, t, eps_used = tangent_gradient(a_cd, crit_V, crit_v, r_vec,
                                              rho, "A")
            out[f"rho={rho}_spread={spread}"] = dict(
                rho=rho, spread=spread,
                r_vec=r_vec.tolist(),
                g=g.tolist(), t=t.tolist(),
                t_norm=float(np.linalg.norm(t)),
                eps_used=eps_used)
    return out


# ---------------------------------------------------------------------
# 3. Allocation deviation: ΔR = R(simplex-opt) - R(equal-split) at the
#    cost-dominant headline cell, across spread × rho.
#
# The reviewer's CR-048 §(b1) found ΔR ≤ 1.5e-4 at the headline cell
# under ρ=0 across spreads ≤ 0.3. We probe whether ρ=0.2 changes the
# magnitude / direction.
# ---------------------------------------------------------------------
def alloc_deviation_test():
    """ΔR = V(simplex-opt) − V(equal-split) at two cells:

      • cost-dominant interior-α cell (V=0.5, v=2, r=0.3, α*≈0.66) —
        the rebuilt analogue of the reviewer's CR-048 §(b1) probe; we
        expect ΔR small but nonzero and growing with var(r_i).
      • benefit-dominant cued-absorption cell (V=0.5, v=5, r=0.4,
        α*=1.0) — at α=1 the uncued budget B=0 so ΔR=0 exactly
        regardless of spread (CR-048 §(b2) prediction, structurally
        r-independent).
    """
    out = {}

    def _probe(label, V, v, r_cd):
        block = {}
        _, a_cd = best_alpha_R(V, v, r_cd, 0.0, 0.0, "A",
                               alpha_grid=ALPHA_GRID)
        block["alpha"] = a_cd
        block["cell"] = dict(V=V, v=v, r=r_cd)
        for rho in RHOS:
            for spread in (0.0, 0.1, 0.2, 0.3):
                r_vec = uncued_r_spread(r_cd, spread)
                valid = homogeneous_validity(V, N)
                cell = HeadlineCell(N=N, d_max=D_MAX, f0=F0, h_name=H_NAME,
                                    V=V, v=v, variant="A", rho=rho,
                                    cons_p=1.0)
                R_eq = er_full_policy(homog_alloc(a_cd), valid, v,
                                      r_vec, cell)["R"]
                B = 1.0 - a_cd
                step = 0.02
                ks = np.arange(0.0, B + 1e-9, step)
                R_best = R_eq
                best_alloc = None
                for b1 in ks:
                    for b2 in ks:
                        b3 = B - b1 - b2
                        if b3 < -1e-9:
                            continue
                        alloc = np.array([a_cd, b1, b2, max(b3, 0.0)])
                        R = er_full_policy(alloc, valid, v, r_vec,
                                           cell)["R"]
                        if R > R_best:
                            R_best = R
                            best_alloc = alloc
                dR = R_best - R_eq
                block[f"rho={rho}_spread={spread}"] = dict(
                    rho=rho, spread=spread,
                    R_eq=float(R_eq), R_best=float(R_best),
                    dR=float(dR),
                    var_r=float(np.var(r_vec[1:])),
                    best_alloc=(best_alloc.tolist()
                                if best_alloc is not None else None))
        out[label] = block

    _probe("cost_dominant", 0.5, 2.0, 0.3)
    _probe("benefit_dominant", 0.5, 5.0, 0.4)
    return out


# ---------------------------------------------------------------------
# 4. C2 reframe: VDA peak vs r_cued across spread × rho.
# ---------------------------------------------------------------------
def c2_reframe_sweep():
    out = {}
    # For each (spread, rho), build VDA(r_cued) over R_GRID.
    for rho in RHOS:
        for spread in SPREADS:
            vdas = []; cfs = []; alphas = []
            for r in R_GRID:
                m = vda_cf_hetero(HEAD_V, HEAD_v, float(r), spread, rho, "A",
                                  alpha_grid=ALPHA_GRID)
                vdas.append(m["VDA"]); cfs.append(m["CF"]); alphas.append(m["alpha"])
            vdas = np.array(vdas); cfs = np.array(cfs); alphas = np.array(alphas)
            k = int(np.argmax(vdas))
            out[f"rho={rho}_spread={spread}"] = dict(
                rho=rho, spread=spread,
                r_grid=R_GRID.tolist(),
                vdas=vdas.tolist(), cfs=cfs.tolist(),
                alphas=alphas.tolist(),
                r_peak=float(R_GRID[k]), vda_peak=float(vdas[k]),
                cf_at_peak=float(cfs[k]), alpha_at_peak=float(alphas[k]))
    return out


# ---------------------------------------------------------------------
# 5. C1 contested corner.
# ---------------------------------------------------------------------
def c1_corner_test():
    out = {}
    for rho in RHOS:
        for spread in (0.0, 0.1, 0.2, 0.3):
            m = vda_cf_hetero(C1_CORNER["V"], C1_CORNER["v"],
                              C1_CORNER["r"], spread, rho,
                              C1_CORNER["variant"], alpha_grid=ALPHA_GRID)
            out[f"rho={rho}_spread={spread}"] = dict(
                rho=rho, spread=spread,
                VDA=m["VDA"], CF=m["CF"], alpha=m["alpha"],
                R_P1=m["R_P1"], R_P2=m["R_P2"],
                R_P3=m["R_P3"], R_P4=m["R_P4"])
    return out


# ---------------------------------------------------------------------
# Figures.
# ---------------------------------------------------------------------
def make_figures(c2, dev, c1, out_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig_dir = Path(out_dir)
    fig_dir.mkdir(parents=True, exist_ok=True)

    # Figure 1: VDA(r_cued) panels by rho × spread family-of-curves.
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, rho in zip(axes, RHOS):
        for spread in SPREADS:
            entry = c2[f"rho={rho}_spread={spread}"]
            ax.plot(entry["r_grid"], entry["vdas"],
                    marker="o", ms=3, lw=1.4,
                    label=f"spread={spread:.1f}")
        ax.set_xscale("log")
        ax.set_xlabel(r"$r_{\mathrm{cued}}$ (cued benefit/cost ratio)")
        ax.set_title(rf"$\rho = {rho:.1f}$")
        ax.axhline(0.0, color="k", lw=0.6, alpha=0.3)
        ax.grid(True, alpha=0.3, which="both")
        ax.legend(fontsize=9, loc="upper right")
    axes[0].set_ylabel(r"VDA $= R(P_1) - R(P_2)$")
    fig.suptitle("A2 heterogeneous-r: VDA$(r_{\\mathrm{cued}})$ at headline cell "
                 "(V=0.5, v=5, N=4, variant A, p=1)")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(fig_dir / "vda_curves_spread.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: peak (r*, VDA*) vs spread, both rhos overlaid.
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    spr = np.array(SPREADS)
    for rho in RHOS:
        peaks_v = [c2[f"rho={rho}_spread={s}"]["vda_peak"] for s in SPREADS]
        peaks_r = [c2[f"rho={rho}_spread={s}"]["r_peak"] for s in SPREADS]
        axes[0].plot(spr, peaks_v, marker="o", lw=1.6, label=rf"$\rho={rho}$")
        axes[1].plot(spr, peaks_r, marker="o", lw=1.6, label=rf"$\rho={rho}$")
    axes[0].set_ylabel(r"peak VDA$^\star$")
    axes[0].set_xlabel("uncued spread")
    axes[0].set_title("A2: peak VDA invariance under spread")
    axes[0].axhline(0.083, color="grey", ls="--", lw=0.8,
                    label="rb-006 ref (spread=0)")
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3)
    axes[1].set_ylabel(r"peak $r_{\mathrm{cued}}^\star$")
    axes[1].set_xlabel("uncued spread")
    axes[1].set_title("A2: peak $r_{\\mathrm{cued}}^\\star$ under spread")
    axes[1].set_yscale("log")
    axes[1].axhline(0.398, color="grey", ls="--", lw=0.8,
                    label="rb-006 ref (spread=0)")
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(fig_dir / "vda_peak_band.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Figure 3: C1 contested corner CF vs spread, two rhos.
    fig, ax = plt.subplots(figsize=(6.5, 4.4))
    sp_grid = (0.0, 0.1, 0.2, 0.3)
    for rho in RHOS:
        cfs = [c1[f"rho={rho}_spread={s}"]["CF"] for s in sp_grid]
        ax.plot(sp_grid, cfs, marker="o", lw=1.6, label=rf"$\rho={rho}$")
    ax.set_xlabel("uncued spread")
    ax.set_ylabel("CF at C1 contested corner")
    ax.set_title("C1 contested corner under A2 spread × A1 ρ\n"
                 "(V=0.25, v=4, r=10, variant B)")
    ax.grid(True, alpha=0.3)
    ax.axhline(0.5, color="red", ls="--", lw=0.8, alpha=0.6,
               label="paper's [0.6, 0.96] floor lower edge (broken)")
    ax.legend(fontsize=9, loc="best")
    fig.tight_layout()
    fig.savefig(fig_dir / "cf_contested_corner.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------
def main():
    t0 = time.time()
    out = dict(config=dict(
        N=N, d_max=D_MAX, f0=F0, h=H_NAME,
        head_V=HEAD_V, head_v=HEAD_v,
        alpha_grid_n=len(ALPHA_GRID), alpha_grid_step=0.02,
        r_grid_n=len(R_GRID), r_grid=R_GRID.tolist(),
        spreads=list(SPREADS), rhos=list(RHOS),
        variant="A", cons_p=1.0,
        c1_corner=C1_CORNER,
        phi_backend=PHI_BACKEND,
    ))

    print("=" * 70)
    print("VALIDATION — spread=0 byte-for-byte recovery vs `policies()`")
    print("=" * 70)
    t1 = time.time()
    out["validation"] = validation_spread0_recovery()
    print(f"  max|ΔVDA|={out['validation']['max_d_VDA']:.3e}  "
          f"max|ΔCF|={out['validation']['max_d_CF']:.3e}  "
          f"tol=1e-9  passed={out['validation']['passed']}  "
          f"({time.time()-t1:.1f}s)")

    print("=" * 70)
    print("(a) CRITICALITY of equal-split on the uncued simplex")
    print("=" * 70)
    t1 = time.time()
    out["criticality"] = criticality_test()
    print(f"  cell: {out['criticality']['cell']}  α*={out['criticality']['alpha_at_test']:.3f}")
    for k, vv in out["criticality"].items():
        if isinstance(vv, dict) and "t_norm" in vv:
            print(f"  {k}: ||t||={vv['t_norm']:.3e}  eps={vv['eps_used']:.2e}")
    print(f"  ({time.time()-t1:.1f}s)")

    print("=" * 70)
    print("(b) ALLOCATION DEVIATION  (cost-dominant + benefit-dominant cells)")
    print("=" * 70)
    t1 = time.time()
    out["alloc_deviation"] = alloc_deviation_test()
    for cell_label, block in out["alloc_deviation"].items():
        print(f"  {cell_label} (α*={block['alpha']:.3f}):")
        for key, vv in block.items():
            if key in ("alpha", "cell"):
                continue
            print(f"    {key}: ΔR={vv['dR']:.3e}  var_r={vv['var_r']:.5f}")
    print(f"  ({time.time()-t1:.1f}s)")

    print("=" * 70)
    print("(c) C2 REFRAME — VDA peak vs r_cued under spread × ρ")
    print("=" * 70)
    t1 = time.time()
    out["c2_reframe"] = c2_reframe_sweep()
    for rho in RHOS:
        for spread in SPREADS:
            e = out["c2_reframe"][f"rho={rho}_spread={spread}"]
            print(f"  ρ={rho} spread={spread:.1f}  "
                  f"peak VDA*={e['vda_peak']:.5f} @ r_cued={e['r_peak']:.4f}")
    print(f"  ({time.time()-t1:.1f}s)")

    print("=" * 70)
    print("(d) C1 CONTESTED CORNER (variant B, V=0.25, v=4, r=10)")
    print("=" * 70)
    t1 = time.time()
    out["c1_corner"] = c1_corner_test()
    for k, v in out["c1_corner"].items():
        print(f"  {k}: CF={v['CF']:.4f}  α*={v['alpha']:.3f}")
    print(f"  ({time.time()-t1:.1f}s)")

    wall_clock_s = time.time() - t0
    print(f"\nTotal wall-clock: {wall_clock_s:.1f}s")
    # `wall_clock_s` is reported but deliberately NOT embedded in the
    # hashed payload — the run is otherwise deterministic and we want
    # the hash to be reproducible across machines / wall-clock noise.

    # Write results.json. Convention (matches rb-016): hash the payload
    # BEFORE embedding the hash field, then write `sha256_pre_hash` into
    # the on-disk file. The printed digest is the canonical
    # reproducibility hash — re-running this script should produce a
    # results.json whose `sha256_pre_hash` matches.
    out_dir = Path("/Users/jonathanmorgan/AttentionManuscript/Rebuild/"
                   "sims/A2--heterogeneous-r/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(out, indent=2, sort_keys=True,
                         default=float).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    out_with_hash = {**out, "sha256_pre_hash": digest}
    results_path = out_dir / "results.json"
    results_path.write_bytes(
        json.dumps(out_with_hash, indent=2, sort_keys=True,
                   default=float).encode("utf-8"))
    print(f"\nresults.json pre-hash sha256: {digest}")
    print(f"results.json size: {results_path.stat().st_size:,} B")

    # Figures.
    print("\nWriting figures.")
    make_figures(out["c2_reframe"], out["alloc_deviation"], out["c1_corner"],
                 out_dir / "figures")
    print("Done.")


if __name__ == "__main__":
    main()
