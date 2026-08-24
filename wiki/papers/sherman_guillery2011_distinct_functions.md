---
id: sherman_guillery2011_distinct_functions
title: "Distinct functions for direct and transthalamic corticocortical connections"
authors:
  - "Sherman, S. Murray"
  - "Guillery, R. W."
year: 2011
venue: "Journal of Neurophysiology"
doi: "10.1152/jn.00429.2011"
arxiv: ""
url: "https://doi.org/10.1152/jn.00429.2011"
tags:
  - cortical-anatomy
  - subcortical
  - theoretical-essay
  - review
concepts:
  - cortico-thalamo-cortical-loops
  - transthalamic-pathway
  - top-down-feedback
  - cortical-microcircuit-model
related:
  - sherman2022_ctc_loop
  - mckinnon_mo_sherman2025_transthalamic_v1
  - felleman_vanessen1991_hierarchical_cortex
  - bastos2012_canonical_microcircuits
  - weiler2025_l6_corticocortical
  - keller_mrsic_flogel2018_pc_review
  - rao_ballard1999_predictive_coding
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-16"
---

# Distinct functions for direct and transthalamic corticocortical connections

> **Provenance note.** Deepened 2026-05-15 from a metadata stub. Verified DOI is `10.1152/jn.00429.2011` (an earlier draft had a typo); PMID 21676936; J Neurophysiol 106(3):1068–1077, September 2011. Classified by PubMed as both Journal Article and Review. The paper is the canonical Sherman & Guillery synthesis of the driver/modulator distinction and is the conceptual root that [sherman2022_ctc_loop](research_db/papers/sherman2022_ctc_loop.md) and [mckinnon_mo_sherman2025_transthalamic_v1](research_db/papers/mckinnon_mo_sherman2025_transthalamic_v1.md) operationalize experimentally.

## 1. Abstract

Essentially all cortical areas receive thalamic inputs and send outputs to lower motor centers. Cortical areas communicate with each other by means of direct corticocortical and corticothalamocortical pathways, often organized in parallel. Sherman & Guillery distinguish these functionally, stressing that the transthalamic pathways are class 1 (formerly "driver") pathways capable of transmitting information, whereas the direct pathways vary, being either class 2 (formerly "modulator") or class 1. The transthalamic pathways provide a thalamic gate that can be open or closed (and otherwise more subtly modulated), and the inputs to the thalamus that establish these gated pathways are generally branches of axons with motor functions. Thus the transthalamic corticocortical pathways carry information about the cortical processing in one cortical area and *also* about the motor instructions currently being issued from that area and copied to other cortical areas — an efference-copy claim that is one of the paper's most consequential and controversial moves.

## 2. Why this matters for us

This paper is the conceptual root of the entire driver-versus-modulator framework on which the user's `bidirectional_hierarchical_feedback` concept rests. Two architectural commitments in the user's program — that (i) feedback into V1 should be *modulatory* rather than driving, and (ii) the cortical hierarchy is implemented by parallel direct and transthalamic routes — are both inherited from Sherman & Guillery's 2011 synthesis. Every later paper in the database that we lean on for the "feedback is FiLM-style modulation, not replacement" claim (Miller-Hansen & Sherman 2022; McKinnon, Mo & Sherman 2025; Weiler et al. 2025) is downstream of this one. The Feedback Transformer's Hadamard-product modulation of Q/K/V projections is the computational analog of the class-2 / modulator synapse described here; the paper is the empirical grounding for that choice.

## 3. Key claims

