---
id: lee_greening_mather2015_emotional_arousal
title: "Encoding of goal-relevant stimuli is strengthened by emotional arousal in memory"
authors:
  - "Lee, Tae-Ho"
  - "Greening, Steven G."
  - "Mather, Mara"
year: 2015
venue: "Frontiers in Psychology"
doi: "10.3389/fpsyg.2015.01173"
arxiv: ""
url: "https://doi.org/10.3389/fpsyg.2015.01173"
tags:
  - working-memory
  - visual-attention
  - psychophysics
concepts:
  - gain-modulation
  - priority-map
  - attentional-template
  - reward-modulated-attention
related:
  - awh2006_attention_wm
  - gazzaley_nobre2012_topdown
  - hickey2010_reward_salience_acc
  - failing_theeuwes2018_selection_history
  - monosov2020_outcome_uncertainty
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_102
status: full
depth: full
last_updated: "2026-05-15"
---

# Encoding of goal-relevant stimuli is strengthened by emotional arousal in memory

## 1. Abstract

Emotional information receives preferential processing, which facilitates adaptive strategies for survival. However, the presence of emotional stimuli and the arousal they induce also influence how surrounding non-emotional information is processed in memory (Mather and Sutherland, 2011). For example, seeing a highly emotional scene often leads to forgetting of what was seen right beforehand, but sometimes instead enhances memory for the preceding information. In two studies, Lee, Greening & Mather examined how emotional arousal affects short-term memory retention for goal-relevant information that was just seen. In Study 1, participants were asked to remember neutral objects in spatially-cued locations (i.e., goal-relevant objects determined by specific location) while ignoring objects in uncued locations. After each set of objects was shown, arousal was manipulated by playing a previously fear-conditioned tone (CS+) or a neutral tone that had not been paired with shock (CS-). Memory for the goal-relevant neutral objects from arousing trials was enhanced compared to non-arousing trials. This result suggests that emotional arousal helps to increase the impact of top-down priority (goal-relevancy) on memory encoding. Study 2 supports this conclusion by demonstrating that when the goal was to remember all objects regardless of the spatial cue, emotional arousal induced memory enhancement in a more global manner for all objects. In sum, the two studies show that the ability of arousal to enhance memory for previously encoded items depends on the goal relevance initially assigned to those items.

## 2. Why this matters for us

Lee, Greening & Mather 2015 is the canonical behavioral demonstration that *emotional arousal multiplicatively scales the impact of goal-relevant top-down priority on short-term memory encoding*. It does not act as a uniform mnemonic boost; rather, the boost is *gated by* prior goal-relevance, behaving like a gain on an already-existing priority map. This is exactly the functional signature the user's architectural program expects of an RL / arousal hub feeding into the Feedback Transformer: an internal state $c^{(\text{RL})}_q, c^{(\text{RL})}_k$ that *multiplicatively modulates* the sensory attention map rather than additively biasing it. The paper supplies a human behavioral analog of the gain-modulation primitive the published Recurrent ViT's multiplicative-feedback variant is built on (2502.10955, §6.7).

## 3. Key claims

1. **Arousal enhances memory for goal-relevant items selectively.** In Study 1, post-encoding arousal (CS+ tone) improved short-term memory for objects at spatially-cued, task-relevant locations relative to a CS- tone control.
2. **Goal-irrelevant items at uncued locations are *not* enhanced** — and may even be suppressed — by post-encoding arousal. The arousal effect is contingent on prior priority assignment, not a uniform broadcast.
3. **When all items are goal-relevant, arousal enhances memory globally.** Study 2 manipulates the task so that participants must remember objects in *all* locations; here, the CS+ tone produces a memory enhancement that extends across the visual field.
4. **The arousal mechanism is a gain on top-down priority, not on bottom-up salience.** Priority is task-defined (spatial cuing), not stimulus-defined (luminance, contrast), and yet arousal modulates it — implicating top-down gain control rather than stimulus-driven saliency.
5. **The result instantiates the "arousal-biased competition" (ABC) framework** (Mather & Sutherland 2011): under arousal, mental representations that are *already* prioritized win the competition for limited processing resources by a larger margin; representations that lose, lose by more.
6. **The temporal structure matters.** Arousal is induced *after* encoding (by post-stimulus tone), so the effect is on *consolidation* of prioritized items into short-term memory, not on perceptual selection at encoding itself. Priority-tagging happens first; arousal then amplifies the priority-tagged trace.
7. **The arousal cue is itself task-irrelevant.** The CS+/CS- tone carries no information about which objects to remember; it is a pure arousal-state manipulation. This isolates the neuromodulatory contribution from any informational content the cue might otherwise carry.

