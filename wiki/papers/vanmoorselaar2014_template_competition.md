---
id: vanmoorselaar2014_template_competition
title: "In competition for the attentional template: Can multiple items within visual working memory guide attention?"
authors:
  - "van Moorselaar, Dirk"
  - "Theeuwes, Jan"
  - "Olivers, Christian N. L."
year: 2014
venue: "JEP: HPP"
doi: "10.1037/a0036229"
arxiv: ""
url: "https://doi.org/10.1037/a0036229"
tags:
  - working-memory
  - visual-attention
  - psychophysics
concepts:
  - attentional-template
  - working-memory-persistent-activity
related:
  - olivers2011_wm_states_attention
  - carlisle2011_attentional_templates
  - awh2006_attention_wm
  - bahle2018_wm_attention_architecture
  - panichello_buschman2021_shared_mechanisms
  - oberauer2002_access_wm
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_19
status: full
depth: full
last_updated: "2026-05-16"
---

# In competition for the attentional template: Can multiple items within visual working memory guide attention?

## 1. Abstract

Van Moorselaar, Theeuwes, and Olivers (2014) test whether multiple items held in visual working memory (VWM) can simultaneously guide attention, as a direct empirical test of Olivers et al. (2011)'s active-accessory framework. Across a series of memory-plus-search experiments, observers maintained varying numbers of colors (set size 1, 2, 3, 4) in VWM while performing a visual-search task in which one search-distractor could match a memorized color. With a single item in memory, the memory-matching distractor reliably captured attention (the canonical Soto-style memory-driven capture effect). As memory set size increased beyond one, the memory-driven capture effect vanished — even though items remained well-represented in memory and were correctly reported at the end of the trial. Crucially, when observers were retro-cued to a single memorized item after encoding (so only one of the multiple memorized items was active), capture by that item returned. The authors conclude that VWM contains representations of multiple types, but *only one* representation can occupy the "attentional template" state that biases perception at any given moment. Multi-item memory load does not produce proportional multi-item guidance; instead, the additional items move into an accessory state.

## 2. Why this matters for us

This is the direct empirical test of the *capacity-of-1 active template* commitment that Olivers et al. (2011) introduced as theory. Van Moorselaar et al. (2014) provide the behavioral evidence that distinguishes between two architectural hypotheses for the WM-attention interface: (a) all memorized items proportionally bias attention (the additive-template hypothesis); and (b) only one memorized item, at any moment, occupies the attention-biasing role (the single-template hypothesis). The data unambiguously support (b). For the user's program, this constrains the design of the recurrent-state-to-attention pathway: the central self-attention substrate behaves like a single-template channel, with the multi-hub system implementing competition for *which* memorized item gets to be the active template, not a parallel superposition of templates.

## 3. Key claims

1. **One template at a time.**
   Only one item from VWM can serve as an active attentional template biasing visual selection at any given moment. Multiple memorized items do not produce additive or proportional attentional guidance.
2. **Capture disappears with load.**
   Memory-driven capture (the bias toward a search distractor matching a memorized item) is robust at set size 1 but vanishes at set size 2 and larger, even when the memorized items are individually well-represented.
3. **Memory quality is not the bottleneck.**
   The collapse of capture is not a consequence of degraded memory precision under load — items at set sizes 2-4 are still recalled reliably; they just don't guide attention. This dissociates *maintenance* from *attentional templatehood*.
4. **Cueing restores capture.**
   A retro-cue presented after encoding, indicating which memorized item is relevant for the upcoming trial, restores memory-driven capture for that item. This shows the single-template channel is plastic — items can be promoted into it by an internal cue.
5. **VWM is multi-state.**
   The data require a distinction within VWM between an "active" representation (the attentional template) and "accessory" representations (maintained but not biasing perception). This empirically validates Olivers et al. (2011)'s theoretical proposal.
6. **The active state has a capacity of approximately 1.**
   The capture effect does not appear to be diluted across two items; it appears to be present for one and absent for two-or-more. The active state is closer to a discrete single slot than to a continuously dividable resource.
7. **Individual-difference invariance.**
   The capacity-of-1 pattern holds across individuals with differing memory capacity and precision, ruling out the explanation that low-capacity observers are responsible for the effect.

## 4. Methods

A series of behavioral experiments combining a memory task with a visual-search task within each trial.

**General trial structure.** On each trial, observers were shown $N$ colored items to memorize ($N \in \{1, 2, 3, 4\}$ depending on the condition), followed by a visual-search display in which they had to find a shape singleton (e.g., a uniquely-shaped target among shape distractors) and respond to a property of it. The critical manipulation was whether one of the search distractors was rendered in a color that matched one of the memorized items. The trial ended with a memory probe asking observers to identify the memorized item(s).

