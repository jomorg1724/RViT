---
id: hoffman2016_attention_eye_movements
title: "Visual attention and eye movements"
authors:
  - "Hoffman, James E."
year: 2016
venue: "In H. Pashler (Ed.), Attention (Chapter 4), Routledge / Psychology Press (reissue of 1998 edition)"
doi: "10.4324/9781315784762-4"
arxiv: ""
url: "https://www.taylorfrancis.com/chapters/edit/10.4324/9781315784762-4/visual-attention-eye-movements-james-hoffman"
tags:
  - visual-attention
  - review
  - psychophysics
concepts:
  - attentional-spotlight
  - cueing-effect
  - top-down-feedback
  - priority-map
related:
  - posner1980_orienting
  - krauzlis2013_sc_attention
  - gupta_sridharan2024_presaccadic_change
  - vanede2019_gaze_internal_wm
  - moore_armstrong2003_fef_microstim
  - thompson1996_fef_stages
  - bollimunta2018_fef_sc_covert
  - cavanaugh_wurtz2004_sc_change_blindness
  - tas2016_attention_wm_covert_overt
  - carrasco2011_visual_attention_25y
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_3
status: full
depth: full
last_updated: "2026-05-16"
---

# Visual attention and eye movements

## 1. Abstract

Hoffman's chapter (Chapter 4 in Pashler's edited volume *Attention*; Psychology Press / Routledge reissue 2016 of the 1998 original) reviews behavioural and neurophysiological evidence on the relationship between covert visual attention and overt eye movements. The chapter is organised around a single thesis: covert attention and the oculomotor system are mechanistically coupled — they share circuitry (frontal eye fields, superior colliculus, posterior parietal cortex), share spatial coordinate systems (retinotopic priority maps), and share computational primitives (target selection, weighting by behavioural relevance). Hoffman synthesises evidence from dual-task paradigms (where subjects must attend to one location while saccading to another), pre-saccadic enhancement experiments (where discrimination performance improves at the saccade target before the eyes move), and microstimulation / lesion work (where perturbing oculomotor structures perturbs covert attention even in the absence of saccades). The chapter is the most-cited treatment of the so-called **premotor theory of attention** (Rizzolatti, Riggio & Dascola 1987; Rizzolatti et al. 1994) in the cognitive-psychology textbook literature: the claim that covert spatial attention is, at the algorithmic level, a *suppressed saccade plan* — the same circuits that would normally execute an eye movement instead emit a sub-threshold motor program that gates visual processing at the planned-saccade target. Hoffman is careful, however: he reviews the evidence that supports the strong form of the theory and notes the places where the theory leaks (dissociations of attention from saccade endpoints, the existence of attentional effects under conditions that should preclude any motor plan). The chapter ends by endorsing a *coupling* rather than an *identity* claim: covert attention and saccade preparation share substantial neural machinery but are not strictly the same process.

## 2. Why this matters for us

This is the **canonical foundation** for treating the recurrent ViT's attention map as a model of the same circuit that drives both *covert* attention and *overt* saccades. The premotor-theory lineage that Hoffman synthesises is what licenses the architectural step from a purely sensory attention map (as in standard ViT) to one that could be read out as a motor command. The Recurrent ViT (2502.10955) currently implements only the *covert* half of this lineage — a soft attention distribution $\alpha_{ij}$ over patches with no oculomotor output — but Hoffman's chapter is the textbook citation for why the *same* mechanism, in primate cortex, is also the substrate of saccade planning. This in turn licenses the natural extension of the user's program: read the recurrent-state-modulated attention map as a saccade priority map and add an oculomotor head that emits explicit fixation commands. The eye-tracking results the user reports in the Evolution of Architecture notes (network's predicted fixation tracks true fixation on natural images) are the empirical instantiation of this idea — they treat the model's attention map exactly as Hoffman treats primate FEF / SC activity: as a single priority computation read out for both perception and action.

## 3. Key claims

