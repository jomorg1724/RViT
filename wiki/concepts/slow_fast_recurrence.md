---
id: slow_fast_recurrence
type: concept
title: "Slow-fast recurrence (multi-timescale coupled RNNs)"
papers:
  - mujika2017_fast_slow_rnn
  - tallec_ollivier2018_chrono_init
  - wang2025_hierarchical_reasoning_model
  - schmidhuber2015_learn_to_think
  - hochreiter_schmidhuber1997_lstm
  - beck2024_xlstm
  - buzsaki_wang2012_gamma
  - goldman_rakic1995_cellular_wm
  - funahashi1989_mnemonic_dlpfc
  - constantinidis2018_persistent_activity
  - masse2019_circuit_wm
source_documents:
  - "PrismV2/docs/PRISM_V2_PROPOSAL.md (§ 3.3)"
  - "Private & Shared-4/Evolution of Architecture (§ Hierarchical Memory Layers)"
last_updated: "2026-05-18"
---

# Slow-fast recurrence (multi-timescale coupled RNNs)

## Definition

An architectural commitment to maintaining *multiple recurrent state variables that update at different effective time constants*, with explicit coupling between fast-evolving low-level states and slow-evolving high-level states. The fast states track moment-to-moment input; the slow states maintain context, plans, working-memory contents, or other slowly-evolving variables. The coupling is bidirectional — slow states condition the fast-state update; fast states drive the slow-state update — but with strongly asymmetric update frequencies.

The biological motivation is the well-documented timescale separation in cortex: gamma-band oscillations (~30–100 Hz) in early sensory areas (Buzsáki & Wang 2012, `papers/buzsaki_wang2012_gamma.md`) versus persistent activity over seconds in PFC working-memory neurons (Funahashi 1989, `papers/funahashi1989_mnemonic_dlpfc.md`; Goldman-Rakic 1995, `papers/goldman_rakic1995_cellular_wm.md`; Constantinidis et al. 2018, `papers/constantinidis2018_persistent_activity.md`).

## Implementation mechanisms

Three architectural mechanisms have been used to instantiate slow-fast recurrence:

**Mechanism 1 — Hard update-rate separation.** The fast module updates every step; the slow module updates every $T$ steps. The Hierarchical Reasoning Model (HRM, `papers/wang2025_hierarchical_reasoning_model.md`) commits to this:

$$
z_L^i = f_L(z_L^{i-1}, z_H^{i-1}, \tilde x; \theta_L), \quad z_H^i = \begin{cases} f_H(z_H^{i-1}, z_L^{i-1}; \theta_H) & i \equiv 0 \pmod T \\ z_H^{i-1} & \text{otherwise} \end{cases}
$$

The advantage is computational: the slow module's parameters are updated $1/T$ as often, so the slow module can be larger. The disadvantage is that $T$ is a hard hyperparameter; the model cannot adapt update frequency to task structure.

**Mechanism 2 — Soft update-rate separation via gate-bias.** Both modules update every step, but the slow module's update gate is biased to typically retain its previous state. In PRISM v2 (`PrismV2/docs/PRISM_V2_PROPOSAL.md` §3.3), the fast memory uses $b_u^{\text{fast}} = -1$ giving $\sigma(-1) \approx 0.27$ per-step update probability; the slow memory uses $b_u^{\text{slow}} = -3$ giving $\sigma(-3) \approx 0.05$. The "chrono-init" trick from Tallec & Ollivier 2018 (`papers/tallec_ollivier2018_chrono_init.md`) generalizes this: initialize gate biases such that the expected forgetting time matches the desired task timescale.

The advantage is differentiability: gate biases are learnable, so the system can adapt update frequency to task demands. The disadvantage is that the slow module still consumes per-step compute even though most updates are no-ops.

**Mechanism 3 — Coupled-RNN with separate parameterizations.** Mujika, Meier & Steger 2017 (`papers/mujika2017_fast_slow_rnn.md`) use two parameterized RNNs running in parallel, with explicit communication channels (concatenation, attention) between them, and update rates either fixed or learned.

