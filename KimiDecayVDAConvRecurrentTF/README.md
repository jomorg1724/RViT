# KimiDecayVDAConvRecurrentTF

KDA-style visual accumulator on the dual-state convolutional recurrent transformer,
sized for **VDA16** (4×4 grid, 16 Gabors, 100×100 px frames).

Self-contained bundle for a later RunPod upload — nothing has been run yet.

## Layout

| File | Role |
|---|---|
| `kda_conv_memory_model.py` | Model. `KDAConvMemoryModel` = conv stem → **visual accumulator** → vision conv-attn (X-side widened to 2C) → H1/H2 memory conv-attn → per-pixel JEPA head + mean-pool change classifier. `accum_mode` selects the accumulator: `ema` (in-flight baseline: static per-channel EMA), `gated` (dynamic 16×16×C decay field + decoupled write gate, vector state), `kda` (gated delta rule — per-pixel matrix state, error-corrected write, per-head-channel decay; Kimi Linear, arXiv:2510.26692). |
| `pretrain_kda_convmem.py` | Trainer. Same objectives/scheme as the motion-dmc conv-memory trainer: per-pixel temporal JEPA (EMA teacher, DINO centering, Sinkhorn) + change classifier on pool(R@last) with full BPTT + VICReg anti-collapse; theta curriculum; fresh-collection training; `--resume`. Default task `vda16`. |
| `smoke_test.py` | Shape/finiteness/gradient-flow check for all three accumulator modes. **Not a training run.** |
| `envs/`, `ppo.py`, `train_rl.py` | Copied verbatim from the live repo (`experiments/2026-08-26-convmem-motion-dmc/code`, Aug 28) for the JEPA loss utils, device/seed helpers, and the task registry. |

## Accumulator modes (ablation ladder)

1. `ema` — static per-channel decay d, write (1−d): the current run's baseline.
2. `gated` — α_t, β_t from 1×1 convs on [X_t‖H1]; bias-initialised so step 0 == the EMA.
3. `kda` — S ← Diag(α_t)·S + β_t·k·(v − S̃ᵀk)ᵀ per pixel; k,q L2-normalised; fp32 state
   math under AMP; `heads×head_dim == n_channels` (default 4×32 = 128).
   `‖v − S̃ᵀk‖` per pixel is an explicit surprise/change signal; per-step accumulator
   diagnostics (α/β means, error norm) are available via `forward_seq(..., return_stats=True)`.

## RunPod launch (kda pilot, seed 0)

`launch_kda_vda16_seed0.sh` is the frozen scientific contract: VDA16, T=7, change at
t=5, sensory noise 5.0, H1 memory noise σ=0.05, kda accumulator (4×32, init decay 0.5),
JEPA coef 1.0 + change coef 1.0, fixed teacher EMA 0.996, shrinking-theta curriculum
(65° → −3° when a 1024-trial collection's change accuracy > 0.85, floor 8°),
500K trials in 1024-trial fresh collections × 5 epochs, batch 64, lr 3e-4, AMP, seed 0.

```bash
python smoke_test.py                      # CPU, all modes (passed 2026-08-29)
bash launch_kda_vda16_seed0.sh            # full run; RUN_ROOT and DEVICE overridable
# GPU plumbing canary (NOT a scientific run):
python pretrain_kda_convmem.py --task vda16 --accum-mode kda --amp \
    --n-trials 1024 --epochs 1 --save-every 1 \
    --checkpoint-dir /workspace/runs/vda16_kda_c128_seed0_canary/checkpoints
```
