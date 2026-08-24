---
type: verdict
claim_id: C3
claim_statement: "VDA is confined to a narrow regime: low cue validity (V near 1/N), high value contrast (v ≫ 1), moderate benefit/cost asymmetry (r ∈ [0.2, 1.0]). §5.2 strengthens this to a categorical experimental-design prediction: 'Standard spatial cueing paradigms with high validity (V ≥ 0.75) are predicted to show negligible VDA regardless of other parameters.'"
paper_section: "§4.4 (Fig. 5 strategy landscape; 'Regime where VDA matters' subsection) and §5.2 (Implications for Experimental Design)"
current_label: CONTESTED
attacks_tried:
  - vector: literature
    run_id: run-004
    outcome: |
      Wiki sweep + one targeted PubMed fetch. C3a (low-V end) confirmed
      by value-driven-attentional-capture literature (Failing & Theeuwes
      2018; Hickey 2010). C3b (high-V end) supported by the SDT-aligned
      macaque tradition (Luo & Maunsell 2018; Maunsell 2015; Sridharan
      2017) but with a circularity caveat (designs assume the
      decomposition); constrained by Stănișor et al. 2013 PNAS, which
      finds V1 single-unit modulation by relative reward value at high V
      with attention-like latency and per-cell value/attention
      covariation. Stănișor's behavioural-d′ implication is not in the
      abstract and requires a full-depth read to adjudicate.
  - vector: re-derivation
    run_id: run-005
    outcome: |
      Re-derivation + numerical sup at the paper's reference regime
      (N=4, d'_max=2, f_0=0.5, h=sqrt, Variant A, V=0.75). sup_{r,v}
      VDA = 0.040 reward units at (r=0.10, v=5) — 8× the paper's 0.005
      "negligible" threshold and 2× §4.4's own 0.02 "hot zone"
      boundary. Closed-form V_critical(r,N) = 1/(1 + r(N-1)/κ)
      derived; empirical boundary V_critical(r=0.1, N=4) ∈ (0.775,
      0.780) — paper's "V≥0.75" threshold is one V-grid step too
      generous. C3b REFUTED internal to the model. Proposed §4.4/§5.2
      reformulation drafted (Version 0.2 §7 below) that preserves the
      paper's scientific point while making the V-threshold explicitly
      r-dependent.
load_bearing_for:
  - "§4.4 'Regime Where VDA Matters' — the headline experimental-regime characterisation"
  - "§5.2 'Implications for Experimental Design' — the categorical advice to experimenters"
  - "§5.3 'Implications for Computational Models' — the recommendation that high-validity tasks favour criterion-routing architectures (this is the bridge into the PRISM relevance)"
  - "Conclusion §6 — 'narrow niche in the normative landscape'"
last_updated: 2026-05-17
prompt_version_observed: 0.1
---

# Verdict: VDA is confined to a narrow regime (C3)

## Claim as written in the paper

From §4.4 ("The Regime Where VDA Matters"), the qualitative
characterisation of the regime:

> "This identifies a clear recipe for the regime where VDA matters: low
> cue validity (so validity alone does not saturate attention), high
> value contrast ($v \gg 1$), moderate or cost-dominant benefit/cost
> asymmetry (so the value-blind policy is suboptimal), and, as the
> secondary sweeps confirm, low baseline sensitivity $f_0$ (so attention
> is perceptually consequential)."

From §5.2 ("Implications for Experimental Design"), the strongest /
testable version of the regime claim — the one this verdict
interrogates:

> "When VDA should not be expected. Standard spatial cueing paradigms
> with high validity ($V \geq 0.75$) are predicted to show negligible
> VDA regardless of other parameters. In these regimes, the validity
> gradient alone drives attention to ceiling, and any observed
> value-related performance differences are more parsimoniously
> attributed to criterion adjustment. Experimenters should not
> interpret the absence of VDA in high-validity paradigms as evidence
> against value-driven attentional mechanisms — the normative model
> predicts that VDA is simply not needed in this regime."

The §5.2 wording is more categorical and more falsifiable than the
§4.4 wording: it commits to a *quantitative* threshold (V ≥ 0.75),
quantifies the predicted VDA at that threshold (*negligible*), and
asserts the prediction holds *regardless of other parameters*. This
verdict treats §5.2 as the operational version of C3.

## Why this matters

C3 is the paper's principal *positive contribution to experimental
design*. C1 (criterion-fraction range; now CONTESTED per
`C1--criterion-fraction-floor.md`) and C2 (non-monotonic VDA in r; now
CONFIRMED-UNDER-ATTACK per `C2--non-monotonic-vda.md`) are *findings
about the model itself*; C3 is the model's *prescription for primate
and human experimentation*. If C3b is wrong — if VDA at V ≥ 0.75 is
not negligible across all parameters — the §5.2 advice that
experimenters should accept the absence of high-V VDA as consistent
with the normative model is invalidated, and a substantial part of
the paper's claim to experimental-design relevance falls.

For the user's PRISM v1 / v2 program (see `Prism/docs/THESIS.md` §3;
`PrismV2/`), C3 specifically predicts that in high-V Posner-style
change-detection — exactly the paradigm class PRISM is trained on
(`Prism/env.py`) — *value-directed attention reallocation should not
emerge in trained policies*. If C3b stands, this is a *positive
prediction* for PRISM: a trained agent's attention pattern at
V ≥ 0.75 should be driven by validity, and reward differentials
should manifest as bias-like (choice-side) shifts rather than as
attention-allocation shifts. If C3b falls (e.g., via the Stănișor
2013 V1-reward channel surviving a behavioural-d′ probe), then PRISM
agents that are still emerging value-driven attention shifts at high V
are *consistent with biology* rather than diverging from the
normative model.

