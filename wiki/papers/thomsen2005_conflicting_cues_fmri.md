---
id: thomsen2005_conflicting_cues_fmri
title: "Processing of conflicting cues in an attention-shift paradigm studied with fMRI"
authors:
  - "Thomsen, Tormod"
  - "Specht, Karsten"
  - "Ersland, Lars"
  - "Hugdahl, Kenneth"
year: 2005
venue: "Neuroscience Letters"
doi: "10.1016/j.neulet.2005.01.026"
arxiv: ""
url: "https://pubmed.ncbi.nlm.nih.gov/15854766/"
tags:
  - visual-attention
  - human-neuroimaging
  - posner-cuing
  - parietal-cortex
concepts:
  - cueing-effect
  - validity-effect
  - attentional-spotlight
  - top-down-feedback
related:
  - posner1980_orienting
  - brisson_jolicoeur2008_express_reengagement
  - bisley_goldberg2010_parietal_priority
  - clark2015_prefrontal_attention
  - gazzaley_nobre2012_topdown
  - silver2005_topographic_parietal
  - weiler2025_l6_corticocortical
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_47
status: full
depth: full
last_updated: "2026-05-16"
---

# Processing of conflicting cues in an attention-shift paradigm studied with fMRI

## 1. Abstract

The paper reports a single fMRI experiment using a modified Posner cueing paradigm in which a peripheral
exogenous cue and a central endogenous (symbolic) cue are presented simultaneously and convey *conflicting*
directional information. Two crucial conditions are contrasted: "exogenous invalid / endogenous valid" (the
peripheral flash points to the wrong side; the central arrow points to the correct side) and "exogenous valid
/ endogenous invalid" (the reverse). Behaviorally, reaction times are significantly longer when the exogenous
cue is invalid, indicating that the bottom-up peripheral cue captures attention even when a competing top-down
central cue is available. fMRI shows activation of bilateral visual cortex, the left inferior parietal lobule,
and the left cingulate gyrus in both conflict conditions, with additional left frontal (inferior frontal gyrus
/ dorsolateral prefrontal) activation specifically in the exogenous-invalid / endogenous-valid condition. The
authors interpret the additional frontal activation as the neural signature of the extra top-down control
required to override an erroneous bottom-up capture, and they situate this finding within the Posner
two-systems framework.

## 2. Why this matters for us

This is the fMRI reference behind the Recurrent ViT paper's claim (ref [47] in 2502.10955) that conflicting
bottom-up and top-down spatial cues recruit a distinguishable frontoparietal control circuit beyond ordinary
covert orienting. The paper is the empirical anchor for two design decisions in our work: (i) that a model of
cue-driven attention should *exhibit* an extra computational cost when bottom-up and top-down cue signals
disagree (a behavioral analog of the prolonged RT and a representational analog of the additional frontal
activation); and (ii) that the architecture should plausibly contain distinct mechanisms for stimulus-driven
and memory-driven attention, since the human data dissociate their conflict from their cooperation. This is
the bridge between Posner's two-system framing (`posner1980_orienting`) and the multi-hub feedback structure
central to `the_user_architectural_program`.

## 3. Key claims

1. When peripheral (exogenous) and central (endogenous) cues are presented simultaneously with conflicting
   spatial information, the exogenous cue dominates behavior: RTs are longer when the peripheral cue is
   invalid even if the central arrow is valid.
2. Cue conflict per se activates a common network across both conflict directions: bilateral occipital visual
   cortex, left inferior parietal lobule, and left cingulate gyrus.
3. Overriding an invalid exogenous cue with a valid endogenous cue specifically recruits left frontal cortex
   (inferior frontal / dorsolateral prefrontal) in addition to the common conflict network.
4. The asymmetry between conflict directions is interpreted as evidence that top-down endogenous control is
   recruited only when needed to suppress an erroneous bottom-up capture, consistent with a frontoparietal
   executive system that is engaged on demand rather than continuously.
5. The cingulate activation in both conflict conditions is consistent with the standard role of anterior
   cingulate in conflict monitoring and is not specific to which cue type was misleading; the parietal
   activation is consistent with the inferior parietal lobule operating as a stimulus-locked priority map
   whose content is modulated but not gated by top-down expectations.

## 4. Methods

A modified Posner spatial cueing paradigm was used. Each trial presented two cues simultaneously: a peripheral
flash (exogenous, bottom-up) on one side, and a central directional arrow (endogenous, top-down). The cues
were either congruent (both pointing to the upcoming target location) or conflicting (one pointing to the
target, the other to the opposite side). Target detection was the subject's task; reaction times were recorded
throughout.

The two critical conflict conditions — "exogenous invalid / endogenous valid" (peripheral flash misleads,
central arrow tells the truth) and "exogenous valid / endogenous invalid" (central arrow misleads, peripheral
flash tells the truth) — were contrasted against each other and against the congruent baseline. Validly cued
conditions provided the implicit reference for the standard cueing benefit and a control on overall
trial-level processing demand.

