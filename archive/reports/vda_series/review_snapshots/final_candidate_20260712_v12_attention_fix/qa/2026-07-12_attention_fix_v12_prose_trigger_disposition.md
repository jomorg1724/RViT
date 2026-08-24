# Attention-fix v12 prose-trigger disposition

- Source: `main.tex` SHA-256 `28ae6ecb4057ea32a7ac491f8f528100362e74e514a0953a1e68fc4b459bd5eb`
- PDF: `main.pdf` SHA-256 `28fb82d7dcffcc1f34eb4a280d88a326de99ed7d456a42f0a1a23481bdd88e55`
- Canonical linter exit: `1` (findings are triage events, not automatic failures)
- Raw events: **48** across **40** source lines
- Trigger multiset: 37 comma-chain; 11 semicolon-chain; 0 long-sentence
- Disposition multiset: **48 RETAIN; 0 REVISE; 0 unassigned; 0 duplicated**

## Classes

- **S** — machine syntax or mathematical notation; punctuation is not prose structure.
- **L** — deliberate parallel logical partition; clauses are short, symmetric, and contrastive.
- **C** — compact table, caption, legend, value vector, or protocol key whose repeated attributes require local enumeration.
- **E** — necessary scientific/provenance enumeration with an explicit governing claim and readable hierarchy.

Every event below is assigned exactly once. `RETAIN` means the punctuation trigger was manually reviewed and does not obscure the scientific hierarchy; it does not waive independent review of other defects on the same line.

| Event | Source line | Trigger | Measure | Words | Decision | Class |
|---:|---:|---|---:|---:|---|:---:|
| 1 | 25 | comma-chain | 6 | 8 | RETAIN | S |
| 2 | 66 | comma-chain | 4 | 13 | RETAIN | C |
| 3 | 77 | comma-chain | 4 | 23 | RETAIN | E |
| 4 | 77 | comma-chain | 4 | 32 | RETAIN | E |
| 5 | 80 | comma-chain | 4 | 29 | RETAIN | L |
| 6 | 80 | semicolon-chain | 4 | 29 | RETAIN | L |
| 7 | 90 | comma-chain | 6 | 20 | RETAIN | C |
| 8 | 93 | comma-chain | 6 | 39 | RETAIN | C |
| 9 | 94 | comma-chain | 4 | 36 | RETAIN | C |
| 10 | 105 | semicolon-chain | 2 | 46 | RETAIN | L |
| 11 | 107 | comma-chain | 4 | 45 | RETAIN | E |
| 12 | 114 | comma-chain | 4 | 9 | RETAIN | C |
| 13 | 145 | semicolon-chain | 3 | 53 | RETAIN | L |
| 14 | 149 | comma-chain | 5 | 25 | RETAIN | E |
| 15 | 157 | comma-chain | 4 | 25 | RETAIN | C |
| 16 | 188 | comma-chain | 5 | 32 | RETAIN | C |
| 17 | 208 | comma-chain | 4 | 25 | RETAIN | E |
| 18 | 208 | comma-chain | 5 | 41 | RETAIN | E |
| 19 | 219 | comma-chain | 7 | 24 | RETAIN | E |
| 20 | 231 | semicolon-chain | 2 | 28 | RETAIN | C |
| 21 | 261 | comma-chain | 4 | 18 | RETAIN | C |
| 22 | 269 | semicolon-chain | 2 | 26 | RETAIN | C |
| 23 | 275 | comma-chain | 5 | 17 | RETAIN | E |
| 24 | 338 | semicolon-chain | 2 | 27 | RETAIN | C |
| 25 | 341 | semicolon-chain | 2 | 36 | RETAIN | C |
| 26 | 351 | comma-chain | 7 | 36 | RETAIN | C |
| 27 | 356 | comma-chain | 6 | 14 | RETAIN | C |
| 28 | 366 | comma-chain | 6 | 20 | RETAIN | C |
| 29 | 372 | comma-chain | 5 | 44 | RETAIN | C |
| 30 | 394 | comma-chain | 5 | 17 | RETAIN | C |
| 31 | 406 | comma-chain | 4 | 1 | RETAIN | S |
| 32 | 411 | comma-chain | 5 | 22 | RETAIN | C |
| 33 | 411 | comma-chain | 5 | 33 | RETAIN | C |
| 34 | 415 | semicolon-chain | 2 | 17 | RETAIN | C |
| 35 | 429 | comma-chain | 5 | 27 | RETAIN | C |
| 36 | 439 | semicolon-chain | 2 | 40 | RETAIN | L |
| 37 | 445 | comma-chain | 4 | 19 | RETAIN | E |
| 38 | 447 | comma-chain | 4 | 18 | RETAIN | E |
| 39 | 450 | comma-chain | 4 | 13 | RETAIN | E |
| 40 | 459 | comma-chain | 5 | 20 | RETAIN | C |
| 41 | 466 | comma-chain | 5 | 24 | RETAIN | E |
| 42 | 466 | comma-chain | 5 | 35 | RETAIN | E |
| 43 | 466 | comma-chain | 4 | 31 | RETAIN | E |
| 44 | 472 | comma-chain | 12 | 43 | RETAIN | C |
| 45 | 472 | comma-chain | 4 | 26 | RETAIN | C |
| 46 | 484 | semicolon-chain | 4 | 29 | RETAIN | C |
| 47 | 500 | semicolon-chain | 4 | 21 | RETAIN | C |
| 48 | 500 | comma-chain | 6 | 18 | RETAIN | C |

## Mechanical closure

- Class multiset: S=2, L=5, C=27, E=14.
- Raw-event count equals disposition-row count: `48 = 48`.
- Raw trigger-kind multiset reproduced exactly: `{'comma-chain': 37, 'semicolon-chain': 11}`.
- The 265-to-266 test-count correction changes no prose-overload tuple.
- Publication-consequential defects outside the linter remain subject to independent prose audit; this record does not pre-approve them.
