---
id: senkowski_engel2024_multi_timescale_msi
title: "Multi-timescale neural dynamics for multisensory integration"
authors:
  - "Senkowski, Daniel"
  - "Engel, Andreas K."
year: 2024
venue: "Nature Reviews Neuroscience"
doi: "10.1038/s41583-024-00845-7"
arxiv: ""
url: "https://doi.org/10.1038/s41583-024-00845-7"
tags:
  - human-neuroimaging
  - primate-neurophysiology
  - review
concepts:
  - multi-sensory-integration
  - neural-oscillations-cfc
  - slow-fast-recurrence
  - top-down-feedback
  - precision-weighting
related:
  - ernst_banks2002_cue_combination
  - choi2023_msi_review
  - jordan2023_dendritic_bayesian
  - bastos2015_laminar_macaque
  - buzsaki_wang2012_gamma
  - feldman_friston2010_attention_free_energy
  - friston2010_fep_unified_theory
  - keller_mrsic_flogel2018_pc_review
relevance_to:
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# Multi-timescale neural dynamics for multisensory integration

## 1. Abstract

Carrying out any everyday task — driving in traffic, conversing with friends, or playing basketball — requires rapid selection, integration, and segregation of stimuli from different sensory modalities. At present, even the most advanced artificial intelligence systems are unable to replicate the multisensory processes that the human brain routinely performs, and how neural circuits in the brain carry out these processes is still not well understood.

In this Perspective, the authors discuss recent findings that shed fresh light on the oscillatory neural mechanisms mediating multisensory integration (MI), including power modulations, phase resetting, phase-amplitude coupling, and dynamic functional connectivity. They then consider studies suggesting multi-timescale dynamics in intrinsic ongoing neural activity and during stimulus-driven bottom-up and cognitive top-down neural network processing in the context of MI.

They propose a new concept of MI emphasizing the critical role of neural dynamics at multiple timescales within and across brain networks, enabling simultaneous integration, segregation, hierarchical structuring, and selection of information in different time windows. To highlight predictions from this multi-timescale concept, real-world scenarios in which multi-timescale processes may coordinate MI in a flexible and adaptive manner are considered.

(Nat Rev Neurosci 25(9):625–642, Sep 2024; DOI 10.1038/s41583-024-00845-7.)

## 2. Why this matters for us

Senkowski & Engel 2024 is the load-bearing review supplying the *biological* warrant for two of the user's architectural commitments: (a) the MSI hub as one of the three hubs of the multi-hub system, and (b) PRISM v2's slow/fast recurrence structure. The paper argues that multisensory integration in cortex is not a single-timescale operation but a *coordinated dance across multiple oscillatory bands* — slow (delta/theta) dynamics carry contextual / top-down structure, gamma carries bottom-up sensory transients, and phase-amplitude coupling (PAC) binds them. The user's program inherits this as the empirical pattern an MSI hub running on top of a slow/fast recurrent substrate should reproduce: fast pathway tracks transient evidence; slow pathway carries context and top-down priors; cross-frequency coupling implements the binding.

Together with `ernst_banks2002_cue_combination` (behavior) and `jordan2023_dendritic_bayesian` (cellular implementation), this paper supplies the *systems-level oscillatory description* of the same MSI computation — completing a three-level account: cell → circuit / oscillation → behavior. The user's architectural program is positioned as a *computational instantiation* of this stack, with the Feedback Transformer playing the role of the coupling substrate, the slow/fast recurrence playing the role of the multi-timescale state, and the central self-attention substrate playing the role of the binding substrate.

## 3. Key claims

The Perspective's argumentative core is the assertion that MI is irreducibly multi-timescale. The numbered claims below are the propositions a reader should be able to recite after one careful pass, distilled from the abstract and the Perspective's emphasis paragraphs.

