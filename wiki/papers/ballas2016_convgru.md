---
id: ballas2016_convgru
title: "Delving deeper into convolutional networks for learning video representations"
authors:
  - "Ballas, Nicolas"
  - "Yao, Li"
  - "Pal, Chris"
  - "Courville, Aaron"
year: 2016
venue: "ICLR"
doi: ""
arxiv: "1511.06432"
url: "https://arxiv.org/abs/1511.06432"
tags:
  - recurrent-networks
  - deep-learning
  - representation-learning
concepts:
  - convgru-cell
  - gru-cell
  - topographic-organization
  - recurrence-for-temporal-dynamics
  - gridcell-rnn
related:
  - hochreiter_schmidhuber1997_lstm
  - jozefowicz2015_rnn_exploration
  - perez2018_film
  - cho2014_gru
  - shi2015_convlstm
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Delving deeper into convolutional networks for learning video representations

## 1. Abstract

The paper proposes a method for learning video representations that exploits *intermediate* convolutional features ("percepts") from a CNN pretrained on ImageNet, rather than relying solely on the top-layer features that most prior video models had used. The authors observe that top-layer percepts are highly discriminative but spatially collapsed — their spatial resolution is too low to capture fine-grained motion — while bottom-layer percepts retain spatial detail but lack semantic abstraction. Their solution is a **convolutional-GRU (GRU-RCN)** that replaces the fully-connected weight matrices of a standard GRU with **2-D convolutions**, so that the recurrent unit accepts and emits a feature *map* rather than a vector. Stacking GRU-RCN units across multiple CNN depths gives a model that simultaneously tracks low-, mid-, and high-level video dynamics while keeping the parameter count tractable (a fully-connected GRU on a 14×14×512 feature map would have ~10⁹ parameters; the convolutional variant has on the order of 10⁶). On UCF-101 action recognition and YouTube2Text video captioning the stacked GRU-RCN matches or exceeds prior recurrent baselines using only RGB inputs (no optical flow, no 3-D CNN features).

## 2. Why this matters for us

ConvGRU is **the memory substrate of PRISM v1**. PRISM v1's recurrent state $M_t$ is maintained over time by a ConvGRU cell whose gates operate convolutionally over the patch grid, preserving the spatial topography of the change-detection scene. Every architectural argument in PRISM v1 about "the memory remembers *where* things are" is licensed by this paper. The conv-over-FC substitution is also a load-bearing inductive bias for the user's broader program — the GridCell RNN's spatially-independent processing stage is a direct intellectual descendant of the GRU-RCN's per-location gating. Without ConvGRU as a worked precedent, PRISM v1's choice of memory cell would require independent justification.

## 3. Key claims

1. **Intermediate CNN features carry complementary spatial information** that the top layer alone discards, and a video model that ignores them is leaving signal on the table.
2. **Fully-connected RNN gates are wasteful for spatially-structured inputs.** They impose dense connectivity across all positions, scaling quadratically with spatial resolution and ignoring the visual prior that information is local.
3. **Convolutional gates are the natural inductive bias for video sequences.** Replacing $W x$ with $W * x$ in the GRU update equations preserves spatial topography, enforces translation-equivariance, and dramatically reduces parameter count.
4. **Stacking GRU-RCNs over CNN depths gives a multi-scale temporal model.** Each level has its own recurrent state; lower levels track fine spatial dynamics over short receptive fields, higher levels track abstract dynamics over large receptive fields.
5. **Empirical wins on action recognition and captioning.** The stacked GRU-RCN reaches competitive accuracy on UCF-101 and matches state of the art on YouTube2Text without optical-flow or 3-D-CNN features.

## 4. Methods

