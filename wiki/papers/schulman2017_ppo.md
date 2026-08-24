---
id: schulman2017_ppo
title: "Proximal Policy Optimization Algorithms"
authors:
  - "Schulman, John"
  - "Wolski, Filip"
  - "Dhariwal, Prafulla"
  - "Radford, Alec"
  - "Klimov, Oleg"
year: 2017
venue: "arXiv:1707.06347"
doi: ""
arxiv: "1707.06347"
url: "https://arxiv.org/abs/1707.06347"
tags:
  - reinforcement-learning
  - deep-learning
concepts:
  - ppo
  - actor-critic
  - gae
related:
  - schulman2016_gae
  - mnih2014_recurrent_attention
  - pleines2022_recurrent_ppo
  - sutton_barto2018_rl_intro
  - ha_schmidhuber2018_world_models
  - hafner2020_dreamer
  - botvinick2020_deep_rl_neuro
  - mnih2016_a3c
  - bellemare2017_c51
  - dabney2018_qr_dqn
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-19"
---

# Proximal Policy Optimization Algorithms

## 1. Abstract

The paper proposes Proximal Policy Optimization (PPO), a family of policy-gradient methods for reinforcement learning that alternate between sampling data through interaction with the environment and optimizing a "surrogate" objective function using stochastic gradient ascent. Whereas standard policy-gradient methods perform one gradient update per data sample, PPO introduces a novel surrogate objective that enables *multiple epochs of minibatch updates* on the same rollout buffer. The principal variant, PPO-Clip, replaces TRPO's hard KL-divergence trust-region constraint with a clipped probability-ratio objective that is first-order, requires no Hessian-vector products, and is straightforward to implement on top of any deep-learning framework. A secondary variant (PPO-KL) uses an adaptive KL penalty whose coefficient is adjusted online to match a target divergence. Across MuJoCo continuous-control benchmarks and the Atari Arcade Learning Environment, PPO matches or exceeds the sample complexity of TRPO and the wall-clock efficiency of A2C/ACER, while being much simpler to tune. PPO has since become the default on-policy actor-critic algorithm in deep RL practice.

## 2. Why this matters for us

PPO is the *training algorithm* used by both the published Recurrent ViT change-detection model (arXiv:2502.10955) and PRISM v1, and it is the actor-side optimizer for PRISM v2's actor + distributional-Q-critic system. The user's broader RL hub in the multi-hub architecture is also trained with PPO. Every claim about the trainability of a recurrent attention controller in the user's program depends on PPO's ability to (a) tolerate the high-variance gradients of long-horizon recurrent rollouts, (b) bound the policy update so that the recurrent state distribution does not shift catastrophically between data-collection epochs, and (c) couple cleanly with a learned value baseline used in GAE. Reading PPO carefully also fixes the vocabulary — clip ratio, advantage estimate, KL drift, value-function coefficient, entropy bonus — that recurs in every published RL-trained vision-attention model the database tracks.

## 3. Key claims

1. A clipped probability-ratio surrogate objective $L^{CLIP}$ provides a first-order approximation to TRPO's trust region without computing the Fisher–KL constraint explicitly.
2. The clipped objective is a pessimistic (lower) bound on the unclipped surrogate, so optimizing $L^{CLIP}$ for multiple epochs on the same batch will not push the policy past the trust region in directions that hurt the bound.
3. The same on-policy data can be reused for several epochs of minibatch SGD without destabilizing training, which sharply improves sample efficiency over single-update methods like A2C.
4. Generalized Advantage Estimation (GAE, $\lambda$) is the standard advantage estimator for PPO and supplies the bias–variance trade-off that makes the clipped objective well-behaved over long rollouts.
5. A joint loss combining the clipped surrogate, a squared-error value loss, and an entropy bonus is sufficient to train policy and value networks end-to-end with shared parameters.
6. On MuJoCo and Atari benchmarks, PPO matches or beats TRPO, A2C, and ACER on sample complexity and final performance, with far simpler hyperparameter tuning.

## 4. Methods

**The probability ratio.** Define $r_t(\theta) = \pi_\theta(a_t \mid s_t) / \pi_{\theta_\text{old}}(a_t \mid s_t)$, the importance ratio between the current and rollout-time policies. The unclipped surrogate is $L^{CPI}(\theta) = \hat{\mathbb{E}}_t[r_t(\theta)\,\hat A_t]$ (conservative policy iteration; Kakade & Langford 2002).

**The clipped surrogate.** PPO-Clip replaces $L^{CPI}$ with

