# M2 architecture-figure visual audit

Date: 2026-07-11

## Artifact set

- `reports/vda_series/figures/architecture/m2_architecture.pdf`
- `reports/vda_series/figures/architecture/m2_architecture.svg`
- `reports/vda_series/figures/architecture/m2_architecture.png`
- `reports/vda_series/figures/architecture/m2_architecture.json`

The PDF is the publication vector artifact, the SVG preserves editable/searchable text, the PNG is the inspection raster, and the JSON contains the source-object mapping, admitted architecture specifications, source hashes, and claim boundary.

## Scientific scope

M2 is a deterministic model-specification diagram. It does not contain checkpoint measurements, learned parameters, behavioral outcomes, or biological evidence. The figure covers:

- M2a: RGB input and task-resolved patch tokenization;
- M2b: the admitted `affine_ew` and `crossattn1` routing operators without conflating them;
- M2c: the shared spatial xLSTM update and recurrent feedback path; and
- M2d: flattening followed by separate actor and distributional QR-critic heads, with the JEPA auxiliary branch labeled training-only.

## Inspection record

The 220-dpi full-page raster was inspected twice. The second inspection followed a revision that replaced a disconnected pair of recurrent-feedback arrows in panel C with one directed curved path from `H_t` back to routing at `t+1`.

| Check | Result | Evidence |
|---|---|---|
| Panel labels and titles | Pass | A–D are distinct, aligned, and readable. |
| Text clipping | Pass | No title, equation, box label, note, or footer is clipped. |
| Box and arrow overlap | Pass | Arrows terminate at intended modules and do not obscure equations. |
| Recurrent directionality | Pass after revision | Panel C now shows one unambiguous `H_t` → next-step routing feedback path. |
| Affine routing semantics | Pass | Panel B separates `gamma` and `beta`, applies `X' = gamma ⊙ X + beta`, and labels identity initialization. |
| Cross-attention semantics | Pass | Panel D shows image-derived queries, concatenated image/memory keys and values, `N × 2N` attention, and the shared downstream xLSTM. |
| Readout semantics | Pass | Patch structure is retained through routing/memory and flattened only before actor/critic readout. |
| Claim boundary | Pass | Title/footer and metadata explicitly identify a source-derived specification rather than a model result. |
| Accessibility | Pass | Meaning is carried by text and arrow topology, not color alone; fills are pale and borders/text retain high contrast. |
| Vector/raster export | Pass | PDF, SVG, and PNG were regenerated together after the revision. |

## Verdict

**Approved for manuscript placement as a specification figure.** Coverage remains `partial`, rather than `complete`, until the new manuscript actually includes and captions the figure.
