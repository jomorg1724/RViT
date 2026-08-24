# Notes — A3 multiplicative-conservation slice (CR-040, run-010)

## Headline

The paper's §5.5 robustness claim **survives this slice**: under the
multiplicative constraint βγ=1 (β=√r, γ=1/√r), all three named
qualitative findings hold at the reference regime — (i) VDA is
non-monotonic in r with an interior peak, (ii) no inversion (α*≥1/N),
(iii) criterion dominance (CF>0.5). But the survival of (iii) is
**razor-thin** (min CF = 0.507 at r=10 vs 0.601 additive), so the
verdict is WEAKLY-SUPPORTED pending the broader-cell second vector
(CR-008).

## The κ(r) rescaling theorem (Block 0)

Both families share the ratio β/γ = r; they differ only in the
conserved quantity. The multiplicative pair is the additive pair
scaled by a **common** factor:

```
κ(r) = β_mul/β_add = γ_mul/γ_add = (r+1)/(2√r) = ½(√r + 1/√r) = cosh(½ ln r)
```

Verified to 8.9e-16 (machine precision) across the grid. Properties:
κ(1)=1 (the unique minimum), κ≥1 always, κ(1/r)=κ(r), κ→∞ at both
extremes. Therefore:

- `β_mul + γ_mul = 2κ(r) ≥ 2`: **multiplicative does NOT conserve the
  L1 magnitude**. The paper's phrase "β+γ=2 conserves total attention
  magnitude" is an *additive-only* property; βγ=1 systematically
  *inflates* total gain magnitude as |ln r| grows (κ(0.1)=κ(10)=1.74,
  i.e. +74% at the swept extremes; κ(0.3)≈1.20 at the VDA peak).
- Geometrically: in (β,γ) space the additive family is the line
  β+γ=2; the multiplicative family is the hyperbola βγ=1. By AM–GM the
  hyperbola lies **on or above** the line everywhere, tangent only at
  (1,1). So the βγ=1 model is uniformly *more aggressive* (larger
  departures from baseline) than β+γ=2, except at r=1 where they
  coincide. This is the mechanism behind every quantitative shift
  below — it is structural, not arbitrary.

## C5 cross-check (the r=1 row)

At r=1 the two families produce **identical** numbers to all printed
digits: VDA=0.03983, CF=0.7282, α*_P1=1.000, α*_P2=0.750. This is the
constraint-agnosticism proved in the C5 v0.2 verdict (βγ=1 ∧ β+γ=2 ⇒
β=γ=1) showing up numerically — a free consistency check linking
CR-040 back to the just-closed C5.

## C2 — non-monotonic VDA (Block 1): ROBUST, peak shifts left + up

| family | peak r | peak VDA | VDA(0.1) | VDA(10) |
|---|---|---|---|---|
| additive | 0.398 | 0.0797 | 0.0185 | 0.00085 |
| multiplicative | 0.316 | 0.0909 (+14%) | 0.0411 | 0.00317 |

Both curves are cleanly single-peaked in the cost-dominant regime
(r<1) and decline toward both extremes — the non-monotonicity is
**robust**. The peak moves one log-grid step *left* (0.398→0.316, i.e.
deeper into cost-dominance) and is *14% higher* under βγ=1. This is
exactly what the κ-theorem + the two-limit theorem predict: βγ=1 still
has β(0)=√0=0 (cued benefit vanishes) and γ(∞)=1/√∞=0 (uncued cost
vanishes), so VDA→0 at both extremes under both rules; the inflation
κ(r)>1 off r=1 raises the interior peak.

(My additive peak 0.0797 ≈ the paper's Figure-4 reference ~0.080 — and
slightly closer to it than CR-001's coarse-grid 0.0774, because this
run uses the paper's Δα=0.005 resolution.)

## C1 — criterion fraction (Block 2): SURVIVES but ERODES

CF is monotone decreasing in r for both families (P3,P4 are
family-independent; only the R(P1) denominator grows):

| family | CF(r=0.1) | CF(r=1) | CF(r=10) = min |
|---|---|---|---|
| additive | 0.961 | 0.728 | **0.601** |
| multiplicative | 0.917 | 0.728 | **0.507** |

Criterion dominance (CF>0.5, criterion captures the *majority* of
value-related reward) **survives at this slice under βγ=1**, but the
floor drops from 0.601 to 0.507 — a margin of only 0.007 above the
50% line at r=10. The mechanism: at r=10, β_mul=√10≈3.16 vs
β_add≈1.82, so the attentional gain R(P1)−R(P4) is materially larger
under multiplicative, shrinking CF. **Caveat / second-vector flag:**
C1 is *already CONTESTED* under the additive rule (run-003 found CF as
low as 0.304 in variant-B, low-V, high-v cells outside this slice).
Since βγ=1 lowers CF wherever R(P1) can grow, those same cells will
very plausibly push CF *below 0.5* under βγ=1 — i.e. criterion
dominance may *fail* in part of the space the paper claims robustness
for. This slice does not visit those cells (§8.5), so the verdict
flags it as the designated next attack (CR-008, the multiplicative
full replication).

## C4 — no inversion (Block 3): ROBUST

min α*_P1/P2 = 0.2500 = 1/N exactly, across the reference r-grid and
the most-adversarial V≥1/N cells at r=10. **No inversion under βγ=1**
within V≥1/N — consistent with CR-004's location-count-asymmetry
mechanism, which depends on f(1)=1 vs f(1/(N−1))<1 and on w_c≥w_u
(V≥1/N), neither of which involves β,γ. (C4 already provably fails for
V<1/N under *both* rules — that is the CONFIRMED-CONDITIONAL scope, not
re-tested here.)

## Bottom line for the A3 verdict

The paper's §5.5 robustness claim is **WEAKLY-SUPPORTED** (first attack
vector). Qualitative findings (i)–(iii) all survive the βγ=1 swap at
the reference slice; the quantitative shifts (peak +14% and left, CF
floor −0.09) are exactly the κ(r)-magnitude-inflation the paper's own
"could yield quantitatively different results" anticipates. The one
genuine concern — that criterion dominance (CF>0.5) may *break* under
βγ=1 in the low-V/high-v cells where C1 already fails under β+γ=2 — is
spawned as the second vector (CR-008, full multiplicative replication).
The paper's incidental phrasing "β+γ=2 conserves total attention
magnitude" should be read narrowly: βγ=1 does *not* conserve it
(Σ=2κ≥2), so the constraints are not interchangeable reparameterisations.
