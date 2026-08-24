# A3 conservation-family band on the headline numbers — RB-019

| field | value |
| --- | --- |
| task_id | RB-019 |
| run_id | rb-016-2026-05-25 |
| prompt_version | 0.2 |
| claim_ids | A3 (CONTESTED, primary), C1 (CONTESTED), C2 (CONFIRMED-UNDER-ATTACK) |
| output kind | simulation |
| backing for | manuscript §extensions-A3 (RB-034) + the cross-claim band annotations |
| inputs | `Rebuild/model/core.py` `beta_gamma(r, p)` + `policies(r, cell)` (rb-015 wiring); reviewer reference data at `Critique/replications/A3--multiplicative-conservation/output/results.json` (Block A recovery) and `Critique/replications/C1--criterion-fraction-floor/output/results.json` (Block B cross-check). |
| sha256 (pre-hash) | `055bf4ec862c711f2c6a3fa0831e1373b806a84c5f5c1a6b13fd1d9d7a039a33` |
| results.json bytes | 4,941,767 |
| wall-clock | ~36–39 s |
| determinism | re-run produces byte-identical `results.json`; verified across two runs |

## What it computes

Two simulation blocks, both at ρ = 0 (the conservation question is
orthogonal to the A1 decorrelation channel — the joint (p × ρ) sweep
is a future increment, not this one).

### Block A — C2 conservation-family band at the headline cell

At (N = 4, d′\_max = 2, f₀ = 0.5, h = √, V = 0.5, variant A) — rb-006's
headline cell — sweep VDA(r) on rb-006's 84-point log-r grid for the
v-family {2, 3, 5, 8, 10} at p ∈ {0, 0.5, 1.0}. Record per-(v, p) peak
r\* and peak VDA\*, plus the closed-form escape threshold r†(v) at
each p.

The headline finding is a *theorem*:

> **r†(v) is conservation-form-invariant.** At α = 1/N the perturbation
> bracket d\_max · f(1/N) − d\_base = 0 collapses d_c = d_u = d_base
> regardless of (r, p), so the P3-optimal criteria (c_c\*, c_u\*) and
> the per-channel gradients K_c(v), K_u(v) — both evaluated at d_c =
> d_u = d_base — are p-independent. Therefore r†(v) = K_u(v) / [(N − 1)
> · K_c(v)] is the same closed-form number for every conservation
> order p.

The simulation hard-checks this by computing K_c, K_u, r† at
p ∈ {0, 0.5, 1.0} via the same formula rb-006 used; they agree to
**floating-point identity** (max diff exactly 0.0 across K_c, K_u, and
r_dagger; see TEST 3 below).

What *does* shift with p: peak r\* and peak VDA\*. At v = 5, peak VDA\*
goes 0.0830 (p = 1, additive) → 0.0885 (p = 0.5) → 0.0951 (p = 0,
multiplicative); peak r\* shifts left from 0.3758 (p = 1) to 0.3548
(p = 0). The multiplicative regime *amplifies* peak VDA and triggers
escape from α = 1/N at smaller r — the same direction the reviewer's
21-row A3 replication block_c2_c1 reported. r†(v = 5) = 0.0504 sits
well below the empirical peak r\* (gap ≈ +0.30), so the §2.3
prediction "peak r > r†(v)" survives every conservation order tested.

### Block B — C1 conservation-family band on the 4,410-cell sweep

At ρ = 0, the same 4,410-cell primary sweep rb-003 (RB-005) used —
22 r × 21 V × 5 v × 2 variants — at p ∈ {0, 1.0}. The headline result
extends the C1 distributional restatement (CLAIM_LEDGER row C1) with a
*conservation-family band*:

| metric | variant A, p = 1 | variant A, p = 0 | variant B, p = 1 | variant B, p = 0 |
| --- | ---: | ---: | ---: | ---: |
| n_valid (out of 2,205) | 2,205 | 2,205 | 2,205 | 2,205 |
| median CF | 0.7552 | 0.7540 | 0.7682 | 0.7640 |
| min CF | 0.5587 | 0.4638 | 0.3040 | 0.2309 |
| max CF | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| frac CF < 0.5 | 0.0000 | 0.0327 | 0.0803 | 0.1342 |
| frac CF < 0.6 | 0.0703 | 0.2168 | 0.1973 | 0.2712 |

