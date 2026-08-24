---
id: christophel2017_distributed_wm
title: "The Distributed Nature of Working Memory"
authors:
  - "Christophel, Thomas B."
  - "Klink, P. Christiaan"
  - "Spitzer, Bernhard"
  - "Roelfsema, Pieter R."
  - "Haynes, John-Dylan"
year: 2017
venue: "Trends in Cognitive Sciences"
doi: "10.1016/j.tics.2016.12.007"
arxiv: ""
url: "https://www.cell.com/trends/cognitive-sciences/abstract/S1364-6613(16)30221-X"
tags:
  - working-memory
  - distributed-coding
  - sensory-recruitment
  - mvpa
  - delay-activity
  - review
concepts:
  - multi_compartmental_memory
  - bidirectional_hierarchical_feedback
  - hierarchical_predictive_coding
  - top-down-feedback
related:
  - postle2006_wm_emergent
  - desposito_postle2015_wm_neuroscience
  - stokes2015_activity_silent_wm
  - sreenivasan_desposito2019_delay_activity
  - panichello_buschman2021_shared_mechanisms
  - constantinidis2018_persistent_activity
  - awh_jonides2001_overlapping_attention_wm
  - foster2017_alpha_vwm
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

# The Distributed Nature of Working Memory

## 1. Abstract

> "Studies in humans and non-human primates have provided evidence for storage of working memory contents in multiple regions ranging from sensory to parietal and prefrontal cortex. We discuss potential explanations for these distributed representations: (i) features in sensory regions versus prefrontal cortex differ in the level of abstractness and generalizability; and (ii) features in prefrontal cortex reflect representations that are transformed for guidance of upcoming behavioral actions. We propose that the propensity to produce persistent activity is a general feature of cortical networks. Future studies may have to shift focus from asking where working memory can be observed in the brain to how a range of specialized brain areas together transform sensory information into a delayed behavioral response." (Christophel, Klink, Spitzer, Roelfsema & Haynes 2017, *Trends in Cognitive Sciences* 21(2):111-124, abstract.)

## 2. Why this matters for us

Christophel et al. 2017 is the most direct biological warrant for the user's [multi_compartmental_memory](../concepts/multi_compartmental_memory.md) commitment. The review's central empirical synthesis — that WM contents are simultaneously represented in V1-V4, IPS/posterior parietal, premotor, and PFC at *progressively higher levels of abstraction* — is exactly the cortical-hierarchy organization the user's program commits to with its V1/V2/V4-paired memory compartments. The review also re-frames the field's central question from "where is WM?" to "how do specialized regions cooperate to transform sensory information into a delayed response?" — which is precisely the question the user's multi-hub, Feedback-Transformer-coupled architecture is engineered to answer. The level-of-abstractness gradient (concrete sensory features in early areas → categorical/rule-related codes in PFC) directly motivates the user's hierarchical memory split, where shallow memory carries low-level visual primitives and deep memory carries object-level / task-level abstractions.

## 3. Key claims

1. WM contents are represented across a *distributed* network spanning sensory cortex, parietal cortex, and prefrontal cortex — not localized to PFC.
2. Different cortical regions hold the *same* memorandum at *different levels of abstraction* — sensory cortex stores concrete features, parietal stores intermediate codes, PFC stores categorical/rule-related abstractions.
3. Prefrontal codes are biased toward task-relevant, *action-oriented transformations* of the input — they represent what the stimulus *means for behavior*, not the raw stimulus.
4. *Persistent activity is a generic cortical capability* rather than a PFC specialization — it has been documented in V1, V4, IT, parietal, premotor, and prefrontal cortex.
5. Distributed storage explains why early sensory areas can be decoded during delays (V1-V4 MVPA shows orientation/color/motion content even at low BOLD baseline).
6. The hierarchy of WM codes *parallels the perception-to-action processing hierarchy* — WM content recapitulates the cortical processing chain it was acquired through.
7. The classic "WM is in PFC" view derived from single-unit work in delayed-response tasks is too narrow; PFC is one node in a distributed system.
8. The right empirical question is *how distributed regions cooperate*, not *where WM lives* — research should focus on cross-region interaction.

## 4. Methods

This is a narrative review of monkey single-unit, monkey/human fMRI MVPA, EEG/MEG decoding, and TMS studies of delayed-match-to-sample and delayed-recall paradigms, organized across visual, auditory, somatosensory, and numerical/abstract domains. The argument structure is to canvas each cortical region in turn (V1-V4, MT, IT, IPS/SPL, premotor, PFC) and consolidate the evidence that *each* region carries content-specific delay representations, then to integrate the regions into a hierarchical scheme organized by representational abstraction. The methodological centerpiece is MVPA, which decodes stimulus-specific content from BOLD patterns; the review weighs decoding evidence from many groups (Harrison & Tong, Serences, Riggall, Postle, Sprague, Ester, Lewis-Peacock, Bettencourt & Xu) against each other to identify which regions reliably carry content. Persistent firing data from monkey work (Funahashi, Miller, Constantinidis) are integrated in the synthesis, with the framing that single-unit persistent activity is *one* form of distributed storage rather than *the* mechanism.

