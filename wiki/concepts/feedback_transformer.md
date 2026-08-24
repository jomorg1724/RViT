---
id: feedback_transformer
type: concept
title: "The Feedback Transformer"
papers:
  - vaswani2017_attention
  - dosovitskiy2020_vit
  - locatello2020_slot_attention
  - mante2013_context_dependent_pfc
  - perez2018_film
  - reynolds_heeger2009_normalization
  - bahdanau2014_neural_translation
  - voita2019_head_specialization
  - weiler2025_l6_corticocortical
  - larkum2013_apical_basal
  - sherman2022_ctc_loop
  - mckinnon_mo_sherman2025_transthalamic_v1
  - bastos2012_canonical_microcircuits
  - felleman_vanessen1991_hierarchical_cortex
source_documents:
  - "Private & Shared/Encoder-Decoder Architecture"
  - "Private & Shared-4/Evolution of Architecture (§ Feedback Transformer)"
last_updated: "2026-05-18"
---

# The Feedback Transformer

## Definition

A self-attention layer whose Q/K/V projections are augmented by an arbitrary number of recurrent internal-state contributions, combined with the bottom-up sensory contribution via element-wise (Hadamard) broadcasting prior to the softmax. For each recurrent state $C^{(k)}$ in the feedback set, learned projections produce per-state query $q^{(k)}$, key $k^{(k)}$, and value $v^{(k)}$; these are summed with the sensory projections $s_q, s_k, s_v$ and the broadcast products feed the standard softmax-attention computation.

In compact notation, for sensory input $X$ and feedback set $\{C^{(1)}, \ldots, C^{(K)}\}$:

$$
\tilde Q = X W^Q_X \odot \sum_k C^{(k)} W^Q_{C^{(k)}}, \quad \tilde K = X W^K_X \odot \sum_k C^{(k)} W^K_{C^{(k)}}
$$

$$
\text{Attention}(X, \{C^{(k)}\}) = \text{softmax}\!\big(\tilde Q \tilde K^\top / \sqrt{d_k}\big) \tilde V
$$

where $\tilde V$ is similarly broadcast.

## Architectural commitment

Every feedback source must have the same number of patches/tokens as the sensory input. Cross-layer feedback whose native shape differs is reshaped by convolutional descending (for shallower-to-deeper) or convolutional transpose ascending (for deeper-to-shallower) operations before entering the Feedback Transformer.

Up to twelve simultaneous feedback sources have been integrated successfully in the user's Video VAE model.

## Why the element-wise broadcasting matters

Sign-flip via multiplication is computationally cheap: a multiplicative pathway can invert a sign with a single factor of $-1$, whereas an additive pathway must supply a compensating value of equal magnitude (which in turn must be predicted from somewhere). The user explicitly motivates this choice in the Evolution of Architecture document (§"Mechanism of Control: Modulating the Inner Product Space"). The strategic-competition argument also requires multiplicative coupling: a hub trying to suppress a stimulus's attention score must be able to make the corresponding Q–K inner product *negative*, which is straightforward multiplicatively but requires precise compensatory addition additively.

The biological parallel is Reynolds–Heeger style divisive normalization with multiplicative gain (`reynolds_heeger2009_normalization`): top-down feedback modulates the gain (multiplicative), not just the bias (additive), at every cortical level.

## Variants in published work

- **Token concatenation**: feedback states concatenated to the sensory input along the sequence axis. Used as variant 1 in 2502.10955 §6.7.1.
- **Additive feedback**: feedback contributions added to the sensory projections inside the QK products. Variant 2 in 2502.10955 §6.7.2.
- **Multiplicative feedback**: the Hadamard-product version described above. Variant 3 in 2502.10955 §6.7.3. This is the variant that the published paper reports as best-performing and the variant the user's program adopts as canonical.

## How the published work uses one source; the program uses many

The Recurrent ViT paper uses a single feedback source (the prior LSTM hidden state $H^{(t-1)}$). The program calls for many simultaneous feedback sources: parallel hubs (RL, VAE, MSI), hierarchical levels (V1, V2, V4-analog memory), and lateral connections from neighboring layers. The Feedback Transformer is the architectural commitment that makes scaling to many sources tractable without combinatorial blowup at the attention computation.

## Biological correlate

Layer 6 corticocortical neurons (`weiler2025_l6_corticocortical`) are a major route for intra- and inter-hemispheric feedback in mouse cortex, and integrate feedback from many cortical sources into a single sensory processing stage — structurally analogous to the Feedback Transformer's multi-source attention layer. Weiler's quantification of the L6 CC laminar bias toward feedback (especially into primary sensory and motor cortices) is the anatomical warrant for the architectural commitment that "feedback is a distinguished class" with its own integration substrate.

Anatomically, this corresponds to Larkum's (`larkum2013_apical_basal`) account of apical-versus-basal dendritic compartmentalization: feedback signals arrive at apical dendrites (broadly distributed top-down predictions), feedforward signals arrive at basal dendrites (sensory drive), and the soma integrates the two. The element-wise broadcasting of the Feedback Transformer is the abstract analog of this dendritic integration; the multiplicative coupling between feedback and feedforward pathways at the soma is the cellular implementation of the Hadamard step.

