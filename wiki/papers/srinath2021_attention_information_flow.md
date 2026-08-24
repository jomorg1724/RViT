---
id: srinath2021_attention_information_flow
title: "Attention improves information flow between neuronal populations without changing the communication subspace"
authors:
  - "Srinath, Ramanujan"
  - "Ruff, Douglas A."
  - "Cohen, Marlene R."
year: 2021
venue: "Current Biology"
doi: "10.1016/j.cub.2021.09.076"
arxiv: ""
url: "https://doi.org/10.1016/j.cub.2021.09.076"
tags:
  - primate-neurophysiology
  - visual-attention
  - decoding-analysis
concepts:
  - gain-modulation
  - top-down-feedback
  - divisive-normalization
  - precision-weighting
  - recurrence-for-temporal-dynamics
related:
  - cohen_maunsell2009_correlations
  - ruff_cohen2016_cross_area_correlations
  - mante2013_context_dependent_pfc
  - panichello_buschman2021_shared_mechanisms
  - kietzmann2019_recurrence_required
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_42
status: full
depth: full
last_updated: "2026-05-14"
---

# Attention improves information flow between neuronal populations without changing the communication subspace

## 1. Abstract

Visual attention allows observers to change the influence of different parts of a visual scene on their behavior, suggesting that information can be flexibly shared between visual cortex and neurons involved in decision making. The authors investigated the neural substrate of flexible information routing by analyzing the activity of populations of visual neurons in the medial temporal area (MT) and oculo-motor neurons in the superior colliculus (SC) while rhesus monkeys switched spatial attention.

They demonstrated that attention increases the efficacy of visuomotor communication: trial-to-trial variability in SC population activity could be better predicted by the activity of the MT population (and vice versa) when attention was directed toward their joint receptive fields. Surprisingly, this improvement in prediction was not explained by changes in the dimensionality of the shared subspace or in the magnitude of local or shared pairwise noise correlations. These results lay a foundation for future theoretical and experimental studies into how visual attention can flexibly change information flow between sensory and decision neurons.

(Per PubMed PMID 34699782; *Current Biology* 31(23):5299–5313.e4; DOI 10.1016/j.cub.2021.09.076.)

## 2. Why this matters for us

This paper is the empirical fulcrum on which the user's "multi-hub system with a central self-attention substrate" reading of cortical attention turns. It establishes that attention does *not* sculpt connectivity by rotating a low-dimensional communication subspace between visual and decision populations; instead, the same subspace is used more *efficiently* — more variance in the downstream area is predicted by the upstream area when attention is engaged.

Read against the user's program, this is exactly the behavior expected of a Feedback Transformer whose Q/K/V projections are gain-modulated by a top-down attentional state: the linear-readout geometry of who-talks-to-whom is preserved, but the strength of cross-population information transfer is up-regulated. The Recurrent ViT's multiplicative-feedback variant (`2502.10955` §6.7) is the architectural translation of precisely this measurement, and the result tells us that the *multiplicative* variant — not the additive or token variant — is the biologically motivated one.

## 3. Key claims

1. In simultaneously recorded MT and SC populations of macaques performing a cued spatial-attention change-detection task, the cross-population linear prediction (regression of one area's trial-to-trial variability from the other's) is *more accurate when attention is directed toward the joint MT/SC receptive field*, in both directions (MT → SC and SC → MT).
2. The dimensionality of the communication subspace — the rank at which cross-area reduced-rank regression saturates — is unchanged by attention, typically a small handful of dimensions in each direction.
3. The principal axes of the communication subspace (the directions in MT that best predict SC variability, and vice versa) are *not* rotated by attention; the same subspace carries traffic in both attention states.
4. The local noise-correlation reduction reported in Cohen & Maunsell 2009 and Mitchell et al. 2009, and the cross-area noise-correlation reduction reported in Ruff & Cohen 2016, are reproduced here but are *not* sufficient on their own to explain the improvement in cross-area predictability.
5. Therefore, attention is best described as a multiplicative scaling of the efficacy of a *fixed* cross-area communication channel — not as a re-routing of that channel.
6. The bidirectionality of the effect — both feedforward (MT → SC) and "feedback-like" (SC → MT) predictions improve symmetrically — is incompatible with a purely feedforward gain-modulation account in which attention acts only at the sensory stage. Whatever modulates the channel acts on both endpoints, consistent with a third (top-down) source projecting to both populations.
7. The improvement in cross-area predictability is correlated, across recording sessions, with behavioral attention benefits (faster detection, higher hit rate at the cued location), establishing that the neural signature is behaviorally relevant rather than epiphenomenal.

