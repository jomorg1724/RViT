---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.2
run_id: run-014
started: 2026-05-24T05:34:49Z
ended: 2026-05-24T05:58:00Z
worked_on: A2
attack_vector: literature
verdict_touched: A2--single-global-r
verdict_after: WEAKLY-SUPPORTED
papers_read: [reynolds_heeger2009_normalization, treue_martinez_trujillo1999_feature_attention, maunsell2015_attention_mechanisms, sani2017_temporal_v4_gain, ghose_maunsell2002_task_timing, reynolds_chelazzi2004_attentional_modulation, mcadams_maunsell1999_v4_tuning, carrasco2011_visual_attention_25y, luo_maunsell2018_criterion_sensitivity]
papers_added: []
spawned_tasks: [CR-049, CR-050]
---

# A2 — the single global asymmetry ratio r

## What I attacked

Assumption **A2** (mission §2.7; paper §2.4, named in §5.5): the
benefit/cost asymmetry is governed by a **single global ratio** $r>0$
($\beta(r)=2r/(r+1)$ at the gaining location, $\gamma(r)=2/(r+1)$ at every
losing location, the same $r$ everywhere, every trial, every feature). The
paper grounds $r$ in two dissociable mechanisms — top-down feedback (FEF/IPS)
for the benefit, lateral inhibition/surround suppression for the cost (§2.4,
refs [11–14]) — and itself flags A2 in §5.5: *"the asymmetry ratio $r$ is a
single global parameter; real neural circuits may have location-specific,
feature-specific, or time-varying asymmetries."*

This was the run-013 recommendation: the CR-045 re-derivation proved A8's
homogeneity-optimality is **A2-conditional**, so A2 is the connective frontier
tying together A3 (conservation form, CONTESTED) and A8 (allocation geometry,
CONFIRMED-CONDITIONAL) into one "heterogeneity" arc. A2 was the only headline
or assumption claim with no verdict file that also sat on this connective path
(CR-006/A1 was the alternative; deferred).

## How I attacked it

**Literature** (mission §3.2). A literature attack is the right first vector
because A2 is fundamentally an *empirical* claim about real neural circuits.
I read the paper's §2.4 / §5.4 / §5.5 verbatim, then ran the §11 wiki sweep
over the gain-modulation / normalization / surround-suppression /
feature-attention / temporal-attention cluster, reading eight full-depth
entries that bear directly on whether the benefit:cost asymmetry is one scalar.
0 web fetches (the wiki was sufficient — appropriate per §4.3). No new stub
(every relevant paper is already present), so no audit.py needed.

The pivotal analytical move was separating two readings of "single global $r$"
that the literature forces apart: **R1 between-preparation** ($r$ a constant
per preparation, varying across preparations — what the 100-fold $r$-sweep
operationalises) vs **R2 within-display homogeneity** (one $r$ for all
locations/features/times at once — what the model actually assumes).

## What I found

**The premise is decisively false under R2 — four independent axes, all in the
wiki:** *location/eccentricity* (reynolds_heeger2009: gain *form* set by
stimulus/RF ratio; mcadams_maunsell1999: V1 ≈8% vs V4 ≈26%, a 3× gradient;
carrasco2011: attention *helps then hurts* across eccentricity — a sign
reversal); *feature* (treue_martinez_trujillo1999 feature-similarity gain,
enhancement→suppression continuum, applied globally); *time*
(sani2017: gain form cycles contrast→response→contrast within a trial;
ghose_maunsell2002: gain magnitude tracks within-trial event probability,
same neuron different profiles); *mechanism multiplicity* (maunsell2015:
"attention" is a family of mechanisms "each with its own task dependence";
reynolds_chelazzi2004: contrast- and selectivity-dependence). The paper
concedes all of this in §5.4 ([8,13,18]) and §5.5.

