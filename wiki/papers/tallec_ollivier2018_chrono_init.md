---
id: tallec_ollivier2018_chrono_init
title: "Can recurrent networks warp time? (chrono-initialization)"
authors:
  - "Tallec, Corentin"
  - "Ollivier, Yann"
year: 2018
venue: "ICLR"
doi: ""
arxiv: "1804.11188"
url: "https://arxiv.org/abs/1804.11188"
tags:
  - recurrent-networks
  - deep-learning
  - theoretical-essay
concepts:
  - chrono-initialization
  - lstm-cell
  - gru-cell
  - slow-fast-recurrence
  - multi-compartmental-memory
related:
  - mujika2017_fast_slow_rnn
  - hochreiter_schmidhuber1997_lstm
  - wang2025_hierarchical_reasoning_model
  - beck2024_xlstm
  - jozefowicz2015_rnn_exploration
relevance_to:
  - prism_v2
seed_source:
  - prism_v2_proposal
status: full
depth: full
last_updated: "2026-05-16"
---

# Can recurrent networks warp time? (chrono-initialization)

## 1. Abstract

Tallec & Ollivier argue that the gating mechanisms inside LSTM and GRU cells can be re-derived from a single requirement: a recurrent network should be approximately invariant to *time warpings* of its input — smooth, time-varying changes in the effective sampling rate at which the temporal signal is presented. Starting from a continuous-time leaky integrator and asking what discrete update rule makes the hidden state robust to such warpings, the authors recover gated update equations of the same form as the LSTM forget gate and the GRU update gate. The same derivation yields a principled *initialization* for the bias parameters of these gates: a "chrono initialization" that sets the forget-gate bias so that the cell's effective memory horizon at initialization matches a user-specified maximum dependency timescale $T_{\max}$. Empirically the authors show that chrono initialization substantially improves learning of long-term dependencies on synthetic tasks (copy, adding) and on pixel-by-pixel sequence classification, compared with standard zero or +1 initializations of the forget-gate bias.

## 2. Why this matters for us

PRISM v2 commits to a slow/fast memory split (`PrismV2/docs/PRISM_V2_PROPOSAL.md` §3.3) implemented as two parallel gated states whose update probabilities are set by initial gate biases: $b_u^{\text{fast}} = -1$ ($\sigma(-1) \approx 0.27$ per-step update probability), $b_u^{\text{slow}} = -3$ ($\sigma(-3) \approx 0.05$). This bias-based timescale separation is exactly the mechanism Tallec & Ollivier formalize. Their derivation supplies the ML foundation for PRISM v2's design: gate biases are not arbitrary regularization knobs but the parameters that control the cell's *characteristic memory timescale*, and they should be initialized to span the timescales the task actually demands. Their formula for that initialization is the literal tool PRISM v2 uses to set $b_u^{\text{fast}}$ and $b_u^{\text{slow}}$, and it generalizes naturally to the user's planned three-memory architecture (`threads/the_user_architectural_program.md` §3) where each level needs its own characteristic timescale.

## 3. Key claims

1. The hidden-state update of an LSTM forget gate (or a GRU update gate) is the natural discrete-time analog of a continuous-time leaky integrator whose time constant is itself input-dependent — i.e., gates are not an ad-hoc trick but the unique mechanism that gives a recurrent cell quasi-invariance to time warpings of the input.
2. Under this view, the forget-gate bias $b_f$ controls the cell's characteristic memory horizon at initialization: $\sigma(b_f)$ is the per-step retention probability, so the expected forgetting time is approximately $1 / (1 - \sigma(b_f))$, equivalently $\exp(b_f)$ for moderately positive $b_f$.
3. *Chrono initialization* sets $b_f \sim \log(\mathcal{U}([1, T_{\max} - 1]))$ for an LSTM forget gate, with input-gate bias initialized as $b_i = -b_f$. This makes each unit's effective memory horizon at initialization uniformly distributed (in log space) between 1 and $T_{\max}$, where $T_{\max}$ is the longest dependency length the task is expected to contain.
4. Chrono initialization substantially improves training and final performance on tasks with long-range dependencies (synthetic copy and adding tasks at long horizons, pixel-by-pixel sequence classification) compared with standard zero or +1 forget-gate initialization.
5. The argument is architecture-prescriptive, not merely a tuning recipe: the requirement of time-warping invariance singles out the gated-leaky-integrator family of cells, suggesting that any well-functioning recurrent cell must in some form implement this kind of input-dependent time constant.
6. Initialization matters more than the literature had assumed for long-range tasks. The common practice of initializing $b_f = 1$ (Gers et al. 2000) corresponds to a *single* initial timescale of $\sigma(1) \approx 0.73$, i.e., $\approx 3.7$ steps — far too short for the long-horizon copy task. The remedy is structural, not optimizer-related: no amount of careful training fixes a network whose entire population of units has a $\sim 4$-step initial horizon.

