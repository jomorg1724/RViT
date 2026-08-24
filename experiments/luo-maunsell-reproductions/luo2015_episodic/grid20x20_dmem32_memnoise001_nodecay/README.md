# Luo–Maunsell 20×20 Token / No-Decay / Noisy-Memory Experiment

## Hypothesis

Attention maintains coherence in a distributed mnemonic representation. Small, independent perturbations to every recurrent-memory scalar progressively decohere an unattended representation; learned attention should preserve or reconstruct the task-relevant signal.

## Controlled changes

Relative to the existing Luo–Maunsell episodic task, this experiment changes only model-side representation and memory parameters:

- visual/model patch grid: `20×20` (`400` tokens)
- recurrent width: `d_mem=32` per token
- explicit memory retention: `1.0` (no explicit decay/leak term)
- mnemonic-noise SD: `0.01` in normalized xLSTM cell-state units
- feedback: `crossattn1`
- JEPA remains enabled with the matrix default coefficient `0.5`

The environment remains the original seven-frame, `50×50` Luo scene with the existing reward schedules, orientation pairs, orientation jitter (`5°`), curriculum, first test, inter-test gap, and guaranteed-changed second test. The launcher does **not** set `--luo-spatial-grid-size`.

## Tokenization

A `50×50` image is not evenly divisible by 20. `ConvPatchFrontEnd` uses rounded row/column boundaries, so patches have exact shapes `2×2`, `2×3`, `3×2`, or `3×3`. Every input pixel belongs to exactly one patch; the image is not padded, cropped, resized, or otherwise changed.

Each visual token has:

- 128 learned SE-ResNet features
- 400-way spatial one-hot code
- 8-way temporal one-hot code

Thus the model receives `400×536` perceptual tokens and maintains `400×32 = 12,800` recurrent-memory scalar values.

## Independent mnemonic noise

The xLSTM update samples noise with `torch.randn_like(C)`. Consequently, each `(batch, token, memory-dimension)` cell-state value receives its own independent standard-normal draw on every recurrent update. With `memory_noise_std=0.01`, the perturbation is scaled in the cell's normalized `C/N` units before being carried to the next step.

## Design and gating

The launcher runs seeds `0,1,2`. For each seed it first trains the unchanged neutral parent. The existing hard competence gate must pass before criterion/sensitivity children are launched. This prevents an untrained parent from producing uninterpretable SDT comparisons.

## Launch

From the repository root:

```bash
bash experiments/luo2015_episodic/grid20x20_dmem32_memnoise001_nodecay/launch_20k.sh
```

Override the accelerator or output path if necessary:

```bash
DEVICE=cuda RUN_ROOT=/workspace/rvit_runs/luo_grid20 \
  bash experiments/luo2015_episodic/grid20x20_dmem32_memnoise001_nodecay/launch_20k.sh
```
