---
id: shi2015_convlstm
title: "Convolutional LSTM Network: A Machine Learning Approach for Precipitation Nowcasting"
authors:
  - "Shi, Xingjian"
  - "Chen, Zhourong"
  - "Wang, Hao"
  - "Yeung, Dit-Yan"
  - "Wong, Wai-kin"
  - "Woo, Wang-chun"
year: 2015
venue: "NIPS 2015"
doi: ""
arxiv: "1506.04214"
url: "https://arxiv.org/abs/1506.04214"
tags:
  - recurrent-networks
  - deep-learning
  - representation-learning
concepts:
  - lstm-cell
  - convgru-cell
  - topographic-organization
  - recurrence-for-temporal-dynamics
related:
  - ballas2016_convgru
  - hochreiter_schmidhuber1997_lstm
  - jozefowicz2015_rnn_exploration
  - cho2014_gru
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-16"
---

# Convolutional LSTM Network: A Machine Learning Approach for Precipitation Nowcasting

## 1. Abstract

The goal of precipitation nowcasting is to predict the future rainfall intensity in a local region over a relatively short period of time, formulated by the authors as a *spatiotemporal sequence forecasting* problem in which both the input and the prediction target are sequences of two-dimensional radar maps. The paper observes that the dominant recurrent primitive of the era — the fully-connected LSTM (FC-LSTM) — is poorly suited to such inputs: collapsing each 2-D radar frame to a vector destroys the spatial structure that any sensible forecaster must respect, and the parameter count of FC weight matrices on flattened images is prohibitive. The authors propose **ConvLSTM**, an LSTM variant in which *all* input-to-state and state-to-state matrix multiplications are replaced by **2-D convolutions**, so that the cell state, hidden state, and three gates are themselves spatial feature maps registered to the input grid. They build an end-to-end encoder–forecaster stack of ConvLSTM layers that consumes a short sequence of radar maps and emits a sequence of future maps. On a synthetic Moving-MNIST benchmark the model substantially outperforms FC-LSTM with comparable parameter budget; on a real Hong Kong radar-echo dataset it outperforms both FC-LSTM and the operational ROVER optical-flow forecasting algorithm on standard meteorological skill metrics (CSI, FAR, POD, correlation). ConvLSTM is presented as a general spatiotemporal primitive, not a precipitation-specific tool.

## 2. Why this matters for us

ConvLSTM is the **architectural origin point** of the convolutional-recurrent cell family that PRISM v1's ConvGRU memory belongs to. Every PRISM v1 argument about a recurrent state that "remembers *where* things are without an explicit position encoding" descends, intellectually, from this paper: the claim that recurrent dynamics over visual content should preserve spatial topography rather than flatten through a fully-connected weight matrix. The application — *spatiotemporal prediction* of future frames from past ones — is also conceptually aligned with our work: the Recurrent ViT's change-detection task is a discrimination among possible future scene-states, and PRISM v1's predictive-feedback substrate is, ultimately, a spatiotemporal forecaster. ConvLSTM's encoder–forecaster construction is the closest published precursor of the user's iterative encoder–decoder (`the_user_architectural_program.md` §4), differing mainly in that ConvLSTM uses a single forward pass over the sequence rather than $n_{FR}$ forward-reasoning iterations over the same input.

## 3. Key claims

1. **Precipitation nowcasting is naturally a spatiotemporal sequence prediction problem**, not a per-pixel regression problem; treating it as the former licenses learning end-to-end from data rather than relying on hand-engineered optical-flow heuristics.
2. **Fully-connected LSTM is the wrong inductive bias for spatial inputs.** Flattening discards locality and translation-equivariance and explodes the parameter count.
3. **Replacing matrix products with convolutions in *all* LSTM gates** — input-to-state *and* state-to-state — yields a recurrent unit whose hidden state is a feature map preserving spatial topography.
4. **Stacking ConvLSTM layers in an encoder–forecaster configuration** enables learning long-range spatiotemporal correlations while keeping parameter counts tractable.
5. **ConvLSTM beats FC-LSTM on Moving-MNIST and beats both FC-LSTM and the operational ROVER algorithm on real radar-echo nowcasting**, demonstrating that the convolutional-recurrent inductive bias is the source of the gain rather than mere extra capacity.

## 4. Methods

