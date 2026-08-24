---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.2
run_id: run-017
started: 2026-05-25T02:38:14Z
ended: 2026-05-25T03:05:00Z
worked_on: A1
attack_vector: re-derivation
verdict_touched: A1--independence
verdict_after: CONTESTED
papers_read: [cohen_maunsell2009_correlations, ruff_cohen2016_cross_area_correlations, srinath2021_attention_information_flow, muller_findlay1987_sensitivity_criterion, luo_maunsell2018_criterion_sensitivity, hawkins1990_attention_detectability, ernst_banks2002_cue_combination, mcadams_maunsell1999_reliability]
papers_added: []
spawned_tasks: [CR-054, CR-055]
---

# A1 second vector: does per-location independence upper-bound the VDA benefit?

## What I attacked

Assumption **A1** (mission §2.7) — per-location SDT decisions are independent
(paper §2.1, Eqs. 1–2; operationalised as the Eq. 9 product
$P_{\text{no-fa}}=(1-\mathrm{FAR}_c)(1-\mathrm{FAR}_u)^{N-1}$). Specifically the
**§5.5 directional self-characterisation**: *"real observers emit a single
global response, introducing dependencies that could alter the optimal policy.
Our results therefore represent an upper bound on VDA benefit."* This was the
decisive loose end left by v0.1/run-016 (literature): the *sign* of the
"upper bound" claim, which literature could not settle. A1 entered this run at
**WEAKLY-SUPPORTED**.

## How I attacked it

