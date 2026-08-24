---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-019-2026-05-25
started: 2026-05-25T21:00:00Z
ended: 2026-05-25T21:15:00Z
worked_on: RB-014
output_kind: model
claims_touched: [A2, A3, A8]
artifacts_written:
  - Rebuild/model/core.py  (d_prime_hetero, canonical_alloc added; module docstring "Done so far" extended)
  - Rebuild/model/__init__.py  (re-exports d_prime_hetero, canonical_alloc)
  - Rebuild/model/tests/test_heterogeneous_r.py  (new; 5 checks, all PASS)
  - Rebuild/model/tests/heterogeneous_r_output.json  (sha256 0486921f8a4e253a1682ee0731e52c7de800bf6c3dbb1b5e8ff3200602454c7e)
  - Rebuild/model/README.md  (A2 axis added; "two axes" -> "three axes"; recovery digest block added; public-surface example extended)
  - Rebuild/CLAIM_LEDGER.md  (A2 row extended with rb-019 model wiring + recovery numbers)
  - Rebuild/REBUILD_BACKLOG.md  (RB-014 -> done; long-form notes with unblock list)
  - Rebuild/rebuilder_state.json  (runs_completed 18 -> 19; model_increments extended; heterogeneous_r_test_digest field added)
  - Rebuild/BUILD_LOG.md  (rb-019 entry prepended)
papers_added: []
spawned_tasks: []
---

# What I built

The **A2 heterogeneous-r d'-map** (`d_prime_hetero`) was wired into
the rebuilt model module `Rebuild/model/`. The single-`r` asymmetric
mapping (paper §2.4, `d_prime_asym`) becomes a per-location mapping:

$$ d'_i = \max\!\big( d_{\mathrm{base}} + s_i \, (d'_{\max} f(a_i) - d_{\mathrm{base}}),\; 0\big), $$

with $d_{\mathrm{base}} = d'_{\max} f(1/N)$ r-independent (paper Eq. 4)
and the per-slot gain/loss-branch criterion

$$ s_i = \beta(r_i, p)\quad\text{if } a_i \ge 1/N,\qquad
   s_i = \gamma(r_i, p)\quad\text{if } a_i < 1/N. $$

Two new public functions:

- `d_prime_hetero(alloc, r_vec, d_max, f0, h, N, p=1.0)` — returns
  a length-$N$ array of per-location $d'_i$ under a per-location
  ratio vector $r_i$. `r_vec` may also be a scalar (broadcast to a
  uniform vector). The conservation order $p$ propagates through
  `beta_gamma(r_i, p)` at each location, so the A2 extension composes
  cleanly with the rb-015 A3 conservation family.
- `canonical_alloc(alpha, N)` — convenience to build the canonical
  homogeneous allocation $(\alpha, (1-\alpha)/(N-1), \ldots, (1-\alpha)/(N-1))$,
  used by the recovery contract and as a starting point for A8
  N-dim sweeps (RB-017).

`d_prime_asym` is unchanged. The extension is purely additive: no
downstream pipeline call (`P_no_fa`, `optimal_R`, `policies`,
`vda_curve`, `slepian_curve`) is modified, and the pre-existing
recovery digests `d3c62215…` (A1, `test_recovery.py`) and
`f4f57a89…` (A3, `test_conservation_family.py`) are byte-identical
post-edit.

# How it connects to the ledger

This run discharges **RB-014** (A2 model extension) per
`Rebuild/REBUILD_BACKLOG.md`. It addresses the §3.2 A2 entry of the
mission prompt:

> "Benign under the *between-preparation* reading (one effective $r$
> per fixed preparation — what the $r$-sweep operationalises); false
> under the *within-display homogeneity* reading. Rebuild action:
> adopt the between-preparation reading *explicitly* in the model
> statement, and present heterogeneous per-location $r_i$ as a model
> *extension* with its own analysis."

