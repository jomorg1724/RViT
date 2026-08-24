# Dual-stream d_mem=64 Luo sensitivity curriculum rerun

This package launches exactly two fresh seed-0 sensitivity policies: manipulated location 0 and manipulated location 3. Criterion cells are unsupported.

## Intervention

The recurrent width is doubled from `d_mem=32` to `d_mem=64` independently in the actor and critic streams. With four spatial tokens, each stream exposes 256 hidden-memory scalars and carries 1,024 xLSTM state scalars across H/C/N/M; both streams carry 2,048 state scalars total.

## Required protocol correction

Unlike the invalid original fixed-theta launch and the later mixed-phase continuation, this rerun enables the shrinking-theta curriculum from iteration zero: start 65 degrees; evaluate non-overlapping windows of 1,000 valid SDT trials; decrement 3 degrees at correctness >=0.85; floor 8 degrees.

## Held fixed

Dual actor/critic separation, 2x2 token grid, xLSTM/crossattn1, independent JEPA branches at coefficient 0.5 each, gamma 1.0, mnemonic-noise SD 0.075, sensory jitter 5 degrees, BC 0, reward table, action timing, seed 0, and 20,000 iterations.

The fixed reward ratios are intentionally unchanged to isolate memory capacity. They directly pressure criterion and therefore this is not a corrected criterion-titration or direct Luo-Maunsell replication experiment.

## Dry run

```bash
CELL=sensitivity_loc3 RUN_ROOT=/tmp/dmem64_loc3 DRY_RUN=1 bash experiments/luo2015_episodic/fresh_dualstream_dmem64_grid2_memnoise0075_gamma100_bc000_curriculum_sensitivity_runpod/launch_cell.sh
```
