---
id: treisman_gelade1980_feature_integration
title: "A feature-integration theory of attention"
authors:
  - "Treisman, Anne M."
  - "Gelade, Garry"
year: 1980
venue: "Cognitive Psychology"
doi: "10.1016/0010-0285(80)90005-5"
arxiv: ""
url: "https://doi.org/10.1016/0010-0285(80)90005-5"
tags:
  - visual-attention
  - psychophysics
  - theoretical-essay
concepts:
  - feature-binding
  - attentional-spotlight
  - attentional-template
related:
  - desimone_duncan1995_biased_competition
  - luck_vogel1997_wm_capacity
  - wheeler_treisman2002_binding
  - koch_ullman1984_winner_takes_all
  - bisley_goldberg2010_parietal_priority
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-14"
---

# A feature-integration theory of attention

## 1. Abstract

(No standardized abstract is available on PubMed for this 1980 paper; PMID 7351125 lists "No abstract available." The summary below is a faithful paraphrase reconstructed from prior knowledge of the paper and its decades of replication / citation. Cognitive Psychology, 12(1):97–136, 1980.) Treisman and Gelade propose a *feature-integration theory* (FIT) of visual attention. Simple visual features — color, orientation, size, motion, basic shape primitives — are registered in parallel across the visual field, automatically and pre-attentively, in separate feature maps. Conjunctions of features into objects, however, require focal attention, which acts as a serial "glue" binding co-located feature values into unified object representations. Five experiments using visual search and texture segregation establish the asymmetry: search for a single distinctive feature (a red letter among green, or a tilted line among vertical) is fast, parallel, and roughly independent of display size, whereas search for a *conjunction* of features (a red T among red Os and green Ts) is slow, serial, and scales linearly with display size. When attention is overloaded or unavailable, observers report *illusory conjunctions* — incorrect feature combinations such as "red T" when the display contained a green T and a red O. The theory is offered as a unifying account of feature analysis, attentional binding, and the spotlight metaphor of attention.

## 2. Why this matters for us

Treisman & Gelade 1980 is the foundational behavioral paper establishing the *binding problem*: feature maps are computed in parallel but object identity requires attention to bind them. This is the explicit warrant for the user's program's commitment to object-level representations and to *attention as the binding mechanism*. The Recurrent ViT's softmax-attention map is, on the FIT reading, exactly the computational instantiation of the "glue" — each query token attends to all keys and produces a unified per-token representation that integrates spatially-distributed feature information. PRISM v1's per-pixel prediction-error formulation, by contrast, sidesteps attention-based binding by computing features locally; whether PRISM v1 can solve binding-heavy tasks (illusory-conjunction-prone displays, conjunction visual search) is an open empirical question this paper sharpens. FIT is also the direct precursor of biased competition ([desimone_duncan1995_biased_competition](research_db/papers/desimone_duncan1995_biased_competition.md)), priority-map theory ([bisley_goldberg2010_parietal_priority](research_db/papers/bisley_goldberg2010_parietal_priority.md)), and the WM-capacity literature ([luck_vogel1997_wm_capacity](research_db/papers/luck_vogel1997_wm_capacity.md)) — it sits at the root of the citation graph for the user's program.

## 3. Key claims

1. **Separate feature maps.** The visual system computes a separate map for each elementary feature dimension (color, orientation, size, basic shape primitives) in parallel across the visual field. Each map registers feature *presence* but not feature *location-binding* to other dimensions.
2. **Pre-attentive parallel feature detection.** Detection of a single distinctive feature is parallel and roughly independent of display size; an item that differs from distractors in one feature "pops out."
3. **Attention is required to bind features into objects.** Conjunction of features from separate maps into a unified object representation requires focal attention applied serially to each location.
4. **Conjunction search is serial and capacity-limited.** Search for a target defined by a feature *conjunction* (e.g., red T among red Os and green Ts) yields linear set-size functions consistent with serial item-by-item examination.
5. **Illusory conjunctions occur when attention is unavailable.** Under brief presentation or divided attention, observers mis-combine features across objects, reporting feature combinations that were not present (e.g., "red T" when the display contained a green T and a red O). This is direct evidence that feature-to-object binding is attention-dependent.
6. **A "master map of locations" integrates the feature maps.** Attention is directed by selecting a location on a master spatial map; selecting a location automatically retrieves all features registered at that location, producing the bound object percept.
7. **Texture segregation is parallel for single features but not for conjunctions.** Texture boundaries defined by a single feature pop out; boundaries defined by a feature conjunction do not segregate pre-attentively.

