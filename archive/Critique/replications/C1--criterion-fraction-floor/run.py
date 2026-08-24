"""
C1 sensitivity attack — locate the criterion-fraction floor and
probe extrapolations outside the paper's swept space (CR-002).

Mission claim C1 (§4.1 of paper, mission §2.6):
    "Across the full parameter sweep (4,410 combinations), the
    criterion fraction is between 0.60 and 0.96."

The criterion fraction is defined as
    CF = [R(P3) - R(P4)] / [R(P1) - R(P4)]
i.e. the share of the *total* reward gain (from the unbiased
uniform-attention floor up to the joint optimum) that is captured
by criterion adjustment alone at uniform attention. The paper's
qualitative reading: "criterion adjustment is always the single
largest contributor to value-related reward." (§4.1)

Attack design (mission §3.2 — sensitivity vector):
    Phase A. Locate min CF on the paper's swept primary grid
        r ∈ {21 log-pts in [0.1, 10.0]} ∪ {1.0}
        V ∈ {21 pts in [1/N, 1.0]}
        v ∈ {1, 2, 3, 4, 5}
        variant ∈ {A, B}
        N = 4, d'_max = 2.0, f_0 = 0.5, h = sqrt
    Verify that the empirical range matches 0.60–0.96.

    Phase B. At the (V*, v*, variant*) where Phase A found min CF,
    extrapolate just outside the swept space along five axes:
        (i)   r > 10  -- push benefit-dominance further;
        (ii)  f_0 < 0.1  -- lower than paper's lowest sweep point;
        (iii) h ∈ {a^3, a^4}  -- more accelerating than a^2;
        (iv)  N > 4  -- more locations to spread uncued cost across;
        (v)  v > 5  -- larger value contrast than paper sweeps.
    Goal: drive CF below 0.50 if possible, identifying the
    boundary at which attention reallocation overtakes criterion
    as the dominant mechanism for value encoding.

Mathematical caveat. CF is a *ratio* of small numbers near the
limit V → 1/N (where there is no validity gradient and both
numerator and denominator vanish). In that regime CF is numerically
fragile; we skip combinations where the denominator R(P1) - R(P4)
is below 1e-4 reward units.

Speed notes. We re-use primitives from
Critique/replications/C2--non-monotonic-vda/run.py (the Phi via
math.erf and the policy_rewards function), but with two
optimisations for this larger sweep:
  (i) alpha*(v=1) for the value-blind P2 baseline only depends on
      (r, V, N, f_0, h, variant) -- not on the v currently being
      evaluated -- so we precompute it once per (r, V, variant)
      and reuse across v ∈ {1..5};
  (ii) optional scipy.special.ndtr Phi (faster than the math.erf
       Python loop) if scipy is available in the sandbox.

CR-002, prompt v0.1, run 2026-05-17.
"""

from __future__ import annotations

import math
import json
import os
import time
from typing import Callable

import numpy as np


# ---------------------------------------------------------------
# Phi (standard normal CDF) — try scipy first, fall back to a
# vectorised math.erf loop if scipy is unavailable.
# ---------------------------------------------------------------

_SQRT2 = math.sqrt(2.0)
_SQRT_2PI = math.sqrt(2.0 * math.pi)

try:
    from scipy.special import ndtr as _ndtr  # vectorised numpy ufunc

    def Phi(x):
        return _ndtr(np.asarray(x, dtype=float))

    _PHI_BACKEND = "scipy.special.ndtr"
except ImportError:
    # Abramowitz & Stegun 7.1.26 — vectorised erf approximation.
    # Max abs error ~1.5e-7 for x ∈ ℝ. Numpy-native (no Python loop).
    _A1 = 0.254829592
    _A2 = -0.284496736
    _A3 = 1.421413741
    _A4 = -1.453152027
    _A5 = 1.061405429
    _P = 0.3275911

    def _erf_np(x_arr: np.ndarray) -> np.ndarray:
        # Sign-fold so the polynomial is evaluated on |x|.
        x_abs = np.abs(x_arr)
        t = 1.0 / (1.0 + _P * x_abs)
        # Horner: ((((a5·t + a4)·t + a3)·t + a2)·t + a1)·t
        poly = ((((_A5 * t + _A4) * t + _A3) * t + _A2) * t + _A1) * t
        y = 1.0 - poly * np.exp(-x_abs * x_abs)
        return np.where(x_arr >= 0.0, y, -y)

    def Phi(x):
        arr = np.asarray(x, dtype=float)
        return 0.5 * (1.0 + _erf_np(arr / _SQRT2))

    _PHI_BACKEND = "A&S 7.1.26 numpy-vectorised"


