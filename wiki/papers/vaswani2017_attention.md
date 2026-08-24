---
id: vaswani2017_attention
title: "Attention Is All You Need"
authors:
  - "Vaswani, Ashish"
  - "Shazeer, Noam"
  - "Parmar, Niki"
  - "Uszkoreit, Jakob"
  - "Jones, Llion"
  - "Gomez, Aidan N."
  - "Kaiser, Lukasz"
  - "Polosukhin, Illia"
year: 2017
venue: "NeurIPS"
doi: ""
arxiv: "1706.03762"
url: "https://arxiv.org/abs/1706.03762"
tags:
  - transformers
  - deep-learning
  - self-attention
concepts:
  - scaled-dot-product-attention
  - multi-head-attention
  - positional-encoding
  - self-attention-over-tokens
  - gridcell-rnn
  - iterative-variational-encoder-decoder
related:
  - dosovitskiy2020_vit
  - voita2019_head_specialization
  - khan2022_transformers_vision_survey
  - locatello2020_slot_attention
  - bahdanau2014_neural_translation
  - tay2022_efficient_transformers_survey
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_23
  - thesis_md
  - prism_v2_proposal
status: full
depth: full
last_updated: "2026-05-16"
---

# Attention Is All You Need

## 1. Abstract

The paper introduces the Transformer, an encoder–decoder sequence model built entirely from stacked self-attention and feedforward layers, with no convolutions or recurrence. The core primitive is scaled dot-product attention: $\text{softmax}(QK^\top / \sqrt{d_k}) V$. Multi-head attention runs this primitive in parallel under multiple learned projections of $Q, K, V$, allowing the model to jointly attend to information from different representation subspaces at different positions. The Transformer trains substantially faster than RNN/CNN sequence models of comparable capacity and sets state-of-the-art BLEU on WMT 2014 English-German and English-French translation. The architecture has since become the default backbone for sequence models in language, vision, and multimodal applications.

## 2. Why this matters for us

The self-attention primitive is the operation the Recurrent ViT (2502.10955) augments with recurrent feedback and the operation PRISM v2 imitates with its multi-head saliency (`PRISM_V2_PROPOSAL.md` §3.6, "Recipe 1"). Vaswani et al.'s multi-head construction is the explicit ML antecedent for partitioning a saliency map into specialized heads. PRISM's central claim — that prediction error can substitute for softmax-attention in vision-RL — is meaningful only against the backdrop of the Transformer's dominance. The paper is therefore both a foundation and a foil.

## 3. Key claims

1. Self-attention alone (with positional encodings and feed-forward sublayers) is sufficient to produce a state-of-the-art sequence model, without convolution or recurrence.
2. Scaled dot-product attention — with the $1/\sqrt{d_k}$ scaling factor — avoids softmax saturation that would otherwise occur as dot-product magnitudes grow with the key dimension.
3. Multi-head attention enables the model to attend to different subspaces in parallel; eight heads with $d_k = 64$ each give better results than a single head with $d_k = 512$ at matched parameter count.
4. Sinusoidal positional encodings injected at the input are sufficient to give the model access to position information (the architecture is otherwise permutation-equivariant).
5. The Transformer trains in a fraction of the wallclock time of RNN-based seq2seq models of comparable capacity because attention is parallelizable across the sequence length.

## 4. Methods

The encoder is a stack of $N = 6$ identical layers, each with two sub-layers: multi-head self-attention and a position-wise feed-forward network (two linear layers with ReLU). Each sub-layer is wrapped in a residual connection followed by layer normalization. The decoder is structurally similar but adds a third sub-layer: cross-attention over the encoder output, with causal masking on the decoder's self-attention to enforce autoregressive generation.

Scaled dot-product attention is defined as:

$$
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{Q K^\top}{\sqrt{d_k}}\right) V
$$

where $Q \in \mathbb{R}^{n_q \times d_k}, K \in \mathbb{R}^{n_k \times d_k}, V \in \mathbb{R}^{n_k \times d_v}$. The $\sqrt{d_k}$ scaling is justified by the observation that the dot product of two independent $\mathcal{N}(0, 1)$ vectors of dimension $d_k$ has variance $d_k$; dividing by $\sqrt{d_k}$ rescales the variance to 1, which keeps softmax inputs in a non-saturated regime.

Multi-head attention applies the primitive $h$ times in parallel with separately learned projections $W_i^Q, W_i^K, W_i^V$ for $i \in 1..h$, then concatenates and projects: $\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) W^O$. The base model uses $h = 8$, $d_\text{model} = 512$, $d_k = d_v = 64$.

