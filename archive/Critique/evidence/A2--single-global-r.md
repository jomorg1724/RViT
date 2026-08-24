# Evidence dossier: A2 — the asymmetry ratio r is a single global parameter

Accumulating literature evidence for the A2 verdict
(`Critique/verdicts/A2--single-global-r.md`). Each run appends a dated
`## Version` section. Structure of each entry follows mission §5.5.

**Assumption under attack (A2; paper §2.4, named in §5.5):** the
benefit/cost asymmetry is governed by a **single global ratio** $r>0$,
with benefit scaling $\beta(r)=2r/(r+1)$ applied at the gaining (cued)
location and cost scaling $\gamma(r)=2/(r+1)$ applied at every losing
(uncued) location, the *same* $r$ everywhere, on every trial, for every
feature. The paper itself flags this in §5.5: *"the asymmetry ratio $r$
is a single global parameter; real neural circuits may have
location-specific, feature-specific, or time-varying asymmetries."* It
also concedes in §5.4 that *"empirical measurements of attentional
benefits and costs ... are often asymmetric and depend on task parameters
such as stimulus-onset asynchrony, eccentricity, and set size [8,13,18]."*

**The two readings this dossier must keep separate (decisive for the
verdict).** "Single global $r$" has two very different operational
meanings:

- **(R1) Between-preparation** — $r$ is *one constant per experimental
  preparation*, differing across preparations (stimulus geometry, SOA,
  eccentricity, set size). The paper's primary sweep $r\in[0.1,10]$
  (a 100-fold range) operationalises exactly this reading; the headline
  claims C1–C5 are all *indexed by* $r$. §5.4 explicitly takes R1
  ("could locate specific experimental preparations in the model's
  parameter space").
- **(R2) Within-display homogeneity** — *one $r$ governs all $N$
  locations / all features / the whole trial simultaneously*. The model
  cannot represent per-location $r_i$, per-feature $r$, or time-varying
  $r(t)$. This is the form A2 actually asserts as a simplification.

The literature attack must establish (a) whether the empirical asymmetry
is heterogeneous at all, and (b) under which reading, if either, that
heterogeneity is consequential for C1–C5.

---

## Version 0.1 — 2026-05-24 (run-014, CR-007, literature attack)

The wiki coverage of the gain-modulation / normalization / surround-
suppression cluster is rich (six full-depth primary/review entries bear
directly on $r$). No web fetch was needed (0 of the 2-fetch soft cap).

### Source: [[reynolds_heeger2009_normalization]] (depth: full)

- **Bears on the claim how:** The normalization model is the canonical
  theory of the very mechanisms $\beta,\gamma$ summarise. Its Key claim 3
  and Results: *the same attentional gain* produces **contrast gain**
  (leftward CRF shift) when the stimulus is small relative to the
  receptive field and **response gain** (multiplicative scaling) when the
  stimulus dominates the RF; the regime is set by the ratio of
  stimulus-size to attention-field/RF-size. So the *form and magnitude*
  of the attentional benefit — and, through the shared normalization
  pool, the suppression of competitors — is a function of stimulus/RF
  geometry, not a circuit constant. The "benefit" (enhancement of the
  attended) and "cost" (divisive suppression of the rest) are *coupled
  through one normalization* and their relative size moves with
  configuration.
- **Direction:** **constrains (R2), confirms (R1).** Under R2 it is the
  strongest theoretical statement that $\beta{:}\gamma$ is
  configuration-dependent, hence not one global scalar within a display
  of heterogeneous geometry. Under R1 it is benign: a fixed preparation
  has fixed geometry, hence one effective regime → one $r$, which the
  sweep covers.
- **Quantitative weight:** strong (the field-standard theoretical model;
  cited by the target paper's own §5.4 mechanism list).
- **What the verdict did with this:** cited as the lead theoretical
  ground that $r$ is configuration-dependent (R2) yet preparation-stable
  (R1); the linchpin of the "two readings" split.

### Source: [[treue_martinez_trujillo1999_feature_attention]] (depth: full)

- **Bears on the claim how:** The **feature-similarity-gain model**:
  attentional gain on a neuron is proportional to the *similarity*
  between the cell's preferred feature and the attended feature —
  *enhancement* (≈10–20% in MT) for matched features, *suppression* for
  anti-preferred features, graded in between, applied **globally across
  the visual field**. So in the feature dimension the benefit↔cost map is
  a continuous function of feature similarity, not a single $\beta{:}\gamma$.
- **Direction:** **contradicts (R2).** Direct evidence for
  feature-specific asymmetry: the same display has enhancement at some
  feature channels and suppression at others, simultaneously.
- **Quantitative weight:** strong (founding FBA result, replicated and
  extended; co-cited by the paper's [11–14] mechanism cluster).
- **What the verdict did with this:** cited as the feature-axis
  refutation of within-display single-$r$ (R2), and as the cousin of A8's
  heterogeneous-allocation result (feature-similarity gain *is*
  heterogeneous gain).

### Source: [[maunsell2015_attention_mechanisms]] (depth: full)

- **Bears on the claim how:** The authoritative review. Two load-bearing
  points for A2. (i) **Hierarchy gradient:** firing-rate gain rises V1
  (≈1.08) → V4 (≈1.2–1.5) → IT (>1.5) — the benefit magnitude is
  *area/eccentricity-specific*, so a single display spanning RFs at
  different hierarchical levels has different effective gains. (ii)
  **Mechanism multiplicity (Key claim 9):** "attention" aggregates several
  mechanisms (driven-response gain, shared-variability reduction,
  oscillatory coherence, decision criterion) "each with its own task
  dependence" — i.e. benefit and cost are not a single coupled scalar but
  a family of partially independent effects. Claim 12: temporal precision
  tracks task-relevant intervals (the time axis).
- **Direction:** **contradicts (R2).** The single-$r$ coupling of one
  benefit to one cost is a strong simplification of a documented
  multi-mechanism, hierarchy-graded, task-dependent reality.
- **Quantitative weight:** strong (field-defining review; the paper's
  "dissociable mechanisms ... independently modulated [11–14]" sentence
  is this literature).
- **What the verdict did with this:** cited as the review-level statement
  that the benefit:cost relation is neither single nor uniform; anchors
  the "named limitation is real" half of the verdict.

### Source: [[sani2017_temporal_v4_gain]] (depth: full)

- **Bears on the claim how:** Within a *single trial*, V4 attentional
  modulation passes through qualitatively different gain regimes — an
  early baseline-shift contrast gain, a middle response gain (peak
  ≈150 ms), and a late contrast-gain resurgence. Not merely the magnitude
  but the *form* of the gain is time-varying.
- **Direction:** **contradicts (R2), time axis.** Direct evidence that
  the effective $\beta{:}\gamma$ is non-stationary within a trial.
- **Quantitative weight:** medium-strong (single primate study, but
  mechanistically explicit; converges with Ghose & Maunsell).
- **What the verdict did with this:** cited for the "time-varying"
  clause of §5.5; together with Ghose & Maunsell establishes the temporal
  heterogeneity of $r$.

### Source: [[ghose_maunsell2002_task_timing]] (depth: full)

- **Bears on the claim how:** V4 attentional-modulation *magnitude* tracks
  the within-trial event-probability schedule; the **same neuron** shows
  different temporal modulation profiles under different schedules; the
  signal is re-learned online within tens of trials. Key claim 6:
  "attention is *when* as well as where and what, and the three axes are
  not separable in V4 firing rates."
- **Direction:** **contradicts (R2), time axis.** The benefit magnitude
  (hence $r$) is a learned function of within-trial time.
- **Quantitative weight:** medium-strong (canonical Nature result; two
  animals, robust population effect).
- **What the verdict did with this:** cited alongside Sani 2017 for the
  temporal non-stationarity of $r$.

### Source: [[reynolds_chelazzi2004_attentional_modulation]] (depth: full)

- **Bears on the claim how:** Catalogues the contrast-dependence of the
  gain (largest in the CRF dynamic range, ~none at saturation) and the
  selectivity-dependence in the two-stimuli-in-one-RF regime (attention to
  the preferred stimulus elevates, to the poor stimulus suppresses,
  scaling with the cell's selectivity). Also supplies a *fairness* anchor:
  "attention is worth ~50% effective contrast," a **stable** quantity
  across V4/MT/labs.
- **Direction:** **constrains (R2), with a confirming caveat.** The
  benefit depends on stimulus contrast and on the cell's selectivity for
  the competing stimuli — so within a heterogeneous display $r$ is not
  uniform; *but* the ~50%-contrast equivalence shows there is a stable
  summary statistic for the spatial-attention benefit in the dynamic
  range, which is what makes R1 (a per-preparation $r$) a reasonable
  idealisation.
- **Quantitative weight:** strong (the field's standard synthesis of
  single-unit attention).
- **What the verdict did with this:** cited for contrast/selectivity
  dependence (R2) and for the stable-summary point that licenses R1.

### Source: [[mcadams_maunsell1999_v4_tuning]] (depth: full)

- **Bears on the claim how:** Two-edged. **Confirming:** within a V4 cell,
  attention is a near-pure multiplicative gain (~26%) that is uniform
  across orientations and preserves tuning width and preferred
  orientation — a "label-preserving" single multiplier, which is exactly
  the kind of object the paper's per-location $\beta,\gamma$ idealise.
  **Contradicting (R2):** V4 gain ≈26% vs V1 gain ≈8% — a *threefold*
  area/eccentricity difference under identical task and stimulus; and the
  Critique §6 notes the population statistic "obscures genuine
  heterogeneity ... not every V4 cell shows multiplicative scaling, and
  some show ... additive or non-uniform modulations."
- **Direction:** **constrains (R2), partially supports the
  per-location-scalar idealisation.** Within a cell/location a single gain
  is a good description; across locations/areas it varies threefold and is
  heterogeneous cell-to-cell.
- **Quantitative weight:** strong (canonical single-unit gain result).
- **What the verdict did with this:** cited as the most explicit
  "single multiplier *per location*, but heterogeneous *across*
  locations" datum — the empirical shape of R2's violation.

### Source: [[carrasco2011_visual_attention_25y]] (depth: full)

- **Bears on the claim how:** Psychophysics synthesis. The contrast-gain
  vs response-gain regime depends on the attention-field/stimulus-size
  ratio (Key claims 5–6); endogenous vs exogenous attention have different
  time courses (the time axis). Most strikingly (Yeshurun & Carrasco
  texture-segmentation), attention **helps at some eccentricities and
  hurts at others** — the *sign* of the perceptual effect flips with
  eccentricity/spatial scale. Threshold shifts 10–30%.
- **Direction:** **contradicts (R2), location/eccentricity axis — and
  the strongest form of it.** A sign reversal is heterogeneity beyond a
  changing scalar; in the model's terms it is not even "small $r$ vs large
  $r$" but a regime where the "benefit" mechanism degrades performance.
- **Quantitative weight:** strong (the field's 25-year psychophysics
  review; the paper's ref [1]-class source).
- **What the verdict did with this:** cited as the eccentricity-axis
  refutation of R2, and as empirical grounding for the §5.4 [8,13,18]
  task-parameter-dependence the paper itself concedes.

### Source: [[luo_maunsell2018_criterion_sensitivity]] (depth: full)

- **Bears on the claim how:** Sensitivity (the perceptual *benefit* the
  paper routes through $\beta$ on $d'$) and criterion are dissociable and
  have *different substrates* (visual cortex carries sensitivity; LPFC
  carries both). Bears obliquely on A2: the "benefit" and the decisional
  side are not one coupled quantity — reinforcing that the single scalar
  $r$ that ties one benefit to one cost is an idealisation of a
  multi-substrate reality.
- **Direction:** **constrains (weakly).** More central to A1/A6 (the
  decomposition) than to A2's gain-asymmetry; included because the
  benefit-vs-cost coupling is the heart of $r$.
- **Quantitative weight:** medium (primary LPFC study; tangential to the
  *spatial gain ratio* specifically).
- **What the verdict did with this:** cited as supporting context for the
  "benefit and cost need not be one ratio" point; flagged as the bridge to
  A1/A6.

### Sources consulted and judged not load-bearing for A2 (sweep hygiene)

- [[reynolds1999_competitive_v2_v4]], [[moran_desimone1985_selective_attention]],
  [[desimone_duncan1995_biased_competition]] — biased-competition / zero-sum
  reallocation; they ground the *cost* ($\gamma$) side and the surround-
  suppression regime $r<1$, but say nothing new about whether $r$ is
  *single*; cited only in passing.
- [[moore_armstrong2003_fef_microstim]] — FEF microstimulation as a causal
  source of the *benefit* ($\beta$) side (top-down feedback); confirms the
  mechanism the paper attributes to $\beta$ but does not bear on its
  uniformity. Noted, not load-bearing for the heterogeneity question.
- [[cohen_maunsell2009_correlations]] — noise-correlation channel; central
  to A1 (independence), tangential to A2.
- [[sridharan2017_sc_sensitivity_bias]], [[muller_findlay1987_sensitivity_criterion]]
  — SDT sensitivity/criterion decomposition; A1/A6-adjacent.
- Value-source cluster ([[failing_theeuwes2018_selection_history]],
  [[hickey2010_reward_salience_acc]], [[stanisor2013_v1_value_attention]]) and the
  dopamine/RPE/basal-ganglia entries — concern *where value comes from*,
  not the *form of the gain asymmetry*; **unrelated on inspection** for A2.
- Priority-map / LIP / parietal entries
  ([[bisley_goldberg2010_parietal_priority]], [[bisley_mirpour2019_priority_map]],
  [[rust_cohen2022_priority_coding]]) — set *where* attention goes, not the
  benefit:cost ratio at a location; unrelated to the $r$-uniformity
  question.

### Net assessment (carried into the verdict)

The empirical premise of A2 is **decisively false** under reading R2:
the benefit:cost asymmetry is location-/eccentricity-specific
(Reynolds-Heeger; McAdams-Maunsell V1-vs-V4 threefold gradient;
Carrasco/Yeshurun sign reversal), feature-specific
(Treue-Martínez-Trujillo feature-similarity gain), and time-varying
(Sani 2017; Ghose-Maunsell 2002) — and the paper concedes this in §5.4
and §5.5. Under reading R1 the assumption is **benign and in fact
methodologically appropriate**: the paper's 100-fold $r$-sweep is exactly
how one handles a per-preparation $r$, and §5.4 takes R1 explicitly.
What the literature attack *cannot* settle on its own is whether R2
heterogeneity (genuine, well-characterised) *materially shifts* C1–C5 —
that is a re-derivation question routed to **CR-048** (A2×A8
interaction), the designated second vector.
