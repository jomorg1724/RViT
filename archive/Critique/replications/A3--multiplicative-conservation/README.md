# A3 — multiplicative-conservation focused slice (CR-040)

**Claim attacked:** A3 (mission §2.7) — the additive conservation rule
`β + γ = 2`. The paper itself (§5.5, p.8) names the multiplicative
alternative `βγ = 1` and asserts a *robustness* claim:

> "the β + γ = 2 constraint conserves total attention magnitude;
> alternative constraints (e.g., multiplicative βγ = 1) could yield
> quantitatively different results, **though the qualitative
> findings—non-monotonic VDA, no inversion, criterion dominance—should
> be robust.**"

This script tests that robustness claim on **one focused slice**
(mission §8.5 — not a full 4,410-row sweep).

## What it computes

`run.py` is an independent re-implementation of the §2.4 model with a
**swappable β/γ map**:

| family | constraint | weights |
|---|---|---|
| `additive` | β+γ=2, β/γ=r | β=2r/(r+1), γ=2/(r+1) |
| `multiplicative` | βγ=1, β/γ=r | β=√r, γ=1/√r |

- **Block 0** verifies the rescaling identity
  `κ(r) = β_mul/β_add = γ_mul/γ_add = (r+1)/(2√r) = cosh(½ ln r)`
  to machine precision, and tabulates `Σ_mul = β_mul+γ_mul = 2κ ≥ 2`
  (multiplicative does **not** conserve the L1 magnitude).
- **Block 1 (C2)** sweeps `VDA(r)=R(P1)−R(P2)` over log-`r ∈ [0.1,10]`
  (21 pts) at the paper's reference regime (N=4, d′_max=2, f₀=0.5, √,
  V=0.5, v=5, Variant A) under **both** families.
- **Block 2 (C1)** the criterion fraction
  `CF(r)=[R(P3)−R(P4)]/[R(P1)−R(P4)]` over the same slice. (P3,P4 sit at
  α=1/N where β,γ multiply a zero bracket, so R(P3),R(P4) are
  *family-independent* — only R(P1) moves.)
- **Block 3 (C4)** re-optimises α over a grid including α<1/N to check
  for inversion under the multiplicative map, at the reference r-grid
  and the most-adversarial V≥1/N cells from CR-004 (r=10).

Grid: log-r 21 pts; α-grid Δα=0.005 + the 1/N point (200 pts); c-grid
Δc=0.05 over [−3,3] (121 pts). Φ via scipy if present, else A&S 7.1.26
(both code paths share the same Φ, so any Φ error cancels in the
P1−P2 / P3−P4 gaps and cross-family differences).

## How to run

```bash
cd Critique/replications/A3--multiplicative-conservation
python3 run.py            # writes output/results.json and output/run.log
```

## Expected output (run-010, 2026-05-22)

```
[Block 0] max |identity deviation| over grid: 8.882e-16
[Block 1+2]
  [additive      ] peak VDA=0.07974 @ r=0.3981 | VDA(0.1)=0.01848 VDA(10)=0.00085 | CF∈[0.601,0.961]
  [multiplicative] peak VDA=0.09085 @ r=0.3162 | VDA(0.1)=0.04111 VDA(10)=0.00317 | CF∈[0.507,0.917]
[Block 3] min α*_P1/P2 = 0.2500 = 1/N ; inversion detected? False
```

## How this differs from the paper's code

The paper has no published multiplicative-constraint run (it floats
βγ=1 in §5.5 but does not execute it). The additive column here is a
re-derivation cross-check, not the paper's code; its additive peak
(0.0797 @ r=0.398) lands on the paper's Figure-4 reference (~0.080),
which validates the implementation before the multiplicative
comparison is trusted.

See `notes.md` for the interpretation and the verdict link.
