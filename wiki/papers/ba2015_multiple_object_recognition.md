---
id: ba2015_multiple_object_recognition
title: "Multiple Object Recognition with Visual Attention"
authors:
  - "Ba, Jimmy Lei"
  - "Mnih, Volodymyr"
  - "Kavukcuoglu, Koray"
year: 2015
venue: "ICLR"
doi: ""
arxiv: "1412.7755"
url: "https://arxiv.org/abs/1412.7755"
tags:
  - deep-learning
  - visual-attention
  - recurrent-networks
  - reinforcement-learning
concepts:
  - recurrent-attention
  - attentional-spotlight
  - reinforce
  - lstm-cell
  - top-down-feedback
related:
  - mnih2014_recurrent_attention
  - bahdanau2014_neural_translation
  - vaswani2017_attention
  - schulman2016_gae
  - mnih2016_a3c
  - hochreiter_schmidhuber1997_lstm
  - dosovitskiy2020_vit
  - ballas2016_convgru
  - schulman2017_ppo
  - banino2021_pondernet
  - graves2016_act
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Multiple Object Recognition with Visual Attention

## 1. Abstract

The paper presents an attention-based model for recognizing multiple objects in images. The proposed model is a deep recurrent neural network trained with reinforcement learning to attend to the most relevant regions of the input image. The authors show that the model learns to both localize and recognize multiple objects despite being given only class labels during training. They evaluate the model on the challenging task of transcribing house number sequences from Google Street View images and show that it is both more accurate than the state-of-the-art convolutional networks (Goodfellow et al. 2013) and uses fewer parameters and less computation.

## 2. Why this matters for us

Ba, Mnih & Kavukcuoglu 2015 (DRAM — Deep Recurrent Attention Model) is the immediate descendant of Mnih et al. 2014 RAM and the first hard-attention paper to scale a recurrent-attention model from cluttered-MNIST to real-world multi-object recognition (multi-digit SVHN). It introduces three architectural moves that the user's recurrent ViT inherits: (i) a stacked LSTM core in place of a single-layer rectifier RNN — the user's $H^{(t)}$ accumulator generalizes this to a grid of memory tokens; (ii) a *context network* that processes a low-resolution version of the whole image to initialize the recurrent state — the conceptual ancestor of any "global tokenization first, then iterate" pipeline, including the recurrent ViT's initial patch embedding before recurrent rollout; (iii) the multi-object sequential-recognition objective that combines REINFORCE on the location policy with cross-entropy on the class head, derived as a variational lower bound on the marginal label-sequence likelihood. The user's program inherits DRAM's "iterate-and-attend" pattern but replaces hard glimpse selection with soft, differentiable transformer attention over all patches simultaneously — making the REINFORCE-vs-soft-attention choice point a load-bearing architectural decision the user has explicitly made in favor of soft attention.

## 3. Key claims

1. A deep recurrent attention model (DRAM) with a stacked LSTM core, a multi-scale "foveal" glimpse network, and a context network for state initialization can be trained end-to-end on multi-object recognition using only sequence-of-class labels — no bounding-box supervision.
2. The training objective is derivable as a variational free-energy lower bound on the marginal log-likelihood $\log \sum_l p(l \mid I, W) p(y \mid l, I, W)$; the resulting gradient (estimated by Monte Carlo samples of the glimpse locations) is equivalent to a REINFORCE update on the location policy plus a cross-entropy gradient on the classifier.
3. On multi-digit SVHN (cropped 54x54), DRAM with forward-backward Monte Carlo averaging achieves 3.9% whole-sequence error, outperforming the 11-layer Goodfellow et al. 2013 ConvNet baseline at 3.96% while using roughly one-quarter of the parameters and far less computation per inference.
4. On *enlarged* 110x110 multi-digit SVHN — where the bounding box is larger and the digits occupy less of the image — DRAM's advantage grows: the model trained on 54x54 transfers to 110x110 with a "focus" trick (run once, crop, re-feed) and reaches 5.0% error vs. 50% for the same CNN naively resized and 5.6% for the CNN retrained from scratch, demonstrating computation roughly independent of input size.
5. A context network that provides initial recurrent state from a downsampled whole image plus an architectural separation that prevents the classifier from short-cutting via context (context feeds only the top recurrent layer; classifier reads only the bottom layer) is critical for forcing the model to actually use glimpses rather than the coarse context.