## Version 0.1 — 2026-05-17

### What this version did

Executed a literature attack on C3 (mission §3.2) by (i) wiki sweep
per §11.1 anchors against `research_db/`, (ii) one targeted PubMed
fetch to fill a gap the wiki was silent on. The full evidence
breakdown is in `Critique/evidence/C3--narrow-regime.md`. Only one
attack vector was run; per mission §3.1 the verdict cannot elevate
beyond WEAKLY-SUPPORTED without a second distinct attack vector.

The attack decomposed §5.2's wording into two testable sub-statements
and evaluated each separately against the wiki literature:

- **C3a:** VDA is robustly observed in the *low-V* regime (V near
  1/N).
- **C3b:** VDA is *negligible* in the *high-V* regime (V ≥ 0.75)
  *regardless of other parameters*.

### Verdict

**Label: WEAKLY-SUPPORTED.**

- **C3a is confirmed by the value-driven-attentional-capture
  literature** (Anderson 2011 paradigm; reviewed in
  [[failing_theeuwes2018_selection_history]] and operationalised in
  [[hickey2010_reward_salience_acc]]). Both operate at V = 1/N (the
  rewarded feature is uninformative or even counter-strategic with
  respect to location), and both find reliable RT slowing of
  ≈10–60 ms, N2pc enhancement, ERP and oculomotor signatures of
  value-driven attentional biasing. Effects persist for ≥6 months
  after the reward-pairing phase.

- **C3b is consistent with the SDT-aligned macaque tradition**:
  [[luo_maunsell2018_criterion_sensitivity]] explicitly demonstrates
  that, in a high-V cued change-detection task, *reward asymmetry
  loads on criterion (β) and not on sensitivity (d′)*; the
  sensitivity manipulation in the same study is delivered by
  physical stimulus changes (contrast, size), not by reward.
  [[sridharan2017_sc_sensitivity_bias]] re-analyses four published
  SC manipulation studies (all at high V) and finds SC contributes
  primarily to choice bias, not to sensitivity.
  [[maunsell2015_attention_mechanisms]] supplies the review-level
  synthesis: V4 / IT firing-rate modulations correlate with d′;
  criterion changes correlate with LPFC and subcortical activity.
  [[carrasco2011_visual_attention_25y]] confirms that the standard
  high-V psychophysics literature has not run the value-magnitude
  manipulation that would constitute a direct test.

