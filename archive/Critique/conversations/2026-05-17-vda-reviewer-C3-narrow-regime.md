---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.1
run_id: run-004
started: 2026-05-17T16:30:00Z
ended: 2026-05-17T17:35:00Z
worked_on: C3 (mission §2.6; via task CR-020 merged with CR-003)
attack_vector: literature
verdict_touched: C3--narrow-regime
verdict_after: WEAKLY-SUPPORTED
papers_read:
  - failing_theeuwes2018_selection_history
  - hickey2010_reward_salience_acc
  - luo_maunsell2018_criterion_sensitivity
  - maunsell2015_attention_mechanisms
  - sridharan2017_sc_sensitivity_bias
  - posner1980_orienting
  - cameron2002_covert_attention_contrast
  - carrasco2011_visual_attention_25y
  - srinath2021_attention_information_flow
  - bhatnagar2022_attention_choice_metaanalysis
  - baluch_itti2011_topdown_mechanisms
  - monosov2020_outcome_uncertainty
  - herman_krauzlis2017_sc_change_detection
  - herman_arcizet2020_caudate_sc
papers_added:
  - stanisor2013_v1_value_attention
spawned_tasks:
  - CR-023 (literature, low-priority: full-depth read of Stănișor 2013 to assess behavioural-d′ implications)
  - CR-024 (literature, medium-priority: add stubs for Peck 2009 LIP-reward and Serences 2008 fMRI-V1-reward)
  - CR-025 (replication, low-priority, depends on CR-005: add a sensitivity-side reward channel to the model and re-evaluate CF/VDA decomposition)
  - CR-026 (re-derivation, medium-priority: analytically compute R(P1)-R(P2) at V=0.75 across (r,v) sweep, determine whether C3b is a theorem of the model or a numerical observation)
---

# C3 literature attack — paper's §5.2 categorical "negligible VDA at V ≥ 0.75" claim survives but is constrained by Stănișor et al. 2013 V1 reward modulation

## What I attacked

C3 (mission §2.6): "VDA is confined to a narrow regime — low cue
validity (V near 1/N), high value contrast (v ≫ 1), moderate
benefit/cost asymmetry (r ∈ [0.2, 1.0])." The operational version is
the paper's §5.2 categorical experimental-design wording:
"Standard spatial cueing paradigms with high validity (V ≥ 0.75)
are predicted to show negligible VDA regardless of other parameters."
This is the strongest, most falsifiable version of C3 and the version
this run targets.

Per mission §3.2, the attack vector chosen is *literature*. The
backlog had two duplicate seed tasks on this claim (CR-003 from
bootstrap; CR-020 spawned by CR-002 with overlapping scope); I
merged them into a single CR-020 execution, with CR-003 marked
abandoned and noted as merged.

## How I attacked it

(i) Read paper §5 in full to pin down the exact testable wording
(read pages 5-8, including Figures 5, 6, and the §5.2 prose). (ii)
Wiki sweep per mission §11.1 anchors: value-directed attention,
reward-modulated attention, attentional capture, selection history,
criterion shift, signal detection theory, normalization model,
priority map, dopamine, change detection, Posner cueing, cue
validity, surround suppression, lateral inhibition. (iii) Read
14 relevant wiki entries at full depth. (iv) Identified one
literature gap — the wiki was silent on the canonical high-V ×
value-magnitude × early-visual-cortex experiment paradigm. (v) Made
one targeted PubMed fetch (Stănișor[Author] AND V1 AND reward),
which returned Stănișor et al. 2013 PNAS — the canonical paper. (vi)
Added a new wiki stub for Stănișor 2013 (depth: abstract) per
mission §4.2; ran `python3 research_db/tools/audit.py` → exit 0. (vii)
Built the evidence dossier at
`Critique/evidence/C3--narrow-regime.md` with per-source direction /
weight / verdict-use ratings. (viii) Wrote the verdict file at
`Critique/verdicts/C3--narrow-regime.md`.

Web budget used: **1 of 2 fetches** (PubMed search + metadata get
counted as one logical fetch); under the soft cap (§4.3). No
WebFetch / WebSearch needed.

## What I found

Decomposing C3 into two sub-claims clarifies the evaluation:

**C3a (VDA at low V, V ≈ 1/N):** **Confirmed by the
value-driven-attentional-capture literature.** Failing & Theeuwes
2018 (review) and Hickey, Chelazzi & Theeuwes 2010 (single-trial
reward at V = 1/N) both document robust reward-driven attentional
bias on RT (10–60 ms slowing), N2pc, saccade trajectory, fMRI BOLD.
Effects persist for ≥6 months and are robust across labs.

