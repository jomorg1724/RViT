---
id: the_user_architectural_program
type: thread
title: "The user's architectural program: feedback transformers, multi-compartmental memory, and competition-emergent predictive coding"
source_documents:
  - "Private & Shared/Encoder-Decoder Architecture"
  - "Private & Shared-2/Classifier"
  - "Private & Shared-3/VAE"
  - "Private & Shared-4/Evolution of Architecture"
papers:
  - vaswani2017_attention
  - dosovitskiy2020_vit
  - hochreiter_schmidhuber1997_lstm
  - rao_ballard1999_predictive_coding
  - friston2010_fep_unified_theory
  - bastos2012_canonical_microcircuits
  - desimone_duncan1995_biased_competition
  - reynolds_heeger2009_normalization
  - felleman_vanessen1991_hierarchical_cortex
  - dicarlo2012_object_recognition
  - constantinidis2018_persistent_activity
  - mante2013_context_dependent_pfc
  - spratling2008_pc_biased_competition
  - kietzmann2019_recurrence_required
concepts:
  - feedback-transformer
  - gridcell-rnn
  - multi-compartmental-memory
  - bidirectional-hierarchical-feedback
  - competition-emergent-predictive-coding
  - multi-hub-multi-objective-system
  - iterative-variational-encoder-decoder
last_updated: "2026-05-22"
---

# The user's architectural program

This thread is the central organizing narrative of the database. Everything below was extracted from the user's personal research notes in the four `Private & Shared` folders. It is the architectural and theoretical program that the published Recurrent ViT (2502.10955), PRISM v1, and PRISM v2 are partial, simplified, or specialized instances of. Every paper in `papers/` is most usefully read as evidence for, foundation under, or contrast against one of the components catalogued here.

The program has five interlocking components: a self-attention primitive that admits arbitrary recurrent feedback (the Feedback Transformer); a recurrent-state primitive that combines spatially-independent processing with the Feedback Transformer (the GridCell RNN); a multi-compartmental, hierarchical, bidirectionally-connected memory system built from those primitives; an iterative variational encoder–decoder that uses those components as encoder and decoder hubs; and an original theoretical thesis — predictive coding as a strategy emerging from inter-coalition competition for limited neural resources — that motivates the entire architectural commitment.

---

## 1. The Feedback Transformer

The core architectural primitive. A standard transformer self-attention layer is augmented to integrate, at the level of the Q / K / V projections, an arbitrary number of recurrent internal states drawn from elsewhere in the architecture — from serial layers preceding (bottom-up), serial layers following (top-down), and parallel layers (multi-modal sensory integration).

For each recurrent state $C_i$, the Feedback Transformer projects $C_i$ into a per-state query $Q_{C_i}$, key $K_{C_i}$, and value $V_{C_i}$, and combines these with the bottom-up sensory projections $Q_S, K_S, V_S$ via element-wise broadcasting prior to the softmax. Concretely, the attention score for position $i$ becomes

$$
\alpha_{ij} \propto \big\langle s_{q,i} \odot \sum_k c^{(k)}_{q,i},\; s_{k,j} \odot \sum_k c^{(k)}_{k,j} \big\rangle
$$

where $\odot$ is the Hadamard product and the sum runs over all feedback sources $k$. Up to twelve feedback sources have been integrated successfully in the user's Video VAE work.

The structural constraint is that every feedback source has the same number of patches/tokens as the sensory input. Spatial mismatches between hierarchical layers are handled by patch-expansion / patch-reduction conv operations (next section).

The biological motivation is that cortical layer 6 corticocortical neurons are a major route for intra- and inter-hemispheric feedback (`weiler2025_l6_corticocortical`) — i.e., real cortex implements precisely this kind of integration of feedback from many sources into a single sensory processing stage. The complementary transthalamic feedback route (`sherman2022_ctc_loop`; causally confirmed by `mckinnon_mo_sherman2025_transthalamic_v1`) supplies the second long-range feedback path that runs in parallel.

### Why this matters for the published work

