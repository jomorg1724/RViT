---
id: assran2023_ijepa
title: "Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture (I-JEPA)"
authors:
  - "Assran, Mahmoud"
  - "Duval, Quentin"
  - "Misra, Ishan"
  - "Bojanowski, Piotr"
  - "Vincent, Pascal"
  - "Rabbat, Michael"
  - "LeCun, Yann"
  - "Ballas, Nicolas"
year: 2023
venue: "CVPR 2023"
doi: "10.1109/CVPR52729.2023.01499"
arxiv: "2301.08243"
url: "https://arxiv.org/abs/2301.08243"
tags:
  - self-supervised-learning
  - jepa
  - vision-transformers
  - latent-prediction
  - non-generative
  - masked-image-modeling
concepts:
  - hierarchical_predictive_coding
  - coupled_rnn_world_models
  - iterative_variational_encoder_decoder
  - prediction-error-map
related:
  - bardes2023_vjepa
  - lecun2022_path_to_agi
  - hafner2023_dreamerv3
  - schrittwieser2020_muzero
  - friston2010_fep_unified_theory
  - rao_ballard1999_predictive_coding
  - vaswani2017_attention
  - dosovitskiy2020_vit
relevance_to:
  - prism_v2
  - rvit_plus
seed_source:
  - manual_deep_dive_2026_05_23
status: full
depth: full
last_updated: "2026-05-23"
---

# Self-Supervised Learning from Images with a Joint-Embedding Predictive Architecture (I-JEPA)

## 1. Abstract

> "This paper demonstrates an approach for learning highly semantic image representations without relying on hand-crafted data-augmentations. We introduce the Image-based Joint-Embedding Predictive Architecture (I-JEPA), a non-generative approach for self-supervised learning from images. The idea behind I-JEPA is simple: from a single context block, predict the representations of various target blocks in the same image. A core design choice to guide I-JEPA towards producing semantic representations is the masking strategy; specifically, it is crucial to (a) sample target blocks with sufficiently large scale (semantic), and to (b) use a sufficiently informative (spatially distributed) context block. Empirically, when combined with Vision Transformers, we find I-JEPA to be highly scalable. For instance, we train a ViT-Huge/14 on ImageNet using 16 A100 GPUs in under 72 hours to achieve strong downstream performance across a wide range of tasks, from linear classification to object counting and depth prediction." (Assran, Duval, Misra, Bojanowski, Vincent, Rabbat, LeCun & Ballas 2023, *CVPR*, abstract.)

## 2. Why this matters for us

I-JEPA is the *image-domain instantiation* of the JEPA program: latent-space prediction (not pixel reconstruction) for self-supervised representation learning. For the user's program, this is one of the most architecturally consequential modern vision papers because it sits in the same architectural design space as the user's [iterative_variational_encoder_decoder](../concepts/iterative_variational_encoder_decoder.md): a context-encoder + target-encoder + predictor architecture trained to predict latent embeddings rather than pixels. The user's program inherits the JEPA architectural commitment — *predict in latent space* — from the same lineage (LeCun's position paper, V-JEPA, I-JEPA). I-JEPA also matters because it provides clean empirical evidence that latent-prediction representations are *more semantic* (better for downstream high-level tasks) than pixel-prediction representations (MAE), validating the design choice. For the user's program, this is a load-bearing empirical anchor for *latent-prediction* as the right self-supervised signal for the iterative VAE.

## 3. Key claims

1. Self-supervised representations *need neither pixel reconstruction nor hand-crafted view augmentation* — latent-space prediction is sufficient.
2. *Predicting in representation space yields more semantic features* than predicting in pixel space (MAE) — empirical demonstration of the LeCun JEPA claim.
3. *Block-level masking with large semantic targets + informative spatially distributed context* is essential — the masking strategy is what makes JEPA work in images.
4. I-JEPA is *highly compute-efficient* relative to data-augmentation methods (DINO, iBOT) and generative methods (MAE).
5. The architecture instantiates the JEPA template (predictor on top of encoded latents with a stop-gradient target encoder) — an alternative to contrastive and generative SSL.
6. *Strong transfer to low-level tasks* (depth, counting) where contrastive methods underperform — JEPA representations capture *both* semantic and geometric content.
7. *Continues to scale with model size* up to ViT-G/16, providing scaling-law evidence.
8. *No representation collapse* is observed despite the absence of explicit anti-collapse losses, due to the EMA target encoder.

## 4. Methods

