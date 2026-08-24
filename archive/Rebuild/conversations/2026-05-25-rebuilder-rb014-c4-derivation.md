---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-014-2026-05-25
started: 2026-05-25T19:00:00Z
ended: 2026-05-25T19:30:00Z
worked_on: RB-030
output_kind: derivation
claims_touched: [C4]
artifacts_written:
  - Rebuild/derivations/C4--anti-cue-inversion.md
papers_added: []
spawned_tasks: []
---

# rb-014 — C4 anti-cue inversion derivation

## What I built

`Rebuild/derivations/C4--anti-cue-inversion.md` — a self-contained,
rebuild-voiced derivation of the closed-form boundary inversion threshold
`r†_inv = (N - 1) A_0 / B_0` that backs the four cited equations of the
manuscript's §results-c4 section (rb-013, RB-012). The derivation is
~42 KB / 940 lines / 9 sections + Verification block + Extensions list, and
covers:

- §1 setup + the inversion-branch kink at α = 1/N (the β/γ swap)
- §2 boundary partials A_0, B_0 and the one-sided ∂R/∂α derivatives
- §3 the closed form `r†_inv = (N-1) A_0/B_0` (Proposition 3.1) + structural
  mirror to the C2 escape threshold
- §4 ρ-extension via one-factor Gauss-Hermite quadrature + the explicit
  ρ→0 collapse to the inherited analytic form
- §5 **Proposition 5.1 (symmetric-corner identity)** — formal proof from
  FOC symmetry that `r†_inv(V=1/N, v=1, N, CR, ρ) = 1` exactly, for any
  N ≥ 2, any conservation variant, any ρ ∈ [0, 1)
- §6 the value-weight inequality `w_c ≥ w_u ⟺ V ≥ 1/[(N-1)v+1]` +
  location-count asymmetry + **Theorem 6.1 (global no-inversion,
  conditional)** + §6.4 anti-cue prediction from the flipped inequality
- §7 numerical realisation table (equation → run.py line range → results.json
  block key) + three recovery records
- §8 scope (local statement only; equicorrelated only; additive A3 only;
  observational anchor for Theorem 6.1; variant A only for anti-cue)
- §9 references

The derivation is independent of `Critique/derivations/C4--no-inversion.md`
— the math is identical because there is only one correct derivation of
Eq. 3.3, but the framing is rebuild-voiced (constructive Propositions
3.1 / 5.1 + Theorem 6.1 instead of "paper claim X is incomplete"), the
equation labels are fresh (1.1–9), the ρ-extension §4 is *new* (the
reviewer's derivation is ρ = 0 only), and Proposition 5.1's formal
FOC-symmetry proof of the symmetric-corner identity is *new* (the
reviewer's §5 records numerical confirmation and one-sided derivative
algebra at the corner but does not promote the identity to a stated
proposition with ρ-inclusive proof).

## How it connects to the ledger

**C4 (CONFIRMED-CONDITIONAL, live).** Rebuilt strength unchanged. The
*Backing* column of the C4 row in `CLAIM_LEDGER.md` is extended with the
new derivation file. Specifically, the four equations the manuscript
§results-c4 section cites in-line —

- Eq. `value-weight` (`w_c ≥ w_u ⟺ V ≥ 1/[(N-1)v+1]`)
- Eq. `left-derivative` (the boundary left one-sided ∂R/∂α)
- Eq. `r-inv` (the closed form `r†_inv = (N-1) A_0/B_0`)
- Eq. `r-inv-corner` (the symmetric-corner identity `r†_inv = 1`)

— each now has a formal derivation file backing it, plus a ρ-extension
the inherited model did not have, plus a formal proof of the symmetric-
corner identity that the inherited paper does not state.

**A1.** No strength change. The derivation reuses the same one-factor
Gauss-Hermite quadrature the rebuilt model's `p_no_fa_grid` implements
(see `Rebuild/derivations/A1--rho-channel.md` §2 for the parallel
construction), so the ρ-extension here inherits the recovery contract
sha256 `d3c62215…` end-to-end. The rb-012 Step A finding that median
`r†_inv` drops 13–21% from ρ=0 to ρ=0.2 is documented in the derivation
as an empirical observation; a candidate spin-off increment (Slepian-
style monotonicity on the A_0/B_0 ratio in ρ) is listed in §8 Extensions
as a future analytic upgrade.

**No drift.** Live verdict labels all match the §3 table of
`agents/paper_rebuilder_prompt.md` v0.2 (10/10); the §3 A6 stale entry
(OPEN/in-progress vs live WEAKLY-SUPPORTED) remains as flagged in
`CLAIM_LEDGER.md`'s "Drift from §3 of the prompt" section.

## Simulation evidence

This is a derivation-only increment; no new simulation was run. The
evidence consumed is rb-012's `step_A.tally`, `step_B.rows`,
`step_C.incidence_*`, `step_D.frac_inversion`, `recovery_step_Ci.rows`
(sha256 `6ad651d648ae597cdfb28c6fd19b6261e4f9d5cb96b599557e10aad47ffd6d96`,
17.4 s wall-clock). Three recovery records are cited verbatim in §7:

1. **ρ = 0 vs the inherited closed form.** rb-012 Step A's $48.6\%$ vs
   reviewer §4's $49.0\%$ count of cells with `r†_inv ∈ [0.1, 10]` on
   the N=4 primary grid. Δ = 0.4 percentage points. PASS at the
   simulation's 1.0 pp tolerance. The residual is a grid-tie
   reclassification near the `r†_inv ∈ {0.1, 10}` borders, not a
   numerical drift in (4.4) at ρ = 0.

2. **ρ = 0 vs reviewer's §5 Step C(i) table** (V=0.25, v=1, N=4,
   variant A, ρ=0, r ∈ {0.1, 1, 1.585, 2.512, 3.981, 10}). max
   |Δα\*| = 0 (floating-point identity), max |ΔR\*| = 3e-6. PASS at
   tolerances 5e-4 / 5e-5.

