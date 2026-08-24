# Reconstruction/ — the assembled VDA paper

This workspace holds **one** deliverable: a single, coherent
reconstruction of the Herman Lab 2026-04-09 manuscript *"When Does
Value-Directed Attention Matter? A Normative Model with Independent
Attentional Benefit and Cost"* (`Critique/source/main.pdf`), with the
rebuilder's repairs folded in.

It is produced by the **VDA Paper-Synthesizer agent**
(`agents/paper_synthesizer_prompt.md`), the third member of the paper
family:

| Agent | Posture | Workspace |
|---|---|---|
| Skeptical-Reviewer | try to falsify | `Critique/` |
| Paper-Rebuilder | repair each claim | `Rebuild/` |
| **Paper-Synthesizer** | **assemble into one paper** | `Reconstruction/` |

## What this is (and is not)
- **Assemble-only.** Every scientific assertion traces to an existing
  artifact (the original's framing, a `Rebuild/CLAIM_LEDGER.md` row, a
  sim, a derivation, a rebuilder draft, or a citation). Nothing is
  invented. See `TRACE.md`.
- **Ledger-bound.** `Rebuild/CLAIM_LEDGER.md` is the ceiling on how
  strongly any claim is stated. The original's categorical wording
  ("60--96%", "negligible regardless", "never") is actively corrected
  to its distributional / graded / conditional form.
- **Structure-faithful, re-narrativised.** The paper follows the
  *original's* argument arc, not the rebuilder's claim-by-claim
  (C1--C5 / A1--A8) layout. No claim ids appear in the manuscript; the
  artifact trail lives in `TRACE.md` and the conversation pages.
- Everything outside `Reconstruction/` is **read-only**. This agent
  adds nothing to `research_db/`.

## Reading order
1. `manuscript/main.tex` -> the paper (`pdflatex` per `manuscript/BUILD.md`).
2. `TRACE.md` -> section-to-artifact provenance.
3. `GAP_REQUESTS.md` -> the rebuilder-directed punch list of missing
   artifacts (owner-mediated hand-off).
4. `SYNTHESIS_LOG.md` -> chronological run record.
5. `SYNTH_BACKLOG.md` -> queued integration / coherence tasks.

## Manuscript arc (section file order)
`abstract` -> `intro` -> `model` -> `results` -> `discussion` ->
`methods` -> `appendix`.

Note: the original places **Methods at §3** (before Results). This
reconstruction places Methods and the appendix at the **end** of the
arc, per the synthesizer mission's stated order (§2.1, §6). This is a
deliberate editorial choice; the scientific content of Methods is
unchanged.

## Status (as of SY-003, 2026-05-30)
- Skeleton created; preamble/notation copied from the rebuilder.
- **Introduction** integrated at ledger strength (three-lever framing;
  four-finding preview corrected from the original's categorical claims).
- **Model** integrated (original §2.1–2.5 + the three-lever
  decomposition; the $\corr$ decorrelation lever woven in).
- **Results §4.1** integrated (the original's "Criterion Adjustment
  Dominates" finding, C1) as a *distributional* result — the categorical
  $[0.60,0.96]$ floor and "always the single largest contributor"
  corrected to a central tendency with a tail.
- Compiles clean, **11 pages**. Next: Results 4.2–4.3 (C2, VDA
  non-monotonic in $\Rsens$; SY-004).
- **1 open gap** (G-001: the original's Figure 1, attention-to-$d'$
  mapping — no rebuilder artifact; non-blocking placeholder in §2.3).

The milestone this agent exists to reach is **"draft complete"**: every
section integrated at ledger strength, every figure placed, the abstract
written from the finished body, zero open gaps, clean compile.
