---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.2
run_id: run-012
started: 2026-05-24T01:43:05Z
ended: 2026-05-24T02:05:00Z
worked_on: A8
attack_vector: replication
verdict_touched: A8--heterogeneous-uncued
verdict_after: WEAKLY-SUPPORTED
papers_read: [wang_theeuwes2018_statistical_learning_distractor_suppression, coalition_resource_competition]
papers_added: []
spawned_tasks: [CR-045, CR-046, CR-047]
---

# A8 — is homogeneous-uncued allocation an assumption or an optimum?

## What I attacked

Assumption **A8** (mission §2.7; paper §2.2, verbatim: *"the remaining
attention is distributed equally among uncued locations, so each receives
$(1-\alpha)/(N-1)$"*). A8 forces the policy space to be 1-D in $\alpha$. It is
implicit in §2.2/§2.3, is **not** in the paper's four-item §5.5 limitations
list, and was surfaced/ratified at v0.2. No prior verdict existed — A8 was the
only owner-ratified assumption with no verdict file, so per mission §3.3 it was
the highest-value frontier (the explicit run-011 recommendation, CR-036).

The precise question: does the homogeneity assumption *bias* the headline
conclusions C1–C5, or would the optimiser choose homogeneity anyway if freed?

## How I attacked it

Replication (`Critique/replications/A8--heterogeneous-uncued/run.py`). Built a
general-$N$ optimal-observer model with arbitrary allocation **and** validity
vectors and per-location criteria, generalising the paper's $\beta/\gamma$ rule
to each location's own departure from $1/N$ (the unique generalisation
consistent with the §2.3 "roles reverse" note). It reduces identically to the
paper's homogeneous Eqs. (7)–(9). Three tests: (1) does equal-split maximise
$E[R]$ under equal uncued validity, including a curvature probe and a forced-
uniform-cued stress test; (2) does the full unconstrained simplex optimum
differ from the homogeneous one at headline cells; (3) with one anti-cued
(low-validity) slot, does the optimum produce graded suppression?

I caught and fixed a real bug mid-run: plain coordinate-ascent criterion
optimisation stalled in a local optimum on one variant-B config (missing the
joint optimum by 0.05). Replaced with an exact joint grid for $\le2$ criterion
groups and multi-restart coordinate ascent for $\ge3$, then **validated to
machine precision** against the C4 base optimiser ($G\le2$) and a joint 3-D
grid ($G=3$). Every number rests on the validated optimiser.

## What I found

**Validation** reproduces the headline numbers (C2 peak VDA $0.0769$ at
$r{=}0.398$; C1 CF $0.86/0.73/0.64$, matching run-003 incl. the CR-022 $r{=}0.3$
flag).

**A8 is innocuous for C1–C5.** Under equal uncued validity, equal-split is the
optimum in 32/32 cells (gain from any unequal split $=0.0$; $R''(0)<0$ in every
non-degenerate cell). The decisive test: the full unconstrained simplex optimum
**coincides** with the homogeneous-constrained optimum at every headline cell
($a_{\text{cued}}^\star\to1$, uncued spread $0$, $\Delta R$ within grid slack).
Relaxing A8 changes no headline number.

**But A8 is not a trivially-free assumption.** With a *forced* uncued budget
($\alpha=1/N$), 8/12 cells prefer to **concentrate** the uncued budget
($R''(0)>0$) — the benefit-dominant regime ($r>1$, $\beta>\gamma$) rewards
winner-take-all, the cost-dominant regime rewards spreading. The headline-claim
safety is a **structural coincidence**: concentrate-favouring $r>1$ also drives
$a_{\text{cued}}^\star\to1$, so the uncued budget vanishes before concentration
can bite.

**Relaxing A8 enriches the model.** With one anti-cued slot, the optimum
reproduces a **graded suppression** ($a_{\text{anti}}^\star$ falls monotonically
below uniform and below the higher-validity uncued slots as its validity drops;
freed attention reallocated to the cued/rest). This is the Wang & Theeuwes
(2018) spatial suppression gradient and the Kong 2020 reciprocity, and confirms
the CR-031/run-007 conjecture that the model predicts $\alpha<1/N$ at anti-cued
locations.

## Verdict movement

A8 had **no prior verdict** (ratified but untouched). After this run:
**(none) → WEAKLY-SUPPORTED**. One vector (replication) failed to show A8 biases
C1–C5. Per mission §6, no elevation on a single run. The support is conditional
on equal uncued validity and is a structural (not trivial) coincidence — the
designated second vector is a re-derivation of the "uncued-concentration ⇒
cued-absorption" lemma, which would elevate to CONFIRMED-CONDITIONAL. This is a
*confirming* assumption-layer outcome (contrast A3, CONTESTED): A8 is the most
defensible of the paper's simplifications.

## Next-attack recommendation

**CR-045** — re-derivation (the second vector): prove (a) Schur-concavity ⇒
equal-split optimal under equal validity for concave/linear $h$, and (b)
benefit-dominant uncued-concentration is always pre-empted by cued absorption,
so A8 never binds at the model's own optimum. Elevates A8 → CONFIRMED-CONDITIONAL.

## Wiki cross-references

- [[wang_theeuwes2018_statistical_learning_distractor_suppression]] — cited; the
  empirical spatial-suppression gradient Part 2 reproduces (the key anchor).
- [[failing_theeuwes2018_selection_history]], [[hickey2010_reward_salience_acc]]
  — cited; selection-history / reward priority that produce heterogeneous validity.
- [[bisley_mirpour2019_priority_map]], [[bisley_goldberg2010_parietal_priority]]
  — cited; the LIP priority map is the per-location substrate A8 collapses to a scalar.
- [[koch_ullman1984_winner_takes_all]], [[itti_koch2001_saliency_review]] —
  cited; winner-take-all = the Part 1b benefit-dominant concentration tendency.
- [[desimone_duncan1995_biased_competition]], [[reynolds1999_competitive_v2_v4]],
  [[reynolds_heeger2009_normalization]] — cited; biased-competition / divisive
  normalization = the zero-sum reallocation in Part 2.
- [[coalition_resource_competition]] (concept) — cited; the user's finite-resource
  framing; the PRISM bridge.
- [[stanisor2013_v1_value_attention]] — noted (value side, not central to A8).
- [[gupta_sridharan2024_presaccadic_change]], [[cohen_maunsell2009_correlations]]
  — unrelated on inspection for A8 (C4 and A1 respectively).
- §11.1 anchors searched and unrelated for A8: dopamine/RPE/basal-ganglia
  (value source not allocation geometry), FEF/SC microstim, V4 within-RF gain,
  Posner/change-detection (task foundation).
- Taxonomy gap (surfaced to owner): no `selection-history` /
  `statistical-learning-of-priority` concept exists; A8's gradient finding
  strengthens the case for adding one.
