---
id: meyerhoff2017_mot_review
title: "Studying visual attention using the multiple object tracking paradigm: A tutorial review"
authors:
  - "Meyerhoff, Hauke S."
  - "Papenmeier, Frank"
  - "Huff, Markus"
year: 2017
venue: "Attention, Perception, & Psychophysics"
doi: "10.3758/s13414-017-1338-1"
arxiv: ""
url: "https://doi.org/10.3758/s13414-017-1338-1"
tags:
  - visual-attention
  - psychophysics
  - review
concepts:
  - signal-detection-theory
related:
  - bettencourt_somers2009_mot
  - luck_vogel2013_wm_capacity_review
  - bays2024_wm_representation
  - awh2006_attention_wm
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_105
status: full
depth: full
last_updated: "2026-05-15"
---

# Studying visual attention using the multiple object tracking paradigm: A tutorial review

## 1. Abstract

The multiple object tracking (MOT) paradigm, introduced by Pylyshyn and Storm (1988), has become a workhorse for studying the dynamics of distributed visual attention.

In the canonical task, an observer is shown a set of identical objects, a subset of which is briefly cued as targets; all objects then move along independent trajectories for several seconds while the observer holds the target identities in mind, after which the observer reports which objects were targets. Performance robustly drops with the number of targets tracked, the speed of motion, the density of objects, and the duration of the trial — establishing MOT as a sensitive probe of the *capacity*, *resolution*, and *temporal dynamics* of attention distributed across multiple spatiotemporal locations.

This tutorial review synthesizes three decades of MOT research, covering: classical capacity findings (~4 targets); the discrete-slot vs. flexible-resource debate; target–distractor confusion as the primary error mode; the role of feature information for individuation; hemifield independence; the interaction between tracking and working memory; the relationship between MOT and the related multiple-identity-tracking (MIT) paradigm; and methodological recommendations (stimulus design, dependent measures, signal-detection analysis, and modelling pitfalls). The review is intended as a starting point both for researchers new to the paradigm and for theorists seeking a clean behavioral assay of multifocal attention.

## 2. Why this matters for us

MOT is the canonical psychophysical paradigm that *directly probes whether attention can be distributed across multiple spatial loci simultaneously* — the exact computational property a transformer-style attention map can express trivially (multi-head, multi-peak softmax) but that classical "spotlight" theories of attention denied.

For the Recurrent ViT, which is trained on change-detection but whose attention map must learn to maintain coverage over multiple to-be-monitored items across time, MOT is the behavioral benchmark against which the model's multi-focus capability should be validated. The review also crystallizes the *resource vs. slot* debate within the MOT literature, directly paralleling the WM debates in Luck & Vogel 2013 and Bays 2024 — and supplying a second, motion-based test bed for resolving it.

## 3. Key claims

1. **MOT capacity is ~4 targets** under standard conditions, replicating across labs, stimuli, and decades; capacity degrades smoothly with target count, speed, density, and trial duration rather than dropping abruptly at a hard ceiling.
2. **Capacity is not fixed but graded.** Capacity estimates depend on speed, spacing, and feature heterogeneity; an "infinitely divisible flexible resource" account fits the speed/density manipulations better than a strict slot account in many studies, while a hybrid account (a finite number of object indexes whose precision varies with resources) reconciles much of the data.
3. **Target–distractor confusion is the dominant error mode** rather than complete loss of tracking. Errors cluster near close encounters between targets and distractors, implicating *spatial resolution* of attention as the limiting factor — the system loses *which* object was a target rather than losing the object entirely.
4. **Feature information is used opportunistically.** Although the canonical task uses identical objects, observers exploit any available featural cue (color, shape, surface markings) to re-individuate targets after occlusion or close encounters, improving capacity above the feature-blind baseline. This is the empirical hook for the multiple-identity-tracking (MIT) variant.
5. **MOT taps both attention and working memory.** Dual-task interference shows tracking shares resources with visual WM and with attentional control; tracking load reduces concurrent change-detection sensitivity, and concurrent WM load reduces tracking capacity.
6. **Hemifield resources are partially independent.** Capacity is roughly additive across hemifields, suggesting two hemisphere-specific tracking pools rather than a single global pool — a finding with direct implications for any biologically inspired computational model.
7. **Methodological recommendations.** Report partial-credit and signal-detection-style measures rather than raw accuracy; control density and speed independently (they confound); avoid ceiling/floor effects via adaptive procedures; report capacity estimates with confidence intervals appropriate for within- vs. between-subject manipulations.
8. **MOT is a behavioral assay for theories of multi-focal attention** — any computational model that posits a single attentional spotlight predicts catastrophic failure on MOT, whereas multi-focus or object-based accounts predict the graceful degradation actually observed.