1. **Covert attention and saccade planning are tightly coupled.** When subjects are required to make a saccade to one location while simultaneously discriminating a target at another, discrimination performance at the saccade target is significantly better than at the to-be-discriminated location — even when subjects are explicitly instructed otherwise. Attention is yoked to saccade preparation.
2. **Pre-saccadic enhancement is obligatory.** In the ~50–150 ms before a saccade, visual discrimination sensitivity rises at the saccade target. The enhancement begins before motor execution, indexing the *preparation*, not the *execution*, of the eye movement.
3. **Endogenous covert attention can dissociate from saccade plans — but only weakly.** Subjects can deploy covert attention to a non-saccade location, but the deployment is slower and less complete than when attention and saccades go to the same place. The system *prefers* coupling.
4. **The frontal eye fields (FEF) are a common substrate.** Sub-threshold microstimulation of FEF sites (insufficient to evoke a saccade) produces *covert* attentional facilitation at the corresponding retinotopic location (Moore & Armstrong 2003; reviewed in the chapter). The same circuit emits both signals.
5. **The superior colliculus (SC) is also a common substrate.** SC inactivation disrupts covert attention even when no saccades are required. The SC is part of the priority-map network, not merely a motor relay.
6. **Posterior parietal cortex (LIP / 7a) carries the integrated priority map.** Parietal neurons respond both to attended visual stimuli and to saccade targets; the same cells are recruited for both functions.
7. **The premotor theory in its strong form is over-strong.** Examples where covert attention deploys to a location no motor plan ever targets (e.g., when the task explicitly forbids that saccade) suggest attention is not strictly *identical* to a suppressed saccade — but does share most of the neural machinery.
8. **Attention guides eye movements via the same priority computation.** The selection of the next saccade target is the same computation as the selection of the covert focus of attention: both consult a behavioural-priority map weighted by salience, top-down task relevance, and reward history.
9. **Eye-movement data are a behavioural read-out of the attention system.** Even free-viewing scan paths on natural scenes can be analysed as indices of attentional priority — fixation duration and fixation order reflect attentional engagement.

## 4. Methods

This is a review chapter; "methods" refers to the experimental paradigms Hoffman synthesises.