## Why timescale separation matters

The argument has three legs:

1. **Effective computational depth.** Stacking many sequential layers (BPTT-style) suffers vanishing gradients. Distributing computation across modules updating at different rates gives the system effective depth (HRM's hierarchical-convergence argument) without the gradient problems.

2. **Working memory.** Tasks that require maintaining a goal, context, or partial result over many timesteps benefit from a slow state that doesn't get overwritten by moment-to-moment input. The biological literature on PFC working memory (Funahashi 1989; Goldman-Rakic 1995; Constantinidis et al. 2018; Masse et al. 2019, `papers/masse2019_circuit_wm.md`) confirms that the brain implements this with persistent-activity neurons whose effective time constant is seconds-long.

3. **Hierarchical structure of natural tasks.** Real tasks have nested structure: short-timescale events embedded in medium-timescale episodes embedded in long-timescale goals. A multi-timescale architecture matches the task's natural decomposition.

## How HRM differs from Mujika 2017

HRM is not the first slow-fast RNN architecture. The conceptual novelty over Mujika et al. 2017 and Tallec & Ollivier 2018 is the **hierarchical convergence** mechanism: the L module is explicitly run to a local equilibrium within each cycle before the H module updates, then L is *reset* to begin a new equilibrium phase. This is more than fast-slow update rates; it is nested fixed-point computation, with the slow module conditioning a sequence of fast-module equilibria. The advantage is qualitatively higher effective computational depth than either Mujika 2017 or a single converging RNN can achieve.

## Connection to PRISM v2

PRISM v2 (`PrismV2/docs/PRISM_V2_PROPOSAL.md` §3.3) uses Mechanism 2 (soft gate-bias separation with chrono-init). The architecture has $M^{\text{fast}}$ paired with V1 features and $M^{\text{slow}}$ paired with V2 features, with cross-level error and prediction flow (`concepts/bidirectional_hierarchical_feedback.md`).

The user's program (`threads/the_user_architectural_program.md` §3) commits to *three* memory levels with monotonically slower update rates, not just two. The architecture for the third level is sketched (deeper spatial reduction, slower update gate) but the empirical instantiation hasn't yet been tested.

A potential future direction is to adopt HRM's hierarchical-convergence mechanism (Mechanism 1) in place of or in combination with PRISM v2's gate-bias mechanism (Mechanism 2). The hard-vs-soft trade-off is one of the most important open architectural questions.

## Connection to other concepts

- `multi_compartmental_memory` — the multi-state structure that slow-fast recurrence implements.
- `gridcell_rnn` — each level of the multi-compartmental memory is a GridCell RNN with its own update gate.
- `bidirectional_hierarchical_feedback` — the cross-level coupling between slow and fast states is one direction of the hierarchical feedback.
- `coupled_rnn_world_models` — the architectural family that HRM (Mechanism 1) sits in. HRM's controller-and-world-model pair is a special case of slow-fast recurrence with hard timescale separation and hierarchical convergence; coupled-RNN world models are the broader family of two-RNN architectures of which slow-fast is one organizing axis.
- `hierarchical_convergence` (taxonomy concept) — HRM's specific mechanism for slow-fast coupling.
- `chrono-initialization` (taxonomy) — Tallec-Ollivier mechanism for soft gate-bias separation.

## Open questions

1. **Hard vs soft timescale separation.** HRM uses hard; PRISM v2 uses soft. Which is better in practice — and under what conditions — is not yet known.
2. **How many timescales?** Two (PRISM v2, HRM) vs three (user's program target) vs continuous (chrono-init with arbitrary gate biases).
3. **Training stability with very slow timescales.** Gate-biases that produce very slow update rates ($\sigma(b_u) \ll 0.1$) can be hard to train: the slow state changes so rarely that few gradient signals reach it. The right balance is unsettled.
4. **What slow-state content is useful?** Working-memory contents, planning state, attention priors, posterior summaries — different choices give different architectures. The user's program treats this as an empirical question.
