# Fresh gamma-1.0 reward matrix at mnemonic noise 0.1066667

This controlled follow-up repeats all four completed gamma-0.8 counterphased cells with `gamma` changed from `0.8` to `1.0`. Mnemonic-noise SD remains `0.10666666666666666`; sensory jitter remains `5°`; task, architecture, optimizer, replay, reward tables/scales, seed, and iteration budget are unchanged.

Each cell starts from fresh seed-0 weights. This is not a resume or warm start.

## Preregistered hypotheses

1. **Temporal-discount hypothesis:** removing discounting should reduce the manipulated-location sensitivity false-alarm collapse and produce positive d-prime.
2. **Reward-magnitude-invariance hypothesis:** gamma 1 may make the learned sensitivity policy insensitive to absolute reward magnitude. This predicts competent behavior but little or no counterphased sensitivity d-prime difference.

The hypotheses will be separated with matched frozen-policy trials: always-declare behavior falsifies successful sensitivity learning, while competent but equal condition/control d-prime supports reward-magnitude invariance.
