# Fresh `2×2` Luo reward matrix at gamma 0.7

Four independent seed-0 policies train from identical fresh initialization under fixed reward objectives:

- sensitivity × condition location 0/3;
- criterion × condition location 0/3.

Held fixed: corrected independent axial initial orientations, `Δ~Uniform(-65°,65°)`, no curriculum, seven-frame timing, `2×2` visual/memory grid, `d_mem=32`, mnemonic-noise SD `0.32`, retention `1.0`, sensory jitter `5°`, cross-attention xLSTM, JEPA coefficient `0.5`, sampled actions, and 20,000 iterations.

`gamma=0.7` is a deliberate temporal-credit hypothesis. Because correct rejections are delivered later than hits, it changes effective first-test H:CR values. These runs estimate independent fixed-condition policy optima, not warm-start adaptation or the paper's alternating reward blocks. Location counterphasing is required to remove static spatial asymmetry from the primary `d'` and criterion contrasts.
