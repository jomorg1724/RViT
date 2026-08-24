---
id: babayan_uchida_gershman2018_belief_states_dopamine
title: "Belief state representation in the dopamine system"
authors:
  - "Babayan, Benedicte M."
  - "Uchida, Naoshige"
  - "Gershman, Samuel J."
year: 2018
venue: "Nature Communications"
doi: "10.1038/s41467-018-04397-0"
arxiv: ""
url: "https://doi.org/10.1038/s41467-018-04397-0"
tags:
  - dopamine
  - reinforcement-learning
  - primate-neurophysiology
concepts:
  - precision-weighting
  - reward-modulated-attention
  - cortico-basal-ganglia-thalamic-loops
  - bayesian-cue-integration
  - world-model-emergence
related:
  - haber2015_cbgtc_circuits
  - glimcher2011_dopamine_rpe
  - friston2010_fep_unified_theory
  - feldman_friston2010_attention_free_energy
  - botvinick2020_deep_rl_neuro
  - monosov2020_outcome_uncertainty
  - pezzulo_parr_friston2024_active_inference
  - dabney2020_distributional_dopamine
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_114
status: full
depth: full
last_updated: "2026-05-19"
---

# Belief state representation in the dopamine system

## 1. Abstract

Learning to predict future outcomes is critical for driving appropriate behaviors. Reinforcement learning (RL) models have successfully accounted for such learning, relying on reward prediction errors (RPEs) signaled by midbrain dopamine neurons. It has been proposed that when sensory data provide only ambiguous information about which state an animal is in, it can predict reward based on a set of probabilities assigned to hypothetical states (called the belief state). Here we examine how dopamine RPEs and subsequent learning are regulated under state uncertainty. Mice are first trained in a task with two potential states defined by different reward amounts. During testing, intermediate-sized rewards are given in rare trials. Dopamine activity is a non-monotonic function of reward size, consistent with RL models operating on belief states. Furthermore, the magnitude of dopamine responses quantitatively predicts changes in behavior. These results establish the critical role of state inference in RL.

## 2. Why this matters for us

The user's competition-emergent-PC thesis ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5) predicts that implicit world-models / belief-states should arise from inter-hub competition. Babayan et al. supplies the cleanest single-cell-level evidence that the brain's canonical RL machinery — the VTA dopamine system — does not operate on raw sensory input but on a *belief state*, a posterior over hidden environmental states. Two implications matter for the multi-hub architecture. First, the RL hub's "reward" signal is dopaminergic and is itself a function of belief, not of stimulus — so the RL hub's gradient already encodes the agent's uncertainty about which world-state it occupies. Second, the same dopamine signal predicts subsequent behavioral changes quantitatively (Fig. 4c, signed-rank p = 0.032 in favor of the belief-state model), grounding the user's precision-weighted-attention argument: the magnitude of the dopaminergic teaching signal scales with how informative the current evidence is about hidden state. This is the empirical anchor for treating dopamine as a precision signal that the RL hub broadcasts back into the central self-attention substrate.

## 3. Key claims

1. Under state uncertainty, normative RL theory requires that prediction errors be computed against a belief state — a posterior distribution over hidden states given the current sensory evidence — rather than against a single observable state.
2. Standard single-state RL predicts dopamine RPEs that scale *linearly* (monotonically) with reward magnitude; belief-state RL predicts a *non-monotonic* pattern in which mid-sized rewards probed across two trained states elicit smaller RPEs than rewards near either trained reward magnitude.
3. VTA dopamine population activity (fiber photometry, GCaMP6f) in 11 DAT-Cre mice shows the predicted non-monotonic pattern on trial 2 of intermediate-reward blocks, while showing the expected monotonically-increasing response on trial 1 (when no within-block evidence has yet accumulated).
4. The non-monotonic dopamine pattern is reproduced quantitatively only by RL models that compute prediction errors on belief states, not by single-state TD models — BIC and protected-exceedance-probability model selection both favor the belief-state RL with two free initial priors.
5. The belief-state value function — fit only to dopamine, not to behavior — independently predicts the mouse's anticipatory licking rate better than the single-state value function (signed-rank p = 0.032), demonstrating that belief states drive both neural RPE and behavior.
6. The result holds across recording configurations (VTA cell bodies from transgenic and viral GCaMP6f expression; dopamine terminals in ventral striatum), three baseline-correction methods, and peak-vs-mean response quantifications — i.e., it is robust.

## 4. Methods

**Task.** Eleven DAT-Cre × Ai9(tdTomato) mice — five additionally crossed to Ai95D (GCaMP6f reporter); six receiving AAV9-Syn-Flex-GCaMP6f viral injection into VTA — performed a head-fixed Pavlovian conditioning task. Each trial: a 2 s block-start tone, then (3 s later) the first of five identical trials, each with 1 s odor (CS, same odor regardless of block), a 1 s delay, then a fixed-volume sucrose-water reward. Two training blocks were used: s1 (1 μL, "small") and s2 (10 μL, "big"), randomly alternating with 50% transition probability. After ≥20 days of training, every other session 10% (3 of 30) of training blocks were replaced by intermediate-reward blocks (2, 4, 6, or 8 μL), each intermediate volume appearing at most once per day. Each mouse experienced 3980 ± 213 training-block trials and 42 ± 6 trials of each intermediate reward.