- **C3b is *constrained* by [[stanisor2013_v1_value_attention]]**
  (new stub this run; abstract-depth read of PNAS PMID 23676276,
  [DOI](https://doi.org/10.1073/pnas.1300117110)). In a macaque
  curve-tracing task at high effective V with varied reward
  magnitude across stimuli, *V1 single-unit activity is
  significantly predicted by the relative reward value of stimuli*,
  with attention-like latency and per-cell covariation between
  value and attention effects. The authors conclude that "relative
  value and top-down attention engage overlapping, if not identical,
  neuronal selection mechanisms." This is *prima facie* in tension
  with §5.2's "negligible VDA regardless of other parameters." The
  tension is **not yet a refutation** because the V1 single-unit
  effect could, in principle, be the substrate of a criterion-side
  decision-readout effect rather than a true sensitivity gain that
  contributes to behavioural d′. Disambiguating this requires a
  full-depth read of the Stănișor paper (spawned as CR-023) or an
  independent SDT-aware experiment.

- **Circularity caveat.** The principal high-V support for C3b
  (Luo-Maunsell 2018; Maunsell 2015; Sridharan 2017) comes from
  experiments whose *design* already factors out reward effects on
  sensitivity by using reward asymmetry specifically to induce
  criterion shifts. The paper's normative model formalises a
  decomposition the macaque-physiology canon has been built around;
  finding the literature consistent with the decomposition is
  weaker evidence than it appears, because the literature inherited
  the decomposition.

- **Proposed weaker reformulation that the wiki evidence
  unambiguously supports** (drafted here for owner review):
  > "Standard spatial cueing paradigms with high validity
  > (V ≥ 0.75) in which reward magnitude is manipulated to *induce
  > criterion shifts* are predicted to show negligible
  > *attention-reallocation-side* VDA on behavioural d′. The
  > normative model does not preclude reward-driven modulation of
  > early visual cortex at high V (e.g., the Stănișor et al. 2013
  > V1 signature), but interprets such modulation as the neural
  > correlate of criterion-side decision routing rather than as
  > evidence of attentional reallocation that improves d′."
  >
  > "Experimenters should not interpret the absence of *d′-side*
  > VDA in high-validity paradigms as evidence against value-driven
  > attentional mechanisms; conversely, observing reward
  > modulation of early visual cortex at high validity is not by
  > itself evidence that the criterion-only account is wrong, as
  > the same priority-map / gain-modulation substrate can carry a
  > criterion-aligned signal."

### Evidence

Full source-by-source breakdown:
[`Critique/evidence/C3--narrow-regime.md`](../evidence/C3--narrow-regime.md).

Direct citations from this version:
- [[failing_theeuwes2018_selection_history]] — C3a confirmation,
  low-V value-driven attentional capture.
- [[hickey2010_reward_salience_acc]] — C3a confirmation,
  trial-to-trial reward at V = 1/N.
- [[luo_maunsell2018_criterion_sensitivity]] — C3b support,
  high-V cueing with reward-asymmetry-induced criterion shifts.
- [[maunsell2015_attention_mechanisms]] — review-level
  sensitivity/criterion decomposition consistent with C3b.
- [[sridharan2017_sc_sensitivity_bias]] — SC contributes
  bias-not-sensitivity at high V (cross-substrate support for
  C3b).
- [[stanisor2013_v1_value_attention]] — *new this run.* V1
  reward modulation at high V; the principal constraint on C3b.
- [[posner1980_orienting]] — validity-saturation baseline that
  C3b inherits.
- [[cameron2002_covert_attention_contrast]] — high-V attention
  effects exist and are sensitivity-side, but V-driven not
  v-driven (so consistent with C3b).
- [[carrasco2011_visual_attention_25y]] — synthesis confirming
  that the standard high-V psychophysics literature has not run
  the high-V × value-magnitude experiment.
- [[srinath2021_attention_information_flow]] — high-V attention
  effects on cross-area communication (validity-driven, not
  value-driven; consistent with C3 but not a direct test).
- [[monosov2020_outcome_uncertainty]] — uncertainty-axis
  theoretical framing in which C3's V-dependence is natural.

### Wiki cross-references

(Mission §11. One line per consulted entry, plus the
unconsulted-but-anchor entries.)

- [[failing_theeuwes2018_selection_history]] — cited as primary
  C3a anchor.
- [[hickey2010_reward_salience_acc]] — cited as primary C3a anchor
  (trial-to-trial version of the Anderson 2011 paradigm).
- [[luo_maunsell2018_criterion_sensitivity]] — cited as primary
  C3b anchor; circularity caveat recorded.
- [[maunsell2015_attention_mechanisms]] — cited as the
  review-level synthesis underlying the SDT decomposition.
- [[sridharan2017_sc_sensitivity_bias]] — cited as cross-substrate
  support for C3b (SC bias-side contribution at high V).
- [[posner1980_orienting]] — cited as the validity-saturation
  baseline.
- [[cameron2002_covert_attention_contrast]] — cited to make the
  V-driven-vs-v-driven distinction explicit.
- [[carrasco2011_visual_attention_25y]] — cited as the absence-of-
  evidence acknowledgement for high-V × value-magnitude.
- [[srinath2021_attention_information_flow]] — cited as high-V
  attention-effect existence proof (validity-driven).
- [[bhatnagar2022_attention_choice_metaanalysis]] — consulted;
  unrelated on inspection to the C3 question (preferential
  choice, not perceptual change-detection); logged in dossier
  but not cited in verdict body.
- [[baluch_itti2011_topdown_mechanisms]] — consulted; flags
  reward as an emerging fifth top-down channel but predates the
  empirical material; cited only in dossier framing.
- [[monosov2020_outcome_uncertainty]] — cited as the
  uncertainty-axis theoretical framing under which the paper's
  V-dependence prediction is natural.
- [[herman_krauzlis2017_sc_change_detection]] — cited in the
  Implications-for-PRISM block; high-V SC paradigm precursor.
- [[herman_arcizet2020_caudate_sc]] — cited in the
  Implications-for-PRISM block; SC → CDh cascade.
- [[stanisor2013_v1_value_attention]] — *new stub added this
  run.* Cited as the principal current candidate-refutation of
  §5.2, with the caveat that abstract-depth reading leaves the
  behavioural-d′ question open.
- [[reynolds_heeger2009_normalization]] — anchor for the
  divisive-normalization substrate of all the gain-modulation
  results; consulted indirectly via downstream citers; no
  unique contribution to C3 beyond what's already in the
  Maunsell 2015 / Carrasco 2011 syntheses.
- [[mcadams_maunsell1999_reliability]] — V4 attentional gain
  reliability anchor; consulted indirectly; not cited
  separately.
- [[cohen_maunsell2009_correlations]] — noise-correlation
  reduction with attention; consulted indirectly; not cited
  separately.
- [[desimone_duncan1995_biased_competition]] — biased-competition
  framework underlying the divisive-normalization synthesis;
  consulted indirectly; not cited separately.
- [[wolfe2021_guided_search_6]] — guided-search framework
  (priority-map relevant); inspected; unrelated to V × v
  interaction.

Searched anchors that produced no relevant unconsulted
material: surround-suppression, lateral-inhibition (no entry
that bears on the high-V × value question), gamma-coherence,
LIP-specific reward coding (no Peck 2009 stub in wiki —
spawned as CR-024).

### Implications for PRISM v1 / v2

(Mission §3.5.) The Herman-lab change-detection paradigm
([[herman_krauzlis2017_sc_change_detection]]) on which PRISM is
trained operates at *high V by default* — the cue is
informative about which stimulus to attend, and most of the
PRISM training distribution sits at V near 1.0 with the cue
deterministic. C3's prediction, if it stands, is:

1. **At high V (the typical PRISM training regime), value
   differentials should not produce attention-reallocation
   shifts in trained PRISM agents.** Instead, reward
   differentials should manifest as bias-like (choice-side,
   decision-routing) shifts. Concretely: at V = 1.0 with reward
   asymmetry, a trained PRISM agent's $\alpha$ (attention
   allocation to the cued location) should be near ceiling
   regardless of reward; only the readout-side activity
   (analog of LPFC criterion in
   [[luo_maunsell2018_criterion_sensitivity]]) should track
   reward magnitude.

2. **If the user runs PRISM with explicitly low-V training
   conditions** (e.g., V = 0.4 in a 4-location environment, so
   the cue carries some but not most of the information about
   target location), C3 predicts that *value-driven attention
   shifts should emerge in this regime and not in the high-V
   regime.* This is a falsifiable architectural prediction
   that can be tested directly against the PRISM training
   trajectories. The existing `Prism/analysis/avg_saliency_*.py`
   and `Prism/figures/avg_alpha_*.pdf` artifacts could be
   re-run with reward-magnitude blocks crossed against cue
   validity to test this.

3. **The Stănișor 2013 V1 result is the empirical fly in the
   ointment for both above predictions.** If V1-level reward
   modulation is real and translates to early-stage
   sensitivity-like gain on the attended stimulus's
   representation (not just a criterion-stage decision
   readout), then PRISM's early-layer features should *also*
   show reward-modulated gain even at high V — i.e., PRISM's
   shallow grids of the GridCell RNN
   ([[failing_theeuwes2018_selection_history]] §7; see
   `the_user_architectural_program`) should encode reward
   value not just at the readout but at the V1-analog level.
   This would make PRISM partially divergent from the paper's
   normative-model prediction but partially convergent with
   the Stănișor empirical pattern — an architecturally
   informative outcome.

The cleanest within-PRISM experiment that adjudicates this
question would be: train two otherwise-identical PRISM agents,
one on high-V trials only (V = 1.0), one on low-V trials only
(V = 1/N). At evaluation, present both with the same
intermediate-V transfer set and compare (a) attention
allocation $\alpha$ to the cued location as a function of
reward magnitude; (b) decision-head readout sensitivity to
reward; (c) shallow-grid (V1-analog) representational
similarity for high-vs-low-reward stimuli at the cued
location. C3's prediction is that (a) and (c) should be flat in
the high-V agent and graded in the low-V agent, while (b)
should be graded in both. The Stănișor-style refutation of C3b
would correspond to a graded (c) in the high-V agent.

### Loose ends

Candidate follow-up tasks (spawned as backlog items
CR-023 / CR-024 / CR-025; see RESEARCH_BACKLOG.md).

- The Stănișor 2013 result is at *abstract* depth in the wiki.
  Whether the V1 reward modulation translates to a behavioural
  d′ improvement is not in the abstract and is the single most
  consequential piece of information for the C3b verdict. A
  full-depth read via PMC (open-access at
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3670348/) is
  spawned as CR-023.
- The wiki is silent on Peck et al. 2009 *J Neurosci* (LIP
  reward at high V) and Serences 2008 *Neuron* (human fMRI
  value modulation of early visual cortex). Adding stubs and
  evaluating their behavioural-d′ implications spawns as
  CR-024.
- A formal *replication-attack* version of C3b — adding a
  sensitivity-side reward channel to the paper's model and
  re-running the CF / VDA decomposition to see whether the
  qualitative claims survive — spawns as CR-025 (depends on
  CR-005 building the replication substrate).
- The §5.2 wording asks experimenters to *not interpret* the
  absence of high-V VDA as evidence against value-driven
  mechanisms. The dual question — under what conditions
  *should* experimenters interpret the *presence* of high-V
  reward modulation as evidence *for* value-driven attentional
  mechanisms — is not addressed by the paper. The proposed
  weaker reformulation above addresses this asymmetry.

### Next-attack recommendation

Two distinct next-attacks would each be sufficient to elevate
or further weaken this verdict, and both should eventually be
run:

1. **Re-derivation attack on C3 within the model.** Compute
   analytically: at V = 0.75 with the paper's reference
   parameters (N = 4, $d'_{\max} = 2.0$, $f_0 = 0.5$, $h = \sqrt{}$),
   what is the magnitude of $R(P_1) - R(P_2)$ as a function of
   r and v? Is it bounded below 0.005 (the paper's "negligible"
   threshold) for *all* (r, v) in the swept space? If yes, C3b
   is a *theorem of the model* (modulo numerical precision)
   and the verdict's caveat is purely about the model's
   *assumptions* mapping to biology. If no, C3b is at most a
   numerical observation about a particular parameter region
   and the §5.2 categorical wording is too strong even
   internal to the model. This re-derivation would be a
   second attack vector and would license elevation to
   CONFIRMED-CONDITIONAL or movement to CONTESTED depending on
   outcome.

2. **Full-depth Stănișor read (CR-023).** If the behavioural-d′
   probe in Stănișor 2013 shows reward-driven d′
   improvement at high V that the paper's criterion-only
   account cannot recover, C3b is *refuted* and the verdict
   moves to CONTESTED. If the behavioural data are consistent
   with a criterion-side interpretation, C3b stays
   WEAKLY-SUPPORTED with the Stănișor result reclassified
   from "constrain" to "support."

Of the two, the re-derivation attack is the cheaper and more
informative first step: it adjudicates whether the §5.2
categorical wording is a theorem of the model or a numerical
observation, which determines what the literature attack can
ever conclude.

## Version 0.2 — 2026-05-17

### What this version did

Executed the re-derivation attack recommended at the end of Version
0.1 (CR-026; mission §3.2 vector "re-derivation"). The attack uses
the closed-form escape-threshold machinery from
[`../derivations/C2--non-monotonic-vda.md`](../derivations/C2--non-monotonic-vda.md)
§2.5 (CR-001) to compute
$\sup_{r \in [0.1, 10],\,v \in \{1,...,5\}}\,[R(P_1) - R(P_2)]$ at
$V = 0.75$, the paper's stated "high validity" threshold. Numerical
sweep at the paper's primary grid resolution
($\Delta\alpha = 0.01$, $\Delta c = 0.05$), with a refinement pass
at $\Delta\alpha = 0.005$, $\Delta c = 0.025$ at the empirical sup
to rule out grid-resolution artefacts. Full derivation in
[`../derivations/C3--high-V-supremum.md`](../derivations/C3--high-V-supremum.md);
companion replication code at
[`../replications/C3--high-V-supremum/`](../replications/C3--high-V-supremum/).

### Verdict

**Label: CONTESTED.** (Moved from WEAKLY-SUPPORTED.)

The §4.4 / §5.2 categorical wording is **refuted internal to the
model under its own assumptions** (A1–A7). The supremum at
$V = 0.75$ across the paper's primary $(r, v)$ grid is

$$
\sup_{r,v}\,\mathrm{VDA}(r,v;\,V{=}0.75) \;=\; 0.0410\;\text{(coarse)}\;/\;0.0400\;\text{(refined)}
$$

attained at $(r, v) = (0.10, 5)$, with $\alpha^\star_{P_1} = 0.97$,
$\alpha^\star_{P_2} = 1/N = 0.25$. This is $8\times$ §4.4's
"$<0.005$ negligible" threshold and $2\times$ §4.4's own
"hot zone" boundary ($\mathrm{VDA} > 0.02$).

The mechanism is the one CR-001 §2.5 derived in closed form: at
high $V$, $P_2$ (value-blind, $v{=}1$ fixed-$\alpha$) has an
escape threshold $r^\dagger(1)$ that is *not* arbitrarily small.
At $V = 0.75$, $N = 4$, $r^\dagger(1) \approx 0.11$ — interior to
the paper's $r$-grid. The VDA window $(r^\dagger(v),\,r^\dagger(1))$
at $v = 5$, $V = 0.75$ is approximately $(0.025, 0.13)$, and the
paper's grid samples *two* points inside it (at $r \in \{0.10,
0.126\}$). Across both grid points and across $v \in \{2, 3, 4,
5\}$, eight grid combinations violate "$<0.005$" and six violate
"$<0.02$" — $\approx 8\%$ of the V=0.75 slice.

