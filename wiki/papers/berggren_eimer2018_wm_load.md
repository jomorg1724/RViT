---
id: berggren_eimer2018_wm_load
title: "Visual Working Memory Load Disrupts Template-guided Attentional Selection during Visual Search"
authors:
  - "Berggren, Nick"
  - "Eimer, Martin"
year: 2018
venue: "Journal of Cognitive Neuroscience"
doi: "10.1162/jocn_a_01324"
arxiv: ""
url: "https://doi.org/10.1162/jocn_a_01324"
tags:
  - working-memory
  - visual-attention
  - human-neuroimaging
  - psychophysics
concepts:
  - attentional-template
  - working-memory-persistent-activity
  - cueing-effect
related:
  - awh2006_attention_wm
  - carlisle2011_attentional_templates
  - olivers2011_wm_states_attention
  - kiyonaga_egner2013_wm_internal_attention
  - panichello_buschman2021_shared_mechanisms
  - desimone1996_visual_memory_attention
  - vanmoorselaar2014_template_competition
  - bahle2018_wm_attention_architecture
  - feldman_friston2010_attention_free_energy
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_20
status: full
depth: full
last_updated: "2026-05-16"
---

# Visual Working Memory Load Disrupts Template-guided Attentional Selection during Visual Search

## 1. Abstract

The selection of relevant visual objects is controlled by *attentional templates* that represent target-defining features. Whether these templates are stored in visual working memory (vWM) or in a separate template-specific store has been a matter of theoretical debate. Berggren & Eimer probe this question by manipulating *concurrent vWM load* during a colour-defined visual search task and recording the N2pc — the lateralised ERP component that indexes attentional selection of a lateralised target — together with early visual N1 components. Across two experiments, participants memorised either *one shape* (low vWM load) or *four shapes* (high vWM load) and then performed an interleaved visual search task in which targets were defined by either *two possible colours* (i.e., a multi-feature attentional template) or a *single constant colour* (i.e., a singleton template). When targets were defined by two colours, *target N2pc components were delayed and attenuated under high vWM load*, and behavioural search RTs were slowed; these effects were not observed for single-colour targets. Early visual N1 components were also attenuated by high load, and the magnitude of this N1 attenuation predicted individual vWM accuracy. Berggren & Eimer conclude that multi-feature attentional templates are *actively maintained in vWM* and consume the same limited-capacity store as the concurrently maintained shape memoranda, whereas single-feature templates can be supported by a separate (likely LTM-based) store that is unaffected by concurrent vWM load.

## 2. Why this matters for us

The recurrent ViT and PRISM commit, architecturally, to a *single substrate* — the recurrent memory state $H^{(t)}$ or $M_t$ — that does double duty as working memory and as the source of top-down attentional guidance. The Awh-Vogel-Oh 2006 and Kiyonaga-Egner 2013 reviews catalogue this unification at the level of cognitive theory; Panichello-Buschman 2021 demonstrate it at the level of single-unit PFC dynamics. Berggren-Eimer 2018 supply the *causal-behavioural* evidence for this unification: when one part of vWM is loaded with shape memoranda, the very same store can no longer hold a multi-feature attentional template effectively, so attentional selection (indexed by the N2pc) degrades. This is precisely the prediction the user's architectural commitment makes: load on the memory state should propagate to degradation of the attention map. The paper is the load-bearing behavioural-neural citation for treating the recurrent ViT's $H^{(t)}$ capacity as a *shared* resource between maintenance and selection.

## 3. Key claims

