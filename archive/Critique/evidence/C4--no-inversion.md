# Evidence dossier: C4 — Inverted attention is never optimal

Accumulating literature evidence for the C4 verdict
(`Critique/verdicts/C4--no-inversion.md`). Each run appends a dated
`## Version` section. Structure of each entry follows mission §5.5.

**Claim under attack (C4, paper §4.5):** across the 4,410-row primary
sweep ($N=4$, $V \in [1/N, 1]$, $v \in \{1,\dots,5\}$, both reward
variants), the optimal allocation $\alpha^\star$ to the cued location is
always $\geq 1/N$; "inverted attention" ($\alpha^\star < 1/N$) is never
optimal.

**The model fact this literature must be read against (from CR-004 /
run-006 re-derivation):** the model produces $\alpha^\star < 1/N$
*cleanly and optimally* when the value-weight inequality flips, i.e.
when $w_c = Vv < w_u = (1-V)/(N-1)$. For $v \geq 1$ this is exactly the
**anti-cued regime $V < 1/N$**. So the model's "no inversion" is not a
blanket structural prohibition — it is a *consequence of the conditional
$V \geq 1/N$*. Any behavioural phenomenon that looks like "attending
below uniform to a location" is only a counterexample to C4 if it occurs
at a location that is **high-value / high-target-probability**
($V \geq 1/N$). Down-weighting a **low-target-probability** location is
the model's own normative prediction, not a violation.

---

## Version 0.1 — 2026-05-19 (run-007, CR-031, literature attack)

Two sub-questions from the C4 verdict's next-attack recommendation:

- **(i)** Does anyone report behavioural $\alpha^\star < 1/N$ at a
  *validly cued / high-value* location ($V \geq 1/N$) — e.g. via
  eye-tracking, microsaccade, or fixation-eccentricity proxies?
- **(ii)** Is the distractor-suppression-learning literature a
  behavioural counterexample to C4 in the model's terms — i.e. does
  learned suppression of a location amount to $\alpha < 1/N$ at a
  location that the model would classify as $V \geq 1/N$?

### Source: [[wang_theeuwes2018_statistical_learning_distractor_suppression]] (depth: abstract — stub added this run)

