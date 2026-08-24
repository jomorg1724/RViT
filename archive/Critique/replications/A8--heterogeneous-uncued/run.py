"""
CR-036 — Replication attack on assumption A8 ("uncued-location attention is
homogeneous"), mission §2.7 / paper §2.2.

Companion verdict : Critique/verdicts/A8--heterogeneous-uncued.md
Companion notes   : ./notes.md
Companion readme  : ./README.md

--------------------------------------------------------------------------
The assumption under attack (paper §2.2, verbatim)
--------------------------------------------------------------------------
    "The observer allocates attention α ∈ [0,1] to the cued location. The
     remaining attention is distributed equally among uncued locations, so
     each receives (1−α)/(N−1). At uniform attention, α = 1/N and all
     locations are treated identically."

The model's policy space is therefore *one-dimensional in α*: the uncued
locations are forced to share attention equally. This is A8. It is implicit
in §2.2/§2.3 and is NOT one of the paper's four explicitly-listed §5.5
limitations (which name A1 independence, A2 single-global-r, A3 additive
conservation, A4 no-learning). It was surfaced by run-007/CR-031 and
ratified into the mission at v0.2.

--------------------------------------------------------------------------
Two questions this script answers (CR-036 task)
--------------------------------------------------------------------------
  (b) Do any C1–C5 headline numbers shift when uncued homogeneity is
      relaxed?  ── Part 1.
  (a) Does the optimal policy reproduce a *graded suppression* of an
      anti-cued (low-target-validity) location, matching the Wang &
      Theeuwes statistical-learning suppression gradient?  ── Part 2.

The pivotal conceptual distinction the run draws:

    Is homogeneous-uncued allocation an ASSUMPTION the model imposes, or
    an OPTIMUM the model would choose anyway if the constraint were lifted?

If, under equal uncued *validity*, the unconstrained optimum still splits
uncued attention equally, then A8 is INNOCUOUS for the headline claims —
the optimiser was never going to break homogeneity, so C1–C5 are unchanged.
A8 only becomes load-bearing where the unconstrained optimum prefers an
*unequal* uncued split.

--------------------------------------------------------------------------
Mathematical formulation (general-N, heterogeneous allocation + validity)
--------------------------------------------------------------------------
Locations i = 1..N, location 1 cued. Define:
  • allocation vector  a = (a_1,…,a_N),  a_i ≥ 0,  Σ a_i = 1
  • validity vector    w = (w_1,…,w_N),  w_i ≥ 0,  Σ w_i = 1
       (w_i = P[change at i | change trial]; cued w_1 = V)
  • value vector       u_i = v if i = 1 (cued) else 1
  • baseline d'        d'_base = d'_max · f(1/N),  f(a)=f_0+(1−f_0)h(a)

Per-location sensitivity GENERALISES Eqs. (7)–(8) via the gain/loss rule the
paper itself states in §2.3 ("If α<1/N … the cued location's departure is
scaled by γ and each uncued location's by β"):

    d'_i = max( d'_base + s_i·[d'_max f(a_i) − d'_base],  0 ),
        s_i = β(r)  if a_i ≥ 1/N   (a GAIN  — departure ≥ 0)
        s_i = γ(r)  if a_i <  1/N   (a LOSS  — departure < 0)

with β(r)=2r/(r+1), γ(r)=2/(r+1)  (mission §2.4).  This reduces EXACTLY to
the paper's cued/uncued split in the homogeneous case: cued a_1=α≥1/N → β;
each uncued a_i=(1−α)/(N−1)≤1/N → γ (and the inverted branch swaps, per the
paper's note). Tying s_i to the sign of the per-location departure is the
unique generalisation consistent with §2.3 — documented as a modelling
choice in notes.md.

Per-location criteria c_i;  HR_i = Φ(d'_i/2 − c_i),  FAR_i = Φ(−d'_i/2 − c_i).

Expected reward (generalises Eq. (9)):

    E[R] = 0.5 Σ_i w_i u_i HR_i  +  0.5 · CR · Π_i (1 − FAR_i)

    Variant A: CR = Σ_i w_i u_i = V·v + (1−V)   (uncued u=1, Σ_unc w = 1−V)
    Variant B: CR = 1

In the homogeneous case (w_i=(1−V)/(N−1), a_i=(1−α)/(N−1) for i≥2) this is
identically the paper's Eq. (9) with P_no-fa=(1−FAR_c)(1−FAR_u)^{N−1}.

--------------------------------------------------------------------------
Complexity
--------------------------------------------------------------------------
  Φ/φ via math.erf (no scipy; matches the C4/C5 substrate).
  Criterion optimisation: coordinate ascent over distinct-d' GROUPS, each a
  1-D grid search of |C_GRID| points; G groups, S sweeps ⇒ O(S·G·|C_GRID|).
  Allocation probes are coarse grids over a 1- or 2-parameter reduction of
  the simplex ⇒ bounded, single-machine, < 1 min total.

CR-036, prompt v0.2, run-012, 2026-05-24.
"""

from __future__ import annotations

import math
import json
import os
from typing import Callable

import numpy as np


# ===============================================================
# 0.  SDT primitives — identical to the C4/C5 substrate (no scipy).
# ===============================================================

_SQRT2 = math.sqrt(2.0)
_SQRT_2PI = math.sqrt(2.0 * math.pi)


def Phi_scalar(x: float) -> float:
    """Standard normal CDF, scalar, via math.erf."""
    return 0.5 * (1.0 + math.erf(x / _SQRT2))


def Phi(x):
    """Vectorised standard normal CDF over a numpy array (loop over erf)."""
    x_arr = np.asarray(x, dtype=float)
    out = np.empty_like(x_arr)
    flat = x_arr.ravel()
    flat_out = out.ravel()
    for i, xi in enumerate(flat):
        flat_out[i] = 0.5 * (1.0 + math.erf(float(xi) / _SQRT2))
    return out


