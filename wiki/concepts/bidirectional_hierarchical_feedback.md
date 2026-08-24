---
id: bidirectional_hierarchical_feedback
type: concept
title: "Bidirectional hierarchical feedback"
papers:
  - rao_ballard1999_predictive_coding
  - bastos2012_canonical_microcircuits
  - felleman_vanessen1991_hierarchical_cortex
  - dicarlo2012_object_recognition
  - kietzmann2019_recurrence_required
  - miconi_vanrullen2016_feedback_attention
  - reynolds_chelazzi2004_attentional_modulation
  - friston2010_fep_unified_theory
  - manns_eichenbaum2006_lec_mec
source_documents:
  - "Private & Shared-4/Evolution of Architecture (§ Hierarchical Visual Processing in the Cortex, § Descending Projections, § Ascending Projections, § Rationale For Diminishing Feedback Inputs)"
last_updated: "2026-05-18"
---

# Bidirectional hierarchical feedback

## Definition

The architectural commitment that every memory layer in a multi-compartmental memory stack receives feedback from *every* other layer — both higher (top-down predictions) and lower (bottom-up errors) — and that this feedback flows through shape-matching conv operations: descending feedback uses spatially-reducing, channel-expanding conv stacks; ascending feedback uses spatially-expanding (conv-transpose) operations.

Formally, for a stack of memory states $\{C^{(1)}, C^{(2)}, C^{(3)}\}$ with $n_{gh}^{(1)} > n_{gh}^{(2)} > n_{gh}^{(3)}$, the feedback inputs to layer $i$ are:

- **Layer 1 (V1-analog)**: receives feedback from $C^{(1)}, C^{(2)}_{\uparrow 1}, C^{(3)}_{\uparrow\uparrow 1}$ — all layers, with deeper layers up-projected via conv-transpose to layer-1 spatial resolution.
- **Layer 2 (V2-analog)**: receives feedback from $C^{(2)}, C^{(3)}_{\uparrow 2}$ — itself plus the next-deeper layer up-projected one step.
- **Layer 3 (V4/IT-analog)**: receives feedback from $C^{(3)}$ only — no ascending feedback, since there is nothing deeper.

## The deliberate asymmetry

Deeper layers receive *fewer* feedback inputs. The user motivates this design (Evolution of Architecture, §"Rationale For Diminishing Feedback Inputs Into Deeper Layers") with three connected claims:

1. **Representation stability.** Layers with many feedback inputs are subject to more frequent perturbations from competing rivals — their representations are less stable. Deep layers with fewer inputs can maintain more stable, more abstracted representations. This is the same logical move that the Hierarchical Reasoning Model (Wang et al. 2025, arXiv:2506.21734) makes with its "high-level" module running on a slower timescale than its "low-level" module.

2. **Power asymmetry creating an incentive for cooperation.** Because deeper layers feed back into every shallower layer but receive feedback from fewer sources themselves, they have a structural advantage in the competition for representational dominance. Shallower layers are pushed to "play nice" with deeper layers' top-down predictions — otherwise the deeper layer can simply persist with its own representation. This is the architectural translation of the Reynolds–Heeger (2009) gain-modulation argument: top-down feedback dominates when bottom-up evidence is weak or ambiguous.

3. **Ability to shut off feedback.** The user further argues that each layer should be able to ignore selected feedback sources via learned gating — making the architecture *opt-in* for feedback. This creates an incentive for upstream layers to send useful feedback (otherwise it gets ignored) and for the system as a whole to converge to a cooperative equilibrium between layers.

## Biological grounding

The cortical visual hierarchy implements precisely this pattern (Felleman & Van Essen 1991; in seed): every visual area both projects forward and projects back. The descending pathways predominate numerically — at every level, descending fibers outnumber ascending fibers by roughly an order of magnitude. Layer 6 corticocortical neurons are a major contributor to this descending pathway (Weiler et al. 2025, in seed, full depth).

Rao & Ballard's predictive-coding framework (1999, full-depth in `papers/rao_ballard1999_predictive_coding.md`) gives this bidirectional pattern its functional interpretation: descending pathways carry top-down predictions; ascending pathways carry residual prediction errors. Bastos et al. (2012) refine this into a laminar account where deep-layer pyramidal cells code predictions and superficial-layer pyramidal cells code errors.

