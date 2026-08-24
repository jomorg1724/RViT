# RViT+ v8_part2 — memory-only K/V: the continual mnemonic codebook

**Status:** implemented + tested 2026-06-12. Fresh-init. Exact copy of
RViT_plus_v8 (trained & deep-dived 2026-06-09/10) with **one further change**
on top of the H1-residual.

## The change

v8's cross-attention block still had patch tokens in the K/V stream:

    Z = H1_prev + attn( Q=norm(X), KV=[X ++ H1 ++ H2] )   # v8

v8_part2 removes visual content from K/V entirely:

    Z = H1_prev + attn( Q=norm(X), KV=[H1 ++ H2] )        # v8_part2

Patch tokens are **queries only**. The keys and values are the mnemonic memory
bank — previous-frame H1 and H2, tagged and position-aligned. Visual
information can reach the recurrent state ONLY through **query-side gating**:
the current frame re-aims the softmax over stored representations. There is no
visual value stream at all — no "straw" to measure, because raw pixels never
enter the attention output projection.

This is the logical conclusion of the v8 exp6 finding: the trained v8 model
carried perception mostly through query-gating, not patch value content
(zeroing patch values cost nothing; freezing attention weights erased
detection). v8_part2 forces that mechanism by construction.

Everything else — H1-residual, patch embed, stacked per-token LSTMs, 1D-conv
decoders, PAC + QR-DQN + PER trainer, every hyperparameter — is v8 verbatim.
Parameter count is **identical** (we remove patch from K/V but the same
`in_proj` weights remain; the model simply never routes queries through the K/V
projection for patch tokens).

## Why (the hypothesis)

v8 closed the X-residual bypass but still allowed visual *content* to enter via
attended patch values. exp6 showed the trained model barely used that channel.
v8_part2 asks: can the model solve change detection using **only** a continual,
learnable mnemonic codebook addressed by query-gating? This is closer to the
user's VQVAE analogy — soft lookup into stored codes, with the frame selecting
*which* codes to read, not injecting new visual content downstream of the
attention map.

Predicted signatures:

1. **It learns at all** — the task requires perceiving orientation/color changes;
   if query-gating alone cannot carry enough information, hit rate stays at
   chance while entropy stays healthy.
2. **Patch-key causal probes are gone** — there are no patch keys to bias.
   Causal experiments target memory keys (H1/H2) and query-side interventions.
3. **Attention mass is 100% on memory** — by construction. Spatial
   selectivity shows up as which *memory positions* (patch-aligned rows in H1/H2)
   get re-weighted, not which patch keys are attended.
4. If it works, the mechanism is unambiguously attention-as-addressing on a
   continual codebook — no visual content downstream of the softmax.

## Risks / what to watch

- Strictest bottleneck yet: no visual values AND no X-residual. Only query
  gating + H1_prev skip. Slower learning or failure is informative.
- t=0: H1 = learned H0, first-frame content arrives purely via gating added
  to a generic prior.
- Gradients to patch_embed still flow through Q = norm(X) and through the
  softmax Jacobian — the patch MLP can still learn features that drive
  gating, even though pixels never appear in V.

## The no-bypass property is unit-tested

With the attention `out_proj` zeroed, the encoder's recurrent update is
bit-identical across wildly different input frames — and now for a stronger
reason than v8: even with `out_proj` live, **no visual content exists in the
value stream**. Only query-side gating (which depends on X) can differentiate
frames; silencing `out_proj` blocks that too.

## Running

```bash
.venv/bin/python -m RViT_plus_v8_part2.tests.test_v8_part2
.venv/bin/python RViT_plus_v8_part2/train_rl.py
```

Checkpoints go to `~/rvit_plus_checkpoints/v8_part2/`.
