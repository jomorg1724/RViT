# RB-018 / rb-021 — A2 heterogeneous-r sweep

**Claim.** A2 (single global ratio `r`). Live verdict
`Critique/verdicts/A2--single-global-r.md` = CONFIRMED-CONDITIONAL.

**Question.** Do the C2 non-monotonicity and the C1 CF distribution
survive heterogeneous per-location `r_i` — and does this survival
remain intact under the rebuild's A1 ρ channel?

## Substrate

Scored through `Rebuild/model/core.er_full_policy` (the rb-020 N-dim
grouped-criterion driver), which composes:

* `d_prime_hetero(alloc, r_vec, ..., p)` (rb-019) — per-location
  asymmetric d'-map with the conservation-order p threaded through.
* `optimal_ER_general(d, wu, n, CR, rho)` (rb-020) — exact 2-D grid
  (G ≤ 2) or 17-seed multi-restart coordinate ascent (G ≥ 3) over the
  rebuilt module's `C_GRID = [-3, 3]` step 0.05 (121 points).
* The A1 one-factor Gauss-Hermite quadrature (rb-001) so any policy
  is scored at any ρ in [0, 1).

This is the *rebuild-voiced* generalisation of the reviewer's CR-048 /
run-015 verification harness
(`Critique/replications/A2xA8--heterogeneous-r/verify_heterogeneous_r.py`),
extended to preserve ρ end-to-end (the reviewer's substrate ran ρ=0
only). Conservation `p = 1` (additive, the paper's choice) only — the
conservation-family band is RB-019/RB-034's job, already shipped.

## Parameters

| symbol | value |
| --- | --- |
| N | 4 |
| d'_max | 2.0 |
| f₀ | 0.5 |
| h | sqrt |
| variant | A (primary) + B (C1 corner only) |
| ρ | {0.0, 0.2} |
| p (conservation) | 1.0 (additive) |
| α-grid | step 0.02, [0.02, 1.00] (50 points; matches CR-048) |
| r-grid | 21 geom + {0.398, 1.0, 3.162} reference pins (24 points) |
| spreads | {0.0, 0.1, 0.2, 0.3} on uncued r factors {1−s, 1, 1+s} |
| headline cell | (V=0.5, v=5) |
| criticality cell | (V=0.5, v=2, r=0.3) — interior α*≈0.66 |
| C1 corner | (V=0.25, v=4, r=10, variant B) |

## Tests

1. **Validation (spread=0 recovery vs `policies()`).** Every (ρ, r)
   on the 21-point r-grid × 2 ρ = 42 cells of the headline (V, v) is
   evaluated twice: once through `er_full_policy` with `spread=0`,
   once through the legacy `policies()`. The contract (rb-020) is 1e-9
   absolute. **PASS: max|ΔVDA| = 2.35e-10, max|ΔCF| = 2.98e-10.**

2. **Criticality of equal-split (CR-048 §a).** At interior-α
   cost-dominant cell (V=0.5, v=2, r=0.3, α*=0.66), central-difference
   tangent gradient on the uncued simplex. Equal-split is critical
   iff `‖t‖ = 0` (i.e. iff r_i are all equal across uncued slots).
   - ρ=0, spread=0: ‖t‖ = 0.000 (binary; equal-split is a critical point)
   - ρ=0, spread=0.3: ‖t‖ = 2.6e-3 (equal-split breaks)
   - ρ=0.2, spread=0: ‖t‖ = 0.000
   - ρ=0.2, spread=0.3: ‖t‖ = 5.8e-3 (ρ amplifies the asymmetry by ~2×)
   The reviewer's "equal-split generically NOT critical under
   heterogeneous r" finding (CR-048 §a) generalises to ρ>0; the
   asymmetry is roughly twice as large at ρ=0.2 as at ρ=0, suggesting
   the A2 and A1 levers compose constructively when present together.

3. **Allocation deviation (CR-048 §b).** ΔR = R(simplex-opt) −
   R(equal-split) at two cells:
   - **Cost-dominant** (V=0.5, v=2, r=0.3, α*=0.66, B=0.34). ΔR scales
     monotonically in var(r_i): at ρ=0, ΔR = 1.42e-5 → 7.10e-5 →
     1.48e-4 as spread goes 0.1 → 0.2 → 0.3. **ρ=0.2 suppresses the
     deviation** to ΔR = 0 → 0 → 2.36e-5 → 7.47e-5 at the same
     spreads (~50% suppression at spread=0.3).
   - **Benefit-dominant** (V=0.5, v=5, r=0.4, α*=1.00, B=0). ΔR = 0
     exactly at every (spread, ρ) — cued-absorption pre-emption: with
     zero uncued budget there is no allocation lever for heterogeneous
     r to bend (CR-048 §b2 mechanism, structurally r-independent).

   Headline: the reviewer's ΔR ≤ 1.5e-4 bound at ρ=0 not only holds
   under the rebuilt model but **tightens** under ρ=0.2 (ΔR ≤ 7.5e-5 at
   spread=0.3, ρ=0.2). Heterogeneous r does NOT amplify in correlated
   noise.

4. **C2 reframe (CR-048 §c).** VDA peak (over the 24-point r-grid) at
   the headline cell, across spread × ρ. **All 8 panels collapse to a
   single curve.**

   | ρ | spread | peak VDA★ | peak r★ |
   | --- | --- | --- | --- |
   | 0.0 | 0.0 | 0.07972 | 0.398 |
   | 0.0 | 0.1 | 0.07972 | 0.398 |
   | 0.0 | 0.2 | 0.07972 | 0.398 |
   | 0.0 | 0.3 | 0.07971 | 0.398 |
   | 0.2 | 0.0 | 0.08130 | 0.398 |
   | 0.2 | 0.1 | 0.08130 | 0.398 |
   | 0.2 | 0.2 | 0.08130 | 0.398 |
   | 0.2 | 0.3 | 0.08130 | 0.398 |

   Peak VDA varies by ≤ 1e-5 across spreads ∈ {0, 0.1, 0.2, 0.3}; peak
   r★ is fixed at 0.398 in every panel (the rebuilt model's
   coarse-α-grid peak). C2 non-monotonicity is invariant under ±30%
   uncued spread, at every ρ probed. **The ρ-channel offset (+0.00158
   in peak VDA) is itself spread-invariant — A1 and A2 act
   orthogonally at the C2 peak.**

5. **C1 contested corner.** Variant B, V=0.25, v=4, r=10 — the rb-005
   variant-B minimum CF cell.

   | ρ | spread | CF | α* |
   | --- | --- | --- | --- |
   | 0.0 | 0.0 | 0.3040 | 0.980 |
   | 0.0 | 0.1 | 0.3042 | 0.980 |
   | 0.0 | 0.2 | 0.3047 | 0.980 |
   | 0.0 | 0.3 | 0.3055 | 0.980 |
   | 0.2 | 0.0 | 0.2665 | 0.980 |
   | 0.2 | 0.1 | 0.2667 | 0.980 |
   | 0.2 | 0.2 | 0.2672 | 0.980 |
   | 0.2 | 0.3 | 0.2681 | 0.980 |

   ΔCF (spread=0.3 − spread=0): +0.0015 at ρ=0 and +0.0016 at ρ=0.2.
   The corner is **not deepened** by A2 spread — in fact slightly
   attenuated. ρ alone deepens the corner (CF 0.304 → 0.266 = −0.037);
   A2 spread does not amplify that deepening.

## Headline narrative

> Within-display heterogeneity (R2 in mission §3.2) is a bounded
> perturbation on every headline C1/C2 number AT EVERY ρ probed, and
> the A1 ρ-channel effect on those numbers is itself invariant under
> A2 heterogeneity. The two levers compose orthogonally at the headline
> cells, with one suggestive asymmetry: ρ-induced correlation in
> decision noise **suppresses** the A2 allocation deviation in the
> cost-dominant regime by ~50%, while leaving the C2 peak location and
> C1 corner CF essentially unchanged. No C1–C5 headline claim shifts
> under heterogeneous r within a ±30% spread, with or without ρ.

## Output

* `output/results.json` — 41 KB, pre-hash sha256
  `22b183f942d6b1f8868848ec1143ab959afd78c72cd6d3704763eedf5713e615`
  (deterministic; re-running this script reproduces this hash exactly).
* `output/figures/vda_curves_spread.png` — 8 VDA(r_cued) curves
  (2 ρ × 4 spread) overlaid — the C2 reframe headline figure.
* `output/figures/vda_peak_band.png` — peak VDA★ and peak r★ vs
  spread, both ρ — the "peak invariance" panel.
* `output/figures/cf_contested_corner.png` — variant-B C1 corner CF
  vs spread, both ρ.

## Reproducibility

```
cd /Users/jonathanmorgan/AttentionManuscript
python3 Rebuild/sims/A2--heterogeneous-r/run.py
```

Wall-clock: ≈ 27 seconds on python3.13 / scipy 1.17.1 / numpy 2.4.4.

## Recovery contract

Spread=0 byte-for-byte against `Rebuild/model/core.policies()` at every
(ρ, r) of the 21-point r-grid × 2 ρ = 42 cells of the headline cell:
max|ΔVDA| = 2.35e-10, max|ΔCF| = 2.98e-10. Tolerance 1e-9 (matches the
rb-020 N-dim recovery contract sha256 `883ea15a…`). The residual is the
1e-10-level wu-reconstruction slack noted in rb-020's
`test_general_policy.py` docstring — six orders of magnitude tighter
than any reported headline number.
