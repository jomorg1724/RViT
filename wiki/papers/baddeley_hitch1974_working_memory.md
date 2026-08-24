---
id: baddeley_hitch1974_working_memory
title: "Working Memory"
authors:
  - "Baddeley, Alan D."
  - "Hitch, Graham J."
year: 1974
venue: "Psychology of Learning and Motivation (G. H. Bower, Ed.), Vol. 8, pp. 47-89. New York: Academic Press"
doi: "10.1016/S0079-7421(08)60452-1"
arxiv: ""
url: "https://www.sciencedirect.com/science/article/pii/S0079742108604521"
tags:
  - working-memory
  - cognitive-architecture
  - dual-task
  - theoretical
  - foundational
concepts:
  - multi_compartmental_memory
  - slow_fast_recurrence
  - coalition_resource_competition
related:
  - postle2006_wm_emergent
  - awh_jonides2001_overlapping_attention_wm
  - oberauer2002_access_wm
  - desposito_postle2015_wm_neuroscience
  - panichello_buschman2021_shared_mechanisms
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

# Working Memory

## 1. Abstract

The 1974 book chapter pre-dates the *Psychology of Learning and Motivation* series convention of supplying formal chapter abstracts; no verbatim abstract appears in the original publication. The chapter opens by arguing that the unitary short-term store (STS) of the Atkinson–Shiffrin modal model is empirically inadequate, and proceeds to develop the *working memory* alternative through a programmatic sequence of dual-task experiments. The proposal is a tripartite architecture: a limited-capacity *central executive* that controls processing and allocates attentional resources, served by two specialized *slave systems* — a *phonological loop* (originally articulatory loop) for verbal/phonological material, and a *visuospatial sketchpad* for visual and spatial material. The chapter operationally defines working memory as the system that simultaneously stores and processes information in service of higher cognition (reasoning, comprehension, learning), not merely as the passive temporary store of the modal model.

## 2. Why this matters for us

Baddeley & Hitch 1974 is the *origin point* of the entire computational and biological literature on working memory that the user's program engages with. Every paper in the user's WM corpus — Luck & Vogel, Bays & Husain, Olivers, Postle, D'Esposito & Postle, Stokes, Christophel, Panichello & Buschman — is in conversation with this chapter, either elaborating, extending, or contesting it. For the user's architecture, the chapter matters in three load-bearing ways. First, it establishes the *fractionability* principle: working memory is not one unitary buffer but a coordinated assembly of specialized systems, which is the cognitive-psychology source of the user's `multi_compartmental_memory` commitment. Second, it introduces the *central executive* construct — the resource allocator over slave systems — which corresponds structurally to the Feedback Transformer's central attention in the user's program (the central self-attention that arbitrates among hubs is the architectural analog of Baddeley & Hitch's central executive arbitrating among slave systems). Third, the *dual-task logic* the chapter establishes — concurrent secondary task selectively impairs one subsystem while leaving others intact — is the empirical paradigm that any computational model of working memory must reproduce; the user's multi-hub system is partly motivated by the prediction that hub-specific loss perturbations should produce dual-task-style selective interference.

## 3. Key claims

1. The unitary STS of Atkinson & Shiffrin (1968) is theoretically and empirically inadequate; short-term memory must be replaced by a multi-component working memory.
2. Working memory is a control system with limited capacity that is *fractionable* into specialized subsystems with dissociable empirical profiles.
3. A *central executive* coordinates subsidiary slave systems and allocates attentional/processing resources between them.
4. A *phonological loop* (originally articulatory loop) holds phonologically-coded verbal material via subvocal rehearsal; its time constant is set by articulation rate.
5. A *visuospatial sketchpad* maintains visual/spatial material in a code separable from verbal material.
6. Concurrent digit load impairs reasoning, comprehension, and learning only modestly — incompatible with a single STS bottleneck for higher cognition, supporting separable storage and processing resources.
7. Working memory mediates higher cognition (reasoning, comprehension, learning) rather than serving as a passive transit station to long-term memory.
8. Phonological similarity and word-length effects in immediate serial recall index distinct loop properties (rehearsal-based coding and time-based decay).
9. Articulatory suppression selectively eliminates phonological-loop effects on visually presented material, dissociating loop access from primary sensory pathways.
10. The phonological loop and visuospatial sketchpad are doubly dissociable — a domain-specific concurrent task in one domain leaves the other intact.

