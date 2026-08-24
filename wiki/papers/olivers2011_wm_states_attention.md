---
id: olivers2011_wm_states_attention
title: "Different states in visual working memory: when it guides attention and when it does not"
authors:
  - "Olivers, Christian N. L."
  - "Peters, Judith"
  - "Houtkamp, Roos"
  - "Roelfsema, Pieter R."
year: 2011
venue: "Trends in Cognitive Sciences"
doi: "10.1016/j.tics.2011.05.004"
arxiv: ""
url: "https://doi.org/10.1016/j.tics.2011.05.004"
tags:
  - working-memory
  - visual-attention
  - review
concepts:
  - attentional-template
  - working-memory-persistent-activity
related:
  - awh2006_attention_wm
  - kiyonaga_egner2013_wm_internal_attention
  - vanmoorselaar2014_template_competition
  - panichello_buschman2021_shared_mechanisms
  - oberauer2002_access_wm
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_37
status: full
depth: full
last_updated: "2026-05-16"
---

# Different states in visual working memory: when it guides attention and when it does not

## 1. Abstract

Recent studies have revealed a strong relationship between visual working memory and selective attention, such that attention is biased by what is currently on our mind. However, *other data show that not all memorized items influence the deployment of attention*, thus calling for a *distinction within working memory*: whereas **active memory items** function as an *attentional template* and directly affect perception, other, **accessory items** do not. Olivers et al. review recent evidence that items *compete for the status of "attentional template"* — which contains only **one** object at a time. Neurophysiological results provide insight into these different memory states by revealing a more intricate organization of working memory than was previously thought.

## 2. Why this matters for us

Olivers et al. 2011 is the canonical paper introducing the *active-accessory distinction* in WM: only one (or a small number of) items is in an "active" state where it directly biases attention; the rest are in an "accessory" state where they're maintained but don't drive attention. This is a substantive architectural commitment that constrains how the user's program implements the WM-attention interface. The recurrent ViT's recurrent state likely implements this implicitly — only one item is "active" (the cued location) at a time even though multiple stimuli are present. The Olivers framework is the cognitive-science vocabulary for what the model architecturally does.

## 3. Key claims

1. **WM has multiple states.** Not all WM items are equivalent. At least two states must be distinguished: an *active* state (one item) and an *accessory* state (multiple items, weaker representation).
2. **Only active items capture attention.** Accessory items are *maintained* (recallable, behavior-relevant later) but do *not* bias visual attention. The capture effect Soto et al. 2005 found applies specifically to the active item.
3. **Items compete for the active slot.** The active state contains at most one item at a time. Items can swap into the active state, but only one is active at any moment. This is a *capacity-of-1* for the active state.
4. **The two states have different neural signatures.** Active items show stronger PFC activity, more sustained sensory-cortex signatures, and contralateral delay activity scaling. Accessory items show weaker, more diffuse activity.
5. **Both states are still "in WM"** — both items can be recalled, used for behavior, etc. The distinction is about *online influence on perception*, not about whether the item is stored.
6. **Active-accessory transitions are dynamic.** Items can swap between active and accessory states depending on task demands. The "active item" is determined by the current attentional priority.
7. **Implications for WM-attention models.** Any model that treats all WM contents as having equal effect on attention is wrong. The active-vs-accessory distinction must be built into models.

## 4. Methods

A narrative review of behavioral and neurophysiological evidence for the multi-state framework. The Olivers lab and others' contributions are synthesized into the active-accessory distinction.

Key empirical evidence:
- **Attention-capture studies** showing that holding multiple items in WM does *not* increase the attention-capture effect proportionally — only the active item captures attention.
- **EEG (CDA) studies** showing CDA amplitude that depends on the active item, not the total WM load.
- **fMRI** showing distinct activation patterns for active vs accessory items.
- **Behavior** showing that only the active item produces involuntary attention-capture effects.

## 5. Results

The principal empirical claims the review consolidates:

- **Active item capture-effect.** Holding one item in WM (the active item) produces attention capture for matching display items.
- **Accessory items do not capture.** When two or more items are held but only one is task-relevant, only the relevant item produces capture. The "irrelevant" items are accessory and don't drive attention.
- **The active state is plastic.** Cues that signal which item to attend to next produce a swap into the active state, with corresponding shifts in attention-capture and neural activity.
- **CDA amplitude tracks active items.** EEG CDA reflects active rather than total WM load.
- **Verbal-encoding studies.** Items maintained via verbal rehearsal (rather than visual encoding) are less likely to enter the active state — the active state may be specific to one encoding format.

## 6. Critique / limitations

The "capacity-of-1" for the active state is a strong claim. Subsequent work (Beck et al. 2018; van Moorselaar et al. 2014) has shown that under certain conditions, multiple items can be in the active state simultaneously — though with reduced effect per item. The active-state capacity may be variable rather than strictly 1.

The active-accessory distinction is presented as binary. A continuous-state framing — items vary in their "activation level" with continuous attention-effect — may be more accurate. The Bays-Schneegans tradition would favor this.

The framework focuses on attention-capture. Whether the active-accessory distinction generalizes to other WM-attention interactions (e.g., WM-guided search, WM-guided motor planning) is less developed.

The neural-substrate claims are correlational. Direct causal manipulation (e.g., PFC inactivation while in active vs accessory state) would more decisively support the distinction.

The framework predates the more recent shared-substrate work (Panichello & Buschman 2021). The active-accessory distinction may map onto Panichello-Buschman's "output subspace" (active state) vs "stored subspace" (accessory state) framing, but the connection isn't made in the 2011 paper.

## 7. Connection to our work

This paper supplies the *operational* framing for the recurrent ViT's recurrent-state dynamics:

**The cued location as the active item.** The recurrent ViT's cue mechanism establishes the cued location as the "active" item in the model's recurrent state. The cued location dominates the attention map (architectural analog of the active item capturing attention); the other locations are maintained but don't drive attention (accessory items). The Olivers framework is the cognitive-science vocabulary for this architectural pattern.

**Capacity-of-1 for attention.** The recurrent ViT's softmax attention map is dominated by *one* peak (the most active location). This is the architectural form of "only one item is active at a time." Models that produce multi-peak attention maps under WM load (e.g., when multiple items are equally task-relevant) might be testing the boundaries of the capacity-of-1 framing.

**Active-accessory swap as cue-driven attention shifting.** In the recurrent ViT, the cue at time $t$ shifts the recurrent state to make the cued location the active item. This is the architectural form of "the active state is plastic." Multi-cue trials (where the cue changes mid-trial) would exercise this plasticity.

**Multi-hub system implications.** The user's multi-hub system maintains multiple memory states across hubs. The Olivers framework suggests that at any moment, only *one* hub's contribution dominates the central self-attention substrate — the rest are in an accessory role. The capacity-of-1 for the active hub is the architectural commitment matching Olivers's empirical pattern.

**Differential representational geometry.** Panichello & Buschman 2021 ([panichello_buschman2021_shared_mechanisms](research_db/papers/panichello_buschman2021_shared_mechanisms.md)) shows that PFC items in the "output subspace" guide behavior while items in their own "memory subspace" don't. This is the modern primate-data confirmation of the Olivers active-accessory framework: the output subspace is the architectural analog of "active state."

The recurrent ViT paper cites Olivers et al. 2011 in its bibliography (ref [37]). Future manuscripts that model attention-WM interactions should cite this paper for the active-accessory distinction.

## 8. Citations to follow

- `awh2006_attention_wm` — broader attention-WM framework. In seed, full depth.
- `kiyonaga_egner2013_wm_internal_attention` — unified-substrate theory. In seed, full depth.
- `vanmoorselaar2014_template_competition` — multi-template competition. In seed.
- `panichello_buschman2021_shared_mechanisms` — modern subspace analysis. In seed, full depth.
- `soto_heinke_humphreys2005_memory_attention_capture` — foundational WM-capture paper. Not in seed.
- `carlisle_arita_pardo_woodman2011_attentional_templates` — attentional templates in WM. In seed.
- `bahle_beck_hollingworth2018_wm_attention_architecture` — WM-attention architecture. In seed.
- `oberauer2002_access_wm` — Oberauer's access-WM model. In seed.
