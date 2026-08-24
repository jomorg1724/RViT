# V10 — V6's Arena Transformer with the v8 Memory-Residual, Per Layer

**Status:** implemented + tested 2026-06-12. Fresh-init. Copy of
`v6_VizdoomArena` (design, env, trainer, all hyperparameters — see
`v6_VizdoomArena/V6_DESIGN.md` for the full lineage, the run-1 postmortem, and
the reward audit) with a rewired encoder and a new readout stage.

## The change

V6's cross-attention layers put their residual on the layer input:

    Z₁ = X  + attn( Q=norm(X),  KV=[X ++ H₁..H_L ++ state] )      # V6 layer 1
    Z₂ = Z₁ + attn( Q=norm(Z₁), KV=[Z₁ ++ H₁..H_L ++ state] )     # V6 layer 2

V10 makes every layer's residual its **own carried memory** (RViT_plus_v8's
H1-residual, generalized per layer), gives the layers distinct roles, and adds
a third, attention-free LSTM stage whose state is the decoders' sole input:

    Z₁ = H₁_prev + attn( Q=norm(X),      KV=[X ++ H₁..H_L ++ state] )  # PERCEPTION
    Z₂ = H₂_prev + attn( Q=norm(H₁_new), KV=[H₁ ++ H₂ (+pos+tag)] )    # CONSOLIDATION
    H₃ ← LSTM₃( H₂_new )                                               # READOUT

(residuals are the raw carried memories — no tag/pos-emb; H₁_new is the
this-frame H₁, already written by LSTM₁ before layer 2 runs — v5's
hierarchical update order.)

- **Layer 1 (perception)** is the sole port of entry for frame-t input. Its
  residual is the previous frame's H₁, so current-frame content (patches AND
  the K/V-only game-state tokens) reaches LSTM₁ only through the attention —
  value content plus query-driven gating.
- **Layer 2 (consolidation)** sees no raw input at all: its queries are the
  freshly written H₁, its K/V is the memory bank [H₁ ++ H₂], and its residual
  is the previous frame's H₂. The frame reaches H₂ only via H₁. (For L > 2 the
  pattern repeats: layer ℓ queries H_{ℓ-1}, reads [H₁..H_L], residual H_ℓ.)
- **Readout (H₃)**: a per-token LSTM with no attention block ingests the
  freshly written H₂ and carries H₃ — the ONLY representation the actor and
  critic CLS-decoders read ([CLS ++ H₃], 1+48 tokens, instead of v6's
  [CLS ++ H₁ ++ H₂]). H₃ is not in any attention K/V bank: it is a pure
  decision-side accumulator downstream of the whole attention stack, so the
  policy/value gradient reaches the encoder only through the
  perception → consolidation → readout chain.

Everything else — patch embed, game-state tokens, CLS-transformer decoders,
PAC + QR-DQN + segment-PER trainer, every hyperparameter, the reward shaping —
is V6 verbatim. Parameter delta vs v6: +LSTM₃ (132 k) + the H₃ initial state,
− the decoders' shrunken position embeddings; 1.83 M total (v6 ≈1.7 M). Note the key
axis now differs per layer: layer 1 has N·(1+L)+S keys, layer 2 has N·L
(`encoder.key_layout(ℓ)` / `n_keys_for(ℓ)`).

## Why (what v8 taught us)

The v8 experiment on the cued change-detection task showed that closing the
X-residual bypass makes visual attention genuinely load-bearing — and the
follow-up value-stream deep-dive (`RViT_plus_v8/analysis/deepdive/exp6_straw.py`)
showed *how* the trained model actually used the forced bottleneck:

- Zeroing the patch **value content** at every frame cost nothing
  (detect 0.613 vs baseline 0.602).
- Freezing the attention **weights** at the change erased detection exactly to
  chance (hit = FA), while frozen-content/live-weights kept most of it.

I.e. the model perceived through the **query-gating sub-channel**: the current
frame re-aims the softmax over the memory keys, and the re-weighted memory
readout carries the percept — attention-as-addressing (gain modulation on
stored representations), not attention-as-content. V10 asks whether this same
mechanism scales from a 29-frame toy task to the arena: long horizons
(~1050 steps), 13 actions, moving enemies, and reward that depends on fast
reaction to what is currently on screen.

## Predictions / what to watch

1. **It learns at all.** The arena demands frame-accurate perception (aiming at
   moving monsters); if the attention bottleneck throttles that, kills/ep will
   plateau at the ~1.0 noop-infight baseline while entropy stays healthy —
   informative either way (bounds what the X-residual was doing for v6).
2. **Slower early learning** is expected (v8 risk note): at t=0 the residual is
   the learned H₀, so first-frame content arrives purely via attention added
   to a generic prior. If the return is flat far past v6's schedule, suspect
   the attention values under-carrying.
3. If it works, the v6 attention-maps suite applies unchanged
   (`analysis/attention_maps.py` — enemy-attention decomposition + the causal
   bias probe), and the exp6-style value-stream instrumentation can be ported
   to test whether the gating channel dominates here too.

## The no-bypass property is unit-tested

With ONLY layer 1's attention `out_proj` zeroed, the entire recurrent update
(H₁..H₃, C₁..C₃) is bit-identical across wildly different frames AND
game-state features (`tests/test_v10.py::test_no_bypass`) — impossible in v6,
whose X-residual leaks the frame through. Layer 2 and the readout LSTM go
blind automatically because they read nothing but memories.

## Running

```bash
.venv/bin/python -m v10_VizdoomArena.tests.test_v10      # unit + smoke tests
.venv/bin/python v10_VizdoomArena/train_rl.py            # train (auto-selects MPS)
.venv/bin/python v10_VizdoomArena/train_rl.py --iters 200 --device cpu   # quick check
.venv/bin/python v10_VizdoomArena/analysis/attention_maps.py \
    --checkpoint ~/rvit_plus_checkpoints/v10_vizdoom_arena/v10_latest.pt
```

Checkpoints go to `~/rvit_plus_checkpoints/v10_vizdoom_arena/` — outside the
Drive-synced repo (same corruption-avoidance policy as v5/v6).