I-JEPA uses three ViT networks. (i) A *context encoder* $f_\theta$ that processes a single sampled context block of patches from an image — typically scale 0.85-1.0 of the image, with target patches masked out. (ii) A *target encoder* $f_{\bar\theta}$ that is an EMA of the context encoder weights (stop-gradient applied to the target encoder; its weights only update via momentum), processing the *full* image and from which 1-4 large target blocks are extracted — typically scale 0.15-0.2 with aspect ratio 0.75-1.5. (iii) A *predictor* $g_\phi$ (a small ViT, ~5% the size of the context encoder) that, conditioned on positional tokens (where in the image the target block sits), predicts the target-block embeddings from the context embedding. Loss is the *smooth L1* between predicted and target patch-level embeddings: $L = \|g_\phi(f_\theta(\text{context}), \text{pos}) - \text{sg}(f_{\bar\theta}(\text{image}, \text{pos}))\|$. No data augmentations beyond a single random crop and horizontal flip; the architectural choice of which blocks to predict is what shapes the learned representations. The target encoder receives no gradient — its weights only update via EMA, which is the anti-collapse mechanism.

## 5. Results

Headline quantitative results:

- **ViT-H/14, 224×224, 300 epochs, 16 A100 GPUs, ~72 hours** — significantly cheaper than data2vec (~16 nodes) at comparable downstream performance.
- **ImageNet linear probe:** 77.3% (ViT-H/14) at 224; 77.5% (ViT-H/16) at 448 — comparable to iBOT, exceeding MAE (~76.6%).
- **ImageNet-1% semi-supervised linear:** I-JEPA ViT-H/14 = 73.3%, exceeding MAE (~71%).
- **Low-shot 1% labels (logistic):** 66.6% vs MAE 51.1% — substantial improvement in label-efficient regimes.
- **Depth prediction (NYUv2 RMSE):** better than MAE and on par with iBOT — JEPA captures geometric content.
- **Object counting (Clevr/Count):** I-JEPA outperforms iBOT, DINO, and MAE by 3-8 points — strong on tasks requiring spatial reasoning.
- **10× lower compute** than DINO/iBOT for comparable linear accuracy — the headline efficiency claim.
- **Continues to scale with model size up to ViT-G/16** — scaling-law evidence for the architecture.

## 6. Critique / limitations

I-JEPA is influential but has well-documented gaps.

- **Lags pure contrastive/self-distillation methods (DINOv2) on ImageNet linear probe** by a few points at matched scale — JEPA is not the SOTA for pure linear-probe classification.
- **Predictor design is task-agnostic but adds non-trivial hyperparameter cost** (block sampling distributions, number of targets) — the apparent "no hand-crafted augmentation" framing hides architectural hyperparameters.
- **Requires a careful EMA schedule for the target encoder**; instability if EMA momentum is wrong.
- **Evaluation focused on ImageNet-pretrained representations**; domain transfer (medical, satellite, video) less explored in this paper (though V-JEPA extends to video).
- **Block-masking is image-only**; extending to video required substantial redesign (V-JEPA).
- **No explicit prevention of representation collapse beyond EMA + masking** — collapse risk under aggressive crop ratios or other architectural perturbations.
- **Despite "no augmentations" framing, still relies on resizing and normalization** that act as data augmentations — the claim is somewhat marketing.
- **Predictor conditioning on positional tokens is somewhat hand-engineered** for the masking pattern — the predictor is bespoke to the chosen masking strategy.

## 7. Connection to our work

I-JEPA is one of the most architecturally consequential modern vision papers for the user's program because it sits in the same architectural design space as the iterative VAE.

**Touchpoint 1: latent-space prediction as the architectural commitment.** I-JEPA's central architectural commitment — predict in latent space, not in pixel space — is the same commitment the user's [iterative_variational_encoder_decoder](../concepts/iterative_variational_encoder_decoder.md) should make. The user's iterative VAE, configured to predict in its own encoder's latent space rather than at the pixel level, is in the I-JEPA architectural family. I-JEPA provides the empirical evidence that this commitment produces *more semantic* representations than pixel prediction — a load-bearing empirical anchor for the user's iterative VAE design.

**Touchpoint 2: context-encoder + predictor architecture — the user's iterative VAE structure.** I-JEPA's context-encoder + predictor architecture is structurally analogous to the user's iterative VAE: the encoder produces a guide representation, and the iterative refinement passes (or, in I-JEPA's case, the predictor) reconstruct or predict from that guide. The user's program inherits the architectural pattern: a primary encoder that produces a representation, and a secondary predictor/decoder that operates on that representation. I-JEPA is one instance of this pattern; the user's program is another, with additional commitments (multi-compartment memory, iterative refinement, multi-hub competition).

**Touchpoint 3: masking strategy — the architectural insight for the user's program.** I-JEPA's key empirical insight — block-level masking with large semantic targets and informative spatially distributed context — has a direct architectural implication for the user's program. When training the user's models with a JEPA-style auxiliary loss, the masking strategy matters: large semantic blocks (not random patches) and informative context (not random patches) produce *more semantic* representations. The architectural recommendation: any JEPA-style auxiliary loss in the user's program should use semantic block-masking, not random masking.

