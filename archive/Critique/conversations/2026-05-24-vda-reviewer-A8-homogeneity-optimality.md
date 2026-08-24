---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.2
run_id: run-013
started: 2026-05-24T04:42:58Z
ended: 2026-05-24T05:05:00Z
worked_on: A8
attack_vector: re-derivation
verdict_touched: A8--heterogeneous-uncued
verdict_after: CONFIRMED-CONDITIONAL
papers_read: [wang_theeuwes2018_statistical_learning_distractor_suppression, koch_ullman1984_winner_takes_all, itti_koch2001_saliency_review, desimone_duncan1995_biased_competition, reynolds1999_competitive_v2_v4, reynolds_heeger2009_normalization, luo_maunsell2018_criterion_sensitivity, maunsell2015_attention_mechanisms, sridharan2017_sc_sensitivity_bias, muller_findlay1987_sensitivity_criterion, bisley_mirpour2019_priority_map, bisley_goldberg2010_parietal_priority, rust_cohen2022_priority_coding, cohen_maunsell2009_correlations, coalition_resource_competition]
papers_added: []
spawned_tasks: [CR-048]
---

# A8 re-derivation: homogeneity-optimality + cued-absorption ⇒ CONFIRMED-CONDITIONAL

## What I attacked

Assumption **A8** (mission §2.7; paper §2.2 verbatim: *"the remaining attention
is distributed equally among uncued locations, so each receives
$(1-\alpha)/(N-1)$"*) — the homogeneous-uncued-allocation assumption that
collapses the policy space to one dimension in $\alpha$. It was left
`WEAKLY-SUPPORTED` by the CR-036/run-012 replication, which showed *numerically*
that homogeneity is the optimum (not just the assumption) at the swept cells but
flagged that it is not a trivially-free choice (it binds under a forced
benefit-dominant uncued budget). I executed **CR-045**, the designated second
attack vector: a closed-form re-derivation of the two propositions the
replication established only numerically.

## How I attacked it

Re-derivation, reusing the C4 location-count / value-weight machinery
(`Critique/derivations/C4--no-inversion.md` §6), with independent numerical
corroboration (not reusing CR-036's `run.py`). I proved:

(a) **Homogeneity-optimality.** $\mathbb{E}[R]$ is a symmetric function of the
uncued allocation (equal uncued validity ⇒ exchangeable slots), so the equal
split is *always* a critical point on the uncued simplex (exact). The stabiliser
$S_{N-1}$ acts irreducibly on the zero-sum tangent space, so by Schur's lemma the
restricted Hessian is a single scalar $\lambda I$; I derived $\lambda$ in closed
form on the smooth $\gamma$-branch and signed it.

(b) **Cued-absorption pre-emption.** I showed the two concentration pressures
(accelerating $h$; benefit-dominant kink) are subsets of the winner-take-all
regime, and that the value-weight inequality $w_c\ge w_u$ + the location-count
asymmetry drive $\alpha^\star\to1$ there — emptying the uncued budget before
concentration can act.

Verification: `Critique/replications/A8--heterogeneous-uncued/cr045_rederivation_check/`
(two scripts + logs).

## What I found

- **Equal split is an exact critical point** for every $r,h$ (exchange
  symmetry); numerically $\mathcal V'(0)=O(10^{-5})$.
- **Closed-form $\lambda=\lambda_{\mathrm{HR}}+\lambda_{\mathrm{noFA}}$
  (derivation Eq. 2.4) matches a fixed-criterion finite difference to 5 decimal
  places** across all four $h$ and $r\in\{0.398,0.5,1,2\}$. The no-FA term
  $\lambda_{\mathrm{noFA}}=Q[G^2g'^2(\log G)''+G G_d g'']\le0$ **unconditionally**
  for concave/linear $h$ because $\Phi$ is **log-concave** — the correct-rejection
  channel is a pure spreading force. So $\lambda<0$ (equal split = strict max)
  for $a^{0.3},\sqrt a,a$; only accelerating $a^2$ gives smooth-branch
  $\lambda>0$ ($+0.024$ to $+0.048$).
- **The forced-uniform-budget "concentration" (CR-036 Part 1b) is a CUSP, not a
  curvature.** At $\alpha=1/N$ the uncued sit on the $\beta/\gamma$ kink;
  $\mathcal V(t)=\mathcal V(0)+m|t|+O(t^2)$ with
  $\operatorname{sign}(m)=\operatorname{sign}(\beta-\gamma)=\operatorname{sign}(r-1)$.
  Verification: one-sided slope → nonzero constant ($-0.021$ at $r{=}0.5$,
  $+0.021$ at $r{=}2$, $\approx0$ at $r{=}1$) while the central second difference
  scales as $1/\varepsilon$. CR-036's finite "$R''(0)>0$" was measuring this cusp
  slope; I replaced the $\varepsilon$/grid-dependent magnitudes with the exact
  first-order law.
- **Cued-absorption is decisive and the mutual exclusion is tight.** Optimising
  jointly over $(\alpha,\text{uncued winner share})$ from scratch on the paper's
  $\Delta\alpha=0.005$ grid: $\max|\Delta R_{\text{uncon}-\text{homog}}| =
  1.4\times10^{-4}$ over **all four $h$ and all swept regimes** — and for the
  accelerating $a^2$ (the only $\lambda>0$ case) cued-absorption is *total*
  ($\alpha^\star=1$, $B=0$ exactly, $\Delta R=0$ exactly). The more $h$
  accelerates, the harder the optimum empties the uncued budget — the two effects
  are perfectly anti-correlated.

## Verdict movement

**WEAKLY-SUPPORTED → CONFIRMED-CONDITIONAL.** Two distinct vectors (replication
run-012, re-derivation run-013) have now failed to falsify A8, with the closed
forms validated against independent finite differences — mission §3.1 licenses
elevation. The label is CONFIRMED-**CONDITIONAL** (not -UNDER-ATTACK) because the
no-bias result is conditional on (i) equal uncued validity (heterogeneous
validity → a graded suppression the homogeneous model cannot represent — a scope
enrichment, not a C1–C5 bias) and (ii) excludes the degenerate value-blind
$V{=}1/N,v{=}1$ corner (vacuous). A8 is now the **best-defended of the paper's
simplifications**: relaxing it changes nothing within the grid
($\Delta R\le1.4\times10^{-4}$), because the optimiser would make A8's choice
unprompted — in sharp contrast to A3 (CONTESTED), the paper's one *named* §5.5
limitation that actually moved a headline conjunct.

## Next-attack recommendation

The A8 thread is now settled (two vectors, CONFIRMED-CONDITIONAL); its remaining
followups (CR-046 resolution hygiene, CR-047 graded-suppression at $N>4$) are
sharpening, not verdict-moving. The substantive frontier is the **untouched
assumptions A1, A2, A4, A5, A6, A7**. The single most informative next pick is
**CR-007 (A2, single global $r$)** by literature attack: the A8 re-derivation
showed that its symmetry argument depends on a *single global $r$* (homogeneous
gain asymmetry) — under heterogeneous $r_i$ the uncued slots stop being
exchangeable even at equal validity, so A2 and A8 interact. A2 is also the cousin
of the now-CONTESTED A3 (conservation form) and the now-confirmed A8 (allocation
geometry), so attacking A2 unifies the three "heterogeneity" assumptions into one
arc. **CR-006 (A1 independence)** is the alternative — it is the assumption the
paper itself names first in §5.5 and the one with the richest wiki coverage
(`cohen_maunsell2009_correlations` is the canonical entry). I recommend **CR-007
before CR-006** because of the A2↔A8↔A3 connective tissue this run exposed.

## Wiki cross-references

- [[wang_theeuwes2018_statistical_learning_distractor_suppression]] — cited: the
  heterogeneous-validity enrichment reproduces its suppression gradient (the
  equal-validity conditional's scope boundary).
- [[koch_ullman1984_winner_takes_all]], [[itti_koch2001_saliency_review]] —
  cited: WTA = the concentration pressure pre-empted by cued-absorption.
  (`tsotsos1988_complexity_vision` surfaced as an extra WTA entry; noted, not
  load-bearing.)
- [[desimone_duncan1995_biased_competition]], [[reynolds1999_competitive_v2_v4]],
  [[reynolds_heeger2009_normalization]] — cited: zero-sum / divisive-normalization
  backdrop of budget conservation (freed budget → cued).
- [[luo_maunsell2018_criterion_sensitivity]], [[maunsell2015_attention_mechanisms]],
  [[sridharan2017_sc_sensitivity_bias]], [[muller_findlay1987_sensitivity_criterion]]
  — cited: the SDT criterion/sensitivity substrate behind the
  $\lambda_{\mathrm{HR}}$ vs $\lambda_{\mathrm{noFA}}$ decomposition.
- [[bisley_mirpour2019_priority_map]], [[bisley_goldberg2010_parietal_priority]],
  [[rust_cohen2022_priority_coding]] — cited: the LIP priority map = the
  $N$-dimensional substrate A8 projects to a scalar (lossless for behaviour in
  the swept regimes, lossy under heterogeneous validity).
- [[coalition_resource_competition]] (concept) — cited: finite-resource / zero-sum
  framing; cued-absorption = "highest-priority coalition member captures the
  shared resource" (PRISM bridge).
- [[cohen_maunsell2009_correlations]] — noted: A1 (cross-location independence),
  the assumption interacting with A8 under heterogeneity; central to CR-006.
- **Math-methods gap (no wiki substrate):** log-concavity of $\Phi$,
  Schur-concavity/majorization, $S_{N-1}$ standard-representation — no entry; the
  lone "Schur" grep hit is *Schurgin* (WM precision), unrelated. Expected gap,
  mirrors the C5 floating-point gap; flagged not filled.
- §11.1 anchors **unrelated on inspection**: dopamine/RPE/basal-ganglia (value
  source), FEF/SC microstim (causal foundation), V4 within-RF gain (not
  across-location), change-detection/Posner (task foundation),
  `gupta_sridharan2024` (C4 failure-of-facilitation).
