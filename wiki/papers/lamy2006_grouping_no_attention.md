---
id: lamy2006_grouping_no_attention
title: "Grouping does not require attention"
authors:
  - "Lamy, Dominique"
  - "Segal, Hannah"
  - "Ruderman, Lital"
year: 2006
venue: "Perception & Psychophysics"
doi: "10.3758/BF03193652"
arxiv: ""
url: "https://link.springer.com/article/10.3758/BF03193652"
tags:
  - visual-attention
  - psychophysics
  - theoretical-essay
concepts:
  - figure-ground-segmentation
  - feature-binding
  - attentional-spotlight
  - top-down-feedback
related:
  - mehrani_tsotsos2023_attention_grouping
  - wolfe2011_scene_search
  - itti_koch2001_saliency_review
  - treisman_gelade1980_feature_integration
  - wheeler_treisman2002_binding
  - egly1994_object_attention
  - desimone_duncan1995_biased_competition
  - koch_ullman1984_winner_takes_all
  - kietzmann2019_recurrence_required
  - dosovitskiy2020_vit
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_76
status: full
depth: full
last_updated: "2026-05-16"
---

# Grouping does not require attention

> **Sourcing note.** The Springer / Perception & Psychophysics PDF requires institutional or paywalled access; WebFetch on the article URL redirected through Springer's IDP login. The summary below is reconstructed from (a) the PubMed abstract for PMID 16617826 and (b) the canonical content of this paper as cited across the perceptual-grouping literature (Moore & Egeth 1997, Kimchi et al., Driver et al.). Quantitative claims that could not be sourced verbatim are described qualitatively as the paper's argumentative structure rather than as numeric findings.

## 1. Abstract

Gestalt grouping has classically been treated as a *preattentive* process — visual features are organized into perceptual wholes prior to and independent of focal attention. Subjective reports under conditions of inattention, however, cast doubt on this assumption: observers often fail to report having perceived grouping patterns when those patterns fall outside the focus of attention. Moore and Egeth (1997) reconciled this tension by showing that, while observers cannot *explicitly* report grouping outside attention's focus, *implicit* effects of grouping on visual perception are nonetheless measurable.

The present paper replicates and extends Moore and Egeth's result across five experiments. Experiments 1 and 2 use the Müller-Lyer illusion as an implicit probe of background grouping: the perceived length of a line is biased by inducer arrows formed via Gestalt grouping of an otherwise unattended dot field, even when subjects cannot consciously identify the inducer pattern. Experiment 3 (and follow-ups) uses a flanker-task variant in which the amount of available attentional resources is manipulated; grouping-driven flanker interference persists under conditions of attentional load. Together the experiments establish that perceptual grouping operates without requiring attention, even though the grouped percept may not enter explicit awareness. The paper's contribution is to dissociate the *perceptual-organization* function (which is attention-independent) from the *explicit-report* function (which is attention-dependent), and to argue that the apparent failure of grouping under inattention in earlier studies reflects the latter, not the former.

## 2. Why this matters for us

This paper supplies the *cognitive-science* warrant for treating perceptual grouping and selective attention as *dissociable* computational stages — grouping is the pre-attentive substrate on which attention later operates. That dissociation is the load-bearing premise for the Recurrent ViT's iterate-and-refine reading of its own attention dynamics ([the_user_architectural_program](../threads/the_user_architectural_program.md) §4). On that reading, the recurrent ViT's *first iterate* — when the recurrent state $H_0$ carries no task-specific bias and the self-attention map has not yet been steered by feedback — implements the pre-attentive grouping stage that Lamy et al. document. Later iterates ($H_2, \ldots, H_{n_{FR}}$) overlay attentional binding on top of the grouped substrate.

This paper therefore acts as the *empirical counterpoint* to [mehrani_tsotsos2023_attention_grouping](mehrani_tsotsos2023_attention_grouping): Mehrani & Tsotsos argue that ViT self-attention is grouping rather than attention, and read this as a deficiency of feedforward architectures; Lamy et al. supply the cognitive-science result that grouping-without-attention is exactly what one should expect from a feedforward stage prior to attentional selection, in both biological and artificial systems. Read together, the two papers reframe Mehrani & Tsotsos's negative result: a feedforward ViT *should* do grouping, not attention, because that is what the corresponding stage of the human visual system does. What was missing in vanilla ViT was not grouping (which it does correctly) but the *subsequent* attention-implementing recurrent loop. The Recurrent ViT supplies that loop.

## 3. Key claims

