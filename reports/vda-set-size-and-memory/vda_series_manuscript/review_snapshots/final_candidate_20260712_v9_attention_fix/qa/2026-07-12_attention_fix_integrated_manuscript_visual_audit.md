# Attention-correction integrated manuscript visual audit

Date: 2026-07-12

Verdict: **PASS**

## Candidate identity

- Source: `reports/vda_series/manuscript/main.tex`
- Source SHA-256: `41fe5f860a61cdb41e63e4f2f26a2658b9bd0aa26b1e2f0ac53d9afd319c3509`
- PDF: `reports/vda_series/manuscript/main.pdf`
- PDF SHA-256: `25e1fec1152b55eab6c2e80e1dc8cb2b52f5a64d151d3911157020c2f7468c41`
- PDF bytes: 2,958,680
- Page count: 56
- Ordered rendered-page-set SHA-256 (digest over the ordered `sha256sum rendered/page-*.png` output): `8badab34b89757bf68f45ef1c6ff99fab6bbfcfb75fee1c8e3190e5e1e45d306`
- Corrected first-wave production manifest SHA-256: `c58a864ae3e6776bf7d64af719180d298ab1cd9615558c59f29ddd2168c45706`

## Procedure

1. Compiled the candidate with three successful XeLaTeX passes.
2. Scanned `main.log` for overfull boxes, undefined references, missing glyphs, and TeX errors; none were present.
3. Rasterized the exact PDF to 56 canonical 150-dpi pages named `rendered/page-01.png` through `rendered/page-56.png`.
4. Inspected contact sheets covering every rendered page for blanks, clipping, overlap, missing figures, margin overflow, and unreadable placement.
5. Inspected pages 20--25 at enlarged final-placement scale. These pages contain the corrected VDA4 and VDA9 attention figures.
6. Compared the newly generated environment and psychometric PDFs against their approved predecessors after rasterization at 150 dpi; all six comparisons were pixel-identical.

## Corrected attention-page findings

Pages 20--25 each show four explicit cue-proportion rows (25%, 50%, 75%, and 100%) and seven logical-timestep columns (`t0` through `t6`). The `t5` heading explicitly identifies the nominal change opportunity and states that no change occurred. The red outline remains fixed at the top-left/S1 cue location in every cell.

The VDA4 and VDA9 cross-attention results are split into dedicated landscape image-key and recurrent-memory-key panels. Each companion pair uses a common zero-to-observed-maximum scale, and the source titles, row labels, timestep labels, colorbars, footers, and captions remain readable at their compiled manuscript size. No panel is clipped or overlapped.

All attention captions state that the evidence is checkpoint-recomputed, descriptive, based on 96 matched no-change trials per displayed cue proportion, and averaged over query patches. No physical change is claimed at `t5`.

## Whole-document finding

All 56 pages of the exact hash-bound PDF passed rendered-page QA. No blank page, clipped object, overlapping float, missing figure, margin overflow, or unreadable corrected attention placement was found.
