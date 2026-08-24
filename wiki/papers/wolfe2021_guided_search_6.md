---
id: wolfe2021_guided_search_6
title: "Guided Search 6.0: An updated model of visual search"
authors:
  - "Wolfe, Jeremy M."
year: 2021
venue: "Psychonomic Bulletin & Review"
doi: "10.3758/s13423-020-01859-9"
arxiv: ""
url: "https://doi.org/10.3758/s13423-020-01859-9"
tags:
  - visual-attention
  - psychophysics
  - theoretical-essay
  - review
concepts:
  - attentional-template
  - priority-map
  - signal-detection-theory
  - drift-diffusion-model
  - top-down-feedback
  - working-memory-persistent-activity
related:
  - itti_koch2001_saliency_review
  - bisley_goldberg2010_parietal_priority
  - bundesen2005_neural_theory_attention
  - desimone_duncan1995_biased_competition
  - olivers2011_wm_states_attention
  - lemeur2006_coherent_attention
  - treisman_gelade1980_feature_integration
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_99
status: full
depth: full
last_updated: "2026-05-16"
---

# Guided Search 6.0: An updated model of visual search

## 1. Abstract

This paper describes Guided Search 6.0 (GS6), a revised model of visual search. When we encounter a scene, we can see *something* everywhere. However, we cannot recognize more than a few items at a time. Attention is used to select items so that their features can be "bound" into recognizable objects. Attention is "guided" so that items can be processed in an intelligent order. In GS6, this guidance comes from five sources of preattentive information: (1) top-down and (2) bottom-up feature guidance, (3) prior history (e.g., priming), (4) reward, and (5) scene syntax and semantics. These signals combine in a dynamic priority map that selects an item every ~50 ms; each selected item is processed by an asynchronous diffusion stage that accumulates evidence toward a target or distractor boundary and toward an adaptive quitting threshold. GS6 unifies the family of Guided Search models (1989, 1994, 2007, 2017) with two decades of psychophysics on history, value, and scene-based guidance, and it issues quantitative predictions for reaction-time slopes and error rates across set sizes and target-presence conditions.

## 2. Why this matters for us

GS6 is the canonical behavioral model of visual search and the most authoritative single-paper specification of the *functional architecture* the Recurrent ViT and PRISM are implicitly competing with. Its core construct — a priority map fed by parallel preattentive feature channels and read out by a serial selection mechanism that updates a template-based decision — is the cognitive-science antecedent of the recurrent ViT's iterate-and-attend loop and of PRISM's slow-fast memory split. The five sources of guidance map onto distinct memory channels in our architectures: top-down templates → working-memory feedback into self-attention; selection history → slow memory; scene syntax → contextual priors; bottom-up salience → bottom-up sensory projection. GS6 is also the standard against which any neural model of *human* search behavior will be evaluated on RT slopes, error rates, and quitting times. If a recurrent ViT cannot reproduce the qualitative signatures GS6 catalogues — shallow slopes for guided search, steep slopes for serial search, set-size-dependent miss rates, ≈3:1 absent/present slope ratios — it has not captured the behavior.

## 3. Key claims

1. **Visual search is guided, not exhaustive.** Items are selected in an order biased by preattentive guidance signals; truly random serial search is the limit case, not the default.
2. **Guidance has five sources.** Top-down feature guidance, bottom-up feature guidance, prior history (priming, contextual cueing), value/reward, and scene syntax + semantics. Each is preattentive and each contributes additively (in log-odds) to a shared priority map.
3. **Selection is driven by a dynamic priority map.** The map represents the system's current best guess for where to deploy attention next; the highest-activation location wins and is sampled approximately every 50 ms (≈20 Hz).
4. **Attentional templates live in activated long-term memory (ALTM), not just working memory.** Working memory holds at most one currently guiding template; ALTM stores additional templates and provides them when context demands.
5. **Recognition is a diffusion process.** Each selected item accumulates evidence toward a target boundary or a distractor boundary at a rate of ≈1/20 of the bound distance per step, yielding ≥150 ms per item and ≈200 ms in noise-free recognition.
6. **Search is "carwash" parallel.** Up to ≈5 items can be in the diffusion stage simultaneously, asynchronously initiated at 50 ms intervals — selection is serial, identification is overlapping.
7. **Quitting is a second diffusion to an adaptive threshold.** A separate accumulator races to an absent-decision bound whose height adapts to recent feedback (correct rejections lower it; misses raise it).
8. **Preattentive features are coarse, not fine.** Guidance uses categorical or ≥10–15° orientation differences, not 0.5° discriminations; this is why "steepest line" is found pre-attentively but "slightly steeper line" is not.
9. **Three functional visual fields constrain selection.** A high-resolution field, a covert-attention field, and an overt-saccade field each set independent limits on what can be selected at a given moment.
10. **Limited inhibition-of-return memory.** Only ≈4–6 previously rejected distractors are tagged as visited; this finite memory predicts the empirical ≈3:1 absent-to-present RT-slope ratio.

## 4. Methods

