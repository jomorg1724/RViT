# INVALID FOR THE CORRECTED LUO TASK CONTRACT

All behavioral curves, attention summaries, intervention comparisons, trial renderings, and reports in this directory were generated from a checkpoint trained under the broken pre-fix initial-orientation contract.

The corrected task independently samples both initial orientations from `Uniform[0°, 180°)` on every trial and uses `theta` only as the bound for `change ~ Uniform(-theta, theta)`. The old implementation instead coupled sample orientations to `theta`.

Retain these files only as forensic provenance. They are not evidence about the corrected Luo delayed change-detection task and must not be reused in a paper or new report.