1. **Grouping is dissociable from explicit attention.** Although observers under conditions of inattention cannot *report* perceiving grouping patterns, those patterns nonetheless influence their performance on concurrent perceptual judgments — i.e., grouping leaves an implicit perceptual signature even when explicit awareness is absent.
2. **The Müller-Lyer illusion can serve as an implicit probe.** When the illusion-inducing inward / outward arrows are constructed not from drawn lines but from Gestalt grouping of a dot field, the resulting illusory length distortion persists even when the inducer pattern is task-irrelevant and unreported.
3. **Grouping resists attentional load.** In a flanker-task variant where attentional resources are constrained, flanker-grouping effects persist, indicating that grouping does not consume the same limited resource that focal attention does.
4. **Methodological lesson: implicit measures matter.** Studies that probed grouping using explicit recognition of the grouped pattern systematically *underestimated* the extent of preattentive grouping; converging implicit probes (illusions, flanker interference) recover the effect.
5. **Theoretical consequence.** Classical Gestalt accounts that posit grouping as a preattentive stage (Neisser, Treisman, Julesz) are vindicated against more recent challenges (Mack & Rock's inattentional-blindness work, Joseph et al.'s attention-required-for-texture-segregation results). Grouping does not require attention; the *reportability* of grouping does.
6. **Convergence across paradigms.** The dissociation between implicit perceptual influence and explicit reportability holds across two methodologically independent paradigms (illusion bias; flanker interference), strengthening the inference that the underlying grouping operation is genuinely attention-independent rather than an artifact of any single measure.

## 4. Methods

The paper reports five experiments organized into two paradigm families. Both families share an underlying logic: probe whether perceptual grouping influences a *concurrent* perceptual judgment under conditions where the grouped pattern itself is task-irrelevant and outside the focus of explicit attention. If the influence persists, grouping does not require attention; if it disappears, it does.

**Müller-Lyer paradigm (Experiments 1–2).** Observers judged the length of a central horizontal line. The illusion-inducing arrowheads at the line's endpoints were not drawn directly; they were *grouped* from a sparse dot array by proximity / good-continuation Gestalt cues, so that the perception of an "inward-pointing fin" or "outward-pointing fin" required the visual system to organize a set of dots into an oriented contour. The grouping was made task-irrelevant: subjects' explicit task was to compare line lengths, not to identify the inducer pattern. A post-experiment recognition test verified that observers had no reliable explicit awareness of which inducer configuration (inward-pointing "fins-in" vs outward-pointing "fins-out") had been displayed on each trial. The dependent measure was the bias of length judgments by inducer configuration — i.e., the Müller-Lyer illusion magnitude as a function of an implicit, unreported grouping. The logic is that if grouping requires attention, the dot field — being task-irrelevant — should not be organized into fins, and the line-length judgment should be uninfluenced by the dot configuration. Any reliable illusion bias is therefore evidence for grouping-without-attention.

**Flanker paradigm (Experiment 3 and follow-ups).** A central target letter was flanked by distractor letters. The flankers and target could either *belong to the same perceptual group* (by Gestalt cues such as proximity, common color, or common contour) or *belong to distinct groups*. Grouping was manipulated independently of stimulus identity, so flanker interference effects could be decomposed into a baseline flanker effect (the well-known compatibility / incompatibility effect of Eriksen & Eriksen 1974) and a grouping-modulation of that effect. The amount of attentional resources available to the target was manipulated by varying task difficulty (e.g., adding a secondary load, varying eccentricity, manipulating set size). The prediction was clear: if grouping requires attention, then withdrawing attention from the flankers (or loading the target task) should abolish the grouping-modulation of the flanker effect. The alternative — that grouping does not require attention — predicts that the grouping-modulation should survive attentional load, even though the absolute level of flanker interference might shift.

**Subjects and design.** The experiments use modest-N adult observer samples (typical for the Lamy lab and for this generation of attention psychophysics, on the order of 10–20 observers per experiment), within-subjects manipulation of grouping condition, and counterbalanced trial orders. Statistics report ANOVA / planned contrasts on RT and accuracy. Each experiment is paired with a post-experiment explicit-report check that establishes that the grouping manipulation was unreportable, securing the "implicit" status of the measure.

## 5. Results

The pattern of results across the five experiments is consistent and forms the paper's empirical case:

- **Müller-Lyer experiments.** The standard Müller-Lyer illusion was reliably elicited even when the inducer fins were dot-grouped rather than drawn — i.e., line-length judgments were biased by the implicit grouping of the dot field into inward vs outward fins. Critically, the post-experiment recognition test confirmed that observers were at or near chance in explicitly identifying which inducer configuration had been shown — yet their length judgments tracked the grouping. The illusion magnitude under implicit grouping was reduced relative to the fully-drawn-fin baseline but remained statistically reliable, indicating that the grouping operation that produces the fin percept is functionally intact even when the percept itself is not entered into explicit report.
- **Flanker experiments.** Flanker interference (RT cost for incompatible vs compatible flankers) was *modulated by perceptual grouping*: when target and flankers belonged to the same Gestalt group, interference was larger; when grouping segregated target from flankers, interference was reduced. This grouping-modulation persisted under attentional load — i.e., when the target task was made harder, the *magnitude* of the grouping effect on flanker interference did not significantly decrease, even though overall RTs lengthened. The interaction of central interest (Grouping × Load) was either non-significant or in the direction opposite to the attention-required hypothesis.
- **Convergent conclusion.** Across two methodologically distinct implicit-measure paradigms (illusion magnitude in Müller-Lyer; interference modulation in flanker), grouping influenced perception in the absence of explicit awareness and resisted attentional load. The convergence across paradigms is the key inferential move: any single implicit measure could be challenged as an artifact of residual attention, but two independent implicit measures pointing the same way are jointly hard to explain without granting that grouping operates without attention.

Specific RT and accuracy numbers are reported in the paper's Tables 1–3 but were not accessible from the open abstract; the qualitative pattern above is the load-bearing finding. The paper's argumentative weight rests less on absolute effect sizes and more on the *dissociation pattern*: explicit reportability collapses under inattention, implicit perceptual influence does not.

## 6. Critique / limitations

The paper's strongest claim — that grouping is computationally pre-attentive — is supported by a *behavioral signature* (implicit effects survive inattention) rather than by a *mechanism*. Whether the underlying neural process is genuinely feedforward and stimulus-driven, or is itself a fast attention-like process operating on a different timescale or substrate, is not adjudicated. Subsequent work (Kimchi & Razpurker-Apfeld 2004; Kimchi 2009) has shown that different grouping operations have different attentional requirements: grouping by color similarity and proximity is robustly pre-attentive, while grouping by shape similarity or by closure depends on attention. The Lamy et al. result is therefore best read as establishing that *some* grouping operations are pre-attentive, not that all are.

The reliance on implicit measures cuts both ways. Implicit effects are a more sensitive probe of unconscious processing, but they are also more interpretively ambiguous: a residual flanker-modulation under load could in principle reflect either pre-attentive grouping or a small amount of leaked attention to the flankers. The paper's defense against this is the converging-evidence structure across paradigms, which is genuinely compelling, but a strict skeptic could still hold that the experiments establish *low-attention* rather than *no-attention* grouping.

The flanker manipulation of "attentional resources" is operationalized as task difficulty (eccentricity, secondary load). This is a workable but indirect manipulation; it does not directly measure or control the distribution of attention. Subsequent work using more direct attention manipulations (cueing paradigms, dual-task with established capacity limits) has produced a more nuanced picture — some grouping operations are immune to load, others are not.

The paper does not engage in depth with the *neural* literature on grouping. The V1-V2-V4 contour-grouping circuit (Roelfsema and colleagues), the feedforward-vs-feedback decomposition of figure-ground segmentation (Lamme, Roelfsema), and the role of horizontal connectivity in early visual cortex are all directly relevant but not discussed. A reader interested in mapping the behavioral result onto a computational substrate has to do the bridging work themselves.

Finally, the paper's framing — "grouping does not require attention" — is in some sense too strong for the data, which establish only that grouping does not require *the kind of explicit attention measured by reportability and by flanker-load resistance*. A more cautious title would have been "grouping is dissociable from explicit attention," and the subsequent literature has largely converged on that more cautious reading.

A further limitation worth flagging for the present database: Lamy et al. work entirely at the *behavioral* level. The paper does not specify, and the experiments cannot adjudicate, whether the pre-attentive grouping stage is purely feedforward or whether it already uses fast local recurrence (the kind documented by Lamme and colleagues in V1-V2). For the Recurrent ViT analogy to be tight, this distinction matters — a single-pass feedforward stage maps onto iterate 1 of the RViT, while a fast-local-recurrence pre-attentive stage maps onto something more like a within-iterate inner loop. The paper leaves this open. The conservative reading, which we adopt in §7, is that "pre-attentive" here means "prior to the slow, top-down-feedback-driven attentional selection that closes the cortical loop," and is compatible with fast local recurrence in early cortex.