## 4. Methods

A series of visual-search and texture-segregation experiments in human observers, with the following structure:

- **Visual search task.** Observers searched displays of 1, 5, 15, or 30 items for a target, and reaction time (RT) was measured as a function of display size. Two target conditions: (a) *feature* targets — defined by a single distinctive feature (e.g., the letter S among green Ts and brown Xs, where the target is the only orange item); (b) *conjunction* targets — defined by a conjunction (e.g., a green T among brown Ts and green Xs).
- **Target-present vs target-absent trials.** Both were collected; the slope of RT against display size on target-absent trials is the diagnostic measure of serial vs parallel search. A self-terminating serial mechanism predicts a ≈2:1 ratio of absent:present slopes (the observer must scan, on average, half the items to find a target but all items to confirm absence).
- **Illusory-conjunction paradigm.** Brief masked presentation (≈200 ms) of multi-item displays, with verbal report or forced-choice identification of target features and their bindings. Observers were biased away from attentional focus by a concurrent letter-identification task at fixation, with the to-be-reported items in the periphery. The key contrast is between *illusory conjunctions* (correct features incorrectly bound across objects) and *feature errors* (features not present in the display) — the relative rates dissociate guessing from mis-binding.
- **Texture-segregation task.** Observers judged whether a target region of a textured display lay to the left or right of fixation, with the region defined either by a single feature or by a conjunction. The two conditions are matched on low-level stimulus statistics (the same letters in the same densities) so that any difference in segregation performance isolates the binding requirement.
- **Identification-vs-detection contrast.** Observers were sometimes asked to *detect* a target (yes/no) and sometimes to *identify* it (which target was present). Identification requires correct binding, detection of a single feature does not — providing a within-experiment dissociation of the two stages.

The dependent measures were RT slopes (target-present, target-absent), error rates, and the rate and pattern of illusory conjunctions vs feature-only errors. The theoretical analysis is anchored in the slope-of-RT-vs-set-size signature plus the illusory-conjunction rate; together these provide converging behavioral evidence for the two-stage architecture.

## 5. Results

The 1980 paper reports a set of now-canonical findings, replicated hundreds of times in the subsequent literature:

- **Feature search is parallel.** RT slope for feature-target search is shallow (≈0–5 ms/item for target-present; similarly shallow for target-absent), consistent with parallel processing.
- **Conjunction search is serial and self-terminating.** RT slope for conjunction-target search is steep (≈25–30 ms/item target-present, ≈50–60 ms/item target-absent); the 2:1 ratio of absent:present slopes is the classical serial-self-terminating signature.
- **Illusory conjunctions are frequent and systematic.** Under divided / unfocused attention, observers report illusory conjunctions at rates substantially above chance (often 15–30% of trials in the relevant cells). Feature-only errors (reporting a feature not present at all) are much rarer than mis-binding errors, ruling out a purely guessing account.
- **Spatial proximity matters.** Illusory conjunctions are more likely between spatially adjacent items, consistent with attention as a spatial selection operation.
- **Texture segregation is parallel only for single features.** Conjunction-defined texture boundaries do not produce automatic segregation; they require serial scrutiny.

Combined, these results dissociate two regimes of visual processing — a pre-attentive parallel feature stage and a serial attention-dependent binding stage — and identify attention as the mechanism responsible for the second.

## 6. Critique / limitations

Subsequent work has substantially refined and qualified FIT, though the binding-requires-attention core has held up.

**Strict serial/parallel dichotomy too rigid.** The strict parallel/serial dichotomy was challenged by Wolfe's *Guided Search* (Wolfe 1989, 1994 and subsequent versions): conjunction search is not purely serial but is *guided* by parallel feature maps that bias attention toward likely target locations. The RT-by-set-size functions are continuous rather than bimodal, and many "conjunction" searches are faster than strict serial scanning predicts.

