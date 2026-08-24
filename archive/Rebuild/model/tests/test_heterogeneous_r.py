"""
tests/test_heterogeneous_r.py — the homogeneous-r recovery contract for
the heterogeneous-r d'-map (A2/A8 model increment, rb-019).

This is the contract every A2/A8 simulation will be built against.
Under uniform r_vec = (r, r, ..., r) and the canonical homogeneous
allocation alloc = (alpha, (1-alpha)/(N-1), ..., (1-alpha)/(N-1)), the
new d_prime_hetero(...) primitive must reproduce the legacy single-r
d_prime_asym(alpha, r, ...) (d_c, d_u) pair to BINARY equality.

Three test surfaces.

(1) HOMOGENEOUS-R RECOVERY (alpha grid).  Across the full default alpha
    grid (1/N to 1 step 0.005), six representative r values
    {0.1, 0.3, 0.398, 1.0, 3.162, 10.0}, three conservation orders
    p in {0.0, 0.5, 1.0}, and h in {"sqrt", "linear"}: confirm
    d_prime_hetero returns [d_c, d_u, d_u, ..., d_u] with d_c, d_u
    BINARY-equal to d_prime_asym(alpha, r, ...).  The max-abs-diff
    across all sampled (alpha, r, p, h) cells must be exactly 0.0.

(2) HOMOGENEOUS-R RECOVERY (inversion regime).  Across the inversion-
    regime alpha grid (1/(2N) to 1/N step 0.01), same r/p/h selection:
    confirm the per-slot gain/loss branch correctly mirrors
    d_prime_asym's else-branch (cued slot in loss-branch -> gamma;
    uncued slots in gain-branch -> beta), again to BINARY equality.

(3) HETEROGENEOUS-R SANITY.  The CR-048 / run-015 "spread=0" validation
    at the headline cell (V=0.5, v=5, N=4, d'_max=2, f_0=0.5, h=sqrt)
    at r=0.398, alpha=0.5: the legacy (d_c, d_u) and the new d_prime
    array must agree.  Spread=0.3 produces a non-uniform d' vector
    whose mean over the uncued slots equals d_u(alpha=0.5,
    r=mean_uncued_r) to a tolerance reflecting the non-linearity of
    beta_gamma in r (this is a smoke test for direction-of-effect, not
    a recovery contract).

A failing recovery test invalidates every downstream A2/A8 simulation
that depends on the heterogeneous-r d'-map.  Run before any new A2/A8
simulation is wired in.

Run:
    python3 Rebuild/model/tests/test_heterogeneous_r.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

# Allow running as a script: `python3 Rebuild/model/tests/test_heterogeneous_r.py`
_HERE = Path(__file__).resolve()
_REBUILD_ROOT = _HERE.parent.parent.parent  # .../Rebuild/
if str(_REBUILD_ROOT) not in sys.path:
    sys.path.insert(0, str(_REBUILD_ROOT))

import numpy as np

from model.core import (  # noqa: E402
    PHI_BACKEND,
    beta_gamma,
    canonical_alloc,
    d_prime_asym,
    d_prime_hetero,
    default_alpha_grid,
    make_h,
)


# --------------------------------------------------------------------
# Test configuration.
# --------------------------------------------------------------------
N = 4
D_MAX = 2.0
F0 = 0.5
R_VALUES = (0.1, 0.3, 0.398, 1.0, 3.162, 10.0)        # C2/C1 reference points
P_VALUES = (0.0, 0.5, 1.0)                             # A3 conservation orders
H_NAMES = ("sqrt", "linear")                           # transfer-function variants


def _approx(a: float, b: float, tol: float) -> bool:
    return abs(a - b) <= tol


# --------------------------------------------------------------------
# (1) Homogeneous-r recovery across the full alpha >= 1/N grid.
# --------------------------------------------------------------------
def test_recovery_alpha_grid() -> dict:
    """Binary-equal (d_c, d_u) recovery across the default alpha grid."""
    alpha_grid = default_alpha_grid(N)
    max_diff = 0.0
    n_cells = 0
    failed: list[dict] = []
    for h_name in H_NAMES:
        h = make_h(h_name)
        for p in P_VALUES:
            for r in R_VALUES:
                for alpha in alpha_grid:
                    d_c_legacy, d_u_legacy = d_prime_asym(
                        float(alpha), r, D_MAX, F0, h, N, p)
                    alloc = canonical_alloc(float(alpha), N)
                    d_vec = d_prime_hetero(alloc, r, D_MAX, F0, h, N, p)
                    # Slot 0 = cued; slots 1..N-1 = uncued (homogeneous).
                    diff_c = abs(float(d_vec[0]) - d_c_legacy)
                    diffs_u = [abs(float(d_vec[i]) - d_u_legacy)
                               for i in range(1, N)]
                    cell_max = max([diff_c, *diffs_u])
                    if cell_max > max_diff:
                        max_diff = cell_max
                    n_cells += 1
                    if cell_max > 0.0:
                        failed.append(dict(
                            h=h_name, p=p, r=r, alpha=float(alpha),
                            diff_c=diff_c, diffs_u=diffs_u,
                            d_c_legacy=d_c_legacy, d_u_legacy=d_u_legacy,
                            d_vec=d_vec.tolist()))
    ok = (max_diff == 0.0)
    return dict(name=f"d_prime_hetero == d_prime_asym (binary) on alpha>=1/N grid "
                     f"[{n_cells} cells; h={list(H_NAMES)}, p={list(P_VALUES)}, r={list(R_VALUES)}]",
                ok=ok, max_abs_diff=max_diff, n_cells=n_cells,
                n_failed=len(failed),
                failures_head=failed[:3])  # truncated on failure for debuggability


# --------------------------------------------------------------------
# (2) Homogeneous-r recovery in the inversion regime (alpha < 1/N).
# --------------------------------------------------------------------
def test_recovery_inversion_branch() -> dict:
    """Per-slot gain/loss branch correctly mirrors d_prime_asym's else-branch."""
    # alpha in (0, 1/N) — the inversion regime (cued allocation BELOW
    # the uniform baseline).  Mirrors the C4 anti-cue regime; the
    # rebuild's reported sims operate on alpha >= 1/N, but the d'-map
    # must remain consistent in the inversion branch for completeness.
    alpha_grid = np.round(np.arange(1.0 / (2 * N), 1.0 / N - 1e-9, 0.01), 6)
    max_diff = 0.0
    n_cells = 0
    failed: list[dict] = []
    for h_name in H_NAMES:
        h = make_h(h_name)
        for p in P_VALUES:
            for r in R_VALUES:
                for alpha in alpha_grid:
                    d_c_legacy, d_u_legacy = d_prime_asym(
                        float(alpha), r, D_MAX, F0, h, N, p)
                    alloc = canonical_alloc(float(alpha), N)
                    d_vec = d_prime_hetero(alloc, r, D_MAX, F0, h, N, p)
                    diff_c = abs(float(d_vec[0]) - d_c_legacy)
                    diffs_u = [abs(float(d_vec[i]) - d_u_legacy)
                               for i in range(1, N)]
                    cell_max = max([diff_c, *diffs_u])
                    if cell_max > max_diff:
                        max_diff = cell_max
                    n_cells += 1
                    if cell_max > 0.0:
                        failed.append(dict(
                            h=h_name, p=p, r=r, alpha=float(alpha),
                            diff_c=diff_c, diffs_u=diffs_u,
                            d_c_legacy=d_c_legacy, d_u_legacy=d_u_legacy,
                            d_vec=d_vec.tolist()))
    ok = (max_diff == 0.0)
    return dict(name=f"d_prime_hetero == d_prime_asym (binary) on alpha<1/N (inversion) grid "
                     f"[{n_cells} cells]",
                ok=ok, max_abs_diff=max_diff, n_cells=n_cells,
                n_failed=len(failed),
                failures_head=failed[:3])


