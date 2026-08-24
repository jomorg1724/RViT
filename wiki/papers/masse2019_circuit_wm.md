---
id: masse2019_circuit_wm
title: "Circuit mechanisms for the maintenance and manipulation of information in working memory"
authors:
  - "Masse, Nicolas Y."
  - "Yang, Guangyu R."
  - "Song, H. Francis"
  - "Wang, Xiao-Jing"
  - "Freedman, David J."
year: 2019
venue: "Nature Neuroscience"
doi: "10.1038/s41593-019-0414-3"
arxiv: ""
url: "https://doi.org/10.1038/s41593-019-0414-3"
tags:
  - prefrontal-cortex
  - working-memory
  - neuro-ai-bridging
  - recurrent-networks
concepts:
  - working-memory-persistent-activity
  - recurrence-for-temporal-dynamics
  - slow-fast-recurrence
related:
  - mante2013_context_dependent_pfc
  - funahashi1989_mnemonic_dlpfc
  - goldman_rakic1995_cellular_wm
  - constantinidis2018_persistent_activity
  - riley_constantinidis2016_pfc_persistent
  - laughlin1998_metabolic_cost
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# Circuit mechanisms for the maintenance and manipulation of information in working memory

## 1. Abstract

Working memory (WM) — the short-term maintenance and manipulation of behaviorally relevant information — is thought to depend on persistent neuronal firing in prefrontal cortex (PFC). Recent experimental and theoretical work has challenged this view by proposing that information can also be stored in "activity-silent" hidden states such as patterns of short-term synaptic plasticity (STSP). Masse, Yang, Song, Wang & Freedman train recurrent neural networks (RNNs) endowed with biologically constrained short-term synaptic facilitation and depression on a battery of WM tasks ranging from simple delayed-match-to-sample (DMS) maintenance to active manipulation (delayed-match-to-rotated-sample, DMRS; A-B-B-A; A-B-C-A; delayed cue; dual DMS), and dissect how the trained circuits actually store and transform their contents. The key result is that the *form* of WM encoding is task-dependent: pure maintenance tasks are solved with little or no delay-period persistent activity, with information stored almost entirely in STSP, whereas manipulation tasks recruit progressively stronger persistent activity that scales with the cognitive demands of the transformation. The two regimes coexist in a hybrid code in which STSP and persistent firing share the load, and the partition between them is dissociable by selective ablation. The findings reconcile the long-standing persistent-activity literature (Funahashi 1989; Goldman-Rakic 1995; Riley & Constantinidis 2016; Constantinidis 2018) with activity-silent alternatives (Mongillo 2008; Stokes 2015) by showing both arise from the same recurrent substrate under different task demands, with the regime determined by the interaction of task structure and a biologically motivated metabolic cost on activity.

## 2. Why this matters for us

Masse et al. is the cleanest existing demonstration that *recurrent networks trained on working-memory tasks self-organize into the same compositional code* — a slow synaptic component for maintenance, a fast persistent-activity component for manipulation — that the user's program postulates as a first-class architectural commitment. It is the direct precedent for the Recurrent ViT (2502.10955) and the PRISM ConvGRU learning WM-like dynamics from a change-detection objective rather than being hand-engineered, and the transient-vs-persistent decomposition it documents maps almost one-to-one onto PRISM v2's slow/fast memory architecture. Just as importantly, the paper supplies the conceptual bridge between persistent-activity accounts of WM (Funahashi 1989; Goldman-Rakic 1995; Riley & Constantinidis 2016; Constantinidis 2018) and activity-silent accounts (Mongillo 2008; Stokes 2015): both regimes are recovered from a single trained recurrent substrate, and the regime that emerges is dictated by what the task asks the network to do. That is the dialectical resolution PRISM v2 needs in order to claim its slow/fast memory is biologically motivated rather than ad hoc. Beyond the architectural takeaway, Masse's methodological move — *let* the network choose its encoding regime under a metabolic-cost prior, then dissect the chosen regime — is the template the user's empirical program should follow when evaluating the GridCell RNN stack, the iterative VAE rollout, or any future multi-hub instance.

