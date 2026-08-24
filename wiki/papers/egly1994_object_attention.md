---
id: egly1994_object_attention
title: "Shifting visual attention between objects and locations: evidence from normal and parietal lesion subjects"
authors:
  - "Egly, Robert"
  - "Driver, Jon"
  - "Rafal, Robert D."
year: 1994
venue: "JEP: General"
doi: "10.1037//0096-3445.123.2.161"
arxiv: ""
url: "https://doi.org/10.1037/0096-3445.123.2.161"
tags:
  - visual-attention
  - psychophysics
  - posner-cuing
  - parietal-cortex
  - reaction-time
concepts:
  - attentional-spotlight
  - cueing-effect
  - validity-effect
  - chronometric-function
  - figure-ground-segmentation
  - feature-binding
related:
  - desimone_duncan1995_biased_competition
  - treisman_gelade1980_feature_integration
  - wheeler_treisman2002_binding
  - posner1980_orienting
  - brisson_jolicoeur2008_express_reengagement
  - bisley_goldberg2010_parietal_priority
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_46
status: full
depth: full
last_updated: "2026-05-16"
---

# Shifting visual attention between objects and locations: evidence from normal and parietal lesion subjects

## 1. Abstract

Space- and object-based attention components were examined in neurologically normal and parietal-lesion subjects, who detected a luminance change at one of four ends of two outline rectangles. One rectangle end was precued (75% valid); on invalid-cue trials, the target appeared at the other end of the cued rectangle or at one end of the uncued rectangle. For normals, the cost for invalid cues was greater for targets in the uncued rectangle, indicating an object-based component. Both right- and left-hemisphere patients showed costs that were greater for contralesional targets. For right-hemisphere patients, the object cost was equivalent for contralesional and ipsilesional targets, indicating a spatial deficit; for left-hemisphere patients, the object cost was larger for contralesional targets, indicating an object deficit.

## 2. Why this matters for us

Egly, Driver & Rafal 1994 is the canonical demonstration that visual attention is *object-based*, not purely *location-based*. The same physical-distance shift of attention is faster within a single object than between two objects — even when retinal eccentricity and spatial separation are matched. This is directly relevant to the Recurrent ViT, whose attention map operates over a uniform patch grid with no built-in object structure: whether the network's attention spreads preferentially within object boundaries (as in primate vision) is an open architectural question, and Egly et al. is the diagnostic paradigm for asking it. The paper also supplies the dissociation between *spatial* and *object* attention substrates in parietal cortex, which constrains how the user's program should think about attention substrate vs. attentional bias.

## 3. Key claims

1. **Attention spreads within objects faster than across objects.** When attention has to shift the same physical distance, the shift is cheaper if it stays within a single outline object than if it crosses to a separate object — a same-object advantage.
2. **The object effect coexists with a space-based effect.** Invalid-cue costs for within-object shifts are still larger than for valid-cue trials, so spatial attention is still operating; the object effect is an additional component layered on top of space-based attention.
3. **Right-parietal lesions impair the spatial component, sparing the object component.** Right-hemisphere patients show a large contralesional spatial cost but a normally-sized, hemifield-symmetric object cost.
4. **Left-parietal lesions impair the object component, with the deficit lateralized to the contralesional side.** Left-hemisphere patients show an object cost that is larger for contralesional than for ipsilesional targets, the opposite signature from right-hemisphere patients.
5. **Spatial and object attention have at least partly dissociable neural substrates.** The double dissociation across hemispheres rules out the possibility that object-based attention is a derivative epiphenomenon of spatial attention.
6. **The same-object advantage occurs without eye movements and without grouping by similarity.** Participants fixated centrally; the only available cue to objecthood was the closed outline contour of the rectangle, so the effect is plausibly mediated by perceptual grouping at a pre-attentive stage.

## 4. Methods

**Stimuli.** Two outline rectangles arranged either horizontally or vertically on a CRT, centered on fixation. Each rectangle has two "ends"; with two rectangles in the display there are four candidate locations for the target.

