---
id: springenberg2024_offline_actor_critic
title: "Offline actor-critic reinforcement learning scales to large models"
authors:
  - "Springenberg, Jost Tobias"
  - "Abdolmaleki, Abbas"
  - "Zhang, Jingwei"
  - "et al."
year: 2024
venue: "ICML"
doi: ""
arxiv: "2402.05546"
url: "https://arxiv.org/abs/2402.05546"
tags:
  - reinforcement-learning
  - deep-learning
  - transformers
concepts:
  - actor-critic
  - cross-attention
  - self-attention-over-tokens
related:
  - schulman2016_gae
  - schulman2017_ppo
  - mnih2016_a3c
  - pleines2022_recurrent_ppo
  - ha_schmidhuber2018_world_models
  - hafner2020_dreamer
  - sutton_barto2018_rl_intro
  - herman_krauzlis2017_sc_change_detection
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_126
status: full
depth: full
last_updated: "2026-05-16"
---

# Offline actor-critic reinforcement learning scales to large models

## 1. Abstract

The authors show that offline actor-critic reinforcement learning scales to large transformer-based models — exhibiting scaling laws similar to those of supervised learning — and outperforms strong behavioral-cloning baselines on a broad multi-task continuous-control suite. They introduce the Perceiver-Actor-Critic (PAC), a Perceiver-IO-style architecture for multi-task control in which a small set of learned latent tokens cross-attends to heterogeneous proprioceptive, visual, and language-conditioning inputs and then self-attends to produce both an MPO-style policy and a Q-critic. Trained on a heterogeneous corpus covering 132 continuous-control tasks (DeepMind Control Suite, Meta-World, locomotion, and a real bi-manual manipulation set) with mixed expert and sub-optimal trajectories, PAC matches or beats behavioral-cloning at every scale tested and continues to improve as parameters, data, and compute grow — including in regimes where additional sub-optimal data hurts behavioral cloning. The authors argue that this is the first demonstration that an off-policy *value-based* training signal can be the load-bearing objective for a large multi-task control transformer, opening a route to "large foundation models for control" trained from logged behavioral data without an online environment loop.

## 2. Why this matters for us

This paper supplies the *training paradigm* that closes the RL cluster around the user's program. The Recurrent ViT (2502.10955), PRISM v1, and PRISM v2 are all currently trained with online PPO+GAE (`schulman2017_ppo`, `schulman2016_gae`, `pleines2022_recurrent_ppo`) — a regime that requires an interactive change-detection environment. Offline actor-critic at the scale demonstrated here means a recurrent ViT could instead be initialized on a behavioral *dataset* — e.g., monkey or human fixation traces during change-detection (Krauzlis lab data, `herman_krauzlis2017_sc_change_detection`) — and then optionally fine-tuned online. The pipeline becomes *behavior policy logged in the lab → offline AC pretraining → online PPO fine-tune*. This is the only practical way to give a sufficiently large recurrent ViT enough RL experience to learn a competent attention controller, since the lab-task environment generates orders of magnitude fewer samples per wall-clock hour than a parallel MuJoCo cluster. The paper also matters architecturally: its Perceiver-based actor-critic is a direct demonstration that cross-attention over heterogeneous inputs (an instance of the user's Feedback Transformer in spirit, if not in detail) scales as the load-bearing primitive of a large RL agent.

## 3. Key claims

1. Offline actor-critic RL exhibits power-law scaling in parameters and compute that is qualitatively indistinguishable from supervised-learning scaling laws on the same control corpus.
2. Behavioral cloning saturates and then degrades when additional sub-optimal data is added to the training set; offline actor-critic continues to improve, because the value-function critic re-weights the learning signal toward higher-return actions.
3. A Perceiver-IO actor-critic, with a small number of learned latent tokens cross-attending to heterogeneous per-modality input embeddings, is a strictly better architecture for multi-task control than a flat MLP or a vanilla transformer over a per-step token sequence — at every parameter count tested.
4. The same architecture, with the same offline-AC objective and the same hyperparameters, trains across all 132 tasks of a heterogeneous multi-domain corpus (DM Control, Meta-World, locomotion, bi-manual robot manipulation) — i.e., a single multi-task control "foundation model" is feasible from purely offline data.
5. Self- *and* cross-attention are both load-bearing: ablating cross-attention to inputs or self-attention among latents each costs roughly half the performance gap to behavioral cloning.
6. The MPO-style policy update is critical to the scaling story; naively imitating the data with a return-weighted regression baseline (à la AWR) trains stably but plateaus earlier, suggesting that the *explicit* actor-critic structure with a learned Q is what carries the additional bits of behavioral signal at scale.
7. Offline AC can train on data generated by an in-progress version of itself ("self-generated data") and continue to improve — i.e., the offline-online distinction is softened into a *batch-iterated* training loop rather than a strict offline-only pipeline.

