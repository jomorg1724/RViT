#!/usr/bin/env bash
set -euo pipefail

GRID="${GRID:?set GRID to 20 or 2}"
case "$GRID" in
  20|2) ;;
  *) echo "GRID must be exactly 20 or 2; got: $GRID" >&2; exit 2 ;;
esac

RUN_ROOT="${RUN_ROOT:-/workspace/rvit_runs/luo2015_corrected_grid${GRID}x${GRID}_dmem32_memnoise064_seed000}"
PYTHON_BIN="${PYTHON_BIN:-python}"
ITERS="${ITERS:-20000}"
DEVICE="${DEVICE:-cuda}"
SAVE_EVERY="${SAVE_EVERY:-50}"
if [[ "$ITERS" -lt 1 ]]; then
  echo "ITERS must be positive" >&2
  exit 2
fi
SCHEDULE_FINAL_ITERATION=$((ITERS - 1))

cmd=(
  "$PYTHON_BIN" -u train_rl.py
  --T 7
  --patch-grid-rows "$GRID"
  --patch-grid-cols "$GRID"
  --cell xlstm
  --feedback crossattn1
  --memory-decay 1.0
  --memory-noise-std 0.64
  --noise 5.0
  --conv-frontend
  --jepa-coef 0.5
  --d-mem 32
  --episodes-per-iter 8
  --gamma 1.0
  --save-every "$SAVE_EVERY"
  --log-every 1
  --seed 0
  --device "$DEVICE"
  --iters "$ITERS"
  --schedule-final-iteration "$SCHEDULE_FINAL_ITERATION"
  --checkpoint-dir "$RUN_ROOT"
  --experiment-launcher experiments/luo2015_episodic/run_matrix.py
  --task luo2015_criterion
  --init-mode fresh
  --r-hit 1.0
  --r-cr 1.0
  --high-loc 0
  --reward-scale 1.0
  --theta-start 65.0
  --curriculum
  --curr-floor 18.0
)

if [[ "${DRY_RUN:-0}" == "1" ]]; then
  printf '%q ' "${cmd[@]}"
  printf '\n'
  exit 0
fi

if [[ -e "$RUN_ROOT/rvit_plus_rl_latest.pt" || -e "$RUN_ROOT/rvit_paper_luo2015_criterion_final.pt" ]]; then
  echo "refusing fresh launch into a run root containing a checkpoint: $RUN_ROOT" >&2
  exit 3
fi
mkdir -p "$RUN_ROOT"
cp experiments/luo2015_episodic/corrected_orientation_grid_compare_runpod/experiment_manifest.json \
  "$RUN_ROOT/experiment_manifest.json"
printf 'grid=%s\nrun_root=%s\niters=%s\ndevice=%s\n' "$GRID" "$RUN_ROOT" "$ITERS" "$DEVICE" \
  > "$RUN_ROOT/launch_contract.txt"

exec "${cmd[@]}"
