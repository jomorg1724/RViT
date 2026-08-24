"""Contract tests for the paired VDA4 memory-noise pilot.

These tests deliberately distinguish engineering integrity from scientific
evidence.  Passing them can establish that the registered sham/noise pair is
constructed and evaluated as specified; it cannot establish a cueing or
attention effect.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from paper_encoder import SpatialXLSTM


ROOT = Path(__file__).resolve().parents[1]
HERE = (
    ROOT
    / "experiments"
    / "vda4_memory_noise"
    / "grid2x2_crossattn1_pilot_v1"
)
DESIGN = HERE / "design_manifest.json"
CONFIG = HERE / "config_v1.json"
CANARY_LAUNCHER = HERE / "launch_canary_v1.sh"
PRODUCTION_LAUNCHER = HERE / "launch_production_v1.sh"


def _zero_state(batch: int = 2, patches: int = 4, d_mem: int = 8):
    return tuple(torch.zeros(batch, patches, d_mem) for _ in range(4))


def _normalise_shell(text: str) -> str:
    return re.sub(r"\\\s*\n\s*", " ", text)


def _evaluator():
    from experiments.vda4_memory_noise.grid2x2_crossattn1_pilot_v1 import (
        evaluate_paired_v1,
    )

    return evaluate_paired_v1


def test_design_registry_freezes_a_two_condition_paired_seed0_pilot() -> None:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))

    assert design["schema_version"] == 1
    assert design["status"] == "paired_pilot_contract_prepared_not_launched"
    fixed = design["fixed_scientific_contract"]
    assert fixed == {
        **fixed,
        "task": "vda4",
        "active_items": 4,
        "stimulus_grid": [2, 2],
        "patch_memory_grid": [2, 2],
        "tokens": 4,
        "image_size": 50,
        "cell": "xlstm",
        "feedback": "crossattn1",
        "d_mem": 128,
        "memory_decay": 1.0,
        "training_seed": 0,
        "initialization": "fresh",
        "iterations": 20_000,
        "terminal_iteration": 19_999,
        "no_early_stopping": True,
    }
    assert [
        (row["condition_id"], row["memory_noise_std"], row["seed"], row["required"])
        for row in design["registered_runs"]
    ] == [
        ("noise0p0", 0.0, 0, True),
        ("noise0p5", 0.5, 0, True),
    ]
    pairing = design["pairing_contract"]
    assert pairing["queue_order"] == [0.0, 0.5]
    assert pairing["same_named_trainable_initialization_sha256"] is True
    assert pairing["same_initial_environment_seed"] is True
    assert pairing["same_training_environment_trace"] is False
    assert "not asserted to be common-random-number" in pairing["training_trace_limitation"]
    assert pairing["no_result_dependent_stopping"] is True
    assert pairing["inference_unit"] == "one paired seed-0 pilot; directional and descriptive only"
    # Equal seed/initialization does not make training trajectories bitwise CRN:
    # memory noise may alter actions and therefore episode lengths.  CRN pairing
    # is required for the independent held-out trial banks below, not claimed for
    # the endogenous training path.
    assert design["heldout_evaluation"]["common_random_numbers"] is True
    reset_diagnostic = design["initial_environment_reset_diagnostic"]
    assert reset_diagnostic["evidence_class"] == (
        "engineering_only_not_a_training_trajectory_claim"
    )
    assert "does not imply identical trial sequences" in reset_diagnostic["claim_boundary"]


def test_design_registers_common_random_numbers_source_separation_and_falsifiers() -> None:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    heldout = design["heldout_evaluation"]

    assert heldout["prerequisite"].startswith("Both registered runs pass terminal validation")
    assert heldout["common_random_numbers"] is True
    assert heldout["attention_bank"]["display"].startswith(
        "Always show visual-key and memory-key maps separately"
    )
    assert heldout["online_noise_modes"]["matched_trained_condition"].startswith(
        "Compare the noise0p0 checkpoint"
    )
    asymmetry = design["manipulation"]["trainer_asymmetry"]
    assert "noisy-student/noise-off-teacher" in asymmetry
    assert "target_model.forward_rl_sequence" in asymmetry
    assert "jepa_teacher.forward_rl_sequence" in asymmetry
    measurement = design["attention_measurement_contract"]
    assert "four visual keys followed by four recurrent-memory keys" in measurement["native_shape"]
    assert "pV_j=(1/N)*sum_i A[i,j]" in measurement["column_average"]
    assert "algebraically identical" in measurement["regional_max"]
    assert design["admission_gates"]["paired_admission"].startswith(
        "No paired scientific comparison"
    )
    nulls = "\n".join(design["hypothesis"]["null_or_disconfirming_patterns"])
    assert "criterion" in nulls
    assert "floor/ceiling" in nulls
    assert "seed-0 direction fails to replicate" in nulls
    assert any("not attention" in item for item in design["evidence_boundaries"])


def test_design_and_evaluator_freeze_the_same_validities_locations_and_trial_budgets() -> None:
    """Every registered held-out cell must be realizable without hidden truncation."""
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    evaluation = _evaluator()
    heldout = design["heldout_evaluation"]

    np.testing.assert_array_equal(
        evaluation.VALIDITIES,
        np.asarray(heldout["psychometric_bank"]["validities"], dtype=np.float64),
    )
    assert heldout["psychometric_bank"]["primary_in_distribution_validities"] == [
        0.25,
        0.5,
        0.75,
    ]
    assert "out-of-distribution" in heldout["psychometric_bank"]["validity_one_status"]
    assert evaluation.PRIMARY_VALIDITY in evaluation.VALIDITIES
    assert evaluation.LOCATIONS == (0, 1, 2, 3)
    expected_invalid_pairs = tuple(
        (cue, change)
        for cue in evaluation.LOCATIONS
        for change in evaluation.LOCATIONS
        if cue != change
    )
    assert evaluation.ORDERED_INVALID_PAIRS == expected_invalid_pairs
    assert len(expected_invalid_pairs) == 12

    budgets = {
        "calibration": heldout["adaptive_nonsaturation_calibration"][
            "aggregate_trials_per_magnitude_condition"
        ],
        "psychometric": heldout["psychometric_bank"][
            "aggregate_trials_per_validity_magnitude_condition"
        ],
        "attention": heldout["attention_bank"]["aggregate_trials_per_condition"],
        "intervention": heldout["intervention_bank"][
            "aggregate_trials_per_role_source_dose_condition"
        ],
    }
    assert budgets == {
        "calibration": 120,
        "psychometric": 300,
        "attention": 240,
        "intervention": 240,
    }
    assert all(count % 12 == 0 for count in budgets.values())

    parser_defaults = vars(evaluation.build_parser().parse_args([
        "--clean-run-dir", "clean",
        "--clean-checkpoint", "clean/rvit_paper_vda4_final.pt",
        "--clean-expected-sha256", "0" * 64,
        "--noisy-run-dir", "noisy",
        "--noisy-checkpoint", "noisy/rvit_paper_vda4_final.pt",
        "--noisy-expected-sha256", "1" * 64,
        "--output-root", "out",
    ]))
    assert {
        "calibration": parser_defaults["calibration_trials"],
        "psychometric": parser_defaults["psychometric_trials"],
        "attention": parser_defaults["attention_trials"],
        "intervention": parser_defaults["intervention_trials"],
    } == budgets

    calibration_rule = heldout["adaptive_nonsaturation_calibration"]["selection_rule"]
    assert "one common focal magnitude once across all four" in calibration_rule
    assert "every cell lies in [0.20,0.80]" in calibration_rule
    assert "target response rate 0.60" in calibration_rule
    assert "never select per checkpoint" in calibration_rule
    intervention = heldout["intervention_bank"]
    assert intervention["sources"] == ["visual", "memory", "both"]
    assert intervention["doses"] == [0.0, 0.25, 0.5, 0.75, 1.0]
    assert "b=6*(2*alpha-1)" in intervention["intervention_formula"]


@pytest.mark.parametrize("condition", ["valid", "nochange"])
def test_spatial_allocator_balances_valid_and_nochange_over_all_four_cues(
    condition: str,
) -> None:
    evaluation = _evaluator()
    strata = evaluation.allocate_spatial_strata(120, condition)

    assert strata == tuple((location, location, 30) for location in range(4))
    assert sum(count for _cue, _change, count in strata) == 120


def test_spatial_allocator_balances_forced_invalid_over_all_ordered_pairs() -> None:
    evaluation = _evaluator()
    strata = evaluation.allocate_spatial_strata(120, "invalid")

    assert tuple((cue, change) for cue, change, _count in strata) == (
        evaluation.ORDERED_INVALID_PAIRS
    )
    assert {count for _cue, _change, count in strata} == {10}
    assert sum(count for _cue, _change, count in strata) == 120
    with pytest.raises(ValueError, match="divisible by 12"):
        evaluation.allocate_spatial_strata(122, "invalid")
    with pytest.raises(ValueError, match="unsupported spatial condition"):
        evaluation.allocate_spatial_strata(120, "fixed_top_left_example")


def test_counterbalanced_rollout_preserves_every_spatial_identity_and_bank_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evaluation = _evaluator()
    captured: list[dict[str, object]] = []

    def fake_make_trial_bank(_core, _registry, **kwargs):
        captured.append(dict(kwargs))
        count = int(kwargs["trials"])
        return evaluation.TrialBank(
            bank_id=f"bank-{len(captured)}",
            videos=np.zeros((count, 7, 3, 2, 2), dtype=np.float32),
            policy_uniforms=np.full((count, 7), 0.5, dtype=np.float32),
            memory_noise_seed=1000 + len(captured),
            registry=dict(kwargs),
        )

    def fake_paired_rollouts(bank, _models, cells, **_kwargs):
        count = int(bank.registry["trials"])
        return {
            cell.label: {
                "press": np.zeros((count, 7), dtype=np.int64),
                "memory_noise_seed": bank.memory_noise_seed,
                "memory_noise_draw_calls": 0,
                "memory_noise_schedule_sha256": "disabled",
                "runtime_noise_contract": {"inject_memory_noise": False},
            }
            for cell in cells
        }

    monkeypatch.setattr(evaluation, "make_trial_bank", fake_make_trial_bank)
    monkeypatch.setattr(evaluation, "paired_rollouts", fake_paired_rollouts)
    cells = (evaluation.EvaluationCell("clean", "clean", 0.0, 0.0),)
    result = evaluation.counterbalanced_rollouts(
        SimpleNamespace(),
        {},
        {"clean": SimpleNamespace()},
        cells,
        namespace="test",
        assay="spatial_contract",
        condition="invalid",
        total_trials=120,
        displayed_validity=0.75,
        magnitude=18.0,
    )["clean"]

    assert len(captured) == 12
    assert {(item["cue_index"], item["change_index"]) for item in captured} == set(
        evaluation.ORDERED_INVALID_PAIRS
    )
    assert {item["displayed_validity"] for item in captured} == {0.75}
    assert {item["trials"] for item in captured} == {10}
    observed_pairs = list(zip(result["cue_index"], result["change_index"], strict=True))
    for pair in evaluation.ORDERED_INVALID_PAIRS:
        assert observed_pairs.count(pair) == 10
    assert result["press"].shape == (120, 7)


def test_evaluator_contains_no_legacy_single_validity_or_fixed_location_shortcuts() -> None:
    """Primary assays must use the registered validity/location axes, not one old example."""
    source = (HERE / "evaluate_paired_v1.py").read_text(encoding="utf-8")
    for legacy_name in (
        "DISPLAYED_VALIDITY",
        "CUE_INDEX",
        "VALID_CHANGE_INDEX",
        "INVALID_CHANGE_INDEX",
    ):
        assert re.search(rf"\b{legacy_name}\b", source) is None


def test_figure_inventory_has_both_formats_and_never_fuses_visual_with_memory(
    tmp_path: Path,
) -> None:
    evaluation = _evaluator()

    assert evaluation.FIGURE_STEMS == {
        "psychometric_sdt": "psychometric_rt_sdt",
        "visual_maps": "attention_visual_column_score_maps",
        "memory_maps": "attention_memory_column_score_maps",
        "source_timecourses": "attention_source_timecourses",
        "interventions": "causal_intervention_dose_response",
    }
    paths = evaluation.expected_figure_paths(tmp_path)
    assert len(paths) == 10
    assert len(set(paths)) == 10
    assert {path.suffix for path in paths} == {".png", ".pdf"}
    assert all(path.parent == tmp_path / "figures" for path in paths)
    visual = {path.name for path in paths if "visual" in path.name}
    memory = {path.name for path in paths if "memory" in path.name}
    assert visual == {
        "attention_visual_column_score_maps.png",
        "attention_visual_column_score_maps.pdf",
    }
    assert memory == {
        "attention_memory_column_score_maps.png",
        "attention_memory_column_score_maps.pdf",
    }
    assert visual.isdisjoint(memory)


def test_figure_smoke_writes_valid_hash_manifested_png_and_pdf_pairs(
    tmp_path: Path,
) -> None:
    evaluation = _evaluator()
    cells = tuple(
        evaluation.EvaluationCell(label, model, train_std, eval_std)
        for label, model, train_std, eval_std in (
            ("train0_eval0", "train0", 0.0, 0.0),
            ("train0_eval0p5", "train0", 0.0, 0.5),
            ("train0p5_eval0", "train0p5", 0.5, 0.0),
            ("train0p5_eval0p5", "train0p5", 0.5, 0.5),
        )
    )
    psych_shape = (4, len(evaluation.VALIDITIES), len(evaluation.MAGNITUDES), 2)
    psych = {
        "response_rate": np.full(psych_shape, 0.55, dtype=np.float64),
        "mean_rt": np.full(psych_shape, 5.5, dtype=np.float64),
        "dprime": np.full(psych_shape, 1.1, dtype=np.float64),
        "criterion": np.zeros(psych_shape, dtype=np.float64),
    }

    spatial = {
        condition: evaluation.allocate_spatial_strata(12, condition)
        for condition in ("valid", "invalid", "nochange")
    }
    cue_index = np.stack(
        [
            np.concatenate([np.full(count, cue) for cue, _change, count in spatial[condition]])
            for condition in ("valid", "invalid", "nochange")
        ]
    ).astype(np.int64)
    change_index = np.stack(
        [
            np.concatenate(
                [np.full(count, change) for _cue, change, count in spatial[condition]]
            )
            for condition in ("valid", "invalid", "nochange")
        ]
    ).astype(np.int64)
    rng = np.random.default_rng(20260803)
    raw = rng.uniform(0.01, 0.25, size=(4, 3, 12, 7, 4, 4))
    attention = {
        "visual_attention_full_4x4": raw,
        "memory_attention_full_4x4": raw[..., ::-1].copy(),
        "cue_index": cue_index,
        "change_index": change_index,
    }

    intervention_labels = ["natural"] + [
        f"{role}|{source}|alpha={float(dose):g}"
        for role in evaluation.INTERVENTION_ROLES
        for source in evaluation.INTERVENTION_SOURCES
        for dose in evaluation.INTERVENTION_DOSES
    ]
    intervention = {
        "intervention_labels": np.asarray(intervention_labels),
        "dprime": rng.normal(1.0, 0.1, size=(4, len(intervention_labels), 2)),
    }

    evaluation.create_figures(
        tmp_path / "figures", psych, attention, intervention, cells, 18.0
    )
    expected = evaluation.expected_figure_paths(tmp_path)
    assert all(path.is_file() and path.stat().st_size > 1_000 for path in expected)
    for path in expected:
        magic = path.read_bytes()[:8]
        if path.suffix == ".png":
            assert magic == b"\x89PNG\r\n\x1a\n"
        else:
            assert magic[:5] == b"%PDF-"

    manifest = evaluation.build_manifest(tmp_path, {"test_fixture": True})
    manifested = {record["path"] for record in manifest["files"]}
    assert manifested == {path.relative_to(tmp_path).as_posix() for path in expected}


def test_graded_intervention_targets_visual_and_memory_keys_separately() -> None:
    evaluation = _evaluator()
    assert evaluation.intervention_clamp(
        "natural", cue_index=0, change_index=3
    ) is None

    visual_suppress = evaluation.intervention_clamp(
        "true_change", cue_index=0, change_index=3, source="visual", dose=0.0
    )
    memory_neutral = evaluation.intervention_clamp(
        "true_change", cue_index=0, change_index=3, source="memory", dose=0.5
    )
    both_boost = evaluation.intervention_clamp(
        "true_change", cue_index=0, change_index=3, source="both", dose=1.0
    )
    assert visual_suppress == {"3": -6.0}
    assert memory_neutral == {"7": 0.0}
    assert both_boost == {"3": 6.0, "7": 6.0}
    assert set(visual_suppress).isdisjoint(memory_neutral)

    cued_wrong = evaluation.intervention_clamp(
        "cued_wrong", cue_index=0, change_index=3, source="both", dose=0.0
    )
    neutral_control = evaluation.intervention_clamp(
        "neutral_control", cue_index=0, change_index=3, source="both", dose=0.0
    )
    assert cued_wrong == {"0": -6.0, "4": -6.0}
    assert neutral_control == {"1": -6.0, "5": -6.0}
    with pytest.raises(ValueError, match="unregistered intervention dose"):
        evaluation.intervention_clamp(
            "true_change", cue_index=0, change_index=3, source="both", dose=0.6
        )


def test_config_is_common_to_both_levels_and_bound_to_the_design_hash() -> None:
    from experiments.vda4_memory_noise.grid2x2_crossattn1_pilot_v1 import (
        preflight_contract_v1 as preflight,
    )

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    contract = config["contract"]
    assert contract["design_manifest_sha256"] == preflight.sha256(DESIGN)
    assert contract["memory_noise_std_levels"] == [0.0, 0.5]
    assert contract["seeds"] == [0]
    assert contract["patch_memory_grid"] == [2, 2]
    assert config["model"]["memory_noise_std_levels"] == [0.0, 0.5]
    assert "memory_noise_std" not in config["run"]
    assert config["run"]["init_mode"] == "fresh"
    assert config["run"]["checkpoint_path"] == ""
    assert config["ppo"]["iters"] == 20_000


@pytest.mark.parametrize(
    ("noise_std", "seed", "run_kind"),
    [(0.25, 0, "canary"), (0.5, 1, "production"), (0.0, 0, "exploratory")],
)
def test_preflight_rejects_unregistered_requests(
    noise_std: float, seed: int, run_kind: str
) -> None:
    from experiments.vda4_memory_noise.grid2x2_crossattn1_pilot_v1 import (
        preflight_contract_v1 as preflight,
    )

    with pytest.raises(SystemExit, match="PREFLIGHT_FAIL"):
        preflight.validate_request(noise_std, seed, run_kind)


def _preflight_args(
    launcher: Path,
    *,
    noise_std: float,
    run_kind: str,
    expected_config_sha256: str | None = None,
    expected_design_sha256: str | None = None,
) -> argparse.Namespace:
    from experiments.vda4_memory_noise.grid2x2_crossattn1_pilot_v1 import (
        preflight_contract_v1 as preflight,
    )

    return argparse.Namespace(
        project_root=ROOT,
        config=CONFIG,
        design=DESIGN,
        launcher=launcher,
        expected_config_sha256=(
            expected_config_sha256
            if expected_config_sha256 is not None
            else preflight.sha256(CONFIG)
        ),
        expected_design_sha256=(
            expected_design_sha256
            if expected_design_sha256 is not None
            else preflight.sha256(DESIGN)
        ),
        memory_noise_std=noise_std,
        seed=0,
        run_kind=run_kind,
        run_dir=None,
        emit_json=False,
    )


def test_preflight_fails_closed_on_a_hash_mismatch_before_model_construction() -> None:
    from experiments.vda4_memory_noise.grid2x2_crossattn1_pilot_v1 import (
        preflight_contract_v1 as preflight,
    )

    with pytest.raises(SystemExit, match="config SHA-256 mismatch"):
        preflight.run_preflight(
            _preflight_args(
                CANARY_LAUNCHER,
                noise_std=0.0,
                run_kind="canary",
                expected_config_sha256="0" * 64,
            )
        )


def test_production_preflight_verifies_both_models_pairing_and_noise_semantics() -> None:
    from experiments.vda4_memory_noise.grid2x2_crossattn1_pilot_v1 import (
        preflight_contract_v1 as preflight,
    )

    result = preflight.run_preflight(
        _preflight_args(PRODUCTION_LAUNCHER, noise_std=0.5, run_kind="production")
    )

    assert result["status"] == "preflight_passed"
    assert result["request"] == {
        "condition_id": "noise0p5",
        "memory_noise_std": 0.5,
        "seed": 0,
        "run_kind": "production",
        "iterations": 20_000,
        "terminal_iteration": 19_999,
    }
    initializations = result["paired_trainable_initialization_sha256_by_condition"]
    assert set(initializations) == {"noise0p0", "noise0p5"}
    assert len(set(initializations.values())) == 1
    checks = result["model_checks_by_condition"]
    assert checks["noise0p0"]["memory_noise_std"] == 0.0
    assert checks["noise0p5"]["memory_noise_std"] == 0.5
    assert {record["tokens"] for record in checks.values()} == {4}
    semantics = result["noise_semantics"]
    assert semantics["noise0_injection_is_noop"] is True
    assert semantics["noise0p5_disabled_matches_noise0"] is True
    assert semantics["noise0p5_reproducible_after_rng_reset"] is True
    assert semantics["noise0p5_changes_with_rng_seed"] is True
    assert semantics["checked_state_elements"] == 3 * 4 * 128


@pytest.mark.parametrize(
    ("launcher", "run_kind", "iterations"),
    [
        (CANARY_LAUNCHER, "canary", 50),
        (PRODUCTION_LAUNCHER, "production", 20_000),
    ],
)
def test_launchers_require_explicit_level_and_seed_and_never_resume_or_overwrite(
    launcher: Path, run_kind: str, iterations: int
) -> None:
    from experiments.vda4_memory_noise.grid2x2_crossattn1_pilot_v1 import (
        preflight_contract_v1 as preflight,
    )

    preflight.validate_launcher(
        launcher,
        run_kind,
        {"config": preflight.sha256(CONFIG), "design": preflight.sha256(DESIGN)},
    )
    text = launcher.read_text(encoding="utf-8")
    normal = _normalise_shell(text)
    assert '[[ "$#" -eq 2 ]]' in text
    assert 'MEMORY_NOISE_STD="$1"' in text
    assert 'SEED="$2"' in text
    assert 'case "$MEMORY_NOISE_STD" in 0.0|0.5)' in text
    assert '--memory-noise-std "$MEMORY_NOISE_STD"' in normal
    assert '--seed "$SEED"' in normal
    assert f"--iters {iterations}" in normal
    assert "--init-mode fresh" in normal
    assert 'RUN_STAMP="$(' in text
    assert 'mkdir "$CHECKPOINT_DIR"' in text
    assert 'mkdir -p "$CHECKPOINT_DIR"' not in text
    for forbidden in ("--checkpoint-path", "--resume", "rm -rf", "${MEMORY_NOISE_STD:-"):
        assert forbidden not in text


def test_queues_cover_both_levels_unconditionally_and_bind_one_runtime() -> None:
    for queue_name, launcher_name, run_kind in (
        ("queue_canaries_v1.sh", "launch_canary_v1.sh", "canary"),
        ("queue_seed0_pair_v1.sh", "launch_production_v1.sh", "production"),
    ):
        text = (HERE / queue_name).read_text(encoding="utf-8")
        assert 'for MEMORY_NOISE_STD in 0.0 0.5; do' in text
        assert f'LAUNCHER="$SCRIPT_DIR/{launcher_name}"' in text
        assert f"--run-kind {run_kind}" in _normalise_shell(text)
        assert 'export VDA_PAIR_RUNTIME_SHA256="$(runtime_fingerprint)"' in text
        assert 'bash "$LAUNCHER" "$MEMORY_NOISE_STD" 0' in text
        assert "cueing" not in text.lower()
        assert "attention" not in text.lower()
        assert "theta" not in text.lower()
        assert "rm -rf" not in text


def _terminal_payload(run_dir: Path, noise_std: float, producer: dict[str, str]) -> dict:
    model_kwargs = {
        "n_actions": 2,
        "n_quantiles": 5,
        "init_action_bias": [0.0, -1.5],
        "seq_len": 7,
        "feedback": "crossattn1",
        "two_lstm": False,
        "cell": "xlstm",
        "jepa_n_heads": 4,
        "jepa_proto_dim": 256,
        "frame_repeat": 1,
        "d_mem": 128,
        "memory_decay": 1.0,
        "memory_noise_std": noise_std,
        "conv_frontend": True,
        "grid_rows": 2,
        "grid_cols": 2,
        "image_size": 50,
    }
    training_args = {
        "task": "vda4",
        "T": 7,
        "frame_repeat": 1,
        "min_change_time": 5,
        "max_change_time": 5,
        "noise": 5.0,
        "patch_grid_rows": 2,
        "patch_grid_cols": 2,
        "effective_visual_streams": None,
        "effective_memory_streams": None,
        "cell": "xlstm",
        "two_lstm": False,
        "feedback": "crossattn1",
        "d_mem": 128,
        "memory_decay": 1.0,
        "memory_noise_std": noise_std,
        "conv_frontend": True,
        "n_actions": 2,
        "n_quantiles": 5,
        "init_action_bias": [0.0, -1.5],
        "jepa_coef": 0.5,
        "jepa_heads": 4,
        "jepa_proto_dim": 256,
        "jepa_same_time": False,
        "jepa_tau_student": 0.1,
        "jepa_tau_teacher_start": 0.04,
        "jepa_tau_teacher_end": 0.07,
        "jepa_tau_warmup": 300,
        "jepa_center_momentum": 0.9,
        "jepa_ema_decay": 0.996,
        "curriculum": True,
        "theta_start": 65.0,
        "curr_window": 1000,
        "curr_threshold": 0.85,
        "curr_step": 3.0,
        "curr_floor": 8.0,
        "lr": 0.0003,
        "gamma": 0.95,
        "entropy_coef": 0.01,
        "ema_decay": 0.995,
        "buffer_capacity": 1000,
        "qr_kappa": 1.0,
        "mpo_temperature": 0.1,
        "init_mode": "fresh",
        "start_iteration": 0,
        "iters": 20_000,
        "schedule_final_iteration": 19_999,
        "episodes_per_iter": 8,
        "save_every": 50,
        "log_every": 1,
        "seed": 0,
        "device": "cuda",
        "checkpoint_path": None,
        "expected_parent_sha256": None,
        "allow_schedule_overrun_resume": False,
        "experiment_launcher": str(PRODUCTION_LAUNCHER.resolve()),
        "config": str(CONFIG.resolve()),
        "checkpoint_dir": str(run_dir.resolve()),
    }
    return {
        "checkpoint_schema_version": 3,
        "iter": 19_999,
        "task": "vda4",
        "model_kwargs": model_kwargs,
        "training_args": training_args,
        "initialization_contract": {"mode": "fresh"},
        "resume_contract": {
            "task": "vda4",
            "episodes_per_iter": 8,
            "schedule_final_iteration": 19_999,
            "model_kwargs": model_kwargs,
            "producer_sha256": producer,
        },
        "replay_buffer_persisted": False,
        "resume_fidelity": "replay_excluded_trainer_state",
        "producer_sha256": producer,
        "model_state_dict": {"weight": torch.tensor([1.0, 2.0])},
        "optimizer_state_dict": {"state": {0: {"exp_avg": torch.tensor([0.1])}}},
        "target_model_state_dict": {"weight": torch.tensor([1.0, 2.0])},
        "jepa_teacher_state_dict": {"weight": torch.tensor([1.0, 2.0])},
        "environment_state": {"theta": 8.0},
        "rolling_correct": [0.9, 0.95],
        "rolling_return": [2.0, 2.5],
    }


def _write_terminal_metrics(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("iter", "loss", "env/theta"))
        writer.writeheader()
        for iteration in range(20_000):
            writer.writerow({"iter": iteration, "loss": 0.25, "env/theta": 8.0})


@pytest.fixture(scope="module")
def terminal_noise_run(tmp_path_factory: pytest.TempPathFactory) -> Path:
    from experiments.vda4_memory_noise.grid2x2_crossattn1_pilot_v1 import (
        preflight_contract_v1 as preflight,
    )

    root = tmp_path_factory.mktemp("vda4_memory_noise_terminal")
    run = root / "vda4_memory_noise_grid2x2_crossattn1_noise0p5_seed0_production_v1_fixture"
    run.mkdir()
    launch_contract = preflight.run_preflight(
        argparse.Namespace(
            **{
                **vars(
                    _preflight_args(
                        PRODUCTION_LAUNCHER,
                        noise_std=0.5,
                        run_kind="production",
                    )
                ),
                "run_dir": run,
            }
        )
    )
    payload = _terminal_payload(run, 0.5, launch_contract["producer_sha256"])
    torch.save(payload, run / "rvit_paper_vda4_final.pt")
    torch.save(payload, run / "rvit_plus_rl_latest.pt")
    _write_terminal_metrics(run / "metrics.csv")
    (run / "train.log").write_text(
        "[checkpoint] saved replay-excluded trainer state to final\n"
        "[paper] replay-excluded trainer checkpoint saved; iters logged=20000\n",
        encoding="utf-8",
    )
    (run / "launch_contract.json").write_text(
        json.dumps(launch_contract, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (run / "runtime_identity.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "pair_id": "production_20260803T000000Z_abcdef123456",
                "runtime_sha256": "a" * 64,
                "gpu_uuid": "GPU-test-fixture",
                "recorded_at_utc": "2026-08-03T00:00:00+00:00",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return run


def _validate_terminal_fixture(run: Path) -> dict:
    from experiments.vda4_memory_noise.grid2x2_crossattn1_pilot_v1 import (
        validate_terminal_v1 as terminal,
    )

    return terminal.validate_terminal(
        run,
        expected_memory_noise_std=0.5,
        project_root=ROOT,
        launcher=PRODUCTION_LAUNCHER,
        config=CONFIG,
        design=DESIGN,
    )


def test_terminal_validator_accepts_only_training_integrity_not_science(
    terminal_noise_run: Path,
) -> None:
    result = _validate_terminal_fixture(terminal_noise_run)

    assert result["status"] == "validated_terminal_training_artifacts_only"
    assert result["condition_id"] == "noise0p5"
    assert result["memory_noise_std"] == pytest.approx(0.5)
    assert result["metrics"]["rows"] == 20_000
    assert result["final_latest_semantically_equal"] is True
    assert result["scientific_behavior_evaluated"] is False
    assert "not cueing" in result["claim_boundary"]


def test_terminal_validator_rejects_an_exact_noise_level_mismatch(
    terminal_noise_run: Path, tmp_path: Path
) -> None:
    mutated = tmp_path / terminal_noise_run.name
    shutil.copytree(terminal_noise_run, mutated)
    for filename in ("rvit_paper_vda4_final.pt", "rvit_plus_rl_latest.pt"):
        path = mutated / filename
        payload = torch.load(path, map_location="cpu", weights_only=False)
        payload["model_kwargs"]["memory_noise_std"] = 0.0
        payload["training_args"]["memory_noise_std"] = 0.0
        payload["resume_contract"]["model_kwargs"]["memory_noise_std"] = 0.0
        payload["training_args"]["checkpoint_dir"] = str(mutated.resolve())
        torch.save(payload, path)

    with pytest.raises(ValueError, match="memory_noise_std"):
        _validate_terminal_fixture(mutated)


def test_terminal_validator_rejects_a_nonterminal_metrics_ledger(
    terminal_noise_run: Path, tmp_path: Path
) -> None:
    mutated = tmp_path / terminal_noise_run.name
    shutil.copytree(terminal_noise_run, mutated)
    lines = (mutated / "metrics.csv").read_text(encoding="utf-8").splitlines()
    (mutated / "metrics.csv").write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="19999 rows; expected 20000"):
        _validate_terminal_fixture(mutated)


def test_std_half_uses_one_independent_standard_normal_draw_per_memory_scalar(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The destructive interference is elementwise, not one draw per slot/batch."""
    torch.manual_seed(20260803)
    clean = SpatialXLSTM(input_dim=3, d_mem=8, memory_decay=1.0, memory_noise_std=0.0)
    noisy = SpatialXLSTM(input_dim=3, d_mem=8, memory_decay=1.0, memory_noise_std=0.5)
    noisy.load_state_dict(clean.state_dict())
    inputs = torch.randn(2, 4, 3)
    state = _zero_state()
    _, clean_c, clean_n, _ = clean(inputs, *state)

    draws = torch.arange(clean_c.numel(), dtype=clean_c.dtype).reshape_as(clean_c)
    observed_shapes: list[torch.Size] = []

    def fake_randn_like(tensor: torch.Tensor) -> torch.Tensor:
        observed_shapes.append(tensor.shape)
        return draws.to(tensor)

    monkeypatch.setattr(torch, "randn_like", fake_randn_like)
    _, noisy_c, _, _ = noisy(inputs, *state, inject_memory_noise=True)

    assert observed_shapes == [clean_c.shape]
    expected_delta = 0.5 * (clean_n + 1e-8) * draws
    torch.testing.assert_close(noisy_c - clean_c, expected_delta)
    assert torch.unique((noisy_c - clean_c).reshape(-1)).numel() > 4


