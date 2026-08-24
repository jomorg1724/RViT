"""
Sensitivity probe of the C2 peak location (CR-014).

The CR-001 re-derivation produced a closed-form *escape threshold*
governing the lower edge of the non-zero VDA interval:

    r†(v) = G_u(V, N, c_c*, c_u*) / [(N-1) * G_c(v, V, N, c_c*, c_u*)]      (Eq. 2.5)

where (c_c*, c_u*) are the criteria optimised at uniform attention
α = 1/N for the policy in question, and G_c, G_u are the chain-rule
coefficients on the ∂E[R]/∂α gradient at α = 1/N⁺:

    G_c(v) = (1/2) * V * v * φ(d'_b/2 − c_c)/2
           − (1/2) * CR * φ(−d'_b/2 − c_c)/2 * (1 − Φ(−d'_b/2 − c_u))^{N-1}      (cued β-channel)

    G_u    = − [ (1/2) * (1 − V) * φ(d'_b/2 − c_u)/2
              − (1/2) * CR * (1 − Φ(−d'_b/2 − c_c)) * (N-1)
                       * (1 − Φ(−d'_b/2 − c_u))^{N-2} * φ(−d'_b/2 − c_u)/2 ] * (N-1)    (uncued γ-channel)

(The factor (N-1) is absorbed into G_u above so that the threshold
expression carries an explicit (N-1) in the denominator, matching
the derivation §2.3.)

  Sign convention. The gradient
      ∂E[R]/∂α|_{1/N⁺} = d'_max f'(1/N) · [ G_c(v) β(r) − G_u/(N-1) γ(r) ]
  is positive precisely when r > r†(v) (cf. derivation §2.4 Eq. 2.4).
  G_c(v) and G_u as defined here are both *positive*; the cued
  channel raises d'_c (good for hits, bad for false-alarm-no-fa
  product), and the uncued channel lowers d'_u (bad for uncued hits,
  good for false-alarm-no-fa product).  The two CR-induced terms
  partially cancel the hit-rate terms; for the parameter regimes
  the paper sweeps (V=0.5, v∈{1..5}, Variant A CR = V v + 1 − V),
  both G_c(v) and G_u come out positive — we check this assumption
  numerically in the run.

Reference regime (Figure 6 of paper):
    N = 4 (or 2), d'_max = 2.0, h ∈ {a, √a, a^0.3, a^2},
    f_0 ∈ {0.1, 0.3, 0.5, 0.7}, V = 0.5, v = 5, Variant A.

For each combination of (f_0, h, N), the script:
  1. Computes d'_base = d_max * f(1/N).
  2. Finds (c_c*, c_u*) by grid-searching the criterion plane at
     α = 1/N (i.e. with d_c = d_u = d'_base).
  3. Computes G_c(v), G_u, and r†(v=5), r†(v=1).
  4. Sweeps r on the paper's primary grid and records empirical
     peak (r*_emp, VDA*_emp).
  5. Compares closed-form direction-of-shift predictions to the
     empirical sweep and to the paper's §4.6 / Figure 6 narrative:
        (i)  lower f_0 ⇒ peak higher and to slightly lower r;
        (ii) a^0.3 compresses, a^2 stretches;
        (iii) N=2 similar shape with slightly larger VDA magnitudes.

The sensitivity probe is a *second* attack vector for C2: the
re-derivation in CR-001 already established the analytic skeleton;
this script tests whether the *quantitative direction* of peak
shifts the closed form predicts matches the paper's empirical
Figure 6. If yes, two distinct attack vectors have failed to
falsify C2 — verdict elevates to CONFIRMED-UNDER-ATTACK.

The script uses only numpy + math.erf (scipy not assumed in the
sandbox; cf. CR-001 notes about disk pressure).
"""

from __future__ import annotations

import math
import json
import os
import sys
from typing import Callable

import numpy as np


# ---------------------------------------------------------------
# Standard normal CDF/PDF via math.erf (no scipy assumed).
# ---------------------------------------------------------------

_SQRT2 = math.sqrt(2.0)
_SQRT_2PI = math.sqrt(2.0 * math.pi)