## 4. Methods

**Algorithmic skeleton.** Offline actor-critic in the MPO / V-MPO family (Abdolmaleki et al. 2018, Song et al. 2020), with a learned Q-function $Q_\phi(s, a)$ trained by TD regression on logged transitions, and a policy $\pi_\theta(a \mid s)$ trained to maximize the expected $Q$ under a KL constraint to the previous policy. The policy update is the standard MPO closed-form
$$
\pi_\text{target}(a \mid s) \propto \pi_{\theta_\text{old}}(a \mid s) \exp\!\big(Q_\phi(s, a) / \eta\big)
$$
with $\eta$ tuned by a dual variable to enforce $D_\text{KL}(\pi_{\theta_\text{old}} \,\|\, \pi_\theta) \leq \epsilon$. The actor's supervised target is the temperature-weighted action distribution induced by the current critic, so the gradient is a weighted log-likelihood rather than a REINFORCE estimator — which is what makes the method viable in the offline regime, where any high-variance importance-sampled estimator would diverge. The critic is regressed against a Retrace($\lambda$) target computed on the logged trajectories.

**Architecture (Perceiver-Actor-Critic, PAC).** A Perceiver-IO encoder maintains a small set ($\sim$256) of *latent* tokens. At each step, modality-specific input embeddings (joint angles, end-effector pose, RGB image patches, language instruction tokens, prior action) are concatenated into a long input sequence; the latents cross-attend to the input sequence over several layers, then self-attend among themselves, then optionally cross-attend again. Two output heads — a Gaussian policy head and a Q-value head — read out from the latents. Cross-attention compresses the heterogeneous input into a fixed-size latent bank; the latents themselves carry the agent's "working memory" of the current observation. Parameters scale primarily by widening the latents and stacking more self-attention layers; the input-side cross-attention has cost linear in input length and fixed in latent count, which is what makes the per-step cost manageable as the input modality count grows.

**Training corpus.** 132 continuous-control tasks across DeepMind Control Suite, Meta-World, locomotion benchmarks, and an in-house real-robot bi-manual manipulation set. Each task contributes a mixture of expert demonstrations (when available) and sub-optimal exploratory trajectories from training-in-progress agents. Total corpus size on the order of $10^9$ environment steps. No online environment interaction during training of the reported runs.

**Scaling sweep.** Models from $\sim$5M to several-hundred-million parameters, with compute, data, and parameter count varied along the standard Chinchilla-style axes. Loss curves are fit with power laws in compute and in parameters, and the resulting exponents are reported alongside the corresponding fits for a behavioral-cloning model trained on the same data.

**Evaluation.** Held-out task performance, multi-task average return normalized to expert-data returns, and sample-efficiency comparisons against per-task online baselines (D4PG, MPO) and offline baselines (CRR, AWAC, BC).

## 5. Results

**Scaling.** Offline AC loss decreases as a power law in compute with an exponent comparable to that of behavioral cloning on the same data; offline AC's *return* (the quantity that actually matters) decreases more sharply with compute because the critic-weighted update extracts more signal per step than the cloning loss. At the largest scale tested, PAC reaches roughly 70–80% of expert return averaged across the 132-task suite; behavioral cloning saturates around 50% at the same scale.

**Mixed-quality data.** When sub-optimal trajectories are added to the training set, behavioral cloning's normalized return *decreases* (it imitates the average behavior, including the bad behavior). PAC's return *increases* monotonically with additional sub-optimal data — the critic identifies and up-weights the high-return slices. This is the headline qualitative result.

**Real robot bi-manual manipulation.** PAC trained offline on logged real-robot data solves bi-manual tasks (e.g., placing a small object into a container held by the other arm) that behavioral cloning on the same data fails to reliably solve, with no online robot interaction during training.

**Architecture ablations.** Removing cross-attention (i.e., concatenating all modalities into a flat token sequence read directly by a standard transformer) costs $\sim$10–15 points of normalized return; removing self-attention among latents costs roughly the same. Single-modality projection MLPs in place of cross-attention is the worst-performing ablation.

**Algorithm ablations.** Replacing MPO with AWR (advantage-weighted regression) costs $\sim$5–10 points of normalized return at the largest scale and plateaus earlier; replacing it with pure behavioral cloning costs $\sim$20–30 points and the gap widens with scale. Removing the critic entirely (i.e., supervised imitation only) reproduces the BC curve.

