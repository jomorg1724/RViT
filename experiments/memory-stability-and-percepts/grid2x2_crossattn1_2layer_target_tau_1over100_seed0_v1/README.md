# VDA4 two-layer transformer memory: actor/critic target tau ÷100

This is a fresh seed-0 retraining of the two-layer transformer-memory architecture. All trunk, actor, critic, and JEPA parameters start fresh and are trainable.

The sole intended intervention relative to the original from-scratch contract is the PAC actor-and-critic target-network Polyak coefficient:

```text
previous: tau = 0.005      (EMA decay = 0.995)
new:      tau = 0.00005    (EMA decay = 0.99995)
```

The trainer implements `target <- decay*target + (1-decay)*online`, so `--ema-decay 0.99995` gives `tau=0.00005`, exactly 1/100 of the previous magnitude.

This does not alter MPO temperature or any JEPA temperature/EMA setting. The actor bias, entropy coefficient, dual JEPA losses, VDA4 task, curriculum, and all architecture routing remain matched to the original from-scratch run.

Local CUDA only; no RunPod.
