---
id: locatello2020_slot_attention
title: "Object-Centric Learning with Slot Attention"
authors:
  - "Locatello, Francesco"
  - "Weissenborn, Dirk"
  - "Unterthiner, Thomas"
  - "Mahendran, Aravindh"
  - "Heigold, Georg"
  - "Uszkoreit, Jakob"
  - "Dosovitskiy, Alexey"
  - "Kipf, Thomas"
year: 2020
venue: "NeurIPS"
doi: ""
arxiv: "2006.15055"
url: "https://arxiv.org/abs/2006.15055"
tags:
  - deep-learning
  - vision-transformers
  - self-attention
concepts:
  - slot-attention
  - feedback-transformer
  - gridcell-rnn
related:
  - vaswani2017_attention
  - dosovitskiy2020_vit
  - bardes2023_vjepa
  - mehrani_tsotsos2023_attention_grouping
  - hassanin2024_attention_dl_survey
  - cho2014_gru
relevance_to:
  - prism_v1
  - recurrent_vit
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Object-Centric Learning with Slot Attention

## 1. Abstract

"Learning object-centric representations of complex scenes is a promising step towards enabling efficient abstract reasoning from low-level perceptual features. Yet, most deep learning approaches learn distributed representations that do not capture the compositional properties of natural scenes. In this paper, we present the Slot Attention module, an architectural component that interfaces with perceptual representations such as the output of a convolutional neural network and produces a set of task-dependent abstract representations which we call slots. These slots are exchangeable and can bind to any object in the input by specializing through a competitive procedure over multiple rounds of attention. We empirically demonstrate that Slot Attention can extract object-centric representations that enable generalization to unseen compositions when trained on unsupervised object discovery and supervised property prediction tasks."

## 2. Why this matters for us

Slot Attention is the published architecture closest in spirit to the Feedback Transformer (`concepts/feedback_transformer.md`): a small bank of learned recurrent state vectors ("slots") iteratively attends to a feature map and is updated via a GRU, with the attention softmax normalized *over slots* rather than over input positions, so that slots compete for the explanatory mass of each feature location.

The user's program treats this as the canonical "many-source feedback into a single attention computation" prior art — slots play the role the program assigns to parallel-hub memory states ($C^{(\text{RL})}, C^{(\text{VAE})}, C^{(\text{MSI})}$). The competition-by-softmax-over-sources mechanism is the operational core of the user's competition-emergent predictive coding (`concepts/competition_emergent_predictive_coding.md`) reduced to a single layer.

PRISM v2's per-head feature partition (`PRISM_V2_PROPOSAL.md` §3.6) is a deterministic variant of the same idea: $K$ specialists compete for explanatory mass of the image, here via softmax, in PRISM via prediction-error magnitude. Slot Attention therefore sits at exactly the intersection of the program's three main commitments (multi-source feedback, multi-hub competition, multi-head specialization), and is the published baseline against which any program-derived module that combines those commitments should be measured.

## 3. Key claims

1. Object-centric representations can be learned with a generic, differentiable attention module that has no built-in notion of object identity, by *normalizing attention over a small set of exchangeable slots* and updating them recurrently.
2. Slots are permutation-equivariant by construction: they are initialized i.i.d. from a learned Gaussian and the architecture is symmetric under slot permutation, so any binding between slots and objects emerges from the competitive dynamics, not from positional bias.
3. The same module supports both unsupervised object discovery (trained with a per-slot decoder and a mixture-of-slots reconstruction loss) and supervised set prediction (trained with Hungarian matching against a target set), without architectural change.
4. The competitive softmax-over-slots and the iterative refinement together are required: removing competition (replacing slots with an MLP read-out) or reducing iterations sharply degrades object discovery quality.
5. The learned slot-binding generalizes to scenes containing more objects than were seen at training, simply by increasing the number of slots at test time — a compositional generalization claim absent in fixed-set baselines.
6. The same module trained with different objectives (reconstruction vs. property prediction) yields slots with different semantics, indicating that the inductive bias is the architecture rather than the loss, and that the loss merely selects which axes of object structure the slots align to.

## 4. Methods

Slots are a set of $K$ vectors $S \in \mathbb{R}^{K \times D_\text{slot}}$ initialized i.i.d. from a Gaussian with learned mean $\mu$ and (diagonal) variance $\sigma^2$, both of which are shared across slots. Inputs are a feature map $X \in \mathbb{R}^{N \times D_\text{in}}$ from a CNN (with positional embedding added).

