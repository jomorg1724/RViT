---
id: zhuang2021_unsupervised_ventral
title: "Unsupervised neural network models of the ventral visual stream"
authors:
  - "Zhuang, Chengxu"
  - "Yan, Siming"
  - "Nayebi, Aran"
  - "Schrimpf, Martin"
  - "Frank, Michael C."
  - "DiCarlo, James J."
  - "Yamins, Daniel L. K."
year: 2021
venue: "PNAS"
doi: "10.1073/pnas.2014196118"
arxiv: ""
url: "https://www.pnas.org/doi/10.1073/pnas.2014196118"
tags:
  - deep-learning
  - neuro-ai-bridging
  - self-supervised-learning
  - representational-geometry
concepts:
  - ventral-stream-hierarchy
  - unsupervised-ventral-stream-model
  - representational-dissimilarity-matrix
related:
  - bardes2023_vjepa
  - dicarlo2012_object_recognition
  - kietzmann2019_recurrence_required
  - kriegeskorte2008_rsa
  - yamamoto2024_human_like_vit_attention
  - riesenhuber_poggio1999_hierarchical_models
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_112
status: full
depth: full
last_updated: "2026-05-16"
---

# Unsupervised neural network models of the ventral visual stream

## 1. Abstract

Deep neural networks currently provide the best quantitative models of the response patterns of neurons throughout the primate ventral visual stream. However, such networks have remained implausible as a model of the development of the ventral stream, in part because they are trained with supervised methods requiring many more labels than are accessible to infants during development. Here, we report that recent rapid progress in unsupervised learning has largely closed this gap. We find that neural network models learned with deep unsupervised contrastive embedding methods achieve neural prediction accuracy in multiple ventral visual cortical areas that equals or exceeds that of models derived using today's best supervised methods, and that the mapping of these neural network models' hidden layers is neuroanatomically consistent across the ventral stream. Strikingly, we find that these methods produce brain-like representations even when trained solely with real human child developmental data collected from head-mounted cameras, despite the fact that these datasets are noisy and limited. We also find that semisupervised deep contrastive embeddings can leverage small numbers of labeled examples to produce representations with substantially improved error-pattern consistency to human behavior. Taken together, these results illustrate a use of unsupervised learning to provide a quantitative model of a multiarea cortical brain system and present a strong candidate for a biologically plausible computational theory of primate sensory learning.

## 2. Why this matters for us

Zhuang et al. demonstrate that *self-supervised contrastive embedding* (local aggregation, instance recognition, SimCLR) can match or exceed supervised ImageNet networks as quantitative models of macaque V1, V4, and IT — closing the developmental-plausibility gap that has shadowed deep-network ventral-stream models since Yamins et al. 2014 and DiCarlo et al. 2012. For the user's architectural program, this is the empirical license to abandon supervised classification as the training objective for the encoder hub of the iterative variational encoder–decoder (`threads/the_user_architectural_program.md` §4): a biologically defensible self-supervised pressure can produce equally brain-like representations. The paper is the direct intellectual ancestor of the V-JEPA / DINO line of self-supervised vision-transformer work (`bardes2023_vjepa.md`, `yamamoto2024_human_like_vit_attention.md`) that the user's program treats as the natural training objective for the Recurrent ViT and PRISM v2 encoder. It also supplies the methodological scaffolding — neural prediction scores on V1 / V4 / IT, RSA-style comparisons, BrainScore-aligned metrics — that any successor model in our program will be judged against.

## 3. Key claims

1. Self-supervised *contrastive* embedding methods (local aggregation, instance recognition, SimCLR, MoCo, CMC) match or exceed supervised ImageNet networks as predictors of macaque V4 and IT single-unit responses.
2. The same models reach near-supervised performance on V1 prediction and on linear-readout transfer to object categorization, position, pose, and size estimation.
3. Non-contrastive self-supervised methods (colorization, in-painting, relative-position prediction, depth prediction, autoencoders, RotNet, deep clustering) lag well behind contrastive methods on neural prediction — the contrastive family is the regime that closes the gap.
4. The hierarchical layer-to-area mapping is neuroanatomically consistent: early model layers best predict V1, mid layers best predict V4, late layers best predict IT, just as in supervised networks.
5. Contrastive models trained on the SAYCam developmental video corpus (head-mounted camera footage from a single child) achieve neural predictivity approaching that of ImageNet-trained models, despite SAYCam being noisy, single-subject, and three orders of magnitude smaller than ImageNet.
6. Semisupervised contrastive methods (local label propagation, ~36k labels) bring behavioral *error patterns* into closer agreement with human confusion matrices than purely unsupervised methods do — labels matter for *behavior*, not for *representation geometry*.
7. The paper's overall claim is that the field now has a developmentally plausible computational theory of ventral-stream representation: a contrastive embedding objective, applied to realistic visual experience, produces brain-like ventral-stream representations without any external label supervision.

