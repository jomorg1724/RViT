---
id: wang2025_hierarchical_reasoning_model
title: "Hierarchical Reasoning Model"
authors:
  - "Wang, Guan"
  - "Li, Jin"
  - "Sun, Yuhao"
  - "Chen, Xing"
  - "Liu, Changling"
  - "Wu, Yue"
  - "Lu, Meng"
  - "Song, Sen"
  - "Abbasi Yadkori, Yasin"
year: 2025
venue: "arXiv:2506.21734"
doi: ""
arxiv: "2506.21734"
url: "https://arxiv.org/abs/2506.21734"
tags:
  - deep-learning
  - recurrent-networks
  - theoretical-essay
concepts:
  - slow-fast-recurrence
  - parallel-recurrent-units
  - hierarchical-reasoning-model
  - chrono-initialization
  - hierarchical-convergence
  - one-step-implicit-gradient
  - deep-supervision-detached-segments
  - adaptive-computation-time
  - system-1-vs-system-2
  - coupled-rnn-world-models
related:
  - mujika2017_fast_slow_rnn
  - tallec_ollivier2018_chrono_init
  - schmidhuber2015_learn_to_think
  - mante2013_context_dependent_pfc
  - bardes2023_vjepa
  - constantinidis2018_persistent_activity
  - banino2021_pondernet
  - graves2016_act
  - bai_kolter_koltun2019_deep_equilibrium_models
  - buzsaki_wang2012_gamma
  - funahashi1989_mnemonic_dlpfc
  - goldman_rakic1995_cellular_wm
relevance_to:
  - prism_v2
  - recurrent_vit
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# Hierarchical Reasoning Model

> **Sourcing note (revised 2026-05-13).** This entry has been verified against the actual arXiv PDF of v3 (4 Aug 2025) of the paper. The previous sourcing caveat — that the entry was written from prior knowledge — no longer applies. Equations, algorithmic details, and benchmark numbers below are sourced directly from the PDF.

## 1. Abstract

The Hierarchical Reasoning Model (HRM) is a recurrent architecture inspired by hierarchical and multi-timescale processing in the human brain. It attains "significant computational depth while maintaining both training stability and efficiency," executing sequential reasoning tasks in a single forward pass without explicit supervision of the intermediate process. HRM consists of two interdependent recurrent modules: a high-level (H) module responsible for slow, abstract planning, and a low-level (L) module handling rapid, detailed computations. With only 27M parameters and 1000 training samples per task, HRM achieves near-perfect performance on complex Sudoku puzzles and optimal path finding in large mazes, and outperforms much larger Chain-of-Thought models on the Abstraction and Reasoning Corpus (ARC-AGI). The authors position HRM as evidence that brain-inspired architectural commitments — hierarchical processing, temporal separation between modules, and recurrent connectivity — can substitute for both pretraining and CoT prompting on reasoning benchmarks.

## 2. Why this matters for us

HRM is the contemporary published model that most cleanly instantiates the slow/fast memory architecture PRISM v2 commits to ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3) and the diminishing-feedback-into-deeper-layers design from the user's Evolution of Architecture document ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §3). The user cites HRM explicitly as the rationale for v2's design choice that deeper memory layers should have fewer feedback inputs and run on slower timescales than shallower layers. The verified PDF reveals a *specific* coupling mechanism (the L module repeatedly converges to a local equilibrium, then the H module performs one update and resets L) — the "hierarchical convergence" mechanism. This is more than a fast-slow timescale separation; it is a deliberate architectural commitment to *nested fixed-point computation*, which has direct implications for what PRISM v2's slow memory should look like. HRM also adopts a one-step implicit-gradient training scheme (Deep Equilibrium Model framing) that the user's program does not currently use but should consider.

## 3. Key claims

