#!/usr/bin/env python3
# =====================================================================
# CR-048 / run-015 — A2 second attack vector (re-derivation), numerical
# corroboration of the A2xA8 interaction.
#
# QUESTION (mission A2, paper §2.4). The paper governs the benefit/cost
# asymmetry by a SINGLE GLOBAL ratio r (β(r)=2r/(r+1), γ(r)=2/(r+1)).
# CR-007/run-014 settled the empirical premise (within-display
# heterogeneity R2 is real) and conjectured the C1–C5 consequence is
# bounded. CR-045/run-013 proved A8 (homogeneous-uncued allocation) is
# the OPTIMUM — but its exchange-symmetry argument REQUIRES a single
# global r. This script tests, with a per-location ratio vector r_i,
# whether:
#
#   (a) equal-split stays a CRITICAL POINT of the uncued simplex
#       (the derivation predicts: generically NO — tangent gradient
#        nonzero, ∝ spread of the uncued γ_i; exactly zero iff r_i equal);
#   (b) the ALLOCATION deviation ΔR = V(uncued-simplex-opt) − V(equal)
#       scales as O(var r_i) on the cost-dominant branch and is
#       PRE-EMPTED to ~0 by cued-absorption at benefit-dominant cells
#       (the C4/CR-045 §4 mechanism is structurally r-INDEPENDENT);
#   (c) a ±30% uncued spread shifts any C1/C2 headline number — in
#       particular whether the C2 non-monotonic VDA peak survives in
#       the CUED ratio r_cued (run-014's "reframes not refutes").
#
# The model primitives are imported from the VALIDATED general-N
# replication (CR-036/CR-045); only the d'-map is generalised so each
# location carries its own r_i. Notation: mission §2.
# =====================================================================

import math
import sys
import json
import numpy as np

# Import the validated substrate (CR-036/run-012, bug-fixed + machine-
# precision-validated against the C4/C5 optimiser in CR-045/run-013).
sys.path.insert(0, "/sessions/bold-nifty-hamilton/mnt/AttentionManuscript/"
                    "Critique/replications/A8--heterogeneous-uncued")
import run as base  # noqa: E402

Phi_scalar = base.Phi_scalar
f_transfer = base.f_transfer
beta_gamma = base.beta_gamma
optimal_ER_general = base.optimal_ER_general
H_FORMS = base.H_FORMS

# Reference regime (mission §2 / CR-001 / paper Fig. 4).
N      = 4
D_MAX  = 2.0
F0     = 0.5
H_NAME = "sqrt"
H      = H_FORMS[H_NAME]


# ---------------------------------------------------------------------
# 0.  Heterogeneous-r d' map and reward.
#
#     d'_i = max( d'_base + s_i·[d'_max f(a_i) − d'_base], 0 ),
#     s_i  = β(r_i) if a_i ≥ 1/N (gain) else γ(r_i) (loss).
#
#     d'_base = d'_max·f(1/N) is r-INDEPENDENT (paper Eq. 4), so a
#     per-location r_i changes only the per-location SCALING s_i of the
#     departure, never the common baseline. This is the unique
#     generalisation consistent with paper Eqs. (7)–(8) and the §2.3
#     reversal note, with the global r promoted to a vector r_i.
# ---------------------------------------------------------------------
def d_prime_hetero(a_i, r_i, N=N, d_max=D_MAX, f0=F0, h=H):
    a_i = float(min(max(a_i, 0.0), 1.0))
    beta_i, gamma_i = beta_gamma(r_i)                  # this location's β,γ
    d_base = d_max * f_transfer(1.0 / N, f0, h)        # r-independent baseline
    departure = d_max * f_transfer(a_i, f0, h) - d_base
    s_i = beta_i if a_i >= 1.0 / N else gamma_i         # gain vs loss branch
    return max(d_base + s_i * departure, 0.0)


def ER_hetero(alloc, valid, value, r_vec, variant="A"):
    """E[R] at a full allocation+validity+value vector with a per-location
    ratio vector r_vec, criteria optimised (paper Eq. 9 generalised).
    Groups locations by (d', wu) so equal-d' equal-weight slots share a
    criterion; under heterogeneous r the uncued d' generally differ →
    each its own group (G up to N)."""
    alloc = np.asarray(alloc, float); valid = np.asarray(valid, float)
    value = np.asarray(value, float); r_vec = np.asarray(r_vec, float)
    d_arr = np.array([d_prime_hetero(alloc[i], r_vec[i]) for i in range(len(alloc))])
    wu_arr = valid * value
    CR = float(np.sum(wu_arr)) if variant == "A" else 1.0
    groups = {}
    for i in range(len(alloc)):
        key = (round(float(d_arr[i]), 9), round(float(wu_arr[i]), 12))
        groups.setdefault(key, []).append(i)
    d_list = [k[0] for k in groups]
    wu_list = [k[1] for k in groups]
    n_list = [len(groups[k]) for k in groups]
    res = optimal_ER_general(d_list, wu_list, n_list, CR)
    return res["R"]


