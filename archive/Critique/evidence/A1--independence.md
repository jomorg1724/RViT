---
type: evidence-dossier
claim_id: A1
claim_statement: "Per-location SDT decisions are independent (paper §2.1, Eqs. 1–2, 9); the paper self-characterises the resulting numbers as an upper bound on VDA benefit (§5.5)."
paper_section: "§2.1 (Eqs. 1–2), §2.5 (Eq. 9 P_no-fa product), §5.5 (limitation)"
attack_vector: literature
created: 2026-05-24
last_updated: 2026-05-24
---

# Evidence dossier — A1: per-location SDT independence

This dossier accumulates literature bearing on assumption **A1** (mission
§2.7): *"Per-location SDT decisions are independent. Real observers emit a
single global response; correlations across locations could alter the
optimal policy."* The paper states the assumption verbatim in §2.1 — *"The
observer makes independent detection decisions at each location using signal
detection theory (SDT)"* — and operationalises it in **Eq. (9)**:

$$
P_{\text{no-fa}} = (1-\mathrm{FAR}_c)\,(1-\mathrm{FAR}_u)^{N-1},
$$

i.e. the joint probability of *no false alarm anywhere* on a no-change trial
is computed as the **product** of the per-location marginal no-FA
probabilities. The paper names the assumption in §5.5 and pre-empts it:
*"the model assumes independent per-location SDT decisions; real observers
emit a single global response, introducing dependencies that could alter the
optimal policy. Our results therefore represent an upper bound on VDA
benefit."*

The dossier's job (mission CR-006) is to **quantify how consequential** the
limitation is — not to repeat that it exists — and to test the *direction*
of the self-characterised "upper bound."

---

## Version 0.1 — 2026-05-24 (run-016, literature attack)

### Where independence is mathematically load-bearing

Two distinct readings of "independence," which the literature forces apart
(cf. the R1/R2 split the agent used for A2 in run-014):

- **(I-dec) Decision-level independence.** The product factorisation in
  Eq. (9), $P(\bigcap_i\{\text{no FA}_i\}) = \prod_i P(\text{no FA}_i)$,
  holds **iff** the per-location false-alarm events are mutually
  independent. This is the binding locus for the correct-rejection reward
  term $0.5\,P_{\text{no-fa}}\,\mathrm{CR}$ in Eq. (9), and hence for the
  criterion-gain $R(\mathrm{P3})-R(\mathrm{P4})$ and the **criterion
  fraction (C1)**.
