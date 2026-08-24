---
type: replication-readme
claim_id: C4
attack: re-derivation (with numerical corroboration)
companion_derivation: Critique/derivations/C4--no-inversion.md
prompt_version: 0.1
run_id: run-006
---

# C4 — "Inverted attention is never optimal": replication

This directory contains the numerical companion to the
re-derivation in `Critique/derivations/C4--no-inversion.md`.

## What it computes

`run.py` runs three steps:

- **Step A.** Numerically evaluates the closed-form boundary
  inversion threshold $r^\star_{\mathrm{inv}}(V, v, N, \mathrm{CR}) = (N-1)\,A_0/B_0$
  derived in §3 of the derivation, across the paper's primary
  $(V, v, \text{variant})$ grid at $N = 4$. Reports the fraction of
  cells with $r^\star_{\mathrm{inv}}$ inside the swept $r$-range
  $[0.1, 10]$ — i.e. cells where the *local* derivative test fails
  somewhere in the sweep.

- **Step B.** At the cells flagged in Step A, computes the full
  $\mathbb{E}[R](\alpha)$ curve on the paper's fine grid ($\Delta\alpha = 0.005$)
  at $r = 10$ (most cost-flipped, most adversarial). Reports
  global, left-branch, and right-branch maxima. If any cell has
  $\alpha^\star_{\mathrm{global}} < 1/N$, C4 would be refuted.

- **Step C.** CR-019 V=1/N degeneracy refinement at three sub-cases:
  (i) $(V=1/N=0.25, v=1, N=4)$ across $r$, the symmetric corner of
      the primary sweep;
  (ii) $(V=1/N=0.5, v=5, N=2)$ across $r$, the CR-014 P2-inversion
       cell from secondary sweep;
  (iii) Anti-cue regime $(V < 1/N, v \in \{1, 5\}, N = 2)$ across
        $(V, r)$ — outside the paper's *primary* sweep but inside
        the paper's stated V-range $[0.25, 1.0]$ when discussed
        generally. The verdict-relevant test: does inversion occur
        at $v = 1$ when $V < 1/N$ flips the location-count
        argument?

## Expected output

From `output/run.log`:

```
STEP A — Closed-form inversion threshold r*_inv(V, v, N=4, variant).
  Across 210 (V, v, variant) cells at N=4:
    r*_inv  > 10        :  107  ( 51.0%)  C4 boundary trivially holds
    r*_inv  ∈ [0.1, 10] :  103  ( 49.0%)  Step B inspects these
    r*_inv  < 0.1       :    0  (  0.0%)  boundary fails at all swept r

  10 most-adversarial cells (smallest r*_inv):
       V    v  variant      r*_inv
   0.250    1        A      1.0000   ← V=1/N corner: r*_inv = 1 exactly
   0.250    1        B      1.0000
   ...

STEP B — Sweep α at r=10 across the 12 most-adversarial cells:
  All 12 cells have α*_global = 0.95–0.99 (right branch wins).
  Left-branch max always exists (near α = 0.02) but R_left < R_right
  by 0.005–0.15 reward units. PRIMARY-SWEEP INVERSIONS: 0.

STEP C — V=1/N degeneracy:
  (i)  At (V=0.25, v=1, N=4), r ≤ 1: degenerate (R_left ≈ R_right);
       r > 1: right-branch wins strictly (location-count asymmetry).
  (ii) At (V=0.5, v=5, N=2), the cued is still value-boosted, so
       right-branch wins for all r.
  (iii) Anti-cue at v=1: at (V=0.25, N=2, r=1.0), α*_global = 0.180
       < 1/N = 0.5. Inversion is globally optimal. C4 holds only
       under the conditional V ≥ 1/N (or v sufficiently large).

Verdict: WEAKLY-SUPPORTED — C4 holds globally across primary sweep;
boundary closed form predicts left-branch local inversion in some
cells but right-branch always dominates globally.
```

## Differences from the paper

- The paper's primary sweep covers exactly the regime where C4 holds
  ($N = 4$, $V \in [1/N, 1.0]$, $v \in \{1, \dots, 5\}$). Within
  that regime, this replication finds zero inversions, matching the
  paper's 4,410-row result. The existing 4,410-row sweep at
  `Critique/replications/C1--criterion-fraction-floor/output/results.json`
  also independently corroborates this (search for rows with
  `alpha_p1 < 0.25` or `alpha_p2 < 0.25` — there are none).

- This replication *extends* the test by deriving a closed-form
  threshold $r^\star_{\mathrm{inv}}$ that the paper's empirical sweep
  could not have surfaced. The threshold reveals that the local
  derivative test fails in ~half the swept cells — a behavior the
  paper's "regardless of $r$" wording obscures.

- This replication tests the **anti-cue regime** (V < 1/N at N = 2)
  which the paper does not. The result is direct: C4 fails outside
  the conditional $V \geq 1/N$ with $v \geq 1$.

## Re-running

```bash
cd Critique/replications/C4--no-inversion
python3 run.py   # writes output/results.json and output/run.log
```

No external dependencies beyond `numpy` and `math` (no scipy
required — uses `math.erf` for Φ).

## Files

- `run.py` — script.
- `output/results.json` — full structured results (step A row-level,
  step B row-level, step C row-level, plus metadata and verdict).
- `output/run.log` — captured stdout of the run.
- `README.md` — this file.
