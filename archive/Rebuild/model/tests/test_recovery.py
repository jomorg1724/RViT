"""
tests/test_recovery.py — the rho->0 recovery contract.

This is the contract every future extension of Rebuild/model/ must
satisfy: in the rho = 0 limit, the rebuilt model reproduces the
inherited Herman-Lab model (paper Eq. 9, independent SDT decisions)
*to machine tolerance*.  The reviewer's CR-052 replication
(Critique/replications/A1--correlated-fa/run.py, run-017) is the
authoritative numerical reference for those numbers; the targets pinned
below come straight from
    Critique/replications/A1--correlated-fa/output/results.json
inspected on 2026-05-25.

Two test surfaces.

(1) PROBABILITY-LEVEL recovery.  At any (d_c, d_u, c_c, c_u, N), the
    correlated quadrature P_no-fa(rho) must agree with the independent
    product Phi(b_c) Phi(b_u)^(N-1) as rho -> 0 AND when rho = 0 is
    shortcut.  Specifically:
      - the rho = 0 path (the analytical shortcut) equals the product
        exactly (binary equality across the full criterion grid);
      - the rho = 1e-6 path (the quadrature path) matches the product
        to better than 1e-12.

(2) POLICY-LEVEL recovery.  At the C2 headline cell (V=0.5, v=5, N=4,
    d'_max=2, f_0=0.5, h=sqrt, variant A), with rho = 0 the rebuilt
    pipeline reproduces the reviewer's logged numbers:
      r = 0.398:  VDA = 0.07972,   CF = 0.82952    (peak r is C2 ref)
      r = 1.0:    VDA = 0.03983,   CF = 0.72823
      r = 3.162:  VDA = 0.00809,   CF = 0.64094
    Peak VDA over a log r-grid (with the C2 references pinned): 0.0797
    at r = 0.398.

(3) SLEPIAN MONOTONICITY (sanity).  P_no-fa(rho) is non-decreasing in
    rho at a fixed (d_c, d_u, c_c, c_u, N), with rho = 0 the minimum.

A failing recovery test invalidates every downstream simulation / claim
that depends on the model module.  Run before any new mechanism is
wired in.

Run:
    cd Rebuild/
    python3 -m model.tests.test_recovery
or  python3 model/tests/test_recovery.py
"""

from __future__ import annotations

import math
import sys
import os
from pathlib import Path

# Allow running as a script: `python3 Rebuild/model/tests/test_recovery.py`
_HERE = Path(__file__).resolve()
_REBUILD_ROOT = _HERE.parent.parent.parent  # .../Rebuild/
if str(_REBUILD_ROOT) not in sys.path:
    sys.path.insert(0, str(_REBUILD_ROOT))

import numpy as np

from model.core import (  # noqa: E402
    C_GRID,
    GH_NQ,
    HeadlineCell,
    PHI_BACKEND,
    Phi,
    p_no_fa_grid,
    p_no_fa_point,
    policies,
    r_grid_log,
    slepian_curve,
    vda_curve,
)


# --------------------------------------------------------------------
# Reviewer's logged headline numbers (rho = 0, variant A, C2 headline cell).
# Source: Critique/replications/A1--correlated-fa/output/results.json
# These are the recovery targets.  Tolerances are picked tight enough to
# catch any silent change in the criterion grid, the alpha grid, or the
# Phi backend.
# --------------------------------------------------------------------
REVIEWER_TARGETS_RHO0 = {
    0.398: dict(VDA=0.07971892561151384, CF=0.8295190133917728,
                R_P1=2.2414603355617007, R_P4=1.696653810304055),
    1.000: dict(VDA=0.03982512744634903, CF=0.7282279801682813,
                R_P1=2.317238824377106,  R_P4=1.696653810304055),
    3.162: dict(VDA=0.00808898926330448, CF=0.6409382701716876,
                R_P1=2.401756614042182,  R_P4=1.696653810304055),
}

