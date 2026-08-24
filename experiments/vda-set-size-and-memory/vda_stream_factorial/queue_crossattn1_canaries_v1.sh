#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -eq 0 ]] || { printf 'USAGE: %s\n' "$0" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG="$SCRIPT_DIR/config_crossattn1_v1.json"
DESIGN="$SCRIPT_DIR/design_manifest.json"
LAUNCHER="$SCRIPT_DIR/launch_crossattn1_canary_v1.sh"
PREFLIGHT="$SCRIPT_DIR/preflight_contract_v1.py"
EXPECTED_CONFIG_SHA256="f5b62e32e40e2d8c5ee97ae71e2c520737fbf431ff4b64f82b58c718b23eb6aa"
EXPECTED_DESIGN_SHA256="8a82292d725eb7519c4c394a0ddfe9037aac2a60fa02476e1ce241e76b9daf76"
PYTHON_BIN="${PYTHON_BIN:-/workspace/rvit_venv/bin/python}"

[[ -x "$PYTHON_BIN" ]] || { printf 'ERROR: Python is not executable: %s\n' "$PYTHON_BIN" >&2; exit 2; }

CELLS=("4 4" "4 100" "100 4" "100 100")

# Fail every cell closed before launching the first engineering canary.
for CELL in "${CELLS[@]}"; do
  read -r VISUAL MEMORY <<< "$CELL"
  "$PYTHON_BIN" "$PREFLIGHT" \
    --project-root "$PROJECT_ROOT" \
    --config "$CONFIG" \
    --design "$DESIGN" \
    --launcher "$LAUNCHER" \
    --expected-config-sha256 "$EXPECTED_CONFIG_SHA256" \
    --expected-design-sha256 "$EXPECTED_DESIGN_SHA256" \
    --visual-streams "$VISUAL" \
    --memory-streams "$MEMORY" \
    --seed 0 \
    --run-kind canary
done

printf 'QUEUE_PREFLIGHT_PASS|run_kind=canary|cells=4|seed=0|evidence=engineering_only\n'
for CELL in "${CELLS[@]}"; do
  read -r VISUAL MEMORY <<< "$CELL"
  bash "$LAUNCHER" "$VISUAL" "$MEMORY" 0
done

printf 'QUEUE_COMPLETE|run_kind=canary|cells=4|seed=0|scientific_evidence=false\n'