Sinusoidal positional encodings $PE_{(\text{pos}, 2i)} = \sin(\text{pos}/10000^{2i/d_\text{model}})$ are added to input embeddings.

Training uses Adam with the now-standard warmup-then-inverse-square-root learning rate schedule, label smoothing, and dropout. The base model has approximately 65M parameters; the "big" model has 213M.

## 5. Results

On WMT 2014 English–German, the base Transformer achieves BLEU 27.3 — outperforming all previously published single models. The big Transformer achieves BLEU 28.4. On WMT 2014 English–French, the big Transformer achieves BLEU 41.8. Training cost (FLOPs) is reported as approximately 1.5×10¹⁸ for the big EN-DE model, several times less than the best prior ensembles.

Ablation studies establish: a single head with full $d_\text{model} = 512$ is worse than 8 heads with $d_k = 64$ (BLEU ~0.9 lower); fewer than 8 layers in the encoder loses performance; dropout is essential to prevent overfitting; sinusoidal positional encodings perform comparably to learned positional embeddings.

## 6. Critique / limitations

The original Transformer assumes that all positions in the sequence are equally accessible — every token attends to every other token. This $O(n^2)$ scaling in sequence length is the central computational limitation, addressed by the subsequent long-context literature (sparse attention, linear attention, state-space models). For our purposes the more important conceptual limitation is that the Transformer is *feedforward* with respect to time: no recurrent state carries information across the sequence other than via the explicit attention reads. In sequence-to-sequence translation this is fine because the entire input is observed at once; in sequential decision-making it forces the model to re-attend over the entire history at each step or to compress it into the input via context windows.

The biological-plausibility critique is more substantial. There is no clear cortical analog of softmax over arbitrary token pairs; the multi-headed parallel structure has loose parallels in cortical area parcellation but no detailed alignment. Mehrani & Tsotsos (2023) argue that ViT self-attention performs perceptual grouping rather than the goal-directed selection that the term "attention" implies in neuroscience.

The "$1/\sqrt{d_k}$" justification rests on the assumption that $Q$ and $K$ entries are independent samples of variance 1 — true at initialization, not necessarily true after training. In practice the scaling is empirically beneficial regardless.

## 7. Connection to our work

The Recurrent ViT (2502.10955) starts from precisely the Transformer encoder layer and augments it with a spatially organized memory module that feeds back into self-attention. Vaswani's multi-head, key/query/value structure (eqs. 14 in our paper) is preserved; what's added is recurrence (LSTM-style updates) and three different schemes for injecting memory contents (concatenation, additive, multiplicative; §6.7 of our paper). The architectural contribution of our paper is therefore best understood as adding recurrence and memory feedback to Vaswani's primitive, not replacing it.

PRISM v1 explicitly *rejects* the self-attention primitive — there is no $\text{softmax}(QK^\top/\sqrt{d_k})$ anywhere in the architecture. The interpretable attention map in PRISM is instead the per-location prediction-error magnitude. Vaswani et al.'s paper is therefore the foil for PRISM's central architectural claim.

PRISM v2 brings the multi-head idea back, but reinterpreted. `PRISM_V2_PROPOSAL.md` §3.6 partitions the feature decoder into $K$ heads, each predicting a disjoint subset of feature channels. The per-head prediction-error map is the v2 analog of a multi-head attention map — but derived from a generative model rather than learned softmax weights. Voita et al.'s (2019) analysis of head specialization in transformers (`voita2019_head_specialization`) is the specific motivation for expecting the partition to produce specialized heads.

Bitter-lesson framing: Vaswani et al. is the canonical example of a scalable architecture with a single objective (cross-entropy) that produces state-of-the-art results without task-specific inductive bias — precisely the standard PRISM aspires to (`THESIS.md` §1.4).

## 8. Citations to follow

- `dosovitskiy2020_vit` — Vision Transformer. The application of Transformer encoder to image patches. Our Recurrent ViT is built on this.
- `voita2019_head_specialization` — head specialization analysis, the motivation for PRISM v2's multi-head saliency partition.
- `bahdanau2014_neural_translation` — the additive-attention precursor to Vaswani's dot-product attention; not currently in the seed set but should be added.
- `khan2022_transformers_vision_survey` — survey of how the Transformer has been applied across vision; useful for situating the Recurrent ViT in the broader ViT literature.
- `tay2022_efficient_transformers_survey` — survey of efficient attention variants (linear, sparse, etc.); not currently in seed, candidate for addition.
