---
id: world_model_emergence
type: concept
title: "Emergence of a world model from inter-hub competition"
papers:
  - schmidhuber2015_learn_to_think
  - ha_schmidhuber2018_world_models
  - hafner2020_dreamer
  - bardes2023_vjepa
  - lecun2022_path_to_agi
  - mante2013_context_dependent_pfc
  - desimone_duncan1995_biased_competition
source_documents:
  - "Private & Shared-4/Evolution of Architecture (§ Predictive Coding from Competition, empirical-test paragraph)"
last_updated: "2026-05-18"
---

# Emergence of a world model from inter-hub competition

## Definition

A falsifiable empirical prediction of the user's coalition-competition theory: if a multi-hub multi-objective system (`concepts/multi_hub_multi_objective_system.md`) is trained on tasks that put the hubs' objectives in productive conflict, *no hub is given an explicit world-model training signal*, and yet at the end of training a separate decoder trained to predict the system's global internal state at $t+1$ from the global state at $t$ achieves long-range coherent prediction of those internal states. That coherent multi-step prediction is the operational signature of a world model. If observed, it constitutes evidence that the competition pressure between hubs is sufficient to produce predictive-coding-like dynamics — predictive coding emerges from competition, rather than being installed by an explicit objective.

## The empirical test in detail

**Training phase.** Three-hub system (MSI + RL + VAE; `concepts/multi_hub_multi_objective_system.md`) is trained on a benchmark whose objective puts the hubs in conflict — e.g., a partially-observable reinforcement-learning task where the RL hub's policy benefits from one set of internal representations while the VAE hub's reconstruction benefits from a different set. Each hub's loss is its own native loss (PPO for RL, reconstruction ELBO for VAE, V-JEPA-style for MSI); no auxiliary world-model loss is added. Gradients flow only through each hub's own loss.

**Probing phase.** After training, freeze the multi-hub system. Train a fresh decoder $D$ (a separate network with its own parameters) to take the system's full internal state $S_t$ at time $t$ — concatenation of all hubs' memory states plus the central self-attention map — and predict $S_{t+1}$ as a regression target. The decoder is trained on rollouts of the frozen system in test environments.

**Test phase.** Iteratively roll out the decoder: starting from $S_t$, predict $\hat S_{t+1}$, then $\hat S_{t+2} = D(\hat S_{t+1})$, and so on for $k$ steps. Measure: (a) prediction accuracy at each step; (b) whether iterated rollouts produce trajectories that match the system's actual behavior when run forward from $S_t$; (c) whether the rollouts produce *coherent* trajectories (i.e., they stay on the manifold of plausible system states rather than diverging).

**Positive result.** If the decoder's $k$-step predictions remain accurate for large $k$ (say $k = 10$–$100$ steps), and the trajectories stay coherent, then a world model has emerged. The hubs' competition produced an internal representation that is forward-predictable, without any explicit forward-prediction loss.

**Negative result.** If the decoder fails — predictions diverge within 1–2 steps, or trajectories leave the manifold — then the competition pressure was not sufficient to produce predictive-coding dynamics in this architecture, and the user's theoretical claim is falsified for this particular instantiation.

## Why this is meaningful evidence for the competition-emergent-PC thesis

The decoder is *not part of the trained system*. Its predictions are based on the trained system's frozen internal states. If those states are forward-predictable, it must be because the system itself encoded predictability into its representations during training. The only source of pressure toward predictability in this experiment is the inter-hub competition: each hub had to predict its rivals' contributions to win attention weight, and the resulting hub-level predictions sum to an implicit global predictive model. The world-model emergence is therefore the experimental signature of the architectural-competition pressure.

## Relation to existing world-model literature

Ha & Schmidhuber 2018 (`papers/ha_schmidhuber2018_world_models.md`), Dreamer (`papers/hafner2020_dreamer.md`), and V-JEPA (`papers/bardes2023_vjepa.md`) all *explicitly* train a world model. The user's prediction is fundamentally different: a world model should emerge *without explicit training*, as a byproduct of inter-hub competition. If the multi-hub system can match Dreamer's world-model quality without ever being told to learn a world model, that is a substantial theoretical result.

LeCun's JEPA program (`papers/lecun2022_path_to_agi.md`) also commits to explicit world-model training but at the latent level rather than the pixel level. The user's program goes further by predicting that world-modelling capacity arises from the right architectural commitments and competition pressure, without any explicit forward-prediction loss at all.

## What this concept is *not*

This is *not* a claim that all neural networks develop world models. Specifically:

- A single-hub network trained on RL alone is unlikely to develop a coherent world model (consistent with the known difficulty of learning world models from pure reward).
- A two-hub cooperative system (Schmidhuber's C + M) develops a world model only because M is explicitly trained on prediction.
- The claim is specifically about *multi-hub competitive* systems with the right architectural substrate (Feedback Transformer central attention; per-hub memory; gradient flow through inter-hub Q/K manipulation).

## Connection to other concepts

- `coalition_resource_competition` — the theoretical foundation; this concept is its empirical-test prediction.
- `multi_hub_multi_objective_system` — the experimental architecture.
- `competition_emergent_predictive_coding` — the user's theoretical thesis; world-model emergence is the testable consequence.
- `feedback_transformer` — the architectural substrate that makes the competition possible.
- `coupled_rnn_world_models` — the contrast class. Ha & Schmidhuber, Dreamer, V-JEPA, and LeCun's JEPA all train an *explicit* world model; the user's competition-emergent prediction is that a coupled-RNN-like world model arises *without* an explicit world-model objective, as a byproduct of inter-hub competition. The lineage in `coupled_rnn_world_models` therefore supplies the baselines this concept's empirical test would be measured against.

## Open questions

1. **What counts as "coherent"?** Operationally, this requires defining a manifold of plausible system states; a rollout that leaves the manifold is incoherent. The manifold can be defined empirically (held-out forward-rollouts from the trained system) but the definition has free parameters.
2. **What is the right benchmark task?** A POMDP with both reward signals and reconstruction signals is the simplest; how to engineer hub conflict is unsettled.
3. **What's the failure mode if hub objectives don't conflict?** If MSI and RL agree on the right representations, the hubs cooperate without competition, and the world-model-emergence prediction may not hold. The right amount of inter-hub conflict for the prediction to bite is unsettled.
4. **Comparison baselines.** Even if the world model emerges, it may emerge less efficiently than in explicitly-trained baselines. The relevant baselines are Dreamer's world model quality at matched compute and parameter budget.
