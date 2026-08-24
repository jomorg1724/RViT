---
id: lee2008_game_theory_neural
title: "Game theory and neural basis of social decision making"
authors:
  - "Lee, Daeyeol"
year: 2008
venue: "Nature Neuroscience"
doi: "10.1038/nn2065"
arxiv: ""
url: "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2413175/"
tags:
  - primate-neurophysiology
  - decision-making
  - review
  - dopamine
concepts:
  - coalition-resource-competition
  - reward-modulated-attention
  - actor-critic
related:
  - edelman1987_neural_darwinism
  - buzsaki2010_cell_assemblies
  - laughlin1998_metabolic_cost
  - schmidhuber2015_learn_to_think
  - glimcher2011_dopamine_rpe
relevance_to:
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-15"
---

# Game theory and neural basis of social decision making

## 1. Abstract

Decision making in a social group has two distinguishing features. First, humans and other animals routinely alter their behavior in response to changes in their physical and social environment. As a result, the outcomes of decisions that depend on the behavior of multiple decision makers are difficult to predict and require highly adaptive decision-making strategies. Second, decision makers may have preferences regarding consequences to other individuals and therefore choose their actions to improve or reduce the well-being of others. Many neurobiological studies have exploited game theory to probe the neural basis of decision making and suggested that these features of social decision making might be reflected in the functions of brain areas involved in reward evaluation and reinforcement learning. Molecular genetic studies have also begun to identify genetic mechanisms for personal traits related to reinforcement learning and complex social decision making, further illuminating the biological basis of social behavior.

## 2. Why this matters for us

Lee 2008 supplies the *game-theoretic landscape* layer of the user's competition-emergent-PC thesis. Step 2 of the four-step argument in `concepts/coalition_resource_competition.md` — "in a competitive environment, predicting your rivals is a winning strategy" — is not assumed but grounded: Lee documents that real biological decision-makers, when placed in mixed-strategy and iterated games against adaptive opponents, recruit reward-evaluation circuits (orbitofrontal cortex, anterior cingulate, striatum, dlPFC) to *model the opponent's likely action* and update that model from prediction errors.