1. Synapses in cortex (and in thalamus) come in two distinguishable functional classes — class 1 ("drivers") that transmit the receptive-field-defining information, and class 2 ("modulators") that adjust the gain, tuning, or precision of that information without themselves driving suprathreshold responses.
2. Class 1 synapses are large, proximal on the dendrite, ionotropic-only (AMPA + NMDA), show paired-pulse depression, and produce all-or-nothing graded EPSPs that drive postsynaptic spikes. Class 2 synapses are small, distal, mixed ionotropic + metabotropic (mGluR), show paired-pulse facilitation, and produce subthreshold, gain-modulating responses.
3. Direct corticocortical projections are heterogeneous: some are class 1 (driver), some are class 2 (modulator). They are not, as the field had often assumed, uniformly driving.
4. Transthalamic corticocortical projections (cortex L5 → higher-order thalamus → cortex) are reliably class 1: the cortical L5 input to higher-order thalamus is a driver, and the higher-order thalamic projection back to the target cortical area is also typically class 1 from the thalamic side.
5. Because direct and transthalamic pathways operate in parallel between essentially every pair of communicating cortical areas, cortex implements *redundant, dissociable* routes for the same inter-areal communication, with different gating and modulation properties.
6. The L5 cells that drive higher-order thalamus are branched: the *same* axon that descends to brainstem motor centers also branches into the thalamus. Therefore the transthalamic signal is an *efference copy* — a copy of the motor instruction the cortical area is issuing — not just a copy of its sensory representation.
7. The higher-order thalamus acts as a *gate*: thalamic membrane state (set by class-2 modulators from L6, the brainstem, the thalamic reticular nucleus) determines whether the L5 driver is relayed to the next cortical area at all. The transthalamic route is therefore conditionally active in a way direct corticocortical routes are not.

## 4. Methods