def value_vec(v):
    val = np.ones(N); val[0] = v; return val


def valid_vec(V):
    vv = np.full(N, (1.0 - V) / (N - 1)); vv[0] = V; return vv


def uncued_r_spread(r_cued, spread):
    """r vector: cued = r_cued; the N−1=3 uncued = r_cued·{1−s,1,1+s}
    (a ±100·s % linear spread around the global ratio). spread=0 ⇒
    homogeneous (recovers the paper's single-r model exactly)."""
    facs = np.array([1.0 - spread, 1.0, 1.0 + spread])   # N-1 = 3 uncued
    return np.concatenate(([r_cued], r_cued * facs))


# ---------------------------------------------------------------------
# 1.  CRITICALITY TEST (derivation §1): is equal-split a critical point?
#     Compute free partials g_i = ∂V/∂a_i at the uncued slots (criteria
#     re-optimised), at fixed cued α. The tangent gradient on the uncued
#     simplex is g_i − mean(g_uncued); zero iff equal-split is critical.
# ---------------------------------------------------------------------
def tangent_gradient(alpha, V, v, r_vec, variant="A", eps=1e-4):
    val = value_vec(v); vld = valid_vec(V)
    B = 1.0 - alpha
    a_bar = B / (N - 1)
    base_alloc = np.concatenate(([alpha], np.full(N - 1, a_bar)))
    g = np.zeros(N - 1)
    for j in range(1, N):                       # uncued slots 1..N-1
        ap = base_alloc.copy(); ap[j] += eps
        am = base_alloc.copy(); am[j] -= eps
        g[j - 1] = (ER_hetero(ap, vld, val, r_vec, variant)
                    - ER_hetero(am, vld, val, r_vec, variant)) / (2 * eps)
    tang = g - g.mean()                          # project onto Σδ=0
    return g, tang


# ---------------------------------------------------------------------
# 2.  ALLOCATION-DEVIATION TEST (derivation §2/§4): at fixed cued α,
#     ΔR = V(uncued-simplex-opt) − V(equal-split) ≥ 0. Grid the 2-D
#     uncued simplex (N=4) at the given step; criteria optimised at each.
# ---------------------------------------------------------------------
def uncued_simplex_best(alpha, V, v, r_vec, variant="A", step=0.01):
    val = value_vec(v); vld = valid_vec(V)
    B = 1.0 - alpha
    # equal split reference
    a_bar = B / (N - 1)
    R_equal = ER_hetero(np.concatenate(([alpha], np.full(N - 1, a_bar))),
                        vld, val, r_vec, variant)
    # grid the 2-D uncued simplex {b1,b2 ≥0, b1+b2 ≤ B}; b3 = B−b1−b2
    best = R_equal; best_alloc = None
    ks = np.arange(0.0, B + 1e-9, step)
    for b1 in ks:
        for b2 in ks:
            b3 = B - b1 - b2
            if b3 < -1e-9:
                continue
            alloc = np.array([alpha, b1, b2, max(b3, 0.0)])
            R = ER_hetero(alloc, vld, val, r_vec, variant)
            if R > best:
                best = R; best_alloc = alloc
    return R_equal, best, best - R_equal, best_alloc


# ---------------------------------------------------------------------
# 3.  HEADLINE NUMBERS under heterogeneity, A8 IMPOSED (paper's equal
#     uncued split; A2 relaxed). 1-D α policy → exact, fast. This is the
#     LEVEL effect of A2 on C1/C2.
# ---------------------------------------------------------------------
_ALPHA_GRID = np.arange(0.02, 1.0 + 1e-9, 0.02)    # coarse α (peak/CF to grid-step;
                                                   # validated vs run-003/012 below)


def homog_alloc(alpha, V):
    alloc = np.full(N, (1.0 - alpha) / (N - 1)); alloc[0] = alpha
    return alloc


def best_alpha_hetero(V, v, r_cued, spread, variant="A"):
    """P1 under A8-imposed equal uncued split, per-location r."""
    r_vec = uncued_r_spread(r_cued, spread)
    vld = valid_vec(V); val = value_vec(v)
    bestR, bestA = -1.0, float("nan")
    for a in _ALPHA_GRID:
        R = ER_hetero(homog_alloc(a, V), vld, val, r_vec, variant)
        if R > bestR:
            bestR, bestA = R, float(a)
    return bestR, bestA, r_vec


