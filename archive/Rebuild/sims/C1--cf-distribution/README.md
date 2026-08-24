# C1 — criterion-fraction distributional sweep

| | |
|---|---|
| **Task** | RB-005 (rebuild backlog) |
| **Run** | rb-003 (2026-05-25) |
| **Output kind** | simulation |
| **Backs** | manuscript §results-C1 (RB-009), §results-A1 extension cell-wise |
| **Reuses** | `Rebuild/model/` (rb-001), reviewer reference `Critique/replications/C1--criterion-fraction-floor/` |

## What this sim does

Reproduces the paper's primary 4,410-cell parameter sweep on the *rebuilt*
model library at ρ ∈ {0, 0.2}, publishing CF as a **distribution** rather
than as the paper's stated [0.60, 0.96] floor. Three things land:

1. **Recovery (ρ=0).** Cell-wise comparison against the reviewer's
   `Critique/replications/C1--criterion-fraction-floor/output/results.json`
   confirms the rebuilt model reproduces the reviewer's substrate to
   `max |ΔCF| = 1.47e-6`, `max |ΔR(P1..P4)| ≤ 5.65e-7` across all
   4,410 cells. The ULP-scale gap is the cost of `1 - Phi(-b)` vs
   `Phi(b)` rearrangement in `floor_R` (mathematically identical, ULP-
   different under `scipy.special.ndtr`); well past the precision of any
   reported headline number.
2. **Distribution.** Full per-variant CF distribution at each ρ:
   range, median, 5/25/50/75/95 quantiles, fraction below 0.5/0.6/0.8.
3. **Δ-distribution.** Cell-wise `ΔCF = CF(ρ=0.2) − CF(ρ=0)` per
   variant, generalising rb-002's headline-cell A1 result across all
   4,410 cells.

## Headline numbers (`output/results.json`)

CF distribution, per variant, per ρ:

| variant | ρ | n_valid | min | median | max | <0.5 | <0.6 | <0.8 |
|---|---|---|---|---|---|---|---|---|
| A | 0.0 | 2205 | **0.5587** | **0.7552** | 1.0000 | 0.0000 | 0.0703 | 0.5701 |
| B | 0.0 | 2205 | **0.3040** | **0.7682** | 1.0000 | 0.0803 | 0.1973 | 0.5429 |
| A | 0.2 | 2205 | 0.4854 | 0.7197 | 1.0000 | 0.0122 | 0.2222 | 0.6177 |
| B | 0.2 | 2205 | 0.2406 | 0.7538 | 1.0000 | 0.1088 | 0.2522 | 0.5565 |

The ρ=0 row reproduces the reviewer's CR-002 numbers: variant-A min
0.5587, variant-B min 0.3040, combined median ≈ 0.76. **The paper's
[0.60, 0.96] floor is retracted at every variant**: even variant-A's
strict minimum (0.5587) falls below the stated 0.60.

Δ-distribution (CF(ρ=0.2) − CF(ρ=0)):

| variant | n | frac dec | frac inc | frac flat | median Δ | \|Δ\|q95 |
|---|---|---|---|---|---|---|
| A | 2205 | **0.8376** | 0.0834 | 0.0789 | **−0.0348** | 0.0640 |
| B | 2205 | 0.6372 | 0.2354 | 0.1274 | −0.0093 | 0.0650 |

The rb-002 headline-cell variant-A finding ("CF monotone-down in ρ")
**generalises but is not universal**: 84% of variant-A cells decrease,
16% increase-or-flat. Variant B is much more mixed: only 64% decrease,
24% increase, 13% flat; the rb-002 headline-cell flatness is one
manifestation of a broader variant-B pattern.

## Figures (`output/figures/`)

- **`cf_histogram.png`** — CF histogram, 4-panel (variant × ρ), with
  paper-floor reference lines and the median + frac-below annotations.
  The distributional shape (peak around 0.65, long left tail at
  variant B, a spike at CF=1) is the figure the rebuilt §results-C1
  cites in place of the paper's categorical floor language.
