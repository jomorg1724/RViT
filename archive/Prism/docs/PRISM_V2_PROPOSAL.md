# PRISM v2 — Hierarchical Predictive Coding with Slow/Fast Memory and Multi-Head Saliency

**Author:** Jonathan Morgan (drafted with Claude as research scribe)
**Date:** 2026-05-02
**Status:** Pre-implementation proposal. Defines the v2 architecture; v1 is locked at `prism-v1` per `PROJECT_PLAN.md` §1.
**Companion to:** `THESIS.md` (v1 manuscript and architecture writeup), `PROJECT_PLAN.md` (experimental roadmap), `PRISM_V2/Q_CRITIC.md` (action-value critic derivation added during v2 development). The original v1 design doc (`SPOTLIGHT_PROPOSAL.md`) was deleted when the project was pruned to PRISM v1 + v2 only; its content has been merged into `THESIS.md` §3.

---

## 0. Executive summary

PRISM v1 collapsed several design dimensions into their minimal forms in order to validate the core thesis — that an all-convolutional architecture with derived prediction-error attention, mnemonic feedback, and a single free-energy auxiliary objective can solve a Posner-style cued change-detection task. v1 has now crossed chance and is in characterization (Phases 1–11 of the project plan). The four scale-up axes that were intentionally deferred — and that emerged naturally from the v1 retrospective — are addressed here as the v2 architecture.

The four additions are: a second perceptual level (a V2-like stem) that produces a coarser-resolution feature map fed by V1; a dual recurrent memory consisting of fast and slow ConvGRU states with different time constants paired with different cortical levels; multi-head saliency at each level via partitioned feature decoders, so that the model can carry distinct "what is surprising about *this* feature subspace at *this* level" signals; and longer inner variational-inference loops with potentially different depths at each level. Cross-level Rao-Ballard error propagation closes the hierarchical predictive-coding loop and ties the slow memory's predictions to the fast memory's contents.

The total architecture grows from approximately 250K parameters in v1 to approximately 700K in v2 — still laptop-trainable. The single-objective bitter-lesson framing is preserved: no new auxiliary losses are added beyond per-level variational free-energy terms.

This document specifies the architecture mathematically, grounds each component in cortical neuroscience, gives a parameter budget, lays out a staged implementation roadmap (v2.1 → v2.2 → v2.3 → v2.4) so each addition is isolable for ablation, and registers the predicted differential effects each addition should have on the analyses in `PROJECT_PLAN.md`.

---

## 1. Motivation: which v1 limitations does v2 resolve

The v1 architecture has three structural limitations that the proposed v2 additions specifically resolve. None of these were defects of v1 — each was a deliberate simplification for the validation phase — but each is now a ceiling on what v1 can plausibly do.

The first limitation is the single-channel saliency map. Because $S_t$ collapses the prediction error across all feature channels into one scalar per location, the architecture cannot carry distinct "color novelty," "orientation novelty," and "spatial-frequency novelty" signals separately. In primate cortex these are coded by distinct populations (the color-selective regions in V4, orientation-selective columns in V1, and so on) and are read out separately by downstream attention circuits. A single saliency channel forces the model to either average these out (losing diagnostic information) or to use the channel as whichever is most behaviorally informative (effectively becoming task-specialized in a way that violates the bitter-lesson framing). Multi-head saliency via the partitioned-decoder construction (the "Recipe 1" of the v2-scaling discussion) gives the architecture distinct heads, each specialized to a feature subspace inherited from the upstream stem.

The second limitation is the single recurrent memory state. v1 uses a single $M_t$ that must simultaneously hold cue identity (constant across the trial), per-quadrant baseline orientations (slowly drifting under per-frame noise), per-quadrant change indicators (zero until $t^\star$, then nonzero), and a running decision evidence accumulator. These have wildly different timescales — the cue is stable across all 30 frames; the decision evidence is recomputed every frame. Forcing one ConvGRU with one set of forget-gate biases to handle both timescales is the recurrent analogue of asking a single capacitor to function as both a long-term storage cell and a high-pass filter. The literature on dual-timescale recurrence (Mujika et al., 2017 fast-slow RNNs; Tallec & Ollivier, 2018 chrono-init) and the prefrontal cortex literature on persistent versus transient activity (Goldman-Rakic, 1995; Constantinidis et al., 2018) both argue for explicit timescale separation. v2 introduces $M^\text{fast}$ and $M^\text{slow}$ with structurally different gating biases, paired with the V1 and V2 levels respectively.

The third limitation is the absence of true hierarchical predictive coding. v1 has feedback in the FiLM pathway and a generative decoder, which is the *form* of predictive coding, but it is single-level. The actual Rao & Ballard (1999) construction has predictions flowing down at every level of the hierarchy and errors flowing up at every level, with each level's posterior computed from its own residual error. Without this, v1 cannot exhibit the canonical predictive-coding signatures that the framework was designed to explain — extra-classical receptive-field effects at lower levels driven by predictions from higher levels, gain modulation at one level conditional on context at another, and the precision-weighting interpretation of attention as a confidence on the prediction error at each level. v2 closes this loop with a V2 stem, a second decoder, and a cross-level error propagation pathway.

Inner-loop compute depth is not strictly a v1 limitation — the loop exists with $K = 2$ in v1 — but the project plan's Phase 7 will sweep $K$ as a v1 ablation. v2 inherits the construction and extends it with potentially different iteration counts at each level ($K^\text{fast}$, $K^\text{slow}$), motivated by the observation that higher-level posterior computations may benefit from more iterations than lower-level ones.

---