The defensible strength on A2 — CONFIRMED-CONDITIONAL per the live
verdict `Critique/verdicts/A2--single-global-r.md` — is unchanged
after this increment. What changed is the model now *contains* the
heterogeneous-r mapping as a callable, validated primitive instead
of as a queued claim. Downstream §extensions-A2 manuscript prose
needs an empirical sim (RB-018) before it can claim *behavioural*
effects of heterogeneous $r$; this run lands only the model-wiring
substrate.

# Simulation evidence

`Rebuild/model/tests/test_heterogeneous_r.py` — **5/5 PASS**, sha256
`0486921f8a4e253a1682ee0731e52c7de800bf6c3dbb1b5e8ff3200602454c7e`.

| # | check | result |
| - | --- | --- |
| 1 | alpha ≥ 1/N grid recovery (5,436 cells: 151 α × 2 h × 3 p × 6 r) | binary, `max|diff| = 0.0` |
| 2 | alpha < 1/N inversion-regime grid recovery (468 cells: 13 α × 2 h × 3 p × 6 r) | binary, `max|diff| = 0.0` |
| 3 | scalar r_vec ≡ uniform N-vector (72 cells) | binary, `max|diff| = 0.0` |
| 4 | CR-048 / run-015 headline-cell spread=0 sanity ($V=0.5, v=5, r=0.398, \alpha=0.5$) | binary, `max|diff| = 0.0` |
| 5 | heterogeneous-r sign smoke (spread=0.3 around $r_{\mathrm{cued}}=0.398$, uncued ratios $\{0.7, 1.0, 1.3\}\,r_{\mathrm{cued}}$) | monotone-increasing $d'_{u,i}$ in $r_i$; cued unchanged |

The recovery contract (TESTs 1–4) is byte-for-byte against
`d_prime_asym` on the homogeneous-`r_vec` reduction. This is the
strongest possible recovery: no floating-point coercion, no operand-
order drift, no scipy/numpy backend dependence. TEST 5 confirms the
direction-of-effect of heterogeneous $r$ matches the closed-form
prediction from $\gamma(r) = 2/(r+1)$ being monotone-decreasing on
the loss branch.

**Cross-test sanity check.** Ran `test_recovery.py` (7/7 PASS, sha256
`d3c62215…`) and `test_conservation_family.py` (14/14 PASS, sha256
`f4f57a89…`) after the edit — pre-existing digests unchanged, so
this increment introduces **no behaviour change** in any existing
sim or policy call.

Reproducibility: deterministic test (no rng), byte-for-byte
re-runnable. The published `heterogeneous_r_output.json` sha256
`0486921f…` is the canonical pin.

# What the manuscript can now say

The §extensions-A2 subsection (queued under `sections/extensions.tex`;
extend the existing file that already hosts §extensions-A3) may now
state:

> *"The inherited paper governs the benefit/cost asymmetry by a single
> global ratio $r$ (assumption A2). The reviewer's verdict A2 (CONFIRMED-
> CONDITIONAL) decomposes this into a benign **between-preparation**
> reading — one effective $r$ per fixed preparation, which is what the
> published $r$-sweep operationalises — and an empirically false
> **within-display** reading (per Cohen-Maunsell-style fixed-feature
> heterogeneity, $R_2$). The rebuild adopts the between-preparation
> reading in the model statement and admits per-location $r_i$ as a
> model extension via the heterogeneous-$r$ d'-map (Eq.
> eq:d-prime-hetero) and its conservation-order composition through
> $(\beta, \gamma)(r_i, p)$. Under uniform $r_i = r$ and the canonical
> homogeneous allocation $(\alpha, (1-\alpha)/(N-1), \ldots)$, the
> heterogeneous-$r$ d'-map reduces to the inherited single-$r$ mapping
> byte-for-byte (Proposition A2-recovery: $\max|\Delta d'| = 0$ across
> $5{,}904$ $(\alpha, r, p, h)$ cells, sha256 `0486921f…`). A non-trivial
> $r$-vector produces a non-uniform $d'$-vector ordered as predicted
> from the $\gamma$ monotonicity (Lemma A2-sign-smoke, witnessed by the
> spread=0.3 cell)."*

