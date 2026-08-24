---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.2
run_id: run-016
started: 2026-05-24T21:08:36Z
ended: 2026-05-24T21:40:00Z
worked_on: A1
attack_vector: literature
verdict_touched: A1--independence
verdict_after: WEAKLY-SUPPORTED
papers_read: [cohen_maunsell2009_correlations, ruff_cohen2016_cross_area_correlations, srinath2021_attention_information_flow, mcadams_maunsell1999_reliability, hawkins1990_attention_detectability, ernst_banks2002_cue_combination, luo_maunsell2018_criterion_sensitivity, reynolds_heeger2009_normalization]
papers_added: []
spawned_tasks: [CR-052, CR-053]
---

# A1 — per-location SDT independence (first verdict, literature attack)

## What I attacked

Assumption **A1** (mission §2.7): per-location SDT decisions are independent.
The paper states it verbatim in §2.1 (*"The observer makes independent
detection decisions at each location using signal detection theory"*,
Eqs. 1–2), operationalises it in **Eq. (9)** as the product
$P_{\text{no-fa}}=(1-\mathrm{FAR}_c)(1-\mathrm{FAR}_u)^{N-1}$, and names it in
§5.5 with a *directional* self-characterisation: independence makes the
reported numbers *"an upper bound on VDA benefit."* This was the highest-
priority OPEN verdict (no WEAKLY-SUPPORTED verdicts remained after run-015)
and the explicit run-015 recommendation — the paper's first-named limitation
with the richest wiki coverage.

## How I attacked it