## 4. Methods

Networks are predominantly ResNet-18 backbones (with robustness checks on alternative architectures in the SI), trained under a battery of unsupervised, self-supervised, and supervised objectives. The contrastive family is the main subject of interest: instance recognition (IR), local aggregation (LA), SimCLR, momentum contrast (MoCo), and contrastive multiview coding (CMC). Non-contrastive baselines include autoencoders, variational autoencoders, sparse coding, colorization, image in-painting, relative position prediction, depth prediction, RotNet, deep clustering, contrastive predictive coding (CPC), and PredNet (which requires a bespoke recurrent architecture). Supervised ImageNet ResNet-18 is the upper-bound reference; an untrained random-weight network is the lower-bound floor.

Neural data are macaque single-unit responses from two published electrophysiology datasets. V1 responses are taken from Cadena et al. (linear 32-channel arrays; ~1,450 ImageNet images plus synthesized textures). V4 and IT responses are from Majaj et al. (chronically implanted Utah arrays; 5,760 images comprising 64 3D objects across 8 categories rendered at variable pose, position, and size against natural backgrounds). For each (model, layer, brain area) tuple, the authors fit a regularized linear regression from model activations to neuronal firing rates on a held-out set and report the noise-corrected Pearson correlation as the *neural predictivity*. The reported score for a model on an area is the maximum across layers — i.e., each model gets its best shot at predicting each area.

Behavioral consistency is measured by computing the 24-category confusion matrix of a linear readout on each model and correlating it with the empirical human confusion matrix on the same image set. The layer-area mapping consistency is measured by extracting the *best-matching layer index* for each area and asking whether the V1 → V4 → IT ordering of best layers respects the model's depth ordering. Linear-readout transfer is reported on object categorization, position localization, size estimation, and pose estimation.

A separate experimental arm trains the same contrastive objectives on the SAYCam developmental video corpus (head-mounted camera footage from one child, ~70k hours-resolved frames). The authors introduce *video instance embedding* (VIE), a frame-level instance-recognition objective extended across time, and report neural predictivity for VIE-on-SAYCam models against the same V1, V4, IT data.

A final arm trains *local label propagation* (LLP), a semisupervised method, with varying numbers of ImageNet labels (3k–36k–full) on top of a contrastive backbone, and reports both neural predictivity and human-behavior consistency.

## 5. Results

On IT (the highest ventral-stream area), the top contrastive models match supervised ImageNet within noise: LA achieves IT predictivity statistically indistinguishable from supervised (reported $p=0.36$), IR is also indistinguishable ($p=0.25$), and SimCLR is indistinguishable ($p=0.49$). On V4, LA reaches near-parity ($p=0.11$) and IR is close ($p=0.12$), while SimCLR is significantly worse than supervised on V4 ($p=0.0001$) despite matching it on IT — the contrastive family is not internally uniform. On V1, all unsupervised methods significantly exceed the untrained baseline, but none significantly match supervised. Non-contrastive self-supervised methods (colorization, depth, in-painting, autoencoders) lag substantially behind the contrastive family across all three areas.

The hierarchical layer-to-area mapping is preserved: for LA, IR, and SimCLR the best-matching layer indices increase monotonically from V1 to V4 to IT, matching the canonical ventral-stream depth ordering and matching the layer-area mapping found in supervised ResNet-18. This is non-trivial: a model could achieve high IT predictivity with shallow layers (which would be neuroanatomically inconsistent) — instead, the contrastive models recapitulate the depth-area correspondence.

Linear-readout transfer shows that the best contrastive models equal or *outperform* supervised models on position and size estimation, and are within a few percentage points on object categorization. This suggests that the representations the contrastive objective learns are richer along non-category axes than supervised classification representations, which are well-known to discard category-irrelevant variance.