Two complementary biological feedback substrates are anchored in the corticothalamic and laminar-microcircuit literature: Sherman's transthalamic route (`sherman2022_ctc_loop`) supplies the second long-range feedback path (driver L5→pulvinar→cortex) that runs in parallel to direct L6 CC corticocortical feedback, and McKinnon, Mo & Sherman 2025 (`mckinnon_mo_sherman2025_transthalamic_v1`) provides the causal optogenetic evidence that the transthalamic limb specifically contributes to visual discrimination. Bastos et al. (`bastos2012_canonical_microcircuits`) supplies the canonical-microcircuit predictive-coding implementation that distributes feedback (deep-layer) versus feedforward (superficial-layer) signals across cortical laminae. Felleman & Van Essen (`felleman_vanessen1991_hierarchical_cortex`) supplies the original laminar feedforward/feedback criterion that every paper in this lineage operationalizes.

## Architectural antecedents

Bahdanau, Cho & Bengio's neural-translation attention (`bahdanau2014_neural_translation`) is the additive-attention precursor — the original mechanism that *summed* per-source context vectors before computing a soft alignment. The multiplicative variant in the Feedback Transformer is a deliberate departure: where Bahdanau's additive form requires the network to learn balanced magnitudes to suppress a source, the multiplicative form makes suppression cheap (single −1 factor). The Feedback Transformer keeps the multi-source spirit and discards the additive form.

Voita et al.'s head-specialization analysis (`voita2019_head_specialization`) is directly relevant to open question 1 (how many feedback sources are useful?). Voita shows that, in vanilla transformer NMT, 38 of 48 encoder heads can be pruned with negligible BLEU loss — the network functionally collapses onto a small set of specialized heads. By analogy, even with up to 12 simultaneous feedback sources in the user's Video VAE, a similar collapse onto a sparse subset is the default Voita prior; demonstrating that all 12 are used (rather than tolerated-but-pruneable) requires per-source ablation, not just successful training.

## Connection to other concepts in the database

- `gridcell_rnn` — uses the Feedback Transformer as the inter-cell communication mechanism after spatially-independent processing.
- `bidirectional_hierarchical_feedback` — the cross-layer routing of feedback into the Feedback Transformer.
- `multi_hub_multi_objective_system` — the multi-hub system uses parallel feedback into a shared Feedback Transformer as the substrate for inter-hub competition.
- `competition_emergent_predictive_coding` — the Q-K inner-product manipulation that makes inter-hub competition possible *is* the Feedback Transformer's broadcasting operation.
- `apical_basal_dendritic_integration` — the cellular substrate. The Hadamard-product structure of the Feedback Transformer is the architectural analog of pyramidal-cell apical/basal AND-gating; Larkum's BAC mechanism is the load-bearing biological warrant for choosing multiplicative over additive coupling.
- `hierarchical_predictive_coding` — the Feedback Transformer is the multi-source generalization of top-down prediction injection in hierarchical PC; bastos2012's canonical-microcircuit feedback (deep-layer) and feedforward (superficial-layer) lanes are routed into the FT as separately-projected feedback streams.

## Open questions

1. **How many feedback sources are useful?** Up to 12 has been demonstrated. Whether the network learns to use all of them or collapses to a sparse subset (analogous to the head-collapse phenomenon in transformers; `voita2019_head_specialization`) is not yet quantified.
2. **What is the right initialization for the feedback Q/K/V matrices?** Identity-at-init (analogous to the FiLM identity-at-init in PRISM v1) is one option; small-Gaussian is the other. The trade-off has not been characterized.
3. **Does the multiplicative broadcasting cause optimization instability?** Sign-flipping behaviors require the network to have well-calibrated sign estimates; if these are noisy at init, the attention map can be chaotic. Normalization (per the "literally normalize everything" advice in the Evolution document) appears to help.
4. **Why is the Feedback Transformer's spatial attention uniform after ~4k PPO episodes on the Posner change-detection task?** (HRA empirical finding, MEMORY.md.) The iter-499 and iter-1999 checkpoints show entropy/max-entropy ≈ 1.000, Gini ≈ 0.03 across all layers and all 5 inner iterations, and learned `ft_residual_scale` going *negative* in two of three cells. Wiki anchors that bear on this:

   - `voita2019_head_specialization` directly predicts head-level collapse onto a sparse subset under standard supervised training; under sparse-reward PPO the collapse pressure is plausibly *stronger* because most of the attention map produces zero gradient (no event → no policy-gradient signal differentiating spatial locations). A Voita-style differential-ablation-during-training analysis (head magnitude vs. survival of pruning) would localize whether the FT heads are differentiating then collapsing, or never differentiating at all.
   - `schulman2017_ppo` and `pleines2022_recurrent_ppo` (in the DB) supply the PPO learning-dynamics priors. Recurrent PPO is known to underuse temporal structure when the policy entropy bonus is the dominant exploration mechanism — uniform attention is consistent with the policy collapsing before the attention head differentiates, since both share the actor's gradient signal.
   - The Voita-plus-PPO joint reading suggests the failure mode is not "FT is structurally broken" but "FT receives no differentiating gradient under sparse-reward Posner": the task can be solved (per PRISM v1) with global pooling and no spatial focus, so the attention map is at a *flat minimum* of the policy loss. The architectural fix in HRA D7 (V→C₂, V→C₃ skip connections + per-layer LayerHead in DecisionReadout) attacks the upstream information-flow bottleneck; it does *not* directly attack the FT-collapse loop. A complementary attention-supervision auxiliary (e.g. a small KL penalty against a per-step location-prior derived from the cue, applied only during the cue and change windows) may be needed to break the flat-minimum trap.
   - Follow-up HRA experiment proposed in `the_user_architectural_program.md` thread and queued for the next iteration.