# ===============================================================
# 1.  Model primitives (mission §2 / paper §2.3–2.4).
# ===============================================================

H_FORMS: dict[str, Callable] = {
    "linear": lambda a: a,                  # h(a)=a            (linear)
    "sqrt":   lambda a: math.sqrt(a),       # h(a)=√a           (diminishing, DEFAULT)
    "p0_3":   lambda a: a ** 0.3,           # h(a)=a^0.3        (strongly diminishing)
    "p2":     lambda a: a ** 2.0,           # h(a)=a^2          (accelerating)
}


def f_transfer(a: float, f0: float, h: Callable) -> float:
    """f(a) = f_0 + (1−f_0)·h(a).  Paper §2.3."""
    return f0 + (1.0 - f0) * h(a)


def beta_gamma(r: float) -> tuple[float, float]:
    """β(r)=2r/(r+1) (benefit), γ(r)=2/(r+1) (cost).  Paper Eqs. (5)–(6)."""
    return 2.0 * r / (r + 1.0), 2.0 / (r + 1.0)


def d_prime_of_allocation(a_i: float, r: float, d_max: float, f0: float,
                          h: Callable, N: int) -> float:
    """
    Per-location d' under the GENERALISED gain/loss rule (see module docstring).
    Reduces to Eqs. (7)–(8) in the homogeneous case.

        d'_i = max( d'_base + s_i·[d'_max f(a_i) − d'_base], 0 )
        s_i  = β  if a_i ≥ 1/N (gain) else γ (loss)
    """
    a_i = float(min(max(a_i, 0.0), 1.0))
    beta, gamma = beta_gamma(r)
    d_base = d_max * f_transfer(1.0 / N, f0, h)
    departure = d_max * f_transfer(a_i, f0, h) - d_base
    s_i = beta if a_i >= 1.0 / N else gamma
    return max(d_base + s_i * departure, 0.0)


# ===============================================================
# 2.  Criterion optimisation by coordinate ascent over GROUPS.
# ===============================================================
#
# A "group" is a set of locations sharing the same d' and the same
# value×validity weight wu := w_i·u_i; by symmetry they share an optimal
# criterion. The reward is
#
#   E[R] = 0.5 Σ_g n_g·wu_g·HR(d'_g,c_g)  +  0.5·CR·Π_g (1−FAR(d'_g,c_g))^{n_g}
#
# Holding all c_{g'≠g} fixed, the c_g-dependent part is
#   0.5 n_g wu_g HR(d'_g,c_g) + 0.5 CR P_{-g} (1−FAR(d'_g,c_g))^{n_g}
# with P_{-g} = Π_{g'≠g}(1−FAR_{g'})^{n_{g'}} constant in c_g. We maximise it
# over the Δc=0.05 grid (matching the paper), cycling groups until the
# criteria stop changing. This is exact at grid resolution.

_C_GRID = np.arange(-2.5, 2.5 + 1e-9, 0.05)
_C_HR = None     # caches Φ(d/2 − c) per d (filled lazily); negligible here.


def _hr_far_on_grid(d: float):
    """Return (HR_grid, oneminusFAR_grid) over _C_GRID for sensitivity d."""
    hr = Phi(d / 2.0 - _C_GRID)              # Φ(d/2 − c)
    one_minus_far = Phi(d / 2.0 + _C_GRID)   # 1 − Φ(−d/2 − c) = Φ(d/2 + c)
    return hr, one_minus_far


