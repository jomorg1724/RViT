# SYNTHESIS_LOG.md — append-only run record (newest first)

---

## SY-013 — Abstract (written last, from the finished body)
- **run_id:** 2C4E6A80-1D3F-4B52-9C61-7A84E2F5B903
- **prompt_version:** 0.2
- **ended:** 2026-05-31T14:30:00Z
- **task worked:** SY-013 (highest-priority unblocked task; the whole-paper
  pre-abstract coherence pass SY-012 is done and `firewall_clean: true`, so
  the abstract — mission's designated last first-draft increment, written
  from the finished body — is next on the arc)
- **output kind:** frontmatter (section: abstract)
- **section touched:** `sections/abstract.tex` (written from the red stub)

**Headline thing done.** Replaced the red abstract placeholder with a
finished Abstract: one unstructured paragraph (~205 words), no citations,
no meta, written from the completed body. It states the cued
change-detection task and the three adaptive levers (criterion adjustment,
value-directed attention, decorrelation of the population code, with the
cross-location correlation a free parameter whose zero limit recovers the
independent-noise case), then the four findings positively at their body /
ledger strength: (C1) criterion adjustment typically dominant, median
≈ three-quarters of the reward gain with a substantial tail in which
attention contributes materially; (C2) the attention benefit non-monotonic
in the benefit/cost ratio, lower edge of the active band in closed form;
(C3) concentrated in a graded regime (low validity, high value contrast,
cost-dominant asymmetry), mapped quantitatively and turned into validity
thresholds for cueing designs; (C4) no inversion under a predictive cue as
a conditional theorem, with anti-cue inversion as a new falsifiable
prediction.

**Grounding summary.** Every clause restates an already-grounded body
result (AB1–AB6 in `TRACE.md`): C1 `sec:results-criterion` (median CF
0.7552 A / 0.7682 B); C2 `sec:results-vda-nonmonotonic` (`eq:r-dagger`);
C3 `sec:results-graded` (iso-VDA band, validity thresholds); C4
`sec:results-noninversion` (`eq:value-weight`, condition $\valid\ge1/\Nloc$,
36.1% anti-cue inversion at $\Nloc=4$). No number, mechanism, or claim is
introduced that is not already in (and grounded by) the body; nothing is
stated above its CLAIM_LEDGER row.

**Mission note (firewall).** The `Rebuild/` source abstract is written in
build-process voice (it speaks of rebuilding, an inherited paper, a
"published [0.60, 0.96] interval … retracted", and claims licensed by a
named ledger). None of that was re-flowed. The Abstract was written fresh,
positive, and standalone — this paper's own result on its own footing.

**Firewall sweep.** Banned-vocabulary grep on `abstract.tex`: zero hits.
No reconstruction/inherited/published/retracted language, no
comparison-hedge framing, no version tag, no build-process comment (the
file's lone `%` comment was tightened to a content description).

**Compile.** `pdflatex` ×2 + `bibtex` + `pdflatex` ×2, exit 0, **33
pages**, 0 undefined references, 0 undefined citations, 0 bibtex warnings.
One pre-existing 3.0pt overfull hbox (Supplementary, Corollary 2) — not
introduced by the abstract; nothing new.

**Gaps.** 0 opened, 0 closed. G-001 (model attention-to-$\dprime$
illustration figure) remains open and owner-mediated.

**What the next run should do.** SY-014 — front/back-matter finalisation
(title/author block already clean; figure list; final build). The
"submission-ready draft" milestone requires zero open gaps, and **G-001 is
still open**, so SY-014 cannot flip the README to "draft complete" until
the rebuilder stages the model attention-to-$\dprime$ figure under
`Rebuild/manuscript/figures/` or the owner decides to drop that
illustration.

---

## SY-012 — Coherence pass (whole paper, pre-abstract)
- **run_id:** 1B2C3D4E-5F60-4A71-9B82-2C93D4E5F607
- **prompt_version:** 0.2
- **ended:** 2026-05-31T13:00:00Z
- **task worked:** SY-012 (highest-priority unblocked task; the de-meta
  scrub gate was already satisfied — `firewall_clean: true` from SY-015 —
  and the body + Methods + Supplementary are all written, so the
  pre-abstract whole-paper coherence pass is next on the arc, and is the
  required step before the abstract can be written from the finished body)
- **output kind:** coherence
- **section touched:** `sections/results.tex` (two grid-description
  reconciliations), `sections/methods.tex` (one grid-count reconciliation)

**Headline thing done.** Third interleaved coherence pass, end to end
before the abstract. Firewall re-swept first (mandatory on a coherence
pass): zero hits across all `.tex` + `refs.bib`; `main.tex` title/author
block already clean (`[Author names]` / `[Affiliations]`, no build
footnote, no version tag). Found and fixed two cross-section
parameter-grid drifts, both reconciled onto the validated source and
both content-preserving (no headline number, distribution, or claim
strength changed):

1. **Distributional-sweep $\Rsens$ grid (Results §4.1 vs Methods).**
   Results said "$21$ log-spaced points" — which lands directly on the
   4,410 valid cells with no drop — while Methods correctly said "$22$
   ratios … of 4,620 nominal cells, 4,410 valid." The source
   `Rebuild/sims/C1--cf-distribution/run.py` is decisive:
   `R_GRID = np.unique(concat([logspace(log10(0.1),log10(10),21),[1.0]]))`
   = 22 r-values; `n_total = 22·21·5·2 = 4620`; `n_valid = 2205`/variant
   (one degenerate $\Rsens$-slice dropped). Rewrote §4.1 to "$22$ values
   ($21$ log-spaced plus a pinned $\Rsens=1$)" and stated the
   4,620-nominal / 4,410-valid (2,205/variant) distinction, matching
   Methods and the source.
2. **VDA$(\Rsens)$ grid count (Results vs Methods).** Results said "$84$
   log-spaced points"; Methods said "$83$ log-spaced ratios (… pinned)."
   The C2 README gives *both* "83-point + pinned log-spaced r-grid"
   (l.13) and "84-pt r-grid" (l.103): 83 log-spaced ∪ a pinned set = 84
   total. Harmonised both sections to "$84$ (83 log-spaced + pinned
   escape/peak neighbourhoods)."

**Grounding summary.** Both fixes resolve to the C1/C2 sim
`run.py`/README — the authoritative grids — used silently. The
valid-cell counts the prose already reports (4,410; 2,205/variant; peak
on the 84-point grid) are unchanged; nothing exceeds its evidence. No
result, number, or mechanism invented or altered.