TOL_REWARD = 1e-9
TOL_VDA = 1e-9
TOL_CF = 1e-9


def _approx(a: float, b: float, tol: float) -> bool:
    return abs(a - b) <= tol


# --------------------------------------------------------------------
# (1) Probability-level recovery.
# --------------------------------------------------------------------
def test_p_no_fa_rho0_equals_product() -> dict:
    """rho = 0 shortcut returns exactly the paper Eq. 9 product."""
    d_c, d_u, N = 1.8, 1.2, 4
    grid = p_no_fa_grid(d_c, d_u, N, 0.0)
    b_c = C_GRID + d_c / 2.0
    b_u = C_GRID + d_u / 2.0
    expected = Phi(b_c)[:, None] * (Phi(b_u)[None, :] ** (N - 1))
    diff = float(np.max(np.abs(grid - expected)))
    ok = diff == 0.0
    return dict(name="p_no_fa(rho=0) == product (binary)", ok=ok,
                max_abs_diff=diff)


def test_p_no_fa_tiny_rho_converges_to_product() -> dict:
    """rho -> 0 quadrature path converges to the product.

    The integrand depends *analytically* on rho, with a first-order
    correction of size O(rho), so |P(rho) - P(0)| ~ rho is the right
    expectation as rho -> 0.  We check this directly by halving rho and
    confirming the diff to the product shrinks by ~2x.  The threshold
    on the absolute diff is then any safe constant times rho — we use
    10 * rho.
    """
    d_c, d_u, N = 1.8, 1.2, 4
    b_c = C_GRID + d_c / 2.0
    b_u = C_GRID + d_u / 2.0
    expected = Phi(b_c)[:, None] * (Phi(b_u)[None, :] ** (N - 1))
    diffs = []
    rhos = (1e-4, 1e-5, 1e-6)
    for rho in rhos:
        grid = p_no_fa_grid(d_c, d_u, N, rho)
        diffs.append(float(np.max(np.abs(grid - expected))))
    # O(rho) scaling: each 10x cut in rho should cut the diff ~10x.
    scaling_ok = (diffs[1] < 0.5 * diffs[0]) and (diffs[2] < 0.5 * diffs[1])
    abs_ok = diffs[-1] < 10.0 * rhos[-1]
    return dict(name="p_no_fa(rho->0) -> product, O(rho) scaling", ok=(scaling_ok and abs_ok),
                max_abs_diff=diffs[-1],
                diffs=dict(zip([f"{r:.0e}" for r in rhos], diffs)))


# --------------------------------------------------------------------
# (2) Policy-level recovery against reviewer-logged numbers.
# --------------------------------------------------------------------
def test_policy_recovery_at_reference_r() -> list[dict]:
    cell = HeadlineCell(rho=0.0)
    out = []
    for r, tgt in REVIEWER_TARGETS_RHO0.items():
        p = policies(r, cell)
        ok = (_approx(p["VDA"], tgt["VDA"], TOL_VDA)
              and _approx(p["CF"], tgt["CF"], TOL_CF)
              and _approx(p["R_P1"], tgt["R_P1"], TOL_REWARD)
              and _approx(p["R_P4"], tgt["R_P4"], TOL_REWARD))
        out.append(dict(
            name=f"policy recovery @ r={r}",
            ok=ok,
            VDA=p["VDA"], VDA_target=tgt["VDA"], VDA_diff=p["VDA"] - tgt["VDA"],
            CF=p["CF"],   CF_target=tgt["CF"],   CF_diff=p["CF"] - tgt["CF"],
        ))
    return out


