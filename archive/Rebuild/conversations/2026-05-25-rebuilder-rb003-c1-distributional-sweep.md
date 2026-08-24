---
type: conversation
agent: constructive-rebuilder
prompt_version: "0.2"
run_id: rb-003-2026-05-25
started: 2026-05-25T11:24:00Z
ended: 2026-05-25T11:31:00Z
worked_on: RB-005
output_kind: simulation
claims_touched: [C1, A1]
artifacts_written:
  - Rebuild/sims/C1--cf-distribution/run.py
  - Rebuild/sims/C1--cf-distribution/README.md
  - Rebuild/sims/C1--cf-distribution/output/results.json
  - Rebuild/sims/C1--cf-distribution/output/figures/cf_histogram.png
  - Rebuild/sims/C1--cf-distribution/output/figures/cf_heatmap.png
  - Rebuild/sims/C1--cf-distribution/output/figures/cf_curves.png
papers_added: []
spawned_tasks: [RB-024, RB-025]
---

# rb-003 — C1 distributional sweep (RB-005)

## What I built

`Rebuild/sims/C1--cf-distribution/` — the second simulation under
`Rebuild/sims/`, and the first to exercise the rebuilt model library
across the paper's *full* primary 4,410-cell sweep rather than at a
single headline cell.

The sim:

- Reproduces the paper's primary 4,410-cell grid
  (`N=4, d'_max=2, f_0=0.5, h=sqrt; r ∈ {21 log-pts in [0.1,10]} ∪ {1};
  V ∈ {21 pts in [1/N, 1]}; v ∈ {1..5}; variant ∈ {A,B}`) on the
  rebuilt model library, at two ρ values: 0 (recovery) and 0.2
  (A1 sensitivity).
- Computes (R(P1), R(P2), R(P3), R(P4), VDA, CF) per cell.
- Emits **three publication-quality figures** (cf_histogram,
  cf_heatmap, cf_curves) and a sha256-stamped `results.json`.
- Compares cell-wise to the reviewer's CR-002 reference
  (`Critique/replications/C1--criterion-fraction-floor/output/results.json`).

Wall-clock: 67.4 s end-to-end (scipy.special.ndtr backend).

## How it connects to the ledger

This sim discharges the simulation portion of the **C1 (CONTESTED)**
verdict. C1 as written in the paper ("CF ∈ [0.60, 0.96] across the
4,410-cell sweep") is decisively refuted:

| statement                                        | rb-003 finding |
|---|---|
| CF ∈ [0.60, 0.96] across all 4,410 cells          | **FALSE** (variant-A min 0.5587 < 0.60; variant-B min 0.3040 < 0.50) |
| CF ≥ 0.50 across all 4,410 cells                  | **FALSE** (variant-B has 8.03% < 0.50; variant-A 0.00% < 0.50) |
| Median CF ≈ 0.76                                  | **TRUE** (variant A 0.7552, variant B 0.7682) |
| "criterion typically dominates" (CF ≥ 0.5 in most cells) | **TRUE** (variant A 100%, variant B 91.97%) |

The defensible rebuilt strength (see CLAIM_LEDGER.md, updated this
run) is therefore the distributional / central-tendency form: "median
CF ≈ 0.76, but the categorical [0.60, 0.96] range is retracted on both
ends; 7% of variant-A cells fall below 0.60, and 8% of variant-B cells
fall below 0.50." This is the form the rebuilt §results-C1 (RB-009)
is now licensed to state.

The sim **also** discharges a cell-wise extension of A1 (still
CONTESTED): rb-002 demonstrated at the single headline cell that
adding ρ amplifies VDA in the benefit-dominant regime and suppresses
the criterion fraction monotonically (variant A) or flatly (variant
B). rb-003 generalises the CF half of that result across all 4,410
cells:

- **Variant A**: 84% of cells have CF(ρ=0.2) < CF(ρ=0) (median Δ = −0.035).
  The rb-002 headline-cell monotone-down ordering generalises, but is
  not universal — 16% of cells move flat or upward.
- **Variant B**: 64% decrease, 24% increase, 13% flat (median Δ = −0.009).
  The rb-002 headline-cell flatness is one manifestation of a broader
  variant-B pattern: A1's CF lever is weaker and sign-mixed in variant B.

This is the honest-reporting (mission §5.5) extension of rb-002's
caveat: the manuscript must say "variant A: 84% of cells; variant B:
64%" rather than treating the variant-A pattern as universal.

## Simulation evidence

### Recovery test (ρ=0 vs reviewer's CR-002 reference)

All 4,410 cells of the rebuilt sweep joined cell-wise against the
reviewer's `results.json`:

| field   | n compared | max \|Δ\| | mean \|Δ\| |
|---|---|---|---|
| CF      | 4,410 | 1.466e-6 | 2.478e-7 |
| R(P1)   | 4,410 | 5.645e-7 | 9.942e-8 |
| R(P2)   | 4,410 | 5.645e-7 | 9.797e-8 |
| R(P3)   | 4,410 | 1.811e-7 | 6.287e-8 |
| R(P4)   | 4,410 | 4.839e-7 | 1.785e-7 |

The recovery is at ~1.5e-6 on CF, **not** byte-for-byte floating-point
identity. The gap is a known ULP-level reordering artifact:
`floor_R` evaluates `Phi(b)` directly while the reviewer's
`reward_at_c_zero` evaluates `1 - Phi(-b)`. Mathematically identical;
under `scipy.special.ndtr` these round differently at the last 1–2
ULPs and the difference compounds to ~1e-7 on R(P1..P4) and ~1e-6 on
CF (a ratio). This is well past the 4-decimal precision of any
reported headline number in the paper (CF=0.73, 0.64, etc.).

Reviewer's reported headline numbers (which the rebuild substrate must
match in spirit):