**Coherence checks that passed without edits.** Cross-reference graph
fully resolves (98 labels, 236 `\ref`/`\eqref` calls, 0 undefined on a
3-pass build); 11/11 `\includegraphics` targets present in `figures/`
and each referenced exactly once; notation consistent vs the
`\newcommand` block ($\varphi$, $\dprime_{\mathrm{base}}\equiv\dprime_b$,
three-lever symbols); intro four-finding previews match body strength;
all sweep sizes (4,410 / 2,205 / 3,534 / 420 / 544 / 72; the
$31{\times}19{\times}3{\times}2$, $4{\times}3{\times}6$, $17{\times}16$
grids) now consistent Results ↔ Methods.

**Firewall sweep.** Clean before and after. Banned-vocabulary grep over
all `.tex` + `refs.bib`: zero hits. Edits introduced no meta, no
comparison framing — both are positive parameter-grid statements.

**Compile.** Clean 3-pass build (`pdflatex` ×2 + `bibtex` + `pdflatex`),
exit 0, **33 pages**, 0 undefined references/citations, largest overfull
hbox 3.0pt.

**Gaps.** 0 opened, 0 closed. G-001 (model attention-to-$\dprime$
illustration figure) remains open and owner-mediated; the abstract stub
remains a deliberate placeholder (written last).

**What the next run should do.** SY-013 — write the Abstract (~150–200
words, unstructured, no citations, no meta) from the finished body, now
unblocked. Then SY-014 (front/back-matter finalisation; flip README to
"draft complete" iff zero open gaps — note G-001 is still open, so the
"submission-ready" milestone is not yet reachable without the model
figure or a decision to drop it).

---

## SY-011 — Section (Supplementary derivations and extensions)
- **run_id:** E8F1A0D4-7C26-4B9A-A3E5-1F08C7B24D60
- **prompt_version:** 0.2
- **ended:** 2026-05-31T12:00:00Z
- **task worked:** SY-011 (highest-priority unblocked section; prereq SY-007 done;
  the two main-text forward-references into the Supplementary — Model §reward for
  the correlated-noise derivation + Slepian monotonicity, Results §4.2 for the
  escape-threshold derivation — were both still dangling on a red stub)
- **output kind:** section
- **section touched:** `sections/appendix.tex` (written from stub);
  `refs.bib` (+1 entry); `sections/discussion.tex` (one firewall fix)

**Headline thing done.** Replaced the red Supplementary stub with a full,
self-contained Supplementary in clean Nature-Neuroscience voice — four
subsections, ~430 LaTeX lines, every derivation lifted from validated
material and every trace of how it was assembled stripped:

