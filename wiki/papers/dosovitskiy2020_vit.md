---
id: dosovitskiy2020_vit
title: "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale"
authors:
  - "Dosovitskiy, Alexey"
  - "Beyer, Lucas"
  - "Kolesnikov, Alexander"
  - "et al."
year: 2020
venue: "ICLR 2021 (arXiv 2020)"
doi: ""
arxiv: "2010.11929"
url: "https://arxiv.org/abs/2010.11929"
tags:
  - transformers
  - vision-transformers
  - deep-learning
concepts:
  - self-attention-over-tokens
  - scaled-dot-product-attention
  - multi-head-attention
  - gridcell-rnn
  - iterative-variational-encoder-decoder
related:
  - vaswani2017_attention
  - khan2022_transformers_vision_survey
  - bardes2023_vjepa
  - mehrani_tsotsos2023_attention_grouping
  - yamamoto2024_human_like_vit_attention
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_24
status: full
depth: full
last_updated: "2026-05-16"
---

# An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale (ViT)

## 1. Abstract

The Vision Transformer (ViT) applies the standard Transformer encoder (Vaswani et al. 2017) directly to image classification with minimal modification. Images are split into fixed-size patches (typically 16×16 pixels), each patch is linearly projected to a token embedding, learned positional embeddings are added, and the resulting sequence of tokens is processed by a stack of Transformer encoder layers. A learnable `[CLS]` token aggregates information for classification. When pre-trained on large datasets (ImageNet-21k or JFT-300M) and fine-tuned to ImageNet-1k, ViT matches or exceeds the accuracy of state-of-the-art ResNet models while requiring substantially fewer pre-training FLOPs. The paper establishes that, given sufficient data, pure attention-based vision models can replace the inductive biases of convolutions.

## 2. Why this matters for us

ViT is the direct architectural ancestor of the Recurrent ViT (2502.10955). The Recurrent ViT replaces the feedforward Transformer encoder with a recurrent variant that incorporates spatial working memory feedback into the self-attention mechanism (§7 of our paper). Without ViT, the Recurrent ViT would have no baseline architectural target. ViT is also the explicit foil for PRISM v1, which removes the softmax-attention primitive ViT relies on. The patch-based input parsing in our paper (`§6.2` of 2502.10955: $\mathbf{o}^{(t)} \to \{\mathbf{o}_i^{(t)}\}_{i=1}^{n_\text{patch}}$) is the ViT patch-tokenization procedure.

## 3. Key claims

1. Pure self-attention, without convolutions, can match or exceed CNN performance on image classification when scaled to sufficient pre-training data.
2. The inductive bias of convolutions (translation equivariance, locality, hierarchy) is not necessary for vision; it can be replaced by data scale and the global receptive field of self-attention.
3. The transition between "CNNs win" and "Transformers win" occurs around the JFT-300M scale; on ImageNet-1k alone, CNNs remain competitive.
4. ViT scales smoothly with data and compute, in contrast to CNNs whose returns diminish at the same scales.
5. The architecture is essentially the unmodified Transformer encoder — the contribution is the demonstration that no vision-specific modification is needed.

## 4. Methods

Images are split into a grid of non-overlapping patches (typically 16×16 pixels). Each patch is flattened to a vector and linearly projected to the model dimension $d_\text{model}$ (768 for ViT-Base, 1024 for ViT-Large). Learnable positional embeddings are added. A learnable `[CLS]` token is prepended to the sequence.

The token sequence (length $n_\text{patch} + 1$) is passed through a stack of $N$ Transformer encoder layers, each with multi-head self-attention and an MLP block, residual connections, and LayerNorm. The final `[CLS]` token output is fed to a linear classification head.

Training is two-stage: large-scale pre-training (ImageNet-21k or JFT-300M), then fine-tuning on the target task (ImageNet-1k, CIFAR, etc.). The model is trained with AdamW; the standard training tricks (label smoothing, dropout, gradient clipping) are used.

Three model sizes are released: ViT-Base (12 layers, 86M params), ViT-Large (24 layers, 307M params), ViT-Huge (32 layers, 632M params).

## 5. Results

On ImageNet-1k (after JFT-300M pre-training and ImageNet-1k fine-tuning):