**Self-generated data.** Iterating the PAC training loop on data sampled from the previous-iteration PAC policy continues to improve return, suggesting a viable "batch RL flywheel" without true online interaction.

## 6. Critique / limitations

The paper does not characterize the *off-policy bias* of the Retrace($\lambda$) critic target when the behavior policy is a heterogeneous mixture of dozens of partially-trained policies plus human demonstrations. Retrace assumes a known or estimable behavior likelihood; in practice this is approximated, and the resulting bias is unquantified.

The scaling fits are at relatively modest sizes by 2024 transformer standards (peak runs are smaller than typical language-model pretraining). Whether the offline-AC scaling exponents continue to track supervised-learning exponents at, say, billion-parameter scale is an open empirical question that the paper does not settle.

The "outperforms behavioral cloning at every scale" claim is sensitive to the *quality* of the cloning baseline. The authors use a standard transformer BC; more sophisticated baselines such as Decision Transformers (Chen et al. 2021), trajectory transformers (Janner et al. 2021), or Diffusion-Policy (Chi et al. 2023) are not compared head-to-head at the same scale on the same corpus. Those baselines also use return-conditioning and could close some of the gap.

The architecture-versus-algorithm decomposition is partially confounded: the BC baseline shares the same Perceiver-IO architecture, but the *training data composition* used for the multi-task results is one that BC is known to handle poorly (mixed-quality demonstrations). On a clean expert-only corpus, BC may be more competitive — but expert-only datasets are not what the "scaling to logged data" pitch is really about, so the paper's framing is consistent.

The method requires a value-function bootstrap target, which means $\gamma$, the Retrace $\lambda$, and the KL constraint $\epsilon$ must all be tuned per task family in practice. The paper reports a single set of hyperparameters that works across the 132-task suite, but does not show how performance degrades as the multi-task corpus becomes more heterogeneous (e.g., adding a navigation or visual-search domain).

Real-robot results are reported on a single in-house manipulation platform; cross-platform generalization (a different robot, a different camera setup) is not demonstrated. This is the gap that subsequent work (RT-2, OpenVLA, $\pi_0$) explicitly targets.

The offline-AC framing inherits the standard MPO assumption of approximate KL control of the policy update — but with a large transformer policy, the per-token KL is hard to control tightly. The paper handles this with a dual variable but does not show the dual's trajectory or evidence that the constraint is binding at all scales.

## 7. Connection to our work

This paper is the *training-paradigm closure* of the RL cluster around the user's architectural program, and the immediate practical implication is a viable end-to-end recipe for the recurrent ViT.

**The offline-online pipeline.** The published Recurrent ViT (2502.10955), PRISM v1, and PRISM v2 all train with online PPO+GAE (`schulman2017_ppo`, `schulman2016_gae`, `pleines2022_recurrent_ppo`). Online RL is sample-hungry: a 200M-parameter ViT needs $\sim$$10^7$–$10^8$ task-relevant environment steps, which is feasible in a parallelized synthetic change-detection environment but *not* in a real lab task with finite primate or human behavioral data. Offline AC inverts the problem: train the actor-critic on logged behavioral data (`herman_krauzlis2017_sc_change_detection` would be the natural source for Krauzlis-lab style change-detection), then optionally fine-tune online if cheap simulation is available. The pipeline becomes *lab-collected behavior policy → offline AC pretraining (MPO + Q via Retrace) → optional online PPO/A2C fine-tune* — a viable training recipe for a recurrent ViT at a size that online-only training would not support.

**Connection to PRISM v2's distributional critic.** The Recurrent ViT and PRISM v2 use a scalar value head; PRISM v2's design also entertains a *distributional* critic (`bellemare2017_distributional_rl`-style). PAC uses a scalar Q-head and reports that MPO works at scale, but the algorithm is agnostic to the critic's parameterization. A natural future direction is *distributional offline MPO* — drop a distributional Q-head into PAC, keep the closed-form policy update, and pre-train on the same lab data. The user's RL hub would then be a distributional-MPO actor-critic with offline-pretraining capability and online-fine-tuning capability — a strict superset of the current PPO+GAE setup.

**Cross-attention as Feedback Transformer.** PAC's Perceiver-IO encoder cross-attends from a small bank of latent tokens to a heterogeneous input sequence. This is a structurally simple instance of the user's Feedback Transformer (`feedback-transformer`): the latents play the role of recurrent memory tokens, the inputs play the role of bottom-up sensory tokens, and the cross-attention is the inter-source integration step. The user's full Feedback Transformer is more expressive — it integrates *many* feedback sources via per-source Q/K/V projections and elementwise broadcasting — but PAC demonstrates that even the restricted "single bank of latents cross-attending to one heterogeneous input sequence" version scales to multi-task control at $\sim$10$^8$ parameters with stable training. This is empirical evidence that the Feedback Transformer's basic structural commitment (latents that cross-attend rather than concatenate-and-self-attend) is the right scaling primitive for RL agents at the scales the user's program contemplates.