1. Standard transformer architectures, including those augmented with chain-of-thought (CoT), are computationally shallow ($AC^0$ / $TC^0$ complexity classes) and brittle on reasoning tasks that require polynomial-time deliberation. CoT externalizes reasoning into token-level language, which is brittle, data-hungry, and slow.
2. Latent reasoning in the hidden state — analogous to how the brain reasons in a latent space without constant translation to language — is a more efficient substrate for reasoning. The constraint is *effective computational depth*: naive stacking suffers vanishing gradients, and standard RNNs converge too quickly to a fixed point and stall.
3. **Architectural solution: hierarchical convergence.** HRM has four learnable components — an input network $f_I$, a low-level recurrent module $f_L$, a high-level recurrent module $f_H$, and an output network $f_O$. Dynamics unfold over $N$ high-level cycles of $T$ low-level timesteps each. The L module updates every step; the H module updates only every $T$ steps. Crucially, the L module converges to a local equilibrium within each cycle (conditioned on the current $z_H$), and then the H module performs one update, "resetting" the L computation for a new equilibrium phase. The effective computational depth is $NT$ steps.
4. **Training via one-step implicit gradient.** Inspired by Deep Equilibrium Models (DEQ), the authors approximate the BPTT gradient by backpropagating only through the final-state Jacobian at the converged fixed point: $\partial z_H^* / \partial \theta \approx (\partial f_H / \partial \theta)|_{z_H^*}$, plus a similar approximation for L. Memory footprint is $O(1)$ rather than BPTT's $O(T)$. The gradient pathway is "output head → final state of the H module → final state of the L module → input embedding."
5. **Deep supervision with detached segments.** Training runs $M$ segments per sample. After each segment, the state $z^m$ is detached from the computation graph before being used as initial state for $z^{m+1}$. Gradients flow only one segment back, providing more frequent feedback to the H module and acting as a regularizer.
6. **Adaptive computational time (ACT).** A Q-learning head on top of the final H-state predicts halt vs continue actions, with reward = prediction correctness on halt. The maximum number of segments $M_{\max}$ is a hyperparameter; the minimum $M_{\min}$ is sampled stochastically to encourage longer "thinking" sometimes. At inference, increasing $M_{\max}$ trades extra compute for more deliberate reasoning — an inference-time scaling knob without retraining.
7. **Empirical performance.** With ≈27M parameters trained on ~1000 input-output examples per task from scratch (no pretraining, no CoT data): on ARC-AGI-1, HRM achieves 40.3%, surpassing o3-mini-high (34.5%) and Claude 3.7 with 8K context (21.2%); on ARC-AGI-2, HRM achieves 5.0% vs o3-mini-high 3.0% and Claude 3.7 8K 1.3%; on Sudoku-Extreme-Full (a tree-search puzzle) and Maze-Hard 30×30, HRM achieves near-perfect accuracy where CoT models score 0%. Maze-Hard bar chart: HRM 74.5%.

## 4. Methods

**Architecture.** HRM operates on input $x$ projected by the input network $\tilde x = f_I(x; \theta_I)$. The total number of timesteps in one forward pass is $N \times T$, indexed $i = 1, \dots, NT$. Both modules maintain hidden states $z_L^i$ and $z_H^i$, initialized from learned vectors $z_L^0, z_H^0$. The recurrence rules are

$$
z_L^i = f_L(z_L^{i-1}, z_H^{i-1}, \tilde x; \theta_L)
$$
$$
z_H^i = \begin{cases} f_H(z_H^{i-1}, z_L^{i-1}; \theta_H) & \text{if } i \equiv 0 \pmod{T} \\ z_H^{i-1} & \text{otherwise} \end{cases}
$$

The output prediction is $\hat y = f_O(z_H^{NT}; \theta_O)$.

**Hierarchical convergence.** Standard RNNs converge too early; gradients vanish and effective depth caps out. HRM avoids this by resetting the L module each time H updates. During each high-level cycle $k$, the L module repeatedly applies $z_L^i = f_L(z_L^{i-1}, z_H^{k-1}, \tilde x; \theta_L)$ until it converges to a fixed point $z_L^* = f_L(z_L^*, z_H^{k-1}, \tilde x; \theta_L)$ conditioned on the current $z_H^{k-1}$. The H module then updates once: $z_H^k = f_H(z_H^{k-1}, z_L^*; \theta_H)$. This new $z_H^k$ supplies a fresh context that "restarts" the L computation toward a new equilibrium. Empirically (Figure 3 of the PDF), the L module shows residual spikes between cycles and the H module shows smooth convergence — the qualitative signature of nested fixed-point computation.

