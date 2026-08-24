# Dual-stream d_mem=128 Luo sensitivity curriculum rerun

This package launches exactly two fresh seed-0 sensitivity policies: manipulated location 0 and manipulated location 3. Criterion cells are unsupported.

## Single-variable intervention

The recurrent width is doubled from `d_mem=64` to `d_mem=128` independently in actor and critic streams. With four spatial tokens, each stream exposes 512 hidden-memory scalars and carries 2,048 xLSTM state scalars across H/C/N/M; both streams carry 4,096 state scalars total.

## Curriculum contract

The shrinking-theta curriculum is enabled from iteration zero: start at 65 degrees; evaluate non-overlapping windows of 1,000 valid SDT trials; decrement 3 degrees at correctness >=0.85; floor 8 degrees.

## Held fixed

Dual actor/critic separation, 2x2 token grid, xLSTM/crossattn1, independent JEPA branches at coefficient 0.5 each, fixed JEPA teacher EMA 0.996, gamma 1.0, mnemonic-noise SD 0.075, sensory jitter 5 degrees, BC 0, reward table, action timing, seed 0, and 20,000 iterations.

The fixed reward ratios are intentionally unchanged to isolate memory capacity. They directly pressure criterion, so this is not a corrected criterion-titration experiment or a direct Luo-Maunsell replication. The strict frozen-policy target remains positive location-specific delta d-prime with absolute delta criterion no greater than 0.2, counterphased across both lineages.

## Dry run

```bash
CELL=sensitivity_loc3 RUN_ROOT=/tmp/dmem128_loc3 DRY_RUN=1 bash experiments/luo2015_episodic/fresh_dualstream_dmem128_grid2_memnoise0075_gamma100_bc000_curriculum_sensitivity_runpod/launch_cell.sh
```
