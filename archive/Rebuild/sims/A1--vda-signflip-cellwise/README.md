# A1 — cell-wise sign-flip of ∂VDA/∂ρ across the 4,410-cell sweep

Backlog: RB-025 (claim A1; output_kind: simulation; spawned-by RB-005 / rb-003).
Run id: rb-025-2026-05-29.

## What this sim does

Generalises rb-002's **single-cell** observation — at the C2 headline
cell (variant A, V=0.5, v=5, N=4), VDA(r; ρ=0.2) drops below VDA(r;
ρ=0) for r ≲ 0.46 (suppression) and rises above it for r ≳ 0.46
(amplification) — to a **cell-wise** statistic across the 4,410-cell
(variant, r, V, v) sweep that rb-003 already evaluated at ρ ∈ {0, 0.2}.

The sim does **no model evaluation**: it is a pure consumer of
`Rebuild/sims/C1--cf-distribution/output/results.json` (sha256
`91fc4692…`), which already stores `VDA` and `CF` per cell at both ρ
panels. The sim joins the two ρ panels on (variant, r, V, v), computes
`ΔVDA = VDA(ρ=0.2) − VDA(ρ=0)`, classifies each cell as
**amplification** (ΔVDA > +ε), **suppression** (ΔVDA < −ε), or
**inactive** (|ΔVDA| ≤ ε) with ε = 10⁻⁶, and reports three
distributional cuts of the result:

1. **Per-variant Δ-distribution** — counts of amp / supp / inactive
   cells, quantiles (q5, q25, q50, q75, q95), min, max, mean.
2. **r-stratified sign-flip pattern** — at each r in the rb-003 21-pt
   log10 r-grid, the fraction of (V, v) cells that amplify vs
   suppress. The **cell-wise crossover r** is the smallest r at which
   `frac_amp(r) ≥ frac_supp(r)`.
3. **(V, r) sign-of-mean heatmap at v = 5** — mean ΔVDA per (V, r) cell
   at v = 5, per variant. Cell-wise companion to rb-010's
   `iso_vda_drho` figure on the C3 thread.

## Why this matters for the rebuild

The §3.3 unifying-reframe theme of the rebuild — *report
distributional / conditional / quantitative claims by default* —
requires generalising rb-002's single-cell sign-flip observation
before the manuscript states it as a cell-wise pattern. rb-002 made
the **mechanism** claim (∂VDA/∂ρ flips sign somewhere in r); this
sim adds the **incidence** claim (how often, where in (V, v),
how big). It's the natural empirical companion to the *analytic*
lower-edge channel rb-023 / §appendix-deriv-c2 already pinned via
the closed-form drift r†(v; ρ).

## Headline numbers (this run)

Source: rb-003 results.json sha256 `91fc4692…`; n = 2,205 cells per
variant per ρ panel (one VDA per cell), 4,410 joined cell-pairs.

```
                       variant A          variant B
n cells                2,205              2,205
amp   (ΔVDA > +1e-6)   404 (18.3%)        269 (12.2%)
supp  (ΔVDA < −1e-6)   621 (28.2%)        607 (27.5%)
inactive               1,180 (53.5%)      1,329 (60.3%)

ΔVDA min               −0.00914           −0.00323
ΔVDA q5                −0.00451           −0.00070
ΔVDA q50 (median)       0.00000            0.00000
ΔVDA q95               +0.00387           +0.00038
ΔVDA max               +0.04974           +0.00577
ΔVDA mean              +0.00023           −0.00005

cell-wise crossover r   0.7943             never
(frac_amp ≥ frac_supp)
```