**Recording.** Fiber photometry with a 473 nm laser excited GCaMP6f in VTA dopamine neurons (cell bodies, n = 7) or in dopamine terminals in ventral striatum (n = 4); a parallel 561-channel tracked tdTomato as a motion control (no correction applied because prior work had ruled out artefacts in this rig). Signals digitized at 1 kHz; dF/F computed against a 1 s pre-odor baseline; phasic CS and US responses defined as mean activity in the 1 s post-onset window (peak-response analysis in supplement gave identical conclusions).

**Computational models.** Trial-level (not real-time) TD. Standard RL: a single state s with value V(s); update δ_t = r_t − V(s), V(s) ← V(s) + α δ_t. Belief-state RL: posterior b(s) = P(r|s)P(s)/P(r), with P(r|s) = N(r; r̄_s, σ²) gaussian likelihood centered on the typical reward of state s with sensory-noise variance σ²; value approximated as V(b_t) = w_1 b_t(s_1) + w_2 b_t(s_2); weight update Δw = α δ_t b_t. Four belief-state variants were tested, differing only in how the prior P(s) was set (fixed at 0.5; one free; two free; three free with an explicit "intermediate" state). All models additionally fit a coefficient β mapping theoretical RPE to GCaMP magnitude. Model comparison used BIC and Bayesian model selection (protected exceedance probability, Rigoux 2014; Stephan 2009).

## 5. Results

- **Trial 1, training blocks (Fig. 2):** Anticipatory licking on trial 1 of a new block is similar across block types (two-way ANOVA, no effect of current or previous block, p > 0.16). Dopamine *cue* response is unaffected by the upcoming block but reflects the previous block (main effect of previous block on trial 1, p = 0.0025). Dopamine *reward* response on trial 1 shows main effects of both current (p < 0.001) and previous (p = 0.038) block — i.e., the RPE on trial 1 carries the prior.
- **Trial 1, intermediate-reward blocks (Fig. 3a–c):** Dopamine reward response increases monotonically with reward magnitude (1 → 10 μL), as expected for a first-encounter trial with no within-block belief.
- **Trial 2 (Fig. 3e–g):** The dopamine reward response is *non-monotonic*: smaller intermediate rewards (2 and 4 μL) elicit smaller responses than larger intermediate rewards (6 and 8 μL), and the responses to 4 μL fall below those of 1 μL while those of 8 μL fall below those of 10 μL — the qualitative "M-shape" predicted by belief-state RL (Fig. 1d). Polynomial fits give highest adjusted R² for a cubic (trial 2) and a linear (trial 1) fit (Supplementary Fig. 7).
- **Behavior tracks dopamine (Fig. 3d, h):** Anticipatory-lick change trial 1 → 2 is monotonic in reward; change trial 2 → 3 is non-monotonic, mirroring the dopamine pattern. Trial-by-trial Pearson correlations between dopamine reward response and next-trial anticipatory-lick change are significant for every within-block transition (p < 2.5 × 10⁻³).
- **Model fits (Fig. 4):** Both models fit trial 1; only belief-state RL fits trial 2. BIC and protected exceedance probability both favor the belief-state RL with two free initial priors over four variants and the standard RL. Crucially, belief-state values fit *only to dopamine* predict anticipatory licking better than standard-RL values (signed-rank statistic = 9, p = 0.032).
- **Generality:** Effects hold for VTA cell bodies (transgenic and viral) and ventral-striatum terminals (n = 5, 2, 4 respectively), and across three baseline-normalization methods.

## 6. Critique / limitations

The task design conflates "reward size" with "state identity" — the two reference states differ *only* in their reward distribution. This means the inferred belief state and the reward expectation are nearly the same quantity, and the paper cannot distinguish between (a) dopamine encoding RPE-on-belief and (b) dopamine encoding RPE against a flexible mixture-of-Gaussians value distribution without a discrete latent-state representation. A stronger test would dissociate state identity from reward magnitude (e.g., two states with the same mean reward but different variance, or different temporal structure).

The "belief state" is computed by the experimenter via Bayes' rule on a known generative model. The paper does not show that the brain implements Bayesian inference — only that the *output* of optimal inference quantitatively matches dopamine. Suboptimal or heuristic state-inference schemes (e.g., a Kalman-style running estimate, a delta-rule with a state-dependent context cue) are not ruled out.

Calcium imaging averages over hundreds of dopamine neurons and cannot distinguish subpopulations. Subsequent work has shown striatal-target-specific dopamine subcircuits (Menegas 2017; Lerner 2015) and "value-prediction-error" vs "sensory-prediction-error" dopamine subsets (Takahashi 2017); the present recordings cannot say which subset carries the belief-state signal.