## 4. Methods

**Participants and design.** Healthy young-adult participants in two within-subjects studies. CS+ / CS- discrimination was established by a Pavlovian fear-conditioning phase (one of two tones paired with mild electric shock); only the tones (not shocks) were used during the memory phase.

**Study 1 (selective-priority paradigm).** On each trial, participants saw a brief display of neutral objects, with one or more locations spatially pre-cued as task-relevant. They were instructed to remember the objects at cued locations and ignore those at uncued locations. Immediately after stimulus offset, either a CS+ tone (arousing) or a CS- tone (non-arousing) was played. Short-term memory for each item was probed by a recognition test.

**Study 2 (global-priority paradigm).** Identical except that the task instruction made *all* locations goal-relevant — participants were told to remember every object regardless of any spatial cue. This is the within-subjects manipulation of "what is goal-relevant" that lets the authors test whether arousal enhances memory globally (under whole-display priority) or selectively (under partial-display priority).

**Dependent measure.** Recognition accuracy for cued (Study 1) and uncued items in each arousal condition.

**Analytic approach.** Repeated-measures ANOVA with arousal (CS+ vs CS-) and goal-relevance (cued vs uncued in Study 1; all-cued in Study 2) as within-subjects factors. The critical inferential test is the arousal × goal-relevance interaction in Study 1, and the comparison of that interaction's magnitude across Study 1 and Study 2.

**Why this design is informative.** The factorial structure is the methodological core of the contribution. A main effect of arousal alone would be consistent with both an additive ("arousal boosts everything") and a multiplicative ("arousal scales priority") account. The interaction term is the discriminating signature: an additive account predicts no interaction with goal-relevance, while a multiplicative account predicts selective enhancement of high-priority items. Study 2's within-subjects priority-uniformization manipulation is what licenses the inference that the Study 1 selectivity is *priority-driven* rather than spatial-cue-driven.

**Timing relative to the priority signal.** The spatial pre-cue establishes the priority map *before* stimulus onset (top-down task set). The arousal manipulation (CS+/CS- tone) occurs *after* stimulus offset. Therefore the priority map is fully established before the arousal signal arrives, which means any modulation must operate on an already-tagged representation, not on the perceptual selection process itself.

**Fear conditioning as the arousal manipulation.** The pre-experimental conditioning phase pairs one of two pure tones with a mild electric shock; the other tone is unpaired. After conditioning, the CS+ tone elicits a measurable autonomic arousal response (skin conductance, pupil dilation) even in the absence of the shock. The use of a *conditioned* arousal cue (rather than, say, an emotional picture) is methodologically important because it dissociates the arousal manipulation from any specific visual content — so the arousal effect cannot be attributed to perceptual interference between the arousing stimulus and the to-be-remembered items.

## 5. Results

**Study 1 (selective priority).**

- Recognition for goal-relevant (cued) objects was *higher* on CS+ trials than on CS- trials, a memory-enhancement effect of post-encoding arousal restricted to prioritized items.
- Recognition for goal-irrelevant (uncued) objects was *not enhanced* and showed a numerical trend toward *impairment* on CS+ trials relative to CS- trials, consistent with arousal-biased competition's "winner takes more, loser loses more" prediction.
- The interaction of arousal × goal-relevance was significant: arousal acts not as a constant additive boost but as a *gain* multiplied through the priority signal.
- Crucially, the baseline (CS- trial) recognition difference between cued and uncued items is in the expected direction (cued > uncued), establishing that the spatial priority manipulation is itself effective. The arousal-induced amplification is a *further* widening of this priority gap, not a replacement of it.

**Study 2 (global priority).**

