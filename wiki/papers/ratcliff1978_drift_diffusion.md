---
id: ratcliff1978_drift_diffusion
title: "A theory of memory retrieval"
authors:
  - "Ratcliff, Roger"
year: 1978
venue: "Psychological Review"
doi: "10.1037/0033-295X.85.2.59"
arxiv: ""
url: "https://psycnet.apa.org/doi/10.1037/0033-295X.85.2.59"
tags:
  - psychophysics
  - decision-making
  - reaction-time
  - theoretical-essay
concepts:
  - drift-diffusion-model
  - signal-detection-theory
  - chronometric-function
  - psychometric-function
related:
  - gold_shadlen2007_decision_making
  - sridharan2017_sc_sensitivity_bias
  - hawkins1990_attention_detectability
  - luo_maunsell2018_criterion_sensitivity
  - muller_findlay1987_sensitivity_criterion
  - hanks_summerfield2017_perceptual_decisions
  - roitman_shadlen2002_lip_rt
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-15"
---

# A theory of memory retrieval

## 1. Abstract

Ratcliff (1978) presents a theory of memory retrieval that accounts jointly for *response time* (RT) distributions and *accuracy* in two-alternative forced-choice recognition tasks. The central proposal is that retrieval is a noisy *evidence accumulation* process: each memory probe drives a continuous random walk (a Wiener diffusion process) whose *drift rate* is proportional to the resemblance between the probe and the stored memory representation, and whose *starting point* lies between two *absorbing boundaries* corresponding to the "old" and "new" responses. The first boundary crossed determines the response; the time at which it is crossed determines the RT, plus a non-decision residual that absorbs encoding and motor latencies. The model derives closed-form expressions for the joint distribution of choice and RT and shows that a small number of parameters — drift rate $v$, boundary separation $a$, starting point $z$, and non-decision time $T_{er}$ — reproduce the empirically observed signatures of recognition memory: right-skewed RT distributions, faster correct than error responses (or the reverse, under appropriate conditions), the scaling of RT with discriminability, and the speed-accuracy tradeoff. The paper thus introduces what is now called the *Ratcliff drift-diffusion model* (DDM), which has become the canonical computational account of two-alternative decision-making across perceptual, mnemonic, and value-based domains.

## 2. Why this matters for us

Ratcliff 1978 is the foundational reference for treating any two-alternative decision — whether the response of the recurrent ViT's actor head, PRISM v1's binary change/no-change output, or a primate's saccade in a motion-discrimination task — as the *output of a bounded evidence-accumulation process*. The decomposition into drift rate (sensitivity), starting-point (bias), boundary separation (speed-accuracy tradeoff), and non-decision time (motor/encoding latency) is the canonical mechanistic vocabulary used by every subsequent paper in the user's decision-framework cluster (Gold & Shadlen 2007, Roitman & Shadlen 2002, Hanks & Summerfield 2017, Sridharan et al. 2017). The choice-bias / sensitivity decomposition that Sridharan and the user's program take as central is, in its two-alternative form, a *direct re-labelling* of Ratcliff's $v$ and $z$ parameters. The recurrent ViT's response-over-time generation can be reframed as DDM-style accumulation over recurrent passes, with the actor's confidence at each step playing the role of the diffusion variable.

## 3. Key claims

1. **Memory retrieval is evidence accumulation, not threshold detection.** Recognition memory is not a single threshold comparison between a stored familiarity value and a criterion; it is a noisy *integration over time* of a momentary match signal, with response triggered by accumulator-boundary crossing.
2. **The diffusion equation models the accumulator.** The decision variable $x(t)$ follows $dx = v \, dt + \sigma \, dW$, where $v$ is the drift rate, $dW$ is a Wiener increment, and $\sigma$ is the within-trial noise (conventionally fixed for scaling).
3. **Two absorbing boundaries determine the response.** Boundaries at $0$ and $a$ correspond to the two responses; the first boundary crossed selects the response.
4. **Four core parameters suffice for the basic model:** drift rate $v$ (signal strength), boundary separation $a$ (speed-accuracy tradeoff), starting point $z$ (bias), and non-decision time $T_{er}$ (encoding + motor latency).
5. **Between-trial variability in drift and starting point captures error-RT asymmetries.** Adding Gaussian variability $\eta$ to drift across trials predicts that error RTs are *slower* than correct RTs; adding uniform variability $s_z$ to starting point predicts the opposite. Real data show both patterns under different conditions, and the model accommodates both.
6. **The full RT distribution is right-skewed and approximately ex-Gaussian in shape.** The first-passage-time distribution of the diffusion process is closed-form and reproduces the empirically universal right-skew of RT distributions without invoking an additional skewed mixing distribution.
7. **The model unifies recognition with general 2AFC.** Although introduced as a theory of memory retrieval, the mathematical structure applies to any binary decision in which a continuous signal must be classified. This is the seed of the modern unified DDM treatment.
8. **The signal-detection theory criterion is a special case.** If the boundary separation $a \to 0$ and decision-time is ignored, the model reduces to SDT: $v$ becomes the SDT signal strength and $z$ becomes the SDT criterion. DDM extends SDT into the time domain.

