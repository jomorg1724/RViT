# Neutral calibration: mnemonic-noise SD 0.16

This fresh seed-0 neutral calibration doubles mnemonic-noise SD from `0.08` to `0.16`. The `0.08` run was stopped after reaching 100% rolling correctness while the change bound was 56 degrees.

All other model and task settings remain matched: unchanged 50x50 Luo scene, 20x20 recurrent token grid, `d_mem=32`, retention `1.0`, independent elementwise mnemonic noise at every recurrent update, xLSTM, `crossattn1`, JEPA coefficient `0.5`, and 5-degree sensory orientation jitter.

The changed-trial orientation offset is sampled independently each episode from `Uniform(-theta, +theta)`. Theta is therefore a bound, not a fixed change magnitude. The curriculum starts with theta 65 and can lower the bound to 18 as online performance increases.

Only the neutral parent is launched. Criterion and sensitivity children remain withheld until performance is competent but sufficiently below ceiling to leave measurable headroom for reward-dependent changes in `d'` and criterion.
