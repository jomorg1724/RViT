---
id: jordan2023_dendritic_bayesian
title: "Conductance-based dendrites perform Bayes-optimal cue integration"
authors:
  - "Jordan, Jakob"
  - "Sacramento, João"
  - "Wybo, Willem A. M."
  - "Petrovici, Mihai A."
  - "Senn, Walter"
year: 2024
venue: "PLoS Computational Biology"
doi: "10.1371/journal.pcbi.1011835"
arxiv: "2104.13238"
url: "https://arxiv.org/abs/2104.13238"
tags:
  - theoretical-essay
  - cortical-anatomy
  - bio-plausible-learning
concepts:
  - dendritic-bayesian-integration
  - multi-sensory-integration
  - bayesian-cue-integration
  - apical-dendrite-coincidence-detection
  - pyramidal-cell-two-compartment
  - apical-basal-dendritic-integration
related:
  - larkum2013_apical_basal
  - bastos2012_canonical_microcircuits
  - rao_ballard1999_predictive_coding
  - aitchison_lengyel2017_pc_bayesian
  - ernst_banks2002_cue_combination
  - friston2010_fep_unified_theory
  - urbanczik_senn2014_predictive_dendrite
relevance_to:
  - prism_v2
  - recurrent_vit
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# Conductance-based dendrites perform Bayes-optimal cue integration

## 1. Abstract

The paper proposes a Bayesian view on the dynamics of conductance-based neurons and synapses, in which the somatic potential of a pyramidal cell naturally computes a posterior distribution over latent causes by combining priors (encoded in apical-dendrite conductances) with likelihoods (encoded in basal-dendrite conductances). Apical dendrites represent prior expectations over the somatic potential; basal dendrites represent likelihoods of the somatic potential given current sensory evidence; both are parametrized by effective reversal potentials and membrane conductances. The somatic compartment naturally computes the corresponding posterior. The authors derive a gradient-based plasticity rule that enables neurons to learn target distributions and to weight synaptic inputs by their reliability — i.e., to perform optimal precision-weighting at the dendritic level. The framework explains multi-sensory integration phenomena and provides experimentally testable predictions about dendritic Bayesian computation.

## 2. Why this matters for us

Jordan et al. formalize Larkum's BAC-firing pyramidal cell ([larkum2013_apical_basal](research_db/papers/larkum2013_apical_basal.md)) as a *Bayes-optimal cue integrator*. Where Larkum 2013 establishes that pyramidal cells multiplicatively combine basal and apical input via the BAC mechanism, Jordan et al. show that this multiplicative integration is the cellular implementation of Bayesian posterior computation — basal = likelihood, apical = prior, soma = posterior. This is the cleanest published bridge between the user's Feedback Transformer (architectural commitment to multiplicative feedback integration), Larkum's pyramidal cell (cellular substrate), and the broader predictive-coding / Bayesian-brain framework (theoretical motivation). It also supplies a *learning rule* — a gradient-based plasticity rule that updates synapses so the dendritic computation tracks an actual Bayesian posterior, providing a normative justification for the multiplicative architecture.

## 3. Key claims

1. The dynamics of a conductance-based two-compartment neuron, with apical and basal dendrites separately receiving input, naturally implement a form of Bayesian inference: the somatic membrane potential approximates the log-posterior of a latent variable, with apical input contributing a log-prior and basal input contributing a log-likelihood.
2. The mapping is not merely metaphorical: under specific parametric assumptions (Gaussian priors, Gaussian likelihoods, multiplicative-conductance gain), the steady-state somatic potential exactly equals the log-posterior mean, with the posterior precision determined by the sum of prior and likelihood precisions.
3. Synaptic plasticity rules can be derived from gradient descent on the KL divergence between the dendritically-computed posterior and an externally specified target posterior. The resulting rules are *local* (each synapse updates based on locally available signals) and *biologically plausible* (consistent with experimentally-observed plasticity phenomena).
4. The framework predicts that synapses with more reliable inputs should accumulate larger weights — *not* because they fire more often but because their reliability shifts the precision of the corresponding (basal or apical) likelihood/prior factor. This is a quantitative testable prediction about cortical synaptic plasticity.
5. The framework provides a unified account of multi-sensory integration phenomena (e.g., visual-auditory cue combination in Ernst & Banks 2002 paradigms): each sensory modality contributes a likelihood factor; their multiplicative combination at the dendritic level produces the empirically-observed Bayesian-optimal cue integration in psychophysics.

## 4. Methods

Theoretical derivation grounded in conductance-based neuron dynamics. The authors model a two-compartment pyramidal cell with explicit apical-dendrite and basal-dendrite compartments, each receiving synaptic input that opens conductances at characteristic reversal potentials. They derive the steady-state somatic membrane potential as a function of the dendritic conductances and show that, under specific Gaussian-likelihood assumptions, this potential equals the log-posterior mean of a latent variable.

For the plasticity rule, they take the KL divergence between the dendritic posterior and a target posterior as a loss function and derive a gradient-descent update for the synaptic weights. The resulting rule is shown to be local (depends only on pre- and postsynaptic activity plus the compartmental voltage) and to reproduce known experimental plasticity phenomena (Hebbian plus reliability-weighting).

The framework is validated in simulations of canonical multi-sensory integration tasks: pairs of noisy cues are presented to the apical and basal dendrites, and the network is shown to converge to the Bayes-optimal posterior precision-weighted combination, with the empirically-observed scaling of behavioral precision with cue reliability.

## 5. Results

