"""
CR-045 — numerical corroboration of the A8 homogeneity-optimality / cued-
absorption RE-DERIVATION (Critique/derivations/A8--homogeneity-optimality.md).

This is a *companion verification* for a re-derivation attack, not a fresh
replication: it confirms the closed-form claims of the derivation independently
of CR-036's run.py. Specifically it checks

  (V1) equal-split is an exact critical point of E[R] on the uncued simplex
       (the exchange-symmetry argument; first derivative = 0);
  (V2) the closed-form restricted-Hessian eigenvalue  λ  (smooth γ-branch,
       fixed-criterion analytic terms) matches a finite-difference R''(0)
       computed with FULLY RE-OPTIMISED criteria, in sign and approximate
       magnitude, across regimes — and reproduces CR-036's reported numbers
       (R''(0) ≈ −2.26 at r=0.1 value-blind along [+1,+1,−2]; positive at
       benefit-dominant forced-budget cells);
  (V3) the β/γ KINK mechanism: at the FORCED uncued budget (α=1/N ⇒ ā=1/N,
       uncued sit *at* the kink) the benefit-dominant r>1 regime flips R''(0)
       to >0 (concentration), while the cost-dominant r<1 regime keeps it <0;
  (V4) CUED-ABSORPTION: at headline cells (v>1, benefit-dominant) the joint
       optimum over (α, uncued split) has uncued spread = 0 and α*→1, so the
       uncued budget B=1−α* is driven small and A8 never binds.

SDT primitives identical to the C4/C5/A8 substrate (math.erf, no scipy).

CR-045, prompt v0.2, run-013, 2026-05-24.
"""
from __future__ import annotations
import math
import itertools
import numpy as np

_SQRT2 = math.sqrt(2.0)
_SQRT_2PI = math.sqrt(2.0 * math.pi)

def Phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / _SQRT2))

def phi(x: float) -> float:  # standard normal pdf
    return math.exp(-0.5 * x * x) / _SQRT_2PI

# ----- model primitives (paper §2.3–2.4) -----
H = {
    "linear": lambda a: a,
    "sqrt":   lambda a: math.sqrt(a),
    "p0_3":   lambda a: a ** 0.3,
    "p2":     lambda a: a ** 2.0,
}

def f_transfer(a, f0, h):
    return f0 + (1.0 - f0) * h(a)

def beta_gamma(r):
    return 2.0 * r / (r + 1.0), 2.0 / (r + 1.0)

def dprime(a, r, dmax, f0, h, N):
    a = min(max(a, 0.0), 1.0)
    b, g = beta_gamma(r)
    dbase = dmax * f_transfer(1.0 / N, f0, h)
    dep = dmax * f_transfer(a, f0, h) - dbase
    s = b if a >= 1.0 / N else g
    return max(dbase + s * dep, 0.0)

# ----- exact criterion optimiser over GROUPS (joint grid for G<=2; multi-
#       restart coordinate ascent for G>=3) — identical logic to A8 run.py -----
_CGRID = np.arange(-2.5, 2.5 + 1e-9, 0.05)

def _hr_omf(d):
    """HR and (1-FAR) over the c-grid for sensitivity d."""
    hr = np.array([Phi(d / 2.0 - c) for c in _CGRID])
    omf = np.array([Phi(d / 2.0 + c) for c in _CGRID])  # 1-FAR = Φ(d/2+c)
    return hr, omf

