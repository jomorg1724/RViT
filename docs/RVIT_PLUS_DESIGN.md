# RViT+ — design document

**Status:** Design proposal, 2026-05-20. Pre-implementation review document for the next-generation visual-attention model. Replaces the HRA design after the May 2026 failure-mode post-mortem.

**Working name:** *RViT+* (Recurrent ViT plus). Ties to the published Herman & Morgan 2025 lineage; "+" denotes the architectural extensions detailed below.

**Synthesis basis:** the research_db's four threads + 15 concept files (notes in `RVIT_PLUS_NOTES.md`), the user's documented Video Autoencoder design philosophy (per `research_db/threads/the_user_architectural_program.md`), and the failure-mode lessons from HRA (`MODEL_DESIGN.md` + post-mortem diagnostics).

---

## 1. Central claim

The Video Autoencoder works because **video reconstruction is a task that cannot be solved by global pooling** — it forces the model's attention layer to develop spatial structure as a side-effect of the gradient. HRA failed on the Posner change-detection task because the task *can* be solved by global pooling (PRISM v1 demonstrates this), and the Feedback Transformer's spatial attention sat at a flat minimum of the policy loss with no gradient pushing it toward structure (`concepts/feedback_transformer.md` open question 4; `MODEL_DESIGN.md` deep-dive findings).

RViT+ inherits the Video Autoencoder's architectural lineage (multi-layer GridCell RNN stack with Feedback Transformer integration, iterative variational encoder-decoder protocol) and extends it with four specific design choices that make it (a) interpretable to Herman & Morgan 2025 standards from day one, (b) parameter-efficient for video at small scales, and (c) ready for clean RL bridging without re-architecting.

The four extensions:

1. **Microstim-analog interpretability hooks as first-class architectural outputs**, not bolted-on probes.
2. **Spatially-preserving layer organization** (full retinotopy for V1- and V4-analog layers; abstraction only at the IT-analog layer) — addressing HRA's signal-flow bottleneck.
3. **Hybrid pixel + latent-space prediction objectives** (iterative-VAE recon + V-JEPA-style latent prediction) — denser supervision than either alone.
4. **RL-ready architecture from training day one**: actor and action-conditional distributional Q critic heads exist alongside the decoder, with a curriculum-staged training protocol that pretrains on video before exposure to sparse-reward Posner.

---

## 2. Falsifiable predictions (pre-registered)

**P1 — Reconstruction shapes attention.** After 10⁴ updates of MovingMNIST pretraining, per-layer attention entropy will drop below 80% of max-entropy on at least 50% of timesteps. *Falsified if:* attention stays at >95% max-entropy (uniform) as in HRA. [Anchor: `feedback_transformer.md` open question 4; `voita2019_head_specialization`; `kietzmann2019_recurrence_required`.]

**P2 — Layer-wise representational hierarchy emerges from recon.** Per-layer RDMs (Kriegeskorte 2008 RSA) computed on UCF101 video frames will show monotonically-increasing alignment with primate IT recordings (BrainScore) as we ascend the layer stack. *Falsified if:* alignment is flat or inverted across layers. [Anchor: `kriegeskorte2008_rsa`, `zhuang2021_unsupervised_ventral`, `dicarlo2012_object_recognition`.]

**P3 — Cue encoding emerges before RL.** After Stage 3 attention-shaping pretraining (synthetic cue-attention tasks), the encoder hidden state at t=10 will linearly separate left-cue vs right-cue Posner trials with >85% accuracy. *Falsified if:* linear separability stays at chance (~50%) as in HRA's iter-1999 model. [Anchor: HRA `deep_dive.py` Test 2 — concrete numerical comparison available.]

**P4 — Microstim-analog produces the published RViT signature.** Adding a Gaussian bias to the attention map at iteration k=2 of layer C₁ at the cue location reproduces the FEF-microstimulation behavioural effect described in Herman & Morgan 2025 (selective improvement at the perturbed location). *Falsified if:* perturbation has no behavioural effect or effect is opposite. [Anchor: `moore_armstrong2003_fef_microstim`, `cavanaugh_wurtz2004_sc_change_blindness`, `sridharan2017_sc_sensitivity_bias`, Herman & Morgan 2025.]

