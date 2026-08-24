---
id: khan2022_transformers_vision_survey
title: "Transformers in vision: a survey"
authors:
  - "Khan, Salman"
  - "Naseer, Muzammal"
  - "Hayat, Munawar"
  - "Zamir, Syed Waqas"
  - "Khan, Fahad Shahbaz"
  - "Shah, Mubarak"
year: 2022
venue: "ACM CSUR"
doi: "10.1145/3505244"
arxiv: "2101.01169"
url: "https://arxiv.org/abs/2101.01169"
tags:
  - transformers
  - vision-transformers
  - self-attention
  - deep-learning
  - review
concepts:
  - self-attention-over-tokens
  - multi-head-attention
  - scaled-dot-product-attention
  - positional-encoding
  - cross-attention
related:
  - vaswani2017_attention
  - dosovitskiy2020_vit
  - hassanin2024_attention_dl_survey
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_25
status: full
depth: full
last_updated: "2026-05-14"
---

# Transformers in vision: a survey

## 1. Abstract

Astounding results from Transformer models on natural language tasks have intrigued the vision community to study their application to computer vision problems. Among their salient benefits, Transformers enable modeling long dependencies between input sequence elements and support parallel processing of sequence as compared to recurrent networks (e.g., LSTMs). Different from convolutional networks, Transformers require minimal inductive biases for their design and are naturally suited as set-functions. Furthermore, the straightforward design of Transformers allows processing multiple modalities (e.g., images, videos, text, speech) using similar processing blocks and demonstrates excellent scalability to very large capacity networks and huge datasets. The survey provides a comprehensive overview of Transformer models in computer vision: an introduction to fundamental concepts (self-attention, large-scale pre-training, bidirectional feature encoding), then extensive applications across recognition tasks (image classification, object detection, action recognition, segmentation), generative modeling, multi-modal tasks (VQA, visual reasoning, visual grounding), video processing (activity recognition, forecasting), low-level vision (super-resolution, enhancement, colorization), and 3D analysis (point cloud classification and segmentation). The authors compare advantages and limitations of popular techniques in terms of architectural design and experimental value, and close with an analysis of open research directions and future work.

## 2. Why this matters for us

This is the field-level reference frame for Jonathan's Recurrent ViT (2502.10955). The Recurrent ViT inherits the Vaswani/Dosovitskiy attention substrate that the survey catalogues — scaled dot-product self-attention, multi-head attention, patch tokenization, positional encoding, and the encoder block. The survey makes explicit that the design space of vision transformers is enormous (single-head vs. multi-head, uniform vs. multi-scale, pure vs. hybrid, supervised vs. self-supervised) and that almost all of this space treats the encoder as a stateless function of one image. The Recurrent ViT and the user's broader architectural program (Feedback Transformer, GridCell RNN, multi-compartmental memory) are bets that a recurrence-extended branch of the same design tree is underexplored and load-bearing for change-detection, video, and cued-attention tasks. The survey thus supplies (a) the design vocabulary the manuscript already uses, (b) the field-level "what has been tried" baseline against which recurrent variants must be positioned, and (c) the explicit open-problem list (data hunger, compute, interpretability) that the program inherits.

## 3. Key claims

