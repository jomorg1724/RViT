---
type: conversation
agent: paper-writer
prompt_version: "0.2"
run_id: 2F9C61B4-7A3E-4C81-B0D5-9E62F1A4C73B
started: 2026-05-30T23:40:00Z
ended: 2026-05-30T23:59:59Z
worked_on: "SY-005 — first interleaved coherence pass (Intro + Model + Results §4.1–§4.2)"
output_kind: coherence
section_touched: ["sections/model.tex", "sections/results.tex", "manuscript/BUILD.md"]
artifacts_consumed: ["manuscript/main.tex", "manuscript/sections/*.tex", "manuscript/refs.bib", "build log"]
firewall_violations_fixed: 0
gaps_opened: 0
gaps_closed: 0
compiles: true
manuscript_pages: 13
---

# Run summary

Selected SY-005, the first interleaved coherence pass, per the mission's
"after every 2–3 sections" cadence (four sections — Intro, Model,
Results §4.1, Results §4.2 — were integrated, and the prior run's log
explicitly handed off to SY-005). The pass is content-preserving: it
fixed consistency and typesetting defects only; no scientific assertion,
number, equation, or figure changed.

## What I wrote / changed

Five fixes, all in `sections/model.tex` and `sections/results.tex`:

1. **Density glyph unified to $\varphi$.** Results' gradient
   coefficients $K_c, K_u$ (Eqs. `eq:K-c`, `eq:K-u`) wrote the
   standard-normal density as $\phi$, while the Model's boxed orthant
   integral (`eq:pnofa-rho`) uses $\varphi$. Since the $K$ equations are
   agent-authored (SY-004) and the Model integral is copied upstream
   math, I conformed the Results glyph to the Model — 4 occurrences
   $\phi\!\to\!\varphi$ — and left the upstream equation untouched.

2. **Baseline-$\dprime$ symbol de-duplicated.** Results §4.2 introduced
   $\dprime_b := \dprimemax f(1/\Nloc)$ — the same quantity the Model
   already defines (§2.3) as $\dprime_{\mathrm{base}}$. I changed the
   `:=` to an identification $\dprime_b \equiv \dprime_{\mathrm{base}}$
   with a pointer to Section~\ref{sec:model}. The quantity is now defined
   once; the compact subscript $\dprime_b$ remains a stated shorthand for
   the dense $K$ expressions (keeps them narrow, avoids a fresh overfull
   box).

3. **"Appendix" → "Supplementary."** The de-meta scrub (SY-015) renamed
   the section heading to "Supplementary derivations and extensions" and
   Results refers to "the Supplementary material," but two Model
   cross-references still said "Appendix~\ref{sec:appendix}." Conformed
   both to "the Supplementary material (Section~\ref{sec:appendix})"
   (Nature format, mission §5.5). Internal `\appendix`, `\label{sec:appendix}`,
   and `appendix.tex` left as-is — none render to the reader.

4. **Overfull `\hbox` cleared.** Exactly one overfull box remained
   (54.7pt), in the Results §4.2 paragraph "The threshold falls as cued
   value rises," where the wide configuration tuple
   $(\Nloc,\dprimemax,f_0,h,\valid)=(4,2,0.5,\sqrt\cdot,0.5)$ was forced
   at a tight line start. Re-ordered the sentence ("Evaluating
   Eqs.~…–… at the configuration … gives the values in
   Table~…") so the tuple has a breakpoint before it. The Model §2.4 box
   flagged in SY-003/SY-004 had already cleared once SY-004 re-paginated;
   the live build showed only the Results one.

5. **Two "continuous trace" → "continuous curve"** (the plotted-line
   sense, in the body and the `r_dagger_vs_v` caption) — clearer, and
   also removes the only borderline `trace` substring the firewall grep
   was catching.

## Grounding

No new assertions. Every TRACE row for Intro (I1–I11), Model (M1–M14),
Results §4.1 (R0–R8), and Results §4.2 (V0–V7) still holds verbatim; the
fixes touch glyphs, one symbol identity, cross-reference wording, and
line-breaking, not content. A content-preserving note was added to
`TRACE.md`.

## Strength check

Nothing changed strength. The four-finding previews in the Introduction
remain matched to the §4.1–§4.2 body: criterion fraction as a
distribution (median $\approx 0.76$, span $[0.30,1.00]$, tail), VDA
non-monotonic in $\Rsens$ with $\rdagger(\val)$ the closed-form lower
edge of the active band. No categorical floors; the non-monotonicity
stays at its confident-centerpiece ceiling.

## Firewall sweep

Re-swept `main.tex`, all `sections/*.tex`, and `refs.bib` for the full
banned-vocabulary set (reconstruct/rebuild/synthesiz/original/prior/
previous/published/critique/reviewer/verdict/ledger/provenance/
defensible/restate/TRACE/inherited/sha256/comparison-hedges/Appendix).
**Zero reader-visible hits.** Remaining grep matches are the internal
`sec:appendix` label, the `\appendix` command, and the `appendix.tex`
filename — LaTeX scaffolding that never renders. `firewall_clean` stays
true.

## Gaps

None opened, none closed. G-001 (the attention-to-$\dprime$ mapping
figure, Model §2.3) remains open and non-blocking, with its red
placeholder intact.

## Compile

`pdflatex ×3 + bibtex`, all exit 0. **13 pages**, **0 overfull `\hbox`**
(was 1×54.7pt), 0 undefined references, 0 undefined citations.

## Next increment

SY-006 — Results §4.4, the graded regime where VDA matters (C3): the
iso-VDA contour band over $(\valid, \val, \Rsens)$, the high-$\valid$
probe table, and the graded design boundary, in graded (not "negligible
regardless") voice. Place `iso_vda_contours` / `vda_at_high_V` /
`iso_vda_drho` if those sims are staged under `Rebuild/`; gap any absent
figure. Then SY-007 (§4.5–4.6, C4 + robustness), and the SY-009
coherence pass once the Discussion (SY-008) lands.

## Drift watch

- Intro finding-1 preview says the attention-dominated tail "grows as
  correlated noise ($\corr>0$) is admitted." The §4.1 body shows this for
  variant~A (the V4-anchored variant; tail $\times 3$ at $\corr=0.2$)
  while variant~B is mixed. The preview is fair at preview granularity
  (the dominant tendency is growth) and does not overstate — left
  unchanged, but flagged for the SY-009 pass to re-check once the
  Discussion makes the variant split explicit.
- §4.1/§4.2 forward-references to `sec:discussion` (conservation band;
  sign of $\partial\VDA/\partial\corr$) currently resolve to a stub.
  SY-009 must confirm they point at real content after SY-008.