**Architecture skeleton.** A pretrained VGG-16 is run on each frame of a video clip. Feature maps are extracted at five depths (after pool2, pool3, pool4, pool5, and the fc-layer features). Each spatial feature map $X^{(l)}_t \in \mathbb{R}^{H_l \times W_l \times C_l}$ becomes the input to a depth-specific GRU-RCN whose hidden state $H^{(l)}_t \in \mathbb{R}^{H_l \times W_l \times C'_l}$ is the **same spatial shape** as the input. The five recurrent states are independent in this paper (no cross-depth feedback); their final hidden states are pooled and concatenated for classification.

**The GRU-RCN update.** Where a fully-connected GRU computes

$$
z_t = \sigma(W_z x_t + U_z h_{t-1}), \quad r_t = \sigma(W_r x_t + U_r h_{t-1})
$$
$$
\tilde h_t = \tanh(W x_t + U (r_t \odot h_{t-1})), \quad h_t = (1 - z_t) \odot h_{t-1} + z_t \odot \tilde h_t,
$$

the GRU-RCN replaces every matrix-vector product with a 2-D convolution, treating $x_t$ and $h_{t-1}$ as feature maps:

$$
z_t = \sigma(W_z * x_t + U_z * h_{t-1}), \quad r_t = \sigma(W_r * x_t + U_r * h_{t-1})
$$
$$
\tilde h_t = \tanh(W * x_t + U * (r_t \odot h_{t-1})), \quad h_t = (1 - z_t) \odot h_{t-1} + z_t \odot \tilde h_t.
$$

The Hadamard products are now per-pixel-per-channel; $z_t$ and $r_t$ are spatial maps of gate values, one per position. The convolutional kernels are typically 3×3, so the recurrent unit's receptive field grows by one kernel radius per time step.

**Parameter count.** For a $14 \times 14 \times 512$ feature map with hidden width 256, a fully-connected GRU has $\sim 3 \cdot (14 \cdot 14 \cdot 512) \cdot (14 \cdot 14 \cdot 256) \approx 1.5 \times 10^{10}$ parameters per gate matrix; the convolutional GRU with 3×3 kernels has $3 \cdot (3 \cdot 3 \cdot 512 \cdot 256) \approx 3.5 \times 10^6$ parameters total — a $\sim 10^4$ reduction.

**Training.** End-to-end backprop-through-time on UCF-101 (action recognition) and YouTube2Text (captioning). Sequence lengths are short (10–30 frames) so vanishing-gradient is less of a concern than in long-sequence text models. Dropout is applied between the recurrent layers and the classifier.

## 5. Results

**UCF-101 action recognition** (RGB only, no optical flow):
- Baseline VGG averaged over frames: ~78%.
- Top-layer fully-connected GRU: ~79%.
- Single-level GRU-RCN on pool5: ~80%.
- Stacked GRU-RCN over multiple percept depths: **~84%** — competitive with multi-stream RGB-plus-flow baselines from the same period that used additional optical-flow features.

**HMDB-51 action recognition** (RGB only): the stacked GRU-RCN reaches **~46%**, again competitive with single-stream baselines.

**YouTube2Text video captioning**: matches or exceeds the prior recurrent-decoder baselines on BLEU, METEOR, and CIDEr metrics using only RGB inputs, despite competitors using 3-D-CNN or motion features.

**Parameter efficiency**: the convolutional variant has roughly $10^4 \times$ fewer parameters than a fully-connected GRU on the same feature map and trains stably; the fully-connected variant overfits dramatically at this scale.

## 6. Critique / limitations

The five percept-level GRU-RCNs are run **independently** — there is no cross-level recurrent communication, no descending or ascending projection between depths. This is a substantial limitation from the standpoint of the user's program: the paper establishes that *parallel* multi-scale memory works, but says nothing about how to **integrate** information across scales recurrently. That integration is exactly what the user's GridCell RNN / Feedback Transformer is designed to supply.

The convolutional kernel is small (3×3). Long-range spatial dependencies must accrue across time steps via the growing temporal receptive field, which is a relatively weak mechanism — much weaker than the global mixing a self-attention layer provides. Subsequent work (ConvLSTM, predRNN, attention-augmented ConvLSTMs) addressed this by either enlarging kernels or by injecting attention into the recurrent update.

The model has no explicit *forget* mechanism analogous to LSTM's forget gate; the GRU's update gate $z_t$ does both reset and forget. Whether this is adequate for long video sequences (minute-scale, not clip-scale) is not tested.

There is no analysis of what the convolutional gates *learn*. Are the gates spatially uniform (in which case the conv structure was unnecessary) or do they exhibit interpretable spatial patterns (object/motion masks)? This was a missed opportunity for representational analysis that subsequent work (Lotter et al. PredNet; Finn et al. video prediction) partially filled.

The paper does not compare ConvGRU to ConvLSTM (Shi et al. 2015, NIPS), which appeared months earlier and proposed essentially the same idea for the LSTM cell. The ConvGRU framing is therefore best read as a *GRU adaptation* of an idea Shi et al. introduced for LSTM — the novel contribution being the multi-percept-level stacking, not the conv-gating itself.

## 7. Connection to our work

This paper is the memory cell of PRISM v1 and a foundational reference for the user's GridCell RNN. Several specific connections are load-bearing.

**ConvGRU as PRISM v1's working memory.** PRISM v1 maintains a recurrent state $M_t$ over a sequence of attended patches in a change-detection trial (`THESIS.md` §2.4–§2.5). The cell is a ConvGRU exactly as defined in this paper: the gate maps $z_t$, $r_t$ are spatial; the kernel is small; the hidden state has the same patch-grid shape as the input. The architectural decision the paper licenses is that **a recurrent memory of *visual* content should have *visual* structure** — the memory state is not a flattened vector but a feature map registered to the scene's patch grid. This is what makes PRISM v1's memory "remember where things are" without an explicit position encoding: spatial topography is preserved by the recurrence itself.

**Why convolutional gating is the right inductive bias.** A fully-connected GRU over an $H \times W$ patch grid would mix all $HW$ positions in every gate computation, paying $O(H^2 W^2)$ parameters and destroying the patch-grid registration the model needs to localize a change. The convolutional gate mixes only nearby positions per step, paying $O(k^2)$ parameters per channel pair (where $k$ is kernel size), and the gate at position $(i, j)$ is a function of a *local neighborhood* of the previous memory state. This is the same inductive bias that justifies CNNs over MLPs for static images, applied to the *recurrent* axis: visual information is spatially local, so the recurrent operator should be too.

**Link to the GridCell RNN.** The GridCell RNN's stage-one **spatially-independent processing (SIP)** is essentially a ConvGRU update specialized to a $1 \times 1$ kernel — each grid cell is processed independently with the LSTM-style gates of the user's notes. The user's stage two then adds the inter-cell communication that this paper's GRU-RCN explicitly *lacks* (the Feedback Transformer). So the user's design can be read as **GRU-RCN + cross-cell self-attention**, with this paper supplying the within-cell recurrent primitive and Vaswani et al. supplying the between-cell mixer. The clean factorization is what allows the user's system to scale to many memory layers without combinatorial blowup, and the conceptual ancestor of that factorization is in this paper's stacking of multiple independent GRU-RCNs.

**Multi-compartmental memory and the unrealized potential here.** The paper stacks five GRU-RCNs at five CNN depths *but does not let them talk to each other*. The user's multi-compartmental memory (`the_user_architectural_program.md` §3) is exactly the missing piece: descending convolutional projections and ascending conv-transpose projections that couple GRU-RCNs across the hierarchy. So this paper is best read as *one half* of the architecture the user proposes — the per-layer recurrent state — with the inter-layer feedback supplied by the user's contribution.

**Connection to PRISM v2.** PRISM v2 keeps ConvGRU as the per-patch memory cell (`PRISM_V2_PROPOSAL.md` §3.2) and adds the slow-fast dual-timescale structure on top. The slow memory is still a ConvGRU, just with a slower effective update rate. The paper's parameter-efficiency argument is what makes the dual-memory commitment feasible — two parallel ConvGRUs at full spatial resolution would be prohibitive if either were fully connected.

**Connection to FiLM modulation.** PRISM v1's FiLM injection point (`THESIS.md` §2.4) sits *upstream* of the ConvGRU, supplying per-channel scale/shift conditioning. The ConvGRU's gating is convolutional; the FiLM modulation is featurewise-affine. The two compose: FiLM tells the ConvGRU *what* features to weight, the ConvGRU's gates decide *whether to update* each spatial position. See `perez2018_film` for the modulation primitive; this paper for the recurrent primitive that consumes its output.

## 8. Citations to follow

- `shi2015_convlstm` — Shi, Chen, Wang, Yeung, Wong, Woo, "Convolutional LSTM Network: A machine learning approach for precipitation nowcasting." NIPS 2015. The earlier-and-essentially-equivalent ConvLSTM. Should be in the database as the genuine origin of conv-recurrent cells; the present paper is the GRU port.
- `cho2014_gru` — Cho, van Merriënboer, Bahdanau, Bengio. The fully-connected GRU this paper adapts. **In seed, full depth; should be added.**
- `simonyan_zisserman2014_vgg` — VGG-16 is the CNN backbone of every experiment in this paper.
- `simonyan_zisserman2014_two_stream` — Two-stream RGB+flow networks are the comparison baseline on UCF-101.
- `donahue2015_lrcn` — Long-term recurrent convolutional networks; the top-layer-GRU baseline this paper improves on.
- `tran2015_c3d` — 3-D ConvNets for video; the convolutional alternative this paper outperforms with RGB-only inputs.
- `xu2015_show_attend_tell` — Soft-attention captioning that frames this paper's YouTube2Text experiments.
- `lotter2016_prednet` — PredNet uses ConvLSTM-style cells in a predictive-coding stack; the natural follow-up combining this paper's recurrent primitive with hierarchical feedback.