**The capture effect.** Memory-driven attentional capture is operationalized as a reaction-time slowdown on trials where the search display contains a distractor matching one of the memorized colors, compared to trials where no distractor matches. A positive capture effect is evidence that at least one memorized item is currently functioning as an active template that biases search.

**Set-size manipulation.** Critical comparisons were between set sizes 1, 2, 3, and 4 for the memory load, holding constant the structure of the search display. The search display itself was deliberately unrelated to the memory items in shape and task, so any attentional bias toward the matching-color distractor reflects involuntary, memory-driven guidance rather than strategic search.

**Retro-cue manipulation.** In a follow-up experiment, after encoding multiple items observers received a cue (e.g., a single color word or icon) indicating which memorized item would be tested at the end of the trial. The retro-cue was presented before the search display. The prediction was that the cue would promote one memorized item into the active-template state and restore capture for that item.

**Memory precision controls.** To rule out a memory-quality explanation, the authors ran control experiments confirming that memorized items at set sizes 2-4 were still recalled at above-chance levels and with sufficient precision to support recognition of the matching distractor color, had the comparison been done. They also stratified analyses by individual differences in WM capacity to test whether capacity-of-1 reflects a low-capacity-observer artifact.

**Distractor-irrelevance instructions.** Critically, the matching color was *never* the target's color; observers always knew it was task-irrelevant. Capture in this paradigm is therefore involuntary, driven by the contents of WM rather than by strategic deployment of attention. This makes the result speak directly to architectural rather than strategic constraints on template usage.

## 5. Results

The principal quantitative findings:

- **Set size 1.** Memory-matching distractors produced reliable capture, with reaction-time costs in the range typical of the memory-driven capture literature (tens of milliseconds slowdown on matching-distractor vs. nonmatching-distractor trials).
- **Set size 2-4.** The capture effect vanished. Reaction times on matching-distractor trials were statistically indistinguishable from those on nonmatching-distractor trials, despite memorized items being well-represented.
- **Set size 1 vs 2-4 contrast.** The interaction between memory set size and matching-distractor cost was reliable: the capture effect was specific to single-item memory loads.
- **Retro-cue condition.** When observers were cued post-encoding to a single memorized item from a multi-item set, the capture effect for that item returned to a magnitude comparable to the set-size-1 condition. Capture for the uncued (still-memorized) items remained absent.
- **Memory accuracy.** Memory accuracy at set size 4 remained substantially above chance, ruling out a "the items were forgotten" account of the absent capture effect.
- **Individual differences.** The pattern held when participants were stratified by individual WM capacity or memory precision: even high-capacity observers showed the single-item-only capture pattern. Capacity-of-1 is therefore not an artifact of low-capacity participants pulling the average down.
- **Robustness.** The pattern was robust across multiple experiments with different stimulus details, encoding times, search-display configurations, and different observer pools, supporting generality of the conclusion.

## 6. Critique / limitations

The capacity-of-1 conclusion is the strongest interpretation; a weaker reading is that the active state is *small* (perhaps 1, perhaps 2 under some conditions). The all-or-nothing transition between set size 1 and set size 2 in these data supports the strong reading, but subsequent work (e.g., Beck et al. 2018) has demonstrated conditions under which two items can simultaneously guide attention. The active state's capacity may be context-dependent rather than strictly 1.

The dissociation between memory accuracy and capture is the load-bearing finding. The control experiments rule out a memory-quality account but do not rule out a more subtle account in which capacity-of-1 reflects a strategic choice (under high memory load, observers strategically disengage memory from attention) rather than an architectural constraint. A strategic account predicts that with sufficient incentive, observers could deploy multiple templates simultaneously; an architectural account predicts they cannot.

The retro-cue result is consistent with active-state plasticity but does not directly demonstrate that exactly one item is in the active state. A continuous-activation account (where the cued item has higher activation than the others but not exclusive access) could also produce the data pattern.

The paradigm is specific to color-based capture in a singleton-search task. Whether the capacity-of-1 generalizes to other features (shape, motion, orientation) and other tasks (e.g., conjunction search, feature-guided memory tasks) is an open question, though subsequent work largely supports generalization.

