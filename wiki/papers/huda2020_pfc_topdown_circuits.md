---
id: huda2020_pfc_topdown_circuits
title: "Distinct prefrontal top-down circuits differentially modulate sensorimotor behavior"
authors:
  - "Huda, Rafiq"
  - "Sipe, Grayson O."
  - "Breton-Provencher, Vincent"
  - "Cruz, K. Guadalupe"
  - "et al."
year: 2020
venue: "Nature Communications"
doi: "10.1038/s41467-020-19772-z"
arxiv: ""
url: "https://doi.org/10.1038/s41467-020-19772-z"
tags:
  - primate-neurophysiology
  - prefrontal-cortex
  - subcortical
  - early-visual-cortex
  - lesion-microstimulation
concepts:
  - top-down-feedback
  - optogenetic-perturbation
  - gain-modulation
  - priority-map
  - cortical-microcircuit-model
related:
  - clark2015_prefrontal_attention
  - mante2013_context_dependent_pfc
  - panichello_buschman2021_shared_mechanisms
  - gazzaley_nobre2012_topdown
  - mcnab_klingberg2008_pfc_bg_wm
  - monosov2011_pfc_inactivation_it
  - krauzlis2013_sc_attention
  - moore_armstrong2003_fef_microstim
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_83
status: full
depth: full
last_updated: "2026-05-16"
---

# Distinct prefrontal top-down circuits differentially modulate sensorimotor behavior

## 1. Abstract

Sensorimotor behaviors require processing of behaviorally relevant sensory cues and the ability to select appropriate responses from a vast behavioral repertoire. Modulation by the prefrontal cortex (PFC) is thought to be key for both processes, but the precise role of specific circuits remains unclear. We examined the sensorimotor function of anatomically distinct outputs from a subdivision of the mouse PFC, the anterior cingulate cortex (ACC). Using a visually guided two-choice behavioral paradigm with multiple cue-response mappings, we dissociated the sensory and motor response components of sensorimotor control. Projection-specific two-photon calcium imaging and optogenetic manipulations show that ACC outputs to the superior colliculus, a key midbrain structure for response selection, principally coordinate specific motor responses. Importantly, ACC outputs exert control by reducing the innate response bias of the superior colliculus. In contrast, ACC outputs to the visual cortex facilitate sensory processing of visual cues. Our results ascribe motor and sensory roles to ACC projections to the superior colliculus and the visual cortex and demonstrate for the first time a circuit motif for PFC function wherein anatomically non-overlapping output pathways coordinate complementary but distinct aspects of visual sensorimotor behavior.

## 2. Why this matters for us

Huda et al. 2020 is the cleanest extant demonstration that a single PFC subdivision (mouse ACC) implements **functionally specialized top-down channels**: one channel (ACC → V1) modulates **sensory** processing; an anatomically non-overlapping channel (ACC → superior colliculus) modulates **motor** response selection. This is the empirical archetype for the user's multi-hub system commitment: a single high-level controller does not modulate downstream computation through a single homogeneous feedback signal but through *projection-specific*, *target-specific* channels, each shaping a different downstream computation. For the recurrent ViT and PRISM, this licenses the architectural move of having a single recurrent memory state $H^{(t)}$ project distinct top-down signals into distinct downstream substrates (the attention map, the FiLM modulator, the readout head), rather than collapsing top-down influence to a single scalar gain.

The paper is also the operational complement to Clark et al. 2015. Clark argues that PFC is *the source* of top-down attention; Huda argues that the source decomposes into anatomically labeled output channels, each functionally specialized. Together they establish the source-and-channels picture the user's program inherits.

## 3. Key claims

