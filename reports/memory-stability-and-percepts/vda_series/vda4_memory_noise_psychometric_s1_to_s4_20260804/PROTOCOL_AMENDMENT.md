# Frozen diagnostic protocol: fully expressed S1 cue with forced S4 change

Frozen before any result from this magnitude sweep was computed or inspected.
Date: 2026-08-04.

## Question

For native VDA4, how does the probability of a correctly timed change report
vary with orientation-change magnitude when the displayed cue is fully
expressed at S1 but the physical change is forced at the uncued S4 location?
Compare the historical no-noise VDA4 with the interrupted memory-noise model
operating with independent Gaussian memory-slot noise of standard deviation
0.5.

`displayed_validity=1.0` means a fully expressed S1 cue in the environment. A
forced S4 change is therefore an **out-of-distribution invalid probe**; it is not
a genuinely 100%-valid cue-target trial. This distinction must appear in every
figure and summary.

## Evidence boundary

This is a post-interruption held-out behavioral diagnostic, not the registered
terminal paired pilot. The noisy weights stop at iteration 15,999, while the
historical clean reference is terminal at iteration 19,999; initialization,
training duration, and training provenance are not paired. The primary two-
curve contrast also changes both training-time and evaluation-time noise. It
therefore describes these two checkpoint conditions but cannot isolate learned
adaptation from the acute effect of injected evaluation noise or establish a
population-level effect.

## Frozen checkpoints and operating conditions

| curve label | training noise SD | evaluation noise SD | saved iteration | SHA-256 |
|---|---:|---:|---:|---|
| historical clean | 0.0 | 0.0 | 19999 | `ea671f9758551e06b39ef19c06e85e888ce3ee74dda8a534c1532251a69ee4ca` |
| interrupted noisy | 0.5 | 0.5 | 15999 | `be5e67f907e6603229c48ee54cc41e7075d62a4514f61f0f9da0d2e56d1de967` |

Both must load as schema-3 native VDA4, 2x2/four-patch, `crossattn1`, one xLSTM,
`d_mem=128`, `memory_decay=1`, seven logical frames, fresh seed-0 architecture.
Their state-dictionary keys and tensor shapes must match exactly.

## Frozen psychometric bank

- Cue location: S1/top-left (`cue_index=0`).
- Displayed cue proportion/validity parameter: `1.0`.
- Forced changed location: S4/bottom-right (`change_index=3`).
- Change onset: logical frame `t5`.
- Magnitudes in degrees: `0, 3, 6, 9, 12, 15, 18, 22, 26, 30`.
- Trials per magnitude and checkpoint: `300`.
- Cue color: red.
- Sensory seed: `2608044101`, reused at every magnitude so the base stimulus
  bank is common across magnitudes.
- Policy-uniform seed: `2608044102`, producing one fixed `300 x 7` bank reused
  across magnitudes and checkpoints.
- Mnemonic standard-normal seed: `2608044103`, producing one fixed independent
  trial-by-slot-by-coordinate schedule reused across magnitudes for the noisy
  operating condition. The clean condition injects no mnemonic noise.
- A disjoint no-change bank uses sensory seed `2608044201`, policy seed
  `2608044202`, and mnemonic seed `2608044203` for false-alarm, d-prime, and
  criterion summaries. It does not add a third plotted curve.

All actions are sampled from the model policy using the external common uniform
bank. No argmax-policy substitution is allowed.

## Behavioral endpoint

The response time is the first sampled action-1 frame. A change trial is scored
as detected only when the first press is at `t5` or `t6`. First presses at
`t0..t4` are early responses and do not count as detections; no press is a miss.
For the no-change bank, any first press is a false alarm, matching the frozen
paired evaluator.

The plotted point is the empirical detection probability at each magnitude.
Each point receives a two-sided 95% Wilson binomial confidence interval. Points
are connected only to guide the eye; no sigmoid or monotonic fit is imposed.
The monotone-envelope 50% threshold is reported only if the empirical range
brackets 0.5. Hautus-corrected d-prime and criterion are retained in the tables
but are not substituted for the requested two psychometric curves.

## Required outputs

1. One plot with exactly the two requested response-probability curves and
   Wilson intervals on common axes.
2. Trial-level presses and action probabilities, per-magnitude counts/rates,
   confidence intervals, early-response counts, mean qualifying response time,
   false alarms, d-prime, and criterion.
3. Exact trial-bank, runtime-noise, checkpoint, producer, and file hashes.
4. A manifest independently revalidated after generation.

