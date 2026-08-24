---
id: competition_emergent_predictive_coding
type: concept
title: "Predictive coding as emergent from coalition competition"
papers:
  - rao_ballard1999_predictive_coding
  - friston2010_fep_unified_theory
  - desimone_duncan1995_biased_competition
  - reynolds1999_competitive_v2_v4
  - spratling2008_pc_biased_competition
  - bastos2012_canonical_microcircuits
  - mante2013_context_dependent_pfc
  - feldman_friston2010_attention_free_energy
  - laughlin1998_metabolic_cost
  - attwell_laughlin2001_brain_energy_budget
  - schmidhuber2015_learn_to_think
source_documents:
  - "Private & Shared-4/Evolution of Architecture (§ Motivation 1: Predictive Coding as an Emergent Property of Biased Competition, § Predictive Coding as an Emergent Strategy of Neural Competition)"
last_updated: "2026-05-18"
---

# Predictive coding as emergent from coalition competition

## The user's original hypothesis

Conventional predictive coding (Rao & Ballard 1999; Friston 2010) explains top-down cortical feedback as predictions about *sensory* input. The user's reformulation is that top-down feedback is, more fundamentally, predictions about the *behavior of competing neural coalitions* — that the architectural ubiquity of predictive coding across the cortex is a consequence of a deeper, more universal organizational pressure: internal competition for limited neural resources.

This is the principal theoretical contribution of the user's research program beyond what is published in 2502.10955 or PRISM v1/v2. It is original, falsifiable, and the architectural commitments of the rest of the program flow from it.

## The argument in four steps

**Step 1 — Resource scarcity.** The brain operates under strict metabolic and bandwidth constraints (Laughlin et al. 1998, `papers/laughlin1998_metabolic_cost.md`; Attwell & Laughlin 2001, `papers/attwell_laughlin2001_brain_energy_budget.md`). Different neural coalitions — sensory hubs, RL hubs, default-mode hubs, etc. — compete for these resources to ensure their representations are maintained, strengthened, and used to guide behavior.

**Step 2 — Game-theoretic landscape.** To win the competition for resources, a coalition cannot afford to be purely reactive; it must be proactive. The coalition's success depends on its ability to *predict* the likely states and resource demands of its rival coalitions.

**Step 3 — Feedback as opponent modeling.** A top-down feedback signal from coalition $A$ to a downstream target shared with coalition $B$ is, in this view, a prediction of what coalition $B$ is about to represent or "say" in the next moment. The descending signal pre-emptively biases the target's representation. The prediction-error signal is therefore *strategic surprise* — an indication that a competing coalition acted in an unpredicted way. The error is used to update coalition $A$'s internal model of coalition $B$.

**Step 4 — Explanation of architectural ubiquity.** Predictive coding is observed throughout cortex, including high-level association cortex with no obvious sensory-prediction role. The conventional theory has trouble explaining why an area that does not receive sensory input should implement predictive coding. The competition account does not have this problem: the relevant prediction is not of sensory input but of *internal competitors*, which exist at every level of the hierarchy. Sensory predictive coding then becomes a special case in which the "competitor" is the sensory periphery.

## Concretely: how competition operates inside a Feedback Transformer

The competition for control over the self-attention map happens at the inner-product level inside the Feedback Transformer. Consider two hubs $\mathcal{C}_Q$ (RL hub) and $\mathcal{C}_{\text{dec}}$ (autoencoder hub) competing for attention on two stimuli $S_1, S_2$. The final query and key vectors for stimulus $S_i$ are

$$
q_i = s_{q,i} \odot (c^{(Q)}_{q,i} + c^{(\text{dec})}_{q,i}), \quad k_i = s_{k,i} \odot (c^{(Q)}_{k,i} + c^{(\text{dec})}_{k,i})
$$

and the attention score is $\alpha_i = \langle q_i, k_i \rangle$.

If $\mathcal{C}_Q$ wants to win attention on $S_2$ and suppress it on $S_1$, it must choose $c^{(Q)}_{q,1}, c^{(Q)}_{k,1}$ to be *anti-aligned* with $s_{q,1}, s_{k,1}$ (so the inner product becomes negative) and $c^{(Q)}_{q,2}, c^{(Q)}_{k,2}$ to be *aligned* with $s_{q,2}, s_{k,2}$ (so the inner product becomes large positive).

But to align or anti-align, $\mathcal{C}_Q$ must *know the sign and magnitude* of $s_{q,i}, s_{k,i}$ — i.e., it must have a predictive model of the sensory projections. If $\mathcal{C}_{\text{dec}}$ adopts a different strategy, $\mathcal{C}_Q$ must also predict $c^{(\text{dec})}_{q,i}, c^{(\text{dec})}_{k,i}$ — i.e., a predictive model of the competing hub.

