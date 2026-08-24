---
id: banino2018_vector_navigation
title: "Vector-based navigation using grid-like representations in artificial agents"
authors:
  - "Banino, Andrea"
  - "Barry, Caswell"
  - "Uria, Benigno"
  - "Blundell, Charles"
  - "Lillicrap, Timothy"
  - "Mirowski, Piotr"
  - "Pritzel, Alexander"
  - "Chadwick, Martin J."
  - "Degris, Thomas"
  - "Modayil, Joseph"
  - "Wayne, Greg"
  - "Soyer, Hubert"
  - "Viola, Fabio"
  - "Zhang, Brian"
  - "Goroshin, Ross"
  - "Rabinowitz, Neil C."
  - "Pascanu, Razvan"
  - "Beattie, Charlie"
  - "Petersen, Stig"
  - "Sadik, Amir"
  - "Gaffney, Stephen"
  - "King, Helen"
  - "Kavukcuoglu, Koray"
  - "Hassabis, Demis"
  - "Hadsell, Raia"
  - "Kumaran, Dharshan"
year: 2018
venue: "Nature"
doi: "10.1038/s41586-018-0102-6"
arxiv: ""
url: "https://www.nature.com/articles/s41586-018-0102-6"
tags:
  - reinforcement-learning
  - grid-cells
  - navigation
  - hippocampus
  - emergent-representation
  - deep-learning
concepts:
  - gridcell_rnn
  - world_model_emergence
  - multi_compartmental_memory
  - hierarchical_predictive_coding
related:
  - okeefe_dostrovsky1971_hippocampal_map
  - hafting2005_grid_cells
  - whittington2020_tem
  - stachenfeld2017_predictive_map
  - behrens2018_cognitive_map
  - wayne2018_merlin
  - hafner2023_dreamerv3
  - lisman_grace2005_hippocampal_vta
relevance_to:
  - prism_v2
  - rvit_plus
seed_source:
  - manual_deep_dive_2026_05_23
status: full
depth: full
last_updated: "2026-05-23"
---

# Vector-based navigation using grid-like representations in artificial agents

## 1. Abstract

A clean verbatim abstract from the Nature paper is paywalled. The opening sentence ("Deep neural networks have achieved impressive successes in fields ranging from object recognition to complex games such as Go") is verbatim; the remainder is paraphrased composite of verified language from PubMed, DeepMind's blog post, and Google Research's publication page:

The authors note that deep neural networks have achieved impressive successes in fields ranging from object recognition to complex games such as Go, but navigation remains a substantial challenge for artificial agents — deep networks trained by reinforcement learning fail to rival mammalian spatial behaviour, which is underpinned by grid cells in the entorhinal cortex providing a multi-scale periodic metric for coding space. The authors train a recurrent network to perform path integration; in the trained network, units emerge with response patterns resembling grid cells (as well as border, head-direction and place-like cells). When these grid-like representations are incorporated as the input to a deep reinforcement learning agent solving challenging navigation tasks in 3D environments, the agent surpasses both an expert human and comparison agents, and exhibits shortcut behaviours reminiscent of those performed by mammals. The findings support neuroscientific theories that grid cells provide a Euclidean spatial framework essential for vector-based navigation.

## 2. Why this matters for us

Banino et al. 2018 is the *first major demonstration* that *biological grid cells emerge in artificial neural networks* trained on path-integration tasks, and that *adding these grid-like representations to a deep RL agent dramatically improves navigation*. For the user's program, this paper is the *most direct empirical bridge* between deep-learning architectures and the cognitive-map / hippocampus literature. It demonstrates that the architectural choices the user's program commits to (grid-organized memory, multi-scale spatial representations, predictive substrate) are *empirically supported* by the deep-RL field — when the architecture has the right inductive bias (recurrent network + appropriate regularization), grid-like representations *emerge spontaneously*. The paper is also the cleanest existence proof for the user's [world_model_emergence](../concepts/world_model_emergence.md) thesis at the level of spatial representations: grid cells emerge as a *byproduct* of training on a particular task, not as a hard-coded architectural commitment. This is a constructive demonstration of the user's program-level claim that the *right architecture + the right training pressure* produces biologically-plausible internal representations spontaneously.

