---
id: yamamoto2024_human_like_vit_attention
title: "Emergence of human-like attention in self-supervised vision transformers"
authors:
  - "Yamamoto, Takuto"
  - "Akahoshi, Hirosato"
  - "Kitazawa, Shigeru"
year: 2024
venue: "arXiv:2410.22768 (Neural Networks, 2025)"
doi: ""
arxiv: "2410.22768"
url: "https://arxiv.org/abs/2410.22768"
tags:
  - vision-transformers
  - self-supervised-learning
  - visual-attention
  - human-neuroimaging
concepts:
  - self-attention-over-tokens
  - multi-head-attention
  - figure-ground-segmentation
  - attention-as-prediction-error
related:
  - dosovitskiy2020_vit
  - bardes2023_vjepa
  - vaswani2017_attention
  - kietzmann2019_recurrence_required
  - desimone_duncan1995_biased_competition
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_31
status: full
depth: full
last_updated: "2026-05-14"
---

# Emergence of human-like attention in self-supervised vision transformers

## 1. Abstract

Many models of visual attention have been proposed so far. Traditional bottom-up models, like saliency models, fail to replicate human gaze patterns, and deep gaze-prediction models lack biological plausibility due to their reliance on supervised learning. Vision Transformers (ViTs), with their self-attention mechanisms, offer a new approach but often produce dispersed attention patterns if trained with supervised learning. This study explores whether self-supervised DINO (self-DIstillation with NO labels) training enables ViTs to develop attention mechanisms resembling human visual attention. Using video stimuli to capture human gaze dynamics, we found that DINO-trained ViTs closely mimic human attention patterns, while those trained with supervised learning deviate significantly. An analysis of self-attention heads revealed three distinct clusters: one focusing on foreground objects, one on entire objects, and one on the background. DINO-trained ViTs offer insight into how human overt attention and figure-ground separation develop in visual perception.

## 2. Why this matters for us

This is the closest published empirical parallel to the Recurrent ViT paper's (2502.10955) central biological claim: that a transformer's self-attention map, read off directly without auxiliary saliency training, can be aligned with primate / human overt attention. Yamamoto et al. demonstrate this alignment with a self-supervised ViT (DINO) on free-viewing of video, while the Recurrent ViT demonstrates a related alignment with an RL-trained recurrent ViT on a change-detection task. Together the two papers triangulate the architectural claim from two different training paradigms and two different behavioral regimes. The paper also supplies direct evidence that *the training objective matters*: supervised classification ViTs produce diffuse, human-unlike attention, while self-supervised DINO ViTs produce focused, object-centered attention — a result that bears on whether PRISM's predictive objective should yield more human-like attention than a classification objective on the same backbone. Finally, the three functional head clusters (foreground / whole-object / background) are an emergent figure-ground decomposition that anticipates the Feedback Transformer's commitment to functional head specialization (thread §1) and the user's competition-emergent predictive-coding thesis (thread §5).

The result also supplies an *empirical motivation* for the architectural design choice underlying both the Recurrent ViT and PRISM v2: to read attention out of self-attention dynamics directly, rather than train a separate saliency head. If a transformer's self-attention map natively aligns with human attention (Yamamoto et al.) and with primate change-detection attention (Recurrent ViT 2502.10955), then a dedicated saliency-prediction module is architecturally redundant.

## 3. Key claims

1. Self-supervised DINO training produces ViT self-attention patterns that quantitatively resemble human overt attention measured by eye-tracking on free-viewing of video.
2. Supervised-classification ViTs with the same backbone produce dispersed, much less human-like attention — the alignment is a property of the *training objective*, not of the self-attention mechanism per se.
3. Across self-attention heads of the DINO ViT, three distinct functional clusters emerge: foreground-selective heads, whole-object heads, and background heads — a figure-ground decomposition that arises without supervision.
4. The figure-ground decomposition parallels classic primate accounts of attention as competition between figure and ground (Desimone & Duncan 1995), suggesting the same computational pressure (predictive self-distillation) recovers a similar functional partition.
5. Saliency-model baselines (bottom-up feature-anomaly models) and supervised deep-gaze-prediction baselines are each insufficient: the former lacks the top-down structure, the latter lacks biological plausibility because it requires gaze supervision.
6. The result demonstrates a biologically-plausible route to human-like attention: a self-supervised objective on natural images, with no labels and no gaze supervision, recovers the spatial structure of human overt attention as a byproduct of representation learning.

## 4. Methods

ViT backbones (small-patch variants of the standard architecture from Dosovitskiy et al. 2020, typically ViT-S/8 or ViT-S/16 in the DINO recipe) are trained under two regimes: (i) self-supervised DINO (Caron et al. 2021), in which a student network is trained to match the output of a teacher (an EMA of past student weights) on multiple augmented crops of the same image, with no labels; (ii) standard supervised classification on ImageNet. The trained models are then evaluated on a set of natural video stimuli for which human eye-tracking data have been collected during free viewing.

