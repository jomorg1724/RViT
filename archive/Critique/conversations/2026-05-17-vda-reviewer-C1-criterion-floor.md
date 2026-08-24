---
type: conversation
agent: skeptical-reviewer
prompt_version: "0.1"
run_id: run-003
started: 2026-05-17T15:00:00Z
ended:   2026-05-17T15:50:00Z
worked_on: C1
attack_vector: sensitivity
verdict_touched: C1--criterion-fraction-floor
verdict_after: CONTESTED
papers_read:
  - muller_findlay1987_sensitivity_criterion
  - hawkins1990_attention_detectability
  - luo_maunsell2018_criterion_sensitivity
  - sridharan2017_sc_sensitivity_bias
  - carrasco2011_visual_attention_25y
papers_added: []
spawned_tasks: [CR-020, CR-021, CR-022]
---

# C1 sensitivity attack — the criterion-fraction floor fails

## What I attacked

Claim **C1** (paper §4.1, last paragraph; mission §2.6):

> "Across the full parameter sweep (4,410 combinations), the
> criterion fraction is between 0.60 and 0.96."

Specifically, the *categorical* statement that CF ∈ [0.60, 0.96]
across all (r, V, v, variant) cells of the paper's primary grid,
where CF = (R(P3) − R(P4)) / (R(P1) − R(P4)).

The task was CR-002 from `agents/RESEARCH_BACKLOG.md`: locate the
in-sweep argmin CF, then probe extrapolations just outside the swept
ranges to see whether plausible parameter excursions push CF below
0.50 (the "attention dominates" boundary).

## How I attacked it

**Sensitivity vector** (mission §3.2.4). Two phases:

1. **Phase A.** Independently re-implemented the paper's policy
   decomposition (mission §2.5) from the equations stated in §§2.1–2.5,
   re-using the C2-replication primitives from CR-001 with a faster
   vectorised Phi (Abramowitz & Stegun 7.1.26, max error ~1.5×10⁻⁷;
   scipy was not installable in the sandbox owing to disk pressure).
   Swept the paper's primary grid exactly: 21 log-spaced r × 21 V ×
   5 v × 2 variants = 4,410 combinations, with N = 4, d'_max = 2.0,
   f_0 = 0.5, h = √, α-grid Δα = 0.02, c-grid Δc = 0.05 on [−3, +3].
   Validated against the paper's three §4.1 reference points.

2. **Phase B.** At the Phase A argmin, extrapolated along six axes
   outside the paper's sweep: (i) r ∈ {20, 50, 100, 500, 2000}, (ii)
   f_0 ∈ {0.05, 0.02, 0.01, 0.001}, (iii) h ∈ {a^3, a^4}, (iv) N ∈
   {8, 16, 32}, (v) v ∈ {10, 20, 50, 100}, and (vi) joint combos.

Implementation, output, and diagnostic trace at
`Critique/replications/C1--criterion-fraction-floor/`.

## What I found

**Phase A — primary sweep.**

| Metric                                | Paper        | This replication              |
|---------------------------------------|--------------|-------------------------------|
| CF range across all 4,410 rows        | [0.60, 0.96] | **[0.30, 1.00]**              |
| Variant A: CF range over 2,205 rows   | n/a          | [0.5587, 1.0000]              |
| Variant B: CF range over 2,205 rows   | n/a          | [0.3040, 1.0000]              |
| Rows with CF < 0.60                   | 0            | 590 (13.4%); A: 155; B: 435   |
| Rows with CF < 0.50                   | 0            | 177 (4.0%); A: 0; B: 177      |
| Median CF (both variants)             | ≈ 0.75 (impl) | 0.76                          |

Reference-point validation:

| Regime (V ≈ 0.5125, v = 5, variant A)  | Paper text | This code | Status |
|---------------------------------------|------------|-----------|--------|
| r = 1.0  (symmetric)                  | 0.73       | 0.7284    | ✓ |
| r = 3.16 (benefit-dominant)           | 0.64       | 0.6422    | ✓ |
| r = 0.32 (cost-dominant)              | 0.96       | 0.8542    | ✗ (Figure 2 visual reads ~0.85, consistent with my 0.85) |

