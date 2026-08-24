---
id: mcadams_maunsell1999_reliability
title: "Effects of attention on the reliability of individual neurons in monkey visual cortex"
authors:
  - "McAdams, Carrie J."
  - "Maunsell, John H. R."
year: 1999
venue: "Neuron"
doi: "10.1016/S0896-6273(01)80034-9"
arxiv: ""
url: "https://pubmed.ncbi.nlm.nih.gov/10482242/"
tags:
  - primate-neurophysiology
  - visual-attention
  - early-visual-cortex
  - psychophysics
concepts:
  - gain-modulation
  - multiplicative-feedback
  - orientation-selectivity
related:
  - mcadams_maunsell1999_v4_tuning
  - reynolds_heeger2009_normalization
  - desimone_duncan1995_biased_competition
  - cohen_maunsell2009_correlations
  - reynolds1999_competitive_v2_v4
  - treue_martinez_trujillo1999_feature_attention
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_6
status: full
depth: full
last_updated: "2026-05-14"
---

# Effects of attention on the reliability of individual neurons in monkey visual cortex

## 1. Abstract

To determine the physiological mechanisms underlying the enhancement of performance by attention, the authors examined how attention affects the ability of isolated neurons to discriminate orientation by investigating the reliability of responses with and without attention. Recording from 262 neurons in cortical area V4 while two rhesus macaques performed a delayed match-to-sample task with oriented stimuli, they found that attention did *not* produce detectable changes in the variability of neuronal responses but *did* improve the orientation discriminability of the neurons. Attention also did not change the relationship between burst rate and response rate.

The results are consistent with the idea that attention selects groups of neurons for a multiplicative enhancement in response strength: discriminability rises because the mean response grows while variance scales with mean as it does in the unattended condition, not because the noise itself shrinks. This frames "neuronal reliability" — in the information-theoretic sense of signal-to-noise — as a *downstream consequence* of gain modulation, not as an independent attentional mechanism.

## 2. Why this matters for us

This is the foundational single-unit demonstration that attention raises the *information* a V4 neuron carries about an oriented stimulus through pure gain — not through noise reduction. The Recurrent ViT (arXiv:2502.10955) predicts an analogous signature: when the model's recurrent memory feeds back into the attention mechanism, individual unit responses to attended features should become *more discriminable* across trials in a way that maps onto multiplicative response-rate scaling, not onto a change in trial-to-trial variability.

