---
id: pertzov_husain2014_location_wm
title: "The privileged role of location in visual working memory"
authors:
  - "Pertzov, Yoni"
  - "Husain, Masud"
year: 2014
venue: "Attention, Perception, & Psychophysics"
doi: "10.3758/s13414-013-0589-8"
arxiv: ""
url: "https://doi.org/10.3758/s13414-013-0589-8"
tags:
  - working-memory
  - visual-attention
  - psychophysics
concepts:
  - feature-binding
  - topographic-organization
  - retinotopy
  - priority-map
related:
  - luck_vogel1997_wm_capacity
  - schneegans_bays2017_feature_binding_wm
  - wheeler_treisman2002_binding
  - bays2024_wm_representation
  - treisman_gelade1980_feature_integration
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_121
status: full
depth: full
last_updated: "2026-05-14"
---

# The privileged role of location in visual working memory

## 1. Abstract

Visual working memory (VWM) maintains a small number of items across brief delays, but how the features of those items are organized and bound together remains contested. Pertzov & Husain (2014) test whether *location* enjoys a privileged status among feature dimensions — that is, whether spatial position serves as the index along which other features (color, orientation, shape) are stored and retrieved. Across a series of continuous-report change-detection experiments, the authors manipulate whether to-be-remembered items are presented sequentially at the *same* spatial location or at *different* locations, holding all non-spatial features equal. They find that when objects share a location, participants make substantially more *misbinding* errors (reporting the feature of a non-probed item), and that the precision of the recalled non-spatial feature degrades more steeply than when items occupy distinct locations. The pattern indicates that location is not merely one feature among many: it is the *organizing index* on which feature bindings hang. When that index collapses (because items share a location), the bindings collapse with it.

## 2. Why this matters for us

The user's architectural program is committed, at every level, to *spatially-organized* memory: the Recurrent ViT's recurrent memory is a 12×12 patch grid that aligns with the input's spatial layout; PRISM v1 modulates its feature stack via FiLM gains that vary across spatial positions; the GridCell RNN concept and the multi-compartmental memory stack both treat space as the primary axis of organization. Pertzov & Husain 2014 supplies the strongest psychophysical evidence that human VWM uses *exactly this design choice*: location indexes object representations, and binding between features rides on the location index. This is a non-trivial commitment — one could imagine VWM as an unstructured set of bound feature bundles — and the evidence that human VWM is *spatially indexed* supports the user's architectural decision over the alternative of a flat, location-agnostic memory.

## 3. Key claims

1. **Location is privileged.** When multiple objects in VWM occupy the *same* location (presented sequentially), the binding of non-spatial features to those objects is impaired beyond what would be expected if all features were exchangeable indices.
2. **Misbinding scales with shared-location.** The frequency of *swap errors* — reporting the feature of an unprobed item — rises sharply when items share a location.
3. **Precision degrades with shared-location.** Even when the correct item is reported, the precision of recalled non-spatial features (e.g., orientation, color) is lower in shared-location than distinct-location conditions.
4. **The effect is not feature-specific.** The same pattern obtains across color, orientation, and shape, suggesting that location's privileged role is general, not an artifact of one feature dimension.
5. **Location encoding is robust.** Unlike non-spatial features, location itself is recalled accurately regardless of whether items share other features.
6. **Implication for binding theory.** Visual working memory is not a flat slot-set of bound objects; it is a *spatially-indexed* structure in which features are bound *to* locations, and the location index is the load-bearing dimension.
7. **Connection to feature-integration theory.** The result is broadly consistent with Treisman & Gelade's feature-integration theory ([treisman_gelade1980_feature_integration](research_db/papers/treisman_gelade1980_feature_integration.md)): attention bound to a location is what integrates features, and location is the medium through which the integration is maintained over the retention interval.

## 4. Methods

**Continuous-report paradigm.** The authors used the Bays / Husain–lab continuous-response paradigm: subjects view a brief memory array of N items (e.g., colored, oriented bars), and after a retention interval (typically ~900 ms–1 s) are probed on one item. The probe can specify the target via its location (cue the location, recall the feature) or via its feature (cue the feature, recall the location). The response is a continuous rotation of a dial — orientation in degrees, color on a continuous color wheel — yielding a continuous error distribution.

**Critical manipulation: shared vs distinct location.** In the key experiments, items were presented *sequentially* either all at the same screen location (shared-location condition) or at different locations (distinct-location condition). All other variables — set size, retention interval, feature dimension, exposure duration — were matched across conditions. This isolates the role of spatial separation in binding.