Argmin locations:
- Overall: (r = 10, V = 0.25, v = 4, variant B) → CF = 0.3040.
- Variant A (v ≥ 2): (r = 10, V = 0.2875, v = 3) → CF = 0.5588.
- Variant A, all rows: (r = 10, V = 0.55, v = 1) → CF = 0.5587.

**Phase B — extrapolation (anchored at V = 1/N argmin).**

- Axis (i) r > 10: CF monotonically decreases from 0.30 at r = 10
  to 0.26 at r = 2000 (asymptote at r → ∞: CF_∞ ≈ 0.26). The
  paper's r ≤ 10 cap captures most of the in-corner floor.
- Axis (ii) f_0 < 0.1: CF *rises* to 0.69–0.72. Lower-baseline-d'
  regimes raise criterion gain faster than attention gain.
- Axis (iii) h ∈ {a^3, a^4}: CF rises to 0.66.
- Axis (iv) N > 4: CF rises to 0.78–0.87.
- Axis (v) v > 5: CF rises sharply to 0.78 (v = 10) → 0.97 (v = 20)
  → 0.9997 (v = 100). Higher value contrast favours criterion.
- Axis (vi) joint extreme combos: CF in [0.89, 0.99].

So pushing outside the sweep generally *raises* CF away from the
V = 1/N corner. The paper's swept r range [0.1, 10.0] already
captures essentially the worst-case CF; the categorical claim's
failure is interior to the sweep, not an extrapolation artefact.

**Mechanism.**

- The V = 1/N boundary is the principal source of low CF. The model's
  β/γ asymmetry produces an attention-reallocation incentive even at
  v = 1 (no value gradient) and V = 1/N (no validity gradient), because
  the β-scaled cued gain (weight 1/N in the reward, with d_c rising
  by β · Δd) exceeds the γ-scaled uncued loss (weight (N−1)/N, with
  d_u falling by γ · Δd) by a factor of approximately r at large r.
  α*(v=1) at r = 10, V = 1/N is ≈ 0.96 — far from the uniform 1/N
  the paper's terminology implies.
- The paper's policy decomposition labels R(P2) − R(P3) as
  "validity-attention gain". At V = 1/N this is a misnomer: the gap
  is purely β/γ-asymmetry-driven, not validity-driven. The
  decomposition mechanics are sound, but the naming overstates what
  is driving the gap at the boundary.
- Variant B's CR = 1 (value-decoupled) is more vulnerable than
  variant A's CR = V·v + (1−V). Variant B's P4 is smaller relative
  to P1, inflating the CF denominator and shrinking CF for the same
  numerator. This is a real model property — variant B's design
  intent was precisely to amplify the relative value of detection at
  high-value locations.

## Verdict movement

**Before this run:** OPEN (bootstrap-seeded, no verdict file).

**After this run:** **CONTESTED** (mission §3.1).

The paper's claim "CF ∈ [0.60, 0.96] across all 4,410 combinations"
is **falsified as written**: 13.4% of swept rows fall below 0.60,
4.0% fall below 0.50, and variant B's argmin is CF = 0.30 — half the
paper's claimed floor.