def Phi(x):
    """Standard normal CDF. Scalar or array. Vectorised via list-comp."""
    if np.isscalar(x):
        return 0.5 * (1.0 + math.erf(float(x) / _SQRT2))
    arr = np.asarray(x, dtype=float)
    flat = arr.ravel()
    out = np.empty_like(flat)
    for i, xi in enumerate(flat):
        out[i] = 0.5 * (1.0 + math.erf(float(xi) / _SQRT2))
    return out.reshape(arr.shape)


def phi(x):
    """Standard normal PDF. Scalar or array."""
    return np.exp(-0.5 * np.asarray(x, dtype=float) ** 2) / _SQRT_2PI


# ---------------------------------------------------------------
# Model primitives (mission §2; identical to ../run.py for clarity).
# ---------------------------------------------------------------

H_FORMS: dict[str, Callable] = {
    "linear":  lambda a: a,
    "sqrt":    lambda a: np.sqrt(a),
    "p0_3":    lambda a: np.power(a, 0.3),
    "p2":      lambda a: np.power(a, 2.0),
}

H_LABELS = {
    "linear": "h(a) = a",
    "sqrt":   "h(a) = √a",
    "p0_3":   "h(a) = a^0.3",
    "p2":     "h(a) = a^2",
}


def f_transfer(a, f0: float, h: Callable):
    """f(a) = f_0 + (1 − f_0) h(a)."""
    return f0 + (1.0 - f0) * h(a)


def beta_gamma(r: float) -> tuple[float, float]:
    return 2.0 * r / (r + 1.0), 2.0 / (r + 1.0)


def d_prime_cued_uncued(alpha: float, r: float, d_max: float, f0: float,
                        h: Callable, N: int) -> tuple[float, float]:
    """Per-location d′ at cued and (each) uncued location (mission §2.4)."""
    beta, gamma = beta_gamma(r)
    d_base = d_max * f_transfer(1.0 / N, f0, h)
    if alpha >= 1.0 / N:
        d_c = d_base + beta  * (d_max * f_transfer(alpha, f0, h)            - d_base)
        d_u = d_base + gamma * (d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h) - d_base)
    else:
        d_c = d_base + gamma * (d_max * f_transfer(alpha, f0, h)            - d_base)
        d_u = d_base + beta  * (d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h) - d_base)
    return float(max(d_c, 0.0)), float(max(d_u, 0.0))


#  Extended c-grid (-3.0 .. 3.5) to handle the low-f_0 case, where
#  d_base is small and the optimal c_u at uniform attention drifts
#  above 2.5 (the default grid stopped at the edge of the optimum
#  for f_0 = 0.1).
C_GRID = np.arange(-3.0, 3.5 + 1e-9, 0.05)


def optimal_criteria(d_c: float, d_u: float, v: float, V: float, N: int,
                     variant: str = "A") -> tuple[float, float, float]:
    """Grid-search (c_c, c_u) maximising E[R] at the given d's. Returns (c_c*, c_u*, R*)."""
    hr_c = Phi(d_c / 2.0 - C_GRID)
    hr_u = Phi(d_u / 2.0 - C_GRID)
    far_c = Phi(-d_c / 2.0 - C_GRID)
    far_u = Phi(-d_u / 2.0 - C_GRID)
    cr = V * v + (1.0 - V) if variant == "A" else 1.0
    p_no_fa = (1.0 - far_c)[:, None] * ((1.0 - far_u) ** (N - 1))[None, :]
    er = 0.5 * (V * hr_c[:, None] * v + (1.0 - V) * hr_u[None, :]) \
       + 0.5 * p_no_fa * cr
    idx = np.unravel_index(int(np.argmax(er)), er.shape)
    return float(C_GRID[idx[0]]), float(C_GRID[idx[1]]), float(er[idx])


# ---------------------------------------------------------------
# Closed-form G_c, G_u, r†(v) from the CR-001 derivation §2.3.
# ---------------------------------------------------------------