## 4. Methods

**Glimpse sensor.** At step $n$ the model attends to location $l_n$ and extracts two concentric crops $(x_n^1, x_n^2)$ — original-resolution patch and a downsampled coarser surround — concatenated to form the "foveal" glimpse $x_n$.

**Glimpse network $G$.** Three convolutional layers (5x5, then 3x3, 3x3 with {64, 64, 128} filters in the SVHN model) without pooling, followed by a fully-connected layer, produce $G_\text{image}(x_n \mid W_\text{image})$. The location tuple $l_n$ is mapped by an FC layer to $G_\text{loc}(l_n \mid W_\text{loc})$ with the same dimension. The two are combined *multiplicatively* (element-wise product, after Larochelle & Hinton 2010):
$$g_n = G_\text{image}(x_n \mid W_\text{image}) \odot G_\text{loc}(l_n \mid W_\text{loc}).$$
This "what × where" multiplicative gating is the architectural ancestor of the modulated-attention designs in PRISM and the recurrent ViT.

**Recurrent core.** *Two stacked LSTM layers* (512 units per layer in the SVHN model) — a critical departure from RAM's single-layer rectifier RNN. The bottom layer $r^{(1)}$ receives the glimpse vector; the top layer $r^{(2)}$ receives $r^{(1)}$:
$$r_n^{(1)} = R_\text{recur}(g_n, r_{n-1}^{(1)} \mid W_{r_1}), \quad r_n^{(2)} = R_\text{recur}(r_n^{(1)}, r_{n-1}^{(2)} \mid W_{r_2}).$$

**Emission network.** A single FC layer maps $r_n^{(2)}$ to the *mean* of the next glimpse location: $\hat l_{n+1} = E(r_n^{(2)} \mid W_e)$, with sampling $\tilde l_{n+1} \sim \mathcal{N}(\hat l_{n+1}, \Sigma)$ at training time and deterministic $\hat l_{n+1}$ at inference.

**Context network.** Three conv layers map a downsampled whole image $I_\text{coarse}$ to a fixed-length vector $c_I$, which initializes only the *top* recurrent layer $r^{(2)}_0$. The bottom layer $r^{(1)}_0$ is initialized to zero. This architectural separation is the load-bearing trick: because the classifier reads from $r^{(1)}_N$ (bottom layer) and the context-initialized top layer only drives the location policy, the model cannot bypass glimpse processing by reading off the coarse image.

**Classification network.** A single FC hidden layer followed by softmax over class $y$:
$$P(y \mid I) = O(r_N^{(1)} \mid W_o).$$

**Variational training objective.** The marginal likelihood is decomposed via Jensen as
$$\log \sum_l p(l \mid I, W) p(y \mid l, I, W) \geq \sum_l p(l \mid I, W) \log p(y \mid l, I, W) + H[l].$$
Differentiating and applying the score-function trick gives
$$\frac{\partial \mathcal{F}}{\partial W} \approx \frac{1}{M} \sum_m \left[ \frac{\partial \log p(y \mid \tilde l_m, I, W)}{\partial W} + \lambda (R - b)\,\frac{\partial \log p(\tilde l_m \mid I, W)}{\partial W} \right]$$
where $R \in \{0, 1\}$ is the classification-correctness indicator, $b_n = E_\text{baseline}(r_n^{(2)} \mid W_\text{baseline})$ is a learned state-dependent baseline (fit by regression to $R$), $\lambda$ trades off the two gradient components, and $M$ is the number of Monte Carlo glimpse-sequence samples per image. The second term *is* REINFORCE (Williams 1992) on the location policy.

**Multi-object extension.** For $S$ targets the model emits $N = 3$ glimpses per target plus 3 final glimpses for an end-of-sequence symbol — at most $N(S+1) = 18$ glimpses for SVHN ($S \leq 5$). The reward becomes the *cumulative* count of correctly predicted targets $R_s = \sum_{j \leq s} R_j$, and the gradient is truncated at the first mislabeled target — a curriculum trick the paper describes as crucial.

