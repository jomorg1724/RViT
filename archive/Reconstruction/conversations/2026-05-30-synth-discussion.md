---
type: conversation
agent: paper-writer
prompt_version: "0.2"
run_id: 4A8E2D17-9C0B-4E6A-A1F2-7B3D5E8C09A4
started: 2026-05-30T23:30:00Z
ended: 2026-05-30T23:59:59Z
worked_on: SY-008
output_kind: section
section_touched: sections/discussion.tex
artifacts_consumed:
  - Rebuild/CLAIM_LEDGER.md (C1, C2, C3, C4 rows; non-claims)
  - Rebuild/manuscript/sections/limitations.tex (scope content, framing stripped)
  - Reconstruction/manuscript/sections/results.tex (forward-ref targets, design box, prediction numbers)
  - Reconstruction/manuscript/sections/intro.tex (four-finding framing, three-lever setup)
  - Reconstruction/manuscript/main.tex (macros, labels, bib keys)
firewall_violations_fixed: 0
gaps_opened: 0
gaps_closed: 0
compiles: true
manuscript_pages: 24
---

# SY-008 — Discussion

## What I wrote
Replaced the red placeholder in `sections/discussion.tex` with the full
Discussion, in clean positive Nature Neuroscience voice. Structure:

- **Opening synthesis** — the four findings recapped as one layered
  answer to "when does VDA matter."
- **Why criterion adjustment is typically dominant** — the price
  difference between the two levers (criterion is free of perceptual
  reallocation; VDA pays a trade-off), why residual value is most
  economically booked into thresholds under predictive cues, the CF
  median (0.7552 / 0.7682) and $[0.30,1.00]$ concentration, and the
  benefit-dominant low-validity corner where the lever cedes.
- **The benefit/cost asymmetry and its biological reading** — $\Rsens$
  as the enhancement/suppression efficacy ratio, read through the
  normalisation/gain literature; a clean mechanistic reading of the
  non-monotonicity (cheap enhancement → already attended; very expensive
  → nobody re-allocates; peak in between), with the lower edge
  $\rdagger(\val)$.
- **Guidance for experimental design** — the quantitative validity
  thresholds, and why standard high-validity cueing paradigms sit in the
  dormant regime; how to design into the cost-dominant low-validity
  high-contrast corner to isolate VDA.
- **New predictions** — (1) anti-cue inversion under $\valid<1/\Nloc$,
  sharply bounded, absent in the predictive regime, a falsifiable
  re-allocation signature; (2) decorrelation as an active lever whose
  effect on VDA changes sign with $\Rsens$, with a ~100× dormant-cell
  amplification at the empirical $\corr=0.2$ anchor; (3) the
  conservation-form sensitivity of the criterion/attention tail (median
  fixed, tail rule-dependent) and the deeper variant-B tail / higher
  anti-cue incidence.
- **Scope and limitations** — conservation rule as a one-parameter
  family, bounded heterogeneity, the decision-noise channel as a natural
  further axis (not included), transfer-function family, equicorrelation
  scope, and the explicit non-claims (normative + stationary; no neural
  implementation claim beyond the $\Rsens$↔gain-control correspondence).

## Grounding
See TRACE.md rows D0–D9. Every scientific sentence maps to a LEDGER row
(C1–C4, conservation band, non-claims) and the corresponding Results
subsection; the biological reading cites only pre-existing bib keys
(reynolds_heeger2009, mcadams_maunsell1999, treue_martinez_trujillo1999,
carrasco2011, CohenMaunsell2009, RuffCohen2016, Srinath2021). The
limitations content was lifted from `Rebuild/.../limitations.tex` and
restated as the model's own scope, with all build framing removed.

## Strength check
Nothing exceeds the ledger. C1 is distributional (median + tail, no
floor, no "regardless"); C2 is the confident centerpiece; C3 is graded /
contour-band; C4 is a conditional theorem with the anti-cue inversion as
a positive new prediction; the decorrelation sign is a model property;
the conservation/variant sensitivities are reported as bands. The
biological reading is explicitly hedged and paired with the
no-neural-implementation limitation, so no interpretive sentence is
stated as a result.

## Firewall sweep
Zero violations introduced. `grep -niE` over `discussion.tex` for the
full banned-vocabulary set returns only `inVERSION` / `noninVERSION`
substring false-positives (the regex `version` inside "inversion").
One pre-emptive reword: "the cue carries little prior" → "the cue is
weakly informative", to avoid the bare banned-cousin word *prior* even
though it was used in its statistical sense. No prior/original/rebuilt/
reviewer/ledger/verdict language anywhere; no comparison-hedge
constructions; the conservation-form and variant-B findings are stated
as positive structural properties of the model, not as corrections of an
absent statement. The upstream §5.3 NN/vision-transformer self-reference
was deliberately not reconstructed (mission §9); it is an internal
cross-link, not a scientific element, so no gap was opened.

## Gaps
None opened, none closed. G-001 (the Model Figure 1 attention→$d'$
mapping placeholder) remains open and owner-mediated.

## Compile
Clean 3-pass `pdflatex` + `bibtex`. 24 pages (was 21 at SY-007). 0
undefined references/citations, 0 overfull hboxes >20pt, 0 LaTeX
warnings.

## Next increment
SY-009 — second interleaved coherence pass over Results + Discussion:
confirm the §4.1/§4.3/§4.4 forward-refs to `sec:discussion` resolve to
the matching content (D5/D7/D8 — they do); check prediction wording is
identical in both places (anti-cue boundary, decorrelation sign,
conservation tail); verify notation and figure refs; re-sweep the
firewall end to end. Then SY-010 (Methods), SY-011 (Supplementary), and
the abstract (SY-013) last.

## Drift watch
- One broken cross-reference fixed: my first draft cited
  `\eqref{eq:conservation-family}`, which does not exist in this
  manuscript (the power-mean family is carried as prose, not a labelled
  equation). Re-pointed to `Section~\ref{sec:model}` +
  `\eqref{eq:beta-gamma}`, matching the §4.1 robustness paragraph's own
  phrasing. SY-009 should confirm the conservation-family discussion
  reads consistently between §4.1 and the Discussion.
- The Discussion states variant-B has "a somewhat higher anti-cue
  inversion incidence" inferred from its lower median $\rstarinv$
  (`tab:noninv-tally`); the Results §4.4 scope paragraph makes the same
  inference. This is a reading of the lower median, consistent with
  LEDGER:C4 — no variant-B anti-cue sweep has been run, so the wording
  stays at "indicates"/"somewhat", not a quantified incidence. Flag for
  SY-009 to keep both places hedged identically.
