---
id: funahashi1989_mnemonic_dlpfc
title: "Mnemonic coding of visual space in the monkey's dorsolateral prefrontal cortex"
authors:
  - "Funahashi, Shintaro"
  - "Bruce, Charles J."
  - "Goldman-Rakic, Patricia S."
year: 1989
venue: "Journal of Neurophysiology"
doi: "10.1152/jn.1989.61.2.331"
arxiv: ""
url: "https://journals.physiology.org/doi/10.1152/jn.1989.61.2.331"
tags:
  - primate-neurophysiology
  - prefrontal-cortex
  - working-memory
concepts:
  - working-memory-persistent-activity
  - topographic-organization
  - gain-modulation
  - multi-compartmental-memory
related:
  - goldman_rakic1995_cellular_wm
  - constantinidis2018_persistent_activity
  - riley_constantinidis2016_pfc_persistent
  - miller_cohen2001_pfc_function
  - mante2013_context_dependent_pfc
  - desimone1996_visual_memory_attention
  - vijayraghavan_everling2021_muscarinic_wm
  - tallec_ollivier2018_chrono_init
relevance_to:
  - prism_v1
  - prism_v2
  - recurrent_vit
seed_source:
  - thesis_md
  - prism_v2_proposal
status: full
depth: full
last_updated: "2026-05-16"
---

# Mnemonic coding of visual space in the monkey's dorsolateral prefrontal cortex

## 1. Abstract

Funahashi, Bruce & Goldman-Rakic recorded from 288 neurons in and around the principal sulcus of the dorsolateral prefrontal cortex (DLPFC) of macaques performing an *oculomotor delayed-response* (ODR) task. The monkey fixated a central point while a brief (0.5 s) visual cue appeared at one of eight peripheral locations (separated by 45°), held fixation through a 1–6 s memory delay during which the cue was no longer visible, and then made a saccade to the remembered location when the fixation point disappeared. Of the 288 principal-sulcus neurons, 170 were task-related and **87 showed significant change in firing during the delay period** — i.e., sustained activity in the absence of the eliciting stimulus, while the animal held the location in memory. **79 % of these delay-active cells had directional ("mnemonic") tuning**: they fired strongly only when the to-be-remembered location lay in a restricted region of the visual field — the cell's "memory field" — and weakly or not at all for other locations. Tuning was preserved across delay durations of 1–6 s, and errors made by the monkey correlated with disruption of the cell's directional delay activity. The paper is the foundational demonstration that DLPFC neurons encode the *content* of spatial working memory in their sustained firing rate during a delay, and that this code is organised retinotopically into discrete memory fields — the cellular substrate of working memory.

## 2. Why this matters for us

This is the founding experimental paper for the concept of **persistent delay-period activity as the neural substrate of working memory**. Every recurrent architecture in the user's program — the Recurrent ViT's hidden state $H^{(t)}$, PRISM v1's ConvGRU memory cell $M_t$, PRISM v2's slow/fast dual memory, the GridCell RNN's stack of $C_i^{(t)}$ states — is a computational descendant of the mechanism Funahashi et al. characterised in DLPFC. The paper supplies three load-bearing facts for the user's architectural commitments: (1) working memory is implemented by **sustained firing during a stimulus-free delay**, supporting the design choice of a recurrent state carried across time without explicit re-presentation of the stimulus; (2) the maintained code is **spatially tuned** — each cell has a memory field — supporting PRISM v1's choice to maintain a spatially-organised $M_t$ rather than a single flat vector; (3) tuning is **mnemonic, not perceptual** — the same cell fires during the delay only for its preferred remembered location, so the activity carries content rather than reflecting the now-absent stimulus, supporting the framing of recurrent activity as task-relevant maintenance rather than as image residue. The paper is also the empirical anchor for the *working-memory compartment* of the user's multi-compartmental memory framework.

## 3. Key claims

