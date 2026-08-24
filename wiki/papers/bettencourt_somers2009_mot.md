---
id: bettencourt_somers2009_mot
title: "Effects of target enhancement and distractor suppression on multiple object tracking capacity"
authors:
  - "Bettencourt, Katherine C."
  - "Somers, David C."
year: 2009
venue: "Journal of Vision"
doi: "10.1167/9.7.9"
arxiv: ""
url: "https://doi.org/10.1167/9.7.9"
tags:
  - visual-attention
  - psychophysics
  - working-memory
concepts:
  - attentional-spotlight
  - priority-map
  - feature-binding
  - psychometric-function
related:
  - meyerhoff2017_mot_review
  - luck_vogel1997_wm_capacity
  - awh2006_attention_wm
  - panichello_buschman2021_shared_mechanisms
  - treisman_gelade1980_feature_integration
  - bisley_goldberg2010_parietal_priority
  - bays2024_wm_representation
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_104
status: full
depth: full
last_updated: "2026-05-16"
---

# Effects of target enhancement and distractor suppression on multiple object tracking capacity

## 1. Abstract

Mounting evidence suggests that visual attention may be simultaneously deployed to multiple distinct object locations, but the constraints upon this multi-object attentional system are still debated. Results from multiple object tracking (MOT) experiments have been interpreted as revealing a fixed attentional capacity limit of 4 objects, while other evidence has suggested that attentional capacity may be more fluid. Here, Bettencourt and Somers investigated the influence of *target* stimulus factors — such as speed and size — and of *distractor filtering* factors — such as number of distractors and screen density — on MOT performance. Each factor had significant effects on capacity, producing values that ranged from above 6 objects down to one object, depending on the task demands. Although the results support the view that crowding effects modulate the effective capacity of attention, the authors also find evidence that central processes related to distractor suppression and target enhancement modulate capacity. The empirical bottom line is that MOT capacity is *not* a fixed slot count but a graded resource jointly determined by target-side gain and distractor-side suppression.

## 2. Why this matters for us

MOT is the canonical task for testing whether an attentional system can simultaneously maintain *multiple* spatial foci while tracking objects that move and intermix with visually identical distractors. The Recurrent ViT's softmax attention map can, in principle, exhibit multiple simultaneous peaks; whether it actually does so, and whether those peaks track the targets across frames, is a directly testable prediction on MOT-style stimuli. Bettencourt & Somers establish that the relevant capacity is not a hard slot ceiling but is modulated by both target-enhancement and distractor-suppression — exactly the two mechanisms that the recurrent state $H^{(t-1)}$ should learn to implement via its feedback into the attention map.

## 3. Key claims

1. **MOT capacity is not a fixed number near 4.** Depending on task parameters, capacity ranges from above 6 objects down to ~1.
2. **Target speed reduces capacity.** Faster targets are harder to track; capacity drops monotonically with speed.
3. **Target size affects capacity through crowding.** Smaller targets in dense arrays are harder to track, but the effect is partially a peripheral crowding effect rather than a pure central-attention limit.
4. **Distractor number reduces capacity even with target number fixed.** Adding distractors degrades tracking of an unchanged set of targets, implicating a distractor-suppression cost on the central attentional system.
5. **Screen density (target + distractor crowding) reduces capacity.** Capacity falls when objects are packed closer together, independent of total count.
6. **Two distinct mechanisms modulate capacity.** Target enhancement (boosting target representations) and distractor suppression (inhibiting distractor representations) are dissociable contributors, not redundant.
7. **The Pylyshyn 4-slot account is insufficient.** A fixed-pointer architecture cannot accommodate the wide range of measured capacities; a graded-resource account is needed.

## 4. Methods

**Task.** Standard MOT paradigm. Each trial begins with a static array of identical objects (typically disks). A subset (the *targets*) is briefly cued (color change). All objects then move independently along pseudo-random trajectories for several seconds. After motion ceases, one object is probed; the subject reports whether it was a target.

**Experimental factors.** Across multiple experiments, the authors orthogonally manipulated:
- *Target number* (typically 1–6).
- *Target speed* (degrees per second of visual angle).
- *Target size* (disk diameter).
- *Distractor number* (with target number held fixed).
- *Screen density* (overall packing of items in the display).

**Capacity estimation.** Capacity $K$ is computed from accuracy at each set size using the same Cowan-style formula employed in the WM literature: $K = N \cdot (h - f)$, where $N$ is targets, $h$ is hit rate, and $f$ is false-alarm rate. $K$ thus expresses the effective number of targets that the attentional system maintained throughout the trial. By estimating $K$ separately at each combination of stimulus factors, the authors construct a *capacity surface* rather than a single scalar.

**Probe procedure.** At trial end, a single probed object's identity (target vs distractor) is queried. This avoids the *response selection* confounds that arise when subjects must identify *all* targets — only the maintained representation of one randomly-chosen object is read out.

