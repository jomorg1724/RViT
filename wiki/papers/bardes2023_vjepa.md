---
id: bardes2023_vjepa
title: "V-JEPA: Latent Video Prediction for Visual Representation Learning"
authors:
  - "Bardes, Adrien"
  - "Garrido, Quentin"
  - "Ponce, Jean"
  - "Chen, Xinlei"
  - "Rabbat, Michael"
  - "LeCun, Yann"
  - "Assran, Mido"
  - "Ballas, Nicolas"
year: 2023
venue: "arXiv preprint / Meta AI"
doi: ""
arxiv: ""
url: ""
tags:
  - self-supervised-learning
  - world-models
  - predictive-coding
  - vision-transformers
concepts:
  - generative-decoder
  - prediction-error-map
  - hierarchical-predictive-coding
  - coupled-rnn-world-models
  - iterative-variational-encoder-decoder
related:
  - dosovitskiy2020_vit
  - rao_ballard1999_predictive_coding
  - friston2010_fep_unified_theory
  - vaswani2017_attention
  - lecun2022_path_to_agi
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_32
status: full
depth: full
last_updated: "2026-05-16"
---

# V-JEPA: Latent Video Prediction for Visual Representation Learning

## 1. Abstract

V-JEPA (Video Joint-Embedding Predictive Architecture) is a self-supervised video representation learning method that trains a vision encoder by predicting *embeddings* of masked future frames rather than reconstructing pixels. A context encoder processes a visible portion of a video clip; a predictor network produces predicted embeddings for masked spatiotemporal locations; a separately maintained target encoder (typically an EMA of the context encoder) produces target embeddings for the same locations. The training loss is the squared error between predicted and target embeddings. By predicting in latent space rather than pixel space, V-JEPA bypasses the need to model pixel-level appearance details and produces representations that transfer well to downstream tasks (action recognition, motion prediction). The architecture is a ViT applied to spatiotemporal patches.

## 2. Why this matters for us

V-JEPA is explicitly cited in the Recurrent ViT paper (`[32]` in 2502.10955) as the closest contemporary architecture using predictive coding as the self-supervised signal for vision. The paper makes the contrast: V-JEPA processes entire image sequences without selective encoding, providing continuous access to past stimuli; the Recurrent ViT, in contrast, imposes a recurrent bottleneck where memory and attention must be selectively allocated. V-JEPA is therefore the principal *predictive-coding* contrast architecture to both our papers — it shows what a predictive-coding-based vision model looks like without the working-memory bottleneck PRISM and Recurrent ViT both implement.

## 3. Key claims

1. Self-supervised vision representations can be learned by predicting latent embeddings rather than pixels, sidestepping the "pixel-level appearance" trap that plagues reconstructive methods like MAE.
2. The joint-embedding predictive architecture — separate context and target encoders, with the predictor mapping context to target embeddings — is a flexible framework that subsumes BYOL, DINO, and related methods.
3. Spatiotemporal patch tokenization plus ViT processing produces video representations that transfer to action recognition, motion prediction, and other downstream tasks.
4. Latent prediction outperforms pixel prediction on representation-quality benchmarks at matched compute.
5. The method is fully self-supervised; no labels, no manual augmentations beyond random cropping, no curriculum.

## 4. Methods

Input is a video clip; spatiotemporal patches (e.g., 16×16×2 pixel-frame blocks) are tokenized. A masking strategy selects a context (visible) region and a set of target (masked) locations.

The context encoder $f_\theta$ is a ViT that processes the visible patches and produces context embeddings. The predictor $g_\phi$ is a smaller Transformer that takes context embeddings plus positional information about target locations and produces predicted embeddings for those locations.

The target encoder $f_{\bar\theta}$ is an EMA of $f_\theta$: $\bar\theta \gets \alpha \bar\theta + (1-\alpha)\theta$ at each step. It processes the same video (with all patches visible) and produces target embeddings at the target locations.

The training loss is $L = \sum_\text{targets} \| g_\phi(f_\theta(\text{context}), \text{pos}) - \text{sg}(f_{\bar\theta}(\text{video}, \text{pos})) \|^2$, where $\text{sg}$ is stop-gradient. The target encoder receives no gradient — its weights only update via EMA.