1. Self-attention is the core primitive: each position's output is a softmax-weighted sum over value projections of all positions, computed as $\mathbf{Z} = \mathrm{softmax}(\mathbf{Q}\mathbf{K}^\top / \sqrt{d_q})\mathbf{V}$ with learned projection matrices $\mathbf{W}^Q, \mathbf{W}^K, \mathbf{W}^V$ per head.
2. Multi-head attention encapsulates multiple parallel attention sub-blocks ($h=8$ in the original Transformer), concatenates their outputs, and projects via $\mathbf{W} \in \mathbb{R}^{h\,d_v \times d}$; this is strictly more expressive than convolution and can model convolution as a special case (Cordonnier et al. 2019).
3. Transformers carry minimal inductive bias compared to CNNs and RNNs (no locality, no translation equivariance, permutation invariance by default), making them naturally set-functions and requiring positional encodings to inject order; this is both the source of their generality and their data hunger.
4. Pre-training on large unlabelled or weakly labelled corpora (supervised or self-supervised) is essential to unlock Transformer performance: ViT-L drops ~13% top-1 on ImageNet when trained on ImageNet-1K alone vs. pre-trained on JFT-300M.
5. The vision-transformer design space partitions into single-head self-attention (non-local blocks, criss-cross, stand-alone, attention-augmented CNNs) and multi-head ViTs (uniform-scale: ViT, DeiT, T2T-ViT, TNT, CaiT, Cross-Covariance; multi-scale: PVT, SegFormer, Swin, CrossFormer, Focal; hybrid CNN-ViT: CvT, CCT, LeViT, ResT, NesT; self-supervised: DINO, MoCo v3, EsViT). Multi-scale and hybrid designs reintroduce convolutional inductive biases for data efficiency.
6. Transformers achieve state-of-the-art on essentially every vision task surveyed: image classification (ViT 88.55 top-1 on ImageNet after JFT pre-training), object detection (DETR 44.9 AP on COCO, D-DETR 43.8 AP with much faster convergence), semantic segmentation (SETR, Segmenter, Segformer, MaX-DeepLab for panoptic), low-level vision (IPT for super-resolution, denoising, deraining), generation (TransGAN, image GPT, ViT-VQGAN), video (TimeSformer, ViViT, Video Transformer Network), multi-modal (ViLBERT, CLIP, Oscar, UNITER), 3D (Point Transformer, Mesh Transformer), and few-shot learning (CrossTransformers).
7. Open challenges are: high computational cost ($\mathcal{O}(n^2)$ in tokens), large data requirements, the gap between language-tailored and vision-tailored designs, limited NAS coverage for ViTs, limited interpretability tools, hardware-efficient deployment for edge devices, and unified-modality designs (Perceiver, Perceiver IO as early attempts).
8. Pre-training–transfer is the dominant training recipe across vision tasks: a Transformer pre-trained (supervised on ImageNet-21K / JFT-300M, or self-supervised via DINO, MoCo v3, BEiT, MAE) is fine-tuned to the target task, with the encoder unchanged and only the head re-initialized.
9. Self-supervised pre-training pretexts fall into three families — generative (in-painting, colorization, masked image modeling), context-based (jigsaw, rotation, temporal-order), cross-modal (CLIP-style image-text, audio-video) — and SSL is the principal mechanism by which the Transformer's data hunger is mitigated without requiring labels at scale.

## 4. Methods

The survey is structured in five layers. **§2 Foundations.** Reviews the Vaswani 2017 transformer end-to-end: scaled dot-product attention, the masked variant $\mathrm{softmax}(\mathbf{Q}\mathbf{K}^\top/\sqrt{d_q} \circ \mathbf{M})$ for causal decoding, multi-head attention with $d_q = d_k = d_v = 64$ and $h=8$, the encoder–decoder block stack ($N=6$ each), positional encodings (sinusoidal or learned), residual + LayerNorm after each sub-block, and the feed-forward MLP. The contrast with convolutions is drawn: self-attention's filters are dynamically computed from the input, are permutation-invariant by default, and operate on irregular sets — which makes them theoretically more general than convolution but practically more data-hungry. The (self)supervised pre-training section catalogues generative pretexts (image colorization, in-painting, masked image modeling), context-based pretexts (jigsaw, rotation, temporal-order verification), and cross-modal pretexts (CLIP-style image-text contrastive learning, audio-video).

**§3 Self-attention & Transformers in vision.** The taxonomy splits into §3.1 single-head self-attention (non-local nets, criss-cross attention, stand-alone self-attention, attention-augmented CNNs, vector attention) and §3.2 multi-head ViTs. The latter subdivides into uniform-scale ViTs (ViT, DeiT, T2T-ViT, TNT, Cross-Covariance Image Transformer), multi-scale ViTs (PVT/PVTv2, SegFormer, Swin, CrossFormer, Focal Transformer), hybrid ViTs with convolutions (CCT, CvT, LeViT, ResT, NesT), and self-supervised ViTs (DINO, MoCo v3, EsViT). Each problem setting — image recognition, object detection, segmentation, generation, low-level, multi-modal, video, low-shot, clustering, 3D — receives its own subsection covering representative architectures, training recipe, and benchmark results.

