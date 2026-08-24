# CR-002 — diagnostic notes

## The r = 0.3 reference-point gap

The paper's §4.1 text quotes:

> "In the cost-dominant regime (r = 0.3), the criterion fraction
> reaches 96%."

This sits inside the paper's *primary* reference regime (Figure 2):
N = 4, d'_max = 2.0, f_0 = 0.5, h = √, V ≈ 0.5, v = 5, variant A. My
replication at this regime gives CF = 0.8542 (r = 0.3162, V = 0.5125)
or 0.8613 (r = 0.30, V = 0.50 exactly) — at α-grid Δα = 0.001 and
c-grid Δc = 0.05 on [-3, +3]. Widening the c-grid to ±4, ±5, ±6 or
refining α to 0.001 changes CF by less than 0.001.

Decomposition at (r = 0.3162, V = 0.5125, v = 5, variant A) from my
code:
- R(P4) = 1.71928
- R(P3) = 2.18218  (criterion gain = 0.4629)
- R(P2) = 2.18218  (validity-attention gain = 0.0000 — P2 = P3
   because at r = 0.3, α*(v=1) = 1/N; this is the paper's §4.2 finding)
- R(P1) = 2.26102  (VDA = 0.0788)
- Total gain (R(P1) - R(P4)) = 0.5417
- CF = 0.4629 / 0.5417 = 0.854

The numerical VDA value (0.0788) matches the paper's stated peak of
"VDA = 0.080 at r ≈ 0.3" (Figure 4, §4.3) to two decimals. CR-001's
re-derivation also reproduced this peak to within sub-grid
resolution. So the *model* and the *criterion fraction definition*
are not in dispute — only the §4.1 quoted "96%" number.

A visual reading of the paper's Figure 2 at r = 0.3 supports my
0.85 number: the blue (criterion) bar tops out near ≈ 2.18 above
a floor near ≈ 1.74, while the red (VDA) sliver adds another ≈ 0.08.
That gives criterion fraction ≈ (2.18 − 1.74) / (2.26 − 1.74) =
0.44 / 0.52 ≈ 0.85. The figure's bars are consistent with my code;
the text's "96%" is not.

The paper's r = 1.0 and r = 3.2 reference numbers (73% and 64%) match
my code to within 0.002 of CF. So the model implementation is
correct; the issue is localised to the r = 0.3 text quote.

**Most likely explanation:** the "96%" in §4.1 is a transcription
error in the manuscript, where a number from a *different* metric
(perhaps criterion / (criterion + VDA), ignoring validity-attention,
which at r = 0.3 happens to be 0 so doesn't disambiguate; or
criterion / criterion+VDA at a smaller r in the sweep where VDA is
near 0) was substituted for the actual r = 0.3 CF. The figure's bars
are the authoritative depiction.

A less likely explanation: the paper's actual code uses a slightly
different convention for P4 (e.g., maximises CR over c_c, c_u rather
than fixing c = 0). Inspecting the paper's prose §2.5 closes that
door: "Floor (P4): α = 1/N, c = 0." So c = 0 is explicit.

I do not pursue this further in this run; if the §4.1 wording is
corrected by the authors, the verdict's "specific number disagreement"
sub-clause drops out, but the *structural* refutation (the 60% floor
fails across the swept space) stands independently.

## Why V = 1/N produces low CF

The argmin in Phase A is (r = 10, V = 0.25, v = 4, variant B) with
CF = 0.3040. At V = 1/N = 0.25 the cue's *prior validity* gradient is
zero: each location is equally likely to host the change. The only
asymmetry between "cued" and "uncued" is the *reward* label (cued hits
pay v, uncued hits pay 1).

The model's β/γ asymmetry creates an *attention-reallocation
incentive even at v = 1, V = 1/N*. At α = 1, d_c rises by β · (d'_max
· f(1) - d'_base) = β · 0.5 with weight 1/N (the change probability
at cued); d_u drops by γ · (d'_base - d'_max · f(0)) = γ · 0.5 with
total weight (N-1)/N (the change probability at any of the (N-1)
uncued locations). For r = 10:
  - β = 20/11 ≈ 1.818, weight 1/N = 0.25  → gain ≈ 1.818 · 0.5 · 0.25
    ≈ 0.227 (×∂HR/∂d')
  - γ = 2/11 ≈ 0.182, weight (N-1)/N = 0.75 → loss ≈ 0.182 · 0.5 ·
    0.75 ≈ 0.068 (×∂HR/∂d')

The gain (cued, β-scaled) exceeds the loss (uncued, γ-scaled) by a
factor of ≈ 3.3, even with v = 1 and V = 1/N. So α*(v=1) at r = 10,
V = 1/N is far from 1/N — my code records α_P2 ≈ 0.96 there. The
paper's policy decomposition then attributes the (P2 - P3) gap to
"validity-attention", but the actual mechanism is pure β/γ asymmetry
(the cue's *label* drives the reallocation, not its *informational
content*).

This is not a bug in my replication; it is a model property the
paper does not explicitly discuss. The "validity-attention" name for
R(P2) - R(P3) becomes misleading at V = 1/N: the gap is asymmetry-
attention, not validity-attention. The paper's policy decomposition
is *agnostic* to which feature of the asymmetry is producing the gap
— it just measures the gap. So the CF definition is unaffected,
but the *interpretation* of the "validity-attention" component at
V = 1/N is.

## Why variant B is more vulnerable than variant A

Variant A's correct-rejection reward CR = V·v + (1−V) is value-
coupled — when value is high, the no-change-trial floor (P4) reward
is also high (the unbiased c = 0 baseline collects much of the CR
reward without effort). This inflates P4 and shrinks the total gain
R(P1) - R(P4), keeping CF large.

Variant B's CR = 1 is value-decoupled — at v = 5 the cued hit pays 5
but the no-FA pays 1. The unbiased c = 0 baseline collects less, so
P4 is lower, the total gain R(P1) - R(P4) is larger, and the
*relative* share captured by criterion adjustment can shrink. The
mathematical consequence: variant B has a larger denominator for CF,
so CF tends to be smaller for the same numerator.

This is also a model property, not an artefact. The paper introduces
variant B in §2.4 as "a stronger marginal benefit for detection at
high-value locations, since the hit-CR difference at the cued
position scales with v." That same property makes the denominator of
CF larger and the CF itself smaller. The paper's §4.1 claim "CF ∈
[0.60, 0.96]" implicitly assumed this didn't matter — but it does.

## What "would push CF below 0.50" looks like

At the V = 1/N anchor:
- Pushing r > 10 takes CF down monotonically: 0.30 (r=10) → 0.28
  (r=20) → 0.27 (r=50) → 0.26 (r=2000). The asymptote near r = ∞
  is approximately CF_∞ ≈ 0.26 — the limit β → 2, γ → 0 with α* → 1.
- Pushing f_0 < 0.1 RAISES CF substantially (0.30 → 0.72). The
  lower-baseline-d' regime makes uniform-attention criterion gain
  larger (HR responds more sensitively to c at lower d'), which
  dominates the also-rising attention gain.
- Pushing h to a^3, a^4 (more-accelerating) raises CF to 0.66.
- Pushing N upward raises CF (more uncued locations dilute the cost
  of attention reallocation, but criterion gain also rises with N
  via the (1-FAR_u)^(N-1) term in P_no_fa).
- Pushing v upward raises CF substantially (0.30 → 0.78 → 0.97 →
  0.9997). Larger value differentials make criterion adjustment
  disproportionately powerful — the criterion can shift to capture
  the v·HR_c term at low cost.
- Joint extreme combos do not push CF below the in-sweep
  argmin of 0.30 — they raise it.

**Bottom line for Phase B:** the paper's swept r range [0.1, 10.0]
already captures essentially the worst-case CF for the swept (V, v,
variant) regime; pushing further does not produce a sub-0.50
construction outside the V = 1/N corner. The CF floor inside the
sweep (0.30 at variant B; 0.56 at variant A) IS the answer.

## Cross-reference to CR-014

CR-014 (C2 sensitivity probe) noted in passing that at V = 1/N
exactly (N = 2, V = 0.5 was the case noted), the model's cued/uncued
labelling has no informational content and the optimum is symmetric.
That observation was made for C4 (no-inversion claim) and spawned
CR-019. The C1 attack here surfaces the *same* V = 1/N degeneracy
but in a different direction: the β/γ asymmetry produces a non-
trivial attention shift even at V = 1/N, which inflates the (P2 - P3)
gap and shrinks CF. The two findings are consistent — the V = 1/N
boundary is a recurring source of model-edge-case behaviour the
paper's primary sweep includes but does not discuss.

## What the wiki sweep added

Mission §11 keyword sweep. Most relevant wiki entries:
- `muller_findlay1987_sensitivity_criterion` — foundational SDT
  decomposition of cueing into sensitivity (d') and criterion
  changes. The paper's whole C1 framing inherits from this work.
- `hawkins1990_attention_detectability` — Hawkins's psychophysical
  extension; demonstrates *sensitivity* improvements in cueing,
  partitioning out criterion. Cited by the paper as ref [2].
- `luo_maunsell2018_criterion_sensitivity` — neural-substrate paper:
  LPFC carries the criterion component, visual cortex carries
  sensitivity. Provides biological plausibility for the
  *dissociability* the paper exploits.
- `sridharan2017_sc_sensitivity_bias` — the most directly
  relevant *empirical* finding: re-analysing 4 SC-attention studies
  with a multialternative SDT framework, Sridharan et al. find
  bias (criterion) is the dominant SC attention effect — an
  empirical convergence with the paper's normative claim that
  criterion dominates value encoding in the swept regime.

None of these wiki entries CONTRADICT C1's spirit. They support the
*sensitivity vs criterion* decomposition machinery the paper builds
on. The empirical literature has not directly tested the criterion-
fraction-floor claim "CF ∈ [0.60, 0.96]" — that is a normative
claim from the paper's specific model. The wiki sweep does not
yield independent evidence to refute or support the specific 0.60
floor.

## Outcome

Verdict: **CONTESTED** (mission §3.1).

The paper's claim as written ("the criterion fraction ranges from
60% to 96% across all (r, V, v) combinations tested") is too strong:
my replication finds CF as low as 0.30 (variant B) and 0.56 (variant A)
inside the swept space. A weaker reformulation captures the
substantive point:

> "Variant A: CF ∈ [0.56, 1.00] across the 2,205 combinations, with
> 93% of rows having CF ≥ 0.60. Variant B: CF ∈ [0.30, 1.00], with
> 80% of rows having CF ≥ 0.60 and 92% having CF ≥ 0.50. Violations
> of the CF ≥ 0.60 condition concentrate at high r, low V (especially
> V near 1/N), and v ∈ {1, 2}, where validity-attention gain (which
> at V = 1/N is really β/γ-asymmetry-driven attention) rivals or
> exceeds criterion gain."

This reformulation preserves the substantive scientific point
(criterion typically dominates value encoding in the normative model)
while removing the false categorical "always 60–96%" claim.

Spawning follow-ups: see backlog.