$$
L^{CLIP}(\theta) = \hat{\mathbb{E}}_t\Big[\min\big(r_t(\theta)\,\hat A_t,\; \mathrm{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\,\hat A_t\big)\Big]
$$

with $\epsilon \approx 0.2$. The min over the clipped and unclipped product ensures that improvements outside the $[1-\epsilon, 1+\epsilon]$ band are not rewarded; deteriorations inside the band are. This is asymmetric by design: positive advantages can pull the ratio up only to $1+\epsilon$, negative advantages down only to $1-\epsilon$.

**Adaptive KL penalty (alternative).** PPO-KL uses $L^{KL}(\theta) = \hat{\mathbb{E}}_t[r_t(\theta) \hat A_t - \beta\,\mathrm{KL}[\pi_{\theta_\text{old}}(\cdot \mid s_t),\,\pi_\theta(\cdot \mid s_t)]]$, where $\beta$ is updated after each rollout: doubled if the empirical KL exceeds $1.5\,d_\text{target}$, halved if below $d_\text{target}/1.5$. PPO-Clip is reported to outperform PPO-KL across both benchmarks and is the de facto standard.

**Advantage estimation (GAE).** Advantages are computed by GAE($\lambda$): $\hat A_t = \sum_{l=0}^{T-t-1} (\gamma\lambda)^l\,\delta_{t+l}$ with TD residual $\delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)$ and typical $\gamma \approx 0.99$, $\lambda \approx 0.95$. The truncated form (finite horizon $T$) is used for fixed-length rollouts.

**Joint loss.** Policy and value networks usually share parameters in Atari (shared CNN trunk with policy and value heads); on MuJoCo they are often disjoint MLPs. The training objective per step is

$$
L_t^{CLIP+VF+S}(\theta) = \hat{\mathbb{E}}_t\big[L_t^{CLIP}(\theta) - c_1\,L_t^{VF}(\theta) + c_2\,S[\pi_\theta](s_t)\big]
$$

with squared-error value loss $L_t^{VF} = (V_\theta(s_t) - V_t^\text{targ})^2$, entropy bonus $S$, and typical coefficients $c_1 \approx 1.0$, $c_2 \approx 0.01$.

**Algorithm loop.** (i) Run $N$ parallel actors for $T$ steps with $\pi_{\theta_\text{old}}$ to collect $NT$ transitions; (ii) compute $\hat A_t$ via GAE using the current value function; (iii) optimize $L^{CLIP+VF+S}$ for $K$ epochs of minibatch SGD over the buffer; (iv) replace $\theta_\text{old} \leftarrow \theta$ and repeat. Typical $N \in \{8, 32\}$, $T \in \{128, 2048\}$, $K \in \{3, 10\}$ epochs, minibatch size $\in \{32, 64, 256\}$, Adam learning rate $\sim 3 \times 10^{-4}$.

## 5. Results

**MuJoCo (1M environment steps, 7 continuous-control tasks).** PPO-Clip ($\epsilon=0.2$) matches or beats TRPO on every task and outperforms PPO-KL and A2C uniformly. On HalfCheetah, Walker2d, and Hopper, PPO-Clip reaches the asymptotic TRPO performance in roughly half the samples. PPO-Clip with $\epsilon=0.2$ outperforms variants with $\epsilon \in \{0.1, 0.3\}$ on average across the task suite.

**Atari (10M frames per game, 49 games).** PPO outperforms A2C on a strong majority of games and is competitive with ACER while being substantially simpler. PPO has the best mean and median normalized scores in head-to-head with A2C and ACER under matched compute. The Atari training uses the Nature-DQN CNN trunk with shared policy/value heads, 8 parallel actors, $T = 128$, $K = 3$ epochs, minibatch 256, learning-rate annealing.

**Sample-efficiency ablation.** $K = 1$ epoch per rollout (i.e., no data reuse) is significantly worse than $K \in [3, 10]$; large $K$ without clipping diverges. The clipping is therefore the load-bearing mechanism that makes multi-epoch updates safe.

**Hyperparameter robustness.** PPO-Clip's performance varies smoothly with $\epsilon$, learning rate, and batch size. TRPO requires a per-task KL constraint that is harder to set; A2C is brittle to learning rate at long horizons.

## 6. Critique / limitations

PPO's clipping is a *heuristic*, not a principled trust region. The bound $L^{CLIP} \leq L^{CPI}$ holds, but there is no guarantee that successive PPO updates produce monotonic improvement in the true return — only that egregious ratio explosions are suppressed. Subsequent analytical work (Engstrom et al. 2020, *Implementation matters*) shows that much of PPO's published performance is attributable to engineering details — observation normalization, advantage normalization, value-clipping, learning-rate annealing, orthogonal initialization — rather than to the clipped objective alone. These details are essentially undocumented in the original paper; reimplementations must replicate them to match published numbers.

PPO is on-policy: every rollout must be discarded after $K$ epochs, which limits sample efficiency relative to off-policy methods (SAC, TD3) on continuous control. PPO is therefore not the right algorithm for the setting where environment interaction is the dominant cost.

PPO assumes the advantage estimator $\hat A_t$ is reliable. With short rollouts or a poorly trained value function, GAE($\lambda$) advantages are biased or noisy, and the clipped objective propagates that noise. For recurrent policies with truncated BPTT, the value bootstrapping at segment boundaries is a known source of bias that the paper does not address.

The paper provides only feedforward policy/value experiments. The interaction between PPO and recurrent state — the situation that matters for the Recurrent ViT and PRISM — is not characterized in the original paper and has been a subject of subsequent empirical work (Pleines et al. 2022; see §7).

