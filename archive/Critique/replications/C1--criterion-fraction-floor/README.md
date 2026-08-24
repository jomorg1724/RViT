# C1 sensitivity attack — criterion-fraction floor

**Task:** CR-002 (mission `agents/RESEARCH_BACKLOG.md`).
**Claim under attack:** C1 (mission §2.6).
**Attack vector:** sensitivity (mission §3.2).
**Run:** run-003, prompt v0.1, 2026-05-17.

## Claim as written

Paper §4.1 (last paragraph):

> "This pattern holds across the full sweep: the criterion fraction
> ranges from 60% to 96% across all (r, V, v) combinations tested.
> Criterion adjustment is always the single largest contributor to
> value-related reward."

Paper §4.1 (specific numerical reference points): "In the cost-dominant
regime (r = 0.3), the criterion fraction reaches 96%. ... In the
symmetric case (r = 1.0), the criterion fraction is 73%. Even in the
benefit-dominant regime (r = 3.2), where attention is cheap to deploy,
criterion still accounts for 64% of total gain."

## What this code computes

`run.py` implements the paper's policy decomposition (mission §2.5)
and performs two phases:

**Phase A — primary sweep.**
Faithfully replicates the paper's primary 4,410-row grid:
  - r ∈ 21 log-spaced points in [0.1, 10.0] (r=1.0 included)
  - V ∈ 21 linearly-spaced points in [1/N, 1.0]
  - v ∈ {1, 2, 3, 4, 5}
  - variant ∈ {A, B}
  - Fixed: N = 4, d'_max = 2.0, f_0 = 0.5, h = √, α-grid Δα = 0.02
    (+1/N), c-grid Δc = 0.05 on [-3.0, +3.0].

Records R(P1), R(P2), R(P3), R(P4), VDA, criterion gain,
validity-attention gain, and the criterion fraction
CF = (R(P3) - R(P4)) / (R(P1) - R(P4)) for each row.

**Phase B — extrapolation probes.**
Anchored at the (V*, v*, variant*) that produced the in-sweep argmin
CF in Phase A, push the parameters just outside the paper's swept
ranges along six axes:

  (i)   r ∈ {20, 50, 100, 500, 2000} — beyond the paper's r=10 cap.
  (ii)  f_0 ∈ {0.05, 0.02, 0.01, 0.001} — below the paper's f_0=0.1
        secondary-sweep floor.
  (iii) h ∈ {a^3, a^4} — more accelerating than the paper's a^2.
  (iv)  N ∈ {8, 16, 32} — more locations than the paper's primary
        N=4 and secondary N∈{2,4}.
  (v)   v ∈ {10, 20, 50, 100} — larger value contrast than the
        paper's v=5 cap.
  (vi)  Combinations of the above for joint stress tests.

Goal: push CF below 0.50 to see whether attention reallocation
can normatively overtake criterion adjustment as the dominant
value-encoding mechanism outside the paper's sweep.

## Speed and numerical notes

The criterion grid optimisation is done by brute-force grid search
(101 × 101 = 10,201 (c_cued, c_uncued) points per α-evaluation).
The Phi (standard normal CDF) is implemented as a numpy-vectorised
Abramowitz & Stegun 7.1.26 erf approximation (max abs error ~1.5e-7,
verified to ~7e-8 in spot tests). scipy was not installable in the
sandbox due to disk pressure (cf. CR-001 notes); the polynomial
approximation is ~100× faster than the math.erf Python-loop fallback
and is more than accurate enough for CF-floor work.

The full 4,410-row Phase A completes in about 20 seconds.

## Numerical validation against the paper's reference points

At the paper's central regime V ≈ 0.51, v = 5, variant A, N = 4,
f_0 = 0.5, h = √ (paper §4.1 reference points):

| r       | Paper CF | This code CF | Status |
|---------|----------|--------------|--------|
| 0.3162  | 0.96     | 0.8542       | DISAGREEMENT — see notes.md |
| 1.0     | 0.73     | 0.7284       | matches to 0.002 |
| 3.1623  | 0.64     | 0.6422       | matches to 0.002 |

The r = 0.3 disagreement is a 11-percentage-point gap and is not
explained by α-grid resolution, c-grid resolution, or c-grid range.
It IS consistent with a visual reading of the paper's own Figure 2,
which shows the criterion bar at r = 0.3 reaching ≈ 85% of the total
gain rather than 96%. The most likely explanation is that the paper's
text §4.1 "96%" is a transcription error from the actual numerical
value (~85% per Figure 2's bars). The r = 1.0 and r = 3.2 references
match precisely.

The replication also reproduces the paper's Figure 4 peak (VDA = 0.080
at r ≈ 0.3) within the grid: the C2 replication previously found peak
VDA = 0.0774 at r = 0.398 (CR-001), and this code's R(P1) – R(P2) at
the matching cell is 0.0795 — consistent.

## How to run

```bash
cd Critique/replications/C1--criterion-fraction-floor
python3 run.py | tee output/run.log
```

Outputs to `output/results.json`.

## Headline result

Across the 4,410 swept rows:
- **CF ∈ [0.3040, 1.0000]** (paper claim: ∈ [0.60, 0.96]).
- Variant A: CF ∈ [0.5587, 1.0000]. 155 of 2,205 variant-A rows
  (7.0%) fall below 0.60. 0 fall below 0.50.
- Variant B: CF ∈ [0.3040, 1.0000]. 435 of 2,205 variant-B rows
  (19.7%) fall below 0.60. 177 (8.0%) fall below 0.50.
- Argmin (overall): (r=10, V=0.25, v=4, variant B) → CF = 0.3040.
- Argmin (variant A, v≥2): (r=10, V=0.29, v=3) → CF = 0.5588.

Phase B extrapolation, anchored at (r=10, V=0.25, v=4, variant B):
- Axis (i) r > 10 pushes CF further down to 0.26 at r=2000.
- All other extrapolation axes (lower f_0, accelerating h, larger N,
  larger v, joint combos) push CF *upward* relative to the V=1/N
  anchor — they do not assist a sub-0.50 construction.

The paper's claim "CF ∈ [0.60, 0.96] across all 4,410 combinations" is
falsified by the model's own numerical output. The substantive spirit
of C1 (criterion typically dominates value encoding) survives but
must be re-stated with explicit conditioning.

See `notes.md` for the diagnostic trace; the verdict and evidence
files at `Critique/verdicts/C1--criterion-fraction-floor.md` and
`Critique/evidence/C1--criterion-fraction-floor.md` summarise the
finding's implications.
