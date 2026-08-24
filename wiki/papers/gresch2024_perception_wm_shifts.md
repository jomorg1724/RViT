---
id: gresch2024_perception_wm_shifts
title: "Shifting attention between perception and working memory"
authors:
  - "Gresch, Daniela"
  - "Boettcher, Sage E. P."
  - "van Ede, Freek"
  - "Nobre, Anna C."
year: 2024
venue: "Cognition"
doi: "10.1016/j.cognition.2024.105731"
arxiv: ""
url: "https://doi.org/10.1016/j.cognition.2024.105731"
tags:
  - visual-attention
  - working-memory
  - psychophysics
concepts:
  - attentional-template
  - working-memory-persistent-activity
  - top-down-feedback
  - cueing-effect
  - priority-map
related:
  - teng_kravitz2019_wm_alters_perception
  - awh2006_attention_wm
  - kiyonaga_egner2013_wm_internal_attention
  - panichello_buschman2021_shared_mechanisms
  - olivers2011_wm_states_attention
  - gazzaley_nobre2012_topdown
  - vanede2019_gaze_internal_wm
  - nobre_vanede2018_anticipated_moments
  - bays2024_wm_representation
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_108
status: full
depth: full
last_updated: "2026-05-16"
---

# Shifting attention between perception and working memory

## 1. Abstract

Most everyday tasks require shifting the focus of attention between sensory signals in the external environment and internal contents in working memory. To date, shifts of attention have been investigated within each domain — external selection from sensory arrays, or internal selection among WM items — but shifts *between* the external and internal domain remain poorly understood. Gresch and colleagues developed a combined perception and working-memory task in which participants were sequentially cued to attend to items either in a maintained WM array or in an upcoming sensory display, and were occasionally required to shift the focus of attention either within the same domain (external→external, internal→internal) or across domains (external→internal, internal→external). Across two experiments, they show that participants shift attention effectively in either domain, but pay a measurable *additional* cost when transitioning attention *between* domains relative to *within* them. Crucially, these cross-domain shift costs persist even when participants are given substantially more time (up to 750 ms) to complete the attentional shift. Eye-tracking confirms that the behavioural cost is not driven by oculomotor preparation differences. The authors conclude that shifting between attentional domains is regulated by a unique control function distinct from the within-domain selection processes that have dominated the attention literature, opening a new axis for studying the architecture of attention as it actually operates in everyday cognition.

## 2. Why this matters for us

Gresch 2024 is the most recent and most quantitatively precise demonstration that *perception and working memory occupy a common attentional state* — observers can be cued to a location in either domain, performance benefits when the cue is valid, and the *transition* between domains incurs a residual cost that no amount of preparation time eliminates. For the user's architectural program, in which a single recurrent state $H^{(t)}$ feeds back into the same self-attention substrate that processes the bottom-up sensory input, this paper is the cleanest behavioural support yet: the cost structure of cross-domain shifts is exactly what one expects when attention, perception, and WM live on the same representational substrate but must be re-pointed by a domain-general control signal. The published Recurrent ViT (2502.10955) instantiates this commitment as a single Feedback Transformer integrating $H^{(t-1)}$ into Q/K/V at the same node where the patch tokens enter; Gresch's persistent cross-domain shift cost is the behavioural fingerprint that mechanism predicts.

## 3. Key claims

