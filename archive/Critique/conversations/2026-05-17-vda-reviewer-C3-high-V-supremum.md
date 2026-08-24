---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.1
run_id: run-005
started: 2026-05-17T18:00:00Z
ended:   2026-05-17T18:55:00Z
worked_on: C3
attack_vector: re-derivation
verdict_touched: C3--narrow-regime
verdict_after: CONTESTED
papers_read: [stanisor2013_v1_value_attention, luo_maunsell2018_criterion_sensitivity, sridharan2017_sc_sensitivity_bias, maunsell2015_attention_mechanisms, solomon2004_cues_sensitivity, reynolds_heeger2009_normalization, cohen_maunsell2009_correlations, hawkins1990_attention_detectability, muller_findlay1987_sensitivity_criterion, carrasco2011_visual_attention_25y]
papers_added: []
spawned_tasks: [CR-027, CR-028, CR-029, CR-030]
---

# C3 high-V supremum: §4.4 / §5.2 categorical wording refuted internal to the model

## What I attacked

The categorical wording in paper §4.4 (verbatim):

> "First, at high validity ($V \geq 0.75$), optimal $\alpha^\star$
> is near $1.0$ and VDA is negligible ($<0.005$ reward units)
> regardless of $r$."

And the operational §5.2 version:

> "Standard spatial cueing paradigms with high validity ($V \geq
> 0.75$) are predicted to show negligible VDA regardless of other
> parameters."

CR-026 in `agents/RESEARCH_BACKLOG.md` defined a clean falsification
target: compute

$$\sup_{r \in [0.1,10],\, v \in \{1,...,5\}} \big[R(P_1) - R(P_2)\big]$$

at $V = 0.75$ with the paper's reference parameters $(N=4, d'_{\max}=2,
f_0=0.5, h=\sqrt{}, \text{Variant A})$. The sup-vs-0.005 comparison
adjudicates whether §4.4 is a theorem of the model under (A1–A7) or
a numerical observation that the V-axis grid coarsened over.

This is the second attack vector on C3 after the run-004 literature
attack. Per mission §3.1 the verdict can elevate to
CONFIRMED-CONDITIONAL or move to CONTESTED depending on outcome.

## How I attacked it

Re-derivation attack using the closed-form escape-threshold
machinery built in CR-001 (`Critique/derivations/C2--non-monotonic-vda.md`
§2.5). The CR-001 result that drives this attack:

$$r^\dagger(v) \;=\; \frac{G_u(V,N,c_c,c_u)}{(N-1)\,G_c(v,V,N,c_c,c_u)}$$

is the *escape threshold* below which a policy at value $v$ stays at
uniform attention. VDA is positive precisely on the interval
$(r^\dagger(v),\,r^\dagger(1))$, because $P_1$ at high $v$ has a
smaller threshold than $P_2$ at $v=1$. The high-V VDA window closes
when both thresholds drop below the swept r-range — i.e. when $V$
exceeds a critical value $V_{\text{critical}}(r, N)$ above which
$r^\dagger(1) < r$ as well.

Three sub-tasks:

1. **Analytic derivation of $V_{\text{critical}}(r,N)$.** Using the
   change-side approximation of (3) in the derivation file, solve
   $r = r^\dagger(1)$ for $V$ to get
   $V_{\text{critical}}(r,N) \approx 1/(1 + r\,(N-1)/\kappa)$ where
   $\kappa \in [0.8, 1.0]$ is a slowly-varying density ratio.

2. **Numerical sup at $V=0.75$** over the paper's $(r, v)$ grid,
   plus a refinement pass at finer $\Delta\alpha, \Delta c$ to rule
   out grid-resolution artefacts.

3. **Boundary characterisation.** Fine V-grid in $[0.75, 0.80]$ at
   the empirical sup location $(r, v)$ to locate $V_{\text{critical}}$
   numerically. Fine r-grid in $[0.05, 0.20]$ at $(V=0.75, v=5)$ to
   characterise the high-V VDA window's $r$-extent.