It does **not** yet license:
- any *behavioural / empirical* claim about heterogeneous $r$ —
  requires RB-018 (the heterogeneous-r C2/C1 sweep simulation);
- statements about $\alpha^\star$ being a critical point or not under
  heterogeneous $r$ — needs RB-017 (A8 N-dim policy/optimiser
  extension) for the rebuilt pipeline to host that statement (the
  reviewer's CR-048 derivation already states the answer; the
  rebuild needs its own pipeline before it can re-state and re-verify);
- any allocation-deviation $\Delta R$ bound — needs RB-017 + RB-021
  (A8 N-dim sweep on the rebuilt pipeline).

# Next increment

**RB-017 — A8 N-dim policy/optimiser extension** is the natural
next pick by the §4.1 default selection rule:

- Highest-priority unblocked task (priority `medium`; the only other
  unblocked `medium` task is RB-018, which can run in parallel using
  the reviewer's substrate or wait for RB-017 to use the rebuilt
  pipeline).
- Natural continuation of the model→model thread: this run's
  `d_prime_hetero` returns an N-vector of $d'_i$, but `optimal_R`
  still consumes a scalar `(d_c, d_u)` pair under the implicit "all
  uncued share one $d'$" assumption (A8). RB-017 promotes
  `optimal_R` / `policies` to an N-group reward in the style of the
  reviewer's `optimal_ER_general` in
  `Critique/replications/A8--heterogeneous-uncued/run.py`. Recovery
  contract: at a homogeneous `r_vec` and the canonical alloc, the
  N-group policy must return the same `R_P1, R_P2, R_P3, R_P4, VDA,
  CF` as the current scalar `policies(r, cell)` to floating-point
  identity (probably to *binary* identity if the operand order is
  matched carefully).

Alternative immediate pick: **RB-018 — A2 heterogeneous-r sweep
simulation** is also unblocked. The minimal-viable sim — spread
sweep at the C2/C1 headline cells reproducing the reviewer's CR-048
numbers from the rebuilt model module — can be authored on top of
`d_prime_hetero` + the existing reviewer's `optimal_ER_general`
substrate (called transiently via path-imports as the rb-001 model
did during bootstrap). Choosing RB-018 first gives the manuscript a
§extensions-A2 empirical paragraph faster but defers the cleanest
single-source-of-truth for the heterogeneous policies; choosing
RB-017 first lands the substrate for a cleaner RB-018 + a future
RB-021 (A8 N-dim sweep).

Other unblocked alternatives (all priority `low`): RB-025 (A1
cell-wise sign-flip map), RB-026 (C2 closed-form $r^\dagger(v,\rho)$
derivation in the rebuild's voice), RB-024 (C1 closed-form CF<0.5
corner), RB-023 (A1 finer-ρ grid sensitivity),
RB-027/28/29/31/32 (variant-B / threshold-sharpening follow-up sims),
RB-033 (A3 formal derivation in the rebuild's voice).

# Wiki cross-references

Sweep keywords ran against `research_db/papers/`,
`research_db/concepts/`, and `research_db/threads/`:
`{heterogeneous attention, per-location asymmetry, between vs within
preparation, attention noise correlations, asymmetric scaling β γ,
within-display heterogeneity, location-specific gain}`. No relevant
existing entries returned by grep across the wiki. The heterogeneous-r
generalisation sits inside the rebuild's own model machinery; the
empirical within-display-heterogeneity citation needed for the
§extensions-A2 prose (Cohen-Maunsell R2 and follow-ups) is already
available via `cohen_maunsell_2009` in `Rebuild/manuscript/refs.bib`
(added at rb-009), and a dedicated R2-mechanism stub is deferred
until RB-018 lands its sim (parallel to the math-methods
deferral noted in rb-008 / rb-017). No new wiki writes; `audit.py`
not re-run.