**Forward–backward ensembling.** A second DRAM is trained right-to-left with shared glimpse weights but separate recurrent / emission / classifier weights. Final predictions are formed by flipping the first $k$ predictions from the backward model where $k$ is the shorter of the two predicted sequence lengths. This heuristic exploits the leading-digit Benford-law prior to fix the model's tendency to over-predict trailing digits.

## 5. Results

**MNIST digit-pair classification (100x100 cluttered background, 55-way classification of digit pairs, 4 glimpses).** RAM 9.0% error; DRAM without context 7.0%; DRAM with context 5.0%. The context network roughly halves the error vs. RAM.

**MNIST two-digit addition (100x100, 19-way prediction of digit-sum).** ConvNet 64-64-64-512 baseline: 3.2%. DRAM: 2.5%. The qualitative result is that the *learned glimpse policy differs by task* — for addition the model toggles back and forth between the two digits, whereas for pair classification it visits each once.

**Multi-digit SVHN (54x54 cropped, whole-sequence accuracy).**
- 11-layer CNN (Goodfellow et al. 2013): 3.96%
- 10-layer CNN (reimplementation): 4.11%
- Single DRAM (deterministic inference): 5.1%
- Single DRAM with $M$ Monte Carlo samples averaged: 4.4%
- Forward–backward DRAM with MC averaging: **3.9%**

**Enlarged multi-digit SVHN (110x110, less tightly cropped).**
- 10-layer CNN, resize input back to 54x54: 50% (catastrophic failure)
- 10-layer CNN retrained on 110x110: 5.6%
- Single DRAM with "focus" trick (run once, crop the glimpse-trajectory bounding box, re-feed): 5.7%
- Forward-backward DRAM with focus: 5.0%
- Single DRAM fine-tuned on 110x110: 5.1%
- Forward-backward DRAM fine-tuned: **4.46%**

**Computation and parameters (Table 5).** At 54x54: 10-layer CNN 2.1 GFLOP / 51M params; DRAM 0.2 GFLOP / 14M params (deterministic), 0.35 GFLOP / 14M (MC avg), 0.7 GFLOP / 28M (F-B MC avg). At 110x110: 10-layer CNN 8.5 GFLOP / 169M params; DRAM remains 0.2 GFLOP / 14M (deterministic) — the **CNN's cost grows 4x with image area while DRAM's stays constant**, the cleanest empirical demonstration of the model's signature property.

**Training time.** SVHN model: roughly 3 days on a single GPU; fine-tuning to 110x110: a few hours vs. one week to retrain the 10-layer ConvNet.

## 6. Critique / limitations

The model is still using *hard* attention with stochastic sampling. The Monte Carlo gradient estimator inherits REINFORCE's high variance — DRAM mitigates this only with a state-dependent baseline $b_n$ and the curriculum trick that truncates gradient at the first error. The paper does not compare against any soft-attention baseline despite Bahdanau et al. 2014 being contemporaneous; the field's subsequent move to soft attention (Show, Attend & Tell; transformers) is a direct rejection of the hard-attention commitment DRAM inherits from RAM.

The "context-feeds-only-top-layer, classifier-reads-only-bottom-layer" trick is load-bearing but architecturally ad hoc. It exists to prevent a learned short-cut and reflects the difficulty of training such a system end-to-end without supervisory leakage. A soft-attention model with full differentiability does not need this trick.

Sequence ordering must be specified in advance (left-to-right for SVHN). DRAM cannot discover the ordering and the forward-backward ensemble is a hand-engineered patch for the systematic over-prediction the forward model exhibits at sequence ends. This is essentially a workaround for the lack of a principled end-of-sequence treatment under REINFORCE.

Glimpse count per target is a fixed hyperparameter ($N = 3$ for SVHN), so DRAM cannot adaptively allocate computation across digits — easy and hard digits get the same budget. Adaptive-computation-time methods (Graves 2016 ACT, Banino et al. 2021 PonderNet) explicitly target this limitation. The "exploration vs. exploitation" location-variance hyperparameter $\Sigma$ is hand-tuned and the paper notes performance is "very sensitive" to it.

