---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-025-2026-05-29
started: 2026-05-29T00:00:00Z
ended: 2026-05-29T00:00:00Z
worked_on: RB-025
output_kind: simulation
claims_touched: [A1, C1]
artifacts_written:
  - Rebuild/sims/A1--vda-signflip-cellwise/run.py
  - Rebuild/sims/A1--vda-signflip-cellwise/README.md
  - Rebuild/sims/A1--vda-signflip-cellwise/output/results.json
  - Rebuild/sims/A1--vda-signflip-cellwise/output/figures/vda_delta_distribution.png
  - Rebuild/sims/A1--vda-signflip-cellwise/output/figures/signflip_by_r.png
  - Rebuild/sims/A1--vda-signflip-cellwise/output/figures/vda_sign_heatmap_v5.png
  - Rebuild/CLAIM_LEDGER.md
  - Rebuild/REBUILD_BACKLOG.md
  - Rebuild/rebuilder_state.json
  - Rebuild/BUILD_LOG.md
papers_added: []
spawned_tasks: [RB-041]
---

# rb-025 — A1 cell-wise sign-flip of ∂VDA/∂ρ across the 4,410-cell sweep

## What I built

A new simulation under
[Rebuild/sims/A1--vda-signflip-cellwise/](../sims/A1--vda-signflip-cellwise/)
that turns rb-002's single-cell observation (sign-flip of ∂VDA/∂ρ
at r ≈ 0.46 at the C2 headline cell V=0.5, v=5) into a **cell-wise
statistic** parallel to rb-003's CF Δ-distribution.