| reviewer reports | rb-003 produces | match? |
|---|---|---|
| variant-B argmin CF = 0.3040 at (r=10, V=0.25, v=4) | variant-B min CF = 0.3040 | ✓ |
| variant-A argmin CF = 0.5587 at (r=10, V=0.55, v=1) | variant-A min CF = 0.5587 | ✓ |
| max CF = 1.0 | max CF = 1.0000 | ✓ |
| combined median CF = 0.7605 | per-variant medians 0.7552/0.7682; combined ≈ 0.7617 | ✓ within ~1% |
| 13.4% of cells below 0.60 (paper claim broken) | 0.07 × 0.5 + 0.20 × 0.5 = 13.5% combined | ✓ |

### Distributional headline (ρ=0; the rebuild's restatement of C1)

| variant | n_valid | min | q5 | q25 | median | q75 | q95 | max | frac<0.5 | frac<0.6 | frac<0.8 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 2205 | 0.5587 | 0.612 | 0.687 | **0.7552** | 0.844 | 0.973 | 1.000 | 0.000 | 0.070 | 0.570 |
| B | 2205 | 0.3040 | 0.451 | 0.633 | **0.7682** | 0.886 | 0.996 | 1.000 | 0.080 | 0.197 | 0.543 |

(q5/q25/q75/q95 read from `output/results.json` summaries block.)

### A1 sensitivity (ρ=0.2 vs ρ=0)

Headline-number shift:

| variant | metric | ρ=0 | ρ=0.2 | Δ |
|---|---|---|---|---|
| A | min CF       | 0.5587 | **0.4854** | −0.073 |
| A | median CF    | 0.7552 | 0.7197 | −0.035 |
| A | frac<0.5     | 0.000  | 0.012 | +0.012 |
| A | frac<0.6     | 0.070  | **0.222** | **+0.152** |
| B | min CF       | 0.3040 | 0.2406 | −0.063 |
| B | median CF    | 0.7682 | 0.7538 | −0.014 |
| B | frac<0.5     | 0.080  | 0.109 | +0.029 |
| B | frac<0.6     | 0.197  | 0.252 | +0.055 |

Cell-wise sign-classification of ΔCF = CF(ρ=0.2) − CF(ρ=0):

| variant | n | frac dec | frac inc | frac flat | median Δ | \|Δ\|_q95 |
|---|---|---|---|---|---|---|
| A | 2205 | **0.838** | 0.083 | 0.079 | −0.0348 | 0.0640 |
| B | 2205 | 0.637 | 0.235 | 0.127 | −0.0093 | 0.0650 |

### Output reproducibility

`results.json` is deterministic and re-running the script produces
identical output. Output digest (sha256, computed pre-stamp over the
sorted-key serialisation):

`91fc4692dbc106eca9c90770c79e22f7f4757d76421ed55e7e8e91f80e44706c`

### Figure manifest

- `output/figures/cf_histogram.png` — 4-panel (variant × ρ) CF
  histograms with paper-floor reference lines (0.60 dashed, 0.50
  dotted), median annotation per panel, and frac-below annotations.
  The visual restatement of C1 as a distribution. The figure shows
  (a) variant A is tightly held above 0.5 at ρ=0 but tail extends
  below 0.5 at ρ=0.2; (b) variant B has a substantial CF<0.5 tail at
  both ρ; (c) both panels have a CF=1 spike (the high-V × low-r
  saturation corner).
- `output/figures/cf_heatmap.png` — 4-panel (variant × ρ) CF over
  (r, V) at v=5. Shows the low-CF corner is low-V × high-r (where
  attention reallocation is the dominant lever); high-V × low-r is
  the CF=1 saturation; the corner widens at ρ=0.2 in both variants
  (variant A more dramatically).
