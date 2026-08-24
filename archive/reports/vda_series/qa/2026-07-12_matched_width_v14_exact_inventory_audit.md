# Matched-width v14 exact-inventory and provenance audit

Date: 2026-07-12

## Verdict

PASS for reconstruction, completed-tree integrity, delayed read-only audit, relative-root audit, publication identity, and visual standalone-evidence QA.

This verdict is a local engineering/provenance gate. The separate independent v14 scientific verdict remains a required release input.

## Production root

`reports/vda_series/matched_width_20260712_production_v14/`

- Fresh build required a nonexistent output root.
- Immediate builder audit: PASS.
- Delayed audit after 15 seconds: PASS.
- Delayed audit invoked with a relative output-root path: PASS; the builder normalizes the path before inventory comparison.
- Exact completed inventory: 11 regular single-link files, 0 symlinks, 0 special files, 0 hard-link aliases.
- Production manifest SHA-256: `0f5ceafff75fa43742b2ea9750235abd5cdae4570f1eabd39f041b0a5c7af4dd`.
- Bound post-build validation record SHA-256: `e6ca78e0325b7aba77179aeb24aa0decd9e4a4b6f118379b8875a98e95487949`.
- The validation record binds the rebuilt JSON and PDF/SVG/PNG identities and records PASS for upstream read-only audit, summary reconstruction, trial contract, decoder support, and checkpoint inventory.

## Reconstructed contracts

- Change occurrence: 900 samples, 450 per binary class, balanced-accuracy chance 0.5.
- Realized location: 450 change-present samples; VDA4 has four classes with counts 225/75/75/75 and chance 0.25; VDA9 has nine classes with 225 cued-location samples and 28–29 samples at each uncued location and chance 1/9.
- Cued versus uncued change location: 450 samples, 225 per binary class, chance 0.5.
- Singleton VDA1 location estimands are explicitly undefined.
- VDA2 is explicitly retained as blocked by the four-token d128 versus two-token d256 geometry mismatch.
- The JSON contains checkpoint identity, iteration, recurrent width, task geometry, active locations, and trainable parameter count for all 12 cells.
- “Matched width” is explicitly defined as a recurrent-width comparison within fixed task geometry and routing family, not total-parameter matching.
- Affine clamps target the cued image/self key; cross-attention clamps target the image key plus its corresponding memory key. Equal numeric biases are not asserted to be equal cross-routing doses or achieved-attention allocations.
- Warning localization is explicitly described as process-log-derived and non-hash-bound; native trajectories are omitted conservatively, and v14 does not claim a hash-bound no-warning ledger for the retained PCA fits.

## Production artifact hashes

- PDF: `2bf164ed9a02891face995d82a6bf032a0f31a07d8255afb9a820f3f909bad54`
- SVG: `9e47c1228cd9858580df931dd6258bd1b1aaa379ddec050ab7b9fb6384347422`
- PNG: `0c08f84fb57f9af677feb29b7975994bee1ed8fca1b663791269cd5bc9877b79`
- JSON: `15dadb9e2e290918e3dc2bb0af92d1170871eb8fedaea04796615f3bfda4fa5c`

The standalone PNG was visually inspected. Its three visible evidence-boundary lines are complete and readable; panel labels, axes, legend, competence annotation, and plotted products are not clipped or overlapping.

## Publication projection

`reports/vda_series/figures/matched_width/`

- The publication directory is explicitly classified as a non-self-contained projection of audited production v14.
- Local publication manifest: `PUBLICATION_MANIFEST.json`.
- Exact publication inventory: 7 regular single-link files, 0 symlinks, 0 special files, 0 hard-link aliases.
- The local manifest admits six artifacts plus itself: PDF, SVG, PNG, JSON, production-manifest snapshot, and the zero-byte regular `Icon\r` housekeeping sidecar.
- Every copied semantic artifact is byte-identical to production v14.
- Publication manifest SHA-256: `8d60721e6f940c70b4abb2e9b5663835afc53968c921808b80fe37034dc7d4af`.
- Production-manifest snapshot SHA-256: `0f5ceafff75fa43742b2ea9750235abd5cdae4570f1eabd39f041b0a5c7af4dd`.
- Manifested zero-byte sidecar SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

The projection is not claimed to contain the immutable shards, source graph, or checkpoints. Durable reconstruction and read-only re-audit depend on the absolute upstream battery named by production v14.
