---
id: awh_jonides2001_overlapping_attention_wm
title: "Overlapping mechanisms of attention and spatial working memory"
authors:
  - "Awh, Edward"
  - "Jonides, John"
year: 2001
venue: "Trends in Cognitive Sciences"
doi: "10.1016/S1364-6613(00)01593-X"
arxiv: ""
url: "https://www.cell.com/trends/cognitive-sciences/abstract/S1364-6613(00)01593-X"
tags:
  - attention
  - visual-working-memory
  - spatial
  - rehearsal
  - shared-substrate
  - review
concepts:
  - top-down-feedback
  - bidirectional_hierarchical_feedback
  - coalition_resource_competition
related:
  - postle2006_wm_emergent
  - kiyonaga_egner2013_wm_internal_attention
  - awh2006_attention_wm
  - desimone_duncan1995_biased_competition
  - panichello_buschman2021_shared_mechanisms
  - gazzaley_nobre2012_topdown
  - foster2017_alpha_vwm
  - soto2008_automatic_attention_wm
  - vanede2019_gaze_internal_wm
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

# Overlapping mechanisms of attention and spatial working memory

## 1. Abstract

> "Spatial selective attention and spatial working memory have largely been studied in isolation. Studies of spatial attention have provided clear evidence that observers can bias visual processing towards specific locations, enabling faster and better processing of information at those locations than at unattended locations. We present evidence supporting the view that this process of visual selection is a key component of rehearsal in spatial working memory. Thus, although working memory has sometimes been depicted as a storage system that emerges 'downstream' of early sensory processing, current evidence suggests that spatial rehearsal recruits top-down processes that modulate the earliest stages of visual analysis." (Awh & Jonides 2001, *Trends in Cognitive Sciences* 5(3):119-126, abstract.)

## 2. Why this matters for us

Awh & Jonides 2001 is the *first major synthesis* that argues *attention IS rehearsal in spatial working memory* — there is no separate "visuospatial sketchpad" buffer; rehearsal is implemented by continuously directing spatial attention to the to-be-remembered location. For the user's program, this is the *foundational cognitive-psychology paper* that licenses the architectural commitment to shared substrate between attention and memory ([postle2006_wm_emergent](postle2006_wm_emergent.md) generalizes the framework five years later). The paper also establishes a methodologically clean prediction: if attention is rehearsal, then *requiring attention to shift elsewhere during the delay should degrade spatial WM*. The dual-task evidence that supports this prediction is the cognitive-psychology source of the user's architectural commitment that *unattended hubs cannot maintain their memory state* — they go effectively silent without continuous attention-driven refresh.

## 3. Key claims

1. *Spatial attention is the mechanism of rehearsal in spatial WM* — they share a common substrate, not merely overlap occasionally.
2. Maintaining a location in WM produces *measurable attentional facilitation* at that location (faster RTs and better discrimination for probes appearing at the remembered location).
3. Disrupting spatial attention (e.g., requiring shifts elsewhere) *degrades spatial WM*, demonstrating that attention is *necessary* for spatial WM maintenance.
4. Spatial rehearsal modulates *early visual cortex* (e.g., V1), not merely late decision stages — an "early selection" account.
5. fMRI shows *overlapping fronto-parietal* (FEF, IPS) activation for covert attention and spatial WM maintenance — the shared neural substrate.
6. Spatial WM is *dissociable* from object/verbal WM and recruits distinct rehearsal mechanisms (visual-spatial vs verbal-articulatory).
7. The paper *bridges Posner's spatial-cuing literature with Baddeley's WM model* — uniting two largely independent research programs.

## 4. Methods

This is a theoretical/integrative review. The argument structure has three legs. (i) *Behavioral evidence for the attention-rehearsal identity:* Awh and colleagues had developed a *probe-discrimination during the WM delay* paradigm where subjects maintain a spatial location in WM and concurrently discriminate brief probes at the remembered or non-remembered locations. The empirical prediction is *facilitation at the remembered location* — and Awh et al. (1998 *JEP:HPP*; 1999) showed exactly that. (ii) *Necessity evidence:* the paper integrates dual-task results where requiring covert orienting elsewhere during the delay produces *selective forgetting* — incompatible with spatial WM being a buffer downstream of attention. (iii) *Neural evidence:* fMRI work showing overlapping fronto-parietal (FEF, IPS) activation for spatial attention and spatial WM, and ERP work showing P1/N1 modulations for probes at remembered locations — implicating early visual cortex modulation rather than late decision-stage effects.

## 5. Results

Key empirical anchors consolidated in the review:

- **Probe discrimination at the memorized location** is faster/more accurate than at unattended locations — RT benefits ~20-40 ms; d' improvements supporting facilitation.
- **Requiring covert orienting to a non-memorized location during the delay produces selective forgetting** in spatial WM, demonstrating necessity of attention for storage.
- **BOLD in superior parietal lobule and frontal eye fields** is sustained during the WM delay at levels comparable to attention tasks, supporting shared substrate.
- **ERP P1/N1 to probes at the memorized location** are enhanced relative to unattended-location probes — early-visual-cortex modulation, not late decision.
- **Spatial WM does not impair concurrent verbal WM** (and vice versa), supporting domain separability between visuospatial and verbal stores.
- **Patient/lesion evidence:** parietal lesions disrupt *both* attention and spatial WM together (neglect patients show both attentional and spatial-WM deficits) — converging causal evidence for shared substrate.
- **Articulatory suppression abolishes verbal-WM rehearsal but spares spatial WM**, demonstrating the modality-specific nature of rehearsal mechanisms.

## 6. Critique / limitations

The "spatial attention = spatial rehearsal" identity has been substantially refined and partially contested.

- **Strong identity contested by Belopolsky & Theeuwes (2009):** maintaining a location in WM can *inhibit* saccades there, not facilitate them, under certain conditions — incompatible with a strict identity.
- **Theeuwes, Belopolsky & Olivers (2009)** argue WM-based attentional capture differs in important ways from voluntary spatial attention; the two are related but not identical.
- **Newer evidence:** WM rehearsal can persist when overt attention is drawn elsewhere (Hollingworth & Maxcey-Richard 2013), undermining strict identity.
- **Most cited paradigms use single-location WM**; multi-location rehearsal is hard to reconcile with single-focus attention — how does one *simultaneously* attend to 3 remembered locations?
- **The early-visual-cortex modulation evidence is mixed**; some studies fail to find retinotopic WM signals at low loads, complicating the early-selection claim.
- **Heavily dependent on the authors' own probe-discrimination paradigm** — generalizability to other VWM paradigms (delayed-estimation, change detection) is debated.
- **Doesn't address non-spatial features** or how object WM (color, shape) is rehearsed — the model is spatial-only.
- **Pre-dates activity-silent and alpha-band evidence** that complicates the "continuous attentional focus" assumption (Foster et al. 2017, [foster2017_alpha_vwm](foster2017_alpha_vwm.md); Stokes 2015, [stokes2015_activity_silent_wm](stokes2015_activity_silent_wm.md)).

## 7. Connection to our work

Awh & Jonides 2001 is the founding cognitive-psychology paper for the user's program-level commitment that *attention and memory share substrate*.

**Touchpoint 1: spatial attention IS spatial rehearsal — the architectural identity in the user's program.** The paper's central claim — spatial attention is the mechanism of rehearsal in spatial WM — has a direct architectural translation: the central self-attention substrate, when querying a spatial location in the grid-cell memory, *is* rehearsing that location's content. There is no separate "rehearsal mechanism" in the user's architecture; the attention computation over the memory state, at every step, *is* the rehearsal. This makes the user's architecture a *constructive instantiation* of the Awh-Jonides framework.

**Touchpoint 2: necessity of attention for storage — architecturally enforced by the update gate.** The Awh-Jonides finding that requiring attention to shift elsewhere degrades spatial WM is architecturally enforced in the user's models by the *attention-gated memory update*: content that does not win attention weight in the central self-attention does not get refreshed in the memory update, and degrades through gradual decay. The user's architecture therefore predicts the empirical phenomenon by construction: removing attention from a memory item produces forgetting, exactly as Awh-Jonides document.

**Touchpoint 3: early-cortex modulation — biological warrant for V1-paired shallow memory.** The early-visual-cortex modulation evidence (P1/N1 enhancement, V1 BOLD modulation during spatial WM rehearsal) is the biological warrant for the user's V1-paired shallow memory layer ($M_{fast}$ / $C^{(1)}$). The shallow memory, being paired with V1-equivalent features, should be the architectural locus of early-cortex-style rehearsal — and probing the user's $M_{fast}$ should show that its content modulates the early features in subsequent timesteps, recapitulating the empirical finding.

**Touchpoint 4: shared fronto-parietal substrate — central self-attention as the FEF/IPS analog.** The fMRI finding that FEF and IPS are *jointly* engaged for spatial attention and spatial WM is the biological warrant for the user's central self-attention substrate playing both roles. The FEF/IPS-equivalent in the user's architecture is the central self-attention layer of the Feedback Transformer; it operates simultaneously as the attention-allocator (deciding what gets queried) and as the WM-control (deciding what gets refreshed in memory). The architectural homology gives the user's design a clean biological mapping.

