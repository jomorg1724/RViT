---
id: friston2012_dopamine_active_inference
title: "Dopamine, affordance and active inference"
authors:
  - "Friston, Karl J."
  - "Shiner, Tamara"
  - "FitzGerald, Thomas"
  - "et al."
year: 2012
venue: "PLoS Computational Biology"
doi: "10.1371/journal.pcbi.1002327"
arxiv: ""
url: "https://doi.org/10.1371/journal.pcbi.1002327"
tags:
  - free-energy-principle
  - dopamine
  - theoretical-essay
  - predictive-coding
concepts:
  - active-inference
  - precision-weighting
  - variational-free-energy
  - hierarchical-predictive-coding
  - prediction-error-map
  - reward-modulated-attention
related:
  - friston2010_fep_unified_theory
  - glimcher2011_dopamine_rpe
  - babayan_uchida_gershman2018_belief_states_dopamine
  - pezzulo_parr_friston2024_active_inference
  - feldman_friston2010_attention_free_energy
  - monosov2020_outcome_uncertainty
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_93
status: full
depth: full
last_updated: "2026-05-15"
---

# Dopamine, affordance and active inference

## 1. Abstract

> "The role of dopamine in behaviour and decision-making is often cast in terms of reinforcement learning and optimal decision theory. Here, we present an alternative view that frames the physiology of dopamine in terms of Bayes-optimal behaviour. In this account, dopamine controls the precision or salience of (external or internal) cues that engender action. In other words, dopamine balances bottom-up sensory information and top-down prior beliefs when making hierarchical inferences (predictions) about cues that have affordance. In this paper, we focus on the consequences of changing tonic levels of dopamine firing using simulations of cued sequential movements. Crucially, the predictions driving movements are based upon a hierarchical generative model that infers the context in which movements are made. This means that we can confuse agents by changing the context (order) in which cues are presented. These simulations provide a (Bayes-optimal) model of contextual uncertainty and set switching that can be quantified in terms of behavioural and electrophysiological responses. Furthermore, one can simulate dopaminergic lesions (by changing the precision of prediction errors) to produce pathological behaviours that are reminiscent of those seen in neurological disorders such as Parkinson's disease. We use these simulations to demonstrate how a single functional role for dopamine at the synaptic level can manifest in different ways at the behavioural level." (Friston et al. 2012.)

## 2. Why this matters for us

This paper is the canonical statement of the alternative-to-RPE account of dopamine: instead of encoding reward prediction error, dopamine encodes the *precision* of prediction errors in a hierarchical generative model. For the user's multi-hub architectural program ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5), which explicitly entertains a dual interpretation in which the RL hub's broadcast signal can be read either as a TD-RPE (Glimcher 2011) or as a precision-weighting gate ([feldman_friston2010_attention_free_energy](research_db/papers/feldman_friston2010_attention_free_energy.md), Friston 2010), this paper is the load-bearing reference for the second horn of that interpretation. It is also the reference cited by the Recurrent ViT paper (2502.10955, ref 93) when motivating the precision-weighting role of the saliency map — and it is therefore one of the small set of papers that any reader of the published work might trace back to in order to understand what "precision-weighting" actually means in a working simulation.

## 3. Key claims

1. Dopamine encodes the *precision* (inverse variance) of prediction errors in a hierarchical generative model — not the prediction errors themselves and not a reward signal.
2. Precision-weighting gates the relative influence of bottom-up sensory evidence vs top-down prior beliefs at each hierarchical level. High dopamine ⇒ bottom-up cues dominate; low dopamine ⇒ top-down priors dominate.
3. This single synaptic-level role (gain on prediction-error units) reproduces, at the behavioural level, both the canonical "reward learning" phenomenology and the "attentional / motivational vigour" phenomenology — the apparent multi-functionality of dopamine is a level-of-description artifact.
4. The framework is a strict alternative to the dopamine-reward-prediction-error (DA-RPE) hypothesis: in active inference there is no separate reward signal; "reward" is the agent's prior expectation over its own observations, and behaviour optimises (expected) free energy rather than expected reward.
5. The simulations use a hierarchical Markov-decision-process generative model in which a higher level represents *context* (which sequence of cues is currently relevant) and a lower level represents *cue → action* affordances. Dopamine sets the precision of the lower-level prediction errors.
6. Reducing simulated tonic dopamine (i.e., reducing precision on sensory prediction error) reproduces Parkinsonian phenomena: bradykinesia, reduced movement vigour, increased reliance on prior beliefs, impaired set-shifting when context changes unexpectedly. Increasing tonic dopamine reproduces impulsivity and reduced contextual stability.
7. Because dopamine modulates the gain of prediction-error units, its effect on plasticity is *indirect*: dopaminergic gain controls how strongly prediction errors drive belief updates and, downstream, synaptic change — recovering the broad outlines of the three-factor learning story without committing to RPE as the third factor.