**The ConvLSTM cell.** Let $\mathcal{X}_t \in \mathbb{R}^{H \times W \times C_x}$ be the input feature map at time $t$ and $\mathcal{H}_t, \mathcal{C}_t \in \mathbb{R}^{H \times W \times C_h}$ be the hidden state and cell state — both feature maps with the same spatial shape as the input. The update equations are

$$
i_t = \sigma(W_{xi} * \mathcal{X}_t + W_{hi} * \mathcal{H}_{t-1} + W_{ci} \odot \mathcal{C}_{t-1} + b_i)
$$
$$
f_t = \sigma(W_{xf} * \mathcal{X}_t + W_{hf} * \mathcal{H}_{t-1} + W_{cf} \odot \mathcal{C}_{t-1} + b_f)
$$
$$
\mathcal{C}_t = f_t \odot \mathcal{C}_{t-1} + i_t \odot \tanh(W_{xc} * \mathcal{X}_t + W_{hc} * \mathcal{H}_{t-1} + b_c)
$$
$$
o_t = \sigma(W_{xo} * \mathcal{X}_t + W_{ho} * \mathcal{H}_{t-1} + W_{co} \odot \mathcal{C}_t + b_o)
$$
$$
\mathcal{H}_t = o_t \odot \tanh(\mathcal{C}_t)
$$

where $*$ is 2-D convolution and $\odot$ is the Hadamard product. The $W_{c\cdot}$ are peephole connections (still elementwise to keep the spatial structure of the cell state); everything else is convolutional. Kernels are typically $3 \times 3$ or $5 \times 5$.

**Encoder–forecaster architecture.** The end-to-end model is a two-network stack. The *encoding network* is a stack of ConvLSTM layers that consumes the input sequence $\mathcal{X}_1, \ldots, \mathcal{X}_J$ and produces a final hidden/cell state at each layer. The *forecasting network* is a separate stack of ConvLSTM layers initialized from the encoder's final states; it autoregressively produces the prediction sequence $\hat{\mathcal{X}}_{J+1}, \ldots, \hat{\mathcal{X}}_{J+K}$. The forecasting network's hidden states at each step are concatenated across layers and passed through a $1 \times 1$ convolution to produce the predicted frame.

**Datasets.** Moving-MNIST: two digits move with random initial position and velocity inside a $64 \times 64$ frame for 20 steps; the model sees 10 and predicts the next 10. Hong Kong Observatory radar echo maps: 97 rainy days, $100 \times 100$ radar pixel grid, each step is 6 minutes; model sees 5 and predicts the next 15 (90-minute nowcast).

**Configurations.** Up to 3 stacked ConvLSTM layers; hidden channel counts of 64 / 128 / 128 per layer; kernel sizes $3 \times 3$ to $5 \times 5$. Optimized end-to-end with RMSProp and BPTT.

## 5. Results

**Moving-MNIST (cross-entropy per sequence, lower is better).** FC-LSTM with a comparable parameter budget reaches $\sim 4832$ nats per sequence; single-layer ConvLSTM with $5 \times 5$ kernel reaches $\sim 4185$; a 3-layer ConvLSTM with $5 \times 5$ kernels reaches $\sim 3670$ — the deepest convolutional stack substantially outperforming FC-LSTM despite using **fewer parameters**.

**Radar nowcasting** (skill metrics averaged over 15 forecast steps; rainfall threshold 0.5 mm/h):
- ROVER (operational optical-flow baseline): CSI $\approx 0.45$, FAR $\approx 0.52$, POD $\approx 0.66$, correlation $\approx 0.64$.
- FC-LSTM: comparable or worse than ROVER on most skill metrics, despite end-to-end training.
- ConvLSTM (2-layer, $3 \times 3$ kernels, 64 channels): CSI $\approx 0.58$, FAR $\approx 0.39$, POD $\approx 0.71$, correlation $\approx 0.73$ — uniformly best.

**Parameter efficiency.** ConvLSTM achieves better Moving-MNIST loss than FC-LSTM with roughly an order of magnitude fewer parameters, demonstrating that the spatial-convolutional inductive bias is the source of the gain, not extra capacity.

**Kernel size and depth.** Larger kernels ($5 \times 5$) marginally outperform smaller ($3 \times 3$) on Moving-MNIST when the motion is fast; stacking depth helps consistently up to 3 layers, after which gains plateau.

