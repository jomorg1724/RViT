---
id: prinzmetal2005_rt_vs_accuracy
title: "Attention: reaction time and accuracy reveal different mechanisms"
authors:
  - "Prinzmetal, William"
  - "McCool, Christin"
  - "Park, Samuel"
year: 2005
venue: "Journal of Experimental Psychology: General"
doi: "10.1037/0096-3445.134.1.73"
arxiv: ""
url: "https://pubmed.ncbi.nlm.nih.gov/15702964/"
tags:
  - visual-attention
  - posner-cuing
  - psychophysics
  - reaction-time
concepts:
  - cueing-effect
  - validity-effect
  - signal-detection-theory
  - chronometric-function
  - psychometric-function
related:
  - posner1980_orienting
  - muller_findlay1987_sensitivity_criterion
  - hawkins1990_attention_detectability
  - lu_dosher1998_external_noise
  - cameron2002_covert_attention_contrast
  - saltzman_garner1948_rt_span
  - carrasco2011_visual_attention_25y
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_56
status: full
depth: full
last_updated: "2026-05-16"
---

# Attention: reaction time and accuracy reveal different mechanisms

## 1. Abstract

Prinzmetal, McCool, and Park argue that the cueing effects measured in spatial-attention experiments are not produced by a single attentional mechanism but by two functionally distinct ones, and that the standard dependent variables — reaction time and accuracy — index them differently. *Voluntary* attention is the deliberate, endogenous allocation of perceptual resources to a likely target location; it enhances the perceptual representation at that location and so produces benefits in both accuracy and RT. *Involuntary* attention is a reflexive, exogenously triggered channel-selection process; it does not alter the perceptual representation but biases decision and response selection toward the cued location, so it shows up in RT but not in accuracy. Across four spatial-cuing experiments that orthogonally manipulate cue informativeness and dependent variable, the authors show the predicted dissociation: cues that should engage only involuntary attention produce RT validity effects with negligible accuracy effects, whereas informative cues that engage voluntary attention produce both. The paper concludes that RT-only paradigms and accuracy-only paradigms are not redundant measurements of the same underlying construct and that conclusions from one cannot be transferred uncritically to the other.

## 2. Why this matters for us

The Recurrent ViT (arXiv:2502.10955) reports cueing effects in both reaction time (more precisely, a chronometric proxy: per-step accuracy as a function of recurrent step at the cued location) and trial-final accuracy. Prinzmetal et al. supply the interpretive constraint that these two measures are not interchangeable — they can be driven by *different* underlying mechanisms. This matters directly for how the model's behavior is interpreted: an architecture that produces an RT-only benefit at the cued location is consistent with a decision-stage bias, whereas an architecture that produces both RT and accuracy benefits is consistent with a perceptual-representation change. PRISM's actor head produces both kinds of behavior and so faces the same interpretive question. The Müller–Findlay (1987) sensitivity/criterion framework is the SDT-level vocabulary in which the dissociation is most cleanly stated, and we adopt it for §7.

## 3. Key claims

1. Spatial cueing engages at least two functionally distinct attentional mechanisms, voluntary and involuntary, with different signatures across dependent measures.
2. Voluntary attention enhances the perceptual representation at the cued location and produces benefits in both accuracy and RT.
3. Involuntary attention is a channel-selection or decision-stage process that biases responses toward the cued location and produces an RT benefit *without* a corresponding accuracy benefit.
4. The informativeness of the cue (whether it predicts target location above chance) is the experimental lever that determines which mechanism is engaged: non-predictive peripheral cues isolate involuntary attention; predictive central cues recruit voluntary attention.
5. Consequently, RT-only and accuracy-only spatial-cuing experiments measure overlapping but non-identical constructs, and apparent contradictions in the cuing literature can be resolved by recognizing which mechanism each paradigm taps.

## 4. Methods

