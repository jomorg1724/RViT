---
id: sani2017_temporal_v4_gain
title: "Temporally evolving gain mechanisms of attention in macaque area V4"
authors:
  - "Sani, Ilaria"
  - "Santandrea, Elisa"
  - "Morrone, Maria Concetta"
  - "Chelazzi, Leonardo"
year: 2017
venue: "Journal of Neurophysiology"
doi: "10.1152/jn.00522.2016"
arxiv: ""
url: "https://pubmed.ncbi.nlm.nih.gov/28468996/"
tags:
  - primate-neurophysiology
  - visual-attention
  - early-visual-cortex
concepts:
  - gain-modulation
  - divisive-normalization
  - multiplicative-feedback
  - top-down-feedback
related:
  - ghose_maunsell2002_task_timing
  - nobre_vanede2018_anticipated_moments
  - reynolds_heeger2009_normalization
  - mcadams_maunsell1999_reliability
  - kietzmann2019_recurrence_required
  - treue_martinez_trujillo1999_feature_attention
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_60
status: full
depth: full
last_updated: "2026-05-16"
---

# Temporally evolving gain mechanisms of attention in macaque area V4

## 1. Abstract

Cognitive attention and perceptual saliency jointly govern our interaction with the environment, yet a universally accepted account of the interplay between attention and luminance contrast — a fundamental dimension of saliency — is still lacking. Sani and colleagues measured the attentional modulation of V4 neurons' contrast response functions (CRFs) in awake, behaving macaques, applying a new approach that emphasizes the temporal dynamics of cell responses. They found that attention modulates CRFs via different gain mechanisms during subsequent epochs of visually driven activity: an early contrast-gain effect strongly dependent on prestimulus activity changes (baseline shift); a time-limited, stimulus-dependent multiplicative (response-gain) modulation reaching its maximal expression around 150 ms after stimulus onset; and a late resurgence of contrast-gain modulation. Attention produced comparable time-dependent gain changes across cells with heterogeneous contrast coding, supporting the view that the same circuits mediate attention in V4 regardless of the form of contrast selectivity. Attention was also occasionally able to induce radical transformations in the shape of CRFs. These findings offer a new perspective on contrast coding and attention in primate visual cortex, one in which time is a fundamental factor.

## 2. Why this matters for us

Sani et al. is direct empirical evidence that attentional gain in V4 is *not* a single stationary multiplier but a sequence of qualitatively different modulations — baseline shift, then response gain, then contrast gain — unfolding on the same trial within ~300 ms. This is the closest neurophysiological analog of the Recurrent ViT's claim that attention maps evolve over recurrent passes (`THESIS.md` §6; 2502.10955 §6) and of PRISM's commitment to a saliency-gated update that *changes character* across timesteps (`PRISM_V2_PROPOSAL.md` §3.3). It also extends Ghose & Maunsell 2002 from temporal expectation per se to the gain mechanism that implements it.

## 3. Key claims

1. Attentional modulation of V4 CRFs decomposes into at least three temporally distinct regimes within a single trial.
2. An early effect (~0–80 ms after stimulus onset) is a contrast-gain modulation that rides on a prestimulus baseline shift — i.e., it is inherited from anticipatory activity, not stimulus-driven.
3. A middle effect (peaking ~150 ms after stimulus onset) is a stimulus-dependent multiplicative response-gain modulation.
4. A late effect (>200 ms) is a resurgence of contrast-gain modulation, distinct in mechanism from the early one because no baseline shift is required.
5. These time-dependent gain changes are observed similarly across V4 cells with heterogeneous contrast tuning, suggesting a common attentional circuit operates on whatever contrast representation each cell encodes.
6. Attention can occasionally induce qualitative transformations of the CRF shape (e.g., non-monotonic into monotonic), not merely scale it.

## 4. Methods

Two macaques performed a covert spatial attention task in which a peripheral cue indicated the location of an upcoming target whose contrast varied across trials. Single-unit recordings in V4 isolated neurons whose receptive fields contained either the attended or an unattended location. Contrast response functions were measured separately for attend-in and attend-out conditions, and crucially the firing-rate response was decomposed into successive time windows (early, ~0–80 ms; middle, ~80–180 ms; late, ~180–300 ms post-stimulus) so that the attentional modulation could be characterized as a function of poststimulus time.

For each time window the authors fit the Naka–Rushton CRF $R(c) = R_\text{max} c^n / (c^n + c_{50}^n) + b$ and asked which parameters (baseline $b$, multiplicative gain $R_\text{max}$, semi-saturation $c_{50}$) differed between attend-in and attend-out. A contrast-gain regime corresponds to a horizontal shift ($c_{50}$ changes); a response-gain regime corresponds to a vertical scaling ($R_\text{max}$ changes); a baseline shift corresponds to a change in $b$ even before stimulus onset. The same per-time-window fitting was applied population-wise and per-cell.

## 5. Results

- Three distinct epochs of attentional modulation are robustly identified across the V4 population:
  - **Early (≈0–80 ms post-stimulus):** dominated by contrast-gain modulation, but only because of a prestimulus baseline shift; subtracting baseline removes most of the apparent early gain effect.
  - **Middle (peaks ≈150 ms):** stimulus-dependent multiplicative response-gain modulation; here $R_\text{max}$ increases under attention with little change in $c_{50}$.
  - **Late (>200 ms):** a second contrast-gain phase emerges, this one not explained by baseline shift.
