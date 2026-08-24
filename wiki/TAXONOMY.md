# Taxonomy — Tags and Concepts

Every value used in a paper file's `tags:` or `concepts:` frontmatter list must appear below. This keeps the graph's edge labels consistent and prevents typo-induced silos.

When adding a new term, append it under the right group with a one-line definition. Do not delete or rename terms — add a deprecation note instead. The audit script (`tools/audit.py`) cross-checks every used tag against this file.

## Tags (broad topic flags)

Tags partition the literature into the major sub-fields the database covers. Each paper should have 1–4 tags.

### Cognitive / behavioral

- `visual-attention` — covert or overt attention to visual stimuli; cued or free-viewing.
- `working-memory` — short-term maintenance of behaviorally relevant content.
- `psychophysics` — quantitative behavior in human or animal observers.
- `posner-cuing` — the specific spatial-cuing paradigm.
- `change-detection` — change-blindness, change-detection, vigilance paradigms.
- `decision-making` — drift-diffusion, evidence accumulation, perceptual choice.
- `reaction-time` — chronometric analysis of behavior.

### Neuroscience

- `primate-neurophysiology` — single-unit, LFP, or microstimulation in NHP.
- `human-neuroimaging` — fMRI, EEG, MEG.
- `cortical-anatomy` — connectivity, laminar structure, hierarchies.
- `prefrontal-cortex` — dlPFC, FEF, working-memory areas.
- `parietal-cortex` — LIP, posterior parietal, priority maps.
- `subcortical` — superior colliculus, basal ganglia, thalamus.
- `dopamine` — DA neuromodulation, reward prediction error.
- `early-visual-cortex` — V1, V2, V4 receptive-field and tuning work.
- `lesion-microstimulation` — causal manipulation in animals.

### Computational / theoretical

- `predictive-coding` — Rao-Ballard family of generative-model accounts.
- `free-energy-principle` — Friston's variational-Bayes framework.
- `normalization-model` — divisive normalization as attention substrate.
- `biased-competition` — Desimone & Duncan style competitive accounts.
- `saliency-models` — bottom-up feature-anomaly attention models.
- `attentional-template` — top-down memory-driven attention.

### Machine learning

- `self-attention` — broad tag for any self-attention-based work; use the concept-level `self-attention-over-tokens` / `scaled-dot-product-attention` for finer granularity.
- `transformers` — self-attention-based architectures.
- `recurrent-networks` — LSTM, GRU, ConvGRU, RNN variants.
- `vision-transformers` — ViT and descendants.
- `reinforcement-learning` — RL methods, actor-critic, PPO, REINFORCE.
- `deep-learning` — broad DL methodology.
- `self-supervised-learning` — contrastive / generative pretraining.
- `world-models` — model-based RL, generative scene models, JEPA.
- `representation-learning` — feature learning, embeddings.
- `meta-learning` — learning-to-learn, in-context learning.

### Biologically-plausible / NeuroAI

- `bio-plausible-learning` — Hebbian, STDP, predictive-coding networks.
- `spiking-networks` — SNNs, surrogate gradients.
- `neuro-ai-bridging` — papers explicitly bridging the two fields.

### Methodology

- `methodology` — broad methodology tag, used when a paper's contribution is a method rather than a finding (e.g., RSA, decoding pipelines).
- `decoding-analysis` — linear / nonlinear decoders over neural / model activity.
- `representational-geometry` — RSA, manifold analysis.
- `ablation-study` — component or input ablations as causal probes.
- `review` — review or survey article.
- `theoretical-essay` — non-empirical position piece.

## Concepts (mechanism-level)

Concepts are finer-grained than tags. A paper may have many concepts. The concept layer is what the LLM wiki graph will use to build cross-paper edges.

### Attention mechanisms