For the recognition core, ViT (Dosovitskiy 2020) flattens a $224\times 224$ image into $14\times 14$ non-overlapping patches of size $16\times 16$, linearly projects each to a token embedding, prepends a learnable class token, adds 1D learned positional embeddings, and feeds the sequence through $N$ standard Transformer encoder blocks. DeiT (Touvron 2021) adds a distillation token attended to alongside the class token, with the distillation target being a CNN teacher's prediction. T2T-ViT recursively soft-splits and reaggregates tokens to inject local structure. Swin (Liu 2021) computes attention inside non-overlapping windows and shifts the window partition between layers, restoring locality and yielding linear cost in image size. PVT and SegFormer interleave spatial-reduction attention layers with token-merging to produce a feature pyramid suitable for dense prediction. For detection, DETR (Carion 2020) pairs a CNN backbone with a Transformer encoder–decoder where learned "object queries" cross-attend to encoded image features, producing a fixed-size set of $(class, box)$ predictions matched to ground truth via the Hungarian algorithm. For video, TimeSformer and ViViT factorize space-time attention along spatial and temporal axes. For multi-modal work, CLIP trains image and text encoders to maximize cosine similarity of matched pairs; Oscar, ViLBERT, and UNITER co-encode image-region tokens with text tokens via cross-attention.