- ViT-Large achieves 85.3% top-1 accuracy, exceeding the best ResNet baseline (BiT-L at 84.3%).
- ViT-Huge achieves 88.5% top-1.
- Pre-training compute is approximately 4× less than BiT-L for matched accuracy.

When pre-trained on smaller datasets (ImageNet-1k or ImageNet-21k), ViT underperforms ResNets — the architectural bias of convolutions matters at small data scales but is dominated by data scale at large ones.

Ablations show:

- 16×16 patches outperform smaller patches at matched compute (smaller patches blow up the sequence length).
- Class token versus global average pool over tokens performs similarly.
- Learned positional embeddings work; sinusoidal 2D embeddings work; no positional information catastrophically fails.

## 6. Critique / limitations

ViT's data hunger is the principal limitation: state-of-the-art performance requires JFT-300M pre-training, a dataset not publicly available. Subsequent work (DeiT, Touvron et al. 2021) showed that with the right training recipe and augmentation, ImageNet-1k alone can suffice, partially closing this gap.

The $O(n^2)$ scaling with sequence length is the same problem as in NLP Transformers. For high-resolution images, the sequence becomes prohibitive; subsequent work (Swin Transformer, hierarchical ViTs) addresses this with windowed attention.

For the biological-attention question that motivates our Recurrent ViT: ViT's attention maps are not particularly human-like (Mehrani & Tsotsos 2023 argue they perform perceptual grouping, not goal-directed selection). The lack of top-down modulation, working memory, and recurrence is the principal limitation our Recurrent ViT addresses.

ViT is feedforward in the strong sense: every layer sees the entire image at once via attention. There is no notion of sequential processing, no recurrence, no temporal dynamics. For video or sequential decision-making, additional architectural commitments are required — exactly what V-JEPA (Bardes et al. 2023) and our Recurrent ViT explore.

## 7. Connection to our work

The Recurrent ViT is structurally a ViT encoder with several modifications:

- A VAE pre-processing stage (`§7.1` of 2502.10955) replaces the raw patch linear projection with a learned latent code. This was empirically necessary for RL training; raw patches gave worse performance.
- The image is parsed into exactly four patches corresponding to the four Gabor-stimulus quadrants (`§6.2`: $n_\text{patch} = 4$, patches of 25×25 pixels). This is far fewer tokens than standard ViT but matches the task's spatial structure.
- The self-attention mechanism is augmented with recurrent memory feedback (`§6.7`, three variants: token-concat, additive, multiplicative). Self-attention now attends over both visual patches and memory patches, with the memory contents biasing the attention weights. This is the principal architectural contribution.
- The downstream architecture is a patch-based LSTM that maintains a spatially-organized working-memory state, with an actor-critic policy on top.

The interpretability advantage emphasized in our paper — that ViT's attention map can be visualized per-patch — is inherited directly from Dosovitskiy et al.'s architecture. Specifically, the $\alpha_{ij}^{(t)}$ matrix in our paper (Eq. 5) is the standard ViT attention matrix, just with the inputs modified by recurrent memory contributions.

PRISM v1 is the architectural antagonist of ViT. It explicitly does *not* contain the $\text{softmax}(QK^\top/\sqrt{d_k})$ primitive (`THESIS.md` §1.2). Its interpretable "attention" map is the per-location prediction-error magnitude $S_t$, not a learned softmax. The two papers therefore represent the same experimental task tackled with opposite architectural commitments — Recurrent ViT keeps softmax-attention and adds memory; PRISM removes softmax-attention and uses predictive coding.

## 8. Citations to follow

- `vaswani2017_attention` — the Transformer paper ViT is built on.
- `khan2022_transformers_vision_survey` — survey contextualizing ViT in the broader vision-Transformer literature.
- `mehrani_tsotsos2023_attention_grouping` — critique that ViT attention performs perceptual grouping, not goal-directed selection.
- `yamamoto2024_human_like_vit_attention` — recent eye-tracking study comparing ViT attention to human gaze.
- `touvron2021_deit` — DeiT, the data-efficient ViT training recipe; not currently in seed, candidate for addition.
- `caron2021_dino` — DINO self-supervised ViT producing human-like attention maps; cited in our paper as `[31]` but currently keyed to a different reference — verify.
