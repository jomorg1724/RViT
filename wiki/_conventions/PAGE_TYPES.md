---
type: meta
status: stable
created: 2026-05-30
tags:
  - meta/conventions
---

# Page types — when to use which

> Adapted from the Palladio wiki's `PAGE_TYPES.md` for this neuro-AI corpus.
> Two types are local specialties Palladio lacks: **`paper`** (the rich
> external research card) and **`thread`** (the narrative engineering log).

> All substantive pages follow **layered disclosure**
> ([`LAYERED_DISCLOSURE.md`](LAYERED_DISCLOSURE.md)): a `## TL;DR` opener, a
> `## Plain explanation`, then technical sections. Pages that assert empirical
> findings (`note`, `brief`, and `conversation` answers involving new analysis)
> additionally follow **reproducible findings**
> ([`REPRODUCIBLE_FINDINGS.md`](REPRODUCIBLE_FINDINGS.md)).

The vault distinguishes types across three layers. The **knowledge layer**
(`paper`, `concept`, `thread`, `brief`, `note`, `conversation`) holds what we
have learned — from the literature and from our own experiments. The
**operational layer** (`sop`, `person`, `preference`) holds how the team works.
The **wiki-meta layer** (`adr`, `moc`, `meta`) holds the rules and indexes for
the wiki itself.

The server uses `type` to decide where a `write_page` may land and how to treat
a page (papers are quoted, concepts are linked to, `_conventions/`/`adr` are
read but not freely written). Rule of thumb in the knowledge layer: *concept >
brief > note* — prefer the smallest container that fits, promote upward only
when a real audience appears.

## Knowledge layer

### `paper`  *(corpus specialty)*
An external research-paper card under `papers/`, one file per work, named
`{firstauthor}{year}_{keyword}.md`. The eight-section body (Abstract · Why this
matters for us · Key claims · Methods · Results · Critique · Connection to our
work · Citations to follow) is the curated summary; the original paper (arXiv /
DOI) is the source of truth for quotation. `depth` tracks completeness
(`metadata`→`full`); layered disclosure adds a `## TL;DR`. Papers are the
slowest-moving substantive type — written once, deepened over time, rarely
rewritten. They are the `grounded-in` target for concepts and the `informs`
target for other papers.

### `concept`  *(atomic unit)*
One mechanism or term per file under `concepts/` (e.g.
`hierarchical_predictive_coding`, `slow_fast_recurrence`). A concept page
*defines* a single noun phrase; its `papers:` are the evidential anchors
(`grounded-in`). Well-formed when (a) the title is the defined term, (b) the
body holds a definition compact enough to quote inline, (c) other concepts it
mentions are wikilinked, (d) at least one anchor paper is cited. **Not** a place
for synthesis — past ~400 words it is probably a `brief`. Concepts are the only
type for which "does this need a backlink yet?" is "yes by default". There are
89 concept *tags* referenced by papers that have no page yet — that backlog is
the natural source of new concept pages.

### `thread`  *(narrative through-line — local specialty)*
A long-running, chronological log under `threads/` that ties many papers and
concepts into a story or an engineering record (e.g. `rvit_plus_engineering`,
`predictive_coding_as_canonical_computation`). Threads are part map-of-content,
part running brief. Each dated run entry should carry enough method + result +
run-id to be reproducible (the thread as a whole is a chronology, not one
finding). Threads are where the human and the Researcher agent narrate the
program over time.

### `brief`  *(synthesis)*
A multi-concept synthesis under `briefs/` (created on first need). Briefs answer
"how does X interact with Y?" and are allowed to have opinions; a concept page
is not. Structured Finding · Mechanism · Frame · Action, every load-bearing
claim cited to a concept/paper/note. The natural promotion target for a
`conversation` or `note` that turns out to matter.

### `note`  *(working memory / finding — agent write-target)*
A finding about our own work, or low-confidence working memory, under `notes/`.
Notes may be dated investigation stubs (`YYYY-MM-DD-<topic>.md`) produced by the
Researcher agent as the `crystallized:` target of a conversation. Finding notes
follow the six-section reproducible-findings template; scratch notes under ~150
words may skip it. The agent reads notes but flags their uncertainty when
quoting. **Promotion rule:** a note moves to `concept` (atomic term) or `brief`
(synthesis) when **two independent** non-conversation pages cite it *and* its
Method/Evidence/Reproduction are non-empty.

### `conversation`  *(dated Q&A / run-log — append-only)*
A record of a substantive exchange or an agent run, under `conversations/`. The
`crystallized:` list names the concepts/notes/briefs the exchange produced —
the compounding signal that tells us the wiki is getting denser under use.
Append-only: written once, promoted by reference (not mutation).

## Operational layer

### `sop`
A team operational procedure under `sops/` — written once a procedure has run
twice and converged. Body: Trigger · Preconditions · Steps · Verification ·
Rollback · Owner. (e.g. "how to deepen a paper stub", "how to crystallize a
run into a note", "how to run the graph rebuild".)

### `person`
A collaborator profile under `people/` (e.g. the RViT co-authors). Tunes agent
tone/depth for the active user; not a store of factual claims. The agent writes
only the active user's page.

### `preference`
A team-level working rule under `preferences/` (e.g. "cite runs by run-id, not
date"; "default to full 8-section paper cards, not reading lists").

## Wiki-meta layer

### `moc`  *(project hub)*
A map of content under `mocs/` (or vault root, `_`-prefixed). The four project
hubs — `recurrent_vit`, `prism_v1`, `prism_v2`, `rvit_plus` — become MOCs:
curated entry points linking the papers/concepts/threads/notes for that program
in reading order. These are the `relevance_to:`/`informs` targets of 498 paper
edges, so creating them resolves a large block of otherwise-dangling links.

### `adr`
Architecture decision record for the wiki/system itself, under `_adr/`, numbered
sequentially. Immutable once accepted (only `superseded_by` is ever filled in).

### `meta`
Pages about the vault itself — the `_conventions/` files, `README`, `SCHEMA`,
`TAXONOMY`. Read by the agent for context; the curator edits conventions only
when explicitly tasked.

## Decision flow

Knowledge layer first, then operational, then fall through to `note`:

1. A summary of an external paper? → `paper` (`papers/`).
2. A single mechanism or term? → `concept` (`concepts/`).
3. A chronological log tying many works into a story or run-record? → `thread`
   (`threads/`).
4. A synthesis across two or more concepts? → `brief` (`briefs/`).
5. A record of a Q&A exchange or an agent run? → `conversation`
   (`conversations/`).
6. A multi-step operational procedure with a trigger? → `sop` (`sops/`).
7. A collaborator profile / team preference? → `person` / `preference`.
8. A curated hub for a whole project? → `moc`.
9. An architecture decision for the wiki itself? → `adr` (`_adr/`).
10. None of the above? → `note` (`notes/`), review later.

## Write allowlist

Agents may write the knowledge layer (`paper`, `concept`, `thread`, `brief`,
`note`, `conversation`) and, with the right role, the operational layer. Agents
may **not** freely write `_conventions/` (`meta`) or `_adr/` — those are human +
curator canon. The server enforces this allowlist.