## 4. Methods

The chapter is methodologically dominated by a *dual-task* design: subjects perform a *primary* cognitive task (grammatical-transformation reasoning, prose comprehension, paired-associate learning, free recall) while concurrently holding *secondary* digit-sequence loads of variable length (typically 0, 1, 2, 4, 6, or 8 items) in short-term memory. Performance on the primary task is plotted as a function of concurrent-load size; the predicted signature of a unitary STS — a steep, monotonic decrement in primary-task performance with increasing concurrent load — fails to appear in the data, with most primary tasks tolerating loads up to 6 items with only modest (~20-35%) RT increases and minimal accuracy loss. The chapter complements this with *articulatory suppression* manipulations (subjects continuously repeat an irrelevant word during the primary task, blocking subvocal rehearsal) to isolate the contribution of the articulatory/phonological loop, and with *unattended-modality* manipulations (visually presented vs. auditory items under suppression) to dissociate sensory and rehearsal contributions. Logical structure of the argument: each experiment is designed to falsify a specific unitary-STS prediction; the multi-component working memory model is built up as the cumulative best-fit architecture across the dissociations the chapter establishes.

## 5. Results

The 1974 chapter is largely a programmatic theoretical paper supported by selected dual-task experiments; the headline quantitative results are:

- **Grammatical reasoning under concurrent load:** RTs increased only modestly (~35%) under a 6-digit concurrent load, with error rates approximately constant. Reasoning is incompatible with being limited by a unitary STS that has been substantially occupied.
- **Prose comprehension:** preserved under concurrent digit loads up to ~6 items; semantic processing of prose proceeds without large dual-task cost.
- **Free recall:** the recency portion of supraspan free-recall lists is *unaffected* by a concurrent digit preload — dissociating recency from STS and prefiguring later work distinguishing primary from secondary memory.
- **Paired-associate learning:** acquisition curves are largely intact under modest concurrent loads, again contradicting a single-resource STS account.
- **Articulatory suppression:** abolishes the phonological-similarity effect for visually presented items but leaves it intact for auditorily presented items, isolating the role of the subvocal rehearsal loop in re-coding visual material.
- **Word-length effects:** immediate serial recall span depends on articulation rate (longer words → shorter spans) — the empirical basis for the time-based phonological-loop model.
- **Visuospatial dual-task:** concurrent visuospatial pursuit tasks selectively impair visuospatial WM (imagery, sketchpad) while leaving verbal STM intact, supporting the sketchpad as a distinct system.
- **Capacity estimates:** the phonological loop holds roughly what can be articulated in ~2 seconds (the "Brown-Peterson" time constant in this framework).

## 6. Critique / limitations

Baddeley & Hitch 1974 has aged remarkably well as a programmatic statement but several of its commitments have been refined or challenged.

