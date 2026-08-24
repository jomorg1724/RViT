---
id: jehu2015_postural_attention
title: "Prioritizing attention on a reaction time task improves postural control and reaction time"
authors:
  - "Jehu, Deborah A."
  - "Desponts, Alyssa"
  - "Paquet, Nicole"
  - "Lajoie, Yves"
year: 2015
venue: "International Journal of Neuroscience"
doi: "10.3109/00207454.2014.907573"
arxiv: ""
url: "https://pubmed.ncbi.nlm.nih.gov/24655152/"
tags:
  - reaction-time
  - visual-attention
  - psychophysics
concepts:
  - cueing-effect
  - chronometric-function
related:
  - posner1980_orienting
  - prinzmetal2005_rt_vs_accuracy
  - saltzman_garner1948_rt_span
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_57
status: full
depth: full
last_updated: "2026-05-16"
---

# Prioritizing attention on a reaction time task improves postural control and reaction time

## 1. Abstract

*Paraphrase from the PubMed record and the published abstract; the full article is paywalled and was not retrieved verbatim.*

Flexible allocation of attention is central to dual-task behavior, where a postural-control task (standing) is performed simultaneously with a perceptual–motor task (a speeded button-press in response to a visual or auditory stimulus). In this pilot study, twenty healthy young adults stood on a force platform under two postural-difficulty levels (two-foot stance versus one-foot stance) and performed two reaction-time conditions (simple RT versus choice RT). Crossed with these manipulations was an explicit instruction to prioritize either posture or RT on a given block.

The principal finding is that when participants were instructed to prioritize the RT task, *both* dependent measures improved: reaction times were significantly faster, and center-of-pressure (COP) displacement and 95%-confidence-ellipse sway area were significantly reduced, relative to the prioritize-posture condition. The authors interpret this as evidence that, in healthy young adults, deliberately directing attention away from posture toward an external chronometric task does not impair — and in fact benefits — postural control, consistent with a "constrained-action" account of motor control in which over-attention to an automatized motor task disrupts it.

## 2. Why this matters for us

The Recurrent ViT paper cites Jehu et al. 2015 in the chronometric/behavioral introduction (ref [57]) as one of the modern behavioral-psychology references that establish reaction time as a sensitive index of internal attentional allocation.

For our purposes the paper plays a supporting, cluster-completing role rather than a load-bearing one. It belongs to a small set of references — Saltzman & Garner 1948 (ref [54]), Prinzmetal et al. 2005 (ref [56]), Jehu et al. 2015 (ref [57]) — that together establish that (i) RT measures attention, (ii) RT and accuracy measures can be dissociated by mechanism, and (iii) the *direction* of attentional prioritization itself is a manipulable variable whose effect on RT is measurable.

Our work uses the third point implicitly: in cued change-detection, the cue is precisely an instruction to prioritize attention toward a spatial location, and the validity effect is the chronometric/accuracy consequence of that prioritization being correct or incorrect. The Jehu et al. result also serves as a cautionary counterexample to a too-simple "attention always helps where it goes" reading: a sufficient amount of attention to a process that does not benefit from it (postural control in young adults) can actively harm performance.

## 3. Key claims

1. Healthy young adults can deploy attention flexibly between a postural task (standing on one or two feet) and a chronometric perceptual–motor task (simple or choice RT) on the basis of explicit instruction.
2. Prioritizing attention toward the RT task improves the RT measure as expected, with $F(1,19) = 30.9$, $p < 0.001$.
3. The same prioritization toward the RT task *also* improves postural-control measures, reducing both COP displacement ($F(1,19) = 5.1$, $p < 0.05$) and 95%-confidence-ellipse sway area ($F(1,19) = 7.1$, $p < 0.05$).
4. Therefore, in healthy young adults, the dual-task cost of standing is not simply a fixed attentional load that has to be paid; rather, the *allocation* of attention between posture and a concurrent task can be adjusted by instruction, and the optimal allocation for both tasks is to direct attention away from posture.
5. The result is consistent with the constrained-action hypothesis (Wulf and colleagues): explicit internal-focus attention on an automatized motor task (standing) interferes with the task's automatic execution and degrades performance.
6. Reaction time is a sensitive enough behavioral measure to detect the chronometric consequence of an instruction-driven attentional reallocation, vindicating the Saltzman–Garner-era premise that RT is a usable index of internal attentional state.

## 4. Methods

Twenty healthy young adults participated in a within-subjects design. The factorial structure was:

- **Postural condition** (2 levels): two-foot stance versus one-foot stance on a force platform. The two-foot condition is the standard quiet-stance baseline; the one-foot condition substantially increases the postural-control demand by reducing the base of support and increasing the mediolateral instability the postural controller must compensate for.
- **RT task** (2 levels): simple RT (single stimulus, single response) versus choice RT (multiple stimulus–response mappings). Choice RT is known to elicit longer mean RTs and higher central-processing load than simple RT, providing a within-subject manipulation of the cognitive demand of the chronometric task.
- **Attentional priority** (2 levels): prioritize posture versus prioritize RT, given by explicit verbal instruction before each block. This is the central novel manipulation of the study.

This is a $2 \times 2 \times 2$ within-subject design with eight cells per subject. Postural measures were derived from the COP signal on the force platform: mean COP displacement and the area of the 95% confidence ellipse of the COP trajectory (a standard sway-area summary in the postural-control literature). The RT measure was mean reaction time to the imperative stimulus, computed across trials within a block. Statistical analysis used repeated-measures ANOVA over the within-subjects factors with $\alpha = 0.05$.

The methods are conventional for the postural-attention dual-task literature; the novel feature of the design is the orthogonal manipulation of *which task* the subject is instructed to prioritize, which most prior work in this paradigm had treated as fixed (typically prioritize-posture by default, on the implicit assumption that maintaining balance is the more urgent task).

## 5. Results

The principal numerical results, as reported in the abstract:

- **RT improvement under RT prioritization**: $F(1,19) = 30.9$, $p < 0.001$. This is the largest effect in the data and confirms that subjects can comply with the prioritization instruction. The size of the F-statistic — with $df = (1, 19)$, corresponding to an effect size of roughly $\eta_p^2 \approx 0.62$ — indicates that prioritization is not a subtle within-subject manipulation but a large and reliable one.
- **COP displacement under RT prioritization**: $F(1,19) = 5.1$, $p < 0.05$. COP displacement was *smaller* — i.e., better postural control — when RT was prioritized than when posture was prioritized. Effect size is moderate ($\eta_p^2 \approx 0.21$), and the result reaches conventional significance.
- **95% confidence ellipse area under RT prioritization**: $F(1,19) = 7.1$, $p < 0.05$. Sway area was *smaller* (better postural control) when RT was prioritized than when posture was prioritized. The convergence of two distinct sway summary statistics on the same conclusion ($p < 0.05$ in both cases) adds confidence that the postural effect is not an artifact of any single COP summary metric.

The paradoxical-looking result — that telling subjects to attend less to posture produces better postural control — is the headline of the paper.

Within the constrained-action framework, the interpretation is that postural control in healthy young adults is sufficiently automatized that voluntary internal-focus attention disrupts rather than aids it, while external-focus attention on the RT task leaves the postural controller free to execute its automatic program.

The specific cell-by-cell breakdown (which combinations of stance, RT-task type, and prioritization produced the largest effects) is reported in the full paper but not in the abstract; the F-statistics quoted above are main effects of the prioritization manipulation, and the interaction structure with stance difficulty and RT-task type is not disclosed in the abstract.

## 6. Critique / limitations

Several caveats limit the strength of the conclusions drawn.

First, the sample size is small ($n = 20$) and the population is restricted to healthy young adults. The authors themselves describe the work as a pilot study, which is the right framing given the sample size and the absence of a power analysis.

The constrained-action prediction reverses, in principle, for populations whose postural control is *not* fully automatized — children, older adults, patients with Parkinson's disease, vestibular disorders, or recovery from injury. The dual-task gait literature (Woollacott & Shumway-Cook 2002; Yogev-Seligmann et al. 2008) shows that for such populations, prioritizing posture is often the correct strategy. The paper's result is therefore not a general principle of attention allocation but a specific consequence of the healthy young-adult regime.

Second, the design conflates internal-focus versus external-focus attention with prioritization of task A versus task B.

Wulf's classical manipulation contrasts attending to *the body* versus attending to *the environment* while performing the same motor task; the present paper instead contrasts which of two simultaneous tasks the subject treats as primary. These are related but not identical manipulations, and the resulting interpretive ambiguity is not fully resolved.

Third, the postural measures (COP displacement, 95%-confidence-ellipse area) are summary statistics over a block of trials and do not resolve the temporal microstructure of sway. Whether the prioritization effect operates via reduced low-frequency drift, reduced high-frequency jitter, or both is not addressed by the reported analyses. Modern postural-control work (e.g., wavelet decomposition of sway) would be informative here.

Fourth, the F-statistics in the abstract are main effects of prioritization without explicit reporting of interaction terms with stance difficulty or RT-task type.

