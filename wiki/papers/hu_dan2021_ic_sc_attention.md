---
id: hu_dan2021_ic_sc_attention
title: "An inferior-superior colliculus circuit controls auditory cue-directed visual spatial attention"
authors:
  - "Hu, Fei"
  - "Dan, Yang"
year: 2021
venue: "Neuron"
doi: "10.1016/j.neuron.2021.10.004"
arxiv: ""
url: "https://doi.org/10.1016/j.neuron.2021.10.004"
tags:
  - visual-attention
  - subcortical
  - posner-cuing
  - lesion-microstimulation
  - early-visual-cortex
concepts:
  - cueing-effect
  - attentional-spotlight
  - optogenetic-perturbation
  - priority-map
  - top-down-feedback
  - multi-sensory-integration
related:
  - krauzlis2013_sc_attention
  - sridharan2017_sc_sensitivity_bias
  - cavanaugh_wurtz2004_sc_change_blindness
  - herman_krauzlis2017_sc_change_detection
  - moore_armstrong2003_fef_microstim
  - posner1980_orienting
  - herman2018_midbrain_decisions
  - choi2023_msi_review
  - knudsen2007_fundamental_components
  - bolton2015_dopamine_sc
  - huda2020_pfc_topdown_circuits
  - senkowski_engel2024_multi_timescale_msi
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - programmatic_pubmed
status: full
depth: full
last_updated: "2026-05-16"
---

# An inferior-superior colliculus circuit controls auditory cue-directed visual spatial attention

## 1. Abstract

Selective attention modulates neuronal activity across multiple brain regions, but the origins of attention-control signals — and where in the brain a *cue* signal is converted into a *spatial-attention* signal — remain unclear. Hu & Dan train head-fixed mice on a two-alternative cued visual-detection task in which an auditory cue indicates which hemifield contains the behaviorally relevant visual target while a competing distractor appears on the uncued side. Recording in primary visual cortex (V1) and superior colliculus (SC), the authors find strong attentional modulation of stimulus-evoked responses in both areas, with a *shorter onset latency in SC* than in V1. The nucleus of the brachium of the inferior colliculus (nBIC) — an auditory midbrain structure that projects to SC — shows two distinct response phases to the cue: a transient onset response at cue presentation and a sustained delay-period activity bridging cue and visual target. Optogenetic silencing of nBIC delay activity (but not cue-onset activity) abolishes the behavioral attention effect and the SC/V1 attentional modulation, while activation of nBIC during the delay enhances attentional performance. The paper localizes a causal midbrain substrate for auditory-cued visual spatial attention to the IC → nBIC → SC pathway.

## 2. Why this matters for us

This paper supplies a causally-tested midbrain circuit for *cross-modal cue-directed spatial attention*: an auditory cue is converted into a delay-period spatial-attention signal in the nBIC and routed to SC, where it modulates the visual priority map even before cortical visual attention engages. For the Recurrent ViT and PRISM v2, this is direct evidence that the *attention-control signal does not have to originate in cortex*. A subcortical hub that integrates an auxiliary modality (audio) with a maintained spatial expectation, then projects into a priority-map substrate, maps cleanly onto the user's multi-hub architecture: the nBIC is exactly the kind of MSI hub that the Feedback Transformer is designed to fuse into a central self-attention map. The shorter SC latency than V1 latency also bears on the user's commitment to top-down feedback into early visual processing — the spatial-attention signal is available *before* V1's stimulus-driven response peaks.

## 3. Key claims

1. **Mice exhibit auditory cue-directed visual spatial attention.** Performance on the cued side is higher than on the uncued side; the attention effect is robust and quantifiable in head-fixed mice.
2. **V1 and SC both show attentional modulation.** Stimulus-evoked responses to the visual target are enhanced when the target is on the cued (attended) side relative to the uncued side, in both V1 and SC.
3. **SC attentional modulation precedes V1.** The attentional modulation has a *shorter onset latency in SC* than in V1, suggesting the SC is upstream of cortical attention in this circuit.
4. **The nBIC carries the cue signal to SC.** The nBIC, an auditory midbrain structure providing major input to SC, is activated at cue onset and sustains activity through the cue-to-target delay.
5. **Delay-period nBIC activity is causally necessary.** Optogenetic silencing of nBIC during the *delay* abolishes the behavioral attention effect and the SC/V1 attentional modulation; silencing only at cue *onset* does not.
6. **Delay-period nBIC activity is causally sufficient (enhancing).** Optogenetic activation of nBIC during the delay enhances behavioral performance on the cued side.
7. **The IC → nBIC → SC pathway is a midbrain substrate for cross-modal cued attention.** A single circuit converts a cue in one modality (audio) into a spatial-attention signal modulating processing in another (vision).

