#!/bin/zsh
set -e
VENV=/Users/jonathanmorgan/AttentionManuscript/.venv/bin/python
export OMP_NUM_THREADS=3 MKL_NUM_THREADS=3 PYTHONUNBUFFERED=1
SNAP=$1; FB=$2; LAB=$3; SCALE=${4:-full}
D=$(cd "$(dirname "$0")" && pwd)
if [[ $SCALE == smoke ]]; then N12=120; N16=60; NTR=300; NTE=250; else N12=1500; N16=300; NTR=3000; NTE=2000; fi
$VENV $D/repro9_fig567.py  $SNAP $FB $LAB
$VENV $D/repro9_fig12.py   $SNAP $FB $LAB $N12
$VENV $D/repro9_fig13.py   $SNAP $FB $LAB $N12
$VENV $D/repro9_fig14.py   $SNAP $FB $LAB
$VENV $D/repro9_fig15.py   $SNAP $FB $LAB
$VENV $D/repro9_fig16.py   $SNAP $FB $LAB $N16 18
$VENV $D/repro9_fig17.py   $SNAP $FB $LAB
$VENV $D/repro9_fig8_11.py $SNAP $FB $LAB $NTR $NTE
