---
id: urbanczik_senn2014_predictive_dendrite
title: "Learning by the dendritic prediction of somatic spiking"
authors:
  - "Urbanczik, Robert"
  - "Senn, Walter"
year: 2014
venue: "Neuron"
doi: "10.1016/j.neuron.2013.11.030"
arxiv: ""
url: "https://doi.org/10.1016/j.neuron.2013.11.030"
tags:
  - bio-plausible-learning
  - theoretical-essay
  - cortical-anatomy
concepts:
  - apical-dendrite-coincidence-detection
  - prediction-error-map
  - pyramidal-cell-two-compartment
  - apical-basal-dendritic-integration
  - gridcell-rnn
related:
  - jordan2023_dendritic_bayesian
  - larkum2013_apical_basal
  - larkum_zhu_sakmann1999_bac_firing
  - bastos2012_canonical_microcircuits
  - wang2025_hierarchical_reasoning_model
relevance_to:
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-16"
---

# Learning by the dendritic prediction of somatic spiking

## 1. Abstract

Recent modeling of spike-timing-dependent plasticity indicates that plasticity involves, as a third factor, a *local dendritic potential* besides pre- and postsynaptic firing times. The authors present a simple compartmental neuron model with a non-Hebbian, biologically plausible learning rule for dendritic synapses where plasticity is modulated by these three factors. In functional terms, the rule seeks to *minimize discrepancies* between somatic firings and a local dendritic potential. Such prediction errors arise from stochastic fluctuations *and* from synaptic input that directly targets the soma. Depending on the nature of this direct input, the plasticity rule subserves *supervised* or *unsupervised* learning. When a reward signal modulates the learning rate, *reinforcement learning* results. A single plasticity rule therefore supports diverse learning paradigms.

## 2. Why this matters for us

The Urbanczik-Senn rule is the canonical biologically-plausible local plasticity rule for a two-compartment pyramidal neuron with apical and somatic compartments. It is the cellular substrate of the Jordan et al. 2023 Bayesian-dendrite framework ([jordan2023_dendritic_bayesian](research_db/papers/jordan2023_dendritic_bayesian.md)) and is one of the leading candidate replacements for backpropagation in biologically-realistic learning. For the user's program, this paper supplies the *learning rule* that biologically-plausible variants of the Feedback Transformer or PRISM architecture would adopt to replace BPTT with local plasticity. The connection between the cellular AND-gate (Larkum 1999, 2013) and a normative learning objective is established here.

## 3. Key claims

1. **The third factor.** Standard STDP uses two factors (presynaptic time, postsynaptic time). Urbanczik & Senn add a *third* factor: the local dendritic potential at the synapse. Plasticity becomes a function of all three.
2. **Functional objective.** The plasticity rule minimizes the discrepancy between the *somatic firing rate* and the *apical-dendrite-predicted firing rate*. The dendrite is trying to predict the soma's output.
3. **Two compartments.** The model has a *somatic* compartment receiving "teaching" input (the direct somatic drive) and a *dendritic* compartment receiving "input to be learned" (the synaptic input that plasticity adjusts). The two are electrotonically coupled but functionally distinct.
4. **Supervised learning.** When the somatic compartment receives target firing-rate input (the teaching signal), the dendritic plasticity learns to *predict* this firing rate from its inputs. After learning, the dendrite can drive the soma even without the teaching signal — i.e., it has learned the input-output mapping.
5. **Unsupervised learning.** When the somatic compartment receives only stochastic background activity, the dendrite still learns to predict it — this is unsupervised representation learning, with the dendrite learning the statistical structure of its input that drives the soma.
6. **Reinforcement learning.** When a *reward* signal modulates the learning-rate, the plasticity rule becomes a reward-modulated update. The cell learns to fire when its dendritic input is associated with reward; this is the classical reward-modulated three-factor rule.
7. **One rule, three paradigms.** The same local plasticity rule supports supervised, unsupervised, and reinforcement learning depending on what drives the somatic compartment. This unifies the standard three learning paradigms in a single biophysical mechanism.

## 4. Methods

**Compartmental model.** A neuron with two compartments — soma and (single) apical dendrite. Each compartment has a membrane voltage; the two are coupled by a passive conductance. The soma generates Poisson spikes whose rate is a function of the somatic voltage.

**Inputs.** The dendritic compartment receives synaptic inputs with weights $w_i$ to be learned. The somatic compartment receives "teaching" input (this is the third factor).

**Plasticity rule.** The synaptic weight update is

$$
\Delta w_i \propto \text{(presynaptic activity)}_i \times \big[ \phi(V_{\text{soma}}) - \phi(V_{\text{dendrite}}) \big]
$$

where $\phi$ is the soma's firing-rate function and the *bracketed term* is the prediction error: the actual somatic firing rate minus the dendritically-predicted firing rate.

The rule is **local** (each synapse updates based on its own presynaptic activity, its own dendritic potential, and the somatic potential — all available at the synaptic site).

**Learning paradigms.**
- *Supervised:* the somatic compartment receives target rate signals. The dendrite learns to predict the target from its synaptic input.
- *Unsupervised:* the somatic compartment receives stochastic background. The dendrite learns to predict its statistical structure.
- *Reinforcement:* the learning rate is modulated by a reward signal. The dendrite learns to fire on rewarded inputs.

## 5. Results

The principal theoretical and simulation findings:

- **Convergence.** Under the Urbanczik-Senn rule, the synaptic weights converge such that the dendritic potential matches the somatic firing rate. The convergence proof is analytical for the simplified model.
- **Supervised classification.** In a binary classification task with the teacher signal as the target firing rate, the trained dendrite correctly produces the target rate from its input. The classification accuracy matches a comparable backpropagation-trained network.
- **Unsupervised representation learning.** When trained on natural-image patches as input (without explicit supervision), the dendrites learn weights that recover Gabor-like receptive fields, similar to the unsupervised representations learned by sparse-coding or ICA models.
- **Reinforcement learning.** With a reward-modulated learning rate, the model performs operant-conditioning-style tasks: it learns to associate specific dendritic input patterns with reward.
- **Local plasticity is the right rule.** The rule depends only on locally-available signals — there is no need for a global error signal or for cross-layer credit assignment. This is the biological plausibility argument.

## 6. Critique / limitations

The model is *highly simplified*. Real pyramidal cells have many dendritic compartments with complex electrotonic structure; the Urbanczik-Senn model collapses to two. The plasticity dynamics in real dendrites are richer than the model captures.

The plasticity rule requires the *somatic potential* at the synapse. This is biologically plausible only if the somatic potential is communicated to the synapse via back-propagating action potentials. The BAC mechanism ([larkum_zhu_sakmann1999_bac_firing](research_db/papers/larkum_zhu_sakmann1999_bac_firing.md)) provides this — but only on coincidence-detection timescales. Whether the plasticity rule operates on the BAC timescale or on slower (rate-coded) timescales is not fully resolved.

The model has only forward inputs. Real cortical circuits have feedback. The "supervised" interpretation (teacher signal on the soma) is a placeholder for whatever feedback drives the somatic firing — in cortex, this is top-down predictions from higher cortical areas. The integration with hierarchical feedback frameworks (Bastos 2012; Friston 2010) is left to subsequent work.

The rule doesn't explicitly implement *credit assignment* in deep networks. For a deep stack of Urbanczik-Senn cells, the local rule learns each cell's input-output mapping but doesn't coordinate learning across layers. Subsequent work (Sacramento et al. 2018; Lillicrap-Hinton variants) has extended the framework to multi-layer networks.

The scaling to behaviorally-relevant tasks is limited. The 2014 paper demonstrates the rule on simple classification, simple unsupervised, and simple RL tasks. Scaling to deep object-recognition or complex RL is an open question; the framework's success at scale (vs backpropagation) is not yet established.

## 7. Connection to our work

This paper supplies the candidate *learning rule* for biologically-plausible variants of the user's architectures:

**Local plasticity as a future training scheme.** PRISM v1 and v2 are trained with backpropagation through time. Backprop is biologically implausible — real cortex does not have the bidirectional weight-symmetric pathways needed for true backprop. The Urbanczik-Senn rule is a candidate local plasticity rule that biologically-plausible variants of PRISM could adopt. The user's program is currently neutral on the training-rule question; if the program is to be presented as biologically grounded, the Urbanczik-Senn rule (or its multi-layer extensions) is the most natural learning rule to commit to.

**The dendritic-prediction-error framework matches PRISM v1's saliency-gated update.** PRISM v1's update gate ([Prism/docs/THESIS.md](Prism/docs/THESIS.md) §2.7) is driven by the prediction-error magnitude $|S_t|$. The Urbanczik-Senn rule's plasticity is driven by the difference between somatic firing and dendritic prediction — a prediction error at the cellular level. The two frameworks are aligned at the conceptual level; PRISM v1's architectural commitment to error-driven learning has a cellular substrate in the Urbanczik-Senn rule.

**Unifying supervised, unsupervised, and RL.** The Urbanczik-Senn paper's argument that the same plasticity rule supports all three learning paradigms is *exactly* the user's multi-hub commitment ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)): different hubs train on different objectives (supervised MSI, unsupervised VAE, reinforcement RL), but the underlying *learning machinery* — the local plasticity rule — is shared. The user's program's architectural cleanliness is supported by the Urbanczik-Senn unification at the cellular level.

**Backward-propagating action potentials as the credit-assignment signal.** The Urbanczik-Senn rule depends on the somatic potential at the synapse — communicated via back-propagating action potentials. Larkum's BAC framework is the precise biological mechanism for this. The user's Feedback Transformer is the architectural analog: multiplicative integration of feedback (apical) and bottom-up (basal) at the same node. A biologically-plausible variant of the Feedback Transformer would use Urbanczik-Senn-style local plasticity rather than backprop for training.

**The local-plasticity-as-cortical-credit-assignment narrative.** HRM ([wang2025_hierarchical_reasoning_model](research_db/papers/wang2025_hierarchical_reasoning_model.md)) cites Whittington-Bogacz-style local-plasticity work for its motivation. Urbanczik-Senn is the foundational candidate plasticity rule in this line of work. If the user's program adopts HRM-style training, citing Urbanczik-Senn for the biological-plausibility argument is appropriate.

## 8. Citations to follow

- `larkum_zhu_sakmann1999_bac_firing` — the cellular BAC mechanism. In seed, full depth.
- `larkum2013_apical_basal` — cortex-wide framing. In seed, full depth.
- `jordan2023_dendritic_bayesian` — Bayesian formalization. In seed, full depth.
- `sacramento2018_dendritic_credit_assignment` — extension to deep networks. Not in seed.
- `whittington_bogacz2019_local_credit_assignment` — broader local-plasticity review. Not in seed.
- `bastos2012_canonical_microcircuits` — microcircuit framework. In seed, full depth.
- `richards2019_deep_learning_neuroscience` — review of biologically-plausible learning. Not in seed.
- `roelfsema_holtmaat2018_local_plasticity_credit` — cellular credit assignment review. Not in seed.
