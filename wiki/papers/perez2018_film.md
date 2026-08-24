---
id: perez2018_film
title: "FiLM: Visual Reasoning with a General Conditioning Layer"
authors:
  - "Perez, Ethan"
  - "Strub, Florian"
  - "de Vries, Harm"
  - "Dumoulin, Vincent"
  - "Courville, Aaron"
year: 2018
venue: "AAAI"
doi: ""
arxiv: "1709.07871"
url: "https://arxiv.org/abs/1709.07871"
tags:
  - deep-learning
  - representation-learning
concepts:
  - feature-wise-linear-modulation
  - gain-modulation
  - multiplicative-feedback
  - additive-feedback
  - top-down-feedback
  - gridcell-rnn
related:
  - treue_martinez_trujillo1999_feature_attention
  - reynolds_heeger2009_normalization
  - ballas2016_convgru
  - vaswani2017_attention
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# FiLM: Visual Reasoning with a General Conditioning Layer

## 1. Abstract

We introduce a general-purpose conditioning method for neural networks called FiLM: Feature-wise Linear Modulation. FiLM layers influence neural network computation via a simple, feature-wise affine transformation based on conditioning information. We show that FiLM layers are highly effective for visual reasoning — answering image-related questions which require a multi-step, high-level process — a task which has proven difficult for standard deep learning methods that do not explicitly model reasoning. Specifically, we show on visual reasoning tasks that FiLM layers 1) halve state-of-the-art error for the CLEVR benchmark, 2) modulate features in a coherent manner, 3) are robust to ablations and architectural modifications, and 4) generalize well to challenging, new data from few examples or even zero-shot.

## 2. Why this matters for us

FiLM **is the modulation primitive used in PRISM v1 and v2**. The paper supplies the canonical formulation — γ(z) ⊙ x + β(z), an affine, channel-wise modulation conditioned on an external signal z — and the empirical demonstration that this minimal conditioning layer is sufficient for hard multi-step visual reasoning. For our work, FiLM is both (a) the literal layer used to inject top-down memory feedback into the convolutional encoder of PRISM v1 and the hierarchical encoder of PRISM v2, and (b) a clean architectural realization of the *feature-similarity-gain* model of feature-based attention (Treue & Martínez Trujillo 1999): a multiplicative scalar gain per channel, derived from an external "task" signal, applied to a feature-tuned representation.

## 3. Key claims

1. **A single primitive — feature-wise affine modulation — suffices for conditioning.** Given a feature map $F$ and a conditioner $z$, FiLM computes $\text{FiLM}(F \mid \gamma, \beta) = \gamma(z) \odot F + \beta(z)$, where $\gamma$ and $\beta$ are produced by a small "FiLM generator" network conditioned on $z$, and the $\odot$ is broadcast across spatial dimensions but distinct per channel.
2. **FiLM is general.** It subsumes or matches conditional batch normalization (de Vries et al. 2017), conditional instance normalization (Dumoulin et al. 2017), adaptive instance normalization / AdaIN (Huang & Belongie 2017), dynamic layer normalization (Kim et al. 2017), and certain hypernetwork constructions, by treating the affine part of any normalization layer as a special case.
3. **A FiLM-ed ResNet halves SOTA error on CLEVR.** A standard ResNet image stem followed by 4 FiLM-modulated residual blocks (with the modulator γ, β computed by a GRU over the question tokens) reaches 97.7% test accuracy on CLEVR — versus ~94% for the previous best (Relation Networks; Santoro et al. 2017), and well above Stacked Attention Networks and the End-to-End Module Network.
4. **FiLM modulates features coherently.** Inspecting the learned γ and β values shows that the network learns task-relevant, semantically grouped modulations — e.g., attending to the relevant color or object class for the question.
5. **FiLM generalizes from few examples and zero-shot.** On CLEVR-Humans (natural-language paraphrases) and CLEVR-CoGenT (compositional generalization splits with held-out attribute combinations), FiLM transfers well, suggesting the modulation captures abstract task structure rather than memorizing training pairs.
6. **FiLM is robust to ablations.** Removing γ (additive-only) hurts more than removing β (multiplicative-only), but neither catastrophically collapses; depth, placement, and number of FiLM layers can be varied widely.
7. **FiLM is cheap.** A FiLM layer adds two parameters per channel per conditioning step and a single elementwise multiply-add at inference; the cost is negligible compared with the conv layers it modulates.

## 4. Methods

**The FiLM layer.** For feature map $F_{i,c}$ at sample $i$, channel $c$ (with spatial positions $h, w$ broadcast), FiLM applies

$$
\text{FiLM}(F_{i,c,h,w} \mid \gamma_{i,c}, \beta_{i,c}) = \gamma_{i,c}\,F_{i,c,h,w} + \beta_{i,c}.
$$

