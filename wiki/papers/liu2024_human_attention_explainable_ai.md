---
id: liu2024_human_attention_explainable_ai
title: "Human attention guided explainable artificial intelligence for computer vision models"
authors:
  - "Liu, Guoyang"
  - "Zhang, Jindi"
  - "Chan, Antoni B."
  - "Hsiao, Janet H."
year: 2024
venue: "Neural Networks"
doi: "10.1016/j.neunet.2024.106392"
arxiv: ""
url: "https://www.sciencedirect.com/science/article/pii/S0893608024003162"
tags:
  - visual-attention
  - deep-learning
  - methodology
  - vision-transformers
concepts:
  - attentional-spotlight
  - top-down-feedback
  - figure-ground-segmentation
  - self-attention-over-tokens
related:
  - mehrani_tsotsos2023_attention_grouping
  - yamamoto2024_human_like_vit_attention
  - hassanin2024_attention_dl_survey
  - cartella2024_human_attention_modeling
  - itti_koch2001_saliency_review
  - dosovitskiy2020_vit
  - kietzmann2019_recurrence_required
  - desimone_duncan1995_biased_competition
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_119
status: full
depth: full
last_updated: "2026-05-16"
---

# Human attention guided explainable artificial intelligence for computer vision models

## 1. Abstract

The paper examines whether embedding human attention knowledge into saliency-based explainable-AI (XAI) methods for computer vision models could enhance the *plausibility* and *faithfulness* of those explanations.

The authors first develop two novel gradient-based XAI methods for object detection — FullGrad-CAM and FullGrad-CAM++ — that extend existing class-activation-mapping methods (originally designed for image classification) to produce object-specific saliency for detectors. They then propose HAG-XAI (Human-Attention-Guided XAI), a framework that *learns* how to combine multi-layer model gradients/activations into a saliency map by maximizing similarity to a human attention map collected via eye-tracking on the same images. HAG-XAI uses trainable activation functions and smoothing kernels over the channel- and layer-wise contributions and is trained on a per-dataset eye-tracking corpus.

Evaluation on BDD-100K (driving), MS-COCO (general object detection), and ImageNet (classification) shows that HAG-XAI improves plausibility (overlap with human attention) and user trust across both classification and detection regimes, and improves faithfulness (does removing high-saliency regions actually hurt the model?) specifically in the object-detection regime. For classification, the plausibility/trust gain comes at a faithfulness cost; for detection, the three desiderata are simultaneously improved. The authors release code and data at https://github.com/GitVirTer/HAG-XAI.

## 2. Why this matters for us

This paper is the closest published instance, in the database so far, of using human attention *as a training signal* — rather than as an evaluation reference or as an emergent target — for a vision model's spatial explanation. It validates a core premise of the user's program: that the spatial structure of human attention is informative enough about the structure of natural images and the structure of a CNN/ViT's decision boundary that it can be used to *shape* a model's internal saliency map and produce simultaneously more plausible, more trustworthy, and (for detection) more faithful explanations.

The Recurrent ViT paper (2502.10955) reads attention out of self-attention dynamics directly, claims that the resulting maps are human/primate-like on change detection, and uses no gaze supervision. Liu et al. show that *adding* a small human-gaze-supervised post-hoc layer to existing detector backbones produces explanations that align with human attention with measurable benefit. The two papers together stake out a range of options for "where in the pipeline should human attention enter": Yamamoto et al. 2024 (no gaze, self-supervised pretraining); Recurrent ViT (no gaze, RL on task reward); Liu et al. 2024 (explicit gaze supervision on the saliency head). The recurrent ViT's attention map is precisely the kind of artifact this XAI literature is built to study, and Liu et al. supply both an evaluation protocol (CC/NSS/AUC-Judd over BDD-100K/MS-COCO gaze data) and a constructive method (HAG-XAI) that could be used as an external check on the Recurrent ViT's claim.

## 3. Key claims