1. **Shifts of attention occur as readily within working memory as within perception.** Internal cueing (re-pointing the focus among WM items) yields valid-cue benefits comparable to external cueing (re-pointing the focus among sensory items).
2. **Cross-domain shifts incur an additional cost beyond within-domain shifts.** Switching the focus from perception to WM or from WM to perception is reliably slower / less accurate than switching the focus within either domain alone.
3. **The cross-domain cost is asymmetry-robust.** External→internal and internal→external transitions both produce the additional cost, suggesting a shared control bottleneck rather than a one-way translation problem.
4. **The cost is not absorbed by preparation time.** Manipulating the interval between the first cue and the shift cue (0, 250, 750 ms) does not eliminate the cross-domain shift cost, ruling out a slow attentional-orienting account.
5. **Gaze-bias dynamics do not differentiate shift types in latency.** Fixational gaze biases ("towardness") track the cued item in both domains and arise with comparable latencies for external- and internal-first cues, indicating the cost is not an oculomotor preparation difference.
6. **A dedicated cross-domain control function is implicated.** The persistence of the cost across preparation intervals supports a distinct supervisory mechanism that re-points attention across the perception/WM boundary, rather than a generic reconfiguration cost.
7. **The framework reframes "attention" as a single resource that selects from a heterogeneous priority map.** External-and-internal locations are treated as alternative entries in one map, with the cost reflecting the control signal that must re-weight across heterogeneous sources rather than two separate maps.

## 4. Methods

Two psychophysical experiments in adult human observers, run as variants of a combined perception + working-memory task.

**Task structure.** Each trial began with a memory array of two oriented bars (the WM domain). After a short retention interval, a first cue indicated either (a) one of the held WM items (an *internal* cue) or (b) a future location in a sensory display about to appear (an *external* cue). After a variable interstimulus interval, a second cue appeared. The second cue either *stayed* on the originally cued item (the baseline within-domain stay condition) or *shifted* the focus to a different item, in either the same domain (within-domain shift: external→external, internal→internal) or the other domain (cross-domain shift: external→internal, internal→external). Following the second cue the participant reproduced the orientation of the indicated item on a continuous response wheel.

**Critical manipulation.** The factorial structure crosses {stay, within-domain shift, cross-domain shift} × {first cue external, first cue internal}, plus, in Experiment 2, the second-cue interstimulus interval (0, 250, 750 ms) to test whether preparation time absorbs the cross-domain cost.

**Eye-tracking.** Gaze was monitored throughout the task. Trials with overt fixations away from centre were excluded; the residual fixational gaze bias ("towardness" of micro-shifts toward the cued item) was analysed separately as a covert-attention index.

**Analyses.** Response error and response time were analysed across shift conditions; the planned contrast was the difference between cross-domain and within-domain shifts (the "extra" shift cost). In Experiment 2, an interaction between shift type and preparation interval would indicate that additional time absorbs the cross-domain cost. Fixational gaze "towardness" was analysed as a time-resolved signal locked to cue onset.

**Why this design isolates the cross-domain control function.** The within-domain shift conditions absorb any cost that comes from re-pointing the focus of attention generally — i.e., from disengaging from one item and engaging another. The *additional* cost incurred on cross-domain trials, relative to within-domain shifts, must therefore reflect something specific to traversing the perception/WM boundary. That "extra" cost, and especially its insensitivity to preparation interval, is the load-bearing dependent variable of the paper.

## 5. Results

**Within-domain shift costs are present and roughly symmetric across domains.** Both external→external and internal→internal shifts are slower / less accurate than stay trials, confirming that re-pointing the focus inside a domain itself carries a measurable cost. The magnitude is comparable in the two domains, consistent with prior reports that internal selection follows attentional dynamics similar to external selection.

**Cross-domain shifts incur an additional cost.** External→internal and internal→external shifts produce a further reliable cost on top of the within-domain shift cost. The effect is present in both response-error and response-time measures, and is comparable in magnitude in the two directions, indicating a shared cross-domain control bottleneck.

**Preparation time does not absorb the cost.** Experiment 2's manipulation of the second-cue ISI (0, 250, 750 ms) produces overall improvements in performance with more time, but does *not* selectively reduce the cross-domain shift cost. The cross-domain "extra" cost persists at 750 ms, ruling out an explanation in which the cost is simply that the cross-domain shift takes longer to complete.

