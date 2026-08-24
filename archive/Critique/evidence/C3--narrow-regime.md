---
type: evidence-dossier
claim_id: C3
paper_section: "§4.4 + §5.2"
claim_summary: "VDA is confined to a narrow regime: low cue validity (V near 1/N), high value contrast (v ≫ 1), moderate benefit/cost asymmetry (r ∈ [0.2, 1.0]). §5.2 strengthens this to a categorical experimental-design prediction: 'Standard spatial cueing paradigms with high validity (V ≥ 0.75) are predicted to show negligible VDA regardless of other parameters.'"
first_attack_run: run-004
last_updated: 2026-05-17
---

# Evidence dossier: C3 — VDA confined to a narrow regime (low V, high v)

This dossier accumulates literature evidence bearing on C3 across runs. New
entries append a dated `## Version <X.Y>` section at the bottom; earlier
sections are preserved verbatim. Each source is rated for direction
(supports / contradicts / constrains / unrelated) and weight per mission §5.5.

## Version 0.1 — 2026-05-17

### Attack scope this version

Literature attack on C3 (and its §5.2 derivative experimental-design
prediction) via mission-§11 wiki sweep, with a single targeted PubMed
fetch to fill one gap the wiki was silent on. The §5.2 wording is the
strongest version of C3 — categorical ("regardless of other parameters")
and quantitative (V ≥ 0.75 threshold) — and is the version this attack
interrogates.

### Decomposition of the claim into testable sub-statements

The §5.2 wording bundles two distinct empirical predictions; the
literature has different things to say about each.

- **(C3a)** *VDA is robustly observed in the LOW-V regime* (V near 1/N).
  This is a positive prediction the literature can confirm. The
  value-driven-attentional-capture paradigm (Anderson, Laurent & Yantis
  2011 and follow-ups) operates at V = 1/N (target colour uninformative
  of location, or even task-irrelevant) and reliably finds value-driven
  attentional biasing on RT, accuracy, ERP (N2pc), and saccade
  trajectory. CONFIRMS C3a.
- **(C3b)** *VDA is negligible in the HIGH-V regime* (V ≥ 0.75)
  *regardless of other parameters*. This is a categorical negative
  prediction. The wiki contains many high-V cueing studies, but most
  hold reward constant within trial and so do not test the *value*
  manipulation specifically at high V. Two classes of high-V studies do
  vary reward magnitude and are the relevant tests: (i) studies in
  which reward differentials are used *deliberately to induce criterion
  shifts* (Luo & Maunsell 2018); these support C3b because they show
  reward loading on criterion, not on sensitivity. (ii) studies in
  which reward differentials are not designed around the SDT
  decomposition (Stănișor et al. 2013 PNAS; Peck et al. 2009; Serences
  2008); these are the candidate refutations, and the principal one in
  the wiki after this run is Stănișor et al. 2013, which reports V1
  single-unit modulation by relative reward value at high V with
  attention-like latency and per-cell correlation between value and
  attention effects. This is the entry in the dossier that most
  *constrains* C3b without yet outright refuting it (mechanism — V1
  modulation — could still be the substrate of a criterion-side
  decision-readout effect rather than a true α-reallocation).

### Source-by-source evaluation

#### Source: [[failing_theeuwes2018_selection_history]] (depth: full)

- **Bears on the claim how:** Comprehensive review of value-driven /
  selection-history attention. Documents the canonical paradigm:
  training phase pairs colours with high vs low monetary reward; test
  phase uses formerly-rewarded colours as task-irrelevant distractors
  in a singleton search where colour carries *no spatial validity*
  (V = 1/N). Reports RT slowing of ~20–60 ms and accuracy drops of
  several percentage points from value-driven capture; effects survive
  ≥6 months after the reward-pairing phase. Distinct neural
  correlates: enhanced N2pc to formerly-rewarded distractors; LIP
  reward-coding; ACC reward-feedback amplitude predicting bias.
- **Regime:** V = 1/N or lower (rewarded feature is uninformative or
  actively counterproductive). Direct empirical evidence for the *low-V*
  end of the C3 prediction interval.
- **Direction:** **Supports C3a.** Silent on C3b — does not run a
  high-V condition.
- **Quantitative weight:** Strong. Narrative review of dozens of
  primary studies across multiple labs; effects replicate at scale
  (Anderson, Laurent & Yantis 2011 alone has been cited 1500+ times).