Four spatial-cuing experiments using variants of the Posner paradigm. The shared structure is: a central fixation, a cue (peripheral abrupt-onset or central symbolic), a variable cue–target SOA, and a target requiring a speeded discrimination or an unspeeded forced-choice accuracy judgment. The factorial design crosses (i) cue type — non-predictive peripheral vs. predictive central — and (ii) response regime — speeded RT with accuracy at ceiling vs. accuracy-emphasized with brief masked targets that hold accuracy off ceiling. Across experiments the authors manipulate cue validity (whether the cue's spatial information is informative), display set size, and target eccentricity to triangulate the conclusion. Mean correct RT and percent correct are reported by (cue × validity × experiment), and conclusions are drawn from the *pattern of dissociation* between RT and accuracy benefits, not from a single number.

## 5. Results

The canonical finding across the four experiments:

- Non-predictive peripheral cues produced a robust RT validity effect (valid faster than invalid, on the order of tens of milliseconds) but no reliable accuracy validity effect when accuracy was measured under masked, off-ceiling conditions.
- Predictive central cues produced *both* an RT validity effect *and* a reliable accuracy validity effect (valid more accurate than invalid by a few percent).
- The dissociation was not attributable to ceiling effects in the speeded condition or to floor effects in the accuracy condition: the conditions were calibrated so that both RT and accuracy had room to vary in both paradigms.
- The size of the RT validity effect was comparable across the two cue types, but only the predictive cue moved accuracy. This is the load-bearing pattern: a single common mechanism would predict the two measures to move together.

The authors interpret the pattern as direct evidence that involuntary attention does not modulate perceptual representation. If it did, accuracy under masked targets would have to move with RT. It does not.

## 6. Critique / limitations

The dissociation is established at the behavioral level only. The paper does not (and cannot) directly localize the proposed mechanisms to specific neural stages. Subsequent SDT analyses (Hawkins et al. 1990; Lu & Dosher 1998; Cameron, Tai, & Carrasco 2002) recover the same dissociation but parameterize it differently — sometimes as sensitivity vs. criterion shifts within a single SDT framework rather than as two architecturally distinct mechanisms — and the choice between these parameterizations cannot be made on Prinzmetal et al.'s behavioral data alone.

Whether "involuntary attention as response bias" is genuinely a separate mechanism or simply a smaller, faster instance of the same gain-modulation process tapped by voluntary attention remains contested in the post-2005 literature. The Müller–Findlay (1987) framing — sensitivity changes vs. criterion changes within signal detection theory — is the more parsimonious alternative that several authors (Carrasco 2011 §III; Lu & Dosher 1998) prefer.

The paper's claim that involuntary attention does not alter perceptual representation is also in tension with later contrast-discrimination work (e.g., Cameron, Tai, & Carrasco 2002) showing that even non-predictive peripheral cues can move the psychometric function for contrast — a direct measure of perceptual sensitivity. The most likely synthesis is that involuntary attention does have a sensitivity component, but a smaller one than voluntary attention, which the four-experiment design here was underpowered to detect.

Finally, the experiments rely on RT in the speeded condition being unconfounded by accuracy. The authors check for speed–accuracy tradeoff, but the standard worry — that subjects use a more conservative response criterion at uncued locations and so trade RT for accuracy — is not fully eliminated by the design.

## 7. Connection to our work

The Recurrent ViT paper reports two distinct behavioral signatures of attention. The first is a *chronometric* signature: at the cued location, per-step accuracy rises faster across recurrent steps than at uncued locations (Fig. 3F-style curves). This is the model's RT-analog — fewer recurrent steps are needed to reach a given accuracy at the attended location. The second is a *psychometric* signature: at the final recurrent step, trial accuracy is higher at the cued location than at uncued ones. These two signatures co-occur in the Recurrent ViT just as they do in human subjects given a predictive central cue, and they would naturally be interpreted as two faces of one underlying mechanism — until Prinzmetal et al. dissociate them.

The relevant Prinzmetal-style question for our architecture is: *which* of the two mechanisms does the Recurrent ViT's cued-token attention implement? If the cue biases the model's softmax-over-tokens toward the cued patch without altering the patch's feature representation, this is the architectural correlate of *involuntary*, decision-stage attention: an RT-style speed-up without a representational change. If, instead, the recurrent rollout uses the cue to alter the *features* computed at the cued patch — by changing which feature dimensions the patch contributes to subsequent attention — this is the architectural correlate of *voluntary*, perceptual-representation attention.

The Müller–Findlay (1987) sensitivity/criterion framework is the cleanest way to phrase this for our architecture: a criterion shift is a change in the model's effective decision threshold at the cued location (an additive bias on the readout logit) and predicts an RT-style benefit only; a sensitivity shift is a change in the *slope* of the psychometric function at the cued location and predicts benefits in both RT and accuracy. PRISM's actor head produces both kinds of behavior because both effects fall out of the prediction-error map naturally: the cue increases prediction-error mass at the cued patch (sensitivity-like) *and* the actor reads out from that mass with a learned policy that can implement a criterion-like bias on top.

The practical experimental upshot for the manuscript is that an architectural ablation that *removes* recurrent updates at the cued patch while keeping the cue's logit-bias intact should preserve the RT-style chronometric benefit but eliminate the accuracy benefit — the Prinzmetal dissociation as a model-internal manipulation. Conversely, an ablation that *keeps* recurrent updates but zeroes the explicit logit bias at the cued readout should preserve the accuracy benefit and weaken the RT benefit. Running this 2x2 in the Recurrent ViT or PRISM would constitute a direct architectural test of the Prinzmetal dissociation, with the additional payoff that the model's two mechanisms can be cleanly isolated in a way they cannot be in human subjects.

This also bears on the interpretation of PRISM v2's slow/fast memory (`PRISM_V2_PROPOSAL.md` §3.3): slow memory is the natural locus for voluntary, sensitivity-style attention because it carries the cue's predictive content across many steps; fast memory is the natural locus for involuntary, criterion-style attention because it implements a rapid, transient bias. The Prinzmetal taxonomy is therefore not just a behavioral constraint but a roadmap for which architectural component should be expected to produce which behavioral signature.

## 8. Citations to follow

- `muller_findlay1987_sensitivity_criterion` — the SDT-level vocabulary (sensitivity vs. criterion shifts) in which the Prinzmetal dissociation is most cleanly stated; load-bearing for §7.
- `hawkins1990_attention_detectability` — SDT deconstruction of the cuing effect; the empirical precedent that pre-figures Prinzmetal et al.'s dissociation.
- `lu_dosher1998_external_noise` — external-noise paradigm separating stimulus-enhancement from external-noise-exclusion accounts of attention; an alternative parameterization of the same dissociation.
- `cameron2002_covert_attention_contrast` — shows non-predictive peripheral cues do shift the contrast psychometric function, tensioning Prinzmetal's strong "no perceptual change" claim.
- `saltzman_garner1948_rt_span` — the historical origin of using RT as a chronometric measure of attentional capacity; relevant for situating the RT measure within the broader chronometric tradition.
- `carrasco2011_visual_attention_25y` — modern review that situates the Prinzmetal dissociation within the broader graded-gain account of covert attention.
