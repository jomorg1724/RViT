---
id: salzman1992_mt_microstim_methods
title: "Microstimulation in visual area MT: effects on direction discrimination performance"
authors:
  - "Salzman, C. Daniel"
  - "Murasugi, Chieko M."
  - "Britten, Kenneth H."
  - "Newsome, William T."
year: 1992
venue: "Journal of Neuroscience"
doi: "10.1523/JNEUROSCI.12-06-02331.1992"
arxiv: ""
url: "https://doi.org/10.1523/JNEUROSCI.12-06-02331.1992"
tags:
  - primate-neurophysiology
  - lesion-microstimulation
  - visual-attention
  - psychophysics
  - decision-making
concepts:
  - microstimulation
  - drift-diffusion-model
  - signal-detection-theory
  - hidden-state-perturbation
related:
  - salzman1990_mt_microstim
  - salzman_newsome1994_winner_take_all
  - ditterich2003_microstim_rt
  - hanks2006_lip_microstim
  - muller2005_sc_microstim_covert
  - cavanaugh_wurtz2004_sc_change_blindness
  - roitman_shadlen2002_lip_rt
  - gold_shadlen2007_decision_making
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - pubmed
status: summary
depth: full
last_updated: "2026-07-04"
---

# Microstimulation in visual area MT: effects on direction discrimination performance

## 1. Abstract

This is the full-length quantitative and methodological companion to Salzman, Britten & Newsome's 1990 *Nature* letter, which first showed that electrical microstimulation of a direction-selective column in extrastriate area MT (V5) biases a monkey's perceptual judgment of motion direction. Two rhesus macaques performed a near-threshold, two-alternative motion-direction discrimination on a stochastic random-dot kinematogram whose motion coherence was varied trial-by-trial and whose aperture was centered on the receptive field of a physiologically characterized MT column. On a random half of the trials, weak microstimulation was applied to that column while the monkey viewed the dots. Across 139 experiments the authors observed direction-specific behavioral biases toward the stimulated neurons' preferred direction: in 86 of the 89 experiments that yielded a statistically significant effect (~97%), microstimulation shifted the psychometric function so that the monkey more often reported motion in the column's preferred direction. The paper introduces the **equivalent-signal analysis** — quantifying the perceptual impact of stimulation as the amount of real coherent motion (in the preferred direction) that would produce the same horizontal shift of the psychometric function. Stimulation was equivalent, on average, to adding a substantial increment of coherent dots in the preferred direction, sometimes exceeding the animal's own coherence threshold. The result is the canonical causal demonstration that the activity of a small, columnar population of feature-selective sensory neurons is *sufficient* to determine a perceptual choice, and it establishes the definitive effect-size numbers and analysis machinery for the microstimulation-and-perception literature.

## 2. Why this matters for us

This is the load-bearing biological precedent for the program's core causal method. Our recurrent-ViT program does not just fit primate psychophysics correlationally; it aims to *intervene* on the model the way experimenters intervene on the brain, and the `attn_clamp` operator — an additive bias on the attention logits that pushes the model's attention map toward or away from a location — is the in-silico analog of exactly this experiment. Salzman 1992 is the paper that makes that analogy quantitative rather than hand-wavy: it shows that a small, additive push injected into a *feature-selective sensory* population produces a graded, direction-specific shift of the decision, and it supplies the analytic device (equivalent-signal) for asking "how much stimulus is this artificial perturbation worth?"

The paper is doubly relevant now because the program has just built the `motion4` battery environment — a random-dot motion-direction change-detection task that reuses the entire conv → recurrent-ViT → xLSTM → QR-DQN stack with only the pixels changed (moving-dot fields instead of Gabors). Salzman's task *is* a random-dot motion discrimination in MT-RF-centered apertures; `motion4` is the RL-task cousin of that stimulus. So this card is the anchor for two things at once: (a) the causal logic that `attn_clamp` is meant to reproduce, and (b) the exact stimulus family the new environment instantiates. Crucially, it also pins down *which node* microstimulation perturbed — a direction-tuned *sensory* population, i.e. MT/V5, mapping onto our model's **perception layer / priority stream**, not the downstream value/accumulator. Keeping that distinction straight is what lets us predict whether clamping perception vs. clamping the QR-DQN value head should reproduce this signature.

