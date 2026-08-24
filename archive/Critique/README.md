# Critique — VDA Skeptical-Reviewer Workspace

This directory is the writeable workspace for the VDA Skeptical-
Reviewer agent (see `../agents/skeptical_reviewer_prompt.md` for the
mission). The agent reads `source/main.pdf` and the wiki at
`../research_db/` and produces verdicts, derivations, replications,
evidence dossiers, and conversation pages here.

## Layout

```
Critique/
├── README.md            # this file
├── source/
│   └── main.pdf         # the target paper (read-only by the agent)
├── verdicts/            # one .md per claim/assumption; append-only at the version level
├── evidence/            # one .md per claim; literature dossiers accumulate across runs
├── derivations/         # one .md per re-derivation attack
├── replications/        # one subdir per replication attack: run.py + README + output/ + notes
└── conversations/       # one .md per run; the chronological "what I did" log
```

## How to read the work

To get the current state of the critique:

1. **`verdicts/`** — the headline. Each file's latest `## Version`
   section is the current verdict on one claim or assumption.
2. **`../agents/RUN_LOG.md`** — the trajectory. Newest run at top;
   read the top 5–10 entries to see what's moved recently.
3. **`../agents/RESEARCH_BACKLOG.md`** — what's queued. The agent
   owns this file after bootstrap; status fields are authoritative.
4. **`evidence/`** — the case behind a verdict, citation by citation.
5. **`derivations/`** and **`replications/`** — the math and code
   that drives the verdicts. Always read in conjunction with the
   verdict file that cites them.

## Verdict labels

Defined in mission §3.1:

- **CONFIRMED-UNDER-ATTACK** — survived ≥2 distinct attack vectors.
- **CONFIRMED-CONDITIONAL** — survives within stated scope; fails
  or unclear outside.
- **WEAKLY-SUPPORTED** — one attack failed; second attack needed.
- **CONTESTED** — at least one credible attack succeeded; verdict
  proposes a weaker reformulation.
- **REFUTED** — derivation error, replication failure, or
  literature contradiction the paper cannot survive without
  substantive revision.
- **OPEN** — verdict stub; no run has attacked yet.

The agent is biased toward staying in `WEAKLY-SUPPORTED` /
`OPEN` until two distinct attack vectors have been tried. This is
intentional. Confidence is earned across runs, not declared in one.

## The agent's epistemic stance

Adversarial-first, fair-on-confirmation. Default to attack; only
elevate to `CONFIRMED-*` after the obvious objections fail. If the
paper is wrong somewhere, the agent's job is to find where. If
it's right, the agent's job is to show why the obvious objections
fail.