Each of $T$ iterations performs the following update. Three linear projections produce $k(X), v(X) \in \mathbb{R}^{N \times D}$ from inputs and $q(S) \in \mathbb{R}^{K \times D}$ from current slots. Scaled dot-product logits $M = q(S) k(X)^\top / \sqrt{D} \in \mathbb{R}^{K \times N}$ are computed. The critical departure from standard attention is the normalization axis: softmax is applied *over the slots dimension*, $A_{k,n} = \text{softmax}_k(M)_{k,n}$, so for each input location the slots compete to "explain" it. Contrast this with Vaswani-style attention, which softmaxes over keys so each query distributes its mass across input positions; here each input position distributes its mass across queries. The contribution that each slot pulls from inputs is a *weighted mean*: $U_k = \sum_n \bar A_{k,n} v(X)_n$ where $\bar A_{k,n} = A_{k,n} / \sum_{n'} A_{k,n'}$ (renormalizing along the input axis to keep slot updates in a stable range regardless of how many inputs a slot has captured). Finally, slots are updated by a GRU cell with $U_k$ as input and the previous slot as hidden state, followed by an optional residual MLP: $S \leftarrow \text{GRU}(U, S)$; $S \leftarrow S + \text{MLP}(\text{LN}(S))$. LayerNorm is applied to both inputs and slots inside the loop. Typically $T = 3$ iterations are used at training time; the authors note that test-time $T$ may be increased without retraining.

The CNN encoder is a small (4-layer) convolutional network with positional embedding concatenated to the channel dimension before flattening to a sequence of feature vectors. The "spatial-broadcast decoder" used for unsupervised discovery takes each slot, tiles it spatially to a fixed grid, concatenates 2-D positional coordinates, and runs a 4-layer transposed-convolution stack to produce a 4-channel output (RGB + alpha). The per-slot alphas are softmaxed across slots at every pixel; the final reconstruction is $\hat X = \sum_k \text{softmax}_k(\alpha)_k \cdot \hat X_k$.

For **unsupervised object discovery**, each final slot is broadcast-decoded by a shared spatial-broadcast CNN into a per-slot RGB image and an alpha mask; per-pixel reconstructions are alpha-composited and trained against the input with pixel-wise MSE. The alpha masks recover the segmentation by argmax. There is no segmentation supervision: the segmentation emerges as a side effect of the alpha-compositing reconstruction loss combined with the slot competition.

For **supervised set prediction**, each slot is mapped by a small MLP to an object property vector (position, size, color, shape, material) and the predicted set is matched to the ground-truth set by the Hungarian algorithm, optimizing a Huber loss on matched pairs. The shared MLP plus permutation-invariant matching is what makes the architecture genuinely a set predictor rather than a sequence predictor.

The whole module is permutation-equivariant in the slot dimension: any permutation of the initial slot set produces the same permuted final slot set, regardless of the inputs. This is the architectural guarantee that lets the Hungarian matching make sense — without it, the matching loss would have a preferred slot order and the architecture would not behave as a set.

Datasets: CLEVR6 (up to six 3-D objects), Multi-dSprites, Tetrominoes for object discovery; CLEVR (10 objects) with properties for set prediction. $K$ is chosen one larger than the max object count. Slot dimension $D_\text{slot} = 64$ in most experiments; the GRU has the same hidden size.

## 5. Results

**Unsupervised object discovery.** On CLEVR6, Slot Attention reports Adjusted Rand Index (ARI, foreground) ≈ 0.99, on par with or slightly above IODINE (≈ 0.99) and substantially above MONet (≈ 0.96) and Slot MLP (≈ 0.60). On Multi-dSprites, ARI ≈ 0.91 (IODINE ≈ 0.77, MONet ≈ 0.90). On Tetrominoes, ARI ≈ 0.99 (IODINE ≈ 0.99). The training cost is roughly an order of magnitude lower than IODINE for comparable accuracy because Slot Attention does only $T = 3$ refinement steps versus IODINE's amortized-inference loop.

**Supervised set prediction.** On CLEVR with properties, Slot Attention reaches AP@∞ ≈ 94.3 (full property matching) and AP@1 ≈ 71.6 (1-pixel position tolerance), outperforming a Deep Set Prediction Network baseline by several AP points across thresholds. Property accuracy is highest for categorical attributes (shape, color, material) and degrades for fine-grained position.

