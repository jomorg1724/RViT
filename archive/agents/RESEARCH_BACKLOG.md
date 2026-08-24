---
type: backlog
status: active
prompt_version: 0.2
created: 2026-05-17
last_updated_by: skeptical-reviewer
last_updated_at: 2026-05-25
next_id_counter: 58
last_owner_intervention: 2026-05-17 — initial bootstrap. Twelve seed tasks created, one per headline claim (C1–C5) and one per load-bearing assumption (A1–A7). The agent should pick CR-001 (attack C2 by re-derivation) as the very first run per mission §8.6. After CR-001 completes, the agent owns this file; subsequent owner edits will be marked here with a fresh `last_owner_intervention` line.
---

# VDA Skeptical-Reviewer — Research Backlog

This file is the queue of attack tasks the reviewer agent draws from.
After the first non-bootstrap run, the agent owns this file; the
owner intervenes only by editing it directly (escalating priorities,
killing threads, adding new claim-level tasks).

See `agents/skeptical_reviewer_prompt.md` §3 and §8 for the attack
taxonomy and the loop semantics. Tasks are ordered roughly by
*priority then prereq depth*; the agent picks the top unblocked
queued task by default, with CR-001 as the explicit first pick per
mission §8.6.

All attacks operate against the target paper at
`Critique/source/main.pdf`. Claim and assumption IDs (C1–C5, A1–A7)
are defined in mission §2.6 and §2.7.

---

## Tasks

