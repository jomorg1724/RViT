---
type: conversation
agent: paper-writer
prompt_version: "0.2"
run_id: 2C4E6A80-1D3F-4B52-9C61-7A84E2F5B903
started: 2026-05-31T14:05:00Z
ended: 2026-05-31T14:30:00Z
worked_on: SY-013
output_kind: frontmatter
section_touched:
  - sections/abstract.tex
artifacts_consumed:
  - Reconstruction/manuscript/sections/intro.tex
  - Reconstruction/manuscript/sections/results.tex
  - Reconstruction/manuscript/sections/discussion.tex
  - Rebuild/CLAIM_LEDGER.md (silent ceiling)
  - Rebuild/manuscript/sections/abstract.tex (source voice — NOT re-flowed)
firewall_violations_fixed: 1   # de-meta'd the file's lone .tex comment
gaps_opened: 0
gaps_closed: 0
compiles: true   # 33 pages, 0 undefined refs/citations, 0 bibtex warnings
---

# SY-013 — Abstract (written last, from the finished body)

## Selection
The whole-paper pre-abstract coherence pass (SY-012) is done and
`synthesizer_state.json` carries `firewall_clean: true`; the body, Methods,
and Supplementary are all written. The abstract is the mission's designated
last first-draft increment (§4.1), written from the finished body, and was
the highest-priority unblocked task. SY-014 (front/back-matter) is its only
successor and depends on it.

## What I wrote
Replaced the red abstract stub in `sections/abstract.tex` with a single
unstructured paragraph (~205 words), no citations, no meta. It states the
cued change-detection task and the three adaptive levers (criterion,
value-directed attention, decorrelation — cross-location correlation a free
parameter whose zero limit recovers independent noise), then the four
findings positively: C1 criterion typically dominant (median ≈¾ of the
reward gain, with a material tail); C2 attention benefit non-monotonic in
the benefit/cost ratio with a closed-form lower edge; C3 concentrated in a
graded regime mapped to validity thresholds for cueing designs; C4 no
inversion under a predictive cue (conditional theorem) + anti-cue inversion
as a new falsifiable prediction.

## Grounding (assertion → evidence)
Every clause restates an already-grounded body result (AB1–AB6 in
`TRACE.md`): C1 `sec:results-criterion` (median CF 0.7552 A / 0.7682 B,
`tab:cf-distribution`); C2 `sec:results-vda-nonmonotonic` (`eq:r-dagger`);
C3 `sec:results-graded` (iso-VDA band; $\valid\gtrsim0.95$ / $0.8$ design
guidance); C4 `sec:results-noninversion` (`eq:value-weight`, condition
$\valid\ge1/\Nloc$; 36.1% anti-cue inversion at $\Nloc=4$). The model
setup (three levers, $\corr$ free, $\corr\to0$ recovery) maps to `sec:model`
+ `def:three-levers` + `eq:rho-zero-recovery`.

## Strength check
Nothing exceeds the evidence. The abstract introduces no number, mechanism,
or claim absent from the body; each finding is stated at the same
distributional / closed-form / graded / conditional strength as its body
section and its CLAIM_LEDGER row. No claim restated above its ceiling.

## Firewall sweep
The `Rebuild/` source abstract is written in build-process voice
("we rebuild", "the inherited independent-noise model", "the published
[0.60, 0.96] interval is retracted", "Independence is not an upper bound",
"nothing … stated more strongly than its `CLAIM_LEDGER.md` licenses"). None
of that was re-flowed. I wrote a fresh, positive, standalone abstract.
Banned-vocabulary grep on `abstract.tex`: zero hits — no
reconstruction/inherited/published/retracted/ledger language, no
comparison-hedge ("rather than…", "not a categorical…"), no version tag.
The file's single `%` comment ("written last, from the finished body") was
tightened to a content description ("unstructured summary of the model and
the four findings") so even the comments carry no authoring/build process.

## Gaps
None opened, none closed. **G-001** (model §2.3 attention-to-$\dprime$
illustration figure) remains open and owner-mediated; its red placeholder
still stands and compiles.

## Compile
`pdflatex` ×2 + `bibtex` + `pdflatex` ×2, exit 0. **33 pages.** 0 undefined
references, 0 undefined citations, 0 bibtex warnings. Single pre-existing
3.0pt overfull hbox (Supplementary, Corollary 2) — not introduced by the
abstract.

## Next increment
**SY-014** — front/back-matter finalisation: the title and `[Author names]`
/ `[Affiliations]` block are already clean; finalise the figure list and do
the final build. Milestone gate: "submission-ready draft" requires zero
open gaps, and **G-001 is still open**, so SY-014 cannot flip the README to
"draft complete" until the model figure is staged by the owner-routed
rebuilder or a decision is taken to drop that illustration.

## Drift watch
- No `Critique/verdicts/` drift was checked this run (the abstract restated
  findings already fixed by the body; it touched no finding's strength).
  The next finding-touching run should spot-check before restating.
- The headline CF medians (0.7552 / 0.7682) and the 36.1% anti-cue figure
  are quoted in the abstract exactly as in the body; if a future sharpening
  run (e.g. a rebuilder finer-grid re-run) moves them, the abstract and the
  body sentences must move together.