**One-step implicit gradient.** Treating each L cycle as a fixed-point iteration of $z_L^*$ and the full H update as a fixed point of $\mathcal{F}(z_H; \theta) = f_H(z_H, z_L^*(z_H); \theta)$, the authors invoke the Implicit Function Theorem to compute $\partial z_H^* / \partial \theta = (I - J_\mathcal{F})^{-1} \partial \mathcal{F} / \partial \theta$. Approximating $(I - J_\mathcal{F})^{-1} \approx I$ (one-step Neumann series), the gradient reduces to

$$
\frac{\partial z_H^*}{\partial \theta_H} \approx \frac{\partial f_H}{\partial \theta_H}, \qquad \frac{\partial z_H^*}{\partial \theta_L} \approx \frac{\partial f_H}{\partial z_L^*} \frac{\partial z_L^*}{\partial \theta_L}, \qquad \frac{\partial z_L^*}{\partial \theta_L} \approx \frac{\partial f_L}{\partial \theta_L}.
$$

The gradient pathway is output head → H final state → L final state → input embedding, with each module backproped only through its own most recent application. $O(1)$ memory, no BPTT unrolling. The authors note this aligns with the perspective that cortical credit assignment relies on short-range, temporally local mechanisms (citing Whittington & Bogacz 2019 and similar work).

**Deep supervision with detached segments.** Training runs $M$ segments per sample. For segment $m \in \{1, \dots, M\}$ with state $z^{m-1}$, compute $(z^m, \hat y^m) = \text{HRM}(z^{m-1}, x; \theta)$, the loss $\mathcal{L}^m = \text{Loss}(\hat y^m, y)$, and step the optimizer. The state $z^m$ is *detached* from the graph before being used as initial state for the next segment, so gradients from segment $m+1$ do not propagate back through segment $m$. This is a 1-step approximation of the gradient of the recursive deep-supervision process.

**Adaptive computational time (ACT).** A Q-head $\hat Q^m = \sigma(\theta_Q^\top z_H^{mNT})$ predicts (halt, continue) Q-values at each segment. The MDP reward is $\mathbf{1}\{\hat y^m = y\}$ on halt, 0 on continue. Halt is selected if $\hat Q_{\text{halt}} > \hat Q_{\text{continue}}$ and the segment count exceeds $M_{\min}$, or if it reaches $M_{\max}$. The loss combines task loss and Q-learning loss: $\mathcal{L}_{\text{ACT}}^m = \text{Loss}(\hat y^m, y) + \text{BCE}(\hat Q^m, \hat G^m)$.

**Inference-time scaling.** Setting $M_{\max}$ at inference larger than at training increases compute and improves performance on tasks requiring more deliberation (e.g., Sudoku). On ARC, additional compute helps less because solutions are typically short.

## 5. Results

Verified from the PDF:

| Benchmark | HRM (27M, 1K samples) | o3-mini-high | Claude 3.7 (8K) | Notes |
|---|---|---|---|---|
| ARC-AGI-1 (960 train) | **40.3%** | 34.5% | 21.2% | Direct-pred baseline 15.8% |
| ARC-AGI-2 (1120 train) | **5.0%** | 3.0% | 1.3% | Direct-pred baseline 0.9% |
| Sudoku-Extreme 9×9 | near-perfect (~55%+ from bar chart, "near-perfect" in text) | 0% | 0% | CoT methods completely fail |
| Maze-Hard 30×30 | **74.5%** | 0% | 0% | CoT methods completely fail |

**Architectural depth scaling.** On Sudoku-Extreme-Full, increasing transformer *width* (8 layers fixed, hidden sizes from 27M to 872M params) yields *no* performance gain. Increasing depth (512 hidden fixed, 8 → 256 layers) saturates at ≈75% for a standard Transformer and ≈75% for a recurrent Transformer; HRM reaches ≈95%+ with the same depth budget.

