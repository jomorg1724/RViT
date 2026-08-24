---
id: bahle2018_wm_attention_architecture
title: "The architecture of interaction between visual working memory and visual attention"
authors:
  - "Bahle, Brett"
  - "Beck, Valerie M."
  - "Hollingworth, Andrew"
year: 2018
venue: "Journal of Experimental Psychology: Human Perception and Performance"
doi: "10.1037/xhp0000509"
arxiv: ""
url: "https://doi.org/10.1037/xhp0000509"
tags:
  - working-memory
  - visual-attention
  - psychophysics
  - change-detection
concepts:
  - attentional-template
  - working-memory-persistent-activity
  - feature-binding
  - top-down-feedback
related:
  - kiyonaga_egner2013_wm_internal_attention
  - olivers2011_wm_states_attention
  - vanmoorselaar2014_template_competition
  - carlisle2011_attentional_templates
  - awh2006_attention_wm
  - gazzaley_nobre2012_topdown
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_77
status: full
depth: full
last_updated: "2026-05-14"
---

# The architecture of interaction between visual working memory and visual attention

## 1. Abstract

A central question in the study of memory-guided attention concerns the *architecture* of the interaction between visual working memory (VWM) and visual attention: when multiple items are concurrently held in VWM, can more than one of those items simultaneously guide perceptual selection, or is only one item — the active "search template" — given priority while the others are held in a passive, accessory state? Bahle, Beck, and Hollingworth contrast two hypotheses. The **single-item template (SIT)** hypothesis holds that only one VWM representation can actively bias attention at any moment; other items in VWM are maintained in an accessory state that does not guide attention. The **multiple-item template (MIT)** hypothesis holds that multiple items in VWM can simultaneously bias attention, so all maintained items influence perceptual selection. Across five experiments employing abstract search arrays and natural scenes, with reaction-time and eye-movement dependent measures, and varying both memory and search dimensions, the authors find that a distractor matching a *secondary* item in VWM (i.e., an item held for a later memory test, not the current search target) consistently captures attention. The result generalizes across stimulus dimensions, search task types, and dependent measures. Bahle et al. conclude that VWM is structured such that *multiple* items can simultaneously serve as templates for attentional guidance, providing strong support for the MIT architecture and against the single-template view.

## 2. Why this matters for us

This paper is the empirical anchor for the *architecture* of the VWM–attention interface. Kiyonaga & Egner 2013 ([kiyonaga_egner2013_wm_internal_attention](research_db/papers/kiyonaga_egner2013_wm_internal_attention.md)) gives the theoretical framing that "WM is internal attention"; Bahle et al. give the experimental answer to the architectural question that follows immediately from it — *how many* items in WM can act as attention templates at once. The MIT answer is the cognitive-science counterpart of the architectural commitment that the recurrent ViT's recurrent state $H^{(t)}$ is a *distributed*, multi-content substrate that simultaneously biases attention toward multiple maintained features rather than serializing through a single dominant template. For the user's program, this is the behavioral evidence that the shared attention–WM substrate is wide enough to host concurrent templates.

## 3. Key claims

1. **Multiple items in VWM can simultaneously guide attention.** Distractors matching a *secondary* (non-search-target) VWM item capture attention, demonstrating that the secondary item is not stored in an attention-inert accessory state.
2. **The single-item template hypothesis is rejected.** Across five experiments, evidence for MIT-style multi-template guidance is consistent; SIT predictions of zero secondary-item capture are violated.
3. **The result generalizes across stimulus dimensions.** Capture occurs whether the memory and search dimensions are color, shape, or other feature dimensions — it is not an artifact of a single feature space.
4. **The result generalizes across dependent measures.** Capture appears in both manual reaction-time costs and oculomotor measures (first-saccade direction, fixation latency), so it is not a strategic late-stage effect.
5. **The result generalizes across search-task types.** Capture is observed in abstract search arrays and in naturalistic scene search, ruling out a paradigm-specific explanation.
6. **VWM has a multi-template architecture.** The VWM-attention interface is not bottlenecked at one active item; it admits parallel guidance from multiple maintained representations.
7. **The "accessory state" account of secondary WM items needs revision.** Olivers et al. (2011)'s distinction between an active template and an accessory state is at minimum weaker than originally proposed: secondary items continue to influence attention, just perhaps with reduced weight.

## 4. Methods

The paper reports five experiments using a *dual-task* paradigm that combines a VWM load with a visual search task. The basic structure of each trial is: (i) encode one or two items into VWM (the memory items); (ii) perform a visual search task in which one of the memory items is the designated current-trial template (the *primary* memory item) and the other is merely held for a later memory test (the *secondary* memory item); (iii) report the search target's features or location; (iv) take a delayed memory test on one of the items.