## 3. Key claims

1. **Short-term synaptic plasticity can solve simple WM maintenance tasks with negligible persistent activity.** In delayed-match-to-sample (DMS) with a short delay, five of six trained networks store the sample stimulus almost entirely in synaptic efficacies; neuronal firing rates during the delay are near baseline.
2. **Active manipulation of WM contents requires persistent activity.** Delayed-match-to-rotated-sample (DMRS) and similar tasks in which the stored stimulus must be transformed before comparison cannot be solved by STSP alone; persistent firing reliably emerges from learning.
3. **Persistent-activity strength scales with manipulation demand.** Across nine task variants of graded transformation complexity, the end-of-delay persistent-activity magnitude correlates very strongly (Spearman R = 0.93, P < 0.001) with the amount of manipulation the task requires.
4. **WM is encoded hybrid by default.** For manipulation tasks all twenty trained networks adopt a hybrid code in which both STSP and persistent activity carry decodable stimulus information, and ablating either component degrades performance.
5. **The two components play distinct computational roles.** STSP holds a faithful trace of the *original* sample; persistent activity holds a *prospective* code aligned with the upcoming behavioral comparison. In DMRS, inhibitory neurons with depressing synapses show asymmetric tuning rotated toward the test direction — a prospective recoding of the stored stimulus.
6. **Trained recurrent circuits reproduce the empirical task-dependence of persistent activity.** The model's regime shift from low to high delay-period activity as a function of task demand mirrors the heterogeneity observed in primate PFC across studies (Funahashi 1989; Constantinidis 2018), reconciling reports of strong and weak persistent activity within a single mechanistic framework.
7. **The hybrid code is dissociable.** Selective shuffling ablations targeting either the synaptic state or the firing-rate state degrade performance asymmetrically across task types: synapses are necessary for maintenance, firing rates for manipulation. The two substrates are not redundant.
8. **Inhibitory units with depressing synapses are the engine of prospective recoding.** The asymmetric tuning rotation is not a network-wide phenomenon but is concentrated in a specific cell class — a structural-functional correspondence that the rate model can articulate explicitly.

## 4. Methods

