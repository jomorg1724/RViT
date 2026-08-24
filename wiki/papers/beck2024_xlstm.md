---
id: beck2024_xlstm
title: "xLSTM: Extended Long Short-Term Memory"
authors:
  - "Beck, Maximilian"
  - "Pöppel, Korbinian"
  - "Spanring, Markus"
  - "Auer, Andreas"
  - "et al."
year: 2024
venue: "arXiv:2405.04517"
doi: ""
arxiv: "2405.04517"
url: "https://arxiv.org/abs/2405.04517"
tags:
  - recurrent-networks
  - deep-learning
  - transformers
concepts:
  - lstm-cell
  - xlstm
  - slow-fast-recurrence
  - multiplicative-feedback
  - multi-compartmental-memory
related:
  - hochreiter_schmidhuber1997_lstm
  - vaswani2017_attention
  - mujika2017_fast_slow_rnn
  - tallec_ollivier2018_chrono_init
  - wang2025_hierarchical_reasoning_model
  - jozefowicz2015_rnn_exploration
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_41
status: full
depth: full
last_updated: "2026-05-16"
---

# xLSTM: Extended Long Short-Term Memory

> **Sourcing note.** Abstract is verbatim from arXiv:2405.04517. Architectural details, gating equations, and block structure are sourced from the paper's body via WebFetch. Several specific benchmark numbers (PALOMA perplexity, downstream-task accuracies at 1.3B / 2.7B) could not be cleanly extracted from the binary PDF in this session; the qualitative comparative claims (xLSTM favorable vs Transformers and SSMs at matched scale) are sourced from the abstract.

## 1. Abstract

In the 1990s, the constant error carousel and gating were introduced as the central ideas of the Long Short-Term Memory (LSTM). Since then, LSTMs have stood the test of time and contributed to numerous deep learning success stories, in particular they constituted the first Large Language Models (LLMs). However, the advent of the Transformer technology with parallelizable self-attention at its core marked the dawn of a new era, outpacing LSTMs at scale. We now raise a simple question: How far do we get in language modeling when scaling LSTMs to billions of parameters, leveraging the latest techniques from modern LLMs, but mitigating known limitations of LSTMs? Firstly, we introduce exponential gating with appropriate normalization and stabilization techniques. Secondly, we modify the LSTM memory structure, obtaining: (i) sLSTM with a scalar memory, a scalar update, and new memory mixing, (ii) mLSTM that is fully parallelizable with a matrix memory and a covariance update rule. Integrating these LSTM extensions into residual block backbones yields xLSTM blocks that are then residually stacked into xLSTM architectures. Exponential gating and modified memory structures boost xLSTM capabilities to perform favorably when compared to state-of-the-art Transformers and State Space Models, both in performance and scaling.

## 2. Why this matters for us

xLSTM is the contemporary, scaled-up incarnation of the LSTM lineage by Hochreiter's own lab, and it lands in the same architectural neighborhood as the user's program: gated recurrence as the central primitive, augmented to handle the failure modes that made vanilla LSTM uncompetitive against Transformers. The published Recurrent ViT (2502.10955) uses an LSTM-style patch-wise recurrent unit in its single feedback source; PRISM v2's slow/fast memory ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3) uses chrono-initialized gates over a fast and a slow ConvGRU; and the user's GridCell RNN ([concepts/gridcell_rnn.md](research_db/concepts/gridcell_rnn.md)) explicitly inherits LSTM gating in its spatially-independent processing stage. xLSTM's two cells — sLSTM (scalar memory with exponential gating and head-wise memory mixing) and mLSTM (matrix memory with a covariance update rule and fully parallelizable training) — are both directly relevant as drop-in candidates for the SIP stage of the GridCell RNN, and the mLSTM's matrix memory is a separate, complementary scaling strategy to PRISM v2's slow/fast timescale separation.

## 3. Key claims