# --------------------------------------------------------------------
# (3) Scalar broadcast: scalar r is equivalent to a uniform N-vector.
# --------------------------------------------------------------------
def test_scalar_r_broadcast() -> dict:
    """Passing a scalar r_vec is identical to passing a uniform N-vector."""
    h = make_h("sqrt")
    max_diff = 0.0
    n_cells = 0
    for p in P_VALUES:
        for r in R_VALUES:
            for alpha in (0.25, 0.5, 0.75, 1.0):
                alloc = canonical_alloc(float(alpha), N)
                d_scalar = d_prime_hetero(alloc, r, D_MAX, F0, h, N, p)
                d_vector = d_prime_hetero(alloc, [r] * N, D_MAX, F0, h, N, p)
                diff = float(np.max(np.abs(d_scalar - d_vector)))
                if diff > max_diff:
                    max_diff = diff
                n_cells += 1
    ok = (max_diff == 0.0)
    return dict(name=f"scalar r_vec == uniform N-vector r_vec (binary) [{n_cells} cells]",
                ok=ok, max_abs_diff=max_diff, n_cells=n_cells)


# --------------------------------------------------------------------
# (4) CR-048 / run-015 headline-cell "spread=0" sanity: the heterogeneous
# code reduces to the single-r model at the headline cell exactly.
# --------------------------------------------------------------------
def test_cr048_spread0_headline() -> dict:
    """Headline cell: spread=0 r-vector reproduces the legacy (d_c, d_u)."""
    h = make_h("sqrt")
    r_cued, alpha = 0.398, 0.5
    d_c_legacy, d_u_legacy = d_prime_asym(alpha, r_cued, D_MAX, F0, h, N, 1.0)
    # Build CR-048-style spread=0 vector: cued + (N-1) uncued, all = r_cued.
    r_vec_homo = np.array([r_cued, r_cued, r_cued, r_cued])
    alloc = canonical_alloc(alpha, N)
    d_vec = d_prime_hetero(alloc, r_vec_homo, D_MAX, F0, h, N, 1.0)
    diff_c = abs(float(d_vec[0]) - d_c_legacy)
    diffs_u = [abs(float(d_vec[i]) - d_u_legacy) for i in range(1, N)]
    max_diff = max([diff_c, *diffs_u])
    ok = (max_diff == 0.0)
    return dict(name="CR-048 headline (r=0.398, alpha=0.5, spread=0) -> binary recovery",
                ok=ok, max_abs_diff=max_diff,
                d_c_legacy=d_c_legacy, d_u_legacy=d_u_legacy,
                d_vec=d_vec.tolist())


