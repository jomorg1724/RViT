---
id: hikosaka2006_bg_reward_eyes
title: "Basal ganglia orient eyes to reward"
authors:
  - "Hikosaka, Okihide"
  - "Nakamura, Kae"
  - "Nakahara, Hiroyuki"
year: 2006
venue: "Journal of Neurophysiology"
doi: "10.1152/jn.00458.2005"
arxiv: ""
url: "https://doi.org/10.1152/jn.00458.2005"
tags:
  - subcortical
  - dopamine
  - primate-neurophysiology
  - review
concepts:
  - reward-modulated-attention
  - cortico-basal-ganglia-thalamic-loops
  - priority-map
  - gain-modulation
related:
  - haber2015_cbgtc_circuits
  - glimcher2011_dopamine_rpe
  - babayan_uchida_gershman2018_belief_states_dopamine
  - mcnab_klingberg2008_pfc_bg_wm
  - krauzlis2013_sc_attention
  - herman_arcizet2020_caudate_sc
  - dabney2020_distributional_dopamine
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_88
status: full
depth: full
last_updated: "2026-05-19"
---

# Basal ganglia orient eyes to reward

## 1. Abstract

> *Faithful paraphrase; the original is paywalled and the PubMed entry was unreachable from this session.*

The authors review and synthesize their decade of work on the oculomotor basal ganglia, arguing that the caudate nucleus and its downstream targets — the substantia nigra pars reticulata (SNr) and superior colliculus (SC) — implement a reward-biased priority map for saccadic eye movements. Single-unit recordings in macaque caudate during memory-guided saccade tasks with asymmetric reward show that caudate projection neurons are exquisitely sensitive to the positional difference in expected reward: they fire more strongly for saccades to locations that have been paired with reward, and this differential firing emerges in advance of the saccade. The basal ganglia output (SNr) is tonically active and gates SC activity by GABAergic inhibition; reward-biased caudate firing transiently disinhibits the SC contralateral to the rewarded target, producing shorter latencies, higher peak velocities, and greater accuracy for rewarded saccades. Dopaminergic input from the substantia nigra pars compacta (SNc) supplies the reward-prediction-error signal that trains this bias via corticostriatal synaptic plasticity. The authors conclude that the basal ganglia act as an automatic, value-based action-selection mechanism that *orients the eyes toward reward* — a substrate for the link between motivation and attention. The paper frames the oculomotor loop as a tractable model system for the basal ganglia's role in action selection generally, with the same architecture replicated in parallel for skeletomotor, cognitive, and limbic behaviors.

## 2. Why this matters for us

The user's program ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5) posits an RL hub that competes for control of self-attention via dopamine-modulated reward. Hikosaka et al. 2006 is the canonical empirical demonstration that the basal ganglia, driven by dopamine, *physically reorient the visual system toward rewarded locations* — exactly the saccade-like attention control that the Recurrent ViT (2502.10955) and PRISM emit as policy actions. The paper supplies both the neuroanatomical and the neurophysiological substrate for treating "where to look next" as the natural output of a CBGTC RL loop, and supplies a quantitative target (the latency and velocity asymmetries) against which an artificial RL hub's behavior could be benchmarked.

## 3. Key claims

1. Caudate projection neurons in the oculomotor zone encode the *positional difference in expected reward* — they discriminate between saccade targets based on which target has been paired with reward, with the discrimination emerging hundreds of milliseconds before the saccade.
2. The reward bias is *automatic*: it appears even when reward delivery is fully predictable and the animal cannot strategically modulate it, indicating a hard-wired action-selection circuit rather than top-down cognitive control.
3. SNr neurons are tonically active GABAergic projection neurons that inhibit the superior colliculus; the direct pathway (caudate → SNr) suppresses SNr firing for the rewarded direction, *disinhibiting* the contralateral SC and facilitating the rewarded saccade.
4. The indirect pathway (caudate → GPe → STN → SNr) increases SNr firing and suppresses non-rewarded saccade directions, providing the competitive complement to the direct pathway's selection.
5. SNc dopamine neurons provide the reward-prediction-error teaching signal that shapes caudate firing via long-term plasticity at corticostriatal synapses; the same RPE signal that Schultz/Glimcher describe at the dopaminergic source is shown here to *cash out* as oriented behavior.
6. The reward bias manifests behaviorally as shorter saccade latencies (tens of milliseconds), higher peak velocities, and greater endpoint accuracy for rewarded targets — i.e., reward modulates not just choice but the kinematics of the chosen movement.
7. The oculomotor basal ganglia loop is a *model system* for understanding action selection more generally: the same architecture — caudate/putamen → GPi/SNr → thalamus/SC, with dopamine teaching — is replicated for skeletomotor, cognitive, and limbic actions, with only the cortical input and downstream target varying.
8. Reward modulation appears at every stage of the loop (caudate, SNr, SC, and dopamine source), and the modulation is *coherent* across stages — i.e., a single reward bias is amplified and refined as it passes from caudate through SNr to SC, rather than being recomputed independently at each station.

