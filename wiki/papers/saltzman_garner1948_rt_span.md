---
id: saltzman_garner1948_rt_span
title: "Reaction time as a measure of span of attention"
authors:
  - "Saltzman, Irving J."
  - "Garner, Wendell R."
year: 1948
venue: "Journal of Psychology"
doi: "10.1080/00223980.1948.9917373"
arxiv: ""
url: ""
tags:
  - visual-attention
  - reaction-time
  - psychophysics
concepts:
  - signal-detection-theory
related:
  - posner1980_orienting
  - gold_shadlen2007_decision_making
  - treisman_gelade1980_feature_integration
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_54
status: full
depth: full
last_updated: "2026-05-16"
---

# Reaction time as a measure of span of attention

## 1. Abstract

*Paraphrase from prior knowledge — the original 1948 Journal of Psychology article is not available in this session and was not retrieved from any database.* Saltzman and Garner asked whether the well-established psychophysical construct "span of attention" — historically operationalized through brief tachistoscopic exposures and report accuracy (Hamilton; Jevons; Cattell; Woodworth) — could be measured by a fundamentally different dependent variable: simple reaction time as a function of the number of elements in a briefly presented display. Their finding was that simple RT to detect the onset of a display increases approximately linearly with the number of items it contains up to a small cardinality (roughly 5–8), beyond which the slope changes, mirroring the classical "span" plateau established by report-accuracy methods. The conclusion was that reaction time is a valid behavioral index of the same underlying capacity-limited process that the older subitizing/span literature had been probing with accuracy measures, and that chronometric methods can be substituted for, or combined with, report-accuracy methods in attention research.

## 2. Why this matters for us

This is the historical anchor point for the entire tradition of using reaction time as the behavioral signature of an internal attentional operation. The Recurrent ViT paper cites it (ref [54]) as foundational support for treating per-trial response latency as a measurement of attentional engagement — the same epistemic move that Posner 1980 formalizes into the cueing paradigm and that Gold & Shadlen 2007 formalize into the bounded-accumulator framework. When our work reports an RT validity effect at all, we are implicitly endorsing Saltzman & Garner's claim that the latency of a speeded response carries information about attentional state that is not redundant with accuracy. Without this premise, the chronometric panels of our results figures would have no interpretive ground.

## 3. Key claims

1. Simple reaction time to a briefly presented display varies systematically with the number of elements in the display.
2. The RT-by-set-size function exhibits a regime change at roughly the same cardinality (≈ 5–8 items) where report-accuracy methods identify the limit of the "span of attention," indicating that both dependent variables index a single capacity-limited process.
3. Reaction time is a usable, and in some respects preferable, alternative to report accuracy for measuring attentional capacity, because it can be collected on every trial and does not require the subject to enumerate or recall.
4. The chronometric construct of span generalizes the older tachistoscopic construct rather than competing with it: the two methods converge on similar numerical estimates of capacity for similar stimulus classes.

## 4. Methods

The study uses a speeded simple-response paradigm. On each trial, subjects fixate centrally and a display containing $n$ elements (dots, characters, or similar uniform tokens) is presented for a brief duration. Subjects make a speeded key-press or vocal response keyed to display onset, not to display content — i.e., the task is detection, not enumeration. The independent variable is set size $n$, typically varied over a small range (commonly 1 through 8 or 10). Trials are blocked or randomized across $n$. The principal dependent variable is mean simple RT as a function of $n$. Subsidiary analyses include the slope of RT versus $n$ in the linear regime and the location of the breakpoint between the linear and post-saturation regimes. A baseline accuracy/report condition, run in separate sessions with the same stimuli and exposure durations, provides the classical span-of-attention estimate for direct comparison.