```yaml
- id: CR-001
  claim_id: C2
  attack_vector: re-derivation
  task: |
    Re-derive the VDA-benefit-vs-r relationship from the
    independent-benefit-and-cost model (mission §2.4) and verify
    that it is non-monotonic in r with a peak near r ≈ 0.3 at the
    cited reference regime (V=0.5, v=5, N=4, d'_max=2.0, f_0=0.5,
    h(a) = sqrt(a)). The paper's Figure 4 is the empirical target.
    Show every algebraic step in LaTeX under
    Critique/derivations/C2--non-monotonic-vda.md. Independently
    locate the value of r at which dR(P1)/dr − dR(P2)/dr changes
    sign and compare to the paper's r ≈ 0.3.

    First attack on C2 because it is the paper's most distinctive
    finding — confirming or breaking it sets the tone for the
    whole critique. Re-derivation (not replication) chosen because
    the math is tractable and a re-derivation can surface skipped
    steps that a black-box replication would miss.
  status: done
  priority: high
  prereqs: []
  notes: |
    Bootstrap-seeded 2026-05-17. The paper's Eqs. (5)–(8) and (12)
    plus the Eq. (9) reward decomposition are the substrate.
    Expected outcome: re-derivation reproduces the qualitative
    non-monotonicity but may surface that the peak location is
    sensitive to f_0 and h() — that sensitivity is itself a
    verdict-shaping observation. Spawn a follow-up
    (replication-attack) for the actual numerical Figure-4
    reproduction if the analytic derivation is informative but
    not numerically conclusive.
    [2026-05-17 run start] Marked in_progress at start of first
    scheduled run.
    [2026-05-17 run done] Re-derivation succeeded. Proved the
    two-limit theorem (VDA→0 at both r→0 and r→∞) analytically;
    identified closed-form escape thresholds r†(v) =
    G_u/[(N-1)G_c(v)] explaining the non-monotonicity mechanism.
    Numerical sweep corroborated to within sub-grid resolution:
    peak VDA = 0.0774 at r=0.398 (paper: ~0.080 at r≈0.3, one
    log-grid step apart). One expository gap surfaced in paper
    §4.3 (closed-form thresholds not stated) but no error.
    Verdict label: WEAKLY-SUPPORTED. Spawned CR-013 (high-res
    Figure 4 replication), CR-014 (peak-location sensitivity
    prediction), CR-015 (literature deepening into
    maunsell2015_attention_mechanisms for A2), CR-016 (consider
    maunsell_treue2006 stub for the wiki).
  origin: seed
  touched: 2026-05-17T12:30:00Z

- id: CR-002
  claim_id: C1
  attack_vector: sensitivity
  task: |
    Identify the parameter combination in the swept space (mission
    §2.6 C1: criterion fraction 0.60–0.96) where the criterion
    fraction is closest to 0.60. Determine whether any plausible
    extrapolation just outside the swept space would push the
    criterion fraction below 0.50 — i.e., whether the agent can
    construct a scenario the paper's sweep didn't cover where
    attention reallocation, not criterion, would dominate value
    encoding. Document the construction (or its failure) under
    Critique/evidence/C1--criterion-fraction-floor.md.
  status: done
  priority: high
  prereqs: []
  notes: |
    Bootstrap-seeded. The paper's strongest claim is that criterion
    "always" dominates; the agent's job here is to find the
    boundary. A sensitivity attack is cheaper than a full
    replication and is the natural first move.
    [2026-05-17 run start, run-003] Marked in_progress at start of
    third scheduled run. Attack plan: (Phase A) replicate paper's
    primary sweep over (r ∈ [0.1,10], 21 log-pts) × (V ∈ [1/N,1],
    21 pts) × (v ∈ {1..5}) × variant ∈ {A,B}, locate argmin CF and
    verify 0.60–0.96 range; (Phase B) extrapolate at the argmin's
    (V*, v*) into r > 10, f_0 < 0.1, h = a^3, a^4, larger d'_max,
    larger N, to check whether CF crosses 0.50.
    [2026-05-17 run done] Phase A REFUTED the categorical claim:
    swept-space CF range is [0.30, 1.00], not [0.60, 0.96]. Variant
    A argmin CF=0.559 at (r=10, V=0.55, v=1); variant B argmin
    CF=0.304 at (r=10, V=0.25, v=4). 13.4% of rows below 0.60, 4.0%
    below 0.50. Reference-point validation: code matches paper at
    r=1.0 (0.728 vs 0.73) and r=3.2 (0.642 vs 0.64) to 0.002 of CF;
    DISAGREES at r=0.3 (mine 0.854, paper text 0.96) — but paper's
    own Figure 2 visual reads ~0.85, consistent with mine. Likely
    manuscript transcription error. Phase B at V=1/N anchor: only
    pushing r > 10 takes CF further down (asymptote ~0.26 at
    r=∞); other axes (f_0 < 0.1, h ∈ {a^3, a^4}, N > 4, v > 5,
    combos) push CF UP. So the categorical-floor failure is
    interior to the sweep, not an extrapolation artefact. Verdict
    label: CONTESTED (mission §3.1). Substantive spirit
    ("criterion typically dominates") survives — median CF ≈ 0.76
    in both variants; 80%+ of rows have CF ≥ 0.50; §5.1
    theoretical argument unaffected. Proposed weaker
    reformulation drafted in verdict file. Spawned CR-020 (C3
    literature attack on narrow-regime), CR-021 (V=1/N
    degeneracy derivation), CR-022 (r=0.3 reference-point
    clarification note).
  origin: seed
  touched: 2026-05-17T15:50:00Z

- id: CR-003
  claim_id: C3
  attack_vector: literature
  task: |
    [MERGED INTO CR-020 at start of run-004; see CR-020 notes for
    execution log. The seed-task CR-003 and the spawned-task CR-020
    were noted as duplicates in the re-prioritisation note after
    CR-002; this run executed them as one.]
    The paper claims VDA is confined to low V, high v, moderate
    r (mission §2.6 C3). Survey research_db/ for empirical
    primate-attention studies whose stimulus paradigm sits in the
    "high V" regime the paper predicts should NOT show VDA, and
    check whether those studies reported VDA effects anyway. If
    yes, the claim is in tension with the literature and the
    verdict moves to CONTESTED. Write the evidence dossier at
    Critique/evidence/C3--narrow-regime.md, citing each wiki
    entry by id with §-pointers.
  status: abandoned
  priority: high
  prereqs: []
  notes: |
    Bootstrap-seeded. Candidate wiki entries to start with:
    failing_theeuwes2018_selection_history, hickey2010_reward_salience_acc,
    mcadams_maunsell1999_reliability, srinath2021_attention_information_flow,
    babayan_uchida_gershman2018_belief_states_dopamine,
    glimcher2011_dopamine_rpe. These are the agent's first-cut
    candidates; the §11 wiki sweep should turn up more.
    [2026-05-17 run-004] Abandoned: merged into CR-020 (which was
    spawned by CR-002 with overlapping scope). CR-020 is the
    canonical execution. See CR-020's notes for the run-004
    summary and the Critique/verdicts/C3--narrow-regime.md
    verdict file.
  origin: seed
  touched: 2026-05-17T16:30:00Z

- id: CR-004
  claim_id: C4
  attack_vector: re-derivation
  task: |
    The paper's §4.5 argues inverted attention (α < 1/N) is never
    optimal. Re-derive: given v ≥ 1, V ≥ 1/N, and the β/γ scaling
    in §2.4 of this mission, show that ∂E[R]/∂α evaluated at
    α = 1/N is non-negative for all r > 0. If the derivation
    succeeds, the verdict is CONFIRMED-CONDITIONAL on the assumption
    set (A1–A7). If the derivation fails, identify the parameter
    region where it could fail and elevate the verdict to CONTESTED.
    Write the derivation at Critique/derivations/C4--no-inversion.md.
  status: done
  priority: medium
  prereqs: []
  notes: |
    Bootstrap-seeded. This is a "never" claim — categorical claims
    are usually easier to refute than confirm; a single
    counterexample in the swept space would refute. The
    derivation should reveal whether the categorical statement is
    a theorem or an empirical regularity.
    [2026-05-18 run-006 start] Marked in_progress at start of sixth
    scheduled run. Approach: derive the one-sided boundary
    derivative analytically, then numerical Step A (closed-form
    threshold across grid), Step B (full E[R](α) at adversarial
    cells), Step C (anti-cue regime test + CR-019 V=1/N
    refinement).
    [2026-05-18 run-006 done] Re-derivation succeeded with
    substantive refinement. The empirical C4 holds (zero
    inversions across 4,410 primary-sweep rows; independently
    corroborated by CR-002 phase-A data). The theoretical
    justification is REFINED: paper's "regardless of r" wording
    is wrong as a local statement (~49% of cells have local
    boundary derivative changing sign in the swept r range);
    correct mechanism is the location-count asymmetry combined
    with the value-weight inequality w_c ≥ w_u (equivalent to
    V ≥ 1/[(N-1)v + 1], which for v ≥ 1 simplifies to V ≥ 1/N).
    Derived closed-form inversion threshold r*_inv(V,v,N,CR) =
    (N-1) A_0 / B_0; at corner (V=1/N, v=1) gives r*_inv = 1
    exactly. CR-019 resolved in the negative: C4's wording does
    not need V > 1/N because right-branch wins strictly at r > 1
    by location-count asymmetry; the CR-014 α=0.02 was the
    left-branch local maximum. Anti-cue counterexample
    (V=0.25, v=1, N=2): α*_global = 0.180 at r=1 dropping to
    0.020 at r=10 — C4 fails OUTSIDE the conditional but the
    primary sweep is INSIDE the conditional, so the empirical
    claim survives. Verdict label: WEAKLY-SUPPORTED. Spawned
    CR-031 (literature attack), CR-032 (Wang & Theeuwes / Geng
    stubs), CR-033 (β/γ kink sensitivity), CR-034 (anti-cue at
    N=4 derivation extension).
  origin: seed
  touched: 2026-05-18T12:00:00Z

- id: CR-005
  claim_id: C5
  attack_vector: replication
  task: |
    Reproduce the paper's Appendix A claim: at r = 1, the
    independent-benefit-and-cost model reduces exactly to the
    symmetric special case (β = γ = 1) at machine precision on
    210 matched parameter combinations. Implement a minimal
    version of both formulations under
    Critique/replications/C5--symmetric-recovery/, run them, and
    check max(|α*_independent − α*_symmetric|) and
    max(|R*_independent − R*_symmetric|). The paper reports max
    diff 0.0; the agent should reproduce or refute that.
  status: done
  priority: medium
  prereqs: []
  notes: |
    Bootstrap-seeded. This is a self-consistency check the paper
    already ran — confirming attack rather than falsifying attack.
    Useful because it (a) builds the substrate the agent will
    later use for assumption sweeps (A3, A5, A6), and (b) catches
    any reproducibility failure in the paper's own code if
    code is available. If no code is available, the replication
    is implemented from the paper's equations directly.
    [2026-05-20 run-008 start] Marked in_progress at start of the
    eighth scheduled run (prompt v0.2). Picked over CR-036 (the
    run-007-recommended substantive descendant) and over the stale
    high-priority CR-013 (a third C2 vector — C2 is already
    CONFIRMED-UNDER-ATTACK, so CR-013 fails the §3.3 "OPEN/WEAKLY-
    SUPPORTED verdict" selection criterion). Rationale for CR-005:
    C5 is the ONLY untouched headline claim (closes per-headline-
    claim coverage); the replication builds the symmetric+asymmetric
    model substrate that CR-036 and the A3/A5/A6 sweeps reuse, so
    it is a natural prerequisite-in-spirit for CR-036; and it is
    bounded enough for the 10–20 min budget, de-risking the heavier
    CR-036 simplex optimisation. Override documented in the run-008
    conversation page.
    [2026-05-20 run-008 done] DONE. Replication at
    Critique/replications/C5--symmetric-recovery/ reproduced C5
    EXACTLY: d' arrays bit-identical (np.array_equal True),
    max|Δα*| = max|ΔR*| = 0.0 across all 210 combos (V×v×variant at
    r=1, N=4, d'_max=2.0, f_0=0.5, √). Traced the exactness to
    Sterbenz's lemma — β(1)=γ(1)=1 exactly, and every swept
    x=d'_max·f(·) ∈ [1.0,2.0] lies inside the Sterbenz band
    [d'_base/2, 2·d'_base] = [0.75,3.0], so a+(x−a)=x bit-for-bit.
    Robustness probe: the literal "0.0" is config-specific (4/15
    (f_0,d'_max) configs drift ~1 ulp once x leaves the band; low
    f_0 is the culprit) — "machine precision" is the universal
    statement, "0.0" the validation-config one. Continuity probe:
    max|ΔR*| linear in |r−1| (slope ≈0.084), exactly 0 at r=1 — the
    symmetric case is the smooth centre, not a knife-edge. Verdict
    C5 (none) → WEAKLY-SUPPORTED (one vector, first touch). Spawned
    CR-038 (re-derivation, the second vector for elevation) and
    CR-039 (owner-facing config-specificity doc note). Built the
    symmetric+asymmetric P1 optimiser CR-036 / A3 / A5 reuse.
  origin: seed
  touched: 2026-05-21T02:19:24Z

- id: CR-006
  claim_id: A1
  attack_vector: literature
  task: |
    Assumption A1: per-location SDT decisions are independent.
    Survey the SDT and primate-attention literature for evidence
    on response correlations across spatial locations in change-
    detection / cued-search tasks. If empirical work shows
    substantial cross-location response correlations, the
    independence assumption is load-bearing for the policy
    decomposition (P1–P4) and the verdict for A1 moves to
    WEAKLY-SUPPORTED-CONDITIONAL or CONTESTED. Document at
    Critique/evidence/A1--independence.md.
  status: done
  priority: medium
  prereqs: []
  notes: |
    Bootstrap-seeded. The paper itself acknowledges this in §5.5
    as a limitation. The agent's job is to quantify how
    consequential the limitation is, not to repeat that it
    exists. Cohen & Maunsell 2009 (cohen_maunsell2009_correlations)
    is the canonical wiki entry to start with.
    [2026-05-24 run-016 start] Marked in_progress at start of the
    sixteenth scheduled run. Picked per mission §3.3 (highest-
    priority OPEN verdict; no WEAKLY-SUPPORTED verdicts remain) and
    the explicit run-015 recommendation: A1 is the paper's
    first-named §5.5 limitation, richest wiki coverage
    (cohen_maunsell2009_correlations, mcadams_maunsell1999_reliability),
    and the assumption the CR-048 per-slot gradient explicitly
    presumed. Attack plan: (1) verbatim A1 framing already read —
    §2.1 independent per-location SDT decisions + Eq.(9) P_no-fa
    PRODUCT factorisation, and §5.5 "upper bound on VDA benefit"
    self-characterisation; (2) §11 wiki sweep over the noise-
    correlation / interneuronal-correlation / pooling / SDT cluster
    + §11.1 anchors — is independence empirically tenable, and which
    direction do cross-location correlations push?; (3) classify
    each entry supports/contradicts/constrains; (4) write the
    evidence dossier + first A1 verdict. Literature (not
    re-derivation) chosen because A1 is fundamentally an *empirical*
    claim about real observers' response structure; the sign of the
    correlation effect on VDA (testing the "upper bound" assertion)
    is a re-derivation question for the designated second vector.
    [2026-05-24 run-016 done] DONE. Verdict A1 (none) → WEAKLY-SUPPORTED
    (first touch, one vector: literature;
    Critique/verdicts/A1--independence.md V0.1 +
    Critique/evidence/A1--independence.md V0.1). Read 8 full-depth wiki
    entries; 0 web fetches; no new stub (all present → no audit.py).
    PIVOTAL MOVE: separated I-dec (Eq. 9 product needs decision-level FA
    independence — load-bearing for C1's criterion fraction) from I-neur
    (per-location d' as a marginal vs. cortex's
    d'^2 ∝ (Δμ)ᵀ Σ⁻¹ (Δμ)). FINDINGS: (1) premise empirically FALSE under
    I-neur and in the paper's own paradigm — cohen_maunsell2009 (macaque
    orientation change-detection w/ peripheral cue) finds r_SC≈0.2 and that
    >80% of attention's behavioural benefit comes from correlation
    REDUCTION, <20% from rate gain; ruff_cohen2016 (within-down/between-up
    sign reversal) + srinath2021 (~2/3 supra-pairwise shared-variance
    amplification) show the omitted object is a structured, attention-
    modulated Σ. (2) Independence is the Eq. 9 product; closed form via
    Slepian's inequality: equicorrelated-Gaussian FAs give
    P_no-fa = Φ_N(c;R_ρ) ≥ Π(1-FAR_i) for ρ>0 (monotone), so the
    independent corner MAXIMISES the FA penalty → C1's criterion fraction
    sits at a boundary in correlation space. (3) Two-tool taxonomy
    (criterion vs d'-reallocation) OMITS the empirically dominant lever
    (decorrelation), which the scalar d'(α) conflates with marginal gain
    (mcadams1999: real, multiplicative, Fano-flat) — so "criterion captures
    60–96%" is a WITHIN-MODEL decomposition, not a claim about cortex's
    mechanism inventory. FAIR LEGS: A1 is the field-standard behavioural
    idealisation (hawkins1990) and the d' tool is real; ernst_banks2002 §6
    gives the optimal-pooling theorem (correlated noise breaks the
    independent rule), tying §5.5's "single global response" to A6/CR-011.
    (4) The §5.5 "upper bound on VDA" self-characterisation is UNDERIVED and
    SIGN-AMBIGUOUS — neural-decorrelation reading: value-directed
    decorrelation could make real VDA EXCEED the model's ("upper bound"
    wrong); decision-aggregation reading: could go either way. Label
    WEAKLY-SUPPORTED (mission §6: one vector cannot elevate; NOT CONTESTED
    because no headline number shifted this run — premise shown false but
    not yet consequential, mirroring A2/run-014). §11 sweep: cohen_maunsell2009,
    ruff_cohen2016, srinath2021, mcadams_maunsell1999_reliability,
    hawkins1990, ernst_banks2002, luo_maunsell2018, reynolds_heeger2009
    cited; coalition_resource_competition + competition_emergent_predictive_coding
    (concepts) cited for the PRISM bridge; dopamine/RPE/priority-map anchors
    unrelated on inspection; rust_cohen2022_priority_coding surfaced but not
    read (tangential). Spawned CR-052 (A1 second vector, re-derivation —
    the decisive sign test on "upper bound on VDA") and CR-053 (literature:
    is decorrelation value-directed?). The decorrelation-is-value-directed
    question is a genuine wiki gap (no entry addresses reward-modulation of
    noise correlations) → CR-053 likely needs a web fetch.
  origin: seed
  touched: 2026-05-24T21:40:00Z

- id: CR-007
  claim_id: A2
  attack_vector: literature
  task: |
    Assumption A2: a single global asymmetry ratio r. Survey
    research_db/ for primate-physiology evidence on location-,
    feature-, or time-specific attentional gain modulation vs.
    surround suppression — i.e., evidence that r is not a single
    scalar. The Reynolds & Heeger (2009) normalization model is
    the obvious entry point. If the literature supports
    location- or feature-specific asymmetries that would
    materially shift the optimal policy, the verdict moves.
    Document at Critique/evidence/A2--single-global-r.md.
  status: done
  priority: medium
  prereqs: []
  notes: |
    Bootstrap-seeded. The agent should examine
    reynolds_heeger2009_normalization,
    mcadams_maunsell1999_reliability,
    srinath2021_attention_information_flow,
    cohen_maunsell2009_correlations, and the Maunsell-lab
    references cited in the paper (refs 3, 4, 11–14, 16).
    [2026-05-24 run-014 start] Marked in_progress at start of the
    fourteenth scheduled run. Picked per mission §3.3 (A2 is the
    connective frontier — the CR-045/run-013 re-derivation proved
    A8's homogeneity-optimality is A2-conditional) and the explicit
    run-013 recommendation. A2 is the cousin of A3 (CONTESTED) and
    A8 (CONFIRMED-CONDITIONAL): both are heterogeneity assumptions.
    Attack plan: (1) read paper §2.4/§5.4/§5.5 to nail the verbatim
    single-global-r framing and what (if anything) the Limitations
    say about location/feature/time-specific asymmetries; (2) §11
    wiki sweep over the gain-modulation / surround-suppression /
    normalization cluster — is the benefit:cost ratio a single
    scalar empirically, or location/feature/time-specific?; (3)
    classify each entry supports/contradicts/constrains; (4) write
    the evidence dossier + first A2 verdict. Literature (not
    re-derivation) chosen because A2 is fundamentally an *empirical*
    claim about real neural circuits; CR-048 (the A2×A8 analytic
    half) is the designated second vector for a later run.
    [2026-05-24 run-014 done] DONE. Verdict A2 (none) → WEAKLY-SUPPORTED
    (first touch, one vector: literature;
    Critique/verdicts/A2--single-global-r.md V0.1 +
    Critique/evidence/A2--single-global-r.md V0.1). Read 8 full-depth
    wiki entries; 0 web fetches; no new stub (all present → no audit.py).
    PIVOTAL MOVE: separated two readings of "single global r" — (R1)
    between-preparation (r a per-preparation constant, varying across
    preparations: this is what the 100-fold r-sweep operationalises, and
    §5.4 explicitly adopts it) vs (R2) within-display homogeneity (one r
    for all locations/features/time at once: what the model assumes).
    FINDING: the premise is DECISIVELY FALSE under R2 — the benefit:cost
    asymmetry is location/eccentricity-specific (reynolds_heeger2009 gain
    form set by stim/RF ratio; mcadams_maunsell1999 V1≈8% vs V4≈26% 3×
    gradient; carrasco2011 attention helps-then-hurts across eccentricity,
    a SIGN reversal), feature-specific (treue_martinez_trujillo1999
    feature-similarity gain enhancement→suppression continuum), and
    time-varying (sani2017 gain form cycles contrast→response→contrast
    within a trial; ghose_maunsell2002 magnitude tracks within-trial event
    probability) — and the paper concedes this in §5.4 ([8,13,18]) and
    §5.5. BUT under R1 the simplification is BENIGN and methodologically
    correct: fixed preparation → fixed geometry → one effective regime →
    one r; the sweep covers it; C1–C5 are r-indexed (reynolds_chelazzi2004
    stable ~50%-effective-contrast + mcadams within-cell label-preserving
    single multiplier are positive evidence a per-preparation scalar is
    reasonable). The R2-consequence for C1–C5 is the genuine open question
    (first-pass: C2 REFRAMES vs r_cued; C4 likely ROBUST — its proof rests
    on r-independent location-count geometry; C1 could deepen its
    already-contested corner) — a RE-DERIVATION question, routed to CR-048.
    Label WEAKLY-SUPPORTED (mission §3.1/§6: one vector cannot elevate; not
    CONTESTED because no attack SHIFTED a headline claim — R2 shown
    motivated, not yet consequential). Referee theme: A2 is the MOST
    R1-defensible of the paper's named/identified simplifications (methodology
    discharges its dominant reading) — contrast A3 (named, CONTESTED) and A8
    (unnamed, CONFIRMED-CONDITIONAL); residual A2 risk = the A2×A8 coupling
    CR-045 exposed. §11 sweep: reynolds_heeger2009, treue_martinez_trujillo1999,
    maunsell2015, sani2017, ghose_maunsell2002, carrasco2011,
    reynolds_chelazzi2004, mcadams_maunsell1999_v4_tuning cited; luo_maunsell2018
    (benefit/cost distinct substrates, bridge to A1/A6) cited; value-source /
    priority-map / dopamine anchors unrelated on inspection. Spawned CR-049
    (C2-reframing replication: VDA vs r_cued under heterogeneous uncued r_i),
    CR-050 (sign-reversal/β<0 note: model's r>0 excludes the
    attention-impairs-segmentation regime). Promoted CR-048 to the designated
    A2 second vector / recommended next pick.
  origin: seed
  touched: 2026-05-24T05:58:00Z

- id: CR-008
  claim_id: A3
  attack_vector: replication
  task: |
    Assumption A3: β + γ = 2 (additive conservation). The paper
    notes in §5.5 that alternative constraints (e.g. β·γ = 1)
    would give different results but does not run them. Implement
    a minimal model that replaces β + γ = 2 with β·γ = 1
    (multiplicative conservation), re-run the headline parameter
    combination (V=0.5, v=5, N=4, h=sqrt), and report how much
    the headline numbers (criterion fraction, VDA peak location,
    VDA peak magnitude) shift. Document under
    Critique/replications/A3--multiplicative-conservation/. If
    the qualitative findings (non-monotonic VDA, narrow regime,
    no inversion) hold under both conservation rules, the
    verdict for A3 is WEAKLY-SUPPORTED. If they break, the
    verdict moves to CONTESTED and C2/C3/C4 may need revisiting.
  status: done
  priority: high
  prereqs: [CR-005]
  notes: |
    Bootstrap-seeded. Depends on CR-005 because that task builds
    the replication substrate. Crucial because it directly tests
    whether the headline claims are artifacts of one specific
    parameterization choice — i.e., whether the paper's
    qualitative findings are robust beyond the additive
    conservation rule it studied.
    [2026-05-22 run-010] PROMOTED medium → high and re-scoped as the
    DESIGNATED SECOND VECTOR for the A3 verdict (CR-040/run-010 was the
    first, a re-derivation that left A3 WEAKLY-SUPPORTED). CR-040 showed
    on the V=0.5,v=5 reference slice that the βγ=1 swap preserves all
    three §5.5-named findings BUT erodes criterion dominance to CF=0.507
    (only 0.007 above 0.5 at r=10). The decisive open question: does
    criterion dominance (CF>0.5) BREAK under βγ=1 in the low-V/high-v/
    variant-B cells where C1 is ALREADY CONTESTED under additive
    (run-003 phase-A found CF→0.304 there)? Re-scope this task: run the
    multiplicative (β=√r,γ=1/√r) sweep RESTRICTED to the run-003 cells
    with additive CF<0.60 (read them from
    Critique/replications/C1--criterion-fraction-floor/output/results.json),
    and report whether any cell has CF_mult<0.5. If yes → A3 elevates to
    CONTESTED (criterion-dominance conjunct fails) AND the §6 categorical
    "criterion dominance" needs scoping. If no → A3 → CONFIRMED-CONDITIONAL
    (robust within the paper's grid, two vectors). Reuse the swappable
    β/γ map already built in
    Critique/replications/A3--multiplicative-conservation/run.py
    (beta_gamma_multiplicative). This is now the recommended next pick.
    [2026-05-24 run-011 start] Marked in_progress at start of the
    eleventh scheduled run. Picked per mission §3.3 (highest-priority
    WEAKLY-SUPPORTED verdict, A3, prereq CR-005 done) and the explicit
    run-010 recommendation. Attack plan: (1) load run-003 phase_A
    rows from C1 results.json; select valid (total_gain>1e-4) cells
    with additive CF<0.60; (2) re-implement the model at run-003's
    exact config (A&S Φ, Δc=0.05, Δα=0.02+1/N, N=4, d'_max=2, f0=0.5,
    √), cross-check recomputed additive CF vs stored; (3) compute
    CF_mult (β=√r, γ=1/√r) on the same cells; (4) decompose honestly —
    NEW constraint-attributable flips (CF_add≥0.5→CF_mult<0.5) vs
    already-failed cells (CF_add<0.5, C1's contested corner); (5) cheap
    full-grid multiplicative cross-check for the global CF<0.5 fraction.
    [2026-05-24 run-011 done] DONE. Verdict A3 WEAKLY-SUPPORTED →
    CONTESTED (second vector, replication). Code:
    Critique/replications/A3--multiplicative-conservation/cr008_cf_floor/.
    Validation EXACT: local βγ=1 map ≡ parent run.py (dev 0.0);
    recomputed additive CF ≡ run-003 stored, bit-for-bit over all 590
    at-risk cells (max|Δ|=0.0); R(P3),R(P4) family-independent
    (max|Δ|=0.0); independent from-scratch recompute of the worst cell
    matched (CF_mult=0.2309, CF_add=0.3040); re-run deterministic.
    RESULT: |S|=590 (additive CF<0.60). Over the FULL 4,410-cell grid
    the criterion-subordinate fraction (CF<0.5) DOUBLES: additive
    177/4410 (4.01%) → multiplicative 368/4410 (8.34%); 191 cells FLIP
    from CF≥0.5 to CF<0.5 (0 recover; ΔCF∈[−0.109,0.000], max exactly 0
    — βγ=1 never raises CF). BUT median CF essentially unchanged
    (0.7605→0.7578); new flips concentrate in the BENEFIT-DOMINANT
    high-r corner (r≳2.5, mostly variant B, +variant A at r=10) — the
    same corner C1 already contested under additive, deepened/widened
    not relocated. Min CF deepens 0.304→0.231 at (r=10,V=0.25,v=4,B).
    The literal "any CF_mult<0.5 → CONTESTED" rule was refined: 177
    cells already fail under additive (C1), so the constraint-
    attributable signal is the 191 NEW flips + the doubling of the
    failure fraction, not the blunt count. Verdict CONTESTED (not
    CONFIRMED-CONDITIONAL: fails WITHIN the paper's stated grid; not
    REFUTED: bulk/central-tendency criterion dominance survives).
    Reformulation proposed (§5.5/§6: criterion dominance is robust as a
    central-tendency claim but boundary-sensitive to the conservation
    form; report "typically" not "always" the largest contributor).
    §11 sweep surfaced muller_findlay1987_sensitivity_criterion (new
    cite) + reynolds_chelazzi2004 (divisive-normalization). No new stub;
    0 web fetches. Spawned CR-044 (Δα=0.005 grid-robustness spot-check
    on borderline flips, low). CR-042 (f0/h secondary-sweep sensitivity)
    promoted in spirit to the highest-leverage A3 follow-up.
  origin: seed
  touched: 2026-05-24T01:55:00Z

- id: CR-009
  claim_id: A4
  attack_vector: literature
  task: |
    Assumption A4: no learning dynamics. The paper's normative
    model assumes the observer has already discovered the
    optimal policy. Survey the reinforcement-learning literature
    (and the PRISM training literature in Prism/docs/) for
    evidence on how rapidly attention-reallocation policies vs.
    criterion-shift policies are learned in practice. If learning
    dynamics consistently favor the simpler (criterion) policy,
    that REINFORCES the paper's normative conclusion (criterion
    dominance) on practical grounds — a CONFIRMING attack from
    a different angle. Document at
    Critique/evidence/A4--no-learning-dynamics.md.
  status: queued
  priority: low
  prereqs: []
  notes: |
    Bootstrap-seeded. Lower priority because the paper itself
    flagged this and the empirical literature on learning
    dynamics for spatial-cueing tasks is sparse. Worth doing
    once the higher-priority headline-claim attacks have moved.
    PRISM training logs (Prism/checkpoints/*, training curves
    if archived) are a candidate first-party data source.
  origin: seed
  touched: 2026-05-17T00:00:00Z

- id: CR-010
  claim_id: A5
  attack_vector: replication
  task: |
    Assumption A5: the four functional forms h(a) ∈ {a, √a, a^0.3,
    a^2} exhaust the qualitative landscape. Test a sigmoidal form
    (e.g. h(a) = 1/(1+exp(-k(a-0.5))) for k=4 and k=10) and a
    threshold form (h(a) = 0 for a<θ; a-θ scaled to fit boundary
    conditions otherwise). Re-run the headline parameter
    combination and report how the VDA peak location and
    magnitude shift relative to the paper's four forms.
    Document under
    Critique/replications/A5--alternative-transfer-functions/.
  status: queued
  priority: low
  prereqs: [CR-005]
  notes: |
    Bootstrap-seeded. Lower priority but conceptually important —
    the paper's qualitative claims (non-monotonic, narrow regime)
    should be robust to transfer-function family changes if they
    really are properties of the cost-benefit asymmetry rather
    than the transfer function. A counterexample here would be
    significant.
  origin: seed
  touched: 2026-05-17T00:00:00Z

- id: CR-011
  claim_id: A6
  attack_vector: re-derivation
  task: |
    Assumption A6: homogeneous decision rule across locations.
    Re-derive the optimal policy under heterogeneous decision
    noise (e.g. larger decision noise at uncued locations) and
    check whether the policy decomposition (P1–P4) still
    cleanly separates the contributions of criterion vs.
    attention. If the decomposition breaks under
    heterogeneity, the criterion-fraction metric loses its
    interpretation and the verdict for A6 moves. Document at
    Critique/derivations/A6--heterogeneous-decision-rule.md.
  status: done
  priority: medium
  prereqs: []
  notes: |
    Bootstrap-seeded. The paper does not state A6 explicitly —
    it's an implicit assumption that the same SDT machinery
    applies at every location. Worth surfacing as a verdict in
    its own right.
    [2026-05-25 run-018 start] Marked in_progress at start of the
    eighteenth scheduled run. Picked per mission §3.3: A6 is the
    highest-priority OPEN verdict (medium; A4/A5/A7 are low) with
    prereqs settled, so it is the default pick with no override
    needed (CR-053, the run-017 recommendation, is on an
    already-CONTESTED A1, so it fails the §3.3 OPEN/WEAKLY-SUPPORTED
    selection filter). A6 is also the home of §5.5's "single global
    response" clause that run-017's Booking-1/Booking-2 split routed
    here (CR-055 pointer). Folding CR-055 into this run. Attack plan
    (re-derivation): (1) introduce per-location decision noise s_i,
    derive HR_i=Φ((d'_i/2−c_i)/s_i), FAR_i=Φ((−d'_i/2−c_i)/s_i);
    (2) Prop 1 — fixed s_i is absorbed into effective d̃'_i=d'_i/s_i,
    c̃_i=c_i/s_i (bijection in the free criterion), so the P1–P4
    decomposition is structurally invariant → A6-fixed benign;
    (3) Prop 2 — attention-coupled s_i=s(α_i) is a THIRD lever whose
    gain the criterion-fraction metric mis-books to "attention,"
    deflating CF (same direction as the A1-ρ result); (4) numerical
    corroboration reusing the C5/A3/A1 optimiser (validate κ=0
    reproduces headline CF + VDA peak), illustrative s(α) coupling.
    [2026-05-25 run-018 done] DONE. Verdict A6 (none) → WEAKLY-SUPPORTED
    (first touch, one vector: re-derivation +
    Critique/derivations/A6--heterogeneous-decision-rule.md +
    Critique/replications/A6--heterogeneous-decision-rule/, numeric
    sha256 d6741d48…, deterministic; 0 web fetches; no new stub → no
    audit.py). Folded in CR-055. PROVED Prop 1: fixed heterogeneous
    decision noise s_i is ABSORBED into effective d'_i=d'_i/s_i via the
    exact identity Φ((d'/2−c)/s)=Φ(d̃'/2−c̃) (1.1e-16), so the entire
    P1–P4 set = paper's at d'→d'/s and CF(s_c,s_u)=CF_paper|_{d'→d'/s}
    EXACTLY (numerically ≤1.7e-5 on a non-clipping grid, →0 as Δc→0) —
    the decomposition is STRUCTURALLY INVARIANT; fixed s is a per-location
    d'-perturbation (same class as d'_max/f_0), moves CF's value
    (0.728→0.789 at s_u=2) not its interpretation. Prop 2: ATTENTION-
    COUPLED noise s(α) is a THIRD lever — ∂_α(d'_c/s_c) gains a
    noise-reduction term, so the P1−P3 increment CF books to "attention"
    bundles spatial d'-reallocation + noise reduction; CF DEFLATES
    0.728→0.626 (κ:0→1, wide-grid guard) while total gain grows
    0.62→0.78 (same direction as the A1-ρ result). A6-(ii) single global
    response (§5.5/CR-055): single global criterion removes the per-loc
    DOF §5.1 calls criterion's advantage, G_crit^global≤G_crit^per-loc
    strict for v>1,V≠1/N ⇒ CF compounds down (CR-055 prediction); pooled
    rule also dissolves the Eq.9 FA product = A1 locus. Label
    WEAKLY-SUPPORTED (mission §6 one vector; NOT CONTESTED — Prop 1
    confirming, no headline number shifts within the paper's stated model
    s≡1; cracks need a model extension). Caught+fixed a criterion-grid
    clipping trap (default [-3,3] clips uncued criterion at large s,
    inflating CF; widened to [-8,8]). §11 sweep: luo_maunsell2018 +
    lu_dosher1998 (attention's mechanism inventory exceeds the single
    d'-gain) cited as Prop-2 substrate; mcadams1999 + hawkins1990 the fair
    legs; cohen_maunsell2009 the empirical s'(α)<0; ernst_banks2002 +
    Shadlen/Ratcliff accumulator cluster the A6-(ii) pooling substrate
    (deferred to CR-056); PRISM bridge via coalition_resource_competition
    + multi_hub_multi_objective_system. Spawned CR-056 (A6 second vector,
    replication — single-global-criterion CF deflation across the grid;
    settles CONFIRMED-CONDITIONAL vs CONTESTED) and CR-057 (A6 literature
    — is the noise/criterion lever value- AND attention-modulated;
    overlaps CR-053). CR-056 is the recommended next pick.
  origin: seed
  touched: 2026-05-25T15:58:00Z

- id: CR-012
  claim_id: A7
  attack_vector: replication
  task: |
    Assumption A7: only two reward variants (A: value-coupled
    CR; B: fixed CR=1) are tested. Implement a third variant
    where CR scales as CR = V^α · v + (1-V^α) for some α ∈ {0.5,
    2}, or a fourth where there is an explicit cost for a false
    alarm. Re-run the headline parameter combination and check
    whether the criterion-fraction range (0.60–0.96 per C1) and
    the VDA-peak location (r ≈ 0.3 per C2) survive. Document
    under Critique/replications/A7--alternative-reward-structures/.
  status: queued
  priority: low
  prereqs: [CR-005]
  notes: |
    Bootstrap-seeded. The paper claims the two variants bracket
    extremes; this task tests that bracketing.
  origin: seed
  touched: 2026-05-17T00:00:00Z

- id: CR-013
  claim_id: C2
  attack_vector: replication
  task: |
    High-resolution Figure 4 replication. Reproduce VDA(r) at the
    paper's grid resolution (Δα = 0.005, Δc = 0.05) across the
    full v ∈ {1,2,3,4,5} envelope, with V=0.5, N=4, d'_max=2.0,
    f_0=0.5, h=sqrt, Variant A. Compare peak (r*, VDA*) at v=5
    to the paper's r ≈ 0.3, VDA ≈ 0.080. The agent's first-pass
    sweep at Δα=0.01 found peak (r=0.398, 0.0774), one log-grid
    step right of the paper. This task resolves whether the
    discrepancy is sub-grid resolution or substantive.

    If peak location matches the paper to within one Δα step at
    the higher resolution, C2's verdict elevates to
    CONFIRMED-UNDER-ATTACK after this run (two attack vectors:
    re-derivation in CR-001, replication here).
  status: queued
  priority: high
  prereqs: []
  notes: |
    Spawned by CR-001 (re-derivation surfaced sub-grid peak
    ambiguity). The replication code lives at
    Critique/replications/C2--non-monotonic-vda/run.py — extend
    it with finer Δα and a full v-sweep. Requires scipy or a
    similarly fast Phi/erf vectorisation; the sandbox in the
    CR-001 run lacked scipy (disk pressure). Consider asking the
    owner for a sandbox with scipy, or implementing erf via a
    numpy polynomial approximation if disk constraints persist.
  origin: spawned-by-CR-001
  touched: 2026-05-17T12:30:00Z

- id: CR-014
  claim_id: C2
  attack_vector: sensitivity
  task: |
    The CR-001 re-derivation produced a closed-form escape
    threshold r†(v) = G_u(V,N,c_c,c_u) / [(N-1)·G_c(v,V,N,c_c,c_u)]
    governing the lower edge of the non-zero VDA interval. Use
    this expression to predict how the peak location r* shifts
    as f_0, h, and N vary across the values in the paper's
    secondary sweeps (paper §3.1). Compare against the paper's
    Figure 6 ("VDA benefit vs r: sensitivity to model
    parameters"). If the closed-form predictions match the
    empirical pattern, this is a *second* successful attack
    vector for C2 — together with CR-001 this would justify
    elevation to CONFIRMED-UNDER-ATTACK. If they disagree, the
    analytic skeleton has a missing piece and C2's verdict
    should be reconsidered.
  status: done
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-001. Conceptually cheaper than the full
    replication in CR-013 because the closed-form prediction
    can be evaluated analytically for each (f_0, h, N) and only
    the peak location needs to be measured numerically (or
    eyeballed from Figure 6). The dependence on f_0 should
    flow through f'(1/N): for h=√, f'(1/N) = (1-f_0)·√N/2; so
    lower f_0 → larger f'(1/N) → larger G_c → lower r† → peak
    shifts left. The paper's Figure 6 caption: "Lower f_0
    shifts the peak VDA higher and to slightly lower r." That
    is consistent with the analytic prediction.
    [2026-05-17 run start] Marked in_progress at start of second
    scheduled run. Attack: predict r†(v) and peak r* across
    secondary sweeps (f_0 ∈ {0.1,0.3,0.5,0.7}, h ∈ {a, √a, a^0.3,
    a^2}, N ∈ {2,4}), compare to Figure 6.
    [2026-05-17 run done] Closed-form r†(v) directionally predicts
    every shift in the paper's §4.6 / Figure 6 narrative:
    – f_0 sweep: r†(v=5) strictly increasing in f_0 (0.014,
      0.028, 0.050, 0.066), matching empirical peak r (0.10,
      0.25, 0.40, 0.50). Lower f_0 → lower peak r ✓.
    – h sweep: log10(r†(1)/r†(v)) narrowest for a^0.3 (0.76)
      and widest for a^2 (1.27), exactly mapping the paper's
      "a^0.3 compresses, a^2 stretches" claim ✓.
    – N sweep: r†(v=5)=0.27 for N=2 vs 0.05 for N=4; empirical
      peak r=5 vs 0.4; direction ✓ (paper's "qualitatively
      similar" understates the quantitative shift).
    Closed-form is exact at non-clamping regime, conservative
    in the clamping regime (low f_0, accelerating h, low-r where
    d_u clamps to 0). C2 verdict elevates from WEAKLY-SUPPORTED
    to CONFIRMED-UNDER-ATTACK — two distinct attack vectors have
    now failed to falsify.
    One subsidiary §4.6 wording weakened: peak VDA is
    non-monotonic in f_0 (max at f_0=0.3, not f_0=0.1) at the
    agent's α-grid resolution. Affects §4.6 wording, not C2
    proper. Spawned CR-017 (clamping derivation extension),
    CR-018 (f_0-VDA literature attack), CR-019 (C4
    no-inversion refinement at V=1/N).
  origin: spawned-by-CR-001
  touched: 2026-05-17T14:30:00Z

- id: CR-017
  claim_id: C2
  attack_vector: re-derivation
  task: |
    Extend the closed-form escape threshold r†(v) =
    G_u/[(N-1)·G_c(v)] from the CR-001 derivation §2.3 to the
    *clamping regime* in which d'_u saturates at 0 for large α.
    The CR-014 sensitivity probe found that at f_0=0.1 (or
    h=a^2) the empirical P1 escape from uniform happens at
    much lower r than the closed-form predicts, because the
    d'-clamping bounds the marginal cost of large α
    deviations. Replace the infinitesimal-deviation gradient
    with a finite-deviation comparison between R(α=1/N) and
    R(α=1) (or R(α=1−ε)), and derive the new escape
    threshold. The result would unify clamping and non-clamping
    regimes under one analytic prediction. Write the
    derivation extension at
    Critique/derivations/C2--clamping-extension.md.
  status: queued
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-014. The clamping condition is
    γ > d'_base / (d'_base − d'_max·f((1−α)/(N-1))). At
    f_0=0.1, N=4, h=√: d'_base=1.10, f((1−α)/(N−1)) at α=1 is
    f(0)=0.1, so d'_max·0.1=0.2, and clamping triggers at
    γ ≥ 1.22, i.e. r ≤ 0.64. The clamping-extended r† should
    predict r†_clamp = R(α=1) − R(α=1/N) at γ_clamp, which is
    finite (not gradient-based).
  origin: spawned-by-CR-014
  touched: 2026-05-17T14:30:00Z

- id: CR-018
  claim_id: C2
  attack_vector: literature
  task: |
    The CR-014 sensitivity probe found that peak VDA is
    *non-monotonic* in f_0: the empirical max is at f_0 ≈ 0.3,
    not at f_0=0.1 (the paper's §4.6 wording implies lower f_0
    → higher peak VDA monotonically). Investigate the empirical
    literature on attention-d' relationships at *very low
    baseline d'* (near-threshold paradigms): do empirical
    studies show monotonic ↑VDA with ↓baseline-sensitivity, or
    a peak at intermediate sensitivity? Key candidates:
    cameron2002_covert_attention_contrast,
    lu_dosher1998_external_noise (especially the high-external-
    noise regime, which approximates low effective f_0), and
    psychophysics papers on near-threshold cued detection.
    If the empirical pattern is monotonic, this confirms the
    paper's §4.6 wording and the agent's non-monotonic finding
    is an α-grid resolution artefact. If the empirical pattern
    is non-monotonic, the paper's §5.2 experimental-design
    recommendation ("low f_0 to maximise observable VDA")
    needs to be refined to "moderately low f_0".
    Document at Critique/evidence/C2--f0-vda-relationship.md.
  status: queued
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-014. Lower priority than CR-017 because the
    f_0 non-monotonicity is a refinement to §4.6 wording, not a
    challenge to C2 proper. But the result has experimental-
    design implications via §5.2.
  origin: spawned-by-CR-014
  touched: 2026-05-17T14:30:00Z

- id: CR-019
  claim_id: C4
  attack_vector: sensitivity
  task: |
    The CR-014 sensitivity probe surfaced that at V=1/N exactly
    (N=2, V=0.5), the model's cued/uncued labelling has no
    informational content and the optimum is symmetric: α and
    1−α give the same expected reward. The numerical optimiser
    in CR-014 picked α=0.02 for P2 at high r (the "inverted"
    branch). This technically violates C4 (no inversion) at the
    V=1/N boundary, but is vacuous at V=1/N (the labelling is
    meaningless). When CR-004 (C4 re-derivation) is taken on,
    the verdict for C4 should note that the categorical claim
    "α*≥1/N is normatively optimal" implicitly requires V >
    1/N, not just V ≥ 1/N. The paper's primary sweep uses
    V ∈ [0.25, 1.0], which for N=2 includes V=0.25 < 1/N (a
    region with no meaningful interpretation). Document the
    V=1/N degeneracy and its implications for C4's wording.
  status: done
  priority: low
  prereqs: [CR-004]
  notes: |
    Spawned by CR-014. This task should be executed as part of,
    or immediately after, CR-004. It is a refinement of C4's
    wording, not an independent attack. The wording change
    suggested: "α*≥1/N is normatively optimal under the
    paper's primary sweep regime V ∈ [1/N, 1.0] for V > 1/N";
    at V=1/N exactly, multiple α values give equivalent
    optima.
    [2026-05-18 run-006 done] Resolved IN THE NEGATIVE as part
    of CR-004. The CR-019 conjecture — that C4 implicitly needs
    V > 1/N strict — is incorrect. At V=1/N, v=1, r > 1, the
    model is bimodal (right- and left-branch local maxes
    exist), but the right branch wins strictly by ~0.005–0.014
    reward units due to the location-count asymmetry (at α→1
    the single cued reaches d_max; at α→0 the N-1 uncued each
    reach only d_base + β[d_max f(1/(N-1)) − d_base] < d_max
    for N≥3). At V=1/N, v=1, r ≤ 1, E[R] is flat in a
    neighbourhood of α=1/N; the CR-014 α=0.02 finding for P2
    (which is value-blind at v=1) was the left-branch local
    maximum found because the value-blind P_2 optimiser may
    have settled there. C4's V ≥ 1/N (weak) is correct as
    written; no wording change needed. CR-019 closed.
  origin: spawned-by-CR-014
  touched: 2026-05-18T13:00:00Z

- id: CR-020
  claim_id: C3
  attack_vector: literature
  task: |
    Survey the wiki for primate-attention / cueing experiments
    that sit in the *high-V* regime the paper's §5.2 predicts
    should NOT show VDA. With C1 now CONTESTED, the §5.2
    advice "high-validity paradigms predicted to show negligible
    VDA regardless of other parameters" is the next-most-load-
    bearing claim in the experimental-design narrative. If any
    published cueing study at V ≥ 0.75 reports VDA-like value-
    driven attention effects, that contradicts C3's "narrow
    regime" claim and the §5.2 advice. Document at
    Critique/evidence/C3--narrow-regime.md.
  status: done
  priority: high
  prereqs: []
  notes: |
    Spawned by CR-002. Strongly overlaps with seed task CR-003
    (the same C3 literature attack). Consider executing CR-020
    as the actual completion of CR-003 — they are the same task
    in different words. Owner attention: maybe merge them.
    Candidate wiki entries: failing_theeuwes2018_selection_history,
    hickey2010_reward_salience_acc, anderson_laurent_yantis2011_
    value_capture (if it exists), carrasco2011_visual_attention_25y,
    posner1980_orienting. Web fetches likely unnecessary — wiki
    coverage of the cueing literature is rich.
    [2026-05-17 run-004 start] Marked in_progress at start of fourth
    scheduled run. Merging CR-003 into this task (per re-prioritisation
    note CR-002 → next run, identified as duplicates). Attack plan:
    (a) read paper §5.2 in full to nail the exact testable prediction;
    (b) wiki sweep per §11.1 anchors to surface every entry bearing
    on high-V cueing × value/reward modulation; (c) classify each as
    supporting (saturation at high V), contradicting (value-driven
    performance effects at high V), or constraining (e.g. neural-but-
    not-behavioral effects). The hardest test: studies in which
    cue validity is high but value still alters PERFORMANCE (not just
    RT priming, not just neural firing). Default first-pass position:
    the value-driven-attentional-capture literature (Anderson et al.
    2011 paradigm) is at V=1/N, so it CONFIRMS rather than refutes;
    Maunsell-lab macaque physiology is typically at V=1.0, neural
    effects do not directly refute (criterion-only mechanism can
    produce neural correlates). Real tension cases would be:
    high-V cueing tasks where reward magnitude alters d' (sensitivity)
    in a way not attributable to validity.
    [2026-05-17 run-004 done] Verdict label set to WEAKLY-SUPPORTED.
    Decomposed §5.2 into C3a (low-V VDA exists) and C3b (high-V VDA
    negligible). C3a confirmed by failing_theeuwes2018 and hickey2010
    (V=1/N paradigm). C3b supported by luo_maunsell2018,
    maunsell2015, sridharan2017 (high-V SDT-aligned macaque tradition,
    with circularity caveat — designs assume the decomposition).
    C3b CONSTRAINED by new wiki stub stanisor2013_v1_value_attention
    (added this run; abstract-depth read of PNAS PMID 23676276;
    high-V curve-tracing with varied reward magnitude shows V1
    single-unit modulation by relative reward value with
    attention-like latency and per-cell value/attention covariation;
    authors conclude "relative value and top-down attention engage
    overlapping, if not identical, neuronal selection mechanisms").
    The tension is prima facie but not yet a refutation: V1 effect
    could be a criterion-side decision-readout correlate rather
    than a true sensitivity gain. 14 wiki entries consulted; 10
    cited in verdict body; 1 new stub added; audit.py exit 0.
    1 PubMed fetch used (1 of 2 soft cap). Spawned CR-023
    (Stanisor full-depth read), CR-024 (Peck 2009 + Serences 2008
    stubs), CR-025 (replication-attack adding sensitivity-side
    reward channel; depends on CR-005), CR-026 (re-derivation:
    compute sup_{r,v} [R(P1)-R(P2)] at V=0.75 analytically to
    determine whether C3b is a theorem of the model or a
    numerical observation).
  origin: spawned-by-CR-002
  touched: 2026-05-17T17:35:00Z

- id: CR-021
  claim_id: C1+C4+spawned-multi
  attack_vector: re-derivation
  task: |
    Closed-form derivation at the V = 1/N boundary. CR-002 (C1)
    and CR-014/CR-019 (C2/C4) have all surfaced V=1/N as a
    recurring model edge case. A unified treatment: at V = 1/N
    exactly, partition R(P2) − R(P3) into (a) a validity-driven
    component (formally zero, since V − 1/N = 0) and (b) an
    asymmetry-driven component (a closed-form expression in r,
    N, f_0, h). Demonstrate analytically that (i) the
    "validity-attention" label at V = 1/N is a misnomer, (ii)
    the asymmetry-driven α-shift produces R(P2) > R(P3) for
    all r > some r_*(N, f_0, h) at V=1/N, and (iii) the
    contribution to the criterion fraction's denominator is
    sufficient to drive CF below 0.50 in variant B. Write the
    derivation at
    Critique/derivations/V-equals-1-over-N--degeneracy.md.
  status: queued
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-002. Builds on the CR-001 G_c/G_u machinery
    from `Critique/derivations/C2--non-monotonic-vda.md`. The
    boundary's analytic treatment unifies three previously
    separate findings (C1's low-CF corner, C2's escape
    threshold at high r, C4's V=1/N degeneracy from CR-019).
    Re-derivation rather than replication because the closed-
    form is what's missing — numerics from CR-002 are
    sufficient.
  origin: spawned-by-CR-002
  touched: 2026-05-17T15:50:00Z

- id: CR-022
  claim_id: C1-expository
  attack_vector: clarification
  task: |
    Surface to owner attention: the paper's §4.1 text quotes
    "criterion fraction reaches 96% at r = 0.3", but my
    replication (CR-002) finds CF = 0.854 there at V = 0.5125
    (and 0.861 at V = 0.50 exact, r = 0.30 exact, Δα = 0.001).
    The discrepancy is 11 percentage points. The paper's r =
    1.0 and r = 3.2 references match my code to 0.002 of CF, so
    the model implementation is correct. The paper's *own
    Figure 2* visually reads CF ≈ 0.85 at r = 0.3, consistent
    with my code. Most likely the §4.1 "96%" is a manuscript
    transcription error.

    No code task. Output: a brief one-page note in
    Critique/conversations/ summarising the discrepancy with
    reproducible reference points, for the owner to flag with
    the paper's authors (or to confirm independently if their
    code is accessible).
  status: queued
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-002. Low priority because the categorical-
    floor refutation (CR-002's main finding) is independent of
    this expository discrepancy. But the r=0.3 number is the
    paper's most-quoted criterion-fraction value (it appears in
    §4.1, Figure 2 caption, and §5.2 effectively), so a
    correction would tighten the paper materially.
  origin: spawned-by-CR-002
  touched: 2026-05-17T15:50:00Z

- id: CR-015
  claim_id: A2
  attack_vector: literature
  task: |
    Deepen the wiki entry for maunsell2015_attention_mechanisms
    (currently shallow) and use it to interrogate A2 (single
    global asymmetry ratio r). The Maunsell 2015 review is
    cited by the paper as refs [11–14] grouped under "dissociable
    benefit and cost"; the agent should read it carefully and
    identify whether the empirical evidence Maunsell summarises
    is consistent with a *single global* r or requires
    location-/feature-specific r values. If the latter, A2's
    verdict moves and C2/C3 may need revisiting under
    heterogeneous-r assumptions.
  status: queued
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-001 wiki sweep. Note overlap with seed task
    CR-007 (broader A2 literature attack); CR-015 is a focussed
    deepening that should produce a stronger A2 verdict than
    CR-007's general survey. Consider executing CR-015 before
    CR-007, or rolling CR-007 into CR-015's broader scope.
  origin: spawned-by-CR-001
  touched: 2026-05-17T12:30:00Z

- id: CR-016
  claim_id: A2
  attack_vector: literature
  task: |
    The C2 wiki sweep noted that the wiki has no entry for
    Maunsell & Treue (2006), the canonical feature-vs-spatial
    attention dissociation review. Mission §4.2 allows the
    agent to add a new stub. This task: add a metadata- or
    abstract-depth stub for maunsell_treue2006, following
    research_db/SCHEMA.md exactly, and run audit.py. Cite this
    paper from A2-related verdicts.
  status: queued
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-001 wiki sweep. Low priority because the
    user's wiki has many other canonical attention-mechanism
    sources; this is a polish task, not a load-bearing one.
    Defer until either CR-007 or CR-015 makes the citation
    actually load-bearing.
  origin: spawned-by-CR-001
  touched: 2026-05-17T12:30:00Z

- id: CR-023
  claim_id: C3
  attack_vector: literature
  task: |
    Full-depth read of Stănișor, van der Togt, Pennartz & Roelfsema
    2013 PNAS ("A unified selection signal for attention and reward
    in primary visual cortex"). PMC open-access available at
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3670348/. Promote
    the existing wiki stub stanisor2013_v1_value_attention from
    depth: abstract to depth: full (the user owns this depth
    promotion in general per §4.2; the agent can additionally
    deepen its own newly-added stubs within the same depth-step
    constraint).
    The single most consequential question for the C3 verdict:
    does the V1 reward modulation translate to a behavioural d′
    improvement at the high-value stimulus that the paper's
    criterion-only account cannot recover? If yes, C3b is REFUTED
    and the verdict moves to CONTESTED with a §5.2 reformulation
    proposed in the verdict file. If no — i.e., the behavioural
    data are equally consistent with a criterion-side
    decision-readout interpretation of the V1 effect — C3b stays
    WEAKLY-SUPPORTED with Stănișor reclassified from "constrain"
    to "support."
    Write findings as a Version 0.2 section appended to both
    Critique/verdicts/C3--narrow-regime.md and
    Critique/evidence/C3--narrow-regime.md.
  status: queued
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-020. Lower priority than CR-026 because the
    re-derivation attack (whether C3b is a theorem of the model)
    has to be settled first — only once we know the model itself
    predicts negligible VDA at V=0.75 does the empirical
    behavioural-d′ data become diagnostic. If CR-026 finds C3b is
    NOT a theorem (i.e., there exist (r,v) at V=0.75 with
    R(P1)-R(P2) > 0.005), the §5.2 wording is too strong even
    internal to the model and CR-023's role shifts from
    "refutation/support" to "auxiliary empirical anchor."
    Web-fetch budget: 1 fetch likely sufficient (PMC abstract +
    Results section).
  origin: spawned-by-CR-020
  touched: 2026-05-17T17:35:00Z

- id: CR-024
  claim_id: C3
  attack_vector: literature
  task: |
    Add wiki stubs (depth: abstract or metadata; per §4.2) for two
    additional high-V × value-magnitude × early-visual-cortex
    papers identified by the CR-020 wiki sweep as gaps:
    (a) Peck, Jangraw, Suzuki, Efem, Gottlieb 2009 J Neurosci on
        LIP single-unit reward coding in cued attention. Candidate
        id: peck2009_lip_reward.
    (b) Serences 2008 Neuron on human fMRI value modulation of
        early visual cortex. Candidate id: serences2008_value_v1.
    Run audit.py after additions. Cite both from the C3 verdict
    file's Version 0.3 section (or whatever version is next).
  status: queued
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-020. Medium priority because both are
    additional anchors for the high-V × value question — if
    Stănișor 2013 turns out to be a behavioural-d′ refutation of
    §5.2 (via CR-023), Peck 2009 and Serences 2008 would provide
    convergent neural evidence (LIP and human-fMRI) for the
    same conclusion. If Stănișor 2013 is a criterion-side
    correlate, Peck and Serences would help characterise the
    broader high-V × value substrate.
    Both papers are cited in failing_theeuwes2018_selection_history
    and hickey2010_reward_salience_acc as "citations to follow"
    and are well-known to the field.
  origin: spawned-by-CR-020
  touched: 2026-05-17T17:35:00Z

- id: CR-025
  claim_id: C3
  attack_vector: replication
  task: |
    Add a sensitivity-side reward-modulation channel to the
    paper's model and re-evaluate the CF and VDA decomposition.
    Concretely: instead of (or in addition to) the existing
    α-mediated value channel (where v modulates the attention
    allocation), introduce a per-stimulus sensitivity multiplier
    f_v(v) on d'_cued and (optionally) a contralateral
    f_v((1-V)/(N-1) · v_other) on d'_uncued. The motivation is
    the Stănișor 2013 V1 finding (per stanisor2013_v1_value_attention
    stub) that high-V tasks show V1 reward modulation that has
    the latency and per-cell profile of attentional gain. If a
    sensitivity-side reward channel that bypasses α-reallocation
    produces high-V VDA above the paper's "negligible" threshold,
    that constitutes a formal refutation of §5.2 (and of C3b)
    independent of the empirical behavioural-d′ question.
    Document under
    Critique/replications/C3--sensitivity-side-reward/.
  status: queued
  priority: low
  prereqs: [CR-005]
  notes: |
    Spawned by CR-020. Depends on CR-005 (C5 replication) for the
    replication substrate. Lower priority than CR-026 (cheaper
    re-derivation) but more architecturally informative: if a
    minimal modification to the model (adding sensitivity-side
    reward channel) produces high-V VDA, then C3b is not a
    property of the cost-benefit-asymmetry framework but of one
    specific embedding of value into the model (via α only).
  origin: spawned-by-CR-020
  touched: 2026-05-17T17:35:00Z

- id: CR-026
  claim_id: C3
  attack_vector: re-derivation
  task: |
    Re-derivation attack on C3b. Using the closed-form machinery
    built in CR-001 (Critique/derivations/C2--non-monotonic-vda.md),
    compute analytically or semi-analytically the supremum
        sup_{r ∈ [0.1, 10], v ∈ {1, ..., 5}} [R(P1) - R(P2)]
    at V = 0.75 with the paper's reference parameters (N = 4,
    d'_max = 2.0, f_0 = 0.5, h = sqrt, Variant A). Three outcomes:
    (i) Supremum < 0.005 (the paper's "negligible" threshold):
        C3b is a theorem of the model under its assumptions; the
        verdict elevates to CONFIRMED-CONDITIONAL on (A1-A7).
    (ii) Supremum in [0.005, 0.020] (moderate): the §5.2
        categorical wording is too strong; weaker reformulation
        (drafted in C3 verdict V0.1) becomes the operational
        claim; verdict stays WEAKLY-SUPPORTED.
    (iii) Supremum > 0.020: the §5.2 wording is wrong internal
        to the model; verdict moves to CONTESTED.
    Write the derivation at
    Critique/derivations/C3--high-V-supremum.md and append the
    finding as Version 0.2 to Critique/verdicts/C3--narrow-regime.md.
  status: done
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-020 as the recommended next-attack for C3.
    This is the cheaper of the two C3 follow-ups and is more
    informative than CR-023 because it adjudicates whether C3b
    is a property of the model or a property of one parameter
    choice — which determines what any subsequent empirical
    attack can ever conclude.
    Technical note: the supremum may not be attained at the
    grid corners; gradient-based optimisation within
    (r, v) ∈ R+ × R+ may be needed. The closed-form r†(v) from
    CR-001 gives the lower edge of the non-zero VDA interval at
    each v; the sup is at the *interior* peak of VDA(r, v) at
    V = 0.75.
    [2026-05-17 run-005 start] Marked in_progress at start of
    fifth scheduled run. Re-derivation attack using CR-001's
    closed-form r†(v) machinery extended to the V-axis.
    [2026-05-17 run-005 done] Outcome (iii): sup VDA = 0.040
    reward units at (r=0.10, v=5), V=0.75. Eight times the paper's
    "<0.005 negligible" threshold and twice §4.4's own "hot zone"
    boundary 0.02. §4.4/§5.2 categorical wording REFUTED internal
    to the model under its own assumptions (A1-A7). Closed-form
    V_critical(r,N) ≈ 1/(1 + r(N-1)/κ) derived; empirical boundary
    V_critical(r=0.1, N=4) ∈ (0.775, 0.780) — paper's "V≥0.75"
    threshold is one V-grid step too generous at the cost-dominant
    corner. Across the V=0.75 slice in the paper's primary
    (r,v)=21×5 grid: 8 cells violate "<0.005" (r ∈ {0.10, 0.126} ×
    v ∈ {2,3,4,5}), 6 violate "<0.02" (same r-corners × v ∈
    {3,4,5}). Substantive content (high-V VDA window is NARROW,
    §5.1 theoretical argument intact) survives; categorical wording
    fails. Verdict C3 label: WEAKLY-SUPPORTED → CONTESTED.
    Proposed §4.4/§5.2 reformulation drafted with explicit
    r-dependent V_critical threshold. Refinement pass at
    (r=0.1, v=5) with Δα=0.005, Δc=0.025 confirms sup=0.0400
    (not a grid artefact). Fine V-grid in [0.75, 0.80] locates
    boundary; fine r-grid in [0.05, 0.20] confirms sup interior to
    the high-V VDA window. Stănișor 2013 V0.1 classification
    reclassified from "constrain" to potential "support of
    reformulated C3b" (the high-V V1 reward signature is now
    *predicted* by the reformulation as the residual VDA window's
    neural correlate). No new wiki stubs added (attack was
    internal to the model; literature attack already done in
    run-004). Spawned CR-027 (FAR-corrected V_critical closed
    form, medium), CR-028 (Variant B sup at V=0.75, medium),
    CR-029 (V_critical across secondary sweep, low), CR-030
    (literature search in residual high-V VDA window, low).
  origin: spawned-by-CR-020
  touched: 2026-05-17T18:55:00Z

- id: CR-027
  claim_id: C3
  attack_vector: re-derivation
  task: |
    Derive the FAR-side-corrected closed form for V_critical(r, N,
    d'_max, f_0, h). The simple change-side approximation in CR-026's
    derivation §2 Eq. (5),
        V_critical(r, N) ≈ 1/(1 + r·(N-1)/κ)
    with κ a slowly-varying density ratio, underestimates the
    empirical boundary at V=0.75, r=0.1, N=4 by ≈ 4 percentage points
    (predicts ≈ 0.74; empirics give ≈ 0.78). The FAR-side
    contribution to G_u (Eq. 2) is *comparable* to the change-side
    contribution when the optimal c_u is near zero (which it is
    when V > 0.7). A full closed form should include both
    change-side and FAR-side density terms, and recover the
    empirical boundary across the secondary-sweep grid.
    Write the extension as Critique/derivations/C3--V-critical-FAR.md
    or append as a §10 to C3--high-V-supremum.md.
  status: queued
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-026. The cheapest C3 follow-up; resolves the
    4pp gap between closed-form prediction and numerical boundary.
    Once correct, the closed form becomes the operational tool the
    proposed §4.4 / §5.2 reformulation can be stated in.
  origin: spawned-by-CR-026
  touched: 2026-05-17T18:55:00Z

- id: CR-028
  claim_id: C3
  attack_vector: replication
  task: |
    Variant B sup at V=0.75. Re-run the CR-026 sweep with CR=1
    (Variant B, mission §2.5) instead of CR=V·v+(1-V) (Variant A).
    The no-FA payoff in Variant B does not scale with v, which
    dampens the cued-side gain in the high-V VDA window's reward
    differential. Provisional prediction: sup VDA at V=0.75 in
    Variant B is smaller than in Variant A but likely still > 0.005.
    Determines whether the §4.4 / §5.2 wording is wrong in *both*
    variants or only in Variant A. Use the same script substrate
    as CR-026 (Critique/replications/C3--high-V-supremum/run.py)
    with the `variant="B"` switch. Document in
    Critique/replications/C3--high-V-supremum/variant_B/.
  status: queued
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-026. The paper's two variants bracket reward
    structures (A: value-coupled CR; B: fixed CR=1). The CR-026
    finding refutes §4.4 in Variant A only; CR-028 closes the gap.
    Cheap (5–10 minutes of script-run).
  origin: spawned-by-CR-026
  touched: 2026-05-17T18:55:00Z

- id: CR-029
  claim_id: C3
  attack_vector: sensitivity
  task: |
    Map V_critical(r, f_0, h, N) across the paper's secondary
    sweep grid (f_0 ∈ {0.1, 0.3, 0.5, 0.7}, h ∈ {a, √a, a^0.3, a^2},
    N ∈ {2, 4}). Uses the (FAR-corrected, once CR-027 done) closed
    form to predict V_critical at each combination, then numerically
    verifies a few sample points. Output: a heatmap or table
    characterising the "negligible VDA regardless of r" region in
    parameter space — the empirically-correct version of what
    §4.4's "V ≥ 0.75 regardless of r" claim was trying to convey.
    Write under Critique/replications/C3--V-critical-map/.
  status: queued
  priority: low
  prereqs: [CR-027]
  notes: |
    Spawned by CR-026. Depends on CR-027 (FAR-corrected closed
    form). The end product is the experimental-design tool the
    paper's §5.2 should have offered: given an experimenter's
    chosen (N, f_0, h, r), what is the lowest V at which they can
    safely assume "negligible VDA"?
  origin: spawned-by-CR-026
  touched: 2026-05-17T18:55:00Z

- id: CR-030
  claim_id: C3
  attack_vector: literature
  task: |
    Literature search for empirical cueing experiments in the
    predicted *residual high-V VDA window* (V in [0.75, V_critical],
    cost-dominant r, high v). The CR-026 reformulation predicts a
    measurable VDA effect at high V if (r, v) sit in the boundary
    regime. Candidate paradigms in the wiki: Solomon 2004 (cued
    sensitivity at high V, no reward magnitude); Stănișor 2013
    (high-V V1 reward modulation; CR-023 full-depth read still
    queued); Peck 2009 (LIP reward at high V; stub spawned as
    CR-024, not yet executed); Serences 2008 (human fMRI value
    modulation; same CR-024). The search question: do any high-V
    psychophysics studies cross validity with reward magnitude
    AND measure d′ AND find a d′ effect from reward? If yes, that
    is direct empirical validation of the reformulation. If no,
    the field has a clear experimental gap the paper's authors
    should be flagged toward.
    Document at Critique/evidence/C3--reformulation-empirical-test.md.
  status: queued
  priority: low
  prereqs: [CR-023, CR-024]
  notes: |
    Spawned by CR-026. Lower priority than CR-027 / CR-028 because
    the reformulation is already drafted from first principles;
    empirical validation strengthens but does not change the C3
    verdict. The Stănișor full-depth read (CR-023) is the most
    informative single piece of evidence; the Peck and Serences
    stubs (CR-024) would provide convergent neural evidence.
  origin: spawned-by-CR-026
  touched: 2026-05-17T18:55:00Z

- id: CR-031
  claim_id: C4
  attack_vector: literature
  task: |
    Second attack vector on C4 (no-inversion). Two sub-questions
    to be adjudicated against the literature:
    (i) Do any behavioural cueing studies at V ≥ 1/N report eye-
        tracking / microsaccade / fixation-eccentricity signatures
        of α < 1/N (attention allocated *below* the uniform
        baseline at the cued location)? Candidate: gupta_sridharan
        2024 (presaccadic attention not facilitating change
        detection — possibly a behavioural counterexample if
        observers are *actively avoiding* the cued location).
    (ii) Is the distractor-suppression learning literature
         interpretable as behavioural inversion under the model's
         frame? Specifically: Wang & Theeuwes 2018 (Statistical
         learning of distractor locations), Geng 2014 (Attentional
         mechanisms of distractor suppression), Vatterott & Vecera
         2012 (Learning to suppress). These show observers can
         learn to down-weight specific spatial locations — if
         this constitutes α(location) < 1/(N+1) (treating the
         suppressed location like an inverted cue), the no-
         inversion claim has a behavioural counterexample that
         the paper's normative argument does not preclude (because
         the suppressed location is implicitly *anti-cued* in the
         model's V<1/N sense).
    Write at Critique/evidence/C4--no-inversion.md (new file).
  status: done
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-004 (run-006). This is the second attack vector
    required for the C4 verdict to elevate from WEAKLY-SUPPORTED
    to CONFIRMED-UNDER-ATTACK (or to move to CONTESTED if the
    literature has a counterexample). Cheapest path: add stubs for
    Wang & Theeuwes 2018 and Anderson Laurent Yantis 2011 via
    PubMed (CR-032 may execute these stubs first), then summarise
    the suppression-learning literature on whether suppression =
    behavioural inversion in the model's terms. Soft web budget:
    1-2 PubMed fetches.
    [2026-05-19 run-007 start] Marked in_progress at start of
    seventh scheduled run. Attack plan: (1) §11 wiki sweep over
    suppression/capture cluster — Failing & Theeuwes 2018 (full),
    Hickey 2010 (full) already cover value-driven capture and
    statistical-learning-of-distractor-locations; (2) one PubMed
    fetch for Wang & Theeuwes 2018 (the canonical statistical-
    learning-of-distractor-suppression paradigm) → abstract-depth
    stub; (3) adjudicate the analytic crux carried over from
    CR-004/run-006: distractor suppression maps onto the model's
    ANTI-CUED (V<1/N) regime where the model itself predicts
    α*<1/N — so suppression is consistent with the model, not a
    C4 counterexample. Value-driven capture pulls TOWARD value,
    supporting no-inversion at the cued (V≥1/N) location.
    [2026-05-19 run-007 done] Executed as planned. Verdict
    WEAKLY-SUPPORTED → CONFIRMED-CONDITIONAL (C4--no-inversion.md
    Version 0.2). Both sub-questions resolved AGAINST a
    counterexample: (i) no study reports below-uniform allocation
    to a high-value/validly-cued location; value-driven capture
    pulls toward value (Failing & Theeuwes 2018; Hickey 2010);
    Gupta & Sridharan 2024 is a failure-of-facilitation not active
    inversion. (ii) Distractor-suppression learning (Wang &
    Theeuwes 2018a, stubbed; Wang/Samara/Theeuwes 2019 eye-tracking;
    Kong et al. 2020 biased-competition) suppresses the
    high-DISTRACTOR-probability = low-TARGET-probability location =
    anti-cued (V<1/N) in the model, exactly where the model itself
    predicts α*<1/N. Convergence, not contradiction. Kong 2020's
    "suppress here ⇒ more there" positively corroborates §5.1
    zero-sum framing. Label is CONFIRMED-CONDITIONAL not
    CONFIRMED-UNDER-ATTACK because the claim provably fails outside
    V≥1/N. 1 stub added (audit exit 0); 2 PubMed calls. Surfaced an
    unnamed load-bearing assumption (homogeneous uncued allocation)
    → proposed A8 + spawned CR-036; also spawned CR-035 (stub the
    2019/2020 follow-ups) and CR-037 (Anderson 2011 + Geng 2014
    stubs, supersedes the Anderson/Geng half of CR-032).
  origin: spawned-by-CR-004
  touched: 2026-05-19T05:42:00Z

- id: CR-032
  claim_id: C4
  attack_vector: literature
  task: |
    Add wiki stubs for the three foundational papers on value-
    driven attentional capture and distractor-suppression learning,
    so CR-031 has the substrate to cite:
      - Anderson, Laurent & Yantis 2011 — "Value-driven attentional
        capture" (PNAS); the origin paper of the value-driven-capture
        paradigm.
      - Wang & Theeuwes 2018 — "Statistical learning of distractor
        locations" (Cognition or APP); the suppression-learning
        paradigm.
      - Geng 2014 — "Attentional mechanisms of distractor
        suppression" (TICS); the review tying suppression-history
        to distractor-side priority modulation.
    Add each as depth: abstract via PubMed (mission §4.3), following
    SCHEMA.md exactly. Run audit.py after.
  status: abandoned
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-004 (run-006). Prerequisite-ish (not formally,
    but informationally) for CR-031. Cheap; takes ~3 PubMed fetches
    plus 3 stub writes plus 1 audit run. Each fetch costs ~1 of
    the soft cap of 2 per run, so this task should be split across
    two runs (one stub per run) or done as a dedicated wiki-
    augmentation pass.
    [2026-05-19 run-007] ABANDONED as superseded. The Wang &
    Theeuwes 2018 third of this task was completed during CR-031
    (stub wang_theeuwes2018_statistical_learning_distractor_suppression
    added, audit exit 0). The remaining two stubs (Anderson, Laurent
    & Yantis 2011; Geng 2014) are re-homed under CR-037 with a
    cleaner scope. No information lost; this id retired to avoid a
    duplicate-stub race with CR-037.
  origin: spawned-by-CR-004
  touched: 2026-05-19T05:42:00Z

- id: CR-033
  claim_id: C4
  attack_vector: sensitivity
  task: |
    The CR-004 derivation §1 surfaced that the β/γ asymmetric
    scaling produces a **kink** in d'(α) at α = 1/N for any r ≠ 1
    (because the cued is over-allocated with β for α > 1/N and
    under-allocated with γ for α < 1/N, swapping at the kink).
    Test whether the paper's grid-based optimiser (Δα = 0.005)
    handles the kink correctly, or whether the kink can be a
    source of convergence error at coarser α-grids (Δα = 0.02,
    0.05). Compare CR-001 / CR-002 / CR-004 results at the
    primary-grid resolution to a fine-grid (Δα = 0.001) baseline
    at a handful of (r, V, v) cells near the kink. Document at
    Critique/replications/C4--no-inversion/kink_sensitivity/.
  status: queued
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-004 (run-006). Low priority because the paper's
    Δα = 0.005 grid is already 4× finer than what the kink would
    require for convergence to within machine precision; the
    earlier replication results corroborate the paper's numbers
    to within sub-grid resolution. But if any future run finds
    a discrepancy near α = 1/N at coarser grids, this is the
    explanation.
  origin: spawned-by-CR-004
  touched: 2026-05-18T13:30:00Z

- id: CR-034
  claim_id: C4
  attack_vector: re-derivation
  task: |
    Extend the CR-004 anti-cue test (Step C(iii)) to N = 4 with
    V ∈ [0.05, 0.20] (i.e. V < 1/N = 0.25 at N=4). The CR-004
    finding that inversion is globally optimal in the anti-cue
    regime was tested only at N = 2 (where 1/N = 0.5 leaves a wide
    V-band below). Confirm the same closed-form inversion threshold
    r*_inv = (N-1) A_0 / B_0 governs the boundary at N = 4 anti-cue
    cells. Tabulate α* across (V, r) for V ∈ {0.05, 0.10, 0.15,
    0.20}, r ∈ {0.1, 1, 5, 10}, v ∈ {1, 5}, N = 4.
  status: queued
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-004 (run-006). The anti-cue case at N = 4 is
    structurally identical to N = 2 (per the closed-form
    derivation §3), but explicit confirmation would close the
    "different N, same mechanism" loop. Useful for the PRISM
    extension where anti-cue training might be tested with N = 4
    (matching the paper's primary sweep size).
  origin: spawned-by-CR-004
  touched: 2026-05-18T13:30:00Z

- id: CR-035
  claim_id: C4
  attack_vector: literature
  task: |
    Stub the two distractor-suppression follow-ups read at abstract
    depth in run-007 but not yet stubbed (cited in
    Critique/verdicts/C4--no-inversion.md V0.2 by full bibliographic
    reference): Wang, Samara & Theeuwes (2019) "Statistical
    regularities bias overt attention", Atten Percept Psychophys
    81(6):1813-1821, PMID 30919311, DOI 10.3758/s13414-019-01708-5
    (eye-tracking signature of below-baseline allocation at the
    high-distractor location); and Kong, Li, Wang & Theeuwes (2020)
    "Proactively location-based suppression elicited by statistical
    learning", PLoS ONE 15(6):e0233544, PMID 32479531,
    DOI 10.1371/journal.pone.0233544 (biased-competition reallocation;
    behavioural analogue of the paper's §5.1 zero-sum framing). Add
    each as depth: abstract per SCHEMA.md, related to
    wang_theeuwes2018_statistical_learning_distractor_suppression.
    Run audit.py after. Soft budget: PubMed abstracts already in
    run-007 transcript; no new fetch strictly required if working
    from the recorded abstracts, else 1 fetch.
  status: queued
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-031 (run-007). Pure wiki-augmentation; the C4
    verdict already cites both by full bibliographic reference, so
    this does not change the verdict — it makes the citations
    first-class graph nodes. Cheap.
  origin: spawned-by-CR-031
  touched: 2026-05-19T05:42:00Z

- id: CR-036
  claim_id: A8
  attack_vector: replication
  task: |
    Test the (currently unnamed, proposed-A8) HOMOGENEOUS-UNCUED
    ALLOCATION assumption. The model (paper §2.3 / mission §2.3)
    forces every uncued location to receive (1-α)/(N-1) uniformly.
    CR-031 showed the distractor-suppression literature (Wang &
    Theeuwes 2018a; Wang/Samara/Theeuwes 2019; Kong 2020) exercises
    exactly the axis the model cannot represent: observers
    heterogeneously down-weight ONE specific uncued location.
    Extend the model to give one "uncued" location a distinct lower
    target-validity (an anti-cued slot) while holding the others at
    baseline, then optimise allocation over the now-(N)-dimensional
    simplex (or a 2-parameter cued/anti-cued/rest reduction).
    Question: (a) does the optimal policy reproduce a graded
    suppression of the anti-cued location (matching the Wang &
    Theeuwes spatial gradient)? (b) do any C1-C5 headline numbers
    shift when uncued homogeneity is relaxed? Document under
    Critique/replications/A8--heterogeneous-uncued/. Build on the
    existing CR-002 / CR-004 model substrate
    (Critique/replications/C4--no-inversion/run.py).
  status: done
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-031 (run-007). RATIFIED 2026-05-20: A8 is now a
    formal load-bearing assumption in mission §2.7 (skeptical-
    reviewer prompt v0.1 → v0.2, with cross-reference inserted at
    §2.3). The `proposed_mission_change` flag previously on this
    task has been cleared; CR-036 is now a standard A8 replication
    seed. Substantive descendant of CR-031: relax the homogeneous-
    uncued constraint (give one uncued location distinct lower
    target-validity / anti-cued status); ask (a) does optimal
    policy reproduce a graded suppression matching the Wang &
    Theeuwes spatial gradient, and (b) do any C1–C5 headline
    numbers shift when uncued homogeneity is relaxed. Build on the
    Critique/replications/C4--no-inversion/run.py substrate. Feeds
    A2 (single global r) since heterogeneous allocation and
    heterogeneous gain asymmetry are cousins.
    [2026-05-24 run-012 start] Marked in_progress at start of the
    twelfth scheduled run. Picked per mission §3.3 (A8 is the only
    owner-ratified assumption with no verdict file; A1/A2/A4/A5/A6/A7
    OPEN but A8 is the explicit run-011 substantive recommendation and
    bears directly on the PRISM program via the Wang & Theeuwes
    suppression gradient). Attack plan: (1) build a general-N model
    (arbitrary allocation vector a, validity vector w, per-location
    criteria by coordinate ascent) that REDUCES to the homogeneous base
    model and cross-check it reproduces C2 peak VDA ≈0.08 and C1 CF;
    (2) Part 1 — equal-validity uncued, test whether equal allocation is
    the OPTIMUM (not just the assumption) via a curvature/redistribution
    probe at the symmetric point across all four h-forms — concave h
    (√, a^0.3, a) should make homogeneity optimal (A8 innocuous for the
    headline numbers), convex h (a²) may favour concentrating (A8
    load-bearing for the a² secondary sweep); (3) Part 2 — introduce one
    anti-cued slot (lower target-validity) and optimise the full simplex,
    asking whether the optimum reproduces graded suppression matching
    Wang & Theeuwes 2018a/2019/Kong 2020.
    [2026-05-24 run-012 done] DONE. Verdict A8 (none) → WEAKLY-SUPPORTED
    (first touch, one vector: replication;
    Critique/verdicts/A8--heterogeneous-uncued.md V0.1). Built a
    general-N optimal-observer model (arbitrary allocation+validity, per-
    location criteria) that reduces exactly to the homogeneous Eqs.(7)–(9);
    Critique/replications/A8--heterogeneous-uncued/. Caught + fixed a real
    bug: plain coordinate-ascent criterion optimisation stalled in a local
    optimum on one variant-B config (missed joint opt by 0.05) — replaced
    with exact joint grid for G≤2 and multi-restart coord-ascent for G≥3,
    VALIDATED to machine precision vs the C4 base optimiser (G≤2, max|Δ|=
    4.4e-16, incl. the failing config) and a joint 3-D grid (G=3, max|Δ|=0).
    Validation reproduces C2 peak VDA 0.0769@r=0.398 and C1 CF 0.86/0.73/
    0.64 (matches run-003 + CR-022 r=0.3 flag). KEY FINDINGS: (i) A8 is
    INNOCUOUS for C1–C5 — under equal uncued validity, equal-split is the
    OPTIMUM in 32/32 cells (R''(0)<0 every non-degenerate cell; gain 0.0);
    the DECISIVE full-simplex test (Part 1c) shows the unconstrained optimum
    coincides with the homogeneous one at every headline cell (a_cued*→1,
    uncued spread 0, ΔR within 0.05-grid slack). (ii) BUT A8 is NOT a free
    assumption: with a FORCED uncued budget (α=1/N), 8/12 cells prefer to
    CONCENTRATE (R''(0)>0), benefit-dominant (r>1, β>γ) ⇒ winner-take-all,
    cost-dominant ⇒ spread. The headline-claim safety is a STRUCTURAL
    COINCIDENCE: concentrate-favouring r>1 also drives a_cued*→1, so the
    uncued budget vanishes before concentration bites. (iii) Relaxing A8
    ENRICHES the model: one anti-cued slot ⇒ optimum reproduces GRADED
    suppression (a_anti* falls monotonically below uniform and below the
    higher-validity uncued; freed attention reallocated) = the Wang &
    Theeuwes 2018 spatial suppression gradient + Kong 2020 reciprocity;
    confirms CR-031/run-007's conjecture that the model predicts α<1/N at
    anti-cued slots. Deterministic (re-run byte-identical, sha256 53e2d5f9…).
    §11 sweep: wang_theeuwes2018 (key anchor), bisley priority-map ×2,
    koch_ullman1984 + itti_koch2001 (WTA = the concentration tendency),
    desimone_duncan1995 + reynolds1999 + reynolds_heeger2009 (biased-
    competition zero-sum reallocation), coalition_resource_competition
    (PRISM bridge), failing_theeuwes2018, hickey2010 cited; dopamine/RPE/
    FEF/SC/V4/Posner anchors unrelated on inspection. No new wiki stub (all
    relevant papers present → no audit.py needed); 0 web fetches. Spawned
    CR-045 (re-derivation = designated 2nd vector → CONFIRMED-CONDITIONAL),
    CR-046 (finer-grid check of the +6.8e-4 V=1/N corner, low), CR-047
    (N>4 graded-neighbour suppression, low). PRISM implication: trained
    PRISM agents should spread uncued attention homogeneously in the swept
    regimes but show WTA concentration (FiLM = multiplicative gain, βγ=1
    side) and graded anti-cued suppression — checkable vs
    Prism/figures/avg_alpha_trajectories_*.pdf.
  origin: spawned-by-CR-031
  touched: 2026-05-24T02:05:00Z

- id: CR-037
  claim_id: C4
  attack_vector: literature
  task: |
    Add wiki stubs (depth: abstract, via PubMed) for the two
    value-driven-capture / suppression foundational papers still
    missing from research_db, so future C4/A8 runs can quote them
    firsthand rather than via the Failing & Theeuwes 2018 review:
      - Anderson, Laurent & Yantis (2011) "Value-driven attentional
        capture", PNAS — origin of the value-driven-capture paradigm
        (supports C4's no-inversion-at-value: capture is TOWARD
        value, resists suppression).
      - Geng (2014) "Attentional mechanisms of distractor
        suppression", Curr Dir Psychol Sci / TICS — the review tying
        suppression-history to distractor-side priority modulation;
        argues the inhibitory side may be a distinct learning system.
    Follow SCHEMA.md exactly; run audit.py after. Supersedes the
    Anderson/Geng remainder of the abandoned CR-032.
  status: queued
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-031 (run-007). Re-homes the two stubs left over
    after CR-031 completed the Wang & Theeuwes third of CR-032.
    Split across runs if the 2-fetch soft cap binds (1 stub/run).
  origin: spawned-by-CR-031
  touched: 2026-05-19T05:42:00Z

- id: CR-038
  claim_id: C5
  attack_vector: re-derivation
  task: |
    Second attack vector on C5 (the first, CR-005/run-008, was a
    replication that reproduced "max diff 0.0" exactly). Formalise
    the recovery as a short symbolic derivation under
    Critique/derivations/C5--symmetric-recovery.md:
      (1) Show β(1) = 2·1/(1+1) = 1 and γ(1) = 2/(1+1) = 1, both
          EXACT in IEEE-754 binary64, so the asymmetric d'(α) map
          collapses to d'_base + (d'_max f(·) − d'_base), equal as
          REALS to the symmetric d'_max f(·).
      (2) State the Sterbenz sufficient condition as a lemma: if
          {d'_max f(·)} ⊆ [d'_base/2, 2 d'_base] then the float
          round-trip a+(x−a) returns x bit-for-bit, so the two code
          paths are bit-identical (this is the run-008 Block-2
          finding promoted to a proof).
      (3) Note the condition fails for low f_0 (run-008 Block 3),
          giving the precise scope of the literal "0.0".
    If the derivation goes through (it will), elevate C5
    WEAKLY-SUPPORTED → CONFIRMED-UNDER-ATTACK (two distinct vectors,
    two runs, per mission §3.1 / §6). Cheap; no new compute.
  status: done
  priority: medium
  prereqs: [CR-005]
  notes: |
    Spawned by CR-005 (run-008). This is the designated elevation
    vector for C5. The Sterbenz mechanism and the β(1)=γ(1)=1
    exactness are already established numerically in run-008; CR-038
    just promotes them to a stated derivation + lemma so the verdict
    has two independent attack vectors on record.
    [2026-05-22 run start, run-009] Marked in_progress at start of
    the ninth scheduled run. Attack plan: write
    Critique/derivations/C5--symmetric-recovery.md as a symbolic
    re-derivation in three parts — (1) β(1)=γ(1)=1 exact ⇒
    asymmetric(r=1) ≡ symmetric as a real-number identity; (2)
    Sterbenz sufficient-condition lemma ⇒ bit-exactness; (3) scope
    where the literal "0.0" fails (low f_0). Verify the float claims
    numerically in the sandbox (independent of run-008's run.py).
    CR-039 (config-specificity owner note) bundled into this run per
    its own notes (both touch C5, no compute).
    [2026-05-22 run done, run-009] DONE. Derivation written and
    float-verified independently of run.py: Theorem 1 (β(1)=γ(1)=1 ⇒
    asymmetric(r=1) ≡ symmetric, a real-number identity); Theorem 2
    (β(1),γ(1) are exact float 1.0 + multiply-by-1.0 identity +
    Sterbenz lemma ⇒ bit-exact 0.0, because swept x∈[1.0,2.0] ⊂
    Sterbenz band [0.75,3.0] at the validation config); scope clause
    (literal 0.0 fails for f_0 < h(1/N)/(1+h(1/N)) = 1/3 at N=4,√).
    Off-band drift table reproduced run-008's notes to the digit
    (2.78e-17 / 5.55e-17 / 1.11e-16). C5 elevated WEAKLY-SUPPORTED →
    CONFIRMED-UNDER-ATTACK (two distinct vectors, two runs). Spawned
    CR-040 (A3 βγ=1 off-r=1) and CR-041 (owner wording note,
    absorbs/supersedes CR-039).
  origin: spawned-by-CR-005
  touched: 2026-05-22T13:43:19Z

- id: CR-039
  claim_id: C5
  attack_vector: literature
  task: |
    Owner-facing documentation note (no literature fetch needed
    despite the vector tag — it is a clarity flag for the
    manuscript, filed under the C5 verdict's Loose ends). Surface
    that the paper's Appendix-A "maximum difference: 0.0" is EXACT
    only at the validation config (N=4, d'_max=2.0, f_0=0.5, √),
    where the Sterbenz band contains the swept sensitivity range;
    off that config (notably low f_0) the recovery is exact only to
    machine epsilon (~1 ulp), not literally 0.0. Recommend the
    manuscript either (a) keep "0.0" but scope it explicitly to the
    validation config, or (b) report "identical to machine
    precision (≤ 1 ulp)" as the general statement. One paragraph;
    append to the C5 verdict, do not modify the paper.
  status: done
  priority: low
  prereqs: [CR-005]
  notes: |
    Spawned by CR-005 (run-008). Pure clarity flag; does not move
    the verdict. Low priority. Bundle into CR-038's run if convenient
    (both touch C5 and need no compute).
    [2026-05-22 run done, run-009] DONE — addressed inside CR-038's
    run. The C5 verdict v0.2 Loose-end #1 now states the precise
    config-specificity (literal 0.0 exact iff f_0 ≥ h(1/N)/(1+h(1/N))
    = 1/3 at N=4,√; otherwise exact only to ≤1 ulp) and the two
    recommended manuscript wordings. Because the derivation supplies
    the exact threshold, the owner-facing flag is re-homed as the
    cleaner one-line CR-041 (which absorbs this task). Marked done,
    not abandoned, since its deliverable (the owner note) exists in
    the verdict.
  origin: spawned-by-CR-005
  touched: 2026-05-22T13:43:19Z

- id: CR-040
  claim_id: A3
  attack_vector: re-derivation
  task: |
    Attack the additive-conservation assumption A3 (mission §2.7;
    paper §5.5 names it explicitly as "could yield quantitatively
    different results"). The model uses β+γ=2 (additive). The paper
    floats β·γ=1 (multiplicative) as the alternative. KEY OBSERVATION
    from CR-038/run-009: at r=1 BOTH constraints give β=γ=1 (βγ=1 ∧
    β+γ=2 ⇒ β=γ=1), so C5's symmetric recovery is constraint-agnostic
    and the two families AGREE at r=1; they diverge only OFF r=1.
    Re-derive the βγ=1 weight pair as a function of r (β(r)=?, γ(r)=?
    solving βγ=1 with β/γ=r ⇒ β=√r, γ=1/√r), then compare the two
    weight families: where do they diverge most? Does the
    non-monotonic-VDA peak (C2, r≈0.3) move under βγ=1? Does criterion
    dominance (C1) or no-inversion (C4) survive? Reuse the run-008
    symmetric+asymmetric P1 optimiser
    (Critique/replications/C5--symmetric-recovery/run.py) — swap the
    β/γ map and re-run the C2 peak-location and C1 CF probes only (not
    a full 4,410 sweep — one focused slice per mission §8.5).
  status: done
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-038 (run-009), Loose-end #2 of the C5 v0.2 verdict.
    This is the bridge from the now-closed C5 into the assumption
    layer. A3 is attractive because (i) the paper itself flags it in
    §5.5, (ii) the run-008 optimiser substrate is already built and
    validated, (iii) β=√r / γ=1/√r is a clean closed form so a
    re-derivation can predict the divergence before any sweep. The
    paper claims the qualitative findings (non-monotonic VDA, no
    inversion, criterion dominance) "should be robust" to the
    constraint choice — that robustness claim is the actual target.
    [2026-05-22 run start, run-010] Marked in_progress at the tenth
    scheduled run. Confirmed the exact §5.5 target wording from the
    PDF p.8: "the β + γ = 2 constraint conserves total attention
    magnitude; alternative constraints (e.g., multiplicative βγ = 1)
    could yield quantitatively different results, though the
    qualitative findings—non-monotonic VDA, no inversion, criterion
    dominance—should be robust." Attack plan: (1) re-derive β=√r,
    γ=1/√r from βγ=1∧β/γ=r; (2) prove the common-rescaling theorem
    mult=κ(r)·additive with κ(r)=(r+1)/(2√r)=cosh(½ln r)≥1, so βγ=1
    does NOT conserve β+γ (=2κ≥2) — the paper's "conserves total
    magnitude" is additive-only; (3) prove the two-limit theorem
    (VDA→0 at r→0,∞) holds under both constraints ⇒ non-monotonicity
    is constraint-robust; (4) focused slice (run.py swapping β/γ map)
    for the C2 VDA-vs-r peak and C1 CF-vs-r at the reference regime +
    a no-inversion spot-check.
    [2026-05-22 run done, run-010] DONE. Verdict A3 (none) →
    WEAKLY-SUPPORTED. Re-derivation written
    (Critique/derivations/A3--multiplicative-conservation.md): proved
    the rescaling theorem (β_mul,γ_mul)=κ(r)(β_add,γ_add) with
    κ(r)=(r+1)/(2√r)=cosh(½ln r)≥1 (verified 8.9e-16), so βγ=1 does NOT
    conserve Σ=β+γ (=2κ≥2) — the paper's "conserves total magnitude" is
    additive-only — and proved the two-limit theorem holds under both
    rules (β(0)=0, γ(∞)=0 in both). Focused slice
    (Critique/replications/A3--multiplicative-conservation/, exit 0):
    at the reference regime all three §5.5-named findings SURVIVE the
    βγ=1 swap — (i) non-monotonic VDA robust, peak shifts 0.398→0.316
    and rises +14% (0.0797→0.0909; additive 0.0797 matches paper Fig-4
    ~0.080); (ii) no inversion robust within V≥1/N (min α*=1/N exactly);
    (iii) criterion dominance survives but ERODES (CF floor 0.601→0.507,
    only 0.007 above 0.5 at r=10). At r=1 both families return identical
    numbers (free C5 cross-check). Flagged risk: C1 is already CONTESTED
    under additive (run-003: CF→0.304 in low-V/high-v/variant-B cells
    outside this slice); βγ=1 lowers CF wherever R(P1) grows, so those
    cells may push CF<0.5 ⇒ criterion dominance could BREAK there. That
    is the one place A3 → CONTESTED; needs CR-008 (promoted to the
    designated second vector). §11 sweep: reynolds_heeger2009 (divisive
    normalization ⇒ βγ=1 is the more mechanism-aligned rule) is the
    standout cite; dopamine/RPE/LIP/FEF/saccade anchors unrelated
    (value-source, not conservation-form). No stub added; 0 web fetches.
    Spawned CR-042 (sensitivity), CR-043 (literature). Recommended next:
    CR-008.
  origin: spawned-by-CR-038
  touched: 2026-05-23T03:52:00Z

- id: CR-041
  claim_id: C5
  attack_vector: literature
  task: |
    Owner-facing manuscript-clarity flag (no fetch; vector tag is
    nominal — filed under the C5 verdict Loose ends). Absorbs/
    supersedes CR-039 now that CR-038 has supplied the exact
    threshold. Surface to the owner: Appendix-A "maximum difference:
    0.0" is PROVEN exact at the validation config (N=4, d'_max=2.0,
    f_0=0.5, √) but is NOT universal — off the Sterbenz band (f_0 <
    h(1/N)/(1+h(1/N)) = 1/3 for √,N=4) the recovery is exact only to
    ≤1 ulp. Recommend the manuscript either (a) scope "0.0" to the
    validation config explicitly, or (b) state "identical to machine
    precision (≤1 ulp)" as the general claim. One line; already
    drafted in the C5 v0.2 verdict — this task just tracks owner
    sign-off. Do NOT modify the paper.
  status: queued
  priority: low
  prereqs: [CR-038]
  notes: |
    Spawned by CR-038 (run-009). Re-homes CR-039 with the exact
    threshold attached. Pure documentation; does not move the
    verdict. Bundle into any future C5-adjacent run or hand directly
    to the owner.
  origin: spawned-by-CR-038
  touched: 2026-05-22T13:43:19Z

- id: CR-042
  claim_id: A3
  attack_vector: sensitivity
  task: |
    CR-040/run-010 found that under βγ=1 the C2 VDA peak shifts LEFT
    (r 0.398→0.316) and UP (+14%) at the reference regime (f_0=0.5,
    h=√). Does this peak-shift direction persist across the f_0 and h
    secondary sweeps the paper reports in §4.6? The mechanism: the
    multiplicative inflation κ(r)=(r+1)/(2√r) interacts with the
    CR-001 closed-form escape thresholds r†(v)=G_u/[(N-1)G_c(v)],
    which themselves depend on f_0 and h. Predict, then verify on a
    handful of (f_0,h) points (e.g. f_0∈{0.1,0.3,0.7}, h∈{a,a^0.3,a^2}),
    reusing the swappable β/γ map in
    Critique/replications/A3--multiplicative-conservation/run.py. Cheap
    sensitivity probe; one focused slice (mission §8.5). Outcome feeds
    whether the A3 "qualitatively robust" statement is uniform across
    the secondary sweep or only holds at the f_0=0.5,√ reference.
  status: queued
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-040 (run-010), C2-peak-shift loose end. Lower
    priority than CR-008 (which decides whether A3 moves to CONTESTED);
    this one only sharpens the WEAKLY-SUPPORTED→CONFIRMED-CONDITIONAL
    quantitative story. Reuses the run-010 substrate.
  origin: spawned-by-CR-040
  touched: 2026-05-23T03:52:00Z

- id: CR-043
  claim_id: A3
  attack_vector: literature
  task: |
    CR-040/run-010 surfaced (via the §11 sweep of
    reynolds_heeger2009_normalization) that divisive normalization —
    the canonical neural model of attention — is a multiplicative/
    divisive operation, so the βγ=1 alternative the paper dismisses is
    arguably MORE biologically apt than the additive β+γ=2 it uses.
    The wiki's reynolds_heeger2009 entry supports this at review depth.
    Strengthen it with a firsthand primate citation that directly
    contrasts additive vs divisive/multiplicative conservation of
    attentional gain ACROSS LOCATIONS (not just within a single RF).
    Candidates: Lee & Maunsell 2009 (normalization model of attention,
    PNAS / J Neurosci); Ni, Ray & Maunsell 2012 (tuning-curve vs
    normalization); Reynolds & Chelazzi 2004 (already stubbed). Add at
    most one new abstract-depth stub via PubMed per SCHEMA.md; run
    audit.py. ≤1 fetch.
  status: queued
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-040 (run-010), A3 verdict Loose-end #3. Bears on the
    "βγ=1 is the more mechanism-aligned rule" point in the A3 verdict
    and on §5.4's gain(β)-vs-suppression(γ) interpretation of r. Pure
    literature accretion; does not by itself move the A3 verdict but
    upgrades a review-depth citation to a firsthand one.
  origin: spawned-by-CR-040
  touched: 2026-05-23T03:52:00Z

- id: CR-044
  claim_id: A3
  attack_vector: sensitivity
  task: |
    Grid-robustness spot-check on the CR-008 criterion-dominance flips.
    CR-008/run-011 found that βγ=1 doubles the criterion-subordinate
    fraction (additive 4.01% → multiplicative 8.34% of the 4,410-cell
    grid; 191 cells flip from CF≥0.5 to CF<0.5) at run-003's Δα=0.02
    grid. The ΔCF magnitudes driving the flips are 0.03–0.11 (15–50× the
    grid error CR-002 validated at ≤0.002), so the DIRECTION and the
    DOUBLING are grid-robust, but the exact count "191" is grid-dependent
    at the unit level. Re-run the multiplicative CF on the borderline
    flips (CF_mult ∈ [0.48, 0.50) and CF_add ∈ [0.50, 0.52)) at Δα=0.005,
    Δc=0.025 and report the tightened flip count. Reuse
    Critique/replications/A3--multiplicative-conservation/cr008_cf_floor/
    cr008_run.py (parameterise the α/c grids). Outcome: confirms the
    CONTESTED verdict's "≈doubles / ≈191 flips" to ±a few; does not move
    the verdict (the central-tendency survival and the corner location
    are resolution-independent).
  status: queued
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-008 (run-011), A3 v0.2 Loose-end #1. Pure resolution
    hygiene; the CONTESTED label does not depend on it. Cheap (<60 borderline
    cells × 2 maps at the finer grid). Lower priority than CR-042 (which
    asks the load-bearing question of whether the doubling holds across the
    f0/h secondary sweep).
  origin: spawned-by-CR-008
  touched: 2026-05-24T01:55:00Z

- id: CR-045
  claim_id: A8
  attack_vector: re-derivation
  task: |
    Second attack vector on A8 (first was CR-036/run-012 replication, which
    left A8 WEAKLY-SUPPORTED). Prove analytically, from the §2 model, the two
    propositions the replication established numerically:
    (a) HOMOGENEITY-OPTIMALITY under equal uncued validity. With uncued
        locations exchangeable (equal validity, value 1), E[R] as a function
        of the uncued allocation vector (fixed sum, criteria re-optimised) is
        SYMMETRIC; show it is Schur-CONCAVE on the uncued simplex for concave-
        or-linear h (so the equal split is the maximiser), and identify the
        sign of the redistribution Hessian R''(0) ∝ d²/da²[w_u·HR(d'(a)) +
        CR-side log(1−FAR)] — negative for diminishing/linear h. This is the
        clean version of the Part-1 curvature result.
    (b) CUED-ABSORPTION PRE-EMPTION. Where the uncued subspace favours
        concentration (R''(0)>0, the benefit-dominant r>1 regime via β>γ),
        prove the cued allocation is driven to α*=1 (single-location winner-
        take-all on the highest-validity slot), so no uncued budget survives
        and A8 never binds at the model's own optimum. Tie to the location-
        count / value-weight machinery already in
        Critique/derivations/C4--no-inversion.md.
    If both go through, A8 elevates WEAKLY-SUPPORTED → CONFIRMED-CONDITIONAL
    (conditional on equal uncued validity). Write
    Critique/derivations/A8--homogeneity-optimality.md.
  status: done
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-036 (run-012), A8 v0.1 Loose-end #1 — the DESIGNATED second
    vector for A8 elevation. Re-derivation (not replication): the replication
    already gives the numbers; what is missing is the closed-form Schur-
    concavity argument + the cued-absorption lemma. Reuses the C4 closed-form
    boundary machinery. This is the recommended next pick for the A8 thread;
    it mirrors how CR-038 elevated C5 and CR-040→CR-008 advanced A3.
    [2026-05-24 run-013 start] Marked in_progress at start of the thirteenth
    scheduled run. Picked per mission §3.3 (A8 is the ONLY WEAKLY-SUPPORTED
    verdict now A3 is CONTESTED; prereqs none) and the explicit run-012
    recommendation. [Attack plan elided — see start-note above / derivation.]
    [2026-05-24 run-013 done] DONE. Verdict A8 WEAKLY-SUPPORTED →
    CONFIRMED-CONDITIONAL (second vector, re-derivation, after CR-036
    replication). Both propositions PROVEN. (a) HOMOGENEITY-OPTIMALITY: E[R] is
    a symmetric fn of the uncued allocation ⇒ equal split is ALWAYS a critical
    point on the uncued simplex (exact, ∀r,h; numerically R'(0)=O(1e-5)); the
    S_{N-1} action on the zero-sum tangent space is the irreducible standard
    rep ⇒ restricted Hessian = single scalar λI (Schur's lemma); closed-form
    λ=λ_HR+λ_noFA (derivation Eq.2.4) MATCHES a fixed-criterion finite diff to
    5 d.p. across all four h, r∈{0.398,0.5,1,2}; λ_noFA=Q[G²g'²(logG)''+GG_d g'']
    ≤0 UNCONDITIONALLY for concave/linear h (Φ log-concave ⇒ (logG)''<0) — the
    no-FA channel is a pure spreading force; so λ<0 (equal split=strict max) for
    a^0.3,√a,a; only accelerating a² flips λ>0 (+0.024..+0.048). The
    forced-uniform-budget concentration (CR-036 Part 1b) is a CUSP not a
    curvature: at α=1/N the uncued sit on the β/γ kink, V(t)=V(0)+m|t|+O(t²)
    with sign(m)=sign(β−γ)=sign(r−1) (one-sided slope→const, 2nd-diff∝1/ε —
    verified); CR-036's finite "R''>0" was the cusp slope. (b) CUED-ABSORPTION:
    the two concentration pressures (accelerating h; benefit-dominant kink r>1)
    are subsets of WTA, and by w_c≥w_u (C4 Eq.6.4, V≥1/N,v≥1) + the
    location-count asymmetry (only cued reaches d'_max) the cued wins the budget
    first ⇒ α*→1, B→0 — FASTEST exactly for accelerating a² that most wanted to
    concentrate (perfect anti-correlation). Joint (α, uncued-winner-share)
    optimum from scratch on Δα=0.005: max|ΔR_uncon−homog|=1.4e-4 over ALL four h
    and ALL swept cells (=0 EXACTLY for a², where α*=1,B=0). So A8 never binds
    at the model's own optimum. Conditional on equal uncued validity (het.
    validity → suppression gradient = scope enrichment, not C1–C5 bias) + the
    vacuous degenerate v=1,V=1/N corner. A8 = the BEST-defended simplification
    (contrast A3 CONTESTED): the optimiser would make A8's choice unprompted.
    Deliverables: Critique/derivations/A8--homogeneity-optimality.md +
    Critique/replications/A8--heterogeneous-uncued/cr045_rederivation_check/
    (2 scripts + output logs). §11 sweep: no new lit (re-derivation internal +
    C4 machinery); log-concavity-of-Φ / Schur / majorization have NO wiki
    substrate (expected math-methods gap, mirrors C5 floating-point gap); no
    new stub ⇒ no audit.py. 0 web fetches. Spawned CR-048 (A2×A8 interaction:
    does heterogeneous r_i break homogeneity-optimality? — the connective task
    the symmetry argument exposed). Downgraded CR-046 (now EXPLAINED as the
    vacuous degenerate corner). PRISM: softmax allocation = the A8-relaxed
    model ⇒ homogeneous uncued spread in swept regimes (optimal, not just
    allowed), WTA only if learned transfer accelerates AND cued hasn't absorbed.
  origin: spawned-by-CR-036
  touched: 2026-05-24T05:05:00Z

- id: CR-046
  claim_id: A8
  attack_vector: sensitivity
  task: |
    Finer-grid check of the single positive ΔR in CR-036/Part-1c: at
    (V=1/N=0.25, v=1, r=2, √, variant A) the full simplex beat the
    homogeneous optimum by +6.8e-4 with a_cued*≈0.10 and uncued spread 0.30.
    This is within the 0.05 allocation-grid slack AND at the degenerate V=1/N
    boundary where cued/uncued labels are meaningless (cf. CR-019). Re-run the
    full simplex at Δ=0.02 (and the homogeneous α at Δ=0.005, already fine) at
    this cell and a small neighbourhood (V∈{0.25,0.28}, r∈{1.5,2,3}, v=1) to
    confirm ΔR collapses to ≤ grid slack and a_cued*→1 (or the symmetric tie)
    once resolution is matched. Reuse
    Critique/replications/A8--heterogeneous-uncued/run.py (parameterise the
    simplex step). Does NOT move the A8 verdict — pure resolution hygiene at
    the degenerate boundary.
  status: queued
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-036 (run-012), A8 v0.1 Loose-end #2. Cheap. The +6.8e-4 is
    almost certainly the coarse-simplex-vs-fine-α grid mismatch at the V=1/N
    symmetric degeneracy (multiple equivalent single-location optima), not a
    genuine heterogeneous-allocation benefit. Confirming it closes the only
    numerical loose thread in the A8 "A8 never binds at the optimum" claim.
    [2026-05-24 run-013] DOWNGRADED (still low). The CR-045 re-derivation already
    EXPLAINS this corner analytically: at V=1/N,v=1 the cued/uncued weights are
    equal (w_c=w_u, C4 Eq.6.4 equality), labels are meaningless (cf. CR-019), and
    at the forced kink r>1 the model is genuinely indifferent among single-winner
    policies — the +6.8e-4 is the value-blind degenerate boundary and CANNOT
    touch any C1–C5 number. CR-046 remains worthwhile resolution-hygiene but no
    longer guards the A8 verdict (it is now proven non-binding for the headline
    claims regardless of this corner).
  origin: spawned-by-CR-036
  touched: 2026-05-24T05:05:00Z

- id: CR-047
  claim_id: A8
  attack_vector: replication
  task: |
    Extend the CR-036 Part-2 anti-cued test from ONE anti-cued slot at N=4 to
    a GRADED VALIDITY PROFILE across N>4 uncued locations — a closer match to
    the Wang & Theeuwes (2018) "spatial gradient of suppression scaled with
    distance from the high-distractor location". Set up N∈{6,8} with uncued
    target-validities decaying with index (a 1-D "distance" proxy), optimise
    the simplex (value-blind v=1, cost-to-symmetric r), and test whether the
    optimal allocation reproduces a MONOTONIC suppression gradient (not just a
    single suppressed slot). If yes, the A8-relaxed model quantitatively
    matches the empirical distance-gradient — a positive result strengthening
    the "relaxing A8 enriches the model" finding and the PRISM prediction.
    Document under Critique/replications/A8--graded-suppression/. Reuse the
    general-N model in
    Critique/replications/A8--heterogeneous-uncued/run.py.
  status: queued
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-036 (run-012), A8 v0.1 Loose-end #3. The general-N model is
    already built and validated, so this is mostly a validity-profile + plot
    task. Lower priority than CR-045 (the elevation vector). Feeds the PRISM
    prediction: a PRISM run with a graded distractor-probability profile is
    the empirical analogue. Also feeds A2 (heterogeneous gain asymmetry is the
    cousin of heterogeneous allocation).
  origin: spawned-by-CR-036
  touched: 2026-05-24T02:05:00Z

- id: CR-048
  claim_id: A2
  attack_vector: re-derivation
  task: |
    A2×A8 INTERACTION (surfaced by the CR-045 re-derivation). A8's homogeneity-
    optimality proof rests entirely on the uncued slots being EXCHANGEABLE,
    which requires (i) equal uncued validity AND (ii) a single global asymmetry
    ratio r (assumption A2). Under a HETEROGENEOUS gain asymmetry r_i (location-
    /feature-specific β_i,γ_i — the empirical situation A2 abstracts away), the
    uncued slots are NO LONGER exchangeable even at equal validity, so the
    exchange-symmetry argument (CR-045 §1) fails and the equal split need not
    even be a critical point of E[R] on the uncued simplex. Re-derive: with
    uncued slots carrying distinct r_i, (a) is equal-split still a critical
    point? (No, generically.) (b) Does the deviation from equal-split scale with
    var(r_i), and is it bounded by the cued-absorption pre-emption (CR-045 §4)
    the same way the homogeneous case was — i.e. does B→0 still neutralise it at
    headline cells? (c) Quantify whether a plausible spread of r_i (e.g. ±30%
    around the global r) shifts any C1/C2 headline number beyond the 1.4e-4
    slack CR-045 found for the homogeneous case. This is the bridge that unifies
    A2 (single-global-r), A3 (conservation form, CONTESTED), and A8 (allocation
    geometry, CONFIRMED-CONDITIONAL) into one "heterogeneity" arc. Write
    Critique/derivations/A2xA8--heterogeneous-r-allocation.md.
  status: done
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-045 (run-013), A8 v0.2 Loose-end #3. The A8 re-derivation made
    explicit that homogeneity-optimality is A2-CONDITIONAL (needs a single global
    r), so this is the natural next step in the assumption layer and a concrete,
    bounded re-derivation (reuses the general-N model in
    Critique/replications/A8--heterogeneous-uncued/run.py — just let r be a
    per-location vector). Sequence-wise, can be folded into CR-007 (the broad A2
    literature survey) or run first as the analytic half. Medium priority: it is
    the most leveraged A2 entry because it connects three assumption verdicts.
    [2026-05-24 run-014] PROMOTED to the designated A2 SECOND VECTOR and the
    recommended next pick, now that CR-007/run-014 created the A2 verdict at
    WEAKLY-SUPPORTED. The run-014 literature attack established the R1/R2 split
    (between-preparation r is benign — the sweep handles it; within-display
    heterogeneous r_i is empirically real but its C1–C5 consequence is
    unresolved). CR-048 is exactly that unresolved re-derivation: let r be a
    per-location vector and test (a) whether equal-split stays a critical point
    of the uncued simplex (generically no — A8 exchange symmetry breaks even at
    equal validity), (b) deviation ∝ var(r_i) bounded by cued-absorption
    pre-emption (CR-045 §4), (c) whether a ±30% spread moves any C1/C2 number
    beyond the 1.4e-4 homogeneous-case slack. Outcome → A2 CONFIRMED-CONDITIONAL
    (R2 also bounded) or CONTESTED (shifts a headline claim). Reuses the
    general-N model in Critique/replications/A8--heterogeneous-uncued/run.py
    (let r be per-location).
    [2026-05-24 run-015 start] Marked in_progress at start of the fifteenth
    scheduled run. Picked per mission §3.3 (A2 is the only WEAKLY-SUPPORTED
    verdict; CR-048 is its designated second vector; no unsettled prereqs) and
    the explicit run-014 recommendation. Attack plan: (1) re-derive the tangent
    gradient of E[R] on the uncued simplex at equal-split under heterogeneous
    r_i and show it is generically nonzero (∝ spread of γ_i), zero iff r_i all
    equal — equal-split is generically NOT a critical point (the A2×A8 break);
    (2) show the reward deviation from re-optimising the uncued split scales as
    O(var(r_i)/|λ|) (second order in the spread), and that the cued-absorption
    pre-emption (CR-045 §4 / C4 §6) is STRUCTURALLY r-independent so at
    benefit-dominant / headline cells α*→1, B→0 neutralises it; (3) numerically
    verify (gradient nonzero, ΔR ∝ var quadratic) and run the C1/C2 headline
    test — ±30% uncued r_i spread, max|ΔVDA|, max|ΔCF| vs the homogeneous
    baseline, plus the A8-imposed-vs-relaxed gap. Re-derivation (not literature)
    because A2's empirical premise was already settled by CR-007; the open
    question is the analytic CONSEQUENCE for C1–C5 under within-display
    heterogeneity (R2).
    [2026-05-24 run-015 done] DONE. Verdict A2 WEAKLY-SUPPORTED →
    CONFIRMED-CONDITIONAL (second vector, re-derivation; mission §3.1/§6).
    Deliverables: Critique/derivations/A2xA8--heterogeneous-r-allocation.md +
    Critique/replications/A2xA8--heterogeneous-r/ (2 scripts + output;
    results.json sha256 2659d7b5…, byte-identical on re-run). FINDING: the
    A2×A8 interaction is real but BOUNDED — no headline claim shifted. (a)
    Heterogeneous r_i break the uncued exchange symmetry, so equal-split is
    GENERICALLY NOT a critical point: closed-form tangent gradient g_i =
    M_i·γ_i·ρ depends on slot i only through r_i (Eq.1.2), ‖g−mean‖=0.072 at
    ±30% vs exactly 0 at homogeneity; the optimum tilts budget toward the more
    cost-dominant (smaller-r_i) slots. (b) BUT the restricted Hessian stays
    neg-def on the smooth branch by the SAME log-concavity-of-Φ argument as
    CR-045 §2.2 applied PER SLOT (the no-FA spreading force is r-independent in
    sign), so the optimal tilt is O(spread) and its reward O(var r_i):
    max ΔR=1.50e-4 over all interior cells at ±30% = the CR-045 homogeneous
    grid slack. (c) Cued-absorption pre-emption (C4 §6) is STRUCTURALLY
    r-independent → α*→1, B→0 at every value-contrast cell (ΔR=0 exactly at the
    C2 headline cell); the cost-dominant P3 kink keeps equal-split optimal
    (ΔR=0 → criterion fraction UNTOUCHED by the A8-relaxation). LEVEL effect
    (A8 imposed): C2's VDA peak essentially fixed (0.0771→0.0770, r_peak=0.398)
    → C2 REFRAMES in r_cued (run-014 conjecture confirmed); C4 robust
    (r-independent geometry); C1 contested corner NOT deepened (0.3040→0.3055).
    Validation: spread=0 reproduces the single-r model exactly (C2 peak
    0.0771@0.398; C1 CF 0.866/0.729/0.640, matching run-003/010/012 + CR-022
    flag). Label CONFIRMED-CONDITIONAL not -UNDER-ATTACK: the PREMISE is false
    under R2 (confirms safety despite a false premise) and safety is conditional
    on equal uncued validity + moderate r_i spread. Completes the A2/A3/A8
    heterogeneity arc: A8 + R1-A2 discharged by the optimiser's own behaviour;
    only A3 (conservation form) CONTESTED. §11 sweep: the v0.1 gain-heterogeneity
    cluster re-cited (reynolds_heeger2009, mcadams_maunsell1999_v4_tuning,
    treue_martinez_trujillo1999, sani2017, ghose_maunsell2002, carrasco2011,
    maunsell2015, reynolds_chelazzi2004) + WTA (koch_ullman1984, itti_koch2001)
    + wang_theeuwes2018 (het-validity scope) + luo_maunsell2018 (A1/A6 bridge) +
    LIP priority-map (bisley×2, rust_cohen2022) + coalition_resource_competition;
    cameron2002 surfaced, unrelated on inspection; value-source anchors unrelated.
    Math-methods gap (majorization/Schur/log-concavity, S_{N-1} rep) — no wiki
    substrate, flagged not filled (mirrors C5/A8 gaps). No new stub → no audit.py;
    0 web fetches. Spawned CR-051 (extreme-spread stress test, low). UNBLOCKED
    CR-049 (C2-reframing replication — prereq CR-048 now done) + de-risked it
    (the O(var r_i) bound says moderate spreads are the informative ones).
  origin: spawned-by-CR-045
  touched: 2026-05-24T15:58:00Z

- id: CR-049
  claim_id: A2
  attack_vector: replication
  task: |
    C2-reframing under heterogeneous gain asymmetry. The CR-007/run-014
    literature attack showed that under within-display heterogeneity (R2),
    "VDA vs r" is no longer a univariate curve, but conjectured that the
    non-monotonicity persists in the CUED location's ratio r_cued with the
    uncued r_i as nuisance parameters. Test it: using the general-N model in
    Critique/replications/A8--heterogeneous-uncued/run.py with a per-location
    r vector, plot VDA vs r_cued at the reference regime (N=4, d'_max=2, f0=0.5,
    √, V=0.5, v=5, variant A) for several fixed spreads of uncued r_i (e.g.
    uncued r_i drawn uniform on [r_cued/k, r_cued·k] for k ∈ {1, 1.5, 3}), and
    report (i) whether the non-monotonic peak persists, (ii) how the peak
    location/height move with var(r_uncued), (iii) whether the peak stays in
    the cost-dominant region (r_cued ≈ 0.3). If the peak persists and moves
    smoothly, C2 REFRAMES (survives as a statement about r_cued); if it
    vanishes or relocates wildly, C2 is R2-fragile and the verdict for A2 (and
    C2's scope) moves. Document under
    Critique/replications/A2--heterogeneous-r-C2/.
  status: queued
  priority: medium
  prereqs: [CR-048]
  notes: |
    Spawned by CR-007 (run-014), A2 v0.1 Loose-end #2. Lower priority than
    CR-048 (the analytic A2×A8 interaction, which settles the A2 verdict
    label); CR-049 is the numerical C2-specific follow-up that sharpens the
    "C2 reframes vs refutes" sub-question. Prereq CR-048 because the analytic
    boundedness result should guide which r_i spreads are worth simulating.
    [2026-05-24 run-015] PREREQ DISCHARGED — CR-048 done; CR-049 is now
    unblocked. De-risked: the CR-048 re-derivation proved the level effect is
    O(var r_i) and the A8-relaxation deviation ≤1.5e-4, so the C2 peak is
    expected to stay near r_cued≈0.36–0.40; CR-048's coarse-grid first pass
    already shows the peak fixed at 0.0771@0.398 under ±30% and 0.0765–0.0798
    @≈0.36 for k=1.5/3. CR-049 is now the full-resolution confirmation (paper's
    Δα=0.005, 41-pt r-grid), not an open question — LOW/MEDIUM, optional polish.
  origin: spawned-by-CR-007
  touched: 2026-05-24T15:58:00Z

- id: CR-050
  claim_id: A2
  attack_vector: literature
  task: |
    Owner-facing §5.4 clarity note (nominal literature vector — no fetch
    needed; filed under the A2 verdict Loose ends). Surface that the model's
    parameterisation β(r)=2r/(r+1) ≥ 0 assumes the gaining location's d'
    departure is always non-negative — i.e. attention never *impairs* the
    attended location. But carrasco2011 (Yeshurun & Carrasco texture
    segmentation) documents a real regime where attention HURTS performance at
    some eccentricities/spatial scales (the "central performance drop"), i.e.
    an effective β < 0. This regime is OUTSIDE the model's r > 0
    parameterisation entirely. Recommend the manuscript's §5.4 biological-
    interpretation paragraph add a one-line scope note: the single-r
    parameterisation, beyond being a single scalar (the §5.5 limitation),
    also excludes the documented attention-impairs regime. One paragraph;
    append to the A2 verdict Loose ends; do NOT modify the paper.
  status: queued
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-007 (run-014), A2 v0.1 Loose-end #3. Pure clarity flag;
    does not move the verdict. Overlaps in spirit with the existing CR-016
    (maunsell_treue2006 stub) only insofar as both touch the FBA literature;
    can be batched into any future A2-adjacent run or handed to the owner.
  origin: spawned-by-CR-007
  touched: 2026-05-24T05:58:00Z

- id: CR-051
  claim_id: A2
  attack_vector: sensitivity
  task: |
    EXTREME-SPREAD stress test of the CR-048 O(var r_i) bound. The A2 verdict
    is CONFIRMED-CONDITIONAL conditional on a MODERATE uncued-r spread (CR-048
    found max ΔR=1.5e-4 at ±30%, = the homogeneous slack). Probe the boundary:
    drive one uncued slot's r_i → 0 (pure cost) or → ∞ (pure benefit) while the
    cued and other uncued stay moderate, at the cost-dominant interior cells
    (V=0.5, v=1, r_cued∈{0.2,0.3,0.4}) where the uncued budget is largest, and
    measure whether the A8-relaxed allocation deviation ΔR and the C1/C2 headline
    numbers degrade past grid resolution. If ΔR stays small → the conditional can
    be widened (drop "moderate"); if it blows up → name the spread threshold at
    which A2's safety fails. Reuse Critique/replications/A2xA8--heterogeneous-r/
    (let the spread factor exceed 1, i.e. one r_i ≪ r_cued).
  status: queued
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-048 (run-015), A2 v0.2 Loose-end #2. Low priority: an extreme
    single-slot r_i (≈0 or ≈∞ within one display) is empirically implausible
    (no preparation puts one location in pure-cost and its neighbour in
    pure-benefit), so this is a robustness-of-the-conditional probe, not a
    likely refutation. Does not move the A2 label unless ΔR blows up. Cheaper as
    a sensitivity probe than a full re-derivation.
  origin: spawned-by-CR-048
  touched: 2026-05-24T15:58:00Z

- id: CR-052
  claim_id: A1
  attack_vector: re-derivation
  task: |
    A1 SECOND VECTOR (the designated decider). Test the sign of the paper's
    §5.5 self-characterisation that independence makes the reported numbers
    "an upper bound on VDA benefit." Re-derive the no-change-trial false-alarm
    aggregation under a correlated decision model — equicorrelated-Gaussian (or
    Gaussian-copula) decision variables with cross-location correlation ρ, so
    P_no-fa = Φ_N(c; R_ρ) replaces the Eq. (9) product (run-016 showed by
    Slepian's inequality that Φ_N(c;R_ρ) ≥ Π(1-FAR_i) for ρ>0, monotone — the
    independent product is the FA-penalty-maximising corner). RE-OPTIMISE the
    per-location criteria (and α) under the correlated P_no-fa, recompute the
    criterion fraction (C1) and VDA benefit (C2) at the headline cell
    (V=0.5, v=5, N=4, d'_max=2.0, f_0=0.5, √) for ρ ∈ [0, 0.4] bracketing the
    Cohen & Maunsell r_SC range, both variants. DECISION RULE: if VDA rises
    materially with ρ → the "upper bound on VDA" claim FAILS → A1 → CONTESTED
    (and §5.2 design advice inherits the error); if VDA falls or is flat → the
    claim holds within scope → A1 → CONFIRMED-CONDITIONAL. Either way report the
    direction and magnitude of the criterion-fraction shift (C1 is computed at
    ρ=0, the stiffest-FA-penalty corner). Code under
    Critique/replications/A1--correlated-fa/ (reuse the C5/A3 P1 optimiser
    substrate); the MVN-orthant evaluation needs scipy.stats.multivariate_normal
    or a Genz routine — if the sandbox lacks it, an equicorrelated 1-D Gaussian-
    mixture reduction (condition on the shared factor, integrate) is exact for
    the equicorrelation case and avoids the MVN-CDF dependency.
  status: done
  priority: high
  prereqs: [CR-005]
  notes: |
    Spawned by CR-006 (run-016), A1 v0.1 decisive loose end. Promoted to HIGH:
    it is the only path to settle A1 (CONFIRMED-CONDITIONAL vs CONTESTED), it
    tests a DIRECTIONAL claim the paper actively uses (§5.5 "upper bound" →
    §5.2 design advice), and it is the second vector required by §6 for any
    elevation. The equicorrelation reduction (condition on a shared latent
    factor z~N(0,1): each location FAs independently given z with criterion
    c_i - √ρ·z, then integrate over z) makes P_no-fa = ∫ Π_i Φ((√ρ z - c_i)/√(1-ρ)) φ(z) dz
    — a 1-D quadrature, no MVN-CDF needed, exact. This is the clean substrate.
    Prereq CR-005 = the P1 optimiser. The hardest honest sub-question: where to
    book correlation-mediated sensitivity — if folded into d'(α) it is already
    in the model (so the binding assumption is purely I-dec, the FA product);
    if treated as a separate channel it is the omitted lever. Re-derive both
    bookings and report which makes "upper bound" hold.
    [2026-05-25 run-017 start] Marked in_progress at start of the seventeenth
    scheduled run. Picked per mission §3.3 (A1 is the only WEAKLY-SUPPORTED
    verdict; CR-052 is its prereq-settled (CR-005 done) HIGH second vector) and
    the explicit run-016 recommendation. Sandbox has scipy (ndtr) this run, but
    the equicorrelation 1-D shared-factor reduction P_no-fa(ρ) = ∫ Φ((b_c−√ρz)/
    √(1−ρ))·Φ((b_u−√ρz)/√(1−ρ))^{N−1} φ(z) dz (Gauss–Hermite quadrature, no
    MVN-CDF) is used regardless — exact for equicorrelation. Booking decision
    resolved in the derivation: within the paper's Eq. 9 reward, independence is
    operationalised ONLY in the P_no-fa product (hit terms are linear in marginal
    HRs, no cross-location product), so Booking 1 (correlation enters P_no-fa
    only) is the FAITHFUL, COMPLETE relaxation of A1; the I-neur "pooled-d'"
    Booking 2 requires a global detection rule = A6, not A1. Attack plan: (1)
    re-derive P_no-fa(ρ) + Slepian monotonicity; (2) recompute VDA(r) curve
    (V=0.5,v=5,N=4,d'_max=2,f0=0.5,√,variant A) and CF at headline cells for
    ρ∈{0,0.1,0.2,0.3,0.4}; (3) decision rule: peak VDA rises in ρ → CONTESTED;
    falls/flat → CONFIRMED-CONDITIONAL.
    [2026-05-25 run-017 done] DONE. Verdict A1 WEAKLY-SUPPORTED → CONTESTED
    (second vector, re-derivation succeeded). Derivation
    Critique/derivations/A1--correlated-fa-upper-bound.md + replication
    Critique/replications/A1--correlated-fa/ (numeric sha256 b9828f02…,
    byte-identical re-run; 0 web fetches; no new stub → no audit.py).
    BOOKING resolved: Eq. 9's change-trial term is linear in marginal HRs, so
    independence enters ONLY the P_no-fa product → Booking 1 (correlation in
    P_no-fa only) is the faithful/complete A1 relaxation; the pooled-d' Booking 2
    is A6, not A1 (disentangles the two §5.5 clauses). RESULT: the "upper bound
    on VDA" claim FAILS as a uniform statement — dVDA/dρ flips sign at r≈0.5:
    correlation SUPPRESSES VDA in the cost-dominant regime (incl. the headline
    peak) but AMPLIFIES it ~20% in the benefit-dominant tail (r≳0.5), excess
    growing with ρ (+0.0048→+0.0101 for ρ=0.1→0.4); even the headline peak rises
    at ρ=0.1 (0.0811>0.0799). Independence instead upper-bounds the CRITERION
    FRACTION (CF(0)≥CF(ρ) monotone; variant A r=1: 0.728→0.647, r=3.16:
    0.641→0.539 toward 0.5). Headline C2 magnitude ROBUST (peak within 0.4% at
    ρ=0.2). Validation: ρ=0 reproduces C2 peak 0.0799@0.383; Slepian monotonicity
    + independent-corner-is-minimum confirmed. CONTESTED (not REFUTED: magnitudes
    survive; not CONFIRMED-CONDITIONAL: shifted the §5.5→§5.2 directional chain, a
    quantity the paper uses). Reformulation proposed in verdict. Spawned CR-054
    (structured-Σ sensitivity on the VDA tail, low), CR-055 (Booking2=A6
    cross-link note, low). CR-053 (value×correlation, the standing A1 follow-up)
    is the recommended next pick — confirmed a genuine wiki gap this run.
  origin: spawned-by-CR-006
  touched: 2026-05-25T03:05:00Z

- id: CR-053
  claim_id: A1
  attack_vector: literature
  task: |
    A1 completeness follow-up: is the noise-correlation-reduction channel
    VALUE-directed (reward-modulated), or only ATTENTION/validity-modulated?
    The run-016 completeness critique (the model's two tools omit decorrelation,
    which carries >80% of attention's behavioural benefit per cohen_maunsell2009)
    only adds a VALUE channel outside the model if decorrelation tracks reward
    MAGNITUDE, not merely cued/uncued status. Survey for studies that vary
    reward value (not just validity) and measure interneuronal/noise-correlation
    structure. If decorrelation scales with value → the model omits a genuine
    value-directed sensitivity lever and the "criterion captures 60–96% of
    VALUE-related reward" claim is incomplete in a way that bears on C1/C3. If
    decorrelation is value-insensitive → the omission is about attention
    generally, not value specifically, and the model's value-decomposition is
    safe. Document in Critique/evidence/A1--independence.md (append V0.2).
  status: queued
  priority: medium
  prereqs: []
  notes: |
    Spawned by CR-006 (run-016), A1 v0.1 loose end #2. GENUINE WIKI GAP: the
    run-016 value×correlation sweep surfaced only attention-correlation papers
    (cohen_maunsell2009, ruff_cohen2016, srinath2021) and unrelated reward
    papers — no entry addresses reward-modulation of noise correlations. Start
    with stanisor2013_v1_value_attention (V1 value modulation, already in wiki);
    likely needs a web fetch / new stub for Mitchell-Sundberg-Reynolds 2009
    (V4 noise-correlation companion) or a value-×-correlation primate study
    (e.g. work from the Cohen/Kohn labs). Soft cap two fetches. Medium (not
    high): it sharpens the completeness critique but does not settle the A1
    label — CR-052 does that. Best run AFTER CR-052 so the re-derivation tells
    us whether the value-channel question is even consequential.
  origin: spawned-by-CR-006
  touched: 2026-05-24T21:40:00Z

- id: CR-054
  claim_id: A1
  attack_vector: sensitivity
  task: |
    The CR-052 re-derivation refuted a UNIFORM "upper bound on VDA" using the
    simplest correlated model (equicorrelation, ρ≥0) — one counterexample
    suffices. But real cross-location covariance is STRUCTURED: within-area
    correlations fall and between-area rise under attention (ruff_cohen2016),
    and there is a supra-pairwise shared-variance component (srinath2021).
    Probe whether a block / signed-ρ structure (e.g. ρ_cued-uncued ≠
    ρ_uncued-uncued, or a 2-factor model) moves the MAGNITUDE (not the sign) of
    the benefit-dominant VDA amplification found at ρ>0. Reuse the
    A1--correlated-fa P_no-fa(ρ) machinery generalised to a 2-block correlation
    matrix (still a low-dim Gaussian quadrature). Report whether the +20% tail
    amplification grows, shrinks, or reverses. Does NOT change the A1 label
    (already CONTESTED) — it characterises the magnitude for the referee report.
  status: queued
  priority: low
  prereqs: [CR-052]
  notes: |
    Spawned by CR-052 (run-017). The equicorrelation result is sufficient to
    contest the uniform bound; this is magnitude-characterisation, hence low.
    The 2-block reduction conditions on per-block shared factors (Z_cued,
    Z_uncued correlated) — a 2-D quadrature, still no MVN-CDF.
  origin: spawned-by-CR-052
  touched: 2026-05-25T03:05:00Z

- id: CR-055
  claim_id: A6
  attack_vector: re-derivation
  task: |
    Cross-link note + first A6 substrate. CR-052 showed the §5.5 sentence
    conflates A1 ("independent per-location SDT decisions" = the Eq. 9 product,
    now CONTESTED) with A6 ("real observers emit a single global response"). The
    pooled-d' / global-decision reading (Booking 2) is A6, not A1, and has no
    locus in Eq. 9. When CR-011 (A6, heterogeneous/global decision rule) is
    taken, it should (a) reuse the A1--correlated-fa P_no-fa(ρ) machinery and the
    Booking-1/Booking-2 split, and (b) test the CR-052 prediction that a single
    GLOBAL criterion has fewer DOF to exploit value cheaply, so the criterion
    fraction should compound DOWNWARD under A6 the way it fell under ρ (CF
    inversion). This task is a pointer; the real work is CR-011.
  status: abandoned
  priority: low
  prereqs: []
  notes: |
    Spawned by CR-052 (run-017). Effectively a re-scoping note for CR-011 (A6);
    kept as a distinct id so the A1↔A6 booking link is auditable. Could be merged
    into CR-011 at its next touch (mark abandoned-merged then, like CR-003→CR-020).
    [2026-05-25 run-018] ABANDONED-MERGED into CR-011 (executed this run). The
    A6 re-derivation incorporated the Booking-1/Booking-2 split: §5 of
    Critique/derivations/A6--heterogeneous-decision-rule.md treats the "single
    global response" reading (A6-(ii)), derives G_crit^global ≤ G_crit^per-loc
    (strict for v>1, V≠1/N) ⇒ the predicted CF compound-down, and notes the
    pooled-decision overlap with the (already-CONTESTED) A1 FA product. The
    quantitative single-global-criterion sweep is the spawned CR-056. CR-055
    closed.
  origin: spawned-by-CR-052
  touched: 2026-05-25T15:58:00Z

- id: CR-056
  claim_id: A6
  attack_vector: replication
  task: |
    A6 SECOND VECTOR (the designated decider). Test the §5.5 "single global
    response" reading head-on: constrain the decision rule to a SINGLE GLOBAL
    CRITERION c_c = c_u = c (one response threshold) in the C1 criterion-
    fraction optimiser, re-run the paper's 4,410-cell primary grid, and measure
    the criterion-fraction shift vs the paper's per-location-criterion model.
    The A6 derivation (ineq. 12) proves G_crit^global ≤ G_crit^per-loc with
    strict inequality whenever v>1 and V≠1/N, so CF should compound DOWNWARD —
    the CR-055 prediction and the same direction as the A1-ρ result (CR-052) and
    Prop-2 attention-coupled noise. DECISION RULE: if the single-global-criterion
    CF stays materially above 0.5 across the grid (the paper's "criterion
    dominates" survives the DOF restriction) → A6 → CONFIRMED-CONDITIONAL
    (decomposition robust within scope, conditional on per-location criteria +
    σ=1 machinery); if a material fraction of cells fall below / CF deflates into
    the already-contested C1 corner → A6 → CONTESTED (the §5.1 "criterion can
    independently encode value at each location" claim is the load-bearing DOF).
    Reuse Critique/replications/C1--criterion-fraction-floor/run.py with a
    one-line constraint (optimise over the diagonal c_c=c_u of C_GRID²). Watch
    the criterion-grid range (the A6 run-018 clipping trap): use [-8,8] if any
    cell has inflated effective criteria.
  status: queued
  priority: high
  prereqs: []
  notes: |
    Spawned by CR-011 (run-018), the A6 v0.1 decisive loose end. Promoted to
    HIGH: it is the only path to settle A6 (CONFIRMED-CONDITIONAL vs CONTESTED),
    it tests §5.1's stated mechanism directly, and it is the second vector
    required by §6 for any elevation. Cheap (one constrained optimisation per
    cell, reuses the C1 grid). The honest decomposition (mirroring CR-008): the
    single-global-criterion CF will fall everywhere; the question is whether the
    NEW constraint-attributable sub-0.5 cells overlap the C1/A3 already-contested
    benefit-dominant corner (deepening, not relocating) or open a new failure
    region. Note the A6-(ii)∩A1 coupling: a fuller pooled-statistic rule would
    ALSO relax the Eq.9 FA product (A1, CONTESTED) — CR-056 isolates the
    criterion-DOF half; a joint A1×A6 re-derivation is a later option.
  origin: spawned-by-CR-011
  touched: 2026-05-25T15:58:00Z

- id: CR-057
  claim_id: A6
  attack_vector: literature
  task: |
    A6 completeness follow-up (cousin of CR-053 for A1): is the decision-noise /
    criterion lever VALUE-directed (reward-magnitude-modulated), or only
    attention/validity-modulated? The A6 Prop-2 result (run-018) showed an
    attention-coupled s(α) deflates the criterion fraction by ~0.10 — a third
    lever the two-tool decomposition mis-books. That only adds a VALUE channel
    outside the model if the noise/criterion modulation tracks reward MAGNITUDE.
    luo_maunsell2018 localises the criterion component to LPFC and the
    sensitivity component to visual cortex; survey for studies that vary reward
    value (not just validity/cue) and measure decision-noise / criterion / Fano
    / interneuronal-correlation structure. If the noise-criterion lever scales
    with value → the model omits a genuine value-directed lever, bearing on
    C1/C3 completeness the same way the A1 decorrelation channel does. Append to
    a new Critique/evidence/A6--decision-rule.md.
  status: queued
  priority: low
  prereqs: [CR-056]
  notes: |
    Spawned by CR-011 (run-018). Overlaps CR-053 (A1 value×correlation) — the
    decorrelation channel (A1) and the decision-noise channel (A6) are the same
    population-level phenomenon seen from two sides, so CR-053 and CR-057 may
    share a web fetch (Mitchell-Sundberg-Reynolds 2009 / a value×correlation
    primate study). Low + prereq CR-056: run after the A6 label is settled, and
    likely batched with CR-053. Genuine wiki gap (no entry addresses
    reward-modulation of decision noise / criterion-substrate gain).
  origin: spawned-by-CR-011
  touched: 2026-05-25T15:58:00Z
```