**But the headline-safety question splits by reading.** Under **R1** the
simplification is *benign and methodologically correct*: a fixed preparation
has fixed geometry → one effective regime → one $r$; the 100-fold sweep covers
wherever any preparation lands; C1–C5 are $r$-indexed. The positive evidence
that a per-preparation scalar is reasonable is real
(reynolds_chelazzi2004's stable ~50%-effective-contrast benefit;
mcadams_maunsell1999's within-cell label-preserving single multiplier). Under
**R2** the simplification is empirically contraindicated, and whether that
*shifts C1–C5* is the open question — a first-pass structural argument suggests
C2 *reframes* (VDA vs $r_\text{cued}$ survives, uncued $r_i$ as nuisance
parameters), C4 is likely *robust* (its proof rests on $r$-independent
location-count geometry), and C1 could *deepen its already-contested corner* —
but this is a re-derivation question, not a literature one.

## Verdict movement

A2: **(none) → WEAKLY-SUPPORTED**. The label attaches to *whether the paper's
reliance on a single global $r$ is safe for its headline conclusions*, not to
the (false) empirical premise. Supported because the simplification is provably
safe under R1 (the dominant, paper-endorsed reading; the $r$-sweep *is* the
between-preparation handling); *weak* and *conditional* because R2 is
empirically real and its consequence for C1–C5 is unresolved. Not CONTESTED
(unlike C1): no attack this run *shifted* a headline claim — R2 was shown
empirically motivated, not yet consequential. Per §3.1/§6 a single vector
cannot elevate to CONFIRMED-*.

Referee theme sharpened: A2 is the **most R1-defensible of the paper's three
named/identified simplifications** — the methodology already discharges its
dominant reading. Contrast A3 (named, CONTESTED — a within-scope alternative
shifts a conjunct) and A8 (unnamed, CONFIRMED-CONDITIONAL — the optimiser makes
its choice unprompted). The residual A2 risk is localised exactly to the A2×A8
coupling CR-045 exposed.

## Next-attack recommendation

**CR-048** (re-derivation, already spawned by run-013) is the designated A2
second vector and the decisive test: let $r$ be a per-location vector $r_i$ and
ask (a) is equal-split still a critical point of the uncued simplex (generically
no — A8's exchange symmetry breaks even at equal validity), (b) does the
deviation scale with $\mathrm{var}(r_i)$ and is it bounded by the cued-absorption
pre-emption (CR-045 §4), and (c) does a $\pm30\%$ spread move any C1/C2 number
beyond the $1.4\times10^{-4}$ homogeneous-case slack. Outcome → A2
CONFIRMED-CONDITIONAL (if R2 is also bounded) or CONTESTED (if it shifts a
headline claim). CR-048 is now the recommended next pick.

## Wiki cross-references

- [[reynolds_heeger2009_normalization]] — cited (lead R2 constraint:
  configuration-dependent gain *form*; lead R1 confirm: fixed geometry → one
  regime).
- [[treue_martinez_trujillo1999_feature_attention]] — cited (feature-axis R2
  refutation; feature-similarity gain is heterogeneous gain — cousin of A8).
- [[maunsell2015_attention_mechanisms]] — cited (V1→V4→IT gain gradient +
  mechanism multiplicity; the review behind the paper's [11–14]).
- [[sani2017_temporal_v4_gain]] — cited (time-axis R2: gain form non-stationary
  within a trial).
- [[ghose_maunsell2002_task_timing]] — cited (time-axis R2: gain magnitude
  tracks within-trial event time).
- [[carrasco2011_visual_attention_25y]] — cited (eccentricity-axis R2 with sign
  reversal; grounds §5.4 [8,13,18]).
- [[reynolds_chelazzi2004_attentional_modulation]] — cited (contrast/selectivity
  dependence R2; ~50%-contrast stability R1).
- [[mcadams_maunsell1999_v4_tuning]] — cited (within-cell single multiplier R1;
  3× V1-vs-V4 gradient + cell-to-cell heterogeneity R2).
- [[luo_maunsell2018_criterion_sensitivity]] — cited (benefit/cost distinct
  substrates; bridge to A1/A6).
- [[mcadams_maunsell1999_reliability]], [[reynolds1999_competitive_v2_v4]],
  [[moran_desimone1985_selective_attention]],
  [[desimone_duncan1995_biased_competition]],
  [[moore_armstrong2003_fef_microstim]],
  [[sridharan2017_sc_sensitivity_bias]],
  [[muller_findlay1987_sensitivity_criterion]],
  [[cohen_maunsell2009_correlations]] — consulted; ground the $\beta$/$\gamma$
  mechanisms and the SDT decomposition but are silent on the *uniformity* of
  $r$; cited in passing / noted not load-bearing.
- [[failing_theeuwes2018_selection_history]], [[hickey2010_reward_salience_acc]],
  [[stanisor2013_v1_value_attention]], dopamine/RPE/basal-ganglia entries —
  value *source*, not asymmetry *form*; unrelated on inspection.
- [[bisley_goldberg2010_parietal_priority]], [[bisley_mirpour2019_priority_map]],
  [[rust_cohen2022_priority_coding]] — priority map sets *where*, not the
  benefit:cost ratio; unrelated on inspection.
- concept [[coalition_resource_competition]] — finite-resource/zero-sum framing
  behind $\beta+\gamma=2$ and the PRISM bridge (§3.5).
- §11.1 anchors *change detection / Posner cueing / cue validity*
  ([[posner1980_orienting]]) and *oculomotor / saccade* — task-foundation /
  premotor-overlap; unrelated to $r$-heterogeneity; noted.

**Math-methods gap (flagged, not filled):** the CR-048 re-derivation will need
majorization / Schur-concavity-under-perturbation tooling (as CR-045 did) — no
wiki substrate, an expected gap that mirrors the C5 floating-point and A8
log-concavity gaps.