1. Existing saliency-based XAI methods (Grad-CAM, Grad-CAM++, Score-CAM, RISE, etc.) produce saliency maps that diverge measurably from human attention measured by eye-tracking.
2. The conventional XAI evaluation focuses on faithfulness (does the saliency explain the model?) but underweights plausibility (does the saliency match human-intuitive evidence?) and user trust.
3. FullGrad-CAM and FullGrad-CAM++ extend class-activation-mapping to object detectors by aggregating gradients across all bias terms, producing object-specific rather than image-level saliency.
4. Human attention maps themselves are higher-faithfulness explanations of a detector's output than existing saliency-XAI methods — i.e., a human's gaze on the image is more predictive of where the model is "looking" than the model's own gradient-based saliency.
5. HAG-XAI, a small trainable layer over multi-layer activations/gradients that is optimized for similarity to a human attention map, improves plausibility and user trust across regimes and simultaneously improves faithfulness in the object-detection regime.
6. For image classification, HAG-XAI trades faithfulness for plausibility — the gaze-fitted saliency is less aligned with the *model's* feature attribution even as it is more aligned with human attention.
7. The plausibility-faithfulness trade-off is regime-specific: detection backbones produce internal feature maps whose centroid is already closer to objects than classification backbones, so a gaze-aligned saliency stays consistent with the model's decision structure.

## 4. Methods

**CAM-family background.** Standard CAM-family methods compute a class-conditional spatial saliency $S^c(x,y) = \mathrm{ReLU}\big(\sum_k w_k^c A_k(x,y)\big)$ from final-layer activations $A_k$ and class-specific channel weights $w_k^c$. Grad-CAM derives $w_k^c$ from class-logit gradients $\partial y^c / \partial A_k$ globally averaged over space; Grad-CAM++ uses second-order weighting; Score-CAM forgoes gradients entirely and uses input-masking scores.

**FullGrad and its detection extensions.** FullGrad (Srinivas & Fleuret 2019) sums the gradient contributions of *all* bias terms across the network, producing an input-resolution saliency that includes early-layer contributions that Grad-CAM (a final-layer method) misses. Liu et al. extend FullGrad to detection by computing per-detection rather than per-image-class biases, giving FullGrad-CAM and a higher-order variant FullGrad-CAM++. The key technical move is that an object detector's output is a set of (bounding box, class) pairs, and the relevant "logit" for saliency is the detection-specific score; FullGrad-CAM aggregates bias-gradient contributions specific to each detection.

**HAG-XAI procedure.** The paper's central contribution. Given a backbone, a target output (a class for classification, a detection bounding box for detection), and a corpus of (image, gaze map) pairs collected during eye-tracking on those same images, HAG-XAI:

1. Computes a vector of candidate saliency maps from the model — one per layer, one per channel, or one per CAM-family base method.
2. Passes each candidate through a trainable activation function (a learned nonlinearity that can suppress, amplify, or invert each channel's contribution).
3. Applies a trainable Gaussian smoothing kernel whose bandwidth is learned.
4. Combines the activated, smoothed candidates via a learned weighted sum to produce the final HAG-XAI saliency map.
5. Trains the activation, kernel, and weight parameters by maximizing a similarity metric (CC, KL-divergence, or NSS) between the produced saliency map and the human attention map.

**Train/test split.** The training set is the gaze-image corpus; at test time only the trained activation/kernel/weights are used (the same backbone, no gaze input). The procedure is *post-hoc*: the backbone itself is not modified, only the saliency read-out. This is what makes HAG-XAI cheap to plug onto an existing detector but also what limits its reach.

**Datasets.** BDD-100K is used for driving-scene object detection with collected driver gaze; MS-COCO for general object detection with collected eye-tracking; ImageNet for classification. Each dataset contributes gaze data from a separate participant pool with a separate task (driving, free-viewing object scenes, classification-tagged image inspection), which means the "human attention map" being targeted is not a single coherent construct across the experiments — a methodological point the critique section returns to.

**Baselines.** The authors compare HAG-XAI against Grad-CAM, Grad-CAM++, Score-CAM, RISE, Smooth-Grad, FullGrad, FullGrad-CAM, FullGrad-CAM++, plus the raw human attention map as a baseline saliency method.

**Metrics.** Three families. *Plausibility* — CC (Pearson correlation), NSS (normalized scanpath saliency), AUC-Judd between the saliency map and human gaze. *Faithfulness* — deletion AUC (drop in model confidence as high-saliency regions are progressively masked) and insertion AUC (rise in confidence as high-saliency regions are progressively re-inserted into a blank image). *User trust* — a subjective rating study on a sample of explanations, in which participants score each explanation on a Likert scale.

## 5. Results

**Plausibility on detection.** On detection (BDD-100K, MS-COCO), HAG-XAI exceeds every CAM-family baseline on all three plausibility metrics (CC, NSS, AUC-Judd). The improvement over the strongest gradient baseline (FullGrad-CAM++) is on the order of a 10–20% relative gain on plausibility metrics. The pattern holds across both datasets and across the detector backbones the authors test.

**Faithfulness on detection.** On the deletion-AUC faithfulness metric the same ordering survives: HAG-XAI's gaze-fitted saliency, when used to progressively mask the input, induces a steeper drop in detector confidence than any of the CAM-family baselines, including the FullGrad variants the same authors introduce. The corresponding insertion-AUC results are weaker but still favor HAG-XAI.

**Plausibility vs. faithfulness on classification.** On ImageNet, HAG-XAI again exceeds plausibility baselines but is worse than Grad-CAM on faithfulness. The gaze-aligned saliency is dragged toward image regions that humans look at (faces, central foreground) even when the classifier's discriminative features lie elsewhere (textures, periphery). This is the cleanest empirical exhibit in the paper of a *bona fide* plausibility-faithfulness conflict.

**User-trust study.** A subjective ratings study finds that participants prefer HAG-XAI explanations to baseline CAMs at a higher rate than chance, especially in the detection regime — consistent with the plausibility metrics. The trust gain is robust across the rater pool.

**Human gaze as a baseline XAI.** The most surprising single number is in the "human gaze as XAI" comparison: raw human gaze maps, used as if they were a saliency method, score higher on detection-faithfulness than several CAM-family methods do, including Grad-CAM. This is the result the paper highlights as evidence that *humans look at where the model is computing from* — a precondition for the rest of the HAG-XAI framework to make sense, and a substantive empirical claim in its own right.

**Component ablations.** The authors report ablations of HAG-XAI's components: removing the trainable activation, the smoothing kernel, or the per-channel weighting each degrades plausibility, with the activation function being the largest contributor. This is consistent with the view that HAG-XAI is doing a learned channel re-weighting whose nonlinearity, not the smoothing prior, carries the bulk of the gaze-alignment gain.

**Cross-dataset generalization.** HAG-XAI is trained on each gaze corpus independently (BDD-100K gaze, MS-COCO gaze, ImageNet gaze). The paper does not extensively test whether weights learned on one corpus transfer to another. Given that the underlying gaze regimes differ across datasets, the absence of strong cross-corpus transfer would be unsurprising; its presence would be a stronger result the paper does not claim.

## 6. Critique / limitations

**Gaze supervision is the contribution and the limitation.** HAG-XAI requires per-dataset gaze collection. This is fine for a research paper but is the principal cost of the method: a new detector or a new dataset cannot be explained without first running an eye-tracking study. Compared with the Recurrent ViT (2502.10955) and Yamamoto et al. 2024 — both of which obtain human-aligned attention with *no gaze supervision* — HAG-XAI's regime is more expensive but more controlled. The right question for the user's program is not which approach is better in isolation but which combination produces the most faithful explanation: a self-supervised or RL-trained backbone (no gaze) plus a HAG-XAI-style trainable read-out (gaze) might dominate both.

**The plausibility/faithfulness trade-off in classification is glossed.** The paper reports that HAG-XAI is worse on faithfulness for classification but does not deeply diagnose *why*. The natural explanation — that classification backbones use diffuse / shortcut features that don't lie under human gaze — is consistent with Yamamoto et al.'s observation that supervised-classification ViTs produce diffuse attention. But the diagnosis matters: if classification models' decisions truly do not flow through gaze-aligned regions, then HAG-XAI's classification explanations are misleading even if more plausible. The paper acknowledges this but does not resolve it.

**The framework is post-hoc, not architectural.** HAG-XAI does not change the backbone's internal computations; it only changes how saliency is read out. A more architecturally serious move would be to inject gaze supervision into an *internal* attention layer of a ViT during training, so the model learns to attend to gaze-aligned regions natively (Locatello slot-attention with gaze targets; auxiliary head from Lai et al. 2025-style; Sood et al.'s GazeFollow auxiliary tasks). The paper does not test this, leaving open whether HAG-XAI's improvements survive when the backbone is end-to-end trained against the same human-attention target.

**Gaze maps as "ground truth" is itself contested.** The paper treats human attention maps as a ground-truth target without much discussion of what kind of attention the gaze data represents (free-viewing? task-driven? what task instructions?). For BDD-100K the gaze data is plausibly task-driven driver gaze, which is structured by the driving task; for MS-COCO and ImageNet the gaze regime is less clear. A model that aligns with task-driven gaze is not necessarily a model that aligns with bottom-up attention or with cognitive saliency.

