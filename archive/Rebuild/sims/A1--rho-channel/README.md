# sims/A1--rho-channel — VDA(r, ρ) and CF(ρ) at the C2 headline cell

Backlog task: **RB-002** (simulation increment, A1).
Backs: manuscript §model and §results-A1 — the "three levers, not two"
reframe and the corrected self-characterisation of A1.
Recovery contract: bit-for-bit at ρ=0 against
`Critique/replications/A1--correlated-fa/output/results.json`.

## What this sim computes

At the C2/Figure-4 headline cell

    N=4, d'_max=2, f_0=0.5, h=sqrt, V=0.5, v=5

under both reward variants (A: `CR = V v + (1-V)`; B: `CR = 1`):

1. **VDA(r; ρ)** family-of-curves on a log-spaced r grid (25 points in
   [0.1, 10] with the C2 reference points {0.316, 0.398, 1.0, 3.162}
   pinned in), for ρ in {0.0, 0.1, 0.2, 0.3, 0.4}. Diagnostics:
   per-ρ peak (value + argmax), the pointwise upper-bound check
   `VDA(r; ρ) <= VDA(r; 0)` ∀r, and the first r at which (ρ>0) excess
   becomes positive.
2. **CF(ρ)** at three r values {0.398, 1.0, 3.162} — cost-dominant
   peak, symmetric centre, benefit-dominant — plus a monotone-down-in-ρ
   diagnostic.
3. **Recovery test**: at ρ=0, single-cell VDA/CF/R_P1/R_P3/R_P4 at
   r ∈ {0.398, 1.0, 3.162} (variant A) match the reviewer's reference
   numbers to floating-point identity; peak VDA(r) at ρ=0 reproduces
   the reviewer's 0.07986 @ r ≈ 0.383; Slepian monotonicity holds.

## How to run

    .venv/bin/python3 Rebuild/sims/A1--rho-channel/run.py

Wall-clock ≈ 16 s on the rb-002 host (Apple Silicon, scipy.special.ndtr,
nq=64). The script aborts before drawing figures if the recovery test
fails. Output lands in `output/` (results.json + figures/*.png).

## Output

- `output/results.json` — full numeric content + meta. Deterministic.
- `output/figures/vda_curves_variantA.png` — variant A VDA(r) curves.
- `output/figures/vda_curves_variantB.png` — variant B VDA(r) curves.
- `output/figures/cf_vs_rho.png` — CF(ρ) at three r, variants A+B.

## Headline numbers (variant A, headline cell)

- **Recovery (ρ=0)**: single-cell max|diff| = 0.00e+00 at all three r
  references; peak VDA(r; 0) = 0.07986 at r = 0.3831; Slepian
  monotonicity satisfied across ρ ∈ {0, 0.05, ..., 0.8}.

- **VDA(r) peaks**, variant A:

  | ρ   | peak VDA | peak r |
  |-----|----------|--------|
  | 0.0 | 0.07986  | 0.3831 |
  | 0.1 | 0.08110  | 0.3831 |
  | 0.2 | 0.07955  | 0.3831 |
  | 0.3 | 0.07763  | 0.3980 |
  | 0.4 | 0.07368  | 0.3980 |

  Pointwise upper-bound `VDA(r; ρ) <= VDA(r; 0)` **fails** for every
  ρ > 0 — max excess over the ρ=0 curve grows from +4.84e-3 (ρ=0.1) to
  +1.01e-2 (ρ=0.4). First sign-flip r is ≈ 0.38 (ρ=0.1) to 0.56
  (ρ ≥ 0.3). This reproduces the reviewer's run-017 finding and is
  the *load-bearing* damage to the paper's §5.5 "upper bound on VDA"
  self-characterisation.

- **CF(ρ)** at three r, variant A:

  | r       | CF(0)  | CF(0.1) | CF(0.2) | CF(0.3) | CF(0.4) |
  |---------|--------|---------|---------|---------|---------|
  | 0.398   | 0.8295 | 0.8181  | 0.8071  | 0.7969  | 0.7875  |
  | 1.0     | 0.7282 | 0.7097  | 0.6903  | 0.6698  | 0.6473  |
  | 3.162   | 0.6409 | 0.6180  | 0.5936  | 0.5673  | 0.5386  |

  **Monotone-down in ρ at every r** — this is what independence
  actually upper-bounds: CF(0) ≥ CF(ρ).

## Variant B caveat (honest reporting per the simulation mandate §5.5)

In variant B (`CR = 1`), CF(ρ) at the headline cell is essentially
**flat** in ρ at all three r values (small non-monotone bumps, not a
clean upper-bound). Variant B drops the value-scaling on correct
rejections, so ρ↑ does not shift the relative leverage of the
criterion lever in the same way. The rebuilt manuscript should state
the CF upper-bound as a **variant-A result** and report variant B as
a sensitivity in which the effect washes out — not as a uniform claim
across reward conventions.

The VDA-rises-with-ρ finding survives in variant B (max excess up to
+2.94e-3, sign-flip at r ≈ 0.26), at a smaller absolute scale —
variant B's VDA is itself smaller by an order of magnitude.

## Recovery contract

Single source of truth for model code is `Rebuild/model/`; this script
does not reimplement primitives. The bit-for-bit ρ=0 cross-check
against the reviewer's reference output tightens the rb-001 contract
from "rho=0 → paper Eq. 9 within Phi backend tolerance" to
"rho=0 → reviewer reference numbers to last digit on every reported
(r, variant) cell." Re-running must reproduce sha256
**b692c06456530ccd1b319762d8a948814324d3129f39902ce9531a66d1206614**.

## What this sim does NOT yet license

- Headline numbers at cells outside (V=0.5, v=5, N=4, f_0=0.5, h=sqrt).
  The 4,410-cell distributional sweep is **RB-005** (queued, C1).
- An iso-VDA contour band over (V, v) (the C3 graded boundary): **RB-007**.
- The Slepian-monotonicity *derivation* and the booking-decomposition
  argument that A1 enters E[R] in exactly one place: **RB-003**
  (queued, derivation).
- The manuscript model section (the prose): **RB-004** (queued).

## Attribution

All model primitives via `Rebuild/model/` (rb-001), itself lifting from
`Critique/replications/A1--correlated-fa/run.py` (CR-052, run-017) and
its `C1`/`C5` upstreams. This sim is the first artifact under
`Rebuild/sims/`.
