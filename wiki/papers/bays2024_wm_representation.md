---
id: bays2024_wm_representation
title: "Representation and computation in visual working memory"
authors:
  - "Bays, Paul M."
  - "Schneegans, Sebastian"
  - "Ma, Wei Ji"
  - "Brady, Timothy F."
year: 2024
venue: "Nature Human Behaviour"
doi: "10.1038/s41562-024-01871-2"
arxiv: ""
url: "https://doi.org/10.1038/s41562-024-01871-2"
tags:
  - working-memory
  - review
  - theoretical-essay
concepts:
  - working-memory-persistent-activity
  - bayesian-cue-integration
  - precision-weighting
related:
  - luck_vogel1997_wm_capacity
  - luck_vogel2013_wm_capacity_review
  - constantinidis2018_persistent_activity
  - ernst_banks2002_cue_combination
  - schneegans_bays2017_feature_binding_wm
  - feldman_friston2010_attention_free_energy
  - brady_tenenbaum2013_probabilistic_wm
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_39
status: full
depth: full
last_updated: "2026-05-16"
---

# Representation and computation in visual working memory

## 1. Abstract

The ability to *sustain internal representations* of the sensory environment beyond immediate perception is a fundamental requirement of cognitive processing. Recent debates regarding the *capacity and fidelity* of the working memory (WM) system have advanced understanding of the nature of these representations. There is growing recognition that WM representations are *not merely imperfect copies* of perceived objects: new experimental tools reveal that observers possess richer information about the *uncertainty* in their memories and take advantage of *environmental regularities* to use limited memory resources optimally. Meanwhile, computational models of visuospatial WM formulated at different levels of implementation have *converged* on common principles relating capacity to variability and uncertainty. The review covers recent research on human WM from a computational perspective, including the neural mechanisms that support it.

## 2. Why this matters for us

Bays, Schneegans, Ma & Brady 2024 is the *most current* synthesis of the computational WM-representation literature. It argues for a substantively different framework than Luck-Vogel 1997/2013: WM is a *continuous, uncertainty-encoding* representation rather than a set of discrete slots. The framework is consistent with the Bayesian-brain tradition (Jordan et al. 2023, Ernst & Banks 2002) and matches modern neural-network architectures (where memory is continuous activation vectors, not discrete slots). For the user's program, this paper supplies the contemporary framing under which PRISM's continuous-valued recurrent memory is *biologically appropriate*, not a simplification or compromise.

## 3. Key claims

1. **WM is continuous, not discrete.** Observers can store more than 4 items at lower precision, rather than 4 items at high precision with the rest dropped. The discrete-slot interpretation of Luck-Vogel 1997 is updated.
2. **WM representations carry uncertainty.** Subjects' explicit reports of uncertainty (confidence ratings) track the precision of their WM contents. This means WM doesn't just hold *what* the item was — it also holds *how confidently* the item is known.
3. **Observers use environmental regularities.** WM allocation is *informed*: prior knowledge of typical structure (typical colors, common spatial arrangements) shifts the allocation of WM precision. This is a Bayesian-brain commitment at the WM level.
4. **Computational models converge.** Despite differences in modeling style (continuous resource, mixture-of-Gaussians, neural-network models), the leading models converge on the *core principles*: capacity is linked to variability and uncertainty; precision is allocated rather than slotted; environmental priors shape allocation.
5. **Neural mechanisms.** The framework aligns with neural data: PFC population activity shows continuous precision-related signatures; the persistent-activity model and the dynamic-coding accounts both predict continuous representations.
6. **Beyond capacity to representation structure.** The 2024 review shifts the emphasis from "how many items can be stored" to "*how are items represented*" — what features, what uncertainty, what binding structure. The richer representational question is the contemporary frontier.
7. **Cross-modal extension.** The framework generalizes from visuospatial WM to other modalities (haptic, auditory) with similar Bayesian-allocation principles.

## 4. Methods

A narrative review covering recent (2014–2024) empirical and computational WM research. The authors synthesize:
- **Continuous-report psychophysics** (e.g., color-wheel reports) where subjects place a continuous estimate of remembered features.
- **Mixture-of-Gaussians modeling** (Bays-Husain-Schneegans framework) that decomposes errors into precision, guesses, and swap errors.
- **Neural-network models** (e.g., the Bouchacourt-Buschman framework) that produce continuous WM representations with precision-allocation behavior.
- **Bayesian-brain models** that frame WM allocation as expected-value-maximizing precision allocation.
- **Neural data** on PFC, parietal, and visual-cortex WM signatures.

## 5. Results

The principal empirical claims the review consolidates:

- **Continuous reports show continuous distributions.** Color-wheel and orientation-wheel reports show a Gaussian (or vM) distribution of errors around the true value, not a binary "stored vs not stored" distribution.
- **Precision decreases with set size.** As more items are held, *each item's precision decreases* — consistent with a finite resource distributed across items.
- **Uncertainty reports correlate with precision.** Subjects' explicit uncertainty reports track the actual error magnitude. WM contains explicit precision information.
- **Priors influence allocation.** When some locations or features are more probable in the environment, WM allocates more precision to those — a Bayesian-priors signature.
- **Neural model fits.** Population-level neural-network models (with recurrent dynamics and continuous activation) reproduce the continuous-report behavioral signatures better than discrete-slot models.
- **Feature-binding extension.** The Bays-Schneegans-Ma framework extends to multi-feature objects (color + orientation + position): observers store feature combinations with continuous precision per feature.

## 6. Critique / limitations

The framework is contested. Luck-Vogel-tradition adherents argue that discrete slots fit the data better when distractor filtering is properly accounted for. The discrete-vs-continuous debate is not fully resolved.

The framework's neural-level support relies on population-level decoding. Single-unit-level signatures of "continuous precision" are sparse — the population picture is more developed than the single-cell picture.

The framework's *behavioral* tests rely on continuous-report tasks. Traditional change-detection (Luck-Vogel paradigm) gives binary responses; whether the continuous-report task captures the same underlying WM or a different one is debated.

The Bayesian-priors framing is a specific theoretical commitment. Other frameworks (e.g., predictive-coding implementations of WM) would frame the prior-knowledge effects differently. The 2024 review is Bayesian-brain-tradition-aligned.

The cross-modal claim is supported by some studies but is not as rigorously tested as the visual-WM case. Generalization across modalities should be treated as a *prediction*, not a confirmed empirical fact.

## 7. Connection to our work

This paper supplies the *contemporary* framing for the user's program's WM commitments:

**PRISM's continuous recurrent memory as biologically appropriate.** PRISM v1's recurrent memory state is *continuous-valued* (network activations). Luck-Vogel-tradition discrete-slot accounts would treat this as an architectural compromise — the model has unbounded internal precision but bounded capacity at the behavioral level. Bays-Schneegans-Ma-Brady's continuous-uncertainty framework supports the architectural commitment: continuous WM is biologically realistic, not a simplification.

**Uncertainty representation in the recurrent ViT.** Bays et al. emphasize that WM contains *explicit uncertainty*. The recurrent ViT's softmax attention map can be interpreted as encoding uncertainty: high softmax probability = high precision at that location; flat distribution = high uncertainty. This is the architectural form of "WM contains uncertainty."

**Bayesian-prior allocation in the multi-hub system.** Bays et al. argue that prior knowledge shapes WM allocation. In the user's multi-hub system, each hub generates priors that bias the central self-attention substrate. The architectural mechanism — top-down Q/K projections that modulate the attention map — is the network analog of "priors shape WM allocation."

**Precision-weighting at the WM level.** The user's commitment to precision-weighted attention ([feedback_transformer](research_db/concepts/feedback_transformer.md), [feldman_friston2010_attention_free_energy](research_db/papers/feldman_friston2010_attention_free_energy.md)) is a perception-level claim. Bays et al. extend precision-weighting to WM. The unified framework — precision-weighting applies to *perception, WM, and decision* — is consistent with the user's program's framing.

**Continuous capacity vs the discrete 4-item limit.** The recurrent ViT operates with ≤4 simultaneous stimuli — within the Luck-Vogel limit. If the architecture were tested with more stimuli, the Bays-Schneegans-Ma-Brady prediction would be *graceful degradation* (lower precision per item) rather than a hard cutoff (some items dropped entirely). Testing this is a natural follow-up experiment.

The recurrent ViT paper cites Bays et al. 2024 in its bibliography (ref [39]). Future manuscripts that engage with WM should cite the contemporary Bays framework alongside Luck-Vogel for full coverage of the literature.

## 8. Citations to follow

- `luck_vogel2013_wm_capacity_review` — companion / counterpoint. In seed, full depth.
- `luck_vogel1997_wm_capacity` — founding capacity paper. In seed, full depth.
- `constantinidis2018_persistent_activity` — WM persistent activity. In seed, full depth.
- `ernst_banks2002_cue_combination` — Bayesian cue integration. In seed, full depth.
- `schneegans_bays2017_feature_binding_wm` — feature binding in continuous WM. In seed.
- `bays_husain2008_dynamic_shifts_visual_wm` — Bays continuous-resource foundational paper. Not in seed.
- `ma_husain_bays2014_changing_concepts_wm` — Ma et al. review. Not in seed.
- `brady_tenenbaum2013_probabilistic_wm` — probabilistic WM model. In seed.
- `bouchacourt_buschman2019_population_wm` — neural-network model of WM. Not in seed.
