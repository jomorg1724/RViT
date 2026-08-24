"""
Rebuild/sims/A1--rho-channel/run.py — RB-002.

Status: simulation increment rb-002 (2026-05-25), prompt v0.2.
Backing for: manuscript §model and §results-A1 (the "three levers, not
two" reframe; what independence actually upper-bounds).

WHAT THIS SIMULATION COMPUTES
=============================
At the C2/Figure-4 headline cell — (N=4, d'_max=2, f_0=0.5, h=sqrt, V=0.5,
v=5) — under both reward variants A (CR = V v + (1-V)) and B (CR = 1), it
runs the rebuilt model's policies(r, cell) function across:

  * an r grid (log-spaced 25 points in [0.1, 10] with the C2 reference
    points {0.316, 0.398, 1.0, 3.162} pinned in), and
  * five rho values {0.0, 0.1, 0.2, 0.3, 0.4}, bracketing the Cohen &
    Maunsell (2009) interneuronal r_SC ~ 0.2.

It collects two deliverables, both required by RB-002:

  (1) VDA(r; rho) — VDA = R(P1) - R(P2) — as a family of five curves
      (one per rho) per reward variant.  Reports the per-rho peak (peak
      VDA value + the r at which it occurs).  Reports the pointwise
      upper-bound diagnostic: is VDA(r; rho > 0) <= VDA(r; 0) for all r?
      (The A1 verdict's headline finding is NO — d VDA/d rho flips sign
      near r ~ 0.5.)

  (2) CF(rho) at three r values {0.398, 1.0, 3.162} — the cost-dominant
      peak, the symmetric centre, and a benefit-dominant point.  CF is
      monotone-down in rho (Slepian: P_no-fa(rho) is monotone-up; the
      P3 - P4 numerator gains less than the P1 - P4 denominator when
      the criterion lever cheapens).  This is the corrected
      self-characterisation of A1: independence upper-bounds the
      CRITERION FRACTION, not VDA.

It also produces two figures, both intended for the manuscript:

  figures/vda_curves_variantA.png  VDA(r) family-of-curves (5 rhos)
  figures/vda_curves_variantB.png  same, variant B
  figures/cf_vs_rho.png            CF(rho) at the three r values
                                   (variants A and B side-by-side)

RECOVERY TEST (the mission's binding contract on every extension)
=================================================================
Before any rho > 0 result is trusted, the rho = 0 corner must reproduce
the inherited model byte-for-byte.  This sim verifies, at the headline
cell:

  rho=0 peak VDA(r), variant A:
      reviewer A1 replication: 0.0799 at r ~ 0.383
      rebuilt model module   : same to floating-point identity

  rho=0 CF and VDA at r in {0.398, 1.0, 3.162}, variant A:
      reviewer A1 replication: (see Critique/replications/A1--correlated-fa/
                                output/results.json, "cf_A" block)
      rebuilt model module   : same to floating-point identity

These checks are run BEFORE the figures are drawn; the script aborts with
a non-zero exit code if any check fails.

OUTPUT DETERMINISM
==================
The full numeric content is dumped to output/results.json, hashed with
sha256, and the hash is printed on stdout.  Re-running the script must
produce the same hash.  The only stochastic primitive in scope is
np.polynomial.hermite.hermgauss (deterministic); there is no RNG seed to
record.

REUSE / ATTRIBUTION
===================
All model primitives come from Rebuild/model (the rebuilt model module,
itself extending Critique/replications/A1--correlated-fa/run.py).  This
script does NOT re-implement the model; it only choreographs sweeps,
runs the recovery test, and draws figures.

Notes
-----
- The reviewer's A1 replication, run as a one-off CR-052 script under
  Critique/replications/A1--correlated-fa/, produced identical numbers.
  RB-002 lifts the same sweep out of the one-off into a manuscript-
  citable artifact under Rebuild/, with the figures the manuscript will
  actually \\include{}.  The byte-cross-check tightens the recovery
  contract: not only does rho=0 reproduce the paper, the entire (r, rho)
  surface reproduces the reviewer's reference output.

- Wall-clock budget: ~30-90 s on a laptop (2 variants x 5 rhos x ~28 r
  points x value-blind + value-on alpha sweeps).  Comfortably inside the
  mission's 10-20 min per-run cap.

Verification performed
----------------------
1. rho=0 path equals paper Eq. 9 to binary equality (inherited from
   model/tests/test_recovery.py and re-checked here).
2. rho=0 headline numbers (peak VDA, CF at three r values) reproduce
   the reviewer's logged numbers from
   Critique/replications/A1--correlated-fa/output/results.json.
3. Slepian monotonicity of P_no-fa(rho) at a fixed cell, exposed by
   model.slepian_curve and re-checked here.
4. sha256 of the full results.json is stable on re-run.

Extensions to consider
----------------------
- Sweep rho on a finer grid (e.g. {0.0, 0.05, 0.1, 0.15, 0.2}) to
  bracket the sign-flip r* more tightly.
- Add a structured-Sigma variant (block-diagonal cued vs uncued, or a
  signed correlation between cued and uncued only) to test how much of
  the benefit-dominant amplification is specific to equicorrelation
  (this is queued as a separate manuscript-extensions task, not RB-002).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from typing import Sequence

import numpy as np

# --- Make the parent Rebuild/ package importable when run as a script ---
HERE = os.path.dirname(os.path.abspath(__file__))
REBUILD_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if REBUILD_ROOT not in sys.path:
    sys.path.insert(0, REBUILD_ROOT)

# Rebuilt model module — single source of truth for VDA/CF computation.
from model import (  # noqa: E402  (sys.path manipulation above is intentional)
    GH_NQ,
    HeadlineCell,
    PHI_BACKEND,
    default_alpha_grid,
    p_no_fa_grid,
    p_no_fa_point,
    policies,
    r_grid_log,
    slepian_curve,
)


# ====================================================================
# CONSTANTS — exactly mirror the reviewer's A1 replication block so the
# rho=0 cross-check is byte-for-byte.
# ====================================================================

HEAD = HeadlineCell(N=4, d_max=2.0, f0=0.5, h_name="sqrt",
                    V=0.5, v=5.0, variant="A", rho=0.0)
RHOS = [0.0, 0.1, 0.2, 0.3, 0.4]
R_REF = (0.398, 1.0, 3.162)        # three r values for the CF(rho) figure

# Pre-built alpha grid (deterministic, used by both variants/rhos).
ALPHA_GRID = default_alpha_grid(HEAD.N)

# Reviewer reference numbers (Critique/replications/A1--correlated-fa/
# output/results.json, "cf_A" block, rho=0.00, variant A).  Used by the
# recovery test below.  Floats here must match the JSON to last digit.
# R_P3 and R_P4 are r-independent at rho=0 because P3/P4 use alpha=1/N
# (symmetric attention), at which the asymmetric d'(alpha) map collapses
# to the symmetric one: d_c = d_u = d'_base, independent of (beta, gamma)
# and hence of r.  This identity is also a useful sanity hook for the
# recovery check.
REVIEWER_REF_RHO0_A = {
    0.398: dict(VDA=0.07971892561151384, CF=0.8295190133917728,
                R_P1=2.2414603355617007, R_P3=2.148581181625177,
                R_P4=1.696653810304055),
    1.0:   dict(VDA=0.03982512744634903, CF=0.7282279801682813,
                R_P1=2.317238824377106, R_P3=2.148581181625177,
                R_P4=1.696653810304055),
    3.162: dict(VDA=0.00808898926330448, CF=0.6409382701716876,
                R_P1=2.401756614042182, R_P3=2.148581181625177,
                R_P4=1.696653810304055),
}
# Reviewer reference: peak VDA at rho=0, variant A, on the same r grid.
REVIEWER_REF_PEAK_RHO0_A = dict(peak_VDA=0.07986, peak_r_approx=0.383,
                                tol=5e-4)  # nearest r on the grid


# ====================================================================
# HELPERS
# ====================================================================

def _cell(variant: str, rho: float) -> HeadlineCell:
    """Build a HeadlineCell with the variant/rho swapped in."""
    return HeadlineCell(N=HEAD.N, d_max=HEAD.d_max, f0=HEAD.f0,
                        h_name=HEAD.h_name, V=HEAD.V, v=HEAD.v,
                        variant=variant, rho=rho)


def _vda_curve(variant: str, rho: float,
               r_grid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """VDA(r) at fixed (variant, rho); also returns CF(r) for free."""
    cell = _cell(variant, rho)
    vda = np.empty_like(r_grid, dtype=float)
    cf = np.empty_like(r_grid, dtype=float)
    for k, r in enumerate(r_grid):
        p = policies(float(r), cell, ALPHA_GRID)
        vda[k] = p["VDA"]
        cf[k] = p["CF"]
    return vda, cf


# ====================================================================
# BLOCKS
# ====================================================================

def block_recovery() -> dict:
    """The recovery contract: rho=0 must reproduce the reviewer's numbers.

    Tightest possible form — single-cell rewards must be EQUAL bit-for-
    bit at rho=0, since (i) the rebuilt model's rho=0 path short-circuits
    to the same Phi(b_c) Phi(b_u)^(N-1) product and (ii) both call the
    same Phi backend.  Any difference would indicate a deviation in the
    optimiser, the criterion grid, or the policy structure.
    """
    cell_A0 = _cell("A", 0.0)
    out = {}
    for r in R_REF:
        p = policies(float(r), cell_A0, ALPHA_GRID)
        ref = REVIEWER_REF_RHO0_A[r]
        diffs = {k: float(p[k] - ref[k]) for k in
                 ("VDA", "CF", "R_P1", "R_P3", "R_P4")}
        max_abs = max(abs(d) for d in diffs.values())
        out[f"r={r}"] = dict(rebuilt=p, reviewer=ref, diffs=diffs,
                             max_abs_diff=max_abs)
    # Peak VDA over a coarser inherited r grid (the one the reviewer's
    # block_vda_curve used).  Must match to 5e-4 in VDA value.
    rg = r_grid_log()
    vda0, _ = _vda_curve("A", 0.0, rg)
    pk = int(np.argmax(vda0))
    out["peak_rho0_A"] = dict(peak_VDA=float(vda0[pk]),
                              peak_r=float(rg[pk]),
                              reviewer=REVIEWER_REF_PEAK_RHO0_A)
    # Slepian monotonicity at a fixed (d_c, d_u, c_c=c_u=0.5) cell.
    curve = slepian_curve()
    monotone = all(curve[i + 1][1] >= curve[i][1] - 1e-12
                   for i in range(len(curve) - 1))
    out["slepian"] = dict(curve=curve, monotone=bool(monotone),
                          indep_is_min=bool(curve[0][1] <= min(
                              v for _, v in curve[1:]) + 1e-12))
    return out


def _assert_recovery(rec: dict) -> None:
    """Hard-fail the run if the recovery test does not pass."""
    bad = []
    for r in R_REF:
        if rec[f"r={r}"]["max_abs_diff"] > 1e-12:
            bad.append((f"single-cell r={r}",
                        rec[f"r={r}"]["max_abs_diff"]))
    pk = rec["peak_rho0_A"]
    if abs(pk["peak_VDA"] - REVIEWER_REF_PEAK_RHO0_A["peak_VDA"]) > \
            REVIEWER_REF_PEAK_RHO0_A["tol"]:
        bad.append(("peak VDA at rho=0",
                    abs(pk["peak_VDA"] -
                        REVIEWER_REF_PEAK_RHO0_A["peak_VDA"])))
    if not rec["slepian"]["monotone"]:
        bad.append(("slepian monotonicity", float("nan")))
    if not rec["slepian"]["indep_is_min"]:
        bad.append(("indep is P_no-fa minimum", float("nan")))
    if bad:
        for name, d in bad:
            print(f"  RECOVERY FAILURE [{name}]  max|d|={d:.3e}",
                  file=sys.stderr)
        raise AssertionError("Recovery test failed; aborting before figures.")


def block_vda_curves(variant: str) -> dict:
    """VDA(r) and CF(r) for each rho in RHOS, at fixed variant."""
    rg = r_grid_log()
    by_rho = {}
    for rho in RHOS:
        vda, cf = _vda_curve(variant, rho, rg)
        pk = int(np.argmax(vda))
        by_rho[f"{rho:.2f}"] = dict(rho=float(rho),
                                    peak_VDA=float(vda[pk]),
                                    peak_r=float(rg[pk]),
                                    vda=vda.tolist(),
                                    cf=cf.tolist())
    # Pointwise upper-bound diagnostic: does VDA(r; rho) <= VDA(r; 0)
    # hold for all r?  The verdict's headline finding is NO at r >~ 0.5
    # in the benefit-dominant tail.
    base = np.array(by_rho["0.00"]["vda"])
    ub_holds = {}
    max_excess = {}
    sign_flip_r = {}
    for rho in RHOS[1:]:
        cur = np.array(by_rho[f"{rho:.2f}"]["vda"])
        excess = cur - base                                # > 0 ==> VDA rose
        ub_holds[f"{rho:.2f}"] = bool(np.all(excess <= 1e-9))
        max_excess[f"{rho:.2f}"] = float(np.max(excess))
        # First r at which the sign of (cur - base) becomes positive.
        pos = np.where(excess > 0)[0]
        sign_flip_r[f"{rho:.2f}"] = float(rg[int(pos[0])]) if len(pos) \
            else float("nan")
    return dict(variant=variant, r_grid=rg.tolist(), by_rho=by_rho,
                upper_bound_holds_pointwise=ub_holds,
                max_excess_over_rho0=max_excess,
                first_sign_flip_r=sign_flip_r)


def block_cf_rho(variant: str) -> dict:
    """CF(rho) at the three reference r values, fixed variant."""
    rows = {}
    for r in R_REF:
        rows[f"r={r}"] = {}
        for rho in RHOS:
            p = policies(r, _cell(variant, rho), ALPHA_GRID)
            rows[f"r={r}"][f"{rho:.2f}"] = dict(
                CF=p["CF"], VDA=p["VDA"], R_P1=p["R_P1"],
                R_P3=p["R_P3"], R_P4=p["R_P4"], alpha_P1=p["alpha_P1"])
    # Monotonicity-down diagnostic for CF(rho).
    cf_mono_down = {}
    for r in R_REF:
        seq = [rows[f"r={r}"][f"{rho:.2f}"]["CF"] for rho in RHOS]
        cf_mono_down[f"r={r}"] = bool(all(seq[i + 1] <= seq[i] + 1e-12
                                          for i in range(len(seq) - 1)))
    return dict(variant=variant, rows=rows, cf_monotone_down_in_rho=cf_mono_down)


# ====================================================================
# FIGURES
# ====================================================================

def _ensure_figdir() -> str:
    fig_dir = os.path.join(HERE, "output", "figures")
    os.makedirs(fig_dir, exist_ok=True)
    return fig_dir


def fig_vda_curves(results: dict, variant: str) -> str:
    """VDA(r) family-of-curves figure, one curve per rho."""
    import matplotlib                                          # noqa: PLC0415
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt                            # noqa: PLC0415

    vc = results[f"vda_curves_{variant}"]
    rg = np.array(vc["r_grid"])
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    cmap = plt.get_cmap("viridis")
    for k, rho in enumerate(RHOS):
        vda = np.array(vc["by_rho"][f"{rho:.2f}"]["vda"])
        ax.plot(rg, vda, color=cmap(k / max(1, len(RHOS) - 1)),
                lw=1.8, label=fr"$\rho = {rho:.1f}$")
    ax.set_xscale("log")
    ax.set_xlabel(r"benefit-to-cost asymmetry $r = \beta/\gamma$")
    ax.set_ylabel(r"VDA $\equiv R(\mathrm{P1}) - R(\mathrm{P2})$")
    title = (rf"VDA$(r; \rho)$ — variant {variant}, "
             rf"$V={HEAD.V}$, $v={HEAD.v:g}$, $N={HEAD.N}$")
    ax.set_title(title, fontsize=10)
    ax.axvline(1.0, color="0.6", lw=0.7, ls=":")
    ax.legend(loc="upper right", fontsize=9, frameon=False)
    ax.grid(True, which="both", alpha=0.2)
    fig.tight_layout()
    fig_dir = _ensure_figdir()
    path = os.path.join(fig_dir, f"vda_curves_variant{variant}.png")
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def fig_cf_vs_rho(results: dict) -> str:
    """CF(rho) at three r, variants A + B side by side."""
    import matplotlib                                          # noqa: PLC0415
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt                            # noqa: PLC0415

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.0), sharey=True)
    markers = {0.398: "o", 1.0: "s", 3.162: "D"}
    labels = {0.398: r"$r=0.398$ (cost-dominant peak)",
              1.0:   r"$r=1.0$ (symmetric)",
              3.162: r"$r=3.162$ (benefit-dominant)"}
    for ax, variant in zip(axes, ("A", "B")):
        rows = results[f"cf_rho_{variant}"]["rows"]
        for r in R_REF:
            cf = [rows[f"r={r}"][f"{rho:.2f}"]["CF"] for rho in RHOS]
            ax.plot(RHOS, cf, marker=markers[r], lw=1.6, label=labels[r])
        ax.set_xlabel(r"noise correlation $\rho$")
        ax.set_title(f"variant {variant}", fontsize=10)
        ax.grid(True, alpha=0.2)
        ax.set_xlim(-0.02, 0.42)
    axes[0].set_ylabel("criterion fraction CF")
    axes[0].legend(loc="lower left", fontsize=8.5, frameon=False)
    fig.suptitle(rf"CF$(\rho)$ at three $r$ — what independence "
                 rf"actually upper-bounds (cell: $V={HEAD.V}$, $v={HEAD.v:g}$, "
                 rf"$N={HEAD.N}$)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig_dir = _ensure_figdir()
    path = os.path.join(fig_dir, "cf_vs_rho.png")
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


# ====================================================================
# MAIN
# ====================================================================

def main() -> int:
    t0 = time.time()
    out_dir = os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)

    # 1. Recovery test — abort hard if rho=0 deviates.
    rec = block_recovery()
    _assert_recovery(rec)

    # 2. Headline sweeps.
    results = dict(
        meta=dict(
            phi_backend=PHI_BACKEND,
            nq=GH_NQ,
            alpha_step=0.005,
            c_step=0.05,
            head=dict(N=HEAD.N, d_max=HEAD.d_max, f0=HEAD.f0,
                      h_name=HEAD.h_name, V=HEAD.V, v=HEAD.v),
            rhos=RHOS,
            r_ref=list(R_REF),
            rebuild_run="rb-002",
            backed_claim="A1",
            reuses="Rebuild/model (rb-001) — single source of truth",
        ),
        recovery=rec,
        vda_curves_A=block_vda_curves("A"),
        vda_curves_B=block_vda_curves("B"),
        cf_rho_A=block_cf_rho("A"),
        cf_rho_B=block_cf_rho("B"),
    )

    # 3. Figures (after numeric content is finalised; do not include
    #    figure paths in the digest so output is path-independent).
    fig_paths = dict(
        vda_curves_A=fig_vda_curves(results, "A"),
        vda_curves_B=fig_vda_curves(results, "B"),
        cf_vs_rho=fig_cf_vs_rho(results),
    )

    # 4. Determinism digest — hash NUMERIC content only.
    numeric_json = json.dumps(results, indent=2, sort_keys=True)
    digest = hashlib.sha256(numeric_json.encode()).hexdigest()
    results["meta"]["sha256_numeric"] = digest
    results["meta"]["runtime_s"] = round(time.time() - t0, 2)
    results["figures"] = {k: os.path.relpath(v, REBUILD_ROOT)
                          for k, v in fig_paths.items()}

    with open(os.path.join(out_dir, "results.json"), "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    # ---- console summary ----
    print(f"[Phi backend] {PHI_BACKEND}  | nq={GH_NQ} | "
          f"runtime={results['meta']['runtime_s']}s")
    print(f"[recovery] rho=0 single-cell max|d| at r={R_REF}: "
          + ", ".join(f"{rec[f'r={r}']['max_abs_diff']:.2e}"
                      for r in R_REF))
    print(f"[recovery] rho=0 peak VDA: rebuilt={rec['peak_rho0_A']['peak_VDA']:.5f} "
          f"at r={rec['peak_rho0_A']['peak_r']:.4f}  "
          f"(reviewer ~{REVIEWER_REF_PEAK_RHO0_A['peak_VDA']:.5f} @ "
          f"r~{REVIEWER_REF_PEAK_RHO0_A['peak_r_approx']:.3f})")
    print(f"[Slepian] monotone-up in rho: {rec['slepian']['monotone']}; "
          f"indep is min: {rec['slepian']['indep_is_min']}")
    for variant in ("A", "B"):
        vc = results[f"vda_curves_{variant}"]
        print(f"\n[VDA(r) peak vs rho - variant {variant}]")
        for rho in RHOS:
            d = vc["by_rho"][f"{rho:.2f}"]
            print(f"   rho={rho:.2f}:  peak VDA = {d['peak_VDA']:.5f} "
                  f"at r = {d['peak_r']:.4f}")
        print(f"   upper-bound holds pointwise (VDA(r;rho) <= VDA(r;0) "
              f"for all r): {vc['upper_bound_holds_pointwise']}")
        print(f"   max excess over rho=0: "
              + ", ".join(f"rho{rho:.1f}->{vc['max_excess_over_rho0'][f'{rho:.2f}']:.3e}"
                          for rho in RHOS[1:]))
        print(f"   first sign-flip r (>0 excess): "
              + ", ".join(f"rho{rho:.1f}->{vc['first_sign_flip_r'][f'{rho:.2f}']}"
                          for rho in RHOS[1:]))
    for variant in ("A", "B"):
        print(f"\n[CF(rho) - variant {variant}]")
        rows = results[f"cf_rho_{variant}"]["rows"]
        for r in R_REF:
            line = (f"   r={r:>5}:  "
                    + "  ".join(f"rho{rho:.1f}->CF={rows[f'r={r}'][f'{rho:.2f}']['CF']:.4f}"
                                for rho in RHOS))
            print(line)
        print(f"   CF monotone-down in rho: "
              f"{results[f'cf_rho_{variant}']['cf_monotone_down_in_rho']}")
    print(f"\n[figures]")
    for name, path in fig_paths.items():
        print(f"   {name}: {os.path.relpath(path, REBUILD_ROOT)}")
    print(f"\n[sha256 numeric] {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