## 3. Key claims

1. *Grid-cell-like firing patterns emerge* in a supervised recurrent network trained on path integration with regularization (dropout) — not hard-coded.
2. The *hexagonal grid pattern* is not predicted by any single input variable; it falls out of optimizing for self-motion integration in the recurrent network.
3. *Border cells, head-direction cells, and irregular spatial cells* also appear in the same network — multiple EC cell types emerge from one training objective.
4. Adding the grid-cell representations as input to a *deep RL navigation agent* improves performance dramatically — from ~30-40% optimal to ~80-90% optimal.
5. The grid-augmented agent performs *novel shortcuts* that resemble vector-based navigation in mammals — qualitative behavioral validation of the framework.
6. Provides a *normative computational argument* for why brains evolved grid cells: they are the optimal code for path integration in a recurrent network.
7. Multiple grid scales emerge with realistic *spacing ratios* (clustered at ~1.4, matching empirical EC modular structure).
8. The grid representation enables *linear decoding of goal direction and distance* — establishing the metric role of the code for vector navigation.

## 4. Methods

A two-layer recurrent network (LSTM followed by a linear bottleneck) is trained in a *supervised* fashion to predict the agent's current place- and head-direction-cell activities (computed analytically from ground-truth trajectories in simulated rectangular environments) from a stream of *egocentric velocity inputs*. The supervised targets are the *biologically-derived* place-cell and head-direction-cell activities, treated as known. After training, the linear bottleneck units exhibit *periodic hexagonal firing fields* characteristic of medial entorhinal grid cells across multiple spatial scales. This frozen "grid module" is then plugged in as an *additional input stream* to an A3C deep-RL agent learning to navigate a 3D DeepMind Lab maze with random goal locations. Goal-vector signals can be read off *linearly* from the grid units, providing the RL agent with a direct vector-navigation signal. The training pipeline therefore has two stages: (i) supervised path-integration training that produces the grid module, (ii) RL training that uses the grid module as a frozen perceptual feature. The supervised stage is the architectural insight; the RL stage is the demonstration of utility.

## 5. Results

Headline quantitative results:

- **Trained recurrent network develops units with gridness scores > 0.3** (the standard biological threshold) at multiple spatial scales clustered at ratio ~1.4 — matching empirical entorhinal scale ratios.
- **Grid-cell agent reaches ~80-90% of optimal returns** on goal-navigation tasks; baseline DeepMind Lab A3C agent reaches ~30-40%.
- **Grid-cell agent outperforms a tested expert human player** on the difficult maze configurations — superhuman navigation.
- **Shortcut behavior:** agent traverses opened-up doorways with success rate ~93% vs ~26% for baseline — demonstrating vector-based rather than path-following navigation.
- **Removing dropout in the recurrent layer eliminates the hexagonal grid pattern**, indicating its dependence on regularization — a methodologically critical finding that subsequent work (Schaeffer et al. 2022) used to argue for the fragility of emergent grids.
- **Linear decoder of goal direction/distance from grid-cell activity achieves < 2-cell error** — establishing the cleanly linear, metric role of the code.
- **Border cells emerge alongside grid cells** in the same network, validating the EC cell-type repertoire.
- **The agent's improved navigation generalizes** to novel maze configurations not seen during training, supporting the vector-navigation interpretation.

## 6. Critique / limitations

The Banino et al. result is influential but has substantial limitations and contestation.

