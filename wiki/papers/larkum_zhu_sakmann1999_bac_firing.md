---
id: larkum_zhu_sakmann1999_bac_firing
title: "A new cellular mechanism for coupling inputs arriving at different cortical layers"
authors:
  - "Larkum, Matthew E."
  - "Zhu, J. Julius"
  - "Sakmann, Bert"
year: 1999
venue: "Nature"
doi: "10.1038/18686"
arxiv: ""
url: "https://doi.org/10.1038/18686"
tags:
  - primate-neurophysiology
  - cortical-anatomy
concepts:
  - apical-dendrite-coincidence-detection
  - pyramidal-cell-two-compartment
  - top-down-feedback
  - cortical-microcircuit-model
  - apical-basal-dendritic-integration
related:
  - larkum2013_apical_basal
  - jordan2023_dendritic_bayesian
  - urbanczik_senn2014_predictive_dendrite
  - bastos2012_canonical_microcircuits
relevance_to:
  - prism_v2
  - recurrent_vit
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-16"
---

# A new cellular mechanism for coupling inputs arriving at different cortical layers

## 1. Abstract

Pyramidal neurons in layer 5 of the neocortex extend their axons and dendrites into all cortical layers and have both an axonal and a dendritic initiation zone for action potentials. Distal dendritic inputs, which normally appear greatly attenuated at the axon, must cross a high threshold at the dendritic initiation zone to evoke calcium action potentials, but can then generate bursts of axonal action potentials. The authors show that a single back-propagating sodium action potential generated in the axon facilitates the initiation of these calcium action potentials when it coincides with distal dendritic input within a time window of several milliseconds. Inhibitory dendritic input can selectively block the initiation of dendritic calcium action potentials, preventing bursts of axonal action potentials. Excitatory and inhibitory postsynaptic potentials in the distal dendrites can therefore exert significantly greater control over axonal action potential initiation than expected from their electrotonically isolated locations. The coincidence of a single back-propagating action potential with a subthreshold distal EPSP to evoke a burst of axonal action potentials is a new mechanism — termed BAC firing — by which the main cortical output neurons associate inputs arriving at different cortical layers.

## 2. Why this matters for us

This is the cellular substrate of the Feedback Transformer's central commitment: multiplicative integration of bottom-up sensory and top-down feedback signals. Where Larkum 2013 ([larkum2013_apical_basal](research_db/papers/larkum2013_apical_basal.md)) frames the BAC mechanism as a cortex-wide organizing principle, the 1999 *Nature* paper is the foundational experimental result that established the mechanism in the first place. It is the most cited single-cell experiment in the cortical-feedback literature and is the load-bearing citation for any biologically-motivated claim about why feedback integration should be multiplicative rather than additive. The user's program ([feedback_transformer](research_db/concepts/feedback_transformer.md), [apical_basal_dendritic_integration](research_db/concepts/apical_basal_dendritic_integration.md)) inherits its architectural commitments directly from this paper.

## 3. Key claims

1. Pyramidal neurons in L5 of the neocortex have *two functionally distinct action-potential initiation zones*: the axonal initiation zone (near the soma, generating sodium spikes) and the dendritic initiation zone (in the apical dendrite, generating calcium spikes).
2. The two initiation zones are *electrotonically separated*: distal dendritic input is greatly attenuated by the time it reaches the axon, and dendritic Ca²⁺ spikes decay before reaching the soma. Each compartment can generate spikes independently.
3. **BAC firing** (back-propagating action potential + Ca²⁺ event): when a basal-driven somatic action potential coincides with apical-dendrite input within a temporal window of several milliseconds, the back-propagating sodium action potential lowers the threshold for the dendritic Ca²⁺ spike. The dendritic Ca²⁺ spike then drives a *burst* of axonal action potentials.
4. The coincidence detection is *temporally precise* — a window of several milliseconds is required. Apical input outside this window produces only single spikes (or subthreshold dendritic activity).
5. **Inhibitory gating.** Dendritic inhibitory inputs can selectively block the dendritic Ca²⁺ spike *without* affecting axonal AP initiation. This creates an inhibitory veto on the apical-basal coincidence detection, dissociating the two compartments' contributions to output.
6. The mechanism allows L5 pyramidal cells — the main cortical *output* neurons — to associate input arriving in superficial cortical layers (L1, distal apical dendrites; carrying top-down feedback) with input arriving in deep cortical layers (basal dendrites; carrying intracortical and thalamocortical feedforward). The cell is therefore a biophysical AND-gate for top-down and bottom-up evidence.

