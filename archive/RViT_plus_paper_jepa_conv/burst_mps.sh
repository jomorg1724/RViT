#!/usr/bin/env bash
# Burst-train on the Mac GPU (MPS) around the Apple-MPS memory leak (pytorch #164299/#16445):
# run a short BURST of iters, let the python process EXIT (the OS reclaims the leaked GPU memory —
# empty_cache() does NOT, the leak is in the graphCache/allocator), then RESUME from the checkpoint
# for the next burst. Loop. See memory: reference_torch212_conv_backward_leak.
#
# NOTE (resume behaviour): --init-mode resume loads the WEIGHTS but restarts the iter counter at 0 and
# the curriculum window. So each burst does `BURST` fresh-counter updates; weights accumulate across
# bursts. Judge progress by correct-rate, not the iter field (which resets each burst). motion is at
# theta=65 (not advancing), so the window reset costs nothing here.
#
# Usage:  bash burst_mps.sh            # runs NBURSTS bursts of BURST iters each
set -u
REPO=/Users/jonathanmorgan/AttentionManuscript/RViT_plus_paper_jepa_conv
VENV=/Users/jonathanmorgan/AttentionManuscript/.venv/bin/activate

# ── knobs ───────────────────────────────────────────────────────────────────
FEEDBACK=affine_ew          # affine_ew  (swap to crossattn1 for the cross-attn two-LSTM variant)
TWOLSTM="--two-lstm"        # the H1-feedback / H1->H2 / H2->heads variant + dual JEPA. "" = plain single-LSTM
DMEM=128
BURST=3000                  # iters per burst (well under the ~10-12k MPS OOM point)
NBURSTS=12                  # 12 x 3000 = 36k updates total; Ctrl-C any time, re-run to continue
CKPT="/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/motion_${FEEDBACK}_twolstm_mps"
# ─────────────────────────────────────────────────────────────────────────────

mkdir -p "$CKPT"; source "$VENV"; cd "$REPO"
for b in $(seq 1 "$NBURSTS"); do
  MODE=fresh; [ -f "$CKPT/rvit_plus_rl_latest.pt" ] && MODE=resume
  echo ">>> burst $b/$NBURSTS  mode=$MODE  ($BURST iters on MPS) $(date '+%H:%M:%S')"
  PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONUNBUFFERED=1 \
  python train_rl.py --device mps --init-mode "$MODE" \
    --T 20 --min-change-time 12 --max-change-time 12 --cell xlstm --feedback "$FEEDBACK" $TWOLSTM \
    --conv-frontend --jepa-coef 0.5 --d-mem "$DMEM" --curriculum --theta-start 65 \
    --iters "$BURST" --save-every 200 --task motion_zk --qr-kappa 10 \
    --checkpoint-dir "$CKPT"
  rc=$?
  # python has EXITED here -> MPS memory is freed by the OS -> the next burst starts with a clean allocator.
  [ $rc -ne 0 ] && echo "!! burst $b exited rc=$rc (OOM? lower BURST). checkpoint is safe; re-run to resume." && break
  echo ">>> burst $b done; checkpoint at $CKPT (resume next)"
done