---

## Re-prioritisation note (CR-048 / run-015 → next run)

CR-048 is **done**: A2 elevated to **CONFIRMED-CONDITIONAL** (second vector,
re-derivation). This **settles the A2/A3/A8 heterogeneity arc** — A3 CONTESTED,
A8 CONFIRMED-CONDITIONAL, A2 CONFIRMED-CONDITIONAL — and closes the run-013/014
"connective frontier." Verdict ledger after run-015: C1 CONTESTED, C2 CUA,
C3 CONTESTED, C4 CONFIRMED-CONDITIONAL, C5 CUA; A2 CONFIRMED-CONDITIONAL,
A3 CONTESTED, A8 CONFIRMED-CONDITIONAL; **A1/A4/A5/A6/A7 OPEN**.

Per mission §3.3 (highest-priority OPEN/WEAKLY-SUPPORTED verdict, prereqs
settled), there are now **no WEAKLY-SUPPORTED verdicts left** — the queue is the
five OPEN assumptions. Recommended ordering for the next runs:

1. **CR-006 (A1, independence, literature)** — the paper's FIRST-named §5.5
   limitation, the richest wiki coverage (`cohen_maunsell2009_correlations`,
   `mcadams_maunsell1999_reliability`), and the assumption the CR-048 per-slot
   gradient explicitly presumes (A1+A6 surfaced as the next link). HIGH-value
   next pick: opens a fresh assumption with strong literature substrate.
