# VDA4 spatial-discretization experiment: 10×10 patches

## Question

Does attention become more behaviorally important when a fixed visual scene is represented by more spatially compartmentalized sensory and memory units?

Working biological interpretation: as local spatial computations proliferate, attention may become increasingly necessary to integrate them into a coherent task-relevant signal.

## Manipulation

This experiment keeps the VDA4 task itself unchanged:

- four Gabor stimuli arranged in the original 2×2 VDA4 task geometry;
- the same 50×50 RGB image;
- the same cue, value, validity, timing, reward, noise, and curriculum semantics;
- the same element-wise affine feedback (`affine_ew`), xLSTM, convolutional front end, JEPA coefficient, memory width, optimizer/trainer configuration, seed, and 20,000-iteration horizon used by the matched VDA4 affine run.

Only the model's sensory discretization is overridden. The unchanged 50×50 image is divided into a 10×10 row-major grid of non-overlapping 5×5 patches. This produces 100 visual tokens and 100 corresponding xLSTM memory tokens rather than four of each.

## Architectural consequences and interpretation limits

The implementation follows the existing model's grid-dependent conventions. Therefore increasing the token count also has two unavoidable downstream consequences:

- the positional one-hot block grows from 4 to 100 dimensions, so token width grows from 140 to 236 (`128 visual + 100 position + 8 time`);
- the flattened recurrent readout grows from `4×128` to `100×128`, increasing the actor/critic input size.

The experiment is therefore a spatial-discretization scaling test, not a parameter-matched causal test of attention alone. A later control should match parameter count and/or pool the recurrent readout before attributing effects specifically to attention.

## Run

From anywhere in the workspace:

```bash
cd /Users/jonathanmorgan/AttentionManuscript/RViT_plus_paper_jepa_grid9 && ./experiments/vda4_spatial_discretization/grid_10x10/launch_20k.sh
```

Each launch creates a unique, non-overwriting run directory under `battery_sweep_results/spatial_discretization/`. Checkpoints use the replay-excluded trainer-state schema: model, optimizer, target network, JEPA teacher, environment/curriculum, rolling metrics, and RNG are persisted; replay is intentionally not persisted.
