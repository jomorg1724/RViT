# VDA16 affine element-wise manuscript integration

This bundle adds one descriptive VDA16 cell to the VDA evidence series using the
same matched trial-bank psychometrics, native/PCA-128 decoders, graded key-logit
clamps, and source-resolved attention analysis used by the current VDA pipelines.

## Result boundary

- Checkpoint: iteration 19,999, SHA-256 `52141da629e2c7f8f902826196067efbadb924608eecde7560559fdc0f813233`
- Architecture: affine element-wise, d_mem=128, memory decay=1.0, 4×4/16 tokens
- Training status: **competence_gated**
- Final theta: 47.0 degrees
- Late-50 rolling correctness: 0.845
- At displayed validity .75 and the nearest sampled change to 18 degrees:
  valid=0.893, forced-invalid=0.480,
  difference=+0.413

The bundle is intended for the VDA Set Size manuscript. The descriptive
task-sequence panel omits VDA2 because no compatible modern matched-width VDA2
shard exists.

## Required caveats

This is a single seed and a single affine element-wise/d128/no-decay checkpoint.
VDA16 d256, decay contrasts, and seed-level uncertainty are unavailable.
The historical VDA1/VDA4/VDA9 comparison is descriptive because task geometry and
token count change together. Historical and VDA16 cells also come from separately
frozen executable/runtime lineages. Cross-method intervention effects are not
compared at nominal clamp dose; equal logit biases do not imply equal achieved
attention mass. Because training remained at theta=47.0
degrees, mechanistic outputs are competence-gated and should be described as an
easiest-condition diagnostic.
