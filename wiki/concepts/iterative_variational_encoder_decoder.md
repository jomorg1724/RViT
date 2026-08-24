---
id: iterative_variational_encoder_decoder
type: concept
title: "The iterative variational encoder–decoder"
papers:
  - friston2010_fep_unified_theory
  - rao_ballard1999_predictive_coding
  - bardes2023_vjepa
  - lecun2022_path_to_agi
  - higgins2017_factorized_representations
  - vaswani2017_attention
  - dosovitskiy2020_vit
  - buckley2017_fep_mathematical
source_documents:
  - "Private & Shared-3/VAE"
  - "Private & Shared/Encoder-Decoder Architecture"
  - "Private & Shared-4/Evolution of Architecture (§ ELBO derivation)"
  - "RViT_plus/latent.py + decoder.py (run-8 reference instantiation, 2026-05-20)"
last_updated: "2026-05-20"
---

# The iterative variational encoder–decoder

## Definition

A pair of structurally-identical multi-compartmental memory stacks (`concepts/multi_compartmental_memory.md`) — an encoder and a decoder — that interact via a two-phase iterative recurrent protocol with a variational free-energy objective.

**Phase 1 — Forward reasoning ($n_{FR}$ steps).** The encoder is shown the same input $X$ (image or video clip) repeatedly. At each pass $t$, the encoder updates its internal "guide" state: $H_{t+1} \leftarrow \psi_\theta(X, H_t)$. The hypothesis (supported by the Food-101 classifier experiment in the user's "Classifier" note) is that the encoder's self-attention dynamics evolve nontrivially even on a static image, exhibiting attractor-like trajectories that depend on the underlying image semantics. After $n_{FR}$ passes, the encoder produces a final guide $H_{n_{FR}}$.

**Phase 2 — Backward reasoning ($n_{BR}$ steps).** The decoder is initialized with $\tilde H_0 = H_{n_{FR}}$ and a learned latent $Z_0$. At each pass $\tau$, the decoder produces an updated latent, an updated state, and a reconstruction proposal:

$$
(Z_{\tau+1}, \tilde H_{\tau+1}, \tilde X_{\tau+1}) \leftarrow \phi_\theta(Z_\tau, \tilde H_\tau)
$$

The reconstruction loss is weighted across all $n_{BR}$ proposals with an exponential schedule favoring later proposals:

$$
\mathcal{L}_{\text{recon}} = \sum_{i=1}^{n_{BR}} \gamma_i \, \text{MSE}\big[\tilde X_i, X\big], \qquad \gamma_i = e^{i - n_{BR}}.
$$

## Variational objective

Treat the initial guide as a latent random variable $\tilde H_0 \sim q_\theta(\tilde H_0; H_{n_{FR}}) = \mathcal{N}(\mu_\theta(H_{n_{FR}}), \Sigma_\theta(H_{n_{FR}}))$. Place a unit Gaussian prior $p(\tilde H_0) = \mathcal{N}(0, I)$. Then the ELBO over the iterative rollout decomposes as

$$
\mathcal{L}_{\text{ELBO}} = \sum_{i=1}^{n_{BR}} \mathbb{E}_{q_\theta}\!\Big[\log p_\theta^{(i)}\big(X \mid \tilde H_0\big)\Big] \;-\; D_{\text{KL}}\!\big[q_\theta(\tilde H_0 \mid H_{n_{FR}}) \,\big\|\, p(\tilde H_0)\big]
$$

Under a Gaussian likelihood, each expectation term reduces to negative MSE between the reconstruction proposal and the target image (up to a scale). The KL term has the standard analytic Gaussian-vs-unit-Gaussian closed form.

## Multi-patch distributional latents

The guide is a matrix $\tilde H_0 \in \mathbb{R}^{n_{\text{patch}} \times d_{\text{guide}}}$, not a vector. The user models it as a matrix-normal distribution $\tilde H_0 \sim \mathcal{MN}(M, U, V)$ with row-covariance $U$ over patches and column-covariance $V$ over guide dimensions. Row-whitening via eigendecomposition of $U$ gives an equivalent representation in which the patch rows are independent. In practice the user enforces approximate row-independence with an off-diagonal penalty:

$$
\mathcal{L}_{\text{row-indep}} = \big\| \hat U - \text{diag}(\hat U) \big\|_F^2
$$

on an empirical row-covariance $\hat U$. This is the `multi-patch-distributional-latents` mechanism in the taxonomy.

## Why the iterative variational structure matters

The KL regularizer induces three properties the user calls out as load-bearing for the program (Evolution of Architecture §"Why the KL Matters"):

1. **Continuity / smoothness** of the guide-to-output mapping, so that small changes in the guide produce small changes in reconstruction.
2. **Disentanglement** of the latent space along axis-aligned factors of variation — the Higgins et al. β-VAE phenomenon.
3. **Hopfield-like attractor dynamics** in the sampled guide space, with the prior ensuring the attractor landscape stays well-behaved rather than memorizing individual training examples.

The KL term is interpreted explicitly as the variational free-energy regularizer of Friston (`papers/friston2010_fep_unified_theory.md`): the iterative-VAE objective *is* variational free-energy minimization, with the encoder–decoder pair instantiating the recognition and generative models respectively.

The mathematical formalization is given by Buckley et al. 2017 (`papers/buckley2017_fep_mathematical.md`), which works out the FEP in fully explicit form: the variational density $q$, the generative model $p$, the ELBO decomposition into accuracy and complexity terms, and the gradient flows on $q$'s parameters that constitute "perception" in Friston's framework. Buckley's derivation is what makes the FEP an operational, implementable objective rather than a conceptual claim. The iterative-VAE's two-phase rollout ($n_{FR}$ encoder passes + $n_{BR}$ decoder passes) is exactly the kind of *iterative inference* loop Buckley specifies as the natural implementation of a non-linear generative model: when $p$ is non-Gaussian or hierarchical, $q$ cannot be computed in closed form and must be refined iteratively — Buckley's §"inner-inference-loop". The user's encoder's $n_{FR}$ forward passes are this inner inference loop; the decoder's $n_{BR}$ backward passes implement the corresponding amortized generative model. Buckley 2017 thus supplies the explicit mathematical bridge from Friston's high-level FEP statement to the concrete iterative encoder–decoder architecture.

## How this generalizes Rao-Ballard

Rao & Ballard 1999 (`papers/rao_ballard1999_predictive_coding.md`) describes a single forward pass through a hierarchical generative model with prediction-error feedback. The iterative variational encoder–decoder is the multi-pass, fully variational extension: $n_{FR}$ encoder passes amortize the recognition computation; $n_{BR}$ decoder passes implement an iterative-refinement generative model. The ELBO closes the loop with a probabilistic objective.

## Why not just JEPA?

V-JEPA (`papers/bardes2023_vjepa.md`) and LeCun's broader JEPA program (`papers/lecun2022_path_to_agi.md`) commit to latent-space prediction without explicit pixel reconstruction. The iterative VAE differs in two ways: (a) it includes pixel reconstruction via $\tilde X_i$ proposals at each $n_{BR}$ step, which provides a strong supervisory signal that JEPA does not have; (b) it uses an iterative protocol rather than a single forward-pass prediction, which licenses the multi-step refinement dynamics observed in the Food-101 classifier experiment.

The two approaches are not mutually exclusive: a JEPA loss at the latent level could be added on top of the iterative-VAE reconstruction loss, giving the system both fine-grained pixel feedback and high-level semantic structure.

## Connection to other concepts

- `multi_compartmental_memory` — the encoder and decoder are each instances of a multi-compartmental memory stack.
- `gridcell_rnn` — each level of the encoder/decoder stack is a GridCell RNN.
- `multi_hub_multi_objective_system` — the VAE hub in the multi-hub system is an instance of the iterative variational encoder–decoder.
- `feedback_transformer` — the encoder's and decoder's inter-level communication uses the Feedback Transformer.

## Open questions

1. **Optimal $n_{FR}$ and $n_{BR}$.** The user's notes have explored 2–8 for each; the trade-off between compute cost and reconstruction quality is not yet quantified.
2. **Is the matrix-normal latent worth the complexity?** Adding the row-independence penalty improves disentanglement but increases training instability. A simpler vector-valued latent might be a useful baseline. — **Empirical update (RViT+ runs 5–7, 2026-05-20):** the vector-latent baseline is *not* a useful simplification: collapsing the spatial scene to (B, latent_dim) at the bottleneck destroys the spatial information path even when the rest of the architecture preserves spatial structure. The diagonal per-position spatial latent (one (μ, σ²) per (channel, h, w) at the deepest encoder level) is the *minimum* faithful instantiation; matrix-normal with row-covariance is the next refinement. A pure vector latent should not be used even as a baseline. See `threads/rvit_plus_engineering.md` for the run-by-run history.
3. **What is the right reconstruction-vs-KL weighting?** The β-VAE literature (Higgins et al. 2017) gives a clear answer for single-pass VAEs; the answer for the iterative setting is open. — RViT+ run 7 demonstrated that vanilla KL on a vector latent triggers posterior collapse early (KL crushed to ≈ 0 by iter 100) and the model never recovers. Free-bits (Kingma 2016) prevents this for the spatial latent at the cost of one hyperparameter; bench-tested values are `free_bits=2.0` nats per (channel, h, w) position in run 8.
4. **How does this interact with task-specific losses (RL, classification)?** When the iterative VAE is the VAE hub in the multi-hub system, the ELBO is one objective among many; the right gradient balancing across hubs is an open question.
5. **What is the right reconstruction-loss shape for background-dominated data?** Plain MSE and plain L1 both have a trivial-constant minimum (the mean and median respectively) on background-dominated inputs — RViT+ runs 6 and 7 both converged to constant predictions because of this. Content-weighting (digit-pixel weight ≫ background weight) breaks the symmetry. The general form is `L = E[w(x) * f(x − x̂)]` where `w(x)` upweights regions of interest. For naturalistic video (UCF101), Stage-2 onwards, this may not be needed — the content is rich enough across the whole frame — but for synthetic sparse data it's load-bearing.

## Implementation notes (run-8 reference, 2026-05-20)

The RViT+ instantiation in `RViT_plus/latent.py` (`SpatialVAELatentSampler`) is the simplest faithful implementation of the multi-patch latent commitment. It samples a per-(channel, h, w) diagonal Gaussian at the deepest encoder level (C₃ in the reference architecture, native shape 6×6), with the spatial grid preserved through the bottleneck via Conv1×1 projections (no GAP, no broadcast, no Linear-over-flat-tensor at any point). The matrix-normal `MN(M, U, V)` extension with the off-diagonal penalty `\|U − \text{diag}(U)\|_F^2` for approximate row-independence is deferred but conceptually compatible — it can be added as an additional loss term on the empirical row-covariance of the sample without changing the sampler's outward shape.

The decoder side (`RViT_plus/decoder.py` `RViTPlusVideoDecoder`) reads the spatial latent into D₃ via a per-position Conv1×1 channel adapter (`latent_to_d3`), and uses D₃ as the deepest spatial state at decoder step τ=0. Per-step content flows: latent → D₃ → ascend_3to1, ascend_3to2 → D₁, D₂ → pix_out. The decoder's z₁(τ) carries only the temporal index (broadcast) — content is strictly through the spatial state path.
