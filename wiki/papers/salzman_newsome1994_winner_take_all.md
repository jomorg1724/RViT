---
id: salzman_newsome1994_winner_take_all
title: "Neural mechanisms for forming a perceptual decision"
authors:
  - "Salzman, C. Daniel"
  - "Newsome, William T."
year: 1994
venue: "Science"
doi: "10.1126/science.8146653"
arxiv: ""
url: "https://doi.org/10.1126/science.8146653"
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
  - salzman1992_mt_microstim_methods
  - cavanaugh_wurtz2004_sc_change_blindness
  - ditterich2003_microstim_rt
  - gold_shadlen2007_decision_making
  - roitman_shadlen2002_lip_rt
  - hanks2006_lip_microstim
  - treue_martinez_trujillo1999_feature_attention
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - pubmed
status: summary
depth: full
last_updated: "2026-07-04"
---

# Neural mechanisms for forming a perceptual decision

## 1. Abstract

Salzman & Newsome asked how the brain reads out a population of direction-selective neurons in middle temporal area (MT/V5) to form a single perceptual decision about motion direction. Building on earlier demonstrations that microstimulation of MT direction columns biases a two-alternative motion judgement, they moved to an eight-alternative direction-discrimination task and placed a *visual* motion signal in direct competition with an *electrically introduced* directional signal delivered to an MT column tuned to a different direction. The critical question was how the two co-existing directional signals combine. If the read-out mechanism averaged the population activity, the monkey's reported direction should shift toward an intermediate, vector-averaged direction lying between the visual and stimulated directions. Instead, the animals' choices favored *one signal or the other* — the visual direction or the stimulated direction — but not their average, and the two influences behaved independently. This pattern implies a **winner-take-all** read-out of the MT direction representation rather than vector averaging: the decision process selects a single interpretation from the competing directional signals rather than blending them. The result is a landmark constraint on how sensory population codes are converted into categorical perceptual decisions.

## 2. Why this matters for us

Our program builds small recurrent vision-transformers (conv front-end -> recurrent-ViT self-attention with feedback -> spatial xLSTM working memory -> distributional QR-DQN actor-critic) trained by RL to reproduce primate visual-attention signatures, and it uses an **attn_clamp** additive bias on attention logits as an in-silico analog of microstimulation. This paper is the biological precedent that turns that analog from a stylistic choice into a testable hypothesis about *read-out geometry*. Salzman & Newsome show that when you inject an artificial directional signal into a sensory population (MT) while a real visual signal is present, the animal does not report the average of the two — it reports one or the other. That is a claim about how downstream circuitry *combines competing signals*: winner-take-all selection, not vector averaging.

For us this is directly instrumented. When we apply an attn_clamp that pushes the PRIORITY stream toward a location or feature that competes with the genuine stimulus, the network's policy readout can either (a) blend — producing intermediate, graded choices along the axis between clamped and true directions — or (b) select — snapping to one or the other. Salzman & Newsome predict (b), and our QR-DQN policy over the discrete action set gives us a clean way to measure which regime the model is in: we read the argmax action distribution as a function of clamp strength and ask whether it passes through intermediate directions (averaging) or stays bimodal (winner-take-all). The paper also cleanly separates the PRIORITY interpretation (which signal wins the decision) from any VALUE bookkeeping, because the manipulation is purely on the sensory-direction evidence and the read-out is categorical — the same PRIORITY-drives-the-decision logic our two-stream framing rests on.

## 3. Key claims

1. **Eight-alternative direction discrimination.** Moving from the original 2AFC microstimulation paradigm to an eight-direction task gives enough angular resolution to distinguish *averaging* (intermediate reported directions) from *selection* (only the component directions) — the whole logic of the experiment depends on this richer choice set.
2. **Two competing directional signals.** A coherent visual motion signal in one direction is presented simultaneously with electrical microstimulation of an MT column tuned to a *different* direction, deliberately pitting a natural signal against an artificial one inside the same population code.
3. **Choices favor one signal or the other, not the average.** The reported direction clusters at the visual direction or the stimulated direction; it does *not* systematically shift to the vector-averaged direction between them. This is the central finding.
4. **The two influences are independent.** The effect of microstimulation and the effect of the visual signal combine independently rather than summing into a single blended vector — consistent with a competitive selection stage rather than a linear pooling stage.
5. **Winner-take-all read-out.** The data are best explained by a winner-take-all mechanism reading out the MT direction representation: downstream circuitry selects a single winning direction from the population rather than computing its centroid.
6. **MT activity is causally sufficient to enter the decision.** As in the 1990/1992 work, the stimulated signal is not merely correlated with choice — injecting it changes the decision, establishing MT as a causal node whose read-out geometry constrains perception.

