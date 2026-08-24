# Fresh `2×2` Luo discount-factor ladder

Each of four counterphased reward cells runs three independent 20,000-iteration models sequentially on one pod: `gamma=0.8`, then `0.9`, then `1.0`. Every stage starts from fresh seed-0 weights; no weights, optimizer, replay, target network, environment state, or RNG state carry between discount factors.

Held fixed: `2×2` grid, `d_mem=32`, mnemonic-noise SD `0.32`, retention `1.0`, sensory jitter `5°`, `theta=65°`, no curriculum, seven-frame corrected Luo timing and action semantics, cross-attention xLSTM, and JEPA coefficient `0.5`.

The ladder advances per cell after the previous final checkpoint passes iteration, initialization, gamma, task, location, curriculum, and theta checks. This avoids idle barrier time; cells are independent and do not exchange state. A terminal controller watchdog exports all three stages, verifies checkpoint hashes locally, and deletes the pod.
