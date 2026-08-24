---
id: emrich2017_attention_wm_resources
title: "Attention Mediates the Flexible Allocation of Visual Working Memory Resources"
authors:
  - "Emrich, Stephen M."
  - "Lockhart, Holly A."
  - "Al-Aidroos, Naseem"
year: 2017
venue: "JEP: HPP"
doi: "10.1037/xhp0000398"
arxiv: ""
url: "https://psycnet.apa.org/doi/10.1037/xhp0000398"
tags:
  - working-memory
  - visual-attention
  - psychophysics
concepts:
  - precision-weighting
  - attentional-spotlight
  - cueing-effect
  - feature-binding
related:
  - bays2024_wm_representation
  - awh2006_attention_wm
  - panichello_buschman2021_shared_mechanisms
  - kiyonaga_egner2013_wm_internal_attention
  - olivers2011_wm_states_attention
  - schneegans_bays2017_feature_binding_wm
  - luck_vogel1997_wm_capacity
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_36
status: full
depth: full
last_updated: "2026-05-16"
---

# Attention Mediates the Flexible Allocation of Visual Working Memory Resources

## 1. Abstract

Visual working memory (VWM) has clear capacity limitations, but the mechanisms that *impose* those limitations have remained elusive. Most extant models characterize VWM performance in terms of the *number of items* to be remembered — either a fixed set of discrete slots or a fixed resource divided across a bounded set.

Across two continuous-report experiments using spatial pre-cues of varying validity, the authors examine whether changes in *spatial attention* — operationalized as the prioritization of memory items via cue probability — better account for VWM performance than changes in memory load. They find that performance is better predicted by the prioritization of memory items (i.e., attention) than by the number of items to be remembered (i.e., memory load), and that this attention–precision relationship follows a *power law*.

The power-law relationship holds regardless of whether performance is assessed in terms of overall response precision or any of the three components of the standard mixture model (precision, guess rate, swap rate). Crucially, at large set sizes, even minimally attended items continue to receive a small but nonzero proportion of resources — with no evidence for a discrete upper bound on the number of items that can be maintained in VWM.

## 2. Why this matters for us

Emrich, Lockhart & Al-Aidroos 2017 is the empirical workhorse for the claim that **attention is the resource-allocation mechanism of VWM**. The paper directly motivates an architectural commitment that the Recurrent ViT and PRISM share: the softmax attention map over memory tokens *is* the resource-allocation policy.

The same continuous, graded, power-law allocation that Emrich et al. document in human observers is what an attention-over-memory mechanism is structurally suited to produce. The paper also provides the strongest behavioral counter-evidence to discrete-slot accounts (Luck & Vogel 1997) — completing, with Bays 2024 and Panichello & Buschman 2021, the modern triangulation that VWM is a continuous, attention-modulated resource.

## 3. Key claims

1. **Attention, not load, is the proximal determinant of VWM precision.** When cue validity (attentional prioritization) and set size are jointly manipulated, precision is better predicted by how much attention an item received than by the total number of items in the display.
2. **The attention–precision relationship follows a power law.** Precision scales as a power function of the proportion of attention allocated to an item, across the range of cue validities tested.
3. **The power-law form holds for every mixture-model component.** It governs precision, guess rate, *and* swap (mis-binding) rate — not just the central precision term.
4. **No evidence for a discrete item-number cap.** Even at large set sizes, minimally attended items receive a small but nonzero share of resources. There is no set-size at which items are simply "dropped."
5. **Variable-precision is the natural functional form.** Behavioral error is well-described by a variable-precision model in which each item's precision is set by the proportion of an allocable resource it receives — and that proportion is set by attention.
6. **Cue validity acts as a graded attentional prior.** Higher cue validity at a location yields a larger resource share for the item at that location; lower validity yields a smaller share. The cue's information value translates monotonically into precision.
7. **Spatial attention and VWM share a common resource currency.** The same manipulation that biases pre-stimulus spatial attention also biases the post-stimulus precision of the maintained VWM representation — consistent with the Awh-Jonides 2006 / Kiyonaga-Egner 2013 line that external and internal attention draw on shared mechanisms.

## 4. Methods

Two continuous-report VWM experiments with pre-cues of varying probabilistic validity.