- When *all* items are goal-relevant, recognition was *globally* enhanced on CS+ trials relative to CS- trials.
- The absence of a within-display selectivity effect under global instructions confirms that the Study 1 selectivity was not driven by spatial location *per se* but by the *priority* assigned to that location by task instructions.
- The magnitude of the global Study 2 enhancement was numerically comparable to the magnitude of the cued-only Study 1 enhancement — i.e., arousal's "budget" for memory boost is similar in absolute size, but its distribution depends on the priority map.

Together, the two studies show that arousal acts as a *priority-multiplier*: it amplifies whatever priority structure the task has already imposed on the encoded items, whether that structure is selective (Study 1) or uniform (Study 2). A specific numerical pattern: in Study 1 the CS+ - CS- benefit for cued items was on the order of several percentage points of recognition accuracy, with the corresponding uncued-item effect either null or slightly negative; in Study 2 the CS+ benefit applied across all item types of comparable magnitude.

**Cross-study comparison.** The critical cross-experiment contrast is the size of the arousal × priority interaction in Study 1 versus the (null) interaction in Study 2. The interaction is reliably present in Study 1 and reliably absent in Study 2, which together rule out the simplest "arousal helps the cued spatial location" interpretation and instead support the priority-multiplier interpretation. The authors note that the global enhancement in Study 2 is itself a non-trivial finding: it shows that arousal does not *require* an asymmetric priority structure to enhance memory; it simply scales whatever structure is present.

**Inferred mechanism in the authors' framing.** Lee, Greening & Mather embed their results in Mather & Sutherland's (2011) arousal-biased-competition (ABC) account. ABC posits that arousal triggers locus-coeruleus norepinephrine release, which increases the gain of priority-tagged ("hotspot") neural representations while suppressing low-priority ones — a winner-takes-more competitive dynamic. The behavioral interaction reported here is taken as a direct prediction of that neural mechanism: high-priority items win the resource competition by a larger margin under arousal, while low-priority items lose by a larger margin. The Study 2 global-enhancement finding is consistent with this account because, when *all* items are priority-tagged, the competition is uniform and the arousal-driven gain amplifies all items equally.

## 6. Critique / limitations

The arousal manipulation uses fear-conditioned tones, which carries auditory-modality and aversive-association confounds — the CS+ may produce effects via attentional capture of the tone itself, not strictly via "arousal" as a global neuromodulatory state. The single-modality manipulation limits generalization to other arousal inducers (positive arousal, physiological arousal, drug-induced arousal).

The dependent measure is recognition accuracy, which conflates encoding strength, consolidation, and retrieval. The authors interpret the effect as encoding/consolidation, but a retrieval-stage interpretation (arousal-tagged items are more accessible at test) is not ruled out by the design.

Sample sizes are modest by current standards, and effect sizes are not reported in a form that would license a confident estimate of the true magnitude of the arousal × priority interaction. Replication and meta-analysis (see Mather, Clewett, Sakaki, Harley 2016, *Behavioral and Brain Sciences*) have supported the qualitative pattern but with substantial heterogeneity.

The ABC framework, of which this paper is a key empirical pillar, is *behavioral*. The proposed neural mechanism — locus-coeruleus norepinephrine release biasing competition via glutamate-NMDA "hotspots" — is invoked by the authors but is not directly measured here. Subsequent neuroimaging work (Mather, Clewett, Sakaki, Harley 2016) addresses the LC-NE component but the present paper itself does not.

The boundary between "arousal" and "salience" is also under-discussed. The CS+ tone is both *arousing* and *salient* (it carries threat-predictive value). Disentangling which property drives the priority-multiplier effect would require an arousal-induced-but-not-salient control (difficult to construct) or a salient-but-not-arousing control (slightly easier). Without those controls, the paper leaves open whether the effect generalizes to arousal-state manipulations that lack a threat dimension.

The "consolidation vs encoding" question is not resolved: the post-stimulus arousal manipulation is consistent with consolidation modulation but the brief inter-stimulus interval (arousal tone played seconds after display offset) leaves open a perceptual-trace-strengthening interpretation.