- **(I-neur) Neural-level independence.** The per-location sensitivities
  $d'_{\text{cued}}, d'_{\text{uncued}}$ are treated as marginal
  single-channel quantities. Population sensitivity in cortex is a function
  of the *full covariance* $\Sigma$, not the marginals
  ($d'^2 \propto (\Delta\mu)^\top \Sigma^{-1}(\Delta\mu)$), so I-neur is the
  reading the correlation-structure literature contradicts directly.

A clean formalisation of the I-dec consequence: model the no-change-trial
decision variables $\{X_i\}_{i=1}^N$ as jointly Gaussian with unit variance
and equicorrelation $\rho$ (location $i$ false-alarms iff $X_i>c_i$). Then
$P_{\text{no-fa}} = \Phi_N(\mathbf c;\,R_\rho)$, the multivariate-normal CDF.
By **Slepian's inequality**, for $\rho>0$,
$$
\Phi_N(\mathbf c;\,R_\rho)\;\ge\;\prod_i\Phi(c_i)\;=\;\prod_i(1-\mathrm{FAR}_i),
$$
monotonically increasing in $\rho$. **Positive cross-location correlations
make the no-false-alarm event strictly more probable than the independent
product** — so Eq. (9) *under-counts* $P_{\text{no-fa}}$ and imposes a
**stiffer multiple-comparisons penalty** than a correlated observer actually
faces. Re-optimising criteria under correlated FAs therefore moves the
criterion-gain term, which is the C1 numerator/denominator. (This is a
re-derivation/replication question — flagged for CR-052 — but the *sign* of
the Slepian effect is settled: independence is the conservative, FA-penalty-
maximising corner.) No wiki substrate exists for Slepian / MVN-orthant
inequalities — a math-methods gap mirroring the C5 floating-point and A8
majorization gaps the agent has previously flagged.

### Source: [[cohen_maunsell2009_correlations]] (depth: full)

- **Bears on the claim how.** The single most load-bearing entry. Same
  paradigm class as the target paper — macaque **orientation change-detection
  with a peripheral validity cue** (paper §2.1 task). Simultaneous V4
  population recording: mean spike-count (noise) correlation
  $r_{SC}\approx 0.20$ unattended, $\approx 0.12$ attended (§5). Decisively:
  **>80% of the population sensitivity improvement under attention is
  attributable to the *reduction in noise correlations*, not single-neuron
  rate gain (<20%)** (key claims 2–3); shuffling the correlation structure
  while preserving rates destroys most of the attention benefit (claim 5).
- **Direction:** **contradicts** (I-neur premise) **+ constrains** (model
  completeness). (a) Cross-location/interneuronal correlations are
  substantial and behaviourally dominant in the paper's own paradigm, so the
  independence premise is empirically false at the population level. (b) The
  empirically *dominant* attentional lever — correlation reduction — is a
  **third mechanism** outside the paper's two-tool taxonomy (criterion shift
  vs. $d'$-reallocation). The model's scalar $d'(\alpha)$ conflates marginal
  gain (à la McAdams) with decorrelation (à la Cohen–Maunsell) and cannot
  represent value-directed decorrelation as a *distinct* channel.
- **Quantitative weight:** **Strong.** Replicated, mechanism-level primate
  result with a clean rate-vs-correlation dissociation; the canonical anchor
  of the population-coding-of-attention literature.
- **What the verdict did with this:** the spine of the contradiction leg —
  premise empirically false; "criterion captures 60–96%" is a statement about
  the *model's* reward decomposition, not about cortex's mechanism inventory.
  Drove the verdict to WEAKLY-SUPPORTED and seeded CR-053 (is decorrelation
  value-directed?).

### Source: [[ruff_cohen2016_cross_area_correlations]] (depth: full)

- **Bears on the claim how.** Same lab/paradigm, simultaneous V1+MT:
  attention **increases** cross-area $r_{SC}$ for RF-overlapping pairs while
  **decreasing** within-area $r_{SC}$ (key claims 1–2) — a sign reversal
  with anatomical scope. Microstimulation shows attention amplifies the
  V1→MT causal channel (claim 3).
- **Direction:** **contradicts / constrains.** The covariance structure
  attention manipulates is rich, sign-dependent on scope, and not reducible
  to a per-location marginal — exactly the dimension A1 assumes away. A model
  with one scalar $d'$ per location has no degree of freedom to represent
  "within-down, between-up."
- **Quantitative weight:** **Medium-to-strong.** Robust dual-direction
  result with a causal (microstim) leg; one of the few studies measuring both
  signs simultaneously.
- **What the verdict did with this:** reinforces that A1 is not a benign
  scalar idealisation — the omitted object (a structured, attention-modulated
  $\Sigma$) is itself the carrier of the dominant effect.

### Source: [[srinath2021_attention_information_flow]] (depth: full)

- **Bears on the claim how.** MT–SC simultaneous recording, same
  change-detection task: even after accounting for within- and cross-area
  noise-correlation changes, attention improves cross-population predictive
  efficacy; the authors attribute **~1/3** of the gain to decorrelation and
  **~2/3** to a "shared-variance amplification" not reducible to pairwise
  statistics (§5).
- **Direction:** **constrains.** Independence fails at an even higher order
  than pairwise correlation: the relevant object is the communication
  channel between populations, which attention amplifies multiplicatively.
  None of this is representable in an independent-per-location SDT model.
- **Quantitative weight:** **Medium.** Sophisticated single-study
  population-level result; bounds how much of the gap A1 could ever recover
  even if pairwise correlations were added.
- **What the verdict did with this:** caps the optimism of any "just add a
  correlation term" fix — there is structure beyond $\rho$.

### Source: [[mcadams_maunsell1999_reliability]] (depth: full)

- **Bears on the claim how.** V4 single-unit: attention is **pure
  multiplicative gain** ($G\approx1.26$), **Fano factor unchanged**, $d'$ up
  ~20% via the mean (claims 1–3). Explicitly notes (§6) the single-unit
  picture is "correct but **incomplete**": population reliability depends on
  pairwise covariance, which single electrodes cannot measure and which the
  2009 companion shows attention reduces.
- **Direction:** **supports (partial) / constrains.** Supports the *reality*
  of the model's $d'$-gain tool at the single-unit margin (a genuine
  sensitivity change exists, vindicating the $\beta$-scaled benefit). But its
  own §6/§7 hand-off to Cohen–Maunsell is the constraint: marginal $d'$ is
  one of two levers, and the model collapses both into $f(\alpha)$.
- **Quantitative weight:** **Medium.** Foundational single-unit result; its
  value here is precisely the self-flagged incompleteness.
- **What the verdict did with this:** the fair leg — A1's $d'$ tool is real,
  so A1 is an idealisation, not a fiction; the issue is *completeness*, not
  falsity of the sensitivity channel.

### Source: [[hawkins1990_attention_detectability]] (depth: full)

- **Bears on the claim how.** Foundational SDT-of-attention demonstration:
  spatial cueing produces genuine **$d'$ (sensitivity)** increases (0.3–0.6
  $d'$ units), with criterion shifts smaller and less consistent. Analysis is
  the standard **per-location HR/FAR SDT decomposition** the target paper
  inherits (Eqs. 1–2).
- **Direction:** **supports the convention.** The independent-per-location
  SDT framework is the *field-standard behavioural analysis* of cued
  detection; the target paper's A1 is a conventional, defensible modelling
  inheritance at the decision level, not an idiosyncratic choice.
- **Quantitative weight:** **Medium (methodological).** Establishes the
  legitimacy of the per-location-SDT idealisation behaviourally even though
  the neural substrate (Cohen–Maunsell) is correlated.
- **What the verdict did with this:** anchors the WEAKLY-SUPPORTED (not
  CONTESTED) call — at the behavioural/decision level A1 is the standard
  idealisation; the contradiction lives at the neural-population level the
  model does not claim to resolve.

### Source: [[ernst_banks2002_cue_combination]] (depth: full)

- **Bears on the claim how.** Canonical optimal multi-cue integration:
  precision-weighted (inverse-variance) combination is Bayes-optimal **only
  under independent noise**; the paper's own §6 flags that *"if the noises
  are correlated (e.g., shared attention fluctuations), the integration is no
  longer Bayes-optimal under the simple formula."*
- **Direction:** **constrains.** Directly relevant to the §5.5 "real
  observers emit a single global response" reading: a global decision is an
  *integration* across locations, whose optimal form depends on the
  cross-location correlation. The independent-decision product (Eq. 9) is the
  $\rho=0$ special case of a more general (and generally non-factorising)
  optimal pooling rule.
- **Quantitative weight:** **Medium.** Theorem-level statement of why
  correlated noise breaks independent-pooling optimality; general, not
  attention-specific.
- **What the verdict did with this:** ties the §5.5 "global response" concern
  to a precise optimality consequence, and marks the I-dec reading as the
  A6 cousin (heterogeneous/global decision rule, CR-011).

### Mechanism anchors consulted (supporting context, not load-bearing alone)

- [[luo_maunsell2018_criterion_sensitivity]] (full) — attentional *benefit*
  and *cost* (and criterion vs. sensitivity) have **dissociable neural
  substrates**; relevant because correlation-reduction is plausibly part of
  the "sensitivity" substrate the model folds into $f(\alpha)$, so the
  benefit/cost ratio $r$ may not be the only sensitivity knob. **Constrains.**
- [[reynolds_heeger2009_normalization]] (full) — divisive normalization
  changes *both* rate and correlation structure simultaneously (per
  Cohen–Maunsell §6/§7), so the model's $f(\alpha)$ gain and the omitted
  decorrelation channel are two faces of one normalization operation.
  **Constrains** (the omission is not arbitrary — it is the off-diagonal half
  of the same mechanism the model already half-represents).

### Net assessment (this version)

1. **Premise empirically false (I-neur).** Cross-location correlations are
   substantial ($r_{SC}\sim0.2$) and, via decorrelation, carry the *majority*
   of attention's behavioural benefit in the paper's own paradigm
   (Cohen–Maunsell). The richness is sign-dependent (Ruff–Cohen) and
   supra-pairwise (Srinath).
2. **Load-bearing for C1.** Independence is exactly the Eq. (9) product
   factorisation; positive $\rho$ relaxes the FA penalty (Slepian), so the
   criterion fraction is computed at the FA-penalty-maximising corner.
3. **Two-tool taxonomy incomplete.** The empirically dominant lever
   (decorrelation) is neither criterion nor $d'$-reallocation; "criterion
   captures 60–96%" is a within-model decomposition, not a claim about
   cortex's mechanism inventory.
4. **But A1 is the field-standard behavioural idealisation** (Hawkins), and
   the model's $d'$-gain tool is real (McAdams) — so A1 is an idealisation
   named and pre-empted by the paper, not a fatal error.
5. **The §5.5 "upper bound on VDA" self-characterisation is underived and
   sign-ambiguous.** Neural-decorrelation reading: if decorrelation is
   value-directed, real VDA could *exceed* the model's → "upper bound" wrong.
   Decision-aggregation reading: a single global criterion has fewer DoF to
   exploit value cheaply → could *raise* VDA reliance (also against "upper
   bound") *or* positive $\rho$ relaxing the FA penalty could make criterion
   *more* effective → less room for VDA (*supporting* "upper bound"). The
   literature cannot adjudicate the sign; only a re-derivation can.

**Direction of the verdict:** the assumption is empirically untenable under
I-neur and load-bearing for C1, but no attack in this version *shifted a
headline number* — consistent with mission §6, the verdict is set to
**WEAKLY-SUPPORTED** with the sign of the "upper bound" claim as the decisive
open question for the designated second (re-derivation) vector, CR-052.