1. *The correlated no-false-alarm probability and its monotonicity* —
   the one-factor reduction that produces the boxed integral
   `eq:pnofa-rho` (discharging the Model §reward promise of "the full
   derivation … in the Supplementary"), the 64/128-node quadrature
   agreement, the Slepian orthant-monotonicity Proposition
   (`prop:orthant-monotone`, cites `Slepian1962`/`Tong1990`) and its
   per-policy reward corollary, and the two-channel account of why the
   sign of $\partial\VDA/\partial\corr$ flips with $\Rsens$.
2. *Closed-form escape threshold* — the boundary collapse, the two
   $\corr$-aware Gauss–Hermite gradient integrals, the boundary
   first-order condition, the boxed threshold
   `eq:r-dagger-rho` (`prop:escape-rho`), the structural $\corr\to0$
   recovery to the Results closed form `eq:r-dagger`, and the drift
   table `tab:r-dagger-rho-drift` (discharging the Results §4.2 promise).
3. *Symmetric recovery at unit benefit/cost ratio* — the real-number
   identity (`prop:symmetric-recovery`), the bit-exact Sterbenz-band
   identity (`prop:bitexact-recovery`, cites `Sterbenz1974`/`Goldberg1991`)
   with its off-band threshold, and the smooth-centre reading.
4. *The power-mean conservation family* — the closed-form weights, HLP
   monotonicity as a KL-divergence identity (`eq:hlp-kl`), the
   symmetric-corner identity, the full three-step proof that the escape
   threshold is conservation-form invariant, and the criterion-fraction
   chain rule with its one analytic invariant and the honest open status
   of the uniform $\Delta\CF\le0$ bound.

**Grounding summary.** 19 assertions, all traced (TRACE.md P1–P19) to the
validated decorrelation-channel / escape-threshold / symmetric-recovery /
power-mean material, used silently at ledger strength (C2 confirmed
closed-form + conservation-invariant + $\corr$-extended; C5 confirmed
consistency result; A3 banded family with the $\Delta\CF$ closed form
declared open; A1 monotonicity + two-channel sign). No number exceeds its
ledger row; the $\corr=0$ column of `tab:r-dagger-rho-drift` matches the
already-published `tab:r-dagger-family` digit-for-digit. No result, number,
or mechanism invented.

**Firewall sweep.** New file written firewall-clean from the start; the
two `inherit` hits found on first sweep were ordinary mathematical usage
("a term inherits a dependence") and were reworded anyway
(`depend on`/`carry`) as insurance. Whole-manuscript sweep then surfaced
one *pre-existing* comparison-hedge in `sections/discussion.tex` ("…a
substantial tail, **not a categorical split**") — the exact construction
the firewall bans — rewritten to the positive "…a substantial tail across
the parameter space." Final whole-manuscript grep: **zero hits**.

**Compile.** Clean 3-pass `pdflatex` + `bibtex`; **33 pages** (was 26),
0 undefined references/citations, largest overfull box 3.0 pt. One new
real bib entry (`Tong1990`, Springer 1990) added and resolved.

**Gaps.** None opened (the Supplementary is pure derivation, no figures).
G-001 (the Model §2.3 attention-to-$d'$ illustration figure) remains open
and untouched.

**What the next run should do.** SY-012 — the full pre-abstract coherence
pass, now unblocked (SY-011 was its last prereq alongside SY-008/SY-010):
verify the complete cross-reference graph end to end (the Supplementary
adds ~30 new `\ref`/`\eqref` targets and four propositions), confirm the
Methods "→ Supplementary" pointers land on the right subsections, check
notation across Methods↔Supplementary (e.g. $\dprime_{\mathrm{base}}$,
the GH node count), and confirm G-001 is the only open placeholder before
the abstract (SY-013) is written.

---

## SY-009 — Coherence pass (Results §4.1–§4.4 + Discussion)
- **run_id:** C3D9A1F7-8B20-4E5C-9F61-2A7D4C0E8B13
- **prompt_version:** 0.2
- **ended:** 2026-05-31T00:00:00Z
- **task worked:** SY-009 (second interleaved coherence pass, due after four
  sections landed since SY-005 — mission §4.1; firewall already clean, so the
  regular loop, with the de-meta scrub satisfied at SY-015)
- **output kind:** coherence
- **section touched:** `sections/results.tex`, `sections/discussion.tex`

**Headline thing done.** End-to-end consistency pass over the second
integrated stretch. One substantive cross-section defect found and fixed,
plus a clean bill on everything else. The defect: a terminology
conflation between **two orthogonal axes** that the validated model keeps
distinct — the **reward variant** (variant~A = value-coupled correct
rejection, $\CR=\valid\val+(1-\valid)$; variant~B = fixed, $\CR=1$) and
the **conservation rule** (additive $\benefit+\cost=2$ vs multiplicative
$\benefit\cdot\cost=1$, a separate one-parameter family). The
Reconstruction's own Model §2.4 and Methods define A/B as the *reward*
variant; Results §4.1/§4.2 and the Discussion had drifted to labelling
A/B "conservation variants" and to pairing the median $\CF=0.7552$ with
"the additive rule." Five content-preserving fixes, **no number changed**:
1. "conservation variant" → "reward variant" at all seven Results spots,
   including the `tab:cf-distribution` and `fig:cf-histogram` captions.
2. §4.1 "Robustness to the conservation rule": reworded so
   additive/multiplicative are the conservation-family **endpoints**
   (swept within each reward variant), not "the two variants above" — the
   paragraph's own $-0.0012$/$-0.0042$ additive→multiplicative shifts make
   the orthogonality explicit.
3. §4.2: "$\CR(\val)$ encodes the conservation rule" → "$\CR(\val)$ is the
   correct-rejection reward scaling set by the reward variant"; $\CR=1$
   kept as the value-blind computational setting and additive conservation
   named as the (separate) weight rule.
4. Discussion opening: medians $0.7552$/$0.7682$ re-attributed to the
   value-coupled / equal-reward **variants**, both at the additive
   conservation rule.
5. Discussion "New predictions": "the additive, value-weighted
   convention" → "the value-coupled reward variant."

**Coherence checks that passed without edits.** Full cross-reference graph
resolves (51 distinct `\ref`/`\eqref` targets, every one defined; no
dangling refs, no undefined citations). Intro's four-finding previews
match the body strength (criterion median $\approx0.76$ in $[0.30,1.00]$
with a $\corr$-growing tail; non-monotonic VDA with $\rdagger(\val)$ edge;
graded contour band; conditional no-inversion + anti-cue prediction).
Prediction wording consistent across Results and Discussion: dormant-cell
amplification $\VDA\,0.0007\!\to\!0.0676$ ($\approx96\times$) ↔
"roughly a hundredfold"; the anti-cue boundary $\valid<1/[(\Nloc-1)\val+1]$
and the $\valid\ge0.95/0.80/0.75$ design thresholds stated identically in
both sections. Density glyph uniformly $\varphi$ (the SY-005 fix held).

**Grounding summary.** A coherence pass asserts nothing new; authority for
the variant/conservation distinction is Model §2.4 + Methods +
the validated source (`model.tex`, `extensions.tex`:
$0.7552\!\to\!0.7540$ var-A, $0.7682\!\to\!0.7640$ var-B as additive→
multiplicative — i.e. A/B persist across the conservation move). Recorded
as the SY-009 note in `TRACE.md`. No assertion exceeds its ceiling; no
finding restated at a different strength than before.

**Firewall sweep.** Re-swept `results.tex` + `discussion.tex` for the full
banned vocabulary: **zero hits.** No meta reached the page; the new wording
("reward variant", "value-coupled", "conservation-family endpoints") is
positive, standalone science.

**Compile.** `pdflatex`×3 + `bibtex`, all exit 0. **26 pages** (unchanged),
0 undefined references, 0 undefined citations, 0 overfull `\hbox`, no
errors.

**Gaps.** 0 opened, 0 closed. G-001 (the attention-to-$\dprime$ mapping
figure in the Model) remains the single open gap, untouched.

**What the next run should do.** SY-011 — the Supplementary material
(`sections/appendix.tex`): the symmetric recovery at $\Rsens=1$, the
closed-form $\rdagger(\val)$ derivation, the correlation-aware
$\rdagger(\val;\corr)$ extension and drift table, the
$\rstarinv$/symmetric-corner derivation, and the power-mean conservation
family — all forward-referenced from Results §4.2/§4.5 and Methods and
currently pointing at the `sec:appendix` stub. Then SY-012 (whole-paper
coherence, pre-abstract), SY-013 (Abstract, last), SY-014 (frontmatter /
draft-complete milestone). G-001 is the only thing standing between the
current draft and a zero-open-gap state.

---

## SY-010 — Section (Methods)
- **run_id:** B7E3F0A2-1D4C-4F8A-9E2B-6C5A0D7E13F4
- **prompt_version:** 0.2
- **ended:** 2026-05-31T00:00:00Z
- **task worked:** SY-010 (Methods; next unblocked arc section after Discussion; firewall already clean — regular loop, not the scrub)
- **output kind:** section
- **section touched:** `sections/methods.tex` (red placeholder → full section)

**Headline thing written.** The Methods, at the end of the arc, in
detailed venue voice. Seven subsections: (i) *Task and decision model* —
SDT recap referencing the Model equations, the headline perceptual cell
($\Nloc=4$, $\dprimemax=2$, $f_0=0.5$, $h=\sqrt\cdot$), the four transfer
forms used for robustness; (ii) *Benefit, cost, and reward variants* —
the additive conservation rule, the power-mean conservation family
deferred to Supplementary, the value-coupled (A) vs fixed (B) correct-
rejection reward; (iii) *Correlated-noise channel* — the one-factor
Gauss–Hermite quadrature (64 nodes, $\le 10^{-15}$ vs a 128-node
reference), with the $\corr\in\{0,0.2\}$ band anchored to V4 spike-count
correlation; (iv) *Policy optimisation* — exhaustive grid search, the
121-point criterion grid ($\Delta c=0.05$ over $[-3,3]$), the attention
grids ($[1/\Nloc,1]$ for P1/P2, extended to $[0.02,1]$ for the
distributional and anti-cue sweeps), and the value-blind caching; (v)
*Parameter sweeps* — the four sweeps with exact grid sizes (4,410-valid
distributional; 83-point VDA($\Rsens$) family; 3,534-cell iso-VDA;
inversion = 420 closed-form cells + 197-point verification + the
anti-cue grid + a 544-cell allocation map); (vi) *Validation* — the
$\corr\to0$ recovery contract to floating-point precision, the
closed-form/grid agreement ($\rdagger$ ordering and the exact
symmetric-corner identity), and the Slepian monotonicity sign check;
(vii) *Reproducibility* — fully deterministic, no Monte-Carlo, fixed
grids giving bitwise-reproducible output.

**Grounding summary.** Every equation is lifted by `\ref`/`\eqref` from
the already-written Model and Results (no re-derivation, no duplicated
definitions). Every grid size, node count, and tolerance is grounded in
the C1/C2/C3/C4 sim READMEs and `Rebuild/model/core.py` (criterion grid
`C_GRID` = 121 pts; `default_alpha_grid` step 0.005; C1 `run.py`
`R_GRID`/`V_GRID`/`V_LIST` and the 0.02-step `ALPHA_GRID`; `gauss_hermite(64)`).
Methods asserts no finding — it documents procedure; the findings stay in
Results. Traced ME1–ME7 in `TRACE.md`.

**Firewall sweep.** Zero hits on `sections/methods.tex` for the full
banned-vocabulary set. The READMEs validate by comparing to an external
"reviewer substrate" (max $|\Delta\CF|=1.47\mathrm{e}{-6}$; 48.6% vs a
reported 49.0%); those external comparisons are **deliberately not
surfaced** — validation is framed only as the model's internal
$\corr\to0$ limit (stated conservatively as $<10^{-6}$) and its
closed-form/grid self-consistency. No file paths, sha256, or sim ids in
the prose. "Supplementary," not "Appendix."

**Compile.** Clean `pdflatex`×3 + `bibtex`, then a re-pass after fixing
one 6.2 pt overfull box (the inline cell-parameter tuple, respaced).
Final: **26 pages** (was 24), 0 undefined refs/citations, 0 overfull
boxes.

**Gaps.** None opened (Methods needs no figures); G-001 (the
attention-to-$\dprime$ mapping figure, in the Model) remains open and
unchanged.

**What the next run should do.** SY-009 (coherence pass over Results +
Discussion) is now due — four sections have landed since the last
coherence pass (SY-005). Alternatively SY-011 (Supplementary: symmetric
recovery at $\Rsens=1$; the $\rdagger$ closed form; the conservation
family) is the last unwritten body section. Recommended order: SY-009 →
SY-011 → SY-012 (whole-paper coherence) → SY-013 (Abstract, last) →
SY-014 (frontmatter / draft-complete milestone). The Methods now
forward-refs Supplementary in two places (conservation family; the
$\rdagger$ and recovery derivations) — SY-011 should close those.

---

## SY-008 — Section (Discussion)
- **run_id:** 4A8E2D17-9C0B-4E6A-A1F2-7B3D5E8C09A4
- **prompt_version:** 0.2
- **ended:** 2026-05-30T23:59:59Z
- **task worked:** SY-008 (Discussion; next unblocked high-priority arc section after the four Results findings; firewall already clean so the regular loop, not the scrub)
- **output kind:** section
- **section touched:** `sections/discussion.tex` (placeholder → full section)

**Headline thing written.** The Discussion, in clean positive venue
voice. An opening synthesis of the four findings, then six descriptive
subsections: (i) *why criterion adjustment is typically dominant* —
criterion shifts exploit value without paying a perceptual trade-off, so
the criterion fraction concentrates above one-half (median 0.7552 / 0.7682,
$[0.30,1.00]$) and cedes only in the benefit-dominant low-validity corner;
(ii) *the benefit/cost asymmetry and its biological reading* — $\Rsens$ as
the enhancement-vs-suppression efficacy ratio, read through the
normalisation/gain literature, with the non-monotonic VDA advantage
peaking in a cost-dominant window bounded below by $\rdagger(\val)$;
(iii) *guidance for experimental design* — the $\valid\ge0.95$ /
$\valid\ge0.80$-at-$\corr{=}0$ / $\valid\ge0.75$-too-permissive boundary,
and why standard high-validity cueing paradigms sit in the dormant regime;
(iv) *new predictions* — anti-cue inversion under $\valid<1/\Nloc$ as a
falsifiable re-allocation signature, the decorrelation lever with a
$\Rsens$-dependent sign and a ~100× dormant-cell amplification at the
empirical $\corr=0.2$ anchor, and the conservation-form / variant-B
sensitivity of the criterion/attention tail; (v) *scope and limitations*.

**Grounding summary.** Every assertion traced (TRACE D0–D9). C1 (criterion
median + tail), C2 (non-monotonic + $\rdagger$), C3 (graded corner, design
box, $\corr$ sign-flip, dormant-cell amplification), C4 (conditional
no-inversion + anti-cue), conservation band + variant-B sensitivity — all
at LEDGER strength. Biological reading hedged as interpretation and paired
with an explicit no-neural-implementation limitation. Limitations content
lifted from internal scope prose with all build-framing stripped.

**Firewall sweep.** Zero meta. Grep over `discussion.tex` returns only
`inVERSION`/`noninVERSION` substring false-positives. No
prior/original/rebuilt/reviewer/ledger language; no comparison-hedges; the
conservation and variant findings stated as positive structural properties.
Did not reconstruct the upstream §5.3 NN self-reference (not a scientific
element; no gap).

**Compile result.** Clean 3-pass `pdflatex` + `bibtex`. **24 pages**
(was 21). 0 undefined references/citations, 0 overfull hboxes, 0 LaTeX
warnings.

**Gaps.** 0 opened, 0 closed. G-001 (Model Figure 1 attention→$d'$
mapping) remains open.

**What the next run should do.** SY-009 — the second interleaved coherence
pass over Results + Discussion: verify the §4.1/§4.3/§4.4 forward-refs to
`sec:discussion` now resolve to the matching content (they do — D5/D7/D8),
check prediction wording is consistent across Results and Discussion,
notation/figure-ref consistency, and re-sweep the firewall. Then SY-010
(Methods) and SY-011 (Supplementary/derivations); abstract (SY-013) last.

---

## SY-007 — Section (Results, no inversion under predictive cues)
- **run_id:** 9E4D7C13-6A21-4F0B-B8E5-1D7C2A93F6E4
- **prompt_version:** 0.2
- **ended:** 2026-05-30T23:59:59Z
- **task worked:** SY-007 (fourth/closing Results finding; next unblocked high-priority section after SY-006)
- **output kind:** section
- **section touched:** `sections/results.tex` (new subsection `sec:results-noninversion`); `manuscript/figures/` (+3); `BUILD.md`

**Headline thing written.** The closing Results finding: *optimal
allocation does not invert when the cue is predictive.* Whenever the
cued location carries at least its chance share of targets
($\valid\ge1/\Nloc$), the optimum stays at or above the uniform share
$1/\Nloc$ everywhere in the primary range. The governing boundary is the
closed-form value-weight inequality $w_c\ge w_u \iff \valid\ge
1/[(\Nloc-1)\val+1]$; a closed-form local threshold $\rstarinv=
(\Nloc-1)A_0/B_0$ organises the boundary bimodality, with the exact
symmetric-corner identity $\rstarinv(1/\Nloc,1,\cdots)=1$. Crossing into
the counter-predictive regime ($\valid<1/\Nloc$) flips the inequality and
the optimum inverts ($\alpha^\star<1/\Nloc$) — presented as a new
falsifiable prediction (36.1% incidence on the probed sub-grid, sharp
$\val$-dependence). Three figures placed (closed-form threshold map,
reward-vs-allocation family, optimal-allocation heatmap).

**Grounding summary.** All assertions traced N0–N8 + Robustness in
TRACE.md against the C4 anti-cue-inversion simulation output and the C4
derivation, at the LEDGER:C4 (CONFIRMED-CONDITIONAL) ceiling. The
"regardless of $\Rsens$" wording in the ceiling is deliberately not
reproduced; replaced by the positive closed-form bimodality + conditional
theorem. Behavioural alignment cites six pre-existing bib keys (0 new).

**Firewall sweep.** Grep over all `.tex` for the banned vocabulary
(reconstruct/rebuild/synthesiz/inherited/prior/previous/published/
critique/reviewer/verdict/ledger/provenance/defensible/restate/sha256/
step-[ABCD]/claim-ids): **zero hits**. The section was written positively
from the start — no comparison or correction framing reached the page.

**Compile.** Clean 3-pass (pdflatex ×2 + bibtex + settle). 21 pages
(was 17), 0 undefined refs/citations, 0 overfull hboxes, no errors.

**Gaps.** 0 opened, 0 closed. All three figures existed in the C4 sim
output. G-001 (the model-illustration attention→$d'$ mapping figure)
remains the single open gap.

**What the next run should do.** SY-008 — the Discussion (why criterion
dominates; re-scoped quantitative design advice; biological reading of
$\Rsens$; the new predictions: counter-predictive inversion and the
dormant-cell decorrelation amplification; conservation-band sensitivity).
The Results argument is now complete (four findings + model). After
Discussion, SY-009 is the second interleaved coherence pass over
Results+Discussion.

---

## SY-006 — Section (Results §4.3, the graded regime)
- **run_id:** 7B3F1A92-5D2C-4E18-A6F0-3C91B47E2DA5
- **prompt_version:** 0.2
- **ended:** 2026-05-30T23:59:59Z
- **task worked:** SY-006 (third finding; next unblocked high-priority section after the SY-005 coherence pass)
- **output kind:** section
- **section touched:** `sections/results.tex` (new §4.3 `sec:results-graded`); `manuscript/figures/` (+3); `BUILD.md`

**Headline thing written.** The third of the four findings:
*the value-directed attention benefit is concentrated in a graded
regime.* An iso-VDA contour band over the experimental-design plane
$(\valid,\val)$ shows the benefit is materially large only in a corner
at low validity / high value contrast / moderate-low $\Rsens$, with a
graded (not categorical) boundary. The section delivers the model's
quantitative experimental-design prediction — $\valid \gtrsim 0.95$
unconditionally, or $\gtrsim 0.8$ if cross-location correlation is
bounded below $r_{SC}\approx0.2$, with $\valid\ge0.75$ shown too
permissive — as a positive recommendation on the paper's own footing
(no comparison to any absent statement). Closes with the decorrelation
sign-flip across the plane and the $\approx96\times$ dormant-cell
amplification at $(0.7,10,0.3)$, flagged as a falsifiable prediction
for the Discussion.

**Grounding summary.** Eight assertions (G0–G7), all from
SIM:C3--iso-vda-Vv (3,534-cell sweep, sha256 `72820559…`) at
LEDGER:C3's graded/quantitative ceiling, with the $\corr$ sign-flip and
dormant-cell amplification at the joint LEDGER:C3 + LEDGER:A1 strength.
Three figures (`iso_vda_contours`, `vda_at_high_V`, `iso_vda_drho`)
copied from the sim output. Three tables (`graded-marginals`,
`graded-highV`, `graded-signflip`) carry the numbers to the digits the
sim reports. $r_{SC}\approx0.2$ anchor cites CohenMaunsell2009 (already
in `refs.bib`). Full map in TRACE G0–G7.

**Firewall sweep.** Section written from scratch in positive venue
voice; the categorical high-validity statement is presented as the
model's contour-band guidance, never as a correction of anything. Grep
for banned vocabulary across all `.tex` (incl. comments): **0 hits.**

**Compile result.** Clean 3-pass `pdflatex` + `bibtex`: **17 pages**
(was 13), 0 undefined references, 0 undefined citations, 0 overfull
boxes.

**Gaps.** None opened, none closed. All three figures pre-existed; G-001
(the attention→$d'$ Model figure) remains the only open gap, untouched.

**What the next run should do.** SY-007 (Results §4.4–§4.5: the
conditional no-inversion theorem $\valid\ge1/\Nloc$, closed-form
$r^\dagger_{\mathrm{inv}}$, symmetric-corner identity, and anti-cue
inversion as a new prediction; place `r_inv_closed_form`,
`er_vs_alpha_anticue`, `alpha_star_V_r_map`). That completes the Results
arc and unblocks the SY-008 Discussion and the SY-009 second coherence
pass.

---

## SY-005 — Coherence pass (Intro + Model + Results §4.1–§4.2)
- **run_id:** 2F9C61B4-7A3E-4C81-B0D5-9E62F1A4C73B
- **prompt_version:** 0.2
- **ended:** 2026-05-30T23:59:59Z
- **task worked:** SY-005 (first interleaved coherence pass, due after 4 integrated sections — mission §4.1)
- **output kind:** coherence
- **section touched:** `sections/model.tex`, `sections/results.tex` (+ `BUILD.md`)

**Headline thing done.** End-to-end consistency pass over the first
integrated stretch. Five content-preserving fixes — no assertion,
number, equation, or figure changed:
1. **Density glyph unified.** The Results gradient coefficients
   $K_c, K_u$ wrote the standard-normal density as $\phi$ while the
   Model's boxed orthant integral uses $\varphi$. Conformed the
   agent-authored Results equations to the upstream Model glyph
   ($\varphi$, 4 occurrences); the copied Model equation was left
   untouched.
2. **Baseline symbol de-duplicated.** Results §4.2 introduced
   $\dprime_b := \dprimemax f(1/\Nloc)$ for a quantity the Model already
   defines as $\dprime_{\mathrm{base}}$. Replaced the `:=` with an
   identification $\dprime_b \equiv \dprime_{\mathrm{base}}$ + a pointer
   to Section~\ref{sec:model}, so the baseline is defined once and the
   compact subscript stays available for the dense $K$ expressions.
3. **Supplementary wording unified.** The two Model cross-references to
   the supplementary section said "Appendix"; Results and the section
   heading say "Supplementary." Brought the Model into line ("the
   Supplementary material (Section~\ref{sec:appendix})"). Internal
   label/filename `sec:appendix`/`appendix.tex` left as-is (not
   reader-visible).
4. **Overfull `\hbox` cleared.** The single remaining overfull box
   (54.7pt, the Results §4.2 "threshold falls as cued value rises"
   paragraph, caused by the wide config tuple landing at a tight line
   start) fixed by re-ordering the sentence
   ("Evaluating Eqs.~… at the configuration … gives …"). The Model §2.4
   box flagged in earlier runs had already cleared once SY-004
   re-paginated.
5. **Two "trace"→"curve"** rewordings (plot-curve sense; also removes a
   borderline `trace` substring from the firewall sweep).

**Coherence checks that passed without edits.** Intro's four-finding
previews match the §4.1–§4.2 body strength (criterion median $\approx
0.76$, span $[0.30,1.00]$, tail; VDA non-monotonic, peak in the
cost-dominant band, $\rdagger(\val)$ as the lower edge). All five
referenced figures present in `figures/`. Captions match their text.
CF and VDA each defined once (Model), referenced not redefined in
Results. §4.1→§4.2 transition intact.

**Firewall sweep result.** Re-swept all `.tex` + `refs.bib` for the full
banned-vocabulary set: **zero reader-visible hits** (the only matches are
the internal `sec:appendix` label, the `\appendix` command, and the
`appendix.tex` filename, none of which render). `firewall_clean` remains
**true**.

**Compile result.** `pdflatex ×3 + bibtex`, all exit 0, **13 pages**, **0
overfull `\hbox`**, 0 undefined references, 0 undefined citations.

**Gaps.** None opened, none closed. G-001 still open.

**What the next run should do.** SY-006 — Results §4.4 (the graded regime
where VDA matters, C3): the iso-VDA contour band over $(\valid, \val,
\Rsens)$, the high-$\valid$ probe table, and the graded design boundary,
in graded (not categorical) voice. Place `iso_vda_contours`,
`vda_at_high_V`, `iso_vda_drho` if staged under `Rebuild/`; gap any that
are absent. Then SY-007 (§4.5–4.6, C4 + robustness).

## SY-004 — Results §4.2: VDA non-monotonic in the benefit/cost ratio (C2)
- **run_id:** A7E3F1C9-2B58-4D6E-8F01-3C9A7E0B16D2
- **prompt_version:** 0.2
- **ended:** 2026-05-30T23:59:59Z
- **task worked:** SY-004 (next first-draft section after the de-meta scrub)
- **output kind:** section
- **section touched:** `sections/results.tex` (new `sec:results-vda-nonmonotonic`)

**Headline thing written.** The confident centerpiece of the paper:
$\VDA(\Rsens) = \Rpone - \Rptwo$ is non-monotonic in the benefit/cost
ratio — rises from zero, peaks in an interior band, decays again — and
the model supplies a closed-form lower edge for that band, the escape
threshold $\rdagger(\val) = K_u(\val)/[(\Nloc-1)K_c(\val)]$ (Eqs
eq:r-dagger, eq:K-c, eq:K-u). Five paragraphs + three tables + two
figures: the threshold's $\val$-family numerics (falls 0.343→0.016 over
$\val=1..10$, Table r-dagger-family, Fig r_dagger_vs_v); the empirical
peak lying above $\rdagger(\val)$ for every $\val$ (Table
peak-vs-threshold, 84-pt log-grid) with peak height growing
0.012→0.183 in $\val$ (Fig vda_curves_vfamily); and the decorrelation
sensitivity — $\corr:0\to0.2$ suppresses the peak for $\val\le8$,
amplifies at $\val=10$, drifts $r^\star$ upward, with a closed-form
$\rdagger(\val;\corr)$ that drifts up +3%..+30% and sign-matches the
empirical drift at every $\val\neq1$ (Table rho-sensitivity).

**Grounding summary.** Every number and both figures come from the
$84\,r \times 5\,v \times 2\,\rho$ C2 sweep (output sha256
09ecef3c…); the closed-form threshold and its $\corr$-aware extension
from the C2 derivation. Stated at the LEDGER:C2 confident-centerpiece
ceiling; the decorrelation result kept at LEDGER:A1 strength and stated
positively as a model property (decorrelation is not a uniform
attenuator of VDA). Traced V0–V7 in TRACE.md.

**Firewall sweep result.** Grep over `results.tex` for the full
banned-vocabulary set returns **zero hits**. No comparison to any other
text; the non-monotonicity and the decorrelation finding are stated on
the paper's own footing. `firewall_clean` remains **true**.

**Compile result.** `pdflatex ×2 + bibtex` (+ third pass), all exit 0,
**13 pages** (was 10), 0 undefined references, 0 undefined citations.

**Gaps.** None opened; G-001 still open. Forward references to the
Supplementary ($\corr$-aware derivation + drift table) point at
`sec:appendix` (stub exists, content lands under SY-011) — refs resolve.

**What the next run should do.** SY-005 — first interleaved coherence
pass over Intro + Model + Results §4.1–§4.2 (4 sections integrated, a
pass is due per mission §4.1): notation vs `\newcommand` block,
duplicated definitions, dangling `\ref`, intro previews vs body
strength, figure/caption consistency, and the known overfull `\hbox` in
Model §2.4; re-sweep the firewall. Then SY-006 (Results §4.4, C3).

## SY-015 — De-meta scrub (firewall enforcement, first task under prompt v0.2)
- **run_id:** F2C7A9E1-3D04-4B86-9A1F-7E52C0B8D34A
- **prompt_version:** 0.2
- **ended:** 2026-05-30T23:59:00Z
- **task worked:** SY-015 (mandated first task under v0.2 — mission §4.1, §5.6)
- **output kind:** scrub
- **section touched:** all (`main.tex`, `sections/*.tex`, `refs.bib`)

**Headline thing done.** Purged the v0.1 "reconstruction" framing from the
entire manuscript so it reads as original, standalone work. 38 firewall
violations removed across every file: stripped meta comment headers from
`model.tex`, `results.tex`, `discussion.tex`, `methods.tex`,
`appendix.tex`, and `refs.bib`; rewrote all "inherited paper / the
original / our reconstruction / as published" prose into positive,
self-standing statements; converted comparison-hedges ("rather than
asserting…", "categorical floor", "we sharpen") into direct claims;
removed every `Rebuild/`·`Critique/`·`research_db/` path, the `sha256`
hash, and all `SY-`/`rb-`/`RB-`/`CR-` ids from prose, table/figure
captions, and bib comments; collapsed the styled title subtitle; retitled
"Appendix" → "Supplementary derivations and extensions"; made the GAP
G-001 placeholder terse (detail stays in `GAP_REQUESTS.md`).

**Grounding summary.** Content-preserving: no assertion, number, equation,
or figure changed. Strength unchanged — the distributional/graded/
conditional character of the four findings is intact, now stated as what
the model does rather than against an absent statement.

**Firewall sweep result.** Final grep over `main.tex`, all
`sections/*.tex`, and `refs.bib` for the full banned-vocabulary set
returns **zero hits**. `firewall_clean` flipped to **true** in
`synthesizer_state.json` (schema bumped to v2).

**Compile result.** `pdflatex ×2 + bibtex` (+ third pass), all exit 0,
**10 pages**, 0 undefined references, 0 undefined citations, 0 bibtex
warnings.

**Gaps.** G-001 still open (attention-to-d′ mapping figure); none opened
or closed.

**What the next run should do.** SY-004 — Results §4.2–4.3 (asymmetry
shapes allocation; VDA non-monotonic in r, closed-form r†(v)). Place
`vda_curves_vfamily` and `r_dagger_vs_v` once staged. Write in clean venue
voice from the outset. Run the SY-005 coherence pass (re-sweeping the
firewall) after §4.2–4.3 land.

---

## SY-003 — Results §4.1 integration (criterion typically dominates, C1)
- **run_id:** D8A3F1C2-6B47-4E92-A5D0-1C9E7B3F4A86
- **prompt_version:** 0.1
- **ended:** 2026-05-30T23:35:00Z
- **task worked:** SY-003 (first Results finding; default next increment in arc order)
- **output kind:** section
- **section touched:** `sections/results.tex`

**Headline thing assembled.** Opened the Results section: a four-finding
orienting paragraph (the developing argument) + reconstructed the
original's §4.1 *"Criterion Adjustment Dominates Value Encoding"*
(`sec:results-criterion`, finding C1) as a **distributional** result.
The criterion fraction $\CF$ (defined once in the Model, Eq.
`eq:cf-def` — referenced, not redefined) is reported as a distribution
across the $4{,}410$-cell sweep: median $0.7552$ (variant~A) / $0.7682$
(variant~B), concentrated $[0.30, 1.00]$, with the regime structure
(quadrant breakdown) showing the criterion lever dominant in the
cost-dominant corner (median $\ge 0.90$) and ceding to attention in the
benefit-dominant, low-validity corner (variant~B median $0.51$, min
$0.30$). Two tables (CF distribution, quadrant breakdown), three figures
(`cf_histogram`, `cf_heatmap`, `cf_curves`) copied from the C1 sim and
placed. The $\corr$ sensitivity and the conservation-family band are
reported in prose.

**Corrections made (original → reconstruction), auditable.**
- §4.1 "$\CF$ ranges from $60\%$ to $96\%$ across all $(r,V,v)$" →
  "median $\approx 0.76$, concentrated $[0.30,1.00]$; categorical
  $[0.60,0.96]$ retracted at both ends (min $0.5587$ A / $0.3040$ B;
  max $1.00$)".
- §4.1 "criterion adjustment is *always* the single largest contributor"
  → "*typically* the dominant lever; cedes the lead in the
  benefit-dominant low-validity corner (var-B median $0.51$, min
  $0.30$)".
- §5.5 (folded in along the CF axis) "independent noise is an upper
  bound on the VDA benefit" → "independence upper-bounds the *criterion
  fraction*, variant~A only (one-sided, $84\%$ of cells); variant~B is
  mixed ($64\%$ dec / $24\%$ inc)".

**Provenance summary.** Every claim traced in `TRACE.md` (rows R0–R8).
Structure/framing → ORIG §4.1. Distribution + quadrant numbers →
LEDGER:C1 + `SIM:C1--cf-distribution` (sha256 `91fc4692…`). $\corr$
sensitivity → LEDGER:C1, LEDGER:A1 + the same sim at $\corr=0.2$.
Conservation band → LEDGER:C1 + `SIM:A3--conservation-band` (sha256
`055bf4ec…`). Citations (`CohenMaunsell2009`, `MullerFindlay1987`)
resolve in `refs.bib`.

**Strength check.** C1 stated only as a distribution / central tendency;
the median carries the "criterion typically dominates" reading and the
categorical floor is retracted at both ends. The §5.5 retraction is held
at LEDGER:A1 strength (CF, not VDA; variant~B a sensitivity, not a
uniform claim). No assertion exceeds its ledger row.

**Compile.** `pdflatex`×2 + `bibtex` + `pdflatex`: clean. **11 pages**
(was 7), 0 undefined references, 0 multiply-defined labels, 0 citation
warnings. One pre-existing overfull `\hbox` (~52pt) in Model §2.4
(unrelated to this increment) flagged for the SY-005 coherence pass.

**Gaps opened/closed.** None opened, none closed. The original's Figure 2
(reward-decomposition bar chart) is **not** reconstructed — no rebuilder
artifact regenerates it, and the rebuild deliberately supersedes it with
the distributional `cf_histogram`; the decomposition it depicts is
already typeset in the Model (Eqs. eq:gain-criterion/eq:gain-validity/
eq:vda-def). Logged as a supersession in `TRACE.md`, **not** a gap.

**Drift watch.** Did not re-open `Critique/verdicts/` this run; the C1
and A1 rows of `CLAIM_LEDGER.md` record no label drift as of rb-047
(C1 CONTESTED, A1 CONTESTED) and §4.1 states both inside the ceiling.
No action.

**What the next run should do.** SY-004 — Results 4.2–4.3 (asymmetry
shapes allocation + C2 VDA non-monotonic in $\Rsens$): re-flow the
closed-form escape threshold $\rdagger(\val)$, the peak-vs-threshold
confirmation, and the $\val$-family. Place `vda_curves_vfamily` and
`r_dagger_vs_v`. Fold in the carried-over VDA-side of the §5.5
retraction (the $\val$-dependent sign-flip of $\partial\VDA^\star/
\partial\corr$, `tab:rho-sensitivity`) at LEDGER:A1/C2 strength. Do not
redefine $\CF$ or the $\corr$ recovery contract (already in the Model).

---

## SY-002 — Model integration (original §2.1–2.5 + three-lever decomposition)
- **run_id:** B1F4A2E7-3C8D-4E55-9A21-7F0C6D9E8A14
- **prompt_version:** 0.1
- **ended:** 2026-05-30T22:40:00Z
- **task worked:** SY-002 (Model integration; default next increment in arc order)
- **output kind:** section
- **section touched:** `sections/model.tex`

**Headline thing assembled.** Re-flowed the rebuilder's claim-organised
`Rebuild/manuscript/sections/model.tex` (rb-009) into the original's §2
arc: **2.1 Task Structure** (N locations, value/validity cue, per-location
SDT marginals), **2.2 Attention Allocation**, **2.3 Attention-to-Perception
Mapping** (transfer $f$, four $h$-forms, the $\benefit/\cost$ asymmetry
ratio, the $\dprime_c/\dprime_u$ map), **2.4 Reward Structure + the
decorrelation channel** (variants A/B, expected-reward Eq.~9, the locus of
A1 at $\PnoFA$, the equicorrelation covariance, the boxed exact 1-D
integral $\PnoFA(\corr)$, the $\corr{=}0$ recovery contract), and **2.5
Policy Decomposition** (P1–P4, the criterion/validity-attention/VDA gain
split, the CF definition, and Definition~\ref{def:three-levers} naming the
three levers — criterion, sensitivity, decorrelation). The decorrelation
lever (LEDGER:A1) is woven into 2.4/2.5 as a *model parameter* with a
floating-point recovery contract, not as a result.

**Re-narrativisation decision (logged per §4.1 override discipline).**
The rebuilder's `model.tex` devotes its second half (`sec:model-upper-bound`)
to the §5.5 "upper bound on VDA" retraction, the cell-wise sign-flip
$\Delta\VDA$ distribution (Table `tab:a1cw-summary`), and four A1 sign-flip
figures. Under the reconciliation rule **"the original wins on structure"**,
that material is *empirical Results/Discussion* content (the original makes
no such claim in §2), so it is **deferred**, not placed in the Model: the
CF($\corr$) channel → Results-C1 (SY-003), the $\partial\VDA/\partial\corr$
sign-flip → Results-C2/C3 (SY-004/006), the §5.5 retraction itself →
Discussion (SY-008). M14 *names* the upper-bound question as open and routes
it forward; it does not assert or pre-rebut it. Carry-in note added to SY-003.

**Provenance summary.** Every claim traced in `TRACE.md` (rows M1–M14).
Machinery/framing → ORIG §2.1–2.5 + RB:model.tex (equations lifted
verbatim). Decorrelation channel → LEDGER:A1 + RB:model.tex
(`eq:pnofa-rho`, `eq:rho-zero-recovery`, `def:three-levers`) +
DERIV:A1--rho-channel.md + `model/core.py` + `test_recovery.py`. All
citations (MullerFindlay1987, posner1980, reynolds_heeger2009,
treue…1999, mcadams…1999, CohenMaunsell2009, RuffCohen2016, Srinath2021,
Slepian1962) resolve in `refs.bib`.

**Strength check.** CF is *defined* (Eq.~cf-def) with its distribution
explicitly deferred to Results — the retracted "$[0.60,0.96]$" floor does
not appear. The §5.5 upper-bound claim is named but not asserted (M14). The
$\corr$ lever is stated at LEDGER:A1 strength (a parameter + recovery
contract), not as a finding. No assertion exceeds its ledger row.

**Compile.** `pdflatex`×2 + `bibtex` + `pdflatex`: clean. **7 pages**
(was 3 after intro), 0 undefined references, 0 rerun requests, 0
non-hyperref warnings.

**Gaps opened/closed.** Opened **G-001** (original Figure 1, the
attention-to-$\dprime$ mapping — no regenerated artifact under `Rebuild/`;
owner→rebuilder; non-blocking, red placeholder in §2.3). Closed: none.

**Drift watch.** Did not re-open `Critique/verdicts/` this run; the A1 row
of `CLAIM_LEDGER.md` records no label drift as of rb-047 and the Model
states A1 only at its model-parameter / recovery-contract strength, well
inside the ledger ceiling. No action.

**What the next run should do.** SY-003 — Results 4.1 (C1, criterion
typically dominant): re-flow the CF distribution (median ≈0.76,
concentrated $[0.30,1.00]$, frac<0.6) at distributional strength only (no
floor), with the contested high-$r$ corner and the $\corr$ sensitivity;
fold in the carried-over A1 CF($\corr$) channel (cf_vs_rho; CF monotone-down
in 84% var-A / 64% var-B cells). Place cf_histogram / cf_heatmap / cf_curves
and the original's Figure 2 (reward decomposition) if a rebuilder artifact
exists (else gap).

---

## SY-001 — Bootstrap + Introduction integration
- **run_id:** C75C3D90-5EE2-47E7-A40A-994E7EE9ED0D
- **prompt_version:** 0.1
- **ended:** 2026-05-30T21:12:00Z
- **task worked:** SY-001 (bootstrap, then the default first increment = Introduction)
- **output kind:** section (+ workspace bootstrap)
- **section touched:** `sections/intro.tex`

**Headline thing assembled.** Bootstrapped the `Reconstruction/`
workspace (mission §9.8): created the skeleton, copied the rebuilder's
LaTeX preamble + `\newcommand` notation block verbatim into
`manuscript/main.tex`, laid out all section files in the original's arc
order as compiling placeholders, copied `refs.bib`, and seeded
`README.md`, `TRACE.md`, `GAP_REQUESTS.md`, `SYNTH_BACKLOG.md` (14
tasks), and `synthesizer_state.json`. Then executed the **Introduction
integration**: reconstructed the original's §1 at ledger strength —
restating the two-mechanism framing (criterion / VDA) and the
asymmetry-ratio motivation, folding in the **decorrelation ($\corr$)
lever** as the third mechanism (LEDGER A1; forward-ref to the Model's
three-lever definition), and previewing the four findings at
distributional / confirmed / graded / conditional strength.

**Provenance summary.** Every claim traced in `TRACE.md` (rows
I1--I11). Framing claims -> ORIG §1. Third-lever claim -> LEDGER:A1 +
RB:model.tex. Finding previews -> LEDGER:C1--C4 + the four C-sims.
Citations all resolve to `refs.bib`.

**Strength corrections made (original -> reconstruction):**
- C1: "criterion captures 60--96%" -> "median CF $\approx0.76$,
  concentrated $[0.30,1.00]$; central tendency with a tail, not a
  floor; $\corr>0$ shifts mass toward attention."
- C3: "VDA confined to a narrow regime ... criterion alone is
  sufficient" -> "concentrated in a graded regime ... mapped as a
  contour band; outside it, the optimal-criterion observer loses little
  treating attention as value-blind."
- C4: "inverted attention is never optimal" -> "not optimal under
  predictive cues, conditional on $\valid\ge1/\Nloc$; anti-cue
  inversion ($\valid<1/\Nloc$) is a new falsifiable prediction."
- Two-mechanism premise -> three-lever decomposition; the original's
  "two ways" is the $\corr=0$ special case.

**Compile.** `pdflatex`×2 + `bibtex` + `pdflatex` (4 steps): clean.
**3 pages**, 0 undefined references, 0 non-hyperref warnings. (One
citation key typo `reynolds_heeger2009` caught and fixed to
`reynolds_heeger2009_normalization` before the clean build.)

**Gaps opened/closed.** None. The Introduction is fully traceable.

**Drift watch.** Did not re-open verdicts this run (intro is a framing
restatement). The ledger's own header notes no label drift as of rb-047
(10/10 labels match; only the §3 A6 entry is stale, already flagged in
the ledger). No action.

**What the next run should do.** SY-002 — Model integration: re-flow
`Rebuild/manuscript/sections/model.tex` into the original's §2 arc
(2.1--2.5), weaving the $\corr$ lever into §2.3 and stating the
three-lever Definition the Introduction forward-references; place
Figure 1 (attention$\to\dprime$ mapping); copy the figures it needs.
Watch notation against the copied `\newcommand` block.