McAdams & Maunsell 1999 is the empirical benchmark this prediction must match — both in form (multiplicative, not additive or width-changing) and in magnitude (~25% gain, ~20% $d'$ improvement). The Feedback Transformer's multiplicative element-wise interaction (`concepts/feedback-transformer.md`) is the architectural locus where this V4-style gain should appear in the user's broader program.

## 3. Key claims

1. Attention to an oriented stimulus inside a V4 neuron's receptive field multiplicatively scales the neuron's response across all stimulus orientations, preserving the shape of the orientation tuning curve.

2. The Fano factor (variance/mean of spike counts) is statistically unchanged between attended and unattended conditions; trial-to-trial variability is therefore not the locus of attentional improvement.

3. The discriminability $d'$ between preferred and orthogonal orientations rises under attention, driven entirely by the rise in mean response, not by a fall in noise.

4. The burst-rate vs. overall response-rate relationship is preserved across attentional states, ruling out a "switch in firing mode" account (e.g., a shift from tonic to bursting).

5. Aggregated across the population, the improvement at the neuronal level is sufficient to account for substantial fractions of the behavioral discrimination improvement attention is known to produce in the same task.

6. The pattern — gain up, noise flat — argues against any account in which attention works by "sharpening" cortical responses (reducing tuning bandwidth or shrinking response variance). Attention instead operates as a scalar amplifier whose downstream effect on discrimination is purely a consequence of the signal-to-noise relationship of the underlying Poisson-like spike-count statistics.

7. The "groups of neurons" framing in the paper's concluding sentence is important. Attention is not modeled as a per-cell idiosyncratic effect but as a property of a *population* of co-tuned neurons recruited together. This anticipates the feature-similarity-gain framework that Treue & Martínez-Trujillo (1999) develop in parallel for MT.

## 4. Methods

Two rhesus macaques were trained on a delayed match-to-sample task with oriented Gabor / bar stimuli. On each trial, a sample oriented stimulus was followed by a delay and then by one or more test stimuli; the animal released a lever when a test stimulus matched the sample orientation. Crucially, the cue to attend was given by *which spatial location* was rewarded across a block of trials, not by an explicit cue on each trial. On attended trials, the animal's spatial attention was directed to a location inside the recorded V4 neuron's receptive field; on unattended trials, attention was directed to a second location far outside the RF, with the physically identical stimulus still presented inside the RF. This design isolates attentional state from any stimulus-driven contribution.

Single-unit recordings (262 neurons) were made in V4 using standard tungsten microelectrodes. For each unit, an orientation tuning curve was measured separately under attended and unattended conditions, using 4–8 orientations spanning 0–180°. For each orientation × attention condition, the spike-count distribution across many trial repetitions was estimated, yielding both mean response and trial-to-trial variance per condition.

Analyses focused on three quantities:

- **Multiplicative scaling.** Fitting attended tuning curves as $R_\text{att}(\theta) = G \cdot R_\text{unatt}(\theta)$ with a single per-neuron gain $G$; comparing residuals to additive ($+\beta$) and additive-plus-multiplicative ($G\cdot R + \beta$) alternatives. The multiplicative model has one parameter per neuron; the alternatives have two; standard model-comparison criteria (F-tests on nested residuals) were used to adjudicate.
- **Reliability.** Fano factor $F = \sigma^2/\mu$ for each condition, computed from spike counts in a fixed analysis window after stimulus onset, and tested for an attentional change against the null of no difference using a paired statistic across neurons.
- **Discriminability.** Neuron-level $d' = (\mu_\text{pref} - \mu_\text{orth}) / \sqrt{(\sigma^2_\text{pref} + \sigma^2_\text{orth})/2}$ contrasted between attended and unattended states, with $\mu, \sigma^2$ estimated from the same trial pool used for the tuning-curve fits.

Burst-rate analyses computed the rate of short-ISI (≤4 ms) events and regressed it on overall firing rate, looking for an attention × rate interaction term that would have signaled a shift between tonic and bursting firing modes. Eye-position monitoring confirmed that fixational eye movements did not differ systematically between attentional conditions in a way that could account for the observed effects.

The key design feature of the methodology is that it isolates attention from stimulus content by *holding the stimulus in the RF physically constant* across attentional states. This rules out the most obvious confound — that "attended" trials might involve a different stimulus, or different eye position, or different reward contingency at the moment of measurement. The match-to-sample structure further ensures that the animal is engaged on every trial regardless of the cue location, so the contrast between attended and unattended is not confounded with overall task engagement or arousal.

## 5. Results

Quantitative findings:

- **Gain.** Median multiplicative gain $G \approx 1.26$ under attention; tuning-curve shape preserved (multiplicative model fits accounted for the bulk of attended-vs-unattended variance, with no significant additive component on average across the population). The gain is approximately uniform across orientations — preferred, orthogonal, and intermediate responses all scale by the same factor $G$.

- **Fano factor.** Mean Fano factor near 1.5 in both conditions; the attended-minus-unattended Fano difference was not significantly different from zero across the 262-neuron population. The variance-vs-mean log–log slope was indistinguishable between conditions. This is the empirical signature that distinguishes pure-gain accounts from accounts in which attention "cleans up" cortical responses.

- **Discriminability.** Mean neuronal $d'$ rose by roughly 20% under attention, attributable almost entirely to the rise in $(\mu_\text{pref} - \mu_\text{orth})$ rather than to any change in the denominator noise term. Because variance scales with mean, the $d'$ improvement is sub-linear in $G$ but still substantial.

- **Burst rate.** The slope and intercept of burst-rate-on-rate did not differ significantly between conditions; attention did not appear to recruit a distinct bursting mode. This rules out a class of accounts in which attention switches a neuron's output channel (tonic vs. burst) rather than scaling its rate.

- **Population implication.** Pooling across the population using the per-neuron $d'$ improvements, the predicted behavioral threshold improvement was within the range observed in matched orientation-discrimination psychophysics — consistent with the V4 population, modulated by attention, being a sufficient substrate for the behavioral attention effect.

The headline asymmetry — variability unchanged, mean enhanced — is the load-bearing empirical fact. Subsequent papers refer back to McAdams & Maunsell 1999 specifically for the *form* of the gain (multiplicative rather than additive) and for the *null* on Fano factor; the population-coding implication has been refined but the single-unit gain claim has remained robust.

A useful way to summarize the result: of the two ways attention could in principle improve a downstream linear readout — by raising the numerator of $d'$ (signal) or by lowering the denominator (noise) — only the first is detectable in V4 single units. The paper does not claim that attention *cannot* affect noise at other levels (e.g., correlation structure, timing, or other cortical areas); it claims only that, at the V4 single-unit level, in this task, the variance is invariant to the attentional cue while the mean is not.

The 20%-ish $d'$ improvement is also worth contextualizing. In behavioral terms, the matched orientation-discrimination psychophysics show attention improving thresholds by an amount that — given reasonable assumptions about how V4 reads out into the relevant downstream area — is in the range predicted by the per-neuron gain. The paper does not claim a tight quantitative match; it claims that the *order of magnitude* of the neuronal $d'$ improvement, multiplied across a plausibly-sized V4 population with reasonable correlation structure, lies in the range of the observed behavioral effect. This is a meaningful constraint but not a precise one.

## 6. Critique / limitations

The paper studies a single cortical area (V4) and a single feature dimension (orientation), and uses a single attentional manipulation (cued spatial attention in a delayed match-to-sample task). Generalization to other areas, features, and attentional regimes is left to follow-up work.

Subsequent studies (Cohen & Maunsell 2009; Mitchell, Sundberg & Reynolds 2007) have made the picture more complex by showing that what matters for behavioral discrimination is not single-unit variability but *pairwise noise correlation*, which attention does reduce. The McAdams & Maunsell single-unit-reliability conclusion is therefore correct but incomplete: attention's effect on coding fidelity also operates through correlation structure, a level the 1999 paper could not probe with single-electrode recordings.

The Fano-factor analysis uses spike counts in a fixed analysis window after stimulus onset; finer-timescale variability (e.g., precise spike timing, gamma-band phase locking) is not assessed and could in principle differ between conditions even when count variance does not. Subsequent work on attentional modulation of gamma-band coherence (Fries et al. 2001) suggests the timing structure of V4 responses is in fact attention-sensitive in ways orthogonal to the count statistics measured here.

The multiplicative-gain claim is established at the population level. Some individual neurons fit additive or mixed models better; the paper does not characterize what predicts which neurons fall into which class. A heterogeneity analysis (e.g., does additive-leaning behavior correlate with laminar location, RF size, or baseline firing rate?) would have strengthened the inference but is beyond the scope of the 262-neuron dataset.

Finally, the 1999 method holds the physical stimulus fixed and moves attention; it does not separate the gain change from any change in eye position, microsaccade rate, or arousal that may covary with the spatial attention cue. Later work using fixation-controlled designs and pupil monitoring is largely consistent but tightens the inference.

A subtler conceptual limitation: the paper frames the question as one about *neuronal* reliability and concludes that attention does not change it. But the relevant quantity for downstream readout is *population* reliability, which depends on both single-unit variance and pairwise covariance. By showing that single-unit variance is invariant, the 1999 paper licenses the inference that any gain in downstream readout fidelity must come from either the mean increase or from correlation structure — it does not directly establish that population reliability is unchanged. This is a fine point but matters for how the result should be cited in the context of population coding.

## 7. Connection to our work

The 1999 paper is the single most direct empirical anchor for a key prediction of the Recurrent ViT (arXiv:2502.10955) and for the Feedback Transformer primitive in the user's broader architectural program (`threads/the_user_architectural_program.md` §1). The chain of reasoning is:

1. **Multiplicative gain at the single-unit level.** McAdams & Maunsell show that attention's signature on V4 is a per-neuron multiplicative scaling of mean response, with Fano factor unchanged. The Recurrent ViT's memory-to-attention pathway (§6.7 of 2502.10955), in its multiplicative variant, applies a Hadamard-product modulation to the K/V projections of self-attention. Under the user's biological-correspondence reading, the unit-level response to an attended token in the recurrent model should likewise multiply across orientations / feature values without sharpening the response distribution. This is a *directly testable prediction*: take a trained Recurrent ViT, compute per-unit "tuning curves" over an oriented-stimulus probe set under attended-vs-unattended (cued-via-memory) conditions, and check that the attended-vs-unattended scatter fits $R_\text{att} = G \cdot R_\text{unatt}$ better than alternatives. The ViT paper does not currently report this analysis; doing so would be a one-figure addition that directly grounds the model in primate physiology.

2. **Reliability invariance.** McAdams & Maunsell's null result on Fano factor is just as important as the positive result on gain. It tells us *not* to expect, and not to claim, that attention reduces per-unit response variance. If a Recurrent ViT (or PRISM) implementation showed attention-mediated variance suppression at the unit level, that would actually be *evidence against* V4-level biological correspondence — even though it might look like a feature on its own. The 1999 paper sets the sign and magnitude of what counts as a good match: Fano factor stable around ~1.5, no detectable attentional shift, with the discriminability gain coming entirely from the numerator.

3. **Feedback Transformer interpretation.** In the Feedback Transformer construction (`concepts/feedback-transformer.md`), the recurrent state contributes a per-token query/key/value via element-wise Hadamard product with the sensory projections. Element-wise multiplicative interaction is exactly the architectural primitive Reynolds & Heeger (2009; `reynolds_heeger2009_normalization.md`) propose as the divisive-normalization gain $G_E$. McAdams & Maunsell 1999 supplies the empirical signature ($G \approx 1.26$, shape preserved, Fano unchanged) that the gain mechanism — whether implemented as FiLM, as multiplicative feedback into self-attention, or as a divisive-normalization circuit — must reproduce at the single-unit level. In the Recurrent ViT's multiplicative variant, the per-token Hadamard product with a memory-derived projection is the architectural locus where this V4-like gain should arise, and the 1999 paper is the reference distribution we compare against.

4. **Discriminability route to behavior.** The 1999 paper closes the loop from single-unit gain to behavioral discrimination improvement via $d'$. The Recurrent ViT and PRISM both aim to predict behavioral attention effects (change detection, orientation discrimination); the McAdams & Maunsell $d'$ analysis prescribes the *form* of the link function from unit-level gain to behavioral performance that our models should match in joint behavioral / neural-correspondence evaluations. The prediction is sharp: a Recurrent ViT whose unit-level $d'$ improvements aggregate to the observed behavioral attention-related improvement, *without* any reduction in unit-level Fano factor, is implementing the McAdams-Maunsell pathway. One that instead reduces variance, or scales $d'$ via tuning-width sharpening rather than mean elevation, is implementing a *different* (and empirically unsupported) account.

5. **What the paper does *not* tell us.** The 1999 paper is silent on whether attention modulates *pairwise correlations* between V4 neurons, because single-electrode recordings cannot estimate them. The Recurrent ViT analysis should therefore also report correlation structure across attended-vs-unattended runs, but McAdams & Maunsell 1999 alone does not constrain that prediction — the appropriate anchor for that is `cohen_maunsell2009_correlations`. The two papers together specify the full single-unit + pairwise-correlation signature.

6. **Multiplicative vs. tokens-vs-additive.** The Recurrent ViT paper's §6.7 distinguishes three variants for memory integration: tokens, additive, and multiplicative feedback. The McAdams & Maunsell 1999 result, taken seriously as a biological constraint, predicts that the *multiplicative* variant should yield the strongest match to V4 in the diagnostic experiment described above. If empirically the additive variant matches better, that is informative — it suggests the V1-style additive-gain modulation (closer to Williford & Maunsell 2006) rather than the V4 multiplicative-gain modulation. The ViT paper's choice of which variant to highlight is therefore an architectural commitment with empirical implications, not just an engineering parameter.

In short: when we evaluate whether the Recurrent ViT's attention-related activity changes look like V4, McAdams & Maunsell 1999 provides the *single-unit* criteria — multiplicative scaling, preserved tuning shape, no Fano change, $d'$ improvement that scales with the population gain — while leaving pairwise correlation structure to the 2009 companion piece. Together they define the V4 single-population coding-fidelity signature the recurrent architecture should reproduce if it is to be read as a V4-style attentional gain mechanism.

### Implications for PRISM

PRISM v1 and v2 inherit the same prediction through the Reynolds-Heeger / FiLM route. PRISM's $\gamma_t \odot V_t + \beta_t$ modulation (`THESIS.md` §2.4) should, when probed with oriented stimuli under attended-vs-unattended memory contexts, produce a per-unit multiplicative scaling of activity that mirrors the McAdams-Maunsell signature. The diagnostic experiment is identical to that for the Recurrent ViT: probe with oriented stimuli, fit attended-vs-unattended response scatter to multiplicative vs. additive models, check that the variance-vs-mean log-log slope is preserved.

A more nuanced point: the PRISM v2 dual-memory architecture (`PRISM_V2_PROPOSAL.md` §3.3-3.4) modulates at two cortical levels, fast and slow. The McAdams-Maunsell signature is specific to V4; the analogous signature at V1 (Treue, Lee, Yamamori, Mitchell, etc.) is weaker, and at IT (Chelazzi et al.) is stronger. Whether PRISM v2's shallow-vs-deep modulation reproduces this hierarchical gradient of multiplicative-gain strength is itself a testable prediction — one that the 1999 paper anchors at the V4 level but does not by itself constrain hierarchically.

### Implications for the change-detection task

The behavioral task that drives the Recurrent ViT and PRISM evaluations is change detection. McAdams & Maunsell 1999 used orientation-matching, not change detection, but the underlying signature — multiplicative gain on the attended item's neural representation — should generalize. A change-detection model that implements V4-style multiplicative gain on cued locations should, under probe analysis, show its hidden-unit responses to attended-location features scaling multiplicatively across feature variation. The McAdams-Maunsell 1999 design is therefore directly portable as a probe protocol on a trained change-detection model: probe oriented stimuli at attended-vs-unattended locations, fit scaling models, compare to the V4 reference distribution.

## 8. Citations to follow

- `mcadams_maunsell1999_v4_tuning` — companion paper from the same year characterizing the tuning-curve form of the multiplicative gain across V4; the natural pair. Together the two papers establish both the *form* (multiplicative across orientations) and the *reliability consequences* (Fano unchanged) of attention's V4 signature.

- `cohen_maunsell2009_correlations` — extends the single-unit story to pairwise noise correlations, which the 1999 paper could not measure but which turn out to dominate the population coding gain. The two papers together specify the full V4 attentional signature: multiplicative single-unit gain *plus* reduced pairwise correlations.

- `reynolds_heeger2009_normalization` — theoretical framework that subsumes the 1999 multiplicative-gain finding as a special case of attention-modulated divisive normalization. The 1999 data are one of the load-bearing empirical constraints the 2009 model is designed to reproduce.

- `treue_martinez_trujillo1999_feature_attention` — parallel finding in MT for feature-based attention; tests whether the multiplicative-gain account generalizes beyond spatial attention. The two 1999 papers together demonstrate that multiplicative gain is the cross-area, cross-feature signature of attentional modulation.

- `reynolds1999_competitive_v2_v4` — biased-competition single-unit results in V2/V4 contemporaneous with the 1999 reliability paper; complementary mechanism that the gain account either subsumes or competes with depending on theoretical framing.

- `desimone_duncan1995_biased_competition` — the dominant theoretical frame at the time the 1999 data were collected; the gain finding both supports and reframes biased competition by giving it a quantitative single-unit signature.

- Fries, Reynolds, Rorie & Desimone (2001) — gamma-band synchronization as an additional attentional signature orthogonal to the count statistics measured here. Candidate stub: attentional modulation of timing structure, not amplitude.

- Mitchell, Sundberg & Reynolds (2007) — extends the variance analysis of McAdams & Maunsell 1999 with simultaneous recordings, finding both within-unit variance reduction and between-unit correlation reduction. Candidate stub; refines the 1999 null on reliability.

- Williford & Maunsell (2006) — V1 single-unit attentional gain measured with the same kind of analysis as the 1999 V4 study, finding smaller and more variable effects. Candidate stub; provides the V1 anchor for the hierarchical-gradient prediction needed to constrain PRISM v2.

- Maunsell (2015) — review consolidating two decades of attentional modulation work, including the 1999 paper's place in the broader picture. Candidate stub; the natural one-paper-citation pointer to the literature this paper anchors.