**Crowding controls.** To isolate central from peripheral contributions, the authors include conditions in which screen density is increased without changing target/distractor count (by shrinking the display) and conditions in which the count is increased without changing density (by enlarging the display). Comparing the two cleanly separates a peripheral-crowding contribution from a central-attention contribution.

**Subjects.** Young-adult human observers, viewing displays binocularly at fixed viewing distance with fixation enforced (eye position monitored).

## 5. Results

- **Capacity range.** Measured $K$ spans from >6 (slow, small, low-density displays) down to ~1 (fast, dense displays). The "magic number 4" is a single point inside this range, not a ceiling.
- **Speed effect.** Increasing target speed monotonically reduces $K$. Effect is substantial — a few-fold change in speed can halve capacity.
- **Distractor effect.** With targets held constant, adding distractors reduces $K$. This is not predicted by a pure pointer-allocation account (pointers should already be assigned and indifferent to non-targets).
- **Crowding contribution.** Part of the distractor effect tracks local spatial crowding, but a residual component survives crowding controls — implying a central (non-peripheral) suppression cost.
- **Target enhancement.** Manipulations that boost target salience (e.g., reduce target-distractor similarity) raise $K$ above the canonical 4.
- **No single bottleneck.** No single factor — number, speed, size, density — accounts for all variance; capacity is jointly determined by enhancement and suppression.
- **Crowding vs central dissociation.** When density was manipulated while count was held fixed, crowding accounted for part of the capacity drop, but a residual central effect remained after crowding was controlled — direct evidence for a non-peripheral attentional cost.
- **Target/distractor interaction is super-additive in pressure on capacity.** When both target factors (speed, size) and distractor factors (number, density) were taxed simultaneously, capacity collapsed faster than the sum of single-factor effects, consistent with a single shared resource being drained by both demands.

## 6. Critique / limitations

The paper does not directly identify the neural mechanism of target enhancement or distractor suppression; it infers them from behavior. Whether these correspond to multiplicative gain in retinotopic priority maps (Bisley & Goldberg 2010, [bisley_goldberg2010_parietal_priority](bisley_goldberg2010_parietal_priority.md)), to attentional templates in frontoparietal cortex, or to local gain in V4 cannot be distinguished from these data alone.

Capacity is operationalized via Cowan's $K$, which inherits the discrete-slot framing — even though the authors argue against fixed slots. A continuous-resource model (Bays-style precision-allocation, see [bays2024_wm_representation](bays2024_wm_representation.md)) might explain the data with a different parameterization.

The MOT paradigm uses *identical* objects, so feature-binding within a target is not tested. Whether the same capacity story would hold for featurally distinct targets (color-bound, orientation-bound) is not addressed; subsequent feature-MOT work has shown that feature-binding additionally taxes capacity.

The behavioral measure is end-of-trial accuracy. Within-trial dynamics — when in the trial the tracker is lost, or whether tracking is intermittent — are not resolved. Eye-tracking and decoding analyses in later MOT papers have shown that tracking failures are typically discrete events, not gradual decay.

No neural data are reported. The "central" vs "peripheral" dissociation is inferred from psychophysical patterns; direct fMRI or EEG correlates of the proposed enhancement / suppression mechanisms are not provided. Bettencourt's later fMRI work begins to fill this gap, but the 2009 paper is purely behavioral.

The "target enhancement" and "distractor suppression" framing is operationalized via stimulus manipulations rather than by independent neural or behavioral signatures. In principle, both could be artifacts of a single underlying gain mechanism with opposite signs at target vs distractor locations; the data here cannot strictly rule out a one-mechanism account.

The capacity formula assumes that hits and false alarms reflect a single underlying number of maintained items. Mixture models in which some trials involve full tracking and others involve guessing — analogous to the swap-and-guess decomposition in Bays-style WM models — would parse the data differently and might attribute the capacity variation to different proportions of fail-to-track trials rather than to graded resource allocation.

## 7. Connection to our work

MOT (multiple object tracking) is a paradigm where subjects covertly track 4–5 targets among visually identical distractors over several seconds of independent motion. It taxes *sustained, multi-focal* spatial attention in a way that single-target cueing tasks (Posner) do not. For the user's program, MOT is the natural psychophysical bridge between two literatures the database already integrates: visual attention (where multi-focal deployment has been controversial) and visual working memory (where the 4-item capacity limit is canonical).

**MOT capacity parallels WM capacity, and both anchor attention–WM unification.** The classical 4-item MOT capacity (Pylyshyn & Storm 1988) and the 4-item visual-WM capacity (Luck & Vogel 1997, [luck_vogel1997_wm_capacity](luck_vogel1997_wm_capacity.md); Cowan 2001) coincide numerically. Awh, Vogel & Oh 2006 ([awh2006_attention_wm](awh2006_attention_wm.md)) explicitly argues that this coincidence reflects a *shared* limited-capacity mechanism — attention and WM are not separate stores but a single capacity-limited substrate. Bettencourt & Somers extend the story: the "4" is not the right number — capacity is graded — but the *modulators* of MOT capacity (target enhancement, distractor suppression) are the same modulators that determine the precision of WM (Bays-style resource allocation, Panichello & Buschman 2021 — see [panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md)).