Literature attack (CR-006). The job per the backlog is to *quantify how
consequential* independence is, not to repeat that it exists. I separated two
readings the literature forces apart (mirroring the A2 R1/R2 move): **I-dec**
(decision-level — the Eq. 9 product needs FA-event independence) and **I-neur**
(neural-level — per-location $d'$ as a marginal vs. cortex's
$d'^2\propto(\Delta\mu)^\top\Sigma^{-1}(\Delta\mu)$). §11 sweep over the
noise-correlation / interneuronal-correlation / pooling / SDT cluster plus the
§11.1 anchors; read 6 full-depth entries across three axes (correlation
structure, single-unit-vs-population coding, the per-location-SDT behavioural
convention) and classified each supports / contradicts / constrains.

## What I found

**The premise is empirically false at the population level, in the paper's own
paradigm.** [[cohen_maunsell2009_correlations]] — macaque orientation
change-detection with a peripheral validity cue, exactly the paper's task
class — finds noise correlations $r_{SC}\approx0.20$ (substantial), and that
**>80%** of attention's population-sensitivity benefit comes from *reducing*
those correlations, with single-neuron rate gain recovering <20%. The covariance
structure is sign-dependent on anatomical scope
([[ruff_cohen2016_cross_area_correlations]]: within-area down, cross-area up)
and has a supra-pairwise component ([[srinath2021_attention_information_flow]]:
~2/3 of the cross-population gain is shared-variance amplification not reducible
to $\rho$).

**Independence is load-bearing for C1.** It is precisely the Eq. (9) product.
Closed form: model the no-change-trial decision variables as equicorrelated
Gaussian; then $P_{\text{no-fa}}=\Phi_N(\mathbf c;R_\rho)$ and by **Slepian's
inequality** $\Phi_N(\mathbf c;R_\rho)\ge\prod_i(1-\mathrm{FAR}_i)$ for
$\rho>0$, monotone in $\rho$. The independent product is therefore the
**FA-penalty-maximising corner** — positive correlations relax the
multiple-comparisons pressure that shapes the optimal criteria, so the
criterion fraction is computed at a boundary point in correlation space.

**The two-tool taxonomy is incomplete.** Correlation reduction is neither
criterion shift nor $d'$-reallocation; the model's scalar $d'(\alpha)$
conflates marginal gain ([[mcadams_maunsell1999_reliability]]: real,
multiplicative, Fano-flat — the $d'$ tool is genuine) with decorrelation. So
"criterion captures 60–96% of the reward gain" is a within-model decomposition,
not a claim about cortex's mechanism inventory.

**But A1 is the field-standard behavioural idealisation**
([[hawkins1990_attention_detectability]] and the SDT-of-attention tradition
analyse cued detection per-location), and optimal multi-location pooling only
*reduces* to the independent product when noise is uncorrelated
([[ernst_banks2002_cue_combination]] §6 states correlated noise breaks the
simple optimal rule) — which is exactly the §5.5 "single global response"
concern made precise.

**The "upper bound on VDA" claim is underived and sign-ambiguous.** Neural-
decorrelation reading: value-directed decorrelation would add a value channel
outside the model → real VDA could *exceed* the model's → claim wrong.
Decision-aggregation reading: fewer global-criterion DoF could raise VDA
reliance (against the claim) *or* positive $\rho$ relaxing the FA penalty could
make criterion more effective (supporting it). Literature cannot settle the
sign.

## Verdict movement

A1 **(none) → WEAKLY-SUPPORTED**. Per mission §6, one vector cannot elevate to
CONFIRMED or refute. Not CONTESTED because no attack *shifted a headline
number* this run — A1 is a named, pre-empted, field-standard idealisation whose
$d'$ tool is real; the contradiction lives at the neural-population level the
model does not claim to resolve. The honest residual is the **sign of the
"upper bound on VDA" claim**, which is a re-derivation question. This is the
same shape as the A2 run-014 first-touch (premise empirically motivated/false
under one reading, but not yet shown to *move* a headline claim).

Verdict ledger after run-016: C1 CONTESTED, C2 CUA, C3 CONTESTED, C4
CONFIRMED-CONDITIONAL, C5 CUA; A2 CONFIRMED-CONDITIONAL, A3 CONTESTED, A8
CONFIRMED-CONDITIONAL, **A1 WEAKLY-SUPPORTED**; A4/A5/A6/A7 OPEN. Four of eight
assumptions now carry a verdict.

## Next-attack recommendation

**CR-052 (re-derivation — the designated A1 second vector).** Re-derive
$P_{\text{no-fa}}$ under an equicorrelated-Gaussian / Gaussian-copula FA model
with per-location criteria re-optimised; recompute criterion fraction and VDA
at the C2 headline cell across $\rho\in[0,0.4]$ (bracketing Cohen–Maunsell).
If VDA *rises* with $\rho$, the §5.5 "upper bound" claim fails → A1 CONTESTED;
if it falls or is flat, the claim holds → A1 CONFIRMED-CONDITIONAL. This is the
decisive move and reuses the C5/A3 optimiser substrate. Secondary: **CR-053**
(literature — is decorrelation value-directed? the completeness critique only
adds a *value* channel if so; no wiki entry addresses this, likely needs a
fetched stub).

## Wiki cross-references

- [[cohen_maunsell2009_correlations]] — cited; spine of the attack (premise
  false; dominant omitted mechanism).
- [[ruff_cohen2016_cross_area_correlations]] — cited; sign-dependent covariance
  structure (constrains).
- [[srinath2021_attention_information_flow]] — cited; supra-pairwise structure
  (constrains, caps any "add $\rho$" fix).
- [[mcadams_maunsell1999_reliability]] — cited; $d'$ tool real but
  self-flagged incomplete (supports/constrains).
- [[hawkins1990_attention_detectability]] — cited; per-location-SDT is the
  behavioural standard (supports the convention; anchors WEAKLY-SUPPORTED).
- [[ernst_banks2002_cue_combination]] — cited; correlated noise breaks
  independent pooling (constrains; ties §5.5 global-response to A6/CR-011).
- [[luo_maunsell2018_criterion_sensitivity]] — cited; dissociable benefit/cost
  & criterion/sensitivity substrates (constrains).
- [[reynolds_heeger2009_normalization]] — cited; normalization changes rate
  AND correlations (constrains; omitted channel is the off-diagonal half).
- `concepts/coalition_resource_competition.md`,
  `concepts/competition_emergent_predictive_coding.md` — cited; PRISM bridge.
- §11.1 dopamine/RPE/basal-ganglia/saccade/priority-map anchors
  ([[bisley_goldberg2010_parietal_priority]], [[glimcher2011_dopamine_rpe]],
  …) — unrelated on inspection (value *source*, not decision independence).
  [[rust_cohen2022_priority_coding]] surfaced in sweep, not read this run
  (tangential priority-coding geometry).
- No new wiki stub added → audit.py not required this run. 0 web fetches.