1. **Multi-feature attentional templates are held in vWM.** When targets are defined by two colours, holding four shapes concurrently impairs both the speed and the EEG signature of attentional target selection.
2. **Single-feature templates are not held in vWM.** When the target colour is constant across trials, concurrent vWM load has no detectable effect on N2pc or RT, implying that constant templates have been off-loaded to LTM (cf. Carlisle et al. 2011's CDA decrease over repetitions).
3. **vWM-attention sharing is template-specific, not generic.** The cost of vWM load is on target-related selection, not on a generic perceptual deficit; it scales with the *featural complexity* of the search template.
4. **Early visual processing is also load-modulated.** Visual N1 components over posterior electrodes are attenuated under high load, and N1 attenuation correlates with individual vWM performance — evidence that the load reaches as early as object-perceptual stages.
5. **Capacity is shared, not parallel.** The single-substrate prediction is favoured over models with a dedicated, capacity-independent template store (the "template-store separate from vWM" account).
6. **The N2pc is a sensitive online index of template-guided selection.** N2pc latency / amplitude tracks the *quality* of template engagement on a trial-by-trial basis, complementing the CDA's index of template *maintenance*.

## 4. Methods

Two ERP experiments using a dual-task design that interleaves a vWM memory task with a visual search task.

**Participants.** Healthy adults (typical N ≈ 16–20 per experiment for ERP studies of this type).

**Trial structure.** On each trial, participants first memorise a shape array (one shape in low-load blocks; four shapes in high-load blocks) for a delay period. During the delay they perform a *visual search task*: identify the orientation of a small line inside a coloured target item embedded in a search array. After the search, a probe shape is presented and participants report whether it matches an item in the memorised shape set.

**Target template manipulation.** In *multi-colour* (variable template) blocks, the search target is defined by one of *two possible colours* on each trial; the participant must hold both colours as the template. In *single-colour* (constant template) blocks, the target is a fixed colour throughout the block.

**EEG.** Dense-array EEG, with primary analyses on the *N2pc* (≈ 200–300 ms post-stimulus, posterior contralateral minus ipsilateral to the target) as the index of template-guided attentional selection. Secondary analyses on the *N1* (≈ 150–200 ms, bilateral posterior) as an index of early visual processing.

**Design logic.** vWM load (low vs high) × template type (multi-colour vs single-colour) is the critical 2 × 2. If templates are held in vWM, load should impair N2pc only for multi-colour templates. If templates have a dedicated store outside vWM, load should not impair N2pc in either condition.

## 5. Results

**Behaviour — multi-colour blocks.** Search RTs were significantly slowed under high vs low vWM load, with errors more frequent. Memory probe accuracy was reduced in the high-load condition, as expected.

**N2pc — multi-colour blocks.** Target N2pc was *delayed in onset* and *reduced in amplitude* under high vWM load, indicating that the attentional template was less effective in driving lateralised selection when the same store was loaded with shape memoranda.

**Behaviour and N2pc — single-colour blocks.** Neither RTs, accuracy, nor N2pc latency/amplitude differed reliably between low- and high-load conditions, replicating the prediction that constant templates are supported by a store that does not share capacity with vWM.

**N1.** Posterior visual N1 was attenuated under high load in both template conditions. The magnitude of the N1 attenuation correlated with individual vWM accuracy: participants whose N1 was most attenuated by load were also those whose memory performance suffered most. This suggests load reaches early visual cortex, possibly via reduced sensory gain when capacity is consumed elsewhere.

**Interaction.** The critical statistical signature is the *vWM load × template type* interaction on N2pc — present and significant — and on RT, also significant.

Specific numerical effect sizes are reported in the paper; the qualitative pattern is robust enough that the multi-vs-single template dissociation is the headline result.

## 6. Critique / limitations

The paper rests on a *null result* for the single-colour condition — the conclusion that constant templates leave vWM relies on not detecting a load effect when one is searched for. ERP null results with modest sample sizes should be treated with appropriate uncertainty; the dissociation is suggestive rather than definitive.

The "two possible colours" manipulation conflates *template complexity* with *template variability* across trials. A two-colour template that is *constant* across trials would distinguish whether vWM load impairs the holding of *more featural information* per se, or the holding of *variable template content* across trials. The paper cannot fully separate these accounts.

The shape memoranda are *categorically different* from the colour template (shapes vs colours). If there were genuinely segregated stores for shape vWM and colour vWM, the load effect would not be expected — yet it is found. The authors take this as evidence for a *generic* vWM store shared across features; an alternative reading is that some other central resource (attention itself; central-executive control) is the bottleneck, not feature-specific vWM.

The N1 attenuation finding is intriguing but the paper does not strongly mechanistically interpret it. Whether N1 attenuation reflects a top-down gain reduction, a competition for selection resources, or a sensory consequence of WM load remains under-determined.

The paper does not engage with predictive-coding accounts. The Friston/free-energy interpretation — that WM load reduces *precision* available for sensory target gain — would map naturally onto the N1 result, but is not discussed.

The N2pc index is restricted to *lateralised* targets; central, foveal, or RSVP-style attentional selection cannot be assessed with this measure. Generalising to spatially-broader template engagement requires further work.

## 7. Connection to our work

Berggren-Eimer 2018 is the *direct experimental demonstration* of the WM-attention shared-resource claim that the user's architectural program treats as axiomatic. Its connections to our work are concrete and load-bearing.

**Direct evidence for WM-attention shared resource.** The paper demonstrates *causally* (via a load manipulation) that increasing demand on visual WM degrades template-guided attentional selection. This is the strongest behavioural-neural evidence in the database for the unification commitment that anchors the recurrent ViT's single-state design. Awh-Vogel-Oh 2006 ([awh2006_attention_wm](research_db/papers/awh2006_attention_wm.md)) catalogue this interaction descriptively; Olivers et al. 2011 ([olivers2011_wm_states_attention](research_db/papers/olivers2011_wm_states_attention.md)) supply the active-accessory state distinction that motivates a *single* active template; Kiyonaga & Egner 2013 ([kiyonaga_egner2013_wm_internal_attention](research_db/papers/kiyonaga_egner2013_wm_internal_attention.md)) supply the theoretical unification ("WM is internal attention"); Panichello & Buschman 2021 ([panichello_buschman2021_shared_mechanisms](research_db/papers/panichello_buschman2021_shared_mechanisms.md)) confirm the unification at the level of PFC single-unit codes; Desimone 1996 ([desimone1996_visual_memory_attention](research_db/papers/desimone1996_visual_memory_attention.md)) supplies the biased-competition substrate. Berggren-Eimer 2018 is the *behavioural-causal* layer of this evidentiary stack.

**Capacity prediction for the recurrent ViT.** The recurrent ViT (2502.10955, §6.7) maintains a single state $H^{(t)}$ whose dimensionality is fixed. Berggren-Eimer's load-dependent N2pc impairment predicts that, in the recurrent ViT, *increasing the number of items the model is asked to track* should *degrade the attention map's selectivity* for the cued target — and that this degradation should be most evident for *multi-feature templates* (e.g., colour-and-shape conjunction targets) rather than for single-feature ones. This is a falsifiable test of the architectural commitment: train the model on dual-task variants of change-detection where one slot of $H^{(t)}$ is loaded with concurrent memoranda and measure attention-map sharpness for the cued target as a function of load.

**Multi-vs-single template dissociation and PRISM.** Berggren-Eimer's finding that single-feature templates are not load-sensitive supports the Carlisle et al. 2011 ([carlisle2011_attentional_templates](research_db/papers/carlisle2011_attentional_templates.md)) WM→LTM handoff: with sufficient repetition, a constant template moves out of vWM. For PRISM v1 (THESIS.md §2.4), this predicts an interesting training-dynamics asymmetry: tasks with constant templates (e.g., always search for red) should require *less* recurrent-state capacity over training as the template is "learned into the weights," whereas tasks with variable templates should *persistently* tax the recurrent state. PRISM v1's prediction-error-driven attention is well-suited to capture the constant-template case (the prediction errors are stably generated); the variable-template case is where PRISM v1's lack of explicit WM may be a weakness relative to the recurrent ViT.

**Connection to the Feedback Transformer primitive.** The user's Feedback Transformer (`threads/the_user_architectural_program.md` §1) integrates multiple recurrent feedback sources into a single attention computation. Berggren-Eimer's finding that load on one cognitive content (shape memoranda) degrades attention to *another* content (colour-defined targets) is consistent with the Feedback Transformer's design: when multiple memory states project into one attention map, they share a finite communication bandwidth (the Q/K inner-product space). The user's architectural intuition that "rival hubs compete for the self-attention map" (`competition-emergent-predictive-coding`) is the architectural-level version of Berggren-Eimer's behavioural-level cross-content interference.

**Empirical bridging test.** A direct cognitive-neuroscience analogue of the recurrent ViT could be run by training the model on a dual task that mirrors Berggren-Eimer's design — concurrent shape memorisation plus colour-defined visual search — and asking whether N2pc-like signatures (e.g., a measure of contralateral attention-map activation following target onset) are degraded under high concurrent load. The recurrent ViT's architectural commitment predicts that they should be, and that the degradation should be specific to multi-feature (i.e., dimensionality-consuming) templates.

**N1 attenuation as early gain effect.** The Berggren-Eimer N1 finding parallels the predictive-coding interpretation of attention as precision-weighting (Feldman & Friston 2010 [feldman_friston2010_attention_free_energy](research_db/papers/feldman_friston2010_attention_free_energy.md)). If precision is a finite resource and WM maintenance consumes some, then less precision is available for early sensory channels — explaining the N1 attenuation. The user's program is compatible with this; the recurrent ViT's feedback into low-level features (PRISM v2's hierarchical FiLM) is the architectural mechanism for the same effect.

**Relationship to Olivers' active-accessory distinction.** Olivers et al. 2011's claim that only *one* item is in the active "attentional-template" state at any time predicts the Berggren-Eimer pattern at the cognitive-architectural level: under high vWM load, four shape memoranda compete with the colour template for the single active slot. The template is intermittently displaced, and on trials where it is not active the attention selection process is slowed — explaining the delayed and attenuated N2pc. In the recurrent ViT, this maps onto the proposal that $H^{(t)}$ has a distinguished low-dimensional subspace that drives the attention map; high-dimensional WM content uses *other* subspaces but compete with the template subspace for the dimensionality budget. The Olivers ↔ Berggren-Eimer pairing thus jointly motivates a design where the recurrent state has an *explicit* template subspace and a *separate* accessory subspace, with controlled bandwidth between them.

**Relationship to van Moorselaar's template-competition finding.** Van Moorselaar et al. 2014 ([vanmoorselaar2014_template_competition](research_db/papers/vanmoorselaar2014_template_competition.md)) showed that *two* templates can be maintained simultaneously but only one is active for attention at a time. Berggren-Eimer extend this by showing that even when *one* template is sufficient for the search task, the *complexity* of that template (two colours vs one) modulates how badly it is impaired by unrelated WM load. The two papers together imply: the template store has a small, fixed, content-addressable capacity, and the more featural content per template, the more capacity it consumes — exactly the prediction one would make if templates and memoranda share a single dimensionality budget.

## 8. Citations to follow

- `soto2005_wm_capture_attention` — original behavioural demonstration that WM contents capture attention; foundational for Berggren-Eimer's framing.
- `eimer1996_n2pc_origin` — Eimer's original N2pc papers, the methodological foundation for using the N2pc as an attentional-selection index. Worth a stub.
- `woodman_arita_luck2007_template_specificity` — earlier work from the Woodman lab on whether attentional templates are in WM, predecessor to Carlisle 2011.
- `vogel_machizawa2004_cda` — origin of the CDA as the WM-maintenance ERP index, complementary to N2pc.
- `dube_emrich2025_template_vwm_neural` — recent reviews of the template-in-vWM debate that incorporate Berggren-Eimer's results.
- `hakim2019_dissociable_neural_signals_wm` — combined CDA / N2pc work distinguishing maintenance from selection, follow-up to Carlisle.
- `gunseli2014_template_specificity` — N2pc evidence that templates sharpen with task demands; complements the multi/single-template dissociation here.
- `reinhart_woodman2014_causal_template_lpfc` — TMS / tDCS evidence that lateral PFC is causally necessary for template-based search; the candidate substrate for the shared store Berggren-Eimer infer behaviourally.
- `berggren_eimer2018_space_based_companion` — Berggren & Eimer's companion 2018 paper showing the same load disrupts the *space-based* guidance of selection, generalising the finding beyond colour templates.