**Iteration ablation.** $T = 1$ collapses to a single non-competitive read-out and segmentation quality is near-chance; $T = 2$ recovers most of the gain; gains beyond $T = 3$ are small. Test-time iterations can be increased without retraining.

**Generalization to more objects.** A model trained with $K = 7$ slots on CLEVR6 can be evaluated with $K = 11$ slots on full CLEVR and recovers most of the additional objects, demonstrating compositional extrapolation. The empty/used slot dichotomy is itself emergent: there is no architectural label distinguishing "slot bound to nothing" from "slot bound to an object," only the alpha mask of the decoder.

**Qualitative attention dynamics.** Visualization of the per-iteration attention maps shows that at $t = 0$ all slots produce nearly uniform attention; by $t = 1$ slots have partitioned the image into rough regions; by $t = 3$ slots have committed to specific objects with clean boundaries. This is the same kind of "attention focusing and reactivating over recurrent steps" that the user reports for the Recurrent ViT on Food-101 (`threads/the_user_architectural_program.md` §6), but here driven by within-step iteration rather than across-step recurrence.

## 6. Critique / limitations

The framework's empirical scope is restricted to synthetic, well-lit, low-clutter scenes with prototypical "object" geometry (CLEVR-style). On natural images, the slot-decoder reconstruction loss is known to underperform without additional structure (this has been the central limitation addressed by follow-ups: SAVi, SLATE, DINOSAUR). The reconstruction objective is also a strong scene-rendering inductive bias — it presumes that a sum of slot-rendered components is the right generative story, which is plausible for CLEVR and false for occluded textured natural scenes.

The competitive softmax-over-slots is the load-bearing inductive bias, but the paper does not analytically characterize when this competition produces semantically aligned slots versus arbitrary partitions of the feature space. Empirically, on textured datasets slots often bind to color or spatial blobs rather than objects (later established by follow-up work).