For each video frame, the [CLS]-token self-attention map of each head is read out from the final transformer block. This map is upsampled to image resolution and compared, per-frame, to a fixation density map computed from the eye-tracking data over a short temporal window. Standard saliency-evaluation metrics are used (correlation coefficient CC, normalized scanpath saliency NSS, AUC-style scores) to quantify the match between the model's attention map and human gaze. The video regime — as opposed to static image saliency benchmarks like MIT1003 or SALICON — exposes the model to gaze dynamics, including refixation and pursuit, that static benchmarks miss.

To characterize the head population, the authors cluster heads by the spatial statistics of their attention maps (e.g., focality, mass on foreground vs background regions delineated by object segmentation), recovering three reproducible clusters. The DINO ViT is compared to (a) the supervised ViT control with matched backbone, (b) classical bottom-up saliency models (Itti-Koch-family), and (c) supervised deep gaze-prediction models like DeepGaze.

A control important to the paper's interpretation is that DINO's [CLS] token is trained to match across multiple augmented crops of the same image; this is a self-distillation objective with no explicit supervision toward object-centered attention. Any object-centered structure in the resulting attention map must therefore emerge from the interaction between the self-distillation pressure, the multi-crop augmentation, and natural image statistics — not from a designed inductive bias toward foreground attention.

## 5. Results

The DINO-trained ViT's [CLS]-token attention map predicts human gaze on the video stimuli substantially better than the supervised-classification ViT control, and competitively with or exceeding standard saliency models. The advantage is robust across the saliency-evaluation metrics the paper reports. The supervised ViT, despite having the same architecture and similar ImageNet classification accuracy, produces diffuse attention maps that match human gaze much more weakly — a within-architecture isolation of the role of the training objective. Numerical values are reported per metric in the paper; the qualitative pattern across metrics is consistent.

The head-clustering analysis yields three reproducible functional clusters: (i) foreground-object-selective heads whose attention concentrates on the salient subject, (ii) whole-object heads whose attention covers full object extents (including extended limbs / contours), and (iii) background heads whose attention tiles non-object regions. These clusters appear without any segmentation supervision; they emerge from the self-distillation objective alone. The foreground-cluster heads are the ones whose attention maps most closely match human gaze.

The paper interprets the result as evidence that figure-ground separation — a prerequisite for object-based attention — emerges naturally from a self-supervised generative-like (self-distillation) objective on natural images, without explicit segmentation or gaze supervision.

A secondary observation is that the foreground-cluster heads tile the visual field in a way that is reminiscent of attentional spotlight models in primate vision: their attention concentrates on contiguous object-shaped regions whose centroid is a strong predictor of where humans next fixate. The whole-object cluster appears to extend this spotlight to cover the object's spatial support — a candidate for the "object-based attention" stage in Egly-Driver-style accounts. The background cluster is the complement and may be functioning as a normalization / context channel.

The supervised-ViT control is the most diagnostically important comparison. The same backbone, trained to classify ImageNet images instead of self-distill, produces attention maps that are diffuse and not aligned with object boundaries. This rules out a trivial explanation in which the ViT architecture *itself* produces human-like attention regardless of objective. The architecture is necessary but not sufficient; the objective contributes the structure. The fact that classification training is so much worse than DINO is, in retrospect, predictable from the discriminative-vs-generative distinction: classification objectives pressure the model to find any sufficient discriminative feature, which may be spatially diffuse or located on diagnostic details rather than whole objects (the well-known "shortcut learning" pathology). Self-distillation under multi-crop augmentation pressures the model to find features that are *invariant across crops of the same object*, which forces object-level spatial support.

## 6. Critique / limitations

The result is correlational: the alignment between DINO attention and human gaze is measured but not causally probed. The paper does not test whether perturbing the DINO attention map predicts a corresponding perturbation of human gaze, or whether the DINO ViT's attention map could be used to *generate* human-like scanpaths under a saccade-selection model. The comparison is at the level of fixation density, not gaze trajectory dynamics.

The training-objective comparison is between DINO and supervised classification; intermediate objectives (e.g., masked autoencoding, contrastive learning, video prediction) are not exhaustively tested. It is therefore not established that *predictive* self-supervision specifically is the relevant ingredient — only that *some* self-supervised objective (DINO) outperforms *one* supervised objective (classification). A more complete factorial design would cover {DINO, MAE, V-JEPA, SimCLR, classification, segmentation, detection} × {ViT-S/16, ViT-S/8, ViT-B/16} × {single-image, video} and report human-alignment metrics for each cell. As it stands, the paper supports the narrower claim that DINO-trained ViTs produce human-like attention, but leaves open whether the credit goes to DINO specifically or to the self-supervised family more broadly.