The critical manipulation is whether a *distractor* in the search display matches the secondary memory item. If only the primary template guides attention (SIT), a secondary-matching distractor should produce no capture (no reaction-time or oculomotor cost). If multiple memory items guide attention (MIT), the secondary-matching distractor should capture attention.

Across experiments, the authors vary:
- **Memory dimension**: which feature (color, shape, orientation, etc.) is held in VWM.
- **Search-task structure**: abstract arrays of geometric items vs. naturalistic scene search.
- **Dependent measures**: manual reaction time, accuracy, first-saccade direction, saccade latency, fixation dwell.
- **Set size and number of memory items**: typically one primary and one secondary, with control conditions in which the secondary is removed.

The factorial design isolates the secondary-match capture effect from confounds with the primary template, with display layout, and with item-level salience.

## 5. Results

The principal quantitative pattern, reported consistently across all five experiments:

- **Reaction-time capture by secondary-matching distractors** is reliable and significantly above zero. Manual search RTs are slowed when one distractor matches the secondary VWM item relative to a matched no-secondary-match baseline; the magnitude is on the order of 20–60 ms in the abstract-search experiments.
- **Oculomotor capture by secondary-matching distractors** is reliable: first saccades are more often directed to the secondary-matching distractor than chance, and fixation latencies on secondary-matching distractors are elevated.
- **The effect is smaller than the primary-template effect but is robust.** Primary-template-matching items produce larger capture (the strongest attention-bias signal), but secondary-matching distractors produce a clear non-zero capture signal — exactly the qualitative pattern MIT predicts and SIT forbids.
- **The effect is preserved in naturalistic scene search.** Capture by the secondary-matching item occurs even when search is in a complex natural image, supporting ecological validity.
- **Memory accuracy on the delayed test is high for both primary and secondary items**, ruling out the alternative explanation that the secondary item was dropped from VWM during search.

Bahle et al. take the totality of these findings as decisive against the SIT and in favor of the MIT architecture.

## 6. Critique / limitations

The strongest critique comes from the *competition for template status* literature (van Moorselaar, Theeuwes, Olivers 2014; [vanmoorselaar2014_template_competition](research_db/papers/vanmoorselaar2014_template_competition.md)). van Moorselaar et al. argue that the *number* of items that can guide attention is bounded — perhaps as low as one when the items are sufficiently complex or when the VWM load approaches its capacity. Bahle et al.'s evidence for multi-template guidance is obtained with two memory items; whether the conclusion scales to three, four, or more items is left open. The two-item case is the *easiest* one for MIT; it does not establish that VWM in general is fully parallel for attention guidance.

The "capture" effects are *small* relative to the primary-template effect. A reasonable critic could argue that the secondary item is in a *weaker* but still partly attention-active state — a refinement of Olivers et al. (2011)'s accessory state, not a refutation of it. The architectural binary (SIT vs MIT) may be too coarse.

The paper does not directly test the *capacity limit* of multi-template guidance. If MIT is true but only up to k templates, the experiments do not estimate k.

The paper does not engage neurally: there is no neural correlate (single-unit, fMRI, EEG decoding) of the secondary item's putative attention-template status. The cognitive-architectural conclusion is supported behaviorally only.

The natural-scene search experiment is the smallest sample / weakest evidence in the set. Its inclusion supports generality, but the abstract-array experiments carry most of the statistical weight.

The "single template" alternative the authors reject is a specific operationalization of Olivers et al. (2011); other formulations of SIT (e.g., one *active* template plus *prioritized* accessory items that can race in) are not directly tested.

The paper does not characterize the *temporal dynamics* of secondary-item template status. Does the secondary item remain attention-active for the entire memory delay, or does its template status fluctuate? Eye-movement data could in principle address this on a trial-by-trial basis, but the analyses focus on aggregate capture rather than within-trial dynamics. A model in which templates *switch* between primary and secondary at sub-trial timescales is observationally indistinguishable from a model in which both are simultaneously active when only trial-aggregated measures are reported.

The dual-task design conflates *encoding* of the secondary item with its *active maintenance* during search. If the secondary memory item is automatically encoded into an attention-relevant feature map (a perceptual aftereffect of seeing it), the capture effect could be driven by lingering perceptual priming rather than by active VWM. The authors address this with delayed-test accuracy data, but a perceptual-priming alternative is hard to rule out with behavioral measures alone.

## 7. Connection to our work

