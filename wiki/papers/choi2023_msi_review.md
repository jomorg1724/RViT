---
id: choi2023_msi_review
title: "Multisensory integration in the mammalian brain: diversity and flexibility in health and disease"
authors:
  - "Choi, Inah"
  - "Demir, Ilsong"
  - "Oh, Seungju"
  - "Lee, Seung-Hee"
year: 2023
venue: "Philosophical Transactions of the Royal Society B"
doi: "10.1098/rstb.2022.0338"
arxiv: ""
url: "https://doi.org/10.1098/rstb.2022.0338"
tags:
  - primate-neurophysiology
  - review
concepts:
  - multi-sensory-integration
  - bayesian-cue-integration
  - top-down-feedback
  - cortico-thalamo-cortical-loops
related:
  - ernst_banks2002_cue_combination
  - senkowski_engel2024_multi_timescale_msi
  - jordan2023_dendritic_bayesian
  - bays2024_wm_representation
  - sherman2022_ctc_loop
  - schneegans_bays2017_feature_binding_wm
  - desimone_duncan1995_biased_competition
  - feldman_friston2010_attention_free_energy
  - friston2010_fep_unified_theory
  - mckinnon_mo_sherman2025_transthalamic_v1
  - reynolds_heeger2009_normalization
  - sherman_guillery2011_distinct_functions
relevance_to:
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# Multisensory integration in the mammalian brain: diversity and flexibility in health and disease

## 1. Abstract

Multisensory integration (MSI) occurs in a variety of brain areas, spanning cortical and subcortical regions. In traditional studies on sensory processing, the sensory cortices have been considered for processing sensory information in a modality-specific manner. The sensory cortices, however, send the information to other cortical and subcortical areas, including the higher association cortices and the other sensory cortices, where the multiple modality inputs converge and integrate to generate a meaningful percept. This integration process is neither simple nor fixed because these brain areas interact with each other via complicated circuits, which can be modulated by numerous internal and external conditions. As a result, dynamic MSI makes multisensory decisions flexible and adaptive in behaving animals. Impairments in MSI occur in many psychiatric disorders, which may result in an altered perception of the multisensory stimuli and an abnormal reaction to them. This review discusses the diversity and flexibility of MSI in mammals, including humans, primates and rodents, as well as the brain areas involved. It further explains how such flexibility influences perceptual experiences in behaving animals in both health and disease. This article is part of the theme issue 'Decision and control processes in multisensory perception'.

## 2. Why this matters for us

Choi et al. 2023 is the recent synoptic review of *where* and *how* multisensory integration occurs in the mammalian brain. For the user's program, the central design commitment is that MSI is not a one-shot computation at a single late-stage convergence node but a *distributed, multi-site, dynamically-modulated* process spanning early sensory cortices, higher association cortices, and subcortical structures. This is the empirical grounding the user's multi-hub system needs: the MSI hub is not a single layer hanging off a unimodal stack but a *substrate* that influences and is influenced by every other hub through bidirectional connectivity.

The review also frames MSI as flexibly modulated by internal state (attention, expectation, task) and lesionable in disease — exactly the kind of architecture the user proposes when arguing that the central self-attention map should be the cross-modal binding site, with modality-specific hubs feeding into it. The Bayes-optimal cue-combination framework (Ernst & Banks 2002; Jordan et al. 2023) is endorsed as the closest available unifying account, providing the computational-level commitment that links the user's MSI hub to the broader Bayesian-integration tradition.

## 3. Key claims

