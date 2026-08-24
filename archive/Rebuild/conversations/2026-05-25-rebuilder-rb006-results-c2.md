---
type: conversation
agent: constructive-rebuilder
prompt_version: "0.2"
run_id: rb-006-2026-05-25
started: 2026-05-25T13:31:00Z
ended: 2026-05-25T13:55:00Z
worked_on: RB-010
output_kind: manuscript
claims_touched: [C2, A1]
artifacts_written:
  - Rebuild/manuscript/sections/results.tex (§Results header + §results-c2 body)
  - Rebuild/manuscript/figures/r_dagger_vs_v.png (copied from sim)
  - Rebuild/manuscript/figures/vda_curves_vfamily.png (copied from sim)
  - Rebuild/manuscript/main.pdf (regenerated; 7 pages / 542463 bytes)
  - Rebuild/CLAIM_LEDGER.md (C2 backing column + reconcile line)
  - Rebuild/REBUILD_BACKLOG.md (RB-010 in_progress → done)
  - Rebuild/rebuilder_state.json (runs_completed 5 → 6, done_task_ids +RB-010, manuscript_sections_drafted +"RB-010 (§results-C2)", +rb_006_manuscript_pdf_bytes)
  - Rebuild/BUILD_LOG.md (rb-006 entry)
papers_added: []
spawned_tasks: []
---

## What I built

The §results-C2 subsection of the rebuilt manuscript: the first
fully-prosed results subsection under `Rebuild/manuscript/`.

Concretely:

1. Rewrote `\section{Results}` from a one-paragraph stub to a
   substantive section-level introduction that names the four
   subsections (C1 distributional, C2 confident spine, C3 graded,
   C4 conditional theorem) and explains the "A1 reported alongside,
   not segregated" convention that operationalises the three-levers
   reframe (mission §3.3).
2. Replaced the §results-c2 stub with: (a) a claim-restatement
   paragraph pinning the rebuilt strength to the live verdict
   `CONFIRMED-UNDER-ATTACK`; (b) the numbered closed-form display
   `r†(v) = K_u(v) / [(N-1) · K_c(v)]` with $K_c$ and $K_u$
   companion equations derived from the first-order condition
   $\partial_\alpha R_\mathrm{P1}|_{\alpha=1/N} = 0$; (c) a
   $\val$-family numerics table with 6 rows
   ($\val \in \{1, 2, 3, 5, 8, 10\}$) reporting
   $\rdagger, c_c^\star, c_u^\star, K_c, K_u$; (d) a peak-vs-threshold
   consistency table showing $r^\star > \rdagger(\val)$ for every
   $\val$ in the family with the empirical gap reported; (e) an A1
   sensitivity table showing the $\val$-dependent sign-flip of
   $\partial \VDA^\star / \partial \corr$ (suppression at
   $\val \le 8$, amplification at $\val = 10$); (f) explicit
   scope-and-not-yet-claimed and reproducibility paragraphs.
3. Copied the two rb-004 figures
   (`vda_curves_vfamily.png`, `r_dagger_vs_v.png`) into
   `Rebuild/manuscript/figures/` and `\includegraphics`-ed them
   with full captions.
4. Compiled the manuscript: 3-pass `pdflatex` build, exit 0 on
   every pass, 7 pages / 542 463 bytes (up from 3 / 316 934 at
   rb-005), no undefined references after pass 2, only cosmetic
   `Overfull`/`Underfull` hbox and `hyperref` Unicode-in-bookmark
   warnings.

Total elapsed wall-clock for the run: ~24 minutes, well within the
mission §11 budget.

## How it connects to the ledger

- **C2 (CONFIRMED-UNDER-ATTACK, live).** The rebuilt strength
  ceiling in `CLAIM_LEDGER.md` reads "Confirmed, strengthened by
  reporting the closed-form escape threshold $\rdagger(\val) =
  K_u(\val) / [(\Nloc - 1) K_c(\val)]$ and its $\val$-family
  numerics" — exactly what the new prose now publishes. The
  subsection states the closed form as a numbered display equation
  in the body of the manuscript, lifts the $\val$-family table and
  the peak-vs-threshold table verbatim from
  `Rebuild/sims/C2--vda-vs-r-vfamily/output/results.json` (sha256
  `09ecef3c2c5a101820951398ed7d6e67d3398aede80c5f0bddfa42b6224fd783`),
  and reproduces both rb-004 figures. The C2 *strength* did not
  move; the C2 *backing* column was updated to point at the
  drafted section.
