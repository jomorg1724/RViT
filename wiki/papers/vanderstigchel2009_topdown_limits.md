---
id: vanderstigchel2009_topdown_limits
title: "The limits of top-down control of visual attention"
authors:
  - "Van der Stigchel, Stefan"
  - "Belopolsky, Artem V."
  - "Peters, Judith C."
  - "Wijnen, Jasper G."
  - "Meeter, Martijn"
  - "Theeuwes, Jan"
year: 2009
venue: "Acta Psychologica"
doi: "10.1016/j.actpsy.2009.07.001"
arxiv: ""
url: "https://doi.org/10.1016/j.actpsy.2009.07.001"
tags:
  - visual-attention
  - psychophysics
  - review
concepts:
  - top-down-feedback
  - attentional-spotlight
  - saliency-models
  - priority-map
  - attentional-template
related:
  - gilbert_li2013_topdown
  - baluch_itti2011_topdown_mechanisms
  - gazzaley_nobre2012_topdown
  - miller_cohen2001_pfc_function
  - lamy2006_grouping_no_attention
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_101
status: full
depth: full
last_updated: "2026-05-16"
---

# The limits of top-down control of visual attention

## 1. Abstract

The extent to which spatial selection is driven by the goals of the observer and by the properties of the environment is one of the major issues in the field of visual attention. The authors review recent experimental evidence from behavioral and eye-movement studies suggesting that top-down control has temporal and spatial limits. More specifically, they argue that the first feedforward sweep of information is bottom-up, and that top-down control can influence selection only after the sweep is completed. In addition, top-down control can limit spatial selection through adjusting the size of the attentional window — an area of visual space which receives priority in information sampling. Finally, the authors discuss the evidence found using brain imaging techniques for top-down control in an attempt to reconcile it with behavioral findings. They conclude by discussing the theoretical implications of these results for current models of visual selection.

## 2. Why this matters for us

Van der Stigchel et al. 2009 is the most-cited statement of the *constraint side* of top-down attention research, and it is the empirically grounded counterpoint to the modulation-everywhere picture catalogued in `gilbert_li2013_topdown`. The review's central commitments — that the first feedforward sweep is essentially bottom-up, that top-down control acts only afterwards, and that observers' main top-down lever is the *size of an attentional window* rather than fine-grained re-tuning of every V1 cell — bear directly on the user's architectural program (`the_user_architectural_program.md`). They impose three concrete constraints on what the Feedback Transformer can plausibly modulate: feedback cannot retro-act on the initial bottom-up sweep, the most stable top-down signal is a spatial-scale / spatial-extent parameter rather than feature-by-feature gain, and any model whose top-down pathway dominates the first pass risks contradicting two decades of capture and singleton-search results.

## 3. Key claims