**§4 Open problems and future directions.** Seven open problems are laid out: §4.1 high computational cost ($\mathcal{O}(n^2)$ in sequence length, prohibitive for high-resolution images) and the surveyed mitigations (pooling/downsampling, local windows, axial attention, low-rank projection, kernelizable attention, similarity clustering); §4.2 large data requirements and the mitigations (distillation in DeiT, T2T's local-structure modeling, CCT and NesT for small datasets, SAM-based smoothing); §4.3 vision-tailored designs (vector attention, jigsaw token rearrangement, token distillation from CNN teachers); §4.4 neural architecture search for ViTs (AutoFormer, BossNAS); §4.5 interpretability (attention rollout/flow, relevancy-score propagation of Chefer et al.); §4.6 hardware-efficient designs (HAT, FPGA acceleration); §4.7 unifying all modalities (Perceiver, Perceiver IO).

The survey is empirical/taxonomic rather than mathematical — its contribution is the structured map, two summary tables (Table 1: design choices per task; Table 2: advantages/limitations per method), and an ImageNet comparison table (Table 3) covering ~40 transformer and CNN models.

## 5. Results

The survey collates benchmark numbers across tasks. Image classification on ImageNet: ViT-L 88.55 top-1 (with JFT pre-training), DeiT-B 83.10 (ImageNet-only), Swin-T 84.5, T2T-ViT-14 81.5, PVTv2-B5 83.8, CaiT-S-36 82.7, Lv-ViT-M 84.1, CrossViT-15 81.5, NesT-B 83.8. Object detection on COCO: DETR 44.9 AP, Deformable DETR 43.8 AP with 10$\times$ faster convergence. Image colorization: ColTran 19.71 FID on ImageNet. Action recognition on NTU 60/120 with ST-TR: 94.0/84.7 top-1. Super-resolution with TTSR: PSNR 27.1 / SSIM 0.8 on CUFED5, 30.0 / 0.81 on Sun80, 25.9 / 0.78 on Urban100, 30.1 / 0.91 on Manga109. Multi-modal: Oscar 80.37 / 57.5 on VQA / retrieval-COCO; ViLBERT 70.6 / 58.2; UNITER 72.47 / 83.72. 3D: Point Transformer 92.8 IoU on ModelNet40, METRO 77.1 MPJPE on 3DPW.

The survey's ImageNet comparison table (Table 3) — restricted to models trained from scratch on $224\times 224$ inputs — gives a parameter-controlled comparison. At the small end ($\sim$5–14M params), T2T-ViT-7 hits 71.7%, CrossViT-T 73.4%, PVTv1-T 75.1%, RegionViT-T 80.4%; the strongest CNN at this scale (EfficientNet-B3) sits at 78.8%, comparable to the best ViTs. At the mid scale ($\sim$20–30M params), Swin-T reaches 81.3%, PVTv2-B2 82.1%, LV-ViT-S 83.3%, vs. ResNet50 76.1% and RegNetY-4G 80.0% — here the ViT advantage is unambiguous. At the large end ($\sim$80–100M params), Swin-B 83.3%, PVTv2-B5 83.8%, NesT-B 83.8%, Lv-ViT-M 84.1%, vs. ResNeXt101-64x4d 79.6% and RegNetY-16G 80.4% — a 3–4 point gap in favor of ViTs.

Two qualitative results matter for our program. First, *every* vision task surveyed has at least one Transformer-based SOTA — meaning the architecture class is general-purpose, not niche. Second, the scaling behavior is unambiguous: more parameters and more pre-training data move performance monotonically (cf. ViT-L 88.55 with JFT vs. its 13-point drop without). The bitter-lesson trend favors generic Transformers + scale.

## 6. Critique / limitations

The survey is a 2021 snapshot frozen for ACM CSUR publication in 2022. It largely predates: (a) ConvNeXt-style "modernized CNNs" that closed much of the ViT–CNN gap on ImageNet without attention, blunting the architectural-superiority claim; (b) the consolidation around hybrid multi-scale designs (Swin v2, MViTv2, MaxViT), making the "pure ViT" debate partly moot; (c) the masked-image-modeling pre-training wave (MAE, BEiT, SimMIM, iBOT) that substantially closed the data-hunger gap; (d) JEPA-style joint-embedding predictive architectures (I-JEPA, V-JEPA) that replace pixel reconstruction with latent prediction; (e) the Mamba/SSM challenge to attention's $\mathcal{O}(n^2)$ cost; (f) modern video transformers beyond the TimeSformer/ViViT generation.

The survey is also taxonomic rather than analytical. It does not test architectural choices in a controlled fashion, does not adjudicate between hybrid and pure ViTs, and does not assess inductive-bias claims empirically — it reports what each paper reports. The discussion of biological attention is essentially absent: there is no engagement with predictive-coding accounts, biased-competition, top-down feedback, or recurrence — i.e., precisely the design axes the user's program operates on. The survey treats the encoder as a feedforward stack and never raises the question of recurrent state, memory, or feedback as a design dimension. For Jonathan's program this is the critical lacuna: the "what has been tried" baseline that the survey establishes is exactly the space where recurrence and bidirectional feedback are absent.

Finally, the multi-head expressiveness claim (Cordonnier et al. 2019) is asymptotic — multi-head SA can express any convolution given sufficient heads and parameters — but in finite-budget practice, hybrid designs that hard-wire convolutional inductive biases consistently beat pure ViTs on small datasets. The survey acknowledges this but does not draw the architectural conclusion: *some* inductive bias is necessary, and the question is which biases.

A subtler limitation is the survey's treatment of attention as a fixed-graph operation. Every method catalogued computes attention afresh on the current input; none maintain attention state across time, none modulate attention scores by an external (e.g., memory, RL, top-down) signal at the Q/K/V level, and none implement softmax-attention as a *function of* prior internal state. This treats the encoder as Markovian in the input — a strong assumption that the Recurrent ViT manuscript and the user's program both reject. The survey's silence on this dimension is therefore informative: as of 2022 the field had not seriously considered stateful or feedback-modulated attention as a design axis. That is the gap the manuscript's §6.7 (tokens / additive / multiplicative feedback variants) is positioned in.

## 7. Connection to our work

This survey is the field-level scaffold against which Jonathan's manuscript and program must be positioned. The connections are specific.

**The Recurrent ViT (2502.10955) backbone.** The published paper's backbone is the standard ViT block of Dosovitskiy 2020 — which the survey catalogs in §3.2.1 as the canonical "uniform-scale ViT." The published paper's §6.7 distinguishes three feedback variants (tokens, additive, multiplicative) for integrating recurrent memory $H^{(t-1)}$ into the encoder. None of these variants appears in the survey's taxonomy. The survey's §3.2 enumerates *what is varied* about ViT (patch size, hierarchy, locality, convolution hybridization, self-supervision) and recurrence over a temporal stream is conspicuously not on that list. This is the gap the manuscript fills.

Concretely, the survey's video subsection (§3.8) reviews TimeSformer, ViViT, Video Transformer Network, and skeleton-based ST-TR — all of which process a fixed clip in one shot, factorize space-time attention, and produce a single prediction per clip. None of these architectures maintains explicit recurrent state across clips or even across frames in the same clip; they treat the temporal dimension as another axis of attention. The Recurrent ViT, by contrast, processes a temporal stream one frame at a time with persistent state $H^{(t-1)}$ — a design choice that is orthogonal to (and could compose with) any of the surveyed video transformers.

**The Feedback Transformer primitive.** The user's Feedback Transformer (`the_user_architectural_program.md` §1) augments the Q/K/V projections with per-state contributions from arbitrary recurrent sources, combined via Hadamard product before softmax. The closest entries in the survey's taxonomy are vector attention (Zhao et al. 2020, learning channel-wise attention) and cross-attention (used in DETR's decoder for object queries, in Perceiver for input-to-latent distillation, in CLIP for text-image fusion). The survey's §4.1 mentions "vector attention from [82] is a nice work in this direction which attempts to specifically tailor self-attention operation for visual inputs via learning channel-wise attentions" — this is the closest published cousin to the Feedback Transformer's multiplicative integration scheme, and it is exactly *one* paper out of ~275 referenced. The opportunity is large.

**Inductive bias and data hunger.** Survey §4.2 makes the data-hunger argument crisply: ViT-L drops 13 points without JFT pre-training. Hybrid designs (CCT, NesT, T2T) and CNN teachers (DeiT) are the standard fixes. The Recurrent ViT's training on relatively modest change-detection datasets is consistent with this concern — the multiplicative-feedback variant in the manuscript should be read partly as an architectural inductive bias that imports temporal continuity as a prior, analogous to how Swin imports locality. The survey's framing supports this reading.

**Open problems alignment.** Of the survey's seven open problems, three bear directly on the program: §4.1 computational cost (the Feedback Transformer multiplies the per-attention cost by the number of feedback sources, so any large-scale instantiation needs efficient attention variants from §4.1); §4.5 interpretability (the user's qualitative attention-map analysis in the Classifier note is exactly the kind of probe Chefer et al. attempt to formalize); §4.7 multi-modal unification (the multi-hub multi-objective system is a strict generalization of the Perceiver-style modality-agnostic substrate that the survey closes on).

**What the survey does not constrain.** The survey is silent on recurrence-over-time, multi-compartmental memory, bidirectional descending/ascending feedback, and predictive-coding interpretations of attention. The PRISM program (separately filed) is consequently *unrelated* to this paper at the architectural level — PRISM rejects softmax attention entirely. The Recurrent ViT and the broader user program *are* directly the natural recurrent extension of the survey's design tree.

## 8. Citations to follow

- `vaswani2017_attention` — already in seed; the foundational architecture the survey starts from.
- `dosovitskiy2020_vit` — already in seed; the paper that anchors §3.2.1 and is the direct backbone of the Recurrent ViT.
- `hassanin2024_attention_dl_survey` — already in seed; complementary attention-mechanisms survey with broader temporal scope.
- `touvron2021_deit` — Data-efficient image Transformers with attention-based distillation; survey §3.2.1; the canonical "small-data ViT" baseline.
- `liu2021_swin` — Swin Transformer; survey §3.2.2; multi-scale hierarchical ViT that has become the default vision backbone post-survey.
- `carion2020_detr` — DETR; survey §3.3; the cross-attention/object-query design that anticipates the Feedback Transformer's Q/K/V augmentation.
- `wang2018_non_local_networks` — Non-local neural networks; survey §3.1.1; the single-head self-attention progenitor used widely in video.
- `jaegle2021_perceiver` — Perceiver; survey §4.7; modality-agnostic latent-bottleneck attention relevant to the multi-hub multi-objective system.
- `zhao2020_point_transformer` — Point Transformer with vector attention; survey §3.11/§4.1/§4.3; the published cousin of the Feedback Transformer's multiplicative-integration scheme.
- `cordonnier2020_self_attention_convolution` — proves multi-head SA can express convolution as a special case; survey §2.1; relevant to the inductive-bias question.
- `chefer2021_transformer_interpretability` — relevancy-score propagation through attention; survey §4.5; the interpretability tool to consider for the manuscript's attention-map analysis.
- `bertasius2021_timesformer` — TimeSformer; survey §3.8; video transformer baseline against which a recurrent variant must be positioned.
- `arnab2021_vivit` — ViViT; survey §3.8; the other canonical video ViT.
- `caron2021_dino` — DINO self-supervised ViTs; survey §3.2.4; emergent attention properties without labels — relevant evidence for the "attention dynamics evolve nontrivially" claim in the Classifier note.
- `naseer2021_intriguing_vit_properties` — robustness and occlusion experiments on ViTs; survey §4.5; quantifies how much occlusion ViTs tolerate.
- `radford2021_clip` — CLIP image-text contrastive pre-training; survey §3.7; the dominant cross-modal self-supervision recipe of the era.
- `he2022_mae` — Masked Autoencoders (post-survey but directly relevant); the SSL pretext that closed much of the data-hunger gap §4.2 identified.
- `liu2022_convnext` — ConvNeXt (post-survey); the "modernized CNN" that re-opens the ViT-vs-CNN debate and is the relevant baseline for any architecture claim.
- `jaegle2022_perceiver_io` — Perceiver IO; survey §4.7; the unified-modality design relevant to the multi-hub multi-objective system.
- `tan2019_efficientnet` — EfficientNet; survey Table 3 baseline; the strongest CNN reference for parameter-controlled ImageNet comparisons.
