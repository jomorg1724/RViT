# VDA16 cross-attention manuscript integration

This bundle adds one descriptive VDA16 cell to the VDA evidence series using the
same matched trial-bank psychometrics, native/PCA-128 decoders, graded key-logit
clamps, and source-resolved attention analysis used by the current VDA pipelines.

## Result boundary

- Checkpoint: iteration 19,999, SHA-256 `b40d9aa49ec28c352d7a790de84f5902e1a307f7b2abe5fe68dc9e6aabb4f84d`
- Architecture: cross-attention, d_mem=128, memory decay=1.0, 4×4/16 tokens
- Training status: **competence_gated**
- Final theta: 65.0 degrees
- Late-50 rolling correctness: 0.774
- At displayed validity .75 and the nearest sampled change to 18 degrees:
  valid=0.653, forced-invalid=0.133,
  difference=+0.520

The current repository extract does not contain the global VDA manuscript source
expected by `tests/test_vda_build_manifest.py`. The LaTeX fragment and PDF/SVG/PNG
figures in this bundle are therefore manuscript-ready, but have not been inserted
into an absent global source tree. The canonical M3 registry consequently remains
blocked for VDA16, and the descriptive task-sequence panel omits VDA2 because no
compatible modern matched-width VDA2 shard exists.

## Required caveats

This is a single seed and a single cross-attention/d128/no-decay checkpoint.
VDA16 affine, d256, decay contrasts, and seed-level uncertainty are unavailable.
The historical VDA1/VDA4/VDA9 comparison is descriptive because task geometry and
token count change together. Historical and VDA16 cells also come from separately
frozen executable/runtime lineages. Cross-method intervention effects are not
compared at nominal clamp dose; equal logit biases do not imply equal achieved
attention mass. Because training remained at theta=65.0
degrees, mechanistic outputs are competence-gated and should be described as an
easiest-condition diagnostic.