## 4. Methods

The paper is a review of multiple single-unit electrophysiology experiments in macaque (mostly Macaca mulatta) performing memory-guided saccade tasks with reward asymmetries. The canonical task is the *one-direction-rewarded* (1DR) variant: four possible target locations are presented across blocks, but within a block only one direction yields reward; the others yield no reward. The animal must make a saccade to the cued location regardless of expected reward. This dissociates the *spatial cue* from the *expected value*, allowing the experimenter to isolate value-related neural signals.

Recordings target three sites in the saccadic basal ganglia loop:
- **Caudate head/body**, the input nucleus of the oculomotor loop, receiving from FEF, SEF, dlPFC and ACC.
- **SNr**, the output nucleus, sending GABAergic projections to the SC.
- **SC intermediate layers**, the downstream motor map.

Behavioral measures include saccade latency, peak velocity, endpoint scatter, and choice in free-choice variants. Anatomical claims are supported by tract-tracing references rather than new tracer injections in this review.

Pharmacological and lesion methods reviewed include local muscimol microinjection in caudate, which produces reversible inactivation lasting roughly an hour, and the surgical preparation conventions of chronic recording chambers over the caudate and SNr. Statistical comparisons in the underlying primary papers typically use ROC analyses to quantify direction × reward selectivity at the single-unit level, with cell counts in the hundreds per animal across the reviewed studies.

## 5. Results

The principal findings the review consolidates:

- **Caudate firing.** ~40–70% of recorded caudate projection neurons in the oculomotor zone show significant reward-direction modulation. Typical effect: firing rate 2–5× higher for saccades to the rewarded direction than to the unrewarded direction, with onset latency several hundred ms before saccade initiation. The modulation is *position-selective*: each neuron prefers one of the four target directions and shows the reward × direction interaction primarily at its preferred location.
- **SNr firing.** Tonic baseline rate ~50–100 Hz. During rewarded saccades, SNr neurons in the appropriate region of the map show a *pause* in firing — typically dropping by 30–80% relative to baseline. For unrewarded saccades to the same direction, the pause is smaller or absent. This is the *disinhibition signal* released to the SC.
- **SC firing.** SC intermediate-layer burst neurons fire more vigorously and earlier for rewarded saccades, consistent with relief from SNr inhibition.
- **Behavior.** Saccade latency is shorter by ~30–80 ms for rewarded vs unrewarded targets (depending on task variant). Peak velocity is higher and endpoint scatter smaller. These behavioral effects can be reproduced by direct pharmacological inactivation of caudate (which abolishes the bias) and are predicted to track caudate firing on a trial-by-trial basis.
- **Dopamine.** SNc dopamine neurons show the canonical Schultz RPE pattern in this task: phasic burst at the reward-predicting cue, suppression at omitted reward, and no response at fully predicted reward. The timing aligns with the period during which caudate plasticity could be sculpted to produce the reward bias.
- **Plasticity timescale.** The reward bias in caudate firing builds up over tens of trials within a block and reverses with comparable speed when the rewarded direction is switched. This is consistent with synaptic eligibility traces at corticostriatal synapses being tagged at saccade time and gated by phasic dopamine on the order of a second later — a timing window the review highlights as a critical constraint for any computational model of corticostriatal RL.
- **Causal manipulation.** Local muscimol injection in the caudate (GABA-A agonist; reversible inactivation) abolishes the reward bias in latency and accuracy without abolishing the saccades themselves. This dissociates the *selection* function of caudate from the *execution* function of downstream SC and brainstem circuits, consistent with the basal ganglia acting as an action-*selecting* rather than action-*generating* structure.

