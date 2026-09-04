#!/usr/bin/env bash
# Reassemble the flat source layout the frozen-policy SDT assay was written against.
#
# `luo2015_analysis/luo2015_core.py` and `experiments/luo2015_episodic/analyze_matrix.py`
# both locate the repo by walking up a fixed number of parent directories, and they
# import `envs` / `model` as top-level modules. That held in the pre-consolidation
# workspace, where all three sat side by side. The 2026-08-23 consolidation split them
# across code/, analysis/luo2015/ and experiments/luo-maunsell-reproductions/, which
# breaks those imports.
#
# Rebuilding the expected layout keeps the measurement code BYTE-IDENTICAL to what
# produced the August numbers, which is the whole point of reusing it. Patching the
# path arithmetic inside those modules would not.
#
# Usage: assemble_eval_tree.sh <repo-root> <destination>
set -euo pipefail

REPO="${1:?usage: assemble_eval_tree.sh <repo-root> <destination>}"
DEST="${2:?usage: assemble_eval_tree.sh <repo-root> <destination>}"

for required in \
  "$REPO/code/model.py" \
  "$REPO/code/envs/luo2015.py" \
  "$REPO/analysis/luo2015/luo2015_analysis/luo2015_core.py" \
  "$REPO/experiments/luo-maunsell-reproductions/luo2015_episodic/analyze_matrix.py"
do
  [[ -e "$required" ]] || { echo "missing required source: $required" >&2; exit 2; }
done

rm -rf "$DEST"
mkdir -p "$DEST"

# code/ supplies model.py, ppo.py, envs/, config/ and its own experiments/ subtree.
cp -r "$REPO/code/." "$DEST/"
# The SDT core, as a top-level package.
cp -r "$REPO/analysis/luo2015/luo2015_analysis" "$DEST/luo2015_analysis"
# The episodic assay, merged into the existing experiments/ namespace package.
mkdir -p "$DEST/experiments"
cp -r "$REPO/experiments/luo-maunsell-reproductions/luo2015_episodic" "$DEST/experiments/luo2015_episodic"
# The assay driver runs from inside the tree, exactly as run_partial_sdt.py did.
cp "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/run_ratio1_sdt.py" "$DEST/run_ratio1_sdt.py"

# Verify the layout resolves before a job spends GPU time on it.
#
# Run this from inside $DEST, never from the repo root: the repo has a `code/` package
# with an __init__.py, which shadows Python's stdlib `code` module for anything that
# imports it (pdb does), producing a confusing circular-import failure. The same trap
# applies to running the assay itself -- always cd into the eval tree first.
cd "$DEST"
python - "$DEST" <<'PY'
import sys, pathlib
dest = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(dest))
from luo2015_analysis import luo2015_core                                    # noqa: F401
from experiments.luo2015_episodic.analyze_matrix import balanced_trial_bank  # noqa: F401
from experiments.luo2015_episodic.evaluate_selected_replication import (     # noqa: F401
    _dc, _location_metrics, summarize_policy,
)
core_repo = pathlib.Path(luo2015_core._REPO).resolve()
assert core_repo == dest, f"luo2015_core resolved repo {core_repo}, expected {dest}"
print(f"[assemble] eval tree OK at {dest}")
PY
