---
id: sreenivasan_desposito2019_delay_activity
title: "The what, where and how of delay activity"
authors:
  - "Sreenivasan, Kartik K."
  - "D'Esposito, Mark"
year: 2019
venue: "Nature Reviews Neuroscience"
doi: "10.1038/s41583-019-0176-7"
arxiv: ""
url: "https://www.nature.com/articles/s41583-019-0176-7"
tags:
  - working-memory
  - delay-activity
  - distributed-coding
  - dynamic-coding
  - thalamocortical
  - review
concepts:
  - multi_compartmental_memory
  - slow_fast_recurrence
  - cortico-thalamo-cortical-loops
  - bidirectional_hierarchical_feedback
related:
  - desposito_postle2015_wm_neuroscience
  - postle2006_wm_emergent
  - christophel2017_distributed_wm
  - stokes2015_activity_silent_wm
  - constantinidis2018_persistent_activity
  - masse2019_circuit_wm
  - panichello_buschman2021_shared_mechanisms
  - foster2017_alpha_vwm
  - sherman2022_ctc_loop
relevance_to:
  - prism_v1
  - prism_v2
  - rvit_plus
seed_source:
  - manual_deep_dive_2026_05_23
status: full
depth: full
last_updated: "2026-05-23"
---

# The what, where and how of delay activity

## 1. Abstract

