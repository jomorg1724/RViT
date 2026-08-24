---
type: conversation
agent: paper-writer
prompt_version: "0.2"
run_id: 9E4D7C13-6A21-4F0B-B8E5-1D7C2A93F6E4
started: 2026-05-30T23:30:00Z
ended: 2026-05-30T23:59:59Z
worked_on: SY-007
output_kind: section
section_touched: "sections/results.tex (new subsection sec:results-noninversion)"
artifacts_consumed:
  - "Rebuild/CLAIM_LEDGER.md (C4 row, silent ceiling)"
  - "Rebuild/manuscript/sections/results.tex §results-c4 (source prose + equations)"
  - "Rebuild/sims/C4--anti-cue-inversion/output/figures/{r_inv_closed_form,er_vs_alpha_anticue,alpha_star_V_r_map}.png"
firewall_violations_fixed: 0
gaps_opened: 0
gaps_closed: 0
compiles: true
manuscript_pages: 21
---

# SY-007 — Results: optimal allocation does not invert under predictive cues

## What I wrote

The closing finding of the Results arc, as a new subsection
`sec:results-noninversion` titled *"Optimal allocation does not invert
when the cue is predictive."* Written in clean, positive Nature
Neuroscience voice — opens with the question and the model's answer, not
with any comparison to another statement.

Structure (8 paragraphs, 3 tables, 3 figures):

1. **Positive opening** — under a predictive cue the optimum never goes
   below the uniform share $1/\Nloc$; the governing boundary is sharp and
   closed-form, and crossing it inverts the policy.
2. **Value-weight inequality** `eq:value-weight`
   $w_c\ge w_u \iff \valid\ge1/[(\Nloc-1)\val+1]$, with the universal
   worst-case condition $\valid\ge1/\Nloc$ at $\val=1$; location-count
   asymmetry mechanism.
3. **Closed-form boundary** — left-derivative `eq:boundary-derivative`,
   threshold `eq:r-inv` $\rstarinv=(\Nloc-1)A_0/B_0$, exact
   symmetric-corner identity `eq:r-inv-corner`
   $\rstarinv(1/\Nloc,1,\cdots)=1$. Full derivation deferred to
   Supplementary (`sec:appendix`, SY-011).
4. **Closed-form tally** Table `tab:noninv-tally` (4 panels; 48.6%→51.9%
   of cells with $\rstarinv\in[0.1,10]$ under decorrelation; median falls
   13%/21%) + Fig `fig:r-inv-map`.
5. **Zero global inversions** on the 12-probe predictive-cue sweep,
   Table `tab:noninv-sweep` + Fig `fig:er-alpha-anticue`.
6. **Counter-predictive inversion** as a new falsifiable prediction:
   36.1% ($\corr=0$) / 34.7% ($\corr=0.2$) incidence on the $\valid<1/N$
   sub-grid, stratified Table `tab:anticue` (75% at $\val=1$, 12.5% at
   $\val=5$; boundary $1/16$) + Fig `fig:alpha-star-map`.
7. **Robustness + decorrelation independence** (the SY-007
   "robustness-across-parameters" element): holds in both variants;
   $\corr$ shifts *where* the sign-flip occurs but not the global
   value-weight decision.
8. **Behavioural alignment** (six pre-existing citations) + **Scope**.

## Grounding

Every scientific assertion is traced N0–N8 + Robustness in `TRACE.md`
against the C4 anti-cue-inversion simulation output (step_A tally,
step_B rows, step_C incidence, step_D map) and the C4 formal derivation,
at the LEDGER:C4 ceiling. Equations `eq:value-weight`,
`eq:boundary-derivative`, `eq:r-inv`, `eq:r-inv-corner` are copied from
the validated math (notation matches the `\newcommand` block;
`\rstarinv` already defined). All table/figure numbers are verbatim from
the ledger row and the source table. No number, mechanism, or claim was
invented.

## Strength check

Nothing exceeds the evidence. The ceiling is CONFIRMED-CONDITIONAL; I
stated the no-inversion result as a conditional theorem (holds for
$\valid\ge1/\Nloc$) and the counter-predictive inversion as a new
falsifiable prediction — exactly the strength the ledger licenses. The
ledger's own "regardless of $\Rsens$" phrasing is **not** reproduced; it
is replaced by the positive closed-form bimodality story, which is both
more accurate and firewall-safe (no "rather than" / correction framing).
The $\valid$-grid bracketing and the variant-A-only counter-predictive
sweep are stated as scope, not as weaknesses of an absent claim.

## Firewall sweep

Grep across all `.tex` for the banned vocabulary
(reconstruct/rebuild/synthesiz/inherited/prior/previous/published/
critique/reviewer/verdict/ledger/provenance/defensible/restate/as-published/
sha256/step-[ABCD]/RB-/SY-/claim-ids): **0 hits**. The section was
authored positively from scratch — no de-meta rewrite needed within it.
Captions describe content + parameters only (no "Reproduced from
Rebuild/..." paths, which the source carried). The two `.tex` comments I
added describe content only.

## Gaps

None opened, none closed. All three figures existed in the C4 sim
output and were copied in. G-001 (the Model attention→$d'$ illustration
figure) remains the single open gap, unrelated to this section.

## Compile

Clean 3-pass build (pdflatex → bibtex → pdflatex → pdflatex). **21
pages** (was 17), 0 undefined references, 0 undefined citations, 0
overfull hboxes, no errors. 0 new bib entries (all six behavioural keys
already in `refs.bib`).

## Next increment

SY-008 — the Discussion: why criterion adjustment dominates; the
re-scoped, quantitative experimental-design guidance; the biological
reading of the benefit/cost ratio $\Rsens$; and the new predictions
(counter-predictive inversion; the dormant-cell decorrelation
amplification flagged in `sec:results-graded`; conservation-band
sensitivity). Per mission §9, do not reproduce any neural-network /
vision-transformer self-reference. After Discussion, SY-009 is the second
interleaved coherence pass over Results + Discussion.

## Drift watch

- Counter-predictive sweep is variant-A only; the variant-B
  higher-incidence band is forward-referenced to the Discussion
  (`sec:discussion`, SY-008). Ref resolves (stub exists).
- Full derivation of the boundary equations is forward-referenced to
  the Supplementary (`sec:appendix`, SY-011). Ref resolves (stub exists).
- The Results argument (model + four findings) is now complete; the
  Intro four-finding preview should be re-checked against the finished
  Results strength in the SY-012 whole-paper coherence pass.