**Hierarchical convergence signature.** PCA trajectories show: HRM L-module trajectories cycle within local equilibria; HRM H-module trajectory is smooth monotone descent in forward residual; standard RNN converges and then sits still (no further useful computation); deep network has residuals dominated by the first and last few layers (vanishing-gradient signature).

**Inference-time scaling.** On Sudoku, increasing $M_{\max}$ at inference improves accuracy. On ARC-AGI, additional compute yields minimal further gains.

## 6. Critique / limitations

The model is evaluated on tasks with very specific structure (Sudoku, mazes, ARC-AGI). All three are essentially symbolic-search problems with deterministic objective solutions. The framing of these as "reasoning" benchmarks is the authors' choice; performance on more natural reasoning (mathematical word problems, scientific question answering, code generation) is not reported, and the architecture's translatability is not yet demonstrated.

The "no pretraining, no CoT data" framing is striking but contextual: HRM is trained directly on the target task's input-output pairs, while LLMs are evaluated zero-shot or few-shot on the same tasks. The comparison is informative but is not strictly apples-to-apples — the LLMs have a vastly broader prior; HRM has a task-specific architecture. The implication "this is a paradigm shift away from scaling" requires HRM-style models to be shown to generalize across many tasks, not just dominate within one.

The one-step gradient approximation rests on the L module having actually converged to a fixed point within $T$ steps. The paper shows this empirically (residual spikes settling within each cycle) but does not characterize when it would fail. If $T$ is too small, the approximation is poor and learning may degrade.

The Q-learning halting head is somewhat heuristic. The reward signal is binary on halt and 0 on continue, with bootstrap from the continue action's max Q. The convergence properties of this Q-head training are not fully characterized; in principle Q-learning with non-stationary value functions (since the underlying network is being trained simultaneously) can be unstable.

The architectural commitments — two modules, fixed timescale ratio $T$ — are simpler than what the user's program calls for. The user wants three (or more) memory levels with smoothly varying timescales and conv-based descending/ascending projections handling the spatial-shape mismatch between layers ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §3). HRM's two-module choice is therefore a special case of a more general design space.

The biological grounding is suggestive but partial. Footnote 2 of the paper explicitly states that the H and L modules are "conceptual abstractions and do not map directly to specific neural oscillation frequencies." The 4–8 Hz theta vs 30–100 Hz gamma motivation is presented as inspiration, not derivation. The connection to PFC slow dynamics (Goldman-Rakic, Constantinidis) is similarly inspirational rather than precise.

The model uses transformer attention internally (the figure on page 6 shows transformer-like blocks); the fact that HRM beats Transformer baselines is therefore not "RNN beats Transformer" but "two transformer-based modules with hierarchical fixed-point dynamics beat a single transformer." The architectural contribution is the *coupling structure*, not a return to pure recurrence.

## 7. Connection to our work

HRM is the closest contemporary published architecture to PRISM v2's design. Verified correspondences (revised from the prior sourcing-caveated version of this entry):

| HRM | PRISM v2 |
|---|---|
| High-level (H) module, updates every $T$ steps | $M^{\text{slow}} \in \mathbb{R}^{B \times C_M^{\text{slow}} \times 6 \times 6}$, paired with V2 features ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3) |
| Low-level (L) module, updates every step | $M^{\text{fast}} \in \mathbb{R}^{B \times C_M^{\text{fast}} \times 12 \times 12}$, paired with V1 features |
| Hard timescale separation: $T$-step cycle | Soft timescale separation via chrono-init: $b_u^{\text{fast}} = -1$ ($\sigma(-1) \approx 0.27$ per-step); $b_u^{\text{slow}} = -3$ ($\sigma(-3) \approx 0.05$ per-step) |
| H → L feedback: $z_H$ supplied as input to $f_L$ | Slow-FiLM modulation: $M^{\text{slow}}_{t-1}$ upsampled to V1 spatial grid, modulates V1 features ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.4) |
| L → H feedback: $z_L^*$ supplied as input to $f_H$ | Spatially-pooled V1 prediction error $E_{V_1}$ fed into slow GRU update ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.7) |
| Hierarchical convergence: L equilibrates per cycle | PRISM v2 has no explicit equilibrium step; the slow update happens occasionally but is not preceded by an L-convergence guarantee |
| One-step implicit gradient | PRISM v2 uses BPTT |
| Deep supervision with detached segments | PRISM v2 trained end-to-end on episodes with BPTT |
| Adaptive computational time | PRISM v2 has no ACT |