3. **Symmetric-corner identity to FP identity under GH quadrature.**
   `step_A.tally.variant_X__rho_Y.min_r_inv_star = 1.0000` in all four
   panels (variant A/B × ρ ∈ {0, 0.2}). A stronger statement than #1
   because it survives the GH quadrature exactly — the ρ-cancellation
   of (5.7) is not just symbolic, it holds at the numerical level.

Output hash for the derivation file itself: 42,062 bytes / 940 lines.

## What the manuscript can now say

The §results-c4 section's "the independent re-derivation in the rebuild's
voice (plus the proof of the symmetric-corner identity below) is
deferred to Section sec:appendix (a separate increment, RB-030, queued)"
sentence (`Rebuild/manuscript/sections/results.tex`, line ~1197) can now
be replaced with a forward reference to `Rebuild/derivations/C4--anti-cue-inversion.md`
§ 5 Proposition 5.1 and § 4 Eqs. 4.2–4.4. The `manuscript/sections/appendix.tex`
`subsection: deriv-C4` stub can now either `\input{}` the derivation
file or reference it externally.

The rebuilt strength on C4 is unchanged. The new artefact strengthens
the *backing* of C4's existing claims — specifically by giving the
manuscript's in-section equations a formal derivation file to cite,
and by promoting the symmetric-corner identity from a numerical
observation to a stated proposition with proof. This is exactly the
"increments, not leaps" pattern of mission §9.5.

This run does *not* modify the manuscript prose itself (one-increment-
per-run discipline). A follow-up manuscript-only increment could either
(a) wire the derivation into `appendix.tex` as `\input{}`'d content with
LaTeX cleanup of the file's macros, or (b) leave the derivation as a
standalone reference file and just tighten the "RB-030 queued"
sentence to cite the now-extant file. Either is a small downstream
manuscript edit.

## Next increment

The C4 thread is now closed (manuscript section + simulation +
derivation all in place). The natural next moves:

- **RB-013 (§appendix-C5 light-touch consistency result).** Low effort,
  no new sim needed (the ρ→0 recovery test in `model/tests/` already
  covers r=1 symmetric recovery to machine precision). Would close the
  five-headline-claim spine and leave only the abstract/intro/
  limitations sections + the A2/A8/A3 extension threads.

- **RB-026 (C2 ρ-extension derivation).** The C2 parallel to the run
  just completed: extend `r†(v) = K_u/[(N-1) K_c]` to ρ > 0 by
  replacing the no-FA terms inside K_c, K_u with the same one-factor
  GH quadrature §4 of this derivation uses. Would let the rebuilt
  manuscript state the rb-004 finding that peak r drifts upward in ρ
  at low v as a closed-form prediction rather than just an empirical
  observation, and would consolidate the rebuild's two main closed-form
  thresholds (C2 and C4) as parallel ρ-aware results.

- **RB-014 (A2 heterogeneous-r model extension).** The largest
  unstarted thread and the most consequential remaining structural
  increment. Would open the A2/A8 heterogeneity story (heterogeneous
  per-location r_i, with the homogeneous recovery test). Three runs
  away from a manuscript §extensions section.

In dependency order, RB-013 is the lowest-cost closer; RB-026 is the
most analytically continuous with the present run; RB-014 is the
largest new thread. My recommendation for the next run is **RB-026**:
it shares the analytic machinery (one-factor GH quadrature on boundary
partials) with the present derivation, parallels the rb-014 / RB-030
arc cleanly, and gives the manuscript a second ρ-aware closed form to
report symmetrically with §4 of the C4 derivation. RB-013 is the
alternate low-cost closer if the run budget is tighter.

## Wiki cross-references

Wiki sweep performed with keywords:

- *boundary inversion*: no exact match; CohenMaunsell2009 (cited) is
  the nearest behavioural-correlation literature; no new stub needed.
- *asymmetric attention transfer*: indirect coverage via Reynolds-
  Heeger normalisation papers already wired (no new stub).
- *β/γ kink*: model-internal; no literature stub applicable.
- *equicorrelated orthant probability*: math-methods; Slepian 1962 +
  Tong 1990 cited by full bibliographic reference (same math-methods
  gap flagged by rb-008/rb-009 — the rebuilder is not adding math-
  methods stubs without owner direction).
- *Gauss-Hermite reduction*: math-methods; no stub.
- *value-weight inequality*: model-internal; no literature stub.
- *location-count asymmetry*: model-internal; no literature stub.
- *symmetric-corner FOC*: model-internal; no literature stub.

No new `research_db/papers/` stubs added. `audit.py` not re-run (no
wiki writes).