1. Three concrete limitations of the original LSTM (Hochreiter & Schmidhuber 1997) bound it below Transformer scale: (i) the sigmoid-bounded input gate cannot revise an earlier storage commitment when a more important signal arrives later in the sequence; (ii) the scalar cell state $c_t \in \mathbb{R}$ is a bandwidth bottleneck (one number per "memory slot"); and (iii) the hidden-to-hidden recurrence forces sequential training, blocking the parallelism Transformers exploit.
2. **Exponential gating** with a log-domain stabilizer fixes (i). Replacing $\sigma(\cdot)$ on the input and forget gates with $\exp(\cdot)$ — combined with a running maximum stabilizer state $m_t$ to prevent overflow — restores the ability to dynamically renormalize the relative importance of old vs new content. The output gate retains a sigmoid.
3. **sLSTM (scalar LSTM)** combines exponential gating with a *new memory-mixing operation* across cells/heads within a layer. The scalar memory per cell is preserved, but the heads exchange information through a mixing matrix at every step. sLSTM is **not parallelizable** along the time axis; it retains the strict serial recurrence of the original LSTM.
4. **mLSTM (matrix LSTM)** replaces the scalar $c_t$ with a matrix memory $C_t \in \mathbb{R}^{d \times d}$ updated by a *covariance rule* $C_t = f_t\, C_{t-1} + i_t\, v_t k_t^\top$ — where $k_t, v_t$ are key and value projections of the input. Retrieval is by query: $\tilde h_t = C_t q_t / \max(|n_t^\top q_t|, 1)$ with a normalizer state $n_t = f_t n_{t-1} + i_t k_t$. The update rule contains no hidden-to-hidden mixing, so mLSTM **is fully parallelizable** at training time (computed in a Transformer-attention-style chunked / parallel form).
5. **xLSTM blocks** are residual blocks containing either an sLSTM or an mLSTM cell, plus layer normalization, causal 1D convolutions, swish nonlinearities, and learned skip connections. Two block topologies: a *post-up-projection* form (mLSTM-style, analogous to a Transformer block with up-projection inside the residual branch) and a *pre-up-projection* form (sLSTM-style, analogous to a state-space-model block). The architecture stacks these blocks residually; the notation `xLSTM[a:b]` denotes a stack with $a$ mLSTM blocks per $b$ sLSTM blocks.
6. **Empirical claim (per abstract).** Scaling xLSTM to billions of parameters yields language-modeling performance and scaling-law curves that compare favorably to state-of-the-art Transformers (Llama-style baselines) and recent linear/state-space alternatives (Mamba, RWKV, RetNet, GLA), at matched parameter and token budgets.

## 4. Methods

**Exponential gating with log-space stabilization.** For both sLSTM and mLSTM, the input and forget gates take exponential parameterizations: $i_t = \exp(\tilde i_t)$ and $f_t \in \{\sigma(\tilde f_t),\ \exp(\tilde f_t)\}$, where $\tilde i_t, \tilde f_t$ are pre-activations from learned linear projections of the input. To prevent floating-point overflow when $\tilde i_t$ or $\tilde f_t$ grow large, a stabilizer state is maintained:
$$
m_t = \max\!\bigl(\log f_t + m_{t-1},\ \log i_t\bigr),
$$
and the effective gates used in the memory update are $i'_t = \exp(\log i_t - m_t)$ and $f'_t = \exp(\log f_t + m_{t-1} - m_t)$. This is mathematically equivalent to the unstabilized exponential update but stays in the representable range of float32/bfloat16.

**sLSTM cell.** Per-cell scalar memory $c_t \in \mathbb{R}$ with update
$$
c_t = f_t\, c_{t-1} + i_t\, z_t,
$$
where $z_t = \phi(W_z x_t + R_z h_{t-1})$ is the candidate cell value (LSTM-style, with hidden-to-hidden recurrence $R_z h_{t-1}$). A normalizer state $n_t = f_t\, n_{t-1} + i_t$ provides per-cell renormalization: $h_t = o_t \cdot (c_t / n_t)$ with output gate $o_t = \sigma(W_o x_t + R_o h_{t-1})$. The "new memory mixing" is a learned mixing matrix applied across multiple heads/cells within an sLSTM layer, allowing within-layer cross-head communication that vanilla LSTM lacks. Because $R_z h_{t-1}$ and the mixing-matrix application both depend on $h_{t-1}$, sLSTM remains strictly sequential.

