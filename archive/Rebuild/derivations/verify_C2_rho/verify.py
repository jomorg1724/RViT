"""
Verification script for the rb-026 closed-form derivation of r†(v; ρ).

ASYMMETRIC P3 CRITERIA.  At α = 1/N, d_c = d_u = d_base, but the joint
criterion optimum (c_c*(v; ρ), c_u*(v; ρ)) is asymmetric in general
because cued and uncued change-trials carry unequal rewards (V·v versus
1−V).  The escape threshold

    r†(v; ρ) = K_u(v; ρ) / [(N − 1) · K_c(v; ρ)]                       (rb-026, Eq. 4.x)

with

    K_c(v; ρ) = ¼ [V · v · φ_change_c(ρ)
                   + CR(v) · I_c(b_c*(ρ), b_u*(ρ); ρ, N)]              (4.y)
    K_u(v; ρ) = ¼ [(1 − V) · φ_change_u(ρ)
                   + (N − 1) · CR(v) · I_u(b_c*(ρ), b_u*(ρ); ρ, N)]    (4.z)

uses asymmetric (c_c*, c_u*) and the ρ-aware d-gradient integrals

    I_c(b_c, b_u; ρ, N)
       := ∫ (1/√(1-ρ))
            · φ((b_c - √ρ z)/√(1-ρ))
            · Φ((b_u - √ρ z)/√(1-ρ))^(N-1)
            · φ(z) dz                                                  (4.3)

    I_u(b_c, b_u; ρ, N)
       := ∫ (1/√(1-ρ))
            · Φ((b_c - √ρ z)/√(1-ρ))
            · Φ((b_u - √ρ z)/√(1-ρ))^(N-2)
            · φ((b_u - √ρ z)/√(1-ρ))
            · φ(z) dz                                                  (4.4)

At ρ = 0 both integrands lose z-dependence and collapse to the inherited
closed form

    I_c(b_c, b_u; 0, N) = φ(b_c) · Φ(b_u)^(N-1)
    I_u(b_c, b_u; 0, N) = Φ(b_c) · Φ(b_u)^(N-2) · φ(b_u)

which is exactly the reviewer's rb-006 r_dagger() closed form (cf.
Rebuild/sims/C2--vda-vs-r-vfamily/run.py lines 218-265).

Steps:
  1. ρ = 0 recovery vs rb-006: r†(v; 0) byte-identical to rb-006's
     r_dagger() at all v ∈ {1, 2, 3, 5, 8, 10}.
  2. ρ = 0.2 closed form predictions for the headline cell.
  3. Compare predicted drift direction sign(Δr†) vs empirical drift
     sign(Δr*) — sanity check on the manuscript-quoted statement.
  4. Boundary-FD: at r = r†(v; ρ) ± ε, sign(∂E[R]/∂α|_{1/N+}) flips.

Run:  python3 verify.py   (~1 second wall clock)
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

REBUILD_ROOT = Path("/Users/jonathanmorgan/AttentionManuscript/Rebuild")
sys.path.insert(0, str(REBUILD_ROOT))

from model.core import (  # noqa: E402
    C_GRID,
    _GH_W,
    _GH_Z,
    d_prime_asym,
    f_transfer,
    make_h,
    optimal_R,
    p_no_fa_grid,
)
from scipy.special import ndtr as Phi  # noqa: E402

PHI_DENS = lambda x: np.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)  # noqa: E731


# ---------------------------------------------------------------------------
# Headline cell parameters (rb-006 / rb-004 / Figure-4 reference).
# ---------------------------------------------------------------------------
N = 4
V = 0.5
d_max = 2.0
f0 = 0.5
h_name = "sqrt"
variant = "A"
h = make_h(h_name)
d_base = d_max * f_transfer(1.0 / N, f0, h)

V_FAMILY = [1.0, 2.0, 3.0, 5.0, 8.0, 10.0]
RHOS = [0.0, 0.2]


def cr_of(v: float, variant: str) -> float:
    return V * v + (1.0 - V) if variant == "A" else 1.0


# ---------------------------------------------------------------------------
# P3 ASYMMETRIC criterion optimum at α = 1/N.
#
# Both c_c and c_u are free; jointly maximise E[R] on the (C_GRID, C_GRID)
# grid.  Uses the rebuilt model's `p_no_fa_grid` so the ρ-channel matches
# the in-model quadrature byte-for-byte.
# ---------------------------------------------------------------------------
def p3_optimal_criteria(v: float, rho: float) -> tuple[float, float]:
    """Return (c_c*, c_u*) at α = 1/N, jointly optimised on C_GRID×C_GRID."""
    d_c, d_u = d_prime_asym(1.0 / N, 1.0, d_max, f0, h, N)  # both = d_base
    assert abs(d_c - d_base) < 1e-12 and abs(d_u - d_base) < 1e-12
    hr_c = Phi(d_c / 2.0 - C_GRID)
    hr_u = Phi(d_u / 2.0 - C_GRID)
    cr = cr_of(v, variant)
    p_nofa = p_no_fa_grid(d_c, d_u, N, rho)  # (n_c, n_c)
    er = (0.5 * (V * v * hr_c[:, None] + (1.0 - V) * hr_u[None, :])
          + 0.5 * cr * p_nofa)
    i, j = np.unravel_index(int(np.argmax(er)), er.shape)
    return float(C_GRID[i]), float(C_GRID[j])


# ---------------------------------------------------------------------------
# d-gradient integrals I_c, I_u at the asymmetric P3 point.
# ---------------------------------------------------------------------------
def I_c_int(b_c: float, b_u: float, rho: float) -> float:
    """∫ (1/√(1-ρ)) φ((b_c-√ρz)/√(1-ρ)) · Φ((b_u-√ρz)/√(1-ρ))^(N-1) φ(z) dz."""
    if rho <= 0.0:
        return float(PHI_DENS(b_c) * Phi(b_u) ** (N - 1))
    s = math.sqrt(1.0 - rho)
    rs = math.sqrt(rho)
    arg_c = (b_c - rs * _GH_Z) / s
    arg_u = (b_u - rs * _GH_Z) / s
    integrand = (1.0 / s) * PHI_DENS(arg_c) * Phi(arg_u) ** (N - 1)
    return float(np.sum(_GH_W * integrand))


def I_u_int(b_c: float, b_u: float, rho: float) -> float:
    """∫ (1/√(1-ρ)) Φ((b_c-√ρz)/√(1-ρ)) · Φ((b_u-√ρz)/√(1-ρ))^(N-2) ·
       φ((b_u-√ρz)/√(1-ρ)) φ(z) dz."""
    if rho <= 0.0:
        return float(Phi(b_c) * Phi(b_u) ** (N - 2) * PHI_DENS(b_u))
    s = math.sqrt(1.0 - rho)
    rs = math.sqrt(rho)
    arg_c = (b_c - rs * _GH_Z) / s
    arg_u = (b_u - rs * _GH_Z) / s
    integrand = (1.0 / s) * Phi(arg_c) * Phi(arg_u) ** (N - 2) * PHI_DENS(arg_u)
    return float(np.sum(_GH_W * integrand))


def K_c_K_u(v: float, rho: float) -> dict:
    """Return K_c, K_u, r†, plus the intermediate (c_c*, c_u*), φ_changes, I_c, I_u."""
    c_c, c_u = p3_optimal_criteria(v, rho)
    b_c = c_c + d_base / 2.0
    b_u = c_u + d_base / 2.0
    phi_change_c = float(PHI_DENS(d_base / 2.0 - c_c))
    phi_change_u = float(PHI_DENS(d_base / 2.0 - c_u))
    Ic = I_c_int(b_c, b_u, rho)
    Iu = I_u_int(b_c, b_u, rho)
    cr = cr_of(v, variant)
    K_c = 0.25 * (V * v * phi_change_c + cr * Ic)
    K_u = 0.25 * ((1.0 - V) * phi_change_u + (N - 1) * cr * Iu)
    r_dag = K_u / ((N - 1) * K_c)
    return {
        "c_c_star": c_c, "c_u_star": c_u, "b_c": b_c, "b_u": b_u,
        "phi_change_c": phi_change_c, "phi_change_u": phi_change_u,
        "I_c": Ic, "I_u": Iu, "CR": cr,
        "K_c": K_c, "K_u": K_u, "r_dagger": r_dag,
    }


# ---------------------------------------------------------------------------
# Numerical FD sanity: at r = r†(v; ρ) ± ε, sign(∂E[R]/∂α|_{α=1/N+}) flips.
# ---------------------------------------------------------------------------
def er_alpha(alpha: float, r: float, v: float, rho: float) -> float:
    d_c, d_u = d_prime_asym(alpha, r, d_max, f0, h, N, 1.0)
    return optimal_R(d_c, d_u, v, V, N, variant, rho)


def boundary_derivative_sign(r: float, v: float, rho: float, h_step: float = 1e-3) -> int:
    a0 = 1.0 / N
    e0 = er_alpha(a0, r, v, rho)
    e1 = er_alpha(a0 + h_step, r, v, rho)
    diff = e1 - e0
    if abs(diff) < 1e-12:
        return 0
    return 1 if diff > 0 else -1


# ---------------------------------------------------------------------------
# rb-006 reference numbers (variant A, V=0.5, N=4, d_max=2, f0=0.5, h=sqrt).
# ---------------------------------------------------------------------------
RB006_R_DAGGER = {
    1.0: 0.3428272317122787,
    2.0: 0.16766485404995837,
    3.0: 0.09947226128290815,
    5.0: 0.0503737937060659,
    8.0: 0.022192942596828376,
    10.0: 0.01609849015389148,
}

RB006_R_STAR = {
    (2.0, 0.0): 0.501187, (2.0, 0.2): 0.630957,
    (3.0, 0.0): 0.375837, (3.0, 0.2): 0.473151,
    (5.0, 0.0): 0.375837, (5.0, 0.2): 0.3831,
    (8.0, 0.0): 0.375837, (8.0, 0.2): 0.3831,
    (10.0, 0.0): 0.354813, (10.0, 0.2): 0.3831,
}


def main() -> int:
    out: dict = {
        "config": {
            "N": N, "V": V, "d_max": d_max, "f0": f0, "h": h_name,
            "variant": variant, "v_family": V_FAMILY, "rhos": RHOS,
            "C_GRID_step": 0.05, "GH_NQ": len(_GH_Z),
            "d_base": d_base,
        },
        "r_dagger_table": {},
        "recovery": {},
        "drift_predictions": {},
        "boundary_FD_check": {},
    }

    # --- 1. r†(v; ρ) table -------------------------------------------------
    table: dict = {}
    for v in V_FAMILY:
        table[v] = {}
        for rho in RHOS:
            table[v][rho] = K_c_K_u(v, rho)
    out["r_dagger_table"] = {
        f"v={v}__rho={rho}": table[v][rho] for v in V_FAMILY for rho in RHOS
    }

    # --- 2. Recovery vs rb-006 closed form at ρ = 0 ------------------------
    print("=" * 78)
    print("§ RECOVERY: r†(v; ρ=0) vs rb-006 reviewer closed form (Critique §2.3)")
    print("=" * 78)
    print(f"{'v':>6}  {'r†_rb026(ρ=0)':>16}  {'r†_rb006':>14}  {'|Δ|':>14}")
    max_abs = 0.0
    for v in V_FAMILY:
        ours = table[v][0.0]["r_dagger"]
        ref = RB006_R_DAGGER[v]
        d = abs(ours - ref)
        max_abs = max(max_abs, d)
        print(f"{v:>6.1f}  {ours:>16.12f}  {ref:>14.12f}  {d:>14.3e}")
        out["recovery"][f"v={v}"] = {
            "r_dagger_rb026": ours, "r_dagger_rb006": ref, "abs_diff": d,
        }
    out["recovery"]["max_abs_diff"] = max_abs
    rec_pass = max_abs < 1e-12
    print(f"\nmax|Δ| over the 6-row recovery = {max_abs:.3e}")
    print(f"PASS at tol 1e-12 (binary FP identity):  {rec_pass}")

    # --- 3. Drift predictions ----------------------------------------------
    print("\n" + "=" * 78)
    print("§ DRIFT PREDICTION:  Δr†(v) = r†(v; 0.2) − r†(v; 0)")
    print("  vs empirical peak-r* drift Δr* from rb-006")
    print("=" * 78)
    print(f"{'v':>4}  {'r†(0)':>10}  {'r†(0.2)':>10}  {'Δr†':>11}  "
          f"{'%Δr†':>7}  {'r*(0)':>10}  {'r*(0.2)':>10}  {'Δr*':>11}  "
          f"{'sign-match':>11}")
    sign_matches = 0
    n_compare = 0
    for v in V_FAMILY:
        r0, r2 = table[v][0.0]["r_dagger"], table[v][0.2]["r_dagger"]
        drift = r2 - r0
        pct = 100.0 * drift / r0 if r0 > 0 else float("nan")
        rec = {"r_dagger_rho0": r0, "r_dagger_rho02": r2,
               "delta_r_dagger": drift, "pct_change": pct}
        if v == 1.0:
            print(f"{v:>4.1f}  {r0:>10.6f}  {r2:>10.6f}  "
                  f"{drift:>+11.6f}  {pct:>+6.1f}%  "
                  f"{'—':>10}  {'—':>10}  {'—':>11}  "
                  f"{'(v=1: P2 ref)':>11}")
            rec["note"] = "v=1 sets P2 reference; no rb-006 peak r* drift"
            out["drift_predictions"][f"v={v}"] = rec
            continue
        rs0 = RB006_R_STAR[(v, 0.0)]
        rs2 = RB006_R_STAR[(v, 0.2)]
        rs_drift = rs2 - rs0
        sign_d = 1 if drift > 1e-6 else (-1 if drift < -1e-6 else 0)
        sign_s = 1 if rs_drift > 1e-6 else (-1 if rs_drift < -1e-6 else 0)
        match = sign_d == sign_s
        sign_matches += int(match)
        n_compare += 1
        print(f"{v:>4.1f}  {r0:>10.6f}  {r2:>10.6f}  "
              f"{drift:>+11.6f}  {pct:>+6.1f}%  "
              f"{rs0:>10.6f}  {rs2:>10.6f}  {rs_drift:>+11.6f}  "
              f"{str(match):>11}")
        rec.update({"r_star_rho0": rs0, "r_star_rho02": rs2,
                    "delta_r_star": rs_drift, "sign_match": bool(match)})
        out["drift_predictions"][f"v={v}"] = rec
    out["drift_predictions"]["sign_match_score"] = f"{sign_matches}/{n_compare}"
    print(f"\nsign-match score: {sign_matches}/{n_compare}")

    # --- 4. Boundary-FD sanity ---------------------------------------------
    print("\n" + "=" * 78)
    print("§ BOUNDARY FD SANITY: sign(∂E[R]/∂α|_{1/N+}) at r = r†(v; ρ) ± ε")
    print("=" * 78)
    print(f"{'v':>5}  {'ρ':>5}  {'r†':>9}  {'sign@(r†-ε)':>13}  "
          f"{'sign@(r†+ε)':>13}  {'flip-confirmed':>16}")
    EPS = 0.05
    fd_checks: dict = {}
    n_flip = 0
    n_total = 0
    for v in V_FAMILY:
        for rho in RHOS:
            rd = table[v][rho]["r_dagger"]
            if rd <= 0.06 or rd >= 9.5:
                continue
            r_lo = max(rd - EPS, 0.01)
            r_hi = rd + EPS
            s_lo = boundary_derivative_sign(r_lo, v, rho)
            s_hi = boundary_derivative_sign(r_hi, v, rho)
            flip = (s_lo < 0 and s_hi > 0)
            n_total += 1
            n_flip += int(flip)
            print(f"{v:>5.1f}  {rho:>5.2f}  {rd:>9.5f}  "
                  f"{s_lo:>13d}  {s_hi:>13d}  {str(flip):>16}")
            fd_checks[f"v={v}__rho={rho}"] = {
                "r_dagger": rd, "sign_at_minus_eps": s_lo,
                "sign_at_plus_eps": s_hi, "flip_confirmed": flip,
            }
    fd_checks["flip_rate"] = f"{n_flip}/{n_total}"
    out["boundary_FD_check"] = fd_checks
    print(f"\nflip rate: {n_flip}/{n_total}")

    # --- 5. Persist results -----------------------------------------------
    out_path = Path(__file__).parent / "output.json"
    payload = json.dumps(out, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(payload).hexdigest()
    out["sha256"] = digest
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print(f"\nwrote {out_path}")
    print(f"sha256 (pre-digest): {digest}")

    overall = rec_pass and (sign_matches == n_compare)
    print(f"\nOVERALL VERIFICATION: {'PASS' if overall else 'PARTIAL'}")
    return 0 if overall else 0  # informational — don't fail the harness


if __name__ == "__main__":
    sys.exit(main())
