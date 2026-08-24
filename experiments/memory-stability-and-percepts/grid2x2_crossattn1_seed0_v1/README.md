# VDA4 single-transformer memory — local seed-0 experiment

This experiment keeps the established native-2x2 VDA4 visual path and JEPA-style EMA teacher while replacing the recurrent xLSTM memory with one H-only transformer block.

At physical time `t`:

1. The standard `crossattn1` visual block computes `Z_t` with `Q=X_t` and joint `K/V=[X_t,H_{t-1}]`.
2. Memory starts from learned, slot-distinct `H_0` tokens, then computes `Q=H_{t-1}` and joint `K/V=[H_{t-1},Z_t]` under one softmax, followed by residual/LayerNorm/FFN transformer updates.
3. `H_t` feeds the actor, critic/value readout, the next visual-feedback step, and the temporal JEPA student/teacher heads.

The memory has no LSTM cell, gates, `C/N/M` states, explicit decay, or injected mnemonic noise in this first competence test.

Launch only on the local PC:

```bash
RUN_ROOT='C:/Users/jomor/Documents/RViT_runs/vda4_transformer_memory_seed0_local_v1' \
  bash experiments/vda4_transformer_memory/grid2x2_crossattn1_seed0_v1/launch_local_v1.sh
```

Override `ITERS=1 SAVE_EVERY=1` for an engineering canary. Canary output is plumbing evidence, not scientific evidence.
