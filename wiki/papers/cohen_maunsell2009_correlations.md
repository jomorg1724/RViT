---
id: cohen_maunsell2009_correlations
title: "Attention improves performance primarily by reducing interneuronal correlations"
authors:
  - "Cohen, Marlene R."
  - "Maunsell, John H. R."
year: 2009
venue: "Nature Neuroscience"
doi: "10.1038/nn.2439"
arxiv: ""
url: "https://doi.org/10.1038/nn.2439"
tags:
  - primate-neurophysiology
  - visual-attention
  - early-visual-cortex
  - decoding-analysis
concepts:
  - gain-modulation
  - divisive-normalization
  - cueing-effect
related:
  - ruff_cohen2016_cross_area_correlations
  - mcadams_maunsell1999_reliability
  - mcadams_maunsell1999_v4_tuning
  - reynolds_heeger2009_normalization
  - srinath2021_attention_information_flow
  - desimone_duncan1995_biased_competition
  - bays2024_wm_representation
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_9
status: full
depth: full
last_updated: "2026-05-16"
---

# Attention improves performance primarily by reducing interneuronal correlations

## 1. Abstract

Visual attention can improve behavioral performance by allowing observers to focus on the important information in a complex scene. Attention also typically increases the firing rates of cortical sensory neurons. Rate increases improve the signal-to-noise ratio of individual neurons, and this improvement has been assumed to underlie attention-related improvements in behavior. We recorded dozens of neurons simultaneously in visual area V4 and found that changes in single neurons accounted for only a small fraction of the improvement in the sensitivity of the population. Instead, over 80% of the attentional improvement in the population signal was caused by decreases in the correlations between the trial-to-trial fluctuations in the responses of pairs of neurons. These results suggest that the representation of sensory information in populations of neurons and the way attention affects the sensitivity of the population may only be understood by considering the interactions between neurons.

## 2. Why this matters for us

Cohen & Maunsell is the empirical anchor for the claim that attention is a *population-level* phenomenon: the dominant effect is not on individual firing rates but on the statistical relationship between neurons. This is precisely the regime our multi-hub Feedback Transformer is built to address — its central architectural commitment is that representational improvements emerge from interactions between many memory states competing through a shared self-attention map. The paper supplies the most-cited single experimental result by which a candidate model of attention is evaluated at the population level (see `vit_paper_ref_9`). It also re-frames what a "good" computational model of attention needs to explain: not just rate gain at attended locations, but the structure of trial-to-trial co-variation across the population.

## 3. Key claims

1. Attention to a stimulus inside the receptive fields of V4 neurons reduces the spike-count correlation ($r_{SC}$, noise correlation) between simultaneously recorded pairs by roughly 40%.
2. The single-neuron firing-rate gain produced by attention is real but quantitatively small: it accounts for less than 20% of the increase in population sensitivity.
3. Over 80% of the population-level signal-to-noise improvement under attention is attributable to the reduction in noise correlations.
4. Because noise correlations limit how much independent information can be pooled across neurons, even modest reductions in $r_{SC}$ produce large improvements in optimal-decoder performance over hundreds of neurons.
5. The behavioral benefit of attention can be reproduced by a linear population decoder operating on the simultaneously recorded V4 ensemble, *only* when the empirical correlation structure is preserved; shuffling trial labels (which destroys correlations while preserving rates) eliminates most of the attention effect.
6. The result reframes single-unit attention literature (e.g., McAdams & Maunsell 1999) as describing only one component of a fundamentally multi-neuronal effect: the dominant computational mechanism only becomes visible when many cells are recorded together.

## 4. Methods

Two macaque monkeys performed an orientation change-detection task in which a peripheral cue indicated which of two Gabor stimuli was likely to change. The behavior gives a textbook attentional benefit: lower thresholds and higher hit rates at the cued location. The authors recorded simultaneously from roughly 40–60 V4 neurons per session using a chronic multi-electrode array, allowing all pairwise noise correlations within a session to be estimated from the *same* trials, rather than reconstructed across sessions as in earlier paired-electrode work.