## 5. Results

The review consolidates the following empirical anchors from the primary literature:

- **V1-V4 MVPA decodes orientation, color, and motion through delays of up to ~10 s** (Harrison & Tong 2009 *Nature*; Serences, Ester, Vogel & Awh 2009 *Psych Sci*) — the foundational result for sensory-recruitment / distributed storage.
- **IPS/posterior parietal cortex carries stimulus-specific WM codes** that often *exceed* sensory-cortex decoding accuracy (Bettencourt & Xu 2016; Sprague, Ester & Serences 2014); under distraction, parietal codes are more robust than sensory codes.
- **Lateral PFC encodes categorical/rule-related rather than veridical sensory codes** (Freedman, Riesenhuber, Poggio & Miller 2001; Wallis, Anderson & Miller 2001) — the abstraction-level gradient.
- **Auditory cortex sustains content-specific delay representations for pitch** (Linke, Vicente-Grabovetsky & Cusack 2011), demonstrating that distributed storage is not unique to vision.
- **Cross-region representational similarity falls off with hierarchical distance** — early sensory and PFC code geometries differ; intermediate regions form a continuum.
- **TMS to occipital cortex disrupts visual WM precision**; TMS to FEF/parietal disrupts spatial WM — the regional double-dissociation expected if storage is distributed by content.
- **Persistent firing has been observed in V1, V4, IT, parietal, premotor and prefrontal cortex** (Super, Spekreijse & Lamme 2001 in V1; Pessoa & Desimone 2003 in V4 etc.) — persistent activity is *not* a PFC monopoly.
- **Decoding accuracy in PFC depends on whether the task taps abstract/categorical vs veridical representations** — confirming the abstraction-gradient hypothesis: PFC is "stronger" on rule-related codes, weaker on raw feature codes.

## 6. Critique / limitations

The distributed-WM synthesis is influential but has several gaps and contested aspects.

- **Cross-modal/cross-task synthesis sometimes glosses over methodological differences** (TMS, MVPA, single-unit) — the apparent agreement across methods may partly reflect cherry-picking compatible studies.
- **"Distributed" claim risks underspecifying which regions are *causally necessary* versus *merely correlated*.** MVPA decodability ≠ functional necessity; only TMS/lesion evidence speaks to causal role, and that evidence is sparse for some regions.
- **MVPA decodability ≠ functional role** — the review does not always distinguish the two; a region can carry decodable information without being the substrate of WM storage in a causally meaningful sense.
- **Power and signal-to-noise differences between regions** can produce apparent gradients of decoding accuracy that are methodological rather than representational. PFC voxels are larger and noisier than V1 voxels, so the "weaker PFC decoding" finding partly reflects measurement.
- **Limited treatment of subcortical contributions** (thalamus, hippocampus, striatum) — the review is cortex-centric, missing the thalamocortical sustaining circuits that Sreenivasan & D'Esposito 2019 later emphasize.
- **Does not deeply integrate activity-silent / STSP frameworks** ([stokes2015_activity_silent_wm](stokes2015_activity_silent_wm.md)) — the review treats distributed storage primarily in terms of active spiking codes, leaving the synaptic-trace mechanism largely unaddressed.
- **Most cited evidence is for visual WM**; auditory, tactile, and abstract domains are less developed in the synthesis.
- **Predictions are largely qualitative**; few falsifiable quantitative claims about which region should carry what abstraction level at what point in the task.

## 7. Connection to our work

Christophel et al. 2017 is the most direct biological warrant for several of the user's most-load-bearing architectural commitments.

**Touchpoint 1: distributed storage is multi-compartmental memory.** The review's central empirical finding — that WM contents are distributed across cortical hierarchy with V1-V4 storing concrete sensory features and PFC storing abstract rule-related codes — is *exactly* the architectural commitment of [concepts/multi_compartmental_memory.md](../concepts/multi_compartmental_memory.md): multiple recurrent states at different cortical levels, each storing the same memorandum at its own abstraction level. PRISM v2's `M_fast` (paired with V1) holds low-level features; `M_slow` (paired with V2) holds higher-level codes; the user's program target of three compartments (V1/V2/V4-paired) instantiates the full distributed-storage gradient. The architectural choice is therefore not a hyperparameter convenience but a direct recapitulation of the cortical organization Christophel et al. document.

**Touchpoint 2: abstraction gradient as channel-dimension gradient.** The review's "level of abstractness" gradient (concrete in V1 → abstract in PFC) maps onto the user's *channel-dimension* gradient in the multi-compartmental memory: shallow memory has many components at small channel dimension (visual primitives for combining flexibly into novel percepts), deep memory has fewer components at high channel dimension (sufficient capacity to represent complex spatio-temporal objects). This is the architectural instantiation of the abstraction gradient: low-level features need many shallow representations; high-level objects need few but rich representations. The architectural justification is therefore *biological* rather than merely engineering — and the abstraction levels can be empirically validated by probing each compartment for the kind of content Christophel et al. predict.