**The cause is now nameable.** §4.4's argument
("the validity gradient alone drives attention to ceiling")
applies to $P_1$ at high $v$ but does *not* apply to $P_2$ when
$r$ is just above $r^\dagger(v)$ but just below $r^\dagger(1)$.
The skipped derivation step in the paper is the assertion that
$P_2$ also converges to $\alpha \approx 1$ at $V \geq 0.75$;
the re-derivation shows this requires the additional condition
$r > r^\dagger(1;V,N)$, which fails at $r = 0.1$ when $N = 4$.

### Why the label is CONTESTED (not REFUTED)

The substantive content of §4.4 / §5.2 — that the high-V VDA
window is narrow, that the *typical* high-validity cueing paradigm
will not detect VDA, and that the §5.2 advice to experimenters
about what null findings mean is *qualitatively* correct — survives
the attack. What fails is the **categorical wording**: the $V \geq
0.75$ threshold is one V-grid step too generous, and the
"regardless of other parameters" quantifier is false at the
$(r \in \{0.10, 0.126\}, v \geq 2)$ corner. A proposed reformulation
(§7 below) preserves the paper's scientific point while making the
V-threshold explicitly $r$- and $N$-dependent.

Per mission §3.1, REFUTED requires that "the paper cannot survive
without substantive revision." This re-derivation suggests
substantive revision is needed in §4.4 and §5.2 *as written*, but
the underlying normative argument and the §5.1 theoretical case
("why criterion dominates") are unaffected. CONTESTED is the
appropriate label: claim too strong as written, with a weaker
reformulation drafted.

