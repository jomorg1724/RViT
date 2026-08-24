---
id: dabney2018_qr_dqn
title: "Distributional Reinforcement Learning with Quantile Regression"
authors:
  - "Dabney, Will"
  - "Rowland, Mark"
  - "Bellemare, Marc G."
  - "Munos, Rémi"
year: 2018
venue: "AAAI"
doi: ""
arxiv: "1710.10044"
url: "https://arxiv.org/abs/1710.10044"
tags:
  - reinforcement-learning
  - deep-learning
concepts:
  - distributional-rl
related:
  - bellemare2017_c51
  - dabney2020_distributional_dopamine
  - botvinick2020_deep_rl_neuro
  - sutton_barto2018_rl_intro
  - schulman2017_ppo
relevance_to:
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-20"
---

# Distributional Reinforcement Learning with Quantile Regression

## 1. Abstract

> In reinforcement learning an agent interacts with the environment by taking actions and observing the next state and reward. When sampled probabilistically, these state transitions, rewards, and actions can all induce randomness in the observed long-term return. Traditionally, reinforcement learning algorithms average over this randomness to estimate the value function. In this paper, we build on recent work advocating a distributional approach to reinforcement learning in which the distribution over returns is modeled explicitly instead of only estimating the mean. That is, we examine methods of learning the value distribution instead of the value function. We give results that close a number of gaps between the theoretical and algorithmic results given by Bellemare, Dabney, and Munos (2017). First, we extend existing results to the approximate distribution setting. Second, we present a novel distributional reinforcement learning algorithm consistent with our theoretical formulation. Finally, we evaluate this new algorithm on the Atari 2600 games, observing that it significantly outperforms many of the recent improvements on DQN, including the related distributional algorithm C51.

(Verbatim from arXiv:1710.10044v1, 27 Oct 2017.)

## 2. Why this matters for us

This paper supplies the *algorithm HRA's distributional Q critic literally implements*. The default `HRAModel.critic` is a `DistributionalQHead` that produces $Q_\phi(s, a; \tau_i) \in \mathbb{R}^{B \times |\mathcal{A}| \times N}$ trained with `losses.quantile_huber_loss` on the executed-action slice — that loss is Equations 9–10 of this paper applied per action, and the parametrization is Equation 7. Everything HRA D6 inherits about *why* a distributional critic is the right value head — Wasserstein contraction, freedom from a pre-specified support, unbiased per-quantile stochastic gradients, the equivalence between the quantile midpoints $\hat\tau_i = (2i-1)/(2N)$ and the W₁-optimal $N$-Dirac projection — comes from this paper. The bridge to D6 runs through both the algorithm (Q_CRITIC.md §2.3 ports `quantile_huber_loss` verbatim from Equation 10) and the broader concept node [`distributional_rl`](../concepts/distributional_rl.md). The Recurrent-ViT lineage's eventual v2 critic upgrade (scalar V → action-conditional QR-DQN) is exactly the design move this paper made for value-only distributional RL.

## 3. Key claims

1. The distributional Bellman operator $\mathcal{T}^\pi$ is a $\gamma$-contraction in the maximal $p$-Wasserstein metric $\bar d_p$ on value distributions (Lemma 1, restated from Bellemare, Dabney & Munos 2017).
2. Sample gradients of the Wasserstein loss are in general *biased*, so the operator's contraction does not directly yield a usable SGD-based algorithm — closing this gap is the paper's central contribution (Theorem 1 of C51 paper; Proposition 1 here).
3. *Transposing* C51's parametrization — fixed uniform probabilities $1/N$ on $N$ adjustable Dirac locations $\theta_i$ — converts the distribution to a *quantile distribution* whose locations correspond to the $\hat\tau_i = (2i-1)/(2N)$ midpoints of the inverse-CDF (Lemma 2 + Equation 7).
4. The classic quantile regression loss $\rho_\tau(u) = u(\tau - \mathbb{1}\{u<0\})$ (Equation 8) provides *unbiased* sample gradients for the per-location quantile estimates $\theta_i$, enabling a true stochastic-gradient distributional RL algorithm.
5. The Huber-smoothed quantile loss $\rho_\tau^\kappa$ with smoothing threshold $\kappa$ (Equations 9–10) improves performance under non-linear function approximation by removing the gradient discontinuity at zero error.
6. The composition $\Pi_{W_1} \circ \mathcal{T}^\pi$ — distributional Bellman update followed by quantile projection — is a $\gamma$-contraction in the $\infty$-Wasserstein metric $\bar d_\infty$ (Proposition 2). Combined with the universal upper bound $\bar d_p \le \bar d_\infty$, this gives convergence in all $p$-Wasserstein metrics.
7. **The contraction proof does not extend to the control setting** (where actions are selected greedily w.r.t. mean Q): the paper's Lemma 5 in the appendix exhibits a counter-example, leaving a theory-practice gap that empirical results then over-fill.
8. QR-DQN — DQN with a quantile-distributional output layer of size $|\mathcal{A}| \times N$, the quantile Huber loss replacing the standard Huber, and Adam replacing RMSProp — substantially outperforms C51 and the best pre-distributional DQN variants on the 57-game Atari 2600 benchmark.

