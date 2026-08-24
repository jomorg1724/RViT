---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.2
run_id: run-008
started: 2026-05-21T02:19:24Z
ended: 2026-05-21T02:42:00Z
worked_on: C5
attack_vector: replication
verdict_touched: C5--symmetric-recovery
verdict_after: WEAKLY-SUPPORTED
papers_read: [reynolds_heeger2009_normalization, luo_maunsell2018_criterion_sensitivity, maunsell2015_attention_mechanisms, sridharan2017_sc_sensitivity_bias]
papers_added: []
spawned_tasks: [CR-038, CR-039]
---

# C5 — does r = 1 exactly recover the symmetric special case?

## What I attacked

**C5** (mission §2.6; paper Appendix A "Validation: Symmetric Special Case", p.8 + Figure 7): "At $r = 1$, the model reduces exactly to the symmetric special case ($\beta = \gamma = 1$); optimal $\alpha^*$ and $R^*$ are identical to machine precision (maximum difference: 0.0) on 210 matched combinations ($N=4$, $d'_{\max}=2.0$, $f_0=0.5$, $\sqrt{\cdot}$)." This was the **only untouched headline claim** — C1 (CONTESTED), C2 (CONFIRMED-UNDER-ATTACK), C3 (CONTESTED), C4 (CONFIRMED-CONDITIONAL) each already carried a verdict.

I picked CR-005 over the run-007-recommended CR-036 (A8 heterogeneous-uncued replication) and over the stale high-priority CR-013 (a *third* C2 vector — but C2 is already CONFIRMED-UNDER-ATTACK, so CR-013 fails the §3.3 "OPEN/WEAKLY-SUPPORTED verdict" selection criterion). Rationale: C5 closes per-headline-claim coverage; it is bounded enough for the run budget; and its replication builds the symmetric+asymmetric P1 optimiser that CR-036 and the A3/A5/A6 assumption sweeps will reuse, so it is a natural prerequisite-in-spirit for the heavier CR-036.

## How I attacked it

**Replication** (§3.2). Built `Critique/replications/C5--symmetric-recovery/run.py`: the paper's asymmetric $d'(\alpha)$ map evaluated at $r=1$ (★) versus an independently-written symmetric "single shared transfer function" map (☆), both run through the same criterion/$\alpha$ grid optimiser (model primitives reused with attribution from the CR-002 C1 code). Swept the 210 matched combos; also ran a Sterbenz-lemma mechanism check, an $(f_0, d'_{\max})$ robustness probe, and an $r = 1 \pm \{10^{-3},10^{-6}\}$ continuity probe. Runtime ~6 s, no scipy (A&S Φ fallback — irrelevant because both models call the same Φ).

## What I found

- **C5 reproduced exactly.** On all 210 combos the cued/uncued $d'$ arrays are **bit-identical** (`np.array_equal` True); $\max|\Delta\alpha^*| = 0.0$ and $\max|\Delta R^*| = 0.0$. Matches the paper's "maximum difference: 0.0".
- **Why exact (paper doesn't say).** $\beta(1)=\gamma(1)=1$ exactly in float64; the asymmetric map then computes $a+(x-a)$ with $a=d'_{\text{base}}=1.5$, $x=d'_{\max}f(\cdot)\in[1.0,2.0]$. By **Sterbenz's lemma**, since $[1.0,2.0]\subset[0.75,3.0]=[a/2,2a]$, the round trip is bit-exact at every grid point. The "0.0" is a structural guarantee of the config.
- **"0.0" is config-specific.** Varying $(f_0,d'_{\max})$: 4 of 15 configs (low $f_0$, where $x$ leaves the Sterbenz band) drift by ~1 ulp ($10^{-17}$–$10^{-16}$). So C5-as-written is exactly right at its config, but "max diff 0.0" should not be read as universal — off-config it is "machine precision," nonzero.
- **$r=1$ is the smooth limit.** $\max|\Delta R^*| = 8.4\mathrm{e}{-5}$ at $r=1\pm10^{-3}$, $8.4\mathrm{e}{-8}$ at $\pm10^{-6}$, $0$ at $r=1$ — linear in $|r-1|$, slope $\approx0.084$. Not a knife-edge.

## Verdict movement

C5: **(none) → WEAKLY-SUPPORTED**. First touch, one attack vector (replication), claim survived intact and was reproduced *exactly* with the exactness explained (Sterbenz). Per §6 a first-touch run cannot elevate to CONFIRMED-UNDER-ATTACK; per §3.1 "direct attack failed, one vector tried" = WEAKLY-SUPPORTED, with a specific second vector requested. The config-specificity of the literal "0.0" sharpens (does not contest) the paper, which scoped its number to the validation config. Verdict ledger after run-008: C1 CONTESTED, C2 CONFIRMED-UNDER-ATTACK, C3 CONTESTED, C4 CONFIRMED-CONDITIONAL, **C5 WEAKLY-SUPPORTED** — all five headline claims now carry a verdict.

## Next-attack recommendation

**CR-038 (re-derivation)** — the cheap second vector: formalise $\beta(1)=\gamma(1)=1\Rightarrow$ (★)$\equiv$(☆) and state the Sterbenz sufficient condition as a lemma, elevating C5 to CONFIRMED-UNDER-ATTACK. After that, the assumption layer (A1–A8) is the frontier: **CR-036** (A8 heterogeneous-uncued, run-007's recommendation, now de-risked because this run built the substrate) is the natural substantive next pick.

## Wiki cross-references

- `reynolds_heeger2009_normalization` — cited (paper ref [12]); normalization = substrate for the β/gain half of $r$; bears on §5.4 not on the numerical claim.
- `luo_maunsell2018_criterion_sensitivity` — cited (paper ref [4]); criterion/sensitivity dissociation underlying P1–P4; the SDT baseline being validated at $r=1$.
- `maunsell2015_attention_mechanisms` — cited loosely; gain-vs-criterion review for the §5.4 reading of $r$.
- `sridharan2017_sc_sensitivity_bias` — noted; SDT decomposition substrate; unrelated to the identity.
- `concepts/coalition_resource_competition.md` — cited (user concept); $\beta+\gamma=2$ is zero-sum reallocation, $r=1$ = balanced coalition.
- `concepts/competition_emergent_predictive_coding.md`, `threads/the_user_architectural_program.md` — inspected for the PRISM block; conceptual link only.
- `failing_theeuwes2018_selection_history`, `hickey2010_reward_salience_acc`, `wang_theeuwes2018_statistical_learning_distractor_suppression`, `stanisor2013_v1_value_attention`, `anderson*` — unrelated on inspection for C5 (they bear on C2/C3/C4).
- Anchors {priority map, LIP, FEF, parietal, dopamine, RPE, basal ganglia, oculomotor, saccade, Posner cueing, change detection}: hits exist (`bisley_*`, `posner1980_orienting`, `herman_*`) but none bear on a floating-point / algebraic-identity claim — unrelated on inspection. No new stub added.