## 3. Key claims

1. **MT microstimulation produces direction-specific perceptual bias.** Injecting current into a direction-selective MT column shifts the psychometric function so the monkey more often reports motion in the column's preferred direction. The bias sign follows the column's tuning, not the current polarity per se — this is the defining control that rules out a nonspecific arousal or motor account.
2. **The effect is highly reliable.** Of 139 experiments, 89 produced a statistically significant effect, and in 86 of those 89 (~97%) the bias was in the preferred (not opposite) direction. The near-unanimous sign agreement is the paper's strongest single result.
3. **The effect is graded and quantifiable as an equivalent signal.** The horizontal shift of the psychometric function can be re-expressed as the amount of real coherent motion (in the preferred direction) that would produce the same behavioral shift. Stimulation is therefore not an on/off switch but a graded addition to the sensory evidence.
4. **The equivalent signal can be large.** For many sites the stimulation was worth an increment of coherent motion comparable to, and sometimes exceeding, the animal's own psychophysical threshold — i.e. a few tens of pulses into ~100–200 neurons can rival the signal from a full stimulus.
5. **Column organization matters.** The effect depends on stimulating within a well-tuned directional column; sites with heterogeneous or poorly tuned local tuning gave weaker or absent effects, consistent with the perturbation acting through the local population's shared direction preference.
6. **Sensory sufficiency for choice.** Because a modest, spatially local perturbation of a feature-selective sensory representation reliably steers the perceptual report, the activity of these neurons is *causally sufficient* (not merely correlated) to influence the decision — the headline conceptual claim of the whole series.

## 4. Methods

**Subjects and task.** Two rhesus macaques were trained on a two-alternative forced-choice motion-direction discrimination. On each trial a stochastic random-dot kinematogram (RDK) presented dots, a controlled fraction of which moved coherently in one of two opposite directions while the rest moved randomly; the monkey reported the perceived direction with an eye movement to one of two targets. Motion coherence was varied across trials to sweep out a full psychometric function (proportion of "preferred-direction" choices vs. signed coherence). Coherence was kept near the animal's perceptual threshold so the judgment was difficult and thus maximally sensitive to a small added signal.

**Physiological characterization.** Before each experiment the authors recorded from the MT site to establish that the local population was direction-selective and to measure its preferred direction and receptive-field location. The RDK aperture was then centered on that receptive field, and the two response directions were aligned to the column's preferred and anti-preferred (null/opposite) axes. This alignment is what makes "bias toward the preferred direction" a meaningful, pre-registered prediction.

**Microstimulation.** On a random ~50% of trials, a train of weak biphasic current pulses (low microampere range, tens of pulses over the motion-viewing epoch) was delivered through the recording microelectrode to the characterized column. Stimulated and non-stimulated trials were interleaved and analyzed against each other, so the non-stimulated trials serve as the within-session baseline psychometric function.

