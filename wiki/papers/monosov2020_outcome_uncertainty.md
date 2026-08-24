---
id: monosov2020_outcome_uncertainty
title: "How outcome uncertainty mediates attention, learning, and decision-making"
authors:
  - "Monosov, Ilya E."
year: 2020
venue: "Trends in Neurosciences"
doi: "10.1016/j.tins.2020.06.009"
arxiv: ""
url: "https://doi.org/10.1016/j.tins.2020.06.009"
tags:
  - primate-neurophysiology
  - review
  - decision-making
  - dopamine
  - subcortical
concepts:
  - reward-modulated-attention
  - precision-weighting
  - priority-map
  - attention-as-prediction-error
  - distributional-rl
related:
  - feldman_friston2010_attention_free_energy
  - glimcher2011_dopamine_rpe
  - babayan_uchida_gershman2018_belief_states_dopamine
  - haber2015_cbgtc_circuits
  - pezzulo_parr_friston2024_active_inference
  - bays2024_wm_representation
  - friston2010_fep_unified_theory
  - botvinick2020_deep_rl_neuro
  - dabney2020_distributional_dopamine
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_115
status: full
depth: full
last_updated: "2026-05-19"
---

# How outcome uncertainty mediates attention, learning, and decision-making

## 1. Abstract

Nervous systems enable organisms to predict future outcomes and to manage uncertainty about them, and adjusting behavioral and learning policies to the current level of uncertainty is essential for survival in non-stationary environments. This review surveys recent discoveries in primate neuroscience that identify dedicated circuits — distributed across subcortical, basal-ganglia, and prefrontal regions — that encode reward uncertainty distinctly from expected value and reward prediction error. These uncertainty signals are proposed to guide three intertwined functions: information-seeking (where to look and what to sample), attentional allocation (which sensory channels are amplified), and learning rate (how strongly to update beliefs from new evidence). The review closes by considering implications for learning in artificial systems, where a uniform learning rate and a single critic value head obscure the rich structure that biological uncertainty circuits exploit.

## 2. Why this matters for us

Monosov 2020 supplies the *uncertainty-mediates-attention* narrative that bridges the user's RL hub (reward-modulated attention) and the precision-weighting framework (Feldman & Friston 2010). The Recurrent ViT (2502.10955) treats attention as gated by a fixed cue token; Monosov's review establishes that in primates the *reliability* of the cue — its uncertainty content — is computed by separate circuits and feeds back into where attention is deployed and how fast learning occurs. For the user's multi-hub program this is the empirical license to give the RL hub a privileged channel into the Feedback Transformer, because uncertainty signals in biology *do* gate attention. For PRISM v2's variational machinery, this is the empirical-neuroscience anchor for the claim that the variance of the posterior is itself a behaviorally important quantity, not merely a regularization knob. It is also the bridge from the cited reference 115 in the recurrent-ViT manuscript into the broader neuroscience program: uncertainty-modulated attention is one of the few places where reward-system anatomy and visual-attention behavior demonstrably converge.

## 3. Key claims

1. Outcome uncertainty is a distinct neural quantity, computed and represented separately from expected value and reward prediction error, by dedicated circuits in primate brain.
2. Multiple uncertainty types are dissociated neurally: *expected uncertainty* (known variance of a familiar distribution; "risk"), *estimation uncertainty* (incomplete knowledge of a stationary distribution), and *unexpected uncertainty* (change-points indicating that the generative process has shifted).
3. Reward uncertainty signals are carried by neurons in the anterior cingulate cortex, orbitofrontal cortex, basal ganglia output structures, and pallidal regions; the lateral habenula and dopamine neurons additionally carry reward prediction error in a manner that is modulated by belief-state uncertainty.
4. These uncertainty representations drive *information-seeking*: animals exert costly effort to obtain advance information about uncertain outcomes even when that information cannot change the outcome — a behavior recapitulated by single-unit responses in the same circuits.
5. Uncertainty modulates attentional priority: the more uncertain a predicted outcome, the more attention is drawn to the cues and contexts that predict it, in line with Pearce-Hall associability theory.
6. Uncertainty controls learning rate: high uncertainty (especially unexpected) drives faster belief updates, consistent with Kalman-filter and Bayesian-surprise accounts of associative learning.
7. The same uncertainty circuits in primates that drive information-seeking, attentional allocation, and learning rate plausibly furnish the priors required for resolving ambiguity in perceptual inference — pointing to a unified role for uncertainty across cognitive subsystems.
8. Artificial agents trained with a single scalar value critic miss this structure. Algorithms that explicitly represent uncertainty (e.g., distributional RL, ensemble critics) recover some of the function but do not match the dissociation observed in biology.

