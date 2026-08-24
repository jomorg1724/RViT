---
id: bays_husain2008_dynamic_resources
title: "Dynamic Shifts of Limited Working Memory Resources in Human Vision"
authors:
  - "Bays, Paul M."
  - "Husain, Masud"
year: 2008
venue: "Science"
doi: "10.1126/science.1158023"
arxiv: ""
url: "https://www.science.org/doi/10.1126/science.1158023"
tags:
  - visual-working-memory
  - resource-model
  - attention
  - eye-movements
  - delayed-estimation
  - capacity
concepts:
  - coalition_resource_competition
  - multi_compartmental_memory
  - top-down-feedback
related:
  - luck_vogel1997_wm_capacity
  - luck_vogel2013_wm_capacity_review
  - brady_tenenbaum2013_probabilistic_wm
  - bays2024_wm_representation
  - emrich2017_attention_wm_resources
  - schneegans_bays2017_feature_binding_wm
  - vanede2019_gaze_internal_wm
  - awh_jonides2001_overlapping_attention_wm
  - panichello_buschman2021_shared_mechanisms
relevance_to:
  - prism_v1
  - prism_v2
  - rvit_plus
seed_source:
  - manual_deep_dive_2026_05_23
status: full
depth: full
last_updated: "2026-05-23"
---

# Dynamic Shifts of Limited Working Memory Resources in Human Vision

## 1. Abstract

> "Our ability to remember what we have seen is very limited. Most current views characterize this limit as a fixed number of items—only four objects—that can be held in visual working memory. We show that visual memory capacity is not fixed by the number of objects, but rather is a limited resource that is shared out dynamically between all items in the visual scene. This resource can be shifted flexibly between objects, with allocation biased by selective attention and toward targets of upcoming eye movements. The proportion of resources allocated to each item determines the precision with which it is remembered, a relation that we show is governed by a simple power law, allowing quantitative estimates of resource distribution in a scene." (Bays & Husain 2008, *Science* 321(5890):851-854, abstract.)

## 2. Why this matters for us

