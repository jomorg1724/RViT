# Migration Note — 2026-08-23 (RViT repository unification)

This wiki formerly lived at `AttentionManuscript/research_db/` on the Mac-era
workspace. It is now tracked in git as the `wiki/` directory of the unified
**RViT** repository (`github.com/jomorg1724/RViT`).

## Path changes

| Old location | New location |
|---|---|
| `AttentionManuscript/research_db/` | `wiki/` |
| `AttentionManuscript/README.md` | `docs/ATTENTION_MANUSCRIPT.md` |
| `AttentionManuscript/MODEL_DESIGN.md` | `docs/MODEL_DESIGN.md` |
| `AttentionManuscript/RVIT_PLUS_DESIGN.md` | `docs/RVIT_PLUS_DESIGN.md` |
| `AttentionManuscript/RVIT_PLUS_NOTES.md` | `docs/RVIT_PLUS_NOTES.md` |
| `AttentionManuscript/archive/` (Prism, HRA, RViT_plus_v*, …) | `archive/` |
| `AttentionManuscript/archive/reports/research_state/` | `reports/research_state/` |
| `OngoingRViTExperiments/<Category>/experiments/` | `experiments/<program>/` |
| `OngoingRViTExperiments/<Category>/reports/` | `reports/<program>/` |
| `OngoingRViTExperiments/<Category>/runs/` | `runs/<program>/` (git-ignored) |
| `OngoingRViTExperiments/<Category>/rescues/` | `rescues/<program>/` (git-ignored) |
| `RViT_plus_paper_jepa_grid9/` (live codebase) | `code/` |

Program slugs: `VDASetSizeAndMemory` → `vda-set-size-and-memory`,
`LuoMaunsellReproductions` → `luo-maunsell-reproductions`,
`RethinkingMemoryStabilityAndPercepts` → `memory-stability-and-percepts`.

## Link maintenance performed

- 12 links across `papers/dabney2018_qr_dqn.md`, `papers/dicarlo2012_object_recognition.md`,
  `papers/sutton_barto2018_rl_intro.md`, and `concepts/distributional_rl.md` that pointed at
  `../../Prism/…`, `../../HRA/…`, and `../../MODEL_DESIGN.md` were retargeted to
  `../../archive/Prism/…`, `../../archive/HRA/…`, and `../../docs/MODEL_DESIGN.md`.
  All targets verified to exist after the move. One previously-broken link
  (`../../Prism/PrismV2/docs/PRISM_V2_PROPOSAL.md`) was repaired to
  `../../archive/Prism/docs/PRISM_V2_PROPOSAL.md`.
- `../reports/research_state/…` links resolve to `reports/research_state/` as before.
- All other links are internal to the wiki and were preserved verbatim.

## What did not move into git

Model weights/checkpoints, datasets/archives, run outputs, and virtual
environments are excluded by `.gitignore`. Lightweight run artifacts
(logs/configs/plots ≤ 2 MB) were copied locally under `runs/` and `rescues/`
for reference but are intentionally untracked. The full-fidelity heavy data
remains at the original locations (see `docs/provenance/MANIFEST.md`).
