# Matched-width v15 exact-inventory and local validation audit

Date: 2026-07-12
Verdict axis: engineering/provenance
Verdict: **PASS**

## Production root

`reports/vda_series/matched_width_20260712_production_v15/`

- Built into a previously nonexistent root.
- Immediate builder audit: PASS.
- Delayed audit after 15 seconds: PASS.
- Delayed audit invoked through a relative output-root path: PASS.
- Exact inventory: 11 regular single-link files, 971,613 bytes; no symlinks, special files, or hard-link aliases.
- Manifest SHA-256: `3ded3023a0cd81a344487807e11d8a06fa46b7c29cf7f5f499ef5ac659ff5e24`.
- Bound post-build validation SHA-256: `72b730572d45a77a1430d091f6fa36e4029a7ebf148698e8d8beab3f38711214`.

## Figure and metadata identities

- PDF: `dafba8a4e721a02c56ef0e9703c1f555909aefbdc2fab238309b2018bc1a2628`
- SVG: `f7622adae3a63edfe39efeeca9dd061a4cc831eda7371c8532bea7425437feb3`
- PNG: `74d1c203452553e1af0b2c628075ba3750ee6f737ac06bc260db190b87944b7b`
- JSON: `15dadb9e2e290918e3dc2bb0af92d1170871eb8fedaea04796615f3bfda4fa5c`

The standalone PNG was inspected at full resolution. Panel B visibly states: “VDA1 location probes undefined: singleton task · chance N/A.” The annotation and VDA9 competence-gate annotation do not cover data, axes, labels, or each other. All three evidence-boundary lines remain visible and readable.

## Publication projection

`reports/vda_series/figures/matched_width/`

- Classification: non-self-contained publication projection of production v15.
- Exact inventory: 7 regular single-link files, 897,493 bytes; no symlinks, special files, or hard-link aliases.
- Every semantic publication asset is byte-identical to production v15.
- Local publication manifest SHA-256: `5433cdf26321b64b424304ed39fd5149e29cc259307a35b48568de13d58575f6`.
- The exact inventory includes the local manifest, PDF/SVG/PNG/JSON, production-manifest snapshot, and manifested zero-byte `Icon\r` housekeeping sidecar.

## Reconstructed contracts retained from v14 and verified by the v15 build

- change occurrence: 900 samples, 450/450, balanced-accuracy chance 0.5;
- VDA4 realized location: 450 change-present samples, counts 225/75/75/75, chance 0.25;
- VDA9 realized location: 450 change-present samples, 225 cued and 28–29 per uncued location, chance 1/9;
- cued versus uncued location: 450 samples, 225/225, chance 0.5;
- VDA1 location probes: undefined, effective n=0, chance N/A;
- VDA2: blocked by four-token d128 versus two-token d256 geometry mismatch;
- all 12 checkpoint identities, recurrent widths, token geometries, and reconstructed trainable parameter counts are retained in the JSON;
- affine and cross-attention clamps have distinct routing targets and are not calibrated as equivalent cross-routing doses;
- warning localization remains process-log-derived and non-hash-bound.

This local PASS does not replace the separate independent scientific artifact verdict. Active scientific limits remain separate-checkpoint training, no seed replication or paired intervals, competence gating, VDA2 geometry blocking, conservative warning exclusions, and non-equivalent routing interventions.
