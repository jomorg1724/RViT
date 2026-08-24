---
type: verdict
claim_id: A6
claim_statement: "The decision rule is homogeneous across locations (same SDT machinery everywhere); the criterion-vs-attention decomposition cleanly separates the two mechanisms."
paper_section: "§2.2 (implicit); §5.1 (why criterion dominates); §5.5 (limitation, 'single global response')"
current_label: WEAKLY-SUPPORTED
attacks_tried:
  - vector: re-derivation
    run_id: run-018
    outcome: "A6-(i) fixed heterogeneous noise proved benign (absorbed into effective d'); surfaced two conditional cracks (attention-coupled noise, single global criterion). No headline number shifted within the paper's stated model."
load_bearing_for:
  - "§4.1 criterion fraction 0.60–0.96 (C1) — the metric's interpretation as criterion-vs-attention"
  - "§5.1 'criterion can independently encode value at each location'"
  - "§5.3 implications for computational models (criterion-like vs attentional routing)"
last_updated: 2026-05-25
prompt_version_observed: "0.2"
---

# Verdict: the homogeneous decision rule and the criterion-vs-attention decomposition

## Claim as written in the paper

A6 is **unstated**; it is the implicit premise of §2.2, where the same
equal-variance Gaussian SDT transform (internal noise σ = 1) is applied at
every location — only $d'_i$ (attention) and $c_i$ (the optimiser) differ.
The paper names it only obliquely, bundled with A1, in §5.5:

> "First, the model assumes independent per-location SDT decisions; **real
> observers emit a single global response**, introducing dependencies that
> could alter the optimal policy. Our results therefore represent an upper
> bound on VDA benefit."

The claim A6 underpins is §5.1:

> "Criterion adjustment is costless: shifting $c$ at one location has no
> effect on $d'$ at any location. **It can therefore independently encode
> value at each location** without any perceptual tradeoff. Attention
> reallocation, by contrast, is a zero-sum game …"