## 4. Methods

- **Subjects and task.** Rhesus monkeys trained on a random-dot motion display performed an *eight-alternative* direction-discrimination task, reporting the perceived global direction of motion (typically with an eye movement to one of eight targets), a substantial extension of the earlier two-alternative design.
- **Stimuli.** Dynamic random-dot kinematograms with a controllable fraction of coherently moving dots set the strength and direction of the *visual* motion signal; coherence set the reliability of the natural evidence.
- **Microstimulation.** Low-current electrical microstimulation was delivered through the recording electrode to a physiologically characterized MT column whose neurons shared a common preferred direction, introducing an *artificial* directional signal at a direction chosen to differ from the visual direction (see companion methods paper salzman1992_mt_microstim_methods).
- **Competition design.** On stimulated trials the visual direction and the stimulated (preferred) direction were placed in competition; the angular separation between them was chosen so that a vector-average outcome would fall on a *distinct* intermediate direction, cleanly separable from either component.
- **Read-out analysis.** The distribution of reported directions was examined for whether stimulation shifted reports toward the intermediate (averaged) direction or toward the discrete stimulated direction, and whether the visual and electrical influences acted additively/independently or as a single blended vector — the discriminating test between averaging and winner-take-all.

## 5. Results

- **Reports cluster at the component directions.** Across the competition conditions, the animals' choices concentrated at the visual direction or at the stimulated direction, with little systematic mass at the intermediate vector-averaged direction — the signature of selection rather than blending.
- **Microstimulation shifts choices toward the stimulated direction.** As in the earlier 2AFC work, injecting the artificial signal reliably biased perceptual reports toward the stimulated column's preferred direction, confirming causal entry of the stimulated signal into the decision.
- **Independence of the two signals.** The visual influence and the electrical influence combined independently; the outcome was not a single averaged vector whose angle tracked the relative strengths of the two signals.
- **Winner-take-all is the parsimonious account.** The combination of "reports at the components, not the mean" plus "independent influences" is naturally explained by a winner-take-all read-out that selects one direction from the MT population, and is not predicted by a vector-averaging read-out.
- **Constraint on decoding models.** The result places a strong constraint on population-decoding theories of MT: the mapping from population activity to perceptual report is competitive/selective at the relevant stage, not a graded centroid computation.

## 6. Critique / limitations

- **Read-out mechanism is inferred, not observed.** Winner-take-all is inferred from behavioral choice geometry; the paper does not record the downstream circuit implementing the selection, so alternative decoders that mimic winner-take-all behavior at the reported angular separations are not fully excluded.
- **Regime may depend on separation and reliability.** The averaging-vs-selection dichotomy can be a function of the angular separation between competing directions and the relative reliability of the two signals; at small separations or matched strengths a partially graded (averaging-like) regime can appear, so "winner-take-all" is best read as the dominant regime in the tested parameter range rather than an absolute rule.
- **Artificial signal geometry.** Microstimulation activates a spatially restricted set of columns and may not faithfully mimic the distributed population a natural motion signal evokes; the injected "direction" is an idealization of what MT normally represents.
- **Single area, single feature.** The claim is specific to MT and to motion direction; whether the same winner-take-all read-out governs other feature dimensions or higher decision areas is left open (subsequent LIP microstimulation work — hanks2006_lip_microstim — addresses the accumulator side).
- **Static, near-threshold framing.** The design targets the direction of the final report; it says less about the *dynamics* of how the winner emerges over time, which later reaction-time microstimulation work (ditterich2003_microstim_rt) began to probe.

## 7. Connection to our work