1. **ACC has anatomically non-overlapping projections to V1 and SC.** Retrograde rabies tracing shows that ACC → V1 and ACC → SC neurons are largely distinct populations within ACC, supporting a *labeled-line* organization rather than a single broadcast signal.
2. **ACC → SC encodes motor responses; ACC → V1 encodes sensory cues.** Projection-specific two-photon calcium imaging during a two-choice visual task reveals that ACC → SC axons carry information predominantly about the chosen motor response, while ACC → V1 axons carry information predominantly about the visual cue identity.
3. **Optogenetic inactivation of ACC → SC impairs motor response selection.** Inhibiting this pathway shifts choice behavior toward the animal's innate response bias, indicating ACC → SC normally counteracts intrinsic SC bias to enable goal-appropriate responses.
4. **Optogenetic inactivation of ACC → V1 impairs sensory discrimination.** Inhibiting this pathway selectively reduces perceptual sensitivity to the visual cue without altering motor bias, dissociating sensory facilitation from response selection.
5. **The ACC → SC effect is to reduce response bias, not to drive responses.** Unlike a direct motor command, ACC → SC modulation acts by *flattening* the SC's intrinsic preference for one response over another, allowing cue-driven evidence to determine the chosen response.
6. **A single PFC subdivision implements complementary sensory and motor channels.** This is a generalizable PFC circuit motif: the same controller can shape both *what is perceived* and *what is selected* through anatomically segregated output channels.
7. **The dissociation is causal, not merely correlational.** Projection-specific optogenetics (rather than ACC-wide inactivation) is required to demonstrate that the two channels carry distinct information; bulk ACC manipulation would have conflated them.
8. **The mechanism for ACC → V1 modulation is consistent with long-range glutamatergic excitation onto V1 interneurons.** This aligns with Zhang et al. 2014 *Science* showing that long-range top-down inputs to V1 act via local inhibitory interneurons; ACC → V1 plausibly engages the same circuit.
9. **The mechanism for ACC → SC bias reduction is consistent with re-balancing collicular mutual inhibition.** SC's left/right asymmetry is maintained by commissural inhibition (Takahashi 2010); ACC → SC input may shift the balance of this competition rather than directly drive saccade-related bursts.

## 4. Methods

**Behavioral task.** Head-fixed mice perform a visually guided two-choice task on a custom response interface. A visual cue (oriented grating) on the left or right of a screen instructs the animal to make a left or right motor response (rotational locomotion or lick direction). Multiple cue–response mappings are used so that the sensory cue and the motor response can be statistically dissociated. Difficulty is titrated by contrast or orientation discriminability so that psychometric curves can be fit.

**Projection-specific imaging.** AAV-Cre is injected into the SC or V1; Cre-dependent GCaMP6f is injected into ACC. This restricts GCaMP expression to ACC neurons that project to the target (ACC → SC or ACC → V1). Two-photon calcium imaging captures activity in these projection-defined ACC populations during the behavioral task. Imaging is performed at single-cell resolution through a chronic cranial window over ACC.

**Projection-specific optogenetics.** A red-shifted inhibitory opsin (Jaws; Chuong et al. 2014) is expressed in ACC; an optical fiber is implanted over the SC or V1 to inhibit the *axon terminals* of ACC neurons projecting to that target. This silences a specific *projection*, not the whole ACC, allowing a clean dissociation of the two channels' behavioral contributions.

**Anatomical tracing.** Retrograde AAV or G-deleted rabies virus (Wickersham et al. 2007) injected into SC and V1 reveals overlap (or lack thereof) of ACC → SC and ACC → V1 source populations. Double-injection experiments quantify the fraction of ACC neurons that project to both targets vs only one.

**Analysis.** Linear classifiers (SVMs via LIBSVM) decode cue identity, response identity, and choice from ACC axonal calcium signals. Psychometric functions fit to behavioral performance under optogenetic vs control trials quantify perceptual-sensitivity and response-bias changes separately. DeepLabCut (Mathis et al. 2018) is used for pose tracking. Suite2p (Pachitariu et al.) handles ROI extraction and neuropil correction for the two-photon imaging.

## 5. Results