It is plausible (and likely, given the wider literature) that the prioritization effect is largest in the more challenging cells (one-foot stance × choice RT) and weakest or absent in the easy cells (two-foot stance × simple RT); the abstract does not disclose this. Without the interaction structure, the paper's conclusion is a qualitative one — "prioritization helps" — rather than the more useful conditional claim about when it helps and by how much.

Fifth, there is no signal-detection or process-model decomposition of the RT effect (cf. Prinzmetal et al. 2005 in the same database). The RT improvement under RT-prioritization could reflect a perceptual-sensitivity gain, a decisional criterion shift, or a motor-preparation effect. The paper's design is not equipped to distinguish among these.

Sixth, the explicit verbal instruction "prioritize RT" or "prioritize posture" is a coarse manipulation that bundles together several distinct cognitive operations: setting a strategic goal, allocating an attentional resource, adjusting decision thresholds, and biasing motor preparation.

The paper treats the prioritization instruction as a unitary manipulation, but in modern cognitive-control terms it could plausibly be operating at any or all of these levels. A more refined version of the study would manipulate, say, decision-threshold and attentional-gain separately and measure their distinct effects on RT and sway.

Seventh, the COP-based postural measures are themselves indirect proxies for the underlying control problem. COP displacement reflects the integrated output of a many-degree-of-freedom musculoskeletal system regulated by spinal reflexes, cerebellar feedback, vestibular integration, and cortical voluntary control. Attributing a change in COP to a change in *attention* requires assuming that none of these lower-level loops have changed — an assumption that is plausible but not directly tested in the design.

These limitations do not undermine the paper's pilot-study contribution, but they do constrain how heavily it can be cited as evidence for a general claim about attentional allocation. The paper is best read as a *demonstration* that the prioritization-instruction manipulation is tractable and produces measurable effects in young adults, not as a definitive characterization of how attention is allocated in dual-task standing.

## 7. Connection to our work

Jehu et al. 2015 is a lower-priority paper for the user's architectural program, and the connection to the Recurrent ViT and PRISM is indirect. It belongs to the cluster of references — Saltzman & Garner 1948 (`saltzman_garner1948_rt_span`), Posner et al. 1980 (`posner1980_orienting`), Prinzmetal et al. 2005 (`prinzmetal2005_rt_vs_accuracy`) — that collectively license the use of reaction time as an empirical index of attentional state.

Within that cluster, Jehu et al. contribute a specific point that the others do not: *the direction of attentional prioritization is itself a manipulable variable whose chronometric consequences are measurable.* Saltzman & Garner show that RT depends on set size; Posner shows that RT depends on cue validity; Prinzmetal shows that RT and accuracy can dissociate by mechanism; Jehu et al. show that RT depends on which of two simultaneous tasks the subject is instructed to prioritize.

This is the same epistemic move that the Recurrent ViT's cued change-detection paradigm makes computationally. A Posner cue at $t = 1$ is, formally, an instruction to prioritize attention toward a particular spatial location.

The model's response — measured at all subsequent recurrent steps as a chronometric proxy and at the end of the trial as accuracy — is the consequence of that prioritization being correct (valid cue) or incorrect (invalid cue). The validity effect we report in Figure 3C/F of the Recurrent ViT paper is, in this sense, the model-side analog of the prioritization-effect Jehu et al. report on the human side: in both cases, an instruction-driven reallocation of attention produces measurable chronometric and outcome consequences.

The constrained-action interpretation that Jehu et al. invoke — that over-attention to an automatized process disrupts it — has no direct architectural correspondent in our models, since our models have nothing analogous to "automatized" versus "controlled" processing.

But it is a useful reminder that attentional allocation is not zero-sum in human behavior: directing attention toward task A does not strictly subtract from task B's performance, because the relationship between attention and performance is mediated by whether the recipient process benefits from attention at all.

In our cued paradigm, the analogous question is whether all locations benefit equally from attention or whether some locations (e.g., already-predicted ones) are unaffected by it. This is not a question we have systematically addressed in the published Recurrent ViT, but it is the kind of follow-up that the Jehu et al. result motivates.

A second computational connection worth recording: the prioritization manipulation in Jehu et al. is, formally, a top-down task-set signal that biases processing in favor of one of several concurrent input streams.

The neural substrate for such task-set signals in primates is dorsolateral prefrontal cortex, with influences on parietal priority maps (LIP) and ultimately on early visual cortex via descending projections. In the user's architectural program, this top-down task-set is naturally implemented as a learned feedback signal from a "task" hub into the central self-attention mechanism — exactly the kind of signal the Feedback Transformer (`feedback-transformer` in TAXONOMY.md) is designed to integrate.

