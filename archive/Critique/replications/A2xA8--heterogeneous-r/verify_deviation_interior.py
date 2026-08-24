#!/usr/bin/env python3
# =====================================================================
# CR-048 / run-015 — Part 2: the ALLOCATION-deviation magnitude at
# INTERIOR-α cells (where the uncued budget B = 1−α* is non-trivial).
#
# Part 1 (verify_heterogeneous_r.py) found the P1 optimum at the C2
# headline cell is fully cued-absorbed (α*=1, B=0), so the A2×A8
# allocation interaction is trivially 0 there. The budget that DOES
# survive lives in the value-blind policies P2 (α=α*(v=1)) and P3
# (α=1/N) — which feed VDA and the criterion fraction. This script
# measures, at those interior cells, the deviation
#       ΔR(spread) = V(uncued-simplex-opt) − V(equal-split)
# with a FINE search, to test the derivation's two claims:
#   (i)  ΔR scales as O(var r_i)  (second order in the spread), and
#   (ii) ΔR stays within the homogeneous-case slack (CR-045: 1.4e-4),
#        i.e. relaxing A8 under heterogeneous r does not move a
#        headline number.
# =====================================================================
import importlib.util, sys, json
import numpy as np

spec = importlib.util.spec_from_file_location(
    "vh", "/sessions/bold-nifty-hamilton/mnt/AttentionManuscript/Critique/"
          "replications/A2xA8--heterogeneous-r/verify_heterogeneous_r.py")
vh = importlib.util.module_from_spec(spec); spec.loader.exec_module(vh)

N = vh.N
ER_hetero = vh.ER_hetero
uncued_r_spread = vh.uncued_r_spread
value_vec = vh.value_vec
valid_vec = vh.valid_vec


def simplex_opt_fine(alpha, V, v, r_vec, variant="A", coarse=0.01, fine=0.0025):
    """Best uncued split at fixed cued α: coarse full-simplex scan then a
    local fine refinement around the best, criteria optimised throughout.
    Returns (R_equal, R_best, ΔR, best_uncued_alloc)."""
    vld = valid_vec(V); val = value_vec(v)
    B = 1.0 - alpha
    a_bar = B / (N - 1)
    R_equal = ER_hetero([alpha, a_bar, a_bar, a_bar], vld, val, r_vec, variant)

    def scan(lo1, hi1, lo2, hi2, step):
        best = R_equal; balloc = None
        b1 = lo1
        while b1 <= hi1 + 1e-12:
            b2 = lo2
            while b2 <= hi2 + 1e-12:
                b3 = B - b1 - b2
                if b3 >= -1e-12:
                    R = ER_hetero([alpha, b1, b2, max(b3, 0.0)], vld, val, r_vec, variant)
                    if R > best:
                        best = R; balloc = (b1, b2, max(b3, 0.0))
                b2 += step
            b1 += step
        return best, balloc

    best, balloc = scan(0.0, B, 0.0, B, coarse)
    if balloc is not None:                       # local refine around the winner
        b1c, b2c, _ = balloc
        best2, balloc2 = scan(max(0, b1c - coarse), b1c + coarse,
                              max(0, b2c - coarse), b2c + coarse, fine)
        if best2 > best:
            best, balloc = best2, balloc2
    return R_equal, best, best - R_equal, balloc


def main():
    out = {}
    sep = "=" * 64
    print(sep); print("INTERIOR-α deviation: V=0.5 variant A sqrt; "
                      "value-blind cost-dominant cells (P2/P3 regime)")

    # P3 policy is α=1/N exactly (feeds CF). P2 uses α=α*(v=1).
    cells = [
        ("P3  α=1/N, r_cued=0.3", 1.0/N, 0.3, 1.0),
        ("P3  α=1/N, r_cued=0.2", 1.0/N, 0.2, 1.0),
        ("P2  α*(v=1)=0.26, r_cued=0.3", 0.26, 0.3, 1.0),
        ("P2  α*(v=1)=0.32, r_cued=0.4", 0.32, 0.4, 1.0),
    ]
    for label, alpha, r_cued, v in cells:
        print(f"\n  {label}  (B={1-alpha:.3f})")
        rows = []
        for spread in (0.0, 0.1, 0.2, 0.3):
            r_vec = uncued_r_spread(r_cued, spread)
            Re, Rb, dR, alc = simplex_opt_fine(alpha, 0.5, v, r_vec, "A")
            var_r = float(np.var(r_vec[1:]))
            tag = "" if alc is None else f" best={np.round(alc,4).tolist()}"
            print(f"     spread={spread:.1f}  var(r)={var_r:.5f}  ΔR={dR:.3e}{tag}")
            rows.append(dict(spread=spread, var_r=var_r, dR=dR))
        # quadratic-scaling check: ΔR / var(r) should be ~constant (2nd order)
        ratios = [r["dR"] / r["var_r"] for r in rows if r["var_r"] > 0]
        if ratios:
            print(f"     ΔR/var(r) ratios: {[f'{x:.3e}' for x in ratios]}  "
                  f"(≈const ⇒ ΔR=O(var r))")
        out[label] = rows

    # The decisive bound: max ΔR over all interior cells & spreads.
    alld = [row["dR"] for rows in out.values() for row in rows]
    print(sep)
    print(f"  MAX ΔR over all interior cells & spreads = {max(alld):.3e}")
    print(f"  CR-045 homogeneous-case slack = 1.4e-4;  C2 VDA scale ~0.077, "
          f"CF scale ~0.3–0.9")
    out["max_dR"] = max(alld)

    with open("/sessions/bold-nifty-hamilton/mnt/AttentionManuscript/Critique/"
              "replications/A2xA8--heterogeneous-r/output/deviation_interior.json",
              "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print("  deviation_interior.json written.")


if __name__ == "__main__":
    main()
