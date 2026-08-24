---
id: laughlin1998_metabolic_cost
title: "The metabolic cost of neural information"
authors:
  - "Laughlin, Simon B."
  - "de Ruyter van Steveninck, R. R."
  - "Anderson, J. C."
year: 1998
venue: "Nature Neuroscience"
doi: "10.1038/236"
arxiv: ""
url: "https://doi.org/10.1038/236"
tags:
  - primate-neurophysiology
  - theoretical-essay
concepts:
  - metabolic-cost-of-neural-information
  - coalition-resource-competition
related:
  - hochreiter_schmidhuber1997_lstm
  - friston2010_fep_unified_theory
  - attwell_laughlin2001_brain_energy_budget
relevance_to:
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# The metabolic cost of neural information

## 1. Abstract

The authors derive experimentally-based estimates of the energy used by neural mechanisms to code known quantities of information. Biophysical measurements from cells in the blowfly retina yield estimates of the ATP required to generate graded (analog) electrical signals that transmit known amounts of information. Energy consumption is several orders of magnitude greater than the thermodynamic minimum. It costs ≈10⁴ ATP molecules to transmit a bit at a chemical synapse, and ≈10⁶–10⁷ ATP for graded signals in an interneuron or a photoreceptor, or for spike coding. Therefore, in noise-limited signaling systems, a weak pathway of low capacity transmits information more economically than a strong pathway of high capacity, which promotes the distribution of information among multiple pathways.

## 2. Why this matters for us

This is the foundational paper for the user's competition-emergent-PC theoretical thesis ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5, step 1: "resource scarcity"). The user's program rests on the claim that the brain operates under strict metabolic and bandwidth constraints, which forces neural coalitions to compete for these resources, which in turn motivates predictive coding as a strategy for winning that competition. Laughlin et al. 1998 is the empirical anchor for "the brain is metabolically constrained" — it puts specific numbers (ATP per bit) on the cost of neural information processing. Without this paper, the resource-scarcity premise is a plausible-sounding assertion; with it, the premise is a quantitative fact about neural biophysics.

## 3. Key claims

1. The thermodynamic minimum cost of transmitting a bit of information (the Landauer limit, $kT \ln 2 \approx 3 \times 10^{-21}$ J) is many orders of magnitude smaller than the cost real neurons pay.
2. **Chemical synaptic transmission.** Transmitting one bit through a chemical synapse — including vesicle release, postsynaptic potential generation, and the active processes that maintain ion gradients — costs ≈10⁴ ATP molecules. This is several orders of magnitude above the Landauer limit.
3. **Graded signaling.** Transmitting one bit through graded analog signaling in an interneuron or photoreceptor costs ≈10⁶–10⁷ ATP molecules. The high cost reflects the energetic requirements of maintaining ion-gradient steady states across continuously active channels.
4. **Spike coding.** The cost of spike-based signaling is intermediate, dominated by Na⁺/K⁺-pump activity restoring the ion gradients after each action potential. Per bit, spike coding is more expensive than chemical synaptic transmission but cheaper than maximum-rate graded signaling.
5. **Architectural implication.** In a metabolically-constrained, noise-limited system, *distributing* information across many low-capacity pathways is more energy-efficient than concentrating it in a few high-capacity pathways. The optimum is highly distributed coding with redundancy — a prediction directly relevant to cortical architecture, which is exactly distributed and redundant.
6. The brain's actual energy budget is dominated by signaling, not by housekeeping. Synaptic transmission and action-potential generation together account for the majority of cerebral ATP consumption (estimates from later work converge on ≈75% of brain energy use). This means the metabolic constraint on neural computation is severe and directly couples to architectural choices.

## 4. Methods

The authors combine three sources of data: (a) electrophysiological recordings from blowfly retinal photoreceptors and large monopolar cells (LMCs), giving direct measurements of the information rate (bits per second) of these cells; (b) biophysical estimates of the ATP cost of maintaining the resting potential, generating graded responses, and chemical synaptic transmission in these cells; (c) thermodynamic calculations of the minimum cost (Landauer limit). The fly retina is an exceptionally well-characterized system at the time of the paper, with quantitative information-theoretic and biophysical measurements available, which is why the authors use it as the empirical anchor.

They divide ATP cost by information rate to estimate ATP-per-bit. The estimates are then extrapolated to mammalian cortex via known scaling relationships (cell density, firing rates, synaptic counts).

## 5. Results

The principal quantitative results:

- ATP cost per bit at a chemical synapse: ≈10⁴ ATP molecules.
- ATP cost per bit for graded signaling: ≈10⁶–10⁷ ATP molecules.
- ATP cost per bit for spike coding: intermediate, dominated by Na⁺/K⁺ pump activity.
- The thermodynamic minimum (Landauer limit): ≈3 × 10⁻²¹ J per bit, equivalent to roughly 1 ATP-equivalent per ~10⁴ bits — i.e., the neural system is ≈10⁸–10¹¹ times above the Landauer limit.
- The implication for distributed vs concentrated coding: in noise-limited regimes, $N$ weak pathways carrying $r$ bits per second each at a per-pathway cost $c$ are *more* efficient than one pathway carrying $Nr$ bits per second at cost $\propto N r^2$, because the noise floor makes high-capacity per-pathway coding super-linearly expensive.
- Brain-wide implication: the cortex's distributed redundant coding (overlapping receptive fields, population coding, redundant inter-area projections) is consistent with energy-efficient information transmission.

## 6. Critique / limitations

The estimates are from the blowfly retina. Mammalian cortex differs in cell density, firing-rate distributions, and synaptic density. Subsequent work (Attwell & Laughlin 2001) extends the analysis to mammalian gray matter and arrives at qualitatively similar conclusions (signaling dominates the energy budget), but the specific ATP-per-bit numbers are not directly portable.

The "noise-limited" assumption is load-bearing for the distributed-coding implication. In some regimes (e.g., low-firing-rate cortical neurons with high reliability per spike), the distributed-coding optimum may not apply, and concentrated high-rate coding could be more efficient.

The paper does not engage with the *computational* implications of metabolic cost beyond the information-transmission level. The question "what does the brain compute given that it can't afford to compute everything?" is implicit but not formalized. Later work (Stemmler & Koch 1999; Levy & Baxter 1996, 2002) formalizes the optimization problem more fully.

The paper does not address the user's specific extension: that *coalitions* of neurons compete for the limited resources, with predictive coding as the strategic-response mechanism. The user's program goes beyond Laughlin et al. by adding game-theoretic structure to the resource-scarcity premise; Laughlin et al. supplies the premise but not the game-theoretic extension.

## 7. Connection to our work

This paper supplies *step 1* of the user's competition-emergent-PC argument ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5 and `concepts/competition_emergent_predictive_coding.md`):

> **Step 1: resource scarcity.** The brain operates under strict metabolic and bandwidth constraints (Laughlin et al. 1998 — not yet in seed). Different neural coalitions — sensory hubs, RL hubs, default-mode-style hubs, etc. — compete for these resources to ensure their representations are maintained and used to guide behavior.

Without the quantitative grounding Laughlin et al. provides, the resource-scarcity premise is a metaphor. With it, the premise is an experimentally-supported fact: chemical synapses cost ≈10⁴ ATP per bit, spike generation costs more, and a cortex with 10¹¹ neurons firing at 1 Hz pays a metabolic price that constrains how much computation can be done where.

The architectural implications for the user's program are:

- **Distributed coding is metabolically warranted.** The user's multi-compartmental memory ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §3) maintains many parallel recurrent states with different spatial resolutions and timescales. Laughlin's distributed-coding implication is the metabolic justification: distributing computation across many medium-capacity memory layers is more energy-efficient than one giant memory layer, and the cortex apparently does this.
- **Bandwidth between hubs is limited.** The user's multi-hub architecture ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5) requires inter-hub communication via the central self-attention substrate. The communication bandwidth is metabolically constrained, which means hubs that produce signals their consumers actually need will be preferred — the architectural pressure that the user's competition argument exploits.
- **Prediction reduces transmission.** Predictive coding has, since Rao & Ballard 1999, been justified partly by the argument that *transmitting prediction errors instead of raw inputs is sparser* — i.e., it transmits fewer bits when predictions are good. Laughlin's metabolic cost-per-bit is the quantitative substrate for this argument: PC saves energy because prediction errors are sparser than raw signals.
- **Architectural pressure for sparsity and gating.** The Feedback Transformer's gating of feedback inputs ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §3, "ability to shut off feedback") is metabolically warranted: maintaining feedback channels has a cost, and channels that don't supply useful information should be silenced.

The Recurrent ViT paper (2502.10955) does not engage with metabolic constraints. The user's program does, but only at the theoretical-thesis level. Laughlin et al. 1998 is the appropriate primary citation for the resource-scarcity claim in any future manuscript that develops the competition-emergent-PC thesis.

## 8. Citations to follow

- `attwell_laughlin2001_brain_energy_budget` — extension to mammalian gray matter. *Strongly recommended for the seed.*
- `levy_baxter1996_energy_efficient_neural` — optimal-coding analysis of energy-efficient firing rates. Not in seed.
- `lennie2003_cortex_energy_cost` — cortical energy cost per neuron. Not in seed.
- `harris_jolivet_attwell2012_brain_energy_review` — modern review of brain energy use. Not in seed.
- `stemmler_koch1999_information_per_spike` — information per spike given energy constraints. Not in seed.
- `friston2010_fep_unified_theory` — the FEP can be derived in part as energy-efficient inference. In seed; full depth.