This paper supplies the *architectural* answer to the question that follows immediately from the user's commitment to a unified attention–WM substrate. If $H^{(t)}$ in the recurrent ViT serves both attention guidance and WM maintenance (per the [the_user_architectural_program](research_db/threads/the_user_architectural_program.md) and the theoretical anchor of Kiyonaga & Egner 2013), one must ask: *how is multi-content guidance achieved when more than one item is in WM?* Bahle et al. answer: not by serializing through a single template, but by allowing multiple WM contents to simultaneously bias selection.

**Distributed recurrent state, not single-template bottleneck.** The recurrent ViT's $H^{(t)} \in \mathbb{R}^{n_\text{patch} \times d}$ is a *matrix*, not a vector — it has the dimensionality to encode multiple feature-location bindings in parallel. Bahle et al. give the behavioral mandate to *use* that capacity rather than collapse it onto a single dominant template. The architectural commitment to a multi-token recurrent state is empirically licensed by MIT.

**Multi-content feedback into the Feedback Transformer.** In the user's Feedback Transformer (program §1), the Q/K/V projections of the recurrent state are summed with the sensory projections via element-wise broadcast. If multiple WM contents are encoded in $H^{(t)}$, their projections superpose, and the resulting attention map biases selection toward *all* of them. This is the architectural mechanism by which Bahle et al.'s MIT prediction emerges — multi-template guidance is the natural consequence of the additive Q/K/V combination at the softmax input.

**Multi-hub system shared substrate.** In the user's [multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md), each hub contributes its own Q/K/V into the shared central self-attention. Hub-level contributions are themselves multi-content (each hub's recurrent state can encode multiple objective-relevant items). The shared substrate's ability to host concurrent contributions from multiple sources — and to express multiple templates simultaneously — is what makes hub competition non-degenerate. Bahle et al. is the cognitive-science evidence that the central shared substrate operates in this parallel mode rather than serially.

**Capacity questions become architectural questions.** van Moorselaar et al. 2014's bounded-template result, combined with Bahle et al.'s MIT result, gives a graded answer: WM can host *more than one* template, but not arbitrarily many. The recurrent ViT's $H^{(t)}$ has a fixed dimensionality $n_\text{patch} \times d$; its template-hosting capacity should be empirically testable by varying the number of cued features and measuring attention precision. This is a falsifiable prediction the user's architecture inherits from MIT plus capacity-limit work.

**Change-detection relevance.** The recurrent ViT is evaluated on change detection (CDT, 2502.10955), a task where multiple feature-location bindings must be held across the inter-stimulus interval and compared at test. MIT licenses the assumption that the recurrent state encodes *all* of them in parallel and guides attention to *any* mismatching item at test — exactly the operational requirement of CDT performance.

**Bidirectional-feedback consistency.** The user's commitment to bidirectional hierarchical feedback ([bidirectional-hierarchical-feedback](research_db/concepts/bidirectional-hierarchical-feedback.md)) implies that descending projections from higher-layer memory states bias V1-level processing through feature-and-location specific gain. Multiple-template guidance is the natural prediction: a higher-layer state containing multiple feature-binding patterns sends a descending projection that activates *all* matching V1 locations. The single-template view would require gating the descending projection to a single dominant pattern at each timestep, which has no obvious architectural mechanism. MIT is therefore the *default* prediction of the user's architecture; Bahle et al. supplies behavioral confirmation that this default matches human performance.

**Cite location.** The recurrent ViT paper (2502.10955) cites this paper at ref [77] in the context of WM-attention interactions and templates. Future manuscripts arguing for the multi-template character of $H^{(t)}$ should cite Bahle et al. as the behavioral anchor, together with Kiyonaga & Egner for the theoretical framing.

## 8. Citations to follow

- `olivers2011_wm_states_attention` — the active/accessory distinction Bahle et al. are arguing against. In seed.
- `vanmoorselaar2014_template_competition` — the complementary capacity-limit finding. In seed.
- `soto_heinke_humphreys2005_memory_attention_capture` — foundational involuntary WM-capture-of-attention paper. Not yet in seed.
- `carlisle2011_attentional_templates` — template formation and CDA work. In seed.
- `kiyonaga_egner2013_wm_internal_attention` — theoretical anchor; multi-template question follows from the unified-substrate view. In seed, full depth.
- `awh2006_attention_wm` — behavioral catalog of WM-attention interactions. In seed.
- `gazzaley_nobre2012_topdown` — neural common-mechanism review. In seed.
- `hollingworth_hwang2013_scene_attention_wm` — same-lab work on scene-search/WM interactions. Not yet in seed; useful for naturalistic generalization.
- `beck_hollingworth_luck2012_simultaneous_templates` — earlier evidence for simultaneous templates from this group. Not yet in seed.