**Gaze bias tracks cued items in both domains with comparable latencies.** Fixational gaze "towardness" rose for both external and internal first cues, with no reliable latency difference. This rules out the possibility that the cross-domain cost is driven by an oculomotor preparation difference; the covert attention signal arrives in both domains on the same timecourse.

**Interpretation.** The pattern is most parsimoniously explained by a *unique cross-domain control function* — a supervisory mechanism that must be engaged whenever attention is re-pointed across the perception/WM boundary, regardless of how much time is available. Within-domain shifts engage the standard re-pointing machinery; cross-domain shifts engage that machinery *plus* this extra control signal. The persistence across ISIs rules out the alternative that the cost is just additional time-to-completion.

## 6. Critique / limitations

The work is *behavioural* throughout; no neural measurement directly identifies the proposed cross-domain control mechanism. The authors interpret the persistent extra cost as evidence for a dedicated supervisory function, but a reader could equally argue that the cost reflects a structural property of any priority map that mixes external and internal entries (e.g., greater representational distance, lower template-match precision across domains, or asymmetric feedback connectivity between the WM substrate and incoming sensory cortex). Distinguishing these would require neural decoding during the shift period; a companion PNAS paper from the same lab (Gresch et al. 2024, "Neural dynamics of shifting attention between perception and working-memory contents") takes that step but is not part of the present paper.

The orientation-reproduction paradigm and two-item WM load are small. Whether the cross-domain extra cost scales with WM load, or generalises across feature dimensions (colour, motion, naturalistic objects), is not established. Cross-domain shifts in naturalistic tasks — looking from a held-in-mind shopping list to the items on a shelf — almost certainly involve richer contents than oriented Gabors and may differ quantitatively.

The "preparation time" manipulation tops out at 750 ms. Cross-domain shifts in everyday life unfold over much longer intervals (seconds), and the present data cannot rule out that asymptotic preparation eventually eliminates the cost. The robust claim is only that the cost is not absorbed by typical sub-second preparation windows.

The framework leaves the *direction of control* underspecified. The "unique control function" is inferred from the cost asymmetry, but the paper does not tell us where in the brain that control lives, what its time-course looks like, or how it interacts with the standard FEF/IPS attentional control network. Panichello & Buschman 2021 ([panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md)) place shared attention/WM control in PFC, and the natural extension is that the cross-domain cost reflects a PFC reconfiguration event, but that prediction is not tested here.

Finally, the paper does not engage computational models. The behavioural pattern is suggestive of a *single priority map with heterogeneous entries*, but no formal account is given. A reader can imagine variants — separate maps with bidirectional gating, a single map with domain-coded slots, an attractor network with cross-domain energy barriers — that would all predict a residual cross-domain cost. The data constrain but do not adjudicate these.

## 7. Connection to our work

Gresch 2024 is *the recent empirical anchor for the user's central architectural claim*: that perception, attention, and working memory are not three modular systems with interfaces between them but three projections of a single recurrent state. The paper joins Teng & Kravitz 2019 ([teng_kravitz2019_wm_alters_perception](teng_kravitz2019_wm_alters_perception.md)) in the lineage of work that pushes the WM/perception boundary inward and demands a unified architectural treatment.

**Single shared state and the Feedback Transformer.** The Feedback Transformer (thread §1) integrates a recurrent state $C_i$ into the same Q/K/V projections that read the bottom-up sensory input — i.e., the memory signal and the perceptual signal share an attentional substrate at the level of inner-product geometry. Gresch's headline result — a residual *cross-domain* shift cost that persists across preparation intervals — is exactly what this architecture predicts: when the control signal must re-point attention from a sensory token to an internal-state token (or vice versa), there is no separate "internal-attention head" to redirect; the same head must reweight which entry in the unified Q/K/V map is winning. The reweighting takes a moment regardless of how much preparation time precedes it, because the control signal must traverse the same competitive substrate that hosts both kinds of entries.