- `positional-encoding` — sinusoidal or learned position embeddings injecting order information into permutation-equivariant architectures.
- `scaled-dot-product-attention`
- `multi-head-attention`
- `cross-attention`
- `self-attention-over-tokens`
- `additive-attention`
- `bahdanau-attention`
- `slot-attention`
- `recurrent-attention` — RAM-style glimpse models.
- `multiplicative-feedback`
- `additive-feedback`
- `attentional-spotlight`
- `divisive-normalization`
- `gain-modulation`
- `precision-weighting`

### Memory mechanisms

- `lstm-cell`
- `gru-cell`
- `convgru-cell`
- `xlstm`
- `working-memory-persistent-activity`
- `slow-fast-recurrence`
- `chrono-initialization`
- `error-gated-update`
- `feature-binding`

### Predictive-coding mechanisms

- `rao-ballard-coding`
- `hierarchical-predictive-coding`
- `feature-wise-linear-modulation` — FiLM.
- `generative-decoder`
- `prediction-error-map`
- `variational-free-energy`
- `inner-inference-loop`
- `expectation-maximization-inference`
- `active-inference`

### Vision

- `gabor-receptive-fields`
- `orientation-selectivity`
- `topographic-organization`
- `retinotopy`
- `ventral-stream-hierarchy`
- `dorsal-stream`
- `figure-ground-segmentation`

### Decision and action

- `drift-diffusion-model`
- `signal-detection-theory`
- `reward-modulated-attention`
- `priority-map`
- `actor-critic`
- `ppo`
- `reinforce`
- `gae`
- `distributional-rl`

### Causal-manipulation methods

- `microstimulation`
- `pharmacological-inactivation`
- `optogenetic-perturbation`
- `lesion`
- `virtual-lesion`
- `tms`

### Analytical / experimental

- `psychometric-function`
- `chronometric-function`
- `cueing-effect`
- `validity-effect`
- `cross-temporal-decoding`
- `representational-dissimilarity-matrix`

### Neuro-AI bridging

- `unsupervised-ventral-stream-model`
- `recurrence-for-temporal-dynamics`
- `attention-as-prediction-error`
- `top-down-feedback`
- `cortical-microcircuit-model`

### Core mechanisms of the user's architectural program (Private/Shared notes)

These concepts come from the user's working notes (`Private & Shared` folders) and are first-class organizing principles for the database, not just tags on individual papers. Each has its own file under `concepts/`.

- `feedback-transformer` — self-attention augmented to integrate an arbitrary number of recurrent internal states via per-state Q/K/V projection and element-wise broadcasting prior to softmax. Allows bottom-up sensory input plus parallel (multi-modal) and hierarchical (top-down + bottom-up) memory feedback at one node.
- `gridcell-rnn` — internal grid of recurrent states where each cell first undergoes spatially-independent processing (SIP), then a feedback transformer integrates information across cells and across hierarchical/parallel grids. LSTM-derived gating.
- `multi-compartmental-memory` — explicit architectural commitment to maintain multiple recurrent states in parallel, each with potentially different spatial resolution, channel dimensionality, and update timescale.
- `bidirectional-hierarchical-feedback` — every memory layer receives feedback from every other (parallel and hierarchical) layer, with explicit convolutional descending projections and conv-transpose ascending projections that close the cortical-style loop.
- `competition-emergent-predictive-coding` — the user's original hypothesis that predictive coding is a strategy for neural coalitions to win an internal competition for limited resources by modeling their rivals. Top-down feedback signals are predictions of *competing populations*, not just of sensory input.
- `multi-hub-multi-objective-system` — an MSI hub + RL hub + VAE hub architecture where each hub maintains its own memory states and all hubs' memory feeds back into a central self-attention module. Competition for self-attention control is the central learning pressure.
- `iterative-variational-encoder-decoder` — encoder runs $n_{FR}$ forward-reasoning steps over the same image, building a "guide" $H_{n_{FR}}$; decoder runs $n_{BR}$ backward-reasoning steps producing iteratively refined reconstruction proposals; KL on the guide gives a VAE objective.
- `multi-patch-distributional-latents` — treats the guide as a matrix-normal $\mathcal{MN}(M, U, V)$ with explicit row-covariance handling; row-whitening or off-diagonal penalty enforces patch-independence in the latent.
- `parallel-recurrent-units` — multiple recurrent units operating in parallel on related but distinct representations, communicating via the feedback transformer rather than concatenation.
- `descending-projections` — conv-stack operations that reshape spatially-shallow, channel-thin memory states into deeper, more abstracted ones ($n_{C_1} > n_{C_2} > \ldots$ with $d_{C_1} < d_{C_2} < \ldots$).
- `ascending-projections` — conv-transpose operations that upsample deep memory states back to the shape of shallow ones, supplying top-down feedback to V1-level processing.
- `coalition-resource-competition` — the metabolic / bandwidth competition between neural coalitions that the user proposes as the evolutionary pressure giving rise to predictive coding.
- `strategic-prediction-error` — the reformulation of prediction error as a signal of strategic surprise about a competing coalition's behavior, rather than purely sensory surprise.
- `world-model-emergence` — a world model that arises implicitly from inter-hub competition rather than from an explicit world-model training signal.
- `apical-basal-dendritic-integration` — single-neuron AND-gate mechanism where pyramidal cells integrate top-down apical input with bottom-up basal input multiplicatively (BAC firing). The cellular substrate of the Feedback Transformer's Hadamard-product feedback structure.
- `coupled-rnn-world-models` — architectures in which a separate world-model RNN is trained jointly or sequentially with a controller RNN and exposes its internal state to the controller (Schmidhuber 2015; HRM; Ha & Schmidhuber 2018). The two-hub special case of the multi-hub program.

