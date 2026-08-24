---
id: gridcell_rnn
type: concept
title: "The GridCell RNN"
papers:
  - hochreiter_schmidhuber1997_lstm
  - vaswani2017_attention
  - dosovitskiy2020_vit
  - ballas2016_convgru
  - wu_he2018_groupnorm
  - perez2018_film
  - locatello2020_slot_attention
  - urbanczik_senn2014_predictive_dendrite
source_documents:
  - "Private & Shared-4/Evolution of Architecture (§ GridCell RNN)"
  - "Private & Shared/Encoder-Decoder Architecture"
  - "RViT_plus/memory.py (run-6 reference implementation, 2026-05-20)"
last_updated: "2026-05-20"
---

# The GridCell RNN

## Definition

A recurrent neural unit that maintains an internal *grid* of states $C^{(t)} \in \mathbb{R}^{n_{gh} \times n_{gw} \times n_C}$ — one state vector per spatial position — and updates the entire grid in two architectural stages per timestep.

**Stage 1 — Spatially-independent processing (SIP).** Each grid cell is updated *independently* of its neighbors using only its own previous state $C^{(t-1)}_{ij}$ and the current input $Z^{(t)}_{ij}$ at that spatial position. The SIP stage produces an update proposal $\hat C^{(t)}_{ij}$ — the analog of the LSTM's candidate cell. SIP is a per-cell MLP or per-cell convolutional cell; no communication across cells.

**Stage 2 — Feedback Transformer integration.** The SIP proposal is fed into a Feedback Transformer (`concepts/feedback_transformer.md`), which treats each grid cell as a token and integrates feedback from an arbitrary set of other GridCell RNN states (parallel hubs, deeper or shallower hierarchical levels). The Feedback Transformer's output is the integrated proposal $\tilde C^{(t)}_{ij}$.

The final state update is an LSTM-style gated combination of SIP and FT contributions:

$$
C^{(t)}_{ij} = (1 - z^{(t)}_{ij}) \odot C^{(t-1)}_{ij} + z^{(t)}_{ij} \odot \tilde C^{(t)}_{ij}
$$

where $z^{(t)}_{ij}$ is a learned update gate (LSTM-derived) computed per cell.

## Architectural motivation

The two-stage decomposition is the architectural reason the system can scale to many memory layers without combinatorial blowup at update time. SIP is embarrassingly parallel across cells; FT integration is a single attention pass over $n_{gh} \times n_{gw}$ tokens with arbitrary feedback sources. The compute cost is therefore $O(\text{cells}) + O(\text{cells}^2 \cdot d)$ rather than the $O(\text{cells}^k)$ that a naively-coupled k-source recurrent network would incur.

The clean separation is also a *credit-assignment* simplification: gradients through SIP flow only locally (each cell to itself), while gradients through FT flow globally (across cells and across feedback sources). Local plasticity rules (`urbanczik_senn2014_predictive_dendrite` is the candidate biological substrate) could in principle replace BPTT for the SIP stage without losing the global structure that FT provides.

## Why "GridCell"

