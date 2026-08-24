---
id: wheeler_treisman2002_binding
title: "Binding in short-term visual memory"
authors:
  - "Wheeler, Mary E."
  - "Treisman, Anne M."
year: 2002
venue: "JEP: General"
doi: "10.1037/0096-3445.131.1.48"
arxiv: ""
url: "https://doi.org/10.1037/0096-3445.131.1.48"
tags:
  - working-memory
  - visual-attention
  - change-detection
  - psychophysics
concepts:
  - feature-binding
  - working-memory-persistent-activity
related:
  - luck_vogel1997_wm_capacity
  - luck_vogel2013_wm_capacity_review
  - bays2024_wm_representation
  - treisman_gelade1980_feature_integration
  - schneegans_bays2017_feature_binding_wm
  - awh2006_attention_wm
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_78
status: full
depth: full
last_updated: "2026-05-14"
---

# Binding in short-term visual memory

## 1. Abstract

Wheeler and Treisman investigated how features are bound together in visual short-term memory (VSTM), extending the feature-integration theory of attention (Treisman & Gelade 1980) into the working-memory domain. Across a series of change-detection experiments using objects defined by combinations of color, shape, and location, they tested whether the ~4-item capacity reported by Luck & Vogel 1997 reflects storage of *bound objects* or of *parallel feature pools*. Their central findings: (1) features drawn from the same dimension (e.g., two colors per item) compete for a limited within-dimension store, whereas features from *different* dimensions can be maintained in parallel with little mutual interference, implying multiple specialized feature stores rather than one global object-slot pool; (2) memory for the *binding* between features is *more fragile* than memory for the constituent features themselves, and is selectively impaired when attention is withdrawn or when the test display is a whole array rather than a single probe; (3) location–feature bindings behave differently from feature–feature bindings, with location occupying a privileged role. The authors propose that VSTM consists of independent feature stores plus an attention-demanding integration mechanism that maintains conjunctions as transient "object files." This positions binding in WM as an active, attentionally-gated process rather than a passive byproduct of slot-based storage.

## 2. Why this matters for us

This is the paper that converts the *static* Feature-Integration-Theory (FIT) claim — that binding requires focused attention at encoding — into a *dynamic, maintenance-phase* claim: even once features are encoded, holding them as a bound object across a delay continues to demand attention. For the user's program, that distinction matters in two ways. First, the recurrent ViT (arXiv:2502.10955) performs cued change detection across a delay; whether its recurrent state holds bound object representations or merely parallel feature buffers is precisely the Wheeler–Treisman question, transposed onto an artificial network. Second, the Feedback Transformer's Q/K/V integration of multiple recurrent states is, in functional terms, a candidate mechanism for *exactly* the attention-mediated binding maintenance Wheeler and Treisman argue is necessary. The paper supplies the empirical signature any architectural model of binding-in-WM must reproduce: dissociation between feature memory and binding memory, with the latter degrading first under attentional load.

## 3. Key claims

1. **Within-dimension features compete; cross-dimension features do not.** Two colors per object interfere more than one color + one shape per object, indicating dimension-specific stores rather than a single object-slot pool.
2. **Binding memory is more fragile than feature memory.** Subjects can report constituent features (color, shape) above chance while failing to report which features were bound together, especially under attentional load or long delays.
3. **Binding maintenance demands attention.** A concurrent attention-demanding task (verbal load, articulatory suppression, attentional capture) selectively impairs binding performance while sparing feature memory.
4. **Single-probe tests outperform whole-display tests for binding.** When the test display presents only the probed object, binding accuracy improves substantially; when the test display presents all original objects (some intact, some rearranged), interference from rebinding alternatives degrades binding memory disproportionately.
5. **Location–feature bindings have privileged status.** Bindings that include location are more robust than feature–feature bindings without location, consistent with location's role as the "indexing variable" of the visual system.
6. **VSTM is not a unified object store.** Rather, it consists of (a) parallel feature stores, one per dimension, each with its own capacity, plus (b) an attention-gated binding mechanism that maintains conjunctions as long as attention is available.
7. **Implications for Luck & Vogel 1997.** The ~4-item object capacity reflects the *limit on bound representations the binding mechanism can maintain*, not the limit of feature storage per se — features may be available in greater numbers but only bound for a small subset.
8. **Binding architecture is two-component.** VSTM = parallel dimension-specific stores + attention-gated binding mechanism; this two-component view replaces the unified-slot view of Luck & Vogel and ports FIT's encoding-time attention requirement into the maintenance phase.

