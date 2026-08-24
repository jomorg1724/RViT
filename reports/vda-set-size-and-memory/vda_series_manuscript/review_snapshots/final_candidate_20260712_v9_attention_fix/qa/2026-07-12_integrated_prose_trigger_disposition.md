# Integrated prose-trigger disposition — repaired candidate v3

- Source: `main.tex` SHA-256 `19f8cbbd85d736b77263f273dccb15a2ac962f8d9f996e44cd829f6ce30a8f5d`
- PDF: `main.pdf` SHA-256 `d1f87f402019f05158dbe3b3db451a3cab77494edb5c56c7b00e3c19cf6d30f7`
- Canonical linter exit: `1` (findings are triage events, not automatic failures)
- Raw events: **46** across **38** source lines
- Trigger multiset: 37 comma-chain; 9 semicolon-chain; 0 long-sentence
- Disposition multiset: **46 RETAIN; 0 REVISE; 0 unassigned; 0 duplicated**

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
| 23 | 275 | comma-chain | 5 | 16 | RETAIN | E |
| 24 | 339 | comma-chain | 7 | 36 | RETAIN | C |
| 25 | 344 | comma-chain | 6 | 14 | RETAIN | C |
| 26 | 354 | comma-chain | 6 | 20 | RETAIN | C |
| 27 | 360 | comma-chain | 5 | 44 | RETAIN | C |
| 28 | 382 | comma-chain | 5 | 17 | RETAIN | C |
| 29 | 394 | comma-chain | 4 | 1 | RETAIN | S |
| 30 | 399 | comma-chain | 5 | 22 | RETAIN | C |
| 31 | 399 | comma-chain | 5 | 33 | RETAIN | C |
| 32 | 403 | semicolon-chain | 2 | 17 | RETAIN | C |
| 33 | 417 | comma-chain | 5 | 27 | RETAIN | C |
| 34 | 427 | semicolon-chain | 2 | 40 | RETAIN | L |
| 35 | 433 | comma-chain | 4 | 19 | RETAIN | E |
| 36 | 435 | comma-chain | 4 | 18 | RETAIN | E |
| 37 | 438 | comma-chain | 4 | 13 | RETAIN | E |
| 38 | 447 | comma-chain | 5 | 20 | RETAIN | C |
| 39 | 454 | comma-chain | 5 | 24 | RETAIN | E |
| 40 | 454 | comma-chain | 5 | 35 | RETAIN | E |
| 41 | 454 | comma-chain | 4 | 31 | RETAIN | E |
| 42 | 460 | comma-chain | 9 | 34 | RETAIN | C |
| 43 | 460 | comma-chain | 4 | 26 | RETAIN | C |
| 44 | 472 | semicolon-chain | 4 | 29 | RETAIN | C |
| 45 | 488 | semicolon-chain | 4 | 21 | RETAIN | C |
| 46 | 488 | comma-chain | 6 | 18 | RETAIN | C |

## Mechanical closure

- Class multiset: S=2, L=5, C=25, E=14.
- Raw-event count equals disposition-row count: `46 = 46`.
- Raw trigger-kind multiset reproduced exactly: `{'comma-chain': 37, 'semicolon-chain': 9}`.
- Publication-consequential defects outside the linter remain subject to the independent prose audit; this record does not pre-approve them.