1. **DLPFC neurons exhibit sustained activity during a memory delay** in the absence of the eliciting stimulus — the cellular signature of working memory.
2. **The majority of delay-active cells are directionally selective**: 79 % have a preferred direction (a "memory field") and a corresponding anti-preferred direction.
3. **Memory fields tile visual space**: across the recorded population the preferred directions cover all eight tested cue locations, providing a topographic code for remembered position.
4. **Delay activity persists across long delays** (1–6 s) without decaying to baseline, indicating an active maintenance process rather than passive sensory decay.
5. **Errors correlate with breakdown of delay activity**: on trials where the monkey made an incorrect saccade, the cell's delay-period firing was reduced or absent at its preferred location, linking the maintained representation causally to behaviour.
6. **Distinct cue, delay, and response sub-populations exist**: many cells are tuned only during the cue, only during the delay, or only during the saccade; some span multiple epochs. Roughly half of delay cells have *only* delay-period tuning and are silent during cue and response.
7. **Both excitatory and inhibitory delay tuning are observed**: of the 87 delay cells, 50 showed increased firing for the preferred direction (92 % directional) and 37 showed pure inhibition (62 % directional); 15 cells combined excitatory tuning for one direction with inhibitory tuning for another, suggesting a push-pull "Mexican hat" organisation in memory space.
8. **Mnemonic activity dissociates from sensory and motor coding**: control runs with a visually-guided saccade task — same eye-movement endpoints, no memory requirement — eliminate the directional tuning in most delay-active cells, demonstrating that the code reflects the *remembered* location rather than either the seen cue or the planned eye movement.

## 4. Methods

**Task — the oculomotor delayed-response (ODR) paradigm.** The monkey fixated a central fixation point. A peripheral cue was flashed for 0.5 s at one of eight locations on a circle centred on fixation, the eight locations equally spaced at 45° intervals. The cue then disappeared and the monkey continued to fixate centrally for a delay of 1, 3, or 6 s. When the fixation point was extinguished, the monkey was required to make a single saccade to the remembered cue location and was rewarded for accuracy. Critically, during the delay the screen was blank, so the monkey could not solve the task by reading off the current visual input; success required active maintenance of the cue location across the delay. The use of the *same* response (a saccade) for all eight cued directions ensures that motor preparation alone cannot account for the directional code — the saccade plan is identical until the moment of execution.

**Recording.** Single-unit extracellular recordings were obtained from neurons in and around the principal sulcus of DLPFC in two macaques (Brodmann area 46 / 9–46). 288 isolated units were recorded with tungsten microelectrodes through chronic recording chambers, with histological reconstruction confirming the principal-sulcus locus. 31 additional units were recorded in the frontal eye fields as a control population. Eye position was monitored with a magnetic search coil so that fixation breaks could be excluded from analysis.

**Analysis.** Each cell's firing rate was binned within the three task epochs — cue, delay, and saccadic response — and compared statistically to a pre-trial baseline period. A cell was classified as "delay-active" if its mean firing rate during the delay differed significantly from baseline for at least one of the eight cue directions. Direction tuning was assessed by ANOVA across the eight cue locations; cells with a significant effect of direction during the delay were classified as **directional** ("memory-field" cells). The preferred direction was taken as the cue location yielding the strongest delay response; the memory-field width was assessed by the spread of significant responses across adjacent directions. To rule out a perceptual or motor confound, the authors compared each cell's delay tuning against tuning measured during a *visually-guided* saccade control task (in which the target stayed visible during the "delay"); cells with bona fide mnemonic coding are those tuned in ODR but not in the visually-guided control.

**Error analysis.** Trials in which the monkey made an incorrect saccade (to a location other than the cued one) were separated from correct trials. For directional delay cells, the firing rate during the delay on error trials at the preferred direction was compared to the firing rate on correct trials at the preferred direction. This is the central single-cell behavioural-linking analysis of the paper.

## 5. Results

