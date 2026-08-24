---
type: verdict
claim_id: A1
claim_statement: "Per-location SDT decisions are independent (paper §2.1, Eqs. 1–2); Eq. (9) factorises the joint no-false-alarm probability as a product, and §5.5 claims the resulting numbers are an upper bound on VDA benefit."
paper_section: "§2.1 (Eqs. 1–2), §2.5 (Eq. 9), §5.5 (limitation)"
current_label: CONTESTED
attacks_tried:
  - vector: literature
    run_id: run-016
    outcome: "premise empirically false at the population level (substantial cross-location noise correlations, in the paper's own paradigm); independence load-bearing for C1 via the Eq. 9 product; two-tool taxonomy omits the empirically dominant decorrelation channel; §5.5 'upper bound on VDA' shown underived and sign-ambiguous. No headline number shifted → no elevation/contest on one vector."
  - vector: re-derivation
    run_id: run-017
    outcome: "ATTACK SUCCEEDED. Re-derived P_no-fa under an exact equicorrelated-Gaussian decision model (Booking 1, the faithful A1 relaxation; Booking 2 = A6) and re-optimised criteria + α. The §5.5 'upper bound on VDA' claim FAILS as a uniform statement: dVDA/dρ flips sign at r≈0.5 — correlation suppresses VDA in the cost-dominant regime (incl. the headline peak) but AMPLIFIES it ~20% in the benefit-dominant tail (r≳0.5), excess growing with ρ; even the headline peak rises at ρ=0.1. Independence instead upper-bounds the CRITERION FRACTION (CF(0)≥CF(ρ), monotone). Headline C2 peak magnitude robust (within 0.4% at ρ=0.2). → CONTESTED with weaker reformulation."
load_bearing_for: ["§2.5 Eq. 9 (P_no-fa)", "§4.1 / C1 criterion fraction", "§5.1 'criterion captures 60–96%'", "§5.5 'upper bound on VDA' self-characterisation", "§5.2 design advice (inherits the directional error)", "§5.3 implications for computational models"]
last_updated: 2026-05-25
prompt_version_observed: 0.2
---

# Verdict: A1 — per-location SDT decisions are independent

## Claim as written in the paper

§2.1: *"On each trial, a change occurs with probability 0.5 ('change trial')
or does not ('no-change trial'). The observer makes **independent** detection
decisions at each location using signal detection theory (SDT):"* followed by
$\mathrm{HR}(d',c)=\Phi(d'/2-c)$, $\mathrm{FAR}(d',c)=\Phi(-d'/2-c)$
(Eqs. 1–2). Operationalised in §2.5, Eq. (9):
$P_{\text{no-fa}} = (1-\mathrm{FAR}_c)(1-\mathrm{FAR}_u)^{N-1}$ — the joint
no-false-alarm probability as a **product** of per-location marginals.
Named in §5.5: *"the model assumes independent per-location SDT decisions;
real observers emit a single global response, introducing dependencies that
could alter the optimal policy. Our results therefore represent an **upper
bound on VDA benefit**."*

## Why this matters