The iterative refinement is presented as a fixed-T unrolled procedure but is conceptually a coordinate-ascent-style EM. The paper does not relate this to the broader iterative-inference literature (e.g., IODINE's amortized variational inference, which it benchmarks against but does not subsume). Permutation-equivariance is by construction; the paper does not study how breaking it (e.g., positional slot encodings) would interact with set prediction.

Slot count $K$ is a hyperparameter, not learned. Choosing $K$ correctly is benign on synthetic data with known object counts but a real problem on natural scenes. Excess slots tend to bind to "background" or to empty mass, which the architecture has no principled mechanism to mark as such — they merely contribute small alpha masks that are absorbed into the compositing.

A subtler critique relevant to the user's program: the GRU update is a black-box recurrence with no clean interpretation as a Bayesian update, a free-energy step, or a coordinate-ascent move on any explicit objective. The "competition" Slot Attention exhibits is therefore not derived from a normative principle — it is the empirical consequence of softmaxing along the slot axis. This matters because subsequent work (e.g., Engelcke et al. 2021 "GENESIS-V2") has shown that competition-by-softmax can underfit in scenes with many small objects, while other competition formulations (stick-breaking, attention bottlenecks) handle the same regime better. The user's program wants the *normative* version of this story, where competition emerges from a resource constraint (`concepts/coalition_resource_competition.md`), not from an architectural softmax.

## 7. Connection to our work

The user's Feedback Transformer (`concepts/feedback_transformer.md`) is most usefully read as a *generalization* of Slot Attention along three axes.

(i) **Direction of softmax.** Slot Attention softmaxes over slots so slots compete for input mass; the Feedback Transformer softmaxes over input positions but lets multiple feedback sources combine multiplicatively into Q and K. The two normalization directions are complementary, not competing — a multi-hub Feedback Transformer with softmax also taken over hubs would recover Slot Attention's competition as a special case. A worthwhile design experiment for the program is a "Feedback Slot Attention" hybrid that softmaxes simultaneously over input positions (Vaswani direction) and over feedback sources (Locatello direction), giving a joint competition for representational mass.

(ii) **Update rule.** Slot Attention uses a GRU update on slot states; the user's GridCell RNN (`concepts/gridcell_rnn.md`) uses an LSTM-style gated update at each grid cell, with the Feedback Transformer playing the role of inter-cell communication. The two designs converge on "recurrent state + iterative attention" as the right shape, but Slot Attention's GRU update is applied per-slot and is permutation-equivariant, whereas the GridCell RNN's LSTM is applied per-spatial-cell and is *not* permutation-equivariant (the spatial position carries meaning). The two are the right specializations of the same underlying recipe for the different things they bind to (objects vs. retinotopic locations).

(iii) **Number and heterogeneity of sources.** Slot Attention treats slots as exchangeable and homogeneous; the user's program treats feedback sources as heterogeneous (RL hub, VAE hub, MSI hub, hierarchical layers) with hub-specific projection matrices. Locatello et al.'s exchangeability is the right move when you don't know what an object is; the user's heterogeneity is the right move when the sources have known, distinct semantics. The continuum between these two regimes — "homogeneous many" vs. "heterogeneous few" — is open territory for the program.

Direct architectural debts. The element-wise broadcasting that the Feedback Transformer uses to combine Q from multiple sources (`feedback_transformer.md`, "Why the element-wise broadcasting matters") plays the same role that Slot Attention's per-slot query projection does: it lets each source/slot bias the attention map without overwriting the bottom-up sensory contribution. The competition-emergent predictive coding thesis (`concepts/competition_emergent_predictive_coding.md`) inherits Slot Attention's central operational insight: when softmax-normalized scores share a budget, the units producing those scores are under competitive pressure to predict each other's output. Slot Attention demonstrates this empirically at the level of objects within a scene; the user's program scales it to coalitions across a brain.

The Recurrent ViT (2502.10955) does *not* use Slot Attention's normalization direction; it remains a standard softmax-over-positions attention, augmented with a single recurrent feedback source. The connection to Slot Attention is conceptual rather than algorithmic: both are "iterative refinement of a small recurrent state via cross-attention into a feature map." Reframing the Recurrent ViT in slot-attention terms — slots = patch-grid memory states $H^{(t-1)}$, iterations across time rather than within a step — is a useful re-description even though no equation changes. It also surfaces a candidate generalization: the paper's three feedback variants (token, additive, multiplicative; §6.7) could each be replaced or augmented with a Slot-Attention-style memory-as-query block that softmaxes over memory cells rather than over patches.

PRISM v2's per-head feature partition (`PRISM_V2_PROPOSAL.md` §3.6) is the generative-error analog of Slot Attention's per-slot competition: $K$ heads each predict a disjoint subset of feature channels, and the per-head error map plays the role of the per-slot attention map. The Hungarian-matching set-prediction setup in Slot Attention is a direct analog of how PRISM v2 evaluates per-head specialization without supervised head labels. PRISM v1 (which has no multi-head structure) is the degenerate $K = 1$ case where competition vanishes.

A final point of contact is with V-JEPA (`bardes2023_vjepa`): both Slot Attention and V-JEPA's predictor produce a set of latent codes whose meaning is determined entirely by training dynamics rather than by an explicit assignment rule. The user's iterative variational encoder–decoder (`concepts/iterative_variational_encoder_decoder.md`) sits in this same neighborhood, with the additional commitment that the latent set is the *guide* of a recurrent generative model rather than a target for masked prediction.

## 8. Citations to follow

- `kipf2021_savi` — Slot Attention for Video, the direct sequel that adds temporal slot binding; relevant to the Recurrent ViT's temporal-feedback story.
- `singh2022_slate` — SLATE, transformer-decoder slot attention scaling to richer visual domains.
- `seitzer2023_dinosaur` — DINOSAUR, slot attention on DINO features for natural images; the empirical answer to §6's "what about real scenes" critique.
- `greff2019_iodine` — IODINE, the iterative-amortized-inference baseline Slot Attention benchmarks against and dramatically outpaces in efficiency.
- `burgess2019_monet` — MONet, the other principal competitor; mask-prediction-based unsupervised object discovery.
- `cho2014_gru` — the GRU cell used inside the Slot Attention update; load-bearing for the architecture's stability under iteration.
- `engelcke2021_genesis_v2` — alternative competition mechanism (stick-breaking) that handles many-object scenes better than softmax-over-slots; directly informs the program's choice of normative competition formulation.
- `vaswani2017_attention` — the dot-product attention primitive Slot Attention rebrands; already in seed and the natural cross-reference for the "different softmax axis" reframing.
