---
id: coalition_resource_competition
type: concept
title: "Coalition resource competition"
papers:
  - laughlin1998_metabolic_cost
  - attwell_laughlin2001_brain_energy_budget
  - edelman1987_neural_darwinism
  - buzsaki2010_cell_assemblies
  - lee2008_game_theory_neural
  - desimone_duncan1995_biased_competition
  - reynolds1999_competitive_v2_v4
  - schmidhuber2015_learn_to_think
source_documents:
  - "Private & Shared-4/Evolution of Architecture (§ Predictive Coding from Competition)"
last_updated: "2026-05-13"
---

# Coalition resource competition

## Definition

A theoretical commitment, original to the user's program, that frames neural coalitions (cell assemblies, functional hubs, cortical areas) as agents competing for finite metabolic and bandwidth resources, and treats the dynamics of cortical computation as the equilibrium of that competition rather than as the output of a single optimization process.

The argument has four steps:

**Step 1 — Resource scarcity is real.** The brain operates under strict metabolic and bandwidth constraints. Laughlin et al. 1998 (`papers/laughlin1998_metabolic_cost.md`) puts numbers on this: chemical synaptic transmission costs ≈10⁴ ATP per bit, graded analog signaling 10⁶–10⁷ ATP per bit, far above the thermodynamic minimum. Attwell & Laughlin 2001 (`papers/attwell_laughlin2001_brain_energy_budget.md`) extends to mammalian cortex: ≈75% of grey-matter ATP is used for signaling. The brain cannot afford to compute everything; computational resources must be allocated.

**Step 2 — Multiple coalitions compete for these resources.** Different neural coalitions — sensory hubs, RL hubs, default-mode hubs, etc. — each pursue their own objectives and each require resources (firing-rate budget, synaptic-weight space, attention bandwidth) to ensure their representations are maintained and used to guide behavior. The neural-Darwinism framing (Edelman 1987, `papers/edelman1987_neural_darwinism.md`; Buzsáki 2010 cell-assemblies, `papers/buzsaki2010_cell_assemblies.md`) provides the precedent: coalitions of neurons that "win" the selection pressure persist and shape behavior; losers are pruned or quiescent.

**Step 3 — In a competitive environment, predicting your rivals is a winning strategy.** Game-theoretic reasoning (Lee 2008, `papers/lee2008_game_theory_neural.md`) tells us that a coalition that can predict the resource demands and representational states of competing coalitions has a strategic advantage: it can anticipate where rivals will draw resources, position itself to avoid wasteful conflict or to exploit gaps, and update its own representations in ways that exploit the rivals' weaknesses. This is opponent modeling, generalized from social to neural agents.

**Step 4 — Predictive coding emerges as the strategic substrate.** If the right move for every coalition is to predict every other coalition, the cortex's hierarchical descending-prediction architecture (Rao-Ballard, Bastos, Keller-Mrsic-Flogel) is the natural implementation. Top-down feedback signals are not predictions of *sensory input* — they are predictions of *what competing coalitions are about to represent*. Prediction errors are then signals of *strategic surprise*: an indication that a competing coalition acted in an unpredicted way. The error updates the coalition's internal model of the competitor, leading to better future predictions and stronger competitive position.

## How this reframes predictive coding

Conventional predictive coding (`concepts/hierarchical_predictive_coding.md`) treats top-down feedback as predictions about the sensory periphery. This works fine for primary sensory cortex but is awkward for high-level association cortex, default-mode network, and other cortical regions with no direct sensory-prediction role.

The coalition-competition reframing handles this naturally: top-down predictions in association cortex are predictions of *internal* competitors (other association regions, default-mode hubs, RL circuits), not of sensory input. The ubiquity of predictive-coding-like dynamics across cortex (rather than just in sensory areas) is the empirical observation this reframing explains. Sensory predictive coding is then the special case where the "competitor" is the sensory periphery (which can be modeled as a fixed adversary, since its outputs do not respond strategically to neural feedback).

## Formal account of the competition mechanism

The competition is implemented architecturally at the level of the central self-attention substrate (`concepts/multi_hub_multi_objective_system.md`). For each stimulus token $i$, the final attention-related Q vector is

