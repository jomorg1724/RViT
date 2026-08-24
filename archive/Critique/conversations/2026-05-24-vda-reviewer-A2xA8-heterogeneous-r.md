---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.2
run_id: run-015
started: 2026-05-24T15:33:07Z
ended: 2026-05-24T15:58:00Z
worked_on: A2
attack_vector: re-derivation
verdict_touched: A2--single-global-r
verdict_after: CONFIRMED-CONDITIONAL
papers_read: [reynolds_heeger2009_normalization, mcadams_maunsell1999_v4_tuning, treue_martinez_trujillo1999_feature_attention, sani2017_temporal_v4_gain, ghose_maunsell2002_task_timing, carrasco2011_visual_attention_25y, maunsell2015_attention_mechanisms, reynolds_chelazzi2004_attentional_modulation, koch_ullman1984_winner_takes_all, itti_koch2001_saliency_review, wang_theeuwes2018_statistical_learning_distractor_suppression, luo_maunsell2018_criterion_sensitivity, bisley_mirpour2019_priority_map, bisley_goldberg2010_parietal_priority, rust_cohen2022_priority_coding, cameron2002_covert_attention_contrast, coalition_resource_competition]
papers_added: []
spawned_tasks: [CR-051]
---

# A2×A8 — within-display heterogeneous $r_i$ does not bias C1–C5 (bounded)

## What I attacked

**A2** (mission §2.7; paper §2.4): the benefit/cost asymmetry is governed by a
**single global** ratio $r$ ($\beta(r)=2r/(r+1)$, $\gamma(r)=2/(r+1)$), named as a
limitation in §5.5 ("real neural circuits may have location-specific,
feature-specific, or time-varying asymmetries"). The v0.1 literature attack
(CR-007/run-014) settled the *premise* — within-display heterogeneity (reading R2)
is empirically real — but left the *consequence* for C1–C5 unresolved. This run
(CR-048) is the designated second vector: a **re-derivation of the A2×A8
interaction**, attacking whether a per-location ratio vector $r_i$ shifts any
headline number.

## How I attacked it

Re-derivation (mission §3.2), reusing the validated general-$N$ optimal-observer
model (`A8--heterogeneous-uncued/run.py`, CR-036/CR-045) with the single $r$
promoted to a per-location vector $r_i$ — only the per-location departure scaling
$s_i\in\{\beta(r_i),\gamma(r_i)\}$ changes; the baseline $d'_{\text{base}}$ is
$r$-independent. I extended the CR-045 exchange-symmetry machinery, then
corroborated with two independent grid scripts
(`Critique/replications/A2xA8--heterogeneous-r/`).

## What I found

The A2×A8 interaction is real but **bounded — no headline claim is shifted**.

1. **Criticality breaks (as predicted).** Distinct $r_i\Rightarrow$ distinct
   transfer functions $\Rightarrow\mathbb E[R]$ no longer symmetric in the uncued
   allocations, so the $S_{N-1}$ argument fails: equal-split is *generically not a
   critical point*. Closed form: $g_i=M_i\cdot\gamma_i\rho$ depends on slot $i$ only
   through $r_i$ (derivation Eq. 1.2); tangent gradient $\|g-\bar g\|=7.2\times
   10^{-2}$ at ±30% vs $0$ at homogeneity (verified). The optimum tilts budget
   *toward the more cost-dominant (smaller-$r_i$) slots*.
2. **But the deviation is $O(\mathrm{var}\,r_i)$ and tiny.** The restricted Hessian
   stays negative-definite on the smooth branch by the *same* log-concavity-of-$\Phi$
   argument as CR-045, applied per slot (the no-FA spreading force is
   $r$-independent in sign). So the optimal tilt is $O(\text{spread})$ and its
   reward $O(\mathrm{var}\,r_i)$: **$\max\Delta R=1.50\times10^{-4}$ over all
   interior cells at ±30% — the CR-045 homogeneous-case grid slack itself.**
3. **Cued-absorption pre-emption is $r$-independent.** The C4 mechanism ($w_c\ge
   w_u$ + location-count) has no $r$ in it, so the budget is cued-absorbed
   ($\alpha^\star\to1$, $B\to0$) at every value-contrast cell — $\Delta R=0$ exactly
   at the C2 headline cell. At the cost-dominant P3 kink the spreading force keeps
   equal-split optimal ($\Delta R=0$), so the **criterion fraction is untouched**.
4. **Level effect (A8 imposed) — C2 reframes.** VDA peak essentially fixed
   ($0.0771\to0.0770$, $r_{\text{peak}}=0.398$) under ±30%; $k=1.5/3$ spreads keep
   it $0.0765$–$0.0798$ @ $r_{\text{cued}}\approx0.36$. C2 reframes as a statement
   about $r_{\text{cued}}$ (run-014 conjecture confirmed). C4 robust ($r$-independent
   geometry); C1 contested corner not deepened ($0.3040\to0.3055$). Validation:
   spread $0$ reproduces the single-$r$ model exactly.

## Verdict movement

A2 **WEAKLY-SUPPORTED → CONFIRMED-CONDITIONAL**. Two distinct vectors (literature
run-014 + re-derivation run-015) now agree that the single-$r$ reliance does not
bias C1–C5. CONFIRMED-**CONDITIONAL** (not -UNDER-ATTACK) because the *premise* is
false under R2 (we confirm *safety despite a false premise*) and the safety is
conditional on **equal uncued validity** + **moderate $r_i$ spread** (deviation is
$O(\mathrm{var}\,r_i)$). This completes the A2/A3/A8 heterogeneity arc: A8 and the
R1-reading of A2 are discharged by the optimiser's own behaviour (cued-absorption +
log-concavity spreading, both $r$-independent); only A3 (conservation *form*)
remains CONTESTED.

