# RViT+ v5 — conv-free, RL-only, memory-as-tokens

**Status:** implemented + smoke-validated 2026-06-03. Fresh-init only.

## What v5 is

v5 is **v4 with one change: the encoder**. Where v4's feedback transformer lets
the recurrent memory *steer* attention via FiLM (memory → gain/bias on Q/K/V over
the N patch tokens), v5 instead treats the memory **as tokens** — the
"memory-as-tokens transformer" (`FBT_MemTok`) from the Palladio wiki
(`habit_formation/sequence_models/mt_models.py`).

Everything else is identical to v4: the conv-free patch embedding (reshape +
expansion MLP), the 2-layer Transformer actor/critic decoders with CLS-token
readout, and the PAC (MPO+BC) + distributional QR-DQN + prioritized episode
replay trainer.

## The encoder (`memtok_encoder.py`)

Per frame, per layer, the recurrent memory does **not** modulate attention.
Instead each layer is a plain pre-norm `nn.TransformerEncoderLayer` that
self-attends over the concatenation of patch tokens and **all** memory tokens:

```
layer ℓ input  =  [ X + s_patch  ‖  H₁ + p + s_H1  ‖  H₂ + p + s_H2 ]   # 3·N tokens
                    └ N patch ──┘   └ N memory-1 ─┘   └ N memory-2 ─┘
Zℓ            =  TransformerEncoderLayerℓ( · )[:, :N]      # take the patch-token outputs
Hℓ, Cℓ        ←  LSTMCellℓ( Zℓ, (Hℓ, Cℓ) )                # update THIS layer's memory
X             ←  Z₁  (layer 2 consumes layer-1 output AND the just-updated H₁)
```

- **No FiLM.** Attention is standard scaled-dot-product over the 3N-token set.
- **All memory sent as feedback.** Both H₁ and H₂ enter every layer's attention,
  so the transformer sees `(1 + n_layers)·N = 3·N` tokens for the default
  `enc_layers=2` — the "N_tokens × 3" of the spec.
- **Source tags.** A learned `src_emb` (3 entries) tags each group {patch, H₁, H₂};
  memory rows additionally get a positional embedding `p` so row i aligns with
  patch position i. (Patch tokens carry their own pos-emb from PatchEmbed.)
- **Memory update.** The patch-token outputs (first N positions) drive a per-layer
  shared `LSTMCell` that writes that layer's new memory — exactly as in v4, only
  the *source* of `Z` changed (attention-over-tokens instead of FiLM-attention).
- **Requires `d_model == d_mem`** because memory rows are concatenated into the
  d_model token stream. (v4 allowed them to differ; v5 asserts equality.)

The two recurrent states H₁, H₂ (each `(B, N, d_mem)`) are exposed unchanged, so
the **decoders are structurally the same as v4** (CLS + concat(H₁,H₂) = 2N+1
tokens) — with two v5-only refinements:

1. **≥2-layer MLP readout head** — the CLS vector is decoded by an MLP
   (`Linear→GELU→Dropout→Linear`, `head_layers`/`head_hidden` configurable,
   default 2 × `d_mem`) instead of v4's single `Linear`; the final Linear is
   small-init'd and the actor's `init_action_bias` sits on its bias.
2. **Critic action-as-input encoding** — the critic conditions on the action
   *before* the transformer: a learned `action_emb` `(n_actions, n_tokens, d_mem)`
   is added (positional-style, tiled across both memory blocks) to the input
   tokens, the decoder is run once per action (batched over B·n_actions), and
   that pass's CLS readout *is* `Q(s,a,·)`. The action thus modulates the whole
   attention computation, not just a final projection. The actor keeps its
   single-pass head.

## v4 vs v5 at a glance

|                         | v4 (`feedback_transformer.py`) | v5 (`memtok_encoder.py`)              |
|-------------------------|-------------------------------|---------------------------------------|
| memory → attention      | FiLM gain/bias on Q/K/V        | concatenated as tokens (no FiLM)      |
| encoder attention size  | N patch tokens                 | 3·N (patch + H₁ + H₂)                 |
| feedback reach          | layer's own memory steers it   | **all** memories feed every layer     |
| memory update           | LSTMCell from attended Z        | LSTMCell from patch-token outputs Z   |
| decoders                | CLS + 2N memory tokens         | same, + ≥2-layer MLP readout head     |
| CLS readout head        | single `Linear`                | **≥2-layer FF MLP** (`head_layers`)   |
| critic action-cond.     | final projection only          | **learned input encoding**, per-action decode |
| trainer (PAC+QR-DQN+PER)| —                              | **same**                              |
| params (defaults)       | ~1.91M                         | ~1.67M                                |

Outside the encoder, v5 matches v4 except the decoder's CLS readout head (single
`Linear` in v4 → ≥2-layer MLP in v5). `ppo.py`, `env.py`, `config/loader.py`, and
the model's external interface are unchanged from v4.

## Running

```bash
.venv/bin/python -m RViT_plus_v5.tests.test_v5          # 10 smoke tests
.venv/bin/python RViT_plus_v5/train_rl.py               # full 2000-iter run
.venv/bin/python RViT_plus_v5/train_rl.py --device mps
```

Checkpoints → `~/rvit_plus_checkpoints/v5` (outside the Drive-synced repo).
`enc_layers` controls both the number of recurrent memory states and the
encoder token count `(1+enc_layers)·N`; `d_model` must equal `d_mem`.

## Default model size

`d_model=d_mem=128`, `enc_heads=dec_heads=4`, `enc_layers=dec_layers=2`,
`n_quantiles=51`, `head_layers=2` → **~1.67M trainable params**. The 3N-token encoder attention
is heavier per step than v4's N-token FiLM attention (~2× the encoder
self-attention cost), so expect somewhat slower iters than v4.