- **Sample composition.** Of 288 principal-sulcus neurons, **170 (≈59 %) were task-related** in at least one task epoch. **87 (≈30 % of total; ≈51 % of task-related)** showed significant delay-period modulation.
- **Directionality.** Of the 87 delay cells, **79 % (69 cells) were directional** — their delay response differed significantly across the eight cue locations. The remaining **21 % (18 cells) were "omnidirectional"** — they fired during the delay regardless of cue location, suggesting a non-spatial "delay" or attention/effort signal rather than a content code.
- **Sign of modulation.** 50 of 87 cells showed excitatory delay responses above spontaneous baseline; of these, **92 % were directional**. 37 of 87 showed pure inhibitory delay responses; of these, **62 % were directional, 38 % omnidirectional**. **15 cells exhibited excitatory tuning for one preferred direction and inhibitory tuning for the opposite direction**, the clearest single-cell evidence for a centre-surround organisation in memory space analogous to a visual receptive field's centre-surround organisation.
- **Memory-field structure.** Memory-field widths were typically ≈90°–135° at half-maximum, with the firing rate falling off systematically as the cue moved away from the preferred direction. The eight preferred directions were approximately uniformly distributed across the recorded population, giving a topographic code that spans the full visual field — every direction was represented by at least one tuned cell, and no direction was systematically over- or under-represented.
- **Visually-guided control.** Cells with delay-period tuning in ODR generally lacked tuning in the visually-guided control task, confirming that the delay activity reflects *mnemonic* coding of an absent stimulus rather than a continuing sensory or motor signal.
- **Persistence across delay durations.** Sustained activity was maintained throughout the entire delay at all three tested durations (1, 3, 6 s) without monotonic decay. Some cells showed phasic onsets at the cue, sustained activity during the delay, and phasic offsets at the response — i.e., the activity was structured by task epoch, not merely by stimulus echo.
- **Error correlation.** On trials in which the monkey saccaded to an incorrect location, the directional delay-period firing of cells tuned for the *correct* cue direction was significantly reduced, often falling to baseline. This is the central behavioural-neural linking finding: when the cell's memory representation fails, so does the behaviour.
- **Epoch dissociation.** Cells with delay-only tuning (silent at cue and response) constituted a substantial fraction of the delay-active population, demonstrating that the maintained representation is not a simple persistence of the visual response.

## 6. Critique / limitations

- The eight-location, single-cue design isolates *spatial* working memory; the same architecture may support different content domains (objects, features, rules), and how memory fields combine across content dimensions is left for later work (Wilson, Ó Scalaidhe & Goldman-Rakic 1993; Rao, Rainer & Miller 1997).
- The paper is **correlational at the single-cell level**. The link to behaviour comes only from the error-trial analysis; causal demonstrations awaited pharmacological inactivation (Funahashi, Bruce & Goldman-Rakic 1993) and dopaminergic-modulation studies (Williams & Goldman-Rakic 1995; Vijayraghavan et al. 2007). The 1989 paper does not establish that disrupting delay activity *causes* memory failure, only that the two co-vary.
- The "persistent activity" interpretation has been challenged by later population-level analyses showing that maintained information can ride on **dynamic** trajectories in which no single cell fires persistently — the activity propagates through the network rather than parking in one population (Stokes 2015; Lundqvist et al. 2016). The 1989 paper interprets sustained single-cell firing as the substrate of memory, and is silent on dynamic-coding alternatives.
- The recordings are restricted to DLPFC; subsequent work has shown that delay activity exists in parietal cortex (Gnadt & Andersen 1988), inferior temporal cortex (Miller, Erickson & Desimone 1996), and frontal eye fields. The 1989 paper cannot speak to where the maintenance "originates" or how distributed it is.
- The delay durations tested (≤6 s) are short relative to behavioural working-memory spans; whether the same mechanism scales to tens of seconds, or whether longer maintenance requires additional substrates (consolidation into hippocampus / cortex), is outside the paper's scope.
- The analysis is by hand-classified epochs and ANOVA on firing rates. Modern population analyses (state-space, decoding, RSA) would extract additional structure invisible to single-cell statistics — including the dynamic-coding signatures noted above.
- The role of *distractors* during the delay is untested. Real working memory must resist interference; the 1989 ODR delay is empty, so robustness to distraction — a property the user's architecture must also exhibit — cannot be assessed from this paper alone (subsequent work: di Pellegrino & Wise 1993; Miller, Erickson & Desimone 1996).
- The recordings sample firing rates only. Whether the same memory is also encoded in spike timing, LFP phase, or cross-area coherence is left untouched — and is precisely the alternative axis along which dynamic-coding and oscillation-based accounts later challenged the persistent-activity picture.

## 7. Connection to our work

This paper is the empirical foundation for **the working-memory compartment of the user's multi-compartmental memory framework** (`threads/the_user_architectural_program.md` §3) and for **the choice to carry a recurrent hidden state across timesteps without re-presenting the stimulus** in the Recurrent ViT (`Prism/docs/THESIS.md` and the 2502.10955 paper).