### Additional concepts from the notes' cite trail

These appear in the user's notes and seed papers we will add for them.

- `cortico-thalamo-cortical-loops`
- `cortico-basal-ganglia-thalamic-loops`
- `system-1-vs-system-2`
- `embodied-cognition`
- `causal-reasoning`
- `factorized-representations` — Higgins-style factorized latents.
- `lec-mec-factorization` — sensory vs. spatial factorization in entorhinal cortex.
- `hierarchical-reasoning-model` — Wang et al. coupled-RNN with different temporal update rates.
- `dendritic-bayesian-integration` — Jordan et al. conductance-based dendritic Bayes-optimal cue integration.
- `multi-sensory-integration`
- `neural-oscillations-cfc` — cross-frequency coupling for binding multi-timescale info.
- `metabolic-cost-of-neural-information`
- `transthalamic-pathway` — Sherman-style cortico-thalamo-cortical drivers in which L5 of one cortical area projects via higher-order thalamus (pulvinar, posterior medial nucleus) to another cortical area, paralleling direct corticocortical projections.
- `layer-6-corticocortical` — L6 corticocortical excitatory neurons (Weiler et al.) as a major route for intra- and inter-hemispheric cortical feedback.
- `apical-dendrite-coincidence-detection` — Larkum's BAC (back-propagating action potential + apical Ca²⁺) coincidence mechanism by which pyramidal cells fire bursts only when basal (bottom-up) and apical (top-down) inputs coincide.
- `pyramidal-cell-two-compartment` — the architectural commitment that pyramidal cells implement two functionally distinct processing compartments (apical vs basal) coupled by an active dendritic mechanism.
- `bayesian-cue-integration` — combining cues (sensory modalities, prior beliefs) weighted by their reliabilities to form an optimal posterior, often by neurons or dendrites.
- `hierarchical-convergence` — HRM's mechanism where a fast inner-loop module converges to a local equilibrium, then a slow outer-loop module performs one update and resets the inner loop for a new equilibrium phase.
- `one-step-implicit-gradient` — Deep-Equilibrium-Model-style approximation that backprops only through the final-step Jacobian at a converged fixed point, avoiding BPTT.
- `deep-supervision-detached-segments` — training a recurrent model by running M segments, computing loss per segment, and detaching state between segments so gradients flow only one segment back.
- `adaptive-computation-time` — learning when to halt vs continue computation (Graves 2016, PonderNet; HRM uses a Q-learning halt head).
- `algorithmic-information-theory` — Solomonoff/Kolmogorov framing of compressible structure that Schmidhuber uses to justify curiosity-driven world-model learning.
- `curiosity-driven-learning` — intrinsic reward proportional to compression progress / prediction-improvement, used to drive exploration without external task reward.
- `coupled-rnn-controller-model` — Schmidhuber's RNN-AI framework where a controller RNN learns to query and exploit the algorithmic structure of a separately-trained predictive world-model RNN.