fMRI BOLD signal was acquired during the task on a clinical scanner with echo-planar imaging, and analyzed
with standard whole-brain general linear model statistics; contrasts targeted condition-specific activation
differences using corrected statistical thresholds appropriate to the era. The participant sample comprised
healthy adults (single-digit to low-double-digit N, typical of an early-2000s *Neuroscience Letters* short
report). Eye movements were not centrally reported, but the central fixation requirement was enforced as a
behavioral constraint, so the orienting effects should be treated as covert.

## 5. Results

Behavior. Reaction times in the exogenous-invalid / endogenous-valid condition were significantly longer than
in the exogenous-valid / endogenous-invalid condition, demonstrating that the peripheral cue captures
attention even when a valid central cue points elsewhere. This is the behavioral validity-effect asymmetry:
the cost of overriding a bottom-up capture exceeds the cost of overriding a top-down expectation. Peripheral
capture appears to be the default operating mode of the visual orienting system, consistent with Posner's
classification of exogenous attention as fast and stimulus-bound.

fMRI. Common to both conflict conditions, relative to congruent trials: bilateral occipital visual cortex,
left inferior parietal lobule, and left cingulate gyrus. Specific to the exogenous-invalid / endogenous-valid
condition, relative to the reverse conflict: additional left frontal activation, in inferior frontal /
dorsolateral prefrontal regions. The authors do not report large effect sizes in absolute BOLD units (typical
of the era and journal), but the directional contrasts are statistically significant at corrected thresholds.
No reliable RT difference is reported in the congruent baseline that would confound the interpretation of the
conflict-specific frontal signal.

The fMRI pattern therefore decomposes the conflict response into two components: a generic conflict-detection
/ priority-map signal (cingulate + parietal + occipital), present whenever any disagreement exists between
cues, and a conflict-resolution / top-down-override signal (frontal), present only when the resolution
requires suppressing a captured exogenous orientation. This double-dissociation between detection and
resolution is the principal scientific contribution of the paper.

## 6. Critique / limitations

The sample size is small by modern fMRI standards, and the statistical thresholds are those of mid-2000s
whole-brain analysis, which has known false-positive issues (Eklund et al. 2016). Effect-size estimates and
any voxel-wise replication should therefore be treated as provisional pending a better-powered re-test.

The "frontal activation" cluster is reported at a single laterality (left) and the lateralization is not
strongly defended; later work has typically found bilateral or right-lateralized engagement of the
dorsolateral prefrontal / inferior frontal cortex in conflict and reorienting tasks (Corbetta & Shulman 2002
ventral attention network is canonically right-lateralized), so the laterality claim should be treated
cautiously and may be sample-specific.

The paradigm uses simultaneous cues, which conflates competition for *attentional* control with competition
for *perceptual* representation of the cues themselves; designs with staggered SOAs (e.g., Brisson & Jolicoeur
2008) better dissociate the two by allowing exogenous attention to reach its peak (~100 ms) before the
endogenous cue is presented. The simultaneous-cue design also limits inference about which system "wins": the
answer here is "bottom-up always wins" but it is not clear whether this reflects a true hierarchical priority
of stimulus-driven capture or merely the relative processing speed of peripheral vs. central cues at the
chosen latencies.

The cingulate cluster is interpreted as conflict monitoring, but the same anatomy is engaged by
error-likelihood, effort, and motor preparation, so this attribution is not unique. A control task that varies
motor demand without varying cue conflict would have tightened the interpretation.

Finally, the central theoretical contribution — that override-of-bottom-up requires extra frontal control — is
descriptively supported but not causally established; lesion or TMS evidence is required to confirm that the
frontal activation is necessary, not merely correlated.

## 7. Connection to our work

The architectural commitment in the Recurrent ViT and in PRISM is that a cue-driven attentional system should
have separate substrates for stimulus-driven and memory-driven orienting, and that these substrates should
*interact*, not merely add. Thomsen et al. supply the human-neuroimaging evidence that this interaction is
real and asymmetric — bottom-up capture is the default, and top-down control is recruited specifically when
the default is wrong.

**Recurrent ViT response to conflicting cues.** The published architecture (2502.10955) contains a single
feedback source $H^{(t-1)}$ that integrates with bottom-up sensory input $X^{(t)}$ via either token, additive,
or multiplicative feedback (§6.7). Under any of these schemes, a *conflict* between the bottom-up cue
presented at $t = 1$ and the top-down memory expectation derived from a different prior cue should produce a
measurable RT-analog (delayed change-detection response, requiring more recurrent steps to converge on the
correct localization) and a measurable internal-state perturbation (the memory has to "win" against the
bottom-up input). This is the closest computational analog of Thomsen's exogenous-invalid / endogenous-valid
contrast. If the model does *not* exhibit this asymmetry, the architecture has under-specified the top-down
route — a falsifiable diagnostic that can be checked directly against the existing change-detection
environment by introducing trials with a planted cue-vs-memory conflict. We can further test whether the
magnitude of the cost scales with feedback strength: a multiplicative-feedback variant should produce a larger
override cost than an additive one, because the top-down expectation modulates the attention scores rather
than merely adding to them.