**(a) Biological precedent for attn_clamp.** This is a purest-form instance of the microstimulation logic our attn_clamp perturbation imitates: an artificial signal is injected into a sensory population and its causal effect on choice is read off behavior. Where Salzman & Newsome inject current into an MT direction column, we add a bias to the attention logits (attn_clamp) to inject an artificial spatial/feature signal into the PRIORITY stream, then read the effect on the QR-DQN policy. The paper licenses attn_clamp as an *evidence-injection* manipulation, not merely an attention nudge.

**(b) Sensory node, not decision node.** Crucially, the electrode is in **MT/V5 — a sensory representation of motion**, not in LIP or an accumulator. In our architecture MT maps onto the **perception layer** (conv front-end + recurrent-ViT feature representation feeding the PRIORITY stream), *not* the VALUE/accumulator/QR-DQN read-out. So the model-side homolog of this experiment is an attn_clamp (or a feature-level additive bias) applied at the *perceptual/priority* stage — clamping which motion direction the network's early representation emphasizes — and then observing whether the downstream policy selects or averages. Contrast this with LIP-microstimulation papers (hanks2006_lip_microstim), which map onto perturbing the model's accumulator/QR-DQN value read-out; keeping this sensory-vs-decision distinction straight is exactly what lets us assign each biological perturbation to the correct layer of our network.

**(c) The RL task where this is tested: motion4.** We now have a **motion4** battery environment — random-dot MOTION-direction change-detection, a Cavanaugh & Wurtz 2004 analog that reuses the entire architecture with only the pixels swapped (moving-dot fields instead of Gabors). motion4 is the natural home for reproducing Salzman & Newsome: it presents genuine coherent motion the network must read out, and its dot-field stimulus is the direct in-silico counterpart of the random-dot kinematogram. To run the competition experiment we clamp the PRIORITY stream toward a direction that differs from the displayed coherent direction and sweep clamp strength and angular separation, exactly mirroring the visual-vs-electrical competition.

**(d) A directly testable read-out prediction.** Salzman & Newsome make a sharp, falsifiable prediction for motion4: as the clamped direction is pitted against the true direction, the **policy should select one or the other, not their average**. Because the QR-DQN policy is a distribution over a discrete action set, we can measure this cleanly — plot the argmax (and full action) distribution against angular separation between clamped and true directions. Winner-take-all predicts a *bimodal* distribution collapsing onto the two component directions with a switch as clamp strength crosses the visual reliability; vector-averaging predicts a *unimodal* distribution that migrates smoothly through the intermediate directions. This is a rare case where a 1994 electrophysiology result yields a concrete pass/fail test on our trained RL agent's policy geometry, and it doubles as a probe of whether our read-out is genuinely competitive (as primate MT read-out appears to be) or merely a linear pooler.

## 8. Citations to follow

- Salzman, Britten & Newsome (1990), *Nature* — original MT microstimulation biases 2AFC motion judgements (salzman1990_mt_microstim); the direct predecessor establishing causal MT influence on choice.
- Salzman, Murasugi, Britten & Newsome (1992), *J. Neurosci.* — full microstimulation methods and the systematic 2AFC characterization (salzman1992_mt_microstim_methods).
- Ditterich, Mazurek & Shadlen (2003), *Nat. Neurosci.* — MT microstimulation effects on reaction times, adding the temporal dynamics this study leaves implicit (ditterich2003_microstim_rt).
- Hanks, Ditterich & Shadlen (2006), *Nat. Neurosci.* — LIP microstimulation biasing the *decision/accumulator* stage, the decision-node counterpart to this sensory-node result (hanks2006_lip_microstim).
- Gold & Shadlen (2007), *Annu. Rev. Neurosci.* — synthesis of the MT->LIP evidence-accumulation framework in which winner-take-all read-out is embedded (gold_shadlen2007_decision_making).
- Roitman & Shadlen (2002), *J. Neurosci.* — LIP ramping during motion discrimination, the accumulator dynamics downstream of the MT read-out characterized here (roitman_shadlen2002_lip_rt).
- Cavanaugh & Wurtz (2004), *J. Neurosci.* — the change-detection microstimulation paradigm our motion4 environment is modeled on (cavanaugh_wurtz2004_sc_change_blindness).
- Treue & Martínez-Trujillo (1999), *Nature* — feature-based attention scaling of MT direction responses, relevant to how a clamped feature signal would modulate the same population (treue_martinez_trujillo1999_feature_attention).
