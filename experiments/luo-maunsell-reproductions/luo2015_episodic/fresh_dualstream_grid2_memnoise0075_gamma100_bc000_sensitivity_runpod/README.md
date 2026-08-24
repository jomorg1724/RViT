# Dual-stream Luo–Maunsell sensitivity counterphase

This package launches exactly two fresh policies:

- `sensitivity_loc0`: location 0 receives the sensitivity reward manipulation.
- `sensitivity_loc3`: location 3 receives the sensitivity reward manipulation.

Criterion cells are intentionally unsupported.

## Model intervention

Each policy contains two independently initialized and fully separate paths:

1. actor conv front-end → cross-attention Transformer feedback → xLSTM memory → actor;
2. critic conv front-end → cross-attention Transformer feedback → xLSTM memory → QR critic.

Actor and critic share observations but no trunk or recurrent parameters. Each branch has its own JEPA student projection, center, and corresponding parameters in the EMA JEPA teacher. The JEPA coefficient is `0.5` per branch. Self-behavior cloning is disabled with `bc_alpha=0.0`.

## Held fixed

The task, reward table and timing, action semantics, 2×2 sensory/memory grid, memory width 32 per branch, mnemonic noise 0.075, sensory orientation noise 5°, theta distribution `Uniform(-65°, +65°)`, gamma 1.0, seed 0, and 20,000-iteration horizon match the preceding sensitivity runs.

## Dry run

```bash
CELL=sensitivity_loc0 RUN_ROOT=/tmp/sensitivity_loc0 DRY_RUN=1 bash experiments/luo2015_episodic/fresh_dualstream_grid2_memnoise0075_gamma100_bc000_sensitivity_runpod/launch_cell.sh
```