**Stimuli and task.** On each trial, observers saw a brief memory array of colored items presented at multiple spatial locations, followed by a blank delay, followed by a single probe location for which the observer reported the remembered color on a continuous color wheel. Set size was manipulated within or across blocks. Crucially, *prior to* the memory array, a *probabilistic spatial cue* indicated one of the locations with a known validity (e.g., 50%, 70%, 90%) — telling the observer that the to-be-probed item was *more likely* to come from the cued location, but not certainly. The cue therefore induces a graded attentional weighting across items: cued items receive more attention, uncued items receive less. By crossing cue validity with set size, the design dissociates *number of items* from *attentional share per item*.

**Independent variables.**
- *Set size* (memory load): the number of items in the display.
- *Cue validity*: the probability that the cued item would be the probed item, varied across conditions to produce a range of attentional weightings.
- *Attention proportion per item*: derived from cue validity and the number of items, this is the per-item share of attention/resources, ranging from near-zero (an uncued item in a high-validity, large-set-size display) to near-one (a single, fully cued item).

**Dependent measure and model.** Color report error (in degrees on the color wheel) was decomposed using the standard *three-component mixture model* (Bays-Husain-Schneegans / Zhang-Luck form): a von Mises target distribution (with concentration parameter $\kappa$ giving precision), a uniform guess component (rate $\gamma$), and a swap component reflecting reports centered on a non-target item (rate $\beta$). Precision was also computed nonparametrically as the circular standard deviation of the error distribution, to guard against model-form dependence of the precision estimates.

**Analysis.** The authors fit precision (and each mixture component) as a function of (a) set size — the load-only prediction — and (b) the *proportion of attention/resources* allocated to the probed item — the attention prediction. Model comparison via $R^2$ / AIC determined which predictor accounted for more variance. They additionally fit a *power-law* function $\kappa \propto p^{\alpha}$, where $p$ is the proportion of attention allocated and $\alpha$ is the recovered power exponent. The power-law fit was compared against linear and exponential alternatives to confirm the functional form.

## 5. Results

The principal quantitative findings:

- **Attention prediction dominates load prediction.** Across both experiments, the proportion of attention allocated to an item accounts for substantially more variance in precision than set size does. When attention proportion is held constant, varying set size produces little additional change in precision; when set size is held constant, varying cue validity produces large changes in precision. The same conclusion holds whether precision is operationalized as the von Mises concentration $\kappa$ or as the nonparametric circular standard deviation.
- **Power-law fits are excellent.** Precision as a function of attention proportion is well fit by $\kappa = c \cdot p^{\alpha}$ with $\alpha$ in a range consistent with *diminishing-returns* allocation: the marginal precision gain from adding attention to an already-attended item is smaller than the gain from attending an unattended item. Power-law fits dominate linear and exponential alternatives by AIC.
- **All three mixture components scale.** Guess rate $\gamma$ *decreases* with attention proportion (more attention → fewer pure guesses); swap rate $\beta$ also decreases (more attention → fewer mis-bindings); precision $\kappa$ increases. All three follow the same power-law functional form against the attention-proportion axis, with distinct exponents per component.
- **Continuous tails at large set sizes.** Even when set size is large and cue validity at a location is low (yielding attention proportions of just a few percent), the precision for the un-cued item is *above chance* — items continue to receive a small share of resources rather than being categorically dropped. This is the central piece of evidence against discrete-slot accounts: there is no set-size at which the data show a step-function drop to chance for un-prioritized items.
- **The relationship is captured by variable-precision modeling.** A variable-precision model that allocates a finite resource across items in proportion to the attention weights captures the data, including the heavy tails of the error distribution at low attention proportions. Fixed-precision and slot+averaging models fit worse.
- **Set-size effects fall out of the attention account.** What looks like a classical set-size effect (precision drops as set size rises) is, in this framework, *derived*: at larger set sizes the per-item attention share is smaller, and the power-law mapping from attention to precision then produces the observed precision drop. Set size is the *consequence*, not the cause.

## 6. Critique / limitations

The paper rests on the assumption that pre-cue validity manipulates *attentional prioritization* and not other variables (e.g., perceptual encoding strength, decision criteria, motivational allocation). While the authors argue convincingly that cue validity acts at the resource-allocation level, the design cannot fully dissociate attentional allocation during *encoding* from later, *retrieval-stage* prioritization, nor can it separate attention-during-perception from attention-during-maintenance. The Panichello & Buschman 2021 framework, which uses delay-period cues and direct neural recordings, addresses this distinction more directly.

