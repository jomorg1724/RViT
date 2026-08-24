---
id: postle2006_wm_emergent
title: "Working memory as an emergent property of the mind and brain"
authors:
  - "Postle, Bradley R."
year: 2006
venue: "Neuroscience"
doi: "10.1016/j.neuroscience.2005.06.005"
arxiv: ""
url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC1428794/"
tags:
  - working-memory
  - emergent-property
  - sensory-recruitment
  - attention
  - theoretical
  - prefrontal-cortex
concepts:
  - coalition_resource_competition
  - multi_compartmental_memory
  - multi_hub_multi_objective_system
  - top-down-feedback
related:
  - baddeley_hitch1974_working_memory
  - desposito_postle2015_wm_neuroscience
  - christophel2017_distributed_wm
  - stokes2015_activity_silent_wm
  - awh_jonides2001_overlapping_attention_wm
  - sreenivasan_desposito2019_delay_activity
  - kiyonaga_egner2013_wm_internal_attention
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

# Working memory as an emergent property of the mind and brain

## 1. Abstract

> "Cognitive neuroscience research on working memory has been largely motivated by a standard model that arose from the melding of psychological theory with neuroscience data. Among the tenets of this standard model are that working memory functions arise from the operation of specialized systems that act as buffers for the storage and manipulation of information, and that frontal cortex (particularly prefrontal cortex) is a critical neural substrate for these specialized systems. However, the standard model has been a victim of its own success, and can no longer accommodate many of the empirical findings of studies that it has motivated. An alternative is proposed: Working memory functions arise through the coordinated recruitment, via attention, of brain systems that have evolved to accomplish sensory-, representation-, and action-related functions. Evidence from behavioral, neuropsychological, electrophysiological, and neuroimaging studies, from monkeys and humans, is considered, as is the question of how to interpret delay-period activity in the prefrontal cortex." (Postle 2006, *Neuroscience* 139(1):23-38, abstract.)

## 2. Why this matters for us

Postle 2006 is the field-defining theoretical statement that *working memory is not a dedicated buffer system* — it is an emergent functional state that arises whenever attention is allocated to internal representations in domain-specific perception/action systems. For the user's program, this is the cognitive-psychology foundation of the *attention-as-memory-substrate* commitment. Every architectural choice in the user's program that does not separate "memory" from "attention" — sharing the central self-attention substrate between hubs, conditioning the attention computation on the previous memory state, gating the memory update by attention — has its conceptual warrant here. The paper is also the field's most direct rejection of the *Baddeley-style central executive + slave systems* architecture in favor of an emergent-recruitment architecture; the user's program inherits this commitment by replacing the central executive with an *emergent* central self-attention that arises from inter-hub competition rather than from a privileged controller.

## 3. Key claims

1. WM is not a dedicated buffer system but an *emergent functional state* arising from attention-driven recruitment of perception/action systems.
2. PFC delay activity reflects *control functions* (interference resolution, goal maintenance, response selection), not storage of content.
3. Domain-specific WM (verbal, visual, spatial) is supported by the *same posterior cortical regions* that perceive that content — the sensory/sensorimotor recruitment view.
4. Spatial WM is rehearsed by *spatial attention or prospective oculomotor codes*, not by a Baddeley-style "visuospatial sketchpad" buffer.
5. Capacity limits reflect *representational fidelity / noise* rather than discrete slots.
6. The brain *opportunistically* recruits whatever codes (verbal, semantic, perceptual, motor) are afforded by the stimulus and the task.
7. A double dissociation in primate lesion work (Petrides) and human patients argues against PFC-as-storage and for PFC-as-control.
8. The unified-attention-and-WM view ([awh_jonides2001_overlapping_attention_wm](awh_jonides2001_overlapping_attention_wm.md)) is a special case of the broader emergent-property framework.

## 4. Methods