### Evidence

Full derivation:
[`../derivations/C3--high-V-supremum.md`](../derivations/C3--high-V-supremum.md).

Numerical sweep data:
[`../replications/C3--high-V-supremum/output/sup_vda_at_V075.json`](../replications/C3--high-V-supremum/output/sup_vda_at_V075.json).

Headline numbers:

| Quantity | Value | Source |
|:---|---:|:---|
| sup VDA at $V=0.75$ (coarse) | 0.0410 | replication §5.1 |
| sup VDA at $V=0.75$ (refined) | 0.0400 | replication §5.1 |
| Paper's "negligible" threshold | 0.005 | paper §4.4 |
| Paper's "hot zone" threshold | 0.020 | paper §4.4 |
| Empirical $V_{\text{critical}}$ at $r=0.1$, $N=4$ | $(0.775, 0.780)$ | derivation §5.2 |
| Closed-form $V_{\text{critical}}$ at $r=0.1$, $N=4$ (simple approx, $\kappa{=}0.85$) | 0.74 | derivation §2 Eq. 7 |
| VDA at $(V{=}0.50, r{=}0.1, v{=}5)$ (reference) | 0.0155 | CR-001 |
| VDA at $(V{=}0.75, r{=}0.1, v{=}5)$ | 0.0400 | this run |
| Ratio $V{=}0.75 / V{=}0.50$ at sup | $\approx 2.6$ | this run |