**C3b (negligible VDA at V ≥ 0.75 regardless of other parameters):**
**Weakly supported, with one significant constraint.**

Three pieces of support from the wiki:
- Luo & Maunsell 2018: high-V cueing in macaques with reward
  asymmetry deliberately used to induce criterion shifts. Reward
  loads on β, not d′. *Caveat:* the experimental design was built
  around the SDT decomposition the paper's model formalises;
  partial circularity.
- Sridharan et al. 2017: re-analysis of four published SC
  manipulation studies (all high V); SC contributes primarily to
  choice bias, not sensitivity.
- Maunsell 2015 review: the standard primate-physiology
  decomposition has V4 / IT carrying d′ modulation (validity-
  driven) and LPFC / subcortical carrying β modulation (reward-
  driven).

One significant constraint from the new stub:
- Stănișor et al. 2013 PNAS ([DOI](https://doi.org/10.1073/pnas.1300117110),
  PMID 23676276; full-depth read deferred, abstract: "*relative
  value and top-down attention engage overlapping, if not identical,
  neuronal selection mechanisms*"). High effective V curve-tracing
  task with reward magnitude varied across stimuli; V1 single-unit
  activity is significantly predicted by relative reward value, with
  attention-like latency and per-cell value/attention covariation.
  This is the missing high-V × value-magnitude × early-visual-cortex
  test that the wiki was silent on. *Prima facie* in tension with
  §5.2 "negligible VDA regardless of other parameters."

The tension is *not yet a refutation*. The V1 single-unit effect
could in principle be a criterion-side decision-readout correlate
rather than a true sensitivity gain. Resolving this requires either
a full-depth read of Stănișor 2013 (spawned as CR-023) or an
independent SDT-aware experiment that decomposes the behavioural
effect at high V × variable reward.

## Verdict movement

C3 had no prior verdict file. This run sets the verdict to
**WEAKLY-SUPPORTED** (mission §3.1) — one attack vector run
(literature); the literature is consistent with C3a (low-V
confirmation) and with the *spirit* of C3b (high-V criterion
dominance) but the §5.2 categorical wording is constrained by the
Stănișor 2013 V1 result, which is the canonical high-V × value
experiment in the literature.

Per mission §3.1, elevation to CONFIRMED-UNDER-ATTACK requires a
second distinct attack vector. The natural second attack is a
**re-derivation attack** (spawned as CR-026): analytically compute
$R(P_1) - R(P_2)$ at V = 0.75 across the (r, v) sweep with the
paper's reference parameters, and determine whether the bound is
*always* below 0.005 (the paper's "negligible" threshold) for *all*
(r, v) — i.e., whether C3b is a theorem of the model or a numerical
observation. The re-derivation either elevates C3 to CONFIRMED-
CONDITIONAL (if C3b is a theorem under the model's assumptions, with
caveats about whether the model's assumptions hold biologically) or
moves it to CONTESTED (if it is only a numerical observation about
specific parameters).

A weaker reformulation that the literature would *unambiguously*
support is drafted in the verdict's V0.1 section.

## Next-attack recommendation

**CR-026 (re-derivation, medium priority).** Compute
$\sup_{(r, v) \in \text{swept space}} [R(P_1) - R(P_2)]$ at
V = 0.75 analytically, using the closed-form machinery built in
the CR-001 derivation. If the supremum is bounded below the
paper's "negligible" threshold (0.005 of reward units), C3b is a
theorem of the model and the verdict elevates. If not, the §5.2
categorical wording is too strong even internal to the model.

The re-derivation is *cheaper* than the alternative second-attack
candidate (CR-023, full-depth Stănișor read) and is more
informative: it adjudicates whether the §5.2 wording is a property
of the model itself or a property of one particular parameter
choice. Stănișor (CR-023) remains spawned but at lower priority
because its outcome only matters once we know whether the model's
prediction is a theorem or a sensitivity.

## Wiki cross-references

See verdict body's "Wiki cross-references" sub-block for the full
per-entry breakdown. Summary:

- 14 wiki entries consulted at full depth; 10 cited in the
  verdict body, 4 additional consulted but unrelated on
  inspection or already-subsumed by cited entries.
- 1 new wiki stub added (Stănișor et al. 2013;
  `stanisor2013_v1_value_attention`) at depth: abstract.
- Audit script run after stub addition: exit 0.
- 4 follow-up tasks spawned: CR-023 (Stănișor full-depth read),
  CR-024 (Peck 2009 + Serences 2008 stubs), CR-025 (replication-
  attack adding sensitivity-side reward channel), CR-026
  (re-derivation attack — the recommended next pick).