The Recurrent ViT paper (2502.10955) describes three variants of memory integration into self-attention (§6.7): tokens, additive, and multiplicative feedback. The published paper reports only on a single-layer instance of this with one feedback source ($H^{(t-1)}$). The Feedback Transformer is the general primitive of which all three published variants are special cases, and which licenses scaling to many parallel and hierarchical feedback sources.

PRISM v1's FiLM modulation (`THESIS.md` §2.4) is a strictly weaker variant: FiLM injects modulation only at the input to the feature stack, not into the attention mechanism itself, and uses only one feedback source ($M_{t-1}$). PRISM v2's hierarchical FiLM (`PRISM_V2_PROPOSAL.md` §3.4) goes one step in this direction but still uses linear modulation rather than the full Feedback-Transformer Q/K/V structure.

---

## 2. The GridCell RNN

A recurrent unit that combines an LSTM-style gated update with the Feedback Transformer. Maintains an internal grid of states $C_i^{(t)} \in \mathbb{R}^{n_{gh} \times n_{gw} \times n_{C_i}}$. The forward step proceeds in two stages.

Stage one is spatially-independent processing (SIP). Each grid cell is processed independently to produce an update proposal — analogous to the LSTM candidate cell — using only the previous grid state and the input $Z_i^{(t)}$ at that cell. Stage two is inter-cell and inter-grid integration: the Feedback Transformer takes the proposal as input, treats each grid cell as a token, and integrates feedback from an arbitrary set of other GridCell RNN states (parallel, deeper, shallower). The final update is a gated sum of the SIP proposal and the FT output.

The clean separation between SIP and FT integration is the architectural reason the system can scale to many memory layers without combinatorial blowup. SIP handles within-state computation in parallel; FT handles between-state communication.

---

## 3. Multi-compartmental, hierarchical, bidirectionally-connected memory

The architectural target is a stack of GridCell RNNs that implement a cortex-like visual hierarchy. The user's notes describe a 3-layer reference design.

**Layer 1** is paired with the V1-level visual features. Grid resolution $n_{gh}^{(1)} \times n_{gw}^{(1)}$ matches the patch grid; channel dimension $n_{C_1}$ is relatively small. Its update state is the bottom-up feedforward signal $Z_{X_1}$ from the V1 stem.

**Layer 2** is paired with V2/V4-level features. Grid resolution is halved; channel dimension is increased. The update state $Z_2$ is the sum of two pathways: a convolutional descending projection of $C_1$ (the memory contribution) and a parallel convolutional projection of $X_1$ (the sensory residual). Both pathways use learned conv stacks that simultaneously reduce spatial resolution and expand channel count.

**Layer 3** is paired with the most abstract level. The same descending construction repeats, yielding even coarser spatial resolution and larger channel count.

The key design choices are:

- **Descending projections** use spatially-reducing, channel-expanding conv filters. The user's rationale (Evolution of Architecture, "Descending Projections" section) is that these enforce spatially-oriented receptive fields with progressively larger RFs and progressively more featural abstraction — i.e., the canonical V1 → V2 → V4 → IT progression.
- **Ascending projections** use conv-transpose operations to reshape deeper memory states back to the spatial dimensions of shallower ones. Layer 0 receives feedback from $C_1$, $C_2^{(UP)}$, and $C_3^{(UP^2)}$. Layer 2 receives feedback from $C_2$ and $C_3^{(UP)}$. Layer 3 receives only its own $C_3$.
- **Diminishing feedback into deeper layers** is by design. Deeper layers have fewer feedback inputs and therefore more control over their internal representations — a power asymmetry the user explicitly motivates by analogy to the Hierarchical Reasoning Model (Wang et al. 2025, arXiv:2506.21734), which couples RNN modules running at different temporal update rates.
- **The ability to shut off feedback inputs** creates an incentive for cooperation between layers: a layer can decline to incorporate feedback from a hostile or noisy source, which means rival layers have to "play nice" to be heard.

The bidirectional, hierarchical, parallel structure is the canonical cortical loop: feedforward sensory input plus descending memory projections plus ascending memory projections plus lateral parallel-hub feedback, all integrated by a single Feedback Transformer at each level.