**Mixture-model decomposition.** Error distributions were fit with the standard Bays mixture model: a von Mises around the target (precision $\kappa$), a uniform component (random guessing), and a non-target mixture component (swap errors / misbinding). The three components quantitatively separate three failure modes: imprecise memory, complete loss, and misbinding to a non-probed item. The mixture decomposition is essential: a raw error-magnitude analysis would conflate swap errors with imprecision, and the central claim of the paper rides on the swap component specifically.

**Set sizes and retention intervals.** Set sizes typically ranged from 1 to 4 (within the Luck-Vogel capacity), with retention intervals up to several seconds. The effect of shared-location was tested across these manipulations to assess robustness.

**Probe types.** Two probe directions were tested: location-cue (cue the location, recall the non-spatial feature) and feature-cue (cue the non-spatial feature, recall the location). The asymmetry between these two directions is itself diagnostic of which feature is the privileged index.

## 5. Results

The principal quantitative findings:

- **Misbinding rates are elevated in shared-location.** When items share a location, the swap-component of the mixture model rises substantially — participants report the feature of a non-probed item at rates well above the distinct-location baseline.
- **Precision drops in shared-location.** The von Mises concentration $\kappa$ for correctly-attributed responses is lower in shared-location, indicating noisier non-spatial feature recall when the location index is degenerate.
- **Location-cued recall outperforms feature-cued recall.** When subjects are cued by location and asked to report a feature, performance is higher than when they are cued by a feature and asked to report a location — consistent with location being the primary index.
- **The effect is monotonic with set size.** Shared-location costs grow as more items must be stored, confirming that the deficit is in binding rather than in encoding a single item.
- **Robustness across feature dimensions.** The same qualitative pattern holds for color, orientation, and shape, supporting the generality of the location-privileged account.
- **Location precision is preserved.** Even in conditions where non-spatial features are reported poorly, location recall remains accurate — a striking asymmetry that motivates the "privileged" framing.
- **Time-since-encoding interacts with shared-location.** Items encoded earlier in the sequence are more vulnerable to misbinding when locations are shared, suggesting that the location index is what protects older bindings from feature-level interference.

## 6. Critique / limitations

The shared-location manipulation requires *sequential* presentation. This conflates two factors: (a) the spatial overlap itself and (b) the temporal grouping that necessarily accompanies sequential same-location presentation. Subsequent work has tried to dissociate these; the 2014 paper does not fully control for temporal-binding-window effects.

The "privileged location" framing rests on continuous-report error decompositions, which assume the Bays mixture model's three-component structure (precision, guesses, swaps). This model has been critiqued (e.g., variable-precision alternatives; see [bays2024_wm_representation](research_db/papers/bays2024_wm_representation.md)) and the partition of errors into swaps vs. precision-loss can be model-dependent.

The neural mechanism is left implicit. The paper is psychophysical; it does not identify *where* in the brain location indexes feature bindings (parietal priority maps? early visual retinotopic cortex? entorhinal grid cells?). This neural locus is supplied by subsequent work but is open in 2014.

The paradigm is *retinotopic*: all stimuli are on a screen and locations are coded in screen coordinates. Whether the "privileged location" finding extends to spatiotopic, allocentric, or object-centric reference frames is not tested. Real-world VWM operates over moving eyes and bodies, where this distinction matters.

Finally, the effect is *relative*: location is privileged relative to color, orientation, shape. The paper does not address whether other dimensions (time of presentation, identity, semantic category) might also serve as binding indices under different conditions.

A further concern: the continuous-report paradigm uses small set sizes (≤4) and brief retention intervals (≤ a few seconds). The location-privileged effect at longer delays or under interference is unclear from this paper alone. Subsequent work (Schneegans & Bays 2017, [schneegans_bays2017_feature_binding_wm](research_db/papers/schneegans_bays2017_feature_binding_wm.md)) extends and partially refines the account, formalizing location-binding as a population-coding model rather than a discrete index.

## 7. Connection to our work

This paper is one of the strongest empirical supports for the user's *spatial-grid* commitment in memory architecture. Several specific connections.

**Recurrent ViT — the 12×12 patch grid memory.** The Recurrent ViT (2502.10955) maintains a recurrent memory state $H^{(t)}$ that is a 12×12 grid aligned with the input patches — i.e., the memory is explicitly retinotopic. Pertzov-Husain shows that this is the design choice human VWM appears to make: locations index features, and the memory's organizing axis is spatial. The published paper's grid-aligned memory is therefore not just a computational convenience; it is the *psychophysically motivated* design for a VWM model. Future analyses of the recurrent ViT's memory state — e.g., misbinding analyses when stimuli share a patch — could directly test whether the model reproduces Pertzov-Husain's shared-location cost.