## 4. Methods

The paper is a simulation study built on Friston's active-inference framework. The generative model is a discrete-time hierarchical partially observable Markov decision process (POMDP) with two levels.

At the lower level, hidden states $s_t^{(1)}$ encode the current cue / affordance (which limb to move, in which direction). Observations $o_t^{(1)}$ are the sensory cues. Actions $a_t$ are emitted by the agent and re-enter the generative model as part of the state transition.

At the higher level, hidden states $s_t^{(2)}$ encode the *context*: which cue-sequence is currently operative. Context changes slowly; the agent must infer it from the pattern of recent cues.

Inference proceeds by minimisation of variational free energy

$$
F = \mathbb{E}_q[\log q(s) - \log p(o, s)]
$$

with a mean-field approximate posterior $q(s) = \prod_l q(s^{(l)})$ factorised over hierarchical levels. Under the Laplace approximation and Gaussian assumptions used throughout the paper, the gradient update on the posterior expectation $\mu^{(l)}$ at level $l$ has the standard predictive-coding form

$$
\dot\mu^{(l)} \;\propto\; \Pi^{(l)} \,\varepsilon^{(l)} \;-\; \partial_\mu \Pi^{(l-1)} \,\varepsilon^{(l-1)}
$$

where $\varepsilon^{(l)}$ is the prediction error at level $l$ and $\Pi^{(l)}$ is its precision (inverse covariance). The precision $\Pi^{(l)}$ is the quantity dopamine modulates. The authors implement this as a multiplicative gain $\Pi^{(l)} \leftarrow \gamma \cdot \Pi_0^{(l)}$ with $\gamma$ identified as tonic dopamine.

Action selection is implemented by minimisation of *expected* free energy over policies $\pi$:

$$
G(\pi) = \mathbb{E}_{q(o,s|\pi)}[\log q(s|\pi) - \log p(o, s)]
$$

so that policies are scored both by how well they reduce uncertainty (epistemic value) and by how well their predicted observations match the agent's prior preferences (pragmatic value). There is no explicit reward function; instead, prior preferences over observations play the role that a reward function would in conventional RL.

The simulations consist of repeated cued sequential-movement trials. The authors vary tonic dopamine $\gamma$ across simulations and across blocks within a simulation, then measure (i) reaction times, (ii) movement vigour, (iii) set-switching behaviour when the cue-sequence context is changed without warning, (iv) simulated electrophysiological proxies (pre-movement build-up of expected state precision; phasic deviations of $\gamma$ around context changes).

## 5. Results

The simulations reproduce a set of canonical empirical findings under the single manipulation of precision $\gamma$:

- **Tonic-dopamine-vigour relationship.** Movement vigour (peak velocity of the simulated action) scales monotonically with $\gamma$. Low $\gamma$ ⇒ bradykinesia-like slowing; high $\gamma$ ⇒ hyperkinetic, impulsive responding. This recovers Niv et al.'s 2007 tonic-DA-and-vigour result without invoking average-reward-rate machinery.
- **Set-switching under context change.** Following an uncued change in cue-sequence context, agents with reduced $\gamma$ persist in the old context for many more trials before updating $s^{(2)}$, mirroring perseveration in Parkinson's patients on the Wisconsin Card Sorting Test.
- **Phasic dopamine analog.** At trial boundaries where the agent's posterior over context is highly uncertain, the model's effective precision spikes briefly — a precision burst — that the authors identify with the phasic dopamine response classically attributed to reward prediction error. Under this identification, the same waveform that Schultz / Glimcher read as RPE is reinterpreted as a precision update over a hierarchical belief.
- **Pathology of high $\gamma$.** Persistently elevated $\gamma$ produces impulsive policy selection, reduced exploration, and over-confidence in current beliefs — reminiscent of dopaminergic addiction-state phenomena and L-DOPA-induced impulsivity in Parkinson's patients.
- **Dissociation of dopamine and reward.** The framework predicts (and the simulations confirm) that dopaminergic manipulations should bias *which cues an agent attends to and acts on* even in the absence of any reward — a prediction at variance with strict RPE accounts and in line with the salience-coding dopamine literature (Matsumoto & Hikosaka 2009; Bromberg-Martin et al. 2010).
- **Cross-pathology unification.** A single one-parameter manipulation ($\gamma$) is sufficient to span a continuum of behavioural pathologies from Parkinsonian bradykinesia to impulsive over-action — the paper's principal demonstration of explanatory parsimony.