### Additional tags from the 2026-05-23 manual_deep_dive_2026_05_23 batch (WM / VWM / hippocampus / world models)

These tags entered the database via the 20-paper deep-dive batch on 2026-05-23. Many overlap conceptually with existing tags but are kept as the more-specific terms used by the deep-dive batch's authoring agent — see `threads/wm_vwm_hippocampus_world_models_deep_dive.md` for the cross-paper synthesis.

#### Cognitive / behavioral (extended)

- `attention` — broad tag for any attentional process (used as a coarse tag by the WM/VWM batch; prefer `visual-attention` or `spatial-attention` for finer granularity).
- `capacity` — limits on the number of items maintained in memory or attended to at once.
- `visual-working-memory` — short-term maintenance of visual content (distinct from broader `working-memory`).
- `eye-movements` — saccades, fixations, smooth pursuit as observable proxies for attention or oculomotor planning.
- `dual-task` — paradigms requiring concurrent performance on two tasks to probe shared resources or interference.
- `rehearsal` — covert or overt repetition mechanisms for maintaining WM contents.
- `templates` — attentional or memory templates that guide search or selection.
- `attention-capture` — exogenous, stimulus-driven capture of attention by salient or behaviorally-relevant features.
- `memory` — broad tag for memory processes (used as a coarse tag; prefer `working-memory`, `visual-working-memory`, etc. for finer granularity).
- `generalization` — transfer of learned representations or behaviors to novel inputs.

#### Neuroscience (extended)

- `hippocampus` — hippocampal-formation neuroanatomy and physiology including dentate gyrus, CA1–CA3, subiculum.
- `entorhinal-cortex` — EC including medial-EC (grid cells, path integration) and lateral-EC (object/content).
- `place-cells` — hippocampal pyramidal neurons with location-specific firing fields.
- `grid-cells` — MEC neurons with hexagonal-lattice spatial firing patterns.
- `delay-activity` — sustained or dynamic neural activity during the maintenance period of a delay task.
- `thalamocortical` — interactions between thalamic relay/order nuclei and cortex.
- `single-unit` — electrophysiological recording from individual neurons.
- `navigation` — spatial cognition including path integration, route planning, allocentric mapping.
- `top-down` — cognitively-driven or higher-level signals modulating lower-level processing.
- `alpha-oscillations` — 8–12 Hz cortical rhythms implicated in attentional gating and WM.
- `spatial-attention` — attention to a location in retinotopic or allocentric space.
- `spatial-coding` — neural representation of spatial position.
- `sensory-recruitment` — the hypothesis that WM contents are stored in early sensory cortex.
- `distributed-coding` — representation spread across many neurons or brain regions rather than localized.
- `population-coding` — encoding of stimulus or task variables in the joint activity of a population of neurons.
- `dynamic-coding` — time-varying neural codes (Stokes-style) in which the population trajectory itself encodes information.
- `path-integration` — updating estimated position via integration of self-motion signals.
- `short-term-synaptic-plasticity` — facilitation, depression, or augmentation of synaptic transmission on a 100ms–10s timescale.

#### Computational / theoretical (extended)