So while Jehu et al. do not themselves bear on the Feedback Transformer architecturally, the behavioral phenomenon they document is precisely the kind of phenomenon the Feedback Transformer is designed to model: an exogenous top-down signal that reweights ongoing perceptual computation in a goal-relevant way.

For the user's broader architectural program (`threads/the_user_architectural_program.md`), Jehu et al. anchor the *task* side rather than the architectural side (per §7 item 5 of that thread). The paper has no bearing on the Feedback Transformer, the multi-compartmental memory, the iterative variational encoder–decoder, or the competition-emergent predictive-coding thesis. Its inclusion in the database is for citation-cluster completeness rather than architectural relevance.

A speculative architectural reading is nonetheless worth recording. The Jehu et al. result — that two ostensibly competing tasks can be jointly optimized when attention is directed away from the "default" task — has a loose analog in the user's multi-hub multi-objective system (concept `multi-hub-multi-objective-system` in TAXONOMY.md).

In that architecture, an MSI hub, an RL hub, and a VAE hub compete for control of a central self-attention map. The premise that all three hubs benefit from a *correctly allocated* competition, rather than from any one hub dominating, is structurally analogous to the dual-task result.

The analogy is loose because Jehu et al. study an instruction-driven allocation in a single subject, whereas the multi-hub architecture envisions a learned allocation across hubs; but the family-level claim — that attention allocation is a manipulable variable with surprising joint-performance consequences — is shared. This is not a load-bearing connection, and the paper is not cited for it in `the_user_architectural_program.md`.

Finally, on the citation-cluster role: the entry `jehu2015_postural_attention` completes a four-paper cluster — `saltzman_garner1948_rt_span`, `posner1980_orienting`, `prinzmetal2005_rt_vs_accuracy`, `jehu2015_postural_attention` — that together establishes RT as the canonical chronometric variable for attention research.

The four papers cover, in roughly chronological order, the developmental arc of the RT-attention method: tachistoscopic display detection (Saltzman & Garner, 1948), spatial cueing (Posner, 1980), mechanism-dissociation between RT and accuracy (Prinzmetal, 2005), and dual-task prioritization (Jehu, 2015). Each paper adds one new dimension that the others lack, and the cluster as a whole is what gives RT its modern status as a sensitive, dissociable, paradigm-independent behavioral index of attention.

The Recurrent ViT paper cites all four references in adjacent positions of its bibliography (refs [54], [11], [56], [57]), and the cluster collectively supports the introduction's claim that the model's RT measures index the same kind of construct that decades of human behavioral work has used RT to index.

## 8. Citations to follow

These are the citations from Jehu et al. (and the closely adjacent dual-task / constrained-action literature) that would best round out the RT-attention cluster in this database. None are currently entered; they are candidates for future expansion.

- `wulf_lewthwaite2010_attentional_focus` — Wulf & Lewthwaite's constrained-action / external-focus framework; the conceptual frame Jehu et al. invoke for their interpretation. The original constrained-action hypothesis is articulated most clearly in this review.
- `woollacott_shumwaycook2002_attention_posture` — the canonical review of attention and postural control; the field-defining reference for postural-attention dual tasks. Establishes the basic dual-task-cost taxonomy that Jehu et al.'s prioritization manipulation refines.
- `yogev_seligmann2008_dualtask_gait` — review of dual-task gait performance, including the "posture-first" priority strategy in older adults; the population-level counterpoint to Jehu et al.'s young-adult result and the reason the constrained-action prediction cannot be assumed to generalize.
- `kahneman1973_attention_effort` — Kahneman's *Attention and Effort*; the foundational reference for attention-as-limited-capacity-resource, the assumption all dual-task work inherits.
- `pashler1994_dualtask_interference` — Pashler's bottleneck-vs-capacity-sharing review; the methodological frame for any dual-task RT result. Establishes the distinction between structural (response-selection) bottlenecks and graded capacity-sharing accounts of dual-task interference.
- `lajoie1996_attentional_demands_balance` — Lajoie's earlier RT-during-balance work; the senior author's own foundational paper on this paradigm and the methodological template the 2015 study refines.
- `wulf1998_external_focus_motor_learning` — Wulf's original external-focus / internal-focus demonstrations in motor learning; the empirical foundation of the constrained-action framework.
- `mcnevin2003_increasing_distance_external_focus` — McNevin's demonstrations that the magnitude of the external-focus benefit scales with the spatial distance between the focus and the body; gives a parametric handle on the constrained-action effect.