This is a theoretical/integrative review. The argument structure is constructive: Postle takes each pillar of the "standard model" (Baddeley's multi-component WM + PFC-as-buffer) and shows that the accumulated empirical evidence — from monkey single-unit electrophysiology, monkey lesion data, human patient neuropsychology, scalp/intracranial EEG, and especially human fMRI/MVPA — is incompatible with it. The integration synthesizes (i) Miller's monkey PFC recordings showing extensive non-content-specific delay activity; (ii) Petrides' monkey lesion dissociations between dorsolateral PFC (manipulation deficits) and anterior temporal cortex (long-delay retention deficits); (iii) human PFC lesion patients with intact basic span; (iv) fMRI showing posterior fusiform gyrus (not PFC) carries content-selective delay activity for object WM in multi-delay paradigms; (v) Todd & Marois' IPS BOLD scaling with VSTM capacity; (vi) concurrent-saccade/finger-tapping selective interference with spatial WM. The synthesis is then articulated as the *emergent-recruitment* alternative: WM is the joint state of (a) attention deployed to (b) whatever perception/action codes the task affords.

## 5. Results

This is a theoretical paper; the empirical anchors Postle consolidates from the primary literature are:

- **Miller's monkey PFC recordings:** many neurons show *non-selective* delay activity, inconsistent with content-specific storage as the primary function.
- **Petrides lesion work:** dissociation between dorsolateral PFC (multi-item manipulation deficits) and anterior temporal cortex (long-delay retention deficits) — separating control and storage.
- **Human PFC lesion patients have intact digit span and delayed recognition** of small loads — incompatible with PFC being the primary storage substrate.
- **fMRI:** posterior fusiform gyrus, not PFC, shows content-selective delay activity for object WM in multi-delay paradigms (Postle's own paradigm).
- **Todd & Marois (2004):** IPS BOLD scales with individual VSTM capacity — implicating parietal cortex as the locus of capacity limitation, not PFC.
- **Concurrent saccades / finger tapping selectively disrupt spatial WM**, supporting the attention/motor-rehearsal view that spatial WM is rehearsed by oculomotor/attention codes.
- **Within-subject effect sizes** for delay-period BOLD load manipulations are 1-2 orders of magnitude larger than group averages, suggesting individual recruitment strategies that an average-PFC story obscures.
- **MVPA decodability of stimulus features in posterior visual cortex during delays** even at near-baseline univariate BOLD — the foundational sensory-recruitment finding.

## 6. Critique / limitations

Postle 2006 is influential but its strong claims have been refined and partially rolled back in subsequent work.

- **The theoretical framework is hard to falsify** — almost any null result for PFC storage can be re-interpreted as "control," and the emergent-property language can absorb nearly any positive finding.
- **Underplays evidence for distinct content-selective PFC populations.** Later work (Riggall & Postle 2012; Christophel et al. 2017, [christophel2017_distributed_wm](christophel2017_distributed_wm.md); Mendoza-Halliday & Martinez-Trujillo 2017) shows that PFC *does* carry content-specific delay codes, especially for abstract / categorical content. Postle 2006's strong PFC-no-storage claim has been softened.
- **The sensory-recruitment claim has been challenged.** Bettencourt & Xu (2016) and Rademaker et al. (2019) show that early visual cortex content can be decoded but is *not necessary* for WM — TMS to V1 during the delay does not abolish recall. Parietal cortex is more critical than V1.
- **Conflates attention with WM in ways that limit empirical separability** (Oberauer 2019 extends this critique). If WM = attention to internal representations, then dissociating the two becomes definitionally impossible, weakening the framework's empirical claims.
- **Says little about activity-silent / synaptic mechanisms** (these became salient post-2010; [stokes2015_activity_silent_wm](stokes2015_activity_silent_wm.md)) — the emergent framework treats WM as ongoing activity, but the active-silent debate complicates this.
- **Largely human-imaging-centric**; the monkey single-unit literature with strong *content-selective* PFC delay tuning (Miller, Funahashi, Romo, Constantinidis) is downplayed.
- **Does not specify computational implementation.** "Emergent recruitment" is a verbal framework, not a formal model; no closed-form expression for how attention recruits sensory codes into WM.
- **Newer work shows PFC delay codes carry uniquely task-abstracted information that posterior areas do not** (Sreenivasan, Curtis, D'Esposito 2014; Kwak & Curtis 2022) — challenging the strong "PFC = control only" claim.

## 7. Connection to our work

Postle 2006 is the cognitive-psychology *theoretical anchor* for the user's most-load-bearing program-level commitment: *memory and attention share substrate*.

**Touchpoint 1: emergent-property thesis as the user's design philosophy.** Postle's central claim — WM is an emergent state arising from attention applied to internal representations, not a dedicated buffer — is the cognitive-psychology source of the user's program-level design choice to *share substrate* between memory and attention. There is no "memory module" and "attention module" in the user's architecture; instead, the central self-attention substrate of the Feedback Transformer simultaneously plays both roles. WM arises *emergently* from the joint state of (a) hub-internal recurrent states holding content and (b) central attention biasing access to that content. The architecture is therefore the engineering instantiation of Postle's theoretical commitment.

**Touchpoint 2: rejection of the central executive — replaced by emergent inter-hub competition.** Postle's framework rejects the Baddeley-style central executive as a privileged controller; the user's architecture inherits this commitment by replacing the executive with an *emergent* coordinator: the central self-attention arises from inter-hub competition for bandwidth, not from a hard-coded controller. The user's [coalition_resource_competition](../concepts/coalition_resource_competition.md) concept is the architectural instantiation of Postle's anti-homunculus stance: there is no agent "deciding what to attend to"; attention is what *emerges* when hubs compete for finite central-attention bandwidth. This is one of the strongest theoretical alignments between Postle and the user's program.

**Touchpoint 3: sensory recruitment as the multi-compartmental-memory commitment.** Postle's claim that WM content lives in domain-specific perception/action codes is the cognitive-psychology source of the user's commitment to memory compartments paired with V1/V2/V4-equivalent cortical levels ([concepts/multi_compartmental_memory.md](../concepts/multi_compartmental_memory.md)). The shallow memory ($M_{fast}$ paired with V1) holds low-level perceptual content; deeper memory holds higher-abstraction codes; the entire memory hierarchy is *content-paired* rather than buffered into an abstract central store. This is sensory recruitment at the architectural level.

**Touchpoint 4: opportunistic recruitment of multiple codes — multi-hub multi-objective system.** Postle's "the brain opportunistically recruits whatever codes are afforded" maps onto the user's [multi_hub_multi_objective_system](../concepts/multi_hub_multi_objective_system.md) commitment: multiple hubs (visual, motor, memory, planning) are co-engaged whenever the task affords useful contributions from each; the system is not committed to any single processing pathway. The architectural instantiation of opportunistic recruitment is the *competitive* inter-hub dynamics — hubs that have useful contributions for the current task win attention weight; hubs that do not are silent. This is Postle's recruitment at the multi-hub level.

**Touchpoint 5: spatial attention as the spatial-WM rehearsal mechanism.** Postle's claim that spatial WM is *rehearsed* by spatial attention / prospective oculomotor codes (consistent with [awh_jonides2001_overlapping_attention_wm](awh_jonides2001_overlapping_attention_wm.md)) is directly instantiated in the user's architecture: the central attention substrate operating on the grid-cell memory state *is* the spatial rehearsal mechanism. When the central attention focuses on grid position $(i, j)$ in $M_{fast}$, that position's content gets refreshed and integrated; this is the architectural analog of "spatial attention rehearsing spatial WM contents." The user's architecture therefore reproduces the empirical finding by construction.

**Touchpoint 6: capacity from representational fidelity, not discrete slots.** Postle's claim that capacity limits arise from representational fidelity / noise rather than discrete slots converges with [bays_husain2008_dynamic_resources](bays_husain2008_dynamic_resources.md). The architectural implication for the user's models: capacity should *not* be hard-coded (e.g., as a fixed slot count) but should *emerge* from the noise properties of the recurrent state, the competition for central attention bandwidth, and the gradient-driven precision of the encoding. The user's architecture already commits to this: there is no explicit slot count anywhere; capacity emerges from the dynamics. This is one of the deepest alignments between Postle's theoretical framework and the user's architecture.

**Touchpoint 7: the framework's underspecified computational implementation — gap the user fills.** Postle's framework is verbal/theoretical; it does not specify a formal model of "attention recruitment." The user's architecture *is* a formal model: the Feedback Transformer with hubs holding content, the central self-attention substrate arbitrating access, and the gated memory updates all together constitute a *computationally explicit* instantiation of Postle's emergent-recruitment framework. This is one of the strongest contributions the user's program makes to the WM literature: it supplies the missing computational implementation that Postle's verbal framework requires.

**Touchpoint 8: implications for empirical analysis of the user's models.** The emergent-recruitment view predicts that the *same* recurrent state should support multiple WM functions (storage, comparison, response preparation) depending on which attention pattern is applied. Empirical analyses of the user's models should therefore look for *task-conditional re-use* of the same memory state: probing $M_{fast}$ with different attention queries should extract different content (orientation under one query, color under another, position under a third). If the user's architecture passes this test, it has empirically validated Postle's emergent-recruitment framework at the model level.

## 8. Citations to follow

- `desposito2007_cognitive_neural_wm_phil_trans_b` — D'Esposito's *Phil Trans B* paper that complements this one. Not in seed.
- [desposito_postle2015_wm_neuroscience](desposito_postle2015_wm_neuroscience.md) — the modern follow-on review by Postle and D'Esposito. In seed.
- `sreenivasan_curtis_desposito2014_persistent_activity_revisited` — *TiCS* — the conceptual bridge from Postle 2006 to D'Esposito-Postle 2015. Not in seed.
- `lewis_peacock_drysdale_oberauer_postle2012_focus_attention` — *JoCN* — neural evidence for a distinction between short-term memory and the focus of attention; the empirical follow-up. Not in seed.
- `riggall_postle2012_wm_storage_elevated_activity` — *J Neurosci* — MVPA of WM content in visual vs PFC; the empirical refinement. Not in seed.
- `serences2016_storage_review` — *Brain Research* — review extending sensory recruitment; the modern synthesis. Not in seed.
- [christophel2017_distributed_wm](christophel2017_distributed_wm.md) — the distributed-storage review that updates the sensory-recruitment view. In seed.
- [sreenivasan_desposito2019_delay_activity](sreenivasan_desposito2019_delay_activity.md) — the modern delay-activity review. In seed.
- `lorenc_sreenivasan2021_distributed_wm` — *Curr Opin Behav Sci* — distributed WM mechanisms. Not in seed.
- `oberauer2019_wm_formal_models_critique` — *Annu Rev Psych* — formal models of WM that critique sensory recruitment. Not in seed.
- [awh_jonides2001_overlapping_attention_wm](awh_jonides2001_overlapping_attention_wm.md) — the foundational attention-WM overlap paper that Postle generalizes. In seed.
- [panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md) — the shared-substrate empirical demonstration that validates Postle's framework. In seed.
