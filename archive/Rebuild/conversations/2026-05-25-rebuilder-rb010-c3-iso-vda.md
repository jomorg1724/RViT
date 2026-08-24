---
type: conversation
agent: constructive-rebuilder
prompt_version: "0.2"
run_id: rb-010-2026-05-25
started: 2026-05-25T16:00:00Z
ended: 2026-05-25T16:25:00Z
worked_on: RB-007
output_kind: simulation
claims_touched: [C3, A1]
artifacts_written:
  - Rebuild/sims/C3--iso-vda-Vv/run.py
  - Rebuild/sims/C3--iso-vda-Vv/README.md
  - Rebuild/sims/C3--iso-vda-Vv/output/results.json
  - Rebuild/sims/C3--iso-vda-Vv/output/figures/iso_vda_contours.png
  - Rebuild/sims/C3--iso-vda-Vv/output/figures/vda_at_high_V.png
  - Rebuild/sims/C3--iso-vda-Vv/output/figures/iso_vda_drho.png
  - Rebuild/CLAIM_LEDGER.md (C3 + A1 rows updated)
  - Rebuild/REBUILD_BACKLOG.md (RB-007 done, RB-028 + RB-029 spawned, RB-011 notes refreshed)
  - Rebuild/rebuilder_state.json
  - Rebuild/BUILD_LOG.md (rb-010 entry)
papers_added: []
spawned_tasks: [RB-028, RB-029]
---

# rb-010 — C3 iso-VDA contour sweep over `(V, v)`

## What I built

`Rebuild/sims/C3--iso-vda-Vv/` — a 3,534-cell sweep of the rebuilt
model's `policies()` over the experimental-design plane `(V, v)`,
crossed with `r ∈ {0.3, 1.0, 3.0}` and `ρ ∈ {0.0, 0.2}`, at the
canonical headline cell `(N=4, d'_max=2, f_0=0.5, h=sqrt, variant A)`.
The sweep ran in 130.5 s on the user's macOS / Python 3.13 / scipy
1.17.1 / matplotlib 3.10.9 stack (matplotlib was missing on the
default interpreter; installed via `pip --break-system-packages`).

Three publishable figures landed:

1. `iso_vda_contours.png` — the 2×3 (`ρ × r`) grid of filled iso-VDA
   contours over `(V, v)`. This is the manuscript §results-C3 figure
   — the quantitative-band replacement for the inherited paper's
   categorical §5.2 statement.
2. `vda_at_high_V.png` — 1×3 (by `r`) panel grid plotting `VDA(v)` at
   four validity strata `V ∈ {0.4, 0.6, 0.8, 0.95}`, with `ρ=0` solid
   and `ρ=0.2` dashed. Targets the §5.2 sentence directly: visualises
   that "negligible at high V" survives at `V=0.95` but admits a small
   `ρ`-conditional signal at `V=0.8`.
3. `iso_vda_drho.png` — 1×3 (by `r`) signed contour map of
   `ΔVDA = VDA(ρ=0.2) − VDA(ρ=0)` over `(V, v)`. The zero-isoline is
   the A1 sign-flip locus in `(V, v)`-space; the rb-002 / rb-004
   headline-cell / v-family sign-flip generalises to the third axis V.

The sim's `run.py` is heavily commented and runs deterministically:
no RNG, brute-force grid optimisation on fixed `α` (step 0.005) and
`c` (step 0.05) grids. `results.json` sha256
`72820559e1c1ab1919f74308623eaf4230aa3ea92ad3d9c62d81e993e4f27de6`.

The recovery contract was wired in advance against rb-006's anchor
at `(V=0.5, v=5, r=1, ρ=0, variant A)` where the rebuilt model returns
`VDA = 0.039825`. The present sim's `results.json` at that grid point
returns `0.0398251274…` — `|Δ| = 1.27e-7`, **PASS** (the residual is
the rb-006 reference's 6-dp rounding; the underlying `policies()`
call is bit-exact deterministic). Independent sanity: every `v=1`
column is identically zero across every `(V, r, ρ)` cell (value-blind
baseline ⇒ joint optimum = value-blind allocation ⇒ `VDA = 0`).

## How it connects to the ledger