— i.e. that there are exactly **two** value-encoding mechanisms (a costless
per-location criterion and a zero-sum $d'$-reallocation), which the
criterion fraction $\mathrm{CF}=[R(\mathrm{P3})-R(\mathrm{P4})]/[R(\mathrm{P1})-R(\mathrm{P4})]$
(§4.1) cleanly partitions.

## Why this matters

If the homogeneous-machinery premise is load-bearing, the criterion fraction
(C1, already CONTESTED) is not merely a number with a contested range — its
*meaning* as "the share of value-encoding done by criterion vs attention" is
conditional. Downstream, §5.3's advice to computational modellers ("route
value through criterion") and §5.2's experimental-design predictions inherit
that conditionality. For the user's PRISM program the stakes are direct:
PRISM's population code with learned covariance and per-channel FiLM is the
model that *does* have the extra levers (noise/correlation modulation, and a
learned rather than stipulated decision rule) that A6 assumes away, so A6 is
the assumption that most sharply separates the Herman normative model from
what a trained PRISM agent can express.

## Version 0.1 — 2026-05-25

### What this version did

Attack vector: **re-derivation** (`Critique/derivations/A6--heterogeneous-decision-rule.md`)
with independent numerical corroboration
(`Critique/replications/A6--heterogeneous-decision-rule/`, numeric content
sha256 `d6741d48…`, deterministic). Folds in CR-055 (the run-017 Booking-2 =
A6 cross-link). I introduced a per-location decision-noise scale
$s_i = \sqrt{1+\sigma_{d,i}^2}\ge 1$ (the paper is $s_i\equiv1$), giving rates
$\mathrm{HR}_i=\Phi((d'_i/2-c_i)/s_i)$, $\mathrm{FAR}_i=\Phi((-d'_i/2-c_i)/s_i)$,
and re-derived the P1–P4 optimum. Two readings of A6 were tested.

**Prop 1 (A6-(i), fixed heterogeneous machinery — the literal mission-§2.7
reading): BENIGN, proved.** The rate map obeys the exact identity
$\Phi((d'_i/2-c_i)/s_i)=\Phi(\tilde d'_i/2-\tilde c_i)$ with
$\tilde d'_i=d'_i/s_i$, $\tilde c_i=c_i/s_i$ (numerically $1.1\times10^{-16}$).
Since $c_i\mapsto\tilde c_i$ is a bijection and the optimiser searches all
criteria, the *entire* P1–P4 reward set equals the paper's at the rescaled
sensitivities $d'_i\to d'_i/s_i$, so $\mathrm{CF}(s_c,s_u)=\mathrm{CF}_{\text{paper}}|_{d'\to d'/s}$
**exactly**. Numerically (on a non-clipping criterion grid) CF computed with
explicit $(s_c,s_u)$ equals CF from the rescaled-$d'$ model to $\le1.7\times10^{-5}$,
the residual vanishing as $\Delta c\to0$. ⇒ fixed heterogeneous decision noise
is a per-location $d'$-perturbation (same class as $d'_{\max}/f_0$); the
*structure* of the decomposition is untouched. (It does move the CF *value*,
e.g. $0.728\to0.789$ for $s_u=2$ — verdict-relevant scope, not a break.)

**Prop 2 (attention-COUPLED noise — a third lever): cracks the metric's
interpretation, conditionally.** Prop 1 requires $s_i$ constant in $\alpha$.
Empirically it is not (`lu_dosher1998_external_noise`: internal-noise
suppression is one of the three canonical attention mechanisms;
`luo_maunsell2018_criterion_sensitivity`: attention modulates correlation and
Fano factor, not only rate; `cohen_maunsell2009_correlations`). With
$s_i=s(a_i),\,s'<0$, moving $\alpha$ changes effective sensitivity through two
channels — $\partial_\alpha(d'_c/s_c)=d'^{\,\prime}_c/s_c - d'_c s'_c/s_c^2$ —
so the $R(\mathrm{P1})-R(\mathrm{P3})$ increment the CF books to "attention"
now bundles spatial $d'$-reallocation **and** attention-modulated noise
reduction. With the illustrative coupling $s(a)=\sqrt{1+\kappa(1-h(a))}$, CF at
the headline cell **deflates** $0.728\to0.626$ ($\kappa{:}0\to1$, wide-grid
guard) while the total achievable gain *grows* $0.62\to0.78$ — attention does
more than the model credits. Direction matches the A1-$\rho$ result (CF fell
under FA correlation, V0.2 of `A1--independence.md`).

**A6-(ii) single global response (§5.5 / CR-055): analytic skeleton.** A
single global criterion $c_c=c_u=c$ removes the per-location DOF that §5.1
calls criterion's defining advantage; the constrained criterion gain cannot
exceed the free one ($G_{\text{crit}}^{\text{global-}c}\le G_{\text{crit}}^{\text{per-loc}}$,
strict when $v>1,V\ne1/N$), so CF compounds downward — the CR-055 prediction.
A fuller pooled-decision rule also dissolves the Eq. 9 $P_{\text{no-fa}}$
product, which is the A1 locus, so the §5.5 sentence's two clauses are
coupled (A1 = FA aggregation; A6-(ii) = criterion DOF). Quantifying this is
the designated second vector (CR-056).

### Verdict

**WEAKLY-SUPPORTED.** Per mission §6 one vector cannot elevate. The literal
A6 relaxation (fixed heterogeneous machinery) *failed to break* the
decomposition — a confirming result (Prop 1, proved exactly) — so the label
is not CONTESTED: **no headline number shifts within the paper's stated
model** ($s\equiv1$, per-location criteria). Both cracks (Prop 2; A6-(ii))
require a model *extension* beyond what the paper computes, so A6 is a
**scope/conditional** matter, mirroring A1's and A2's first touches (premise
shown vulnerable, not yet consequential). The referee-level statement: the
criterion fraction is a clean criterion-vs-attention partition **iff**
(a) attention acts only on $d'$ (no attention-modulated decision noise) and
(b) the criterion is per-location (no single global response) — two premises
the paper neither states nor (per §5.5's own hedge) believes. The designated
second vector that would settle CONFIRMED-CONDITIONAL vs CONTESTED is CR-056
(single-global-criterion replication across the C1 grid).

### Evidence

- Re-derivation: `Critique/derivations/A6--heterogeneous-decision-rule.md`
  (Prop 1 absorption theorem Eqs. 6–8; Prop 2 gradient Eqs. 9–10; A6-(ii)
  inequality 12).
- Replication: `Critique/replications/A6--heterogeneous-decision-rule/`
  (Block 0 validates CF=0.7282 vs C1's 0.728 and VDA peak 0.0797@0.398 vs
  C2's ≈0.0799@0.383, Prop-1 identity 1.1e-16; Block 1 Prop-1 CF agreement
  ≤1.7e-5 on wide grid; Block 2 CF deflation 0.728→0.626 + wide-grid guard).
- Literature (via §11 sweep, below): `lu_dosher1998_external_noise` and
  `luo_maunsell2018_criterion_sensitivity` establish that attention's
  mechanism inventory exceeds the model's single $d'$-gain (internal-noise
  suppression; dissociable criterion/sensitivity substrates), grounding
  Prop 2's premise; `mcadams_maunsell1999_reliability` and
  `hawkins1990_attention_detectability` are the fair legs (the $d'$-gain is
  real and multiplicative; A6 is the field-standard idealisation of cued
  detection).

### Loose ends

- **CR-056** (A6 second vector, replication): constrain $c_c=c_u$ in the C1
  criterion-fraction optimiser, re-run the 4,410-cell grid, measure the CF
  deflation predicted by ineq. (12). Decides CONFIRMED-CONDITIONAL vs
  CONTESTED.
- **CR-057** (A6 literature): is the decision-noise/criterion lever both
  attention- *and* value-modulated? `luo_maunsell2018` localises criterion to
  LPFC; Cohen–Maunsell decorrelation is the empirical $s(\alpha)$; overlaps
  CR-053 (A1 value×correlation gap). If the noise channel is value-directed,
  the omitted lever bears on C1/C3 completeness the same way the A1
  decorrelation channel does.
- **Coupling form for Prop 2** is illustrative (κ-parametrised); a
  literature-calibrated $s(\alpha)$ would pin the deflation magnitude.
- **A6-(ii) ∩ A1**: a pooled-statistic decision rule couples the criterion
  DOF (A6) and the FA-product (A1, CONTESTED); both push CF down — a joint
  re-derivation would quantify the combined effect.

### Implications for PRISM (mission §3.5)

A6 is the assumption PRISM most cleanly *relaxes*. The Herman model has one
decision-noise level (σ=1) and a per-location criterion; PRISM v1/v2 learn a
population code with full covariance and per-channel FiLM, plus a recurrent
read-out that is not a stipulated SDT rule. So a trained PRISM agent can in
principle express *all three* Lu–Dosher mechanisms (signal enhancement,
distractor exclusion, internal-noise suppression) and an attention-modulated
$s(\alpha)$ — exactly the channels Prop 2 shows the criterion fraction
mis-books. The `luo_maunsell2018` §7 architectural reading already in the
wiki (sensitivity ≙ Feedback-Transformer V1 gain; criterion ≙ central
self-attention / PRISM-v2 slow memory) predicts the two SDT components live
in *distinct* PRISM modules. **Falsifiable conjunction:** decompose a trained
PRISM agent's cued-attention benefit by the Lu–Dosher external-noise method
(`Prism/analysis/` + an added external-noise probe) and by SDT (criterion vs
sensitivity); the Herman two-tool decomposition predicts the benefit is
exhausted by criterion + $d'$-reallocation, whereas if PRISM also shows an
internal-noise-suppression component (low-external-noise-only benefit that
SDT cannot assign to either tool), that is the third lever — the same
structural blind spot flagged for A1 (decorrelation) and here (decision
noise), now testable behaviourally.

### Wiki cross-references

Mechanism-keyword sweep (mission §11.1 anchors + A6-specific: *decision
noise, late/readout/internal noise, decision variable, criterion shift,
signal detection theory, d-prime, optimal observer, pooling, global decision
rule, sensitivity vs criterion, Fano factor, noise correlation*). Searched
`papers/`, `concepts/`, `threads/`.

- `luo_maunsell2018_criterion_sensitivity` — **cited** (Prop 2, Evidence,
  PRISM): attention has dissociable criterion + sensitivity substrates and
  modulates correlation/Fano factor, not only rate ⇒ "attention acts only on
  $d'$" is false; the model's two-tool inventory is incomplete.
- `lu_dosher1998_external_noise` — **cited** (Prop 2, Evidence, PRISM): the
  canonical three-mechanism taxonomy (signal enhancement / distractor
  exclusion / internal-noise suppression); internal-noise suppression is the
  $s(\alpha)$ channel the model omits; supplies the falsifiable PRISM probe.
- `mcadams_maunsell1999_reliability` — **cited** (Evidence, fair leg): the
  $d'$-gain is real, multiplicative, Fano-flat — A6-(i) being benign is
  consistent with a genuine sensitivity tool.
- `hawkins1990_attention_detectability` — **cited** (Evidence, fair leg): the
  field-standard SDT idealisation of cued detection = the homogeneous A6
  machinery; A6 is a defensible default, not a blunder.
- `cohen_maunsell2009_correlations` — **cited** (Prop 2): attention reduces
  noise correlations = empirical evidence for $s'(\alpha)<0$; the A1 dossier's
  decorrelation channel is A6's noise channel seen at the population level.
- `muller_findlay1987_sensitivity_criterion`, `sridharan2017_sc_sensitivity_bias`,
  `solomon2004_cues_sensitivity` — **cited (supporting)**: the SDT
  criterion-vs-sensitivity dissociation tradition the criterion fraction sits
  in; confirm the two components are empirically separable (so a clean
  two-way decomposition is *coherent*, the fair side of the ledger).
- `ernst_banks2002_cue_combination` — **cited (A6-(ii))**: optimal-pooling
  theorem; the "single global response" reading is a pooling rule and breaks
  the simple independent-decision optimum (also the A1 link).
- `gold_shadlen2007_decision_making`, `ratcliff1978_drift_diffusion`,
  `hanks_summerfield2017_perceptual_decisions`, `roitman_shadlen2002_lip_rt` —
  **spawned CR-056 pointer / not read in depth**: accumulator/pooling models
  are the substrate for a full "single global response" (A6-(ii)) decision
  rule; deferred to CR-056.
- `reynolds_heeger2009_normalization` — **noted**: gain-modulation substrate
  of the $d'(\alpha)$ map; orthogonal to the decision-noise channel here.
- `coalition_resource_competition`, `competition_emergent_predictive_coding`
  (concepts) — **cited** (PRISM bridge): the competition substrate is where a
  learned $s(\alpha)$/decorrelation lever would live in PRISM.
- `multi_hub_multi_objective_system` (concept) — **cited** (PRISM bridge, via
  luo_maunsell §7): the criterion/sensitivity architectural split.
- §11.1 anchors *dopamine, RPE, basal ganglia, priority map, LIP, FEF, V4,
  oculomotor, saccade, Posner cueing, cue validity, surround suppression* —
  **unrelated on inspection** for this decision-architecture re-derivation
  (no value-source or spatial-priority mechanism is exercised by A6).
- **No new wiki stub** (all relevant papers present; the absorption theorem's
  math-methods — Sterbenz-style reparametrisation invariance, Slepian for the
  A6-(ii)∩A1 pooling — have no wiki substrate, the same recurring gap flagged
  for C5/A8/A1; not a paper-stub matter). ⇒ no `audit.py` run required.