def vda_cf_hetero(V, v, r_cued, spread, variant="A"):
    """VDA = R(P1)−R(P2); CF = (R(P3)−R(P4))/(R(P1)−R(P4)). A8 imposed,
    per-location r. P2 fixes α at α*(v=1)."""
    r_vec = uncued_r_spread(r_cued, spread)
    vld = valid_vec(V)
    R_p1, a_star, _ = best_alpha_hetero(V, v, r_cued, spread, variant)
    _, a_v1, _ = best_alpha_hetero(V, 1.0, r_cued, spread, variant)

    def R_at(a, vv):
        return ER_hetero(homog_alloc(a, V), vld, value_vec(vv), r_vec, variant)

    R_p2 = R_at(a_v1, v)
    R_p3 = R_at(1.0 / N, v)
    # P4: α=1/N, criteria forced to 0.
    alloc = homog_alloc(1.0 / N, V)
    d_arr = np.array([d_prime_hetero(alloc[i], r_vec[i]) for i in range(N)])
    wu = vld * value_vec(v)
    CR = float(np.sum(wu)) if variant == "A" else 1.0
    HR = np.array([Phi_scalar(d_arr[i] / 2.0) for i in range(N)])
    omf = np.array([Phi_scalar(d_arr[i] / 2.0) for i in range(N)])  # 1−FAR at c=0
    R_p4 = 0.5 * float(np.sum(wu * HR)) + 0.5 * CR * float(np.prod(omf))
    VDA = R_p1 - R_p2
    denom = R_p1 - R_p4
    CF = (R_p3 - R_p4) / denom if abs(denom) > 1e-12 else float("nan")
    return dict(VDA=VDA, CF=CF, alpha=a_star, R_p1=R_p1, R_p2=R_p2,
                R_p3=R_p3, R_p4=R_p4)


