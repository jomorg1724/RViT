# Fresh gamma-0.8 reward matrix with half mnemonic noise

This follow-up repeats the four completed gamma-0.8 counterphased cells with recurrent-memory noise SD reduced from `0.32` to `0.16`. Sensory orientation jitter remains `5°`; all other task, architecture, optimization, reward, seed, and iteration settings are unchanged.

Each cell starts from fresh seed-0 weights. This is not a resume, warm start, or child of the prior checkpoint. The primary operational comparison is the same-distribution training evidence at noise `0.32` versus `0.16`; matched frozen-policy SDT evaluation remains a separate requirement.