- `cognitive-architecture` — formal architectural proposals for cognitive systems (Baddeley-Hitch, ACT-R, etc.).
- `theoretical` — broad tag for non-empirical theoretical contributions.
- `foundational` — broad tag for landmark or originating contributions.
- `cognitive-map` — abstract relational representations of structured environments (Tolman; Behrens).
- `cognitive-control` — top-down regulation of goal-directed behavior.
- `resource-model` — continuous-resource (vs slot-based) models of WM capacity.
- `emergent-property` — a property arising from system dynamics rather than from a designed mechanism.
- `emergent-representation` — representations emerging from training without being explicitly imposed.
- `latent-dynamics` — temporal evolution of internal-state (latent) variables.
- `latent-prediction` — predicting in a learned latent space rather than in raw observation space (JEPA-style).
- `relational-memory` — memory for relations between items rather than item identities alone.
- `successor-representation` — predictive state representation encoding expected future occupancy (Dayan; Stachenfeld).
- `mcts` — Monte Carlo tree search.
- `planning` — model-based deliberation over future action sequences.
- `imagination` — internal generation of trajectories or scenes (Dreamer-style imagined rollouts).

#### Machine learning (extended)

- `jepa` — joint-embedding predictive architectures (Assran/LeCun lineage).
- `masked-image-modeling` — pretraining by predicting masked patches (MAE, I-JEPA).
- `non-generative` — self-supervised learning without an explicit generative-reconstruction objective.
- `neural-network` — broad tag for neural-network methods.
- `rssm` — Recurrent State-Space Model (Hafner et al.; Dreamer's world-model architecture).
- `transformer` — singular alternative spelling of the existing `transformers` tag.
- `external-memory` — differentiable memory modules separate from the recurrent state (Neural Turing Machine, MERLIN, Differentiable Neural Computer).
- `partial-observability` — environments where the agent does not receive full state information.

#### Methodology (extended)

- `binding` — methodological probes of feature binding in perception or memory.
- `inverted-encoding-model` — model-based decoding technique recovering tuning-curve-style channel responses.
- `shared-substrate` — broad methodological tag for studies probing whether two processes share neural substrate.
- `delayed-estimation` — continuous-report VWM paradigm.
- `eeg` — electroencephalography methodology.
- `mvpa` — multivariate pattern analysis.
- `spatial` — broad tag for spatially-organized representations (used coarsely by the WM/VWM batch).

### Snake_case concept aliases

These snake_case concept terms were introduced into paper frontmatter by the 2026-05-23 manual_deep_dive_2026_05_23 batch. Each is structurally identical to an existing kebab-case concept term and resolves to the same `concepts/*.md` file under the build_graph.py dash-to-underscore normalization (build_graph.py:214). They are kept here as aliases for audit-cleanliness rather than re-edited in the 20 paper files. A future iteration may consolidate by editing the papers to use kebab-case and removing this section.

- `bidirectional_hierarchical_feedback` — alias of `bidirectional-hierarchical-feedback`.
- `coalition_resource_competition` — alias of `coalition-resource-competition`.
- `coupled_rnn_world_models` — alias of `coupled-rnn-world-models`.
- `gridcell_rnn` — alias of `gridcell-rnn`.
- `hierarchical_predictive_coding` — alias of `hierarchical-predictive-coding`.
- `iterative_variational_encoder_decoder` — alias of `iterative-variational-encoder-decoder`.
- `multi_compartmental_memory` — alias of `multi-compartmental-memory`.
- `multi_hub_multi_objective_system` — alias of `multi-hub-multi-objective-system`.
- `slow_fast_recurrence` — alias of `slow-fast-recurrence`.
- `world_model_emergence` — alias of `world-model-emergence`.

### Concept: hidden-state-perturbation

- `hidden-state-perturbation` — perturbation methodology that intervenes on a recurrent network's hidden state during inference to test causal claims about its computational role (e.g., the Stokes 2015 "ping" methodology; trained-RNN analyses that inject targeted state perturbations and read out downstream effects).

## Adding new terms

When a paper introduces a mechanism that doesn't fit any existing concept, add the new term here (under the appropriate group, with a one-line gloss) before using it in the paper's frontmatter. The audit script will reject undefined terms.