## 4. Methods

Two adult rhesus macaques performed a spatial change-detection task with valid cue blocks (~80%) directing covert attention to one of two Gabor patches in opposite hemifields. On each trial, after a variable foreperiod, one stimulus changed orientation; the monkey indicated detection by an eye movement. Simultaneous multi-electrode recordings used Utah arrays in area MT and linear arrays in the intermediate/deep layers of the superior colliculus (SC), with receptive fields overlapping at one of the two cued locations. Trials were sorted by attention condition (attend-into-RF vs. attend-away-from-RF), and for each condition a trial-by-neuron spike-count matrix was built over a stimulus-aligned window.

The core analysis is *reduced-rank regression* of the population activity in one area on the other, evaluated by held-out cross-validated R². For a target area $Y$ and source area $X$, the model fits $Y \approx X B_r$ with $B_r$ of rank $r$, sweeping $r$ from 1 to $\min(n_X, n_Y)$ and identifying the dimensionality at which performance saturates. Comparisons between attention conditions are made (i) at the population R² peak, (ii) at the saturation rank, and (iii) on the principal-angle similarity of the fitted $B_r$ subspaces. Auxiliary analyses include factor analysis to separate shared from private variance, and pairwise noise-correlation comparisons within and between areas.

Controls confirm that the effect is not driven by firing-rate gain changes (results hold after rate-matching), by trial-count imbalances, by attention-related changes in stimulus drive, or by single-neuron variance differences. The communication-subspace identification follows Semedo, Zandvakili, Machens, Yu & Kohn 2019: cross-area shared variance is bounded above by the dominant-mode variance of the source area, and the saturation rank of the regression is the operational definition of "subspace dimensionality."

Two methodological subtleties are worth flagging for the model-side reader. First, the regression is implemented on residuals after subtracting the trial-averaged stimulus response, so the "communication" being measured is *shared trial-to-trial variability* — i.e., shared noise — not shared stimulus-driven signal. This is the right quantity for studying information *flow* (as opposed to information *content*), because shared signal would be present even with no functional connectivity. Second, all analyses are repeated with stimulus-matched subsamples to rule out attention-related changes in the visual drive itself as the source of the effect.

## 5. Results

The headline quantitative finding is a robust attention-driven increase in cross-area predictive R² with the same fitted rank in both attention conditions. The saturation rank of the MT → SC subspace is typically 3–5 (and similarly for SC → MT), and is essentially unchanged between attend-in and attend-out conditions; the *peak* predictive R² rises by a meaningful fraction (≈20–40% relative gain in cross-validated predictability across the reported sessions) when attention is directed into the joint receptive field. Principal-angle analysis confirms that the attend-in and attend-out subspaces lie within a few degrees of each other on average, well below the angles that would constitute a meaningful rotation. Local noise correlations decrease with attention as expected, and cross-area noise correlations also decrease; regressions that control for these effects still leave a substantial attention-related improvement in cross-area predictability, indicating that the pairwise-correlation story is incomplete.

