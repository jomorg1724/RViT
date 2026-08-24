---
type: conversation
agent: skeptical-reviewer
prompt_version: "0.2"
run_id: run-018
started: 2026-05-25T15:29:00Z
ended: 2026-05-25T15:58:00Z
worked_on: A6
attack_vector: re-derivation
verdict_touched: A6--heterogeneous-decision-rule
verdict_after: WEAKLY-SUPPORTED
papers_read: [luo_maunsell2018_criterion_sensitivity, lu_dosher1998_external_noise]
papers_added: []
spawned_tasks: [CR-056, CR-057]
---

# A6 — is the homogeneous decision rule load-bearing for the criterion-vs-attention decomposition?

## What I attacked

A6 (mission §2.7): the paper's per-location SDT uses **homogeneous decision
machinery** — the same equal-variance Gaussian transform (internal noise
σ=1) everywhere; only $d'_i$ (attention) and $c_i$ (the optimiser) vary
(paper §2.2, implicit). A6 is the unstated half of the §5.5 limitation
("real observers emit a single global response") that run-017/CR-052 split
off from A1, and it is the premise behind §5.1's load-bearing claim that
criterion "can independently encode value at each location" — i.e. that the
criterion fraction (C1) is a clean two-mechanism partition. First verdict on
A6; the fifth assumption to receive one. Folded in CR-055 (the Booking-2 = A6
pointer). Picked per mission §3.3: A6 is the highest-priority OPEN verdict
(medium; A4/A5/A7 are low), prereqs settled — the default pick, no override.

## How I attacked it

