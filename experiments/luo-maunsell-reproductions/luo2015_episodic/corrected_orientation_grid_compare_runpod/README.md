# Corrected Luo initial-orientation experiment: 20×20 versus 2×2 token grids

This pair retrains the previous neutral Luo–Maunsell mechanistic extension from random initialization after correcting the trial generator.

## Corrected task contract

Each trial independently samples both sample orientations from the full axial domain:

```text
sample[0], sample[3] iid ~ Uniform[0°, 180°)
signed change Δ ~ Uniform(-theta, +theta)
```

`theta` is only the signed-change bound. Curriculum can decrement `theta` by 3° toward the inherited 18° implementation floor; it never changes the initial-orientation distribution.

## Comparison

Only model tokenization changes:

- dense condition: `20×20 = 400` visual/recurrent tokens;
- coarse condition: `2×2 = 4` visual/recurrent tokens.

Both use seed 0, 20,000 iterations, the 50×50 seven-frame scene, xLSTM `crossattn1`, `d_mem=32`, retention coefficient 1.0, independent per-memory-scalar noise SD 0.64, sensory jitter SD 5°, JEPA coefficient 0.5, eight episodes per iteration, sampled actions, and neutral rewards.

This is not capacity matched. Token count changes recurrent-state count, positional width, flattened readout width, and parameter count. Interpret it as a whole-tokenization comparison.

No criterion or sensitivity child launches automatically. Each neutral parent must first demonstrate matched fresh-episode competence with non-ceiling sensitivity/criterion headroom.
