---
id: hochreiter_schmidhuber1997_lstm
title: "Long short-term memory"
authors:
  - "Hochreiter, Sepp"
  - "Schmidhuber, Jürgen"
year: 1997
venue: "Neural Computation"
doi: "10.1162/neco.1997.9.8.1735"
arxiv: ""
url: "https://www.bioinf.jku.at/publications/older/2604.pdf"
tags:
  - recurrent-networks
  - deep-learning
  - methodology
concepts:
  - lstm-cell
  - error-gated-update
  - multiplicative-feedback
  - gain-modulation
  - gridcell-rnn
  - multi-compartmental-memory
related:
  - beck2024_xlstm
  - mujika2017_fast_slow_rnn
  - tallec_ollivier2018_chrono_init
  - jozefowicz2015_rnn_exploration
  - vaswani2017_attention
  - schmidhuber2015_learn_to_think
  - wang2025_hierarchical_reasoning_model
  - cho2014_gru
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_40
status: full
depth: full
last_updated: "2026-05-16"
---

# Long short-term memory

## 1. Abstract

Learning to store information over extended time intervals via recurrent backpropagation takes a very long time, mostly due to insufficient, decaying error back-flow. The paper briefly reviews Hochreiter's 1991 analysis of this problem and then addresses it by introducing a novel, efficient, gradient-based method called Long Short-Term Memory (LSTM). By truncating the gradient where this does not do harm, LSTM can learn to bridge minimal time lags in excess of 1000 discrete time steps by enforcing *constant* error flow through "constant error carrousels" (CECs) within special units. Multiplicative gate units learn to open and close access to the constant error flow. LSTM is local in space and time; its computational complexity per time step and weight is $O(1)$. In experiments with artificial data involving local, distributed, real-valued, and noisy pattern representations, LSTM is compared with RTRL, BPTT, Recurrent Cascade-Correlation, Elman nets, and Neural Sequence Chunking — LSTM leads to many more successful runs, learns much faster, and solves complex artificial long-time-lag tasks that have never been solved by previous recurrent network algorithms.

## 2. Why this matters for us

LSTM is the foundational recurrent-state primitive on which the entire architectural program rests. The published Recurrent ViT (arXiv:2502.10955) uses an LSTM as its recurrent state. PRISM v1 uses a ConvGRU — a direct descendant — and PRISM v2 reinstates LSTM-style gating with chrono-initialized biases (`PRISM_V2_PROPOSAL.md` §3.3). The GridCell RNN primitive (`concepts/gridcell_rnn.md`) commits to LSTM-style gated updates in its Stage-1 spatially-independent-processing (SIP) step. The Hierarchical Reasoning Model's H and L modules and the slow/fast memory in PRISM v2 inherit LSTM's gated-recurrence and constant-error-carousel commitments. Everything downstream of "we need a recurrent state that bridges long time lags without vanishing gradients" cites this paper as the substrate.

## 3. Key claims

1. Standard BPTT/RTRL error signals propagating $q$ steps back through a recurrent network are scaled by a product of $q$ Jacobian factors $\prod_m f'_{l_m}(\text{net}_{l_m}) w_{l_m l_{m-1}}$, which either explode or vanish exponentially in $q$ — the long-time-lag problem.
2. A self-recurrent linear unit with a fixed unit weight on its self-loop ($f_j(x) = x$, $w_{jj} = 1$) yields *constant* error flow through time. This is the Constant Error Carousel (CEC), the load-bearing element of LSTM.
3. Naively used, the CEC suffers from input-weight conflict (the same incoming weight has to both store and ignore inputs at different times) and output-weight conflict (the same outgoing weight has to both retrieve and protect-from-perturbation at different times). These conflicts make gradient learning intractable.
4. Multiplicative *input* and *output* gate units — sigmoid units that scale the input to and output from the CEC — resolve both conflicts by learning *when* to write and *when* to read, decoupling the gating decision from the stored content. The resulting unit is the LSTM memory cell.
5. With gradient truncation at memory-cell boundaries (errors do not leak out of $\text{net}_{c_j}, \text{net}_{in_j}, \text{net}_{out_j}$ back through time), LSTM has $O(1)$ update complexity per weight per time step — matching BPTT and beating RTRL's $O(W^2)$ — while preserving exact constant error flow inside the CEC.
6. Empirically, LSTM solves long-time-lag artificial tasks (embedded Reber grammar; noise-free and noisy sequences with up to 1000-step minimal lags; the 2-sequence problem; real-valued continuous-input tasks; temporal-order tasks) that RTRL, BPTT, Elman nets, Recurrent Cascade-Correlation, and Neural Sequence Chunker fail or solve only orders of magnitude more slowly.