2. **CR-011 (A6, heterogeneous decision rule, re-derivation)** — the cousin of
   A1; does the P1–P4 decomposition survive heterogeneous decision noise? The
   CR-048 cross-terms point here too.
3. **CR-009 (A4, no learning dynamics, literature)** / **CR-010 (A5, transfer
   forms, replication)** / **CR-012 (A7, reward structures, replication)** — the
   remaining untouched assumptions; A5/A7 reuse the CR-005/CR-036 substrate.
4. **CR-049** (full-resolution C2 reframing) and **CR-051** (extreme-spread A2
   stress test) are now OPTIONAL polish on the settled A2 — neither moves a
   verdict; defer behind the OPEN-assumption coverage.

Recommend **CR-006** next: it advances assumption-layer coverage (A1 is
untouched, paper-named-first) and is the connective prerequisite the A2×A8
cross-terms exposed.

## Re-prioritisation note (CR-052 / run-017 → next run)

CR-052 is **done**: A1 **WEAKLY-SUPPORTED → CONTESTED** (second vector,
re-derivation succeeded). The §5.5 "upper bound on VDA benefit" claim fails as a
uniform statement — correlation amplifies VDA ~20% in the benefit-dominant
regime (r≳0.5) while suppressing it in the cost-dominant regime; independence
instead upper-bounds the *criterion fraction*. Headline C2 magnitude robust.
**This makes A1 the THIRD CONTESTED claim/assumption joining C1, C3, A3 — and
the failure is the same shape every time: a true central/peak result over-stated
as a uniform/categorical directional claim.** Verdict ledger after run-017:
C1 CONTESTED, C2 CUA, C3 CONTESTED, C4 CONFIRMED-CONDITIONAL, C5 CUA;
**A1 CONTESTED**, A2 CONFIRMED-CONDITIONAL, A3 CONTESTED, A8 CONFIRMED-CONDITIONAL;
A4/A5/A6/A7 OPEN.