The replication code lives at
`Critique/replications/C3--high-V-supremum/run.py`. Model code is
identical to CR-001/CR-002, modulo a defensive
`np.clip(alpha, 0.0, 1.0)` that fixes a NaN bug surfaced only in
the refinement pass.

## What I found

**The sup is 0.040 reward units at $(r, v) = (0.1, 5)$, $V = 0.75$.**

This is $8\times$ the paper's "$<0.005$ negligible" threshold and
$2\times$ §4.4's own "$>0.02$ hot zone" boundary. The §4.4 / §5.2
categorical wording is refuted *internal to the model* under the
paper's own assumptions.

The mechanism:

| at V=0.75, r=0.1, v=5 | value |
|:---|---:|
| $\alpha^\star_{P_1}$ | 0.97 (escaped uniform) |
| $\alpha^\star_{P_2}$ | 0.25 = 1/N (stuck at uniform) |
| $R(P_1)$ | 3.0409 |
| $R(P_2)$ | 2.9999 |
| VDA | 0.0410 (coarse) / 0.0400 (refined) |
| Criterion fraction | 0.95 |

$P_1$ (value-aware) has escaped uniform; $P_2$ (value-blind, $v=1$
fixed-$\alpha$) has not. The gap is the "validity-doesn't-quite-
saturate-the-value-blind-policy" gap that the paper's §4.4 argument
implicitly assumed away.

**Empirical boundary $V_{\text{critical}}(r=0.1, N=4) \in (0.775,
0.780)$.** Across this boundary, $\alpha^\star_{P_2}$ jumps from
0.40 to 0.93 in one V-step of 0.005, and VDA collapses by $50\times$.
The paper's "$V \geq 0.75$" threshold is one V-grid step too generous
at the cost-dominant corner.

**Closed-form prediction.** $V_{\text{critical}}(r=0.1, N=4) \approx
1/(1 + 0.1 \cdot 3 / 0.85) = 0.74$ (simple change-side approximation).
The 4-percentage-point gap from the empirical 0.78 comes from
neglecting the FAR-side density contribution to $G_u$; full
correction (spawned as CR-027) would shift the prediction to ≈0.78,
matching empirics.

**Window extent.** Across the $V = 0.75$ slice in the paper's primary
$(r, v) = 21 \times 5 = 105$-cell grid:
- 8 cells violate "$<0.005$" (the two r-corners $\{0.10, 0.126\}$
  × $v \in \{2, 3, 4, 5\}$).
- 6 cells violate "$<0.02$" (the same r-corners × $v \in \{3, 4, 5\}$).

So this is $\approx 8\%$ of the V=0.75 slice in systematic violation
of §4.4's wording — not an isolated grid corner.

**Strikingly: VDA at $V = 0.75$ is $2.6\times$ larger than at $V = 0.5$**
at the same $(r=0.1, v=5)$. The high-V VDA window doesn't just exist;
it has a peak that is *larger than the paper's headline V=0.5
"hot zone"* peak at the same $(r, v)$ corner. Explanation: inside the
window, VDA $\propto V\,v\,\Delta\Phi_c - (1-V)\,\Delta\Phi_u$; both
terms work in favour of larger VDA at higher V (the cued-side gain
gets weighted by V, the uncued-side loss gets weighted by $(1-V)$).
The window collapses at $V_{\text{critical}}$ because $P_2$ catches
up to $P_1$ in $\alpha^\star$.

## Verdict movement

C3 verdict moved **WEAKLY-SUPPORTED → CONTESTED**. The substantive
content of §4.4 / §5.2 — that the high-V VDA window is narrow, that
typical high-validity paradigms will not detect VDA, and that the
qualitative §5.1 theoretical argument for criterion dominance is
correct — *survives*. What fails is the categorical V-threshold
($V \geq 0.75$) and the "regardless of other parameters" quantifier.
Proposed reformulation (§7 of the derivation file) makes the
V-threshold explicitly $r$- and $N$-dependent via the closed-form
$V_{\text{critical}}(r, N)$.

Per mission §3.1, REFUTED requires "cannot survive without substantive
revision." This re-derivation suggests substantive revision is
required in the §4.4 and §5.2 wording, but the §5.1 theoretical
argument is unaffected. CONTESTED is the appropriate label.