## 4. Methods

**The CEC.** A single self-recurrent linear unit $j$ with identity activation $f_j(x) = x$ and self-weight $w_{jj} = 1$ has local backpropagated error $\vartheta_j(t) = f'_j(\text{net}_j(t))\,\vartheta_j(t+1)\,w_{jj} = \vartheta_j(t+1)$, i.e. the error flows backward in time unattenuated. This is the constant error carousel.

**The memory cell.** Wrap the CEC with two multiplicative gate units. The $j$-th memory cell $c_j$ has:

- An internal state $s_{c_j}$ updated by $s_{c_j}(0) = 0$ and $s_{c_j}(t) = s_{c_j}(t-1) + y^{in_j}(t)\, g(\text{net}_{c_j}(t))$, where $g$ is a squashing function (logistic sigmoid scaled to $[-2, 2]$).
- An input gate $in_j$ with logistic-sigmoid activation $y^{in_j}(t) = f_{in_j}(\text{net}_{in_j}(t)) \in [0, 1]$ multiplying the squashed cell input — controlling write access.
- An output gate $out_j$ with activation $y^{out_j}(t) \in [0, 1]$ multiplying the cell output: $y^{c_j}(t) = y^{out_j}(t)\, h(s_{c_j}(t))$, where $h$ squashes to $[-1, 1]$ — controlling read access.

Crucially: in the 1997 paper there is **no forget gate**. The internal state is a pure additive accumulator with self-weight exactly 1. The forget gate is a 2000 extension (Gers, Schmidhuber & Cummins).

**Memory-cell blocks.** $S$ memory cells sharing the same pair of input/output gates form a block of size $S$. Block-internal cells share gating decisions, encouraging distributed representations within a block.

**Network topology.** One input layer, one hidden layer containing memory-cell blocks (and optionally conventional units), one output layer. All non-gate units in the hidden layer feed all higher layers. Gate units are biased — output gates are initialized with negative bias (e.g., $-1, -2, -3$) so initial cells start "off" and get sequentially recruited (the "abuse problem" mitigation).

**Learning.** A hybrid of RTRL (for memory-cell internal-state derivatives, which need to persist across the long-time-lag horizon) and truncated BPTT (for everything else). Errors entering a memory cell at its output get scaled by output-gate activation and $h'$, then circulate inside the CEC untouched until they leave through the input gate (where they are scaled by input-gate activation and $g'$) and propagate one step further. Errors are truncated at the gate net-inputs $\text{net}_{in_j}, \text{net}_{out_j}, \text{net}_{c_j}$ — they do not propagate back further in time through these signals, only through the internal state $s_{c_j}$.

**Computational cost.** Update complexity per time step is $O(KH + KCS + CSI + HI) = O(W)$ where $K$ is output count, $C$ is block count, $S$ is block size, $H$ is hidden count, $I$ is fan-in. This matches BPTT for fully recurrent nets and beats RTRL's $O(W^2)$. LSTM is *local in both space and time*: per-step storage is bounded independent of sequence length.

## 5. Results

**Experiment 1 (Embedded Reber Grammar).** A non-long-lag benchmark used to show LSTM is competitive on short-lag tasks. With 3–4 memory-cell blocks of size 1–2 (264–276 weights) and learning rates 0.1–0.5, LSTM succeeds on 97–100% of trials versus 0% for Elman nets (15 hidden units, ~435 weights), 50% for Recurrent Cascade-Correlation, and only "some fraction" for RTRL. LSTM converges in 8,440–39,740 sequence presentations; RTRL takes 25,000–173,000 on its successful subset; ELM exceeds 200,000 with no success.

**Experiment 2a (noise-free long lags).** With minimal lag $p = 100$ and a 2-element vocabulary, RTRL achieves 0% success after 5,000,000 sequences; BPTT 0%; Neural Sequence Chunker 33% after 32,400 sequences; LSTM 100% after 5,040 sequences. At $p = 4$, RTRL succeeds on a fraction of trials in $\sim 10^6$ steps; at $p = 10$, RTRL and BPTT already collapse to 0% success.