This is the same computational structure the user proposes for inter-coalition competition inside cortex, with the opponent's "action" replaced by a rival hub's representational state. The paper licenses the move from external opponent modeling (cited literature) to internal opponent modeling (the user's program): if cortex demonstrably implements opponent-modeling RL when the opponent is another player at a table, then the architectural primitives required for opponent modeling are already part of the cortical toolkit, and recruiting them for intra-cortical competition costs no additional evolutionary innovation.

## 3. Key claims

1. Behavior in iterated games with adaptive opponents is well-described by reinforcement-learning models in which the agent maintains action-value estimates and updates them by reward prediction errors, rather than by computing Nash equilibria from first principles.
2. dlPFC and anterior cingulate neurons in macaques playing matching-pennies and rock–paper–scissors encode the animal's own previous choice, the opponent's previous choice, the resulting reward, and combinations thereof — the variables required for opponent-aware action-value updates.
3. Dopamine and the striatal RL system, which encode scalar reward prediction error in non-social tasks, are recruited in social tasks but their signal is now relative to a prediction that depends on the inferred opponent — i.e., a *social* RPE.
4. Inequity aversion, altruistic punishment, and trust behavior modulate activity in orbitofrontal cortex, insula, and ventral striatum, indicating that "other-regarding" terms enter the value function rather than being computed by a separate moral module.
5. Mentalizing-network areas (medial PFC, temporo-parietal junction) supply the model of the opponent that the RL system then uses; this is a division of labor between an opponent-model module and a value-update module.
6. Heritable variation in serotonergic and dopaminergic genes correlates with individual differences in social-game behavior, suggesting that the same neuromodulatory systems that tune non-social learning also tune the social variants.
7. Optimal Nash strategies are typically *not* what biological agents converge to; instead, agents converge to belief-learning equilibria (fictitious-play-like) that exploit any predictable opponent and approach Nash only as the opponent becomes unexploitable.
8. The opponent's recent actions enter the agent's state representation with a recency-weighted exponential filter whose time constant ($\sim$3–10 trials) is itself a learned parameter, suggesting a meta-learning layer on top of the RL update.

## 4. Methods

A review article, not a primary study. Lee surveys behavioral and neural game-theory experiments in three classes of paradigm:

- **Competitive zero-sum games** against adaptive opponents (matching pennies, rock–paper–scissors, inspection games) in humans and macaques.
- **Bargaining games** with social-preference components (ultimatum, dictator, trust) in humans.
- **Iterated cooperation games** (prisoner's dilemma, public-goods) in humans.

For each, he juxtaposes the behavioral finding (deviation from Nash, sensitivity to opponent history, sensitivity to social context) with the neural correlate (single-unit recording in macaque, fMRI in humans, occasional lesion or pharmacological manipulation).

The unifying framework is reinforcement learning with state-dependent value functions:

$$V_t(a) \leftarrow V_{t-1}(a) + \alpha \cdot \delta_t$$

where $\delta_t$ is a prediction error whose definition depends on what the agent is trying to predict — own reward (non-social RL), reward conditional on opponent action (opponent-aware RL), or reward including other-regarding terms (social-preference RL). The substantive empirical claim throughout is that the *same* circuits (dopaminergic midbrain, ventral and dorsal striatum, OFC, ACC, dlPFC) implement all three variants, distinguished only by what state-vector they take as input.

The opponent-aware variant has the form:

$$\delta_t = r_t - \sum_{a'} P(a'_{op} \mid h_t) \cdot Q(a_t, a'_{op})$$

where $a'_{op}$ ranges over the opponent's possible actions, $P(a'_{op} \mid h_t)$ is the inferred opponent-policy conditioned on game history $h_t$, and $Q(a_t, a'_{op})$ is the joint action-value. The inferred opponent-policy is what mentalizing-network areas supply; the value update is what striatal / OFC circuits perform. This decomposition is the central organizing structure of Lee's review.

## 5. Results

Because this is a review, the "results" are the cross-study generalizations Lee establishes.

**Macaque matching-pennies.** Against a computer opponent that exploits any predictable pattern, macaques approach the mixed-strategy equilibrium (50/50) but show systematic small departures — biases towards win-stay/lose-shift — that are quantitatively captured by RL models with a learning rate $\alpha \approx 0.4$–$0.7$ and a small choice-history bias term. Single-unit recordings (Barraclough, Conroy & Lee 2004; Seo, Barraclough & Lee 2007) show that 20–40% of dlPFC neurons encode the conjunction of own previous choice and opponent previous choice within $\approx$200 ms of feedback. ACC neurons additionally encode the reward outcome conjoined with these choice variables.

**Human ultimatum game.** fMRI shows that unfair offers activate anterior insula in proportion to the rejection rate ($r \approx 0.45$ across studies). Rejection rates rise from $\sim$10% for fair offers (50/50) to $\sim$50% for offers $<$20% of the pot. Right dlPFC TMS reduces rejection rates of unfair offers without changing the explicit judgment that they are unfair — dissociating affective evaluation from action selection.

**Trust and oxytocin.** In iterated trust games, intranasal oxytocin administration roughly doubles the amount entrusted to anonymous partners. Caudate activity at the moment of partner reciprocation scales with the trustor's growing investment, consistent with a social-RPE signal.

**Iterated prisoner's dilemma.** Mutual cooperation activates ventral striatum and OFC at levels comparable to monetary reward of similar magnitude; defection following cooperation produces a negative striatal RPE-like signal. The reciprocity-driven cooperation rate ($\sim$60–80% in iterated play) is substantially above the Nash prediction of pure defection, and the gap is well captured by RL models with a social-preference term (positive utility of partner reward, weight $\sim$0.3 of own reward).

**Imaging genetics.** Lee reports that 5-HTTLPR short-allele carriers reject unfair offers more frequently and that COMT Val/Val individuals show flatter response curves to social feedback. Heritabilities for ultimatum-game rejection rates are estimated at $\sim$40% from twin data.

**Mentalizing dissociation.** Across tasks, mentalizing-network areas (medial PFC, TPJ) activate during *opponent-model construction* phases, while striatum and OFC activate during *value-update* phases. The two networks rarely co-activate within a trial — a serial rather than parallel architecture for opponent inference and value learning.

**Lesion and pharmacological evidence.** OFC lesions in macaques and humans selectively impair adaptation to changing reward contingencies in social games while sparing performance in non-social tasks of similar difficulty. Pharmacological serotonin depletion in humans increases rejection rates of unfair offers without changing fair-offer acceptance — a dissociation Lee uses to argue that serotonin specifically modulates social-RPE, not RPE in general.

**Cross-paradigm consistency.** A key strength Lee highlights is that the same RL-with-opponent-model framework fits behavior in matching-pennies, rock-paper-scissors, ultimatum, trust, and iterated prisoner's dilemma games with the *same* learning-rate and inverse-temperature parameters within an individual. The state-vector changes (own choice, opponent choice, reward, social-preference terms) but the update rule does not. This cross-paradigm consistency is what makes the "single mechanism, multiple state-vectors" claim more than fitting noise.

## 6. Critique / limitations

The review's central commitment — that social decision making is "RL with a richer state" — is parsimonious but understates several things.

- **Where does the opponent model come from?** Lee largely treats it as a black box supplied by mentalizing-network areas; the actual computational form of opponent inference (Bayesian level-$k$ models, fictitious play, finite-automaton induction) is not adjudicated. This is the load-bearing gap for any program — including the user's — that wants to operationalize "predict your rival" as a concrete update rule.
- **fMRI confounds.** The human social-preference evidence in OFC and anterior insula is correlational and confounded with task difficulty, salience, and reaction time. Subsequent re-analyses (Behrens et al. 2009; Hare et al. 2010) have argued for more specific computational mappings than Lee's review offers.
- **Dyadic-only macaque evidence.** The single-unit work is methodologically tighter but restricted to dyadic zero-sum games against a computer, leaving open whether the same neurons encode the richer state spaces of multi-agent or cooperative play. The user's $N$-hub program is precisely the $N > 2$ generalization Lee does not test.
- **Imaging-genetics replication.** The 2008 vintage of imaging-genetics literature is now widely regarded as underpowered. The 5-HTTLPR / COMT claims should be treated as suggestive, not settled.
- **Scalar reward.** The RL framework Lee uses assumes a scalar reward; extending to vector-valued "rewards" (which the user's strategic-prediction-error concept requires) is a non-trivial theoretical step that Lee does not take.
- **Cooperation vs. competition.** Lee's review covers both cooperative and competitive games but does not adjudicate when each regime dominates. The user's coalition-competition account is *only* about the competitive regime; importing Lee's results requires assuming the cortical setting is closer to matching-pennies than to iterated prisoner's-dilemma cooperation. This assumption is plausible (coalitions compete for finite metabolic resources) but not entailed by Lee's evidence.
- **No mechanism for the opponent-model architecture.** Lee identifies *which* areas implement opponent modeling (mPFC, TPJ) but not *how*. A computational architecture for the opponent-model module would be the natural next step; the user's Feedback-Transformer Q/K integration is one candidate mechanism, but Lee's review predates and does not constrain that proposal.

## 7. Connection to our work

Lee 2008 is the **citation that does the work for Step 2** of the four-step coalition-competition argument (`concepts/coalition_resource_competition.md`, §"The argument has four steps"; also `threads/the_user_architectural_program.md` §5).

The user's claim there is that in a competitive environment, the right move for each coalition is to predict its rivals — that the optimal strategy under inter-coalition competition is opponent modeling rather than reactive policy.

Lee establishes this empirically for the case the brain demonstrably solves: zero-sum and mixed-motive games against adaptive external opponents. The biological agents Lee surveys do not compute Nash equilibria; they maintain action-value estimates that depend on inferred opponent state and update them by prediction errors. This is exactly the computational primitive the user proposes operates *inside* cortex, with each coalition (RL hub, VAE hub, MSI hub, default-mode hub) playing the role of an "opponent" whose representational state must be predicted by the other coalitions to win the attention-substrate competition.

The transfer of Lee's empirical content to the user's program rests on one assumption: that the *kind* of agency a coalition exhibits within cortex is sufficiently similar to the kind of agency a player exhibits at a poker table for the same RL-with-opponent-model machinery to apply. The defense of this assumption is that both settings share the load-bearing features: (i) multiple agents with partially conflicting objectives; (ii) the agents' actions are observable but their internal states are not; (iii) the payoff structure rewards predicting the other's action; (iv) the system is iterated, so prediction errors accumulate into improved opponent models. Each of these features is concretely realized in the user's multi-hub architecture.

Three specific architectural commitments in the user's program inherit from this paper.

**Strategic prediction error.** The reformulation in `concepts/coalition_resource_competition.md` ("How this reframes predictive coding") generalizes the social-RPE Lee documents. Lee's dopaminergic / striatal RPE is a scalar mismatch between predicted and actual *opponent-conditioned reward*. The user's strategic prediction error is a vector mismatch between predicted and actual *opponent representational state*. Both are RPEs over a quantity that depends on a rival agent; the user's version is the vector-valued generalization required when the "reward" is replaced by a high-dimensional internal state. The biological precedent Lee supplies makes this less of a leap than it would otherwise be: the brain already computes RPEs over targets defined by an inferred rival.

**Multi-hub multi-objective system.** `concepts/multi_hub_multi_objective_system.md` and the formal account in `threads/the_user_architectural_program.md` §5 ("Formal account of the competition") describe hubs competing for the Q/K inner-product space. This is a multi-player generalization of Lee's dyadic-game setup. Lee's two-player matching-pennies dynamics become an $N$-coalition mixed-strategy equilibrium in the Q/K manifold; the same RL-with-opponent-model logic Lee documents at the behavioral level then describes how gradient descent on each hub's loss will train it to predict the others. The fact that real neural circuits implement this RL-with-opponent-model logic (rather than, say, explicit equilibrium computation) is what permits the user to claim the architectural pressure is *implementable*, not just normatively desirable.

**Falsifiable test plan.** The empirical test in `threads/the_user_architectural_program.md` §5 ("Empirical test plan") — train a multi-hub system on conflicting-objective tasks, then test whether a separate decoder can roll out coherent global-state predictions from local state — has the same logical shape as Lee's evidence: if RL-style opponent modeling really is what the system is doing, then internal representations should contain the variables that an opponent-aware RL update rule would require, and a probe trained to read those variables out should succeed. Lee provides the existence proof at the cortical-neuron level (dlPFC encodes the required conjunctions of own-choice $\times$ opponent-choice $\times$ outcome); the user's plan is to demonstrate the corresponding existence at the artificial-system level via the global-state decoder.

**Links to related entries.** `glimcher2011_dopamine_rpe` is the *non-social* baseline (RPE over own predicted reward); Lee 2008 is the *social* extension (RPE over opponent-conditioned reward). Together they bracket the strategic-prediction-error concept. `schmidhuber2015_learn_to_think` complements this from the architectural side: Schmidhuber's C–M (controller–world-model) pairing is one rival modeling another, and Lee provides the biological precedent for that move. `laughlin1998_metabolic_cost`, `edelman1987_neural_darwinism`, and `buzsaki2010_cell_assemblies` connect via Step 1 of the four-step argument (resource scarcity creates the competition that Lee's mechanisms then resolve at the algorithmic level).

The paper does *not* directly bear on the Recurrent ViT (2502.10955) or PRISM v1/v2 implementations as currently published. Its relevance is purely to the theoretical motivation for the multi-hub direction in PRISM v2 and beyond — specifically, it provides the empirical grounding that lets the user claim "inter-hub competition with opponent modeling" is not a metaphor borrowed from economics but a description of how real cortex behaves when it faces this kind of problem.

**Predictions for a multi-hub implementation.** Three Lee-inspired predictions follow for the user's multi-hub architecture that are testable in PRISM v2 or a successor system:

- *Recency-weighted opponent traces.* If each hub maintains an exponentially-weighted recency filter over the *other hubs'* recent contributions to the Q/K substrate (analogous to Claim 8's $\sim$3–10 trial recency in Lee's RL fits), this trace should appear in the hub's hidden state and be decodable from it. The time constant should be learnable and should scale with the volatility of the rival hub's behavior.
- *Serial mentalizing / value-update phases.* If the user's hubs follow the serial rather than parallel architecture Lee documents, then within a single forward pass we should see two distinguishable sub-phases: one where each hub estimates the others' likely contribution (mentalizing-like), one where it updates its own Q/K projection accordingly (value-update-like). Decoding the hub's *prediction-of-other* should peak earlier in the pass than decoding its *own-action*.
- *Social-RPE-like signal.* The gradient flowing into each hub's contribution layer at training time should resemble a social RPE: a vector mismatch between predicted and actual rival contributions, weighted by how strongly that rival's behavior moves the hub's loss. Probing this gradient signal during training and comparing it to the analytical "strategic prediction error" of `concepts/coalition_resource_competition.md` is a concrete connection between Lee's neuroscience and the user's ML implementation.
- *Anti-correlated representations under shared resource demand.* If two hubs share resource demands (e.g., both want the same Q/K subspace), Lee's matching-pennies analog predicts they should develop anti-correlated outputs — each "fakes" in the direction the other does not. This is the same prediction §"Why this is more than a metaphor" (point 1) of `coalition_resource_competition.md` makes from first principles; Lee 2008 provides the biological precedent that the necessary dynamics exist.

If these predictions hold, the user's competition-emergent-PC thesis acquires both a biological precedent (Lee 2008) and an algorithmic instantiation (the multi-hub system) — closing the gap between the two halves of the program.

**Why "game-theoretic landscape" is the right label.** The user's phrase in `threads/the_user_architectural_program.md` §5 — "game-theoretic landscape" — is doing real work. It is not borrowing game theory's *equilibrium* concepts (Nash, subgame-perfect, correlated) but its *learning-dynamics* concepts (fictitious play, no-regret, opponent-aware RL). Lee's review is the bridge: it makes precise that the brain has internalized the learning-dynamics framing, not the equilibrium one. The user's program is therefore committed to learning-dynamics game theory at the architectural level, and the natural mathematical objects for analyzing the multi-hub system are evolutionary-stable strategies and replicator dynamics on the Q/K manifold, rather than fixed-point Nash analysis. This is a non-trivial design commitment that Lee's evidence specifically supports.

## 8. Citations to follow

- barraclough2004_matching_pennies — Lee's own single-unit work on macaque dlPFC in matching pennies; the empirical bedrock for Claim 2 and the closest neural evidence for opponent-aware action-value coding.
- seo2007_pfc_acc_game — dlPFC and ACC encoding of own-choice, opponent-choice, and reward in iterated matching pennies; the conjunction-coding result.
- sanfey2003_ultimatum_fmri — the canonical anterior-insula / ultimatum-game fMRI study; primary citation behind the social-preference claims.
- behrens2008_social_value — fMRI evidence that medial PFC distinguishes self-derived from advisor-derived reward estimates; sharpens Lee's "mentalizing supplies the opponent model" claim.
- camerer2003_behavioral_game_theory — the behavioral-game-theory reference framework; necessary for any deeper treatment of why biological agents deviate from Nash.
- king_casas2005_iterated_trust — fMRI of iterated trust game showing caudate RPE-like signals to partner reciprocation; bridges Lee's social-RPE claim to the dopaminergic literature.
- montague2006_neuroeconomics_review — the broader neuroeconomics survey that contextualizes Lee's game-theoretic slice.
- fehr_camerer2007_social_neuroeconomics — companion review with stronger emphasis on inequity aversion and altruistic punishment.
- mccabe2001_reciprocal_trust_fmri — early fMRI of trust games; first identification of medial PFC engagement during opponent modeling.
- glimcher2003_decisions_uncertainty — Glimcher's framing of neuroeconomic decision-making under uncertainty; the non-social analog Lee builds on.
- frith_frith2006_mentalizing — review of the mentalizing network (mPFC, TPJ) that Lee invokes but does not himself review; necessary for adjudicating where opponent-model inference actually happens.
- daw2005_uncertainty_competition — model-based vs. model-free competition for behavioral control; a structural analog of the user's inter-hub competition at the level of decision systems rather than coalitions.
- camerer_ho1999_experience_weighted_attraction — Camerer-Ho EWA learning model, the most common belief-learning RL hybrid Lee's data fit; necessary to specify the exact functional form of the opponent-aware RL update.
- niv2009_reinforcement_learning_brain — review of RL in the brain that complements Lee's social-game slant with the non-social baseline.
- yoshida2008_game_theory_prefrontal — single-unit dlPFC recordings in macaques playing repeated games; closest companion to Lee's own animal work.
- behrens2009_associative_learning_amygdala — model-based learning signals separable from model-free RPE; constrains where the "opponent model" lives.
- hampton2008_neural_correlates_mentalizing — fMRI of model-based opponent inference in inspection games; the cleanest test of the mentalizing-supplies-the-model claim.
- rilling2002_neural_basis_cooperation — early fMRI of iterated prisoner's-dilemma cooperation showing striatal activation; the source of the "mutual cooperation is rewarding" result.
