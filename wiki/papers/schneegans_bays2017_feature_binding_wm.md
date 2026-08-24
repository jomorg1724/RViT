---
id: schneegans_bays2017_feature_binding_wm
title: "Neural architecture for feature binding in visual working memory"
authors:
  - "Schneegans, Sebastian"
  - "Bays, Paul M."
year: 2017
venue: "Journal of Neuroscience"
doi: "10.1523/JNEUROSCI.3493-16.2017"
arxiv: ""
url: "https://doi.org/10.1523/JNEUROSCI.3493-16.2017"
tags:
  - working-memory
  - primate-neurophysiology
  - psychophysics
concepts:
  - feature-binding
  - working-memory-persistent-activity
  - topographic-organization
  - retinotopy
related:
  - bays2024_wm_representation
  - luck_vogel1997_wm_capacity
  - wheeler_treisman2002_binding
  - pertzov_husain2014_location_wm
  - treisman_gelade1980_feature_integration
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_122
status: full
depth: full
last_updated: "2026-05-14"
---

# Neural architecture for feature binding in visual working memory

## 1. Abstract

A fundamental challenge for visual working memory (VWM) is the *binding problem*: when multiple objects are remembered, how are the features of each object (e.g. color, orientation) kept associated with one another rather than confused across objects? Schneegans & Bays develop a neural-population model in which feature binding is achieved through *shared retinotopic location*. Two feature-specific neural population codes (e.g. for color and orientation) are each conjunctively coded with a population code for *spatial location*, and binding between non-spatial features is read out *via* their common location. The model is implemented as a set of dynamic neural fields with biologically motivated lateral excitation / global inhibition. It reproduces the principal behavioral signatures of VWM — set-size-dependent precision decreases, the prevalence of *swap errors* (misbinding), and the asymmetry between location-cued and feature-cued report — and predicts that binding errors are systematically larger between nearby items than between distant ones. The architecture supplies a concrete neural mechanism by which a continuous-resource WM system also solves the binding problem.

## 2. Why this matters for us

The paper supplies the *binding* component that the Bays continuous-resource framework ([bays2024_wm_representation](research_db/papers/bays2024_wm_representation.md)) leaves underspecified. It commits to a specific architectural claim — *spatial location is the common substrate that binds non-spatial features* — that maps directly onto the user's program. In the recurrent ViT, each token is identified by its patch position; feature channels at that position constitute the bound representation. In PRISM v1/v2, the recurrent memory's spatial grid plays the same role: features held at the same grid location are bound. In the user's GridCell RNN, the *grid itself is the binding substrate*. Schneegans & Bays gives the neuroscientific warrant for this architectural commitment, and at the same time predicts a specific failure mode (swap errors increasing with spatial proximity) that the user's architectures should exhibit if they implement the same mechanism.

## 3. Key claims

1. **Binding through shared location.** Non-spatial features are bound to one another not directly, but *indirectly* via their common conjunction with spatial location. Color-orientation binding is mediated by color-location and orientation-location conjunctive codes.
2. **Conjunctive population coding.** Each feature dimension is jointly coded with location in a 2D neural population (location × feature), implemented as a dynamic neural field with localized excitation and global inhibition.
3. **Continuous resource via shared dynamics.** Capacity limits emerge from divisive competition within the field: each additional item lowers the steady-state activity available to every other item, producing the graded precision-loss-with-set-size signature without slots.
4. **Swap errors are mislocalization errors.** When location is recalled imprecisely at retrieval, the read-out queries the wrong column of the (location × feature) field, returning *another item's* feature rather than the target's. Swap errors are not a separate process — they fall out of location-mediated binding.
5. **Asymmetric cueing.** Cueing by *location* is more accurate than cueing by a non-spatial feature: location is the *retrieval key*, so location-cued report reads directly from the bound representation, whereas feature-cued report must first invert through location.
6. **Proximity predicts swaps.** Because location is coded with finite precision, swap errors between items are graded by spatial proximity — nearby items are more likely to be misbound than distant ones. This is a falsifiable prediction of the architecture.
7. **No item-level slots.** The model contains no discrete object files. Binding, capacity, and identity all emerge from the population-coded field dynamics.

## 4. Methods

The model is implemented as a system of *dynamic neural fields* (DNFs) — continuous-attractor neural populations with localized lateral excitation and global / surround inhibition, evolving by the Amari field equation
$$
\tau \dot{u}(x,t) = -u(x,t) + h + s(x,t) + \int w(x - x') f(u(x',t)) \, dx'
$$
where $u$ is the membrane-potential field, $h$ the resting level, $s$ the external input, $w$ a Mexican-hat-shaped lateral kernel, and $f$ a sigmoidal firing-rate function. The field equation is well-studied (Amari 1977) and supports localized self-sustaining "bump" attractors when the inhibition strength is in the appropriate regime.