Re-derivation (`Critique/derivations/A6--heterogeneous-decision-rule.md`)
with independent numerical corroboration reusing the C1/C5 P1 optimiser
(`Critique/replications/A6--heterogeneous-decision-rule/`). I introduced a
per-location decision-noise scale $s_i=\sqrt{1+\sigma_{d,i}^2}\ge1$ (paper =
$s_i\equiv1$) so $\mathrm{HR}_i=\Phi((d'_i/2-c_i)/s_i)$,
$\mathrm{FAR}_i=\Phi((-d'_i/2-c_i)/s_i)$, and tested two readings of A6:
fixed heterogeneous machinery (Prop 1), attention-coupled noise (Prop 2),
and sketched the §5.5 single-global-response reading (A6-(ii)).

## What I found

- **Prop 1 — fixed heterogeneous noise is BENIGN (proved exactly).** The rate
  map obeys $\Phi((d'/2-c)/s)=\Phi(\tilde d'/2-\tilde c)$ with $\tilde d'=d'/s$,
  $\tilde c=c/s$ (numerically $1.1\times10^{-16}$). Since the criterion is a
  free bijection, the entire P1–P4 set equals the paper's at rescaled
  sensitivities $d'\to d'/s$, so $\mathrm{CF}(s_c,s_u)=\mathrm{CF}_{\text{paper}}|_{d'\to d'/s}$
  exactly. Numerically (non-clipping criterion grid) CF the two ways agrees to
  $\le1.7\times10^{-5}$, → 0 as $\Delta c\to0$. Fixed heterogeneous machinery
  is a per-location $d'$-perturbation; the decomposition's *structure* is
  invariant (it moves CF's value, e.g. $0.728\to0.789$ at $s_u=2$, but not its
  interpretation).
- **Prop 2 — attention-COUPLED noise is a third lever.** With $s_i=s(a_i),s'<0$
  (empirically motivated: `lu_dosher1998` internal-noise suppression;
  `luo_maunsell2018` correlation/Fano modulation; `cohen_maunsell2009`
  decorrelation), $\partial_\alpha(d'_c/s_c)$ gains a noise-reduction term, so
  the $R(\mathrm{P1})-R(\mathrm{P3})$ increment the CF books to "attention"
  bundles two mechanisms. With $s(a)=\sqrt{1+\kappa(1-h(a))}$, CF at the
  headline cell **deflates** $0.728\to0.626$ ($\kappa{:}0\to1$, wide-grid
  guard) while total gain *grows* $0.62\to0.78$. Same direction as the A1-$\rho$
  result.
- **A6-(ii) single global response.** A single global criterion removes the
  per-location DOF §5.1 calls criterion's advantage; $G_{\text{crit}}^{\text{global}}\le G_{\text{crit}}^{\text{per-loc}}$
  (strict when $v>1,V\ne1/N$) ⇒ CF compounds downward (the CR-055 prediction).
  A pooled decision rule also dissolves the Eq. 9 FA product = the A1 locus,
  so §5.5's two clauses are coupled.
- **Validation:** $s\equiv1$ reproduces C1's CF (0.7282) and C2's VDA peak
  (0.0797@0.398). A criterion-grid clipping trap was caught and fixed (the
  default [-3,3] grid silently clips the uncued criterion at large $s$,
  spuriously inflating CF; widening to [-8,8] restored the Prop-1 identity to
  1.7e-5).

## Verdict movement

A6 (none) → **WEAKLY-SUPPORTED**. First touch, one vector. The literal A6
relaxation failed to break the decomposition (Prop 1, confirming) so not
CONTESTED — **no headline number shifts within the paper's stated model**
($s\equiv1$, per-location criteria); both cracks require model extensions.
Per mission §6 one vector cannot elevate to CONFIRMED-*. The result mirrors
A1/A2 first touches: premise shown vulnerable, not yet consequential within
scope. Referee statement: the criterion fraction is a clean
criterion-vs-attention partition **iff** attention acts only on $d'$ (no
attention-modulated decision noise) **and** the criterion is per-location (no
single global response) — two premises the paper neither states nor (§5.5)
believes.

## Next-attack recommendation

**CR-056** (A6 second vector, **replication**): constrain $c_c=c_u$ (single
global criterion) in the C1 criterion-fraction optimiser and re-run the
4,410-cell grid; measure the CF deflation predicted by the derivation's
inequality (12). This settles A6 → CONFIRMED-CONDITIONAL (if CF holds up) or
CONTESTED (if the single-global-criterion deflation is material within the
grid). It directly tests §5.1's "criterion can independently encode value at
each location" and the CR-055 prediction, reusing the C1 optimiser with a
one-line constraint.

## Wiki cross-references

(Full sweep block in the verdict file.) `luo_maunsell2018_criterion_sensitivity`
— cited (attention's dissociable criterion+sensitivity substrates; modulates
correlation/Fano, not only rate). `lu_dosher1998_external_noise` — cited (the
3-mechanism taxonomy; internal-noise suppression = the omitted $s(\alpha)$
channel; PRISM probe). `mcadams_maunsell1999_reliability`,
`hawkins1990_attention_detectability` — cited (fair legs: real multiplicative
gain; field-standard SDT idealisation). `cohen_maunsell2009_correlations` —
cited (empirical $s'(\alpha)<0$). `muller_findlay1987_sensitivity_criterion`,
`sridharan2017_sc_sensitivity_bias`, `solomon2004_cues_sensitivity` — cited
(SDT criterion/sensitivity dissociation tradition). `ernst_banks2002_cue_combination`
— cited (A6-(ii) optimal pooling). `gold_shadlen2007_decision_making`,
`ratcliff1978_drift_diffusion`, `hanks_summerfield2017_perceptual_decisions`,
`roitman_shadlen2002_lip_rt` — spawned CR-056 substrate, not read in depth.
`reynolds_heeger2009_normalization` — noted (gain substrate, orthogonal).
`coalition_resource_competition`, `competition_emergent_predictive_coding`,
`multi_hub_multi_objective_system` (concepts) — cited (PRISM bridge).
dopamine/RPE/priority-map/LIP/FEF/saccade §11.1 anchors — unrelated on
inspection. No new stub → no audit.py. 0 web fetches.
