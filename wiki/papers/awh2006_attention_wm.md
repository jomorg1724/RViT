---
id: awh2006_attention_wm
title: "Interactions between attention and working memory"
authors:
  - "Awh, Edward"
  - "Vogel, Edward K."
  - "Oh, Sei-Hwan"
year: 2006
venue: "Neuroscience"
doi: "10.1016/j.neuroscience.2005.08.023"
arxiv: ""
url: "https://doi.org/10.1016/j.neuroscience.2005.08.023"
tags:
  - visual-attention
  - working-memory
  - review
concepts:
  - attentional-template
  - working-memory-persistent-activity
related:
  - gazzaley_nobre2012_topdown
  - panichello_buschman2021_shared_mechanisms
  - constantinidis2018_persistent_activity
  - desimone_duncan1995_biased_competition
  - olivers2011_wm_states_attention
  - bays2024_wm_representation
  - kiyonaga_egner2013_wm_internal_attention
  - oberauer2002_access_wm
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_12
status: full
depth: full
last_updated: "2026-05-16"
---

# Interactions between attention and working memory

## 1. Abstract

Studies of attention and working memory address the fundamental limits in our ability to encode and maintain behaviorally relevant information — processes that are critical for goal-driven processing. Awh, Vogel & Oh review the current understanding of the interactions between these processes, with a focus on how each construct encompasses a *variety of dissociable phenomena*. Attention facilitates target processing during both *perceptual* and *post-perceptual* stages of processing, and functionally dissociated processes have been implicated in the maintenance of *different kinds of information* in working memory. Thus, although it is clear that these processes are closely intertwined, the nature of these interactions depends upon the *specific variety* of attention or working memory that is considered.

## 2. Why this matters for us

Awh, Vogel & Oh 2006 is the canonical reference for the *attention-WM link* that grounds the recurrent ViT's central architectural metaphor: the recurrent memory state is functionally analogous to working memory, and its modulation of self-attention is functionally analogous to WM-template-guided attention. The paper is the load-bearing citation for treating these two processes as *one shared substrate* rather than as separate cognitive faculties. The recurrent ViT paper (2502.10955) explicitly takes this position — its single recurrent state serves both attention-guidance and WM-maintenance roles. Awh, Vogel & Oh provide the cognitive-science precedent.

## 3. Key claims

1. **Attention and WM are tightly coupled but not identical.** They are *dissociable* — there exist forms of attention without WM and forms of WM without attention — but they are *intertwined* in normal cognition.
2. **Attention is *multiplexed*.** It encompasses at least perceptual selection (e.g., spatial attention), postperceptual selection (e.g., response selection), and selection-from-memory (e.g., retrieving an item from WM).
3. **WM is also multiplexed.** It encompasses verbal-phonological, visuospatial, and central-executive components (the Baddeley framework) plus more recent fractionations (e.g., separate spatial WM, feature WM, object WM).
4. **Attention can *protect* WM content.** Holding a stimulus in WM is helped by attending to its features during the maintenance period; distractor attention reduces WM precision.
5. **WM can *guide* attention.** A held-in-WM template biases attentional capture toward template-matching items, even when those items are not the current task target ("memory-guided attention").
6. **Capacity limits.** Both attention and WM have capacity limits (roughly 4 items for visual WM, roughly 3–5 for tracking); the limits *interact* (attending to N items reduces the number of items that can be held in WM).
7. **Neural substrates overlap.** Prefrontal cortex, parietal cortex, and feature-selective sensory cortex are all engaged by both attention and WM. The overlap supports the shared-substrate view.

## 4. Methods