The user's program inherits the Rao-Ballard interpretation but augments it with the resource-competition interpretation (see `competition_emergent_predictive_coding.md`): descending predictions are predictions of what the shallower layer's *competitors* (other coalitions sending input to that layer) will do, not just sensory predictions.

## Connection to PRISM

PRISM v2's hierarchical FiLM modulation (`PRISM_V2_PROPOSAL.md` §3.4) implements a *partial* form of bidirectional hierarchical feedback:

- **Descending pathway**: $M^{\text{slow}}_{t-1}$ produces FiLM modulation that, after upsampling, modulates the V1 features. This is the analog of Layer 2 → Layer 1 descending feedback.
- **Ascending pathway**: the V1-level prediction error is pooled to V2 resolution and fed to the V2-level GRU update (PRISM_V2 §3.7). This is the analog of Layer 1 → Layer 2 ascending error.

The user's full program goes further: every layer feeds back into every layer, with explicit up/down conv operations, and the integration happens inside the Feedback Transformer rather than as a separate FiLM stage.

## Connection to the Recurrent ViT

The published Recurrent ViT (2502.10955) has *no* hierarchical feedback: a single LSTM compartment feeds back into a single ViT layer. The paper acknowledges this limitation in §5.5: "scaling up to deeper, multilayer recurrent architectures may capture the intricate, multi-level feedback loops characteristic of the primate cortex (Khan et al. 2022; Felleman & Van Essen 1991; Kietzmann et al. 2019)." The user's program is the proposed solution.

## Empirical evidence for the bidirectional pattern

- **Kietzmann et al. 2019 (in seed):** recurrent processing is required to capture human visual-system representational dynamics; pure feedforward models miss key temporal-evolution signatures.
- **Reynolds & Chelazzi 2004 (in seed):** review of attentional modulation in visual cortex showing pervasive top-down gain effects at every level of the ventral stream.
- **Miconi & VanRullen 2016 (in seed):** computational model showing that feedback explains diverse attentional effects on firing rates and receptive fields.
- **Gilbert & Li 2013 (cite-trail):** review of top-down influences on visual processing.
- **Larkum 2013 (cite-trail):** cellular mechanism (apical/basal dendrites) for the integration of top-down predictions with bottom-up sensory evidence in a single neuron.

## Connection to other concepts

- `multi_compartmental_memory` — the substrate that bidirectional feedback connects.
- `feedback_transformer` — the within-layer mechanism that integrates the feedback. Bidirectional feedback is *what* gets routed; the Feedback Transformer is *how* it gets integrated.
- `competition_emergent_predictive_coding` — the user's reinterpretation of descending feedback as predictions of *competing coalitions* generalizes the Rao-Ballard pattern.
- `iterative_variational_encoder_decoder` — the encoder runs forward reasoning across the bidirectional stack; the decoder runs backward reasoning back through it.
- `hierarchical_predictive_coding` — the conventional functional interpretation of the bidirectional pattern (descending = predictions, ascending = errors). Bidirectional hierarchical feedback is the *anatomical* commitment; hierarchical predictive coding is the *functional* commitment most often paired with it.
- `apical_basal_dendritic_integration` — the cellular implementation of the integration step. Apical dendrites receive descending feedback; basal dendrites receive ascending drive; the BAC mechanism is the AND-gate that makes the bidirectional integration *cooperative* (top-down and bottom-up co-activation) rather than competitive at the single-cell level.

## Open questions

1. **What's the right ratio of descending to ascending feedback weight?** The cortex has roughly 10:1 descending:ascending fiber counts (Felleman & Van Essen 1991). Whether the architecture should respect this asymmetry or learn it freely is open.
2. **Should ascending feedback carry raw representations, errors, or both?** Rao-Ballard says errors; the user's program currently uses raw representations (with implicit error computation happening at the Feedback Transformer level). The two are not equivalent.
3. **How does the shutdown gating learn?** If a layer can shut off feedback from another layer, the shutdown decision itself needs a training signal. Currently this is left to gradient descent on the task loss, but a more principled criterion (e.g., predictive utility of the source layer) might help.
4. **Are conv/conv-transpose the right reshape operations?** They preserve translation equivariance, which matches retinotopy. Alternative reshape (e.g., learned MLP, learned attention pooling) might allow non-retinotopic representations at deeper layers, which is closer to true IT cortex.
