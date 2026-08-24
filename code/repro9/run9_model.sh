#!/bin/zsh
set -e
VENV=/Users/jonathanmorgan/AttentionManuscript/.venv/bin/python
export OMP_NUM_THREADS=3 MKL_NUM_THREADS=3 PYTHONUNBUFFERED=1
SNAP=$1; FB=$2; LAB=$3
D=$(cd "$(dirname "$0")" && pwd)
echo "########## GRID9 FULL $LAB ($FB) ##########"
$VENV $D/repro9_fig2.py $FB $LAB
$VENV $D/repro9_fig3.py $SNAP $FB $LAB
$VENV $D/repro9_fig4.py $SNAP $FB $LAB
$VENV $D/repro9_fig5.py $SNAP $FB $LAB
$D/run9_supp.sh $SNAP $FB $LAB full
echo "########## GRID9 FULL $LAB DONE ##########"
