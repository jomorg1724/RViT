# RB-006 — C2 high-resolution VDA(r) family-of-curves

**Run id:** rb-004-2026-05-25 · **Prompt version:** 0.2
**Backing for:** manuscript §results-C2 (RB-010); confident-spine
headline result of the rebuild (mission §3.3).
**Output digest (sha256 of pre-hash JSON):**
`09ecef3c2c5a101820951398ed7d6e67d3398aede80c5f0bddfa42b6224fd783`

## What this simulation computes

At the C2/Figure-4 headline cell `(N=4, d'_max=2, f_0=0.5, h=sqrt,
V=0.5)`, variant A, it sweeps the VDA = R(P1) − R(P2) metric on an
**83-point + pinned log-spaced r-grid** for a v-family `v ∈ {2, 3, 5,
8, 10}` at two correlation magnitudes `ρ ∈ {0, 0.2}`, and computes the
**closed-form escape threshold r†(v)** from §2.3 of
`Critique/derivations/C2--non-monotonic-vda.md`:

    d'_b      := d'_max · f(1/N) = 1.5
    K_c(v) = ¼ · [V·v·φ(d'_b/2 − c_c*) +
                  CR(v)·φ(d'_b/2 + c_c*) · Φ(d'_b/2 + c_u*)^(N-1)]
    K_u(v) = ¼ · [(1−V)·φ(d'_b/2 − c_u*) +
                  (N−1)·CR(v)·Φ(d'_b/2 + c_c*)·
                          Φ(d'_b/2 + c_u*)^(N-2)·φ(d'_b/2 + c_u*)]
    r†(v)  = K_u(v) / [(N−1) · K_c(v)]

with (c_c*, c_u*) the **P3-optimal criteria at α = 1/N** (the
asymmetric uniform-attention criterion pair the inner P3 maximisation
picks out).

## Headline numbers

### Recovery (ρ=0, v=5) vs rb-002 — all pass

| r       | metric | rb-002 ref | rb-004 obs | |Δ|      |
|---------|--------|-----------:|-----------:|---------:|
| 0.3831  | VDA    | 0.07986    | 0.07985    | 5.93e-6  |
| 0.398   | VDA    | 0.07972    | 0.07972    | 1.07e-6  |
| 0.398   | CF     | 0.82952    | 0.82952    | 9.87e-7  |
| 1.000   | VDA    | 0.03983    | 0.03983    | 4.87e-6  |
| 1.000   | CF     | 0.72823    | 0.72823    | 2.02e-6  |
| 3.162   | VDA    | 0.00809    | 0.00809    | 1.01e-6  |
| 3.162   | CF     | 0.64094    | 0.64094    | 1.73e-6  |

Plus the rb-004 finer-grid argmax: peak VDA = **0.08300** at
**r = 0.3758** — a refinement gain over rb-002's coarser
25-point peak (0.07986 at r = 0.3831). Same model, same α-grid;
the higher peak is a grid-density artefact of the original
paper / rb-002 grid.

### Closed-form r†(v) — monotone decreasing in v

| v   | r†(v)  | c_c*    | c_u*    | K_c(v)   | K_u     |
|----:|-------:|--------:|--------:|---------:|--------:|
| 1   | 0.3433 | 0.40    | 1.05    | 0.0930   | 0.0958  |
| 2   | 0.1677 | 0.10    | 1.10    | 0.1722   | 0.0866  |
| 3   | 0.0995 | −0.05   | 1.10    | 0.2698   | 0.0805  |
| 5   | 0.0504 | −0.25   | 1.10    | 0.4937   | 0.0747  |
| 8   | 0.0222 | −0.50   | 1.10    | 0.9979   | 0.0664  |
| 10  | 0.0161 | −0.65   | 1.10    | 1.4097   | 0.0681  |

The §2.3 prediction that r†(v) is monotone-decreasing in v is
confirmed empirically by the rebuilt model.

### Peak-vs-threshold consistency (ρ=0) — §2.3 prediction holds

| v   | r†(v)  | r* (peak) | VDA*    | r* − r†(v)  | above r†? |
|----:|-------:|----------:|--------:|------------:|:---------:|
| 2   | 0.168  | 0.501     | 0.01233 | +0.334      | ✓         |
| 3   | 0.099  | 0.376     | 0.03698 | +0.276      | ✓         |
| 5   | 0.050  | 0.376     | 0.08300 | +0.325      | ✓         |
| 8   | 0.022  | 0.376     | 0.14422 | +0.354      | ✓         |
| 10  | 0.016  | 0.355     | 0.18284 | +0.339      | ✓         |

The peak r* > r†(v) for every v in the family. The peak r* clusters
near **r ≈ 0.36–0.40** for v ≥ 3, well above the individual r†(v) but
**near r†(v=1) ≈ 0.343** — consistent with the §2.3 mechanism that
VDA opens up when P1 escapes (r > r†(v)) but P2 is still locked
(r < r†(v=1)).

### A1 sensitivity (ρ=0 vs ρ=0.2, variant A)

| v   | peak ρ=0 | peak ρ=0.2 | Δpeak    | peak r (ρ=0) | peak r (ρ=0.2) |
|----:|---------:|-----------:|---------:|-------------:|---------------:|
| 2   | 0.01233  | 0.01036    | −0.00197 | 0.501        | 0.631          |
| 3   | 0.03698  | 0.03291    | −0.00407 | 0.376        | 0.473          |
| 5   | 0.08300  | 0.07954    | −0.00345 | 0.376        | 0.383          |
| 8   | 0.14422  | 0.14355    | −0.00067 | 0.376        | 0.383          |
| 10  | 0.18284  | 0.18387    | **+0.00103** | 0.355    | 0.383          |

Peak suppression by ρ shrinks with v and **flips sign at v = 10**
(+0.001 amplification). The peak r* shifts to higher r under ρ for
the low-v cells, consistent with rb-002's headline-cell sign-flip
locus (`r ≈ 0.4–0.6`).

## How to run

```bash
source .venv/bin/activate
python Rebuild/sims/C2--vda-vs-r-vfamily/run.py
```

Wall-clock: ~19 s (Phi backend `scipy.special.ndtr`, α-grid
Δα = 0.005, c-grid Δc = 0.05, 84-pt r-grid × 5 v × 2 ρ).
Deterministic; re-running must reproduce the sha256 byte-for-byte.

## Files

| path                                          | what it is                              |
|-----------------------------------------------|-----------------------------------------|
| `run.py`                                      | the sweep + r†(v) + recovery + figures  |
| `output/results.json`                         | full per-cell numbers + sha256          |
| `output/figures/vda_curves_vfamily.png`       | 2-panel (ρ=0 \| ρ=0.2) family-of-curves |
| `output/figures/r_dagger_vs_v.png`            | r†(v) trace; v-family points + r†(v=1) reference |

## Manuscript claim now licensed

> *"At the headline cell, the closed-form escape threshold
> `r†(v) = K_u(v) / [(N−1) · K_c(v)]` decreases monotonically in v —
> from r†(2) = 0.17 down to r†(10) = 0.02 — while the empirical peak
> argmax of VDA(r) lies in `r* ∈ [0.36, 0.50]` across the v-family,
> well above r†(v) and close to r†(v=1) ≈ 0.34. This is the §2.3
> mechanism made concrete: VDA opens up where P1 has escaped uniform
> attention but P2 has not, and the resulting interior maximum is a
> theorem of the model definitions rather than an empirical
> regularity. The non-monotonicity claim C2 returns at this strengthened
> form: peak r* > r†(v) for every v in {2, 3, 5, 8, 10}, with the peak
> magnitude growing from 0.012 (v=2) to 0.183 (v=10). Promoting the A1
> independence assumption to ρ = 0.2 suppresses the peak at low v
> (Δpeak = −0.002 at v=2, −0.003 at v=5) but amplifies it at v=10
> (+0.001) — consistent with rb-002's r-dependent A1 sign-flip
> generalised across the v-family rather than fixed-r."*

It does **not** yet license:
- the same statement for variant B (RB-006 is variant A; a small
  follow-up sim could rerun the same r†(v) closed form for variant B,
  but the rebuild explicitly reports the CF-upper-bound caveat as a
  variant-A pattern and variant B as a sensitivity — see CLAIM_LEDGER
  A1 row);
- a closed-form r†(v; ρ > 0) at ρ > 0 (the K_c, K_u derivation is
  written for ρ = 0; a follow-up derivation increment could repeat it
  with the equicorrelated ∂P_no-fa/∂d' inside the GH quadrature, but
  the present sim does not need it — the ρ = 0 r†(v) is the load-
  bearing closed form for the headline manuscript claim, and the
  ρ = 0.2 overlay is an empirical sensitivity, not a theorem);
- a conservation-family band on the peak VDA magnitudes (queued
  RB-019; once A3 generalisation lands, the headline VDA peaks above
  become a band over {additive, multiplicative} conservation).