- **The central executive is under-specified.** It is defined largely by exclusion — "what the slave systems are not" — and functions as a homunculus that absorbs every cognitive operation the slave systems do not explain. Subsequent work (Baddeley 1996, 2000) sub-divided the executive into focusing, dividing, switching, and updating components, but the executive remained the model's weakest construct.
- **The episodic buffer was missing.** The original three-component model had no dedicated multimodal binding store; Baddeley (2000) added the *episodic buffer* as a fourth component to handle cross-modal chunking and long-term-memory interfacing. The 1974 chapter therefore omits binding entirely.
- **Capacity quantification is weak.** Each slave system's capacity is hard to isolate because tasks rarely cleanly tax one component; the model gives no closed-form expression for capacity limits.
- **Weak initial grounding for the visuospatial sketchpad.** The chapter relies heavily on verbal dual-task evidence; the sketchpad is sketched rather than demonstrated, and the visuospatial WM literature did not converge for another decade (Logie 1995).
- **The phonological loop's strict temporal/articulatory account has been contested.** Jones & Macken (1995) and related "changing-state" theories propose feature-based accounts that handle the same data without the rehearsal loop.
- **Largely behavioral and pre-imaging.** The model makes no neural predictions; it predated single-unit work on PFC delay activity (Funahashi 1989, Goldman-Rakic 1995) and human fMRI by decades.
- **The WM-LTM boundary has blurred.** Ericsson & Kintsch's (1995) long-term WM and Cowan's (1988, 2001) embedded-process model both reject the sharp WM/LTM dichotomy this chapter assumes, instead treating WM as activated LTM.
- **Limited treatment of binding, chunking, and serial-order coding.** Serial-order phenomena that dominate the modern WM literature (Hurlstone, Hitch & Baddeley 2014) are not addressed; the loop is silent about how items are bound to positions.
- **Attention is treated as resource, not selection.** The 1974 chapter does not deeply engage with the Posner attention literature; the unification of selective attention and WM (`papers/awh_jonides2001_overlapping_attention_wm.md`, `papers/postle2006_wm_emergent.md`) would not arrive for 25+ years.
- **The "central executive" sits in tension with the modern distributed view.** Christophel et al. (2017, `papers/christophel2017_distributed_wm.md`) and Postle (2006, `papers/postle2006_wm_emergent.md`) reject the central-executive-as-PFC localization that 1974 implicitly invited; WM contents are now thought to be represented across a distributed cortical network.

## 7. Connection to our work

This chapter is the cognitive-psychology load-bearing reference for the user's commitment to *multi-component, fractionated* working memory; several distinct architectural touchpoints connect the 1974 model to the user's program.

**Touchpoint 1: multi-compartmental memory as the architectural analog of slave-system fractionation.** Baddeley & Hitch's central insight — that working memory is not one buffer but a coordinated assembly of specialized stores — is the cognitive-psychology source of the user's `multi_compartmental_memory` commitment ([concepts/multi_compartmental_memory.md](../concepts/multi_compartmental_memory.md)). PRISM v2's `M_fast`/`M_slow` split is a two-component instantiation of the same fractionation logic; the user's program calls for at least three compartments paired with V1/V2/V4-like spatial resolutions and progressively slower update rates. The architectural recommendation that follows is that the compartments should be empirically dissociable — perturbing one should leave the others functionally intact, recapitulating Baddeley & Hitch's dual-task signature.

**Touchpoint 2: the central executive as the Feedback Transformer's central attention.** The 1974 model's central executive — a limited-capacity controller that allocates resources across slave systems — has a clean architectural homolog in the user's program: the *central self-attention* of the Feedback Transformer ([concepts/feedback_transformer.md](../concepts/feedback_transformer.md)) arbitrates among hubs by allocating attention weight, with the constraint that total attention sums to a fixed budget. The Q/K manipulation by which hubs compete for self-attention bandwidth is the architectural analog of Baddeley's executive distributing attention across slave systems. This isomorphism gives the user's `coalition_resource_competition` concept a direct cognitive-psychology genealogy.

**Touchpoint 3: dual-task selective interference as an empirical signature.** Baddeley & Hitch's dual-task logic — that loading slave system A while performing primary task in slave system B leaves B intact, while loading A while performing in A degrades performance — is a falsifiable prediction the user's multi-hub system should reproduce. Specifically: perturbing one hub's loss function should selectively degrade tasks that depend on that hub's representations while leaving other hubs functional. The dual-task paradigm therefore becomes a *behavioral signature* for empirically validating whether the user's architecture has actually instantiated fractionated working memory, or merely shuffled the same operations across nominally distinct modules. This is a direct experimental program for the multi-hub system.

**Touchpoint 4: the phonological-loop time constant as a chrono-init analog.** The phonological loop's defining property is its time constant — the loop holds what can be re-articulated in roughly two seconds, with longer items decaying faster. This is the cognitive-psychology version of the `slow_fast_recurrence` time-constant logic the user's program implements via Tallec-Ollivier chrono-init ([concepts/slow_fast_recurrence.md](../concepts/slow_fast_recurrence.md)). Each compartment should have its own characteristic decay/retention time constant, set by its update gate's bias, matching the timescale of the content it maintains — fast for moment-to-moment per-frame evidence (`M_fast`, gate bias ~−1), slow for trial-spanning context (`M_slow`, gate bias ~−3).