**The XAI evaluation is borrowed from saliency benchmarking.** CC, NSS, and AUC-Judd were developed to evaluate bottom-up saliency models against free-viewing gaze (Bylinskii et al. 2019). Applied to XAI saliency maps, they answer "does this look like a gaze map" rather than "does this explain the model." The faithfulness metrics (deletion / insertion AUC) partially correct for this, but the overall evaluation is dominated by the plausibility metrics. A reader who cares about *model debugging* (faithfulness) should weight the classification result, where HAG-XAI is worse, more heavily than the marketing in the abstract suggests.

**No recurrence, no top-down inner loop.** The detector backbones used (Faster R-CNN, YOLO-family) are feedforward. The paper does not address whether human attention alignment would be different for recurrent backbones, where the *temporal* signature of attention within an inference run becomes available. This is precisely the regime where the Recurrent ViT (2502.10955) and PRISM v2 expect to differ from feedforward baselines, and HAG-XAI does not engage with it.

**Single-snapshot saliency vs sequential gaze.** Like Yamamoto et al. 2024, HAG-XAI compares a per-image saliency map to a per-image gaze density. Saccade dynamics — scanpath sequence, refixation patterns, inhibition of return — are not part of the evaluation. A model that produces the *right* saliency map but the wrong dynamics is rewarded the same as one that produces both correctly.

**Channel/layer aggregation is opaque.** HAG-XAI's learned per-channel activation function is the largest contributor to its gain (per the ablations) but the paper does not characterize what the activations look like or which channels are amplified vs suppressed. A more interpretable HAG-XAI would report which feature channels the gaze fitting selects for; the absence of such an analysis means HAG-XAI's *internal* explanation of why it improves on Grad-CAM is itself opaque.

**Distribution of gaze across the participant pool is not characterized.** The paper treats the per-image gaze map as a unitary target without considering between-participant variability. If different participants attend to different parts of an image (which is generic for natural images), the "average" gaze map is an artifact of pooling rather than a well-defined cognitive object. The Recurrent ViT paper at least operates in a regime (change detection) where the relevant gaze is highly constrained by the task, side-stepping this issue.

## 7. Connection to our work

This is the third pillar of the database's "human-aligned model attention" cluster, alongside `yamamoto2024_human_like_vit_attention` (which gets human-like attention from DINO self-supervision, no gaze) and the Recurrent ViT 2502.10955 (which gets primate-like attention from RL on change detection, no gaze). Liu et al. is the *opposite endpoint*: explicit gaze supervision on a post-hoc saliency layer over an off-the-shelf backbone. Reading the three together gives a near-complete spectrum of how human attention can enter a deep model — no supervision (Yamamoto), task-only supervision (Recurrent ViT), explicit gaze supervision (Liu) — and the empirical headline is that all three positions can produce human-aligned saliency, but with different costs and different residual properties.

**Validation of the user's framing.** The user's architectural program (`threads/the_user_architectural_program.md`) treats human-aligned model attention as scientifically useful in itself — not just as a phenomenology of attention maps but as a substantive constraint on the model's internal computation. Liu et al.'s deletion-AUC results provide direct evidence for this: raw human gaze maps explain detector outputs better than several CAM-family attribution methods. Translated to the user's terms: human gaze captures structure that the model is computing from, even when the model's own gradient-based introspection misses it. This is one of the strongest published statements of the position that human attention is not just a *target* for model attention to mimic but a *probe* into the model's actual computation. The Recurrent ViT's claim that its self-attention map matches primate change-detection attention is, in the same spirit, a claim that the model and primate are using the same computation; HAG-XAI is an external method for checking such a claim.

**Bearing on the Recurrent ViT's evaluation strategy.** The Recurrent ViT (2502.10955) reports primate-attention alignment qualitatively, via attention-map visualizations, but does not report quantitative plausibility metrics (CC, NSS, AUC-Judd) against a gaze corpus on the same task. Liu et al.'s methodology supplies a templated evaluation: collect free-viewing or task-driven gaze data on the change-detection stimuli, compute per-trial attention maps from the Recurrent ViT, and report plausibility metrics — and, with HAG-XAI's machinery, compute the deletion-AUC faithfulness score. This is a concrete experimental extension of the Recurrent ViT paper that the database can recommend.

