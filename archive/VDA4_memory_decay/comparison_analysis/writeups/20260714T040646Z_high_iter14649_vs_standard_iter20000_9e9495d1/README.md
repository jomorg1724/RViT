# VDA4 memory-decay attention comparison

Final standalone LaTeX writeup comparing the frozen standard-decay checkpoint (decay 1.00, iteration 20,000) with the frozen high-decay checkpoint (decay 0.80, iteration 14,649).

## Deliverables

- `VDA4_memory_decay_attention_comparison.pdf` — final 12-page PDF.
- `main.tex` — editable LaTeX source.
- `figures/` — PDF, SVG, and PNG figures regenerated from the admitted evidence cache with extractable fonts.
- `provenance/` — summary, report, frozen-input and analysis manifests, evidence cache, tables, and producer source.
- `BUILD_COMMAND.txt` — exact two-pass XeLaTeX rebuild command.
- `FINAL_REVIEW_RECORD.json` — hash-bound independent-review verdicts.
- `PACKAGE_MANIFEST.json` — SHA-256 inventory of every other file in this package.

## Result and boundary

The standard checkpoint's mean frame-to-frame attention motion was 0.5245; the high-decay checkpoint's was 0.4249. The paired high-minus-standard difference was -0.0995 with a 95% evaluation-trial bootstrap interval of [-0.1021, -0.0970]. For this frozen pair, high decay was therefore associated with quieter—not more dynamic—attention under the prespecified total-variation metric.

This is not a causal estimate of decay. The high-decay checkpoint was frozen 5,351 iterations earlier, the checkpoints were trained independently, and there is one training seed per condition.

## Verification

- 13/13 analysis tests passed.
- XeLaTeX compiled twice with no warnings, missing glyphs, undefined references, or box overflows.
- A clean independent rebuild was byte-identical to the delivered PDF.
- All 12 physical pages were rendered and visually inspected.
- Analysis manifest, frozen checkpoints, cache, copied provenance, and extracted numerical text passed a fail-closed audit.
- All nine figure PDFs contain no Type-3 fonts; Unicode `λ` survives extraction.
- Independent reader-journey, numerical/statistical, and visual/accessibility reviews returned PASS with no must-fixes.

Final PDF SHA-256: `868b420a127a0907a3092546d442c62d4dd9bcee1cc97878794898d43a1a0683`
