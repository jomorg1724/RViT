# Frozen diagnostic protocol amendment: VDA4 memory-noise attention maps

Frozen before any attention result from the interrupted noise-0.5 checkpoint was
computed or inspected. Date: 2026-08-04.

## Scope and evidence boundary

This is a user-requested, post-interruption descriptive comparison. It is **not**
the registered terminal paired experiment: the noisy run was stopped early, the
clean reference is historical rather than a same-runtime mate, and neither
checkpoint may be represented as a replicated training-noise effect. The maps
may describe routing in these two frozen checkpoints on new held-out trials.
They do not establish behavior, causal mechanism, biological attention, or a
population-level effect.

## Frozen checkpoints

| label | training noise | evaluation noise | saved iteration | SHA-256 |
|---|---:|---:|---:|---|
| historical clean VDA4 | 0.0 | 0.0 | 19999 | `ea671f9758551e06b39ef19c06e85e888ce3ee74dda8a534c1532251a69ee4ca` |
| interrupted noisy VDA4 | 0.5 | 0.5 | 15999 | `be5e67f907e6603229c48ee54cc41e7075d62a4514f61f0f9da0d2e56d1de967` |

The noisy training metrics extend through iteration 16037, but the immutable
periodic checkpoint contains weights saved at iteration 15999. All displays use
the checkpoint iteration, not the later metrics row.

## Assay A: exact manuscript-style cue-proportion display

- Native VDA4, 2x2 carrier, four active patches, seven logical frames.
- No physical orientation change.
- Fixed red cue at top-left (S1).
- Displayed cue proportions: 0.25, 0.50, 0.75, and 1.00.
- 96 deterministic held-out trials per proportion.
- Sensory seed 1701 is reused across proportions, matching the established
  first-wave display convention; policy uniforms and the mnemonic standard-
  normal schedule are also held fixed across proportions.
- The clean checkpoint is evaluated with memory noise disabled. The noisy
  checkpoint is evaluated with independently drawn sigma=0.5 slot noise, using
  one deterministic standard-normal realization per trial, slot, coordinate,
  and recurrent update.

This assay isolates cue-proportion-dependent routing on no-change trials. It
cannot show true-change localization.

## Assay B: invalid-change exemplar

- Fixed cue at top-left (S1) and true change at bottom-right (S4).
- Displayed validity 0.75, orientation change 18 degrees, 96 held-out trials.
- New sensory, policy, and mnemonic streams are disjoint from Assay A and shared
  across the two checkpoint evaluations wherever the operation exists.
- This is an intuitive spatial exemplar, not a counterbalanced population map.

## Attention definition

For `crossattn1`, each frame returns a joint attention matrix
`A[4 current-image queries, 8 keys]`. Columns 0:4 are current-image keys and
columns 4:8 are previous-hidden-state keys. The sources are split **before** any
spatial reduction and are never fused in a primary display.

For source `s` and physical patch `j`, the displayed raw column score is

```text
p_s(j) = (1 / 4) * sum_i A_s[i, j]
```

Thus every 2x2 cell is the mean down one key column. Raw source shares are
retained; one common zero-to-maximum scale is used across clean/noisy and
current-image/previous-hidden-state panels. A source-conditional map, when
reported, must be paired with raw source share because conditional normalization
can conceal near-zero allocation to that source.

The native grid already has one patch per physical region, so a maximum within
region equals the region's single patch score and is not an independent measure.
The strongest individual query-to-key weight is a separate diagnostic and must
not be mislabeled as the column score.

## Planned outputs

1. Separate current-image-key and previous-hidden-state-key 2x2 maps for both
   checkpoints across all four cue proportions and all seven frames.
2. Separate invalid-exemplar maps across all seven frames, with cue and true
   target outlined independently.
3. Noisy-minus-clean difference maps computed separately by source.
4. Full trial-level 4x4 source matrices, column scores, source share, conditional
   allocation, maxima, entropy, and effective-location summaries in machine-
   readable artifacts.
5. Hash manifest binding checkpoints, producer, trial banks, arrays, tables, and
   figures.