1. **MSI is multi-site, not single-site.** Multisensory integration occurs across many cortical and subcortical regions, including primary sensory cortices (V1, A1, S1), higher association cortices (parietal, prefrontal, temporal), and subcortical structures (superior colliculus, thalamus including pulvinar and posterior medial nucleus, basal ganglia).
2. **Early sensory cortices are themselves multisensory.** Contrary to the classical view that primary sensory cortices are strictly unimodal, the review documents that V1 receives auditory and somatosensory inputs (direct corticocortical and via thalamus) and A1 reciprocally receives visual inputs; integration begins at the first cortical stage.
3. **Multiple integration architectures coexist.** Three integration motifs are catalogued: direct corticocortical (sensory-sensory cortex projections), transthalamic (sensory cortex → higher-order thalamus → second sensory cortex), and converging at association cortex (parietal, prefrontal). These motifs operate in parallel, not sequentially.
4. **MSI is gated by attention and expectation.** Top-down signals from prefrontal and parietal cortex modulate when and how cross-modal information is bound. The same physical stimulus pair can be integrated or segregated depending on task demands, attention allocation, and prior expectations.
5. **The temporal-binding window is flexible.** Whether two cross-modal events are bound depends on a temporal coincidence window of tens to hundreds of milliseconds whose width is itself modulated by experience, attention, and pathology.
6. **Causal-inference framework.** Behavioral and neural data align with a Bayesian *causal-inference* model in which the brain infers whether two sensory signals share a common source; when they do, they are integrated with precision-weighting (Ernst-Banks style), and when they don't, they are kept segregated. The framework extends Bayes-optimal cue combination to allow modality segregation as well as integration.
7. **MSI is impaired in psychiatric disorders.** Altered MSI is documented in autism spectrum disorder, schizophrenia, and Parkinson's disease, often via altered temporal-binding-window width and altered top-down modulation of early sensory areas; behavioral consequences include hallucination-like percepts (McGurk effect anomalies, sound-induced flash illusion abnormalities). The review frames altered MSI as a contributing mechanism to symptom formation, not merely an epiphenomenon.
8. **Rodent models are now tractable for circuit-level MSI.** Recent rodent work (with optogenetics, two-photon imaging, and cell-type-specific manipulation) has shown that the same MSI principles operate in mice, opening circuit-level causal access to mechanisms previously studied only correlationally in humans and primates.
9. **Inverse-effectiveness and spatiotemporal congruence are organizing principles.** Multisensory enhancement is largest when single-modality inputs are weakest (inverse-effectiveness) and requires spatial and temporal alignment between modalities; mismatch produces suppression. These regularities hold across the regions surveyed and are predicted by Bayes-optimal accounts.
10. **Cell-type-specific MSI in cortex.** Layer-5 pyramidal cells, layer-6 corticothalamic neurons, and parvalbumin-positive interneurons play distinguishable roles in early-sensory-cortex MSI; the review highlights how rodent cell-type-specific manipulations are beginning to dissociate these contributions.
11. **MSI is bidirectional, not just bottom-up convergence.** Top-down feedback from association cortex back to early sensory cortex shapes cross-modal responses just as much as bottom-up convergence does; binding is a circuit-level dialogue rather than a one-way pipeline.

## 4. Methods

The paper is a review; no new data. The authors synthesize human psychophysics, human neuroimaging (fMRI, EEG, MEG), non-human primate electrophysiology, and rodent circuit dissection (optogenetic / chemogenetic / two-photon) studies. The organization is twofold: by brain region (early sensory cortices, higher association cortices, subcortical structures including superior colliculus and higher-order thalamus) and by integration motif (direct corticocortical, transthalamic via higher-order thalamus, and association-cortex convergence).