**Special feature combinations.** Some feature dimensions yield surprisingly efficient conjunction search (e.g., color × motion, color × stereoscopic depth), suggesting either special pre-attentive conjunction detectors or top-down guidance from multiple feature maps simultaneously. This has prompted hybrid models (Guided Search, *similarity theory* of Duncan & Humphreys 1989) that retain FIT's feature-map architecture but reject the strict serial-binding bottleneck.

**Guessing-corrected illusory-conjunction rates.** Illusory conjunctions, while real, occur at lower rates than the original paper's bias-uncorrected estimates suggested once guessing-corrected (Ashby et al. 1996; Donk 1999). They remain a robust signature of binding failure but are no longer the iron-clad "attention required" evidence Treisman initially claimed.

**Master map underspecified.** The "master map of locations" is functionally described but anatomically unspecified. Subsequent work has localized priority-map-like spatial representations to LIP / FEF / pulvinar / SC ([bisley_goldberg2010_parietal_priority](research_db/papers/bisley_goldberg2010_parietal_priority.md)), but the binding function — actually retrieving features-at-an-attended-location — remains computationally underspecified at the neural level.

**Treisman's own revisions.** Treisman herself substantially revised FIT in later work (Treisman 1996, 1998; [wheeler_treisman2002_binding](research_db/papers/wheeler_treisman2002_binding.md)), incorporating object files, feature-integration in working memory, and the recognition that binding is a multi-stage process distributed across perception, attention, and memory rather than a single serial bottleneck.

**Mechanism vs metaphor.** The theory is silent on *how* attention performs the binding computationally. "Glue" is a metaphor, not a mechanism. Modern accounts (synchrony / oscillation binding; convergence onto conjunction-selective neurons; attention-modulated normalization; softmax-attention-style population readout) all postdate FIT and are partly competing, partly compatible elaborations.

**Pre-attentive feature set under-defined.** What counts as a "feature" available pre-attentively is operationally defined by what supports parallel search. This is circular: a stimulus that supports parallel search is by definition a feature. The theory does not predict in advance which novel dimensions will or will not yield parallel search.

## 7. Connection to our work

This paper is the foundational behavioral citation for binding-via-attention and is load-bearing across the user's program.

**Softmax attention as a binding mechanism.** The Recurrent ViT's per-layer softmax self-attention can be read, in FIT terms, as the computational implementation of the "glue." Each query token gathers information from all keys, weighted by feature-similarity. The output token at each location is a feature-bound representation: it integrates color, shape, position, and any other dimension carried in the value projection, all gated by a single attention map. The user's commitment to softmax attention (Recurrent ViT paper, 2502.10955, §3 and §6.7) rather than to PRISM v1's pixel-wise prediction error is *exactly* a commitment to FIT-style binding: softmax attention solves the binding problem by construction, prediction-error does not.

**Cued attention and the master map of locations.** The cued-attention result in the Recurrent ViT (faster RT and higher accuracy at cued locations) is a direct behavioral echo of FIT's master-map-of-locations claim: a top-down cue selects a location on the spatial map, which biases the attention competition (per biased-competition theory, [desimone_duncan1995_biased_competition](research_db/papers/desimone_duncan1995_biased_competition.md)) toward features at that location. The user's program reads the central self-attention map as the master map of locations and the per-hub Q/K projections as the feature maps that populate it.

**Multi-hub competition for binding.** The user's competition-emergent-PC thesis ([coalition_resource_competition](research_db/concepts/coalition_resource_competition.md)) extends FIT in a specific way: in the multi-hub system, *each hub* is a different feature dimension or task-relevant feature set, and the central self-attention map is the binding substrate where hubs compete to determine *which features get bound to which spatial locations*. The Feedback Transformer's Hadamard combination of bottom-up sensory Q/K projections with hub-specific feedback projections is the mechanism by which competing hubs influence which feature-conjunction wins the binding competition at each location. FIT's "attention binds features" generalizes to "the multi-hub system's central attention map binds whichever features the winning coalition has biased into the attention competition."