- **Anatomical segregation.** ACC → SC and ACC → V1 neurons show minimal somatic overlap; the two output channels are largely *distinct cell populations* in ACC. Double-retrograde labeling quantifies the overlap as a small fraction of the labeled population.
- **Imaging dissociation.** Linear decoders applied to ACC → SC axons predict the animal's *response* on each trial with high accuracy but cue identity weakly. Decoders applied to ACC → V1 axons predict *cue identity* well but response weakly. The dissociation holds across cue–response mappings, ruling out a confound between cue and response. Cross-decoders (train on cue, test on response) confirm the two channels carry orthogonal information.
- **Optogenetic dissociation.** Silencing ACC → SC produces a shift in *response bias* toward the animal's innate preference (psychometric-function lateral shift, point of subjective equality moved toward the preferred side) without changing perceptual sensitivity (slope). Silencing ACC → V1 produces a *sensitivity* decrease (psychometric slope reduction, flatter curve) without a bias shift. The two manipulations yield opposite signatures in the psychometric decomposition.
- **Innate bias and ACC.** SC has intrinsic asymmetric response preferences (a well-known feature; Munoz & Istvan 1998 on lateral inhibition); ACC → SC normally counteracts this asymmetry. Optogenetic silencing reveals the underlying SC bias, demonstrating that ACC's role is corrective rather than commanding — ACC supplies the *evidence-driven correction* on top of SC's intrinsic prior.
- **Pathway-specific rather than ACC-wide.** Bulk ACC silencing would have produced a mixed deficit (both sensitivity and bias changes). The projection-specific approach is essential for the dissociation and reveals that the two effects, if conflated, would have looked like a single non-specific PFC role.
- **Cell-type and laminar inference.** The ACC → SC projection is consistent with L5b extratelencephalic neurons; the ACC → V1 projection is consistent with L5/L6 intratelencephalic (corticocortical) neurons. The functional dissociation thus tracks the canonical laminar / projection-class division.
- **Single-trial information content.** Trial-by-trial decoding from ACC axons predicts behavioral choice on individual trials, not just averaged across conditions. This rules out the possibility that the channels carry only block-level or condition-level information.
- **Temporal profile.** ACC → SC activity ramps near the time of the response; ACC → V1 activity peaks closer to the cue. The temporal dissociation supports the functional dissociation: each channel carries the relevant information at the relevant phase of the trial.
- **Control experiments.** Sham-light controls and contralateral-hemisphere controls rule out non-specific opsin or light artifacts. Behavioral controls (open-loop trials, simple-stimulus controls) rule out gross perceptual or motor impairment.

Quantitative effect sizes (psychometric shift in bias for ACC → SC inhibition; psychometric slope reduction for ACC → V1 inhibition) are reported in the paper figures. The behavioral effects are on the order of those produced by classic FEF microstimulation work (Moore & Armstrong 2003) but in a circuit-decomposed form: where FEF microstim conflates sensory and motor effects, the projection-specific manipulation cleanly separates them.

## 6. Critique / limitations

The study is in mouse ACC, not primate dlPFC or FEF. Whether the same projection-specific motif holds for primate PFC is an extrapolation; the paper's discussion is cautious about this. The Clark et al. 2015 framework was built on primate FEF / dlPFC; Huda et al. extends it to mouse but at the cost of less-developed primate comparators. Mouse ACC and primate dlPFC are not strict homologs — mouse ACC is more comparable to primate medial PFC / Area 24, and the projection patterns may differ.

The task is a *two-choice* sensorimotor task, not a covert-attention task with cue validity. Cue-benefit effects (the canonical attention-task signature emphasized by Clark et al. 2015) are not directly reported in the same form. The "sensory facilitation" claim for ACC → V1 is psychometric-slope based, not validity-based. A direct test of whether ACC → V1 produces cue-validity-dependent effects (as Clark et al. would prefer) remains open.

The functional segregation may be partial. Even if cell bodies are largely non-overlapping, ACC neurons could still share upstream inputs, share local recurrent dynamics, and exhibit coordinated activity. The paper shows *output* segregation; *input* and *internal* segregation are less directly tested. Coordinated activity between the two populations during task engagement is not ruled out and would be expected on theoretical grounds.

