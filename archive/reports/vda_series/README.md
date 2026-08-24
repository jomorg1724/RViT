# VDA figure-reproduction series

This series asks whether each value-directed-attention (VDA) environment reproduces the complete empirical and mechanistic figure logic of Morgan, Albanna, and Herman (2025), including the bundled supplement. Each environment receives its own data products, figures, manuscript, and visual-quality record; results are never borrowed across environments.

## Scope

The canonical source is arXiv:2502.10955v1, archived locally as:

- `source_material/mah/2502.10955v1.pdf`
- `source_material/mah/2502.10955v1-source.tar`
- `source_material/mah/source_v1/main.tex`
- `source_material/mah/source_v1/supplement/supplement.tex`

The source contains five active main-text image objects and seventeen active supplementary image objects. The reproduction target is therefore 22 source-figure objects, not merely the informal seventeen-block sequence used by older VDA9 reports. A source figure may be scientifically undefined for a particular environment—for example, change-location decoding at set size one—but it may not silently disappear. The corresponding manuscript must explain the estimand and why it is undefined.

## Environment families

### Preserved varying-geometry lineage

- `vda1`: one active item on a 2×2, four-token support; validity is degenerate.
- `vda2`: two active items on a 2×2, four-token support; exact displayed validity.
- `vda4`: four active items on a 2×2 support; archived runs use realized validity p+(1-p)/4.
- `vda9`: nine active items on a 3×3, nine-token support; archived runs use realized validity p+(1-p)/9.
- `vda16`: sixteen active items on a 4×4 support; preserved historical training is partial/incomplete, its stop reason is unknown, and it cannot be treated as a completed endpoint.
- `vda_excl`: a distractor-exclusion experiment. It is part of the broader VDA task family but requires a distinct translation of source panels.

### Controlled fixed-geometry lineage

- `vda_fixed1`, `vda_fixed2`, `vda_fixed4`, `vda_fixed9`, `vda_fixed16` all use a 4×4 geometry, 100×100 RGB observations, and sixteen model tokens. Only the number of active items changes.
- `vda_fixed1` is a declared validity degeneracy.
- `vda_fixed2`, `vda_fixed4`, `vda_fixed9`, and `vda_fixed16` implement exact displayed validity by excluding the cue from invalid-target sampling.

The historical and controlled lineages must never be pooled as if they were equivalent replications.

## Evidence classes

Every quantitative statement and caption must label its evidential source:

1. **Regenerated:** recomputed deterministically from a hashed checkpoint by a recorded command, with cached analysis output.
2. **Preserved artifact:** read from an immutable historical NPZ, CSV, log, or figure whose producer semantics have been audited.
3. **Reported:** transcribed from a manuscript or prior report but not independently regenerated.
4. **Pending:** required by the figure matrix but not yet supported by a suitable checkpoint or corrected producer.
5. **Undefined:** the scientific estimand does not exist in that environment; the reason is stated explicitly.

A fixed-checkpoint evaluation batch estimates trial/evaluation uncertainty, not independent training uncertainty. A single seed is provisional. Logged completion is not evidence of convergence.

## Required deliverables per environment

Each environment directory will contain:

- `manifest.json`: task semantics, checkpoint hash, architecture, seed, device, producer hashes, and source-figure mapping.
- `data/`: deterministic cached NPZ/CSV outputs; no plotting dependency on Torch.
- `figures/`: paired vector PDF and high-resolution PNG outputs.
- `manuscript/`: one self-contained figure-reproduction paper with explicit main/supplement mapping.
- `qa/`: machine checks, page renders, contact sheets, and a human/vision inspection record.

The compute layer writes versioned data. A separate light plotting layer reads only cached data. Neither layer may overwrite preserved legacy artifacts.

## Current combined audit manuscript

The newly authored combined VDA-series manuscript is:

- source: `manuscript/main.tex`;
- compiled PDF: `manuscript/main.pdf`;
- reproducibility record: `manuscript/BUILD_MANIFEST.json`;
- final page audit: `qa/2026-07-11_final_manuscript_visual_audit.md`.

It is a provenance-first audit of the frozen archive, not a claim that every MAH analogue has been regenerated. M1 task schematics, M2 inspected-source architecture specifications, and eight M3 archived-aggregate behavior figures are placed in the manuscript. Unsupported M4/M5, decoder, intervention, and supplementary estimands retain explicit partial, available, blocked, undefined, or inapplicable dispositions in the exact 952-cell matrix. `reports/upgraded_paper/manuscript/main.pdf` belongs to an older rebuilt manuscript lineage and is not this deliverable.

## Scientific narrative

The prose follows the source paper’s argumentative sequence: task and model; behavior; intrinsic attention dynamics; causal intervention; alternative mechanisms; memory decoding; policy geometry; value and temporal-difference signals; signal-detection decomposition; and training-objective comparisons. Neuroscience supplies hypotheses and comparison standards, not proof of biological equivalence. Claims about FEF, superior colliculus, visual working memory, biased competition, criterion, or sensitivity must be stated as model–experiment correspondences with their limits.

## Quality gate

No VDA reproduction is complete until:

- all 22 source objects have a status and a rendered counterpart or an explicit undefined panel;
- every plotted value traces to a cached data field and producer version;
- fonts, markers, colors, and line styles remain legible at final manuscript size;
- color distinctions survive grayscale and common color-vision deficiencies;
- labels, legends, annotations, and panel letters do not overlap data or one another;
- every figure is exported as vector PDF and at least 300-dpi PNG;
- LaTeX builds with no undefined references/citations or overfull-box defects;
- every rendered PDF page is visually inspected at full resolution and as a contact sheet.

See `STYLE_AND_QA_STANDARD.md` and `FIGURE_COVERAGE_MATRIX.md`.