## 4. Methods

**Quantile distribution.** Let $\theta : \mathcal{X} \times \mathcal{A} \to \mathbb{R}^N$ be a parametric model and define
$$
Z_\theta(x, a) := \frac{1}{N} \sum_{i=1}^N \delta_{\theta_i(x, a)} \quad \in \mathcal{Z}_Q \qquad (\text{Equation 7}).
$$
The corresponding cumulative probabilities are $\tau_i = i/N$ (with $\tau_0 = 0$), and the *midpoints* — the W₁-optimal target locations per Lemma 2 — are $\hat\tau_i = (\tau_{i-1} + \tau_i)/2 = (2i - 1)/(2N)$.

**W₁-optimal projection.** Lemma 2 establishes that the set of $\theta$ minimizing $\int_\tau^{\tau'} |F^{-1}(\omega) - \theta|\,d\omega$ is $\{\theta \in \mathbb{R} : F(\theta) = (\tau+\tau')/2\}$, i.e., the median location of the CDF over the interval. Together with Equation 7, this means the projection $\Pi_{W_1} Z$ of any distribution $Z$ onto $\mathcal{Z}_Q$ assigns each $\theta_i$ the value $F_Z^{-1}(\hat\tau_i)$ — the per-midpoint quantile of the target.

**Quantile regression loss.** For a target distribution $Z$ and quantile $\tau \in [0,1]$, the (asymmetric) quantile regression loss is
$$
L_{QR}^\tau(\theta) := \mathbb{E}_{\hat Z \sim Z}\!\left[\rho_\tau(\hat Z - \theta)\right], \qquad \rho_\tau(u) = u(\tau - \mathbb{1}\{u < 0\}) \qquad (\text{Equation 8}).
$$
This loss has unbiased sample gradients — the practical fix to Proposition 1's biased-Wasserstein-gradient obstacle. By Lemma 2, simultaneously minimizing $\sum_i L_{QR}^{\hat\tau_i}(\theta_i)$ recovers the $\Pi_{W_1}$ projection of the target.

**Quantile Huber loss.** Because $\rho_\tau$ is non-smooth at $u = 0$, the authors propose a Huber-smoothed variant. With Huber penalty
$$
\mathcal{L}_\kappa(u) = \begin{cases} \tfrac{1}{2} u^2, & |u| \le \kappa \\ \kappa(|u| - \tfrac{1}{2}\kappa), & \text{otherwise} \end{cases} \qquad (\text{Equation 9}),
$$
the quantile Huber loss is
$$
\rho_\tau^\kappa(u) = |\tau - \mathbb{1}\{u < 0\}| \cdot \mathcal{L}_\kappa(u) \qquad (\text{Equation 10}).
$$
$\rho_\tau^{\kappa=0}$ recovers the original quantile regression loss; HRA / PRISM v2 use the $\kappa = 0.5$ variant per Q_CRITIC.md's `value_huber_kappa` setting.

