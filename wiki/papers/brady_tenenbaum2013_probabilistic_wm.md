---
id: brady_tenenbaum2013_probabilistic_wm
title: "A probabilistic model of visual working memory: incorporating higher order regularities into working memory capacity estimates"
authors:
  - "Brady, Timothy F."
  - "Tenenbaum, Joshua B."
year: 2013
venue: "Psychological Review"
doi: "10.1037/a0030779"
arxiv: ""
url: "https://doi.org/10.1037/a0030779"
tags:
  - working-memory
  - theoretical-essay
  - change-detection
  - psychophysics
concepts:
  - bayesian-cue-integration
  - precision-weighting
  - feature-binding
  - factorized-representations
  - variational-free-energy
related:
  - bays2024_wm_representation
  - luck_vogel1997_wm_capacity
  - ernst_banks2002_cue_combination
  - jordan2023_dendritic_bayesian
  - aitchison_lengyel2017_pc_bayesian
  - feldman_friston2010_attention_free_energy
  - friston2010_fep_unified_theory
  - schneegans_bays2017_feature_binding_wm
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_35
status: full
depth: full
last_updated: "2026-05-16"
---

# A probabilistic model of visual working memory: incorporating higher order regularities into working memory capacity estimates

## 1. Abstract

Visual working memory (VWM) is conventionally characterized as a small set of independent slots, each holding an item with fixed precision; the canonical claim is that capacity is approximately four items (Luck & Vogel, 1997). Brady and Tenenbaum (2013) argue that this independent-items framing systematically misrepresents how visual memory operates over real-world displays, where items co-occur, group perceptually, and obey learned higher-order regularities. The authors develop a hierarchical Bayesian model of VWM in which a remembered display is generated from a layered prior: a high-level prior over scene structure (groupings, color statistics, configural relationships), a mid-level prior over chunks of items that obey shared regularities, and a low-level prior over individual feature values. Inference at recall combines the noisy item-level evidence with the higher-order priors to produce a posterior over the true display. Across change-detection and continuous-report experiments using both standard random displays and displays with embedded color/spatial regularities, the authors show that capacity estimates derived under independent-slot assumptions undercount how much information observers actually encode, because observers exploit compressibility through chunking and prior structure. The probabilistic model fits the empirical data substantially better than independent-slot or fixed-precision continuous-resource accounts, and it predicts the specific patterns of bias and false-alarm errors that arise when higher-order regularities are violated.

## 2. Why this matters for us

Brady and Tenenbaum 2013 is the foundational Bayesian-brain treatment of visual working memory and the immediate intellectual precursor to Bays, Schneegans, Ma, and Brady's 2024 synthesis ([bays2024_wm_representation](research_db/papers/bays2024_wm_representation.md)). Where Luck-Vogel 1997 treats VWM as a discrete-slot register and Bays-style continuous-resource models treat it as a precision-weighted continuous resource, Brady and Tenenbaum reframe VWM as Bayesian inference over a structured generative model of the display. This is precisely the framing the user's program adopts at the architectural level: PRISM's variational-free-energy objective, the iterative-VAE encoder-decoder, and the multi-hub feedback architecture all instantiate the same commitment that memory is the posterior of a structured generative model rather than a buffer of independent slots.

Three specific architectural commitments in the user's program are directly underwritten by this paper. First, the continuous, probabilistically regularized memory state (PRISM's $M_t$, the user's guide $\tilde H_0$) is the network analog of the posterior over the display. Second, the hierarchical multi-compartmental memory stack is the network analog of the hierarchical prior, with deeper layers encoding higher-order regularities. Third, the iterative encoder-decoder rollout ($n_{FR} \to n_{BR}$) is the network analog of variational posterior inference, with the KL term enforcing the prior and the reconstruction term enforcing the likelihood.

## 3. Key claims

