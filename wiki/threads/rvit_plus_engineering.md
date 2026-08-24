---
id: rvit_plus_engineering
type: thread
title: "RViT+ engineering log: video-compression pretraining, attention-collapse failure modes, surgical fixes"
papers:
  - vaswani2017_attention
  - dosovitskiy2020_vit
  - hochreiter_schmidhuber1997_lstm
  - ballas2016_convgru
  - voita2019_head_specialization
  - tallec_ollivier2018_chrono_init
  - wu_he2018_groupnorm
concepts:
  - feedback-transformer
  - gridcell-rnn
  - multi-compartmental-memory
  - bidirectional-hierarchical-feedback
  - iterative-variational-encoder-decoder
  - positional-encoding
source_documents:
  - "RViT_plus/ (project code)"
  - "RVIT_PLUS_DESIGN.md (design doc, 8-question approval + 5-stage curriculum)"
  - "research_db/threads/the_user_architectural_program.md §6"
  - "memory/project_visual_attention_model.md (HRA predecessor findings)"
last_updated: "2026-05-25-confirmed-baseline"
---

# RViT+ engineering log

This thread is the iteration-by-iteration empirical narrative of the **RViT+** model — the architectural successor to HRA, after HRA was abandoned (May 2026) for failing to develop interpretable attention structure under sparse-reward PPO. RViT+ pivots to a pretraining-first strategy: train the encoder/decoder stack as a **video-compression autoencoder** on synthetic data, verify that attention develops structure under dense reconstruction-gradient pressure, *then* attach the RL controller for downstream Posner change-detection. The architectural commitments (multi-compartmental memory, Feedback Transformer cells, retinotectal-analog skips, iterative variational encoder–decoder) inherit from the architectural-program thread but with empirically-motivated refinements documented here.

The thread is organized as a chronological log of runs and their findings. Each run's failure mode informed the architectural change for the next run. The current canonical state is documented at the end.

---

## Context: why RViT+ exists

HRA (the prior prototype, `HRA/` in repo, documented in `memory/project_visual_attention_model.md`) ran 4k+ episodes of PPO on Posner change-detection and produced:

- Attention entropy / max-entropy ≈ 1.000 across all 3 layers and all 5 inner iterations — the FT never developed any spatial focus
- `ft_residual_scale` went *negative* in 2 of 3 cells — cells learned to *subtract* the FT contribution
- Correct rate stuck < 0.50 with policy frozen at 6% press

The diagnosis (recorded in `concepts/feedback_transformer.md` open question 4) reads as a Voita-style head-collapse trap exacerbated by sparse-reward PPO: most of the attention map produces zero gradient (no event → no policy-gradient differential across spatial locations), so the FT sits at a flat minimum where uniform attention is locally optimal.

**RViT+ pivots to dense reconstruction supervision before any RL.** The bet is that with per-pixel MSE gradient flowing back through the FT at every timestep, attention must develop spatial structure to compress video. This converts a sparse credit-assignment problem into a dense supervised one, and only then introduces RL on top of an already-structured representation.

The architectural ancestry is the user's Video VAE work (the most successful published instance of the program; ~12 feedback sources, UCF101 video reconstruction). RViT+ is structurally that lineage rebuilt from scratch as a clean small-scale prototype, with explicit interpretability hooks (per-layer attention maps, `attn_bias` microstimulation plumbing) and a falsifiable falsifiable-prediction list (P1–P6 in `RVIT_PLUS_DESIGN.md`).

---

## Architecture (as of run 6, 2026-05-20)

Three GridCell-RNN cells with explicit Feedback-Transformer attention, mirrored between encoder and decoder.

- **Stem:** 3-channel 50×50 RGB input → V₁ feature map (B, 64, 12, 12). Two-conv ReLU stem.
- **Encoder cells:**
  - C₁: (B, 64, 12, 12) — V1 analog
  - C₂: (B, 96, 12, 12) — V4 analog
  - C₃: (B, 128, 6, 6) — IT analog
- **Cross-layer routing:** descending C₁→C₂ (1×1 conv adapter), C₂→C₃ (stride-2 conv); ascending C₂→C₁, C₃→C₁, C₃→C₂ via 1×1 + bilinear upsample. Three feedback sources into C₁, two into C₂, zero into C₃ — the diminishing-feedback-into-deep-layers design from `threads/the_user_architectural_program.md` §3.
- **Retinotectal skips:** V → C₂, V → C₃ at `skip_scale=0.3` — bottom-up shortcut around C₁ congruent with the L4 thalamic + L5 long-range projections in the cortex literature.
- **Per-cell update rule** (`memory.py` `GridCellRNN_LSTM`, evolved over runs 1–6):
  - Stage 1: SIP candidate via 1×1 conv on `[z_t, C_{t-1}]`, tanh-bounded
  - Stage 2: FT integration on `(sip_candidate + pos_emb)`, with `C_{t-1}` and external feedback as feedback sources
  - Stage 2b (added run 6): **SIP residual** — `tilde_C = sip_candidate + ft_out`
  - Stage 3: LSTM-style update gate — `C_new = (1 − u) ⊙ C_{t-1} + u ⊙ tilde_C` with `u = σ(W_u · [z_t, C_{t-1}])`, bias=0 (σ(0)=0.5 reactive baseline, Tallec–Ollivier chrono-init at the neutral setting)
- **Iterative variational encoder–decoder:** encoder runs n_FR=4 inner iterations per video frame; final encoder state feeds a Gaussian VAE latent sampler; decoder is a structural mirror that takes (final_state, latent, T) and unrolls T per-step reconstructions.
- **Microstimulation hook:** every cell's `forward()` accepts an `attn_bias` kwarg passed through to `FeedbackTransformer.forward`, plumbed end-to-end so analyses can inject per-(frame, layer, iter) attention biases and observe downstream effects — the FEF-microstim analog from the published RViT paper.

Param count: **1.36M trainable** (1.18M pre-run-6; the +180K is the restored update-gate convs and the per-cell positional embedding parameters).

---

## Run-by-run log

### Stage 0a/0b/0c — scaffold and primitive tests (2026-05-18 → 05-19)

All 20 primitive shape tests (`tests/test_primitives.py`) pass. All 55 full-model shape + microstim + gradient-flow tests (`tests/test_full_model.py`) pass. Microstim plumbing verified end-to-end: a 5.0-logit bias added to the FT attention scores at a specific (frame, layer, iter, key location) propagates correctly and lands at exactly that cell with no contamination of other frames or iterations. The microstim hook is the same one HRA had but with the FT *in the gradient path from step one* (no zero-init `ft_residual_scale`) — the wiring fix that follows from the HRA iter-499 finding.

### Run 1: 250-iter smoke, PPO setup (HRA legacy, not RViT+ proper)

Initial sketch on Posner directly. Cell params 349K — over the 250K budget. Trace: I had used 3×3 convolutions for SIP. Per `concepts/gridcell_rnn.md` *Stage 1 — SIP must be strictly per-cell (1×1)* — the 3×3 was a non-spec spatial coupling at Stage 1. Fixed to 1×1; cell dropped to 87K params, total under budget.

### Run 2: per-frame autoencoding, 2000 iters, GAP decoder

**Result:** Reconstructions near-perfect (recon=0.0007). **Attention entropy 0.999 (uniform) across all (layer, iter, frame) cells.** P1 falsified.

**Diagnosis:** The decoder used global average pooling on the final state, destroying spatial gradient flow. Combined with per-frame autoencoding (every frame reconstructed from its own current encoding), the encoder has no incentive to retain spatial structure — a trivial per-pixel mapping suffices.

### Run 3: spatial decoder, 2000 iters

**Result:** Recon still ≈ 0.001. **Attention still uniform.** P1 falsified.

**Diagnosis:** Even with a spatial decoder, per-frame autoencoding lets the model exploit the LSTM update gate: keep `u` small, pass through `C_{t-1}` largely unchanged, ignore the FT entirely. The FT's contribution becomes a small additive perturbation that the model can compensate for elsewhere. No compression pressure → no reason for the FT to develop structure.

### Run 4: removed update gate (C_new = tilde_C only), 2000 iters

**Result:** Same uniform-attention pattern. **The update gate wasn't the issue.**

**Diagnosis:** The architectural issue is *per-frame autoencoding*, not the gate. With every frame independently encoded and decoded, there is no temporal compression pressure: the encoder never has to *retain* spatial information from earlier frames into later state. The FT, which is the only mechanism by which spatial information could be retained, is unused and collapses to uniform.

### Run 5: video compression mode, 2000 iters — TOTAL COLLAPSE

**User clarification (the critical correction, 2026-05-20):** *"The video autoencoder model is a video compression model. It watches the video until the very end, compressing along the way until the final frame. Then when we decode, we use a mirror model to reconstruct, backwards from the last time step, the full video."*

This is fundamentally different from per-frame autoencoding. Implementation: encoder consumes T=10 frames sequentially, producing a final compressed state; VAE samples a latent from that state; decoder is initialized from the final state + latent and unrolls T per-step reconstructions. Direction (forward vs. backward decode) is implementation-equivalent; we decode forward because the temporal-embedding math is cleaner.

**Result:** Reconstruction MSE 0.02 — superficially looks fine. **But:**
- All reconstructions are visually all-black or near-black
- All encoder hidden states (C₁, C₂, C₃) have **zero spatial variance** — every (h, w) cell has the same value
- All decoder hidden states likewise have zero spatial variance
- Attention entropy still 0.999 uniform

This is a more severe failure than runs 2–4. Recon loss 0.02 is just MSE(0, video) — i.e. the model degenerated to producing the *mean image* (which for centered MovingMNIST inputs is near zero) and the optimizer rode that local minimum. Compression pressure was real but the FT collapse was so complete that the encoder produced a position-invariant (= spatially uniform) latent that could only decode to a position-invariant output. P1 falsified, P5 (visible reconstruction) falsified.

**Root-cause diagnosis (the three contributing factors):**

1. **No positional embeddings.** Without per-(h, w) position tags, the FT is permutation-equivariant. Uniform attention is a fixed point: every key is interchangeable with every other key, so the softmax has no reason to prefer one over another, and the cell's spatial dimension is unused. *This was the dominant contributor* — without position info, the FT cannot break symmetry.

2. **FT had unilateral control over the candidate.** Run 4 removed the update gate (Stage 3); the candidate was `C_new = tilde_C` where `tilde_C = ft_output` directly. So if FT collapsed to uniform, the entire candidate collapsed to uniform, and the optimizer minimized loss by producing the zero/mean output (no spatial detail anywhere → no detail-mismatch penalty).

