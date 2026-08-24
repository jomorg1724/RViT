---
id: apical_basal_dendritic_integration
type: concept
title: "Apical-basal dendritic integration"
papers:
  - larkum2013_apical_basal
  - larkum_zhu_sakmann1999_bac_firing
  - jordan2023_dendritic_bayesian
  - urbanczik_senn2014_predictive_dendrite
  - bastos2012_canonical_microcircuits
  - keller_mrsic_flogel2018_pc_review
  - rao_ballard1999_predictive_coding
  - weiler2025_l6_corticocortical
source_documents:
  - "Private & Shared-4/Evolution of Architecture (§ Mechanism of Control)"
last_updated: "2026-05-18"
---

# Apical-basal dendritic integration

## Definition

The biophysical and computational mechanism by which a cortical pyramidal cell integrates two functionally distinct streams of input — *basal* input arriving near the soma (bottom-up sensory and intracortical feedforward), and *apical* input arriving distally on the apical-tuft dendrites (top-down feedback in L1, broadly distributed predictions) — into a single output that depends multiplicatively on whether the two streams co-activate. The mechanism is implemented at the single-neuron level via the **BAC** (back-propagating action potential + apical Ca²⁺) phenomenon discovered by Larkum, Zhu & Sakmann 1999 (`papers/larkum_zhu_sakmann1999_bac_firing.md`).

## The BAC mechanism

The behavior of a L5 pyramidal cell as a function of compartmental input:

| Basal input | Apical input | Soma output |
|---|---|---|
| Yes | No | Single action potential (low rate) |
| No | Yes | Small subthreshold dendritic Ca²⁺ event; no axonal output |
| Yes (somatic AP) + Apical (within ~10 ms) | — | **Burst** of 3–5 action potentials at ~100 Hz |

The coincidence detection has a temporal window of ~10 ms and is asymmetric (basal-then-apical is more effective than apical-then-basal, consistent with the apical-tuft electrotonic propagation delay).

## Architectural interpretation

The pyramidal cell is therefore an **AND gate** for top-down and bottom-up evidence. Neither stream alone is sufficient to drive a burst; *coincidence* is required. Larkum 2013 (`papers/larkum2013_apical_basal.md`) generalizes this from L5 to L2/3 and frames it as the cellular basis of cortical "associations": the cortex binds top-down predictions to bottom-up sensory input precisely when the two agree.

The architectural commitment for AI models is that *multi-source feedback integration should be multiplicative, not additive*. This is the load-bearing motivation for the Feedback Transformer's Hadamard-product structure (`concepts/feedback_transformer.md`).

## Bayesian interpretation

Jordan et al. 2023 (`papers/jordan2023_dendritic_bayesian.md`) formalizes the apical-basal dichotomy as Bayes-optimal cue integration:

- **Apical input** encodes a *prior* over the latent variable the cell represents.
- **Basal input** encodes a *likelihood* under the current sensory evidence.
- **Soma** computes the *posterior* by combining prior and likelihood with precision weighting determined by their respective conductances.

This is more than metaphor: under specific parametric assumptions (Gaussian priors and likelihoods, multiplicative conductance gain), the steady-state somatic potential exactly equals the log-posterior mean, with the posterior precision being the sum of prior and likelihood precisions. The framework provides a normative justification for multiplicative integration: it implements Bayesian inference at the cellular level.

The Urbanczik-Senn rule (`papers/urbanczik_senn2014_predictive_dendrite.md`) gives the local plasticity rule: synaptic weights update to minimize the discrepancy between the apical-dendrite-predicted spike rate and the somatic-actual spike rate. The result is a biologically-plausible local learning rule that converges to Bayes-optimal integration.

## Inhibitory gating

Larkum's framework includes inhibitory microcircuits that gate the BAC mechanism:

- **SST+ Martinotti interneurons** target the apical-tuft and suppress apical Ca²⁺. SST activity *reduces* the BAC AND-gate's sensitivity to apical input.
- **VIP+ interneurons** target SST+ cells and *disinhibit* the apical pathway, enabling BAC firing.