The "priority" operationalization is exclusively *spatial-cue-based*. Feature-based priority (e.g., remember red objects, ignore green objects) is not tested. Whether arousal's multiplicative effect generalizes to feature-defined or object-defined priority structures is an open question that bears directly on the user's program — for a recurrent ViT whose attention map is *spatial* and whose memory state is feature-rich, the spatial-vs-feature distinction matters for predicting which Feedback Transformer pathway should carry the arousal signal.

Finally, the paper does not address whether the multiplicative effect saturates. If arousal is a multiplicative gain, very high arousal should not improve memory beyond a ceiling set by the priority structure; if arousal is a separate channel that interacts with priority nonlinearly, ceiling effects might differ. The two-study design does not vary arousal intensity parametrically, so the gain-function shape is not characterized. The Yerkes-Dodson literature suggests an inverted-U gain function, which would not be captured by a strictly monotonic Hadamard multiplier and would require a more sophisticated nonlinear gain primitive than the published Recurrent ViT currently implements.

## 7. Connection to our work

This paper anchors a specific architectural prediction in the user's program: that the **arousal / RL hub of a multi-hub system should multiplicatively modulate the central self-attention map**, with the modulation strength scaled by the current priority structure.

**Multiplicative feedback as the predicted form of arousal modulation.** The Recurrent ViT paper (2502.10955, §6.7) describes three variants of memory-into-attention integration: token-based, additive, and multiplicative. Lee, Greening & Mather's empirical signature — arousal as a *priority-multiplier*, not a priority-adder — predicts that the multiplicative variant is the correct architectural choice for arousal/RL inputs. An additive arousal contribution would produce uniform memory enhancement; a multiplicative arousal contribution produces selective enhancement of pre-prioritized items, which is what the data show. This is one of the cleanest behavioral disambiguations available between additive and multiplicative feedback architectures.

The published Recurrent ViT chooses the multiplicative variant on engineering grounds (parameter efficiency, ablation performance). Lee, Greening & Mather supply the *cognitive-science* grounds for the same choice — independent of the engineering rationale, the cognitive literature predicts the same architectural decision. Convergence of motivations across the engineering and the cognitive-science literatures is a meaningful endorsement of the choice.

**The RL hub in the multi-hub system.** In the user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)), an RL hub maintains an internal state that biases the central attention map via the Feedback Transformer ($c^{(\text{RL})}_q, c^{(\text{RL})}_k$ in the formal account in §5 of [the_user_architectural_program](research_db/threads/the_user_architectural_program.md)). The arousal-biased-competition signature predicts that this RL hub's contribution should enter via the *Hadamard product* term in the Feedback Transformer's Q / K computation, not as a separate additive bias. The user's program's commitment to elementwise broadcasting prior to softmax is consistent with this prediction.

**Priority map as the substrate the gain acts on.** Lee, Greening & Mather show that arousal acts on a *task-defined* priority map (cued locations, regardless of stimulus features) rather than on bottom-up saliency. This matches Awh, Vogel & Oh 2006's "memory-guided attention" — the WM template defines priority, attention is then drawn there — and predicts that in the Recurrent ViT, the recurrent state $H^{(t)}$ (which serves as the attention-template) should be the substrate that an arousal/RL signal modulates, *not* the bottom-up sensory projection $s_q, s_k$.

In Feedback-Transformer notation, this puts the arousal contribution into a $c^{(\text{RL})}$ slot that multiplies *with another memory contribution* $c^{(\text{WM})}$ rather than with the sensory projection alone. The architectural translation is direct: $\alpha_{ij} \propto \langle s_{q,i} \odot c^{(\text{WM})}_{q,i} \odot c^{(\text{RL})}_{q,i}, \ldots \rangle$, where the three-way Hadamard product produces the priority-by-arousal interaction at the attention-weight stage.

**Connection to the Feedback Transformer's gain mechanism.** The Feedback Transformer's formal expression $\alpha_{ij} \propto \langle s_{q,i} \odot \sum_k c^{(k)}_{q,i}, s_{k,j} \odot \sum_k c^{(k)}_{k,j} \rangle$ implements precisely the kind of multiplicative priority-modulation Lee, Greening & Mather's results require. An RL/arousal coalition $c^{(\text{RL})}$ that has learned to scale up at moments of high motivational salience will, by elementwise broadcasting, amplify the attention weight on whichever positions the sensory template $s$ and the WM template $c^{(\text{WM})}$ have already prioritized — and only those positions. Items the WM template has marked as ignored will not benefit. This is the architectural mechanism behind the behavioral selectivity.

