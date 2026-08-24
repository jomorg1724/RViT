---
type: conversation
agent: constructive-rebuilder
prompt_version: "0.2"
run_id: rb-015-2026-05-25
started: "2026-05-25T20:00:00Z"
ended: "2026-05-25T20:50:00Z"
worked_on: RB-015
output_kind: model
claims_touched: [A3, C5]
artifacts_written:
  - Rebuild/model/core.py (modified — beta_gamma extended, cons_p threaded through d_prime_asym/_alpha_opt/HeadlineCell/policies; module docstring extended with CONSERVATION FAMILY block)
  - Rebuild/model/tests/test_conservation_family.py (new — 14/14 PASS, sha256 f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e)
  - Rebuild/model/tests/conservation_family_output.json (new — numerical output + digest)
  - Rebuild/model/README.md (modified — added "A3 conservation family (rb-015)" subsection + recovery contract block + Files table entry + run instructions)
  - Rebuild/CLAIM_LEDGER.md (modified — A3 row backing extended; C5 row backing extended with conservation-form-invariance observation; reconcile note updated to rb-015)
  - Rebuild/REBUILD_BACKLOG.md (modified — RB-015 done; spawned RB-033, RB-034; RB-019 notes updated to reflect prereq satisfied)
  - Rebuild/rebuilder_state.json (modified — atomic rewrite)
  - Rebuild/BUILD_LOG.md (modified — rb-015 DONE entry)
papers_added: []
spawned_tasks: [RB-033, RB-034]
---

# What I built

The **A3 conservation-family model increment**: generalised `beta_gamma()` in
`Rebuild/model/core.py` from the paper's fixed additive form
$(\beta = 2r/(r+1), \gamma = 2/(r+1))$ to the one-parameter
**power-mean conservation family**

$$M_p(\beta, \gamma) := \left(\frac{\beta^p + \gamma^p}{2}\right)^{1/p} = 1
\qquad (\text{with } M_0 := \sqrt{\beta\gamma}),$$

together with $\beta/\gamma = r$. The closed-form solution is

$$\gamma(r, p) = \left(\frac{2}{r^p + 1}\right)^{1/p}, \quad \beta(r, p) = r\gamma(r, p)
\qquad (p \ne 0),$$
$$\gamma(r, 0) = r^{-1/2}, \quad \beta(r, 0) = r^{1/2} \quad (p = 0).$$

Recovered special cases:

| $p$ | $M_p$ | constraint | $(\beta, \gamma)$ |
| --- | --- | --- | --- |
| $1$  | arithmetic | $\beta + \gamma = 2$ (paper A3) | $(2r/(r+1),\, 2/(r+1))$ |
| $0$  | geometric  | $\beta\gamma = 1$ (multiplicative) | $(\sqrt{r},\, 1/\sqrt{r})$ |
| $-1$ | harmonic   | $2\beta\gamma/(\beta+\gamma) = 1$ | $((r+1)/2,\, (r+1)/(2r))$ |

The parameter `cons_p` is now a field on `HeadlineCell` (default `1.0`, so the
back-compat path is "do nothing"). It is threaded through `d_prime_asym`,
`_alpha_opt`, and `policies` to influence every reward/policy evaluation. The
$p=1$ branch in `beta_gamma` literally returns the paper's expressions with
no `**` operator, so additive recovery is *binary*.

# How it connects to the ledger

- **A3 (CONTESTED → unchanged rebuilt strength, now wired).** The CLAIM_LEDGER
  A3 row already licensed a "general conservation family parameterised so
  additive ($\beta+\gamma=2$) and multiplicative ($\beta\gamma=1$) are special
  cases." rb-015 turns that license into a recovery-tested, byte-compatible
  model. The strength does not move; the *backing* column gains
  `Rebuild/model/core.py` + `Rebuild/model/tests/test_conservation_family.py`
  (14/14 PASS, sha256 `f4f57a89…`). The downstream sweep RB-019 is now
  unblocked.

