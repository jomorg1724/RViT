---
id: coupled_rnn_world_models
type: concept
title: "Coupled-RNN world models"
papers:
  - schmidhuber2015_learn_to_think
  - ha_schmidhuber2018_world_models
  - hafner2020_dreamer
  - bardes2023_vjepa
  - lecun2022_path_to_agi
  - wang2025_hierarchical_reasoning_model
  - mante2013_context_dependent_pfc
  - mujika2017_fast_slow_rnn
source_documents:
  - "Private & Shared-4/Evolution of Architecture (§ A Schmidhuber Aside; § A General Purpose Multi-Objective System)"
last_updated: "2026-05-18"
---

# Coupled-RNN world models

## Definition

A family of architectures in which two (or more) recurrent neural networks are trained on different objectives, communicate via learned input/output channels, and jointly implement model-based reasoning or model-based reinforcement learning. The canonical structure is a **controller** $C$ trained on task reward and a **world model** $M$ trained on environment prediction (next-observation, latent prediction, reconstruction); $C$ uses $M$ as a queryable subroutine by feeding inputs into $M$ and reading outputs. Originally proposed by Schmidhuber 2015 (`papers/schmidhuber2015_learn_to_think.md`), first major empirical instantiation in Ha & Schmidhuber 2018 (`papers/ha_schmidhuber2018_world_models.md`), most influential modern instance in Dreamer (Hafner et al. 2020, `papers/hafner2020_dreamer.md`).

## The lineage

The architectural lineage runs:

| Year | Paper | Key contribution |
|---|---|---|
| 2015 | Schmidhuber, *On Learning to Think* | C–M conceptual framework; algorithmic-information-theory framing; "learning to query" |
| 2018 | Ha & Schmidhuber, *World Models* | First empirical instantiation: V (VAE) + M (MDN-RNN) + C (linear policy); CMA-ES inside M's dream |
| 2019 | Hafner et al., *PlaNet* | Latent-space planning via CEM in a learned RSSM |
| 2020 | Hafner et al., *Dreamer* | Actor-critic trained via analytic value gradients through the world model; outperforms model-free on continuous control |
| 2022 | LeCun, *Path to AGI* (`papers/lecun2022_path_to_agi.md`) | JEPA framework: world model predicts in latent space rather than pixels |
| 2023 | Bardes et al., *V-JEPA* (`papers/bardes2023_vjepa.md`) | Video-specific JEPA |
| 2025 | Wang et al., HRM (`papers/wang2025_hierarchical_reasoning_model.md`) | Coupled H/L modules with hierarchical convergence; not a world model per se but uses the coupled-RNN substrate for reasoning |

Sitting alongside the explicit world-model lineage is a parallel **coupled-RNN-without-world-model-loss** lineage that uses the same architectural primitive — two recurrent modules trained jointly, communicating through learned channels — but trained on supervised next-token prediction rather than environment dynamics. The canonical instance is Mujika et al. 2017's Fast-Slow RNN (`papers/mujika2017_fast_slow_rnn.md`), which couples a fast inner-loop RNN with a slow outer-loop RNN running at different effective timescales. The Fast-Slow RNN is conceptually the *un-objective-differentiated* sibling of Schmidhuber's C–M framework: both commit to the structural separation of two RNNs at different functional roles, but Fast-Slow RNN does not commit to an explicit world-model loss. The user's program's prediction that world-modelling capacity *emerges* from inter-hub competition (`concepts/world_model_emergence.md`) means architectures like Mujika's are direct points on the predicted spectrum: a coupled-RNN architecture that does not explicitly optimize world-model loss should still develop world-model-like internal dynamics if the competition pressure is right.

## What the user's program adds

The user's multi-hub multi-objective system (`concepts/multi_hub_multi_objective_system.md`) generalizes the two-hub C–M structure to many hubs (MSI + RL + VAE in the reference design) and adds **competition pressure** for control of a shared self-attention substrate. The architectural extensions over Schmidhuber 2015 are:

1. **More than two hubs.** Schmidhuber's framework is conceptually general but the canonical instantiation has C and M. The user's reference design has three.
2. **Shared self-attention substrate.** Schmidhuber's hubs communicate via direct querying. The user's hubs all feed into a central Feedback Transformer; the central attention map is the shared computational substrate that mediates all inter-hub communication.
3. **Competition rather than cooperation.** Schmidhuber's hubs cooperate. The user's hubs compete for control of the central attention map. The competition pressure is the source of the predictive-coding-like dynamics the user predicts (`concepts/coalition_resource_competition.md`).
4. **No explicit world-model training signal.** Schmidhuber's M is explicitly trained on next-step prediction. The user's prediction is that *no* hub needs an explicit world-model loss; world-modelling capacity emerges from inter-hub competition (`concepts/world_model_emergence.md`).

The user's program is therefore not just an extension of Schmidhuber 2015; it is a theoretical claim that the *cooperative* framing in Schmidhuber's framework misses the most important architectural driver in real cortex (competition for limited resources).

## The driver-vs-modulator analog

Sherman & Guillery's transthalamic-pathway framework (`concepts/cortico_thalamo_cortical_loops.md`) makes a distinction relevant to coupled-RNN architectures: feedforward transthalamic projections are *drivers* (strong, suprathreshold) and feedback transthalamic projections are *modulators* (small, subthreshold). The C–M analog: $M$'s output to $C$ is plausibly modulatory (informs $C$'s decisions without dictating them); $C$'s queries to $M$ are also modulatory (selecting which questions $M$ is asked rather than dictating $M$'s internal state). The user's Feedback Transformer's Hadamard-product structure captures this modulatory character (multiplicative gain rather than additive replacement).

## Why this concept is not the same as `multi_compartmental_memory`

Multi-compartmental memory (`concepts/multi_compartmental_memory.md`) commits to *multiple memory states at different spatial resolutions and timescales within a single hierarchy*. Coupled-RNN world models commit to *multiple architecturally-distinct RNNs trained on different objectives*. The two are orthogonal: a multi-compartmental memory could be all one hub; a multi-hub system could use single-state RNNs without spatial/temporal compartmentalization. The user's full architecture combines both: each hub has its own multi-compartmental memory, and the hubs are coupled at the central attention substrate.

## Connection to other concepts

- `multi_hub_multi_objective_system` — the multi-hub generalization of coupled-RNN world models.
- `world_model_emergence` — the prediction that the user's competitive variant produces an emergent world model.
- `coalition_resource_competition` — the theoretical pressure that distinguishes the user's program from Schmidhuber's cooperative framework.
- `slow_fast_recurrence` — HRM's coupling structure (a special case of coupled-RNN architecture with hierarchical convergence).
- `feedback_transformer` — the shared central substrate in the user's program.

## Open questions

1. **Is the cooperative framing wrong, or just incomplete?** Real systems likely have both cooperation and competition. The right architectural balance is unsettled.
2. **What is the minimum information transfer needed between hubs?** Schmidhuber's framework allows arbitrary querying. The user's program constrains communication to Q/K/V projections through the shared attention. Whether the constraint helps or hurts learning is open.
3. **JEPA-style latent prediction or pixel reconstruction?** LeCun's bet is on latent prediction; Ha & Schmidhuber used pixel reconstruction. The user's iterative VAE uses pixel reconstruction; the multi-hub system's MSI hub could use either. The trade-offs aren't yet clear.
4. **Scaling laws for coupled-RNN architectures.** Dreamer-style architectures have been scaled successfully; HRM's scaling behavior on inference-time compute is novel. Whether the user's multi-hub variant scales similarly is unsettled.
