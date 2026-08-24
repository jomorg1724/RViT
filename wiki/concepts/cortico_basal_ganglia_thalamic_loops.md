---
id: cortico_basal_ganglia_thalamic_loops
type: concept
title: "Cortico-basal-ganglia-thalamic (CBGTC) loops"
papers:
  - haber2015_cbgtc_circuits
  - hikosaka2006_bg_reward_eyes
  - mcnab_klingberg2008_pfc_bg_wm
  - herman_arcizet2020_caudate_sc
  - glimcher2011_dopamine_rpe
  - botvinick2020_deep_rl_neuro
  - babayan_uchida_gershman2018_belief_states_dopamine
  - sutton_barto2018_rl_intro
source_documents:
  - "Private & Shared-4/Evolution of Architecture (§ A General Purpose Multi-Objective System)"
last_updated: "2026-05-16"
---

# Cortico-basal-ganglia-thalamic (CBGTC) loops

## Definition

The closed-loop circuit by which cortical areas send topographically-organized projections to the striatum, the striatum sends inhibitory outputs through the globus pallidus and substantia nigra to the thalamus, and the thalamus projects back to the source cortical areas via mediodorsal (MD), ventral anterior (VA), and ventral lateral (VL) nuclei. Modulated by dopamine signals from the substantia nigra pars compacta (SNc, dorsal striatum) and ventral tegmental area (VTA, ventral striatum). Implements the brain's reinforcement-learning machinery: outcome-based teaching signals drive corticostriatal plasticity, biasing the loop toward outcomes that have been rewarded.

The framework is reviewed by Haber 2016 (`papers/haber2015_cbgtc_circuits.md`).

## The functional topography

Different sectors of the striatum support different functions:

| Striatal sector | Cortical input | Function |
|---|---|---|
| Ventral striatum (nucleus accumbens) | Orbital/medial PFC, vACC, hippocampus, amygdala | Reward evaluation |
| Caudate (head/body) | Dorsolateral PFC, dorsal ACC | Cognitive control |
| Putamen | Primary motor, premotor, supplementary motor | Motor control |

The topography is *not sharp* — Haber emphasizes the "convergence zones" where terminal fields from different functional cortical territories overlap, providing anatomical substrates for cross-domain integration. Reward signals can influence cognitive processing because the relevant cortical territories converge in specific striatal sites.

## The direct and indirect pathways

Striatal medium spiny neurons split into two pathways:

- **Direct pathway** (striatum → GPi/SNr → thalamus → cortex). Facilitates selected actions. D1-receptor-dominated.
- **Indirect pathway** (striatum → GPe → STN → GPi/SNr → thalamus → cortex). Suppresses competing actions. D2-receptor-dominated.

The two pathways together implement action selection by gating cortex-bound thalamic projections: actions whose direct-pathway input dominates are facilitated; actions whose indirect-pathway input dominates are suppressed. Dopamine asymmetrically modulates the two pathways (D1: enhances direct; D2: suppresses indirect), giving the system a strong positive-feedback amplification of rewarded actions.

## Dopamine as teaching signal

SNc and VTA dopamine neurons project to the striatum and encode a reward prediction error (RPE) signal: positive when outcomes exceed expectations, negative when they fall short. The RPE acts as a synaptic plasticity signal at corticostriatal synapses, strengthening cortex-to-striatum connections that led to positive surprise and weakening those that led to disappointment. This is the substrate of Schultz-Dayan-Montague's RPE hypothesis (Glimcher 2011 review, `papers/glimcher2011_dopamine_rpe.md`; Babayan, Uchida & Gershman 2018, `papers/babayan_uchida_gershman2018_belief_states_dopamine.md`).

## The RL hub of the user's multi-hub system

The CBGTC loop is the biological substrate of the RL hub in the user's multi-hub multi-objective system (`concepts/multi_hub_multi_objective_system.md`). Specific correspondences:

- **RL hub's memory state.** Anatomically distributed across ventral striatum (value), dorsal striatum (action), OFC (outcome representation), and PFC (context).
- **RL hub's learning signal.** RPE from SNc/VTA dopamine.
- **RL hub's output channel.** The thalamic projections that close the loop back onto cortex provide the channel by which RL representations influence the central self-attention substrate.
- **RL hub's interaction with other hubs.** Convergence zones in striatum (where multiple cortical territories overlap) are the anatomical analog of the inter-hub competition arena.

PRISM v1 implements a single-hub actor-critic that combines policy and value within one network. PRISM v2's distributional Q-critic (`Prism/docs/PRISM_V2/Q_CRITIC.md`) is a step toward the CBGTC structure: separating policy and Q-value into distinct heads with separate gradients. A full implementation of the user's program would further separate these into a separate RL hub with its own memory states, with the central self-attention substrate playing the role of cortex.

## Connection to attention

The CBGTC loop has a specific attention-control role through subcortical attention pathways. McNab & Klingberg 2008 (`papers/mcnab_klingberg2008_pfc_bg_wm.md`) shows that PFC and basal ganglia interact to control working-memory access — a form of internal attention. Herman, Arcizet & Krauzlis 2020 (`papers/herman_arcizet2020_caudate_sc.md`) shows that attention-related caudate modulation depends on the superior colliculus, linking the CBGTC loop to overt-attention machinery. Hikosaka, Nakamura & Nakahara 2006 (`papers/hikosaka2006_bg_reward_eyes.md`) shows that the basal ganglia orient eye movements toward reward.

The CBGTC loop is therefore not only the RL substrate but also a key part of the attention-control machinery.

## Connection to other concepts

- `multi_hub_multi_objective_system` — the RL hub is the computational analog of the CBGTC loop.
- `cortico_thalamo_cortical_loops` — the thalamic-relay portion of the CBGTC loop is a special case of the more general transthalamic-pathway concept.
- `reward-modulated-attention` (tag) — the CBGTC loop is the substrate.
- `priority_map` (tag) — striatal value representations contribute to priority-map construction.
- `coalition_resource_competition` — the convergence zones implement physical competition between functional territories.

## Connection to the literature

The most influential recent computational model of CBGTC-style RL is Botvinick et al. 2020 (`papers/botvinick2020_deep_rl_neuro.md`), which synthesizes deep RL with neuroscientific findings on dopamine and striatum. This provides the modern bridge between the anatomy (Haber 2016) and the algorithmic implementation (Sutton & Barto 2018, `papers/sutton_barto2018_rl_intro.md`).

## Open questions

1. **How is the convergence-zone interaction implemented at the cellular level?** The Haber framework identifies sites of overlap; the cellular mechanism of cross-territory integration (medium-spiny-neuron co-activation, GABA-ergic interneuron mediation, dopamine-modulated plasticity) is still being worked out.
2. **What is the relationship between direct/indirect and exploration/exploitation?** D1 vs D2 receptor dynamics have been related to exploration vs exploitation; the exact mapping is open.
3. **Is the RL hub strictly subcortical?** In the user's program the RL hub has its own cortical memory states. The biological RL machinery is distributed across cortex (PFC, ACC, OFC) and basal ganglia; treating it as primarily subcortical may oversimplify.
4. **What is the right computational analog of the convergence zone?** In the multi-hub architecture, the central self-attention substrate is the proposed analog. Whether this is structurally adequate — capturing the topographic precision of striatal anatomy — is open.