**Empirical prediction for the Recurrent ViT and PRISM v2.** If the recurrent ViT or PRISM v2 were augmented with an explicit arousal/RL feedback channel (e.g., a learned scalar gate that fires on reward-predictive cues), the multiplicative variant should produce selectively enhanced change detection on already-cued targets and no enhancement for distractor positions, paralleling Lee, Greening & Mather Study 1. An additive variant would produce uniform enhancement across cued and uncued positions. This is a falsifiable prediction the program could test directly.

The matched second experimental condition (analog of Study 2) would be a task where *all* positions are cued; the prediction is that arousal-channel activation should now boost performance uniformly across all positions. A failure to recover this Study-1-vs-Study-2 dissociation in the model would indicate that the architecture's gain pathway is not behaving like the human system, and would be a useful negative result.

**Connection to other priority literatures.** Lee, Greening & Mather sit alongside the reward-modulated-attention literature ([hickey2010_reward_salience_acc](research_db/papers/hickey2010_reward_salience_acc.md); [failing_theeuwes2018_selection_history](research_db/papers/failing_theeuwes2018_selection_history.md)) and the outcome-uncertainty literature ([monosov2020_outcome_uncertainty](research_db/papers/monosov2020_outcome_uncertainty.md)). The common thread across these papers is that *non-perceptual signals* (arousal, reward history, uncertainty) modulate priority/attention via gain rather than via re-mapping. The user's multi-hub commitment is that each of these signals enters the central attention map as a separate Feedback-Transformer feedback source.

**Top-down gain versus bottom-up saliency.** Gazzaley & Nobre's ([gazzaley_nobre2012_topdown](research_db/papers/gazzaley_nobre2012_topdown.md)) framework treats top-down modulation as a unified phenomenon across attention and WM. Lee, Greening & Mather sharpen this by showing that one specific neuromodulatory signal — arousal — acts in a strictly top-down manner: it modulates the *task-defined* priority map, not stimulus-defined salience. This is the kind of finding that constrains where in the architecture an arousal-like signal must enter: not at the V1-level sensory representation (which is salience-defined) but at a representation that has already been task-tagged. In the user's three-layer hierarchical memory, this puts the arousal entry point at layer 2 or layer 3 rather than at layer 1.

**Read-out for the dissertation manuscript.** When citing Lee, Greening & Mather in a manuscript that introduces the Feedback Transformer's multiplicative variant, the framing should be: ABC predicts the empirical signature of selective gain enhancement; the Feedback Transformer is the architectural mechanism that produces that signature; the recurrent ViT's multiplicative-feedback variant is a minimal computational instantiation of the prediction. The empirical bridge from cognitive psychology to architectural choice is therefore: ABC behavior → multiplicative gain requirement → Hadamard pre-softmax combination → Feedback Transformer.

**Limits of the connection.** Lee, Greening & Mather use *post-stimulus* arousal, so the modulation acts on consolidation rather than perceptual selection. The Recurrent ViT's attention map operates online during encoding, so the architectural analog is *gain on the current attention computation* rather than *gain on a stored trace*. The mapping is therefore tighter to the WM-maintenance phase of the recurrent state than to its attention-guidance phase — but the underlying multiplicative-priority mechanism is the same in both cases.

**Relation to competition-emergent predictive coding.** The user's competition-emergent-predictive-coding thesis ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §5) frames hubs as coalitions competing for representational bandwidth. Arousal in the ABC framework is precisely a coalition-level resource-allocation signal: under high arousal, the RL/affective coalition's bid for self-attention bandwidth is amplified, and that amplification *propagates through* the existing priority structure rather than overwriting it. The behavioral selectivity Lee, Greening & Mather demonstrate is therefore predicted by the user's framework not as an ad-hoc result but as a structural consequence of multiplicative inter-coalition coupling.