Direct citations:
- [`../derivations/C2--non-monotonic-vda.md`](../derivations/C2--non-monotonic-vda.md)
  Eq. (2.5) — the closed-form $r^\dagger(v) = G_u / [(N-1) G_c(v)]$
  that drives the entire re-derivation.
- [[stanisor2013_v1_value_attention]] — the Version 0.1 constraint is now
  *predicted by the proposed §4.4 reformulation*: the high-V V1
  reward modulation Stănișor reports could be the substrate of the
  residual high-V VDA window the model predicts at small $r$.
  Stănișor's classification potentially shifts from "constrain" to
  "support" of the *reformulated* C3b. Adjudication requires CR-023
  (Stănișor full-depth read).
- [[luo_maunsell2018_criterion_sensitivity]] — the Version 0.1
  primary support for C3b unchanged; the reformulation's
  "pre-commit to $r$-calibration" prescription is consistent with
  Luo-Maunsell's stimulus-side sensitivity manipulation, which is
  one implementation of $r$-calibration.
- [[solomon2004_cues_sensitivity]] — newly relevant: high-V cueing
  with sensitivity measurement. The proposed reformulation predicts
  Solomon's design would find a measurable d′ effect at $v \geq 3$
  if it had crossed cueing with reward magnitude (it did not). A
  follow-up could be a literature attack searching for any
  unpublished or unindexed extensions.