This is a theoretical/review essay, not a primary experimental report. The authors synthesize two decades of synaptic-physiology and tract-tracing evidence from cat and rodent thalamus and cortex (much of it from their own and collaborators' labs) to argue for a generalizable class-1 / class-2 classification scheme that applies equally to thalamocortical, corticothalamic, and corticocortical synapses. The supporting evidence cited is principally:

- *In vitro slice recordings* of EPSP amplitude, paired-pulse ratio, and mGluR pharmacology that operationalize the class-1 / class-2 distinction at the level of individual synapses.
- *Anterograde tract-tracing* showing that L5 cortical projections to higher-order thalamus (pulvinar in visual, posterior medial nucleus in somatosensory, and pulvinar/mediodorsal in higher association cortex) terminate as large class-1-type boutons on proximal dendrites of thalamocortical relay cells, whereas L6 corticothalamic projections terminate as small class-2-type boutons on distal dendrites.
- *Axon-reconstruction work* (often Golgi-stained or single-axon traced) showing that L5 corticothalamic axons branch from descending motor-related axons rather than originating as pure forebrain projections — the structural evidence behind the efference-copy claim.
- *Comparative anatomy* across visual, somatosensory, auditory, and motor systems, used to argue that the same class-1/class-2 organization recurs across modalities and across mammalian species.

The argumentative move is therefore principally one of *unification*: data previously partitioned by modality or by anatomical level is re-described under a single classification scheme, and the parallelism between direct corticocortical and transthalamic pathways is presented as a general organizing principle of mammalian cortex.

## 5. Results

Because the paper is a synthesis, "results" here are the consolidated empirical generalizations the authors take to be established:

**Driver vs modulator EPSP signatures.** Class-1 (driver) EPSPs are large (often 5–10 mV from rest, sufficient to bring relay neurons or pyramidal cells to threshold), show paired-pulse depression (>30% reduction on a 50–100 ms interstimulus interval), and are blocked by AMPA + NMDA antagonists alone. Class-2 (modulator) EPSPs are small (typically <1 mV per stimulus), show paired-pulse facilitation, and recruit mGluR-mediated slow components that can shift the postsynaptic resting potential and burst-mode threshold for many seconds.

**Inputs to higher-order thalamus.** Cells in the pulvinar and posterior medial nucleus receive class-1 driver input from L5 of cortex, plus class-2 modulator input from L6 of cortex, from the thalamic reticular nucleus (GABAergic, modulatory), from cholinergic brainstem nuclei, and from local interneurons. The class-1 / class-2 architecture is preserved at every synapse along the transthalamic chain.

**L5 axon branching.** The L5 corticothalamic axon is a branch of a descending axon whose main trunk continues to spinal cord, superior colliculus, or other brainstem motor structures. The same action potential travels along both branches, so the higher-order thalamus receives — and the next cortical area, via the transthalamic relay, also receives — a temporally synchronous copy of the motor command being sent from L5.

**Parallel direct corticocortical pathways.** Direct corticocortical projections sampled across visual, somatosensory, and auditory cortex include both class-1 and class-2 boutons, with the mixture varying by area pair. Sherman & Guillery argue this means the direct corticocortical pathway carries a *mixture* of driving and modulating signals, whereas the transthalamic pathway carries a *purer* driving signal that is conditionally gated by the thalamic membrane state.

**Timescale separation.** Class-1 driver synapses act on the fast (millisecond) AMPA-NMDA timescale appropriate to relaying spike trains. Class-2 modulator synapses act on a much slower (hundreds of milliseconds to seconds) mGluR-mediated timescale appropriate to setting the gain regime, the burst-versus-tonic mode of relay cells, and the receiving cell's overall excitability. The two synaptic classes therefore not only differ in postsynaptic effect size but in temporal grain — a separation that will turn out to matter for mapping them onto the user's slow/fast memory commitments.

**Conditional gating by thalamic mode.** A thalamic relay cell can operate in tonic mode (faithful linear relay of driver input) or burst mode (high-gain, oscillatory, all-or-nothing relay), and the mode is determined by the slow class-2 modulators acting on the relay cell. The transthalamic pathway therefore has an additional degree of freedom that the direct pathway lacks: even a sustained L5 driver input can be transformed into qualitatively different downstream signals depending on the thalamic membrane state set by the modulators.

## 6. Critique / limitations

The class-1 / class-2 dichotomy is operationally crisp at the extremes (a large, depressing AMPA + NMDA bouton is unambiguously class 1) but Sherman & Guillery do not quantify how often individual boutons fall in an intermediate regime. Subsequent work has shown that some corticocortical synapses display mixed properties or short-term plasticity that depends on activity history; the binary classification is a useful abstraction, not an exhaustive taxonomy.

The efference-copy claim — that L5 corticothalamic axons are obligatory branches of motor output axons — is grounded in anatomy of a relatively small number of reconstructed axons. The claim is plausible and has been replicated in further systems (see [mckinnon_mo_sherman2025_transthalamic_v1](research_db/papers/mckinnon_mo_sherman2025_transthalamic_v1.md)), but the generality is still contested: not every L5 corticothalamic projection has been shown to originate from a motor-projecting axon, and Sherman & Guillery's broad claim sometimes outstrips the data.

The paper is theoretical: it does not establish a causal *behavioral* role for the transthalamic pathway. The functional necessity of class-1 transthalamic relay for visual perception is established only later (McKinnon, Mo & Sherman 2025 for V1; see also Roth et al. 2016 for pulvinar contributions to visual attention). The 2011 paper provides the framework but cannot validate it without that downstream work.

There is no engagement with predictive coding. The "modulator" classification of class-2 synapses is computationally consistent with the gain-control, precision-weighting role attributed to feedback in the predictive-coding literature ([bastos2012_canonical_microcircuits](research_db/papers/bastos2012_canonical_microcircuits.md); [keller_mrsic_flogel2018_pc_review](research_db/papers/keller_mrsic_flogel2018_pc_review.md)), but Sherman & Guillery do not draw the connection. Conversely, the transthalamic *driver* feedback to primary cortex (established later by [sherman2022_ctc_loop](research_db/papers/sherman2022_ctc_loop.md) as modulatory to primary, driving to higher) does not fit cleanly onto a predictive-coding ascending-error / descending-prediction scheme.

Mouse vs primate generalization is also uncertain. The 2011 synthesis is largely cat- and rodent-based; primate higher-order thalamus (especially primate pulvinar) is much more elaborated and its detailed driver/modulator partitioning has not been mapped to the same resolution. Anatomical homology is suggestive but not a substitute for primate-specific synaptic-physiology.

Finally, the paper treats "feedforward" and "feedback" as anatomically given. In practice, the direction of information flow between two cortical areas depends on task and behavioral state; what is feedforward in one context can be feedback in another. The class-1 / class-2 classification is synaptic and therefore stable, but the functional label "driver vs modulator" can shift with circuit state in ways the paper does not address.

## 7. Connection to our work

This paper is the conceptual root of the user's `bidirectional_hierarchical_feedback` concept and one of the two empirical pillars (along with [weiler2025_l6_corticocortical](research_db/papers/weiler2025_l6_corticocortical.md)) supporting the architectural commitment that feedback should *modulate* rather than *drive* the feedforward representation.

**Commitment 1: Drivers vs modulators map onto Q/K/V vs FiLM-style feedback.** In the Feedback Transformer ([concepts/feedback_transformer.md](research_db/concepts/feedback_transformer.md); [threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §1), the bottom-up sensory projections $Q_S, K_S, V_S$ are the architectural analog of class-1 *driver* synapses: they carry the receptive-field-defining content that determines what each token represents. The recurrent feedback projections $Q_{C_i}, K_{C_i}, V_{C_i}$ enter the attention computation via element-wise (Hadamard) broadcasting with the sensory projections — $q_i = s_{q,i} \odot \sum_k c^{(k)}_{q,i}$ — exactly the gain-modulating, non-driving operation that class-2 *modulator* synapses perform on cortical pyramidal cells. The mathematical form $\gamma \odot x + \beta$ used by PRISM v1's FiLM ([PrismV1/THESIS.md](PrismV1/THESIS.md) §2.4) and PRISM v2's hierarchical FiLM ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.4) is the most literal computational instantiation: feedback adjusts the gain and bias of the bottom-up signal without replacing it. Sherman & Guillery 2011 is the biological warrant for that mathematical choice.

**Commitment 2: Parallel direct and transthalamic pathways as parallel feedback sources.** The user's multi-compartmental memory architecture commits to *multiple* feedback inputs at every layer ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §3): descending memory projections from higher hubs, ascending projections from lower hubs, and lateral parallel-hub projections (MSI, RL, VAE). Sherman & Guillery establish that cortex itself implements multiple parallel routes between every pair of communicating areas — a direct route (L2/3 and L5 corticocortical) plus a transthalamic route (L5 → pulvinar/PoM → cortex). The architectural choice to admit "an arbitrary number of recurrent internal states" into the Feedback Transformer is licensed by exactly this kind of biological redundancy: cortex is not built around a single feedback channel but around several with different gating, gain, and timescale properties.

**Commitment 3: Hierarchical implementation via L5-driven transthalamic relay.** The hierarchy of areas the user inherits from [felleman_vanessen1991_hierarchical_cortex](research_db/papers/felleman_vanessen1991_hierarchical_cortex.md) is implemented at the cellular level by the canonical microcircuit ([bastos2012_canonical_microcircuits](research_db/papers/bastos2012_canonical_microcircuits.md)) — but the canonical microcircuit is mute on how L5 output reaches the next area. Sherman & Guillery 2011 supplies the missing piece: L5 of area $n$ drives higher-order thalamus, which relays the signal to area $n+1$. The user's *descending projections* (conv stacks with spatial reduction + channel expansion: $C_1 \to C_2 \to C_3$ with $n_{gh}^{(1)} > n_{gh}^{(2)} > n_{gh}^{(3)}$ and $n_{C_1} < n_{C_2} < n_{C_3}$; [threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §3) are the architectural analog of this L5-driven feedforward relay. The *ascending projections* (conv-transpose, with diminishing feedback into deeper layers) are the architectural analog of the class-2 feedback Sherman & Guillery attribute to direct corticocortical and to higher-order thalamic projections back to primary cortex.

**Commitment 4: Feedback as efference copy of competing coalitions.** Sherman & Guillery's most original claim — that the transthalamic pathway carries an *efference copy* of motor instructions, not just a copy of sensory representations — resonates with the user's `competition_emergent_predictive_coding` thesis ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5). In the user's reformulation, top-down feedback is not a prediction of sensory input but a prediction of the *behavior of competing neural coalitions* — i.e., what other hubs are about to do. Sherman & Guillery establish that cortex literally sends each area a copy of what other areas are commanding their motor outputs to do, which is precisely the kind of inter-coalition signal the user's account requires. This is a closer match to the user's theoretical claim than is the strict sensory-prediction reading of Rao-Ballard predictive coding ([rao_ballard1999_predictive_coding] and successor reviews [keller_mrsic_flogel2018_pc_review](research_db/papers/keller_mrsic_flogel2018_pc_review.md)).