The entropy bonus coefficient $c_2$ is a flat global constant; richer exploration schemes (parameter-space noise, distributional critics, intrinsic motivation) are entirely outside PPO's scope.

## 7. Connection to our work

PPO is the *training algorithm of the recurrent ViT and PRISM v1*, and the actor optimizer in PRISM v2. The clip-ratio objective, the GAE advantage estimator, and their interaction with recurrent state's gradient flow are therefore load-bearing for the whole architectural program.

**The clipped objective and the recurrent state.** In the Recurrent ViT (2502.10955) and in PRISM v1 (`Prism/docs/THESIS.md`), the policy at step $t$ is conditioned on a recurrent state $H_t$ (or $M_t$) produced by the previous step. The ratio $r_t(\theta) = \pi_\theta(a_t \mid s_t, H_t) / \pi_{\theta_\text{old}}(a_t \mid s_t, H_t)$ involves $H_t$ that *itself depends on $\theta$* through the recurrent dynamics. Clipping the ratio bounds how much each $H_t$-conditioned action distribution can shift per epoch, which is the only mechanism preventing the rollout's $H_t$ from going off-distribution after a few epochs of SGD. Without clipping, a recurrent policy diverges within one or two epochs because $H_t$ trajectories sampled under $\pi_{\theta_\text{old}}$ become arbitrarily unrepresentative of trajectories under the updated $\pi_\theta$. The clip ratio is the user's program's de facto state-distribution-shift regularizer.

**GAE and recurrent credit assignment.** GAE($\lambda$) is the advantage estimator for every PPO-trained model in the user's program. The $\lambda$ parameter sets how far the credit-assignment window reaches into the past via the recurrent state: low $\lambda$ relies on the value function $V_\theta(s_t, H_t)$ to absorb long-horizon credit, high $\lambda$ relies on the empirical return. For the recurrent ViT's change-detection task — where the relevant event may occur many steps before the action — high $\lambda$ ($\approx 0.95$) is essential. The value head must therefore be conditioned on $H_t$, which couples the value loss $L^{VF}$ to the recurrent state in the same way as the policy loss; both gradient signals flow back through the same $H_t$.

**Truncated BPTT and PPO's epoch loop.** PPO's $K$-epoch reuse of rollouts is in tension with truncated BPTT: the recurrent state at the start of each minibatch must be cached from the rollout collection step and *replayed*, not recomputed, because recomputing under the updated $\pi_\theta$ would change $H_t$ and break the ratio's importance-sampling interpretation. This is the standard "stored hidden state" implementation that Pleines et al. (2022, `pleines2022_recurrent_ppo`) systematize. PRISM v1's training loop follows this pattern; the user's RL hub does as well.

**Entropy bonus and the multi-hub competition.** In the multi-hub program (`research_db/concepts/multi_hub_multi_objective_system.md`), the RL hub trained by PPO competes with the VAE hub and MSI hub for control of the shared self-attention substrate. PPO's entropy bonus $c_2 S[\pi_\theta]$ acts as a regularizer on the RL hub's confidence — preventing it from prematurely locking the attention map into a low-entropy mode that the other hubs cannot perturb. The bonus is therefore *the architectural lever* by which the RL hub's competitive aggressiveness is tuned.

**PRISM v2's distributional Q-critic + PPO actor.** PRISM v2 (`PRISM_V2_PROPOSAL.md`) replaces the scalar value head with a distributional Q-critic but keeps a PPO-clip actor. The clip-ratio objective is applied to the actor exactly as in the original paper; the only change is that $\hat A_t$ is computed from the distributional Q rather than from GAE-over-V. This is an architectural variant the paper does not consider but is compatible with the clip mechanism, because the clip bound depends only on the ratio and the *sign and magnitude* of $\hat A_t$.

**Recurrent ViT, §RL training.** The recurrent ViT paper trains the change-detection actor with PPO using the same clip $\epsilon = 0.2$, GAE $\lambda = 0.95$, and entropy coefficient roughly $0.01$ as the original PPO MuJoCo settings. This is essentially a transplant of the PPO recipe onto a recurrent ViT backbone; the success of the transplant is empirical evidence that PPO's clip mechanism extends to recurrent vision architectures without modification.

## 8. Citations to follow

- `schulman2015_trpo` — TRPO, the trust-region predecessor PPO approximates. Not in seed; high priority.
- `schulman2016_gae` — GAE, the advantage estimator PPO uses. In seed; should be deepened.
- `kakade_langford2002_cpi` — conservative policy iteration, the source of $L^{CPI}$. Not in seed.
- `mnih2016_a3c` — A3C / A2C, the main on-policy baseline. In seed, full depth.
- `wang2016_acer` — ACER, the off-policy baseline. Not in seed.
- `pleines2022_recurrent_ppo` — best-practices for PPO with recurrent policies; directly relevant to the user's program. In seed.
- `engstrom2020_implementation_matters` — the empirical audit of which PPO details actually matter. Not in seed; high priority.
- `andrychowicz2021_what_matters_onpolicy` — large-scale on-policy ablation. Not in seed.