## 6. Critique / limitations

The state-to-state convolutional kernel is small (typically $3 \times 3$). Long-range spatial dependencies must accumulate via repeated time steps, which is a weak mixer compared to a global self-attention operator. Subsequent work (Trajectory GRU; PredRNN; attention-augmented ConvLSTMs) addressed this by either learning location-variant connections (TrajGRU) or interleaving the recurrent dynamics with global mixing. From the standpoint of the user's program, the conv kernel is exactly the kind of *local-only* recurrent operator that the Feedback Transformer is designed to augment with global cross-position communication.

The encoder–forecaster split is hand-designed and the forecaster is autoregressive in pixel space, which compounds prediction errors over long horizons. The model has no explicit mechanism for separating *deterministic* from *stochastic* future dynamics — there is no latent random variable bridging encoder and forecaster, no VAE structure. This is the gap the user's iterative variational encoder–decoder (`the_user_architectural_program.md` §4) is designed to fill: place a latent $\tilde H_0$ between encoder and decoder so that future-frame uncertainty is captured by a KL-regularized stochastic layer, not by greedy autoregression.

ConvLSTM layers in the paper do not communicate cross-hierarchically — each layer's hidden state evolves in isolation aside from the strict bottom-up input flow between layers. There are no descending projections from deeper to shallower layers, no ascending feedback from shallower to deeper, no parallel-hub feedback. The architecture is therefore strictly *feedforward across the depth axis*, even though it is recurrent across time. This is the same limitation `ballas2016_convgru` carries and the same gap the user's multi-compartmental memory (`the_user_architectural_program.md` §3) is designed to fill.

The peephole convolution is awkward: cell-state-to-gate connections use Hadamard products (elementwise, no convolutional mixing) rather than full convolutions, breaking the conceptual cleanliness of "all matrix-multiplies become convolutions". Most subsequent work (including ConvGRU) drops peephole connections without loss of performance, suggesting they were a holdover from FC-LSTM rather than a load-bearing component.

The model is trained and evaluated on relatively short sequences (10–20 frames). Long-horizon stability — error compounding over hundreds of forecast steps — is not tested, and the architecture has no explicit mechanism to prevent it.

No representational analysis. The paper demonstrates the spatial gates work but does not analyze *what* the gates learn. Are the forget-gate maps spatially organized in interpretable ways (e.g., low forget rate inside coherent rain cells, high forget rate at frame boundaries)? This was a missed opportunity later partially filled by PredNet and trajectory-GRU analyses.

## 7. Connection to our work

This paper is the **conceptual origin** of the conv-recurrent cell that PRISM v1's memory inherits via ConvGRU. Several specific connections are load-bearing for the user's program.

**Convolutional recurrence preserves spatial topography — the foundational claim PRISM v1 relies on.** PRISM v1 maintains a recurrent memory state $M_t$ over a change-detection trial whose entire job is to "remember where things are" in the scene. The architectural decision to make $M_t$ a feature map registered to the patch grid, with gates that operate convolutionally rather than across all positions, is the design choice ConvLSTM established. Without this paper (and its ConvGRU descendant `ballas2016_convgru`), PRISM v1 would have to justify the conv-recurrent substrate independently from first principles. The paper supplies that justification empirically on a spatiotemporal forecasting benchmark — exactly the family of tasks PRISM and the Recurrent ViT operate on.

**Input-to-state convolution is the architectural justification for keeping convolutions inside the recurrent dynamics.** A crucial subtlety: FC-LSTM with a CNN feature extractor in front of it is *not* equivalent to ConvLSTM. The CNN extracts spatial features, but the LSTM then immediately flattens them, destroying topography inside the recurrent state. ConvLSTM's contribution is to keep the convolutional structure *inside* the loop — so the recurrent state itself has a spatial layout that persists from step to step. This is the architectural commitment that the user's GridCell RNN's spatially-independent processing stage (`the_user_architectural_program.md` §2) inherits: per-cell gated updates that preserve spatial registration, with the Feedback Transformer then supplying the cross-cell mixing that ConvLSTM's $3 \times 3$ kernel cannot.