**Commitment 5: Gated relay as the conditional-recurrence primitive.** Sherman & Guillery's argument that higher-order thalamus *gates* the transthalamic signal — tonic mode passes information faithfully, burst mode passes it as oscillatory all-or-nothing packets, hyperpolarized mode blocks it entirely — is a biological precedent for the user's "ability to shut off feedback inputs creates an incentive for cooperation between layers" design choice ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §3). A GridCell RNN layer that can refuse feedback from a noisy or hostile parallel hub is implementing the same gating logic that the thalamic reticular nucleus and intrathalamic modulators implement at the cellular level. Sherman & Guillery thus supply biological warrant not just for *what* the feedback signal looks like (modulator, class-2, slow) but also for *whether* it gets through at all.

**Commitment 6: Slow modulators map onto the slow-memory commitment.** The mGluR-mediated, hundreds-of-milliseconds class-2 modulator timescale is the biological counterpart of the slow-update memory state the user inherits from the Mujika/Tallec slow-fast RNN literature and instantiates as PRISM v2's $M^{\text{slow}}$ ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3). The user's `multi_compartmental_memory` and `slow_fast_recurrence` concepts ([concepts/multi_compartmental_memory.md](research_db/concepts/multi_compartmental_memory.md); [concepts/slow_fast_recurrence.md](research_db/concepts/slow_fast_recurrence.md)) commit to deeper layers running at slower update rates. Sherman & Guillery 2011 supplies a synapse-level biological correlate: the gain-setting feedback synapses are constitutively slower than the information-transmitting driver synapses, so the slow/fast architectural separation is built into cortex at the level of individual synapses, not just at the level of multi-area dynamics.