## 4. Methods

This is a review article. The methodological scope is therefore the literature it surveys: primate single-unit electrophysiology in awake macaques performing Pavlovian and instrumental conditioning tasks with parametrically manipulated reward probability and magnitude; pharmacological and lesion studies in the same animals; functional imaging in humans on comparable paradigms; and computational modeling work (Kalman filters, Pearce-Hall, hierarchical Bayesian inference, distributional RL) that places the empirical findings in formal frameworks. No new experimental data is reported. Monosov organizes the survey around four behavioral functions (information-seeking, attention, learning, decision-making) rather than around brain regions, and then maps each function onto the candidate circuits.

The structure of the review is: (i) define the taxonomy of uncertainty (risk, ambiguity, estimation, unexpected); (ii) survey the neural correlates of each in primate circuitry; (iii) link each uncertainty signal to a behavioral function; (iv) propose unifying computational principles; (v) discuss implications for artificial learning systems.

Formally, the review canonicalizes the following decomposition. Let $r$ be a future reward with belief distribution $p(r \mid h_t)$ conditional on history. The agent's *expected uncertainty* is $\text{Var}_{p(r \mid h_t)}[r]$ — the known variance of the predictive distribution given a stable generative model. *Estimation uncertainty* is the variance of the agent's posterior over the parameters of that generative model, $\text{Var}_{p(\theta \mid h_t)}[\mathbb{E}_{p(r \mid \theta)}[r]]$. *Unexpected uncertainty* is the posterior probability that the generative model has changed at time $t$, $p(\text{change}_t \mid h_t)$. The review's central empirical claim is that primate brain implements distinguishable representations of these three quantities, with different cell types and pathways for each.

## 5. Results

The review's principal empirical findings, drawn from cited primary literature:

- **Pallidal and habenular uncertainty coding.** Neurons in the primate basal forebrain and lateral habenula respond parametrically to reward uncertainty (variance of the predicted outcome), independently of expected value. Peak firing occurs at intermediate reward probability (~0.5), the variance-maximizing point.
- **Anterior cingulate and orbitofrontal uncertainty.** ACC and OFC neurons encode uncertainty at multiple timescales — instantaneous variance and accumulated estimation uncertainty — with separable populations.
- **Dopamine and belief states.** Midbrain dopamine reward prediction errors are scaled by the current belief state and its uncertainty, consistent with the Babayan-Uchida-Gershman belief-state framework; dopamine therefore does not encode a model-free error in primates but a belief-state-weighted error.
- **Information-seeking behavior.** Monkeys and humans pay a cost (delay, effort, foregone reward) to obtain advance information that is behaviorally non-instrumental. Neural correlates of this information-seeking are found in the same uncertainty-coding regions; pharmacological inactivation reduces information-seeking selectively.
- **Pearce-Hall associability.** Pupil and ACC responses scale with associability rather than value, consistent with the prediction that uncertain cues attract more attention; associability dynamics match Pearce-Hall predictions quantitatively in human-fMRI studies.
- **Learning rate adaptation.** Behavioral learning rates rise after change-points (unexpected uncertainty) and fall during stable periods, tracking a normative Bayesian learner; the neural correlate is a transient surge in noradrenergic signaling and ACC activity at change-points.

The review does not produce its own quantitative comparison numbers; the function is to make the case that the disparate findings cohere under a single uncertainty-mediates-everything framework.

A unifying observation across the surveyed studies is that uncertainty representations are *not* monolithic — different cell populations within the same region (e.g., ACC) carry expected-uncertainty vs change-point signals, and the projection targets of these populations differ. The pallidal-habenular axis appears to be specialized for risk and information value; the ACC-locus coeruleus axis is specialized for change-point detection and learning-rate control; OFC bridges the two, providing belief-state context that scales dopaminergic RPE. The review therefore implicitly sketches a circuit-level division of labor that the user's multi-hub program can mirror in artificial form.