## 4. Methods

**Time-warping invariance.** A *time warping* is a smooth monotone reparameterization $\tau: \mathbb{R}_+ \to \mathbb{R}_+$ of the time axis: the same underlying signal $s(t)$ is presented to the network as $s(\tau(t))$ on a faster or slower clock. A recurrent cell is *invariant to time warpings* if its hidden trajectory, viewed in the new time coordinate, is the same as the un-warped trajectory of the un-warped signal. For a fixed-time-constant leaky integrator this fails: the cell's effective memory length is measured in *steps*, not in *signal time*, so resampling the input changes the network's behavior. Invariance requires the time constant itself to scale with the local rate $\tau'(t)$.

**Leaky-integrator derivation.** Start from a continuous-time leaky-integrator hidden state $\dot{h}(t) = -\alpha\, h(t) + \alpha\, F(x(t), h(t))$ with time constant $1/\alpha$. Discretize at step size $\Delta t$ to obtain $h_{t+1} = (1 - \alpha \Delta t)\, h_t + (\alpha \Delta t)\, F(x_t, h_t)$. To make the network invariant to time-warpings $t \mapsto \tau(t)$, the time constant $\alpha$ must itself depend on the input — there is no way to fix a single $\alpha$ that works across warpings, because the warping is not known a priori. The minimal modification is to make $\alpha$ a learnable input-dependent quantity $\alpha(x_t, h_t) = \sigma(W x_t + U h_t + b)$ with $\sigma$ the logistic sigmoid (which keeps $\alpha \in (0,1)$). Substituting back gives an update rule of the form
$$h_{t+1} = (1 - g_t)\, h_t + g_t\, F(x_t, h_t), \qquad g_t = \sigma(W x_t + U h_t + b),$$
which is exactly the GRU update equation (or the LSTM forget-gate equation, after the analogous derivation for the cell state). The authors emphasize that this derivation is *prescriptive*: starting from the requirement of time-warping invariance, the gated leaky integrator is essentially forced, and architectures that achieve robust long-range learning without such gates (e.g., unitary RNNs) are doing so by other means than time-warp invariance.

**Chrono initialization.** From the leaky-integrator interpretation, $\sigma(b_f)$ is the expected per-step *retention* probability at initialization (input-independent term). A unit with retention $p = \sigma(b_f)$ has expected forgetting time $1/(1 - p) \approx \exp(b_f)$ for $b_f \gg 0$. To cover dependency timescales up to $T_{\max}$, sample each unit's forget-gate bias as
$$b_f \sim \log\!\big(\mathcal{U}([1,\, T_{\max} - 1])\big),$$
i.e., $b_f = \log u$ with $u$ uniform on $[1, T_{\max} - 1]$. For the LSTM, the input-gate bias is set to $b_i = -b_f$, so that the candidate-input fraction $\sigma(b_i) = 1 - \sigma(b_f)$ is the complement of the retention fraction — the cell can equally well move toward a new input as retain its state. All other parameters use a conventional small-Gaussian initialization.

**Experiments.** Three families of benchmark sequence tasks. (i) Synthetic *copy task*: present a short pattern, wait $T$ steps, reproduce the pattern. The required dependency length is $T$. (ii) Synthetic *adding task*: present a length-$T$ sequence of random numbers with two marked positions; output the sum of the two marked numbers. (iii) *Pixel-by-pixel sequence classification* (pMNIST, permuted-pMNIST): a 28×28 image is flattened to a length-784 sequence presented one pixel at a time, the network must classify the digit after consuming the full sequence. For each task the authors compare LSTM and GRU with chrono-init forget/update gate biases against the same architectures with standard initialization (commonly $b_f = 0$ or $b_f = 1$).

## 5. Results