## 4. Methods

In vitro whole-cell patch-clamp recordings from L5 pyramidal neurons in rat somatosensory cortex slices. The authors made simultaneous *dual* patch recordings — one electrode at the soma, one at the apical dendrite (typically 600–800 μm from the soma, in the apical tuft). This allowed independent stimulation of basal-vs-apical compartments and simultaneous recording of voltage in both.

Experimental conditions:
- **Basal-only.** Somatic current injection drives axonal action potentials; record both at soma and dendrite.
- **Apical-only.** Distal dendritic current injection; record both compartments.
- **Coincidence.** Brief basal pulse + concurrent or near-concurrent apical pulse; vary the temporal offset.
- **Inhibition.** Local pharmacological GABA agonist application at the apical dendrite to block dendritic Ca²⁺ spikes selectively.

Pharmacology was used to dissect the contributions: TTX to block axonal Na⁺ spikes, calcium-channel antagonists to block dendritic Ca²⁺ spikes, GABA-A and GABA-B antagonists to dissect inhibitory contributions.

## 5. Results

The principal quantitative findings:

- **Basal-only condition.** A somatic Na⁺ spike back-propagates into the dendrite but is *attenuated* in the distal apical tuft. The back-propagating AP alone does not produce a Ca²⁺ spike unless paired with apical input.
- **Apical-only condition.** Distal dendritic current must cross a *high* threshold to evoke a Ca²⁺ spike (estimated ≈ –40 mV at the dendritic initiation zone). Subthreshold apical inputs alone produce only local PSPs that decay before reaching the soma.
- **Coincidence (BAC firing).** When the somatic AP and the apical input coincide within ≈10 ms, the back-propagating AP *facilitates* the dendritic Ca²⁺ spike, lowering its effective threshold by several mV. The combined input produces a burst of 3–5 axonal action potentials at ≈100–150 Hz.
- **Temporal asymmetry.** The BAC mechanism is more effective when the basal-driven somatic AP arrives *before* the apical input (within ≈10 ms) than the other way around. The asymmetry reflects the time required for the back-propagating AP to depolarize the dendritic initiation zone.
- **Inhibitory veto.** GABA-A and GABA-B agonist application at the apical dendrite selectively blocks the dendritic Ca²⁺ spike without affecting somatic firing. The BAC mechanism's output (burst vs single AP) is therefore controlled by inhibitory dendritic input — a state-dependent gate.
- **Amplification.** The output difference between coincidence (burst, 3–5 APs) and non-coincidence (single AP) is categorical, not graded. The amplification factor at the output level is large.

## 6. Critique / limitations

The experiments are *in vitro* in rat somatosensory cortex slices. Generalization to primate cortex (and to other cortical areas) is plausible but was not directly tested. Subsequent work has confirmed the BAC mechanism in macaque V1 and in mouse cortex broadly.

The experiments use direct current injection rather than synaptic input. The temporal precision of BAC firing in vivo, with realistic synaptic timing and background activity, is harder to characterize. Subsequent in-vivo work (Murayama et al. 2009, Takahashi et al. 2016) has shown the mechanism is preserved in vivo but the precision is reduced.

The role of NMDA receptors in dendritic Ca²⁺ generation was not fully resolved in 1999. Later work has emphasized that NMDA spikes in the apical dendrite (Schiller et al. 2000, Polsky et al. 2004) interact with the BAC mechanism. The 1999 paper isolates the back-propagating-AP + Ca²⁺-spike interaction without engaging the full NMDA-spike repertoire.