**Touchpoint 5: working memory as in-the-service-of higher cognition.** The 1974 chapter's most important conceptual move — defining WM as the system that simultaneously *stores and processes* in service of reasoning, comprehension, and learning — is the cognitive-psychology source of the user's commitment that memory in the recurrent ViT is not a passive buffer but an *active substrate for ongoing computation*. The memory's job is not to hold the input verbatim but to maintain the partial-result representations that downstream computations consume. This is why the user's architecture places memory and computation in the same compartment (the GridCell RNN's internal state both stores and computes), rather than separating them into static buffer + computation engine. Baddeley & Hitch's working memory is *active* working memory; so is the user's.

**Touchpoint 6: the episodic-buffer gap as a target for the user's slow memory.** The episodic buffer that Baddeley (2000) had to add as a fourth component handles multimodal binding and the interface with long-term memory — exactly the functional role the user's slow memory and the [`lisman_grace2005_hippocampal_vta`](lisman_grace2005_hippocampal_vta.md) hippocampus-VTA loop are positioned to support. The user's slow-memory compartment, gated by novelty-driven prediction-error (Lisman-Grace), is functionally the episodic buffer with a biological gate mechanism that Baddeley's framework lacked. This is a substantive synthesis: the user's architecture supplies the missing mechanism that the cognitive-psychology framework had to posit by hand.

**Touchpoint 7: the relation to attention is foreshadowed but not resolved.** Baddeley & Hitch 1974 anticipates but does not develop the attention-WM relationship; that synthesis arrived 25+ years later (Awh & Jonides 2001, Postle 2006, Kiyonaga & Egner 2013). The user's program inherits this synthesis: the central self-attention substrate that connects hubs is *simultaneously* the attention mechanism and the WM-control mechanism, with no architectural separation between them — directly mirroring Panichello & Buschman 2021's "shared mechanisms" finding. The 1974 chapter is therefore a starting point whose unification with the attention literature is one of the load-bearing theoretical commitments of the user's program.

## 8. Citations to follow

- `cowan1988_attention_memory` — Cowan's evolving conceptions of memory storage and selective attention; the alternative embedded-process framework that subsumes WM into activated LTM. Not in seed.
- `baddeley2000_episodic_buffer` — Baddeley's addition of the episodic buffer as the fourth component; the response to the binding/multimodal gap. Not in seed.
- `baddeley2003_wm_review` — Baddeley's *Nature Reviews Neuroscience* retrospective; the modern-era restatement of the WM framework with neural data. Not in seed.
- `cowan2001_magical_number_4` — the magical number 4 in short-term memory; capacity-limit account that competes with the slot debate. Not in seed.
- `ericsson_kintsch1995_long_term_wm` — long-term working memory; the WM-LTM boundary-blurring framework. Not in seed.
- `engle1999_wm_intelligence` — working memory, short-term memory, and general fluid intelligence; the individual-differences extension. Not in seed.
- `logie1995_visuospatial_wm` — Logie's book-length development of the visuospatial sketchpad. Not in seed.
- `jones_macken1995_phonological_critique` — the changing-state critique of the phonological-loop account. Not in seed.
- `hurlstone_hitch_baddeley2014_serial_order` — memory for serial order across domains; the serial-order gap the original loop did not address. Not in seed.
- [postle2006_wm_emergent](postle2006_wm_emergent.md) — the emergent-property alternative to the Baddeley-Hitch architecture; rejects dedicated buffers in favor of attention-recruited posterior cortex. In seed.
- [awh_jonides2001_overlapping_attention_wm](awh_jonides2001_overlapping_attention_wm.md) — the attention-WM bridge the 1974 chapter foreshadows but does not develop. In seed.
- [desposito_postle2015_wm_neuroscience](desposito_postle2015_wm_neuroscience.md) — the modern neural-substrate review that continues the Postle 2006 line. In seed.
- [panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md) — the shared-mechanisms-of-attention-and-WM PFC paper that closes the loop. In seed.