## 4. Methods

**Paradigm.** Standard change-detection task: memory array (1 s), retention interval (~900 ms), test array. Subjects judged whether the test array matched the memory array or whether something had changed. Set size was varied from 1 to 6.

**Stimulus dimensions.** Objects were defined by combinations of features drawn from up to three dimensions: color, shape, and location. The critical manipulation across experiments was whether the changed item involved a *feature swap* (a feature value novel to the display) or a *binding swap* (all feature values present in the original memory array but recombined across objects).

**Single-probe vs whole-display test.** In some experiments the test array showed only the probed object at its original location; in others, the full set of objects reappeared. Whole-display tests force binding judgments to be made in the presence of rebinding-distractor information.

**Attentional manipulations.** Concurrent verbal load (articulatory suppression with random digit shadowing), attentional capture by transient onsets during the retention interval, and divided-attention encoding were all used to test whether binding maintenance is attention-demanding.

**Critical contrast.** *Feature change* trials change a constituent feature value, testing feature memory. *Binding change* trials preserve all feature values but rearrange the conjunctions, testing only the binding. Subtracting performance on the two trial types isolates binding memory from feature memory.

**Capacity estimation.** Cowan's *K* computed separately for feature changes and binding changes. Difference between the two K values indexes the cost of binding.

**Experiment series.** The paper reports a sequence of experiments that progressively isolate the binding cost. Early experiments establish baseline single-feature and conjunction capacities under matched conditions; intermediate experiments introduce the binding-change vs feature-change contrast at fixed set size; later experiments add the concurrent-attention manipulations and the single-probe vs whole-display test contrast. The cumulative design lets the authors triangulate the binding deficit from multiple convergent operationalizations, which is what makes the central conclusion — binding is a separate, attention-gated component of VSTM — relatively robust to any single experimental choice.

## 5. Results

The principal quantitative findings:

- **Feature-change K** is comparable to Luck & Vogel's ~3–4 item capacity across feature dimensions tested in isolation.
- **Binding-change K** falls noticeably below feature-change K, with the gap widening as set size grows and as attentional demands during the delay increase. Reported differences are on the order of 1–1.5 items at set size 4–6 under loaded conditions.
- **Within-dimension competition.** When objects carried two values from the same dimension (e.g., two-color stripes), performance dropped sharply relative to one-color objects; cross-dimension combinations (color + shape) showed minimal additional cost beyond single-feature memory.
- **Articulatory suppression and concurrent attention loads** reduced binding accuracy by ~10–20% with relatively spared feature accuracy, producing a selective deficit.
- **Whole-display vs single-probe.** Single-probe tests improved binding accuracy by ~10–15% at set size 4, indicating that the cost of holding bindings is partly a cost of *resisting interference from competing bindings at test*, not only of storage.
- **Location–feature bindings** were more robust than feature–feature bindings by roughly 10% at matched set sizes, consistent with location serving as a default index.
- **Retention-interval effects.** Binding accuracy degraded faster than feature accuracy as the retention interval extended from ~100 ms to ~4 s, reinforcing the interpretation that binding maintenance is an active process that decays without ongoing attentional support.
- **Set-size scaling.** The feature–binding gap was small at set size 1–2 (where binding is essentially trivial) and grew monotonically through set size 6, consistent with a fixed-capacity binding mechanism saturating earlier than the feature stores.

