---
id: mnih2014_recurrent_attention
title: "Recurrent Models of Visual Attention"
authors:
  - "Mnih, Volodymyr"
  - "Heess, Nicolas"
  - "Graves, Alex"
  - "Kavukcuoglu, Koray"
year: 2014
venue: "NeurIPS"
doi: ""
arxiv: "1406.6247"
url: "https://arxiv.org/abs/1406.6247"
tags:
  - deep-learning
  - reinforcement-learning
  - visual-attention
  - recurrent-networks
concepts:
  - recurrent-attention
  - reinforce
  - attentional-spotlight
  - top-down-feedback
related:
  - ba2015_multiple_object_recognition
  - vaswani2017_attention
  - dosovitskiy2020_vit
  - schulman2017_ppo
  - hochreiter_schmidhuber1997_lstm
  - bardes2023_vjepa
  - rao_ballard1999_predictive_coding
  - bahdanau2014_neural_translation
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Recurrent Models of Visual Attention

## 1. Abstract

Applying convolutional neural networks to large images is computationally expensive because the amount of computation scales linearly with the number of image pixels. The paper presents a novel recurrent neural network model — the Recurrent Attention Model (RAM) — that is capable of extracting information from an image or video by adaptively selecting a sequence of regions or locations and only processing the selected regions at high resolution. Like convolutional neural networks, the proposed model has a degree of translation invariance built in, but the amount of computation it performs can be controlled independently of the input image size. While the model is non-differentiable, it can be trained using reinforcement learning methods to learn task-specific policies. RAM is evaluated on several image-classification tasks, where it significantly outperforms a convolutional neural network baseline on cluttered images, and on a dynamic visual control problem, where it learns to track a simple object without an explicit training signal for doing so.

## 2. Why this matters for us

RAM is the founding paper of *recurrent visual attention in deep learning* and the direct architectural ancestor of the user's recurrent ViT (arXiv:2502.10955). RAM established the four-part template that the recurrent ViT generalizes: (i) a recurrent state that accumulates evidence across glimpses, (ii) a learned attention policy that selects what to look at next, (iii) end-to-end training of the policy via reinforcement learning because the selection step is non-differentiable, and (iv) classification only after a fixed number of glimpses. The recurrent ViT replaces RAM's hard, one-location-at-a-time glimpse with a soft transformer attention map over patches, swaps REINFORCE for PPO with a sparse change-detection reward, and replaces the MLP glimpse network with a ViT encoder — but the architectural commitment is the same. PRISM v1 inherits the recurrent-state-plus-attention commitment without RL training; PRISM v2's slow/fast memory matches RAM's accumulator-plus-policy decomposition.

## 3. Key claims

1. Visual attention can be cast as a sequential decision process in which a recurrent agent chooses a sequence of glimpse locations and only processes pixels at those locations, decoupling computation from input size.
2. The full system — glimpse encoder, recurrent core, location policy, and classifier — can be trained end-to-end by REINFORCE with a final classification reward, despite the location policy being non-differentiable.
3. On cluttered and translated MNIST the attention model achieves lower error than a CNN with comparable parameter count while processing far fewer pixels, demonstrating that learned glimpse policies dominate fixed convolutional sampling under clutter.
4. The same architecture, with the classifier replaced by an action head, learns to track a moving object in a simple game environment using only the game's reward signal, without any explicit tracking supervision.
5. The number of glimpses, glimpse resolution, and glimpse field-of-view structure are hyperparameters that trade accuracy for computation, giving an explicit computation–accuracy dial absent from a standard CNN.

## 4. Methods

**Glimpse sensor.** At each step $t$ the agent emits a location $l_t \in [-1,1]^2$ and the sensor extracts a "retina-like" foveated patch $\rho(x, l_t)$ from the full image $x$: $k$ concentric crops centered at $l_t$, each successively larger and downsampled to the same fixed resolution, then stacked. This gives high acuity at the fixation point and progressively coarser context.

**Glimpse network $f_g$.** A small two-stream MLP. One stream encodes the foveated patch $\rho(x, l_t)$ as $h_g = \text{Rect}(\text{Linear}(\rho))$; another encodes the location $l_t$ as $h_l = \text{Rect}(\text{Linear}(l_t))$. The two streams are combined as $g_t = \text{Rect}(\text{Linear}(h_g) + \text{Linear}(h_l))$, producing the glimpse representation used at step $t$.

**Core recurrent network $f_h$.** A single-layer RNN with rectified-linear units (no LSTM in the original) that maintains an internal state $h_t$. The state is updated as $h_t = f_h(h_{t-1}, g_t)$. This $h_t$ is the entire memory of past glimpses.

