---
id: luck_vogel1997_wm_capacity
title: "The capacity of visual working memory for features and conjunctions"
authors:
  - "Luck, Steven J."
  - "Vogel, Edward K."
year: 1997
venue: "Nature"
doi: "10.1038/36846"
arxiv: ""
url: "https://doi.org/10.1038/36846"
tags:
  - working-memory
  - psychophysics
concepts:
  - working-memory-persistent-activity
  - feature-binding
related:
  - luck_vogel2013_wm_capacity_review
  - bays2024_wm_representation
  - awh2006_attention_wm
  - wheeler_treisman2002_binding
  - treisman_gelade1980_feature_integration
  - panichello_buschman2021_shared_mechanisms
  - pertzov_husain2014_location_wm
  - schneegans_bays2017_feature_binding_wm
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_33
status: full
depth: full
last_updated: "2026-05-16"
---

# The capacity of visual working memory for features and conjunctions

## 1. Abstract

Short-term memory storage can be divided into separate subsystems for verbal information and visual information. Although the verbal storage system has been well characterized, the storage capacity of visual working memory had not yet been established for simple, suprathreshold features or for *conjunctions* of features. Luck & Vogel demonstrate that it is possible to retain information about only **four** colours or orientations in visual working memory at one time. However, it is also possible to retain *both* the colour and the orientation of four objects, indicating that visual working memory stores *integrated objects* rather than individual features. Indeed, objects defined by a *conjunction of four features* can be retained in working memory just as well as single-feature objects, allowing *sixteen* individual features to be retained when distributed across four objects. The capacity of visual working memory must therefore be understood in terms of integrated objects rather than individual features — placing significant constraints on cognitive and neurobiological models of the temporary storage of visual information.

## 2. Why this matters for us

Luck & Vogel 1997 is the *founding* empirical paper of the visual-WM-capacity tradition. The "four-item capacity limit" is one of the most cited findings in cognitive psychology, and the *object-based* (not feature-based) capacity is a substantive theoretical commitment that constrains any architectural model of visual WM. For the user's program, this paper supplies the *capacity-limited* empirical signature that PRISM v1's recurrent memory should reproduce: a fixed-dimensional memory state that maintains a small number of integrated object representations rather than an unbounded feature buffer. The recurrent ViT's task involves tracking ≤4 distinct stimuli, well within the Luck-Vogel limit; PRISM's memory architecture is implicitly bounded in a comparable way.

## 3. Key claims

1. **Visual WM has a fixed capacity of ~4 items.** Whether the items are single colors, single orientations, or single shapes, the capacity is approximately 4 (with individual variation between 3 and 5).
2. **Capacity is for *integrated objects*, not features.** When the 4 items each have 4 features (e.g., color + orientation + size + shape), the total *feature* count is 16 — but the 4-item capacity is preserved. This is the strongest finding of the paper.
3. **The capacity limit is at the level of object slots, not feature storage.** This forces theoretical models of visual WM to commit to *object-binding*: each WM slot holds a bound representation of one object's complete feature set.
4. **The capacity is robust across feature dimensions.** Orientation, color, conjunction tasks all yield approximately the same 4-item limit.
5. **The capacity is robust across timescales.** Retention intervals from 100 ms to several seconds give the same capacity, indicating that the limit is not in the rate of encoding but in the storage capacity itself.
6. **The capacity is robust to passive vs active maintenance.** Whether subjects passively viewed or actively rehearsed, the 4-item limit applies.
7. **Implications for the binding problem.** The object-based capacity solves part of the binding problem: the cortex must integrate features into object representations *before* storing them in WM, and the WM slots already contain bound representations.

## 4. Methods

**Task.** Sequential change-detection task. Subjects briefly viewed a memory array (1–12 items, each a simple visual feature: color, orientation, size, conjunction). After a delay (typically 1 s), a test array appeared. Subjects judged whether the test array was identical to the memory array or whether one item had changed.

**Manipulation.** Set size (number of items in the memory array) varied from 1 to 12. The slope of accuracy vs set size gives the capacity estimate: items above the capacity limit can't be remembered reliably, so accuracy drops.

**Conjunction condition.** In the critical experiment, each memory-array item had multiple features (e.g., colored oriented bars). The number of features per item was varied to test whether capacity is limited by features or by objects.

**Capacity estimation.** Cowan's *K* (= set size × accuracy − 0.5 × set size × (1 − accuracy)) gives the estimated number of items in WM. K plateaus around 4 across feature dimensions and conjunction tasks.

## 5. Results

The principal quantitative findings:

- **Single-feature capacity:** ~4 items for color, ~4 for orientation, ~3.5 for shape. The capacity is feature-dimension-robust.
- **Conjunction capacity:** ~4 *objects* even when each object has up to 4 features. The 16-feature total exceeds the single-feature capacity, but the 4-object structure is preserved.
- **K-value plateaus at ~4 across set sizes ≥4.** Above the capacity, additional items cannot be added; below it, capacity scales with set size.
- **Individual variation.** Some subjects show K of ~3; others ~5. Mean is ~4; range is 2–6.
- **Robustness.** The 4-item limit is stable across multiple paradigms, including ones with explicit feature-binding manipulations.

## 6. Critique / limitations

The framework assumes *discrete slots*. Subsequent work (Bays and colleagues; see [bays2024_wm_representation](research_db/papers/bays2024_wm_representation.md)) argues that WM is *continuous* rather than discrete — capacity is a limited *resource* that can be allocated more or less precisely across items. Whether the 4-item limit is discrete or continuous is a major debate.

The "4-item" limit is for *single-modality* visual stimuli. Auditory-visual or multi-modal stimuli may have different limits. The framework is visual-specific.

The capacity measurement assumes the WM content is *intact* before the response. If items decay or interfere during the retention interval, the K measurement underestimates initial capacity. The "capacity" might be different at different points in the trial.

The framework treats objects as binary (encoded or not). Subsequent work has emphasized that WM precision varies continuously — items can be more or less faithfully maintained, not just "in" or "out" of WM. The Bays-Schneegans-Ma-Brady 2024 review covers this more fully.

The 1997 paper doesn't engage with the *neural mechanism* of WM. Subsequent single-unit work (Funahashi, Goldman-Rakic, Constantinidis) and Panichello-Buschman 2021 ([panichello_buschman2021_shared_mechanisms](research_db/papers/panichello_buschman2021_shared_mechanisms.md)) supplies the neural substrate; the 1997 paper is purely psychophysical.

## 7. Connection to our work

This paper supplies the *empirical capacity constraint* the user's program's WM analog must satisfy:

**PRISM's recurrent memory as the ~4-item WM substrate.** PRISM v1's recurrent memory state has fixed dimensionality; in the task it's used for (change-detection with ≤4 stimuli per trial), it operates within the Luck-Vogel capacity. This is empirically realistic, not unrealistic.

**Object-binding in the recurrent ViT.** The recurrent ViT's recurrent state must implicitly bind features (color, location, identity) into integrated object representations to perform the change-detection task. The Luck-Vogel finding that humans store *bound objects* (not free features) is the empirical pattern the model should reproduce. Whether the recurrent ViT's internal representations are object-bound (vs feature-distributed) is an interesting empirical question for future work.

**Capacity in the multi-hub system.** The user's multi-hub multi-objective system maintains multiple memory states across hubs. Whether the total system has a Luck-Vogel-style capacity limit, and whether the limit scales with the number of hubs vs is shared across them, is an architectural question. PRISM v2's slow + fast memory might collectively maintain more items than either alone, but the *bound-object capacity* may still be bounded.

**Discrete vs continuous capacity.** The user's program is currently neutral on this debate. The recurrent ViT's continuous memory state suggests continuous capacity; the Luck-Vogel discrete 4-item story suggests discrete slots. Future analysis of the model's representational geometry could discriminate between these.

**The feature-binding problem.** PRISM and the recurrent ViT implicitly bind features. The Luck-Vogel object-based capacity is the empirical pattern this binding should produce. The user's program inherits the binding problem from the broader cognitive-science literature; Luck-Vogel 1997 is the foundational binding-in-WM citation.

The recurrent ViT paper cites Luck & Vogel 1997 in its bibliography (ref [33]). Future manuscripts that engage with WM capacity should cite this paper.

## 8. Citations to follow

- `luck_vogel2013_wm_capacity_review` — modern update. In seed, full depth.
- `bays2024_wm_representation` — continuous-resource alternative. In seed, full depth.
- `wheeler_treisman2002_binding` — feature binding in WM. In seed.
- `treisman_gelade1980_feature_integration` — FIT, the classical theory of binding. In seed.
- `awh2006_attention_wm` — attention-WM interactions. In seed, full depth.
- `vogel_machizawa2004_neural_capacity_individual` — neural correlate of WM capacity. Not in seed.
- `cowan2001_magical_number_4` — Cowan's "4 items" review. Not in seed.
- `pertzov_husain2014_location_wm` — location priority in WM. In seed.
- `schneegans_bays2017_feature_binding_wm` — binding architecture in WM. In seed.
