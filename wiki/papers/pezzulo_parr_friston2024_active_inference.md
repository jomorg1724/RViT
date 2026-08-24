---
id: pezzulo_parr_friston2024_active_inference
title: "Active inference as a theory of sentient behavior"
authors:
  - "Pezzulo, Giovanni"
  - "Parr, Thomas"
  - "Friston, Karl"
year: 2024
venue: "Biological Psychology"
doi: "10.1016/j.biopsycho.2023.108741"
arxiv: ""
url: "https://doi.org/10.1016/j.biopsycho.2023.108741"
tags:
  - free-energy-principle
  - predictive-coding
  - review
  - theoretical-essay
concepts:
  - active-inference
  - variational-free-energy
  - hierarchical-predictive-coding
  - precision-weighting
related:
  - friston2010_fep_unified_theory
  - feldman_friston2010_attention_free_energy
  - keller_mrsic_flogel2018_pc_review
  - rao_ballard1999_predictive_coding
  - bastos2012_canonical_microcircuits
  - clark2013_whatever_next
  - schmidhuber2015_learn_to_think
  - spratling2008_pc_biased_competition
  - mazzaglia2022_fep_deep_learning
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - programmatic_pubmed
status: full
depth: full
last_updated: "2026-05-16"
---

# Active inference as a theory of sentient behavior

## 1. Abstract

This review traces the history and future of *active inference* — a unifying perspective on action and perception based on the idea that sentient behavior depends on implicit use of internal models to predict, infer, and direct action. The review traces the evolution from Helmholtzian *unconscious inference* through predictive-coding accounts of cortical function to the contemporary active-inference framework. The development includes the formulation of predictive-coding models and related theories of neuronal message passing, sequential models for planning and policy optimization, and the importance of *hierarchical (temporally deep)* internal generative models. Active inference has been used to account for aspects of anatomy and neurophysiology, to offer theories of psychopathology in terms of *aberrant precision control*, and to unify extant psychological theories. The authors anticipate further development in biology, robotics, machine learning, and AI.

## 2. Why this matters for us

Pezzulo, Parr & Friston 2024 is the *contemporary canonical* review of active inference — the unification of perception, action, and learning under the free-energy principle. It supersedes earlier active-inference reviews (Friston 2010, Friston, Daunizeau & Kiebel 2009, Parr & Friston 2019) by adding the past decade of empirical findings and the contemporary deep-learning connections. For the user's program, this paper is the primary reference for the variational-free-energy framework that PRISM's inner inference loop ([Prism/docs/THESIS.md](Prism/docs/THESIS.md) §2.11) is built on. Any manuscript that situates PRISM in the active-inference tradition should cite this paper rather than the older Friston 2010 alone.

## 3. Key claims

1. Sentient behavior arises from the brain's implicit use of *internal generative models* to predict, infer, and direct action. This is the unifying principle of active inference.
2. The framework subsumes Helmholtzian unconscious inference, Rao-Ballard predictive coding, Friston's variational-free-energy framework, and modern temporally-deep planning models into a single unified theory.
3. **Action and perception are dual.** Perception minimizes free energy by updating internal beliefs to match sensory data; action minimizes free energy by *changing sensory data* to match internal beliefs. The two are mathematically equivalent under the variational framework.
4. **Hierarchical temporally-deep models.** The brain's internal model is hierarchical (multiple cortical levels with descending predictions and ascending errors) *and* temporally deep (each level operates at a different timescale, with deeper levels predicting longer-range structure). The temporal-depth aspect is the contemporary extension over Rao-Ballard.
5. **Precision control is central.** The framework's empirical successes — modeling attention, psychopathology, mismatch responses — turn critically on *precision weighting* of prediction errors. Psychopathologies (schizophrenia, autism, depression) are framed as *aberrant precision control* rather than discrete deficits.
6. **Active inference unifies cognitive psychology.** Multiple distinct psychological theories (attention, motor control, decision-making, learning, social cognition) can be re-cast in active-inference terms with the same underlying variational machinery. The framework therefore acts as a *unification* rather than a single-domain theory.
7. **AI applications.** Active inference is increasingly being applied to robotics, machine learning, and AI agents — particularly for sample-efficient learning, hierarchical planning, and curiosity-driven exploration.

## 4. Methods

A *historical and synthetic review*. The paper traces the conceptual evolution from Helmholtz's unconscious inference (mid-19th-century philosophy of perception) through Bayesian-brain proposals, Rao-Ballard predictive coding (1999), Friston's variational free-energy principle (2005, 2010), to contemporary active inference. The contribution is the *synthesis* and the situation of the framework in current empirical and applied contexts.

The paper does not present new experimental data. Its empirical engagement is through the literature it consolidates: Keller-Mrsic-Flogel-style mouse-V1 mismatch experiments, Bastos canonical-microcircuit primate data, psychopathology phenotyping work, and AI applications.

