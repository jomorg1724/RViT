#!/usr/bin/env bash
set -euo pipefail

RUN_ROOT="${1:-C:/Users/jomor/Documents/RViT_runs/luo2015_grid20x20_dmem32_memnoise064_nodecay_matched_eval_neutral_seed000_local}"
mkdir -p "$RUN_ROOT"

python -u train_rl.py \
  --T 7 \
  --patch-grid-rows 20 \
  --patch-grid-cols 20 \
  --cell xlstm \
  --feedback crossattn1 \
  --memory-decay 1.0 \
  --memory-noise-std 0.64 \
  --noise 5.0 \
  --conv-frontend \
  --jepa-coef 0.5 \
  --d-mem 32 \
  --episodes-per-iter 8 \
  --gamma 1.0 \
  --save-every 50 \
  --log-every 1 \
  --seed 0 \
  --device cuda \
  --iters 20000 \
  --schedule-final-iteration 19999 \
  --checkpoint-dir "$RUN_ROOT" \
  --experiment-launcher experiments/luo2015_episodic/run_matrix.py \
  --task luo2015_criterion \
  --init-mode fresh \
  --r-hit 1.0 \
  --r-cr 1.0 \
  --high-loc 0 \
  --reward-scale 1.0 \
  --theta-start 65.0 \
  --curriculum \
  --curr-floor 18.0