## 4. Methods

The paper is a narrative tutorial review, not a primary empirical study. It is organized around five strands:

- **A taxonomy of MOT task variants.** Classical 2-D MOT (Pylyshyn & Storm 1988); 3-D MOT (objects on receding/approaching trajectories, Tinjust et al.); MOT with occluders (objects disappear behind opaque surfaces and must be re-acquired); MOTS — multiple object tracking with surface features that change during the trial; and MIT — multiple identity tracking, where each object has a unique label that must be maintained throughout motion.
- **A walk-through of dependent measures.** Proportion correct on the probe report; the capacity estimate *K* (e.g., Hulleman's correction $K = N \cdot (2p - 1)$ for two-alternative report); partial-credit scoring; hit-rate / false-alarm-rate decomposition; signal-detection-theoretic $d'$ on target/distractor probes; and proximity-to-distractor analyses of error trials that diagnose *where* in the trajectory tracking failed.
- **A review of the principal experimental manipulations.** Target number (typically 1–6), object speed (deg/s), density (objects per unit area or mean inter-object distance), trial duration (1–15 s typical), occlusion frequency and duration, identity-report vs. location-report at probe, and whether targets and distractors are distinguishable on features alone.
- **A discussion of competing theoretical accounts.** Multifocal-attention / FINST theory (Pylyshyn — a fixed set of 4–5 pre-attentive indexes); flexible-resource accounts (Alvarez & Franconeri — a continuously divisible pool of attention); object-based and grouping accounts (the system tracks emergent virtual polygons whose vertices are the targets); oculomotor accounts (covert tracking is parasitic on the saccade system); and probabilistic/Bayesian accounts (MOT is approximate posterior inference over object trajectories under uncertainty).
- **Methodological appendix-style guidance.** Stimulus generation in Psychophysics Toolbox / PsychoPy; motion-trajectory constraints (avoiding inter-object collisions while still producing close encounters); avoidance of ceiling/floor effects via adaptive procedures; appropriate baselines for assessing chance performance with varying numbers of targets and distractors; and pitfalls in cross-condition capacity comparisons when underlying difficulty is not equated.

## 5. Results

The review consolidates the following quantitative regularities from the MOT literature:

- **Capacity K ≈ 4 targets** under standard conditions (8 objects total, moderate speed, identical featureless disks on a uniform background); the finding replicates Pylyshyn & Storm 1988 across labs, decades, and populations.
- **K decreases with speed.** Alvarez & Franconeri (2007) show $K$ varies continuously from ~8 (slow speeds) down to ~1 (fast speeds) within individual observers, arguing for flexible-resource rather than fixed-slot accounts.
- **K decreases with density / inter-object spacing.** Franconeri et al. (2008, 2010) find that capacity is principally limited by the *closest-approach distance* between targets and distractors during the trial, not by absolute target count. Equating closest-approach across conditions largely abolishes the speed effect.
- **Error analyses concentrate near close encounters.** Proximity-to-distractor at the moment of probe predicts error probability; "swap" errors (a tracked target is reported as a nearby distractor that crossed paths with it) account for the majority of mistakes.
- **Feature heterogeneity helps but does not eliminate confusion.** Adding distinguishing features (color, shape, surface markings) improves tracking modestly, but observers do not rely on features alone — spatiotemporal trajectory remains the primary mechanism, and tracking persists even with featurally identical items.
- **Hemifield independence.** Cavanagh & Alvarez (2005) and Alvarez & Cavanagh (2005) show that left- and right-hemifield tracking pools are largely independent — capacity for 2 targets in each hemifield exceeds capacity for 4 targets in one hemifield, implicating hemisphere-specific attention resources.
- **Dual-task costs.** Concurrent visual WM tasks reduce tracking capacity by 1–2 items; tracking reduces concurrent change-detection sensitivity ($d'$). The dual-task cost is asymmetric, often larger when WM is the secondary task.
- **Individual differences.** Tracking capacity correlates with fluid intelligence and with visual WM capacity (consistent with Luck & Vogel 2013), but the correlations are modest ($r \approx 0.3$–$0.5$), suggesting partially separable systems and a tracking-specific component beyond general capacity.

## 6. Critique / limitations

**Resource-vs.-slot ambivalence.** The review is descriptive rather than synthetic on the resource-vs.-slot question; the authors do not advance a strong theoretical position, leaving the reader to weigh competing accounts. Subsequent modelling work (Vul, Alvarez, Tenenbaum & Black 2009; Srivastava & Vul 2016) frames MOT as Bayesian-tracking-under-uncertainty, where the apparent "capacity" is the noise floor of the inferred trajectories — a framing that subsumes both slot and resource accounts as limiting cases, and that the review does not engage in depth.

**Stimulus restriction.** Most cited results use 2-D screen displays with point-mass objects on featureless backgrounds. Generalization to natural scenes, ecological motion (Meyerhoff & Huff 2013 on biological motion), and crowded real-world tracking (e.g., crowd surveillance, sports broadcasting) is less well established. The features that real-world tracking can exploit — occlusion cues, depth ordering, kinematic regularities — are largely absent from the canonical paradigm.

**MIT vs. MOT relationship.** The review focuses on tracking *position* identity. The closely related multiple-identity-tracking (MIT) paradigm, where each object has a distinct feature label that must be maintained throughout motion, is treated more briefly; the relationship between MOT capacity and MIT capacity — and the extent to which the two reflect a common underlying limit — is a substantive open question that subsequent literature (Oksama & Hyönä 2008; Horowitz et al. 2007) has continued to debate.

**Neural underspecification.** The neural substrate is mentioned only briefly. The Bettencourt & Somers 2009 work and the broader IPS / FEF literature on MOT are cited but not synthesized into a neural-network-level account that could constrain computational models. The role of the dorsal-attention network (FEF, IPS) versus the ventral-attention network in MOT remains an open question.

**Pre-deep-learning vintage.** The review is pre-2017; it does not engage with deep-learning-era tracking models (DeepSORT-family, object-centric slot models like Locatello et al.'s Slot Attention, transformer-based multi-object trackers) which have since become natural computational substrates against which to compare human MOT. The promised computational-cognitive bridge — using MOT as a benchmark for object-centric deep models — has matured substantially after this review.

**No explicit attention-map prediction.** Because the review predates dense attention-map probes of deep models, it does not articulate the prediction that should govern a model-vs.-human MOT comparison: namely, that the attention map should exhibit multi-peak structure during tracking, with the peaks centered on (but slightly lagging) target locations. This prediction has to be imported from the broader covert-attention literature when designing a model benchmark.

## 7. Connection to our work

This review is the **methodological standard for testing distributed attention** in the user's program and the most direct behavioral analog to the Recurrent ViT's attention-map dynamics on change-detection tasks.

**MOT directly tests the multi-focus capability of the recurrent ViT's attention map.** The single-head transformer attention used in the published Recurrent ViT (2502.10955) produces a softmax-normalized map that, in principle, can place mass at multiple locations simultaneously — this is the property MOT was invented to test in humans.

If the Recurrent ViT is presented with an MOT-style sequence (multiple cued targets among distractors, common motion), its attention map should track multiple loci. Whether it actually does so — and whether its capacity degrades with target count, speed, and density in the same way human capacity does — is a near-zero-cost behavioral test for the model that has not yet been run. This is a natural follow-up experiment to the change-detection benchmark.

A direct prediction: under the Feedback Transformer (`the_user_architectural_program` §1) with hierarchical descending feedback, capacity should *exceed* that of a single-layer attention model because deeper layers with larger receptive fields can maintain identity through close encounters that defeat a single fine-grained tracker. This is testable.

**The resource vs. slot debate in MOT parallels the WM debates.** Luck & Vogel 2013 ([luck_vogel2013_wm_capacity_review](research_db/papers/luck_vogel2013_wm_capacity_review.md)) endorses discrete slots; Bays 2024 ([bays2024_wm_representation](research_db/papers/bays2024_wm_representation.md)) endorses continuous resources. MOT's Alvarez–Franconeri speed-capacity tradeoff is one of the strongest pieces of evidence for the flexible-resource side. For the Recurrent ViT, whose recurrent state is continuous-valued, the *flexible-resource* interpretation maps naturally onto the model's behavior: target count and motion speed should trade off continuously, not in step-function form. MOT thus offers an independent test of which side of the debate the model's behavior lands on.

**MOT response variability is informative about the recurrent ViT's attention noise structure.** Swap errors — reporting a nearby distractor as a target — are the modal error type in human MOT. If the Recurrent ViT exhibits the same error structure (attention drifting from a target to a spatially proximal distractor), this is direct evidence that the model's attention map has human-like spatial resolution and noise properties. If instead the model exhibits "total loss" errors (attention to neither target nor neighboring distractor), the model's failure mode differs qualitatively from human attention — diagnostic for architectural improvements.

**Connection to** [bettencourt_somers2009_mot](research_db/papers/bettencourt_somers2009_mot.md): Bettencourt & Somers identify target enhancement and distractor suppression as separable mechanisms, with distinct fMRI signatures. The Feedback Transformer architecture (`the_user_architectural_program` §1) can implement both: top-down feedback can up-weight target-feature dimensions in K/V while a separate gain channel suppresses distractor-feature dimensions. MOT is the behavioral handle for asking whether the model has independently parameterized both.

**Connection to** [awh2006_attention_wm](research_db/papers/awh2006_attention_wm.md): Awh, Vogel & Oh argue attention and WM are deeply intertwined. MOT — which requires simultaneous tracking (attention) and maintaining the target/non-target distinction (WM) — is one of the cleanest paradigms for studying that interaction. PRISM v1's inner-inference loop and the Recurrent ViT's recurrent state both formally couple attention and WM; MOT is the appropriate behavioral test bed.

**Signal-detection-theory framing.** The review emphasizes hit/false-alarm decomposition over raw proportion correct. Any computational comparison between human MOT and Recurrent ViT MOT should use the same $d'$ framing rather than accuracy alone — this is a methodological prescription the review supplies directly. For the user's program, applying SDT to model behavior also disentangles two failure modes that raw accuracy conflates: degraded *sensitivity* (the model cannot tell targets from distractors at the moment of probe) versus a shifted *criterion* (the model is biased toward "is a target" or "is a distractor" responses). The former indicates a representational failure; the latter, a decision-rule failure that is addressable without changing the underlying attention mechanism.

**Density / speed as continuous control parameters.** The Franconeri closest-approach finding implies that the appropriate independent variable in a model-vs.-human comparison is *minimum inter-object distance at moments of probe*, not target count alone. This is a re-parameterization the Recurrent ViT MOT benchmark should adopt from the outset; otherwise nominally identical "4-target" trials are not actually comparable.

**Tutorial framing as a research-database asset.** Because this paper is a tutorial review rather than a primary study, its highest-value contribution to the database is methodological: it provides the canonical reading list (Pylyshyn & Storm; Alvarez & Franconeri; Franconeri et al.; Scholl & Pylyshyn; Vul et al.; Cavanagh & Alvarez) that should be added as stubs and elevated as the user's behavioral-validation program matures.

## 8. Citations to follow

- `pylyshyn_storm1988_mot` — the founding MOT paper; FINST theory. Not yet in seed.
- `alvarez_franconeri2007_flexible_tracking` — speed-capacity tradeoff, central evidence for flexible-resource account. Not yet in seed.
- `franconeri2008_tracking_density` — closest-approach as the actual capacity limit. Not yet in seed.
- `vul_alvarez_tenenbaum_black2009_bayesian_mot` — Bayesian-tracking model that subsumes slot and resource accounts. Not yet in seed.
- `scholl_pylyshyn1999_tracking_visible` — object-file theory of MOT. Not yet in seed.
- `oksama_hyona2008_mit` — multiple identity tracking. Not yet in seed.
- `cavanagh_alvarez2005_tracking_multiple` — review predecessor; tracking as a hemispherically-independent resource. Not yet in seed.
- `meyerhoff_huff2013_biological_motion_mot` — naturalistic-motion MOT. Not yet in seed.
- `srivastava_vul2016_mot_bayesian` — modern Bayesian tracking account. Not yet in seed.
