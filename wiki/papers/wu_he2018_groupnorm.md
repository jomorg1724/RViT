---
id: wu_he2018_groupnorm
title: "Group Normalization"
authors:
  - "Wu, Yuxin"
  - "He, Kaiming"
year: 2018
venue: "ECCV"
doi: "10.1007/978-3-030-01261-8_1"
arxiv: "1803.08494"
url: "https://arxiv.org/abs/1803.08494"
tags:
  - deep-learning
  - methodology
concepts:
  - divisive-normalization
  - gain-modulation
  - gridcell-rnn
related:
  - vaswani2017_attention
  - reynolds_heeger2009_normalization
  - kingma_ba2015_adam
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Group Normalization

## 1. Abstract

Batch Normalization (BN) is a milestone technique in the development of deep learning, enabling various networks to train. However, normalizing along the batch dimension introduces problems — BN's error increases rapidly when the batch size becomes smaller, caused by inaccurate batch statistics estimation. This limits BN's usage for training larger models and transferring features to computer vision tasks including detection, segmentation, and video, which require small batches constrained by memory consumption. In this paper, the authors present Group Normalization (GN) as a simple alternative to BN. GN divides the channels into groups and computes within each group the mean and variance for normalization. GN's computation is independent of batch sizes, and its accuracy is stable in a wide range of batch sizes. On ResNet-50 trained in ImageNet, GN has 10.6% lower error than its BN counterpart when using a batch size of 2; when using typical batch sizes, GN is comparably good with BN and outperforms other normalization variants. Moreover, GN can be naturally transferred from pre-training to fine-tuning. GN outperforms its BN-based counterparts for object detection and segmentation in COCO, and for video classification in Kinetics, showing that GN can effectively replace BN in a variety of tasks. GN can be implemented by a few lines of code in modern libraries.

## 2. Why this matters for us

Group Normalization is the normalization layer used throughout the user's architectural program — Recurrent ViT, PRISM v1, PRISM v2, and the MCLSTM change-detection variants. The choice is *load-bearing*, not cosmetic. Three things drive it. First, all of these models are trained with *small effective batches per device* — recurrent rollouts over video sequences make each gradient step a batch of trajectories, not a batch of i.i.d. frames, and BN's batch-statistic noise corrupts both training and inference. Second, the user's recent MCLSTM architecture findings memo explicitly identifies GroupNorm as one of the *missing* ingredients that turned a non-working architecture into a working one — alongside the corrected kinetic-gate direction, three-memory layout, and the `memory_compute` block. Third, GN's per-sample channel-group statistics are the deep-learning analog of *divisive normalization* in early visual cortex (Reynolds & Heeger 2009), which is itself a load-bearing neuroscience reference for the user's competition-emergent-predictive-coding thesis: GroupNorm is therefore not just a numerical-stability trick but a structural commitment that aligns the architecture's normalization stage with the canonical cortical computation.

## 3. Key claims

1. BatchNorm's error grows rapidly as batch size decreases because the per-batch mean and variance become noisy estimates of the population statistics; at batch size 2 on ResNet-50/ImageNet the gap to a large-batch BN is over 10 percentage points.
2. Normalizing along the *channel* axis — partitioned into $G$ groups of $C/G$ channels each — produces statistics that are computed *per sample* and are therefore *independent of batch size*.
3. GroupNorm interpolates between LayerNorm ($G=1$: one group of all channels) and InstanceNorm ($G=C$: one group per channel) and outperforms both endpoints across vision tasks.
4. GroupNorm matches BatchNorm at *large* batch sizes (e.g., 32) on ImageNet ResNet-50 (24.1% vs 23.6% top-1 error) while strictly outperforming it at small batch sizes.
5. GroupNorm transfers cleanly from pre-training to fine-tuning — there is no train/eval discrepancy in statistics, unlike BN's running-mean/running-variance buffers.
6. GroupNorm outperforms BN on COCO detection/segmentation (Mask R-CNN) and Kinetics video classification, where small batches are forced by memory constraints.
7. The number of groups $G$ is a robust hyperparameter — performance is stable across $G \in \{8, 16, 32, 64\}$ with a mild optimum near $G=32$ for typical channel counts.
8. The construction is motivated by divisive normalization in visual cortex and by classical grouped-feature representations (SIFT, HOG), where features are normalized within groups of related channels rather than globally.

## 4. Methods

For a 4D activation tensor $x \in \mathbb{R}^{N \times C \times H \times W}$ — batch, channel, height, width — a normalization layer computes

$$
\hat x_i = \frac{x_i - \mu_i}{\sqrt{\sigma_i^2 + \epsilon}}, \qquad y_i = \gamma \hat x_i + \beta
$$

where the mean $\mu_i$ and variance $\sigma_i^2$ are computed over an index set $\mathcal{S}_i$ that defines the normalization scheme:

- **BatchNorm:** $\mathcal{S}_i = \{j : j_C = i_C\}$ — average over batch and spatial dimensions per channel.
- **LayerNorm:** $\mathcal{S}_i = \{j : j_N = i_N\}$ — average over channels and spatial per sample.
- **InstanceNorm:** $\mathcal{S}_i = \{j : j_N = i_N, j_C = i_C\}$ — average over spatial per (sample, channel).
- **GroupNorm:** $\mathcal{S}_i = \{j : j_N = i_N, \lfloor j_C / (C/G) \rfloor = \lfloor i_C / (C/G) \rfloor\}$ — average over spatial and over a *group* of $C/G$ adjacent channels, per sample.

The per-channel affine parameters $\gamma, \beta \in \mathbb{R}^C$ are learned. GroupNorm has *no* running statistics, no train/eval distinction, and no dependence on $N$.

**Experimental setup.** ResNet-50 on ImageNet at batch sizes $\{32, 16, 8, 4, 2\}$ per GPU (8 GPUs), trained with the standard 100-epoch schedule. For detection/segmentation: Mask R-CNN with ResNet-50 / ResNet-101 FPN backbones on COCO, where memory limits force batch sizes of 1–2 images per GPU. For video: I3D on Kinetics with short clip batches. $G = 32$ is the default; ablations vary $G$ and also vary the per-group channel count $C/G$.

## 5. Results

**ImageNet ResNet-50 top-1 error (batch size per GPU):**

| Method | bs=32 | bs=16 | bs=8 | bs=4 | bs=2 |
|---|---|---|---|---|---|
| BN | 23.6 | 23.7 | 24.8 | 27.3 | 34.7 |
| GN | 24.1 | 24.2 | 24.0 | 24.2 | 24.1 |

GN is essentially flat across batch sizes; BN degrades by >10 points at bs=2.

**Groups ablation (bs=32, ResNet-50):** $G=32$: 24.1%, $G=16$: 24.6%, $G=8$: 24.4%, $G=4$: 24.6%, $G=2$: 25.6%, $G=1$ (LayerNorm): 25.3%. Per-group channel count $C/G$: 64 → 24.3%, 32 → 24.4%, 16 → 24.2%, 8 → 24.0%. Stable across roughly an order of magnitude in $G$.

**COCO Mask R-CNN (ResNet-50 FPN, fine-tuned from ImageNet pretrain):** GN box AP 38.0 vs BN* (frozen) 37.7; mask AP 34.3 vs 32.8. With ResNet-101 backbones the GN gap widens. Training Mask R-CNN *from scratch* with GN reaches 39.5 box AP — competitive with the pretrained baseline — which is not possible with frozen BN.

**Kinetics I3D:** GN matches or exceeds BN; at clip batch size 4 GN beats BN by ~3 points top-1.

## 6. Critique / limitations

GroupNorm trades batch-size dependence for the introduction of a discrete hyperparameter $G$. While the ablation shows robustness, $G$ has to be chosen so that $C/G$ is integer and meaningful at every layer, which complicates architectures with heterogeneous channel counts (e.g., U-Nets, transformer blocks with $d_{\text{model}}$ not divisible by typical $G$). A naïve $G=32$ everywhere can produce per-group sizes of $1$ (collapsing to InstanceNorm) or $C$ (collapsing to LayerNorm) at the extremes of the network.

The biological motivation — channels grouped by tuning similarity — is not enforced architecturally. Adjacent channels in a conv layer are *not* known to be tuning-similar; the grouping is arbitrary at initialization and only becomes meaningful insofar as training arranges related features into contiguous channel blocks. Subsequent work (e.g., switchable normalization, evolved normalization layers) explores this question further. The paper does not analyze whether channel reordering after training would change the effective normalization.

The 2018 results are predominantly on CNN backbones. GN's behavior in transformer architectures, where LayerNorm is the canonical choice, is empirically established by subsequent work but not by this paper. For pure transformers with token-level normalization the GN-vs-LN distinction is partially moot; for *vision transformers with spatial structure* (the user's setting) the question of whether to group channels is open.

The "GN = divisive normalization" framing is suggestive but informal. Reynolds & Heeger 2009's divisive normalization has *learned* normalization weights, surround-suppression structure, and contrast-dependent gain — none of which GroupNorm implements. The analogy is at the level of "divide each unit by a pool of related units," not at the level of mechanism.

Finally, GN has no obvious account of the *training dynamics* benefits BN provides (gradient smoothing, learning-rate robustness). The paper measures end-task accuracy, not optimization landscape geometry.

## 7. Connection to our work

GroupNorm is the normalization layer in *every* serious model in the user's program, and the architectural reasons reach beyond convenience.