# ---------------------------------------------------------------
# Model primitives — mirrors C2's run.py but inlined for clarity.
# Mission §2.3, §2.4.
# ---------------------------------------------------------------


def make_h(name: str) -> Callable:
    """Transfer function families. h(0)=0, h(1)=1, monotone."""
    if name == "sqrt":
        return lambda a: np.sqrt(a)
    if name == "linear":
        return lambda a: a
    if name == "p0_3":
        return lambda a: np.power(a, 0.3)
    if name == "p2":
        return lambda a: np.power(a, 2.0)
    if name == "p3":
        return lambda a: np.power(a, 3.0)
    if name == "p4":
        return lambda a: np.power(a, 4.0)
    raise ValueError(name)


def f_transfer(a, f0: float, h: Callable):
    """f(a) = f_0 + (1 - f_0) h(a). Mission §2.3."""
    return f0 + (1.0 - f0) * h(a)


def beta_gamma(r: float) -> tuple[float, float]:
    """β(r) = 2r/(r+1); γ(r) = 2/(r+1). β + γ = 2."""
    return 2.0 * r / (r + 1.0), 2.0 / (r + 1.0)


def d_prime_pair(alpha: float, r: float, d_max: float, f0: float,
                 h: Callable, N: int) -> tuple[float, float]:
    """Per-location d' at cued and (each) uncued location. Mission §2.4."""
    beta, gamma = beta_gamma(r)
    d_base = d_max * f_transfer(1.0 / N, f0, h)
    if alpha >= 1.0 / N:
        d_c = d_base + beta * (d_max * f_transfer(alpha, f0, h) - d_base)
        d_u = d_base + gamma * (d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h) - d_base)
    else:
        d_c = d_base + gamma * (d_max * f_transfer(alpha, f0, h) - d_base)
        d_u = d_base + beta * (d_max * f_transfer((1.0 - alpha) / (N - 1), f0, h) - d_base)
    return float(max(d_c, 0.0)), float(max(d_u, 0.0))


# ---------------------------------------------------------------
# Criterion grid (Δc = 0.05 — paper's grid; same as CR-001's code).
# ---------------------------------------------------------------

C_GRID = np.arange(-3.0, 3.0 + 1e-9, 0.05)
_C_GRID_LEN = len(C_GRID)


def optimal_criteria_R(d_c: float, d_u: float, v: float, V: float, N: int,
                       variant: str = "A") -> float:
    """
    Joint optimal (c_c, c_u) by grid search over C_GRID × C_GRID.
    Returns R*. Reward function: mission §2.5 Eq (9).
    """
    # Phi values: 1-d arrays of length |C_GRID|.
    hr_c = Phi(d_c / 2.0 - C_GRID)
    hr_u = Phi(d_u / 2.0 - C_GRID)
    far_c = Phi(-d_c / 2.0 - C_GRID)
    far_u = Phi(-d_u / 2.0 - C_GRID)
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    # Broadcast: c_c axis 0, c_u axis 1.
    p_no_fa = (1.0 - far_c)[:, None] * ((1.0 - far_u) ** (N - 1))[None, :]
    er = 0.5 * (V * hr_c[:, None] * v + (1.0 - V) * hr_u[None, :]) + 0.5 * p_no_fa * cr
    return float(er.max())


def reward_at_c_zero(d_c: float, d_u: float, v: float, V: float, N: int,
                     variant: str = "A") -> float:
    """R(P4) when α = 1/N AND c_c = c_u = 0 at uniform d'."""
    hr_c = float(Phi(d_c / 2.0))
    hr_u = float(Phi(d_u / 2.0))
    far_c = float(Phi(-d_c / 2.0))
    far_u = float(Phi(-d_u / 2.0))
    cr = (V * v + (1.0 - V)) if variant == "A" else 1.0
    p_no_fa = (1.0 - far_c) * (1.0 - far_u) ** (N - 1)
    return 0.5 * (V * hr_c * v + (1.0 - V) * hr_u) + 0.5 * p_no_fa * cr


# ---------------------------------------------------------------
# CF computation — optimised over (r, V) so alpha*(v=1) cached.
# ---------------------------------------------------------------