- **Path-integration training uses ground-truth place- and head-direction-cell targets** — these themselves carry strong inductive bias; the network is *taught* the biological representation rather than discovering it from raw sensory experience.
- **Hexagonal grids depend on a regularization (dropout) hyperparameter**; *criticised by Schaeffer, Khona & Fiete 2022 NeurIPS* as evidence of fragile emergence — alternative regularizers do not produce hexagonal grids, suggesting the result is partly artifactual.
- **Spatial environments are flat 2D arenas**; does not address 3D grid coding (Yartsev & Ulanovsky 2013) or naturalistic spaces.
- **The agent's navigation policy is RL-trained separately**; the contribution of grid cells vs. simply having a richer feature input is conflated. A non-grid but high-dimensional perceptual feature might produce similar improvements.
- **"Shortcut behavior" demonstration is on a small set of contrived doorway environments** — generalization to richer naturalistic environments not tested.
- **The neuroscience claim** — that the brain learns grid cells via path-integration optimization — is computational evidence, not biological proof; the brain may use a different objective.
- **Place-cell-like inputs to the network are arguably the real workhorse**; subsequent work shows grids do not always emerge from path integration alone.
- **Code released only for the supervised path-integration component**; the RL agent code remains proprietary, limiting reproducibility.

## 7. Connection to our work

Banino et al. 2018 is one of the most architecturally consequential ML-neuroscience-bridge papers for the user's program.

**Touchpoint 1: grid-cell emergence as the empirical anchor for the user's gridcell_rnn architecture.** The Banino-et-al demonstration that grid cells emerge in a trained recurrent network is the *most direct empirical bridge* between deep-learning recurrent architectures and the biological hippocampus / EC literature. The user's [gridcell_rnn](../concepts/gridcell_rnn.md) is named after biological grid cells; Banino-et-al provide the empirical evidence that a recurrent neural network with appropriate inductive bias (path-integration training + regularization) develops the named representations *spontaneously*. The biological warrant for the user's architectural commitment is therefore not just analogical — it is supported by direct empirical demonstration in the DL field.

**Touchpoint 2: convergent emergence — the architectural prediction for the user's program.** Banino-et-al show that grid cells, border cells, head-direction cells, and place cells all emerge from *one* training objective (supervised path integration). This is a substantial *convergent emergence* result — multiple cell types fall out of a single architectural-and-training-objective configuration. The user's program inherits the architectural prediction: *with the right architecture + training, multiple biological cell types should emerge in the user's models*. Probing the user's grid-organized memory should reveal not just grid-like units but also border-like, place-like, and direction-like units. This is a concrete empirical analysis the user can perform.

**Touchpoint 3: world_model_emergence as the broader thesis — grid cells as a special case.** Banino-et-al's grid-cell emergence is a *special case* of the user's [world_model_emergence](../concepts/world_model_emergence.md) thesis: the right architecture + the right training pressure produces useful internal representations *spontaneously*. The user's program generalizes the Banino-et-al demonstration: grid cells emerge under path-integration training; the user's program predicts that world models — and more broadly, useful predictive representations — should emerge under inter-hub competition pressure even without explicit world-model objectives. Banino-et-al is the constructive evidence that emergence is achievable; the user's program extends the principle to a richer architectural / training-objective regime.

**Touchpoint 4: multi-scale grid spacing — empirical anchor for multi-compartmental memory.** Banino-et-al's finding that multiple grid scales emerge with realistic ratios (~1.4) is the empirical evidence for *multi-scale spatial organization* the user's [multi_compartmental_memory](../concepts/multi_compartmental_memory.md) commits to. The user's V1-paired ($C^{(1)}$, fine resolution) → V4-paired ($C^{(3)}$, coarse resolution) hierarchy is the engineering analog of Banino-et-al's multi-scale grid module. The biological warrant for *multiple parallel spatial resolutions* is direct.

**Touchpoint 5: linear decoding of vector quantities — the architectural readout pattern.** Banino-et-al show that goal direction and distance can be *linearly decoded* from the grid-cell activity. This is a strong architectural property: the grid representation makes useful vector quantities *linearly readable*, which is what downstream RL or planning systems need. The user's program inherits the architectural design principle: the deeper memory compartments should produce *linearly decodable* representations of task-relevant variables. This is a strong empirical criterion for evaluating the user's architecture: probe the deepest compartment with linear decoders for task variables and verify they are recoverable.