## 4. Methods

**Species and task.** Head-fixed mice trained on a two-alternative cued visual-detection task. A brief auditory cue (delivered to one ear or one azimuthal location) indicates the hemifield in which a subsequent visual target will appear. After a variable cue-to-target delay, a visual target appears on the cued side; a distractor is presented simultaneously on the uncued side. Mice must report the target's identity (e.g., grating orientation) by directional licking or running. Performance is measured as accuracy and reaction time on cued versus uncued trials.

**Electrophysiology.** Multi-channel silicon-probe recordings in V1 and SC during task performance. Single-unit responses are aligned to the visual target onset and decomposed into cued versus uncued conditions to extract the attentional modulation index. Onset latencies of attentional modulation are estimated per area and compared across V1 and SC.

**nBIC recording.** Single-unit or multi-unit recording in the nucleus of the brachium of the inferior colliculus during task performance, isolating two response components: (a) a transient cue-onset response and (b) a sustained delay-period response between cue offset and target onset.

**Optogenetic perturbation.** Cre-dependent or pan-neuronal expression of inhibitory opsins (e.g., halorhodopsin / ArchT for silencing) and excitatory opsins (ChR2 for activation) in nBIC. Light delivery is gated to one of two windows: (1) the cue-onset period only, or (2) the delay period only. This temporal dissociation tests whether the *cue-onset* component or the *delay* component of nBIC activity is causally relevant for behavior.

**Read-outs.** Behavioral effect on cued vs. uncued accuracy and reaction time; SC and V1 attentional modulation index of stimulus-evoked responses; nBIC firing-rate profiles around cue and target.

## 5. Results

- **Behavioral attention effect.** Mice perform reliably better on cued than on uncued trials (the canonical Posner-like attention benefit), establishing the task as a valid covert-attention paradigm in rodents.
- **SC modulation precedes V1.** Onset latency of attentional modulation in SC is *shorter* than in V1. The SC priority signal is therefore not inherited from cortex.
- **nBIC has two response phases.** A transient cue-onset response and a sustained delay-period response. Both are present on cued trials; the delay component is the candidate spatial-expectation signal.
- **Delay-only silencing eliminates the attention effect.** Optogenetic suppression of nBIC restricted to the delay period abolishes the behavioral cued-vs-uncued performance difference and eliminates attentional modulation in both SC and V1.
- **Cue-onset-only silencing leaves attention intact.** Optogenetic suppression restricted to the cue-onset window does *not* abolish the attention effect — the cue-onset transient is not the causally relevant signal.
- **Delay-period activation enhances attention.** Optogenetic activation of nBIC during the delay enhances cued-side performance, completing the necessity-plus-sufficiency causal demonstration.
- **Dissociation logic.** The fact that the same neurons' *cue-onset* activity is not behaviorally required but their *delay* activity is, localizes the attention-control signal to the delay-period sustained component — i.e., to the maintained spatial expectation, not to the sensory cue trace.

## 6. Critique / limitations

The paper is in mouse. Whether the IC → nBIC → SC pathway plays the same causal role in primates — where cortex is far more developed and where most existing SC-attention work (Krauzlis et al. 2013; Cavanaugh & Wurtz 2004; Müller et al. 2005; Sridharan et al. 2017) has been done — is an open question. Mouse SC may dominate visual attention more than primate SC; cross-species generalization is non-trivial.