1. **Multi-timescale MI as the core thesis.** Multisensory integration is mediated by neural dynamics operating at multiple timescales simultaneously, not by a single canonical mechanism at one timescale. Slow rhythms (delta/theta, 1–8 Hz), alpha/beta (8–30 Hz), and gamma (>30 Hz) each contribute a distinct functional role to MI.
2. **Oscillatory mechanisms of MI.** Four mechanisms recur across studies: (i) *power modulations* of band-limited activity in modality-specific and association cortices; (ii) *phase resetting* of slow rhythms by salient cross-modal events; (iii) *phase-amplitude coupling* (PAC), in which the phase of a slow rhythm modulates the amplitude of a faster rhythm; and (iv) *dynamic functional connectivity* across regions reconfiguring on timescales of hundreds of milliseconds.
3. **Slow rhythms structure long time windows.** Delta/theta phase organizes the temporal windows during which cross-modal binding can occur. Phase resetting by one modality (e.g., an audio onset) primes integration of a temporally proximate stimulus in another modality (e.g., a coincident visual flash).
4. **Gamma carries bottom-up content.** Gamma-band activity is locally generated and tracks fine-grained sensory content. PAC between slow phase and gamma amplitude is the proposed binding mechanism: the slow rhythm gates the gamma "packets" of information that get bound together.
5. **Bottom-up vs. top-down asymmetry across frequencies.** Building on Bastos et al. 2015 and related laminar/frequency-channel work, the authors endorse the view that feedforward sensory signals are carried predominantly in gamma, while feedback top-down signals (predictions, expectations, attention) are carried predominantly in alpha/beta. MI sits at the convergence of these channels.
6. **Intrinsic ongoing activity matters.** Pre-stimulus oscillatory state (alpha power, theta phase) predicts trial-by-trial MI outcomes: the brain is never a passive integrator; its endogenous multi-timescale state biases what gets bound.
7. **Network-level dynamic FC.** Functional networks supporting MI are not fixed; they reconfigure adaptively across stimuli and tasks. The same cortical sites can participate in different transient coalitions depending on the multi-timescale context.
8. **Predictive / Bayesian framing.** The multi-timescale account is consistent with — and partially subsumes — Bayesian precision-weighting accounts of MI: precision is implemented by the gain of gamma-band activity, modulated by the phase / power of slower rhythms carrying priors and attentional set.
9. **Segregation as well as integration.** A multi-timescale account naturally explains *segregation* alongside integration: stimuli falling into separate temporal windows defined by slow-rhythm phase do not get bound, even if they share modality content. The framework therefore handles the "binding problem" and the "segregation problem" symmetrically.
10. **Adaptivity / context-sensitivity.** Which timescale dominates MI at any moment depends on task, context, and arousal. The framework predicts no fixed band assignment for any cortical site; the same site can switch role with context.
11. **Network-level rather than region-level.** No single "MI region" carries the integration; the operation is distributed across a coordinated network reconfiguring on the fly. Region-based attributions (e.g., "superior temporal sulcus is the MI hub") are reframed as *transient nodes in a dynamic graph*, not fixed loci.
12. **Bridging to AI.** The authors note explicitly that contemporary AI systems do not replicate human MI; the implicit claim is that the multi-timescale framework is what such systems are missing. This is the gap the user's program targets — not by claiming biological fidelity, but by instantiating the structural ingredients (multiple timescales, gating substrate, top-down feedback, cross-modal projection) that the framework identifies as essential.

## 4. Methods

This is a Perspective / review article in *Nature Reviews Neuroscience*, not an experimental paper. The "methods" are therefore the conceptual integration the authors perform across a body of prior work. Concretely, they synthesize:

- **Electrophysiology in humans (EEG, MEG, intracranial ECoG/sEEG).** Studies measuring oscillatory power, phase, PAC, and coherence during audiovisual, audiotactile, and visuotactile tasks. The intracranial work in epilepsy patients is particularly load-bearing because it gives the spatial resolution needed to map band-specific activity to cortical sites.
- **Animal electrophysiology (rodent, NHP).** Studies of laminar profiles, LFP–LFP coherence, and granger-causal directionality across frequency bands (e.g., Bastos-style feedforward-gamma / feedback-alpha-beta findings). These provide the circuit-level mapping that human imaging cannot.
- **Computational models.** Coupled-oscillator and predictive-coding models that account for cross-modal binding and rivalry. The authors lean on coupled-oscillator formalism to motivate the PAC story without committing to a single computational instantiation.
- **Real-world / naturalistic paradigms.** Speech-in-noise, audiovisual scene perception, ecologically valid multimodal stimuli. These are presented as the *target* regime the multi-timescale framework is designed to explain, in contrast to the simplified flashes-and-beeps designs that dominate the foundational MI literature.
- **Behavioral psychophysics.** Used as the link to Ernst-Banks-style precision-weighting and to the temporal-binding-window literature (the question of how wide a window the brain integrates across, and how the window's width depends on stimulus and context).

From these sources the authors derive a *single conceptual framework*: MI as the coordinated multi-timescale activity of distributed networks, with explicit functional roles assigned to slow, intermediate, and fast bands. The framework explicitly subsumes earlier proposals (modality-specific binding regions, single-rhythm accounts of attention) as special cases or partial views.

The novel theoretical contribution is the framework itself; the empirical support is drawn from prior work cited throughout. The Perspective format permits this kind of synthesis but constrains the depth of any single line of evidence — the reader who wants chapter-and-verse must follow the in-text citations.

## 5. Results

Being a review, this paper does not present new data. The principal *conceptual results* — the take-aways a reader should be able to recite — are summarized below. They are organized not by experimental finding (the paper does not present new experiments) but by the cross-study consensus the authors extract from existing literature.

- **Frequency–function mapping.**
  - Delta/theta (1–8 Hz) → temporal scaffolding and cross-modal phase alignment.
  - Alpha/beta (8–30 Hz) → top-down predictions, attentional gating, suppression of irrelevant modalities.
  - Gamma (>30 Hz) → bottom-up sensory content, locally generated, PAC-bound to slow phase.
- **PAC as the binding operation.** Phase-amplitude coupling between slow phase and gamma amplitude is identified as the canonical neural implementation of cross-modal binding within a temporal window.
- **Phase resetting as the alignment operation.** A salient onset in one modality resets the phase of slow rhythms in target cortices, opening a temporal window for integration of stimuli in other modalities.
- **Pre-stimulus state predicts MI.** Trial-by-trial variability in MI outcomes is predicted by pre-stimulus oscillatory state (e.g., alpha desynchronization predicts better binding); the brain's intrinsic multi-timescale activity is a real factor, not noise.
- **Multi-timescale account unifies findings.** A single multi-timescale framework can explain heterogeneous prior findings on MI that look conflicting under a single-timescale account.
- **Predictions for further study.** Real-world scenarios — speech-in-noise, scene perception, social interaction — should show characteristic multi-timescale signatures; lesions or perturbations targeting specific bands should produce specific MI deficits.
- **Disease relevance.** The framework gestures at clinical relevance: schizophrenia and autism are characterized in part by aberrant cross-frequency coupling and MI deficits. Whether these are *causes* or *correlates* of the disorders is unsettled, but the framework supplies a vocabulary for asking the question.
- **Hierarchical structuring.** The slow rhythms are not just "containers" for fast packets — their hierarchical nesting (delta ⊂ theta ⊂ alpha ⊂ beta ⊂ gamma in terms of period) corresponds to a hierarchy of *temporal scopes* over which integration can occur. This nesting is the systems-level analog of cortical hierarchy.
- **Selection and segregation are dual to integration.** The same multi-timescale machinery that binds cross-modal stimuli into a single percept also *segregates* unrelated streams. Within-window content gets integrated; across-window content gets separated. Binding and segregation are the two sides of one mechanism, not separate operations.
- **Temporal-binding window plasticity.** The width of the cross-modal binding window is not fixed; it adapts to task demands, training, and developmental state. The framework attributes this plasticity to changes in slow-rhythm frequency and PAC strength rather than to changes in feedforward connectivity.

## 6. Critique / limitations

The framework is *descriptive* rather than mechanistic, and this is the dominant limitation. Identifying that gamma carries bottom-up content and slow rhythms carry context tells us *what* the bands do at the population level, but does not yet say *how* — what circuitry, what synaptic dynamics, what learning rules produce this assignment. Bastos et al. 2015 and the canonical-microcircuit literature partially fill this gap; the synthesis is still incomplete.

The mapping from frequency band to function is *correlational*. Most evidence comes from observational electrophysiology where stimulus, attention, and arousal covary with band-limited activity. Causal manipulations (TMS, tACS, optogenetics by band) are sparser and produce mixed results. The strong functional claims — "gamma carries bottom-up", "alpha carries top-down" — are probably too clean.

The article is *anthropocentric*. The strongest evidence is from human MEG/EEG, where spatial resolution is limited; the mapping to circuit-level mechanisms relies on animal homologies that are themselves contested.

The Bayesian / precision-weighting framing is *handwavy*. The authors gesture toward Bayesian accounts but do not commit to a specific computational implementation linking precision to band power / PAC strength. A reader looking for a derivation will not find one here.

The framework is, by its review nature, *open enough to accommodate almost any finding*. This is both a virtue (it organizes a heterogeneous literature) and a liability (it makes few hard, falsifiable predictions about specific experiments). The most testable claims are the band-specific perturbation predictions, but these are largely not yet executed.

Finally, the paper says little about *artificial-intelligence implementations*. The opening claim that AI systems cannot replicate MI is gestural; the paper does not engage with what an AI architecture would need to look like to instantiate the multi-timescale framework. This is the gap our program is positioned to address. A reader interested in *how to build* a multi-timescale MSI substrate gets ideas about *what* the substrate has to do, but no architectural blueprint.

A related concern: the band-to-function mapping (gamma ↔ bottom-up, alpha/beta ↔ top-down, delta/theta ↔ scaffolding) is presented as a near-canonical story, but the underlying evidence is more equivocal than the framework suggests. Gamma in some sensory areas behaves more like a local-noise floor than a content carrier; alpha can index inhibitory gating *or* maintenance, and the two are not the same; delta phase can reflect attention, prediction, or motor readiness depending on task. The multi-timescale framework is most useful as a *scaffold for hypothesis generation* rather than a finished theory.

## 7. Connection to our work

Senkowski & Engel 2024 is one of the strongest biological warrants in the database for the user's architectural program. Three specific connections:

**The MSI hub of the multi-hub system.** The user's [multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md) commits to an MSI hub as one of three competing hubs (MSI / RL / VAE) feeding into a central self-attention substrate. Senkowski & Engel argue that biological MI is a *distributed multi-timescale process* — not a localized computation in a "binding region" but a coordinated dynamic across networks. The user's MSI hub, implemented as a parallel recurrent unit communicating with other hubs through the [feedback-transformer](research_db/concepts/feedback_transformer.md), is structurally compatible with this: it is a *process*, not a place. The hub maintains its own recurrent state and exchanges information with other hubs at every layer through Q/K/V projections — the architectural analog of cross-network coupling.

**Slow/fast recurrence.** PRISM v2's slow-fast memory commitment (`PRISM_V2_PROPOSAL.md` §3.3) — a fast pathway tracking transient evidence plus a slow pathway carrying context — directly mirrors Senkowski & Engel's frequency-function mapping. The fast PRISM pathway corresponds to the gamma channel (bottom-up sensory content); the slow pathway corresponds to alpha/beta and delta/theta (top-down priors, contextual scaffolding). Cross-frequency coupling (PAC) is the biological analog of how PRISM v2's slow state modulates / gates the fast state. The user's program inherits the Senkowski–Engel architectural commitment to *two-or-more timescales coordinated by a coupling mechanism*. The paper supplies the empirical warrant that this is what cortex actually does. The MCLSTM kinetic-gate finding from `project_mclstm_architecture_findings` — that the gate must point in a specific direction relative to memory_compute — is one architectural-level reflection of the same constraint: a coupling between memory states only works if its phase relationship to the content stream is correctly set up.

**Central self-attention as binding substrate.** The user's commitment to a *central self-attention mechanism* into which all hubs project Q/K/V is the architectural counterpart of Senkowski & Engel's *dynamic functional connectivity* and *PAC-mediated binding*: a flexible substrate over which any subset of sources can be transiently combined. Self-attention's softmax-weighted mixing over tokens is mathematically homologous to PAC's slow-phase-gated mixing of gamma packets: in both, a slow / contextual variable selects which fast / content tokens participate in the current binding. This homology is not coincidental — both implement *gain-modulated selection over a substrate of fast content*. The Feedback Transformer's multiplicative integration of hub-specific feedback into the Q/K projections is the architectural extension: instead of a single slow-phase variable gating a single fast-amplitude variable, multiple hubs simultaneously gate the same content tokens through element-wise Hadamard products before softmax. The structural commitment is therefore *PAC at scale, generalized to many simultaneous gating sources*.

**Top-down feedback as alpha/beta.** The Feedback Transformer's commitment to integrating top-down feedback streams as Q/K/V contributions aligns with the Bastos-style alpha/beta feedback story that Senkowski & Engel endorse. The user's `bidirectional-hierarchical-feedback` is the architectural instance: descending projections (top-down) and ascending projections (bottom-up) carry different signals and use the Feedback Transformer to integrate them. Senkowski & Engel's mapping of feedforward → gamma and feedback → alpha/beta is the biological signature this architectural choice predicts and should be tested against. A future analysis would extract from a trained recurrent ViT the *update rates* of descending vs ascending streams and check whether they show analogous frequency asymmetry — fast updates on ascending (gamma-like), slow updates on descending (alpha/beta-like).

**Precision-weighting via slow gating of fast.** Ernst & Banks 2002 ([ernst_banks2002_cue_combination](research_db/papers/ernst_banks2002_cue_combination.md)) gives the behavioral pattern (precision-weighted cue combination); Jordan et al. 2023 ([jordan2023_dendritic_bayesian](research_db/papers/jordan2023_dendritic_bayesian.md)) gives the cellular implementation (conductance-based Bayesian dendrites); Senkowski & Engel 2024 gives the *systems-level oscillatory signature* of the same computation: slow rhythms carrying precisions modulate gamma-band content carrying sensory evidence. The user's architecture instantiates all three levels: behavioral pattern (the MSI hub's outputs should match Ernst-Banks), cellular substrate (precision-weighted dendritic integration in Jordan's framework as the per-neuron operation), and systems-level dynamics (slow/fast separation in PRISM v2 plus central self-attention as binding substrate). The chain — behavior ← systems ← cell — is closed enough to support targeted comparisons at every level rather than only at the behavioral output.

**Competition-emergent predictive coding under multi-timescale framing.** The user's [competition-emergent-predictive-coding](research_db/concepts/competition-emergent-predictive-coding.md) thesis (in `the_user_architectural_program` §5) recasts top-down feedback as predictions of competing coalitions' behavior. Senkowski & Engel's slow-rhythm alpha/beta top-down channel is a candidate biological signature of these predictions: slow oscillatory contributions from one coalition act as *priors over what another coalition will do*. Hub-level prediction error then has an oscillatory signature — a mismatch between the slow-rhythm prior structure and the actual gamma content of a competitor. This is a non-trivial empirical prediction the user's program could test by inducing multi-hub conflict in a trained system and inspecting whether the resulting "prediction error" signals are distributed across hubs in a way that maps onto Senkowski-Engel's frequency-channel taxonomy.

**The recurrent ViT.** The published Recurrent ViT (2502.10955) is single-modality and runs a single timescale, but the architectural primitive (memory feedback into self-attention) is exactly what generalizes to a multi-timescale, multi-modality system. The user's program treats the published paper as a single-timescale, single-modality slice of a multi-timescale, multi-modality architecture whose biological warrant is supplied here.

**Phase-amplitude coupling as central self-attention.** The mathematical homology deserves a longer treatment. In PAC, slow-rhythm phase $\theta_s(t)$ gates the amplitude of fast-rhythm packets $a_f(t)$ — concretely, $a_f(t) \approx g(\theta_s(t)) \cdot a_f^{\text{raw}}(t)$ for some gating function $g$ peaking at preferred phases. In self-attention, slow / contextual queries $q$ gate the amplitude of fast / content values $v$ — concretely, $v_i^{\text{eff}} = \text{softmax}(q^\top k_i / \sqrt{d}) \cdot v_i$. Both compute *gain-modulated selection*: a slow / context variable picks which fast / content tokens are read out into the next stage. The architectural implication is that *self-attention is, at a high level, the right computational substrate for the multi-timescale framework*. The user's architectural program inherits this homology as a deep reason — not just a convenience — for committing to self-attention plus multi-timescale recurrent feedback rather than to LSTM-only architectures.

**Falsifiable predictions for the architecture.** If the multi-timescale framework is right, several predictions follow for the user's program:

1. An MSI hub running on a single timescale should underperform one with explicit slow/fast separation, especially on tasks with cross-modal context (e.g., audiovisual speech).
2. Within the slow/fast architecture, ablating the slow pathway should impair *binding across temporal gaps* more than it impairs *instantaneous fusion*; ablating the fast pathway should produce the inverse pattern.
3. The central self-attention layer's attention weights should show a temporal structure analogous to slow-phase gating: weights concentrate within "windows" set by the slow state, rather than uniformly across the sequence.
4. Lesioning specific cross-modal feedback streams (e.g., disabling audio→visual top-down feedback while leaving visual→audio intact) should produce asymmetric MI deficits that mirror the lesion/perturbation findings the multi-timescale framework anticipates.
5. Pre-stimulus / pre-event hidden state should *predict trial-by-trial MI outcomes* analogously to the human pre-stimulus oscillatory state.
6. Training with explicit cross-modal binding objectives should yield emergent PAC-like coupling between slow and fast pathway state variables — a measurable, predicted signature.

The user's architecture is *expressive enough* to instantiate all of these tests, which is a non-trivial property: most contemporary deep-learning MSI baselines are not.

## 8. Citations to follow

- `bastos2015_laminar_macaque` — laminar / frequency-channel asymmetry of feedforward gamma vs feedback alpha/beta; load-bearing for the multi-timescale framework. In seed, partial depth.
- `buzsaki_wang2012_gamma` — mechanisms of gamma oscillations; underlies the bottom-up gamma claim. In seed, stub.
- `choi2023_msi_review` — complementary MSI review with circuit/connectivity emphasis. In seed, stub.
- `ernst_banks2002_cue_combination` — behavioral precision-weighting target. In seed, full.
- `jordan2023_dendritic_bayesian` — cellular substrate for Bayesian cue combination. In seed, full.
- `friston2010_fep_unified_theory` — variational-Bayes / precision-weighting framework subsuming MI. In seed.
- `feldman_friston2010_attention_free_energy` — attention as precision-weighting; bridges to oscillatory precision. In seed.
- `lakatos_chen2008_phase_reset_attention` — phase-reset / oscillatory-attention foundational study. Not in seed.
- `schroeder_lakatos2009_low_frequency_attention` — delta/theta as instrument of attention and MI. Not in seed.
- `canolty_knight2010_pac` — phase-amplitude coupling as a binding mechanism. Not in seed.
- `fries2015_communication_through_coherence` — CTC framework as the cross-region coupling story behind dynamic FC. Not in seed.
- `keller_mrsic_flogel2018_pc_review` — predictive coding review tying precision to gain. In seed.
- `vanrullen2016_perceptual_cycles` — perception as a rhythmic / cyclic process; complementary multi-timescale view. Not in seed.
- `helfrich_knight2016_oscillatory_dynamics_pfc` — top-down oscillatory control from PFC. Not in seed.
