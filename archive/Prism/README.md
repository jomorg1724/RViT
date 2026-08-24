# PRISM — Predictive Recurrent Inference via Self-Modulation

A small (~250 K parameter), all-convolutional, recurrent visual-attention
architecture for cued change-detection and other temporal sensory environments.
The architecture's *only* auxiliary loss is variational free-energy /
predictive-coding error; its "interpretable attention map" is the per-location
prediction error itself, not a learned softmax.

**Status (May 2026):** PRISM v1 (this directory) is the best-performing model
on the cued change-detection task in this repo. The v2 follow-up
(`../PrismV2/`) explored hierarchical PC + slow/fast memory + multi-head
saliency + an action-value critic; despite multiple architectural iterations,
v2 has not yet matched v1's performance. v1 remains the reference model.

Full architecture writeup, math, and references: `docs/THESIS.md`.
Companion docs in `docs/`: `PRISM_V2_PROPOSAL.md`, `PROJECT_PLAN.md`,
`PRISM_V2/Q_CRITIC.md`.

## Layout

```
Prism/
├── README.md                  this file
├── env.py                     ChangeDetectionEnv (the Posner-cuing task)
├── stem.py                    V1 stem (bottom-up perceptual encoder)
├── film.py                    FiLM modulation (top-down gain pathway)
├── decoder.py                 Generative decoder + saliency map (PC error)
├── memory.py                  Error-gated ConvGRU + inner WM loop (K-step VFE)
├── readout.py                 Decision projection + actor / critic heads
├── losses.py                  L_PC + optional L_slow
├── model.py                   PrismModel (wires everything together)
├── ppo.py                     Recurrent PPO with truncated BPTT + joint PC
├── train.py                   Main entry point
├── config/prism_config.json   Default hyperparameters
├── checkpoints/               Saved model weights
├── docs/                      THESIS.md, PRISM_V2_PROPOSAL.md, PROJECT_PLAN.md
└── tests/                     Shape, identity, and smoke tests
```

## Quick start

Run the unit + smoke tests (a few seconds total):

```bash
cd /path/to/AttentionManuscript/Prism
python3 tests/test_shapes.py
python3 tests/test_inner_wm.py
python3 tests/test_pred_error.py
python3 tests/test_ppo_smoke.py
```

Train with the default config:

```bash
python3 train.py
```

Override config or seed:

```bash
python3 train.py --config config/prism_config.json --seed 42
```

## What the model does at each env step

```
x_t  ─► V1 stem ─► V_t                                            (bottom-up)
                  │
        M_{t-1} ─► FiLM(γ,β) ─► P_t                               (top-down gain)
              │
              └─► decoder g ──► V̂_t                               (top-down prediction)
                                │
                  E_t = V_t − V̂_t                                 (prediction error)
                  S_t = ‖E_t‖_c                                    (interpretable map ◄─)
                                │
                  error-gated ConvGRU update of M                  (write-where-surprised)
                                │
                  K-step variational inference on M                (free-energy descent)
                                │
                  decision pool → actor / critic                   (PPO)
```

The only aux loss is `L_PC = ‖V_t − g(M_{t-1})‖²`. This is the variational
free-energy *accuracy* term. It is bitter-lesson compliant: it knows nothing
about the env, the cue, the change-detection task, or the reward palette.

## Default hyperparameters

| Knob                       | Default | Notes |
|---|---|---|
| `feature_channels` (C_V)   | 32      | V1 stem output channels |
| `memory_channels` (C_M)    | 16      | recurrent state channels |
| `inner_K`                  | 2       | iterations of variational inference per env step |
| `inner_eps`                | 0.1     | step size of inner loop |
| `lr`                       | 3e-4    | single Adam lr for everything |
| `pc_coef`                  | 1.0     | weight of L_PC |
| `slow_coef`                | 0.0     | optional slowness regulariser, off by default |
| `clip_range`               | 0.2     | PPO clip |
| `bptt_truncation`          | 16      | gradient truncation window |
| `init_action_logit_bias`   | [0,-4]  | actor bias init — avoids bootstrapping starvation |

Total parameter budget: ~250 K. Runs comfortably on CPU; faster on M-series
or NVIDIA.

## What's NOT here

- **No spotlight / softmax-over-locations primitive.** Intentional — the spotlight account of attention has been progressively undermined by psychophysics (Carrasco 2011) and the normalization model of attention (Reynolds & Heeger 2009). PRISM uses error-derived saliency instead.
- **No task-specific aux losses.** Bitter-lesson compliant — the only auxiliary objective is environment-agnostic VFE.
- **No replay buffer.** PPO is on-policy.
- **No distributional / action-value critic.** Scalar value head. (PrismV2 experimented with both; see `../PrismV2/`.)

## Relation to PrismV2

`../PrismV2/` is a heavier follow-up exploring four extensions: hierarchical
predictive coding (V1 + V2 stems), dual-timescale slow/fast memory at
different spatial resolutions, multi-head saliency with per-head feature
decoders, and an action-conditional distributional Q critic. Each addition
was theoretically motivated; the cumulative architecture has not yet matched
v1's performance on the change-detection task. See
`docs/PRISM_V2_PROPOSAL.md` and `docs/PRISM_V2/Q_CRITIC.md` for the design
rationales and `../PrismV2/README.md` for the current status.