3. **No SIP residual.** The SIP candidate (which *did* have per-cell spatial structure, since it's a 1×1 conv on `[z_t, C_{t-1}]`) was *replaced* by the FT output rather than *added to* it. So SIP's per-cell structure never reached the next layer. The user's original `gridcell_rnn.md` spec describes Stage 2 producing the integrated proposal `tilde_C` as the FT output — this is technically fine when FT is healthy, but provides no fallback when FT collapses.

### Run 6: surgical fixes — pos_emb + SIP residual + restored update gate (current, 2026-05-20)

Three changes to `memory.py`'s `GridCellRNN_LSTM`:

1. **Add learned positional embedding** per (channel, h, w). Initialized small (std=0.02, ViT convention) so it perturbs the candidate gently at init. Added to `sip_candidate` *before* GroupNorm-pre-FT so the FT input carries position info.

2. **SIP residual.** `tilde_C = sip_candidate + ft_output` rather than `tilde_C = ft_output`. Guarantees that the per-cell spatial structure produced by SIP survives even if FT collapses to uniform — the FT is now a *refinement on top of* the SIP candidate, not a *replacement for* it. The architectural reading: SIP is the spatially-local low-frequency component, FT is the high-frequency spatial-coupling correction.

3. **Restore the LSTM update gate** with bias=0 (σ(0)=0.5 reactive baseline). `C_new = (1 − u) ⊙ C_{t-1} + u ⊙ tilde_C`. Critically, FT remains in the gradient path *from step one* (via `u ⊙ tilde_C`, where `u` starts at 0.5) — this is NOT the HRA `ft_residual_scale=0` trap from iter-499. The gate provides recurrence-stability without gating out the FT.

**Status:** Completed 2026-05-20 ~20:35. recon = 0.49 → 0.02 over 2000 iters (similar trajectory to run 5), no grad-skips.

**P1 verdict: STILL FALSIFIED.** Encoder entropy/max ≈ 0.9998 across all (layer, iter, frame); decoder entropy/max ≈ 0.998 (cell C_3) to 1.000 (cells C_1, C_2). Both encoder and decoder report frac<0.80 = 0.0%. The three surgical fixes did NOT break the attention-uniformity pattern.

**P5 verdict (visible reconstruction): FALSIFIED, but differently from run 5.** Reconstructions are not all-black-zero — they have nonzero spatial std (0.013 per frame, vs input 0.144). What the model learned is the *mean image with 10% contrast* — not total collapse.

### Run-6 post-hoc diagnosis: posterior collapse + MSE mean-regression, NOT FT collapse

Numerical diagnosis on two distinct MovingMNIST sequences (seeds 0 and 1):

| Quantity | Value | Reading |
|---|---|---|
| Input mean / std | −0.987 / 0.144 | background-dominant; digits ≈ 15% of pixels |
| Recon mean / std | −0.986 / 0.014 | matches input mean exactly; **10× less contrast** |
| MSE | 0.0205 | ≈ Var(input) − Var(recon) ≈ 0.144² − 0.014² |
| Latent μ range | [−0.011, 0.010] | **KL collapsed**: μ ≈ 0 |
| Latent μ std | 0.0041 | essentially noise around 0 |
| `\|μ(v1) − μ(v2)\|`.mean | 0.0007 | **different videos → same latent** |
| Encoder ΔC₁ / state.std | 1.1% | weak content differentiation |
| Encoder ΔC₂ / state.std | 0.3% | nearly zero |
| Encoder ΔC₃ / state.std | 0.1% | **C₃ is content-blind** |

The architectural protections from runs 1–5 *did* work at the encoder level — encoder states have nonzero spatial std (C₁: 0.068, C₂: 0.016, C₃: 0.031, vs. run-5's effective-zero). The SIP residual prevents the FT-collapse → zero-spatial-variance failure mode. But the model never *uses* this capacity because:

1. **The MSE loss on background-dominant data rewards the trivial-mean prediction.** A model predicting the constant near-mean (≈ −0.99 everywhere) gets MSE ≈ Var(input) ≈ 0.02 — essentially the loss the model converged to. There is no asymmetric pressure that would cost more to under-predict digit pixels than to under-predict background pixels.

2. **The KL collapsed the latent before the model needed it.** Early-training KL was high (113 at iter 9), the optimizer aggressively squashed it (0.005 by iter 100s and onward). Once collapsed, the decoder learned to ignore the latent. The encoder then had no gradient pressure to put information *into* the latent, so the latent stays collapsed forever — classic VAE posterior collapse.

3. **The decoder has a non-latent path (final encoder states) that bypasses KL.** Decoder cells D₁/D₂/D₃ are initialized from the encoder final states, which carry some spatial info free of KL pressure. *But the model also barely uses this path:* inter-video state difference is 1.1% / 0.3% / 0.1% in C₁/C₂/C₃ — the model is not differentiating videos at any level.

4. **The decoder per-step driving signal is spatially uniform.** `z₁(τ) = latent_proj(latent) + temporal_proj(temporal_emb(τ))` is computed as a (B, c1) vector then spatially broadcast to (B, c1, h1, w1). When the latent is collapsed, `z₁` is a function of τ only — purely temporal, no content. The decoder cells then must extract content from `D_{prev}` (cell state) alone, and with collapsed encoder states there is little content there to extract.

This is a *different failure mode from runs 2–5*. Runs 2–5 failed because the FT collapsed and destroyed spatial structure. Run 6 doesn't have that failure — the FT collapsed (attention is still uniform) but spatial structure is preserved by the SIP residual. The failure is *upstream of the architecture*: the training objective itself is degenerate on this data shape, and the FT receives no gradient pressure to develop because reconstruction is "solved" by predicting the mean.

### What this means for the architectural-program claim

The architectural-program hypothesis (dense reconstruction gradient pressures the FT to develop attention) is now in trouble. On MovingMNIST (50×50, background-dominant), MSE reconstruction is too easy to satisfy with a trivial-mean predictor for the FT to have any work to do. The hypothesis is not falsified — it is *untested* on this data + loss combination, because the test setup doesn't actually pressure attention.

### Run-7 design (next): break the trivial-mean trap

The architecture stays. The fixes are to the training objective:

1. **Reduce `kl_coef` aggressively** (0.05 → 0.001 or use free-bits with threshold 2.0). The latent must carry real information for the model to develop genuine compression.
2. **Replace MSE with L1 + perceptual contrast loss** or weight digit pixels above background pixels. The current MSE has no asymmetry penalizing under-prediction of digit content.
3. **Drop the `pix_out` zero-init.** It was supposed to prevent NaN at init but in practice makes the trivial-mean solution a strong attractor: gradient at init = `dL/d(recon) = 2(recon − video) = 2(0 − video) = −2·video`, which pushes pix_out.bias toward mean(video) very fast and pix_out.weight only slowly. Initializing pix_out with small Gaussian gives the model immediate spatial gradient.
4. **Optionally add a contrast-floor loss term** (`max(0, σ_target − σ(recon))`) that explicitly penalizes low-contrast reconstructions.
5. **Increase digit count or shrink frame** so background fraction is lower. MovingMNIST at 50×50 with 14×14 digits is 84% background; tighter framing or more digits per frame would reduce the mean-prediction reward.

If run 7 produces attention structure under these adjustments, the architectural-program claim is *vindicated*: dense reconstruction pressure does develop FT structure, but only when the optimization objective is well-posed. If run 7 still fails, the FT is structurally not earning its keep on synthetic data and the bridge to Posner RL (the original goal) will need an explicit attention-supervision signal from the cue position.

**Run-6 stays a learning experience preserved in this log. Run-7 changes do not touch `memory.py` — the cell is correct.** Edits are confined to `train.py` (loss-function changes) and `decoder.py` (`pix_out` init).

### Run 7: loss-function and pix_out-init fixes (2026-05-20, in progress)

User chose "fix the loss & init" over data densification or explicit attention supervision (see `AskUserQuestion` exchange in session log). Architecture frozen at run-6 form. Four interventions ship together:

1. **`pix_out` init: zero → small-Gaussian (std=0.02)** in `decoder.py`. Removes the zero-init attractor toward mean-image prediction; the model produces nontrivial output from iter 0.

2. **Reconstruction loss: MSE → L1** in `train.py`. L1 is less mean-biased on sparse / background-dominant data; the L1 minimum of a mixture is the median, not the mean, so digit pixels carry comparable gradient weight to background pixels. MSE is still computed and reported as a secondary metric so loss curves are cross-comparable with runs 1–6.

3. **`kl_coef`: 0.05 → 0.001** in `train.py`. Reduces the dominant pressure that collapsed the run-6 latent.

4. **Free-bits KL** (Kingma 2016 trick) in `train.py`. KL is hinged: each latent dim is allowed up to 2.0 nats "for free" before contributing to loss. Implementation: `kl_hinge = clamp(kl_per_dim − 2.0, min=0).sum()`. This removes the gradient pressure to push μ → 0 below the free-bits ceiling. Latent sampler `latent.py` now exposes `kl_per_dim: (B, latent_dim)` in its return dict; `CompressionOutput` propagates this for trainer access.

**Predictions for run 7:**
- *KL behavior:* `kl_raw` per dim should sit near (slightly below) 2.0 nats — the model uses the free-bits budget. `kl_hinge` should hover near 0 once trained.
- *MSE companion metric:* should converge to a value *higher* than run-6's 0.02 (because the model produces nontrivial contrast under L1 instead of trivial-mean under MSE) but the recons should be visually informative for the first time.
- *P1 (attention entropy):* The architecturally critical test. If the model now genuinely compresses video (rather than predicting the mean), the FT should have real work to do — gathering relevant information from distant cells — and attention should sharpen. The smoke-test signature is already healthier: at iter 49 of the smoke run, kl_raw=158 nats (1.23 nats/dim, below the 2.0 free-bits ceiling so kl_hinge=0) and mse_t0=0.63 (nontrivial contrast), vs. run-6's converged mse=0.02 (trivial-mean).
- *Inter-video latent variability:* should be large now (run-6 was 0.0007 — same latent for any video). If `|μ(v1) − μ(v2)|` is still small, the encoder is not using the latent even when it has the freedom to.

Smoke test (50 iters, batch=4) confirms the loss-function plumbing is correct: L1 trains, free-bits hinge engages then releases, no NaN. Full 2000-iter run launched ~20:45.

Files touched in run 7 (for audit trail): `RViT_plus/train.py` (loss function + arg flags), `RViT_plus/latent.py` (expose `kl_per_dim`), `RViT_plus/model.py` (`CompressionOutput.kl_per_dim` field), `RViT_plus/decoder.py` (`pix_out` init), `RViT_plus/tests/test_full_model.py` (one test updated for new init range). 55/55 + 20/20 tests pass post-edit.

### Run-7 result: P1 falsified again, but the diagnosis localized to the DECODER

**Loss curve:** L1 = 0.64 → 0.014 over 2000 iters. KL settled at ~148 nats (1.16 nats/dim, below the 2.0 free-bits ceiling → kl_hinge=0). No NaN. Encoder *did* respond:

| Quantity | Run 6 | Run 7 | Improvement |
|---|---|---|---|
| Encoder C₁ spatial_std | 0.068 | 0.103 | +52% |
| Encoder C₂ spatial_std | 0.016 | 0.042 | +163% |
| Encoder C₃ spatial_std | 0.031 | 0.065 | +110% |
| Latent μ std | 0.004 | 0.670 | **+167×** |
| `\|μ(v1) − μ(v2)\|`.mean | 0.0007 | 0.0032 | +357% |
| `\|C₁(v1) − C₁(v2)\|`.mean | 0.015 | 0.033 | +120% |

**But P1 STILL FALSIFIED.** Encoder entropy/max ≈ 0.999, decoder ≈ 0.998–1.000, frac<0.80 = 0.0% on both. And the reconstruction is *worse* in a specific sense: recon.std = 0.0007 (vs run-6's 0.014) — the model converged to **an exactly-constant prediction of -1 everywhere**:

```
recon mean = -0.9999, recon std = 0.0007, pixel correlation with input = -0.01
```

The L1 loss of 0.014 equals 1 + E[input] = 1 + (-0.987) = 0.013 — *precisely* the L1 of predicting the constant -1. L1's minimum on background-dominant data is the *median* (the most-common value), and our data's median IS -1 (background). I'd replaced "MSE → mean image" with "L1 → median image", and both attractors are the same: a constant-background prediction.

### The DECODER-collapse finding

Probe of decoder hidden state D₁ over time:

| t | D₁ spatial_std | Interpretation |
|---|---|---|
| 0 (from encoder) | **0.017** | encoder hands over spatial structure |
| 4 | 0.0007 | decoder has washed it out ~24× |
| 9 | 0.0001 | gone |

The decoder's per-step driving signal `z₁(τ) = latent_proj(latent) + temporal_proj(temporal_emb(τ))` is **spatially uniform** (the (B, c1) projection is broadcast across (h1, w1)). With the update gate at σ(0)=0.5 reactive baseline, every decoder step washes out 50% of the encoder's spatial structure: after 10 steps the encoder-bequeathed spatial structure is 0.5¹⁰ ≈ 10⁻³ of its initial magnitude — empirically observed as 0.017 → 0.0001.

The encoder IS encoding spatially-structured information. The decoder cannot WRITE this information back into spatial pixels because its driving-signal pathway has no spatial channel. Even if the FT attention had developed structure, the SIP candidate is `tanh(conv1×1([z₁, D_prev]))` — if z₁ dominates (it does at decoder init, before D_prev's contribution accumulates), SIP is also spatially uniform.

### What this means

The architectural-program claim is still not falsified, but the test is *doubly degenerate*: the loss permits a trivial constant prediction AND the decoder architecture cannot easily produce spatial output even when the encoder produces a structured latent. Both have to be fixed before P1 is a meaningful test.

The next run needs *both* a content-weighted loss (so the trivial-constant minimum is not optimal) AND a spatially-structured decoder input (so the decoder cells have a spatial signal to operate on). The loss fix alone (run 7) made the encoder do real work, but it had no channel to deliver that work to pixels.

### Foundational error called out by the user (2026-05-20, after run 7)

The user explicitly flagged that I had violated the central architectural commitment of the program:

> *"You have reduced the visual scene to a single 1D vector. This was the foundational thing I asked you not to do. Look again how the video autoencoder works in the theory document. Memory is spatially oriented. Our memory should be oriented as (batch, n_channels, H_mem, W_mem)."*

The `latent.py` `VAELatentSampler` had been doing GAP across spatial positions to produce a (B, 128) vector latent — collapsing the encoder's spatial structure at the VAE bottleneck. The decoder then broadcast this vector back across (h, w) at every step, producing a spatially-uniform driving signal. The whole spatial pipeline (encoder cells spatial, decoder cells spatial) was interrupted by a 1D bottleneck that my training-data prior toward standard VAEs had inserted.

This is documented in `concepts/iterative_variational_encoder_decoder.md` §"Multi-patch distributional latents":

> *"The guide is a matrix $\\tilde H_0 \\in \\mathbb{R}^{n_\\text{patch} \\times d_\\text{guide}}$, not a vector."*

I had deferred the matrix-normal latent to "v2" in `RVIT_PLUS_DESIGN.md` §3.4 with the rationale that "vector latent is the simpler v1 baseline." That deferral was the architectural error: it broke the spatial commitment in the one place that matters most (the bottleneck where information density is highest), and it explains why P1 failed across runs 5–7 despite multiple architectural protections elsewhere in the pipeline. Pre-existing failure modes (FT collapse, posterior collapse, mean-regression) were *symptoms* of this error, not independent issues.

### Run 8: spatial latent at C₃ + content-weighted loss (2026-05-20, current)

Architecturally faithful redesign of the VAE bottleneck. The latent is now a *spatial* tensor at the deepest encoder level — no GAP, no broadcast, no 1D anywhere in the pipeline.

**`latent.py` rewrite — `SpatialVAELatentSampler`:**
- Input: encoder final states (C₁, C₂, C₃)
- Per-position Conv1×1 on C₃ produces (μ, log σ²) at shape (B, latent_channels=16, h3=6, w3=6)
- Reparametrized sample: (B, 16, 6, 6) — spatial structure preserved at every position
- KL: per-position diagonal Gaussian against unit prior, summed over (latent_c, h3, w3), batch-mean
- Total latent dimensionality: 16 × 6 × 6 = 576 (vs. previous 128) — slightly larger, organized spatially.

**`decoder.py` rewrite — spatial-latent pathway:**
- D₃ initial state = `latent_to_d3(sample)` — Conv1×1 channel adapter, preserves the 6×6 grid
- D₁, D₂ initial states still come from encoder final C₁, C₂ — these were already spatial
- Per-step driving signal z₁(τ) for cell1 is now ONLY the temporal embedding broadcast across (h1, w1). Removed the `latent_proj` (was the broadcast that destroyed spatial structure). Spatial content flows into cell1 via the ascending feedback from D₂ and D₃ (both spatial), and via D_prev (which is initialized spatial and updated each step).
- Removed `z_to_c1` (no longer needed; temporal_emb directly has c1 channels).

**`train.py` addition — content-weighted reconstruction loss:**
- Compute per-pixel weight: `1.0 + (content_weight − 1.0) * (|input| > content_threshold)` with defaults `content_weight=10.0`, `content_threshold=0.5`
- Normalize weight so `mean(weight) = 1` → unweighted loss scale is preserved on average
- Weighted L1 or MSE: `(weight * |recon − video|).mean()` per timestep
- This breaks the trivial-constant minimum: with digit pixels weighted 10× over background, predicting `−1` everywhere is no longer optimal — the digit-pixel residual contributes more weighted loss than the background-saving.

**Param count:** 1.28M (down ~80K from run 6/7 because the spatial latent's Conv1×1 has fewer params than the GAP→Linear→128 vector pathway).

**Smoke test (50 iters, batch=4):**
- L1: 0.93 → 0.79
- KL: ~700 nats (~1.2 nats/dim across 576 dims, below the 2.0 free-bits ceiling — latent is *being used*)
- kl_hinge: occasionally nonzero (0.35–0.63), so some dims are exceeding 2.0 nats and getting penalized — the model is actively pushing past the free-bits ceiling on selected positions, which is the desired behavior
- MSE companion: 0.62 (vs. run-7 smoke 0.42 at iter 49) — model is producing *more contrast*, not collapsing to constant
- 76/76 tests pass (20 primitive + 56 full-model)

Full 2000-iter run launched 2026-05-20 ~21:30. Predictions:
- *P1 (attention entropy):* meaningful test for the first time. If the FT now has a real spatial reconstruction task to support (because the latent is spatial and the loss penalizes background-only predictions), attention should sharpen. If P1 still fails after this, the architectural-program claim that dense reconstruction develops FT structure is in genuine trouble for synthetic data.
- *P5 (visible reconstructions):* digits should appear in the recon panels. If they don't, the spatial path from latent → decoder cells → pix_out is still blocked at some layer.
- *Latent retention test:* `|μ(v1) − μ(v2)|` between distinct videos should be substantial — at least 0.1–0.3 — not the 0.0007–0.003 of runs 6/7. This is the "different videos compress to different latents" test.

Files touched in run 8 (for audit trail): `RViT_plus/latent.py` (complete rewrite, spatial sampler), `RViT_plus/decoder.py` (spatial-latent integration + remove broadcast), `RViT_plus/model.py` (`latent_channels` arg, accept legacy `latent_dim`), `RViT_plus/train.py` (content-weighting), `RViT_plus/tests/test_full_model.py` (updated for spatial latent shape), three analysis scripts (legacy `latent_dim` → `latent_channels`).

**This is the architectural commitment, not a hyperparameter.** Future sessions must NOT regress to a vector latent. The (batch, channels, H_mem, W_mem) shape is the foundational invariant of the program — the GAP-then-Linear shortcut is forbidden at any point in the pipeline, not just at the bottleneck. If a future task seems to require a vector latent (e.g., for cross-task transfer), the right move is to add a *separate* projection alongside the spatial latent, not to replace it.

### Three more architectural corrections from the user (2026-05-20, mid-run-8)

The user killed run 8 mid-training and issued three additional corrections that touched architectural commitments I had not honored:

1. *"If you have 3 layers of memory, the first layer could be `(n_channels_l1, H_l1, W_l1)`. The second could be `(n_channels_l2, H_l2, W_l2)`, where `n_channels_l2 > n_channels_l1` and `H_l2 < H_l1, W_l2 < W_l1`. Essentially, this gives decreasing spatial resolution, but increasing representational capacity. Sound familiar?"*

   I had grids `((12,12), (12,12), (6,6))` — C₁ and C₂ shared the same spatial resolution. The encoder's docstring justified this as "the key departure from HRA's 12→6→3 chain" because the HRA empirical finding had been that aggressive spatial reduction froze deeper layers. That was a workaround for an optimization issue, not a faithful implementation of the V1→V4→IT hierarchy. *Corrected to `((12,12), (6,6), (3,3))`* — clean halving, proper capacity-vs-resolution trade-off at each level.

2. *"You can keep almost everything in convolutional processing form. Why ever do something using a feed forward NN? Memory can be processed by conv networks."*

   The pre-correction `decoder.py` had `nn.Embedding(max_T, c1)` for `temporal_emb` plus `nn.Linear(latent_dim, stem_out_channels)` for the broadcast pathway. Both gone now. The decoder is fully conv: the latent enters through Conv1×1 channel adapter (preserves spatial grid), the pixel head is `ConvTranspose2d` mirror of `V1Stem`, the descend/ascend pyramid uses convs as in the encoder. *No `nn.Linear`, no `nn.Embedding` in the decoder.* (The `FeedbackTransformer`'s internal Linear projections remain — they are per-token operations functionally equivalent to Conv1×1 over the patch grid.)

3. *"For the decoder, you can just mirror our encoder architecture... we have multiple memory states already present. These are our initial conditions. Then you have a recurrent architecture unroll this backwards in time from the final point our encoder left off. This is a beautiful setup. Both the encoder and decoder can be nearly the exact same architectures. Conv transpose is the way to go for decoding from memory. The reverse decoding process could be: 1. Decode from memory the current visual state, use that next state to update the recurrent states, then decode the previous visual state. It is like a world model working backwards in time."*

   The pre-correction decoder was unrolling FORWARD in time with a learned `temporal_emb(τ)` as the per-step driving signal — a custom contraption I had invented rather than the structural mirror specified. The user's design is far more elegant and is now implemented as `RViTPlusVideoDecoder`:
   - Initialize D₁=C₁_final, D₂=C₂_final, D₃=`latent_to_d3(sample)` (spatial latent).
   - Loop τ = T-1 → 0:
     - Decode `x̂_τ = InverseV1Stem(D₁)` (the conv-transpose pixel head)
     - Stem the prediction: `V̂_τ = self.stem(x̂_τ)` — mirror of encoder's V1Stem
     - Run encoder-style update on (D₁, D₂, D₃) with V̂_τ as the bottom-up driver: same `descend_1to2`, `descend_2to3`, `ascend_*to*`, retinotectal skips, and `GridCellRNN_LSTM` cells as the encoder. n_FR inner iterations.
   - Reverse `recons` so `recons[t] = x̂_t` (source-time order).

   *The decoder IS the encoder, with its own predictions as the bottom-up sensory input, unrolling in reverse time.*

### Run 9: hierarchical memory + mirror-backwards decoder + all-conv (current, 2026-05-20)

All three corrections shipped together. Architecture summary:

  - **Encoder** (`encoder.py`): `GRID_HW = ((12,12), (6,6), (3,3))`. Stride-2 `descend_1to2` (12→6) and `descend_2to3` (6→3). Skip pathways `V → C₂` (12→6) and `V → C₃` (12→3 via two stride-2 descends). Ascend pathways `C₂ → C₁` (×2), `C₃ → C₁` (×4), `C₃ → C₂` (×2).
  - **Spatial VAE latent** (`latent.py`): Per-position Conv1×1 on `C₃` (the 3×3 deepest level). Sample shape `(B, 16, 3, 3)` — 144 dims, fully spatial. KL summed over `(latent_c, h₃, w₃)`. Free-bits at 2.0 nats per position prevents posterior collapse.
  - **Decoder** (`decoder.py`): `RViTPlusVideoDecoder` is a *structural mirror* of the encoder. Initialized from encoder finals + spatial latent sample. `InverseV1Stem` pixel head uses `ConvTranspose2d` to invert `V1Stem` exactly (12 → 25 → 50 with matching kernel/stride). Backwards-unroll: at each step τ, decode `x̂_τ` from D₁, stem it to V̂, run encoder-style cell update. The output sequence is reversed so `recons[t] = x̂_t`.
  - **Loss** (`train.py`): content-weighted L1 with `content_weight=10.0` (digit pixels weighted 10× over background) + free-bits KL.

**Param count: 1.81M** (up from 1.28M because the decoder has its own stem and pyramid; this is the natural cost of true mirroring).

**Smoke test (50 iters, batch=4):**
  - L1 descent: 0.77 → 0.10 over 50 iters. Run-7's smoke was 0.94 → 0.79 over the same span — an order-of-magnitude faster descent.
  - **`mse_t0` ≠ `mse_tT`** (0.038 vs 0.048 at iter 49). **First time across runs 5–8 that the decoder produces time-varying output.** This is direct evidence that the backwards-unroll dynamic is producing different reconstructions for different frames — proof that the recurrent dynamics carry time-dependent information.
  - KL = 180 nats (~1.25 nats per spatial position, below the 2.0 free-bits ceiling — latent is actively used).
  - 76/76 tests pass after the redesign (20 primitive + 56 full-model).

Full 2000-iter run launched 2026-05-20 ~22:00.

**Predictions for run 9:**
  - *P1:* genuinely tested for the first time. The FT must integrate spatial information at each layer for the cells to produce useful predictions of nontrivial frames. If attention entropy fails to drop below 0.80×max on at least one (layer, iter) cell, the architectural-program hypothesis (dense reconstruction develops FT structure) is in genuine trouble.
  - *P5 (visible recon):* digits should appear in the reconstruction panels with comparable contrast to inputs. The smoke test's L1=0.10 at iter 50 (vs run-7's L1=0.79 at the same point) and content-weighting suggests this should land.
  - *Time-varying recons:* `mse_t0 ≠ mse_tT` should remain true post-training. The backwards-unroll generates per-frame outputs that depend on the cell dynamics, not on a temporal-index lookup.

Files touched in run 9: `RViT_plus/encoder.py` (grid + skip pathways), `RViT_plus/decoder.py` (complete rewrite — `InverseV1Stem` + mirror-backwards forward), `RViT_plus/latent.py` (grid default), `RViT_plus/model.py` (latent_channels propagation), `RViT_plus/analysis/attention_entropy.py` (`layer_grid`), `RViT_plus/tests/test_full_model.py` (shape updates).

**Standing architectural invariants (do NOT regress):**

1. **Memory is spatial.** Every recurrent state is `(B, channels, H, W)`. No GAP, no flatten, no broadcast-from-vector anywhere in the pipeline.
2. **Layers hierarchy is V1 → V4 → IT.** Each successive layer has more channels AND less spatial resolution. The "C₁ and C₂ at same resolution" workaround from run 6 is forbidden.
3. **Decoder mirrors encoder.** Same cells, same descend/ascend pyramid, same retinotectal skips. The decoder is the encoder unrolled in reverse time with its own predictions as the bottom-up input.
4. **All-conv.** No `nn.Linear` (except inside `FeedbackTransformer` per-token projections, which are 1×1 conv equivalents). No `nn.Embedding` for memory or pixel pathways. No `Upsample+Conv` where `ConvTranspose2d` would do.
5. **Conv-transpose pixel head.** The pixel decoder is the architectural inverse of the V1 stem — same kernel sizes, same strides, same spatial arithmetic.

### Run-9 result: P1 falsified — but for a localized bug, not an architectural issue

Loss curve: L1 = 0.05 (iter 99) → 0.017 (iter 1999). KL ≈ 174 nats throughout (latent stays well-used, never collapses, free-bits ceiling never hit). No NaN, gn ≈ 1–2.

P1 verdict: encoder/decoder both at frac<0.80 = 0.0%, entropy/max ≈ 0.99 across all layers. Same uniform-attention signature as runs 5–8.

Numerical probe revealed the model converged to the same trivial-constant trap as run 7:

| Quantity | Value |
|---|---|
| Recon mean | -1.0007 (essentially predicting -1 everywhere) |
| Recon std | 0.0096 (basically zero per-pixel variation) |
| Pixel correlation with input | -0.002 (no content tracking) |
| L1 | 0.016 (= 1 + mean(input) = the L1 of predicting -1 everywhere) |

**But the architectural pieces themselves are working correctly.** Same probe also showed:

| Quantity | Run 7 | Run 9 |
|---|---|---|
| C₂ encoder spatial std | 0.042 | **0.075** (run-9 better) |
| C₃ encoder spatial std | 0.065 | **0.080** |
| **Decoder D₁ spatial_std (t=0)** | 0.017 | **0.047** |
| **Decoder D₁ spatial_std (t=9)** | **0.0001** (collapsed) | **0.045** (preserved!) |

The mirror-backwards decoder *preserves* spatial structure in D₁ across all T steps — the spatial-collapse problem of runs 5–8 is fixed at the architecture level. Run-7's D₁ went from 0.017 to 0.0001 over 10 forward-unroll steps; run-9's D₁ stays at 0.045 across all 10 backwards-unroll steps. The mirror-encoder cell architecture is doing exactly what it should.

So the failure mode is no longer architectural — it's the loss function, again. **Specifically: a bug in the content-weighting code from run 8 that I shipped into run 9 without verifying it actually worked.**

### The bug

`train.py` `compute_loss` had:

```python
digit_mask = (video.abs() > content_threshold).float()
weight = 1.0 + (content_weight - 1.0) * digit_mask
weight = weight / weight.mean().clamp(min=1e-6)
```

With MovingMNIST data in `[−1, 1]` where background = `−1` and digits = `+1`, `video.abs() > 0.5` is true for **every pixel** (because `|−1| = 1 > 0.5` too). Empirical check on a 4-batch sample:

  - Buggy mask: 99.6% of pixels flagged as "digit".
  - After normalization, all pixels get effective weight 1.0 → **content weighting is a no-op** → the loss reduces to plain L1.

Plain L1 on background-dominant data has its minimum at the median = `−1` (per the run-7 analysis already documented above). The model reproduced the run-7 result faithfully, with the architectural improvements visible at the encoder/decoder hidden states but invisible at the pixel output because the loss objective didn't pressure the model to learn digit content.

### Run-10 fix

```python
digit_mask = (video > content_threshold).any(dim=2, keepdim=True).float()
weight = 1.0 + (content_weight - 1.0) * digit_mask
weight = weight / weight.mean().clamp(min=1e-6)
```

  - `video > threshold` (no `abs`) — only flags pixels with values above 0.5 (the bright digit strokes).
  - `.any(dim=2, keepdim=True)` reduces across the RGB channel dim so at digit positions the whole RGB triple is weighted up consistently. Shape: `(B, T, 1, H, W)` broadcasts back across channels in the loss.

Verification on a 4-batch sample:
  - Fixed mask: 1.6% of pixels flagged as digit.
  - Normalized weight: bg ≈ 0.87, digit ≈ 8.74. Real ~10× weighting.

Predicting `−1` everywhere now costs weighted L1 ≈ 0.28 (vs. the buggy 0.013). The trivial-constant attractor is no longer the loss minimum.

Smoke test (50 iters, batch=4): L1 = 0.78 → 0.17. Slower descent than run-9 smoke (0.78 → 0.10) — expected, because the model now has to learn digit content rather than just match background. `mse_t0` (0.04) ≠ `mse_tT` (0.054) — backwards-unroll still producing time-varying output. KL stable at ~180 nats.

**Architecture untouched between run 9 and run 10.** All changes confined to `train.py` `compute_loss`. The architectural correctness of run 9 stands: encoder hierarchy, mirror-backwards decoder, spatial latent, all-conv, decoder D₁ preserves spatial structure across the unroll. The remaining question is whether the FT develops attention structure under a properly-weighted reconstruction loss. Full 2000-iter run 10 launched 2026-05-20 ~23:00.

**Lesson written into the wiki, not just my head:** verify the loss function actually penalizes what it's supposed to penalize, with numerical checks, *before* launching long training runs. The run-9 result superficially looked "converged" with a low L1, but the L1 was meaningless because the weighting that was supposed to make it discriminative was inactive.

### Run-10 result: content weighting active, model still stuck in trivial-constant attractor

Loss curve: L1 = 0.14 (iter 99) → 0.11 (iter 1999), plateau at ~0.10. Significantly higher than run-9's bogus 0.017 — confirming content weighting is now active. But P1 still falsified (encoder/decoder both at frac<0.80 = 0.0%) and reconstructions visually all-black.

Numerical probe revealed the model converged to predicting `-1` everywhere — *the trivial-constant minimum even under proper content weighting:*

| Quantity | Value |
|---|---|
| Recon mean | -1.0000 (constant -1) |
| Recon std | 0.0103 |
| Pixel correlation with input | 0.002 |
| Mean recon on background pixels | -1.000 (target -1, correct) |
| Mean recon on digit pixels | -1.000 (target +1, WRONG) |
| Weighted L1 | 0.088 |

Predicting -1 everywhere under the run-10 weighting (bg≈0.87, digit≈8.74) gives weighted L1 ≈ 0.09 — matching the observed value. The model is at this local minimum exactly.

But two more findings localize the *bottleneck*:

| Quantity | Value |
|---|---|
| Encoder C₁ spatial_std | 0.034 (carrying spatial info) |
| Encoder C₃ spatial_std | 0.082 |
| Latent μ std | 0.65 (active) |
| Decoder D₁ spatial_std (t=0) | 0.040 |
| Decoder D₁ spatial_std (t=9) | 0.038 (preserved!) |
| **`\|D₁(t=0) − D₁(t=9)\|`** | **0.020** (vs D₁.std = 2.13) |
| **convT_1 weight std** | **0.022** (vs init 0.02 — barely moved!) |
| convT_2 weight std | 0.084 (moved) |
| conv3_inv weight std | 0.060 (moved) |

Two distinct failure modes:

1. **The pixel-decoder final layer (`convT_1`) is stuck near init.** Other layers in the InverseV1Stem learned (convT_2, conv3_inv moved well above their init std), but the FINAL output projection didn't escape its small-Gaussian init. The bias moved to -0.023 (pulling toward -1) but the weight stayed at ~0.022 std.

2. **The decoder cells aren't time-differentiating.** `|D₁(t=0) − D₁(t=9)|` is < 1% of D₁'s total std — the cells produce essentially the same D₁ at every backward-unroll step. The mirror-encoder is *preserving* spatial structure (good), but not *evolving* it across time (bad).

**Diagnosis: bootstrap deadlock.** convT_1 can't move its weights until upstream signal differentiates digit pixels from background; upstream cells don't get differentiating gradient until convT_1 produces meaningful pixel output. Standard chicken-and-egg.

### Run 11: progressive curriculum (T=1 → T=2 → … → T=10)

User directive after run 10:

> *"Try the curriculum. Also, make sure you are NOT detaching gradients anywhere. The entire forward then backward should be one gradient pass."*

Then, after I initially shipped a hard T=1 → T=10 switch:

> *"Jumping from T=1 to T=10 is not curriculum. Curriculum is T=1, T=2, ... T=10"*

Both corrections shipped:

1. **Gradient audit (no leaks).** Audit of all `.detach()` and `torch.no_grad()` call sites in the model and training code:
   - `train.py`: `no_grad` only for the content-mask computation (data-derived, no gradient needed) and for the diagnostic MSE companion (not in loss).
   - `train.py`: `.detach()` only on `.item()` conversions for logging and on `per_t_mse`/`per_t_recon` stat-only tensors.
   - `memory.py`: `no_grad` only around bias-initialization (not in forward pass).
   - `encoder.py`: removed dead `z2.detach() if False else z2` code (always non-detached, but confusing).

   Forward and backward are a single gradient pass — confirmed clean.

2. **Progressive T curriculum.** Replaces the broken T=1→T=10 hard switch with a true ramp: each `T ∈ {1, 2, …, seq_len}` gets `warmup_iters / seq_len` iters before advancing. With `warmup_iters=1000` and `seq_len=10`: 100 iters per T stage, then the remaining 1000 iters at T=10 with the model already warmed up at every shorter length. Implementation in `train.py`: a `_T_at_iter(it)` function that returns `min(it // stage_iters + 1, seq_len)` during the warmup, then `seq_len` afterwards. The batch tensor is truncated to the current T along the temporal axis — no architectural change needed because the encoder and decoder are T-agnostic by design.

**Smoke test (60 iters, batch=4, seq_len=5, warmup_iters=25, 5 iters per T):**
  - T=1: L1=0.84 → 0.77 (iters 0-4)
  - T=2: 0.77 → 0.66 (iters 5-9)
  - T=3: 0.66 → 0.56 (iters 10-14)
  - T=4: 0.56 → 0.48 (iters 15-19)
  - T=5: 0.48 → 0.18 (iters 20-59) — full-T phase

The L1 drops smoothly through each T stage. By iter 24 (T=5 onset) the model is at L1=0.48, and by iter 59 (35 iters of T=5 training) it's at L1=0.18 — well below the trivial-constant baseline of 0.28.

Run launched: 2000 iters, batch=8, seq_len=10, warmup_iters=1000.

**Predictions for run 11:**
  - *Bootstrap escape:* `convT_1` weight std should grow beyond its 0.02 init during the T=1 phase (when the pixel decoder is the only thing being trained meaningfully). If it doesn't grow even with T=1, the pixel-output bottleneck is a deeper issue than a chicken-and-egg deadlock.
  - *Time-varying recons:* by the end of T=10 phase, `|D₁(t=0) − D₁(t=9)|` should be substantially > 0.02 (run-10's value). The backwards-unroll dynamic should engage once the pixel decoder gives the cells meaningful gradient.
  - *P1:* genuinely tested for the first time with a working pixel pathway. If attention is still uniform after curriculum + content-weighting + spatial latent + mirror-backwards decoder + hierarchical memory all working, the FT-collapse problem is robust and warrants direct intervention (e.g., explicit attention supervision).

### Run-11 result: curriculum partially works, but the trivial-constant attractor persists

| Quantity | Run 10 | Run 11 |
|---|---|---|
| L1 plateau | 0.107 | 0.107 (essentially identical) |
| `convT_1` weight std (final) | 0.022 | 0.022 (still at init!) |
| `\|D₁(t=0) − D₁(t=9)\|` | 0.020 | **0.130** (**6.5× larger** — cells now evolve) |
| Recon mean | -1.00 | -1.00 |
| Recon std | 0.0103 | 0.0105 |
| Pixel correlation with input | 0.002 | 0.001 |

The progressive curriculum *did* engage the backwards-unroll dynamic — `|D₁(t=0)−D₁(t=9)|` jumped from 0.020 to 0.130, indicating cells now evolve meaningfully across the 10-step unroll. But the *pixel-output bottleneck* survived even the T=1 phase: 100 iters of single-frame training failed to move `convT_1.weight` beyond its 0.02 init value.

### The pix-out cancellation pathology (run-11 final diagnosis)

Layer-by-layer probe of the InverseV1Stem on the trained run-11 model:

| Layer | Output std | Output range |
|---|---|---|
| D₁ (decoder cell) | 2.07 | [-4.5, 4.9] |
| after conv3_inv + GN + GELU | 0.61 | [-0.17, 2.61] |
| after convT_2 + GN + GELU | **0.58** | [-0.17, 2.82] |
| **after convT_1 (final, no activation)** | **0.0104** | **[-1.04, -0.66]** |

The std *drops by 56×* in the final layer. The expected output std if `convT_1`'s weights were random Gaussian at std=0.022 with input std=0.58 over a 5×5×32 receptive field would be `sqrt(800) × 0.022 × 0.58 ≈ 0.36`. The observed 0.0104 is **34× smaller than the random-init expectation**.

**The model learned weights that destructively cancel out** to produce near-constant output at the bias value. With:
- Input mean=-0.99, std=0.14
- Output (no activation) = `ConvT(input) + bias`
- Bias drifted to mean ≈ -0.025

The optimizer found that *cancellation* of the convolutional contribution + a near-zero bias gives nearly-constant output, which is the trivial-mean minimum the model can't escape. **The weights actively destructively interfere** — this is a learned pathology, not a failure to learn.

### User's diagnosis (handed to me, 2026-05-21)

> *"You can go with your recommendation, but I am worried you are missing something simple. For example, what is the range of pixels in the image. Then, what is the range of our outputs? Please double check how you are doing these type of things"*

The mismatch the user is pointing at:

- **Input range**: `[-1, 1]` (98.65% of pixels are exactly -1; 0.54% are above 0.5 — the bright digit strokes).
- **Output range**: *unconstrained* — `convT_1` is a raw linear projection with no activation, free to output any value. Observed range: `[-1.04, -0.66]` — the model squeezes itself near the bias rather than spanning the full input range.

The architectural fix: **add `tanh` on the InverseV1Stem output** so predictions are constrained to `[-1, 1]`. Two attractor regions (saturated -1, saturated +1) instead of one flat minimum at the bias. To hit exactly -1, the model must drive pre-activation strongly negative — this requires non-cancelling weights. To hit +1, strongly positive. The trivial cancellation pathology becomes structurally impossible.

### Run 12: tanh on the pixel output (current)

Single-line architectural change in `decoder.py`:

```python
# was: x_hat = self.convT_1(h)               # raw linear, range unbounded
# now: x_hat = torch.tanh(self.convT_1(h))   # constrained to [-1, 1]
```

Architecture otherwise identical to run 11 (hierarchical memory, mirror-backwards decoder, spatial latent, progressive curriculum, content-weighted L1). All 76 tests pass.

**60-iter smoke test signals dramatic immediate change:**

| Quantity | Run 11 (no tanh, final) | Run 12 (with tanh, smoke at iter 60) |
|---|---|---|
| Recon range | [-1.04, -0.66] | **[-0.99, -0.12]** |
| Recon std | 0.0103 | **0.093** (**9× higher**) |
| Recon mean | -1.00 | -0.90 |

Even with only 60 iters of training, the model is *no longer pinned to constant -1*. Pixel correlation is still near 0 at this early checkpoint (model has range to use but hasn't found content yet) — but the structural attractor is broken: the optimizer can no longer trivially "cancel itself to the bias." The full 2000-iter run will show whether content correlation develops once the model has actual range to predict in.

Full 2000-iter run-12 launched 2026-05-21 with progressive curriculum (warmup_iters=1000, 100 iters per T stage, then 1000 iters at T=10).

### Major redesign for run 13: drop the VAE + drop the backwards-unroll + decode from all memories

User directive 2026-05-21 (after seeing the layer-by-layer probe + tanh output add):

> *"1) It makes no sense to pass all recurrent states and only project one of them to a variational latent space. Let's just skip the stochastic latent projection for now. We will reintroduce this later if we get the autoencoder to work.
> 2) Why specifically decode from only D1? This again, makes no sense. Instead, let's try something more interesting.
> 3) Let's forgo the recurrent backwards unroll for now. Rather, first use conv transposes to bring every recurrent state up to the size of the input image. Then, concatenate them all along the channel dimension. Finally, use a moderate sized convolutional neural network to decode the concatenated memory states into the full video."*

The directive simplifies the decoder substantially. Rationale (mine, but the user clearly intended it): the previous design forced two hard problems on the model simultaneously — learn a stochastic VAE bottleneck AND a recurrent backwards-time generative dynamic. Both have known failure modes (posterior collapse, prediction-feedback bootstrap deadlock). Strip both, get a basic working autoencoder, then reintroduce them once the simple version works.

**New decoder (`RViTPlusVideoDecoder` in `decoder.py`):**

  1. Take encoder final states `(C₁: (B, 64, 12, 12), C₂: (B, 96, 6, 6), C₃: (B, 128, 3, 3))` directly — no VAE in between.
  2. Three `MemoryUpsamplePyramid` instances bring each Cᵢ to image resolution `(B, 32, 50, 50)` via stacked `ConvTranspose2d` layers:
       * C₁ (12×12 → 25×25 → 50×50) via two ConvT stages
       * C₂ (6×6 → 12×12 → 25×25 → 50×50) via three stages
       * C₃ (3×3 → 6×6 → 12×12 → 25×25 → 50×50) via four stages
     Each stage halves channels roughly. All-conv, no `nn.Upsample`.
  3. Concatenate the three upsampled feature maps along the channel axis → `(B, 96, 50, 50)`.
  4. A moderate 4-layer CNN (3×3 convs with GroupNorm + GELU, final 1×1 conv) decodes to `(B, T·3, 50, 50)`.
  5. Reshape to `(B, T, 3, 50, 50)` and apply `tanh` to bound the output to `[-1, 1]`.

  No recurrence in the decoder. No backwards-unroll. No temporal embedding. The temporal dimension is the output channel partitioning: each contiguous 3-channel slice of the CNN output corresponds to one frame.

**Model changes:**
  - `model.py`: removed `latent_sampler` (kept as `None` for back-compat); `compress_and_reconstruct` no longer samples a latent. `decode_sequence` no longer takes a `target_length` argument — `seq_len` is fixed at decoder construction time.
  - `train.py`: KL term is now 0 (no VAE). Curriculum disabled by default (`--warmup-iters 0`) since the curriculum existed to bootstrap the recurrent backwards-unroll, which is gone.
  - Tests updated: 52/52 in `test_full_model.py` pass.

**Param count: 1.52M** (down from run-12's 1.81M). Breakdown: encoder 813K, decoder 647K (`up_c1` 55K, `up_c2` 154K, `up_c3` 326K, CNN 112K), stem 58K. The deepest upsample pyramid (C₃ from 3×3) carries the most params because it goes through more upsample stages.

**Smoke test (50 iters, batch=4, seq_len=10):**
  - L1: 0.93 → **0.73** in 50 iters (smooth descent, no plateau).
  - `mse_t0 = 0.56, mse_tT = 0.51` — output is naturally time-varying because each frame is an independent slice of the CNN's output channels, not the same recurrent state recomputed.
  - No NaN, gn ~0.7, KL=0 (as designed — no VAE).

Full 2000-iter run launched 2026-05-21.

**Predictions for run 13:**
  - *Pixel correlation:* finally nonzero. The architecture is now structurally simple enough that if it can't produce digit content here, it can't produce it anywhere. This is the clean test of whether the encoder is capable of compressing video → spatial memory and whether a feedforward CNN can decode that back to pixels.
  - *Recon contrast:* `recon_video.std()` should be on the order of the input's 0.144, not run-12's 0.01. The tanh output combined with `convT_1` no longer being a single bottleneck (the CNN has multiple paths) should prevent the cancellation pathology.
  - *Visible digits:* `visualize_recon.py` should show recognizable digit content in the `recon` panels for the first time across all 13 runs. If this still produces all-black recons, the issue is deeper than architecture — it's an optimization-finds-easier-degenerate-solution problem.
  - *P1:* tested as a SIDE EFFECT now, not the primary objective. With the decoder no longer using the FT at all, only the encoder's FT is in play. If the encoder learns to use its FT meaningfully under reconstruction pressure, P1 confirms. If not, the FT-collapse problem is structurally robust and will need explicit attention supervision for Stage 1 of the program.

**Standing architectural invariants (continued from run-9), refined for run-13:**

1. **Memory is spatial.** Every recurrent state is `(B, C, H, W)`. No GAP, no flatten anywhere in the gradient path.
2. **Layers hierarchy is V1→V4→IT.** Each level has more channels AND less spatial resolution.
3. **All recurrent states feed the decoder, not just one.** Decoder fuses C₁ + C₂ + C₃ via upsample-and-concatenate.
4. **All-conv.** No `nn.Linear`, `nn.Embedding`, or `Upsample+Conv` in memory or pixel pathways.
5. **Output range matches input range.** `tanh` on the pixel decoder output to bound recons to `[-1, 1]`.
6. **VAE bottleneck and backwards-unroll are deferred.** Reintroduce after a working autoencoder demonstrates the encoder ↔ pixel decoder pathway can carry content.

### Run-13 result: worst trivial-output yet — tanh saturation killed the gradient

Loss curve: L1 = 0.93 (iter 9) → 0.10 (iter 499) → **0.078** (iter 1999). Looks like learning. But:

| Quantity | Value |
|---|---|
| recon range | **[-0.998, -0.997]** |
| recon std | **0.0002** (essentially zero) |
| recon mean | -0.998 |
| pixel correlation with input | -0.028 |
| **\|recon(v1) − recon(v2)\|.mean** | **0.0000** (different videos → identical recons) |
| gn at iter 1999 | **0.006** (gradient collapsed) |
| C₁ encoder spatial std | **0.111** (3× run-11's value) |
| C₃ encoder spatial std | 0.079 |
| **\|C₁(v1) − C₁(v2)\|** | **0.052** (5× run-10's value) |

The encoder is now doing **substantially more video-specific work** than any prior run (spatial std up 3×, inter-video discrimination up 5×). But the decoder output is the worst yet — every pixel locked at exactly `-0.998` regardless of input.

**Root cause: tanh saturation killed the gradient.** When the pre-activation pushed strongly negative (the model trying to hit bg = -1), `tanh`'s derivative `1 − tanh²(x) ≈ 0.004` at `tanh(x) ≈ -0.998`. Gradient was damped 250× through the tanh layer. The optimizer ratcheted the pre-activation more and more negative trying to reduce the digit-pixel error, but each step damped its own gradient further. By iter 2000, gn = 0.006 — the gradient is essentially zero and learning has stopped at the all-bg-saturated minimum.

The run-12 tanh introduction was the wrong fix to the convT_1 cancellation problem in run-11. tanh did break the cancellation pathology (run-13's `up_c3` weights are actively learning, gn was nonzero through training) — but introduced a new failure mode where the decoder locks into saturation.

### Run 14: linear output (remove tanh)

Single-line change in `decoder.py`:

```python
# was: recon_video = torch.tanh(out.view(...))
# now: recon_video = out.view(...)
```

Rationale: L1 gradient on linear output is `sign(error)` — constant magnitude regardless of how close the prediction is to the target. No saturation. The output may occasionally exceed `[-1, 1]` but the L1 loss treats that as any other mismatch and pulls it back.

The user's concern about "input vs output range mismatch" still stands — but the answer turns out to be NOT to constrain via activation, just to trust the loss to pull values into range. tanh is the wrong tool when most of your data is at the saturation boundary.

Architecture otherwise unchanged from run-13 (encoder hierarchy 12→6→3, upsample-and-concat decoder, no VAE, no curriculum, content-weighted L1).

**Smoke test (50 iters, batch=4):** L1 = 0.93 → **0.72** in 50 iters, gn stable at 0.78 (vs run-13's 0.73 — slightly higher gradient signal, no damping). Full 2000-iter run launched 2026-05-21.

**Predictions for run-14:**
  - *Gradient survives*: gn should stay above 0.05 throughout training instead of collapsing to 0.006. If the gradient survives but the model still produces constant output, the problem isn't the activation — it's somewhere else (e.g., the cancellation pathology returning).
  - *Recon std nonzero*: model should actually use the output range, not lock at a single value.
  - *Pixel correlation > 0.1*: the encoder's video-specific signal should make it to the output. If C₁ encodes content (verified: spatial std 0.11, inter-video Δ 0.05) and the decoder is not gradient-starved, the connection should land.

### Run-14 result: gradient survived, but model still chose trivial constant

| Quantity | Value |
|---|---|
| L1 plateau | 0.077 (vs run-13's 0.078 — essentially identical) |
| **gn at iter 1999** | **0.766** (vs run-13's 0.006 — **gradient survived** as predicted) |
| recon range | [-1.01, -0.99] |
| recon std | 0.0008 |
| pixel correlation | 0.05 (nonzero but tiny) |
| `\|recon(v1) − recon(v2)\|` | 0.0001 |
| C₁ encoder spatial_std | 0.073 |
| `\|C₁(v1) − C₁(v2)\|` | 0.026 |

Removing tanh fixed the saturation: gradient stayed alive (0.7-0.8) throughout training. But the model still converged to a near-constant output — just without the tanh-saturation mechanism this time. With healthy gradient, the model *actively chose* the constant-output local minimum.

**Diagnosis: content_weight=10 is too weak.** The L1 floor for predicting `-1` everywhere with content_weight=10 is ~0.093 (the 0.5% bright pixels contribute the only nonzero loss). Run-14 converged to 0.077 — only ~17% better than trivial constant. The 5% pixel correlation indicates the model *barely* started tracking content, but the gradient pressure to do more was insufficient.

### Run 15: content_weight=100 + MSE (current)

Two stacked changes, no architecture change:

1. **content_weight: 10 → 100.** Bright-pixel weight goes from 8.74× → 38.8× after normalization. Trivial-constant prediction now costs weighted L1 ≈ 1.0 (10× more painful than before). The model can no longer settle at the constant-output minimum.

2. **L1 → MSE.** MSE provides quadratic gradient: at digit-pixel error of 2.0, the gradient is 4× larger than L1's. Combined with content_weight=100, the effective gradient leverage at digit pixels is ~150× the leverage at background pixels (vs ~10× in run-14).

Both changes target the same problem: making the trivial-constant minimum *not* the optimization local minimum. Architecture (encoder hierarchy, upsample-and-concat decoder, linear output) untouched. Param count unchanged.

**Predictions for run-15:**
  - *Recon std should exceed 0.05* by iter 1000. This is the basic test of whether the model is producing varied output at all.
  - *Pixel correlation > 0.3* — if the encoder's content signal can actually reach the pixel output under stronger gradient pressure.
  - If run-15 still produces constant-output recon, the diagnosis points away from loss-tuning toward something deeper — most likely either the upsample pyramid's checkerboard/smoothing artifacts destroying spatial information, or the encoder's compression isn't actually content-preserving despite the spatial-std evidence.

### Run-15 result: **WORKING AUTOENCODER** — both predictions confirmed and then some

| Quantity | Run-14 | Run-15 | Multiple |
|---|---|---|---|
| Final MSE loss | 0.077 (L1) | 0.032 (weighted MSE) | — |
| **recon std** | 0.0008 | **0.241** | **301×** |
| recon range | [-1.01, -0.99] | [-1.67, +1.05] | width 268× |
| **pixel correlation w/ input** | 0.05 | **0.594** | **12×** |
| **\|recon(v1) − recon(v2)\|.mean** | 0.0001 | **0.102** | **1020×** |
| bg pixel recon mean | -1.00 | -0.99 (target -1, ✓) | — |
| **digit pixel recon mean** | -1.00 | **-0.17** | moved 83% of the way to target +1 |

The reconstructions show recognizable digit-like blobs at approximately correct positions with correct colors (red blob where the red digit is, green where the green is, both moving across frames). Resolution is blurry — the model is producing a low-frequency approximation of the digits — but for the first time across 15 runs, the autoencoder **is doing its job**: encoder compresses → spatial memory states → decoder reconstructs recognizable content.

### Run-15 also shows emerging FT attention structure (partial P1)

For the first time across 15 runs, the encoder's FeedbackTransformer attention is meaningfully non-uniform:

| Layer | mean entropy/max | frac<0.95 | Previous runs |
|---|---|---|---|
| C₁ (12×12, 144 tokens) | 0.92-0.93 | 95-100% | uniform (~0.999) |
| **C₂ (6×6, 36 tokens)** | **0.87** | 90-99% | uniform (~0.999) |
| C₃ (3×3, 9 tokens) | 0.94 | 37-44% | uniform (~0.998) |

Run-12's C₃ was at 0.988. Run-15's C₂ is at 0.867 — a real, structural drop. Not yet below the 0.80 threshold for full P1 confirmation, but the *trajectory* is correct: as the model learns to compress and reconstruct content, the FT begins to develop position-specific attention.

This is direct evidence for the architectural-program claim that dense reconstruction supervision (when properly set up) develops FT attention structure. Runs 5–14 falsified this because they were all degenerate (the model produced trivial constant output, so the FT had nothing to attend to). Run-15 is the first non-degenerate test.

(Decoder attention reports NaN — the run-13 decoder redesign removed the FT from the decoder, replacing it with a feedforward upsample+CNN. That's expected. To test decoder FT attention, the recurrent backwards-unroll decoder would need to be reintroduced.)

### Loss-function summary

The two-knob change in run-15 (`content_weight 10 → 100`, `L1 → MSE`) was the difference between a degenerate trivial-constant output and a working autoencoder. The architecture was correct since run-13. The loss objective was the missing piece.

Why it worked:
  - `content_weight=100` makes trivial-constant prediction cost weighted L1 ≈ 1.0 (vs 0.09 at cw=10). The constant-output local minimum is no longer cheaper than learning content.
  - MSE provides quadratic gradient — 4× stronger at the |error|=2 digit-pixel mismatches than L1's constant gradient. At equal content_weight, MSE gives the optimizer more leverage to find the steep digit-error regions of the loss landscape.

**Standing architectural invariants (continued from run-9), confirmed by run-15:**

The architecture established by run-13 is the working baseline:
1. Spatial memory `(B, C, H, W)` everywhere
2. V1→V4→IT hierarchy: 12×12/64ch → 6×6/96ch → 3×3/128ch
3. All recurrent states feed the decoder (upsample-and-concat — not just D₁)
4. All-conv: no Linear/Embedding in memory/pixel pathways
5. **Linear output** (no tanh — saturation kills the gradient when the data mean is at the saturation boundary)
6. **Content-weighted MSE** with weight_digit ≈ 100× weight_bg, threshold above 0.5 (only bright pixels flagged)
7. VAE bottleneck and recurrent backwards-unroll **remain deferred** — the working autoencoder can now serve as the baseline they'll be added on top of.

### Run-16 result: longer training sharpens recons substantially, P1 deepens

10k iters (vs run-15's 2k) at identical hyperparameters. Loss kept descending smoothly: weighted MSE 0.032 (iter 2k) → 0.020 (iter 5k) → 0.015 (iter 8k) → **0.012 (iter 10k)**. No plateau.

| Quantity | Run-15 (2k iters) | Run-16 (10k iters) | Change |
|---|---|---|---|
| weighted MSE loss | 0.032 | **0.012** | -63% |
| pixel correlation | 0.59 | **0.78** | +31% |
| recon std | 0.241 | 0.200 | small drop |
| **bright-pixel (target +1) recon mean** | (not measured directly) | **0.83** | new |
| R-bright recon | — | 0.88 (target +1) | — |
| G-bright recon | — | 0.72 (target +1) | — |
| bg-pixel (target -1) recon mean | -0.99 | -0.98 | unchanged |

The model has substantially improved at digit reconstruction. Bright pixels at digit positions go from a barely-moving -0.17 (run-15) to 0.83 (run-16) — 87% of the way to target +1. Reconstructions visually show recognizable colored digit shapes at correct positions across frames, with some residual blur but unambiguous content.

**P1 attention structure also deepened:**

| Layer | Run-15 entropy/max | Run-16 entropy/max | Run-16 frac<0.80 |
|---|---|---|---|
| C₁ (12×12, 144 tokens) | 0.92-0.93 | 0.93-0.94 | 0% |
| **C₂ (6×6, 36 tokens)** | 0.87 | **0.82-0.86** | **23-30%** |
| **C₃ (3×3, 9 tokens)** | 0.94 | **0.88-0.90** | **16-20%** |

Overall encoder frac<0.80 went from 1.4% → **13.8%** (10× increase). Not yet at the 50% bar for full P1 confirmation, but the deeper layers (C₂, C₃) show real, growing position-specific attention — and crucially, **C₂ and C₃ show MORE structure than C₁**, which is the biologically-expected ordering (V4 and IT analogs have more spatial selectivity than V1).

The architectural-program claim that dense reconstruction supervision develops FT attention structure is *no longer falsified*. It's now partially confirmed and trending toward full confirmation with more training.

**Trajectory across runs 5–16:**

| Run | Architecture/loss change | Key result |
|---|---|---|
| 5 | First video-compression mode | Total collapse, zero spatial variance |
| 6 | + pos_emb + SIP residual + update gate | Trivial-constant minimum (recon=-1.0 everywhere) |
| 7 | + spatial-VAE-on-vector latent | Same trivial-constant minimum |
| 8 | + content-weighting (buggy `abs()` mask) | Same — mask was no-op |
| 9 | Fixed mask, mirror-backwards decoder, hierarchy | Decoder cells preserve spatial info but constant output remains |
| 10 | Same with proper content-weighting | content_weight=10 too low — model at floor |
| 11 | Progressive T curriculum | Curriculum helps cell evolution, output still constant |
| 12 | + tanh output activation | Saturation kills gradient |
| 13 | Drop VAE + backwards-unroll, feedforward decoder | constant output via tanh saturation |
| 14 | Remove tanh | Gradient survives, but model still chooses constant minimum |
| 15 | **content_weight=100 + MSE** | **Working autoencoder, recons emerge, FT partial structure** |
| 16 | Same, 10k iters | **Sharp recons, frac<0.80 = 13.8%, target ≥ 50% in sight** |

The story is: architecture was correct since run-13; runs 14-15 were loss-function tuning; run-16 just needed more wall time. The combination `linear output + content_weight=100 + MSE + 10k iters` is the working baseline for Stage 1 of the program.

### Run-17 result: 30k iters at the run-16 settings — attention now content-tracking

Final loss **0.0058** weighted MSE (vs 0.012 at 10k, 0.032 at 2k). Loss kept descending smoothly for the entire 30k iters; no plateau. 30k iters took ~2.8 hours wall on MPS.

**P1 attention entropy:**

| Layer | iter | entropy/max | frac<0.80 |
|---|---|---|---|
| C₁ (12×12) | 0-3 | 0.92-0.94 | 0% |
| **C₂ (6×6)** | 0-3 | 0.80-0.85 | **18-47%** |
| C₃ (3×3) | 0-3 | 0.87-0.88 | 21-26% |

Overall encoder frac<0.80 = **19.7%** (run-16: 13.8%; run-15: 1.4%; runs 1-14: 0.0%). **C₂ at iter 1-2 hits 46-47% — just below the 50% threshold for full P1 confirmation, and trending up.**

**Reconstruction quality:** recons are clearly recognizable digits in correct colors at correct positions. Some residual edge blur. Pixel correlation appears to be 0.85+ (qualitative — not measured precisely in this analysis pass).

**Attention is now content-tracking (the key finding).** `RViT_plus/analysis/attention_maps.py` (new tool) generates three figures revealing the FT's learned attention structure:

  1. **`attn_recon_grid.png`** (input + recon + per-layer attention received, per frame, per sequence):
     - Sequence 0 (red 4 + green digit moving horizontally across frames): C₁ shows bright attention spots that SLIDE WITH the digits as they move. C₂ has a sharp single peak that follows the green digit's spatial position frame-to-frame.
     - Sequence 1 (red 0 top + green 9 bottom): C₁ concentrates in upper-right where the red 0 is, with the bright region sliding across frames. C₂ peaks at upper-right and slides consistently.

     This is the architectural-program claim made concrete: the FT has learned spatial attention that aligns with CONTENT POSITION. Not a generic center-bias; per-frame attention that tracks where the digits actually are.

  2. **`attn_dynamics.png`** (attention evolution across n_FR=4 inner iters for one frame):
     - C₁ attention SHARPENS and concentrates from k=0 → k=3 (the "attention trajectory" pattern the published Herman & Morgan 2025 RViT paper analyzed)
     - C₂ peak shifts position across iterations as cells refine their estimate
     - C₃ is stable (already converged at k=0)

  3. **`attn_summary.png`** (mean attention received over 16 sequences × 10 frames, per layer per iter):
     - C₁: roughly uniform with mild center bias (range 0.005-0.020 — small but structured)
     - C₂: strong horizontal middle-band — corresponds to where MovingMNIST digits typically appear in the data distribution
     - C₃: clear center bias

**Verdict:** the working autoencoder baseline established in run-13 + the loss-tuning of run-15 + the long training of run-17 produces:
  - A functional video autoencoder on MovingMNIST (recons recognizable, loss 0.006 weighted MSE)
  - **Content-tracking FT attention** in encoder C₁ and C₂ — the central interpretability claim of the architectural program
  - Position-specific attention selectivity that hierarchically increases at deeper layers (C₂, C₃ show more structure than C₁), consistent with the V1→V4→IT biological analog
  - C₂ at the 47% frac<0.80 threshold, full P1 (50%) plausibly reachable with more training or with the deferred VAE/recurrent-decoder components reintroduced.

The architectural-program hypothesis ("dense reconstruction supervision develops FT attention structure") is now empirically supported on Stage 1. Ready to reintroduce the deferred VAE + recurrent backwards-unroll, or scale up to Stage 2 (KTH/UCF101).

**New analysis tool added:** `RViT_plus/analysis/attention_maps.py` — generates the three figure types above. Three functions: `figure_recon_grid` (per-frame input/recon/attention), `figure_attention_dynamics` (per-iter evolution), `figure_attention_summary` (population average). All read from `out.encoder_attn_per_frame[t][k][L]` exposed in the model's `CompressionOutput`.

---

### RL phase — symmetry-breaking experiments and the PER breakthrough (2026-05-25)

Once the Stage-1 autoencoder was working (run 15–17), the next move was to attach the PPO + distributional QR-DQN critic on top of the pretrained encoder and run Posner change-detection. Run-18 was the first RL run; runs 19–28 covered an extended sequence of attempts to keep the actor from collapsing to a deterministic single-action policy. *None of the symmetry-breaking interventions tried during this stretch held up; PER is the first that did.* This section catalogs what failed and why, then documents the PER finding.

**The collapse mode the entire RL phase has been trying to escape.** Within ~100–300 iterations of RL onset, the actor's logits collapse to a single deterministic action (typically "wait"), entropy `H[π(·|s)] → 0`, and the encoder's internal state diversifies very little across timesteps (the recurrent cells reach a near-fixed-point under nearly constant input). Once collapsed, the system has no exploration signal to break out: there is no on-policy data on the unchosen action, so the critic's `Q(s, a_other, :)` is uninformed, and any mechanism that depends on critic disagreement to drive exploration is starved.

**Mechanism 1: adaptive certainty-decay (σ branch).** The first attempt added a dedicated 4th C₃ specialist `cell3_sigma` and a `SigmaHead` reading `(C₁, C₂, C₃_σ)`, producing a per-state logit `f_σ` with `σ = sigmoid(f_σ + 2.0)` as a "should I encourage exploration here?" gate. An L1 penalty on `f_σ` kept σ near its default (≈ 0.88) unless the network had a reason to deviate. Several formulations of *what* σ should gate were tried: (a) σ-weighted critic spread reward (mistakenly framed as a reward, pinned σ to ≈ 1); (b) σ-weighted expected critic uncertainty under π as an actor pull (worked mechanically but couldn't break the actor's existing collapse); (c) σ-weighted *positive* critic over-certainty penalty on unchosen actions (correct sign, but the gradient on σ_head was either too weak to deviate σ from default or, in poorly-tuned coefficient regimes, drove σ to 0 deep enough to NaN the recurrent state on padded inputs). All three variants were ablated. The σ branch was retired in full on 2026-05-25.

**Mechanism 2: intrinsic UCB exploration via critic uncertainty.** Added `loss_ucb = -c · E_{a ~ π}[std(Q(s, a, :)).detach()]` as a policy-shaping term — the action-selection analog of UCB1, where the critic's quantile spread directly biases the policy toward uncertain actions. Initial implementation was inverted (adding `c · std(Q(s, a_t))` to the executed action's advantage), which has zero effect when the actor never picks the uncertain action; corrected version was the expected-std term above. Even with the corrected formulation, the policy did not escape its collapse — `std(Q(s, a_wait))` was small for all states, and `std(Q(s, a_press))` was a noisy artifact of an untrained head, so the bonus contained almost no useful signal. Retired with the σ branch.

**Mechanism 3: contrastive auxiliary losses on encoder state.** Two SimCLR-style projection heads (one per actor/critic branch) tried to shape the encoder's internal representations directly. Actor head used binary pair labels (same action AND same reward → attract; otherwise repel below cosine margin). Critic head used continuous weights (`|err_i − err_j|` repel, `cos(Q_i, Q_j)` attract). Several variants tried: full state triplet `(C₁, C₂, C₃_X)` as input, then restricted to the unique specialist `C₃_X` only to avoid putting conflicting pressure on shared C₁/C₂. The contrastive losses are *mathematically correct* — when the embedding collapses (`cos+ = cos- = 1`), the loss is exactly the margin term `1 − 0.5 = 0.5`, and the gradient signal is non-zero — but in practice the encoder cannot break the cos = 1 attractor because every (b, t) pair in the batch has the same (action, reward) class once the actor collapses. Tried higher coefs, tighter margins, single-cell input, separate heads, GroupNorm-based projection heads — all hit the same wall. **Contrastive losses by themselves do not break symmetry in the regime where the upstream policy is already collapsed.**

**Mechanism 4 (the one that worked so far): prioritized episode replay (PER).** Added an `EpisodeReplayBuffer` of capacity ~200 episodes alongside the on-policy PPO loop. Each PPO update augments the fresh `episodes_per_iter = 8` on-policy batch with `per_n_replay = 4` episodes sampled from the buffer, with sampling probability `p_i ∝ priority_i^α` (`α = 0.6`) and importance-sampling weights `w_i = (1 / (N·p_i))^β` linearly annealed `β: 0.4 → 1.0`. Priority is per-episode mean quantile-Huber error, refreshed each time the episode contributes to an update (standard PER convention, Schaul et al. 2016). Per-episode IS weights flow into every masked-mean loss term (policy, value, entropy, recon) via `μ_{b,t} = m_{b,t} · ŵ_b`. PPO's clip range absorbs mildly stale-policy samples automatically (their policy-gradient contribution is zeroed when `r_{b,t}` falls outside `[1−ε, 1+ε]`), so the only correction needed is the IS weight on the off-policy loss terms.

**Why this works (preliminary hypothesis).** The collapse mode is fundamentally a *batch-composition* problem: a fresh on-policy batch from a deterministic actor contains only (a_wait, *) transitions, so the contrastive losses have no positive/negative pair structure to learn from, the value loss has no signal on the unchosen action's `Q(s, a_press, :)`, and the policy gradient has no advantage on actions it has never tried. Persistent replay holds past episodes from when the actor *did* explore — including ones with rare (press, +1) outcomes from very early training — and re-injects them into every update with priority by Q-error. This:

  1. Restores pair diversity in the contrastive losses (some (a, r) classes only exist in the buffer at this point);
  2. Continues to refresh the critic's `Q(s, a_press, :)` predictions via quantile-Huber on replayed press transitions;
  3. Keeps representational pressure on the encoder for state-distinguishing features beyond what the current policy visits.

**Empirical signature (2026-05-25, preliminary, ~few-thousand iters horizon).** PER is the first mechanism in the RL phase that **breaks the symmetry of the encoder's internal representations** (contrastive cos+/cos− diverges from the (1, 1) collapse) **and holds the actor's output entropy above the deterministic-collapse floor**. Every earlier mechanism either had no discernible effect, collapsed the actor within `O(10²)` iterations, or pinned the auxiliary gate to its boundary. This is preliminary — long-horizon training under PER has not yet been characterised — but the qualitative behaviour is unambiguously different from every prior intervention.

**Companion observation: gradient-magnitude restoration.** During the collapse regime (all pre-PER mechanisms), `gmax` (max-absolute gradient element across all parameters) was on the order of `10⁻²`. Once PER is active and the contrastive cos+/cos− has separated, `gmax` settles in the `10²–10³` range — a roughly `10⁴-10⁵×` increase. This is *not* a sign of instability: the two-stage gradient clip (per-element cap at `1e6` and L2-norm cap at `0.5`) handles these magnitudes, and `loss_policy`, `loss_value`, `loss_recon` all remain bounded. Rather, it reflects that the collapsed batch produced essentially no contrast signal — pairs were all-positive (same action, same reward), the value loss had no novel transitions to fit, and the per-step quantile-Huber error was uniformly small. PER reintroduces diverse, informative transitions into every update, and the optimizer's gradient magnitude is restored to the regime characteristic of an actively-learning network rather than a network sitting at a flat collapse point. This restoration tracks the contrastive-cosine separation 1:1 across iterations: when the buffer warms up and replay episodes start contributing diverse (action, reward) pairs, `gmax` jumps and `cos+ / cos−` diverges in the same window.

**Status.** PER is now the **default RL training configuration** (`per_n_replay = 4` in the config). The σ branch, UCB term, and the contrastive-only attempts (without PER) are retired from the active training stack. The mathematical specification of the buffer, sampling distribution, IS correction, and the algorithm is written up in `RViT_plus/docs/per_buffer.pdf` (section "Empirical Observation"). All buffer + IS-weight code lives in `RViT_plus/ppo.py` (`EpisodeReplayBuffer`, `concat_batches`, weighted-mean losses keyed by `batch.sample_weights`).

**Follow-up observation: the contrastive losses are competing, not embedding permanent structure (2026-05-25, post-PER).** On a model that had been training under PER + contrastive auxiliaries for several hundred iterations and was holding its non-collapsed state, *reducing the contrastive coefficients* caused the system to **rapidly re-collapse**: actor entropy dropped back toward zero, cos+/cos− re-merged toward (1, 1), gradients shrank again. If the contrastive losses had been building up a permanent representational structure in the encoder, removing them should have left the encoder in roughly the same state for at least a number of iterations. Instead the collapse was nearly immediate.

Interpretation: the contrastive losses do not appear to be *teaching* the encoder a stable invariant. They are providing a continuous *counter-pressure* against something else in the loss landscape that, when the pressure relaxes, snaps the system back to its preferred fixed point. The "something else" is likely the joint of (a) the policy-gradient term collapsing toward whichever action is locally lowest-loss and (b) the value-loss term being trivially solved at the collapse point (homogeneous Q means small per-step error). The contrastive cos+/cos− separation we observe under steady-state training is therefore a *dynamical equilibrium* between an actively-applied separation pressure and a passively-applied collapse pressure — not a representational achievement that persists when one party is removed.

This shifts the working hypothesis for the next intervention: rather than continuing to crank the contrastive coefficient (which would just push the equilibrium further from collapse without removing the underlying collapse attractor), we should add a loss term that operates on the encoder's *dynamics* — a constraint the encoder must satisfy regardless of the actor/critic behavior — so that even if the actor degenerates, the encoder still has a structural reason to differentiate states across time. The candidate being added next is a predictive-coding auxiliary: at each timestep `t`, the actor's and critic's deep specialist state at `t-1` must predict the shared middle state at `t` (cosine similarity between a learned projection of `C_{3, X, t-1}` and `C_{2, t}`). This is a temporal-consistency constraint that exists independently of action / reward labels and should therefore not be dependent on the actor having any particular behavioral structure.

---

### Working baseline (2026-05-25): PER + contrastive + PC + PAC actor loss — task competence confirmed

After the chain of failed symmetry-breaking attempts catalogued above, the configuration that produces **sustained task competence** on Posner change-detection combines **four** mechanisms, each addressing a distinct failure mode that surfaced during the RL phase:

| Mechanism | Failure mode addressed | Role in the baseline |
|---|---|---|
| Prioritized episode replay (PER) | Batch-composition collapse: a deterministic actor produces all-`(wait, 0)` batches with no learning signal for unchosen actions or rare rewards. | Maintains diverse `(state, action, reward, outcome)` tuples from past iterations; concentrates sampling on episodes the current critic still finds surprising. |
| Contrastive auxiliaries | Encoder state symmetry across timesteps under repetitive input. | Continuous separation pressure on `(action, reward)` pair structure in `cell3_actor` / `cell3_critic`. Empirically a *dynamical counter-pressure* (removing it collapses the system in ~50 iters) rather than a permanent achievement. |
| Predictive coding (PC) | Encoder dynamics with no representational constraint independent of behavioral labels. | `P_X(C_{3, X, t-1})` predicts `C_{2, t}.detach()` via cosine. A temporal-consistency constraint that survives actor collapse — provides the "underlying structure" the contrastive losses fail to embed. |
| PAC actor loss (MPO + BC) | Under PPO's clipped surrogate, Q's per-action structure was routed only through a scalar V baseline — the action-conditional critic was vestigial. | Replaces PPO surrogate. Q drives the actor directly via the MPO E-step weights `q(a\|s) ∝ π_old(a\|s)·exp(Q̄(s,a)/η)`. |

**Empirical signature at iter ≈ 1450–1670, sustained > 200 iterations (run of 2026-05-25):**
- `correct ≈ 0.70–0.78` (chance = 0.5 on binary detection)
- `return ≈ 2.1–2.3` per episode
- `len ≈ 22–28` out of `seq_len = 29` — actor is timing presses, not pressing randomly or never
- `H[π] ≈ 0.01–0.04` — committed policy, not deterministic-collapsed
- `pcCos ≈ +0.94–+0.96` — encoder dynamics genuinely predictable
- `gmax ≈ 10⁻³ – 10⁻¹` — stable, no overflow, no vanishing
- `buf = 200/200` populated, `β ≈ 0.85–0.90` (PER IS exponent in steady-state regime)
- `+rep = 4` every step (replay augmentation active)

This is the **first model in the program to exhibit sustained Posner-task competence** without any hardcoded exploration schedule. The only prior working model in the larger architectural program is PRISM v1, which required hardcoded epsilon-greedy. The present setup achieves the same task signature with purely principled losses + PER replay.

#### The total per-update loss

Over the combined (fresh + replay) batch:
$$
\mathcal{L} \;=\; \mathcal{L}_\text{actor}^\text{PAC} \;+\; c_v\,\mathcal{L}_\text{value} \;+\; c_e\,\mathcal{L}_\text{entropy} \;+\; c_r\,\mathcal{L}_\text{recon} \;+\; c_\text{ac}\,\mathcal{L}_\text{con,actor} \;+\; c_\text{cc}\,\mathcal{L}_\text{con,critic} \;+\; c_\text{pa}\,\mathcal{L}_\text{PC,actor} \;+\; c_\text{pc}\,\mathcal{L}_\text{PC,critic}
$$

Every masked mean uses the IS-weighted effective mask
$$
\mu_{b,t} \;=\; m_{b,t}\cdot \hat w_b
$$
where `m_{b,t}` is the per-step valid mask and `ŵ_b` is the per-episode PER IS weight (`ŵ_b = 1` for fresh episodes, the PER weight for replay).

##### PAC actor loss (replaces PPO clipped surrogate)

For discrete actions the MPO E-step is closed-form. Define
$$
\bar Q(s, a) \;=\; \frac{1}{N}\sum_{i=1}^{N} Q(s, a, \tau_i),\qquad N = 51,
$$
with `.detach()` on Q so the actor loss does *not* train the critic. With `π_old(·\|s)` reconstructed from the stored `log π_old(a_t\|s)` (closed-form for `n_actions = 2`):

E-step (target distribution, fully detached):
$$
q(a\mid s) \;=\; \mathrm{softmax}_a\!\Bigl[\log \pi_\text{old}(a\mid s) \;+\; \bar Q(s, a)\, /\, \eta\Bigr]
$$

M-step + BC blend:
$$
\boxed{\;\mathcal{L}_\text{actor}^\text{PAC} \;=\; -\mathbb{E}_{(s, a_t)}\!\Bigl[(1-\alpha) \sum_a q(a\mid s)\,\log \pi_\theta(a\mid s) \;+\; \alpha\,\log \pi_\theta(a_t\mid s)\Bigr]\;}
$$

Gradient enters `π_θ` exclusively via `log_softmax(logits_t)`. Both `Q̄.detach()` and the final `q(a\|s).detach()` cut all gradient paths into Q and the target distribution.

##### Distributional value loss (quantile-Huber, QR-DQN-style)

Per (s, a_t) the critic predicts a 51-quantile distribution `Q(s, a_t, τ)`. TD target:
$$
y_t \;=\; r_t \;+\; \gamma\, V_\text{dist}(s_{t+1})\,(1 - d_t), \qquad
V_\text{dist}(s) \;=\; \sum_a \mathrm{sg}[\pi_\theta(a\mid s)] \cdot Q(s, a, :)
$$
(expected SARSA with stop-gradient on π, per `Q_CRITIC.md` §2.4).

Quantile-Huber loss per quantile pair `(i, j)`:
$$
\ell^\text{QH}_{ij} \;=\; \bigl|\tau_i - \mathbf{1}\{\delta_{ij} < 0\}\bigr|\cdot \ell_\kappa(\delta_{ij}), \qquad \delta_{ij} = y_j - q_i,\quad \kappa = 1.0
$$
where `ℓ_κ` is the standard Huber loss. Per-step reduction:
$$
\rho^\text{QH}_{b,t} \;=\; \frac{1}{N^2}\sum_{i,j} \ell^\text{QH}_{ij}(b, t)
$$

$$
\mathcal{L}_\text{value} \;=\; \frac{1}{\sum_{b,t}\mu_{b,t}}\sum_{b,t} \mu_{b,t}\,\rho^\text{QH}_{b,t}
$$

The same `ρ^QH_{b,t}` is also the per-episode PER priority signal (averaged over valid timesteps).

##### Reconstruction auxiliary

Content-weighted MSE on the decoder's per-frame reconstruction. Pixel weights
$$
w_p \;=\; 1 + (c_\text{cw} - 1)\cdot \mathbf{1}\{|x_p| > \text{thr}\},\quad c_\text{cw} = 100,\quad \text{thr} = 0.5
$$
so digit pixels weighted 100× over background:
$$
\mathcal{L}_\text{recon} \;=\; \frac{1}{\sum \mu_{b,t}\,w_p}\sum_{b, t, p} \mu_{b,t}\cdot w_p \cdot (\hat x_{b,t,p} - x_{b,t,p})^2
$$

##### Entropy bonus

$$
\mathcal{L}_\text{entropy} \;=\; -\frac{1}{\sum \mu_{b,t}}\sum_{b,t} \mu_{b,t}\,H[\pi_\theta(\cdot\mid s_{b,t})]
$$

##### Contrastive auxiliaries (separate projection heads per branch)

Per branch X ∈ {actor, critic}, a SimCLR-style head `g_X`: `(c_3, 3, 3) → ℝ^{128}` (L2-normalised). Pairwise cosine `c_{ij} = ⟨z_i, z_j⟩` over the flattened (b, t) batch, restricted to valid steps.

Actor (binary pair labels — same action AND same reward → positive; else negative):
$$
\mathcal{L}_\text{con,actor} \;=\; \mathbb{E}_\text{pos}[1 - c_{ij}] \;+\; \mathbb{E}_\text{neg}\!\bigl[\,\text{relu}(c_{ij} - m_\text{margin})\,\bigr],\quad m_\text{margin} = 0.3
$$

Critic (continuous weights, both `.detach()`-ed):
- Repulsive weight `r_{ij} = |\rho^\text{QH}_i - \rho^\text{QH}_j|`.
- Attractive weight `a_{ij} = \text{relu}(\langle \hat Q_i, \hat Q_j \rangle)`, `\hat Q` = L2-normalised flat Q-distribution.

$$
\mathcal{L}_\text{con,critic} \;=\; \mathbb{E}\!\bigl[a_{ij}(1 - c_{ij})\bigr] \;+\; \mathbb{E}\!\bigl[r_{ij}\cdot\text{relu}(c_{ij} - m_\text{margin})\bigr]
$$

Gradient flows only through `z` → encoder + projection head. Q and per-step error are detached.

##### Predictive-coding auxiliaries

Per branch X, a small upsampler `P_X`: `(128, 3, 3) → (96, 6, 6)`. The C₂ target is detached, isolating actor and critic branches even though C₂ is shared:
$$
\boxed{\;\mathcal{L}_\text{PC,X} \;=\; \mathbb{E}_{b, t \geq 1}\!\Bigl[\mu_{b,t}\cdot \bigl(1 - \cos\!\bigl(P_X(C_{3,X,t-1}),\ C_{2,t}.\mathrm{detach}()\bigr)\bigr)\Bigr]\;}
$$

##### PER buffer

FIFO ring of episodes, capacity `C_\text{buf} = 200`. Per-iteration:
1. Sample `n = 4` episodes with `p_i \propto \tilde p_i^\alpha`, `α = 0.6`, where `\tilde p_i = \min(p_i,\, c_\text{clip}\cdot \mathrm{median}(p))`, `c_\text{clip} = 50`.
2. IS weight `\hat w_i = (1/(N\cdot p_i))^{\beta(t)} \big/ \max_j \hat w_j`, with `β` linearly annealed:
$$
\beta(t) \;=\; \beta_0 + (\beta_1 - \beta_0)\cdot \min(t/(T_\text{train}-1), 1),\quad \beta_0 = 0.4,\ \beta_1 = 1.0
$$
3. Concatenate `fresh ∥ replay` into one batch.
4. Run PPO update (n_epochs = 4) on the combined batch.
5. Refresh sampled-replay priorities with post-update `p_b = (\sum_t m_{b,t}\,\rho^\text{QH}_{b,t}) / (\sum_t m_{b,t})`.
6. Push fresh episodes into the buffer with their post-update priorities.

#### Hyperparameter table (working baseline, 2026-05-25)

| Group | Parameter | Value |
|---|---|---|
| **Training** | `iters` | 2000 |
| | `episodes_per_iter` | 8 fresh |
| | `seq_len` | 29 |
| | `lr` | 3e-4 |
| | `n_epochs` (per PPO update) | 4 |
| | `recon_pretrain_iters` | 50 |
| | `grad_clip` (L2 norm) | 0.5 |
| | `grad_value_clip` (per-element) | 1.0e3 |
| **Architecture** | `state_channels` | (64, 96, 128) |
| | `n_FR` (legacy; encoder uses 1 pass) | 4 |
| | `n_heads` | 4 |
| | `enable_skips`, `skip_scale` | true, 0.3 |
| | `upsample_out_channels`, `cnn_hidden` | 32, 64 |
| | `n_quantiles` (N) | 51 |
| | `n_actions` | 2 |
| | `init_action_bias` | [0.0, -1.5] |
| | `split_c3` | true (cell3_actor, cell3_critic) |
| | `contrastive_projection_dim` | 128 |
| **Critic / discounting** | `gamma` (γ) | 0.95 |
| | `qr_kappa` (κ) | 1.0 |
| | `gae_lambda` | 0.95 (retained; unused under PAC) |
| | `clip_range` | 0.2 (retained; unused under PAC) |
| **Loss coefficients** | `value_coef` (c_v) | 0.5 |
| | `entropy_coef` (c_e) | 0.1 |
| | `recon_coef` (c_r) | 0.5 |
| | `content_weight` (c_cw) | 100.0 |
| | `recon_kind` | mse |
| | `contrastive_actor_coef` (c_ac) | 0.5 |
| | `contrastive_critic_coef` (c_cc) | 0.5 |
| | `contrastive_margin` (m_margin) | 0.3 |
| | `pc_actor_coef` (c_pa) | 0.1 |
| | `pc_critic_coef` (c_pc) | 0.1 |
| **PAC actor** | `mpo_temperature` (η) | 0.1 |
| | `bc_alpha` (α) | 0.1 |
| **PER buffer** | `buffer_capacity` | 200 |
| | `per_n_replay` | 4 |
| | `per_alpha` (α_PER) | 0.6 |
| | `per_beta_start` → `per_beta_end` | 0.4 → 1.0 |
| | `per_priority_clip` (c_clip) | 50.0 |

#### Why this works (current understanding)

Each mechanism addresses a distinct failure mode encountered along the path to this configuration:

1. **PER buffers diverse experience.** A collapsed actor produces a fresh batch with no informative pairs for the contrastive losses, no off-policy transitions for the critic, and no rare-reward signal for the policy gradient. The buffer holds past data from when the policy was more diverse, and PER's priority weighting concentrates sampling on episodes the current critic finds most surprising — which empirically correlates with the rare-reward `(press, +1)` events.

2. **Predictive coding constrains encoder dynamics independent of behavior.** Even if the actor briefly degenerates, the PC term still forces `cell3_X` to encode information about the next-step `C_2`. The encoder retains a non-vanishing gradient signal that does *not* depend on actor or reward labels and cannot be silenced by behavioral collapse.

3. **Contrastive auxiliaries provide pair-level structure.** Necessary but not sufficient: removing them on a trained model collapses the system within ~50 iterations, but contrastive *alone* (no PC, no PAC) cannot prevent the initial collapse. They are *locking in* what PC + PAC + PER establish.

4. **PAC actor loss puts Q to work.** Under PPO's clipped surrogate the action-conditional structure of Q was vestigial; the actor only saw a scalar V baseline. Under MPO + BC, the relative `Q̄(s, a=press) − Q̄(s, a=wait)` directly shapes the policy target `q(a\|s)` via softmax-with-temperature `η = 0.1`. Improvements in the critic translate directly to improvements in the policy.

The combination is what cleared collapse. We have no evidence that any strict subset would have sufficed.

#### Open questions

1. Does this configuration sustain past iter 2000? The current observation window is ~200 iters of steady-state behavior; the next experiment is a longer run.
2. Stage 5 of the curriculum (microstim + RSA against IT cortex) requires the model to be doing the task — that gate is now passed, so Stage 5 is the next milestone.
3. Ablation order to confirm each mechanism is necessary: (a) PER off → expected: collapse; (b) PC off → expected: contrastive becomes counter-pressure again, eventual collapse; (c) PAC reverted to PPO → expected: actor stops responding to per-action Q differences; (d) contrastive off → expected: collapse within ~50 iters from a trained checkpoint. None of these have been run yet — they're the next batch of experiments.

### Channel-softmax collapse — progression ladder for interventions

As of iter ≈ 2200 (cumulative training across resumed runs), the per-head channel softmax `A` in the conv-spatial attention block has converged to a one-hot routing decision at every layer. Layer 1 and Layer 2 are at the fp32 numerical floor (entropy ≈ 1e-9, indistinguishable from a hard top-1). Layer 3 was briefly broader earlier in training — at iter ≈ 1999 the L3 softmax entropy spiked from ~1e-4 to ~1.0 at the action moment in random episodes (interpreted as the network reaching for additional V-channels at the decision boundary). After ~200 more iterations of continued training this L3 broadening is no longer visible in forced-trial diagnostics; press-time entropy at L3 has dropped to ~6e-4 (a ~1700× reduction relative to the iter-1999 random-episode value, with the caveat that the iter-1999 forced trial wasn't dumped at the time).

Whether this is a problem worth fixing depends on three concerns: (i) loss of action-moment representational dynamics (the L3 broadening was the cleanest interpretability signal in the model and is now gone); (ii) potential brittleness to distribution shift since the routing decision is now context-independent; (iii) architectural-design mismatch — channel attention assumes context-dependent routing and currently has none. Concerns (i) and (iii) are aesthetic / interpretability-flavored; (ii) is empirically testable and is the basis for the diagnostic below.

The following interventions form a progression from least to most invasive. We do not commit to running all of them; the goal is to record the option set so that if the chosen path doesn't work we have a documented escalation rather than ad hoc reinvention.

**Step 0 — Diagnostic before intervening.** Re-run the forced-trial attention analysis with `proportion=0.25` (low-validity cue, model should be uncertain about where the change will appear). If L3 softmax entropy at the press frame is still ≈ 1e-3 or lower, the collapse is genuine and unconditional — proceed to Step 1. If L3 entropy spikes on the hard trial (matches the iter-1999 random-episode signature), the collapse is trial-difficulty-dependent and possibly does not need an intervention at all.

**Step 1 — Entropy regularization on the channel softmax.** Add to the total loss
$$
\mathcal{L}_\text{softmax\_ent} \;=\; -c_\text{se}\cdot \frac{1}{n_\text{layers}\,n_\text{heads}} \sum_{\ell, h} H\bigl[A_{\ell, h}\bigr]
$$
with `c_se` ~ 0.01 (small relative to the task losses). The optimizer gets a constant outward push on the softmax that resists collapse but does not dominate. One-line implementation in `ppo_update`. Annealable if needed. **Failure mode:** if `c_se` is too large the optimizer fights it and the task losses degrade; if too small, no observable change. Tune `c_se` over `{0.01, 0.05, 0.1, 0.5}` if the first value is ineffective.

**Step 2 — Bounded-temperature softmax.** Replace `A = softmax(scores)` with `A = softmax(scores / τ)` where `τ = τ_min + (τ_max − τ_min) · sigmoid(raw_τ)` and `raw_τ` is a learnable scalar per-layer-per-head. With `τ_min = 0.5, τ_max = 2.0`, the softmax cannot sharpen past `1/τ_min = 2`. **Pro:** doesn't fight the optimizer; the optimizer chooses where in the allowed range to sit. **Con:** changes the attention module's parameter count; existing checkpoints load as warm-start only on the affected layers.

**Step 3 — Sigmoid instead of softmax.** Drop the per-head softmax entirely. Replace with `A = sigmoid(scores)` so each channel has an independent gate in `[0, 1]` with no competitive normalisation. This structurally eliminates the source of collapse (the "compete for unit mass" constraint). The mechanism becomes a channel-wise gated-additive block rather than channel attention. **Pro:** rules out softmax collapse by construction. **Con:** sigmoid gates can independently saturate (~0 or ~1) so we may have replaced one collapse mode with another. Also changes the mechanism's interpretation enough to warrant a re-derivation in the writeup.

**Step 4 — Hybrid spatial + channel attention.** Restore spatial Q·K' attention from the pre-rewrite design as a *parallel* path alongside the current channel attention. The spatial path provides the dynamic context-dependent attention the channel path has lost; the channel path keeps doing routing. **Pro:** restores conventional attention behaviour without removing what's working. **Con:** doubles attention parameter count and compute; substantial architectural change; needs care to avoid the original spatial-attention failure modes (uniform-attention collapse on sparse-reward tasks, run-5 style).

**Step 5 — Replace the attention block with self-attention over spatial tokens.** A full revert to flatten-and-linear attention with sequence-style Q·K'/√d scoring over the (B, H·W, C) token grid. This is essentially undoing the 2026-05-23 conv-spatial redesign. **Pro:** the most dynamic-attention-friendly mechanism, well-studied. **Con:** parameter count, latency, and previously-identified failure modes; we'd be restarting an architectural arc we've spent significant effort on.

The plan is to escalate at most one step at a time, with a documented before/after comparison on the standard forced-trial diagnostic (`RViT_plus/analysis/attention_maps_forced.py`) showing L3 softmax entropy at the action frame, task `correct` rate, and `return` after a meaningful training run. We commit to a step only if the previous step's intervention failed to restore at least partial broadening at L3 OR demonstrably hurt task competence.

**Architectural commitments preserved through the entire RL phase.**
  - Encoder: V1→V4→IT hierarchy, n_FR=1 single bottom-up pass per timestep (the n_FR loop was retired 2026-05-23; runs 18+ all use single-pass connectivity).
  - `split_c3 = True`: each of the AE, actor, and critic gets its own `cell3_X` specialist.
  - Attention block (`attention.py`): fully conv-spatial, gated Z↔H fusion via 3×3 convs, 4-head channel attention, conv-FFN block. No 1×1 convs anywhere. Replaces the prior flatten-and-linear FT (2026-05-23).
  - Cell (`memory.py`): no SIP candidate, no pos_emb, no pre-GN — the new attention block handles fusion internally; only an LSTM-style update gate `u = σ(Conv3x3([z, C_prev]))` survives.
  - Distributional QR-DQN critic with 51 quantiles, expected-SARSA V from `Σ_a sg[π(a)] · Q(s, a, :)`.
  - Content-weighted MSE recon auxiliary (run-15 baseline).

**Things explicitly NOT in the stack as of 2026-05-25.** Adaptive σ certainty-decay (any variant). UCB exploration (any variant). Hardcoded ε-greedy schedules. Hardcoded entropy bonuses beyond the default `entropy_coef = 0.01`. Any explicit "spread reward" on critic quantile std. The microstim `attn_bias` plumbing is retained as a hook but is a no-op under the channel-attention block (spatial-attention biasing doesn't map onto channel attention).

---

## Stage curriculum (5 stages from `RVIT_PLUS_DESIGN.md`)

- **Stage 1: synthetic video compression** (MovingMNIST, 50×50, T=10). The current stage. Goal: P1 confirms attention structure emerges.
- **Stage 2: natural video pretraining** (KTH or UCF101 if Stage 1 P1 confirms). Validates that the architecture scales.
- **Stage 3: synthetic cue-attention pretraining** (Posner-style targets in a compression context). Bridges from passive reconstruction to attentional task structure.
- **Stage 4: Posner RL fine-tune.** The HRA task, with the pretrained encoder providing the starting point that HRA never had.
- **Stage 5: microstim ablations + RSA.** The interpretability standard from the published RViT paper (Herman & Morgan 2025), reproduced on RViT+ with the formal microstim hook plumbed at every (frame, layer, iter) cell.

---

## Open architectural questions (post run 6)

1. **Does the SIP residual obviate the update gate, or do they serve different functions?** SIP residual preserves spatial structure across the FT bottleneck; the update gate preserves temporal recurrence across the cell update. They are conceptually orthogonal but I have not yet ablated them independently. The fully-conservative (with both) is run 6; the "no update gate" was run 4 (failed for unrelated reasons); a "no SIP residual but with update gate" ablation is a natural next-step run.

2. **Why does the model converge to recon=0.02 = MSE(0, video) in run 5?** This is the trivial-mean-image minimum. Under what conditions does an autoencoder fall into this trap vs. into a meaningful low-rank reconstruction? `Friston2010_fep_unified_theory` predicts that minimizing variational free energy will find the *most precise* model consistent with the data, but a model with no spatial-variation capacity is "consistent" with a zero output for centered data — there is no asymmetry penalizing the trivial solution. The KL term on the latent does not break this symmetry because the latent samples don't carry position info.

3. **Will MovingMNIST (Stage 1) actually pressure the FT?** Two bouncing digits in a 50×50 frame is information-rich enough that *some* spatial structure has to live in the latent — the digit identity, position, velocity all need to be retained. A finer-grained question is whether the FT contributes here or whether SIP alone (with the residual) does the work. If the SIP path is strong enough to solve compression on its own, the FT may still be vestigial. Stage 1 verdict needs not just "attention entropy < threshold" (P1) but also a per-component ablation: train an identical model with FT zeroed-out and compare reconstruction quality.

4. **Does the temporal embedding leak too much information to the decoder?** The decoder synthesizes `z₁(τ) = latent_proj(latent) + temporal_proj(temporal_emb(τ))` at each step. A learned temporal embedding gives the decoder strong knowledge of "what time step it is," potentially letting it produce coherent unrolls without the latent carrying much information. The KL coefficient (currently 0.05) regularizes this but may not be enough.

5. **What is the right ablation order for downstream stage decisions?** If Stage 1 confirms P1, the next experiment is *not* immediately jumping to Stage 2 — it's verifying that the structure transfers to Stage 4 with an RL fine-tune. A KTH detour (Stage 2) is only valuable if Stage 1's structure does not transfer to RL, in which case scale becomes the suspected cause.

---

## Connection to other concepts

- `gridcell_rnn` (concepts/) — the per-cell update rule. The post-run-6 SIP+pos_emb+residual+gate variant should be reflected back into that concept file (see the empirical refinements section).
- `feedback_transformer` (concepts/) — open question 4 in that file (FT spatial-attention uniformity under sparse-reward PPO) is the immediate ancestor problem; this thread documents the supervised-learning analog and the architectural protections that close it under dense gradient.
- `iterative_variational_encoder_decoder` (concepts/) — RViT+ is a faithful instance of this concept, with n_FR=4 forward-reasoning iters per frame, the encoder running over a full T-frame video, and the decoder unrolling T steps.
- `the_user_architectural_program` (threads/, §6) — RViT+ replaces HRA as the current empirical instance of the program; that thread's §6 should be updated to reflect the lineage.

## Connection to the published RViT (Herman & Morgan 2025)

The published paper documents one feedback source (H^{t-1}), single layer, multiplicative variant. RViT+ generalizes that to three layers with K = {3, 2, 1} feedback sources per layer (including the self-recurrent), retinotectal-analog skip connections, an iterative variational encoder–decoder structure, and the microstim hook plumbed at every (frame, layer, iter). The interpretability comparison standard the paper sets — attention-trajectory dynamics, FEF-microstim analog, RSA against IT cortex — is the explicit acceptance criterion for Stage 5.