# --------------------------------------------------------------------
# (5) Heterogeneous-r smoke: spread > 0 produces a non-uniform uncued
# d' vector with the EXPECTED SIGN.
#
# At alpha = 0.5 > 1/N, every uncued slot is in the loss branch, so
# s_i = gamma(r_i, p=1) = 2/(r_i + 1), monotone-decreasing in r_i.  The
# departure d'_max f(a_i) - d'_base = d'_max [f(0.5/3) - f(1/4)] is the
# SAME for every uncued slot (same a_i = (1-alpha)/(N-1)), and it is
# NEGATIVE (f is monotone-increasing, 0.5/3 < 1/4).  Therefore a SMALL
# gamma_i (= LARGE r_i) gives a LESS-NEGATIVE departure-contribution
# and hence a LARGER d'_u_i.  Smoke test: increasing r_i on an uncued
# slot must raise that slot's d'_u_i (not decrease it).  Conversely on
# the cued slot (alpha > 1/N, gain branch) a positive departure scaled
# by beta = 2r/(r+1) means larger r_c -> larger d'_c.
# --------------------------------------------------------------------
def test_heterogeneous_sign_smoke() -> dict:
    """Spread on r_vec -> non-uniform d'_u with the predicted sign."""
    h = make_h("sqrt")
    alpha = 0.5
    spread = 0.3
    # CR-048 ordering: uncued = r_cued * {1-s, 1, 1+s}; cued = r_cued.
    r_cued = 0.398
    r_vec = np.array([r_cued,
                      r_cued * (1.0 - spread),
                      r_cued,
                      r_cued * (1.0 + spread)])
    alloc = canonical_alloc(alpha, N)
    d_vec = d_prime_hetero(alloc, r_vec, D_MAX, F0, h, N, 1.0)
    # Expectation: d_vec[2] equals the single-r d_u(r=r_cued, alpha=0.5),
    # d_vec[3] (largest r_i) > d_vec[2] > d_vec[1] (smallest r_i).
    d_c_legacy, d_u_legacy = d_prime_asym(alpha, r_cued, D_MAX, F0, h, N, 1.0)
    middle_matches = (float(d_vec[2]) == d_u_legacy)
    monotone = float(d_vec[1]) < float(d_vec[2]) < float(d_vec[3])
    cued_matches = (float(d_vec[0]) == d_c_legacy)  # cued r unchanged -> exact
    ok = monotone and middle_matches and cued_matches
    return dict(name="heterogeneous-r smoke: spread=0.3 -> sign(d'_u_i) as predicted",
                ok=ok,
                d_vec=d_vec.tolist(), d_u_legacy=d_u_legacy, d_c_legacy=d_c_legacy,
                middle_matches=middle_matches, monotone=monotone,
                cued_matches=cued_matches)


# --------------------------------------------------------------------
# Driver.
# --------------------------------------------------------------------
def main() -> int:
    print(f"[backend] Phi = {PHI_BACKEND}")
    results: list[dict] = []
    results.append(test_recovery_alpha_grid())
    results.append(test_recovery_inversion_branch())
    results.append(test_scalar_r_broadcast())
    results.append(test_cr048_spread0_headline())
    results.append(test_heterogeneous_sign_smoke())

    n_ok = sum(1 for r in results if r["ok"])
    n_tot = len(results)
    width = max(len(r["name"]) for r in results) + 2
    for r in results:
        tag = "PASS" if r["ok"] else "FAIL"
        extra = ""
        if "max_abs_diff" in r:
            extra = f"max|diff|={r['max_abs_diff']:.2e}"
            if "n_cells" in r:
                extra += f"  n_cells={r['n_cells']}"
        elif "d_vec" in r:
            extra = f"d_vec={r['d_vec']}"
        print(f"[{tag}] {r['name']:<{width}} {extra}")

    payload = dict(phi_backend=PHI_BACKEND, checks=results,
                   n_passed=n_ok, n_total=n_tot)
    digest = hashlib.sha256(
        json.dumps(payload, indent=2, sort_keys=True, default=float).encode()
    ).hexdigest()
    payload["sha256_numeric"] = digest
    out_path = os.path.join(os.path.dirname(__file__), "heterogeneous_r_output.json")
    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, default=float)
    print(f"\n[sha256] {digest}")
    print(f"[written] {out_path}")

    print(f"\n=== {n_ok}/{n_tot} checks passed ===")
    return 0 if n_ok == n_tot else 1


if __name__ == "__main__":
    sys.exit(main())