**Illusory conjunctions as a failure mode to test.** The user's program predicts that when the binding mechanism is overloaded (too many objects, insufficient recurrent passes, restricted attention bandwidth), the architecture should produce *systematic* binding errors analogous to illusory conjunctions. This is a falsifiable prediction. PRISM v1, which does not use softmax attention, should produce a *different* error signature (e.g., spatially-local feature errors rather than cross-object feature swaps). Testing this contrast on a synthetic conjunction-search task is a clean way to empirically distinguish the binding mechanisms of the two architectures.

**PRISM v1's binding problem.** PRISM v1 (`Prism/docs/THESIS.md`) uses per-patch prediction error in place of softmax attention. This is theoretically attractive (computational efficiency, predictive-coding alignment) but it raises a binding concern: how does a per-patch error signal solve the FIT binding problem? The user's program should explicitly address whether PRISM v1's $M_t$ memory state plus FiLM modulation provides functionally adequate binding, or whether the lack of softmax attention is a load-bearing limitation. PRISM v2's reintroduction of multi-head attention (`PrismV2/docs/PRISM_V2_PROPOSAL.md` §3.4) partially walks this back.

**Visual-search RT signatures as model evaluation.** Treisman & Gelade's RT-by-set-size methodology gives a clean evaluation paradigm for the recurrent ViT: present feature-target and conjunction-target search displays and measure the number of recurrent passes (the model's analog of RT) required to localize the target. If conjunction search requires more passes than feature search, and the per-pass increment scales with set size, that is a behaviorally-grounded validation of FIT-style processing in the architecture. The same paradigm can be used to compare the recurrent ViT against PRISM v1 / v2, providing a direct behavioral discriminator between attention-based and prediction-error-based binding.

**Recurrence as the substrate for serial binding.** FIT posits *serial* application of attention to bind conjunctions. The user's program operationalizes "serial" as recurrent passes over a shared self-attention substrate (Recurrent ViT 2502.10955 §3). A single forward pass corresponds to FIT's pre-attentive parallel stage; additional recurrent passes correspond to attention being deployed serially across locations. The qualitative finding in the Food-101 classifier experiments — that attention maps "focus, defocus, and reactivate" over passes — is exactly the FIT-predicted signature of serial binding, observed at the level of model internals. This is a non-trivial cross-validation: the user's architecture, designed on different grounds (cortical recurrence, feedback-transformer primitive), reproduces the qualitative dynamics that FIT predicts on behavioral grounds.

**Object files and PRISM's memory state.** Treisman's later work introduced *object files* — episodic representations that hold the bound features of an attended object across time. PRISM v1's $M_t$ memory state can be read as a population-level object-file analog: a persistent representation that maintains feature-binding across recurrent steps. The user's program should make this connection explicit in PRISM v1 / v2 writeups; it provides a cognitive-science-grounded interpretation of what the slow memory is *for* beyond the engineering claim of "improved change-detection performance."

## 8. Citations to follow

- `wolfe1994_guided_search` — Guided Search 2.0; the principal refinement of FIT. Not in seed.
- `duncan_humphreys1989_similarity_search` — similarity-based account of visual search as a competitor to strict-FIT. Not in seed.
- `treisman1988_features_objects` — Treisman's own 1988 mid-life revision of FIT (Bartlett Lecture). Not in seed.
- `treisman1996_binding` — Treisman's "Binding problem" review article. Not in seed.
- `wheeler_treisman2002_binding` — Treisman's later WM-binding work. In seed list.
- `koch_ullman1984_winner_takes_all` — saliency map / WTA mechanism that complements FIT's master map. In seed list.
- `desimone_duncan1995_biased_competition` — biased-competition framework; the neural-mechanism successor to FIT. In seed, full depth.
- `bisley_goldberg2010_parietal_priority` — priority-map theory and its candidate neural substrates. In seed.
- `luck_vogel1997_wm_capacity` — WM capacity for bound objects vs features. In seed.
- `wolfe2017_five_factors_search` — recent integrative review of visual search; not in seed.
- `ashby_etal1996_illusory_conjunctions_chance` — guessing-corrected analysis of illusory-conjunction rates. Not in seed.