def test_zero_std_sham_is_exact_and_does_not_consume_noise_rng(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The sham condition differs only in registered sigma, not hidden RNG use."""
    torch.manual_seed(17)
    sham = SpatialXLSTM(input_dim=3, d_mem=8, memory_decay=1.0, memory_noise_std=0.0)
    inputs = torch.randn(2, 4, 3)
    state = _zero_state()
    expected = sham(inputs, *state, inject_memory_noise=False)

    monkeypatch.setattr(
        torch,
        "randn_like",
        lambda tensor: (_ for _ in ()).throw(AssertionError("sham consumed noise RNG")),
    )
    actual = sham(inputs, *state, inject_memory_noise=True)
    for expected_tensor, actual_tensor in zip(expected, actual):
        torch.testing.assert_close(actual_tensor, expected_tensor)


def test_evaluator_activates_the_registered_noise_during_heldout_rollout() -> None:
    evaluation = _evaluator()

    class Cell:
        memory_noise_std = -1.0

    class Encoder:
        feedback = "crossattn1"
        cell = "xlstm"
        two_lstm = False
        memory_noise_std = -1.0
        lstm = Cell()

    class Model:
        encoder = Encoder()

    model = Model()
    record = evaluation.set_runtime_memory_noise(model, eval_noise_std=0.5)

    assert model.encoder.memory_noise_std == pytest.approx(0.5)
    assert model.encoder.lstm.memory_noise_std == pytest.approx(0.5)
    assert record["encoder_memory_noise_std"] == pytest.approx(0.5)
    assert record["lstm_memory_noise_std"] == pytest.approx(0.5)
    assert record["inject_memory_noise"] is True


def test_rollout_passes_the_eval_noise_flag_on_every_recurrent_step() -> None:
    evaluation = _evaluator()

    class Cell:
        memory_noise_std = -1.0

    class Encoder:
        feedback = "crossattn1"
        cell = "xlstm"
        two_lstm = False
        memory_noise_std = -1.0
        lstm = Cell()

    class Model:
        encoder = Encoder()

        def __init__(self) -> None:
            self.inject_flags: list[bool] = []

        def init_states(self, batch_size: int, device: torch.device):
            return None

        def rl_step(
            self,
            frame: torch.Tensor,
            state,
            *,
            return_attn: bool,
            attn_clamp,
            inject_memory_noise: bool,
        ) -> dict:
            self.inject_flags.append(inject_memory_noise)
            if inject_memory_noise:
                torch.randn_like(torch.zeros(frame.shape[0], 4, 128, device=frame.device))
            return {
                "new_states": None,
                "actor_logits": torch.zeros(frame.shape[0], 2, device=frame.device),
            }

    bank = evaluation.TrialBank(
        bank_id="mock",
        videos=torch.zeros(2, 7, 3, 50, 50),
        policy_uniforms=np.full((2, 7), 0.5, dtype=np.float32),
        memory_noise_seed=12345,
        registry={},
    )
    noisy_model = Model()
    noisy = evaluation.rollout_sampled(noisy_model, bank, eval_noise_std=0.5)
    assert noisy_model.inject_flags == [True] * 7
    assert noisy["memory_noise_draw_calls"] == 7
    assert noisy["runtime_noise_contract"]["inject_memory_noise"] is True
    assert noisy["memory_noise_schedule_sha256"] != "disabled"

    clean_model = Model()
    clean = evaluation.rollout_sampled(clean_model, bank, eval_noise_std=0.0)
    assert clean_model.inject_flags == [False] * 7
    assert clean["memory_noise_draw_calls"] == 0
    assert clean["runtime_noise_contract"]["inject_memory_noise"] is False
    assert clean["memory_noise_schedule_sha256"] == "disabled"

    paired_models = {"first": Model(), "second": Model()}
    paired_cells = (
        evaluation.EvaluationCell("first_noisy", "first", 0.0, 0.5),
        evaluation.EvaluationCell("second_noisy", "second", 0.5, 0.5),
    )
    paired = evaluation.paired_rollouts(bank, paired_models, paired_cells)
    assert (
        paired["first_noisy"]["memory_noise_schedule_sha256"]
        == paired["second_noisy"]["memory_noise_schedule_sha256"]
    )
    np.testing.assert_array_equal(
        paired["first_noisy"]["actions"], paired["second_noisy"]["actions"]
    )


def test_evaluator_keeps_visual_and_memory_key_maps_separate_before_reduction() -> None:
    evaluation = _evaluator()

    # leading axes are trial and time; final axes are query=4 and joint key=8
    visual_row = np.asarray([0.01, 0.02, 0.03, 0.04], dtype=np.float64)
    memory_row = np.asarray([0.10, 0.20, 0.30, 0.30], dtype=np.float64)
    visual = np.broadcast_to(visual_row, (2, 3, 4, 4)).copy()
    memory = np.broadcast_to(memory_row, (2, 3, 4, 4)).copy()
    raw = np.concatenate((visual, memory), axis=-1)

    observed_visual, observed_memory = evaluation.split_source_attention(raw)
    np.testing.assert_array_equal(observed_visual, visual)
    np.testing.assert_array_equal(observed_memory, memory)

    visual_scores = evaluation.column_averaged_patch_scores(observed_visual)
    memory_scores = evaluation.column_averaged_patch_scores(observed_memory)
    np.testing.assert_allclose(visual_scores, visual.mean(axis=-2))
    np.testing.assert_allclose(memory_scores, memory.mean(axis=-2))
    assert visual_scores.shape == memory_scores.shape == (2, 3, 4)
    assert np.all(memory_scores > visual_scores)


def test_source_attention_metrics_preserve_trials_frames_and_named_reductions() -> None:
    evaluation = _evaluator()

    # Two trials and three frames must survive every reduction.  Every query has
    # source-specific raw patch mass [.04,.08,.12,.16], so source share=.4 and
    # conditional patch allocation=[.1,.2,.3,.4].
    per_query = np.asarray([0.04, 0.08, 0.12, 0.16], dtype=np.float64)
    source = np.broadcast_to(per_query, (2, 3, 4, 4)).copy()

    metrics = evaluation.source_attention_metrics(source, target_index=2)

    assert metrics["patch_score"].shape == (2, 3, 4)
    assert metrics["source_share"].shape == (2, 3)
    assert metrics["conditional_patch_score"].shape == (2, 3, 4)
    assert np.allclose(metrics["patch_score"], per_query)
    assert np.allclose(metrics["source_share"], 0.4)
    assert np.allclose(metrics["conditional_patch_score"], per_query / per_query.sum())
    assert np.allclose(metrics["target_raw"], 0.12)
    assert np.allclose(metrics["target_conditional"], 0.3)
    assert np.allclose(metrics["distractor_conditional_mean"], 0.7 / 3.0)
    assert np.allclose(metrics["target_selectivity"], 0.3 - 0.7 / 3.0)
    assert np.allclose(metrics["max_raw_patch"], 0.16)
    assert np.allclose(metrics["max_conditional_patch"], 0.4)
    assert np.allclose(metrics["normalized_max_conditional"], 1.6)
    assert np.all((metrics["normalized_entropy"] >= 0.0) & (metrics["normalized_entropy"] <= 1.0))
    np.testing.assert_allclose(
        metrics["effective_locations"],
        np.exp(metrics["normalized_entropy"] * np.log(4.0)),
        rtol=1e-6,
    )
