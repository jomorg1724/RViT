#!/bin/bash
# ONE Slurm task = train one ratio-1 sensitivity policy AND measure it.
#
# Training and behavioural data collection are deliberately a single job. Splitting them
# would leave trained policies sitting on disk waiting for a second submission, and would
# make every result depend on a checkpoint surviving between two jobs.
#
# The array is 5 seeds x 2 counterphase lineages:
#   task 0-4 -> high_loc=0, seeds 42..46
#   task 5-9 -> high_loc=3, seeds 42..46
#
# Everything except the H:CR ratios and the seed is held identical to the August
# dual-stream d_mem=128 runs (experiments/luo-maunsell-reproductions/
# fresh_dualstream_dmem128_..._runpod/launch_cell.sh), so the comparison is clean.
#
# Submit:  sbatch -M gpu --array=0-9 train_and_measure.slurm
#SBATCH --job-name=lm_ratio1
#SBATCH --cluster=gpu
#SBATCH --partition=l40s
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
# Measured: 2:37-2:44 wall for all ten runs of the 2026-09-02 sweep (20,000 iterations
# plus the in-job assay). 5h leaves ~85% headroom. Do not raise this casually -- an
# oversized walltime request backfills badly on a busy l40s and the first submission of
# this sweep sat PENDING at 8h until the limit was lowered.
#SBATCH --time=05:00:00
#SBATCH --output=/ix/jpherman/hermanj/rvit_ratio1/logs/ratio1_%A_%a.out
set -euo pipefail

BASE="${BASE:-/ix/jpherman/hermanj/rvit_ratio1}"
TREE="${TREE:-$BASE/tree}"
RESULTS="${RESULTS:-$BASE/results}"
ITERS="${ITERS:-20000}"
TRIALS="${TRIALS:-2000}"
SEED_BASE="${SEED_BASE:-42}"
SEEDS_PER_LINEAGE="${SEEDS_PER_LINEAGE:-5}"
TASK=luo2015_sensitivity
# The August runs' overall reward scale, unchanged. It multiplies hit and CR alike, so it
# cannot affect beta* = R_CR/R_hit and therefore cannot affect the reward-optimal criterion.
REWARD_SCALE=0.3333333333333333

IDX="${SLURM_ARRAY_TASK_ID:?this script must run as a job array}"
if (( IDX < SEEDS_PER_LINEAGE )); then
  HIGH_LOC=0; SEED=$(( SEED_BASE + IDX ))
else
  HIGH_LOC=3; SEED=$(( SEED_BASE + IDX - SEEDS_PER_LINEAGE ))
fi

CELL="loc${HIGH_LOC}_seed${SEED}"
RUN_ROOT="$BASE/runs/$CELL"
RUN_ID="ratio1_${CELL}"
FINAL_CKPT="$RUN_ROOT/rvit_paper_${TASK}_final.pt"

echo "== $RUN_ID =="
echo "   array task $IDX -> high_loc=$HIGH_LOC seed=$SEED"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

module load python/pytorch_251_311_cu124
mkdir -p "$RUN_ROOT" "$RESULTS" "$BASE/logs"

# Never run from the repo root: its code/ package shadows the stdlib `code` module.
cd "$TREE"

# ---------------------------------------------------------------- train
if [[ -f "$FINAL_CKPT" ]]; then
  echo "[train] final checkpoint already present; skipping training"
else
  TRAIN_ARGS=(
    --task "$TASK" --T 7
    --patch-grid-rows 2 --patch-grid-cols 2 --cell xlstm --feedback crossattn1
    --dual-actor-critic-streams
    --memory-decay 1.0 --memory-noise-std 0.075 --noise 5.0 --conv-frontend
    --jepa-coef 0.5 --bc-alpha 0.0 --d-mem 128 --episodes-per-iter 8 --gamma 1.0
    --high-loc "$HIGH_LOC" --reward-scale "$REWARD_SCALE"
    # The Step-1 manipulation: H:CR = 1 at BOTH locations, so ln beta* = 0 at both and
    # the reward-optimal criterion difference is exactly zero for any pair of d' values.
    # The 5:1 value manipulation is untouched and is carried by the mean reward alone.
    --high-hit-cr-ratio 1.0 --low-hit-cr-ratio 1.0
    --curriculum --theta-start 65.0 --curr-window 1000 --curr-threshold 0.85
    --curr-step 3.0 --curr-floor 8.0
    --seed "$SEED" --device cuda --save-every 250 --log-every 25
    --iters "$ITERS" --schedule-final-iteration $(( ITERS - 1 ))
    --checkpoint-dir "$RUN_ROOT"
    --experiment-launcher "$TREE/train_and_measure.slurm"
  )
  LATEST="$RUN_ROOT/rvit_plus_rl_latest.pt"
  if [[ -f "$LATEST" ]]; then
    echo "[train] resuming from $LATEST"
    TRAIN_ARGS+=(--init-mode resume --checkpoint-path "$LATEST")
  else
    TRAIN_ARGS+=(--init-mode fresh --start-iteration 0)
  fi
  python -u train_rl.py "${TRAIN_ARGS[@]}"
fi

[[ -f "$FINAL_CKPT" ]] || { echo "training produced no final checkpoint at $FINAL_CKPT" >&2; exit 4; }

# ------------------------------------------------- measure, same job
# Dense theta grid: the August assay's three common thetas exactly saturate the
# equal-variance SDT model, leaving nothing to estimate the variance ratio from.
echo
echo "[assay] measuring $FINAL_CKPT"
ASSAY_ARGS=(
  --checkpoint "$FINAL_CKPT"
  --condition-loc "$HIGH_LOC"
  --run-id "$RUN_ID"
  --output "$RESULTS/$RUN_ID.json"
  --trials "$TRIALS"
  --device cuda
)
# THETAS is an override for pipeline smoke tests only; production uses the script default.
if [[ -n "${THETAS:-}" ]]; then
  # shellcheck disable=SC2206
  ASSAY_ARGS+=(--thetas ${THETAS})
fi
python -u run_ratio1_sdt.py "${ASSAY_ARGS[@]}"

echo
echo "== $RUN_ID complete: policy trained and measured in one job =="