## 6. Critique / limitations

The review's framework is integrative rather than mechanistic. By collapsing multiple uncertainty taxonomies (risk, ambiguity, estimation, unexpected) into a single banner, the review smooths over real disagreements in the primary literature about whether these are dissociable computations or facets of one quantity. The Soltani-Izquierdo line (volatility vs stochasticity) and the Yu-Dayan line (expected vs unexpected uncertainty) propose different decompositions that the review treats as compatible without adjudicating.

The mapping from uncertainty signal to behavioral function is correlational. Causal evidence is limited to a handful of pharmacological-inactivation and lesion studies; the strong claim that ACC *computes* uncertainty rather than *reflecting* it is not yet established.

The artificial-learning closing section is brief and aspirational. Concrete predictions for how a multi-headed RL agent should be organized to mirror biology are not offered. Subsequent work (e.g., distributional RL critiques, model-based meta-RL) has continued to debate what counts as a satisfying engineering implementation of uncertainty-driven learning.

The review predates the active-inference unification of attention and uncertainty (Pezzulo, Parr & Friston 2024); it treats precision-weighting as one of several candidate frameworks rather than as a unifying account. The Bayesian and predictive-coding literatures are mentioned but not foregrounded.

Finally, the review's primate-centric scope obscures rodent work on the same circuits, where causal manipulation is more tractable; this limits the strength of the proposed mechanistic claims to what awake macaque recording can support.

## 7. Connection to our work

This paper is the empirical-neuroscience pillar under several commitments in the user's architectural program.

**The RL hub of the multi-hub system as an uncertainty-aware controller.** The user's `multi-hub-multi-objective-system` ([the_user_architectural_program §1, §5](research_db/threads/the_user_architectural_program.md)) posits an RL hub that competes for control of the central Feedback Transformer. Monosov's review establishes that in primates the structures plausibly implementing such a hub (ACC, basal ganglia, pallidum, habenula) compute uncertainty as a first-class signal, not just expected value. The RL hub's projection into the Feedback Transformer Q/K should therefore carry an uncertainty channel, not only a value channel — concretely, the $c^{(\text{RL})}_q$ feedback should be parameterized by both $\hat V$ and $\hat \sigma_V$.

**Uncertainty as precision in the Feldman-Friston framework.** The user's interpretation of attention as precision-weighting ([feldman_friston2010_attention_free_energy.md §7](research_db/papers/feldman_friston2010_attention_free_energy.md)) is most empirically supported when the *source* of precision is identified. Monosov's review identifies that source: uncertainty-encoding circuits in subcortex and prefrontal cortex are the candidates that supply precision modulation to sensory processing. This empirically grounds the otherwise abstract Friston-style precision parameter; it tells us what circuit, in a biologically realistic implementation, should set the multiplicative gain on prediction-error pathways.

**Uncertainty in PRISM's variational framework.** PRISM v1's inner inference loop (`THESIS.md` §2.8) and PRISM v2's hierarchical FiLM (`PRISM_V2_PROPOSAL.md` §3.4) implicitly carry uncertainty information in the posterior covariance, but neither uses it as a control signal for memory update gating or attentional allocation. Monosov's review suggests the right architectural move: the posterior variance $\Sigma_t$ of the memory state should *itself* feed back into the attention gate, mirroring the biological role of uncertainty in driving attentional priority. This is a concrete v3 extension.

**Competition-emergent PC and information-seeking.** The user's `competition-emergent-predictive-coding` thesis treats prediction error as strategic surprise. Monosov's information-seeking results — animals pay costs for non-instrumental information about uncertain outcomes — extend this story: a coalition that *can predict its rival* is also a coalition that *wants to sample evidence about the rival* when uncertain. The information-seeking circuits are then the natural empirical home for the strategic-sampling behaviors that the user's framework predicts must accompany competitive prediction.

