---
type: meta
status: stable
created: 2026-05-30
tags:
  - meta/conventions
  - meta/writing
---

# Layered disclosure — global writing SOP

> Adapted from the Palladio wiki's `LAYERED_DISCLOSURE.md` for this
> neuro-AI literature + research-findings corpus. The principle is
> identical; the jargon examples are ours.

## TL;DR

Every substantive page opens with a plain-language summary a non-specialist
can follow. Specialized terms — neuroscience jargon, architecture shorthand,
mathematical notation — are introduced **only after** they are defined inline
or wikilinked to a definition. A reader who knows nothing about the page's
topic must be able to learn from the page without external context. *This
applies to every page an agent writes.*

## Why

This wiki is read by people coming from different specialties (systems
neuroscience, deep learning, RL), by autonomous agents that have not seen the
conversation that produced a page, and eventually by collaborators with no
context on this research program. A page that opens with "the SIP residual
restored the update gate after the run-5 collapse" before defining any of
those terms is useful to maybe two people. That is a failure of the wiki, not
a tolerable cost of precision.

## The three layers

Every page with substantive content (`concept`, `paper`, `thread`, `brief`,
`note`, `conversation`) is structured as three independently-readable layers.

| Layer | Section name(s) | Audience assumption | Length |
|---|---|---|---|
| **L1** | `## TL;DR` | None. No domain context, no jargon, no prior pages. | 2–4 sentences. |
| **L2** | `## Plain explanation` / `## Why this matters` / `## Background` | None at start; introduces and defines every term it uses, inline. | 1–3 paragraphs. |
| **L3** | `## Mechanism` / `## Definition` / `## Methods` / `## Results` / `## Key claims` | Reader has read L1+L2. May use defined terms freely; may carry equations, code, dense tables. | As long as needed. |

L1 is **mandatory** on every page that is not a one-line stub. L2 is mandatory
for `concept`, `paper`, `thread`, `brief`, and `conversation`. L3 is optional
and appears only when there is real depth.

The layers are **independent reads**, not one argument chopped into sections. A
reader with 20 seconds reads L1 and leaves with the headline; 2 minutes reads
L1+L2 and understands the idea; the one doing the work reads all three.

## Jargon rules

A specialized term must be introduced one of three ways at **first use, on
every page** (a term defined on `[[predictive_coding]]` is *not* defined on
`[[hierarchical_predictive_coding]]` — each page stands alone):

1. **Inline**, in a parenthetical or short clause:
   > *Predictive coding* (the hypothesis that cortex continually predicts its
   > own inputs and propagates only the prediction error) underlies the model.
2. **Wikilinked** to a concept page that defines it:
   > The decoder is trained with a [[distributional_rl]] objective.
3. **Footnote-glossed** when an inline definition would derail the sentence and
   no concept page exists yet.

Mathematical notation counts as jargon. A loss term or gating equation needs an
English gloss the first time it appears, even when the equation is the whole
point of the page. Math in the first paragraph of L1 is a write failure.

Concretely for this corpus:
- **Avoid in L1**: bare acronyms (MCLSTM, SIP, PAC, PER, MPO, VWM, FEP, ViT),
  run labels ("run-5 collapse"), Greek-letter loss terms, internal config names.
- **Prefer**: "a memory-augmented recurrent network", "the surgical fix to the
  positional embedding", "the prioritized replay buffer", "working memory".
- **Acceptable in L1 only with an inline gloss**: *predictive coding* (defined
  in one clause as above).

## Per-page-type templates

### `concept`
```markdown
# <term>

## TL;DR
<two sentences: what it is, why it matters here>

## Plain explanation
<one paragraph: what it is, what it isn't, how it relates to nearest concepts —
every specialized term defined inline or wikilinked>

## Definition / Mechanism
<formal definition, notation, variants, validity regime — free to use L2 terms>
```

### `paper`
The existing eight-section card (`## 1. Abstract` … `## 8. Citations to
follow`) already is a strong L3. Layered disclosure adds **one** thing: a
`## TL;DR` (2–4 sentences, plain language) **above** `## 1. Abstract`, so the
card can be skimmed and so `find_pages_by_description` has a description to
seed on. The TL;DR is the one-look "why this paper is in the database" — it is
not the abstract reworded.

### `note` (a finding about our own work)
L1 + L2 mandatory; L3 is the reproducible-findings body (see
[`REPRODUCIBLE_FINDINGS.md`](REPRODUCIBLE_FINDINGS.md)).
```markdown
# <title>

## TL;DR
<two sentences: what this note shows>

## Plain explanation
<one paragraph: the question, the method, the result — plain, terms defined>

## Research goal
## Method
## Finding
## Evidence
## Reproduction
## Caveats
```

### `thread`, `brief`, `conversation`
Each opens with `## TL;DR` then `## Plain explanation`/`## Plain summary`, then
its detailed body (chronological log for threads; Finding · Mechanism · Frame ·
Action for briefs; the full exchange for conversations).

## What this SOP does **not** require

- It does not dumb down L3 — the technical layer may be dense and mathematical.
- It does not eliminate jargon — it requires *introducing* it.
- It does not require rewriting old pages at once. New writes follow the SOP;
  existing pages (notably the 260 paper cards, which currently have **no
  TL;DR**) are backfilled opportunistically, highest-inbound-link pages first
  (`wiki_stats` surfaces them).

## Self-check before `write_page`
1. Does the page open with a `## TL;DR` of 2–4 sentences?
2. Is every specialized term in L1 glossed inline, wikilinked, or absent?
3. Does L2 exist for substantive types and define every term it uses?
4. Is math absent from L1 and glossed in English before use in L3?

If any answer is no, revise before writing. The check is a precondition of the
write, not a cleanup afterward. It composes with the
[`REPRODUCIBLE_FINDINGS.md`](REPRODUCIBLE_FINDINGS.md) check — both must pass.