The modulators $\gamma_{i,c}, \beta_{i,c} \in \mathbb{R}$ are produced by a *FiLM generator* $g$ taking a conditioning input $x_i$ (typically a language embedding): $(\gamma_{i,\cdot}, \beta_{i,\cdot}) = g(x_i)$.

**Conditioner for CLEVR.** $x_i$ is the final hidden state of a GRU that reads the question token-by-token. A linear layer projects the GRU output to the concatenation of all $\gamma$ and $\beta$ vectors across all FiLM-modulated layers in the image stack.

**Image stack.** The CLEVR image is processed by a small convolutional stem (or a frozen pretrained ResNet feature extractor), then through 4 *FiLM-ed residual blocks*. Each block is a standard ResNet block whose post-conv BatchNorm has been replaced by BatchNorm without an affine parameter, followed by a FiLM layer; the FiLM layer's $\gamma, \beta$ come from the FiLM generator. A small classifier head (global max-pool, MLP) produces the answer logits.

**Training.** Standard cross-entropy on the 28-way answer classification of CLEVR, end-to-end with Adam.

**Generalization protocols.** CLEVR-Humans tests transfer to free-form natural-language questions with the model's vocabulary expanded but most weights frozen. CLEVR-CoGenT trains on one (color, shape) co-occurrence pattern and tests on a held-out pattern, isolating compositional generalization.

## 5. Results

**CLEVR test accuracy.**

- Stacked Attention Networks (Yang et al. 2016): 76.6%.
- End-to-End Module Networks (Hu et al. 2017): 83.7%.
- Relation Networks (Santoro et al. 2017): 95.5%.
- **FiLM (this paper): 97.7%** — roughly halving error vs. RN and approaching human-level (92.6% on the same test set).

**Ablations (CLEVR).**

- Removing the $\gamma$ (multiplicative) component drops accuracy by several points more than removing $\beta$ (additive); both terms contribute, with multiplicative gain doing most of the work.
- Reducing from 4 to 2 FiLM blocks costs a small amount of accuracy.
- Replacing the GRU conditioner with a simpler bag-of-words encoder hurts but does not collapse performance.
- Replacing FiLM with concatenation of $z$ onto every feature map performs substantially worse, confirming that affine modulation is doing real work, not just supplying side information.

**CLEVR-Humans.** With limited fine-tuning, FiLM reaches ~75% on natural-language paraphrases, well above the from-scratch baseline.

**CLEVR-CoGenT.** FiLM transfers to held-out attribute combinations with moderate degradation, indicating partial compositional generalization.

## 6. Critique / limitations

**Synthetic-stimulus regime.** CLEVR is synthetic: rendered shapes, perfect segmentation, closed vocabulary. FiLM's clean performance there does not by itself establish that affine modulation suffices for real-world VQA, where Bayes-optimal feature gating may not be expressible as channelwise affine.

**One conditioner per pass.** FiLM in this paper supplies a single $(\gamma, \beta)$ per layer per example, fixed for the whole image. It does *not* spatially vary the modulation — γ and β are scalars per channel, broadcast across space. Truly spatial top-down attention requires extending FiLM (e.g., to spatially-varying γ, β, as later work has done).

**The conditioner is feed-forward.** The GRU runs once over the question; the image stack then runs once with fixed modulators. There is no iterative refinement, no closed-loop interaction between modulation and feature extraction. This is exactly the gap that recurrent feedback architectures (including PRISM v1) seek to fill.

**Affine is a strong constraint.** FiLM's expressive power is bounded by what an affine transformation per channel can implement: it cannot rotate the channel basis, mix channels, or apply nonlinear gating across channels. Comparison with more expressive conditioning (gated linear units, attention-based conditioners, hypernetworks generating full conv kernels) shows FiLM is often *enough* but not strictly more expressive.

**Why does it work so well?** The paper is mostly empirical. The theoretical question of *why* a per-channel affine layer suffices for multi-step reasoning is left open; later analyses (e.g., Dumoulin et al. 2018 "Feature-wise transformations") give partial answers in terms of conditional computation and information routing.

## 7. Connection to our work

FiLM is **the literal modulation primitive used by PRISM v1 and PRISM v2.** The user's program treats it as a foundational building block, and the connection runs in three directions.

**(a) FiLM as the PRISM modulation layer.** PRISM v1 (`THESIS.md` §2.4) injects the previous memory state $M_{t-1}$ into the convolutional feature stack via FiLM: each conv block's output is modulated by $\gamma(M_{t-1}) \odot F + \beta(M_{t-1})$. PRISM v2 (`PRISM_V2_PROPOSAL.md` §3.4) extends this to a *hierarchical* FiLM stack — each level of the encoder receives its own $\gamma, \beta$ derived from a level-matched memory state. This is the **channel-wise feedback modulation** referenced in the user's architectural-program thread. The mapping is exact:

| FiLM (this paper) | PRISM v1/v2 |
|---|---|
| Conditioner $x_i$ = GRU(question) | Conditioner = $M_{t-1}$ (previous memory) |
| FiLM generator $g$ = linear projection | FiLM generator = learned MLP / conv stack |
| Modulated stack = ResNet image blocks | Modulated stack = ConvGRU-style encoder (Ballas et al. 2016) |
| Per-channel $\gamma, \beta$, spatially broadcast | Per-channel $\gamma, \beta$, spatially broadcast (v1); per-level in v2 |

**(b) FiLM as a clean architectural implementation of feature-based attention (FBA).** Treue & Martínez Trujillo 1999 establish that real cortical attention takes the form of a *multiplicative gain* on direction-tuned MT neurons, with the gain magnitude proportional to similarity between cell preference and attended feature. FiLM's γ is exactly this: a per-feature-channel multiplicative gain, derived from an external task signal. The β term is the *additive* (criterion-shift) counterpart — what signal-detection theory would call a bias shift on top of the sensitivity (gain) change. So FiLM provides a one-to-one architectural realization of the two-parameter sensitivity/bias decomposition that the FBA literature isolates empirically. The Reynolds & Heeger 2009 normalization model embeds the same multiplicative gain inside a divisive denominator; FiLM is the un-normalized affine slice of that picture, and pairing FiLM with a normalization layer (BatchNorm or LayerNorm without its own affine parameters, as in the original FiLM ResNet) recovers a structure isomorphic to the Reynolds-Heeger normalization-with-gain.

**(c) FiLM and the Feedback Transformer.** The user's Feedback Transformer (`threads/the_user_architectural_program.md` §1) is a *strict generalization* of FiLM. Where FiLM modulates only the input to a stack, the Feedback Transformer multiplies the Q and K projections (and additively combines V projections) of self-attention itself, integrating arbitrarily many feedback sources via per-source Q/K/V projections combined by Hadamard product before softmax. FiLM in the PRISM line is the *single-source, pre-attention, MLP-projection* special case of this. The published Recurrent ViT paper (2502.10955 §6.7) catalogues three variants — tokens, additive, multiplicative — and FiLM cleanly maps onto the third. The Feedback Transformer's contribution beyond FiLM is (i) multiple feedback sources via summation in the projection space, (ii) modulation injected *inside* attention rather than only at the stem, and (iii) hierarchical / multi-modal integration at one node.

**(d) What this paper licenses for PRISM.** FiLM's empirical success on CLEVR is the existence proof that channelwise affine modulation suffices for complex, compositional, multi-step reasoning *when the conditioner is well-tuned to the task*. In PRISM, the conditioner is a recurrent memory state being trained end-to-end on a change-detection task, so the same expressive sufficiency carries over modulo the recurrent training dynamics. The cheap parameter cost (2 numbers per channel per layer) is what makes FiLM tractable to scale across all layers of a hierarchical encoder in PRISM v2.

**(e) Limitations carried into PRISM.** PRISM inherits FiLM's lack of spatial variation: a single $(\gamma, \beta)$ per channel cannot implement *spatial* top-down attention. The user's program addresses this via the Feedback Transformer (which is spatially differentiated by construction), but PRISM v1/v2 retain the spatially-uniform FiLM gating. A future direction sketched in the architectural-program thread is to replace the per-channel scalar γ, β with a per-(channel, patch) tensor — effectively a spatially-resolved FiLM, equivalent to a token-wise multiplicative feedback inside self-attention.

## 8. Citations to follow

- `de_vries2017_conditional_batchnorm` — Conditional Batch Normalization, the immediate predecessor and special case of FiLM. Not in seed.
- `dumoulin2017_conditional_instance_norm` — Conditional Instance Norm for style transfer; the parallel root of FiLM. Not in seed.
- `huang_belongie2017_adain` — Adaptive Instance Normalization; another parallel root. Not in seed.
- `santoro2017_relation_networks` — Relation Networks, the CLEVR SOTA that FiLM beats. Not in seed.
- `johnson2017_clevr` — CLEVR benchmark itself. Not in seed.
- `hu2017_e2e_module_networks` — End-to-End Module Networks; structured competitor. Not in seed.
- `dumoulin2018_feature_wise_transformations` — Distill survey unifying FiLM with sibling conditioning layers. Not in seed.
- `ha2017_hypernetworks` — HyperNetworks; an alternative, more expressive conditioning route. Not in seed.
- `ballas2016_convgru` — ConvGRU, the recurrent backbone PRISM combines with FiLM. In seed.
- `treue_martinez_trujillo1999_feature_attention` — biological grounding for multiplicative-gain attention. In seed, full depth.
- `reynolds_heeger2009_normalization` — normalization-with-gain that FiLM partially implements. In seed, full depth.
