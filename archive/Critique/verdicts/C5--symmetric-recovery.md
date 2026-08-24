---
type: verdict
claim_id: C5
claim_statement: "At r = 1 the independent benefit/cost model reduces exactly to the symmetric special case (β = γ = 1); α* and R* agree to machine precision (max diff 0.0) on 210 matched combinations."
paper_section: "Appendix A (Validation: Symmetric Special Case), Figure 7"
current_label: CONFIRMED-UNDER-ATTACK
attacks_tried:
  - vector: replication
    run_id: run-008
    outcome: "claim reproduced EXACTLY — d' arrays bit-identical, max|Δα*| = max|ΔR*| = 0.0 on all 210 combos; exactness traced to Sterbenz's lemma and shown config-specific; recovery continuous through r=1"
  - vector: re-derivation
    run_id: run-009
    outcome: "claim PROVEN, not merely reproduced — Theorem 1 (β(1)=γ(1)=1 ⇒ asymmetric(r=1) ≡ symmetric as a real-number identity) + Theorem 2 (Sterbenz lemma + band membership [1.0,2.0]⊂[0.75,3.0] ⇒ bit-exact 0.0 on the validation config); literal 0.0 shown config-specific (Sterbenz hypothesis fails for f_0 ≲ h(1/N)/(1+h(1/N)) = 1/3 at N=4,√). Independently float-verified."
load_bearing_for:
  - "Appendix A (the named validation)"
  - "internal consistency of the whole β/γ apparatus — every C1–C4 result at r=1 is the symmetric baseline, so a recovery failure would have impugned the model implementation generally"
  - "§4.1 / Figure 2 reference point at r=1 (the 'symmetric' anchor used to validate the model in CR-002)"
last_updated: 2026-05-22
prompt_version_observed: 0.2
---

# Verdict: r = 1 recovers the symmetric special case (C5)

## Claim as written in the paper

Appendix A ("Validation: Symmetric Special Case", p.8), verbatim:

> At $r = 1$, the model's independent benefit and cost scaling reduces to a symmetric special case ($\beta = \gamma = 1$) where a single shared transfer function governs both benefit and cost. We validated this by comparing the $r = 1$ results against an independent implementation of the symmetric model across all 210 matched parameter combinations ($N = 4$, $d'_{\max} = 2.0$, $f_0 = 0.5$, $\sqrt{\cdot}$ form). Optimal $\alpha^*$ and $R^*$ values are identical to machine precision (maximum difference: 0.0; Figure 7).

Figure 7 caption: *"Validation: the model at $r=1$ exactly recovers the symmetric special case. Left: optimal $\alpha^*$. Right: optimal reward $R^*$(P1). All 210 points fall on the identity line."* (panel annotations: "max diff: 0.0000", "mean: 0.000000").

## Why this matters

C5 is not an empirical claim about attention; it is a **self-consistency / code-correctness** claim about the model implementation. Its load-bearing role is indirect but real: $r = 1$ is the *symmetric anchor* of the entire $\beta(r)/\gamma(r)$ apparatus, and every headline result (C1–C4) passes through $r = 1$ as one of its 21 swept $r$-values. CR-002 used the $r = 1$ cell as one of its two reference points to validate that the independent re-implementation matched the paper's code (CF 0.728 vs 0.73). If $r = 1$ did *not* cleanly recover the symmetric model, that would signal a bug in the $\beta/\gamma$ scaling that would contaminate the whole sweep — so confirming C5 retroactively strengthens confidence in C1–C4's substrate.

The claim also has an interpretive payload via the paper's §5.4 "Biological Interpretation of the Asymmetry Ratio": $r$ is the relative effectiveness of attentional **gain modulation** (β, enhancement at attended locations) versus attentional **suppression / lateral inhibition** (γ, suppression at unattended locations). $r = 1$ is the biologically *balanced* point where the two mechanisms are equally effective — the natural null against which an asymmetry would be measured.

