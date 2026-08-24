# Sample-phase spatial attention in the noisy-memory Luo task

## Executive result

Suppressing the future-tested sample region produced 0 discordant correctness outcomes among n=704 paired trials (observed Δ accuracy +0.000). Because the ordinary paired bootstrap is degenerate when every observed pair agrees, we report the conservative two-sided 95% no-discordance bound |Δ accuracy| < 0.0052 under IID trial-pair sampling.

The manipulation reduced mean attention mass at the future-tested quadrant during the two sample frames from 0.2342 to 0.0011. This is a successful routing manipulation, but the behavioral estimate comes from one frozen mid-training checkpoint and does not quantify training-seed uncertainty.

## Frozen model and protocol

- Checkpoint iteration: `12899`
- Checkpoint SHA-256: `2c4a6d2d21bd9698387f7a4b27cbc242c7f3bb097868518deb7790ae1c8b339f`
- Model grid: `20×20`
- Sensory orientation noise: `5.0°`
- Mnemonic noise SD: `0.64`
- Training change sampler: `Uniform(−35.0°, +35.0°)`
- Map aggregation: `64` noisy repetitions per identical latent condition
- Psychometric grid: `64` changed trials per magnitude; `128` shared no-change trials
- Policy actions were sampled; sensory and recurrent-memory noise were enabled.

## Intervention results

| Condition | Correct / total | Accuracy | Sample-region mass | Paired Δ; conservative bound | Hit rate at 18° | d′ at 18° | Mean hit frame at 18° |
|---|---:|---:|---:|---:|---:|---:|---:|
| Natural | 476 / 704 | 0.676 | 0.2342 | reference | 0.984 | 3.443 | 3.254 |
| Inhibit future-tested sample | 476 / 704 | 0.676 | 0.0011 | +0.000; |Δ|<0.0052 | 0.984 | 3.443 | 3.254 |
| Inhibit other active sample | 476 / 704 | 0.676 | 0.0012 | +0.000; |Δ|<0.0052 | 0.984 | 3.443 | 3.254 |
| Inhibit blank control | 476 / 704 | 0.676 | 0.0009 | +0.000; |Δ|<0.0052 | 0.984 | 3.443 | 3.254 |

## Phase-resolved routing

At first-test onset `t3`, combined incoming tested-minus-other mass was -0.0615 at L0 (95% CI [-0.0615, -0.0615]) and -0.0608 at L3. Among changed-trial survivors reaching `t4`, recurrent-memory tested-minus-other routing became positive: +0.0331 at L0 (n=8) and +0.0256 at L3 (n=11). At guaranteed test 2, the location-specific contrasts reversed sign (+0.0519 at L0, -0.0517 at L3), so there is no location-general same-site return.

## Psychometric and chronometric shape

The controlled curve was non-monotonic: natural hit rate/d′ peaked at 18° (0.984/3.443) and fell to 0.547/1.565 at 35°. All intervention hit-rate and d′ points were identical. Tested-sample inhibition shifted mean hit time by -0.018 frame at 12° without changing correctness.

## Specific trial

The rendered example was a no-change first test at location 0 followed by the guaranteed +18° second test. The sampled first declaration occurred at `t6`, producing `correct_rejection`.

- Declare probabilities: `[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]`
- Sampled actions: `[0, 0, 0, 0, 0, 0, 1]` (`0=wait`, `1=declare`)
- GIF: `reports\luo2015_scientific_assay_20260803_production\trial\specific_trial_all_frames.gif`

## Evidence boundaries

- The finite −6 logit bias is strong soft suppression, not hard exclusion; 0.48% of natural target-region mass remained.
- The task has no cue. Both sample Gabors are simultaneously relevant; the lesion uses oracle knowledge of the future test location.
- Attention maps are normalized routing weights, not orientation-content decoding.
- Fixed-magnitude curves are controlled slices within the training support; they are not the training distribution itself.
- Post-decision map frames are survivor-filtered. Changed trials do not contribute after the first-test window.
- Confidence intervals reflect repeated noisy evaluation trials from one checkpoint, not independent training runs.
- The biological comparison target is Luo and Maunsell (2015) V4; this assay is a computational abstraction, not a neural replication.