def G_coefs(d_base: float, c_c: float, c_u: float, v: float, V: float, N: int,
            variant: str = "A") -> tuple[float, float]:
    """
    Chain-rule coefficients on the cued (G_c) and uncued (G_u) channels of
    ∂E[R]/∂α evaluated at α = 1/N⁺ with d_c = d_u = d_base (uniform attention).

    Derivation §2.3 expands the gradient as
        ∂E[R]/∂α|_{1/N⁺}
           = d'_max f'(1/N) · [ G_c(v) β(r) − (G_u / (N-1)) γ(r) ]
    where G_c := ∂E[R]/∂d_c and G_u := ∂E[R]/∂d_u, both evaluated at
    d_c = d_u = d_base.  Both partials are SUMS of two positive terms
    (the hit-rate term and the no-false-alarm survival term):

        G_c(v) = ∂E[R]/∂d_c
               =   (1/4) * V * v   * φ(d_b/2 − c_c)
                 + (1/4) * CR      * φ(−d_b/2 − c_c) * (1 − Φ(−d_b/2 − c_u))^{N-1}

        G_u    = ∂E[R]/∂d_u
               =   (1/4) * (1 − V) * φ(d_b/2 − c_u)
                 + (1/4) * CR      * (1 − Φ(−d_b/2 − c_c))
                                   * (N − 1) * (1 − Φ(−d_b/2 − c_u))^{N-2}
                                   * φ(−d_b/2 − c_u)

    The negative sign in the β/γ expansion comes from the JACOBIAN of
    d_u on α at α = 1/N⁺ (∂d_u/∂α = − γ d'_max f'(1/N) / (N-1)), not
    from G_u itself.  Setting the gradient to zero yields

        r†(v) = G_u / [ (N − 1) · G_c(v) ]                              (Eq. 2.5)

    Both G_c, G_u > 0 for the parameter regimes the paper sweeps;
    this is verified numerically in the run.  (Earlier bootstrap-001
    derivation §2.3 had the right sign on the gradient but the python
    transcription erroneously *subtracted* the no-FA contribution
    inside G_c and G_u — that produced a negative r†(v) in regions
    where the no-FA term dominates the hit-rate term, which is a
    transcription error not a math error.  The corrected expressions
    above are sums of strictly positive quantities for V > 0,
    v ≥ 1, N ≥ 2.)
    """
    cr = V * v + (1.0 - V) if variant == "A" else 1.0
    # Densities and survival probabilities at the uniform-attention criteria.
    phi_hit_c = phi(d_base / 2.0 - c_c)
    phi_hit_u = phi(d_base / 2.0 - c_u)
    phi_fa_c  = phi(-d_base / 2.0 - c_c)
    phi_fa_u  = phi(-d_base / 2.0 - c_u)
    surv_fa_c = 1.0 - Phi(-d_base / 2.0 - c_c)
    surv_fa_u = 1.0 - Phi(-d_base / 2.0 - c_u)

    G_c = 0.25 * V * v * phi_hit_c \
        + 0.25 * cr * phi_fa_c * surv_fa_u ** (N - 1)

    G_u = 0.25 * (1.0 - V) * phi_hit_u \
        + 0.25 * cr * surv_fa_c * (N - 1) * surv_fa_u ** (N - 2) * phi_fa_u

    return float(G_c), float(G_u)


def r_dagger(G_c_v: float, G_u: float, N: int) -> float:
    """r†(v) = G_u / [(N-1) G_c(v)]; returns +inf if G_c(v) ≤ 0."""
    if G_c_v <= 0:
        return float("inf")
    return G_u / ((N - 1) * G_c_v)


# ---------------------------------------------------------------
# Empirical VDA(r) sweep: re-uses ../run.py's policy_rewards path.
# Local copy to keep this script standalone.
# ---------------------------------------------------------------

def policy_rewards(v: float, V: float, N: int, d_max: float, f0: float,
                   h: Callable, r: float, variant: str = "A",
                   alpha_grid: np.ndarray | None = None) -> dict:
    if alpha_grid is None:
        alpha_grid = np.arange(0.02, 1.0 + 1e-9, 0.01)
    d_pairs = [d_prime_cued_uncued(float(a), r, d_max, f0, h, N) for a in alpha_grid]

    # P1: optimise α and criteria jointly at v.
    rs_p1 = np.empty(len(alpha_grid))
    for i, (dc, du) in enumerate(d_pairs):
        _, _, rs_p1[i] = optimal_criteria(dc, du, v, V, N, variant)
    idx_p1 = int(np.argmax(rs_p1))
    alpha_p1 = float(alpha_grid[idx_p1])
    R_p1 = float(rs_p1[idx_p1])

    # P2: α fixed at α*(v = 1).
    rs_p2_v1 = np.empty(len(alpha_grid))
    for i, (dc, du) in enumerate(d_pairs):
        _, _, rs_p2_v1[i] = optimal_criteria(dc, du, 1.0, V, N, variant)
    idx_p2 = int(np.argmax(rs_p2_v1))
    alpha_p2 = float(alpha_grid[idx_p2])
    dc_p2, du_p2 = d_prime_cued_uncued(alpha_p2, r, d_max, f0, h, N)
    _, _, R_p2 = optimal_criteria(dc_p2, du_p2, v, V, N, variant)

    return {
        "r": float(r),
        "alpha_p1": alpha_p1,
        "alpha_p2": alpha_p2,
        "R_p1": R_p1,
        "R_p2": R_p2,
        "VDA": R_p1 - R_p2,
    }