**Within-domain vs cross-domain costs as a falsifiable prediction of the architecture.** A two-system architecture with separate external and internal attentional substrates would predict that, given enough preparation time, cross-domain costs should be absorbed by parallel pre-allocation of the two systems. The user's single-substrate architecture predicts the opposite: cross-domain costs should persist because the competition lives in one substrate. Gresch's 750-ms-resistant cost is direct support for the single-substrate prediction. This is a non-trivial behavioural-architectural alignment.

**Lineage with Teng & Kravitz 2019.** Teng & Kravitz showed that *holding* a feature in WM biases the perception of an unrelated probe — i.e., WM contents leak into perception at the representational level. Gresch extends the story to the *control* level: not only does WM modulate perception passively, but the *act of selecting* something in WM uses the same control machinery that selects something in perception, and traversing between them incurs a measurable extra cost because the control signal must reconfigure the unified substrate. Together the two papers bracket the WM-perception unification claim: Teng & Kravitz at the representational substrate, Gresch at the attentional control level.

**Connection to Awh, Vogel & Oh 2006.** Awh et al. ([awh2006_attention_wm](awh2006_attention_wm.md)) established that attention and WM share resources. Gresch 2024 sharpens this: the *act of switching* between WM and perception engages a unique control function not invoked by within-domain switches. For the user's architecture, the within-domain cost corresponds to ordinary attention-map updates inside the Feedback Transformer; the extra cross-domain cost corresponds to a higher-level supervisory signal that re-weights *which feedback source dominates the Q/K/V mix* — i.e., whether the bottom-up sensory projection $s_{q,k,v}$ or the recurrent memory projection $c_{q,k,v}$ has more weight at that timestep. This is the kind of control the multi-hub architecture (thread §5) naturally hosts.

**Connection to Kiyonaga & Egner 2013.** Kiyonaga & Egner ([kiyonaga_egner2013_wm_internal_attention](kiyonaga_egner2013_wm_internal_attention.md)) proposed treating WM as "internal attention" — the same selection mechanism turned inward. Gresch's result complicates the picture: internal and external selection share a mechanism (consistent with Kiyonaga & Egner), but the *transition* between them requires a distinct control signal (extending Kiyonaga & Egner). For the user's architecture this maps onto the distinction between *attention-map updates within a feedback source* and *gain reweighting across feedback sources*, both of which the Feedback Transformer supports.

**Connection to Panichello & Buschman 2021.** Panichello & Buschman ([panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md)) identified PFC populations that multiplex attention and WM control. Gresch's "unique cross-domain control function" is exactly what such populations would implement: a PFC-level signal that reconfigures the Q/K/V mix in posterior sensory/memory cortex. In the user's 3-layer reference design (thread §3), the deep memory layer $C_3$ is the architectural analog of PFC, and the cross-domain shift cost is what one would expect to see in a model in which $C_3$ must reconfigure the descending feedback to $C_1$ when the task domain changes.

**Connection to Olivers 2011 (active vs accessory WM).** Olivers et al. ([olivers2011_wm_states_attention](olivers2011_wm_states_attention.md)) distinguished *active* WM items (those guiding selection) from *accessory* items (those merely held). Gresch's design makes this concrete: the first cue puts an item in the active state in either domain; the second cue may re-point to a different active item, possibly across the domain boundary. The cross-domain extra cost is then specifically about the state transition between "active in WM" and "active in perception" — a transition Olivers' framework did not parameterise but the user's architecture must model.

**Connection to van Ede 2019 and gaze-based readouts of internal attention.** van Ede ([vanede2019_gaze_internal_wm](vanede2019_gaze_internal_wm.md)) established that fixational gaze biases index covert internal attention. Gresch uses the same readout to demonstrate that the gaze signature of internal cueing arrives on the same timecourse as the gaze signature of external cueing — i.e., the covert orienting *itself* is not slower in either domain; only the cross-domain transition is. For the user's program this is methodologically important: gaze "towardness" is a cheap, non-invasive readout of which entry in the unified priority map is currently winning, and it should be reproducible in a trained Recurrent ViT by reading off attention weights over patch tokens.