- [[reynolds_heeger2009_normalization]] — the normalisation
  substrate. The closed-form $\kappa(V,N)$ ratio depends on the
  optimal criteria $c_c, c_u$, which in turn depend on the
  normalisation properties of the response gain. A clean test of
  the proposed reformulation would predict $\kappa$ from a
  Reynolds-Heeger normalisation pool and check $V_{\text{critical}}$.

### Wiki cross-references

(Mission §11. New entries consulted *this version*; entries in
Version 0.1 list above remain relevant.)

- [[../derivations/C2--non-monotonic-vda.md]] (internal) — re-used
  the §2.5 closed-form escape-threshold machinery; the entire §1–§4
  of the new derivation is an *extension* of that work to the
  $V$-axis. Cited in derivation §1, §2.
- [[stanisor2013_v1_value_attention]] — reclassified
  ("constrain" → potential "support of reformulated C3b") in light
  of the predicted residual high-V VDA window. Awaits CR-023
  full-depth read.
- [[solomon2004_cues_sensitivity]] — re-inspected. Solomon's
  high-V psychophysics did not cross validity with reward, so the
  reformulation's d′-at-high-V prediction is not directly tested by
  Solomon. Spawned as part of CR-030 (literature follow-up).
- [[luo_maunsell2018_criterion_sensitivity]] — re-cited as the
  closest *positive* test of the reformulation; their stimulus-side
  sensitivity manipulation is one way to operationalise the
  "$r$-calibration" the proposed §5.2 prescribes.
- [[reynolds_heeger2009_normalization]] — bears on the
  $\kappa(V,N)$ density ratio that controls $V_{\text{critical}}$
  via the optimal criteria; not directly cited in derivation but
  flagged for the future $\kappa$-from-normalisation derivation
  spawned as CR-027.
- [[cohen_maunsell2009_correlations]] — bears on assumption A1
  (independence) which the re-derivation assumes. The high-V VDA
  window magnitude predicted by the derivation could shrink under
  cross-location response correlations; a future replication-attack
  on A1 should test this.
- [[hawkins1990_attention_detectability]] — high-V cueing with d′
  measurement; their classical paradigm shows attention effects on
  d′ at high V (validity-driven, not value-driven). Consistent with
  the original C3b in its existence-of-attention-d′-effects sense;
  silent on the value-magnitude variant the reformulation
  emphasises.
- [[muller_findlay1987_sensitivity_criterion]] — Mueller & Findlay's
  classical d′/c decomposition methodology underlies the SDT
  decomposition the paper formalises; the closed-form $\kappa$
  ratio of densities at the optimal criteria is essentially their
  ROC framework restated for the multi-location case. Consulted but
  not cited separately.

Anchors that turned up nothing new in this version's targeted sweep:
*surround-suppression*, *LIP-reward* (still no wiki entry; spawned
CR-024 in run-004 remains queued).

### Implications for PRISM v1 / v2