Specific numbers are not all directly verifiable from the metadata pages reachable here (the arXiv landing page and the OpenReview record, see §6), so this section gives the qualitative direction the paper claims rather than exact tables. The paper's headline experimental claims are:

- On the *copy task* at long horizons ($T = 500$ and longer), an LSTM with chrono initialization learns to copy with near-zero loss, while the same LSTM with standard initialization plateaus at the trivial baseline loss (the model never learns to retain information across the gap). The chrono-init effect is qualitative, not marginal — it is the difference between a network that solves the task and one that does not.
- On the *adding task* at long horizons, chrono-init similarly produces orders-of-magnitude lower MSE than standard initialization, and the gap widens as $T$ grows.
- On *pMNIST*, chrono-init reaches test accuracy comparable to the best contemporaneous LSTM variants while training noticeably faster in the first epochs; on *permuted-pMNIST* the advantage over standard initialization is larger because the task's effective dependency length is closer to the full 784-pixel sequence.
- GRUs benefit from the same idea applied to the update gate.
- The single hyperparameter that has to be set is $T_{\max}$, which the authors recommend choosing as the longest dependency length the task is plausibly expected to contain — this is the only task-side knowledge the method requires. Setting $T_{\max}$ too low truncates the network's effective memory; setting it too high distributes too many units to long timescales they cannot make use of. The method is robust across a wide range of intermediate $T_{\max}$ values.

The take-away the paper presses is not "chrono-init is the best initialization on every benchmark" but "chrono-init removes a *specific* failure mode (the network cannot retain information beyond its default time constant) that standard initialization induces on long-range tasks." On tasks whose dependency length is comparable to the default $\sigma(b_f) = \sigma(1) \approx 0.73$ retention (i.e., a few-step horizon), chrono-init and standard init perform similarly.

## 6. Critique / limitations

The strength of the paper is conceptual: it gives a single principle — invariance to time warping — that motivates the gated update *and* tells you how to initialize it. The empirical demonstration is at the scale that was standard for ICLR 2018 papers on RNN long-range modelling (synthetic tasks plus pMNIST), so the evidence is suggestive rather than definitive at the scale of, say, language modelling on contemporary corpora. The derivation assumes that the cell's update rate should be invariant to *smooth* warpings of time; tasks with abrupt regime changes (e.g., event-driven streams) fit the framework less obviously.

Several load-bearing assumptions deserve naming. (i) The "characteristic timescale" interpretation of $\sigma(b_f)$ is exact only when the gate's input-dependent term $W x_t + U h_t$ is held at zero in expectation; once a network is trained these terms shift the effective timescale, sometimes substantially. (ii) The sampling distribution $\log \mathcal{U}([1, T_{\max} - 1])$ is uniform in log-timescale, which assumes the task's relevant timescales are distributed log-uniformly; for tasks with a strongly bimodal timescale structure (a slow and a fast regime, no intermediate) one might prefer to draw $b_f$ from a bimodal distribution.