- The effect sizes reported are typical for V4 attention studies (population multiplicative gains of order 1.1–1.4× during the middle epoch).
- The pattern is preserved across cells with different contrast selectivities, including non-monotonic CRFs.
- In a minority of cells, attention transforms CRFs qualitatively rather than parametrically (e.g., flipping non-monotonic to monotonic shapes within the same neuron between attend-in and attend-out).

## 6. Critique / limitations

The decomposition into "early / middle / late" epochs is by design analytically clean but rests on time-window choices that are partly methodological; the underlying neural process is presumably continuous, and the appearance of three discrete regimes may overstate the segregation. Replication with sliding-window analyses would strengthen the claim.

The temporal dynamics are observed but the mechanism generating them is not isolated. The early contrast-gain-via-baseline-shift could reflect tonic top-down drive from FEF/LIP priority maps; the middle response-gain could reflect a thalamocortical or normalization-pool change triggered by stimulus arrival; the late contrast-gain resurgence is the least well-explained. The paper does not adjudicate among these candidate sources.

Cell sample sizes are modest (typical for primate single-unit work) and the task uses a single behavioral paradigm. Whether the three-phase structure generalizes to feature-based attention, to natural images, or to free viewing is untested.

Finally, the Naka–Rushton parameter decomposition treats the cell as a static nonlinearity within each time window. If V4 cells implement nontrivial recurrent dynamics across the same window (which other work suggests they do), some of the apparent "gain change" is really a dynamical-systems phenomenon being mis-modeled as a parameter shift.

## 7. Connection to our work

Sani et al. is one of the load-bearing empirical anchors for the *time-varying* attention claim that motivates both the Recurrent ViT and PRISM. Three concrete connections:

**Recurrent ViT — attention map evolution over recurrent passes.** The published Recurrent ViT (2502.10955 §6; `THESIS.md` §6) explicitly visualizes attention maps as a function of recurrent step and shows that they evolve nontrivially: focusing, defocusing, and re-engaging. This is qualitatively the same phenomenology Sani et al. document in V4: an early baseline-driven phase, a middle multiplicative phase, and a late resurgence. The ViT's recurrent step plays the role of poststimulus time. Where Reynolds & Heeger 2009 supplies a *static* gain-field theory, Sani et al. supplies the temporal layer that justifies modeling attention as a dynamic process — i.e., the recurrent ViT's central architectural commitment.

**PRISM v2 — slow/fast memory and temporally-graded gain.** PRISM v2 (`PRISM_V2_PROPOSAL.md` §3.3, §3.4) introduces two memory timescales (fast $M^F_t$ and slow $M^S_t$) and applies hierarchical FiLM at two cortical levels. The Sani et al. three-phase structure is naturally read as: the *early baseline-shift contrast-gain* corresponds to slow-memory top-down drive arriving before stimulus onset; the *middle multiplicative response-gain* corresponds to a fast, stimulus-locked FiLM modulation; the *late contrast-gain resurgence* corresponds to a second, integrated readout from the slow memory after evidence has accumulated. The fact that biology uses *different* gain mechanisms at different epochs, not just different magnitudes of one mechanism, is an argument for PRISM v2's commitment to compositional modulation rather than a single FiLM block (`PRISM_V2_PROPOSAL.md` §3.4).

**User's broader program — feedback-transformer dynamics over forward-reasoning steps.** In the user's iterative-VAE program (`threads/the_user_architectural_program.md` §4), the encoder runs $n_{FR}$ forward-reasoning passes over a static image and the guide $H_t$ evolves attractor-like across passes. Sani et al. is the closest biological evidence that such within-trial reuse of the same input *does* drive qualitatively different gain states at different times in the primate visual system. The Food-101 classifier observation that attention maps "focus, defocus, and reactivate" across recurrent passes (`Private & Shared-2/Classifier`) recapitulates the Sani et al. early/middle/late pattern. This is an empirical license to expect that recurrent ViTs and feedback-transformer architectures should exhibit non-monotonic attention trajectories, and that those trajectories are biologically natural rather than artifacts.

The connection to Reynolds & Heeger 2009 is that Sani et al. accepts the gain-modulation framework but argues for *time-varying parameters*: the normalization-model parameters $G_E$ and $G_S$ (and the implicit baseline) are themselves functions of poststimulus time. Any ML implementation of normalization-based attention that holds these parameters fixed will miss the biologically dominant phenomenon. PRISM v1's single per-timestep FiLM (`THESIS.md` §2.4) is therefore consistent with Sani et al. only if we read the timestep index $t$ as poststimulus time within a single trial — which is how the user's recurrent-ViT and PRISM are in fact organized.

## 8. Citations to follow

- `ghose_maunsell2002_task_timing` — already an intended seed; the temporal-expectation foundation that Sani et al. mechanistically extends.
- `mcadams_maunsell1999_reliability` — already an intended seed; the baseline V4 attentional-gain reference against which Sani et al.'s time-resolved decomposition is measured.
- `reynolds_heeger2009_normalization` — already in the database; the gain-field framework Sani et al. extends to time.
- `nobre_vanede2018_anticipated_moments` — already an intended seed; supplies the human-behavior counterpart to Sani et al.'s prestimulus baseline shift.
- `kietzmann2019_recurrence_required` — already an intended seed; argues that recurrent dynamics are required to capture exactly the kind of temporally-evolving cortical responses Sani et al. report.
- `reynolds_chelazzi2004_attention_review` — Chelazzi's own review; would consolidate the lab's interpretive framework around the present result.
- `motter1993_focal_attention_v4` — candidate for addition; an earlier V4 spatial-attention study Sani et al. contrasts methodologically.
- `treue_martinez_trujillo1999_feature_attention` — candidate for addition; the feature-based-attention counterpart often co-cited with V4 spatial-attention data.