Behaviorally, the same sessions show the canonical attention benefit: faster reaction times and higher hit rates at the cued location, with attention-modulation indices that covary across sessions with the magnitude of the cross-area predictability improvement. The symmetry between MT → SC and SC → MT predictability is striking: both directions improve, by similar amounts, with a similar invariance of rank and principal angles. This bidirectional symmetry is the result that most resists a purely feedforward gain-modulation reading and most strongly motivates the multiplicative-on-fixed-channel interpretation.

Quantitatively the attention-driven decorrelation contributes only a fraction (the authors estimate roughly one-third) of the predictability improvement; the remaining two-thirds is attributable to a "shared-variance amplification" that cannot be reduced to pairwise noise statistics. This is the key dissociation between the 2009/2016 noise-correlation findings and the 2021 communication-channel finding.

## 6. Critique / limitations

The paper is methodologically careful but bounded in four ways the user's program should note.

(i) The analysis is *linear*. Communication is identified with the linear-Gaussian shared variance between population vectors; nonlinear or higher-moment information flow — e.g., mixed selectivity, gating-by-multiplication, conjunctive coding — could be re-routed under attention without showing up as a subspace rotation. A multiplicative readout that uses one population to gate another would manifest in this analysis as a "fixed subspace with increased efficacy" even if the underlying mechanism is in fact a re-routing in the nonlinear sense.

(ii) The communication-subspace framework inherits the Semedo 2019 assumption that the shared signal is a stationary linear projection during the analysis window. Attention-driven dynamics on faster-than-trial timescales — oscillatory phase-locking, transient routing, sub-trial bursts — would be averaged out. The closely related "communication-through-coherence" hypothesis (Fries 2005, 2015) is in fact a *dynamical* routing mechanism that this analysis is by construction blind to.

(iii) The MT–SC pairing is one of many cross-area dyads. Whether the same conservation-of-subspace-with-gain-of-efficacy holds for V4 → PFC, LIP → FEF, or pulvinar-gated cortico-cortical traffic is not established here. Subsequent work from the Kohn, Cohen, and Smith labs has extended the communication-subspace logic to V1/V2/V4 dyads with broadly compatible results, but task-relevant cortico-prefrontal channels and transthalamic channels remain open.

(iv) Causal direction is correlational. The paper shows that MT and SC carry shared trial-to-trial variance and that this shared variance is amplified by attention. It does not show that MT causes the SC variance (or vice versa); a third structure (the pulvinar, frontal eye fields, or parietal cortex) could in principle be supplying the shared variance to both, with the attentional gain applied at that third structure. Microstimulation or optogenetic experiments would be needed to break the symmetry.

## 7. Connection to our work

Three explicit hooks back into the user's architectural program (`threads/the_user_architectural_program.md`).

**The "central self-attention substrate" of the multi-hub system is a communication-subspace analog.** In §5 of the program thread the user proposes hubs (MSI, RL, VAE) that all feed back into a central self-attention map, with each hub's contribution implemented as a multiplicative term $c^{(\text{hub})}_q$ on the sensory Q/K projection. Srinath et al.'s finding that attention preserves the *axes* along which two cortical populations communicate but rescales the *strength* of that communication is exactly the empirical signature this architecture predicts: a fixed Q/K projection, a multiplicative gain term injected by a top-down hub, and consequently the same shared subspace running at a higher SNR under attention. This is a direct point of empirical support for the user's commitment to multiplicative (rather than additive or rotational) feedback in the Feedback Transformer (§1 of the program thread).

The user's competition-emergent predictive-coding thesis (§5 of the program thread) gets a separate boost from this paper. The thesis predicts that hubs compete for control of the attention map via multiplicative contributions to Q and K — a mechanism that *would* preserve the geometric subspace while shifting its gain, exactly the Srinath signature. An alternative thesis in which hubs steer the attention map by re-routing connectivity would predict subspace rotation, which Srinath et al. fail to observe. The paper therefore disfavors the "rerouting" reading of attention and supports the "competitive gain on a fixed substrate" reading the user has committed to.