**Persistent activity → recurrent hidden state.** The user's program treats each layer's recurrent state $C_i^{(t)}$ as a continuously-maintained representation that bridges temporal gaps between sensory inputs. Funahashi 1989 is the canonical neural correlate: the DLPFC cell's delay-period firing is the biological instantiation of $C_i^{(t)}$ during the moment between cue and response. The Recurrent ViT's $H^{(t)}$ (paper §3) and PRISM v1's ConvGRU memory cell $M_t$ (`THESIS.md` §2.4) are computational analogues — each maintains task-relevant content across timesteps in the absence of the eliciting stimulus, exactly as Funahashi's principal-sulcus neurons do across the ODR delay. The 1–6 s persistence with no monotonic decay is the empirical license for choosing a memory state that does *not* decay to baseline absent input, i.e., for gating mechanisms (LSTM/GRU/ConvGRU) that can hold information indefinitely rather than leaky integrators.

**Memory fields → spatially-organised working memory.** Funahashi et al. demonstrate that the DLPFC code is **topographic**: each cell has a preferred location and the population tiles visual space. This directly supports PRISM v1's commitment to a **spatially-organised** memory $M_t \in \mathbb{R}^{H \times W \times C}$ (`THESIS.md` §2.4) — not a flat vector — and to the GridCell RNN's grid structure ($C_i^{(t)} \in \mathbb{R}^{n_{gh} \times n_{gw} \times n_{C_i}}$, `threads/the_user_architectural_program.md` §2). The same topographic logic — *the location of activity carries the location of the remembered content* — operates in both the cortical population and the user's grid of recurrent units.

**Push-pull memory fields → multiplicative / additive feedback.** The 15 cells with excitatory tuning at one direction and inhibitory tuning at the opposite direction implement a centre-surround organisation in memory space. This is the cellular analogue of the **multiplicative-feedback** variant of the Feedback Transformer (`threads/the_user_architectural_program.md` §1; Recurrent ViT §6.7): a feedback signal that selectively amplifies content matching a preferred memory state and suppresses content matching a competing one. The "memory field with surround" structure validates the architectural choice of multiplicative rather than purely additive feedback for memory-driven modulation.

**Mnemonic vs perceptual coding → content carried by recurrence, not by stimulus residue.** Funahashi's delay-only cells fire *only* during the delay, not during the cue or the response. The maintained activity is therefore not an after-image of the sensory drive — it is task-relevant content held aloft by the network's internal dynamics. This directly supports the user's interpretive framing (`THESIS.md` and `PRISM_V2_PROPOSAL.md`) that the recurrent state $M_t$ holds **task-relevant predictions** about the world, not a copy of the last frame. PRISM v1's interpretation of $M_t$ as the network's running model of the scene — distinct from any specific frame — is the computational analogue of Funahashi's delay-only memory cells.

**Foundational for the multi-compartmental memory framework.** The user's program (§3) commits to multiple parallel recurrent compartments with potentially different timescales: a fast iconic-memory compartment, a working-memory compartment, and (in PRISM v2) a slow consolidation compartment. Funahashi 1989 is the empirical anchor for the **middle compartment** — the seconds-scale spatially-organised working memory implemented by DLPFC. The fast compartment maps onto iconic / V1-level persistence (Sperling 1960); the slow compartment maps onto hippocampal / association-cortex consolidation (Constantinidis & Klingberg 2016; Riley & Constantinidis 2016, already in seed). Funahashi 1989 occupies the centre of this three-compartment scheme and is the most-cited single empirical reference for any architecture claiming biological grounding for a working-memory state.

**Error-trial linking → behavioural validation of the recurrent state.** The result that errors correlate with degraded delay activity is the empirical model for **using the recurrent state as a behavioural read-out**. In the Recurrent ViT and PRISM, change-detection accuracy is read directly off $H^{(t)}$ / $M_t$; the user's interpretation is that this state holds the task-relevant comparison. Funahashi's finding that *when the cell's delay activity collapses, the monkey errs* is the cleanest possible neural analogue of "when the recurrent state degrades, the model's task performance degrades" — a prediction that should be directly testable by ablating or perturbing $M_t$ during sustained tasks.