GS6 is a theoretical synthesis paper with an explicit computational specification rather than a new behavioral experiment. The paper builds a single integrated model and verifies it against the cumulative record of visual-search psychophysics from the Wolfe lab and others over 1989–2020.

The computational core: at each time-step ($\Delta t \approx 50$ ms) the system evaluates a priority map

$$
P(x, t) = \sum_{f} w_f^{TD}(t)\, F_f(x) + \sum_{f} w_f^{BU}\, F_f(x) + H(x, t) + V(x) + S(x \mid \text{scene})
$$

where $F_f$ is the preattentive feature signal at location $x$ in channel $f$ (color, orientation, motion, size, depth, …), $w_f^{TD}$ is the top-down template weight on channel $f$ (potentially modulated by the active ALTM template), $w_f^{BU}$ is the bottom-up salience weight, $H(x,t)$ aggregates history (priming, IOR, contextual cueing), $V(x)$ is value/reward, and $S(x \mid \text{scene})$ is the scene-prior contribution. The argmax of $P$ is the next selection target. Once selected, item $i$ enters a Wiener diffusion $E_i(t)$ with drift toward the target or distractor bound; up to five items diffuse simultaneously. A parallel quitting accumulator $Q(t)$ races to an absent-decision threshold whose height is updated trial-to-trial by reinforcement-learning-like feedback.

The empirical anchor is a corpus of search experiments: feature search (color, orientation), conjunction search (color × orientation), categorical search (animals among non-animals), and scene-context search.

## 5. Results

The model issues quantitative predictions matched to the empirical corpus:

- **Selection cadence.** ≈20 Hz (one new item every 50 ms), consistent with the ≈100–150 ms minimum attention-dwell times observed in the rhythmic-attention literature.
- **Per-item identification.** ≥150 ms minimum; ≈200 ms in noise-free conditions. Combined with the 50 ms selection interval and ≤5 concurrent diffusers, this yields the canonical 25–50 ms/item RT slope for inefficient search.
- **Carwash parallelism.** Five-item asynchronous diffusion is required to reproduce the observed RT slopes; serial diffusion is too slow, fully parallel is too fast.
- **Absent/present slope ratio.** ≈3:1 (vs. the 2:1 predicted by perfect-memory serial models), explained by limited (4–6 item) IOR memory that lets the search occasionally revisit rejected items in absent trials.
- **Guidance threshold.** Orientation guidance requires ≥10–15° differences; below that, search becomes inefficient even when the difference is perceptually discriminable.
- **Scene effects.** Search slopes drop sharply when scene context narrows the priority map to a region (e.g., looking for a teapot on a counter, not the ceiling).
- **History effects.** Priming on color reduces RTs by ≈50–100 ms across trials; contextual cueing improves slopes by ≈30% over training.

## 6. Critique / limitations

GS6 is a *functional* model, not a neural one. It specifies what computations the brain must perform but is silent on where they happen or how neurons implement them. The mapping from the priority map onto LIP (Bisley & Goldberg 2010), FEF, pulvinar, or SC is left open. This is appropriate for a behavioral synthesis but means GS6 cannot itself adjudicate neural-substrate questions.