This avoids the trivial-solution problem (collapse to constant embeddings) by virtue of the EMA target: any collapse must propagate slowly through the EMA, and gradient-based optimization prefers non-collapsed solutions.

## 5. Results

V-JEPA achieves state-of-the-art frozen-features results on multiple video benchmarks:

- Kinetics-400 action recognition: top-1 ~80% with ViT-Huge frozen features.
- Something-Something v2 (motion-focused): substantial improvement over pixel-prediction baselines.
- Linear probe on ImageNet (from video pretraining): competitive with image-only methods.

The headline claim is that latent prediction provides a more efficient self-supervised signal than pixel prediction at matched compute. Specifically, V-JEPA outperforms VideoMAE on a variety of downstream tasks with comparable architecture and training budget.

The architecture transfers to image tasks (e.g., ImageNet linear probe) without modification, suggesting the learned representations are not video-specific.

## 6. Critique / limitations

The EMA-target trick is essential to avoid collapse but is not fully understood theoretically. Why does the EMA target prevent collapse? Pure mathematical accounts exist (the "negative momentum" interpretation) but they assume the optimization landscape is benign. In practice the method works but its training dynamics are sensitive to the EMA rate and the predictor architecture.

V-JEPA is *not* a sequential decision-making architecture. It learns representations from video clips offline; there is no agent, no action, no reward. Applying V-JEPA to an RL setting (the regime our papers address) requires additional architectural commitments — exactly the gap our recurrent architectures aim to fill.

The "continuous access to past stimuli" property our paper cites is both a feature (rich temporal context) and a limitation (no selective encoding, no working-memory bottleneck). For modeling biological working memory or attention, the lack of a capacity-limited memory is a substantial architectural mismatch.

The latent space V-JEPA learns is not interpretable. Whereas PRISM's prediction-error map $S_t$ has a direct attention-map interpretation, V-JEPA's embedding-prediction errors are in a learned latent space with no obvious spatial or feature-level structure.

## 7. Connection to our work

V-JEPA and PRISM are conceptual cousins: both use prediction in latent space (PRISM's feature-PC term is essentially this) as a self-supervised signal. The differences are architectural:

- **PRISM** has a recurrent memory bottleneck that compresses the entire past into a fixed-size $M_t$ at each step. V-JEPA processes the entire spatiotemporal video clip as input at every step (no bottleneck).
- **PRISM** has a single objective (variational free energy) jointly optimized with PPO for action selection. V-JEPA has only the self-supervised loss; there is no agent, no policy.
- **PRISM** explicitly computes a per-location prediction-error map used for attention readout. V-JEPA's prediction error is in latent space and has no spatial-map interpretation.
- **PRISM** uses both pixel-level and feature-level prediction losses (`THESIS.md` §2.11). V-JEPA uses only latent prediction; the original V-JEPA paper does not have a pixel-PC term.

The Recurrent ViT paper cites V-JEPA at `§1` of 2502.10955 as the contrast architecture that motivates the need for selective encoding: "Although this approach may capture certain aspects of visual working memory, the continuous access to past stimuli (or their compressed representations) reduces the need for selective encoding and storage." This is precisely the architectural axis on which the Recurrent ViT (with its LSTM memory bottleneck) and PRISM (with its $M_t$ bottleneck) differ from V-JEPA.

If V-JEPA were extended with a recurrent memory bottleneck and an RL action head, the result would be architecturally similar to PRISM v2 — modulo the EMA-target trick and the absence of an explicit saliency readout. This is one of the most natural future-work directions for both lines of research.

## 8. Citations to follow

- `assran2023_ijepa` — the image-only predecessor (I-JEPA); candidate for addition.
- `grill2020_byol` — BYOL, the EMA-target self-supervised trick V-JEPA inherits; candidate for addition.
- `caron2021_dino` — DINO, another joint-embedding self-supervised method; cited in our paper as `[31]`.
- `tong2022_videomae` — pixel-prediction baseline; candidate for addition.
- `lecun2022_path_to_agi` — LeCun's position paper proposing JEPA as the path to AGI; candidate for context.
