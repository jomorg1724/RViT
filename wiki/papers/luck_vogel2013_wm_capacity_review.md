---
id: luck_vogel2013_wm_capacity_review
title: "Visual working memory capacity: from psychophysics and neurobiology to individual differences"
authors:
  - "Luck, Steven J."
  - "Vogel, Edward K."
year: 2013
venue: "Trends in Cognitive Sciences"
doi: "10.1016/j.tics.2013.06.006"
arxiv: ""
url: "https://doi.org/10.1016/j.tics.2013.06.006"
tags:
  - working-memory
  - review
  - human-neuroimaging
  - psychophysics
concepts:
  - working-memory-persistent-activity
  - feature-binding
related:
  - luck_vogel1997_wm_capacity
  - bays2024_wm_representation
  - awh2006_attention_wm
  - constantinidis2018_persistent_activity
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_34
status: full
depth: full
last_updated: "2026-05-14"
---

# Visual working memory capacity: from psychophysics and neurobiology to individual differences

## 1. Abstract

Visual working memory capacity is of great interest because it is *strongly correlated with overall cognitive ability*, can be understood at the level of neural circuits, and is easily measured. Recent studies have shown that capacity influences tasks ranging from saccade targeting to analogical reasoning. A debate has arisen over whether capacity is constrained by a *limited number of discrete representations* or by an *infinitely divisible resource*; the empirical evidence and neural-network models currently favor a discrete item limit. Capacity differs markedly across individuals and groups, and recent research indicates that some of these differences reflect true differences in storage capacity whereas others reflect variations in the ability to *use memory capacity efficiently*.

## 2. Why this matters for us

Luck & Vogel 2013 is the *modern update* of the 1997 capacity paper ([luck_vogel1997_wm_capacity](research_db/papers/luck_vogel1997_wm_capacity.md)), bringing the field 16 years forward with neurobiological substrates, individual differences, and the discrete-vs-continuous-resource debate. For the user's program, this review supplies the contemporary framing for WM-capacity as a constraint on architectural choices: PRISM's memory must respect the ~4-item capacity at the *behavioral* level even if its internal representations are continuous; the recurrent ViT's behavior must show capacity-limited performance under load. The review also establishes WM capacity as *correlated with general cognitive ability*, which motivates the broader user's program of building AI systems that match human-cognitive-capacity profiles.

## 3. Key claims

1. **WM capacity ≈ 4 items, replicated.** The 1997 finding is robust across many subsequent studies, with the 4-item limit holding across populations and paradigms.
2. **Capacity correlates with cognitive ability.** Visual WM capacity is *strongly correlated* with fluid intelligence, language comprehension, and academic achievement. This is one of the most replicable individual-differences findings in cognitive psychology.
3. **Discrete-slot vs continuous-resource debate.** Some accounts treat WM as 4 discrete slots; others treat it as a continuous resource that can be distributed across more items at lower precision. The 2013 review concludes that *both behavioral and neural evidence favor the discrete-slot model* — but the debate is ongoing.
4. **Neural correlates.** Contralateral delay activity (CDA) in EEG, sustained PFC and PPC fMRI activity, and single-unit persistent activity (Funahashi 1989; Constantinidis 2018) all show capacity-related signatures. The neural substrate for the 4-item limit is *partially identified*.
5. **Individual and group differences.** WM capacity varies markedly across individuals (range typically 2–6 items). Some differences reflect true *storage* capacity; others reflect *efficiency* of use (filtering distractors, etc.). The 2013 review highlights this dissociation.
6. **WM capacity influences diverse cognitive functions.** Beyond WM tasks proper, WM capacity correlates with performance on saccade-target-selection, analogical reasoning, language comprehension, and selective-attention tasks. The construct is broadly relevant.
7. **Capacity is malleable.** Some interventions (cognitive training, neurofeedback) can increase capacity; some pharmacological manipulations modulate it. The capacity is not a hardwired ceiling.

## 4. Methods

A narrative review covering 16 years of WM-capacity research after the 1997 founding paper. The authors synthesize:
- **Behavioral** evidence for the 4-item limit across paradigms.
- **Neural** correlates from EEG (CDA), fMRI, and single-unit recording.
- **Individual-differences** literature on capacity and cognitive ability.
- **Modeling** work on discrete-slot vs continuous-resource accounts.
- **Applied** literature on WM capacity in education, clinical conditions, training studies.

## 5. Results

The principal empirical claims the review consolidates:

- **K ≈ 4 across populations.** Capacity is consistent across age groups (developing in childhood, peaking in young adulthood, declining slightly in old age).
- **CDA scales with capacity.** Contralateral delay activity in EEG plateaus at the individual's K. The plateau is direct neural evidence of the capacity limit.
- **PFC and PPC fMRI activity track capacity.** BOLD activity in posterior parietal cortex and dlPFC scales with WM load up to the capacity limit, then plateaus.
- **Cognitive correlations.** Capacity correlates ~0.5–0.7 with fluid intelligence (Gf) measures. This is one of the strongest behavioral-cognitive correlations.
- **Distractor filtering.** Individuals with high WM capacity are better at filtering irrelevant items; some apparent capacity differences are actually filtering differences.
- **Trainability.** Cognitive-training programs (Cogmed, n-back) show modest increases in WM capacity, transferring partially to fluid-intelligence measures.

## 6. Critique / limitations

The discrete-vs-continuous debate is not fully resolved. Bays-and-colleagues continuous-resource models also have strong empirical support; the 2013 review's preference for discrete slots is one position in a contested debate. Subsequent work (Bays 2024, [bays2024_wm_representation](research_db/papers/bays2024_wm_representation.md)) presents the case for continuous resources.

The capacity-cognitive-ability correlation is *correlational*. Whether high capacity *causes* better cognitive performance, or whether both are caused by an underlying factor (e.g., general processing efficiency), is not directly tested.

The review focuses on *visual* WM. Verbal and auditory WM have different capacity profiles; the review doesn't address them.

The neural correlates are mostly *macroscopic* (BOLD, EEG). Single-unit-level mechanism of the 4-item limit is still being worked out. The Lundqvist counterpoint to Constantinidis 2018 ([constantinidis2018_persistent_activity](research_db/papers/constantinidis2018_persistent_activity.md)) suggests the neural substrate of "WM maintenance" may be more transient and sparse than the macroscopic signatures suggest.

The training-transfer literature is contested. Some studies find substantial transfer; others find specific training without transfer. The 2013 review's claim of trainability is consistent with the literature but stronger transfer claims are debated.

## 7. Connection to our work

This review supplies the contemporary framing for the user's program's WM commitments:

**Capacity as architectural constraint.** PRISM v1's recurrent memory state should be *capacity-limited* in a way that mimics the ~4-item human limit. Whether this is achieved by discrete slots in the model's internal representation or by continuous noise growing with load is an empirical question worth testing.

**Discrete vs continuous in the recurrent ViT.** The recurrent ViT's recurrent state is *continuous-valued* (network activations). The Luck-Vogel discrete-slot framework is the *behavioral target*; whether the underlying neural / network representation is discrete or continuous is the contested question Bays-and-Schneegans address.

**Capacity-cognitive-ability correlation as a future direction.** If WM capacity correlates with general cognitive ability in humans, models that improve WM capacity might also improve performance on broader cognitive tasks. The user's program could test this: train models on WM-heavy tasks, then measure performance on reasoning, language, and other tasks. This is an empirical research direction.

**Multi-hub system and capacity allocation.** The user's multi-hub system maintains multiple memory states across hubs. Whether the total capacity is the *sum* of hub capacities (each hub has its own ~4 slot) or shared across hubs (total ~4 slots regardless of hub count) is an architectural question. Luck-Vogel's empirical framing — capacity as a constraint at the system level — informs the choice.

**Distractor filtering as a target.** Luck-Vogel 2013 highlights that some capacity differences are actually distractor-filtering differences. The user's program's commitment to *gateable* feedback ([bidirectional_hierarchical_feedback](research_db/concepts/bidirectional_hierarchical_feedback.md)) is biologically warranted by this finding: the ability to filter (vs encode) is a key WM-capacity-related skill.

The recurrent ViT paper cites Luck & Vogel 2013 in its bibliography (ref [34]). Future manuscripts that engage with WM capacity should cite both the 1997 and 2013 papers.

## 8. Citations to follow

- `luck_vogel1997_wm_capacity` — the 1997 founding paper. In seed, full depth.
- `bays2024_wm_representation` — modern continuous-resource framing. In seed, full depth.
- `awh2006_attention_wm` — attention-WM interactions. In seed, full depth.
- `constantinidis2018_persistent_activity` — neural substrate of WM. In seed, full depth.
- `vogel_machizawa2004_neural_capacity_individual` — CDA scales with capacity. Not in seed.
- `cowan2001_magical_number_4` — Cowan's "4 items" review. Not in seed.
- `engle2002_wm_capacity_attention` — WM-attention link via individual differences. Not in seed.
- `bays_husain2008_dynamic_shifts_visual_wm` — Bays & Husain's continuous-resource paper. Not in seed.