**QRTD (policy evaluation).** Online TD-style update for the per-quantile locations (Equation 12):
$$
\theta_i(x) \;\leftarrow\; \theta_i(x) + \alpha \left(\hat\tau_i - \mathbb{1}\{r + \gamma z' < \theta_i(x)\}\right), \qquad z' \sim Z_\theta(x'),\; r \sim R(x,a),\; x' \sim P(\cdot \mid x, a).
$$
In practice the full $N \times N$ matrix of pairs $(\theta_i(x), \theta_j(x'))$ is averaged per step.

**QR-DQN (control, Algorithm 1).** Three modifications to DQN:
1. Output layer size $|\mathcal{A}| \times N$ instead of $|\mathcal{A}|$.
2. Replace DQN's Huber loss with the quantile Huber loss $\rho_{\hat\tau_i}^\kappa$ applied per quantile index.
3. Replace RMSProp with Adam.

The greedy action at the next state is taken w.r.t. the *mean* of the next-state quantile distribution: $a^* = \arg\max_{a'} \sum_j q_j \theta_j(x', a')$. The target $\mathcal{T}\theta_j = r + \gamma \theta_j(x', a^*)$ is used per quantile.

**Convergence theory.** Proposition 2 shows that $\Pi_{W_1} \circ \mathcal{T}^\pi$ is a $\gamma$-contraction in $\bar d_\infty$. The contraction holds for $p = \infty$ but *not* in general for $p < \infty$ when projection is involved (Lemma 5 in the appendix). For the *control* operator (greedy action), no contraction proof is given — the empirical successes of QR-DQN are not theoretically guaranteed in this setting, only the evaluation case is.

## 5. Results

All Atari numbers below are human-normalized scores, best-agent protocol, 200M training frames, 57 games (Table 1 of the paper):

| Algorithm           | Mean  | Median | >human | >DQN |
|---------------------|-------|--------|--------|------|
| DQN                 | 228%  | 79%    | 24     | 0    |
| Double DQN          | 307%  | 118%   | 33     | 43   |
| Dueling DQN         | 373%  | 151%   | 37     | 50   |
| Prioritized replay  | 434%  | 124%   | 39     | 48   |
| Prior. Dueling      | 592%  | 172%   | 39     | 44   |
| **C51**             | 701%  | 178%   | 40     | 50   |
| **QR-DQN-0** (κ=0)  | 881%  | 199%   | 38     | 52   |
| **QR-DQN-1** (κ=1)  | **915%** | **211%** | 41   | 54   |

QR-DQN-1 outperforms C51 by ~33% median score (the headline number in the introduction) and is the strongest single-improvement DQN variant in the table — beating Prioritized Dueling by 39 percentage points in median and almost half the games (50% of 57 ≈ 28 games) by raw score margin.

**Best hyperparameters** (from a sweep on 5 training games): $\alpha = 5 \times 10^{-5}$, ADAM-$\epsilon = 0.01/32$, $N = 200$. The sweep over $N \in \{10, 50, 100, 200\}$ shows monotonic improvement with $N$, plateauing only weakly at $N = 200$. Exploration $\epsilon$ decays to 0.01 (lower than DQN's 0.1, matching recent practice).

**Tabular policy-evaluation experiment (Figure 3).** On a stochastic two-room windy gridworld, QRTD ($N = 32$) recovers the Monte-Carlo–estimated value *distribution* (1-Wasserstein error to ground truth) while TD(0) only recovers the mean. Validates that the algorithm does the distributional thing it claims to.

## 6. Critique / limitations

1. **No contraction proof for the control setting.** Proposition 2 only covers policy evaluation under a fixed $\pi$. The Bellman *optimality* operator with greedy action selection is not shown to be a contraction in any Wasserstein metric, and Lemma 5 (appendix) gives a counter-example showing why the natural extension fails. QR-DQN's empirical success in the control setting (Atari results above) is therefore unexplained by the paper's theory.
2. **Wasserstein gradient bias is acknowledged but not closed for finite-sample empirical distributions.** Proposition 1 here shows that even with the quantile parametrization $Z_\theta$, the empirical sample gradient of $W_p(\hat Z_m, Z_\theta)$ is biased for general $p$. The paper's resolution — minimize per-quantile regression losses instead of the joint Wasserstein loss — sidesteps this rather than refuting it. The auxiliary-task-like explanation of distributional RL's empirical wins (return distribution as a richer supervised signal for shared representation learning) remains the best account of why distributional methods work despite the control-setting gap.
3. **$N$ is a hyperparameter with no principled prior.** The Atari sweep uses $N = 200$; smaller values (10, 50, 100) trade resolution for compute. There is no theoretical justification for any specific value — only the empirical pattern that more quantiles are better up to a plateau. (Subsequent work, IQN (Dabney et al. 2018b), eliminates this by making $\tau$ itself an input.)
4. **Greedy-by-mean action selection discards the distribution at decision time.** The whole point of representing $Z(s, a)$ is that it carries information beyond the mean; QR-DQN's action selection $a^* = \arg\max_a \mathbb{E}[Z(\cdot, a)]$ ignores all of it. The paper acknowledges this in the Conclusions ("richer policy class…risk-sensitive decision making") as a future direction; the issue is dispatched but not addressed in the algorithm.
5. **No combination with the other DQN improvements in Table 1.** QR-DQN is evaluated as a *pure* substitute for the categorical projection of C51, deliberately not stacked with Double DQN / Dueling / Prioritized Replay. Rainbow (Hessel et al. 2018, not in this paper's references but published the same year) would shortly demonstrate the additivity.
6. **All experiments are off-policy DQN-style.** The distributional + on-policy combination — which HRA's recurrent PPO requires — is not characterized in this paper; later work has only partially closed this gap (see open question 5 in [`concepts/distributional_rl.md`](../concepts/distributional_rl.md)).
7. **Asymptotic-only convergence guarantees.** As with all stochastic-approximation arguments, the contraction proof gives the *fixed-point* behaviour at $t \to \infty$ but no finite-time rate; sample-complexity guarantees are absent.

## 7. Connection to our work

**Direct algorithmic ancestor of HRA's distributional Q critic.** HRA D6 ([`MODEL_DESIGN.md`](../../docs/MODEL_DESIGN.md) §6, "D6 — Critic: action-conditional distributional QR-DQN") commits the default `HRAModel.critic` to the action-conditional form of this paper's algorithm. The mapping is essentially mechanical:

- *Parametrization.* `DistributionalQHead` in [`HRA/readout.py`](../../archive/HRA/readout.py) produces $Q_\phi(s, a; \tau_i) \in \mathbb{R}^{B \times |\mathcal{A}| \times N}$ at $N = 51$ (HRA's chosen quantile count; this paper used $N = 200$ on Atari, but the underlying argument is invariant). This is the action-conditional generalization of Equation 7 in this paper — instead of one $Z_\theta(x, a)$ head per (state, action), HRA exposes the full $|\mathcal{A}| \times N$ block in a single forward pass, then `gather`-indexes the executed-action slice for the loss.
- *Loss.* HRA's [`quantile_huber_loss`](../../archive/HRA/losses.py) is *exactly* Equation 10 of this paper, applied on the executed-action quantile slice (the `gather`-then-broadcast pattern in [`Q_CRITIC.md`](../../archive/Prism/docs/PRISM_V2/Q_CRITIC.md) §"Common pitfalls"). HRA uses $\kappa = 0.5$ rather than this paper's $\kappa \in \{0, 1\}$ — the smaller Huber threshold was a stability fix shipped after the iter-887 NaN crash (project memory: "value_huber_kappa (1.0 → 0.5)").
- *Value derivation.* HRA derives $V_\phi(s) = \sum_a \mathrm{sg}[\pi_\theta(a \mid s)]\,Q_\phi(s, a)$ via expected-SARSA-style mixing against the stop-graded policy — this is the on-policy analogue of QR-DQN's greedy-by-mean action selection, swapped in for PPO's GAE recursion (see [`Q_CRITIC.md`](../../archive/Prism/docs/PRISM_V2/Q_CRITIC.md) §2.4 on gradient routing).

**The "transposed parametrization" is what HRA D6 is exploiting at the architectural level.** This paper's central insight is that *fixed probabilities on adjustable locations* is dual to C51's *fixed locations with adjustable probabilities* — and the former gets you (i) freedom from a pre-specified return support, (ii) Wasserstein contraction in the evaluation projection, and (iii) unbiased per-quantile SGD. HRA's change-detection task has no principled prior on the return support (rewards range from ~−1 to ~+10 in early training and can grow with policy improvement), so the C51 alternative would require an engineering choice that the QR parametrization simply does not need. This is the design pressure that drives the D6 choice of QR-DQN over C51.

**Per-action exposure rather than marginal.** A subtler architectural commitment: this paper exposes $Q(s, a)$ per-action (Algorithm 1's output layer is $|\mathcal{A}| \times N$), whereas the *marginal*-$Z$ formulation of distributional RL (PRISM v2's original v2 critic — see [`Q_CRITIC.md`](../../archive/Prism/docs/PRISM_V2/Q_CRITIC.md) §1) computes only $Z(s)$ and recovers $V$ as its mean. The marginal formulation suffers the bootstrapping-prior failure mode documented in Q_CRITIC.md §1: when the policy is near-deterministically committed to one action, the marginal critic only ever learns the value of the dominant action, and the rare exploration-action transitions produce noise advantages. *Per-action* exposure (this paper's Equation 7 generalized to action-conditional form) supplies a learnable parameter for each $(s, a)$ pair whose gradient says "the value of this action here differs from the value of that one" — the structural fix the marginal critic cannot make. HRA D6 inherits this fix verbatim.

**Where HRA *departs* from this paper.** Three deltas:

1. **On-policy (PPO) rather than off-policy (DQN).** This paper's empirical setting is pure off-policy DQN with replay; HRA pairs the distributional Q head with recurrent PPO ([`schulman2017_ppo`](schulman2017_ppo.md), [`pleines2022_recurrent_ppo`](pleines2022_recurrent_ppo.md)). The on-policy combination is less explored in the literature and the bias/variance properties of QR-Huber-on-executed-slice as a GAE-target replacement are not fully characterized — flagged as open question 5 in [`concepts/distributional_rl.md`](../concepts/distributional_rl.md).
2. **Greedy-by-mean replaced by stochastic-by-actor-logits.** This paper's action selection is $a^* = \arg\max_a \mathbb{E}[Z(s, a)]$, discarding the distribution at decision time. HRA's actor is a separate PPO policy head and samples actions per its softmax; the quantile distribution feeds into *training* (via QR-Huber on the executed slice) and into *analysis* (the `q_dist` interpretability hook in §7 of MODEL_DESIGN.md) but does *not* gate the action choice. This is one of the architectural surfaces where HRA D6 could be extended in a v3 — a *risk-sensitive* or *information-seeking* policy that reads the per-action quantile distribution rather than just the mean.
3. **Variance-into-attention as a v3 commitment.** HRA's eventual plan is to project the variance $\hat\sigma^2_V(s)$ of the learned $Z(s, a)$ distribution into the Feedback Transformer's Q/K stream as a precision signal — the engineering analogue of [`monosov2020_outcome_uncertainty`](monosov2020_outcome_uncertainty.md)'s pallidal-habenular uncertainty circuits. This is not in this paper (which uses the distribution only as a training target), but the architectural precondition — a distribution rather than a scalar — is what this paper supplies.

**Verification surface.** The HRA test [`test_critic_head_action_conditional_distributional`](../../archive/HRA/tests/test_shapes.py) enforces $V = \sum \pi Q$ identity; [`test_action_conditional_critic_grad_routing`](../../archive/HRA/tests/test_shapes.py) verifies that the QR-Huber gradient routes only to the executed-action column of `critic.fc2` (the structural property *this paper* exploits, generalized to the action-conditional case). These tests are the contract that HRA's implementation matches the paper's algorithm.

## 8. Citations to follow

- `dabney2018_iqn` — Dabney, Ostrovski, Silver & Munos 2018 *Implicit Quantile Networks for Distributional Reinforcement Learning* (arXiv:1806.06923). The natural successor: replace fixed $\{\hat\tau_i\}$ with sampled $\tau \sim U(0, 1)$ at every step, parametrize $Z(s, a, \tau)$ as an implicit quantile network. Eliminates the $N$ hyperparameter and supports risk-sensitive policies. *Not yet in db.*
- `mnih2015_dqn` — Mnih, Kavukcuoglu, Silver et al. 2015 *Human-level control through deep reinforcement learning*. *Nature* 518:529. The DQN architecture QR-DQN inherits and minimally modifies (cf. this paper's "We focus on the minimal changes necessary…"). Foundational. *Not yet in db.*
- `koenker_bassett1978_quantile_regression` — Koenker & Bassett 1978 *Regression quantiles*. *Econometrica* 46(1):33–50. Source of the asymmetric pinball loss this paper ports into the deep-RL setting; the citation chain Koenker 2005 textbook → this paper → HRA's `quantile_huber_loss`. *Not yet in db.*
- `rowland2018_categorical_analysis` — Rowland, Bellemare, Dabney, Munos, Teh 2018 *An Analysis of Categorical Distributional Reinforcement Learning* (AISTATS). Theoretical companion that frames C51 as a Cramér-distance projection — the paper this work positions against. *Not yet in db.*
- `hessel2018_rainbow` — Hessel, Modayil, van Hasselt et al. 2018 *Rainbow: Combining Improvements in Deep Reinforcement Learning* (AAAI). Demonstrates that QR-DQN (and the rest of the Table 1 column) combine additively — the empirical follow-up this paper explicitly defers in §"Conclusions". *Not yet in db.*
- `wang2016_dueling` — Wang, Schaul, Hessel, van Hasselt, Lanctot, de Freitas 2016 *Dueling Network Architectures for Deep Reinforcement Learning* (ICML). Closest published precursor for the explicit per-action exposure of Q (the architectural antecedent of the action-conditional form HRA D6 uses). Cited by Q_CRITIC.md §3. *Not yet in db.*
- `bellemare2023_distributional_textbook` — Bellemare, Dabney & Rowland 2023 *Distributional Reinforcement Learning* (MIT Press). The canonical algorithmic textbook treatment subsuming this paper, C51, IQN, and the contraction proofs. *Not yet in db; flagged for `concepts/distributional_rl.md` reference list.*
