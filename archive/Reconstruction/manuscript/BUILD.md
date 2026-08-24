# BUILD — Reconstruction manuscript

## Toolchain
Plain `pdflatex` + `bibtex` (TeX Live 2026; `latexmk` not in sandbox).
From `Reconstruction/manuscript/`:

```
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

(Two final `pdflatex` passes settle cross-references and the
bibliography.)

## Structure
`main.tex` is a thin skeleton that `\input`s section files in arc order:
abstract, intro, model, results, discussion, methods, supplementary.
The preamble defines the `\newcommand` notation block once. Bibliography:
`refs.bib`. Figures live in `figures/`.

## Dependencies
`article` class; `amsmath, amssymb, amsthm, mathtools, graphicx,
booktabs, xcolor, hyperref, geometry, lmodern`. No `cleveref`, no
`multirow` (not in TeX Live 2026basic — use plain `\ref{}` and
`\multicolumn`).

## Last build
- **SY-013 (2026-05-31):** Abstract written from the finished body
  (`sections/abstract.tex`; single unstructured paragraph, no citations,
  no meta; the four findings stated positively at ledger strength). Clean
  4-step build (`pdflatex` ×2 + `bibtex` + `pdflatex`), **33 pages**, 0
  undefined references, 0 undefined citations, 0 bibtex warnings, one
  pre-existing 3.0pt overfull `\hbox` (Supplementary). Firewall grep on
  `abstract.tex`: 0 hits. (Structure is now complete through abstract;
  remaining: SY-014 front/back-matter finalisation. Note: BUILD.md last
  build was previously recorded at SY-007/21 pages; the body, Methods,
  Supplementary, and abstract have since landed via SY-008…SY-013, all
  recorded in `SYNTHESIS_LOG.md`.)
- **SY-007 (2026-05-30):** Results subsection `sec:results-noninversion`
  (optimal allocation does not invert under predictive cues; closed-form
  value-weight inequality + inversion threshold $\rstarinv$ + symmetric-
  corner identity; counter-predictive inversion as new prediction)
  integrated; clean 3-pass build, **21 pages**, 0 undefined references,
  0 undefined citations, 0 overfull boxes. Three figures
  (`r_inv_closed_form`, `er_vs_alpha_anticue`, `alpha_star_V_r_map`)
  placed; firewall grep clean (0 hits); 0 new bib entries (all six
  behavioural keys pre-existing).
- **SY-006 (2026-05-30):** Results §4.3 (graded regime; iso-VDA contour
  band over $(\valid,\val)$; quantitative high-validity design guidance)
  integrated; clean 3-pass build, **17 pages**, 0 undefined references,
  0 undefined citations, 0 overfull boxes. Three C3 figures
  (`iso_vda_contours`, `vda_at_high_V`, `iso_vda_drho`) placed; firewall
  clean (0 hits across all `.tex`).
- **SY-005 (2026-05-30):** coherence pass over Intro + Model + Results
  §4.1--§4.2. Clean 3-pass build, **13 pages**, 0 undefined references, 0
  undefined citations, **0 overfull `\hbox`** (the single remaining one,
  54.7pt in Results §4.2, fixed). Standardised the standard-normal density
  glyph to $\varphi$ across Model and Results; identified the baseline
  discriminability $\dprime_b \equiv \dprime_{\mathrm{base}}$ with the
  Model symbol (removed a duplicate `:=` definition); brought the two
  Model cross-references to the supplementary section into "Supplementary
  material" wording (was "Appendix"); reworded two plot-curve mentions.
  No science changed; firewall clean.
- **SY-004 (2026-05-30):** Results §4.2 (VDA non-monotonic in $r$,
  closed-form escape threshold $\rdagger(\val)$) integrated; clean 3-pass
  build, **13 pages**, 0 undefined references, 0 undefined citations.
  Two C2 figures (`r_dagger_vs_v`, `vda_curves_vfamily`) placed; firewall
  clean. Known overfull `\hbox` in Model §2.4 still pending SY-005.
- **SY-015 (2026-05-30):** de-meta scrub; clean 4-step build, **10
  pages**, 0 undefined references, 0 undefined citations, 0 bibtex
  warnings. Content-preserving (no science changed); firewall clean.
- **SY-003 (2026-05-30):** clean 4-step build, **11 pages**, 0 undefined
  references, 0 multiply-defined labels, 0 citation warnings. Real
  content: `intro`, `model`, `results` §4.1. One pre-existing overfull
  `\hbox` (~52pt) in Model §2.4 (GH-64 quadrature sentence) — flagged for
  the SY-005 coherence pass. Three C1 figures
  (`cf_histogram`/`cf_heatmap`/`cf_curves`) now in `figures/`.
- **SY-002 (2026-05-30):** clean build, **7 pages**; Model integrated.
- **SY-001 (bootstrap, 2026-05-30):** clean build, **3 pages**;
  Introduction integrated, other body sections placeholders.