**MOT is a natural task for the recurrent ViT.** The recurrent ViT's task family in the published paper (2502.10955) is change detection on small numbers of stimuli; MOT is the dynamic-tracking analog, with the same load regime (≤6 targets) but with continuous motion over time. The recurrent state $H^{(t-1)}$ that the ViT maintains across frames must, on an MOT trial, *encode the identity of each target across frame-to-frame motion* — exactly the role assigned to attentional pointers / WM slots in the human literature. If the recurrent ViT can perform MOT at human-comparable capacities, that is a strong empirical demonstration that the architecture supports multi-focal attentional maintenance.

**The recurrent ViT's attention map can have multiple peaks.** Softmax over patches does not force a single argmax. The question is whether training pressure encourages multiple simultaneous peaks aligned with all targets, or whether attention collapses to a single dominant peak that scans serially. Bettencourt & Somers' result — that capacity is graded and modulated by *both* target enhancement and distractor suppression — predicts that a well-trained recurrent ViT on MOT should show (a) attention-map peaks at all targets simultaneously, (b) peak amplitude that grows with target enhancement manipulations, and (c) anti-peak (suppression) at distractor locations. These are directly testable on the model's attention maps.

**Architectural mapping.** In the user's program (see [the_user_architectural_program](../threads/the_user_architectural_program.md)), the Feedback Transformer integrates recurrent memory state into the Q/K/V projections of self-attention. On an MOT task, this is the natural substrate for both modulations: the recurrent state can boost Q/K projections at target locations (target enhancement) and dampen them at distractor locations (distractor suppression), via the per-state $c^{(k)}_q, c^{(k)}_k$ contributions that broadcast prior to softmax. Bettencourt & Somers' dissociation of enhancement and suppression as *separable* mechanisms maps cleanly onto the architectural prediction that distinct memory channels (or distinct hubs) might contribute positively (targets) and negatively (distractors) to the same attention competition.

**Capacity is graded, not slotted — supports a continuous-state recurrent memory.** Bettencourt & Somers' core empirical message is that MOT capacity is not a fixed integer. The recurrent ViT's continuous-valued memory state is, structurally, a *graded* resource — capacity is not architecturally bounded at 4 — which is more compatible with the Bettencourt & Somers picture than with strict Pylyshyn pointers. This is a point of consonance: the empirical psychophysics and the model's representational format both reject hard slots.

**A predicted manipulation in silico.** Following Bettencourt & Somers' factorial design, a recurrent-ViT MOT experiment should orthogonally vary target speed, target size, distractor number, and screen density, and measure the network's tracking accuracy. If the network shows the same qualitative pattern (capacity falling with speed and density, dissociable target / distractor effects), that is positive evidence that the architecture's attentional dynamics share the human signatures.

**Connection to priority-map accounts.** Bisley & Goldberg's parietal priority map ([bisley_goldberg2010_parietal_priority](bisley_goldberg2010_parietal_priority.md)) is the leading neural account of how multi-focal attention is encoded — a single retinotopic map with simultaneous local peaks at target locations. Bettencourt & Somers' enhancement / suppression dissociation maps cleanly onto positive and negative modulations of this map. The recurrent ViT's attention map is itself a priority-map-like object; modeling its dynamics on MOT therefore lets the user's program engage directly with the parietal-priority-map literature without having to commit to a separate "tracker" mechanism.

**Why MOT is the right next benchmark.** The user's published change-detection task uses small numbers of static stimuli per frame; it stresses *binding and maintenance* but not *simultaneous tracking under motion*. MOT preserves the small-N regime (within the WM capacity range that Luck & Vogel established and that the architecture can plausibly support) but adds two dimensions the published work cannot test: continuous-time motion, and the need to maintain *multiple* discriminable foci across frames. Bettencourt & Somers' factorial design provides a ready-made battery of conditions under which the architecture should be probed — and provides quantitative human capacity values against which the architecture's behavior can be calibrated, not just compared qualitatively.

## 8. Citations to follow

- `pylyshyn_storm1988_mot` — original MOT paper; FINST pointer model. Not in seed; should be added as the foundational MOT citation.
- `alvarez_franconeri2007_flexible_resource` — flexible-resource MOT account, directly bearing on graded capacity. Not in seed.
- `cavanagh_alvarez2005_tracking_attention` — review on multi-focal attentional tracking. Not in seed.
- `scholl_pylyshyn1999_tracking_objects` — what makes a "tracked object". Not in seed.
- `bisley_goldberg2010_parietal_priority` — parietal priority map underlying multi-focal selection. In seed.
- `franconeri2013_flexible_cognitive_resources` — generalized flexible-resource account. Not in seed.
- `intriligator_cavanagh2001_spatial_resolution_attention` — spatial-resolution limits on attention; complements crowding story. Not in seed.