def compute_CF(r: float, V: float, v: float, N: int, d_max: float,
               f0: float, h: Callable, variant: str,
               alpha_grid: np.ndarray,
               cached_alpha_p2: float | None = None
               ) -> dict:
    """
    Returns dict with R(P1), R(P2), R(P3), R(P4), VDA, criterion_fraction,
    and the alpha used for P1 / P2.

    If cached_alpha_p2 is provided, P2 uses it instead of recomputing —
    note: cached value must have been computed at the SAME (r, V, N,
    d_max, f0, h, variant).
    """
    # Precompute d'(α) pairs once.
    d_pairs = [d_prime_pair(float(a), r, d_max, f0, h, N) for a in alpha_grid]

    # P3, P4 at uniform attention.
    d_b = d_max * f_transfer(1.0 / N, f0, h)
    R_p3 = optimal_criteria_R(d_b, d_b, v, V, N, variant)
    R_p4 = reward_at_c_zero(d_b, d_b, v, V, N, variant)

    # P1 = max over α of R(α, c*).
    rs_p1 = np.array([optimal_criteria_R(dc, du, v, V, N, variant)
                      for dc, du in d_pairs])
    idx_p1 = int(np.argmax(rs_p1))
    R_p1 = float(rs_p1[idx_p1])
    alpha_p1 = float(alpha_grid[idx_p1])

    # P2 — alpha fixed at α*(v=1); criteria re-optimised at current v.
    if cached_alpha_p2 is None:
        rs_p2_v1 = np.array([optimal_criteria_R(dc, du, 1.0, V, N, variant)
                             for dc, du in d_pairs])
        cached_alpha_p2 = float(alpha_grid[int(np.argmax(rs_p2_v1))])
    alpha_p2 = cached_alpha_p2
    dc_p2, du_p2 = d_prime_pair(alpha_p2, r, d_max, f0, h, N)
    R_p2 = optimal_criteria_R(dc_p2, du_p2, v, V, N, variant)

    total = R_p1 - R_p4
    crit = R_p3 - R_p4
    cf = crit / max(total, 1e-12)
    return {
        "r": r, "V": V, "v": v, "N": N, "d_max": d_max, "f0": f0,
        "variant": variant,
        "alpha_p1": alpha_p1, "alpha_p2": alpha_p2,
        "R_p1": R_p1, "R_p2": R_p2, "R_p3": R_p3, "R_p4": R_p4,
        "VDA": R_p1 - R_p2,
        "validity_attention_gain": R_p2 - R_p3,
        "criterion_gain": crit,
        "criterion_fraction": cf,
        "total_gain": total,
    }


def get_cached_alpha_p2(r: float, V: float, N: int, d_max: float,
                        f0: float, h: Callable, variant: str,
                        alpha_grid: np.ndarray) -> float:
    """Compute α*(v=1) for (r, V, ...) once; reuse across v ∈ {1..5}."""
    d_pairs = [d_prime_pair(float(a), r, d_max, f0, h, N) for a in alpha_grid]
    rs = np.array([optimal_criteria_R(dc, du, 1.0, V, N, variant)
                   for dc, du in d_pairs])
    return float(alpha_grid[int(np.argmax(rs))])


# ---------------------------------------------------------------
# Phase A — primary sweep
# ---------------------------------------------------------------


def phase_A_primary_sweep():
    """Replicate paper's 4,410 primary-sweep grid; locate min CF."""
    N = 4
    d_max = 2.0
    f0 = 0.5
    h = make_h("sqrt")
    # Paper's grid: 21 log-spaced r in [0.1, 10] plus r=1. 21 V in [1/N, 1].
    r_grid = np.unique(np.concatenate([np.logspace(np.log10(0.1), np.log10(10.0), 21),
                                       np.array([1.0])]))
    V_grid = np.linspace(1.0 / N, 1.0, 21)
    v_grid = np.array([1, 2, 3, 4, 5])
    variants = ["A", "B"]

    # α grid — Δα = 0.02 plus the 1/N point. 50 points is enough for CF
    # locating; the ratio is dominated by P3/P4 which are at fixed α=1/N.
    alpha_grid = np.unique(np.concatenate([np.arange(0.02, 1.0 + 1e-9, 0.02),
                                           np.array([1.0 / N])]))

    rows = []
    t0 = time.time()
    n_total = len(r_grid) * len(V_grid) * len(v_grid) * len(variants)
    n_done = 0
    print(f"Phase A — primary sweep ({n_total} combinations)")
    print(f"  Phi backend: {_PHI_BACKEND}")
    print(f"  α-grid: {len(alpha_grid)} pts, c-grid: {_C_GRID_LEN} pts")

    for r in r_grid:
        for V in V_grid:
            for variant in variants:
                # Cache α*(v=1) once per (r, V, variant).
                cached_alpha_p2 = get_cached_alpha_p2(
                    float(r), float(V), N, d_max, f0, h, variant, alpha_grid)
                for v in v_grid:
                    row = compute_CF(float(r), float(V), float(v), N, d_max, f0,
                                     h, variant, alpha_grid,
                                     cached_alpha_p2=cached_alpha_p2)
                    rows.append(row)
                    n_done += 1
        elapsed = time.time() - t0
        rate = n_done / max(elapsed, 1e-9)
        eta = (n_total - n_done) / max(rate, 1e-9)
        print(f"  r={r:8.4f}  done={n_done}/{n_total}  rate={rate:.1f}/s  ETA={eta:.0f}s")

    return rows