The phasic-only analysis explicitly discards tonic dopamine, which is precisely the timescale most relevant for uncertainty / precision signalling in some Friston/Yu accounts. The paper acknowledges the bleaching constraint but cannot speak to whether belief-state representation extends to tonic levels.

The source of belief-state input to VTA is not identified. The Discussion nominates OFC (Wilson et al. 2014; Sadacca et al. 2016) and hippocampus (Gershman 2010, 2014) on functional grounds, but no anatomical or perturbation evidence is provided here.

## 7. Connection to our work

This paper is the empirical hinge that connects three components of the user's architectural program to the canonical RL substrate documented in [haber2015_cbgtc_circuits](haber2015_cbgtc_circuits.md).

**(a) RL hub's signal is a belief-state RPE, not a stimulus-RPE.** The user's RL hub ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5) is meant to interact with MSI and VAE hubs through a shared self-attention substrate. Babayan establishes that the dopaminergic teaching signal the RL hub broadcasts is already a function of the *agent's inferred world-state*, not of raw input. Architecturally, this means that wiring an RL hub into the system on the assumption that its gradient is a function of (state, action, reward) is incorrect; the gradient is a function of (belief over states, action, reward). The corresponding implementation in the multi-hub system is that the RL hub must *maintain its own posterior over latent task states* — i.e., its own memory state — exactly as the user already specifies. Babayan supplies the empirical authority for that commitment.

**(b) World-model-emergence from competition.** The user's central testable claim ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5, "Empirical test plan") is that an implicit world-model emerges from inter-hub competition. Babayan demonstrates that exactly such an implicit world-model — a discrete two-state belief representation, never explicitly trained — is present in mice's VTA dopamine signal after Pavlovian conditioning on two reward magnitudes. The mice were *never* told there were two states; the structure was inferred from the reward distribution. This is a biological existence proof for the world-model-emergence concept the user wants to test in silico, and it identifies the dopamine system as the natural location to *read out* such an emergent model in artificial multi-hub architectures.

**(c) Dopamine as precision-weighting on attention.** Under Feldman & Friston (2010, [feldman_friston2010_attention_free_energy](feldman_friston2010_attention_free_energy.md)), attention is the inverse of expected uncertainty (precision). Babayan's quantitative result — dopamine magnitude predicts both belief-state value and anticipatory-licking change — supports treating dopamine as the brain's precision broadcast. In the user's Feedback Transformer ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §1), per-state Q/K/V contributions from the RL hub multiplicatively shape the attention map. The biological correlate is that VTA dopamine modulates corticostriatal plasticity in proportion to belief-state uncertainty (precision), thereby shaping which sensory streams the rest of cortex listens to.

**(d) CBGTC-loop belief-state computation.** Reading Babayan alongside Haber ([haber2015_cbgtc_circuits](haber2015_cbgtc_circuits.md)) gives the full RL-hub picture: belief states are likely computed in OFC and/or hippocampus (per Babayan §Discussion), routed through the ventral striatum (Haber's ventral-striatum reward-evaluation hub), modulated by VTA dopamine carrying belief-state RPE (Babayan, Fig. 4), and fed back to cortex via thalamic relays (Haber's CBGTC closure). This is the user's RL hub at biological resolution. The connection it does *not* establish — but is compatible with — is that the same RPE signal could implicitly train MSI and VAE hubs to predict the RL hub's behavior, the user's strategic-prediction-error claim.

This paper is most relevant to PRISM v2's reward-modulated extensions and to any future Recurrent ViT variant that takes a reward or auxiliary-loss signal as input.

## 8. Citations to follow

- `schultz_dayan_montague1997_dopamine_rpe` — the canonical RPE theory of dopamine; cited as ref. 1 and is the foundation Babayan extends. Not yet in seed.
- `starkweather_babayan_uchida_gershman2017_hidden_state_inference` — companion paper from the same labs on temporal hidden-state inference in dopamine RPE (Nat Neurosci 20:581). The most direct prior work; should be added.
- `wilson_takahashi_schoenbaum_niv2014_ofc_task_space` — OFC as a cognitive map of task space; the strongest candidate substrate for the belief-state input to VTA. Should be added.
- `sadacca_jones_schoenbaum2016_inferred_cached_value` — VTA dopamine computes both inferred and cached value-prediction errors; refines and extends Babayan. Should be added.
- `stalnaker2016_cholinergic_interneurons_state` — cholinergic interneurons in dorsomedial striatum track current-state beliefs; the striatal-circuit substrate for state inference. Should be added.
- `takahashi2017_sensory_feature_prediction_errors` — dopamine errors over sensory features rather than reward magnitude; opens a path to multi-dimensional belief states (Babayan suggests this future direction). Should be added.
- `eshel2016_common_response_function` — population-level dopamine RPE; the methodological precedent for the photometry analyses here. Should be added.
- `lak_nomoto_keramati_sakagami_kepecs2017_choice_confidence` — dopamine signals belief in choice accuracy during perceptual decisions; the visual-cue analog to Babayan's reward-magnitude belief states. Should be added.