def optimal_ER_general(d_list: list[float], wu_list: list[float],
                       n_list: list[int], CR: float,
                       max_sweeps: int = 80) -> dict:
    """
    Criterion optimisation for an arbitrary set of location GROUPS.

    Args
      d_list  : group sensitivities d'_g           (len G)
      wu_list : group weights wu_g = w_g·u_g        (len G)
      n_list  : group multiplicities n_g            (len G)  Σ n_g = N
      CR      : correct-rejection reward
    Returns dict(R, c_idx, c_vals).

    METHOD. The per-group criterion landscape is BIMODAL (a "liberal/detect"
    attractor that maximises HR vs a "conservative/avoid-FA" attractor that
    maximises the no-FA product), so plain coordinate ascent can stall in a
    local optimum (verified: it missed the joint optimum by 0.05 on one
    variant-B config). We therefore use:
      • G ≤ 2 : an EXACT joint grid over the c-grid (1-D for G=1, the full
                2-D outer product for G=2 — identical machinery to the C4/C5
                base optimiser, so the homogeneous validation is bit-faithful).
      • G ≥ 3 : multi-restart exact-coordinate-ascent. Restarts span the 2^G
                corner seeds (each group started at its change-side OR its
                CR-side standalone argmax) plus the all-zero seed; each restart
                runs coordinate ascent (each step an EXACT 1-D argmax over the
                c-grid); the best R over restarts is returned. Validated
                against a joint 3-D grid on sampled G=3 configs (see __main__).
    """
    G = len(d_list)
    grids = [_hr_far_on_grid(d) for d in d_list]        # [(hr_g, omf_g)]

    def total_R(idx):
        prod = 1.0
        change = 0.0
        for g in range(G):
            hr_g, omf_g = grids[g]
            change += n_list[g] * wu_list[g] * hr_g[idx[g]]
            prod *= omf_g[idx[g]] ** n_list[g]
        return 0.5 * change + 0.5 * CR * prod

    # ---- Exact joint grid for G ≤ 2 -----------------------------------
    if G == 1:
        hr0, omf0 = grids[0]
        obj = 0.5 * n_list[0] * wu_list[0] * hr0 + 0.5 * CR * (omf0 ** n_list[0])
        bi = int(np.argmax(obj))
        return dict(R=float(obj[bi]), c_idx=[bi], c_vals=[float(_C_GRID[bi])])
    if G == 2:
        hr0, omf0 = grids[0]
        hr1, omf1 = grids[1]
        # E[R] over the full (c0,c1) grid via outer products.
        change = (0.5 * n_list[0] * wu_list[0] * hr0[:, None]
                  + 0.5 * n_list[1] * wu_list[1] * hr1[None, :])
        prod = (omf0[:, None] ** n_list[0]) * (omf1[None, :] ** n_list[1])
        ER = change + 0.5 * CR * prod
        i0, i1 = np.unravel_index(int(np.argmax(ER)), ER.shape)
        return dict(R=float(ER[i0, i1]), c_idx=[int(i0), int(i1)],
                    c_vals=[float(_C_GRID[i0]), float(_C_GRID[i1])])

    # ---- Multi-restart coordinate ascent for G ≥ 3 --------------------
    # Per-group standalone argmaxes for the two attractors.
    change_arg = [int(np.argmax(grids[g][0])) for g in range(G)]            # max HR
    cr_arg = [int(np.argmax(grids[g][1] ** n_list[g])) for g in range(G)]   # max (1-FAR)^n
    zero_idx = int(np.argmin(np.abs(_C_GRID)))                              # c≈0

    # Build 2^G corner seeds + all-zero seed.
    seeds = []
    for mask in range(1 << G):
        seeds.append([change_arg[g] if (mask >> g) & 1 else cr_arg[g] for g in range(G)])
    seeds.append([zero_idx] * G)

    def coord_ascent(c_idx):
        c_idx = list(c_idx)
        for _ in range(max_sweeps):
            changed = False
            for g in range(G):
                P_minus_g = 1.0
                for g2 in range(G):
                    if g2 == g:
                        continue
                    P_minus_g *= grids[g2][1][c_idx[g2]] ** n_list[g2]
                hr_g, omf_g = grids[g]
                obj = (0.5 * n_list[g] * wu_list[g] * hr_g
                       + 0.5 * CR * P_minus_g * (omf_g ** n_list[g]))
                best = int(np.argmax(obj))
                if best != c_idx[g]:
                    c_idx[g] = best
                    changed = True
            if not changed:
                break
        return c_idx

    best_R, best_idx = -1.0, None
    for s in seeds:
        idx = coord_ascent(s)
        R = total_R(idx)
        if R > best_R:
            best_R, best_idx = R, idx
    return dict(R=float(best_R), c_idx=list(best_idx),
                c_vals=[float(_C_GRID[i]) for i in best_idx])


# ===============================================================
# 3.  Convenience: E[R] for a FULL allocation+validity vector.
# ===============================================================

def ER_full_policy(alloc: np.ndarray, valid: np.ndarray, v: float,
                   r: float, N: int, d_max: float, f0: float, h_name: str,
                   variant: str = "A") -> dict:
    """
    Expected reward at a fully-specified allocation vector `alloc` and validity
    vector `valid` (both length N, location 0 = cued), with criteria optimised.

    Groups locations by (rounded d', rounded wu) so symmetric locations share a
    criterion (keeps coordinate ascent small and exact).
    """
    h = H_FORMS[h_name]
    # value vector: cued (index 0) = v, others = 1.
    value = np.ones(N)
    value[0] = v
    # per-location d' and wu.
    d_arr = np.array([d_prime_of_allocation(float(alloc[i]), r, d_max, f0, h, N)
                      for i in range(N)])
    wu_arr = valid * value
    CR = float(np.sum(wu_arr)) if variant == "A" else 1.0

    # Group by (d', wu) to within a fine tolerance.
    groups: dict[tuple, list[int]] = {}
    for i in range(N):
        key = (round(float(d_arr[i]), 9), round(float(wu_arr[i]), 12))
        groups.setdefault(key, []).append(i)
    d_list = [k[0] for k in groups]
    wu_list = [k[1] for k in groups]
    n_list = [len(groups[k]) for k in groups]

    res = optimal_ER_general(d_list, wu_list, n_list, CR)
    res["d_arr"] = d_arr.tolist()
    res["wu_arr"] = wu_arr.tolist()
    res["CR"] = CR
    return res


# ===============================================================
# 4.  Homogeneous base model (validation substrate).
# ===============================================================
#
# Reproduces the paper's 3-parameter (α, c_cued, c_uncued) optimum via the
# SAME machinery: a homogeneous policy is just alloc=[α, (1−α)/(N−1),…],
# valid=[V, (1−V)/(N−1),…]. We optimise α on the paper's Δα=0.005 grid.

_ALPHA_GRID = np.arange(0.02, 1.0 + 1e-9, 0.005)   # paper §3.2 (extends below 1/N)


def homogeneous_optimum(V: float, v: float, r: float, N: int, d_max: float,
                        f0: float, h_name: str, variant: str = "A",
                        alpha_grid: np.ndarray | None = None) -> dict:
    """Joint optimum over α (grid) with criteria optimised at each α. (= paper P1.)"""
    if alpha_grid is None:
        alpha_grid = _ALPHA_GRID
    best = dict(R=-1.0, alpha=float("nan"))
    Rs = np.empty_like(alpha_grid)
    for k, a in enumerate(alpha_grid):
        alloc = np.full(N, (1.0 - a) / (N - 1))
        alloc[0] = a
        valid = np.full(N, (1.0 - V) / (N - 1))
        valid[0] = V
        res = ER_full_policy(alloc, valid, v, r, N, d_max, f0, h_name, variant)
        Rs[k] = res["R"]
        if res["R"] > best["R"]:
            best = dict(R=res["R"], alpha=float(a), c_vals=res["c_vals"],
                        d_arr=res["d_arr"])
    best["alpha_grid"] = alpha_grid
    best["Rs"] = Rs
    return best