**Dual-timescale gating → PRISM v2's slow/fast pathway.** Funahashi's delay durations span only 1–6 s, well within the working-memory timescale, but the absence of decay over a 6× variation in delay imposes a constraint on the gating mechanism: it must be temperature-flat across this range. PRISM v2's slow-memory pathway (`PRISM_V2_PROPOSAL.md` §3.3) implements an analogous flat-retention regime by chrono-initialisation of forget-gate biases (Tallec & Ollivier 2018), giving the slow compartment a time-constant much longer than the fast compartment. Funahashi 1989's flat persistence across 1–6 s is the cellular justification for this architectural commitment, and motivates further tests with much longer delays.

**Distinct cue / delay / response sub-populations → factorised recurrent state.** The 1989 finding that many cells are tuned in *only* one of the three task epochs (cue, delay, or saccade) implies that the DLPFC population factorises representations across functional roles. The user's program (`PRISM_V2_PROPOSAL.md` §3) commits to multiple parallel recurrent units rather than a single monolithic state. A natural mapping is: PRISM's *prediction* state ↔ Funahashi's delay-only cells; its *error / drive* signal ↔ Funahashi's cue-only cells; its *action / readout* head ↔ Funahashi's response-only cells. The empirical existence of these functional sub-populations within a single cortical area validates the architectural choice of multiple specialised compartments inside one "memory" module.

## 8. Citations to follow

- `goldmanrakic1987_circuitry_pfc` — Goldman-Rakic 1987 *Handbook of Physiology* chapter on PFC circuitry; the anatomical companion to the 1989 physiology. Not yet in seed.
- `fuster_alexander1971_neuron_activity_delayed_response` — Fuster & Alexander's earlier (1971) demonstration of delay-period activity in PFC, the direct predecessor of the 1989 paper. Not yet in seed.
- `funahashi_bruce_goldmanrakic1993_dlpfc_inactivation` — the 1993 follow-up using local cooling to establish causal necessity of DLPFC delay activity for ODR performance. Not yet in seed.
- `williams_goldmanrakic1995_d1_wm` — D1-receptor modulation of DLPFC delay activity; bridges to dopaminergic gating relevant to PRISM v2's RL-gated memory. Not yet in seed.
- `vijayraghavan2007_d1_inverted_u` — the inverted-U D1 dose-response on DLPFC persistent activity. Partial via `vijayraghavan_everling2021_muscarinic_wm`; the 2007 paper itself not yet in seed.
- `miller_erickson_desimone1996_neural_mechanisms_wm` — IT-cortex object-memory analogue of Funahashi spatial-memory cells; key for generalising memory-field framework to non-spatial content. Not yet in seed.
- `wilson_oscalaidhe_goldmanrakic1993_dissociation_pfc` — dorsal-vs-ventral PFC dissociation of spatial vs object working memory. Not yet in seed.
- `gnadt_andersen1988_lip_delay` — parietal LIP delay activity, showing that spatial WM is distributed beyond PFC. Not yet in seed.
- `stokes2015_activity_silent_wm` — challenges pure persistent-activity framing with synaptic / dynamic-coding alternatives. Not yet in seed.
- `lundqvist2016_gamma_pfc_wm` — bursty / dynamic delay-period gamma in PFC; revises the "tonic firing" picture toward a discrete-events one. Not yet in seed.
- `compte2000_attractor_wm` — Compte, Brunel, Goldman-Rakic & Wang network model of bump-attractor working memory built explicitly on Funahashi memory fields. Not yet in seed.
- `wang1999_synaptic_basis_wm` — Xiao-Jing Wang's NMDA-based account of persistent activity. Not yet in seed.
- `sperling1960_iconic_memory` — the foundational iconic-memory paper; the fast compartment in the user's three-compartment scheme. Not yet in seed.
- `dipellegrino_wise1993_pfc_distractor` — distractor-resistance of PFC delay activity; tests whether memory fields survive interference. Not yet in seed.
- `tallec_ollivier2018_chrono_init` — chrono-initialisation of forget-gate biases for long-timescale RNN retention; already cited in `PRISM_V2_PROPOSAL.md` §3.3. In seed, full depth.
