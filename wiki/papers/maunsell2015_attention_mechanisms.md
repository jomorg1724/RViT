---
id: maunsell2015_attention_mechanisms
title: "Neuronal mechanisms of visual attention"
authors:
  - "Maunsell, John H. R."
year: 2015
venue: "Annual Review of Vision Science"
doi: "10.1146/annurev-vision-082114-035431"
arxiv: ""
url: "https://doi.org/10.1146/annurev-vision-082114-035431"
tags:
  - primate-neurophysiology
  - visual-attention
  - review
  - biased-competition
concepts:
  - gain-modulation
  - divisive-normalization
  - signal-detection-theory
  - top-down-feedback
  - multiplicative-feedback
related:
  - desimone_duncan1995_biased_competition
  - reynolds_heeger2009_normalization
  - moran_desimone1985_selective_attention
  - mcadams_maunsell1999_v4_tuning
  - mcadams_maunsell1999_reliability
  - cohen_maunsell2009_correlations
  - ghose_maunsell2002_task_timing
  - luo_maunsell2018_criterion_sensitivity
  - sridharan2017_sc_sensitivity_bias
  - reynolds1999_competitive_v2_v4
  - reynolds_chelazzi2004_attentional_modulation
  - carrasco2011_visual_attention_25y
  - bisley_goldberg2010_parietal_priority
  - hawkins1990_attention_detectability
  - krauzlis2013_sc_attention
  - treue_martinez_trujillo1999_feature_attention
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Neuronal mechanisms of visual attention

## 1. Abstract

Maunsell's 2015 *Annual Review of Vision Science* article surveys the state of neurophysiological evidence on visual attention as of the mid-2010s, after roughly three decades of single-unit and population-level recording in attending non-human primates. The review consolidates the principal findings: attention modulates neural responses across the visual hierarchy from V1 to IT and into parietal, frontal, and subcortical structures; the modulations take recognizable computational forms — most prominently *response gain* (a multiplicative scaling of the driven response) and *contrast gain* (a leftward shift of the contrast-response function) — and these forms map onto a small set of canonical circuit mechanisms (notably attention-modulated divisive normalization in the Reynolds-Heeger sense). The review's most important conceptual move is to take seriously the *multiplicity* of attentional signatures uncovered in the previous decade — firing-rate gain, noise-correlation reduction, Fano-factor changes, gamma-band synchronization, criterion shifts dissociable from sensitivity changes — and to argue that "attention" as ordinarily named is not a single neural mechanism but a *family* of mechanisms, only partially overlapping across tasks and brain regions, that the field has historically lumped together under one label. Single-mechanism accounts (e.g., gain modulation *alone*, or biased competition *alone*) are inadequate; what is needed is a taxonomy of attentional effects coupled to a taxonomy of the circuits that implement them.

## 2. Why this matters for us

Maunsell 2015 is the most authoritative one-paper synthesis the user's program can cite for the architectural commitment that attention is *implemented as gain modulation* (not as winner-take-all selection), *in multiple distinct forms across the hierarchy*, and that *the right model has more than one mechanism*. It is the review-level analog of the user's own *multi-hub, multi-mechanism* framing of cortical computation (`threads/the_user_architectural_program.md` §3, §5). It also provides the empirical license for treating sensitivity and bias as separable architectural components — the same separation that Luo & Maunsell 2018 and Sridharan et al. 2017 anchor at the single-unit and SDT-modeling levels respectively. For the Recurrent ViT, this paper is the canonical pointer to the V4 multiplicative-gain literature; for PRISM, it is the canonical pointer to the divisive-normalization gain mechanism PRISM's FiLM operator approximates.

## 3. Key claims