The five guidance sources are added to a single priority map by hand-tuned weights. The model does not specify *how* those weights are learned or how they trade off when in conflict. Subsequent work on attentional weighting (e.g., Bundesen's TVA) supplies formal weighting machinery that GS6 does not include.

The diffusion stage uses standard Wiener-process assumptions; the drift rate and bound parameters are fit, not derived. The carwash-of-five assumption is empirically motivated but mechanistically unexplained — why five, not three or seven?

Scene guidance is treated as a single $S(x \mid \text{scene})$ term without committing to its computational form. The recent surge in deep-network scene models (e.g., DeepGaze, Itti-Koch-derived saliency, GIST-based priors) has many candidate implementations; GS6 endorses none specifically.

The model is largely about *target search*, not *change detection* or *free viewing*. The recurrent ViT and PRISM operate primarily in change-detection regimes where the "target" is defined by temporal mismatch rather than feature template; GS6 does not directly cover this case, although the priority-map machinery transfers naturally.

Finally, GS6 inherits a long-standing concern with Guided Search: the line between "preattentive feature" and "attended object" is the load-bearing assumption of the framework, and that line is increasingly blurred by demonstrations that even "attended" recognition has parallel components (Wolfe's own carwash assumption is a partial concession to this).

## 7. Connection to our work

GS6 is the *behavioral* counterpart to the user's architectural program — the cognitive-science model whose functional commitments any neural-substrate model must ultimately reproduce.

**The priority map is the recurrent ViT's attention map.** GS6's $P(x, t)$ over time is structurally equivalent to the recurrent ViT's per-step self-attention map: a spatial distribution that selects which token receives processing on the next step. The five GS6 sources of guidance correspond directly to the bias signals the Feedback Transformer ([feedback_transformer](research_db/concepts/feedback_transformer.md)) integrates: bottom-up sensory ($s_{q,i}$), top-down memory ($c^{(k)}_{q,i}$ from working memory), history (slow memory in PRISM v2), and scene priors (contextual hubs in the multi-hub architecture). GS6 commits to a *summation* in priority space; the Feedback Transformer commits to a *Hadamard product* in Q/K space prior to softmax. The functional content is the same; the Feedback Transformer is the multiplicative analog of GS6's additive priority map.

**Attentional templates are PRISM's ConvGRU and the recurrent ViT's $H^{(t-1)}$.** GS6 distinguishes a single guiding template in working memory from many templates in ALTM. PRISM v1's ConvGRU working-memory state ([THESIS.md](Prism/docs/THESIS.md) §2.4) is the architectural analog of GS6's WM template: a single, fast-updating, currently-active state that biases attention. PRISM v2's slow memory ([PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3) is the analog of ALTM: a longer-timescale store that supplies context-dependent template content to the fast pathway. GS6's WM-vs-ALTM split is, in our terms, the slow-fast memory split.

**Selection history → slow memory channel.** GS6's history term $H(x, t)$ aggregates priming (recent target features), inhibition-of-return (recent rejections), and contextual cueing (slow associations between context and target location). All three are dual-timescale: priming is fast (trial-to-trial); contextual cueing is slow (across training); IOR is intermediate (within-trial). PRISM v2's slow memory is precisely the architectural commitment that lets the model carry information across the kind of timescales GS6 needs for $H$ to work.

**Iterate-and-attend ≈ ≈20 Hz selection cadence.** GS6's 50 ms selection interval — one new item every 50 ms with up to five concurrent diffusers — is the behavioral counterpart of the recurrent ViT's per-step attention update. The "carwash" architecture (asynchronous start, overlapping processing) is the conceptual ancestor of the recurrent-iteration-with-memory pattern: at each step the system commits to a new selection while still holding evidence from previous selections in memory. Reproducing this empirical signature is a concrete falsification target for the recurrent ViT.

**GS6, biased competition, priority maps, TVA, saliency: a coherent literature ring.** GS6 sits at the center of a tight set of cited works: it is the behavioral synthesis; [desimone_duncan1995_biased_competition](research_db/papers/desimone_duncan1995_biased_competition.md) is the neural-mechanism account of how the priority map's bias gets implemented at the receptive-field level; [bisley_goldberg2010_parietal_priority](research_db/papers/bisley_goldberg2010_parietal_priority.md) is the neural substrate of the priority map in LIP; [bundesen2005_neural_theory_attention](research_db/papers/bundesen2005_neural_theory_attention.md) is the formal weighting calculus (TVA) for the multiple guidance terms; [itti_koch2001_saliency_review](research_db/papers/itti_koch2001_saliency_review.md) is the canonical computational instantiation of the bottom-up feature-guidance term; [olivers2011_wm_states_attention](research_db/papers/olivers2011_wm_states_attention.md) elaborates the WM-template-as-bias claim into a more nuanced active-vs-accessory account; [lemeur2006_coherent_attention](research_db/papers/lemeur2006_coherent_attention.md) supplies the engineering side of the bottom-up + top-down + scene-prior synthesis for free-viewing prediction. GS6 is the integration paper whose components we have already entered into the database individually.

**Quantitative falsification targets.** A recurrent-ViT-as-search model should produce: (i) ≈25–50 ms/item RT-slope analog for inefficient search; (ii) ≈3:1 absent/present slope ratio; (iii) ≈20 Hz selection cadence; (iv) ≥150 ms minimum per-item identification time when noise is added; (v) qualitatively shallower slopes when a feature template is supplied as memory; (vi) qualitatively shallower slopes when scene priors are supplied. These are the GS6 signatures any computational model of human-like search must reproduce, and they are the right benchmarks for a behavioral validation of the architectural program.

## 8. Citations to follow

- `treisman_gelade1980_feature_integration` — the original FIT paper from which Guided Search descends. In seed, full depth.
- `wolfe1989_guided_search` — GS1, the founding paper of the Wolfe lineage. Not yet in seed.
- `wolfe1994_guided_search2` — GS2, introduces the priority-map structure. Not yet in seed.
- `wolfe2007_guided_search4` — GS4, the immediate predecessor. Not yet in seed.
- `wolfe2017_five_factors` — Wolfe & Horowitz, the five sources of guidance review. Not yet in seed; should be added as a seed for the "five guidance sources" claim.
- `chun_jiang1998_contextual_cueing` — the contextual-cueing paradigm cited heavily in GS6's scene-syntax discussion. Not yet in seed.
- `awh_belopolsky_theeuwes2012_top_down_bottom_up_dichotomy` — the history-as-third-source argument GS6 endorses. Not yet in seed.
- `anderson2011_value_driven_attention` — empirical basis for the reward/value guidance term. Not yet in seed.
- `vo_wolfe2013_scene_grammar` — scene-syntax mechanisms cited in the GS6 scene-guidance term. Not yet in seed.
- `henderson2003_eye_movements_scenes` — eye-movement-in-scenes literature underlying the exploratory FVF. Not yet in seed.
- `nakayama_martini2011_situating_visual_search` — a critique of Guided Search worth tracking. Not yet in seed.
- `eckstein2011_visual_search_review` — Bayesian-search alternative framework. Not yet in seed.