The mixture-model decomposition assumes a particular generative form (von Mises target + uniform guess + swap to non-targets). Alternative non-target distributions (e.g., distance-weighted swaps; continuous binding-error models à la Schneegans & Bays 2017) could redistribute variance across the three components. Bays and colleagues have argued in other work that the apparent guess component is partly an *artifact* of low-precision items being misclassified as guesses by the mixture-model fitter — which would, if true, push more of the data toward a fully-continuous, no-guess account.

The "no discrete cap" claim is grounded in the *absence* of a discrete cutoff in the precision-vs-attention relationship. Defenders of slot models can re-fit the data with stochastic-slot variants that produce continuous-looking allocation through item-by-item slot probability — the experiment does not categorically falsify those refits, though it does shift the burden of proof onto them.

The experiments do not directly measure neural correlates of attention or precision. The interpretation that attention *is* the resource-allocation mechanism rests on behavior alone. The Panichello & Buschman 2021 neural recordings in primate PFC and parietal cortex provide the most direct neural test of the underlying shared-substrate claim, and broadly corroborate it.

The cue validity manipulation produces voluntary, top-down attentional weighting. Whether the same allocation rule governs stimulus-driven, bottom-up attentional biasing (e.g., from salience, reward, or selection history) is left as a prediction. Failing-Theeuwes-style selection-history paradigms are the natural follow-up.

## 7. Connection to our work

This paper is one of the *load-bearing* behavioral references for the user's program. It is the cleanest behavioral demonstration that attention is the mechanism by which a continuous, finite VWM resource is distributed across items. Every architectural commitment in the Recurrent ViT and PRISM that treats *attention over memory tokens* as the resource-allocation policy traces back, in part, to this finding. The connection is most direct at six levels.

**(a) The attention map as resource-allocation policy in the Recurrent ViT.** The Recurrent ViT's softmax attention over patch tokens is, structurally, exactly the kind of object Emrich et al. document behaviorally: a *continuous, graded weighting across items that determines the precision with which each item is maintained.*

- The Q/K inner product produces an unnormalized score per item.
- The softmax converts those scores into a probability distribution that sums to 1.
- The value-weighted sum then allocates representational bandwidth in proportion to that distribution.

The "softmax over patches" is the architectural realization of the "proportion of attention per item" that Emrich et al. recover from their behavior.

In particular, the *power-law* form Emrich et al. report ($\kappa \propto p^{\alpha}$) is a strong behavioral constraint that any cognitive model of attention-over-memory should match. Softmax-attention with learned Q/K projections produces precisely this kind of monotone, smooth allocation — and is therefore in good agreement with the behavioral data. PRISM v1's prediction-error-driven attention (without softmax) is the architectural antagonist: it would have to recover the same power-law shape through a different mechanism, which is an experimentally testable contrast.

**(b) Continuous, attention-weighted memory as the contemporary framing.** Emrich et al. join Bays et al. 2024 in arguing that VWM is *continuous and attention-modulated*, not discrete and slot-bounded. This is the framing under which:

- The Recurrent ViT's continuous hidden state $H^{(t)}$ is *biologically appropriate*, not an approximation.
- PRISM's continuous memory $M_t$ is biologically appropriate.
- The graded softmax over patches (rather than a hard top-$k$ selection) is the biologically appropriate attention mechanism.

The recurrent ViT paper (2502.10955) cites Emrich et al. as ref [36] precisely because the continuous-resource framing licenses the continuous-state architecture.

**(c) Attention and WM as a shared mechanism, supporting bidirectional feedback in the user's program.** Emrich et al.'s finding that *pre-stimulus spatial attention* sets *post-stimulus VWM precision* is the behavioral signature of the Awh-Jonides 2006 / Kiyonaga-Egner 2013 thesis that external and internal attention share a substrate.

In the user's architectural program (the_user_architectural_program §3 — Multi-compartmental, hierarchical, bidirectionally-connected memory), the Feedback Transformer integrates:

- bottom-up sensory projections,
- top-down descending memory projections (deeper layers),
- ascending memory projections (shallower layers),
- and lateral parallel-hub feedback,

at the *same* attention layer. The "shared substrate" thesis is the cognitive-science justification for this architectural choice: there is no reason to maintain separate attention mechanisms for perception and for memory if behavior is consistent with a single, shared resource pool.

**(d) Graded attention → continuous attention weights.** The behavioral finding that minimally-attended items still receive a small, nonzero share — no discrete cap — maps directly onto the *softmax* in transformer attention, which always assigns nonzero probability to every token.