**Bays continuous-resource framework and uncertainty.** The Bays-Schneegans line ([bays2024_wm_representation.md](research_db/papers/bays2024_wm_representation.md)) treats working-memory resource as graded precision per item. Monosov's review supplies the *source* of that precision in the biological system: uncertainty circuits set the precision budget. Linking the two suggests that working-memory load and attentional gating share a common control variable, with Monosov's pallidal-habenular-ACC circuit as a candidate substrate.

**The Recurrent ViT and validity-modulated cuing.** The published 2502.10955 result that cue validity modulates RT and accuracy is at present a fixed-precision phenomenon. Monosov's review suggests a v2 extension: rather than treating cue validity as a fixed scalar, treat it as a learned, dynamically updated uncertainty estimate supplied by an auxiliary head that explicitly tracks change-points in the input statistics. Concretely, a change-point head over the history of cue-target congruence would parameterize the precision channel of the Feedback Transformer; the predicted volatility would scale how strongly recent cues are weighted against accumulated priors, mirroring the noradrenergic-ACC mechanism Monosov surveys.

**Uncertainty-driven exploration vs strategic competition.** A subtle implication of Monosov's information-seeking results, when read through the user's competition-emergent-PC lens, is that the *cost-bearing* nature of information-seeking is exactly the kind of behavior the competition framework predicts for coalitions trying to model rivals. A coalition that incurs cost to sample evidence about an uncertain quantity is paying down the variance of its predictive model of that quantity — and in the user's reformulation, the relevant quantity is not just the world state but the state of a competing coalition. This suggests that primate information-seeking circuits may double as the architectural locus of strategic-sampling behavior in the multi-hub system, and that empirical signatures of "non-instrumental" information-seeking in biology may in fact be instrumental once the competitor-prediction objective is taken into account.

**Open scholarly debt: distributional RL.** Monosov closes with a brief gesture toward distributional RL ([taxonomy concept `distributional-rl`](research_db/TAXONOMY.md)) as the candidate engineering implementation of biological uncertainty coding. The user's RL hub is currently agnostic on this; aligning it with Monosov's framing argues for a distributional critic rather than a scalar one, with the variance of the return distribution providing the precision signal back into the Feedback Transformer. This is a concrete, testable architectural commitment that Monosov's review motivates from primate data.

## 8. Citations to follow

- `pearce_hall1980_associability` — the associability theory of attention to uncertain cues; foundational for Monosov's attention-uncertainty link. Not in seed.
- `dayan_kakade_montague2000_uncertainty_attention` — the original computational claim that uncertainty modulates associative learning rate. Not in seed; foundational.
- `kepecs2008_uncertainty_decision_confidence` — neural correlates of decision confidence and post-decision uncertainty in OFC. Not in seed.
- `nassar2010_change_point_learning_rate` — the canonical demonstration that human learning rates track change-point probability. Not in seed.
- `bromberg_martin_hikosaka2009_lateral_habenula_information` — early single-unit evidence for information-value coding in the habenula. Not in seed; closely tied to the review's information-seeking thread.
- `yu_dayan2005_uncertainty_neuromodulation` — the classic expected-vs-unexpected uncertainty dissociation; needed for any deepening. Not in seed.
- `soltani_izquierdo2019_volatility_stochasticity` — the modern reformulation of the uncertainty taxonomy. Not in seed.
- `bromberg_martin_monosov2019_uncertainty_pallidum` — the primary-data companion paper; pallidal uncertainty coding. Not in seed.
- `behrens2007_volatility_learning_rate` — the canonical fMRI demonstration that learning rate tracks volatility. Not in seed.
- `friston2010_fep_unified_theory` — the unifying variational-Bayes account that Monosov's framework can be mapped onto. In seed.
- `babayan_uchida_gershman2018_belief_states_dopamine` — the belief-state DA framework Monosov endorses. In seed; deepen.
- `glimcher2011_dopamine_rpe` — the canonical RPE story that Monosov refines with uncertainty. In seed.
- `haber2015_cbgtc_circuits` — the basal-ganglia loop anatomy in which Monosov's uncertainty circuits live. In seed.
- `pezzulo_parr_friston2024_active_inference` — the post-Monosov active-inference unification of attention, uncertainty, and information-seeking. In seed.