Architecturally:

- **One conjunctive field per feature dimension.** Color is coded as a 2D field over (location × color); orientation as a 2D field over (location × orientation). Each item produces a bump of activity at its (location, feature) coordinate. The location axis is itself a 2D retinotopic manifold, so each conjunctive field is in principle 3D (two location dimensions plus one feature dimension); for tractability the paper uses a 1D location axis matched to the experimental display geometry.
- **Encoding.** When a multi-item display is presented, each item activates a bump in each conjunctive field at its location × feature coordinate; lateral inhibition forces the bumps to compete for total activation, lowering each bump's amplitude as set size grows. The competition is *non-selective* — adding any item degrades all items, which is the architectural origin of the continuous-resource signature.
- **Maintenance.** After stimulus offset, the bumps are sustained by self-recurrent excitation in each field. Noise diffuses the bumps along both axes, producing the continuous-report variability that grows with delay. Bump amplitude can also collapse below threshold under sufficient competition, producing genuine "guess" responses when an item is effectively lost.
- **Retrieval (feature-cued).** Given a probe feature (e.g. a specific color), the model identifies the location coordinate at which the color field is most active near the probed value, then reads out the orientation field at that location. This two-step inversion introduces extra noise from the location-decoding step.
- **Retrieval (location-cued).** Given a probe location, the model reads out the feature field directly at that location — a more direct readout that avoids the cross-field inversion and is therefore less noisy.

The model is fit to continuous-report behavioral data from human experiments (the Bays-lab color-orientation paradigm) using a small number of biophysical parameters (kernel widths, inhibition strength, noise amplitude). Performance is quantified by fitting *mixture models* to the response distributions (target, swap, uniform-guess components, after Bays-Catalao-Husain 2009) and comparing the mixture parameters predicted by the DNF to those observed in human data. Model parameters are held fixed across set sizes — the set-size effects are emergent properties of the field competition, not free fits per condition.

## 5. Results

The model reproduces all principal signatures of the binding literature:

- **Precision decreases with set size.** As set size increases from 1 to 6 items, the standard deviation of target-centered responses grows monotonically; the DNF matches the human pattern (precision $\sim$ set-size$^{-\alpha}$) without item-level slots.
- **Swap-error rate increases with set size.** The fraction of non-target ("swap") responses grows with set size in both data and model. The model predicts swap rates of order 5–20% across the tested set sizes, matching the empirical range.
- **Swaps are graded by spatial proximity.** When non-target probabilities are plotted as a function of the distance between probe and non-target items, both data and model show that closer non-targets are more likely to be reported. This is the architecture's distinctive prediction and it is empirically confirmed.
- **Location cueing is more accurate than feature cueing.** Conditioned on equal stimulus information, location-cued precision exceeds feature-cued precision; the model reproduces this asymmetry from the asymmetric retrieval routes.
- **Binding errors scale with location precision.** As the location code is made noisier (parameter sweep), the swap-error rate rises monotonically — a direct prediction that misbinding *is* mislocalization.
- **Quantitative fits.** The full mixture-model parameters (target SD, swap rate, guess rate) across set sizes are fit by a small set of DNF parameters; the model accounts for the majority of variance in the human response distributions.

## 6. Critique / limitations

The model commits to *spatial location as the unique binding substrate*. This is a strong claim and is contested. Wheeler & Treisman 2002 ([wheeler_treisman2002_binding](research_db/papers/wheeler_treisman2002_binding.md)) and others argue that binding can be observed in conditions where location is not informative; the Schneegans & Bays model would predict no successful binding in those conditions. The empirical record on whether non-spatial binding exists at all is mixed.

The model is fit to *two-feature* tasks (color + orientation). Generalization to three or more features per object — and whether all features are bound pairwise via location, or whether a more elaborate object-file mechanism is needed — is left as future work.

The DNF implementation does not address *temporal* binding (binding by synchronous activity, as in the binding-by-synchrony tradition of Singer / von der Malsburg). The architecture is silent on whether oscillations or synchrony play any role; binding here is *structural*, by shared spatial coordinate.

The model uses hand-tuned biophysical parameters rather than learned ones. There is no learning rule; the parameters are fit. Whether the same architecture could emerge from a learning objective is not addressed.

Set sizes above 6 are not tested empirically. The model's prediction at very large set sizes (where the literature is sparse) is therefore an extrapolation.

The discrete-slot tradition (Luck-Vogel; [luck_vogel1997_wm_capacity](research_db/papers/luck_vogel1997_wm_capacity.md)) would argue that the apparent continuous-precision-decrease pattern actually reflects discrete drop-out plus high-precision storage. Schneegans & Bays do not directly adjudicate this — the model is committed to the continuous interpretation but the fit alone does not exclude slot-and-averaging accounts.