**Bearing on PRISM v1/v2.** PRISM v1 substitutes a prediction-error map $S_t$ (`THESIS.md` §2.6) for a softmax-attention map. PRISM v2 reintroduces softmax-attention readouts. The Liu et al. evaluation protocol applies to *both*: the prediction-error map can be treated as a saliency map and evaluated with the same plausibility and faithfulness metrics. A particularly clean test for the "prediction-error-as-attention" thesis is whether PRISM v1's $S_t$ map scores higher than DINO's [CLS]-token map and higher than a baseline CAM on the same change-detection stimuli with the same gaze data. HAG-XAI's training procedure can also be applied to PRISM as a stress test: if a small trainable read-out *on top of* the prediction-error map can be fit to align with human attention, that is consistent with the user's view that prediction error is the right substrate for attention; if not, it is evidence against.

**Bearing on the Feedback Transformer (`feedback-transformer` concept, thread §1).** HAG-XAI is a multi-layer aggregation over backbone activations weighted by a learned function. The user's Feedback Transformer is also a multi-source aggregation — over recurrent feedback channels rather than over backbone layers — combined element-wise prior to softmax (thread §1). The two ideas are *architecturally analogous*: a learned weighted combination over multiple internal information streams produces a unified spatial attention/saliency target. HAG-XAI is the *post-hoc* version of this idea (over a fixed backbone, fit to gaze); the Feedback Transformer is the *in-training* version (inside the backbone, fit to task). The user's program predicts that the in-training version should be strictly more powerful because it can shape the internal representations as well as the read-out — and HAG-XAI's classification-regime weakness (it cannot fix a misaligned backbone) is consistent with that prediction.

**Bearing on biased competition (`desimone_duncan1995_biased_competition`).** HAG-XAI's per-channel trainable activation is doing channel-level resource allocation: which feature channels are amplified, which are suppressed, which are inverted, in producing the final saliency map. Biased competition predicts that this kind of weighting should be the natural form of top-down attentional control. The user's competition-emergent predictive-coding thesis (thread §5) further predicts that *the model should learn to weight channels by how well they predict the human attention pattern*. HAG-XAI is, in effect, a one-shot bias setting; an in-training analog would set the bias dynamically per stimulus.

**Connection to the iterative-VAE program.** The user's iterative variational encoder-decoder (thread §4) iterates over the same image, refining an internal "guide" state. One signature of a useful guide is that it concentrates on regions that humans also look at on the same image. The Liu et al. evaluation pipeline is a natural diagnostic for whether successive iterations of the guide produce *better* gaze alignment — a within-trajectory analog of HAG-XAI's static comparison.

**Connection to figure-ground separation.** Both Yamamoto et al. and Liu et al. surface a figure-ground theme: Yamamoto's foreground / whole-object / background head clusters, and Liu's finding that human gaze aligns with detector-relevant object regions. The user's program, via its hierarchical memory stack (thread §3), is set up to produce figure-ground separation as a byproduct of the descending/ascending projections — and Liu et al.'s plausibility metrics are a clean way to test whether that separation, when it emerges, looks like human attention.

**Connection to `mehrani_tsotsos2023_attention_grouping`.** Mehrani & Tsotsos argue that ViT self-attention performs perceptual *grouping* rather than attention. Liu et al.'s result that human attention has higher detector-faithfulness than CAM-family methods is consistent: humans look at *grouped objects* (whole-object attention, in Yamamoto et al.'s language), and detector decisions flow through whole-object features, so gaze tracks the model's computation. The CAM methods, derived from classification gradients, do not group; they highlight whatever pixel-level features the gradient happens to pass through. The user's recurrent attention mechanism, if it is genuinely attentional rather than purely grouping, should also be evaluable on the Liu et al. metrics — and the prediction is that a properly attentional model should align with gaze even better than a grouping-only model.

**Connection to `hassanin2024_attention_dl_survey`.** The Hassanin survey catalogues attention methods by where they sit in the pipeline (input, feature, channel, spatial, etc.). HAG-XAI is a *spatial* attention method that operates as a post-hoc read-out; the Recurrent ViT's attention is a *self-attention* method that operates inside the backbone. Hassanin's taxonomy is the conceptual map on which the Liu / Yamamoto / Recurrent-ViT spectrum can be plotted, and Liu et al.'s empirical evidence that a post-hoc spatial-attention layer can be fit to gaze gives Hassanin's taxonomy a concrete demonstration of why the where-in-the-pipeline distinction matters.

