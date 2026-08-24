# `Rebuild/` — the constructive rebuild of the Herman-Lab VDA paper

## What this is

The constructive twin of `Critique/`. The skeptical reviewer agent
operated under `agents/skeptical_reviewer_prompt.md` and spent 17+ runs
damaging the load-bearing claims of the Herman Lab paper
*"When Does Value-Directed Attention Matter? A Normative Model with
Independent Attentional Benefit and Cost"* (`Critique/source/main.pdf`,
2026-04-09). The constructive rebuilder agent
(`agents/paper_rebuilder_prompt.md`, v0.2) inherits that verdict
ledger and **rebuilds the paper** so the same scientific question is
answered with a more accurate, honestly-bounded mathematical
description.

The reviewer's output is read-only input. Everything we produce lives
under `Rebuild/`.

## What the rebuild claims (status: 1 increment in)

The rebuilt paper does **not** restate any claim more strongly than the
live verdict ledger licenses. `CLAIM_LEDGER.md` is the live table of
how each C1–C5 / A1–A8 claim returns in the rebuilt manuscript and
which artifact backs it. As of `rb-001` (2026-05-25):

- A1 (independence) — promoted to a tunable parameter `rho` in the
  rebuilt model. The inherited model is the `rho = 0` limit, recovered
  exactly by `model/tests/test_recovery.py`. The reframing is "three
  levers, not two": criterion shift, sensitivity reallocation, and
  decorrelation.
- All other claims still pending their own increment (see backlog).

## Status

- Bootstrap done. `Rebuild/` skeleton, claim ledger, backlog, and
  state file written. Model module `Rebuild/model/` extended with the
  rho channel; recovery test passes 7/7 with the rho=0 limit matching
  the reviewer's logged numbers to floating-point identity.

## Reading order

1. `agents/paper_rebuilder_prompt.md` — the binding mission.
2. `CLAIM_LEDGER.md` — what the rebuilt paper says about each claim
   and what backs it.
3. `REBUILD_BACKLOG.md` — what is queued for future increments.
4. `BUILD_LOG.md` — what every past increment did.
5. `model/README.md` — the rebuilt model.
6. `model/tests/test_recovery.py` — the recovery contract (rho->0
   reproduces inherited model exactly).
7. `conversations/` — per-run narrative pages.

## Directory layout

```
Rebuild/
  README.md               <- this file
  CLAIM_LEDGER.md         <- live disposition of each claim
  REBUILD_BACKLOG.md      <- queued increments (model -> sim -> derivation -> manuscript)
  BUILD_LOG.md            <- append-only run record
  rebuilder_state.json    <- lightweight state
  model/                  <- the rebuilt VDA model implementation
    core.py
    __init__.py
    README.md
    tests/
      test_recovery.py
      recovery_output.json
  sims/                   <- simulations backing rebuilt claims (none yet)
  derivations/            <- derivations (none yet)
  manuscript/             <- LaTeX paper (skeleton not yet drafted)
    sections/
    figures/
  conversations/          <- per-run conversation pages
```

## What we don't do

- Modify `Critique/source/main.pdf` (read-only target).
- Modify anything the reviewer owns (`Critique/verdicts/`,
  `Critique/derivations/`, `Critique/replications/`,
  `Critique/evidence/`, `Critique/conversations/`, the reviewer's
  files under `agents/`). Copy freely; never edit in place.
- Modify `research_db/HANDOFF.md`, `SCHEMA.md`, `TAXONOMY.md`,
  `INDEX.md`, `README.md`, `concepts/`, `threads/`, or existing
  `papers/*.md`. Only add new `papers/*.md` stubs per SCHEMA.md.
- Rename, move, or delete any directory.
- State a claim more strongly than the live verdict ledger licenses.
- Write manuscript prose ahead of the simulation that supports it.

The rebuilt paper stands on its own normative/empirical footing and
does **not** reference the owner's neural-network models (PRISM/HRA or
any successor); v0.2 of the mission removed all PRISM bridging.