For each region, the review summarizes (i) anatomical evidence for cross-modal input (tracer studies, viral labeling), (ii) functional evidence for integrative responses (unisensory vs bimodal response comparisons, superadditivity, inverse-effectiveness), (iii) behavioral consequences of disruption (lesion, pharmacological inactivation, optogenetic silencing), and (iv) clinical relevance in psychiatric and neurological disease (autism spectrum disorder, schizophrenia, Parkinson's). Where computational accounts exist (Bayes-optimal cue combination, causal inference), the review summarizes them but does not commit to a single formalism. The review's scope is explicitly mammalian: humans, primates, rodents — invertebrate and non-mammalian vertebrate work is not included.

## 5. Results

The principal findings collated in the review:

- **V1 multisensory responses.** Auditory and somatosensory stimuli modulate V1 firing rates in rodents and primates. In mice, auditory cortex sends direct projections to V1 that target deep layers and modulate visual response gain. The integration is *modulatory* (gain-changing) rather than driving in primary sensory cortex.
- **A1 cross-modal modulation.** Visual stimuli speed up auditory responses and sharpen frequency tuning in A1; the source is partly direct V1 → A1 corticocortical and partly transthalamic via posterior thalamus.
- **Higher-order thalamus as MSI hub.** Pulvinar (visual-associated) and posterior medial nucleus (somatosensory-associated) carry cross-modal information; they receive driver inputs from layer 5 of one sensory cortex and project to another. The transthalamic motif (Sherman / Guillery) is a major MSI substrate.
- **Superior colliculus.** Classical site of MSI; deep layers contain multisensory neurons whose response to combined cross-modal input exceeds the sum of unisensory responses (superadditivity) when stimuli are spatially and temporally coincident.
- **Association cortices.** Posterior parietal cortex, prefrontal cortex, and superior temporal sulcus are convergence sites where modality-specific information is recoded into modality-independent format for decision-making.
- **Causal inference behaviorally.** Multiple psychophysical experiments are consistent with the Körding-Shams causal-inference model: subjects integrate stimuli when they could plausibly share a source and segregate them when they couldn't. Neural correlates of the causal-inference computation are found in parietal cortex.
- **Disease signatures.** Autism: narrower temporal-binding windows in some tasks, wider in others; altered McGurk susceptibility. Schizophrenia: widened temporal-binding windows; greater susceptibility to cross-modal illusions; altered top-down modulation of early sensory cortex. Parkinson's: altered cross-modal cuing effects on motor preparation.
- **Inverse-effectiveness.** Multisensory enhancement is largest when individual unisensory responses are weakest — a quantitative regularity observed in superior colliculus and replicated in cortical MSI neurons; aligns with the Bayes-optimal prediction that integration helps most when no single cue is reliable.
- **Spatial congruence.** Cross-modal enhancement requires approximate spatial alignment between modalities; spatially mismatched stimuli produce response suppression rather than enhancement.

Quantitative regularities cited:

- **Superadditivity index.** Multisensory enhancement in superior-colliculus neurons can exceed the linear sum of unisensory responses by 50-200% when stimuli are spatiotemporally coincident; the index drops to near-additivity or subadditivity when coincidence is reduced.
- **Temporal-binding window.** Behavioral binding windows are on the order of 100-300 ms for audiovisual stimuli in healthy adults; widened by tens of milliseconds in schizophrenia.
- **Reaction-time speeding.** Cross-modal stimulus pairs speed responses relative to unimodal stimuli by typically 30-50 ms in detection tasks, beyond what statistical-facilitation race models alone predict.

## 6. Critique / limitations

As a review, the paper inherits the limitations of the underlying literature. Several load-bearing inferences depend on correlation rather than causal manipulation: most human-imaging work is correlational, and even primate electrophysiology only rarely combines lesion or microstimulation with MSI tasks. The recent rodent work cited closes this gap only partially — cell-type-specific manipulations target broad classes (parvalbumin interneurons, layer-5 pyramidal cells) rather than the projection-defined populations one would need to dissociate, e.g., direct corticocortical from transthalamic MSI routes.

The review treats MSI as a *family of mechanisms* rather than a single computation. This is honest about the empirical state of the field but means the review does not commit to a unifying mathematical framework. The causal-inference / Bayesian-integration thread is the closest the review comes to a unifying account, but it is presented as one perspective among many rather than as the canonical formalism.

The cortical-region-by-region organization risks obscuring the *dynamic* nature of MSI: the same physical region (e.g., parietal cortex) can act as either an integration site or a segregation site depending on task demands. The review acknowledges this but its taxonomy by region can read as if MSI has fixed loci.

Cross-species comparison is uneven: rodent circuit work is rich on subcortical and early-sensory motifs but thin on high-level association cortices; primate work is rich on parietal and prefrontal MSI but lacks circuit-level access. Disease signatures are summarized but the underlying mechanistic accounts (e.g., what specifically about cortical excitation/inhibition balance produces a widened temporal-binding window in schizophrenia) remain speculative.

The review does not deeply engage the computational-modeling literature (Bayesian causal inference, divisive-normalization models of MSI, dendritic-Bayesian implementations) — it cites these but does not commit to a position. Readers looking for a computational-level commitment must turn elsewhere (Ernst & Banks 2002; Jordan et al. 2023).

The disease-mechanism discussion is illuminating but does not commit to falsifiable circuit-level predictions: knowing that the temporal-binding window is widened in schizophrenia does not, on its own, tell us which projection or cell type is malfunctioning. The review's framing leaves this open to future circuit-dissection work.

The review under-discusses *learning* of MSI: how cross-modal contingencies are acquired through experience, how the temporal-binding window is set developmentally, and how predictive learning shapes which modality combinations are integrated vs segregated. These questions are central to any architectural model that hopes to *learn* MSI rather than have it hand-wired.

## 7. Connection to our work

This paper is central to the user's architectural program in three ways:

**The MSI hub as a distributed substrate, not a single layer.** The user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) commits to an MSI hub that maintains its own recurrent state and feeds into the central self-attention map alongside RL and VAE hubs. Choi et al.'s key empirical claim — that MSI is multi-site and dynamic, with integration occurring in early sensory cortices, higher-order thalamus, association cortices, and subcortical structures — supports the user's design choice that the MSI hub should not be a single late-stage convergence module but a *substrate* with bidirectional connectivity to every level of the hierarchy. The Feedback Transformer ([feedback_transformer](research_db/concepts/feedback_transformer.md)) is the architectural primitive that admits this: each level of the visual hierarchy can take parallel feedback from the MSI hub's state at the matching spatial resolution.