1. **Independent-slot models systematically misestimate VWM capacity** by ignoring that observers exploit display structure to encode more information than a slot count predicts.
2. **VWM is hierarchical Bayesian inference,** with priors over groupings and higher-order configural regularities sitting above priors over individual item features.
3. **Chunking is compressibility.** Items that share regularities (color repetitions, spatial groupings, configural symmetries) are encoded jointly at lower per-item cost, raising the effective number of remembered items.
4. **Inference at recall combines noisy item evidence with the structural prior,** producing systematic biases toward prior-consistent values and away from prior-inconsistent values.
5. **The model unifies change-detection and continuous-report paradigms.** The same generative posterior predicts both binary change-detection responses and the distribution of continuous-report errors.
6. **Capacity is not a property of the buffer; it is a property of the inference.** Observed performance is the joint product of generative-model priors, sensory noise, and the loss function appropriate to the task.
7. **Bayesian priors predict specific error signatures.** Prior-driven biases, attractor effects near prior modes, and elevated false-alarm rates when probes violate higher-order regularities are all predicted and observed.
8. **Priors are learned online from the display ensemble.** Within a short experimental block, observers update the strength of the regularity prior based on the trial-to-trial statistics they encounter, and the magnitude of bias grows with prior strength.
9. **The framework generalizes Luck-Vogel and Bays-Husain as special cases.** Independent-item priors yield the slot model; uniform priors over a continuous feature space yield the Bays-Husain mixture model; structured priors yield the hierarchical model. The new framework is strictly more general than the prior baselines.

## 4. Methods

The authors construct a generative model of a display $D = \{x_1, \ldots, x_n\}$ where each $x_i$ is an item's feature vector (color, location, orientation). Items are not drawn independently; instead, a latent group structure $G$ partitions items into chunks, and a higher-order regularity $R$ governs feature relationships within and across chunks. The full prior decomposes as

$$
p(D) = \sum_G \sum_R p(R)\, p(G \mid R) \prod_{c \in G} p(\{x_i\}_{i \in c} \mid R)
$$

The chunk-level prior $p(\{x_i\}_{i \in c} \mid R)$ encodes within-chunk correlations: paired chunks share a color or a spatial offset; symmetric chunks share a configural axis; texture chunks share a higher-order statistical regularity. The grouping prior $p(G \mid R)$ is itself learned from the display ensemble across trials, so that an observer's effective prior at trial $t$ reflects the statistics of all preceding trials in the block.

At encoding, observers obtain noisy sensory evidence $y_i = x_i + \epsilon_i$ with item-level Gaussian noise of variance $\sigma_y^2$. The likelihood under independent encoding is $p(Y \mid D) = \prod_i \mathcal{N}(y_i; x_i, \sigma_y^2 I)$. At recall, the posterior over the true display combines this evidence with the structured prior:

$$
p(D \mid Y) \propto p(Y \mid D)\, p(D)
$$

The response rule depends on the task. For continuous report, the response is the posterior-expected feature $\hat x_i = \mathbb{E}_{p(D \mid Y)}[x_i]$. For change detection, the response is the Bayes-optimal decision under a 0–1 loss: compare $p(D = D_{\text{probe}} \mid Y)$ to a threshold. Marginalization over the latent group structure $G$ and regularity $R$ is performed exactly for the small displays the experiments use and by Monte Carlo otherwise.

Empirically, the authors run change-detection and continuous-report tasks with displays in three classes: (a) standard random displays matching the Luck-Vogel paradigm; (b) displays with embedded color regularities (e.g., paired or grouped colors, color frequency distributions skewed toward a subset of the color wheel); (c) displays with embedded spatial / configural regularities (paired locations, symmetric arrangements, texture-like repetitions). Set sizes range from below to well above the conventional four-item limit. Model fits compare the hierarchical Bayesian model against independent-slot, fixed-precision continuous-resource, mixture-model (Bays-Husain), and intermediate variant baselines. Fits are evaluated by log-likelihood on held-out trials and by qualitative match to specific error signatures (bias direction, false-alarm asymmetry).

A central methodological move is the use of *both* paradigms (change-detection and continuous-report) under a shared model with shared parameters. Earlier modeling work tended to fit one paradigm or the other; by demonstrating that the same generative posterior predicts both, the authors raise the bar for what counts as an adequate account of VWM. The cost is increased model complexity; the benefit is increased falsifiability, because a model that fits one paradigm but fails the other is now decisively rejected.

The hierarchical Bayesian inference is implemented exactly when display size is small (so the partition space is tractable) and via sequential Monte Carlo sampling when the partition space grows. The paper makes both implementations available and shows that the qualitative results are stable across the inference algorithm; the algorithm is not load-bearing for the empirical conclusions.