A narrative review of behavioral psychophysics, electrophysiology, and neuroimaging on attention-WM interactions. The authors synthesize work from many labs (Awh's own, Vogel's, Oh's, Olivers's, Cowan's, others) into a unified framework that emphasizes the *multiplexed* nature of both constructs.

The review's principal argument: claims about "attention" and "WM" must specify *which variety* of attention or WM. Generic claims that conflate the varieties are unproductive; specific claims about feature attention modulating object WM are tractable.

## 5. Results

The principal empirical claims:

- **Memory-guided attention.** Items matching a WM template capture attention even when the WM content is task-irrelevant (Soto, Heinke, Humphreys 2005). This is the WM → attention direction.
- **Attention-protects-WM.** Holding multiple items in WM is more robust when sustained attention is directed to the WM content; distractor-rich environments reduce WM precision (Awh and colleagues' original studies). This is the attention → WM direction.
- **Capacity interaction.** Attention to N visual items reduces the number of additional items that can be held in WM, suggesting the two share a limited pool (Cowan's "embedded-processes" model). Capacity is a *shared* resource.
- **Neural overlap.** PFC, parietal cortex, and feature-selective extrastriate cortex are engaged by both attention and WM tasks in fMRI and single-unit recordings.
- **Dissociations exist.** Some WM tasks proceed normally with reduced attention (rapid encoding); some attention tasks proceed normally with cleared WM. The two are not identical.
- **Goal-driven processing depends on both.** Holding task goals in mind (WM) plus selecting goal-relevant stimuli (attention) is the unified mechanism for goal-driven cognition.

## 6. Critique / limitations

The framework is *descriptive*. It catalogs the varieties of attention and WM and their interactions but doesn't provide a unified computational mechanism. Subsequent work (Gazzaley & Nobre 2012, [gazzaley_nobre2012_topdown](research_db/papers/gazzaley_nobre2012_topdown.md); Panichello & Buschman 2021, [panichello_buschman2021_shared_mechanisms](research_db/papers/panichello_buschman2021_shared_mechanisms.md)) has moved toward unified mechanistic accounts.

The "dissociation" claims rest on *behavioral* and *neural correlations*. Direct causal evidence (perturbing one and measuring the other) is sparse. The dissociations may be due to dissociable *parameters* of the same underlying mechanism rather than dissociable mechanisms.

The framework is *cortex-centric*. Subcortical contributions (basal ganglia gating of WM, thalamic gating of attention) are mentioned but not centrally developed.

The 2006 paper predates much of the modern empirical work — particularly the Panichello-Buschman 2021 demonstration that PFC implements *shared* control mechanisms for attention and WM. The 2006 framework is a precursor to but not as developed as the modern shared-substrate account.

The 2006 framework doesn't engage with *predictive-coding* interpretations. The Friston-tradition view that attention is precision-weighting and WM is a slow generative-model state is consistent with Awh-Vogel-Oh's framework but is not addressed in this paper.

## 7. Connection to our work

This paper is the canonical *cognitive-science* precedent for the user's program's commitment to a shared attention-WM substrate:

**The recurrent ViT's recurrent state as a shared attention-WM substrate.** The recurrent ViT (2502.10955) maintains a single recurrent memory state $H^{(t)}$ that serves both attention-guidance (via the Feedback Transformer's feedback projection) and WM-maintenance (across timesteps). Awh-Vogel-Oh's framework — attention and WM as overlapping but multiplexed — is the cognitive-science support for this unified architectural commitment.

**Memory-guided attention as the cue-condition mechanism.** The recurrent ViT's cue mechanism (cue token presented before the target) sets up a memory state that subsequently *guides attention* to the cued location. This is exactly the "WM-template guides attention" phenomenon Awh-Vogel-Oh describe.

**Attention-protects-WM as a future test.** The reverse direction — attention to WM contents protects them from distractors — would be a test of whether the recurrent ViT's recurrent state behaves like real WM. The user's program could empirically test this by training the network on distractor-rich variants of the change-detection task.

**Shared capacity.** Awh-Vogel-Oh's "shared capacity" between attention and WM is a key empirical prediction for any unified-substrate architecture. The recurrent ViT's recurrent state has a fixed dimensionality; whether this fixed capacity is shared between attention-guidance and WM-maintenance can be empirically tested by varying the number of items the network must track.

**Multi-hub system framing.** In the user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)), one of the hubs is dedicated to MSI / context maintenance (the analog of WM); the central self-attention substrate handles attention. Awh-Vogel-Oh's argument that attention and WM share a substrate is the cognitive-science version of the user's claim that hubs interact through a shared self-attention map.

**Multiplexed varieties.** Awh-Vogel-Oh's emphasis on the *varieties* of attention and WM warns that the user's program should be specific about which kind of each it commits to. The recurrent ViT's "attention" is *covert spatial attention* (as in Posner cuing); its "WM" is *visual working memory* for a single object's position and feature. Specifying the variety lets the architectural commitment be empirically tested.

The recurrent ViT paper cites Awh-Vogel-Oh in its bibliography (ref [12]). Future manuscripts that elaborate the attention-WM relationship should cite this paper alongside the more recent Panichello-Buschman 2021 work.

## 8. Citations to follow

- `gazzaley_nobre2012_topdown` — top-down modulation bridging attention and WM. In seed, full depth.
- `panichello_buschman2021_shared_mechanisms` — modern shared-substrate account. In seed, full depth.
- `kiyonaga_egner2013_wm_internal_attention` — WM as internal attention. In seed.
- `olivers2011_wm_states_attention` — WM states guiding attention. In seed.
- `bays2024_wm_representation` — modern WM-representation review. In seed.
- `desimone_duncan1995_biased_competition` — biased competition (attention component). In seed, full depth.
- `constantinidis2018_persistent_activity` — WM persistent activity. In seed, full depth.
- `oberauer2002_access_wm` — Oberauer's access-WM model. In seed.
