---
id: ha_schmidhuber2018_world_models
title: "World Models"
authors:
  - "Ha, David"
  - "Schmidhuber, Jürgen"
year: 2018
venue: "NeurIPS"
doi: ""
arxiv: "1803.10122"
url: "https://arxiv.org/abs/1803.10122"
tags:
  - deep-learning
  - reinforcement-learning
  - world-models
  - self-supervised-learning
concepts:
  - coupled-rnn-controller-model
  - world-model-emergence
  - coupled-rnn-world-models
related:
  - schmidhuber2015_learn_to_think
  - hafner2020_dreamer
  - bardes2023_vjepa
  - lecun2022_path_to_agi
relevance_to:
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-16"
---

# World Models

## 1. Abstract

The paper presents a generative neural-network model for reinforcement-learning environments. The system has three components: a Variational Autoencoder (V) for compressing visual observations into low-dimensional latent variables; a recurrent mixture-density network (M, the MDN-RNN) for modeling the time-evolution of those latents conditioned on actions; and a compact linear Controller (C) mapping latent + memory state to actions. The C is trained via evolutionary search (CMA-ES) *entirely inside the learned world model's hallucinated dream* — never touching the real environment after the initial V and M training. The resulting policy is then evaluated zero-shot on the real environment. The system achieves competitive performance on the OpenAI Gym car-racing task (CarRacing-v0) and on VizDoom (a first-person shooter benchmark). The paper is the founding empirical demonstration that a controller can be trained efficiently entirely inside a learned world model and transfer to the real environment.

## 2. Why this matters for us

Ha & Schmidhuber 2018 is the first empirical instantiation of Schmidhuber 2015's C–M framework ([schmidhuber2015_learn_to_think](research_db/papers/schmidhuber2015_learn_to_think.md)) — the lineage that the user's multi-hub multi-objective system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) generalizes. It establishes that a *modular* coupled-RNN architecture (vision + memory + controller, each trained separately on different objectives) can produce competitive RL performance. The paper is the load-bearing reference for treating multi-component architectures with hub-specific objectives as a viable research direction, rather than as a theoretical convenience.

## 3. Key claims

1. A generative world model can be learned from random-policy exploration of an environment. No reward signal is required during world-model training — just observations and actions.
2. The world model can be *decomposed* into a *spatial* compression (VAE) and a *temporal* model (MDN-RNN). The decomposition is computationally clean and biologically suggestive (perceptual encoding vs sequence modeling).
3. A simple Controller can be trained *entirely inside the dream* — running CMA-ES on policy parameters using only the learned world model's predictions — and transfer the resulting policy to the real environment with high performance.
4. The Controller is *small* (linear, hundreds of parameters) relative to the world model (millions of parameters). The architecture concentrates learning capacity in the world model; the policy is a thin layer on top.
5. The framework subsumes earlier model-based RL approaches and connects to predictive-coding / hierarchical-generative-model frameworks: V learns a compressed sensory representation, M learns a predictive temporal model on top.
6. The framework is **architectural advice**: separate environment-modelling from policy-learning; learn the environment model from observation alone; train the policy in the dream.

## 4. Methods

**V (Vision).** A VAE trained on random-rollout observations from the environment. The encoder maps high-dimensional pixel observations $o_t$ to low-dimensional latent variables $z_t$; the decoder reconstructs pixel observations from $z_t$. The VAE objective is the standard ELBO. After V is trained, the encoder is used to extract $z_t$ from observations; the decoder is used to generate dream observations.

**M (Memory).** A recurrent mixture-density network (MDN-RNN) trained on sequences $(z_t, a_t) \mapsto z_{t+1}$. The output of M is a probability distribution over the next latent $z_{t+1}$, parameterized as a mixture of Gaussians. M is trained by maximum-likelihood on the rollouts collected with the random policy.

**C (Controller).** A small linear policy $\pi: (z_t, h_t) \to a_t$, where $h_t$ is M's hidden state. C has only ~1000 parameters for the car-racing task.

**Training C in the dream.** CMA-ES is run on C's parameters using *only the world model* to simulate rollouts. The controller takes $z_t$ from the dream, produces an action $a_t$, feeds it back to M which produces $z_{t+1}$; the dream proceeds. A learned reward predictor (auxiliary head on M) gives the reward signal. CMA-ES optimizes C's parameters to maximize predicted dream reward.

**Transfer to real environment.** After training, the C is evaluated zero-shot on the real environment by feeding real observations through V (to get $z_t$), then computing $a_t = C(z_t, h_t)$ where $h_t$ is M's hidden state given the actual sequence of $z_t$'s.

## 5. Results

The principal quantitative findings:

- **CarRacing-v0.** The Ha-Schmidhuber agent achieves an average score of ≈900 over 100 random trials (the original benchmark threshold for "solved" is 900). This was the first reported solution to CarRacing-v0 at the time of publication.
- **VizDoom (TakeCover task).** The agent achieves competitive performance, surviving substantially longer than baseline methods.
- **Training efficiency.** The world model is trained from random rollouts (no reward used for V or M training). The controller training (CMA-ES inside the dream) requires only the learned model — no real environment interaction beyond the initial random-rollout collection.
- **Hallucination resilience.** When the M model produces inaccurate dream predictions, C can still learn a policy that transfers — the C does not need a perfect world model, just a useful one.
- **Component contribution.** Ablation studies show that the latent-space dimensionality (V) and the temporal-model capacity (M) both contribute to performance; the architecture works best with a coordinated choice of capacities.

## 6. Critique / limitations

The tasks are limited: car-racing (2D continuous control) and VizDoom (low-resolution first-person shooter). Generalization to richer environments (Atari, modern game environments, robotics) is not demonstrated in this paper. Subsequent work (PlaNet, Dreamer, MuZero) has scaled the approach to richer tasks; the 2018 paper is the proof-of-concept.

The CMA-ES training of C is evolutionary, not gradient-based. CMA-ES doesn't scale well to large controllers. Subsequent work (Dreamer, 2020) uses analytic value gradients through the world model — a more scalable training scheme.

The V (VAE) and M (MDN-RNN) are trained separately, not jointly. Joint training would in principle improve both components but is harder. Subsequent work (RSSM in PlaNet/Dreamer) trains V and M jointly with the variational structure built into M.

The world model is *deterministic in its temporal predictions*: the MDN gives a distribution over $z_{t+1}$ but the *evolution* is rolled out by sampling. Long-horizon rollouts compound errors; the paper handles this with the relatively short horizons of car-racing and VizDoom.

The framework is *modular by design*. Separating V, M, and C is conceptually clean but may be suboptimal — end-to-end joint training of the three components might produce better representations. Subsequent work has both approaches; the trade-off is unsettled.

The framework doesn't engage with the *competitive* multi-hub structure the user's program commits to. V, M, and C cooperate (each is used by the others without competition). The user's coalition-competition thesis would say that competitive coupling produces fundamentally different (and better) world-model emergence ([world_model_emergence](research_db/concepts/world_model_emergence.md)).

## 7. Connection to our work

This paper is the foundational empirical reference for the user's multi-hub program:

**The C–M architectural separation is in PRISM v1.** PRISM v1 ([Prism/docs/THESIS.md](Prism/docs/THESIS.md)) has a structural analog of V (the V1 stem and feature encoder), M (the generative decoder and recurrent state), and C (the actor-critic policy). The architectural commitment to separate world-modelling from policy-learning is the Ha-Schmidhuber commitment. This is the strongest published precedent for PRISM's design.

**Training in the dream as a future direction.** The user's program does *not* currently train policies inside a learned world model. PRISM v1 trains actor-critic via PPO with real-environment interaction. A future PRISM v2 or v3 could adopt the Ha-Schmidhuber training scheme: train V and M from observation, then train C inside the dream. This would be a substantial change but the architectural compatibility is straightforward.

**The MDN-RNN as the slow-memory prediction substrate.** Ha-Schmidhuber's M is an LSTM with a mixture-density output head, modeling the distribution over next latents. PRISM v2's slow memory is similar in spirit but has no explicit predictive output. Adding a predictive output to PRISM v2's slow memory would make it more Ha-Schmidhuber-like and would give it an explicit world-model role.

**Multi-hub generalization of V, M, C.** The user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) generalizes Ha-Schmidhuber from three modules (V, M, C) to three or more hubs (MSI, RL, VAE), with the critical addition that the hubs *compete* for control of a shared self-attention substrate. The Ha-Schmidhuber architecture is therefore a *cooperative* special case of the user's competitive multi-hub design.

**Emergent world models without explicit training.** The user's world-model-emergence prediction ([world_model_emergence](research_db/concepts/world_model_emergence.md)) is that a world model should emerge from multi-hub competition *without* explicit M training. Ha-Schmidhuber explicitly trains M; the user's program predicts that this explicit training is unnecessary if the competition pressure is right. This is the key theoretical extension over Ha-Schmidhuber.

The recurrent ViT paper doesn't cite Ha-Schmidhuber. PRISM v1 implicitly inherits the architectural separation. Future manuscripts on the multi-hub system should cite Ha & Schmidhuber 2018 as the founding empirical instantiation of the coupled-RNN-world-model paradigm the user's program generalizes.

## 8. Citations to follow

- `schmidhuber2015_learn_to_think` — the conceptual ancestor. In seed, full depth.
- `hafner2020_dreamer` — the scaled-up modern descendant. In seed, full depth.
- `hafner2019_planet` — PlaNet, the latent-planning predecessor of Dreamer. Not in seed.
- `bardes2023_vjepa` — V-JEPA, latent-prediction self-supervised world model. In seed, full depth.
- `lecun2022_path_to_agi` — LeCun's JEPA position paper. In seed.
- `kim2020_recurrent_world_models` — extension of Ha-Schmidhuber with attention. Not in seed.
- `schrittwieser2020_muzero` — MuZero, model-based RL without explicit world-model loss. Not in seed.