**Touchpoint 3: distributed regions cooperating = inter-hub Feedback Transformer.** The review's central reformulation of the field's question — from "where is WM?" to "how do distributed regions cooperate?" — is *exactly* the question the user's Feedback-Transformer-coupled multi-hub architecture is designed to answer. The user's central self-attention substrate is the cooperation mechanism; it lets each compartment query and be queried by every other compartment, instantiating the inter-region communication Christophel et al. argue is the actual locus of WM function. The biological warrant: distributed storage is empirically real, and the right architectural commitment is to make the *inter-storage communication substrate* a first-class component of the model. This is what the Feedback Transformer is.

**Touchpoint 4: persistent activity as a generic cortical capability — every hub gets a recurrent state.** The review's argument that persistent activity is a *generic* cortical capability rather than a PFC specialization is the biological warrant for the user's architectural commitment that *every* hub (visual, motor, memory, planning) has its own recurrent state, rather than relegating recurrence to a single "memory module." The user's `parallel_recurrent_units` concept (TAXONOMY) is the architectural instantiation of "every cortical area can hold information across delays." The biological warrant gives the design choice a substantive grounding.

**Touchpoint 5: PFC's "transformed for guidance of upcoming behavioral actions" — the user's planning hub.** The review's claim that PFC represents stimulus *as transformed for upcoming action* — not the raw stimulus — is the biological template for the user's planning/control hub. The deepest memory compartment should not hold low-level features but rather *action-relevant transformations* of those features: the policy bias, the expected reward, the next-step planning representation. This sharpens the design specification for the user's deepest compartment: its content should be diagnostic of the *response* the system is preparing to make, not of the stimulus itself.

**Touchpoint 6: bidirectional hierarchical feedback as the architectural substrate.** Christophel et al.'s implicit prediction — that information flows both *up* (sensory → PFC, abstracting) and *down* (PFC → sensory, biasing) — is exactly the user's [bidirectional_hierarchical_feedback](../concepts/bidirectional_hierarchical_feedback.md) commitment. The Feedback Transformer's bidirectional connectivity supports both ascending (low-to-high abstraction) and descending (top-down biasing) communication, instantiating the cross-level information flow the distributed-WM framework requires. The architectural commitment to *full* bidirectional connectivity (rather than feedforward-only) follows directly from the biological organization Christophel et al. document.

**Touchpoint 7: implications for empirical analysis of the user's models.** The distributed-storage finding suggests a specific empirical protocol for the user's models: probe *each* compartment for content of the appropriate abstraction level, not just the deepest compartment for the "answer." If $M_1$ (shallow) carries orientation/color codes and $M_3$ (deep) carries task-rule codes, then a probe targeting orientation in $M_3$ will fail — and that failure is a *correct* prediction of the distributed-storage architecture rather than evidence that the model is broken. The user's evaluation protocols should be *content-specific per compartment*, mirroring the layer-specific MVPA decoding analyses Christophel et al. consolidate.

## 8. Citations to follow

- `sreenivasan_desposito2019_delay_activity` — the follow-on review four years later by Sreenivasan and D'Esposito; already in seed via the WM cluster. In seed.
- `constantinidis_klingberg2016_wm_capacity_training` — neuroscience of WM capacity and training; the orthogonal capacity-limit literature. Not in seed.
- `mendoza_halliday_martinez_trujillo2017_perceived_memorized` — population coding of perceived and memorized visual features; the population-decoding follow-up. Not in seed.
- `bettencourt_xu2016_decoding_under_distraction` — the key result that parietal cortex's WM codes are more distractor-robust than sensory cortex; one of the most consequential follow-ups. Not in seed.
- `ester_sprague_serences2015_parietal_frontal_mnemonic` — *Neuron* paper showing parietal and frontal cortex encode stimulus-specific mnemonic codes. Not in seed.
- `lorenc_sreenivasan_desposito2018_flexible_coding` — flexible coding of visual WM during distraction; the modern extension of the framework. Not in seed.
- `christophel_iamshchinina_haynes2018_attended_unattended_wm` — cortical specialization for attended versus unattended WM; the authors' empirical follow-on. Not in seed.
- `spitzer_haegens2017_beta_oscillations_endogenous` — beta oscillations in endogenous content (re)activation; the oscillatory-mechanism extension. Not in seed.
- `kwak_curtis2022_abstract_mnemonic_format` — abstract format of mnemonic representations in human PFC; the abstraction-level deep-dive. Not in seed.
- [panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md) — shared mechanisms of WM and attention; the empirical convergence with the distributed-control framework. In seed.
- [stokes2015_activity_silent_wm](stokes2015_activity_silent_wm.md) — the activity-silent framework that the distributed-WM view does not fully integrate. In seed.
- `xu2017_reevaluating_sensory_account` — *TiCS* critique of the sensory-account version of distributed storage; the methodological-skeptic position. Not in seed.