The Monte Carlo inference path (averaging $M$ glimpse-sample predictions) inflates inference cost by a factor of $M$, eroding the computation advantage. The forward-backward variant doubles parameter count to 28M and doubles inference cost. The headline 3.9% error is at 0.7 GFLOP / 28M params, not the 0.2 GFLOP / 14M cited for single deterministic DRAM.

The benchmarks are MNIST and SVHN — both small-scale digit recognition. DRAM was not shown to scale to ImageNet, and the field's subsequent successes on ImageNet went almost entirely to soft-attention / transformer architectures rather than RL-trained hard glimpse models. By the time the recurrent ViT appears in 2025, hard glimpse models are essentially out of the mainstream image-classification literature.

## 7. Connection to our work

DRAM occupies a precise structural position in the lineage to the user's recurrent ViT: it is the **direct successor** of Mnih et al. 2014 RAM (`mnih2014_recurrent_attention`) and the **immediate hard-attention predecessor** of the user's recurrent ViT (arXiv:2502.10955). Three threads of inheritance and three threads of departure matter.

**Inherited: the iterate-and-attend pattern.** DRAM is a sequential glimpse-based attention model that updates an internal recurrent state across $N$ steps and reads off a final prediction. The recurrent ViT iterates a soft attention map over patches across $T$ recurrent steps and reads off a change-detection prediction. The control structure is identical — pick (or weight) regions, accumulate evidence into recurrent state, attend again, eventually decide. The user's program (`threads/the_user_architectural_program.md` §1–§4) explicitly inherits this: the Feedback Transformer is an iterate-and-attend primitive; the iterative variational encoder–decoder runs $n_{FR}$ forward-reasoning and $n_{BR}$ backward-reasoning passes on the same image. The fact that "static-image attention dynamics evolve nontrivially across passes" — the user's Food-101 observation — is precisely the qualitative phenomenon DRAM demonstrates with its task-dependent glimpse trajectories (toggling for addition vs. visiting each digit once for pair classification).

**Inherited: stacked LSTM as the recurrent core.** DRAM's move from RAM's single-layer rectifier RNN to a two-layer LSTM is the first instance of "treat the recurrent state as a structured, multi-layer object" in the lineage. PRISM v1's convGRU memory (`ballas2016_convgru`) is the spatial generalization of this — the recurrent state becomes a multi-channel grid. The recurrent ViT's $H^{(t)}$ token grid (with the Feedback Transformer integrating it back into self-attention) is the architectural completion of the move. The user's multi-compartmental memory commitment (`threads/the_user_architectural_program.md` §3) — multiple recurrent states with different spatial resolution, channel dimension, and update timescale — is the logical endpoint: DRAM has two LSTM layers because that helped; the user's program has many layers at many timescales for the same reason but built systematically.

**Inherited: context-then-iterate.** DRAM's context network initializes the recurrent state from a coarse global view of the image *before* glimpse iteration begins. This is the conceptual ancestor of the recurrent ViT's "patch-embed the whole image, then iterate the attention" structure — both architectures separate "global context priming" from "iterative attention refinement". The user's program preserves this in the iterative-VAE encoder, which sees the same image repeatedly and refines an internal guide $H_t$ across passes; the first pass is essentially the "context" pass.

**Departure: hard vs. soft attention.** DRAM samples a single location per step from a Gaussian policy. The recurrent ViT places a *soft, differentiable* attention distribution over the full patch grid every step. This is the most consequential architectural difference and bears on every other choice. Soft attention is the conceptual ancestor of Bahdanau et al. 2014 (`bahdanau2014_neural_translation`), Show-Attend-Tell, and the transformer (`vaswani2017_attention`); the field's verdict by 2017 is that soft attention dominates for differentiable end-to-end training. The user's program inherits this verdict: every attention mechanism in the Feedback Transformer is soft and differentiable. Hard attention is recovered only as the degenerate $\sigma \to 0$ limit, never used in practice. The trade is explicit: soft attention loses the "computation independent of input size" property DRAM advertises (the recurrent ViT processes all patches every step), but gains differentiability, lower-variance gradients, and the ability to attend to multiple regions simultaneously.

