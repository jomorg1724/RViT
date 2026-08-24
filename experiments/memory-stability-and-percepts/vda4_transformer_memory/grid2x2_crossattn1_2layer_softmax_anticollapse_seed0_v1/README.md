# VDA4 two-layer softmax memory with JEPA collapse prevention

This fresh local experiment adds an explicit per-token softmax activation to both transformer memories and strengthens the fixed-EMA JEPA objective against collapse.

## Memory activation

For every patch token, softmax is applied over the 128 memory features:

```text
raw H1 -> softmax(dim=d_mem) -> H1 -> memory 2, next-step vision feedback, H1 JEPA
raw H2 -> softmax(dim=d_mem) -> H2 -> actor, critic, recurrence, H2 JEPA
```

Learned H1/H2 initial states are treated as logits and softmaxed before the first timestep. The older `transformer_memory_2layer` selector remains unchanged for reproducibility; this variant is `transformer_memory_2layer_softmax`.

The EMA teacher is a copy of the same architecture, so its H1/H2 states obey the same simplex geometry. Softmax activation does not detach gradients.

## JEPA collapse prevention

The existing detached teacher, valid-step centering, temperature sharpening, and independent H1/H2 heads remain. This experiment adds:

1. Three-iteration Sinkhorn-Knopp teacher assignment balancing, independently per memory layer, token, and structured head.
2. A variance floor on the student's pre-prototype projection features (`coef=1.0`, target standard deviation `1.0`).
3. Off-diagonal covariance decorrelation on those features (`coef=0.01`).

The JEPA teacher EMA remains fixed at `0.996`; there is no rising EMA schedule.

Local CUDA only; no RunPod.