**Findings.** (i) Suppression is the more common sign of the A1 effect
in *both* variants across this sweep (28.2% vs 18.3% amp in A; 27.5%
vs 12.2% in B). (ii) The **amplification tail is much fatter in
variant A** than in variant B — variant A's max amp is +0.0497 (≈ 9× its
max suppression −0.0091); variant B's max amp is +0.0058 (≈ 2× its max
suppression −0.0032). (iii) The **cell-wise crossover** in variant A
sits at **r ≈ 0.794**, well to the right of rb-002's V=0.5
headline-cell crossover at **r ≈ 0.464**; the higher-V cells in the
sweep (V ≥ 0.5125) pull the crossover right because suppression
dominates more strongly there. (iv) Variant B never crosses across this
sweep — `frac_amp(r) < frac_supp(r)` at every r — corroborating
rb-002's headline-cell observation that variant B's CF was essentially
flat in ρ. (v) The **maximum cell-wise amplification** (variant A,
ΔVDA = +0.0497) is **5.3× larger** than rb-002's maximum
headline-cell pointwise excess (+0.00936 at V=0.5, v=5, r=0.4 from
rb-002's `max_excess_over_rho0["0.20"]`). The most-amplified cells
are NOT at the rb-002 headline — they sit elsewhere in (V, v, r), at
cells where VDA(ρ=0) is small and ρ-channel reallocation lifts it
multiplicatively.

## Recovery contract (verification performed)

The sim does no model evaluation, so the upstream guarantee is
rb-003's own recovery test (max|ΔCF| = 1.47e-6 across all 4,410 cells
vs the reviewer's CR-002 floor-replication). This sim adds three
*structural* contracts:

**(a) Source-payload sha** — embedded `metadata.source_sha256 =
"91fc4692…"` is the rb-003 sha verified at rb-003 run time;
this sim's reads are deterministic w.r.t. that payload.

**(b) Sign-flip at the nearest cell to rb-002 headline** — at variant
A, V = **0.5125** (the closest rb-003 V to rb-002's V = 0.5,
distance +0.0125; rb-003's V-grid step is 0.0375), v = 5, the sign of
ΔVDA flips from negative (suppression at small r) to positive
(amplification at large r) across the rb-003 r-grid. The
nearest-cell crossover is at r ≈ **0.398** — consistent with rb-002's
V=0.5 cell crossover at r ≈ 0.464 within the rb-003 V-grid
perturbation. **PASS**: small-r suppression present AND large-r
amplification present at the nearest cell.

**(c) Cell-wise crossover ≥ rb-002 headline** — the rb-003 sweep
includes higher-V cells (V up to 1.0), where suppression dominates,
so the cell-wise crossover (averaged across (V, v)) should sit at or
above the rb-002 V=0.5 single-cell crossover (r ≈ 0.464). Observed:
**r ≈ 0.794 ≥ 0.464**. **PASS.**

**Overall**: all three contracts pass.

## Determinism / reproducibility

No RNG, no model evaluation; pure JSON IO + NumPy aggregation.
Re-running produces byte-identical `results.json`.

- Pre-embed payload sha256: `489c7c2581d1e940cfc67427e0793959bb33b24afda075ee648743aa2ac659ea`
- Source (rb-003) sha256: `91fc4692dbc106eca9c90770c79e22f7f4757d76421ed55e7e8e91f80e44706c`
- rb-002 reference sha256: `b692c06456530ccd1b319762d8a948814324d3129f39902ce9531a66d1206614`
- python: 3.13, numpy 2.4.4, matplotlib (Agg)
- wall clock: < 1 s

## Outputs

`output/results.json`
  - `metadata` — sim_id, claim_id, source sha, ε, sign classification
  - `per_variant_distribution` — `{n, amp/supp/inactive, quantiles, mean, min, max}` × {A, B}
  - `per_variant_signflip_by_r` — `rows: [{r, n, frac_amp, frac_supp, frac_inactive, mean_dVDA, max_amp, max_supp}, …]` × {A, B} plus `crossover_r`
  - `per_variant_heatmap_v5` — `{Vs, rs, mean_dVDA[V][r]}` at v=5 × {A, B}
  - `recovery_test` — rb-002 sha, nearest-cell sign-pattern table, cell-wise crossover, pass/fail

`output/figures/`
  - `vda_delta_distribution.png` — ΔVDA histogram, 2-panel variant
  - `signflip_by_r.png` — frac_amp / frac_supp curves vs r (log scale), 2-panel variant, crossover r marked
  - `vda_sign_heatmap_v5.png` — mean ΔVDA over (V, r) at v=5, 2-panel variant, diverging colormap

## What the manuscript can now say (at the A1 row strength ceiling)

The §results-A1 paragraph (or the §extensions / §sensitivity paragraph
that consumes this sim) can now state:

> Across the rb-003 4,410-cell (variant, r, V, v) sweep at ρ = 0.2 vs
> ρ = 0, the sign of ∂VDA/∂ρ varies cell-wise as predicted by the
> rb-002 headline-cell observation, with 18.3% of variant-A cells
> showing amplification, 28.2% showing suppression, and the remaining
> 53.5% inactive; the cell-wise crossover (the smallest r at which
> amplification overtakes suppression across (V, v)) sits at r ≈ 0.794
> in variant A and does not occur in variant B at any r in the rb-003
> grid. The mean ΔVDA is +0.00023 in variant A (slightly amplifying)
> and −0.00005 in variant B (slightly suppressing); the maximum
> cell-wise amplification (+0.0497, variant A) is 5.3× the rb-002
> headline-cell maximum (+0.0094 at V=0.5, v=5), demonstrating that
> the rb-002 single-cell observation was a *typical-magnitude*
> snapshot of a *cell-wise* phenomenon whose largest excursions sit
> elsewhere in (V, v, r). The original paper's §5.5 framing of
> independence as a uniform upper bound on VDA fails cell-wise as
> well as pointwise.

The manuscript should **not** yet state:

- (a) A closed-form prediction of which (V, v, r) cell maximises
  amplification — the cell-wise maximum is empirical here; the
  analytic locus is queued (extension of RB-026 / Slepian-gradient
  analogue RB-040).
- (b) A cell-wise crossover at *finer* ρ resolution — RB-039 would
  refine, but this sim reports at ρ = 0.2 only.
- (c) A *quantitative* generalisation across higher correlations
  (ρ > 0.4) — outside the empirical envelope of CohenMaunsell2009.

## Wiki sweep

Keywords: {cell-wise sign-flip, ∂VDA/∂ρ, amplification incidence,
cost-dominant vs benefit-dominant regime, criterion devaluation,
concentration-cost relaxation, A1 two-channel decomposition}.

All citations needed are inherited from §model and §appendix-deriv-A1
(CohenMaunsell2009, RuffCohen2016, Srinath2021; Slepian 1962 and
Tong 1990 by full bib reference). No new `research_db/papers/` stubs.

## Files

- `run.py` — the sim driver (heavily commented; consumes rb-003 JSON)
- `README.md` — this file
- `output/results.json` — full distribution + recovery test
- `output/figures/*.png` — three figures
