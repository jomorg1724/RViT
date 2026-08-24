# Sample-phase spatial attention in the noisy-memory Luo task

## Executive result

Suppressing the future-tested sample region changed pooled task accuracy by +0.000 (paired trial-bootstrap 95% interval [+0.000, +0.000]; n=44 paired trials).

The manipulation reduced mean attention mass at the future-tested quadrant during the two sample frames from 0.0048 to 0.0000. This is a successful routing manipulation, but the behavioral estimate comes from one frozen mid-training checkpoint and does not quantify training-seed uncertainty.

## Frozen model and protocol

- Checkpoint iteration: `12899`
- Checkpoint SHA-256: `2c4a6d2d21bd9698387f7a4b27cbc242c7f3bb097868518deb7790ae1c8b339f`
- Model grid: `20×20`
- Sensory orientation noise: `5.0°`
- Mnemonic noise SD: `0.64`
- Training change sampler: `Uniform(−35.0°, +35.0°)`
- Map aggregation: `2` noisy repetitions per identical latent condition
- Psychometric grid: `4` changed trials per magnitude; `8` shared no-change trials
- Policy actions were sampled; sensory and recurrent-memory noise were enabled.

## Intervention results

| Condition | Correct / total | Accuracy | Sample-region mass | Δ accuracy vs natural [95% CI] | Hit rate at 18° | d′ at 18° | Mean hit frame at 18° |
|---|---:|---:|---:|---:|---:|---:|---:|
| Natural | 28 / 44 | 0.636 | 0.0048 | reference | 1.000 | 2.875 | 3.000 |
| Inhibit future-tested sample | 28 / 44 | 0.636 | 0.0000 | +0.000 [+0.000, +0.000] | 1.000 | 2.875 | 3.000 |
| Inhibit other active sample | 28 / 44 | 0.636 | 0.0000 | +0.000 [+0.000, +0.000] | 1.000 | 2.875 | 3.000 |
| Inhibit blank control | 28 / 44 | 0.636 | 0.0000 | +0.000 [+0.000, +0.000] | 1.000 | 2.875 | 3.000 |

## Specific trial

The rendered example was a no-change first test at location 0 followed by the guaranteed +18° second test. The sampled first declaration occurred at `t6`, producing `correct_rejection`.

- Declare probabilities: `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]`
- Sampled actions: `[0, 0, 0, 0, 0, 0, 1]` (`0=wait`, `1=declare`)
- GIF: `reports\luo2015_scientific_assay_smoke_20260803\trial\specific_trial_all_frames.gif`

## Evidence boundaries

- The task has no cue. Both sample Gabors are simultaneously relevant; the lesion uses oracle knowledge of the future test location.
- Attention maps are normalized routing weights, not orientation-content decoding.
- Fixed-magnitude curves are controlled slices within the training support; they are not the training distribution itself.
- Post-decision map frames are survivor-filtered. Changed trials do not contribute after the first-test window.
- Confidence intervals reflect repeated noisy evaluation trials from one checkpoint, not independent training runs.
- The biological comparison target is Luo and Maunsell (2015) V4; this assay is a computational abstraction, not a neural replication.