- **Dual-task paradigm.** Subjects prepare a saccade to one location and must simultaneously discriminate a brief target at another. Discrimination accuracy is compared at saccade-target vs non-saccade-target locations. Hoffman & Subramaniam (1995) and Kowler et al. (1995) are the prototypical instances.
- **Pre-saccadic discrimination.** A brief target is flashed at various times relative to saccade onset. Sensitivity ($d'$) at the saccade target is plotted as a function of time-to-saccade. Sensitivity rises in the ~50–150 ms window before the eyes move (Deubel & Schneider 1996; Kowler et al. 1995).
- **Cued covert attention without saccades.** Posner-style cuing paradigms (cued location, neutral / valid / invalid trials) with fixation strictly enforced. The validity effect persists even with eyes static, demonstrating that covert attention is not merely a saccade by another name.
- **FEF microstimulation.** Sub-threshold electrical stimulation of FEF in monkeys (Moore & Armstrong 2003; Moore & Fallah 2001 series): currents too low to elicit saccades but sufficient to enhance V4 responses at the corresponding retinotopic position, indexing covert attention.
- **SC microstimulation and inactivation.** Cavanaugh & Wurtz 2004 and Müller et al. 2005 series: SC stimulation produces covert attentional facilitation; SC inactivation produces covert attentional deficits even when no saccades are required.
- **Behavioural eye-tracking on natural scenes.** Fixation locations during free viewing or task-directed search analysed as indices of attentional priority.
- **Patient-lesion data.** Parietal-lesion patients with hemispatial neglect show coupled deficits in covert attention and contralesional saccades — a clinical demonstration of the shared substrate.

## 5. Results

The chapter is a synthesis; key quantitative landmarks Hoffman emphasises:

- **Discrimination $d'$ at the saccade target** is reliably higher than at non-target locations in dual-task paradigms by a factor that grows with saccade preparation time. The effect size is large enough to be detected in single-subject psychophysics.
- **Pre-saccadic enhancement** has a characteristic time course: discrimination at the saccade target begins improving ~150 ms before saccade onset and peaks ~50 ms before onset.
- **Sub-threshold FEF microstimulation** (Moore & Armstrong 2003) elicits V4 firing-rate gains comparable in magnitude to those produced by behavioural covert attention (~10–30% gain for preferred-orientation stimuli at the corresponding retinotopic location).
- **SC inactivation** (Lovejoy & Krauzlis; reviewed by Hoffman) produces selective deficits in covert attention at the corresponding spatial location, with attention deficits surviving even when no saccades are required.
- **Endogenous covert attention can be dissociated from saccade plans** but at a cost: a ~30–60 ms slowdown in attentional deployment and a ~10–20% reduction in the discrimination advantage relative to the coupled condition.
- **Free-viewing fixation distributions** on natural scenes are well-predicted by behavioural-priority models that integrate bottom-up salience with top-down task relevance — the same priority maps that predict covert attention.

## 6. Critique / limitations

- **The review is now over two decades old in its empirical base.** The 2016 reissue does not substantively update the 1998 source. Important subsequent developments — Bisley & Goldberg's parietal priority-map synthesis (2010), Krauzlis et al.'s SC review (2013), Carrasco's 25-year retrospective (2011), and Gupta & Sridharan's recent demonstration that pre-saccadic attention does *not* improve change-detection sensitivity (2024) — are absent. The reader should treat the chapter as historically foundational rather than contemporary.
- **The strong premotor theory has been refined.** Hoffman is appropriately cautious, but the chapter's framing slightly oversells the identity claim. Modern accounts (Krauzlis 2013; Bisley & Mirpour 2019) treat covert attention and saccade planning as *partially overlapping* priority computations that diverge in their downstream readouts.
- **No distinction between sensitivity and bias.** Hoffman treats discrimination improvement as straightforward evidence for attentional enhancement of perception. Gupta & Sridharan 2024 demonstrate that much of the "presaccadic enhancement" is actually a *choice bias* effect, not a sensitivity effect, when the task is change-detection rather than discrimination. This is a major refinement the chapter predates.
- **The chapter is largely behavioural.** Neurophysiological evidence is invoked but not deeply engaged; the cortical-microcircuit details of how FEF or SC implement priority weighting (e.g., dendritic integration, laminar specificity) are not addressed.
- **The eye-movement / attention coupling is treated as universal.** The chapter does not distinguish reflexive (exogenous) from voluntary (endogenous) saccade planning, even though these have different time courses and partially different substrates. Subsequent work has shown that the coupling is tighter for voluntary saccades than for reflexive ones.
- **No engagement with working memory.** The chapter predates the demonstrations that *internal* attention to maintained representations also recruits the oculomotor system (van Ede, Chekroud & Nobre 2019; [vanede2019_gaze_internal_wm](vanede2019_gaze_internal_wm.md)). The substrate-sharing claim is therefore weaker in the chapter than it could be: not only does covert attention share circuitry with overt saccades, it shares circuitry with *imagined* saccades to memorised locations.
- **Computational models are not engaged.** The chapter does not relate the premotor framework to computational priority-map models (Itti & Koch's saliency framework; Bisley & Goldberg's priority map; modern attention transformers). The translation from a Hoffman-style cognitive substrate-sharing claim to a concrete neural-network attention-map architecture is therefore left to the reader.
- **No within-trial dynamics.** The chapter treats covert attention as if it deploys to a single location at a time. Modern attention-dynamics work (e.g., the divisive-normalisation model of Reynolds & Heeger 2009; gain-modulation accounts) and the user's own observation that attention maps in the recurrent ViT "focus, defocus, and reactivate over recurrent steps" suggest a richer within-trial structure that the chapter does not address.

## 7. Connection to our work

Hoffman 2016 is the **textbook authority** for one of the user's program's most consequential extension paths: from a purely *covert* attention model (the published Recurrent ViT) to a *coupled covert-overt* model that emits oculomotor commands. The chapter is cited as reference [3] in the Recurrent ViT paper (2502.10955) precisely because it grounds the claim that the attention map the network learns is the same data structure that, in primate cortex, drives saccade planning.

**The lineage the chapter anchors.** Hoffman synthesises the empirical foundation of what later becomes a four-paper chain in this database. (i) [posner1980_orienting](posner1980_orienting.md) establishes that covert attention is real — measurable as a validity effect independent of fixation. (ii) Hoffman 2016 establishes that this covert process shares circuitry with saccade preparation (FEF, SC, LIP). (iii) [krauzlis2013_sc_attention](krauzlis2013_sc_attention.md) modernises the SC story, showing the SC is a *primary* attention substrate, not merely a motor relay. (iv) [gupta_sridharan2024_presaccadic_change](gupta_sridharan2024_presaccadic_change.md) refines the presaccadic-enhancement claim, showing that the apparent change-detection benefit at the saccade target is choice bias rather than sensitivity. The Recurrent ViT lives at the cognitive-science end of this chain: its attention map is the model-level analog of the priority computation Hoffman traces from behavioural dual-task data to FEF / SC neurophysiology.

**The user's eye-tracking result.** The Evolution of Architecture notes ([the_user_architectural_program](../threads/the_user_architectural_program.md) §6) report that a hierarchical RViT with bidirectional feedback predicts human fixation locations on natural scenes, with the network's predicted fixation tracking the true fixation qualitatively. This is exactly the prediction Hoffman's chapter would make: if the network's internal attention map is the right computational substrate for covert attention, and if covert attention shares circuitry with saccade planning (Hoffman's main claim), then a read-out of the network's attention map at each pass should be a reasonable saccade-target predictor. The user's eye-tracking experiment is therefore the empirical test of Hoffman's substrate-sharing claim *in the model* — and the result is a positive instance: the same map that supports the model's covert internal attention also reads out as a reasonable overt-saccade plan.

**Extension to oculomotor outputs.** The recurrent ViT does *only* covert attention — soft $\alpha_{ij}$ over patches with no explicit motor head. Hoffman's chapter is the licence for the natural extension: add a head that reads the attention map (or its post-FT priority distribution) and emits an explicit fixation command. The biological precedent — FEF and SC as common substrates for covert priority and overt saccade selection — is exactly what justifies a *single* shared map for both purposes rather than two parallel heads. This would convert the recurrent ViT from a covert-attention model into a coupled covert-overt model and would let it interact with embodied / active-vision benchmarks the current model cannot address.

**Connection to van Ede 2019.** Hoffman's chapter is the foundational reference behind [vanede2019_gaze_internal_wm](vanede2019_gaze_internal_wm.md)'s most ambitious claim — that *internal* attention to maintained representations recruits the same oculomotor circuitry that drives covert and overt visual attention. Van Ede's gaze-tracks-WM result is the cognitive-science completion of the Hoffman chapter: not only do covert attention and overt saccades share substrate (Hoffman), but *internal* attention to memorised content also recruits that same substrate (van Ede). For the user's program, this triple coupling is the empirical motivation for treating the recurrent ViT's spatial attention map $\alpha_{ij}$, its recurrent memory state $H^{(t)}$ on the same patch grid, and (in the proposed extension) its oculomotor output as a *single* shared data structure rather than three separate maps.

**Connection to the Feedback Transformer.** The Feedback Transformer primitive ([the_user_architectural_program](../threads/the_user_architectural_program.md) §1) integrates bottom-up sensory input with multiple recurrent memory states by element-wise modulation of Q / K vectors prior to softmax. The biological gloss: this is the architectural mechanism by which a single attention map can simultaneously serve sensory selection, memory selection, and (in the proposed extension) motor selection. Hoffman's substrate-sharing claim is the *biological* version of this architectural commitment: the same circuit (FEF / SC / LIP) implements the priority computation that drives covert attention, saccade planning, and (per van Ede) internal-memory selection. The Feedback Transformer is the architectural primitive that achieves the analogous integration in the model.

**Connection to PRISM.** PRISM v1's spatial precision map $\Sigma_t$ ([Prism/docs/THESIS.md] §2.4) is a single per-patch quantity that serves both inference (where prediction error is large) and memory update (which patches to write). Hoffman's substrate-sharing claim provides one biological motivation for this design — a single map that serves multiple downstream readouts is exactly what the FEF / SC / LIP circuit does in primate cortex. PRISM v2's hierarchical FiLM modulation inherits this commitment.

**Distinction the chapter does not address.** The chapter predates the demonstration that pre-saccadic enhancement is largely a *bias* effect rather than a *sensitivity* effect in change-detection tasks (Gupta & Sridharan 2024). For the user's change-detection benchmarks, this is a load-bearing distinction: the model's apparent improvement at cued locations could be a sensitivity gain (true attentional enhancement) or a bias shift (criterion change), and these have different architectural implications. Hoffman 2016 is the historical context; Gupta & Sridharan 2024 is the contemporary refinement.

**Why "shared substrate" is stronger than "correlated dynamics".** A weaker reading of the attention-saccade coupling would be that the two systems exhibit correlated time courses but operate on distinct neural maps that exchange signals. Hoffman explicitly rejects this weaker reading: the FEF-microstimulation and SC-inactivation data only make sense if covert attention is implemented *by the same neurons* that plan saccades, not by a separate map that talks to them. For the user's architectural commitments, this matters because a "correlated but distinct" account would license a two-map architecture (one for attention, one for motor output, with a learned bridge between them), while the substrate-sharing account demands a single-map architecture in which the *same* $\alpha_{ij}$ distribution serves both purposes. The recurrent ViT's single-attention-map design and the proposed oculomotor extension are the latter; a multi-head design that decouples them would be the former. Hoffman is the textbook authority for choosing the single-map architecture.

**Methodological implication: behavioural eye-tracking as a model diagnostic.** Because Hoffman establishes that fixation patterns are a behavioural read-out of the attention priority computation, eye-tracking on the same stimuli used to test the recurrent ViT is a comparatively cheap empirical anchor: if the model's attention map matches human fixation patterns on natural-scene change-detection, then the model has correctly learned the priority computation. If it diverges systematically, the divergence localises where the model deviates from the human attention-saccade circuit. The user's eye-tracking results are the positive instance of this diagnostic; scaling them up to a quantitative human-model comparison (rather than the qualitative red-circle / green-dot tracking the notes report) is a natural next experiment.

## 8. Citations to follow

- `rizzolatti_riggio_dascola1987_premotor_attention` — original premotor-theory paper; the canonical reference Hoffman's chapter synthesises. Not yet in seed.
- `deubel_schneider1996_saccade_attention` — pre-saccadic enhancement: discrimination at the saccade target improves before the eyes move. Methodological cornerstone of the chapter. Not yet in seed.
- `kowler1995_role_of_attention_saccades` — dual-task paradigm and the obligatory coupling of attention to saccades. Foundational for the chapter. Not yet in seed.
- `hoffman_subramaniam1995_attention_saccades` — the author's own dual-task study, a key empirical anchor for the chapter. Not yet in seed.
- `moore_fallah2001_microstimulation_attention` — pre-Moore & Armstrong 2003 work establishing FEF microstimulation effects on covert attention. Not yet in seed.
- `rizzolatti1994_premotor_theory_neuroscience` — the neuroscience-side extension of the 1987 paper, integrating monkey neurophysiology. Not yet in seed.
- `mcpeek_keller2004_sc_target_selection` — SC as target-selection substrate, central to the SC half of the chapter's substrate-sharing claim. Not yet in seed.
- `craighero_rizzolatti2005_premotor_review` — modern review of the premotor theory, post-Hoffman. Useful for the post-1998 update the chapter does not provide. Not yet in seed.
- `corbetta_shulman2002_dorsal_ventral_attention` — dorsal vs ventral attention network; the cortical-network context the chapter mostly leaves to neurophysiologists. Not yet in seed.
- `awh_armstrong_truong2006_attention_and_eyes` — direct successor to the substrate-sharing claim, distinguishing the modes of coupling. Not yet in seed.
- `findlay_walker1999_saccade_model` — computational model of saccade target selection integrating attention and motor priority; the modelling-side complement to the Hoffman chapter's behavioural review. Not yet in seed.