The hub with the more accurate predictive model of both the sensory world and its competitor will more reliably control the self-attention map. *Gradient descent on hub-specific task losses will therefore preferentially train each hub to become a better predictor of both.* This is the precise mechanism by which "predictive coding emerges from competition."

## Connection to the published biased-competition framework

Desimone & Duncan's (1995) biased competition framework — and Reynolds, Chelazzi & Desimone's (1999) operationalization in V2 and V4 — is the closest published account. Both describe within-receptive-field competition between stimuli, biased by top-down attentional signals from PFC.

The user's contribution is to scale this from individual receptive fields to whole coalitions, and to identify the predictive-coding architecture itself as the natural strategic response. Spratling (2008) showed that biased competition and predictive coding can be unified mathematically — the user's account explains *why* they should be unified in this way.

## Connection to Schmidhuber's coupled-RNN framework

Schmidhuber (2015, arXiv:1511.09249; `papers/schmidhuber2015_learn_to_think.md`) proposes coupled RNNs where a predictive world model $M$ and a controller $C$ are trained on different tasks, with $C$ learning to inspect and reuse $M$'s algorithmic information. The user's multi-hub system is a direct generalization: many objective-specific hubs, all of which both implement and exploit predictive models of the others.

## Connection to PRISM and the Recurrent ViT

The published architectures *implement* the competition mechanism implicitly but do not *test* the competition hypothesis explicitly. The Recurrent ViT (2502.10955) has a single hub (the actor-critic). PRISM v1 has the same. PRISM v2 has an actor-conditional Q-critic added during development (`Prism/docs/PRISM_V2/Q_CRITIC.md`), which is closer to a multi-hub design but not yet structured for inter-hub competition.

The user's proposed test (Evolution of Architecture §"Testing the Hypothesis"):

1. Build a multi-objective architecture: MSI hub + RL hub + VAE hub, each with own memory states, all feeding back through a central Feedback Transformer.
2. Train on tasks that put hub objectives in conflict.
3. Train a separate decoder to predict the *entire global internal state* at $t+1$ from the global state at $t$. Then iterate the decoder: predict $t+2$ from the predicted $t+1$, etc.
4. If long-range iterative prediction succeeds without any explicit world-model training signal, that is evidence that a world model emerged implicitly from the inter-hub competition.

This is the most distinctive, falsifiable, and publishable claim in the user's research program.

## Why this matters for the existing architectures

PRISM v1 and v2 should be reinterpreted in this light. The fact that PRISM v1 "works better" than v2 may be partially because v1 has fewer competing internal subsystems and therefore less strategic-prediction overhead; v2's multiple subsystems (slow/fast memory, multi-head saliency, distributional Q-critic) introduce competition pressures that the architecture is not yet well-tuned to support. The diagnostic prediction: v2's loss curves should show oscillatory behavior characteristic of zero-sum competitions between subsystems, whereas v1's should not. This is a testable prediction within the existing PRISM training infrastructure.

## Connection to other concepts

- `feedback_transformer` — the substrate for the competition. The Q-K inner-product manipulation by which competition is implemented *is* the Feedback Transformer's broadcasting operation.
- `multi_hub_multi_objective_system` — the concrete architecture in which the competition plays out.
- `bidirectional_hierarchical_feedback` — the routing of competitive signals between layers and hubs.
- `coalition_resource_competition` — the underlying resource-scarcity argument. This concept (`competition_emergent_predictive_coding`) is the *strategic-prediction-as-cortical-pressure* claim; coalition resource competition is the *why-the-pressure-exists* claim. The two file separately because the first is a claim about cortex; the second is a claim about evolution/metabolism. Together they form the user's complete theoretical thesis.
- `hierarchical_predictive_coding` — the conventional account this concept reframes. Hierarchical PC says: descending feedback = sensory predictions. The competition reframing says: descending feedback = predictions of *competing internal coalitions*; sensory predictive coding is the special case where the competitor is the sensory periphery.
- `strategic-prediction-error` (taxonomy concept) — the reinterpretation of prediction error as strategic-surprise about competitors.

## Open questions

1. **Falsification target.** What experimental outcome would *falsify* the competition account? The Evolution document does not specify clearly. A natural test: ablate one hub and check whether the others' predictive accuracy of the third hub's outputs degrades disproportionately. If yes, that's evidence the hubs were predicting each other.
2. **Multi-agent RL connection.** The competition account is structurally a multi-agent RL problem inside a single brain / network. Whether the convergence properties of multi-agent RL apply (e.g., does the system converge to a Nash equilibrium? Does it cycle?) is open.
3. **Empirical signature.** What measurable signature of "competition" should we see in trained models? Hub-specific activations correlating negatively with each other? Cross-hub mutual information patterns? These are not yet specified.
4. **Cooperation vs competition.** The user notes that the architecture creates an incentive for *cooperation* (shutdown gating). What is the equilibrium ratio of cooperation to competition that the architecture supports? Probably task-dependent.