**Network architecture.** A single recurrent layer of 100 leaky-integrator rate units (80 excitatory, 20 inhibitory; Dale's law enforced) with time constant $\tau = 100$ ms simulated at $\Delta t = 10$ ms. Inputs: 24 motion-direction-tuned neurons with cosine tuning curves plus rule/fixation cues. Outputs: 3 decision units (fixate / match / non-match). The update equation is the standard $\tau \dot{r} = -r + W^{rec}(S \odot r) + W^{in} u + b + \eta$, where $S$ is the per-synapse short-term efficacy described below and $\eta$ is Gaussian noise injected into the membrane current.

**Short-term synaptic plasticity.** Following Mongillo et al. 2008 and the Markram–Tsodyks tradition, each recurrent synapse $i$ has a multiplicative efficacy $S_i(t) = x_i(t) \cdot u_i(t)$, where $x_i \in [0, 1]$ tracks available neurotransmitter (depression) and $u_i \in [0, 1]$ tracks release probability (facilitation). Half of the recurrent neurons project *facilitating* synapses ($\tau_x = 200$ ms, $\tau_u = 1500$ ms, $U = 0.15$); the other half project *depressing* synapses ($\tau_x = 1500$ ms, $\tau_u = 200$ ms, $U = 0.45$). All synaptic state variables are smooth, differentiable functions of presynaptic activity, so STSP is folded into the BPTT graph and the whole circuit is trainable end-to-end. Crucially, $S$ is *not* a learned parameter — its kinetics are fixed; what the network learns is how to *exploit* the prebuilt slow channel.

**Tasks.** A battery of WM paradigms ordered by manipulation demand: (i) **DMS** — delayed match-to-sample, the canonical pure-maintenance paradigm of Funahashi-style oculomotor delay. (ii) **DMRS** — delayed match-to-rotated-sample; the stored direction must be mentally rotated by 90° before comparison. (iii) **A-B-B-A** and **A-B-C-A** — sequential matching with intervening distractors, requiring the network to keep the sample distinguishable from one or two distractor stimuli. (iv) **Delayed-cue** — the matching rule (DMS vs DMRS) is revealed only after the delay, so the network cannot prospectively recode during the delay and must hold a faithful copy. (v) **Dual DMS** — two stimuli must be remembered and a cue selects which is to be matched. The graded difficulty across these tasks is what supports the Spearman correlation in §5.

**Training.** Adam optimizer (learning rate 0.02), cross-entropy loss on the decision outputs, L2 firing-rate regularizer ($\beta = 0.02$) penalizing mean-squared activity to encourage biologically realistic sparsity, batch size 1024 trials, 2000 batches. Twenty independent networks per task with different random seeds; reported statistics are computed across these networks.

**Analyses.** Linear-SVM cross-temporal decoding from (a) recurrent firing rates and (b) STSP efficacies, separately, lets the authors say *where* in the network the information lives at every moment of the delay. Shuffling ablations selectively destroy either the neuronal or the synaptic code at chosen time points and let the authors say *which* component is causally load-bearing. A "tuning similarity index" (TSI) measures how the population's preferred direction rotates between sample and end-of-delay, exposing prospective recoding. Spearman correlation across nine task variants relates manipulation demand (operationalized via task structure) to end-of-delay activity, producing the headline R = 0.93 result.

## 5. Results

- **Activity-silent maintenance in DMS.** Decoding accuracy from synaptic efficacies stayed at 1.0 throughout the 1000-ms delay; decoding from firing rates dropped to ≤ 0.7 (and to chance in five of six networks). The trained circuit chose, on its own, an essentially activity-silent regime for pure maintenance — without being told to.
- **Hybrid coding in DMRS and other manipulation tasks.** All 20 networks held information in both substrates simultaneously. Decoding from synapses stayed near ceiling; decoding from firing rates was significantly above chance throughout the delay. Networks with the strongest delay-period selectivity also suffered the largest performance loss under neuronal-activity shuffling, confirming that the persistent component is functionally load-bearing rather than epiphenomenal.
- **Manipulation–persistence correlation.** Across nine task variants spanning the full range from pure maintenance (DMS, delayed-cue with simple match) to heavy manipulation (DMRS with sample-test rotation), end-of-delay persistent-activity magnitude versus manipulation demand gave a Spearman R = 0.93 (P < 0.001, n = 9). The correlation is essentially monotone: more transformation, more delay-period firing.
- **Prospective recoding.** During the DMRS delay, inhibitory units with depressing synapses developed asymmetric tuning rotated 90° toward the upcoming test direction. Their activity therefore prospectively encoded the *transformed* stimulus rather than the original sample. The asymmetry was strongest in the population that combined depression (so the synapse forgets the sample faster) with inhibition (so the population can implement a structured competition between past sample and future test).
- **Causal ablations.** Shuffling synaptic efficacies at the end of the delay catastrophically degraded performance in maintenance tasks but only modestly in manipulation tasks. Shuffling firing rates did the reverse. The two substrates are dissociable and selectively necessary for different task components.
- **Reconciliation with primate data.** The task-graded persistent-activity emergence reproduces the qualitative pattern across the PFC literature: classic oculomotor delay tasks (Funahashi 1989) and category-comparison tasks (Freedman lab; Riley & Constantinidis 2016) consistently elicit strong persistent activity; simpler match-to-sample paradigms sometimes do not (the empirical disagreement that motivated Stokes 2015 and the activity-silent literature). The model puts both regimes on a single continuum parameterized by task demand.

## 6. Critique / limitations

The network is small (100 units) and rate-based, with synaptic kinetics tuned to literature values rather than fit to data. The result that maintenance falls preferentially onto STSP is partly forced by the L2 firing-rate penalty: a network trained without that penalty would have less pressure to remain quiet during the delay. The authors acknowledge this, and treat the penalty as a stand-in for the metabolic cost of cortical activity (Laughlin et al. 1998; Attwell & Laughlin 2001) — a defensible choice but one that should be flagged when transporting the conclusions to systems with different cost structures.

The synaptic-plasticity model is the Mongillo/Markram-Tsodyks two-variable formulation. Real STSP is more heterogeneous, with multiple timescales and post-synaptic contributions; calcium dynamics are absent. The exact 200 ms / 1500 ms timescale split into facilitating and depressing populations is hand-set. Whether the qualitative regime (maintenance ↔ STSP, manipulation ↔ persistence) survives richer plasticity models is not tested.

Dale's law and the 80/20 E/I split are imposed but not derived; the network is not given a spatial structure, so claims about laminar or columnar localization of the two components cannot be made. The paper is silent on the BPTT issue (biological plausibility of gradient-based learning) that Mante 2013 also leaves open — the architectural claim survives whatever learning rule one prefers, but the *learned solution* is conditional on the optimizer's inductive bias.

The tasks are all delayed match/comparison paradigms with one or two stimuli. Whether the dual STSP-plus-persistence code scales to complex sequential cognition (multi-step planning, hierarchical control, language-like recursion) is open. The HRM-style multi-timescale architectures (Wang et al. 2025, in seed) are one plausible extension; the user's GridCell RNN stack is another.

Finally, the paper is descriptive about *what* the network does and not normative about *why* the slow/fast decomposition is the optimal one. A regularized-objective derivation of the regime split (e.g., from a free-energy or information-bottleneck argument) is missing and would be a natural next theoretical step.

## 7. Connection to our work

Masse et al. is one of the load-bearing precedents for the user's architectural program because it converts a debate about WM substrates into a constructive demonstration that *both* substrates can be learned end-to-end inside the same recurrent network from a task objective alone.

**Direct precedent for the Recurrent ViT and PRISM ConvGRU learning WM-like dynamics.** The Recurrent ViT (2502.10955) and PRISM v1/v2 share Masse's central methodological move: train a recurrent network with one external loss and observe what kind of memory code emerges. Masse showed that on WM tasks the emergent code recovers the canonical persistent-activity signature of primate PFC (Funahashi 1989; Goldman-Rakic 1995; Riley & Constantinidis 2016; Constantinidis 2018) and the activity-silent alternative simultaneously. This is the existence proof that the user's narrower change-detection objective is the same kind of probe — a behavioral task whose only requirement is to make WM dynamics emerge — and that the emergent dynamics can reasonably be expected to resemble the dynamics those tasks evoke in cortex.

**The transient-vs-persistent decomposition maps onto PRISM v2's slow/fast memory.** PRISM v2 (`PRISM_V2_PROPOSAL.md` §3.3) commits to two coupled recurrent states: a fast memory $M^{\text{fast}}$ that updates every step and a slow memory $M^{\text{slow}}$ updated rarely (per-step update probability ~0.05). Masse's hybrid code is the biological analog of exactly that decomposition. The STSP component — efficacies with $\tau$ on the order of 1.5 s — plays the role of the slow memory: it integrates over many trial events and decays gracefully. The persistent-activity component — firing rates with $\tau = 100$ ms — plays the role of the fast memory: it updates on the fast timescale of within-trial cognitive operations and is the substrate of online manipulation. The argument that motivates PRISM v2's dual-timescale commitment (`PRISM_V2_PROPOSAL.md` §3.3, citing Mujika et al. 2017 and Tallec & Ollivier 2018) is here given a *biological* justification: a trained recurrent network endowed with two timescales spontaneously partitions WM tasks between them in the same way the slow/fast architecture proposes to.

**Synaptic plasticity supplementing persistent activity is the conceptual bridge to activity-silent WM.** The two pillars of the modern WM literature — Stokes 2015 ("activity-silent" hidden states) and Mongillo 2008 (synaptic theory of WM) on one side; Funahashi 1989, Goldman-Rakic 1995, Riley & Constantinidis 2016, and Constantinidis 2018 (persistent activity is the WM substrate) on the other — are reconciled here by showing the same recurrent network supports both. For the user's program this matters because the architectural commitment to *multi-compartmental memory* (a slow synapse-like state plus a fast activation-like state) is not the choice between persistent-activity and activity-silent accounts; it is the architectural acknowledgement that both must coexist, that they fill complementary roles, and that gradient descent on a WM task is sufficient to discover the partition. PRISM v2's slow/fast memory and the GridCell RNN stack's per-layer state variables can each be read as a discretization of Masse's continuous hybrid code.

**Architectural specifics the paper supports.** (i) That recurrent memory states should be *gated* with at least two timescales (justifying PRISM v2 §3.3 and the slow/fast Mujika commitment). (ii) That memory contents need not be retrievable solely from instantaneous activity — they can sit in slowly varying parameters of the dynamics, which is the conceptual licence for FiLM / attention-key conditioning in the Feedback Transformer's $K, V$ projections. (iii) That manipulation tasks specifically force prospective recoding (the rotated-tuning result), which is exactly the kind of computation the user's `iterative variational encoder–decoder` performs in its $n_{FR} \to n_{BR}$ rollout — the decoder side has to produce a *transformed* output rather than a copy of the encoder's guide.

**Architectural specifics the paper qualifies.** The L2 firing-rate penalty in Masse is what tips the maintenance regime into STSP; without it, the network would happily store everything in firing rates. Translating to our work: PRISM's preference for "biologically plausible" sparsity should be made explicit rather than left implicit, because *the regime that emerges depends on it*. The Masse result is therefore both encouragement (slow/fast partitioning is learnable) and warning (the regime is a function of the regularizer, not just of the task).

**Relationship to mante2013_context_dependent_pfc.** Mante 2013 established that a trained RNN can reproduce PFC population dynamics in a context-dependent decision task; Masse 2019 extends the same methodology to working-memory-and-manipulation tasks and adds a biologically grounded plasticity layer. Together they constitute the strongest existing case that trained recurrent networks are an appropriate model class for the user's PFC analog (the central self-attention substrate of the multi-hub system). Masse is the natural next citation after Mante in the user's "trained-RNN-as-PFC-model" literature trail. Where Mante demonstrates context-dependent *selection* via line attractors, Masse demonstrates context-dependent *encoding regime* via the partition between firing rates and synaptic state — two complementary instances of the same overarching idea that a single recurrent substrate can flexibly reconfigure its computational role under task control.

**Relationship to the persistent-activity literature.** Funahashi 1989 and Goldman-Rakic 1995 are the empirical foundation of the persistent-activity orthodoxy; Riley & Constantinidis 2016 documents that the persistence is genuinely mnemonic rather than artifactual; Constantinidis 2018 is the modern defense of the persistent-activity-as-WM thesis against activity-silent challengers. Masse 2019 is the constructive synthesis: it shows in a single trained network *both* that persistent activity is the natural code for manipulation and that activity-silent maintenance is the natural code for simple holding. The user's program inherits all four citations in a single coherent story — PFC implements WM via a hybrid code whose mix is set by task demand, and the user's GridCell RNN / PRISM v2 dual-memory architectures are bets on which substrate to engineer for what role.

**Implication for the change-detection task.** The change-detection benchmark used by the Recurrent ViT and PRISM is a maintenance-plus-comparison task: hold a representation of frame $t-1$ and compare it to frame $t$. By Masse's taxonomy this sits closer to DMS than to DMRS — no overt rotation, mostly faithful holding — which predicts that a network with adequate slow recurrence (i.e., the PRISM ConvGRU's gate dynamics or the Recurrent ViT's recurrent token state) should be able to solve it with relatively modest delay-period activity. The empirical observation that PRISM v1 succeeds with a single slow ConvGRU memory (`THESIS.md` §2.4) is consistent with this prediction. The further prediction is that *richer* change tasks requiring transformation between $t-1$ and $t$ (mental rotation, predictive extrapolation, multi-step planning) will demand a fast-memory contribution proportional to the manipulation. PRISM v2's fast memory is the architectural response.

**Implication for the Feedback Transformer.** The Feedback Transformer (§1 of the user's program) integrates multiple recurrent states via per-state Q/K/V projections into the attention computation. Masse's hybrid code suggests that at least two of those states should differ in timescale by an order of magnitude — a fast one matching the within-trial dynamics ($\sim$100 ms) and a slow one matching synaptic kinetics ($\sim$1.5 s). The current Recurrent ViT uses a single recurrent state per layer ($H^{(t-1)}$); the user's program already commits to multiple parallel states; Masse provides the biological rationale for ensuring at least one of them carries a distinctly slower update rule than the others.

**Open question the paper raises for the program.** Masse partitions WM tasks by manipulation demand and shows persistent activity scales with it. The user's tasks (change detection, video autoencoding, eye-tracking, classification) do not have a clean manipulation-demand axis; they have an overall *world-modeling* demand. A natural extension is to ask whether the same partition emerges along the world-modeling axis: do simpler benchmarks (single-frame classification) recruit STSP-like slow states, while richer benchmarks (multi-step video prediction) recruit fast persistent activity? Designing PRISM v3 experiments that can answer this would directly extend Masse's framework into the user's domain.

## 8. Citations to follow

- `mongillo2008_synaptic_theory_wm` — Synaptic theory of working memory (Science). The foundational STSP-as-WM model whose Tsodyks-Markram synaptic kinetics Masse uses; essential for any database treatment of activity-silent WM.
- `stokes2015_activity_silent_wm` — "'Activity-silent' working memory in prefrontal cortex: a dynamic coding framework." (Trends in Cognitive Sciences). The conceptual review of activity-silent WM; the paradigm Masse is reconciling with persistent activity.
- `markram_tsodyks1996_synaptic_dynamics` — Original short-term plasticity formulation behind the $x \cdot u$ kinetics.
- `sussillo_barak2013_opening_blackbox` — Methods for analyzing trained RNN dynamics; applied implicitly here and in Mante 2013.
- `yang_wang2019_task_representations` — Yang/Wang follow-up showing how multitask training shapes RNN representations; relevant to multi-objective / multi-hub extensions of Masse.
- `laughlin1998_metabolic_cost` — The metabolic-cost-of-neural-information argument that justifies Masse's L2 activity penalty; load-bearing for the user's `coalition-resource-competition` thesis.
- `wang1999_synaptic_basis_persistent` — Wang's NMDA-based persistent-activity model; the cellular-mechanism alternative to Masse's network-level account.
- `compte2000_synaptic_mechanisms_wm` — Compte/Brunel/Wang spatial WM model, the canonical bump-attractor persistent-activity circuit.
- `lundqvist2018_gamma_beta_wm` — Discrete gamma/beta bursts in PFC during WM, an empirical phenomenon the Masse model does not exhibit; a useful contrast.
- `freedman2001_categorical_pfc` — Freedman lab's category-selective PFC neurons; the empirical context for many of Masse's task variants (DMC and beyond).
- `song2016_rnn_cognitive` — Song/Yang/Wang RNN framework that Masse builds on; would expand the methodological lineage of trained-RNN cognitive models.