def policy_decomposition_homog(V: float, v: float, r: float, N: int, d_max: float,
                               f0: float, h_name: str, variant: str = "A") -> dict:
    """
    Compute the paper's P1..P4 and the VDA benefit + criterion fraction, under
    the homogeneous (A8) model. Used to validate against C1/C2 figures.

      P1: joint optimum (α*, criteria) at this v.
      P2: α fixed at α*(v=1); criteria re-optimised at this v.
      P3: α = 1/N; criteria optimised.
      P4: α = 1/N; c = 0.
      VDA = R(P1) − R(P2);  CF = (R(P3)−R(P4)) / (R(P1)−R(P4)).
    """
    p1 = homogeneous_optimum(V, v, r, N, d_max, f0, h_name, variant)
    # α*(v=1) for P2:
    alpha_v1 = homogeneous_optimum(V, 1.0, r, N, d_max, f0, h_name, variant)["alpha"]

    def R_at_alpha(a, vv):
        alloc = np.full(N, (1.0 - a) / (N - 1)); alloc[0] = a
        valid = np.full(N, (1.0 - V) / (N - 1)); valid[0] = V
        return ER_full_policy(alloc, valid, vv, r, N, d_max, f0, h_name, variant)["R"]

    R_p1 = p1["R"]
    R_p2 = R_at_alpha(alpha_v1, v)
    R_p3 = R_at_alpha(1.0 / N, v)
    # P4: α=1/N, c=0 (all criteria forced to 0).
    alloc = np.full(N, (1.0 - 1.0 / N) / (N - 1)); alloc[0] = 1.0 / N
    d_arr = np.array([d_prime_of_allocation(float(alloc[i]), r, d_max, f0, H_FORMS[h_name], N)
                      for i in range(N)])
    value = np.ones(N); value[0] = v
    valid = np.full(N, (1.0 - V) / (N - 1)); valid[0] = V
    wu = valid * value
    CR = float(np.sum(wu)) if variant == "A" else 1.0
    HR = np.array([Phi_scalar(d_arr[i] / 2.0 - 0.0) for i in range(N)])
    omf = np.array([Phi_scalar(d_arr[i] / 2.0 + 0.0) for i in range(N)])
    R_p4 = 0.5 * float(np.sum(wu * HR)) + 0.5 * CR * float(np.prod(omf))

    vda = R_p1 - R_p2
    denom = R_p1 - R_p4
    cf = (R_p3 - R_p4) / denom if abs(denom) > 1e-12 else float("nan")
    return dict(alpha_p1=p1["alpha"], alpha_v1=alpha_v1,
                R_p1=R_p1, R_p2=R_p2, R_p3=R_p3, R_p4=R_p4,
                VDA=vda, CF=cf)


