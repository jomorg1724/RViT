# VDA4 element-wise affine feedback with leaky xLSTM cell memory

## Question

Can the element-wise affine priority-routing variant remain competent on VDA4 when stored xLSTM cell content is forced to decay at the same 0.80 rate used in the prior cross-attention experiment?

## Registered architecture and manipulation

The shared engine uses `feedback=affine_ew`. Prior recurrent output modulates each current sensory token before ordinary spatial self-attention:

```text
b = tanh(B * H_{t-1})
gamma = G_gamma(b)
beta = G_beta(b)
X' = gamma * X + beta
A = softmax(Q(X') * K(X')^T / sqrt(d))
Z = X + A * V(X')
```

The scale and shift are element-wise vectors. `gamma` is initialized to one and `beta` to zero, so the attention block begins as ordinary sensory self-attention. Unlike `crossattn1`, this variant has four spatial keys and no separate recurrent-memory key/value bank; memory influences routing through `gamma` and `beta`.

The shared engine's `SpatialXLSTM` receives `memory_decay=0.80`. Only carried cell content is leaked:

```text
C_t = 0.80 * (F_t * C_{t-1}) + I_t * U_t
```

The current write `I_t * U_t` is not immediately attenuated. `N_t`, `M_t`, and all gate equations are unchanged.

## Matched configuration

This project matches `VDA4_memory_decay/c_decay_080_crossattn1` except for the registered routing family.

- Task: VDA4, original 2x2 stimulus geometry and 50x50 image
- Sensory/memory tokens: 4
- Feedback: `affine_ew` element-wise affine modulation followed by 4x4 spatial self-attention
- Cell: one xLSTM, `d_mem=128`, carried-cell retention `0.80`
- Front-end: shared SE-ResNet convolutional encoder
- JEPA coefficient: 0.5
- Curriculum: enabled, theta starts at 65 degrees
- Seed: 0
- Training horizon: 20,000 global iterations, 8 episodes per iteration
- Schedule endpoint: global iteration 19,999
- Checkpoint cadence: every 50 iterations plus final
- Device: MPS
- Initialization: fresh random weights
- Resume fidelity: schema-v3 replay-excluded trainer state

## Interpretation boundary

A successful run establishes competence of the affine-routing architecture under forced carried-cell leakage. It does not isolate a causal decay effect by itself. The primary matched comparisons are:

1. this `affine_ew`, decay-0.80 run versus the completed standard `affine_ew`, decay-1.00-equivalent run; and
2. this run versus the matched `crossattn1`, decay-0.80 run.

Because the two routing families expose different attention topologies (4x4 spatial maps for `affine_ew`, 4x8 sensory-plus-memory maps for `crossattn1`), later analysis must compare shared spatial/temporal estimands rather than treating raw columns as interchangeable.

## Output contract

Each production launch creates a unique directory under `battery_sweep_results/memory_decay/` named with the task, routing, decay, memory width, checkpoint fidelity, seed, UTC timestamp, and random suffix. It writes:

- `metrics.csv` on every completed iteration;
- `rvit_plus_rl_latest.pt` every 50 iterations and at completion; and
- `rvit_paper_vda4_final.pt` at completion.

`launch_20k.sh` is retained as the hash-bound internal launch specification. Operator handoffs should use the literal expanded Python command, not the wrapper path.
