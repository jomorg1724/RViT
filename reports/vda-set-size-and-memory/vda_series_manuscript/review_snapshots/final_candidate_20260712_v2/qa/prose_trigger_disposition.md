# Integrated prose-trigger disposition — repaired candidate v2

- Source: `main.tex` SHA-256 `1ffb36dabc7e9cdfc4877baa3926a7e1f8f3103d8de76f725c4570b83dd65502`
- PDF: `main.pdf` SHA-256 `598c332ea0404e0a7d4c39efc6edd7906477235c52021e280cf63c7a4506461d`
- Canonical linter exit: `1` (findings are triage events, not automatic failures)
- Raw events: **44** across **37** source lines
- Trigger multiset: 36 comma-chain; 8 semicolon-chain; 0 long-sentence
- Disposition multiset: **44 RETAIN; 0 REVISE; 0 unassigned; 0 duplicated**

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
| 5 | 88 | comma-chain | 6 | 20 | RETAIN | C |
| 6 | 91 | comma-chain | 6 | 39 | RETAIN | C |
| 7 | 92 | comma-chain | 4 | 31 | RETAIN | C |
| 8 | 103 | semicolon-chain | 2 | 46 | RETAIN | L |
| 9 | 105 | comma-chain | 4 | 45 | RETAIN | E |
| 10 | 112 | comma-chain | 4 | 9 | RETAIN | C |
| 11 | 143 | semicolon-chain | 3 | 53 | RETAIN | L |
| 12 | 147 | comma-chain | 5 | 21 | RETAIN | E |
| 13 | 155 | comma-chain | 4 | 25 | RETAIN | C |
| 14 | 186 | comma-chain | 5 | 32 | RETAIN | C |
| 15 | 206 | comma-chain | 4 | 25 | RETAIN | E |
| 16 | 206 | comma-chain | 5 | 41 | RETAIN | E |
| 17 | 217 | comma-chain | 7 | 24 | RETAIN | E |
| 18 | 229 | semicolon-chain | 2 | 28 | RETAIN | C |
| 19 | 259 | comma-chain | 4 | 18 | RETAIN | C |
| 20 | 267 | semicolon-chain | 2 | 26 | RETAIN | C |
| 21 | 273 | comma-chain | 5 | 16 | RETAIN | E |
| 22 | 337 | comma-chain | 7 | 36 | RETAIN | C |
| 23 | 342 | comma-chain | 6 | 14 | RETAIN | C |
| 24 | 352 | comma-chain | 6 | 20 | RETAIN | C |
| 25 | 358 | comma-chain | 5 | 44 | RETAIN | C |
| 26 | 380 | comma-chain | 5 | 17 | RETAIN | C |
| 27 | 392 | comma-chain | 4 | 1 | RETAIN | S |
| 28 | 397 | comma-chain | 5 | 22 | RETAIN | C |
| 29 | 397 | comma-chain | 5 | 33 | RETAIN | C |
| 30 | 401 | semicolon-chain | 2 | 17 | RETAIN | C |
| 31 | 415 | comma-chain | 5 | 27 | RETAIN | C |
| 32 | 425 | semicolon-chain | 2 | 40 | RETAIN | L |
| 33 | 431 | comma-chain | 4 | 19 | RETAIN | E |
| 34 | 433 | comma-chain | 4 | 18 | RETAIN | E |
| 35 | 436 | comma-chain | 4 | 13 | RETAIN | E |
| 36 | 445 | comma-chain | 5 | 20 | RETAIN | C |
| 37 | 452 | comma-chain | 5 | 24 | RETAIN | E |
| 38 | 452 | comma-chain | 5 | 35 | RETAIN | E |
| 39 | 452 | comma-chain | 4 | 31 | RETAIN | E |
| 40 | 458 | comma-chain | 9 | 34 | RETAIN | C |
| 41 | 458 | comma-chain | 4 | 26 | RETAIN | C |
| 42 | 470 | semicolon-chain | 4 | 29 | RETAIN | C |
| 43 | 486 | semicolon-chain | 4 | 21 | RETAIN | C |
| 44 | 486 | comma-chain | 6 | 18 | RETAIN | C |

## Mechanical closure

- Class multiset: S=2, L=3, C=25, E=14.
- Raw-event count equals disposition-row count: `44 = 44`.
- Raw trigger-kind multiset reproduced exactly: `{'comma-chain': 36, 'semicolon-chain': 8}`.
- Publication-consequential defects outside the linter remain subject to the independent prose audit; this record does not pre-approve them.
