---
id: mante2013_context_dependent_pfc
title: "Context-dependent computation by recurrent dynamics in prefrontal cortex"
authors:
  - "Mante, Valerio"
  - "Sussillo, David"
  - "Shenoy, Krishna V."
  - "Newsome, William T."
year: 2013
venue: "Nature"
doi: "10.1038/nature12742"
arxiv: ""
url: "https://doi.org/10.1038/nature12742"
tags:
  - primate-neurophysiology
  - prefrontal-cortex
  - neuro-ai-bridging
  - decision-making
concepts:
  - recurrence-for-temporal-dynamics
  - working-memory-persistent-activity
  - drift-diffusion-model
  - coupled-rnn-world-models
related:
  - constantinidis2018_persistent_activity
  - goldman_rakic1995_cellular_wm
  - funahashi1989_mnemonic_dlpfc
  - wang2025_hierarchical_reasoning_model
  - kietzmann2019_recurrence_required
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_116
status: full
depth: full
last_updated: "2026-05-16"
---

# Context-dependent computation by recurrent dynamics in prefrontal cortex

## 1. Abstract

Prefrontal cortex is thought to have a fundamental role in flexible, context-dependent behavior, but the exact nature of the underlying computations is largely unknown. Individual prefrontal neurons often generate remarkably complex responses that defy understanding of their contribution to behavior. Mante et al. study prefrontal cortex activity in macaque monkeys trained to flexibly select and integrate noisy sensory inputs (motion and color) towards a binary choice, with a context cue indicating which stimulus feature is currently task-relevant. They find that the observed complexity of single-neuron responses is readily understood in the framework of a *dynamical process unfolding at the level of the population*. The population dynamics can be reproduced by a trained recurrent neural network, which suggests a previously unknown mechanism for selection and integration of task-relevant inputs. The mechanism implies that selection and integration are two aspects of a single dynamical process unfolding within the same prefrontal circuits, providing a general framework for understanding context-dependent computations.

## 2. Why this matters for us

Mante et al. 2013 is the empirical anchor for treating PFC as a *recurrent dynamical system* rather than a representational layer. This is the architectural commitment behind the user's program: every memory state in the GridCell RNN stack is a recurrent dynamical system, and the central self-attention substrate in the multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) is the dynamical-system-level analog of PFC. The paper also demonstrates that *trained* RNNs reproduce the empirical population dynamics — the legitimating result that licenses using neural-network models to study PFC computation. For PRISM v2's slow memory and any future multi-hub instance, Mante is the citation that connects the architectural choice to the biological data.

## 3. Key claims

1. **Single PFC neurons show heterogeneous, mixed-selectivity responses.** In a context-dependent decision task, individual PFC neurons encode mixtures of stimulus features, context, choice, and reaction time. Pure "category cells" do not adequately describe the response patterns.
2. **The complexity disappears at the population level.** Population-level analysis (using dimensionality reduction and dynamical-system characterization) reveals a low-dimensional structure in which the relevant computations (selection of task-relevant input; evidence integration toward a choice) are clearly visible as distinct dynamical processes.
3. **Selection and integration share a substrate.** Selection of the task-relevant input (motion in motion-context, color in color-context) and integration of evidence toward a decision are not implemented by separate circuits but by a *single* recurrent dynamical process. The same PFC neurons participate in both.
4. **Selection works via context-dependent line attractors.** The context cue sets up a line-attractor structure in the PFC state space; the task-relevant input is the dimension along which the attractor extends, while the task-irrelevant input is the dimension perpendicular to the attractor. The population dynamics therefore *select* the relevant input as part of its intrinsic geometry.
5. **A trained recurrent neural network reproduces these dynamics.** A simple RNN trained on the same task with the same input structure develops a population-level structure with the same line-attractor selection mechanism. This is the existence proof that the dynamical-system framework is computationally sufficient.
6. **The mechanism is general.** The line-attractor selection mechanism is a general principle for context-dependent computation, not specific to the perceptual-decision task used. Any task that requires selecting one input among many based on context should benefit from a similar dynamical-system architecture.

## 4. Methods

**Task.** Macaque monkeys performed a context-dependent direction-of-motion or color discrimination on a random-dot stimulus. The dots had both motion and color information; a context cue indicated which feature to report. The task therefore requires both *selection* (which feature) and *integration* (decision over time).

**Neural recordings.** Single- and multi-unit recordings in macaque dorsolateral PFC during task performance. Population-level analyses using principal component analysis, regression-based subspaces, and dynamical-system characterizations.

**Model.** A trained recurrent neural network (fully-connected RNN) was trained with backpropagation through time on the same task structure. The network had the same inputs as the monkey received and was trained to produce the same outputs. After training, the same population-level analyses were applied to the network's internal activity.

**Comparison.** The empirical population dynamics and the model population dynamics were compared in terms of their geometric structure, the dimensions along which selection and integration happen, and the dynamics during context switches.

## 5. Results

The principal quantitative findings:

- **Mixed selectivity in single cells.** PFC neurons show responses that depend nonlinearly on combinations of context, stimulus features, choice, and time. No subset of neurons is well-described as a "context cell" or a "decision cell" — most cells encode mixtures.
- **Low-dimensional population structure.** Despite single-neuron heterogeneity, the population activity lies on a low-dimensional manifold (typically 3–5 dimensions account for most of the variance during the task).
- **Selection geometry.** In motion-context trials, the population trajectory is dominated by motion-related dynamics; the color-related dynamics are present but projected onto a different (largely orthogonal) subspace and don't drive the decision. In color-context trials, the situation reverses. The context cue *rotates* the relevant dimensions in the population state space.
- **Integration as movement along the line attractor.** Within each context, the decision is implemented as a slow drift along a line in the state space. The drift direction depends on the sign of the relevant input.
- **RNN reproduction.** A trained RNN with realistic complexity (~100 hidden units) reproduces the line-attractor structure and the orthogonal context-selection mechanism. The same population-level analyses applied to the RNN's hidden activity recover the same geometric structure.
- **Context switching.** When the context cue changes, the population dynamics rapidly reorganize, with the rotation happening over ~100 ms. This is consistent with the RNN's behavior during context-switch trials.

## 6. Critique / limitations

The framework is descriptive rather than mechanistic at the synaptic level. The paper shows that PFC population dynamics implement context-dependent computation via line attractors but does not specify the synaptic / cellular implementation. Subsequent work (Sussillo, Maheswaranathan and collaborators) has explored implementation candidates; this paper itself does not commit.

The task is a perceptual-decision task with a simple binary structure. Whether the line-attractor selection mechanism generalizes to richer, multi-step, hierarchical tasks (e.g., multi-stage reasoning, planning over long horizons) is an empirical open question. The HRM paper (Wang et al. 2025) extends the recurrent-dynamics framework to multi-step reasoning, but uses different architectural commitments.

The model is a single trained RNN. Real PFC is not a single RNN; it interacts with sensory cortex, motor cortex, basal ganglia, and thalamus. The "PFC computation" the paper isolates is therefore an idealization — it assumes the relevant computation can be studied without modeling the surrounding circuits. This is a reasonable approximation for a perceptual-decision task but may not hold for tasks with strong interactions across regions.

The paper does not engage with the predictive-coding framework. The PFC dynamics it describes can be interpreted as a hierarchical generative model (PFC as a top-level prediction generator) but the paper itself does not draw this connection. Subsequent work has bridged the two; this paper is silent.

The recurrent-network model is trained with BPTT. The biological plausibility of BPTT in cortex is well-known to be questionable. The paper's claim is "the architectural class is right" rather than "the training procedure is right." For the user's program, this means Mante's results legitimate the *architecture* of recurrent dynamics but not the *training rule*.

## 7. Connection to our work

This paper supports several architectural commitments in the user's program:

**PFC as the central self-attention substrate.** The user's multi-hub multi-objective system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) treats a shared self-attention substrate as the analog of PFC. Mante's finding that PFC implements context-dependent selection via low-dimensional dynamics supports this: the central self-attention map is the place where contextual signals (from RL hub, MSI hub, VAE hub) come together to select the relevant input from the sensory stream. The line-attractor mechanism is the dynamical-system-level implementation of this selection.

**Slow memory as the line-attractor substrate.** PRISM v2's slow memory $M^{\text{slow}}$ ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3) is updated rarely (per-step probability ~0.05) and maintains task-relevant context over many steps. This matches Mante's "context dimension" in the PFC state space: a slow-evolving variable that sets up the line-attractor along which decision-relevant integration happens.

**Mixed-selectivity representations in the user's hubs.** The user's hub-level representations are explicitly mixed: each hub's memory state encodes a combination of sensory, task, and reward variables. Mante's finding that PFC single neurons show similar mixed selectivity is the biological warrant — the user's program isn't trying to enforce one-cell-one-concept clean representations because the biology doesn't either.

**Trained RNNs as the right modeling framework.** Mante's RNN reproduction of the empirical dynamics is the legitimating result for the user's choice of trained recurrent-attention networks. The recurrent ViT (2502.10955), PRISM v1, and PRISM v2 are all trained recurrent networks that aim to reproduce primate-attention signatures. Mante's paper is the canonical citation for "trained RNNs are the right level of description."

The recurrent ViT paper cites Mante 2013 in its bibliography (ref [116]) but does not engage with the context-dependent selection mechanism explicitly. Future manuscripts that extend the recurrent ViT to multi-hub or multi-context tasks should engage with Mante's framework more directly, because it provides the dynamical-system-level vocabulary for describing what the trained model is doing.

## 8. Citations to follow

- `sussillo_barak2013_opening_blackbox` — population-dynamics analysis methods. Not in seed.
- `constantinidis2018_persistent_activity` — modern review of PFC persistent activity. In seed, full depth.
- `wang2025_hierarchical_reasoning_model` — modern recurrent reasoning architecture. In seed, full depth.
- `kietzmann2019_recurrence_required` — empirical evidence for recurrence in human vision. In seed, full depth.
- `goldman_rakic1995_cellular_wm` — cellular basis of PFC WM. In seed.
- `funahashi1989_mnemonic_dlpfc` — classic PFC persistent activity. In seed.
- `mante2024_decision_dynamics` — Mante's follow-up work. Not in seed.
- `maheswaranathan2019_universality` — universal dynamics across trained RNNs. Not in seed.