**mLSTM cell.** Matrix memory $C_t \in \mathbb{R}^{d \times d}$ and normalizer vector $n_t \in \mathbb{R}^d$. The input is projected into a key $k_t = W_k x_t / \sqrt{d}$, value $v_t = W_v x_t$, and query $q_t = W_q x_t$. The covariance update is
$$
C_t = f_t\, C_{t-1} + i_t\, v_t k_t^\top, \qquad n_t = f_t\, n_{t-1} + i_t\, k_t,
$$
and retrieval is
$$
\tilde h_t = \frac{C_t\, q_t}{\max\!\bigl(|n_t^\top q_t|,\ 1\bigr)}, \qquad h_t = o_t \odot \tilde h_t
$$
with $o_t = \sigma(W_o x_t)$. The update has **no hidden-to-hidden recurrence**: $k_t, v_t, q_t$ are pure functions of $x_t$, and the recurrence acts only through the $f_t C_{t-1}$ memory carry. This is the same property that makes Linear Attention (Katharopoulos 2020), RetNet, and Mamba parallelizable. mLSTM can therefore be computed in chunked / parallel form analogous to attention at training time, and in efficient sequential form at inference.

**xLSTM blocks.** Two designs:

- *Pre-up-projection block* (sLSTM): input $\to$ LayerNorm $\to$ up-projection $\to$ causal Conv1D $\to$ swish $\to$ sLSTM cell $\to$ down-projection $\to$ residual add.
- *Post-up-projection block* (mLSTM): input $\to$ LayerNorm $\to$ mLSTM cell with internal up-projection and causal Conv1D $\to$ down-projection $\to$ residual add.

These two block types correspond loosely to the Transformer-block topology (post-up) and the state-space-model topology (pre-up). An xLSTM architecture is a residual stack of these blocks, mixed in a chosen ratio (e.g., `xLSTM[7:1]` is seven mLSTM blocks per one sLSTM block).

**Training.** Standard autoregressive next-token cross-entropy on SlimPajama. Comparison baselines (Llama, Mamba, RWKV-4, RetNet, GLA, HGRN) are trained on matched token budgets and parameter counts to isolate architectural effects from scale effects.

## 5. Results

