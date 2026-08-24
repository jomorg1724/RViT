---
id: failing_theeuwes2018_selection_history
title: "Selection history: how reward modulates selectivity of visual attention"
authors:
  - "Failing, Michel"
  - "Theeuwes, Jan"
year: 2018
venue: "Psychonomic Bulletin & Review"
doi: "10.3758/s13423-017-1380-y"
arxiv: ""
url: "https://pubmed.ncbi.nlm.nih.gov/28986770/"
tags:
  - visual-attention
  - review
  - psychophysics
concepts:
  - reward-modulated-attention
  - priority-map
  - attentional-template
related:
  - hickey2010_reward_salience_acc
  - desimone_duncan1995_biased_competition
  - krauzlis2013_sc_attention
  - glimcher2011_dopamine_rpe
  - awh2006_attention_wm
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_90
status: full
depth: full
last_updated: "2026-05-15"
---

# Selection history: how reward modulates selectivity of visual attention

## 1. Abstract

Visual attention enables us to selectively prioritize or suppress information in the environment. Prominent models concerned with the control of visual attention differentiate between goal-directed, top-down and stimulus-driven, bottom-up control, with the former determined by current selection goals and the latter determined by physical salience. In the current review, the authors discuss recent studies that demonstrate that attentional selection does not need to be the result of top-down or bottom-up processing but, instead, is often driven by lingering biases due to the "history" of former attention deployments. The review mainly focuses on reward-based history effects; yet other types of history effects such as (intertrial) priming, statistical learning, and affective conditioning are also discussed. The authors argue that evidence from behavioral, eye-movement, and neuroimaging studies supports the idea that selection history modulates the topographical landscape of spatial "priority" maps, such that attention is biased toward locations and features having the highest activation on this map.

## 2. Why this matters for us

This review establishes a third class of attentional control, in addition to top-down goals and bottom-up salience: a *learned, persistent bias* installed by the history of past selections and reinforced by reward. For the Recurrent ViT and PRISM, this is the most direct cognitive-neuroscience license for the idea that a model's attention map is not fully determined by the current input or the current task instruction, but by an internal state carrying forward the consequences of past selections. The recurrent feedback loop $H^{(t-1)} \to H^{(t)}$ in the Recurrent ViT and the value-shaped attention emerging from PPO training in PRISM are computational analogues of the priority-map biases this review documents in humans.

## 3. Key claims

1. The classical top-down vs. bottom-up dichotomy of attentional control is insufficient: a third source, selection history, must be added to account for empirical biases that are neither goal-aligned nor salience-aligned.
2. Reward-associated stimuli capture attention even when they are task-irrelevant, no longer rewarded, physically non-salient, and known by the observer to be unhelpful — i.e., the effect resists strategic suppression.
3. Reward-based selection-history effects generalize across feature dimensions (color, orientation, shape, location) and across response modalities (manual RT, saccade latency, saccade trajectory, EEG signatures such as the N2pc).
4. Other history-based phenomena — intertrial feature priming (priming of pop-out), statistical/contingency learning of distractor or target locations, and affective conditioning — share the same signature: a persistent bias not reducible to current goals or current salience.
5. The most parsimonious mechanistic account is that all three control sources (goals, salience, history) converge on a single spatial *priority map*; selection history modifies the topography of this map by raising activation at locations/features that were rewarded or recently selected.
6. The priority-map account locates the integration site in parietal cortex (LIP, IPS) and FEF, with subcortical contributions from the superior colliculus and a dopaminergic gating signal from VTA/SNc shaping the weights.
7. History effects appear within a few trials, persist for minutes to days, and can survive across sessions, which distinguishes them from short-lived bottom-up salience but also from declaratively held top-down goals.

## 4. Methods

This is a narrative review rather than a single experiment. The authors synthesize roughly a decade of behavioral, eye-tracking, EEG, fMRI, and (in animals) electrophysiology studies on reward-based attentional bias. The principal experimental paradigms surveyed are:

- **Value-driven attentional capture (Anderson, Laurent & Yantis 2011 style).** A training phase pairs specific colors (or other features) with high vs. low monetary reward in a search task where the feature *is* the target. A subsequent test phase uses the previously rewarded features as singleton distractors in a task where they are task-irrelevant and no longer rewarded. RT and accuracy costs imposed by the formerly rewarded distractor index history-based capture.
- **Reward-modulated singleton search.** Reward is delivered contingent on selecting a particular singleton; subsequent trials measure how the reward history biases capture by that feature.
- **Implicit / statistical contingency learning.** Target or distractor locations are sampled non-uniformly across trials without informing the participant; the resulting spatial bias is measured.
- **Pavlovian / affective conditioning.** A stimulus is paired with an aversive or appetitive US in a separate phase; later attentional capture by the CS is measured.
- **Neurophysiological / neuroimaging probes.** Reward modulation of N2pc, Pd, and reward positivity (ERPs); fMRI BOLD in LIP, FEF, ACC, ventral striatum; single-unit responses in LIP and SC under reward manipulations.

Each section synthesizes effect sizes and replication status across labs. The review does not perform a quantitative meta-analysis but flags converging evidence and identifies cases where claims rest on a single study.

## 5. Results

Specific findings the authors emphasize:

- Value-driven distractors slow target RTs by ~20–60 ms and reduce accuracy by several percentage points relative to unrewarded distractors, with effects persisting for at least 6 months after the reward-pairing phase (Anderson et al.).
- The N2pc — a parietal-occipital ERP component indexing covert attentional deployment ~200–300 ms post-stimulus — is elicited by previously rewarded distractors even when these are not goal-relevant, indicating attention is genuinely deployed to the location rather than merely a post-selection conflict signal.
- Saccade trajectories curve toward previously rewarded distractor locations (curvature effect of ~1–3° of visual angle), again indexing oculomotor priority elevation.
- Statistical learning of high-probability distractor locations produces RT facilitation that develops over tens of trials and remains stable for many trials after the contingency is removed; participants are typically unaware of the contingency, ruling out a top-down strategic account.
- fMRI: BOLD activity in IPS / posterior parietal cortex and in FEF tracks the value of distractors; striatal and ACC activity covaries with the magnitude of reward learning. The Hickey-Chelazzi-Theeuwes (2010) ACC result is cited as one anchor for the loop that writes reward signals into the priority map.
- Electrophysiology in LIP (Peck et al. 2009 and follow-ups) shows that LIP neurons code a stimulus' learned reward value even when that stimulus is currently being used as a distractor — the priority-map signal is reward-modulated at the level of single neurons.
- Effects of intertrial priming and reward generalize across many feature dimensions and even across task contexts, supporting the priority-map integration hypothesis.

## 6. Critique / limitations

- **Operational vs. theoretical separation of "history" from "top-down."** The authors define top-down as *current* explicit goal and history as *past* selections, but most history effects could in principle be re-described as implicit, automatized top-down templates. The review acknowledges this ambiguity but does not fully resolve it.
- **No formal computational model.** The priority-map framework is verbal. The review does not commit to a specific learning rule (e.g., reward-prediction-error gated Hebbian update vs. value-based reinforcement of saliency weights), leaving the mechanism underspecified.
- **Reliance on RT / accuracy proxies.** The behavioral measures used to infer attentional priority are downstream of many processes; the review's strongest causal evidence comes from electrophysiology and eye-movement results, which are themselves limited in number.
- **Generalization across timescales.** History effects ranging from one-trial priming (~seconds) to value-driven capture (~months) are lumped under one umbrella. Whether they share a common substrate or merely a common phenomenological label is left open.
- **Limited treatment of suppression history.** The asymmetry between selection-history (facilitatory) and distractor-suppression history (inhibitory) effects is acknowledged but not deeply analyzed; subsequent work (Wang & Theeuwes 2018; Geng 2014) has since argued the inhibitory side may be a distinct learning system.
- **Sample homogeneity.** Most cited studies use young adult university samples with monetary reward; generalization to other populations and to other reinforcer types remains thin.