## 5. Results

The principal quantitative findings, in the paper's own terms:

- **Capacity is underestimated by independent-slot fits** when structured displays are scored under independent-item assumptions. The hierarchical model recovers substantially higher effective capacity for displays with exploitable regularities — the gap grows with the regularity strength and with the set size.
- **Continuous-report errors show prior-driven bias.** Reports of features near prior modes are pulled toward those modes; reports far from prior modes show elevated noise. The bias magnitude scales with the relative precision of the prior versus the sensory likelihood, exactly as a Bayesian estimator predicts.
- **Change-detection false-alarm rates rise systematically** when probes violate higher-order regularities embedded at study. Hits and false alarms shift in the directions the Bayesian posterior predicts, not in the directions independent-slot models predict.
- **Model comparison favors hierarchical priors.** The hierarchical Bayesian model fits the joint distribution of errors and decisions across paradigms substantially better than independent-slot and fixed-precision continuous-resource baselines, with the largest gains on structured displays. The fit improvement is robust across observers and set sizes.
- **The same model fits both paradigms with shared parameters,** demonstrating that change-detection and continuous-report tap a common underlying representation when interpreted through Bayesian inference. Earlier accounts had argued that the two paradigms tap different representations; the unified Bayesian account dissolves the apparent inconsistency.
- **Higher-order regularities are learned across trials,** with the inferred prior strength growing within a block as the observer accumulates exposure to the embedded regularity. Trial-to-trial learning dynamics in the bias signature track this accumulation.
- **The model reproduces classic capacity-estimation results as a special case** when the display has no exploitable regularities: the independent-item posterior collapses onto the standard Luck-Vogel and Bays-Husain predictions for unstructured displays, so the new framework subsumes rather than replaces the prior literature.
- **Stronger regularities produce larger bias and smaller variance.** As the precision of the embedded regularity prior grows relative to sensory likelihood precision, posterior-driven bias toward the prior mode grows and reported variance around the prior mode shrinks — the quantitative signature predicted by a Bayesian estimator with varying prior strength.
- **Configural regularities produce asymmetric error structure.** Symmetric or paired-location displays produce false-alarm patterns where the false alarms cluster on probe items that preserve the configural relationship; this clustering is predicted by the hierarchical model but is opaque to independent-item baselines.
- **Cross-feature integration is observed.** When a chunk regularity links two features (e.g., color and location), violations of the linked structure produce coordinated errors across both features rather than independent errors on each — the signature of joint, not factorial, encoding.
- **Posterior bias scales with set size in the structured-display condition** in a way independent-item models cannot reproduce: at small set sizes the prior contribution is dominated by the likelihood and bias is weak; at larger set sizes the per-item likelihood weakens and the bias toward the prior grows, exactly as Bayesian inference predicts.

## 6. Critique / limitations

The model's hierarchical prior is specified at the level of display statistics rather than mechanistically grounded in cortical computation. The paper does not commit to a particular neural substrate for the prior or the posterior computation; it leaves the implementational question open. Subsequent work (Bays et al. 2024; Bouchacourt & Buschman 2019) has begun to supply mechanistic accounts in terms of population-level continuous attractors and recurrent neural networks, but the connection between those mechanisms and Brady-Tenenbaum's hierarchical-prior framing is not fully established.

The set of "higher-order regularities" considered is limited to the regularities the authors choose to embed. Whether the model generalizes to the full open-ended class of real-world scene regularities is asserted rather than demonstrated, and the inference machinery scales poorly as the regularity class grows. The combinatorial explosion in the space of groupings and regularities is a practical bottleneck that the paper handles by restricting attention to small, well-defined regularity classes.

The Bayesian-optimality framing licenses post-hoc curve-fitting: a sufficiently flexible prior will match almost any empirical pattern. The model's predictions are most compelling where they generate specific qualitative signatures (bias direction, false-alarm asymmetries) rather than where they merely fit error magnitudes. The Bayesian-cognitive-science literature has been criticized on this point generally (Bowers and Davis 2012; Marcus and Davis 2013), and the criticism applies to this paper in the same form.

