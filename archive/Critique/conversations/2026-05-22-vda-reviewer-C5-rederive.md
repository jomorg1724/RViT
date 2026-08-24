---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.2
run_id: run-009
started: 2026-05-22T13:36:23Z
ended:   2026-05-22T13:43:19Z
worked_on: C5
attack_vector: re-derivation
verdict_touched: C5--symmetric-recovery
verdict_after: CONFIRMED-UNDER-ATTACK
papers_read: [reynolds_heeger2009_normalization, luo_maunsell2018_criterion_sensitivity, beck2024_xlstm, mongillo2008_synaptic_wm, buzsaki_wang2012_gamma]
papers_added: []
spawned_tasks: [CR-040, CR-041]
---

# C5 re-derivation: proving the r=1 symmetric recovery (CR-038)

## What I attacked

C5 (mission §2.6; paper **Appendix A**, "Validation: Symmetric Special
Case", and Figure 7, p.8): *"At $r=1$ the model's independent benefit
and cost scaling reduces to a symmetric special case ($\beta=\gamma=1$);
optimal $\alpha^\star$ and $R^\star$ are identical to machine precision
(maximum difference: 0.0) across all 210 matched combinations."* Run-008
had already *reproduced* the "0.0" via replication; this run executed the
designated **second attack vector** (CR-038, re-derivation) to either
falsify the recovery symbolically or promote it to a theorem and elevate
the verdict.

## How I attacked it

Re-derivation. I wrote `Critique/derivations/C5--symmetric-recovery.md`
from the §2.4 equations: (1) a real-number identity showing
$\beta(1)=\gamma(1)=1$ collapses the asymmetric affine map
$d'_{\text{base}}+s\,[x-d'_{\text{base}}]$ to the symmetric transfer
output $x=d'_{\max}f(\cdot)$; (2) a floating-point theorem deriving the
bit-exact "0.0" from three composable facts — $\beta(1),\gamma(1)$ are
the exact float `1.0`, multiply-by-$1.0$ is the IEEE-754 identity, and
**Sterbenz's lemma** ($a/2\le x\le 2a \Rightarrow \mathrm{fl}(x-a)=x-a$)
makes the round-trip $a+(x-a)$ exact whenever the swept sensitivity range
sits in the band $\mathcal B=[d'_{\text{base}}/2, 2d'_{\text{base}}]$;
(3) a scope clause locating where the literal "0.0" fails. I then
verified all float claims in the sandbox with a script independent of
run-008's `run.py`.

## What I found

The derivation goes through cleanly with no skipped step:

- **Theorem 1.** $\beta(1)=\tfrac{2\cdot1}{2}=1$, $\gamma(1)=\tfrac{2}{2}=1$;
  substituting into the asymmetric map gives
  $d'_{\text{base}}+(x-d'_{\text{base}})=x$ exactly. The recovery is a
  genuine real-number identity, so "reduces" is exact, not approximate.
- **Theorem 2.** At the validation config $d'_{\text{base}}=2.0\cdot0.75=1.5$,
  band $\mathcal B=[0.75,3.0]$, and every swept output
  $x=2.0\,f(\cdot)\in[1.0,2.0]\subset\mathcal B$ — so by Sterbenz the
  asymmetric and symmetric code paths are **bit-identical** at every grid
  point. The paper's "0.0" is a *structural guarantee of the config*, the
  mechanism Appendix A asserts but never derives.
- **Scope.** Theorem 2's hypothesis fails when $d'_{\max}f_0 < d'_{\text{base}}/2$,
  i.e. $f_0 < h(1/N)/(1+h(1/N)) = 1/3$ at $N=4,\sqrt{\cdot}$. The
  sandbox probe reproduced run-008's drift table **to the digit**
  (off-band configs lose bit-identity by $\sim$1 ulp:
  $2.78\text{e-}17$, $5.55\text{e-}17$, $1.11\text{e-}16$), independently
  confirming both the threshold and "sufficient-not-necessary".

Independent float checks (this run, not run-008's code):
`β(1)=γ(1)=1.0` hex `0x1.0…p+0`; `np.array_equal(asym_r1, sym)=True`
and `max|Δ|=0.0` over a $10^5$-point $\alpha$ grid on both branches;
`1.0*x==x` on $10^7$ random doubles.

## Verdict movement

**WEAKLY-SUPPORTED → CONFIRMED-UNDER-ATTACK.** C5 now carries two
distinct, independently-failing attack vectors across two runs
(replication run-008, re-derivation run-009), satisfying mission §3.1/§6
for elevation. The vectors are genuinely independent: the replication
fed both maps through the same optimiser (so a shared coding artifact was
conceivable), whereas the symbolic proof derives the identity from the
algebra and IEEE-754 semantics, ruling that out. The label is
CONFIRMED-UNDER-ATTACK rather than -CONDITIONAL because the *headline*
claim — scoped, as the paper writes it, to the 210 combos at the stated
config — is now *proven* exact; the only conditional governs
generalisation to other $(f_0,d'_{\max})$, which the paper never claimed.

## Next-attack recommendation

C5 is closed; no further vector needed. Move to the assumption layer.
The natural continuation is **CR-040** (re-derivation/replication,
A3): the multiplicative constraint $\beta\gamma=1$ also collapses to
$\beta=\gamma=1$ at $r=1$ (since $\beta\gamma=1\wedge\beta+\gamma=2
\Rightarrow\beta=\gamma=1$), so C5 is constraint-agnostic at the centre
— the A3 content is entirely *off* $r=1$, where the two constraints
diverge. CR-040 reuses the run-008 optimiser and lands on the assumption
the paper itself flags in §5.5. Alternative: **CR-036** (A8
heterogeneous-uncued), run-007's standing pick.

## Wiki cross-references

§11 sweep re-run (anchors per §11.1 + claim-specific {Sterbenz,
floating-point, IEEE-754, machine precision, symmetric special case,
β+γ}). C5 is a float/algebra claim, so empirical anchors bear on
C2/C3/C4, not here.

- `reynolds_heeger2009_normalization` — cited in verdict §5.4-interpretation context (gain-modulation = β half of $r$); confirmed present, not a constraint on the numerics.
- `luo_maunsell2018_criterion_sensitivity` — cited as the SDT criterion/sensitivity substrate whose $r=1$ symmetric baseline is recovered.
- `maunsell2015_attention_mechanisms`, `sridharan2017_sc_sensitivity_bias` — noted as §5.4 / SDT substrates; unrelated to the float identity.
- `concepts/coalition_resource_competition.md` — noted; $r=1$ = balanced-coalition point, conceptual hook only.
- `beck2024_xlstm` — read; the lone `papers/` "floating-point" hit, but it is xLSTM log-space overflow stabilization — **unrelated on inspection**.
- `mongillo2008_synaptic_wm`, `buzsaki_wang2012_gamma` — read; the "β/γ" hits are neural *oscillation bands*, not the asymmetry weights — **unrelated on inspection** (false positives, logged for honesty).
- {priority map, LIP, FEF, dopamine, saccade, change detection, Posner} filename scan: `bisley_*`, `posner1980_orienting`, `herman_krauzlis2017_sc_change_detection`, dopamine cluster all present but none bear on a floating-point identity — unrelated on inspection.

No new stub added (attack internal to the model). No floating-point /
numerical-methods literature exists in `research_db/` — an expected,
acceptable gap for this claim type.