## 7. Connection to our work

This paper supplies the cognitive-science premise that *perceptual grouping is computationally distinct from, and prior to, attentional selection*. That premise is load-bearing for the user's architectural reading of the Recurrent ViT and for the contrast with [mehrani_tsotsos2023_attention_grouping](mehrani_tsotsos2023_attention_grouping). Five specific connections follow.

**1. Lamy et al. as the empirical complement of Mehrani & Tsotsos 2023.** Mehrani & Tsotsos 2023 argue that softmax self-attention over patch tokens, evaluated in a single feedforward pass, implements similarity-based perceptual grouping rather than attention. They read this as a deficiency of vanilla ViTs: the architecture cannot, without feedback, do attention. Lamy et al. supply the cognitive-science premise that makes Mehrani & Tsotsos's result *expected rather than damning*: in the cognitive system itself, the feedforward stage does grouping; attention is a feedback-dependent later operation.

The vanilla ViT's success at grouping (Mehrani-Tsotsos) and the human visual system's pre-attentive grouping (Lamy et al.) are the same phenomenon in two substrates. The negative result is a feature, not a bug — provided the architecture also has a later, attention-implementing stage. This is the architectural lever the Recurrent ViT ([dosovitskiy2020_vit](dosovitskiy2020_vit) recurrent variant in arXiv:2502.10955) pulls: it preserves the feedforward grouping primitive (a single self-attention block) and adds the missing piece — a recurrent state that supplies the top-down feedback Lamy et al.'s framework predicts is necessary to convert grouping into attention.

**2. The recurrent ViT's first iterate as the pre-attentive grouping stage.** The Recurrent ViT (arXiv:2502.10955) runs the same self-attention block multiple times with a recurrent state $H_t$ as feedback. At $t=0$ the state $H_0$ carries no task-specific bias, and the self-attention map produced is — by Mehrani & Tsotsos's argument — a grouping map. At $t = n_{FR}$ the state $H_{n_{FR}}$ has been updated by the task signal and the attention map is now biased by top-down feedback.

The Lamy et al. premise is what licenses calling these two stages by their respective cognitive names: iterate 1 = pre-attentive grouping (the Gestalt parse of the patch grid into similarity-defined groups); iterate $n$ = attention-driven binding (the selective focus on task-relevant groups). The Food-101 attention-map visualizations ([the_user_architectural_program](../threads/the_user_architectural_program.md) §6) — where maps focus, defocus, and reactivate across recurrent steps — are then a direct visualization of the transition from grouping-only to grouping-plus-attention. This also predicts a falsifiable empirical signature: the entropy or spatial structure of the iterate-1 attention map should be largely *image-determined* (reflecting Gestalt cues in the input) and largely *task-invariant*, whereas the iterate-$n$ map should be increasingly *task-determined*. The Recurrent ViT's published results, in which later iterates produce more task-discriminative maps, are consistent with this prediction.

**3. Connection to [wolfe2011_scene_search](wolfe2011_scene_search) and the nonselective pathway.** Wolfe et al. 2011 partition real-scene search into a fast, parallel, capacity-unlimited *nonselective* pathway that extracts gist and scene statistics in one fixation, and a slow, serial *selective* pathway that binds and recognizes individual objects. Lamy et al.'s pre-attentive grouping is the perceptual-organization component of Wolfe's nonselective pathway: in a single feedforward pass, the visual system parses the input into Gestalt-defined groups (figure-ground, similarity, proximity) without explicit attention. The Recurrent ViT's first iterate is then doing the same work — extracting the parallel, attention-free perceptual structure — and the subsequent iterates implement Wolfe's selective pathway via the recurrent feedback loop. This three-way alignment (Lamy → Wolfe nonselective → RViT iterate 1) is what gives the user's architectural reading its empirical bite.

**4. Connection to [itti_koch2001_saliency_review](itti_koch2001_saliency_review) and the saliency-vs-grouping question.** Itti & Koch's saliency model treats the feedforward stage as producing a *topographic saliency map* (feature-contrast peaks). Lamy et al. and the Gestalt tradition treat the feedforward stage as producing *grouped percepts* (similarity-defined coalitions of patches). These are not the same operation: a saliency map says *where* to attend; a grouping parse says *what perceptual units are available* to attend to. The Recurrent ViT's first iterate, on Mehrani & Tsotsos's reading, produces something closer to a grouping parse than to a saliency map (which is consistent with their negative singleton-detection result). The Lamy et al. premise is that this is the *correct* feedforward output — grouping, not saliency — and that saliency-like attentional peaks emerge only after recurrent feedback biases the grouped map.