# ---------------------------------------------------------------
# Phase B — extrapolate at min-CF anchor point
# ---------------------------------------------------------------


def phase_B_extrapolations(anchor: dict, alpha_grid_fine: np.ndarray):
    """
    Take the (V, v, variant) that produced the min CF in Phase A.
    Probe just outside the paper's sweep along five axes, holding
    (V, v, variant) fixed at the anchor values.
    """
    N0 = anchor["N"]
    d_max0 = anchor["d_max"]
    f0_0 = anchor["f0"]
    V0 = anchor["V"]
    v0 = anchor["v"]
    variant0 = anchor["variant"]
    h0 = make_h("sqrt")
    print()
    print(f"Phase B — extrapolations anchored at "
          f"(V={V0:.3f}, v={v0}, variant={variant0}, "
          f"N={N0}, d'_max={d_max0}, f_0={f0_0}, h=sqrt)")

    results = {}

    # (i) push r upward, far past the paper's r=10 cap.
    r_extended = np.array([10.0, 20.0, 50.0, 100.0, 500.0, 2000.0])
    print("  axis (i) r > 10:")
    r_rows = []
    for r in r_extended:
        row = compute_CF(float(r), V0, float(v0), N0, d_max0, f0_0, h0,
                         variant0, alpha_grid_fine)
        r_rows.append(row)
        print(f"    r={r:8.2f}  CF={row['criterion_fraction']:.4f}  "
              f"VDA={row['VDA']:.5f}  total_gain={row['total_gain']:.4f}")
    results["r_extrapolation"] = r_rows

    # (ii) lower f_0 below paper's secondary-sweep floor (0.1).
    f0_extended = [0.05, 0.02, 0.01, 0.001]
    print("  axis (ii) f_0 < 0.1:")
    f0_rows = []
    # Use the anchor's r (best inside-sweep r) for the f_0 probe.
    r_anchor = anchor["r"]
    for f0_v in f0_extended:
        row = compute_CF(float(r_anchor), V0, float(v0), N0, d_max0, f0_v, h0,
                         variant0, alpha_grid_fine)
        f0_rows.append(row)
        print(f"    f_0={f0_v:6.3f}  CF={row['criterion_fraction']:.4f}  "
              f"VDA={row['VDA']:.5f}  total_gain={row['total_gain']:.4f}")
    results["f0_extrapolation"] = f0_rows

    # (iii) more-accelerating h.
    print("  axis (iii) h ∈ {a^3, a^4}:")
    h_rows = []
    for h_name in ["p3", "p4"]:
        h_alt = make_h(h_name)
        row = compute_CF(float(r_anchor), V0, float(v0), N0, d_max0, f0_0, h_alt,
                         variant0, alpha_grid_fine)
        row["h_name"] = h_name
        h_rows.append(row)
        print(f"    h={h_name:>4}  CF={row['criterion_fraction']:.4f}  "
              f"VDA={row['VDA']:.5f}  total_gain={row['total_gain']:.4f}")
    results["h_extrapolation"] = h_rows

    # (iv) more locations N > 4.
    print("  axis (iv) N > 4:")
    N_rows = []
    for N_v in [8, 16, 32]:
        # V floor is 1/N — re-anchor V to V0 if V0 ≥ 1/N_v, else 1/N_v.
        V_use = max(V0, 1.0 / N_v)
        row = compute_CF(float(r_anchor), V_use, float(v0), N_v, d_max0, f0_0, h0,
                         variant0, alpha_grid_fine)
        N_rows.append(row)
        print(f"    N={N_v:3d}  V={V_use:.3f}  CF={row['criterion_fraction']:.4f}  "
              f"VDA={row['VDA']:.5f}  total_gain={row['total_gain']:.4f}")
    results["N_extrapolation"] = N_rows

    # (v) v > 5.
    print("  axis (v) v > 5:")
    v_rows = []
    for v_v in [10, 20, 50, 100]:
        row = compute_CF(float(r_anchor), V0, float(v_v), N0, d_max0, f0_0, h0,
                         variant0, alpha_grid_fine)
        v_rows.append(row)
        print(f"    v={v_v:4d}  CF={row['criterion_fraction']:.4f}  "
              f"VDA={row['VDA']:.5f}  total_gain={row['total_gain']:.4f}")
    results["v_extrapolation"] = v_rows

    # (vi) combination — push every axis simultaneously to maximise
    # attention's share. Lowest plausible f_0, largest plausible r,
    # most-accelerating h, largest plausible v, largest plausible N.
    print("  axis (vi) extreme combo:")
    combo_rows = []
    for combo in [
        dict(r=100.0, f0=0.05, h="p2", v=10.0, N=4, d_max=2.0),
        dict(r=100.0, f0=0.02, h="p4", v=10.0, N=4, d_max=2.0),
        dict(r=100.0, f0=0.02, h="p4", v=50.0, N=4, d_max=2.0),
        dict(r=500.0, f0=0.02, h="p4", v=100.0, N=4, d_max=2.0),
        dict(r=500.0, f0=0.01, h="p4", v=100.0, N=8, d_max=2.0),
        dict(r=500.0, f0=0.01, h="p4", v=100.0, N=16, d_max=2.0),
    ]:
        h_alt = make_h(combo["h"])
        V_use = max(V0, 1.0 / combo["N"])
        row = compute_CF(combo["r"], V_use, combo["v"], combo["N"], combo["d_max"],
                         combo["f0"], h_alt, variant0, alpha_grid_fine)
        row["combo"] = combo
        combo_rows.append(row)
        print(f"    {combo}  ->  CF={row['criterion_fraction']:.4f}  "
              f"VDA={row['VDA']:.5f}  total_gain={row['total_gain']:.4f}")
    results["combo_extrapolation"] = combo_rows

    return results


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------