## 2. Architecture overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│  PRISM v2 — per-step computation at env step t                             │
└────────────────────────────────────────────────────────────────────────────┘

  x_t ∈ ℝ^(B,3,50,50)
        │
        ▼
   ┌─────────────────────┐         M_slow_{t-1} ∈ ℝ^(B,C_M^slow,6,6)
   │  V1 stem            │              │
   │  (V1-like)          │              │   (top-down FiLM_V1)
   │  → V1_t ∈ (B,64,12,12) ◄───────────┤
   └─────────────────────┘              │
        │ (feedforward)                 │
        ▼                               │
   ┌─────────────────────┐              │
   │  V2 stem            │              │
   │  (V2/V4-like)       │              │
   │  → V2_t ∈ (B,128,6,6) ◄────────────┤
   └─────────────────────┘              │
        │                               │
        ▼                               │
                                        │
   ┌──── V1 LEVEL ──────────────────────┤
   │                                    │
   │  M_fast_{t-1}  (B, C_M^fast, 12, 12)
   │     │                              │
   │     ├─► g_V1^(k) for k=1..K_fast: predict V1_t per feature head
   │     │       │                      │
   │     │       └► E_V1^(k), S_V1^(k) ∈ ℝ^(B,K_fast,12,12)
   │     │              │               │
   │     │              ├──► error-gated GRU update of M_fast
   │     │              ├──► inner WM loop on M_fast (K_fast inner iters)
   │     │              └──► decision-readout pool from M_fast
   │     │
   │     └─► E_V1 sent UP to V2-level GRU (Rao-Ballard error propagation)
   │
   └──── V2 LEVEL ────────────────────────────────────────────────────────┐
                                                                          │
        M_slow_{t-1}  (B, C_M^slow, 6, 6)                                 │
           │                                                              │
           ├─► g_V2^(k) for k=1..K_slow: predict V2_t per feature head    │
           │       │                                                      │
           │       └► E_V2^(k), S_V2^(k) ∈ ℝ^(B,K_slow,6,6)               │
           │              │                                               │
           │              ├──► error-gated GRU update of M_slow           │
           │              │       (with extra input: pooled E_V1 from V1) │
           │              ├──► inner WM loop on M_slow (K_slow inner iters)
           │              └──► decision-readout pool from M_slow          │
           │                                                              │
           └─► top-down FiLM into V1-level pathway (loops back up)        │
                                                                          │
   ┌──── DECISION ────────────────────────────────────────────────────────┘
   │
   │  s_t = [GAP(M_fast_d), saliency_pool(M_fast_d, S_V1),
   │         GAP(M_slow_d), saliency_pool(M_slow_d, S_V2),
   │         coarse_grid(M_fast_d, S_V1, G=2),
   │         coarse_grid(M_slow_d, S_V2, G=1)]
   │  ∈ ℝ^(B, decision_dim)
   │
   │  π(a|s) = softmax(MLP(s_t))
   │  V(s)   = MLP(s_t)
   ▼
   action a_t  →  env  →  (x_{t+1}, r_t, done_t)

   Auxiliary loss (single objective, per-level VFE):
     L_PC = L_PC^V1 + λ_2 · L_PC^V2
   where each L_PC^level is the (forward + autoenc + feature) sum from v1.