**Encoder–forecaster as one-shot ancestor of the iterative encoder–decoder.** ConvLSTM's encoder–forecaster split is the closest published structure to the user's iterative-VAE construction (`the_user_architectural_program.md` §4). The differences are illuminating: ConvLSTM runs the encoder forward once, then runs the forecaster forward once. The user's program runs the encoder $n_{FR}$ times *on the same image* (forward reasoning), then runs the decoder $n_{BR}$ times producing iteratively refined reconstructions (backward reasoning), with a KL-regularized latent bridging the two. ConvLSTM thus supplies the *structural template* — a recurrent encoder paired with a recurrent decoder that consumes the encoder's final state — and the user's contribution is to (a) iterate each direction multiple times, (b) interpose a stochastic latent for variational regularization, and (c) decode reconstruction proposals at every $n_{BR}$ step.

**Hadamard-product peephole connections are an early instance of multiplicative-feedback gating.** The Hadamard products $W_{ci} \odot \mathcal{C}_{t-1}$ etc. in the gate equations are a primitive form of multiplicative feedback from the cell state into the gates. The Recurrent ViT paper's "multiplicative feedback" variant (`2502.10955` §6.7) is structurally similar — it injects memory into the attention mechanism via per-position multiplicative scaling. ConvLSTM's peephole is the most basic version of this: cell-state values multiplicatively modulate gate activations at the same spatial position. The Feedback Transformer's element-wise broadcasting of feedback Q/K/V into sensory Q/K/V (`the_user_architectural_program.md` §1) is the general form of which peepholes are a heavily simplified ancestor.

**Spatiotemporal forecasting as task substrate.** The user's program includes a video-autoencoding task (UCF101 reconstruction, the most successful current empirical instance — `the_user_architectural_program.md` §6) and an eye-tracking forecasting task. Both are members of the same task family ConvLSTM established as benchmarks for conv-recurrent models. The paper's framing of "spatiotemporal sequence forecasting" as a unifying problem class — applicable to weather, video, and other gridded time series — is the conceptual ancestor of the video VAE task setup.

**Connection to PRISM v2.** PRISM v2's slow-fast dual-memory stack (`PRISM_V2_PROPOSAL.md` §3.3) is two parallel conv-recurrent cells differing only in effective update rate. The parameter-efficiency argument that makes this dual stack feasible at full spatial resolution rests on the conv-over-FC substitution this paper introduced. A dual FC-LSTM at the same resolution would be parameter-prohibitive; a dual ConvLSTM at the same resolution is routine.

**Conceptual limit of ConvLSTM that motivates the Feedback Transformer.** ConvLSTM's only inter-position mixing is via the $3 \times 3$ convolutional kernel, which grows linearly per time step. For change-detection over a scene where the change can be arbitrarily far from prior fixations, this is too slow. The Feedback Transformer's role is precisely to supply global position mixing inside the recurrent loop while keeping the spatial registration ConvLSTM established. The two designs are therefore complementary, and the user's architecture is best read as **ConvLSTM-style spatial recurrence + Vaswani-style global mixing**, with this paper supplying the former half.

## 8. Citations to follow

- `cho2014_gru` — Cho, van Merriënboer, Bahdanau, Bengio. The fully-connected GRU that `ballas2016_convgru` later adapted analogously to what this paper did for LSTM. **In seed, full depth; should be added.**
- `srivastava2015_unsupervised_video_lstm` — Srivastava, Mansimov, Salakhutdinov. Encoder–decoder LSTM for unsupervised video learning; the FC-LSTM baseline in this paper and the direct conceptual ancestor of the encoder–forecaster framing.
- `sutskever2014_seq2seq` — Sutskever, Vinyals, Le. Sequence-to-sequence learning; the encoder–decoder template generalized here to 2-D feature maps.
- `lotter2016_prednet` — PredNet stacks ConvLSTM cells in a predictive-coding hierarchy with explicit error-driven feedback between layers — the bidirectional-feedback extension this paper lacks.
- `wang2017_predrnn` — PredRNN; spatiotemporal LSTM with cross-layer "highway" memory that addresses this paper's lack of cross-layer recurrent communication.
- `shi2017_trajgru` — Shi et al. follow-up; TrajGRU learns location-variant recurrent connections, addressing the small-kernel locality limit of the present paper.
- `finn2016_video_prediction` — Action-conditioned video prediction; combines ConvLSTM-style recurrence with explicit motion-decomposition modules.