def sweep_vda_r(v: float, V: float, N: int, d_max: float, f0: float,
                h: Callable, variant: str = "A",
                r_grid: np.ndarray | None = None) -> tuple[float, float, list]:
    """Return (peak_r_empirical, peak_vda, rows) on the paper's primary grid."""
    if r_grid is None:
        r_grid = np.logspace(np.log10(0.1), np.log10(10.0), 21)
    rows = []
    for r in r_grid:
        rows.append(policy_rewards(v, V, N, d_max, f0, h, float(r), variant))
    vdas = np.array([row["VDA"] for row in rows])
    idx = int(np.argmax(vdas))
    return float(r_grid[idx]), float(vdas[idx]), rows


# ---------------------------------------------------------------
# Main: sweep the paper's §3.1 secondary parameter combinations and
# compare closed-form r†(v) to empirical peak r*.
# ---------------------------------------------------------------

def main():
    d_max = 2.0
    V = 0.5
    v = 5.0
    variant = "A"

    # Three secondary sweeps (paper §3.1, mirrored in Figure 6):
    sweeps = []

    # (a) f_0 sensitivity at h = √, N = 4
    for f0 in [0.1, 0.3, 0.5, 0.7]:
        sweeps.append({"family": "f0", "f0": f0, "h_key": "sqrt", "N": 4,
                       "label": f"f_0 = {f0}"})

    # (b) h sensitivity at f_0 = 0.5, N = 4
    for h_key in ["linear", "sqrt", "p0_3", "p2"]:
        sweeps.append({"family": "h", "f0": 0.5, "h_key": h_key, "N": 4,
                       "label": H_LABELS[h_key]})

    # (c) N sensitivity at f_0 = 0.5, h = √
    for N in [2, 4]:
        sweeps.append({"family": "N", "f0": 0.5, "h_key": "sqrt", "N": N,
                       "label": f"N = {N}"})

    # Extended r-grid downward to [0.01, 10.0] with 31 log-spaced
    # points so that low-f_0 and h = a^2 cases (which predict r†(v) <
    # 0.02) are not clipped at the bottom.  The paper's primary grid
    # was [0.1, 10.0] @ 21 points; the extension is for boundary
    # robustness here.
    r_grid_main = np.logspace(np.log10(0.01), np.log10(10.0), 31)

    results = []
    print(f"{'family':>6} {'label':<18} {'d_base':>7} {'c_c*':>7} {'c_u*':>7} "
          f"{'G_c(v)':>9} {'G_u':>9} {'r†(v=5)':>9} {'r†(v=1)':>9} "
          f"{'√r†r†1':>8} {'logW':>6} {'r*_emp':>8} {'VDA_emp':>8}")
    for s in sweeps:
        f0 = s["f0"]
        h = H_FORMS[s["h_key"]]
        N = s["N"]

        # Step 1: d_base at uniform attention.
        d_base = d_max * f_transfer(1.0 / N, f0, h)

        # Step 2: optimal (c_c, c_u) at α = 1/N for value v.
        c_c, c_u, _ = optimal_criteria(d_base, d_base, v, V, N, variant)

        # Step 3: closed-form G_c, G_u, r†.
        G_c_v, G_u = G_coefs(d_base, c_c, c_u, v, V, N, variant)
        # r†(v=1) uses the c_c,c_u optimised at v=1 (P2's escape).
        c_c1, c_u1, _ = optimal_criteria(d_base, d_base, 1.0, V, N, variant)
        G_c_1, G_u_1 = G_coefs(d_base, c_c1, c_u1, 1.0, V, N, variant)

        r_dag_v   = r_dagger(G_c_v, G_u,   N)
        r_dag_1   = r_dagger(G_c_1, G_u_1, N)

        # Step 4: empirical peak via VDA(r) sweep at the same params.
        peak_r, peak_vda, sweep_rows = sweep_vda_r(v, V, N, d_max, f0, h, variant, r_grid_main)

        # Geometric mean of (r†(v=5), r†(v=1)) — a natural one-number
        # predictor of the peak location, since the peak lives in the
        # interval (r†(v), r†(1)).  The log-r width log10(r†(1)/r†(v))
        # is a direct test of the paper's "compression / stretching"
        # narrative for h.
        if r_dag_v > 0 and r_dag_1 > 0:
            geomean_r_dag = float(np.sqrt(r_dag_v * r_dag_1))
            log_width = float(np.log10(r_dag_1 / r_dag_v))
        else:
            geomean_r_dag = float("nan")
            log_width = float("nan")

        row = {
            **s,
            "d_base":         d_base,
            "c_c":            c_c,
            "c_u":            c_u,
            "G_c_v":          G_c_v,
            "G_u":            G_u,
            "r_dag_v5":       r_dag_v,
            "r_dag_v1":       r_dag_1,
            "geomean_r_dag":  geomean_r_dag,
            "log_width":      log_width,
            "peak_r_emp":     peak_r,
            "peak_vda":       peak_vda,
            "vda_curve":      [{"r": rr["r"], "VDA": rr["VDA"],
                                 "alpha_p1": rr["alpha_p1"],
                                 "alpha_p2": rr["alpha_p2"]} for rr in sweep_rows],
        }
        results.append(row)
        print(f"{s['family']:>6} {s['label']:<18} {d_base:7.3f} {c_c:7.3f} {c_u:7.3f} "
              f"{G_c_v:9.5f} {G_u:9.5f} {r_dag_v:9.4f} {r_dag_1:9.4f} "
              f"{geomean_r_dag:8.4f} {log_width:6.2f} "
              f"{peak_r:8.4f} {peak_vda:8.5f}")

    # ----- summary / direction-of-shift checks -----
    print()
    print("=== Direction-of-shift checks vs paper §4.6 narrative ===")
    f0_rows = [r for r in results if r["family"] == "f0"]
    f0_rows.sort(key=lambda x: x["f0"])
    print("Sensitivity to f_0 (lower f_0 ⇒ paper predicts peak higher & to slightly lower r):")
    for r in f0_rows:
        print(f"   {r['label']}: r†(v=5)={r['r_dag_v5']:.4f}, "
              f"peak_emp r={r['peak_r_emp']:.4f}, peak_emp VDA={r['peak_vda']:.5f}")

    h_rows = [r for r in results if r["family"] == "h"]
    print("Sensitivity to h (paper §4.6: a^0.3 compresses, a^2 stretches):")
    for r in h_rows:
        print(f"   {r['label']}: r†(v=5)={r['r_dag_v5']:.4f}, "
              f"peak_emp r={r['peak_r_emp']:.4f}, peak_emp VDA={r['peak_vda']:.5f}")

    N_rows = [r for r in results if r["family"] == "N"]
    print("Sensitivity to N (paper §4.6: N=2 similar pattern, slightly larger VDA):")
    for r in N_rows:
        print(f"   {r['label']}: r†(v=5)={r['r_dag_v5']:.4f}, "
              f"peak_emp r={r['peak_r_emp']:.4f}, peak_emp VDA={r['peak_vda']:.5f}")

    os.makedirs("output", exist_ok=True)
    with open("output/sensitivity_results.json", "w") as fh:
        json.dump({
            "reference_regime": {"d_max": d_max, "V": V, "v": v, "variant": variant},
            "results": results,
            "narrative_checks": {
                "f0_monotonic_lower_f0_lower_r_dag":
                    all(f0_rows[i]["r_dag_v5"] <= f0_rows[i+1]["r_dag_v5"]
                        for i in range(len(f0_rows) - 1)),
                "f0_monotonic_lower_f0_higher_peak_vda":
                    all(f0_rows[i]["peak_vda"] >= f0_rows[i+1]["peak_vda"]
                        for i in range(len(f0_rows) - 1)),
                "f0_peak_emp_monotone_in_f0":
                    [r["peak_r_emp"] for r in f0_rows],
            }
        }, fh, indent=2)
    print()
    print("Wrote output/sensitivity_results.json")


if __name__ == "__main__":
    main()