(Update of Version 0.1's PRISM block, in light of the new derivation.)

The Version 0.1 prediction — *at high V (PRISM's training regime),
value differentials should not produce attention-reallocation shifts
in trained PRISM agents* — needs a refinement. The re-derivation
shows that the prediction is correct *only above*
$V_{\text{critical}}(r, N) \approx 1/(1 + r\,(N-1)/\kappa)$, and
fails in a narrow $r$-band just above $r^\dagger(v)$ at any $V$
below $V_{\text{critical}}$.

Concretely, for PRISM trained on a 4-location task ($N{=}4$) at
$V = 1.0$ (deterministic cue), the prediction holds without
caveat: $V = 1.0 > V_{\text{critical}}$ at every $r$, so trained
PRISM should not show value-driven $\alpha$ shifts. But:

1. **Curriculum or evaluation at $V \in [0.75, 0.78]$ is the
   diagnostic regime.** If the user evaluates PRISM at intermediate
   validity $V \in [0.75, 0.78]$ with reward magnitude crossed
   against asymmetry, the model predicts a *measurable but small*
   VDA effect at low $r$ (cost-dominant asymmetry) and high $v$.
   This is a sharper PRISM prediction than the V0.1 version
   ("flat at high V, graded at low V"): the boundary at $V \approx
   0.78$ is sharp, and PRISM agents that show VDA at $V = 0.80$ but
   not at $V = 0.75$ would *diverge* from the normative model in a
   testable way.

2. **The Stănișor V1 result becomes more conjoint with the
   reformulation.** The original V0.1 worry was that the Stănișor V1
   reward-modulation finding could refute C3b. The reformulation
   *predicts* a residual high-V VDA window: at the boundary
   $V \to V_{\text{critical}}^-$, the model itself predicts
   reward-driven sensitivity gain at the cued location. If PRISM's
   early layers (the GridCell RNN; see
   [[../../research_db/threads/the_user_architectural_program.md]])
   show reward-modulated gain *only* in the boundary regime and *not*
   far above it, this is convergent with both Stănișor (existence)
   and the reformulated normative prediction (boundary regime).

3. **The PRISM "pre-commit to $r$-calibration" prescription** from
   the §5.2 reformulation is directly relevant to PRISM evaluation
   protocols. The user's
   `Prism/analysis/avg_saliency_*.py`,
   `Prism/figures/avg_alpha_*.pdf`
   artifacts presumably evaluate at the training $r$ (whatever the
   PRISM env stipulates implicitly via its loss landscape); a
   protocol that explicitly varies $r$ across evaluation conditions
   would let the experimenter locate $V_{\text{critical}}$ in
   PRISM's behaviour and compare to the closed-form prediction.

### Loose ends

Candidate follow-up tasks (to be added to the backlog at end of
this run as CR-027, CR-028, CR-029, CR-030):

- **CR-027** (re-derivation, medium): full FAR-corrected
  $V_{\text{critical}}(r, N, d'_{\max}, f_0, h)$ closed form. The
  simple change-side approximation §2 Eq. 5 underestimates by
  $\approx 4$pp because it neglects the FAR-side density. A full
  closed form would predict $V_{\text{critical}}$ across the paper's
  full secondary-sweep grid.
- **CR-028** (replication, medium): Variant B sup at $V = 0.75$.
  Confirms whether the §4.4 wording is wrong in both variants or
  only in Variant A.
- **CR-029** (sensitivity, low): map $V_{\text{critical}}(r, f_0,
  h, N)$ across the paper's secondary-sweep grid; predicts the
  shape of the "negligible-VDA-regardless-of-r" region across the
  full parameter space.
- **CR-030** (literature, low): given the new closed-form
  $V_{\text{critical}}$, search the literature for cueing experiments
  with high $V$ AND high $v$ AND cost-dominant $r$ (the predicted
  residual high-V VDA window). Solomon 2004, Stănișor 2013 (under
  CR-023), and the Peck 2009 / Serences 2008 stubs (under CR-024)
  are the candidates.

### Next-attack recommendation

C3 is now CONTESTED with the §4.4 / §5.2 wording specifically
under attack. The next-attack ordering depends on whether the
goal is to *characterise the V_critical boundary further* (CR-027,
CR-028, CR-029) or to *empirically validate the reformulation*
(CR-023 Stănișor full-depth read; CR-030 broader literature
search). For verdict-stability purposes the *re-derivation*
follow-ups would not change the CONTESTED label (the substantive
refutation is already in place) — they would only sharpen the
proposed reformulation.

The recommended next pick is **CR-027** (full FAR-corrected
closed form): cheapest, builds on the same machinery, and would
resolve the 4-percentage-point gap between the simple-approximation
prediction ($\approx 0.74$) and the empirical boundary
($\approx 0.78$) — strengthening the reformulation's analytic
substrate. After CR-027, switching to CR-004 (the still-untouched
C4 re-derivation, with CR-019 piggyback) is the natural critical-
path move: C4 is the only remaining headline claim with no
attack-vector executed.

### Connection to other verdicts

The CR-026 finding also has implications for the C1 verdict
(`C1--criterion-fraction-floor.md`, currently CONTESTED). At
$V = 0.75$, $r = 0.1$, the criterion fraction is $\approx 0.95$ —
firmly inside C1's claimed $[0.60, 0.96]$ range. So the C1 CONTESTED
verdict is not affected at this point; the C1 CF-floor failure
happens at $V = 0.25$ (variant B argmin), not at the new C3
refutation corner. But the *combined* C1+C3 picture suggests the
paper's §4 figures are best described by saying: "VDA and CF have
opposite v-axis monotonicities; both their categorical wordings
($V \geq 0.75 \to$ low VDA; $V \in [0.25, 1.0] \to$ CF $\in [0.60,
0.96]$) fail at specific corners of the swept space, but the
qualitative trends are correct in the bulk." The agent should not
re-attack C1 on the strength of CR-026 alone; spawning a *unified*
V-boundary derivation under CR-021 (already in backlog) would
treat the two verdict adjustments as one piece of work.