The principal empirical results (per the abstract and the paper's figures, with concrete numbers not all extractable from the binary PDF in this session) are:

- **Language modeling on SlimPajama.** xLSTM matches or beats Transformer (Llama-architecture) and modern recurrent / state-space baselines (Mamba, RWKV-4, RetNet, GLA, HGRN) on validation perplexity at matched parameter and token budgets up to the billions-of-parameters scale tested.
- **Scaling laws.** Plotted as loss-vs-compute (or loss-vs-parameters at fixed tokens), the xLSTM scaling slope is at least as favorable as the Transformer baseline and the leading SSM baselines. The paper's headline claim — "perform favorably when compared to state-of-the-art Transformers and State Space Models, both in performance and scaling" (abstract) — is supported by these scaling-law plots.
- **Synthetic associative recall.** xLSTM (specifically the mLSTM variant with its matrix memory) performs substantially better than Mamba and other constant-memory SSMs on Multi-Query Associative Recall (MQAR), where the test sequence requires retrieving many key-value pairs from a long context. The matrix memory $C_t \in \mathbb{R}^{d \times d}$ provides $O(d^2)$ retrievable slots, vs $O(d)$ for a Mamba-style scalar/vector recurrence.
- **Long Range Arena and language downstream tasks** (HellaSwag, PIQA, ARC-e, ARC-c, Winogrande, LAMBADA, etc.) report zero-shot accuracies competitive with Llama at matched parameter count, with the mLSTM-heavy configurations (e.g., xLSTM[7:1]) typically the strongest of the xLSTM variants.

The specific numerical entries in the paper's Tables and Figures are needed for direct quantitative comparison against the user's own future benchmarks; they should be re-extracted from a clean text source in a follow-up session.

## 6. Critique / limitations

**Cell-internal heuristics.** Exponential gating with a max-based log-space stabilizer is mathematically clean, but the choice between $\sigma$ and $\exp$ on the forget gate is a hyperparameter rather than a derived property. The paper does not characterize when the exponential forget gate is necessary versus harmful, and the stabilizer adds two extra state variables ($m_t$ in scalar form, plus the normalizer $n_t$) per cell.

**sLSTM is not parallelizable.** The memory-mixing operation across heads, and the hidden-to-hidden $R_z h_{t-1}$ term in the candidate computation, force sLSTM to be evaluated sequentially. Any architecture with a non-trivial fraction of sLSTM blocks pays a wall-clock penalty at training time vs a pure mLSTM (or pure Transformer) stack. xLSTM[7:1] limits this penalty to one-eighth of the blocks; xLSTM[1:1] does not.

**Matrix memory is fixed-rank.** The mLSTM matrix memory $C_t \in \mathbb{R}^{d \times d}$ provides $d^2$ scalar slots, which is large but finite. Information older than what fits in this rank-$d$ representation is eventually overwritten by the forget gate. This is the same intrinsic limit as Linear Attention / RetNet / Mamba — the constant memory budget is a feature for inference, but a hard ceiling for tasks with very long-range exact-recall requirements. Quadratic-attention Transformers, with their full $O(L^2)$ access pattern, retain an advantage when exact recall over a very long context is needed (modulo their own scaling issues).

**Comparison fairness.** As with most recent "we beat Transformers" papers, the comparison baselines are trained by the authors at the budgets and configurations they choose. The headline scaling-law claim is at the scales tested (up to a few billion parameters); whether the favorable comparison persists at frontier scale (10s–100s of billions of parameters, trillions of tokens) is not addressed in this paper.

**No biological-plausibility claim.** Unlike the user's program, xLSTM is engineering rather than NeuroAI. The covariance update rule has a clear interpretation as outer-product associative storage (Schlag et al. 2021's Fast Weight Programmers; Hopfield-style associative memory), but the paper does not engage with the cortical-microcircuit, predictive-coding, or working-memory literatures.

**No spatial structure.** xLSTM is a sequence model. The matrix memory is unstructured; there is no explicit grid-structured / spatial inductive bias of the kind the user's GridCell RNN imposes ([concepts/gridcell_rnn.md](research_db/concepts/gridcell_rnn.md)). Applying mLSTM to vision tasks (xLSTM has been extended to vision in follow-up work) requires the architecture to either flatten spatial structure or impose it via convolutional projections at the periphery.

## 7. Connection to our work

xLSTM is the *recurrent-architecture contemporary* of the user's program: both make the bet that gated recurrence — not quadratic self-attention — is the right central primitive, and both invest in scaling it to be competitive with Transformers. The architectural commitments overlap substantially, but the user's program goes further along the structural-inductive-bias axis while xLSTM goes further along the pure-scale axis.

**Drop-in cell for the GridCell RNN's SIP stage.** The GridCell RNN ([concepts/gridcell_rnn.md](research_db/concepts/gridcell_rnn.md)) has two stages per timestep: spatially-independent processing (SIP) of each grid cell's hidden state, followed by Feedback-Transformer-mediated communication across cells. The SIP stage is described in the user's notes as LSTM-style. Either xLSTM cell is a candidate replacement:

- **mLSTM in SIP** would give each grid cell a $d \times d$ matrix memory accessed by query-key-value within that cell. This is appealing because the matrix memory's $O(d^2)$ retrievable slots per cell would let a single grid cell maintain a richer per-location working set than a scalar/vector LSTM. The parallelizability of mLSTM along the time axis is also operationally convenient if the GridCell RNN is unrolled over many recurrent passes per image (the user's $n_{FR}$ forward-reasoning steps; [threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §4).

- **sLSTM in SIP** offers the cross-head memory mixing operation, which in the SIP context would mix across the channel dimension within each grid cell. This is less aligned with the user's design — the grid-vs-channel split in the GridCell RNN already separates within-cell channel processing from across-cell communication — but the exponential gating with stabilizer would still be a clean upgrade over vanilla LSTM gating.

