"""
Rebuild/derivations/verify_C1_cf_half/verify.py
=================================================
RB-024 — Verification of the closed-form CF<1/2 boundary derivation.

Companion to Rebuild/derivations/C1--cf-half-boundary.md.

VERIFIES (per the §7 contract):

  (1) Recovery contract (§7.2 / Proposition 2.1, r-independence of
      G_crit):
        |G_crit_closed(V, v, variant) − (R(P3) − R(P4))_rb-003(r, V, v, variant)|
          ≤ 1e-10
      across the 4,410-cell rb-003 sweep at every r-grid index. The
      closed form has no r-dependence; the rb-003 numbers do (in
      principle); the contract is that the two agree at every cell.

  (2) Necessary-condition truth table (§7.3 / Theorem 4.3):
      For each of the 210 distinct (V, v, variant) cells, compare:
        is_reachable_closed := [G_att_infty(V, v) > G_crit(V, v)]
      against
        is_reachable_empirical := [∃ r in rb-003's r-grid : CF(r, V, v) < 0.5]
      Report counts + any mismatches.

  (3) Sufficient-condition envelope (§7.4 / Theorem 5.1):
      For each (r, V, v, variant) row (4,410 rb-003 cells + extended
      high-r anchors {30, 100}), compare:
        sufficient_closed := [G_att_alpha1(r; V, v) > G_crit(V, v)]
      against
        empirical_below_half := [CF(r, V, v) < 0.5]
      Theorem 5.1 says sufficient ⇒ empirical; report any violations
      (expected count: 0) and the per-(V, v, variant) gap
        r_½_emp − r_*  (positive: conservative sufficient form;
                        negative: bug).

  (4) Headline aggregates (§7.5):
      - max ΔG_crit across recovery
      - reachable-cell counts per variant
      - sufficient-condition coverage of the empirical CF<0.5 region
      - any closed-form predictions absent from the empirical sweep
        (expected: cells where the necessary condition succeeds but
        the rb-003 r-grid (max r = 10) is insufficient to trigger)

OUTPUT:
  output.json — deterministic, sha256-stamped (excluding wall-clock).
  Re-running produces byte-identical results.json.

RUNTIME: ~30 s on a 2026-era laptop.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

THIS_FILE = Path(__file__).resolve()
REBUILD_ROOT = THIS_FILE.parents[2]                  # .../Rebuild
PROJ_ROOT = REBUILD_ROOT.parent                      # .../AttentionManuscript
sys.path.insert(0, str(REBUILD_ROOT.parent))
sys.path.insert(0, str(REBUILD_ROOT))

from model.core import (  # noqa: E402
    PHI_BACKEND,
    Phi,
    make_h,
    f_transfer,
    beta_gamma,
    d_prime_asym,
    C_GRID,
    p_no_fa_grid,
    p_no_fa_point,
    optimal_R,
    floor_R,
)

OUT_DIR = THIS_FILE.parent
RB003_RESULTS = (
    REBUILD_ROOT / "sims" / "C1--cf-distribution" / "output" / "results.json"
)

# ---------------------------------------------------------------------
# Standing parameters — match rb-003 byte-for-byte.
# ---------------------------------------------------------------------
N = 4
D_MAX = 2.0
F0 = 0.5
H_NAME = "sqrt"
H = make_h(H_NAME)
RHO = 0.0
CONS_P = 1.0

V_GRID = np.linspace(1.0 / N, 1.0, 21)
V_LIST = (1.0, 2.0, 3.0, 4.0, 5.0)
VARIANTS = ("A", "B")

D_BASE = D_MAX * f_transfer(1.0 / N, F0, H)           # 1.5 at standing params

# Closed-form asymptotic d-pair at α=1, r→∞ (Eqs. 4.4–4.6):
#   d_c^∞ = 2 d_max − d_base
#   d_u^∞ = d_base
D_C_INF = 2.0 * D_MAX - D_BASE                        # 2.5
D_U_INF = D_BASE                                      # 1.5

# Extended r-grid for §7.4 — rb-003's r-grid + high-r anchors.
R_GRID_RB003 = np.unique(np.concatenate([
    np.logspace(np.log10(0.1), np.log10(10.0), 21),
    np.array([1.0]),
]))                                                   # 22 r-values
R_GRID_EXT = np.array([30.0, 100.0])
R_GRID = np.concatenate([R_GRID_RB003, R_GRID_EXT])   # 24 r-values


# ---------------------------------------------------------------------
# Closed-form pieces.
# ---------------------------------------------------------------------
def CR_(V: float, v: float, variant: str) -> float:
    """Correct-rejection scaling (variant A: V*v + (1-V); variant B: 1)."""
    return (V * v + (1.0 - V)) if variant == "A" else 1.0


def R_eval(d_c: float, d_u: float, c_c: float, c_u: float,
           V: float, v: float, variant: str, rho: float) -> float:
    """E[R] at a fixed (d_c, d_u, c_c, c_u) — equivalent to F in (2.4)."""
    hr_c = float(Phi(d_c / 2.0 - c_c))
    hr_u = float(Phi(d_u / 2.0 - c_u))
    cr = CR_(V, v, variant)
    p_nofa = p_no_fa_point(d_c, d_u, N, rho, c_c, c_u)
    return 0.5 * (V * v * hr_c + (1.0 - V) * hr_u) + 0.5 * cr * p_nofa


def G_crit_closed(V: float, v: float, variant: str) -> float:
    """G_crit = R(P3) − R(P4), closed-form via (2.3).
    Independent of r by Proposition 2.1.
    """
    r3 = optimal_R(D_BASE, D_BASE, v, V, N, variant, RHO)
    r4 = floor_R(D_BASE, D_BASE, v, V, N, variant, RHO)
    return r3 - r4


def G_att_infty_closed(V: float, v: float, variant: str) -> float:
    """G_att^∞ = R^∞(V, v) − R(P3)(V, v), closed-form via (4.8).
    R^∞ is the 2-D criterion grid max at (d_c^∞, d_u^∞).
    """
    r_inf = optimal_R(D_C_INF, D_U_INF, v, V, N, variant, RHO)
    r3 = optimal_R(D_BASE, D_BASE, v, V, N, variant, RHO)
    return r_inf - r3


def G_att_alpha1_closed(r: float, V: float, v: float, variant: str) -> float:
    """G_att^{α=1}(r; V, v) = R*(α=1, r; V, v) − R(P3)(V, v),
    closed-form via (5.2), (5.4)–(5.5).
    """
    d_c, d_u = d_prime_asym(1.0, r, D_MAX, F0, H, N, CONS_P)
    r_a1 = optimal_R(d_c, d_u, v, V, N, variant, RHO)
    r3 = optimal_R(D_BASE, D_BASE, v, V, N, variant, RHO)
    return r_a1 - r3


# ---------------------------------------------------------------------
# §7.2 recovery contract: G_crit closed vs rb-003 empirical R(P3)-R(P4).
# ---------------------------------------------------------------------
def recovery_test_g_crit(rb003: dict) -> dict:
    """For every (r, V, v, variant) row in rb-003, compare
    G_crit_closed(V, v, variant) against (R(P3) − R(P4))_rb-003(r, V, v).

    Proposition 2.1 says these are equal modulo numerical noise; the
    contract is max|Δ| ≤ 1e-10.

    The rb-003 results.json structure has rows keyed by rho ('0.0', '0.2'):
    rows is a dict {rho_string: [row, row, ...]}. We use rho='0.0'.
    """
    rows = rb003["rows"]["0.0"]
    diffs = []
    max_diff = 0.0
    max_diff_cell = None
    for row in rows:
        if not row["valid"]:
            continue
        V = float(row["V"])
        v = float(row["v"])
        variant = str(row["variant"])
        emp = float(row["R_P3"]) - float(row["R_P4"])
        clo = G_crit_closed(V, v, variant)
        d = abs(emp - clo)
        diffs.append(d)
        if d > max_diff:
            max_diff = d
            max_diff_cell = dict(
                r=float(row["r"]), V=V, v=v, variant=variant,
                empirical=emp, closed=clo, diff=d,
            )
    return dict(
        n_compared=len(diffs),
        max_diff=max_diff,
        mean_diff=float(np.mean(diffs)) if diffs else 0.0,
        contract_threshold=1e-10,
        contract_pass=bool(max_diff <= 1e-10),
        max_diff_cell=max_diff_cell,
    )


# ---------------------------------------------------------------------
# §7.3 necessary-condition truth table (210 cells).
# ---------------------------------------------------------------------
def necessary_truth_table(rb003: dict) -> dict:
    """For each (V, v, variant) cell, compute is_reachable_closed and
    is_reachable_empirical; tally and report mismatches.
    """
    rows = rb003["rows"]["0.0"]
    # Build empirical lookup: (V_key, v_key, variant) → min_r CF (over valid r).
    empirical_min_cf: dict = {}
    for row in rows:
        if not row["valid"]:
            continue
        V_key = round(float(row["V"]), 6)
        v_key = float(row["v"])
        variant = str(row["variant"])
        cf = float(row["CF"])
        k = (V_key, v_key, variant)
        if k not in empirical_min_cf or cf < empirical_min_cf[k]["min_cf"]:
            empirical_min_cf[k] = dict(
                min_cf=cf, argmin_r=float(row["r"]),
            )

    closed_cells = []
    mismatches = []
    counts = {"A": dict(reachable=0, total=0), "B": dict(reachable=0, total=0)}
    for V in V_GRID:
        V_key = round(float(V), 6)
        for v in V_LIST:
            for variant in VARIANTS:
                g_crit = G_crit_closed(float(V), float(v), variant)
                g_att_inf = G_att_infty_closed(float(V), float(v), variant)
                reachable_closed = bool(g_att_inf > g_crit)
                emp_row = empirical_min_cf.get((V_key, v, variant))
                reachable_emp = bool(emp_row is not None and emp_row["min_cf"] < 0.5)
                counts[variant]["total"] += 1
                if reachable_closed:
                    counts[variant]["reachable"] += 1
                cell = dict(
                    V=float(V), v=float(v), variant=variant,
                    G_crit=g_crit, G_att_infty=g_att_inf,
                    margin=g_att_inf - g_crit,
                    reachable_closed=reachable_closed,
                    reachable_empirical=reachable_emp,
                    emp_min_cf=(emp_row["min_cf"] if emp_row else None),
                    emp_argmin_r=(emp_row["argmin_r"] if emp_row else None),
                )
                closed_cells.append(cell)
                if reachable_closed != reachable_emp:
                    mismatches.append(cell)
    return dict(
        n_cells=len(closed_cells),
        counts=counts,
        n_mismatches=len(mismatches),
        mismatches=mismatches,
        # Variant-A minimum margin (closed): if all negative, predicts
        # variant-A "CF≥1/2 everywhere" from primitives.
        variant_A_max_margin=max(
            c["margin"] for c in closed_cells if c["variant"] == "A"
        ),
        variant_B_max_margin=max(
            c["margin"] for c in closed_cells if c["variant"] == "B"
        ),
        all_closed_cells=closed_cells,
    )


# ---------------------------------------------------------------------
# §7.4 sufficient-condition envelope.
# ---------------------------------------------------------------------
def sufficient_envelope(rb003: dict) -> dict:
    """For each (r, V, v, variant) in the extended grid, evaluate:
      G_att_alpha1(r; V, v) and compare to G_crit(V, v).
    Then check: sufficient ⇒ empirical CF<0.5 (Theorem 5.1).

    Reports:
      - sufficient_count
      - empirical_below_half_count
      - sufficient ∩ empirical / sufficient (Theorem 5.1: should be 1.0)
      - sufficient ∩ empirical / empirical (coverage of empirical region)
      - per-(V, v, variant) gap r_½_emp − r_*  where defined.
    """
    rows = rb003["rows"]["0.0"]
    # Empirical (r, V, v, variant) → CF lookup.
    emp_lookup: dict = {}
    for row in rows:
        if not row["valid"]:
            continue
        k = (
            round(float(row["r"]), 6),
            round(float(row["V"]), 6),
            float(row["v"]),
            str(row["variant"]),
        )
        emp_lookup[k] = float(row["CF"])

    sufficient_rows = []
    violations = []        # sufficient but empirical CF ≥ 0.5
    empirical_below = 0
    sufficient_and_empirical = 0
    sufficient_count = 0

    for r in R_GRID:
        for V in V_GRID:
            for v in V_LIST:
                for variant in VARIANTS:
                    g_crit = G_crit_closed(float(V), float(v), variant)
                    g_att_a1 = G_att_alpha1_closed(
                        float(r), float(V), float(v), variant,
                    )
                    sufficient = bool(g_att_a1 > g_crit)
                    # Empirical CF only available for r ∈ R_GRID_RB003.
                    if r <= 10.0 + 1e-9:
                        emp_cf = emp_lookup.get(
                            (round(float(r), 6), round(float(V), 6),
                             float(v), variant),
                        )
                        emp_below = bool(emp_cf is not None and emp_cf < 0.5)
                    else:
                        emp_cf = None
                        emp_below = None
                    if sufficient:
                        sufficient_count += 1
                    if emp_below is True:
                        empirical_below += 1
                        if sufficient:
                            sufficient_and_empirical += 1
                    if sufficient and emp_below is False:
                        violations.append(dict(
                            r=float(r), V=float(V), v=float(v),
                            variant=variant,
                            G_crit=g_crit, G_att_alpha1=g_att_a1,
                            margin=g_att_a1 - g_crit,
                            empirical_cf=emp_cf,
                        ))
                    sufficient_rows.append(dict(
                        r=float(r), V=float(V), v=float(v),
                        variant=variant,
                        G_crit=g_crit, G_att_alpha1=g_att_a1,
                        sufficient=sufficient,
                        emp_cf=emp_cf,
                        emp_below=emp_below,
                    ))

    # Per-(V, v, variant) gap: r_½_emp (smallest r with CF<0.5 in rb-003 grid)
    #                       vs r_* (smallest r with sufficient=True).
    per_cell_gaps = []
    for V in V_GRID:
        for v in V_LIST:
            for variant in VARIANTS:
                r_half_emp = None
                r_star = None
                for r in R_GRID_RB003:
                    emp = emp_lookup.get(
                        (round(float(r), 6), round(float(V), 6),
                         float(v), variant),
                    )
                    if emp is not None and emp < 0.5 and r_half_emp is None:
                        r_half_emp = float(r)
                for r in R_GRID:
                    g_crit = G_crit_closed(float(V), float(v), variant)
                    g_att_a1 = G_att_alpha1_closed(
                        float(r), float(V), float(v), variant,
                    )
                    if g_att_a1 > g_crit and r_star is None:
                        r_star = float(r)
                if r_half_emp is not None or r_star is not None:
                    per_cell_gaps.append(dict(
                        V=float(V), v=float(v), variant=variant,
                        r_half_emp=r_half_emp,
                        r_star=r_star,
                        gap=(r_star - r_half_emp if r_half_emp is not None and r_star is not None else None),
                    ))

    coverage = (
        sufficient_and_empirical / empirical_below
        if empirical_below > 0 else None
    )
    soundness = (
        sufficient_and_empirical / sufficient_count
        if sufficient_count > 0 else None
    )
    # Soundness restricted to cells where empirical data is available
    # (excludes the extended-grid r ∈ {30, 100} predictions that have no
    # rb-003 companion to validate against). This is the correct
    # Theorem 5.1 contract: among cells where we CAN compare, sufficient
    # ⇒ empirical CF < 0.5 should hold exactly.
    sufficient_with_empirical = sufficient_and_empirical + len(violations)
    soundness_within_empirical = (
        sufficient_and_empirical / sufficient_with_empirical
        if sufficient_with_empirical > 0 else None
    )

    return dict(
        n_rows=len(sufficient_rows),
        sufficient_count=sufficient_count,
        empirical_below_count=empirical_below,
        sufficient_and_empirical=sufficient_and_empirical,
        soundness_ratio=soundness,        # over all sufficient rows
        soundness_within_empirical=soundness_within_empirical,  # Theorem 5.1 over available cells
        coverage_ratio=coverage,          # how much of empirical region
        n_violations=len(violations),
        violations=violations,
        per_cell_gaps=per_cell_gaps,
    )


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main() -> None:
    print(f"RB-024 / rb-051 — verify C1 CF<1/2 boundary derivation")
    print(f"  Phi backend: {PHI_BACKEND}")
    print(f"  d_base = {D_BASE:.6f}; d_c^∞ = {D_C_INF:.6f}; d_u^∞ = {D_U_INF:.6f}")
    print(f"  output: {OUT_DIR}")

    if not RB003_RESULTS.exists():
        raise SystemExit(f"missing rb-003 sweep: {RB003_RESULTS}")
    with open(RB003_RESULTS) as fh:
        rb003 = json.load(fh)
    print(f"  rb-003 loaded; sha256 = {rb003['metadata']['sha256']}")

    t0 = time.time()
    print("\n§7.2 — recovery contract on G_crit (Proposition 2.1):")
    recovery = recovery_test_g_crit(rb003)
    print(f"  n_compared = {recovery['n_compared']}")
    print(f"  max|Δ| = {recovery['max_diff']:.3e}")
    print(f"  contract (≤ 1e-10): {'PASS' if recovery['contract_pass'] else 'FAIL'}")
    if not recovery["contract_pass"]:
        print(f"  worst cell: {recovery['max_diff_cell']}")

    print("\n§7.3 — necessary-condition truth table (210 cells):")
    nec = necessary_truth_table(rb003)
    print(f"  variant A: {nec['counts']['A']['reachable']}/"
          f"{nec['counts']['A']['total']} cells reachable (closed)")
    print(f"  variant B: {nec['counts']['B']['reachable']}/"
          f"{nec['counts']['B']['total']} cells reachable (closed)")
    print(f"  mismatches (closed vs empirical): {nec['n_mismatches']}")
    print(f"  variant A max margin (G_att^∞ − G_crit): "
          f"{nec['variant_A_max_margin']:+.4f}")
    print(f"  variant B max margin: {nec['variant_B_max_margin']:+.4f}")
    if nec["n_mismatches"] > 0:
        print(f"  first 5 mismatches:")
        for cell in nec["mismatches"][:5]:
            print(f"    V={cell['V']:.4f} v={cell['v']:.0f} "
                  f"variant={cell['variant']} "
                  f"margin={cell['margin']:+.4f} "
                  f"closed={cell['reachable_closed']} "
                  f"emp={cell['reachable_empirical']} "
                  f"min_cf={cell['emp_min_cf']}")

    print("\n§7.4 — sufficient-condition envelope (24 r × 105 cells/variant):")
    suff = sufficient_envelope(rb003)
    print(f"  n_rows = {suff['n_rows']}")
    print(f"  sufficient_count = {suff['sufficient_count']}")
    print(f"  empirical_below_count (rb-003 r-grid only) = "
          f"{suff['empirical_below_count']}")
    print(f"  sufficient ∩ empirical = {suff['sufficient_and_empirical']}")
    print(f"  Theorem 5.1 soundness over all sufficient rows = "
          f"{suff['soundness_ratio']:.4f} (lumps in extended-grid rows w/o empirical)")
    print(f"  Theorem 5.1 soundness restricted to cells w/ empirical data = "
          f"{suff['soundness_within_empirical']} (target: 1.0)")
    print(f"  coverage of empirical CF<0.5 by sufficient = "
          f"{suff['coverage_ratio']}")
    print(f"  violations (sufficient but empirical ≥ 0.5): "
          f"{suff['n_violations']}")
    if suff["n_violations"] > 0:
        print(f"  first 3 violations:")
        for v in suff["violations"][:3]:
            print(f"    r={v['r']:.4f} V={v['V']:.4f} v={v['v']:.0f} "
                  f"variant={v['variant']} margin={v['margin']:+.4e} "
                  f"emp_cf={v['empirical_cf']:.4f}")

    t1 = time.time()
    print(f"\nwall-clock: {t1 - t0:.1f}s")

    # Build the deterministic output payload.
    out = {
        "recovery_test": recovery,
        "necessary_truth_table": nec,
        "sufficient_envelope": suff,
        "metadata": {
            "task_id": "RB-024",
            "run_id": "rb-051",
            "prompt_version": "0.2",
            "date": "2026-05-31",
            "phi_backend": PHI_BACKEND,
            "N": N, "d_max": D_MAX, "f0": F0, "h_name": H_NAME,
            "rho": RHO, "cons_p": CONS_P,
            "d_base": D_BASE,
            "d_c_infty": D_C_INF,
            "d_u_infty": D_U_INF,
            "V_grid": [float(V) for V in V_GRID],
            "v_grid": list(V_LIST),
            "r_grid_rb003": [float(r) for r in R_GRID_RB003],
            "r_grid_extended": [float(r) for r in R_GRID_EXT],
            "variants": list(VARIANTS),
            "rb003_input_sha256": rb003["metadata"]["sha256"],
            # wall-clock excluded from digest input.
        },
    }

    # Deterministic serialisation → sha256 (excluding wall-clock).
    payload = json.dumps(out, indent=2, sort_keys=True, default=float)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    out["metadata"]["sha256"] = digest
    out["metadata"]["wallclock_seconds"] = float(t1 - t0)
    payload2 = json.dumps(out, indent=2, sort_keys=True, default=float)

    results_path = OUT_DIR / "output.json"
    with open(results_path, "w") as fh:
        fh.write(payload2)
    print(f"\nWrote {results_path}")
    print(f"sha256 (pre-stamp, deterministic): {digest}")


if __name__ == "__main__":
    main()