**Frontoparietal attention-control network analog.** Thomsen's frontoparietal network maps onto the multi-hub
structure in `the_user_architectural_program` §3 (multi-compartmental memory) and §5 (competition-emergent
predictive coding). The inferior parietal lobule is the classical priority map (Bisley & Goldberg 2010 in
`related:`) — in our terms, the bottom-up sensory hub closest to V1/V2, which Silver et al. (2005) (in
`related:`) identifies as retinotopically organized. The dorsolateral prefrontal / inferior frontal cluster
recruited specifically when overriding bottom-up capture is the classical top-down control hub (Clark 2015;
Gazzaley & Nobre 2012 in `related:`) — in our terms, a memory hub at the apex of the hierarchy whose
descending projections must "win" the self-attention competition (the formal account in
`the_user_architectural_program` §5). The cingulate activation common to both conflict directions corresponds,
in the user's program, to the conflict signal that incentivizes hub-cooperation (the
diminishing-feedback-into-deeper-layers design choice, §3 of the thread). This is *precisely* the kind of
competition the user's architecture is built to instantiate: when two hubs (bottom-up sensory, top-down
memory) signal conflicting predictions about the next attention map, a third process (the cingulate analog, or
in our architecture the cross-hub feedback transformer integration) must arbitrate, and the arbitration cost
shows up both behaviorally (longer RT) and representationally (additional activation in the controlling hub).

A subtler connection: Thomsen's asymmetry — overriding bottom-up is harder than overriding top-down — argues
that the bottom-up route is the default winner of the competition, and the top-down route is the exception.
This is consistent with the user's commitment that *bottom-up* sensory projections enter every layer of the
memory hierarchy unconditionally, while top-down feedback diminishes with depth
(`the_user_architectural_program` §3). The architectural asymmetry mirrors the empirical asymmetry. A model in
which top-down and bottom-up routes were symmetric would predict equal RT in the two conflict conditions,
which contradicts Thomsen — so the empirical result falsifies the symmetric variant and licenses the
asymmetric one.

There is also a clean mapping to the formal competition account in `the_user_architectural_program` §5. Under
that account, each hub's query and key are gain-modulated by other hubs' contributions: $q_i = s_{q,i} \odot
(c^{(\text{RL})}_{q,i} + c^{(\text{dec})}_{q,i})$. When the bottom-up contribution $s_{q,i}$ and the top-down
contribution $c_{q,i}$ point to *different* spatial locations, the Hadamard product is small at both locations
and the attention map is forced into a low-confidence state. Resolving this requires an additional control
signal — exactly the role Thomsen ascribes to the left frontal cluster. The cingulate's conflict-detection
role corresponds to monitoring the entropy of this attention map, and recruiting additional control capacity
when entropy is high.

The bottom line: ref [47] in 2502.10955 supports the architectural commitment to distinct top-down and
bottom-up integration pathways (§6.7) and the prediction that conflict between them carries a measurable
behavioral cost. The current single-source feedback variant ($H^{(t-1)}$ only) is an under-specified version
of this; the full Feedback Transformer treatment (`the_user_architectural_program` §1) with parallel hubs is
the architecture that the Thomsen result more naturally licenses. A future Recurrent ViT experiment that
manipulates cue conflict — varying the relative reliability of exogenous and endogenous routes — would test
whether the model recapitulates not only the validity effect (Figure 3) but also the conflict-override
asymmetry Thomsen et al. document.

## 8. Citations to follow

- `corbetta_shulman2002_dorsal_ventral_attention` — the canonical fMRI synthesis of dorsal (top-down) and
  ventral (stimulus-driven) attention networks; Thomsen's results sit squarely inside this framework.
- `botvinick2001_conflict_monitoring` — the anterior cingulate conflict-monitoring theory that Thomsen's
  cingulate cluster invokes; needed to evaluate the conflict-monitoring interpretation.
- `kerns2004_acc_cognitive_control` — fMRI test of conflict-monitoring → control-engagement; the mechanistic
  story Thomsen invokes for the frontal cluster.
- `egner_hirsch2005_conflict_resolution` — replicates the recruitment of dorsolateral PFC for conflict
  resolution under conflicting cues.
- `eklund2016_cluster_failure` — methodological reference for evaluating the false-positive risk in mid-2000s
  whole-brain fMRI.
- `weiler2025_l6_corticocortical` — laminar substrate for the top-down feedback route that overrides bottom-up
  capture (cited but not yet in seed; load-bearing for the user's program).