**Trial structure.** On each trial: (a) one rectangle end is briefly highlighted (the cue, 75% valid); (b) after a short SOA, a luminance-change target appears at one of the four ends; (c) subjects make a speeded simple-detection response (press a key when the target appears). The cue thus has three target-location contingencies:
- *Valid* (75%): target at the cued end.
- *Invalid same-object* (≈12.5%): target at the *other end of the cued rectangle*. Same physical distance from the cue as the invalid-different-object condition.
- *Invalid different-object* (≈12.5%): target at one end of the uncued rectangle, matched for physical distance from the cue.

The critical contrast is *invalid same-object* vs. *invalid different-object*. Physical distance from cue to target is identical; only objecthood differs.

**Subjects.** Experiment 1: neurologically normal adults. Experiments 2–3: patients with unilateral parietal lesions (right hemisphere or left hemisphere), tested on left-visual-field and right-visual-field targets to compare contralesional and ipsilesional costs.

**Dependent measure.** Mean correct reaction time as a function of cue validity × object × hemifield. The "object cost" is RT(invalid-different-object) − RT(invalid-same-object); the "spatial cost" is RT(invalid-same-object) − RT(valid).

## 5. Results

**Normals (Experiment 1).** Both a spatial and an object component were present. Valid trials were fastest; invalid-same-object trials were slower than valid; invalid-different-object trials were slower still. The reported same-object advantage (the object cost) is on the order of ≈12–13 ms across the original data, with the spatial cost (invalid-same-object minus valid) on the order of ≈20–30 ms. Both effects were highly reliable.

**Right-parietal patients.** Contralesional (left-field) targets were dramatically slowed relative to ipsilesional targets — the expected hemispatial-neglect-like spatial deficit. Critically, the *object* cost (invalid-different vs. invalid-same) was preserved and was approximately equal in size for contralesional and ipsilesional targets. Right parietal damage thus selectively impairs the space-based component while sparing the object-based component.

**Left-parietal patients.** Contralesional (right-field) targets were also slowed, but the *object* cost itself was lateralized: it was substantially larger for contralesional than for ipsilesional targets. Left parietal damage thus impairs the object-based component, with the deficit confined to the contralesional hemifield.

**Double dissociation.** Across the two patient groups the pattern is a hemispheric double dissociation: right parietal damage → spatial deficit, object component preserved; left parietal damage → contralesional object deficit, with the spatial component still present. This is the result most cited downstream and is the load-bearing piece of evidence for the claim that space-based and object-based attention have distinct neural substrates.

## 6. Critique / limitations

**The "objects" are minimalist.** The stimuli are outline rectangles with no surface texture, no 3D structure, no semantic content. The same-object advantage is therefore demonstrated for the simplest possible Gestalt cue (closed contour / good continuation). Subsequent work has shown the effect generalizes to richer object definitions, but the original demonstration is narrow.

**Static, single-fixation paradigm.** Subjects fixate centrally and the attentional shift is covert. The result thus speaks to covert attentional spread within a static scene; it does not directly address eye-movement-based exploration of objects or the dynamics of attention across multi-second viewing.

**The object cost is small.** The same-object advantage is on the order of 10–15 ms — robust statistically but small relative to the spatial cost. This has been used by critics to argue the object component is a derivative effect of attention-based grouping rather than a genuinely object-anchored substrate. The lesion data partially answers this critique (the double dissociation rules out pure derivation from spatial attention), but the magnitude difference still constrains how strongly one can claim a separate object-attention mechanism.

**Two-rectangle design has limitations.** Drawbacks include possible strategic effects (subjects may attend the cued rectangle preferentially because it has a higher local prior of containing the target), and difficulty extending to more than two objects without introducing confounds.

**Lesion-group sizes are modest.** The patient samples are small (typical of 1994-era neuropsychology), and lesions are extensive and variable. The double-dissociation conclusion relies on group-level patterns rather than fine anatomical localization; subsequent fMRI work has been needed to pin down the substrates.

**The mechanism is not specified.** The paper establishes *that* object-based attention exists and is dissociable from spatial attention. It does not specify *how* object structure modulates attentional allocation — whether by grouping at the priority-map level, by spreading activation along object contours, by a separate object-indexed substrate, or by some combination. The mechanism question is left for subsequent literature.