The SAYCam result is the most striking. VIE trained only on the SAYCam developmental corpus — a single child's noisy egocentric video — achieves IT predictivity approaching ImageNet-trained models. This is a roughly three-order-of-magnitude reduction in dataset size relative to ImageNet and a complete elimination of label supervision, with only a modest loss of brain-prediction accuracy. The paper argues this dissolves the developmental-plausibility objection to deep-network ventral-stream models.

Local label propagation with 36k labels closes the *behavioral* consistency gap between purely unsupervised contrastive models and supervised ones, producing human-like confusion patterns. The implication is that representation geometry is set by the unsupervised objective, while category-label semantics (which determine *which* errors a network makes) require some label exposure, albeit far less than full supervision.

## 6. Critique / limitations

The neural data are macaque single-unit responses on static images, not human or developmental data. The "developmental plausibility" claim is therefore an *inference* — the architecture is plausible (the input regime can be made plausible via SAYCam), but no developmental dynamics, no critical periods, no infant-behavioral validation are reported. A stronger test would compare model representational geometry at different points of training to infant looking-behavior or pediatric fMRI data.

The contrastive objective uses *backpropagation* and a global contrastive loss requiring negative samples from across the dataset; both ingredients are biologically implausible at the synaptic level (the credit-assignment problem and the impossibility of cross-batch negatives in a real circuit). The authors are explicit that they decouple "optimization target" (which they argue is plausible) from "optimization mechanism" (which is not), but the latter is precisely where any literal biological-plausibility claim collapses. The paper does not test surrogate-gradient or local-rule implementations of contrastive learning.

The architecture is feedforward ResNet-18. The ventral stream is not feedforward: top-down feedback, lateral connections, and recurrence are essential for matching the *temporal* signature of IT responses to challenging images (Kietzmann et al. 2019; `kietzmann2019_recurrence_required.md`). The Zhuang et al. paper inherits all the limitations of feedforward models — they may match the *time-averaged* response well while missing the within-trial dynamics that recurrence is required to explain. PredNet, which is recurrent, is included as a baseline but performs poorly; this is suggestive but not dispositive, because PredNet is a particular recurrent architecture with particular failure modes.

The neural-predictivity benchmark is itself a moving target. The reported V4 and IT scores are at or near the noise ceiling on the Majaj dataset, but newer datasets (THINGS-fMRI, Algonauts, NSD) include more images and more cortical area coverage, and the ranking of models on newer benchmarks does not perfectly track the Majaj-era ranking. The paper's headline claim — "self-supervised matches supervised on IT" — is well-supported on the Majaj data but should be re-examined on later, larger datasets, where SimCLR-style methods have sometimes underperformed and where transformer-based self-supervision (DINO, MAE, V-JEPA) has overtaken ResNet-based contrastive learning. The Yamamoto et al. 2024 result (`yamamoto2024_human_like_vit_attention.md`) on DINO ViTs is the natural successor experiment but uses behavior (gaze) rather than direct neural prediction.

The "best layer per area" methodology gives each model the most favorable layer-area assignment, which inflates absolute predictivity scores. A more conservative analysis would commit to a single layer-area assignment per model architecture and report scores on that assignment for all training objectives. This is reported in supplementary form but the headline numbers use the most-favorable assignment.

The semisupervised behavioral-consistency result is interesting but interpretively delicate. The error patterns of supervised models reflect ImageNet-class biases (e.g., the well-documented dog-breed bias); the fact that 36k labels are sufficient to recover that error structure is more a statement about how much category information is in a small subset of labels than a finding about brain-like behavior per se. Human confusion matrices on the same 24-category task do not necessarily reflect ImageNet category structure either, so the alignment may be partly coincidental.

The contrastive-vs-non-contrastive split is treated as natural, but the paper does not separate the *contrastive loss* from the *augmentation strategy*. Modern non-contrastive self-supervision (BYOL, SimSiam, MAE) post-dates the paper and is known to match contrastive methods without negative samples; their inclusion would change the narrative from "contrastive is special" to "any self-supervised method with strong augmentation invariance is special." V-JEPA (`bardes2023_vjepa.md`) sits in this newer family.

