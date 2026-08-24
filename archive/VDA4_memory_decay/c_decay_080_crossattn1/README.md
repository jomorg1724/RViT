# VDA4 cross-attention with leaky xLSTM cell memory

## Question

Can sensory-to-memory cross-attention preserve task-critical representations when the xLSTM's stored cell content is forced to decay rapidly?

## Registered manipulation

The shared engine's `SpatialXLSTM` receives `memory_decay=0.80`. Only carried cell content is leaked:

```text
C_t = 0.80 * (F_t * C_{t-1}) + I_t * U_t
```

The current write `I_t * U_t` is not immediately attenuated. `N_t`, `M_t`, and the gate equations are unchanged. This placement lets `crossattn1` read prior `H` through its memory keys/values and potentially rewrite important content into `C_t`.

## Fixed configuration

- Task: VDA4, original 2x2 stimulus geometry and 50x50 image
- Sensory/memory tokens: 4
- Feedback: `crossattn1` (one xLSTM; sensory queries, concatenated sensory+memory keys/values)
- Cell: xLSTM, `d_mem=128`
- Front-end: shared SE-ResNet convolutional encoder
- JEPA coefficient: 0.5
- Curriculum: enabled, theta starts at 65 degrees
- Seed: 0
- Training horizon: 20,000 global iterations, 8 episodes per iteration
- Device: MPS
- Initialization: fresh random weights

## Interpretation boundary

Training success establishes competence under forced memory leak. It does not by itself prove that cross-attention preserves representations. That claim requires comparison with the matched `memory_decay=1.0` cross-attention control and attention/memory interventions or decoding tied to the task-relevant delay.

## Launch

```bash
./VDA4_memory_decay/c_decay_080_crossattn1/launch_20k.sh
```

The launcher creates a unique checkpoint directory under `battery_sweep_results/memory_decay/` and prints it before training.