## 7. Connection to our work

This review is the most direct cognitive-neuroscience license in the database for the architectural commitments of both the Recurrent ViT and PRISM v2 — specifically, the commitment that attention is shaped not only by the current input and the current goal, but by a persistent, learned internal state that survives across timesteps and across episodes. The mapping is concrete:

**Recurrent ViT (2502.10955).** The recurrent memory $H^{(t-1)}$ enters the attention computation as multiplicative or additive feedback (paper §6.7). Functionally, this is the architecture's *selection-history* channel: it carries forward a representation of what was attended on previous frames and biases the current attention map accordingly. The review provides empirical license that real brains do exactly this, on timescales from one trial to many sessions. It also implies a falsifiable behavioral signature: if the recurrent feedback is genuinely implementing a priority-map-style history bias, then ablating it should disproportionately impair conditions in which the to-be-attended location was unpredictable from the current frame but predictable from the recent history.

**PRISM v1 and v2.** PPO training in PRISM (`THESIS.md` §3; `PRISM_V2_PROPOSAL.md` §4) gradient-shapes the attention pattern $M_t$ via the reward signal in exactly the way the review documents in primates. The persistent learned bias toward task-rewarded features that emerges over training in PRISM has the same operational signature as the value-driven attentional capture this review reviews — a feature being attended because it was once predictive of reward, even when current bottom-up salience does not favor it. This grounds the architectural choice of an RL-trained attention head in a robust empirical literature rather than in pure ML pragmatism.

**Architectural program (the_user_architectural_program thread).** The Feedback Transformer's commitment to integrating multiple internal states into the Q/K/V projections (§1 of the thread) is the natural generalization of priority-map integration in cortex. The review's parietal-priority-map hypothesis maps onto a single integration site combining goal-driven (top-down feedback from a goal hub), salience-driven (bottom-up sensory), and history-driven (recurrent memory) signals into a single attention map. This is precisely the architectural primitive the user is committed to, and Failing & Theeuwes supply the cognitive-level evidence that brains require all three sources at one integration node.

**Competition-emergent predictive coding (§5 of the thread).** Reward-based selection history is one of the clearest cases of a competing internal coalition (the value/RL hub) writing into the attention map at the expense of the current task hub. The review's emphasis that the effect persists even when participants explicitly know the reward-associated feature is unhelpful is consistent with the user's view that hub-level competition is not arbitrated by a strategic top-down controller but by a more basic priority-arbitration mechanism.

**Direct empirical anchor for the Hickey et al. (2010) ACC result.** This paper and Hickey 2010 are co-cited (vit_paper_refs 89 and 90); the review provides the framework within which the ACC result is interpreted as the dopamine-gated writer of reward signals into the parietal priority map.

## 8. Citations to follow

- anderson_laurent_yantis2011_value_driven_capture — the foundational behavioral demonstration of value-driven attentional capture that the review's reward section is built around.
- peck_jangraw_suzuki_efem_gottlieb2009_lip_reward — LIP single-unit reward coding, the electrophysiological anchor for the priority-map account.
- wang_theeuwes2018_statistical_learning_distractor_suppression — the suppression-history complement to selection-history, addressing the asymmetry §6 flags.
- chelazzi_perlato_santandrea_dellibera2013_reward_priority_map — explicit reward-on-priority-map proposal central to the review's mechanistic claim.
- bisley_goldberg2010_lip_priority_map — the canonical LIP-as-priority-map review the authors lean on.
- maunsell2004_reward_signals_visual — early demonstration of reward modulation in extrastriate visual cortex.
- awh_belopolsky_theeuwes2012_history_third_factor — the proposal paper that introduced "selection history" as a third control axis; this review elaborates and tests it.
- geng2014_attentional_mechanisms_distractor_suppression — the active-suppression alternative the review treats as an open question.
- theeuwes2010_top_down_bottom_up — Theeuwes's prior defense of stimulus-driven capture, useful as the dialectical predecessor to this review.