The cue is auditory. The paper does *not* establish whether the same nBIC delay-period mechanism carries spatial expectations cued by *visual* or *internally generated* signals. The IC → nBIC pathway is an auditory route; visual cueing presumably uses a different upstream path into SC, but the *delay-period spatial expectation in SC* may be a shared bottleneck. This is not tested here.

The attentional modulation in V1 is interpreted as inherited from SC because of the latency difference, but the paper does not rule out a parallel cortical attention signal that simply has a longer transduction delay. A more conclusive test would silence SC (or the SC → V1 thalamic projection) and show V1 attentional modulation is abolished.

The optogenetic manipulations are *area-level*, not cell-type-specific. The specific nBIC projection neurons that carry the signal to SC are not isolated; the result is causal at the level of the structure, not the cell type or synapse.

The task is two-alternative; the priority-map content (whether the delay activity encodes the cued *location* in topographic detail) is less rigorously characterized than the existence of the attention effect. The framing is *priority-map-compatible* but does not include a fine-grained spatial-encoding analysis at the resolution of Cavanaugh & Wurtz (2004) or Herman & Krauzlis (2017).

The result does not engage with predictive-coding or precision-weighting interpretations of attention. The nBIC delay signal is described in priority-map / spatial-expectation terms, but a PC-style reading — the delay signal as a *prior* on visual-target location, with the post-target response as a precision-weighted prediction error — is implicit at most.

Finally, the paper does not characterize the *internal dynamics* of the nBIC delay-period activity. Whether it is a tonic plateau, a ramp, an oscillation, or a population of neurons with diverse latency profiles is not resolved. For the user's program — where delay-period feedback into self-attention is implemented as a recurrent state with explicit dynamics — knowing what the biological delay code looks like would discipline the architectural choice (e.g., LSTM with persistent activation vs. attractor RNN vs. integrator).

## 7. Connection to our work

This paper is a fresh and load-bearing data point for several commitments of the user's architectural program.

**IC → nBIC → SC as a midbrain MSI substrate.** The user's multi-hub system (`multi_hub_multi_objective_system`) explicitly posits a multisensory-integration (MSI) hub feeding into a central self-attention map. The IC → nBIC → SC circuit is the biological exemplar: an auditory midbrain area integrates a cross-modal cue and projects into the SC priority map, modulating visual processing. This is precisely the architecture the user's MSI hub is intended to model. Hu & Dan 2021 therefore replaces an in-principle plausibility argument with a causally-tested circuit-level proof of concept.

**Cue-delivery as delay-period activity, not cue-onset transient.** The dissociation between cue-onset and delay-period nBIC activity is informative for the Feedback Transformer (`feedback-transformer`). The user's Recurrent ViT integrates feedback from a recurrent memory state $H^{(t-1)}$ — i.e., from a *maintained* representation, not from a transient input event. Hu & Dan show that the biologically causal attention signal is precisely the *maintained* delay-period activity, not the transient cue response. This supports the architectural choice to route feedback through persistent recurrent state.

**Connection to the SC priority-map literature.** Krauzlis et al. 2013 (`krauzlis2013_sc_attention`) established the SC as a primate-attention priority-map substrate. Cavanaugh & Wurtz 2004 (`cavanaugh_wurtz2004_sc_change_blindness`) gave the microstimulation causal demonstration. Sridharan et al. 2017 (`sridharan2017_sc_sensitivity_bias`) decomposed the SC effect into sensitivity vs. bias. Herman & Krauzlis 2017 (`herman_krauzlis2017_sc_change_detection`) extended to change-detection. Hu & Dan 2021 adds the *cross-modal cueing pathway* upstream of SC, completing the loop: a midbrain MSI hub (nBIC) feeds the SC priority map, which feeds (via thalamus or direct projection) visual cortex. The recurrent ViT's attention map is, by analogy, a model of this composite priority signal — not just of SC, and not just of cortex.

