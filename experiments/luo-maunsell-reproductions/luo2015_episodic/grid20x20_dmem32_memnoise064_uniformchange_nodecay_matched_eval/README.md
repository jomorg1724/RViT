# Neutral calibration: mnemonic-noise SD 0.64 with uniform signed changes

This fresh seed-0 run halves mnemonic-noise SD from `1.28` to `0.64` and corrects the Luo changed-trial distribution. For every trial the environment samples one signed orientation offset:

```text
Delta theta ~ Uniform(-theta, +theta)
```

A changed first test uses `sample + Delta theta`; an unchanged first test repeats the sample, and its second test uses `sample + Delta theta`. Thus, at `theta=65`, changed-trial absolute magnitudes span continuously from 0 to 65 degrees instead of always equaling 65 degrees. Rendering still adds independent approximately 5-degree Gaussian orientation jitter and pixel noise.

Held constant: unchanged 50x50 Luo scene, 20x20 recurrent grid, `d_mem=32`, retention `1.0`, independent per-memory-scalar noise at each update, xLSTM, `crossattn1`, JEPA coefficient `0.5`, seed 0, and neutral rewards. This is a fresh 20,000-iteration calibration; no criterion or sensitivity children launch automatically.
