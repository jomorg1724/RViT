# Research evidence organization implementation log

Date: 2026-07-11
Workspace: `/Users/jonathanmorgan/AttentionManuscript`
Plan: `.hermes/plans/2026-07-11_084812-research-evidence-organization.md`

## Safety invariants

- Workspace root is not a Git repository.
- Existing checkpoints, metrics, NPZ bundles, logs, and manuscript sources are preserved in place.
- New training and resumed runs must use new run directories and explicit parent links; legacy checkpoints must not be overwritten.
- Physical moves remain gated on a dependency report and explicit user approval.
- A logged 20,000-row phase is not labeled convergence.

## Pre-flight gate

- Disk: 400 GiB available.
- Python: 3.12.13 in `.venv`.
- Torch: 2.12.0; Apple MPS built and available.
- Baseline model tests: 7 passed (`RViT_plus_paper_jepa_grid9/tests/test_paper.py`).
- Legacy `research_db/tools/audit.py`: 0 issues.
- No active training processes found at pre-flight.
- Installed development dependencies from `requirements-dev.txt`; pytest 9.1.1 and pandas 3.0.3 are available.
- `latexmk` is unavailable. TeX Live `pdflatex`, `xelatex`, `lualatex`, Tectonic, `pdftoppm`, and `pdfinfo` are available.

## Implementation status

- VDA correctness is complete. Strict RED--GREEN repairs cover runtime clamp indexing, exact-validity sampling for future runs, deterministic balanced decoding, matched seeded clamp batches, RNG isolation, output immutability, and checkpoint-bound replay provenance. Controller verification reports 87 tests passing and successful syntax compilation; independent code-quality review approved the implementation with no critical or important findings. The preserved legacy decoder remains byte-identical at SHA-256 `1d8c7fe221d7b67d12dfc7dca05126550228a4825cfaf5d3e0ba6edd696b3a4e`.
- The registry gate is complete. The builder emits 44 deterministic records; normal and strict-active audits both report 0 errors and 217 explicit unknown-provenance warnings. Forty-six focused tests pass. Staged `projects.json` and `artifacts.jsonl` are both validated before either canonical replacement, and the rollback regression preserves prior outputs byte-for-byte. Independent review approved the final staged-catalog repair.
- The empirical-manuscript gate is complete. The manuscript builds as a clean 46-page A4 PDF with no LaTeX warning, undefined-reference, or box-error patterns, and all rendered pages passed contact-sheet visual QA. Archived validity semantics remain historical rather than retroactively corrected. The affine VDA4 change-location value is now consistently reported as 0.50 at the change frame; independent scientific review approved the evidence attribution.
- The fixed-grid controlled-environment gate is complete. Five tasks hold 4x4 geometry, 100x100 RGB observations, and the 16-token model interface constant while varying only active set size. `train_rl.py --seed` initializes both PyTorch and NumPy before environment construction. The full project suite reports 117 passing tests, and independent review approved deterministic CLI seeding.
- No legacy NPZ, checkpoint, metrics file, or source figure was overwritten.
- Wiki integration is in progress now that the registry, manuscript, and fixed-grid gates are complete. Experiment execution remains behind wiki integration and immutable provenance backfill.
