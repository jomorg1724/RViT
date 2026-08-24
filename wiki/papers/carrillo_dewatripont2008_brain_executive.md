---
id: carrillo_dewatripont2008_brain_executive
title: "Promises, promises,..."
authors:
  - "Carrillo, Juan D."
  - "Dewatripont, Mathias"
year: 2008
venue: "Economic Journal"
doi: "10.1111/j.1468-0297.2008.02175.x"
arxiv: ""
url: "https://doi.org/10.1111/j.1468-0297.2008.02175.x"
tags:
  - theoretical-essay
  - review
concepts:
  - coalition-resource-competition
related:
  - lee2008_game_theory_neural
  - edelman1987_neural_darwinism
  - schmidhuber2015_learn_to_think
  - hawkins2021_thousand_brains
relevance_to:
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-15"
---

# The brain as a Central Executive System

## 1. Abstract

Carrillo and Dewatripont develop a "brain-as-organization" framework in which the agent is modelled not as a unitary maximiser but as an internal hierarchy of sub-agents with partially conflicting objectives, coordinated through delegation, monitoring, and incentive structures borrowed from the economics of organisations. A Central Executive System (CES) — identified loosely with prefrontal cortex — acts as a principal that delegates execution to specialised modules (sensory, affective, motor, mnemonic) and uses imperfect, costly monitoring plus internal "promises" (commitments) to align the modules' actions with longer-run goals. The paper's contribution is methodological as much as substantive: it imports contract theory, delegation, and commitment-device analysis from organisational economics into a normative model of how an internally fragmented brain reaches behaviour, and argues that many cognitive phenomena (self-control failures, internal deal-making, motivated belief) are equilibrium outcomes of this principal–agent structure rather than departures from rationality.

## 2. Why this matters for us

The user's architectural program (`threads/the_user_architectural_program.md`, §5) commits to a multi-hub system whose hubs (MSI, RL, VAE, default-mode, …) compete for control of a shared self-attention substrate. Carrillo & Dewatripont supply the *organisational-economics vocabulary* for that competition: delegation under asymmetric information, monitoring costs, incentive design, and credible commitment. Their CES is the closest published economics analogue of what the user's central self-attention map is doing — adjudicating between sub-agent proposals — and their machinery for analysing internal contracts gives us a principled way to specify (and later test) what counts as "winning" attention for a hub. It is also a useful brake on naive utilitarian readings of the brain: behaviour is not the output of a single objective but of a negotiated equilibrium, which is precisely what the multi-objective hub system is supposed to instantiate.

## 3. Key claims

1. The brain is more productively modelled as an *organisation of sub-agents* than as a unitary expected-utility maximiser; intra-personal conflict is the rule, not the exception.
2. A Central Executive System sits as a principal over specialised modules; it cannot directly observe their internal states and must rely on imperfect signals and costly monitoring.
3. Standard organisational-economics tools — delegation, incentive compatibility, commitment, reputation — translate to the brain and explain otherwise puzzling phenomena (procrastination, self-deception, willpower, motivated reasoning).
4. Internal "promises" — pre-commitment devices binding the future self — are an equilibrium response to time-inconsistent preferences between modules with different temporal discount profiles.
5. Behaviour observed at the whole-organism level is the *equilibrium outcome* of internal bargaining; it generally fails to maximise any single sub-agent's objective and is not pathological merely because it deviates from a unitary-rational benchmark.
6. The framework is normatively neutral: it does not endorse any particular module as "the real self", and treats the CES as one player among several with limited authority rather than as an executive dictator.

## 4. Methods

The paper is a theoretical essay rather than an empirical study. The authors review and synthesise three strands: (i) the multi-self / dual-self literature in economics (Schelling, Thaler-Shefrin, Bénabou-Tirole, Loewenstein), (ii) the principal–agent and contract-theory literature on delegation under asymmetric information (Holmström, Tirole), and (iii) the neuroeconomics evidence for functionally distinct modules with distinct objectives (especially limbic-vs-prefrontal valuation studies of intertemporal choice). They sketch reduced-form models in which a CES principal contracts with one or more module agents whose private states (drive, fatigue, affect) are unobservable. Equilibrium concepts are standard Bayesian Nash / Perfect Bayesian; the analytical contribution is mapping organisational primitives onto neural ones rather than proving new theorems. There are no experiments, no datasets, and no simulations — the work is conceptual and integrative.

## 5. Results

There are no quantitative results in the empirical sense. The paper's "results" are a set of conceptual mappings and predictions:

- A delegation model with hidden module-state and costly monitoring reproduces the observed pattern that willpower is *limited and depletable*: the CES cannot continuously override modules without paying a monitoring cost.
- Time-inconsistent intertemporal choice (hyperbolic discounting, present bias) emerges naturally when modules have heterogeneous discount factors and the CES has imperfect commitment technology.
- Internal commitment devices (public pledges, bright-line rules, automatic-debit savings) are predicted to be more prevalent in domains where module-CES conflict is large and external monitoring is cheap, matching observed self-control technologies.
- Motivated belief and self-deception are equilibria in which the CES strategically withholds information from itself / its modules to preserve incentive properties of internal contracts.
- The framework predicts that lesions to the CES (dorsolateral / ventromedial PFC damage) should produce not "irrationality" per se but *failures of intra-personal coordination* — exactly the pattern reported for PFC patients in the neuroeconomics literature the authors cite.

## 6. Critique / limitations

The framework is largely *programmatic* — a vocabulary and a stance rather than a falsifiable model. Several specific concerns:

- **Identification of the CES is loose.** The paper conflates several PFC roles (dorsolateral working memory, ventromedial valuation, anterior cingulate conflict-monitoring) under a single "executive" label. Subsequent neuroeconomics work (Glimcher; Padoa-Schioppa; Kable & Glimcher) suggests valuation is distributed rather than centralised, weakening the principal–agent metaphor where the principal sits in one anatomical place.
- **The modules are stipulated rather than derived.** Why exactly *these* sub-agents (limbic / cognitive / motor) and not some other partition? Without a principled decomposition the framework risks being a redescription of whichever phenomenon needs explaining.
- **Empirical content is thin.** Most predictions (willpower depletion, motivated belief, commitment devices) were already in the literature the paper synthesises; the novel contribution is unifying them, not generating new testable predictions. The Baumeister "ego depletion" line they implicitly support has since suffered substantial replication failures (Hagger et al. 2016).
- **The "promises" mechanism leans on the CES having more commitment technology than the modules.** It is unclear why a CES that is itself just another module should be able to credibly bind the others; the asymmetry is asserted rather than derived.
- **No formal account of the attention bottleneck.** The paper assumes the CES can selectively engage with modules but does not model the bottleneck itself. For our purposes this is the most consequential gap: the user's architectural program is precisely about *how* the central substrate adjudicates, which Carrillo & Dewatripont leave at the level of metaphor.

These limitations do not undermine the framing's usefulness; they bound what the framing can be load-bearing for.

## 7. Connection to our work

Carrillo & Dewatripont are the cleanest published statement of the *organisational stance* underlying the multi-hub multi-objective system in `the_user_architectural_program.md` §5 (competition-emergent predictive coding) and the multi-hub commitment in `multi_hub_multi_objective_system.md` (concept). Three specific connections:

**(i) The central self-attention map as CES.** In the user's program, the global self-attention map at each layer is the substrate over which hubs compete for representational bandwidth (see thread §5 "Formal account of the competition", $q_i = s_{q,i} \odot (c^{(\text{RL})}_{q,i} + c^{(\text{dec})}_{q,i})$). Carrillo & Dewatripont's CES gives this substrate an organisational reading: the attention map is not a hub itself but the *institution* through which hubs contract for influence. Treating it this way clarifies the design decision in the Feedback Transformer (thread §1): the substrate must be neutral with respect to hub identity but informative about their proposals, exactly the role of a principal with imperfect monitoring.

**(ii) Hub-level objectives as private agent types.** The user's hubs (MSI, RL, VAE) have hub-specific losses (cf. PRISM v2's per-objective heads). Carrillo & Dewatripont's framework recasts these as the *private types* of the agents. The competition-emergent predictive-coding thesis (thread §5, step 3) — that top-down feedback functions as opponent modelling — is then directly equivalent to the CES learning the modules' private types through repeated interaction. This is a strict generalisation of the user's account, and it gives a principled name (mechanism design) for the kind of training objective that should select for honest hub feedback.

**(iii) Diminishing feedback into deeper layers as a commitment device.** Thread §3 ("Diminishing feedback into deeper layers is by design") motivates the power asymmetry between layers by analogy to dual-timescale RNNs. Carrillo & Dewatripont supply a complementary reading: deeper layers' insulation from feedback is a *credible commitment* technology — they cannot be lobbied at every step, so their slow updates are protected from short-horizon module pressure. This matches the role of the CES as a commitment device for the long-run self. PRISM v2's slow/fast memory (`PRISM_V2_PROPOSAL.md` §3.3) inherits this design implicitly; the Carrillo-Dewatripont reading makes the *reason* explicit.

The framework also licenses a falsifiable test that is more specific than the one in thread §5: train the multi-hub system, then probe whether the gating that wins attention for a hub depends on the *predicted* type of competing hubs (consistent with the principal-agent reading) or only on each hub's own state (consistent with a non-strategic readout). If the former, the system is doing the kind of mechanism design Carrillo & Dewatripont posit; if the latter, the organisational metaphor is decorative.

In sum: this paper does not give us equations to plug in, but it gives us the right *category* — internal organisation under asymmetric information — for the architectural commitments the user has already made on other grounds. Lee (2008, game-theoretic neural decision-making) and Schmidhuber (2015, coupled controller-model RNNs) are the two adjacent entries; Edelman 1987's Neural Darwinism is the deeper progenitor.

## 8. Citations to follow

- thaler_shefrin1981_self_control — economic-self-control planner-doer model; direct ancestor of CES principal-agent framing.
- benabou_tirole2002_self_confidence — motivated belief and self-deception as equilibrium; cited by Carrillo & Dewatripont and parallel to the multi-hub honesty problem.
- loewenstein1996_visceral_factors — visceral / affective module as economic agent; the prototype of a "hot" hub.
- mcclure2004_separate_neural_systems — fMRI evidence for dual valuation systems (limbic vs lateral PFC); the empirical hook for the CES partition.
- kable_glimcher2007_neural_correlates_subjective_value — distributed-valuation evidence that complicates a single-CES reading; useful as a critical counterweight.
- hagger2016_ego_depletion_metaanalysis — replication failure for willpower-as-depletable-resource; bears on the empirical robustness of the framework.
- bernheim_rangel2004_addiction_cue — internal-conflict model of addiction; a tractable special case of the CES framework.
- fudenberg_levine2006_dual_self — formal dual-self model with patient long-run self and impulsive short-run self; closest formal companion.
- brocas_carrillo2008_brain_economic — the authors' own companion paper laying out the broader economics-of-the-brain program; adds the formal models the present paper sketches.