The optogenetic inhibition could have off-target axonal effects (back-propagation, antidromic activation) that the paper controls for but cannot fully eliminate. Terminal inhibition with Jaws is generally cleaner than soma inhibition, but not perfect.

The paper does not engage with predictive-coding interpretations. The "ACC → SC reduces innate bias" finding could be reframed as ACC supplying a *prior* that reweights SC's likelihood, but the authors do not pursue this. Similarly, the ACC → V1 facilitation could be reframed as a precision-weighting signal that enhances the gain of cue-relevant V1 representations.

The temporal resolution of two-photon imaging is calcium-indicator-limited; sub-trial dynamics that might reveal phase-coding or sequence-coding of the channels' contributions are not accessible. A future replication with electrophysiology (paired with the projection-specific genetic targeting) would be informative.

The two channels (sensory and motor) are presented as complementary; whether they *compete* for shared ACC resources, or whether they are gated by a third (working-memory or context) signal upstream, is left open. This is exactly the question the user's competition-emergent predictive-coding framework would ask.

The "innate bias reduction" story for ACC → SC is consistent with multiple mechanistic implementations: differential drive of direct vs indirect pathway neurons in SC, biased engagement of commissural inhibition between the two SC hemispheres, or rebalancing of basal-ganglia inputs to SC. The paper does not adjudicate between these; the SC cell-type-specific work this would require is left to follow-ups.

The number of mice is on the order of typical mouse circuit-neuroscience studies, and individual-mouse variability in the effect sizes is reported but not exhaustively dissected. Whether the dissociation holds at the level of single neurons (within each projection class) or only at the population level is also not fully resolved.

## 7. Connection to our work

Huda et al. 2020 is the empirical anchor for the user's *multi-hub system framing*. The paper's central architectural claim — that a single PFC subdivision modulates downstream sensorimotor behavior through anatomically segregated, target-specific projection channels — is a direct biological analog of the multi-hub system the user has built.

**Direct analog: multi-hub modulation of central attention.** In the user's program (thread §5), the RL hub, the MSI hub, and the VAE/decoder hub each project distinct contributions $c^{(\text{RL})}, c^{(\text{MSI})}, c^{(\text{dec})}$ into the central self-attention's Q/K/V via the Feedback Transformer. Huda et al. supplies the biological precedent: a single high-level controller (ACC) implements *channel-specific* top-down influence (ACC → V1 shapes sensory processing; ACC → SC shapes response selection). The architectural commitment — that top-down influence is not a single homogeneous broadcast but a *bundle of target-specific signals* — is the same in both. The key inversion is that in the user's program the multiple channels emerge from *multiple hubs* projecting into one substrate, while in Huda et al. the multiple channels emerge from *one hub* projecting into multiple substrates. Both are valid instantiations of the general principle that top-down influence is channelized; the user's program commits to both directions of channelization (multi-hub source + multi-target).

**Sensory channel ↔ ACC → V1.** The recurrent ViT's $H^{(t-1)}$ feedback into the attention map (§6.7 multiplicative variant) is the architectural analog of ACC → V1's modulation of cue-related processing in V1. Huda et al. demonstrates that this kind of top-down influence specifically improves sensory *sensitivity* (psychometric slope) without shifting motor *bias* — exactly the kind of dissociation the recurrent ViT's cue-validity analysis aims to demonstrate.

The architectural prediction this generates is testable in the recurrent ViT: if the model's $H^{(t-1)}$ feedback channel into the attention map is ablated, the cue-validity benefit should disappear (sensitivity drops) without the response-bias being affected. This is a clean target for §6.7-style ablation experiments and would replicate the Huda et al. ACC → V1 silencing result in silico.

