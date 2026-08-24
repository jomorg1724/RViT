---
id: multi_compartmental_memory
type: concept
title: "Multi-compartmental memory"
papers:
  - hochreiter_schmidhuber1997_lstm
  - beck2024_xlstm
  - mujika2017_fast_slow_rnn
  - tallec_ollivier2018_chrono_init
  - constantinidis2018_persistent_activity
  - goldman_rakic1995_cellular_wm
  - funahashi1989_mnemonic_dlpfc
  - panichello_buschman2021_shared_mechanisms
  - manns_eichenbaum2006_lec_mec
source_documents:
  - "Private & Shared-4/Evolution of Architecture (§ Hierarchical Memory Layers, § Working Memory)"
  - "Private & Shared/Encoder-Decoder Architecture (§ Multi-Layer RViTs)"
last_updated: "2026-05-18"
---

# Multi-compartmental memory

## Definition

The architectural commitment to maintain *multiple* recurrent states in parallel, each with potentially different spatial resolution, channel dimensionality, and update timescale, and to route communication between them through a shared self-attention substrate (the Feedback Transformer) rather than through ad-hoc concatenation.

A multi-compartmental memory consists of $N$ recurrent states $\{C^{(1)}, C^{(2)}, \ldots, C^{(N)}\}$ where each $C^{(i)} \in \mathbb{R}^{n_{gh}^{(i)} \times n_{gw}^{(i)} \times d_{C^{(i)}}}$. The user's reference design has $N = 3$ memory layers with:

- $C^{(1)}$: paired with V1 features. Highest spatial resolution, smallest channel count.
- $C^{(2)}$: paired with V2/V4 features. Halved spatial resolution, doubled channel count.
- $C^{(3)}$: paired with the most abstract level. Quartered spatial resolution, quadrupled channel count.

## Why multiple compartments rather than one big memory

The user's program addresses three different functional pressures with this design:

1. **Different timescales for different content.** Working-memory items vary wildly in their natural timescale. The cue in a Posner task is stable across the entire trial (30+ frames); the per-frame orientation evidence is recomputed every step. A single ConvGRU with one set of gate biases cannot serve both purposes (Tallec & Ollivier 2018; this is the same argument PRISM v2 uses for slow/fast memory in `PRISM_V2_PROPOSAL.md` §3.3).

2. **Different spatial-feature trade-offs.** Shallow memory ($C^{(1)}$) needs many components at small channel dimension — the user describes these as "visual primitives" useful for combining low-level features flexibly into novel percepts. Deep memory ($C^{(3)}$) needs fewer components at high channel dimension — sufficient capacity to represent complex spatio-temporal objects. Higgins et al. 2017 (factorized representations) and the Manns–Eichenbaum LEC/MEC distinction support this two-axis trade-off.

3. **Separate working-memory subsystems for distinct cognitive functions.** Robert Logie's account of working memory as a workspace with specialized subsystems (Logie 2003, cited in Evolution of Architecture) maps naturally to the multi-compartment design. There is no one component that "is" working memory; instead working memory is the joint state of all compartments.

## Biological grounding

The dual-timescale organization is well-documented in cortex: fast dynamics in early visual areas (V1 gamma-band oscillations, ~30-80 Hz; Buzsáki & Wang 2012) versus slow dynamics in dorsolateral prefrontal cortex (delay-period persistent activity over seconds; Funahashi et al. 1989, Goldman-Rakic 1995, Constantinidis et al. 2018).

The spatial-vs-feature factorization has a clean cortical homolog in the entorhinal cortex: medial EC encodes spatial information while lateral EC encodes object features (Manns & Eichenbaum 2006, cited in Evolution of Architecture). The hippocampus combines them into relational memory representations — a direct biological analog of the multi-compartmental design.

Panichello & Buschman (2021, in seed) demonstrate shared mechanisms underlying attention and working-memory control in PFC, consistent with the user's view that the memory compartments themselves participate in attention competition.

## Distinction from naive multi-layer LSTMs

A standard multi-layer LSTM is *not* multi-compartmental memory in this sense: it stacks layers but each layer has the same shape, and information flows only feedforward in the time-unrolled graph (within a step) and recurrently (between steps). The compartments in the user's program have *different shapes by design* (descending projections enforce $n_{gh}^{(i)}$ decreasing and $d_{C^{(i)}}$ increasing), and inter-compartment communication is *bidirectional* (the next concept file).

## Connection to other concepts

- `feedback_transformer` — the inter-compartment communication substrate. Without it, multi-compartmental memory degenerates to parallel-but-independent recurrent stacks.
- `bidirectional_hierarchical_feedback` — the routing of information across compartments, both descending (V1 → V2 → V4) and ascending (V4 → V2 → V1).
- `gridcell_rnn` — the per-compartment cell. Each $C^{(i)}$ in a multi-compartmental memory stack is, in the user's reference design, a GridCell RNN with its own spatial resolution, channel dimensionality, and update gate.
- `slow_fast_recurrence` — the timescale axis. Multi-compartmental memory commits to multiple shapes and update rates *in parallel*; slow_fast_recurrence is the special case in which the principal axis of differentiation is the update rate (with two or three compartments at progressively slower timescales).
- `descending-projections` and `ascending-projections` — the conv/conv-transpose machinery that handles shape mismatches between compartments.
- `multi_hub_multi_objective_system` — multi-compartmental memory generalizes to multi-hub when each hub has its own multi-compartmental memory stack.

## In the published work

- **Recurrent ViT (2502.10955)** uses a single memory compartment (patch-based LSTM $H^{(t)}$). The hierarchical V1/V2/V4 axis is absent. The paper acknowledges this as a limitation in §5.5 ("scaling up to deeper, multilayer recurrent architectures may capture the intricate, multi-level feedback loops characteristic of the primate cortex").

- **PRISM v1 (`THESIS.md`)** uses a single $M_t$ with no hierarchical decomposition. Single compartment.

- **PRISM v2 (`PRISM_V2_PROPOSAL.md`)** introduces a two-compartment design: $M^{\text{fast}}$ paired with V1 features and $M^{\text{slow}}$ paired with V2 features (§3.3). This is the closest the published program has come to instantiating the user's three-compartment design, but it stops at two and uses linear FiLM rather than the full Feedback Transformer.

The user's program calls for at least three compartments, with full Feedback-Transformer integration. This is a natural target for PRISM v3 / Recurrent ViT v2.

## Open questions

1. **How many compartments?** Three has worked empirically. Whether four or more compartments adds capability or just compute overhead is open.
2. **Should compartments be paired with explicit cortical-area analogs (V1, V2, V4, IT)?** The user's program leans toward yes for interpretability; alternative designs (e.g., compartments organized by timescale alone, without spatial-area pairing) are not yet tested.
3. **What gating/decay schedule for each compartment?** Tallec & Ollivier chrono-initialization gives a principled starting point, but the right schedule for each compartment depends on the task.
4. **Capacity vs depth trade-off.** Should deeper compartments be smaller in component count and larger in channel dimension (the user's current choice)? Or larger overall with deeper channel-feature factorizations? Untested.