The independence assumption is the precise content of the Eq. (9) product, so
it is load-bearing for the correct-rejection reward term, the criterion-gain
$R(\mathrm{P3})-R(\mathrm{P4})$, and therefore the **criterion fraction
(C1)** — the paper's flagship "criterion captures 60–96%" claim. It also
fixes the *vocabulary* of the whole paper: the model has exactly two tools
(criterion shift; $d'$-reallocation). If real observers exploit a third lever
that independence assumes away — cross-location/interneuronal **correlation
reduction**, empirically the dominant carrier of attention's behavioural
benefit — then the two-tool decomposition is incomplete as a description of
cortex even where it is internally correct. Finally the paper leans on
independence for a *directional* claim ("upper bound on VDA"): if that sign is
wrong, §5.2's experimental-design advice ("VDA should be negligible outside
the narrow regime") inherits the error.

**For the user's PRISM program:** A1 is the assumption PRISM most directly
violates. PRISM v1/v2 carry a *population* code with a full (learned)
covariance structure and per-location/per-channel FiLM gain; the Herman model
cannot represent the very mechanism (value- or attention-directed
decorrelation) that the user's own evaluation protocol — Cohen–Maunsell §7,
measure $r_{SC}$ in the trained model and run the shuffle decomposition — is
built to detect. So A1 marks the boundary where the normative model and the
user's empirical program stop sharing a state space.

## Version 0.1 — 2026-05-24 (run-016)

### What this version did

**Attack vector: literature** (CR-006). Read 6 full-depth wiki entries
spanning three axes — correlation structure
([[cohen_maunsell2009_correlations]], [[ruff_cohen2016_cross_area_correlations]],
[[srinath2021_attention_information_flow]]), single-unit vs. population coding
([[mcadams_maunsell1999_reliability]]), and the per-location-SDT behavioural
convention ([[hawkins1990_attention_detectability]], with optimal-pooling
theory from [[ernst_banks2002_cue_combination]]). Mechanism context from
[[luo_maunsell2018_criterion_sensitivity]] and
[[reynolds_heeger2009_normalization]]. Full dossier:
`Critique/evidence/A1--independence.md`. 0 web fetches; no new wiki stub
(every relevant paper already present).

Pinned the two load-bearing readings (mirroring the A2 R1/R2 split):
**I-dec** (the Eq. 9 product needs decision-level FA independence) and
**I-neur** (per-location $d'$ as a marginal, vs. cortex's
$d'^2\propto(\Delta\mu)^\top\Sigma^{-1}(\Delta\mu)$). Gave the closed-form
load-bearing statement: under an equicorrelated-Gaussian no-change-trial
model with correlation $\rho$, $P_{\text{no-fa}}=\Phi_N(\mathbf c;R_\rho)$ and
by **Slepian's inequality** $\Phi_N(\mathbf c;R_\rho)\ge\prod_i(1-\mathrm{FAR}_i)$
for $\rho>0$, monotone in $\rho$ — so the independent product is the
**FA-penalty-maximising corner**, and positive correlations relax the
multiple-comparisons pressure that shapes the optimal criteria (and hence
C1's criterion-gain term).

### Verdict

**(none) → WEAKLY-SUPPORTED.**

Reasoning. The literature establishes three things and leaves one decisive
thing open:

1. **The premise is empirically false at the population level (I-neur).** In
   the paper's own paradigm class (macaque orientation change-detection with
   a peripheral validity cue), cross-location noise correlations are
   substantial ($r_{SC}\approx0.2$) and, through decorrelation, carry **>80%**
   of attention's behavioural benefit; rate gain alone recovers <20%
   ([[cohen_maunsell2009_correlations]]). The structure is sign-dependent on
   anatomical scope ([[ruff_cohen2016_cross_area_correlations]]: within-down,
   between-up) and has a supra-pairwise component
   ([[srinath2021_attention_information_flow]]: ~2/3 shared-variance
   amplification). Independence is not a small idealisation here — the object
   it discards is the dominant lever.

2. **Independence is load-bearing for C1.** It *is* the Eq. (9) product;
   Slepian shows the independent corner maximises the aggregate FA penalty,
   so the criterion fraction is computed at a boundary, not a typical, point
   in correlation space.

3. **The two-tool taxonomy is incomplete.** Correlation reduction is neither
   "criterion shift" nor "$d'$-reallocation"; the model's scalar $d'(\alpha)$
   conflates marginal gain ([[mcadams_maunsell1999_reliability]]: real,
   multiplicative, Fano-flat) with decorrelation. So "criterion captures
   60–96% of the reward gain" is a statement about the *model's* reward
   decomposition, **not** a claim about cortex's mechanism inventory.

Why **not** CONTESTED: no attack in this version *shifted a headline number*.
A1 is also the **field-standard behavioural idealisation** of cued detection
([[hawkins1990_attention_detectability]] and the SDT-of-attention tradition),
and the model's $d'$ tool is genuinely real — so the assumption is a named,
pre-empted idealisation, not a fiction. Mission §6 forbids elevation or
refutation on a single vector.

Why **not** elevated: only one attack vector (literature). The **decisive
open question is the sign of the §5.5 "upper bound on VDA" claim**, which the
literature cannot settle:

- *Neural-decorrelation reading* — if decorrelation is **value-directed**
  (more decorrelation at high-value locations), it is an additional
  value-directed sensitivity channel outside the model; real VDA could
  **exceed** the model's → "upper bound" **wrong**.
- *Decision-aggregation reading* — a single global criterion has fewer
  degrees of freedom to exploit value cheaply (could **raise** VDA reliance,
  against the claim), but positive $\rho$ relaxing the FA penalty could make
  criterion **more** effective (less room for VDA, **supporting** the claim).

The sign is genuinely undetermined by literature and requires a re-derivation
(equicorrelated-Gaussian FA model with criteria re-optimised) — the
designated second vector (CR-052).

### Evidence

- `Critique/evidence/A1--independence.md` V0.1 — full dossier with per-source
  direction/weight classification.
- Load-bearing primary: [[cohen_maunsell2009_correlations]] (contradicts
  I-neur; constrains completeness; strong). Supporting:
  [[ruff_cohen2016_cross_area_correlations]],
  [[srinath2021_attention_information_flow]] (constrain).
  Fair/limiting: [[mcadams_maunsell1999_reliability]] ($d'$ tool real but
  incomplete), [[hawkins1990_attention_detectability]] (per-location SDT is
  the behavioural standard). Optimality theory:
  [[ernst_banks2002_cue_combination]] (correlated noise breaks independent
  pooling). Mechanism: [[luo_maunsell2018_criterion_sensitivity]],
  [[reynolds_heeger2009_normalization]].
- Closed-form: Slepian-inequality argument that the independent product is the
  FA-penalty-maximising corner (no wiki substrate — math-methods gap, flagged;
  mirrors the C5 floating-point and A8 majorization gaps).

### Loose ends

- **[decisive] Sign of "upper bound on VDA."** Re-derive $P_{\text{no-fa}}$
  under an equicorrelated-Gaussian (or Gaussian-copula) FA model with
  per-location criteria re-optimised; recompute the criterion fraction and
  VDA at the C2 headline cell ($V=0.5,v=5,N=4,f_0=0.5,\sqrt{\cdot}$) for a
  sweep of $\rho\in[0,0.4]$ bracketing the Cohen–Maunsell range. Does VDA rise
  or fall in $\rho$? → CR-052 (re-derivation, the A1 second vector → settles
  CONFIRMED-CONDITIONAL vs CONTESTED).
- **Is the decorrelation channel value-directed?** The completeness critique
  only adds a *value* channel if decorrelation is reward-modulated, not merely
  attention-modulated. No wiki entry addresses this directly (the value+
  correlation sweep surfaced only attention-correlation papers and unrelated
  reward papers). → CR-053 (literature follow-up; candidates
  [[stanisor2013_v1_value_attention]], and likely a fetched stub of
  Mitchell/Sundberg/Reynolds 2009 or Cohen & Maunsell 2011).
- **I-dec ↔ A6 cousin.** The §5.5 "single global response" reading is the
  heterogeneous/global decision-rule assumption A6 (CR-011) interrogates from
  the re-derivation side; the optimal-pooling consequence
  ([[ernst_banks2002_cue_combination]] §6) is shared. Recommend CR-011 be run
  aware of this dossier; do not duplicate.

### Wiki cross-references

- [[cohen_maunsell2009_correlations]] — cited (contradicts I-neur premise;
  constrains two-tool completeness); the spine of the attack.
- [[ruff_cohen2016_cross_area_correlations]] — cited (constrains; sign-
  dependent covariance structure attention manipulates).
- [[srinath2021_attention_information_flow]] — cited (constrains; supra-
  pairwise shared-variance amplification caps any "add a $\rho$ term" fix).
- [[mcadams_maunsell1999_reliability]] — cited (supports the reality of the
  $d'$ tool; self-flagged incompleteness vs. population coding).
- [[hawkins1990_attention_detectability]] — cited (supports the per-location-
  SDT behavioural convention; anchors WEAKLY-SUPPORTED-not-CONTESTED).
- [[ernst_banks2002_cue_combination]] — cited (constrains; correlated noise
  breaks independent-pooling optimality, ties to the §5.5 global-response
  concern and to A6).
- [[luo_maunsell2018_criterion_sensitivity]] — cited (constrains; benefit/cost
  and criterion/sensitivity have dissociable substrates).
- [[reynolds_heeger2009_normalization]] — cited (constrains; normalization
  changes rate *and* correlation structure → the omitted channel is the
  off-diagonal half of a mechanism the model already half-represents).
- `concepts/coalition_resource_competition.md` — cited (PRISM bridge:
  competition-emergent decorrelation is the population-level signature PRISM
  can carry but the Herman model cannot).
- `concepts/competition_emergent_predictive_coding.md` — cited (PRISM bridge;
  the user's thesis-level account of where decorrelation comes from).
- §11.1 anchors *unrelated on inspection* for A1: dopamine / RPE / basal
  ganglia / saccade / oculomotor / priority-map entries
  ([[bisley_goldberg2010_parietal_priority]], [[glimcher2011_dopamine_rpe]],
  etc.) bear on the *source* of value, not on cross-location decision
  independence; [[rust_cohen2022_priority_coding]] surfaced in the sweep but
  was not read this run (priority-coding geometry, tangential to the
  independence question) — left for a future run if CR-052 needs it.

## Version 0.2 — 2026-05-25 (run-017)

### What this version did

**Attack vector: re-derivation** (CR-052, the designated A1 second vector),
with independent numerical corroboration. Full derivation:
`Critique/derivations/A1--correlated-fa-upper-bound.md`; replication:
`Critique/replications/A1--correlated-fa/` (numeric digest `b9828f02…`,
byte-identical on re-run). 0 web fetches; no new wiki stub → no audit.py.

The decisive loose end from v0.1 was the **sign** of the §5.5 "upper bound on
VDA benefit" self-characterisation, which literature could not settle. I
settled it by re-deriving the no-change-trial false-alarm aggregation under an
**exact equicorrelated-Gaussian decision model** (correlation $\rho$), via the
one-factor (shared-latent-$Z$) reduction
$P_{\text{no-fa}}(\rho)=\int\Phi(\tfrac{b_c-\sqrt\rho z}{\sqrt{1-\rho}})
\Phi(\tfrac{b_u-\sqrt\rho z}{\sqrt{1-\rho}})^{N-1}\varphi(z)\,dz$ (1-D
quadrature, no MVN-CDF), then **re-optimised** the per-location criteria and
$\alpha$ and recomputed the VDA$(r)$ curve and the criterion fraction at the C2
headline cell ($V=0.5,v=5,N=4,d'_{\max}=2,f_0=0.5,\sqrt{\cdot}$), both variants,
for $\rho\in\{0,0.1,0.2,0.3,0.4\}$ bracketing Cohen & Maunsell's $r_{SC}\approx0.2$.

**Pivotal move — the "booking" is forced by the reward.** In Eq. (9) the
change-trial term is *linear* in the marginal hit rates (the change is at one
location, no cross-location product), so independence (A1) enters in **exactly
one place**: the $P_{\text{no-fa}}$ product. Replacing that product with the
correlated orthant probability is therefore the **faithful and complete**
relaxation of A1 (*Booking 1*). The "pooled-$d'$" reading (*Booking 2*) has no
locus in Eq. (9) — it needs a global detection statistic, which is **A6** (single
global response), not A1. This cleanly disentangles the two clauses §5.5
bundles.

Validation: $\rho=0$ reproduces the independent model's C2 peak (VDA $=0.0799$ at
$r=0.383$, inside the CR-001/CR-036/CR-040 band); GH-64≈GH-128 to $8\times10^{-16}$;
**Slepian monotonicity** verified ($P_{\text{no-fa}}(\rho)\uparrow$, independent
corner is the minimum — the run-016 closed-form claim confirmed).

### Verdict

**WEAKLY-SUPPORTED → CONTESTED.**

Cause of the movement: a *second, distinct* attack vector (re-derivation)
**succeeded** — the §5.5 directional self-characterisation is too strong as
written. Three findings drive it:

1. **The "upper bound on VDA" fails as a uniform statement.** $d\mathrm{VDA}/d\rho$
   **flips sign at $r\approx0.5$**: correlation *suppresses* VDA in the
   cost-dominant regime ($r\lesssim0.5$, which contains the headline peak) but
   **amplifies** it throughout the benefit-dominant regime ($r\gtrsim0.5$) by up
   to $+0.0101$ ($\sim+20\%$ of local VDA) at $r\approx0.83,\rho=0.4$, the excess
   growing monotonically with $\rho$ ($+0.0048\to+0.0101$ for $\rho=0.1\to0.4$).
   A single upper-bound statement would require $d\mathrm{VDA}/d\rho\le0$
   everywhere; the sign flips. Even the headline **peak** rises at $\rho=0.1$
   ($0.0811>0.0799$).

2. **What independence actually upper-bounds is the criterion fraction.** CF
   falls monotonically with $\rho$ (variant A): $r=0.398$: $0.830\to0.788$;
   $r=1$: $0.728\to0.647$; $r=3.16$: $0.641\to0.539$. So $\mathrm{CF}(0)\ge\mathrm{CF}(\rho)$
   — independence *over-states* criterion's share of value encoding (the exact
   inverse of the paper's framing), and the high-$r$ CF approaches the $0.5$
   dominance boundary, deepening the same benefit-dominant corner where C1 is
   already CONTESTED (run-003) and A3's $\beta\gamma=1$ pushed CF down (run-011).

3. **The derivation gap.** §5.5 asserts the upper bound with no derivation. The
   only true monotonicity (each policy reward rises with $\rho$, Cor. 3.2) is
   about *levels*; the VDA *difference* is not sign-determined, and the
   concentration-cost-relaxation channel makes it rise where attention is the
   active lever. The claim does not follow from the paper's own model.

Why **CONTESTED**, not REFUTED: the headline magnitudes survive — the C2 peak
($\sim0.08$ at $r\approx0.38$) is robust to the empirically central $\rho\approx0.2$
(within $0.4\%$), and the cited CF values stay $>0.5$. A1 also remains the
field-standard behavioural idealisation (v0.1; [[hawkins1990_attention_detectability]]).
Why **not** CONFIRMED-CONDITIONAL: the attack *shifted the interpretation of a
quantity the paper actively uses* — the §5.5→§5.2 directional chain — which the
CR-052 decision rule designates as failure. **Proposed reformulation** (drop the
unconditional "upper bound on VDA"): *positive decision correlations leave the
VDA peak essentially unchanged at empirically central $\rho$, but the independent
model is not a uniform upper bound — VDA is amplified $\sim20\%$ in the
benefit-dominant regime; independence upper-bounds the criterion fraction
instead.* §5.2's "VDA negligible outside the narrow regime" inherits the
benefit-dominant-tail error.

### Evidence

- `Critique/derivations/A1--correlated-fa-upper-bound.md` — full re-derivation
  (§1 booking, §2 exact reduction, §3 Slepian, §4 two channels, §5 numbers,
  §6 verdict). The Slepian step has no wiki substrate (math-methods gap; mirrors
  C5 floating-point, A8 majorization, run-016 MVN-orthant flags).
- `Critique/replications/A1--correlated-fa/output/results.json` — VDA$(r,\rho)$
  curves (both variants), CF$(\rho)$ table, validation + Slepian blocks.
- Empirical $\rho$ range: [[cohen_maunsell2009_correlations]] ($r_{SC}\approx0.2$);
  structure caveats [[ruff_cohen2016_cross_area_correlations]],
  [[srinath2021_attention_information_flow]]. CF decomposition grounding:
  [[muller_findlay1987_sensitivity_criterion]], [[luo_maunsell2018_criterion_sensitivity]].

### Loose ends

- **[spawned earlier, now sharper] Is the decorrelation channel value-directed?**
  The benefit-dominant amplification means correlation *adds* to VDA where
  attention is active; if decorrelation also scales with reward *magnitude* it is
  a genuine value-directed sensitivity lever the two-tool model omits. Confirmed
  **genuine wiki gap** this run (the value×noise-correlation grep surfaced only
  [[babayan_uchida_gershman2018_belief_states_dopamine]] and
  [[hickey2010_reward_salience_acc]], neither on reward-modulation of noise
  correlations). → **CR-053** (literature, likely a web fetch for
  Mitchell/Sundberg/Reynolds 2009 or a Cohen-lab value×correlation study).
- **[new] Structured $\Sigma$.** Equicorrelation refutes a *uniform* bound (one
  counterexample suffices), but the within-down/between-up sign structure
  ([[ruff_cohen2016_cross_area_correlations]]) and supra-pairwise component
  ([[srinath2021_attention_information_flow]]) could move the *magnitude* of the
  benefit-dominant amplification. → spawn CR-054 (sensitivity: block /
  signed-$\rho$ structure on the VDA tail), low.
- **[new] Booking 2 = A6.** The pooled-$d'$ reading is A6 (global response). The
  CF-inversion here predicts A6 will compound: a single global criterion has
  fewer DOF to exploit value cheaply. → CR-011 should reuse this derivation's
  $P_{\text{no-fa}}(\rho)$ machinery and the booking split; spawn CR-055 (note +
  cross-link), low.
- **[cross-claim] C1/§5.1.** The CF-falls-with-$\rho$ result means the paper's
  "$60$–$96\%$" criterion fraction is computed at the criterion-maximising
  corner; under realistic $\rho$ it is lower. This is a C1 sharpening, not a new
  C1 attack — note in C1's ledger on its next touch.

### Wiki cross-references (§11 sweep, run-017)

- [[cohen_maunsell2009_correlations]] — cited (sets the empirical $\rho$ range
  $r_{SC}\approx0.2$; the spine of the attack's relevance).
- [[ruff_cohen2016_cross_area_correlations]] — cited (sign-structured $\Sigma$;
  spawned CR-054 for the magnitude question).
- [[srinath2021_attention_information_flow]] — cited (supra-pairwise component
  caps an equicorrelation patch).
- [[muller_findlay1987_sensitivity_criterion]] — cited (grounds the CF
  decomposition the inversion is stated in).
- [[luo_maunsell2018_criterion_sensitivity]] — cited (criterion/sensitivity
  dissociable substrates; the CF-share language).
- [[hawkins1990_attention_detectability]] — cited (anchors CONTESTED-not-REFUTED:
  per-location SDT is the behavioural standard).
- [[ernst_banks2002_cue_combination]] — cited (optimal-pooling under correlated
  noise; ties Booking 2 to A6).
- [[mcadams_maunsell1999_reliability]] — cited (the marginal-$d'$ tool is real;
  the conflation the booking analysis resolves).
- [[babayan_uchida_gershman2018_belief_states_dopamine]],
  [[hickey2010_reward_salience_acc]] — surfaced by the value×correlation grep;
  **neither addresses reward-modulation of noise correlations** → confirms the
  CR-053 gap (documented, not cited as support).
- [[ratcliff1978_drift_diffusion]], [[hanks_summerfield2017_perceptual_decisions]]
  — surfaced (decision-aggregation models); **deferred to A6/CR-011** (the global
  decision-rule question), unrelated to A1's per-trial FA aggregation here.
- `concepts/coalition_resource_competition.md`,
  `concepts/competition_emergent_predictive_coding.md` — cited (PRISM bridge,
  below).
- §11.1 anchors *unrelated on inspection* for this run: dopamine / RPE / basal
  ganglia / FEF / saccade / oculomotor / priority-map
  ([[bisley_goldberg2010_parietal_priority]], [[rust_cohen2022_priority_coding]],
  [[bolton2015_dopamine_sc]]) — bear on the *source* of value, not on
  cross-location decision correlation. [[herman_krauzlis2017_sc_change_detection]]
  surfaced (Herman-lab SC change-detection) but not read this run — flagged for a
  future run as possible same-group methodological context.

### Implications for PRISM v1/v2 (v0.2 update)

The v0.1 PRISM block predicted PRISM would carry a value-directed decorrelation
"third slice" the Herman model is blind to. This run sharpens it directionally:
because correlation **amplifies** VDA in the benefit-dominant regime (rather than
only relaxing the FA penalty), a PRISM agent whose learned $\Sigma$ decorrelates
at high-value/cued locations should show *more* value-directed attention
re-allocation than the Herman normative bound predicts, **specifically when its
effective $r$ is benefit-dominant** ($\beta>\gamma$, i.e. the FiLM gain favours
enhancement over suppression). So the falsifiable PRISM prediction is a
*conjunction*: measure (i) the Cohen–Maunsell $r_{SC}$ reduction at cued slots
and (ii) the effective $\beta/\gamma$ from the FiLM gains; the model predicts the
$r_{SC}$-reduction and the attention-reallocation magnitude should *co-vary* and
*exceed* the two-tool decomposition exactly where (ii) is benefit-dominant —
`Prism/analysis/avg_saliency_*.py` + an added $r_{SC}$ probe is the test.

## Implications for PRISM v1/v2

A1 is the sharpest divergence point between the normative model and the
user's program. The Herman model's two-tool state space (scalar per-location
criterion + scalar per-location $d'$) **cannot represent** value- or
attention-directed correlation reduction — the mechanism Cohen & Maunsell
(2009) show carries the majority of attention's behavioural benefit, and the
one PRISM is architecturally built to express (a population code with learned
off-diagonal covariance; per-location/per-channel FiLM; competition for a
shared attention map — `concepts/coalition_resource_competition.md`,
`concepts/competition_emergent_predictive_coding.md`). Concretely: FiLM gain
acts diagonally and cannot by itself change off-diagonal covariance
(Cohen–Maunsell §7), but the Feedback-Transformer competition can — so a
trained PRISM agent should show the Cohen–Maunsell signature ($r_{SC}$
reduction at cued/high-value locations; shuffle-decomposition recovering ≥50%
of the accuracy gain from the correlation channel) that the Herman model is
blind to. The verdict's PRISM-facing prediction: where the Herman model
attributes 60–96% of value-related reward to *criterion*, a PRISM analysis
that measures $r_{SC}$ should find a third slice — value-directed
decorrelation — that the normative decomposition cannot name. If CR-052 finds
VDA *rises* with $\rho$ (the "upper bound" claim fails), that is also the
regime where PRISM's correlation channel would matter most, sharpening the
case that PRISM's value encoding need not route through criterion the way the
Herman model predicts.