- **What the verdict file did with this:** Cited as the primary
  empirical anchor that VDA does emerge at low V; used to argue C3a
  is robust.

#### Source: [[hickey2010_reward_salience_acc]] (depth: full)

- **Bears on the claim how:** Single-trial reward manipulation in a
  human additional-singleton task. Reward magnitude on trial $n$
  modulates the trial-$n+1$ attentional bias toward the previously-
  rewarded colour, with N2pc amplitude rising and RT slowing
  proportionally. Crucially, the rewarded colour *changes
  unpredictably across trials* — V = 1/N for the colour-to-location
  mapping. The bias persists even though it is *counter-strategic*.
  Across-participant FRN amplitude (a dorsal-ACC reward-feedback
  signature) predicts bias magnitude.
- **Regime:** V = 1/N (target colour uninformative of location and
  changing trial-to-trial). The empirical anchor for the *minimal*
  paradigm-version of value-driven attention.
- **Direction:** **Supports C3a.** Silent on C3b.
- **Quantitative weight:** Medium-strong. N = 14 (small for the
  across-subject correlation); within-subject RT and N2pc effects
  replicate. The lag-1 effect is the *minimal* version of the
  Anderson 2011 multi-trial scaling-up.
- **What the verdict file did with this:** Cited alongside Failing &
  Theeuwes 2018 as evidence for C3a. Also cited as the source
  paradigm whose absence in the high-V regime constitutes the §5.2
  gap.

#### Source: [[luo_maunsell2018_criterion_sensitivity]] (depth: full)

- **Bears on the claim how:** Macaque LPFC single-unit recording in a
  cued change-detection task. **Cue is deterministic** (the cue tells
  the monkey which of two stimuli to attend; effective V ≈ 1.0). Two
  task manipulations are run *independently*: (i) reward asymmetry,
  used *deliberately to induce a criterion shift*; (ii) stimulus
  contrast / size, used to induce a sensitivity shift. Both
  manipulations modulate LPFC neurons but with *distinguishable
  neural signatures* (different patterns of firing-rate change,
  Fano factor, pairwise correlation). Visual cortex (V4 etc.)
  modulates only with the sensitivity manipulation.
- **Regime:** V ≈ 1.0 (high V). Reward magnitude varied within this
  regime. The most direct existing test of the §5.2 prediction in the
  wiki: does varying reward at high V produce a sensitivity effect
  or a criterion effect?