## Next-attack recommendation

Open **A1** (CR-006, literature) — the paper's first-named §5.5 limitation
(independent per-location SDT decisions), with the richest wiki coverage
(`cohen_maunsell2009_correlations`); A1/A6 also surfaced here as the next link in
the assumption chain (the per-slot gradient of §1 presumes independence + a
homogeneous decision rule). Alternatively **CR-049** (the full-resolution C2
reframing replication, now de-risked by this run's $O(\mathrm{var})$ bound) or
**CR-011** (A6). Recommend CR-006: it advances assumption-layer coverage (A1 is
untouched) and is the connective prerequisite the A2×A8 cross-terms point to.

## Wiki cross-references

- [[reynolds_heeger2009_normalization]], [[mcadams_maunsell1999_v4_tuning]],
  [[treue_martinez_trujillo1999_feature_attention]], [[sani2017_temporal_v4_gain]],
  [[ghose_maunsell2002_task_timing]], [[carrasco2011_visual_attention_25y]],
  [[maunsell2015_attention_mechanisms]],
  [[reynolds_chelazzi2004_attentional_modulation]] — re-cited; the R2-heterogeneity
  cluster (v0.1) that motivates the per-location $r_i$ this run bounds.
- [[koch_ullman1984_winner_takes_all]], [[itti_koch2001_saliency_review]] — cited;
  WTA = the concentration pressure cued-absorption pre-empts ($r$-independently).
- [[wang_theeuwes2018_statistical_learning_distractor_suppression]] — cited; the
  heterogeneous-*validity* (A8) axis, distinct from the heterogeneous-$r$ (A2) axis.
- [[luo_maunsell2018_criterion_sensitivity]] — cited; distinct benefit/cost
  substrates; bridge to A1/A6 (Loose-end #3).
- [[bisley_mirpour2019_priority_map]], [[bisley_goldberg2010_parietal_priority]],
  [[rust_cohen2022_priority_coding]] — the LIP priority map is the $N$-dim substrate
  the scalar $r$ + homogeneous allocation project away; natural locus of learned
  $r_i$ heterogeneity; noted.
- [[cameron2002_covert_attention_contrast]] — surfaced by the sweep; near-threshold
  contrast regime, not the $r$-uniformity question; unrelated on inspection.
- concept [[coalition_resource_competition]] — finite-resource/zero-sum framing +
  PRISM bridge; cited for §3.5.
- **Math-methods gap:** majorization/Schur-concavity, $S_{N-1}$ standard rep,
  log-concavity of $\Phi$ — no wiki substrate (expected; mirrors C5/A8 gaps).
- §11.1 value-source anchors ([[failing_theeuwes2018_selection_history]],
  [[hickey2010_reward_salience_acc]], [[stanisor2013_v1_value_attention]],
  [[glimcher2011_dopamine_rpe]], dopamine/RPE/basal-ganglia) — value *source*, not
  asymmetry *form*; unrelated on inspection.
