# Spatial attention measures manuscript QA — 2026-08-02

## Scope

This QA record covers the revised VDA4 attention comparison for native 2x2, 4x4, and 10x10 spatial discretizations. All models are compared on the same four physical image quadrants. The revision reports total quadrant mass, raw peak-patch mass, peak/uniform, peak-quadrant share, and within-quadrant focality, with frame 5, frame 6, and the frames 5--6 mean kept as distinct estimands.

The analysis treats attention as correlational localization evidence. It does not promote training metrics, checkpoints, GPU/process health, or attention weights into behavior, mechanism, causal, or scaling evidence.

## Reproducible artifacts

- Producer: `RViT_plus_paper_jepa_grid9/analysis/vda4_spatial_attention_measures.py`
  - SHA-256: `6408135de495a3f11f82cf1f5c866ad64c7f30cb3b39d190d784344680bfc3b9`
- Producer test: `RViT_plus_paper_jepa_grid9/tests/test_vda4_spatial_attention_measures.py`
  - SHA-256: `a30c616b9992a340985b94a8f7175e7a4e368c82fd4cf184aa208c57a91a4853`
- Analysis manifest: `RViT_plus_paper_jepa_grid9/reports/vda_series/spatial_scaling_attention_measures_20260802/MANIFEST.json`
  - SHA-256: `fd0d775d2727d04d37e090e72aeb8351e7be8352170c41488e5e36ed500424cb`
  - Independent verification: PASS, 39/39 producer, source-cache, table, figure, and manuscript-copy hashes matched.
- Manuscript source: `reports/vda_series/manuscript/main.tex`
  - SHA-256: `b8757d8086590908a3b7369364e1c3d32bfb9c237b272e69335beb19d79ee1ae`
- Canonical PDF: `reports/vda_series/manuscript/VDA_Set_Size.pdf`
  - SHA-256: `1c459464e3798d854561f7650e0bda17ae0cf6f03660cc3a4f26da7f260dbee9`
  - Size: 3,581,493 bytes
  - Pages: 35

## Automated verification

- `python -m pytest tests/test_vda4_spatial_scaling_evaluation.py tests/test_vda4_spatial_scaling_endpoint_replication.py tests/test_verify_vda4_spatial_scaling_endpoint_replication.py tests/test_vda4_spatial_attention_measures.py -q`
- Result: **26 passed** in 9.34 seconds.
- Compile-log scan: zero LaTeX errors, undefined references, overfull boxes, or missing-character warnings.
- Non-failing build notices were limited to underfull boxes and local Windows font reproducibility warnings.
- `main.pdf` and `VDA_Set_Size.pdf` have identical SHA-256 hashes.

## Visual QA

- Rendered all 35 PDF pages to PNG at 120 dpi.
- Inspected six contact sheets covering pages 1--35.
- Inspected the revised attention pages 7--13 and appendix pages 27--29, including the final enlarged cross-attention visual-key versus recurrent-memory-key decomposition on page 29.
- No clipping, overlap, blank/corrupt pages, illegible axis labels, or broken figure references were observed.
- Common-quadrant maps, native-patch maps, normalized metric plots, temporal comparisons, endpoint replication, and cross-attention source maps use explicitly labeled scales and captions.

## Interpretation correction

The former broad claim that localization weakens monotonically as token count increases was removed. Direction depends on metric, frame, attention family, and seed: raw peak mass contains a mechanical `1/N` baseline; affine peak-normalized localization can remain high while total quadrant mass falls; cross-attention target-versus-cue routing reverses between frames 5 and 6; and the seed-1 endpoint can reverse the seed-0 frame-5 direction. These are held separate from causal routing evidence.