The paper reports no fits to specific empirical datasets; the results are qualitative pattern-matches between simulation behaviour and the published phenomenology of dopaminergic manipulations.

## 6. Critique / limitations

The paper's stance is openly programmatic: the authors are proposing an alternative to the dominant DA-RPE account and arguing that it is at least as good a fit to the existing phenomenology. They do not claim to falsify the RPE story, and the simulations are constructed to demonstrate possibility rather than to provide a decisive empirical comparison.

- **Identifiability of precision vs RPE.** The paper's central re-identification — phasic dopamine bursts encode precision updates rather than prediction errors — is mathematically natural but empirically under-determined by the data the paper cites. Under reasonable choices of generative model the two accounts are weakly distinguishable on standard cue-reward paradigms (a point [babayan_uchida_gershman2018_belief_states_dopamine](research_db/papers/babayan_uchida_gershman2018_belief_states_dopamine.md) develops in detail for the belief-state generalisation of RPE).
- **No new empirical data.** The paper is a simulation study with qualitative pattern-matching to published behaviour. The Parkinsonian and impulsive phenomena it reproduces are also reproducible by RPE-based models with modified parameters; the paper does not provide a critical test that distinguishes the two.
- **The role of reward is dissolved, not explained.** Active inference replaces a reward function with a prior over preferred observations. This is mathematically convenient but pushes the explanatory burden onto where preferences come from and how they are learned — questions the paper does not address.
- **Hierarchical model is hand-designed.** The two-level context-and-cue generative model is constructed to produce the desired simulated phenomena. Whether the framework scales to richer real-world tasks (where the relevant context structure is not known in advance) is an open question taken up in later active-inference work ([pezzulo_parr_friston2024_active_inference](research_db/papers/pezzulo_parr_friston2024_active_inference.md)).
- **Simulated electrophysiology is loose.** The "precision burst" the authors equate with phasic dopamine is a model-internal quantity whose mapping onto cellular dopamine firing rates is qualitative. Direct fits to electrophysiological waveforms are not attempted.
- **Glosses over heterogeneity.** The model treats dopamine as a single global precision parameter, sidestepping the heterogeneity (RPE-coding vs salience-coding subpopulations; regional release differences) that Glimcher 2011 already flagged and that later voltammetry work has emphasised.
- **No engagement with corticostriatal plasticity.** The three-factor learning rule of [glimcher2011_dopamine_rpe](research_db/papers/glimcher2011_dopamine_rpe.md) is one of the strongest pieces of cellular-level support for the RPE account. Friston et al. acknowledge that gain-modulated prediction errors will modulate downstream plasticity but do not work out a corresponding cellular plasticity rule.

The strongest critique-of-the-critique is that "precision" and "RPE" are not mutually exclusive accounts — recent syntheses ([pezzulo_parr_friston2024_active_inference](research_db/papers/pezzulo_parr_friston2024_active_inference.md)) argue that the two can be unified within active inference, with phasic dopamine carrying both a precision-update component and a value-related component on different timescales. The 2012 paper takes the harder line; the field has since softened.

## 7. Connection to our work

This paper is the load-bearing reference for the precision-weighting horn of the user's dual RL-vs-precision-weighting interpretation of the multi-hub system's neuromodulatory broadcast ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5, §7).