**Touchpoint 5: dual-task selective interference as an empirical prediction.** The Awh-Jonides framework predicts that *concurrent spatial attention demands* should disrupt the user's spatial WM specifically (not verbal/object WM). The dual-task signature is therefore an experimental probe for the user's models: training a model that has a "spatial WM" component (e.g., the grid-cell organization of $M_{fast}$) and then probing whether *attention-distractor* trials selectively degrade spatial recall while leaving non-spatial recall intact. If the user's models pass this test, they have reproduced the empirical signature of attention-rehearsal coupling.

**Touchpoint 6: bridging Posner attention and Baddeley WM — the user's program at large.** The Awh-Jonides synthesis bridges two largely independent research programs (Posner's spatial cuing and Baddeley's WM); the user's program inherits the synthesis by treating attention and WM as *the same architectural substrate*, with no architectural commitment to either Posner-style or Baddeley-style separateness. The user's program is therefore the modern computational synthesis of what Awh-Jonides articulated theoretically: one substrate (central self-attention), multiple functional roles (allocation, rehearsal, control).

**Touchpoint 7: the active-storage limit and the multi-item challenge.** The Awh-Jonides framework struggles with multi-item spatial WM (how does one attend to 3 locations simultaneously?). The user's architecture has a clean answer: the central self-attention is a softmax-normalized distribution over hubs/spatial positions, and multiple items can be held by *distributing* attention weight across them. The user's architecture therefore *generalizes* the Awh-Jonides framework from single-location to multi-location WM by treating attention as a distributed allocation rather than a single focus — a substantive extension that the original framework did not provide.

**Touchpoint 8: the foundational status for the user's program.** Awh-Jonides 2001 is the *earliest* cognitive-psychology paper that the user's program is in deep architectural dialogue with. The recurrent ViT's conditioning of attention on the previous memory state, PRISM v2's attention-modulated memory update, and the Feedback Transformer's role as both attention substrate and memory controller are all architectural instantiations of the Awh-Jonides framework. Citing this paper as the *theoretical foundation* of the shared-substrate program-level commitment is appropriate; the framework predates Postle 2006 by five years and is the more concrete spatial-WM-specific version of the broader emergent-property thesis.

## 8. Citations to follow

- [awh2006_attention_wm](awh2006_attention_wm.md) — the authors' follow-up reviewing interactions between attention and WM more broadly. In seed.
- `theeuwes_belopolsky_olivers2009_acta_psychologica` — interactions of attention and spatial WM; the most direct empirical challenge to strict identity. Not in seed.
- `belopolsky_theeuwes2009_inhibitory_wm_jephpp` — *JEP:HPP* — inhibitory effects of maintaining a location in WM; the strongest counterevidence to the facilitation prediction. Not in seed.
- [postle2006_wm_emergent](postle2006_wm_emergent.md) — the broader emergent-property view that generalizes the Awh-Jonides framework. In seed.
- `curtis_desposito2003_persistent_activity_pfc_tics` — *TiCS* — persistent activity in PFC during WM; the modern follow-up on the neural substrate. Not in seed.
- `ester_serences_awh2009_sustained_delay_visual` — *J Neurosci* — sustained delay activity in early visual cortex during spatial WM; the modern neural evidence. Not in seed.
- `jha2002_erp_visual_attention_spatial_wm_rehearsal` — *Cognitive Brain Research* — ERP evidence for visual attention during spatial WM rehearsal. Not in seed.
- `postle_awh_jonides_smith_desposito2004_neural_spatial_rehearsal` — *Cognitive Brain Research* — neural substrates of spatial rehearsal; the imaging follow-up. Not in seed.
- [gazzaley_nobre2012_topdown](gazzaley_nobre2012_topdown.md) — top-down modulation bridging attention and WM. In seed.
- [kiyonaga_egner2013_wm_internal_attention](kiyonaga_egner2013_wm_internal_attention.md) — "Working memory as internal attention"; the conceptual extension. In seed.
- [soto2008_automatic_attention_wm](soto2008_automatic_attention_wm.md) — the WM-to-attention guidance pathway (the complement direction to Awh-Jonides' attention-to-WM rehearsal). In seed.
- [foster2017_alpha_vwm](foster2017_alpha_vwm.md) — the modern alpha-band evidence for spatial WM coding; partial refinement of the continuous-attention assumption. In seed.
- [panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md) — the modern neural-mechanism demonstration of shared attention-WM substrate. In seed.
