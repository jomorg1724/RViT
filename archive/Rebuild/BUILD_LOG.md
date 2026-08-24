# BUILD_LOG

Append-only, newest at top.

---

## rb-051 — 2026-05-31 — C1 closed-form CF<0.5 boundary derivation (derivation) — DONE

- **Run id:** `rb-051-2026-05-31`
- **Prompt version:** 0.2
- **Task worked:** RB-024 (low priority; the only C1 derivation thread still open per rb-050's "next priority" recommendation — replace the §results-C1 empirical `frac<0.6 = 22%` aggregate with a closed-form predicate the reader can compute pointwise).
- **Output kind:** derivation.
- **Claims touched:** C1 (defensible strength column extended with closed-form boundary characterisation; central-tendency narrative unchanged; variant-A "CF≥1/2 everywhere in the swept range" rb-003 observation is now promoted to a theorem of the model under variant A's CR scaling).
- **Status:** done.

### Headline thing built

Wrote [Rebuild/derivations/C1--cf-half-boundary.md](Rebuild/derivations/C1--cf-half-boundary.md) (41,802 bytes / ~30 KB / 9 sections + Verification + Extensions) plus companion verification script [Rebuild/derivations/verify_C1_cf_half/verify.py](Rebuild/derivations/verify_C1_cf_half/verify.py) (deterministic, `output.json` sha256 `b0b8ad5376e0b874982d97640639334112c6d1a396c1e6f8fd1e9ba09a61fe04`, ~1.4 s wall-clock).

Three pillars:

- **§2 Proposition 2.1 (G_crit is r-independent).** At α = 1/N, the sensitivity collapse $d'_c = d'_u = d'_{\mathrm{base}}$ from `Rebuild/derivations/C2--non-monotonic-vda-rho.md` Eq. 1.3 erases every r-dependence of the d-map. Both R(P3) and R(P4) depend on r only through this d'-pair, so $G_{\mathrm{crit}}(V, v) := R(\mathrm P_3) - R(\mathrm P_4)$ is a function of $(V, v, N, \mathrm{variant}, d'_{\max}, f_0, h, \rho)$ alone. Verified at **machine identity** $\max |\Delta G_{\mathrm{crit}}| = 0.000\mathrm{e}+00$ across all 4,410 rb-003 rows.

- **§3 algebraic reduction + §4 Theorem 4.3 (closed-form necessary condition).** Substituting into the CF identity $\mathrm{CF}(r, V, v) = G_{\mathrm{crit}}/(G_{\mathrm{att}} + G_{\mathrm{crit}})$ gives $\mathrm{CF} < 1/2 \iff G_{\mathrm{att}}(r; V, v) > G_{\mathrm{crit}}(V, v)$. Lemma 4.1 shows $\lim_{r\to\infty} \alpha^{\star}_{\mathrm P_1}(r) = 1$ (because $\gamma(r) \to 0$ removes the negative uncued contribution from the FOC). Proposition 4.2 + Theorem 4.3 prove $G_{\mathrm{att}}(r; V, v) \le G_{\mathrm{att}}^{\infty}(V, v) := R^{\infty}(V, v) - R(\mathrm P_3)$, evaluated at the closed-form asymptote $d_c^{\infty} = 2 d'_{\max} - d'_{\mathrm{base}} = 2.5$, $d_u^{\infty} = d'_{\mathrm{base}} = 1.5$ (standing parameters). Necessary condition: $G_{\mathrm{att}}^{\infty}(V, v) > G_{\mathrm{crit}}(V, v)$.

- **§5 Theorem 5.1 (closed-form sufficient condition).** The trivial $R(\mathrm P_1)(r) \ge R^{\star}(\alpha=1, r; V, v)$ gives $G_{\mathrm{att}}^{\alpha=1}(r; V, v) \le G_{\mathrm{att}}(r; V, v)$, so $G_{\mathrm{att}}^{\alpha=1}(r; V, v) > G_{\mathrm{crit}}(V, v) \Rightarrow \mathrm{CF}(r, V, v) < 1/2$. Monotone in r, gives a unique sufficient threshold $r_{\star}(V, v) \ge r_{1/2}(V, v)$, the closed-form upper bound on the true CF=1/2 boundary.

§6 specialises to variant B (CR = 1 removes the V, v coupling in the no-FA bracket; explains the rb-003 "high r × low V" corner geometry mechanistically). §7 is the four-contract numerical verification. §8 scopes what the appendix licenses vs does not.

### Cross-references discharged

The derivation is independent of `Critique/derivations/C1--*` (no analogue exists; the reviewer's verdict reports only empirical CF distributions, not a closed-form boundary characterisation). It reuses the C2 sensitivity-collapse machinery (Eq. 1.3 of `Rebuild/derivations/C2--non-monotonic-vda-rho.md`) but Propositions 2.1, 4.2, Lemma 4.1, Theorems 4.3, 5.1 are wholly new constructive results in the rebuild's voice.

### Simulation evidence

`output.json` sha256 `b0b8ad5376e0b874982d97640639334112c6d1a396c1e6f8fd1e9ba09a61fe04` (84,027 bytes, ~84 KB). Determinism verified by byte-identical re-run (same digest). The script consumes rb-003's `results.json` sha256 `91fc4692…` as the empirical reference, runs `optimal_R` and `floor_R` from `Rebuild/model/core.py` for the closed-form pieces, and reports four contracts:

| §7 contract | result | target |
|-------------|-------:|-------:|
| §7.2 Recovery (Proposition 2.1) | $\max\|\Delta G_{\mathrm{crit}}\| = 0.000\mathrm{e}+00$ across 4,410 rows | $\le 10^{-10}$ |
| §7.3 Necessary truth table (Theorem 4.3) | variant A 0/105 reachable, variant B 41/105 reachable, 5 small-margin mismatches | 0 false negatives (Theorem 4.3 contract) |
| §7.4 Sufficient envelope (Theorem 5.1) | 0 violations, soundness 1.000 within empirical range, coverage 0.9096 of empirical CF<0.5 cells | 0 violations |
| §7.5 Per-cell gap | median $r_{\star} - r_{1/2}^{\text{rb-003}} = 0.0000$; max $1.298$; 0 negative gaps | $\ge 0$ at every cell |

**Variant-A 0/105 finding.** The closed-form maximum margin $G_{\mathrm{att}}^{\infty} - G_{\mathrm{crit}}$ across the 105 variant-A cells is $-0.0034$ (strictly negative). By Theorem 4.3, $\mathrm{CF}(r, V, v) \ge 1/2$ for **all** $r$ in variant A — promoting the rb-003 empirical "variant A min $\mathrm{CF} = 0.5587 > 0.5$" observation to a *theorem of the model* under variant A's $\mathrm{CR}(V, v) = V v + (1-V)$ scaling.

**Variant-B 5 mismatches.** All have small positive margins $G_{\mathrm{att}}^{\infty} - G_{\mathrm{crit}} \in [+0.0005, +0.0122]$ at $(V, v) \in \{(0.4375, 5), (0.7375, 2), (0.6625, 3), (0.5500, 4), (0.4000, 5)\}$ with rb-003 $\min_r \mathrm{CF} \in [0.514, 0.541]$ — exactly cells where Theorem 4.3 predicts $r_{1/2}(V, v) > 10$. The extended-grid sufficient threshold $r_{\star}$ confirms this: four cells fire at $r = 30$ in the extended grid; the smallest-margin one ($V = 0.4375$, margin $+0.0005$) has $r_{\star} > 100$. Not theorem failures — grid-edge cases consistent with the closed-form "predicted reachable but at $r > 10$" reading.

**Sufficient-condition tightness.** Median per-cell gap $r_{\star} - r_{1/2}^{\text{rb-003}} = 0.0000$ means the closed-form $\alpha = 1$ specialisation captures the same r-grid index as the unconstrained $\mathrm P_1$ optimum on the median cell — the bound is bit-tight on more than half of the empirical CF<1/2 region. The 16/177 empirical CF<1/2 cells not captured by the sufficient predicate are at moderate r between $r^{\dagger}(v)$ and the asymptote, where the unconstrained P1 has $\alpha^{\star} < 1$ and $G_{\mathrm{att}} > G_{\mathrm{att}}^{\alpha=1}$ strictly.

### Wiki cross-references

Sweep performed; keywords {criterion fraction, sensitivity collapse, value-weighted reward, asymmetric P3 criterion, equicorrelated no-FA, attention reallocation upper bound, gain-branch d'-map, monotone-bounded attention gain}. Every cited reference already wired (Slepian1962 from rb-008; MullerFindlay1987 from rb-007; CohenMaunsell2009 / RuffCohen2016 / Srinath2021 from rb-009/rb-011); 0 new wiki stubs; `audit.py` not re-run (no wiki writes).

### What the manuscript can now say

The §results-c1 manuscript section may now state (when the RB-056 fold-in lands):

> *"Across the 4,410-cell sweep, the variant-A criterion fraction satisfies $\mathrm{CF}(r, V, v) \ge 1/2$ at every $r > 0$ — a closed-form prediction of the rebuilt model under variant A's $\mathrm{CR}(V, v) = V v + (1-V)$ scaling (Theorem 4.3 of `Rebuild/derivations/C1--cf-half-boundary.md`). The rb-003 empirical min $\mathrm{CF} = 0.5587$ is the closest variant-A cell to the boundary; the closed-form max margin $G_{\mathrm{att}}^{\infty} - G_{\mathrm{crit}}$ across all 105 variant-A cells is $-0.0034$, strictly negative."*
>
> *"In variant B, the CF<1/2 region is exactly $\{(r, V, v) : G_{\mathrm{att}}^{\infty}(V, v) > G_{\mathrm{crit}}(V, v) \text{ and } r > r_{1/2}(V, v)\}$ where $G_{\mathrm{crit}}, G_{\mathrm{att}}^{\infty}$ are closed-form scalars in $(V, v)$ and $r_{1/2}$ is the implicit boundary defined by $G_{\mathrm{att}}(r; V, v) = G_{\mathrm{crit}}(V, v)$. The closed-form sufficient threshold $r_{\star}(V, v)$ (computable as the 1-D root-find on $G_{\mathrm{att}}^{\alpha=1}(r; V, v) - G_{\mathrm{crit}}(V, v)$) lies above $r_{1/2}$ and is bit-tight on the median empirical CF<1/2 cell."*

These are theorem statements, not aggregate frequencies — the manuscript may replace the empirical `frac<0.6 = 22%` aggregate with closed-form predicates the reader can compute pointwise from the model primitives.

### Why the next run should care

C1 now has a closed-form derivation appendix matching the C2 / A1 / A3 / C4 closed-form derivations the rebuild has previously delivered. The §appendix-deriv-c1 manuscript fold-in (RB-056) is the natural rb-024-style follow-up: it would promote the rb-051 derivation file into a self-contained appendix subsection mirroring §appendix-deriv-c2's structure (rb-023 derivation → rb-024 §appendix-deriv-c2 fold-in pattern), and rewrite the §results-c1 retraction paragraph to cite the new appendix subsection inline. After RB-056, all five headline claims (C1–C5) have appendix-derivation subsections; the only remaining derivation gaps are the low-priority sharpening passes (RB-040 Slepian-gradient analytic locus; RB-053 A3 conservation-family band on Theorem 4.3; RB-054 finer r-grid extension; RB-055 large-r 1/r expansion of $r_{\star}$).

### Next increment

Natural high-yield candidates:

- **RB-056** (manuscript fold-in of rb-051 → §appendix-deriv-c1 + §results-c1 retraction-paragraph rewrite) — the natural rb-024-style follow-up; mirrors §appendix-deriv-c2's structure and would discharge the only C1-related appendix gap.
- **RB-029** (A1 dormant-cell amplification follow-up sim) — the most striking single qualitative finding of rb-010 generalised across the sweep; would give §model-upper-bound an additional falsifiable behavioural prediction.
- **RB-040** (Slepian-gradient analytic locus for the cell-wise $\partial \mathrm{VDA} / \partial \rho$ surface) — would close A1 manuscript-side architecturally, paralleling the A3 closure rb-046 already discharged.

RB-056 is the natural next match by the "finish what is wired" rhythm — the same pattern that produced rb-024 from rb-023 and rb-046 from rb-033.

### Files written

- `Rebuild/derivations/C1--cf-half-boundary.md` — the new derivation (41,802 bytes, ~30 KB, 9 sections + Verification + Extensions).
- `Rebuild/derivations/verify_C1_cf_half/verify.py` — companion verification script.
- `Rebuild/derivations/verify_C1_cf_half/output.json` — verification output (84,027 bytes; sha256 `b0b8ad5376e0b874982d97640639334112c6d1a396c1e6f8fd1e9ba09a61fe04`; deterministic across re-runs).
- `Rebuild/CLAIM_LEDGER.md` — top reconcile paragraph rewritten for rb-051 (previous rb-050 paragraph rolled into the "Previous reconcile" position); C1 row backing column extended with the new derivation + verification.
- `Rebuild/REBUILD_BACKLOG.md` — RB-024 status flipped queued → done with full notes; RB-056 added as spawned-by-rb-051 (manuscript fold-in follow-up).
- `Rebuild/rebuilder_state.json` — atomically rewritten (tempfile + rename); `runs_completed` → 35, `last_run_id` / `last_run_ended` updated, `done_task_ids` adds RB-024, `open_task_ids` removes RB-024 and adds RB-056, `derivations_written` extends with `RB-024`, `next_task_id_counter` → 57, `rb_024_derivation_bytes` = 41802, `rb_024_verification_bytes` = 84027, `rb_024_verification_digest` = `b0b8ad5376e0b874982d97640639334112c6d1a396c1e6f8fd1e9ba09a61fe04`.
- `Rebuild/BUILD_LOG.md` — this entry, header written before execution as a crash-recoverable in_progress marker, then body filled at end of run with `done` status.
- `Rebuild/conversations/2026-05-31-rebuilder-c1-cf-half-derivation.md` (NEW).

No manuscript edits; no new sims (the derivation is backed by the existing rb-003 sim + the new deterministic verify_C1_cf_half/verify.py); no new bib entries; no new wiki stubs; `audit.py` not re-run.

---

## rb-050 — 2026-05-31 — §methods bookend manuscript (manuscript) — DONE

- **Run id:** `rb-050-2026-05-31`
- **Prompt version:** 0.2
- **Task worked:** RB-050 (medium priority; new task spawned by rb-049's "next priority" recommendation — replace the rb-005 stub in `sections/methods.tex` with the fourth and final bookend, completing the structural arc abstract → intro → model → results → extensions → limitations → methods → appendix).
- **Output kind:** manuscript.
- **Claims touched:** cross-cutting (the methods bookend catalogues the infrastructure under `Rebuild/` that already backs every claim in the body sections — no claim's rebuilt strength changes).
- **Status:** done.

### Headline thing built

Replaced the rb-005 stub in [Rebuild/manuscript/sections/methods.tex](Rebuild/manuscript/sections/methods.tex) (34 lines, ~70% placeholder) with a 5-subsection methods bookend (~250 LaTeX lines, ~1,700 words). Catalogues the rebuild's simulation infrastructure paralleling the original paper's §3 methods. The section is organised by infrastructure tier rather than by claim so a reader can locate the precise file under `Rebuild/` that backs any quantitative statement in the manuscript.

Five subsections:

- **§8.1 The validated reference implementation** — `Rebuild/model/core.py` starts as a copy of the validated P1–P4 optimiser from `Critique/replications/C5--symmetric-recovery/`, so the inherited model's headline numbers appear at byte-exact backwards compatibility under inherited defaults by construction. Extends along four orthogonal axes each gated by a recovery test: A1 ($\corr$ channel via one-factor Gauss-Hermite reduction with $n_q = 64$, FP-identity recovery at $\corr = 0$); A3 (power-mean conservation family with closed-form weights, byte-exact recovery at $p = 1$); A2 (per-location $\Rsens_i$ via `eq:d-prime-hetero`, byte-exact recovery under uniform $\Rsens_i$); A8 (full $\Nloc$-dim allocation simplex via the $\corr$-aware grouped-criterion optimiser, $10^{-9}$ ULP recovery — six orders of magnitude past the four-decimal-place sensitivity of every headline number). Closes with the joint recovery statement: with $\corr = 0$, $p = 1$, uniform $\Rsens_i$, and the canonical homogeneous allocation, the rebuilt optimiser reproduces every inherited number in the $4{,}410$-cell sweep at FP identity.

- **§8.2 Recovery contracts** — Table `tab:methods-recovery` with all four sha256 digests verbatim from `rebuilder_state.json`: `test_recovery.py` (A1, $\corr \to 0$) `d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f`; `test_conservation_family.py` (A3, $p \to 1$) `f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e`; `test_heterogeneous_r.py` (A2, uniform $\Rsens_i$) `0486921f8a4e253a1682ee0731e52c7de800bf6c3dbb1b5e8ff3200602454c7e`; `test_general_policy.py` (A8, homogeneous uncued) `883ea15af9fd069e04c05ff156d65f33a7d25278891092539c6441d2248c3d39`. Notes that the four digests appear verbatim in `rebuilder_state.json` and that any model-code change altering a digest is a recovery violation.

- **§8.3 Simulation protocol** — five-point discipline (seeded grids; recovery test before sweep; canonical sort-keys/indent-2 JSON output with sha256 over content excluding wall-clock; captioned figures; backlog cross-reference) + Table `tab:methods-sims-summary` listing all nine wired sims with their output digest prefixes and manuscript cross-references: A1--rho-channel `b692c064…` (sec:model-rho-channel + 3 figs); C1--cf-distribution `91fc4692…` (sec:results-c1 + tab:cf-distribution + 3 figs); C2--vda-vs-r-vfamily `09ecef3c…` (sec:results-c2 + eq:r-dagger + 2 figs); C3--iso-vda-Vv `72820559…` (sec:results-c3 + tab:c3-highV-probe + 2 figs); C4--anti-cue-inversion `6ad651d6…` (sec:results-c4 + eq:value-weight + tab:c4-anticue + 2 figs); A1--vda-signflip-cellwise `489c7c25…` (sec:model-upper-bound + tab:a1cw-summary + 3 figs); A2--heterogeneous-r `22b183f9…` (sec:extensions-a2 + tab:a2-rb021-summary + 2 figs); A3--conservation-band `055bf4ec…` (sec:extensions-a3 + thm:delta-cf-monotone + 2 tabs + 2 figs); A8--nd-uncued-sweep `beb2aa87…` (sec:extensions-a8 + tab:a8-rb027-summary + 2 figs).

- **§8.4 Derivations** — four derivations under `Rebuild/derivations/`: A1 $\corr$-channel (rb-008 → sec:appendix-deriv-a1; Slepian monotonicity, two-channel sign decomposition of $\partial \VDA/\partial \corr$ backing the sec:model-upper-bound retraction); C2 $\rdagger(\val)$ + $\corr > 0$ extension (rb-014 → sec:appendix-deriv-c2 via `eq:c2-Kc-rho` / `eq:c2-Ku-rho` → `prop:r-dagger-rho`); C4 anti-cue inversion (rb-026 → conditional theorem at `eq:value-weight` + closed-form inversion threshold `eq:r-inv`); A3 power-mean (rb-029 → sec:appendix-deriv-a3 with the closed KL-divergence form of HLP monotonicity `eq:a3d-hlp-kl`, full proof of `prop:r-dagger-invariance`, and C5 conservation-form-invariance `cor:a3d-c5-invariance`; finite-difference verification at 7 test pairs to $\le 1.5\times10^{-10}$). Each derivation independently authored from the skeptical reviewer's attack derivations.

- **§8.5 Reproducibility and the rebuild contract** — three-artifact rule (recovery contract + deterministic sim digest + (for novel propositions) derivation); the simulate-first-write-second operating mode as what licenses the manuscript's distributional/graded/conditional voice with the cross-reference to `sec:limitations-not-claimed`; software dependencies listed (NumPy, SciPy with `erf` fallback, Matplotlib; pdflatex/bibtex + AMS-LaTeX); $\sim$10–20 min per-run wall-clock budget with larger sweeps decomposed into multiple runs via the backlog; the full reproducibility ledger maintained in `rebuilder_state.json` + `BUILD_LOG.md` + `CLAIM_LEDGER.md` so a reader can verify any quantitative statement by locating the claim in `CLAIM_LEDGER.md`, following the pointer, and re-running.

### Cross-references discharged

~50 labels — all verified extant before compile via `grep -hE "\\\\label\{(sec|prop|thm|cor|def|eq|tab|fig):" sections/*.tex` (snapshot taken before drafting). 11 section labels (sec:model-inherited, sec:model-rho-channel, sec:model-upper-bound, sec:appendix-deriv-a1, sec:appendix-deriv-a3, sec:appendix-deriv-c2, sec:appendix-c5, sec:extensions-a2, sec:extensions-a3, sec:extensions-a8, sec:results-c1, sec:results-c2, sec:results-c3, sec:results-c4, sec:limitations-not-claimed). 11 equation refs (eq:pnofa-indep, eq:pnofa-rho, eq:rho-zero-recovery, eq:conservation-family, eq:beta-gamma-of-p, eq:d-prime-hetero, eq:r-dagger, eq:value-weight, eq:c2-Kc-rho, eq:c2-Ku-rho, eq:r-inv, eq:a3d-hlp-kl). 4 prop/cor/thm refs (prop:r-dagger-rho, prop:r-dagger-invariance, cor:a3d-c5-invariance, thm:delta-cf-monotone). 1 definition ref (def:three-levers). 11 figure refs (fig:vda-rho-variantA, fig:vda-rho-variantB, fig:cf-vs-rho, fig:cf-histogram, fig:cf-heatmap, fig:cf-curves, fig:vda-curves-vfamily, fig:r-dagger-vs-v, fig:iso-vda-contours, fig:vda-at-high-V, fig:c4-alpha-star-map, fig:c4-rinv-closed-form, fig:a1cw-sign-heatmap-v5, fig:a1cw-signflip-by-r, fig:a1cw-delta-distribution, fig:a2-vda-peak-band, fig:a2-vda-curves-spread, fig:a3-vda-peak-band, fig:a3-delta-cf-distribution, fig:a8-simplex-dr, fig:a8-anticued-suppression). 7 table refs (tab:methods-recovery, tab:methods-sims-summary, tab:cf-distribution, tab:c3-highV-probe, tab:c4-anticue, tab:a1cw-summary, tab:a2-rb021-summary, tab:a3-c1-cf-band, tab:a3-c2-peak-band, tab:a8-rb027-summary). 1 citation (Slepian1962, already wired from rb-008). **One mid-build correction**: first draft used `\citep{Slepian1962}` (natbib) but the manuscript loads no natbib — pass 1 fatal `! Undefined control sequence l.323 \citep`; fixed inline to `\cite{}` before pass 2. Same fix as rb-049.

### Build

4-pass pdflatex+bibtex:

- pass 1 (first attempt) — pdflatex exit 1 with one fatal `! Undefined control sequence l.323 \citep` error. Fixed inline to `\cite{}` and re-ran.
- pass 1 (after `\cite` fix) — pdflatex exit 0; 63 pages / 2,853,842 bytes; ~60 forward-reference warnings on new labels (normal pass-1 behaviour for new labels).
- bibtex — exit 0, 0 warnings, no new entries (Slepian1962 already wired from rb-008).
- pass 2 — pdflatex exit 0; 63 pages / 2,860,922 bytes; all forward references resolved.
- pass 3 — pdflatex exit 0; 63 pages / 2,860,922 bytes; byte-identical to pass 2.
- pass 4 — pdflatex exit 0; 63 pages / 2,860,922 bytes; byte-identical to pass 3, settled, 0 undefined references, 0 non-hyperref warnings. The hyperref Unicode-in-PDF-string warnings on TOC bookmarks are pre-existing cosmetic warnings about Greek letters / math in subsection headers, not new and not semantic.

vs rb-049 baseline 2,815,939 bytes / 59 pages → **+4 pages, +44,983 bytes**. The largest bookend yet because both Table tab:methods-recovery and Table tab:methods-sims-summary are full-width tabular blocks that the abstract / intro / limitations bookends did not contain.

### Wiki cross-references

Sweep performed; keywords {validated reference implementation, recovery contract, simulation protocol, deterministic digest, sha256 fingerprint, canonical JSON output, reproducibility, equicorrelated Gaussian, one-factor Gauss-Hermite reduction, power-mean conservation family, HLP monotonicity, simulate-first-write-second, rebuild contract}. Every cited reference already wired (Slepian1962 from rb-008); no novel literature citations introduced in this bookend. 0 new wiki stubs; `audit.py` not re-run (no wiki writes).

### What the manuscript can now say

The rebuilt paper now has **all four bookends drafted (abstract + intro + limitations + methods) and the manuscript is structurally complete for the first time**: abstract → intro → model → results × 4 → extensions × 3 → limitations → **methods** → appendix × 3 — 63 pages, **zero skeleton stubs remaining**. Every section file is a self-contained, citation-resolved, recovery-pinned rebuild artefact. The §methods bookend is the canonical place a reader looks to verify any quantitative statement, providing the full sha256 ledger that pins each claim to its reproducible artifact.

### Why the next run should care

With the structural arc closed, the rebuild moves into the sharpening phase: every queued task now tightens an existing result rather than adding a structural section. The 14 low-priority queued tasks all map to specific §limitations §7.5 "queued follow-ups" entries: RB-024 closed-form $\CF < 0.5$ boundary derivation; RB-029 dormant-cell amplification closeup; RB-040 Slepian-gradient analytic locus; RB-039 finer $\corr$-grid for $\rdagger(\val; \corr)$; RB-023/RB-027/RB-031/RB-036/RB-043 variant-B re-evaluations; RB-028/RB-032/RB-044 grid-sharpening; RB-037 multiplicative A2 spread; RB-045 d_prime_hetero hardening. Any future referee request for a tighter threshold maps directly onto an identified backlog item that is also named in the manuscript's §7.5.

### Next increment

The natural next moves are all sharpening passes (no structural section remaining). High-yield candidates:

- **RB-024** (closed-form $\CF < 0.5$ boundary derivation) — the only C1 derivation thread still open; would let §results-C1 replace `frac<0.6 = 22%` with a closed-form predicate.
- **RB-029** (A1 dormant-cell amplification follow-up sim) — most striking single qualitative finding of rb-010; would give §model-upper-bound an additional falsifiable behavioural prediction.
- **RB-040** (Slepian-gradient analytic locus for the cell-wise $\partial \VDA / \partial \corr$ surface) — would close A1 manuscript-side architecturally, paralleling the A3 closure rb-046 already discharged.
- **RB-039** (finer $\corr$-grid for $\rdagger(\val; \corr)$) — would tighten Table tab:r-dagger-rho-drift toward a smooth curve.

RB-024 is the natural next match by "discharge what is wired but not yet derived" rhythm. The bookends are done; the rebuild's structural commitments are stated; everything remaining is precision.

### Files written

- `Rebuild/manuscript/sections/methods.tex` — the rb-005 stub (34 lines) replaced by a self-contained 5-subsection §methods bookend (~250 LaTeX lines).
- `Rebuild/manuscript/main.pdf` — rebuilt 63 pages / 2,860,922 bytes (was 59 pages / 2,815,939 at rb-049).
- `Rebuild/CLAIM_LEDGER.md` — top reconcile paragraph rewritten for rb-050 (previous rb-049 paragraph rolled into the "Previous reconcile" position).
- `Rebuild/REBUILD_BACKLOG.md` — RB-050 added at the top of the recent-tasks block, status `done` with full notes.
- `Rebuild/rebuilder_state.json` — atomically rewritten (tempfile + rename); `runs_completed` → 34, `last_run_id` / `last_run_ended` updated, `done_task_ids` adds RB-050, `manuscript_sections_drafted` extended, `next_task_id_counter` → 51, `rb_050_manuscript_pdf_bytes` = 2860922 added.
- `Rebuild/BUILD_LOG.md` — this entry, header written before the section file as a crash-recoverable in_progress marker, then body filled at end of run.
- `Rebuild/conversations/2026-05-31-rebuilder-methods-bookend.md` (NEW).

No model edits; no new sims; no new bib entries; no new wiki stubs; `audit.py` not re-run.

---

---

## rb-049 — 2026-05-30 — §intro bookend manuscript (manuscript) — DONE

- **Run id:** `rb-049-2026-05-30`
- **Prompt version:** 0.2
- **Task worked:** RB-049 (medium priority; new task spawned by rb-048's "next priority" recommendation — replace the rb-005 stub in `sections/intro.tex` with the third bookend, mirroring the abstract's and limitations' voice).
- **Output kind:** manuscript.
- **Claims touched:** cross-cutting (the intro previews every claim already wired in the body — no claim's rebuilt strength changes; the §3.3 unifying reframe is articulated up-front).
- **Status:** done.

### Headline thing built

Replaced the rb-005 stub in [Rebuild/manuscript/sections/intro.tex](Rebuild/manuscript/sections/intro.tex) (34 lines, ~60% placeholder + a 13-line scoping paragraph from the bootstrap) with a 6-paragraph self-contained introduction (~165 LaTeX lines, ~1,100 words) at the §3.3 unifying-reframe voice. The intro articulates the corrective voice up-front, introduces the missing third lever, previews the four C-row headline results at CLAIM_LEDGER-licensed strength, previews the three extensions and the A6 deferral, and outlines the manuscript layout.

Six paragraphs:

- **¶1 The original question** — cued change-detection with value $\val \ge 1$ and validity $\valid \in [1/\Nloc, 1]$; names the three available levers (criterion, sensitivity, decorrelation) at the top without yet committing to a count; restates the inherited paper's normative question verbatim in spirit; closes with the rebuilt-voice clause "what changes is the mathematical description used to answer it."
- **¶2 The §3.3 unifying reframe at intro voice** — the inherited paper's recurring overstatement quoted with numbers ($\CF$ $[0.60, 0.96]$ → $[0.30, 1.00]$ median $0.76$, $\sim 13\%$ tail below 0.60; "negligible regardless of other parameters" at $\valid \ge 0.95$ but not $\valid \approx 0.80$ once $\corr$ is admitted; "no inversion" true cued but not anti-cue $\valid < 1/\Nloc$; A1 "upper bound on VDA" sign-ambiguous — suppresses cost-dominant and amplifies benefit-dominant); pivot to the corrective voice (distributional, graded, or conditional by default).
- **¶3 The missing third lever** — cites `CohenMaunsell2009`, `RuffCohen2016`, `Srinath2021` for the empirically dominant decorrelation channel; promotes $\corr$ to a first-class parameter via the one-factor Gauss–Hermite reduction (`eq:pnofa-rho`); $\corr \to 0$ FP-identity recovery (`eq:rho-zero-recovery`); three-lever Defn `def:three-levers`; A1 §model-upper-bound retraction with the cell-wise crossover at $\Rsens \approx 0.79$ across the 4,410-cell sweep (`sec:model-upper-bound`, `tab:a1cw-summary`).
- **¶4 The four C-row headline results at CLAIM_LEDGER-licensed strength** — C1 distributional median $0.76$ at `sec:results-c1` / `tab:cf-distribution`; C2 closed-form $\rdagger(\val) = K_u/[(\Nloc-1)K_c]$ (`eq:r-dagger`) with $\corr > 0$ extension (`sec:appendix-deriv-c2`, `prop:r-dagger-rho`) and conservation-form invariance (`prop:r-dagger-invariance`); C3 graded contour band (`sec:results-c3`, `tab:c3-highV-probe`) with hierarchical $\valid$ thresholds ($\valid \ge 0.95$ at grid floor under any $(\Rsens, \corr)$ / $\valid \ge 0.80$ only at $\corr = 0$ / $\valid \ge 0.60$ fails); C4 conditional theorem `eq:value-weight` + anti-cue inversion as new falsifiable prediction with $36.1\%$ incidence at $\Nloc = 4$ (`sec:results-c4`, `tab:c4-anticue`); C5 universal real-number identity (`sec:appendix-c5`, `prop:c5-realnumber`) conservation-form-invariant by construction (`cor:a3d-c5-invariance`).
- **¶5 The three extension levers + A6 deferral** — A2 bounded heterogeneity (`sec:extensions-a2`, `tab:a2-rb021-summary`); A3 power-mean conservation family with `eq:conservation-family` / `eq:beta-gamma-of-p` and `thm:delta-cf-monotone` (`sec:extensions-a3`); A8 N-dim policy with new conditional binding at multiplicative conservation and $32\%$ $\corr$-amplification at the focal cell (`sec:extensions-a8`); A6 decision-noise deferral (`sec:limitations-a6`) explicitly held at WEAKLY-SUPPORTED.
- **¶6 Layout and closing voice clause** — model → results → extensions → limitations → appendix; every quantitative claim in the body backed by a sim under `Rebuild/sims/` with a recovered limit, deterministic output hash, and captioned figure; every novel proposition derived under `Rebuild/derivations/`; nothing more strongly stated than its row of `CLAIM_LEDGER.md` licenses.

### Cross-references discharged

25 labels — all verified extant before compile via `grep -hE "\\\\label\{(sec|prop|thm|cor|def|eq|tab|fig):" sections/*.tex` (snapshot taken before drafting). Sections: `sec:model`, `sec:model-upper-bound`, `sec:results`, `sec:results-c1`, `sec:results-c2`, `sec:results-c3`, `sec:results-c4`, `sec:appendix-deriv-a1`, `sec:appendix-deriv-c2`, `sec:appendix-c5`, `sec:extensions`, `sec:extensions-a2`, `sec:extensions-a3`, `sec:extensions-a8`, `sec:limitations`, `sec:limitations-a6`. Equations: `eq:pnofa-rho`, `eq:rho-zero-recovery`, `eq:r-dagger`, `eq:value-weight`, `eq:conservation-family`, `eq:beta-gamma-of-p`. Definitions/Propositions/Theorems/Corollaries: `def:three-levers`, `prop:r-dagger-rho`, `prop:r-dagger-invariance`, `prop:c5-realnumber`, `cor:a3d-c5-invariance`, `thm:delta-cf-monotone`. Tables: `tab:a1cw-summary`, `tab:cf-distribution`, `tab:c3-highV-probe`, `tab:c4-anticue`, `tab:a2-rb021-summary`. Citations: `CohenMaunsell2009`, `RuffCohen2016`, `Srinath2021` — all already wired from rb-009/rb-011/rb-024; **one mid-build correction**: first draft used the lowercase variant `cohen_maunsell2009_correlations` / `ruff_cohen2016_cross_area_correlations` / `srinath2021_attention_information_flow` (the `research_db/papers/` stub-name convention), but the canonical bib keys in `refs.bib` are CamelCase; fixed inline before pass 2.

### Build

4-pass pdflatex+bibtex:

- pass 1 (first attempt) — pdflatex exit 1 with one fatal `! Undefined control sequence l.70 \citep` error; the manuscript loads no `natbib`, so `\citep{}` is not defined. Fixed inline to `\cite{}` and re-ran.
- pass 1 (after `\cite` fix) — pdflatex exit 0; 59 pages / 2,815,939 bytes; one `LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.` (normal pass-1 behaviour for new labels).
- bibtex — exit 0, 0 warnings, no new entries (the three citations `CohenMaunsell2009`, `RuffCohen2016`, `Srinath2021` are already in `refs.bib`).
- pass 2 — pdflatex exit 0; 59 pages / 2,815,939 bytes; resolved the label-change warning.
- pass 3 — pdflatex exit 0; 59 pages / 2,815,939 bytes; byte-identical to pass 2.
- pass 4 — pdflatex exit 0; 59 pages / 2,815,939 bytes; byte-identical to pass 3, settled, 0 undefined references, 0 new warnings. The hyperref Unicode-in-PDF-string warnings on TOC bookmarks are pre-existing cosmetic warnings, not new and not semantic.

vs rb-048 baseline 2,807,597 bytes / 58 pages → **+1 page, +8,342 bytes**.

### Wiki cross-references

Sweep performed; keywords {value-directed attention, criterion fraction, decorrelation lever, three-lever decomposition, anti-cue inversion, conservation family, equicorrelated Gaussian, escape threshold, narrow regime, central tendency, distributional vs categorical claim, symmetric recovery, missing-lever framing}. Every paper the intro cites was already wired through body sections — no novel literature citations introduced in this bookend. 0 new wiki stubs; `audit.py` not re-run (no wiki writes).

### What the manuscript can now say

The rebuilt paper now has **all three drafted bookends** (abstract → intro → limitations) for the first time: abstract → **intro** → model → results × 4 → extensions × 3 → limitations → methods stub → appendix × 3 — 59 pages, one skeleton stub remaining (methods). The §3.3 unifying-reframe voice is now stated both up-front (intro ¶2) and at the end (§limitations §7.6); the corrective voice is the manuscript's narrative spine rather than an implicit pattern across body sections.

### Why the next run should care

The §methods bookend (the rb-005 stub at `sections/methods.tex`, 33 lines, ~70% placeholder) is the only remaining structural increment. With the abstract → intro → body → limitations arc closed, the §methods can be a clean catalogue of the rebuild's simulation infrastructure (`Rebuild/model/` with the four recovery-test digests at `d3c62215…` / `f4f57a89…` / `0486921f…` / `883ea15a…`; `Rebuild/sims/` with the nine sim-output digests; `Rebuild/derivations/` with the four derivations) paralleling the original paper's §3 methods. After §methods, the manuscript is structurally complete and the remaining work is sharpening passes only (14 low-priority queued tasks: RB-023, RB-024, RB-027, RB-028, RB-029, RB-031, RB-032, RB-036, RB-037, RB-039, RB-040, RB-043, RB-044, RB-045).

### Next increment

**§methods bookend** (replace the rb-005 stub in `sections/methods.tex`) — natural rhythm-matching follow-up to the §abstract, §intro, and §limitations bookends; the manuscript's structural arc closes here. Alternatives: any of the queued low-priority sharpening passes (RB-024 closed-form $\CF < 0.5$ boundary derivation; RB-029 dormant-cell amplification closeup; RB-040 Slepian-gradient analytic locus; RB-039 finer $\corr$-grid for $\rdagger(\val; \corr)$; RB-027/RB-031/RB-036/RB-043 variant-B replications; RB-028/RB-032/RB-044 grid-sharpening). §methods is preferred — finishing the bookend quartet leaves the manuscript structurally complete before the sharpening rounds.

---

## rb-048 — 2026-05-30 — §limitations bookend manuscript (manuscript) — DONE

- **Run id:** `rb-048-2026-05-30`
- **Prompt version:** 0.2
- **Task worked:** RB-048 (medium priority; new task spawned by rb-047's "next priority" recommendation — replace the rb-005 stub in `sections/limitations.tex` with the second bookend, mirroring the abstract's voice).
- **Output kind:** manuscript.
- **Claims touched:** cross-cutting (the limitations section collects the explicit scope deferrals every body section has already flagged — no claim's rebuilt strength changes; the §3.3 unifying-reframe voice is reaffirmed by stating what is and is not licensed).
- **Status:** done.

### Headline thing built

Replaced the rb-005 stub in [Rebuild/manuscript/sections/limitations.tex](Rebuild/manuscript/sections/limitations.tex) (34 lines, ~70% placeholder) with a 6-subsection bookend at the §3.3 unifying-reframe voice (~170 LaTeX lines, ~1,400 words). The section is organised by lever rather than by paper section so a reader can locate the precise conditional under which any headline number applies.

Six subsections:

- **§7.1 The conservation rule is a parameter, not a derivation** (A3, CONTESTED) — cites `eq:conservation-family`, `eq:beta-gamma-of-p`, `eq:a3d-power-mean`, `eq:a3d-chain-rule`, `eq:a3d-dprime-of-p`, `thm:delta-cf-monotone`, `prop:a3d-rp3-invariance`, `sec:appendix-deriv-a3` + explicitly names the open $|\partial_p R_{\mathrm{P4}}| \le |\partial_p R_{\mathrm{P1}}|$ closed-form conjecture and the deferred joint $(p, \corr > 0)$ band.
- **§7.2 Heterogeneity is bounded, not abolished** (A2 + A8, both CONFIRMED-CONDITIONAL) — A2 between-preparation reading cites `sec:model` + `eq:d-prime-hetero` + `tab:a2-rb021-summary` + within-display reading citations of `mcadams_maunsell1999_v4_tuning` / `reynolds_heeger2009_normalization` / `carrasco2011_visual_attention_25y`; A8 new conditional cites `sec:extensions-a8` Finding F2 with quoted $\Delta R = +2.79{\times}10^{-3} \to +3.68{\times}10^{-3}$ numbers and names the Slepian-style A8-binding-onset closed form as not derived.
- **§7.3 The decision-noise lever is deferred, not denied** (A6, WEAKLY-SUPPORTED) — explicit hold at the live verdict; would-be fourth-lever framing by symmetry with the $\corr$ channel; gating language matches the stub's prior anticipation.
- **§7.4 Assumptions retained as explicit scope** — A4 (no learning), A5 (transfer-function family $h \in \{a, \sqrt{a}, a^{0.3}, a^{2}\}$) with `def:three-levers` / `eq:r-dagger` / `prop:r-dagger-invariance` stated in generic $f$, A7 (reward variants A vs B) with variant-B sensitivity citations of `tab:cf-distribution` / `tab:cf-quadrants` / `tab:a2-rb021-summary`.
- **§7.5 Equicorrelation, $\corr$-envelope, and queued follow-ups** — cites `eq:equicorr-cov` / `eq:pnofa-rho` / `prop:r-dagger-rho` / `tab:r-dagger-rho-drift` / `RuffCohen2016` / `Srinath2021` / `CohenMaunsell2009` $r_{SC} \approx 0.2$ anchor + the queued $C_3$ / $C_4$ / A8 grid-sharpening sims (RB-028, RB-032, RB-044) + closed-form $\CF < 0.5$ boundary derivation (RB-024) + dormant-cell amplification closeup (RB-029) + Slepian-style analytic locus for cell-wise $\partial \VDA / \partial \corr$ (RB-040) + variant-B replications (RB-027, RB-031, RB-036, RB-043) + finer $\corr$-grid (RB-039) + variant-B/finer-$\corr$ A1 (RB-023).
- **§7.6 What the rebuild does not claim** — no neural-implementation claim; no empirical-$\corr$ prediction beyond the CohenMaunsell anchor; no observer-deviation prediction; no attention-dynamics claim. Explicit non-claims paragraph matching the mission §3.3 voice that the rebuilt paper is a "mathematical description" — not a biological or empirical-fit program.

### Cross-references discharged

25 labels — all verified extant before compile via `grep -hE "\\label\{(sec|prop|thm|cor|def|eq|tab|fig):" sections/*.tex` (snapshot taken before drafting). Sections: `sec:model`, `sec:model-rho-channel`, `sec:model-upper-bound`, `sec:results-c1`, `sec:results-c2`, `sec:results-c3`, `sec:results-c4`, `sec:extensions-a2`, `sec:extensions-a3`, `sec:extensions-a8`, `sec:appendix-deriv-c2`, `sec:appendix-deriv-a3`. Equations: `eq:conservation-family`, `eq:beta-gamma-of-p`, `eq:a3d-power-mean`, `eq:a3d-chain-rule`, `eq:a3d-dprime-of-p`, `eq:d-prime-hetero`, `eq:r-dagger`, `eq:equicorr-cov`, `eq:pnofa-rho`. Propositions / Theorems / Definitions: `prop:a3d-rp3-invariance`, `prop:r-dagger-invariance`, `prop:r-dagger-rho`, `thm:delta-cf-monotone`, `def:three-levers`. Tables: `tab:a2-rb021-summary`, `tab:cf-distribution`, `tab:cf-quadrants`, `tab:r-dagger-rho-drift`, `tab:a1cw-summary`. Citations: `mcadams_maunsell1999_v4_tuning`, `reynolds_heeger2009_normalization`, `carrasco2011_visual_attention_25y`, `RuffCohen2016`, `Srinath2021`, `CohenMaunsell2009`. All citations already wired (no new bib entries needed).

### Build

3-pass pdflatex (no bibtex run needed — 0 new `\cite{}` keys):

- pass 1 — pdflatex exit 0; 58 pages / 2,806,961 bytes; one undefined reference warning on `sec:limitations-followups` (a forward reference within the new section file, label appears at §7.5 below the §7.4 cite — normal pass-1 behaviour).
- pass 2 — pdflatex exit 0; 58 pages / 2,807,597 bytes; forward reference resolved, 0 undefined references.
- pass 3 — pdflatex exit 0; 58 pages / 2,807,597 bytes; byte-identical to pass 2, settled, 0 undefined refs, 0 new warnings. The hyperref Unicode-in-PDF-string warnings are pre-existing cosmetic warnings about TOC bookmarks (e.g. `\Phi`, `\sqrt{a}` etc. in subsection headers), not new and not semantic.

vs rb-047 baseline 2,792,842 bytes / 55 pages → **+3 pages, +14,755 bytes**.

### Wiki cross-references

Sweep performed; keywords {scope, limitations, conservation form, heterogeneity, decision-noise lever, learning dynamics, transfer function, reward convention, equicorrelation, structured covariance, variant B sensitivity, grid sharpening, dormant-cell amplification, neural implementation, attention dynamics}. Every paper the limitations section cites was already wired through body sections — no novel literature citations introduced in this bookend. 0 new wiki stubs; `audit.py` not re-run (no wiki writes).

### What the manuscript can now say

The rebuilt paper now has **both bookends drafted** for the first time: abstract (rb-047) and §limitations (rb-048). The cover-to-cover structure is now abstract → intro stub → model → results × 4 → extensions × 3 → **§limitations** → methods stub → appendix × 3 — 58 pages, two skeleton stubs remaining (intro, methods). The §scope paragraphs scattered across body sections are now collected into a single navigable Section 7, so a later increment that tightens any scope statement (e.g. RB-024 closed-form $\CF < 0.5$ boundary; RB-039 finer $\corr$-grid for $\rdagger(\val; \corr)$) can update one place in §limitations rather than re-stating the scope inline in two sections.

### Why the next run should care

The §limitations section is the canonical place for any future scope tightening: the §intro bookend (the natural next increment) can now anchor its motivation on the contrast between the inherited paper's categorical phrasings and the rebuilt paper's distributional/graded/conditional voice — both of which are now stated at full length (abstract paragraph 1 and §limitations §7.6). The §methods bookend can follow §intro since the rebuild's `Rebuild/` infrastructure is fully stable. The fourteen low-priority sharpening tasks (RB-023, RB-024, RB-027, RB-028, RB-029, RB-031, RB-032, RB-036, RB-037, RB-039, RB-040, RB-043, RB-044, RB-045) are all explicitly named in §limitations §7.5 either as queued sims or as queued derivations, so any future referee request for a tighter threshold maps directly onto an identified backlog item.

### Next increment

**§intro bookend** (replace the rb-005 stub in `sections/intro.tex`) — natural rhythm-matching follow-up to the §limitations and §abstract bookends; the §limitations §7.6 'what the rebuild does not claim' paragraph and the abstract's three-lever framing together set up the §intro voice. Alternatives: §methods bookend (replace the rb-005 stub in `sections/methods.tex` with a catalogue of `Rebuild/model/`, `Rebuild/sims/`, recovery contracts, deterministic hashes), OR a low-priority sharpening pass (RB-024 closed-form $\CF < 0.5$ boundary derivation; RB-029 dormant-cell amplification closeup; RB-040 Slepian-gradient analytic locus). §intro is preferred — finishing the bookend trio leaves only §methods before the manuscript is structurally complete.

---

## rb-047 — 2026-05-30 — abstract bookend manuscript (manuscript) — DONE

- **Run id:** `rb-047-2026-05-30`
- **Prompt version:** 0.2
- **Task worked:** RB-047 (medium priority; prereqs RB-004, RB-009, RB-010, RB-011, RB-012, RB-013, RB-034, RB-035, RB-042, RB-046 all done).
- **Output kind:** manuscript.
- **Claims touched:** cross-cutting (the abstract summarises every claim already wired in the body — no claim's rebuilt strength changes; the §3.3 unifying reframe is articulated up-front).
- **Status:** done.

### Headline thing built

Replaced the rb-005 abstract stub in [Rebuild/manuscript/sections/abstract.tex](Rebuild/manuscript/sections/abstract.tex) (30 lines, ~80% placeholder) with a 4-paragraph honest abstract (~430 words, ~85 LaTeX lines) at the §3.3 unifying-reframe voice: distributional / graded / conditional by default, no floors, no "regardless of", no categorical strengths beyond what the live verdicts license.

Paragraph 1 — the original question (cued $\val \ge 1$, $\valid \in [1/\Nloc, 1]$ change-detection) + the three-lever reframe (criterion + sensitivity + decorrelation; Section sec:model, Definition def:three-levers) + the ρ-channel one-factor Gauss–Hermite reduction with $\corr \to 0$ FP-identity recovery + the lead voice sentence: "every headline result at its defensible distributional, graded, or conditional strength rather than as a categorical floor."

Paragraph 2 — the four C-row headline results at CLAIM_LEDGER-licensed strength:

- **C1** ($\CF$ concentrated in $[0.30, 1.00]$, median $0.76$; inherited $[0.60, 0.96]$ retracted on both ends; $\corr=0.2$ drops the strict minimum below $0.5$; Section sec:results-c1);
- **C2** (non-monotonicity preserved + closed-form $\rdagger(\val) = K_u/[(\Nloc-1) K_c]$ that pins the lower edge of the VDA-active band; Section sec:results-c2 + $\corr > 0$ extension via $\corr$-aware gradient quadratures of Appendix sec:appendix-deriv-c2 + conservation-form-invariance from Appendix sec:appendix-deriv-a3 Prop prop:r-dagger-invariance);
- **C3** (graded iso-$\VDA$ contour band: $\valid \ge 0.95$ at grid floor under any $(\Rsens, \corr)$; $\valid \ge 0.80$ survives only at $\corr=0$; $\valid \ge 0.60$ fails; Section sec:results-c3);
- **C4** (conditional theorem with explicit boundary $\valid \ge 1/[(\Nloc-1)\val+1]$ from Eq. eq:value-weight + the **anti-cue inversion** as a new falsifiable prediction with $36.1\%$ incidence at $\Nloc=4$ anti-cue $\valid < 1/\Nloc$ regime; Section sec:results-c4);
- **C5** (universal real-number identity at $\Rsens=1$, conservation-form-invariant by construction; Appendix sec:appendix-c5).

Paragraph 3 — the A1 §model-upper-bound retraction stated at the §model voice: independence is **not** an upper bound on $\VDA$; what it actually upper-bounds is the criterion fraction, and only in variant A; $\partial\VDA/\partial\corr$ flips sign near $\Rsens \approx 0.5$ with the cell-wise crossover sweeping past $\Rsens \approx 0.79$ across the full $4{,}410$-cell sweep (Section sec:model-upper-bound).

Paragraph 4 — the three extension levers wired across model + sim + manuscript (A2 heterogeneous-$\Rsens$ as a bounded perturbation that leaves the C2 peak coordinates and the contested-CF corner essentially invariant — Section sec:extensions-a2; A3 power-mean conservation-family band on every headline number — Section sec:extensions-a3; A8 N-dim policy innocuous at the inherited additive optimum but exhibiting a new conditional binding in a benefit-dominant symmetric-stress corner under multiplicative conservation — Section sec:extensions-a8) + the closing voice clause: "every quantitative claim above is backed by a simulation under `Rebuild/sims/` with a recovered limit, a deterministic output hash, and a captioned figure; every novel proposition is derived under `Rebuild/derivations/`; nothing in this abstract is stated more strongly than its row of `CLAIM_LEDGER.md` licenses."

### Cross-references discharged

11 section/equation/definition labels — all verified extant before compile via grep against `sections/*.tex`:

- `sec:model` (model.tex), `sec:model-upper-bound` (model.tex)
- `sec:results-c1`, `sec:results-c2`, `sec:results-c3`, `sec:results-c4` (results.tex)
- `sec:extensions-a2`, `sec:extensions-a3`, `sec:extensions-a8` (extensions.tex) — **note three lowercase mismatches caught at the grep step before compile**: the first draft cited `sec:extensions-A2/A3/A8` (uppercase) but the actual labels in extensions.tex are lowercase `a2/a3/a8`; fixed inline before pdflatex was invoked.
- `sec:appendix-c5`, `sec:appendix-deriv-c2`, `sec:appendix-deriv-a3` (appendix.tex)
- `def:three-levers` (model.tex), `eq:value-weight` (results.tex)
- **One non-existent label removed before compile**: the first draft cited `Theorem~\ref{thm:c4-conditional}` in the C4 paragraph; the C4 result is stated in prose in `sec:results-c4`, not via a `\begin{theorem}` environment (verified by `grep -nE 'label\{(thm|theorem)' sections/results.tex` → empty). Replaced inline with `Section~\ref{sec:results-c4}, Equation~\eqref{eq:value-weight}`.

### Build

2-pass pdflatex clean (no bibtex re-run needed — 0 new `\cite{}` keys):

- pass 1 — pdflatex exit 0; 55 pages / 2,792,842 bytes; no errors, no warnings.
- pass 2 — pdflatex exit 0; 55 pages / 2,792,842 bytes; settled, byte-identical to pass 1; 0 undefined references, 0 LaTeX warnings.

vs rb-046 baseline 2,790,640 bytes / 55 pages → **+2,202 bytes, page count unchanged** (the new abstract replaces the stub's placeholder content on the title page without overflowing onto a new page). Small byte delta because the rebuilt abstract is dense prose where the stub was sparse comment-marked placeholder.

### Wiki cross-references

Sweep performed; keywords {value-directed attention, criterion fraction, decorrelation lever, three-lever decomposition, anti-cue inversion, conservation family, equicorrelated Gaussian, escape threshold, narrow regime, central tendency, distributional vs categorical claim, symmetric recovery}. Every paper the abstract alludes to is already wired through body sections (no direct citations in the abstract beyond cross-references to the rebuild's own sections): CohenMaunsell2009, MullerFindlay1987, Slepian1962, HLP1934, RuffCohen2016, Srinath2021, McAdamsMaunsell1999, ReynoldsHeeger2009, Treue1999, Carrasco2011, GhoseMaunsell2002, Sani2017, Sterbenz1974, Goldberg1991, WangTheeuwes2018, WangSamaraTheeuwes2019, KongLiWangTheeuwes2020, FailingTheeuwes2018, Hickey2010, Posner1980. 0 new wiki stubs; `audit.py` not re-run (no wiki writes).

### What the manuscript can now say

The rebuilt paper has a cover-to-cover narrative for the first time: the abstract states the §3.3 unifying reframe up-front; the body wires every claim at its CLAIM_LEDGER-licensed strength; the appendix folds in every novel proposition (Prop prop:r-dagger-rho of §appendix-deriv-c2, Prop prop:r-dagger-invariance of §appendix-deriv-a3, Prop prop:c5-realnumber / prop:c5-sterbenz of §appendix-c5). The remaining three skeleton stubs (intro, limitations, methods) are the bookend follow-ups; none of the C-row or A-row sub-claims requires further work from the rebuild's voice at this run.

### Why the next run should care

The abstract is now the canonical short-form summary of every CLAIM_LEDGER row; subsequent reframes of the §intro / §limitations / §methods stubs can lean on the abstract's voice and citation/cross-reference network. The §limitations stub already lists four sub-items it will fold in (A3 band, A2/A8 heterogeneity, A6 deferral, A4/A5/A7 open scope) — those are all wired in the body and just need to be lifted into the bookend voice. The §intro stub anchors on the inherited paper's literature framing and the unifying reframe — could naturally be authored next.

### Next increment

**§limitations bookend** (replace the rb-005 stub in `sections/limitations.tex` — natural rhythm-matching follow-up; the stub already lists the four sub-items the section will fold in: A3 conservation-family band, A2/A8 heterogeneity, A6 deferral, A4/A5/A7 open scope). Alternatives: §intro bookend, §methods bookend, or one of the low-priority sharpening passes (RB-024 closed-form CF<0.5 boundary, RB-029 dormant-cell amplification follow-up sim, RB-040 Slepian-gradient analytic locus). §limitations is preferred — it mirrors the abstract's voice, lands the second bookend, and naturally collects the §scope paragraphs that every body section has already deferred.

---

## rb-046 — 2026-05-30 — §appendix-deriv-a3 manuscript fold-in (manuscript) — DONE

- **Run id:** `rb-046-2026-05-30`
- **Prompt version:** 0.2
- **Task worked:** RB-046 (medium priority; prereq RB-033 done at rb-029).
- **Output kind:** manuscript.
- **Claims touched:** A3 (CONTESTED, primary); C5 (CONFIRMED-UNDER-ATTACK, picks up the formal Corollary cor:a3d-c5-invariance cross-reference); C2 (CONFIRMED-UNDER-ATTACK, picks up the full three-step proof of Proposition prop:r-dagger-invariance).
- **Status:** done.

### Headline thing built

A ≈220-LaTeX-line `sec:appendix-deriv-a3` subsection in [Rebuild/manuscript/sections/appendix.tex](Rebuild/manuscript/sections/appendix.tex), replacing the 15-line rb-017 stub at line 530. The new subsection mirrors §appendix-deriv-c2's structure (the rb-024 RB-038 fold-in pattern) and folds the rb-029 derivation file (`Rebuild/derivations/A3--power-mean-conservation.md`, ~50 KB / 1026 lines) into the manuscript's formal appendix at the rebuild-strength ceiling licensed by the live A3 verdict (CONTESTED). Five subsection blocks: (i) boxed closed-form weights $\cost(\Rsens; p) = (2/(\Rsens^p+1))^{1/p}$, $\benefit = \Rsens\cost$ (Eq. eq:a3d-closed-form-weights, companion of Eq. eq:beta-gamma-of-p of §extensions-A3) + the three preserved identities (I-1) ratio, (I-2) symmetric corner, (I-3) spread sign; (ii) HLP power-mean monotonicity in pointwise KL-divergence closed form $\partial \ln \cost / \partial p = -(1/p^2) \DKL(\mathrm{Bern}(\theta_p) \| \mathrm{Bern}(1/2))$ (Eq. eq:a3d-hlp-kl, boxed) + Eq. eq:a3d-mono-sign (sign of $\partial \benefit/\partial p$, $\partial \cost/\partial p$) + continuity through $p = 0$ via the $-(\ln\Rsens)^2/8$ limit; (iii) Proposition prop:a3d-symmetric-corner ($\benefit(1; p) = \cost(1; p) = 1$ at every $p$, full proof) + Corollary cor:a3d-c5-invariance (C5 conservation-form-invariance, full proof from the $\dprime$-map at $\Rsens=1$); (iv) **full three-step proof of Proposition prop:r-dagger-invariance** (sensitivities $p$-independent at $\alpha=1/\Nloc$ via the vanishing bracket $\dprimemax f(1/\Nloc) - \dprime_{\mathrm{base}}$; P3-optimal criteria $p$-independent by functional composition; $K_c, K_u$ ratio $p$-independent), promoting the rb-017 §extensions-A3 sketch to a structural derivation tied to a specific property of the $\dprime$-map at the uniform allocation; (v) the d'-channel chain rule Eq. eq:a3d-chain-rule / eq:a3d-dprime-of-p for $\partial R_{\mathrm{P}_i}/\partial p$ via the envelope theorem + Proposition prop:a3d-rp3-invariance ($\partial \Rpthree/\partial p \equiv 0$ at $\alpha = 1/\Nloc$, full proof) as the one analytic full-strength substatement, plus the open-conjecture statement $|\partial_p R_{\mathrm{P4}}| \le |\partial_p R_{\mathrm{P1}}|$ that integrates to $\Delta\CF \le 0$. Reproducibility paragraph cross-references rb-001 (`d3c62215…`), rb-015 (`f4f57a89…`), rb-016 (`055bf4ec…`), and the finite-difference verification of Eq. eq:a3d-hlp-kl at seven test pairs (LHS-RHS $\le 1.5\times10^{-10}$).

### Cross-reference updates

Three forward references in `extensions.tex` discharged:

- **§extensions-A3 intro paragraph** (rb-017 line 53): "a formal derivation in the rebuild's voice is deferred to Appendix~\ref{sec:appendix-deriv-a3} (the queued companion increment RB-033 in the backlog)" → rewritten as "the formal derivation in the rebuild's voice — the closed-form weights, the HLP power-mean monotonicity in exact KL-divergence form, and the two formal proofs underlying Proposition~\ref{prop:r-dagger-invariance} and the C5 conservation-form-invariance corollary — is given in Appendix~\ref{sec:appendix-deriv-a3}."

- **Theorem thm:delta-cf-monotone parenthetical** (rb-017 line 350): "We do not have a closed-form algebraic proof of this empirical monotonicity in the rebuild's voice; the queued companion increment RB-033 is the natural home for one." → rewritten to cite the chain-rule analysis of Appendix~\ref{sec:appendix-deriv-a3} that reduces $\partial \CF/\partial p$ to the open inequality $|\partial_p \Rpfour| \le |\partial_p \Rpone|$ and isolates Proposition~\ref{prop:a3d-rp3-invariance} ($\partial \Rpthree/\partial p \equiv 0$ at $\alpha = 1/\Nloc$) as the one analytic full-strength substatement available.

- **§extensions-A3 scope paragraph item (ii)** (rb-017 lines 417-418): "is deferred to Appendix~\ref{sec:appendix-deriv-a3} (RB-033)" → rewritten as "is given in Appendix~\ref{sec:appendix-deriv-a3}" with an inline pointer to Equation~\eqref{eq:a3d-hlp-kl} (the exact KL-divergence identity).

Plus a new forward-reference paragraph added right after the proof sketch of `prop:r-dagger-invariance` in §extensions-A3, pointing readers at the full three-step proof in Appendix~\ref{sec:appendix-deriv-a3} (each step tied to a specific structural property of the $\dprime$-map at the uniform allocation).

The §appendix-c5 conservation-form-invariance paragraph (`appendix.tex:481-497`) picks up an additional formal cross-reference: "The formal mechanism is Proposition~\ref{prop:a3d-symmetric-corner} of Section~\ref{sec:appendix-deriv-a3}; the C5-side corollary itself is Corollary~\ref{cor:a3d-c5-invariance}." (The existing inline proof is preserved verbatim.)

### How it connects to the ledger

**Discharges** the A3 row's stub at `appendix.tex:530`, completing the A3 thread across all four output kinds for the first time of any claim in the rebuild: **model (rb-015, RB-015), sim (rb-016, RB-019), manuscript-extensions (rb-017, RB-034), derivation (rb-029, RB-033), and manuscript-appendix (rb-046, RB-046)** — five increments × four output kinds × A3 coverage.

**C5 row** picks up a tighter cross-reference: the §appendix-c5 conservation-form-invariance paragraph now points at Proposition prop:a3d-symmetric-corner and Corollary cor:a3d-c5-invariance, replacing the prior "Section~\ref{sec:extensions-a3}" pointer with a formal-statement pointer.

**C2 row** picks up the full structural proof of Proposition prop:r-dagger-invariance in the appendix (the rb-017 proof sketch in §extensions-A3 is preserved verbatim, and a one-paragraph cross-reference now points readers at the full proof).

**No label drift in the live ledger.** All 10 verdict labels still match the §3 table of `agents/paper_rebuilder_prompt.md` v0.2 (only the §3 A6 entry remains stale; already flagged in CLAIM_LEDGER at rb-018).

### Build / verification evidence

- **PDF**: 55 pages / 2,790,640 bytes (was 53 pages / 2,763,376 bytes at rb-028 = +2 pages, +27,264 bytes). Comparable to the rb-024 §appendix-deriv-c2 fold-in (+3 pages / +200 KB) — appendix subsections without figures land lighter than results/extensions subsections.
- **Build**: 4-pass pdflatex+bibtex clean. Pass 1 hit two macro-stub misses: `\DKL` (no macro) — fixed by adding `\newcommand{\DKL}{D_{\mathrm{KL}}}` to `main.tex` next to the existing math macros; `\Pthree`/`\Pone`/`\Pfour`/`\Ppolicy`/`\Ethree[\Rew]`/`\Rpi` (manuscript convention is plain-text policy labels per the existing `\Rpone`/`\Rpthree`/`\Rpfour` functional macros) — fixed by inline replacement with `\textrm{P3}`/`\textrm{P1}`/`\textrm{P4}`/`\textrm{P}`/`\Rpthree`/`R_{\mathrm{P}_i}`. After fixes: pass 1 OK → bibtex no-op (0 new bib entries) → passes 2-4 (settled; 0 undefined refs; 0 non-hyperref warnings).
- **Cross-reference resolution verified** via `pdftotext` extraction: the new subsection appears in the PDF at pages 49-54 with all eight new labels (eq:a3d-power-mean, eq:a3d-closed-form-weights, eq:a3d-hlp-kl, eq:a3d-mono-sign, prop:a3d-symmetric-corner, cor:a3d-c5-invariance, prop:a3d-rp3-invariance, eq:a3d-chain-rule, eq:a3d-dprime-of-p) resolved to printed numbers, and the four cross-reference updates in §extensions-A3 and §appendix-c5 all render the new appendix sections as printed numbers (Section/Equation/Proposition/Corollary references).
- **Math cross-check (Eq. eq:a3d-hlp-kl)**: inherited from rb-029 finite-difference verification at 7 test pairs (LHS-RHS agreement $\le 1.5\times10^{-10}$). No new numerical work this run — the fold-in is pure manuscript prose.
- **Recovery digests unchanged** (this run touches no model code or sim code): rb-001 `d3c62215…` (A1 channel), rb-015 `f4f57a89…` (A3 family), rb-016 `055bf4ec…` (A3 sim), rb-019 `0486921f…` (heterogeneous-r), rb-020 `883ea15a…` (N-dim policy).

### What the manuscript can now say (verbatim ceiling)

- "Equation~\eqref{eq:a3d-closed-form-weights} of Section~\ref{sec:appendix-deriv-a3} gives the closed-form weights $\cost(\Rsens; p) = (2/(\Rsens^p+1))^{1/p}$, $\benefit = \Rsens\cost$ of the A3 conservation family $M_p(\benefit, \cost) = 1$ with $\benefit/\cost = \Rsens$, by direct substitution. The case $p = 1$ recovers the inherited additive rule; $p = 0$ the multiplicative."

- "By the Hardy--Littlewood--Pólya power-mean monotonicity inequality, $\partial \ln \cost/\partial p = -(1/p^2)\DKL(\mathrm{Bern}(\theta_p) \| \mathrm{Bern}(1/2))$ (Equation~\eqref{eq:a3d-hlp-kl}), so $\partial \benefit/\partial p < 0$ and $\partial \cost/\partial p < 0$ at every $\Rsens > 0$, $\Rsens \ne 1$ (Equation~\eqref{eq:a3d-mono-sign})."

- "C5 symmetric recovery is conservation-form-invariant: $\benefit(1; p) = \cost(1; p) = 1$ at every $p$ (Proposition~\ref{prop:a3d-symmetric-corner}), and the asymmetric $\dprime$-map collapses pointwise to the symmetric baseline at $\Rsens = 1$ (Corollary~\ref{cor:a3d-c5-invariance})."

- "Proposition~\ref{prop:r-dagger-invariance} admits a full three-step proof (Section~\ref{sec:appendix-deriv-a3}, following Equation~\eqref{eq:a3d-hlp-kl}): sensitivities $p$-independent at $\alpha = 1/\Nloc$ via the vanishing bracket $\dprimemax\,f(1/\Nloc) - \dprime_{\mathrm{base}}$; P3-optimal criteria $p$-independent by functional composition; $K_c, K_u$ ratio $p$-independent at the $p$-independent operands. The numerical witness rb-016 records $\max|\Delta\rdagger| = 0$ across $p \in \{0, 1/2, 1\}$ to floating-point identity."

- "The chain-rule analysis of Section~\ref{sec:appendix-deriv-a3} reduces $\partial \CF/\partial p$ to a competition between the cued-channel and uncued-channel $d'$ gradients, establishes $\partial \Rpthree/\partial p \equiv 0$ at $\alpha = 1/\Nloc$ analytically (Proposition~\ref{prop:a3d-rp3-invariance}), and identifies the uniform inequality $|\partial_p \Rpfour| \le |\partial_p \Rpone|$ as the closed-form conjecture whose pointwise validity on the $4{,}410$-cell C1 grid is empirically witnessed by Theorem~\ref{thm:delta-cf-monotone}."

The manuscript does **not** license:

- A uniform closed-form proof of $\Delta\CF \le 0$ across the C1 grid — the chain-rule analysis identifies the open inequality but does not close it. Left as a queued open problem (see the scope paragraph in §appendix-deriv-a3).
- A joint $(p, \corr)$ sensitivity analysis — the rb-016 Block B sweep is $\corr = 0$ only.
- Any new conservation-family member outside the closed form Equation~\eqref{eq:a3d-closed-form-weights}.

### Next increment

Per §4.1 of the mission, the highest-priority unblocked open tasks are:

- **RB-024** (C1 closed-form CF<0.5 boundary derivation, prereq RB-005 done at rb-003) — the only C1 derivation thread still open; would let §results-C1 replace `frac<0.6 = 22%` with a closed-form predicate the reader can compute pointwise. Low priority but high natural rhythm match to RB-046 (both are "discharge a queued stub" patterns).
- **RB-029** (A1 dormant-cell amplification follow-up sim, prereq RB-010 done at rb-010) — the most striking single qualitative finding of rb-010; would give §results-A1 a falsifiable behavioural prediction the §5.2 redrafted design recommendations could leverage.
- **RB-040** (Slepian-gradient analytic locus for the cell-wise $\partial\VDA/\partial\rho$ surface, prereq RB-025 done at rb-025) — would close the A1 manuscript-side architecturally, paralleling the A3 manuscript-side closure this run discharged.
- A manuscript-bookend increment (abstract / intro / limitations / methods) — the manuscript content sections are now wired (model, results-C1/C2/C3/C4, extensions-A3/A2/A8, appendix-derivation-A1/C2/C5/A3); the next architectural move is the bookend.

The natural next move is RB-024 (matching the "finish what's wired" rhythm of RB-046), but the A1 follow-up sims (RB-029 / RB-040) and the manuscript bookends are all reasonable parallel options.

### Wiki cross-references

The §11.1 mechanism-keyword sweep across `research_db/` confirms no new external literature is introduced by this fold-in. Keywords swept: {power mean, generalised Hölder mean, Hardy-Littlewood-Pólya, conservation, β+γ=2, β·γ=1, KL divergence, Jensen's inequality, envelope theorem, criterion fraction sensitivity, conservation-form-invariance, $p$-invariance, symmetric corner, Sterbenz lemma}. All citations in the new appendix subsection point at HLP1934 (wired at rb-017) only; Bullen 2003 and Cover-Thomas 2006 are cited by full bibliographic reference in the long-form derivation file `Rebuild/derivations/A3--power-mean-conservation.md` (rb-029) and are not re-cited in the manuscript subsection per the math-methods scope inherited from rb-008/rb-014/rb-015/rb-017. No new `research_db/papers/` stubs added; `audit.py` not re-run.

### Files written

- `Rebuild/manuscript/sections/appendix.tex` — `sec:appendix-deriv-a3` subsection replaced (the 15-line rb-017 stub at lines 530-543 is now a ≈220-LaTeX-line self-contained subsection); §appendix-c5 conservation-form-invariance paragraph picks up a formal cross-reference to Prop prop:a3d-symmetric-corner / Cor cor:a3d-c5-invariance.
- `Rebuild/manuscript/sections/extensions.tex` — three forward references in §extensions-A3 discharged (intro paragraph at line 53; Theorem thm:delta-cf-monotone parenthetical at line 350; scope item (ii) at line 417); one new forward-reference paragraph added right after the proof sketch of prop:r-dagger-invariance.
- `Rebuild/manuscript/main.tex` — one new math macro `\newcommand{\DKL}{D_{\mathrm{KL}}}` next to the existing math macros (line 79).
- `Rebuild/manuscript/main.pdf` — rebuilt 55 pages / 2,790,640 bytes (was 2,763,376 at rb-028 = +27,264 bytes; +2 pages).
- `Rebuild/CLAIM_LEDGER.md` — top reconcile paragraph rewritten for rb-046 (previous rb-029 paragraph rolled out, since its derivation content is now also folded into the manuscript appendix); A3 row backing column extended with the rb-046 manuscript-appendix block.
- `Rebuild/REBUILD_BACKLOG.md` — RB-046 status → done with full notes.
- `Rebuild/rebuilder_state.json` — `runs_completed` → 30, `last_run_id` / `last_run_ended` updated, `done_task_ids` adds RB-046, `open_task_ids` removes RB-046, `manuscript_sections_drafted` extended, `rb_046_manuscript_pdf_bytes` = 2790640 added.
- `Rebuild/conversations/2026-05-30-rebuilder-a3-appendix-foldin.md` (NEW).

No model edits; no new sims; no new bib entries; no new wiki stubs; `audit.py` not re-run.

---

## rb-029 — 2026-05-30 — A3 power-mean conservation family derivation (derivation) — DONE

- **Run id:** `rb-029-2026-05-30`
- **Prompt version:** 0.2
- **Task worked:** RB-033 (A3 derivation: power-mean conservation family in the rebuild's voice; prereq RB-015 done at rb-015, RB-019 done at rb-016, RB-017 manuscript done at rb-017).
- **Output kind:** derivation.
- **Claims touched:** A3 (CONTESTED, primary); C5 (CONFIRMED-UNDER-ATTACK, Corollary 4.2 gains analytic backing); C2 (CONFIRMED-UNDER-ATTACK, $\rdagger(v)$ $p$-invariance Proposition 5.1 promoted to full proof).
- **Status:** done.

### Headline thing built

A new ≈50 KB / 1020-line derivation at [Rebuild/derivations/A3--power-mean-conservation.md](Rebuild/derivations/A3--power-mean-conservation.md) — the project's first formal A3 derivation (the reviewer has none; the verdict relies on replication numerics). The file promotes the rb-017 §extensions-A3 sketch into a full derivation across 9 sections + Verification + Extensions blocks: §1 setup; §2 power-mean family with closed-form weights $\cost(\Rsens; p) = (2/(\Rsens^p+1))^{1/p}$, $\benefit = \Rsens\cost$ (Eq. 2.3, boxed) derived by direct substitution into $\PowerMean_p = 1$; §3 **HLP power-mean monotonicity translated to a KL-divergence closed form** $\partial \ln \cost/\partial p = -(1/p^2)\,D_{\mathrm{KL}}(\mathrm{Bern}(\theta_p) \| \mathrm{Bern}(1/2))$ (Eq. 3.3, boxed; $\theta_p = \Rsens^p/(\Rsens^p+1)$) with the corollary that both $\benefit$ and $\cost$ are strictly decreasing in $p$ for any $\Rsens \ne 1$; §4 Proposition 4.1 (symmetric-corner identity, full proof) + Corollary 4.2 (C5 conservation-form-invariance, full proof from the $\dprime$-map at $\Rsens=1$); §5 **full three-step proof of Proposition 5.1** ($\rdagger(\val)$ $p$-invariance), promoting the rb-017 §extensions-A3 sketch; §6 d'-channel chain rule for $\partial\CF/\partial p$ via envelope theorem with the open-conjecture statement of $\Delta\CF \le 0$; §7 numerical realisation citing rb-015 and rb-016; §8 scope; §9 references.

### Five things the manuscript can now license at appendix strength

1. **Power-mean family is the canonical generalisation of A3.** The constraint $\PowerMean_p(\benefit, \cost) = 1$ with $\benefit/\cost = \Rsens$ has unique closed-form solution $\cost(\Rsens; p) = (2/(\Rsens^p+1))^{1/p}$, $\benefit = \Rsens\cost$ (Eq. 2.3). $p=1$ is the inherited additive rule, $p=0$ the multiplicative limit, $p=-1$ the harmonic.
2. **HLP monotonicity in pointwise form.** $\partial \ln \cost/\partial p = -(1/p^2)\,D_{\mathrm{KL}}(\mathrm{Bern}(\theta_p) \| \mathrm{Bern}(1/2))$ (Eq. 3.3) — the classical HLP power-mean monotonicity inequality expressed as an exact KL divergence. Cross-checked numerically by finite-difference at 7 $(\Rsens, p)$ pairs with LHS-RHS agreement $\le 1.5 \times 10^{-10}$.
3. **C5 corollary at every $p$** (Corollary 4.2). At $\Rsens=1$, $\benefit = \cost = 1$ at every $p$ from Eq. 2.3; the asymmetric model collapses to the symmetric baseline pointwise, giving the C5 real-number identity result conservation-form-invariantly.
4. **Full proof of $\rdagger(\val)$ $p$-invariance** (Proposition 5.1). Three steps: (a) sensitivities $p$-independent at $\alpha = 1/N$ via vanishing bracket $\dprimemax\,f(1/N) - \dprime_{\mathrm{base}} = 0$; (b) $\Pthree$-optimal criteria $p$-independent by functional composition; (c) $K_c, K_u$ partials $p$-independent, hence their ratio is. Numerical witness rb-016 TEST 3 to floating-point identity ($\max|\Delta| = 0$).
5. **d'-channel chain rule for $\partial\CF/\partial p$**, with $\partial \Rpthree/\partial p \equiv 0$ at $\alpha = 1/N$ analytically established but uniform $\Delta\CF \le 0$ left as an open conjecture. The rebuild's two-tier statement: (i) analytic full strength = $\rdagger, \Rpthree$ $p$-invariance; (ii) empirical full strength + chain-rule motivation = $\Delta\CF \le 0$ at $0/4410$ reverse flips.

### How it connects to the ledger

**Discharges** the A3 row's "Derivation §appendix-derivation-A3 (RB-033) remains low-priority" license that has carried since rb-017. The A3 row is now wired across model (rb-015), sim (rb-016), manuscript-extensions (rb-017), AND derivation (rb-029). The C2 row's Proposition prop:r-dagger-invariance picks up a fully formal proof — promoting the rb-017 sketch — and the C5 row's appendix subsection (rb-018, sec:appendix-c5) picks up its forward-referenced conservation-form-invariance corollary as an analytic statement (Corollary 4.2).

**No label drift in the live ledger.** All 10 verdict labels still match the §3 table of `agents/paper_rebuilder_prompt.md` v0.2 (A6's drift to WEAKLY-SUPPORTED was already flagged in CLAIM_LEDGER at rb-018; not re-flagging).

### Build / verification evidence

- **Derivation file size**: 49,720 bytes / 1020 lines. Comparable to rb-014's C4 derivation (42 KB / 940 lines) and rb-023's C2 ρ-extension derivation (~36 KB / ~800 lines).
- **Math cross-check (Eq. 3.3 KL closed form)**: numerically verified by finite-difference at 7 test pairs $(\Rsens, p) \in \{(0.3548, 0.5), (0.3548, 1), (10, 1), (10, 0.5), (3.162, 2), (0.5, -1), (5, 1.5)\}$ with LHS-RHS agreement $\le 1.5\times 10^{-10}$ in every case; at $\Rsens = 1$ both sides are exactly $0$. Verification rationale embedded in §3.3 of the derivation (`gamma(0.3548, p=1) = 1.4762; gamma(0.3548, p=0) = 1.6788; +13.72%`).
- **Eq. 2.3 (closed-form weights) cross-checked** against rb-015 `test_family_identities` to relative error $\le 4.4 \times 10^{-16}$ across $p \in \{-2,-1,-1/2,0,1/2,1,2\}$ and 21-point log-$\Rsens$ grid; this digest carries from rb-015.
- **Proposition 4.1 (symmetric corner)** verified by rb-015 `test_symmetric_corner_invariant` (binary equality across $p \in \{-2..+2\}$).
- **Proposition 5.1 ($\rdagger$ $p$-invariance)** verified by rb-016 `recovery.test_3_r_dagger_p_invariance` ($K_c, K_u, c_c^\star, c_u^\star, \rdagger(\val)$ identical to floating-point identity across $p \in \{0, 1/2, 1\}$; max $|\Delta| = 0.0$).
- **All four model-test recovery digests unchanged**: rb-001 `d3c62215…` (A1 channel), rb-015 `f4f57a89…` (A3 family), rb-019 `0486921f…` (heterogeneous-r), rb-020 `883ea15a…` (N-dim policy). This derivation is a pure consumer; no model code touched, no new sim, no new test, no manuscript edits.

### What the manuscript can now say (verbatim ceiling)

- "The A3 conservation family $\PowerMean_p(\benefit, \cost) = 1$ with $\benefit/\cost = \Rsens$ has unique closed-form solution $\cost(\Rsens; p) = (2/(\Rsens^p+1))^{1/p}$, $\benefit = \Rsens\,\cost$ (Eq. 2.3 of Section sec:appendix-deriv-a3), with $p=1$ the inherited additive rule and $p=0$ the multiplicative limit."
- "By the HLP power-mean monotonicity inequality, $\partial \ln \cost / \partial p = -(1/p^2)\,D_{\mathrm{KL}}(\mathrm{Bern}(\theta_p) \| \mathrm{Bern}(1/2))$ (Eq. 3.3), where $\theta_p = \Rsens^p/(\Rsens^p+1)$. Both $\benefit$ and $\cost$ are strictly decreasing in $p$ for any $\Rsens > 0$, $\Rsens \ne 1$."
- "C5 symmetric recovery is conservation-form-invariant by construction: $\benefit(1; p) = \cost(1; p) = 1$ at every $p$ (Proposition 4.1), so the $\dprime$-map at $\Rsens=1$ collapses to the symmetric baseline pointwise (Corollary 4.2)."
- "Proposition 5.1 ($\rdagger(\val)$ is conservation-form-invariant) admits a full three-step proof: sensitivities $p$-independent at $\alpha = 1/N$ by the vanishing bracket $\dprimemax\,f(1/N) - \dprime_{\mathrm{base}} = 0$; $\Pthree$-optimal criteria $p$-independent by functional composition; $K_c, K_u$ ratio $p$-independent at the $p$-independent operands. The numerical witness $\max|\Delta\rdagger| = 0$ across $p \in \{0, 1/2, 1\}$ (rb-016 TEST 3) verifies that the algebra also commutes with the floating-point implementation."
- "The d'-channel chain rule for $\partial\CF/\partial p$ (Eqs. 6.3–6.6) establishes $\partial \Rpthree/\partial p \equiv 0$ at $\alpha = 1/N$ analytically, but reduces the sign of $\partial \CF / \partial p$ to a competition between two $\dprime$-channel gradients whose uniform inequality is the open closed-form conjecture for Theorem thm:delta-cf-monotone. The rebuild reports the result at full empirical strength ($0/4410$ reverse flips, rb-016) with this chain-rule analysis supplying the mechanism."

The manuscript does **not** license:

- A uniform closed-form proof of $\Delta\CF \le 0$ across the C1 grid — left as a future derivation increment (called out in §6.4 and §8.2 of the file).
- A joint $(p, \corr)$ sensitivity analysis — the rb-016 Block B sweep is $\corr = 0$ only; the rb-029 §8 scope flags this as a queued extension (analytic composition of Eq. 3.3 with `Rebuild/derivations/C2--non-monotonic-vda-rho.md` §3 ρ-channel gradients).
- Manuscript-side discharge of the §appendix-deriv-a3 stub — queued as RB-046 (spawned this run; medium priority; would parallel the rb-023→rb-024 C2 derivation→manuscript-fold pattern).

### Next increment

Per §4.1 of the mission, the highest-priority unblocked open task is now **RB-046** (the §appendix-deriv-a3 manuscript fold-in spawned this run, medium priority — natural rhythm match to the rb-023 → rb-024 §appendix-deriv-c2 pattern). It would discharge the rb-017 stub at `Rebuild/manuscript/sections/appendix.tex:530` completely and close the A3 row's last open thread.

Alternative parallel options, all unblocked: **RB-024** (C1 closed-form CF<0.5 boundary derivation, prereq RB-005 done — the only C1 derivation thread still open); **RB-029** (A1 dormant-cell amplification follow-up sim — the most striking single qualitative finding of rb-010, would give §results-A1 a falsifiable behavioural prediction the §5.2 redrafted design recommendations could leverage); **RB-040** (Slepian-gradient analytic locus for the cell-wise $\partial\VDA/\partial\rho$ surface).

### Wiki cross-references

The §11.1 mechanism-keyword sweep across `research_db/` is unnecessary this run: the derivation cites only math-methods references already in `Rebuild/manuscript/refs.bib` (HLP 1934 wired at rb-017) or by full bibliographic reference per the math-methods scope inherited from rb-008/rb-014/rb-015/rb-017 (Bullen 2003 *Handbook of Means and Their Inequalities*; Cover & Thomas 2006 *Elements of Information Theory*; Sterbenz 1974 — already wired). No new external literature claims were introduced; no new mechanisms or concepts were named that would require a `research_db/papers/` entry. Keywords swept: {power mean, generalised Hölder mean, Hardy-Littlewood-Pólya, conservation, β+γ=2, β·γ=1, KL divergence, Jensen's inequality, envelope theorem, criterion fraction sensitivity}.

### Files written

- `Rebuild/derivations/A3--power-mean-conservation.md` — new (49,720 bytes / 1020 lines; 9 sections + Verification + Extensions; heavily LaTeX; mathematical content cross-checked numerically in §3.3 to $1.5 \times 10^{-10}$).
- `Rebuild/CLAIM_LEDGER.md` — top reconcile paragraph rewritten for rb-029 (previous rb-028 paragraph rolled into "Earlier reconcile"); A3 row backing column extended with the rb-029 derivation block.
- `Rebuild/REBUILD_BACKLOG.md` — RB-033 status → done with full notes; one new task RB-046 queued (§appendix-deriv-a3 manuscript fold-in, medium priority).
- `Rebuild/rebuilder_state.json` — `runs_completed` → 29, `last_run_id` / `last_run_ended` updated, `done_task_ids` adds RB-033, `open_task_ids` removes RB-033 adds RB-046, `next_task_id_counter` → 47, `derivations_written` adds RB-033, `rb_029_derivation_bytes` = 49720 added.
- `Rebuild/conversations/2026-05-30-rebuilder-a3-power-mean-derivation.md` (NEW).

No model edits; no new sim; no manuscript edits; no new bib entries; no new wiki stubs; `audit.py` not re-run.

---

## rb-028 — 2026-05-30 — §extensions-A8 manuscript subsection (manuscript) — DONE

- **Run id:** `rb-028-2026-05-30`
- **Prompt version:** 0.2
- **Task worked:** RB-042 (medium priority, prereqs RB-021 done at rb-027).
- **Output kind:** manuscript.
- **Claims touched:** A8 (CONFIRMED-CONDITIONAL, primary); A1 (compositional axis); A3 (compositional axis).
- **Status:** done.

### Headline thing built

A new ≈420-line §extensions-A8 LaTeX subsection appended to [Rebuild/manuscript/sections/extensions.tex](Rebuild/manuscript/sections/extensions.tex) (sibling to §extensions-A3 from rb-017 and §extensions-A2 from rb-022), turning the rb-027 simulation's five findings into manuscript prose at the rebuild-strength ceiling licensed by the live A8 verdict (CONFIRMED-CONDITIONAL). The subsection states the rebuilt model's lifted policy space (uniform $\boldsymbol{r}$, unconstrained $\boldsymbol{\alpha}$ on the $N$-simplex, scored through `er_full_policy` of rb-020 with the homogeneous-recovery contract at $\le 2.78\times10^{-10}$); reports the rb-027 sim through Table tab:a8-rb027-summary (24-row Part 1c × p panel with explicit $\Delta R$, uncued spread, and a binds-yes/no column — two binding panels both at the symm-stress-r10 cell at $p=0$, both bolded), Table tab:a8-rho-curv-ratio (5-row Part 1 curvature ρ-amplification), and three figures `fig:a8-simplex-dr`, `fig:a8-curvature`, `fig:a8-anticued-suppression`; closes with a Wang–Theeuwes-style behavioural-anchor paragraph citing the two pre-existing bib entries `wang_theeuwes2018_statistical_learning_distractor_suppression` and `failing_theeuwes2018_selection_history`; and adds a Scope paragraph deferring variant-B replication (RB-043), finer r-grid (RB-044), $N>4$ generalisation, sim-boundary hardening (RB-045), and the closed-form A8-binding-onset locus (a future Slepian-style derivation, not queued). The §extensions section intro paragraph was also touched (Two further → Three further; A2/A8 → A2, A8 split) since A8 is now its own subsection rather than co-listed with A2.

### Five findings now licensed in the manuscript

- **F1 (recovery PASS).** At $(\corr=0, p=1)$, 0/6 cells bind; max $\Delta R = 6.82\times10^{-4}$ (below the $10^{-3}$ slack threshold). The lifted `er_full_policy` reproduces the reviewer's CR-036 Part 1c "A8 innocuous everywhere" headline structurally — the universal-statement guarantee under which F2–F5 acquire their meaning.
- **F2 (the new conditional).** At the high-$r$ symmetric-stress benefit-dominant corner ($V=1/N=0.25$, $v=1$, $r=10$, variant A) under multiplicative conservation $p=0$, the full-simplex optimum splits $\boldsymbol{\alpha}^\star = (0.5, 0, 0, 0.5)$ vs the homogeneous $\alpha_c\approx0.05$ optimum; $\Delta R = +2.79\times10^{-3}$ at $\corr=0$ and $+3.68\times10^{-3}$ at $\corr=0.2$ — a strict binding (both above the $10^{-3}$ slack). $\corr=0.2$ amplifies the binding by 32% (3.68/2.79). At $p=1$ the same cell shows $\Delta R<0$ — the binding is conservation-form-dependent. To our knowledge this is the first quantitative statement that A8 binds at all in this model family.
- **F3 (the binding is non-local).** $R''(0)$ along the symmetry-preserving redistribution direction is negative in 20/20 panels — equal-split is a local max at the homogeneous $\alpha^\star$ regardless of $(\corr, p)$. The F2 global optimum at $(0.5, 0, 0, 0.5)$ cannot be reached by local gradient information from the homogeneous policy; a global simplex search is required.
- **F4 (A1×A8 composes more orthogonally than A1×A2).** $\corr$-amplification of $|R''(0)|$ at $p=1$ is small and non-uniform (mean 1.048, max 1.135, one cell suppresses by 6%) — much weaker than the rb-021/A2 ~2× amplification of the equal-split criticality residual. A2 breaks per-location asymmetry exchange symmetry (which the joint no-FA integrand inherits directly); A8 breaks per-location allocation exchange symmetry (which the integrand inherits only through second-order curvature on a homogeneous $\dprime$ — a higher-order coupling).
- **F5 (anti-cued graded suppression survives ρ=0.2).** The Wang–Theeuwes-style monotone-decreasing $a_{\mathrm{anti}}^\star$ in $w_{\mathrm{anti}}$ + strict $a_{\mathrm{anti}}^\star < a_{\mathrm{rest}}^\star$ properties of CR-036 Part 2 both hold at $\corr \in \{0, 0.2\}$; $\corr=0.2$ only weakly perturbs the gradient (shifts the $a_{\mathrm{anti}}^\star=0$ collapse by one grid step from $w_{\mathrm{anti}}=0.075$ to $0.050$).

### How it connects to the ledger

**Discharges** the A8 row's "§extensions-A8 manuscript subsection still queued (natural next manuscript task: discharges the last remaining §extensions sibling)" license from the rb-027 reconcile. The A8 row is now wired across **model** (rb-017 `optimal_ER_general` / `er_full_policy`; rb-020 7/7-PASS contract), **sim** (rb-027 24-panel sweep), and **manuscript-extensions** (rb-028, this subsection). The only remaining A8 threads are RB-043 (variant-B replication, low priority), RB-044 (finer r-grid, low priority), and RB-045 (sim-boundary hardening at the model level — no verdict-bearing claim).

**No label drift in the live ledger.** All 10 verdict labels still match the §3 table of `agents/paper_rebuilder_prompt.md` v0.2 (A6's drift to WEAKLY-SUPPORTED was already flagged in CLAIM_LEDGER at rb-018; not re-flagging).

### Build evidence

- **PDF**: `Rebuild/manuscript/main.pdf` recompiled to **51 pages, 2,763,376 bytes** (was 49 pages / 2,587,742 bytes at rb-026 = +2 pages, +175,634 bytes). This is in line with the §extensions-A3 (rb-017, +6 pages) and §extensions-A2 (rb-022, +5 pages) precedents — the rb-028 increment is slightly lighter because it reuses the `eq:d-prime-hetero` substrate from rb-022 rather than re-stating it.
- **4-pass pdflatex+bibtex clean**: pass 1 → bibtex (no new entries) → pass 2 (refs settled by .aux update) → pass 3 (0 undefined refs, 0 LaTeX warnings beyond cosmetic `hyperref` Unicode-token-in-section-header warnings — the same set seen in rb-022/rb-026). Build artifacts cleaned.
- **3 figures** copied from [Rebuild/sims/A8--nd-uncued-sweep/output/figures/](Rebuild/sims/A8--nd-uncued-sweep/output/figures/) to [Rebuild/manuscript/figures/](Rebuild/manuscript/figures/) with the `a8_` prefix already present.
- **2 citations** added in the F5 behavioural anchor paragraph — both pre-existing in `refs.bib` from rb-013 (the §appendix-C5 increment which seeded the behavioural literature). 0 new bib entries.
- **0 new wiki stubs**; `audit.py` not re-run (no wiki writes).
- **All four model-test recovery digests unchanged**: rb-001 `d3c62215…` (A1 channel), rb-015 `f4f57a89…` (A3 family), rb-019 `0486921f…` (heterogeneous-r), rb-020 `883ea15a…` (N-dim policy). The rb-027 sim digest `beb2aa87…` is the deterministic source of every number in the subsection.

### What the manuscript can now say (verbatim ceiling)

- "The rebuilt model's lifted policy space `er_full_policy(alloc, valid, v, r_vec, cell)` reproduces the reviewer's CR-036 Part 1c 'A8 innocuous everywhere' headline at the inherited $(\corr=0, p=1)$ regime: 0/6 binds, max $\Delta R = 6.82\times10^{-4}$ below the $10^{-3}$ slack."
- "Under multiplicative conservation $p=0$, A8 binds in the high-$\Rsens$ symmetric-stress benefit-dominant corner ($V=1/N=0.25$, $v=1$, $\Rsens=10$, variant A), by $\Delta R = +2.79\times10^{-3}$ at $\corr=0$ and $+3.68\times10^{-3}$ at $\corr=0.2$ — a $32\%$ A1 amplification of the conservation-form-induced binding."
- "The F2 binding is non-local: equal-split is a local maximum at the homogeneous $\alpha^\star$ in every $(\text{cell}, \corr, p)$ panel tested."
- "The A1 amplification of equal-split criticality is much smaller for A8 (mean 1.048, max 1.135) than for A2 (~2×) — A1 and A8 compose more orthogonally than A1 and A2 do."
- "The Wang–Theeuwes-style anti-cued graded-suppression mechanism of CR-036 Part 2 generalises across the A1 channel at $\corr \in \{0, 0.2\}$."

The manuscript does **not** license:

- Variant-B reproduction of the F2 binding — queued as RB-043 (the single variant-B cell tested in Part 1c, `C1-contested-cnr`, has $\Delta R<0$ in all four $(\corr, p)$ panels, but is not the symm-stress-r10 cell).
- A finer-r-grid characterisation of the p=0 binding onset (where does it start and end on the $r$-axis?) — queued as RB-044.
- $N>4$ generalisation — not in the rb-027 substrate (all Part 1c cells at $N=4$).
- A closed-form predicate for the A8-binding locus in $(r, p, V, \text{variant})$ — would be a future derivation increment (possibly a Slepian-style monotonicity argument on the joint no-FA integrand under simplex perturbation; not queued).

### Next increment

Per §4.1 of the mission, the highest-priority unblocked open task is RB-033 (A3 derivation: power-mean conservation family in the rebuild's voice), which would land an `§appendix-deriv-A3` companion to the `§appendix-deriv-C2` from rb-024 — converting the empirical Theorem 3.2 ($\Delta\CF \le 0$) and Proposition 3.1 ($r^\dagger$ $p$-invariance) of §extensions-A3 into formal derivations from a Hardy–Littlewood–Pólya power-mean monotonicity argument. Alternatively, RB-029 (A1 dormant-cell amplification follow-up sim, low priority but high novelty value — the most striking single qualitative finding of rb-010 — would give the §results-A1 a falsifiable falsifiable-prediction paragraph for any value-blind / low-validity behavioural test). Both are model→sim→derivation→manuscript order-compatible.

### Wiki cross-references

The §11.1 mechanism-keyword sweep across `research_db/` is unnecessary this run: the §extensions-A8 subsection cites only artefacts already in the rebuilt manuscript (`eq:d-prime-hetero` from §extensions-A2, `er_full_policy` from `Rebuild/model/`, the rb-027 sim, and four pre-existing recovery digests) plus two pre-wired behavioural citations from `refs.bib`. No new external literature claims were introduced; no new mechanisms or concepts were named that would require a wiki entry.

---

## rb-027 — 2026-05-30 — A8 N-dim uncued allocation sweep under ρ, p extensions (simulation) — DONE

---

## rb-027 — 2026-05-30 — A8 N-dim uncued allocation sweep under ρ, p extensions (simulation) — DONE

- **Run id:** `rb-027-2026-05-30`
- **Prompt version:** 0.2
- **Task worked:** RB-021 (A8 N-dim uncued allocation sweep, prereq RB-017 done at rb-020).
- **Output kind:** simulation.
- **Claims touched:** A8 (CONFIRMED-CONDITIONAL, primary); A1 (compositional axis); A3 (compositional axis).
- **Status:** done.

### Headline thing built

A new simulation at [Rebuild/sims/A8--nd-uncued-sweep/](Rebuild/sims/A8--nd-uncued-sweep/) (`run.py` ≈ 22 KB / ~670 LaTeX lines, `README.md` ≈ 8 KB) that scores **24 panels of full-simplex vs homogeneous-constrained optimum across the (cell × ρ × p) lever cube**, **20 panels of equal-split R″(0) curvature**, and **18 cells of anti-cued joint optimum** through the rebuilt `er_full_policy(alloc, valid, v, r_vec, cell)` driver from rb-020 (sha256 `883ea15a…`, 7/7 PASS). The rebuild contribution beyond the reviewer's CR-036 (`Critique/replications/A8--heterogeneous-uncued/run.py`): lift the "A8 innocuous at the model's own optimum" test from the inherited (ρ=0, p=1) substrate to the joint cube ρ ∈ {0, 0.2} × p ∈ {1, 0}, exercising the A1 channel (rb-001) and the A3 conservation family (rb-015) compositionally with A8.

**Five findings (F1–F5)** capture the picture:

1. **F1 (RECOVERY PASS)** — at (ρ=0, p=1), 0/6 cells bind, max dR = 6.82×10⁻⁴ (threshold dR > 1×10⁻³). The rebuilt model reproduces the reviewer's CR-036 Part 1c "A8 innocuous everywhere" headline exactly.
2. **F2 (NEW CONDITIONAL)** — at multiplicative conservation (p=0), the symm-stress-r10 cell (V=0.25 = 1/N, v=1, r=10, variant A) shows **dR = +2.79×10⁻³ (ρ=0) → +3.68×10⁻³ (ρ=0.2)**: the full-simplex optimum splits attention as (a_cued=0.5, uncued_spread=0.5) vs the homogeneous (a_cued≈0.05); the same cell at p=1 has dR = −1.38×10⁻³ < 0 (homogeneous wins to slack). **ρ amplifies the binding by 32%** (3.68/2.79). To our knowledge this is the first quantitative statement of A8 binding in this model family.
3. **F3 (LOCAL VS GLOBAL)** — R″(0) along [+1, +1, −2] at the homogeneous α* is **negative in 20/20 panels**: equal-split is a local maximum in every tested cell regardless of (ρ, p). Combined with F2, this means the binding is **non-local** — the homogeneous α≈0.05 is locally stable but globally dominated by the far-away α_cued=0.5 concentrated allocation.
4. **F4 (A2 ≠ A8 ρ-COMPOSITION)** — ρ-amplification of |R″(0)| at p=1 is small and non-uniform: mean ratio 1.048, max 1.135 (v1-reference), min 0.941 (v1-symmetric — *suppresses* by 6%). The rb-021 A2 finding of ~2× ρ-amplification of equal-split criticality residual **does NOT generalise to the A8 N-dim uncued question**; A1 and A8 compose more orthogonally than A1 and A2 do.
5. **F5 (WANG-THEEUWES SURVIVAL)** — anti-cued graded suppression at (r=0.398, v=1, V=0.40) is monotone-decreasing in w_anti AND strictly below a_rest at both ρ ∈ {0, 0.2}; ρ only weakly perturbs the gradient (delays w_anti at which a_anti collapses to 0 from ≈0.075 to ≈0.050). The statistical-learning suppression link of CR-036 Part 2 survives the rebuild's correlation channel.

### Key new statements the manuscript can now make

- The rebuilt model's lifted policy space `er_full_policy(alloc, valid, v, r_vec, cell)` reproduces CR-036's "A8 innocuous at the model's own optimum" at (ρ=0, p=1) to the same allocation-grid slack: 0/6 of CR-036's decisive cells admit a non-trivial full-simplex improvement, max dR = 6.82×10⁻⁴.
- **At multiplicative conservation (p=0), A8 binds in the high-r symmetric-stress benefit-dominant corner (V=1/N, v=1, r=10, variant A) — dR = +2.79×10⁻³ at ρ=0 and +3.68×10⁻³ at ρ=0.2.** The conservation-form swap reverses A8's compatibility with the model's optimum in this corner; the same cell at p=1 prefers homogeneity.
- **ρ=0.2 amplifies the F2 A8 binding by 32%** (dR ratio 1.32×); the A1 channel amplifies the conservation-form-induced A8 violation.
- **The F2 binding is non-local**: in every tested (cell × ρ × p) panel, R″(0) at the homogeneous α* is negative — equal-split remains a local max even in the cell where the global optimum is far away.
- The rb-021/A2 finding "ρ amplifies the equal-split criticality residual ~2×" **does not generalise to A8**: the analogous ratio for A8 R″(0) magnitude is mean 1.05, max 1.13. A1 and A8 compose more orthogonally than A1 and A2 do.
- The CR-036 Wang-Theeuwes anti-cued graded suppression gradient generalises across ρ ∈ {0, 0.2}; the monotonicity and strict-suppression checks both pass at ρ=0.2.

The manuscript does **not** yet license:

- Variant-B replication of the F2 binding — queued as RB-043.
- A finer r-grid characterisation of the p=0 binding onset (where does it start? where does it end?) — queued as RB-044.
- A closed-form predicate for the A8-binding boundary in (r, p, V, variant) — would be a derivation increment, possibly a Slepian-style monotonicity argument on the joint no-FA integrand under simplex perturbation; not yet queued.

### How it connects to the ledger

**Discharges** the A8 row's "Sim (RB-021) still queued" license. The A8 row now licenses **one new conditional** at p=0 (multiplicative conservation): A8 binds in the high-r symmetric-stress benefit-dominant corner, ρ-amplified by 32%. The pre-existing "A8 innocuous at the model's own optimum under inherited (ρ=0, p=1)" claim remains licensed by F1 (recovery PASS). The A8 row is now sim-wired (rb-027) and waits on its §extensions-A8 manuscript subsection (queued as RB-042).

**No label drift in the live ledger** (10/10 verdict labels still match the §3 table of `agents/paper_rebuilder_prompt.md` v0.2; only the §3 A6 entry remains stale, already flagged in CLAIM_LEDGER).

### Simulation / verification evidence

- **Deterministic sha256**: `beb2aa879402e5c9f4c354a2c9f53a98c466d0989085dc8c78370be99dee290b` — sha256 of the canonical (sort_keys=True, indent=2) JSON dump of `results` with `wall_clock_seconds` removed. Byte-identical across reruns (verified empirically: `cp output/results.canonical.json /tmp/canon1 && rerun && diff -q canon1 output/results.canonical.json` → no difference).
- **Canonical bytes** persisted at `output/results.canonical.json` (24 KB).
- **Pre-computed digest** persisted at `output/results.json.deterministic_sha`.
- **Wall clock**: 72.2 s on python3.13 / scipy 1.17.1 / numpy 2.4.4.
- **All four model-test digests unchanged** after the sim (the sim is a pure consumer of `er_full_policy`; no model code touched): rb-001 `d3c62215…` (recovery, 7/7); rb-015 `f4f57a89…` (conservation family, 14/14); rb-019 `0486921f…` (heterogeneous r, 5/5); rb-020 `883ea15a…` (general policy, 7/7).
- **Three figures** rendered: `a8_simplex_dr.png` (headline F2 binding bar chart), `a8_curvature.png` (R″(0) heatmap), `a8_anticued_suppression.png` (graded gradient).

### Crash and fix logged

The first run hit `AssertionError: best_idx is None` in `Rebuild/model/core.py:965 optimal_ER_general`, in the multi-restart coordinate-ascent path. Root cause: when the anti-cued joint-optimum loop iterates over `a_anti` near `rem`, float arithmetic in `a_rest = (rem - a_anti) / 2.0` produced values like −1×10⁻¹⁷; `np.sqrt` inside `f_transfer` (via the `make_h("sqrt")` lambda at `core.py:264`) returned NaN, which propagated through every criterion-grid evaluation, leaving every `R` as NaN and `best_idx` never set. Fixed at the sim boundary in `run.py:_ER` by clamping `np.maximum(alloc, 0.0)` before passing to `er_full_policy`; the inherited model never produces negative alloc by construction so byte-for-byte recovery is preserved. The crash mode is a candidate model-side hardening note for `d_prime_hetero` (queued as RB-045).

### What the manuscript can now say

At the A8-row strength ceiling, with the new rb-027 sim backing it:

> The rebuilt model's lifted policy space — the N-dim uncued allocation simplex evaluated through `er_full_policy(alloc, valid, v, r_vec, cell)` — reproduces the reviewer's "A8 innocuous at the model's own optimum" headline (CR-036 Part 1c) exactly under the inherited (ρ=0, p=1) regime: across the 6 decisive cells, the full-simplex optimum coincides with the homogeneous-constrained one to within the 1×10⁻³ allocation-grid slack (max dR = 6.82×10⁻⁴). Under the rebuild's two added levers, A8 **does** acquire one new conditional: at multiplicative conservation (p=0), the high-r symmetric-stress benefit-dominant corner (V=1/N, v=1, r=10, variant A) admits a non-trivial full-simplex improvement of dR = +2.79×10⁻³ (ρ=0) → +3.68×10⁻³ (ρ=0.2), with the full optimum at (a_cued=0.5, uncued_spread=0.5) vs the homogeneous (a_cued≈0.05). The binding is non-local: R″(0) at the homogeneous α* along the symmetric uncued redistribution direction is negative in every tested cell, so equal-split remains a local max even where the global max lies far away. ρ=0.2 amplifies the binding by ~32%; ρ × A8 composition is more orthogonal than ρ × A2 composition (mean |R″(0)|-ratio 1.05 vs ~2× for A2 at the same cell list). The CR-036 anti-cued graded-suppression gradient (Wang-Theeuwes statistical-learning link) survives the correlation channel at ρ ∈ {0, 0.2}.

It does **not** yet license:

- (a) a variant-B replication of the F2 binding — queued as RB-043;
- (b) a sharper r-grid bracketing of the p=0 binding onset — queued as RB-044;
- (c) a closed-form predicate for the A8-binding boundary in (r, p, V, variant) — derivation increment not yet queued;
- (d) the §extensions-A8 manuscript subsection — queued as RB-042 (the natural next increment).

### Why the next run should care

This run **closes the simulation loop on the A8 thread** at the (ρ × p) cube and yields the first quantitative A8-binding statement in this model family. The natural next increment is **RB-042** (§extensions-A8 manuscript subsection) — it lands the last sibling subsection in `extensions.tex`, giving the rebuilt manuscript a complete §extensions trio §extensions-A2 (rb-022), §extensions-A3 (rb-017), §extensions-A8 (RB-042 pending). After RB-042, the heterogeneity thread (A2, A8 levers) is fully wired sim → manuscript-extensions, and the manuscript work shifts toward the abstract / intro / limitations bookends.

Alternative parallel options, all unblocked: **RB-033** (A3 formal derivation in rebuild's voice — fills `§appendix-deriv-a3` stub placed by rb-017); **RB-024** (C1 closed-form CF<0.5 boundary derivation); **RB-040** (Slepian-gradient analytic locus for the cell-wise ∂VDA/∂ρ surface). RB-042 is preferred — it discharges the rb-027 sim into manuscript prose at the same rhythm the rb-021/rb-022 and rb-016/rb-017 pairs established.

### Wiki cross-references

Wiki sweep performed for keywords {N-dim uncued allocation, multi-dimensional simplex policy, equal-split critical point, anti-cued graded suppression, conservation × A8 interaction, ρ × A8 interaction, value-weight inequality}. All needed behavioural citations (Wang-Theeuwes 2018, Wang-Samara-Theeuwes 2019, Kong-Li-Wang-Theeuwes 2020, Failing-Theeuwes 2018, Hickey 2010, Posner 1980) already wired in `Rebuild/manuscript/refs.bib` from rb-013 (RB-012). All math-methods citations (Slepian 1962, Tong 1990, HLP1934, Sterbenz 1974, Goldberg 1991) cited by full bibliographic reference per math-methods scope inherited from rb-008 / rb-013 / rb-017 / CR-035/CR-037. No new `research_db/papers/` stubs added; `audit.py` not re-run (no wiki writes).

### Files written

- `Rebuild/sims/A8--nd-uncued-sweep/run.py` — new (≈22 KB, ~670 lines, heavily commented; deterministic; numpy/scipy/matplotlib).
- `Rebuild/sims/A8--nd-uncued-sweep/README.md` — new (≈8 KB) walking through the F1–F5 findings, the recovery contract, the scope deferrals, and cross-links to CR-036 / rb-020 / rb-016 / rb-021.
- `Rebuild/sims/A8--nd-uncued-sweep/output/results.json` — 24 KB human-readable JSON (includes `wall_clock_seconds`, non-deterministic field).
- `Rebuild/sims/A8--nd-uncued-sweep/output/results.canonical.json` — 24 KB canonical (sort_keys=True, indent=2) JSON with `wall_clock_seconds` removed; sha256 = `beb2aa879402e5c9f4c354a2c9f53a98c466d0989085dc8c78370be99dee290b`.
- `Rebuild/sims/A8--nd-uncued-sweep/output/results.json.deterministic_sha` — pre-computed sha256.
- `Rebuild/sims/A8--nd-uncued-sweep/output/figures/a8_simplex_dr.png` (52 KB) — headline F2 binding bar chart.
- `Rebuild/sims/A8--nd-uncued-sweep/output/figures/a8_curvature.png` (39 KB) — R″(0) heatmap.
- `Rebuild/sims/A8--nd-uncued-sweep/output/figures/a8_anticued_suppression.png` (57 KB) — graded suppression gradient.
- `Rebuild/CLAIM_LEDGER.md` — top reconcile paragraph rewritten for rb-027 (previous rb-026 paragraph rolled into "Earlier reconcile"); A8 row backing column extended with the rb-027 sim block + one new conditional in the strength column tail.
- `Rebuild/REBUILD_BACKLOG.md` — RB-021 status → done with full notes; four new tasks queued (RB-042 §extensions-A8 manuscript, RB-043 variant-B A8 sweep, RB-044 finer r-grid, RB-045 d_prime_hetero hardening).
- `Rebuild/rebuilder_state.json` — `runs_completed` → 27, `last_run_id` / `last_run_ended` updated, `done_task_ids` adds RB-021, `open_task_ids` removes RB-021 adds RB-042/RB-043/RB-044/RB-045, `next_task_id_counter` → 46, `sims_written` adds RB-021, `rb_027_sim_digest` = `beb2aa879402e5c9f4c354a2c9f53a98c466d0989085dc8c78370be99dee290b` added.
- `Rebuild/conversations/2026-05-30-rebuilder-a8-nd-uncued-sweep.md` (NEW).

---

## rb-026 — 2026-05-30 — Fold rb-025 cell-wise sign-flip into §model §5.5-replacement (manuscript) — DONE

- **Run id:** `rb-026-2026-05-30`
- **Prompt version:** 0.2
- **Task worked:** RB-041 (manuscript fold-in of rb-025 cell-wise sign-flip distribution into `sec:model-upper-bound`).
- **Output kind:** manuscript.
- **Claims touched:** A1 (CONTESTED, primary). No model edits; pure prose + figure increment.
- **Status:** done.

### Headline thing built

A four-block continuation of [Rebuild/manuscript/sections/model.tex](Rebuild/manuscript/sections/model.tex) §sec:model-upper-bound (≈155 LaTeX lines), inserted after the existing corrected §5.5 blockquote and replacing the trailing "Statement~B... queued as RB-025 / RB-023 / RB-026" paragraph that has been in `model.tex` since rb-009. The four blocks fold the rb-025 cell-wise sign-flip distribution into manuscript prose at the strength the A1 row of `CLAIM_LEDGER.md` already licensed:

1. **Cell-wise generalisation paragraph.** At $\rho = 0.2$ — the central anchor of the $\rho \in [0, 0.4]$ empirical band of §model-rho-channel — the $4{,}410$-cell sweep of §results-c1 licenses a cell-wise distributional statement. Per-cell $\Delta\VDA = \VDA(\rho{=}0.2) - \VDA(\rho{=}0)$, classified at $|\Delta\VDA| > 10^{-6}$, yields variant-A fractions $18.3\%$ amp / $28.2\%$ supp / $53.5\%$ inactive and variant-B $12.2\% / 27.5\% / 60.3\%$. The variant-A maximum cell-wise amplification ($+4.97 \times 10^{-2}$) is **5.3× the rb-002 single-cell maximum** at $(\valid, \val, \Rsens) = (0.5, 5, 0.4)$ ($+9.4 \times 10^{-3}$ at $\rho = 0.2$): the rb-002 observation was a typical-magnitude snapshot, not the strongest cell.
2. **Table tab:a1cw-summary.** 11 rows × 2 variant columns: fraction counts ($n_{\mathrm{amp}}, n_{\mathrm{supp}}, n_{\mathrm{inactive}}$), per-cell $\Delta\VDA$ quantiles (min / $q_{0.05}$ / $q_{0.50}$ / $q_{0.95}$ / max / mean), and cell-wise crossover $\Rsens^{\times}$. Numbers sourced verbatim from `Rebuild/sims/A1--vda-signflip-cellwise/output/results.json` (sha256 `489c7c25…`).
3. **Two-statement paragraph.** *(i) Cell-wise crossover.* $\Rsens^{\times}(\mathrm{A}) \approx 0.794$ (variant-A first $\Rsens$ at which $\mathrm{frac}_{\mathrm{amp}} \ge \mathrm{frac}_{\mathrm{supp}}$ across $(\valid, \val)$); variant~B never crosses on the rb-003 grid. Nearest-cell sweep at $\valid = 0.5125$, $\val = 5$ reproduces rb-002's small-$\Rsens$ suppression / large-$\Rsens$ amplification pattern within the rb-003 $\valid$-grid perturbation of $+0.0125$ off rb-002's $\valid = 0.5$. *(ii) Spatial structure at $\val = 5$.* The mean $\Delta\VDA$ surface over $(\valid, \Rsens)$ at $\val = 5$ is the cell-wise companion to Figure~\ref{fig:iso-vda-drho} of §results-c3: amplification concentrates at moderate-to-low $\valid$ and moderate-to-large $\Rsens$; suppression concentrates at high $\valid$ and small $\Rsens$. Variant~B is uniformly more suppression-favoring than variant~A.
4. **Three new figure floats** at $0.86\linewidth$: `fig:a1cw-delta-distribution`, `fig:a1cw-signflip-by-r`, `fig:a1cw-sign-heatmap-v5`. Source files copied from `Rebuild/sims/A1--vda-signflip-cellwise/output/figures/` to `Rebuild/manuscript/figures/` with `a1cw_` prefix (byte-identical).

Two outdated cross-references corrected in place:

- The closed-form sign-flip locus formerly "queued as RB-026" is now cited as Section sec:appendix-deriv-c2 / Proposition prop:r-dagger-rho / Equation eq:r-dagger-rho — folded into the manuscript at rb-024 (RB-038).
- The finer-$\rho$ grid extension remains queued as RB-023; the analytic Slepian-gradient locus for the cell-wise $\partial\VDA/\partial\rho$ surface is queued as RB-040.

No model edits; no derivation edits; pure prose + figure + table increment.

### Key new statements the manuscript can now make

- At $\rho = 0.2$, $18.3\%$ of variant-A cells in the $4{,}410$-cell sweep show amplification and $28.2\%$ show suppression; variant~B is uniformly more suppression-favoring ($12.2\% / 27.5\%$).
- Maximum cell-wise amplification (variant~A, $+4.97 \times 10^{-2}$) is **$5.3\times$** the rb-002 single-cell maximum.
- Cell-wise crossover $\Rsens^{\times}(\mathrm{A}) \approx 0.794$; variant~B never crosses. The variant-A nearest-cell at $\valid = 0.5125$, $\val = 5$ reproduces rb-002's pointwise sign-flip pattern.
- The cell-wise $v = 5$ heatmap is the spatial companion to the C3 thread's iso-$\Delta\VDA$ figure.

### How it connects to the ledger

**Discharges** the A1 row's `rb-025 cell-wise distribution can be folded into §model §5.5-replacement (sec:model-upper-bound) in a follow-up manuscript edit` license. After rb-026 the A1 row is fully wired across sim (rb-002, rb-025), derivation (rb-008), manuscript-model (rb-009, rb-026), and is cross-pinned to the appendix via §appendix-deriv-c2 (rb-024, RB-038). Remaining A1 threads are RB-023 (finer-$\rho$ grid, low priority) and RB-040 (Slepian-gradient analytic locus, low priority).

**No label drift in the live ledger** (10/10 verdict labels still match the §3 table of `agents/paper_rebuilder_prompt.md` v0.2; only the §3 A6 entry remains stale, already flagged in CLAIM_LEDGER).

### Simulation / verification evidence

No new sim run (manuscript-prose increment). All numerical content folded into the four blocks draws from rb-025's `Rebuild/sims/A1--vda-signflip-cellwise/output/results.json` (pre-embed sha256 `489c7c2581d1e940cfc67427e0793959bb33b24afda075ee648743aa2ac659ea`), itself a pure consumer of rb-003's `Rebuild/sims/C1--cf-distribution/output/results.json` (sha256 `91fc4692…`, validated against reviewer CR-002 at `max|ΔCF| = 1.47e-6`). Three structural recovery contracts of rb-025 (source-payload sha; sign-flip at nearest cell V=0.5125 to rb-002's V=0.5 headline; cell-wise crossover $0.794 \ge$ rb-002 headline crossover $0.464$) are the upstream guarantee. No model edits; pre-existing recovery contracts unchanged.

### Build details

4-pass pdflatex clean. Pass 1: OK, no errors; "There were undefined references" + "Label(s) may have changed" warnings (expected — the new `tab:a1cw-summary`, `fig:a1cw-*` labels not yet in `.aux`); 45 pages, 2,587,682 bytes. bibtex: no new `\cite{}` commands, no-op. Pass 2: 45 pages, 2,587,742 bytes (cross-refs resolved). Pass 3: 45 pages, 2,587,742 bytes (0 undefined refs, 0 errors). Pass 4: byte-identical to pass 3 — settled. Final PDF: **45 pages / 2,587,742 bytes** (was 43/2,413,318 at rb-024 = +2 pages, +174,424 bytes).

### What the manuscript can now say

At the A1-row strength ceiling, with the new §sec:model-upper-bound continuation backing it:

> At $\rho = 0.2$, the central anchor of the $\rho \in [0, 0.4]$ empirical band, the rebuilt expected-reward expression delivers cell-wise amplification ($\Delta\VDA > +10^{-6}$) in $18.3\%$ of variant-A cells of the primary $4{,}410$-cell sweep and suppression in $28.2\%$; variant~B is uniformly more suppression-favoring ($12.2\%$ amp / $27.5\%$ supp). The maximum cell-wise amplification (variant~A, $+4.97 \times 10^{-2}$) is $5.3\times$ the rb-002 single-cell maximum. The cell-wise crossover $\Rsens^{\times}(\mathrm{A}) \approx 0.794$ sits to the right of the rb-002 single-cell crossover ($\Rsens \approx 0.464$) because higher-$\valid$ cells dominate the sweep; variant~B never crosses. The inherited paper's §5.5 "upper bound on VDA" framing fails cell-wise as well as pointwise.

It does **not** yet license:

- (a) a closed-form prediction of the cell-wise amplification maximiser in $(\valid, \val, \Rsens)$ — queued as RB-040;
- (b) cell-wise sign-flip at $\rho$ values other than $0.2$ — queued as RB-023;
- (c) generalisation across higher correlations ($\rho > 0.4$) — outside the empirical envelope of CohenMaunsell2009.

### Why the next run should care

This run **closes the manuscript loop on the A1 cell-wise sign-flip statement.** The §model §5.5-replacement subsection now carries the cell-wise distributional retraction at the same strength the §appendix-deriv-c2 subsection (rb-024) carries the closed-form lower-edge drift of the escape band — together they form a matched pair of "the inherited §5.5 framing fails along both channels of the A1 two-channel decomposition" statements in the manuscript. The A1 row is now fully wired sim → derivation → manuscript-model → manuscript-appendix-cross-pin; the only A1 follow-ups are RB-023 (finer-$\rho$ grid, low priority) and RB-040 (Slepian-gradient analytic locus, low priority).

**The natural next increment is RB-021** (A8 N-dim uncued sweep, prereq RB-017 done at rb-020) — the only remaining §extensions sibling subsection (§extensions-A3 done at rb-017, §extensions-A2 done at rb-022, §extensions-A8 still queued). Alternative parallel options, all unblocked: **RB-033** (A3 formal derivation, fills `§appendix-deriv-a3` stub placed by rb-017); **RB-024** (C1 closed-form CF $< 0.5$ boundary derivation); **RB-040** (Slepian-gradient analogue for the cell-wise $\partial\VDA/\partial\rho$ locus — formal companion to this run's empirical statement). RB-021 is preferred — it lands the last extension subsection before the manuscript work shifts toward the abstract / intro / limitations bookends.

### Wiki cross-references

Wiki sweep performed for keywords {cell-wise sign-flip, $\partial\VDA/\partial\rho$, amplification incidence, cost-dominant vs benefit-dominant regime, criterion devaluation, concentration-cost relaxation, A1 two-channel decomposition, Slepian-gradient}. All citations needed already wired (CohenMaunsell2009, RuffCohen2016, Srinath2021 from rb-008/rb-009); Slepian 1962 and Tong 1990 still cited by full bibliographic reference (math-methods scope inherited from rb-008/rb-014/rb-017/rb-018 / CR-035/CR-037). No new `research_db/papers/` stubs added; `audit.py` not re-run (no wiki writes).

### Files written

- `Rebuild/manuscript/sections/model.tex` — §sec:model-upper-bound trailing paragraph replaced by ≈155-line four-block continuation (cell-wise paragraph + Table tab:a1cw-summary + two-statement paragraph + 3 Figure floats fig:a1cw-*).
- `Rebuild/manuscript/figures/a1cw_vda_delta_distribution.png` — copy of `Rebuild/sims/A1--vda-signflip-cellwise/output/figures/vda_delta_distribution.png`.
- `Rebuild/manuscript/figures/a1cw_signflip_by_r.png` — copy of `signflip_by_r.png`.
- `Rebuild/manuscript/figures/a1cw_vda_sign_heatmap_v5.png` — copy of `vda_sign_heatmap_v5.png`.
- `Rebuild/manuscript/main.pdf` — regenerated, 45 pages / 2,587,742 bytes (4-pass settled).
- `Rebuild/CLAIM_LEDGER.md` — top reconcile paragraph updated for rb-026; A1 row backing column tail extended with the manuscript fold-in block.
- `Rebuild/REBUILD_BACKLOG.md` — RB-041 status → done with notes block.
- `Rebuild/rebuilder_state.json` — `runs_completed` → 26, `last_run_id` / `last_run_ended` updated, `done_task_ids` adds RB-041, `open_task_ids` removes RB-041, `manuscript_sections_drafted` adds "RB-041 (§model-upper-bound cell-wise fold-in)", `rb_026_manuscript_pdf_bytes` = 2,587,742 added.
- `Rebuild/conversations/2026-05-30-rebuilder-a1-cellwise-model-foldin.md` (NEW).

---

## rb-025 — 2026-05-29 — A1 cell-wise sign-flip of dVDA/dρ across 4,410-cell sweep (simulation) — DONE

- **Run id:** `rb-025-2026-05-29`
- **Prompt version:** 0.2
- **Task worked:** RB-025 (A1 cell-wise sign-flip generalisation, prereq RB-005 done at rb-003).
- **Output kind:** simulation.
- **Claims touched:** A1 (CONTESTED, primary); C1 (cells re-aggregated by sign — distributional, not headline-shifting).
- **Status:** done.

### Headline thing built

A new simulation at [Rebuild/sims/A1--vda-signflip-cellwise/](Rebuild/sims/A1--vda-signflip-cellwise/) that is a **pure consumer** of rb-003's `results.json` (sha256 `91fc4692…`) — no new model evaluation, because rb-003 already saves `VDA` per cell at both ρ ∈ {0, 0.2} panels of the 4,410-cell (variant, r, V, v) sweep. The sim joins the two ρ panels on (variant, r, V, v), computes `ΔVDA = VDA(ρ=0.2) − VDA(ρ=0)` per cell, classifies each cell as amplification (ΔVDA > +1e−6), suppression (ΔVDA < −1e−6), or inactive, and produces three distributional cuts:

1. **Per-variant Δ-distribution.** Counts, quantiles, mean, min, max — the direct VDA analogue of rb-003's CF Δ-distribution.
2. **r-stratified sign-flip pattern.** At each r in the rb-003 21-pt log10 r-grid and per variant: `frac_amp(r)`, `frac_supp(r)`, `mean ΔVDA(r)`, `max amp`, `max supp`. The **cell-wise crossover r** is the smallest r at which `frac_amp(r) ≥ frac_supp(r)` across (V, v) — the direct cell-wise generalisation of rb-002's headline-cell `first_sign_flip_r["0.20"] = 0.4642`.
3. **(V, r) signed-mean heatmap at v = 5.** Cell-wise companion to rb-010's `iso_vda_drho` figure on the C3 thread.

**Headline numbers** (over 2,205 cells per variant):

```
                       variant A          variant B
amp   (ΔVDA > +1e-6)   404 (18.3%)        269 (12.2%)
supp  (ΔVDA < −1e-6)   621 (28.2%)        607 (27.5%)
inactive               1,180 (53.5%)      1,329 (60.3%)

ΔVDA min               −0.00914           −0.00323
ΔVDA q5 / q50 / q95    −0.00451 / 0 /     −0.00070 / 0 /
                        +0.00387           +0.00038
ΔVDA max               +0.04974           +0.00577
ΔVDA mean              +0.00023           −0.00005

cell-wise crossover r   0.7943             never
```

### Key new statements the manuscript can now make

- Cell-wise sign-flip: rb-002's V=0.5 single-cell observation generalises across the full sweep, but the **cell-wise crossover sits at r ≈ 0.7943** (variant A) — well to the right of rb-002's V=0.5 headline-cell crossover at r ≈ 0.4642 — because higher-V cells (V ≥ 0.5125 in rb-003) suppress more strongly and pull the crossover right.
- **Variant B never crosses**: the manuscript now has a 4,410-cell substrate for the rb-002 variant-B flat-in-ρ caveat as a cell-wise pattern, not a single-cell observation.
- **Maximum cell-wise amplification (+0.0497, variant A) is 5.3× rb-002's max headline-cell pointwise excess (+0.0094 at V=0.5, v=5, r=0.4)** — the rb-002 observation was a *typical-magnitude* snapshot, not the strongest case. The largest excursions of the A1 effect sit elsewhere in (V, v, r).

These numbers replace pointwise / single-cell phrasing in §model §5.5-replacement (`sec:model-upper-bound`) with a cell-wise distributional statement; the manuscript fold-in is the natural successor (spawned as **RB-041**, queued, prereq RB-025 done).

### How it connects to the ledger

- **Discharges:** the A1 row's "cell-wise generalisation of rb-002's headline-cell sign-flip observation across the rb-003 4,410-cell sweep" license. The A1 row now carries: (i) the rebuilt model + ρ-channel test (rb-001), (ii) the rb-002 headline-cell sweep, (iii) rb-008's derivation, (iv) the rb-010 (V, v) cross-axis sign-flip evidence at v ∈ [2, 11], (v) rb-003's cell-wise CF Δ-distribution at 84% one-sided variant A / 64% variant B, and now (vi) the cell-wise VDA Δ-distribution at r-stratified crossover 0.7943 (variant A) / never (variant B).
- **No label drift in the live ledger** (10/10 verdict labels still match the §3 table of `agents/paper_rebuilder_prompt.md` v0.2).

### Simulation evidence

Pre-embed sha256 `489c7c2581d1e940cfc67427e0793959bb33b24afda075ee648743aa2ac659ea`. Source rb-003 sha256 `91fc4692…`. rb-002 reference sha256 `b692c064…`. Deterministic — re-running yields the same sha. Wall clock < 1 s (pure JSON IO + NumPy aggregation; no model evaluation, no RNG).

Three recovery contracts PASS:
- **(a) Source-payload sha** guarantee: the rb-003 results.json sha256 matches the rb-003 metadata, and rb-003's own recovery test against the reviewer's CR-002 floor-replication (`max|ΔCF|=1.47e-6` across 4,410 cells) is the upstream guarantee inherited here.
- **(b) Sign-flip at the nearest cell** to rb-002's V=0.5 headline (variant A, V=0.5125, v=5): both small-r suppression and large-r amplification present; nearest-cell crossover r ≈ 0.3981 ≈ rb-002 V=0.5 crossover 0.4642 within the +0.0125 V-perturbation onto rb-003's grid.
- **(c) Cell-wise crossover ≥ rb-002 headline**: the variant-A cell-wise crossover (0.7943) sits at or above the rb-002 V=0.5 single-cell crossover (0.4642), consistent with the expected direction (higher-V cells dominate the sweep and pull the crossover right).

Three figures (in `output/figures/`):
- `vda_delta_distribution.png` (2-panel variant histogram of per-cell ΔVDA, with mean / quantile annotation)
- `signflip_by_r.png` (2-panel variant `frac_amp` vs `frac_supp` curves over the rb-003 21-pt log10 r-grid, crossover r marked)
- `vda_sign_heatmap_v5.png` (2-panel variant mean ΔVDA over (V, r) at v=5, diverging colormap)

### What the manuscript can now say

At the A1 row strength ceiling, with the new rb-025 sim backing it:

> Across the rb-003 4,410-cell (variant, r, V, v) sweep at ρ = 0.2 vs ρ = 0, the sign of ∂VDA/∂ρ varies cell-wise: 18.3% of variant-A cells show amplification, 28.2% show suppression, the remaining 53.5% are inactive; the cell-wise crossover r (where amplification overtakes suppression across (V, v)) sits at r ≈ 0.794 in variant A and **does not occur in variant B at any r in the rb-003 grid**. The mean ΔVDA is +0.00023 in variant A (slightly amplifying) and −0.00005 in variant B (slightly suppressing). The maximum cell-wise amplification (+0.0497, variant A) is 5.3× the rb-002 V=0.5 headline-cell maximum (+0.0094), demonstrating that the rb-002 single-cell observation was a *typical-magnitude* snapshot of a cell-wise phenomenon whose largest excursions sit elsewhere in (V, v, r). The original paper's §5.5 framing of independence as a uniform upper bound on VDA fails cell-wise as well as pointwise.

It does **not** yet license:
- (a) A closed-form prediction of which (V, v, r) cell maximises amplification — the cell-wise maximum is empirical here; the analytic locus is queued (extension of RB-026 / Slepian-gradient analogue RB-040).
- (b) A cell-wise crossover at *finer* ρ resolution — RB-039 / RB-023-the-backlog-item would refine, but this sim reports at ρ = 0.2 only.
- (c) A *quantitative* generalisation across higher correlations (ρ > 0.4) — outside the empirical envelope of CohenMaunsell2009.

### Why the next run should care

This run **closes the empirical loop on the A1 sign-flip statement**: the rebuild now has both an analytic lower-edge locus for ∂VDA/∂ρ (rb-023's r†(v;ρ) closed form / §appendix-deriv-c2, folded in at rb-024) and a 4,410-cell empirical Δ-distribution (rb-025). The §model §5.5-replacement subsection (`sec:model-upper-bound`) currently states the failure of the inherited upper-bound at the *pointwise headline-cell* level; rb-025 promotes that statement to the cell-wise distributional level.

**The natural next increment is RB-041** (the manuscript fold-in of rb-025 into §model §5.5-replacement and/or §sensitivity — parallels the RB-038 manuscript fold-in pattern that landed rb-024). Alternative parallel options (all unblocked): **RB-021** (A8 N-dim uncued sweep — completes the heterogeneity thread architecturally; the only sibling §extensions subsection still unfilled); **RB-033** (A3 formal derivation in the rebuild's voice — fills §appendix-deriv-a3 stub placed by rb-017); **RB-024** (C1 closed-form CF<0.5 boundary derivation — would let §results-c1 replace `frac<0.6 = 22%` with a closed-form predicate). RB-041 is preferred because it converts the rb-025 sim numbers into manuscript prose with stable label set, parallel to the rb-024 manuscript fold-in of rb-023.

### Wiki cross-references

Wiki sweep performed for keywords {cell-wise sign-flip, ∂VDA/∂ρ, amplification incidence, cost-dominant vs benefit-dominant regime, criterion devaluation, concentration-cost relaxation, A1 two-channel decomposition}. All citations needed (CohenMaunsell2009, RuffCohen2016, Srinath2021) already wired from rb-008/rb-009; Slepian 1962 and Tong 1990 still by full bibliographic reference (math-methods gap inherited from rb-008/rb-014/rb-017/rb-018 per reviewer CR-035/CR-037 scope). No new `research_db/papers/` stubs added; `audit.py` not re-run (no wiki writes).

### Files written

- `Rebuild/sims/A1--vda-signflip-cellwise/run.py` (~660 lines incl. comments).
- `Rebuild/sims/A1--vda-signflip-cellwise/README.md`.
- `Rebuild/sims/A1--vda-signflip-cellwise/output/results.json` (~47 KB; pre-embed sha256 `489c7c25…`).
- `Rebuild/sims/A1--vda-signflip-cellwise/output/figures/` — `vda_delta_distribution.png`, `signflip_by_r.png`, `vda_sign_heatmap_v5.png`.
- `Rebuild/CLAIM_LEDGER.md` — top reconcile paragraph updated for rb-025; A1 row backing column extended with the new sim block.
- `Rebuild/REBUILD_BACKLOG.md` — RB-025 status → done with notes block; new RB-041 task queued (manuscript fold-in).
- `Rebuild/rebuilder_state.json` — `runs_completed` → 25, `last_run_id` / `last_run_ended` updated, `done_task_ids` adds RB-025, `open_task_ids` removes RB-025 and adds RB-041, `sims_written` adds "RB-025", `rb_025_sim_digest` = `489c7c25…` added, `next_task_id_counter` → 42.
- `Rebuild/conversations/2026-05-29-rebuilder-a1-vda-signflip-cellwise.md` (NEW).

---

## rb-024 — 2026-05-29 — Fold rb-023 r†(v;ρ) closed form into manuscript (manuscript) — DONE

- **Run id:** `rb-024-2026-05-29`
- **Prompt version:** 0.2
- **Task worked:** RB-038 (manuscript fold-in of the rb-023 closed-form r†(v;ρ) derivation; prereq RB-026 done at rb-023).
- **Output kind:** manuscript.
- **Claims touched:** C2 (CONFIRMED-UNDER-ATTACK, primary); cross-references A1 (rho-channel concentration-cost relaxation, §model and §appendix-deriv-a1).
- **Status:** done.

### Headline thing built

A self-contained §appendix-deriv-c2 subsection in [Rebuild/manuscript/sections/appendix.tex](Rebuild/manuscript/sections/appendix.tex) (≈215 LaTeX lines, replacing the 6-line stub) plus a rewrite of two paragraphs in [Rebuild/manuscript/sections/results.tex](Rebuild/manuscript/sections/results.tex) §results-c2. The appendix subsection is the manuscript fold-in of the rb-023 derivation `Rebuild/derivations/C2--non-monotonic-vda-rho.md` and parallels the structure of §appendix-c5 (rb-018):

1. **Setup at the boundary.** $d_c = d_u = d'_{\text{base}}$ at $\alpha = 1/N$ regardless of $(r, \rho)$; ρ-aware asymmetric P3 criterion optimum $(c^\star_c(\rho), c^\star_u(\rho))$ via the joint argmax of Eq. eq:c2-boundary-crit. Headline-cell numerics quoted directly: at $(N, V, v) = (4, 0.5, 5)$, variant A, the $\rho = 0$ optimum $(0.10, 1.75)$ shifts to $(0.05, 1.80)$ at $\rho = 0.2$ (cued criterion drops 0.05 — more liberal under correlated FAs; uncued criterion climbs 0.05 — more conservative against the cross-location no-FA joint event).

2. **The ρ-aware d-gradient integrals.** Eqs. eq:c2-Ic and eq:c2-Iu give the two 1-D Gauss-Hermite integrals $I_c(b_c, b_u; \rho, N)$ and $I_u(b_c, b_u; \rho, N)$ derived by differentiating $P_{\text{no-fa}}(\rho)$ under the integral (dominated convergence) with the inner $b$-shift contributing the standard $1/\sqrt{1-\rho}$ factor. Both reduce to the independent products $I_c^0 = \varphi(b_c)\Phi(b_u)^{N-1}$ and $I_u^0 = \Phi(b_c)\Phi(b_u)^{N-2}\varphi(b_u)$ at $\rho = 0$.

3. **Boundary FOC.** Eq. eq:c2-rho-foc gives the asymmetric boundary FOC at $\alpha = 1/N^+$ with $\rho$-aware coefficients $K_c(v;\rho), K_u(v;\rho)$ (Eqs. eq:c2-Kc-rho / eq:c2-Ku-rho); the change-trial $\varphi$ summands carry $\rho$ only through $c_i^\star(\rho)$, the no-FA $I_c, I_u$ summands carry the full $\rho$ dependence of the correlated quadrature.

4. **Boxed Proposition prop:r-dagger-rho** stating $r^\dagger(v;\rho) = K_u(v;\rho) / [(N-1) K_c(v;\rho)]$ (Eq. eq:r-dagger-rho), with a short proof from dividing out the strictly positive prefactor in Eq. eq:c2-rho-foc and using $\beta/\gamma = r$ (which holds across the whole conservation family of §extensions-A3). Proof closes with the 6/6 boundary-FD sign-flip witness from rb-023's `verify_C2_rho/verify.py`.

5. **Structural ρ → 0 recovery.** Term-by-term collapse: $I_c \to I_c^0$, $I_u \to I_u^0$, criterion optimum (eq:c2-boundary-crit) → asymmetric P3 optimum of §results-c2; $K_c(v;0) = K_c(v)$ and $K_u(v;0) = K_u(v)$ of Eqs. eq:K-c / eq:K-u; Eq. eq:r-dagger-rho reduces to Eq. eq:r-dagger. Recovery is *structural*, not just numerical; the numerical verification (max|Δr†| ≤ 5e-4 across $v \in \{1,2,3,5,8,10\}$, binary at $v = 2$) is the C_GRID quantisation-noise floor.

6. **Drift Table tab:r-dagger-rho-drift** (6 rows $v \in \{1, 2, 3, 5, 8, 10\}$ at the headline cell): $\Delta r^\dagger(v) = r^\dagger(v; 0.2) - r^\dagger(v; 0)$, $\%\Delta r^\dagger$, and the sign-match column against tab:rho-sensitivity's empirical $\Delta r^\star$. All 5/5 sign-matches at $v \ne 1$; drift fraction +3% at $v = 1$ → +30% at $v = 8$.

7. **Two findings paragraph.** *Sign*: $\Delta r^\dagger > 0$ universally; the escape-band lower edge widens under correlation across the full $v$-family. *Magnitude*: percentage drift largest at $v = 8$ (+30%), smallest at $v = 1$ (+3%); the absolute lower-edge drift $\le 0.014$, while the empirical peak drift ranges up to 0.13 at $v = 2$ — the peak responds also to the matching upward drift of $r^\dagger(1; \rho)$ (widening the escape band's upper edge) and to changes inside the band; the peak-location closed form remains a queued extension.

8. **Mechanistic mirror to A1.** The $I_c, I_u$ of Eqs. eq:c2-Ic / eq:c2-Iu are the gradient analogue of the orthant decomposition behind the "three levers, not two" reframe of §model-three-levers. §appendix-deriv-a1 pins the CF-versus-ρ side of the A1 two-channel decomposition (§4.2 of `Rebuild/derivations/A1--rho-channel.md`) via Slepian monotonicity; §appendix-deriv-c2 pins the lower-edge $r^\dagger$ component of $\partial\text{VDA}/\partial\rho$ — the rebuild now has analytic loci for both channels.

9. **Scope and reproducibility.** Local statement (lower edge only); equicorrelated noise only; variant A only (variant B is a mechanical $\CR$ substitution); conservation-family inheritance via the boundary $p$-invariance of §extensions-A3 Proposition prop:r-dagger-invariance at $\rho = 0$; joint $(p, \rho > 0)$ band is future work. Verification script `Rebuild/derivations/verify_C2_rho/verify.py` deterministic; output.json sha256 `ddbd3988e0253fde2cfae5906ca2749cda872d1382055b3d243b4b7c6a0678dc`. Companion long-form derivation `Rebuild/derivations/C2--non-monotonic-vda-rho.md` cited as the source of elided algebraic steps.

### §results-c2 paragraph rewrites

- **Forward-reference paragraph after Table tab:rho-sensitivity** (was: "reported sensitivity, not yet a closed-form prediction... queued as a derivation increment (RB-026)"). Now: a citing paragraph that reports the closed-form drift inline (drift fraction range, 5/5 sign-match), explains the lower-edge-cannot-exceed-peak mechanism, and cites Section sec:appendix-deriv-c2 / Proposition prop:r-dagger-rho / Table tab:r-dagger-rho-drift by reference. The directional statement at the bottom of the paragraph (A1 lever enhances VDA in benefit-dominant high-value corner; §5.5 framing retracted along this axis) is preserved verbatim.

- **§scope paragraph** (was: "The closed-form $\rdagger(\val; \corr > 0)$ derivation is similarly deferred (RB-026): the upward drift of $r^\star$ in $\corr$ in Table~\ref{tab:rho-sensitivity} is reported as an empirical observation, not as a prediction of a closed form."). Now: a citing sentence pointing at Section sec:appendix-deriv-c2 / Proposition prop:r-dagger-rho / Table tab:r-dagger-rho-drift; the peak-location drift remains data, as before.

### How it connects to the ledger

- **Discharges:** the C2 row's "rb-023 ρ-aware closed form can be folded into the §results-c2 forward-reference paragraph in a follow-up manuscript edit or placed as a self-contained §appendix-derivation-C2 increment" license (CLAIM_LEDGER.md C2 row tail at rb-023; backlog RB-038). C2 row is now fully wired: sim (rb-004), derivation (rb-023), manuscript-results (rb-006), AND manuscript-appendix (rb-024).
- **No label drift in the live ledger** (10/10 verdict labels still match the §3 table of `agents/paper_rebuilder_prompt.md` v0.2).

### Simulation / verification evidence

No new sim run (this is a manuscript-prose increment). All numerical content folded into the manuscript draws from rb-023's `verify_C2_rho/output.json` (sha256 `ddbd3988e0253fde2cfae5906ca2749cda872d1382055b3d243b4b7c6a0678dc`) and rb-006's `Rebuild/sims/C2--vda-vs-r-vfamily/output/results.json` (sha256 `09ecef3c2c5a101820951398ed7d6e67d3398aede80c5f0bddfa42b6224fd783`). No model edits; pre-existing recovery contracts unchanged.

### Build details

4-pass pdflatex+bibtex clean. Pass 1: OK, no errors, 41 pages (resolves \label{sec:appendix-deriv-c2} into .aux). bibtex: no new entries (Slepian 1962, Tong 1990, CohenMaunsell2009, RuffCohen2016, Srinath2021 all already wired). Pass 2: 43 pages (cross-refs to the new \label resolve), undefined-ref warning expected (the \ref{tab:r-dagger-rho-drift} and \ref{prop:r-dagger-rho} cited from §results-c2 are now in .aux but used cross-referentially). Pass 3: 0 undefined references. Pass 4: byte-identical to pass 3 — settled. Final PDF: 43 pages / **2,413,318 bytes** (was 40 / 2,379,430 at rb-022 = +3 pages, +33,888 bytes — three new propositions/equations + one new table + ≈215 LaTeX lines).

### What the manuscript can now say

At the C2-row strength ceiling, with the new §appendix-deriv-c2 subsection backing it:

> The ρ-aware closed form
> $$
>   r^\dagger(v; \rho) \;=\; \frac{K_u(v;\rho)}{(N-1)\,K_c(v;\rho)}
> $$
> (Proposition prop:r-dagger-rho; Equation eq:r-dagger-rho), evaluated at the C2 headline cell, predicts $\Delta r^\dagger(v) > 0$ at every $v \in \{1, 2, 3, 5, 8, 10\}$, with the closed-form sign matching the empirical peak-drift sign at all five $v \ne 1$ rows (Table tab:r-dagger-rho-drift). The lower edge cannot exceed the peak; the analytic upward drift of $r^\dagger(v;\rho)$ is therefore the mechanistic substrate of the empirical upward drift of $r^\star(v;\rho)$ reported in Table tab:rho-sensitivity. The original paper's §5.5 framing of independence as an *upper bound on VDA* is retracted along this axis, consistent with the A1 row of CLAIM_LEDGER.

It does **not** yet license:

- (a) a closed form for the peak location $r^\star(v;\rho)$ — Proposition prop:r-dagger-rho pins the lower edge only;
- (b) a variant-B statement — that requires the mechanical $\CR$ substitution in Eqs. eq:c2-Kc-rho / eq:c2-Ku-rho and is left as a sensitivity probe (the §scope paragraph notes this);
- (c) a joint $(p, \rho > 0)$ band — the conservation-family invariance of §extensions-A3 Proposition prop:r-dagger-invariance applies at $\rho = 0$ only; the $(p, \rho > 0)$ band remains future work;
- (d) a closed-form magnitude statement $d r^\dagger / d\rho$ as a function of $v$ — the drift is reported at $\rho \in \{0, 0.2\}$ only; a finer ρ-grid bracketing is queued as RB-039.

### Why the next run should care

This run **closes the manuscript loop on the rb-023 derivation**: the rebuild now has a manuscript subsection for both channels of the A1 two-channel sign-flip decomposition (criterion devaluation in §appendix-deriv-a1, lower-edge $r^\dagger$ drift in §appendix-deriv-c2). The C2 row is the first claim in the rebuild that is fully covered from sim → derivation → manuscript-results → manuscript-appendix.

**The natural next increment is RB-021** (A8 N-dim uncued sweep, prereq RB-017 done at rb-020) — completes the heterogeneity thread architecturally: §extensions-A3 done (rb-017), §extensions-A2 done (rb-022), §extensions-A8 still queued (the only sibling subsection in `extensions.tex` not yet drafted). Alternative parallel options (all unblocked): **RB-025** (A1 cell-wise sign-flip sim, the empirical companion to this run's analytic lower-edge statement — generalises rb-002's headline-cell observation across the broader 4,410-cell sweep parallel to rb-003's CF Δ-distribution); **RB-033** (A3 formal derivation in the rebuild's voice, fills the §appendix-deriv-a3 stub placed by rb-017); **RB-039** (finer ρ-grid extension of the rb-023 verify_C2_rho/verify.py — would let the manuscript replace the single-step Δr†(0.2) − Δr†(0) drift with a closer characterisation of dr†/dρ as a function of v); **RB-024** (C1 closed-form CF<0.5 boundary derivation).

RB-021 is preferred — it lands the last extension subsection before the structural manuscript work shifts toward the bookends (abstract, intro, limitations).

### Wiki cross-references

Wiki sweep performed for keywords {ρ-aware closed form, equicorrelated d-gradient, one-factor Gauss-Hermite, escape-band lower edge, A1 channel decomposition, criterion devaluation, concentration-cost relaxation, asymmetric P3 criterion, boundary FOC, Slepian monotonicity, two-channel sign-flip}. All citations needed by the appendix subsection (CohenMaunsell2009, RuffCohen2016, Srinath2021) already wired from rb-008/rb-009 cross-references in §model; Slepian 1962 and Tong 1990 cited by full bibliographic reference in §appendix-deriv-a1 (math-methods gap inherited from rb-008/rb-014/rb-017/rb-018 per reviewer CR-035/CR-037 scope). No new research_db/papers/ stubs added. `audit.py` not re-run (no wiki writes).

### Files written

- `Rebuild/manuscript/sections/appendix.tex` — §appendix-deriv-c2 stub replaced with ≈215-line subsection (Proposition prop:r-dagger-rho, Equations eq:c2-Ic / eq:c2-Iu / eq:c2-rho-foc / eq:c2-Kc-rho / eq:c2-Ku-rho / eq:c2-boundary-crit / eq:r-dagger-rho, Table tab:r-dagger-rho-drift).
- `Rebuild/manuscript/sections/results.tex` — §results-c2 forward-reference paragraph (the "reported sensitivity, not yet a closed-form prediction... queued as a derivation increment (RB-026)" block after Table tab:rho-sensitivity) rewritten as a citing paragraph; §scope paragraph (the "closed-form $\rdagger(\val; \corr > 0)$ derivation is similarly deferred (RB-026)" sentence) rewritten as a citing sentence.
- `Rebuild/manuscript/main.pdf` — 43 pages / 2,413,318 bytes (regenerated, 4-pass settled).
- `Rebuild/CLAIM_LEDGER.md` — top reconcile paragraph updated for rb-024; C2 row backing column tail extended with the §appendix-deriv-c2 subsection block.
- `Rebuild/REBUILD_BACKLOG.md` — RB-038 status → done with notes block.
- `Rebuild/rebuilder_state.json` — `runs_completed` → 24, `last_run_id` / `last_run_ended` updated, `done_task_ids` adds RB-038, `open_task_ids` removes RB-038, `manuscript_sections_drafted` adds "RB-038 (§appendix-deriv-C2)", `rb_024_manuscript_pdf_bytes` = 2413318 added.
- `Rebuild/conversations/2026-05-29-rebuilder-c2-rho-manuscript-foldin.md` (NEW).

---

## rb-023 — 2026-05-26 — C2 r†(v;ρ) closed-form derivation (derivation) — DONE

- **Run id:** `rb-023-2026-05-26`
- **Prompt version:** 0.2
- **Task worked:** RB-026 (independent re-derivation of r†(v) in the rebuild's voice + ρ>0 extension; prereq RB-006 done at rb-004).
- **Output kind:** derivation.
- **Claims touched:** C2 (CONFIRMED-UNDER-ATTACK, primary); strengthens A1 row's `Rebuild/derivations/A1--rho-channel.md` §4.2 channel (b) (concentration-cost relaxation) by promoting it from an empirical sign-flip observation to a closed-form lower-edge predictor.
- **Status:** done.

### Headline thing built

`Rebuild/derivations/C2--non-monotonic-vda-rho.md` (~36 KB, 7 sections + Verification block + Extensions) plus companion verification script `Rebuild/derivations/verify_C2_rho/verify.py` and `output.json` (sha256 `ddbd3988e0253fde2cfae5906ca2749cda872d1382055b3d243b4b7c6a0678dc`, deterministic, ~1 s wall-clock).

Structure:

1. **§1 Setup + locus.** Boundary configuration $(d_c, d_u) = (d'_{\text{base}}, d'_{\text{base}})$ at $\alpha = 1/N$ regardless of $(r, \rho)$ (Eq. 1.3); asymmetric P3 criterion optimum $(c^{\star}_c(v, V, N, \mathrm{CR}, \rho), c^{\star}_u(\rho))$ jointly maximised over `C_GRID × C_GRID` (Eq. 1.4); the explicit booking of the no-FA product as the sole locus of $\rho$ dependence at the boundary FOC (mirrors `Rebuild/derivations/A1--rho-channel.md` §1.2).

2. **§2 $\rho = 0$ re-derivation in rebuild voice.** Chain rule on $\mathbb E[R]$ with the asymmetric P3 booking (Eqs. 2.1–2.6 the inherited derivation glosses over: the products $I_c^{0} = \varphi(b_c)\Phi(b_u)^{N-1}$ and $I_u^{0} = \Phi(b_c)\Phi(b_u)^{N-2}\varphi(b_u)$ are not equal in general at asymmetric criteria); boundary-FOC sign (Eq. 2.10); **Proposition 2.1 ($r^{\dagger}(v) = K_u(v)/[(N-1)\,K_c(v)]$)** with $K_c, K_u$ defined in Eqs. 2.8–2.9; recovery contract to `Critique/derivations/C2--non-monotonic-vda.md` Eq. 2.5 (algebraically equivalent modulo (N-1)-factor placement).

3. **§3 $\rho > 0$ extension.** Derivatives of $P_{\text{no-fa}}(\rho)$ under the integral by dominated convergence (Eqs. 3.2–3.3); one-factor Gauss-Hermite reduction giving the ρ-aware $d$-gradient integrals $I_c(b_c, b_u; \rho, N)$ and $I_u(b_c, b_u; \rho, N)$ (Eqs. 3.4–3.5, same `(_GH_Z, _GH_W)` machinery `Rebuild/model/core.py:p_no_fa_grid` uses); ρ-aware P3 criterion optimum (Eq. 3.6); $K_c(v; \rho), K_u(v; \rho)$ (Eqs. 3.8–3.9, boxed Eq. 3.7).

4. **§4 The closed form $r^{\dagger}(v; \rho)$.** **Boxed Proposition 4.1** stating $r^{\dagger}(v; \rho) = K_u(v; \rho) / [(N-1)\,K_c(v; \rho)]$ (Eq. 4.1) with the explicit ratio over the asymmetric P3 criteria. §4.1 ρ→0 recovery: structural (Eq. 4.2 collapses $I_c, I_u$ term-by-term) plus numerical (max\|Δ\| ≤ 5 × 10⁻⁴ on C_GRID-quantised criteria, binary at v=2). §4.2 What (4.1) does and doesn't predict: lower edge of the escape band, not the peak location $r^{\star}(v;\rho)$.

5. **§5 Numerical realisation at the headline cell.** Three findings:
   - **(5.1) ρ=0 recovery.** $r^{\dagger}_{\text{rb-026}}(v;0)$ vs `rb-006 r_dagger(v)` at $v \in \{1, 2, 3, 5, 8, 10\}$: max\|Δ\| = 4.9 × 10⁻⁴; v=2 exact binary match (both implementations land on grid optimum $(c^{\star}_c, c^{\star}_u) = (0.25, 1.30)$). Residual is `C_GRID Δc=0.05` quantisation, not a formula discrepancy.
   - **(5.2) Drift prediction.** $\Delta r^{\dagger}(v) := r^{\dagger}(v; 0.2) − r^{\dagger}(v; 0)$ is **positive at every $v$**, including $v=1$ (the P2 reference): +3.0% at v=1 → +29.7% at v=8. The escape threshold drifts *upward* under correlation across the entire $v$ family — the regime in which P1 is stuck at uniform *widens* as $\rho$ grows. All 5/5 closed-form drift signs match the rb-006 empirical $\Delta r^{\star}$ sign at $v \in \{2, 3, 5, 8, 10\}$.
   - **(5.3) Boundary FD sign-flip.** A one-sided FD step at $r = r^{\dagger}(v; \rho) \pm 0.05$, $\Delta\alpha = 10^{-3}$, confirms $\partial\mathbb E[R]/\partial\alpha|_{1/N^{+}}$ flips from −1 to +1 at every $(v, \rho) \in \{1, 2, 3\} \times \{0, 0.2\}$ probe — 6/6 flips. ($v \in \{5, 8, 10\}$ omitted because $r^{\dagger} < 0.06$ falls below the α-grid stencil floor for the FD step.)
   - **(5.4) Structural mirror to A1 §4.2.** The two ρ-aware $d$-gradient integrals $I_c, I_u$ are exactly the *channel (b)* (concentration-cost relaxation under correlation) of `Rebuild/derivations/A1--rho-channel.md` §4.2; the closed-form $r^{\dagger}(v; \rho)$ here makes that channel **analytic** — what was an empirical sign-flip observation in rb-002 / rb-004 / rb-010 now has a closed-form lower-edge predictor.

6. **§6 Scope.** Local statement (peak location is consistent with $r^{\dagger}$ drift, not directly predicted); equicorrelation specificity (Slepian's monotonicity is for orthant probabilities, not their gradients, hence the §5.4 5/5 sign-match is empirical not propositional); ρ ∈ [0, 0.4] envelope; C_GRID quantisation; variant A only (variant B mechanical substitution); A3 additive (rb-016 establishes ρ=0 $p$-invariance to FP identity; ρ>0 extension queued); A2 heterogeneity (rb-021 shows C2 peak invariance to ≤ 1e-5 across spread ≤ 0.3, so (4.1) is the spread-zero limit).

7. **§7 References.** Slepian 1962, Tong 1990 cited by full bibliographic reference (math-methods gap inherited from rb-008/rb-014/rb-017/rb-018, out of rebuilder scope per reviewer CR-035/CR-037); CohenMaunsell2009, RuffCohen2016, Srinath2021 already wired from rb-008/rb-009.

8. **Verification performed block.** Structural ρ→0 recovery (Eq. 4.2 term-by-term); numerical ρ→0 recovery (max\|Δ\| ≤ 5e-4 at v ∈ {1,...,10}); drift sign-match 5/5; boundary FD sign-flip 6/6; reproducibility (deterministic, byte-identical reruns produce same `output.json` sha256).

9. **Extensions.** Closed-form $r^{\star}(v; \rho)$ (peak location, not just escape edge); Slepian-analogue for $I_c, I_u$ promoting the §5.2 empirical 5/5 to a proposition; variant B mechanical substitution; A3 conservation extension to $\rho > 0$; A2 heterogeneous-$r_i$ perturbation $O(\mathrm{Var}(\boldsymbol{r}))$.

### How it connects to the ledger

- **Discharges:** the C2 row's `closed-form r†(v; ρ) derivation pending` license. The C2 row's rebuilt strength gains the ρ-aware closed form Proposition 4.1, the structural ρ→0 collapse to Proposition 2.1, the 5/5 sign-match drift prediction, and the 6/6 boundary FD sign-flip — all numerical witness recorded in `verify_C2_rho/output.json` (sha256 `ddbd3988…`).
- **Strengthens the A1 row** (no formal label change, but the row's `§4.2 channel (b)` empirical observation now has an analytic substrate — the closed-form $r^{\dagger}(v;\rho)$ explains *where* the concentration-cost relaxation shifts the escape band's lower edge, which is the analytic-locus mechanism rb-002/rb-004/rb-010 had only as an empirical sign-flip).
- **No label drift in the live ledger** (10/10 verdict labels still match the §3 table of `agents/paper_rebuilder_prompt.md` v0.2).

### Simulation / verification evidence

- **Output:** `Rebuild/derivations/verify_C2_rho/output.json`, sha256 `ddbd3988e0253fde2cfae5906ca2749cda872d1382055b3d243b4b7c6a0678dc`.
- **Recovery:** max\|Δr†(v; 0) − r†_rb006(v)\| = 4.9 × 10⁻⁴ across $v \in \{1,2,3,5,8,10\}$ (binary at v=2); residual is `C_GRID Δc=0.05` quantisation of $(c^{\star}_c, c^{\star}_u)$ on the C_GRID, not a formula discrepancy.
- **Drift sign-match:** 5/5 at $v \in \{2,3,5,8,10\}$ (closed-form $\operatorname{sign}(\Delta r^{\dagger}) = +$ matches rb-006 empirical $\operatorname{sign}(\Delta r^{\star}) = +$ at every $v$).
- **Boundary-FD sign-flip:** 6/6 at $(v, \rho) \in \{1, 2, 3\} \times \{0, 0.2\}$ probes (the $v \in \{5,8,10\}$ rows have $r^{\dagger} < 0.06$, below the α-grid stencil floor for the chosen FD step).
- **Determinism:** byte-identical reruns produce the same `output.json` sha256.

### What the manuscript can now say

At the C2-row strength ceiling:

> The escape threshold $r^{\dagger}(v;\rho)$ — the value of $r$ below which $\alpha^{\star}_{\mathrm P_1}(r,v) = 1/N$ — admits the closed form
> $$
>   r^{\dagger}(v;\rho) \;=\; \frac{K_u(v;\rho)}{(N-1)\,K_c(v;\rho)},
> $$
> with $K_c(v;\rho), K_u(v;\rho)$ defined in Eqs. 3.8–3.9 of `Rebuild/derivations/C2--non-monotonic-vda-rho.md`. At the headline cell, $\Delta r^{\dagger}(v) := r^{\dagger}(v;0.2) − r^{\dagger}(v;0)$ is *positive* at every $v \in \{1, 2, 3, 5, 8, 10\}$ (+3.0% at v=1 → +29.7% at v=8), and the closed-form drift sign matches the empirical $\Delta r^{\star}$ sign at all 5/5 tested $v \ne 1$ (rb-006). The closed form makes A1's channel (b) (concentration-cost relaxation under correlation, `Rebuild/derivations/A1--rho-channel.md` §4.2) analytic on the lower edge of the escape band.

The manuscript section `Rebuild/manuscript/sections/results.tex` §results-c2 forward-reference paragraph (currently "deferred to the §appendix derivation queued as RB-026") can now be updated to cite `Rebuild/derivations/C2--non-monotonic-vda-rho.md` directly, OR a separate §appendix-derivation-C2 subsection can be drafted in `Rebuild/manuscript/sections/appendix.tex` (paralleling §appendix-derivation-C5). This manuscript increment is queued as **RB-038**.

### Why the next run should care

This run **lands the closed-form locus** for the A1 channel-(b) sign-flip the rebuild has been observing empirically across rb-002 (single-cell), rb-004 (v-family), rb-010 (V-v plane), and rb-021 (heterogeneous-r). The ρ-aware closed form $r^{\dagger}(v; \rho)$ is the analytic substrate for the manuscript's §model "three levers, not two" reframe: criterion devaluation (channel a) was already shown to be the dominant mechanism under correlation, but channel (b) (the concentration-cost relaxation) had been only an empirical observation. After rb-023, channel (b) has an analytic predictor — the lower edge of the escape band drifts upward in $\rho$ at every $v$.

**The natural next increment is RB-038** (manuscript fold-in of the rb-023 closed form into §results-c2 or as a new §appendix-derivation-C2 subsection), discharging the C2 row's `§results-c2 paragraph still references rb-006-only closed form` license. Alternative next priorities: RB-025 (A1 cell-wise sign-flip sim, the empirical companion to this analytic statement); RB-021 (A8 N-dim uncued sweep, completing the heterogeneity thread); RB-033 (A3 formal derivation).

### Spawned tasks

- **RB-038** — `manuscript`, medium priority — fold the rb-023 closed form into §results-c2 (a short paragraph + the §5.2 drift table) OR place as a self-contained §appendix-derivation-C2 subsection.
- **RB-039** — `simulation`, low priority — empirical ρ-band of $\Delta r^{\dagger}(v)$ at finer ρ-grid $\{0, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4\}$ for sharper dr†/dρ characterisation.
- **RB-040** — `derivation`, low priority — Slepian-analogue for $I_c, I_u$ promoting the §5.2 empirical 5/5 sign-match to a proposition.

### Wiki cross-references

- `[[cohen_maunsell2009_correlations]]` — empirical anchor for ρ ∈ [0, 0.4] envelope (already wired, cited in §6).
- `[[ruff_cohen2016_cross_area_correlations]]` — sign-dependent correlation structure motivating equicorrelation specificity scope (already wired, cited in §6).
- `[[srinath2021_attention_information_flow]]` — supra-pairwise shared-variance amplification (already wired, cited in §6).
- Slepian 1962 / Tong 1990 — math-methods gap, cited by full bibliographic reference; no research_db stub added (inherited from rb-008/rb-014/rb-017/rb-018 per reviewer CR-035/CR-037 scope).
- `audit.py` not re-run (no wiki writes).

### Files written

- `Rebuild/derivations/C2--non-monotonic-vda-rho.md` (NEW, 35,907 bytes).
- `Rebuild/derivations/verify_C2_rho/verify.py` (NEW, ~13 KB).
- `Rebuild/derivations/verify_C2_rho/output.json` (NEW, ~5 KB; sha256 `ddbd3988e0253fde2cfae5906ca2749cda872d1382055b3d243b4b7c6a0678dc`).
- `Rebuild/CLAIM_LEDGER.md` — top reconcile paragraph updated for rb-023; C2 row backing column extended with rb-023 derivation block.
- `Rebuild/REBUILD_BACKLOG.md` — RB-026 status → done with notes block; RB-038, RB-039, RB-040 spawned.
- `Rebuild/rebuilder_state.json` — `runs_completed` → 23, `derivations_written` adds RB-026, `done_task_ids` adds RB-026, `open_task_ids` reorders for the three spawned tasks, `next_task_id_counter` → 41, `rb_023_*` keys added.
- `Rebuild/conversations/2026-05-26-rebuilder-c2-rho-derivation.md` (NEW).

---

## rb-022 — 2026-05-25 — §extensions-A2 manuscript subsection (manuscript) — DONE

- **Run id:** `rb-022-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-035 (§extensions-A2 subsection in `Rebuild/manuscript/sections/extensions.tex`, sibling to §extensions-A3; prereq RB-018 done at rb-021).
- **Output kind:** manuscript.
- **Claims touched:** A2 (CONFIRMED-CONDITIONAL, primary); cross-references A1 (ρ channel, `sections/model.tex` §model-rho-channel) and A8 (rb-020 N-dim policy via `er_full_policy`).
- **Status:** done.

### Headline thing built

`Rebuild/manuscript/sections/extensions.tex` gained a full §extensions-A2 subsection (≈370 LaTeX lines, appended after the §extensions-A3 reproducibility paragraph; the file's section structure is now §extensions / §extensions-A3 / §extensions-A2 — sibling order matches the order in which the levers were wired into the rebuilt model). Contents in order:

1. **Claim restatement** at defensible CONFIRMED-CONDITIONAL strength: the inherited paper's single global $r$ premise is empirically false (V1-vs-V4 ~3× gradient; eccentricity sign-reversal; feature similarity gain; time-varying gain); the live skeptical-reviewer verdict splits A2 into between-preparation $R_1$ (adopted explicitly in §model) and within-display $R_2$ (presented as a model extension); the rebuild's claim is that within-display heterogeneity is a **bounded perturbation**, not abolition, of every headline number. Six heterogeneity citations: McAdamsMaunsell1999, ReynoldsHeeger2009, Treue1999, Carrasco2011, GhoseMaunsell2002, Sani2017 (all from research_db papers stubs, added to refs.bib this run).

2. **Heterogeneous-$r$ d$'$-map (eq:d-prime-hetero)** stating $d'_i(\alpha_i, r_i; p) = \max(d'_\text{base} + s_i [d'_\text{max} f(\alpha_i) - d'_\text{base}], 0)$ with $s_i = \beta(r_i, p)$ if $\alpha_i \ge 1/N$ else $\gamma(r_i, p)$; reduces to the inherited $(d'_c, d'_u)$ pair byte-for-byte under canonical homogeneous allocation + uniform $r$. Composes with A1 ρ channel (via `er_full_policy`'s joint no-FA integral) and A3 conservation order $p$ (via `beta_gamma(r_i, p)`). Recovery contract notes: rb-019 `test_heterogeneous_r.py` 5/5 PASS sha256 `0486921f…` (max|diff|=0.0 across 5,904 sampled cells); rb-020 `test_general_policy.py` 7/7 PASS sha256 `883ea15a…` (max|d|≤2.78e-10 across 4,530 cells at both ρ ∈ {0, 0.2}).

3. **Empirical-band paragraph + Table tab:a2-rb021-summary**: 5-test summary at the C2 headline cell (V=0.5, v=5, N=4, variant A, p=1) with linearly-distributed uncued spread $s \in \{0, 0.1, 0.2, 0.3\}$ and $\rho \in \{0, 0.2\}$. Four columns (ρ × s); rows: recovery max|ΔVDA|/max|ΔCF|, criticality ||t||, allocation ΔR (cost-dominant + benefit-dominant), C2 peak VDA*, C1 corner CF. All cell values drawn verbatim from `Rebuild/sims/A2--heterogeneous-r/output/results.json`.

4. **Four numbered findings** (each one a paragraph + cross-reference to its evidence in the table or one of the figures):
   - F1: equal-split criticality is **exactly conditional on homogeneity** — ||t||=0 at s=0; non-zero at s=0.3; ρ amplifies the criticality residual ~2× (2.6e-3 → 5.8e-3).
   - F2: allocation ΔR is **bounded by 1.48e-4** at the cost-dominant cell (V=0.5, v=2, r=0.3, α*=0.66) and **A1 ρ=0.2 suppresses by ~50%** (1.48e-4 → 7.47e-5); ΔR = 0 exactly at the benefit-dominant cued-absorption cell (V=0.5, v=5, r=0.4, α*=1). Suggestive: A1 and A2 act in the **same** suppressive direction at cost-dominant.
   - F3: **C2 peak invariance** under A2 spread at fixed ρ — peak VDA* varies by ≤1e-5 across s ∈ {0, 0.1, 0.2, 0.3}, peak r* = 0.398 fixed, and the A1 offset ΔVDA*(ρ=0.2) = 0.00158 is itself s-invariant. **A1 and A2 compose orthogonally at the C2 peak.**
   - F4: variant-B contested-CF corner (V=0.25, v=4, r=10, α=0.98) moves UP by +0.0015 (ρ=0) / +0.0016 (ρ=0.2) at s=0.3 — corner **not deepened** by A2 spread, at either ρ panel.

5. **Three figures** (copied from `Rebuild/sims/A2--heterogeneous-r/output/figures/` to `Rebuild/manuscript/figures/` with `a2_` prefix):
   - `a2_vda_curves_spread.png` (fig:a2-vda-curves-spread) — 8 overlaid VDA(r_c) curves, the F3 headline figure.
   - `a2_vda_peak_band.png` (fig:a2-vda-peak-band) — peak VDA* and peak r* vs spread, both ρ panels, the F3 invariance panel.
   - `a2_cf_contested_corner.png` (fig:a2-cf-contested-corner) — variant-B corner CF at the 4 (s, ρ) probes, the F4 figure.

6. **Scope paragraph** explicitly bounds (i) variant-B replication → RB-036 queued; (ii) larger multiplicatively-asymmetric spreads (k ∈ {1.5, 3}) → RB-037 queued; (iii) full N-dim heterogeneous-uncued sweep (the §extensions-A8 sibling subsection that hasn't been written) → RB-021 queued; (iv) closed-form $\Delta R = O(\mathrm{Var}(\boldsymbol{r}))$ derivation in the rebuild's voice → queued as a future increment.

7. **Reproducibility paragraph** citing rb-021 sha256 `22b183f942d6b1f8868848ec1143ab959afd78c72cd6d3704763eedf5713e615` (27.2 s wall-clock; deterministic), rb-019 sha256 `0486921f8a4e253a1682ee0731e52c7de800bf6c3dbb1b5e8ff3200602454c7e` (homogeneous-$r$ contract), rb-020 sha256 `883ea15af9fd069e04c05ff156d65f33a7d25278891092539c6441d2248c3d39` (N-dim full-policy contract), plus the rb-021-embedded recovery (max|ΔVDA|=2.35e-10 / max|ΔCF|=2.98e-10 over 42 cells).

### Simulation evidence (the headline narrative)

This is a manuscript-prose increment, not a sim increment. All numerical content is drawn verbatim from the rb-021 sim's `results.json` (sha256 `22b183f9…`), and every claim in the prose maps to a specific entry in the table or to one of the three figures. The pre-existing recovery contracts of the rebuilt model module are unchanged (extension is purely prose; no edits to `Rebuild/model/`). No new sim was run; no new model code was written.

### Exact manuscript claim now licensed

The rebuilt §extensions-A2 section (now in the PDF at the §extensions-A3 → §extensions-A2 sibling slot in `Rebuild/manuscript/sections/extensions.tex`) is now licensed to state at the live A2 CONFIRMED-CONDITIONAL ceiling:

> "Within-display heterogeneity admits per-location $r_i$ and breaks the equal-split exchange symmetry the homogeneous A8 result relies on. Empirically, however, this is a bounded perturbation on every headline number probed: at $V=0.5, v=5, N=4$, peak $\mathrm{VDA}$ and peak $r^\star$ are invariant to $\le 10^{-5}$ absolute under $\pm 30\%$ uncued spread at every $\rho \in \{0, 0.2\}$, and the A1 $\rho$-channel offset at the peak is itself spread-invariant — the A2 and A1 levers compose orthogonally at the C2 peak. The allocation deviation $\Delta R = R_{\mathrm{simplex-opt}} - R_{\mathrm{equal-split}}$ is bounded by $1.5\times 10^{-4}$ at the cost-dominant interior-$\alpha$ probe cell ($V=0.5, v=2, r=0.3$) and is zero exactly at the benefit-dominant cued-absorption cell ($V=0.5, v=5, r=0.4$) at every $(s, \rho)$; one suggestive asymmetry — $\rho=0.2$ suppresses the cost-dominant $\Delta R$ by $\sim 50\%$. At the rb-005 variant-B minimum-CF corner ($V=0.25, v=4, r=10$), $s=0.3$ raises $\mathrm{CF}$ by $+0.0015$ ($\rho=0$) and $+0.0016$ ($\rho=0.2$) — the contested-CF corner is not deepened by A2 spread, regardless of $\rho$." (`Rebuild/sims/A2--heterogeneous-r/`, pre-hash sha256 `22b183f9…`, 27 s wall-clock.)

It does **not** yet license:

- (a) any *variant-B* statement about the four findings — that requires RB-036, queued;
- (b) any statement about multiplicatively asymmetric uncued spreads with $k \in \{1.5, 3\}$ under $\rho$ — that requires RB-037, queued;
- (c) any N-dim full-simplex result — that requires RB-021, queued;
- (d) any closed-form $\Delta R$-vs-$\mathrm{Var}(\boldsymbol{r})$ scaling theorem — that requires a future formal derivation increment.

### Build details

- Pass 1 hit `LaTeX Error: File 'multirow.sty' not found` — TeX Live 2026basic does not include `multirow`. **Fix:** restructured the Table 4 column header to use plain `\multicolumn{2}{c}{$\corr = 0$}` and `\multicolumn{2}{c}{$\corr = 0.2$}` over a single `Test` cell label row, no `multirow` package required. Verified the same fix works for column-header span at the desired visual layout.
- After fix: pass 1 (1 LaTeX warning "Label(s) may have changed") → bibtex (6 new entries added: `mcadams_maunsell1999_v4_tuning`, `reynolds_heeger2009_normalization`, `treue_martinez_trujillo1999_feature_attention`, `carrasco2011_visual_attention_25y`, `ghose_maunsell2002_task_timing`, `sani2017_temporal_v4_gain`; 0 bibtex warnings) → pass 2 (cleared cite warnings) → pass 3 (settled) → pass 4 (byte-identical to pass 3).
- **PDF:** 40 pages / 2,379,430 bytes (was 35 pages / 2,165,118 at rb-018 = +5 pages, +214,312 bytes; matches the expected ≈+200 KB / 5 pages an additional ~370-line subsection with 3 figures + 1 table + 1 numbered display equation typically produces).
- **Diagnostics:** 0 undefined references; 0 LaTeX warnings beyond hyperref's "Token not allowed in a PDF string (Unicode)" messages on the `\Phinorm` / `\rdagger` macros inside cross-reference titles (cosmetic only, identical to rb-009/rb-017/rb-018 build outputs; no semantic effect).

### Why the next run should care

The natural successor is **RB-021** (A8 N-dim uncued allocation sweep — sibling to rb-021 the A2 sim, this time sweeping the heterogeneous-uncued simplex policy through `er_full_policy` to test whether the A8 homogeneity-optimality condition of the live verdict holds beyond the reviewer's headline cell). That sim's results would feed a §extensions-A8 subsection in the same `extensions.tex` file, completing the heterogeneity thread architecturally: §extensions-A3 done (rb-017), §extensions-A2 done (rb-022, this run), §extensions-A8 still queued.

Alternative parallel options (all unblocked):

- **RB-026** (C2 $r^\dagger(v; \rho)$ closed-form derivation, prereq RB-006 done) — promote the rb-004 $r^\dagger(v)$ to the joint $(v, \rho)$ form via the same one-factor Gauss-Hermite reduction the rb-001 A1 channel and the rb-014 C4 derivation already use.
- **RB-033** (A3 formal derivation in the rebuild's voice, prereq RB-019 done) — fills the §appendix-deriv-a3 stub.
- **RB-024** (closed-form CF<0.5 boundary, prereq RB-005 done) — sharpen the empirical 22% frac<0.6 at ρ=0.2 into a closed-form predicate over (r, V) at fixed v.
- **RB-036** (variant-B A2 replication of rb-021).
- **RB-037** (larger multiplicatively-asymmetric A2 spreads under ρ).

RB-021 is preferred — it discharges the A8 row's last queued sim license, leaving the rebuilt manuscript with the A1 + A3 + A2 + A8 lever quartet all wired AND prose-documented; the limitations / abstract / intro increments then become the remaining structural manuscript work.

### Wiki cross-references

Wiki sweep performed for keywords {within-display heterogeneity, location-specific gain, feature-similarity gain, eccentricity sign-reversal, task timing, gain modulation, equal-split criticality, exchange symmetry, simplex tangent gradient, allocation deviation, cued absorption, C2 peak invariance, variant-B contested-CF corner, criterion fraction, A1×A2 interaction, between-preparation reading}. All 6 cited papers already have research_db stubs (mcadams_maunsell1999_v4_tuning.md, reynolds_heeger2009_normalization.md, treue_martinez_trujillo1999_feature_attention.md, carrasco2011_visual_attention_25y.md, ghose_maunsell2002_task_timing.md, sani2017_temporal_v4_gain.md — all confirmed by Glob); no new wiki stubs needed; `audit.py` not re-run (no wiki writes).

---

## rb-021 — 2026-05-25 — A2 heterogeneous-r sweep (simulation) — DONE

- **Run id:** `rb-021-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-018 (A2 heterogeneous-r sweep; prereq RB-014 done at rb-019, downstream pipeline `er_full_policy` ready at rb-020).
- **Output kind:** simulation.
- **Claims touched:** A2 (CONFIRMED-CONDITIONAL, primary), composes with A1 (ρ ∈ {0, 0.2}) and A8 (homogeneity imposed in headline tests).
- **Status:** done.

### Headline thing built

`Rebuild/sims/A2--heterogeneous-r/` — the rebuild's analogue of the
reviewer's CR-048 / run-015 A2×A8 verification harness, scored end-
to-end through `er_full_policy` (rb-020) so the A1 ρ channel is
preserved at every test. Variant A primary, ρ ∈ {0, 0.2}, additive
conservation p = 1.

Five tests + recovery contract:

| # | test | result |
| --- | --- | --- |
| 0 | validation — spread=0 vs `policies()` at every (ρ, r) of 21-pt r-grid × 2 ρ = 42 cells of headline (V=0.5, v=5) | **PASS** max\|ΔVDA\| = 2.35e-10, max\|ΔCF\| = 2.98e-10, tol 1e-9 |
| 1 | criticality of equal-split at interior-α cell (V=0.5, v=2, r=0.3, α*=0.660) | ‖t‖ = 0 at spread=0; 2.6e-3 at spread=0.3 ρ=0; 5.8e-3 at spread=0.3 ρ=0.2 |
| 2 | ΔR at cost-dominant cell (V=0.5, v=2, r=0.3, α*=0.660) | 0 → 1.42e-5 → 7.10e-5 → 1.48e-4 across spread ∈ {0,0.1,0.2,0.3} at ρ=0; 0 → 0 → 2.36e-5 → 7.47e-5 at ρ=0.2 |
| 3 | ΔR at benefit-dominant cell (V=0.5, v=5, r=0.4, α*=1.000) | ΔR = 0 exactly at every (spread, ρ) |
| 4 | C2 peak (r*, VDA*) across 8 (spread, ρ) panels | peak VDA varies by ≤ 1e-5 at fixed ρ (0.07972→0.07971 at ρ=0; 0.08130→0.08130 at ρ=0.2); peak r* fixed at 0.398 every panel |
| 5 | C1 contested corner CF (V=0.25, v=4, r=10, variant B) | 0.3040 → 0.3055 (Δ+0.0015) at ρ=0; 0.2665 → 0.2681 (Δ+0.0016) at ρ=0.2 across spread ∈ {0,0.3} |

**Pre-hash sha256:** `22b183f942d6b1f8868848ec1143ab959afd78c72cd6d3704763eedf5713e615`. Deterministic — re-running the script reproduces this digest exactly (verified across two independent runs).

**Wall-clock:** 27.2 s on python3.13 / scipy 1.17.1 / numpy 2.4.4. Recovery against rb-001 (`test_recovery.py` sha256 `d3c62215…`) and rb-020 (`test_general_policy.py` sha256 `883ea15a…`) unchanged — the sim is a pure consumer of `er_full_policy`, no model edits.

Three figures landed under `output/figures/`:
- `vda_curves_spread.png` — 8 overlaid VDA(r_cued) curves (2 ρ × 4 spread), the C2 reframe headline.
- `vda_peak_band.png` — peak VDA★ and peak r★ vs spread, both ρ; the "peak invariance under spread" panel.
- `cf_contested_corner.png` — variant-B C1 corner CF vs spread, both ρ.

### Simulation evidence (the headline narrative)

Two findings beyond the reviewer's CR-048:

1. **A1 × A2 interaction at the cost-dominant cell is *suppressive*, not amplifying.** ρ=0.2 cuts the spread=0.3 allocation deviation by ~50% (1.48e-4 → 7.47e-5). The reviewer's harness was ρ=0 only, so this is novel evidence. Mechanism: at the cost-dominant interior-α cell, the joint no-FA integral under ρ>0 couples the heterogeneous d'_i partially across locations — the criterion optimum sits closer to the homogeneous one, shrinking the reward gain available from re-allocating uncued mass to higher-r_i slots.

2. **The A1 ρ-channel offset at the C2 peak is itself spread-invariant.** Peak VDA at ρ=0.2 is +0.00158 above ρ=0 at every spread ∈ {0, 0.1, 0.2, 0.3}. The two levers act orthogonally at the C2 peak, in the precise sense that ∂²VDA/∂ρ∂spread ≈ 0 there.

Recovery contract met:
- spread=0 vs `policies()`: max\|ΔVDA\| = 2.35e-10, max\|ΔCF\| = 2.98e-10 across all 42 cells (≪ 1e-9 tolerance, the rb-020 N-dim contract).
- Determinism: pre-hash sha256 stable across re-runs.
- `test_recovery.py` digest `d3c62215…` and `test_general_policy.py` digest `883ea15a…` both unchanged.

### Exact manuscript claim now licensed

The rebuilt §extensions-A2 section (queued as **RB-035**) may now
state:

> "Within-display heterogeneity admits per-location r_i and breaks the
> exchange symmetry the homogeneous A8 result relies on. Empirically,
> however, this is a bounded perturbation on every headline number:
> across ±30% uncued spread at the C2 headline cell (V=0.5, v=5, N=4,
> variant A), peak VDA and peak r* are invariant to ≤ 1e-5 absolute
> at every ρ ∈ {0, 0.2}, and the A1 ρ-channel offset at the peak is
> itself spread-invariant — the A2 and A1 levers compose orthogonally
> at the C2 peak. The allocation deviation ΔR = R(simplex-opt) −
> R(equal-split) is bounded by 1.5e-4 at the cost-dominant interior-α
> cell (V=0.5, v=2, r=0.3) and 0 exactly at the benefit-dominant
> cued-absorption cell (V=0.5, v=5, r=0.4) at every (spread, ρ); one
> suggestive asymmetry — ρ=0.2 suppresses the cost-dominant ΔR by
> ~50%. At the rb-005 variant-B minimum-CF corner (V=0.25, v=4, r=10),
> spread=0.3 raises CF by +0.0015 (ρ=0) or +0.0016 (ρ=0.2) — the
> contested-CF corner is not deepened by A2 spread, regardless of
> ρ. (`Rebuild/sims/A2--heterogeneous-r/`, pre-hash sha256
> `22b183f9…`, 27 s wall-clock.)"

It does **not** yet license:
- (a) any *variant-B* statement about the A1×A2 cost-dominant ΔR
  suppression — that requires RB-036, queued;
- (b) any statement about multiplicatively asymmetric uncued spreads
  with k ∈ {1.5, 3} under ρ — that requires RB-037, queued;
- (c) any *manuscript prose* — that is RB-035, queued.

### Why the next run should care

The natural successor is **RB-035** — drafting the manuscript
§extensions-A2 subsection in `Rebuild/manuscript/sections/extensions.tex`
(sibling to the §extensions-A3 subsection that landed in rb-017).
The §extensions section file already exists; RB-035 fills a new
subsection in the rebuild's voice, citing the rb-021 sim's five
findings + three figures and the rb-019 (`d_prime_hetero`) + rb-020
(`er_full_policy`) model wiring. This completes the A2 thread (model
→ sim → manuscript), parallel to how the A3 thread completed
(model rb-015 → sim rb-016 → manuscript rb-017).

Alternative parallel options (all unblocked): **RB-021** (A8 N-dim
uncued sweep — the A8 analogue of rb-021, scoring policies on the
full heterogeneous-uncued simplex through `er_full_policy`, tests
whether the A8 homogeneity-optimality condition holds beyond the
reviewer's headline cell), **RB-024** (C1 closed-form CF<0.5
boundary, prereq RB-005 done), **RB-026** (C2 r†(v;ρ) closed form,
prereq RB-006 done), **RB-033** (A3 formal derivation, prereq
RB-019 done).

RB-035 is preferred — it completes the A2 thread and discharges the
A2 row's last queued license, leaving the rebuilt manuscript with
the A1 + A3 + A2 levers all wired AND prose-documented; A8 sim and
its manuscript subsection then become the remaining structural
increments.

### Wiki cross-references

Wiki sweep performed for keywords {heterogeneous r, within-display
heterogeneity, A2×A8 interaction, tangent gradient on simplex,
allocation deviation, equal-split criticality, cued absorption,
value-weight inequality, anti-cue, criterion fraction, correlated
noise, equicorrelated Gaussian}. No new `research_db/papers/` stubs
added — the citations needed are inherited from prior rb runs
(McAdams-Maunsell 1999, Reynolds-Heeger 2009, Treue 1999, Carrasco
2011, Sani 2017, Ghose-Maunsell 2002 — all in
`Critique/verdicts/A2--single-global-r.md`'s evidence dossier
already mapped to research_db papers/ stubs via earlier reviewer
runs; no new entries needed for the rb-021 sim because it is a
theorem of the rebuilt model's own definitions + the reviewer's
inherited substrate). `audit.py` not re-run (no wiki writes).

---

## rb-020 — 2026-05-25 — A8 N-dim uncued allocation policy/optimiser (model increment) — DONE

- **Run id:** `rb-020-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-017 (A8 N-dim uncued allocation policy/optimiser; prereq RB-014 done at rb-019).
- **Output kind:** model.
- **Claims touched:** A8 (CONFIRMED-CONDITIONAL, primary; per the live verdict `Critique/verdicts/A8--heterogeneous-uncued.md`); composes with A2 (RB-014 `d_prime_hetero`) and A3 (conservation order `p` propagates) and A1 (ρ channel preserved through the joint no-FA integral).
- **Status:** done.

### Headline thing built

The rebuilt model module gained a **fourth extension axis (A8)** —
N-dim heterogeneous allocation scoring. Three new public functions in
`Rebuild/model/core.py`, re-exported through `Rebuild/model/__init__.py`:

1. `optimal_ER_general(d_vec, wu_vec, n_vec, CR, rho, max_sweeps=80)` —
   the rho-aware grouped-criterion optimiser. G is the number of
   distinct (d', wu) groups; sum(n_vec) = N total locations.
   - **G = 1**: exact 1-D argmax over `C_GRID`; method `"grid_1d"`.
   - **G = 2**: exact 2-D argmax over `C_GRID × C_GRID` with `n_g`
     exponents; method `"grid_2d"`. Same machinery as `optimal_R`,
     just generalised to admit `n_g ≠ {1, N-1}`.
   - **G ≥ 3**: multi-restart coordinate ascent from `2^G + 1` seeds
     (per-group HR-side standalone argmax × per-group no-FA-side
     standalone argmax + the all-zero seed); each restart sweeps
     1-D-per-group exact-argmax until criteria stop changing; method
     `"coord_ascent_multi_restart"`.

   The rho channel is preserved end-to-end: at rho > 0 each group's
   `(1 - FAR(c_g, z))^{n_g}` is precomputed on the `(n_c, nq)` grid via
   the one-factor reduction
   `Phi((c_g + d_g/2 - sqrt(rho) z)/sqrt(1-rho))`, and the joint no-FA
   integral is the rho-aware product `INT prod_g (...)^{n_g} phi(z) dz`
   evaluated with the same `(_GH_Z, _GH_W)` 64-node Gauss-Hermite
   quadrature `p_no_fa_grid` uses. At rho = 0 the integrand factorises
   and the optimiser shortcuts to the 1-D `(1 - FAR(c_g))^{n_g}` form
   (no GH allocation), matching the homogeneous `optimal_R` operand
   order.

2. `er_full_policy(alloc, valid, v, r_vec, cell)` — full-policy driver
   that composes `optimal_ER_general` with `d_prime_hetero` (rb-019).
   Accepts an N-vector `alloc` on the simplex (slot 0 = cued by
   convention), an N-vector `valid` on the simplex (slot 0 carries V,
   uncued can be heterogeneous), the cued value `v`, an N-vector OR
   scalar `r_vec`, and a `HeadlineCell` carrying `(N, d_max, f0,
   h_name, variant, rho, cons_p)`. Groups locations by `(d, wu)`
   rounded to 9 dp (same tolerance the reviewer's A8 substrate uses),
   passes the group tuple to `optimal_ER_general`, returns a dict with
   `R`, `d_arr`, `wu_arr`, `CR`, `groups`, `c_vals`, `c_idx`, `method`,
   `N`.

3. `homogeneous_validity(V, N)` — convenience to build the canonical
   homogeneous validity vector `(V, (1-V)/(N-1), ..., (1-V)/(N-1))`.
   Mirrors `canonical_alloc(alpha, N)` from rb-019.

Plus two private helpers: `_hr_omf_grids(d)` (per-group HR and
(1 - FAR) vectors on `C_GRID`) and `_omf_grid_correlated(d, rho)` (the
`(n_c, nq)` rho > 0 quadrature grid).

The lifted machinery is the reviewer's A8 grouped-criterion optimiser
(`Critique/replications/A8--heterogeneous-uncued/run.py`, CR-036,
run-012, validated by the A8 verdict) with three structural extensions
in the rebuild's voice:

- **rho channel** preserved — the reviewer's A8 substrate uses ρ=0
  only; the rebuilt version inherits ρ from rb-001's A1 machinery.
- **conservation order `p`** preserved — the reviewer's A8 substrate
  uses additive β+γ=2 only; the rebuilt version threads
  `cell.cons_p` through `d_prime_hetero(..., p)`.
- **wider criterion grid** — the rebuilt module's
  `C_GRID = [-3, 3] step 0.05` (121 pts) replaces the reviewer's
  `[-2.5, 2.5] step 0.05` (101 pts). Identical algorithm, larger
  search space.

### Simulation evidence (the recovery contract)

`Rebuild/model/tests/test_general_policy.py` — **7/7 PASS, sha256
`883ea15af9fd069e04c05ff156d65f33a7d25278891092539c6441d2248c3d39`**.
Output: `Rebuild/model/tests/general_policy_output.json` (5.3 KB JSON
summary). 9,985 evaluations total across:

| TEST | what it checks | n_cells | max\|d\| | tol | result |
| --- | --- | --- | --- | --- | --- |
| 1 | ρ=0 recovery vs legacy `optimal_R`, variant A, p=1, full α × {r=5} × {V=3} × {v=2} | 4,530 | 2.77e-10 | 1e-9 | PASS |
| 2 | ρ=0.2 recovery (engages GH-64 on both sides), same grid | 4,530 | 2.78e-10 | 1e-9 | PASS |
| 3 | variant B (CR=1) sanity at headline cell, α grid × ρ ∈ {0, 0.2} | 302 | 1.19e-10 | 1e-9 | PASS |
| 4 | conservation family p ∈ {0, 0.5, 1.0} threading, ρ=0, variant A | 453 | 2.11e-10 | 1e-9 | PASS |
| 5 | grouping/method check (G=1 grid_1d; alpha=1/N + V≠1/N → G=2 grid_2d; alpha=0.5 → G=2 grid_2d) | 3 | — | — | PASS |
| 6 | `r_vec = [r,r,r,r]` scalar-broadcast equivalence, ρ ∈ {0, 0.2} | 186 | **0.0** | 1e-9 | PASS |
| 7 | G=4 multi-restart smoke check on heterogeneous validity (0.4, 0.3, 0.2, 0.1) | 1 | — | — | PASS (R=1.849, method `coord_ascent_multi_restart`) |

The **1e-9 tolerance** (vs the rb-019 byte-for-byte `d_prime_hetero`
contract) is the **structural wu-reconstruction error** the grouped
form introduces. The general path computes the uncued term as
`n_u · wu_u = (N-1) · ((1-V)/(N-1))` in two float operations; for
`(1-V)/(N-1)` not representable (e.g. `(1-0.5)/3 = 0.16666…64`), the
reconstruction `3 · 0.16666…64 ≈ 0.4999…996` does not bit-match the
legacy `(1-V)` literal. The reward is off by ULP × cell-value, giving
the observed ~3e-10 across 4,530 cells. This is documented in the
test docstring and is six orders of magnitude tighter than any
reported manuscript number. **TEST 6 confirms the rb-019 byte-for-byte
contract carries through** — scalar `r` and uniform `r_vec` produce
identical `R` (max|d| = 0.0 across 186 cells), so promoting r to an
N-vector introduces no additional slack.

**Pre-existing recovery tests re-run, all digests unchanged:**

- `test_recovery.py` (rb-001 A1 ρ-channel): 7/7 PASS, sha256
  `d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f`
  unchanged.
- `test_conservation_family.py` (rb-015 A3): 14/14 PASS, sha256
  `f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e`
  unchanged.
- `test_heterogeneous_r.py` (rb-019 A2): 5/5 PASS, sha256
  `0486921f8a4e253a1682ee0731e52c7de800bf6c3dbb1b5e8ff3200602454c7e`
  unchanged.

The rb-020 increment is **purely additive** — no behavioural change to
`policies`, `optimal_R`, `p_no_fa_grid`, `p_no_fa_point`,
`d_prime_asym`, `d_prime_hetero`, or `beta_gamma`. Every existing sim,
test, and manuscript figure remains numerically identical.

### Exact manuscript claim now licensed

A future §extensions-A8 subsection (or §methods generalisation
paragraph) may state:

> "We score policies over the full N-dimensional allocation simplex
> via a grouped-criterion optimiser (`er_full_policy`, §methods),
> which composes the A1 decorrelation channel, the A3 conservation
> family, and the A2 heterogeneous-r d'-map at no additional cost.
> Recovery contract: under the inherited homogeneous reduction the
> optimiser reproduces `optimal_R(d_c, d_u, ...)` to 1e-9 absolute
> across 9,060 cells of the headline α × r × V × v × variant × ρ × p
> grid (`Rebuild/model/tests/test_general_policy.py`, sha256
> `883ea15a…`)."

The §extensions-A8 quantitative content — does the A8 condition
generalise beyond the reviewer's headline-cell numerics? — is RB-021's
job. The §extensions-A2 content — do C2 non-monotonicity and C1 CF
distribution survive heterogeneous r_i? — is RB-018's job. Both sims
can now run against this driver directly.

### Why the next run should care

`er_full_policy` is the **scoring API for every queued A2/A8 sim**.
RB-018 (A2 heterogeneous-r sweep — does C2 non-monotonicity survive
heterogeneous r_i?) and RB-021 (A8 N-dim uncued sweep — does the A8
condition hold beyond the headline cell?) both depend on this driver.
The natural next pick is **RB-018**: its prereq RB-014 was already
done, the rb-019 note had implicitly deferred it pending the
downstream pipeline (now in place), and it directly answers the A2
row's headline empirical question. RB-021 is the parallel A8 option.

Lower-priority parallel options (all unblocked): RB-024 (C1 closed-
form CF<0.5 boundary), RB-026 (C2 r†(v;ρ) closed form), RB-033 (A3
formal derivation in the rebuild's voice).

### Wiki cross-references

Wiki sweep performed for keywords {N-dim allocation, grouped criterion,
coordinate ascent, equicorrelated Gaussian, joint no-false-alarm,
power-mean conservation, heterogeneous r, anti-cue, Wang-Theeuwes
suppression gradient}. No new `research_db/papers/` stubs added —
the citations needed for the §extensions-A8 prose (Wang-Theeuwes 2018
suppression gradient, etc.) were already added in rb-012/rb-013 for
the §results-C4 section, and the math-methods gap (Slepian 1962, Tong
1990, HLP 1934, Sterbenz 1974, Goldberg 1991) inherited from earlier
runs is unchanged. `audit.py` not re-run (no wiki writes).

---

---

## rb-019 — 2026-05-25 — A2 heterogeneous-r d'-map (model increment) — DONE

- **Run id:** `rb-019-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-014 (A2 heterogeneous-r model extension; prereq RB-001 done at rb-001; no new sim needed for this increment — the recovery contract IS the sim).
- **Output kind:** model.
- **Claims touched:** A2 (CONFIRMED-CONDITIONAL, primary; per the live verdict `Critique/verdicts/A2--single-global-r.md` and §3.2 of `agents/paper_rebuilder_prompt.md`). Cross-references A8 (CONFIRMED-CONDITIONAL, unblocks RB-017) and A3 (the conservation order `p` composes with the heterogeneous-r ratio vector through `beta_gamma(r_i, p)` at each location, validated by TEST 1 across `p ∈ {0, 0.5, 1.0}`).
- **Status:** done.

### Headline thing built

Added the **A2 heterogeneous-r d'-map** to `Rebuild/model/core.py`. Two
new functions exposed via the public surface (`Rebuild/model/__init__.py`):

1. `d_prime_hetero(alloc, r_vec, d_max, f0, h, N, p=1.0)` — per-location
   asymmetric $d'$ map. Returns a length-N float array of
   $d'_i = \max(d_{\mathrm{base}} + s_i (d'_{\max} f(a_i) - d_{\mathrm{base}}), 0)$
   with the per-slot gain/loss-branch criterion
   $s_i = \beta(r_i, p)$ if $a_i \ge 1/N$ else $\gamma(r_i, p)$.
   Accepts `r_vec` as a length-N vector or a scalar (broadcast to a
   uniform N-vector). The conservation order `p` propagates through
   `beta_gamma(r_i, p)` at each location, so the A2 extension composes
   cleanly with the rb-015 A3 conservation family. The per-slot branch
   criterion is the correct generalisation of `d_prime_asym`'s scalar
   `alpha >= 1/N` test: homogeneous alloc with $\alpha > 1/N$ puts
   cued on the gain branch and uncued on the loss branch (matches the
   if-branch of `d_prime_asym`); $\alpha < 1/N$ inverts this (matches
   the else-branch); $\alpha = 1/N$ kills the departure identically
   ($f(1/N) - f(1/N) = 0$) so the branch choice is irrelevant.

2. `canonical_alloc(alpha, N)` — convenience to build the canonical
   homogeneous allocation vector $(α, (1-α)/(N-1), \ldots, (1-α)/(N-1))$.
   Used by the recovery contract and as a starting point for A8 N-dim
   sweeps (RB-017).

The `d_prime_asym` signature and behaviour are unchanged — the
extension is purely additive, with no impact on any existing sim or
test.

### Simulation evidence (the recovery contract IS the evidence here)

`Rebuild/model/tests/test_heterogeneous_r.py` — **5/5 PASS, sha256
`0486921f8a4e253a1682ee0731e52c7de800bf6c3dbb1b5e8ff3200602454c7e`.**

- **TEST 1 — alpha ≥ 1/N grid recovery (5,436 cells).** Across the
  full default alpha grid (step 0.005, alpha ∈ [1/N, 1] = 151 points),
  `h ∈ {sqrt, linear}` (2), `p ∈ {0.0, 0.5, 1.0}` (3),
  `r ∈ {0.1, 0.3, 0.398, 1.0, 3.162, 10.0}` (6) — total
  $151 \cdot 2 \cdot 3 \cdot 6 = 5{,}436$ cells. At each cell:
  `d_prime_hetero(canonical_alloc(alpha,N), r_uniform, ...)` returns
  `[d_c, d_u, d_u, d_u]` with `d_c, d_u` **binary-identical** to
  `d_prime_asym(alpha, r, ...)`. `max|diff| = 0.0` exactly.
- **TEST 2 — alpha < 1/N inversion-regime recovery (468 cells).**
  $\alpha \in [1/(2N), 1/N)$ step 0.01 = 13 points × the same
  $h \times p \times r$ selection = 468 cells. Confirms the per-slot
  branch criterion correctly mirrors `d_prime_asym`'s else-branch
  under cued < uniform. `max|diff| = 0.0`.
- **TEST 3 — scalar broadcast equivalence (72 cells).** Passing
  `r_vec` as a scalar is byte-identical to passing it as a uniform
  N-vector. $p \in \{0,0.5,1\} \times r \in R \times \alpha \in \{0.25,0.5,0.75,1.0\}$ = 72 cells.
  `max|diff| = 0.0`.
- **TEST 4 — CR-048 / run-015 headline-cell spread=0 sanity.** At
  $(V=0.5, v=5, N=4, r=0.398, \alpha=0.5, \text{spread}=0)$:
  `d_prime_hetero` reduces to the legacy $(d_c, d_u)$ exactly,
  reproducing the reviewer's "the hetero code reduces to the single-r
  model exactly" check (CR-048 README). `max|diff| = 0.0`.
- **TEST 5 — heterogeneous-r sign smoke (spread = 0.3).** At
  $\alpha = 0.5 > 1/N$, every uncued slot is on the loss branch with
  $s_i = \gamma(r_i, p=1) = 2/(r_i+1)$, monotone-decreasing in $r_i$.
  The departure $d'_{\max} f((1-\alpha)/(N-1)) - d_{\mathrm{base}}$ is
  the SAME for every uncued slot (same $a_i$) and is NEGATIVE on the
  loss branch, so a smaller $\gamma_i$ (i.e. larger $r_i$) produces a
  less-negative departure contribution and hence a larger $d'_{u,i}$.
  Observed: with uncued $r_i = r_{\mathrm{cued}} \cdot \{0.7, 1.0, 1.3\}$,
  `d_vec[1..3] = [1.3565, 1.3687, 1.3791]` — monotone-increasing in
  $r_i$, as predicted; cued $d_c = 1.6179$ matches the
  $r_{\mathrm{cued}}=0.398$ single-r legacy value exactly.

**Pre-existing recovery digests unchanged.** Re-ran
`test_recovery.py` (7/7 PASS, sha256 `d3c62215…`) and
`test_conservation_family.py` (14/14 PASS, sha256 `f4f57a89…`) after
the edit — extension is purely additive, no behaviour change in any
existing pipeline.

### Exact manuscript claim now licensed

The rebuilt model section / §extensions-A2 may now state:

> *"The inherited paper governs the benefit/cost asymmetry by a single
> global ratio $r$ (assumption A2). The rebuild adopts this in the
> **between-preparation** sense — one effective $r$ per fixed
> preparation, which is what the published $r$-sweep operationalises
> — and admits per-location $r_i$ as a model extension. The
> heterogeneous-$r$ d'-map is*
>
> *$d'_i = \max\!\big( d_{\mathrm{base}} + s_i \,(d'_{\max}\, f(a_i) - d_{\mathrm{base}}),\; 0 \big),$*
>
> *with $d_{\mathrm{base}} = d'_{\max} f(1/N)$ unchanged across locations
> (paper Eq. 4 is $r$-independent) and the per-location scaling
> $s_i = \beta(r_i, p)$ if $a_i \ge 1/N$, else $\gamma(r_i, p)$. The
> conservation order $p$ (Section sec:extensions-A3) propagates through
> $(\beta, \gamma)(r_i, p)$ at each location, so the heterogeneous-$r$
> extension and the conservation-family extension compose. Under
> uniform $r_i = r$ and the canonical homogeneous allocation
> $(\alpha, (1-\alpha)/(N-1), \ldots)$, the heterogeneous-$r$ d'-map
> reduces to the inherited single-$r$ mapping byte-for-byte
> ($\max|\Delta d'| = 0.0$ across $5{,}904$ sampled
> $(\alpha, r, p, h)$ cells; Appendix sec:appendix-recovery-A2)."*

It does **not** yet license:
- (a) any *behavioural / empirical* claim about heterogeneous $r$ —
  that requires RB-018 (the heterogeneous-r C2/C1 sweep simulation,
  modelled on `Critique/replications/A2xA8--heterogeneous-r/`);
- (b) statements about $\alpha^\star$ being a critical point or not
  under heterogeneous $r$ — the reviewer's CR-048 derivation Part 1
  applies, but the rebuild's downstream pipeline (`policies`,
  `optimal_R`) is still homogeneous-in-uncued; promoting it to the
  N-dimensional uncued regime is RB-017 (A8);
- (c) any allocation-deviation $\Delta R$ bound — that needs RB-021
  (A8 N-dim sweep) on top of RB-017's heterogeneous-policies extension.

### What I built (file by file)

- `Rebuild/model/core.py` — appended `d_prime_hetero(...)` and
  `canonical_alloc(...)`; module docstring "Done so far" extended with
  the A2 rb-019 entry. Lines added after the existing `d_prime_asym`
  block (no edits to existing functions; recovery digests of the two
  prior test files unchanged).
- `Rebuild/model/__init__.py` — re-exports `d_prime_hetero`,
  `canonical_alloc`.
- `Rebuild/model/tests/test_heterogeneous_r.py` — 5-check recovery
  contract (sha256 `0486921f…`, 5/5 PASS).
- `Rebuild/model/tests/heterogeneous_r_output.json` — full numeric
  content of the recovery test + sha256.
- `Rebuild/model/README.md` — "three axes" updated (was "two axes"
  after rb-015), A2 subsection added with the heterogeneous-r d' map
  definition and the recovery contract block (sha256 `0486921f…`); the
  files table now includes `test_heterogeneous_r.py` and
  `heterogeneous_r_output.json`; the run command lists the third test;
  the "Public surface" code example shows a 4-slot heterogeneous-r
  call.
- `Rebuild/CLAIM_LEDGER.md` — A2 row extended with the model-wiring
  block and the rb-019 recovery numbers.
- `Rebuild/REBUILD_BACKLOG.md` — RB-014 → done, with a long
  one-paragraph notes block summarising the contract and the unblocks
  (RB-017 and RB-018 both become unblocked).
- `Rebuild/rebuilder_state.json` — `runs_completed` 18 → 19;
  `last_run_id` "rb-018-…" → "rb-019-…";
  `model_increments` ["RB-001", "RB-015"] → ["RB-001", "RB-015", "RB-014"];
  `claims_addressed` extended with "A2";
  `done_task_ids` extended with "RB-014" (now 19 entries);
  `open_task_ids` no longer lists "RB-014";
  `+heterogeneous_r_test_digest` field added (sha256
  `0486921f8a4e253a1682ee0731e52c7de800bf6c3dbb1b5e8ff3200602454c7e`).
  Atomic write (Write overwrites in place; partial-state risk
  mitigated by re-reading the file before this entry was written).
- `Rebuild/conversations/2026-05-25-rebuilder-rb019-a2-hetero-r-model.md` —
  conversation page (frontmatter + 6 sections per the §6.2 template).

### Ledger reconciliation (vs. mission §3, prompt v0.2)

| claim | mission §3 | live verdict | drift? |
| --- | --- | --- | --- |
| C1 | CONTESTED | CONTESTED | no |
| C2 | CONFIRMED-UNDER-ATTACK | CONFIRMED-UNDER-ATTACK | no |
| C3 | CONTESTED | CONTESTED | no |
| C4 | CONFIRMED-CONDITIONAL | CONFIRMED-CONDITIONAL | no |
| C5 | CONFIRMED-UNDER-ATTACK | CONFIRMED-UNDER-ATTACK | no |
| A1 | CONTESTED | CONTESTED | no |
| A2 | CONFIRMED-CONDITIONAL | CONFIRMED-CONDITIONAL | no |
| A3 | CONTESTED | CONTESTED | no |
| A6 | OPEN/in-progress | WEAKLY-SUPPORTED | yes (mild; standing) |
| A8 | CONFIRMED-CONDITIONAL | CONFIRMED-CONDITIONAL | no |

A6's drift is unchanged from prior runs (still pre-CONTESTED,
direction unchanged). No new drift this run.

### Wiki cross-references (§7.3 sweep)

Sweep keywords: `{heterogeneous attention, per-location asymmetry,
between vs within preparation, attention noise correlations,
asymmetric scaling β γ, within-display heterogeneity}`. No relevant
`research_db/papers/` stubs found (the heterogeneous-r generalisation
sits inside the rebuild's own model machinery; the empirical
within-display heterogeneity citation in §extensions-A2 will draw on
the reviewer's CR-007 / R2 references already in `refs.bib` once
RB-018 lands). No new wiki writes; `audit.py` not re-run.

### Why the next run should care

rb-019 unblocks two queued tracks that were both prereq'd on RB-014:

1. **RB-017 (A8 model)** — extend `policies` / `_alpha_opt` /
   `optimal_R` to support an N-dimensional uncued allocation vector
   built from `d_prime_hetero`. Natural continuation of the
   model→model thread; replaces the implicit "uncued split is
   homogeneous" embedded in `optimal_R`'s scalar `(d_c, d_u)` interface
   with an N-group reward in the spirit of the reviewer's
   `optimal_ER_general` (in `Critique/replications/A8--heterogeneous-uncued/run.py`).
   Recovery contract: at a homogeneous `r_vec` and the canonical alloc,
   the N-group policy must return the same `R_P1, R_P2, R_P3, R_P4,
   VDA, CF` as the current scalar `policies(r, cell)` to FP identity
   (probably to *binary* identity if the operand order is matched
   carefully). Once RB-017 lands, RB-018 (A2 sim) can run a true
   heterogeneous-r sweep on the rebuilt pipeline rather than calling
   into the reviewer's substrate.

2. **RB-018 (A2 sim)** — heterogeneous-r C2/C1 sweep using
   `d_prime_hetero`. Can run in parallel to RB-017 (the existing
   reviewer substrate `Critique/replications/A2xA8--heterogeneous-r/`
   suffices for the C2-non-monotonicity-survives-±30%-spread check
   and the C1 contested-corner check), but the *full*
   heterogeneous-r policy reward needs RB-017. The minimal-viable
   sim: spread sweep at the C2/C1 headline cells, reproducing the
   reviewer's CR-048 numbers from the rebuilt model module.

Per the §4.1 default selection rule (highest-priority unblocked + the
model→sim→derivation→manuscript dependency order), **RB-017** is the
natural next pick: it opens the A8 thread, and RB-018 (the A2 sim)
can then call into the heterogeneous-pipeline policies for a clean
extension story. Alternatively, RB-018 first if the next run prefers
the sim track over the model track — both are unblocked and the
reviewer-substrate sim is enough for the §extensions-A2 manuscript
section in isolation.

Lower-priority unblocked alternatives (all priority `low`): RB-025
(A1 cell-wise sign-flip map), RB-026 (C2 closed-form r†(v,ρ)
derivation), RB-024 (C1 closed-form CF<0.5 corner), RB-023 (A1 finer-ρ
grid), RB-027/28/29/31/32 (variant-B / threshold-sharpening follow-up
sims), RB-033 (A3 formal derivation in the rebuild's voice).

---



- **Run id:** `rb-018-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-013 (manuscript §appendix-C5; prereq RB-001 done at rb-001;
  no new sim needed — `model/tests/test_recovery.py` covers r=1 implicitly via the
  ρ→0 product recovery, and `model/tests/test_conservation_family.py` covers the
  conservation-form-invariance corollary).
- **Output kind:** manuscript.
- **Claims touched:** C5 (CONFIRMED-UNDER-ATTACK, primary). Cross-references A3
  (CONTESTED, via the conservation-form-invariance corollary already in
  §extensions-A3 — this section closes the cross-link from the C5 side).
- **Status:** done.

### Headline thing built

Replaced the §appendix-C5 stub placeholder in `Rebuild/manuscript/sections/appendix.tex`
with a full subsection (~140 LaTeX lines, ~8 KB) at the strength the live C5 verdict
(CONFIRMED-UNDER-ATTACK, v0.2 / 2026-05-22) licenses. Contents in order:

1. **Claim-restatement paragraph** at CONFIRMED-UNDER-ATTACK strength:
   the algebraic collapse $\beta(1) = \gamma(1) = 1$ is a *real-number identity*
   (universal); the published "maximum difference: 0.0" is a *bit-exact* guarantee
   tied to the validation configuration via the Sterbenz lemma (config-specific);
   $r=1$ is the smooth centre of the family, not a knife-edge.
2. **Proposition prop:c5-realnumber (real-number recovery at $r=1$).** Universal
   over $(V, v, N, d'_{\max}, f_0, h, \rho)$: $\beta(1) = \gamma(1) = 1$ forces
   $d_c(\alpha) = d_u(\alpha) = d_{\max} f(\alpha)$ in the asymmetric rule,
   collapsing to the symmetric rule and hence forcing identical optimal
   $\alpha^\star$, $c_c^\star$, $c_u^\star$, $R^\star$, and CF as real-number
   identities. The cancellation $d_{\mathrm{base}} - d_{\mathrm{base}} = 0$ is the
   whole content of the word "reduces."
3. **Proposition prop:c5-sterbenz (bit-exact symmetric recovery on the validation
   configuration).** Three observations compose: (i) $\beta(1)$ and $\gamma(1)$
   are the exact float `1.0`; (ii) Sterbenz's lemma states
   $a/2 \le x \le 2a \Rightarrow \mathrm{fl}(x-a) = x-a$ exactly; (iii) at the
   published validation config $a = d'_{\mathrm{base}} = 1.5$ and the swept range
   $x = d'_{\max} f(\alpha) \in [1.0, 2.0]$ sits inside $[a/2, 2a] = [0.75, 3.0]$
   for every grid point, so the round-trip $a + (x-a) = x$ is exact at every
   $\alpha$. Hence $\max|\Delta\alpha^\star| = 0$ and $\max|\Delta R^\star| = 0$
   exactly (not merely to machine epsilon).
4. **Scope clause + closed-form off-band threshold** Eq. eq:c5-sterbenz-threshold:
   $f_0 < h(1/N)/(1 + h(1/N)) = 1/3$ at $h = \sqrt{\cdot}, N = 4$. Off-band
   configurations (notably $f_0 \lesssim 1/3$) lose bit-identity and drift at the
   order of one unit in the last place ($\sim 10^{-17}$ to $10^{-16}$). The proper
   universal statement of C5 is "identical to machine precision"; the literal
   "0.0" of the published Appendix~A is a structural guarantee of the chosen
   config, not a property of the model.
5. **$\Rsens = 1$ is the smooth centre paragraph.** Slopes
   $d\beta/dr|_{r=1} = 1/2$, $d\gamma/dr|_{r=1} = -1/2$; the asymmetric slope
   ratio $\beta(r)/\gamma(r) = r$ is continuous and differentiable through
   $r = 1$. The reviewer's continuity probe at $r = 1 \pm \epsilon$ confirms the
   symmetric recovery is the smooth interior of the family:
   $\max|\Delta R^\star|$ against the symmetric model scales linearly in
   $|r - 1|$, slope $\approx 0.084$ reward units per unit shift in $r$. Reporting
   $r = 1$ as a special case is mathematically correct but interpretively
   misleading if it suggests a knife-edge: it is the balanced gain-modulation
   versus suppression null (Section sec:model, Definition def:three-levers).
6. **C5 conservation-form-invariance paragraph.** Closes the cross-reference to
   §extensions-A3: at $r = 1$ the family identity $\beta/\gamma = 1$ forces
   $\beta = \gamma$, and any power-mean constraint $M_p(\beta, \gamma) = 1$ then
   forces $\beta = \gamma = 1$ for every $p$ (every power mean of the constant
   sequence equals the constant). The entire C5 argument
   (prop:c5-realnumber—prop:c5-sterbenz) holds under any conservation rule in the
   family without modification. The §extensions-A3 corollary block already
   cross-references `sec:appendix-c5`; both sides now closed.
7. **Reproducibility paragraph.** Cites the recovery-test pinned numerics at
   $r = 1$ (variant A, validation config, $\rho = 0$):
   $\VDA = 0.039825$, $\CF = 0.728228$, $\Rpone = 2.317239$ — all matched
   to max-abs-diff $0.0$ against the reviewer's logs at
   `Critique/replications/A1--correlated-fa/output/results.json`. The
   probability-level test confirms $\PnoFA(\rho = 0)$ returns the inherited
   product $\Phi(b_c)\,\Phi(b_u)^{N-1}$ of Eq. eq:pnofa-indep to binary equality.
   All seven recovery checks pass; sha256
   `d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f` for the
   recovery-test JSON payload, sha256
   `f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e` for
   `test_conservation_family.py` (the two checks
   `test_symmetric_corner_invariant` and `test_p0_symmetric_corner_identity`
   verify `policies(r=1, p=0) == policies(r=1, p=1)` to floating-point
   identity, in agreement with the closed-form $\beta(1, p) = \gamma(1, p) = 1$).

### Manuscript build evidence

Build: 4-pass pdflatex+bibtex. Pass 1 hit a fatal **double-subscript error**
because the `\alphacued` macro already expands to `\alpha_c` and the
formulation `\alphacued^\star_{\mathrm{asym}}(\Rsens{=}1)` reads as
`\alpha_c^\star_{\mathrm{asym}}` — two `_` subscripts on a single base. Fixed by
reformulating the equality with the evaluation-bar notation
`\alphacued^\star\!\big|_{\mathrm{asym},\,\Rsens=1} =
 \alphacued^\star\!\big|_{\mathrm{sym}}`
(and similarly for $\Rew^\star$ and $\CF$ in
Proposition prop:c5-realnumber, and for the bit-exact equalities in
Proposition prop:c5-sterbenz using `\max\big|\Delta \alphacued^\star\big|`).
After fix: pass 1 → bibtex (Sterbenz1974, Goldberg1991 added to the bibliography
from the new bib entries) → pass 2 (2 undefined-cite warnings because pass 1 had
errored *before* logging the cite keys to `.aux`) → bibtex 2 → pass 3 (cites
settled) → pass 4 settled, 0 undefined references in the final pass.
`main.pdf` is **35 pages / 2,165,118 bytes**, up from 33 pages / 2,152,496 bytes
at rb-017 (+2 pages, +12.6 KB — light-touch increment as scoped, no new sim).
Only cosmetic hyperref/Unicode warnings on macro expansion in PDF strings; no
semantic warnings or errors.

### Exact manuscript claim now licensed

The rebuilt §appendix-C5 may now state:

> *"At $r = 1$ the asymmetric benefit/cost family $\beta(r), \gamma(r)$
> collapses to $\beta(1) = \gamma(1) = 1$, and the asymmetric implementation
> evaluated at $r = 1$ produces the same sensitivity arrays as the symmetric
> special case. The collapse is therefore a real-number identity, universal
> over $(V, v, N, d'_{\max}, f_0, h, \rho)$ (Proposition prop:c5-realnumber).
> At the validation configuration $(N = 4, d'_{\max} = 2.0, f_0 = 0.5,
> h = \sqrt{\cdot}, \mathrm{variant\ A})$, the Sterbenz lemma additionally
> gives a bit-exact guarantee: the swept range
> $x = d'_{\max} f(\alpha) \in [1.0, 2.0]$ sits inside the band
> $[a/2, 2a] = [0.75, 3.0]$ with $a = d'_{\mathrm{base}} = 1.5$, so
> $\mathrm{fl}(x - a) = x - a$ exactly and the round-trip $a + (x - a)$ returns
> $x$ bit-for-bit at every grid point, hence $\max|\Delta \alpha^\star| = 0$
> and $\max|\Delta R^\star| = 0$ exactly (Proposition prop:c5-sterbenz). The
> hypothesis is sufficient but not necessary: off the Sterbenz band (notably
> $f_0 < h(1/N)/(1 + h(1/N)) = 1/3$ at $h = \sqrt{\cdot}, N = 4$) bit-identity
> is lost and the recovery is only exact to machine precision. The universal
> statement is therefore "identical to machine precision"; the literal "0.0"
> of the published Appendix~A is a structural guarantee of the chosen
> validation config, not a property of the model. The collapse at $r = 1$ is
> the smooth interior of a two-sided family, not a knife-edge: the asymmetric
> slope ratio $\beta(r)/\gamma(r) = r$ is differentiable through $r = 1$, with
> $\max|\Delta R^\star|$ scaling linearly in $|r - 1|$. The result is
> conservation-form-invariant by construction: at $r = 1$ the family identity
> $\beta/\gamma = 1$ forces $\beta = \gamma$, and the constraint
> $M_p(\beta, \gamma) = 1$ then forces $\beta = \gamma = 1$ for every $p$,
> so the entire argument holds under any conservation rule in the
> power-mean family without modification."*

It does **not** yet license:
- (a) the literal "0.0" as a universal property of the model — only as a
  validation-config statement under variant~A;
- (b) any new behavioural / empirical claim — C5 is a consistency result;
- (c) the conservation-form-invariance under conservation choices outside the
  power-mean family $M_p(\beta, \gamma) = 1$ (e.g. an exotic non-power-mean
  rule that breaks $\beta = \gamma \Rightarrow \beta = \gamma = 1$);
- (d) a closed-form rule for how the slope $\approx 0.084$ reward units per
  unit shift in $r$ depends on the cell parameters — only its value at the
  headline cell from the reviewer's continuity probe.

### What I built (file by file)

- `Rebuild/manuscript/sections/appendix.tex` — REPLACED the §appendix-C5 stub
  (lines ~43–52) with the full subsection (~140 lines, ~8 KB).
- `Rebuild/manuscript/refs.bib` — +2 entries: `Sterbenz1974` (Sterbenz,
  *Floating-Point Computation*, Prentice-Hall 1974, Theorem 4.3.1) and
  `Goldberg1991` (Goldberg, ACM Computing Surveys 23(1):5–48, Theorem 11) —
  both cited by full bibliographic reference per the math-methods scope
  inherited from rb-008/rb-017 (Slepian 1962, Tong 1990, HLP1934); no
  research_db/papers/ stubs added.
- `Rebuild/manuscript/main.pdf` — rebuilt, 35 pages / 2,165,118 bytes
  (was 33 pages / 2,152,496 bytes at rb-017 = +2 pages, +12.6 KB).
- Updates: `CLAIM_LEDGER.md` (header reconcile line updated to rb-018; C5 row
  backing column extended with the full §appendix-C5 content listing);
  `REBUILD_BACKLOG.md` (RB-013 status queued → done; notes prepended with
  rb-018 disposition; touched timestamp updated to 2026-05-25T20:30:00Z);
  `rebuilder_state.json` (atomic write — runs 17 → 18; RB-013 added to
  `done_task_ids` and `manuscript_sections_drafted`; `open_task_ids` cleaned;
  `rb_018_manuscript_pdf_bytes` field added).
- `Rebuild/conversations/2026-05-25-rebuilder-rb018-appendix-c5.md` — this
  run's conversation page.

### Ledger reconciliation (vs. mission §3, prompt v0.2)

| claim | mission §3 | live verdict | drift? |
| --- | --- | --- | --- |
| C1 | CONTESTED | CONTESTED | no |
| C2 | CONFIRMED-UNDER-ATTACK | CONFIRMED-UNDER-ATTACK | no |
| C3 | CONTESTED | CONTESTED | no |
| C4 | CONFIRMED-CONDITIONAL | CONFIRMED-CONDITIONAL | no |
| C5 | CONFIRMED-UNDER-ATTACK | CONFIRMED-UNDER-ATTACK | no |
| A1 | CONTESTED | CONTESTED | no |
| A2 | CONFIRMED-CONDITIONAL | CONFIRMED-CONDITIONAL | no |
| A3 | CONTESTED | CONTESTED | no |
| A6 | OPEN/in-progress | **WEAKLY-SUPPORTED** | yes (mild, unchanged from rb-001) |
| A8 | CONFIRMED-CONDITIONAL | CONFIRMED-CONDITIONAL | no |

A6's drift is unchanged from rb-001 (mild, pre-CONTESTED). RB-016 and RB-020
remain `blocked` on a decisive A6 label.

### Wiki sweep

Keywords {Sterbenz lemma, floating-point arithmetic, IEEE-754, machine precision,
symmetric special case, bit-exact recovery, ULP, rounding error, real-number
identity, smooth centre of family, β/γ kink}. No relevant `research_db/papers/`
stubs exist; this is the math-methods gap inherited from rb-008 (Slepian 1962,
Tong 1990) and rb-017 (HLP1934 conservation literature). Out of rebuilder scope
per the reviewer's CR-035/CR-037 backlog; the Sterbenz1974 and Goldberg1991
citations in §appendix-C5 use the full bibliographic reference in refs.bib. No
new wiki stubs added; audit.py not re-run.

### Why the next run should care

rb-018 closes the C5 thread on the manuscript side: the §appendix-C5 subsection
now states the result at its CONFIRMED-UNDER-ATTACK strength as two propositions
(real-number identity + Sterbenz bit-exact bound) plus an explicit off-band
threshold, plus the smooth-centre observation, plus the conservation-form-
invariance cross-reference to §extensions-A3. This discharges the
"four-headline-claim spine + C5 appendix" structural goal of the rebuilt
manuscript, leaving the §abstract/§intro/§limitations/§methods sections (which
are already drafted) and the queued A2/A8/A3 extensions + RB-033 formal A3
derivation as the largest remaining structural increments.

The cleanest next single-increment is **RB-014** (A2 heterogeneous-r model
extension; medium effort; prereq RB-001 done) — it opens the A2/A8 thread into
`extensions.tex` (already structured by rb-017 to host one subsection per lever
extension), and is the natural successor to RB-019 (A3 band sim) and RB-034
(§extensions-A3 manuscript section) in the same file. **RB-026** (C2 r†(v) ρ>0
closed-form, prereq RB-006 done) fills the §appendix-deriv-c2 stub and would
extend the closed-form r†(v) machinery to the A1 channel. **RB-033** (A3 formal
derivation, prereq RB-019 done) fills the §appendix-deriv-a3 stub placed by
rb-017.

---

## rb-017 — 2026-05-25 — §extensions-A3 (manuscript increment) — DONE

- **Run id:** `rb-017-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-034 (manuscript §extensions-A3; prereq RB-019 done at rb-016).
- **Output kind:** manuscript.
- **Claims touched:** A3 (CONTESTED, primary), C2 (CONFIRMED-UNDER-ATTACK, via the
  r†(v) p-invariance theorem and the peak-VDA conservation band), C1 (CONTESTED, via
  the 4,410-cell CF band and the cell-wise ΔCF ≤ 0 monotonicity), C5 (CONFIRMED-UNDER-
  ATTACK, via the corollary that symmetric recovery at r=1 is conservation-form-invariant
  because β(1, p) = γ(1, p) = 1 for every p).
- **Status:** done.

### Headline thing built

A new manuscript section file `Rebuild/manuscript/sections/extensions.tex`
(~340 LaTeX lines), wired into `main.tex` between `sections/results.tex` and
`sections/limitations.tex`. The file is structured to host one subsection per
lever extension; this run fills §extensions-A3 only (A2/A8 and A6 deferred to
later increments). §extensions-A3 contents, in order:

1. Claim restatement at defensible strength (live A3 verdict CONTESTED;
   central tendency robust to conservation form, tail not robust; reproduces
   the reviewer verdict-text Block-C1 numbers verbatim — 4.0% → 8.3% frac_<0.5,
   191 flips, 0 reverse, min CF× = 0.231).
2. **Power-mean conservation family definition** $M_p(\beta, \gamma) = 1$,
   $\beta/\gamma = r$ (Eq. eq:conservation-family) + closed-form weight pair
   (Eq. eq:beta-gamma-of-p) + family identities ($\beta/\gamma = r$ preserved
   at every $p$; symmetric corner $\beta(1, p) = \gamma(1, p) = 1$ at every $p$).
3. **C2 conservation-family band on the peak**: Table tab:a3-c2-peak-band
   (5-row v-family × 3-p block; at v = 5, peak VDA shifts 0.0830 → 0.0885 →
   0.0951 as p goes 1 → 0.5 → 0, a +14% envelope on the headline number) +
   Figure fig:a3-vda-curves-p-v5 (three VDA(r) curves at v = 5 with r†(v=5)
   overlay).
4. **Proposition 3.1 ($r†(v)$ is conservation-form-invariant)** + one-paragraph
   proof from the uniform-attention-point collapse $d_c = d_u = d_{base}$ at
   α = 1/N regardless of (r, p), so the P3-optimal criteria and the partials
   K_c(v), K_u(v) are p-independent, hence r†(v) = K_u/[(N-1) · K_c] is
   p-invariant. Numerical witness: rb-016 TEST 3 K_c, K_u, r†(v) identical to
   FP across p ∈ {0, 0.5, 1.0}, max |Δ| = 0.0. Figure fig:a3-vda-peak-band
   (per-p peak markers clustered vertically above the p-invariant r†(v) trace).
5. **C1 conservation-family band on the 4,410-cell sweep**: Table
   tab:a3-c1-cf-band (6-row variant × p block reporting min/q5/q50/q95/max/
   frac_<0.5/frac_<0.6; central tendency robust — median moves ≤ 0.004; tail
   not robust — variant-A min CF falls 0.559 → 0.464, variant-B min CF falls
   0.304 → 0.231, combined frac_<0.5 roughly doubles 4.0% → 8.3%).
6. **Theorem 3.2 (per-cell ΔCF ≤ 0 monotonicity, empirical)** — 87.7% strict-
   dec variant A, 81.0% variant B; 0 cells where ΔCF > 0 on the entire grid;
   72 flips above-to-below variant A, 119 variant B, 0 reverse in either. The
   cleanest novel statement the rebuild contributes to the A3 question. Figures
   fig:a3-cf-hist-pfamily and fig:a3-delta-cf-distribution.
7. **C5 conservation-form-invariance corollary** — at r = 1 the family identity
   gives $\beta(1, p) = \gamma(1, p) = (2/2)^{1/p} = 1$ at every p ≠ 0, with
   the same limit at p = 0; so the C5 symmetric-recovery result survives any
   conservation choice without modification. Witness: rb-015
   `test_symmetric_corner_invariant` to FP identity.
8. **Scope** — joint (p × ρ) sweep deferred; formal derivation in rebuild's
   voice deferred to RB-033 (§appendix-deriv-a3 stub placed in
   `sections/appendix.tex` this run as a landing pad); closed-form proof of
   per-cell ΔCF ≤ 0 deferred; variant-B ρ-flatness interaction deferred.
9. **Reproducibility** — cites sha256 `055bf4ec…` (rb-016) + rb-015 model-test
   sha256 `f4f57a89…` + all four rb-016 recovery tests verbatim (Test 1 rb-006
   pins ≤ 5e-5; Test 2 reviewer A3 ≤ 1e-5 observed 6.1e-7 CF / 3.6e-7 VDA;
   Test 3 r† p-invariance to FP; Test 4 per-variant median ≤ 4.1e-5).

### Manuscript build evidence

Build: 4-pass pdflatex+bibtex. Pass 1 hit two issues: one Undefined control
sequence on `\citep{HLP1934}` (natbib not loaded — fixed to `\cite{HLP1934}`)
and one Undefined reference on `sec:appendix-deriv-a3` (fixed by adding the
appendix stub). Then: pass 1 → bibtex (HLP1934 added) → pass 2 → pass 3
settled, 0 undefined refs in the final pass. `main.pdf` is **33 pages /
2,152,496 bytes**, up from 27 pages / 1,814,626 bytes at rb-013 (+6 pages,
+338 KB). Only cosmetic overfull/underfull hbox warnings from long file-path
literals; no semantic errors.

### Exact manuscript claim now licensed

The rebuilt §extensions-A3 may now state:

> *"Promoting the inherited additive conservation rule β + γ = 2 to the
> power-mean family M_p(β, γ) = 1 with β/γ = r, we recover the inherited
> model at p = 1 and the reviewer's A3 multiplicative alternative at p = 0.
> The closed-form escape threshold r†(v) of Section §results-c2 is
> conservation-form-invariant by construction (Proposition 3.1), and the
> symmetric-recovery result at r = 1 survives any choice of p (corollary).
> The peak height of VDA(r) at the headline cell moves with p — a +14%
> envelope at v = 5 in the band p ∈ {0, 1} — and is reported as a
> sensitivity. The 4,410-cell C1 sweep at ρ = 0 has a p-robust central
> tendency (median CF moves by ≤ 0.004) and a p-fragile tail
> (frac(CF < 0.5) roughly doubles, 191 cells flip from the criterion-
> dominant to the criterion-subordinate region with 0 reverse flips); per-
> cell, ΔCF ≤ 0 in every valid cell (Theorem 3.2). The conservation rule
> is therefore a model assumption, not a derived statement, and the
> headline numbers properly stand as bands across the family rather than
> as points at one fixed choice."*

It does **not** yet license:
- (a) the joint (p, ρ) sweep — band numbers are at ρ = 0 only;
- (b) a formal derivation in the rebuild's voice with the Hardy-Littlewood-
  Pólya power-mean monotonicity argument or a closed-form algebraic proof of
  Theorem 3.2 — deferred to RB-033 (§appendix-deriv-a3 stub placed);
- (c) harmonic (p = -1) or super-additive (p > 1) numerics — the rb-016 sim
  runs p ∈ {0, 0.5, 1} only; the family is stated for general p but the
  empirical band is reported on the sweep grid.

### What I built (file by file)

- `Rebuild/manuscript/sections/extensions.tex` — NEW section file (~340 lines,
  ~17.5 KB).
- `Rebuild/manuscript/main.tex` — +1 line, `\input{sections/extensions.tex}`
  between results and limitations.
- `Rebuild/manuscript/sections/appendix.tex` — +1 subsection,
  `sec:appendix-deriv-a3` stub clearing the forward reference.
- `Rebuild/manuscript/refs.bib` — +1 entry, `HLP1934` (Hardy-Littlewood-Pólya
  1934 *Inequalities*; by full bib reference; research_db stub deferred per
  math-methods scope inherited from rb-008 / CR-035/CR-037).
- `Rebuild/manuscript/figures/{vda_curves_pfamily_v5,vda_peak_band,cf_histogram_pfamily,delta_cf_distribution}.png`
  — 4 figures copied from `Rebuild/sims/A3--conservation-band/output/figures/`.
- `Rebuild/manuscript/main.pdf` — rebuilt, 33 pages / 2,152,496 bytes.
- Updates: `CLAIM_LEDGER.md` (header reconcile line updated to rb-017; A3 row
  backing column extended with the full §extensions-A3 content listing);
  `REBUILD_BACKLOG.md` (RB-034 status queued → in_progress → done; notes
  prepended with rb-017 disposition; touched timestamp); `rebuilder_state.json`
  (atomic write — runs 16 → 17; RB-034 added to `done_task_ids` and
  `manuscript_sections_drafted`; `rb_017_manuscript_pdf_bytes` field added).
- `Rebuild/conversations/2026-05-25-rebuilder-rb017-extensions-a3.md` — this
  run's conversation page.

### Ledger reconciliation (vs. mission §3, prompt v0.2)

| claim | mission §3 | live verdict | drift? |
| --- | --- | --- | --- |
| C1 | CONTESTED | CONTESTED | no |
| C2 | CONFIRMED-UNDER-ATTACK | CONFIRMED-UNDER-ATTACK | no |
| C3 | CONTESTED | CONTESTED | no |
| C4 | CONFIRMED-CONDITIONAL | CONFIRMED-CONDITIONAL | no |
| C5 | CONFIRMED-UNDER-ATTACK | CONFIRMED-UNDER-ATTACK | no |
| A1 | CONTESTED | CONTESTED | no |
| A2 | CONFIRMED-CONDITIONAL | CONFIRMED-CONDITIONAL | no |
| A3 | CONTESTED | CONTESTED | no |
| A6 | OPEN/in-progress | **WEAKLY-SUPPORTED** | yes (mild, unchanged from rb-001) |
| A8 | CONFIRMED-CONDITIONAL | CONFIRMED-CONDITIONAL | no |

A6's drift is unchanged from rb-001 (mild, pre-CONTESTED). RB-016 and RB-020
remain `blocked` on a decisive A6 label.

### Wiki sweep

Keywords {power mean, generalised mean, Hardy-Littlewood-Pólya, conservation
constraint, asymmetric scaling, β+γ=2, β·γ=1, additive vs multiplicative
conservation}. No relevant `research_db/papers/` stubs exist; this is the
math-methods gap inherited from rb-008 (Slepian 1962, Tong 1990) and rb-014
(conservation literature). Out of rebuilder scope per the reviewer's CR-035/
CR-037 backlog; the HLP1934 citation in §extensions-A3 uses the full
bibliographic reference in refs.bib. No new wiki stubs added; audit.py not
re-run.

### Why the next run should care

rb-017 turned the rb-015/rb-016 A3 wiring (model extension + empirical band)
into a manuscript-citable section, completing the model→sim→manuscript
dependency chain for A3 at the central-tendency / band strength the live
verdict licenses. The rebuilt paper now has four headline-claim results
subsections drafted (§results-c1, -c2, -c3, -c4) plus a §model section plus
a §extensions section with one subsection drafted; one of the three "load-
bearing assumption" extensions (A3 conservation family) is lifted from a
verdict-row license to a written, figure-backed section.

The cleanest next single-increment is **RB-013** (§appendix-C5 light-touch
consistency result; low effort; prereq RB-001 done) — it closes the
§extensions-A3 forward reference to `sec:appendix-c5` and discharges the
four-headline-claim spine. **RB-014** (A2 heterogeneous-r model extension;
medium effort; prereq RB-001 done) opens the A2/A8 thread into the same
`extensions.tex` file this run created — the file is already structured to
host one subsection per lever extension. **RB-033** (A3 formal derivation in
the rebuild's voice; low priority) graduates the in-section Proposition 3.1
proof sketch and Theorem 3.2 empirical statement to a proper appendix
derivation, with the §appendix-deriv-a3 stub written this run as the landing
pad.

---

---

## rb-016 — 2026-05-25 — A3 conservation-family band on headline numbers (simulation increment) — DONE

- **Run id:** `rb-016-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-019 (A3 conservation-family band on headline numbers; sim,
  prereq RB-015 done at rb-015). Two-deliverable minimum-viable cut: (a) VDA(r)
  at the C2 headline cell across p ∈ {0, 0.5, 1.0} on rb-006's 84-r grid with
  per-(v, p) peak-vs-r†(v) annotations; (b) 4,410-cell C1 sweep at p ∈ {0, 1.0}
  at ρ=0 reporting per-cell CF + ΔCF distribution + flip counts as the
  conservation-form band.
- **Output kind:** simulation.
- **Claims touched:** **A3 (CONTESTED)** — the rebuild's first cell-wise sweep
  inside Rebuild/ at p ≠ 1 turns the rb-015 model wiring into a rebuilt-side
  empirical band on the manuscript's headline CF numbers; **C2 (CONFIRMED-
  UNDER-ATTACK)** — adds the conservation-family band on peak (r*, VDA*) and
  the **r†(v) p-invariance theorem** (at α = 1/N the perturbation bracket
  d_max·f(1/N) − d_base = 0, so d_c = d_u = d_base regardless of (r, p); the
  P3-optimal criteria (c_c*, c_u*) are therefore p-independent, K_c(v), K_u(v)
  are p-independent, and r†(v) = K_u/[(N−1)·K_c] is conservation-form-invariant
  by construction — proof by inspection of the model's `d_prime_asym` at the
  uniform-attention point); **C1 (CONTESTED)** — extends the rb-003
  distributional restatement with a conservation-family band on the CF
  histogram and the new cell-wise ΔCF ≤ 0 monotonicity. CLAIM_LEDGER A3/C2/C1
  rows extended; strength unchanged on all three rows (each was already
  licensed at "band over the family" from rb-015).

- **Headline thing built:** `Rebuild/sims/A3--conservation-band/` — a
  two-block sim at ρ = 0 with full README and `run.py` heavily docstring'd
  at the head. Block A: 84-r × 5-v × 3-p VDA(r) sweep at the headline cell
  (N=4, d'_max=2, f_0=0.5, h=sqrt, V=0.5, variant A), recording R(P1..P4),
  VDA, CF per (r, v, p) plus per-(v, p) peak (r*, VDA*) and the closed-form
  K_c(v), K_u(v), r†(v). Block B: full 4,410-cell C1 primary sweep (22 r ×
  21 V × 2 variants × 5 v) at p ∈ {0, 1.0}, ρ = 0, with the same machinery
  rb-003 used (50-point alpha grid, 121-point criterion grid, value-blind
  alpha caching per (r, V, variant, ρ) reused across v). Reports per-cell
  CF distribution per (variant, p), per-cell ΔCF = CF(p=0) − CF(p=1)
  distribution, and the cell-flip tally (CF ≥ 0.5 → < 0.5, and reverse).

  - **Block A results (headline cell, variant A, ρ = 0):**
    - **r†(v) p-invariance theorem** verified to FP identity: K_c, K_u, and
      r_dagger all differ by *exactly 0.0* across p ∈ {0, 0.5, 1.0} at every
      v ∈ {2, 3, 5, 8, 10} (TEST 3 pass tolerance 1e-14, observed 0.0). This
      is a free strengthening of the C2 result.
    - **Empirical band on peak VDA at v = 5:** 0.0830 (p = 1) → 0.0885
      (p = 0.5) → 0.0951 (p = 0). The multiplicative regime widens peak
      VDA by ~14%.
    - **Empirical band on peak r* at v = 5:** 0.3758 (p = 1) → 0.3548
      (p = 0). Multiplicative escapes α = 1/N at smaller r.
    - **Peak r* > r†(v) preserved** under every conservation order tested:
      r†(v = 5) = 0.0504 sits well below the empirical peak (gap ≈ +0.30).
      The §2.3 prediction survives the conservation swap.

  - **Block B results (4,410-cell sweep, ρ = 0):**
    - Variant A: p = 1 median 0.7552 / min 0.5587 / frac<0.5 0.0% / frac<0.6
      7.0%; p = 0 median 0.7540 / min 0.4638 / frac<0.5 3.3% / frac<0.6 21.7%.
    - Variant B: p = 1 median 0.7682 / min 0.3040 / frac<0.5 8.0% / frac<0.6
      19.7%; p = 0 median 0.7640 / min 0.2309 / frac<0.5 13.4% / frac<0.6
      27.1%.
    - **Combined-variant flip tally (matches verdict text exactly):**
      n_below_0_5 177 → 368; **191 cells flip** CF ≥ 0.5 → < 0.5;
      **0 cells flip back** (predicted in
      `Critique/verdicts/A3--multiplicative-conservation.md` Block C1).
    - **Cell-wise ΔCF ≤ 0** in every valid cell — a finding not stated in
      the inherited paper: the conservation swap weakens criterion in every
      cell or leaves it unchanged.
    - Central tendency robust (variant A −0.0012; variant B −0.0042 on
      median CF), tail shape is not (frac<0.5 doubles combined).
    - Variant-B min CF deepens 0.3040 → 0.2309 — matches the verdict text
      "min CF× = 0.231" to the printed precision.

- **Recovery contract built:** four hard tests, all PASS.
  1. **TEST 1 — Block A p = 1, v = 5 at rb-006 reference pins** r ∈ {0.398,
     1.0, 3.162} on VDA and CF: tolerance ≤ 5e-5 each, observed max diff
     ≤ 5e-5 across 3 pins (every cell passes).
  2. **TEST 2 — Block A p = 0, v = 5 vs reviewer A3 multiplicative
     replication** (`Critique/replications/A3--multiplicative-conservation/output/results.json`
     `block_c2_c1.families.multiplicative`, 21-row r-sweep): tolerance
     ≤ 1e-5 on VDA and CF, observed max |ΔVDA| = 3.6e-7, max |ΔCF| = 6.1e-7
     (same cross-Φ-backend ULP-level reordering rb-015's policies() check
     saw, two orders of magnitude under tolerance).
  3. **TEST 3 — r†(v) p-invariance to FP identity:** tolerance 1e-14
     absolute on K_c, K_u, r_dagger across p ∈ {0, 0.5, 1.0}; observed max
     diffs all *exactly 0.0* (every v).
  4. **TEST 4 — Block B p = 1 vs rb-003 logged per-variant medians:**
     tolerance ≤ 5e-5 on cf_median; observed |Δ| = 1.3e-5 (variant A) /
     4.1e-5 (variant B). Both within tolerance.
  Determinism re-verified: re-running the sim produced byte-identical
  `results.json` (sha256 unchanged at `055bf4ec…`, file size unchanged at
  4,941,767 B).

- **Simulation evidence.**
  - **sha256 (pre-hash) of `Rebuild/sims/A3--conservation-band/output/results.json`:**
    `055bf4ec862c711f2c6a3fa0831e1373b806a84c5f5c1a6b13fd1d9d7a039a33`
    (4,941,767 B; deterministic across re-runs).
  - **Wall-clock:** ~36–39 s on the bash sandbox (well under mission §11's
    10–20 min budget).
  - **Four figures** written under `Rebuild/sims/A3--conservation-band/output/figures/`:
    `vda_curves_pfamily_v5.png` (108 KB; VDA(r) at v=5, three curves for
    p ∈ {0, 0.5, 1.0}, peaks marked with hollow circles, vertical dashed =
    closed-form r†(v=5) p-invariant), `vda_peak_band.png` (110 KB; peak
    r* and peak VDA* vs v with r†(v) trace), `cf_histogram_pfamily.png`
    (84 KB; 4-panel variant × p), `delta_cf_distribution.png` (57 KB;
    2-panel variant, flip counts annotated).

- **What the manuscript can now say.**
  - **CLAIM_LEDGER A3 row:** the rebuilt model implements the power-mean
    conservation family $M_p(\beta, \gamma) = 1$ with $\beta/\gamma = r$
    (rb-015) AND the rebuilt manuscript can now report the empirical band
    on the headline numbers as a rebuilt-side artifact (rb-016): C2 peak
    VDA at v = 5 widens by ~14% across the band; C1 frac<0.5 doubles from
    4.0% to 8.3% combined; central-tendency median CF moves by ≤ 0.005;
    191 cells flip CF ≥ 0.5 → < 0.5 with 0 reverse; ΔCF ≤ 0 everywhere.
    Manuscript §extensions-A3 (RB-034) is now unblocked.
  - **CLAIM_LEDGER C2 row:** the rebuilt manuscript can now state the
    *r†(v) p-invariance theorem* — one-paragraph proof from
    `d_prime_asym` at α = 1/N — and cite TEST 3's FP-identity numerical
    verification. The §results-c2 section gets a small sensitivity-table
    update at RB-034 cross-reference.
  - **CLAIM_LEDGER C1 row:** the rebuilt manuscript can now report the
    *conservation-family contour on the CF distribution* and the
    *cell-wise ΔCF ≤ 0 monotonicity* (new finding). §results-c1 gets a
    short paragraph at RB-034 cross-reference.
  - **What the manuscript may NOT yet say:** the formal derivation of the
    conservation family in the rebuild's voice (RB-033, low-priority);
    the conservation × ρ interaction band (no current backlog task; would
    be a follow-up sim if the §extensions reviewer pushes back).

- **Wiki sweep.** Keywords {conservation family, power mean, generalised
  mean, Hardy-Littlewood-Pólya, asymmetric scaling, β+γ=2, β·γ=1,
  multiplicative conservation, additive conservation, monotonic transformation};
  no relevant `research_db/papers/` stubs (math-methods gap, same as
  Slepian/Tong inherited from rb-008/rb-014/rb-015 — out of rebuilder
  scope per reviewer CR-035/CR-037). No new wiki writes; `audit.py` not
  re-run.

- **Next increment.** Natural dependency order suggests **RB-034**
  (manuscript §extensions-A3 — prereq RB-019 now done; the section has
  all six content blocks empirically backed and explicit figure paths
  listed in the backlog notes) as the obvious next thread continuation —
  it lands the third of the rebuild's three extension levers (A1 → A3
  → A2/A8) as a written manuscript section, closes the §extensions
  thread for A3, and gives the rebuilt paper its first conservation-family
  band statement in prose. Alternatives: **RB-013** (§appendix-C5
  light-touch manuscript section, prereq RB-001 + RB-015 both done; can
  now cite both the rb-015 conservation-form-invariance corollary AND
  the rb-016 numerical confirmation); **RB-014** (A2 heterogeneous-r
  model extension, opens the A2/A8 heterogeneity thread — the last of
  the three extension levers); **RB-033** (A3 derivation in the
  rebuild's voice, low-priority but spawned by rb-015 and can now cite
  the rb-016 TEST 3 numerical proof). **RB-034 is preferred** because
  it (a) consumes the rb-016 increment directly as figures + numbers,
  (b) closes the A3 manuscript thread in a single section, and (c)
  maintains the §3.3 unifying-reframe momentum (conservation rule as
  model assumption with band-reporting). Why the next run should care:
  the rebuilt manuscript currently has zero text about the conservation
  family beyond the model section's pointer; RB-034 fixes that with
  empirically-backed content for every claim in the section.

---

## rb-015 — 2026-05-25 — A3 conservation-family model extension (model increment) — DONE

- **Run id:** `rb-015-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-015 (extend `beta_gamma()` to a one-parameter conservation
  family with additive and multiplicative as special cases; thread the parameter
  through the model; add a recovery test that the additive case reproduces the
  inherited numbers byte-for-byte AND that the multiplicative case recovers the
  reviewer's logged A3 numbers to ULP tolerance). Prereq RB-001 done at
  rb-001.
- **Output kind:** model.
- **Claims touched:** A3 (CONTESTED) — the rebuilt strength already licensed
  the conservation-family band; rb-015 turns that license into a wired model
  + recovery contract. Plus C5 (CONFIRMED-UNDER-ATTACK) — gains a free
  *conservation-form-invariance* observation: at $r=1$, $\beta(1, p) =
  \gamma(1, p) = 1$ exactly for every conservation order $p$, so the C5
  symmetric-recovery result is conservation-form-invariant by construction
  (verified to floating-point identity: `policies(p=0, r=1) ==
  policies(p=1, r=1)`).
- **Headline thing built:** the **power-mean conservation family** in
  `Rebuild/model/core.py`. The function signature changes are
  back-compatible — every existing caller using the implicit additive form
  gets numerically identical output post-rb-015.

  - **`beta_gamma(r, p=1.0) -> (beta, gamma)`.** Constraint
    $M_p(\beta, \gamma) = 1$ with $\beta/\gamma = r$; closed-form solution
    $\gamma = (2/(r^p + 1))^{1/p}$, $\beta = r\gamma$ for $p \ne 0$, and
    $\gamma = 1/\sqrt{r}$, $\beta = \sqrt{r}$ at $p = 0$ (the geometric-mean
    limit). The $p = 1$ branch is a literal `return 2*r/(r+1), 2/(r+1)` —
    no `**` operator — so additive recovery is *binary*. Special cases:
    $p=1$ additive (paper A3), $p=0$ multiplicative ($\beta\gamma=1$,
    reviewer's A3 extension), $p=-1$ harmonic; intermediate $p$ traces a
    smooth band.
  - **`d_prime_asym(alpha, r, d_max, f0, h, N, p=1.0)`.** Threads `p` into
    `beta_gamma(r, p)`; the rest of the body is unchanged.
  - **`_alpha_opt(..., p=1.0)`.** Passes `p` into `d_prime_asym`.
  - **`HeadlineCell.cons_p: float = 1.0`.** New dataclass field, default
    additive.
  - **`policies(r, cell, ...)`.** Reads `cell.cons_p` and threads it through
    `_alpha_opt` and `d_prime_asym` for all four policies P1–P4.

  Module docstring extended with a "CONSERVATION FAMILY" block documenting
  the math and the $p$-special-case table; the "Extensions to consider"
  list removed the A3 item and added a "Done so far" subsection listing
  rb-001 (A1) and rb-015 (A3).

- **Recovery contract built:** `Rebuild/model/tests/test_conservation_family.py`
  — 14/14 PASS, sha256 `f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e`.
  Three surfaces:
  1. **Family identities.** `beta(r,p)/gamma(r,p) = r` exact to 4.4e-16
     across $r \in \{0.1, 0.316, 0.398, 1.0, 3.162, 10.0\}$ × $p \in
     \{-2, -1, -0.5, 0, 0.5, 1, 2\}$; `M_p(beta, gamma) = 1` exact to
     4.4e-16 across the same grid; `beta(1, p) = gamma(1, p) = 1` binary
     across $p \in \{-2..+2\}$ (the C5 conservation-form-invariance
     observation, hard-checked).
  2. **Additive $p=1$ byte-exact recovery.** `beta_gamma(r, p=1.0)`
     returns the legacy `(2r/(r+1), 2/(r+1))` *bit-for-bit* on the 21-point
     log-$r$ grid; `policies(r, HeadlineCell(cons_p=1.0))` reproduces the
     rb-001 `REVIEWER_TARGETS_RHO0` pins to **zero diff** at
     $r \in \{0.398, 1.0, 3.162\}$ (VDA, CF, R_P1, R_P4 all match to FP
     identity). **No legacy sim changes numerically — full back-compat
     verified.**
  3. **Multiplicative $p=0$ recovery vs reviewer A3.** `policies(r,
     HeadlineCell(cons_p=0.0))` reproduces the reviewer's logged A3
     multiplicative-family numbers
     (`Critique/replications/A3--multiplicative-conservation/output/results.json`
     `block_c2_c1.families.multiplicative`) on the 6-point pin set $r \in
     \{0.1, 0.316, 0.398, 1.0, 3.162, 10.0\}$ to within tolerance 1e-5
     (observed: max `|d|` ≤ 6.3e-7 on R_P1, ≤ 3.3e-7 on CF, ≤ 2.7e-7 on
     VDA). The residual is the same cross-Phi-backend ULP-level reordering
     rb-003 saw (paper's A&S 7.1.26 vs the rebuilt module's
     `scipy.special.ndtr`). Plus the symmetric-corner identity
     `policies(p=0, r=1) == policies(p=1, r=1)` to **floating-point
     identity** across all 8 returned keys.

  Re-ran rb-001 contract `test_recovery.py` post-edits → **7/7 PASS
  unchanged, sha256 `d3c62215…`** (full back-compat verified end-to-end:
  the rb-001 contract is preserved bit-for-bit by the new code path's
  default `cons_p = 1.0`).

- **Simulation evidence.** Family identities verified across $r \times p$
  grid: $\beta/\gamma = r$ exact to 4.4e-16, $M_p = 1$ exact to 4.4e-16.
  Multiplicative recovery: max `|d|` ≤ 6.3e-7 across VDA/CF/R_P1/R_P4 on
  the 6-cell pin set, sha256
  `f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e`.
  The rb-001 contract sha256 `d3c62215…` is unchanged.

- **What the manuscript can now say.** At the **CLAIM_LEDGER A3 row**: the
  rebuilt model implements the power-mean conservation family
  $M_p(\beta, \gamma) = 1$ with $\beta/\gamma = r$, indexed by `cons_p`
  on `HeadlineCell`; additive ($p=1$) is the inherited paper form, byte-
  exact recovered; multiplicative ($p=0$) is the reviewer's A3 extension,
  recovered to 6.3e-7. Conservation choice is a model assumption, not a
  derived statement; the rebuilt manuscript will report headline numbers
  (C1 CF, C2 peak VDA, C3 boundary) as a *band across* $p$ in a downstream
  A3 sweep increment (RB-019). At the **CLAIM_LEDGER C5 row**: the
  symmetric-recovery result is *conservation-form-invariant by
  construction* — for every $p$, $\beta(1, p) = \gamma(1, p) = 1$, so
  swapping the conservation rule does not move the $r = 1$ result. The
  manuscript §appendix-C5 (RB-013) can now cite this construction rather
  than introduce a one-line ad-hoc argument.

  The rebuilt manuscript may NOT yet say "headline numbers shift by X%
  between additive and multiplicative on the 4,410-cell sweep" — that
  band claim is licensed by the reviewer's A3 numerics but not yet
  *rebuilt-side* simulated; the sweep is RB-019.

- **Wiki sweep.** Keywords {power mean, generalised mean,
  Hardy-Littlewood-Pólya, conservation, asymmetric scaling, β+γ=2,
  β·γ=1}; no relevant `research_db/papers/` stubs (math-methods gap,
  same as Slepian/Tong inherited from rb-008/rb-014 — out of rebuilder
  scope per reviewer CR-035/CR-037). No new wiki writes; audit not
  re-run.

- **Next increment.** Natural dependency order suggests **RB-019**
  (A3 conservation-family band on headline numbers; sim, prereq RB-015
  now done) as the obvious next thread continuation — it turns the
  rebuilt-side family into a *rebuilt-side empirical band* on the
  manuscript's headline numbers, replacing the inherited §5.5
  single-sentence treatment of multiplicative conservation with the
  3.3 §unifying-reframe band. Alternatives: **RB-013** (§appendix-C5
  manuscript, prereq RB-001 done, low effort, can now cite the rb-015
  conservation-form-invariance corollary) closes the 5th headline-claim
  section; **RB-014** (A2 heterogeneous-r model extension, prereq RB-001
  done) opens the A2/A8 heterogeneity thread, the third of the rebuild's
  three extension levers. RB-019 is preferred because (a) it consumes the
  rb-015 increment directly via cell-wise band reporting and (b) it lands
  the §extensions-A3 manuscript section in two runs (RB-019 → RB-034).
  Why the next run should care: every queued manuscript-band claim on A3
  now has a wired, recovery-tested model under it; the band can be
  computed without re-inventing the conservation family.

---

## rb-014 — 2026-05-25 — C4 anti-cue inversion derivation (derivation increment) — DONE

- **Run id:** `rb-014-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-030 (independent re-derivation of `r†_inv = (N-1) A_0/B_0`
  in the rebuild's voice, ρ extension via one-factor GH quadrature, ρ→0 limit
  shown to collapse to reviewer's analytic form, symmetric-corner identity
  `r†_inv(V=1/N, v=1) = 1` promoted to Proposition 5.1 with full
  FOC-symmetry proof). Prereq RB-008 done at rb-012 (sha256 `6ad651d6…`).
- **Output kind:** derivation.
- **Claims touched:** C4 (CONFIRMED-CONDITIONAL) — translates rb-012's
  closed-form `_A0_B0` implementation (in `Rebuild/sims/C4--anti-cue-inversion/run.py`)
  and the four equations cited from §results-c4 (eq:value-weight, eq:left-derivative,
  eq:r-inv, eq:r-inv-corner) into a clean appendix-derivation file at the
  strength `CLAIM_LEDGER.md` already licenses for C4. Backing column extended
  with the new file; rebuilt strength unchanged. No A1 strength change either,
  though the derivation reuses the same one-factor GH machinery as the rebuilt
  model's `p_no_fa_grid` (Section §2 of the A1 derivation), so the ρ-extension
  here inherits the recovery contract sha256 `d3c62215…` end-to-end.
- **Headline thing built:** `Rebuild/derivations/C4--anti-cue-inversion.md`
  — ~42,062 bytes / 940 lines / 9 sections + Verification block + Extensions
  list. Independent of `Critique/derivations/C4--no-inversion.md` (same math
  but rebuild-voiced: constructive Proposition 3.1 + Theorem 6.1 + Proposition 5.1
  framing rather than 'paper claim X is incomplete'; fresh equation labels 1.1–9.x;
  ρ extension §4 is new; Proposition 5.1's formal FOC-symmetry proof of the
  symmetric-corner identity is new — reviewer's §5 records numerical confirmation
  + one-sided derivative algebra at the corner but does not promote to a proposition
  with ρ-inclusive proof).
  - **§1 setup + inversion-branch kink at $\alpha = 1/N$ via the $\benefit/\cost$
    swap.** Eqs. 1.1–1.4 (notation + reward + inversion-branch (1.4)); Eqs.
    1.5–1.6 the explicit one-sided $\dprime'(\alpha)$ at the boundary, named as
    the analytic source of the kink the inherited §4.5 paragraph does not
    mention.
  - **§2 boundary partials $A_0, B_0$ and one-sided $\Rew$-derivatives at
    $\alpha = 1/N$.** Eqs. 2.1–2.2 from envelope theorem; Eq. 2.3 defines
    $A_0, B_0$ as $\Rsens$-independent boundary partials at the jointly
    optimised criteria $(c_c^\star, c_u^\star)$; Eqs. 2.4–2.5 the right/left
    one-sided $\Rew$-derivatives carrying the $\benefit \leftrightarrow \cost$
    swap.
  - **§3 closed-form $\rstarinv = (N-1) A_0/B_0$.** Eq. 3.1 the left
    derivative in $\Rsens$-explicit form (linear in $\Rsens$ once $A_0, B_0$
    are pulled out); Eq. 3.2 sign characterisation; **Eq. 3.3 (boxed) the
    closed form**; Proposition 3.1 (boundary inversion threshold) names the
    iff equivalence with the local left-side-max condition. §3.1 documents
    the structural mirror to C2's $\rdagger(\val) = K_u(\val)/[(N-1)\,K_c(\val)]$ —
    both are ratios of $\Rsens$-independent boundary partials scaled by $(N-1)$.
  - **§4 ρ-extension via one-factor Gauss-Hermite reduction.** Eq. 4.1
    recapitulates $\Pnofa(\rho)$ as the one-factor integral the rebuilt
    model's `p_no_fa_grid` implements (matches `Rebuild/derivations/A1--rho-channel.md`
    §2.3 Eq. 2.3); Eqs. 4.2–4.3 differentiate inside the integral to give
    $\partial \Pnofa / \partial \dprime_c$ and $\partial \Pnofa / \partial \dprime_u$;
    Eq. 4.4 plugs these into (2.1)–(2.2) to give the ρ-aware $A_0(\rho), B_0(\rho)$.
    §4.3 takes $\rho \to 0$ explicitly: Eqs. 4.5–4.6 reduce the integrals to
    their independent-form counterparts (the $z$-dependence drops, the
    integrand factorises out of $\int \phi(z)\,\mathrm{d}z = 1$); Eqs. 4.7–4.8
    are the inherited analytic forms recovered bit-for-bit. The recovery is
    documented numerically by rb-012 Step A 48.6% vs reviewer §4 49.0%
    (PASS) and by rb-012's `_A0_B0` analytic-branch code at `run.py:223-233`.
  - **§5 Proposition 5.1 (symmetric-corner identity).** *Statement:*
    $\rstarinv(\valid=1/N,\val=1,N,\CR,\rho) = 1$ exactly, for any $N \ge 2$,
    any conservation variant, any $\rho \in [0,1)$. *Proof* (Eqs. 5.2–5.8): at
    the corner the FOC system for $(c_c^\star, c_u^\star)$ at
    $\dprime_c = \dprime_u = \dprime_{\mathrm{base}}$ is symmetric in
    $(c, b, \Phi, \phi)$ (cued value-weight $\valid\val = 1/N$ equals per-uncued
    weight $(1-\valid)/(N-1) = 1/N$; $\CR = 1$ under both variants; the no-FA
    cross-partial is symmetric in $(b_c, b_u)$ at $b_c = b_u$). The symmetric
    ansatz $c_c^\star = c_u^\star =: c^\star$ is consistent and (by joint
    concavity, the property `_optimal_criteria_at_uniform` exploits) the global
    maximiser. Under this, $p_c^H = p_u^H = p^H$, $\beta_c(z) = \beta_u(z) =
    \beta(z)$, and the per-channel weights line up to give Eqs. 5.4 + 5.6 + 5.7:
    $B_0(\rho) = (N-1)\,A_0(\rho)$ identically, so $\rstarinv = (N-1) A_0/B_0 =
    1$. The cancellation is exact, *independent of* $N$ (cancels in the ratio),
    *independent of* $\CR$ ($= 1$ at the corner), and *independent of* $\rho$
    (enters only through $I(\rho)$ common to both $A_0$ and $B_0$). QED.
    Remark documents: (a) numerical realisation — `step_A.tally.*.min_r_inv_star
    = 1.0000` in all four (variant A/B, $\rho \in \{0, 0.2\}$) panels of
    rb-012; (b) the bimodal local picture at the corner for $\Rsens > 1$ —
    $\alpha = 1/N$ becomes a local minimum, with two non-trivial maxima; the
    right-branch maximum dominates globally.
  - **§6 value-weight inequality + Theorem 6.1 global no-inversion.** §6.1
    derives Eq. 6.2 $w_c \ge w_u \iff \valid \ge 1/[(N-1)\val+1]$ and Eq. 6.3
    the universal worst-case form $\valid \ge 1/N$ at $\val = 1$. §6.2 documents
    the location-count asymmetry: the right branch can reach the per-location
    ceiling $\dprime_c = \dprimemax$ at $\alpha = 1$; the left branch caps the
    uncued $\dprime$ strictly below $\dprimemax$ for $N \ge 3$ because the
    $(N-1)$ uncued slots share the $(1-\alpha)/(N-1)$ budget per slot. §6.3
    combines (6.3) and §6.2 into **Theorem 6.1 (global no-inversion,
    conditional)**: under $\valid \ge 1/N$ and $\val \ge 1$, the global maximum
    of $\Rew$ has $\alpha^\star \ge 1/N$, with the right-branch maximum strictly
    dominating the left-branch global maximum. Proof sketched + empirically
    anchored to rb-012 Step B (0/12 global inversions across 12 adversarial
    cells under both $\rho \in \{0, 0.2\}$). §6.4 derives the anti-cue
    prediction from the *flipped* value-weight inequality (Eq. 6.4) at
    $\valid < 1/[(N-1)\val+1]$: the location-count asymmetry still caps the
    left branch, but the per-channel reward now favours the uncued slots, and
    for $\Rsens$ sufficiently large the global maximum crosses below $1/N$ —
    the new falsifiable prediction the rebuild adds. Empirical anchor: rb-012
    Step C 36.1% inversion incidence at $\rho = 0$ on the $N = 4$ anti-cue
    probe grid, $\val$-stratification ($75\% / 20.8\% / 12.5\%$ at $\val = 1, 3, 5$)
    matching the sharp boundary (Eq. 6.2).
  - **§7 numerical realisation and sim attribution.** Table mapping each
    derivation equation to its `run.py` line range and `results.json` block
    key; sha256 `6ad651d6…` cited; three recovery records:
    #1 (ρ=0 vs reviewer §4) 48.6% vs 49.0%, $\Delta = 0.4$ pp PASS at 1.0 pp
    tolerance; #2 (ρ=0 vs reviewer §5 Step C(i)) max|Δα| = 0 (FP exact),
    max|ΔR| = 3e-6 PASS; #3 (symmetric-corner identity under GH quadrature)
    min $\rstarinv$ = 1.0000 to FP identity in all four (variant, ρ) panels —
    a stronger statement than #1 because it survives the GH quadrature exactly.
  - **§8 scope.** Explicit non-promises: (3.3) is a *local* statement, not a
    global one; equicorrelated noise only (structured covariance out of scope);
    additive A3 only (conservation-family extension is RB-015/RB-019); Theorem
    6.1's empirical anchor is the inherited 4,410-row sweep + rb-012 Step B 12
    cells (not a fully formal envelope-theorem proof); anti-cue prediction is
    at $N = 4$, variant A only (variant B is RB-031, V-grid sharpening is RB-032).
  - **§9 references.** Inherited paper §4.5 + reviewer's parallel derivation
    by full path + companion sim (sha256) + manuscript §results-c4 + A1
    derivation cross-reference + Slepian 1962 + Tong 1990 by full
    bibliographic reference (same math-methods gap flagged in rb-008/rb-009;
    no new wiki stubs added by this run).
  - **Verification performed block.** ρ→0 collapse by inspection of run.py
    lines 223–233 against Eqs. 4.7–4.8; symmetric-corner identity verified
    algebraically (§5 proof) AND numerically (1.0000 across all four panels);
    48.6% vs 49.0% recovery PASS; one-sided derivatives cross-check at corner —
    both reduce to $A_0\,(\Rsens - 1)$ right / $A_0\,(1 - \Rsens)$ left up to
    the positive prefactor of (3.1), so the sign-flip is exactly at
    $\Rsens = 1 = \rstarinv$ as required; (6.2) algebraic verification.
  - **Extensions to consider** (4 candidate spin-off increments): (1) closed
    form for $\partial \rstarinv / \partial \rho$ (Slepian-style monotonicity
    on the $A_0/B_0$ ratio — would let the manuscript state the direction of
    the A1 shift as a theorem rather than empirics); (2) variant B anti-cue
    replication (RB-031, already queued); (3) conservation-family band on
    (3.3) (RB-015/RB-019, queued; the closed form's *shape* — ratio of
    boundary partials scaled by $(N-1)$ — is robust to A3 even though the
    constants change); (4) heterogeneous-$r_i$ generalisation (RB-014/RB-018,
    queued; would turn (3.3) into an $N$-dimensional sign-flip condition).
- **Simulation evidence (consumed; already established by rb-012):**
  sha256 `6ad651d648ae597cdfb28c6fd19b6261e4f9d5cb96b599557e10aad47ffd6d96`;
  17.4 s wall-clock; recovery #1 PASS (48.6% vs 49.0%); recovery #2 PASS
  ($|\Delta\alpha| = 0$, $|\Delta R| = 3 \times 10^{-6}$); the symmetric-corner
  identity 1.0000 to FP identity in all four `step_A.tally` panels is the
  numerical realisation Proposition 5.1 inherits. This run consumes the rb-012
  outputs without rerunning the sim — every cited number is sourced directly
  from `output/results.json` block-keys.
- **Recovery test:** N/A for a derivation-only increment beyond the three
  inherited recovery records cited in §7. The §model recovery contract
  (rb-001/rb-009, sha256 `d3c62215…`) and rb-012's two simulation recovery
  tests both remain in force.
- **Output hash:** `Rebuild/derivations/C4--anti-cue-inversion.md`
  $42{,}062$ bytes / $940$ lines. No manuscript PDF rebuild (derivation file
  is a standalone `.md`, not yet `\input{}`d into `main.tex`); a follow-up
  manuscript-only increment can `\input{}` it as an appendix subsection or
  cite it externally — the §results-c4 section already cites this file by
  path at the "deferred to Section sec:appendix (a separate increment, RB-030,
  queued)" sentence, which could be tightened in a future manuscript edit.
  PDF size unchanged from rb-013 at 27 pages / 1,814,626 bytes.
- **Wiki cross-references.** Sweep performed with keywords {boundary
  inversion, asymmetric attention transfer, β/γ kink, equicorrelated orthant,
  Gauss-Hermite reduction, value-weight inequality, location-count asymmetry,
  symmetric-corner FOC}; no new `research_db/papers/` stubs added (all
  invoked references are cross-references to `Critique/` or `Rebuild/` files;
  Slepian 1962 and Tong 1990 cited by full bibliographic reference per the
  same math-methods gap flagged by rb-008/rb-009 — the rebuilder is not
  adding math-methods stubs without owner direction). audit.py not re-run
  (no wiki writes).
- **What the manuscript can now say.** §results-c4's "the independent
  re-derivation in the rebuild's voice (plus the proof of the symmetric-corner
  identity below) is deferred to Section sec:appendix (a separate increment,
  RB-030, queued)" sentence (`Rebuild/manuscript/sections/results.tex` line
  ~1197) can now be replaced with a forward reference to
  `Rebuild/derivations/C4--anti-cue-inversion.md` § 5 Proposition 5.1 and
  § 4 Eqs. 4.2–4.4. The §results-c4 prose continues to claim only what the
  rebuilt strength licenses — no strength change. The appendix-derivation-C4
  subsection of `manuscript/sections/appendix.tex` could now `\input{}` the
  derivation file or reference it inline; the present run does not modify
  the manuscript prose (one-increment-per-run discipline, mission §9.5).
- **Why the next run should care.** The C4 thread is now (i) headline-claim
  manuscript section drafted (rb-013), (ii) simulation backing all numerics
  (rb-012), (iii) formal derivation in the rebuild's voice covering all four
  in-section equations + the symmetric-corner identity Proposition 5.1 +
  the global no-inversion Theorem 6.1 (this run). The natural next moves:
  RB-013 (§appendix-C5 light-touch consistency result; low effort; closes the
  five-headline-claim spine, leaving only the abstract/intro/limitations
  sections + the A2/A8/A3 extension threads) OR RB-026 (the C2 parallel:
  ρ-extension derivation of $\rdagger(\val)$, the same family of ρ-extended
  boundary closed forms; would consolidate the rebuilt model's two main
  closed-form thresholds — C2 and C4 — as parallel ρ-aware results). RB-014
  (A2 heterogeneous-$r_i$ model extension) is the largest unstarted thread
  and the most consequential remaining structural increment.

---

## rb-013 — 2026-05-25 — §results-C4 manuscript section (manuscript increment) — DONE

- **Run id:** `rb-013-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-012 (manuscript §results-C4: conditional theorem
  with explicit `V ≥ 1/N` condition + sharp form `V ≥ 1/[(N-1)v+1]`;
  closed-form local threshold `r†_inv = (N-1) A_0/B_0` with the
  symmetric-corner identity `r†_inv(V=1/N, v=1) = 1`; anti-cue
  inversion at `N=4` as a new falsifiable prediction; A1 cross-axis
  robustness across all four steps of the prerequisite sim). Prereq
  RB-008 done at rb-012 (sha256 `6ad651d6…`).
- **Output kind:** manuscript.
- **Claims touched:** C4 (CONFIRMED-CONDITIONAL) — translates rb-012
  sim evidence into main-text voice at the strength `CLAIM_LEDGER.md`
  already licenses; rebuilt strength unchanged, backing column
  extended with the new §results-C4 prose. A1 picks up cross-axis
  corroboration via the cross-axis-sensitivity paragraph (the A1
  decorrelation channel and the C4 inversion lever are independent
  mechanisms; ρ=0.2 quantitatively shifts `r†_inv` by 13-21% but does
  not erase the inversion regime). No A1 strength change.
- **Headline thing built:** `Rebuild/manuscript/sections/results.tex`
  §results-c4 — full section replacing the 7-line stub, ≈530 LaTeX
  lines, eight paragraphs:
  - **Claim restated at defensible strength.** Live verdict
    CONFIRMED-CONDITIONAL summarised; the two specific places the
    inherited §4.5 text is too strong (the local ``regardless of $r$''
    derivative wording, and the categorical ``never below'' that does
    not qualify the anti-cue regime) named; the conditional theorem
    voice + the anti-cue inversion as a new falsifiable prediction
    introduced.
  - **Mechanism + value-weight inequality.** Boxed Eq. value-weight:
    $w_c \ge w_u \iff \valid \ge 1/[(\Nloc - 1)\val + 1]$; $1/\Nloc$
    derived as the universal worst-case at $\val = 1$.
  - **Closed-form local threshold.** Eq. left-derivative
    ($\partial_\alpha R_{P1} |_{1/\Nloc^-}$); Eq. r-inv definition
    $\rstarinv = (\Nloc-1) A_0/B_0$; Eq. r-inv-corner symmetric-corner
    identity $\rstarinv(1/\Nloc, 1, \Nloc, \CR, \corr) = 1$ exactly,
    independent of $\Nloc, \CR, \corr$. ρ-extension stated (one-factor
    Gauss-Hermite-64 quadrature, $\corr\to 0$ recovery to reviewer's
    analytic form bit-for-bit); formal derivation deferred to RB-030.
  - **Closed-form tally on primary $(V, v)$ grid.** Table
    tab:c4-rstar-tally: $n$ / $\rstarinv \in [0.1, 10]$ /
    $\rstarinv > 10$ / $\min \rstarinv$ / $\mathrm{median}\, \rstarinv$
    per (variant, $\corr$) panel; the $\rstarinv = 1.0000$ minimum
    column documents the symmetric-corner identity recovered to FP
    identity; recovery vs reviewer 49.0% → 48.6% at $\corr = 0$
    (PASS). Figure fig:c4-rinv-closed-form ($\log_{10} \rstarinv$
    contours over $(V, v)$ at variant A/B, $\corr = 0$).
  - **Step B primary-sweep empirical confirmation.** Table
    tab:c4-stepB: 6 of 12 probes; 0 primary-sweep inversions across
    all 12 (cell, $\corr$) probes. Figure fig:c4-er-vs-alpha
    ($\Rew(\alpha)$ at the anti-cue cell $(V, v, N) = (0.15, 1, 4)$
    for $r \in \{0.5, 1, 3, 10\}$, both $\corr$, visualising the
    $\benefit/\cost$-kink bimodality and the global-inversion onset
    at $r \ge 1$).
  - **Anti-cue inversion prediction.** Table tab:c4-anticue: r/v/V
    stratifiers at $\corr = 0$ across the $V \in \{0.05, 0.10, 0.15,
    0.20\}$ × $v \in \{1, 3, 5\}$ × $r \in \{0.1..10\}$ probe grid.
    Total 36.1% inversions ($\corr = 0$), 34.7% ($\corr = 0.2$).
    The $\val$-stratifier (75% / 20.8% / 12.5% at $v = 1, 3, 5$) is
    the qualitative test of the sharp boundary
    eq:value-weight — at $v = 5$ inversion is confined to $V < 1/16$
    (only $V = 0.05$ qualifies); at $v = 1$ the boundary collapses to
    $V < 1/N$ and inversion is dense. **Headline figure
    fig:c4-alpha-star-map**: heatmap of $\alpha^\star(V, r)$ at
    $v = 5, N = 4$, both $\corr$; white horizontal line at $V = 1/N
    = 0.25$, red contour at $\alpha^\star < 1/N$ boundary; 6/272 =
    2.21% inversion incidence in both panels, zero cued-region
    inversions. C4 holds as a conditional theorem at both $\corr$.
  - **A1 cross-axis sensitivity.** All four Steps inventoried: Step A
    median $\rstarinv$ drops 13% (A) / 21% (B); Step B 0 inversions at
    both $\corr$; Step C $25$ vs $26$ inversions ($\Delta = 1$ at
    boundary); Step D 2.21% incidence at both. The A1 channel and the
    C4 inversion lever are independent mechanisms.
  - **Behavioural literature corroboration.** Wang-Theeuwes 2018
    statistical-learning suppression cited as the behavioural near-
    analog of the anti-cue inversion prediction (a
    high-probability-distractor location is a $V < 1/N$ slot in the
    model's coordinates → prediction match, not contradiction).
    Wang-Samara-Theeuwes 2019 + Kong-Li-Wang-Theeuwes 2020 cited as
    eye-tracking + reciprocal-reallocation corroboration. Failing-
    Theeuwes 2018 + Hickey 2010 cited as the cued-regime
    (value-driven capture: attention pulled toward, not away) match.
    Posner 1980 cited as the chance-validity boundary $\valid = 1/N$
    no-information limit.
  - **Limitations.** Variant B anti-cue → RB-031; finer V-grid
    inversion-onset bracket → RB-032; formal derivation file →
    RB-030. None weaken the headline.
  - **Reproducibility.** sha256 `6ad651d6...`; recovery #1 vs
    reviewer derivation §4 49.0% → 48.6% (PASS, tol 1.0 pp);
    recovery #2 vs reviewer derivation §5 Step C(i) table at
    $(V, v, N) = (0.25, 1, 4)$, variant A, $\corr = 0$,
    $r \in \{0.1, 1, 1.585, 2.512, 3.981, 10\}$:
    $\max |\Delta \alpha^\star| = 0$ (FP exact),
    $\max |\Delta R^\star| = 3 \times 10^{-6}$ (PASS, tol $5\times 10^{-5}$).
    Symmetric-corner identity eq:r-inv-corner recovered to FP
    identity in every panel of tab:c4-rstar-tally.
- **Simulation evidence (consumed; already established by rb-012):**
  sha256 `6ad651d648ae597cdfb28c6fd19b6261e4f9d5cb96b599557e10aad47ffd6d96`;
  17.4 s wall-clock; recovery #1 PASS (48.6% vs 49.0%); recovery #2
  PASS ($|\Delta \alpha| = 0$, $|\Delta R| = 3 \times 10^{-6}$).
  This run consumes the rb-012 outputs without rerunning the sim —
  every cited number is sourced directly from `results.json` block-
  keys (`step_A.tally`, `step_B.rows`, `step_C.incidence_by_r_rho0`,
  `step_C.rows`, `step_D.frac_inversion`, `recovery_step_Ci.rows`).
- **Recovery test:** N/A for a manuscript-only increment. The
  §model recovery contract (rb-008/rb-009, sha256 `d3c62215…`) and
  rb-012's two recovery tests both remain in force and are cited
  verbatim in the §results-c4 reproducibility paragraph.
- **Output hash:** PDF `main.pdf` 27 pages / **1,814,626 bytes**
  (was 21 / 1,570,450 at rb-011 = +6 pages, +244 KB). 4-pass build
  clean: `pdflatex` (pass 1: 3 missing-figure errors caught
  pre-emptively by build sequence) → `cp` 3 figures
  (`r_inv_closed_form.png`, `er_vs_alpha_anticue.png`,
  `alpha_star_V_r_map.png`) from
  `Rebuild/sims/C4--anti-cue-inversion/output/figures/` to
  `Rebuild/manuscript/figures/` → `pdflatex` (pass 2 with figures,
  6 undefined cite warnings) → `bibtex` (6 new entries:
  wang_theeuwes2018_statistical_learning_distractor_suppression,
  wang_samara_theeuwes2019, kong_li_wang_theeuwes2020,
  failing_theeuwes2018_selection_history,
  hickey2010_reward_salience_acc, posner1980_orienting) →
  `pdflatex` × 2 (refs settled; 0 undefined references in final
  pass; only cosmetic overfull/underfull hbox warnings remain).
- **What the manuscript can now say** (the exact rebuilt-strength
  ceiling, see CLAIM_LEDGER C4 row):
  > "Under $\valid \ge 1/\Nloc$ and $\val \ge 1$, the optimal
  > allocation satisfies $\alpha^\star_{\mathrm{global}} \ge 1/\Nloc$;
  > the empirical claim survives the $4{,}410$-cell primary sweep at
  > $\Nloc = 4$ and remains robust under A1 (Step B 0 inversions and
  > Step D 0 cued-region inversions at $\corr \in \{0, 0.2\}$). The
  > mechanism is the location-count asymmetry combined with the
  > value-weight inequality $w_c \ge w_u$ (equivalently
  > $\valid \ge 1/[(\Nloc-1)\val + 1]$, universally bounded by
  > $\valid \ge 1/\Nloc$ at $\val = 1$). The paper's `regardless of
  > $r$' wording is correct as a global claim but incorrect as a local
  > derivative statement: the left one-sided derivative at
  > $\alpha = 1/\Nloc$ has a closed-form sign-flip at
  > $\rstarinv = (\Nloc-1) A_0/B_0$, which falls inside $[0.1, 10]$
  > in $\approx 49\%$ of primary-sweep cells. Below $\valid = 1/\Nloc$
  > the model produces global inversion $\alpha^\star < 1/\Nloc$ —
  > a new falsifiable prediction of the rebuilt normative model,
  > verified across $36\%$ of probed anti-cue cells at $\Nloc = 4$,
  > with $\corr = 0.2$ essentially preserving both the inversion locus
  > and incidence. The behavioural near-analog —
  > statistical-learning-of-distractor-suppression
  > (Wang \& Theeuwes 2018; Wang, Samara \& Theeuwes 2019; Kong et al.\
  > 2020) — exhibits exactly the $\alpha^\star < 1/\Nloc$ allocation
  > the model predicts at $\valid < 1/\Nloc$, a prediction match
  > rather than a contradiction."
- **Wiki cross-references** (§11.1 sweep performed): keywords
  {anti-cue, counter-predictive cue, inverted attention, distractor
  suppression, statistical learning, value-driven capture,
  no-inversion, priority map, signal detection theory, location-count
  asymmetry, value-weight inequality}. All 4 cited research_db
  entries already wired (no new stubs added):
  wang_theeuwes2018_statistical_learning_distractor_suppression,
  failing_theeuwes2018_selection_history,
  hickey2010_reward_salience_acc, posner1980_orienting. Two
  papers cited by full bibliographic reference (Wang-Samara-Theeuwes
  2019 and Kong et al.\ 2020) — the reviewer's V0.2 evidence dossier
  did the same and explicitly defers their wiki stubs to CR-035/CR-037
  (out of rebuilder scope). audit.py not re-run (no wiki writes).
- **Why the next run should care:** RB-013 (§appendix-C5 consistency
  result) and RB-030 (formal C4 derivation file
  `Rebuild/derivations/C4--anti-cue-inversion.md`) are the natural
  next picks. RB-013 is the lowest-effort option (no new sim; reuses
  the rb-001 recovery contract) and would close out the four-headline
  results subsections + the C5 appendix. RB-030 consolidates the four
  closed forms now stated in §results-c4 (eq:left-derivative,
  eq:r-inv, eq:value-weight, eq:r-inv-corner) into a proper appendix
  derivation in the rebuild's voice — would let §appendix-deriv-c4
  point to a single file the way §appendix-deriv-a1 (rb-008,
  derivations/A1--rho-channel.md) and §appendix-deriv-c2 (queued
  RB-026) point to theirs. Beyond those, RB-014/RB-015 open the
  A2/A3 extension threads with model-level work; RB-005/RB-006/RB-007
  sims are all done so the only remaining sim-prerequisite work is
  in those extensions.

---

## rb-012 — 2026-05-25 — C4 anti-cue inversion (simulation increment) — DONE

- **Run id:** `rb-012-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-008 (simulation: `α*(V, r)` map across and below
  `V = 1/N` at `N = 4`, both `ρ ∈ {0, 0.2}`; closed-form `r†_inv`
  reproduced and extended; recovery against reviewer's CR-004
  derivation §5 Step C(i) and §4 49% closed-form percentage). Prereq
  RB-001 (model, rb-001) already done.
- **Output kind:** simulation.
- **Claims touched:** C4 (CONFIRMED-CONDITIONAL) — produces the
  simulation evidence the §results-C4 manuscript section will cite at
  defensible strength. A1 (CONTESTED) picks up cross-axis corroboration:
  ρ = 0.2 leaves the qualitative anti-cue pattern unchanged (25 vs 26
  inversions across 72 anti-cue probes); shifts the local boundary
  `r†_inv` quantitatively (median by 13% variant A / 21% variant B).
  No A1 strength change.
- **Headline thing built:** `Rebuild/sims/C4--anti-cue-inversion/`
  (run.py = 650 lines, README.md = 130 lines, output/results.json +
  three figures + run.log). 4-step probe + 2 recovery tests, 17.4 s
  wall-clock on python3.13 / scipy 1.17.1 / numpy 2.4.4 on darwin
  25.3.0 / Apple Silicon. The sim drives `Rebuild/model/core.py`
  exclusively — no model reimplementation — and extends the reviewer's
  ρ = 0 closed-form `r†_inv = (N-1) A_0/B_0` to ρ > 0 by computing
  `A_0(ρ)` and `B_0(ρ)` with the same one-factor Gauss-Hermite-64
  quadrature `Rebuild/model/core.py` already uses for `P_no-fa(ρ)`.
- **Simulation evidence (numbers + figures + sha256):**
  - **sha256: `6ad651d648ae597cdfb28c6fd19b6261e4f9d5cb96b599557e10aad47ffd6d96`** over the JSON content excluding wall-clock.
  - **Step A** (closed-form `r†_inv` on primary grid, 420 cells): at
    ρ = 0 the rebuild finds **48.6% of (V, v, variant) cells have
    `r†_inv ∈ [0.1, 10]`** — reviewer reports 49.0% (derivation §4),
    Δ = 0.4 pp, **recovery PASS** (tol 1.0 pp). At ρ = 0.2: 52.4% in
    range (median `r†_inv` drops 13% variant A / 21% variant B).
    Symmetric corner `r†_inv(V=1/N, v=1) = 1.0000` exactly at every
    (variant, ρ) — derivation §5 prediction confirmed.
  - **Step B** (full α-sweep at 6 most-adversarial primary-sweep cells
    at r=10, both ρ; 12 probes total): **zero inversions** —
    `α*_global ≥ 1/N` at every probe; right-branch global maximum
    strictly dominates the left-branch local maximum at all 12 cells.
    C4 holds at ρ = 0 AND under A1.
  - **Step C** (anti-cue regime at N=4, the rebuild's NEW evidence
    beyond reviewer's CR-004 at N=2; 144 cells): **36.1% anti-cue
    inversions at ρ = 0 (26/72), 34.7% at ρ = 0.2 (25/72)** — A1
    essentially preserves the inversion regime. r-stratified: 8% at
    r=0.1, 25% at r=0.5, 50% at r ∈ {1, 3, 5}, 33% at r=10. The
    v-stratification follows the sharp boundary `V < 1/[(N-1)v+1]`
    (derivation §6 Eq. 6.4): at v=5, N=4 inversion is confined to
    `V < 1/16 ≈ 0.0625` (only V=0.05 qualifies); at v=1 the boundary
    collapses to `V < 1/N` and inversion occurs at all four anti-cue
    V values for r ≥ 1.
  - **Step D** (α*(V, r) heatmap at v=5, N=4, both ρ; 544 cells): 2.2%
    inversion cells in each panel (all at V=0.05), **zero
    cued-region inversions** — C4 holds as a conditional theorem.
  - **Recovery #2** (reviewer derivation §5 Step C(i) table, V=0.25,
    v=1, N=4, ρ=0, r ∈ {0.1, 1.0, 1.585, 2.512, 3.981, 10.0}):
    max |Δα| = 0, max |ΔR| = 3e-6. **PASS both tolerances** (5e-4 / 5e-5).
  - **Figures:**
    - `figures/er_vs_alpha_anticue.png` — `E[R](α)` at the anti-cue
      cell V=0.15, v=1, N=4 for r ∈ {0.5, 1, 3, 10}, ρ = 0 and ρ = 0.2
      side-by-side. Visualises the β/γ-swap kink at α=1/N and the
      global-inversion onset (α* at the left grid edge for r ≥ 1).
    - `figures/alpha_star_V_r_map.png` — heatmap of α*(V, r) at v=5,
      N=4, both ρ ∈ {0, 0.2}. White horizontal line at V=1/N=0.25;
      red contour at the α*<1/N boundary. **Headline figure for
      §results-C4.**
    - `figures/r_inv_closed_form.png` — log₁₀ r†_inv contour over
      (V, v) at variants A/B, ρ=0. r†_inv=1 contour passes through
      (V=1/N, v=1) exactly.
- **Exact manuscript claim now licensed (§results-C4 lower bound):**
  > "Under V ≥ 1/N and v ≥ 1, the optimal allocation satisfies
  > α*_global ≥ 1/N globally; the empirical claim survives the 4,410-
  > cell primary sweep at N=4 and remains robust under A1 (ρ ≤ 0.2
  > leaves Step B 0 inversions and Step D 0 cued-region inversions
  > intact). The mechanism is the location-count asymmetry combined
  > with the value-weight inequality `w_c ≥ w_u` (equivalently
  > V ≥ 1/[(N-1)v+1], universally bounded by V ≥ 1/N at v=1). The
  > paper's `regardless of r` wording is correct as a *global* claim
  > but incorrect as a *local* derivative statement: the left
  > one-sided derivative at α=1/N has a closed-form sign-flip at
  > r†_inv = (N-1) A_0/B_0, which falls inside [0.1, 10] in ≈49% of
  > primary-sweep cells. Below V = 1/N the model produces global
  > inversion α* < 1/N — a new falsifiable prediction of the rebuilt
  > normative model, verified across 36% of probed anti-cue cells at
  > N=4 (the paper's primary topology), with ρ = 0.2 essentially
  > preserving both the inversion locus and incidence."
- **Why the next run should care:** RB-012 (§results-C4 manuscript
  section) is now unblocked. The rb-012 sim provides the closed-form
  r†_inv anchor, the anti-cue inversion incidence numbers, the α*(V, r)
  headline figure, and the two recovery tests the §results-C4 prose
  will cite. Three follow-ups spawned (RB-030 derivation, RB-031
  variant B anti-cue replication, RB-032 V-grid sharpening) — all are
  optional sharpening passes the manuscript can defer.

---

## rb-011 — 2026-05-25 — §results-C3 + §5.2 redraft (manuscript increment) — DONE

- **Run id:** `rb-011-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-011 (manuscript §results-C3, graded regime
  boundary, AND a §5.2-replacement experimental-design recommendation
  paragraph anchored to the rb-010 contour band). Prereq RB-007
  (rb-010 simulation, sha256 `72820559…`) already done.
- **Output kind:** manuscript.
- **Claims touched:** C3 (CONTESTED) — translates the rb-010 sweep
  into main-text voice at the strength `CLAIM_LEDGER.md` already
  licenses; rebuilt strength unchanged, backing column extended with
  the new §results-C3 prose. A1 picks up a *passing* mention via the
  `(V, v)`-plane sign-flip generalisation already wired in the
  CLAIM_LEDGER A1 row (no strength change).
- **Headline thing built:** `Rebuild/manuscript/sections/results.tex`
  §results-c3 — full section replacing the 9-line stub, ~280 LaTeX
  lines, seven paragraphs:
  - **Claim restatement.** States that the live C3 verdict is
    CONTESTED, that the qualitative ``narrow regime'' reading is
    sustained, and that the inherited §5.2 categorical
    ``regardless of other parameters'' wording is too strong; the
    rebuilt C3 is presented as a graded/quantitative contour band
    plus a hedged design recommendation.
  - **Sweep design.** Headline configuration $(N, d'_{\max}, f_0, h)
    = (4, 2, 0.5, \sqrt{})$ under variant A; $V \in [0.25, 1.00]$
    step $0.025$ (31 pts), $v \in [1, 10]$ step $0.5$ (19 pts),
    $r \in \{0.3, 1, 3\}$, $\rho \in \{0, 0.2\}$; $3{,}534$ cells
    total. Phi backend `scipy.special.ndtr`, $n_q = 64$
    Gauss--Hermite nodes.
  - **Iso-VDA contour band.** Figure `fig:iso-vda-contours`
    (`iso_vda_contours.png`, the 2×3 panel grid, $\rho$ × $r$);
    qualitative reading: bulk of $(V, v)$ near-zero VDA (median
    $\le 0.007$ every panel), substantial VDA confined to a corner
    along low $V$, high $v$, narrowing with $r$.
  - **Distributional summary.** Table `tab:c3-marginals` —
    $\VDA_{\min} / $ median $/ q_{95\%} / \VDA_{\max} /
    \mathrm{frac}\!\ge\!0.005 / \mathrm{frac}\!\ge\!0.05$ per
    $(r, \rho)$ panel, sourced from
    `summary.r=<r>__rho=<rho>`. Peak VDA drops from $0.173$ at
    $r=0.3$ to $0.062$ at $r=3$; $\mathrm{frac}\!\ge\!0.05$ from
    $28.7\%$ to $1.2\%$.
  - **§5.2 replacement.** Table `tab:c3-highV-probe` — peak VDA
    over the $v$-grid at $V \in \{0.4, 0.6, 0.8, 0.95\}$ for each
    $(r, \rho)$, with the cross-strata pattern: $V \ge 0.95$
    survives strictly; $V \ge 0.80$ survives at $\rho=0$ but admits
    a $\rho$-conditional caveat (max $0.0032$ at $\rho=0.2, r=3$);
    $V \ge 0.60$ fails (peak $0.164$ at $r=0.3, \rho=0.2$). Three
    itemized statements + a boxed quote replacing the inherited
    sentence: ``Spatial cueing paradigms targeting a
    `negligible-VDA' regime should adopt $V \gtrsim 0.95$
    unconditionally, or $V \gtrsim 0.8$ if cross-location
    correlation can be bounded below $r_{SC} \approx 0.2$. The
    inherited threshold $V \ge 0.75$ is too permissive: at
    $V \in [0.6, 0.8)$ the cost-dominant regime $r \in (0, 0.5)$
    admits peak VDA up to $\approx 0.16$.'' Figure
    `fig:vda-at-high-V` (`vda_at_high_V.png`, 1×3 $r$-panels with
    $V$-strata curves).
  - **A1 sign-flip across $(V, v)$.** Figure `fig:iso-vda-drho`
    (`iso_vda_drho.png`, signed $\Delta\VDA$ contour) and Table
    `tab:c3-sign-flip` (per-$r$ frac\_amp / frac\_supp / mean
    $\Delta$ / max amp $(V, v)$ / max supp $(V, v)$ sourced from
    `rho_sensitivity.r=<r>`). Documents the
    cross-axis sign-flip generalisation ($r=0.3$ suppression-dominant,
    $r \in \{1, 3\}$ amplification-dominant) and the
    dormant-cell amplification at $(V, v, r) = (0.7, 10, 0.3)$:
    $\VDA(\rho{=}0) = 0.0007 \to \VDA(\rho{=}0.2) = 0.0676$
    (96$\times$ amplification in a normally-dormant high-$V$ cell),
    flagged as the candidate falsifiable A1 prediction at the end
    of §limitations.
  - **Scope.** Variant-B contour band $\to$ RB-027 (queued);
    threshold sharpening to $\pm 0.01$ in $V$ $\to$ RB-028;
    dormant-cell closeup $\to$ RB-029; cell-wise sign-flip across
    the broader 4,410-cell sweep $\to$ RB-025.
  - **Reproducibility.** sha256 `72820559…`; recovery against
    rb-006 anchor at $|\Delta \VDA| = 1.27 \times 10^{-7}$ (the
    residual is the rb-006 reference's 6-dp rounding; model
    residual is zero); value-blind sanity $v = 1 \Rightarrow VDA = 0$
    holds identically across every cell of the sweep.
- **Simulation evidence (already established by rb-010):** sha256
  `72820559e1c1ab1919f74308623eaf4230aa3ea92ad3d9c62d81e993e4f27de6`;
  recovery PASS at $|\Delta| = 1.27\mathrm{e}{-7}$. This run consumes
  the rb-010 outputs without rerunning the sim — every cited number
  is sourced directly from `results.json` block-keys recorded in the
  table captions.
- **Recovery test:** N/A for a manuscript-only increment. The §model
  recovery contract (rb-008/rb-009, sha256 `d3c62215…`) and the
  rb-010 recovery against the rb-006 anchor both remain in force and
  are cited verbatim in the §results-c3 reproducibility paragraph.
- **Output hash:** PDF `main.pdf` 21 pages / 1,570,450 bytes (was
  16 / 1,177,200 at rb-009 — $+5$ pages, $+393$ KB).
- **What the manuscript can now say** (the exact rebuilt-strength
  ceiling, see CLAIM_LEDGER C3 row):
  > ``Across $(V, v) \in [0.25, 1.0] \times [1, 10]$ for $r \in
  > \{0.3, 1, 3\}$ and $\rho \in \{0, 0.2\}$ (variant A, headline
  > cell), VDA concentrates at low $V$, high $v$, moderate-low $r$:
  > peak VDA $= 0.17$ at $r = 0.3$ falls to $0.06$ at $r = 3$. The
  > inherited §5.2 categorical claim `negligible VDA at high $V$
  > regardless of other parameters' is supported conditionally: at
  > $V \ge 0.95$ peak VDA $\le 10^{-5}$ for every $(r, \rho)$ in
  > the envelope; at $V \ge 0.80$ $\le 0.003$ with a small
  > $\rho$-conditional caveat; at $V \ge 0.60$ it fails (peak
  > $0.16$). The rebuilt §5.2 recommendation is therefore: target
  > $V \gtrsim 0.95$ unconditionally, or $V \gtrsim 0.8$ if
  > $r_{SC} \le 0.2$; the inherited $0.75$ threshold is too
  > permissive.''

  The §results-A1 voice picks up a *passing* corroboration in
  §results-c3: the rb-002 / rb-004 sign-flip generalises to the
  $(V, v)$ plane (cell-wise pattern is $r$-dependent: $r=0.3$
  suppression-dominated, $r \ge 1$ amplification-dominated).
  Strongest single amplification at $(V, v, r) = (0.7, 10, 0.3)$
  lifts $\VDA = 0.0007 \to 0.0676$ at $\rho = 0.2$ --- flagged as
  the candidate falsifiable A1 prediction.
- **Backlog update:** `RB-011 \to done` with full notes (sourcing
  block-keys recorded in every table caption, build chain
  documented). No follow-up tasks spawned by this run beyond what
  rb-010 already queued (RB-025, RB-027, RB-028, RB-029); the
  §results-c3 scope paragraph already cross-references all four.
  Next-priority recommendation: **RB-008** (C4 anti-cue inversion
  sim) opens the third headline-claim thread and lands the new
  falsifiable anti-cue prediction the rebuild adds (mission §3.1
  C4 row); secondary options **RB-014** (A2 heterogeneous-$r$
  model extension; opens A2/A8 thread) and **RB-013**
  (§appendix-C5 light-touch consistency result, no new sim needed).
- **CLAIM_LEDGER:** C3 row's `backing` column extended from
  ``Manuscript prose queued (RB-011)'' to citing the new
  §results-c3 section, the three figures `\\includegraphics`d, the
  three numbered tables (`tab:c3-marginals`, `tab:c3-highV-probe`,
  `tab:c3-sign-flip`), the boxed §5.2 replacement quote, and the
  21-page / 1.5 MB build. C3 rebuilt-strength column unchanged
  (this run translates licensed bands into prose; per-sentence
  claims do not exceed what rb-010 already established).
- **Wiki cross-references:** mechanism keywords swept against
  `research_db/` --- `iso-VDA`, `narrow regime`, `validity
  threshold`, `experimental design`, `signal detection theory`,
  `cross-location correlation`, `equicorrelated Gaussian`. Findings:
  the §5.2 replacement cites `CohenMaunsell2009` (already in
  refs.bib from rb-009); `ruff_cohen2016_cross_area_correlations`
  and `srinath2021_attention_information_flow` already wired by the
  §model section but not load-bearing here; no novel external
  citation introduced by this manuscript increment (the contour
  band, the §5.2 threshold table, and the sign-flip generalisation
  are theorems of the rebuilt model's own definitions). No new
  `research_db/papers/` stubs added (audit.py not re-run).
- **Why the next run should care:** RB-011 closes the second
  ``unifying reframe'' §3.3 item (the §5.2 categorical $\to$ graded
  / quantitative transition), parallel to the §results-c1 closure
  of the §5.1 categorical floor by rb-007. Three of the four
  headline claims (C1 distributional, C2 confirmed + strengthened,
  C3 graded) now have manuscript sections; C4 (conditional theorem
  + anti-cue inversion) is the remaining headline claim, and its
  model machinery is already in place (the rebuilt `policies()`
  brackets $\alpha^\star$ to $[1/N, 1]$ by construction and rb-010
  verified ``no inversion above $V = 1/N$'' in passing across
  3,534 cells). RB-008 would land the third headline-claim sim
  with high marginal value: the anti-cue inversion is the
  rebuild's only entirely new falsifiable prediction beyond the
  inherited paper's results, and the rb-010 §results-c3 prose has
  established the methodological template ($(V, v)$ cell sweep,
  conditional threshold reporting, sign-flip generalisation) that
  RB-008 will reuse directly.

---

## rb-010 — 2026-05-25 — iso-VDA contour sweep over (V, v) (simulation increment) — DONE

- **Run id:** `rb-010-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-007 (C3 simulation — iso-VDA contour maps over
  `(V, v)` at `r ∈ {0.3, 1, 3}` and `ρ ∈ {0, 0.2}`, variant A; quantitative
  / graded boundary of the narrow-regime claim, not the inherited
  paper's categorical "negligible VDA at high V *regardless of other
  parameters*"). Pre-req `RB-001` (model with ρ channel) already done.
- **Output kind:** simulation.
- **Claims touched:** C3 (graded/quantitative regime boundary); A1
  (the `ρ=0.2` panel exhibits the sign-flip of `dVDA/dρ` across the
  `(V, v)` plane, generalising the headline-cell rb-002 result and the
  v-family rb-004 result to the third axis V).
- **Headline thing built:** `Rebuild/sims/C3--iso-vda-Vv/` — a 3,534-cell
  sweep (31 V × 19 v × 3 r × 2 ρ) producing three publishable figures
  (`iso_vda_contours.png` 2×3 panel grid = the manuscript §results-C3
  headline figure; `vda_at_high_V.png` 1×3 panel grid at V strata
  `{0.4, 0.6, 0.8, 0.95}` directly answering the §5.2 categorical claim;
  `iso_vda_drho.png` 1×3 signed contour of `ΔVDA` over `(V, v)` showing
  the A1 sign-flip topology). README, run.py with the rb-006 recovery
  anchor wired in, deterministic `results.json` hashed `72820559…`.
- **Simulation evidence (the load-bearing numbers):**
  - Peak VDA per panel (variant A): `0.173 (r=0.3, ρ=0) / 0.178 (r=0.3,
    ρ=0.2) / 0.157 (r=1, ρ=0) / 0.155 (r=1, ρ=0.2) / 0.062 (r=3, ρ=0)
    / 0.062 (r=3, ρ=0.2)`. Median VDA `≤ 0.007` in every panel — most
    of `(V, v)` is near-zero, but a quantitatively bounded corner is
    not.
  - `frac VDA ≥ 0.05` per panel: `28.7% / 29.5% / 21.9% / 23.6% / 1.2% /
    1.9%` — the benefit-dominant `r=3` panels are essentially flat.
  - §5.2 categorical-claim probe at high V (peak VDA over `v ∈ [1,10]`,
    `r ∈ {0.3, 1, 3}`, bracketed `ρ=0 / ρ=0.2`):
      - `V = 0.95`: `0.0000 / 0.0000` for every `r` — categorical
        "negligible regardless of v, r" SURVIVES at this strict
        threshold.
      - `V = 0.80`: `0.0000 / 0.0000` at `r=0.3`; `0.0000 / 0.0023` at
        `r=1`; `0.0000 / 0.0032` at `r=3` — survives at `ρ=0`,
        ρ-conditional small caveat at `ρ=0.2`.
      - `V = 0.60`: peak `0.143 / 0.164` at `r=0.3` — FAILS. "High V"
        for the §5.2 sentence must mean `V ≳ 0.8`, not `V ≳ 0.6`.
  - A1 sign-flip across `(V, v)` (`ΔVDA = VDA(ρ=0.2) − VDA(ρ=0)`):
    `r=0.3` → 27.2% cells amplified, 37.2% suppressed (cost-dominant
    regime mostly suppression); `r=1.0` → 52.8% / 17.5% (mostly
    amplification); `r=3.0` → 54.0% / 16.1% (mostly amplification).
    Strongest single amplification: at `(V=0.7, v=10, r=0.3)` a
    near-zero cell `VDA=0.0007` at `ρ=0` lifts to `VDA=0.0676` at
    `ρ=0.2` — a 96× amplification in a previously-dormant `(V, v)`
    cell. Strongest single suppression: at `(V=0.25, v=8.5, r=0.3)`
    `VDA` drops from `0.0388` to `0.0284` (`ΔVDA=−0.0105`).
- **Recovery test:** rb-006 anchor at `(V=0.5, v=5, r=1, ρ=0, variant A)`
  → expected VDA `0.039825`, observed VDA `0.0398251274…`, `|Δ| = 1.27e-7`
  vs tolerance `1e-4` — **PASS**. Residual is the rb-006 reference's
  6-dp rounding; the rebuilt model is bit-exact deterministic so the
  model residual is zero. Independent sanity check: `v=1` column is
  identically zero across every `(V, r, ρ)` cell (value-blind baseline
  ⇒ joint optimum = value-blind allocation ⇒ `VDA = 0`).
- **Output hash:** `results.json` sha256 = `72820559e1c1ab1919f74308623eaf4230aa3ea92ad3d9c62d81e993e4f27de6`.
- **What the manuscript can now say** (the exact rebuilt-strength
  ceiling, see CLAIM_LEDGER C3 row):
  > "Across `(V, v) ∈ [0.25, 1.0] × [1, 10]` for `r ∈ {0.3, 1, 3}` and
  > `ρ ∈ {0, 0.2}` (variant A, headline cell), VDA concentrates at low
  > V, high v, moderate-low r: peak VDA = 0.17 at `r = 0.3` falls to
  > 0.06 at `r = 3`. The §5.2 categorical claim 'negligible VDA at
  > high V regardless of other parameters' is supported conditionally:
  > at `V ≥ 0.95` peak VDA ≤ 1e-5 for every `(r, ρ)` in the envelope;
  > at `V ≥ 0.80` ≤ 0.003 with a small ρ-conditional caveat; at
  > `V ≥ 0.60` it fails (peak 0.16). The rebuilt §5.2 advice
  > [drafted in RB-011] states V* ≳ 0.8 as the quantitative threshold,
  > with the iso-VDA contour band as the substrate."
  The §results-A1 voice picks up a *passing* corroboration: the
  rb-002 / rb-004 sign-flip generalises to the `(V, v)` plane (cell-
  wise pattern is r-dependent: `r=0.3` suppression-dominated, `r ≥ 1`
  amplification-dominated). Manuscript A1 row may now state the
  sign-flip "across the (V, v, r) cube" rather than "at the headline
  cell".
- **Backlog update:** `RB-007 → done` with full notes; spawned
  `RB-028` (threshold-sharpening V ∈ [0.75, 0.90] step 0.005, low
  priority; the rb-010 grid step 0.025 already brackets V* to ±0.05
  — sharper only needed if a referee asks) and `RB-029` (closeup on
  the `(V≈0.7, v=10, r=0.3)` dormant-cell amplification phenomenon,
  low priority; the strongest qualitative finding deserves a clean
  before-the-prose look). `RB-011` (§5.2 redraft + §results-C3
  manuscript section) now has all prereqs satisfied — natural next
  manuscript increment.
- **CLAIM_LEDGER:** C3 row's `backing` column updated from "not yet
  wired" to citing rb-010 sim + three figures; rebuilt-strength row
  expanded with quantitative band numbers. A1 row's `rebuilt strength`
  expanded with the cell-wise (V, v) sign-flip generalisation (rb-010
  acts as cross-axis corroboration of the rb-002 derivation §4).
- **Wiki cross-references:** mechanism keywords swept against
  `research_db/` — `narrow regime`, `iso-VDA`, `validity threshold`,
  `experimental design`, `signal detection theory`, `equicorrelated
  Gaussian`, `attention modulation`. Findings: no new
  `research_db/papers/` stubs added (no novel external citation
  introduced by this sim — the figures are theorems of the rebuilt
  model's own definitions; the existing `cohen_maunsell2009_correlations`,
  `ruff_cohen2016_cross_area_correlations`, `srinath2021_attention_
  information_flow`, `muller_findlay1987_sensitivity_criterion` are
  the relevant entries and are already wired by the §model + §results-C1
  sections). `audit.py` not re-run (no wiki writes).
- **Why the next run should care:** RB-011 is now the natural next
  increment — it discharges the §3.3 "unifying reframe" item #2 (§5.2
  categorical → graded), pairing rb-010's bands with prose. Alternative
  parallel threads: RB-008 (C4 anti-cue inversion sim, opens the
  inversion-prediction thread) or RB-014 (A2 heterogeneous-r model
  extension, opens the heterogeneity thread). RB-011 is preferred
  because (a) its figures are already in publishable form, (b) it
  closes a §3.3 reframe item the rb-009 §model section opened, and
  (c) manuscript-prose increments compound the visible deliverable
  (PDF page count) more directly than another sim.

---

---

## rb-009 — 2026-05-25 — §model section, the "three levers" reframe (manuscript increment)

- **Run id:** `rb-009-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-004 (Draft `Rebuild/manuscript/sections/model.tex`:
  the rebuilt model with the ρ channel, stating the 'three levers'
  reframe and what independence actually upper-bounds — CF, not VDA).
  Both prereqs were already done: RB-002 (rb-002 backing simulation,
  sha256 `b692c064…`) and RB-003 (rb-008 derivation
  `Rebuild/derivations/A1--rho-channel.md`).
- **Output kind:** manuscript
- **Claims touched:** A1 (CONTESTED — manuscript section translates the
  rb-008 derivation into main-text voice without expanding any claim;
  rebuilt strength column of `CLAIM_LEDGER.md` unchanged; *backing*
  column extended with the new §model section).
- **Status:** done

### Headline thing built

`Rebuild/manuscript/sections/model.tex` — the §model section of the
rebuilt manuscript, 5 subsections / ~280 LaTeX lines, replacing the
rb-005 skeleton stub. Pulls the rb-008 derivation up into main-text
voice at the strength `CLAIM_LEDGER.md` licenses and at no higher
strength. The five subsections:

- **§2.1 `sec:model-inherited` — compact SDT skeleton.** Restates the
  per-location decision model (Eq. `sdt-marginal`), the
  attention-to-sensitivity transfer, the additive variant-A
  conservation rule `β + γ = 2` (flagged for the §limitations
  sensitivity band), the four nested policies P1–P4 over the
  expected-reward expression (Eq. `expected-reward`), and the two
  derived metrics `VDA` (Eq. `vda-def`) and `CF`
  (Eq. `cf-def-model`). Compressed enough that the reader can move
  through it as a notation reminder without re-deriving anything; the
  full derivation lives in the appendix.
- **§2.2 `sec:model-booking` — the locus of A1.** Localises A1 to the
  single product (Eq. `pnofa-indep`)
  $P_{\text{no-fa}}^{\text{indep}} = \Phi(b_c)\Phi(b_u)^{N-1}$ inside
  (Eq. `expected-reward`); the rest of the reward is linear in
  marginal hit rates and therefore A1-independent. A remark
  explicitly separates A1 from the A6 (homogeneous decision rule)
  relaxation that a pooled detection statistic would implement —
  carrying forward §1.2 of the rb-008 derivation.
- **§2.3 `sec:model-rho-channel` — the decorrelation channel.**
  Promotes A1 to a tunable equicorrelation parameter
  $\rho \in [0, 1)$; one-factor decomposition; boxed Eq. `pnofa-rho`
  for the exact 1-D orthant integral; recovery contract
  Eq. `rho-zero-recovery` tied to sha256 `d3c62215…` (7/7 PASS) at
  floating-point identity, including the headline peak
  $\text{VDA}^\star(\rho=0) = 0.07986$; n_q=64 Gauss–Hermite
  quadrature with $\le 10^{-15}$ error against n_q=128 on the
  operating $\rho \in \{0, 0.05, 0.1, 0.2, 0.3, 0.4\}$ band;
  empirical envelope $\rho \in [0, 0.4]$ bracketing the
  Cohen & Maunsell 2009 $r_\mathrm{SC} \approx 0.2$ in V4
  (\cite{CohenMaunsell2009}); structured-covariance scoped limitation
  citing \cite{RuffCohen2016, Srinath2021}.
- **§2.4 `sec:model-three-levers` — three levers, not two.**
  Definition `def:three-levers` names the three independent
  mechanisms (criterion shift, sensitivity re-allocation,
  decorrelation) with their reward decompositions (CF, VDA, Slepian
  monotonicity respectively, \cite{Slepian1962}). Frames decorrelation
  as the lever the inherited paper held implicitly fixed at the
  boundary, not a free third lever the rebuild adds.
- **§2.5 `sec:model-upper-bound` — what independence actually upper-
  bounds.** Explicitly retracts the inherited §5.5 sentence. Reports
  pointwise VDA excess over the $\rho=0$ curve $+4.84\times10^{-3}$
  (ρ=0.1) → $+1.01\times10^{-2}$ (ρ=0.4); sign-flip of
  $\partial \text{VDA}/\partial \rho$ in
  $r \in [0.38, 0.56]$ variant A and $r \approx 0.26$ variant B
  (Figures `vda-rho-variantA` and `vda-rho-variantB`). Reports CF(ρ)
  monotone-down in ρ at the headline cell in variant A
  (Figure `cf-vs-rho`) and the cell-wise generalisation across the
  rb-003 4,410-cell sweep: 84% one-sided in variant A, 64% in
  variant B (24% increase, 13% flat). Closes with a blockquote
  stating the corrected version of the inherited §5.5 sentence: a
  variant- and cell-conditional ceiling on CF best stated at the
  median across the sweep, not a uniform inequality, and decisively
  not an upper bound on VDA.

### How it connects to the ledger

Discharges the manuscript-side half of the A1 row of the
`CLAIM_LEDGER.md`. After rb-008, the A1 row's *backing* column
listed model code, recovery test, sim, and derivation; after rb-009
it also lists the §model manuscript section. The *rebuilt strength*
column is unchanged — this run is a translation increment, not an
expansion. Two explicit guard-rails honoured against §3 of the
mission prompt:

1. *Stating no claim more strongly than the live ledger licenses.*
   Both the "three levers, not two" reframe and the variant- and
   cell-conditional CF upper-bound clause are stated at the
   `CLAIM_LEDGER.md` A1 ceiling. The §5.5 retraction is stated
   neither as a categorical claim ("VDA is upper-bounded by ρ=0")
   nor as a derivable theorem; it is stated as a reported finding
   on the empirical envelope of the rb-002 sim and the rb-003 sweep,
   with the variant-B caveat preserved verbatim (24% of cells
   increase in ρ, 13% flat).
2. *Distributional / conditional voice by default.* The CF upper-
   bound clause carries the explicit "84% / 64% / median across the
   sweep" qualifier; the sign-flip locus is bracketed in
   $r \in [0.38, 0.56]$ with the empirical envelope named; the
   variant-B counterpart figure is included with its own caption
   noting the shifted sign-flip locus. The §5.5 retraction is a
   blockquote that names what the inherited paper *should* have
   said.

### Simulation evidence

No new simulation in this run; the §model section cites the existing
ones:

- `Rebuild/sims/A1--rho-channel/output/figures/vda_curves_variantA.png`
  → `Rebuild/manuscript/figures/vda_curves_variantA.png`
  (Figure `vda-rho-variantA`, the variant-A pointwise sign-flip
  panel).
- `Rebuild/sims/A1--rho-channel/output/figures/vda_curves_variantB.png`
  → `Rebuild/manuscript/figures/vda_curves_variantB.png`
  (Figure `vda-rho-variantB`, the variant-B counterpart with
  sign-flip $r \approx 0.26$).
- `Rebuild/sims/A1--rho-channel/output/figures/cf_vs_rho.png`
  → `Rebuild/manuscript/figures/cf_vs_rho.png`
  (Figure `cf-vs-rho`, the variant-A CF(ρ) monotone-down family at
  three $r$ anchors).

Backing sim digests cited verbatim in the §model text: rb-002 sha256
`b692c06456530ccd1b319762d8a948814324d3129f39902ce9531a66d1206614`
(the headline-cell A1 sim); rb-003 sha256
`91fc4692dbc106eca9c90770c79e22f7f4757d76421ed55e7e8e91f80e44706c`
(the 4,410-cell C1 sweep, sourced for the cell-wise generalisation
of the CF upper-bound). Recovery test digest
`d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f`
cited in §2.3 in the recovery-contract paragraph (Eq.
`rho-zero-recovery`).

### What the manuscript can now say

After rb-009 the manuscript can state (at no higher strength) the
"three levers, not two" reframe in §model and reference it from
§intro and §results without forward-referring to the appendix. It
can include the corrected version of the inherited §5.5 sentence
in §model and reference it again in §limitations as the disposition
of the inherited paper's most consequential self-characterisation.
The §results sections for C1 (rb-007) and C2 (rb-006) already
cross-reference §model via `\ref{sec:model}` / `\ref{sec:results-c1}`;
those cross-references now resolve to filled content rather than
stubs.

### Next increment

The two natural next manuscript-side threads are independent and
either is a reasonable next pick:

- **RB-007 (C3 iso-VDA contour sim)** + **RB-011 (§5.2 design-advice
  redraft)**. This thread would discharge another §3.3 "unifying
  reframe" item: the §5.2 categorical experimental-design claim
  ("high-validity paradigms show negligible VDA regardless of other
  parameters") gets replaced with a graded / quantitative
  recommendation grounded in an iso-VDA contour band over $(V, v)$
  at several $r$. Model→sim order: RB-007 (sim) is the next
  increment; RB-011 (manuscript) follows once the figures land.
- **RB-014 (A2 heterogeneous-$r$ model extension)** opens the A2/A8
  thread of model extensions (between-preparation single-$r$ adopted
  in §model already; the heterogeneous-$r$ extension is the honest
  generalisation for §extensions / §limitations).

I default the next increment to **RB-007 (C3 iso-VDA sim)** —
strictly higher leverage for the manuscript's voice, since it
directly attacks another categorical self-characterisation of the
inherited paper and produces figures the §5.2 redraft needs.

### Wiki cross-references

Sweep keywords for this section's §11.1-style check: {value-directed
attention, criterion fraction, equicorrelated Gaussian, Slepian
inequality, decorrelation, noise correlation, attention
allocation}.

Consulted (already in wiki, cited):

- `research_db/papers/cohen_maunsell2009_correlations.md` — bib entry
  `CohenMaunsell2009` cited in §2.3 (ρ ∈ [0, 0.4] envelope anchor).
- `research_db/papers/ruff_cohen2016_cross_area_correlations.md` —
  bib entry `RuffCohen2016` added this run; cited in §2.3
  (structured-covariance scoped limitation).
- `research_db/papers/srinath2021_attention_information_flow.md` —
  bib entry `Srinath2021` added this run; cited in §2.3 same paragraph.
- `research_db/papers/muller_findlay1987_sensitivity_criterion.md` —
  already wired via rb-007's results-C1 CF definition citation;
  not re-cited in §model (the §model CF definition forward-references
  results-C1).

Confirmed absent (math-methods gap; inherited from rb-008):

- **Slepian, D. (1962)**, *Bell Syst. Tech. J.* 41(2):463–501. Bib
  entry already in `refs.bib` (`Slepian1962`); no wiki stub.
- **Tong, Y.L. (1990)**, *The Multivariate Normal Distribution.* Not
  cited in §model directly (lives in the appendix derivation only).

No new wiki stubs added; `audit.py` not run (no wiki writes).

### Why the next run should care

This run finalises the "load-bearing narrative move" the mission
prompt names in §3.3 for the A1 dimension: the manuscript now reads
**distributional and conditional by default** in its single most
consequential section, the model section. Subsequent manuscript
increments (the §5.2 design-advice redraft in RB-011, the §results-C4
anti-cue inversion prediction in RB-012, the §limitations conservation-
family band in RB-015/RB-019) can now reference §model without
forward-stubbing; the §intro and §abstract increments (currently
queued informally; no dedicated tasks yet) can build on a §model
that already states the rebuild's voice. The reframe is now load-
bearing rather than promissory.

Manuscript size at end of rb-009: 16 pages, 1177200 bytes
(was 12 / 897327 bytes at end of rb-007). The §model section adds
~4 pages including 3 figures.

---

## rb-008 — 2026-05-25 — A1 ρ-channel derivation (derivation increment)

- **Run id:** `rb-008-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-003 (Promote the equicorrelated 1-D quadrature
  P_no-fa(ρ) + Slepian monotonicity into a clean
  `Rebuild/derivations/A1--rho-channel.md`, authored independently
  rather than copied from `Critique/derivations/`)
- **Output kind:** derivation
- **Claims touched:** A1 (CONTESTED — derivation formalises the rebuilt
  strength already empirically established in rb-002, and bounds it to
  Statements A and B per §4.3 of the derivation file)
- **Status:** done

### Headline thing built

`Rebuild/derivations/A1--rho-channel.md` — the rebuild's own
independent derivation of the decorrelation channel, ~14 KB / 7
sections, full LaTeX-grade equation handling. Independent of the
reviewer's `Critique/derivations/A1--correlated-fa-upper-bound.md` —
same underlying mathematics (there is only one correct derivation of
the equicorrelated 1-D reduction and the Slepian inequality), but
restructured in the rebuild's constructive voice: the reviewer states
**"the inherited §5.5 claim is false"** as the result; the rebuilt
derivation states **"the rebuilt model claims Statements A and B"**
as its result. Concretely the file delivers:

- **§1 Setup and the locus of A1** — notation, then the *booking*:
  the change-trial bracket of `E[R]` is linear in marginal hit rates
  and therefore never multiplies probabilities across locations, so
  the only cross-location product in the whole reward is the no-FA
  probability $P_{\text{no-fa}}$ (Eq. 1.4). Relaxing A1 is therefore
  *exactly* replacing (1.4) by the correlated joint orthant
  probability — nothing else changes. This isolates A1 from
  assumption A6 (global decision rule), which is a different
  relaxation acting via a pooled detection statistic.

- **§2 The correlated decision model and exact 1-D reduction.**
  Equicorrelated Σ; one-factor representation (Eq. 2.2,
  $X_i = \mu_i + \sqrt{\rho}\,Z + \sqrt{1-\rho}\,\varepsilon_i$);
  exact 1-D integral for the orthant probability (Eq. 2.3,
  boxed); ρ→0 recovery to the independent product (Eq. 2.4); the
  Gauss-Hermite-64 numerical realisation (Eq. 2.5) which is exactly
  what `Rebuild/model/core.py:p_no_fa_point` and `:p_no_fa_grid`
  implement. The recovery test sha256 `d3c62215…` is cited as the
  proof that the numerical primitive honours Eq. (2.4).

- **§3 Slepian monotonicity and per-policy reward bounds.**
  Proposition 3.1 (Slepian's inequality, equicorrelated form): the
  orthant probability is non-decreasing in ρ; cited to Slepian 1962
  *Bell Syst. Tech. J.* and Tong 1990 *The Multivariate Normal
  Distribution*. Corollary 3.2: each of the four policies P1–P4 has
  its supremum reward $R(\mathrm P_k; \rho)$ non-decreasing in ρ,
  derived as: (3.1) pointwise → (3.2) sup over criteria preserves the
  inequality → (3.3) sup over the feasible allocation set $\mathcal A_k$
  preserves the inequality. *This is the load-bearing intermediate
  result.*

- **§4 The two-channel sign-decomposition of $d\mathrm{VDA}/d\rho$.**
  Why Cor. 3.2 does NOT pin the VDA sign (both $R(\mathrm P_1)$ and
  $R(\mathrm P_2)$ rise, but their difference can move either way);
  then names the two opposing mechanisms:
  - **Channel (a) criterion devaluation:** ρ↑ flattens
    $P_{\text{no-fa}}(\rho)$ across $(c_c, c_u)$, shrinks
    $R(\mathrm P_3) - R(\mathrm P_4)$, drops CF (Statement A).
  - **Channel (b) concentration-cost relaxation:** at high v, $\mathrm P_1$
    concentrates attention, lowers $d'_u$, raises FAR$_u$;
    that compounds in the $\Phi(b_u)^{N-1}$ factor; ρ>0 relaxes
    the aggregate FA penalty per Slepian, so concentration is
    *cheaper* and VDA grows (Statement B at high r).
  Sign-flip in r where the channels balance. Statements A and B
  named explicitly with the empirical envelope they hold over — the
  rebuilt model's normative replacement for the inherited paper's
  §5.5 "upper bound on VDA" sentence.

- **§5 Numerical realisation at the headline cell.** Three tables
  (peak VDA + sign-flip locus across ρ; CF(ρ) at three r; cross-
  reference to the cell-wise CF ordering from the rb-003 4,410-cell
  sweep); every numeric value sourced from
  `Rebuild/sims/A1--rho-channel/` sha256 `b692c064…`. Statement A
  realised: CF monotone-down in ρ in variant A. Statement B realised:
  pointwise upper-bound on VDA fails for every ρ>0; max excess grows
  $+4.84 \times 10^{-3}$ → $+1.01 \times 10^{-2}$ across ρ=0.1→0.4;
  sign-flip locus drifts $r \approx 0.38 \to 0.56$. Variant-B flat-
  CF caveat carried forward from rb-002 and generalised by the rb-003
  sweep (84% variant-A cells decrease vs 64% variant-B).

- **§6 Scope and limitations.** Equicorrelation specificity (structured
  Σ breaks the 1-D reduction; cites
  [[ruff_cohen2016_cross_area_correlations]] and
  [[srinath2021_attention_information_flow]]); magnitude envelope
  $\rho \in [0, 0.4]$ matched to Cohen & Maunsell 2009 $r_\mathrm{SC}$;
  recovery contract globality (any future model extension must pass
  its own ρ=0 limit); explicit non-promises (no closed-form
  $r^\dagger(v;\rho)$ — queued as RB-026; no tighter sign-flip
  bracket — queued as RB-023; no cell-wise sign-flip map — queued
  as RB-025).

- **§7 References.** Slepian 1962, Tong 1990, Cohen & Maunsell 2009
  ([[cohen_maunsell2009_correlations]]), Ruff & Cohen 2016
  ([[ruff_cohen2016_cross_area_correlations]]), Srinath et al. 2021
  ([[srinath2021_attention_information_flow]]); plus the
  `Rebuild/model/core.py` identifiers it implements
  (`p_no_fa_point`, `p_no_fa_grid`, `d_prime_asym`, `beta_gamma`)
  and the test and simulation digests it depends on.

- **Verification performed** block lists the five numerical checks
  (recovery, Slepian, per-policy monotonicity, sign-flip locus,
  quadrature error) that already ran in earlier increments and that
  the derivation's claims rest on. **Extensions to consider** block
  forwards RB-023 / RB-025 / RB-026 plus a scoped "structured
  covariance" line.

### "Test" for a derivation increment

A derivation has no compile step of its own; the verification is that
every formula it states is the one already exercised by the model
code and the simulation. Per-equation traceability:

| Eq.   | Implemented by                                                | Verified by                                |
|-------|---------------------------------------------------------------|--------------------------------------------|
| 1.4   | `Rebuild/model/core.py:p_no_fa_point` at ρ=0 branch           | `test_recovery.py` sha256 `d3c62215…`      |
| 2.3   | `Rebuild/model/core.py:p_no_fa_point` (Gauss–Hermite-64)      | quadrature self-test in `model/tests/`     |
| 2.4   | `Rebuild/model/core.py:p_no_fa_point` ρ→0 reduction           | `test_recovery.py` 7/7 PASS                |
| 2.5   | `Rebuild/model/core.py:p_no_fa_point` (substituted form)      | unit weight check $\sum w_k = \sqrt{\pi}$  |
| 3.1   | Numerical sweep over $\rho \in \{0,…,0.8\}$ in rb-002         | rb-002 README, Slepian monotonicity block  |
| 3.3   | per-policy supremum sweep in rb-002 + rb-004                  | both sims pass Cor. 3.2 inspection         |
| §4 (a)| CF(ρ) table in rb-002 + cell-wise rb-003 ordering             | rb-002 sha256 `b692c064…`, rb-003 sha256 `91fc4692…` |
| §4 (b)| VDA peak / max-excess table in rb-002                         | rb-002 sha256 `b692c064…`                  |

No new code; no new sims. The increment is pure formalisation of
material the model and sims already produce.

### Exact manuscript claim now licensed

The §appendix-derivation-A1 of `Rebuild/manuscript/main.pdf` may now
assert:

> *"The rebuilt model promotes the per-location-independence assumption
> to a tunable equicorrelation parameter $\rho$. The reward
> decomposes such that A1 enters $\mathbb E[R]$ in exactly one place —
> the no-false-alarm product (Eq. 1.4) — and replacing that product
> by the exact equicorrelated joint orthant probability (Eq. 2.3, a
> one-dimensional integral by the one-factor representation 2.2) is
> the faithful and complete relaxation of A1 within the model's
> reward structure. The independent corner $\rho = 0$ is recovered to
> floating-point identity (Eq. 2.4). Slepian's monotonicity
> (Proposition 3.1) makes the orthant probability — and therefore
> each policy's supremum reward (Corollary 3.2) — non-decreasing in
> $\rho$. The value-directed-attention difference $\mathrm{VDA}(\rho)
> = R(\mathrm P_1;\rho) - R(\mathrm P_2;\rho)$ is **not** sign-
> determined by Corollary 3.2; it splits into two competing channels
> (criterion devaluation vs concentration-cost relaxation) whose
> relative weight depends on the cost--benefit ratio $r$. At the
> headline cell, this yields two falsifiable statements: (A) the
> criterion fraction is non-increasing in $\rho$ in variant A; (B)
> the sign of $d\mathrm{VDA}/d\rho$ flips with $r$, in the band
> $r \in [0.38, 0.56]$ across $\rho \in [0.1, 0.4]$. The inherited
> §5.5 'upper bound on VDA' self-characterisation is therefore
> retracted; what independence upper-bounds is the criterion
> fraction in variant A, not VDA."*

This is the strongest statement the §3.3 voice of the mission
licenses given the live A1 verdict (CONTESTED) — the same ceiling
the manuscript prose has been bound to since rb-002 — but now
underwritten by a derivation rather than only by a simulation.

### Simulation evidence

The derivation does not generate new numbers; it formalises the
numbers already published by rb-002 (sha256 `b692c064…`) and
rb-003 (sha256 `91fc4692…`). §5.1–§5.3 of the derivation file
quote those numbers verbatim and link to the source files. No
re-run was required; both sims' output digests still validate.

### What the manuscript can now say

RB-004 (manuscript §model + §appendix-derivation-A1) is now
**unblocked**: its prereqs `[RB-002, RB-003]` are both done. The
next manuscript increment can:

- Draft the §model section in `Rebuild/manuscript/sections/model.tex`,
  stating the "three levers, not two" reframe and citing the
  derivation file for the equicorrelated reduction. The §model
  section is the largest single increment remaining — it carries
  Eqs. 1.4, 2.3, 2.4 and frames the whole rebuild — so RB-004 is
  the natural next pick.
- Bind the §appendix-derivation-A1 subsection of the manuscript to
  this file by `\input{}`-ing its LaTeX content (or summarising it
  with a pointer; format choice deferred to RB-004).

### Next increment

**RB-004 (manuscript §model)** is the natural next pick: it is the
single largest manuscript section that absorbs the rebuild's narrative
spine, and both its prereqs (RB-002 sim, RB-003 derivation) are now
done. Estimated wall-clock ~10–15 min for the prose plus one
`pdflatex` × 3 build pass.

Alternative picks of comparable priority:

- **RB-007** (C3 iso-VDA contour sim) — opens the C3 results
  subsection. Prereq RB-001 already done.
- **RB-008** (C4 inversion sim with the $V < 1/N$ anti-cue
  prediction) — opens C4 results subsection. Prereq RB-001 done.

The natural model→sim→derivation→manuscript order (§4.1) and the
fact that RB-004 is the unique manuscript section that unifies A1,
C1, and C2 into the model spine argue for RB-004 next.

### Wiki cross-references

Mechanism-keyword sweep on the derivation's content
(equicorrelated Gaussian, orthant probability, Slepian, attention
noise correlations, value-directed attention, multivariate
sensitivity):

- **[[cohen_maunsell2009_correlations]]** — present in
  `research_db/papers/`. Cited as the empirical anchor for
  $\rho \approx 0.2$ in V4 ($r_\mathrm{SC}$ measurement); motivates
  the rebuilt model's $\rho \in [0, 0.4]$ envelope.
- **[[ruff_cohen2016_cross_area_correlations]]** — present in
  `research_db/papers/`. Cited as the structured-covariance limitation
  (within-area-down / between-area-up sign-dependent correlations) that
  caps the equicorrelated specialisation in §6.
- **[[srinath2021_attention_information_flow]]** — present in
  `research_db/papers/`. Cited as the supra-pairwise shared-variance
  result that prevents a "single ρ" patch from covering the full
  cortical-covariance space; supports the §6 scope language.
- **Slepian 1962** *Bell Syst. Tech. J.* 41(2):463–501 — *not in
  `research_db/`*. Math-methods gap. Same gap flagged by reviewer
  C5 and A8 derivations. Cited by full bibliographic reference.
- **Tong 1990** *The Multivariate Normal Distribution* (Springer,
  §5.1) — *not in `research_db/`*. Same math-methods gap. Cited
  by full reference.

No new wiki stubs added in this run (audit.py not invoked). The
Slepian / Tong gap is a candidate for a later math-methods stub
batch.

### Why the next run should care

The §model section of the rebuilt manuscript (RB-004) is the unique
artifact that bonds A1 (this run), C1 (rb-007), and C2 (rb-006) into
a single load-bearing model statement — the "three levers, not two"
reframe that the §3.3 unifying-narrative paragraph of the mission
prompt singles out as the most important narrative move. With RB-003
done, RB-004 is the next single increment that yields the largest
gain in coherence for the rebuilt paper. Picking RB-007 or RB-008
instead is admissible but defers the model-spine consolidation by
one further run.

---

## rb-007 — 2026-05-25 — §results-C1 manuscript prose (manuscript increment)

- **Run id:** `rb-007-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-009 (Draft `Rebuild/manuscript/sections/results.tex`
  §results-c1 — C1 distributional CF + A1 ρ sensitivity)
- **Output kind:** manuscript
- **Claims touched:** C1 (CONTESTED — restated at distributional /
  central-tendency strength); A1 (CONTESTED — Δ-distribution of CF(ρ)
  across the sweep reported alongside, per the three-levers convention
  established in rb-006)
- **Status:** done

### Headline thing built

The rebuild's second body-of-results manuscript section, replacing the
placeholder bracket left by rb-005 (immediately after the §results-C2
prose landed by rb-006):

- **§results-C1 prose (the increment proper).** A fully filled-in
  subsection consisting of: a claim-restatement paragraph pinning
  rebuilt strength to the live verdict `CONTESTED` and naming the
  Müller–Findlay 1987 sensitivity-vs-criterion SDT decomposition
  (`\cite{MullerFindlay1987}`) as the conceptual context for the
  criterion-fraction quantity; a numbered definition of `CF`
  (`eq:cf-def`); a per-variant CF-distribution table
  (`tab:cf-distribution`, range / quantiles / median / mean+s.d. at
  ρ=0) sourced from `summaries.variant_<X>/rho_0.0` in the rb-003
  `results.json`; a 3×2 (r-regime × V-regime) quadrant breakdown
  (`tab:cf-quadrants`, 12 rows, sourced from
  `quadrant_breakdown.rho_0.0.*`) exposing the benefit-dominant
  low-validity corner where CF drops below the inherited floor; an
  A1 ρ-sensitivity table (`tab:cf-rho-sensitivity`, marginals at
  ρ∈{0,0.2} per variant); a cell-wise Δ-distribution table
  (`tab:cf-delta-distribution`, 84% of variant-A cells decrease /
  variant-B 64%/24%/13% dec/inc/flat — the rb-002 headline-cell
  variant-B flat-in-ρ pattern generalised across the sweep); all
  three rb-003 figures (`cf_histogram.png`, `cf_heatmap.png`,
  `cf_curves.png`) copied to `Rebuild/manuscript/figures/` and
  `\includegraphics`-ed in `fig:cf-histogram`, `fig:cf-heatmap`,
  `fig:cf-curves`; an explicit scope-and-not-yet-claimed paragraph
  flagging the conservation-family band (RB-019), the finer-ρ grid
  (RB-023), the closed-form CF<0.5 boundary (RB-024), and the
  cell-wise VDA Δ-distribution (RB-025); a reproducibility paragraph
  citing the rb-003 output digest `91fc4692…`, the full grid spec,
  and the cell-wise recovery against the reviewer's CR-002.

- **`refs.bib`.** One entry added: `MullerFindlay1987`
  (10.3758/bf03203097). The rb-005 seed of two entries (Slepian1962,
  CohenMaunsell2009) grows to three.

### Build verification (the "test" for a manuscript increment)

3-pass `pdflatex` + `bibtex` build (new citation required `bibtex`
this time, unlike rb-006):

| step | command                                          | exit | bytes produced |
|-----:|--------------------------------------------------|-----:|---------------:|
| 1    | `pdflatex -interaction=nonstopmode main.tex`     | 0    | main.pdf 894014 (citation undefined — expected pass 1) |
| 2    | `bibtex main`                                    | 0    | main.bbl rewritten |
| 3    | `pdflatex -interaction=nonstopmode main.tex`     | 0    | main.pdf 897584 (refs partially resolve; rerun warning) |
| 4    | `pdflatex -interaction=nonstopmode main.tex`     | 0    | main.pdf **897327** |

Final PDF: **12 pages, 897327 bytes** (up from rb-006's 7 pages /
542 463 bytes — the +5 pages = the §results-C1 prose with 4 tables,
3 figures, equation `eq:cf-def`, and the longer bibliography that
now lists `MullerFindlay1987`). No undefined references after pass 4.
Remaining warnings are cosmetic: ~11 `hyperref` "Token not allowed in
a PDF string (Unicode)" warnings from math glyphs serialised into PDF
bookmarks, plus a handful of overfull/underfull `\hbox` lines from
long `\texttt{...}` literals inside captions; none affect compilation
or visible output.

One mid-build math-mode error required correction before the prose
typeset cleanly: the texttt literal
`\texttt{summaries.variant\_<X>/rho\_<\corr>}` invoked the math-only
`\corr` macro (`\rho`) inside a text-mode `\texttt` argument; replaced
with the literal token `rho`. A second error was a stray Unicode `Δ`
in the scope paragraph (line 365) where I should have used `$\Delta$`;
fixed.

### Exact manuscript claim now licensed

The §results-C1 subsection of `Rebuild/manuscript/main.pdf` now
asserts:

> *"Across the paper's primary 4{,}410-cell $(\Rsens, \valid, \val)$
> sweep at $(\Nloc, \dprimemax, f_0, h) = (4, 2, 0.5, \sqrt{})$, the
> criterion fraction $\CF$ is distributed over $[0.5587, 1.0000]$ in
> variant~A and $[0.3040, 1.0000]$ in variant~B with median $0.7552$
> (A) / $0.7682$ (B). The inherited paper's stated range
> $\CF \in [0.60, 0.96]$ is retracted on both ends; the substantive
> 'criterion typically dominates' reading is sustained at the median.
> The criterion lever cedes to attention re-allocation in the
> benefit-dominant low-validity corner: variant~B median $0.509$ with
> $78\%$ of cells below $0.60$ and strict minimum $0.304$ in that
> quadrant. Promoting the A1 independence assumption to $\corr = 0.2$
> triples variant-A $\mathrm{frac}\!<\!0.6$ ($0.07 \to 0.22$), drops
> the variant-A strict minimum below $0.50$, and orders $\CF(0.2) \le
> \CF(0)$ in $84\%$ of variant-A cells. The same ordering is mixed in
> variant~B ($64\%$ dec.\ / $24\%$ inc.\ / $13\%$ flat): independence
> upper-bounds $\CF$ on a typical variant-A cell but not uniformly,
> and does not upper-bound $\CF$ at all in variant~B."*

This is the strongest statement the §3.3 distributional-and-conditional
voice licenses. The categorical "$\CF \in [0.60, 0.96]$" floor of the
inherited paper is gone; what replaces it is a distribution with
explicit corner regions, an explicit variant-dependence, and an
explicit ρ-sensitivity.

### Simulation evidence

All numbers and figures trace to the rb-003 simulation
`Rebuild/sims/C1--cf-distribution/` and its `results.json` digest
`91fc4692dbc106eca9c90770c79e22f7f4757d76421ed55e7e8e91f80e44706c`.
Cell-wise recovery against the reviewer's CR-002 substrate at
`max|ΔCF| = 1.47e-6`, `max|ΔR(P1..P4)| ≤ 5.65e-7`. No new simulation
was run this increment; the existing artifact has the recovery test
embedded in `results.json.recovery_test`.

### Wiki cross-references

Mechanism-keyword sweep across `research_db/papers/` per the §11
protocol inherited from the reviewer:

- **`muller_findlay1987_sensitivity_criterion`** — the foundational
  empirical SDT decomposition of spatial cuing into sensitivity vs.
  criterion components; the conceptual ancestor of CF as a one-number
  summary of the criterion lever. **Cited** (`\cite{MullerFindlay1987}`)
  in the §results-C1 claim-restatement paragraph; bib entry added to
  `refs.bib`.
- `hawkins1990_attention_detectability`, `luo_maunsell2018_criterion_sensitivity`,
  `sridharan2017_sc_sensitivity_bias` — the immediate descendants in
  the same lineage; consulted (`research_db/papers/muller_findlay1987_sensitivity_criterion.md`
  cross-references them) but not cited in this increment. Candidates
  for the §intro literature anchor when that section is filled.

No new `research_db/papers/` stubs were added; `audit.py` not run.

### Next increment

The natural next-step is **RB-003 (A1 derivation in clean LaTeX)** —
the prerequisite for RB-004 (the §model section), which is the
foundational section the §results-C1 and §results-C2 prose both
forward-reference (`\ref{sec:model}` already appears in both
subsections, currently pointing at a stub). RB-003 promotes the
equicorrelated 1-D quadrature `P_no-fa(ρ)` and the Slepian-monotonicity
argument to `Rebuild/derivations/A1--rho-channel.md` in the rebuild's
own voice (not a copy of `Critique/derivations/A1--correlated-fa-upper-bound.md`).
With RB-003 in hand, RB-004 unblocks and the §model section can be
filled — at which point the §results subsections gain a non-stub
forward-reference target.

Alternative is **RB-008 (C4 inversion-onset sim)**, which would open
the entirely new C4 claim pipeline and parallel the rb-004 / rb-005
sim cadence; it would unblock RB-012 (C4 §results subsection).

### Why the next run should care

Three §results subsections are now drafted (C2 by rb-006, C1 by rb-007;
C3 and C4 still placeholders). The §model section that both C2 and C1
forward-reference is still a stub; the most consequential unblocking
move at this point is the A1 derivation (RB-003) → §model fill
(RB-004) sequence, because every other subsection's claim-restatement
depends on the three-levers reframe `sec:model` is supposed to
establish. The C3 and C4 sims (RB-007, RB-008) can run in parallel as
independent claim pipelines that don't depend on `sec:model` being
prose-complete.

## rb-006 — 2026-05-25 — §results-C2 manuscript prose (manuscript increment)

- **Run id:** `rb-006-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-010 (Draft `Rebuild/manuscript/sections/results.tex`
  §results-c2 — C2 + closed-form $r^\dagger(v)$ + A1 sensitivity)
- **Output kind:** manuscript
- **Claims touched:** C2 (CONFIRMED-UNDER-ATTACK — confident-spine
  headline); A1 (CONTESTED — $\val$-dependent generalisation of the
  rb-002 sign-flip reported as a sensitivity)
- **Status:** done

### Headline thing built

The rebuild's first body-of-results manuscript section, replacing the
stub left by rb-005:

- **Section-level introduction.** `\section{Results}` rewritten from
  a one-paragraph stub to a substantive paragraph framing the four
  subsections (C1 distribution, C2 confident spine, C3 graded
  boundary, C4 conditional theorem) and explaining the "A1 reported
  alongside, not segregated" convention that operationalises the
  three-levers reframe.
- **§results-C2 prose (the increment proper).** A fully filled-in
  subsection consisting of: a claim-restatement paragraph that pins
  the rebuilt strength to the live verdict label
  `CONFIRMED-UNDER-ATTACK`; the closed-form display equation
  `r†(v) = K_u(v)/[(N-1) K_c(v)]` (numbered `eq:r-dagger`) with its
  $K_c$ and $K_u$ companion displays (`eq:K-c`, `eq:K-u`) derived from
  $\partial_\alpha \Rpone|_{1/\Nloc} = 0$; a numerical $\val$-family
  table (`tab:r-dagger-family`, 6 rows, $\val \in \{1,2,3,5,8,10\}$
  with $\rdagger$, $c_c^\star$, $c_u^\star$, $K_c$, $K_u$ each
  reported); a peak-vs-threshold consistency table
  (`tab:peak-vs-threshold`, 5 rows, $\val \in \{2,3,5,8,10\}$,
  empirical peak $r^\star > \rdagger(\val)$ confirmed for every
  $\val$); an A1 sensitivity table (`tab:rho-sensitivity`, $\val$-
  family $\VDA^\star$ at $\corr \in \{0, 0.2\}$ showing the
  $\val$-dependent sign-flip — suppression at $\val \le 8$,
  amplification at $\val = 10$); both rb-004 figures
  (`vda_curves_vfamily.png`, `r_dagger_vs_v.png`) copied to
  `Rebuild/manuscript/figures/` and `\includegraphics`-ed in
  `fig:vda-curves-vfamily` and `fig:r-dagger-vs-v`; explicit
  scope-and-not-yet-claimed and reproducibility paragraphs.

### Build verification (the "test" for a manuscript increment)

3-pass `pdflatex` build (no `bibtex` — no new citations in this
increment; the existing seed `refs.bib` is untouched):

| step | command                                          | exit | bytes produced |
|-----:|--------------------------------------------------|-----:|---------------:|
| 1    | `pdflatex -interaction=nonstopmode main.tex`     | 0    | main.pdf 541477 (refs undefined — expected pass 1) |
| 2    | `pdflatex -interaction=nonstopmode main.tex`     | 0    | refs resolve |
| 3    | `pdflatex -interaction=nonstopmode main.tex`     | 0    | main.pdf **542463** |

Final PDF: **7 pages, 542463 bytes** (up from rb-005's 3 pages /
316934 bytes — the +4 pages = §results header rewrite + §results-C2
prose + 3 tables + 2 figures). No undefined references after pass 2.
Remaining warnings are cosmetic: ~6 "Overfull/Underfull \\hbox" lines
(long `\\texttt{filename.png}` literals inside captions and the
in-paragraph hyphenation of math-mode displays inside tables) and
~9 `hyperref` "Token not allowed in a PDF string (Unicode)" warnings
from math glyphs in section/figure/table captions that get
serialised into PDF bookmarks — neither category affects compilation,
visible output, or cross-references.

### Exact manuscript claim now licensed

The §results-C2 subsection of `Rebuild/manuscript/main.pdf` now
asserts:

> *"At the C2 headline cell $(\Nloc, \dprimemax, f_0, h, \valid) =
> (4, 2, 0.5, \sqrt{}, 0.5)$ under variant~A, the value-directed
> attention benefit $\VDA(\Rsens)$ is non-monotonic in the
> benefit/cost ratio $\Rsens$. The non-monotonicity is a theorem of
> the model definitions: the closed form
> $\rdagger(\val) = K_u(\val) / [(\Nloc - 1)\,K_c(\val)]$ predicts
> the $\Rsens$ at which P1 leaves the uniform allocation, with
> $\rdagger(\val)$ monotone-decreasing from $\rdagger(2) \approx 0.17$
> to $\rdagger(10) \approx 0.02$. The empirical peak
> $r^\star = \arg\max_{\Rsens} \VDA(\Rsens)$ lies above $\rdagger(\val)$
> for every $\val \in \{2, 3, 5, 8, 10\}$ and clusters near
> $\rdagger(\val{=}1) \approx 0.343$. Peak $\VDA$ grows monotonically
> from $0.012$ at $\val=2$ to $0.183$ at $\val=10$. Promoting the A1
> independence assumption to $\corr = 0.2$ suppresses the peak at
> low $\val$ ($\Delta \VDA^\star = -0.002$ at $\val=2$,
> $-0.003$ at $\val=5$) and amplifies it at $\val = 10$ ($+0.001$):
> the rb-002 $\Rsens$-axis sign-flip of $\partial \VDA / \partial \corr$
> generalises to a $\val$-axis sign-flip of
> $\partial \VDA^\star / \partial \corr$. This is reported as a
> sensitivity; the closed-form $\rdagger(\val; \corr > 0)$ that would
> predict the upward drift of $r^\star$ analytically is queued as a
> derivation increment (RB-026)."*

The subsection does **not** license:
- the variant-B replication (RB-027, queued; the section explicitly
  scopes its claims to variant~A and forwards variant~B to
  `Section~\ref{sec:limitations}`);
- a closed-form $\rdagger(\val; \corr > 0)$ — present text reports
  the $\corr = 0.2$ column as observation, not theorem (RB-026
  queued);
- a conservation-family band on the peak $\VDA^\star$ values — the
  Table~\ref{tab:peak-vs-threshold} entries are conditional on
  variant~A; the band is scoped to the future A3 increment (RB-019)
  and flagged in the "Scope and what is not yet claimed" paragraph.

The claim is now stated at — and not beyond — the CLAIM_LEDGER
ceiling for C2.

### What I built (file by file)

- `Rebuild/manuscript/sections/results.tex` — rewrote the
  `\section{Results}` introductory paragraph and the `\subsection`
  C2 body. The C1, C3, C4 subsections remain stubs (their backlog
  items RB-009, RB-011, RB-012 are still open). Added three
  `\begin{table}` environments (`tab:r-dagger-family`,
  `tab:peak-vs-threshold`, `tab:rho-sensitivity`), two
  `\begin{figure}` environments (`fig:r-dagger-vs-v`,
  `fig:vda-curves-vfamily`), and three numbered display equations
  (`eq:r-dagger`, `eq:K-c`, `eq:K-u`).
- `Rebuild/manuscript/figures/r_dagger_vs_v.png` — copied verbatim
  from `Rebuild/sims/C2--vda-vs-r-vfamily/output/figures/`
  (50 950 bytes).
- `Rebuild/manuscript/figures/vda_curves_vfamily.png` — copied
  verbatim from the same sim output dir (160 767 bytes).
- `Rebuild/manuscript/main.pdf` — regenerated (542 463 bytes,
  7 pages) by the verification step.
- `Rebuild/manuscript/main.aux`, `main.log`, `main.out` —
  regenerated.
- `Rebuild/conversations/2026-05-25-rebuilder-rb006-results-c2.md`
  (the run's conversation page).
- Updates: `CLAIM_LEDGER.md` (C2 row's "backing" column updated to
  cite the drafted section + PDF size; last-reconciled line bumped
  to rb-006), `REBUILD_BACKLOG.md` (RB-010 in_progress -> done with
  a paragraph summary of what landed), `rebuilder_state.json`
  atomically rewritten via `tmp + rename` (runs_completed 5 -> 6;
  done_task_ids adds RB-010; manuscript_sections_drafted adds
  "RB-010 (§results-C2)"; new `rb_006_manuscript_pdf_bytes: 542463`
  field).

### Ledger reconciliation (vs. mission §3, prompt v0.2)

`grep current_label Critique/verdicts/*.md` returns the same ten
labels as rb-005: C1 CONTESTED, C2 CONFIRMED-UNDER-ATTACK, C3
CONTESTED, C4 CONFIRMED-CONDITIONAL, C5 CONFIRMED-UNDER-ATTACK;
A1 CONTESTED, A2 CONFIRMED-CONDITIONAL, A3 CONTESTED, A6
WEAKLY-SUPPORTED (standing drift, direction unchanged), A8
CONFIRMED-CONDITIONAL. No new drift; the existing A6 drift remains
flagged `proposed_mission_change` since rb-001 and does not affect
this section (A6 is not referenced by §results-C2).

### Wiki sweep (mission §11, performed before declaring done)

Keywords swept: `non-monotonic VDA`, `value-directed attention`,
`escape threshold`, `equicorrelated Gaussian`, `criterion shift`,
`attention reallocation`, `cued change detection`. The wiki
(`research_db/papers/`, `concepts/`, `threads/`) contains many
attention-and-SDT-related papers (Maunsell 2015, Posner 1980,
Muller & Findlay 1987, Hawkins 1990, Bays & Husain 2008, Bundesen
2005, …) but no paper specifically about the cued-change-detection
VDA paradigm at the model's core, and no paper makes the
specifically-rebuild claim that VDA non-monotonicity is a theorem
of the model's first-order conditions. The §results-C2 subsection
is therefore self-contained: its substantive cross-references are
all internal (equations, tables, figures, sims, the future
`sec:appendix-deriv-c2` for the derivation, the future
`sec:limitations` for the conservation-family caveat). No new
literature citation is required; no new `papers/*.md` stub was
written; `python3 research_db/tools/audit.py` was not invoked
(no `papers/` change).

### Next increment

The cleanest single-section content target still queued is
**RB-009** (§results-C1 prose) — same shape as the rb-006
increment, with rb-003's three figures and Δ-distribution numerics
ready to cite. Alternatively, **RB-013** (§appendix-C5) is a
short consistency-paragraph increment, and **RB-003** (the A1
ρ-channel appendix derivation) is the natural derivation-track
choice — unblocking RB-004 (model section) is the spine of the
three-levers reframe. A reasonable default next pick: **RB-009**
(maintains the §results-prose track and locks in the second of
the two confident-spine results that already have full simulation
backing).

### Why the next run should care

rb-006 establishes the rebuild's *voice in the wild*: a full
section of LaTeX prose has now been written at the
CLAIM_LEDGER-licensed strength, with every numerical claim
sourced to a sha256-stamped sim, every figure copied from
`Rebuild/sims/*/output/`, and every "regardless" / "always" /
"floor" categorical statement avoided. The §results-C2 subsection
is a template the remaining results sections (RB-009 C1, RB-011
C3, RB-012 C4) and the appendix sections (RB-013 C5, RB-003 A1,
RB-026 C2) can copy structurally: claim-restatement paragraph
$\to$ closed-form display (when available) $\to$ numerical
$\val$/$\corr$/etc.\ table $\to$ figure $\to$ A1 sensitivity
$\to$ scope-and-not-yet-claimed $\to$ reproducibility.

---

---

## rb-005 — 2026-05-25 — Manuscript skeleton in LaTeX (manuscript increment)

- **Run id:** `rb-005-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-022 (Draft `Rebuild/manuscript/main.tex` skeleton + section stubs + `BUILD.md` toolchain)
- **Output kind:** manuscript
- **Claims touched:** cross-cutting (skeleton has homes for every claim row in `CLAIM_LEDGER.md`; no claim's *strength* changes this run)
- **Status:** done

### Headline thing built

`Rebuild/manuscript/` — the first manuscript artifact to land under
`Rebuild/`. A compileable LaTeX skeleton with seven section files,
all hard-anchored to the `CLAIM_LEDGER.md` disposition table and
the named RB-NNN increments that will fill each one. Files
delivered:

- `main.tex` — thin document with `\documentclass[11pt]{article}`,
  the project's standard packages (amsmath/amssymb/amsthm,
  mathtools, graphicx, booktabs, xcolor, hyperref), theorem
  environments (theorem, proposition, lemma, corollary, definition,
  assumption, remark), and macros for the project notation
  (`\dprime`, `\VDA`, `\CF`, `\corr`, `\rdagger`, `\rstarinv`,
  `\PnoFA`, `\Rsens`, etc.). Body is seven `\input{}` calls plus
  bibliography.
- `sections/abstract.tex`, `intro.tex`, `model.tex`,
  `results.tex` (with subsections `c1`/`c2`/`c3`/`c4`),
  `limitations.tex`, `methods.tex`, `appendix.tex` (with subsections
  `deriv-a1`, `deriv-c2`, `c5`) — each stub is a block comment
  naming the RB-NNN increment that will fill it, the
  `CLAIM_LEDGER.md` row that bounds its allowed strength, and a
  short anticipated-contents paragraph in proper LaTeX (citing
  cross-references and notation already wired in `main.tex`).
- `refs.bib` — two seed entries cited by the appendix stubs:
  Slepian 1962 (the monotonicity inequality for the A1 ρ-channel
  derivation) and Cohen & Maunsell 2009 (the empirical anchor for
  attention-modulated cross-location noise correlations).
- `BUILD.md` — toolchain documentation. Records that `latexmk` and
  `siunitx.sty` are absent from the sandbox's TeX Live 2026basic
  install and shows the 4-command `pdflatex / bibtex / pdflatex × 2`
  manual build path. Per-section authoring workflow documented.

### Build verification (the "test" for a manuscript increment)

Manual 4-pass build under `Rebuild/manuscript/`:

| step | command                                          | exit | bytes produced |
|-----:|--------------------------------------------------|-----:|---------------:|
| 1    | `pdflatex -interaction=nonstopmode main.tex`     | 0    | main.pdf 312634 |
| 2    | `bibtex main`                                    | 0    | (no citations yet — expected for stub) |
| 3    | `pdflatex -interaction=nonstopmode main.tex`     | 0    | main.pdf 317104 |
| 4    | `pdflatex -interaction=nonstopmode main.tex`     | 0    | main.pdf 316934 |

Final PDF: **3 pages, 316934 bytes**, PDF version 1.7. No undefined
references in `main.log`; the only warnings are two
"Overfull \\hbox ~78pt" lines and one "Underfull \\hbox" — all
cosmetic, caused by long `\\texttt{filename.png}` literals inside
stub brackets that will disappear when prose lands. Toolchain
caveats (siunitx absent, latexmk absent, cleveref absent) are
encoded directly in `BUILD.md` so subsequent runs do not re-discover
them.

### Exact manuscript claim now licensed

The skeleton is a *home for* claims, not a statement of them: rb-005
does **not** license any new claim. The licensed-strength ceiling for
every section/subsection is the corresponding row of
`CLAIM_LEDGER.md`, which the section files cite explicitly in their
header comments. The rebuild's voice (mission §3.3 — distributional
and conditional by default) is encoded in the abstract / intro stubs
so that subsequent manuscript increments inherit the framing
automatically.

### What I built (file by file)

- `Rebuild/manuscript/main.tex` — preamble, theorem envs, project
  notation, body skeleton, bibliography call.
- `Rebuild/manuscript/sections/abstract.tex` — abstract environment
  stub.
- `Rebuild/manuscript/sections/intro.tex` — Section~\ref{sec:intro}
  stub.
- `Rebuild/manuscript/sections/model.tex` — `sec:model` stub with
  the three-levers reframe anticipated.
- `Rebuild/manuscript/sections/results.tex` — `sec:results` with
  four `subsection{}` stubs (`sec:results-c1`, `sec:results-c2`,
  `sec:results-c3`, `sec:results-c4`).
- `Rebuild/manuscript/sections/limitations.tex` — `sec:limitations`
  stub for the conservation-family band, heterogeneity, decision-noise,
  and unattacked-assumption scoping.
- `Rebuild/manuscript/sections/methods.tex` — `sec:methods` stub
  documenting the validated reference implementation under
  `Rebuild/model/` and the reproducibility protocol every sim
  follows.
- `Rebuild/manuscript/sections/appendix.tex` — `sec:appendix` with
  three `subsection{}` stubs (`sec:appendix-deriv-a1`,
  `sec:appendix-deriv-c2`, `sec:appendix-c5`).
- `Rebuild/manuscript/refs.bib` — seed entries
  (Slepian 1962, Cohen & Maunsell 2009).
- `Rebuild/manuscript/BUILD.md` — toolchain docs + per-section
  workflow.
- `Rebuild/manuscript/main.pdf` — the 3-page compiled skeleton
  (artifact of the verification step).
- `Rebuild/conversations/2026-05-25-rebuilder-rb005-manuscript-skeleton.md`.
- Updates: `CLAIM_LEDGER.md` ("last reconciled" → rb-005 with no
  drift), `REBUILD_BACKLOG.md` (RB-022 in_progress → done with the
  unblock list), `rebuilder_state.json` atomically rewritten
  (`runs_completed: 4 → 5`; `done_task_ids` adds RB-022;
  `manuscript_sections_drafted` adds "RB-022 (skeleton)";
  `+rb_005_manuscript_pdf_bytes` field).

### Ledger reconciliation (vs. mission §3, prompt v0.2)

No new drift. `grep current_label Critique/verdicts/*.md` returns the
same ten labels as rb-004: C1 CONTESTED, C2 CONFIRMED-UNDER-ATTACK,
C3 CONTESTED, C4 CONFIRMED-CONDITIONAL, C5 CONFIRMED-UNDER-ATTACK;
A1 CONTESTED, A2 CONFIRMED-CONDITIONAL, A3 CONTESTED, A6
WEAKLY-SUPPORTED (standing mild drift, direction unchanged), A8
CONFIRMED-CONDITIONAL. Continues to match §3 except A6 (already
flagged `proposed_mission_change` since rb-001). Wiki sweep
deferred: per mission §11, the sweep is required *before declaring
any manuscript section done*; rb-005 declared **no section done**,
only created stubs, so no sweep was performed this run — each
per-section content increment will do its own sweep.

### Why the next run should care

rb-005 unblocks the entire manuscript-prose track. Five
section-content tasks are now both prerequisites-satisfied
and skeleton-ready:

- **RB-010** (§results-C2, `sec:results-c2`) — the cleanest target.
  rb-004's analytic content (the `r†(v)` v-family table, the
  peak-vs-threshold consistency table, the v-dependent A1 sign-flip,
  the closed-form display equation) gives this section the most
  material to land in one increment, and the corresponding figures
  (`vda_curves_vfamily.png`, `r_dagger_vs_v.png`) already exist
  under `Rebuild/sims/C2--vda-vs-r-vfamily/output/figures/`.
- **RB-009** (§results-C1, `sec:results-c1`) — also unblocked.
  rb-003's three figures (`cf_histogram.png`, `cf_heatmap.png`,
  `cf_curves.png`) and the full Δ-distribution numerics are
  ready to cite.
- **RB-013** (§appendix-C5) — light-touch appendix consistency
  paragraph using the rb-001 recovery-test sha256 as evidence.
- **RB-004** (§model, the three-levers reframe) and
  **RB-003** (§appendix-deriv-A1) — still blocked on each other in
  the natural model→derivation order (RB-003 was promoted to
  medium-priority some time ago and unblocks RB-004); a derivation
  increment landing the A1 ρ-channel derivation independently is the
  natural next derivation-output run.

A reasonable next-run pick: **RB-010** (§results-C2 — strongest
single-section content available; one prose-only increment). A
secondary alternative: **RB-003** (the A1 ρ-channel derivation —
unblocks RB-004 model section, the spine of the "three levers"
reframe).

The earlier-recommended RB-007 (C3 iso-VDA contour maps) remains a
valid simulation-track pivot if the owner prefers to finish the
central-tendency confident-spine sim sweep before moving to prose.

---

## rb-004 — 2026-05-25 — C2 high-resolution VDA(r) v-family with closed-form r†(v) (simulation increment)

- **Run id:** `rb-004-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-006 (C2 high-resolution VDA(r), v ∈ {2,3,5,8,10}, V=0.5, N=4, ρ ∈ {0, 0.2}, with closed-form r†(v) marker)
- **Output kind:** simulation
- **Claims touched:** C2 (CONFIRMED-UNDER-ATTACK in live ledger — the rebuild's "confident spine" headline; mission §3.3); A1 (CONTESTED, the rb-002 r-dependent sign-flip generalised across the v-family as a v-dependent sign-flip of Δpeak)
- **Status:** done

### Headline thing built

`Rebuild/sims/C2--vda-vs-r-vfamily/` — the third simulation under
`Rebuild/sims/`, and the first to publish a **closed-form analytic
prediction** alongside a high-resolution numerical sweep. Two
deliverables land under `output/`:

1. `results.json` — full per-(v, ρ, r) VDA / R(P1..P4) / α* values;
   per-(v, ρ) peak (r*, VDA*); closed-form `r†(v)` at ρ=0 for the
   v-family and a continuous v-trace; recovery test block with FOUR
   pinned r values (the rb-002 reference triplet plus r=0.3831 as
   the new peak pin); a peak-consistency table showing `r* > r†(v)`
   for every v. 84 r × 5 v × 2 ρ = 840 P1 evaluations + 168 α_vb
   cells in 18.9 s wall-clock.
2. `figures/vda_curves_vfamily.png` — 2-panel (ρ=0 | ρ=0.2), five
   viridis curves per panel (v ∈ {2, 3, 5, 8, 10}), peak markers
   (white-filled dots), r†(v) vertical dashed lines on the ρ=0
   panel. The §results-C2 manuscript section will `\includegraphics`
   this.
3. `figures/r_dagger_vs_v.png` — r†(v) trace v ∈ [1.05, 12] with
   the v-family points highlighted and r†(v=1) ≈ 0.343 as a
   horizontal reference. Visualises §2.3's prediction that r†(v) is
   monotone-decreasing in v.

The headline contribution is that each VDA(r) curve is annotated
with the **closed-form escape threshold** the reviewer derived in
`Critique/derivations/C2--non-monotonic-vda.md` §2.3, eq. (2.5):

    r†(v) = K_u(v) / [(N-1) · K_c(v)]

evaluated at the P3-optimal criteria (c_c*, c_u*) at α = 1/N. The
rebuild lifts §2.3 from a derivation in `Critique/derivations/` into
a published analytic prediction with v-family numerics in the
manuscript's voice, plus empirical confirmation that the peak r*
lies above r†(v) for every v in the family — exactly the §2.3
mechanism (P1 escapes at r > r†(v), P2 stays locked below
r†(v=1) ≈ 0.343, VDA opens up between them).

### Simulation evidence (the headline numbers)

- **Recovery** vs rb-002 reference at v=5, ρ=0, **four** pinned r:

  | r       | metric | rb-002 ref | rb-004 obs | |Δ|      |
  |--------:|:-------|-----------:|-----------:|---------:|
  | 0.3831  | VDA    | 0.07986    | 0.07985    | 5.93e-6  |
  | 0.398   | VDA    | 0.07972    | 0.07972    | 1.07e-6  |
  | 0.398   | CF     | 0.82952    | 0.82952    | 9.87e-7  |
  | 1.000   | VDA    | 0.03983    | 0.03983    | 4.87e-6  |
  | 1.000   | CF     | 0.72823    | 0.72823    | 2.02e-6  |
  | 3.162   | VDA    | 0.00809    | 0.00809    | 1.01e-6  |
  | 3.162   | CF     | 0.64094    | 0.64094    | 1.73e-6  |

  All pass at ≤5e-5 (rb-002's logged precision). The ~6e-6 gap at
  the new r=0.3831 pin is the same ULP-level `scipy.special.ndtr`
  reordering rb-003 already reported in its CF recovery; mathematically
  identical, ULP-different.

- **Grid-refinement gain.** Finer 84-point grid raises the
  empirical peak of VDA(r) at v=5, ρ=0 from rb-002's 0.07986 (at
  r=0.3831 on its 25-point grid) to **0.08300** at r=0.3758. Same
  model, same α-grid, same V/v/N — the rb-002 / paper grid was
  one log-grid step coarse around the cost-dominant peak. The
  paper's `≈ 0.080` headline VDA-peak number for the reference
  regime is on the rb-002 grid; the rebuild's headline number is
  `≈ 0.083` on the finer grid.

- **r†(v) closed form**, v-family + v=1:

  | v   | r†(v)  | c_c*    | c_u*    | K_c(v)   | K_u     |
  |----:|-------:|--------:|--------:|---------:|--------:|
  | 1   | 0.3433 |  0.40   |  1.05   | 0.0930   | 0.0958  |
  | 2   | 0.1677 |  0.10   |  1.10   | 0.1722   | 0.0866  |
  | 3   | 0.0995 | −0.05   |  1.10   | 0.2698   | 0.0805  |
  | 5   | 0.0504 | −0.25   |  1.10   | 0.4937   | 0.0747  |
  | 8   | 0.0222 | −0.50   |  1.10   | 0.9979   | 0.0664  |
  | 10  | 0.0161 | −0.65   |  1.10   | 1.4097   | 0.0681  |

  Monotone-decreasing in v as §2.3 predicts (more reward for the
  cued hit ⇒ smaller r needed to escape uniform attention).

- **Peak-vs-threshold consistency** (ρ=0, variant A): peak r* >
  r†(v) for every v in {2, 3, 5, 8, 10}, with gap +0.28 to +0.35.
  The peak r* clusters near r†(v=1) ≈ 0.343 — sharper than §2.3
  states explicitly, but exactly the §2.3 mechanism (VDA is positive
  on roughly (r†(v), r†(v=1)) and the peak lies inside that
  interval).

- **A1 sensitivity** (ρ=0 → ρ=0.2): peak suppression at low v and
  amplification at v=10:

  | v   | peak ρ=0 | peak ρ=0.2 | Δpeak    |
  |----:|---------:|-----------:|---------:|
  | 2   | 0.01233  | 0.01036    | −0.00197 |
  | 3   | 0.03698  | 0.03291    | −0.00407 |
  | 5   | 0.08300  | 0.07954    | −0.00345 |
  | 8   | 0.14422  | 0.14355    | −0.00067 |
  | 10  | 0.18284  | 0.18387    | **+0.00103** |

  The rb-002 r-dependent A1 sign-flip generalises to a v-dependent
  sign-flip at the peak of VDA(r): ρ=0.2 suppresses the peak for
  low v, amplifies for high v.

Output digest:
`09ecef3c2c5a101820951398ed7d6e67d3398aede80c5f0bddfa42b6224fd783`.
Reproducible byte-for-byte on re-run (deterministic).

### Exact manuscript claim now licensed

The rebuilt §results-C2 may now state:

> *"Non-monotonicity of VDA in r (C2) is a theorem of the model
> definitions. The escape threshold
> `r†(v) = K_u(v) / [(N − 1)·K_c(v)]`, derived in §2.3 of the
> reviewer's re-derivation, separates the regime in which P1 commits
> attention non-uniformly from the regime in which P1 stays uniform.
> At the headline cell (N=4, V=0.5, variant A), r†(v) decreases
> monotonically from r†(v=1) = 0.343 to r†(v=10) = 0.016. The
> empirical peak of VDA(r) lies above r†(v) for every v in
> {2, 3, 5, 8, 10}, with gap +0.28 to +0.35 — exactly the §2.3
> mechanism that VDA opens up where P1 has escaped uniform attention
> but P2 has not, with the peak clustering near r†(v=1). Peak VDA
> magnitude grows monotonically with v (0.012 → 0.183 across the
> family). Promoting the A1 independence assumption to ρ = 0.2
> suppresses the peak at low v (−0.002 to −0.004) and amplifies at
> v=10 (+0.001), so the A1 sign-flip in dVDA/dρ has v-structure as
> well as r-structure."*

It does **not** yet license: (a) a closed-form `r†(v; ρ > 0)` —
needs RB-026 (spawned this run); (b) the same statement for
variant B — needs RB-027 (spawned); (c) a conservation-family band
on the peak magnitudes — needs RB-019 (A3 generalisation).

### What I built (file by file)

- `Rebuild/sims/C2--vda-vs-r-vfamily/run.py` — heavily commented sim:
  84-pt log-spaced r-grid (with 4 pinned r values for recovery),
  v-family loop, α_vb caching across v at fixed (r, ρ) for ~2×
  speedup, closed-form r†(v) helper using the P3-optimal criteria,
  recovery test that exits non-zero on any failure, two figures.
  Calls into `Rebuild/model` as the single source of truth.
- `Rebuild/sims/C2--vda-vs-r-vfamily/README.md` — what the sim does,
  headline numbers, recovery, manuscript claim licensed, caveats.
- `Rebuild/sims/C2--vda-vs-r-vfamily/output/results.json` — full
  numeric content + sha256 (267 kB).
- `Rebuild/sims/C2--vda-vs-r-vfamily/output/figures/vda_curves_vfamily.png`
- `Rebuild/sims/C2--vda-vs-r-vfamily/output/figures/r_dagger_vs_v.png`
- `Rebuild/conversations/2026-05-25-rebuilder-rb004-c2-vfamily.md`.
- Updates: `CLAIM_LEDGER.md` (C2 row upgraded with rb-004 backing +
  the r†(v) v-family numerics + the peak-consistency table +
  v-dependent A1 sign-flip note; "last reconciled" stamp → rb-004),
  `REBUILD_BACKLOG.md` (RB-006 → done; RB-010 notes updated to
  reflect unblocking + the artifacts it must cite; spawned RB-026
  for the ρ>0 closed form and RB-027 for the variant-B parallel
  scan), `rebuilder_state.json` (runs_completed: 3 → 4; sims_written:
  ["RB-002", "RB-005"] → ["RB-002", "RB-005", "RB-006"];
  claims_addressed: ["A1", "C1"] → ["A1", "C1", "C2"];
  +rb_004_sim_digest field; open/done task lists synced).

### Ledger reconciliation (vs. mission §3, prompt v0.2)

No new drift. Re-checked all 10 live verdict labels via
`grep current_label Critique/verdicts/*.md`: C1 CONTESTED, C2
CONFIRMED-UNDER-ATTACK, C3 CONTESTED, C4 CONFIRMED-CONDITIONAL, C5
CONFIRMED-UNDER-ATTACK; A1 CONTESTED, A2 CONFIRMED-CONDITIONAL, A3
CONTESTED, A6 WEAKLY-SUPPORTED (standing mild drift, direction
unchanged), A8 CONFIRMED-CONDITIONAL. All match §3 except A6
(already flagged `proposed_mission_change` since rb-001).

### Why the next run should care

rb-004 lands the **third sim of the three confident-spine headline
results** (the mission §3.3 "confident spine" is C2 non-monotonicity,
C5 symmetric recovery — already covered by the rb-001 recovery test —
and the central-tendency forms of C1/C3; rb-003 covered C1, rb-004
covers C2). The natural next sim increment is **RB-007** (C3 iso-VDA
contour maps), which finishes the central-tendency confident spine.

Alternatively — and this is the more leverage-yielding pivot — three
manuscript sections are now unblocked simultaneously:
- **RB-004** (model section, "three levers" reframe; rb-002 figures + RB-003 derivation that hasn't landed yet → still effectively blocked on RB-003)
- **RB-009** (§results-C1; rb-003 figures, sha256 91fc4692, Δ-distribution numbers)
- **RB-010** (§results-C2; rb-004 figures, sha256 09ecef3c, r†(v) v-family table, peak-consistency table)

But all three require **RB-022** (the manuscript skeleton — `main.tex`
+ section stubs + BUILD.md) to have a home for the prose. RB-022 has
been queued since bootstrap and is now overdue: with four sim
deliverables landed, the next run should be RB-022 followed by the
first manuscript-section increment (RB-010 is the cleanest target,
since rb-004's analytic content gives it the most material).

A second-best alternative is RB-007 first (finishing the C-row sim
sweep before pivoting to prose), with RB-022 + RB-010/RB-009 then
following in subsequent runs.

---

## rb-003 — 2026-05-25 — C1 distributional sweep (simulation increment)

- **Run id:** `rb-003-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-005 (C1 4,410-cell distributional sweep at ρ ∈ {0, 0.2})
- **Output kind:** simulation
- **Claims touched:** C1 (CONTESTED in live ledger); A1 (CONTESTED, extending the rb-002 headline-cell ordering cell-wise across the sweep)
- **Status:** done

### Headline thing built

`Rebuild/sims/C1--cf-distribution/` — the second simulation under
`Rebuild/sims/`, and the first to exercise the rebuilt model library
across the paper's *full* primary 4,410-cell parameter sweep rather
than at a single headline cell. Two ρ values (0 and 0.2) = 8,820
cell evaluations in 67.4 s wall-clock (scipy.special.ndtr backend).
Three deliverables land under `output/`:

1. `results.json` — full per-cell rewards/VDA/CF for both ρ values;
   per-(variant, ρ) distributional summaries; per-quadrant breakdown
   (V × r × variant); cell-wise CF(ρ=0.2) − CF(ρ=0) Δ-distribution
   per variant; recovery-test block vs the reviewer's CR-002 reference.
2. `figures/cf_histogram.png` — 4-panel (variant × ρ) CF histogram
   with the paper-floor 0.60 reference line, median annotation, and
   frac-below labels per panel. The visual restatement of C1 as a
   distribution rather than a floor.
3. `figures/cf_heatmap.png` — 4-panel (variant × ρ) CF over (r, V) at
   v=5. Shows the regime structure: low-V × high-r is the CF<0.6
   corner, high-V × low-r is the CF=1 saturation; the corner widens
   at ρ=0.2 in both variants (variant A more dramatically).
4. `figures/cf_curves.png` — 4-panel (variant × ρ) CF vs r at V≈0.5,
   v-family of 5 curves. Shows the v=1 curve sits highest (weakest
   value gradient → strongest criterion dominance) and v=5 sits
   lowest; ρ=0.2 pushes all curves downward in variant A more uniformly
   than in variant B.

### Simulation evidence (the headline numbers)

- **Recovery (ρ=0)**: cell-wise join against the reviewer's
  `Critique/replications/C1--criterion-fraction-floor/output/results.json`
  on all 4,410 cells. Max |ΔCF| = 1.466e-6; max |ΔR(P1..P4)| ≤
  5.65e-7; mean |ΔCF| = 2.48e-7. The reviewer's published headline
  numbers reproduce exactly to 4-decimal precision: variant-A min CF
  = 0.5587, variant-B min CF = 0.3040, max CF = 1.0000, combined
  median ≈ 0.76. The ~1.5e-6 gap (vs the floating-point identity rb-002
  achieved at one cell) is a ULP-level `scipy.special.ndtr` reordering
  artifact in `floor_R` (`Phi(b)` vs `1 - Phi(-b)`); mathematically
  identical, ULP-different under the same backend. The gap is well
  past the 4-decimal precision of any reported number — the recovery
  test passes for all manuscript purposes.

- **Distributional restatement of C1 (ρ=0)**, per variant, 2205 cells each:

  | variant | min | median | max | frac<0.5 | frac<0.6 | frac<0.8 |
  |---|---|---|---|---|---|---|
  | A | 0.5587 | **0.7552** | 1.0000 | 0.0000 | 0.0703 | 0.5701 |
  | B | 0.3040 | **0.7682** | 1.0000 | 0.0803 | 0.1973 | 0.5429 |

  The paper's C1 floor `CF ∈ [0.60, 0.96]` is decisively retracted on
  both ends: variant-A strict min 0.5587 < 0.60; variant-B 8% of cells
  below 0.50. The substantive "criterion typically dominates" reading
  (median ≈ 0.76 in both variants, CF ≥ 0.5 in 100% of variant-A and
  92% of variant-B cells) survives.

- **A1 sensitivity (ρ=0.2)**, headline-number shifts:

  | variant | metric | ρ=0 | ρ=0.2 | Δ |
  |---|---|---|---|---|
  | A | min CF       | 0.5587 | **0.4854** | −0.073 |
  | A | median CF    | 0.7552 | 0.7197 | −0.035 |
  | A | frac<0.6     | 0.070  | **0.222** | **+0.152** |
  | B | min CF       | 0.3040 | 0.2406 | −0.063 |
  | B | median CF    | 0.7682 | 0.7538 | −0.014 |
  | B | frac<0.6     | 0.197  | 0.252  | +0.055 |

- **Cell-wise ΔCF = CF(ρ=0.2) − CF(ρ=0)** (the rb-002 headline-cell
  finding generalised across the sweep):

  | variant | n | frac dec | frac inc | frac flat | median Δ | \|Δ\|_q95 |
  |---|---|---|---|---|---|---|
  | A | 2205 | **0.838** | 0.083 | 0.079 | −0.0348 | 0.0640 |
  | B | 2205 | 0.637 | 0.235 | 0.127 | −0.0093 | 0.0650 |

  rb-002's variant-A monotone-down ordering at the headline cell
  generalises to 84% of variant-A cells; rb-002's variant-B
  headline-cell flatness is one manifestation of a broader sign-mixed
  variant-B pattern (24% of cells INCREASE in ρ).

Output digest: `91fc4692dbc106eca9c90770c79e22f7f4757d76421ed55e7e8e91f80e44706c`.
Reproducible byte-for-byte on re-run (deterministic grids, no RNG).

### Exact manuscript claim now licensed

The rebuilt §results-C1 may now state:

> *"Across the paper's primary 4,410-cell (r, V, v) sweep, the criterion
> fraction CF spans [0.56, 1.00] in variant A and [0.30, 1.00] in
> variant B, with a median of 0.76 in both cases. The paper's stated
> range CF ∈ [0.60, 0.96] is too narrow on both ends: 7% of variant-A
> cells fall below 0.60, and 8% of variant-B cells fall below 0.50.
> The substantive 'criterion typically dominates' reading survives —
> the median is comfortably above 0.5 and the distribution mass is
> concentrated above 0.6 — but the categorical floor is retracted.
> Promoting the A1 independence assumption to an equicorrelation
> parameter ρ = 0.2 amplifies the tail: the fraction of variant-A
> cells with CF < 0.6 rises from 0.07 to 0.22. Cell-wise
> CF(ρ=0.2) ≤ CF(ρ=0) holds in 84% of variant-A cells (median
> ΔCF = −0.035); in variant B the ordering is weaker (64%) and 24%
> of cells move upward, so the CF-lever effect of A1 is reported as
> a variant-A pattern with a variant-B sensitivity rather than a
> uniform claim."*

It does **not** yet license: (a) the conservation-family band on
these distributional numbers — needs RB-019 (A3 simulation); (b) a
closed-form predicate for the CF<0.5 corner — needs RB-024
(spawned this run); (c) the cell-wise VDA sign-flip parallel to the
CF Δ-distribution — needs RB-025 (spawned this run).

### What I built (file by file)

- `Rebuild/sims/C1--cf-distribution/run.py` — full 4,410-cell sweep
  on the rebuilt model module, ρ ∈ {0, 0.2}, with the reviewer's
  α-grid (Δα = 0.02) for byte-for-byte recovery testing,
  value-blind α caching, distribution + per-quadrant + Δ-distribution
  summaries, three figures, sha256-stamped JSON. Heavily commented;
  uses `Rebuild/model` as the single source of truth.
- `Rebuild/sims/C1--cf-distribution/README.md` — what the sim computes,
  how to run, headline numbers, manuscript claim licensed, caveats.
- `Rebuild/sims/C1--cf-distribution/output/results.json` — full numeric
  content + sha256 (4.2 MB).
- `Rebuild/sims/C1--cf-distribution/output/figures/cf_histogram.png`
- `Rebuild/sims/C1--cf-distribution/output/figures/cf_heatmap.png`
- `Rebuild/sims/C1--cf-distribution/output/figures/cf_curves.png`
- `Rebuild/conversations/2026-05-25-rebuilder-rb003-c1-distributional-sweep.md`.
- Updates: `CLAIM_LEDGER.md` (C1 row updated with rb-003 backing + the
  full distributional numbers + cell-wise A1 generalisation),
  `REBUILD_BACKLOG.md` (RB-005 → done; spawned RB-024 — closed-form
  CF<0.5 corner derivation; RB-025 — cell-wise VDA sign-flip
  simulation), `rebuilder_state.json` (runs_completed: 2 → 3;
  sims_written: ["RB-002"] → ["RB-002", "RB-005"];
  +rb_003_sim_digest field).

### Ledger reconciliation (vs. mission §3, prompt v0.2)

No new drift since rb-002. Re-checked all 10 live verdict labels at
the start of this run (`current_label:` frontmatter via grep): C1
CONTESTED, C2 CONFIRMED-UNDER-ATTACK, C3 CONTESTED, C4
CONFIRMED-CONDITIONAL, C5 CONFIRMED-UNDER-ATTACK; A1 CONTESTED,
A2 CONFIRMED-CONDITIONAL, A3 CONTESTED, A6 WEAKLY-SUPPORTED
(still pre-CONTESTED — the mild drift rb-001 flagged remains
mild and direction-unchanged), A8 CONFIRMED-CONDITIONAL. All match
§3's table except A6 (the standing mild drift).

### Why the next run should care

rb-003 turned the rb-002 single-cell A1 result into a cell-wise
ordering claim and replaced the paper's categorical C1 floor with a
publication-ready distribution. The §results-C1 and §results-A1
manuscript sections (RB-009, RB-004) can now be drafted citing
rb-003's figures and Δ-distribution numbers. The natural next
high-priority increment is **RB-006** (C2 high-resolution VDA(r) at
multiple v values, marking the closed-form escape threshold r†(v) —
the rebuild's "confident spine" headline result, mission §3.3). After
RB-006, the unblocked queue is RB-003 (A1 derivation), RB-007 (C3
contour map), RB-008 (C4 inversion onset), RB-013 (C5 appendix), and
the three model-extension tracks RB-014 (A2), RB-015 (A3), RB-017
(A8). The manuscript-skeleton task RB-022 stays queued; the natural
moment to land it is right before the first manuscript-section
increment (RB-004 or RB-009), so the section files have a home.

---



---

## rb-002 — 2026-05-25 — A1 ρ-channel headline simulation (simulation increment)

- **Run id:** `rb-002-2026-05-25`
- **Prompt version:** 0.2
- **Task worked:** RB-002 (A1 VDA(r, ρ) and CF(ρ) at the C2 headline cell, both variants)
- **Output kind:** simulation
- **Claims touched:** A1 (CONTESTED in live ledger). C2 peak-VDA at ρ=0 also corroborated as a side product (peak 0.07986 at r ≈ 0.383).
- **Status:** done

### Headline thing built

`Rebuild/sims/A1--rho-channel/` — the first artifact under `Rebuild/sims/`,
and the first simulation to call into the rebuilt `Rebuild/model/`
library rather than into the reviewer's one-off CR-052 script. At the
C2/Figure-4 headline cell (N=4, d'_max=2, f_0=0.5, h=√, V=0.5, v=5),
both reward variants (A: `CR = V v + (1−V)`; B: `CR = 1`), the sim
sweeps ρ ∈ {0.0, 0.1, 0.2, 0.3, 0.4} over a log-spaced r grid (25
points in [0.1, 10] with the C2 reference points pinned). Three
deliverables land under `output/`:

1. `results.json` — full numeric content of VDA(r; ρ) and CF(ρ) sweeps,
   per-ρ peak VDA + argmax, pointwise upper-bound diagnostic, first
   sign-flip r, CF-monotone-down diagnostic, recovery-test block.
2. `figures/vda_curves_variantA.png` and `vda_curves_variantB.png` —
   five curves each (one per ρ), the family-of-curves figure the
   manuscript model-section will cite.
3. `figures/cf_vs_rho.png` — CF(ρ) at three r values (0.398, 1.0,
   3.162), variants A and B side by side; the figure that visualises
   *what independence actually upper-bounds*.

### Simulation evidence (the headline numbers)

- **Recovery (ρ=0)**: single-cell VDA/CF/R_P1/R_P3/R_P4 at r ∈ {0.398,
  1.0, 3.162} reproduce the reviewer's reference output
  (`Critique/replications/A1--correlated-fa/output/results.json`)
  to **floating-point identity** (max|d| = 0.00e+00 at every cell).
  Peak VDA(r; 0) = 0.07986 at r = 0.3831 matches the reviewer's
  reported 0.07986 at r ≈ 0.383. Slepian monotonicity of P_no-fa(ρ)
  satisfied across ρ ∈ {0, 0.05, ..., 0.8}; independence is the
  P_no-fa minimum.

- **VDA(r) variant A peak vs ρ**: 0.07986 → 0.08110 → 0.07955 →
  0.07763 → 0.07368 (ρ = 0.0, 0.1, 0.2, 0.3, 0.4). Peak r drifts
  0.3831 → 0.3980. The pointwise upper-bound
  `VDA(r; ρ) ≤ VDA(r; 0)` **fails** for every ρ > 0; max excess over
  the ρ=0 curve grows from +4.84e-3 (ρ=0.1) to +1.01e-2 (ρ=0.4);
  first sign-flip r ≈ 0.38–0.56. This reproduces the reviewer's
  run-017 result and is the load-bearing damage to the paper's §5.5
  "upper bound on VDA" self-characterisation.

- **CF(ρ) variant A** at three r values:
  - r=0.398: 0.8295 → 0.8181 → 0.8071 → 0.7969 → 0.7875
  - r=1.0:   0.7282 → 0.7097 → 0.6903 → 0.6698 → 0.6473
  - r=3.162: 0.6409 → 0.6180 → 0.5936 → 0.5673 → 0.5386
  Monotone-down in ρ at every r — independence upper-bounds the
  *criterion fraction*.

- **Variant B caveat (honest reporting per §5.5 of the mission)**: at
  the headline cell, CF(ρ) in variant B is essentially **flat** in ρ
  at all three r values; the manuscript will report the CF upper-bound
  as a **variant-A** result, with variant B as a sensitivity in which
  the leverage washes out. VDA-rises-with-ρ does survive in variant B
  but at a smaller absolute scale (max excess +2.94e-3, sign-flip
  r ≈ 0.26).

Output digest: `b692c06456530ccd1b319762d8a948814324d3129f39902ce9531a66d1206614`.
Reproducible byte-for-byte on re-run (confirmed by a second invocation).

### Exact manuscript claim now licensed

The rebuilt §results-A1 may now state:
> *"At the C2 headline cell (N=4, V=0.5, v=5, d'_max=2, f_0=0.5,
> h=√), promoting the per-location independence assumption (A1) to an
> equicorrelation parameter ρ produces a sign-dependent change in
> VDA(r). The pointwise upper-bound
> $\mathrm{VDA}(r;\rho)\le\mathrm{VDA}(r;0)$ implicit in §5.5 of the
> inherited model fails for every ρ > 0 in our sweep: VDA is suppressed
> at small r (cost-dominant) but **amplified** at r ≳ 0.5
> (benefit-dominant), with a +1.0% to +1.6% rise in the peak at
> ρ = 0.1 and a sign-flip r ≈ 0.4–0.6 (variant A). What ρ = 0 does
> upper-bound, monotonically, is the **criterion fraction**:
> CF(r; 0) ≥ CF(r; ρ) at every reference r (variant A); the same
> ordering does not hold in variant B at the headline cell, which we
> report as a sensitivity."*

It does **not** yet license: (a) the same claim at non-headline cells —
that needs RB-005 (C1 4,410-cell sweep at ρ ∈ {0, 0.2}); (b) a contour
band over (V, v) — RB-007; (c) the formal Slepian-monotonicity
derivation that A1 enters E[R] in exactly one place — RB-003.

### What I built (file by file)

- `Rebuild/sims/A1--rho-channel/run.py` — sweep + recovery + figures,
  heavily commented, uses `Rebuild/model` as the single source of
  truth, deterministic.
- `Rebuild/sims/A1--rho-channel/README.md` — what the sim computes,
  how to run, headline numbers, the variant-B honest-reporting note.
- `Rebuild/sims/A1--rho-channel/output/results.json` — full numeric
  content + sha256.
- `Rebuild/sims/A1--rho-channel/output/figures/vda_curves_variantA.png`
- `Rebuild/sims/A1--rho-channel/output/figures/vda_curves_variantB.png`
- `Rebuild/sims/A1--rho-channel/output/figures/cf_vs_rho.png`
- `Rebuild/conversations/2026-05-25-rebuilder-rb002-a1-rho-sim.md`.
- Updates: `CLAIM_LEDGER.md` (A1 row now lists rb-002 backing + the
  variant-B sensitivity caveat), `REBUILD_BACKLOG.md` (RB-002 → done;
  spawned RB-023 — finer-ρ-grid + variant-B sensitivity follow-up),
  `rebuilder_state.json` (runs_completed: 1 → 2; sims_written: [] →
  ["RB-002"]; +rb_002_sim_digest field).

### Ledger reconciliation (vs. mission §3, prompt v0.2)

No new drift since rb-001. A1 still CONTESTED, A6 still
WEAKLY-SUPPORTED (rb-001 already flagged this mild drift as
`proposed_mission_change: true`). All other labels match §3 of the
prompt.

### Why the next run should care

RB-002 turned the rb-001 model module into a manuscript-citable
artifact: the figures the §model and §results-A1 sections will
`\include{}` now exist, and the recovery contract is tightened from
"matches paper Eq. 9" to "matches reviewer reference numbers
bit-for-bit at every reported cell." The natural next increment is
**RB-003** (the A1 derivation — promote the equicorrelated 1-D
quadrature + the Slepian-monotonicity argument into
`Rebuild/derivations/A1--rho-channel.md`), which then unblocks
**RB-004** (the manuscript model section that cites both RB-002's
figures and RB-003's derivation). Alternatively, the next high-priority
*simulation* is **RB-005** (the C1 4,410-cell distributional sweep at
ρ ∈ {0, 0.2}), which is independent of RB-003 and lets the rebuild
extend the variant-A CF-upper-bound claim from "the headline cell" to
"across the 4,410-cell sweep."

---

## rb-001 — 2026-05-25 — bootstrap + A1 decorrelation channel (model increment)

- **Run id:** `185e9941-2790-436e-958e-cb8470f17548`
- **Prompt version:** 0.2
- **Task worked:** RB-001 (bootstrap + A1 model increment)
- **Output kind:** model
- **Claims touched:** A1; rho->0 recovery test also covers C5's symmetric-recovery contract
- **Status:** done

### Headline thing built

Bootstrapped `Rebuild/` skeleton per mission §6 and §9.6. Wired the
**A1 decorrelation channel** into the rebuilt model module
`Rebuild/model/`: per-location SDT decisions are no longer independent
by assumption; the joint no-false-alarm probability is now the exact
equicorrelated-Gaussian orthant probability, evaluated by 1-D
Gauss–Hermite quadrature (`nq = 64`),

    P_no-fa(rho) = INT  Phi((b_c - sqrt(rho) z) / sqrt(1 - rho))
                      * Phi((b_u - sqrt(rho) z) / sqrt(1 - rho))^(N-1)
                      * phi(z) dz

with the inherited paper's Eq. 9 recovered exactly at `rho = 0`. The
public surface is `model.HeadlineCell`, `model.policies`,
`model.vda_curve`, `model.slepian_curve`.

### Simulation evidence (recovery test, the contract on every future extension)

`Rebuild/model/tests/test_recovery.py` — 7/7 PASS.

- `p_no_fa(rho=0)` equals `Phi(b_c) Phi(b_u)^(N-1)` to **binary equality**
  across the full criterion grid.
- `p_no_fa(rho->0)` converges with the expected O(rho) scaling.
- Policy reward (P1–P4), VDA, CF at `(rho=0, V=0.5, v=5, N=4, d'_max=2,
  f_0=0.5, h=sqrt, variant A)` match the reviewer's logged numbers
  (`Critique/replications/A1--correlated-fa/output/results.json`) to
  **floating-point identity** at `r in {0.398, 1, 3.162}`:
  - `r=0.398`: VDA = 0.07972, CF = 0.82952 (d = 0e+00)
  - `r=1.0`:   VDA = 0.03983, CF = 0.72823 (d = 0e+00)
  - `r=3.162`: VDA = 0.00809, CF = 0.64094 (d = 0e+00)
- Peak `VDA(r)` at `rho=0`: 0.07986 at r = 0.3831 (matches reviewer's
  reported 0.0799 at r ~ 0.383).
- Slepian monotonicity: `P_no-fa(rho)` monotone-up over
  `rho in {0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8}`, independent corner
  is the minimum.

Output digest: `d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f`.
Reproducible byte-for-byte on re-run.

### Exact manuscript claim now licensed

The rebuilt model section may now state: *"The rebuilt model promotes
the per-location SDT independence assumption (A1) to a tunable
equicorrelation parameter rho in [0, 1). The inherited model is
recovered exactly as the rho = 0 case (see Recovery Theorem,
Appendix A); the change-trial term is linear in marginal hit rates, so
A1 enters the reward in exactly one place — the joint no-false-alarm
probability, replaced here by its exact equicorrelated-Gaussian
expression evaluated by 1-D quadrature."*

It does **not** yet license any statement about the *behaviour* of
rho > 0 — that requires RB-002 (the VDA(r, rho) / CF(rho) simulation).

### What I built (file by file)

- `Rebuild/README.md` — workspace overview, reading order, policy.
- `Rebuild/CLAIM_LEDGER.md` — disposition table (live).
- `Rebuild/REBUILD_BACKLOG.md` — RB-001 to RB-022 seeded.
- `Rebuild/rebuilder_state.json` — state (atomic write).
- `Rebuild/model/core.py` — model primitives + `policies()` over P1–P4.
- `Rebuild/model/__init__.py` — public surface.
- `Rebuild/model/README.md` — what's in the module, what changed,
  recovery contract.
- `Rebuild/model/tests/test_recovery.py` — `rho -> 0` recovery
  contract (7 checks).
- `Rebuild/model/tests/recovery_output.json` — latest test output +
  sha256.
- `Rebuild/conversations/2026-05-25-rebuilder-bootstrap-a1-model.md`.

### Ledger reconciliation (vs. mission §3, prompt v0.2)

| claim | mission §3 | live verdict | drift? |
| --- | --- | --- | --- |
| C1 | CONTESTED | CONTESTED | no |
| C2 | CONFIRMED-UNDER-ATTACK | CONFIRMED-UNDER-ATTACK | no |
| C3 | CONTESTED | CONTESTED | no |
| C4 | CONFIRMED-CONDITIONAL | CONFIRMED-CONDITIONAL | no |
| C5 | CONFIRMED-UNDER-ATTACK | CONFIRMED-UNDER-ATTACK | no |
| A1 | CONTESTED | CONTESTED | no |
| A2 | CONFIRMED-CONDITIONAL | CONFIRMED-CONDITIONAL | no |
| A3 | CONTESTED | CONTESTED | no |
| A6 | OPEN/in-progress | **WEAKLY-SUPPORTED** | **yes (mild)** |
| A8 | CONFIRMED-CONDITIONAL | CONFIRMED-CONDITIONAL | no |

A6's drift is mild (still pre-CONTESTED, direction unchanged). The
rebuilt strength for A6 is unchanged. Backlog item RB-016 remains
`blocked` waiting for a decisive label. Flagged
`proposed_mission_change: true` for owner ratification at next prompt
revision.

### Why the next run should care

RB-001 turned on the rho channel and proved the inherited model is the
rho=0 corner. The next high-priority increment is **RB-002** (the
A1 VDA(r, rho) and CF(rho) simulation): the same surface the reviewer
exhibited in run-017, re-run from the rebuilt model module rather than
the one-off script, with the resulting figures landed under
`Rebuild/sims/A1--rho-channel/output/` so the manuscript can cite
them. Once RB-002 lands, RB-003 (derivation) and RB-004 (manuscript
model section) unblock in that order.
