---
id: hassanin2024_attention_dl_survey
title: "Visual Attention Methods in Deep Learning: An In-Depth Survey"
authors:
  - "Hassanin, Mohammed"
  - "Anwar, Saeed"
  - "Radwan, Ibrahim"
  - "Khan, Fahad Shahbaz"
  - "Mian, Ajmal"
year: 2024
venue: "Information Fusion"
doi: "10.48550/arXiv.2204.07756"
arxiv: "2204.07756"
url: "https://arxiv.org/abs/2204.07756"
tags:
  - visual-attention
  - deep-learning
  - review
  - transformers
concepts:
  - scaled-dot-product-attention
  - multi-head-attention
  - self-attention-over-tokens
  - cross-attention
  - slot-attention
  - multiplicative-feedback
  - additive-feedback
  - divisive-normalization
related:
  - khan2022_transformers_vision_survey
  - vaswani2017_attention
  - dosovitskiy2020_vit
  - mehrani_tsotsos2023_attention_grouping
  - bardes2023_vjepa
  - hu_dan2021_ic_sc_attention
  - locatello2020_slot_attention
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_96
status: full
depth: full
last_updated: "2026-05-16"
---

# Visual Attention Methods in Deep Learning: An In-Depth Survey

## 1. Abstract

Inspired by the human cognitive system, attention is treated as a mechanism that imitates cognitive awareness of specific information, amplifying critical details while suppressing the rest. Deep learning has exploited this for performance gains across data modalities, and a single attention design often transfers across modalities and integrates easily into large networks. The literature lacks a comprehensive survey of attention techniques to guide researchers in employing attention in their own models; the authors emphasise that transformers cover only a single category in self-attention out of many available. The survey fills this gap and provides an in-depth review of ~50 attention techniques (the introduction claims 70 articles surveyed in total), categorising them by their most prominent features. After introducing the fundamental concepts behind the success of attention, the paper presents the strengths and limitations of each attention category, describes their building blocks and basic formulations, and surveys applications specifically for computer vision. The paper concludes with open questions and recommended future research directions.

## 2. Why this matters for us

This is the broadest taxonomy of attention mechanisms in computer-vision deep learning available, and it is the entry that situates the Recurrent ViT's contribution within the wider non-NLP attention literature. The published Recurrent ViT (2502.10955) and PRISM v1/v2 sit inside the survey's `self-attention` and `arithmetic / multiplicative feedback` categories — but the user's Feedback Transformer is a *multi-source recurrent extension* that the survey does not catalogue. The survey thus simultaneously (a) supplies the canonical reference list for how the field organises attention (channel, spatial, self, arithmetic, multi-modal, logical, category-based, plus stochastic / Gaussian / clustering variants), and (b) identifies a gap — multi-source recurrent feedback into self-attention — into which the user's architectural program inserts itself.

## 3. Key claims

1. Attention methods in vision can be hierarchically organised into **soft (deterministic)** and **hard (stochastic)** branches; soft attention further splits into channel, spatial, self, arithmetic, multi-modal, logical, and category-based; hard attention splits into statistical (reinforcement-learned, Bayesian, variational), Gaussian, and clustering (Fig. 2 of the paper).
2. Transformers (Vaswani et al. 2017; ViT) occupy *one* sub-cell of this taxonomy — self-attention — and the field's identification of "attention = transformer" undersells the diversity of attention designs that have been productive in vision.
3. Channel attention (SE-Net, ECA, CBAM channel branch, A²-Net, Dual, SOCA, Frequency Channel) generates per-channel gating weights via global pooling + small MLP + sigmoid; it is cheap to add and broadly improves classification.
4. Spatial attention (CBAM spatial, SPAN, Spatial-Spectral, RANet, Pyramid Feature, Region) reweights spatial positions and is preferred for detection, segmentation, and saliency.
5. Self-attention encodes higher-order interactions among tokens via Q/K/V projections; many variants exist (Transformer, ViT, Swin, Deformable-Attention Transformer, Standalone, Clustered, Slot, Efficient, Random-Feature, Non-Local, NLSA, X-Linear, Axial). The recurring engineering pressure is to reduce the O(n²) cost of dense attention to linear via factorisation, sparsity, clustering, or kernel approximation.
6. Arithmetic-attention methods (dropout, mirror, reverse, inverse, reciprocal) treat attention as an algebraic operator and have application niches in weakly-supervised detection and salient-object segmentation.
7. Multi-modal attention (Co-Attention, Stacked Cross, Cross, Perceiver, Boosted) explicitly attends across two or more input streams; multi-head attention is the dominant primitive.
8. Hard attention (REINFORCE-trained, self-critical, Bayesian, variational, EM-clustering, uncertainty-aware) sidesteps the differentiability constraint at the cost of higher variance training; it tends to give sharper, more interpretable attention masks but requires policy-gradient or variational training tricks.
9. The major open challenges are: generalisation across vision tasks (esp. low-level), efficiency (transformers are 30× the FLOPs of efficient CNNs for similar accuracy), multi-modal fusion, data hunger, lack of head-to-head benchmarks across attention variants, and the visualisation/interpretability of stacked attention modules.
10. The recommended future direction is hybrid multi-head architectures that combine multiple attention categories within one model, with explicit attention to efficiency and interpretability.