- **C5 (CONFIRMED-UNDER-ATTACK → strengthened qualitatively).** A free
  corollary of the power-mean construction: at $r = 1$, *every* member of
  the family has $\beta(1, p) = \gamma(1, p) = 1$ exactly. (Setting
  $\beta = \gamma$ in any $M_p$ with $M_p = 1$ forces $\beta = \gamma = 1$.)
  This says the C5 symmetric-recovery result is **conservation-form-invariant
  by construction** — swapping the conservation rule cannot move the $r = 1$
  exact recovery. Verified numerically: `policies(p=0, r=1)` equals
  `policies(p=1, r=1)` to **floating-point identity** across all eight
  returned keys (R_P1, R_P2, R_P3, R_P4, VDA, CF, alpha_P1, alpha_vb). The
  CLAIM_LEDGER C5 row's backing column gains this observation; the
  manuscript §appendix-C5 (RB-013) can now cite the construction rather
  than introduce a one-line ad-hoc argument.

- **A1 contract preserved.** Re-ran `test_recovery.py` post-edits → 7/7 PASS,
  sha256 `d3c62215…` unchanged from rb-001. Full back-compat verified
  end-to-end: every existing simulation that calls into the model module
  produces numerically identical output post-rb-015.

# Simulation evidence

Tests live in `Rebuild/model/tests/test_conservation_family.py`. All 14 PASS;
output digest `f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e`.

**(1) Family identities (3 tests).** $\beta(r,p) / \gamma(r,p) = r$ exact to
4.4e-16 across $r \in \{0.1, 0.316, 0.398, 1.0, 3.162, 10.0\}$ ×
$p \in \{-2, -1, -0.5, 0, 0.5, 1, 2\}$ (42 cells); $M_p(\beta, \gamma) = 1$
exact to 4.4e-16 across the same grid (this is the round-trip identity for
the closed form); $\beta(1, p) = \gamma(1, p) = 1$ *binary* across
$p \in \{-2..+2\}$ (the C5 conservation-form-invariance observation,
hard-checked).

**(2) Additive $p = 1$ byte-exact recovery (4 tests).** `beta_gamma(r, p=1.0)`
returns the legacy $(2r/(r+1), 2/(r+1))$ bit-for-bit on the 21-point log-$r$
grid; `policies(r, HeadlineCell(cons_p=1.0))` reproduces the rb-001
`REVIEWER_TARGETS_RHO0` pins to **zero diff** at $r \in \{0.398, 1.0, 3.162\}$
(VDA, CF, R_P1, R_P4 all match to FP identity).

**(3) Multiplicative $p = 0$ recovery vs reviewer A3 (7 tests).** Six
$r$-pin cells $r \in \{0.1, 0.316, 0.398, 1.0, 3.162, 10.0\}$ from
`Critique/replications/A3--multiplicative-conservation/output/results.json`,
`block_c2_c1.families.multiplicative.rows`. Worst-cell observed diff:

| $r$       | $|d\,\mathrm{VDA}|$ | $|d\,\mathrm{CF}|$ | $|d\,\mathrm{R\_P1}|$ |
| ---       | ---                | ---                | ---                  |
| 0.1       | 2.2e-7             | 3.8e-7             | 2.5e-7               |
| 0.316     | 2.7e-7             | 3.9e-7             | 2.6e-7               |
| 0.398     | 2.0e-7             | 2.4e-7             | 5.1e-7               |
| 1.0       | 1.1e-7             | 3.2e-7             | 1.8e-7               |
| 3.162     | 5.3e-8             | 3.3e-7             | 6.3e-7               |
| 10.0      | 1.2e-8             | 9.4e-8             | 3.7e-7               |

Max `|d|` = 6.3e-7 on R_P1 at $r = 3.162$, well below 1e-5 tolerance. The
residual is the cross-Phi-backend ULP-level reordering rb-003 already saw at
the same regime (paper's A&S 7.1.26 vs the rebuilt module's
`scipy.special.ndtr`). Plus the **symmetric-corner identity**
`policies(p=0, r=1) == policies(p=1, r=1)` to floating-point identity across
all 8 returned keys (the conservation choice is invisible at $r = 1$, by
construction).