The model treats the encoding noise as Gaussian and item-wise independent, which is a strong simplification: real visual encoding has feature-correlated noise, attention-dependent precision, and stimulus-specific tuning that the model abstracts away. Incorporating these features would change the predicted bias and false-alarm patterns in ways the paper does not explore.

The empirical paradigm continues to rely on briefly presented arrays of synthetic items. Whether the hierarchical-prior account scales to naturalistic scenes — where the prior is open-ended and learned — is a prediction rather than an established result. The natural-scene generalization is precisely where the framework would be most informative for architectural work, but it is also where the model's combinatorial cost grows fastest.

The continuous-vs-discrete debate is not directly resolved by this paper. The hierarchical Bayesian framing is compatible with either a continuous or a slot-like item-level representation; the contribution is at the level above item encoding, not at the level of how individual items are stored. Readers who care primarily about the slot-vs-resource question will find this paper orthogonal rather than decisive.

The model is also silent about the time course of inference. A Bayesian posterior is an idealized object; how human observers actually compute it — over what time scale, with what neural resources, with what online vs offline computation split — is left to subsequent work. The paper makes no commitment to a specific algorithmic implementation, and the absence of an algorithm-level account leaves open the question of whether human VWM is genuinely Bayesian or merely approximated by a Bayesian account at the computational level (Marr 1982).

Finally, the framework's use of a fully specified generative model of the display is itself a strong assumption: real observers do not have access to the experimenter's true generative model. The paper treats the inferred prior as a reasonable approximation to what observers learn from the trial ensemble, but the gap between the experimenter's prior and the observer's prior is a known source of misfit that the paper acknowledges but does not fully quantify.

## 7. Connection to our work

This paper is one of the most direct theoretical anchors for the user's architectural program. Three connections are load-bearing.

**Continuous probabilistic memory and the variational-free-energy objective.** The user's iterative variational encoder-decoder ([iterative-variational-encoder-decoder](research_db/concepts/iterative-variational-encoder-decoder.md)) treats the guide state $\tilde H_0$ as a latent random variable with a Gaussian posterior conditioned on the encoder output and a unit-Gaussian prior. The KL regularizer is interpreted explicitly as Friston's variational free energy ([friston2010_fep_unified_theory](research_db/papers/friston2010_fep_unified_theory.md)). Brady and Tenenbaum supply the cognitive-science version of the same commitment: VWM contents are the posterior of a generative model, and the prior shapes both the bias and the effective capacity of memory. The user's continuous, probabilistically regularized memory state is the architectural realization of this hierarchical Bayesian view.

**The iterative-VAE encoder-decoder framework as posterior inference.** Brady and Tenenbaum's display posterior $p(D \mid Y) \propto p(Y \mid D)\, p(D)$ is the cognitive analog of the user's $n_{FR} \to n_{BR}$ rollout. The encoder's forward-reasoning passes accumulate evidence from the input (the likelihood); the decoder's backward-reasoning passes refine the reconstruction under the structural prior encoded in network weights and the unit-Gaussian latent prior. The iterative refinement is variational inference over the generative model, exactly the operation Brady and Tenenbaum attribute to VWM recall. The KL term enforces the prior; the reconstruction term enforces the likelihood; the rollout implements gradient-style refinement of the posterior.

**The Bayesian-brain tradition and cue integration at memory.** Brady and Tenenbaum sit alongside Ernst and Banks 2002 ([ernst_banks2002_cue_combination](research_db/papers/ernst_banks2002_cue_combination.md)) and Jordan et al. 2023 ([jordan2023_dendritic_bayesian](research_db/papers/jordan2023_dendritic_bayesian.md)) and Aitchison and Lengyel 2017 ([aitchison_lengyel2017_pc_bayesian](research_db/papers/aitchison_lengyel2017_pc_bayesian.md)) in committing the cortex to Bayesian-optimal inference. The user's multi-hub system, in which each hub generates priors that bias the central self-attention substrate via Q/K modulation, is a network-level realization of this commitment: hubs supply structured priors, the sensory stream supplies the likelihood, and attention is the posterior. Where Brady and Tenenbaum apply the framework to memory contents, the user applies it to the entire perception-memory-action loop.