- **`cf_heatmap.png`** — CF over (r, V) at v=5, 4-panel (variant × ρ).
  Shows the regime structure: low-V × high-r is the CF<0.6 corner;
  high-V × low-r is the CF=1 corner. Variant B has a wider low-CF
  corner; both expand at ρ=0.2.
- **`cf_curves.png`** — CF vs r at V≈0.5, v-family of 5 curves,
  4-panel (variant × ρ). The "criterion shifts dominate at low r,
  attention reallocation takes over at high r" message, plotted.

## How to run

```bash
cd /Users/jonathanmorgan/AttentionManuscript
.venv/bin/python Rebuild/sims/C1--cf-distribution/run.py
```

Runtime: ~67 s on a 2026-era laptop (scipy.special.ndtr backend).
Deterministic (no RNG; all grids fixed); re-running produces identical
results.json.

## Output digest

`results.json` sha256 (pre-stamp, deterministic over sorted keys):
**`91fc4692dbc106eca9c90770c79e22f7f4757d76421ed55e7e8e91f80e44706c`**

## Manuscript claim this sim licenses

The rebuilt §results-C1 may now state:

> *"Across the paper's primary 4,410-cell (r, V, v) sweep, the criterion
> fraction CF is distributed over [0.56, 1.00] in variant A and
> [0.30, 1.00] in variant B, with a median of 0.76 in both cases. The
> paper's stated range CF ∈ [0.60, 0.96] is too narrow on both ends:
> 7% of variant-A cells fall below 0.60, and 8% of variant-B cells fall
> below 0.50. The substantive 'criterion typically dominates' reading
> survives — the median is comfortably above 0.5 and the distribution is
> concentrated above 0.6 — but the categorical floor is retracted.*
>
> *Promoting the A1 independence assumption to an equicorrelation
> parameter ρ = 0.2 amplifies the tail in variant A: the fraction of
> cells with CF < 0.6 rises from 0.07 to 0.22, and a 0.01 fraction of
> cells now lie below 0.5. Cell-wise CF(ρ=0.2) ≤ CF(ρ=0) holds in 84%
> of variant-A cells (median Δ = −0.035), generalising the rb-002
> headline-cell ordering across the sweep. The same ordering is weaker
> in variant B (64% of cells decrease, 24% increase), consistent with
> rb-002's report that variant B is essentially flat in ρ at the
> headline cell — a sensitivity, not a uniform claim."*

It does **not** yet license: (a) the conservation-family band on these
numbers — needs RB-019; (b) a closed-form expression for the boundary
of the CF<0.5 corner — flagged as a possible RB-024 derivation if the
corner geometry is clean.

## Caveats (mission §5.5 honest reporting)

- The α-grid step here is **0.02** (51 alpha points), matching the
  reviewer's CR-002 substrate. The rebuild model's `default_alpha_grid`
  is finer (step 0.005). The coarser grid keeps the recovery test
  meaningful and the runtime within the §11 budget; spot-checks at the
  fine grid agree with the coarse grid to within ~1e-3 on CF for the
  cells inspected (the optimum α is on the coarse grid in the headline
  regime).
- The recovery test compares cell-wise CF to ~1.5e-6 precision, not
  byte-for-byte. The gap is a known ULP-level scipy.ndtr reordering
  artifact in `floor_R` (`Phi(b)` vs `1 - Phi(-b)`); both are exact
  forms of the same probability, but they round differently. The
  agreement is well past the 4-decimal precision of every reported
  number.
- The recovery test's `valid_threshold = 1e-4` matches the reviewer's
  CR-002 mask. The validity-fraction is 100% for both variants (no
  cells were excluded as ill-conditioned at any rho); the V=1/N
  numerical fragility flagged in the reviewer's CR-002 code does not
  arise on this exact grid.
- The Δ-distribution `frac_flat` threshold is `|Δ| ≤ 1e-5`. Tighter
  thresholds (e.g. 1e-8) would shift some "flat" cells back into
  "decrease" or "increase"; the qualitative variant-A vs variant-B
  contrast is robust to the threshold choice.
