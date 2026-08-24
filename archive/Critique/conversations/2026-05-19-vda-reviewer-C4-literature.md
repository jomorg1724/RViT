---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.1
run_id: run-007
started: 2026-05-19T04:57:44Z
ended: 2026-05-19T05:42:00Z
worked_on: C4
attack_vector: literature
verdict_touched: C4--no-inversion
verdict_after: CONFIRMED-CONDITIONAL
papers_read:
  - failing_theeuwes2018_selection_history
  - hickey2010_reward_salience_acc
  - posner1980_orienting
  - gupta_sridharan2024_presaccadic_change
  - bisley_mirpour2019_priority_map
  - desimone_duncan1995_biased_competition
  - carlisle_kristjansson2018_wm_priming
  - hikosaka2006_bg_reward_eyes
papers_added:
  - wang_theeuwes2018_statistical_learning_distractor_suppression
spawned_tasks:
  - CR-035
  - CR-036
  - CR-037
---

# C4 (no-inversion): literature attack — distractor suppression is the model's anti-cue prediction, not a counterexample

## What I attacked

**C4** (mission §2.6; paper §4.5): "Inverted attention ($\alpha^\star <
1/N$) is never optimal" across the 4,410-row primary sweep. Coming into
this run C4 was **WEAKLY-SUPPORTED** — the run-006 re-derivation had
confirmed the empirical claim within the $N=4$ primary sweep, refined the
paper's incomplete §4.5 justification, and shown that the model *does*
produce inversion ($\alpha^\star < 1/N$) at anti-cued ($V<1/N$) locations,
so a conditional $V \geq 1/N$ is necessary. The verdict needed a second,
distinct attack vector to move. I ran the **literature attack** the
Version 0.1 verdict had specified (CR-031).

## How I attacked it

Two sub-questions: (i) does the behavioural literature report
below-uniform allocation to a *validly cued / high-value* location; and
(ii) is distractor-suppression learning a behavioural inversion *in the
model's terms*? I swept the local wiki (§11) over the
suppression/capture/selection-history sub-cluster, then used one PubMed
pass (2 calls: 1 search + 1 metadata batch — at the §4.3 soft cap of two
fetches; no WebSearch/WebFetch) to retrieve the canonical
statistical-learning-of-distractor-suppression cluster. I added one
abstract-depth wiki stub (Wang & Theeuwes 2018a) and cited the 2019
eye-tracking and 2020 biased-competition follow-ups by full bibliographic
reference. Full per-source breakdown in
`Critique/evidence/C4--no-inversion.md`.

## What I found

The single behavioural phenomenon that looks like "attending below
uniform to a location" is statistical-learning suppression of a
high-probability-**distractor** location (Wang & Theeuwes 2018a: reduced
capture and reduced target-selection efficiency, awareness-independent,
spatial gradient; Wang, Samara & Theeuwes 2019: fewer saccades land
there; Kong et al. 2020: suppressing it reallocates resource to the
target). But that location is the one *least* likely to contain the
target — in the paper's model, a location with target-validity below
$1/N$, i.e. **anti-cued**. CR-004/run-006 already showed in closed form
that the model's normative optimum at $V<1/N$ (with $v=1$) *is*
$\alpha^\star<1/N$. So distractor suppression is the model's **own
prediction** in the anti-cued regime — a convergence, not a
contradiction. Two clean mappings of the phenomenon onto the model's
single-cued / homogeneous-uncued geometry both leave C4 intact: as an
anti-cued cued-slot (model predicts inversion) or as heterogeneous
uncued allocation (outside the model's representational scope — a
separate, unnamed homogeneity assumption).

On sub-question (i): no study reports the mirror effect (below-uniform
allocation to a high-value validly-cued location). Value-driven capture
pulls attention *toward* value, even maladaptively (Failing & Theeuwes
2018; Hickey 2010) — positive support for no-inversion at the cued
location. The Gupta & Sridharan 2024 candidate is a failure of
facilitation, not active inversion. And Kong et al. 2020's "suppress
here ⇒ more attention there" reciprocity *positively corroborates* the
paper's §5.1 zero-sum reallocation framing.

## Verdict movement

**WEAKLY-SUPPORTED → CONFIRMED-CONDITIONAL.** A second distinct attack
vector (literature) has failed to falsify C4 within its $V \geq 1/N$
scope, and the conditional that run-006 derived analytically is now
corroborated from an independent direction: the one behavioural
phenomenon resembling inversion lands precisely in the anti-cued regime
where the model independently predicts it. I chose CONFIRMED-CONDITIONAL
over CONFIRMED-UNDER-ATTACK because the claim *provably fails outside*
the $V \geq 1/N$ scope (the model itself inverts at $V<1/N$), so the
honest label is the one that names the conditional rather than asserting
unqualified robustness.

## Next-attack recommendation

**CR-036 (replication / re-derivation, proposed-A8 homogeneous-uncued
assumption)** — the substantive descendant of this run. Extend the model
to give one uncued location a distinct lower validity and test whether
the optimal policy reproduces the Wang & Theeuwes spatial suppression
gradient; this directly probes whether the paper's homogeneity
simplification changes any headline claim and connects the critique to a
concrete behavioural effect. Then **CR-005 (C5 replication)** to close
out headline-claim coverage (C5 is the only untouched headline claim).

## Wiki cross-references

(Full disposition in the verdict's `### Wiki cross-references` block.)

- [[wang_theeuwes2018_statistical_learning_distractor_suppression]] —
  added this run (abstract); cited as the crux evidence (anti-cued
  mapping).
- [[failing_theeuwes2018_selection_history]] — cited; separates
  facilitatory capture (supports C4) from inhibitory suppression
  (anti-cued).
- [[hickey2010_reward_salience_acc]] — cited; value pulls toward, not
  away.
- [[posner1980_orienting]] — cited; $V=1/N$ chance-validity boundary.
- [[gupta_sridharan2024_presaccadic_change]] — cited; resolves
  sub-question (i) candidate in the negative.
- [[bisley_mirpour2019_priority_map]], [[desimone_duncan1995_biased_competition]]
  — cited; priority-map / biased-competition substrate, surfaces the
  homogeneous-uncued limitation; Kong et al. 2020 reciprocity supports
  the §5.1 zero-sum framing.
- [[carlisle_kristjansson2018_wm_priming]], [[hikosaka2006_bg_reward_eyes]]
  — surfaced by grep; background (selection-history-toward / reward-toward),
  consistent direction, not direct tests.
- Concept [[priority-map]] — cited at concept level (shared mechanism).
- Taxonomy gap surfaced: no `selection-history` concept in TAXONOMY;
  filed the stub under closest-fit `priority-map` per mission §4.2 and
  flagged for owner.