### Connection to the literature

The hierarchical V1 → V2 → V4 → IT structure is grounded in Hubel & Wiesel 1962, Felleman & Van Essen 1991, and DiCarlo et al. 2012 (all in the seed). The descending-feedback role of layer 6 corticocortical neurons is in [weiler2025_l6_corticocortical](../papers/weiler2025_l6_corticocortical.md) (cited in the Evolution document; in the DB at depth: full since 2026-05-16). The predictive-coding interpretation of the same hierarchy is in Rao & Ballard 1999, Friston 2010, and Bastos et al. 2012.

The dual-timescale aspect — fast updates at shallow layers, slow updates at deep layers — is also the central commitment of PRISM v2's slow/fast memory (`PRISM_V2_PROPOSAL.md` §3.3), citing Mujika et al. 2017 and Tallec & Ollivier 2018.

---

## 4. The iterative variational encoder–decoder

The encoder and decoder are structurally identical instances of the multi-compartmental memory stack defined above. Their interaction follows an iterative recurrent protocol.

**Forward reasoning ($n_{FR}$ steps).** The encoder is shown the same image (or the same video clip) repeatedly. At each pass, the encoder updates its internal "guide" state $H_t$: $H_{t+1} \leftarrow \psi_\theta(X, H_t)$. The hypothesis — supported by the classifier experiment on Food-101 — is that the encoder's self-attention dynamics evolve nontrivially even on a static image, exhibiting attractor-like trajectories that depend on the underlying image semantics. After $n_{FR}$ passes the encoder produces a final guide $H_{n_{FR}}$.

**Backward reasoning ($n_{BR}$ steps).** The decoder is initialized with $\tilde H_0 = H_{n_{FR}}$ and a learned latent $Z_0$. At each pass, the decoder produces an updated latent, updated state, and a reconstruction proposal: $(Z_{\tau+1}, \tilde H_{\tau+1}, \tilde X_{\tau+1}) \leftarrow \phi_\theta(Z_\tau, \tilde H_\tau)$. The reconstruction loss is weighted across all $n_{BR}$ proposals with an exponential schedule favoring later proposals: $\mathcal{L}_\text{recon} = \sum_i \gamma_i \cdot \text{MSE}[\tilde X_i, X]$ where $\gamma_i = e^{i - n_{BR}}$.

**Variational objective.** Treat the initial guide as a latent random variable $\tilde H_0 \sim q_\theta(\tilde H_0; H_{n_{FR}}) = \mathcal{N}(\mu_\theta(H_{n_{FR}}), \Sigma_\theta(H_{n_{FR}}))$. Place a unit Gaussian prior $p(\tilde H_0) = \mathcal{N}(0, I)$. Then the ELBO over the iterative rollout decomposes as

$$
\mathcal{L}_\text{ELBO} = \sum_i^{n_{BR}} \mathbb{E}_{q_\theta}\big[\log p_\theta^{(i)}(X \mid \tilde H_0)\big] - D_\text{KL}\big[q_\theta(\tilde H_0 \mid H_{n_{FR}}) \,\|\, p(\tilde H_0)\big]
$$

Under Gaussian likelihood, each expectation reduces to (negative) MSE between the reconstruction proposal and the target image, scaled by an inverse noise variance. The KL term collapses to the standard analytic Gaussian-vs-unit-Gaussian form.

**Multi-patch distributional latents.** The guide is actually a matrix $\tilde H_0 \in \mathbb{R}^{n_\text{patch} \times d_\text{guide}}$, not a vector. The user assumes a matrix-normal distribution $\mathcal{MN}(M, U, V)$ with row-covariance $U$ over patches and column-covariance $V$ over guide dimensions. Row-whitening via eigendecomposition of $U$ gives an equivalent representation in which the patch rows are independent. In practice the user enforces this approximately by adding an off-diagonal penalty $\mathcal{L}_\text{row-indep} = \|U - \text{diag}(U)\|_F^2$ on an empirical row-covariance.

**Why the variational structure matters.** The KL regularization induces three properties the user calls out as load-bearing for the program:

1. **Continuity / smoothness** of the guide-to-output mapping, so that small changes in the guide produce small changes in reconstruction.
2. **Disentanglement** of the latent space along axis-aligned factors of variation.
3. **Hopfield-like attractor dynamics** in the sampled guide space, with the prior ensuring the attractor landscape stays well-behaved rather than memorizing each training example.

The KL term is interpreted explicitly as the free-energy regularizer of Friston (2010): the VAE objective is variational free-energy minimization (point 4 in §1 of the Evolution of Architecture document).

### Connection to PRISM and the Recurrent ViT

The iterative-VAE construction is the user's *most ambitious* architecture; the published Recurrent ViT (2502.10955) is a single forward pass over a sequence with no backward reasoning chain, and PRISM v1 has an inner variational-inference loop (`THESIS.md` §2.8) over a single $M_t$ at each step but no parallel decoder pathway. Translating the user's program into a publishable result requires either reporting on the iterative-VAE results directly (the user's Video VAE work) or framing PRISM v1's inner loop as a single-stream approximation to the full $n_{FR} \to n_{BR}$ pipeline.

---

## 5. Competition-emergent predictive coding

The theoretical thesis the user develops in the Evolution of Architecture document is original and important enough to deserve its own treatment. Conventional predictive coding (Rao & Ballard 1999; Friston 2010) explains top-down feedback as predictions about *sensory* input that the brain expects to receive. The user's reformulation is that top-down feedback is, more fundamentally, predictions about the *behavior of competing neural coalitions*.

The argument has four steps.

**Step 1: resource scarcity.** The brain operates under strict metabolic and bandwidth constraints ([laughlin1998_metabolic_cost](../papers/laughlin1998_metabolic_cost.md), in the DB at depth: full). Different neural coalitions — sensory hubs, RL hubs, default-mode-style hubs, etc. — compete for these resources to ensure their representations are maintained and used to guide behavior.

**Step 2: game-theoretic landscape.** To win the competition, a coalition cannot be reactive; it must be proactive. It must predict the likely states and resource demands of its rivals.

**Step 3: feedback as opponent modeling.** Top-down feedback signals, in this view, are predictions of what competing coalitions are about to represent. The prediction-error signal is therefore a *strategic surprise* signal — an indication that a competing coalition acted in an unpredicted way. The error is used to update the coalition's internal model of the competitor, leading to better future predictions and stronger competitive advantage.

**Step 4: ubiquity of predictive architecture explained.** Predictive coding is observed in essentially every cortical area, including high-level association cortex with no obvious sensory-prediction role. The user's account explains this ubiquity: the relevant prediction is not of sensory input but of *internal competitors*, which exist at every level of the hierarchy. Sensory predictive coding is then just a special case where the "competitor" is the sensory periphery.

**Empirical test plan.** The user proposes building a multi-objective neural architecture with separate hubs (MSI, RL, VAE), each with its own memory states, all feeding back into a central self-attention mechanism. After training the system on tasks that put the hubs' objectives in conflict, train a separate decoder to predict the entire global internal state at $t+1$ from the global state at $t$. If iterative roll-out of this decoder produces long-range coherent prediction of internal states, that is evidence that a world model emerged implicitly from the competition, without any explicit world-model training signal.

This is a falsifiable, computationally tractable test of a substantive theoretical claim. It is the kind of contribution that makes the architectural program worth pursuing even independently of the change-detection or video-autoencoding benchmarks.

### Formal account of the competition

Hubs compete for control of the self-attention map by manipulating the inner-product space of Q and K. For each stimulus $S_i$ the final Q vector is $q_i = s_{q,i} \odot (c^{(\text{RL})}_{q,i} + c^{(\text{dec})}_{q,i})$ and similarly for $k_i$. The attention score $\alpha_i = \langle q_i, k_i \rangle$ is then a function of all hubs' contributions plus the sensory contribution. Each hub's optimal contribution depends on two predictions: (a) the bottom-up sensory projection $s_q, s_k$ — predicting the world; (b) the other hub's contribution $c^{(\text{other})}_q, c^{(\text{other})}_k$ — predicting the opponent. A hub with a better predictive model of both wins the attention competition more often, secures more of the representational bandwidth, and accomplishes its objective.

This is the architectural mechanism by which "predictive coding emerges from competition" is not a metaphor but a concrete optimization pressure that gradient descent on hub-specific losses will produce.

### Connection to literature

The biased-competition framework (Desimone & Duncan 1995; Reynolds et al. 1999) is the closest published analog at the cellular level. The user's contribution is to scale this from individual receptive fields to whole coalitions, and to identify the predictive-coding architecture as the natural strategic response. The connection to Schmidhuber's coupled-RNN framework (arXiv:1511.09249) is explicit: Schmidhuber proposes a predictive world model $M$ and a controller $C$ trained on different tasks, with $C$ learning to inspect and reuse $M$'s algorithmic information. The user's multi-hub system generalizes this to many objective-specific hubs, all of which both implement and exploit predictive models of the others.

---

## 6. Empirical results to date

The user reports moderate success on three task families with this architectural program.

**Static-image classification (Food-101 / "Classifier" note).** A recurrent ViT with patch-wise LSTM reaches near-100% train accuracy but plateaus at ~30% test accuracy on Food-101. Test accuracy improves with training-set size (15K → 75K nearly doubled it) and with the number of recurrent passes, but the model overfits aggressively. The interpretive observation that "attention dynamics evolve nontrivially over passes" is qualitatively confirmed via attention-map visualizations: maps focus, defocus, and reactivate over recurrent steps, mirroring primate-attention dynamics. The remaining challenge is sample efficiency / generalization.

**Video autoencoding ("Video VAE" / Evolution of Architecture).** A multi-layer RViT with up to twelve feedback sources successfully reconstructs UCF101 video clips. The "Reconstruction" and "Reconstruction with Attention Maps" figures in the Encoder-Decoder Architecture note demonstrate qualitatively coherent video reconstruction. This is the most successful empirical instance of the program so far.

**Eye-tracking ("Evolution of Architecture" §"Eye Tracking").** A hierarchical RViT with bidirectional feedback predicts human fixation locations, with the network's predicted fixation (red circle) tracking the true fixation (green dot) qualitatively. Layer-0 and layer-1 attention maps differ in spatial scale, as predicted by the hierarchical-feedback hypothesis.

**Change detection (Recurrent ViT paper, 2502.10955; PRISM v1, v2).** The published change-detection result is a single-layer, single-feedback-source instance of the program. PRISM v1 is the "no softmax-attention" antagonist that uses prediction error in place of learned attention. PRISM v2 reintroduces multi-head and dual-memory commitments without yet matching v1.

**HRA (Hierarchical Recurrent Attention), Posner change-detection, May 2026 (abandoned).** The first 3-layer instance of the program with explicit Feedback-Transformer cells and PPO training is in `HRA/` (project root `MODEL_DESIGN.md`). After ~4k PPO episodes the model failed to develop interpretable attention structure; abandoned 2026-05-19 in favor of RViT+. See **RViT+** entry below and the dedicated engineering thread `threads/rvit_plus_engineering.md` for the successor's design and iteration-by-iteration log. Two HRA-specific empirical findings worth preserving:

1. *Stability failure (iter 887, first run).* PPO + QR-DQN combination produced large Q-quantile residuals that the QR-Huber linear regime sustained as large gradients; |Q| drifted up, one bad backward pass produced NaN logits → `Categorical(NaN)` crash. Stability fixes shipped (`return_clip=5.0`, `kl_early_stop=0.02`, `actor_logit_clamp=20.0`, tighter LR + value-loss tuning); the post-fix 30-iter sanity run kept |Q|≤1.12 and gradient-norm ≤1.07.
2. *Information-flow failure (iter 1999, stabilised run).* Correct rate stuck below 0.50, policy frozen at 6% press, critic flat. Deep-dive traced cause: V-stem stimulus-responsive, C₁ weak, C₂ and C₃ frozen (cross-change Δ ≈ 10⁻⁵). 86% of decision features came from frozen layers. Architectural fix (D7 in `MODEL_DESIGN.md`): bottom-up skip connections V→C₂, V→C₃, C₁→C₃ (cortically motivated as L4 thalamic drive + L5 long-range projections); per-layer `LayerHead` reduction in `DecisionReadout` (preserves spatial structure of each layer). Net +22% params (1.73M → 2.11M) targeted at the identified bottleneck.

The **open empirical question** at the architectural-program level: the Feedback Transformer's spatial attention is essentially uniform across all layers and all 5 inner iterations after 4k+ episodes of PPO (entropy/max-entropy ≈ 1.000, Gini ≈ 0.03), and two of three cells learned a *negative* `ft_residual_scale`. This is the failure mode the Voita head-collapse prior (`voita2019_head_specialization`) predicts at the head level translated to the FT spatial-attention level: under sparse-reward PPO on a task that can be solved by global pooling (PRISM v1 demonstrates this), the FT sits at a flat minimum of the policy loss with no differentiating gradient. The D7 architectural fix attacks the upstream information-flow bottleneck but does not directly attack this attention-collapse trap; an attention-supervision auxiliary (e.g. a small KL penalty against a cue-derived location prior, applied only during the cue and change windows) is the next architectural intervention worth testing. See `concepts/feedback_transformer.md` open question 4 for the full analysis.

**RViT+, video-compression pretraining → Posner fine-tune, May 2026 (current).** The pivot after HRA. Same multi-compartmental-memory commitment (3 layers V1/V4/IT analog), same Feedback Transformer with `attn_bias` microstim plumbing, same retinotectal-analog skips — but with the supervision strategy inverted. Rather than expecting attention structure to emerge under sparse-reward PPO directly, RViT+ pretrains the encoder/decoder stack as a **video-compression autoencoder** (encode T frames → final state → VAE latent → decode T reconstructions) on dense per-pixel reconstruction supervision *before* attaching the RL controller. The architectural bet is that the FT, freed from the credit-assignment trap that froze HRA's attention, will develop spatial structure under reconstruction gradient pressure.

Iter-by-iter empirical log lives in `threads/rvit_plus_engineering.md`. Headlines through run 6 (2026-05-20):

- Runs 1–4 (per-frame autoencoding variants) all produced perfect recon with uniform attention — per-frame autoencoding does not pressure the FT because there is no temporal compression demand.
- Run 5 (video-compression mode) produced total collapse: zero spatial variance in all hidden states, all-black reconstructions, recon falling to MSE(0, video) = 0.02 — the trivial-mean-image minimum. Diagnosed as three compounding failure modes: (1) no positional embeddings → FT cannot break spatial symmetry; (2) FT had unilateral control over the candidate; (3) update gate removed → no recurrent memory protection.
- Run 6 (current, 2026-05-20) ships three surgical fixes documented in `concepts/gridcell_rnn.md` *Empirical refinements*: learned per-(channel, h, w) positional embeddings, SIP residual (`tilde_C = sip_candidate + ft_output`), restored LSTM update gate with bias=0 reactive baseline. Param count 1.18M → 1.36M. Verification (P1: attention entropy < 0.80×max on ≥50% of cells; P5: visible reconstructions) pending on the in-progress 2000-iter retrain.

The RViT+ approach also serves as an explicit empirical test of the architectural-program claim that dense reconstruction supervision is sufficient to develop attention structure — if Stage 1 (synthetic MovingMNIST compression) does not confirm P1, the FT-as-canonical-substrate commitment is in trouble. If it does, the bottleneck identified for HRA (sparse-reward credit assignment) is the actionable lever for downstream tasks: pretraining converts the credit-assignment problem into a fine-tuning problem.

---

## 7. Implications for the database's growth

Reading order for new papers added to this database should be:

1. Does the paper bear on the **Feedback Transformer** primitive — i.e., on multi-source memory feedback into self-attention? Most relevant: works on transformer attention with side information (Locatello slot-attention; Schmidhuber 2015 coupled-RNN; Mante-Sussillo PFC dynamics). Tag with `feedback-transformer`.

2. Does the paper bear on **multi-compartmental memory** — multiple recurrent units operating in parallel and communicating across hierarchical levels? Most relevant: hierarchical RNN literature; cortico-thalamo-cortical loops; Mujika fast-slow RNN. Tag with `multi-compartmental-memory`.

3. Does the paper bear on **bidirectional hierarchical feedback** — descending predictions and ascending errors? Most relevant: Rao-Ballard, Bastos canonical microcircuit, Friston FEP, Kietzmann recurrence required. Tag with `bidirectional-hierarchical-feedback`.

4. Does the paper bear on **competition-emergent PC** — the game-theoretic / resource-competition account? Most relevant: biased competition (Desimone & Duncan, Reynolds et al.), Schmidhuber coupled-RNN, multi-agent RL surveys. Tag with `competition-emergent-predictive-coding`.

5. Does the paper bear on the **iterative variational encoder–decoder** — the $n_{FR} \to n_{BR}$ reasoning structure? Most relevant: VAE literature, iterative-inference models, JEPA / V-JEPA. Tag with `iterative-variational-encoder-decoder`.

Papers that satisfy none of these but are still relevant (e.g., behavioral psychophysics from the Posner literature) anchor the *task* side of the program rather than the architectural side. They remain useful but should not crowd out the architectural reading list.

## 8. Open scholarly debts from the notes

**Status as of 2026-05-22: this list is fully discharged.** Every paper originally listed below has been added to the database, and every entry is at `depth: full`. This section is retained as a historical record of the cite-trail expansion from the user's private notes, with each item annotated by its canonical paper id. New scholarly debts surfaced by future deepening should be tracked in `INDEX.md` (priority queue) or in concept-/thread-file open-question sections rather than reopened here.

Canonical-id annotations (every item is at `depth: full`):

- ~~Laughlin, de Ruyter van Steveninck & Anderson (1998)~~ — [laughlin1998_metabolic_cost](research_db/papers/laughlin1998_metabolic_cost.md). Foundational for the resource-competition argument.
- ~~Edelman (1987)~~ — [edelman1987_neural_darwinism](research_db/papers/edelman1987_neural_darwinism.md). The original coalition-competition framing.
- ~~Buzsáki (2010)~~ — [buzsaki2010_cell_assemblies](research_db/papers/buzsaki2010_cell_assemblies.md). The "coalition" terminology.
- ~~Lee (2008)~~ — [lee2008_game_theory_neural](research_db/papers/lee2008_game_theory_neural.md). Game-theoretic landscape in the brain.
- ~~Schmidhuber (2015)~~ — [schmidhuber2015_learn_to_think](research_db/papers/schmidhuber2015_learn_to_think.md). Coupled-RNN predictive world models + controllers. **Caveat:** §4–5 reconstructed from prior knowledge; verify against PDF before manuscript citation (see HANDOFF.md §"Critical context").
- ~~Wang et al. (2025) HRM~~ — [wang2025_hierarchical_reasoning_model](research_db/papers/wang2025_hierarchical_reasoning_model.md). Hierarchical Reasoning Model with coupled H/L RNN modules. **Same caveat as Schmidhuber 2015.**
- ~~Higgins et al. (2017)~~ — [higgins2017_factorized_representations](research_db/papers/higgins2017_factorized_representations.md). Factorized representations for generalization. (Note: the same canonical entry covers the β-VAE work; the original list double-counted the citation.)
- ~~Manns & Eichenbaum (2006)~~ — [manns_eichenbaum2006_lec_mec](research_db/papers/manns_eichenbaum2006_lec_mec.md). LEC/MEC factorization in entorhinal cortex.
- ~~Sherman (2022)~~ — [sherman2022_ctc_loop](research_db/papers/sherman2022_ctc_loop.md). Functions of the cortico-thalamo-cortical loop.
- ~~Haber (2015)~~ — [haber2015_cbgtc_circuits](research_db/papers/haber2015_cbgtc_circuits.md). Cortico-basal-ganglia-thalamic circuits in goal-directed behavior.
- ~~Weiler, Teichert & Margrie (2025)~~ — [weiler2025_l6_corticocortical](research_db/papers/weiler2025_l6_corticocortical.md). L6 corticocortical neurons as the major route for intra/inter-hemispheric feedback.
- ~~Jordan et al. (2023)~~ — [jordan2023_dendritic_bayesian](research_db/papers/jordan2023_dendritic_bayesian.md). Conductance-based dendrites perform Bayes-optimal cue integration.
- ~~Senkowski & Engel (2024)~~ — [senkowski_engel2024_multi_timescale_msi](research_db/papers/senkowski_engel2024_multi_timescale_msi.md). Multi-timescale neural dynamics for multisensory integration.
- ~~Choi, Demir, Oh & Lee (2023)~~ — [choi2023_msi_review](research_db/papers/choi2023_msi_review.md). Multisensory integration in the mammalian brain.
- ~~Riesenhuber & Poggio (1999)~~ — [riesenhuber_poggio1999_hierarchical_models](research_db/papers/riesenhuber_poggio1999_hierarchical_models.md). Hierarchical models of object recognition in cortex.
- ~~Mishkin, Ungerleider & Macko (1983)~~ — [mishkin1983_two_pathways](research_db/papers/mishkin1983_two_pathways.md). Two cortical pathways (dorsal/ventral).
- ~~Hubel & Wiesel (1968)~~ — [hubel_wiesel1968_macaque](research_db/papers/hubel_wiesel1968_macaque.md). Receptive fields in macaque striate cortex.
- ~~Larkum (2013)~~ — [larkum2013_apical_basal](research_db/papers/larkum2013_apical_basal.md). Apical/basal dendritic compartmentalization.
- ~~Gilbert & Li (2013)~~ — [gilbert_li2013_topdown](research_db/papers/gilbert_li2013_topdown.md). Top-down influences on visual processing.
- ~~Tanaka (1996)~~ — [tanaka1996_it_object_vision](research_db/papers/tanaka1996_it_object_vision.md). Inferotemporal cortex and object vision.
- ~~Carrillo & Dewatripont (2008)~~ — [carrillo_dewatripont2008_brain_executive](research_db/papers/carrillo_dewatripont2008_brain_executive.md). The brain as a Central Executive System.
- ~~Glimcher (2011)~~ — [glimcher2011_dopamine_rpe](research_db/papers/glimcher2011_dopamine_rpe.md). Dopamine RPE hypothesis.
- ~~Pearl (2018)~~ — [pearl2018_book_of_why](research_db/papers/pearl2018_book_of_why.md). Ladder of Causation.
- ~~Marcus (2025)~~ — [marcus2025_llm_critique](research_db/papers/marcus2025_llm_critique.md). LLM critique essays.
- ~~LeCun (2022)~~ — [lecun2022_path_to_agi](research_db/papers/lecun2022_path_to_agi.md). JEPA position paper.
- ~~Hawkins~~ — [hawkins2021_thousand_brains](research_db/papers/hawkins2021_thousand_brains.md). *A Thousand Brains.*
- ~~Logie (2003)~~ — [logie2003_mental_workspace](research_db/papers/logie2003_mental_workspace.md). Working memory as mental workspace.
- ~~LeMeur, Le Callet, Barba, Thoreau (2006)~~ — [lemeur2006_coherent_attention](research_db/papers/lemeur2006_coherent_attention.md).
- ~~Bundesen, Habekost & Kyllingsbæk (2005)~~ — [bundesen2005_neural_theory_attention](research_db/papers/bundesen2005_neural_theory_attention.md). Neural theory of visual attention (TVA).
- ~~Moran & Desimone (1985)~~ — [moran_desimone1985_selective_attention](research_db/papers/moran_desimone1985_selective_attention.md). Selective attention gates visual processing in extrastriate cortex.

The completed discharge of this list — every paper now at `depth: full`, every paper anchored to ≥1 concept or thread — was the principal goal of the November 2025 → May 2026 deepening sessions. The wiki has moved past the "is the cite-trail in the DB?" question and into the structural/synthesis phase the wiki-research routine now drives (see SKILL.md §3 — edge construction, concept anchoring, and HRA decision-grounding are the leverage moves now).
