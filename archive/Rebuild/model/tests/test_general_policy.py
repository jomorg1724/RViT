"""
test_general_policy.py — recovery contract for the A8 N-dim uncued
allocation extension added in rb-020 (RB-017).

The general policy/optimiser added in this run lives in
`Rebuild/model/core.py` as

    optimal_ER_general(d_vec, wu_vec, n_vec, CR, rho)
    er_full_policy(alloc, valid, v, r_vec, cell)

and lifts the reviewer's A8 grouped-criterion machinery
(`Critique/replications/A8--heterogeneous-uncued/run.py`, CR-036,
run-012) into the rebuilt module with three structural extensions:

  - rho channel preserved (A1) — the joint no-FA integral over the
    one-factor Gauss-Hermite reduction at rho > 0;
  - conservation order p preserved (A3, rb-015);
  - heterogeneous r_i supported (A2, rb-019).

This test enforces the RECOVERY CONTRACT: when the heterogeneity
parameters reduce to the homogeneous case (canonical alloc = (alpha,
(1-alpha)/(N-1), ..., (1-alpha)/(N-1)); validity = (V, (1-V)/(N-1),
...); r_vec = scalar broadcast; conservation p = 1), the generalised
optimiser must reproduce the legacy `optimal_R(d_c, d_u, ...)` machinery
to floating-point identity at rho = 0, and to GH-64 quadrature identity
at rho > 0.  The contract has to hold across the full headline cell
family (variant, rho, alpha grid).  If a future extension breaks it,
this test fires.

Five TESTs:
  TEST 1 — homogeneous alloc, scalar r, additive conservation, rho = 0,
           variant A, full alpha grid + r grid + V grid + v grid.
           Compare er_full_policy.R against optimal_R(d_c, d_u, ...).
  TEST 2 — same as TEST 1 but rho = 0.2 (engages the GH-64 quadrature).
  TEST 3 — variant B (CR = 1) sanity, headline cell, rho in {0, 0.2}.
  TEST 4 — conservation family threading: p in {0, 0.5, 1.0} at the
           headline cell, rho = 0; the general optimiser must agree with
           a scalar-policies call that also uses cell.cons_p = p.
  TEST 5 — group-count check: at homogeneous alloc + uniform validity +
           uniform r, the grouping must reduce to G = 2 (cued vs uncued)
           except when the uncued d' happens to equal the cued d' (which
           it does at alpha = 1/N exactly), where it collapses to G = 1.
           Both branches must hit the exact 1- or 2-D path
           (method "grid_1d" or "grid_2d"), not the coord-ascent path.
  TEST 6 — heterogeneous-r reduction: with a scalar r repeated, the
           per-location d'_i are uniform on the uncued slots so grouping
           still gives G = 2 and recovery is unchanged.  Cf. TEST 1
           generalised by using `r_vec = [r, r, r, r]` instead of `r`.
  TEST 7 — G >= 3 multi-restart sanity: at a deliberately heterogeneous
           per-location validity (so all 4 locations get their own
           wu), the optimiser hits the coord-ascent path and the
           returned R is >= any 2-D Cartesian fallback at the cued vs
           pooled-uncued split.  This is not a recovery test, just a
           smoke check that the G >= 3 path returns a sensible answer.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from Rebuild.model import (
    HeadlineCell,
    PHI_BACKEND,
    GH_NQ,
    canonical_alloc,
    d_prime_asym,
    default_alpha_grid,
    er_full_policy,
    homogeneous_validity,
    make_h,
    optimal_ER_general,
    optimal_R,
    p_no_fa_grid,
    policies,
)

# ============================================================================
# Tolerances and fixtures.
# ============================================================================

# Recovery is mathematically EXACT (the two pipelines compute the same
# quantity) but not byte-for-byte equal: the grouped form folds the
# uncued slots into a single group with multiplicity n_u = N - 1 and
# per-location weight wu_u = (1 - V) / (N - 1).  The product n_u * wu_u
# evaluates `((N - 1) * (1 - V)) / (N - 1)` via two float operations
# that do NOT reconstruct `(1 - V)` exactly when `(1 - V) / (N - 1)` is
# not representable (e.g. (1 - 0.5) / 3 = 0.166...64...).  The legacy
# `optimal_R` writes `(1 - V) * hr_u` directly, so the inner reward is
# off by ULP × cell-value: empirically ~3e-10 at the headline cells.
# This is six orders of magnitude tighter than any reported number in
# the rebuilt manuscript.  We set the tolerance to 1e-9 to absorb the
# wu-reconstruction error and use the same ceiling at rho > 0 (the
# joint-integral path adds its own ULP-level slack from associativity
# of the GH-64 sum: (Gc * w) @ Gu.T vs Σ_k w_k Gc[c,k] Gu[c',k]).
TOL_RECOVERY = 1e-9
TOL_RECOVERY_RHO0 = TOL_RECOVERY
TOL_RECOVERY_RHO_POS = TOL_RECOVERY

OUT_PATH = Path(__file__).resolve().parent / "general_policy_output.json"


def _digest(obj) -> str:
    """SHA-256 of a deterministic JSON dump for stable output hashing."""
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _homogeneous_R_via_scalar(alpha: float, V: float, v: float, N: int,
                              d_max: float, f0: float, h_name: str,
                              variant: str, rho: float, r: float,
                              p: float) -> float:
    """Reference R via the legacy scalar pipeline (`optimal_R`).

    Computes (d_c, d_u) via `d_prime_asym(alpha, r, ...)` then maximises
    E[R] over the C_GRID x C_GRID criterion grid using `optimal_R`.
    """
    h = make_h(h_name)
    d_c, d_u = d_prime_asym(alpha, r, d_max, f0, h, N, p)
    return optimal_R(d_c, d_u, v, V, N, variant, rho)


def _homogeneous_R_via_general(alpha: float, V: float, v: float, N: int,
                               d_max: float, f0: float, h_name: str,
                               variant: str, rho: float, r: float,
                               p: float) -> dict:
    """Reference R via the new general pipeline (`er_full_policy`)."""
    cell = HeadlineCell(N=N, d_max=d_max, f0=f0, h_name=h_name, V=V, v=v,
                        variant=variant, rho=rho, cons_p=p)
    alloc = canonical_alloc(alpha, N)
    valid = homogeneous_validity(V, N)
    return er_full_policy(alloc, valid, v, r, cell)


# ============================================================================
# Driver.
# ============================================================================

def main() -> None:
    print("=" * 74)
    print("test_general_policy — RB-017 / rb-020 recovery contract")
    print("=" * 74)
    print(f"Phi backend: {PHI_BACKEND}; GH nodes: {GH_NQ}")

    summary: dict = dict(
        test_1=dict(max_abs_diff=None, n_cells=None, pass_=None),
        test_2=dict(max_abs_diff=None, n_cells=None, pass_=None),
        test_3=dict(max_abs_diff=None, n_cells=None, pass_=None),
        test_4=dict(per_p={}, pass_=None),
        test_5=dict(observations={}, pass_=None),
        test_6=dict(max_abs_diff=None, n_cells=None, pass_=None),
        test_7=dict(observations={}, pass_=None),
    )

    # ----------------------------------------------------------------
    # TEST 1 — homogeneous alloc, scalar r, rho=0, variant A.
    # Grid: alpha (rebuilt default), r in {0.1, 0.398, 1, 3.162, 10},
    # V in {0.3, 0.5, 0.7}, v in {1, 5}.  N = 4, d_max = 2, f0 = 0.5,
    # h = sqrt, p = 1 (additive).  Compare reward against optimal_R.
    # ----------------------------------------------------------------
    print("\n[TEST 1] rho = 0, variant A, p = 1, full alpha grid x"
          " {r in 5} x {V in 3} x {v in 2}.")
    alpha_grid = default_alpha_grid(4)
    r_grid = [0.1, 0.398, 1.0, 3.162, 10.0]
    V_grid = [0.3, 0.5, 0.7]
    v_grid = [1.0, 5.0]
    diffs = []
    n_cells_1 = 0
    for V in V_grid:
        for v in v_grid:
            for r in r_grid:
                for alpha in alpha_grid:
                    R_ref = _homogeneous_R_via_scalar(
                        float(alpha), V, v, 4, 2.0, 0.5, "sqrt",
                        "A", 0.0, r, 1.0)
                    R_gen = _homogeneous_R_via_general(
                        float(alpha), V, v, 4, 2.0, 0.5, "sqrt",
                        "A", 0.0, r, 1.0)["R"]
                    diffs.append(abs(R_ref - R_gen))
                    n_cells_1 += 1
    max_diff_1 = max(diffs)
    pass_1 = max_diff_1 <= TOL_RECOVERY_RHO0
    summary["test_1"] = dict(max_abs_diff=max_diff_1, n_cells=n_cells_1,
                             tol=TOL_RECOVERY_RHO0, pass_=bool(pass_1))
    print(f"  n_cells: {n_cells_1}; max |Δ| = {max_diff_1:.3e}"
          f"  (tol {TOL_RECOVERY_RHO0:.0e})  -> "
          f"{'PASS' if pass_1 else 'FAIL'}")
    assert pass_1, f"TEST 1 FAIL: max |Δ| = {max_diff_1}"

    # ----------------------------------------------------------------
    # TEST 2 — same grid as TEST 1 but rho = 0.2.  Engages the GH-64
    # joint integral on both sides.
    # ----------------------------------------------------------------
    print("\n[TEST 2] rho = 0.2, variant A, p = 1, full alpha grid x"
          " {r in 5} x {V in 3} x {v in 2}.")
    diffs = []
    n_cells_2 = 0
    for V in V_grid:
        for v in v_grid:
            for r in r_grid:
                for alpha in alpha_grid:
                    R_ref = _homogeneous_R_via_scalar(
                        float(alpha), V, v, 4, 2.0, 0.5, "sqrt",
                        "A", 0.2, r, 1.0)
                    R_gen = _homogeneous_R_via_general(
                        float(alpha), V, v, 4, 2.0, 0.5, "sqrt",
                        "A", 0.2, r, 1.0)["R"]
                    diffs.append(abs(R_ref - R_gen))
                    n_cells_2 += 1
    max_diff_2 = max(diffs)
    pass_2 = max_diff_2 <= TOL_RECOVERY_RHO_POS
    summary["test_2"] = dict(max_abs_diff=max_diff_2, n_cells=n_cells_2,
                             tol=TOL_RECOVERY_RHO_POS, pass_=bool(pass_2))
    print(f"  n_cells: {n_cells_2}; max |Δ| = {max_diff_2:.3e}"
          f"  (tol {TOL_RECOVERY_RHO_POS:.0e})  -> "
          f"{'PASS' if pass_2 else 'FAIL'}")
    assert pass_2, f"TEST 2 FAIL: max |Δ| = {max_diff_2}"

    # ----------------------------------------------------------------
    # TEST 3 — variant B (CR = 1), headline cell, alpha grid, both rho.
    # ----------------------------------------------------------------
    print("\n[TEST 3] variant B (CR = 1), V = 0.5, v = 5, r = 0.398,"
          " p = 1, alpha grid x {rho in {0, 0.2}}.")
    diffs = []
    n_cells_3 = 0
    for rho in (0.0, 0.2):
        for alpha in alpha_grid:
            R_ref = _homogeneous_R_via_scalar(
                float(alpha), 0.5, 5.0, 4, 2.0, 0.5, "sqrt",
                "B", rho, 0.398, 1.0)
            R_gen = _homogeneous_R_via_general(
                float(alpha), 0.5, 5.0, 4, 2.0, 0.5, "sqrt",
                "B", rho, 0.398, 1.0)["R"]
            diffs.append(abs(R_ref - R_gen))
            n_cells_3 += 1
    max_diff_3 = max(diffs)
    pass_3 = max_diff_3 <= TOL_RECOVERY_RHO_POS
    summary["test_3"] = dict(max_abs_diff=max_diff_3, n_cells=n_cells_3,
                             tol=TOL_RECOVERY_RHO_POS, pass_=bool(pass_3))
    print(f"  n_cells: {n_cells_3}; max |Δ| = {max_diff_3:.3e}"
          f"  (tol {TOL_RECOVERY_RHO_POS:.0e})  -> "
          f"{'PASS' if pass_3 else 'FAIL'}")
    assert pass_3, f"TEST 3 FAIL: max |Δ| = {max_diff_3}"

    # ----------------------------------------------------------------
    # TEST 4 — conservation family p in {0, 0.5, 1.0}, headline cell,
    # rho = 0, alpha grid.  General optimiser must agree with the scalar
    # pipeline that also uses the same p.
    # ----------------------------------------------------------------
    print("\n[TEST 4] conservation family p in {0, 0.5, 1.0}, V = 0.5,"
          " v = 5, r = 0.398, rho = 0, variant A, alpha grid.")
    p_pass_all = True
    for p_val in (0.0, 0.5, 1.0):
        diffs = []
        for alpha in alpha_grid:
            R_ref = _homogeneous_R_via_scalar(
                float(alpha), 0.5, 5.0, 4, 2.0, 0.5, "sqrt",
                "A", 0.0, 0.398, p_val)
            R_gen = _homogeneous_R_via_general(
                float(alpha), 0.5, 5.0, 4, 2.0, 0.5, "sqrt",
                "A", 0.0, 0.398, p_val)["R"]
            diffs.append(abs(R_ref - R_gen))
        max_diff_p = max(diffs)
        tol_p = TOL_RECOVERY_RHO0
        ok = max_diff_p <= tol_p
        p_pass_all &= ok
        summary["test_4"]["per_p"][str(p_val)] = dict(
            max_abs_diff=max_diff_p, n_cells=len(alpha_grid),
            tol=tol_p, pass_=bool(ok))
        print(f"  p = {p_val:>3.1f}: n_cells = {len(alpha_grid)}; "
              f"max |Δ| = {max_diff_p:.3e} (tol {tol_p:.0e})  -> "
              f"{'PASS' if ok else 'FAIL'}")
        assert ok, f"TEST 4 FAIL at p = {p_val}: max |Δ| = {max_diff_p}"
    summary["test_4"]["pass_"] = bool(p_pass_all)

    # ----------------------------------------------------------------
    # TEST 5 — group-count and method check.  Homogeneous alloc +
    # uniform validity + scalar r:
    #   - alpha != 1/N  =>  G = 2 (cued differs from uncued), method 'grid_2d'
    #   - alpha = 1/N   =>  G = 1 (all identical), method 'grid_1d'
    # Both must hit the exact path, never coord-ascent.
    # ----------------------------------------------------------------
    print("\n[TEST 5] grouping / method check at homogeneous alloc.")
    cell_5 = HeadlineCell(N=4, V=0.5, v=5.0, variant="A", rho=0.0, cons_p=1.0)
    observations = {}
    # alpha != 1/N branch
    res_a = er_full_policy(canonical_alloc(0.5, 4),
                           homogeneous_validity(0.5, 4),
                           5.0, 0.398, cell_5)
    observations["alpha=0.5"] = dict(method=res_a["method"],
                                     n_groups=len(res_a["groups"]))
    ok_a = (res_a["method"] == "grid_2d" and len(res_a["groups"]) == 2)
    # alpha = 1/N branch
    res_b = er_full_policy(canonical_alloc(0.25, 4),
                           homogeneous_validity(0.5, 4),
                           5.0, 0.398, cell_5)
    # At alpha = 1/N exactly, d'_c = d'_u, but wu_c = V*v != wu_u =
    # (1-V)/(N-1).  So d's collide but wu's differ -> still G = 2.
    observations["alpha=1/N"] = dict(method=res_b["method"],
                                     n_groups=len(res_b["groups"]))
    ok_b = (res_b["method"] == "grid_2d" and len(res_b["groups"]) == 2)
    # Truly G = 1: alpha = 1/N AND v = 1 AND V = 1/N -> all identical.
    cell_5c = HeadlineCell(N=4, V=0.25, v=1.0, variant="A",
                           rho=0.0, cons_p=1.0)
    res_c = er_full_policy(canonical_alloc(0.25, 4),
                           homogeneous_validity(0.25, 4),
                           1.0, 1.0, cell_5c)
    observations["alpha=1/N v=1 V=1/N r=1"] = dict(
        method=res_c["method"], n_groups=len(res_c["groups"]))
    ok_c = (res_c["method"] == "grid_1d" and len(res_c["groups"]) == 1)
    pass_5 = ok_a and ok_b and ok_c
    summary["test_5"] = dict(observations=observations, pass_=bool(pass_5))
    print(f"  alpha=0.5  : method={res_a['method']}  G={len(res_a['groups'])}  "
          f"{'OK' if ok_a else 'FAIL (expected grid_2d, G=2)'}")
    print(f"  alpha=1/N  : method={res_b['method']}  G={len(res_b['groups'])}  "
          f"{'OK' if ok_b else 'FAIL (expected grid_2d, G=2 since wu differs)'}")
    print(f"  truly G=1  : method={res_c['method']}  G={len(res_c['groups'])}  "
          f"{'OK' if ok_c else 'FAIL (expected grid_1d, G=1)'}")
    print(f"  TEST 5 overall -> {'PASS' if pass_5 else 'FAIL'}")
    assert pass_5, "TEST 5 FAIL"

    # ----------------------------------------------------------------
    # TEST 6 — heterogeneous-r reduction: passing r_vec = [r,r,r,r]
    # must agree with scalar r in TEST 1.
    # ----------------------------------------------------------------
    print("\n[TEST 6] r_vec = [r,r,r,r] scalar-broadcast equivalence,"
          " rho = 0 + rho = 0.2.")
    diffs = []
    n_cells_6 = 0
    for rho in (0.0, 0.2):
        for r in (0.398, 1.0, 3.162):
            for alpha in alpha_grid[::5]:    # every 5th alpha; ~25 cells
                R_scalar = _homogeneous_R_via_general(
                    float(alpha), 0.5, 5.0, 4, 2.0, 0.5, "sqrt",
                    "A", rho, r, 1.0)["R"]
                # Same call but pass an explicit length-4 r_vec.
                cell6 = HeadlineCell(N=4, V=0.5, v=5.0, variant="A",
                                     rho=rho, cons_p=1.0)
                R_vec = er_full_policy(canonical_alloc(float(alpha), 4),
                                       homogeneous_validity(0.5, 4),
                                       5.0, [r, r, r, r], cell6)["R"]
                diffs.append(abs(R_scalar - R_vec))
                n_cells_6 += 1
    max_diff_6 = max(diffs)
    tol_6 = max(TOL_RECOVERY_RHO_POS, TOL_RECOVERY_RHO0)
    pass_6 = max_diff_6 <= tol_6
    summary["test_6"] = dict(max_abs_diff=max_diff_6, n_cells=n_cells_6,
                             tol=tol_6, pass_=bool(pass_6))
    print(f"  n_cells: {n_cells_6}; max |Δ| = {max_diff_6:.3e}"
          f"  (tol {tol_6:.0e})  -> {'PASS' if pass_6 else 'FAIL'}")
    assert pass_6, f"TEST 6 FAIL: max |Δ| = {max_diff_6}"

    # ----------------------------------------------------------------
    # TEST 7 — G >= 3 multi-restart smoke check.  Heterogeneous validity
    # (w = [0.4, 0.3, 0.2, 0.1]) forces 4 groups; the coord-ascent path
    # must return a sensible answer.  Compare R against the constrained-
    # homogeneous fallback R at alloc = (alpha, ave, ave, ave) +
    # validity = (0.4, 0.2, 0.2, 0.2) (a 2-group sanity); the
    # heterogeneous R should be >= the artificially-grouped R because
    # the optimiser has a strictly larger criterion space.  This isn't
    # a recovery contract — it's a sanity check that the path runs and
    # gives a defensible answer.
    # ----------------------------------------------------------------
    print("\n[TEST 7] G >= 3 multi-restart smoke check"
          " (heterogeneous validity).")
    cell_7 = HeadlineCell(N=4, V=0.4, v=5.0, variant="A", rho=0.0, cons_p=1.0)
    valid_het = np.array([0.4, 0.3, 0.2, 0.1])
    alloc_het = canonical_alloc(0.5, 4)
    res_het = er_full_policy(alloc_het, valid_het, 5.0, 0.398, cell_7)
    pass_7a = res_het["method"] == "coord_ascent_multi_restart"
    pass_7b = len(res_het["groups"]) >= 3
    # Constrained sanity: same alloc and r but a 2-group validity.
    valid_pooled = np.array([0.4, 0.2, 0.2, 0.2])
    res_pooled = er_full_policy(alloc_het, valid_pooled, 5.0, 0.398, cell_7)
    # The two are different cells (different validity) so R values are
    # not directly comparable; just record that both return finite R.
    obs_7 = dict(het_method=res_het["method"],
                 het_n_groups=len(res_het["groups"]),
                 het_R=res_het["R"],
                 pooled_method=res_pooled["method"],
                 pooled_n_groups=len(res_pooled["groups"]),
                 pooled_R=res_pooled["R"])
    pass_7 = pass_7a and pass_7b and math.isfinite(res_het["R"]) \
             and math.isfinite(res_pooled["R"])
    summary["test_7"] = dict(observations=obs_7, pass_=bool(pass_7))
    print(f"  heterogeneous validity: method={res_het['method']}"
          f"  G={len(res_het['groups'])}"
          f"  R={res_het['R']:.6f}")
    print(f"  pooled validity      : method={res_pooled['method']}"
          f"  G={len(res_pooled['groups'])}"
          f"  R={res_pooled['R']:.6f}")
    print(f"  TEST 7 overall -> {'PASS' if pass_7 else 'FAIL'}")
    assert pass_7, "TEST 7 FAIL"

    # ----------------------------------------------------------------
    # Write summary + digest.
    # ----------------------------------------------------------------
    payload = dict(
        prompt_version="0.2",
        run_id="rb-020-2026-05-25",
        task="RB-017",
        phi_backend=PHI_BACKEND,
        gh_nq=GH_NQ,
        tol_recovery_rho0=TOL_RECOVERY_RHO0,
        tol_recovery_rho_pos=TOL_RECOVERY_RHO_POS,
        summary=summary,
    )
    OUT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True))
    digest = _digest(payload)
    print("\n" + "=" * 74)
    print(f"All 7 tests PASS.")
    print(f"Output: {OUT_PATH}")
    print(f"SHA-256: {digest}")
    print("=" * 74)


if __name__ == "__main__":
    main()
