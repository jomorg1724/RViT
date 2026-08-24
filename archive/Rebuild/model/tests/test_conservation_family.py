"""
tests/test_conservation_family.py — the A3 conservation-family contract.

Surface contract for the cons_p parameter introduced in rb-015
(Rebuild/model/core.py).  Three layers of recovery are checked.

(1) FAMILY IDENTITIES.  For any (r > 0, p in R):
      beta(r, p) / gamma(r, p) = r      exactly (asymmetry ratio fixed).
      M_p(beta, gamma) = 1               to machine tolerance (conservation).
      beta(1, p) = gamma(1, p) = 1       exactly (symmetric-corner identity;
                                                 C5 result is conservation
                                                 -form-invariant).

(2) ADDITIVE (p = 1) BYTE-EXACT RECOVERY.  The rebuilt module's default
    cons_p = 1.0 must reproduce the inherited additive form
    beta = 2r/(r+1), gamma = 2/(r+1) *bit-for-bit*, and policies() with
    cell.cons_p = 1.0 must reproduce the rb-001 reviewer-pinned numbers
    (REVIEWER_TARGETS_RHO0 from test_recovery.py) to zero diff.  The
    cons_p = 1.0 path in beta_gamma() literally returns the inherited
    expressions (no `**` operator), so the recovery is binary.

(3) MULTIPLICATIVE (p = 0) RECOVERY VS REVIEWER A3.  The reviewer's
    Critique/replications/A3--multiplicative-conservation/output/results.json
    `block_c2_c1.families.multiplicative` block records VDA, CF, R_P1,
    R_P4 across the 21-point r-grid at the C2 headline regime (N=4,
    d'_max=2, f_0=0.5, h=sqrt, V=0.5, v=5, variant A).  With cons_p =
    0.0, the rebuilt policies() must reproduce those numbers to within a
    ULP-level tolerance (1e-5 on VDA/CF/R; the reviewer used the paper's
    A&S 7.1.26 Phi backend, the rebuilt module uses scipy.special.ndtr,
    and the difference is a known ULP-level reordering — same precedent
    as rb-003 CF recovery max|d|=1.47e-6).

A failing test invalidates every downstream A3-band claim.  Run before
any A3 simulation (RB-019) or §extensions manuscript section is wired.

Run:
    cd Rebuild/
    python3 -m model.tests.test_conservation_family
or  python3 model/tests/test_conservation_family.py
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_REBUILD_ROOT = _HERE.parent.parent.parent  # .../Rebuild/
if str(_REBUILD_ROOT) not in sys.path:
    sys.path.insert(0, str(_REBUILD_ROOT))

import numpy as np  # noqa: E402

from model.core import (  # noqa: E402
    GH_NQ,
    HeadlineCell,
    PHI_BACKEND,
    beta_gamma,
    policies,
)


# --------------------------------------------------------------------
# Reviewer's logged multiplicative-family numbers (cons_p = 0 target).
#
# Source: Critique/replications/A3--multiplicative-conservation/output/
#         results.json, block_c2_c1.families.multiplicative.rows.
# Reference regime: N=4, d_max=2.0, f0=0.5, h=sqrt, V=0.5, v=5.0,
#                   variant A, rho=0.  Phi backend (reviewer): A&S
#                   7.1.26 numpy-vectorised.
# Tolerance picked at 1e-5 on VDA/CF/R: well above the cross-backend ULP
# noise floor (rb-003 saw max|d|=1.47e-6 at the same regime), well below
# any rounded-to-4-dp number the reviewer reports.
# --------------------------------------------------------------------
REVIEWER_TARGETS_P0 = {
    # r          : (VDA,            CF,             R_P1,           R_P4)
    0.100000:   (4.110735e-02, 9.166238e-01, 2.189689e+00, 1.696654e+00),
    0.316228:   (9.085281e-02, 8.326158e-01, 2.239434e+00, 1.696654e+00),  # mul peak
    0.398107:   (8.914419e-02, 8.133434e-01, 2.252295e+00, 1.696654e+00),
    1.000000:   (3.982502e-02, 7.282283e-01, 2.317239e+00, 1.696654e+00),  # sym corner
    3.162278:   (8.948227e-03, 6.109311e-01, 2.436389e+00, 1.696654e+00),
    10.000000:  (3.172290e-03, 5.067573e-01, 2.588456e+00, 1.696654e+00),
}

TOL_MUL = 1e-5

# Tolerance for the family identity checks (M_p == 1 and beta/gamma == r).
TOL_FAMILY = 1e-12


def _approx(a: float, b: float, tol: float) -> bool:
    return abs(a - b) <= tol


def _power_mean(beta: float, gamma: float, p: float) -> float:
    """M_p(beta, gamma) = ((beta^p + gamma^p)/2)^(1/p) for p != 0;
    sqrt(beta*gamma) at p = 0."""
    if abs(p) < 1e-12:
        return math.sqrt(beta * gamma)
    return ((beta ** p + gamma ** p) / 2.0) ** (1.0 / p)


# --------------------------------------------------------------------
# (1) Family identities.
# --------------------------------------------------------------------
def test_ratio_is_r_exactly() -> dict:
    """beta(r,p) / gamma(r,p) = r exactly, for any r > 0, any p."""
    rs = [0.1, 0.316228, 0.398, 1.0, 3.162, 10.0]
    ps = [-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0]
    max_diff = 0.0
    for r in rs:
        for p in ps:
            b, g = beta_gamma(r, p)
            d = abs((b / g) - r)
            if d > max_diff:
                max_diff = d
    return dict(name="beta(r,p)/gamma(r,p) = r exactly",
                ok=(max_diff <= TOL_FAMILY),
                max_abs_diff=max_diff)


def test_conservation_invariant() -> dict:
    """M_p(beta(r,p), gamma(r,p)) = 1 to machine tolerance."""
    rs = [0.1, 0.316228, 0.398, 1.0, 3.162, 10.0]
    ps = [-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0]
    max_diff = 0.0
    for r in rs:
        for p in ps:
            b, g = beta_gamma(r, p)
            mp = _power_mean(b, g, p)
            d = abs(mp - 1.0)
            if d > max_diff:
                max_diff = d
    return dict(name="M_p(beta, gamma) = 1",
                ok=(max_diff <= TOL_FAMILY),
                max_abs_diff=max_diff)


def test_symmetric_corner_invariant() -> dict:
    """beta(1, p) = gamma(1, p) = 1 for all p (C5 conservation-invariance)."""
    ps = [-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0]
    max_diff = 0.0
    for p in ps:
        b, g = beta_gamma(1.0, p)
        d = max(abs(b - 1.0), abs(g - 1.0))
        if d > max_diff:
            max_diff = d
    return dict(name="beta(1,p) = gamma(1,p) = 1 for all p",
                ok=(max_diff == 0.0),
                max_abs_diff=max_diff)


# --------------------------------------------------------------------
# (2) Additive (p = 1) byte-exact recovery.
# --------------------------------------------------------------------
def _legacy_additive(r: float) -> tuple[float, float]:
    """Pre-rb-015 additive form: beta=2r/(r+1), gamma=2/(r+1)."""
    return 2.0 * r / (r + 1.0), 2.0 / (r + 1.0)


def test_p1_byte_exact_vs_legacy() -> dict:
    """beta_gamma(r, p=1.0) returns the legacy additive numbers bit-for-bit.

    Required: this is the back-compat contract — every existing sim that
    calls beta_gamma(r) (implicit p=1) gets numerically identical
    output post-rb-015.
    """
    rs = [0.1, 0.125893, 0.158489, 0.199526, 0.251189, 0.316228, 0.398107,
          0.501187, 0.630957, 0.794328, 1.0, 1.258925, 1.584893, 1.995262,
          2.511886, 3.162278, 3.981072, 5.011872, 6.309573, 7.943282, 10.0]
    max_diff = 0.0
    for r in rs:
        b_new, g_new = beta_gamma(r, 1.0)
        b_old, g_old = _legacy_additive(r)
        d = max(abs(b_new - b_old), abs(g_new - g_old))
        if d > max_diff:
            max_diff = d
    return dict(name="beta_gamma(r,p=1) == legacy additive (byte-exact)",
                ok=(max_diff == 0.0),
                max_abs_diff=max_diff)


def test_policies_p1_default_unchanged() -> list[dict]:
    """policies() with default cons_p=1.0 reproduces rb-001 reviewer pins.

    These are the *same* numbers test_recovery.py REVIEWER_TARGETS_RHO0
    pins; if cons_p=1.0 is the genuine back-compat path, the diff is 0.
    """
    # Copied from test_recovery.py (do not import to avoid a hard
    # dependency between the two test scripts).
    PINS = {
        0.398: dict(VDA=0.07971892561151384, CF=0.8295190133917728,
                    R_P1=2.2414603355617007, R_P4=1.696653810304055),
        1.000: dict(VDA=0.03982512744634903, CF=0.7282279801682813,
                    R_P1=2.317238824377106,  R_P4=1.696653810304055),
        3.162: dict(VDA=0.00808898926330448, CF=0.6409382701716876,
                    R_P1=2.401756614042182,  R_P4=1.696653810304055),
    }
    cell = HeadlineCell(cons_p=1.0)
    out = []
    for r, tgt in PINS.items():
        p = policies(r, cell)
        ok = (_approx(p["VDA"], tgt["VDA"], 1e-12)
              and _approx(p["CF"], tgt["CF"], 1e-12)
              and _approx(p["R_P1"], tgt["R_P1"], 1e-12)
              and _approx(p["R_P4"], tgt["R_P4"], 1e-12))
        out.append(dict(name=f"policies(p=1) @ r={r}  vs  rb-001 pin",
                        ok=ok,
                        VDA=p["VDA"], VDA_diff=p["VDA"] - tgt["VDA"],
                        CF=p["CF"], CF_diff=p["CF"] - tgt["CF"],
                        R_P1=p["R_P1"], R_P1_diff=p["R_P1"] - tgt["R_P1"]))
    return out


# --------------------------------------------------------------------
# (3) Multiplicative (p = 0) recovery against the reviewer's A3 numbers.
# --------------------------------------------------------------------
def test_policies_p0_vs_reviewer_a3() -> list[dict]:
    """policies(p=0) reproduces reviewer's A3 multiplicative block.

    Tolerance TOL_MUL = 1e-5 (cross-backend ULP, see file docstring).
    """
    cell = HeadlineCell(cons_p=0.0)  # rho=0 is the default, regime matches reviewer
    out = []
    for r, (vda_t, cf_t, rp1_t, rp4_t) in REVIEWER_TARGETS_P0.items():
        p = policies(r, cell)
        ok = (_approx(p["VDA"], vda_t, TOL_MUL)
              and _approx(p["CF"], cf_t, TOL_MUL)
              and _approx(p["R_P1"], rp1_t, TOL_MUL)
              and _approx(p["R_P4"], rp4_t, TOL_MUL))
        out.append(dict(
            name=f"policies(p=0) @ r={r:.6f}  vs  reviewer A3-mul pin",
            ok=ok,
            VDA=p["VDA"], VDA_diff=p["VDA"] - vda_t,
            CF=p["CF"], CF_diff=p["CF"] - cf_t,
            R_P1=p["R_P1"], R_P1_diff=p["R_P1"] - rp1_t,
        ))
    return out


def test_p0_symmetric_corner_identity() -> dict:
    """At r=1 (the C5 symmetric centre), policies(p=0) and policies(p=1)
    must agree to floating-point identity.  Conservation form is
    invisible at r=1 because beta(1,p)=gamma(1,p)=1 for all p."""
    cell0 = HeadlineCell(cons_p=0.0)
    cell1 = HeadlineCell(cons_p=1.0)
    p0 = policies(1.0, cell0)
    p1 = policies(1.0, cell1)
    keys = ("VDA", "CF", "R_P1", "R_P2", "R_P3", "R_P4",
            "alpha_P1", "alpha_vb")
    diffs = {k: float(abs(p0[k] - p1[k])) for k in keys}
    max_diff = max(diffs.values())
    return dict(name="policies(p=0,r=1) == policies(p=1,r=1) (FP identity)",
                ok=(max_diff == 0.0),
                max_abs_diff=max_diff,
                diffs=diffs)


# --------------------------------------------------------------------
# Driver.
# --------------------------------------------------------------------
def main() -> int:
    print(f"[backend] Phi = {PHI_BACKEND}; GH nq = {GH_NQ}")
    results: list[dict] = []

    # (1) Family identities.
    results.append(test_ratio_is_r_exactly())
    results.append(test_conservation_invariant())
    results.append(test_symmetric_corner_invariant())

    # (2) Additive p=1 byte-exact recovery.
    results.append(test_p1_byte_exact_vs_legacy())
    results.extend(test_policies_p1_default_unchanged())

    # (3) Multiplicative p=0 recovery vs reviewer A3.
    results.extend(test_policies_p0_vs_reviewer_a3())
    results.append(test_p0_symmetric_corner_identity())

    n_ok = sum(1 for r in results if r["ok"])
    n_tot = len(results)
    width = max(len(r["name"]) for r in results) + 2
    for r in results:
        tag = "PASS" if r["ok"] else "FAIL"
        extra = ""
        if "max_abs_diff" in r and "VDA" not in r:
            extra = f"max|diff|={r['max_abs_diff']:.2e}"
        elif "VDA" in r and "VDA_diff" in r:
            extra = (f"VDA={r['VDA']:.6f} (d={r['VDA_diff']:+.1e})  "
                     f"CF={r['CF']:.6f} (d={r['CF_diff']:+.1e})  "
                     f"R_P1={r['R_P1']:.6f} (d={r['R_P1_diff']:+.1e})")
        print(f"[{tag}] {r['name']:<{width}} {extra}")

    payload = dict(phi_backend=PHI_BACKEND, gh_nq=GH_NQ,
                   reviewer_targets_p0=REVIEWER_TARGETS_P0,
                   tol_family=TOL_FAMILY, tol_mul=TOL_MUL,
                   checks=results, n_passed=n_ok, n_total=n_tot)
    digest = hashlib.sha256(
        json.dumps(payload, indent=2, sort_keys=True, default=float).encode()
    ).hexdigest()
    payload["sha256_numeric"] = digest

    out_path = os.path.join(os.path.dirname(__file__),
                            "conservation_family_output.json")
    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, default=float)
    print(f"\n[sha256] {digest}")
    print(f"[written] {out_path}")
    print(f"\n=== {n_ok}/{n_tot} checks passed ===")
    return 0 if n_ok == n_tot else 1


if __name__ == "__main__":
    sys.exit(main())