1. **Attention modulates responses throughout the visual hierarchy.** Attentional effects on firing rate are present from V1 (small) through V2, V4, MT, MST, and IT (large), with the magnitude of the modulation increasing along the ventral and dorsal streams.
2. **The dominant signature is response gain — a multiplicative scaling.** Attended stimuli evoke responses approximately equal to a constant times the unattended response, with the constant typically in the 1.1–1.5 range depending on area and task.
3. **Contrast gain is a distinct, complementary signature.** Under regimes in which the attended stimulus does not dominate the receptive field, attention can instead shift the contrast-response function leftward — i.e., the cell behaves as if the stimulus has higher effective contrast — without a multiplicative scaling at saturation.
4. **The same circuit (attention-modulated divisive normalization) produces both.** Reynolds & Heeger's normalization model accommodates response gain and contrast gain as two regimes of one mechanism, with the regime determined by the ratio of stimulus size to receptive-field size.
5. **Tuning curves are scaled but not sharpened.** Across orientation, direction, color, and feature dimensions, attention scales the tuning curve's amplitude but does not narrow its width (McAdams & Maunsell 1999; Treue & Martínez-Trujillo 1999) — ruling out "sharpening" accounts.
6. **Single-unit variance is largely unchanged by attention; pairwise noise correlation is reduced.** The locus of population-coding improvement is the correlation structure, not the per-cell Fano factor (McAdams & Maunsell 1999 reliability; Cohen & Maunsell 2009; Mitchell, Sundberg & Reynolds 2007, 2009).
7. **Attention modulates gamma-band synchronization between cortical areas.** Attended stimuli are accompanied by enhanced gamma coherence among the neurons representing them (Fries et al. 2001) — a timing-domain signature that is largely orthogonal to firing-rate gain.
8. **Performance changes are not a single quantity: sensitivity and bias dissociate.** Standard cuing manipulations produce both d' changes (sensitivity) and criterion / β changes (bias). These two components have *different* neural correlates: V4 / IT firing-rate modulations correlate with sensitivity; criterion changes correlate with activity in LPFC and with subcortical structures including the superior colliculus.
9. **The "attention" label aggregates several mechanisms.** Maunsell argues explicitly that the field has been treating *one phenomenon* with one word when the evidence demands at least three or four conceptually distinct mechanisms (gain on the driven response, change in shared variability, change in oscillatory coherence, change in decision criterion), each with its own circuit substrate, each with its own task dependence.
10. **Source-region identification remains partial.** Frontal eye fields, lateral intraparietal area, pulvinar, and superior colliculus are each plausible sources for *some* of the gain signal seen in extrastriate cortex; no single source accounts for all signatures, consistent with the multiplicity claim.
11. **Spatial and feature-based attention share computational substrate but differ in spatial extent.** Spatial attention applies the gain at a circumscribed retinotopic location; feature-based attention applies it globally across the visual field to all neurons tuned to the attended feature (Treue & Martínez-Trujillo's feature-similarity-gain). Both are instances of the same multiplicative-gain operator with different gain-field profiles.
12. **Attention's temporal precision tracks task-relevant intervals.** Ghose & Maunsell 2002 and related work show that attention sharpens responses not only spatially / featurally but also temporally, concentrating the modulation in the time window when behaviorally relevant events are expected.

## 4. Methods

The article is a narrative review rather than an empirical paper. Its method is the synthetic one: organize roughly three decades of single-unit and population recording results, in macaques performing covert spatial- and feature-attention tasks, into a coherent computational taxonomy. Maunsell draws principally on his own lab's published work — McAdams & Maunsell 1999 (V4 tuning, reliability), Cohen & Maunsell 2009 (correlations), Ghose & Maunsell 2002 (task timing), Williford & Maunsell 2006 (V1) — together with the canonical extrastriate attention literature (Moran & Desimone 1985, Reynolds et al. 1999, Treue & Martínez-Trujillo 1999, Reynolds & Chelazzi 2004), the normalization-model theoretical framework (Reynolds & Heeger 2009), the gamma-coherence work (Fries et al. 2001, Bichot et al. 2005), and the SDT-decomposition literature (Hawkins et al. 1990; foreshadowing Luo & Maunsell 2018 and Sridharan et al. 2017). The review's organizing axes are (a) *which signature* (rate, correlation, oscillation, criterion); (b) *which cortical area or circuit*; (c) *what computational form* (multiplicative gain, contrast gain, divisive normalization, decision-bound shift); and (d) *how the signatures relate to behavior* under the SDT decomposition.

## 5. Results

The review's quantitative anchors, by signature:

- **V4 firing-rate gain.** Median multiplicative scaling factor ≈ 1.2–1.3 across spatial-attention tasks (McAdams & Maunsell 1999); higher (≈1.5) under stronger attentional load.
- **V1 firing-rate gain.** Median ≈ 1.08 — present but much smaller than V4; consistent with hierarchical amplification of top-down modulation.
- **MT / feature-based gain.** Direction-tuned MT cells show multiplicative scaling on the order of 20–30% when their preferred direction is attended (Treue & Martínez-Trujillo 1999), with the gain applied globally across spatial locations.
- **Contrast-gain shifts.** Horizontal shift of the contrast-response function by roughly 0.3 log units under attention in V4 when stimulus is smaller than the receptive field.
- **Noise correlation.** Attention reduces pairwise spike-count correlations among co-tuned V4 neurons by approximately 40% (Cohen & Maunsell 2009); the population-coding consequence is substantial because shared variability scales the noise floor for linear decoders.
- **Fano factor.** Largely unchanged by attention at the single-unit level (McAdams & Maunsell 1999 reliability), at least within the count-window timescale used in classical analyses.
- **Gamma synchronization.** Enhanced gamma-band (40–90 Hz) coherence between V4 (or MT) neurons representing the attended stimulus, both within-area and with downstream FEF (Fries et al. 2001; Bichot et al. 2005).
- **Sensitivity vs. bias.** Visual-cortex modulations track d'; criterion changes track activity in LPFC and subcortical attention structures (foreshadowing Luo & Maunsell 2018 and Sridharan et al. 2017).
- **Hierarchy gradient.** Modulation magnitude rises from V1 → V2 → V4 → IT, with parallel gradients in the dorsal stream (MT → MST → LIP).

The review's overall *quantitative thesis* is that attention's neural effects are large (tens of percent in firing rate, factor-of-two-ish in noise correlation) but heterogeneous in form, and that the population-level consequences for behavior depend on which signature is dominant in the recorded population.

A useful framing the review makes implicit: the *information-theoretic* gain in V4 population coding under attention is dominated by the noise-correlation effect, not by the per-cell firing-rate gain. The factor-of-two reduction in shared variability among co-tuned cells is what makes a linear decoder substantially better at distinguishing attended from unattended population states; the multiplicative gain on single cells contributes a smaller but real additional improvement. This split — single-cell gain *and* population-correlation restructuring — is part of what Maunsell points at when he says attention is multiple mechanisms. From an architectural-modeling standpoint, this implies that a model claiming biological correspondence must produce *both* signatures, not just the more obvious single-unit one.

A second framing the review draws out: the time-course of attentional modulation is not uniform across signatures. Firing-rate gain develops within tens of milliseconds of the attentional cue; gamma synchronization develops over similar fast timescales; noise-correlation reduction is slower and more sustained. The criterion / bias component, when separable, follows yet a different time course tied to the decision rather than to the perceptual evidence. Any architectural model attempting to recapitulate the *full* attentional repertoire therefore needs more than one timescale of state update — a commitment the user's program makes explicit in PRISM v2's slow/fast memory and in the multi-compartmental memory's diminishing-feedback-into-deeper-layers gradient.

## 6. Critique / limitations

The review is consciously a synthesis; it does not propose a new computational model. Its principal interpretive move — that attention is several mechanisms, not one — is a *negative* claim about the prior literature's lumping habits rather than a constructive proposal for what a multi-mechanism model should look like. The user's architectural program is, in part, a constructive response to exactly this gap.

Coverage is concentrated on the macaque single-unit literature. Human imaging work (Kastner, Corbetta, Womelsdorf, Carrasco-lab psychophysics) is referenced but not foregrounded; the review's center of gravity is V4 / MT electrophysiology. As a consequence, the *behavioral* side of the multiplicity claim is undercharacterized; sensitivity-vs-criterion gets a paragraph rather than a section. Subsequent work (Luo & Maunsell 2018; Sridharan et al. 2017; Gupta & Sridharan 2024) develops this side substantially.

The review treats divisive-normalization-style models (Reynolds & Heeger 2009) as the dominant computational frame and gives less space to predictive-coding (Spratling 2008; Feldman & Friston 2010) or precision-weighting accounts of attention. This is a reasonable editorial choice for a *Annual Review of Vision Science* article in 2015 but understates the alternative theoretical traditions that re-cast attention in inferential rather than gain-modulation terms.

The review is silent on the *source* of attentional signals in much of its discussion. FEF, LIP, pulvinar, and SC are mentioned as candidates but not adjudicated; the priority-map literature (Bisley & Goldberg 2010; Krauzlis et al. 2013) is referenced rather than synthesized. The "where does the gain come from" question is therefore left for the reader to assemble.

The treatment of *temporal dynamics* is partial. Gamma synchronization is covered; slower attentional rhythms (theta-band sampling, presaccadic shifts) are not. Subsequent work (Fiebelkorn, Kastner and colleagues; Gupta & Sridharan 2024) develops the time-resolved attention literature that this review predates.

Finally, the review's *taxonomy of mechanisms* is sketched but not formalized. A reader looking for a numbered list of "the N mechanisms of attention and the circuit substrate of each" will not find one. The argument for multiplicity is made qualitatively and at the level of empirical patterns rather than at the level of a unified computational decomposition.

A subtler limitation: by foregrounding the *modulation* picture (attention as a multiplicative gain on the cortical response), the review implicitly sidelines an alternative empirical reading in which attention is the *output* of a competition that is mostly bottom-up driven. Under the Reynolds-Heeger framing this distinction is partly a matter of where one places the "attention field"; under a predictive-coding or precision-weighting framing it is more substantive. Maunsell's review is consistent with all of these, but a reader looking for a clean disambiguation among them will not find one — and the disambiguation matters for architectural decisions like whether attention should be a *separate* feedback channel into the model or an *emergent* consequence of inter-hub competition. The user's program adopts the latter view; Maunsell 2015 is *compatible* with that view but does not specifically endorse it.

## 7. Connection to our work

This review is *load-bearing* for the user's program in several ways, each of which sharpens an architectural commitment that would otherwise rest on individual primary papers.

**Multiplicity of attention mechanisms maps directly onto the multi-hub framing.** Maunsell's central argument — that "attention" denotes a *family* of mechanisms (gain on the driven response, change in shared variability, change in oscillatory coherence, change in decision criterion) rather than one — is the empirical analog of the user's multi-hub, multi-objective system (`threads/the_user_architectural_program.md` §5; `concepts/multi_hub_multi_objective_system.md`). The user's architectural commitment that *different hubs implement different aspects of attention*, with the central self-attention substrate aggregating their contributions, is the design-time reflection of Maunsell's empirical "different brain regions carry different signatures" claim. The two pictures are mutually reinforcing: the brain has multiple attention mechanisms because attention is what a multi-objective competition for shared representational bandwidth *looks like* when probed with task-specific behavioral readouts.

**Sensitivity vs. bias as hub decomposition.** Maunsell's emphasis on the sensitivity-vs-criterion dissociation (later sharpened by Luo & Maunsell 2018 in LPFC and Sridharan et al. 2017 for the SC) supports the user's program's commitment to architectural separation of *perceptual gain* and *decisional bias*. In the user's terms: the Feedback Transformer's V1 / V4-level gain (`concepts/feedback-transformer.md`) implements the sensitivity component; the central self-attention substrate and slow-memory feedback from PFC-analog hubs (PRISM v2's slow memory, `PRISM_V2_PROPOSAL.md` §3.3) implement the bias component. This is not a stylistic decomposition but a substantive one with neural-correlate predictions: probe the Recurrent ViT under sensitivity-vs-bias manipulations and the V1-gain locus should show modulation tracking d' while the slow-memory / decision-head locus should show modulation tracking criterion.