## 7. Connection to our work

**Object structure is not built into the Recurrent ViT's attention map.** The Recurrent ViT operates on a uniform patch grid; the attention map at each layer is a softmax over patch indices with no explicit object-membership prior. Egly et al. is therefore the canonical diagnostic for asking whether *learned* attention spreads to object structure: replicate the two-rectangle paradigm in the network's input space and measure whether the model's attention-map activation propagates faster within a single rectangle than across two rectangles. This is a direct, low-cost behavioral probe of whether the recurrent dynamics implement an object-spreading prior — and a falsifiable prediction for the user's program, which expects coalition-level competition to *favor* representations that respect perceptual grouping (an object is a stable coalition of patches).

**Object attention as biased competition at the coalition level.** The user's coalition-competition thesis (see [the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §5) extends Desimone & Duncan's RF-level competition to inter-coalition competition. An "object" in Egly et al. is naturally read in this framework as a *coalition of co-active patches* whose joint representation is stabilized by the attention map. The same-object advantage is then the signature of within-coalition resource-sharing being cheaper than between-coalition competition. The Feedback Transformer (see §1 of the program thread) supplies the mechanism: feedback that arrives via a value-projection from a coalition-level memory state will broadcast preferentially to patches already participating in that coalition.

**Spatial vs. object substrates and the dual role of parietal cortex.** The double dissociation between right-parietal (spatial) and left-parietal (object) deficits is directly relevant to the user's account of priority maps and bias signals. Spatial bias is the canonical priority-map output of right parietal cortex (Bisley & Goldberg 2010); object bias appears to require a separate left-parietal contribution. For a multi-hub architecture, this suggests the spatial-attention bias and the object-attention bias may live in *distinct hubs* whose contributions to the central self-attention map are summed — exactly the structure of the user's multi-hub-multi-objective system.

**Connection to feature binding and the binding problem.** The object effect implies attention can be allocated to a *bound* entity (the rectangle as a Gestalt unit), not just to a location or a feature value. This positions Egly et al. between Treisman & Gelade 1980 (feature integration via spatial attention) and Wheeler & Treisman 2002 (object-based binding in working memory). For the user's program, where features are bound into objects in WM and then influence future attention, Egly et al. is the behavioral demonstration that the binding survives the trip through attention and shapes subsequent attentional allocation.

**Probing the Recurrent ViT's emergent object structure.** Concretely, the experiment to run on the published model: present two outline rectangles in the input image; cue one rectangle end via a brief contrast pulse; measure the spread of attention-map mass over recurrent steps to (a) the cued end, (b) the other end of the same rectangle, (c) the matched-distance end of the other rectangle. If the published Recurrent ViT shows a same-object advantage in attention-map propagation latency, that is direct evidence that the recurrent attention dynamics implement an implicit object prior; if it shows none, the program's natural next step is to add an object-spreading mechanism (e.g., via explicit grouping in the value projection, or via a coalition-level feedback hub).

## 8. Citations to follow

- `duncan1984_object_attention` — Duncan's earlier divided-attention demonstration of object-based limits; the conceptual precursor to Egly et al. Not in seed.
- `posner1980_orienting` — the spatial-cuing paradigm Egly et al. extend. In candidates.
- `treisman_gelade1980_feature_integration` — feature integration via spatial attention; the framework Egly et al. complicates. In candidates.
- `wheeler_treisman2002_binding` — object-level binding in working memory; downstream of Egly. In candidates.
- `desimone_duncan1995_biased_competition` — the unifying framework that absorbs spatial, feature, and object attention; cites Egly. Already full.
- `scholl2001_objects_units_attention` — review of the object-attention literature that Egly anchors. Not in seed.
- `mozer_vecera2005_object_attention` — computational model of within-object attentional spread. Not in seed.
- `vecera_farah1994_does_visual_attention` — concurrent demonstration of object-based attention with different stimuli. Not in seed.
- `bisley_goldberg2010_parietal_priority` — priority-map account of parietal attention; subsumes the spatial side of Egly's dissociation. In seed.