**P5 — RL bridge works.** With a Stage-1+2+3 pretrained encoder, RL fine-tuning on Posner change-detection passes the 0.55 correct-rate threshold (HRA's previous best plateau) within 1k iters. *Falsified if:* same flat-policy null result as HRA after 2k iters. [Anchor: HRA failure as null hypothesis.]

**P6 — Small-model competitiveness on video.** At ≤10M params, RViT+ matches or exceeds PredNet and FitVid on MovingMNIST and KTH next-frame PSNR/SSIM. *Falsified if:* PSNR is more than 1.0 dB below matched-parameter baselines. [Anchor: `concepts/coupled_rnn_world_models.md`; PredNet/FitVid as reference.]

---

## 3. Architecture spec

### 3.1 Layer stack

Three GridCell RNN layers — but with **spatially-preserving** structure for the first two, departing from HRA's aggressive 12→6→3 compression.

| Layer | Pairing | Grid resolution | Channels | Rationale |
|---|---|---|---|---|
| C₁ | V1-analog | 12×12 (full) | 64 | retinotopy preserved (Hubel-Wiesel 1962/1968; Felleman-Van Essen 1991) |
| C₂ | V4-analog | 12×12 (full) | 96 | V4 in macaque preserves coarse retinotopy too |
| C₃ | IT-analog | 6×6 (compressed) | 128 | IT loses retinotopy — only here does compression happen (DiCarlo 2012; Tanaka 1996) |

**Why this differs from HRA's 12→6→3:** the deep-dive findings showed C₂ and C₃ frozen because all input flowed through stride-2 conv chains from a barely-responsive C₁. Cortical reality is that V1 and V4 *both* preserve fine retinotopy; only IT becomes spatially-invariant. The HRA compression was an inherited assumption from PRISM, not a biologically- or task-justified one.

Total param budget: ~5-8M depending on attention-head count. Targeted at the "small recurrent video model" niche (PredNet 7M, FitVid small-variant 4-6M).

### 3.2 Cell architecture: GridCell RNN (LSTM SIP + Feedback Transformer)

Per-cell SIP is a **patch-wise LSTM**, matching the Recurrent ViT and Food-101 classifier lineage rather than PRISM's ConvGRU (Jozefowicz et al. 2015 finds LSTM hard to beat in head-to-head). Cell update: LSTM-style input/forget/output gates per grid cell, **forget gate bias = 0** (σ(0) = 0.5 — the HRA-validated reactive setting; bio motivation in Tallec-Ollivier 2018 chrono-init).

The FT operates on the LSTM-candidate state as the "sensory" input plus the layer's previous hidden state + cross-layer feedback as Q/K/V sources per the Feedback Transformer Hadamard-broadcasting structure (`concepts/feedback_transformer.md`):

$$
\tilde Q = X W^Q_X \odot \prod_k (1 + C^{(k)} W^Q_{C^{(k)}}), \quad \tilde K = X W^K_X \odot \prod_k (1 + C^{(k)} W^K_{C^{(k)}})
$$

Note the `(1 + …)` identity-init wrapping — preserves the multiplicative broadcasting from the canonical spec but with `softplus`-initialized gates so the model starts with feedback ≈ identity (HRA-validated).

### 3.3 Cross-layer feedback

`cross_layer_via = "ft"` (HRA's "input" mode was a workaround for sparse-RL exploration failure; with recon-driven training the FT has gradient pressure to use the cross-layer sources, so we put them where they belong).

Per `multi_compartmental_memory.md` reference design:
- Descending (top→bottom abstraction = bottom→top spatial): conv blocks for shape matching (12→12 = 1×1 conv channel adapter for L1→L2; 12→6 stride-2 for L2→L3)
- Ascending feedback: transpose-conv for shape matching, routed through each receiving layer's FT as a Q/K/V source

Plus the **retinotectal-analog skips** validated by the HRA random-init probe (V → C₂ and V → C₃ summed into z_t, scaled by 0.3 so they don't over-drive — `enable_skips=True`, `skip_scale=0.3`).

### 3.4 Iterative encoder-decoder (Video AE protocol)

**Encoder phase ($n_{FR}=4$ forward passes):** show the same frame (or video clip in video mode) repeatedly; encoder updates internal guide state $H_t \leftarrow \psi_\theta(X, H_{t-1})$ each pass. Final guide is $H_{n_{FR}}$.

**Decoder phase ($n_{BR}=4$ backward passes):** $\tilde H_0 = H_{n_{FR}}$, learned $Z_0$, decoder runs $(Z_{\tau+1}, \tilde H_{\tau+1}, \tilde X_{\tau+1}) \leftarrow \phi_\theta(Z_\tau, \tilde H_\tau)$.

Reconstruction loss exponentially weighted: $\mathcal{L}_\text{recon} = \sum_i e^{i-n_{BR}} \cdot \text{MSE}[\tilde X_i, X]$.

**Variational KL** on $\tilde H_0$ (Gaussian posterior over a unit-Gaussian prior; matrix-normal extension with row-whitening penalty per `iterative_variational_encoder_decoder.md` §"Multi-patch distributional latents").

The decoder *exists* as a top-level module but is **detached during RL fine-tune** (Stage 4) — only the recon loss as an auxiliary keeps it learning. Its gradients then don't pollute the actor/critic.

**Wiki anchors for R4.** Three axes of grounding for the fixed-$n_{FR}=4$ iterative-encoder choice, supplied by the research_db. R4 is the RViT+ inheritor of HRA's D2 ([MODEL_DESIGN.md](MODEL_DESIGN.md) §D2 — fixed $n_{FR}=5$); the architectural commitment is identical (no PonderNet halting in the prototype, every input gets the same number of iterations to preserve trial-by-trial trajectory-comparison analyses), the iteration count differs slightly (4 vs 5).

*Axis 1 — Recurrence is required to capture cortical visual dynamics.* The two strongest empirical anchors for *why* iterated computation over a static-frame input is the right computational primitive — the same anchors that ground HRA D2's Axis 1, here reframed for the RViT+ Video AE encoder protocol where each frame receives a fixed iteration budget.

- [kietzmann2019_recurrence_required](research_db/papers/kietzmann2019_recurrence_required.md) §7 — recurrent networks, *not* matched-parameter feedforward ones, are required to capture the representational geometry of the human ventral stream over time (MEG RDM timecourse alignment). The paper's per-image RDM-trajectory comparisons require *matched iteration counts per trial*, the same analytical interface RViT+'s P1–P4 inherit from the published Recurrent ViT. Critically, RViT+ runs *per-frame* iterative refinement inside a video-AE protocol: the matched-iteration constraint applies at the *frame* level (each frame gets $n_{FR}=4$ iterations) so that frame-by-frame attention-trajectory comparisons are commensurate, not just trial-by-trial.
- [mante2013_context_dependent_pfc](research_db/papers/mante2013_context_dependent_pfc.md) §7 — trained-RNN account of context-dependent perceptual choice in primate PFC, where recurrent dynamics over the stimulus presentation window *are* the computation. Mante's state-space-decomposition analyses (the choice and context axes) require recurrent unrolling depth to be the same across trials so that population-level trajectories are readable at matched timesteps. RViT+'s Stage 5 RSA against IT cortex — and the Stage 4 attention-trajectory analyses comparing pre- vs post-RL cell behaviour — inherit the same constraint, now applied at the per-frame iterative-encoder level.

*Axis 2 — Iterative inference as the principled cortical computation; persistent activity as the timescale anchor.* The cortical-physiology anchor that argues a *small finite* iteration budget is biologically plausible AND the predictive-coding anchor that argues iterative refinement of the variational posterior is the canonical cortical computation rather than a heuristic.

- [constantinidis2018_persistent_activity](research_db/papers/constantinidis2018_persistent_activity.md) §7 — review of prefrontal persistent-activity literature, framing maintenance of stimulus-related activity over hundreds of milliseconds as the cellular substrate of WM. The temporal grain is the key anchor for $n_{FR}$: persistent activity supports compute budgets on the order of single perceptual decisions (~5–20 iterations at typical cortical-timestep granularity, ~50 ms/step ≈ a single-frame Posner-target latency window), not unboundedly long horizons. Fixed-4 sits comfortably inside that biologically natural per-frame window — a step below HRA's fixed-5 because the *per-frame* budget within a multi-frame video clip should be smaller than the *per-trial* budget HRA committed to over a single static input.
- [rao_ballard1999_predictive_coding](research_db/papers/rao_ballard1999_predictive_coding.md) §7 — the foundational predictive-coding-as-iterative-inference paper. Rao & Ballard's hierarchical generative model is trained by iterative gradient descent on the prediction-error residual; each pass refines the internal representation toward a better variational posterior over the input. RViT+'s $n_{FR}=4$ encoder iterations operationalise exactly this: each pass refines the guide state $H_t$ via the Feedback Transformer's cross-layer error integration, with the *fixed* count enforcing that every frame gets the same depth of variational refinement. This is the architectural translation of "iterative inference *is* the cortical computation" — a substantive design commitment, not just a recurrence-depth knob.

*Axis 3 — The deferred adaptive-halting alternatives and the principled-fixed-iteration justification.* The design space the fixed-4 choice rejects, plus the variational-theory anchor that argues fixed iteration count is not just an interpretability concession but a principled choice.

- [banino2021_pondernet](research_db/papers/banino2021_pondernet.md) §7 — the canonical published alternative: learnable per-step halting policy with stochastic continuation decisions. PonderNet's empirical wins are on accuracy and compute efficiency; its halting stochasticity is precisely what breaks the per-frame trajectory-comparison interface RViT+'s Stage 4–5 analyses depend on. Deferred to v2 (the same deferral HRA D2 took) — a natural v2 ablation knob is to add a per-frame halt head on top of RViT+ and compare interpretability ergonomics vs. compute savings. Note that PonderNet's §7 explicitly proposes a per-patch extension as the natural fit for vision transformers; RViT+'s per-frame fixed-budget is the inverse architectural choice (uniform-budget across patches and frames; analytical commensurability over compute efficiency).
- [friston2010_fep_unified_theory](research_db/papers/friston2010_fep_unified_theory.md) §7 — the variational free-energy theory that supplies the *principled* reason fixed iteration count is the right design rather than an interpretability concession. Under FEP, every iteration of inner-loop variational inference further reduces free energy with respect to the same generative-model objective; there is no a-priori "right" stopping criterion because the posterior is being refined toward (not at) a global minimum, and the marginal benefit per iteration declines smoothly rather than crossing a sharp threshold. Fixed-4 is therefore a budgeted choice: enough iterations to make meaningful variational refinement (per the Rao-Ballard chain), few enough that the per-frame computational cost stays small in the multi-frame video setting. PRISM v1's free-energy formulation ([friston2010_fep_unified_theory](research_db/papers/friston2010_fep_unified_theory.md) §7 names PRISM v1 as a Friston-framework model) inherits exactly this design pattern, and RViT+'s Video AE protocol generalises it across frames.

These six anchors collectively justify R4 along three axes: **the necessity of per-frame recurrence over the video input** ([kietzmann2019_recurrence_required](research_db/papers/kietzmann2019_recurrence_required.md), [mante2013_context_dependent_pfc](research_db/papers/mante2013_context_dependent_pfc.md)), **the biological + computational substrate for iterative-inference-as-cortical-computation** ([constantinidis2018_persistent_activity](research_db/papers/constantinidis2018_persistent_activity.md), [rao_ballard1999_predictive_coding](research_db/papers/rao_ballard1999_predictive_coding.md)), and **the explicit deferred alternative + the principled-fixed-iteration justification** ([banino2021_pondernet](research_db/papers/banino2021_pondernet.md), [friston2010_fep_unified_theory](research_db/papers/friston2010_fep_unified_theory.md)). The closest published precedent for the *combination* is HRA itself ([MODEL_DESIGN.md](MODEL_DESIGN.md) §D2, fixed $n_{FR}=5$) — R4 inherits the architectural commitment intact but applies it at *per-frame* granularity inside a video-AE protocol rather than at *per-trial* granularity over a single static input. The published Recurrent ViT (Herman & Morgan 2025) ran at $K=1$ (single-pass per input); R4's $n_{FR}=4$ is a step *toward* per-frame iterative refinement, matching the same lineage progression D2 articulated and HRM ([wang2025_hierarchical_reasoning_model](research_db/papers/wang2025_hierarchical_reasoning_model.md)) committed to with a similarly small fixed inner-loop count (~6 steps before the outer slow update).

### 3.5 Auxiliary objectives (in pretrain phase)

1. **Pixel recon MSE** (primary, $\lambda=1$) — the gradient-shaping engine.
2. **Variational KL** ($\lambda=0.1$, beta-VAE style) — smoothness, disentanglement, Hopfield-attractor regularization.
3. **V-JEPA-style latent prediction** ($\lambda=0.5$) — predict next-frame's $H$ from current $H$ via a learned predictor. Complements pixel recon at the semantic level (Bardes 2023; LeCun 2022).
4. **Slowness** on each layer's hidden state ($\lambda=0.01$) — encourages temporal stability.
5. **Row-independence penalty** on the multi-patch latent ($\lambda=0.05$) — matrix-normal row-whitening.

### 3.6 RL bridge — Stage 4 fine-tune

When RL fine-tuning starts, the model adds:
- **Actor head** reading from per-layer hidden states through `LayerHead`-style conv reduction (validated in HRA's interpretability design; `concepts/multi_compartmental_memory.md`).
- **Action-conditional distributional Q critic** per the canonical QR-DQN design in `concepts/distributional_rl.md`: $Q_\phi(s, a; \tau) \in \mathbb{R}^{B \times |A| \times N}$, $V_\phi(s) = \sum_a \text{sg}[\pi(a|s)] Q_\phi(s, a)$. Inherits the gradient-routing safety of `Q_CRITIC.md`.

The encoder + decoder + KL + JEPA + slowness aux losses stay on during RL. Only the actor surrogate + critic QR-Huber are *added*. This is the load-bearing difference from HRA: the encoder cannot collapse to constants because the reconstruction loss actively pulls it away from constants.

**Attention-supervision option** (`attention_supervision_coef` knob, default 0.05): a small KL penalty against a per-step location prior derived from the cue during the cue and change windows. Off by default; turned on if Stage 4 stalls. (Per `feedback_transformer.md` open question 4 recommended fix.)

---

## 4. Interpretability protocol — the microstim experiment is first-class

The model's `StepOutput` exposes (per-iteration, per-layer) named tensors:

| Hook | Shape | Microstim/analysis use |
|---|---|---|
| `attn_per_layer[k][ℓ]` | $(B, n_\text{heads}, N_\ell, N_\ell)$ | **Attention perturbation** = the FEF-microstim analog (`moore_armstrong2003_fef_microstim`, `cavanaugh_wurtz2004_sc_change_blindness`). Add Gaussian bias at chosen $(k, \ell, \text{head}, i, j)$; observe behavioural delta. |
| `state_per_layer[k][ℓ]` | $(B, C_\ell, H_\ell, W_\ell)$ | RSA against IT (`kriegeskorte2008_rsa`); per-layer ablation; persistent-activity probes (`masse2019_circuit_wm`). |
| `feedback_projections[k]` | dict of named cross-layer tensors | Per-pathway ablation (zero one feedback route at a time); Sridharan-style sensitivity-vs-bias attribution. |
| `pc_error_per_layer[k][ℓ]` | $(B, H_\ell, W_\ell)$ | PRISM-style saliency map per level. |
| `q_dist` | $(B, |A|, N)$ | Per-state Q-distribution variance as the precision channel (`distributional_rl.md` §"Uncertainty channel into the Feedback Transformer"). |

**The microstim experiment, precisely:**

```python
# Baseline rollout
baseline = model.forward_step(x_t, prev_states)
baseline_action = sample(baseline.action_logits)
baseline_reward = env.step(baseline_action)

# Microstim rollout — same trial, same prev_states
def microstim_hook(layer_idx, iter_idx, target_loc, magnitude):
    def hook(attn_logits):
        # attn_logits is (B, n_heads, N, N) at layer L, iter k
        if layer_idx == L and iter_idx == k:
            bias = gaussian_kernel_at(target_loc, sigma=1.5) * magnitude
            attn_logits[:, :, :, target_loc_idx] += bias
        return attn_logits
    return hook

with model.attention_hook(microstim_hook(L=0, k=2, target_loc=(3,8), magnitude=2.0)):
    perturbed = model.forward_step(x_t, prev_states)
    perturbed_action = sample(perturbed.action_logits)
    perturbed_reward = env.step(perturbed_action)

delta = perturbed_reward - baseline_reward
```

This is **architecturally guaranteed to work** because the attention maps are first-class outputs that can be hooked. Compare to HRA where attention was buried inside `nn.MultiheadAttention`-style modules — usable but with friction. RViT+ exposes the perturbation interface as a public API.

---

## 5. Training curriculum — RL is Stage 4, not Stage 1

| Stage | Data | Objective | Gate criterion | Estimated time |
|---|---|---|---|---|
| 0 | (scaffolding) | shape tests, smoke tests | 66/66 + 32/32 (HRA precedent) | hours |
| 1 | MovingMNIST | recon + KL + slowness + JEPA-aux | PSNR > 22 dB on 10-step prediction; attention entropy < 80% max | 4-8 hours (MPS) |
| 2 | KTH or BAIR | scale-up recon | match PredNet/FitVid at matched params; attention shows learned spatial structure | 1-2 days |
| 3 | Synthetic cue-attention | recon + supervised cue prediction at hidden states | cue position linearly decodable from C_2 hidden state at t=10 with >85% accuracy | hours |
| 4 | Posner change-detection (env from HRA) | + actor surrogate + Q QR-Huber | correct rate > 0.60 (beats never-press baseline by margin); argmax-deterministic presses > 0 | 1-2 days |

**Critical curriculum decision:** RL only happens at Stage 4, with the encoder warm-started by 3 prior stages of dense-gradient training. This is the lesson that HRA missed.

---

## 6. What's surviving from HRA, what's not

**Surviving:**
- `HRA/env.py` (ChangeDetectionEnv — Posner task unchanged)
- The diagnostic tooling: `deep_dive.py`, `attention_maps.py`, `_load.py`
- Distributional Q critic design (`Q_CRITIC.md` and `concepts/distributional_rl.md`)
- LayerHead conv-reduction readout (preserves per-layer spatial info for the decision pathway)
- The recurrent PPO + non-finite-grad guard (`HRA/ppo.py` with my recent fixes)
- The 235-paper research_db (citation grounding)
- The `model_kwargs`-in-checkpoint scheme

**Going away:**
- HRA's three-layer compression chain (12→6→3) — replaced by 12→12→6
- ConvGRU-with-error-gating cell — replaced by LSTM SIP + Feedback Transformer
- Sparse-RL-first training — replaced by recon-first curriculum
- The collapse-prone attention layer — pre-empted by the recon-task gradient pressure
- The frozen-deeper-layers problem — pre-empted by the spatially-preserving layer organization

---

## 7. Build path

| Stage | Deliverable | Approx. effort |
|---|---|---|
| 0a | New directory `RViT_plus/`, six-module skeleton, env+ppo borrowed from HRA, shape tests | 4-6 hrs |
| 0b | `GridCellRNN_LSTM` cell + `FeedbackTransformer` (Hadamard variant, `(1+·)` identity-init) | 4-6 hrs |
| 0c | Three-layer `RViTPlusEncoder` + `RViTPlusDecoder` with $n_{FR}, n_{BR}$ iterative protocol | 6-8 hrs |
| 0d | Reconstruction-pretrain training loop (MovingMNIST dataloader, recon + KL + JEPA losses) | 4-6 hrs |
| 0e | Interpretability hook layer: named tensor outputs + microstim API + first analysis module on a forward dummy input | 4-6 hrs |
| 1 | Train MovingMNIST to gate | 4-8 hrs runtime |
| 2 | KTH dataloader + scale-up training | 1-2 days |
| 3 | Synthetic cue-attention dataset + Stage-3 fine-tune | hours+days |
| 4 | Bring back HRA's `ppo.py` for actor/critic, RL fine-tune on Posner | days |

Total compute-time to Stage-4 evaluation: roughly **1 week** of MPS time once code is in place. Code time before any training: ~30 hours of focused work, but doable in 2-3 sessions.

---

## 8. Open questions & risks

**Open questions for you, the owner:**

1. **MovingMNIST or your own UCF101 subset?** Stage 1 should be small/fast; Stage 2 should be the kind of video the Video AE proved out. I default to MovingMNIST for Stage 1 (well-documented, fast) and KTH for Stage 2 (small enough to converge in a day; established baseline numbers). If you have UCF101 ready, we can swap directly to it for Stage 2.
2. **Synthetic Stage 3?** I'm proposing a synthetic cue-attention dataset (single random gabor; cue indicates which; model has to encode cue position) as an attention-shaping bridge between video recon and Posner RL. Worth doing, or skip directly from Stage 2 to Stage 4?
3. **Latent JEPA loss right away, or after pixel recon works?** I default to having it on from Stage 1 (lambda=0.5). If it's destabilizing we can ablate it cleanly.
4. **Drop the matrix-normal latent for v1?** Honestly the matrix-normal + row-whitening penalty adds complexity. For the prototype I'm leaning toward "use vector latent, add matrix-normal in v2." OK with that?

**Risks I've identified:**

- **Reconstruction quality at small scale.** 5-8M params is on the small end for video models; if PSNR doesn't reach baselines, the rest of the architecture's value is moot. Mitigation: Stage 1 (MovingMNIST) is small enough that we'll know in hours, not days.
- **JEPA latent prediction is non-trivial to stabilize.** The V-JEPA paper has specific stop-gradient tricks for the target encoder. We'd be reinventing some of that. Mitigation: start with JEPA off and add when pixel recon stabilizes.
- **RL bridge might still fail at Stage 4.** Even with a great encoder, the sparse-reward problem might require attention-supervision or curriculum. Mitigation: attention-supervision knob is built in from day one.
- **The Feedback Transformer's `(1+·)` identity-init might not develop differentiating attention** even under recon pressure. Mitigation: alternative is `(W·x + b)` init with $b$ at 0 — closer to standard transformer init. Easy ablation.

---

## 9. Open scholarly note

For *publishability* of the eventual paper(s), the contribution lineage is:
- vs. Recurrent ViT (2502.10955): RViT+ is the multi-layer extension with explicit Feedback Transformer + recon-pretrain curriculum + microstim-analog hooks at every layer (not just one).
- vs. Video AE (Jonathan's prior work): RViT+ adds (a) latent JEPA loss, (b) RL bridge as part of the architecture, (c) interpretability-first design.
- vs. PRISM v1: RViT+ replaces no-attention-by-design with attention-shaped-by-recon. Same "recurrent visual decision-maker" goal; different architectural strategy.
- vs. HRA: RViT+ replaces sparse-RL-first with recon-first; less spatial compression; LSTM SIP instead of ConvGRU; latent JEPA aux loss; same distributional Q critic.

The neuro-AI publication target reads as: "A recurrent ViT model trained on video reconstruction develops cortically-aligned multi-layer attention dynamics that transfer to a primate-validated change-detection task via RL fine-tuning, with attention perturbations producing FEF-microstimulation-style behavioural shifts."

The AI-space publication target reads as: "A small (5-8M param) recurrent video model competitive with PredNet/FitVid on standard benchmarks, with interpretability properties no diffusion-based model offers."

---

## 10. Approval checklist for the owner

Before I write Stage-0 code, I want explicit yes/no on:

- [ ] **Naming.** `RViT_plus/` directory and `RViT+` model class — OK or rename?
- [ ] **Three layers at (64@12×12, 96@12×12, 128@6×6)** — OK or different shape?
- [ ] **LSTM SIP** vs ConvGRU SIP — OK with LSTM?
- [ ] **`(1+·)` identity-init FT** vs standard transformer init — OK with identity?
- [ ] **MovingMNIST → KTH → synthetic cue → Posner curriculum** — OK or rearrange?
- [ ] **JEPA latent loss on from Stage 1** — OK or defer?
- [ ] **Vector latent (not matrix-normal) for v1** — OK with simpler latent?
- [ ] **Build path order** (Stage 0 modular implementation before any training) — OK?

Anything you want to change, push back on, or add — say so. Once approved, I'll begin Stage 0 implementation.