- **Direction:** **Strongly supports C3b.** In Luo-Maunsell's
  high-V regime, *reward asymmetry produces criterion shifts but
  not sensitivity shifts* — which is precisely the paper's §5.2
  prediction (value at high V loads on criterion, not on attention
  reallocation that improves d').
- **Quantitative weight:** Strong. Mechanism is well-isolated by
  the explicit factorial design (reward × stimulus); the
  sensitivity / criterion dissociation is at the single-neuron and
  population-decoding levels.
- **Caveat:** Partially *circular* support — Luo-Maunsell's
  experimental design was explicitly *built around* the SDT
  decomposition the paper's model formalizes. The finding is
  consistent with the paper's prediction but does not constitute an
  independent test because the paradigm was constructed to keep
  value loading on β by manipulating only reward asymmetry (not
  per-stimulus value differentials that the value-driven-capture
  paradigm uses).
- **What the verdict file did with this:** Cited as the principal
  high-V evidence supporting C3b, with the circularity caveat
  recorded.

#### Source: [[maunsell2015_attention_mechanisms]] (depth: full)

- **Bears on the claim how:** Review-level synthesis of three decades
  of macaque single-unit attention work, organised around the
  sensitivity-vs-criterion dissociation among other dimensions. Key
  empirical generalisations relevant to C3b: (i) V4 / IT firing-rate
  modulations correlate with d′ (sensitivity); (ii) criterion changes
  correlate with LPFC and subcortical activity; (iii) standard
  primate cueing paradigms operate at V near 1.0 (deterministic cue)
  with reward magnitude either fixed or used to induce criterion.
- **Regime:** Synthesis of the entire macaque-physiology canon, which
  is concentrated in the high-V regime by historical accident of how
  the field has run its tasks.
- **Direction:** **Supports C3b at the descriptive level.** The
  review's framing — that sensitivity is a cortical visual-cortex
  signal, criterion is an LPFC + subcortical signal — *is* the
  decomposition the paper's model formalises, and the empirical
  literature Maunsell synthesises is consistent with that
  decomposition in the high-V regime where almost all the work has
  been done.
- **Quantitative weight:** Strong as a review (aggregates ~30 years
  of data); medium as an *independent* test of C3b (the same
  circularity caveat as Luo-Maunsell applies, since most cited
  studies inherit the SDT-aligned design assumptions).
- **What the verdict file did with this:** Cited as the principal
  textbook-level synthesis supporting the paper's decomposition,
  with the circularity caveat recorded.

#### Source: [[sridharan2017_sc_sensitivity_bias]] (depth: full)

- **Bears on the claim how:** Multi-alternative SDT re-analysis of
  four published SC microstimulation / inactivation studies in
  macaques performing high-V attention tasks. Finding: SC
  manipulation effects load **primarily on bias (criterion), not on
  sensitivity**, across all four studies. Implication: the SC
  contributes a spatial choice bias *downstream* of forebrain
  sensitivity enhancement.
- **Regime:** All four re-analysed studies use high V
  (deterministic or near-deterministic cueing).
- **Direction:** **Supports C3b indirectly.** The SC — a primary
  candidate for the source of attention-reallocation signals — turns
  out to contribute mostly to criterion rather than to sensitivity in
  high-V tasks. This is consistent with the paper's framing that, at
  high V, attentional contributions to performance are best modelled
  as criterion-side rather than α-side reallocation.
- **Quantitative weight:** Medium-strong. Re-analyses are
  systematic and apply a formal framework, but the original studies
  were not designed for the dissociation — the SC-as-bias
  characterisation could shift if new studies with explicit
  sensitivity probes are run.
- **What the verdict file did with this:** Cited as
  cross-substrate support: at high V, even the canonical
  attention-source candidates contribute via the criterion stream
  rather than the sensitivity stream.

#### Source: [[stanisor2013_v1_value_attention]] (depth: abstract, new stub this run)

- **Bears on the claim how:** Macaque V1 single-unit recording
  during a curve-tracing / object-based attention task at high
  effective V (object identity is informative of which stimulus to
  select). **Reward magnitude is varied across stimuli within the
  high-V regime.** Findings (verbatim from the PubMed abstract):
  *"The reward value of a stimulus relative to the value of other
  stimuli is a good predictor of V1 activity. Relative value biases
  the competition between stimuli, just as has been shown for
  selective attention. The neuronal latency of this reward value
  effect in V1 was similar to the latency of attentional influences.
  Moreover, V1 neurons with a strong value effect also exhibited a
  strong attention effect, which implies that relative value and
  top-down attention engage overlapping, if not identical, neuronal
  selection mechanisms."*
- **Regime:** High effective V × varied reward magnitude. This is the
  paradigm class the §5.2 prediction directly addresses.
- **Direction:** **Constrains C3b. Possibly partially contradicts.**
  The Stănișor result demonstrates that value at high V *does*
  modulate the earliest cortical sensory signal (V1), with
  attention-like latency and per-cell value/attention covariation.
  This is *prima facie* in tension with the §5.2 prediction that
  value at high V contributes negligibly. But the interpretation
  depends on whether V1 reward modulation translates to
  behavioural d′ improvement (true sensitivity gain, would refute
  C3b) versus a criterion-readout correlate (consistent with
  C3b). The abstract reports that V1 selection signals from value
  and attention are mechanistically overlapping — which is
  Stănișor et al.'s headline claim and the natural reading that
  pushes toward refutation — but the actual behavioural-d′
  decomposition is not in the abstract and requires either a
  full-depth read or a follow-up SDT-aware experiment.
- **Quantitative weight:** Medium-to-strong on the *neural* claim
  (single-unit V1 recording with explicit value-vs-attention
  factorial); weak-to-medium on the *behavioural-d′* claim (not
  reported in abstract; depth: abstract).
- **What the verdict file did with this:** Cited as the principal
  candidate refutation of §5.2 currently in the wiki; verdict
  records this as a specific *constraint* on the §5.2 wording
  rather than a refutation, and spawns a follow-up task to read
  the Stănișor paper at full depth and assess the
  behavioural-d′ claim.

#### Source: [[posner1980_orienting]] (depth: full)

- **Bears on the claim how:** Foundational characterisation of the
  validity effect — validity gradient produces RT and accuracy gains
  at cued locations, scaling with V. Establishes the high-V baseline
  the paper's model uses (validity saturates allocation at high V).
- **Regime:** V varies across blocks (the original parametric
  manipulation of cue validity); reward is held constant.
- **Direction:** **Supports the assumption on which C3b rests.**
  Validity-driven attention does saturate at high V; the paper's
  prediction that there is no room for value to further reallocate
  α inherits its empirical basis from this saturation. Does NOT
  test value × validity interaction.
- **Quantitative weight:** Strong on the validity-saturation claim
  (replicated thousands of times); not a direct test of C3.
- **What the verdict file did with this:** Cited as the
  background-saturation result that licenses the paper's framing.

#### Source: [[cameron2002_covert_attention_contrast]] (depth: full)

- **Bears on the claim how:** Psychophysics of covert attention at
  high V (deterministic peripheral cue). Attention shifts the
  contrast psychometric function — a *sensitivity* effect, not a
  criterion effect — by 10–20% threshold reduction. No reward
  manipulation.
- **Regime:** High V (deterministic cue), no value manipulation.
- **Direction:** **Constrains C3b.** Shows that *some* attention
  effects at high V are sensitivity-side (not criterion-side); but
  these effects are driven by V (validity gradient), not by v
  (value) — so consistent with the paper's framing.
- **Quantitative weight:** Strong for the sensitivity-at-high-V
  claim; unrelated to the value-component-of-attention claim.
- **What the verdict file did with this:** Cited to make explicit
  that high-V attention effects *exist* and are sensitivity-side,
  but are V-driven not v-driven, so do not refute C3b.

#### Source: [[carrasco2011_visual_attention_25y]] (depth: full)

- **Bears on the claim how:** 25-year synthesis of covert visual
  attention psychophysics. Most cited studies use deterministic
  cueing (high V). Findings: attention is multiplicative gain on
  early visual responses; both sensitivity changes (threshold
  shifts) and criterion changes are observable; the gain is
  V-driven in the standard paradigms.
- **Regime:** Almost entirely high V; reward generally held
  constant.
- **Direction:** **Supports C3b indirectly.** The literature
  Carrasco synthesises does not contain a high-V × value-magnitude
  experiment that would refute C3b; the absence is itself a
  signal.
- **Quantitative weight:** Strong as a comprehensive review;
  medium as a direct test of C3b (absence-of-evidence rather than
  evidence-of-absence).
- **What the verdict file did with this:** Cited as part of the
  "the standard high-V psychophysics literature is silent on the
  value manipulation" framing.

#### Source: [[srinath2021_attention_information_flow]] (depth: full)

- **Bears on the claim how:** Macaque MT–SC simultaneous recording
  at V ≈ 0.80 (high V) in a cued change-detection task. Attention
  increases cross-area predictive R² by 20–40% under attention,
  with the same communication subspace. Behavioural attention
  benefit (faster RT, higher hit rate) is present.
- **Regime:** High V (≈ 0.80), no reward magnitude manipulation —
  attention engagement is purely validity-gradient-driven.
- **Direction:** **Consistent with C3b but does not test it.**
  At high V the validity gradient produces robust attention
  effects — the paper's prediction is not that high V produces no
  attention effects, only that adding value differentials at high V
  produces no additional improvement above what validity alone
  delivers.
- **Quantitative weight:** Strong on the cross-area-communication
  result; not a direct test of C3b.
- **What the verdict file did with this:** Cited to clarify
  that high-V attention effects exist (validity-driven) and to
  draw the contrast: the question §5.2 addresses is whether adding
  *value* differentials on top of high V further moves
  performance.

#### Source: [[bhatnagar2022_attention_choice_metaanalysis]] (depth: full)

- **Bears on the claim how:** Meta-analysis on attention →
  preferential choice. Establishes that attention causally biases
  choice by 3–4 percentage points across hundreds of experiments.
  Exposure-time manipulations dominate; first-fixation
  manipulations are null.
- **Regime:** Preferential-choice with visual stimuli; V is not
  parametrically manipulated in this literature.
- **Direction:** **Unrelated to C3 directly.** Relevant to the
  *implications-for-PRISM* block (attention causally drives
  choice) but does not test the high-V × value interaction.
- **Quantitative weight:** Strong meta-analytic effect; orthogonal
  to C3 specifically.
- **What the verdict file did with this:** Not cited in the C3
  verdict body; logged here for completeness of the wiki sweep.

#### Source: [[baluch_itti2011_topdown_mechanisms]] (depth: full)

- **Bears on the claim how:** Taxonomy of top-down attention
  channels (spatial, feature, object, scene-gist); explicitly
  flags reward as an *emerging fifth channel* (anticipating
  Anderson 2011 / Failing & Theeuwes 2018). Does not contain a
  high-V × value-magnitude experiment.
- **Regime:** Synthesis, no specific regime.
- **Direction:** **Constrains.** Notes that reward-driven
  attention is a real channel, but did not (in 2011) have the
  empirical material to characterise its V-dependence.
- **Quantitative weight:** Medium; review-level framing.
- **What the verdict file did with this:** Cited as the taxonomic
  framing.

#### Source: [[monosov2020_outcome_uncertainty]] (depth: full)

- **Bears on the claim how:** Uncertainty-mediates-attention
  framework. Uncertainty is high at low V and low at high V — so
  the *uncertainty* axis predicts attention should be most
  modulated by reward/value at low V (consistent with C3a) and
  least at high V (consistent with C3b).
- **Regime:** Synthesis across primate uncertainty work; no
  single regime.
- **Direction:** **Indirectly supports C3.** The uncertainty
  axis is the natural normative framing that makes the paper's
  V-dependence prediction sensible: at high V the system already
  has low uncertainty about where to attend, so further
  value-driven biasing of attention has nothing to add.
- **Quantitative weight:** Medium (review-level theoretical
  framing rather than a direct empirical test).
- **What the verdict file did with this:** Cited as the
  theoretical framing under which the paper's normative
  prediction makes sense from a different (uncertainty-axis)
  starting point.

#### Source: [[herman_krauzlis2017_sc_change_detection]] (depth: full)

- **Bears on the claim how:** Macaque SC change-detection at high
  V (deterministic cue). Establishes that SC carries attention-
  related signals at high V. No reward magnitude manipulation.
- **Regime:** High V, fixed reward. Direct paradigm precursor for
  the Recurrent ViT.
- **Direction:** **Indirectly relevant to PRISM block.** Cited
  in §3.5 ("Implications for PRISM") of the verdict rather than
  in the C3 evaluation directly.
- **Quantitative weight:** Strong as a paradigm anchor; not a
  test of C3.
- **What the verdict file did with this:** Cited in the
  PRISM-implications block.

#### Source: [[herman_arcizet2020_caudate_sc]] (depth: full)

- **Bears on the claim how:** SC → CDh attention-signal cascade
  in macaque under high-V cueing. Relevant to the PRISM
  multi-hub design.
- **Direction:** **Indirectly relevant to PRISM block.**
- **Quantitative weight:** Strong for the cascade claim; not a
  direct test of C3.
- **What the verdict file did with this:** Cited in the
  PRISM-implications block.

### Synthesis at the end of this version

The wiki literature considered in this version partitions into three
roughly disjoint categories with respect to C3:

1. **Low-V × value-magnitude literature (the value-driven-
   attentional-capture canon).** Operates at V = 1/N. Reliably finds
   value-driven attentional biases. *Confirms C3a; silent on C3b.*

2. **High-V × deliberately-criterion-targeted value literature
   (the Luo-Maunsell SDT-aligned macaque tradition).** Operates at
   V ≈ 1.0 with reward asymmetry explicitly used to induce criterion
   shifts. Finds value loads on criterion, not on sensitivity.
   *Supports C3b, but with a circularity caveat — the design assumes
   the SDT decomposition the paper's model formalises.*

3. **High-V × non-SDT-aligned value-magnitude literature.** The
   principal entry in the wiki after this run is Stănișor et al.
   2013 — high-V curve-tracing with reward magnitude variation,
   finding V1 modulation by relative value with attention-like
   latency and per-cell value/attention covariation. *Constrains
   C3b; potentially partially refutes if the V1 effect translates
   to a behavioural d′ improvement that the model's
   criterion-only account cannot recover.*

The §5.2 wording — "negligible VDA regardless of other parameters at
V ≥ 0.75" — is the strongest version of C3 and is the version that
the Stănișor result directly constrains. A weaker reformulation that
the literature surveyed here would unambiguously support is:

> "Standard spatial cueing paradigms with high validity (V ≥ 0.75) in
> which reward magnitude is manipulated *to induce criterion shifts*
> are predicted to show negligible *attention-reallocation-side* VDA;
> sensitivity-side reward effects observed in early visual cortex
> (e.g., Stănișor et al. 2013) do not refute this if they do not
> translate to behavioural d′ improvements."

Verdict implication: C3 (§4.4 wording) appears robust at the
low-V end (C3a confirmed) and at high V *under the SDT-design
assumption* (C3b weakly supported); the §5.2 categorical wording is
constrained by the Stănișor result and would benefit from explicit
softening or from an explicit acknowledgement that early-visual-
cortex reward modulation has been documented at high V even though
the paper's model interprets it as criterion-side.

### Follow-up attacks spawned by this version

- **CR-023 (literature, low priority — full-depth read).** Read
  Stănișor et al. 2013 at full depth via PubMed Central
  ([PMC3670348](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3670348/))
  or via Wiley publisher abstract; assess whether the V1 reward
  modulation translates to a behavioural-d′ improvement that the
  paper's model cannot recover via criterion alone. If yes, C3
  moves to CONTESTED. If no, C3 stays WEAKLY-SUPPORTED.
- **CR-024 (literature, medium priority).** Add wiki stubs for
  Peck et al. 2009 *J Neurosci* (LIP reward at high V) and
  Serences 2008 *Neuron* (human fMRI value modulation of early
  visual cortex). Both are high-V × value-magnitude experiments
  that could either reinforce or refute Stănișor's V1 signature.
- **CR-025 (replication, low priority, depends on CR-005).** Add
  a *sensitivity-side reward modulation* to the replication
  substrate: model V1-like input gain as a function of reward
  magnitude (not just allocation α), then re-evaluate whether
  the paper's CF and VDA decomposition recovers the same
  qualitative claims. If a sensitivity-side reward channel that
  bypasses α-reallocation produces high-V VDA, that would be a
  formal refutation of §5.2.

---

## Version 0.2 — 2026-05-17

### Attack scope this version

A *re-derivation* attack on C3b at $V = 0.75$, not a literature
attack. The detailed derivation is in
[`../derivations/C3--high-V-supremum.md`](../derivations/C3--high-V-supremum.md);
the numerical companion is at
[`../replications/C3--high-V-supremum/`](../replications/C3--high-V-supremum/).
This evidence-dossier entry records only the *literature-facing*
implications of that derivation — i.e. how the new analytic finding
changes the classification of the V0.1 sources, and which new wiki
entries (none, in this run) the attack would draw on if the
derivation suggested a new empirical test.

### Headline derivation result for dossier purposes

The supremum $\sup_{r,v}\,\mathrm{VDA}(r,v;V{=}0.75) = 0.040$
reward units at $(r{=}0.10, v{=}5)$ — eight times the paper's
"$<0.005$ negligible" threshold and twice §4.4's own
"hot zone" boundary. The §4.4/§5.2 categorical wording fails
*internal to the model*. A proposed reformulation that preserves
the paper's scientific point (§7 of the derivation) makes the
V-threshold explicitly $r$-dependent via the closed form
$V_{\text{critical}}(r,N) \approx 1/(1 + r\,(N-1)/\kappa)$ with
$\kappa$ a slowly-varying $O(1)$ density ratio.

### Reclassification of V0.1 sources

The V0.1 source-by-source classifications carried two unresolved
tensions: (i) Stănișor et al. 2013 as *constrain* (potential
refutation), (ii) the Luo & Maunsell 2018 / Maunsell 2015 /
Sridharan 2017 cluster as *support with circularity caveat*. The
re-derivation result clarifies both.

#### Source: [[stanisor2013_v1_value_attention]] (depth: abstract)

- **Reclassification:** "constrain" → potential **support** of
  the *reformulated* C3b, awaiting CR-023 full-depth read.
- **Bears on the claim how:** Stănișor's high-V V1 reward-magnitude
  modulation is precisely the kind of sensitivity-side effect that
  the reformulated §4.4 *predicts* exists in a narrow boundary
  regime $V \in (V_{\text{critical}} - \epsilon, V_{\text{critical}})$.
  Where the original §4.4 forbade such effects categorically, the
  reformulation accommodates them in the residual high-V VDA
  window. So Stănișor is not a refutation candidate any more — it
  is a *predicted* observation under the reformulation.
- **Direction (reformulated C3b):** Supports (predicted observation).
- **Direction (original §4.4):** Still potential refutation candidate
  if the behavioural-d′ probe survives.
- **What the verdict file did with this:** Cited in Version 0.2's
  evidence summary; CR-023 (Stănișor full-depth read) remains
  queued but its interpretive role has shifted from "adjudication
  between confirmation and refutation" to "validation of the
  predicted residual high-V VDA window's magnitude".

#### Source: [[luo_maunsell2018_criterion_sensitivity]] (depth: full)

- **Reclassification:** "support with circularity caveat" → **support
  of reformulated C3b, with the caveat that the stimulus-side
  sensitivity manipulation is now one operationalisation of the
  reformulation's $r$-calibration prescription.**
- **Bears on the claim how:** Luo & Maunsell explicitly vary
  stimulus features (contrast, size) to manipulate sensitivity
  while using reward asymmetry to manipulate criterion. In the
  reformulated language, this is exactly the
  "pre-commit to $r$-calibration" the §5.2 proposed reformulation
  recommends. So Luo & Maunsell is not just a confirming source —
  it is an existing implementation of the experimental design the
  reformulation prescribes.
- **Direction:** Supports (now as both empirical confirmation and
  experimental-design exemplar).
- **What the verdict file did with this:** Cited as the primary
  empirical exemplar in the §7 proposed reformulation block.

#### Source: [[sridharan2017_sc_sensitivity_bias]] (depth: full)

- **Reclassification:** unchanged ("support" of C3b at high V).
- **Bears on the claim how:** Sridharan's re-analysis of four SC
  manipulation studies finds SC contributes primarily to bias at
  high V — consistent with both the original C3b and the
  reformulation. The reformulation does not predict an
  $\alpha$-reallocation effect at high V *above* $V_{\text{critical}}$,
  so Sridharan's "SC → bias-side" finding at $V \approx 0.8$+
  remains a confirming source.
- **Direction:** Supports.
- **What the verdict file did with this:** No change from V0.1.

#### Source: [[maunsell2015_attention_mechanisms]] (depth: full)

- **Reclassification:** unchanged ("support" of C3b at large V).
- **Bears on the claim how:** Maunsell's review-level
  sensitivity/criterion decomposition is consistent with both the
  original C3b and the reformulation. Maunsell does not address
  the boundary regime explicitly.
- **Direction:** Supports.
- **What the verdict file did with this:** No change from V0.1.

### New sources this version (none directly cited; one re-inspected)

#### Source: [[solomon2004_cues_sensitivity]] (depth: re-inspected from CR-001 dossier)

- **Bears on the claim how:** Cued sensitivity at high $V$ — a
  classical demonstration that attention shifts d′ in addition to
  criterion at moderately high validity. Solomon's design crosses
  cueing with sensitivity *but does not vary reward magnitude*.
  Under the proposed reformulation, an extension of Solomon's
  paradigm that adds reward-magnitude manipulation at the same
  high-V level should detect a $d′$ effect in the residual high-V
  VDA window predicted at low $r$ (i.e. when stimulus parameters
  put the observer in a cost-dominant SDT regime). To my knowledge
  no such extension has been published.
- **Direction:** Consistent with reformulation; silent on original
  C3b.
- **Quantitative weight:** Medium-strong as a methodological
  template; null on the C3 specifically.
- **What the verdict file did with this:** Cited in Version 0.2 as
  the candidate paradigm for a future empirical test of the
  reformulation.

### Anchors the §11 sweep produced no new material on

The Version 0.1 §11.1 anchor list was thoroughly worked. This
version's sweep was focused on the model-internal derivation, not
broad literature; new entries surfaced were limited to re-
inspection of Solomon 2004. The Peck 2009 / Serences 2008 stubs
remain unspawned (CR-024); they remain the most informative
candidate stubs for the next literature-attack iteration.

### Spawned this version

- **CR-027** (re-derivation, medium): FAR-corrected closed-form
  $V_{\text{critical}}$. Tightens the analytic substrate;
  resolves the 4-percentage-point gap between simple-approximation
  prediction (≈0.74) and empirical boundary (≈0.78).
- **CR-028** (replication, medium): Variant B sup at $V=0.75$.
  Tests whether the §4.4 categorical wording fails in both
  variants.
- **CR-029** (sensitivity, low): map $V_{\text{critical}}(r, f_0,
  h, N)$ across the secondary sweep. Predicts the "negligible
  VDA" region's shape.
- **CR-030** (literature, low): literature search for cueing
  experiments in the predicted residual high-V VDA window.
  Solomon 2004, Stănișor 2013, Peck 2009, Serences 2008 are the
  candidates.