**Attention as gain modulation — the architectural commitment.** Reynolds & Heeger 2009 and McAdams & Maunsell 1999 (both reliability and tuning) are the primary papers; Maunsell 2015 is the review that endorses the package. The user's Feedback Transformer applies feedback to the Q/K/V projections via Hadamard product — multiplicative gain — exactly the operator Maunsell identifies as the canonical cortical attentional mechanism. PRISM v1's FiLM modulation ($\gamma_t \odot V_t + \beta_t$) is the same operator with an added affine offset. The Recurrent ViT's multiplicative-feedback variant (§6.7 of 2502.10955) makes the same commitment. Maunsell 2015 is the single-citation justification for *all three* of these architectural choices.

**Hierarchical gradient as design constraint.** The V1 → V4 → IT increase in modulation magnitude is the empirical anchor for the user's diminishing-feedback-into-deeper-layers design (`threads/the_user_architectural_program.md` §3). The user assigns more extensive feedback integration to deeper layers of the multi-compartmental memory; Maunsell shows that this is the gradient real cortex exhibits. Deeper layers in the architecture should therefore show larger attentional gain modulations when probed with the McAdams-Maunsell-style protocol.

**Noise correlation as a population-coding signature the architecture should reproduce.** Maunsell highlights the Cohen-Maunsell 2009 correlation result as the *population-level* mechanism behind behaviorally relevant attention. A Recurrent ViT or PRISM model claiming biological correspondence should be probed not only for single-unit gain (McAdams-Maunsell signature) but also for *attention-modulated reduction in pairwise unit correlation*. This is a sharper biological-plausibility criterion than single-unit gain alone.

