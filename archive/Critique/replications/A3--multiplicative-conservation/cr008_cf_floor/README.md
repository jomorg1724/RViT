# CR-008 — A3 second vector: does criterion dominance survive βγ=1 in the at-risk cells?

**Claim:** A3 (mission §2.7; paper §5.5). The paper asserts that swapping the
additive conservation rule β+γ=2 for the multiplicative βγ=1 leaves the
qualitative findings — *non-monotonic VDA, no inversion, **criterion
dominance*** — robust. CR-040 (run-010, re-derivation) confirmed the first two
and found criterion dominance *erodes* to a thin margin on the V=0.5, v=5
reference slice (CF floor 0.601→0.507). This run settles the open question:
does that erosion push the criterion fraction **below 0.5** in the cells where
it is already most fragile under the additive rule?

**What this computes.** `cr008_run.py`:

1. **Block 0** — asserts the local `beta_gamma_multiplicative` is bit-identical
   to the parent run-010 script `../run.py` on the r-grid (provenance).
2. **Load + Select** — reads run-003's C1 phase-A sweep
   (`../../C1--criterion-fraction-floor/output/results.json`) and selects the
   set **S** of *valid* (total_gain>1e-4) cells with **additive CF < 0.60**
   (the at-risk cells; |S| = 590, 13.4 % of the 4,410-cell grid).
3. **Block A** — on each cell of S, recomputes additive CF (cross-check vs
   run-003's stored value) and computes multiplicative CF (β=√r, γ=1/√r).
   Decomposes the outcome into: pre-existing additive failures (CF_add<0.5),
   multiplicative failures (CF_mult<0.5), **new flips** (CF_add≥0.5 →
   CF_mult<0.5, the constraint-attributable A3 signal), and recovered cells.
4. **Block C** — a full 4,410-cell multiplicative sweep giving the **global**
   criterion-subordinate fraction under each rule, the paired ΔCF distribution,
   and the worst per-cell erosion (this also catches new flips *outside* S).

**Configuration (identical to run-003 / C1).** N=4, d'_max=2.0, f₀=0.5, h=√;
Φ = A&S 7.1.26 numpy (scipy unavailable in sandbox); Δc=0.05 on [-3,3] (121
pts); α-grid Δα=0.02 ∪ {1/N} (51 pts). Matching the config is what makes the
recomputed additive CF reproduce run-003's stored CF bit-for-bit, validating
that CF_mult is computed on the same footing.

**Headline result.**

| quantity | additive (β+γ=2) | multiplicative (βγ=1) |
|---|---|---|
| criterion-subordinate cells (CF<0.5), full grid | 177 / 4410 (4.01 %) | 368 / 4410 (8.34 %) |
| median CF, full grid | 0.7605 | 0.7578 |
| min CF (at r=10,V=0.25,v=4,B) | 0.3040 | 0.2309 |

- **191 cells flip** from criterion-dominant (CF≥0.5) under additive to
  criterion-subordinate (CF<0.5) under multiplicative; **0 recover** (ΔCF ≤ 0
  everywhere, max = 0.0 exactly — βγ=1 never *raises* CF). The new flips are
  concentrated in the **benefit-dominant high-r corner** (r ≳ 2.5), the same
  region where C1 already found additive CF dipping to 0.30.
- The criterion-subordinate fraction **roughly doubles** (4.0 %→8.3 %), but the
  **median CF is essentially unchanged** (0.7605→0.7578): the bulk of the space
  stays strongly criterion-dominant; the failure corner deepens and widens
  rather than relocating.

**How this differs from the paper.** The paper publishes no βγ=1 numbers (§5.5
asserts robustness without running it). The additive column above is run-003's
independent C1 replication (reproduced here to max|Δ|=0.0); the multiplicative
column is new.

**Verdict movement.** A3 **WEAKLY-SUPPORTED → CONTESTED** — the criterion-
dominance conjunct of §5.5 is robust as a central-tendency statement but not
as the per-cell/categorical "criterion is always the largest contributor"
statement; a precise reformulation is in
`Critique/verdicts/A3--multiplicative-conservation.md` v0.2.

**Reproduce.** `python3 cr008_run.py` (≈21 s; deterministic — re-run is
bit-identical except `elapsed_s`). Output → `output/results.json`,
`output/run.log`.