**The central attention substrate as cross-modal binding site.** The user's design places a central self-attention map at the heart of the architecture, with multiple hubs competing for control of its inner-product geometry. Choi et al.'s account of association cortices (parietal, prefrontal) as multimodal convergence sites and of top-down attention as the gate that decides whether cross-modal stimuli are integrated or segregated maps directly onto this design: the central attention map is the *substrate* on which modality-specific hub contributions are combined, with task / attention demands selecting which combinations are reinforced. This is the architectural analog of the review's behavioral claim that the same stimulus pair can be integrated or segregated depending on attention and expectation.

**Bayesian cue integration as the target computation.** Choi et al. endorse the causal-inference / Bayes-optimal-integration framework as the closest available unifying account, citing Ernst-Banks-style precision-weighting ([ernst_banks2002_cue_combination](research_db/papers/ernst_banks2002_cue_combination.md)) as the foundational computation and noting that real MSI extends it with a *causal-inference* step that allows segregation as well as integration. For the user's program, this aligns Jordan et al. 2023 ([jordan2023_dendritic_bayesian](research_db/papers/jordan2023_dendritic_bayesian.md)) — the cellular implementation of Bayesian cue integration in dendrites — with the multi-hub architecture: dendritic Bayesian integration is the local mechanism, the MSI hub's recurrent state is the global mechanism, and Choi et al. is the empirical evidence that both must exist and interact.

**Transthalamic and cortico-thalamo-cortical loops.** Choi et al.'s catalog of integration motifs prominently features the transthalamic pathway (Sherman / Guillery; [sherman2022_ctc_loop](research_db/papers/sherman2022_ctc_loop.md)) as a major MSI route — layer-5 driver projections from one sensory cortex to higher-order thalamus, then driver projections back to a different sensory cortex. The user's multi-compartmental memory implements ascending and descending projections between hierarchical levels; the transthalamic motif suggests that *parallel* (cross-modality) feedback should be routed differently from *hierarchical* (within-modality) feedback. This is a design recommendation Choi et al. supplies that the current single-hub recurrent ViT and PRISM v1/v2 do not yet implement.

**Temporal flexibility and multi-timescale MSI.** Choi et al.'s claim that the temporal-binding window is flexible aligns with Senkowski & Engel 2024 ([senkowski_engel2024_multi_timescale_msi](research_db/papers/senkowski_engel2024_multi_timescale_msi.md)). The user's program's commitment to slow/fast memory (PRISM v2's dual-memory; the Hierarchical Reasoning Model analogy) provides the architectural substrate for adjustable temporal binding: faster memory tracks short coincidence windows; slower memory tracks longer-range cross-modal correlations.

**Disease as ablation.** The disease signatures Choi et al. summarize (altered binding windows in autism and schizophrenia, altered top-down modulation) are natural targets for ablation experiments in the user's architecture: removing or perturbing the MSI hub or its connectivity should produce behavioral signatures comparable to the human disease patterns. This is a clean validation pathway for the multi-hub design — disease models become a benchmark.