The Recurrent ViT paper (2502.10955) does not invoke any of this anatomy explicitly. The connection is at the level of *justification*: the multiplicative-feedback variant (§6.7) and PRISM's FiLM modulation are not arbitrary architectural choices but match the canonical class-2 / modulator synapse role established here. Sherman & Guillery 2011 is the citation we would reach for if a reviewer asked why feedback is multiplicative rather than additive, or why we admit several parallel feedback inputs rather than a single channel.

**A note on what this paper does *not* warrant.** Sherman & Guillery establish only the synaptic-physiology and tract-tracing facts. They do not commit to a particular computational role for the transthalamic pathway (predictive coding, attention, working memory, etc.), and they do not claim — as some later authors have — that the transthalamic pathway is specifically the substrate for top-down attention or for predictive-coding precision-weighting. Our use of the paper as biological warrant for FiLM-style modulation is therefore an *interpretive* move that goes beyond what the authors themselves argued; we should be careful, in any manuscript citing this work, to flag the interpretation rather than imputing it to Sherman & Guillery.

## 8. Citations to follow

- `sherman_guillery1998_relays_messages` — *On the actions that one nerve cell can have on another*. Earlier statement of the driver/modulator distinction. Not in seed.
- `usrey_alitto2015_visual_thalamus` — review of thalamic visual processing; complementary primate-focused synthesis. Already noted as follow-up from `sherman2022_ctc_loop`. Not in seed.
- `guillery1995_anatomical_evidence_pulvinar` — anatomical case that pulvinar relays corticocortical communication. Not in seed.
- `larkum2013_apical_basal_compartments` — apical/basal dendritic compartmentalization in cortical pyramidal cells, the cellular substrate by which a single neuron can integrate class-1 driver and class-2 modulator inputs separately. In the user's open scholarly debts ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §8). Not in seed.
- `roth_dahmen2016_pulvinar_modulatory` — pulvinar's modulatory role in attention; the behavioral side of the framework. Not in seed.
- `briggs_usrey2008_lgn_modulation` — corticothalamic feedback to LGN; comparison case for the L6-modulator role in first-order thalamus.
- `crandall_govindaiah_cox2010_metabotropic_modulation` — mGluR-mediated modulator synapses, providing the cellular mechanism class-2 synapses use. Not in seed.