**Validates the rejection of softmax-as-spotlight.** Reynolds & Heeger 2009 makes the point that attention is graded and distributed, not winner-take-all. Maunsell 2015 endorses it. PRISM's architectural commitment to *no softmax-over-locations* operation (`THESIS.md` §1.2) is licensed by this consensus. The Recurrent ViT's softmax is a learned divisive normalization rather than a discrete selection gate, which is consistent with Maunsell's framing of the softmax-like normalization circuit as the substrate of competition rather than as a winner-take-all selector.

**Gamma synchronization as an open architectural question.** Maunsell discusses gamma coherence as an attention signature largely orthogonal to firing-rate gain. The Recurrent ViT and PRISM both currently implement only rate-coded attention; they have no oscillatory-coherence analog. Whether the user's multi-hub system would benefit from explicit phase or timing-domain coordination among hubs (analogous to gamma) is an open question that Maunsell's review puts on the table.

**Empirical benchmark for "biologically plausible attention."** The review's quantitative anchors — V4 gain ≈ 1.2–1.5, noise correlation reduction ≈ 40%, hierarchical gradient with V1 ≈ 1.08 and IT > 1.5 — are *target distributions* that a trained Recurrent ViT or PRISM model should match if it is to be read as a primate-cortex analog. A Recurrent ViT whose attended-vs-unattended hidden-unit response ratio is far outside the 1.1–1.5 range is implementing attention in a way that does not match the cortical reference.