**Complementarity with PRISM v2's slow/fast structure.** PRISM v2 scales recurrence in the *temporal* direction: chrono-init biases ($b_u^{\text{fast}} = -1$, $b_u^{\text{slow}} = -3$; [PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3) produce a fast memory updating ~27% per step and a slow memory updating ~5% per step. xLSTM scales recurrence in the *representational* direction: the matrix memory $C_t \in \mathbb{R}^{d \times d}$ stores associations rather than slow-varying scalars. The two are orthogonal commitments. A PRISM-v2 variant that replaced the slow ConvGRU with a slow mLSTM (slow forget-gate bias, matrix memory, key-value retrieval) would combine both — chrono-slow timescale separation *and* matrix-capacity scaling — and is a natural future-work direction.

**The covariance update and the Feedback Transformer.** The mLSTM update $C_t = f_t C_{t-1} + i_t v_t k_t^\top$ is structurally an outer-product associative memory, which is the same family as the Fast Weight Programmers (Schmidhuber 1992; Schlag et al. 2021) and modern Hopfield networks (Ramsauer et al. 2020). The Feedback Transformer ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §1) is, in the framing of this literature, a *static* outer-product over an attention context. Plugging an mLSTM matrix memory into the Feedback Transformer's communication step would let recurrence-via-association be the substrate for cross-coalition communication — a concrete architectural unification the user's program does not currently specify.

**Where xLSTM is a strict competitor.** On the empirical question of language modeling at scale, xLSTM is a closer competitor to a "pure Transformer" stack than the user's program is, because xLSTM has no architectural commitment to the spatial / multi-compartmental / cortex-like structure the user requires. If the bitter-lesson reading prevails ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §6 critique of PRISM), xLSTM is the architecture the user's program must justify itself against — "we add structural inductive biases on top of gated recurrence, and the biases earn their keep on tasks where structure matters."

**Where xLSTM is a strict ally.** On the architectural question of what cell to put inside the user's recurrence primitive, xLSTM (especially mLSTM) is a natural upgrade path over vanilla LSTM. The exponential-gating stabilization trick and the matrix-memory retrieval rule are both modular: they can be adopted into the SIP stage of the GridCell RNN, or into PRISM v2's slow memory, without disturbing the rest of the architectural program.

## 8. Citations to follow

- `hochreiter_schmidhuber1997_lstm` — the foundational LSTM paper. Already in seed (status to verify).
- `schlag_irie_schmidhuber2021_fast_weight_programmers` — Fast Weight Programmers / Linear Transformers as outer-product associative memory. Direct ancestor of mLSTM's covariance update. *Add to seed.*
- `katharopoulos2020_linear_transformers` — Linear Attention via kernel feature maps; the parallelizability trick mLSTM uses. *Add to seed.*
- `gu_dao2023_mamba` — Mamba / selective state-space models. The principal alternative scaling strategy xLSTM benchmarks against. *Add to seed.*
- `peng2023_rwkv` — RWKV linear-attention recurrent architecture. Benchmark baseline. *Add to seed.*
- `sun2023_retnet` — RetNet retentive networks. Benchmark baseline. *Add to seed.*
- `yang2023_gated_linear_attention` — Gated Linear Attention (GLA). Benchmark baseline. *Add to seed.*
- `qin2023_hgrn` — Hierarchically Gated Recurrent Network (HGRN). Benchmark baseline; close architectural relative. *Add to seed.*
- `ramsauer2020_modern_hopfield` — modern Hopfield networks with exponential storage; conceptual cousin of the matrix-memory retrieval rule. *Add to seed.*
- `mujika2017_fast_slow_rnn` — fast-slow RNN; the slow/fast timescale separation PRISM v2 uses. Already in seed.
- `tallec_ollivier2018_chrono_init` — chrono initialization of LSTM gate biases. Already in seed.
- `jozefowicz2015_rnn_exploration` — empirical exploration of LSTM/GRU variants; predecessor to xLSTM's gating ablations. Already in seed.