## 4. Methods

This is a survey, not an experimental paper; the "method" is the taxonomy and the gloss given to each surveyed technique. The organising principle (Fig. 2 of the paper) is the function used to generate attention scores (softmax / sigmoid for soft; stochastic sampling / clustering / EM for hard) and the **dimension along which scores are computed** (channels, spatial positions, token-to-token similarity, cross-modal pairs). For each surveyed technique the authors describe:

- The architectural diagram (Figs. 3–7 of the paper cover channel, spatial, self, arithmetic, multi-modal, logical, and hard variants).
- The mathematical form. E.g., the SE block: $f_s = \sigma(\mathrm{FC}(\mathrm{ReLU}(\mathrm{FC}(f_g))))$ with $f_g$ the global-average-pooled features. CBAM's channel branch sums two MLP-pooled descriptors: $f_{ch} = \sigma(\mathrm{MLP}(\mathrm{MaxPool}(f)) + \mathrm{MLP}(\mathrm{AvgPool}(f)))$. CBAM's spatial branch concatenates pooled channels and convolves: $f_{sp} = \sigma(\mathrm{Conv}_{7\times 7}([\mathrm{MaxPool}(f); \mathrm{AvgPool}(f)]))$. The scaled-dot-product transformer attention is $\mathrm{softmax}(QK^\top/\sqrt{d_k})V$ (Algorithm 1 of the paper).
- The primary application(s) (image classification, person re-ID, semantic segmentation, object detection, image captioning, VQA, image generation, 3D analysis, etc.).
- The strengths and limitations, summarised in their Table 1.

The paper does **not** run a fair-comparison benchmark across the surveyed methods; the absence of head-to-head numbers is itself flagged as one of the open problems.

## 5. Results

There are no original empirical numbers in this paper; "results" are the taxonomic synthesis. The survey covers ~50 explicit techniques (Table 1) and references 70+ articles in total. The taxonomy as enumerated in Figure 2 of the paper is:

- **Soft / Channel:** Squeeze-Excitation (SE-Net, Hu 2018), Efficient Channel Attention (ECA, Wang 2020), Split-Attention (ResNeSt, Zhang 2020), Second-Order (SOCA, Dai 2019), High-Order (HA, Ding 2020), Harmonious (Li 2018), Auto-Learning (HOGA, Ma 2020), Double (A²-Net, Chen 2018), Dual (Fu 2019), CBAM channel branch (Woo 2018), Frequency Channel (Qin 2021).
- **Soft / Spatial:** CBAM spatial (Woo 2018), Co-Attention/Co-Excitation (Hsieh 2019), Spatial Pyramid (SPAN, Hu 2020), Spatial-Spectral (Meng 2020), Pixel-wise Contextual, Pyramid Feature (Zhao 2018), Attention Pyramid, Region (RANet, Sun 2021).
- **Soft / Self:** Transformer (Vaswani 2017), ViT (Dosovitskiy 2020), Swin (Liu 2021), Deformable-Attention Transformer (Xia 2022), Standalone Self-Attention (Ramachandran 2019), Clustered Attention (Vyas 2020), Slot Attention (Locatello 2020), Efficient Attention (Shen 2021), Random Feature Attention (Peng 2021), Non-Local (Wang 2018), Non-Local Sparse (NLSA, Mei 2021), X-Linear (Pan 2020), Axial Attention (Wang 2020), and other Efficient Mechanisms.
- **Soft / Arithmetic:** Attention Dropout, Mirror Attention, Reverse Attention, Inverse Attention, Reciprocal Attention.
- **Soft / Multi-Modal:** Cross-Attention, Criss-Cross, Perceiver (Jaegle 2021), Stacked Cross, Boosted (Chen 2018).
- **Soft / Logical:** Sequential, Permutation-Invariant.
- **Soft / Category-Based:** GAIN-style class-supervised attention.
- **Hard / Statistical:** Bayesian Attention (Fan 2020), Repulsive (An 2020), Variational, Self-Critical (Chen 2019).
- **Hard / Gaussian:** Self-Supervised Gaussian, Uncertainty-Aware (Heo 2018).
- **Hard / Clustering:** EM-Attention (Li 2019), GatCluster (Niu 2020).

