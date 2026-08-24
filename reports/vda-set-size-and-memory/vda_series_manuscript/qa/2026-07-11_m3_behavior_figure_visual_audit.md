# M3 behavior-figure visual audit

Date: 2026-07-11

## Artifact set

Eight source-mapped historical M3 figure sets were generated under `reports/vda_series/figures/behavior/`:

- VDA1, VDA2, VDA4, and VDA9;
- `affine_ew` and `crossattn1` for each task;
- PDF, SVG, PNG, and JSON metadata per task/family;
- `m3_behavior_contact_sheet.png` for cross-product inspection.

Historical VDA16 was deliberately excluded because its archived iteration-599 arrays are degenerate (response and false-alarm rates equal to 1.0, with undefined thresholds). Controlled fixed-grid checkpoints were not substituted for unavailable results.

## Evidence class

These figures are **regenerated from the preserved aggregate `psych.npz` cache**, not recomputed from checkpoints. The JSON metadata records the NPZ checksum, the iteration reported by the cache, the current producer-script checksum with an explicit lineage caveat, and the absence of uncertainty and seed-level evidence. The NPZ's `uncued` arrays do not embed their evaluated spatial index and are therefore labeled ``archived uncued,'' not ``opposing.''

The cache contains aggregate point estimates only. Consequently, the figures do not report confidence intervals and cannot support claims about sampling uncertainty, seed reliability, convergence, or mechanism.

## Inspection record

The eight 220-dpi raster outputs were inspected together on a 1840×2280 contact sheet. The first inspection identified a footer/x-axis crowding defect. The plotting layout was revised to reserve a dedicated provenance-footer band, all eight outputs were regenerated, and the contact sheet was rebuilt and reinspected.

| Check | Result | Evidence |
|---|---|---|
| M3A–F mapping | Pass | Each admitted multi-item task has six source-mapped panels: change-response A–C and conditional response-frame D–F. |
| VDA1 undefined estimands | Pass | B, C, E, and F explicitly state that one active item provides no uncued active change location. |
| Curve and legend visibility | Pass after revision | Validity is encoded by color plus distinct markers; cued/archived-uncued location uses color plus circle/square markers. Longer provenance-safe labels initially caused title collisions; two-line titles resolved them on the second inspection. |
| Axis semantics | Pass | Response probability is bounded to [0,1]; timing is labeled as mean response frame conditional on a scored response, not physical reaction time. |
| Panel labels and titles | Pass | A–F are visible and consistent across all eight products. |
| Clipping and overlap | Pass after revision | No labels, legends, axes, or curves are clipped; the provenance footer no longer overlaps x-axis labels. |
| Evidence boundary | Pass | Every figure states that it was regenerated from preserved aggregates, with no checkpoint rerun or uncertainty estimates. |
| Historical VDA16 exclusion | Pass | No degenerate iteration-599 curve was presented as an admitted behavioral result. |
| Accessibility | Pass | Line identity does not depend on color alone; pale backgrounds and dark text preserve contrast. |

## Verdict

**Approved for manuscript placement as regenerated historical aggregate evidence.** The eight admitted figures are included and independently captioned in the new manuscript. The lack of uncertainty, seed replication, spatial-index provenance, and embedded producer/checkpoint lineage remains visible in figures, captions, and prose.