**Continuous representations and compressibility through chunking.** The paper's central insight — that effective capacity is set by compressibility, not by slot count — directly motivates architectural choices in the multi-compartmental memory system. Descending projections ([descending-projections](research_db/concepts/) — defined in the taxonomy) compress shallow spatial features into deeper, channel-richer abstractions; this is the network realization of chunking. The user's commitment to factorized representations ([factorized-representations](research_db/concepts/)) and to a structured latent ([multi-patch-distributional-latents](research_db/concepts/)) follows the same principle: representations that exploit display regularities encode more information at lower cost. Brady and Tenenbaum supply the cognitive justification for why this is the right inductive bias for a memory system.

A specific prediction the user's program inherits from this paper: in change-detection tasks with structured displays, the recurrent ViT should show prior-driven false-alarm patterns analogous to those Brady and Tenenbaum report in humans. Testing this in the published change-detection paradigm (2502.10955) is a natural follow-up that would tie the architectural commitment to a measurable behavioral signature. The published change-detection benchmark uses unstructured random displays at $\leq 4$ items, which lives entirely in the regime where the Bayesian model reduces to the independent-item baseline; the interesting test is whether the architecture, when scaled to structured displays at higher set sizes, exhibits the same compressibility-driven capacity advantage human observers do.

A second prediction concerns the iterative-VAE rollout itself. Brady and Tenenbaum's posterior $p(D \mid Y)$ is a fixed-point object: an idealized observer computes it exactly. The user's iterative encoder-decoder approximates this fixed point through iteration — $n_{FR}$ encoder passes accumulate the likelihood, $n_{BR}$ decoder passes refine toward the posterior mode. The expected signature is that reconstruction quality should improve monotonically across decoder steps (consistent with the user's exponential-weighting schedule on the reconstruction loss) and that the rate of improvement should be larger for displays with stronger embedded regularities, because the prior contributes more to the posterior in those cases. This is a directly testable prediction the user's Video VAE results already partially address; structured-image experiments would sharpen the test.

A third connection, more philosophical, concerns the framing of competition-emergent predictive coding ([competition-emergent-predictive-coding](research_db/concepts/)). Brady and Tenenbaum frame the prior as a model of the environment. The user's reformulation frames the prior as a model of competing internal coalitions: top-down feedback is a prediction of what other hubs will represent, not (only) of what the sensory periphery will produce. Brady and Tenenbaum's environmental-prior account is a special case of the user's broader competition account in which the "competitor" coalition is the sensory periphery. The Brady-Tenenbaum result that learned environmental regularities raise effective capacity is, under the user's reframing, an instance of the more general claim that coalitions accumulate predictive models of their rivals over experience.

**Feature binding and the multi-patch matrix-normal latent.** Brady and Tenenbaum's groupings $G$ partition items into chunks that share within-chunk structure. The user's matrix-normal latent $\mathcal{MN}(M, U, V)$ over the guide ([multi-patch-distributional-latents](research_db/concepts/)) imposes a related but distinct decomposition: rows are patches, columns are guide channels, and the row covariance $U$ models patch-to-patch dependencies. The user's row-whitening penalty $\|U - \text{diag}(U)\|_F^2$ pushes the latent toward independent patches, which is the opposite operational direction from Brady and Tenenbaum's chunking. The reconciliation: chunking captures structured dependency at the level of perceptual groupings, while patch-independence is a useful inductive bias at the level of latent variables. A unified picture would have a hierarchical latent — patch-independent at the bottom, group-structured above — which is exactly the form Brady and Tenenbaum advocate for cognitive representations and which the user's hierarchical memory stack already implements in network terms.

**Precision-weighting at the memory level.** Brady and Tenenbaum's posterior weights the prior by the prior precision and the likelihood by the likelihood precision in the standard Bayesian way. This is the same operation Feldman and Friston (2010, [feldman_friston2010_attention_free_energy](research_db/papers/feldman_friston2010_attention_free_energy.md)) frame as precision-weighted attention. The user's Feedback Transformer ([feedback-transformer](research_db/concepts/feedback-transformer.md)) implements this at the network level: per-state Q/K/V projections are multiplied element-wise into the sensory Q/K/V before softmax, and the multiplicative gating sets the relative weight of each feedback source. Brady-Tenenbaum chunking-prior precision $\to$ Feldman-Friston attentional precision $\to$ Feedback-Transformer Hadamard gating is a three-level chain that the user's program treats as a single phenomenon expressed in different vocabularies.

**Connection to Bays 2024.** Brady and Tenenbaum 2013 and Bays et al. 2024 are continuous-historical: the same first author (Brady) co-authored both, and the 2024 review explicitly cites the 2013 paper as the foundational hierarchical-prior framework. The user's program therefore inherits a coherent two-paper anchor for the Bayesian-cognitive-science view of memory: 2013 supplies the formal probabilistic model, 2024 supplies the contemporary empirical synthesis and the connection to neural-network mechanisms. Future manuscripts engaging with VWM should cite both.

**Implications for the published Recurrent ViT.** The published Recurrent ViT (2502.10955) operates in the unstructured-display regime where Brady and Tenenbaum's framework reduces to the independent-item baseline. The paper's reported behavioral signatures — improved performance with more recurrent passes, attention maps that focus and defocus across passes — are consistent with iterative posterior refinement under a learned prior, but the unstructured displays do not distinguish a structured-prior account from a flat-prior account. The natural follow-up is to run the same architecture on structured displays at higher set sizes and look for the chunking-driven capacity advantage the Bayesian model predicts.

**Implications for PRISM v1 and v2.** PRISM v1's inner variational-inference loop on $M_t$ is structurally analogous to a single-step approximation of Brady and Tenenbaum's posterior, with the prior implicit in the network weights and the likelihood given by the current sensory input. PRISM v2's slow-fast memory split corresponds, at a stretch, to Brady and Tenenbaum's group-level vs item-level prior decomposition: the slow memory accumulates higher-order regularities; the fast memory tracks item-level features. The user's program might frame PRISM v2 explicitly as a network implementation of the Brady-Tenenbaum hierarchy, which would supply a strong external citation for the dual-timescale commitment.

**Summary of the architectural commitment.** Brady and Tenenbaum's central message — VWM is not a buffer of items but a posterior over a structured generative model — maps cleanly onto every layer of the user's program. The Feedback Transformer is the network implementation of multi-source prior combination. The multi-compartmental memory is the network implementation of hierarchical prior structure. The iterative VAE encoder-decoder is the network implementation of posterior inference. The competition-emergent predictive-coding thesis generalizes Brady and Tenenbaum's environmental prior to a prior over competing internal coalitions. Taken together, the user's program is best read as a network-level realization of the Brady-Tenenbaum hierarchical Bayesian view of memory, extended to operate over time, across coalitions, and at network scale.

## 8. Citations to follow

- `luck_vogel1997_wm_capacity` — the discrete-slot baseline this paper argues against. In seed, full depth.
- `bays2024_wm_representation` — the contemporary synthesis that builds on this framework. In seed, full depth.
- `ernst_banks2002_cue_combination` — the Bayesian-cue-integration parent literature. In seed, full depth.
- `jordan2023_dendritic_bayesian` — neuron-level Bayesian integration. In seed.
- `aitchison_lengyel2017_pc_bayesian` — predictive coding as Bayesian inference. In seed.
- `schneegans_bays2017_feature_binding_wm` — feature binding under continuous WM. In seed.
- `bays_husain2008_dynamic_shifts_visual_wm` — Bays's foundational continuous-resource paper. Not in seed.
- `ma_husain_bays2014_changing_concepts_wm` — Ma et al.'s review of changing concepts in WM. Not in seed.
- `orhan_jacobs2013_efficient_coding_wm` — efficient-coding accounts of WM. Not in seed.
- `sims2012_information_theory_wm` — information-theoretic capacity accounts. Not in seed.
- `tenenbaum2011_grow_a_mind` — Tenenbaum's broader hierarchical-Bayesian framework. Not in seed; supplies the parent framework Brady-Tenenbaum applies to WM.
- `feldman_friston2010_attention_free_energy` — precision-weighted attention as Bayesian inference. In seed.
- `bouchacourt_buschman2019_population_wm` — network model with continuous-attractor WM. Not in seed; the mechanistic counterpart to this paper's computational-level account.
- `feigenson_carey2002_object_set_chunking` — chunking in infant cognition. Not in seed; supplies developmental evidence for compressibility.
- `griffiths_kemp_tenenbaum2008_bayesian_cognition` — the Bayesian-cognitive-science textbook chapter. Not in seed.