Generalization to other pyramidal-cell classes (L2/3, L6 CT, L6 CC) is not addressed. L2/3 cells have a morphologically smaller version of the same mechanism; L6 cells have less elaborated apical tufts. The strength of BAC firing varies across pyramidal classes; the 1999 paper focuses on L5.

The behavioral relevance was not addressed in the 1999 paper. Connection to perception, attention, and learning was inferred from the cellular mechanism but not tested directly. Subsequent work (Takahashi et al. 2016; Aru, Suzuki & Larkum 2020) has provided causal links.

## 7. Connection to our work

This is the experimental foundation for the user's commitment to multiplicative feedback integration:

**The Feedback Transformer's Hadamard product is BAC firing at the architectural level.** The Feedback Transformer ([feedback_transformer](research_db/concepts/feedback_transformer.md)) combines sensory and feedback Q/K projections via element-wise multiplication before softmax: $\tilde Q = X W^Q_X \odot \sum_k C^{(k)} W^Q_{C^{(k)}}$. Neither factor alone produces a strong attention score; the product produces a high score precisely when both factors agree. This is the architectural analog of Larkum's AND-gate: basal-driven AP alone produces a single spike; apical input alone produces a subthreshold dendritic event; coincidence produces a burst. The recurrent ViT's multiplicative-feedback variant (2502.10955 §6.7.3) is the user's published instance of this architectural commitment.

**Inhibitory gating as gateable feedback.** The 1999 paper's demonstration that dendritic inhibition can selectively veto the BAC mechanism is the cellular substrate of the user's "ability to shut off feedback" architectural commitment ([bidirectional_hierarchical_feedback](research_db/concepts/bidirectional_hierarchical_feedback.md)). PRISM v2's slow-FiLM modulation can in principle be gated by learned inhibition; future versions of the architecture should explicitly model the inhibitory gating mechanism Larkum identifies.

**Temporal precision of the integration.** The ≈10 ms BAC window has direct implications for the architecture's temporal scales: the architecture should support fast (10 ms equivalent) integration of feedback into ongoing computation. PRISM's per-step update rate and the recurrent ViT's per-token update rate are coarser than this; finer temporal integration might be a useful future architectural variant.

**The bursting output.** The Larkum mechanism's output is a *burst* of action potentials at ~100 Hz, not a graded response. This is a categorical signal — "feedback and sensory agree" → burst — that downstream cells can read out cleanly. The user's architecture treats attention as a *graded* signal (softmax probabilities); the Larkum result suggests that some downstream readout might benefit from a discrete "binding event" representation rather than a graded weight.

The recurrent ViT paper does not cite Larkum 1999 explicitly. The user's program does, via the Feedback Transformer concept. Any biologically-motivated discussion of the multi-source feedback integration mechanism should cite this paper as the cellular precedent.

## 8. Citations to follow

- `larkum2013_apical_basal` — Larkum's cortex-wide framing of the same mechanism. In seed, full depth.
- `jordan2023_dendritic_bayesian` — Bayes-optimal formalization of apical-basal integration. In seed, full depth.
- `urbanczik_senn2014_predictive_dendrite` — local plasticity rule for apical-basal coincidence detection. In seed, full depth.
- `schiller2000_nmda_spikes` — NMDA spikes in basal dendrites (not in seed).
- `polsky2004_compartmentalized_subunits` — dendritic compartmental subunits. Not in seed.
- `murayama2009_dendritic_in_vivo` — in vivo confirmation of dendritic mechanisms. Not in seed.
- `takahashi2016_perception_l5_dendrite` — causal link between L5 dendrite Ca²⁺ and perception. Not in seed.
- `aru_suzuki_larkum2020_consciousness_dendrite` — proposed link to consciousness. Not in seed.
- `larkum2022_dendritic_perspective` — Larkum's modern review. Not in seed.