```

The v2 architecture preserves v1's per-step pipeline structure but doubles it across two cortical levels, with cross-level connections (feedforward stem, top-down FiLM, bottom-up error propagation) that close the hierarchical predictive-coding loop. Sections 3.1–3.10 specify each component.

---

## 3. Components

### 3.1 V1 stem (V1-like primary visual cortex)

The V1 stem is unchanged from v1: three convolutional layers with strides $(2, 2, 1)$, kernel sizes $(5, 3, 3)$, channel counts $(C_{V_1}/2, C_{V_1}, C_{V_1})$ with $C_{V_1} = 64$, GroupNorm, GELU. Output: $V_1^t \in \mathbb{R}^{B \times 64 \times 12 \times 12}$.

The biological correlate is unchanged (V1 simple cells; Hubel & Wiesel, 1962). v2 adds the V2 stem on top of this layer.

### 3.2 V2 stem (V2/V4-like extrastriate cortex)

The V2 stem takes $V_1^t$ as input and produces a coarser, higher-channel-count feature map. Two conv layers:

$$
V_2^{(1)} = \mathrm{GELU}\!\left(\mathrm{GN}_8\!\left(\mathrm{Conv}_{C_{V_1} \to C_{V_2}, k=3, s=2, p=1}(V_1^t)\right)\right) \in \mathbb{R}^{B \times C_{V_2} \times 6 \times 6}
$$

$$
V_2^t = \mathrm{GELU}\!\left(\mathrm{GN}_8\!\left(\mathrm{Conv}_{C_{V_2} \to C_{V_2}, k=3, s=1, p=1}(V_2^{(1)})\right)\right) \in \mathbb{R}^{B \times C_{V_2} \times 6 \times 6}
$$

with $C_{V_2} = 128$. The spatial halving $12 \to 6$ matches the four-Gabor scene structure: $V_2^t$ has exactly one cell per Gabor patch quadrant, plus surrounding context. This is deliberate but not enforced — the network discovers whether to use this resolution as quadrant-aligned or otherwise.

The biological correlate is V2/V4: receptive fields larger than V1, orientation-and-color tuning, contour and texture sensitivity. The doubling of channel count from 64 to 128 mirrors the well-documented increase in feature-dimension expansion as one ascends the ventral stream (Felleman & Van Essen, 1991; DiCarlo, Zoccolan, & Rust, 2012).

Parameter cost: $64 \cdot 128 \cdot 9 + 128 \cdot 128 \cdot 9 = 73{,}728 + 147{,}456 = 221{,}184$ weights, plus norms. This is a significant fraction of the v2 total budget but is the irreducible cost of adding a perceptual level.

### 3.3 Slow/fast recurrent memory dyad

v2 maintains two recurrent states with structurally different gating biases.

The fast memory $M^\text{fast}_t \in \mathbb{R}^{B \times C_M^\text{fast} \times 12 \times 12}$ with $C_M^\text{fast} = 32$ tracks per-frame visual statistics paired with the V1 level. Its ConvGRU is structurally identical to v1's, with update-gate bias $b_u^\text{fast} = -1$ (so $\sigma(-1) \approx 0.27$ — moderate writing).

The slow memory $M^\text{slow}_t \in \mathbb{R}^{B \times C_M^\text{slow} \times 6 \times 6}$ with $C_M^\text{slow} = 64$ tracks trial-spanning facts paired with the V2 level. Its ConvGRU has update-gate bias $b_u^\text{slow} = -3$ (so $\sigma(-3) \approx 0.05$ — strongly conservative writing) and an analogous reset-gate bias toward "preserve memory." This is the chrono-initialization argument of Tallec & Ollivier (2018): by biasing the update gate toward zero, the cell's effective time constant is set to multiple environmental steps regardless of input magnitude. For a constant gate value $u$, the impulse-response halflife is $\tau_{1/2} = \log 2 / \log(1/(1-u))$, so $u = 0.05$ gives $\tau_{1/2} \approx 13.5$ steps — comfortably longer than the 11–25 step episode window.

The asymmetric parameterization is the architectural reason the two memories specialize. Without it, two GRUs would be redundant; with it, one becomes a per-frame integrator and the other becomes a near-stationary context store. The mathematical formulation of each is the v1 ConvGRU (specified in Section 2.7 of the v1 spec) with the bias values changed.

The biological correlate is the dual-timescale organization of cortex: fast dynamics in early visual areas (V1 LFP power peaks at gamma frequencies, ~30–80 Hz); slow dynamics in dorsolateral prefrontal cortex (delay-period activity persists for seconds; Funahashi et al., 1989; Goldman-Rakic, 1995). The Mujika et al. (2017) fast-slow RNN architecture is the closest direct ML antecedent.

Parameter cost: $M^\text{fast}$ ConvGRU: similar to v1 ≈ 100K params (same channel count 32, same conv kernels). $M^\text{slow}$ ConvGRU: $C_M^\text{slow} = 64$ paired with $C_{V_2} = 128$ inputs; the conv input dimensions are $(64 + 128 + 128)$ for the full candidate input = $320$, with output $64$, kernel $3 \times 3$: $320 \cdot 64 \cdot 9 \approx 184$K, plus the simpler reset and update gate convs. Total $M^\text{slow}$ GRU ≈ 280K. Combined: ≈ 380K (the largest single component of v2).

### 3.4 Top-down FiLM modulation, hierarchical

v1's FiLM modulation goes from $M_{t-1}$ to $V_t$. v2 generalizes this to two modulation pathways, both running per-step.

The within-level fast modulation $\gamma^\text{fast}, \beta^\text{fast}$ is computed from $M^\text{fast}_{t-1}$ and modulates $V_1^t$ before it is consumed by the V1-level error computation. This is structurally identical to v1's FiLM, with the same shapes and the same identity-at-init scheme.

The cross-level slow modulation $\gamma^\text{slow}, \beta^\text{slow}$ is computed from $M^\text{slow}_{t-1}$ and modulates either $V_2^t$ (the V2-level analogue of v1 FiLM) or, as a stronger top-down option, modulates $V_1^t$ directly via a learned upsample. We adopt the latter because it implements a cleaner Reynolds–Heeger-style top-down attentional bias from a higher cortical area down to V1:

$$
\gamma^\text{slow}_t = \mathrm{Upsample}_{6 \to 12}\!\left(\mathrm{Conv}_{1 \times 1}^{C_M^\text{slow} \to C_{V_1}}(M^\text{slow}_{t-1})\right) \in \mathbb{R}^{B \times C_{V_1} \times 12 \times 12}
$$

The upsample is bilinear and parameter-free; the $1 \times 1$ conv produces the per-channel modulation vector at coarse resolution. Both fast and slow modulations are then applied:

$$
P_1^t = \gamma^\text{slow}_t \odot \big(\gamma^\text{fast}_t \odot V_1^t + \beta^\text{fast}_t\big) + \beta^\text{slow}_t.
$$

Each modulation initializes to identity ($\gamma$-bias 1, $\beta$-bias 0). The composition order is "fast first, then slow on top," reflecting the cortical observation that within-area recurrence is faster than cross-area feedback. Reynolds and Heeger (2009) propose precisely this kind of multiplicative-gain composition at each level of the visual hierarchy.

Parameter cost: fast FiLM ≈ 4K (as in v1); slow FiLM with upsample ≈ 8K. Combined: ≈ 12K.

### 3.5 Per-level pixel and feature decoders

Each level has its own generative decoder that produces top-down predictions of the level's bottom-up features. We retain the v1 pattern of having both a pixel decoder (the dominant collapse-proof PC target) at the V1 level and a feature decoder used internally for the inner WM loop.

The V1-level pixel decoder $\tilde g_{V_1}: M^\text{fast}_{t-1} \to \hat x_t \in \mathbb{R}^{B \times 3 \times 50 \times 50}$ is the same as v1's, structurally and parametrically. It produces the pixel-level prediction error that defines the V1-level saliency.

The V1-level feature decoder $g_{V_1}: M^\text{fast}_{t-1} \to \hat V_1^t \in \mathbb{R}^{B \times C_{V_1} \times 12 \times 12}$ is also structurally identical to v1's, but is now split into $K^\text{fast}$ heads as specified in Section 3.6.

The V2-level feature decoder $g_{V_2}: M^\text{slow}_{t-1} \to \hat V_2^t \in \mathbb{R}^{B \times C_{V_2} \times 6 \times 6}$ is new. It is structured as $g_{V_1}$ but operates at the coarser V2 resolution. It is split into $K^\text{slow}$ heads.

We do *not* add a V2-level pixel decoder. The V1-level pixel decoder already provides the dominant collapse-proof PC anchor, and adding a second one would not contribute additional grounded supervision (it would just be redundant). The V2 level relies on the feature-PC term against $V_2^t$; collapse is prevented because $V_2^t$ is itself bottom-up-driven through the V1 pixel-PC anchor (the chain $\text{stem}_{V_1} \leftarrow \text{stem}_{V_2}$ is gradient-connected).

Parameter cost: pixel decoder ≈ 7K (v1 size); feature decoders $g_{V_1}, g_{V_2}$ scale with channels: $g_{V_1} \approx 28$K (v1), $g_{V_2} \approx 65$K (larger because $C_{V_2} > C_{V_1}$). Combined: ≈ 100K.

### 3.6 Multi-head saliency via partitioned feature decoders (Recipe 1)

At each level, the feature decoder is partitioned into $K$ parallel "heads," each predicting a disjoint subset of the feature channels of that level. Concretely at V1: the feature decoder $g_{V_1}$ is replaced by $K^\text{fast}$ parallel decoders $g_{V_1}^{(k)}$, each mapping $M^\text{fast}_{t-1}$ to $\hat V_1^{(k), t} \in \mathbb{R}^{B \times C_{V_1} / K^\text{fast} \times 12 \times 12}$, the prediction of one $C_{V_1}/K^\text{fast}$-channel slice of $V_1^t$. Each head produces its own saliency map:

$$
S_{V_1}^{(k), t}(i, j) = \sqrt{\frac{K^\text{fast}}{C_{V_1}}\sum_{c \in \mathrm{group}(k)} \left(V_{1, c, i, j}^{t} - \hat V_{1, c, i, j}^{(k), t}\right)^{\!2} + \epsilon}
$$

stacking gives $S_{V_1}^t \in \mathbb{R}^{B \times K^\text{fast} \times 12 \times 12}$.

The same construction applies at V2 with $K^\text{slow}$ heads.

Crucially, each head's saliency now amplifies a corresponding subspace of the memory state. The fast memory is split into $K^\text{fast}$ groups of $C_M^\text{fast} / K^\text{fast}$ channels, and the per-head saliency $S_{V_1}^{(k), t}$ amplifies the update gate only for the channels in group $k$:

$$
u_{t, k, c, i, j}^{\text{fast}} = u^\text{base, fast}_{t, k, c, i, j}\,\big(1 + \lambda^\text{fast}\,\bar S_{V_1}^{(k), t}(i, j)\big), \quad c \in \mathrm{group}(k).
$$

This is the direct analogue of multi-head attention's per-head value projection in transformers (Vaswani et al., 2017). Heads specialize because they see disjoint feature channels of $V$, and the V1 stem's emergent channel groupings — which we expect to track distinct visual feature dimensions — are inherited by the saliency heads.

Default head counts: $K^\text{fast} = 4$, $K^\text{slow} = 4$. With $C_{V_1} = 64$ and $K^\text{fast} = 4$, each fast head sees 16 channels; with $C_{V_2} = 128$ and $K^\text{slow} = 4$, each slow head sees 32 channels. Both should be more than enough capacity per head.

Parameter cost: feature decoders are *not* increased in total parameter count by partitioning, because the head decoders share the structural form of the v1 single decoder, only with each producing $1/K$ as many output channels. The overhead is the per-head $1 \times 1$ projection from $C_M$ to the head's hidden dimension, which is small.

### 3.7 Per-level error-gated GRU memory updates

The v1 ConvGRU update is generalized for two memories, each with its own per-level multi-head saliency.

For the fast memory:

$$
M^\text{fast}_t = (1 - u^\text{fast}_t) \odot M^\text{fast}_{t-1} + u^\text{fast}_t \odot \tilde C^\text{fast}_t
$$

with $u^\text{fast}_t$ as in Section 3.6 and the candidate $\tilde C^\text{fast}_t$ computed from $[r^\text{fast}_t \odot M^\text{fast}_{t-1}, P_1^t, E_{V_1}^t]$ where $E_{V_1}^t$ is the concatenated per-head error volume.

For the slow memory:

$$
M^\text{slow}_t = (1 - u^\text{slow}_t) \odot M^\text{slow}_{t-1} + u^\text{slow}_t \odot \tilde C^\text{slow}_t
$$

with the candidate computed from $[r^\text{slow}_t \odot M^\text{slow}_{t-1}, V_2^t, E_{V_2}^t, \mathrm{Pool}_{12 \to 6}(E_{V_1}^t)]$. The new last term — the spatially pooled V1-level error fed up to the V2-level GRU — implements the bottom-up-error component of Rao-Ballard hierarchical PC. The slow memory is informed not only by what it *itself* fails to predict (V2 error) but also by what the level *below* it failed to predict (pooled V1 error). This is the canonical "errors flow up" pattern.

Update-gate biases: $b_u^\text{fast} = -1$ (write moderately, as in v1), $b_u^\text{slow} = -3$ (write rarely, conservative integration).

### 3.8 Inner variational-inference loops, per level

Each memory has its own inner loop, structurally identical to v1's, with potentially different iteration depths. The fast loop does $K^\text{inner, fast}$ iterations of free-energy gradient descent on $M^\text{fast}$; the slow loop does $K^\text{inner, slow}$ iterations on $M^\text{slow}$. Both use weight-tied error blocks per level.

The motivation for allowing different depths is that higher-level posteriors involve more abstract bindings (cue identity + reward magnitude + validity prior) and may benefit from more iterations to settle, whereas the V1-level posterior is closer to direct sensory evidence. Default: $K^\text{inner, fast} = 2$ (v1's value), $K^\text{inner, slow} = 4$. Both are swept in the v2 analogue of `PROJECT_PLAN.md` Phase 7.

A more aggressive alternative — adaptive computation time (Graves, 2016; PonderNet of Banino et al., 2021) — would set $K$ per-trial via a halting criterion derived from the residual norm. v2 leaves this as a future direction.

### 3.9 Decision readout, hierarchical

The decision readout combines pools from both memories. Per-level, the readout is structurally analogous to v1's: a $1 \times 1$ projection to evidence channels, then global-average, saliency-weighted, and coarse-grid pools.

$$
d^\text{fast}_t = \mathrm{Conv}_{1 \times 1}^{C_M^\text{fast} \to D}(M^\text{fast}_t) \in \mathbb{R}^{B \times D \times 12 \times 12}
$$

$$
d^\text{slow}_t = \mathrm{Conv}_{1 \times 1}^{C_M^\text{slow} \to D}(M^\text{slow}_t) \in \mathbb{R}^{B \times D \times 6 \times 6}
$$

with $D = 8$. For each, the three pools defined in v1's Section 4.6 are computed: a global mean ($\in \mathbb{R}^{D}$), a saliency-weighted global mean ($\in \mathbb{R}^{D}$ per head), and a coarse-grid pool ($\in \mathbb{R}^{D \times G \times G}$ for the fast memory at $G = 2$; $G = 1$ for the slow memory because the spatial resolution is already only $6 \times 6$).

The full state vector $s_t$ is the concatenation of all of these. With $K^\text{fast} = K^\text{slow} = 4$ and $D = 8$:

$$
\dim(s_t) = \underbrace{D}_{\mathrm{GAP fast}} + \underbrace{4 D}_{\mathrm{sal-pool fast}} + \underbrace{4 D \cdot 4}_{\mathrm{coarse-grid fast}} + \underbrace{D}_{\mathrm{GAP slow}} + \underbrace{4 D}_{\mathrm{sal-pool slow}} = D \cdot (1 + 4 + 16 + 1 + 4) = 26 D = 208.
$$

The actor and critic are MLPs with hidden dimension 128 over this 208-d vector. Total head parameter cost: $\approx 56$K combined.

### 3.10 Cross-level error propagation: closing the Rao-Ballard loop

The hierarchical predictive-coding pattern requires both top-down predictions and bottom-up errors. v2 has both. Top-down predictions flow via FiLM from $M^\text{slow}$ to the V1-level features (Section 3.4). Bottom-up errors flow via the inclusion of the spatially pooled V1-level error in the V2-level GRU input (Section 3.7).

This bidirectional flow means the two levels are not independent recurrent stacks: they form a single coupled dynamical system whose joint fixed point minimizes the sum of free energies at both levels. In the variational interpretation, this is precisely the Rao-Ballard architecture's fixed-point computation: each level's posterior is a function of the level above's prediction and the level below's error. PRISM v2 is, structurally, the simplest two-level instance of this.

The cross-level coupling is also where the slow/fast specialization gets enforced empirically. Without coupling, the two memories would just be parallel models trained on the same input. With coupling — V1 errors feeding V2 updates, V2 predictions modulating V1 perception — the fast memory's contents become the substrate that the slow memory tries to explain, and the slow memory's contents become the substrate that biases what the fast memory expects to see.

---

## 4. The variational free-energy framework, extended

The v1 free-energy interpretation extends naturally to two levels. Define a generative model with two latent layers $M^\text{fast}_t, M^\text{slow}_t$ and one observation $x_t$:

$$
p(x_{1:T}, M^\text{fast}_{1:T}, M^\text{slow}_{1:T}) = \prod_{t} p(x_t \mid M^\text{fast}_t)\, p(M^\text{fast}_t \mid M^\text{fast}_{t-1}, M^\text{slow}_t)\, p(M^\text{slow}_t \mid M^\text{slow}_{t-1}).
$$

Under Gaussian likelihood assumptions and point-estimate posteriors (the same simplifications as v1), the variational free-energy decomposes into three accuracy terms:

$$
F_t \;\propto\; \underbrace{\big\|x_t - \tilde g_{V_1}(M^\text{fast}_{t-1})\big\|^2}_{\mathrm{V1\ pixel\ accuracy}} \;+\; \underbrace{\big\|V_1^t - g_{V_1}(M^\text{fast}_{t-1})\big\|^2}_{\mathrm{V1\ feature\ accuracy}} \;+\; \underbrace{\big\|V_2^t - g_{V_2}(M^\text{slow}_{t-1})\big\|^2}_{\mathrm{V2\ feature\ accuracy}}
$$

plus the autoencoding analogue of each (predicting from the post-GRU memory $M^\text{fast}_t, M^\text{slow}_t$ instead of from $M^\text{fast}_{t-1}, M^\text{slow}_{t-1}$), which serves the same cold-start-prevention role as in v1.

The total auxiliary loss is

$$
\mathcal{L}_\text{PC} = \alpha_\text{pix}\,\mathcal{L}_\text{pix}^{V_1, \text{fwd}} + \alpha_\text{auto}\,\mathcal{L}_\text{pix}^{V_1, \text{auto}} + \alpha_\text{feat}^{V_1}\,\mathcal{L}_\text{feat}^{V_1, \text{fwd}} + \alpha_\text{feat}^{V_2}\,\mathcal{L}_\text{feat}^{V_2, \text{fwd}} + \alpha_\text{feat-auto}^{V_2}\,\mathcal{L}_\text{feat}^{V_2, \text{auto}}.
$$

Default coefficients: $(\alpha_\text{pix}, \alpha_\text{auto}, \alpha_\text{feat}^{V_1}, \alpha_\text{feat}^{V_2}, \alpha_\text{feat-auto}^{V_2}) = (1.0, 1.0, 0.1, 0.5, 0.5)$. The V2 feature term is given a higher coefficient than the V1 feature term because the V1 level already has the dominant pixel anchor; the V2 level needs the feature term to be strong enough to drive non-trivial slow-memory representations.

This is the *only* auxiliary loss. No task-specific term is added. Bitter-lesson compliance is preserved.

---

## 5. Auxiliary losses summary

For the avoidance of doubt: v2 adds *no* new families of auxiliary loss relative to v1. It adds *terms* of the same family — variational free-energy / predictive-coding error, instantiated at a second hierarchical level. The full taxonomy is:

The forward V1 pixel PC term, exactly as in v1 ($\alpha_\text{pix} = 1.0$). The autoencoding V1 pixel PC term, exactly as in v1 ($\alpha_\text{auto} = 1.0$). The forward V1 feature PC term, exactly as in v1 ($\alpha_\text{feat}^{V_1} = 0.1$). The new forward V2 feature PC term ($\alpha_\text{feat}^{V_2} = 0.5$). The new autoencoding V2 feature PC term ($\alpha_\text{feat-auto}^{V_2} = 0.5$). The optional slowness regularizer on either memory (off by default, as in v1).

None of these references the cue, the change, the reward palette, or the trial timeline. Each is appropriate for any temporal sensory environment.

---

## 6. Parameter budget

| Module | Params (approx.) |
|---|---|
| V1 stem | 58K |
| V2 stem | 221K |
| Fast FiLM | 4K |
| Slow FiLM (with upsample) | 8K |
| V1 pixel decoder $\tilde g_{V_1}$ | 7K |
| V1 feature decoder $g_{V_1}$ ($K^\text{fast}=4$ heads) | 28K |
| V2 feature decoder $g_{V_2}$ ($K^\text{slow}=4$ heads) | 65K |
| Fast ConvGRU | 100K |
| Slow ConvGRU (with V1 error input) | 280K |
| Inner ErrBlock fast | 9K |
| Inner ErrBlock slow | 18K |
| Fast decision readout | 0.5K |
| Slow decision readout | 0.5K |
| Actor MLP (208 → 128 → 2) | 27K |
| Critic MLP (208 → 128 → 1) | 27K |
| **Total** | **≈ 853K** |

Roughly 3.4× v1's 250K. Still small enough for laptop training; episode-rate scaling is approximately linear in parameter count per forward pass for this regime, so we expect ≈ 0.3 episodes/sec on the same hardware where v1 runs at 1 episode/sec. The 200K-iteration training budget ports directly.

If the V2 stem turns out to be the budget bottleneck and we need to cut it, the cleanest reduction is $C_{V_2} = 64$ instead of 128, which roughly halves the V2-stem parameter count to ≈ 110K and the V2 decoder to ≈ 33K, total saving ≈ 140K.

---

## 7. Training procedure

The v2 training schedule extends v1's three-stage curriculum.

The PC pretrain phase ($N_\text{pretrain} = 4000$, doubled from v1's 2000) forces action = 0 and trains only $\mathcal{L}_\text{PC}$. The doubling reflects the larger generative-model capacity that has to be brought to a non-trivial joint optimum before RL is introduced.

The inner-K warmup phase ($N_\text{K-warmup} = 8000$, also doubled) holds both inner-loop iteration counts at zero. Once the per-level feature decoders are non-trivial, both inner counts ramp to their target values simultaneously.

The full PPO + PC training proceeds as in v1 with the recurrent PPO loop, truncated BPTT at $T_\text{bptt} = 16$, GAE($\lambda = 0.95, \gamma = 0.95$), entropy coefficient $0.005$, learning rate $3 \times 10^{-4}$ (Adam), gradient clipping at $0.5$.

The single new hyperparameter is the cross-level loss balance $\alpha_\text{feat}^{V_2}$. We start at $0.5$ and sweep $\{0.1, 0.5, 1.0\}$ as part of the v2 ablation suite.

---

## 8. Implementation roadmap (staged additions)

The four v2 additions are independent enough that a clean ablation strategy is to add them one at a time. Each stage produces a sub-version that we can train, characterize, and then either lock or roll back.

**v2.1: multi-head saliency only.** Add the per-level head partitioning to v1 ($K^\text{fast} = 4$, no V2 stem yet). This is the cheapest addition (≈ 5K extra params, mostly readout plumbing) and tests whether the multi-head structure alone produces specialization that helps performance and interpretability. Re-run the canonical analyses (P2.2 psychometrics, P4.2 α trajectories now with per-head decomposition, P5 causal manipulations now per-head).

**v2.2: slow/fast memory only.** Add the slow ConvGRU paired with V1 features (no V2 stem yet, and v2.1's heads disabled). Slow memory has $C_M^\text{slow} = 64$ and operates at the V1 spatial resolution $12 \times 12$. The two memories are coupled via FiLM modulation but not via cross-level error flow (since there is only one level). Tests whether timescale separation alone helps cue maintenance across the delay (predicted to show in P6.1 cue-decoding stability).

**v2.3: hierarchical PC only.** Add the V2 stem and the V2-level feature PC term, with single (not multi-head) saliency at each level and single (not slow/fast) memory split per level. Tests whether the hierarchical generative model alone improves performance and produces V2-level representations that are decodable for higher-order task variables.

**v2.4: combined v2.** All three additions integrated. This is the final v2 architecture as specified in Sections 2–6.

Each stage is a separate `prism-v2.{1,2,3,4}` git tag. The full Phase 1–11 analysis suite runs at v2.4 once it's locked. Phases 7 (inner K) and 8 (ablations) get extended sub-rows for the staged comparisons v2.1, v2.2, v2.3 vs v2.4 vs v1, so the final ablation table reads the contribution of each addition individually.

A go/no-go gate at each stage: if v2.X does *not* outperform v1 on the headline metrics (asymptotic correctness, validity-effect magnitude, cue-decoding stability), we open the question of whether the addition is worth integrating into v2.4 at all. The expectation is that all three add value, but we don't preserve them dogmatically.

---

## 9. Predicted differential effects

Each v2 addition has a predicted differential effect on the analysis battery. These are pre-registered predictions; the final manuscript will report which were borne out.

The multi-head saliency (v2.1) is predicted to improve discriminability between feature-specific surprise types. Concretely: per-head $\alpha^{(k)}_i(t)$ trajectories should differ between trials with color-novel cues and trials with orientation-novel changes, in a way that is collapsed in v1's single-head saliency. The cross-temporal decoding analysis (P6.2) should show clearer feature-specific representational geometry.

The slow/fast memory (v2.2) is predicted to dramatically improve cue maintenance across the delay. Linear decodability of the cue from $M^\text{slow}$ at $t = 25$ should be far higher than decodability of the same information from v1's $M_t$ at $t = 25$. Conversely, the fast memory's per-frame statistics should show much stronger phase-locked dynamics with the Gabor onsets and the change frame.

The hierarchical PC (v2.3) is predicted to improve performance most when the cue carries higher-order information that requires V2-level abstraction. The reward-magnitude-effect analyses (P2.3, P4.8) should be larger in v2.3, because reward magnitude is a categorical (color-encoded) variable whose representation is most naturally V2-level.

The combined v2.4 should outperform any single-stage variant on a Pareto sense across all metrics. The headline expectation is that v2.4 reaches asymptotic correctness ≥ 0.8 (vs v1's projected ≥ 0.6 once trained) and exhibits a validity effect on detection threshold of at least 1.5× the magnitude observed in v1.

---

## 10. Risks and contingencies

A few risks specific to v2 that are not present in v1.

The slow memory may fail to learn if its update gate is too conservative. A slow gate bias of $-3$ produces $\sigma(-3) \approx 0.05$, meaning at random init the slow memory updates by only 5% per step. If the slow memory's content is uninformative and the gate doesn't learn to open in response to behaviorally relevant inputs, it remains uninformative permanently — the dual of the cold-start zero-attractor that motivated the v1 autoencoding fix. Mitigation: use a softer initial bias of $-1$ during the PC pretrain phase, then anneal to $-3$ during the inner-K warmup phase.

The cross-level error pooling (V1 errors feeding the V2 GRU) may dominate the V2-level update signal and prevent the slow memory from developing its own characteristic representations. Mitigation: add a learned per-level scaling on the cross-level error term, initialized small.

The multi-head decomposition may collapse to one effective head (the "head specialization failure" common in transformers). Mitigation: enforce orthogonality of the head-decoder projections via a soft regularization during early training, with the regularization annealed to zero.

The combined v2.4 may simply be too large to train stably with the current PPO setup. Mitigation: at each staged release, monitor PPO's KL divergence and clip-fraction metrics; if they drift outside the canonical ranges (KL > 0.05, clip-frac > 0.3), reduce learning rate by 2× and possibly increase the number of PPO epochs per update.

The V2 decoder's output prediction may simply become a copy of $V_2^t$ if the slow memory has enough capacity to encode it directly — the autoencoding term inside v2 is doing its job, but the *forward* prediction term may degenerate. Mitigation: monitor the gap between forward and autoencoding feature-PC losses at the V2 level. If they collapse to the same value (autoencoding-only solution), reduce $C_M^\text{slow}$.

---

## 11. Bitter-lesson audit

To make compliance with Section 1.4 of the v1 thesis explicit: v2 adds the following inductive biases relative to v1.

A second perceptual level (V2 stem) — generic to any visual environment, just adds one more conv layer. A second recurrent memory (slow GRU) — generic to any temporally extended task, just adds one more recurrent state. Multi-head structure on the saliency map and feature decoders — generic to any predictive-coding model, just splits the existing decoder into independent groups. Cross-level error and prediction propagation — generic to any hierarchical predictive-coding model, completes the Rao-Ballard architecture without task knowledge.

What v2 does *not* add: any task-specific regularizer, any cue probe, any reward-conditioned auxiliary, any architectural element that hard-codes the four-Gabor scene, the cue alphabet, the change-detection task structure, or the reward palette. The architecture is no more task-specific than v1 was; the only loss function is still per-level variational free energy.

The same v2 architecture, with no changes to the loss formula and no architectural surgery, would apply directly to moving MNIST (Phase 9 of the project plan), Atari, or any other partially observable visual control problem. The bitter-lesson generalization claim is preserved.

---

## 12. Connections to literature (additions relative to v1)

v2 cites the same foundational references as v1 (Friston, Rao & Ballard, Reynolds & Heeger, Itti & Koch, Carrasco, etc.) and adds the following:

For dual-timescale recurrence: Mujika, Meier, & Steger (2017) on fast-slow RNNs, and Tallec & Ollivier (2018) on chrono-initialization as the principled way to set time constants in recurrent networks. For the prefrontal cortex's fast/slow dichotomy: the working-memory persistent-activity literature reviewed in Constantinidis et al. (2018), and the contrast with V1 gamma-band fast dynamics in Buzsáki & Wang (2012).

For hierarchical predictive coding architectures: Wen et al. (2018) on deep predictive coding networks for object recognition (the most recent serious attempt at a multi-level PC architecture in the deep-learning era), and Pinchetti et al. (2024)'s benchmarking of predictive-coding networks for the modern empirical baseline.

For multi-head attention as the analogue of multi-head saliency: Vaswani et al. (2017) for the original transformer formulation, and Voita et al. (2019) for the analysis of head specialization that motivates Recipe 1.

For the V2/V4 feature hierarchy: DiCarlo, Zoccolan, & Rust (2012) "How does the brain solve visual object recognition?" for the canonical mapping of cortical-area feature complexity onto a deep-learning hierarchy.

---

## 13. Decision points the user must approve before implementation begins

A small number of design decisions in v2 are deliberately left open in this proposal because they involve trade-offs that should be made explicitly rather than implicitly. These are:

The V2 channel count $C_{V_2}$ — 128 (the proposal default, total budget ~853K) versus 64 (smaller, total budget ~700K). Bigger gives more representational headroom but slower training.

The default head counts $K^\text{fast}, K^\text{slow}$ — 4 each (the proposal default) versus 2 (more conservative, less specialization risk) versus 8 (more aggressive). 4 is the standard transformer-attention default and is a reasonable starting point.

The inner-loop iteration counts $K^\text{inner, fast}, K^\text{inner, slow}$ — (2, 4) per the proposal default. This will be swept in v2's analogue of Phase 7, but the *initial* choice for v2.4 affects training compute.

Whether to fork v2 onto a separate git branch and develop it in parallel with the v1 manuscript polish, or to complete v1's Phase 1–11 first and then start v2 sequentially. The parallel approach is faster to a v2 result; the sequential approach is safer and means v1 results get the manuscript-grade attention they need.

I recommend defaults: $C_{V_2} = 128$, $K^\text{fast} = K^\text{slow} = 4$, $(K^\text{inner, fast}, K^\text{inner, slow}) = (2, 4)$, and sequential development. But these are calls you should make explicitly.

---

## Appendix A — Per-step pseudocode (v2.4 reference)

```python
def prism_v2_step(self, x_t, M_fast_prev, M_slow_prev):
    """
    x_t          : (B, 3, 50, 50)
    M_fast_prev  : (B, C_M^fast, 12, 12)
    M_slow_prev  : (B, C_M^slow, 6, 6)
    """
    # ── 3.1, 3.2  Feedforward perceptual hierarchy ─────────────────────────
    V1 = self.stem_V1(x_t)                                  # (B, 64, 12, 12)
    V2 = self.stem_V2(V1)                                   # (B, 128, 6, 6)

    # ── 3.4  Hierarchical FiLM (slow gates the V1-level pathway) ───────────
    g_fast = self.film_gamma_fast(M_fast_prev)              # (B, 64, 12, 12)
    b_fast = self.film_beta_fast(M_fast_prev)
    g_slow_up = F.interpolate(self.film_gamma_slow(M_slow_prev), size=12, mode='bilinear')
    b_slow_up = F.interpolate(self.film_beta_slow(M_slow_prev),  size=12, mode='bilinear')
    P1 = g_slow_up * (g_fast * V1 + b_fast) + b_slow_up      # (B, 64, 12, 12)
    # (V2-level FiLM analogously, modulating V2 from M_slow_prev. Omitted for brevity.)

    # ── 3.5, 3.6  Per-level multi-head decoders & saliencies ───────────────
    x_hat   = self.pixel_decoder(M_fast_prev)               # (B, 3, 50, 50)
    V1_hats = self.feature_decoder_V1(M_fast_prev)          # (B, K_fast, C_V1/K, 12, 12)
    V2_hats = self.feature_decoder_V2(M_slow_prev)          # (B, K_slow, C_V2/K, 6, 6)

    E_pix = x_t - x_hat
    S_pix = pixel_saliency_pool(E_pix, target_h=12, target_w=12)  # (B, 1, 12, 12)
    E_V1, S_V1 = multi_head_feature_error(V1, V1_hats)             # (B, K_fast, ...)
    E_V2, S_V2 = multi_head_feature_error(V2, V2_hats)             # (B, K_slow, ...)

    # ── 5  PC losses (forward + autoenc on pixel; per-level feature) ───────
    L_pix_fwd  = (E_pix ** 2).mean()
    L_V1_feat  = (E_V1  ** 2).mean()
    L_V2_feat  = (E_V2  ** 2).mean()

    # ── 3.7  Per-level error-gated GRU updates ─────────────────────────────
    M_fast = self.gru_fast(M_fast_prev, P1, E_V1, S_V1)
    E_V1_pooled = F.adaptive_avg_pool2d(E_V1.flatten(1, 2), output_size=6)  # (B, ..., 6, 6)
    M_slow = self.gru_slow(M_slow_prev, V2, E_V2, S_V2, extra_input=E_V1_pooled)

    # ── 3.8  Per-level inner variational-inference loops ───────────────────
    M_fast = self.inner_fast(M_fast, V1, decoder=self.feature_decoder_V1)  # K_inner_fast iterations
    M_slow = self.inner_slow(M_slow, V2, decoder=self.feature_decoder_V2)  # K_inner_slow iterations

    # ── 5  Autoenc PC term (using post-GRU memory) ─────────────────────────
    x_hat_auto    = self.pixel_decoder(M_fast)
    L_pix_auto    = ((x_t - x_hat_auto) ** 2).mean()
    V2_hats_auto  = self.feature_decoder_V2(M_slow)
    L_V2_feat_auto = multi_head_feature_error_loss(V2, V2_hats_auto)

    L_PC = (alpha_pix     * L_pix_fwd
          + alpha_auto    * L_pix_auto
          + alpha_V1_feat * L_V1_feat
          + alpha_V2_feat * L_V2_feat
          + alpha_V2_auto * L_V2_feat_auto)

    # ── 3.9  Hierarchical decision readout ─────────────────────────────────
    s_t = readout_concat(
        gap_fast       = GAP(d_fast := self.d_proj_fast(M_fast)),
        sal_pool_fast  = saliency_pool(d_fast, S_V1),               # per-head
        coarse_fast    = coarse_grid_pool(d_fast, S_V1, G=2),       # per-head
        gap_slow       = GAP(d_slow := self.d_proj_slow(M_slow)),
        sal_pool_slow  = saliency_pool(d_slow, S_V2),
    )

    # ── 3.10  Heads ────────────────────────────────────────────────────────
    action_logits = self.actor(s_t)                          # (B, n_actions)
    value         = self.critic(s_t)                          # (B,)

    return StepOutput(
        action_logits=action_logits, value=value,
        M_fast_next=M_fast, M_slow_next=M_slow,
        saliency_V1=S_V1, saliency_V2=S_V2,
        pc_loss=L_PC,
    )
```

---

## 14. Summary

PRISM v2 adds four neuroscientifically motivated and theoretically principled extensions to the v1 architecture: a second cortical-hierarchy level, a slow/fast recurrent memory dyad, per-level multi-head saliency via partitioned feature decoders, and longer per-level inner variational-inference loops with cross-level error and prediction flow that closes the Rao-Ballard loop. The total parameter budget grows to approximately 850K (still laptop-trainable), and the single-objective bitter-lesson framing is preserved — the only auxiliary loss remains variational free energy, now instantiated at two cortical levels. A staged implementation roadmap (v2.1 → v2.2 → v2.3 → v2.4) allows each addition to be ablated independently. Pre-registered predicted differential effects guide which manuscript figures should change at each stage. Implementation can begin once the open decision points in Section 13 are resolved.
