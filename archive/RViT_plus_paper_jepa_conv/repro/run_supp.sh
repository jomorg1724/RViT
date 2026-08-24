#!/bin/zsh
# Run ALL supplementary figures (5-17) for ONE model, strictly sequentially (one torch job at a time,
# OMP/MKL=3) to respect the laptop compute cap. Usage: run_supp.sh <snap> <feedback> <label> [scale]
# scale=full (default) or smoke (tiny N for a fast correctness pass).
set -e
VENV=/Users/jonathanmorgan/AttentionManuscript/.venv/bin/python
export OMP_NUM_THREADS=3 MKL_NUM_THREADS=3 PYTHONUNBUFFERED=1
SNAP=$1; FB=$2; LAB=$3; SCALE=${4:-full}
D=$(cd "$(dirname "$0")" && pwd)
if [[ $SCALE == smoke ]]; then N12=120; N16=60; MAG=18; NTR=300; NTE=250; else N12=1500; N16=300; MAG=18; NTR=3000; NTE=2000; fi
echo "=== SUPP FIGS for $LAB ($FB), scale=$SCALE ==="
$VENV $D/repro_fig567.py  $SNAP $FB $LAB
$VENV $D/repro_fig12.py   $SNAP $FB $LAB $N12
$VENV $D/repro_fig13.py   $SNAP $FB $LAB $N12
$VENV $D/repro_fig14.py   $SNAP $FB $LAB
$VENV $D/repro_fig15.py   $SNAP $FB $LAB
$VENV $D/repro_fig16.py   $SNAP $FB $LAB $N16 $MAG
$VENV $D/repro_fig17.py   $SNAP $FB $LAB
$VENV $D/repro_fig8_11.py $SNAP $FB $LAB $NTR $NTE
echo "=== DONE $LAB ==="
