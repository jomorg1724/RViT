---
type: conversation
agent: paper-writer
prompt_version: "0.2"
run_id: "F2C7A9E1-3D04-4B86-9A1F-7E52C0B8D34A"
started: 2026-05-30T23:50:00Z
ended: 2026-05-30T23:59:00Z
worked_on: "De-meta scrub (firewall enforcement) — first task under prompt v0.2"
output_kind: scrub
section_touched: "all (main.tex, abstract, intro, model, results, discussion, methods, appendix, refs.bib)"
artifacts_consumed: []
firewall_violations_fixed: 38
gaps_opened: 0
gaps_closed: 0
compiles: true
manuscript_pages: 10
---

# De-meta scrub (firewall enforcement)

## What I did
First task under prompt v0.2 (mission §4.1, §5.6): swept the entire
manuscript for firewall violations introduced under the earlier framing
and rewrote them into positive, standalone statements. No new science was
written and no claim strength changed — only the build-machinery framing
was removed. The manuscript now presents its findings on their own
footing, with no trace of how it was assembled.

## Violations found and fixed (auditable)

**main.tex**
- Title: collapsed the `\large` styled subtitle into a single clean
  declarative title (no clutter, no version tags). Author block was
  already clean placeholders.

**abstract.tex**
- Removed a mislabeled "GAP G-001" tag on the abstract placeholder (the
  abstract is written last by normal workflow, not blocked by a missing
  artifact). Now a neutral placeholder.

**intro.tex**
- "a result we sharpen to a conditional theorem" → "a result that holds
  as a conditional theorem" (removed the comparison-hedge verb).

**discussion.tex / methods.tex / appendix.tex** (placeholder sections)
- Stripped meta comment blocks ("the original's …", "the rebuilder's …",
  "ledger strength", "reconstruction", SY-ids) → content-only comments.
- Rewrote the visible red placeholders to plain "to be written" text with
  no "original"/"rebuilder"/"ledger"/SY-id language.
- "Appendix" retitled "Supplementary derivations and extensions" (Nature
  uses Supplementary, not Appendix — §5.5).

**model.tex**
- Stripped the entire meta comment header (ORIGINAL, reconstructs,
  rebuilder, CLAIM_LEDGER, Provenance/TRACE.md, deferral bookkeeping) →
  content-only.
- Opening paragraph: "the inherited signal-detection account … The
  reconstruction adds one structural element the inherited model
  omitted … recasts the original two-mechanism description" → positive
  statement of the three-mechanism model with the ρ=0 reduction.
- "Under the inherited additive conservation rule" → "Under an additive
  conservation rule".
- Removed the `Rebuild/model/core.py` implementation reference sentence.
- GAP G-001 placeholder: stripped "original Figure 1", the `Rebuild/`
  path, and the `Reconstruction/GAP_REQUESTS.md` path → terse
  "[GAP G-001: needs the attention-to-d′ mapping figure.]" per §5.4.
- "The inherited model assumes the per-location decision variables are
  independent" → "Under independent per-location decision variables".
- Quadrature paragraph: removed "The rebuilt model evaluates it … 
  (Rebuild/model/core.py:…)" → "We evaluate it by 64-node Gauss–Hermite
  quadrature …".
- Recovery-contract paragraph: removed two "inherited model" references,
  the `Rebuild/model/tests/test_recovery.py` path, and "the
  reconstruction" → positive statement that the ρ=0 limit coincides with
  the independent-noise model.
- "Three levers, not two." heading + "The inherited paper decomposes …"
  → "Three levers." + "At fixed correlation the value response
  decomposes into two levers …".
- "moving ρ off the inherited ρ=0 corner" → "off the ρ=0 corner".
- Closing paragraph: removed "not a free mechanism the reconstruction
  invents; … the inherited model held permanently … The inherited paper
  further claimed …" → positive grounding of the decorrelation lever in
  physiology and a neutral statement of the ∂VDA/∂ρ question.

