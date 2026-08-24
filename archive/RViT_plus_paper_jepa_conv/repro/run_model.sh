#!/bin/zsh
# Full figure set (main 2-5 + supplement 5-17) for ONE conv model, strictly sequential on MPS.
# Fig 1 (task/env) is model-independent and rendered once separately. Usage: run_model.sh <snap> <fb> <label>
set -e
VENV=/Users/jonathanmorgan/AttentionManuscript/.venv/bin/python
export OMP_NUM_THREADS=3 MKL_NUM_THREADS=3 PYTHONUNBUFFERED=1
SNAP=$1; FB=$2; LAB=$3
D=$(cd "$(dirname "$0")" && pwd)
echo "########## FULL MODEL $LAB ($FB) ##########"
echo "=== main figures ==="
$VENV $D/repro_fig2.py $FB $LAB
$VENV $D/repro_fig3.py $SNAP $FB $LAB
$VENV $D/repro_fig4.py $SNAP $FB $LAB
$VENV $D/repro_fig5.py $SNAP $FB $LAB
echo "=== supplementary figures ==="
$D/run_supp.sh $SNAP $FB $LAB full
echo "########## FULL MODEL $LAB DONE ##########"