Per mission §3.3, there are again **no WEAKLY-SUPPORTED verdicts left** — the
queue is the four OPEN assumptions (A4/A5/A6/A7) plus the A1 follow-ups.
Recommended ordering:

1. **CR-053 (A1, value×correlation, literature)** — the standing A1 completeness
   follow-up, now SHARPER: CR-052's benefit-dominant amplification means the
   omitted decorrelation channel *adds* to VDA, so whether it is value-directed
   (reward-magnitude-modulated) directly bears on C1/C3 completeness. Confirmed a
   genuine wiki gap this run → likely needs one web fetch (Mitchell-Sundberg-
   Reynolds 2009 V4 noise-correlation, or a Cohen/Kohn-lab value×correlation
   study). Best A1-closing move.
2. **CR-011 (A6, global/heterogeneous decision rule, re-derivation)** — CR-052
   showed §5.5 conflates A1 with A6 (the "single global response" clause = A6,
   Booking 2). CR-011 should reuse the A1--correlated-fa P_no-fa(ρ) machinery and
   the booking split (see CR-055 pointer), and test whether a single global
   criterion compounds the CF-downward shift.
3. **CR-009 (A4, learning dynamics, literature)** / **CR-010 (A5, transfer forms,
   replication)** / **CR-012 (A7, reward structures, replication)** — the
   remaining untouched assumptions; A5/A7 reuse the CR-005/CR-036 substrate.
