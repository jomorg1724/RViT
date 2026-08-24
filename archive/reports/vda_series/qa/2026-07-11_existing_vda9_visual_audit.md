# Existing VDA9 reproduction visual audit

Date: 2026-07-11

Audited artifacts:

- `RViT_plus_paper_jepa_grid9/repro9/paper9_affine_ew.pdf` (14 letter pages)
- `RViT_plus_paper_jepa_grid9/repro9/paper9_crossattn1.pdf` (14 letter pages)

Method: both PDFs were rendered at 100 dpi into full-page JPEGs and six-page contact sheets. Every rendered page was visually inspected. This is a baseline audit of preserved outputs; no legacy figure or PDF was modified.

## Verdict

Neither paper is publication quality. The PDFs establish substantial scientific coverage, but they fail the new VDA standard because the source plots were exported mostly at 130–150 dpi with labels as small as 6–9 pt before further manuscript scaling. Dense panels, confusion matrices, and legends are unreadable at final placement. The papers also treat the MAH source as an informal seventeen-block sequence rather than reproducing all 22 active main/supplement image objects one-for-one.

## Defects common to both variants

| Pages | Findings | Required correction |
|---|---|---|
| 1–3 | Text-heavy opening is set as a compact report rather than a polished computational-neuroscience article. The methods and results are compressed into short section summaries without the evidential and statistical detail needed to interpret the figures. | Rebuild from the series manuscript template with explicit evidence classes, sample/seed semantics, and source-figure mapping. |
| 4 | The task timeline and cue matrix have very small labels and values. Timeline frames and probability cells are too small to inspect at page size. The cue matrix repeats labels tightly and depends on pale green intensity. | Split M1 into a full-width timeline and a separately legible cue/realized-probability panel; use shared semantic colors, larger labels, and exact displayed-versus-realized validity captions. |
| 5 | The architecture figure occupies a narrow band with substantial unused whitespace, while labels inside boxes and arrows are too small. The psychometric/chronometric grid is also undersized. | Rebuild M2 as vector artwork sized to text width; place M3 on a dedicated full page or a landscape spread. |
| 6 | The parameter summary at the page top is extremely small. The attention-map array has dozens of tiny cells with unreadable annotations. The scalar time courses are compressed below it. | Separate fit summaries from M4. Use row/column headers, a shared colorbar, fewer repeated labels, and a second panel for scalar trajectories. |
| 7 | Three distinct scientific figures are stacked on one page. Curves, legends, clamp labels, and captions are too small; the top architecture fragment is not a faithful one-to-one MAH supplementary figure. | Give M5 and each comparator its own source-mapped figure. Rebuild intervention curves from paired deterministic data with visible uncertainty and baselines. |
| 8–9 | Confusion matrices are too small to read; class labels, cell values, and colorbar ticks disappear at manuscript size. Multiple matrices use large amounts of white margin while still compressing the data panels. | Use normalized rates plus support counts, shared color scales, larger cell text, and landscape or multi-page grouping. |
| 10–11 | Actor-logit scatter grids are dominated by whitespace and tiny axes. Colorbars and condition labels are unreadable; curves/points collapse into nearly indistinguishable bands. | Use larger panels, shared axes, high-alpha density design or hexbin where appropriate, and redundant shape/line encodings. |
| 12 | Value/TD panels are more legible than adjacent figures but still use small legends and thin lines. The criterion/entropy panel is compressed into the lower half of the page. | Separate S15 and related diagnostics, increase final-size text and line weight, and state sample/uncertainty semantics. |
| 13 | Criterion and sensitivity panels are readable only at zoom. Multiple conditions depend on similar line colors with no robust grayscale distinction. Legends are small and repeated. | Use the project palette plus unique marker/dash combinations, reserve external legend space, and report intervals and paired effects. |
| 14 | The supervised-versus-RL figure is structurally incomplete: the left two-thirds consists of repeated “supervised not available” placeholders while the only quantitative RL plots are stacked in a narrow right column. The page is mostly blank and the resulting plots are tiny. | Do not present this as a completed source reproduction. Keep S17 explicitly pending until matched supervised models exist, or redesign as a transparent availability figure outside the empirical figure sequence. |

## Variant-specific notes

### Affine element-wise multiplicative paper

- Curves in the behavior and intervention panels often use several related green/cyan traces that become difficult to distinguish.
- Attention heatmaps contain visibly different dynamic ranges across panel groups but do not make the comparability rule visually obvious.
- The causal-manipulation and SDT pages rely on legends too small to resolve at final size.

### Cross-attention paper

- The same layout and typography failures persist.
- Several actor-logit panels become visually overplotted, with colored points following nearly identical trajectories; the color encoding carries little additional readable information.
- The criterion/sensitivity figure uses multiple subdued colors that are especially difficult to distinguish without marker/dash redundancy.
- High-token cross-routing clamp results are subject to the known legacy analysis defect and cannot be treated as scientifically valid merely because the plots render.

## Overlap and clipping

No catastrophic body-text collision or page-edge clipping was visible in the rendered contact sheets. That limited pass does not rescue the papers: legibility, source coverage, uncertainty reporting, color distinction, figure scale, and evidential validity all fail. Full-resolution page review remains mandatory after each rebuild.

## Disposition

The existing PDFs remain preserved historical artifacts and should be labeled **partial**, not complete. Their scientific content can guide the new producers, but their raster outputs and manuscript layouts must not be promoted into the final VDA series. The new series will regenerate cached data where producer semantics are valid, rebuild all figures as vector PDF plus at least 300-dpi PNG, and repeat rendered-page inspection after compilation.