Subsequent work has somewhat softened the prescriptive force of the paper. The *xLSTM* architecture (Beck et al. 2024, `papers/beck2024_xlstm.md`) reorganizes the gating machinery in ways that do not slot cleanly into the leaky-integrator picture — although the chrono-init *idea* (set initial biases so that the cell's memory horizon matches the task) survives. Wang et al. 2025's HRM (`papers/wang2025_hierarchical_reasoning_model.md`) achieves slow-fast separation through *hard* update-rate gating (the slow module updates once per $T$ steps) rather than soft bias-controlled timescales, suggesting that for some tasks the chrono-init style of soft separation may be inferior to a discrete hierarchical schedule. Mujika et al. 2017 (`papers/mujika2017_fast_slow_rnn.md`) similarly use coupled RNNs with explicit fast and slow paths rather than relying on bias initialization. None of this invalidates the paper — these are alternative mechanisms, not refutations — but they do mean that chrono-init is one tool in a family rather than the unique solution.

A final concrete caveat: gate biases that produce *very* slow timescales (say $\sigma(b_f) > 0.99$) can be hard to train, because the slow state changes so rarely that the slow-path parameters receive only sparse gradient signal. This is an open question for PRISM v2's $b_u^{\text{slow}} = -3$ choice and especially for the user's third-memory-level proposal where the gate bias would be more negative still.

## 7. Connection to our work

PRISM v2 (`PrismV2/docs/PRISM_V2_PROPOSAL.md` §3.3) instantiates exactly the chrono-init mechanism this paper proposes, but specialized to a two-module slow/fast split rather than a continuous distribution of timescales:

- **Fast memory** $M^{\text{fast}}$: update-gate bias $b_u^{\text{fast}} = -1$ gives a per-step *update* probability of $\sigma(-1) \approx 0.27$, equivalently a *retention* probability of $\sigma(+1) \approx 0.73$, corresponding to a characteristic memory horizon of $\approx \exp(1) \approx 2.7$ steps for the input-independent term.
- **Slow memory** $M^{\text{slow}}$: $b_u^{\text{slow}} = -3$ gives update probability $\sigma(-3) \approx 0.05$, retention $\approx 0.95$, characteristic horizon $\approx \exp(3) \approx 20$ steps.

These choices implement, in the user's specific architecture, the exact intuition of Tallec & Ollivier: the bias term sets the cell's intrinsic timescale. They differ from the original paper in two ways. First, PRISM v2 hard-codes two specific biases rather than sampling biases over $[1, T_{\max} - 1]$ — the architecture commits to a two-timescale system rather than a continuous spread. Second, PRISM v2's gate is an *update* gate $b_u$ (signed in the standard "0 means freeze" convention), not the LSTM forget gate $b_f$ (signed in the "1 means retain" convention); the sign of the bias is correspondingly flipped, but the underlying mechanism is identical.

For the user's planned three-memory extension (`threads/the_user_architectural_program.md` §3), the same recipe scales directly: pick three characteristic timescales $T_1 < T_2 < T_3$ matching the task's natural hierarchy, set each level's update-gate bias to $b_u^{(k)} = -\log T_k$. The chrono-init derivation says nothing about what $T_k$ should be — that is a task-side question — but it does say that *once chosen*, $b_u^{(k)} = -\log T_k$ is the principled initial value.

The paper also bears on the broader Feedback Transformer / GridCell RNN program (`threads/the_user_architectural_program.md` §§1–2): every gated update in a GridCell RNN is subject to the same chrono-init reasoning. A clean implementation of the user's program would initialize each GridCell RNN's update gate bias from the chrono-init distribution scaled to that layer's expected timescale, rather than from a generic zero or +1 default.

The conceptual contribution is also a constraint on alternative designs. Any proposal in our program that replaces the gated update with a non-leaky alternative (for instance, hierarchical-convergence-style hard schedules à la HRM) is in tension with Tallec & Ollivier's argument that gating is the unique mechanism giving time-warping invariance. The trade-off between hard schedules (HRM) and soft chrono-init schedules (PRISM v2) is one of the open architectural questions catalogued in `concepts/slow_fast_recurrence.md`.

A specific empirical question this paper raises for our work: in PRISM v2 the slow-memory bias $b_u^{\text{slow}} = -3$ corresponds to a fixed initial timescale of $\approx 20$ steps. Change-detection sequences we care about can have dependency lengths well beyond that (across whole videos, hundreds of frames). The chrono-init recipe would suggest $b_u^{\text{slow}} \approx -\log T$ with $T$ in the hundreds — i.e., a much more negative bias than $-3$. The reason the proposal does not push that far is the training-stability issue (§6: very slow gates receive sparse gradient signal). Resolving this — possibly by chrono-init style *sampling* of the bias across the units within each memory level, so that each level contains a distribution of timescales rather than a single one — is a concrete experimental direction this paper licenses.

## 8. Citations to follow

- gers2000_lstm_forget_gate — original argument for forget-gate-bias $b_f = +1$ default; the baseline chrono-init replaces.
- arjovsky2016_urnn — unitary RNNs, the alternative mechanism for long-range dependency learning that chrono-init competes with on the copy/adding tasks.
- le2015_irnn — identity-initialized RNNs, another initialization-based approach to long-range learning that this paper contrasts with.
- pascanu2013_exploding_gradients — the gradient-stability motivation for caring about timescale initialization in the first place.
- chung2014_gru — the GRU paper, whose update gate is one of the two architectures whose initialization is prescribed here.
- ollivier2015_natural_gradient — Ollivier's prior work on invariance principles in deep learning, the methodological precursor to the time-warping-invariance derivation.