The neural-level account is correlational at best: the paper does not directly measure neural activity, so the active-vs-accessory mapping onto neural states (cf. Panichello & Buschman 2021's output-vs-memory subspaces) is an inference from behavior rather than a direct measurement.

## 7. Connection to our work

This paper supplies the *quantitative* foundation for the capacity-of-1 commitment in the user's architectural program:

**Capacity-of-1 in the recurrent ViT's softmax attention.** The recurrent ViT's central self-attention substrate produces an attention map whose softmax tends to concentrate mass on a single peak. The architectural form of this is the temperature-scaled softmax: with sharp enough softmax, only one location dominates the attention map at a time. Van Moorselaar et al. (2014) supply the cognitive-behavioral evidence that this single-peak structure is not an architectural accident but mirrors a real constraint on biological attention: a single active template at a time. The model's single-peak attention is the architectural form of "one item in the active state." The recurrent ViT paper's reported attention-map visualizations — which show a single focal peak rather than a diffuse multi-peak landscape — are consistent with the capacity-of-1 constraint.

**Hub competition in the multi-hub system.** The user's multi-hub system ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md)) maintains multiple memory states across MSI, RL, and VAE hubs, each contributing to the central self-attention through per-hub Q/K projections that combine with sensory Q/K via Hadamard products. Van Moorselaar's capacity-of-1 result implies that, at any moment, only one hub's contribution should effectively *dominate* the resulting attention map. This is the architectural translation of "one active template at a time": the competition for self-attention control is a competition for *which hub's prediction* becomes the de-facto attentional template. Hubs are constrained to take turns at the active-template role; they cannot run in superposition. This converts the capacity-of-1 finding from a behavioral constraint into a falsifiable architectural prediction: in a multi-hub model running on a search-with-distractors task, ablating any single hub at a time should substantially change the attention map, whereas ablating multiple hubs simultaneously should produce non-additive effects, because at any moment only one hub is doing the templatehood work.

**Plasticity via cue-driven swap.** The retro-cue effect in van Moorselaar et al. (2014) — where a post-encoding cue restores capture for the cued item — maps directly onto the recurrent ViT's cue-driven attention shifting. When the recurrent ViT receives a cue, the recurrent state's contribution to the next attention map shifts toward the cued location, effectively swapping which item is the active template. The model's cue-driven attention map is the architectural form of the retro-cue's promotion of an accessory item into the active state. A direct empirical analogue in the model would be: hold a multi-element scene in $H^{(t-1)}$, then inject a cue at time $t$ and measure whether the resulting attention map shifts cleanly to the cued element with the others suppressed (consistent with van Moorselaar) or distributes across all elements (inconsistent).

**Constraint on PRISM v2's multi-memory channels.** PRISM v2's hierarchical FiLM and multi-memory commitments raise the question of whether multiple memory channels should simultaneously bias the next-frame prediction. Van Moorselaar et al. (2014) argue that biological systems do not do this — at any moment, only one memory is in the template-controlling role. PRISM v2 should accordingly implement memory channels that *compete* for influence over the prediction map, rather than additively superpose their contributions.

**Active-vs-accessory and the feedback transformer.** In the Feedback Transformer primitive (`the_user_architectural_program` §1), multiple feedback sources combine via Hadamard products into a single Q vector. The capacity-of-1 result suggests that, at any moment, only one feedback source's contribution should produce a coherent template; the others should be effectively dormant. A test of this in the user's model would be to probe whether, across recurrent steps, the dominant feedback contribution switches identity rather than supporting multiple simultaneous template-like contributions. Operationally: if at time $t$ the MSI hub's feedback dominates the Q projection, the RL and VAE hubs' contributions to that step's Q should be near-multiplicatively-neutral. This is a strong, testable prediction that maps van Moorselaar's behavioral finding onto a measurable property of trained models.

**Empirical contact with the change-detection task.** The Recurrent ViT paper's change-detection task involves comparing successive frames. If the model must hold a representation of frame $t-1$ as the active template against which frame $t$ is compared, van Moorselaar's result says that multi-template comparison (across multiple held frames) is not feasible — the comparison must be done one template at a time. The recurrent ViT's single-state recurrent design (one $H^{(t-1)}$ per time step) is the architecturally consistent choice; a multi-frame buffer would violate the empirical capacity constraint.

**Summary.**
The recurrent ViT paper (2502.10955) cites this paper at ref [19]. The user's manuscripts on change detection and multi-hub competition should cite van Moorselaar et al. (2014) specifically for the capacity-of-1 result, not just Olivers et al. (2011), because van Moorselaar is the direct empirical test where Olivers is the theoretical proposal.

## 8. Citations to follow

- `olivers2011_wm_states_attention` — the theoretical precursor; in seed at full depth.
- `soto_heinke_humphreys2005_memory_attention_capture` — the foundational memory-driven-capture paradigm this paper extends. Not yet in seed; high priority.
- `carlisle2011_attentional_templates` — attentional templates in WM; in seed.
- `bahle2018_wm_attention_architecture` — multi-template architecture; in seed.
- `awh2006_attention_wm` — attention-WM substrate; in seed at full depth.
- `panichello_buschman2021_shared_mechanisms` — modern neural-subspace analog of active-vs-accessory; in seed at full depth.
- `beck2018_multiple_attentional_templates` — argues against strict capacity-of-1; would balance the literature. Not yet in seed.
- `oberauer2002_access_wm` — Oberauer's broad-vs-narrow-focus model that anticipates the active-accessory distinction; in seed.