Bays & Husain 2008 reframes VWM capacity from a *discrete slot count* (Luck & Vogel's four-item limit) to a *continuous resource* whose *allocation is governed by attention and oculomotor priority*. For the user's program, this is foundational on two fronts. First, the resource-as-shared-budget framing is the cognitive-psychology source of the user's [coalition_resource_competition](../concepts/coalition_resource_competition.md) commitment: WM is a fixed-budget resource that hubs/items compete for, and the architectural substrate that resolves the competition is *attention*. Second, the empirical demonstration that *saccade targets automatically capture a disproportionate share* of WM resource is the cleanest behavioral demonstration of *attention-mediated allocation in VWM* — a result that the user's architecture must reproduce for it to claim biological plausibility. The paper is also the theoretical pivot away from a slot-based view: any user-program architecture that allocated a fixed number of "memory slots" would inherit the slot-model's empirical problems; Bays & Husain shows that allocation should be *continuous, attention-modulated, and dynamic*, which the user's central self-attention substrate already provides.

## 3. Key claims

1. VWM capacity is not a fixed item count (~4 slots) but a continuous, shared *resource*.
2. The *precision* of memory for each item degrades smoothly as set size grows, with no discontinuity at item 4 — falsifying strict slot models.
3. Selective covert attention biases the allocation of WM resources toward attended items.
4. Targets of upcoming saccades *automatically* receive a larger share of WM resources — oculomotor priority and WM are coupled.
5. The relation between resource share and recall precision follows a *power law*, providing a closed-form prediction.
6. Resource allocation is *dynamic* — it can be re-shifted during the delay by attention or oculomotor goals.
7. "Slot" models that allow at most 3-4 items are inconsistent with continuous-precision degradation across set sizes 1-8.
8. The framework supports *parametric, quantitative predictions* about VWM performance — set size, attention, saccade target are all single-resource-budget parameters.

## 4. Methods

Two delayed-estimation experiments in healthy adults. Participants viewed brief arrays of oriented colored bars (set sizes 1, 2, 4, 6, 8) and after a delay reproduced the orientation of one cued item by adjusting a probe — yielding a *continuous error distribution* rather than the discrete change-detection or recognition responses of older paradigms. The continuous error distribution is the methodological innovation: it permits modeling recall as a precision parameter ($1/\text{SD}$) that varies parametrically with set size and attention condition, rather than as a binary in/out-of-memory variable. Attention/saccade manipulations: in some conditions one item was pre-cued by exogenous attention; in others, a saccade was made before the delay to one of the items. Errors were modeled with mixtures (target response, uniform-guessing, swap) and fit to a *power-law precision-vs-resource* function $\text{precision}(i) \propto (\text{resource}_i)^\alpha$ with the constraint $\sum_i \text{resource}_i = R$, where $R$ is total budget. The single-resource model with attention/saccade biases captures the data with few free parameters; the comparison alternative — strict 4-slot model — fails to fit the smooth degradation across set sizes.

## 5. Results

The headline quantitative results are:

- **Recall precision (1/SD of error) declined continuously with set size from 1 to 8** — no discontinuity at 4 items, falsifying the strict slot model.
- **Precision-vs-set-size data fit a power law with exponent ≈ -1** (resource scaling); the single-resource budget model captures the data parsimoniously.
- **A pre-cued attended item showed substantially higher precision** than uncued items at the same set size (≈ 2× precision improvement at uncued vs cued items).
- **Items at the target of a planned saccade had reliably higher precision** than non-saccade-target items — the oculomotor-WM coupling.
- **Even at set sizes ≤ 4, increasing set size from 1 to 4 degraded precision** — incompatible with strict 4-slot accounts where all items below capacity should be remembered with equal precision.
- **Subjects with greater attentional bias showed proportionally lower precision for unattended items, conserving total resource** — a strong test of the fixed-budget claim.
- **The model with a single resource parameter accounted for >90% of variance** across set sizes and attention conditions, demonstrating model adequacy.
- **The saccade-target benefit appeared automatically**; participants could not eliminate it via instruction — establishing the *involuntary* coupling between oculomotor priority and WM resource.

## 6. Critique / limitations

The Bays-Husain framework is foundational but has well-documented limits and contestation.

- **Restricted to one feature dimension (orientation)** in the original paper; generalization to multi-feature objects (binding) needed careful follow-up work (Bays, Catalao & Husain 2009; Schneegans & Bays 2017).
- **Does not address swap errors / non-target responses** that later mixture models (Bays, Catalao & Husain 2009; Zhang & Luck 2008) emphasize; the single-target-precision metric obscures intrusions from other items in the array.
- **Power-law fit is descriptive**; the mechanistic neural model is not specified in this paper, and the fit alone does not adjudicate among competing parameterizations.
- **Small-set-size precision improvements at $n=1$** could partly reflect perceptual rather than WM factors (better encoding, less competition for resources during *encoding*); the encoding-vs-maintenance dissociation is not directly tested.
- **Trial counts per cell are modest**; precision estimates carry non-trivial uncertainty especially at the highest set sizes.
- **The slot-vs-resource debate is not settled by this paper.** "Slots+averaging" models (Zhang & Luck 2008 *Nature*) can also fit continuous-precision data by allowing multiple slots per item, blurring the dichotomy. Adam, Vogel & Awh (2017) argue that there *are* item limits, just with continuous precision *within* the limit.
- **Attention manipulations were brief exogenous cues**; effects of *endogenous, sustained* attention on resource allocation are less directly tested.
- **Saccade-target benefit could reflect attentional capture** rather than oculomotor-specific resource allocation per se — the bare paradigm cannot fully disentangle the two contributions.

## 7. Connection to our work

Bays & Husain 2008 is one of the most architecturally consequential VWM papers for the user's program because the resource framework is *structurally homologous* to the user's coalition-competition architecture.

**Touchpoint 1: WM as fixed-budget resource — coalition competition substrate.** The paper's central claim that VWM is a *fixed budget* dynamically allocated across items is structurally identical to the user's [coalition_resource_competition](../concepts/coalition_resource_competition.md) commitment: the central self-attention substrate has a fixed budget (softmax-normalized attention weights summing to 1), and hubs/items compete for that budget. The architectural recommendation that follows is that *no hub should be given a privileged allocation*; the resource share each hub receives should be the *output* of a competitive process, not a hyperparameter input. This is exactly how the user's Feedback Transformer central attention works. The biological warrant: Bays & Husain demonstrate that this fixed-budget-with-competition organization is the empirically-correct description of WM allocation in human vision.

**Touchpoint 2: attention-mediated allocation as inter-hub Q/K manipulation.** The Bays-Husain finding that attention *modulates* the resource share each item receives — high-attention items get higher precision, low-attention items get lower — is the cognitive-psychology source of the user's central architectural mechanism: hubs modify the Q/K weights via which they compete for self-attention bandwidth ([concepts/coalition_resource_competition.md](../concepts/coalition_resource_competition.md)). The user's hubs *are* the items competing in a Bays-Husain-style resource economy; the central self-attention *is* the allocator. The architectural inference: the precision with which each hub's content is "remembered" (encoded in the next memory state) should depend on the attention weight that hub wins in the central competition, mirroring the resource-precision power law Bays & Husain identify.

**Touchpoint 3: oculomotor-WM coupling — the priority-map architectural commitment.** The paper's demonstration that *saccade targets automatically capture VWM resource* is the empirical anchor for the user's view that VWM and the priority map ([bisley_goldberg2010_parietal_priority](bisley_goldberg2010_parietal_priority.md), [bisley_mirpour2019_priority_map](bisley_mirpour2019_priority_map.md), [rust_cohen2022_priority_coding](rust_cohen2022_priority_coding.md)) share substrate. In the user's architecture, the central self-attention substrate is *simultaneously* the WM-allocation mechanism and the priority map driving covert/overt attention; the same softmax-normalized vector decides what gets stored in memory *and* what gets fixated next. This is the structural homolog of the Bays-Husain saccade-target capture finding: the architecture forces a coupling because it shares substrate.

**Touchpoint 4: precision as a probabilistic memory representation — Brady-Tenenbaum connection.** The Bays-Husain framework treats memory contents as having a *precision* (i.e., as Bayesian posteriors with varying SD) rather than as discrete items. This connects directly to [brady_tenenbaum2013_probabilistic_wm](brady_tenenbaum2013_probabilistic_wm.md): VWM should be modeled as a probabilistic representation with hierarchical priors, not as a finite set of discrete slots. The user's iterative variational encoder-decoder ([concepts/iterative_variational_encoder_decoder.md](../concepts/iterative_variational_encoder_decoder.md)) is the architectural instantiation of the probabilistic-VWM framework: the encoder produces a posterior over latent content with a learned precision, and the iterative refinement is exactly the Bayesian update over passes. The user's architecture already commits to the probabilistic-memory view; Bays-Husain is the load-bearing empirical anchor for that commitment.

**Touchpoint 5: the resource power law as a prediction for the user's models.** The Bays-Husain power law — precision scales with resource share to an exponent ~-1 — is a *specific empirical prediction* the user's architecture should reproduce. Probing the user's models in a delayed-estimation analog (multi-item display, cued recall) should show that recall precision degrades continuously with set size, that attention manipulations shift precision among items, and that the precision-resource relationship follows a power-law. If the user's architecture instead shows discrete drop-outs (an item is either remembered perfectly or not at all), it has failed to recapitulate the empirical phenomenon and the architecture needs revision. This is a *quantitative behavioral signature* the user's models should match.

**Touchpoint 6: dynamic re-allocation during the delay — implications for the gate dynamics.** Bays-Husain shows resource is *dynamically* reshiftable during the delay — late retrocues can shift precision to a newly-cued item. The architectural inference is that the user's memory update gate should not freeze during the delay; it should continue to be modulated by incoming attention signals, allowing re-allocation of memory capacity to newly-prioritized content. This is consistent with the user's choice of update-gate bias = 0 ([concepts/gridcell_rnn.md](../concepts/gridcell_rnn.md) Refinement 3): every step continues to allow re-allocation, with the central attention substrate driving which content gets the share. A frozen memory (e.g., gate bias strongly negative) would *prevent* the dynamic re-allocation Bays-Husain documents, and would therefore be the wrong architectural choice for a biologically plausible VWM model.

**Touchpoint 7: implications for the change-detection benchmark.** The recurrent ViT and PRISM are evaluated on change detection, which is functionally a low-precision-threshold version of Bays-Husain's task: the system must compare a probe to a memorized representation and report whether they differ. The Bays-Husain framework predicts that the user's models should show *graceful degradation* of change-detection sensitivity as set size grows, not a sharp drop at any particular item count. Empirically validating this signature in the user's models — measuring d' as a function of set size and finding a smooth power-law-like decline — would be a strong demonstration that the architecture has captured the resource-allocation dynamics rather than a discrete slot-like structure.

## 8. Citations to follow

- `zhang_luck2008_discrete_fixed_resolution` — *Nature* — the slots+averaging alternative model that fits much of the same data; the principal counterposition to the pure-resource view. Not in seed.
- `bays_catalao_husain2009_precision_shared` — *Journal of Vision* — the follow-up paper that adds swap errors to the mixture model. Not in seed.
- `ma_husain_bays2014_changing_concepts` — *Nature Neuroscience* — the major review covering the slot-vs-resource debate at its modern stage. Not in seed.
- `van_den_berg2012_variable_precision` — *PNAS* — variable encoding precision accounts for VSTM limitations; the variable-precision refinement of the resource model. Not in seed.
- `bays2014_neural_population_noise_wm` — *J Neurosci* — the neural-population-coding implementation of the resource model. Not in seed.
- `fougnie_suchow_alvarez2012_variability_quality` — *Nature Communications* — variability in WM quality; the precision-distribution refinement. Not in seed.
- `pertzov_bays_husain2013_retrospective_cues` — *JEP:HPP* — retrospective attention cues prevent rapid forgetting; the temporal-cue extension. Not in seed.
- [schneegans_bays2017_feature_binding_wm](schneegans_bays2017_feature_binding_wm.md) — neural architecture for feature binding in VWM; the binding extension. In seed.
- [bays2024_wm_representation](bays2024_wm_representation.md) — the modern Bays/Schneegans/Ma/Brady synthesis on representation in VWM. In seed.
- `oberauer_lin2017_interference_wm` — *Psych Review* — the interference-model alternative that subsumes resource and slot accounts. Not in seed.
- `adam_vogel_awh2017_item_limits_vwm` — *Cognitive Psychology* — "Clear evidence for item limits" — the modern slot-defense that contests the pure-resource view. Not in seed.
- [emrich2017_attention_wm_resources](emrich2017_attention_wm_resources.md) — attention mediates WM resource allocation; the attention-mediation follow-up. In seed.
- [vanede2019_gaze_internal_wm](vanede2019_gaze_internal_wm.md) — human gaze tracks attention in WM; the modern oculomotor-WM coupling follow-up. In seed.
