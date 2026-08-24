---
type: meta
status: stable
created: 2026-05-30
tags:
  - meta/conventions
  - meta/methodology
---

# Reproducible findings — global methodological SOP

> Adapted from the Palladio wiki's `REPRODUCIBLE_FINDINGS.md`. In Palladio the
> "data" behind a finding is a parquet warehouse; **here it is the research
> program's own code and run artifacts** — `RViT_plus/`, `Prism/`, `PrismV2/`,
> `HRA/`, `Rebuild/`, their run directories and logs, `MODEL_DESIGN.md`,
> `RVIT_PLUS_DESIGN.md`, and the design PDFs. A finding must be redoable from
> the page plus that local code.

## TL;DR

When work surfaces a finding worth keeping — an ablation result, a fixed
failure mode, a confirmed baseline, a synthesis across papers — the agent does
not just record the result. It captures six dimensions (research goal · method
· finding · evidence · reproduction · caveats) so a reader six months from now
can reproduce it from the page alone. A finding page without method and
reproduction is not a finding; it is a rumour, and the wiki does not store
rumours.

## Scope

This SOP governs *what content* a finding page must carry. It composes with
[`LAYERED_DISCLOSURE.md`](LAYERED_DISCLOSURE.md) (*how* the page is presented)
and [`EDGES.md`](EDGES.md) (*how* its cross-links are typed).

It applies to:

| Page type | Applies? | Notes |
|---|---|---|
| `note` (finding / investigation stub) | **Yes** | This is the SOP's home — the agent write-target. |
| `brief` (synthesis) | **Yes** | Map the Finding · Mechanism · Frame · Action house style onto the six sections. |
| `conversation` (answer involved new analysis) | **Yes** | The answer body carries the six dimensions; `crystallized:` lists the notes/concepts spawned. |
| `thread` (engineering log) | **Partial** | Each dated run entry should state method + result + the run id/path; the thread as a whole is a chronology, not a single finding. |
| `paper` (external card) | No | The card summarizes someone else's work; §4 Methods / §5 Results / §6 Critique already serve this role. |
| `concept` | No | Concepts define terms, they do not assert findings. |
| `moc`, `meta`, `sop`, `person` | No | None record empirical findings. |

Test: *if the page asserts something is true about our model or the world (vs.
defining a term or summarizing someone else's paper), it is a finding page.*

## The six dimensions

In this order, after the L1+L2 layered-disclosure opener:

| # | Section | What goes here |
|---|---|---|
| 1 | `## Research goal` | The question and *why* — the design decision, prior run, or gap that prompted it. One short paragraph. |
| 2 | `## Method` | What was actually done. Code paths (`RViT_plus/...`), the config/branch/commit, the task or dataset (e.g. Posner change-detection), the steps. Specific enough to rerun. |
| 3 | `## Finding` | The headline result in one paragraph — the quantitative version (the plain version is in L1/L2). |
| 4 | `## Evidence` | The numbers/curves/examples: metric values (`correct`, `return`), seeds, step counts, where the logs/plots live (run id, `docs/*.pdf`, output dir). |
| 5 | `## Reproduction` | The minimum recipe: script + exact flags, config file, commit hash, expected runtime/hardware. "Run `python -m RViT_plus.train --config X` from commit `abc123`; ~N hours on one GPU." |
| 6 | `## Caveats` | Real limitations: single-seed, narrow regime, confounds, what it does *not* establish, where it was hedged. The page surfaces its own weaknesses. |

Close with a citations block:
```markdown
## Citations
- [[concept-or-paper-slug]] — what it supplies
- [[earlier-finding-slug]] — what this extends or refutes
```

## The "evidence missing" pattern

When a candidate finding is real but evidence is not yet collected, the SOP
does **not** allow recording it as stable — it requires an explicit stub:

```markdown
---
type: note
status: stub
created: 2026-05-30
tags: [topic/...]
summary: "Hypothesis only — evidence not yet captured."
---

# <Title>

## TL;DR
*Unverified hypothesis.* <two sentences stating the candidate finding>

## Research goal
<the question>

## Method
*Not yet executed.* <the planned method>

## Finding
*Hypothesis.* <the candidate result>

## Evidence
*Not yet collected.* Surfaced in [[<conversation-slug>]] without supporting runs.

## Reproduction
<the recipe someone would follow to test it>

## Caveats
This is a stub; the hypothesis is unsupported and must not be cited as fact
from other pages until evidence lands.
```

The honesty is the point: `status: stub`, *Hypothesis* in the TL;DR, and *Not
yet collected.* in Evidence tell a future reader exactly what they are seeing.

## Promotion gate

A `Notes/` finding is promoted toward `concept`/`brief` under the
crystallization rule (two independent inbound citations). This SOP adds one
gate: **Method, Evidence, and Reproduction must be non-empty (not stub
markers) at promotion time.** Inbound citations do not paper over missing
methodology.

## Self-check before `write_page`
1. Is there a `## Research goal` naming a specific question?
2. Does `## Method` name specific code paths, configs, or steps?
3. Does `## Evidence` carry concrete numbers or pointers to artifacts?
4. Could someone follow `## Reproduction`?
5. Does `## Caveats` surface real limitations (not boilerplate)?
6. If any of 1–4 is empty, is the page explicitly a `status: stub` with
   `*Hypothesis*` / `*Not yet collected.*` markers?

If any of 1–5 is no **and** 6 is also no, the page is not ready. Do not
silently write a partial finding.