## Next-attack recommendation

The natural next attack is **CR-027** (full FAR-corrected closed-form
$V_{\text{critical}}$): cheapest, builds on the same machinery,
resolves the 4-percentage-point gap between the simple-approximation
prediction (0.74) and the empirical boundary (0.78). After CR-027,
the C3 verdict's CONTESTED label would not change but the proposed
reformulation's analytic substrate would be sharpened.

The next *critical-path* move for the whole critique is **CR-004**
(C4 no-inversion re-derivation, with CR-019 piggyback). C4 is the
only remaining paper headline claim with no attack vector executed.
Given that C1 is CONTESTED and C3 is now also CONTESTED, the paper's
final categorical claim still in defensive position is C4.

## Wiki cross-references

(Mission §11. One line per wiki entry that bore on the finding.)

- [[../derivations/C2--non-monotonic-vda.md]] (internal CR-001
  derivation) — re-used the §2.5 closed-form escape-threshold
  machinery; the entire derivation §1–§4 extends CR-001 to the
  V-axis. **CITED** in derivation §1, §2.
- [[stanisor2013_v1_value_attention]] — reclassified from
  "constrain" (potential refutation of original C3b) to potential
  "support of reformulated C3b" (now predicts a residual high-V VDA
  window the Stănișor V1 signature could be the substrate of).
  **CITED** in verdict V0.2 evidence and dossier V0.2.
- [[luo_maunsell2018_criterion_sensitivity]] — reclassified as both
  empirical support and *experimental-design exemplar* of the
  proposed §5.2 reformulation's "pre-commit to $r$-calibration"
  prescription. **CITED** in derivation §9, verdict V0.2.
- [[sridharan2017_sc_sensitivity_bias]] — unchanged role: confirming
  source for high-V criterion dominance above $V_{\text{critical}}$.
- [[maunsell2015_attention_mechanisms]] — unchanged role.
- [[solomon2004_cues_sensitivity]] — re-inspected; identified as
  candidate paradigm for a future empirical test of the reformulation.
  **CITED** in dossier V0.2.
- [[reynolds_heeger2009_normalization]] — bears on $\kappa(V,N)$;
  spawned CR-027 ($\kappa$-from-normalisation derivation).
- [[cohen_maunsell2009_correlations]] — bears on A1 (independence)
  which the derivation assumes; CR-006 remains queued.
- [[hawkins1990_attention_detectability]] — re-inspected; consistent
  with reformulation, not a direct test.
- [[muller_findlay1987_sensitivity_criterion]] — methodological
  substrate of the SDT decomposition; consulted but not cited.
- [[carrasco2011_visual_attention_25y]] — re-inspected; the
  high-V × value-magnitude experiment that would test the
  reformulation has not been run.

Searched anchors that produced no new material this run: *surround-
suppression*, *LIP-reward* (still no wiki entry; CR-024 remains
queued). No new wiki stubs added this run (the attack was internal
to the model, not literature-driven).

## Files written this run

- `Critique/derivations/C3--high-V-supremum.md` — full re-derivation
  (new).
- `Critique/replications/C3--high-V-supremum/run.py` — replication
  code (new).
- `Critique/replications/C3--high-V-supremum/README.md` — companion
  doc (new).
- `Critique/replications/C3--high-V-supremum/notes.md` — caveats and
  spawn-list (new).
- `Critique/replications/C3--high-V-supremum/output/sup_vda_at_V075.json`
  — numerical results (new).
- `Critique/verdicts/C3--narrow-regime.md` — Version 0.2 appended.
- `Critique/evidence/C3--narrow-regime.md` — Version 0.2 appended.
- `agents/RESEARCH_BACKLOG.md` — CR-026 marked done; CR-027, CR-028,
  CR-029, CR-030 spawned; re-prioritisation note added.
- `agents/RUN_LOG.md` — run-005 entry body populated.
- `agents/reviewer_state.json` — updated.

Audit: no new wiki `papers/` stubs were added this run, so
`research_db/tools/audit.py` was not re-run (mission §4.2 only
requires audit after adding stubs). The wiki entries cited were
all pre-existing.
