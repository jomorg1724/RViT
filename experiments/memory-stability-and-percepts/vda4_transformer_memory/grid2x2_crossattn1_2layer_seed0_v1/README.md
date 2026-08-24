# VDA4 two-layer transformer memory — local seed 0

At physical time `t`:

1. The established visual `crossattn1` block uses `Q=X_t`, joint `K/V=[X_t,H1_{t-1}]`, and an `X_t` residual to produce `Z_t`.
2. Memory layer 1 uses `Q=H1_{t-1}`, joint `K/V=[H1_{t-1},Z_t]`, and an `H1_{t-1}` residual to produce `H1_t`.
3. Memory layer 2 uses `Q=H2_{t-1}`, joint `K/V=[H2_{t-1},H1_t]`, and an `H2_{t-1}` residual to produce `H2_t`.
4. `H1_t` supplies visual feedback on the next physical step. Actor and QR critic read only `H2_t`.
5. Separate structured JEPA heads and DINO centers supervise `H1` and `H2`; each student at `t` predicts its corresponding EMA-teacher level at `t+1`. The training JEPA scalar is the mean of the two level losses. Center updates average valid episode steps only and exclude padded tails.

Both memory levels start from independent learned, slot-distinct tokens to prevent permutation-symmetric collapse. This is a fresh local VDA4 competence experiment, not a continuation of the failed single-layer run.

## Launch

```bash
RUN_ROOT='C:/Users/jomor/Documents/RViT_runs/vda4_transformer_memory_2layer_maskedcenter_seed0_local_v1_production_20260809' \
  bash experiments/vda4_transformer_memory/grid2x2_crossattn1_2layer_seed0_v1/launch_local_v1.sh
```

Override `ITERS`, `SAVE_EVERY`, or `DEVICE` only for an engineering canary. The launcher refuses pre-existing run directories and snapshots hashes and the exact command.