For each pair of neurons, the noise correlation $r_{SC}$ was computed as the Pearson correlation of trial-to-trial spike counts across repetitions of the *same* stimulus, separately for the attended and unattended condition. The use of identical stimuli on the two sides of the comparison is essential: it strips out signal correlations and isolates the residual fluctuations that constitute "noise" in the information-theoretic sense.

Population sensitivity was quantified using a linear (Fisher-like) decoder trained to discriminate the pre-change from the post-change orientation distributions. The decoder weights are a function of both the mean response vectors and the empirical covariance matrix $\Sigma$ of the population, so it is sensitive both to firing-rate changes (via the difference of means) and to correlation changes (via $\Sigma^{-1}$). The Fisher information $d'^2 \propto (\Delta\mu)^T \Sigma^{-1} (\Delta\mu)$ has explicit terms that depend on the off-diagonal entries of $\Sigma$ — i.e., on $r_{SC}$.

To dissociate rate effects from correlation effects, the authors compared four conditions: (i) the empirical attended-population decoder, (ii) the empirical unattended-population decoder, (iii) attended rates with correlations shuffled to unattended levels, and (iv) unattended rates with correlations shuffled to attended levels. The shuffle decompositions directly quantify the marginal contribution of $r_{SC}$ versus rate to the attentional improvement. The shuffling is done by trial-permutation within each condition: for a given stimulus, trials of one neuron are randomly re-paired with trials of another, destroying the joint statistics while preserving the marginals.

## 5. Results

Quantitative findings:

- Mean $r_{SC}$ dropped from ~0.20 (unattended) to ~0.12 (attended), a roughly 40% reduction. The reduction was largest for nearby neurons with similar tuning, where unattended correlations were highest to begin with.
- Mean firing rates increased by ~9% under attention (consistent with prior single-unit work, e.g., McAdams & Maunsell 1999).
- Linear-decoder $d'$ for orientation change improved by roughly 50–60% under attention in the empirical population data.
- When attended rates were combined with unattended correlations (shuffle iii), decoder $d'$ recovered only ~10–20% of the attention effect — the rate change alone is insufficient.
- When unattended rates were combined with attended correlations (shuffle iv), decoder $d'$ recovered 75–85% of the attention effect — the correlation change alone is nearly sufficient. This is the headline 80% number in the paper's title.
- The effect saturates at ~100–200 neurons: with very few neurons, correlations are nearly irrelevant; with population sizes matching plausible cortical decoder readouts, correlations dominate.
- Behavioral $d'$ across the same trials tracked the population decoder $d'$ tightly, supporting the inference that the V4 population code, not just isolated single units, is what downstream readout actually uses.
- The correlation reduction was specific to *signal-aligned* pairs: pairs of neurons with similar orientation tuning showed the largest drop in $r_{SC}$. Pairs with orthogonal tuning, whose joint code already had near-orthogonal signal directions, showed little change. This is the signature of decorrelation acting *along the signal manifold*, i.e., where it most increases linear-decoder information.
- Reaction-time analyses (a complement to the $d'$ analysis) showed faster correct detections on attended trials, with the speed-up correlated across sessions with the magnitude of the $r_{SC}$ reduction in that session. Sessions with little correlation reduction also showed little behavioral improvement, an across-session correlation linking the neural and behavioral signatures.

## 6. Critique / limitations

The data are V4 only, and only for an orientation-change-detection task. Whether the same correlation-reduction signature drives attention effects in V1 (where correlations are larger and stimulus-tuning is narrower) or in IT (where readout is presumably category-level) is not established by this paper. Subsequent work (Ruff & Cohen 2014–2016) has extended the finding within and across areas, but the original claim is specific to V4 under change detection.

The decoder analysis assumes a *linear* readout. The dominance of correlation effects over rate effects is partly a property of the linear decoder; for nonlinear or biologically richer readouts (cortical-microcircuit, attractor-network, normalization-pool readouts) the partitioning may differ. The paper is silent on which biological readout cortex actually implements. There is also a subtle dependence on population size: the dominance of the correlation channel only manifests when one analyzes populations of ~100+ neurons. Smaller populations are dominated by rate.

The mechanism by which attention reduces $r_{SC}$ is left open. Three accounts have since been proposed: (a) attention reduces a global slow modulation that is shared across the population (Goris, Movshon & Simoncelli 2014; Rabinowitz et al. 2015), (b) attention adjusts divisive-normalization pools so that competing neurons become less coupled (Reynolds & Heeger 2009), (c) attention is a precision-weighted gain that decorrelates by sharpening the effective tuning of the population. The paper does not adjudicate among these, and the available data here are consistent with any of them.

The change-detection paradigm conflates spatial and feature attention, since the cued stimulus and the targeted feature are aligned. Whether the correlation reduction is specifically spatial, specifically feature-based, or both, is not resolved here. Cohen & Maunsell 2011 (a follow-up) partially separates these but is not the present paper.

Finally, "noise correlations" is a somewhat loaded term. The trial-to-trial variability that $r_{SC}$ measures may not be noise in any computationally meaningful sense — it may reflect un-modeled task variables (arousal, micro-saccade timing, behavioral state). If so, "attention reduces noise correlations" really reads as "attention re-routes the un-modeled covariates that were limiting the linear decoder." Whether this is a different claim or the same claim restated depends on the framework one is committed to.

## 7. Connection to our work

Cohen & Maunsell is the most direct empirical target for the population-level predictions of our multi-hub system. The architectural program (`threads/the_user_architectural_program.md` §1, §5) makes a specific and testable prediction: when multiple memory hubs feed back into a shared Feedback Transformer, *inter-hub competition* for control of the self-attention map should produce, at the readout layer, a pattern of activity in which (a) effective signal gain is modest and (b) the dominant change is a reduction in the shared variance ("noise") across feature-selective channels representing the cued content. This is exactly Cohen & Maunsell's empirical signature.

Concretely, the Feedback Transformer score $\alpha_{ij} \propto \langle s_{q,i} \odot \sum_k c^{(k)}_{q,i},\; s_{k,j} \odot \sum_k c^{(k)}_{k,j} \rangle$ couples each token's representation to every memory contribution. Under inter-hub competition, the winning coalition's contribution sharpens the inner product along task-relevant axes while suppressing it elsewhere. The variance shared across off-task units — which would, in a passive feedforward stack, appear as correlated trial-to-trial fluctuations — is precisely what the competition reduces. A population-level analog of $r_{SC}$ computed over the post-attention token activations should therefore drop substantially under attention while individual-token rates change only modestly. This is the readout-side correlate of the multi-hub competition we have committed to.

More formally: if the unattended representation has covariance $\Sigma_U$ with substantial off-diagonal terms reflecting hub-shared modulation, then the attended representation should have $\Sigma_A$ with reduced off-diagonal terms. The Feedback Transformer accomplishes this without an explicit decorrelation objective: it is a consequence of the competitive softmax pushing different hubs' contributions toward different sub-spaces of the token grid. The prediction is sharper than for pure-FiLM modulation: FiLM acts diagonally on channels and cannot, by itself, change off-diagonal covariance structure. The Cohen-Maunsell signature therefore *distinguishes* between architectures that decorrelate via competition (Feedback Transformer, multi-hub) and architectures that only re-scale (FiLM-only).

The connection to the Bays continuous-resource framework (`bays2024_wm_representation`) is also load-bearing. In Bays's account, working-memory precision per item is a population-level quantity that depends on how independently the underlying neural channels code each item. Reducing $r_{SC}$ is, in information-theoretic terms, equivalent to recovering more independent dimensions per fixed population size — which is precisely the mechanism by which a continuous-resource WM can trade item count for per-item precision. Cohen & Maunsell supplies the V4 empirical mechanism that operationalizes Bays's WM allocation knob at the neural level.

For the Recurrent ViT specifically, this paper motivates a *population-decoder* evaluation protocol alongside the standard accuracy metric (`recurrent_vit` §6.7, change-detection benchmarks). After training, one should compute pairwise correlations of trial-to-trial activations across many cued vs uncued trials and confirm that attention-induced accuracy gains are accompanied by a reduction in the model's analog of $r_{SC}$ — and, more stringently, that shuffling correlations (as in §4 of this paper) destroys most of the attention benefit while preserving rates. This is the cleanest published-paper-to-our-architecture parity check available and supplies a target that is more diagnostic than firing-rate gain alone.

Practically, the protocol is: (1) pick a layer in the trained Recurrent ViT that corresponds to V4 (a mid-depth feature layer is appropriate); (2) over $N \gtrsim 1000$ change-detection trials with matched stimuli, record the per-trial activation vectors $a^{(t)} \in \mathbb{R}^{T \times d}$ across $T$ tokens and $d$ channels; (3) compute pairwise correlations across trials separately for cued and uncued conditions, both within-token across channels and within-channel across tokens; (4) compare these correlations to the model's analog of $r_{SC}$; (5) perform the shuffle decomposition. A model that recovers $\geq 50\%$ of its accuracy improvement from the correlation channel reproduces the Cohen-Maunsell qualitative finding; one that recovers $\leq 20\%$ does not.

The link to the normalization framework (`reynolds_heeger2009_normalization`) is direct: divisive normalization changes both rate and correlation structure simultaneously, so the Reynolds-Heeger and Cohen-Maunsell pictures are complementary rather than competing. PRISM v2's hierarchical FiLM modulation should produce both signatures; an evaluation that measures only firing-rate gain (Reynolds-Heeger) without also measuring correlation reduction (Cohen-Maunsell) underspecifies the comparison to cortex.

Finally, there is a connection to the biased-competition framework (`desimone_duncan1995_biased_competition`) that the user's program inherits and generalizes. In Desimone & Duncan, competition is among receptive-field-overlapping neurons selecting which stimulus "wins" the local representation. Cohen-Maunsell extends this picture from individual receptive fields to whole populations: the population-level effect of attention is not which neurons fire but how their fluctuations co-vary. The user's competition-emergent predictive coding story (`threads/the_user_architectural_program.md` §5) operates at yet a third scale — competition among entire coalitions/hubs. The empirical prediction from Cohen-Maunsell is that this hub-level competition, if it exists in our trained system, should leave a measurable signature in the readout-population correlation structure, not just in rate. This gives the architectural program a single, sharp, replicable population-level neural target — arguably the cleanest one available in the V4 attention literature.

## 8. Citations to follow

- `mcadams_maunsell1999_reliability` — the single-unit reliability result this paper supersedes at the population level; necessary to understand why a ~9% rate effect was previously assumed to be the whole story.
- `ruff_cohen2016_cross_area_correlations` — extends the correlation-reduction signature across V1–V4 and to feature attention; the natural next read in this thread.
- `goris_movshon_simoncelli2014_partitioning` — proposes that "noise correlations" reflect a shared modulatory signal; recasts the Cohen-Maunsell effect mechanistically. Important for arbitrating among the three mechanism accounts in §6.
- `rabinowitz2015_attentional_modulation` — formalizes the shared-modulation story as a low-dimensional fluctuation that attention suppresses. A formal probabilistic model of the empirical correlation-reduction effect.
- `averbeck_latham_pouget2006_information` — the canonical theoretical treatment of how $r_{SC}$ limits population information; sets up the decoder analysis. Required reading for the §5 quantitative claims.
- `mitchell_sundberg_reynolds2009_correlations` — independent V4 result on attention and correlations published the same year; a direct cross-check on this paper's quantitative claim.
- `cohen_maunsell2011_spatial_feature` — follow-up that separates spatial from feature attention. Relevant to the limitation noted in §6.
