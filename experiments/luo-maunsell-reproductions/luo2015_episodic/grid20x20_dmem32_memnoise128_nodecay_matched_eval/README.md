# Neutral calibration: mnemonic-noise SD 1.28

This fresh seed-0 neutral calibration doubles mnemonic-noise SD from `0.64` to `1.28`. The `0.64` run was stopped at iteration 1427 after rolling correctness had already climbed to 91.25% at the initial 65-degree uniform change bound, indicating that it was trending toward the same high-performance regime as lower-noise runs.

All other contracts remain matched: unchanged 50x50 Luo scene, 20x20 recurrent grid, `d_mem=32`, retention `1.0`, independent noise for every memory scalar at each recurrent update, xLSTM, `crossattn1`, JEPA coefficient `0.5`, and 5-degree sensory orientation jitter.

Changed-trial offsets remain sampled from `Uniform(-theta, +theta)`. Only the neutral parent runs; reward-manipulation children remain withheld until the neutral task is competent but non-ceiling.