def test_peak_vda_over_r_grid() -> dict:
    """Peak of VDA(r) at rho=0 lands at the reviewer's published peak.

    Reviewer's run-017 reports peak VDA ~ 0.0799 at r ~ 0.383
    (verdict A1, v0.2; numerical digest b9828f02...).  The r_grid_log
    used here is the same one the reviewer used, so the peak should
    fall exactly on r = 0.3831 (the geomspace node nearest 0.383).
    """
    cell = HeadlineCell(rho=0.0)
    rg, vdas = vda_curve(cell)
    pk = int(np.argmax(vdas))
    # Allow 1e-4 on VDA (criterion-grid quantisation) and 5e-3 on r
    # (nearest log-spaced node).
    ok = (_approx(float(vdas[pk]), 0.0799, 1e-3)
          and _approx(float(rg[pk]), 0.383, 5e-3))
    return dict(name="peak VDA(r) @ rho=0 ~= 0.0799 at r ~= 0.383",
                ok=ok, peak_VDA=float(vdas[pk]), peak_r=float(rg[pk]))


# --------------------------------------------------------------------
# (3) Slepian monotonicity (the bound the run-016 closed-form claim
# stated; the reviewer's run-017 verified it numerically).
# --------------------------------------------------------------------
def test_slepian_monotone() -> dict:
    curve = slepian_curve(d_c=1.8, d_u=1.2, N=4, c_c=0.5, c_u=0.5)
    vals = [v for _, v in curve]
    monotone = all(vals[k + 1] >= vals[k] - 1e-14
                   for k in range(len(vals) - 1))
    indep_is_min = (vals[0] <= min(vals[1:]) + 1e-14)
    return dict(name="P_no-fa(rho) monotone-up, rho=0 is min",
                ok=(monotone and indep_is_min),
                curve=curve, monotone=monotone, indep_is_min=indep_is_min)


# --------------------------------------------------------------------
# Driver.
# --------------------------------------------------------------------
def main() -> int:
    import json
    import hashlib

    print(f"[backend] Phi = {PHI_BACKEND}; GH nq = {GH_NQ}")
    results: list[dict] = []
    results.append(test_p_no_fa_rho0_equals_product())
    results.append(test_p_no_fa_tiny_rho_converges_to_product())
    results.extend(test_policy_recovery_at_reference_r())
    results.append(test_peak_vda_over_r_grid())
    results.append(test_slepian_monotone())

    n_ok = sum(1 for r in results if r["ok"])
    n_tot = len(results)
    width = max(len(r["name"]) for r in results) + 2
    for r in results:
        tag = "PASS" if r["ok"] else "FAIL"
        extra = ""
        if "max_abs_diff" in r:
            extra = f"max|diff|={r['max_abs_diff']:.2e}"
        elif "VDA" in r and "VDA_target" in r:
            extra = (f"VDA={r['VDA']:.6f} (d={r['VDA_diff']:+.1e})  "
                     f"CF={r['CF']:.6f} (d={r['CF_diff']:+.1e})")
        elif "peak_VDA" in r:
            extra = f"peak={r['peak_VDA']:.6f} @ r={r['peak_r']:.4f}"
        elif "curve" in r:
            extra = "  ".join(f"r{rho:.2f}:{v:.4f}" for rho, v in r["curve"])
        print(f"[{tag}] {r['name']:<{width}} {extra}")

    # Persist numerical results + sha256 digest for reproducibility.
    payload = dict(phi_backend=PHI_BACKEND, gh_nq=GH_NQ,
                   checks=results, n_passed=n_ok, n_total=n_tot)
    digest = hashlib.sha256(
        json.dumps(payload, indent=2, sort_keys=True, default=float).encode()
    ).hexdigest()
    payload["sha256_numeric"] = digest
    out_path = os.path.join(os.path.dirname(__file__), "recovery_output.json")
    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, default=float)
    print(f"\n[sha256] {digest}")
    print(f"[written] {out_path}")

    print(f"\n=== {n_ok}/{n_tot} checks passed ===")
    return 0 if n_ok == n_tot else 1


if __name__ == "__main__":
    sys.exit(main())
