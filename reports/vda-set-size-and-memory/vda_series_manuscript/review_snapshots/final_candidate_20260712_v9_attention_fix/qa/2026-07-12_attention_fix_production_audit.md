# Corrected first-wave attention production audit

Date: 2026-07-12

Verdict: **PASS**

## Immutable production identity

- Root: `/Users/jonathanmorgan/AttentionManuscriptArtifacts/vda_first_wave_attention_isolated_production_20260712`
- Manifest: `MANIFEST.json`
- Manifest SHA-256: `c58a864ae3e6776bf7d64af719180d298ab1cd9615558c59f29ddd2168c45706`
- Schema version: 4
- Regular-file inventory: 77
- Manifest artifact records: 60
- Validated deterministic caches: 8
- Realized attention trials per cue proportion: 96
- Realized psychometric trials per point: 300

The completed tree passed the builder's independent `--reuse-validated-cache` read-only audit without rewriting any byte.

## Attention semantics

All four attention caches passed strict validation:

- displayed cue proportions: `[0.25, 0.50, 0.75, 1.00]`;
- `change_present = false`;
- `change_index = -1`;
- physical change magnitude: 0 degrees;
- fixed cue index: 0 (S1/top-left);
- nominal event timestep: `t5`;
- seven logical timesteps;
- finite reduced maps;
- checkpoint and producer dependency hashes bound to retained source bytes.

Raw/reduced tensor shapes were:

- VDA4 affine: `(4, 96, 7, 4, 4)` → `(4, 7, 1, 4)`;
- VDA4 cross-attention: `(4, 96, 7, 4, 8)` → `(4, 7, 2, 4)`;
- VDA9 affine: `(4, 96, 7, 9, 9)` → `(4, 7, 1, 9)`;
- VDA9 cross-attention: `(4, 96, 7, 9, 18)` → `(4, 7, 2, 9)`.

Cross-attention image keys and recurrent-memory keys remain separate source arrays. Query patches are averaged only after source separation.

## Publication projection

Twenty-four PDF/JSON products and the production manifest were copied byte-for-byte into `reports/vda_series/figures/first_wave/`. All copied hashes were verified against the production root. The approved environment and psychometric PDFs changed only in embedded PDF metadata: independently rasterized 150-dpi pages were pixel-identical to their predecessors for all six panels.

Visual inspection of all six production attention panels found no clipping, overlap, missing cue marker, source conflation, or mislabeled event.