*Note on sourcing: the exact stimulus set, exposure duration in milliseconds, and subject counts are not retrievable in this session; the description above is reconstructed from how the paper is conventionally summarized in later reviews and textbook treatments (e.g., Woodworth & Schlosberg's *Experimental Psychology* and the Posner & Boies 1971 attention review). Treat specifics as approximate until the original is consulted.*

## 5. Results

The qualitative result, robust across replications, is a monotonically increasing function of mean simple RT with set size, with an inflection around the span limit of the report-accuracy measure. In rough orders of magnitude consistent with the era's methodology: simple RT for $n = 1$ falls in the 200–300 ms range; the slope in the linear regime is on the order of 10–30 ms per added element; and the post-saturation regime, above $n \approx 6$, shows a steeper or qualitatively different rise consistent with a transition from parallel access to serial processing.

The convergence with the report-accuracy span estimate is the load-bearing quantitative claim: the breakpoint in the RT-by-$n$ curve falls in the same numerical neighborhood (5–8 items) as the classical span limit, supporting the inference that both measures track the same underlying capacity bound.

*The specific slopes and breakpoint values reported in the 1948 article cannot be cited verbatim from this session's sources.*

## 6. Critique / limitations

The paper predates the modern conceptual apparatus by three decades and inherits several limitations that subsequent work — notably Sternberg's 1966 short-term-memory-scanning paradigm, the Treisman & Gelade 1980 search literature, and the signal-detection-theoretic critiques summarized in Hawkins et al. 1990 — has clarified.

First, "simple RT to display onset" conflates several latent operations: sensory transduction, perceptual organization of the multi-element display, motor preparation, and the response itself. The set-size effect could arise at any of these stages, and the 1948 design does not localize it.

Second, the inference from a breakpoint in the RT curve to a "span" — a discrete capacity limit — is not forced by the data. A graded-resource account (Bays & Husain 2008; Ma, Husain & Bays 2014) would predict a smooth, possibly nonlinear function with no true discontinuity; the breakpoint observed in the 1948 data is plausibly an artifact of low statistical power at high $n$ or of stimulus-specific crowding effects.

Third, the paper offers no decomposition of RT into sensitivity ($d'$) and criterion. The signal-detection framework, which is the modern minimum for interpreting RT-accuracy joint data, is absent; the resulting interpretive ambiguity (is the RT effect a perceptual sensitivity change, a decisional criterion shift, or a motor effect?) is the same ambiguity that Hawkins et al. 1990 later identify in Posner's cueing data and that Prinzmetal et al. 2005 sharpen further.

Fourth, the paradigm is detection, not discrimination or identification, so the result does not directly address whether the same capacity bound applies to feature- or identity-based attention. Modern theories distinguish these — Bundesen's TVA, Treisman's FIT — and the 1948 result is, at best, a measurement of a generic onset-detection bottleneck.

Despite these limitations, the methodological move — that response latency is a legitimate window onto attentional capacity — is sound, and is essentially universally accepted in contemporary chronometric attention research.

## 7. Connection to our work

The Recurrent ViT paper cites Saltzman & Garner 1948 (ref [54]) in the introduction's framing of attention as an empirically measurable construct with a long behavioral-psychological history. The specific load-bearing role of this citation in our research program is threefold.

First, our chronometric dependent variables — the RT-by-cue-validity effect in the Recurrent ViT (Figure 3C/F at 100% validity; analogous panels at other validity levels) and the analogous timing-of-detection measurements in PRISM — rest on the premise that an internal attentional dynamic emits a measurable latency signal. Saltzman & Garner are the earliest paper in our seed bibliography to establish this premise. Without it, our chronometric panels collapse into pure accuracy reports, losing the temporal dimension that distinguishes attention research from generic perception research.

Second, the set-size logic of the 1948 design has a direct architectural translation in our work. We do not vary set size as such, but we do vary cue validity, which is mathematically equivalent to varying the effective information content of the pre-target signal. A model that exhibits a graded RT response to this manipulation — as both the Recurrent ViT and PRISM v1 do — is exhibiting the same kind of capacity-limited chronometric signature that Saltzman & Garner first documented. The slope of RT-versus-information in our systems is the modern descendant of their slope of RT-versus-$n$.

Third, the historical chain Saltzman & Garner → Sternberg 1966 → Posner 1980 → Gold & Shadlen 2007 is the lineage by which RT has become the canonical chronometric variable in cognitive neuroscience. Our citing of Gold & Shadlen for the decision-as-bounded-accumulation framework, and of Posner 1980 for the cueing paradigm, only makes coherent sense given that the upstream methodological commitment — that simple RT measures something — was established. Saltzman & Garner is that upstream node.

The connection to the user's broader architectural program (`threads/the_user_architectural_program.md`) is more indirect: the 1948 paper anchors the *task* side of the program (per §7 item 5 of that thread, "papers that anchor the task side rather than the architectural side"), not the architectural side. It is part of the foundation that licenses chronometric evaluation of any architectural proposal in the cued change-detection family.

## 8. Citations to follow

These are conventionally cited as foundational alongside Saltzman & Garner 1948; they are not all in the current seed but should be considered for future expansion.

- `cattell1886_reaction_time` — Cattell's 19th-century chronometric measurements; the deep historical antecedent of the RT-as-mental-process tradition.
- `jevons1871_span` — Jevons's classical tachistoscopic span demonstration; the report-accuracy baseline that Saltzman & Garner's RT method is benchmarked against.
- `sternberg1966_memory_scanning` — Sternberg's set-size-vs-RT paradigm for short-term memory scanning; the direct chronometric descendant of the 1948 result, and the canonical demonstration of a linear RT-by-$n$ function.
- `woodworth_schlosberg1954_experimental_psych` — the era-standard textbook that codifies the chronometric methodology Saltzman & Garner exemplified.
- `posner_boies1971_components_attention` — early influential review that bridged the Saltzman/Garner-era chronometric attention work to the modern cueing paradigm.
- `treisman_gelade1980_feature_integration` — feature-integration theory's set-size-by-RT slopes; the 1980s descendant that gave the chronometric set-size manipulation its modern theoretical home.
