# Neutral calibration: mnemonic-noise SD 0.64

This fresh seed-0 neutral calibration doubles mnemonic-noise SD from `0.32` to `0.64`. The `0.32` run was stopped after reaching the 18-degree uniform change bound while retaining approximately 97–98% rolling correctness.

All other contracts remain matched: unchanged 50x50 Luo scene, 20x20 recurrent grid, `d_mem=32`, retention `1.0`, independent noise for every memory scalar at each recurrent update, xLSTM, `crossattn1`, JEPA coefficient `0.5`, and 5-degree sensory orientation jitter.

Changed-trial offsets remain sampled from `Uniform(-theta, +theta)`. Only the neutral parent runs; reward-manipulation children remain withheld until the neutral task is competent but non-ceiling.