> "Working memory is characterized by neural activity that persists during the retention interval of delay tasks. Despite the ubiquity of this 'delay activity' across tasks, species and experimental techniques, our understanding of this phenomenon remains incomplete. Although initially there was a narrow focus on sustained activation in a small number of brain regions, methodological and analytical advances have allowed researchers to uncover previously unobserved forms of delay activity across the entire brain. In light of these new findings, this Review reconsiders what delay activity is, where in the brain it is found, what roles it serves and how it may be generated." (Sreenivasan & D'Esposito 2019, *Nature Reviews Neuroscience* 20(8):466-481, abstract.)

## 2. Why this matters for us

Sreenivasan & D'Esposito 2019 is the *most synthesized modern review* of working-memory neuroscience and is the load-bearing reference for the user's program on three fronts. First, it canonizes the *distributed delay activity* finding (WM contents are maintained across V1-V4, IPS, premotor, MTL, PFC, basal ganglia, and thalamus simultaneously) that the user's [multi_compartmental_memory](../concepts/multi_compartmental_memory.md) commitment depends on. Second, it explicitly integrates *thalamocortical loops* as the causal sustaining substrate for cortical delay activity — providing the biological warrant for any user-program architectural commitment that puts a *recurrent* central pathway (the Feedback Transformer) between cortical regions / hubs. Third, it codifies *delay activity as heterogeneous* — stable persistent firing, dynamic/sequential activity, oscillatory bursts, and activity-silent synaptic states all qualify — implying that the user's recurrent memory state should *not* be expected to look temporally stationary; multiple coding regimes can coexist within a single recurrent population.

## 3. Key claims

1. "Delay activity" is *heterogeneous*: stable persistent firing, dynamic/sequential activity, oscillatory bursts, and synaptic ("activity-silent") states all qualify; the single-attractor view is obsolete.
2. It is *distributed across the brain* — lateral PFC, posterior parietal, MTL, sensory cortices, motor regions, basal ganglia, and thalamus — not localized to PFC.
3. Different brain regions encode functionally *distinct WM components* (content vs rules vs prospective actions).
4. *Population-level coding* (subspaces, dynamics) supersedes the single-unit persistent-firing view.
5. Three mechanistic families generate delay activity: *intrinsic bistability*, *recurrent attractor networks*, and *short-term synaptic plasticity*; hybrids are likely.
6. *Thalamocortical loops* causally sustain frontal delay activity — mouse photoinhibition of mediodorsal thalamus disrupts frontal delay activity and behavior.
7. The classical PFC-as-storage view is too narrow; PFC stores *goal/control* information rather than only content.
8. *Activity-silent and dynamic codes can coexist with persistent activity* within the same task and region — the field is converging on a multi-substrate view.

## 4. Methods

Narrative review integrating monkey single-unit and population recordings, rodent optogenetics (especially the recent thalamocortical-loop literature), human fMRI/MVPA/MEG, and computational models. Organized into four questions: (i) *what* is delay activity — a single phenomenon or many? (ii) *where* is it found in the brain? (iii) *what for* — what functions does each form serve? (iv) *how* is it generated mechanistically? Each section integrates multiple modalities and is structured around resolving (or at least clearly stating) the persistent-vs-dynamic-vs-silent debate. The synthesis is methodologically eclectic — the authors pull together evidence that the field has historically partitioned by method (single-unit vs fMRI vs computational), arguing that the partitioning itself has obscured the distributed and heterogeneous nature of delay activity.

## 5. Results

The review consolidates a set of empirical anchors that constitute the field's modern consensus:

- **Only ~3% of "delay-active" PFC neurons fire at stable rates throughout the delay**; the vast majority show time-varying activity, refuting the strong persistent-activity-as-stable-attractor view.
- **Thalamic photoinhibition in mice disrupts frontal delay activity and behavior** (Schmitt et al. 2017 *Nature*) — direct causal evidence for thalamocortical sustaining loops.
- **Population dynamics in NHP PFC occupy a low-dimensional subspace that stably encodes content** despite single-unit dynamics (Murray et al. 2017 *PNAS*) — the population/single-unit reconciliation.
- **Gamma bursts scale with WM load**; beta bursts gate information by suppressing gamma (Lundqvist et al. 2016 *Neuron*) — the burst-based reframing of delay activity.
- **Content-selective delay codes detectable via MVPA across visual hierarchy, parietal, and PFC** — the distributed-storage finding.
- **Human MTL delay activity is stronger for novel than familiar items** — implicating hippocampus in novelty-sensitive WM updating, consistent with [lisman_grace2005_hippocampal_vta](lisman_grace2005_hippocampal_vta.md).
- **Motor/premotor delay activity encodes prospective actions and abstract rules** — supporting the action-oriented PFC view of [christophel2017_distributed_wm](christophel2017_distributed_wm.md).
- **Attractor models reproduce persistent activity but are fragile to noise; activity-silent models reproduce robustness but lack direct neural verification** — the trade-off between the two main computational families.

## 6. Critique / limitations

This review codifies the field's modern consensus but several aspects remain unresolved or contested.

- **Necessarily speculative on causal mechanisms.** The activity-silent claims still require direct neural readout; pinging-based tests (Wolff et al. 2017) partially support, others (Schneegans & Bays 2017) refute. The mechanism debate is not settled.
- **Heavy reliance on NHP and mouse work**; cross-species mapping to human WM remains imperfect, especially for the thalamocortical-loop claim which rests largely on mouse optogenetics.
- **Doesn't strongly adjudicate between competing computational models** — leaves the field unresolved on attractor vs activity-silent vs burst-based as the dominant mechanism.
- **Treats "WM" and "delay activity" as nearly synonymous**; downplays delay-period processes unrelated to storage (e.g., decision preparation, motor planning that happens to occupy the same time window).
- **The distributed view risks underdetermination.** If *every* region can contribute, what differentiates WM from general attention or from ongoing perception?
- **Limited treatment of behavioral consequences.** Links from neural delay code (gamma bursts, subspace dimensions, thalamic loops) to recall precision / capacity / behavior are sparse.
- **Pre-dates much of the 2020-2024 work** on persistent vs silent debate (Schurgin et al. 2020; Stokes lab updates 2021-2024) — some claims need updating.
- **Underweights ventral-stream content-specific evidence** relative to frontoparietal control evidence; the review is somewhat frontoparietal-biased.

## 7. Connection to our work

Sreenivasan & D'Esposito 2019 is one of the most architecturally consequential reviews for the user's program because it crystallizes three architectural commitments simultaneously.

**Touchpoint 1: distributed delay activity = multi-compartmental memory.** The review's empirical synthesis — WM contents maintained across V1-V4, IPS, premotor, MTL, PFC, basal ganglia, and thalamus simultaneously — is the modern empirical anchor for the user's [multi_compartmental_memory](../concepts/multi_compartmental_memory.md) commitment. Each compartment in the user's architecture is the analog of a cortical region carrying its own form of delay activity; the V1-paired shallow memory holds fine-grained perceptual content, the V4-paired deep memory holds abstract object content, etc. The architectural choice is *biologically licensed* by the distributed-delay-activity finding.

**Touchpoint 2: thalamocortical loops = Feedback Transformer central attention.** The review's emphasis on *thalamocortical loops as the causal sustaining substrate* for cortical delay activity is the biological warrant for the user's architectural commitment to a *central recurrent pathway* (the Feedback Transformer) between hubs. The thalamus in cortex plays the role of an inter-cortical integrator: it receives projections from multiple cortical areas, integrates them through its own dynamics, and sends back projections that sustain cortical delay activity. The user's central self-attention substrate plays an architecturally homologous role: it receives queries/keys from all hubs, integrates them via attention, and sends back integrated values that update each hub's recurrent state. This is one of the deepest biological warrants for the user's central architectural commitment.

**Touchpoint 3: heterogeneous delay activity = no single architectural commitment to "memory."** The review's "delay activity is heterogeneous" finding (stable persistent firing, dynamic/sequential, oscillatory bursts, activity-silent synaptic states all coexist) has a direct architectural implication: the user's memory state should not be expected to look any *one* way at any given time. Some compartments may carry stable codes; others may rotate dynamically; others may go silent and re-emerge under pinging. The user's architecture, with multiple compartments each with its own update gate, time constant, and update history, naturally accommodates this heterogeneity. The architectural recommendation: probe each compartment in multiple ways (stable decoder, dynamic decoder, perturbation pinging) and expect different signatures from different compartments — *that is what the biological substrate does*.

**Touchpoint 4: dynamic coding implies non-stationary memory state.** The Murray et al. 2017 stable-subspace + dynamic-single-unit finding, integrated into this review, has direct architectural implications. The user's memory state $C^{(t)}$ should have a *stable subspace* (the coding subspace that holds the content) coexisting with *dynamic subspaces* (orthogonal directions that morph over time). The architectural commitment to update-gate bias = 0 ([concepts/gridcell_rnn.md](../concepts/gridcell_rnn.md) Refinement 3) achieves this: continuous updates morph the *dynamic* component while the *stable* component (held by the SIP residual + update-gate dynamics) is preserved. The user's architecture therefore already accommodates the stable/dynamic dissociation.

**Touchpoint 5: PFC as goal/control storage = the deepest compartment's role.** The review's claim that PFC stores *goal and control* information rather than raw content sharpens the design specification for the user's deepest memory compartment: its content should be diagnostic of the *response* or *task variable* the system is preparing, not of the raw stimulus features. This converges with the abstraction-gradient inference from [christophel2017_distributed_wm](christophel2017_distributed_wm.md). The architectural target for the user's deepest compartment is *control variables* (attention priors, task rules, decision thresholds, prospective actions) rather than perceptual codes.

**Touchpoint 6: the three mechanistic families map to three architectural commitments.** The review identifies three mechanistic families for sustaining delay activity: (i) *intrinsic bistability* (single cells with bistable dynamics), (ii) *recurrent attractor networks* (network-level fixed points), (iii) *short-term synaptic plasticity* (activity-silent traces). The user's architecture has architectural analogs for each: (i) the LSTM cell's gated state holds intrinsic bistability; (ii) the recurrent self-attention pathway implements network-level attractor-like dynamics; (iii) the slow gate bias creates an effectively-silent state for low-attended compartments. The user's architecture is therefore a *hybrid* of all three mechanistic families, which the review argues is the biological reality.

**Touchpoint 7: empirical analysis protocol for the user's models.** The review's "heterogeneous delay activity" insight implies a specific empirical protocol for the user's models: probe the memory state at multiple times during the delay (early, mid, late) with multiple decoders (stable cross-temporal, time-specific dynamic, perturbation-pinging). Different signatures from different probes is expected, not a problem. The full empirical characterization of the user's memory state should therefore mimic the multi-method protocol the review consolidates from biology — fMRI MVPA (population subspaces), single-unit (per-cell dynamics), TMS pinging (activity-silent), and behavioral capacity probes — to fully characterize what the model has learned to hold.

**Touchpoint 8: MTL delay activity for novel items = hippocampus-VTA loop convergence.** The review's note that MTL delay activity is stronger for novel than familiar items converges with [lisman_grace2005_hippocampal_vta](lisman_grace2005_hippocampal_vta.md): the hippocampus participates in WM specifically when novelty (mismatch with stored model) is present, and that participation is gated by VTA dopamine. The user's program already commits to this novelty-gated slow-memory write; Sreenivasan-D'Esposito 2019 provides the empirical anchor for the MTL involvement in WM under novelty.

## 8. Citations to follow

- `lundqvist2018_gamma_beta_bursts_nat_comm` — *Nature Communications* — gamma/beta bursts and discrete WM; the burst-based mechanism. Not in seed.
- [constantinidis2018_persistent_activity](constantinidis2018_persistent_activity.md) — the persistent-activity defense; the contrast position. In seed.
- `wolff_jochim_akyurek_stokes2017_pinging_nat_neuro` — *Nature Neuroscience* — the activity-silent pinging evidence. Not in seed.
- `schurgin_wixted_brady2020_wm_precision_nhb` — *Nature Human Behaviour* — WM precision and signal-detection; the modern capacity framework. Not in seed.
- `rademaker_chunharas_serences2019_distractor_resistant_visual_wm` — *Nature Neuroscience* — distractor-resistant WM coding in visual cortex; the necessity vs sufficiency dissociation. Not in seed.
- `christophel_iamshchinina_haynes2018_attended_unattended_wm` — *Nature Neuroscience* — content-selectivity in frontal vs visual. Not in seed.
- `bouchacourt_buschman2019_flexible_random_network` — *Neuron* — flexible random-network model of WM. Not in seed.
- `lorenc_sreenivasan_desposito2018_flexible_coding` — *J Neurosci* — distractor resistance in WM coding. Not in seed.
- `curtis_sprague2021_abstract_coding_frontoparietal` — *JoCN* — abstract coding in frontoparietal cortex. Not in seed.
- [panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md) — shared attention-WM mechanisms in PFC. In seed.
- `stokes_muhle_karbe_myers2020_dynamic_silent_updates` — *Curr Opin Behav Sci* — dynamic and activity-silent updates. Not in seed.
- `miller_lundqvist_bastos2018_wm_2_neuron` — *Neuron* — "Working memory 2.0"; Miller's modernized framework. Not in seed.
- [masse2019_circuit_wm](masse2019_circuit_wm.md) — circuit mechanisms for WM maintenance and manipulation. In seed.
- [sherman2022_ctc_loop](sherman2022_ctc_loop.md) — cortico-thalamo-cortical loops as the integrator pathway; the thalamic-causal substrate. In seed.