The principal theoretical and simulation results:

- The steady-state somatic potential of the conductance-based two-compartment neuron, under the specified parametric assumptions, exactly equals the log-posterior mean of a Gaussian latent given apical-prior and basal-likelihood inputs.
- The corresponding posterior precision is the sum of the prior precision (encoded in apical conductances) and the likelihood precision (encoded in basal conductances), reproducing the canonical Bayesian cue-combination formula.
- The gradient-descent plasticity rule on the dendritic KL divergence is local, biologically plausible, and converges to weights that make the dendritic posterior track an externally specified target. Convergence rates and stability properties are characterized.
- Multi-sensory integration simulations reproduce the Ernst-Banks-style cue-combination psychophysics: the perceived stimulus location is a precision-weighted average of the two modalities' inputs, with the weighting changing dynamically as the relative reliabilities are varied across trials.
- The framework predicts specific experimental signatures: synaptic strength should scale with input reliability rather than firing rate alone; apical-dendrite inactivation should specifically remove prior influence on the somatic potential (matching attentional manipulation experiments); the plasticity rule should be sensitive to the *postsynaptic compartmental voltage*, not just the somatic spike.

## 6. Critique / limitations

The Bayesian interpretation depends on specific parametric assumptions (Gaussian priors and likelihoods, multiplicative conductance gain). Real synaptic conductances are not exactly multiplicative (they're partly shunting), real neural noise is not exactly Gaussian, and real cortical computations involve multiple latent variables rather than a single scalar. The mapping is exact under the model's assumptions but approximate in real cortex.

The "two compartments" (apical, basal) idealization is simpler than real pyramidal-cell morphology, which has many dendrites with graded electrotonic coupling to the soma. Whether the Bayes-optimal property of the two-compartment model survives discretization to many compartments is not addressed.

The plasticity rule is derived under steady-state assumptions. Real neural activity is dynamic, with spikes and oscillations on timescales faster than the membrane time constant. The mapping from instantaneous voltages to a posterior distribution requires averaging that the paper does not detail experimentally.

The framework explains multi-sensory integration well but is less developed for *prediction-error* phenomena. Where Bastos 2012 and Keller-Mrsic-Flogel 2018 explicitly distinguish error-coding from representation-coding cells, Jordan et al. give every neuron a Bayesian-inference role. The relationship between Jordan's framework and explicit prediction-error neurons is not formalized.

The framework is theoretical and simulation-based. No new experimental data are presented; the testable predictions remain to be evaluated. Several predictions (synaptic-weight-tracks-reliability, apical-inactivation-removes-prior) are in principle testable but have not been definitively tested at the time of the paper.

## 7. Connection to our work

Jordan 2023 provides the *normative* justification for the user's Feedback Transformer commitment. The relevant correspondences:

- **Multiplicative integration as Bayesian.** The Feedback Transformer ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §1) combines sensory and feedback projections via Hadamard product before softmax. Jordan et al. show that this multiplicative combination is the cellular substrate of Bayes-optimal cue integration. The architectural choice is therefore not arbitrary but is the natural network-level analog of the cellular Bayesian-inference computation.
- **Apical = prior, basal = likelihood.** The user's program treats top-down feedback as predictions (priors) and bottom-up sensory input as evidence (likelihoods). Jordan et al.'s anatomical assignment (apical = prior, basal = likelihood) precisely matches the user's architectural assignment (slow-memory descending feedback = prior; V1 feedforward stem = likelihood). PRISM v2's structure ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.4, §3.10) implements this mapping at the network level.
- **Precision weighting as attention.** Jordan et al.'s prediction that synaptic weight should track input reliability is the cellular substrate of attention-as-precision-weighting. The Recurrent ViT (2502.10955) implements precision weighting at the attention-map level (cued locations get more attention weight); Jordan et al. supplies the cellular implementation.
- **Multi-sensory hub.** The user's multi-hub architecture ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5) includes an MSI (multi-sensory integration) hub. Jordan et al. directly addresses the MSI computation: it's the multiplicative combination of likelihoods from each modality, with precision weighting determining the combination weights. The MSI hub's internal computation should follow this Bayesian template.
- **Local biologically-plausible learning.** PRISM is trained with backpropagation through time; the user's program does not yet engage seriously with local-plasticity alternatives. Jordan et al.'s gradient-descent-on-KL plasticity rule is a candidate target rule for future biologically-plausible variants of the architecture.

The Recurrent ViT paper does not engage with Bayesian-brain frameworks. The user's program, in its theoretical (predictive-coding-as-emergent-from-competition) extension, does. Jordan et al. is the appropriate cellular-level citation for that extension; Larkum 2013 is the empirical cellular substrate, and Jordan 2023 is the computational interpretation of it.

## 8. Citations to follow

- `urbanczik_senn2014_predictive_dendrite` — earlier work from the same lab on a predictive plasticity rule. In seed, full depth.
- `sacramento2018_dendritic_credit_assignment` — dendritic implementation of credit assignment in deep networks. Not in seed.
- `larkum2013_apical_basal` — the cellular substrate. In seed, full depth.
- `ernst_banks2002_cue_combination` — psychophysical evidence for Bayes-optimal cue combination. In seed, full depth.
- `friston2010_fep_unified_theory` — the broader Bayesian-brain framework. In seed; full depth.
- `aitchison_lengyel2017_pc_bayesian` — relating PC to Bayesian inference. In seed.
- `petrovici2016_lif_sampling` — sampling-based Bayesian inference in spiking networks (from same lab). Not in seed.
