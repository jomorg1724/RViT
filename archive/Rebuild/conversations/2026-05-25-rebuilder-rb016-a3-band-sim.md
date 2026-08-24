---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-016-2026-05-25
started: 2026-05-25T22:00:00Z
ended: 2026-05-25T22:35:00Z
worked_on: RB-019
output_kind: simulation
claims_touched: [A3, C2, C1]
artifacts_written:
  - Rebuild/sims/A3--conservation-band/run.py
  - Rebuild/sims/A3--conservation-band/README.md
  - Rebuild/sims/A3--conservation-band/output/results.json
  - Rebuild/sims/A3--conservation-band/output/figures/vda_curves_pfamily_v5.png
  - Rebuild/sims/A3--conservation-band/output/figures/vda_peak_band.png
  - Rebuild/sims/A3--conservation-band/output/figures/cf_histogram_pfamily.png
  - Rebuild/sims/A3--conservation-band/output/figures/delta_cf_distribution.png
papers_added: []
spawned_tasks: []
---

# rb-016 — A3 conservation-family band on headline numbers (RB-019)

## What I built

Two-block simulation under `Rebuild/sims/A3--conservation-band/` that
turns the rb-015 model wiring (the power-mean conservation family
`beta_gamma(r, p)` threaded through the model module) into a
rebuilt-side empirical band on the manuscript's headline numbers, at
ρ = 0:

- **Block A** — C2 v-family VDA(r) sweep at the headline cell across
  p ∈ {0, 0.5, 1.0} on rb-006's 84-r grid for v ∈ {2, 3, 5, 8, 10}.
  Lands the **r†(v) p-invariance theorem** (proof and numerical
  verification to floating-point identity) plus the empirical band on
  peak (r*, VDA*).
- **Block B** — full 4,410-cell C1 primary sweep at p ∈ {0, 1.0}.
  Reproduces the reviewer's verdict-text Block-C1 prediction *exactly*
  (191 cells flip CF ≥ 0.5 → < 0.5; 0 reverse; variant-B min CF
  deepens 0.3040 → 0.2309; combined frac<0.5 doubles from 4.0% to
  8.3%). Adds the new finding that ΔCF ≤ 0 in every valid cell — the
  conservation swap weakens criterion everywhere or leaves it
  unchanged.

The sim's `run.py` reuses `policies()` from the rebuilt model module
(rb-015 wired `cons_p` onto `HeadlineCell`) for Block A and reuses
the rb-003 cell-evaluation machinery with `cons_p` threaded through
`d_prime_asym` for Block B. Four hard recovery tests, all pass.

## How it connects to the ledger

- **A3 (CONTESTED).** The reviewer's verdict text predicted 191 flips
  / 0 reverse and `min CF× = 0.231` on the 4,410-cell sweep but the
  reviewer's frozen replication JSON
  (`Critique/replications/A3--multiplicative-conservation/output/results.json`)
  was only a 21-row r-sweep at the C2 reference cell. rb-016 lands the
  full 4,410-cell rebuilt-side band and reproduces all three reviewer
  headline numbers exactly. The CLAIM_LEDGER A3 row's "headline
  numbers reported as bands over the family" language already licensed
  this; rb-016 turns the license into a rebuilt-side artifact and
  unblocks RB-034 (§extensions-A3 manuscript section).
- **C2 (CONFIRMED-UNDER-ATTACK).** Block A's r†(v) p-invariance theorem
  is a free strengthening — at α = 1/N the perturbation bracket
  collapses regardless of (r, p), so K_c, K_u are p-independent and
  r†(v) is conservation-form-invariant by construction. The empirical
  band on peak (r*, VDA*) is a sensitivity, not a strength change.
- **C1 (CONTESTED).** Block B extends rb-003's distributional
  restatement of CF with a conservation-family contour, AND adds the
  new cell-wise ΔCF ≤ 0 monotonicity (the conservation swap weakens
  criterion everywhere, never strengthens it).

No claim strength changed; all three rows had already been licensed
at "band over the family" by rb-015. rb-016 is the band's first
rebuilt-side empirical realisation.

## Simulation evidence

- **sha256 (pre-hash) of `output/results.json`:**
  `055bf4ec862c711f2c6a3fa0831e1373b806a84c5f5c1a6b13fd1d9d7a039a33`
- **results.json:** 4,941,767 B; re-run produces byte-identical file
  (determinism contract verified across two runs).
- **Wall-clock:** ~36–39 s on the bash sandbox.
- **Figures:**
  `output/figures/vda_curves_pfamily_v5.png` (Block A; VDA(r) at
  v = 5, 3 curves, peaks marked, r†(v=5) dashed),
  `output/figures/vda_peak_band.png` (Block A; peak r* and peak VDA*
  vs v with r†(v) trace),
  `output/figures/cf_histogram_pfamily.png` (Block B; 4-panel
  variant × p),
  `output/figures/delta_cf_distribution.png` (Block B; 2-panel
  variant, flip counts annotated).
