---
id: miconi_vanrullen2016_feedback_attention
title: "A Feedback Model of Attention Explains the Diverse Effects of Attention on Neural Firing Rates and Receptive Field Structure"
authors:
  - "Miconi, Thomas"
  - "VanRullen, Rufin"
year: 2016
venue: "PLoS Computational Biology"
doi: "10.1371/journal.pcbi.1004770"
arxiv: ""
url: "https://doi.org/10.1371/journal.pcbi.1004770"
tags:
  - theoretical-essay
  - visual-attention
  - deep-learning
  - neuro-ai-bridging
concepts:
  - top-down-feedback
  - multiplicative-feedback
  - recurrence-for-temporal-dynamics
  - divisive-normalization
  - gain-modulation
  - biased-competition
  - cortical-microcircuit-model
  - bidirectional-hierarchical-feedback
related:
  - gilbert_li2013_topdown
  - keller_mrsic_flogel2018_pc_review
  - bastos2012_canonical_microcircuits
  - dosovitskiy2020_vit
  - kietzmann2019_recurrence_required
  - reynolds_heeger2009_normalization
  - reynolds1999_competitive_v2_v4
  - desimone_duncan1995_biased_competition
  - moore_armstrong2003_fef_microstim
  - spratling2008_pc_biased_competition
  - boshra_kastner2022_attention_control
  - cohen_maunsell2009_correlations
  - reynolds_chelazzi2004_attentional_modulation
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_118
status: full
depth: full
last_updated: "2026-05-16"
---

# A Feedback Model of Attention Explains the Diverse Effects of Attention on Neural Firing Rates and Receptive Field Structure

## 1. Abstract

Visual attention has many effects on neural responses, producing complex changes in firing rates, as well as modifying the structure and size of receptive fields, both in topological and feature space. Several existing models of attention suggest that these effects arise from selective modulation of neural inputs. However, anatomical and physiological observations suggest that attentional modulation targets higher levels of the visual system (such as V4 or MT) rather than input areas (such as V1). Here we propose a simple mechanism that explains how a top-down attentional modulation, falling on higher visual areas, can produce the observed effects of attention on neural responses — including response-gain and contrast-gain effects, biased competition, feature-similarity gain, and receptive-field shifts and resizings in both topological and feature space.

## 2. Why this matters for us

Miconi & VanRullen 2016 is, among the seed papers, the cleanest computational demonstration that *a single architectural mechanism — multiplicative top-down feedback into a recurrent two-layer hierarchy with divisive normalization* — suffices to reproduce essentially the entire catalogue of attentional effects documented in primate single-unit physiology. It is the most direct conceptual ancestor of the user's Feedback Transformer (`the_user_architectural_program.md` §1) and the Recurrent ViT's multiplicative-feedback variant (2502.10955, §6.7). Where Gilbert & Li 2013 catalogue the *phenomena* of dynamic, top-down-modulated V1, this paper demonstrates that a deliberately minimal *model* — iterative recurrence + modulatory feedback + normalization — is sufficient to generate those phenomena, and that the attentional signal need only be injected at the top of the hierarchy. The architectural lesson the paper teaches is precisely the lesson the user's program builds on: an iterate-and-attend loop, with feedback entering through a multiplicative gate rather than as an additive driving signal, recovers cortex-like adaptive-RF dynamics for free.

## 3. Key claims

