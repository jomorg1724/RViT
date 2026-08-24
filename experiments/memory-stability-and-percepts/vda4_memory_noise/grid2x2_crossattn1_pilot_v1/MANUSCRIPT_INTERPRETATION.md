# Manuscript interpretation plan: VDA4 memory-noise pilot

This file is a writing plan, not a result. No training or held-out evaluation
has been run for this registered pilot.

## Claim under test

The narrow pilot question is whether independently corrupting the recurrent
memory state increases the functional value of selective visual-memory routing
in a native four-patch VDA4 model. The proposed signal-coherence interpretation
is supported only when three kinds of held-out evidence align:

1. behavior: memory noise increases a sensitivity-corrected cueing effect rather
   than merely shifting response criterion;
2. allocation: visual and memory attention become more selectively aligned with
   the cue before change and the true changed location after change; and
3. causal use: graded, spatially specific attention-logit interventions at the
   true location have a larger behavioral consequence than matched interventions
   at cued-wrong or neutral-control locations.

Training accuracy, curriculum theta, engineering canaries, checkpoint existence,
and GPU/process health cannot satisfy any of these three requirements.

## Comparison that belongs in the main text

The evaluator crosses training memory noise {0.0, 0.5} with evaluation memory
noise {0.0, 0.5}. This separates two questions:

- **matched trained-condition contrast:** train0/eval0 versus
  train0.5/eval0.5 asks whether the complete noisy-training-and-testing condition
  shows stronger cueing, allocation, and causal dependence;
- **train-noise by evaluation-noise interaction:** all four cells distinguish
  learned reorganization or compensation from the acute effect of injecting
  noise at test time.

The primary cue-validity trend uses displayed validities 0.25, 0.50, and 0.75.
Forced-invalid trials at validity 1.0 are an explicitly out-of-distribution
expectancy-violation probe and must not be folded into the primary trend.

## Minimal main-text figures

The manuscript should prefer a small evidence chain over a gallery of plots:

1. one psychometric/SDT panel showing the cue-validity interaction, d-prime,
   criterion, and response timing;
2. one paired visual-versus-memory attention panel showing cue-period frames 1-4
   and change-period frames 5-6, including forced-invalid reorientation;
3. one intervention dose-response panel contrasting true-change, cued-wrong,
   and neutral-control roles for visual, memory, and both sources; and
4. one compact four-cell train-noise by evaluation-noise summary.

Full 4x4 source matrices, every frame, every spatial stratum, calibration,
quality-control tables, and trial-level uncertainty belong in the detailed lab
notebook/supplement. Visual and recurrent-memory attention maps must always be
shown separately; a fused map may appear only as a labeled secondary display.

## Interpretation table

| Held-out pattern | Allowed conclusion |
|---|---|
| Behavior, source-separated localization, and spatially specific intervention all strengthen | Seed-0 pilot support for increased functional reliance on selective routing under memory interference |
| Attention sharpens without sensitivity or causal specificity | Descriptive redistribution only; no signal-coherence support |
| Cueing changes through criterion but not d-prime | Response-policy change; no sensitivity/coherence support |
| Behavior improves without source/time-specific allocation and intervention | Behavioral effect without an established attention mechanism |
| Acute eval noise drives the effect but training noise does not | Acute corruption response, not learned compensation |
| Training-noise effect persists with eval noise off | Evidence consistent with learned reorganization, still seed-conditional |
| Any factorial cell fails competence or the common nonsaturation gate | Preserve and report the failure; mechanistic contrast is non-informative |

## Hard limits

This is one paired seed-0 pilot on one native 2x2 architecture. Even a coherent
positive result does not establish an across-seed population effect, a general
discretization law, a set-size law, a routing-family invariant, or a biological
mechanism. A supportive result must be followed by a separately frozen multi-seed
replication. A null result at standard deviation 0.5 would constrain this dose
and training algorithm; it would not rule out all interference strengths or an
all-networks-noisy training variant.
