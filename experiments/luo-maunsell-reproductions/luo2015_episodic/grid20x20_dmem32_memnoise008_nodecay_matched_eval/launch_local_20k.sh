#!/usr/bin/env bash
set -euo pipefail

RUN_ROOT="${1:-C:/Users/jomor/Documents/RViT_runs/luo2015_grid20x20_dmem32_memnoise008_nodecay_matched_eval_seeds012_local}"

python -u experiments/luo2015_episodic/run_matrix.py \
  --run-root "$RUN_ROOT" \
  --seeds 0 1 2 \
  --parent-iters 20000 \
  --child-iters 20000 \
  --theta 18.0 \
  --device cuda \
  --feedback crossattn1 \
  --patch-grid-rows 20 \
  --patch-grid-cols 20 \
  --d-mem 32 \
  --memory-decay 1.0 \
  --memory-noise-std 0.08 \
  --noise 5.0 \
  --execute