The inhibitory circuitry is therefore a state-dependent gate on whether top-down feedback is allowed to bind with bottom-up sensory input at a given cell. Behavioral states associated with attention and learning correlate with VIP+ activation, consistent with the framework that attention enables top-down predictions to participate in cortical computation.

This is the biological substrate of the user's architectural commitment that *feedback should be gateable* (`concepts/bidirectional_hierarchical_feedback.md`, "ability to shut off feedback"). The user's program makes feedback gateability a load-bearing design choice (it creates the incentive for cooperation between layers); Larkum's framework shows that real cortex has dedicated circuitry for exactly this gating.

## Connection to predictive coding

The relationship between apical-basal dendritic integration and predictive coding (`concepts/hierarchical_predictive_coding.md`) is unsettled. Two natural mappings:

1. **Apical = prediction, basal = evidence, soma = prediction error.** Under this mapping, the BAC burst is the signal that bottom-up evidence agrees with top-down prediction (i.e., low surprise). Cells that fire bursts are reporting "I predicted this." Cells that fire single spikes (basal-only, apical absent or wrong) are reporting "I see this, but I didn't predict it" — a prediction error.

2. **Apical = prior, basal = likelihood, soma = posterior.** Jordan et al.'s framework. Under this mapping, the burst is the posterior estimate; no explicit prediction-error neuron is needed.

The two mappings make different predictions about which cells should be tagged as "prediction error" vs "representation" cells in the Bastos 2012 canonical-microcircuit framework. The empirical adjudication is ongoing.

## Connection to other concepts

- `feedback_transformer` — the architectural-level analog of the AND-gate, with Hadamard products replacing the BAC mechanism.
- `hierarchical_predictive_coding` — the framework apical-basal integration plausibly implements at the cellular level.
- `bidirectional_hierarchical_feedback` — apical input is the cellular target of top-down feedback.
- `cortical_microcircuit_model` — Bastos 2012's laminar mapping relies on cellular integration that includes the BAC mechanism implicitly.
- `precision_weighting_attention` — the SST+/VIP+ gating of apical input implements precision weighting at the cellular level.
- `bayesian_cue_integration` — Jordan et al.'s formalization.
- `pyramidal_cell_two_compartment` — the structural commitment behind the framework.

## Open questions

1. **Does the architecture-level Feedback Transformer reproduce the cellular BAC AND-gate's computational benefits?** The Hadamard-product structure is the right architectural primitive in principle; whether it gives the same training dynamics is empirically open.
2. **Apical-prediction or apical-prior?** The two interpretations of apical input differ in what they say about cortical computation. Adjudication requires distinguishing predictions from priors at the cellular level.
3. **Is the BAC mechanism necessary or sufficient for any specific cortical computation?** Larkum 2013 catalogs many phenomena consistent with BAC firing; the necessity claims are still being tested (e.g., Takahashi et al. 2016 for S1 perception, Aru, Suzuki & Larkum 2020 for consciousness).
4. **Generalization beyond L5.** L5 pyramidal cells have the clearest BAC phenomenon. L2/3 pyramidal cells show a related but morphologically smaller mechanism. L6 corticocortical cells (Weiler 2025, `papers/weiler2025_l6_corticocortical.md`) have less elaborated apical tufts and target L1 / superficial layers of distal cortical areas — they are the dominant *long-range descending* projection class but their cellular integration mechanism is different from L5b's BAC. Weiler 2025 quantifies the L6 CC projection as a major route for the *feedback* direction in inter-areal communication; whether L6 CC cells exhibit an apical-basal coincidence-detection analog to BAC firing, or rely on a fundamentally different integration mechanism (perhaps closer to passive linear summation modulated by inhibition), is an open empirical question with direct architectural implications: if L5b's multiplicative integration is the substrate for the Hadamard-product Feedback Transformer at the *receiving* end, what is L6 CC cells' role at the *sending* end?