## 4. Methods

**Mathematical framework.** The decision variable $x(t)$ is a one-dimensional Wiener process with constant drift:

$$
x(0) = z, \qquad dx(t) = v \, dt + \sigma \, dW(t),
$$

with absorbing boundaries at $x = 0$ (response B) and $x = a$ (response A). The *first-passage time* density at boundary $a$, given start at $z$, is

$$
f_a(t \mid v, a, z) = \frac{\pi \sigma^2}{a^2} \, e^{\frac{v(a-z)}{\sigma^2} - \frac{v^2 t}{2 \sigma^2}} \sum_{k=1}^{\infty} k \, \sin\!\left(\frac{k \pi z}{a}\right) e^{-\frac{k^2 \pi^2 \sigma^2 t}{2 a^2}},
$$

with an analogous expression for the lower boundary. Observed RT is $T = T_d + T_{er}$, where $T_d$ is the first-passage time and $T_{er}$ is non-decision time (encoding + motor).

**Predicted observables.** From the first-passage-time densities, the model predicts:
- *Choice probability* as a function of $v, a, z$ (the psychometric function).
- *Mean RT and RT distribution* for each response (the chronometric function plus full distributional shape).
- *Conditional accuracy* given RT bin.
- *Speed-accuracy tradeoff* as $a$ is varied with $v$ fixed.

**Parameter fitting.** Ratcliff fits the model to joint distributions of choice and RT collected in recognition-memory experiments (item recognition, lexical decision-like tasks). Fitting uses chi-squared minimization on RT quantiles by response category — the same fitting strategy still used in modern DDM software (DMAT, HDDM, fast-DM).

**Extensions in the paper.** Beyond the four-parameter "pure" diffusion, Ratcliff introduces between-trial variability in drift ($\eta$) and starting point ($s_z$) to capture systematic patterns in real data. Later extensions (Ratcliff & Tuerlinckx 2002; Ratcliff & McKoon 2008) add between-trial variability in non-decision time ($s_t$) and various boundary collapse mechanisms.

## 5. Results

The model is shown to fit recognition-memory data quantitatively, reproducing:

- **Right-skewed RT distributions.** The first-passage density of the diffusion is naturally right-skewed; the fit to empirical RT distributions is good across many tasks.
- **Drift-rate scaling with discriminability.** Drift $v$ scales monotonically with old/new discriminability ($d'$-like quantities). High-discriminability conditions show high $v$, low error rate, fast RT.
- **Boundary-separation scaling with instructions.** Subjects told to prioritize accuracy show large $a$; subjects told to prioritize speed show small $a$. The accuracy/RT tradeoff is captured *quantitatively*, not just qualitatively.
- **Bias from probabilities and payoffs.** Starting point $z$ shifts toward the more frequent or more rewarded response, predicting the observed shifts in choice probability and RT.
- **Slow errors with drift variability $\eta > 0$.** When drift varies across trials, low-drift trials produce both slow correct and slower errors — explaining classic "slow error" findings.
- **Fast errors with starting-point variability $s_z > 0$.** When starting point varies, trials with starting point near the wrong boundary produce fast errors — explaining classic "fast error" findings.
- **Crossover.** In a single experiment, manipulations of stimulus difficulty produce slow errors while manipulations of bias produce fast errors — the model captures both within one framework.

The fits in Ratcliff 1978 were the first demonstration that a *single* mechanistic model with $\sim$6–7 parameters could account for the *entire joint distribution* of choice and RT across a battery of recognition-memory experiments.

## 6. Critique / limitations

The 1978 paper is restricted to *two-alternative* tasks. The mathematics of multi-boundary first-passage problems for higher-dimensional diffusions is much harder; Sridharan et al. 2017 ([sridharan2017_sc_sensitivity_bias](sridharan2017_sc_sensitivity_bias.md)) is one of the modern descendants addressing this for multialternative spatial-attention tasks. For tasks with three or more response locations, the 1978 DDM does not directly apply.

The model assumes a *constant drift rate* within a trial. Real evidence is often non-stationary (e.g., the random-dot motion stimulus has variable instantaneous coherence; visual scenes evolve). Modern variants (urgency-gated DDM, leaky competing accumulator, time-varying drift) address this, but the 1978 formulation does not.

The *boundaries are stationary*. Collapsing-bounds variants (Cisek et al. 2009; Hawkins, Forstmann, Wagenmakers, Ratcliff & Brown 2015) are needed to capture deadline effects and urgency.

The model is *abstract* — silent on neural implementation. The mapping to LIP/FEF accumulator neurons (Roitman & Shadlen 2002 [roitman_shadlen2002_lip_rt](roitman_shadlen2002_lip_rt.md); Gold & Shadlen 2007 [gold_shadlen2007_decision_making](gold_shadlen2007_decision_making.md)) was established post hoc. The "evidence accumulation" framing is computationally well-defined but neurally underdetermined: many circuit architectures can implement integrate-to-threshold dynamics.

The model treats the decision variable as a *single scalar*. Mante et al. 2013 and subsequent population-dynamics work show that real PFC trajectories during decisions are *high-dimensional*; the DDM scalar may be an aggressive low-dimensional projection of richer dynamics.

The non-decision time $T_{er}$ is a *catch-all* for encoding plus motor latency. It absorbs many components — sensory transduction, attention-driven gain, motor planning — that subsequent work has tried to dissociate.

## 7. Connection to our work

Ratcliff 1978 is the load-bearing reference for the user's program's treatment of *all binary decisions* — perceptual, mnemonic, or policy-driven. The connections to the user's architectural program are deep and pervasive.

**The DDM as the natural readout of recurrent state.** The recurrent ViT (2502.10955) produces an output at each recurrent pass. Reframing this as DDM-style accumulation: the actor head's logits at pass $t$ are a noisy sample from a drift process, and the response is committed when the accumulated logit crosses an implicit threshold (operationalized in practice by softmax temperature or by a learned halt head — see `adaptive-computation-time` in the taxonomy). PRISM v1's THESIS document explicitly cites Gold & Shadlen 2007 and Ratcliff (transitively) in motivating the actor's response generation as bounded accumulation.

**Sensitivity-bias decomposition as DDM $v$-vs-$z$.** The choice-bias / sensitivity dissection that the user's decision-framework cluster takes as central — Sridharan et al. 2017, Luo & Maunsell 2018, Hawkins 1990, Müller & Findlay 1987 — corresponds, in two-alternative form, to the DDM parameter pair $(v, z)$. Specifically:
- $v$ (drift rate) $\sim$ SDT $d'$ $\sim$ "sensitivity": the quality of the evidence the system extracts from the stimulus.
- $z$ (starting point) $\sim$ SDT criterion $\sim$ "bias": the prior weight on one response over another.
- $a$ (boundary separation) $\sim$ speed-accuracy tradeoff: not a classical SDT parameter; *added* by DDM, absent from pure SDT.
- $T_{er}$ (non-decision time) $\sim$ motor/encoding latency: also added by DDM.

The DDM is thus *SDT plus time*. It is the proper framework whenever response latency is informative, which it always is for the recurrent ViT's recurrent-pass-indexed outputs.

**Boundary $a$ as architectural commitment.** The user's program includes the option of variable computation depth (e.g., halt-when-confident in HRM-style architectures, `adaptive-computation-time`). The DDM boundary parameter $a$ is the cognitive-science analog of an adaptive-halt threshold: a higher $a$ means more passes before committing, more accuracy at the cost of latency. The recurrent ViT's number of recurrent passes is the architectural counterpart of $a$.

**Multi-alternative tasks require multi-dimensional extensions.** The recurrent ViT and PRISM operate on tasks (change detection, video reconstruction, eye-tracking) that have many possible response locations or many candidate hypotheses. The 1978 model is two-alternative; Sridharan et al. 2017 ([sridharan2017_sc_sensitivity_bias](sridharan2017_sc_sensitivity_bias.md)) provides the multialternative SDT framework that is the proper extension for the user's settings. Both papers — Ratcliff 1978 for the two-alternative chronometric foundation, Sridharan 2017 for the multialternative spatial extension — should be cited together when interpreting the user's models' behavior.

**Connection to LIP / FEF and the neural substrate.** Roitman & Shadlen 2002 ([roitman_shadlen2002_lip_rt](roitman_shadlen2002_lip_rt.md)) showed that LIP cells implement DDM-like ramps; Gold & Shadlen 2007 ([gold_shadlen2007_decision_making](gold_shadlen2007_decision_making.md)) reviewed the full mapping. The user's program's central self-attention substrate, which integrates contributions from many memory hubs, has been argued in the [the_user_architectural_program](../threads/the_user_architectural_program.md) thread to be the architectural analog of the parietal priority map; if so, then its temporal dynamics should follow DDM-like accumulation, and its readout to the actor should look like LIP-to-SC threshold-crossing.

**Connection to the decision-framework cluster.** The papers [hawkins1990_attention_detectability](hawkins1990_attention_detectability.md), [luo_maunsell2018_criterion_sensitivity](luo_maunsell2018_criterion_sensitivity.md), and [muller_findlay1987_sensitivity_criterion](muller_findlay1987_sensitivity_criterion.md) all use static SDT ($d'$ and criterion) — they ignore the time dimension. Ratcliff 1978 is the natural extension that adds RT and absorbs SDT as the $a \to 0$ limit. Any analysis of the recurrent ViT's behavior should *prefer* DDM-style joint choice-and-RT fits over static SDT whenever response-time information is available, because DDM is strictly more informative and reduces to SDT when latency is ignored.

**Connection to PRISM's variational inner loop.** PRISM v1's inner variational-inference loop (`THESIS.md` §2.8) iterates over the memory state until convergence — this is an inner-loop accumulation process that ends when a precision-weighted prediction error falls below a threshold. The DDM mathematics describe the same kind of bounded accumulation in a different guise, and the formal correspondence ("inner-loop iterations until convergence" $\leftrightarrow$ "diffusion steps until boundary") could be made precise in a future analysis.

**Hanks & Summerfield 2017 ([hanks_summerfield2017_perceptual_decisions](hanks_summerfield2017_perceptual_decisions.md))** is the modern cross-species review that extends DDM-style analysis from monkey-centric work to rodent and human paradigms; it is the natural complement to Ratcliff 1978 for translating between the human-psychophysics origin of DDM and the monkey-neurophysiology elaboration in Gold-Shadlen.

## 8. Citations to follow

- `ratcliff_mckoon2008_dpd_decision_review` — Ratcliff & McKoon, the modern review of the DDM and its extensions; the canonical follow-up reference. Not yet in seed.
- `ratcliff_tuerlinckx2002_estimating_parameters` — the practical fitting methodology, including handling of contaminant RT distributions and outlier trials. Not yet in seed.
- `ratcliff_rouder1998_modeling_response_times` — extension of the 1978 model to handle additional response-time effects. Not yet in seed.
- `usher_mcclelland2001_lca` — the leaky competing accumulator, a multi-alternative neural-style alternative to DDM. Not yet in seed.
- `cisek_etal2009_decisions_action` — urgency-gated decision-making, the collapsing-bounds DDM variant. Not yet in seed.
- `hawkins_etal2015_revisiting_boundaries` — explicit comparison of constant vs collapsing boundaries in monkey and human data. Not yet in seed.
- `bogacz_etal2006_physics_optimal_decisions` — derivation of optimal two-alternative decision rules and the relation between DDM, SPRT, and Bayesian inference. Not yet in seed.
- `palmer_huk_shadlen2005_2afc_motion` — psychophysics of 2AFC motion discrimination with DDM-style analysis. Not yet in seed.