Combined (both variants): 177 cells below CF = 0.5 at p = 1 versus
368 cells at p = 0; **191 cells flip from CF ≥ 0.5 to CF < 0.5**, and
**0 cells flip back** — exactly matching the reviewer's verdict
prediction (`Critique/verdicts/A3--multiplicative-conservation.md`
Block C1: "191 cells flip... 0 recovered"). The variant-B minimum CF
deepens from 0.3040 to 0.2309 — also matching the verdict text
("min CF× = 0.231").

Per-cell ΔCF = CF(p = 0) − CF(p = 1) is **≤ 0 in every cell**: the
multiplicative conservation rule weakens the criterion contribution
everywhere or leaves it unchanged. The damage is concentrated in the
benefit-dominant high-r corner (the same corner C1's additive sweep
already flagged).

## Why these numbers matter for the rebuilt manuscript

1. **A3 (claim CONTESTED) is now rebuilt-side empirically banded.** The
   manuscript §extensions-A3 (RB-034) can now report headline numbers
   as a band across the conservation family, replacing the inherited
   §5.5 single-sentence treatment of multiplicative conservation. The
   rebuilt CLAIM_LEDGER row for A3 already licensed the band; rb-016
   turns the license into an empirical artifact.

2. **C2 (claim CONFIRMED-UNDER-ATTACK) gains a p-invariance theorem.**
   r†(v) is conservation-form-invariant by construction — a free
   strengthening of the C2 result. The manuscript §results-c2 can cite
   this theorem (one sentence + a reference to the present sim) without
   any additional derivation, since the proof is a one-line consequence
   of d_c = d_u = d_base at α = 1/N.

3. **C1 (claim CONTESTED) gains a conservation-family contour on the
   CF distribution.** The §results-c1 distributional restatement
   becomes *two* distributions (one per conservation order), not one;
   the cell-wise ΔCF ≤ 0 monotonicity is itself a new finding the
   inherited paper does not state.

## Recovery tests (all four pass)

| # | scope | tolerance | observed | pass |
| --- | --- | --- | --- | --- |
| 1 | Block A p = 1, v = 5: VDA + CF at rb-006 pins r ∈ {0.398, 1.0, 3.162} | ≤ 5e-5 each | max diff ≤ 5e-5 across 3 pins | ✓ |
| 2 | Block A p = 0, v = 5: 21-row r-sweep vs reviewer A3 multiplicative replication | ≤ 1e-5 on VDA and CF (cross-Φ-backend ULP) | max \|ΔVDA\| = 3.6e-7, max \|ΔCF\| = 6.1e-7 | ✓ |
| 3 | Block A p ∈ {0, 0.5, 1.0}: K_c, K_u, r† at α = 1/N must agree to FP identity | ≤ 1e-14 absolute | max diffs **exactly 0.0** on K_c, K_u, r_dagger | ✓ |
| 4 | Block B p = 1: variant-A and variant-B median CF must match rb-003 logged values (0.7552, 0.7682) | ≤ 5e-5 each | variant A \|Δ\| = 1.3e-5, variant B \|Δ\| = 4.1e-5 | ✓ |

(TEST 2's ~6e-7 residual is the same cross-Φ-backend ULP-level
reordering rb-015's policies() check saw — paper's A&S 7.1.26 vs the
rebuilt module's `scipy.special.ndtr` — and is two orders of magnitude
under tolerance.)

## Files

| file | purpose |
| --- | --- |
| `run.py` | the simulation; heavily docstring'd at the head |
| `output/results.json` | full per-cell rows for Block A and Block B, per-(p, v) peaks, K_c/K_u/r†, summaries, ΔCF distribution, recovery test report, sha256 |
| `output/figures/vda_curves_pfamily_v5.png` | VDA(r) at v = 5, three curves (one per p), peaks marked, vertical dashed = closed-form r†(v = 5) (p-invariant) |
| `output/figures/vda_peak_band.png` | peak r\* and peak VDA\* vs v for p ∈ {0, 0.5, 1.0}, with r†(v) trace |
| `output/figures/cf_histogram_pfamily.png` | CF histogram, 4-panel (variant × p), 4,410-cell sweep |
| `output/figures/delta_cf_distribution.png` | per-cell ΔCF = CF(p = 0) − CF(p = 1) histogram, 2-panel (variant) with flip counts annotated |

## How to re-run

```bash
cd /Users/jonathanmorgan/AttentionManuscript
python3 Rebuild/sims/A3--conservation-band/run.py
```

Re-running must produce byte-identical `results.json` (sha256
`055bf4ec…`); a non-zero exit code is returned if any recovery test
fails.