The headline quantitative point (cited in §4.2 Efficiency of the paper) is the cost gap: the base ViT requires ~18 billion FLOPs to process an image versus ~600 million FLOPs for efficient CNNs at comparable accuracy — a 30× efficiency gap.

## 6. Critique / limitations

**The taxonomy is descriptive, not generative.** Categories are post-hoc groupings of published architectures rather than axes that predict which mechanism will work on a new problem. Many methods straddle categories (the authors acknowledge this — e.g., CBAM appears in both channel and spatial sections). The fact that a paper has to be filed under its "dominant" category obscures combinations and hybrids that are actually load-bearing in practice.

**The survey omits multi-source recurrent feedback into attention.** Every cataloged self-attention variant treats attention as a *single-pass*, single-source operation: Q, K, V come from one input stream (and one frame in time). The user's Feedback Transformer — which projects multiple recurrent states into per-state Q/K/V and combines them with the sensory Q/K/V via Hadamard products before softmax — is not a member of any of the survey's categories. The closest neighbour is the "Cross Attention" / "Perceiver" cell, but those mechanisms still use a single auxiliary stream and additive (concatenative) integration, not multiplicative element-wise broadcasting across many parallel feedback sources. This is a real gap, not a coverage oversight: the architectures the user proposes had not been widely published when the survey was written.

**No head-to-head benchmarking.** The paper explicitly notes (and lists as an open problem) that attention modules are usually evaluated against a *no-attention* baseline rather than against rival attention modules. Consequently, the survey cannot say "use SE-Net for this task, use CBAM for that" with empirical authority; recommendations rest on the reported headline numbers from the individual papers, each with its own training recipe.

**The interpretability discussion is shallow.** The paper notes that stacked attention modules are hard to visualise and that attention weights do not always reflect causal contribution, but does not engage with the substantial literature on attention as explanation (e.g., Jain & Wallace 2019; Wiegreffe & Pinter 2019). Readers looking for a principled stance on interpretation will need to go elsewhere.

**The "70 articles surveyed" figure is generous.** The narrative discusses fewer than that in depth, and several of the categories (logical attention, category-based attention) are represented by a single mechanism each. The taxonomy is wider than it is uniformly deep.