**A1 recovery.** Re-running `Rebuild/model/tests/test_recovery.py` after the
edits produces 7/7 PASS and sha256 `d3c62215…` unchanged from rb-001 — the
back-compat path is byte-for-byte preserved.

# What the manuscript can now say

The CLAIM_LEDGER ceilings (the strength the manuscript may state):

- **A3 row (rebuilt strength, unchanged but now wired).** The rebuilt model
  implements the power-mean conservation family $M_p(\beta, \gamma) = 1$
  with $\beta/\gamma = r$, indexed by `cons_p` on `HeadlineCell`. Additive
  ($p = 1$) is the inherited paper form, *byte-exact* recovered;
  multiplicative ($p = 0$) is the reviewer's A3 extension, recovered to
  6.3e-7. Conservation choice is a model assumption, not a derived
  statement; headline numbers (C1 CF, C2 peak VDA, C3 boundary) will be
  reported as a *band across* $p$ in the downstream sweep increment
  (RB-019).
- **C5 row (rebuilt strength, strengthened qualitatively).** The symmetric
  recovery result is *conservation-form-invariant by construction* — at
  $r = 1$, every $M_p$-constrained $(\beta, \gamma)$ pair with
  $\beta = \gamma$ forces $\beta = \gamma = 1$, so swapping the conservation
  rule does not move the $r = 1$ exact recovery. Verified at the level of
  `policies()`.

**The rebuilt paper may NOT yet say** "headline numbers shift by X% between
additive and multiplicative on the 4,410-cell sweep" — that band claim is
licensed by the reviewer's A3 numerics but not yet *rebuilt-side* simulated;
the sweep is RB-019.

# Next increment

The natural dependency-order continuation is **RB-019** (A3
conservation-family band on headline numbers; sim, prereq RB-015 now done).
RB-019 turns the rebuilt-side family into a rebuilt-side *empirical band*
on the manuscript's headline numbers, replacing the inherited §5.5
single-sentence treatment of multiplicative conservation with the
§3.3-unifying-reframe band. Minimum-viable cut: (a) VDA($r$) at the C2
headline cell across $p \in \{0, 0.5, 1.0\}$ on the rb-006 84-$r$-point
grid, and (b) the 4,410-cell C1 sweep at $p \in \{0, 1\}$ to reproduce the
reviewer's median-CF and frac<0.5 band.

**Alternative branches available**, in priority order:

1. **RB-013** (§appendix-C5 manuscript, prereq RB-001 done, low effort).
   Now strengthened by the rb-015 conservation-form-invariance corollary;
   would close the 5th headline-claim section in one short run.
2. **RB-014** (A2 heterogeneous-$r$ model extension, prereq RB-001 done,
   medium effort). Opens the A2/A8 heterogeneity thread — the third of
   the rebuild's three extension levers (after A1 ρ and A3 conservation).

# Wiki cross-references

§11-style mechanism-keyword sweep performed on
`research_db/papers/`, `research_db/concepts/`, `research_db/threads/` with
keywords {power mean, generalised mean, Hardy-Littlewood-Pólya,
conservation, asymmetric scaling, $\beta + \gamma = 2$, $\beta\gamma = 1$}.

- `research_db/papers/` — no relevant stubs. The Hardy-Littlewood-Pólya 1934
  *Inequalities* monograph and any power-mean reference fall in the
  math-methods gap inherited from rb-008/rb-014 (Slepian 1962, Tong 1990 not
  stubbed). Out of rebuilder scope per the reviewer's CR-035/CR-037
  backlog; if RB-033 (formal A3 derivation, spawned this run) lands, it
  will cite Hardy-Littlewood-Pólya by full bibliographic reference.
- `research_db/concepts/` — no entries on conservation rules or
  asymmetric-scaling families.
- `research_db/threads/` — none of the existing threads (visual attention,
  WM/VWM, hippocampus, world models, RViT+, MCLSTM) cover conservation
  rules.

No new `research_db/papers/` stubs added; `audit.py` not re-run (no wiki
writes).