For the PRISM program (§3.5 of mission): C5 itself makes no behavioural prediction (it is a numerical identity), so its direct PRISM implication is limited. The *useful* corollary for PRISM is methodological — see the Implications block at the foot of this version.

---

## Version 0.1 — 2026-05-20

### What this version did

**Replication attack** (one of mission §3.2's four vectors), the first attack on C5 and the first verdict on the only previously-untouched headline claim. Implemented an independent from-equations replication at `Critique/replications/C5--symmetric-recovery/run.py`: the paper's general asymmetric map evaluated at $r = 1$ (call it ★) versus a separately-written symmetric "single shared transfer function" map (☆), both fed through the *same* criterion/$\alpha$ grid optimiser so the only difference is the $d'(\alpha)$ formula. Four blocks: (1) the 210-combo $\max|\Delta\alpha^*|$, $\max|\Delta R^*|$ and bit-identity of the $d'$ arrays; (2) a Sterbenz-lemma mechanism check; (3) an $(f_0, d'_{\max})$ robustness probe of the literal "0.0"; (4) a continuity probe at $r = 1 \pm \{10^{-3}, 10^{-6}\}$.

### Verdict

**WEAKLY-SUPPORTED.** (Mission §3.1: a direct attack failed to falsify the claim, but only one attack vector has been run, so the label cannot be elevated to CONFIRMED-UNDER-ATTACK on this first touch — §6.) The replication reproduces the paper's headline **exactly**, and the run additionally *explains* the exactness rather than merely observing it:

1. **The number is reproduced exactly, not merely to machine epsilon.** Across all 210 combinations ($V \in \{$21 pts in $[1/N,1]\}$, $v \in \{1..5\}$, variant $\in \{A,B\}$ at $r=1$, $N=4$, $d'_{\max}=2.0$, $f_0=0.5$, $\sqrt{\cdot}$): the cued and uncued $d'$ arrays are **bit-identical** (`np.array_equal` True), and consequently $\max|\Delta\alpha^*| = 0.0$ and $\max|\Delta R^*| = 0.0$. This matches the paper's "maximum difference: 0.0" precisely.

2. **Why exact — Sterbenz's lemma (mechanism the paper does not state).** $\beta(1) = 2{\cdot}1/(1{+}1) = 1$ and $\gamma(1) = 2/(1{+}1) = 1$ are *exactly* representable in IEEE-754 binary64. The asymmetric map at $r=1$ then computes $a + (x - a)$ with $a = d'_{\text{base}}$ and $x = d'_{\max} f(\cdot)$, whereas the symmetric map computes $x$ directly. Sterbenz: if $a/2 \le x \le 2a$ then $\mathrm{fl}(x-a) = x-a$ exactly, hence $\mathrm{fl}(a + (x-a)) = x$ bit-for-bit. At the validation config $a = d'_{\text{base}} = 2.0\,(0.5 + 0.5\sqrt{0.25}) = 1.5$, and every swept $x \in [1.0, 2.0] \subset [0.75, 3.0] = [a/2, 2a]$. So the round trip is exact at *every* grid point — the "0.0" is a **structural guarantee of the chosen config**, not a lucky rounding.

3. **The literal "0.0" is config-specific; "machine precision" is universal.** Block 3 varied $(f_0, d'_{\max})$: configs whose swept $x$ leaves the Sterbenz band (low $f_0$ relative to $d'_{\text{base}}$, e.g. $f_0 = 0.1$) lose bit-identity, drifting by $\sim 1$ ulp ($10^{-17}$ to $10^{-16}$). 4 of 15 probed configs were no longer bit-exact. Band membership is *sufficient* but not *necessary* (e.g. $d'_{\max}=2, f_0=0.3$ sits just outside the band yet is still bit-exact). Consequence: C5 as written — scoped to the 210 combos at the stated config — is **exactly correct**; but a reader should not generalise "max diff 0.0" to arbitrary $(f_0, d'_{\max})$, where the honest statement is "identical to machine precision" ($\le \sim 1$ ulp on $d'$, which the grid argmax rounds away to $0$ for $\alpha^*$ and to $\sim 10^{-16}$ for $R^*$).

4. **$r = 1$ is the smooth limit, not a knife-edge.** Block 4: $\max|\Delta R^*|$ vs the symmetric model is $8.4\times10^{-5}$ at $r = 1\pm10^{-3}$, $8.4\times10^{-8}$ at $r = 1\pm10^{-6}$, and exactly $0$ at $r = 1$ — linear in $|r-1|$ with slope $\approx 0.084$ reward units, vanishing at $r=1$. $\alpha^*$ does not move over $r = 1\pm10^{-3}$ (perturbation below the $\Delta\alpha = 0.005$ grid). The symmetric special case is the genuine, smooth centre of the asymmetric family — confirming the word "reduces" is apt, not a removable singularity.

The claim survives the replication vector intact; the only refinement (the config-specificity of the literal "0.0") sharpens rather than contests the paper, since the paper explicitly scoped its number to the validation config.

### Evidence

- Replication: `Critique/replications/C5--symmetric-recovery/run.py`; outputs `output/results.json`, `output/run.log`; analysis in `README.md` and `notes.md`. Reproduces max diff 0.0 on 210 combos; Sterbenz band check; $(f_0,d'_{\max})$ robustness table; $r\to1$ continuity table.
- Cross-validation with prior runs: the $r=1$ cell is the same reference point CR-002 used to validate its re-implementation against the paper (`Critique/replications/C1--criterion-fraction-floor`), so the bit-exact symmetric recovery and the CR-002 CF-match are mutually corroborating.
- Algebraic basis: $\beta(r)=2r/(r{+}1)$, $\gamma(r)=2/(r{+}1)$ give $\beta(1)=\gamma(1)=1$ (mission §2.4); the CR-002 / CR-004 derivations already note that the $d'(\alpha)$ kink at $\alpha=1/N$ vanishes iff $\beta=\gamma$, i.e. $r=1$ (`Critique/derivations/C4--no-inversion.md` §1).

### Loose ends

1. **Second attack vector for elevation.** To reach CONFIRMED-UNDER-ATTACK, C5 needs one more distinct vector. The natural one is a short **re-derivation** that formalises the $\beta(1)=\gamma(1)=1 \Rightarrow$ (★)$\equiv$(☆) identity symbolically and states the Sterbenz sufficient-condition as a lemma (so the "0.0" is a proven property, not just a measured one). Spawned as **CR-038**.
2. **Config-specificity note for the owner.** The paper's "maximum difference: 0.0" is exact at its config but not universal; an editor-facing one-line caveat ("0.0 at the validation config; machine-precision-but-nonzero off it") may be worth surfacing. Spawned as **CR-039** (documentation note, low).
3. **Substrate reuse.** This run built the symmetric+asymmetric P1 optimiser the A3 ($\beta\cdot\gamma=1$ alternative constraint) and A5 (alternative $h$ forms) sweeps will reuse. At $r=1$ the $\beta\gamma=1$ constraint *also* gives $\beta=\gamma=1$, so it recovers the same symmetric point; its off-$r{=}1$ divergence is the actual A3 question and is out of scope here. Noted for CR-009 (A3 seed).

### Implications for PRISM v1/v2 (§3.5)

C5 is a numerical identity, so it makes no direct behavioural prediction for PRISM. Two indirect, useful corollaries:

- **Methodological / validation.** The clean $r=1$ recovery is a template for a *unit test* on any PRISM-side normative-model code: the symmetric baseline should be bit-recoverable from the asymmetric implementation, and a non-zero diff at $r=1$ would flag a $\beta/\gamma$ bug. The Sterbenz analysis warns that "expected exactly 0.0" is only safe when the sensitivity range stays within a factor of 2 of the baseline $d'_{\text{base}}$ — relevant if PRISM analyses adopt very low floor sensitivities ($f_0 \to 0$), where exact-0 self-checks would spuriously fail at the ulp level.
- **Interpretive.** $r=1$ is the gain-modulation = suppression balance point (paper §5.4). A PRISM agent whose trained attention trajectories (`Prism/figures/avg_alpha_*.pdf`) imply *symmetric* benefit/cost would sit at this null; the paper's more interesting C2/C3 predictions (peak VDA at $r\approx 0.3$, cost-dominant) live *away* from $r=1$, so PRISM evidence for asymmetry is what would make the VDA story bite. C5 just fixes where the null is.

### Wiki cross-references

Mechanism-keyword sweep per mission §11.1 (anchors: value-directed attention, reward-modulated attention, attentional capture, selection history, criterion shift, signal detection theory, d-prime, normalization model, gain modulation, surround suppression, priority map, LIP, FEF, V4, parietal, frontal eye field, biased competition, dopamine, RPE, basal ganglia, oculomotor, saccade, change detection, Posner cueing, cue validity). C5 is a numerical-identity claim, so most empirical anchors are unrelated *to this claim* (they bear on C2/C3/C4); the genuinely connected entries are the gain/suppression and SDT-decomposition substrates that give $r$ its biological reading.

- `reynolds_heeger2009_normalization` — **cited** (paper ref [12]); the normalization model is the substrate for the β (gain-modulation) half of $r$; $r=1$ is the gain=suppression balance. Bears on §5.4 interpretation, not on the numerical claim.
- `luo_maunsell2018_criterion_sensitivity` — **cited** (paper ref [4]); the criterion-vs-sensitivity dissociation the P1–P4 decomposition operationalises; relevant as the SDT substrate whose r=1 symmetric baseline is being validated.
- `maunsell2015_attention_mechanisms` — cited loosely; review-level synthesis of gain vs criterion mechanisms underpinning the §5.4 reading of $r$.
- `sridharan2017_sc_sensitivity_bias` — noted; SDT decomposition substrate (sensitivity vs bias), same circularity caveat flagged in the C1/C3 verdicts; unrelated to the numerical identity.
- `concepts/coalition_resource_competition.md` — **cited** (user concept); the paper's $\beta+\gamma=2$ conservation is a zero-sum reallocation, and $r=1$ is the balanced-coalition point — a conceptual hook into the user's competition thesis, not a constraint on C5.
- `concepts/competition_emergent_predictive_coding.md` — inspected; the user's central thesis; related at the conceptual level (balanced competition) but does not bear on the recovery claim. Noted, not cited.
- `threads/the_user_architectural_program.md` — inspected for the §3.5 PRISM block; referenced for the avg_alpha trajectory artifacts.
- `failing_theeuwes2018_selection_history`, `hickey2010_reward_salience_acc`, `anderson*`, `wang_theeuwes2018_statistical_learning_distractor_suppression`, `stanisor2013_v1_value_attention` — **unrelated on inspection** for C5: these are value/capture/suppression empirical papers that bear on C2/C3/C4, not on the $r=1$ algebraic reduction.
- Searched anchors {priority map, LIP, FEF, parietal, dopamine, RPE, basal ganglia, oculomotor, saccade, Posner cueing, change detection} against `papers/`, `concepts/`, `threads/`: hits exist (`bisley_*`, `posner1980_orienting`, `herman_*`) but none bear on a floating-point / algebraic-identity claim — unrelated on inspection.

No new wiki stub was added this run (the attack is internal to the model; no external paper was needed).

### Next-attack recommendation

**CR-038 — re-derivation**, the cheap second vector: symbolically show $\beta(1)=\gamma(1)=1 \Rightarrow$ asymmetric$(r{=}1)\equiv$symmetric as a real-number identity, and state the Sterbenz sufficient condition $[d'_{\text{base}}/2, 2d'_{\text{base}}] \supseteq \{d'_{\max} f(\cdot)\}$ as the lemma guaranteeing bit-exactness. If it goes through (it will), C5 elevates to CONFIRMED-UNDER-ATTACK. This closes C5 with two vectors and frees the queue for the assumption layer (A1–A8), which is now the critique's frontier.

---

## Version 0.2 — 2026-05-22

### What this version did

**Re-derivation attack** (mission §3.2), the designated second vector (CR-038), executed in run-009. Produced `Critique/derivations/C5--symmetric-recovery.md`: a from-the-equations symbolic proof of the recovery, plus an independent float-arithmetic verification that does **not** reuse run-008's `run.py`. The derivation has two theorems and a scope clause:

- **Theorem 1 (real-number identity).** $\beta(1)=\tfrac{2\cdot1}{1+1}=1$ and $\gamma(1)=\tfrac{2}{1+1}=1$, so the asymmetric map $d'_{\text{base}} + s\,[x-d'_{\text{base}}]$ has unit slope at $r=1$ and collapses to $x = d'_{\max}f(\cdot)$ — exactly the symmetric "single shared transfer function". The cancellation $d'_{\text{base}}-d'_{\text{base}}=0$ is the whole content of the word "reduces". Because the downstream SDT/reward/optimiser stack is a deterministic function of the $d'$ arrays alone, identical arrays force identical $(\alpha^\star,c^\star,R^\star)$.
- **Theorem 2 (bit-exact 0.0 via Sterbenz).** The asymmetric code path at $r=1$ computes $\mathrm{fl}(a+\mathrm{fl}(1.0\cdot\mathrm{fl}(x-a)))$ with $a=d'_{\text{base}}$. Three facts compose: $\beta(1),\gamma(1)$ are the exact float `1.0` (hex `0x1.0…p+0`); multiply-by-$1.0$ is the IEEE-754 identity ($10^7$ random-double check passed); and **Sterbenz's lemma** — $a/2\le x\le 2a \Rightarrow \mathrm{fl}(x-a)=x-a$ exactly. At the validation config $a=d'_{\text{base}}=1.5$, $\mathcal B=[0.75,3.0]$, and every swept output $x=2.0\,f(\cdot)\in[1.0,2.0]\subset\mathcal B$, so the round-trip returns $x$ bit-for-bit. The paper's "max diff 0.0" is therefore a **structural guarantee of the chosen config**, supplying the mechanism Appendix A asserts but never derives.
- **Scope clause.** Theorem 2's hypothesis is *sufficient, not necessary*, and fails when the smallest output $d'_{\max}f_0$ drops below $d'_{\text{base}}/2$, i.e. $f_0 < h(1/N)/(1+h(1/N))$ ($=1/3$ for $h=\sqrt{\cdot}, N=4$). The §5 P3 probe reproduces run-008's drift table exactly (off-band configs lose bit-identity by $\sim$1 ulp: $2.78\text{e-}17$, $5.55\text{e-}17$, $1.11\text{e-}16$), independently confirming it.

### Verdict

**WEAKLY-SUPPORTED → CONFIRMED-UNDER-ATTACK.** *Cause of the change:* a second, methodologically distinct attack vector (re-derivation) has now joined the run-008 replication, and it failed to falsify the claim — it strengthened it from a *measured* identity to a *proven* one. Per mission §3.1/§6, elevation to CONFIRMED-UNDER-ATTACK requires $\ge 2$ distinct attack vectors across separate runs with no weakening; C5 now has replication (run-008) and re-derivation (run-009), both confirming. The two vectors are genuinely independent: the replication could in principle have reproduced a *shared* coding pattern (both maps fed the same optimiser), whereas the symbolic proof rules out any such artifact by deriving the identity from the algebra of (2)–(6) and the IEEE-754 semantics — a different failure surface. The only residual nuance (the literal "0.0" is config-specific) is a *sharpening*, not a weakening: the paper scoped its number to the validation config, where it is now *proven* exact.

This is the strongest available label for C5: it is **not** CONFIRMED-CONDITIONAL, because the *headline* claim (scoped to the 210 matched combos at the stated config, as the paper writes it) holds without conditional — the conditional only governs the *generalisation* to other $(f_0,d'_{\max})$, which the paper did not claim.

### Evidence

- Re-derivation: `Critique/derivations/C5--symmetric-recovery.md` — Theorems 1–2, the band-membership computation $[1.0,2.0]\subset[0.75,3.0]$, the off-band threshold $f_0<1/3$, and the §5 verification script + output.
- Independent float check (run-009, sandbox): `β(1)=γ(1)=1.0` bit-exact; `np.array_equal(asym_r1, sym)=True`, `max|Δ|=0.0` over a $10^5$-point $\alpha$ grid on both branches; `1.0*x==x` on $10^7$ random doubles; off-band table matching run-008 to the digit.
- Standard references for the float lemma: Sterbenz (1974) *Floating-Point Computation*; Goldberg (1991) "What Every Computer Scientist Should Know About Floating-Point Arithmetic," *ACM Comput. Surv.* 23(1).
- Corroboration with prior derivations: `Critique/derivations/C4--no-inversion.md` §1 (the $\beta/\gamma$ kink-slope ratio $=r$, vanishing at $r=1$) is the same identity viewed locally.
- Paper: Appendix A and Figure 7 (`Critique/source/main.pdf`, p.8), confirmed verbatim by direct read this run (annotations "max diff: 0.0000", "mean: 0.000000").

### Loose ends

1. **CR-039 / owner-facing wording note (addressed here; promoted to CR-041).** The manuscript's Appendix-A "maximum difference: 0.0" is *proven exact* at the validation config ($N=4,d'_{\max}=2.0,f_0=0.5,\sqrt{\cdot}$) but is **not** universal: off the Sterbenz band (notably $f_0\lesssim1/3$) the recovery is exact only to machine precision ($\le 1$ ulp on $d'$). Recommended manuscript fix — either (a) keep "0.0" but scope it explicitly to the validation config, or (b) report the general statement as "identical to machine precision ($\le 1$ ulp)". This is the substance of CR-039; since the derivation now states the precise threshold $f_0<h(1/N)/(1+h(1/N))$, CR-039 is **absorbed** and re-homed as **CR-041** (a one-line manuscript-clarity flag) so the owner has a single actionable note.
2. **A3 divergence off $r=1$ (the real next question).** At $r=1$ the alternative multiplicative constraint $\beta\gamma=1$ *also* gives $\beta=\gamma=1$ (since $\beta\gamma=1$ and $\beta+\gamma=2 \Rightarrow \beta=\gamma=1$), so it recovers the **same** symmetric point — C5 is constraint-agnostic at $r=1$. The interesting A3 content is entirely *off* $r=1$, where $\beta+\gamma=2$ and $\beta\gamma=1$ diverge. Spawned as **CR-040** (re-derivation/replication of the $\beta\gamma=1$ family off $r=1$, reusing the run-008 optimiser substrate). This is the natural bridge from the now-closed C5 into the assumption layer (A3).
3. **No second-vector debt remains on C5.** With two confirming vectors, C5 needs no further attack to hold its label; future touches would only be to *contest* it (none anticipated) or to fold its substrate into A3/A5/A6 sweeps.

### Implications for PRISM v1/v2 (§3.5)

Unchanged from v0.1 in substance (C5 is a numerical identity, so no direct behavioural prediction), but the re-derivation sharpens the **methodological** corollary: the Sterbenz threshold $f_0 < h(1/N)/(1+h(1/N))$ now gives PRISM-side normative-model code an *exact* rule for when an "expected 0.0" self-check is safe. If PRISM analyses adopt low floor sensitivities ($f_0\to 0$, e.g. degraded-periphery regimes), an exact-zero symmetric-recovery unit test would spuriously fail at the ulp level; the correct assertion there is `allclose(atol=1e-15)`, not `array_equal`. The interpretive point also stands: $r=1$ is the gain=suppression balance (paper §5.4), the null away from which the C2/C3 VDA story lives, so PRISM evidence of $\beta\ne\gamma$ in trained `avg_alpha_*` trajectories is what would make the asymmetry bite.

### Wiki cross-references

Mechanism-keyword sweep per mission §11.1 re-run this version (anchors: value-directed attention, reward-modulated attention, attentional capture, selection history, criterion shift, signal detection theory, d-prime, normalization model, gain modulation, surround suppression, priority map, LIP, FEF, V4, parietal, frontal eye field, biased competition, dopamine, RPE, basal ganglia, oculomotor, saccade, change detection, Posner cueing, cue validity) plus claim-specific terms {Sterbenz, floating-point, IEEE-754, machine precision, symmetric special case, additive conservation, β+γ}. C5 is a floating-point/algebraic-identity claim, so — as in v0.1 — the empirical anchors bear on C2/C3/C4, not on this claim.

- `reynolds_heeger2009_normalization` — **cited** (paper ref [12]); normalization is the substrate for the β (gain-modulation) half of $r$; $r=1$ is the gain=suppression balance. Bears on the §5.4 interpretation that gives the *meaning* of the point being validated, not on the numerics.
- `luo_maunsell2018_criterion_sensitivity` — **cited** (paper ref [4]); the criterion-vs-sensitivity dissociation the P1–P4 decomposition operationalises; the SDT substrate whose $r=1$ symmetric baseline is being recovered.
- `maunsell2015_attention_mechanisms` — noted; review-level gain-vs-criterion synthesis underpinning the §5.4 reading of $r$. Unchanged from v0.1.
- `sridharan2017_sc_sensitivity_bias` — noted; SDT decomposition substrate; unrelated to the float identity (same circularity caveat as C1/C3).
- `concepts/coalition_resource_competition.md` — noted (user concept); $\beta+\gamma=2$ is a zero-sum reallocation and $r=1$ the balanced-coalition point — conceptual hook, not a constraint on C5.
- `beck2024_xlstm` — **unrelated on inspection** (the lone "floating-point" hit in `papers/`): refers to log-space *overflow* stabilization in xLSTM exponential gating, nothing to do with Sterbenz or the recovery.
- `mongillo2008_synaptic_wm`, `buzsaki_wang2012_gamma` — **unrelated on inspection** (the "β/γ" filename/text hits): refer to *beta/gamma oscillation bands*, not the asymmetry weights $\beta(r),\gamma(r)$ — false positives of the keyword sweep, logged for honesty.
- Searched {priority map, LIP, FEF, parietal, dopamine, RPE, basal ganglia, oculomotor, saccade, Posner cueing, change detection}: hits exist (`bisley_goldberg2010_parietal_priority`, `bisley_mirpour2019_priority_map`, `posner1980_orienting`, `herman_krauzlis2017_sc_change_detection`, the dopamine cluster) but none bear on a floating-point / algebraic-identity claim — unrelated on inspection, consistent with v0.1.

No new wiki stub added this run (re-derivation is internal to the model; no external paper needed). No floating-point / numerical-methods literature exists in `research_db/` — an expected gap for this kind of claim, and not one worth filling with a stub.

### Next-attack recommendation

C5 is closed at CONFIRMED-UNDER-ATTACK and needs no further vector. The substantive frontier is the **assumption layer (A1–A8)**, all OPEN except A8 (ratified, untouched). Two unblocked picks:

- **CR-040** (re-derivation/replication) — the $\beta\gamma=1$ alternative-constraint (A3) *off* $r=1$, the direct descendant of this run's Loose-end #2. It reuses the run-008 symmetric+asymmetric optimiser and attacks the only assumption the paper itself flags in §5.5 as "could yield quantitatively different results."
- **CR-036** (replication) — the A8 heterogeneous-uncued allocation, run-007's standing recommendation, now de-risked by the run-008 substrate.

CR-040 is the recommended next pick: it is the natural continuation of the C5 thread (same $\beta/\gamma$ apparatus, same substrate) and lands on a paper-acknowledged assumption, making it high-information for low setup cost.