4. **CR-054** (structured-Σ magnitude), **CR-049/CR-051** (settled-A2 polish) —
   optional; do not move a verdict.

Recommend **CR-053** next: it closes the A1 thread (the only assumption now with
two vectors but an open completeness question) and is the only queued task whose
result feeds back into the already-CONTESTED C1/C3.

## Re-prioritisation note (CR-001 → next run)

CR-001 (C2 re-derivation) is done. The agent's recommended next
task is **CR-013** (high-res Figure 4 replication) — this is the
second attack vector for C2 that, if successful, elevates C2 to
CONFIRMED-UNDER-ATTACK. CR-014 (sensitivity probe) is a cheaper
alternative that produces a similar elevation. If neither is
selected, the next-highest seed task by mission §3.3 default
ordering is **CR-002** (C1 sensitivity attack on criterion-
fraction floor) — high-priority and unblocked.

## Re-prioritisation note (CR-014 → next run)

CR-014 (C2 sensitivity probe) is done. C2 has elevated to
CONFIRMED-UNDER-ATTACK; further work on C2 is no longer the
critical path. The agent's recommended next task by §3.3 default
ordering is **CR-002** (C1 sensitivity attack on criterion-
fraction floor) — high-priority, unblocked, and the natural
follow-up because C1 is the paper's *other* most-distinctive
empirical claim (criterion fraction always 60–96%) and a
sensitivity attack on the lower edge is the cheap-and-informative
move.

