---
id: clark2013_whatever_next
title: "Whatever next? Predictive brains, situated agents, and the future of cognitive science"
authors:
  - "Clark, Andy"
year: 2013
venue: "Behavioral and Brain Sciences"
doi: "10.1017/S0140525X12000477"
arxiv: ""
url: "https://doi.org/10.1017/S0140525X12000477"
tags:
  - predictive-coding
  - review
  - theoretical-essay
concepts:
  - hierarchical-predictive-coding
  - active-inference
  - top-down-feedback
  - precision-weighting
  - embodied-cognition
related:
  - rao_ballard1999_predictive_coding
  - friston2010_fep_unified_theory
  - friston2005_cortical_responses
  - keller_mrsic_flogel2018_pc_review
  - pezzulo_parr_friston2024_active_inference
  - aitchison_lengyel2017_pc_bayesian
  - desimone_duncan1995_biased_competition
  - spratling2008_pc_biased_competition
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# Whatever next? Predictive brains, situated agents, and the future of cognitive science

## 1. Abstract

Brains, Clark argues, are essentially prediction machines: bundles of cells that support perception and action by constantly attempting to match incoming sensory inputs with top-down expectations or predictions. This is achieved using a hierarchical generative model that minimizes prediction error within a bidirectional cascade of cortical processing. Such accounts offer a unifying model of perception and action, illuminate the functional role of attention, and may capture the special contribution of cortical processing to adaptive success. The target article critically examines this "hierarchical prediction machine" approach and concludes that it offers the best clue yet to the shape of a unified science of mind and action. The paper lays out the key elements and implications of the approach, explores pitfalls and challenges (evidential, methodological, conceptual), and considers how the framework impacts the broader vision of mind, experience, and agency.

## 2. Why this matters for us

Clark 2013 is the *philosophical* synthesis of the predictive-coding / hierarchical-prediction-machine framework that PRISM v1 and v2 inherit. The paper is the most cited single reference for the "the cortex is a prediction machine" framing, and is the primary source for adopting *predictive processing* (as Clark calls it) as the unifying theoretical commitment of the user's program. Where Rao-Ballard 1999 ([rao_ballard1999_predictive_coding](research_db/papers/rao_ballard1999_predictive_coding.md)) gives the architecture and Friston 2010 ([friston2010_fep_unified_theory](research_db/papers/friston2010_fep_unified_theory.md)) gives the variational framework, Clark 2013 gives the philosophical / cognitive-science framing that makes the framework speak to the cross-disciplinary audience the user's manuscripts will need to reach.

## 3. Key claims

1. **The brain is a prediction machine.** All cortical processing — perception, action, attention, learning — can be understood as variants of one underlying computation: minimizing prediction error within a hierarchical generative model.
2. **Bidirectional cascade.** Top-down predictions flow from higher cortical areas to lower; bottom-up prediction errors flow from lower to higher. The cascade is *bidirectional and continuous*, not feedforward-then-feedback.
3. **Action and perception are unified.** Action minimizes prediction error by changing the world to match prediction; perception minimizes prediction error by changing prediction to match the world. The duality is the foundation of *active inference*.
4. **Attention is precision-weighting.** Attention is the modulation of the gain of prediction-error pathways, prioritizing some sensory channels over others. This is a substantive theoretical commitment — attention is *not* a separate cognitive process but an aspect of the unified predictive machinery.
5. **The framework challenges traditional cognitive science.** Predictive processing is incompatible with sense-think-act pipelines, modular architectures with fixed processing stages, and many traditional cognitive-architecture commitments. The "situated agent" framing emphasizes that the brain is continuously engaged with its environment via active inference.
6. **Implications for consciousness.** Conscious experience may be the *content* of the brain's best current prediction — what it expects the world to be. This is a substantive philosophical claim with empirical consequences.
7. **The framework is empirically grounded.** Specific empirical phenomena (perceptual illusions, expectation suppression, attention effects, mismatch negativity) are reproduced by predictive-processing models. The framework is not just a philosophical proposal — it's empirically engaged.

## 4. Methods

A target article in *Behavioral and Brain Sciences* — Clark's primary review is followed by open peer commentary from many other researchers. The paper itself is a *philosophical / theoretical review*, synthesizing predictive-coding work from Rao & Ballard, Friston, Hohwy, Lupyan, and others into a unified framework. No new empirical data; the contribution is the conceptual synthesis and the *positioning* of predictive processing as the leading unified theory.

The paper's structure:
- Sections 1–2: lay out the predictive-processing framework, its empirical grounding, and its theoretical machinery.
- Section 3: identifies pitfalls — empirical challenges (does the framework genuinely predict the data?), methodological challenges (how do we test such a general framework?), conceptual challenges (does it overfit or rule out alternatives?).
- Sections 4–5: extend the framework to broader cognitive-science questions — embodied / situated cognition, consciousness, agency.

## 5. Results

The principal claims the review makes:

- **Hierarchical predictive coding is the unifying framework.** Cortex implements a hierarchical generative model with descending predictions, ascending errors, and precision-weighted gain modulation.
- **Attention falls out naturally.** Selective attention is precision-weighting of prediction-error channels. The framework therefore unifies attention with perception, rather than treating it as a separate mechanism.
- **Action falls out naturally too.** Active inference unifies action and perception: action minimizes prediction error by changing the world; perception minimizes it by changing predictions. The two are dual aspects of the same minimization.
- **Empirical grounding.** The framework predicts and explains specific phenomena: extra-classical receptive-field effects (Rao-Ballard 1999), expectation suppression, mismatch negativity, perceptual illusions, attention effects, and disorders of psychopathology.
- **Compatibility with embodied cognition.** The "situated agent" framing of predictive processing is compatible with embodied / enactive cognitive science. The brain doesn't compute in isolation; it predicts an environment it is actively engaged with.
- **Limitations.** Clark identifies several open questions: the framework's specificity (does it predict anything that other frameworks don't?), its mathematical assumptions (Gaussian priors and likelihoods), its scaling (do deep predictive-coding networks compete with deep supervised networks?), and its relation to consciousness (does the framework genuinely explain phenomenal experience?).

## 6. Critique / limitations

The paper is a *philosophical synthesis*, not an empirical demonstration. Its claims rest on the empirical work it cites. The framework's empirical adequacy is therefore inherited from underlying papers; Clark argues for the unification but doesn't perform new empirical tests.

The framework is *very general*. Almost any cognitive phenomenon can be cast in predictive-processing terms. This generality is both a strength (unification) and a weakness (the framework risks being unfalsifiable). Specific subsidiary theories must be added to derive testable predictions.

The mathematical machinery is *referenced rather than derived*. Readers without background in variational inference may find the framework persuasive without fully appreciating its mathematical commitments. The Friston tradition's specific choices (Gaussian likelihoods, mean-field inference) are not unique; the conceptual framework would survive different mathematical choices, but the empirical predictions might not.

The relationship to *biased competition* (Desimone & Duncan 1995, [desimone_duncan1995_biased_competition](research_db/papers/desimone_duncan1995_biased_competition.md)) is acknowledged but not deeply analyzed. Predictive processing and biased competition are mathematically reconcilable (Spratling 2008, [spratling2008_pc_biased_competition](research_db/papers/spratling2008_pc_biased_competition.md)), but the philosophical framing as "the brain is a prediction machine" may oversimplify the rich biological substrate.

Clark's *philosophical* framing — predictive processing as the unifying theory of mind — has been criticized as overclaiming. Even researchers sympathetic to the framework have argued that not all cognitive phenomena are well-captured by the framework, and that other principles (e.g., reward-driven learning, social cognition) may not reduce cleanly to prediction error.

The framework is *cortex-centric*. The brain's many subcortical structures (basal ganglia, thalamus, cerebellum, brainstem) are not centrally addressed. The user's program, which includes RL hub modeling the cortico-basal-ganglia-thalamic loop ([cortico_basal_ganglia_thalamic_loops](research_db/concepts/cortico_basal_ganglia_thalamic_loops.md)), is more inclusive than Clark's cortex-focused framing.

## 7. Connection to our work

Clark 2013 is the canonical philosophical reference for the predictive-processing framing the user's program adopts:

**The unifying theoretical framing for PRISM and the recurrent ViT.** PRISM v1 and v2 are predictive-coding architectures; the recurrent ViT can be interpreted as a precision-weighted attention machine. Clark 2013 provides the unifying theoretical commitment — "the brain is a prediction machine" — that makes these architectures coherent as a single research program rather than three separate models.

**Attention as precision-weighting.** Clark's framing of attention as precision-weighting of prediction-error channels is the philosophical version of the user's commitment to multiplicative attention modulation ([feedback_transformer](research_db/concepts/feedback_transformer.md)). The Feedback Transformer's Hadamard-product structure is the architectural form of "attention modulates the gain of prediction-error channels."

**Active inference unifying perception and action.** PRISM v1 trains a generative decoder (perception side) and an actor-critic (action side). The unification of the two under predictive processing is a Clark / Friston framing; PRISM's variational free-energy objective ([Prism/docs/THESIS.md](Prism/docs/THESIS.md) §2.11) is the technical instantiation.

**The situated-agent commitment.** The user's program treats the recurrent ViT and PRISM as *agents in dynamic environments*, not as static classifiers. Clark's "situated agents" framing is the philosophical support for this architectural choice.

**The competition-emergent-PC reframing.** Clark presents predictive processing as the unifying theory; the user's coalition-competition thesis ([coalition_resource_competition](research_db/concepts/coalition_resource_competition.md)) is an *extension* of Clark's framing — top-down predictions are predictions of *competing coalitions*, not of sensory input. This is a meaningful contribution to the Clark / Friston line: the framework can be extended to non-sensory cortical regions by reinterpreting the "predicted" target.

The recurrent ViT paper cites Clark 2013 implicitly via the broader predictive-coding tradition. Any manuscript that positions PRISM or the multi-hub system as a predictive-processing architecture should cite Clark 2013 as the philosophical synthesis.

## 8. Citations to follow

- `friston2010_fep_unified_theory` — variational free-energy framework. In seed, full depth.
- `friston2005_cortical_responses` — earlier Friston theory of cortex. In seed, full depth.
- `rao_ballard1999_predictive_coding` — Rao-Ballard foundation. In seed, full depth.
- `keller_mrsic_flogel2018_pc_review` — empirical review. In seed, full depth.
- `pezzulo_parr_friston2024_active_inference` — modern active-inference review. In seed, full depth.
- `aitchison_lengyel2017_pc_bayesian` — formal PC-vs-Bayesian distinction. In seed, full depth.
- `hohwy2013_predictive_mind` — Hohwy's parallel philosophical synthesis. Not in seed.
- `clark2016_surfing_uncertainty` — Clark's book-length elaboration. Not in seed.