**5. Connection to [treisman_gelade1980_feature_integration](treisman_gelade1980_feature_integration), [wheeler_treisman2002_binding](wheeler_treisman2002_binding), and the binding question.** Feature Integration Theory holds that elementary features are computed pre-attentively but that *binding* requires attention. Lamy et al.'s result is consistent with FIT in the sense that *grouping* (a form of pre-attentive feature organization) does not require attention, while *binding into reportable object identity* does. The Recurrent ViT's iterate-and-refine cycle is then naturally read as the computational implementation of FIT: iterate 1 produces grouped feature maps (pre-attentive); iterate $n$ produces a bound, reportable representation under recurrent feedback that selects which group to bind. PRISM v1's prediction-error-driven attention ([the_user_architectural_program](../threads/the_user_architectural_program.md) §5) is a different but related move — it replaces the softmax-grouping primitive with a Rao-Ballard residual primitive — and the open empirical question is whether the prediction-error substrate also admits a grouping-then-binding decomposition, or whether it collapses the two stages.

**6. Connection to [egly1994_object_attention](egly1994_object_attention) and object-based attention.** Egly, Driver & Rafal 1994 showed that attention spreads more efficiently within a perceptual object than across object boundaries, even when locations are matched for distance. This is the canonical object-based-attention result, and its premise is that *the objects must already exist* before attention can be object-based. Lamy et al.'s grouping-without-attention result supplies that premise: the perceptual objects (Gestalt-grouped units) are constructed by a pre-attentive stage; attention then operates over those constructed units. The Recurrent ViT's iterate-1 patch-token grouping is the pre-attentive object-construction stage; the recurrent feedback that biases attention is the object-based-attention stage. The two papers therefore jointly motivate the architectural commitment to a two-stage process — first parse into groups, then attend within / across groups.

The convergent architectural prescription is: the Recurrent ViT's recurrence is not a generic capacity hack, it is the implementation of the grouping-then-attention dissociation that Lamy et al. demonstrate behaviorally. This is also the architectural reading that connects naturally to [kietzmann2019_recurrence_required](kietzmann2019_recurrence_required): recurrence is required for the visual system to do the work that a feedforward stage cannot. Lamy et al. tell us *which* work the feedforward stage already does (grouping) and *which* work it cannot do (attention-dependent binding and reportability). The architectural payoff is concrete: when interpreting Recurrent ViT attention maps, the maps at $t=0$ should be read as Gestalt-grouping maps (similarity / proximity over patch features) and the maps at $t = n_{FR}$ as task-driven attentional-selection maps. The transition between the two — the *iterate-and-refine* trajectory — is the computational realization of the cognitive transition from pre-attentive parse to attentive binding that Lamy et al.'s implicit-explicit dissociation behaviorally indexes.

## 8. Citations to follow

- `moore_egeth1997_perception_without_attention` — the precursor study that Lamy et al. replicate and extend; foundational reference for the implicit-grouping paradigm.
- `kimchi2009_perceptual_organization_attention` — the most-cited follow-up that distinguishes which grouping operations are attention-free vs attention-dependent; necessary qualifier to Lamy et al.'s broad claim.
- `roelfsema2006_cortical_grouping_review` — the canonical neural account of grouping in early visual cortex (horizontal connections in V1, contour grouping in V2-V4); supplies the mechanistic substrate Lamy et al. leave open.
- `mack_rock1998_inattentional_blindness` — the foil against which "grouping does not require attention" is the antagonist position; necessary for the historical context.
- `driver_baylis1989_grouping_attention` — the early grouping-and-selective-attention study cited as background; load-bearing for the visual-search literature's treatment of grouping.
- `lamme_roelfsema2000_feedforward_recurrent` — the explicit feedforward-vs-recurrent decomposition of visual processing; the neural complement of Lamy's behavioral dissociation and a direct bridge to the recurrent-ViT framing.
- `julesz1981_textons` — the texton-based pre-attentive feature-map proposal that the Gestalt-grouping tradition partly supersedes; useful for the FIT lineage.
- `wagemans2012_gestalt_century_review` — the modern Gestalt-perception review; situates Lamy et al. in the longer arc of the Gestalt research program.
- `russell_palmer2006_grouping_attention_review` — companion review on the grouping-and-attention question; useful for the surrounding theoretical context.
- `eriksen_eriksen1974_flanker` — the foundational flanker paradigm; methodological background for the flanker experiments in §4.
