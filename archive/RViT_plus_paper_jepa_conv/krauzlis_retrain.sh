#!/usr/bin/env bash
# Retrain Krauzlis to break the ALWAYS-WAIT exploration deadlock diagnosed via the critic Q-values:
# the encoder+critic already represent+value the task (decode cued-vs-foil 0.91-1.00; Q(wait|cued)=0.02),
# but Q(declare|cued)≈0 (never learned, should be +1) because declaring is punished on ~69% of trials
# (no-change + foil), so exploration of "declare" collapses before the cued-change +1 is learned.
#
# FIX = proportion-WARMUP (bootstrap the declare policy where declaring is pure upside, THEN add the traps):
#   PHASE 1  --proportions 1.0  -> EVERY change is at the cued patch, NO foil traps. Declaring a detected
#            change is always +1 (like validity4, which learned) -> Q(declare|cued) climbs -> actor declares.
#   PHASE 2  --proportions 0.25 0.5 0.75 1.0  (resume) -> reintroduce foil changes -> the actor refines the
#            already-declaring policy into "declare cued / withhold foil" (the discrimination the encoder
#            already supports). Plus mild exploration levers (declare-bias -0.5, entropy 0.02).
#
# Both variants, MPS bursts (dodge the allocator leak). Distinct ckpt dir. Verify with faithful_eval_krauzlis.py.
set -u
REPO=/Users/jonathanmorgan/AttentionManuscript/RViT_plus_paper_jepa_conv
VENV=/Users/jonathanmorgan/AttentionManuscript/.venv/bin/activate
CKROOT=/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results
BURST=4000; BIAS="0.0 -0.5"; ENT=0.02
WARMUP_ITERS=8000        # phase 1 (all-cued bootstrap)
FULL_ITERS=12000         # phase 2 (foils reintroduced)

source "$VENV"; cd "$REPO" || exit 1

run_phase() {  # FB CKPT TOTAL "PROPS" FRESH_OK
  local FB=$1 CKPT=$2 TOTAL=$3 PROPS=$4 FRESHOK=$5 done=0
  while [ "$done" -lt "$TOTAL" ]; do
    local MODE=resume
    { [ "$FRESHOK" = 1 ] && [ ! -f "$CKPT/rvit_plus_rl_latest.pt" ]; } && MODE=fresh
    echo ">>> $FB  props=[$PROPS]  burst mode=$MODE  (+$BURST it)  $(date '+%H:%M:%S')"
    PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=3 \
    python train_rl.py --device mps --init-mode "$MODE" \
      --T 7 --min-change-time 5 --max-change-time 5 --cell xlstm --feedback "$FB" \
      --conv-frontend --jepa-coef 0.5 --d-mem 128 --curriculum --theta-start 65 \
      --init-action-bias $BIAS --entropy-coef "$ENT" --proportions $PROPS \
      --iters "$BURST" --save-every 200 --task krauzlis --checkpoint-dir "$CKPT" || {
        echo "!! $FB burst failed (OOM? lower BURST). checkpoint safe; re-run to continue."; return 1; }
    done=$((done + BURST))
  done
}

for FB in affine_ew crossattn1; do
  CKPT="$CKROOT/krauzlis_retrain_$FB"; mkdir -p "$CKPT"
  echo "===== $FB : PHASE 1 warmup (all-cued, bootstrap the declare policy) ====="
  run_phase "$FB" "$CKPT" "$WARMUP_ITERS" "1.0" 1 || continue
  echo "===== $FB : PHASE 2 full (reintroduce foils, teach localization) ====="
  run_phase "$FB" "$CKPT" "$FULL_ITERS" "0.25 0.5 0.75 1.0" 0 || continue
  echo ">>> $FB retrain complete. Verify: python faithful_eval_krauzlis.py"
done
echo "==== krauzlis retrain finished $(date '+%H:%M:%S') ===="