**Working memory as the integration buffer.** Choi et al.'s emphasis on parietal and prefrontal convergence sites connects to the working-memory literature ([bays2024_wm_representation](research_db/papers/bays2024_wm_representation.md)): the same association-cortex regions that integrate cross-modal cues also maintain working-memory traces, and the user's multi-hub system uses the central attention map as a shared substrate for both. The MSI hub's recurrent state and the working-memory representation are not separate stores in the user's design — they are projections of the same underlying competition for attention-map control. Choi et al.'s clinical observation that altered MSI in schizophrenia co-occurs with working-memory deficits is consistent with this shared substrate.

**Modulatory vs driving inputs.** Choi et al.'s observation that cross-modal inputs to primary sensory cortex are predominantly modulatory rather than driving aligns with the user's commitment that the MSI hub's contribution to the central attention map operates through gain modulation of Q/K/V (via element-wise broadcasting) rather than through additive injection. The Feedback Transformer's multiplicative integration is the architectural realization of "modulatory not driving" at the network level.

**Causal inference as competition selector.** The review's emphasis on causal inference — the brain deciding whether two cross-modal cues share a common source — fits the user's competition-emergent-predictive-coding thesis ([competition_emergent_predictive_coding](research_db/concepts/competition_emergent_predictive_coding.md)). In the user's framing, hubs compete for control of the central attention substrate; cross-modal binding amounts to coalitions of hub contributions that share a predictive model of a single underlying cause. Segregation corresponds to coalitions whose models disagree, prompting the system to maintain separate representations. The strategic-prediction-error formulation extends naturally: prediction error in one modality about another modality's expected state acts as the segregation signal.

**Superadditivity and inverse-effectiveness as benchmarks.** The quantitative regularities Choi et al. catalogs — superadditive enhancement under spatiotemporal coincidence, inverse-effectiveness when single-cue reliability is low — are empirical signatures the user's MSI hub should reproduce. Any future MSI hub instance should be tested on cross-modal detection tasks with parametric variation in cue reliability and spatiotemporal alignment, and should show the inverse-effectiveness pattern characteristic of biological MSI.

**Diversity of integration motifs as architectural redundancy.** Choi et al.'s three coexisting motifs — direct corticocortical, transthalamic, and association-convergence — supply an architectural recommendation: a single feedback channel between modality-specific hubs is insufficient. The user's design already admits multiple parallel feedback sources via the Feedback Transformer; Choi et al. supplies the empirical reason this multiplicity matters. A future multi-modal extension should instantiate at least two distinct routes (a direct hub-to-hub pathway at the same hierarchy level, and an indirect route through a higher-level "thalamic-like" relay hub that broadcasts across multiple targets).

**Implications for the iterative variational encoder–decoder.** The encoder–decoder construction is currently single-modality. Extending it to multi-modal inputs implies adding modality-specific encoders that share the central guide state $H$ but maintain modality-specific recurrent states. Choi et al.'s account of early-sensory-cortex MSI suggests the cross-modal influence should appear *early* in the encoder stack (at the V1-equivalent layer) rather than only at the late-stage guide; the user's commitment to bidirectional feedback at every layer makes this natural.

**Empirical signatures the user's program should produce.** Three predictions follow directly from Choi et al. that a trained multi-modal multi-hub system should reproduce: (i) inverse-effectiveness — cross-modal binding is strongest when unimodal evidence is weakest; (ii) flexible temporal-binding window — the effective window over which cross-modal cues are bound should be modulable by attention signals from the RL or task hub; (iii) ablation-mimics-disease — silencing the MSI hub or its connectivity should widen the binding window and increase susceptibility to cross-modal illusions, paralleling the schizophrenia signature.

**Connection to feature binding in working memory.** The cross-modal binding problem Choi et al. surveys is a generalization of the within-modality feature-binding problem ([schneegans_bays2017_feature_binding_wm](research_db/papers/schneegans_bays2017_feature_binding_wm.md); [bays2024_wm_representation](research_db/papers/bays2024_wm_representation.md)). The user's MSI hub is, by this lens, the *cross-modal* binding substrate, mirroring the within-modality feature-binding mechanism that operates at the level of working memory representation. The same mathematical machinery — competition for slot-like representational resources, precision-weighted combination — applies in both cases; this is a unifying point the user's architecture is positioned to exploit.