1. Top-down attentional modulation falling only on a higher visual area (V4/MT-equivalent) is propagated via modulatory feedback to lower areas and there produces the full range of single-cell attentional signatures — response gain, input/contrast gain, biased competition, feature-similarity gain, and RF shifts and resizings.
2. Feedback is *multiplicative* (modulatory), not driving: the attentional signal scales the gain of feedforward-driven excitation rather than supplying its own drive.
3. The same two-layer, recurrent, normalization-equipped network simultaneously produces topological RF effects (shifts toward the focus of attention; shrinkage inside the RF; expansion outside) and feature-space RF effects (tuning curves shift toward attended orientation).
4. Divisive normalization, acting on the modulated activations, is the mechanism that converts simple multiplicative feedback into the *diverse* (response-gain vs contrast-gain; enhancement vs suppression) signatures observed empirically — the form of the effect depends on where the attended stimulus sits relative to the RF and the competing stimulus.
5. The model makes a falsifiable novel prediction: attentional effects on contrast-response curves should shift from response gain to contrast gain as the spatial focus of attention drifts away from the studied cell. This is a specific, parametric prediction that can be tested in single-unit recordings.
6. Attentional modulation manifests earlier and more strongly in the higher layer than in the lower layer, consistent with the anatomical-physiological observation (Buffalo et al. 2010; Gregoriou et al. 2009) that attention targets higher areas first and is propagated downward via feedback.
7. The same architecture explains both spatial and feature-based attention: changing the attentional field $A$ from a Gaussian over retinotopic positions to a Gaussian over orientation channels swaps spatial RF effects for feature-space RF effects without any other change to the model.
8. The diversity of attentional effects in the empirical literature is not evidence for multiple distinct mechanisms; a single mechanism (recurrent multiplicative feedback + normalization) generates all of them, with the apparent diversity arising from where the attended stimulus is positioned relative to the cell's RF and competing stimuli.

## 4. Methods

A purely computational study; no new physiological data. The model is a two-layer recurrent network. The bottom layer ("V1") has 8 orientation-selective Gabor-filter cells per retinotopic location ($\sigma_\text{Bottom} = 3$ px). The top layer ("V4/MT") has the same orientation channels but coarser spatial pooling. The two layers are reciprocally connected: feedforward weights are convolutional Gabor projections; feedback weights are *proportional* to the feedforward weights (so feedback "knows" where its drive came from).

Layer dynamics are iterative — the network is run for ~30 iterations per stimulus until equilibrium. The bottom-layer equilibrium activation at position $x$ and orientation $\theta$ obeys