**Connection to the user's coalition-competition thesis.** Maunsell's claim that multiple distinct mechanisms underlie attention is consistent with the user's *competition-emergent-PC* account (`concepts/competition-emergent-predictive-coding.md`): if attention is whatever a multi-coalition competition for representational bandwidth *produces* under varying task demands, then it should look multi-mechanism in exactly the way Maunsell documents. The user's thesis predicts the multiplicity Maunsell observes; Maunsell's empirical synthesis is therefore (retrospective) evidence for the user's framing.

**Sensitivity-vs-bias decomposition as the analog of hub decomposition.** The clean conceptual move Maunsell makes — partitioning attention's behavioral effects into d' (sensitivity) and β (criterion) and assigning them to *different brain regions* — is structurally the same move the user makes architecturally with the multi-hub decomposition. In both cases, what looks like a unitary behavioral phenomenon ("the subject is paying attention") decomposes into separable computational sub-effects, each with its own substrate, that *interact* to produce the unified behavioral signature. The user's MSI / RL / VAE hub structure is the architectural-level realization of the sensitivity / bias / context decomposition Maunsell sketches at the empirical level. Future versions of the user's program can invoke Maunsell 2015 as the empirical license for *not* trying to compress attention into a single architectural component.

**Implications for the Recurrent ViT's published claim.** The recurrent ViT (2502.10955) reports cued-attention effects in a recurrent transformer trained on change detection. Under the Maunsell 2015 framing, those behavioral effects should not be expected to factor into a single neural signature; the model's hidden state should — if biologically faithful — show *both* sensitivity-like gain modulations on the V1-stem hidden units *and* criterion-like shifts in the recurrent state that drives the decision head. A future analysis decomposing the ViT's behavioral attention effects into SDT components (per Sridharan et al. 2017's multialternative framework) and mapping each component onto the corresponding hidden-state locus would be the cleanest demonstration of the ViT's biological correspondence. Maunsell 2015 is the citation that warrants this kind of multi-mechanism analysis.

