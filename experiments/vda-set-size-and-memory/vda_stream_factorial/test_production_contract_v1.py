from __future__ import annotations

import argparse
import json
import pathlib

import pytest

from experiments.vda_stream_factorial.preflight_contract_v1 import (
    CELLS,
    EXPECTED_PARAMETERS,
    RUN_CONTRACTS,
    SEEDS,
    run_preflight,
    sha256,
    validate_launcher,
    validate_request,
)


ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
DESIGN = HERE / "design_manifest.json"
CONFIG = HERE / "config_crossattn1_v1.json"
CANARY_LAUNCHER = HERE / "launch_crossattn1_canary_v1.sh"
PRODUCTION_LAUNCHER = HERE / "launch_crossattn1_production_v1.sh"


def _preflight_args(
    launcher: pathlib.Path,
    *,
    visual: int,
    memory: int,
    seed: int,
    run_kind: str,
) -> argparse.Namespace:
    return argparse.Namespace(
        project_root=ROOT,
        config=CONFIG,
        design=DESIGN,
        launcher=launcher,
        expected_config_sha256=sha256(CONFIG),
        expected_design_sha256=sha256(DESIGN),
        visual_streams=visual,
        memory_streams=memory,
        seed=seed,
        run_kind=run_kind,
        run_dir=None,
        emit_json=False,
    )


def test_design_manifest_freezes_full_matrix_banks_gates_and_evidence_boundary():
    payload = json.loads(DESIGN.read_text(encoding="utf-8"))
    assert payload["status"] == "production_contract_prepared_not_launched"
    assert payload["factor_levels"] == {
        "effective_visual_streams": [4, 100],
        "effective_memory_streams": [4, 100],
        "training_seeds": [0, 1, 2],
    }
    assert {
        (row["effective_visual_streams"], row["effective_memory_streams"])
        for row in payload["cells"]
    } == set(CELLS)
    assert payload["engineering_canaries"]["seed"] == 0
    assert payload["engineering_canaries"]["iterations"] == 50
    assert payload["production"]["iterations"] == 20_000
    assert payload["production"]["run_count"] == 12
    assert payload["fixed_scientific_contract"]["trainable_parameters"] == EXPECTED_PARAMETERS
    assert set(payload["heldout_banks"]) == {
        "common_random_numbers",
        "shared_across_all_cells_and_training_seeds",
        "calibration",
        "psychometric",
        "attention",
        "intervention",
        "binding",
    }
    assert payload["heldout_banks"]["calibration"]["disjoint_from_all_test_banks"] is True
    assert payload["factorial_contrasts"]["visual_main_effect"]
    assert payload["factorial_contrasts"]["memory_main_effect"]
    assert payload["factorial_contrasts"]["visual_by_memory_interaction"]
    assert any(
        "attention evidence" in line and "never" in line
        for line in payload["evidence_boundaries"]
    )


def test_common_config_is_bound_to_design_and_contains_no_cell_specific_choice():
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    contract = payload["contract"]
    assert contract["design_manifest_sha256"] == sha256(DESIGN)
    assert contract["effective_visual_streams"] == [4, 100]
    assert contract["effective_memory_streams"] == [4, 100]
    assert contract["seeds"] == list(SEEDS)
    assert "seed" not in payload["run"]
    assert payload["run"]["init_mode"] == "fresh"
    assert payload["ppo"]["iters"] == 20_000
    assert payload["model"]["carrier_grid"] == [10, 10]


@pytest.mark.parametrize(
    ("visual", "memory", "seed", "run_kind"),
    [
        (4, 4, 0, "canary"),
        (4, 100, 0, "production"),
        (100, 4, 1, "production"),
        (100, 100, 2, "production"),
    ],
)
def test_registered_requests_are_admitted(visual, memory, seed, run_kind):
    result = validate_request(visual, memory, seed, run_kind)
    assert result == RUN_CONTRACTS[run_kind]


@pytest.mark.parametrize(
    ("visual", "memory", "seed", "run_kind"),
    [
        (16, 4, 0, "canary"),
        (4, 16, 0, "canary"),
        (4, 4, 1, "canary"),
        (4, 4, 3, "production"),
        (4, 4, 0, "exploratory"),
    ],
)
def test_unregistered_requests_fail_closed(visual, memory, seed, run_kind):
    with pytest.raises(SystemExit, match="PREFLIGHT_FAIL"):
        validate_request(visual, memory, seed, run_kind)


@pytest.mark.parametrize(
    ("launcher", "run_kind", "iterations"),
    [
        (CANARY_LAUNCHER, "canary", 50),
        (PRODUCTION_LAUNCHER, "production", 20_000),
    ],
)
def test_launchers_freeze_science_and_bind_config_design_hashes(launcher, run_kind, iterations):
    validate_launcher(
        launcher,
        run_kind,
        {"config": sha256(CONFIG), "design": sha256(DESIGN)},
    )
    text = launcher.read_text(encoding="utf-8")
    assert f"--iters {iterations}" in text
    assert "--effective-visual-streams \"$VISUAL_STREAMS\"" in text
    assert "--effective-memory-streams \"$MEMORY_STREAMS\"" in text
    assert "--init-mode fresh" in text
    assert "--checkpoint-path" not in text
    assert "${ITERS:-" not in text
    assert "${SEED:-" not in text


def test_queue_scripts_cover_all_cells_and_preserve_run_kind():
    canary = (HERE / "queue_crossattn1_canaries_v1.sh").read_text(encoding="utf-8")
    production = (HERE / "queue_crossattn1_seed_v1.sh").read_text(encoding="utf-8")
    for text in (canary, production):
        assert 'CELLS=("4 4" "4 100" "100 4" "100 100")' in text
        assert "--expected-config-sha256 \"$EXPECTED_CONFIG_SHA256\"" in text
        assert "--expected-design-sha256 \"$EXPECTED_DESIGN_SHA256\"" in text
        assert "${ITERS:-" not in text
    assert "--run-kind canary" in canary
    assert 'bash "$LAUNCHER" "$VISUAL" "$MEMORY" 0' in canary
    assert "--run-kind production" in production
    assert 'bash "$LAUNCHER" "$VISUAL" "$MEMORY" "$SEED"' in production


def test_canary_preflight_validates_all_cell_initializations_and_seed0_trace():
    result = run_preflight(
        _preflight_args(CANARY_LAUNCHER, visual=4, memory=4, seed=0, run_kind="canary")
    )
    assert result["status"] == "preflight_passed"
    assert result["evidence_class"] == "engineering_only_not_scientific_evidence"
    assert len(set(result["paired_trainable_initialization_sha256_by_cell"].values())) == 1
    assert {
        (row["visual_projector_rank"], row["memory_projector_rank"])
        for row in result["model_checks_by_cell"].values()
    } == set(CELLS)


def test_production_preflight_validates_seed2_trace_and_terminal_contract():
    result = run_preflight(
        _preflight_args(
            PRODUCTION_LAUNCHER,
            visual=100,
            memory=100,
            seed=2,
            run_kind="production",
        )
    )
    assert result["status"] == "preflight_passed"
    assert result["request"]["iterations"] == 20_000
    assert result["request"]["terminal_iteration"] == 19_999
    assert result["model_factory"] == {
        "kind": "stream_factorial_v1",
        "effective_visual_streams": 100,
        "effective_memory_streams": 100,
        "carrier_grid": [10, 10],
    }
