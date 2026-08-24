---
type: conversation
agent: constructive-rebuilder
prompt_version: "0.2"
run_id: rb-048-2026-05-30
started: 2026-05-30T14:30:00Z
ended: 2026-05-30T14:55:00Z
worked_on: RB-048
output_kind: manuscript
claims_touched:
  - cross-cutting
  - A1
  - A2
  - A3
  - A4
  - A5
  - A6
  - A7
  - A8
  - C1
  - C2
  - C3
  - C4
  - C5
artifacts_written:
  - Rebuild/manuscript/sections/limitations.tex
  - Rebuild/manuscript/main.pdf
papers_added: []
spawned_tasks: []
---

# Conversation — §limitations bookend (RB-048)

## What I built

Replaced the rb-005 stub at `Rebuild/manuscript/sections/limitations.tex`
(34 lines, ~70% placeholder) with a 6-subsection bookend
(~170 LaTeX lines, ~1,400 words) at the §3.3 unifying-reframe voice.
Mirrors the rb-047 abstract's distributional/graded/conditional voice,
organised by lever rather than by paper section so a reader can locate
the precise conditional under which any headline number applies.

Subsections:

1. **§7.1 The conservation rule is a parameter, not a derivation**
   (A3, CONTESTED). Names the power-mean parameter $p$, the central-
   tendency robustness of $\CF$ under $p \to 0$, the tail doubling
   ($\mathrm{frac}_{<0.5}$ at $p=1$ vs $p=0$), and the open closed-
   form conjecture $|\partial_p R_{\mathrm{P4}}| \le |\partial_p R_{\mathrm{P1}}|$
   that would promote `thm:delta-cf-monotone` from empirical to
   analytic. Names the deferred joint $(p, \corr > 0)$ band.

2. **§7.2 Heterogeneity is bounded, not abolished**
   (A2 + A8, CONFIRMED-CONDITIONAL). A2 between-preparation reading,
   with the empirical $\le 1{\times}10^{-5}$ invariance of the $C_2$
   peak under $\le 30\%$ linear spread, and the deferred closed-form
   $\Delta R = O(\mathrm{Var}(\boldsymbol{r}))$ perturbation
   expansion. A8 new conditional ($\Delta R = +2.79{\times}10^{-3} \to
   +3.68{\times}10^{-3}$ under $(\corr, p)$) with the Slepian-style
   A8-binding-onset closed form named as not derived.

3. **§7.3 The decision-noise lever is deferred, not denied**
   (A6, WEAKLY-SUPPORTED). Explicit hold at the live verdict label
   per mission §3.2; the would-be fourth-lever framing made
   explicit by symmetry with the $\corr$ channel.

4. **§7.4 Assumptions retained as explicit scope** — A4 (no
   learning), A5 (transfer-function family $h \in \{a, \sqrt{a},
   a^{0.3}, a^{2}\}$), A7 (reward variants A vs B). Each named with
   the live-ledger justification that the reviewer has not attacked
   them, and the scope-boundary statement of what they exclude.

5. **§7.5 Equicorrelation, $\corr$-envelope, and queued follow-ups** —
   equicorrelation specificity (structured covariances of
   RuffCohen2016/Srinath2021 out of scope), $\corr \in \{0, 0.1,
   0.2, 0.3, 0.4\}$ tested with central anchor $\corr = 0.2$ from
   CohenMaunsell2009, variant-B caveats (all 9 queued variant-B
   replication sims named), grid-sharpening (8 queued grid-pin
   sims/derivations named — RB-024, RB-028, RB-029, RB-032, RB-039,
   RB-040, RB-044, plus the Slepian-style analytic locus).

6. **§7.6 What the rebuild does not claim** — no neural-implementation
   claim; no empirical-$\corr$ prediction beyond the
   CohenMaunsell anchor; no observer-deviation prediction; no
   attention-dynamics claim. Explicit non-claims paragraph matching
   mission §3.3 voice that the rebuilt paper is a "mathematical
   description" — not a biological or empirical-fit program.

## How it connects to the ledger

This is a cross-cutting bookend increment. No claim's rebuilt
strength changes; the §limitations section consolidates the scope
deferrals scattered across §results-c1..c4 / §extensions-a2..a8 /
§model-rho-channel / §model-upper-bound / §appendix-deriv-c2 /
§appendix-deriv-a3 into a single navigable Section~7.