**Location network $f_l$.** A linear readout from $h_t$ to the *mean* of a Gaussian over the next location: $l_{t+1} \sim \mathcal{N}(f_l(h_t), \sigma^2 I)$ with fixed variance $\sigma^2$. The stochastic sample is the action of the agent — this is the source of non-differentiability.

**Action network $f_a$.** After $T$ glimpses the agent emits a final action $a_T$: a softmax classifier for classification tasks, or a discrete action distribution for the control task. In control settings the action network can also fire at every step.

**Training.** The objective is the expected reward $J(\theta) = \mathbb{E}_{p(s_{1:T};\theta)}[R]$ where $R$ is a final-step classification correctness ($R=1$ if right, $0$ if wrong) for the classification tasks, or environmental reward for the control task. Because $l_{t+1}$ is sampled, the policy gradient is estimated by REINFORCE (Williams 1992):

$$
\nabla_\theta J = \mathbb{E}\!\left[ \sum_{t=1}^{T} \nabla_\theta \log \pi_\theta(l_t \mid h_{t-1})\, (R - b_t) \right]
$$

with a learned scalar baseline $b_t$ to reduce variance, fit by regression on $R$. The classifier loss is added as a supervised cross-entropy term on the final glimpse — i.e., the classifier branch is trained by ordinary backprop and the location-policy branch by REINFORCE, end-to-end through the shared core.

**Evaluation.** Number of glimpses $T$ is a fixed hyperparameter at training and test time (typically 6–8). At test time the location distribution is replaced by its mean for deterministic readout.

## 5. Results

**Translated MNIST (28x28 digit placed in a 60x60 black canvas at a random location).** RAM with 6 glimpses achieves 1.86% error; a fully-connected baseline with comparable parameter count achieves 2.63%; a CNN baseline achieves 1.62% but processes the full 60x60 input.

**Cluttered translated MNIST (28x28 digit plus 4 or 8 distractor fragments in a 60x60 canvas).** With 4 distractors RAM (6 glimpses) achieves 5.23% error vs. 7.83% for the CNN baseline. With 8 distractors RAM reaches 8.11% error vs. 11.25% for the CNN — i.e., a roughly 30% relative reduction in error under heavy clutter. The advantage *grows* with clutter, the central empirical claim.

**100x100 translated MNIST.** RAM (8 glimpses) achieves 1.84% error using a fraction of the pixels a CNN over the full image would process, demonstrating that the per-step computation can be held constant while the input size grows.

**Dynamic object tracking (custom game).** The agent is shown a moving target on a noisy background and rewarded for keeping the target near the center of its glimpse. Without any explicit tracking loss, the policy learns to follow the target after training; the paper reports qualitative tracking trajectories rather than a tracking-error number.

**Computation–accuracy trade.** Error decreases monotonically with the number of glimpses on each task; the curve flattens around $T=6$ for translated MNIST and $T=8$ for cluttered MNIST.

## 6. Critique / limitations

The core RNN is a single-layer rectifier RNN with no LSTM, no skip connections, and no spatial structure in the state. Subsequent work (Ba, Mnih & Kavukcuoglu 2015 on multiple-object recognition; Gregor et al. 2015 DRAW) introduced LSTM cores and showed substantial gains. The user's recurrent ViT goes further still by replacing the scalar state with a structured grid of memory tokens.

REINFORCE with a scalar baseline is the highest-variance policy-gradient estimator available; the paper uses it because the action space is low-dimensional and the rollout horizon is short ($T \leq 8$). On harder tasks (more glimpses, larger images, multi-object) the variance becomes prohibitive — which is exactly why the user's recurrent ViT uses PPO with a learned value baseline and GAE rather than REINFORCE.

The glimpse policy is *hard* (a single location per step). This forces the network to commit to one region before it has integrated context, and prevents the agent from attending to multiple things in parallel — a limitation that motivated soft-attention models (Bahdanau 2014; Xu et al. 2015) and ultimately the transformer's parallel soft attention over all positions.

The retina sensor is hand-designed (concentric crops, fixed downsampling). The paper does not learn the sensor's spatial structure, and the foveated-pyramid choice imports a strong inductive bias from primate retinas that may or may not be optimal for arbitrary datasets.

The tracking experiment is qualitative; no benchmark numbers are reported. The classification experiments are MNIST-scale; RAM was never shown to scale to ImageNet, and the literature subsequently moved to soft attention (transformers) rather than scaling RAM.

The classification reward is delayed to the final step — the policy receives no per-glimpse credit assignment. This is exactly the credit-assignment problem the user's recurrent ViT confronts with its sparse change-detection reward, and is the reason PPO with GAE was chosen over plain REINFORCE.

## 7. Connection to our work