**The Feedback Transformer's information-routing role.** The Recurrent ViT paper (2502.10955) describes three feedback variants — tokens, additive, multiplicative — and reports on a single-layer instance. Srinath et al. argue against the most general "subspace rotation" mechanism and in favor of a gain-on-fixed-channel mechanism. This is a directly testable prediction at the model level: in a Recurrent ViT trained with multiplicative feedback, the principal directions of cross-layer Q/K alignment should be stable across attentional conditions (e.g., across change-detection vs. non-change trials), while the magnitude of the inner product (and thus the softmaxed attention weight) should grow. PRISM v2's hierarchical FiLM (`PRISM_V2_PROPOSAL.md` §3.4) is a strictly weaker version of this mechanism, applying FiLM to the *features* rather than to the Q/K projections; one prediction is that hierarchical FiLM will partly but not fully reproduce the Srinath signature.

Concretely, the model-side measurement to report alongside change-detection accuracy is: fit reduced-rank regression from the patch-token activations of layer $\ell$ to those of layer $\ell+1$, separately for trials where the model attended to the changed region versus trials where it did not. The Srinath prediction, applied to a successful Recurrent ViT, is (a) saturation rank invariant across the two trial sets; (b) principal-angle similarity high; (c) peak R² higher on the attended trials. If the model satisfies all three, it shares the cortical mechanism; if it satisfies only (c), it is using a subspace-rotation strategy that diverges from cortex; if it satisfies (a) and (b) but not (c), it has the architectural skeleton but no attentional modulation. This three-way diagnostic is, to our knowledge, not yet reported for any change-detection model.

**Continuity with the Cohen-lab program.** This paper extends Cohen & Maunsell 2009 (`cohen_maunsell2009_correlations`) and Ruff & Cohen 2016 (`ruff_cohen2016_cross_area_correlations`). The 2009 result is "attention decorrelates within-area noise"; the 2016 result is "attention decorrelates cross-area noise"; the 2021 result is "even after accounting for both, attention still improves cross-area predictability, and it does so by amplifying a fixed channel." The user's program reads this trilogy as evidence that local decorrelation is a *side effect* of selective gain on a fixed feedback geometry, not the mechanism of attention itself — consistent with Reynolds & Heeger 2009 normalization and Desimone & Duncan 1995 biased competition, both already in the seed.

The architectural moral, taken across the three papers, is that the Feedback Transformer's job is *not* to dynamically rewire the network; it is to amplify selected channels of a network whose wiring is fixed by the feedforward Q/K geometry. This sharpens a previously underspecified design choice in the user's program: the per-state Q/K/V projections $W_Q^{(k)}, W_K^{(k)}, W_V^{(k)}$ for feedback source $k$ should be *learned once and frozen during inference*, with attentional modulation entering only through the magnitudes of the projected vectors $Q_{C_k}, K_{C_k}$. Attention is a multiplicative gain, not a learned rerouting. This is implementable, biologically motivated, and now empirically anchored.

A fourth, weaker connection: the conservation of subspace under attention dovetails with Mante et al. 2013's context-dependent PFC computation, in which the same population implements different input–output mappings under different task contexts by re-weighting along fixed axes rather than re-routing. The Srinath result is the visuomotor-pathway analog of Mante's PFC result, and one can read the multi-hub system's central self-attention substrate as the architectural inheritor of both: fixed Q/K axes (the "communication subspace"), context- or attention-dependent multiplicative reweighting (the "hub contributions"), and an emergent input–output mapping that depends on which hub is currently dominating the gain term.