CLAIM_LEDGER row updates: the reconciliation paragraph at line 12
of `CLAIM_LEDGER.md` was advanced from "rb-047" to "rb-048" with
a full reconcile entry (~6 sentences) recording the 25-label
cross-reference inventory, the 3-pass build outcome, the +3-page /
+14,755-byte PDF delta, and the explicit statement that 10/10
live verdict labels still match the §3 table (only the §3 A6
entry remains stale, already flagged below — gating intact).

The §3 A6 row in `agents/paper_rebuilder_prompt.md` v0.2 says A6
is "OPEN/in-progress at authoring (reviewer run-018)"; the live
label is `WEAKLY-SUPPORTED`. The drift is benign: the live label
gates RB-016 / RB-020 (model + sim for the attention-coupled
decision-noise lever) which remain blocked, matching the
prompt's "kept gated until verdict label moves past
WEAKLY-SUPPORTED" stub anticipation. §7.3 of the new limitations
section restates this gating explicitly.

## Simulation evidence

None — this is a manuscript-bookend increment with no new sim,
no new derivation, no new bib entry. The simulation evidence the
section *cites* is inherited from prior runs (rb-001 through
rb-046); the deterministic output hashes named in the abstract
(rb-047) are not restated in §limitations because §limitations
is about scope, not headline numbers.

Build verification (the increment's own evidence): 3-pass
pdflatex clean. Pass 1 produced one undefined forward reference
on `sec:limitations-followups` (label is later in the same file,
at §7.5); pass 2 resolved it; pass 3 was byte-identical to pass
2, settled. Final PDF 58 pages / 2,807,597 bytes (vs rb-047
baseline 55 / 2,792,842 = +3 pages, +14,755 bytes).

## What the manuscript can now say

The rebuilt paper has **both bookends drafted** for the first
time. The cover-to-cover structure is now:

- abstract (rb-047) → intro stub → model (rb-009) → results × 4
  (rb-006, rb-007, rb-010, rb-013) → extensions × 3 (rb-017,
  rb-022, rb-028) → **§limitations (rb-048)** → methods stub →
  appendix × 3 (rb-018, rb-024, rb-046)

Two skeleton stubs remain (intro, methods). Every §scope paragraph
scattered across body sections is now collected into §limitations,
so a later increment that tightens any scope statement updates
§limitations in one place rather than re-stating the scope inline
in two sections.

## Next increment

**§intro bookend** — replace the rb-005 stub in
`Rebuild/manuscript/sections/intro.tex` with the third bookend.
Natural rhythm-matching follow-up to the §abstract + §limitations
pair; the §limitations §7.6 'what the rebuild does not claim'
paragraph and the abstract's three-lever framing together set up
the §intro voice (the §intro should enter from the literature
side — Müller-Findlay sensitivity-vs-criterion vocabulary,
Cohen-Maunsell decorrelation, Wang-Theeuwes statistical-learning
suppression — and motivate the three-lever reframe as the
quantitative answer to "when does VDA matter?").

Alternatives in priority order: §methods bookend (replace the
rb-005 stub with a catalogue of `Rebuild/model/`, `Rebuild/sims/`,
recovery contracts, deterministic hashes); RB-024 (C1 closed-form
$\CF < 0.5$ boundary derivation — would let §results-C1 replace
`frac<0.6 = 22\%` with a closed-form predicate); RB-029 (A1
dormant-cell amplification closeup — the most striking single
qualitative finding of rb-010 deserves a clean falsifiable
prediction); RB-040 (Slepian-gradient analytic locus for the cell-
wise $\partial \VDA / \partial \corr$ surface — promotes rb-025
empirical observation to an analytic statement).

## Wiki cross-references

Sweep performed against `research_db/papers/`. Keywords used:
{scope, limitations, conservation form, heterogeneity, decision-
noise lever, learning dynamics, transfer function, reward
convention, equicorrelation, structured covariance, variant B
sensitivity, grid sharpening, dormant-cell amplification, neural
implementation, attention dynamics}.

Every paper the §limitations section cites was already wired
through earlier body sections:
- `mcadams_maunsell1999_v4_tuning` — wired at rb-022 (§extensions-a2).
- `reynolds_heeger2009_normalization` — wired at rb-022.
- `carrasco2011_visual_attention_25y` — wired at rb-022.
- `RuffCohen2016` — wired at rb-009 (§model).
- `Srinath2021` — wired at rb-009.
- `CohenMaunsell2009` — wired at rb-009 (and many later).

0 new `research_db/papers/` stubs added. `audit.py` not re-run
(no wiki writes). No proposed edits to wiki HANDOFF / SCHEMA /
TAXONOMY / INDEX / README / concepts / threads / existing papers
to surface in this run.