1. The first feedforward sweep of visual information is overwhelmingly bottom-up; top-down signals are too slow to influence the initial selection of which location wins the priority map within roughly the first 100–150 ms of stimulus onset.
2. Top-down control nevertheless exists, but is best characterised as operating *after* the feedforward sweep has computed an initial salience landscape — by gating which selected information is processed further, sustained, or acted upon.
3. The most robust top-down lever observers have over spatial selection is the *size of the attentional window*: the region of visual space that receives priority in sampling. A small window suppresses extra-window distractors; a large window exposes the observer to capture.
4. Within the attentional window, selection is driven primarily by bottom-up salience — even highly motivated, well-instructed observers cannot prevent capture by a salient irrelevant singleton if it falls inside the window they have set.
5. Behavioral evidence (eye-movement deviations, oculomotor capture, contingent capture, additional-singleton paradigm) and neuroimaging evidence (pre-stimulus baseline shifts, biased baseline activity in retinotopic visual cortex driven by FEF/parietal cuing) are reconcilable once the temporal asymmetry is respected: imaging picks up the *preparatory* and *post-selection* phases where top-down signals dominate, while psychophysics indexes the *selection moment itself* where bottom-up signals win.
6. Existing models of visual selection (Wolfe's Guided Search; Theeuwes's stimulus-driven account; Bundesen's TVA; Desimone & Duncan biased competition) all need to incorporate temporal and spatial bounds on top-down influence to remain consistent with the full pattern of data.
7. Pure stimulus-driven accounts (no top-down at all) and pure top-down accounts (selection is fully under intentional control) are both empirically untenable; the data demand an intermediate position in which top-down signals operate only at specific times (after the sweep) and through specific levers (window size, baseline gain) rather than as a global override of bottom-up drive.
8. Cortical and subcortical sources of top-down bias — FEF, parietal cortex, pulvinar, dorsolateral PFC — operate on a slower time course than the feedforward sensory pathway and are most naturally read as setting *priors* on subsequent processing rather than gating the current sweep.

## 4. Methods

This is a narrative review with no new empirical data. The authors synthesize behavioral, eye-movement, and neuroimaging results from roughly fifteen years of visual-attention research, with particular weight on work from the Theeuwes / Belopolsky group at Vrije Universiteit Amsterdam and from the Posner-cuing and oculomotor-capture literatures. The review is organised around three claims and the evidence for them: (a) the feedforward sweep is bottom-up; (b) top-down control adjusts the size of an attentional window; (c) neuroimaging top-down signatures are reconcilable with behavioral capture once timing is accounted for. The paradigms most heavily cited are: the additional-singleton paradigm (Theeuwes 1992, 1994); oculomotor-capture paradigms with saccade-deviation read-outs (Van der Stigchel & Theeuwes 2006); contingent-capture paradigms (Folk, Remington & Johnston 1992); the global-local paradigm (Navon 1977); pre-cuing of attentional window size (Belopolsky, Theeuwes, et al.); and fMRI / TMS studies of FEF and parietal preparatory activity (Kastner, Corbetta, Moore, Ruff). The review's theoretical move is to insist on a temporal decomposition — feedforward sweep first, top-down adjustment after — that the authors argue dissolves the apparent contradiction between "attention is top-down" (imaging) and "attention is captured" (behavior).

The argumentative structure is worth tracking explicitly. The authors first establish the bottom-up sweep claim with reaction-time and saccade-latency data showing that capture by salient singletons occurs within the time window of the first sweep and cannot be prevented by instruction. They then introduce the attentional-window construct as the principal top-down lever that *can* be set ahead of the sweep, and review pre-cuing studies showing that window size predicts capture rate. They then turn to neuroimaging and TMS evidence and argue that these techniques pick up either (a) the preparatory baseline-shift phase (FEF/parietal cuing before stimulus onset) or (b) the post-sweep modulation phase (gain changes in extrastriate cortex after ~150 ms), neither of which is the moment of initial selection. The temporal-decomposition argument is therefore the keystone: behavioral capture, imaging-detected top-down signals, and the attentional-window construct are all simultaneously true if one allows that "top-down attention" denotes different operations at different latencies relative to stimulus onset.

## 5. Results

The review's empirical synthesis yields several quantitative anchors:

- **Feedforward sweep timing.** Visually evoked responses reach V1 within ~50 ms of stimulus onset and propagate through the ventral stream within ~100–150 ms. Top-down signals from frontal / parietal sources are too slow to shape the initial wave; their measurable effects on extrastriate responses arrive later, in the ~150–300 ms window.
- **Oculomotor capture is involuntary.** In the additional-singleton paradigm, a task-irrelevant colour singleton produces saccade-capture rates of roughly 30–50% even when observers are explicitly told to ignore it. The effect is robust across instructions, practice, and reward manipulations.
- **Attentional window size is a real, parametric, top-down lever.** When observers are pre-cued to attend to a small region, capture by extra-region singletons drops sharply; when cued to attend broadly (or under load that defocuses the window), capture returns. The effect scales monotonically with manipulated window size.
- **Within-window selection is bottom-up.** Once two stimuli fall inside the same attentional window, the more salient one wins regardless of observer intent. This is the result that the authors treat as the cleanest demonstration of the limit on top-down control.
- **Saccade-deviation signatures.** Endogenously cued attention deviates saccade trajectories away from the cued location — a measurable, sub-degree trajectory effect — supporting the existence of top-down spatial biases, but the timing of these deviations follows rather than precedes initial fixation programming.
- **Neuroimaging baseline shifts.** Pre-stimulus baseline activity in retinotopic visual cortex (V1–V4) shifts with attentional cuing, in the order of 10–30% above unbiased baseline (Kastner et al.). The authors take this as evidence for the *preparatory* role of top-down signals — biasing the priority map *before* the feedforward sweep — rather than as evidence that the sweep itself is top-down driven.
- **Inactivation studies.** FEF microstimulation and parietal-cortex disruption (TMS or lesion) modulate the size and gain of attentional effects but do not abolish bottom-up capture, consistent with top-down sources biasing rather than overriding the bottom-up sweep.
- **Eye-movement deviations as a window read-out.** Saccade trajectories curve *away from* endogenously cued locations and *toward* highly salient irrelevant singletons. The double dissociation — top-down cuing produces curvature-away, bottom-up salience produces curvature-toward — gives a clean per-trial behavioral index of the relative weight of top-down and bottom-up signals on a single saccade, and supports the claim that both signals operate but on different time courses.
- **Global vs local pre-cuing.** Pre-cuing observers to attend globally (Navon-style) makes them faster on global targets but more susceptible to distractor capture from anywhere in the display; local pre-cuing has the reverse effect. This is one of the strongest demonstrations that the *spatial scale* of attention is the parameter under top-down control, not the per-feature selectivity within that scale.
- **Reward and selection history.** Even reward-driven modulation, often treated as the cleanest case of top-down control, fails to override bottom-up capture when the rewarded feature falls outside the current attentional window — supporting the review's claim that the window-size lever is upstream of feature-based top-down biases.

The composite picture is that top-down attention is real, anatomically localised, and quantitatively measurable, but it is bounded in three ways: temporally (it cannot pre-empt the initial sweep), spatially (it operates by adjusting a window rather than by precise selection within it), and competitively (within the window, salience wins). All three bounds are robust across paradigms, observers, and (with appropriate caveats) species — a body of evidence the review treats as collectively decisive.

## 6. Critique / limitations

The review is partisan. The authors are members of the Theeuwes group, which has spent two decades defending a stimulus-driven account against contingent-capture and signal-suppression accounts (Folk et al.; Bacon & Egeth). The choice of paradigms and the framing of "limits" reflect that program. A reader coming from the Awh / Vogel / Gaspelin tradition (which Van der Stigchel et al. do not engage in depth) would interpret the same data as evidence for *learned* top-down suppression of irrelevant singletons — i.e., the limits the review identifies might be limits on *unlearned* top-down control, not on top-down control in general. Awh, Belopolsky & Theeuwes (2012) — written partly by the same author — eventually argues that the top-down / bottom-up dichotomy is a failed theoretical frame and selection history matters more than either, weakening some of the present review's stronger commitments.

The temporal-sweep argument leans heavily on the assumption that the first ~100–150 ms is unmodulated by top-down signals. Subsequent work using closed-loop mouse-V1 paradigms (Keller, Bonhoeffer & Hübener 2012; Attinger et al. 2017), pre-stimulus baseline-shift studies in primate V4 (Reynolds & Chelazzi 2004), and Gilbert-lab task-dependent V1 tuning (`gilbert_li2013_topdown` §3) have all complicated this assumption: top-down signals can pre-set baseline activity *before* the feedforward sweep, so the sweep is not innocent of top-down context even when it cannot be retro-modulated during the sweep itself. The review acknowledges Kastner-style baseline shifts but interprets them as preparatory rather than as evidence against the feedforward-sweep-is-bottom-up claim.

The "attentional window" construct is operationally defined by manipulations rather than mechanistically pinned down. The review does not commit to where in the brain the window is represented, what its neural correlates are, or how its size is set. This makes the construct flexible enough to absorb a wide range of results but harder to falsify than the competing fine-grained-modulation accounts (Gilbert & Li; Reynolds-Heeger normalization). Subsequent work (Belopolsky & Theeuwes 2010 and successors) has tried to give the window a more mechanistic grounding through saccade-trajectory and oculomotor-priority data, but a fully circuit-level account is still lacking.

The review also leaves under-specified the dynamics by which the window is re-sized between sweeps. If the principal top-down operation is to set the window before the next sweep, then the time course of window-resizing — how quickly observers can adjust focus, whether resizing requires an eye movement, whether the window can be split into multiple foci — becomes a critical empirical target the review does not directly address.

A further limitation is that the review's "attentional window" is operationalised primarily through cuing manipulations and global/local pre-cues, and the size scale it claims is set top-down is not cleanly separable from spatial-attention models in which the gradient of attentional priority around a focus point is itself the modulated variable (Reynolds-Heeger normalization; the "Mexican hat" surround-suppression accounts). The window may therefore be a re-description of the same priority-map mechanism the authors elsewhere treat as bottom-up; the empirical content of "window-size is the top-down lever" is somewhat closer to "the spatial-extent parameter of a priority map is set top-down" than the framing suggests.

Finally, the review is silent on computational implementation. It tells us *what* top-down control can and cannot do behaviorally; it does not tell us *how* — in circuit or model terms — those limits arise. The temporal bound (top-down cannot act within the first ~150 ms) is consistent with the conduction-delay budget of long-range corticocortical feedback loops but the review does not commit to that account. This is the gap a computational model of recurrent attention can either respect (by adopting the temporal/spatial bounds explicitly through architectural choices like per-timestep recurrence) or quietly violate (by giving top-down feedback unrestricted access to first-pass processing within a single sweep).

## 7. Connection to our work

Van der Stigchel et al. 2009 functions in this database as the *boundary-condition counterpart* to `gilbert_li2013_topdown`, and the contrast between the two is what makes both load-bearing for the user's program.

**(i) Boundary conditions on the Feedback Transformer.** The Feedback Transformer (`the_user_architectural_program.md` §1) admits arbitrary recurrent feedback into the Q/K/V projections of self-attention at every layer, including patch-level (V1-analog) layers. Taken naively, this could be read as committing the architecture to *first-pass* top-down dominance — exactly the picture this review argues against. The principled reading, given Van der Stigchel et al., is that the first forward pass of the network corresponds to the feedforward sweep, during which the recurrent feedback state $H^{(t-1)}$ is *the previous timestep's* representation, not a within-pass top-down signal. The Recurrent ViT's recurrence-over-timesteps is therefore consistent with the review: top-down (in the form of $H^{(t-1)}$) biases the priority map *before* the next sweep begins, exactly as Kastner-style pre-stimulus baseline shifts do, and shapes processing on later sweeps rather than retro-acting on the current one. The iterative encoder ($n_{FR}$ forward-reasoning steps; `the_user_architectural_program.md` §4) is best read in the same way: each pass is a fresh feedforward sweep biased by the accumulated state from prior passes.

This reading does have an architectural cost: it implies that any single-pass instance of the program (e.g., a single-step Recurrent ViT applied to a still image with no prior $H$) is genuinely incapable of exhibiting top-down modulation — which is the empirically correct prediction given the review. The iterative pass count $n_{FR}$ is then doing real work, not merely improving accuracy: it provides the *temporal slot* in which top-down attention can act at all. This is the most consequential architectural alignment between the user's program and the present review.

**(ii) Counterpoint to gilbert_li2013_topdown.** Where Gilbert & Li argue that V1 is an adaptive processor whose tuning, gain, and contextual integration are reshaped task-by-task by descending signals, Van der Stigchel et al. argue that the initial selection is largely impervious to top-down signals and that the main top-down lever is window size rather than feature-by-feature retuning. These views are not incompatible — the reconciliation is the temporal decomposition the review itself proposes: top-down signals act *between* and *after* feedforward sweeps, not *during* them. The user's program is consistent with this reconciliation, but it must be stated explicitly: the Feedback Transformer's modulation is correctly interpreted as biasing the *next* sweep, not as a within-sweep override. This is an important framing distinction for any follow-up paper that explicitly invokes Gilbert & Li in support of the architecture — the same paper should cite Van der Stigchel et al. as the boundary condition.

**(iii) Attentional window as a concrete computational target.** The review's most concrete behavioral lever — the size of the attentional window — has a natural architectural analog in patch-level self-attention. The effective receptive field of the recurrent state at each level of the hierarchy (`the_user_architectural_program.md` §3) is precisely a learned spatial-scale parameter: a layer with a coarser grid resolution and broader conv-transpose ascending projections corresponds to a wide attentional window; a layer with finer resolution and narrower projections corresponds to a small window. The dual-resolution structure of GridCell RNN layers (V1-level small, deeper levels coarser) gives the architecture exactly the kind of multi-scale window controller the review treats as the primary top-down handle. Connecting this to behavior — e.g., showing that the hierarchical RViT's eye-tracking predictions (`the_user_architectural_program.md` §6, Eye Tracking) reflect modulation of window size by task context — would be a substantive empirical bridge between the architecture and the review's central construct.

**(iv) Constraint on PRISM v1 / v2 modulation strength.** PRISM v1's FiLM modulation and PRISM v2's hierarchical FiLM inject top-down signals at the input to the feature stack. Van der Stigchel et al.'s analysis cautions against treating these injections as fully overriding bottom-up drive: in any change-detection or video-autoencoding result where the model appears to *ignore* a salient distractor without explicit suppression training, the architecture is making a strong claim about top-down power that the behavioral literature does not support. A defensible interpretation is that FiLM modulation shifts the *window* of processing across timesteps but does not override within-window competition; this aligns the PRISM lineage with the review's bounds.

**(v) Connection to miller_cohen2001_pfc_function.** Miller & Cohen frame top-down control as PFC-supplied bias signals over posterior representations; Van der Stigchel et al. constrain the temporal and spatial scope within which those bias signals operate. Both are needed to read the user's `competition-emergent-predictive-coding` thesis (`the_user_architectural_program.md` §5) correctly: hub-to-hub feedback (e.g., RL hub biasing the sensory hub) is a PFC-style bias signal, but its effects are bounded by the same temporal and spatial constraints that bound biological top-down attention. The Feedback Transformer's per-pass softmax competition is the architectural site where those bounds are realised: top-down signals into Q/K change which attention scores are computed on the *next* sweep but cannot retro-act on the current one.

**(vi) Connection to baluch_itti2011_topdown_mechanisms and gazzaley_nobre2012_topdown.** Baluch & Itti 2011 and Gazzaley & Nobre 2012 catalogue top-down mechanisms (attentional templates, gain modulation, working-memory-mediated bias). Van der Stigchel et al. 2009 places those mechanisms in a temporal and spatial frame: yes, templates and biases exist; no, they cannot rewrite the first feedforward sweep. Together these three reviews give a defensible reading of what the Feedback Transformer is and is not entitled to do: it implements template-, working-memory-, and gain-based top-down feedback (Baluch & Itti / Gazzaley & Nobre) within the temporal and spatial bounds the present review identifies.

**(vii) Connection to lamy2006_grouping_no_attention.** Lamy et al. 2006 show that perceptual grouping proceeds without attention — a result aligned with Van der Stigchel et al.'s "first sweep is bottom-up" claim, since grouping is one of the operations the feedforward sweep accomplishes. For the user's program, both papers anchor the commitment that the architecture's feedforward stem (the patch-embedding ConvNet plus the first ViT block) is genuinely doing pre-attentive work that need not be mediated by recurrent memory — only later passes invoke the Feedback Transformer's full multi-source integration. This also speaks to the design choice of *not* feeding $H^{(t-1)}$ into the very first conv-stem of each frame: the bottom-up sweep should be allowed to compute its initial salience landscape unmodulated, with recurrent feedback entering only at the self-attention stage where Gilbert-style task-dependent re-weighting is biologically plausible.

**(viii) Implication for the iterative encoder's first pass.** In the iterative variational encoder–decoder (`the_user_architectural_program.md` §4), pass $t=1$ has no prior $H_0$ — the guide is initialised, the image is shown, and the first forward sweep proceeds essentially bottom-up. Subsequent passes ($t = 2, \ldots, n_{FR}$) integrate the accumulating $H_t$. This is exactly the temporal decomposition Van der Stigchel et al. argue for: the first sweep is bottom-up; later "sweeps" (here, later recurrent iterations) are top-down-biased. The review therefore not only constrains the architecture but actively motivates its iterative structure: a purely feedforward model cannot exhibit the post-sweep top-down modulation the review identifies as the actual locus of top-down attention. The Recurrent ViT and its descendants are the minimum architectures that can.

In summary: Van der Stigchel et al. 2009 is the paper to cite when the user's program is challenged on the grounds that "real top-down attention does not modulate V1 the way your Feedback Transformer modulates patch-level self-attention." The defensible response — already implicit in the architecture's *per-timestep* recurrence rather than per-layer-within-a-pass top-down injection — is that the architecture respects the review's bounds: feedback acts between sweeps, modulates window size and priority more than within-window selection, and is biological in spirit precisely because it is bounded. The combination of `gilbert_li2013_topdown` (top-down is pervasive and quantitatively large) and `vanderstigchel2009_topdown_limits` (top-down is bounded temporally and spatially) gives the user's program both its empirical mandate and its principled constraints.

## 8. Citations to follow

- `theeuwes1992_additional_singleton` — the foundational additional-singleton paradigm. Not yet in seed.
- `folk_remington_johnston1992_contingent_capture` — the contingent-capture alternative the review argues against. Not yet in seed.
- `awh_belopolsky_theeuwes2012_failed_dichotomy` — same authors' follow-up arguing top-down vs bottom-up is a failed theoretical frame; selection history is the better organising construct. High priority for adding.
- `kastner_ungerleider2000_attention_review` — the fMRI review on baseline shifts the present review reconciles with. Not yet in seed.
- `corbetta_shulman2002_dorsal_ventral_attention` — the two-network framing of top-down vs reorienting attention. Not yet in seed.
- `belopolsky_theeuwes2010_attentional_window` — direct experimental demonstration of the attentional-window construct. Not yet in seed.
- `gaspelin_leonard_luck2015_proactive_suppression` — direct evidence that top-down suppression of salient distractors is possible (counterpoint to the review). High priority.
- `gilbert_li2013_topdown` — the modulation-everywhere companion review; already in seed at full depth.
- `baluch_itti2011_topdown_mechanisms` — top-down mechanisms in computational models; already in seed.
- `gazzaley_nobre2012_topdown` — working-memory and top-down bias; already in seed.
- `miller_cohen2001_pfc_function` — PFC bias-signal account; already in seed.
- `lamy2006_grouping_no_attention` — grouping without attention; already in seed.