- **Bears on the claim how:** Sub-question (ii), the central one. In the
  additional-singleton task, a colour distractor singleton appeared more
  often at one location; for that high-probability-**distractor**
  location, attentional capture was reduced and target selection was
  *less* efficient, with a spatial gradient of suppression scaling with
  distance. Awareness did not matter. Interpretation (the authors'):
  statistical learning induces plasticity in the spatial priority map
  such that high-distractor-probability locations are suppressed
  relative to all others.
- **Direction:** **constrains, then supports.** Prima facie this is the
  closest behavioural analogue of "attending below uniform to a
  location". But the suppressed location is the location *least* likely
  to contain the target (it is where the salient *distractor* lives). In
  the target paper's model that is a location with target-validity below
  $1/N$ — an **anti-cued** location. Per CR-004/run-006, the model's
  normative optimum at $V < 1/N$ *is* $\alpha^\star < 1/N$. So learned
  distractor suppression is the model's own prediction in the anti-cued
  regime, **not** a counterexample to C4's $V \geq 1/N$ claim. After this
  reading the evidence flips from "candidate counterexample" to
  "convergent support for the conditional reformulation".
- **Quantitative weight:** medium-to-strong. A robust, multiply-replicated
  primary paradigm (this 2018a paper plus the 2018b cueing-control study,
  the 2019 eye-tracking study, and the 2020 biased-competition study
  below), not a single experiment. But it is *indirect* for C4 because
  the mapping onto the model's single-cued / homogeneous-uncued
  geometry requires interpretation (see "scope note" below).
- **What the verdict did with this:** cited as the primary evidence in
  C4 Version 0.2 for the finding that the suppression literature is
  consistent with the model (lands in the $V<1/N$ regime), driving the
  WEAKLY-SUPPORTED → CONFIRMED-CONDITIONAL movement.

### Source: Wang, Samara & Theeuwes (2019), *Statistical regularities bias overt attention*, Atten Percept Psychophys 81(6):1813–1821 (PMID 30919311, DOI 10.3758/s13414-019-01708-5) — abstract depth, read from PubMed, NOT yet stubbed (queued CR-035)

- **Bears on the claim how:** Sub-question (i). Eye-tracking variant of
  the above. **Fewer saccades landed at the high-probability distractor
  location** than at any other location, and when a target appeared
  there, saccade latencies were *higher*. A small additional
  faster-disengagement effect was also found.
- **Direction:** **constrains, then supports** (same logic as the 2018a
  entry). This is the most direct *oculomotor* signature of below-uniform
  allocation to a location — exactly the kind of proxy sub-question (i)
  asked for. But again the location is the low-target-probability one
  (anti-cued, $V<1/N$), so it is the model's own prediction, not a
  violation of C4 at $V \geq 1/N$. Importantly, **no study reports the
  mirror effect** — observers actively saccading *away from* a
  high-target-probability / high-value cued location below the uniform
  rate. That asymmetry is the positive content of sub-question (i): the
  behavioural literature has below-uniform allocation only for anti-cued
  locations.
- **Quantitative weight:** medium. Single eye-tracking study, but
  converges with the manual-RT 2018a result and the 2020 probe result.
- **What the verdict did with this:** cited as the oculomotor evidence
  that the only observed below-uniform allocation is at anti-cued
  locations; answers sub-question (i) in the negative (no $\alpha<1/N$ at
  $V\geq 1/N$).

### Source: Kong, Li, Wang & Theeuwes (2020), *Proactively location-based suppression elicited by statistical learning*, PLoS ONE 15(6):e0233544 (PMID 32479531, DOI 10.1371/journal.pone.0233544) — abstract depth, read from PubMed, NOT yet stubbed (queued CR-035)

- **Bears on the claim how:** Adds a search-probe condition to measure the
  *initial* distribution of attentional resources. Result: the probe at
  the high-probability-distractor location was suppressed relative to
  other locations, AND **suppression of that location resulted in MORE
  attention allocated to the target location**. The authors frame this
  explicitly as a space-based resource-allocation ("biased competition")
  model.
- **Direction:** **supports** — on two counts. (1) Same anti-cued reading
  as above. (2) The "suppress here ⇒ more there" reciprocity is precisely
  the **zero-sum reallocation** logic the target paper asserts in §5.1.
  So the suppression literature corroborates the paper's *mechanistic
  framing*, not just its no-inversion conclusion.
- **Quantitative weight:** medium. Single study; but the biased-competition
  reallocation it documents is the behavioural instantiation of the
  paper's core allocation accounting.
- **What the verdict did with this:** cited in C4 Version 0.2 as
  independent behavioural support for the §5.1 zero-sum framing that C4
  underwrites.

### Source: [[failing_theeuwes2018_selection_history]] (depth: full)

- **Bears on the claim how:** Review covering both halves of selection
  history. The *facilitatory* half (value-driven capture: reward-paired
  features capture attention even when task-irrelevant, non-salient, and
  known-unhelpful; RT cost ~20–60 ms; persists ≥6 months) and the
  *inhibitory* half (statistical learning of distractor locations; §6
  explicitly flags that the inhibitory side "may be a distinct learning
  system", citing Wang & Theeuwes 2018 and Geng 2014).
- **Direction:** **supports** (mixed but net-supporting). The
  value-driven-capture half is direct support for no-inversion at the
  cued/high-value location: observers are pulled *toward* value and
  cannot easily suppress reward-associated stimuli — the opposite of
  inverting away from value. The suppression half is the anti-cued
  phenomenon adjudicated above.
- **Quantitative weight:** strong (decade-spanning review synthesizing
  behavioural, ERP/N2pc, fMRI, and LIP single-unit results).
- **What the verdict did with this:** cited as the framing source that
  separates the facilitatory (supports C4 at $V\geq 1/N$) from the
  inhibitory (anti-cued, $V<1/N$) phenomena.

### Source: [[hickey2010_reward_salience_acc]] (depth: full)

- **Bears on the claim how:** Single-trial reward at chance validity
  ($V = 1/N$) shifts next-trial attention *toward* the high-reward
  location/feature, with an ACC reward signal.
- **Direction:** **supports.** Reward pulls allocation toward value, never
  below uniform at the value location — consistent with C4 and with the
  model's location-count + value-weight argument.
- **Quantitative weight:** light-to-medium (single primary study, widely
  cited).
- **What the verdict did with this:** cited as the single-trial primary
  anchor for "value pulls toward, not away".

### Source: [[posner1980_orienting]] (depth: full)

- **Bears on the claim how:** Classic chance-validity ($V = 1/N$)
  condition shows no validity effect — observers do not reallocate when
  the cue is uninformative.
- **Direction:** **supports** at the $V = 1/N$ boundary (the model's
  degeneracy point): no reallocation, certainly no inversion, when the
  cue carries no spatial information.
- **Quantitative weight:** light for inversion specifically (the paradigm
  was not designed to elicit inversion), foundational for the boundary.
- **What the verdict did with this:** cited as the empirical analogue of
  the $V=1/N$ degeneracy.

### Source: [[gupta_sridharan2024_presaccadic_change]] (depth: full)

- **Bears on the claim how:** Sub-question (i) candidate flagged by the
  C4 verdict (run-006): presaccadic attention does *not* facilitate
  change detection. If observers were *actively avoiding* a normatively
  favoured location, that would be a behavioural inversion.
- **Direction:** **unrelated-to-constrains on inspection.** This is a
  *failure of facilitation*, not active below-uniform allocation away
  from a cued/high-value location. It does not provide an $\alpha<1/N$ at
  $V\geq 1/N$ counterexample. It does mildly caution that the
  normative-to-behaviour mapping is imperfect (presaccadic benefits the
  normative model would predict are not always realised).
- **Quantitative weight:** light for the inversion question specifically.
- **What the verdict did with this:** cited as resolving sub-question (i)
  in the negative — the candidate counterexample is not one.

### Source: [[bisley_mirpour2019_priority_map]] / [[desimone_duncan1995_biased_competition]] (depth: full, both)

- **Bears on the claim how:** Substrate. Standard priority-map and
  biased-competition formulations implement *non-negative* priority
  weighting; suppression is competitive down-weighting *relative to other
  locations*, not a negative absolute weight on the cued location.
- **Direction:** **supports / constrains.** The neural substrate that
  would implement the model has no native "attend-away-from-cue" channel;
  what it has is competitive reallocation, which is exactly the
  zero-sum picture. But it also means the homogeneous-uncued assumption
  of the model (uniform $(1-\alpha)/(N-1)$ to every uncued location) is a
  simplification: real priority maps support *heterogeneous* uncued
  weighting (one suppressed location, others not). See scope note.
- **Quantitative weight:** medium (substrate-level, not a direct test).
- **What the verdict did with this:** cited for the substrate argument and
  for surfacing the homogeneous-uncued scope limitation (spawned CR-036).

### Scope note (the load-bearing interpretive step)

There are exactly two ways to map "distractor-location suppression" onto
the target paper's geometry, and **both leave C4 intact**:

1. **Identify the suppressed location with the model's *cued* slot.** Then
   it is a low-target-probability ($V<1/N$) cued location, and the model
   *predicts* $\alpha^\star<1/N$ there (CR-004 anti-cue result). The
   behaviour matches the model; C4 (scoped to $V\geq 1/N$) is untouched.

2. **Identify the suppressed location with one of the $N-1$ *uncued*
   slots.** Then the observer is allocating *heterogeneously* among uncued
   locations (less to the high-distractor one, more to the rest). The
   model assumes **homogeneous** uncued allocation, so it cannot represent
   this at all — it is outside the model's scope and is governed by a
   *different* assumption (related to A2 "single global $r$" / a
   homogeneity-of-uncued-allocation assumption), not by C4.

Either way the distractor-suppression literature is **not** a
counterexample to C4. Under mapping (1) it is convergent support for the
conditional reformulation; under mapping (2) it is out of scope and
indicates a separate assumption worth its own verdict (spawned CR-036).

### Net assessment for the verdict

The literature attack **fails to falsify C4 within its $V \geq 1/N$
scope**, and is the second distinct attack vector after the run-006
re-derivation. No study reports below-uniform allocation to a
high-value / high-target-probability cued location; the only observed
below-uniform allocation (distractor suppression, manual + oculomotor +
probe) is at anti-cued locations, where the model itself predicts it.
Value-driven capture positively supports no-inversion at the cued
location. Net verdict movement: **WEAKLY-SUPPORTED → CONFIRMED-CONDITIONAL**
(confirmed within the paper's stated scope; the conditional $V\geq 1/N$
is necessary and is now corroborated from two independent directions —
the model's own anti-cue derivation and the suppression literature's
anti-cued geometry).