**Departure: REINFORCE vs. PPO with GAE.** DRAM trains the location policy with REINFORCE plus a state-based baseline. The recurrent ViT trains its attention-and-state dynamics with PPO (`schulman2017_ppo`) using GAE (`schulman2016_gae`) for variance reduction. The change is forced by two facts: (i) the recurrent ViT's "action space" — a full soft attention distribution over all patches — is vastly larger than DRAM's 2D location; REINFORCE's variance becomes prohibitive. (ii) the recurrent ViT's reward is sparse (final change-detection correctness only) over long rollouts ($T$ steps), whereas DRAM gives one reward per object every $N = 3$ glimpses. PPO+GAE handles both regimes; REINFORCE handles neither. The lineage REINFORCE → A3C (`mnih2016_a3c`) → PPO (`schulman2017_ppo`) + GAE (`schulman2016_gae`) is the policy-gradient half of what made the move from DRAM to the recurrent ViT possible. DRAM is the canonical reference point for *why* the user did not just keep using REINFORCE.

**Departure: glimpse network → ViT encoder.** DRAM's glimpse network is three conv layers without pooling, ending in an FC layer. The recurrent ViT replaces it wholesale with a patch-embed ViT (`dosovitskiy2020_vit`). This is the same capacity step as RAM → DRAM (rectifier RNN → LSTM) applied to the encoder side — and it is what lets the user's program address natural-scene change detection and Food-101 classification rather than only multi-digit SVHN.

A useful framing for the user's program: DRAM is the **maximal-capacity hard-attention recurrent model** the lineage produced before the field switched to soft attention. Everything that worked in DRAM (stacked LSTM, multiplicative "what × where" gating, context-then-iterate, multi-glimpse evidence accumulation) carries forward; everything that hurt DRAM (REINFORCE variance, hard-pick architectural rigidity, ad hoc context-leakage prevention, fixed glimpse budget per target) is replaced by the soft-attention / PPO / Feedback Transformer machinery in the user's program. The competition-emergent-PC thesis (`threads/the_user_architectural_program.md` §5) goes further still: DRAM's attention policy is trained by a single classification reward; the user's program proposes that attention is the *contested resource* that hubs compete for with their own internal predictions, a fundamental shift in *what attention is for*.

PRISM v1's hard departure — no softmax attention, prediction-error-driven memory updates instead — is in some sense a *different* alternative to DRAM's hard sampling: both reject soft attention, but PRISM v1 replaces it with predictive-coding error signals rather than with sampled location choices. PRISM v2 reintroduces multi-head soft attention, returning closer to the recurrent-ViT trunk of the lineage and farther from DRAM.

## 8. Citations to follow

- `larochelle_hinton2010_attention` — Larochelle & Hinton's "third-order Boltzmann machine" foveal-glimpse paper; the source of the multiplicative "what × where" gating DRAM uses in its glimpse network. Candidate for addition; also cited by RAM.
- `williams1992_reinforce` — the REINFORCE estimator DRAM derives its location-policy gradient from. Foundational for any RL-trained-attention paper; already flagged for addition by `mnih2014_recurrent_attention`.
- `goodfellow2013_svhn_multidigit` — the 11-layer ConvNet baseline DRAM compares against on multi-digit SVHN; the dominant pre-attention approach to multi-digit recognition. Candidate for addition as the empirical foil.
- `xu2015_show_attend_tell` — show-attend-tell soft-attention image captioning; the soft-attention contemporary that became the lineage's mainstream branch after DRAM. Already flagged for addition by `mnih2014_recurrent_attention`.
- `gregor2015_draw` — DRAW soft-attention generative model from the same lab; the soft-attention counterpart to DRAM published the same year. Already flagged for addition by `mnih2014_recurrent_attention`.
- `jaderberg2014_synthetic_text` — synthetic-data ConvNet text recognition; the "non-attention" alternative for sequence-from-image tasks DRAM is positioned against. Candidate for addition.
- `jaderberg2015_spatial_transformers` — Spatial Transformer Networks; the differentiable soft-attention crop module that subsumed DRAM's hard-pick mechanism in the very next year. Candidate for addition as the immediate successor.
- `graves2016_act` — already in seed; the canonical answer to DRAM's "fixed glimpse count per target" limitation. Already in seed.
- `banino2021_pondernet` — already in seed; the modern successor to ACT that fixes adaptive halting more cleanly than DRAM's fixed-budget approach. Already in seed.
