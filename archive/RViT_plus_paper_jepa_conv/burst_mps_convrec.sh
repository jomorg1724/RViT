#!/usr/bin/env bash
# Burst-train the CONV-RECURRENT ("visual-cortex" ConvMGU) motion variant on the Mac GPU (MPS), around the
# Apple-MPS allocator leak (pytorch #164299/#16445): run a BURST, let python EXIT (OS reclaims leaked GPU
# memory), RESUME from the checkpoint, loop. See memory: reference_torch212_conv_backward_leak, and the
# design in CONVMGU_DESIGN.md / project_convmgu_visual_cortex.
#
# DELTA vs burst_mps.sh: adds --conv-recurrent (a ConvMGU after stage1, retention 0.30 ≈ 1-past-step,
# giving the perceptual stage a fast recurrence so a single frame is no longer the whole percept — the
# hypothesis for why plain motion parks at always-wait). Distinct CKPT dir so it never touches the plain run.
#
# Usage:  bash burst_mps_convrec.sh
set -u
REPO=/Users/jonathanmorgan/AttentionManuscript/RViT_plus_paper_jepa_conv
VENV=/Users/jonathanmorgan/AttentionManuscript/.venv/bin/activate

# ── knobs ───────────────────────────────────────────────────────────────────
FEEDBACK=affine_ew          # affine_ew (swap to crossattn1 for the cross-attn two-LSTM variant)
TWOLSTM="--two-lstm"        # H1-feedback / H1->H2 / H2->heads + dual JEPA. "" = plain single-LSTM
DMEM=128
RETAIN=0.3                  # ConvMGU init retention (~1 past step); the cell can LEARN longer if it helps
BURST=3000                  # iters per burst (well under the ~10-12k MPS OOM point)
NBURSTS=12                  # 12 x 3000 = 36k updates; Ctrl-C any time, re-run to continue
CKPT="/Users/jonathanmorgan/AttentionManuscript/battery_sweep_results/motion_convrec_${FEEDBACK}_twolstm_mps"
# ─────────────────────────────────────────────────────────────────────────────

mkdir -p "$CKPT"; source "$VENV"; cd "$REPO"
for b in $(seq 1 "$NBURSTS"); do
  MODE=fresh; [ -f "$CKPT/rvit_plus_rl_latest.pt" ] && MODE=resume
  echo ">>> convrec burst $b/$NBURSTS  mode=$MODE  ($BURST iters on MPS) $(date '+%H:%M:%S')"
  PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONUNBUFFERED=1 \
  python train_rl.py --device mps --init-mode "$MODE" \
    --T 20 --min-change-time 12 --max-change-time 12 --cell xlstm --feedback "$FEEDBACK" $TWOLSTM \
    --conv-frontend --conv-recurrent --conv-rec-stage 1 --conv-rec-retain "$RETAIN" \
    --jepa-coef 0.5 --d-mem "$DMEM" --curriculum --theta-start 65 \
    --iters "$BURST" --save-every 200 --task motion_zk --qr-kappa 10 \
    --checkpoint-dir "$CKPT"
  rc=$?
  # python has EXITED here -> MPS memory freed by the OS -> next burst starts with a clean allocator.
  [ $rc -ne 0 ] && echo "!! convrec burst $b exited rc=$rc (OOM? lower BURST). checkpoint safe; re-run to resume." && break
  echo ">>> convrec burst $b done; checkpoint at $CKPT (resume next)"
done
