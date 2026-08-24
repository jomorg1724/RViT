# PRISM v2 — Hierarchical Predictive Coding with Slow/Fast Memory and Multi-Head Saliency

A heavier follow-up to PRISM v1 (in `../Prism/`) that explores four
architectural extensions: hierarchical predictive coding (V1 + V2 stems),
dual-timescale slow/fast memory at different spatial resolutions, multi-head
saliency with per-head feature decoders, and an action-conditional
distributional Q critic.

**Status (May 2026):** Despite multiple architectural iterations
(per-channel learned gates, learned spatial pools, head-compression
backbone, action-value critic), v2 has not yet matched v1's performance on
the cued change-detection task. v1 (`../Prism/`) remains the reference
model for this repo. v2 is preserved as a record of the design space we
explored and as a substrate for further ablation work.

Full design rationale: `../Prism/docs/PRISM_V2_PROPOSAL.md`.
Action-value critic derivation: `../Prism/docs/PRISM_V2/Q_CRITIC.md`.

## Layout

```
PrismV2/
├── README.md                       this file
├── env.py                          ChangeDetectionEnv (copy of Prism's)
├── stem.py                         V1Stem + V2Stem (hierarchical encoder)
├── film.py                         HierarchicalFiLM (within-level + cross-level)
├── decoder.py                      PixelDecoder + MultiHeadFeatureDecoder + saliency
├── memory.py                       FastConvGRU + SlowConvGRU + InnerWMLoop +
│                                   CrossLevelErrorPool (Rao-Ballard coupling)
├── readout.py                      HierarchicalDecisionReadout +
│                                   HeadCompressionBackbone +
│                                   ActorHead + distributional Q CriticHead
├── losses.py                       Multi-level PC losses + quantile-Huber
├── model.py                        PrismV2Model (wires everything)
├── ppo.py                          Recurrent PPO + truncated BPTT + two memories +
│                                   action-conditional QR critic loss
├── train.py                        Entry point
├── config/prism_v2_config.json     Default hyperparameters
├── checkpoints/                    Saved weights
├── analysis/gradient_audit.py      Per-module gradient-norm audit (run after
│                                   loading a checkpoint to diagnose head starvation)
└── tests/test_shapes.py            Unit + identity tests, including
                                    action-conditional Q gradient routing
```

## Quick start

```bash
cd /Users/jonathanmorgan/AttentionManuscript/PrismV2
python3 tests/test_shapes.py        # ~5 seconds; should print all OKs
python3 train.py                    # full training run
python3 analysis/gradient_audit.py  # post-checkpoint per-module gradient audit
```

## What's different from v1 (architecturally)

| Aspect                | v1 (`../Prism/`)                           | v2 (this dir) |
|---|---|---|
| Perceptual hierarchy  | one level (V1 stem only)                  | two levels (V1 + V2) |
| Memory                | single `M` (16 ch, 12×12)                 | dual `M_fast` (32 ch, 12×12) + `M_slow` (64 ch, 6×6) |
| Memory time constants | one (gate bias = -1)                      | fast (-1) + slow (-3) |
| Saliency map          | single channel `S` (B, 1, 12, 12)         | per-head `S_V1` (B, K_fast, 12, 12) + `S_V2` (B, K_slow, 6, 6) |
| Inner WM loop         | single, K=2                               | per-level (K_fast=2, K_slow=4) |
| FiLM modulation       | within-level only                         | within-level (fast→V1) + cross-level (slow→V1 upsampled, learned ConvTranspose) |
| Cross-level coupling  | none                                      | top-down FiLM + bottom-up pooled error (learned `CrossLevelErrorPool`) |
| Aux loss family       | per-step VFE (1 level)                    | per-step VFE (per level) — same family, more terms |
| Critic                | scalar `V(s)` MLP                          | action-conditional distributional Q: `(B, |A|, N_quantiles)`, with `V(s) = Σ_a sg[π(a|s)] Q(s,a)` derived for GAE |
| Critic loss           | scalar MSE                                | quantile-Huber on `Q(s, a_t; ·)` (action-conditional QR-DQN loss) |
| Head input            | `s_t` from saliency-weighted readout pool | `HeadCompressionBackbone(M_fast, M_slow, s_readout)` — heads see raw memory directly through a learned compression CNN |
| Param budget          | ~250 K                                    | ~1.48 M after the v2.4 refactor |

What stays the same: the only auxiliary-loss family is variational free
energy (now per-level). No task-specific aux. Bitter-lesson framing
preserved.

## Default hyperparameters (from `config/prism_v2_config.json`)

The config currently runs the full v2.4 architecture:

```
feature_channels_V1=64, feature_channels_V2=128,
memory_channels_fast=32, memory_channels_slow=64,
n_heads_fast=4, n_heads_slow=4,
inner_K_fast=2, inner_K_slow=4, inner_eps=0.1,
update_gate_bias_fast=-1.0, update_gate_bias_slow=-3.0,
decision_channels=8, decision_coarse_grid_fast=2,
head_compression_hidden=32, head_compression_output=256,
actor_hidden=128, critic_hidden=128,
n_quantiles=51, n_actions=2,
init_action_logit_bias=[0.0, -2.0],
pc_pixel_coef=1.0, pc_pixel_autoenc_coef=1.0,
pc_pixel_grid_coef=0.1, pc_pixel_grid_autoenc_coef=0.1,
pc_V1_feat_coef=0.1, pc_V2_feat_coef=0.5, pc_V2_feat_autoenc_coef=0.5,
lr=3e-4, n_epochs=4, clip_range=0.2,
value_coef=0.5, entropy_coef=0.005,
pc_coef=1.0, slow_coef=0.0,
grad_clip=0.5, gamma=0.95, gae_lambda=0.95,
bptt_truncation=32,
inner_K_warmup_iters=0, pc_pretrain_iters=0,
save_interval_iterations=500
```

## Staged variants (per the v2 proposal §8)

The default config is v2.4 (everything together). For ablation experiments
isolating each addition (v2.1 multi-head only; v2.2 slow/fast only; v2.3
hierarchical only), make a copy of the config with the relevant components
disabled (e.g. set `n_heads_slow=1` to disable multi-head at the slow level).

## Diagnostics

Two diagnostic columns now appear in the per-iter PPO log:

* `Zstd` — std over the quantile axis of `Q(s, a_t; ·)`. Should grow above 0
  as the critic learns to represent the spread of returns.
* `dQ` — mean `|Q(s, a=0) − Q(s, a=1)|` across the batch. **The key signal
  for whether the action-value critic is engaging.** If `dQ` stays at ~0, the
  critic has not learned to discriminate actions and the policy gradient is
  starved of advantage signal — the failure mode the Q critic was introduced
  to fix. See `../Prism/docs/PRISM_V2/Q_CRITIC.md` §5 for what to do then.

`analysis/gradient_audit.py` loads the latest checkpoint and reports per-
module gradient norms under FULL / RL-only / PC-only loss decompositions —
useful for diagnosing which loss is dominating the global-norm clip.