def optimal_ER(d_list, wu_list, n_list, CR):
    """max over per-group criteria of
       E[R] = 0.5 Σ_g n_g wu_g HR_g + 0.5 CR Π_g (1-FAR_g)^{n_g}."""
    G = len(d_list)
    grids = [_hr_omf(d) for d in d_list]
    if G == 1:
        hr, omf = grids[0]
        val = 0.5 * n_list[0] * wu_list[0] * hr + 0.5 * CR * omf ** n_list[0]
        k = int(np.argmax(val)); return float(val[k]), [float(_CGRID[k])]
    if G == 2:
        (h0, o0), (h1, o1) = grids
        # outer product over the two c-grids
        HRsum = (0.5 * n_list[0] * wu_list[0] * h0)[:, None] + \
                (0.5 * n_list[1] * wu_list[1] * h1)[None, :]
        PROD = 0.5 * CR * (o0[:, None] ** n_list[0]) * (o1[None, :] ** n_list[1])
        val = HRsum + PROD
        i, j = np.unravel_index(int(np.argmax(val)), val.shape)
        return float(val[i, j]), [float(_CGRID[i]), float(_CGRID[j])]
    # G>=3 : multi-restart coordinate ascent (each step exact 1-D argmax)
    def total(cidx):
        hrsum = sum(0.5 * n_list[g] * wu_list[g] * grids[g][0][cidx[g]] for g in range(G))
        prod = 1.0
        for g in range(G):
            prod *= grids[g][1][cidx[g]] ** n_list[g]
        return hrsum + 0.5 * CR * prod
    seeds = []
    for corner in itertools.product([0, 1], repeat=G):
        seeds.append([int(np.argmax(grids[g][0])) if corner[g] == 0
                      else int(np.argmax(grids[g][1])) for g in range(G)])
    seeds.append([int(np.argmin(np.abs(_CGRID)))] * G)  # all c≈0
    best = -1e18; bestc = None
    for seed in seeds:
        cidx = list(seed); improved = True
        while improved:
            improved = False
            for g in range(G):
                # exact 1-D argmax for group g holding others
                P_other = 1.0
                for gg in range(G):
                    if gg != g:
                        P_other *= grids[gg][1][cidx[gg]] ** n_list[gg]
                col = 0.5 * n_list[g] * wu_list[g] * grids[g][0] + \
                      0.5 * CR * P_other * grids[g][1] ** n_list[g]
                k = int(np.argmax(col))
                if k != cidx[g]:
                    cidx[g] = k; improved = True
        v = total(cidx)
        if v > best:
            best = v; bestc = cidx
    return float(best), [float(_CGRID[k]) for k in bestc]

# ----- E[R] for an explicit allocation vector (loc 0 cued), criteria optimised
def ER_alloc(alloc, r, N, dmax, f0, hname, V, v, variant):
    h = H[hname]
    w = [V] + [(1.0 - V) / (N - 1)] * (N - 1)
    u = [v] + [1.0] * (N - 1)
    CR = (V * v + (1.0 - V)) if variant == "A" else 1.0
    ds = [dprime(alloc[i], r, dmax, f0, h, N) for i in range(N)]
    # group by (rounded d', wu) to exploit symmetry
    groups = {}
    for i in range(N):
        key = (round(ds[i], 12), round(w[i] * u[i], 12))
        groups.setdefault(key, [0, key[0], key[1]])[0] += 1
    d_list = [g[1] for g in groups.values()]
    wu_list = [g[2] for g in groups.values()]
    n_list = [g[0] for g in groups.values()]
    R, _ = optimal_ER(d_list, wu_list, n_list, CR)
    return R

# =====================================================================
print("=" * 70)
print("CR-045 numerical corroboration of the A8 re-derivation")
print("=" * 70)

N, dmax, f0 = 4, 2.0, 0.5

# ---------- (V1)+(V2)+(V3): R''(0) along uncued redistribution ----------
def Rpp_exchange(alpha, r, hname, V, v, variant, direction, eps=1e-3):
    """Finite-diff 2nd derivative of E[R] (criteria re-optimised) along a
       zero-sum uncued redistribution `direction` (length N-1), budget fixed."""
    base_unc = (1.0 - alpha) / (N - 1)
    def alloc_at(t):
        a = [alpha] + [base_unc + t * direction[j] for j in range(N - 1)]
        return a
    R0 = ER_alloc(alloc_at(0.0), r, N, dmax, f0, hname, V, v, variant)
    Rp = ER_alloc(alloc_at(+eps), r, N, dmax, f0, hname, V, v, variant)
    Rm = ER_alloc(alloc_at(-eps), r, N, dmax, f0, hname, V, v, variant)
    first = (Rp - Rm) / (2 * eps)
    second = (Rp - 2 * R0 + Rm) / (eps * eps)
    return R0, first, second

dir_112 = [1.0, 1.0, -2.0]   # CR-036's symmetric direction (N-1=3)
dir_1m1 = [1.0, -1.0, 0.0]   # pure two-location exchange

print("\n[V1/V2] equal-split critical point + R''(0) sign vs regime")
print("  value-blind (v=1), cued held at the HOMOGENEOUS optimum α* per cell")
print("  (α* found by scanning the 1-D homogeneous policy, Δα=0.005)")

def homog_opt_alpha(r, hname, V, v, variant):
    best = (-1e18, None)
    a = 1.0 / N
    while a <= 1.0 + 1e-9:
        R = ER_alloc([a] + [(1 - a) / (N - 1)] * (N - 1), r, N, dmax, f0, hname, V, v, variant)
        if R > best[0]:
            best = (R, a)
        a += 0.005
    return best[1]

