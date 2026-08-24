---
id: stokes2015_activity_silent_wm
title: "'Activity-silent' working memory in prefrontal cortex: a dynamic coding framework"
authors:
  - "Stokes, Mark G."
year: 2015
venue: "Trends in Cognitive Sciences"
doi: "10.1016/j.tics.2015.05.004"
arxiv: ""
url: "https://www.cell.com/trends/cognitive-sciences/abstract/S1364-6613(15)00114-2"
tags:
  - working-memory
  - prefrontal-cortex
  - dynamic-coding
  - short-term-synaptic-plasticity
  - population-coding
  - theoretical
concepts:
  - multi_compartmental_memory
  - slow_fast_recurrence
  - error-gated-update
  - hidden-state-perturbation
related:
  - mongillo2008_synaptic_wm
  - desposito_postle2015_wm_neuroscience
  - christophel2017_distributed_wm
  - sreenivasan_desposito2019_delay_activity
  - masse2019_circuit_wm
  - constantinidis2018_persistent_activity
  - panichello_buschman2021_shared_mechanisms
relevance_to:
  - prism_v1
  - prism_v2
  - rvit_plus
seed_source:
  - manual_deep_dive_2026_05_23
status: full
depth: full
last_updated: "2026-05-23"
---

# 'Activity-silent' working memory in prefrontal cortex: a dynamic coding framework

## 1. Abstract

> "Working memory (WM) provides the functional backbone to high-level cognition. Maintenance in WM is often assumed to depend on the stationary persistence of neural activity patterns that represent memory content. However, accumulating evidence suggests that persistent delay activity does not always accompany WM maintenance but instead seems to wax and wane as a function of the current task relevance of memoranda. Furthermore, new methods for measuring and analysing population-level patterns show that activity states are highly dynamic. At first glance, these dynamics seem at odds with the very nature of WM. How can we keep a stable thought in mind while brain activity is constantly changing? This review considers how neural dynamics might be functionally important for WM maintenance." (Stokes 2015, *Trends in Cognitive Sciences* 19(7):394-405, abstract.)

## 2. Why this matters for us

Stokes 2015 is the field-defining articulation of *activity-silent* working memory — the proposal that WM content can be maintained in a *latent* form via short-term synaptic plasticity (STSP), without continuous spiking activity, and re-evoked by impulse perturbations. For the user's program, this is doubly important. First, it provides a biological warrant for *gated* memory: not every item held in memory needs to be continuously refreshed; items can sit silent in the synaptic substrate until needed, with an attention-driven gate deciding when they re-enter active state. Second, the dynamic-coding framework — that WM populations rotate through subspaces over time rather than holding a fixed pattern — predicts that the recurrent ViT's hidden state should *not* be temporally stationary even when carrying a stable mnemonic content. This challenges naive interpretations of the user's memory state and supplies the computational logic for the "code morphing" the user should expect to observe.

## 3. Key claims

1. Persistent attractor-style delay activity is neither necessary nor sufficient for WM maintenance; the field's default mechanism is wrong.
2. WM content can be maintained in *activity-silent* form via short-term synaptic plasticity (STSP, especially short-term facilitation) that biases future network dynamics without continuous firing.
3. Population codes for WM contents are inherently *dynamic*: the neural geometry that represents an item rotates over time even as the represented content remains stable.
4. A *hidden state* in the synaptic substrate can be revealed by a non-specific perturbation (TMS pulse, impulse stimulus, attentional cue) that re-evokes a content-specific pattern.
5. Dynamic coding is functionally adaptive — it supports flexible read-out, gating, and protection from interference.
6. "Code morphing" allows the same population to multiplex maintenance, control, and response-selection operations.
7. WM and selective attention are tightly coupled; only *attended* items occupy active spiking states, while unattended-but-relevant items go silent.
8. A unified framework: WM = dynamic patterns over a network whose connectivity is *transiently sculpted* by STSP — the substrate is not the activity, it is the activity-history-modified synaptic structure.

## 4. Methods

This is a theoretical review integrating three classes of evidence. (i) Primate single-unit recordings from PFC (Stokes et al. 2013 *Neuron*; Meyers et al. 2008) showing population-coding patterns that rotate during the delay, with cross-temporal decoders that generalize poorly across time — diagnostic of dynamic codes. (ii) Computational/biophysical models of short-term synaptic facilitation (Mongillo, Barak & Tsodyks 2008 *Science*) demonstrating that items can be maintained for ~1 s at zero or near-zero firing rates by leaving a synaptic trace in the form of pre-synaptic calcium accumulation. (iii) Human TMS-fMRI and EEG evidence for reactivation of unattended WM items (LaRocque et al. 2013; Wolff et al. 2015) — the "pinging" paradigm where a non-specific perturbation re-evokes a content-specific neural pattern, providing operational evidence for a silent hidden state. Stokes integrates these into a single framework where WM maintenance is *layered* — moment-to-moment active firing for attended items, synaptic-trace silent storage for unattended-but-relevant items, with attention controlling the conversion between states.

## 5. Results

This is a theoretical synthesis paper; the empirical anchors Stokes consolidates from the primary literature are:

- **Stokes et al. (2013) *Neuron*** — prefrontal population coding patterns *rotate* during the delay despite stable task content; cross-temporal classifiers generalize poorly, ruling out a fixed-pattern attractor mechanism.
- **Mongillo et al. (2008) *Science*** — biophysical model with synaptic facilitation maintains item identity for ~1 s with no sustained firing; cued reactivation re-evokes the item's representation.
- **Lundqvist et al. (2010, 2016) *Neuron*** — gamma-burst dynamics show WM activity is non-stationary and bursty; the "burst" framework predicts activity-silent intervals interleaved with brief active firing.
- **LaRocque et al. (2013)** — fMRI MVPA cannot decode "unattended" WM items even when behavior demonstrates they are retained; consistent with these items being held in activity-silent form.
- **Wolff et al. (2015, later *Nat Neurosci* 2017)** — EEG "impulse response" perturbations re-evoke content patterns from silent states, providing direct evidence for the hidden-state account.
- **Murray et al. (2017)** — stable cross-temporal decoding co-exists with dynamic single-unit responses, by virtue of subspace orthogonality between the *stable* coding axis and the *dynamic* code-morphing axes.
- **Watanabe & Funahashi (2014)** — dual-task interference reduces but does not abolish delay firing, consistent with the activity-silent fallback when active firing is disrupted.
- **Quantitative timescale** — synaptic facilitation in cortex has a time constant of ~1 s; maintaining items over multi-second delays therefore requires *either* periodic active-firing refresh or a slower synaptic mechanism. The framework predicts a hybrid: brief active firing intervals refresh the silent synaptic state.

## 6. Critique / limitations

The activity-silent framework is influential but several aspects remain contested.

- **Direct experimental evidence for STSP-based silent storage in vivo remains indirect.** No paper has unambiguously shown a synaptic facilitation trace carrying a specific WM item; the evidence is largely from population dynamics and reactivation paradigms.
- **The "activity-silent" claim is partly a null result.** Sufficiently sensitive decoders applied to large-scale recordings may yet detect persistent low-rate signals; absence-of-decoding ≠ absence of activity.
- **Conflicts with strong evidence for sustained spiking codes in many PFC studies** (Goldman-Rakic, Funahashi, Constantinidis tradition). Constantinidis et al. (2018, [constantinidis2018_persistent_activity](constantinidis2018_persistent_activity.md)) is the principal counterposition; the field is not converged.
- **Capacity limits and precision degradation are not yet quantitatively derived from the dynamic-coding framework.** Why is WM capacity ~4 items rather than 40 or 0.4? The activity-silent account does not yet provide a closed-form answer.
- **Synaptic facilitation time-constants** (~1 s) are shorter than typical WM delays (5-30 s); the framework requires periodic active-firing refresh, but the rate and structure of that refresh are underspecified.
- **Cross-species generalization** (rodent vs primate vs human) is asserted but not strongly demonstrated; most direct evidence is primate PFC.
- **Some "dynamic" results may reflect changes in task state, attention, or motor preparation** rather than storage per se — the framework's predictions need careful task-design disentanglement.
- **Mechanistic separation between attention and storage is underspecified.** The framework's claim that attended items occupy active states while unattended items go silent is intuitively appealing but lacks a circuit-level mechanism for the active/silent conversion.

## 7. Connection to our work

Stokes 2015 is one of the most architecturally consequential WM papers for the user's program because it supplies the biological warrant for several specific design choices.

**Touchpoint 1: gated memory updates as the activity-silent/active conversion.** The activity-silent framework predicts that WM content is held in a synaptic substrate until *attention* (or a task-driven cue) converts it back to active firing for use. This is the biological template for the user's *attention-gated memory update* commitment: the central self-attention substrate decides which items in memory are made *active* at each timestep (gating ON / OFF) while leaving silent items untouched. PRISM v2's `M_slow` (which updates rarely under a heavily-biased gate, [concepts/slow_fast_recurrence.md](../concepts/slow_fast_recurrence.md) Mechanism 2) and the recurrent ViT's attention-modulated memory update are architectural instances of the active/silent conversion. The biological warrant gives the choice of a gated rather than continuously-updated memory a substantive rather than arbitrary motivation.

**Touchpoint 2: dynamic coding predicts the user's memory state should rotate over time.** Stokes' central claim — that WM populations rotate through subspaces during the delay even when carrying a stable content — predicts that the recurrent ViT's hidden state $H^{(t)}$ should *not* be temporally stationary even when the represented content (target identity, task rule) is stable. This is a direct empirical prediction for the user's analyses: probing $H^{(t)}$ at multiple delay times and looking for a stable cross-temporal decoder should *fail* (in line with Stokes 2013), while training time-specific decoders should succeed. The architectural reading is that the user's memory dynamics are *expected* to be non-stationary, and the failure of stable decoders is not a bug but a biological prediction realized.