The name evokes the spatial-grid structure of the internal state (analogous to entorhinal grid cells' spatial organization, though the architectural connection is by analogy, not derivation). It is *not* a model of biological grid cells per se.

## Reference instantiation in the user's code

The recurrent ViT (2502.10955) and PRISM v1 (`Prism/`) both use a special case of the GridCell RNN: a single grid level, an LSTM cell as the SIP, and the standard Vaswani/ViT self-attention as the FT (with one feedback source — the previous timestep's grid state).

## Connection to other concepts

- `feedback_transformer` — the Stage-2 communication primitive.
- `multi_compartmental_memory` — a stack of GridCell RNNs at different spatial resolutions and update rates is the multi-compartmental memory.
- `bidirectional_hierarchical_feedback` — the routing of feedback from other GridCell RNN instances into a given instance's FT.
- `iterative_variational_encoder_decoder` — each level of the encoder and decoder stacks is a GridCell RNN; the iterative VAE is the variational-objective wrapper around a coupled pair of GridCell-RNN stacks.
- `parallel_recurrent_units` — multiple GridCell RNN instances running in parallel constitute parallel recurrent units (TAXONOMY § "Core mechanisms").

## Connection to the literature

The closest published analog is ConvGRU (`ballas2016_convgru`), which maintains a 2D spatial grid of GRU states updated by a learned convolutional kernel. The GridCell RNN generalizes ConvGRU by (a) replacing the convolutional update with the SIP+FT decomposition, which allows arbitrarily many feedback sources to be integrated at the same level of compute, and (b) committing to a grid resolution that varies across hierarchical layers (paired with V1/V2/V4-style spatial-resolution reduction).

The Locatello et al. slot-attention model (`locatello2020_slot_attention`) shares the SIP-like structure (each slot is updated independently) but differs in the integration step (slot attention uses a competitive attention mechanism rather than a Feedback Transformer).

## Open questions

1. **What is the optimal SIP architecture?** LSTM cells, GRU cells, ConvGRU cells, transformer-block-style residual MLPs are all candidates. The user's notes have explored LSTM and ConvGRU; the comparison is not yet definitive. **RViT+ (2026-05) settled on a 1×1 conv on `[z_t, C_{t-1}]` followed by tanh as the SIP for the iterative-VAE compression task.** Strictly per-cell — the 1×1 kernel is the architectural constraint that Stage 1 must not couple neighbors.
2. **Per-cell gates vs grid-level gates.** The gate $z^{(t)}_{ij}$ can be cell-specific (a $n_{gh} \times n_{gw}$ scalar) or globally shared (one scalar). Per-cell is more flexible but harder to train.
3. **Does SIP+FT collapse onto convolutional updates in some limit?** If the FT learns to attend only to spatially-local neighbors, the GridCell RNN behaves like a ConvGRU. Quantifying when this collapse happens (and whether to prevent it) is open.
4. **Spatial-resolution coupling.** The grid resolution at each hierarchical level is currently hand-chosen (V1: 12×12, V2: 6×6 per PRISM v2). Learning the right reduction ratio is a future direction.

## Empirical refinements (RViT+ runs 1–6, 2026-05-18 → 05-20)

The reference instantiation in `RViT_plus/memory.py` adds three empirically-motivated refinements to the abstract definition. Each was added in response to a specific failure mode of an earlier run. The findings are documented in detail in `threads/rvit_plus_engineering.md`; this section is the concept-level summary.

### Refinement 1 — Learned positional embeddings on the FT input

The abstract definition specifies that SIP produces a candidate which feeds the FT. The reference implementation adds a learned per-(channel, h, w) positional embedding to the SIP candidate *before* GroupNorm-pre-FT:

$$
\text{sensory tokens} = \text{GN}(\hat C^{(t)} + P)\quad \text{where } P \in \mathbb{R}^{C \times H \times W}
$$

**Motivation (run-5 collapse).** Without positional embeddings, the FT is permutation-equivariant: there is no asymmetry that makes one (h, w) position different from another, and uniform attention is a fixed point. RViT+ run 5 (video compression, 2000 iters) saw all encoder and decoder hidden states converge to zero spatial variance with all-black reconstructions — the model fell into the trivial-mean-image minimum because the FT could not break spatial symmetry. Standard ViT/Transformer practice; initialized small (std=0.02) to perturb the candidate gently at init.

### Refinement 2 — SIP residual

The abstract definition uses the FT output as the integrated candidate: $\tilde C^{(t)} \leftarrow \text{FT}(\hat C^{(t)}, \{C^{(k)}\})$. The reference implementation **adds the SIP candidate back in**:

$$
\tilde C^{(t)} = \hat C^{(t)} + \text{FT}(\hat C^{(t)} + P, \{C^{(k)}\})
$$

This makes the FT a *refinement* on top of the SIP candidate rather than a *replacement* for it.

**Motivation (run-5 collapse).** When the FT collapses to uniform attention, its output is position-invariant, which destroys whatever per-cell spatial structure the SIP candidate carried. With the residual, SIP's structure survives FT collapse — the cell remains spatially structured even in the worst case. This is the architectural analog of ResNet's identity skip: the FT learns to compute a *correction* to SIP rather than the entire integrated state. The structural reading is that SIP is the spatially-local low-frequency component, FT is the spatial-coupling high-frequency correction, and the residual ensures the low-frequency component is always available.

### Refinement 3 — Update-gate bias = 0 (σ(0) = 0.5 reactive baseline)

The abstract definition specifies an LSTM-style update gate $z^{(t)}_{ij}$ but does not fix its initialization. The reference implementation initializes the gate bias to zero, so $\sigma(0) = 0.5$ at random init — every spatial location and every channel starts with the most reactive baseline: half of $C^{(t-1)}$, half of $\tilde C^{(t)}$.

**Motivation (Tallec-Ollivier chrono-init at the neutral setting + HRA finding).** Tallec & Ollivier 2018 (`tallec_ollivier2018_chrono_init`) show that LSTM forget-gate bias controls the model's effective time constant; large positive bias makes cells "sticky" (long memory), large negative bias makes them "reactive" (short memory). Bias = 0 is the neutral baseline from which the model can learn either direction per location and per channel. The HRA empirical finding — that strong initial-bias settings produce frozen deeper layers — argues for the neutral setting, not for chronologically-aware positive biases.

**Critical: FT remains in the gradient path from step one.** Because $C_{\text{new}} = (1 − u) \odot C_{t-1} + u \odot \tilde C^{(t)}$ with $u$ starting at 0.5 (not 0), the FT receives gradient signal from iteration zero. This is the architectural contrast with HRA, where `ft_residual_scale` was initialized to 0 and the FT received no gradient until that scalar became nonzero — a trap that, combined with sparse-reward PPO, never broke. RViT+'s gate is multiplicative on the *path*, not gating *whether the path is used*.

### Why all three matter together

The three refinements address three distinct failure modes that compounded in run 5. Pos_emb breaks the FT's permutation symmetry. SIP residual preserves the SIP candidate's spatial structure across the FT bottleneck. Update gate with bias=0 preserves recurrent memory across timesteps while keeping FT in the gradient path.

Removing any one of these is a natural ablation that should be re-run on Stage 1 once Stage 1 confirms P1; the prediction is that all three are individually necessary for attention structure to emerge under reconstruction supervision.

### Param-cost accounting

Adding pos_emb to a 3-layer stack at the standard sizes (C₁: 64×12×12 = 9,216; C₂: 96×12×12 = 13,824; C₃: 128×6×6 = 4,608) and adding `conv_update` to each cell costs ~180K params total — a ~14% increase over the no-refinement baseline (1.18M → 1.36M). The cost is concentrated in the encoder and decoder symmetrically (the decoder is structurally identical).
