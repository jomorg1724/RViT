# Attention-fix v10 integrated manuscript visual audit

Date: 2026-07-12

Verdict: **PASS**

## Candidate identity

- Source SHA-256: `c5b5387e20ff76596af71b85b3925a9187dca1a3355ef75de1f15e85eb0d6078`
- PDF SHA-256: `a8342ea65da401418ab71152b43b6ed9cf1e2fd4363f0da660d663b95ab2b86f`
- PDF size: `2959199` bytes
- Physical pages: `56`
- Render set: `page-01.png` through `page-56.png`, 150 dpi
- Ordered render-set SHA-256: `32e943b22dc5a435604ee26566f61d54e5066fbbacb08927ad3b2ed910d7feea`
- Digest framing: for each ascending page, hash the UTF-8 line `<page_sha256>  rendered/<page_name>\n`; hash the concatenated lines with SHA-256.

## Review scope

- Inspected four contact sheets covering all 56 physical pages.
- Inspected physical pages 25–29 separately at enlarged scale after the psychometric protocol correction.
- Rechecked attention pages 20–25 for cue rows, seven timesteps, nominal no-change t5 labeling, fixed S1 markers, source separation, captions, and colorbars.
- Rechecked psychometric pages 26–28 for the fixed-location Panels A/B explanation, Panel C endpoint-replot disclosure, complete captions, and transition to Section 6.
- Scanned the final XeLaTeX log after three successful passes.

## Findings

- No blank page, accidental caption-only continuation, clipping, overlap, missing figure, broken header, or unreadable panel was found.
- The first v10 layout attempt produced a 57th caption-only page for Figure 19. That attempt was rejected. Reducing only the two VDA9 psychometric placements from `0.84\linewidth` to `0.80\linewidth` restored a complete 56-page layout with both Figure 19 and its caption on physical page 28.
- Corrected psychometric prose now states that Panels A and B fix the change location at every point and that Panel C re-plots their 100%-displayed endpoints rather than presenting independent or naturally sampled trials.
- Final XeLaTeX diagnostics contain no overfull box, undefined-reference, missing-glyph, or fatal-error signal.

## Disposition

The rendered 56-page v10 manuscript is visually admissible for fresh immutable review. This audit does not substitute for independent semantic or artifact approval.
