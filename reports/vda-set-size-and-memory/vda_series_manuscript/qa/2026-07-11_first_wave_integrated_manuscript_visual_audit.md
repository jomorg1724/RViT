# First-wave integrated VDA-series manuscript visual audit

Date: 2026-07-11

## Verdict

**LOCAL PASS, pending independent manuscript integration and archive review.**

## Artifact

- PDF: `reports/vda_series/manuscript/main.pdf`
- Source: `reports/vda_series/manuscript/main.tex`
- PDF SHA-256: `a72a414f80c5950b439dca1a6a4de1bc1b1a9f5aadca69ffaf70a6fce9f13566`
- Final page count: 47 A4 pages, with portrait prose and rotated landscape figure/table pages
- Integrated production root: `/Users/jonathanmorgan/AttentionManuscriptArtifacts/vda_first_wave_production_20260712_approved`
- Production manifest SHA-256: `b627814dc19ba8dc11be8c2ac50c64b8b5f8fe9fb2fab9676d49dae3f2950677`

## Build and scientific gates

- Three successful XeLaTeX passes.
- Zero LaTeX errors.
- Zero overfull horizontal or vertical boxes.
- Zero undefined references or citations.
- Zero missing-glyph diagnostics.
- Integrated M1–M4 scientific gate: 148 passed.
- Final PDF rerendered to exactly 47 PNG pages at 144 dpi.
- The ten first-wave products were copied as byte-identical PDF snapshots with their JSON sidecars and production manifest.

## Inspection procedure

All 47 final pages were inspected in five complete-document contact sheets. Pages 24–39 were inspected again in four high-resolution four-page sheets. The final reader-guide page was independently rerendered at 180 dpi after the evidence-class table was updated. Inspection covered:

- clipping, collisions, overlap, and malformed rotation;
- blank, missing, duplicate, or caption-only pages;
- table headers, continuation markers, and orphan rows;
- figure labels, legends, axes, captions, uncertainty bands, and evidence-class text;
- VDA4 2×2 and VDA9 3×3 condition geometry;
- complete 4×7 and 9×7 attention layouts, fixed scales, event borders, and reduction disclosures;
- all three psychometric panels, n=300 labels, Wilson-interval disclosures, all-trial denominators, and forced-location language;
- PDF-to-native-product consistency and legibility after compact pairing.

## First-wave page verdicts

| Final PDF pages | Verdict | Scope |
|---:|---|---|
| 24 | Pass | Distinct checkpoint-recomputed evidence class; no retroactive aggregate-cache promotion. |
| 25 | Pass | Paired VDA4/VDA9 environment products; all occupied cells, S1/S4/S9 labels, borders, and captions are legible. |
| 26 | Pass | Attention semantics and causal boundary. |
| 27–28 | Pass | VDA4 affine and cross-attention; four query rows, seven logical timesteps, colorbars, borders, and captions intact. |
| 29–30 | Pass | VDA9 affine and cross-attention; complete 9×7 layouts remain readable and unclipped. |
| 31 | Pass | Psychometric estimand, denominator, intervention, and uncertainty prose. |
| 32 | Pass | Paired VDA4 affine/cross-attention psychometrics; panels, legends, bands, and captions intact. |
| 33 | Pass | Paired VDA9 affine/cross-attention psychometrics; lower cross-attention S9 response remains consistent between natural-invalid and forced-invalid panels. |
| 34–39 | Pass | Updated accounting, discussion, methods, conclusion, atlas, and table transitions. |

## Complete-document verdicts

| Pages | Verdict | Notes |
|---:|---|---|
| 1–10 | Pass | Title, abstract, reader guide, contents, task universe, M1, and architecture introduction are complete. |
| 11–20 | Pass | M2 and historical M3 figures are complete and correctly oriented. |
| 21–30 | Pass | Remaining M3 figures and first-wave condition/attention products are complete. |
| 31–40 | Pass | Psychometrics, findings, discussion, methods, atlas, object counts, and matrix start are complete. |
| 41–47 | Pass | Exact matrix continuations, artifact table, and references end normally without clipping or orphan rows. |

## Remaining approval boundary

This record establishes local rendered-page QA. It does not substitute for the requested independent manuscript integration, dependency, and archive review. Final manuscript approval remains pending that independent verdict.