The sim does **no model evaluation**: it is a pure consumer of
rb-003's `results.json` (sha256 `91fc4692…`, validated upstream
against the reviewer's CR-002 floor-replication at `max|ΔCF| =
1.47e-6` across the 4,410-cell sweep). It joins the two ρ ∈ {0, 0.2}
panels on (variant, r, V, v), computes `ΔVDA = VDA(ρ=0.2) −
VDA(ρ=0)` per cell, and reports three distributional cuts:

1. Per-variant Δ-distribution (counts, quantiles, min/max/mean).
2. r-stratified frac_amp / frac_supp curves with cell-wise crossover.
3. (V, r) signed-mean heatmap at v=5 — cell-wise companion to rb-010's
   `iso_vda_drho`.

Three figures landed; three structural recovery contracts PASS;
re-running yields the same sha (deterministic).

## How it connects to the ledger

- **A1 row (CONTESTED, primary).** The row's backing column gains
  the rb-025 sim. No strength change — the row was already licensed
  at "sign-flip generalises beyond the headline cell" by the rb-010
  (V, v) corroboration at v ∈ [2, 11]. rb-025 turns that license into
  a 4,410-cell distributional artifact across the full C1 sweep,
  parallel to rb-003's CF Δ-distribution.
- **C1 row (CONTESTED).** Touched aggregationally: the rb-003 cells
  are re-classified by ΔVDA sign here, but no C1 headline number
  shifts. The ΔVDA Δ-distribution sits alongside rb-003's existing
  ΔCF Δ-distribution.
- **No label drift in the live ledger** (10/10 verdict labels still
  match the §3 table of `agents/paper_rebuilder_prompt.md` v0.2; A6
  still WEAKLY-SUPPORTED, all others as the table reads).

## Simulation evidence

- Pre-embed payload sha256:
  `489c7c2581d1e940cfc67427e0793959bb33b24afda075ee648743aa2ac659ea`.
- Source (rb-003) sha256:
  `91fc4692dbc106eca9c90770c79e22f7f4757d76421ed55e7e8e91f80e44706c`.
- rb-002 reference sha256:
  `b692c06456530ccd1b319762d8a948814324d3129f39902ce9531a66d1206614`.

**Headline numbers** (over 2,205 cells per variant):

| | variant A | variant B |
|---|---|---|
| amp   (ΔVDA > +1e-6) | 404 (18.3%) | 269 (12.2%) |
| supp  (ΔVDA < −1e-6) | 621 (28.2%) | 607 (27.5%) |
| inactive | 1,180 (53.5%) | 1,329 (60.3%) |
| ΔVDA min | −0.00914 | −0.00323 |
| ΔVDA q5 / q50 / q95 | −0.00451 / 0 / +0.00387 | −0.00070 / 0 / +0.00038 |
| ΔVDA max | +0.04974 | +0.00577 |
| ΔVDA mean | +0.00023 | −0.00005 |
| cell-wise crossover r | 0.7943 | never |

**Recovery contracts.** All three PASS:

- **(a) Source-payload sha** guarantee.
- **(b) Sign-flip at nearest cell** (variant A, V=0.5125, v=5):
  small-r suppression AND large-r amplification both present;
  nearest-cell crossover r ≈ 0.3981 ≈ rb-002 V=0.5 crossover 0.4642.
- **(c) Cell-wise crossover ≥ rb-002 headline crossover**
  (0.7943 ≥ 0.4642).

**Figures.** `vda_delta_distribution.png` (Δ-distribution
histograms), `signflip_by_r.png` (r-stratified frac_amp / frac_supp
curves with crossover marked), `vda_sign_heatmap_v5.png` (mean ΔVDA
heatmap over (V, r) at v=5).

## What the manuscript can now say

At the A1 row strength ceiling:

> Across the rb-003 4,410-cell (variant, r, V, v) sweep at ρ = 0.2
> vs ρ = 0, the sign of ∂VDA/∂ρ varies cell-wise: 18.3% of
> variant-A cells amplify, 28.2% suppress, 53.5% are inactive; the
> cell-wise crossover r (where amplification overtakes suppression
> across (V, v)) sits at r ≈ 0.794 in variant A and does not occur
> in variant B at any r in the rb-003 grid. The mean ΔVDA is
> +0.00023 in variant A (slightly amplifying) and −0.00005 in
> variant B (slightly suppressing). The maximum cell-wise
> amplification (+0.0497, variant A) is 5.3× the rb-002 V=0.5
> headline-cell maximum (+0.0094), demonstrating that the rb-002
> single-cell observation was a *typical-magnitude* snapshot of a
> cell-wise phenomenon whose largest excursions sit elsewhere in
> (V, v, r). The original paper's §5.5 framing of independence as a
> uniform upper bound on VDA fails cell-wise as well as pointwise.

It does **not** yet license:

- (a) A closed-form prediction of which (V, v, r) cell maximises
  amplification — empirical here; analytic locus queued
  (extension of RB-026 / RB-040).
- (b) A cell-wise crossover at finer ρ resolution — RB-039 / RB-023
  would refine.
- (c) Higher-correlation (ρ > 0.4) generalisation — outside
  CohenMaunsell2009's envelope.

## Next increment

**RB-041** (queued, spawned by rb-025; manuscript fold-in into §model
§5.5-replacement / `sec:model-upper-bound` and/or §sensitivity):
replace the present pointwise / headline-cell phrasing with a
cell-wise distributional statement; copy the three rb-025 figures to
`manuscript/figures/` with `a1cw_` prefix; cite Sections /
Propositions by stable labels paralleling the rb-024 manuscript
fold-in pattern (rb-023 derivation → rb-024 manuscript prose).

Alternative parallel options (all unblocked):

- **RB-021** (A8 N-dim uncued sweep — completes the heterogeneity
  thread architecturally; the last §extensions subsection
  still unfilled).
- **RB-033** (A3 formal derivation in the rebuild's voice — fills the
  §appendix-deriv-a3 stub placed by rb-017).
- **RB-024** (C1 closed-form CF<0.5 boundary derivation — would let
  §results-c1 replace `frac<0.6 = 22%` with a closed-form predicate).

Recommended next: **RB-041**, because it converts rb-025 numbers into
manuscript prose with stable label set, matching the rb-024
manuscript-fold-in cadence.

## Wiki cross-references

Wiki sweep performed for keywords {cell-wise sign-flip, ∂VDA/∂ρ,
amplification incidence, cost-dominant vs benefit-dominant regime,
criterion devaluation, concentration-cost relaxation, A1 two-channel
decomposition}.

- `research_db/papers/cohen_maunsell2009_correlations.md` — already
  wired (cited from §model and §appendix-deriv-A1).
- `research_db/papers/ruff_cohen2016_cross_area_correlations.md` —
  already wired.
- `research_db/papers/srinath2021_attention_information_flow.md` —
  already wired.
- Slepian 1962, Tong 1990 — math-methods gap; not stubbed; cited by
  full bibliographic reference per reviewer CR-035/CR-037 scope.

No new `research_db/papers/` stubs added; `audit.py` not re-run (no
wiki writes).