**Re-derivation** (CR-052, the designated second vector), with independent
numerical corroboration. I replaced the Eq. 9 independent FA product with the
**exact** equicorrelated-Gaussian joint correct-rejection probability at
correlation $\rho$, using the one-factor (shared-latent-$Z$) reduction
$P_{\text{no-fa}}(\rho)=\int\Phi(\tfrac{b_c-\sqrt\rho z}{\sqrt{1-\rho}})
\Phi(\tfrac{b_u-\sqrt\rho z}{\sqrt{1-\rho}})^{N-1}\varphi(z)\,dz$ ($b_i=c_i+d'_i/2$;
1-D Gauss–Hermite quadrature, no MVN-CDF). I then **re-optimised** the
per-location criteria and $\alpha$ under $P_{\text{no-fa}}(\rho)$ and recomputed
the VDA$(r)$ curve and the criterion fraction at the C2 headline cell
($V=0.5,v=5,N=4,d'_{\max}=2,f_0=0.5,\sqrt{\cdot}$), both variants, for
$\rho\in\{0,0.1,0.2,0.3,0.4\}$ bracketing Cohen & Maunsell's $r_{SC}\approx0.2$.
Derivation: `Critique/derivations/A1--correlated-fa-upper-bound.md`; code +
data: `Critique/replications/A1--correlated-fa/`.

A pivotal sub-result fixed *where* correlation may enter: in Eq. 9 the
change-trial term is linear in the marginal hit rates (the change is at one
location, no cross-location product), so independence enters in **exactly one
place** — the $P_{\text{no-fa}}$ product. Hence replacing that product is the
faithful, complete relaxation of A1 (**Booking 1**); the pooled-$d'$ reading
(**Booking 2**) has no locus in Eq. 9 and is actually assumption **A6** (single
global response). The §5.5 sentence conflates A1 and A6.

## What I found

The "upper bound on VDA benefit" claim **fails as a uniform statement**, and the
failure is regime-structured:

- $d\mathrm{VDA}/d\rho$ **flips sign at $r\approx0.5$**. Correlation *suppresses*
  VDA in the cost-dominant regime ($r\lesssim0.5$, which contains the headline
  peak) but **amplifies** it throughout the benefit-dominant regime
  ($r\gtrsim0.5$) — by up to $+0.0101$ ($\sim+20\%$ of local VDA) at
  $r\approx0.83,\rho=0.4$, the excess over the $\rho=0$ curve growing
  monotonically with $\rho$ ($+0.0048\to+0.0101$ for $\rho=0.1\to0.4$). Even the
  headline **peak** rises at $\rho=0.1$ ($0.0811>0.0799$). A single upper-bound
  statement requires $d\mathrm{VDA}/d\rho\le0$ everywhere; it doesn't hold.
- **What independence does upper-bound is the criterion fraction.** CF falls
  monotonically with $\rho$ (variant A): $r=0.398$ $0.830\to0.788$; $r=1$
  $0.728\to0.647$; $r=3.16$ $0.641\to0.539$ (toward the $0.5$ boundary). So
  $\mathrm{CF}(0)\ge\mathrm{CF}(\rho)$ — the exact inverse of the paper's framing.
- **The headline magnitude survives.** At the empirically central $\rho\approx0.2$
  the VDA peak is $0.0796$ vs $0.0799$ ($-0.4\%$): C2's $\sim0.08$ is robust.
- **Mechanism.** Two channels: (a) correlation devalues the criterion lever
  (relaxed FA penalty) → CF falls; (b) correlation makes attentional
  concentration cheaper (the $N{-}1$ degraded uncued FARs hurt less under $\rho>0$)
  → VDA rises where attention is the active lever (benefit-dominant). The paper's
  §5.5 implicitly assumes (b) is absent — an undeived step; the only true
  monotonicity (each policy reward rises with $\rho$, Cor. 3.2) is about levels,
  not the VDA difference.

Validation: $\rho=0$ reproduces the independent C2 peak ($0.0799@r{=}0.383$, in
the CR-001/036/040 band); GH-64≈GH-128 to $8\times10^{-16}$; Slepian monotonicity
confirmed (independent corner is the FA-penalty-maximising minimum). Deterministic
(numeric digest `b9828f02…`, byte-identical on re-run). 0 web fetches; no new wiki
stub.

## Verdict movement

**A1: WEAKLY-SUPPORTED → CONTESTED.** A second, distinct attack vector
(re-derivation) *succeeded*: the §5.5 directional claim is too strong as written
(false as a uniform upper bound; correlation amplifies VDA $\sim20\%$ in the
benefit-dominant tail, and independence upper-bounds the criterion fraction
instead). Not REFUTED — the headline C2 magnitude is robust and the cited CF
values stay $>0.5$; A1 remains the field-standard behavioural idealisation. Not
CONFIRMED-CONDITIONAL — the attack shifted the interpretation of a quantity the
paper actively uses (§5.5→§5.2 design advice inherits the error), which the
CR-052 decision rule designates as failure. A weaker reformulation is proposed in
the verdict.

## Next-attack recommendation

**CR-053** (literature, the standing A1 completeness follow-up — promoted to the
recommended next pick): is the noise-correlation-reduction channel *value*-directed
(reward-magnitude-modulated) or only attention/validity-modulated? This run
confirmed it is a genuine wiki gap (the value×noise-correlation grep surfaced only
`babayan_uchida_gershman2018` and `hickey2010`, neither on-point), and the
benefit-dominant amplification makes it consequential: if decorrelation scales
with value, the two-tool model omits a real value-directed lever bearing on
C1/C3. Likely needs one web fetch (Mitchell/Sundberg/Reynolds 2009 V4
noise-correlation, or a Cohen-lab value×correlation study). Alternatives:
**CR-011** (A6, which Booking 2 showed is the home of the "single global response"
clause — should reuse this run's $P_{\text{no-fa}}(\rho)$ machinery), then the
A4/A5/A7 OPEN remainder.

## Wiki cross-references

- [[cohen_maunsell2009_correlations]] — cited; sets the empirical $\rho$ range
  ($r_{SC}\approx0.2$) that makes the test load-bearing.
- [[ruff_cohen2016_cross_area_correlations]] — cited; sign-structured $\Sigma$ →
  spawned CR-054 (does structure move the amplification magnitude?).
- [[srinath2021_attention_information_flow]] — cited; supra-pairwise variance caps
  any single-$\rho$ patch.
- [[muller_findlay1987_sensitivity_criterion]] — cited; grounds the CF
  decomposition the inversion is stated in.
- [[luo_maunsell2018_criterion_sensitivity]] — cited; criterion/sensitivity
  dissociable substrates (the CF-share language).
- [[hawkins1990_attention_detectability]] — cited; per-location SDT is the
  behavioural standard (anchors CONTESTED-not-REFUTED).
- [[ernst_banks2002_cue_combination]] — cited; optimal pooling under correlated
  noise ties Booking 2 to A6.
- [[mcadams_maunsell1999_reliability]] — cited; the marginal-$d'$ tool is real
  (the conflation the booking analysis resolves).
- [[babayan_uchida_gershman2018_belief_states_dopamine]], [[hickey2010_reward_salience_acc]]
  — surfaced by the value×correlation grep; neither on reward-modulation of noise
  correlations → confirms the CR-053 gap (documented, not cited).
- [[ratcliff1978_drift_diffusion]], [[hanks_summerfield2017_perceptual_decisions]]
  — surfaced (decision-aggregation models); deferred to A6/CR-011, not A1.
- `concepts/coalition_resource_competition.md`,
  `concepts/competition_emergent_predictive_coding.md` — cited (PRISM bridge).
- §11.1 anchors unrelated on inspection: dopamine / RPE / basal ganglia / FEF /
  saccade / oculomotor / priority-map ([[bisley_goldberg2010_parietal_priority]],
  [[rust_cohen2022_priority_coding]], [[bolton2015_dopamine_sc]]) — value *source*,
  not cross-location decision correlation. [[herman_krauzlis2017_sc_change_detection]]
  surfaced (Herman-lab) but not read — flagged for a future run.