(Effect sizes are approximate; the paper's primary inferential frame is significance testing on accuracy differences rather than Cowan-K point estimates. The qualitative dissociations between feature memory and binding memory are robust and have replicated repeatedly in subsequent work.)

## 6. Critique / limitations

The dissociation between feature and binding memory relies on the *binding-change* trial type being a pure test of binding. If subjects occasionally rebind during the retention interval (i.e., update their representation of which features go together), a binding-change trial may be detected as a feature-novelty trial in disguise. The estimates of binding-specific capacity are therefore lower bounds.

The "attention-demanding" claim is operationalized via concurrent-task interference. Concurrent tasks may also interfere with rehearsal, retrieval, or decision processes; the specificity of the effect to binding maintenance is inferred, not directly measured. Subsequent neuroimaging and EEG work (e.g., contralateral delay activity studies by Vogel and colleagues) has somewhat refined which part of the delay period the attentional cost is incurred in.

The framework treats binding as a binary intact/lost variable. The Schneegans–Bays (2017) population-coding account ([schneegans_bays2017_feature_binding_wm](research_db/papers/schneegans_bays2017_feature_binding_wm.md)) and the Bays continuous-resource line ([bays2024_wm_representation](research_db/papers/bays2024_wm_representation.md)) argue that binding is *graded* — bindings can be partially preserved, with feature dimensions decoupling progressively under load. Wheeler–Treisman's discrete binding-or-not analysis does not engage with this continuous degradation.

The location-privilege finding has been complicated by subsequent work. Some studies (Pertzov & Husain 2014) show that location memory is itself capacity-limited and degrades in similar ways to feature memory; others find that the location-binding advantage depends on the specifics of the encoding task. The 2002 claim that location is a uniformly privileged binding axis is too strong.

Finally, the paper predates the "discrete slots vs continuous resource" debate. It assumes a slot-like architecture in its analysis and inherits the assumption's limitations. The qualitative conclusions about attention-gated binding survive that debate, but the quantitative capacity claims should be read in light of subsequent continuous-resource models.

## 7. Connection to our work

Wheeler & Treisman 2002 is the empirical anchor for a specific claim in the user's architectural program: that *maintaining* a bound representation across a delay is not free — it is an active operation that requires an attention-like mechanism. Several implications follow.

**The recurrent ViT's binding problem.** The published recurrent ViT (arXiv:2502.10955) performs cued change detection over short delays, exactly the task family Wheeler and Treisman use. If the model's success at change detection depends on holding bound object representations across the delay, then by Wheeler–Treisman the model needs an attentional mechanism that maintains conjunctions, not just feature pools. The model's single-feedback-source self-attention layer (§6.7 of the ViT paper) is plausibly that mechanism, but the paper does not directly probe whether failures on the task are feature-loss or binding-loss errors. The Wheeler–Treisman feature-change vs binding-change contrast provides a ready-made experimental probe to apply to the model: construct test items where features change vs items where only bindings change, and measure whether the model exhibits the human dissociation. This is a concrete falsifiable test of whether the recurrent state operates by Wheeler–Treisman-style attention-gated binding.

**The Feedback Transformer as a binding mechanism.** The user's Feedback Transformer primitive integrates Q/K/V projections from multiple recurrent states via element-wise broadcasting before softmax. Mechanically, this is well-suited to *implement* exactly the attention-mediated binding maintenance Wheeler and Treisman argue for: each recurrent state $C_i$ contributes its own per-token projections, and the cross-state Hadamard product enforces conjunctive selection — a position–feature index "fires" only when multiple feedback sources jointly support it. This is the architectural rendering of Treisman's "attention as glue." If the multi-feedback variants of the recurrent ViT (the "additive" and "multiplicative" feedback of §6.7) outperform the "tokens" variant on binding-change trials in particular, that would be evidence the Hadamard structure is doing the binding work.

**PRISM v1 and the binding question.** PRISM v1's FiLM-based memory injection ([thesis_md](research_db/papers/thesis_md.md) §2.4) modulates a feature stack with a memory representation, but the modulation is at the input rather than inside the attention computation. By Wheeler–Treisman's logic, this is too weak to support binding maintenance robust against interference: there is no mechanism by which two parallel feature streams (color, shape) are bound to the same object index across the delay. PRISM v1's inner variational loop may partially compensate by iteratively re-binding, but it is not the architectural fit Wheeler–Treisman's account predicts. PRISM v2's hierarchical FiLM (`PRISM_V2_PROPOSAL.md` §3.4) is incrementally better but inherits the same fundamental limitation.

**Capacity in the multi-hub system.** Luck & Vogel ([luck_vogel1997_wm_capacity](research_db/papers/luck_vogel1997_wm_capacity.md)) gives a ~4-item object-slot capacity. Wheeler and Treisman refine this: the ~4 reflects the binding mechanism's capacity, not feature storage per se. For the user's multi-hub multi-objective system, this suggests that hub-level memory states (e.g., MSI hub feature pools) may sustain *more* than four items individually, while the *integration* of those items into bound percepts via the central self-attention competition is the genuine bottleneck. Predictions: bottleneck experiments where hubs compete for binding bandwidth should exhibit a Wheeler–Treisman dissociation — feature recall robust, binding recall fragile.

**Attention-mediated maintenance and predictive coding.** Wheeler and Treisman's attention-demanding-binding result fits naturally with the user's competition-emergent-predictive-coding thesis: holding a bound object across a delay requires *winning* the attention competition against rival representations that would re-bind the features differently. The "rebinding alternatives" in the whole-display test condition are functionally rival coalitions; binding-memory failure is a coalition losing the attention battle. This is one of the cleanest behavioral signatures the user's theory predicts.

**Experimental protocol for the recurrent ViT.** A direct port of the Wheeler–Treisman design to the recurrent ViT is straightforward: train and test the model on change-detection arrays where on a fraction of trials the changed item is a feature change and on a fraction the changed item is a binding swap. If the model shows the human dissociation (binding-change accuracy < feature-change accuracy, gap widening with set size), that is evidence the recurrent state implements something like Wheeler–Treisman binding. If the gap is absent or reversed, the model is solving the task by feature-pool memory without genuine binding — a substantively different solution from the human one. This contrast is a high-value diagnostic for the multi-hub program, since the competition-emergent-PC thesis predicts a binding-specific deficit under inter-hub conflict.

The recurrent ViT paper cites Wheeler & Treisman 2002 in its bibliography (ref [78]). Manuscripts that engage with the binding properties of the recurrent state should foreground this paper alongside Luck & Vogel 1997 and Treisman & Gelade 1980.

## 8. Citations to follow

- `treisman_gelade1980_feature_integration` — the source theory of attention-mediated binding. In seed, full depth in parallel.
- `luck_vogel1997_wm_capacity` — the object-slot capacity finding this paper refines. In seed, full depth.
- `schneegans_bays2017_feature_binding_wm` — population-coding alternative to slot-binding. In seed.
- `bays2024_wm_representation` — continuous-resource framing of binding degradation. In seed, full depth.
- `awh2006_attention_wm` — direct neural evidence for shared attention/WM mechanisms. In seed, full depth.
- `vogel_woodman_luck2001_storage_features_conjunctions` — direct EEG replication and extension of the Wheeler-Treisman binding question. Not yet in seed.
- `allen_baddeley_hitch2006_binding_attention` — Baddeley group's parallel investigation of attention-binding interactions. Not yet in seed.
- `kahneman_treisman_gibbs1992_object_files` — the "object file" construct Wheeler-Treisman invoke. Not yet in seed.
- `treisman_zhang2006_location_and_binding` — Treisman group follow-up on the location-binding-privilege claim. Not yet in seed.
- `wheeler_treisman2002` follow-ups by Allen, Baddeley & Hitch — multiple studies probing the attention-binding link across paradigms. Not yet in seed.
