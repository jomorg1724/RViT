# VDA4 source-separated cross-attention and PDF QA - 2026-08-03

## Scope and correction

This pass restores the established VDA cross-attention display convention. Cross-attention visual-key and recurrent-memory-key blocks are split before query averaging and before any maximum is taken. Primary maps retain raw joint-softmax mass and share a common zero-to-observed-maximum scale across the two sources within each native grid. The co-located `V+M` sum remains only in explicitly labeled secondary paired-location diagnostics.

The common physical comparison partitions every native grid into the same `2 x 2` image regions. For each source and region it reports both the summed query-averaged key mass and the maximum query-averaged key mass. Source share and conditional localization measures are reported separately so that a low-mass source is not made artificially high-contrast by normalization.

These outputs are held-out routing-geometry evidence only. They are not behavior, causal mechanism, representation, or population-scaling evidence.

## Held-out source refresh

- Source refresh manifest: `RViT_plus_paper_jepa_grid9/reports/vda_series/spatial_scaling_crossattn_source_attention_20260803/MANIFEST.json`
- Manifest SHA-256: `b78e9f7134a27f18bdb4a463fc15127f2fcaa0f9da67c919a979b619217e380c`
- Five hash-matched terminal cross-attention checkpoints were replayed on the same 128 valid and 128 forced-invalid common-random-number event trials.
- Press arrays matched exactly for all five checkpoints.
- The sum of retained visual and memory source mass reconstructed the admitted paired-location cache with maximum absolute error from `7.017e-09` to `2.980e-08`.
- No training, psychometric evaluation, or causal intervention was rerun.

## Derived analysis bundle

- Bundle: `RViT_plus_paper_jepa_grid9/reports/vda_series/spatial_scaling_attention_measures_20260803_source_separated_v6/`
- Manifest SHA-256: `e8117f5e4b6e968508d9e9f3fc5346874d1f0cf23c5dd03af630bf83e42e7493`
- Outputs: 6,144 legacy paired-location/affine trial rows; 7,680 source-resolved trial rows; 864 legacy summaries; 1,500 source summaries; 12 metric definitions; 11 PDF/PNG figure pairs.
- The source-resolved figures include a six-row common-grid total/maximum plate, a frame-5 absolute-scale source decomposition, and separate `2 x 2`, `4 x 4`, and `10 x 10` source time courses from `t0` through `t6`.

## Automated checks

- `python -m py_compile analysis/vda4_spatial_attention_measures.py analysis/vda4_crossattn_source_attention_refresh.py`: passed.
- `python -m pytest tests/test_vda4_spatial_attention_measures.py tests/test_vda4_crossattn_source_attention_refresh.py -q`: `20 passed in 4.62s`.
- Tectonic: exit `0`.
- Log scan: no LaTeX errors, undefined control sequences, undefined references, fatal errors, emergency stops, or overfull boxes.
- PDF text extraction: confirmed the source split, pre-maximum separation, source-specific maps/maxima, non-normalized raw display, and `v6` provenance path.
- Stale-path scan: no active `v1` through `v5` derived-bundle paths or superseded manifest prefixes remained in `main.tex`.

## Final manuscript artifact

- Source: `main.tex`
- Source SHA-256: `ab0cb78b8b741243d839717b05f6938123994518db315cdc7184d40583c265ed`
- Build PDF: `main.pdf`
- Promoted PDF: `VDA_Set_Size.pdf`
- Final PDF SHA-256: `19afc721e8961e042072328a927521cb90b0f452378d380f5e92b02b97e79213`
- Final PDF bytes: `3,792,004`
- Page count: `41`
- Promotion: `main.pdf` and `VDA_Set_Size.pdf` are byte-identical by size and SHA-256.

## Visual QA

All 41 pages of the final build were rendered at 110 dpi into the unique directory:

`qa/source_separated_attention_render_20260803_v2/`

Six contact sheets covering pages 1-41 were inspected. Full-size inspection additionally covered the attention definitions and conclusions on pages 8-12; the source-specific common-grid plate on page 31; the absolute-scale source map on page 32; all three source-separated time-course plates on pages 33-35; and the final provenance tables on pages 40-41. The common-grid figure was regenerated with a portrait bounding box and wrapped column titles after QA detected an unreadably shrunken landscape version. The final PDF has no clipping, overlap, missing glyphs, corrupt figures, or unreadable revised labels.

The compiler retains non-fatal underfull-box warnings and local Windows Times-font portability warnings. Neither produced a visible defect in the rendered artifact.