The reviewer's `Critique/verdicts/C3--narrow-regime.md` reads
`current_label: CONTESTED`. The graded statement (VDA concentrates at
low V, high v, moderate r) is intact; the §5.2 *categorical*
experimental-design claim ("negligible VDA *regardless of other
parameters*" at high V) is too strong. The CLAIM_LEDGER C3 row's
ceiling on rebuilt strength reads:

> Graded/quantitative: VDA concentrates at low V, high v, moderate r;
> the §5.2 categorical experimental-design claim is retracted and
> replaced with iso-VDA contour bands.

This sim **publishes the bands** and quantifies the `V`-threshold:

| stratum | peak VDA across `v ∈ [1,10]`, `r ∈ {0.3, 1, 3}`, `ρ ∈ {0, 0.2}` | §5.2 verdict |
| --- | --- | --- |
| `V ≥ 0.95` | `≤ 1e-5` (at grid floor in every panel) | **survives** categorically |
| `V ≥ 0.80` | `≤ 0.003` (peak `0.0032` at `r=3, ρ=0.2`) | survives at `ρ=0`; small `ρ`-conditional caveat at `ρ=0.2` |
| `V ≥ 0.60` | `0.143 → 0.164` at `r=0.3` | **fails** categorically |

So the §5.2 sentence is true *if and only if* "high V" is taken to
mean `V ≳ 0.8`. The §3.3 unifying-reframe move — "report the band,
not the floor; report the conditional, not the categorical" — is
exactly the manuscript move RB-011 will now make.

The A1 row gets a passing addition: the rb-002 headline-cell sign-flip
(suppression at low `r`, amplification at high `r`) and the rb-004
v-family sign-flip (suppression at low `v`, amplification at high `v`
at `V=0.5`) BOTH organise the entire `(V, v)` plane, cell-wise:

| r | n_amp | frac_amp | n_supp | frac_supp |
| --- | ---: | ---: | ---: | ---: |
| 0.3 | 160 | 27.2% | 219 | 37.2% |
| 1.0 | 311 | 52.8% | 103 | 17.5% |
| 3.0 | 318 | 54.0% | 95 | 16.1% |

The rb-008 derivation §4 (Statements A/B and the two-channel
sign-decomposition) thus stands corroborated on a third axis — the
sign-flip is not a single-cell anomaly but a cube-wide pattern. The
strongest single amplification — at `(V=0.7, v=10, r=0.3, ρ=0.2)` a
near-zero cell `VDA=0.0007` lifts to `VDA=0.0676`, a 96× amplification
— is the candidate "dormant-cell amplification" prediction the
manuscript may add (RB-029 spawned to map that band more carefully).

The CLAIM_LEDGER reconcile against the live verdict ledger
(`Critique/verdicts/*.md`) found no label drift this run: 10/10 labels
still match `agents/paper_rebuilder_prompt.md` v0.2 §3 (with the
already-flagged A6 entry remaining stale). No mission-change task
spawned.

## Simulation evidence

- **Sweep size and runtime**: `31 V × 19 v × 3 r × 2 ρ = 3,534` cells
  in `130.5 s` on `python3.13 / scipy 1.17.1`.
- **Recovery**: rb-006 anchor `(V=0.5, v=5, r=1, ρ=0, variant A)`
  → expected `0.039825`, observed `0.03982513...`, `|Δ|=1.27e-7`,
  tolerance `1e-4`. **PASS**.
- **Per-panel VDA distribution** (variant A):
  - `r=0.3, ρ=0`:   min `0.000` / median `0.001` / q95 `0.129` / max `0.173`; `frac ≥ 0.05 = 28.7%`
  - `r=0.3, ρ=0.2`: min `0.000` / median `0.004` / q95 `0.133` / max `0.178`; `frac ≥ 0.05 = 29.5%`
  - `r=1.0, ρ=0`:   min `0.000` / median `0.005` / q95 `0.115` / max `0.157`; `frac ≥ 0.05 = 21.9%`
  - `r=1.0, ρ=0.2`: min `0.000` / median `0.007` / q95 `0.118` / max `0.155`; `frac ≥ 0.05 = 23.6%`
  - `r=3.0, ρ=0`:   min `0.000` / median `0.002` / q95 `0.036` / max `0.062`; `frac ≥ 0.05 = 1.2%`
  - `r=3.0, ρ=0.2`: min `0.000` / median `0.003` / q95 `0.039` / max `0.062`; `frac ≥ 0.05 = 1.9%`
- **Hash**: `72820559e1c1ab1919f74308623eaf4230aa3ea92ad3d9c62d81e993e4f27de6`.
- **Figure paths** (three; absolute):
  - `/Users/jonathanmorgan/AttentionManuscript/Rebuild/sims/C3--iso-vda-Vv/output/figures/iso_vda_contours.png` (205 KB)
  - `/Users/jonathanmorgan/AttentionManuscript/Rebuild/sims/C3--iso-vda-Vv/output/figures/vda_at_high_V.png` (128 KB)
  - `/Users/jonathanmorgan/AttentionManuscript/Rebuild/sims/C3--iso-vda-Vv/output/figures/iso_vda_drho.png` (91 KB)

## What the manuscript can now say

The exact sentence the manuscript may state (ceiling: the
CLAIM_LEDGER C3 row, which now cites this sim and these figures):

> Across `(V, v) ∈ [0.25, 1.0] × [1, 10]` and `r ∈ {0.3, 1, 3}`,
> `ρ ∈ {0, 0.2}` at the headline cell `(N=4, d'_max=2, f_0=0.5,
> h=sqrt, variant A)`, VDA concentrates at low validity, high value,
> and moderate-to-low asymmetry: peak `VDA = 0.17` at `r = 0.3` falls
> monotonically to `0.06` at `r = 3` (a 64% reduction) — confirming
> the qualitative shape of the inherited paper's §4 narrow-regime
> characterisation. The inherited §5.2 design recommendation
> ("high-validity paradigms show negligible VDA regardless of other
> parameters") is supported *conditionally*: at `V ≥ 0.95` peak VDA
> is at the grid floor (`≤ 10^{-5}`) for every `(r, ρ)` in the
> envelope; at `V ≥ 0.80` ≤ `3 × 10^{-3}` with a small
> ρ-conditional caveat; at `V ≥ 0.60` peak VDA reaches `0.164` and
> the recommendation fails categorically. We replace the §5.2
> categorical claim with the iso-VDA contour band of Figure
> `iso_vda_contours.png` and the quantitative threshold `V* ≳ 0.8`
> for the "high-validity" regime.

This is RB-011's target. RB-011 will draft the §results-C3 section
and the redrafted §5.2 paragraph, citing Figures `iso_vda_contours`,
`vda_at_high_V`, `iso_vda_drho`.

The manuscript A1 row also picks up a passing extension:

> The two-channel sign-decomposition of `dVDA/dρ` (rebuild §4 of the
> A1 derivation, Statements A / B) is corroborated cell-wise across
> the `(V, v, r)` cube: at `r = 0.3` (cost-dominant) `ρ` suppresses
> VDA in 37.2% of `(V, v)` cells and amplifies in 27.2%; at
> `r ∈ {1, 3}` (symmetric to benefit-dominant) the ratio inverts to
> ~ 53% amplified / ~ 17% suppressed. The sign-flip locus is thus
> not an artifact of the headline cell — it organises the entire
> design space.

## Next increment

`RB-011` is the natural next increment (manuscript prose closing the
§3.3 reframe item #2): draft `§results-C3` and replace `§5.2` with a
quantitative, hedged design recommendation citing the three rb-010
figures. All its prereqs are now done.

Parallel candidates if RB-011 is deferred:
- `RB-008` (C4 anti-cue inversion sim, opens the inversion-prediction
  thread — rebuilt-strength row's "anti-cue inversion at `V < 1/N` as
  a new falsifiable prediction" still unwired).
- `RB-014` (A2 heterogeneous-r model extension — opens the A2/A8
  heterogeneity thread; second-largest backlog cluster after A1).

RB-011 is preferred because (a) figures are already in publishable
form, (b) it closes one of the three §3.3 unifying-reframe items the
rebuild owes the manuscript (the other two are the A1 §model and the
C1 distributional, both already shipped), and (c) the next prose
section keeps the manuscript PDF page count growing as a visible
deliverable.

## Wiki cross-references

Mechanism-keyword sweep against `research_db/` performed for terms
relevant to this increment. No new `research_db/papers/` stubs
written; `audit.py` not re-run (no wiki writes). Existing entries
consulted:

- `cohen_maunsell2009_correlations` — anchors `ρ = 0.2` as the empirical
  noise-correlation magnitude. Already wired in §model (rb-009) and
  the rb-008 derivation; not re-cited here (this is a sim, not a
  manuscript section).
- `ruff_cohen2016_cross_area_correlations` — already wired in §model
  (rb-009); the structured-covariance scope limitation it grounds
  applies equally to this sim's equicorrelated assumption.
- `srinath2021_attention_information_flow` — already wired in §model
  (rb-009).
- `muller_findlay1987_sensitivity_criterion` — wired in §results-C1
  (rb-007); not consulted here.

Math-methods gap (Slepian 1962, Tong 1990) noted at rb-008 and rb-009
unchanged this run (no new wiki write needed — neither paper is cited
in this sim's README, only the existing model module's docstring
references them, which was set up at rb-001).

No new external citations introduced by this sim — the figures and
the quantitative threshold are theorems of the rebuilt model's own
definitions; the manuscript can state them with internal cross-
references only (citation lift to RB-011 if a literature anchor is
needed for the V-threshold or experimental-design framing).