- **A1 (CONTESTED, live).** The §results-C2 subsection includes a
  paragraph and a dedicated table reporting the A1 sensitivity at
  the empirical peak ($\corr = 0.2$ vs $\corr = 0$), with the
  $\val$-dependent sign-flip of $\partial \VDA^\star /
  \partial \corr$ stated as an observation rather than a closed
  form. This honours the `CLAIM_LEDGER.md` A1 row — the
  $\rho$-channel sign-flip is reported as a *generalisation across
  the $\val$-family of the rb-002 fixed-cell finding*, not as a
  uniform statement. The closed-form $\rdagger(\val; \corr > 0)$
  that would predict the upward drift of $r^\star$ in $\corr$
  analytically is explicitly scoped out and pointed to RB-026 in
  the backlog.

No other claim's licensed strength changed.

## Simulation evidence

Every numerical claim in the new prose is traceable to
`Rebuild/sims/C2--vda-vs-r-vfamily/output/results.json` (rb-004):

| numerical claim in §results-C2 | source in results.json |
|---|---|
| $\rdagger(\val) = \{0.343, 0.168, 0.099, 0.050, 0.022, 0.016\}$ for $\val \in \{1, 2, 3, 5, 8, 10\}$ | `r_dagger_v1`, `r_dagger_family[*].r_dagger` |
| $c_c^\star, c_u^\star, K_c, K_u$ per-$\val$ entries in `tab:r-dagger-family` | `r_dagger_family[*]` |
| $r^\star$ peak locations $\{0.501, 0.376, 0.376, 0.376, 0.355\}$ | `peaks.rho=0.0__v=*.r_star` |
| $\VDA^\star$ peak magnitudes $\{0.012, 0.037, 0.083, 0.144, 0.183\}$ | `peaks.rho=0.0__v=*.VDA_star` |
| $\corr = 0.2$ A1-sensitivity peak shifts in `tab:rho-sensitivity` | `peaks.rho=0.2__v=*.*` |
| recovery $\max\|\Delta\VDA\| \le 4.87 \times 10^{-6}$ vs rb-002 | `recovery.pin_checks[*].d_VDA` |
| recovery $\max\|\Delta\CF\| \le 2.02 \times 10^{-6}$ vs rb-002 | `recovery.pin_checks[*].d_CF` |
| finer-grid argmax raises peak from $0.07986 / 0.3831$ to $0.08300 / 0.3758$ | `recovery.peak_obs` vs `recovery.peak_ref` |

Reproducibility: `python Rebuild/sims/C2--vda-vs-r-vfamily/run.py`
recomputes the entire results.json deterministically; the sha256
field at the top of the JSON is checked against the recorded value
in `rebuilder_state.json` (`rb_004_sim_digest`, unchanged this run).

Figures, both copied byte-for-byte into `manuscript/figures/`:
- `vda_curves_vfamily.png` (160 767 bytes, 2-panel
  $\corr \in \{0, 0.2\}$ family-of-curves with peak markers and
  $\rdagger(\val)$ dashed verticals)
- `r_dagger_vs_v.png` (50 950 bytes, continuous $\rdagger(\val)$
  trace with the family points highlighted and the
  $\rdagger(\val{=}1) \approx 0.343$ horizontal reference)

The PDF visually verifies both renders inline at the correct width
and includegraphics target.

## What the manuscript can now say

Verbatim, the §results-C2 subsection now licenses:

> *"At the C2 headline cell $(N, d'_\max, f_0, h, V) = (4, 2, 0.5,
> \sqrt{}, 0.5)$ under variant~A, the value-directed attention
> benefit $\mathrm{VDA}(r) = R_\mathrm{P1}(r) - R_\mathrm{P2}(r)$
> is non-monotonic in the benefit/cost ratio $r$. The
> non-monotonicity is a theorem of the model definitions: the
> closed form $r^\dagger(v) = K_u(v) / [(N-1) K_c(v)]$ predicts
> the $r$ at which P1 leaves the uniform allocation, with
> $r^\dagger(v)$ monotone-decreasing from
> $r^\dagger(2) \approx 0.17$ to
> $r^\dagger(10) \approx 0.02$. The empirical peak $r^\star =
> \arg\max_r \mathrm{VDA}(r)$ lies above $r^\dagger(v)$ for every
> $v \in \{2, 3, 5, 8, 10\}$ and clusters near $r^\dagger(v{=}1)
> \approx 0.343$. Peak $\mathrm{VDA}$ grows monotonically from
> $0.012$ at $v=2$ to $0.183$ at $v=10$. Promoting the A1
> independence assumption to $\rho = 0.2$ suppresses the peak at
> low $v$ ($\Delta \mathrm{VDA}^\star = -0.002$ at $v=2$,
> $-0.003$ at $v=5$) and amplifies it at $v=10$ ($+0.001$): the
> rb-002 $r$-axis sign-flip of $\partial \mathrm{VDA} /
> \partial \rho$ generalises to a $v$-axis sign-flip of
> $\partial \mathrm{VDA}^\star / \partial \rho$."*

It does **not** yet license: the variant-B replication of any of
the above (scoped to RB-027, §limitations); a closed-form
$r^\dagger(v; \rho > 0)$ (scoped to RB-026, §appendix); a
conservation-family band on the peak magnitudes (scoped to RB-019,
§limitations).

## Next increment

Per mission §4.1 (highest-priority unblocked task whose
prerequisites are satisfied), the next reasonable picks are:

1. **RB-009 — §results-C1 prose** (manuscript). Prereqs: RB-005
   (DONE). Structurally identical to the rb-006 increment with
   rb-003's three figures (`cf_histogram.png`, `cf_heatmap.png`,
   `cf_curves.png`) and the full Δ-distribution numerics
   (`max|ΔCF|=1.47e-6`, median CF=0.7552 / 0.7682, frac<0.6 = 0.07
   / 0.20 at $\rho=0$, etc.) ready to cite. **Default next pick:
   this.** Same one-prose-increment shape; locks in the second
   confident-spine result; sha256 `91fc4692...` already verified.
2. **RB-003 — A1 ρ-channel appendix derivation** (derivation).
   Prereqs: RB-001, RB-002 (both DONE). Independent re-derivation
   of $P_{\text{no-fa}}(\rho)$ via 1-D Gauss–Hermite quadrature
   plus the Slepian-monotonicity argument; unblocks RB-004 (the
   §model section that names the three levers reframe — the
   manuscript's narrative spine).
3. **RB-013 — §appendix-C5 prose** (manuscript). Prereqs: RB-001
   (DONE). Light-touch consistency-paragraph increment using the
   rb-001 recovery-test sha256 as evidence; smallest-scope option
   if a partial-budget run is anticipated.

The natural dependency order (model → simulation → derivation →
manuscript) favours **RB-003 over RB-009 only if** the owner wants
the §model section to land sooner; otherwise RB-009 finishes the
results-prose track for both confident-spine results before any
derivation increment.

No new tasks spawned this run.

## Wiki cross-references

Mission §11 sweep performed before declaring the section done.
Keywords swept against `research_db/papers/`, `concepts/`,
`threads/`:

| keyword group | hits | relevant to §results-C2? |
|---|---:|---|
| `non-monotonic VDA`, `escape threshold` | 0 | — |
| `value-directed attention`, `value attention` | scattered (Maunsell 2015, Posner 1980, Bays & Husain 2008, Bundesen 2005, Hawkins 1990, Muller & Findlay 1987, …) | broad SDT-attention substrate; none specifically about the cued-change-detection VDA paradigm modelled here |
| `equicorrelated Gaussian`, `Slepian` | 0 | — (the A1 channel's substrate; a Slepian 1962 seed entry already lives in `refs.bib`) |
| `criterion shift`, `criterion fraction` | 0 | — |
| `cued change detection` | 0 | — |

Conclusion: no new `research_db/papers/*.md` stub was written; no
existing wiki entry is cited in §results-C2. The result is a
theorem of the rebuilt model's own definitions and is supported by
internal cross-references only (the appendix derivation
RB-003/RB-026, the §model section RB-004, the conservation-family
caveat in §limitations). `audit.py` was not invoked (no `papers/`
change). The sweep is recorded here for the §11 audit trail.
