---
id: attwell_laughlin2001_brain_energy_budget
title: "An energy budget for signaling in the grey matter of the brain"
authors:
  - "Attwell, David"
  - "Laughlin, Simon B."
year: 2001
venue: "Journal of Cerebral Blood Flow & Metabolism"
doi: "10.1097/00004647-200110000-00001"
arxiv: ""
url: "https://doi.org/10.1097/00004647-200110000-00001"
tags:
  - primate-neurophysiology
  - theoretical-essay
  - review
concepts:
  - metabolic-cost-of-neural-information
  - coalition-resource-competition
related:
  - laughlin1998_metabolic_cost
  - friston2010_fep_unified_theory
relevance_to:
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-16"
---

# An energy budget for signaling in the grey matter of the brain

## 1. Abstract

Anatomic and physiologic data are used to analyze the energy expenditure on different components of excitatory signaling in the grey matter of rodent brain. Action potentials and the postsynaptic effects of glutamate are predicted to consume much of the energy (47% and 34% respectively), with the resting potential consuming a smaller amount (13%) and glutamate recycling using only 3%. Energy usage depends strongly on action-potential rate — an increase in activity of one action potential per cortical neuron per second raises oxygen consumption by 145 mL/100 g grey matter/h. The energy expended on signaling is a large fraction of the total energy used by the brain; this favors energy-efficient neural codes and wiring patterns. The estimates predict the use of *distributed codes*, with ≤15% of neurons simultaneously active, to reduce energy consumption and allow greater computing power from a fixed number of neurons. fMRI BOLD signals are likely to be dominated by changes in energy usage associated with synaptic currents and action-potential propagation.

## 2. Why this matters for us

This is the mammalian-cortex extension of Laughlin et al. 1998 ([laughlin1998_metabolic_cost](research_db/papers/laughlin1998_metabolic_cost.md)). Where the 1998 paper used blowfly retina, Attwell & Laughlin 2001 extends the analysis to cortical grey matter and produces the quantitative numbers that anchor every modern argument about cortical metabolic constraints. The user's competition-emergent-PC thesis ([coalition_resource_competition](research_db/concepts/coalition_resource_competition.md)) rests on a resource-scarcity premise; this paper is the canonical citation for that premise in mammalian (and by extension, primate / human) cortex. Together with Laughlin 1998, it establishes that the brain cannot afford to compute everything — that metabolic budgets are *binding* constraints on cortical architecture.

## 3. Key claims

1. **Signaling dominates the cortical energy budget.** Action potentials (47%) plus postsynaptic glutamate effects (34%) plus resting potentials (13%) account for ≈94% of grey-matter ATP. Glutamate recycling and other housekeeping take only ≈3%. The brain spends most of its energy on signaling, not on synthesis or maintenance.
2. **The cost is highly activity-dependent.** Increasing the mean firing rate by 1 spike/neuron/second raises oxygen consumption by ≈145 mL/100 g/h. Because cortical neurons typically fire at a few Hz, signaling cost is a substantial fraction of total brain metabolism and is strongly coupled to neural activity.
3. **Distributed coding is metabolically warranted.** Given the activity-dependent cost, an energy-efficient cortex should use *sparse and distributed* codes — at any time, only a small fraction of neurons should be active. The authors estimate that ≤15% simultaneous activity is consistent with the brain's measured metabolic rate. Higher activity rates would exceed the metabolic budget.
4. **Energy-efficient wiring.** The same metabolic logic predicts that cortical wiring should be optimized to minimize axonal distance per signaling event. This is consistent with the empirical small-world organization of cortical networks.
5. **fMRI BOLD signal interpretation.** The dominant contribution to BOLD comes from postsynaptic glutamate effects (i.e., synaptic input to a region), not from spike output. This has implications for how to interpret fMRI activations as indices of "what a brain region is doing."
6. **Glia don't help much.** Glial cells handle glutamate recycling and a few other housekeeping functions but consume only a small fraction of grey-matter ATP. The energy bottleneck is in neuronal signaling, not in glial support.

## 4. Methods

The paper builds an *anatomical and physiological energy budget*. Inputs:
- Cell density in rodent cortex (≈ 10⁵ neurons/mm³).
- Average firing rate (estimated ≈ 4 Hz from extracellular recordings).
- Number of synapses per neuron (≈ 8 × 10³).
- Synaptic release probability and quantal content.
- Channel densities and conductances at axon initial segments, somatic membranes, and synapses.

For each component (action potential generation, postsynaptic effects, resting potential, glutamate recycling), the authors compute the ATP cost per unit event, multiply by the rate of events per neuron, and sum across neurons per gram of cortex.

The result is a per-gram ATP demand, which they cross-check against measured cortical oxygen-consumption rates. The two numbers agree within the precision of the underlying data, validating the budgeting approach.

The "sparse coding" prediction follows from imposing the constraint that the total ATP demand must equal the measured supply: for the budget to balance, the average firing rate must be in a specific range, which implies sparse codes.

## 5. Results

The principal quantitative results:

- **Total ATP demand:** ≈25–30 μmol/g/min for rodent cortical grey matter, consistent with measured oxygen consumption.
- **Action potential cost:** dominant at ≈47% of total budget. Each AP costs ≈1.6 × 10⁹ ATP molecules in a typical cortical pyramidal cell.
- **Postsynaptic glutamate effects:** ≈34% of total budget. Driven by Na⁺/K⁺-pump activity restoring ion gradients after AMPA/NMDA receptor activation.
- **Resting potential maintenance:** ≈13% of total budget. Mostly Na⁺/K⁺-ATPase activity.
- **Glutamate recycling:** ≈3% of total budget. Cheap compared to signaling.
- **Activity coupling:** d(O₂)/d(rate) ≈ 145 mL/100 g/h per spike/neuron/s. Linear in firing rate over the physiological range.
- **Sparse-coding prediction:** for the measured metabolic rate to be consistent with the predicted per-spike cost, the mean firing rate must be a few Hz, which (combined with the time-resolution of cortical activity) implies that ≤15% of neurons can be simultaneously active.

## 6. Critique / limitations

The estimates are for rodent grey matter. Primate / human cortex has different cell densities, firing rates, and synapse counts. The Lennie 2003 paper (PMID 12745014) extends the analysis to human cortex and arrives at similar qualitative conclusions but different specific numbers. For the user's program (mostly framed in primate / human terms), the Lennie 2003 update should be cited alongside Attwell & Laughlin 2001.

The budget is for *excitatory* signaling. Inhibitory neuron signaling, dendritic processing (active dendrites with NMDA spikes, calcium dynamics), and astrocytic processes are not separately accounted for. The numbers may therefore underestimate total grey-matter cost.

The "≤15% simultaneous activity" prediction is sensitive to the assumed firing rate and synaptic count. Different assumptions give different bounds. The sparse-coding implication is qualitatively robust but the specific 15% number should be treated as approximate.

The BOLD interpretation (postsynaptic glutamate dominates) has been refined by subsequent work (Logothetis et al. 2001 and successors). The current consensus is that BOLD is a complex mixture of synaptic, neuronal, and glial contributions; the Attwell & Laughlin model is a useful first approximation.

The paper does not engage with computational implications beyond "distributed sparse codes are warranted." More recent work (Niven et al. 2007; Levy & Baxter 1996, 2002; Stemmler & Koch 1999) gives more formal information-theoretic treatments of energy-efficient coding. The Attwell & Laughlin paper is the foundational metabolic-budget paper; the modern information-theoretic synthesis builds on it.

## 7. Connection to our work

This paper is the canonical reference for the resource-scarcity premise in the user's competition-emergent-PC thesis:

**Step 1 of the user's argument** ([coalition_resource_competition](research_db/concepts/coalition_resource_competition.md)): "The brain operates under strict metabolic and bandwidth constraints." Attwell & Laughlin supply the *quantitative* version of this claim for mammalian cortex: 94% of grey-matter ATP is spent on signaling; activity rates are tightly constrained by the metabolic budget. Without this paper, the resource-scarcity premise is plausible-sounding; with it, the premise is grounded in specific numbers.

**Sparse coding as architectural pressure.** Attwell & Laughlin's "≤15% simultaneous activity" prediction is the metabolic warrant for sparse representations. The user's program's commitment to many parallel hubs each contributing only a fraction of attention bandwidth ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) is consistent with this — no single hub dominates the central attention substrate, so the activity is distributed.

**Wiring optimization as architectural pressure.** The metabolic logic favors short axonal distances per signaling event. This is consistent with the user's commitment to *local* communication within layers (SIP in GridCell RNNs, [gridcell_rnn](research_db/concepts/gridcell_rnn.md)) and longer-distance communication only via specific Feedback Transformer pathways. The architecture's cost structure mirrors the biological one.

**Prediction-error sparsity.** Predictive coding's claim that prediction errors are sparser than raw signals (because good predictions cancel out predictable structure) is metabolically warranted: sparse errors are cheaper to transmit than dense raw signals. Attwell & Laughlin's numbers are the metabolic substrate for the energy-efficiency argument that motivates predictive coding (Friston 2010; Spratling 2008).

**Gateability of feedback.** The user's architectural commitment that feedback should be gateable ([bidirectional_hierarchical_feedback](research_db/concepts/bidirectional_hierarchical_feedback.md)) is metabolically warranted: maintaining a feedback channel has a cost; channels that don't supply useful information should be silenced to save energy. The biological circuitry for this (SST+/VIP+ inhibitory gating, [apical_basal_dendritic_integration](research_db/concepts/apical_basal_dendritic_integration.md)) exists because it pays off metabolically.

The recurrent ViT paper (2502.10955) does not engage with metabolic constraints. The user's program does, but only at the theoretical-thesis level. Attwell & Laughlin 2001 (together with Laughlin 1998) is the appropriate primary citation for the metabolic argument in any future manuscript developing the competition-emergent-PC thesis.

## 8. Citations to follow

- `laughlin1998_metabolic_cost` — the precursor paper on blowfly retina. In seed, full depth.
- `lennie2003_cortex_energy_cost` — extension to human cortex. Not in seed.
- `niven2007_neural_energy` — energy-efficient sparse coding. Not in seed.
- `levy_baxter1996_energy_efficient_neural` — optimal firing rates for energy efficiency. Not in seed.
- `stemmler_koch1999_information_per_spike` — information per spike under energy constraints. Not in seed.
- `harris_jolivet_attwell2012_brain_energy_review` — modern review of brain energy use. Not in seed.
- `friston2010_fep_unified_theory` — the FEP can be derived in part as energy-efficient inference. In seed, full depth.