CR-013 (high-resolution Figure 4 replication) drops in priority:
its purpose was elevation of C2, which has happened via CR-014.
CR-013 remains queued but at lower urgency; it would still resolve
the "peak at r=0.398 (agent's grid) vs r ≈ 0.3 (paper's grid)"
specificity, which is now a minor expository note rather than a
verdict-shaping question.

CR-017 (clamping derivation extension) is medium-priority: it would
unify the analytic prediction across clamping and non-clamping
regimes, which is a substantive strengthening of the C2 analytic
substrate. CR-018 (f_0-VDA literature attack) is medium-priority
and informs §5.2's experimental-design recommendation. CR-019 is
gated on CR-004 (C4 re-derivation) and remains at low priority
until CR-004 happens.

The agent's recommended ordering for the next 3–5 runs:
1. **CR-002** — high-priority seed task on C1, unblocked.
2. **CR-003** — high-priority seed task on C3 (narrow-regime
   literature attack). Bears directly on §5.2.
3. **CR-004** — medium-priority seed task on C4 (no-inversion
   re-derivation); CR-019 piggybacks.
4. **CR-017** — clamping derivation extension; cheap, refines C2.
5. **CR-005** — C5 replication; builds the substrate for later
   A3/A5/A7 replications.

## Re-prioritisation note (CR-002 → next run)

CR-002 (C1 sensitivity probe) is done. C1 has moved from OPEN to
**CONTESTED**: the categorical "CF ∈ [0.60, 0.96] across all 4,410
combinations" is falsified by the replication (variant B argmin
CF=0.30 at r=10, V=0.25, v=4). The *substantive spirit*
("criterion typically dominates") survives — median CF ≈ 0.76 —
and a weaker reformulation that preserves §5.1's theoretical
argument has been drafted in the verdict file.

Three follow-ups spawned: CR-020 (C3 literature attack on narrow
regime — *strongly overlaps* with seed task CR-003, consider
merging), CR-021 (V=1/N degeneracy unified derivation, ties
CR-002/CR-014/CR-019 together), CR-022 (low-priority owner-
clarification note about the r=0.3 reference-point discrepancy).

The agent's recommended next task is **CR-020 (or equivalently
CR-003)** — high-priority, unblocked, and now even more load-
bearing because §5.2 inherits from both C1 (now contested) and
C3 (not yet attacked). The literature attack is wiki-anchored and
cheap. Specifically: survey research_db/ for high-V (V ≥ 0.75)
cueing experiments and check whether they report VDA-like value-
driven attention effects — if yes, C3's "narrow regime" claim is
also in tension with the literature.

Updated 3–5 run recommendation:
1. **CR-020 (or merged CR-003)** — high-priority C3 literature
   attack. Wiki-anchored, cheap, completes the §5.2 critique.
2. **CR-004** — medium-priority seed task on C4 (no-inversion
   re-derivation); CR-019 piggybacks.
3. **CR-021** — V=1/N degeneracy derivation; unifies three
   previously separate findings (C1/C2/C4) under one analytic
   treatment. Cheap but valuable.
4. **CR-017** — clamping derivation extension; cheap, refines
   C2.
5. **CR-005** — C5 replication; builds substrate for A3/A5/A7
   replications.

CR-022 (r=0.3 clarification note) is low-priority and can be
batched when the owner next reviews the verdict ledger.

## Re-prioritisation note (CR-020 → next run)

CR-020 (C3 literature attack, merged with seed CR-003) is done. C3
moved from OPEN to **WEAKLY-SUPPORTED** (mission §3.1) — first
verdict file written, one attack vector (literature) executed.
Headline: the §5.2 categorical "negligible VDA regardless of other
parameters at V ≥ 0.75" survives the wiki sweep but is *constrained*
by Stănișor et al. 2013 PNAS (new wiki stub added this run), which
finds high-V V1 single-unit reward modulation with attention-like
latency. The tension is prima facie but not a refutation — the V1
effect could be a criterion-side correlate. The §5.2 wording is the
strongest version of C3 and the version most at risk; the §4.4
qualitative wording is unaffected.

Spawned: CR-023 (Stănișor full-depth read, low-priority), CR-024
(Peck 2009 + Serences 2008 stubs, medium-priority), CR-025
(replication-attack adding sensitivity-side reward channel,
low-priority, depends on CR-005), CR-026 (re-derivation: compute
sup_{r,v} [R(P1)-R(P2)] at V=0.75 analytically — the recommended
next attack on C3).

The agent's recommended next-run task is **CR-026**, not CR-023 or
CR-004. The rationale: CR-026 is a re-derivation attack on C3 —
giving C3 its second distinct attack vector — and it adjudicates a
prior question (is §5.2 a theorem of the model or a numerical
observation?) that determines what any subsequent empirical attack
can conclude. CR-023 (empirical) only becomes diagnostic once
CR-026 (theoretical) has settled. CR-026 is also cheap (uses the
already-built CR-001 closed-form machinery; no new replication code
beyond evaluation at one V-value across the (r, v) grid).

Updated 3–5 run recommendation:
1. **CR-026** — C3 re-derivation attack at V=0.75 (second attack
   vector for C3; elevates to CONFIRMED-CONDITIONAL or moves to
   CONTESTED).
2. **CR-004** — C4 no-inversion re-derivation (medium-priority
   seed; CR-019 piggybacks).
3. **CR-021** — V=1/N degeneracy unified derivation (unifies
   C1/C2/C4 boundary findings).
4. **CR-017** — clamping derivation extension (refines C2).
5. **CR-024** — Peck 2009 + Serences 2008 stub additions
   (convergent neural evidence for high-V × value substrate).
6. **CR-005** — C5 replication (substrate for A3/A5/A7/CR-025).

Lower-priority deferred: CR-013 (high-res Figure 4 replication;
expository), CR-022 (r=0.3 reference-point clarification;
expository), CR-023 (Stănișor full-depth; depends on CR-026
adjudication), CR-025 (sensitivity-side reward replication;
depends on CR-005), CR-007/CR-015 (A2 literature; partially
subsumed by C3 evidence dossier), CR-006/CR-008/CR-009/CR-010/
CR-011/CR-012/CR-016/CR-018 (assumption literature/replication
seed tasks).

---

## Re-prioritisation note (CR-026 → next run)

CR-026 (C3 re-derivation at V=0.75) is done. **C3 moved from
WEAKLY-SUPPORTED to CONTESTED** with the strongest possible
adversarial outcome: a refutation of §4.4 / §5.2's categorical
wording *internal to the model* under its own assumptions. Sup VDA
at V=0.75 across the paper's primary (r,v) grid is 0.040 — eight
times the paper's "negligible" threshold and twice §4.4's own
"hot zone" boundary. The mechanism is named in closed form (the
$V_{\text{critical}}(r,N) \approx 1/(1 + r(N-1)/\kappa)$ boundary
above which P_2 also escapes uniform, leaving the high-V VDA window
empty). A proposed reformulation that preserves the paper's
scientific point with an explicitly r-dependent V-threshold is
drafted in `Critique/derivations/C3--high-V-supremum.md` §7.

Verdict ledger after run-005:
- **C1** (criterion fraction range): CONTESTED (run-003).
- **C2** (non-monotonic VDA in r): CONFIRMED-UNDER-ATTACK (run-002).
- **C3** (narrow regime, §5.2 advice): **CONTESTED** (run-005, this run).
- **C4** (no inverted attention): OPEN (no attack vector yet).
- **C5** (r=1 symmetric recovery): OPEN (no attack vector yet).
- A1-A7: all OPEN (no attack vectors yet).

Three of five headline claims are now attacked. C4 and C5 are
unattacked, and (per the mission §3.5 connection to PRISM) C4 is
the more interesting because the no-inversion claim has direct
implications for whether PRISM agents can be expected to discover
inverted-attention strategies under any training regime. C5 is a
self-consistency check the paper already ran; CR-005 is a
confirming-attack rather than a falsifying-attack and should be
ordered after at least one C4 attack.

Spawned this run: CR-027 (FAR-corrected V_critical closed form,
medium), CR-028 (Variant B sup at V=0.75, medium), CR-029
(V_critical map across secondary sweep, low; depends on CR-027),
CR-030 (literature search in residual high-V VDA window, low;
depends on CR-023 and CR-024).

The agent's recommended next task is **CR-004** — the C4
no-inversion re-derivation. The rationale: (i) C4 is the only
headline claim with no attack-vector executed; the critique's
audit trail needs at least one verdict file per headline claim.
(ii) C4 is categorical ("never optimal") — categorical claims
are usually easier to refute than confirm; a single counterexample
in the swept space would refute, and the agent's CR-014 sensitivity
probe already noted a possible V=1/N boundary counterexample
(documented in CR-019). (iii) CR-019 piggybacks on CR-004 by
design, so CR-004 produces *two* verdict updates for the cost of
one. (iv) The C4 re-derivation needs no new infrastructure (the
CR-001 replication substrate already exists).

CR-027 is cheaper and would refine the C3 reformulation, but C3 is
already CONTESTED and further C3 work is no longer critical-path.

Updated 3–5 run recommendation:
1. **CR-004** (+ CR-019 piggyback) — C4 no-inversion re-derivation.
   Medium-priority seed; first attack on the only unattacked
   headline claim. Two verdicts for the price of one.
2. **CR-027** — FAR-corrected V_critical closed form. Cheap;
   tightens C3 analytic substrate.
3. **CR-021** — V=1/N degeneracy unified derivation. Unifies
   C1/C2/C4 boundary findings; complements CR-019.
4. **CR-028** — Variant B sup at V=0.75. Closes the variant gap
   in the C3 attack.
5. **CR-005** — C5 replication. Builds the substrate for the A3/
   A5/A7 replication seeds.

---

### Run-006 update (2026-05-18)

CR-004 (+ CR-019 piggyback) completed. C4 verdict label set
OPEN → WEAKLY-SUPPORTED.

Headline finding: the *empirical* C4 (no inversion across 4,410
primary-sweep rows at N=4) survives independent corroboration
(direct query of CR-002 phase-A output: zero rows with α* < 1/N).
The paper's *theoretical justification* in §4.5 ("the weighted
reward loss exceeds the gain regardless of r") is INCOMPLETE:
the boundary one-sided derivative at α=1/N⁻ has closed form
∂E[R]/∂α|_{1/N⁻} = (2 d'_max f'(1/N) / (r+1)) · [A_0 − r·B_0/(N-1)]
with A_0, B_0 r-independent boundary partials. The sign flips at
r*_inv := (N-1)·A_0/B_0; ~49% of swept (V, v, variant) cells have
r*_inv inside the swept r-range, contradicting the "regardless of
r" wording read as a local statement. At the corner (V=1/N, v=1):
r*_inv = 1 exactly (proof: V·v = (1-V)/(N-1) = 1/N at this corner
forces A_0 = B_0/(N-1) at the symmetric criterion FOC). The
correct mechanism for global no-inversion is a *location-count
asymmetry* the paper does not name: at α→1, the single cued
location reaches d_max·f(1)=d_max; at α→0, the N-1 uncued locations
each reach only d_base + β[d_max f(1/(N-1)) − d_base] < d_max for
N≥3. Combined with the value-weight inequality V·v ≥ (1-V)/(N-1)
(equivalent to V ≥ 1/[(N-1)v+1], simplifying to V ≥ 1/N for v ≥ 1),
this produces strict right-branch dominance globally. CR-019
resolved IN THE NEGATIVE: C4's V ≥ 1/N (weak) is correct; the CR-014
α=0.02 finding was the left-branch local maximum, dominated by
the right branch via location-count asymmetry. Anti-cue regime
(V<1/N, v=1, N=2): inversion IS globally optimal (α*=0.180 at r=1,
α*=0.020 at r=10) — C4 fails outside the conditional but inside
the paper's stated V-range [0.25, 1.0] at N=2.