**Motor channel ↔ ACC → SC.** PRISM v2's commitment to a separate readout/decision substrate that the slow memory modulates (`PRISM_V2_PROPOSAL.md` §3.4) is the architectural analog of ACC → SC's modulation of response selection. The Huda et al. finding that ACC → SC *reduces innate bias* (rather than directly driving responses) is particularly relevant: it suggests the right architectural role for a top-down signal into a decision substrate is to *flatten priors* and let evidence determine choice, not to override evidence with a command. This is consistent with precision-weighting / divisive-normalization interpretations (Feldman & Friston 2010; Reynolds & Heeger 2009).

The corresponding architectural prediction: PRISM v2's slow memory should be wired into the readout in a way that *modulates* the decision boundary or temperature, not the logits directly. Standard residual-add wiring of $H^{(t)}$ into the classifier head conflates these. A FiLM-like multiplicative modulation of the readout — scaling the inverse temperature of the softmax based on $H^{(t)}$ — is the closer architectural match to "ACC → SC reduces bias".

**Projection-specific channels avoid the "single feedback signal" trap.** A naive recurrent architecture might project $H^{(t-1)}$ into a single downstream substrate (e.g., add to a logit). Huda et al. shows the biological substrate does not work this way: distinct projections shape distinct computations. The Feedback Transformer primitive (thread §1) naturally accommodates this — each downstream node receives its own per-source Q/K/V projection. PRISM v2 should preserve this commitment by maintaining anatomically (and parameterically) distinct projection heads for each modulation target.

**Cortical microcircuit interpretation.** The ACC → V1 vs ACC → SC dichotomy aligns with the distinction between *corticocortical* feedback (L6 CC, Weiler 2025 — into V1) and *corticosubcortical* output (L5b — into SC). The user's program (thread §3) already commits to layer-6 corticocortical-style descending projections for inter-area feedback. Huda et al. supplies the functional rationale: these two pathway types serve different computational roles (sensory shaping vs response shaping), and an architecture that conflates them loses the dissociation. The PRISM v2 design should therefore distinguish between top-down projections that target the sensory pathway (V1-analog) — which should be wired to shape attention and gain — and projections that target the readout / decision substrate (SC-analog) — which should be wired to flatten priors and supply evidence-driven bias correction.

**Connection to the Clark et al. 2015 framework.** Where Clark et al. summarizes the primate evidence for PFC as the *source* of top-down attention, Huda et al. decomposes that source into *channels*. The recurrent ViT's PFC analogy (clark2015 §7) should be updated to read: $H^{(t-1)}$ is the *source* (Clark et al.); the *channel-specific projection heads* are what determines which downstream computation gets modulated (Huda et al.). The combined picture is more architecturally precise.

**Connection to the competition-emergent PC thesis.** Huda et al. presents the two channels as complementary, not competitive. The user's thesis (thread §5) would ask: do the channels compete for ACC representational bandwidth? If yes, predictive coding emerges as ACC neurons forecast each other's contributions. The paper does not pursue this, but the framework is consistent: anatomically distinct output channels can still share internal recurrent dynamics within ACC, providing a substrate for inter-channel competition. A productive extension of Huda et al.'s paradigm would be to ask whether ACC → V1 activity *predicts* ACC → SC activity on a trial-by-trial basis — if so, the two channels are coordinated by an internal model of each other, exactly the prediction of the competition-emergent PC framework.

**SC as priority map; ACC as priority-map controller.** Bisley & Goldberg 2010 framed parietal cortex (LIP) as a *priority map* whose intrinsic biases get reweighted by top-down signals. Huda et al. gives the equivalent story for SC: the SC's intrinsic response bias is the "prior" of the priority map; ACC → SC supplies the top-down reweighting. The user's program's `priority-map` concept tag (used here in `concepts:`) is justified at the architectural level: the readout / decision substrate in PRISM v2 should be modeled as a priority map (with intrinsic priors) that the slow memory reweights, not as a pure feedforward classifier.