**Touchpoint 1: dual interpretation of the RL hub's signal.** The user's multi-hub program ([the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5) is deliberately agnostic about whether the global scalar broadcast from the RL hub is best read as a TD-RPE (the Glimcher 2011 / Sutton-Barto / actor-critic reading) or as a precision update (the present paper's reading). Friston et al. 2012 supplies the precision-weighting alternative in explicit, simulated form. Under this reading, the RL hub's contribution to the shared self-attention substrate is not a "teaching signal" for actor-critic plasticity but a *gain on prediction-error signals from the sensory hubs* — exactly the role the `precision-weighting` concept ([TAXONOMY.md](research_db/TAXONOMY.md), attention mechanisms) plays in the user's vocabulary. The architectural commitment that the RL hub emits a scalar (or low-rank) broadcast is consistent with both readings; only the *interpretation* of what that scalar means differs.

**Touchpoint 2: PRISM's saliency map as precision-weighting.** PRISM v1's saliency map (`THESIS.md` §2.6) is interpreted in the published thesis as a precision-weighting signal in the Friston sense — citing Friston (and indirectly this paper, via the 2502.10955 reference list). The present paper is the simulation-level demonstration that *gain modulation on prediction-error units* is a coherent, dynamically rich computational primitive that reproduces a wide range of empirical phenomena. This justifies PRISM's design choice to multiply prediction errors by a learned per-location gain rather than treating saliency as a separable post-hoc readout.

**Touchpoint 3: active inference as an alternative to RL training.** PRISM v1's policy head (`THESIS.md` §2.9) is a standard PPO actor-critic optimising scalar reward. The user's program ([the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5, "Empirical test plan") envisages eventually testing an active-inference variant in which the policy optimises expected free energy rather than expected reward. Friston et al. 2012 is the closest simulation-level template for what that variant would look like: a hierarchical generative model with prior preferences over observations, action selection by minimisation of $G(\pi)$, and a tonic-dopamine-like precision parameter modulating sensory gain. PRISM v2's hierarchical structure (`PRISM_V2_PROPOSAL.md` §3) is the natural substrate for such a generalisation.

**Touchpoint 4: pathology as a probe of architecture.** The paper's most striking result is that a single parameter $\gamma$ spans a continuum from Parkinsonian under-action to impulsive over-action. For the user's program this offers a methodological idea: the multi-hub system can be probed by selectively up- or down-weighting one hub's broadcast and observing the behavioural consequences. If the RL/precision hub's gain is reduced, the system should over-rely on sensory hubs' priors (perseverative behaviour); if it is increased, the system should over-respond to noisy sensory evidence (impulsive behaviour). This is a falsifiable architectural prediction that can be tested in any multi-hub instance of the program.

**Touchpoint 5: precision and competition.** The user's competition-emergent predictive coding thesis ([the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5) holds that hubs compete for control of the self-attention substrate via their Q/K contributions. Precision-weighting in the Friston 2012 sense is one mechanism by which that competition can be implemented at the substrate level: the hub with the higher current precision wins more of the gradient update. The architectural realisation is identical to the Feedback Transformer's Hadamard-broadcast structure (`§1`): per-state Q/K contributions multiplicatively combined with sensory Q/K. Friston 2012 is the biological warrant for reading that multiplicative combination as precision-weighted Bayesian integration rather than as ad-hoc gating.

**Touchpoint 6: contrast with Glimcher 2011 (intentional).** [glimcher2011_dopamine_rpe](research_db/papers/glimcher2011_dopamine_rpe.md) makes the strongest case for the DA-RPE reading; this paper makes the strongest case for the precision reading. The user's program is explicit that both readings should be retained as live options until empirical work decides between them (or unifies them, as [pezzulo_parr_friston2024_active_inference](research_db/papers/pezzulo_parr_friston2024_active_inference.md) suggests is possible). The pair Glimcher 2011 + Friston 2012 is therefore the minimum reference set for any future writing on the user's RL hub.

## 8. Citations to follow

- `feldman_friston2010_attention_free_energy` — the companion paper that develops the attention-as-precision account specifically; in seed.
- `friston2010_fep_unified_theory` — the parent FEP framework; in seed.
- `pezzulo_parr_friston2024_active_inference` — modern review that partially reconciles the precision and RPE accounts; in seed.
- `babayan_uchida_gershman2018_belief_states_dopamine` — the belief-state generalisation of RPE that narrows the empirical gap with the precision account; in seed.
- `monosov2020_outcome_uncertainty` — uncertainty / salience coding in dopamine and basal forebrain; complements the precision reading; in seed.
- `daw_niv_dayan2005_model_based_vs_free` — model-based vs model-free dichotomy; the natural place to slot active inference between; not yet in seed.
- `matsumoto_hikosaka2009_two_types_dopamine` — heterogeneous dopamine coding (RPE vs salience), one of the empirical anchors for the precision reading; not yet in seed.
- `bromberg_martin_matsumoto_hikosaka2010_dopamine_motivational_value` — review of value vs salience vs alerting in dopamine; relevant for the dual-interpretation argument; not yet in seed.
- `friston_fitzgerald_rigoli_schwartenbeck_pezzulo2017_active_inference_process_theory` — the consolidated process-theory account of active inference that builds on this paper; not yet in seed.
- `niv_daw_joel_dayan2007_tonic_dopamine` — the canonical tonic-dopamine-and-vigour account this paper recovers from precision modulation; not yet in seed.
