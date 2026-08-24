---
type: conversation
agent: paper-writer
prompt_version: "0.2"
run_id: C3D9A1F7-8B20-4E5C-9F61-2A7D4C0E8B13
started: 2026-05-31T00:00:00Z
ended: 2026-05-31T00:00:00Z
worked_on: SY-009
output_kind: coherence
section_touched: ["sections/results.tex", "sections/discussion.tex"]
artifacts_consumed:
  - "Reconstruction/manuscript/sections/{model,methods,results,discussion,intro}.tex"
  - "Rebuild/manuscript/sections/model.tex (variant A/B authority)"
  - "Rebuild/manuscript/sections/extensions.tex (additive->multiplicative CF medians)"
  - "Rebuild/manuscript/sections/results.tex (CR / r-dagger framing)"
firewall_violations_fixed: 0
gaps_opened: 0
gaps_closed: 0
compiles: true
manuscript_pages: 26
---

# SY-009 — Coherence pass over Results + Discussion

## Task selection

State on entry: `firewall_clean: true` (the mandated de-meta scrub
completed at SY-015; coherence passes re-sweep it). Eight sections are
written (intro, model, four Results findings, discussion, methods). Four
sections have landed since the last coherence pass (SY-005): SY-006,
SY-007, SY-008, SY-010 — so a second interleaved coherence pass is due
per mission §4.1. SY-009 (Results + Discussion) is the highest-priority
unblocked task and the natural pick. The scheduled-task's "de-meta scrub
first" mandate is satisfied (firewall already clean); a coherence pass
also always re-sweeps the firewall, so the scrub vigilance is honoured
this run as well.

## What I wrote

No new prose; a coherence pass. I found one substantive cross-section
defect and corrected it, and confirmed everything else is consistent.

**The defect — a reward-variant / conservation-rule conflation.** The
model has two *orthogonal* binary axes:

- **Reward variant:** variant~A = value-coupled correct-rejection reward
  ($\CR=\valid\val+(1-\valid)$); variant~B = fixed ($\CR=1$).
- **Conservation rule:** additive ($\benefit+\cost=2$) vs multiplicative
  ($\benefit\cdot\cost=1$) — a separate one-parameter family.

The Reconstruction's own **Model §2.4** and **Methods** already define
A/B as the *reward* variant and treat the conservation rule as a separate
family. But **Results §4.1/§4.2** and the **Discussion** had drifted into
calling A/B "conservation variants" and into pairing the median
$\CF=0.7552$ with "the additive rule" — conflating the two axes. The
giveaway that they are orthogonal is in the §4.1 robustness paragraph
itself: it reports the additive→multiplicative CF-median shift as
$-0.0012$ for variant~A and $-0.0042$ for variant~B, i.e. A/B *persist*
across the conservation move.

Five content-preserving fixes (no number changed):

1. `results.tex` — "conservation variant" → "reward variant" at all 7
   occurrences, including the `tab:cf-distribution` and `fig:cf-histogram`
   captions.
2. `results.tex` §4.1 robustness paragraph — additive/multiplicative are
   now the conservation-family **endpoints** swept within each reward
   variant, not "the two variants above."
3. `results.tex` §4.2 — "$\CR(\val)$ encodes the conservation rule" →
   "$\CR(\val)$ is the correct-rejection reward scaling set by the reward
   variant"; $\CR(\val)=1$ retained as the value-blind computational
   setting, additive conservation named as the (separate) weight rule.
4. `discussion.tex` opening — medians $0.7552$/$0.7682$ re-attributed to
   the value-coupled / equal-reward **variants**, both at additive
   conservation.
5. `discussion.tex` "New predictions" — "the additive, value-weighted
   convention" → "the value-coupled reward variant."

## Grounding

A coherence pass asserts nothing new. The authority for the
variant/conservation distinction:

- `Rebuild/manuscript/sections/model.tex`: "variant~A (value-scaled
  correct rejections, $\CR=\valid\val+(1-\valid)$) and variant~B
  ($\CR=1$); the additive conservation rule is varied [separately]."
- `Rebuild/manuscript/sections/extensions.tex`: median CF $0.7552\to0.7540$
  (variant~A) and $0.7682\to0.7640$ (variant~B) as additive→multiplicative
  — A/B orthogonal to the conservation move.
- The Reconstruction's Model §2.4 and Methods §"Benefit, cost, and reward
  variants" — same definition, already correct.

The Reconstruction's *numbers* were already correct and source-consistent;
only the *labels* drifted. Recorded as the SY-009 note in `TRACE.md`.

## Strength check

Nothing added, removed, or restated at a different strength. The
distributional CF finding (median $\approx0.76$, tail), the non-monotonic
VDA centerpiece, the graded contour band, and the conditional no-inversion
theorem are all stated exactly as before — only the variant/conservation
vocabulary was harmonised. No assertion exceeds its ceiling.

## Firewall sweep

Re-swept `results.tex` + `discussion.tex` for the full banned-vocabulary
set (reconstruct/rebuild/synthesiz/verdict/ledger/provenance/defensible/
critique/reviewer/as-published/inherited/prior/previous): **zero hits.**
The replacement wording ("reward variant", "value-coupled",
"conservation-family endpoints") is positive, standalone science. No meta
reached the page.

## Coherence checks that passed without edits

- **Cross-reference graph:** 51 distinct `\ref`/`\eqref` targets, every one
  defined; no dangling refs; 0 undefined citations.
- **Intro ↔ body:** the four-finding previews match body strength
  (criterion median $\approx0.76$ in $[0.30,1.00]$ with a $\corr$-growing
  tail; non-monotonic VDA with the $\rdagger(\val)$ lower edge; graded
  iso-VDA band; conditional no-inversion $\valid\ge1/\Nloc$ + anti-cue
  prediction).
- **Prediction wording Results ↔ Discussion:** dormant-cell amplification
  $\VDA\,0.0007\!\to\!0.0676$ ($\approx96\times$) ↔ "roughly a
  hundredfold"; anti-cue boundary $\valid<1/[(\Nloc-1)\val+1]$ identical;
  design thresholds $\valid\ge0.95$ / $\ge0.80$-at-$\corr{=}0$ /
  $\ge0.75$-too-permissive stated identically in both sections.
- **Notation:** density glyph uniformly $\varphi$ (the SY-005 fix held);
  no stray bare `\phi`.

## Gaps

0 opened, 0 closed. **G-001** (the attention-to-$\dprime$ mapping figure
in the Model, owner→upstream) remains the single open gap, untouched.

## Compile

`pdflatex`×3 + `bibtex`, all exit 0. **26 pages** (unchanged), 0 undefined
references, 0 undefined citations, 0 overfull `\hbox`, no errors.

## Next increment

**SY-011 — the Supplementary material** (`sections/appendix.tex`): the
symmetric recovery at $\Rsens=1$; the $\rdagger(\val)$ closed-form
derivation; the correlation-aware $\rdagger(\val;\corr)$ extension and
drift table; the $\rstarinv$ / symmetric-corner derivation; the power-mean
conservation family. These are forward-referenced from Results §4.2/§4.5
and Methods and currently point at the `sec:appendix` stub. After that:
SY-012 (whole-paper coherence, pre-abstract) → SY-013 (Abstract, last) →
SY-014 (frontmatter / draft-complete milestone). G-001 is the only thing
standing between the current draft and a zero-open-gap state.

## Drift watch

Did not re-open `Critique/verdicts/` this run (coherence pass, no finding
strength touched). The variant/conservation distinction is structural in
the model definitions, not a contested-strength claim, so no ledger drift
applies. No action.
