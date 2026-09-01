# KDA conv-memory on Luo–Maunsell 2015 (sensitivity)

Wired, **not launched**. Same KDA architecture as the VDA16/motion runs; only the task, timeline, and RL heads differ.

## Environment (most recent Luo we were using)

`envs/luo2015.py` — faithful Luo & Maunsell 2015 analogue (not the 2018 LPFC variant, not the older cued `LuoMaunsellEnv`).

| | |
|---|---|
| Timeline | T=7: sample 0–1, blank delay 2, first-test window 3–4, gap 5, second test 6 |
| Stimuli | two simultaneous Gabors at logical **S1 (top-left, loc 0)** and **S4 (bottom-right, loc 3)**; **no visual cue** |
| Orientations | iid U[0°, 180°); signed Δ ~ U(−θ, θ); θ is a bound, not a privileged 18° |
| Report | action 1 = saccade-to-test; hits/FAs on the first test; CRs verified on a guaranteed-changed second test; second-test misses excluded from SDT |
| Sensitivity rewards | counterphased mean 5 vs 1 with H:CR ratios 0.7 / 1.1, selected by `--high-loc {0,3}` |
| Curriculum | shrinking θ 65° → 8°, −3° when ≥85% on a non-overlapping **1,000 valid-SDT-trial** window |

Last training campaign on this env (Aug-18) was the dual-stream RViT `d_mem=128` loc0/loc3 pair. This directory replaces that **agent**, not the MDP.

## Architecture

```
50×50 frame
  → conv stem (pools to 16×16)
  → KDA accumulator (4 heads × 16, C=64)
  → vision conv-attn   input [X_t ‖ acc_read]
  → H1/H2 memory conv-attn (update every step; H1 noise σ=0.05)
  → R = [H1 ‖ H2 ‖ Z ‖ att_vis]   # 4C = 256 channels
  → mean-pool R → FFActor + QRCritic
  → per-pixel JEPA on R (structured as P=256 tokens × 1 head)
```

Same backbone family as VDA16 KDA, **half the channel width** (C=64 vs VDA's 128). Other differences: 50×50 / 2×2 Luo mapping, T=7, PAC/QR heads instead of the change classifier, `mem_every=1`.

Objective hierarchy (wired, BC off): **critic 1.0 > actor 0.5 > JEPA 0.01**, teacher EMA fixed at 0.996.

## Layout

| file | |
|---|---|
| `kda_conv_memory_model.py` | backbone (copied from the VDA KDA bundle) |
| `kda_rl_model.py` | PPO interface + actor/critic |
| `paper_heads.py` | FFActor / QRCritic |
| `ppo.py` | PAC + QR-DQN + PER harness |
| `envs/luo2015.py` | the 2015 MDP |
| `train_rl.py` | Luo-only CLI; refuses criterion; requires `--curriculum` and `--high-loc` |
| `launch_luo_kda_sensitivity_loc0.sh` | frozen loc0 command |
| `launch_luo_kda_sensitivity_loc3.sh` | frozen loc3 command |
| `make_trials_gif_luo2015.py` | 20-trial stimulus GIF |
| `luo2015_trials.gif` | rendered GIF |

`--high-loc` is written to `checkpoint.training_args.high_loc` (0 or 3), matching the Luo identity contract.

## Not done (by design)

- No training, no pod, no canary.
- Neutral-parent noise calibration is still required before treating σ_mem=0.05 as Luo-calibrated (zero mnemonic noise solves this task trivially).
- Criterion cells are out of scope.

When you want to launch: one pod per `--high-loc`, same frozen source, verify `training_args.high_loc` on the first checkpoint.