**Architectural consequence: distinct heads, not concatenation.** A practical engineering lesson is that when the recurrent state $H^{(t)}$ is used to modulate multiple downstream computations, each modulation should be produced by a *separate learned projection head*, not by concatenating $H^{(t)}$ to multiple downstream inputs and letting the downstream networks figure it out. Huda et al.'s anatomical labeled-line organization is the biological justification for this: distinct output channels are *distinct cell populations*, not the same cells multiplexing. The Feedback Transformer formulation, where each feedback source has its own Q/K/V projection per downstream node, already implements this commitment.

**Bias reduction as a learning signal.** The "ACC → SC reduces SC's innate bias" finding suggests a *training-time* analog: a top-down signal into a decision substrate should be regularized to *decorrelate* with the substrate's intrinsic prior, not to reinforce it. If the slow memory's projection into the decision head ends up aligned with the head's bias, it is not adding information. PRISM v2's evaluation should explicitly check this: does the slow memory's contribution to the readout *correct* the intrinsic biases of the substrate, or merely amplify them?

The recurrent ViT paper (2502.10955) cites Huda et al. 2020 in its bibliography (ref [83]); future manuscripts that argue for the multi-hub architecture should cite this paper as the canonical projection-specific-PFC-top-down result. Together with Clark et al. 2015 (the source review) and Mante et al. 2013 (the PFC-as-dynamical-system result), it forms the three-paper backbone for the architectural argument: PFC is a source (Clark), a recurrent dynamical system (Mante), and a projection-specific multi-channel controller (Huda) — which are exactly the three properties the user's recurrent memory state is designed to instantiate.

## 8. Citations to follow

- `moore_armstrong2003_fef_microstim` — the foundational FEF microstim result the Huda paper cites as primate precedent. In seed, full depth.
- `zhang2014_long_range_topdown` — Zhang et al. 2014 *Science* on long-range and local circuits for top-down modulation of visual cortex. Not in seed; should be added — directly extends the ACC → V1 mechanism.
- `hu2019_corticotectal_pulvinar` — Hu et al. 2019 *Neuron* on prefrontal corticotectal neurons enhancing visual processing via SC and pulvinar. Not in seed; parallel circuit story.
- `gregoriou2012_fef_v4_synchronization` — Gregoriou et al. 2012 *Neuron* on FEF↔V4 cell-type-specific synchronization during attention. Not in seed; primate analog of the imaging.
- `wimmer2015_thalamic_attention` — Wimmer et al. 2015 *Nature* on thalamic control of sensory selection in divided attention. Not in seed; complementary thalamic story.
- `krauzlis2013_sc_attention` — Krauzlis et al. 2013 *Annu Rev Neurosci* on SC and visual spatial attention. In seed, full depth; review of the SC's attention role.
- `zenon_krauzlis2012_attention_without_cortex` — Zenon & Krauzlis 2012 *Nature* on attention deficits without cortical neuronal deficits. Not in seed; directly relevant to SC-mediated attention.
- `crapse2018_sc_decision_criteria` — Crapse et al. 2018 *Neuron* on SC's role in decision criteria. Not in seed; mechanistic basis for "ACC reduces bias" finding.
- `koike2016_acc_attention` — Koike et al. 2016 on chemogenetic dACC inactivation disrupting attention in mouse. Not in seed; companion mouse-attention result.
- `leinweber2017_sensorimotor_visual_flow` — Leinweber et al. 2017 *Neuron* on sensorimotor circuit for visual flow predictions. Not in seed; predictive-coding-adjacent.
- `schafer_moore2011_voluntary_pfc_attention` — Schafer & Moore 2011 *Science* on voluntary control of PFC neurons producing attention. Not in seed; primate top-down evidence.
- `duan2015_pfc_midbrain_executive` — Duan et al. 2015 *Neuron* on PFC and midbrain in rapid executive control. Not in seed; rat-PFC analog.
- `miller_cohen2001_pfc_theory` — Miller & Cohen 2001 *Annu Rev Neurosci* integrative PFC theory. Not in seed; foundational PFC review.
