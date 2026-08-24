# Final prose-lint disposition

Date: 12 July 2026
Source: `reports/vda_series/manuscript/main.tex`
Source SHA-256: `bf5643cc1226f501ea71f2a4d8433e4495d22113a80cd7d1866fb05495d97df8`
Linter: `scientific-writing-four-lenses/scripts/prose_lint.py`
Raw result: **40 review triggers; exit 1**
Disposition: **PASS after manual review; no unreviewed trigger remains**

## Review method

The linter is intentionally a triage heuristic. Every trigger was read in source and classified by function. The final source had already undergone structural compression: detailed source accounting moved to Methods, eight repetitive historical plates moved behind one comparative body overview, coverage counts moved to an appendix, neuroscience became claim-led, and the conclusion was compressed to a direct resolution.

## Trigger classes

### Structured syntax or compact legends — 9

Lines 25, 66, 88, 91, 92, 337, 386, and 479 (two sentences).

These are a `\hypersetup` declaration, evidence tables, a state-dimension table, an equation, and the exact appendix legend. Their punctuation encodes fields, classes, or notation rather than overloaded narrative.

### Figure captions — 5

Lines 155, 185, 228, 258, and 464.

Each caption is deliberately self-contained because the figure may be read out of sequence. The sentences bind estimand, provenance class, undefined state, and inferential boundary. The rendered captions fit cleanly.

### Narrative scientific sentences retained after manual review — 13

Lines 77, 103, 105, 112, 205 (two sentences), 216, 350, 391, 419, 425, 427, and 430.

Each enumerates scientifically non-interchangeable alternatives, exact constituent values, or evidence boundaries. Splitting would either duplicate the governing subject or weaken the explicit contrast. None is a paragraph-length sentence, causal overclaim, jargon substitution, or reader-hostile compression.

### Technical methods and provenance inventories — 13

Lines 143, 147, 269, 347, 353, 374, 409, 439, 446 (three sentences), and 452 (two sentences).

These encode outcome partitions, architecture stages, immutable inventories, decoder class support and chance, intervention doses, anatomical exclusions, revision controls, v15 audit mechanics, and the 161-test/visual-QA gate. The listed fields are necessary for reconstruction and remain legible in the rendered manuscript.

## Additional checks

- No stale v14, 160-test, 52-page, or obsolete-hash reference remains in the active manuscript.
- The prose-lint output itself is persisted at `reports/vda_series/qa/2026-07-12_matched_width_final_prose_lint.txt`.
- Exact-final visual QA passed all 54 pages.

## Final disposition

All 40 triggers are reviewed exceptions. None requires a prose repair. The non-zero linter exit is retained as honest raw output and is not misreported as a machine-clean pass.