$$
q_i = s_{q,i} \odot \big( c_{q,i}^{(\text{hub}_1)} + c_{q,i}^{(\text{hub}_2)} + \cdots \big)
$$

and similarly for $k_i$. The attention score $\alpha_i = \langle q_i, k_i \rangle$ is then a function of all hubs' contributions plus the sensory contribution. Each hub's optimal Q/K projection depends on two predictions:

(a) the bottom-up sensory projection $s_q, s_k$ — predicting the world;
(b) the other hubs' contributions $c_q^{(\text{other})}, c_k^{(\text{other})}$ — predicting the opponents.

A hub with a better predictive model of both wins the attention competition more often, secures more representational bandwidth, and accomplishes its objective. Gradient descent on each hub's loss therefore implicitly trains the hub to predict both the sensory input *and* the rival hubs' behavior — the architectural mechanism by which "predictive coding emerges from competition" is not a metaphor but a concrete optimization pressure.

## Why this is more than a metaphor

The user's claim is *not* "competition is a nice analogy for predictive coding"; it is "the same optimization pressure that gradient descent on hub-specific losses applies in this architecture is the optimization pressure evolution applied to cortex." If true, this gives three predictions that conventional predictive coding does not give:

1. Hubs that share resource demands should develop *anti-correlated* representations more readily than hubs with independent resource demands. Predictive coding alone makes no such prediction.
2. The accuracy of a hub's predictions of *other hubs* should scale with the resource pressure on the system: more resource-constrained systems should show stronger inter-hub prediction. This is testable in the multi-hub architecture by varying the system's compute budget.
3. Disrupting one hub's contribution to the central substrate should specifically increase the error signals in *other hubs* — they were relying on the disrupted hub's predictions and must now re-estimate them. This is testable by ablation in the multi-hub system.

## Connection to other concepts

- `competition_emergent_predictive_coding` — the user's original hypothesis named after this argument; the concept and the argument share the same name in the database.
- `multi_hub_multi_objective_system` — the architectural substrate in which the competition plays out.
- `strategic_prediction_error` — the reformulation of prediction error as strategic surprise about a competing coalition.
- `world_model_emergence` — the empirical prediction that competition produces an emergent world model.
- `metabolic_constraints_on_neural_computation` — the resource-scarcity premise.
- `hierarchical_predictive_coding` — the architectural commitment the competition argument explains.
- `feedback_transformer` — the multiplicative-broadcasting mechanism that makes inter-hub competition computationally tractable.

## Connection to the literature

The closest published analog at the cellular level is the biased-competition framework (Desimone & Duncan 1995, `papers/desimone_duncan1995_biased_competition.md`; Reynolds, Chelazzi & Desimone 1999, `papers/reynolds1999_competitive_v2_v4.md`): receptive fields compete for representation under top-down bias. The user's contribution is to scale this from individual receptive fields to whole coalitions, and to identify the predictive-coding architecture as the natural strategic response that the competition pressure selects for.

Schmidhuber 2015 (`papers/schmidhuber2015_learn_to_think.md`) is the closest computational analog: his C–M framework couples a controller and a world model, with C learning to "query" M's algorithmic information. The user's multi-hub system generalizes this to many hubs and adds the competition pressure that Schmidhuber's cooperative framing lacks.

## Open questions

1. **Is the resource-scarcity premise strong enough to drive predictive coding?** Laughlin's per-bit cost numbers are large in absolute terms but the brain has redundancy; whether the resource pressure is *binding* (forces specific architectural choices) or *non-binding* (the brain has slack) is debated.
2. **Are the empirical predictions (anti-correlation, scaling with compute budget, ablation-sensitivity) actually new?** It's possible that conventional predictive coding plus standard normalization mechanisms produces the same predictions.
3. **What is the right metric for "winning" the attention competition?** Total attention weight allocated; total bandwidth claimed; downstream behavioral influence — different metrics give different competition dynamics.
4. **How does the competition interact with cooperation?** In Schmidhuber's framework, C and M cooperate. In the user's framework, hubs compete. Real cortex likely has both; the right architectural balance is unsettled.