Spawned this run: CR-031 (literature attack on C4 conditional via
distractor-suppression learning, medium), CR-032 (Anderson 2011 +
Wang & Theeuwes 2018 + Geng 2014 wiki stubs, low), CR-033 (β/γ
kink sensitivity, low), CR-034 (anti-cue at N=4 derivation
extension, low).

Verdict ledger after run-006:
- **C1** (criterion fraction range): CONTESTED (run-003).
- **C2** (non-monotonic VDA in r): CONFIRMED-UNDER-ATTACK (run-002).
- **C3** (narrow regime, §5.2 advice): CONTESTED (run-005).
- **C4** (no inverted attention): **WEAKLY-SUPPORTED** (run-006, this run).
- **C5** (r=1 symmetric recovery): OPEN (no attack vector yet).
- A1-A7: all OPEN (no attack vectors yet).

Four of five headline claims are now attacked. Only **C5** remains
OPEN. With C4 at WEAKLY-SUPPORTED, the natural next pick is one of:
  - **CR-031** (literature attack on C4) — the second attack vector
    on C4, the cheapest path to a CONFIRMED-UNDER-ATTACK or
    CONTESTED elevation.
  - **CR-005** (C5 replication) — the only attack on the only
    untouched headline claim; builds the substrate for A3/A5/A7
    replication seeds, and is a confirming-attack rather than
    falsifying (likely WEAKLY-SUPPORTED or CONFIRMED-CONDITIONAL).

Either is justifiable. The recommendation: **CR-031** before CR-005,
because C4 has more analytic load-bearing on the paper's §5.1 / §5.2
narrative than C5 (which is a self-consistency check). The literature
attack on C4 also touches the suppression-history literature that has
broader implications for PRISM's experimental design.

Updated 3–5 run recommendation:
1. **CR-031** — C4 literature attack. The second attack vector on the
   newly-WEAKLY-SUPPORTED C4. Wang & Theeuwes 2018 / Geng 2014
   suppression-learning literature is the highest-leverage target.
2. **CR-005** — C5 replication. Touches the only headline claim with
   no attack vector executed. Self-consistency; expected
   WEAKLY-SUPPORTED.
3. **CR-027** — FAR-corrected V_critical closed form. Cheap; tightens
   C3 analytic substrate.
4. **CR-032** — Anderson 2011 + Wang & Theeuwes 2018 + Geng 2014
   stubs. Prerequisite-ish for CR-031.
5. **CR-021** — V=1/N degeneracy unified derivation. Substantively
   addressed by CR-004 (no new substantive content), but a unified
   derivation file would simplify the future referee report.

Lower-priority deferred (unchanged from run-004's
re-prioritisation): CR-013 (high-res Figure 4 replication), CR-022
(r=0.3 reference-point clarification), CR-023 (Stănișor full-depth;
now even less load-bearing because the reformulation reclassifies
Stănișor as predicted-observation rather than refutation
candidate), CR-024 (Peck 2009 + Serences 2008 stubs), CR-025
(sensitivity-side reward replication; depends on CR-005), CR-029
/ CR-030 (lower-priority C3 follow-ups), CR-006 / CR-007 / CR-008
/ CR-009 / CR-010 / CR-011 / CR-012 / CR-015 / CR-016 / CR-017 /
CR-018 (assumption literature / replication / derivation seeds).

## Re-prioritisation note (CR-031 → next run)

CR-031 (C4 literature attack) is done. C4 moved
**WEAKLY-SUPPORTED → CONFIRMED-CONDITIONAL** (second attack vector,
literature, failed to falsify within the V ≥ 1/N scope; the
distractor-suppression literature maps to the anti-cued V<1/N regime
where the model itself predicts inversion — convergence, not
counterexample). Verdict ledger after run-007: **C1 CONTESTED,
C2 CONFIRMED-UNDER-ATTACK, C3 CONTESTED, C4 CONFIRMED-CONDITIONAL,
C5 OPEN; A1–A7 OPEN; A8 PROPOSED (homogeneous-uncued allocation).**
Four of five headline claims now carry a substantive verdict; **C5 is
the only untouched headline claim.**

Spawned: CR-035 (stub the 2019/2020 Wang-Theeuwes follow-ups, low),
CR-036 (replication of the proposed-A8 heterogeneous-uncued
assumption — the substantive descendant of this run, medium,
`proposed_mission_change: true`), CR-037 (Anderson 2011 + Geng 2014
stubs, low; supersedes the Anderson/Geng remainder of the now-abandoned
CR-032).

The agent's recommended ordering for the next 2–4 runs:
1. **CR-036** — proposed-A8 replication. Highest leverage: tests whether
   relaxing uncued homogeneity shifts any headline number, and connects
   the critique to the concrete Wang & Theeuwes suppression effect. Also
   feeds A2.
2. **CR-005** — C5 replication. Closes the "one verdict file per headline
   claim" goal (C5 is the last untouched headline claim) and builds the
   substrate for the A3/A5/A6 assumption sweeps.
3. **CR-027** — FAR-corrected V_critical closed form (cheap C3 sharpening).
4. **CR-006 / CR-007** — first attacks on the A1/A2 assumption seeds, now
   that four headline claims are covered and the assumption layer is the
   natural next frontier (A8 via CR-036 leads into it).

Lower-priority deferred (carried forward): CR-013, CR-021, CR-022,
CR-023, CR-024, CR-025, CR-028, CR-029, CR-030, CR-033, CR-034, CR-035,
CR-037, and the remaining assumption seeds CR-008/009/010/011/012/
015/016/017/018.

---

## Re-prioritisation note (CR-005 → CR-038 → next run)

(Run-008 closed CR-005 — C5 first attack, replication — and set C5
WEAKLY-SUPPORTED; that re-prioritisation was recorded in
`reviewer_state.json._run_008_summary` but not mirrored here. This note
brings the backlog file current as of run-009.)

CR-038 (C5 re-derivation) is done. **C5 moved WEAKLY-SUPPORTED →
CONFIRMED-UNDER-ATTACK** — the designated second vector (re-derivation,
after run-008's replication) failed to falsify and instead promoted the
recovery to a theorem (β(1)=γ(1)=1 real-number identity + Sterbenz
bit-exactness lemma, with the literal "0.0" shown config-specific:
exact iff f_0 ≥ h(1/N)/(1+h(1/N)) = 1/3 at N=4,√). CR-039 was addressed
inside this run (its owner-note content is in the C5 v0.2 verdict) and
re-homed as CR-041.

**Verdict ledger after run-009: C1 CONTESTED, C2 CONFIRMED-UNDER-ATTACK,
C3 CONTESTED, C4 CONFIRMED-CONDITIONAL, C5 CONFIRMED-UNDER-ATTACK; A1–A7
OPEN, A8 ratified/untouched.** All five headline claims now carry a
*settled-as-far-as-the-evidence-goes* verdict (two are CONFIRMED-UNDER-
ATTACK, one CONFIRMED-CONDITIONAL, two CONTESTED with drafted
reformulations). **The headline-claim phase is complete; the assumption
layer (A1–A8) is now the sole frontier.**

Spawned this run: CR-040 (A3 βγ=1 alternative-constraint re-derivation/
replication *off* r=1 — the bridge from C5 into the assumption layer,
medium), CR-041 (owner wording note absorbing CR-039, low).

The agent's recommended ordering for the next 3–5 runs (all now in the
assumption layer per mission §3.3, since no headline claim is OPEN or
WEAKLY-SUPPORTED any longer):
1. **CR-040** — A3 (βγ=1) re-derivation/replication off r=1. Highest
   leverage: the paper itself flags A3 in §5.5 as "could yield
   quantitatively different results," the run-008 optimiser substrate is
   built and validated, and β=√r / γ=1/√r is a clean closed form. Directly
   tests the paper's "qualitative findings should be robust" claim.
2. **CR-036** — A8 heterogeneous-uncued replication (run-007's standing
   pick; ratified assumption, de-risked by the run-008 substrate). Connects
   to the Wang & Theeuwes suppression gradient and feeds A2.
3. **CR-006 / CR-007** — first attacks on A1 (independence) / A2 (single
   global r) assumption seeds.
4. **CR-027** — FAR-corrected V_critical closed form (cheap C3 sharpening,
   if a CONTESTED-claim refinement is wanted).
5. **CR-041 / CR-039-content** — fold the C5 wording note into the eventual
   owner-facing referee summary (no compute).

Lower-priority deferred (carried forward): CR-013, CR-021, CR-022,
CR-023, CR-024, CR-025, CR-028, CR-029, CR-030, CR-033, CR-034, CR-035,
CR-037, and the assumption seeds CR-008/009/010/011/012/015/016/017/018.

---

## Re-prioritisation note (CR-040 → next run)

CR-040 (A3 βγ=1 re-derivation) is **done**; verdict A3 created at
**WEAKLY-SUPPORTED**. The §5.5 robustness claim survived its first
attack vector: on the V=0.5,v=5 reference slice the βγ=1 swap preserves
all three named findings (non-monotonic VDA — peak shifts 0.398→0.316,
+14%; no inversion within V≥1/N; criterion dominance — but eroded, CF
floor 0.601→0.507). The closed-form result is that the two families are
one rescaling apart, (β,γ)_mul = κ(r)·(β,γ)_add with
κ(r)=(r+1)/(2√r)=cosh(½ln r)≥1, so βγ=1 does **not** conserve total
magnitude (Σ=2κ≥2) — a citable correction to the paper's incidental
"β+γ=2 conserves total attention magnitude" phrasing.

The single decisive open question is whether **criterion dominance
(CF>0.5) breaks under βγ=1 in the low-V/high-v/variant-B cells where C1
is already CONTESTED** (run-003 found additive CF→0.304 there). That is
the only place A3 can move to CONTESTED. **CR-008 has been promoted
medium→high and re-scoped as the designated A3 second vector** to settle
it — it is the recommended next pick.

Recommended ordering for the next 3–5 runs:
1. **CR-008** — A3 second vector (high). Multiplicative sweep restricted
   to the additive-CF<0.60 cells; decides A3 → CONFIRMED-CONDITIONAL
   (if CF stays >0.5) vs CONTESTED (if any cell <0.5, which would also
   scope the §6 "criterion dominance" categorical). Reuses the run-010
   `beta_gamma_multiplicative` substrate.
2. **CR-036** — A8 heterogeneous-uncued replication (run-007/009 standing
   pick; ratified assumption, de-risked substrate).
3. **CR-006 / CR-007** — first attacks on A1 (independence) / A2 (single
   global r) assumption seeds.
4. **CR-042** — sensitivity: does the C2 βγ=1 peak-shift (left+up)
   persist across the f_0/h secondary sweep? (low, cheap, reuses run-010).
5. **CR-043** — literature: firsthand additive-vs-divisive-conservation
   primate citation to upgrade the reynolds_heeger2009 review-depth point
   in the A3 verdict (low, ≤1 fetch).

Spawned this run: CR-042 (sensitivity, low), CR-043 (literature, low).
Promoted: CR-008 (medium→high, re-scoped as A3 second vector).

Verdict ledger after run-010: C1 CONTESTED, C2 CONFIRMED-UNDER-ATTACK,
C3 CONTESTED, C4 CONFIRMED-CONDITIONAL, C5 CONFIRMED-UNDER-ATTACK; **A3
WEAKLY-SUPPORTED (first assumption-layer verdict)**; A1,A2,A4,A5,A6,A7
OPEN, A8 ratified/untouched. The assumption layer is now open for
business with A3 as its first attacked member.

Lower-priority deferred (carried forward): CR-013, CR-021, CR-022,
CR-023, CR-024, CR-025, CR-028, CR-029, CR-030, CR-033, CR-034, CR-035,
CR-037, CR-041, CR-042, CR-043, and the assumption seeds
CR-009/010/011/012/015/016/017/018 (CR-008 promoted out to high).

---

## Re-prioritisation note (CR-008 → next run)

CR-008 (A3 second vector, replication) is **done**; verdict **A3
WEAKLY-SUPPORTED → CONTESTED**. The §5.5 robustness claim's *criterion-
dominance* conjunct survived re-derivation (CR-040) but fails the replication as
a per-cell claim: on the paper's own 4,410-cell grid, swapping additive β+γ=2
for multiplicative βγ=1 **doubles** the criterion-subordinate fraction (4.01%→
8.34%; 191 cells flip CF≥0.5→CF<0.5, 0 recover), concentrated in the
benefit-dominant high-r corner C1 already contested. It survives only as a
central-tendency claim (median CF 0.7605→0.7578). A weaker §5.5/§6 reformulation
is drafted in the verdict ("criterion dominance is robust as a central-tendency
statement but boundary-sensitive to the conservation form"). Validation was
exact (recomputed additive CF ≡ run-003 stored, bit-for-bit). The result is
sharpened by the divisive-normalization point: βγ=1 is the more biologically apt
rule, so the eroded boundary is not a worst-case curiosity.

**Verdict ledger after run-011:** C1 CONTESTED, C2 CONFIRMED-UNDER-ATTACK,
C3 CONTESTED, C4 CONFIRMED-CONDITIONAL, C5 CONFIRMED-UNDER-ATTACK; **A3
CONTESTED** (two vectors: CR-040 re-derivation + CR-008 replication);
A1/A2/A4/A5/A6/A7 OPEN, A8 ratified/untouched.

Spawned: CR-044 (Δα=0.005 grid-robustness spot-check on the borderline flips,
low — does not move the verdict).

The agent's recommended ordering for the next 3–5 runs:
1. **CR-042** — A3 sensitivity (does the criterion-dominance doubling persist
   across the f₀/h secondary sweep, or is it specific to f₀=0.5,√? Lower f₀
   raises reallocation gain, so the erosion may be *worse* there). Highest-
   leverage A3 follow-up; reuses the run-010/011 substrate. With A3 now CONTESTED
   on two vectors, CR-042 is a refinement (it cannot un-contest A3) — so weigh it
   against opening a fresh assumption.
2. **CR-036** — A8 heterogeneous-uncued replication (ratified assumption,
   de-risked substrate; the standing run-007/008/009 pick). The natural
   *substantive* next frontier: A8 is untouched and connects to the Wang &
   Theeuwes suppression gradient and to A2.
3. **CR-006 / CR-007** — first attacks on A1 (independence) / A2 (single global
   r). A2 is a cousin of A3 (heterogeneous gain asymmetry vs heterogeneous
   allocation) and of A8.
4. **CR-044** — grid-robustness hygiene on the A3 flip count (low; cheap).
5. **CR-043** — firsthand additive-vs-divisive primate cite to upgrade the
   reynolds_heeger2009 review-depth point now load-bearing in the A3 CONTESTED.

Recommendation: **CR-036** (open the untouched A8) as the substantive pick, with
**CR-042** as the cheaper A3-sharpening alternative. Rationale for CR-036 over
CR-042: A3 is now settled-as-CONTESTED on two vectors; further A3 sensitivity
sharpens the quantitative story but cannot change the verdict, whereas A8 is a
ratified load-bearing assumption with no verdict file yet, so it advances the
critique's coverage more (mission §3.3 prefers OPEN/WEAKLY-SUPPORTED verdicts,
and every A1–A8 except A3 is now OPEN or untouched).

Lower-priority deferred (carried forward): CR-013, CR-021, CR-022, CR-023,
CR-024, CR-025, CR-028, CR-029, CR-030, CR-033, CR-034, CR-035, CR-037, CR-041,
CR-043, CR-044, and the assumption seeds CR-009/010/011/012/015/016/017/018.

---

## Re-prioritisation note (CR-036 → next run)

CR-036 (A8 heterogeneous-uncued replication) is **done**. **A8 moved from
(none) to WEAKLY-SUPPORTED** — the second assumption-layer verdict, and a
*confirming* one (contrast A3, CONTESTED). The replication showed A8 is
**innocuous for the headline claims C1–C5**: under the paper's equal-uncued-
validity structure, homogeneous allocation is the OPTIMUM (not merely an
assumption) at every swept cell, and the full unconstrained simplex optimum
coincides with the homogeneous-constrained one at every headline cell. The
nuance worth carrying: A8 is *not* trivially free — with a forced uncued budget
the benefit-dominant regime prefers winner-take-all concentration (Part 1b), so
the headline-claim safety is a structural coincidence (concentrate-favouring
r>1 also drives the cued allocation to absorb the whole budget). And relaxing
A8 *enriches* the model: one anti-cued slot ⇒ the optimum reproduces the
Wang & Theeuwes graded suppression gradient.

Verdict ledger after run-012:
- **C1** CONTESTED · **C2** CONFIRMED-UNDER-ATTACK · **C3** CONTESTED ·
  **C4** CONFIRMED-CONDITIONAL · **C5** CONFIRMED-UNDER-ATTACK.
- **A3** CONTESTED · **A8** WEAKLY-SUPPORTED · A1/A2/A4/A5/A6/A7 OPEN.

Two of eight assumptions now carry a verdict. The agent's recommended next-run
ordering:

1. **CR-045** — A8 re-derivation (the designated SECOND vector): prove
   Schur-concavity ⇒ equal-split optimal + the cued-absorption pre-emption
   lemma; elevates A8 → CONFIRMED-CONDITIONAL. Mirrors how CR-038 elevated C5.
   Cheap (reuses the C4 closed-form machinery); the natural completion of the
   A8 thread before opening a new assumption.
2. **CR-006 / CR-007** — first attacks on A1 (independence) / A2 (single
   global r) — the next untouched assumptions; A2 is the cousin of both A3
   (heterogeneous gain) and A8 (heterogeneous allocation), so a unified
   heterogeneity treatment is emerging.
3. **CR-011** — A6 (heterogeneous decision rule) re-derivation; another
   untouched assumption with a clean re-derivation entry point.
4. **CR-047** — A8 N>4 graded-suppression replication (positive-result
   enrichment; substrate built).
5. **CR-042 / CR-044** — A3 sharpening (cannot un-contest A3; low).

Rationale for CR-045 first: per mission §3.1/§6 the WEAKLY-SUPPORTED A8 is one
honest re-derivation away from a settled CONFIRMED-CONDITIONAL, and finishing a
thread before starting a new one keeps the verdict ledger legible; the
re-derivation also supplies the closed-form Schur-concavity statement a referee
report would want. CR-046 (finer-grid hygiene on the V=1/N +6.8e-4 corner) is
low and can be batched into the CR-045 run.

Lower-priority deferred (carried forward): CR-013, CR-021, CR-022, CR-023,
CR-024, CR-025, CR-028, CR-029, CR-030, CR-033, CR-034, CR-035, CR-037, CR-041,
CR-042, CR-043, CR-044, CR-046, CR-047, and the assumption seeds
CR-009/010/011/012/015/016/017/018.

---

## Re-prioritisation note (CR-045/run-013 + CR-007/run-014 → next run)

(Run-013 closed CR-045 — A8 second vector, re-derivation — elevating **A8 →
CONFIRMED-CONDITIONAL** and spawning CR-048; that re-prioritisation lives in
`reviewer_state.json._run_013_summary` and `RUN_LOG.md` and was not mirrored
here. This note brings the backlog current as of run-014.)

CR-007 (A2 single-global-$r$, literature) is **done**; **A2 created at
WEAKLY-SUPPORTED**. The literature attack established the decisive R1/R2 split:
the single-$r$ premise is empirically *false* under within-display
heterogeneity (R2 — location/feature/time, decisively documented and conceded
by the paper in §5.4/§5.5), but *benign and methodologically correct* under the
between-preparation reading (R1) the 100-fold $r$-sweep operationalises and §5.4
adopts. No attack shifted a headline claim this run, so the verdict is
WEAKLY-SUPPORTED, not CONTESTED; the open question — does R2 heterogeneity
materially move C1–C5? — is a re-derivation, routed to **CR-048**.

**Verdict ledger after run-014:** C1 CONTESTED, C2 CONFIRMED-UNDER-ATTACK,
C3 CONTESTED, C4 CONFIRMED-CONDITIONAL, C5 CONFIRMED-UNDER-ATTACK; **A3
CONTESTED, A8 CONFIRMED-CONDITIONAL, A2 WEAKLY-SUPPORTED**; A1/A4/A5/A6/A7 OPEN.
**Three of eight assumptions now carry a verdict; A1/A4/A5/A6/A7 remain the
untouched frontier.**

Spawned this run: CR-049 (A2 C2-reframing replication, medium, prereq CR-048),
CR-050 (A2 sign-reversal/§5.4 clarity note, low). Promoted: CR-048 (now the
designated A2 second vector and the recommended next pick).

Recommended ordering for the next 3–5 runs:
1. **CR-048** — A2 second vector (re-derivation, A2×A8 interaction). Settles
   A2 → CONFIRMED-CONDITIONAL or CONTESTED, and is the keystone of the unified
   A2/A3/A8 "heterogeneity" arc. Reuses the general-$N$ model already built.
2. **CR-006** — first attack on **A1** (independence), the assumption the paper
   names *first* in §5.5 and the one with the richest wiki coverage
   (`cohen_maunsell2009_correlations`, `ruff_cohen2016_cross_area_correlations`).
   Opens a fresh untouched assumption (mission §3.3 prefers OPEN verdicts).
3. **CR-011** — **A6** (heterogeneous decision rule) re-derivation; another
   untouched assumption with a clean entry point, and a cousin of A1/A2.
4. **CR-049** — A2 C2-reframing replication (after CR-048 bounds the regime).
5. **CR-009 / CR-010 / CR-012** — A4 (no-learning) / A5 (transfer-function
   family) / A7 (reward variants); the remaining untouched-assumption seeds.

Lower-priority deferred (carried forward): CR-013, CR-021, CR-022, CR-023,
CR-024, CR-025, CR-028, CR-029, CR-030, CR-033, CR-034, CR-035, CR-037, CR-041,
CR-042, CR-043, CR-044, CR-046, CR-047, CR-050, and the assumption seeds
CR-015/016/017/018.

---

## Notes for the agent

This is the bootstrap backlog. After CR-001 completes, the agent owns
this file. The agent's first run should:

1. Read this whole file plus the mission file plus the top of
   `RUN_LOG.md` (which will be empty on the first run).
2. Pick **CR-001** by default (mission §8.6).
3. Mark it `in_progress`, write the run-log header, then execute.
4. On completion: mark CR-001 `done`, append a notes summary,
   spawn at least one follow-up task (likely a replication-attack
   on C2 if the re-derivation surfaced a sensitivity), update
   the state JSON, append the run-log entry body, and write the
   conversation page.

The agent should *not* attempt to address every seed task in one
run. Mission §8.5: one claim, one attack vector, done well.