$$
R^\text{Bot}_{x,\theta} \propto \big[(I * G_\theta)_x \cdot (1 + FB_{x,\theta})\big]^2 \;\Big/\; \big(\sigma^2 + \sum_{x',\theta'} k_\text{inh}(x - x') R^\text{Bot}_{x',\theta'}\big)
$$

where $G_\theta$ is the orientation-$\theta$ Gabor filter, $I$ is the input image, $FB_{x,\theta}$ is the modulatory feedback term, and the denominator is the divisive-normalization signal with a Gaussian inhibitory kernel ($\sigma_\text{Inh} = 1$). The squared exponent implements a power-law response. The top-layer activation has the same functional form with bottom-layer activity playing the role of input and an *attentional field* $A_{x,\theta}$ replacing $FB$:

$$
R^\text{Top}_{x,\theta} \propto \big[\textstyle(\sum_{x',\theta'} w^\text{ff}_{x,\theta,x',\theta'} R^\text{Bot}_{x',\theta'}) \cdot A_{x,\theta}\big]^2 \;\Big/\; (\text{normalization})
$$

The attentional field $A_{x,\theta}$ is a Gaussian centred on the attended location (with $\sigma_\text{AttSpat} = 3$ for spatial attention) or on the attended orientation (with width $\sigma_\text{Ori}$ for feature-based attention). $A$ multiplies the top-layer drive directly; the feedback term $FB$ in the bottom-layer equation is then computed from $R^\text{Top}$ via the same proportional-to-feedforward connectivity, propagating the attentional bias downward. The crucial architectural choice is that *the attentional signal enters only at the top layer*; the bottom layer inherits attentional modulation purely through recurrent feedback.

The model is tested by reproducing classical experimental paradigms: single- vs paired-stimulus presentations within a single RF (Reynolds 1999 / Reynolds & Heeger 2009 biased competition); feature-similarity gain (Treue & Martínez-Trujillo 1999); RF-shift and RF-resize experiments (Womelsdorf et al. 2006, 2008; Anton-Erxleben et al. 2009); feature-space spectral-RF shifts (David et al. 2008). Parameter sensitivity is examined by ±20% perturbations of inhibitory width, attentional-field width, and feedback strength.

The architectural choices that matter most for the user's program are: (a) the *recurrent* equilibrium computation — the network cannot be unrolled into a single feedforward pass without losing the attentional effects; (b) the *multiplicative* form of feedback — replacing $(1 + FB)$ with $FB$ (additive driving) destroys the biased-competition signature; (c) the placement of the attentional signal at the top of the hierarchy with downward propagation, not as input-level modulation; and (d) the use of divisive normalization to convert linear multiplicative bias into nonlinear, context-dependent gain. None of these choices is novel individually — each has antecedents in the normalization-model and biased-competition literatures — but the demonstration that all four together produce the full empirical catalogue is the paper's central contribution.

## 5. Results

The model reproduces all of the following with a single fixed parameter set:

- **Response gain and contrast gain.** Attention produces response-gain effects (multiplicative scaling of the contrast-response curve) when the attended stimulus is exactly within the RF, and contrast-gain effects (leftward shift of the contrast-response curve) when the focus drifts away. This is the model's novel prediction: a smooth, parametric transition between gain types as a function of attention-to-RF eccentricity.
- **Biased competition.** With two competing stimuli within a single top-layer RF, attending to one of them restores the cell's response to a value close to its response when only the attended stimulus is present — a ~±30% modulation of firing rate, consistent with Reynolds 1999.
- **Feature-similarity gain.** Tuning curves sharpen and shift toward the attended orientation: response is enhanced for stimuli close to the attended feature and suppressed for stimuli far from it.
- **Topological RF shifts.** When attention is focused inside the RF, the RF *shrinks* around the focus; when it is focused outside the RF, the RF *expands toward* the focus. Both effects match the Womelsdorf / Anton-Erxleben experimental observations.
- **Feature-space RF shifts.** Applying attention to a particular orientation shifts the cell's *featural* RF toward that orientation, replicating the David et al. 2008 spectral-RF result in V4.
- **Layer asymmetry.** Top-layer modulation reaches ~51% under the focus of attention; bottom-layer modulation is only ~7%. Attention manifests earlier and more strongly in the higher layer, exactly as in the Buffalo et al. 2010 backward-progression result.
- **Parameter robustness.** Qualitative behaviour is preserved under ±20% perturbations of most parameters; the largest sensitivity is to feedback strength (a 20% increase erases the biased-competition signature by saturating feedback gain).
- **Diagnostic for the contribution of each architectural choice.** Ablating recurrence (collapsing to a single forward-backward pass) eliminates RF shifts and biased-competition restoration but preserves crude response-gain modulation; ablating divisive normalization preserves response gain but destroys the response-gain–to–contrast-gain transition the model predicts; ablating top-down feedback entirely (leaving only attentional modulation at the bottom layer) eliminates the layer-asymmetry result and degrades RF-shift magnitude. Each of the four architectural ingredients is therefore separately necessary for a distinct subset of the empirical effects.

## 6. Critique / limitations

The authors themselves flag three limitations. First, the model captures gross temporal dynamics at the level of whole areas (attention rises in V4 before V1) but cannot reproduce fine within-cell temporal effects — e.g., the differential effect of attention on the late vs early phase of a single neuron's response. The 30-iteration equilibrium computation is too coarse for that. Second, the model is silent on noise correlations and synchrony — both of which attention is known to affect (Cohen & Maunsell 2009) — because the units are deterministic. Third, the model omits outside-the-RF surround suppression, treating only within-RF biased competition; this leaves out a substantial fraction of the contextual-modulation literature.

A second-order limitation concerns the *interpretive scope* of the parameter-sensitivity analysis. The ±20% robustness claim is established only for the small handful of free parameters the authors expose (feedback strength, attentional-field width, inhibitory-kernel width). The behaviour of the model under structural perturbations — changing the number of layers, the connectivity sparsity, the form of the nonlinearity, the size of the orientation channel set — is not characterised. The user's program, which scales to 3+ layer hierarchies with learned rather than tied weights, will encounter robustness regimes Miconi & VanRullen 2016 does not address.

A deeper critique, only obliquely engaged by the authors, is the *interpretive* one. Multiplicative top-down feedback into a normalization-equipped recurrent network is, at the level of equations, indistinguishable from a Reynolds–Heeger 2009 normalization-model-of-attention with a recurrent realisation, and indistinguishable from a Spratling 2008 PC/biased-competition formulation under a different label for the same quantities. The paper does not adjudicate which of these theoretical framings (normalization vs biased competition vs predictive coding vs feedback gating in the Gilbert & Li 2013 sense) is "the right one"; it shows that, mechanically, the same recurrent multiplicative-feedback + normalization arithmetic generates the empirically observed effects regardless of which label is applied. From the user's program's perspective this is a feature: the Feedback Transformer's architectural commitment — multiplicative Q/K gating + softmax competition — sits at exactly the intersection of these accounts and inherits the universality.

The model is also explicitly hand-designed rather than learned. The Gabor filters, the attentional field shape, the inhibitory kernel, and the feedforward-equals-feedback weight tying are all imposed structures, not emergent from training. The paper does not establish that an end-to-end-trained network with this architectural prior would converge to similar behaviour — that is the question subsequent deep-learning work (e.g., Lindsay 2020, recurrent ViTs) has had to attack. The feedforward-equals-feedback weight tying in particular is a strong assumption: empirically, descending corticocortical projections from L5/L6 of higher areas and ascending L2/3 projections from lower areas are anatomically and physiologically distinct (Felleman & Van Essen 1991; Weiler et al. 2025), and there is no clear reason their effective synaptic weights should be exact transposes of each other. The model's success despite this simplification is consistent with the user's program treating ascending and descending paths as architecturally distinct (conv vs conv-transpose) but functionally complementary.

The model uses only two layers. The full cortical hierarchy is V1 → V2 → V4 → IT → PFC (Felleman & Van Essen 1991), with attention signals injected from FEF / LIP / PFC. Whether the multiplicative-feedback + normalization construction scales monotonically across 4–6 layers — and how the "diminishing-feedback-into-deeper-layers" regime the user proposes (`the_user_architectural_program.md` §3) would interact with this scaling — is left open.

Finally, the model has nothing to say about what *generates* the top-level attentional field $A_{x,\theta}$. In the paper, $A$ is hand-specified for each experiment; the model assumes that whatever computation in PFC / FEF / LIP produces the field has already happened. The user's program, by contrast, treats the deepest GridCell RNN layer as the *source* of the field — i.e., it endogenises the attention-generation computation. The Miconi & VanRullen result therefore complements rather than competes with the user's program: it characterises what an attentional signal does once it enters the visual hierarchy; the user's program characterises how that signal might emerge from an inter-coalition competition in a deeper layer.

## 7. Connection to our work

This paper is the most direct conceptual ancestor of the *iterate-and-attend* pattern that defines the Recurrent ViT and the broader Feedback-Transformer program.

The paper is doing, in 2016, almost exactly what the user's program is doing now: pointing at a wide class of empirical phenomena and arguing that a single recurrent-with-multiplicative-feedback architectural primitive explains them. The difference is that Miconi & VanRullen restrict themselves to hand-designed two-layer networks with one stimulus type, whereas the user scales the same architectural commitment to many-layer learned networks operating on real images and video. Several specific connections follow.

**(i) Multiplicative feedback is the load-bearing choice.** The Recurrent ViT manuscript (2502.10955, §6.7) reports three variants of memory integration into self-attention — tokens, additive, and multiplicative. Miconi & VanRullen 2016 establish that *multiplicative* (modulatory) feedback, not additive driving feedback, is what recovers cortex-like attentional dynamics. The user's Feedback Transformer formula

$$
\alpha_{ij} \propto \big\langle s_{q,i} \odot \sum_k c^{(k)}_{q,i},\; s_{k,j} \odot \sum_k c^{(k)}_{k,j} \big\rangle
$$

(`the_user_architectural_program.md` §1) uses Hadamard products — multiplicative gating — exactly as Miconi & VanRullen do. The paper supplies the strongest single piece of evidence in the seed that this is the right choice, against the simpler additive-FiLM alternative that PRISM v1 (`THESIS.md` §2.4) and PRISM v2 (`PRISM_V2_PROPOSAL.md` §3.4) currently use.

**(ii) Recurrence is required for adaptive-RF dynamics.** The model's 30-iteration equilibrium computation is not optional: the attentional bias has to propagate from the top layer down through feedback, then back up via feedforward, then redistribute via normalization, multiple times before the bottom-layer RFs settle into their attended-state configurations. A single feedforward pass cannot exhibit RF shifts, RF resizings, or biased-competition modulation of this kind. This is the cleanest computational version of the *recurrence-for-temporal-dynamics* commitment that kietzmann2019_recurrence_required documents in primate cortex and that the Recurrent ViT instantiates at the patch level. The paper supplies the missing link between Kietzmann's "recurrence is empirically necessary" and the user's "recurrent self-attention is the right computational primitive."

A practical consequence: any single-pass attention mechanism — including a vanilla ViT, a CNN with a single attention block, or a feedforward FiLM-modulated network — is by construction unable to exhibit the equilibrium-time phenomena Miconi & VanRullen demonstrate. The Recurrent ViT is the smallest modification that lifts this restriction, and the user's program scales the same modification to multi-hub, multi-timescale, multi-resolution memory hierarchies. This paper is the cleanest single reference establishing why the lift matters.

**(iii) Feedback enters at the top, propagates downward — and the architectural consequences of that.** A subtle but important commitment of the Miconi & VanRullen model is that the attentional control signal $A_{x,\theta}$ enters *only at the top layer*. The bottom layer's attentional modulation is purely a consequence of feedback. This is the canonical cortical control-signal-injection pattern (FEF / LIP projecting to extrastriate, which then projects back to V1) and it is the pattern the user's hierarchical GridCell stack implements: the deepest layer has the most stable, most abstract internal state with the fewest external feedback inputs, and propagates its bias downward via descending conv projections (`the_user_architectural_program.md` §3 "diminishing feedback into deeper layers"). Miconi & VanRullen show this architecture is sufficient to recover the *empirical phenomena* Gilbert & Li 2013 catalogue.

**(iv) Normalization + multiplicative gating is the right substrate for self-attention.** The paper's key arithmetic insight is that *multiplicative gating combined with divisive normalization* turns a simple top-down bias into the full repertoire of context-dependent attentional effects. The transformer softmax is itself a form of divisive normalization (each token's attention weight is its exponentiated similarity divided by the sum of exponentiated similarities over all tokens). The Feedback Transformer's combination of Hadamard-product Q/K modulation with softmax over tokens is therefore the *direct architectural analog* of Miconi & VanRullen's multiplicative-feedback-plus-divisive-normalization construction, transplanted from cortical column space into transformer token space. This is, in retrospect, the single most important architectural reading of the user's program: the Feedback Transformer is the canonical-microcircuit normalisation-and-gating computation expressed as a self-attention operation.

Concretely, the user's hierarchical GridCell stack maps cleanly onto a multi-layer extension of Miconi & VanRullen's two-layer construction: Layer 1 ≡ V1-equivalent (bottom layer in the paper); Layer 2 ≡ V4/MT-equivalent (top layer in the paper); Layer 3 ≡ a further-abstracted PFC/FEF-equivalent where the attentional field is *generated*, not specified. The paper does not implement Layer 3 — its attentional field is exogenous — but the user's program does, and the multi-hub competition for control of the central self-attention map (`the_user_architectural_program.md` §5) is the proposal for how that generation might emerge from learning rather than being hand-coded.

**(v) Direct lineage to dosovitskiy2020_vit.** The ViT is the *non-recurrent, feedforward* version of the architecture the Miconi & VanRullen model demonstrates is empirically incomplete. A vanilla ViT can produce response-gain modulation by training on attended-stimulus tasks; it cannot exhibit RF shifts, RF resizings, contrast-gain transitions, or biased-competition restoration of suppressed responses, because all of these phenomena are *equilibrium-time* phenomena that require iterative recurrence. The Recurrent ViT is the minimal modification to the ViT that adds this iterative dimension. Miconi & VanRullen 2016 is the model that demonstrates why the modification is necessary.

There is also a *historical* lineage worth marking. The 2016 paper sits chronologically and conceptually between Reynolds & Heeger 2009 (the canonical normalization model of attention, which Miconi & VanRullen explicitly extend) and the modern recurrent-DNN literature on attention (Lindsay 2020 review; Kietzmann et al. 2019). The 2016 paper is the bridge: it takes the Reynolds–Heeger arithmetic and shows it works in a *recurrent two-layer network* rather than in a one-shot computation over a single cell's inputs. The Recurrent ViT line, in turn, takes this recurrent-network commitment and scales it to learned transformer architectures over image patches. The architectural primitive — multiplicative gating + softmax/normalization, applied iteratively over a feedback-coupled hierarchy — is preserved across the entire chain.

**(vi) Predictive-coding bridging.** The paper does not commit to a PC interpretation, but its arithmetic is compatible with one. Bastos et al. 2012 propose a laminar PC microcircuit in which superficial-layer prediction errors propagate upward and deep-layer predictions propagate downward as multiplicative gain modulations — which is exactly the Miconi & VanRullen connectivity pattern with PC labels attached. keller_mrsic_flogel2018_pc_review documents the same arithmetic at the mouse-V1 circuit level. The user's `competition-emergent-predictive-coding` thesis (`the_user_architectural_program.md` §5) inherits this multiplicative-gating commitment and extends it from sensory PC to inter-coalition PC. Miconi & VanRullen 2016 is thus a key node in the chain: Reynolds–Heeger normalization → Miconi–VanRullen recurrent multiplicative feedback → Bastos laminar PC → user's competition-emergent PC.

There is one further bridging connection worth flagging explicitly. Spratling 2008 (already in seed; `spratling2008_pc_biased_competition`) showed that biased competition and predictive coding are *mathematically equivalent* under the right change of variables — the same dynamics can be relabelled as either a PC inference loop or a biased-competition winner-take-all process. Miconi & VanRullen 2016 is the implementation that exhibits both labels simultaneously: from the biased-competition direction, it reproduces Reynolds 1999; from the PC direction, it implements multiplicative top-down modulation of feedforward drive. The Feedback Transformer inherits this dual-labelling property by construction.

**(vii) Possible link to boshra_kastner2022 rhythmic-attention sampling.** VanRullen is independently known for rhythmic / theta-sampling models of attention. This particular paper does not engage that line, but its 30-iteration equilibrium structure is in principle compatible with a periodic-sampling overlay: the equilibrium could be reset on a theta-rhythm cycle, with each cycle producing a fresh allocation of multiplicative feedback. The user's program does not currently include an explicit rhythmic component, but if it adds one — for change-detection over event-segmented video, for example — the Miconi–VanRullen + theta-sampling combination would be the natural starting point. boshra_kastner2022_attention_control supplies the theta-sampling empirical anchor for that extension.

The user's program does not currently include an explicit rhythmic component, but the architectural ingredients are already there: the iterate-and-attend loop in the Recurrent ViT and the $n_{FR} \to n_{BR}$ schedule in the iterative-variational encoder–decoder both impose a discrete-time clock on the network's computation. Adding a theta-frequency reset of the attentional field — or, equivalently, periodically refreshing the deepest GridCell RNN's external input — would map the Miconi & VanRullen equilibrium-attention computation onto the VanRullen-style rhythmic-sampling theory, and supply a natural extension for event-segmented video.

**(viii) Specific architectural implications for the Recurrent ViT and PRISM v2.** Three concrete design transfers follow. First, the multiplicative-feedback variant in 2502.10955 §6.7 should be reported with single-stimulus *and* paired-stimulus task variants, because Miconi & VanRullen show the most diagnostic attentional signatures emerge under within-RF competition. The current change-detection benchmark only weakly probes this. Second, PRISM v2's hierarchical-FiLM should be re-examined as an approximation to the full multiplicative gating in this paper: FiLM applies $\gamma \cdot x + \beta$, but Miconi & VanRullen's gating is $(1 + FB) \cdot x$ — i.e., a pure multiplicative scale with no additive bias. The additive $\beta$ component of FiLM may dilute the cortex-like RF dynamics this paper demonstrates. Third, the equilibrium-time perspective suggests reporting Recurrent ViT performance as a function of iteration count — not just final accuracy but per-iteration accuracy curves — so the iterate-and-attend dynamics can be compared directly to the time-course Miconi & VanRullen report.

A fourth, more speculative transfer: the model's clean prediction that response-gain transitions to contrast-gain as a function of attention-to-RF eccentricity is a *quantitative* signature that a learned multi-head self-attention module could in principle be tested for. If the user's Feedback Transformer is doing what Miconi & VanRullen claim multiplicative-feedback-plus-normalization does, then sweeping the spatial focus of a query-injected attentional bias across the visual field should produce an analogous transition in the patch-level token responses — a falsifiable empirical handle on whether the architectural analogy is real or merely conceptual.

**(ix) What this paper does *not* license.** The model is hand-designed. It does not establish that a learned multiplicative-feedback network will discover this same architecture from data; that question belongs to the deep-learning literature (Lindsay; Kietzmann; recurrent ViTs). It also does not address temporal-sequence input — every result is for a single static image at equilibrium, so the extension to video (the user's primary domain) requires additional commitments about how the equilibrium reset between frames. The user's program treats the architectural commitment as a *prior* and asks gradient descent to fill in the parameters within it. Miconi & VanRullen 2016 justifies the prior; the Recurrent ViT and PRISM lines test whether learning under it scales.

**(x) Summary of the architectural lesson.** The clearest one-sentence summary of what this paper teaches the user's program is: *recurrent multiplicative feedback into a normalization-equipped hierarchy is a single architectural primitive that generates the entire empirical catalogue of single-cell attentional effects.* Every other paper in the program — Gilbert & Li 2013 (the empirical catalogue), Bastos 2012 (the laminar microcircuit), Keller & Mrsic-Flogel 2018 (the PC interpretation), Kietzmann 2019 (recurrence-is-required), Dosovitskiy 2020 (the feedforward ViT baseline) — sits as a complement to this central computational result. The Recurrent ViT, the Feedback Transformer, and the multi-hub competition architecture are then the natural next steps: scale the same primitive to learned, many-layer, video-capable, multi-objective systems.

## 8. Citations to follow

- `reynolds_chelazzi2004_attentional_modulation` — already in seed; the broader review of attentional modulation in extrastriate cortex this paper's results bear on most directly. (Confirm in `related:`.)
- `lindsay2020_attention_dnn_review` — Lindsay's review of attention mechanisms in DNNs, the direct deep-learning descendant of this paper's modelling line. Not yet in seed.
- `buffalo2010_backward_progression` — single-unit demonstration that attention propagates backward through the ventral stream (V4 → V2 → V1), the empirical anchor for this model's top-down-injection architecture. Not yet in seed.
- `gregoriou2009_fef_v4_coupling` — FEF–V4 gamma coherence during attention, supplying the top-down control-signal anatomy. Not yet in seed.
- `womelsdorf2006_attention_rf_shift_mt` — single-unit demonstration of attentional RF shifts in MT, replicated by this model. Not yet in seed.
- `anton_erxleben2009_attention_rf_shape` — attentional reshaping of RF structure in V4, replicated by this model. Not yet in seed.
- `treue_martinez_trujillo1999_feature_similarity_gain` — origin of the feature-similarity-gain principle the model reproduces. Not yet in seed.
- `david2008_v4_spectral_rf_shift` — feature-space spectral-RF shifts in V4 under feature-based attention, replicated by this model. Not yet in seed.
- `carandini_heeger2011_normalization_canonical` — normalization as a canonical neural computation, the broader theoretical home of this paper's arithmetic. Not yet in seed.
- `cohen_maunsell2009_correlations` — already in seed; noise-correlation effects of attention that this model explicitly cannot capture.
- `lamme_roelfsema2000_distinct_feedforward_feedback` — the cleanest separation of feedforward vs feedback contributions; the conceptual frame for this model's two-layer construction. Not yet in seed.
- `lindsay2020_attention_dnn_review` — direct deep-learning descendant survey of attention mechanisms in neural networks; would situate Miconi & VanRullen in the broader DNN-attention landscape. Not yet in seed.
- `mcadams_maunsell1999_attention_v4` — the classical multiplicative-gain demonstration that this model's response-gain prediction is anchored on. Not yet in seed.