**Multisensory integration extension for the Recurrent ViT.** The published Recurrent ViT (2502.10955) processes only visual input. The paper's central architectural primitive — the Feedback Transformer at §6.7 — is designed to admit arbitrary additional feedback sources. Hu & Dan 2021 provides a concrete biological warrant for adding an *auditory* input stream: a parallel hub (audio encoder), with its own recurrent memory, whose state is projected into Q/K/V vectors that combine multiplicatively with the visual Q/K/V before softmax. This is the AI homolog of nBIC's projection into SC. A short-term experimental program would: (a) add a synthetic auditory cue channel to the change-detection task; (b) connect it via a parallel GridCell RNN feeding into the central self-attention map; (c) test whether the network learns to use the cue analogously to the mouse — exhibiting a faster, more accurate change-detection response on cued than uncued sides. The expected signature is a delay-period buildup in the auditory hub's recurrent state that persists from cue to target, exactly as in nBIC.

**PRISM v2 implications.** PRISM v2's slow/fast memory commitment (`PRISM_V2_PROPOSAL.md` §3.3) is partly motivated by the need to maintain spatial expectations over delays. Hu & Dan 2021's delay-period nBIC activity is a concrete biological exemplar of exactly this kind of slow-timescale signal feeding a faster perceptual stream — the auditory-cue hub operates on the cue-to-target delay timescale (~hundreds of ms to seconds), while the visual SC/V1 response operates on the ~10s of ms timescale of stimulus-driven processing.

**Causal localization as a model for ablation experiments.** Hu & Dan's logic — silencing the delay window vs. the cue-onset window separately to dissociate components — is methodologically transferable to model-ablation experiments in the user's architecture. Selectively zeroing the feedback projection during specific task phases (cue period vs. delay vs. target onset) should produce dissociations analogous to the optogenetic dissociation, testing whether the model uses *maintained* feedback vs. *transient* feedback.

**Latency ordering and the Feedback Transformer.** The empirical ordering — SC modulation precedes V1 modulation — is the canonical fingerprint of a *top-down* feedback signal arriving at V1 from a subcortical priority structure. The Feedback Transformer's commitment to integrating feedback at the Q/K/V level *before* the softmax, rather than as a post-hoc additive bias on attention outputs, predicts exactly this kind of pre-stimulus shaping of the attention computation. Hu & Dan 2021 is a biological signature consistent with the architectural choice.

**Bridge to herman2018_midbrain_decisions.** Herman 2018 frames the midbrain (including SC and surrounding structures) as a decision-making substrate that integrates priority information with motor planning. Hu & Dan 2021 supplies the *input* side of that picture: how cued priority arrives in the midbrain in the first place. Together the two papers cover the full loop — cue ingress through nBIC, priority computation in SC, decision read-out at the SC/midbrain interface — that the user's multi-hub system parallels with its MSI hub + central self-attention + RL hub architecture.

## 8. Citations to follow

- `lovejoy_krauzlis2010_inactivating_sc` — primate SC inactivation produces covert-attention deficits, the macaque parallel to Hu & Dan's mouse optogenetic silencing. Already flagged in `krauzlis2013_sc_attention`.
- `stein_meredith1993_merging_senses` — foundational SC multisensory-integration textbook; canonical citation for the SC as MSI substrate.
- `knudsen2002_owl_space_map` — owl IC/OT (homolog of SC) auditory-visual space map; the developmental and computational foundation of midbrain MSI.
- `wang_li2020_msi_sc_review` — recent review of multisensory integration in the SC; bridges Stein/Meredith to the optogenetic era.
- `bolton2015_dopamine_sc` — already in seed; dopamine modulation of SC, relevant to the broader subcortical-attention circuit.
- `huda2020_pfc_topdown_circuits` — already in seed; cortical top-down circuits for attention in mouse, parallel to Hu & Dan's subcortical-only result.
- `wimmer2015_thalamic_attention` — pulvinar / thalamic gating of cortical attention, the cortico-thalamic complement to the midbrain Hu & Dan pathway.
- `zhao_liu2014_v1_attention` — V1 attentional modulation in mouse; useful for the V1 latency comparison in §5.
- `senkowski_engel2024_multi_timescale_msi` — already in seed; multi-timescale MSI in cortex, complements Hu & Dan's midbrain delay-period MSI.
- `choi2023_msi_review` — already in seed; review of MSI in the mammalian brain; companion to Hu & Dan 2021 for the user's MSI-hub design.