**results.tex**
- Stripped the meta comment header (reconstructed, original's, Rebuild
  paths, CLAIM_LEDGER, C1–C4, SY-ids) → content-only.
- "We organise the results as the inherited paper does" → "We present
  four findings …".
- Orienting paragraph: removed "not as the categorical floor the
  inherited paper reported", "a result we retain at full strength and
  strengthen", "rather than asserting that VDA is negligible 'regardless
  of other parameters'" → positive statements of each finding.
- §4.1 opener: removed the quoted "the inherited paper summarises CF
  categorically … 'criterion adjustment is always the single largest
  contributor' … Our reconstruction sustains the substantive reading …
  retracts the categorical floor" → positive distributional statement.
  Paragraph heading "…is a distribution, not a floor" → "…is a
  distribution".
- Removed the "[0.60,0.96] floor fails at both ends" comparison and "the
  inherited reading survives intact"; report the model's own min/median/
  max directly.
- Removed "This ordering is precisely the inherited paper's own
  qualitative picture — it reported CF reaching 96% … 73% … 64%" and
  "What survives is the inherited '…' intuition; what fails is the
  categorical [0.60,0.96] bound" → positive read-off of the quadrant
  medians.
- "Decorrelation sensitivity: what independence actually bounds." +
  "The inherited paper argued (its §5.5) … this is the wrong quantity" +
  "the question the inherited §5.5 claim actually turned on" → "Decorrelation
  sensitivity." + positive variant-specific description.
- Removed "one more reason the categorical floor is the wrong summary".
- Table/figure captions: removed all `Rebuild/sims/...` reproduction
  paths, the `sha256 91fc4692…` hash, "the inherited paper reports
  CF ∈ [0.60,0.96]", "what replaces the inherited categorical-floor
  language", "where the inherited categorical floor breaks". Captions now
  describe content and parameters only.

**refs.bib**
- Stripped all provenance comments ("VDA-rebuild manuscript", `rb-NNN`/
  `RB-NNN`/`CR-NNN` ids, `Critique/…` and `Rebuild/…` paths, "reviewer",
  "research_db", `§model`/`§results`/`§appendix` cross-refs) → short
  content-only topic comments. All 20 real entries left intact.

## Grounding
No assertions added; all numbers, equations, and figures are unchanged
from the prior validated state. The scrub is content-preserving.

## Strength check
No finding was strengthened or weakened. Distributional/graded/conditional
character is intact; it is now stated as what the model does rather than
against an absent statement.

## Firewall sweep
Final grep over `main.tex`, all `sections/*.tex`, and `refs.bib` for the
full banned-vocabulary set (reconstruct/rebuild/synthesiz/original/
inherited/prior/previous/publish/critique/reviewer/verdict/ledger/TRACE/
provenance/defensible/restate/sharpen/"rather than asserting"/"categorical
floor"/Rebuild·Critique·research_db paths/SY·rb·RB·CR ids/sha256/version
tags) returns **zero hits**. Firewall clean.

## Gaps
G-001 (attention-to-d′ mapping figure) remains open; its placeholder was
made terse but the gap is unchanged. No gaps opened or closed.

## Compile
`pdflatex ×2 + bibtex` (plus a third pass for refs): all exit 0, **10
pages**, 0 undefined references, 0 undefined citations, 0 bibtex warnings.

## Next increment
SY-004: Results §4.2–4.3 — asymmetry shapes allocation; VDA non-monotonic
in r, with the closed-form threshold r†(v). Needs figures vda_curves_vfamily
and r_dagger_vs_v staged under Rebuild/. Write in clean venue voice from
the start (the scrub set the standard). A coherence pass (SY-005) should
follow once §4.2–4.3 land, re-running the firewall sweep.

## Drift watch
None. Numbers untouched; nothing checked against the strength ceiling
changed.