**PRISM v1 — retinotopic FiLM modulation.** PRISM v1 (`THESIS.md` §2.4) uses FiLM gains $\gamma, \beta$ that vary across spatial positions: each patch position has its own modulation parameters. The location-privileged account predicts this should work better than a globally-shared FiLM (which would erase the spatial index) and should be roughly indifferent to which non-spatial features are modulated (consistent with PH's cross-feature generality). PRISM v1's architecture is consistent with the location-privileged finding.

**GridCell RNN and multi-compartmental memory.** The GridCell RNN concept (`the_user_architectural_program.md` §2) maintains internal grid states $C_i^{(t)} \in \mathbb{R}^{n_{gh} \times n_{gw} \times n_{C_i}}$ where the grid axis is spatial. The user's architectural commitment is that each grid cell holds a feature bundle bound to its spatial location, and the Feedback Transformer integrates *across* cells. This is precisely the spatially-indexed binding structure Pertzov-Husain argue for in human VWM.

**PRISM v2 — slow/fast and hierarchical memory.** PRISM v2's slow/fast memory and hierarchical FiLM both preserve spatial organization across the hierarchy. The Pertzov-Husain finding suggests this is not just convenient but cognitively realistic.

**Predicted vulnerability.** A direct architectural consequence of the Pertzov-Husain account is that any change-detection model with spatially-indexed memory should exhibit *more* misbindings when stimuli occupy the same patch position across the trial. This is a falsifiable prediction the user's models can be probed for. If the recurrent ViT does *not* show the shared-location swap pattern, that is evidence its memory is not spatially indexed in the same way humans' is.

**Feedback Transformer integration.** The Feedback Transformer primitive (`the_user_architectural_program.md` §1) integrates feedback from multiple memory states at the level of Q/K/V projections, *with the constraint that every feedback source has the same number of patches/tokens as the sensory input*. This patch-aligned constraint is precisely a location-indexed binding: each token's query, key, and value are sums of bottom-up and top-down contributions at *that location*. Pertzov-Husain supplies the psychophysical warrant for this design — human VWM appears to bind features by location, so an architecture that binds feedback by patch position is following human VWM, not just engineering convenience.

**Tension with object-based capacity.** Luck & Vogel 1997 ([luck_vogel1997_wm_capacity](research_db/papers/luck_vogel1997_wm_capacity.md)) argued capacity is at the *object* level. Pertzov-Husain refine this: objects are stored, but the *index* for object retrieval is the location, not the object identity. The two accounts are compatible — objects are bound feature bundles indexed by location — and together specify what an architectural model of VWM should look like.

**Relation to priority maps.** The user's broader literature includes parietal priority-map work (LIP, posterior parietal) as a candidate neural substrate for the location index. The Pertzov-Husain finding is consistent with VWM consulting a priority-map-like spatial structure as its retrieval cue, which is the same structural commitment the recurrent ViT's patch grid embodies in artificial form.

The recurrent ViT paper cites this work in its bibliography (ref [121]). It is one of the key motivations for the spatial-grid memory design.

## 8. Citations to follow

- `bays_husain2008_dynamic_precision` — the precision-resource model behind the continuous-report analysis. Not yet in seed.
- `schneegans_bays2017_feature_binding_wm` — extends the location-privileged account into a full binding-by-location model. In seed.
- `treisman_gelade1980_feature_integration` — FIT, the classical theory of feature binding. In seed.
- `wheeler_treisman2002_binding` — feature binding in short-term visual memory. In seed.
- `luck_vogel1997_wm_capacity` — the founding capacity paper. In seed, full depth.
- `bays2024_wm_representation` — modern review of WM representation, including continuous-resource vs slot debate. In seed.
- `jiang_olson_chun2000_organization_vwm` — location-based organization of VWM. Not yet in seed.
- `hollingworth_henderson2002_object_files` — object-file framework that prefigures location indexing. Not yet in seed.
- `kahneman_treisman_gibbs1992_object_files` — the classical object-files paper. Not yet in seed.
- `pertzov_dong_peich_husain2012_temporal_dynamics` — same lab's earlier work on temporal dynamics of VWM. Not yet in seed.
- `bays_catalao_husain2009_precision_resource` — the precision-as-resource framework. Not yet in seed.