def main():
    outdir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(outdir, exist_ok=True)

    rows = phase_A_primary_sweep()
    cfs = np.array([row["criterion_fraction"] for row in rows])
    total_gains = np.array([row["total_gain"] for row in rows])
    # Mask numerically fragile rows: very small total gain.
    valid = total_gains > 1e-4
    print()
    print("Phase A summary:")
    print(f"  Total rows: {len(rows)}; valid (total_gain > 1e-4): {valid.sum()}")
    print(f"  CF min (valid): {cfs[valid].min():.4f}")
    print(f"  CF max (valid): {cfs[valid].max():.4f}")
    print(f"  CF median (valid): {np.median(cfs[valid]):.4f}")
    print(f"  Paper claim C1: CF ∈ [0.60, 0.96] across all 4,410 combos.")

    # Identify argmin among valid rows.
    idx_min = int(np.argmin(np.where(valid, cfs, np.inf)))
    anchor = rows[idx_min]
    print()
    print(f"  argmin row idx: {idx_min}")
    print(f"  argmin params: r={anchor['r']:.4f}, V={anchor['V']:.4f}, "
          f"v={anchor['v']}, variant={anchor['variant']}, CF={anchor['criterion_fraction']:.4f}")

    # Identify argmax for sanity check.
    idx_max = int(np.argmax(np.where(valid, cfs, -np.inf)))
    top = rows[idx_max]
    print(f"  argmax row idx: {idx_max}")
    print(f"  argmax params: r={top['r']:.4f}, V={top['V']:.4f}, "
          f"v={top['v']}, variant={top['variant']}, CF={top['criterion_fraction']:.4f}")

    # Phase B at the argmin.
    alpha_fine = np.unique(np.concatenate([np.arange(0.01, 1.0 + 1e-9, 0.01),
                                           np.array([1.0 / anchor["N"]])]))
    phase_b = phase_B_extrapolations(anchor, alpha_fine)

    # Save.
    out = {
        "phase_A": {
            "rows": rows,
            "n_valid": int(valid.sum()),
            "cf_min": float(cfs[valid].min()),
            "cf_max": float(cfs[valid].max()),
            "cf_median": float(np.median(cfs[valid])),
            "argmin": anchor,
            "argmax": top,
        },
        "phase_B": phase_b,
        "metadata": {
            "phi_backend": _PHI_BACKEND,
            "c_grid_step": 0.05,
            "c_grid_range": [float(C_GRID[0]), float(C_GRID[-1])],
            "alpha_grid_step": 0.02,
            "valid_threshold": 1e-4,
            "claim_id": "C1",
            "attack_vector": "sensitivity",
            "run_id": "run-003",
            "task_id": "CR-002",
            "prompt_version": "0.1",
            "date": "2026-05-17",
        }
    }
    out_path = os.path.join(outdir, "results.json")
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2, default=float)
    print()
    print(f"Saved results: {out_path}")


if __name__ == "__main__":
    main()