**Touchpoint 4: EMA target encoder as the anti-collapse mechanism.** I-JEPA's EMA target encoder is the principal anti-collapse mechanism (no contrastive loss, no explicit anti-collapse regularizer). The user's program, if it adds a JEPA-style auxiliary loss, should adopt the EMA target mechanism: a slow-updating copy of the encoder serves as the target, preventing the optimization from collapsing all representations to a constant. This is a *low-cost architectural addition* with strong empirical backing.

**Touchpoint 5: scaling-law evidence — compute scales monotonically.** I-JEPA's monotonic scaling — larger models monotonically improve downstream performance — is empirical evidence that the user's program should not be conservative on model size for the iterative VAE. The user's commitment to additional architectural complexity (multi-compartment memory, FT integration, etc.) implies more parameters; I-JEPA's scaling evidence licenses this investment. The architectural commitment to scaling is consistent with the modern self-supervised vision lineage.

**Touchpoint 6: convergence with V-JEPA — the temporal extension.** I-JEPA is the image-domain JEPA; [bardes2023_vjepa](bardes2023_vjepa.md) is the video-domain extension. The user's program operates in the video domain (or at least sequential-vision domain), so V-JEPA is the more directly relevant comparison. I-JEPA matters because it establishes the JEPA architectural template at the simplest (single-image) level; V-JEPA scales the template to video. The user's program inherits the template through both papers and applies it to the user's iterative-VAE-with-recurrent-memory architecture.

**Touchpoint 7: low-level task performance (depth, counting) — JEPA captures geometric content.** I-JEPA's strong performance on low-level tasks (depth, counting) is the empirical demonstration that JEPA representations capture *both* semantic and geometric content. This addresses a common worry about latent-prediction methods: do they discard the geometric detail necessary for spatial reasoning? I-JEPA shows they do not — the latent-prediction representations are *richer* than pixel-prediction representations even for spatial tasks. The user's program inherits this evidence: the iterative VAE with latent-prediction auxiliary loss should support both semantic and geometric downstream tasks.

**Touchpoint 8: integration with the user's multi-hub program — the JEPA hub as a primary architectural component.** In the user's [multi_hub_multi_objective_system](../concepts/multi_hub_multi_objective_system.md), a *JEPA-style hub* is one of the candidate hubs (alongside RL, reconstruction VAE, etc.). I-JEPA provides the architectural blueprint for what this hub should look like: a context-encoder + predictor + EMA target architecture, trained on latent prediction with semantic block masking. The hub's loss contributes to the multi-objective training, and the hub's representations (the context encoder's outputs) are made available to other hubs via the central self-attention substrate. This is a concrete architectural specification for the JEPA hub in the user's program.

## 8. Citations to follow

- [bardes2023_vjepa](bardes2023_vjepa.md) — V-JEPA; the video-domain extension. In seed.
- `garrido2024_world_models_visual_representation_icml` — *ICML* — learning and leveraging world models in visual representation learning. Not in seed.
- `oquab2024_dinov2_tmlr` — *TMLR* — DINOv2: learning robust visual features without supervision; the competing direction. Not in seed.
- `baevski2023_data2vec2_icml` — *ICML* — data2vec 2.0; the related target-prediction method. Not in seed.
- [lecun2022_path_to_agi](lecun2022_path_to_agi.md) — the LeCun JEPA position paper this work instantiates. In seed.
- `bardes2022_vicreg_iclr` — *ICLR* — VICReg: variance-invariance-covariance regularization; often used to stabilize JEPA training. Not in seed.
- `sobal2023_jepa_slow_features` — JEPAs focus on slow features. Not in seed.
- `fini2024_latent_masked_image_modeling_cvpr` — *CVPR* — latent masked image modeling with linear probing. Not in seed.
- `singh2024_hidden_representations_jepa_iclr_ws` — *ICLR workshop* — hidden representations of JEPA models. Not in seed.
- `walmer2024_teaching_matters_cvpr` — *CVPR* — uses I-JEPA as comparison. Not in seed.
- [vaswani2017_attention](vaswani2017_attention.md) — the Transformer paper; underlying architecture. In seed.
- [dosovitskiy2020_vit](dosovitskiy2020_vit.md) — the ViT paper; underlying architecture. In seed.
- [hafner2023_dreamerv3](hafner2023_dreamerv3.md) — DreamerV3; the pixel-reconstruction contrast. In seed.
- [friston2010_fep_unified_theory](friston2010_fep_unified_theory.md) — the free-energy principle that motivates latent prediction. In seed.
- [rao_ballard1999_predictive_coding](rao_ballard1999_predictive_coding.md) — the foundational predictive-coding paper. In seed.