A fifth connection, to the recurrent-dynamics literature. Kietzmann et al. 2019 (`kietzmann2019_recurrence_required`) shows that recurrence is required to fit primate IT under challenging conditions; Panichello & Buschman 2021 (`panichello_buschman2021_shared_mechanisms`) shows that selection-from-perception and selection-from-memory share a common neural mechanism. The Srinath result fits into this picture as the *cross-area* signature of a recurrent attentional state: a top-down recurrent variable, supplied by frontoparietal or pulvinar sources, multiplicatively gain-modulates the communication channel between MT and SC. In a Recurrent ViT with a Feedback Transformer at each layer, this same top-down variable corresponds to the recurrent feedback state $H^{(t-1)}$ projected into per-state Q/K factors; the prediction is that ablating $H^{(t-1)}$ in trained change-detection models should selectively impair the *cross-layer* communication-subspace efficacy while preserving its dimensionality and principal axes — a direct, quantitatively-defined model analogue of the Srinath measurement that could be reported alongside change-detection accuracy in future Recurrent ViT and PRISM v2 evaluations.

An additional implication for the design of attention-related ablations in our models: it is not enough to report that attention "improves performance" or "reduces correlations." The discriminating measurement, suggested by Srinath et al., is the *cross-layer reduced-rank regression* — comparing R², saturation rank, and principal-angle similarity across attentional or task conditions. Reporting these three numbers in a Recurrent ViT or PRISM v2 paper would supply a direct, quantitative bridge between the model and the primate literature and would let the model's mechanism (subspace rotation vs. subspace amplification) be diagnosed in the same vocabulary the neuroscience uses.

Finally, the bidirectional symmetry (claim 6 above) is the experimental anchor for the user's commitment to *parallel* feedback in the GridCell RNN (§2 of the program thread).

A feedforward-only model in which only MT projects to SC cannot produce a symmetric SC → MT predictability improvement. The simplest model that does is one in which a third source (top-down attentional signal) projects to both, scaling shared variance up at both ends — precisely the role the user assigns to top-down recurrent state $H^{(t-1)}$ feeding into every layer's Feedback Transformer.

## 8. Citations to follow

- `semedo2019_communication_subspace` — Semedo, Zandvakili, Machens, Yu & Kohn 2019 (*Neuron*): the methodological foundation. Reduced-rank regression as a definition of cross-area communication. Should be a full-depth entry; it is load-bearing for any future "communication subspace in a Recurrent ViT" model analysis.
- `mitchell2009_attention_noise_v4` — Mitchell, Sundberg & Reynolds 2009: the V4 companion to Cohen & Maunsell 2009 on noise-correlation reduction. Important for the within-area decorrelation literature.
- `kohn2016_correlations_review` — Kohn, Coen-Cagli, Kanitscheider & Pouget 2016 (*Annual Review of Neuroscience*): the most cited review on the functional meaning of cross-area correlations. Useful framing for §6.
- `semedo2022_feedforward_feedback_subspaces` — Semedo et al. 2022 (*Nature Communications*) on V1 → V2 communication subspaces: the natural follow-up generalizing the MT → SC result to a cortico-cortical dyad.
- `ruff_cohen2019_simultaneous_recording_attention` — Ruff & Cohen 2019 simultaneous V4–PFC recordings during attention. Connects the cross-area-correlation lineage to the prefrontal side of the loop.
- `huang2019_circuit_models_attention` — Huang, Pouget, Bensmaia & Doiron 2019 circuit-level account of attention-related decorrelation. The mechanistic counterpart on the modeling side.
- `cohen_kohn2011_measuring_correlations` — Cohen & Kohn 2011 *Nature Neuroscience* methodological review of measuring/interpreting noise correlations. Useful background to make the §6 critique precise.
- `fries2015_rhythms_for_cognition` — Fries 2015 *Neuron* update on communication-through-coherence. The dynamical-routing alternative to the stationary-subspace framework; directly addresses limitation (ii) in §6.
- `bondy2018_feedback_determines_correlations` — Bondy, Haefner & Cumming 2018: cross-area feedback as a source of pairwise noise correlations. The microcircuit-level counterpart of Srinath et al.'s population-level claim.