The mathematical structure of active inference is summarized at the level of *generative models* (the brain's internal model of the world), *recognition models* (the inference of states from observations), the *variational free energy* objective ($\mathcal{F} = \langle \log q - \log p \rangle$), and *expected free energy* (the active-inference action-selection objective). The technical machinery is referenced rather than derived in detail.

## 5. Results

The principal claims and unifications the review consolidates:

- **Perception as inference.** The Helmholtzian / Bayesian / Rao-Ballard view that perception is best understood as inferring latent causes from sensory data is fully formalized in variational terms.
- **Predictive coding as a special case.** Rao-Ballard's predictive-coding architecture is one specific implementation of the more general variational framework. The Bastos canonical-microcircuit framework gives the cortical implementation; the cellular substrate is Larkum's BAC mechanism plus Jordan-style Bayesian dendrites.
- **Action as inference.** Selecting actions to minimize expected free energy gives a unified theory of decision-making that subsumes utility-maximization, exploration-exploitation trade-offs, and curiosity-driven learning. Active inference is therefore a complete theory of behavior, not just perception.
- **Precision and attention.** Attention is the inference of precision (Feldman & Friston 2010). The cellular substrate is neuromodulator-controlled gain and SST+/VIP+ inhibitory gating.
- **Psychopathology as aberrant precision.** Schizophrenia (over-precise priors), autism (under-precise priors / over-precise sensations), depression (high precision on negative priors), and several other conditions are all framed as miscalibrated precision parameters. This is a substantive empirical claim with consistent empirical support but requires further validation.
- **AI translation.** Active-inference agents for robotics, motor control, sample-efficient RL, and curiosity-driven exploration have been demonstrated. The framework is empirically active in current AI research.

## 6. Critique / limitations

The framework is *very general*. Almost any cognitive phenomenon can be cast in active-inference terms; this generality is a strength (unification) but also a weakness (the framework risks being unfalsifiable in practice). Specific subsidiary theories (e.g., what the precision parameters in a given task are) must be added to derive testable predictions.

The framework's *neuro-biological commitments* are still being worked out. The canonical-microcircuit mapping (Bastos 2012) and the cellular substrate (Larkum BAC, Jordan dendritic Bayes) are candidate implementations but are not uniquely supported by current data.

The framework's *AI applications* are still nascent. Active-inference agents perform well on small toy tasks; scaling to competitive performance on standard benchmarks (Atari, Control Suite) is an open research direction. Whether active inference can match or exceed Dreamer-class model-based RL at scale is unsettled.

The free-energy framework is *mathematically deep* but also has many degrees of freedom (which generative model? which prior? which inference algorithm?). Specific choices have substantial empirical consequences; the abstract framework itself doesn't pin them down.

The psychopathology applications are correlational. The "aberrant precision" framing is consistent with the symptomatology but is not yet a clinically actionable diagnostic. Pharmacological interventions based on the framework (boosting or reducing precision in specific channels) are speculative.

The review is *Friston-tradition-aligned*. Alternative frameworks — Spratling-style biased-competition without explicit free energy ([spratling2008_pc_biased_competition](research_db/papers/spratling2008_pc_biased_competition.md)), Keller-Mrsic-Flogel-style simpler predictive-processing accounts ([keller_mrsic_flogel2018_pc_review](research_db/papers/keller_mrsic_flogel2018_pc_review.md)) — are referenced but not engaged with critically. The review presents active inference as the mature framework; critics might argue that some of the unification is rhetorical.

## 7. Connection to our work

This paper is the canonical contemporary reference for several of the user's architectural commitments:

**Variational free energy as PRISM's inner-loop objective.** PRISM v1's variational free-energy auxiliary loss ([Prism/docs/THESIS.md](Prism/docs/THESIS.md) §2.11) is grounded in the active-inference framework Pezzulo-Parr-Friston review. The recurrent ViT and PRISM v1 both implicitly assume the active-inference framework; this paper is the modern citation for it.

**Precision-weighting as attention.** The Feedback Transformer's multiplicative structure ([feedback_transformer](research_db/concepts/feedback_transformer.md)) and PRISM's saliency-gated update both implement precision-weighting. Pezzulo-Parr-Friston supplies the unified theoretical framework in which precision-weighting plays a central role (attention, action-selection, and learning are all unified by it).

**Hierarchical temporally-deep models.** The user's program commits to a hierarchical multi-compartmental memory ([multi_compartmental_memory](research_db/concepts/multi_compartmental_memory.md)) with multiple timescales. Pezzulo-Parr-Friston's emphasis on temporally-deep hierarchical generative models is the matching theoretical commitment. Specifically, the slow-fast recurrence ([slow_fast_recurrence](research_db/concepts/slow_fast_recurrence.md)) the user adopts is the architectural form of the temporally-deep generative model the active-inference framework calls for.

**Unification of perception, action, learning.** The user's multi-hub multi-objective system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) trains hubs on different objectives (perception in MSI; action in RL; reconstruction in VAE). Active inference says these are all *the same* objective at different levels (variational free energy). The user's multi-hub architecture is therefore a *modular* implementation of the unified active-inference principle — separate hubs implementing different aspects of the same overall free-energy minimization.

**Curiosity-driven exploration.** Schmidhuber 2015's "learning to think" framework ([schmidhuber2015_learn_to_think](research_db/papers/schmidhuber2015_learn_to_think.md)) and active inference both motivate curiosity-driven exploration. The user's program's MSI hub could be trained on a curiosity / mutual-information objective in this tradition. Pezzulo-Parr-Friston is the unifying reference.

The recurrent ViT paper cites Friston 2010 in the predictive-coding context (refs [91]-[95]). Future manuscripts should cite Pezzulo-Parr-Friston 2024 as the modern canonical reference for active inference, situating the user's architectural commitments in the contemporary framework.

## 8. Citations to follow

- `friston2010_fep_unified_theory` — the foundational FEP paper. In seed, full depth.
- `feldman_friston2010_attention_free_energy` — attention-as-precision-weighting. In seed, full depth.
- `parr_friston2019_active_inference_review` — earlier active-inference review. Not in seed.
- `friston2017_active_inference_curiosity` — Friston's papers on active inference and curiosity. Not in seed.
- `da_costa2020_active_inference_discrete` — discrete-state active inference. Not in seed.
- `tschantz2020_active_inference_continuous` — continuous-state active inference. Not in seed.
- `mazzaglia2022_fep_deep_learning` — FEP for deep learning. In seed.
- `clark2013_whatever_next` — philosophical predictive-processing review. In seed.
- `hohwy2013_predictive_mind` — Hohwy's philosophical synthesis. Not in seed.
