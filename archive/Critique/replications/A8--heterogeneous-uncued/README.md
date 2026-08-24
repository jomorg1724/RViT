# CR-036 — A8 heterogeneous-uncued allocation (replication)

**Claim/assumption attacked:** A8 (mission §2.7; paper §2.2, verbatim:
*"The remaining attention is distributed equally among uncued locations, so
each receives (1−α)/(N−1)."*). The model's policy space is 1-D in α; the
uncued locations are forced to share attention equally. A8 is implicit in
§2.2/§2.3, is NOT among the paper's four explicit §5.5 limitations, and was
surfaced + ratified at prompt v0.2.

**Attack vector:** replication (run-012, 2026-05-24).

## What `run.py` computes

A general-N optimal-observer model with an **arbitrary allocation vector**
`a` and **arbitrary validity vector** `w` (location 0 = cued), per-location
sensitivities under the paper's β/γ gain–loss rule generalised to each
location's own departure from the 1/N baseline, and **per-location criteria**
optimised exactly. It reduces identically to the paper's homogeneous model
(Eqs. 7–9) when `a`/`w` are homogeneous.

- **VALIDATION** — reproduces the homogeneous headline numbers (C2 VDA peak
  ≈ 0.077 at r≈0.398; C1 CF 0.86/0.73/0.64 at r=0.3/1.0/3.2, matching run-003
  including the known CR-022 r=0.3 transcription-error flag).
- **PART 1** — under *equal* uncued validity, is the equal uncued split the
  OPTIMUM (not just the assumption)? Fix the cued allocation at the
  homogeneous α*, scan the uncued redistribution, and probe the curvature
  R″(0) along the symmetric redistribution direction.
- **PART 1b** — FORCE a uniform cued allocation (α=1/N) so every transfer
  form has a real uncued budget; closes the accelerating-h (a²) loophole.
- **PART 1c** — DECISIVE: full unconstrained simplex optimum vs the
  homogeneous-constrained optimum at headline cells and at the cells most
  likely to break A8 (V=1/N, v=1, r>1).
- **PART 2** — introduce one *anti-cued* (low-target-validity) slot, jointly
  optimise the simplex, and test for a **graded suppression gradient**
  (Wang & Theeuwes link).

## How to run

```bash
python3 run.py        # writes output/results.json ; ~45 s ; numpy only (no scipy)
```

## Headline results

1. **A8 is INNOCUOUS for the headline claims C1–C5.** At every
   headline-relevant cell the unconstrained simplex optimum coincides with
   the homogeneous-constrained optimum (Part 1c: ΔR ≤ grid slack, uncued
   spread 0). Relaxing A8 leaves the C1/C2 numbers exactly unchanged.
2. **But A8 is NOT a trivially-free assumption.** With a *forced* uncued
   budget (Part 1b), the **benefit-dominant regime (r>1) prefers to
   CONCENTRATE** the uncued budget (R″(0)>0), driven by the same β/γ
   asymmetry as the whole paper. The headline-claim safety is a *structural
   coincidence*: the concentrate-favouring regime also drives the cued
   allocation α*→1, so the uncued budget vanishes before concentration can
   bite. Worth stating explicitly; the paper's §2.2 wording presents
   homogeneity as a definitional choice rather than a derived optimum.
3. **Relaxing A8 ENRICHES the model.** With heterogeneous *validity* (Part 2),
   the optimum reproduces a **graded suppression** of the anti-cued slot
   (a_anti* falls monotonically below the uniform baseline and below the
   higher-validity uncued slots, with freed attention reallocated to higher-
   value slots). This matches the Wang & Theeuwes statistical-learning
   suppression gradient and confirms in the affirmative the CR-031/run-007
   conjecture that the model predicts α<1/N at anti-cued locations.

## Difference from the paper's published code

The paper provides no code in this repo. The model is re-implemented from
Eqs. (1)–(9). Two generalisations beyond the paper's homogeneous model:
(i) per-location β/γ tied to each location's own departure sign (consistent
with the §2.3 "roles reverse" note); (ii) per-location criteria via an exact
joint grid (G≤2) or a multi-restart coordinate ascent (G≥3) — both validated
to machine precision against the C4 base optimiser (G=2) and a joint 3-D grid
(G=3); see `notes.md`.

## Files
- `run.py` — the script.
- `output/results.json` — numerical results (deterministic; no RNG).
- `output/_determinism_check.json` — record of the byte-identical re-run.
- `notes.md` — modelling choices, caveats, the optimiser-validation story.