**Equivalent-signal analysis (the paper's methodological contribution).** The authors fit psychometric functions to stimulated and non-stimulated trials separately and measured the horizontal displacement between them along the coherence axis. That displacement, expressed in units of coherence, is the **equivalent visual signal** — the amount of real coherent motion in the preferred direction that would move the psychometric function by the same amount. This converts an abstract "stimulation effect" into an interpretable, comparable quantity (percent coherence), enabling comparison across sites, animals, and even across the sensitivity of the recorded neurons themselves.

**Scope and controls.** The 139 experiments span many MT sites across the two animals. Controls include: the direction-specificity control (bias sign tracks tuning), interleaving to cancel slow performance drift, and site-tuning covariates to relate effect magnitude to local directional homogeneity. Because both the report and the analysis are near threshold, the design isolates the additive sensory contribution of the injected current from ceiling/floor and motor confounds.

## 5. Results

- **Reliability and sign.** 89 of 139 experiments reached statistical significance; in 86 of those 89 (~97%) the induced bias was toward the stimulated column's preferred direction. This near-total sign agreement is the definitive quantitative statement of the microstimulation-biases-perception result.
- **Psychometric shift.** Stimulation shifted the psychometric function horizontally toward more "preferred-direction" reports across the coherence range, rather than merely flattening it — the signature of an *added signal* rather than added noise or a change of slope.
- **Equivalent-signal magnitudes.** Re-expressed as equivalent coherent motion, the stimulation effect was frequently a substantial fraction of, and at some sites exceeded, the animal's own coherence threshold. A local, columnar perturbation therefore rivals a full sensory stimulus in its behavioral leverage.
- **Dependence on local organization.** Larger, cleaner effects came from sites embedded in well-tuned directional columns; sites with weak or mixed local tuning yielded weaker effects, consistent with the perturbation acting through the shared direction preference of the stimulated neighborhood.
- **Gradedness.** Because the effect is measured as a continuous coherence-equivalent, it establishes that the sensory contribution to the choice is graded and additive — the empirical basis for treating perceptual evidence as a continuous quantity that can be nudged, which is precisely how an additive attention-logit bias behaves.

(Where I am not certain of the exact microampere values, pulse counts, or the precise mean equivalent-coherence figure, I state the effect qualitatively; the load-bearing verified numbers are 139 experiments, 89 significant, 86/89 ≈ 97% in the preferred direction, and the introduction of the equivalent-signal analysis.)

## 6. Critique / limitations

**Electrical stimulation is nonspecific.** Current activates whatever lies near the electrode — cell bodies, dendrites, and fibers of passage — not a clean, genetically defined direction channel. The direction-specificity control (bias tracks local tuning) mitigates this, but the method cannot isolate a cell type; the effect is a property of the local mixed population, not of a labeled line.

**Sufficiency, not necessity.** The experiment shows that adding activity to an MT column is *sufficient* to bias the choice. It does not show that this column's activity is *necessary* — inactivation/lesion studies are the required complement. Sufficiency of a sensory node is exactly the claim our `attn_clamp` experiments can also only make on their own.

**2AFC readout conflates sensitivity and bias.** The behavioral measure is a psychometric shift in a 2AFC. As later signal-detection re-analyses in this literature emphasize (e.g. the sensitivity-vs-criterion decompositions applied to SC work), a raw psychometric shift can reflect a change in the effective evidence (sensitivity) or in the decision criterion (bias). Salzman's "equivalent-signal" framing treats it as added evidence, which is the natural reading for a sensory-node injection, but the 2AFC design does not formally partition the two.

**Site heterogeneity and negative sites.** ~36% of experiments did not reach significance, and the effect magnitude depends on local tuning homogeneity that is not fully controlled a priori. The reliability statistic (86/89) is conditioned on significant sessions and should be quoted alongside the base rate.

**Feature and area generality.** The result is specific to MT and to motion direction. Whether the same additive-sufficiency logic holds for other features or other areas is answered by the *rest* of the microstimulation literature (LIP, FEF, SC), not by this paper alone — which is precisely why the related-slug set spans those areas.

## 7. Connection to our work

**(a) Biological precedent for `attn_clamp`.** This paper is the canonical experiment our causal-perturbation method is modeled on. Salzman injected a small, graded, additive signal into a feature-selective population and read out a direction-specific shift of the decision. `attn_clamp` does the software-native version: an additive bias on the attention logits pushes the model's attention map toward (or away from) a location, and we read out the shift in the QR-DQN policy. The equivalent-signal analysis gives us the right measurement template — instead of asking "did the clamp change behavior?", we should ask "how much *stimulus* is a given clamp strength worth?" by finding the real stimulus change (e.g. added motion coherence, or a real cue) that produces the same shift in the model's choice curve. That converts a clamp magnitude into an interpretable, biology-comparable unit and is directly implementable in `motion4`.

**(b) Sensory node vs. decision node — and which layer to clamp.** Salzman perturbed **MT/V5, a sensory node** — a direction-tuned representation *upstream* of the accumulator. In our architecture that maps to the **perception layer / PRIORITY stream**, not to the value/accumulator/QR-DQN readout. This is the key experimental-design lesson: to reproduce *this* signature we should clamp the model's perception-level attention map (the priority stream that feeds the decision), not the value head. The contrasting precedents in the related set — LIP microstimulation (Hanks 2006, Ditterich 2003) perturbs a **decision/accumulator node** and predicts a different behavioral fingerprint (effects on reaction time and on the accumulation rate, not a clean sensory-evidence increment). So Salzman 1992 is our "clamp the perception layer" anchor; the LIP papers are our "clamp the accumulator" anchor. Running both clamp sites in the model and comparing to these two biological precedents is a clean, pre-registered dissociation the program can execute.

**(c) `motion4` is the RL task this is tested in.** The newly built `motion4` environment is a random-dot **motion**-direction change-detection task — the same stimulus physics Salzman used (coherent dots in noise, RF-centered aperture), lifted into our RL change-detection setting. Because `motion4` reuses the whole stack with only the pixels swapped, we can run the perception-layer `attn_clamp` inside it and compute the equivalent-signal (how much added coherence the clamp is worth) exactly as Salzman did — the tightest possible model-to-experiment mapping the program has. It also lets us check that any signature we find is about the *motion* computation and not a Gabor-orientation artifact.

**(d) A directly testable read-out prediction.** Salzman's series (with Salzman & Newsome 1994) established that when two motion signals compete, the animal's read-out of an MT perturbation is closer to **winner-take-all** than to vector-averaging of the stimulus and the injected signal. This is directly testable on our RL policy: apply an `attn_clamp` toward one location/direction *simultaneously* with a real stimulus favoring another, sweep both magnitudes, and ask whether the QR-DQN policy's choice curve follows a winner-take-all rule (the policy commits to whichever signal is momentarily stronger, with a sharp crossover) or an averaging rule (a graded blend). Reproducing winner-take-all under competing clamp-vs-stimulus in `motion4` would be a strong, non-obvious validation that the model's priority-to-policy read-out matches the primate MT read-out. If instead the model averages, that is an equally informative failure that localizes a difference in the read-out nonlinearity.

## 8. Citations to follow

- `salzman1990_mt_microstim` — the *Nature* letter this paper is the full companion to; the first report of the effect. Should be added to seed at full depth as the sibling card.
- `salzman_newsome1994_winner_take_all` — the competing-signals follow-up establishing the winner-take-all read-out prediction used in §7(d). In related set.
- `britten1992_mt_analysis` — the companion neurometric/psychometric MT paper (single-neuron sensitivity vs. behavior) from the same program; the correlational counterpart to this causal result. Not yet in seed; should be added.
- `ditterich2003_microstim_rt` — MT microstimulation with reaction-time readout; extends the additive-signal picture to the temporal/accumulation domain. In related set.
- `hanks2006_lip_microstim` — LIP microstimulation; the *decision-node* counterpart used for the sensory-vs-decision dissociation in §7(b). In related set.
- `roitman_shadlen2002_lip_rt` and `gold_shadlen2007_decision_making` — the accumulator framework that interprets what an MT-injected equivalent-signal does downstream. In related set.
- `muller2005_sc_microstim_covert` and `cavanaugh_wurtz2004_sc_change_blindness` — the SC microstimulation precedents for perceptual enhancement/change-detection; the subcortical cousins of the causal method. In related set.
