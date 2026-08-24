# Integrated prose-trigger disposition — final repaired candidate

- Source: `main.tex` SHA-256 `c13429561f521a622b10bd6bc8d9cbce31f41ff5c79cb3e0305660617e28b221`
- PDF: `main.pdf` SHA-256 `158c18e7b14a045e0ddd5c19cfd12eb9500247408b68b111fce3e0574aa54e2f`
- Canonical linter exit: `1` (findings are triage events, not automatic failures)
- Raw events: **43** across **37** source lines
- Trigger multiset: 36 comma-chain; 7 semicolon-chain; 0 long-sentence
- Disposition multiset: **43 RETAIN; 0 REVISE; 0 unassigned; 0 duplicated**

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
| 3 | 77 | comma-chain | 4 | 24 | RETAIN | E |
| 4 | 88 | comma-chain | 6 | 20 | RETAIN | C |
| 5 | 91 | comma-chain | 6 | 39 | RETAIN | C |
| 6 | 92 | comma-chain | 4 | 31 | RETAIN | C |
| 7 | 103 | semicolon-chain | 2 | 46 | RETAIN | L |
| 8 | 105 | comma-chain | 4 | 45 | RETAIN | E |
| 9 | 112 | comma-chain | 4 | 9 | RETAIN | C |
| 10 | 143 | semicolon-chain | 3 | 53 | RETAIN | L |
| 11 | 147 | comma-chain | 5 | 21 | RETAIN | E |
| 12 | 155 | comma-chain | 4 | 25 | RETAIN | C |
| 13 | 186 | comma-chain | 5 | 32 | RETAIN | C |
| 14 | 206 | comma-chain | 4 | 25 | RETAIN | E |
| 15 | 206 | comma-chain | 5 | 41 | RETAIN | E |
| 16 | 217 | comma-chain | 7 | 24 | RETAIN | E |
| 17 | 229 | semicolon-chain | 2 | 28 | RETAIN | C |
| 18 | 259 | comma-chain | 4 | 18 | RETAIN | C |
| 19 | 267 | semicolon-chain | 2 | 26 | RETAIN | C |
| 20 | 273 | comma-chain | 5 | 16 | RETAIN | E |
| 21 | 337 | comma-chain | 7 | 36 | RETAIN | C |
| 22 | 342 | comma-chain | 6 | 14 | RETAIN | C |
| 23 | 352 | comma-chain | 6 | 20 | RETAIN | E |
| 24 | 355 | comma-chain | 5 | 29 | RETAIN | C |
| 25 | 358 | comma-chain | 5 | 44 | RETAIN | C |
| 26 | 380 | comma-chain | 5 | 17 | RETAIN | C |
| 27 | 392 | comma-chain | 4 | 1 | RETAIN | S |
| 28 | 397 | comma-chain | 5 | 22 | RETAIN | C |
| 29 | 397 | comma-chain | 5 | 33 | RETAIN | C |
| 30 | 415 | comma-chain | 5 | 27 | RETAIN | C |
| 31 | 425 | semicolon-chain | 2 | 40 | RETAIN | L |
| 32 | 431 | comma-chain | 4 | 19 | RETAIN | E |
| 33 | 433 | comma-chain | 4 | 18 | RETAIN | E |
| 34 | 436 | comma-chain | 4 | 13 | RETAIN | E |
| 35 | 445 | comma-chain | 5 | 20 | RETAIN | C |
| 36 | 452 | comma-chain | 5 | 24 | RETAIN | E |
| 37 | 452 | comma-chain | 5 | 35 | RETAIN | E |
| 38 | 452 | comma-chain | 4 | 31 | RETAIN | E |
| 39 | 458 | comma-chain | 9 | 34 | RETAIN | C |
| 40 | 458 | comma-chain | 4 | 26 | RETAIN | C |
| 41 | 470 | semicolon-chain | 4 | 29 | RETAIN | C |
| 42 | 486 | semicolon-chain | 4 | 21 | RETAIN | C |
| 43 | 486 | comma-chain | 6 | 18 | RETAIN | C |

## Mechanical closure

- Class multiset: S=2, L=3, C=24, E=14.
- Raw-event count equals disposition-row count: `43 = 43`.
- Raw trigger-kind multiset reproduced exactly: `{'comma-chain': 36, 'semicolon-chain': 7}`.
- Publication-consequential defects outside the linter remain subject to the independent prose audit; this record does not pre-approve them.