**Touchpoint 3: hidden-state perturbation as a probe for activity-silent representations.** Stokes' "pinging" paradigm — a non-specific perturbation reveals a content-specific representation — has a direct architectural translation in the user's models. To test whether $M_{slow}$ holds latent content even when its current firing/activation pattern looks unstructured, apply a *neutral* input perturbation (e.g., a uniform stimulus or a random noise pulse) and decode the resulting memory state. If a content-specific pattern re-emerges, the user has demonstrated activity-silent storage in the architecture. This is a concrete, novel experimental program for the user's models, directly inspired by the Stokes framework.

**Touchpoint 4: short-term synaptic plasticity as the substrate for the user's slow-fast separation.** Stokes' computational mechanism — STSP — has time constants (~1 s for synaptic facilitation, ~10 s for STDP, longer for late-phase LTP) that span exactly the slow-fast separation the user's program commits to ([concepts/slow_fast_recurrence.md](../concepts/slow_fast_recurrence.md)). The biological hierarchy is:

| Timescale | Biological substrate | Architectural analog |
|---|---|---|
| ~30-100 Hz | Gamma oscillations, active spiking | Per-step input integration |
| ~1 s | Short-term facilitation | $M_{fast}$ recurrent state |
| ~10 s | Short-term plasticity | $M_{slow}$ recurrent state |
| ~minutes-hours | Late-phase LTP (Lisman-Grace) | Slow-memory gated write |

The user's two-compartment design captures the middle two rows; extension to three compartments would add the gamma timescale at the bottom and the LTP timescale at the top. This gives a principled timescale-stacking design rather than an arbitrary hyperparameter choice.

**Touchpoint 5: the "code morphing" framework reframes the user's update gate.** Stokes argues that the same population multiplexes maintenance, control, and response selection by morphing its coding subspace over time. This is the biological warrant for the user's architectural choice to update memory *continuously* (gate bias = 0 in [concepts/gridcell_rnn.md](../concepts/gridcell_rnn.md) Refinement 3) rather than freezing the state during the delay: even when the "content" is stable, the *code* should keep evolving to support different operations (maintenance now → output selection later). The user's reactive baseline ($\sigma(0) = 0.5$) is the architectural instantiation of code morphing — every step modifies the state, keeping the code dynamic rather than frozen.

**Touchpoint 6: attention as the active/silent switch — convergence with Panichello & Buschman.** The framework's prediction that attention determines which WM items are active versus silent converges with Panichello & Buschman's (2021, [panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md)) finding that PFC attention and PFC WM share a substrate. In the user's architecture, this is the *Q/K* manipulation of the central self-attention: hubs that win attention weight have their memory states made active (queried by other hubs); hubs that lose attention weight have their memory states go silent (not queried, not refreshed). The architectural instantiation of activity-silent WM is therefore *exactly* the inter-hub attention competition the user's program already commits to.

**Touchpoint 7: implications for the iterative variational encoder-decoder.** The iterative VAE's forward-reasoning passes ([concepts/iterative_variational_encoder_decoder.md](../concepts/iterative_variational_encoder_decoder.md)) can be reinterpreted through the activity-silent lens: each pass *reactivates* the silent latent state from the previous pass, producing a refined active representation. The dynamic coding framework predicts that intermediate-pass representations should not be stable across iterations — they should rotate as the inference progresses. The architectural recommendation is therefore *not* to enforce stability across iterations (a common assumption in iterative refinement) but to allow code morphing, with stability emerging only in the final pass.

## 8. Citations to follow

- `wolff_stokes2017_dynamic_hidden_states` — the empirical instantiation of the pinging paradigm in human EEG; the most direct evidence for activity-silent WM. Not in seed.
- `rose_postle2016_tms_reactivation_science` — the TMS reactivation of latent WM items in humans; the causal complement to Wolff. Not in seed.
- `lundqvist2016_gamma_beta_bursts_wm` — gamma and beta bursts underlie working memory; the burst-based reframing of delay activity. Not in seed.
- [mongillo2008_synaptic_wm](mongillo2008_synaptic_wm.md) — the foundational synaptic-facilitation model of activity-silent WM. In seed.
- [masse2019_circuit_wm](masse2019_circuit_wm.md) — circuit-level mechanisms for WM maintenance and manipulation that integrate persistent and silent codes. In seed.
- `trubutschek2017_wm_without_consciousness` — eLife paper showing WM can persist without conscious access or sustained activity; the unconscious-WM extension of the activity-silent framework. Not in seed.
- [constantinidis2018_persistent_activity](constantinidis2018_persistent_activity.md) — the persistent-activity defense; the principal counterposition. In seed.
- `lundqvist_herman_miller2018_delay_activity_yes` — the burst-based middle-ground position. Not in seed.
- `schneegans_bays2017_decodability_caveat` — restoration of fMRI decodability does not imply latent WM states; the methodological skeptic's position. Not in seed.
- `barbosa_compte2020_interplay_persistent_silent` — interplay between persistent activity and activity-silent dynamics in PFC; the empirical resolution-attempt. Not in seed.
- `kaminski_rutishauser2020_between_frameworks` — review pitching a between-frameworks synthesis with human single-unit data. Not in seed.
- `panichello_buschman2021_shared_mechanisms` — already in seed; the empirical convergence with the active/silent gate as attention. In seed.
