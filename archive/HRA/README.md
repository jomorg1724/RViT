# HRA — Hierarchical Recurrent Attention

A prototype neural-network model of visual attention. Follow-up to the recurrent ViT (Herman & Morgan 2025, arXiv:2502.10955); designed to be both an *interpretable neuro-AI model* on the Posner change-detection task and a *parameter-efficient video-prediction architecture* on MovingMNIST / KTH / UCF101.

**Status (May 2026):** Stages 0–1 complete. Architecture scaffold + end-to-end training pipeline + shape and PPO smoke tests passing. Real training runs (≥ 1000 iters) and Track B (video prediction) not yet attempted.

Full design document: [`../MODEL_DESIGN.md`](../MODEL_DESIGN.md).

## Layout

```
HRA/
├── README.md
├── stem.py        # V1 stem: (B, 3, 50, 50) → (B, 32, 12, 12)
├── attention.py   # FeedbackTransformer: multi-source self-attention with Q/K/V feedback gates
├── memory.py      # GridCellRNNCell: ConvGRU base + FeedbackTransformer cross-grid attention
├── decoder.py     # Per-layer PixelDecoder + FeatureDecoder (for PC loss and interpretability)
├── readout.py     # DecisionReadout, ActorHead, CriticHead (scalar), DistributionalQHead (default)
├── losses.py      # predictive_coding_loss, slowness_loss, quantile_huber_loss (QR-DQN)
├── model.py       # HRAModel — three-layer stack with all interpretability hooks
├── env.py         # ChangeDetectionEnv (borrowed from PRISM v1)
├── ppo.py         # Recurrent PPO with distributional Q critic + PC auxiliary
├── train.py       # main entry point
├── config/hra_config.json
├── analysis/      # interpretability analyses (Stage 6 — empty for now)
├── checkpoints/
└── tests/
    ├── test_shapes.py     # 61 shape assertions over every module
    └── test_ppo_smoke.py  # 32 training-pipeline assertions
```

## Quick start

PyTorch must be installed (see project root README). Then:

```bash
cd /Users/jonathanmorgan/AttentionManuscript

# Shape tests (~5s).
/usr/bin/python3 HRA/tests/test_shapes.py

# PPO smoke test (~30s).
/usr/bin/python3 HRA/tests/test_ppo_smoke.py

# Short training run (10 iters, small model, ~30s — useful for sanity).
/usr/bin/python3 HRA/train.py --iters 10 --episodes-per-iter 4 --pc-pretrain-iters 2

# Full training run (default config = 1.7M params, 1000 iters).
/usr/bin/python3 HRA/train.py
```

## Architecture in one paragraph

`HRAModel` is a three-layer stack of `GridCellRNNCell` modules at V1/V4/IT-analog grid resolutions (12×12, 6×6, 3×3) with channel counts 32/64/128. Each cell maintains a spatially-resolved hidden state $C_\ell^{(t)}$. Each iteration: a ConvGRU candidate is computed within each cell (spatially-independent processing), then a `FeedbackTransformer` runs cross-grid self-attention with per-source Q/K/V feedback gates from this layer's previous state plus ascending feedback from deeper layers. Cross-layer communication: convolutional descending projections drive each layer from the layer above; transpose-conv ascending projections supply feedback to layers below. Diminishing feedback into deeper layers ($C_3$ self only; $C_1$ self + $C_2$ + $C_3$). `n_FR=5` iterations per env step. The actor is a thin MLP on a pooled summary of all three hidden states; the critic is an action-conditional distributional QR-DQN head with $V = \sum_a \text{sg}[\pi] Q$. The auxiliary loss is PRISM v1's predictive-coding term applied to the $C_1$ pixel decoder.

## Interpretability hooks

`StepOutput` (defined in `model.py`) exposes:

- `action_logits` — (B, |A|)
- `value` — (B,) the GAE baseline
- `q_dist` — (B, |A|, N) the full distributional Q
- `q_values` — (B, |A|) the mean-over-quantiles Q
- `layer_states_new` — tuple of (C₁, C₂, C₃) after `n_FR` iterations
- `pc_pred` — (B, 3, 50, 50) C₁'s pixel reconstruction
- `attn_per_layer[k][ℓ]` — per-iteration, per-layer attention map (B, n_heads, N_ℓ, N_ℓ)
- `state_per_layer[k][ℓ]` — per-iteration, per-layer hidden state
- `feedback_projections[k]` — dict of all 5 cross-layer projection tensors

Analysis scripts in `analysis/` (to be written in Stage 6) consume these hooks directly. See [`../MODEL_DESIGN.md §7`](../MODEL_DESIGN.md) for the planned 8 analyses.

## Relation to other models in this repo

- **`../Prism/`** — PRISM v1. The best-performing model on the change-detection task to date. No softmax attention by design; uses prediction-error saliency. HRA borrows v1's env, PC loss, and PPO structure but adds spatial self-attention (closer to the Recurrent ViT lineage).
- **`../PrismV2/`** — PRISM v2. Hierarchical PC + slow/fast memory + multi-head saliency + action-conditional distributional Q critic. The Q-critic design is inherited verbatim by HRA from `Prism/docs/PRISM_V2/Q_CRITIC.md`.
- **Recurrent ViT (arXiv:2502.10955)** — single-layer global recurrent attention loop. HRA is the multi-layer follow-up.
- **Video VAE (in Jonathan's personal notes, not in this repo)** — multi-layer conv-recurrent ViT variant with up to 12 feedback sources. The empirically-successful precursor to HRA's architecture.