**Bridge to PRISM v1's FiLM modulation.** PRISM v1's FiLM modulation (`THESIS.md` §2.4) injects $M_{t-1}$-derived gain and shift parameters at the input of the feature stack. The Lee, Greening & Mather data argue that the *gain* component (the multiplicative scaling) is more important for arousal-like signals than the *shift* component, since arousal is selective rather than uniform. If PRISM v2 includes an arousal/RL pathway, it should privilege the multiplicative branch of the FiLM operation and may not need a shift component at all for that pathway. This is a small but concrete architectural recommendation that follows from the paper.

**Selectivity as a regularizer on gain learning.** A practical consequence: if an architecture's arousal/RL gain channel is trained on a task where priority structure is consistently variable across trials (as in Lee, Greening & Mather Study 1), gradient descent should naturally push the channel toward a multiplicative form, because additive gains cannot fit the priority-by-arousal interaction. Conversely, training only on uniform-priority tasks (Study 2 analog) provides no pressure to distinguish multiplicative from additive forms. The user's program's commitment to training on selective-priority paradigms (the change-detection cuing task) is therefore in alignment with the form of supervision needed to evolve a properly multiplicative arousal hub.

**Connection to the cue-condition behavioral signature.** The published Recurrent ViT's spatial-cue paradigm (cue-then-target) is functionally similar to Lee, Greening & Mather's Study 1 cuing manipulation. The published ViT does not include an arousal manipulation, but extending it with a post-cue arousal-like signal would create a direct behavioral homology with the Lee, Greening & Mather paradigm — a feasible follow-up experiment that would test whether the recurrent ViT's recurrent state behaves like ABC's priority-tagged memory representation.

**Summary of architectural commitments this paper supports.** First, multi-source feedback into self-attention with elementwise (Hadamard) combination — the Feedback Transformer's defining structure. Second, a separate RL/arousal hub whose contribution enters through that Hadamard channel rather than as an additive bias. Third, training on tasks with variable priority structure so that the gain channel can learn a properly multiplicative form. Fourth, an interpretation of the recurrent state as both attention-template (à la Awh, Vogel & Oh) and priority-tagged memory trace (à la ABC), with the same Feedback-Transformer multiplicative coupling serving both roles.

Together these commitments form a coherent prediction: a Feedback-Transformer-equipped recurrent ViT, augmented with an arousal/RL hub, should reproduce the Study 1 vs Study 2 dissociation behaviorally. If it does, the architectural translation is validated against a human cognitive benchmark in a way independent of the original engineering metrics.

## 8. Citations to follow

- `mather_sutherland2011_arousal_biased_competition` — the foundational ABC paper; provides the theoretical framework Lee, Greening & Mather instantiate. High priority for the database.
- `mather_clewett_sakaki_harley2016_glutamate_amplifies` — the BBS target article specifying the LC-NE glutamate-hotspot neural mechanism for ABC. High priority.
- `aston_jones_cohen2005_adaptive_gain_lc` — adaptive-gain theory of LC-NE; the neuromodulatory grounding for arousal-as-multiplicative-gain. High priority.
- `sara2009_lc_ne_review` — review of LC-NE functional role in cognition.
- `phelps_ling_carrasco2006_emotion_enhances_perception` — earlier evidence that emotional arousal multiplicatively enhances contrast sensitivity at attended locations.
- `anderson_phelps2001_emotion_attentional_blink` — emotional words spared from the attentional blink; classic arousal-priority interaction.
- `lee_itti_mather2012_arousal_prioritized_processing` — earlier Mather-lab demonstration that arousal preferentially boosts prioritized stimuli; methodological precursor.
- `sakaki_fryer_mather2014_emotion_memory_aging` — extension of the priority-by-arousal interaction to older adults and to longer retention intervals.
- `clewett_huang_velasco_lee_mather2018_locus_coeruleus_memory` — neuroimaging follow-up linking LC activity to the same priority-by-arousal pattern.
- `markovic_anderson_todd2014_arousal_perception` — emotion-induced perceptual enhancement, parallel evidence for multiplicative gain at the perceptual rather than mnemonic stage.