Finally, the paper's title — "Unsupervised neural network *models of the ventral visual stream*" — is, strictly, an overclaim relative to its evidence. The paper shows that unsupervised networks *predict* ventral-stream responses, not that they *model* development. The latter would require longitudinal alignment of model-training dynamics with infant cortical maturation. The result remains the most important single demonstration that label-free training is sufficient for brain-aligned representation, but it is a *sufficiency* result, not a *developmental theory*.

## 7. Connection to our work

This paper is the empirical bridge between the user's program (`threads/the_user_architectural_program.md`) and any defensible claim that the user's models are biologically plausible. The user's notes commit, repeatedly, to two positions that depend on this paper being true: first, that the encoder hub of the iterative variational encoder–decoder (§4 of the thread) is trained with a *self-supervised* objective (the VAE reconstruction + KL regularizer, optionally augmented with V-JEPA-style predictive losses) and *not* with supervised ImageNet classification; second, that the resulting representations should be brain-like in their representational geometry. Zhuang et al. is the prior probability that this is achievable. Without it, the user's architectural program would be open to the objection that brain-like ventral-stream representations require supervised classification — an objection this paper retires.

**Bearing on the encoder objective.** The user's iterative variational encoder–decoder objective (`threads` §4) is a Gaussian-likelihood reconstruction loss plus a KL regularizer on the guide $\tilde H_0$. This is closer in spirit to the *autoencoder* family than to the contrastive family — and Zhuang et al. find autoencoders to be among the *worst* self-supervised methods for neural predictivity. This is a serious challenge to the user's commitment. Two responses are available. First, the iterative-VAE adds the $n_{FR} \to n_{BR}$ recurrent reasoning loop, which the Zhuang autoencoder baselines do not have; the relevant comparison would be against an *iterative-inference* autoencoder, not a vanilla one. Second, the user's program can incorporate a V-JEPA-style predictive loss (`bardes2023_vjepa.md`) into the encoder as an additional pressure, moving the objective from pure reconstruction toward the contrastive / predictive regime that Zhuang et al. identify as the brain-aligning ingredient. The thread §4 wording leaves this open; this paper supplies the empirical reason to lean into V-JEPA-like objectives rather than pure reconstruction.

**Bearing on multi-compartmental memory and hierarchy.** The hierarchical layer-to-area mapping result — early layers predict V1, middle layers predict V4, late layers predict IT — is the empirical anchor for the user's three-layer GridCell RNN hierarchy (`threads` §3). The user's design pairs Layer 1 with V1, Layer 2 with V2/V4, Layer 3 with IT-like abstraction; Zhuang et al. is the demonstration that contrastive self-supervision produces exactly this stratification *automatically*, without any architectural enforcement. This is encouraging: the user's bidirectional, hierarchical memory should *also* recapitulate the V1 → V4 → IT depth ordering if trained with a similar self-supervised pressure, and the layer-to-area mapping analysis from Zhuang et al. is the readout we should perform on the user's models to demonstrate it.

**Bearing on PRISM.** PRISM v1 and v2 train their networks with task-specific objectives (change-detection accuracy, prediction-error minimization) rather than with contrastive self-supervision. The Zhuang et al. result implies a missed opportunity: pretraining the PRISM backbone with a contrastive objective (LA, IR, or a V-JEPA-style predictive variant) on natural video before fine-tuning on change detection would, by the logic of this paper, yield more brain-like representations in PRISM than direct task training does. The corresponding test is whether the brain-prediction scores of a PRISM-style model improve when the backbone is initialized from a contrastive pretraining run, and whether the layer-to-area mapping of PRISM's recurrent layers respects the V1 → V4 → IT depth ordering only after such pretraining.

**Bearing on the iterative variational encoder–decoder.** The iterative-VAE (`threads` §4) commits to a generative-decoder reconstruction objective with KL regularization. Zhuang et al.'s ranking puts autoencoders below contrastive methods on neural predictivity, but the iterative-VAE differs from a static autoencoder in two key ways: (a) it runs $n_{FR}$ forward passes on the same input, producing attractor-like dynamics that are not present in single-pass autoencoders; (b) it adds a KL prior on the guide that imposes representational continuity and disentanglement. Whether these augmentations are sufficient to lift the iterative-VAE into the contrastive-equivalent regime is an empirical question Zhuang et al. cannot answer — but it is a question that *should be answered* by running Zhuang et al.'s neural-predictivity protocol on the iterative-VAE encoder before claiming biological plausibility.