The architecture is feedforward — a standard ViT with no recurrence or top-down feedback. The figure-ground decomposition that emerges is therefore necessarily a single-pass, bottom-up phenomenon, even though primate figure-ground processing in V1/V2 is known to depend on feedback from extrastriate cortex (Lamme & Roelfsema 2000; Kietzmann et al. 2019). The paper does not address whether adding recurrence (à la Kietzmann 2019 or the Recurrent ViT 2502.10955) would strengthen or alter the alignment.

The video stimuli are natural but not task-driven; the eye-tracking is free-viewing. The paper does not test whether the same DINO attention map would align with goal-directed attention in tasks like visual search or change detection — regimes where top-down task signals are known to dominate gaze (Yarbus 1967; Henderson 2003). The Recurrent ViT paper (2502.10955) speaks to that complementary regime.

The "three clusters" claim depends on the clustering choice (k=3, the chosen feature space). The paper would be stronger with a hierarchical clustering analysis showing the dendrogram, or a clusterability statistic that would rule out a continuum interpretation of head function.

The paper does not characterize *which layer* the human-alignment is strongest in. DINO's [CLS]-token attention is typically read out from the final block, but earlier blocks may carry different attention structures. A layer-resolved analysis would speak to whether human-like attention is a property of the late, semantic representation, or whether it also appears in earlier, more retinotopic representations — relevant to whether human-like attention is a high-level prior or a low-level statistical regularity.

