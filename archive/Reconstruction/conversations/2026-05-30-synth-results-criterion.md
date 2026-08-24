---
type: conversation
agent: integrative-synthesizer
prompt_version: 0.1
run_id: D8A3F1C2-6B47-4E92-A5D0-1C9E7B3F4A86
started: 2026-05-30T23:05:00Z
ended: 2026-05-30T23:35:00Z
worked_on: SY-003
output_kind: section
section_touched: sections/results.tex (Results header + §4.1 sec:results-criterion)
artifacts_consumed:
  - Critique/source/main.pdf §4.1 (structure + corrected wording)
  - Rebuild/CLAIM_LEDGER.md row C1 (+ A1 for the §5.5 retraction)
  - Rebuild/manuscript/sections/results.tex §results-c1 (harvest material)
  - Rebuild/sims/C1--cf-distribution/ (sha256 91fc4692…) — tables + 3 figures
  - Rebuild/sims/A3--conservation-band/ (sha256 055bf4ec…) — conservation band numbers
  - Rebuild/manuscript/figures/{cf_histogram,cf_heatmap,cf_curves}.png (copied)
gaps_opened: []
gaps_closed: []
compiles: true
manuscript_pages: 11
---

# SY-003 — Results §4.1: criterion typically dominates (C1)

## What I assembled
Opened the Results section with a four-finding orienting paragraph (the
developing argument the original's Results section makes), then
reconstructed the original's §4.1 *"Criterion Adjustment Dominates Value
Encoding"* as a **distributional** finding (`sec:results-criterion`).
Content: claim restated + corrected; CF distribution table; quadrant
regime table; decorrelation ($\corr$) sensitivity paragraph; conservation-
family robustness paragraph. Three C1 figures placed
(`cf_histogram`, `cf_heatmap`, `cf_curves`).

## Provenance (the §5.2 mandate, discharged)
Full table in `TRACE.md` rows **R0–R8**. Summary:
- **Structure / framing** (R0, R1, R6) → ORIG §4.1. The CF *definition*
  is the Model's `eq:cf-def` — referenced, not re-stated (no duplicate
  label, no second definition).
- **Distribution + quadrant numbers** (R3, R5) → LEDGER:C1 +
  `SIM:C1--cf-distribution` (sha256 `91fc4692…`); table values and all
  three figures lifted from `RB:results.tex` §results-c1.
- **Corrections** (R2, R4) → ORIG §4.1 wording vs LEDGER:C1.
- **$\corr$ sensitivity / §5.5 retraction** (R7) → LEDGER:C1 + LEDGER:A1
  + the same sim at $\corr=0.2$; `BIB:CohenMaunsell2009`.
- **Conservation band** (R8) → LEDGER:C1 + `SIM:A3--conservation-band`
  (sha256 `055bf4ec…`).

Every scientific sentence in §4.1 has a trace row. Editorial connective
tissue (the orienting paragraph, transitions) asserts nothing beyond the
findings it previews.

## Strength check
Wrote against **LEDGER:C1** (CONTESTED → distributional / central-
tendency) and **LEDGER:A1** (CONTESTED → independence bounds the
criterion fraction, not VDA; variant B a sensitivity). Confirmed I did
not exceed either:
- The median (≈0.76) carries "criterion typically dominates"; the
  categorical $[0.60,0.96]$ floor is retracted at both ends, never
  restated.
- "Always the single largest contributor *regardless of $r$*" →
  "*typically* dominant", with the explicit corner where it cedes.
- The §5.5 "upper bound on VDA" is corrected to "upper-bounds the
  criterion fraction, variant A only" — exactly the A1 ledger form.

## Gaps
None opened, none closed. The original §4.1 leads with **Figure 2**
(reward-decomposition stacked bars). No rebuilder artifact regenerates
that bar chart; the rebuild deliberately replaces it with the
distributional `cf_histogram`, and the decomposition it depicts is
already typeset in the Model (Eqs. `eq:gain-criterion`,
`eq:gain-validity`, `eq:vda-def`). Treated as a **supersession, not a
gap** — logged in `TRACE.md`. (G-001 from SY-002 remains open,
untouched.)

## Compile
`pdflatex`×2 + `bibtex` + `pdflatex`, plain TeX Live 2026basic. Clean.
**11 pages** (was 7). 0 undefined references, 0 multiply-defined labels,
0 citation warnings. One pre-existing overfull `\hbox` (~52pt) in Model
§2.4 (the GH-64 quadrature sentence) — unrelated to this increment,
flagged for the SY-005 coherence pass.

## Next increment
**SY-004** — Results 4.2–4.3 (benefit/cost asymmetry shapes allocation +
C2, VDA non-monotonic in $\Rsens$). Re-flow the closed-form escape
threshold $\rdagger(\val)$, peak-vs-threshold confirmation, and the
$\val$-family; place `vda_curves_vfamily` + `r_dagger_vs_v`; fold in the
carried-over VDA-side of the §5.5 retraction (the $\val$-dependent
sign-flip of $\partial\VDA^\star/\partial\corr$) at LEDGER:A1/C2 strength.

## Drift watch
Did not re-open the verdict files this run. The C1 and A1 ledger rows
record no label drift as of rb-047, and §4.1 sits inside both ceilings.
No action.

**Provenance verified** — every claim in §4.1 has a TRACE row (R0–R8).
**Compile verified** — 11 pages, 0 undefined refs, 0 multiply-defined.