**Why CONTESTED and not REFUTED.** The substantive scientific point
("criterion adjustment is the dominant value-encoding mechanism in
most of the swept space") survives. Median CF ≈ 0.76. The §5.1
theoretical argument (criterion is costless; attention is zero-sum)
is unaffected. The paper *can* survive with a quantitative
re-statement preserving the spirit; the verdict file proposes such
a reformulation. Mission §6 requires REFUTED to identify a claim
"the paper cannot survive without substantive revision"; the
revision here is minor.

**Specific anomaly worth surfacing.** The paper's text §4.1 quotes
"CF = 96% at r = 0.3", but my replication finds 0.85 there, and the
paper's own Figure 2 bar chart visually reads ~0.85. The r = 1.0
and r = 3.2 reference numbers match precisely. Most likely the
"96%" is a manuscript transcription error. This is independent of
the categorical-floor failure but is worth correcting.

## Next-attack recommendation

The natural follow-up has three branches, in order of priority:

1. **CR-020 (high priority): C3 literature attack on the narrow-
   regime claim.** The seed task CR-003 is now closely tied to C1:
   the paper's §5.2 narrow-regime ("VDA is confined to low V, high
   v, moderate r") rests on C1's quantitative magnitude. With C1
   weakened in the V = 1/N corner, the §5.2 advice "high-validity
   paradigms predicted to show negligible VDA regardless of other
   parameters" needs a literature check. Survey the wiki for cueing
   studies at high V — do they show VDA? If yes, that's a C3
   contradiction; if not, C3 survives. Attack vector: literature.
   Prereq: none (independent of CR-002's findings).

2. **CR-021 (medium priority): V = 1/N degeneracy derivation.**
   Both CR-001/CR-014 (C2/C4) and CR-002 (C1) have surfaced the
   V = 1/N boundary as a recurring model edge case. A focussed
   re-derivation: at V = 1/N exactly, partition R(P2) − R(P3) into
   a validity-driven component (formally zero, since V − 1/N = 0)
   and an asymmetry-driven component (a closed-form expression in
   r, N, f_0, h). The derivation would (a) clarify the
   misleading "validity-attention" label at the boundary, (b)
   provide a unified analytic treatment of the boundary's
   contribution to CF / VDA / inversion, and (c) close out the
   "loose end" in C2, C4, and C1 verdicts simultaneously. Attack
   vector: re-derivation. Output:
   `Critique/derivations/V-equals-1-over-N--degeneracy.md`.

3. **CR-022 (low priority): r = 0.3 reference-point clarification.**
   The 11-percentage-point gap between paper text (96%) and
   replication (85%) at r = 0.3 is unlikely to be a code bug
   (r = 1.0 and r = 3.2 match precisely). Flag for owner attention
   so the authors can either (a) confirm a manuscript typo or (b)
   share the original code to compare. Attack vector: clarification
   request (a no-code task). Output: a one-page note in
   `Critique/conversations/` summarising the discrepancy with the
   reproducible reference points.

The agent's single recommended next attack is **CR-020** (C3
literature attack on narrow-regime claim). Reasoning: with C1 now
contested, the §5.2 experimental-design rubric is the next-strongest
load-bearing claim, and a literature attack against C3 is cheap
(wiki-anchored) and informative.

## Wiki cross-references

(See `Critique/evidence/C1--criterion-fraction-floor.md` for the
full sweep block.)

- [[muller_findlay1987_sensitivity_criterion]] — cited; foundational
  SDT-cueing dissociation.
- [[hawkins1990_attention_detectability]] — cited; foundational
  sensitivity-side cueing data. Not load-bearing on the CF floor.
- [[luo_maunsell2018_criterion_sensitivity]] — cited in
  "Implications for PRISM"; neural substrate of criterion (LPFC) vs
  sensitivity (visual cortex).
- [[sridharan2017_sc_sensitivity_bias]] — cited as the strongest
  empirical convergence; SC contributes primarily bias (criterion),
  not sensitivity, in multialternative attention tasks.
- [[carrasco2011_visual_attention_25y]] — cited as background.
- [[failing_theeuwes2018_selection_history]] — flagged for follow-up
  literature attack, not consulted in this run.
- [[hickey2010_reward_salience_acc]] — flagged for follow-up.
- [[reynolds_chelazzi2004_attentional_modulation]] — not consulted.
- [[reynolds_heeger2009_normalization]] — not consulted; bears on
  the β/γ asymmetry foundations, more relevant to A2.