**Connection to `cartella2024_human_attention_modeling`.** Cartella et al. is a recent survey of human attention modelling. Liu et al. populate one of Cartella's most important categories — model interpretation via gaze — with a concrete, evaluated method. Where Cartella et al. catalogue the field, Liu et al. demonstrate a useful instance of it, and the database's reading should treat the two as a survey/exemplar pair: Cartella for the map, Liu for the route. Both are seeded from the Recurrent ViT paper's bibliography (refs 119 and 120), confirming that the 2502.10955 authors were aware of the human-attention-as-XAI-target literature and chose, deliberately, to read attention from internal self-attention dynamics rather than fit it to gaze post-hoc.

**Concrete experimental program.** Combining the above, the database can recommend the following test sequence for an extension of the Recurrent ViT line: (a) collect gaze data on the change-detection task stimuli (or use existing primate-attention data as a proxy); (b) report plausibility metrics (CC, NSS, AUC-Judd) for the Recurrent ViT's self-attention map; (c) train a HAG-XAI read-out on top of the Recurrent ViT's penultimate features as a control; (d) compare the Recurrent ViT's native attention against the HAG-XAI-trained read-out and against DINO and against CAM-family methods. The architectural thesis predicts that the Recurrent ViT's *native* attention should be competitive with or exceed the HAG-XAI-trained read-out — i.e., that a task-trained recurrent backbone produces gaze-aligned attention without gaze supervision. If true, this is a strong statement of the user's program. If false, the user's program needs to absorb gaze supervision as an auxiliary loss.

**Bearing on the broader interpretability literature.** Liu et al. is, more broadly, a piece of evidence that "what the model attends to" and "what humans attend to" should not be treated as orthogonal: they can be aligned by construction, and the alignment improves both intuitive plausibility (for humans inspecting explanations) and computational faithfulness (for models being debugged). The user's program inherits this view at the architectural level: every internal recurrent state is intended to be an interpretable handle on the model's computation, and human-attention alignment is one of the strongest external probes available for whether that interpretability is real.

## 8. Citations to follow

- `selvaraju2017_grad_cam` — Grad-CAM, the foundational CAM-family XAI method that HAG-XAI extends. High priority.
- `srinivas_fleuret2019_fullgrad` — FullGrad, the technique HAG-XAI generalizes to object detection. High priority.
- `bylinskii2019_saliency_metrics` — the CC / NSS / AUC-Judd evaluation framework HAG-XAI uses. Methodological reference.
- `simonyan2014_deep_inside` — Simonyan et al.'s saliency-via-gradient paper, the origin of gradient-based attribution. Candidate.
- `petsiuk2018_rise` — RISE perturbation-based saliency, a baseline. Candidate.
- `bdd100k_yu2020` — Yu et al.'s BDD-100K driving dataset with gaze annotations. Useful for any change-detection-with-gaze evaluation we might run.
- `kummerer2018_deepgaze` — DeepGaze supervised gaze prediction, the kind of model HAG-XAI improves on. Already a candidate in Yamamoto's citation list.
- `lai2025_gaze_supervised_attention` — a representative of "gaze supervision injected into a model's internal attention layer," the natural extension of HAG-XAI's post-hoc approach. Candidate.
- `hsiao2019_eye_tracking_xai` — Hsiao et al.'s earlier eye-tracking-for-XAI work; Hsiao is a coauthor here and her earlier work motivates the human-gaze-as-ground-truth framing. Candidate.
- `bach2015_lrp` — Layer-wise Relevance Propagation, an alternative attribution method not centered on gradients. Candidate.
- `chattopadhyay2018_grad_cam_pp` — Grad-CAM++, the higher-order variant HAG-XAI uses as a baseline. Candidate.
- `wang2020_score_cam` — Score-CAM, the gradient-free CAM-family method HAG-XAI competes with. Candidate.
- `smilkov2017_smoothgrad` — SmoothGrad, the noise-averaging saliency baseline HAG-XAI evaluates against. Candidate.
- `linsley2019_human_gaze_models` — Linsley et al. on incorporating human attention into deep models; an earlier line of work in the same family. Candidate.
- `mit_saliency_benchmark` — the MIT saliency benchmark and its successor MIT/Tübingen Saliency Benchmark; methodological reference for plausibility metrics in saliency evaluation. Candidate.