**Recurrent ViT (2502.10955).** The recurrent rollouts in change-detection training present each gradient step with a batch of *trajectories*, each containing temporally-correlated frames. Per-frame batch statistics under BN would mix samples across timesteps and drift across the rollout; per-sample, per-group GN statistics keep the normalization local to the trajectory and stable across the rollout's recurrent passes. The paper's bs=2 result is the empirical anchor: at the small effective batches typical of recurrent video training, BN's degradation is severe, and GN is the natural replacement.

**MCLSTM change-detection architecture (memory file `project_mclstm_architecture_findings.md`).** The user's recent memo explicitly identifies GroupNorm as one of the architectural ingredients that converted a non-working MCLSTM into a working one, alongside the corrected kinetic-gate direction, the three-memory layout, and the `memory_compute` block. The memo notes GN is load-bearing because the kinetic-gate update equations are highly sensitive to activation magnitudes that BN's running statistics would corrupt during recurrent rollouts. This is the single sharpest internal validation that GN is not an interchangeable choice.

**PRISM v1 and PRISM v2.** Both maintain memory states $M_t$ over time. PRISM v1's FiLM modulation (`THESIS.md` §2.4) and PRISM v2's hierarchical FiLM (`PRISM_V2_PROPOSAL.md` §3.4) apply learned channel-wise affine modulation on top of normalized features. GN provides the substrate: the per-group divisive normalization sets each channel's pre-FiLM gain to a stable per-sample scale, and FiLM then implements the *learned, content-dependent* gain modulation. This is structurally the same two-stage operation as in Reynolds & Heeger 2009: divisive normalization first, then attention-dependent multiplicative gain.

**Feedback Transformer.** The Feedback Transformer (`concepts/feedback_transformer.md`) integrates multiple feedback sources into the Q/K/V projections via element-wise multiplication. Pre-normalization of each source's channels with GN keeps the multiplicative interactions from blowing up — a feedback source with an outlier activation in one channel would otherwise dominate the Hadamard product. GN's per-group, per-sample statistics ensure each feedback source contributes at a comparable scale.

**Connection to the divisive-normalization / biased-competition literature.** Reynolds & Heeger 2009 (in the seed, full depth) is the canonical neuroscience reference for normalization as the substrate of attention. GroupNorm is the deep-learning analog: each unit's response is divided by the pooled response of a group of related units. The user's program treats this analogy seriously — see thread `the_user_architectural_program` §1 (Feedback Transformer) and §5 (Competition-emergent predictive coding). In the competition-emergent account, GN implements the *resource-bandwidth constraint*: within each group only a finite "budget" of activation magnitude is available, and feature channels within the group compete divisively for it. This is the architectural mechanism by which coalition-resource-competition manifests at the activation-statistics level.

**Practical hyperparameter choices in the user's code.** The user defaults to $G = 8$ or $G = 16$ for layers with $C \in \{64, 128, 256, 512\}$, giving per-group channel counts of $8$–$64$, well within the paper's stable range. Layers with unusual channel counts (e.g., $C = 384$ in some ViT variants) use $G = 8$ to keep per-group sizes integer.

**What this paper does *not* directly support.** It does not establish that GN is the right normalization for transformer self-attention sub-layers, where LayerNorm is the canonical choice. The user's program uses LN inside transformer blocks and GN in the conv stems / patch encoders / SIP stages. The boundary between LN and GN regions of the architecture is an open design question this paper does not resolve.

## 8. Citations to follow

- `ioffe_szegedy2015_batchnorm` — the original BatchNorm paper; the foil against which GN is defined. Not yet in seed. Add as a stub.
- `ba_kiros_hinton2016_layernorm` — LayerNorm; the $G=1$ endpoint of GN. Not yet in seed. Add as a stub.
- `ulyanov2016_instance_normalization` — InstanceNorm; the $G=C$ endpoint of GN. Not yet in seed. Add as a stub.
- `salimans_kingma2016_weight_norm` — alternative normalization scheme often used in RL/recurrent settings. Not in seed.
- `he2016_resnet` — the backbone used in all ImageNet comparisons. Should be added; not in seed.
- `lin2017_focal_loss` / `he2017_mask_rcnn` — the COCO Mask R-CNN setup used for the detection/segmentation transfer results. Not in seed.
- `carreira_zisserman2017_i3d` — the Kinetics video classification backbone. Not in seed.
- `heeger1992_normalization_v1` — the foundational neuroscience reference behind divisive normalization in V1, predating Reynolds & Heeger 2009. Should be added as the historical anchor; not in seed.
- `luo2018_understanding_bn` — analysis of BN's optimization-landscape effects, relevant to the §6 limitation that GN lacks a parallel analysis. Not in seed.
- `wu2019_evolving_normalization` — successor work treating normalization as a search problem; relevant to whether $G$ is the right parametrization. Not in seed.