- `output/figures/cf_curves.png` — 4-panel (variant × ρ) CF vs r at
  V≈0.5, with v-family (v ∈ {1,2,3,4,5}). The v=1 curve sits highest
  (weakest value gradient → strongest criterion dominance); v=5 sits
  lowest. ρ=0.2 pushes all curves downward in variant A more uniformly
  than in variant B.

## What the manuscript can now say

### Licensed (the strongest form the rebuild allows after rb-003)

The rebuilt §results-C1 may state, verbatim:

> *"Across the paper's primary 4,410-cell (r, V, v) sweep, the criterion
> fraction CF spans [0.56, 1.00] in variant A and [0.30, 1.00] in
> variant B, with a median of 0.76 in both cases. The paper's stated
> range CF ∈ [0.60, 0.96] is too narrow on both ends: 7% of variant-A
> cells fall below 0.60, and 8% of variant-B cells fall below 0.50.
> The substantive 'criterion typically dominates' reading survives —
> the median is comfortably above 0.5 and the distribution mass is
> concentrated above 0.6 — but the categorical floor is retracted."*

The rebuilt §results-A1 may extend its rb-002 cell-wise CF lever
statement to:

> *"The amplification of the criterion fraction by independence
> (A1) — observed at a single headline cell in rb-002 — generalises
> across the 4,410-cell sweep. Cell-wise CF(ρ=0.2) ≤ CF(ρ=0) holds in
> 84% of variant-A cells (median ΔCF = −0.035) and 64% of variant-B
> cells (median ΔCF = −0.009). In variant A the ordering is dominant
> enough to license the central claim that independence upper-bounds
> the criterion fraction in expectation; in variant B the cell-wise
> distribution is sign-mixed (24% of cells show CF(ρ=0.2) > CF(ρ=0)),
> and the variant-B CF-lever is reported as a sensitivity rather than
> a uniform claim."*

### Not yet licensed

- The conservation-family band on these numbers (A3): RB-019 needed.
- A closed-form predicate for the CF<0.5 corner (cf_heatmap shows a
  clean diagonal boundary): RB-024 spawned this run.
- The cell-wise VDA sign-flip (the second half of rb-002's A1 finding,
  generalised across the sweep parallel to this run's CF Δ-distribution):
  RB-025 spawned this run.

## Next increment

Two natural options unblock next:

1. **RB-003** (A1 derivation, medium priority): promote the
   equicorrelated 1-D quadrature + Slepian-monotonicity argument into
   `Rebuild/derivations/A1--rho-channel.md` (full LaTeX), authored
   against the inherited model rather than copied. Required for the
   manuscript model section (RB-004).
2. **RB-006** (C2 high-resolution VDA(r) simulation at multiple v
   values, marking r†(v) closed-form, high priority): the only other
   `priority: high` task in the backlog.

Recommendation: **RB-006**, because the C2 verdict is
CONFIRMED-UNDER-ATTACK (the strongest survival) and the rebuild's
spine narrative ("the robust core that survives intact — C2, C5, and
the central-tendency C1/C3 — becomes the paper's confident spine"
per mission §3.3) leans on C2 being strengthened with the closed-form
r† the reviewer derived. C2 is the rebuild's positive headline; RB-006
is the simulation that backs it.

After RB-006, the natural progression is RB-003 (A1 derivation, low
compute) → RB-004 + RB-009 (manuscript drafts cite figures from
rb-002, rb-003, and the new RB-006 sim).

## Wiki cross-references

§11 mechanism-keyword sweep against `research_db/` for the C1 corpus
this run is grounded in. The reviewer's C1 verdict
(`Critique/verdicts/C1--criterion-fraction-floor.md` §"Wiki cross-
references") already enumerates the relevant wiki entries; this run
re-checked but did not consult them in depth (the rebuild's
distributional restatement is grounded in the simulation, not in new
literature). Relevant entries:

- [[muller_findlay1987_sensitivity_criterion]] — foundational SDT
  cueing decomposition; not bearing on the floor itself.
- [[hawkins1990_attention_detectability]] — foundational sensitivity-
  side cueing; not bearing on the floor.
- [[luo_maunsell2018_criterion_sensitivity]] — neural substrate; not
  bearing on the floor.
- [[sridharan2017_sc_sensitivity_bias]] — strongest empirical
  convergence with "criterion typically dominates" (qualitative);
  no quantitative CF floor in this paper.
- [[carrasco2011_visual_attention_25y]] — background.

The empirical CF-floor literature gap the reviewer flagged in §"Loose
ends" remains open. No new stubs added this run; one will be added if
RB-009 (manuscript section) requires a citation not yet in the wiki.
