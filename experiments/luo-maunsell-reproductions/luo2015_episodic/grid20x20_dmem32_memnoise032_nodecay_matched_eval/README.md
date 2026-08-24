# Neutral calibration: mnemonic-noise SD 0.32

This fresh seed-0 neutral calibration doubles mnemonic-noise SD from `0.16` to `0.32`. The `0.16` run was stopped at iteration 725 with 95.5% rolling correctness and 95.875% mean correctness over its final 100 rollouts while the uniform change bound was 62 degrees.

All other contracts remain matched: unchanged 50x50 Luo scene, 20x20 recurrent grid, `d_mem=32`, retention `1.0`, independent noise for every memory scalar at each recurrent update, xLSTM, `crossattn1`, JEPA coefficient `0.5`, and 5-degree sensory orientation jitter.

Changed-trial offsets remain sampled from `Uniform(-theta, +theta)`. Only the neutral parent runs; reward-manipulation children remain withheld until the neutral task is competent but non-ceiling.
