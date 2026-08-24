# Standalone VDA4 cross-attention decay comparison

## Result

The hypothesis is **contradicted for this frozen checkpoint pair** under the prespecified activity metric. Mean frame-to-frame total variation was 0.5238 for the standard model and 0.4292 for the high-decay model. The paired high-minus-standard difference was -0.0945 (95% bootstrap CI -0.1167 to -0.0647; n=4 matched event trials).

“More active” is defined as greater frame-to-frame total variation over the complete 4-query × 8-key attention distribution. It is not defined as total attention mass because each query row is softmax-normalized to one. Selectivity, peak-key mass, image-versus-memory allocation, cue orienting, and change reorientation are reported as secondary descriptors.

## Important boundary

This is a **frozen-checkpoint comparison, not a decay-only causal estimate**. The standard model is complete at iteration 20,000; the high-decay snapshot was frozen at iteration 14,649 while its MPS trainer continued. The models differ in memory decay and training maturity. There is one training seed per model, so confidence intervals describe paired evaluation-trial uncertainty only.

The 100%-cue invalid condition is a deliberate forced intervention (cue S1, change S4), not a trial that the 100%-valid environment would naturally sample.

## Checkpoints

| role | iteration | resolved decay | frozen SHA-256 |
|---|---:|---:|---|
| standard crossattn1 | 20000 | 1.00 (legacy absent field resolves to default) | `a0cf23b788b1bb74ffb598fa3978b8d601b25ec5cfa2bf67d64d2d59bfd7d65a` |
| high-decay crossattn1 | 14649 | 0.80 | `da93490bfbcbf4969f9aedb06d94da2d3c9ef088435d7f390e952ca0aae59ab5` |

Both checkpoints validate as VDA4, xLSTM, `crossattn1`, `d_mem=128`, convolutional frontend, and 2×2/four-patch geometry. The standard final checkpoint has model tensors identical to its iteration-19,999 rolling checkpoint used by the prior VDA4 report.

## Event-locked findings (100% displayed cue, Δ=15°)

| measure | high minus standard | paired 95% CI |
|---|---:|---:|
| attention motion, valid | -0.0811 | [-0.1083, -0.0602] |
| attention motion, forced invalid | -0.1079 | [-0.1426, -0.0628] |
| selectivity | +0.0191 | [+0.0081, +0.0370] |
| peak-key mass | -0.0528 | [-0.0703, -0.0364] |
| image-key mass | -0.0414 | [-0.0429, -0.0394] |
| valid change reorientation, t5−t4 | +0.0012 | [-0.0865, +0.0678] |
| invalid change reorientation, t5−t4 | +0.0005 | [-0.0284, +0.0227] |

At the matched psychometric anchor (100% displayed cue, Δ=15°, 3 trials/point), standard response rates were 0.667 valid and 0.333 forced invalid; high-decay rates were 1.000 valid and 0.333 forced invalid.

## Design

- Event attention: 4 matched valid and forced-invalid trials, identical latent videos through t4, change at t5.
- No-change attention: 2 trials at 25%, 50%, 75%, and 100% displayed cue proportions.
- Psychometrics: 3 shared trials at each of 4 displayed cue proportions × 10 magnitudes × 2 change locations.
- Response: first argmax change action; a first press at frame 5 or 6 qualifies.
- Inference: deterministic paired bootstrap over evaluation trials (10,000 resamples). No training-seed inference is claimed.
- Execution: CPU only; the comparison did not use MPS.

## Figures

- `figures/attention_event_query_averaged.pdf`: direct standard/high-decay, valid/invalid, image/memory map comparison.
- `figures/attention_query_level_*.pdf`: query-preserving source maps; no query-axis collapse.
- `figures/attention_nochange_*.pdf`: cue-proportion attentional patterns without change events.
- `figures/attention_metrics_and_response_strata.pdf`: activity, selectivity, source allocation, cue/change location, and response-stratified traces.
- `figures/psychometric_valid_invalid_comparison.pdf`: valid/forced-invalid response curves and high-minus-standard heatmaps.

PNG and SVG versions accompany every PDF. Exact rates and estimates are in `tables/`; raw evidence is in `data/comparison_evidence.npz`; executable source snapshots and runtime metadata are in `provenance/`.