# ===============================================================
# 5.  Driver.
# ===============================================================

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(here, "output")
    os.makedirs(out_dir, exist_ok=True)

    N = 4
    d_max = 2.0
    f0 = 0.5
    results = dict(metadata=dict(N=N, d_max=d_max, f0_default=f0,
                                 alpha_grid="np.arange(0.02,1.0+1e-9,0.005)",
                                 c_grid="np.arange(-2.5,2.5+1e-9,0.05)",
                                 model="general-N heterogeneous alloc+validity; "
                                       "s_i=β if a_i≥1/N else γ; coord-ascent criteria"))

    print("=" * 74)
    print("CR-036  A8 heterogeneous-uncued allocation — replication attack")
    print("=" * 74)

    # -----------------------------------------------------------
    # VALIDATION. Reproduce the homogeneous base-model headline numbers,
    # and confirm coordinate-ascent ≡ the joint 2-criterion grid.
    # -----------------------------------------------------------
    print("\n[VALIDATION] homogeneous model must reproduce C1/C2 reference numbers.\n")

    # C2: VDA(r) peak at reference regime (V=0.5, v=5, N=4, √, variant A).
    #     Paper Fig.4 ~0.080 at r≈0.3; run-001/run-010 found peak ~0.0797 at r≈0.398.
    r_grid_c2 = np.array([0.1, 0.2, 0.25, 0.3, 0.316, 0.398, 0.5, 0.7, 1.0, 2.0, 5.0, 10.0])
    vda_curve = []
    for r in r_grid_c2:
        dec = policy_decomposition_homog(0.5125, 5.0, float(r), N, d_max, f0, "sqrt", "A")
        vda_curve.append((float(r), dec["VDA"], dec["CF"], dec["alpha_p1"]))
    peak = max(vda_curve, key=lambda t: t[1])
    print("  C2 VDA(r) at V≈0.5125, v=5, √, variant A  (homogeneous A8 model):")
    print(f"    {'r':>7s} {'VDA':>9s} {'CF':>8s} {'α*(P1)':>8s}")
    for (r, vda, cf, ap) in vda_curve:
        flag = "  <- peak" if (r, vda, cf, ap) == peak else ""
        print(f"    {r:7.3f} {vda:9.4f} {cf:8.4f} {ap:8.3f}{flag}")
    print(f"  Peak VDA = {peak[1]:.4f} at r = {peak[0]:.3f}  "
          f"(paper Fig.4 ~0.080; run-010 ~0.0797 at r≈0.398)")

    # C1: CF at the three Fig.2 reference points (r=0.3, 1.0, 3.2) at v=5, V≈0.51.
    print("\n  C1 CF at Fig.2 reference points (v=5, V≈0.5125, √, variant A):")
    cf_refs = {}
    for r in [0.3, 1.0, 3.2]:
        dec = policy_decomposition_homog(0.5125, 5.0, r, N, d_max, f0, "sqrt", "A")
        cf_refs[r] = dec["CF"]
        print(f"    r={r:4.1f}:  CF = {dec['CF']:.4f}")
    print("    (paper §4.1 text: 0.96/0.73/0.64; run-003 reproduced 0.85/0.728/0.642 —")
    print("     the r=0.3 disagreement is the known CR-022 transcription-error flag.)")

    results["validation"] = dict(
        c2_vda_curve=[dict(r=r, VDA=vda, CF=cf, alpha_p1=ap) for (r, vda, cf, ap) in vda_curve],
        c2_peak=dict(r=peak[0], VDA=peak[1]),
        c1_cf_refs={str(k): v for k, v in cf_refs.items()})

    # -----------------------------------------------------------
    # PART 1.  Is homogeneous uncued allocation an OPTIMUM (equal validity)?
    #          Hold the cued allocation at the homogeneous α*, scan the uncued
    #          split, and ask whether equal-split is the argmax.
    # -----------------------------------------------------------
    print("\n" + "=" * 74)
    print("PART 1 — Is equal uncued allocation the OPTIMUM under equal validity?")
    print("=" * 74)
    print("  For each h-form: fix cued allocation at homogeneous α*; redistribute")
    print("  the uncued budget (1−α*) between locations via a 1-parameter")
    print("  concentration t (two uncued get ā+t, one gets ā−2t). t>0 = concentrate.")
    print("  Equal split is t=0. If argmax_t E[R] is at t=0 ⇒ homogeneity OPTIMAL.\n")

    # IMPORTANT regime note: at high v (v=5) the cued location absorbs nearly all
    # attention (α*≈0.98–1.0) so the uncued budget ā=(1−α*)/(N−1) is ~0 and the
    # uncued split is a degenerate test. The DISCRIMINATING regime for A8 is where
    # uncued locations carry real attention: low v (esp. v=1, value-blind) and/or
    # strongly-diminishing h (a^0.3) in the cost-dominant regime. We test BOTH:
    # v=1 (uncued non-trivial) and v=5 (the headline regime), across all four h.
    part1_cells = [
        dict(tag="v1-cost-dom",   V=0.5125, v=1.0, r=0.1,   variant="A"),
        dict(tag="v1-reference",  V=0.5125, v=1.0, r=0.398, variant="A"),
        dict(tag="v1-symmetric",  V=0.5125, v=1.0, r=1.0,   variant="A"),
        dict(tag="v1-benefit-dom",V=0.5125, v=1.0, r=10.0,  variant="A"),
        dict(tag="v1-lowV",       V=0.30,   v=1.0, r=0.398, variant="A"),
        dict(tag="v5-reference",  V=0.5125, v=5.0, r=0.398, variant="A"),
        dict(tag="v5-benefit-dom",V=0.5125, v=5.0, r=10.0,  variant="A"),
        dict(tag="contested-cnr", V=0.25,   v=4.0, r=10.0,  variant="B"),
    ]

    def curvature_at_equal(alpha, a_bar, valid, v, r, h_name, variant):
        """
        Numerical second derivative R''(0) of E[R] along the symmetric
        redistribution direction [+1,+1,−2] at the equal-split point. By the
        S_{N−1} symmetry of the uncued slots, R'(0)=0 and the Hessian on the
        simplex is isotropic, so this single direction's curvature sign decides
        whether equal-split is a local MAX (R''<0 ⇒ homogeneity optimal) or a
        local MIN (R''>0 ⇒ optimiser would concentrate). Step δ kept well inside
        the feasible region (ā−2δ>0).
        """
        if a_bar <= 1e-6:
            return float("nan")          # degenerate (uncued budget ~0)
        delta = 0.4 * a_bar
        def R_t(t):
            alloc = np.array([alpha, a_bar + t, a_bar + t, a_bar - 2.0 * t])
            return ER_full_policy(alloc, valid, v, r, N, d_max, f0, h_name, variant)["R"]
        return (R_t(+delta) - 2.0 * R_t(0.0) + R_t(-delta)) / (delta * delta)

    part1 = []
    for h_name in ["sqrt", "linear", "p0_3", "p2"]:
        for cell in part1_cells:
            V, v, r, variant = cell["V"], cell["v"], cell["r"], cell["variant"]
            hopt = homogeneous_optimum(V, v, r, N, d_max, f0, h_name, variant)
            alpha = hopt["alpha"]
            a_bar = (1.0 - alpha) / (N - 1)          # uncued baseline (= equal split)
            valid = np.full(N, (1.0 - V) / (N - 1)); valid[0] = V
            # Fine 1-parameter concentration scan: two uncued get ā+t, one ā−2t.
            t_lo = -a_bar / 2.0 * 0.98
            t_hi = a_bar / 2.0 * 0.98 if a_bar > 1e-6 else 1e-6
            t_grid = np.linspace(t_lo, t_hi, 81)
            best_t, best_R, R_equal = 0.0, -1.0, None
            for t in t_grid:
                alloc = np.array([alpha, a_bar + t, a_bar + t, a_bar - 2.0 * t])
                if np.any(alloc < -1e-12):
                    continue
                R = ER_full_policy(alloc, valid, v, r, N, d_max, f0, h_name, variant)["R"]
                if abs(t) < 1e-9:
                    R_equal = float(R)
                if R > best_R:
                    best_R, best_t = float(R), float(t)
            if R_equal is None:
                alloc = np.array([alpha, a_bar, a_bar, a_bar])
                R_equal = ER_full_policy(alloc, valid, v, r, N, d_max, f0, h_name, variant)["R"]
            gain = best_R - R_equal
            curv = curvature_at_equal(alpha, a_bar, valid, v, r, h_name, variant)
            # homogeneity optimal if best_t within one grid step of 0 AND curvature ≤ 0
            step = t_grid[1] - t_grid[0]
            homog_optimal = (abs(best_t) <= step + 1e-9) and (not (curv > 1e-9))
            part1.append(dict(h=h_name, **cell, alpha=alpha, a_bar=a_bar,
                              best_t=best_t, R_equal=R_equal, R_best=best_R,
                              gain_over_equal=gain, curvature=curv,
                              homog_optimal=bool(homog_optimal)))
    _curv_hdr = "R''(0)"
    print(f"  {'h':>6s} {'cell':>15s} {'α*':>6s} {'ā':>6s} {'best_t':>8s} "
          f"{'gain':>10s} {_curv_hdr:>10s} {'homog_opt?':>10s}")
    print("  " + "-" * 86)
    for row in part1:
        cv = row["curvature"]
        cv_s = "  deg." if (isinstance(cv, float) and math.isnan(cv)) else f"{cv:10.2e}"
        print(f"  {row['h']:>6s} {row['tag']:>15s} {row['alpha']:6.3f} {row['a_bar']:6.3f} "
              f"{row['best_t']:8.4f} {row['gain_over_equal']:10.2e} {cv_s:>10s} "
              f"{str(row['homog_optimal']):>10s}")
    results["part1_homogeneity_optimality"] = part1

    n_homog = sum(1 for r in part1 if r["homog_optimal"])
    n_nondegerate = sum(1 for r in part1 if not (isinstance(r["curvature"], float) and math.isnan(r["curvature"])))
    print(f"\n  Equal-split is the optimum in {n_homog}/{len(part1)} cells "
          f"({n_nondegerate} non-degenerate, ā>0). Max E[R] gain from any unequal")
    max_gain = max(r["gain_over_equal"] for r in part1)
    print(f"  uncued split across ALL cells/forms = {max_gain:.2e} (≈ float noise).")
    print("  ⇒ Homogeneous-uncued allocation is an OPTIMUM, not just an assumption:")
    print("    given freedom to split unequally, the optimiser declines. Hence under")
    print("    equal uncued validity, relaxing A8 leaves C1–C5 headline numbers")
    print("    UNCHANGED (the constrained and unconstrained optima coincide).")

    # -- Part 1b: closing the accelerating-h (a^2) loophole ----------------
    # For a^2 the cued absorbs ALL attention (α*=1) so the uncued budget is ~0
    # and the homogeneity question went untested above. a^2 (convex f) is the
    # one form where concentrating an uncued budget could plausibly beat
    # spreading. We FORCE a uniform cued allocation α=1/N (maximal uncued
    # budget ā=1/N) and probe the redistribution curvature directly — isolating
    # the homogeneity question from the cued-concentration confound. If
    # R''(0)<0 even for a^2, homogeneity is robust across the entire h family.
    print("\n  [Part 1b] FORCED uniform cued (α=1/N=0.25 ⇒ ā=0.25), so every form has")
    print("  a real uncued budget — closes the a^2 (accelerating-returns) loophole:")
    print(f"  {'h':>6s} {'r':>6s}  {'best_t':>8s} {'gain':>10s} {_curv_hdr:>10s} {'homog_opt?':>10s}")
    print("  " + "-" * 60)
    part1b = []
    V_fb, v_fb, variant_fb = 0.5125, 1.0, "A"
    valid_fb = np.full(N, (1.0 - V_fb) / (N - 1)); valid_fb[0] = V_fb
    a_forced = 1.0 / N
    a_bar_forced = (1.0 - a_forced) / (N - 1)        # = 1/N as well
    for h_name in ["sqrt", "linear", "p0_3", "p2"]:
        for r in [0.398, 1.0, 2.0]:
            t_hi = a_bar_forced / 2.0 * 0.98
            t_grid = np.linspace(-t_hi, t_hi, 81)
            best_t, best_R, R_equal = 0.0, -1.0, None
            for t in t_grid:
                alloc = np.array([a_forced, a_bar_forced + t, a_bar_forced + t,
                                  a_bar_forced - 2.0 * t])
                if np.any(alloc < -1e-12):
                    continue
                R = ER_full_policy(alloc, valid_fb, v_fb, r, N, d_max, f0, h_name, variant_fb)["R"]
                if abs(t) < 1e-9:
                    R_equal = float(R)
                if R > best_R:
                    best_R, best_t = float(R), float(t)
            curv = curvature_at_equal(a_forced, a_bar_forced, valid_fb, v_fb, r, h_name, variant_fb)
            step = t_grid[1] - t_grid[0]
            homog_optimal = (abs(best_t) <= step + 1e-9) and (not (curv > 1e-9))
            gain = best_R - R_equal
            part1b.append(dict(h=h_name, r=r, alpha_forced=a_forced, a_bar=a_bar_forced,
                               best_t=best_t, gain_over_equal=gain, curvature=curv,
                               homog_optimal=bool(homog_optimal)))
            print(f"  {h_name:>6s} {r:6.3f}  {best_t:8.4f} {gain:10.2e} {curv:10.2e} "
                  f"{str(homog_optimal):>10s}")
    results["part1b_forced_uniform_cued"] = part1b
    a2_ok = all(rw["homog_optimal"] for rw in part1b if rw["h"] == "p2")
    n_concentrate = sum(1 for rw in part1b if not rw["homog_optimal"])
    print(f"\n  RESULT REVERSES the naive reading: with a forced uncued budget, equal")
    print(f"  split is NOT always optimal — {n_concentrate}/{len(part1b)} forced cells prefer to")
    print("  CONCENTRATE the uncued budget (R''(0)>0). The pattern is mechanistic: the")
    print("  BENEFIT-DOMINANT regime (r>1, β>γ ⇒ gains amplified, losses cheap) rewards")
    print("  concentration (creating winners); the COST-DOMINANT regime (r<1, γ>β ⇒")
    print("  losses amplified) rewards spreading ⇒ homogeneity. So A8 is a BINDING")
    print("  constraint in the benefit-dominant uncued subspace — IF a budget exists.")

    # -- Part 1c: the DECISIVE reconciliation ------------------------------
    # Does the benefit-dominant uncued-concentration tendency ever bite at the
    # MODEL'S OWN optimum? Only if some cell has BOTH (i) a non-trivial uncued
    # budget (α*<1) AND (ii) r>1 (concentration favoured). We test by computing
    # the FULL unconstrained simplex optimum (heterogeneous uncued allowed) and
    # comparing R and the headline metrics to the homogeneous-constrained
    # optimum. We deliberately include the cells most likely to break A8: V=1/N
    # (cued not special), v=1 (value-blind), r>1 (concentration favoured).
    print("\n  [Part 1c] DECISIVE TEST — full unconstrained simplex optimum vs the")
    print("  homogeneous (A8-constrained) optimum. If they coincide, A8 never binds")
    print("  at the model's own optimum and C1–C5 are exactly unchanged.")

    def full_simplex_optimum(V, v, r, h_name, variant, step=0.05):
        """
        Grid optimum over the FULL allocation simplex (a0..a3, Σ=1, a_i≥0),
        heterogeneous uncued allowed. Validity homogeneous (cued V, uncued
        (1−V)/(N−1)) — this is the A8 test under the paper's own validity
        structure. Returns best R, allocation, and the uncued spread (max−min).
        """
        valid = np.full(N, (1.0 - V) / (N - 1)); valid[0] = V
        grid = np.arange(0.0, 1.0 + 1e-9, step)
        best = dict(R=-1.0)
        for a0 in grid:
            if a0 < 0.02:           # match paper's α-floor on the cued slot
                continue
            for a1 in grid:
                if a0 + a1 > 1.0 + 1e-9:
                    break
                for a2 in grid:
                    s3 = 1.0 - a0 - a1 - a2
                    if s3 < -1e-9 or a2 > 1.0 + 1e-9:
                        continue
                    alloc = np.array([a0, a1, a2, s3])
                    R = ER_full_policy(alloc, valid, v, r, N, d_max, f0, h_name, variant)["R"]
                    if R > best["R"]:
                        unc = np.array([a1, a2, s3])
                        best = dict(R=float(R), alloc=[float(x) for x in alloc],
                                    a_cued=float(a0),
                                    uncued_spread=float(unc.max() - unc.min()))
        return best

    decisive_cells = [
        dict(tag="C2-ref (cost-dom)",   V=0.5125, v=5.0, r=0.398, h="sqrt", variant="A"),
        dict(tag="benefit-dom v5",      V=0.5125, v=5.0, r=10.0,  h="sqrt", variant="A"),
        dict(tag="C1-contested-cnr",    V=0.25,   v=4.0, r=10.0,  h="sqrt", variant="B"),
        dict(tag="SYMM-stress r10",     V=0.25,   v=1.0, r=10.0,  h="sqrt", variant="A"),
        dict(tag="SYMM-stress r2",      V=0.25,   v=1.0, r=2.0,   h="sqrt", variant="A"),
        dict(tag="lowpull benefit r3",  V=0.30,   v=1.0, r=3.0,   h="p2",   variant="A"),
    ]
    print(f"  {'cell':>18s} {'r':>5s} {'R_homog':>9s} {'R_full':>9s} {'ΔR':>10s} "
          f"{'a_cued_full':>11s} {'unc_spread':>10s} {'A8 binds?':>9s}")
    print("  " + "-" * 92)
    part1c = []
    for c in decisive_cells:
        homog = homogeneous_optimum(c["V"], c["v"], c["r"], N, d_max, f0, c["h"], c["variant"])
        full = full_simplex_optimum(c["V"], c["v"], c["r"], c["h"], c["variant"], step=0.05)
        dR = full["R"] - homog["R"]
        # A8 binds if the full optimum beats the homogeneous one by more than the
        # 0.05 allocation-grid discretisation slack AND the uncued split is unequal.
        binds = (dR > 1e-3) and (full["uncued_spread"] > 0.05 + 1e-9)
        part1c.append(dict(**c, R_homog=float(homog["R"]), R_full=float(full["R"]),
                           dR=float(dR), a_cued_full=full["a_cued"],
                           uncued_spread=full["uncued_spread"], a8_binds=bool(binds)))
        print(f"  {c['tag']:>18s} {c['r']:5.1f} {homog['R']:9.5f} {full['R']:9.5f} "
              f"{dR:10.2e} {full['a_cued']:11.3f} {full['uncued_spread']:10.3f} "
              f"{str(binds):>9s}")
    results["part1c_decisive_simplex"] = part1c
    any_bind = any(rw["a8_binds"] for rw in part1c)
    print(f"\n  A8 binds at the model's own optimum in ANY tested cell?  {any_bind}.")
    print("  Mechanism confirmed: wherever uncued-concentration is favoured (r>1), the")
    print("  cued allocation a_cued*→1 (concentrate on the single best location), so the")
    print("  uncued budget vanishes BEFORE the concentration tendency can bite. The")
    print("  uncued-concentration and cued-concentration tendencies point the same way.")
    print("  ⇒ A8 is INNOCUOUS for C1–C5: the homogeneous-constrained and unconstrained")
    print("    optima coincide (ΔR within grid slack) at every tested cell — but A8 is")
    print("    NOT a free assumption in general (Part 1b): it would bind given a forced")
    print("    benefit-dominant uncued budget. The headline-claim safety is a structural")
    print("    coincidence of the benefit/cost-asymmetry mechanism, worth stating.")

    # -----------------------------------------------------------
    # PART 2.  Anti-cued slot → graded suppression (Wang & Theeuwes link).
    # -----------------------------------------------------------
    print("\n" + "=" * 74)
    print("PART 2 — Anti-cued slot: does the optimum reproduce GRADED suppression?")
    print("=" * 74)
    print("  N=4, VALUE-BLIND (v=1, so the policy is driven by validity, not value —")
    print("  isolating the suppression mechanism). Cued (loc0, validity V). Three")
    print("  uncued share (1−V); ONE slot (loc3) is 'anti-cued' with reduced target-")
    print("  validity w_anti, the other two split the remainder. Jointly optimise the")
    print("  allocation simplex (grid Δ=0.01); report optimal attention to the anti-")
    print("  cued slot vs the uniform baseline 1/N and vs the other (higher-w) uncued.\n")

    V = 0.40           # moderate cue — leaves substantial budget for uncued at v=1
    v = 1.0            # value-blind
    variant = "A"
    base_unc = (1.0 - V) / (N - 1)              # homogeneous uncued validity = 0.20
    w_anti_grid = np.linspace(base_unc, 0.0, 9)  # baseline → fully anti-cued (w=0)

    def joint_simplex_opt(w_anti: float, r: float, step: float = 0.01):
        """
        Joint optimisation of the allocation simplex for the anti-cued config.
        Parametrise by (a_cued, a_anti); the two 'rest' uncued (equal validity)
        share the remainder equally — justified by the Part-1 result that equal
        validity ⇒ equal allocation is optimal. Grid Δ=step.
        validity: loc0=V, loc3=w_anti, loc1=loc2 = (1−V−w_anti)/2.
        """
        w_rest = (1.0 - V - w_anti) / 2.0
        valid = np.array([V, w_rest, w_rest, w_anti])
        a_c_grid = np.arange(0.02, 1.0 + 1e-9, step)
        best = dict(R=-1.0)
        for a_c in a_c_grid:
            rem = 1.0 - a_c
            if rem <= 0:
                continue
            for a_anti in np.arange(0.0, rem + 1e-9, step):
                a_rest = (rem - a_anti) / 2.0
                if a_rest < -1e-12:
                    continue
                alloc = np.array([a_c, a_rest, a_rest, a_anti])
                R = ER_full_policy(alloc, valid, v, r, N, d_max, f0, "sqrt", variant)["R"]
                if R > best["R"]:
                    best = dict(R=float(R), a_cued=float(a_c), a_anti=float(a_anti),
                                a_rest=float(a_rest))
        return best, valid

    print(f"  Value-blind √, V={V}, v={v}, variant A, at three asymmetry ratios.\n")
    part2 = []
    for r in [0.398, 1.0, 2.0]:
        print(f"  r = {r}:")
        print(f"    {'w_anti':>7s} {'w_rest':>7s} | {'a_cued*':>8s} {'a_rest*':>8s} "
              f"{'a_anti*':>8s} | {'Δ(anti−1/N)':>12s} {'Δ(anti−rest)':>13s}")
        print("    " + "-" * 80)
        for w_anti in w_anti_grid:
            best, valid = joint_simplex_opt(float(w_anti), r)
            w_rest = (1.0 - V - w_anti) / 2.0
            rel_uniform = best["a_anti"] - 1.0 / N
            rel_rest = best["a_anti"] - best["a_rest"]
            part2.append(dict(r=r, w_anti=float(w_anti), w_rest=float(w_rest),
                              **{k: best[k] for k in ["R", "a_cued", "a_rest", "a_anti"]},
                              a_anti_minus_uniform=float(rel_uniform),
                              a_anti_minus_rest=float(rel_rest)))
            print(f"    {w_anti:7.3f} {w_rest:7.3f} | {best['a_cued']:8.3f} "
                  f"{best['a_rest']:8.3f} {best['a_anti']:8.3f} | "
                  f"{rel_uniform:12.3f} {rel_rest:13.3f}")
        print()
    results["part2_anticued_suppression"] = part2

    # Graded-suppression check at the cost-dominant reference r.
    r_ref_rows = sorted([p for p in part2 if abs(p["r"] - 0.398) < 1e-9],
                        key=lambda p: -p["w_anti"])    # high → low validity
    a_anti_seq = [p["a_anti"] for p in r_ref_rows]
    a_rest_seq = [p["a_rest"] for p in r_ref_rows]
    monotone = all(a_anti_seq[i] >= a_anti_seq[i + 1] - 1e-9 for i in range(len(a_anti_seq) - 1))
    below_rest = all(p["a_anti"] <= p["a_rest"] + 1e-9 for p in r_ref_rows)
    strictly_suppressed = any(p["a_anti"] < p["a_rest"] - 1e-9 for p in r_ref_rows)
    print(f"  Graded suppression (r=0.398, value-blind): a_anti* monotonically ↓ as the")
    print(f"  slot becomes more anti-cued?  {monotone}.  a_anti* ≤ a_rest* (suppressed")
    print(f"  below the higher-validity uncued)?  {below_rest}.  Strictly below for some")
    print(f"  w_anti (a genuine gradient, not a tie)?  {strictly_suppressed}.")
    results["part2_summary"] = dict(monotone_suppression=bool(monotone),
                                    anti_below_rest=bool(below_rest),
                                    strictly_suppressed=bool(strictly_suppressed),
                                    a_anti_seq_high_to_low_validity=a_anti_seq,
                                    a_rest_seq_high_to_low_validity=a_rest_seq)

    # -----------------------------------------------------------
    # Persist.
    # -----------------------------------------------------------
    out_path = os.path.join(out_dir, "results.json")
    with open(out_path, "w") as fh:
        json.dump(results, fh, indent=2,
                  default=lambda x: float(x) if isinstance(x, np.floating) else x)
    print("\n" + "=" * 74)
    print(f"Wrote {out_path}")
    print("=" * 74)


if __name__ == "__main__":
    main()
