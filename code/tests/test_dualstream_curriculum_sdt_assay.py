from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(r"C:\Users\jomor\Documents\RViT_runs\runpod_exports\luo_dualstream_curriculum_transition_sdt_20260816\evaluation_manifest.json")


def test_assay_plan_separates_matched_measurement_from_common_theta_transfer() -> None:
    from experiments.luo2015_episodic.evaluate_dualstream_curriculum_sdt import evaluation_plan

    models = [
        {"id": "loc0", "terminal_theta": 65.0},
        {"id": "loc3", "terminal_theta": 56.0},
    ]
    plan = evaluation_plan(models, common_theta=56.0)
    assert plan["matched_frozen_policy"]["loc0"]["theta"] == 65.0
    assert plan["matched_frozen_policy"]["loc3"]["theta"] == 56.0
    assert plan["common_theta_transfer"]["theta"] == 56.0
    assert plan["common_theta_transfer"]["claim_scope"] == "difficulty_transfer_not_contract_matched_for_every_model"


def test_manifest_pins_sampled_actions_noise_and_balancing() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    contract = manifest["evaluation_contract"]
    assert contract["balanced_change_status_and_locations"] is True
    assert contract["sample_actions"] is True
    assert contract["mnemonic_noise_sd"] == 0.075
    assert contract["sensory_orientation_noise_sd"] == 5.0
    assert contract["primary_trials_per_status_per_location"] == 2000
    assert contract["common_theta_transfer"] == 56.0
    assert [(m["condition_loc"], m["terminal_theta"]) for m in manifest["models"]] == [(0, 65.0), (3, 56.0)]