RAM is the *direct architectural ancestor* of the user's recurrent ViT (arXiv:2502.10955). The lineage is unusually explicit; the recurrent ViT can be read line-by-line as a transformer-era modernization of RAM. The mapping is:

- **Glimpse policy ↔ ViT attention map.** RAM's $l_{t+1} \sim \mathcal{N}(f_l(h_t), \sigma^2 I)$ selects *one* location per step. The recurrent ViT places a *soft* attention distribution over the full patch grid at every step. RAM's hard-pick policy is the degenerate $\sigma \to 0$, one-token-mass limit of soft attention; the user's model relaxes this to a learned full distribution over all $N$ patches, processed in parallel. This is the same architectural commitment — let the network choose where to spend representational capacity — implemented with a vastly more expressive primitive.

- **REINFORCE ↔ PPO.** RAM trains the location policy by REINFORCE because $l_t$ is sampled and non-differentiable. The user's recurrent ViT trains the attention-and-state dynamics by PPO with a sparse change-detection reward — the same RL-trained-attention commitment, with a lower-variance, clipped policy gradient. The choice of PPO over REINFORCE is not merely an engineering upgrade; it is what makes the longer rollouts and larger action spaces of the recurrent ViT tractable. See `schulman2017_ppo`.

- **Recurrent core ↔ recurrent state $H^{(t)}$.** RAM's $h_t = f_h(h_{t-1}, g_t)$ is a single vector. The recurrent ViT's $H^{(t)}$ is a $N \times d$ matrix of memory tokens, one per patch position, integrated into the next step's attention via the feedback transformer (`threads/the_user_architectural_program.md` §1). The architectural function is identical — accumulate task context across glimpses — but RAM's state is a bottleneck where the recurrent ViT's is spatially structured. PRISM v1's $M_t$ (`Prism/memory.py`) is intermediate: spatially structured like the recurrent ViT, but updated by a saliency-gated convGRU rather than a transformer.

- **Glimpse network ↔ ViT encoder.** RAM's two-stream MLP glimpse net is the bottleneck that prevents scaling beyond MNIST. The recurrent ViT replaces it wholesale with a transformer encoder over patches. This is the single largest capacity increase from RAM to the recurrent ViT and is the reason the recurrent ViT can address natural-image change detection where RAM could only address cluttered digits.

- **What the user's program adds beyond RAM.** Three things. (1) Multiple parallel feedback sources via the Feedback Transformer, not just $h_{t-1}$ as a single recurrent state. (2) Predictive-coding interpretation (Rao & Ballard 1999; `rao_ballard1999_predictive_coding.md`) as the theoretical motivation for *why* recurrence and feedback are required, rather than purely an engineering justification. (3) Soft, parallel attention over all patches every step, which removes the credit-assignment burden RAM places on REINFORCE while preserving the attention-as-policy structure.

The user's empirical lineage to RAM is also concrete: the change-detection task the recurrent ViT addresses is the natural successor to RAM's dynamic-tracking task — both require maintaining a recurrent representation of what the world looked like a moment ago and using the current attention map to detect deviations. The recurrent ViT's sparse-reward PPO training is the modern way to do what RAM did with delayed-reward REINFORCE.

A bigger point: RAM was published the same year as Bahdanau soft attention (2014) and three years before the transformer (Vaswani et al. 2017). The field split at this fork — soft attention won for sequence modeling, hard attention faded. The user's program is, in part, a *re-merger* of the two branches: the recurrent ViT uses soft attention (the winning side) but inherits RAM's commitment to RL-trained, task-driven, recurrent attention dynamics (the losing side). The lineage RAM → ViT (Dosovitskiy 2020) → recurrent ViT (user 2025) is the explicit thread.

## 8. Citations to follow

- `ba2015_multiple_object_recognition` — already in seed; Ba, Mnih & Kavukcuoglu's LSTM-core extension of RAM to multiple-object recognition; the immediate descendant.
- `williams1992_reinforce` — the REINFORCE policy-gradient estimator RAM uses; foundational for any RL-trained-attention paper, candidate for full entry.
- `gregor2015_draw` — DRAW (Gregor et al.); the soft-attention generative-modeling counterpart from the same lab; not currently in seed, candidate for addition.
- `bahdanau2014_neural_translation` — already in seed; soft attention for sequence-to-sequence; the alternative branch of the 2014 attention fork.
- `xu2015_show_attend_tell` — show-attend-tell soft-attention image captioning; the soft-attention competitor to RAM on vision tasks; candidate for addition.
- `larochelle_hinton2010_attention` — Learning to combine foveal glimpses with a third-order Boltzmann machine; the direct predecessor RAM cites; candidate for addition.
- `denil2012_attentional_object_tracking` — Denil et al.'s attentional-object-tracking model; cited by RAM as a precursor; candidate for addition.
