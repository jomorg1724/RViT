#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
source "$WORKSPACE_ROOT/.venv/bin/activate"

RUN_ROOT="${RUN_ROOT:-$WORKSPACE_ROOT/runs/luo2015_grid20x20_dmem32_memnoise001_nodecay}"
DEVICE="${DEVICE:-cuda}"
mkdir -p "$RUN_ROOT"

python3 -u "$WORKSPACE_ROOT/experiments/luo2015_episodic/run_matrix.py" \
  --run-root "$RUN_ROOT" \
  --seeds 0 1 2 \
  --parent-iters 20000 \
  --child-iters 20000 \
  --theta 18.0 \
  --device "$DEVICE" \
  --feedback crossattn1 \
  --patch-grid-rows 20 \
  --patch-grid-cols 20 \
  --d-mem 32 \
  --memory-decay 1.0 \
  --memory-noise-std 0.01 \
  --noise 5.0 \
  --execute