**Multi-hub competition and the offline corpus.** The multi-hub system (`multi_hub_multi_objective_system`) trains an RL hub, a VAE hub, and an MSI hub competing for self-attention. The RL hub's training signal in the current design is online PPO+GAE; if PAC-style offline AC replaces this, the RL hub's data corpus can be *the same corpus* that the VAE hub is reconstructing from (e.g., a video dataset with logged eye fixations as the action stream). Both hubs then consume the same data but extract different signal — the VAE hub learns generative reconstruction, the RL hub learns value-weighted action prediction — and they compete for representational bandwidth in the shared self-attention substrate. This is a strictly cleaner training-data story than the current online-PPO-for-RL / offline-data-for-VAE asymmetry.

**Connection to world models.** The world-model lineage (`ha_schmidhuber2018_world_models`, `hafner2020_dreamer`) trains an explicit generative model of the environment and runs an actor-critic *inside* the model. PAC sits in a different part of design space: no explicit model, just a critic trained from logged data. Both are viable for the user's program — Dreamer's "imagined rollouts" align naturally with the iterative-VAE encoder-decoder's $n_{FR} \to n_{BR}$ structure (`iterative-variational-encoder-decoder`), while PAC's pure-offline-AC approach aligns naturally with the multi-hub program's "everything consumes the same logged corpus" data strategy. The choice between them is an architectural commitment, not a forced move; the user's program admits both and may eventually want both (a world-model-based actor with a PAC-style offline-AC pretraining warm-start).

**The recurrent-state question.** PAC is *feedforward* per step in the sense that the Perceiver latents are reset between steps and re-derived from the input; there is no persistent latent recurrence. This is the part of PAC that the user's program would change first: replace the per-step-reset latent bank with a *persistent recurrent latent state* (a GridCell RNN bank in the user's terminology), updated by gating between the previous-step latents and the current cross-attention output. The result is a *recurrent* Perceiver-Actor-Critic — structurally a candidate architecture for the recurrent ViT trained with offline MPO. This is the most concrete near-term variant of the user's program that PAC enables.

**The seeding role.** Stub frontmatter listed only `recurrent_vit` as the relevance hook; the appropriate addition is `prism_v2`, since PRISM v2's actor is the most likely point of integration for an offline-AC training recipe (PRISM v1 has the prediction-error-driven attention controller that is harder to retrofit to a value-based offline update).

## 8. Citations to follow

- `abdolmaleki2018_mpo` — Maximum a Posteriori Policy Optimization, the algorithmic ancestor of PAC's policy update. Not in seed; high priority for the offline-AC cluster.
- `song2019_vmpo` — V-MPO, the value-function variant of MPO; the closest direct predecessor for large-scale on-policy applications. Not in seed.
- `wang2020_crr` — Critic-Regularized Regression, an offline-AC baseline PAC is compared against. Not in seed.
- `nair2020_awac` — Advantage-Weighted Actor-Critic, another offline-AC baseline. Not in seed.
- `kumar2020_cql` — Conservative Q-Learning, the standard offline-RL regularizer; PAC's relationship to CQL-style critic regularization is implicit. Not in seed.
- `jaegle2021_perceiver_io` — Perceiver-IO, the architectural ancestor of PAC's encoder. Not in seed; high priority for the architecture cluster.
- `munos2016_retrace` — Retrace($\lambda$), the off-policy critic target used in PAC. Not in seed; conceptual ancestor of GAE for off-policy settings.
- `kostrikov2021_iql` — Implicit Q-Learning, another offline-AC variant; head-to-head comparison would clarify PAC's algorithmic-vs-architectural advantage. Not in seed.
- `chen2021_decision_transformer` — Decision Transformer, the return-conditioned-BC baseline PAC argues against. Not in seed; obvious cluster-mate.
- `janner2021_trajectory_transformer` — Trajectory Transformer, another return-conditioned offline-RL transformer. Not in seed.
- `chi2023_diffusion_policy` — Diffusion Policy, a strong BC-style baseline at scale. Not in seed.
- `brohan2023_rt2` — RT-2, the cross-platform robot foundation model that supersedes PAC's single-platform demonstration. Not in seed.
- `kim2024_openvla` — OpenVLA, open-source large-scale offline robot policy training. Not in seed.
- `reed2022_gato` — Gato, the multi-task transformer-policy predecessor at DeepMind. Not in seed.