**Touchpoint 6: shortcut behavior as the architectural validation.** Banino-et-al's shortcut behavior (the agent navigates via opened doorways without retraining) is a *qualitative behavioral signature* of vector-based navigation. The user's program should aim for analogous behavioral signatures: training models on a sequence of related tasks and demonstrating *qualitative shortcuts* that an RL agent without the right architecture cannot perform. This is a behavioral validation criterion that complements the quantitative benchmarks.

**Touchpoint 7: Schaeffer-et-al critique — implications for the user's architecture.** The Schaeffer, Khona & Fiete 2022 critique — that the hexagonal grid pattern in Banino-et-al depends on a specific regularizer choice — is a cautionary lesson for the user's program. The user's architectural choices should not depend on knife-edge hyperparameter values. The empirical evidence of emergence should be robust across reasonable variations in the architecture and training procedure. The user's program should explicitly test for robustness of any emergent representations against architectural perturbations, and treat fragile emergence as a sign that the result is artifactual.

**Touchpoint 8: convergence with the cognitive-map ambition.** Banino-et-al, [whittington2020_tem](whittington2020_tem.md), and [stachenfeld2017_predictive_map](stachenfeld2017_predictive_map.md) together constitute the *modern cognitive-map ML literature* — three independent demonstrations that grid-like and cognitive-map-like representations emerge or can be engineered in deep neural networks. The user's program inherits the cognitive-map ambition from this literature: build architectures whose deepest representations are cognitive-map-like in the sense that they support flexible spatial / relational inference. Banino-et-al is the empirical foundation; the user's program is one extension along this trajectory.

## 8. Citations to follow

- `cueva_wei2018_grid_recurrent_iclr` — *ICLR* — emergence of grid-like representations by training recurrent networks to perform spatial localization; the independent contemporaneous demonstration. Not in seed.
- `sorscher2023_unified_theory_grid_cells_neuron` — *Neuron* — unified theory for the origin of grid cells through pattern formation; the modern theoretical synthesis. Not in seed.
- `schaeffer_khona_fiete2022_no_free_lunch_neurips` — *NeurIPS* — "No Free Lunch from Deep Learning in Neuroscience: A Case Study through Models of the Entorhinal-Hippocampal Circuit"; the principal critique. Not in seed.
- [whittington2020_tem](whittington2020_tem.md) — TEM; the relational-memory neural-network model. In seed.
- `bellmund2018_navigating_cognition_science_review` — *Science* — navigating cognition with maps in humans. Not in seed.
- [stachenfeld2017_predictive_map](stachenfeld2017_predictive_map.md) — the SR theoretical framework (concurrent theoretical work). In seed.
- `gao2021_path_integration_group_representation_neurips` — *NeurIPS* — on path integration of grid cells: group representation and isotropic scaling. Not in seed.
- `banino2020_memo_iclr` — *ICLR* — MEMO; the memory-extension follow-up. Not in seed.
- `dorrell_whittington_behrens2023_actionable_iclr` — *ICLR* — actionable neural representations: grid cells from minimal constraints. Not in seed.
- [okeefe_dostrovsky1971_hippocampal_map](okeefe_dostrovsky1971_hippocampal_map.md) — the foundational place-cell paper. In seed.
- [hafting2005_grid_cells](hafting2005_grid_cells.md) — the foundational grid-cell paper. In seed.
- [behrens2018_cognitive_map](behrens2018_cognitive_map.md) — the cognitive-map review. In seed.
- [wayne2018_merlin](wayne2018_merlin.md) — MERLIN; the broader DeepMind RL+memory architecture. In seed.
- [hafner2023_dreamerv3](hafner2023_dreamerv3.md) — DreamerV3; the contrast world-model architecture. In seed.
- [lisman_grace2005_hippocampal_vta](lisman_grace2005_hippocampal_vta.md) — the hippocampal novelty-gating mechanism. In seed.