**The treatment of temporal / recurrent attention is sparse.** Spatio-temporal attention is mentioned briefly in §3, and bidirectional / recurrent forms of attention (which are central to the user's program) receive only the early-LSTM-attention reference (Cheng et al. 2016) before the survey moves on to feed-forward variants. Kietzmann et al. 2019's "recurrence required for biological-grade vision" thesis is not engaged. This matters because the survey's omission of recurrent multi-source feedback is not just an oversight of one technique but a structural blind spot.

## 7. Connection to our work

This is the framing entry for the Recurrent ViT and PRISM program within the broader visual-attention-in-DL literature. Three connections matter.

**1. The user's Feedback Transformer extends two of the survey's categories simultaneously.** Hassanin et al. file SE-Net-style channel attention under "channel" (multiplicative sigmoid gating on channels via global pooling + MLP) and Transformer self-attention under "self" (Q/K/V scaled dot product). The Feedback Transformer — defined in `threads/the_user_architectural_program.md` §1 — is a structurally novel hybrid: it uses per-feedback-source learned projections to produce $Q_{C_i}, K_{C_i}, V_{C_i}$ for each recurrent state $C_i$, then combines them with the sensory $Q_S, K_S, V_S$ via Hadamard products *before* the softmax. The resulting attention score $\alpha_{ij} \propto \langle s_{q,i} \odot \sum_k c^{(k)}_{q,i}, s_{k,j} \odot \sum_k c^{(k)}_{k,j}\rangle$ is *multiplicatively* modulated by every feedback source, in the same way SE-Net's channel gating is multiplicative — but applied inside self-attention rather than to channels. This is the contribution the survey's taxonomy does not have a cell for, and it generalises the Recurrent ViT paper's §6.7 "multiplicative" variant (one feedback source, one layer) to many sources and many layers.

**2. The survey's "efficiency" open problem (§4.2 of the paper) is the constraint that motivates the GridCell RNN's two-stage design.** Hassanin et al. note that transformers' O(n²) cost is the dominant practical limit. The user's GridCell RNN (`thread` §2) addresses this by separating spatially-independent processing (SIP, per-cell, parallel, cheap) from inter-cell Feedback-Transformer integration (per-grid, expensive but amortised across feedback sources). This is the same engineering pressure the survey identifies — but the response is architectural decomposition rather than the survey's preferred remedies (sparsity, clustering, kernel approximation as in NLSA, RFA, Clustered, Efficient).

**3. The "lack of head-to-head benchmarking" open problem is the methodological gap that the user's PRISM-vs-Recurrent-ViT-vs-FeedbackTransformer experimental program should fill.** PRISM v1 (no softmax attention, prediction-error driven) and the Recurrent ViT (softmax attention with one feedback source) and the Feedback Transformer (softmax attention with many feedback sources) are members of three different cells of Hassanin et al.'s taxonomy run on the same change-detection task. Reporting their ablation on a shared benchmark is exactly the kind of cross-category comparison the survey calls for.

The survey supports the bibliography and framing of any future write-up that positions the user's work as a contribution to the broader visual-attention literature rather than as a niche change-detection result. It does *not* substitute for Khan et al. 2022 (`khan2022_transformers_vision_survey`) on the transformer-specific sub-tree, nor for Tsotsos / Mehrani 2023 (`mehrani_tsotsos2023_attention_grouping`) on the biological grounding of attention; those entries cover sub-areas Hassanin et al. only touch.

## 8. Citations to follow

- `hu2018_squeeze_excitation` — SE-Net, the canonical channel-attention paper; the user's multiplicative-feedback variant is its closest published structural ancestor. Not yet in seed.
- `woo2018_cbam` — CBAM, the canonical channel + spatial dual-branch design. Not yet in seed.
- `wang2018_nonlocal` — Non-Local Networks, the bridge from self-attention to spatial long-range dependencies in vision. Not yet in seed.
- `locatello2020_slot_attention` — Slot Attention, the closest published mechanism to the multi-hub competition architecture in `the_user_architectural_program` §5; iteratively updates competing object representations through softmax-normalised competition. In seed, full depth.
- `liu2021_swin_transformer` — Swin Transformer, the dominant hierarchical-window self-attention architecture; relevant for the user's hierarchical memory stack. Not yet in seed.
- `jaegle2021_perceiver` — Perceiver, cross-attention between a learned latent array and the sensory stream; the closest published analogue to the user's iterative-VAE guide $H$. Not yet in seed.
- `xia2022_deformable_attention` — Deformable Attention Transformer; relevant precedent for selecting which positions to attend over, analogous to the user's GridCell SIP/FT split. Not yet in seed.
- `peng2021_random_feature_attention` — RFA, kernel-approximation linear-time attention; the efficiency baseline the GridCell RNN's two-stage decomposition implicitly competes against. Not yet in seed.
- `guo2022_attention_vision_survey` — Guo et al.'s narrower attention survey (their ref [45]); a useful triangulation point for the taxonomy. Not yet in seed.
- `cheng2016_lstm_machine_reading` — the early self-attention-via-LSTM paper the survey cites as the historical bridge from recurrent to self-attention; relevant to the user's reframing of attention as a recurrent state interaction. Not yet in seed.