**Connection to Gazzaley & Nobre 2012 on top-down control.** Gazzaley & Nobre ([gazzaley_nobre2012_topdown](gazzaley_nobre2012_topdown.md)) framed top-down attention as a unified control signal operating over perceptual and mnemonic representations. Gresch quantifies the cost of switching that signal between domains and shows it is not absorbed by preparation time — exactly the prediction one would make if Gazzaley & Nobre's unified top-down control is in fact a single competitive substrate, not parallel systems.

**Iterative variational encoder–decoder.** In the iterative-VAE framing (thread §4), the decoder is initialised from the encoder's guide $H_{n_{FR}}$ and produces reconstruction proposals while continuing to read the encoder's evolving representation. The natural interpretation of Gresch is that *the same attentional substrate is being driven by both the bottom-up encoder pass and the top-down decoder pass*, and the residual cross-domain shift cost is the model's prediction for what happens when the system is asked to abruptly switch from encoder-driven to decoder-driven attention or vice versa. The 750-ms-resistant cost is a non-trivial behavioural target the iterative-VAE could be evaluated against.

**Empirical test for the user's program.** A direct cognitive-science prediction of the Feedback Transformer is that a trained Recurrent ViT, run on a combined external/internal cueing task (cue a patch location for the next frame, or cue a maintained-feature token in $H^{(t)}$), should reproduce Gresch's pattern: comparable within-domain cueing benefits, a residual cross-domain cost on shift trials, and persistence of that cost across preparation intervals. A positive result would be the strongest behavioural alignment the architecture has yet achieved with human attention data. A negative result would identify a missing component — most likely a dedicated cross-domain control signal between the deep memory layer and the shallow ones, which the multi-compartmental memory stack (thread §3) is designed to host but which the published single-layer RViT does not yet have.

**Locating the paper in the WM–attention–perception triad.** Awh 2006 coupled attention and WM; Kiyonaga & Egner 2013 promoted that coupling to "WM as internal attention"; Panichello & Buschman 2021 placed shared control in PFC; Olivers 2011 dissociated active from accessory WM states; Teng & Kravitz 2019 closed the perceptual leg of the triangle by showing WM-driven perceptual bias. Gresch 2024 sharpens the control side of the triangle: traversing the perception/WM boundary is itself a controlled act with a unique signature. The user's program is the architectural commitment that all three legs share a substrate, and Gresch is the most recent quantitative measurement of the *cost* of operating that substrate.

## 8. Citations to follow

- `gresch_etal2024_neural_dynamics_pnas` — the same authors' companion PNAS paper on the neural dynamics of cross-domain attention shifts; provides the neural decoding the present behavioural paper lacks.
- `chun_johnson2011_memory_perception_review` — review of memory/attention/perception unification; theoretical background the present paper builds on.
- `myers_stokes_nobre2017_prioritizing_information_wm` — prioritising information in WM as an internal-attention act; conceptual precursor for the internal cueing manipulation.
- `souza_oberauer2016_in_context_memory` — context-driven biases on continuous-report WM; methodological complement to the orientation-reproduction design.
- `griffin_nobre2003_orienting_attention_internal` — early paper on internal vs external cueing; the paradigmatic ancestor of the Gresch design.
- `landman_spekreijse_lamme2003_large_capacity_pre_memory` — large-capacity perceptual representations vs limited WM; the asymmetry the cross-domain cost may reflect.
- `lamy2017_internal_attention_capture` — internal capture by WM contents; relates to whether cross-domain shifts are involuntary.
- `larocque_lewis_peck_postle2014_decoding_active_latent_wm` — active vs latent WM decoding; bears on whether the cross-domain cost depends on activation state.