for r in [0.1, 0.398, 1.0, 2.0, 5.0]:
    astar = homog_opt_alpha(r, "sqrt", 0.5, 1, "A")
    R0, d1, d2_112 = Rpp_exchange(astar, r, "sqrt", 0.5, 1, "A", dir_112)
    _, _, d2_11 = Rpp_exchange(astar, r, "sqrt", 0.5, 1, "A", dir_1m1)
    lam_from_112 = d2_112 / 6.0   # |[1,1,-2]|^2 = 6
    lam_from_11 = d2_11 / 2.0     # |[1,-1,0]|^2 = 2
    print(f"  r={r:5.3f}  α*={astar:5.3f}  ā=(1-α*)/(N-1)={ (1-astar)/(N-1):5.3f}"
          f"  R'(0)={d1:+.2e}  R''[112]={d2_112:+.4f}"
          f"  λ(112)={lam_from_112:+.4f}  λ(1,-1)={lam_from_11:+.4f}")

print("\n[V3] FORCED uncued budget α=1/N (ā=1/N, uncued sit AT the β/γ kink):")
print("  benefit-dominant r>1 should give R''(0)>0 (concentration);")
print("  cost-dominant r<1 should give R''(0)<0 (spreading).")
for hname in ["sqrt", "linear", "p0_3", "p2"]:
    row = []
    for r in [0.5, 1.0, 2.0]:
        _, _, d2 = Rpp_exchange(1.0 / N, r, hname, 0.5, 1, "A", dir_112)
        row.append(f"r={r}: R''={d2:+.3f}")
    print(f"  h={hname:7s}  " + "   ".join(row))

print("\n[V3b] reproduce CR-036's headline: value-blind, FORCED α=1/N, r=2:")
for hname in ["linear", "sqrt", "p0_3", "p2"]:
    _, _, d2 = Rpp_exchange(1.0 / N, 2.0, hname, 0.5, 1, "A", dir_112)
    print(f"  h={hname:7s}  R''(0)[112] at r=2 = {d2:+.4f}  -> "
          f"{'CONCENTRATE (>0)' if d2 > 0 else 'spread (<0)'}")
print("  and cost-dominant r=0.1 value-blind (expect ≈ -2.26 per CR-036):")
_, _, d2 = Rpp_exchange(1.0 / N, 0.1, "sqrt", 0.5, 1, "A", dir_112)
print(f"  h=sqrt r=0.1 forced: R''(0)[112] = {d2:+.4f}")

# ---------- (V4): CUED-ABSORPTION at headline cells ----------
print("\n[V4] CUED-ABSORPTION: joint optimum over (α, ONE uncued winner share).")
print("  Parameterise uncued split by w∈[0,1]: winner gets w·(1-α), the other")
print("  N-2 share (1-w)(1-α) equally. w=1/(N-1) is the HOMOGENEOUS split.")
print("  Report α*, winner share, and whether the optimum breaks homogeneity.")

def joint_opt_winner(r, hname, V, v, variant, dA=0.02, dW=0.05):
    h = H[hname]
    best = (-1e18, None, None)
    a = 1.0 / N
    while a <= 1.0 + 1e-9:
        B = 1.0 - a
        w = 0.0
        while w <= 1.0 + 1e-9:
            winner = w * B
            other = (1 - w) * B / (N - 2) if N > 2 else 0.0
            alloc = [a, winner] + [other] * (N - 2)
            R = ER_alloc(alloc, r, N, dmax, f0, hname, V, v, variant)
            if R > best[0]:
                best = (R, a, w)
            w += dW
        a += dA
    return best  # (R, alpha*, winnershare*)

homog_w = 1.0 / (N - 1)
for (V, v, variant, tag) in [
    (0.5, 5, "A", "C2-ref benefit cell (v=5)"),
    (0.25, 4, "B", "C1-contested corner (V=1/N,v=4,B)"),
    (0.5, 5, "A", "repeat"),
    (0.75, 5, "A", "high-V v=5"),
]:
    for r in [0.398, 2.0, 10.0]:
        R, astar, wstar = joint_opt_winner(r, "sqrt", V, v, variant)
        homog = "HOMOG" if abs(wstar - homog_w) < 0.051 else f"BROKEN(w*={wstar:.2f})"
        print(f"  {tag:34s} r={r:5.2f}  α*={astar:5.3f}  B=1-α*={1-astar:5.3f}"
              f"  winner*={wstar:4.2f} (homog={homog_w:.3f}) -> {homog}")
    print()

print("=" * 70)
print("done")