The architectural alignment on the *static* design is tight. The architectural differences on the *training procedure* are more substantial: HRM avoids BPTT entirely via the implicit-gradient approximation; PRISM v2 uses BPTT through the unrolled episode. Adopting HRM's training scheme in PRISM v2 would be a significant architectural change but would likely make scaling easier.

**The user's program goes one step further than HRM in three ways:**

1. **Three memory compartments, not two.** The Evolution of Architecture document specifies three hierarchical levels, with conv descending / conv-transpose ascending projections handling the spatial mismatch. HRM's two-level design is a strict simplification.

2. **The Feedback Transformer as the general communication primitive.** HRM's coupling between H and L is via direct state input to the recurrence; the Feedback Transformer ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §1) is a more general primitive that combines arbitrary feedback sources via per-state Q/K/V projection and Hadamard product before softmax. HRM is a special case (two sources, simple input combination).

3. **Competition-emergent-PC theoretical thesis.** HRM has the architectural commitments without the theoretical motivation that the user's program supplies. The user's coalition-resource-competition argument predicts that hub-specific objectives + a shared self-attention substrate should *emergently* produce internal world-model dynamics — a falsifiable claim HRM does not engage with.

**Publishing-strategy implication:** if HRM is the current SOTA on the reasoning benchmarks the paper reports, PRISM v2 / the user's program should be benchmarked against HRM on those tasks. The fairest comparison would be (a) train PRISM v2 from scratch on Sudoku-Extreme or Maze-Hard with comparable parameter budget; (b) report whether the architectural differences (three vs two compartments, conv-based ascending/descending, FT-style multiplicative feedback) compound the hierarchical-convergence gains. If PRISM v2 underperforms HRM, the story is "we have a more general architecture but it's harder to train at scale." If PRISM v2 matches or exceeds, the story is "the additional architectural commitments matter, and they motivate the user's broader theoretical program."

## 8. Citations to follow

- `mujika2017_fast_slow_rnn` — predecessor architecture in seed. Should be deepened next.
- `tallec_ollivier2018_chrono_init` — chrono-init mechanism. Should be deepened.
- `schmidhuber2015_learn_to_think` — coupled-RNN ancestor; in seed (currently full but pre-revision).
- `bai_kolter_koltun2019_deep_equilibrium_models` — the DEQ paper HRM cites for its implicit-gradient framing. *Add to seed.*
- `whittington_bogacz2019_local_credit_assignment` — local-plasticity perspective HRM aligns with. Not in seed.
- `graves2016_act` — adaptive computation time (referenced by HRM, in v2 proposal). In seed.
- `banino2021_pondernet` — PonderNet, another ACT variant. In seed.
- `goldman_rakic1995_cellular_wm`, `funahashi1989_mnemonic_dlpfc`, `constantinidis2018_persistent_activity` — PFC persistent-activity literature grounding the slow timescale. In seed.
- `buzsaki_wang2012_gamma` — fast-timescale gamma. In seed.

## 9. Resolved open questions (from prior entry)

1. **What benchmarks does HRM report?** ARC-AGI-1, ARC-AGI-2, Sudoku-Extreme, Maze-Hard. Numbers in §5.
2. **What architecture is inside each module?** Transformer-like blocks (see PDF figure 4); details on attention/FFN configuration in the paper's appendix.
3. **How is the coupling implemented?** Direct state input: H's previous state is an input to $f_L$, L's final state is an input to $f_H$. No attention-based coupling between modules.
4. **Empirical comparison to Mujika 2017?** Not directly performed in the HRM paper. The contribution over Mujika is the hierarchical-convergence mechanism (nested fixed points) plus the implicit-gradient training, not just fast-slow update rates.
5. **Open-source implementation status.** Code released: `github.com/sapientinc/HRM` (per the paper's title page footnote).