**Specific architectural decisions Choi et al. bears on.** First, the placement of the MSI hub's feedback target: rather than only at the top of the visual stack, feedback should reach the V1-equivalent layer too (matching the cross-modal modulation of V1 documented in §5). Second, the Q/K/V combination should be multiplicative rather than additive at the MSI hub interface (matching modulatory-not-driving). Third, the inter-hub competition framework should admit *segregation* as a learned outcome, not only integration — the causal-inference framing means that some inputs should be kept apart, and the central attention map's softmax competition naturally implements this when hub predictions disagree.

The recurrent ViT paper (2502.10955) and PRISM v1/v2 are single-modality and do not directly engage MSI. The user's program extends to multimodal architectures (Video VAE, planned audio-vision RL extensions). Choi et al. 2023 is the empirical anchor for that extension — the review every future paper from the program should cite when justifying the cross-modal architectural choices.

## 8. Citations to follow

- `koerding_shams_causal_inference` — Körding & Shams's causal-inference model of multisensory integration. Foundational to §3 claim 6. Not yet in seed.
- `stein_meredith_sc_msi` — Stein & Meredith's superior-colliculus MSI work (superadditivity, spatial-temporal coincidence). Foundational to the SC results in §5. Not yet in seed.
- `ghazanfar_schroeder2006_isthecortex_multisensory` — early argument that primary sensory cortex is multisensory. Relevant to §3 claim 2. Not yet in seed.
- `kayser_logothetis_a1_visual_modulation` — A1 visual modulation primate electrophysiology. Relevant to §5. Not yet in seed.
- `sherman_guillery2011_distinct_functions` — driver vs modulator classification underlying transthalamic motif. In seed, full depth.
- `mckinnon_mo_sherman2025_transthalamic_v1` — recent rodent transthalamic V1 dissection. In seed.
- `senkowski_engel2024_multi_timescale_msi` — temporal flexibility of MSI; oscillatory binding. In seed.
- `jordan2023_dendritic_bayesian` — cellular Bayesian-integration substrate. In seed, full depth.
- `ernst_banks2002_cue_combination` — Bayes-optimal cue combination founding paper. In seed, full depth.
- `feldman_friston2010_attention_free_energy` — variational framework for cue integration as precision-weighting. In seed.
- `wallace_stein_msi_development` — development of MSI in superior colliculus across early experience. Not yet in seed.
- `noppeney_msi_perception_review` — complementary review focusing on causal-inference behavior. Not yet in seed.
- `cao_msi_normalization_model` — divisive-normalization formal model of MSI. Relevant to the computational gap in §6. Not yet in seed.
- `beauchamp_sts_msi_human_fmri` — superior temporal sulcus MSI in human fMRI; relevant to §5 association-cortex results. Not yet in seed.
- `meijer_montijn_pennartz_audiovisual_v1` — rodent audiovisual modulation of V1; relevant to §5 V1 multisensory results. Not yet in seed.
- `tang_yoshida_dorsal_thalamic_msi` — higher-order thalamus MSI in rodent. Relevant to §5 transthalamic results. Not yet in seed.
- `wallace_murray_2019_msi_dev_review` — developmental review of MSI; relevant to the learning-of-MSI gap in §6. Not yet in seed.
- `feldman_friston2010_attention_free_energy` — variational free-energy framework subsuming Bayes-optimal cue integration; complements §3 claim 6. In seed.
- `mante_sussillo2013_pfc_context` — PFC context-dependent selection; relevant to top-down modulation of MSI in §5 and §7. In seed.
- `bizley_king_2009_visual_modulation_a1` — visual modulation of auditory cortex; foundational to §5 A1 results. Not yet in seed.
- `desimone_duncan1995_biased_competition` — biased-competition framework that grounds the user's hub-competition formalism. In seed.
- `reynolds_heeger2009_normalization` — normalization model relevant to the divisive-normalization computational gap Choi et al. leaves open. In seed.
- `friston2010_fep_unified_theory` — variational free-energy account; the natural computational embedding for the causal-inference / Bayesian-MSI framework. In seed.
