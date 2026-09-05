#!/bin/bash
# Full analysis battery: belief per-step checkpoint (c99, theta=41)
set -x
cd "C:/Users/jomor/OneDrive/Desktop/RViT_plus_paper_jepa_grid9-20260718T193411Z-1-001/RViT/KimiDecayVDAConvRecurrentTF"
CKPT="C:/Users/jomor/Documents/RViT_runs/vda16_kda_token_belief_perstep_seed0/kda_convmem_latest.pt"
AN="C:/Users/jomor/Documents/RViT_runs/vda16_kda_token_belief_perstep_seed0/analysis"
PY="C:/Python310/python.exe"

$PY -u analyze_kda_gates.py --checkpoint "$CKPT" --out-dir "$AN/gates"
$PY -u psychometric_kda.py "$CKPT" "$AN/psychometrics"
for t in att_vis ah1 az ah; do
  $PY -u psychometric_kda_microstim.py "$CKPT" "$AN/microstim_$t" --target "$t" --stim-cell 3
done
$PY -u psychometric_kda_hemilesion.py "$CKPT" "$AN/hemilesion"
echo BATTERY_DONE