**Bearing on the competition-emergent predictive-coding thesis.** The user's §5 thesis is that predictive coding emerges from inter-coalition competition for limited representational resources. Contrastive learning, in Zhuang et al.'s framing, is a competition: each example competes with negatives for representational mass in the embedding space. The local aggregation method, which wins the paper's brain-predictivity benchmark, explicitly models *neighborhood structure* in the embedding — a form of cooperation among similar examples and competition against dissimilar ones. This is a plausible algorithmic instantiation of the user's "coalition competition" frame, and a natural place to look for a learning rule that bridges the user's theory (coalitions competing for self-attention bandwidth, `threads` §5) and the Zhuang et al. empirical regime (representation embeddings competing for embedding-space mass). The translation between the two pictures — embedding-space mass vs. attention-bandwidth — is a research project in its own right.

**Bearing on V-JEPA, Yamamoto et al., and the broader self-supervision program.** Zhuang et al. (ResNet, contrastive embedding, IT predictivity) and Yamamoto et al. (ViT, DINO self-distillation, human gaze alignment) and Bardes et al. (ViT, V-JEPA predictive embedding, video) are three points on the same curve: self-supervised learning produces brain-aligned visual representations across multiple training regimes (contrastive, self-distillation, predictive-embedding), multiple architectures (ResNet, ViT), and multiple readouts (neural prediction, human gaze, behavioral consistency). The user's program inherits this curve as its empirical justification for choosing self-supervised pretraining over supervised classification for every memory hub.

**Bearing on RSA and representational geometry.** The neural-predictivity metric used in this paper is a noise-corrected Pearson correlation under a regularized linear mapping — a method-cousin of Kriegeskorte's representational similarity analysis (`kriegeskorte2008_rsa.md`). Any application of the user's program to ventral-stream comparison will rest on the RSA / linear-mapping toolkit established by these papers. Zhuang et al. is the most influential application of this toolkit to date for the unsupervised-vs-supervised contrast and supplies the protocol our models should be evaluated under.

**Bearing on hierarchical models of object recognition.** Riesenhuber & Poggio's HMAX (`riesenhuber_poggio1999_hierarchical_models.md`) is the theoretical ancestor of the V1 → V4 → IT computational ladder that Zhuang et al. show contrastive learning recapitulates. The Zhuang et al. result extends HMAX from a hand-designed feedforward hierarchy to a learned one trained without category labels, completing the trajectory: hand-designed → supervised-learned (Yamins 2014; DiCarlo 2012; `dicarlo2012_object_recognition.md`) → self-supervised-learned (Zhuang 2021).

## 8. Citations to follow

- `chen2020_simclr` — the SimCLR contrastive objective; one of the three brain-predictivity-tied methods in the paper. High-priority addition.
- `he2020_moco` — momentum contrast; another contrastive baseline. Candidate.
- `wu2018_instance_discrimination` — instance recognition / IR; one of the best brain-predictive objectives in the paper. Candidate.
- `zhuang2019_local_aggregation` — the LA method that achieves the best neural predictivity. High-priority addition.
- `yamins2014_hierarchical_models_predict` — the supervised-CNN-predicts-IT founding paper; the direct ancestor of this work. High-priority addition.
- `schrimpf2018_brain_score` — the BrainScore benchmark framework; methodological dependency. Candidate.
- `cadena2019_v1_dataset` — the V1 neural data used here. Candidate.
- `majaj2015_simple_learned_features` — the V4/IT neural data used here. High-priority addition.
- `sullivan2021_saycam` — the SAYCam developmental corpus that enables the developmental-plausibility arm. Candidate.
- `grill2020_byol` — BYOL non-contrastive self-supervision, post-dates the paper; the natural follow-up baseline. Candidate.
- `he2022_mae` — MAE masked autoencoder ViT; another post-2021 self-supervision method that should be benchmarked on the same protocol. Already flagged in `yamamoto2024_human_like_vit_attention.md` §8.
- `lotter2017_prednet` — PredNet, the only recurrent baseline in this paper; relevant to the recurrence question. Candidate.
- `oquab2023_dinov2` — DINOv2; the modern ViT self-supervision benchmark. Already flagged in `yamamoto2024_human_like_vit_attention.md` §8.