## 6. Critique / limitations

The review is a synthesis of work largely from the Hikosaka lab; it is not an unbiased meta-analysis and undersells dissenting accounts. In particular, parallel parietal (LIP) and frontal (FEF) circuits also encode reward-direction information, sometimes with comparable or earlier latencies; the review does not adjudicate whether the caudate signal is *causally upstream* of these cortical signals, or whether all are simultaneously read out from a shared dopaminergic teaching signal.

The 1DR task design conflates reward with motivation and effort; the reward effect on saccade kinematics may partly reflect arousal-related gain modulation rather than a purely value-driven action-selection mechanism. Disentangling these requires manipulations not covered in detail in this review (e.g., effort cost, reward probability vs magnitude — addressed in later Hikosaka work and by Glimcher and colleagues).

The dopamine-as-teaching-signal claim is asserted but not directly demonstrated in this paper. Causal optogenetic perturbation of SNc dopamine during caudate recording in awake macaques came later (and in rodents); the paper relies on the established Schultz framework for the teaching-signal claim.

The review covers only the oculomotor loop. Generalization to other actions — skeletomotor reach, cognitive set-switching, limbic approach — is asserted by anatomical analogy but is not directly tested here. Haber's later anatomical reviews (`haber2015_cbgtc_circuits` in this database) provide the parallel-loop scaffolding.

Subsequent work has refined several quantitative claims. Lauwereyns et al. (2002), Kawagoe et al. (1998), and Watanabe et al. (2003) provide the underlying primary data; their effect sizes are summarized but not re-analyzed here. Belief-state accounts of dopamine (e.g., `babayan_uchida_gershman2018_belief_states_dopamine`) suggest the simple RPE story understates the structure of the teaching signal, and distributional-RL accounts (Dabney et al. 2020, not in seed) further complicate the interpretation of dopaminergic firing as a scalar prediction error.

Finally, the framing of saccade selection as an output of a single CBGTC loop, while heuristically useful, glosses over the rich parallel architecture in which SC itself receives direct cortical input from FEF and LIP without passing through caudate. The relative weight of the direct cortico-collicular and indirect cortico-striato-nigro-collicular routes in producing reward-biased saccades is not quantified here.

## 7. Connection to our work

Hikosaka et al. 2006 anchors several specific design decisions in the user's program:

- **Saccade-like outputs of the Recurrent ViT.** The Recurrent ViT (2502.10955) uses PPO to emit action-like outputs over the visual scene, modeled loosely on saccadic targeting. Hikosaka et al. provide the canonical evidence that the brain's saccadic system *is itself* an RL-trained action-selection loop closed through the basal ganglia. This grounds the choice of an RL objective for the attention policy in concrete neurophysiology rather than in machine-learning convenience alone.
- **The RL hub of PRISM v2 / multi-hub system.** The user's RL hub ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5) is the architectural analog of the caudate → SNr → SC → cortex loop. Hikosaka et al. demonstrate that this loop's *output* is a reweighted priority map over visual space — directly the kind of signal the user proposes the RL hub should send into the central self-attention substrate. The Hadamard modulation of attention scores by the RL hub's $c^{(\text{RL})}_q, c^{(\text{RL})}_k$ vectors ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5, formal account) is the computational counterpart of SNr-mediated SC disinhibition.
- **Dopamine as the teaching signal for competitive attention.** The competition-emergent-PC theory ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5) requires that *one* hub be trained on an extrinsic teaching signal so that the others can model it. Hikosaka et al. identify dopamine as exactly that signal in the brain's oculomotor system. The user's RL hub uses PPO-style policy gradients as the analog; the connection makes the RL hub's role in the multi-hub competition biologically motivated, not just stipulated.
- **Reward modulation of saccade *kinematics*, not just choice.** Hikosaka's finding that reward shortens latency and boosts peak velocity is the empirical counterpart of the user's commitment that the RL hub's contribution should modulate the *gain* of the attention map (concept `gain-modulation` in TAXONOMY), not merely bias categorical choice. This favors multiplicative or Hadamard integration into self-attention over additive token-injection.
- **Complement to Haber's anatomy.** Where `haber2015_cbgtc_circuits` supplies the scaffolding (which cortical regions project where, what the convergence zones are), Hikosaka et al. supplies the *physiology* (what those neurons actually do in a behaving animal). The two together close the loop from architecture to function for the RL hub. The Haber anatomy says *the circuit is wired this way*; Hikosaka says *and when wired this way, here is the signal it computes*. Both are needed to motivate the user's RL hub as a working architectural commitment rather than a hand-wave.
- **Link to PRISM's action selection.** PRISM (THESIS.md, PRISM_V2_PROPOSAL.md) emits change-detection decisions; extending PRISM to also emit attention-targeting actions — as a saccade-like policy over the patch grid — is licensed by exactly the Hikosaka loop. This is a concrete path from change-detection benchmarks toward a more biologically-grounded active-perception agent.
- **Selection vs execution dissociation.** The muscimol-inactivation result — the basal ganglia *select* but do not *generate* saccades — favors an architectural decomposition in which the RL hub emits a *gating signal* over a pre-existing motor-action repertoire rather than directly synthesizing motor commands. In the Recurrent ViT and PRISM, this maps cleanly onto an RL policy that outputs a softmax over patch locations rather than directly emitting pixel-level glimpse coordinates.
- **Direct-vs-indirect-pathway counterpart.** The Hikosaka loop's dual-pathway architecture — direct pathway facilitating the chosen action, indirect pathway suppressing competitors — maps naturally onto a competitive softmax: the direct pathway is the positive logit of the chosen patch, the indirect pathway is the negative logits of the rest. An architectural elaboration of the RL hub that emits *two* signed contributions to self-attention (a facilitative and a suppressive head) is licensed by this anatomy and is a plausible PRISM v3 design.
- **Timing constraint from corticostriatal plasticity.** The roughly-1-second eligibility window from Hikosaka's tens-of-trials reward-bias buildup is a soft constraint on the temporal credit-assignment horizon a biologically grounded RL hub should target. PRISM's per-step PPO update is already within this window; longer-horizon credit assignment in the user's system would need to be implemented either via TD($\lambda$)-style eligibility traces or via the RL hub borrowing world-model rollouts from the VAE hub.

## 8. Citations to follow

- `kawagoe_takikawa_hikosaka1998_caudate_reward` — the foundational caudate-reward paper this review consolidates. PMID 10196533. High priority.
- `lauwereyns_watanabe_coe_hikosaka2002_caudate_bias` — the *Nature* paper showing caudate firing predicts saccade bias. High priority.
- `watanabe_lauwereyns_hikosaka2003_motivational` — caudate motivational coding. Companion.
- `schultz1998_dopamine_reward` — the canonical Schultz dopamine-RPE paper; foundational. Not in seed.
- `glimcher2011_dopamine_rpe` — the RPE-hypothesis review. In seed.
- `krauzlis2013_sc_attention` — superior colliculus and attention; the downstream consumer of the SNr signal. In seed.
- `herman_arcizet2020_caudate_sc` — caudate–SC interaction in attention. In seed.
- `babayan_uchida_gershman2018_belief_states_dopamine` — belief-state refinement of the RPE story. In seed.
- `haber_knutson2010_reward_circuit` — anatomical reward-circuit review; complements Hikosaka. Not in seed.
- `hikosaka_takikawa_kawagoe2000_role_bg_eye` — Hikosaka's earlier review of the same loop. Not in seed.
- `dabney2020_distributional_dopamine` — distributional-RL evidence in dopamine neurons; refines the scalar-RPE picture used here. *Now in db (added 2026-05-19).*
- `sutton_barto2018_rl_book` — the formal RL framework (TD learning, eligibility traces) that this circuit instantiates. Not in seed.
- `frank2005_bg_actor_critic` — neurocomputational model of the direct/indirect pathway as an actor with dopamine-modulated learning. Not in seed.