def vda_peak(V, v, spread, variant="A", rgrid=None):
    """Sweep r_cued, return peak VDA and its location (A8 imposed)."""
    if rgrid is None:
        rgrid = np.geomspace(0.1, 10.0, 21)   # paper's log r-grid (21 pts, run-003)
    vdas = np.array([vda_cf_hetero(V, v, float(r), spread, variant)["VDA"]
                     for r in rgrid])
    k = int(np.argmax(vdas))
    return dict(r_peak=float(rgrid[k]), vda_peak=float(vdas[k]),
                rgrid=rgrid.tolist(), vdas=vdas.tolist())


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def main():
    out = {}
    sep = "=" * 64

    # ---- VALIDATION: spread=0 must reproduce the homogeneous baseline.
    print(sep); print("VALIDATION — spread=0 reduces to the single-r model")
    pk0 = vda_peak(0.5, 5.0, 0.0, "A")
    cf_ref = {f"r={r}": round(vda_cf_hetero(0.5, 5.0, r, 0.0, "A")["CF"], 4)
              for r in (0.3, 1.0, 3.2)}
    print(f"  C2 peak (homog): VDA*={pk0['vda_peak']:.4f} at r_cued={pk0['r_peak']:.3f}"
          f"   [paper Fig4 ~0.080 @ r≈0.3; run-010/012 0.0769–0.0797]")
    print(f"  C1 CF (homog) at r=0.3/1.0/3.2: {cf_ref}"
          f"   [run-003: 0.85/0.73/0.64]")
    out["validation"] = dict(c2_peak_homog=pk0["vda_peak"],
                             r_peak_homog=pk0["r_peak"], cf_ref=cf_ref)

    # ---- (a) CRITICALITY: equal-split critical iff r_i equal.
    print(sep); print("(a) CRITICALITY of equal-split on the uncued simplex")
    # cost-dominant cell with large uncued budget (C2-peak neighbourhood).
    r_cd = 0.4
    _, a_cd, _ = best_alpha_hetero(0.5, 5.0, r_cd, 0.0, "A")
    print(f"  cell: V=0.5 v=5 variant A, r_cued={r_cd}, α*≈{a_cd:.3f} (B≈{1-a_cd:.3f})")
    for spread in (0.0, 0.3):
        r_vec = uncued_r_spread(r_cd, spread)
        g, tang = tangent_gradient(a_cd, 0.5, 5.0, r_vec, "A")
        print(f"  spread={spread:.1f}  uncued r_i={np.round(r_vec[1:],3).tolist()}")
        print(f"      free partials g_i = {np.round(g,5).tolist()}")
        print(f"      tangent grad g_i−mean = {np.round(tang,6).tolist()}"
              f"   ||tang||={np.linalg.norm(tang):.2e}")
        out[f"crit_spread_{spread}"] = dict(g=g.tolist(), tang=tang.tolist(),
                                            tang_norm=float(np.linalg.norm(tang)))

    # ---- (b) ALLOCATION DEVIATION scaling + cued-absorption pre-emption.
    print(sep); print("(b) ALLOCATION DEVIATION  ΔR = V(simplex-opt) − V(equal)")
    print("  b1) COST-DOMINANT (r_cued=0.4): expect ΔR small, ∝ var(r_i)")
    dev_cd = {}
    for spread in (0.0, 0.1, 0.2, 0.3):
        r_vec = uncued_r_spread(r_cd, spread)
        Re, Rb, dR, alc = uncued_simplex_best(a_cd, 0.5, 5.0, r_vec, "A", step=0.02)
        var_r = float(np.var(r_vec[1:]))
        print(f"     spread={spread:.1f} var(r_i)={var_r:.5f}  "
              f"ΔR={dR:.3e}  best_uncued={None if alc is None else np.round(alc[1:],3).tolist()}")
        dev_cd[f"{spread}"] = dict(dR=dR, var_r=var_r)
    out["dev_cost_dominant"] = dev_cd

    print("  b2) BENEFIT-DOMINANT (r_cued=3.0, V=0.5,v=5): expect α*→1, B→0, ΔR≈0")
    _, a_bd, _ = best_alpha_hetero(0.5, 5.0, 3.0, 0.3, "A")
    r_vec = uncued_r_spread(3.0, 0.3)
    Re, Rb, dR, alc = uncued_simplex_best(a_bd, 0.5, 5.0, r_vec, "A", step=0.02)
    print(f"     α*≈{a_bd:.3f}  B≈{1-a_bd:.3f}  ΔR(±30%)={dR:.3e}")
    out["dev_benefit_dominant"] = dict(alpha=a_bd, B=1 - a_bd, dR=dR)

    # ---- (c) C2 REFRAMING: does the non-monotonic VDA peak survive in
    #          r_cued under ±30% uncued spread? (run-014 conjecture)
    print(sep); print("(c) C2 REFRAMING — VDA-vs-r_cued peak under uncued spread")
    c2 = {}
    for spread in (0.0, 0.1, 0.2, 0.3):
        pk = vda_peak(0.5, 5.0, spread, "A")
        print(f"  spread={spread:.1f}  VDA*={pk['vda_peak']:.4f} @ r_cued={pk['r_peak']:.3f}")
        c2[f"{spread}"] = dict(vda_peak=pk["vda_peak"], r_peak=pk["r_peak"])
    out["c2_reframe"] = c2
    # also test the larger asymmetric spread k∈{1.5,3} from CR-049 plan
    print("  larger spreads (uncued r_i = r_cued·{1/k,1,k}):")
    c2_mult = {}
    for k in (1.5, 3.0):
        rgrid = np.geomspace(0.1, 10.0, 41)
        vdas = []
        for rc in rgrid:
            r_vec = np.array([rc, rc / k, rc, rc * k])
            vld = valid_vec(0.5)
            # P1
            bestR = max(ER_hetero(homog_alloc(a, 0.5), vld, value_vec(5.0), r_vec, "A")
                        for a in _ALPHA_GRID)
            # P2 (α at v=1 optimum)
            a_v1 = max(_ALPHA_GRID,
                       key=lambda a: ER_hetero(homog_alloc(a, 0.5), vld, value_vec(1.0), r_vec, "A"))
            R_p2 = ER_hetero(homog_alloc(a_v1, 0.5), vld, value_vec(5.0), r_vec, "A")
            vdas.append(bestR - R_p2)
        vdas = np.array(vdas); kk = int(np.argmax(vdas))
        print(f"     k={k}: VDA*={vdas[kk]:.4f} @ r_cued={rgrid[kk]:.3f}")
        c2_mult[f"k={k}"] = dict(vda_peak=float(vdas[kk]), r_peak=float(rgrid[kk]))
    out["c2_reframe_mult"] = c2_mult

    # ---- C1 contested corner under ±30% spread (level effect).
    print(sep); print("C1 contested corner (r_cued=10, V=0.25, v=4, variant B)")
    for spread in (0.0, 0.3):
        d = vda_cf_hetero(0.25, 4.0, 10.0, spread, "B")
        print(f"  spread={spread:.1f}  CF={d['CF']:.4f}  α*={d['alpha']:.3f}"
              f"   [additive homog CF≈0.304 (run-003/011)]")
        out[f"c1_corner_spread_{spread}"] = dict(CF=d["CF"], alpha=d["alpha"])

    # determinism hash
    with open("/sessions/bold-nifty-hamilton/mnt/AttentionManuscript/Critique/"
              "replications/A2xA8--heterogeneous-r/output/results.json", "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print(sep); print("results.json written.")


if __name__ == "__main__":
    main()
