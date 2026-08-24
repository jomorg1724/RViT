---
id: multi_hub_multi_objective_system
type: concept
title: "The multi-hub multi-objective system"
papers:
  - schmidhuber2015_learn_to_think
  - ha_schmidhuber2018_world_models
  - hafner2020_dreamer
  - bardes2023_vjepa
  - lecun2022_path_to_agi
  - mante2013_context_dependent_pfc
  - haber2015_cbgtc_circuits
  - choi2023_msi_review
  - senkowski_engel2024_multi_timescale_msi
  - manns_eichenbaum2006_lec_mec
  - sherman2022_ctc_loop
source_documents:
  - "Private & Shared-4/Evolution of Architecture (§ A General Purpose Multi-Objective System)"
last_updated: "2026-05-16"
---

# The multi-hub multi-objective system

## Definition

A neural architecture in which several functionally-specialized "hubs" run in parallel, each maintaining its own internal memory state(s) and pursuing its own learning objective, and all of which feed back into a central shared self-attention substrate (a Feedback Transformer). Hubs compete for control of the central substrate by manipulating its Q/K/V inner-product space; the competition pressure is the architectural source of cross-hub coordination.

The reference hub set in the user's program is three:

- **MSI hub** (multi-sensory integration). Trained on self-supervised representation-learning objectives (V-JEPA-style latent prediction; contrastive learning; reconstruction). Builds and maintains world-state representations from sensory input.
- **RL hub.** Trained on environmental reward via PPO or distributional Q-learning. The biological analog is the cortico-basal-ganglia-thalamic loop (`concepts/cortico_basal_ganglia_thalamic_loops.md`).
- **VAE / generative hub.** Trained on iterative reconstruction with a variational free-energy objective (`concepts/iterative_variational_encoder_decoder.md`). The biological analog is the generative-decoder pathway of the cortex.

Each hub maintains GridCell-RNN-style memory states (`concepts/gridcell_rnn.md`), and each hub's memory feeds back into the central Feedback Transformer. The central self-attention map is therefore a function of all hubs' contributions plus the bottom-up sensory input.

## The central self-attention map as the competitive arena

Formally, for each token $i$, the final attention score depends on a Q vector formed from sensory and per-hub projections combined via Hadamard product before softmax:

$$
q_i = s_{q,i} \odot \big(c^{(\text{MSI})}_{q,i} + c^{(\text{RL})}_{q,i} + c^{(\text{VAE})}_{q,i}\big)
$$

A hub that wants its preferred tokens to be attended to must contribute Q/K projections that *agree* with the bottom-up sensory projection and *disagree* with rival hubs' projections. The architectural pressure for each hub is therefore: predict the sensory input *and* predict the rivals' contributions. The first half is conventional predictive coding; the second half is the user's strategic extension (`concepts/coalition_resource_competition.md`).

## What makes a hub a hub

Three architectural commitments distinguish a hub from a sub-component of a single network:

1. **Own memory states.** Each hub maintains its own GridCell-RNN-style recurrent states whose update rule is not entangled with other hubs' update rules.
2. **Own learning objective.** Each hub is trained primarily on its own loss. Gradient flow between hubs occurs *through* the central self-attention substrate, but each hub's optimizer is governed by its own loss.
3. **Read/write access to the central substrate.** Each hub contributes Q/K/V to the shared self-attention, and reads the attention-weighted output to update its own state.

Without (3), the hubs are independent networks. Without (2), the hubs are sub-components of one network. The combination — own objectives + shared substrate — is the defining architectural commitment.

## Connection to Schmidhuber 2015

Schmidhuber's C–M framework (`papers/schmidhuber2015_learn_to_think.md`) is the two-hub special case: C is the RL hub, M is the VAE/generative hub. The user's multi-hub system adds an MSI hub and generalizes the communication substrate from "C queries M" to "all hubs share a central self-attention module."

Schmidhuber's hubs are *cooperative*: C reads M's outputs to make better decisions. The user's hubs are *competitive*: each hub fights for control of the central attention map, and the user's theoretical thesis (`concepts/coalition_resource_competition.md`) is that this competition is what produces predictive-coding behavior emergently.

## Connection to biological architecture

- **CBGTC loop ↔ RL hub.** Haber 2016 (`papers/haber2015_cbgtc_circuits.md`) describes the cortico-basal-ganglia-thalamic loop as the brain's RL machinery, with reward signals integrated across cortical functional territories at striatal convergence zones. The user's RL hub is the computational analog.
- **Multi-sensory integration in higher-order thalamus / parietal cortex ↔ MSI hub.** Senkowski & Engel 2024 and Choi et al. 2023 describe the multi-timescale anatomy of MSI; Sherman 2022 (`papers/sherman2022_ctc_loop.md`) describes the transthalamic substrate. The MSI hub is the computational analog.
- **Cortex-wide generative-modeling activity ↔ VAE hub.** Predictive coding (Rao-Ballard, Bastos, Keller-Mrsic-Flogel) treats the cortex as a hierarchical generative model. The VAE hub instantiates this with an explicit variational objective.
- **PFC as the central self-attention substrate.** Mante et al. 2013 (`papers/mante2013_context_dependent_pfc.md`) shows that PFC implements context-dependent computation by recurrent dynamics that integrate multiple input streams. The shared self-attention map in the user's architecture is the computational analog of PFC's context-dependent gating.

## Empirical-test design

The falsifiable test the user proposes (Evolution of Architecture §"A General Purpose Multi-Objective System"): train the multi-hub system on tasks that put the hubs' objectives in conflict, then train a *separate* decoder to predict the entire global internal state at $t+1$ from the global state at $t$. If iterative roll-out of this decoder produces long-range coherent prediction of internal states, that is evidence that a world model has emerged implicitly from the inter-hub competition, without any explicit world-model training signal. The world-model emergence concept (`concepts/world_model_emergence.md`) is this prediction.

## Connection to other concepts

- `feedback_transformer` — the shared central substrate is a Feedback Transformer with each hub contributing one feedback source.
- `gridcell_rnn` — each hub's internal memory is a stack of GridCell RNNs.
- `coalition_resource_competition` — the theoretical justification for the architecture.
- `world_model_emergence` — the empirical prediction that competition produces an emergent world model.
- `competition_emergent_predictive_coding` — the theoretical thesis that predictive coding is the strategic response to coalition competition.

## Open questions

1. **What is the right number of hubs?** Three (MSI, RL, VAE) is the reference design but is partly historical. A two-hub system (Schmidhuber's C+M) and a many-hub system (one per task / sensory modality / temporal scale) are both plausible.
2. **How is the central self-attention substrate shared?** The user's notes commit to "all hubs feed into one FT layer." Whether to share many FT layers (one per cortical level) or just the deepest layer is an open architectural choice.
3. **What objectives put the hubs in productive conflict?** If MSI and RL agree on everything, there is no competition; if they disagree on everything, training is unstable. The right conflict structure is empirically unsettled.
4. **Decoder for the world-model-emergence test.** What architecture should the decoder use? A simple linear-state-prediction decoder is one option; a generative-rollout decoder is another. The choice affects the strength of the falsifiability claim.