- A *hard top-k* attention (as in some sparse-attention variants) would predict a discrete cap on the number of items receiving any resource; the data falsify this.
- A *threshold-and-zero* attention would predict that low-priority items are reported at chance; the data show above-chance reports.
- A *full softmax* attention assigns vanishingly small but nonzero weight to low-priority tokens; the data match this profile.

This is a small but real architectural argument for using full softmax attention in the recurrent ViT rather than sparse / top-k variants — at least when matching human behavioral allocation is a desideratum.

**(e) Mixture-model decomposition as an evaluation framework.** The mixture-model decomposition (precision, guess, swap) is a natural target for evaluating the Recurrent ViT's behavior in continuous-report regimes. If the architecture is to be tested with continuous-report tasks (as opposed to binary change-detection), Emrich et al.'s analysis pipeline — fit a von Mises + uniform + swap mixture, compare to a per-item attention-proportion predictor — is the appropriate yardstick. This is a concrete experiment-design contribution that the paper offers to future work.

**(f) Power-law allocation and softmax temperature.** The recovered power-law exponent $\alpha$ corresponds, at the level of architectural design, to the *temperature* (or scaling) of the softmax attention:

- A *smaller* temperature produces a peakier distribution (closer to one-hot), corresponding to a larger $\alpha$ (sharper diminishing returns).
- A *larger* temperature produces a flatter distribution (closer to uniform), corresponding to a smaller $\alpha$.
- The standard $1/\sqrt{d_k}$ scaling in scaled-dot-product attention is one specific choice; learned per-head temperatures (as in some Transformer variants) give more flexibility.

Fitting the temperature of the Recurrent ViT's attention to recover Emrich-like power-law exponents is a concrete, falsifiable calibration target — and a way of grounding the model's hyperparameters in human behavioral data rather than in task-loss minima alone.

**(g) Indirect support for the competition-emergent PC thesis.** Although Emrich et al. work entirely at the behavioral level and do not engage the predictive-coding literature, the *power-law diminishing-returns* allocation they document is consistent with what one would expect from a system in which neural coalitions compete for a finite resource (the user's competition-emergent PC framing, the_user_architectural_program §5). When a coalition has already won most of the resource at a location, the marginal gain from winning more is small; when a location has very little allocated to it, even a small additional share produces a measurable precision gain. The concavity of the power law is the behavioral signature of a *competitive allocation under a finite budget* — exactly the kind of dynamic the user posits at the architectural level.

The paper does *not* speak directly to the user's deeper architectural commitments (the Feedback Transformer's multi-source integration, the iterative variational encoder–decoder, the full competition-emergent predictive coding thesis). It belongs to the cognitive-science *task* side of the program, anchoring the behavioral phenomenon the architecture must reproduce. In the reading-order taxonomy of the_user_architectural_program §7, it is a paper that "anchors the *task* side of the program" — and along with Bays 2024, Awh 2006, and Panichello & Buschman 2021 it forms the four-paper backbone of the WM/attention behavioral case for the architecture.

## 8. Citations to follow

Papers cited by Emrich et al. 2017 that warrant database entries.

- `bays_husain2008_dynamic_shifts_visual_wm` — the original continuous-resource paper from the Bays lab; Emrich et al.'s variable-precision modeling derives from this lineage. Not yet in seed.
- `zhang_luck2008_discrete_fixed_resolution` — the discrete-slot / fixed-resolution counter-position; necessary for a balanced read. Not yet in seed.
- `van_den_berg2012_variable_precision` — the variable-precision model Emrich et al. fit. Not yet in seed.
- `klyszejko_rahmati_curtis2014_attentional_priority_wm` — a parallel demonstration that attentional priority determines VWM precision, from a different lab. Not yet in seed.
- `gorgoraptis2011_dynamic_updating_vwm` — Bays-lab follow-up on dynamic resource reallocation during the delay. Not yet in seed.
- `pratte_park_rademaker_tong2017_set_size_vwm` — model-comparison paper that re-examines the discrete-vs-continuous debate. Not yet in seed.
- `myers_stokes_nobre2017_prioritizing_information` — review of prioritization of information in WM; aligned with the Emrich framing. Not yet in seed.
- `luck_vogel1997_wm_capacity` — the canonical discrete-slot reference; in seed.
- `bays_catalao_husain2009_swap_errors` — establishes the swap component of the mixture model. Not yet in seed.
- `ma_husain_bays2014_changing_concepts_wm` — review consolidating the continuous-resource view. Not yet in seed.
