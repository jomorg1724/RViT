# Testing the Herman/Morgan FiLM-broadcast mechanism on the RViT+ models

**Status (2026-06-20):** mechanism built + validated on v11_part2 (`RViT_plus_v11_part2_broadcast`, 6/6 tests). The rest is scoped below; each entry is a fresh RL retrain (hand to mps).

## The mechanism

The Herman/Morgan recurrent ViT uses **multiplicative (FiLM) feedback + broadcast self-attention** (paper Eq 13–16), which our v11 line never used — v11 uses cross-attention (the image queries memory). The test: replace each stream's cross-attention with their mechanism and ask whether it helps.

Per stream, self-attention runs over a *content* source; memory feeds back as an identity-initialised FiLM gate on Q/K/V, broadcast (Hadamard) before the attention:

```
Q = (content·W_q) ⊙ Π_g (1 + gate_g·W_gq)          (likewise K, V)
Q, K = LayerNorm(Q), LayerNorm(K)                   # normalize BEFORE the broadcast (stability)
Z = residual + W_o·softmax(QKᵀ/√d)·V + FFN          # broadcast self-attention
```

Two deliberate stabilisations (your prescription): **(1)** gate projections zero-init ⇒ `(1+0)=1` ⇒ feedback off at init ⇒ the block is plain self-attention over `content` (clean baseline, no init explosion — verified Δ=0 vs large gates); **(2)** LayerNorm on Q,K after the FiLM multiply, *before* the softmax — without it the Hadamard product blows the logits up (verified bounded under large gates).

## Phase 1 — broadcast on the v11 family (split pathways left as-is) — IN PROGRESS

Each = the v11 variant's split structure + env, with cross-attn → FiLM-broadcast. Compare to the cross-attn original on the same task.

| variant | env | priority stream (→actor) | value stream (→critic) | cross-attn baseline | broadcast status |
|---|---|---|---|---|---|
| **v11_part2** | cued (4-quad, side cue, colour value) | SA over X, FiLM[H1,H2], res X | SA over H2, FiLM[X], res H2 | hit 0.80 | **built, 6/6 tests, ready to train** |
| v11 | same | parallel; SA over X FiLM[H1] (res X) + SA over H2 FiLM[X] (res H2), heads read both Z | — (joint readout) | hit 0.63 | scoped |
| v11_part3 | same | (swapped readout: value→actor, priority→critic) | | chance (failed) | scoped |
| v11_part4 | same | independent: SA over X FiLM[Hμ] res X / SA over HQ FiLM[X] res HQ, **no shared memory** | | chance (failed) | scoped |
| v11_part5 | distractor (cued side + uncued distractor) | = v11_part2 broadcast on the distractor env | | hit 0.78 | scoped |

Build pattern (per variant): `cp -R RViT_plus_<v> RViT_plus_<v>_broadcast`; sed rename; replace the encoder's cross-attn blocks with `_FiLMBroadcastBlock` (content/gate/residual mapped to that variant's stream structure); keep model/ppo/env/decoder; fresh config; tests. The block module is reusable verbatim.

**Read-out (per variant):** train fresh to the same iters; compare correct/hit/false-alarm/RT and the cueing benefit to the cross-attn baseline. Does the FiLM-broadcast mechanism match or beat cross-attention, and does it change the priority/value dissociation?

## Phase 2 — unified (single) pathway (LATER)

Collapse the split readout: a single FiLM-broadcast stream feeding both actor and critic (the paper's own single-stream form). Tests whether the split is needed once the mechanism is theirs.

## Phase 3 — their exact tasks (LATER)

Port the Herman/Morgan **shorter task variant** (their architecture + their task) and run head-to-head, so the comparison is on their home ground as well as ours.

## Compute note

Every entry is a fresh ~hours-long RL run. Run on **mps**, one at a time (the set-size-9 run is currently occupying mps). Do **not** stack these on the laptop CPU.