**Experiment 2c (very long lags + distractors, no local regularities).** With minimal lag $q + 1$ where $q \in \{50, 100, 200, 500, 1000\}$ and a vocabulary of $p + 4$ symbols where $p \in \{50, \ldots, 1000\}$ acts as distractors, LSTM with 2 memory cells (size-1 blocks) succeeds with training-sequence counts that grow *very slowly* with $q$: 30,000 for $q = 50$, 31,000 for $q = 100$, 49,000 for $q = 1000$. No other recurrent algorithm in the comparison set can solve this regime at all. This is the load-bearing demonstration that CEC plus gating enables time-lag scaling that vanilla RNNs categorically cannot reach.

**Experiments 3, 4, 5, 6.** LSTM additionally solves: the 2-sequence problem with real-valued conditional-expectation targets (3c); distributed continuous-valued representations requiring precise long-term storage (4, 5); and temporal-order-of-widely-separated-inputs tasks (6). Across all of these, no other recurrent net algorithm of the era achieves any success.

## 6. Critique / limitations

The paper itself names two principal limitations.

**Strongly delayed XOR.** Truncated LSTM cannot solve problems like XOR of two widely separated inputs in a noisy sequence, because the task is *non-decomposable* — there is no incremental subgoal that reduces expected error. The authors note that full (non-truncated) gradient would not help in practice because outside the CECs error flow vanishes quickly anyway, so the limitation is fundamental to gradient-based learning, not an artifact of truncation.

**Counting time steps.** All gradient-based methods, including LSTM, lack a precise discrete-time-step counting mechanism. Distinguishing 99 from 100 steps requires an auxiliary counting mechanism; coarse distinctions (3 vs 11 steps) work fine.

**Beyond the paper's self-critique.** Three further limitations have emerged in retrospect:

- *Missing forget gate.* The 1997 cell has $s_{c_j}(t) = s_{c_j}(t-1) + \ldots$ with self-weight exactly 1 and no decay. On sequences where the cell should *erase* stored content, the model relies on input-gate-driven additive cancellation, which is hard to learn. Gers, Schmidhuber & Cummins (2000) added the forget gate, replacing the unit self-weight with a learned gate $f_t \in [0, 1]$. The "LSTM" used everywhere downstream (including in 2502.10955, PRISM, and the user's program) is the post-2000 variant. Jozefowicz et al. (2015) empirically show that the forget-gate bias is the single most impactful hyperparameter.
- *Output gate may be unnecessary.* The paper itself notes (Experiments 2a/2b) that input gates alone suffice for local-output-encoding tasks. Subsequent simplifications — GRU (Cho 2014), Peephole-LSTM (Gers & Schmidhuber 2000) — have shown that the LSTM cell is overparameterized for many tasks.
- *Bias initialization is load-bearing.* The paper hides the importance of negative output-gate-bias initialization in implementation details; downstream work (Tallec & Ollivier 2018 chrono-init; Gers et al. 2000 forget-bias-1 initialization) made this explicit, showing that the timescale of memory is controlled directly by the gate-bias distribution.

The paper's experiments are entirely on *artificial* sequence tasks. The actual significance of LSTM for real data (speech, language, machine translation) was established by Graves & Schmidhuber (2005, 2009) and Sutskever, Vinyals & Le (2014). The 1997 paper proves the architecture works in principle; the empirical case for scaling came a decade later.

## 7. Connection to our work

LSTM is the recurrent-state primitive on which the entire architectural program is built. The connection is dense enough to warrant a per-component breakdown.

**Recurrent ViT (`2502.10955`).** The recurrent state $H_t$ is an LSTM. Concretely, the patch-wise LSTM described in the published paper's §6 implements eq. (9) of the appendix — internal state additively accumulates a gated candidate, with input and output gates controlling read/write. The "tokens / additive / multiplicative feedback" variants from §6.7 of 2502.10955 are three ways of injecting the LSTM hidden state back into the self-attention computation. The constant-error-carousel commitment is what makes per-patch LSTM trainable across the 10–20 recurrent passes the user reports doing on Food-101 — without CEC, backprop through 20 passes would either explode or vanish before the gradient reaches the first pass.

**PRISM v1.** The convolutional GRU in `Prism/memory.py` is a strict simplification of LSTM: the output gate is removed, the forget and input gates are tied ($f_t = 1 - i_t$), and the cell-state/hidden-state distinction is collapsed. The gradient-flow advantage of LSTM's CEC carries over to GRU's gated additive update. PRISM v1 chose the simpler unit because the channel dimension is large and the parameter savings matter; the architectural inheritance from this paper is intact.

**PRISM v2.** The slow/fast dual memory (`PRISM_V2_PROPOSAL.md` §3.3) uses LSTM-style gating with chrono-initialized forget-gate biases. The fast memory's forget bias is initialized so its effective timescale is $\sim 5$ steps; the slow memory's is $\sim 100$ steps. Both rest on the same CEC architecture introduced here. The "memory-compute" variant in `concepts/gridcell_rnn.md` further generalizes the LSTM gating to grid-structured states with Feedback-Transformer integration (Stage 2) layered on top of LSTM-style SIP (Stage 1).

**GridCell RNN.** Stage 1 of the GridCell RNN is literally a per-cell LSTM update — eq. (9) of this paper's appendix A.1, applied independently at each cell of the spatial grid. Stage 2 (Feedback Transformer integration) then communicates across cells. The clean decomposition into "LSTM does within-cell time, FT does across-cell space" is what allows the architecture to scale without combinatorial blowup; both halves rest on the constant-error-flow guarantee LSTM provides.

**HRM (Wang 2025) integration in the program.** The user explicitly cites HRM as the inspiration for the "diminishing feedback into deeper layers" design (the_user_architectural_program §3). HRM's H and L modules are LSTM cells running at different update rates. The hierarchical-convergence and one-step-implicit-gradient mechanisms HRM uses to avoid BPTT through the inner loop are *specifically* enabled by LSTM's CEC: the inner-loop equilibrium is well-defined only because the L-module's gradient does not explode or vanish over many inner steps.

**Feedback Transformer.** Even though the Feedback Transformer is an attention primitive, the recurrent states $C_i$ that it integrates as side-channel Q/K/V projections are typically LSTM hidden states. The "twelve feedback sources" the user reports successfully integrating in the Video VAE work are twelve LSTM-style recurrent units. Without CEC-based gradient flow, training a single self-attention layer with twelve feedback sources would be hopeless — the joint backward pass would multiply twelve gradient streams, each subject to its own vanishing/exploding pathology.

**The deeper point.** What LSTM contributes to the user's program is not a specific architecture but a *guarantee*: gated additive recurrence with self-weight 1 (or near-1) gives a Jacobian eigenvalue at 1, so error flow neither explodes nor decays through the recurrent loop. Every subsequent memory primitive in the program — GRU, ConvGRU, peephole, chrono-init, xLSTM, HRM-style H/L — is a perturbation around this guarantee. The user's commitment to multi-compartmental, hierarchical, bidirectionally-connected memory is structurally a multi-LSTM commitment: many CECs running in parallel at different timescales and spatial resolutions, with the gates carrying the burden of *when* and *what* to communicate. This paper supplied the unit.

## 8. Citations to follow

- `gers_schmidhuber_cummins2000_forget_gate` — adds the forget gate; the "real" LSTM used everywhere downstream. Not yet in seed; high priority.
- `gers_schmidhuber2000_peephole` — peephole connections from CEC to gates; partial relevance to the program. Not yet in seed.
- `cho2014_gru` — gated recurrent unit; the simplification PRISM v1 actually uses. In seed, full depth; high priority.
- `graves_schmidhuber2005_bidirectional_lstm` — the first major real-data demonstration of LSTM. Not yet in seed.
- `tallec_ollivier2018_chrono_init` — chrono-initialization of LSTM gate biases; load-bearing for PRISM v2 slow/fast memory.
- `mujika2017_fast_slow_rnn` — dual-timescale recurrence; cited in PRISM v2.
- `jozefowicz2015_rnn_exploration` — empirical study showing forget-gate bias is the dominant hyperparameter; calibrates the user's intuitions about LSTM hyperparameters.
- `beck2024_xlstm` — modern revival with exponential gating and matrix memory; the "what if we redesigned LSTM in 2024" reference point.
- `hochreiter1991_diploma_thesis` — Hochreiter's 1991 vanishing-gradient analysis cited in §3.1; the prequel. Not in seed; consider for historical context.
- `bengio1994_long_term_dependencies` — the contemporary alternative analysis of the long-time-lag problem. Not yet in seed.