Finally, the eye-tracking comparison treats human gaze as ground truth, but human free-viewing gaze is itself influenced by an "implicit task" (the participant's idle interpretation of what the video is about). The paper does not separate task-influenced from genuinely bottom-up components of human gaze, which would be relevant to interpreting whether the DINO ViT is matching a bottom-up or a top-down structure in human attention.

There is also a residual concern about *what aspect* of human attention the DINO ViT is matching. The [CLS]-token attention map is a single static distribution over patches per frame; human gaze is a *sequential* trajectory through space, with serial dependencies (saccade momentum, inhibition of return). A high CC between the [CLS] map and the fixation-density map can be consistent with very different generative processes — for example, a model that fixates the same point continuously and a model that samples broadly from a similar distribution can produce the same density map. The paper does not test gaze-trajectory metrics (scanpath similarity, sequence-level DTW), which is precisely the regime where a recurrent ViT would be expected to add value over a feedforward one.

## 7. Connection to our work

This is the most direct empirical parallel to the Recurrent ViT paper's (2502.10955) biological claim, and the two papers should be read jointly as triangulation evidence for the architectural thesis.

**What Yamamoto et al. add that the Recurrent ViT does not.** (a) A *static-image / free-viewing* regime: their ViT is feedforward and operates on individual frames with no task instruction, isolating bottom-up plus learned-prior contributions to attention. (b) A *self-supervised* training objective (DINO): the model never sees labels of any kind, so the human-attention-like structure is purely a property of the self-distillation pressure plus natural image statistics. (c) A within-architecture ablation of the training objective (DINO vs supervised), isolating the contribution of the objective rather than the architecture.

**What the Recurrent ViT adds that Yamamoto et al. do not.** (a) A *task-driven* regime (change detection), where top-down attention is known to dominate gaze, and where supervised-attention saliency models systematically fail. (b) *Recurrence*: feedback of $H^{(t-1)}$ into self-attention (`2502.10955` §6.7), which is essential when the relevant attention signal evolves across time within a trial. (c) An *RL training objective*: the model receives only task reward, not gaze supervision and not labels, so the emergence of human-like attention is a strategic consequence of solving the task, not a property of the input statistics alone.

**Joint implication.** The two papers, taken together, suggest that human-like attention is *not* a special property of one training paradigm. It emerges from at least two distinct objectives (DINO self-distillation, RL on change detection) when paired with the transformer attention mechanism. This is a stronger claim than either paper makes alone: it argues that the *architecture* (self-attention over patch tokens) is the load-bearing ingredient, and that the human-attention-like structure is what self-attention converges to under *any* objective that requires the model to identify behaviorally-relevant subsets of the visual field. This is precisely the architectural thesis the user's program (`threads/the_user_architectural_program.md` §1) is built on. A natural further test is to repeat the Yamamoto comparison with the Recurrent ViT's training objective (RL on change detection) and to repeat the Recurrent ViT's primate-attention comparison with a DINO ViT; the architectural thesis predicts that both crossover experiments should still yield human/primate-like attention, while a training-objective-centric account would predict that each model is human-like only on the data regime it was trained for.

**Bearing on PRISM.** PRISM v1 and v2 do not use softmax-attention at all; they substitute prediction-error maps for the attention map. The Yamamoto result is a partial challenge to PRISM's no-attention commitment: it shows that a self-supervised ViT *with* softmax attention recovers human-like attention without prediction error in the architecture. The corresponding test for PRISM is whether its prediction-error map $S_t$ (`THESIS.md` §2.6) matches human gaze on the same video free-viewing benchmark as well as DINO's attention map does. If yes, PRISM's no-attention commitment is consistent with the data. If no, PRISM may need to reintroduce a softmax-attention readout — which is exactly the direction PRISM v2 takes (`PRISM_V2_PROPOSAL.md` §3.4).

**Bearing on the Feedback Transformer.** The three-cluster head decomposition (foreground / whole-object / background) is a piece of empirical evidence that *multiple heads* in self-attention are doing functionally distinct things — exactly the assumption the Feedback Transformer makes when it routes different feedback sources through different per-state Q/K/V projections (thread §1). The Yamamoto result is a within-head specialization that arises *without* the Feedback Transformer's mechanism; integrating multiple feedback streams as the Feedback Transformer does should, in principle, sharpen and stabilize this specialization. A concrete prediction: if a Feedback Transformer is trained on the same DINO objective, the head clusters should sharpen (lower within-cluster variance) and a fourth cluster — driven by the recurrent feedback channel — should appear.

**Bearing on biased competition.** The foreground vs background cluster split is a learned, architectural instantiation of the biased-competition framework (Desimone & Duncan 1995; `desimone_duncan1995_biased_competition.md`): the network has spontaneously developed sub-populations that compete for representational mass between figure and ground. The user's "competition-emergent predictive coding" thesis (`threads/the_user_architectural_program.md` §5) predicts exactly this: that competition for limited representational resources between coalitions of attention heads is the mechanism by which figure-ground separation, and ultimately predictive coding, arises. Yamamoto et al.'s clustering is a piece of empirical support for this thesis at the head-population level, even though the authors do not frame their result in those terms.

**Bearing on V-JEPA and other self-supervised video objectives.** V-JEPA (Bardes et al. 2023; `bardes2023_vjepa.md`) is a self-supervised *predictive* objective for video — predict the representation of a masked future region from a context region. The natural follow-up to Yamamoto et al. is whether a V-JEPA-trained ViT, on the same video eye-tracking benchmark, matches or exceeds DINO's human-attention alignment. The user's program predicts that V-JEPA should match or exceed DINO, because V-JEPA's objective is closer to the "predict the competitor / predict the world" pressure the user identifies as the source of human-like attention.

**Bearing on the recurrence-required claim.** Kietzmann et al. (`kietzmann2019_recurrence_required.md`) argue that recurrent computation is required to reproduce the temporal dynamics of primate ventral-stream responses to images. Yamamoto et al.'s feedforward DINO ViT recovers spatial human-attention alignment without recurrence, which does not contradict Kietzmann — the spatial structure of attention may be recoverable feedforward even if the *dynamics* of attention require recurrence. The Recurrent ViT paper (2502.10955) and the user's program both bet that recurrence is essential for matching the *temporal* signature of attention (within-trial evolution, attention re-engagement, refixation patterns). Yamamoto et al. is a complementary feedforward baseline; the open question is whether adding recurrence to a DINO ViT and re-running their analysis on the dynamic component of the gaze data would yield a further improvement on human alignment.

## 8. Citations to follow

- `caron2021_dino` — the DINO training method that is the load-bearing training objective in this paper. Not yet in the database; high-priority addition because it underwrites the central result.
- `oquab2023_dinov2` — DINOv2 successor; tests whether the human-alignment scales with the DINO recipe and a larger model. Candidate.
- `he2022_mae` — masked autoencoder ViT; a different self-supervised objective. Whether MAE produces similar human-alignment is a natural follow-up and isolates which self-supervised pressure matters.
- `itti_koch2001_saliency_model` — the bottom-up saliency baseline referenced in the abstract. Already a well-known reference in the saliency literature; candidate for stub.
- `lamme_roelfsema2000_feedforward_feedback` — figure-ground processing depends on cortical feedback; relevant counterpoint to the feedforward-DINO interpretation.
- `henderson2003_human_gaze_control` — task-driven vs free-viewing gaze; relevant for situating the paper's free-viewing regime against goal-directed attention.
- `bylinskii2019_saliency_metrics` — what we measure when we measure saliency: a methodological reference for the CC / NSS / AUC metric choices.
- `kummerer2018_deepgaze` — supervised deep-gaze-prediction baseline of the kind the paper argues against; candidate.
- `egly_driver_rafal1994_object_based_attention` — the classical "object-based attention" finding the whole-object cluster resembles; candidate.
- `yarbus1967_eye_movements` — the foundational demonstration that task instructions reshape gaze; relevant for the free-viewing vs task-driven dichotomy.