## 8. Citations to follow

- `treue_martinez_trujillo1999_feature_attention` — feature-similarity-gain in MT; the partner result to McAdams & Maunsell 1999. In seed.
- `cohen_maunsell2009_correlations` — population-level noise-correlation reduction; the second leg of the V4 attention signature. In seed.
- `fries_etal2001_gamma_attention` — gamma-band synchronization signature of attention; the timing-domain leg. Not yet in seed.
- `bichot_etal2005_fef_v4_top_down` — FEF microstimulation as source of V4 attentional gain. Not yet in seed.
- `mitchell_sundberg_reynolds2007_variance` — refines the McAdams-Maunsell reliability result with simultaneous recordings. Not yet in seed.
- `mitchell_sundberg_reynolds2009_correlations` — V4 correlation reduction in awake monkeys, parallel to Cohen & Maunsell 2009. Not yet in seed.
- `williford_maunsell2006_v1_attention` — V1 attentional gain quantification, the small-effect anchor of the hierarchical gradient. Not yet in seed.
- `ghose_maunsell2002_task_timing` — attention's temporal sharpening to task-relevant intervals. Already in seed.
- `hawkins1990_attention_detectability` — early SDT-attention paper; foundational for sensitivity-vs-criterion split. In seed.
- `martinez_trujillo_treue2004_attention_tuning` — feature-similarity gain tuning curves. Not yet in seed.
- `reynolds_pasternak_desimone2000_attention_contrast` — contrast-gain vs response-gain disambiguation in V4. Not yet in seed.
- `bisley_goldberg2010_parietal_priority` — priority-map account of where attention's bias signal originates. In seed.
- `krauzlis2013_sc_attention` — superior-colliculus role in attention. In seed.
- `bundesen_habekost_kyllingsbaek2005_tva` — Bundesen's Theory of Visual Attention; computational decomposition of attentional capacity. Not yet in seed (in `the_user_architectural_program` §8 open debts).
- `motter1993_v1_v2_attention` — V1 / V2 attention with strong task demands; the upward revision of the Moran-Desimone V1-null. Not yet in seed.
- `treue_maunsell1996_mt_attention` — MT attention; predecessor to Treue & Martínez-Trujillo. Not yet in seed.
- `spitzer_desimone_moran1988_attention` — early IT-attention recordings; foundational lineage. Not yet in seed.
- `bisley_goldberg2003_lip` — LIP priority-map evidence; partial answer to "where the gain comes from". Adjacent to `bisley_goldberg2010_parietal_priority`.
- `gregoriou_etal2009_high_freq_long_range` — FEF-V4 gamma coherence during attention; the long-range coupling result the gamma-synchrony argument depends on. Not yet in seed.