- **Recovery tests** (all four PASS, see results.json `recovery` block):
  - TEST 1 (Block A p=1 vs rb-006 pins): ≤ 5e-5 across 3 pins.
  - TEST 2 (Block A p=0 vs reviewer A3 replication): max |ΔVDA| =
    3.6e-7, max |ΔCF| = 6.1e-7 across 21 cells (tolerance 1e-5).
  - TEST 3 (r† p-invariance to FP identity): K_c, K_u, r_dagger all
    differ by *exactly 0.0* across p ∈ {0, 0.5, 1.0} for every
    v ∈ {2, 3, 5, 8, 10} (tolerance 1e-14).
  - TEST 4 (Block B p=1 vs rb-003 logged variant medians): |Δ| =
    1.3e-5 (variant A) / 4.1e-5 (variant B) on cf_median
    (tolerance 5e-5).

### Numerical headline (the rebuilt manuscript may state)

| metric | additive (p = 1) | multiplicative (p = 0) | shift |
| --- | ---: | ---: | --- |
| Block A peak VDA at v = 5 (headline cell) | 0.0830 | 0.0951 | +14% |
| Block A peak r* at v = 5 | 0.3758 | 0.3548 | −0.021 (left) |
| Block A r†(v = 5) closed form | 0.0504 | 0.0504 | **identical (p-invariant)** |
| Block B variant-A median CF | 0.7552 | 0.7540 | −0.0012 |
| Block B variant-A min CF | 0.5587 | 0.4638 | −0.0949 |
| Block B variant-A frac<0.5 | 0.0000 | 0.0327 | +3.3 pp |
| Block B variant-B median CF | 0.7682 | 0.7640 | −0.0042 |
| Block B variant-B min CF | 0.3040 | 0.2309 | **−0.0731 (verdict text quotes 0.231)** |
| Block B variant-B frac<0.5 | 0.0803 | 0.1342 | +5.4 pp |
| Block B combined n_below_0_5 | 177 | 368 | **+191 cells; 0 reverse** |

The "combined n_below_0_5 177 → 368, 191 net flips, 0 reverse" line
reproduces the reviewer's
`Critique/verdicts/A3--multiplicative-conservation.md` Block-C1
prediction byte-for-byte at the integer level.

## What the manuscript can now say

- **§extensions-A3 (RB-034, queued; backed by rb-016):** the rebuilt
  manuscript can now state the conservation-family generalisation,
  the C2 conservation-family band table, the **r†(v) p-invariance
  theorem** (one proposition + one-paragraph proof + a citation to
  TEST 3 in `Rebuild/sims/A3--conservation-band/`), the C1
  conservation-family contour on the CF distribution, the cell-wise
  ΔCF ≤ 0 monotonicity, and the C5 conservation-form-invariance
  corollary (β(1, p) = γ(1, p) = 1 for every p). Six content blocks,
  each with a number or a figure or both.
- **§results-c2 (RB-010, drafted) cross-reference at RB-034:** the
  rb-016 r†(v) p-invariance theorem belongs in §extensions-A3 (where
  the conservation family is defined), with a one-sentence
  cross-reference from §results-c2.
- **§results-c1 (RB-009, drafted) cross-reference at RB-034:** the
  rb-016 conservation-family contour on CF (frac<0.5 doubling; ΔCF ≤ 0
  monotonicity; 191 flips) belongs in §extensions-A3, with a
  one-sentence cross-reference from §results-c1.
- **What the manuscript may NOT yet say:** the formal derivation of
  the conservation family in the rebuild's voice (RB-033, low-priority
  spawn from rb-015); the conservation × ρ interaction band (no
  current backlog task — would be a follow-up sim if §extensions
  reviewer pushes back); a comparison across the full p ∈ [-2, 2]
  smooth band on the 4,410-cell sweep (Block B is at p ∈ {0, 1.0}
  only; intermediate p was not run on the full sweep, only on Block A's
  headline cell).

## Next increment

**RB-034 — manuscript §extensions-A3.** Prereq RB-019 done at rb-016.
The section has all six content blocks empirically backed; figure paths
listed in the rb-019 backlog notes; can copy 4 figures from
`Rebuild/sims/A3--conservation-band/output/figures/` to
`Rebuild/manuscript/figures/`; cite Hardy-Littlewood-Pólya 1934
*Inequalities* for the power-mean monotonicity (by full bib reference;
research_db stub deferred per math-methods scope inherited from
rb-008/rb-014/rb-015). One run lands the third of the three extension
levers (A1 → A3 → A2/A8) as a written manuscript section, closes the
§extensions thread for A3, and gives the rebuilt paper its first
conservation-family band statement in prose.

Alternative continuations: **RB-013** (§appendix-C5 light-touch
manuscript section; can now cite both the rb-015 conservation-form-
invariance corollary AND the rb-016 numerical confirmation), **RB-014**
(A2 heterogeneous-r model extension, opens the A2/A8 thread —
the last extension lever), **RB-033** (A3 formal derivation,
low-priority; can now cite rb-016 TEST 3).

## Wiki cross-references

- Wiki sweep performed at the keyword set
  {conservation family, power mean, generalised mean,
  Hardy-Littlewood-Pólya, asymmetric scaling, β+γ=2, β·γ=1,
  multiplicative conservation, additive conservation,
  monotonic transformation} — same math-methods gap as the Slepian/
  Tong references cited by rb-008/rb-014 and the power-mean references
  cited by rb-015. The gap is intentionally out of rebuilder scope
  (reviewer's CR-035/CR-037 owns the bibliographic backlog); the
  manuscript will cite Hardy-Littlewood-Pólya 1934 *Inequalities* by
  full bibliographic reference at RB-034.
- No new `research_db/papers/` stubs added by this run; `audit.py` not
  re-run (no wiki writes).