The neural realization remains schematic. The model identifies the conjunctive (location × feature) field with parietal / extrastriate populations that show location-tuned feature selectivity, but a direct cortical mapping (which area implements which conjunctive field, what the projection structure is) is not pinned down. The model is best understood as a *computational-level* commitment with biologically motivated dynamics rather than a circuit-level proposal.

## 7. Connection to our work

This paper is one of the most architecturally consequential entries in the database for the user's program: it specifies a *neural* mechanism for feature binding that maps almost directly onto the recurrent ViT, PRISM, and the user's GridCell RNN.

**Spatial grid as binding substrate (recurrent ViT and PRISM).** In the recurrent ViT, each patch token is identified by its spatial position; feature channels at that token are bound by virtue of co-occupying the same token slot. This is the exact architectural form of Schneegans & Bays's "binding through shared retinotopic location." The recurrent ViT's patch grid *is* the location dimension of their conjunctive (location × feature) field. PRISM v1's spatial memory $M_t$ ([THESIS.md](Prism/docs/THESIS.md) §2.3) plays the same role: features at the same memory-grid cell are bound. The paper supplies the neuroscientific warrant for this architectural commitment, which is otherwise implicit.

**GridCell RNN as the full Schneegans-Bays architecture.** The user's [gridcell-rnn](research_db/concepts/gridcell_rnn.md) primitive maintains an internal grid of recurrent states $C_i^{(t)} \in \mathbb{R}^{n_{gh} \times n_{gw} \times n_{C_i}}$ in which each grid cell holds a feature vector — i.e. each location holds its bound non-spatial features. This is *structurally* the conjunctive (location × feature) population of Schneegans & Bays, but vectorized across feature channels and dynamically updated by gated recurrence rather than DNF dynamics. The user's architecture and Schneegans & Bays's model are alternative implementations of the same computational commitment: *location is the retrieval key for bound feature content*.

**Swap-error prediction as a benchmark.** The architecture's distinctive prediction — that misbinding is mislocalization, and that swap rates are graded by spatial proximity — translates directly to a testable prediction about the recurrent ViT and PRISM. If those architectures, when scaled to multi-item change-detection tasks, exhibit swap-error patterns that scale with patch-grid proximity rather than with feature similarity, that is direct evidence that they implement Schneegans-Bays-style binding. This is a natural follow-up experiment to the published recurrent ViT result (2502.10955), which uses ≤4 stimuli and does not analyze swap structure explicitly.

**Continuous-resource binding (consistency with Bays 2024).** The model is the natural complement to [bays2024_wm_representation](research_db/papers/bays2024_wm_representation.md): Bays et al. 2024 give the contemporary continuous-resource framework; Schneegans & Bays 2017 supply the binding mechanism within that framework. Together they form the contemporary "continuous, location-bound, precision-allocating" account of VWM that the user's architectures most closely instantiate.

**Tension with discrete object files.** The model has no item-level slots — there is no "object file" or "item index" anywhere in the architecture. This matches the recurrent ViT and PRISM, which also have no slot-like data structure. It contrasts with slot-attention-style approaches (Locatello et al.), where objects are explicit slots; this is a load-bearing architectural divergence to flag in any future publication that compares the user's program to slot-attention.

**Implications for the Feedback Transformer.** Within the user's [feedback-transformer](research_db/concepts/feedback_transformer.md) primitive, the per-position Q/K/V projections from each recurrent state implement *exactly* the Schneegans-Bays read-out: a probe at one position queries all feedback sources at that position, retrieving the bound feature content. This is a satisfying convergence — the Feedback Transformer's per-position structure is *the* architectural form of location-mediated binding.

## 8. Citations to follow

- `bays_husain2008_dynamic_shifts_visual_wm` — the Bays continuous-resource foundational paper; the empirical base this model fits. Not yet in seed.
- `bays_catalao_husain2009_precision_wm` — color-orientation binding behavioral paradigm that this model targets. Not yet in seed.
- `treisman_gelade1980_feature_integration` — feature-integration theory, the classical attentional-binding antagonist. In seed.
- `wheeler_treisman2002_binding` — the alternative "binding without location" position; the principal empirical challenger. In seed.
- `pertzov_husain2014_location_wm` — location precision in VWM; direct empirical complement. In seed.
- `singer1995_binding_by_synchrony` — the temporal-binding-by-synchrony tradition the model is silent on. Not yet in seed.
- `amari1977_dynamic_neural_fields` — the DNF formalism the model uses. Not yet in seed.
- `johnson_spencer_schoner2009_dnf_wm` — DNF accounts of WM that predate this model. Not yet in seed.
- `swan_wyble2014_binding_pool` — alternative binding-pool model. Not yet in seed.
- `oberauer_lin2017_interference_model` — interference-based account of binding. Not yet in seed.
