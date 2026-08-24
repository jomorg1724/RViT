from __future__ import annotations

import json
from pathlib import Path


EXPERIMENT = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "vda4_transformer_memory"
    / "grid2x2_crossattn1_2layer_softmax_modern_gamma095_jepa06_teacher003005_seed0_v1"
)


def test_jepa_weight_and_teacher_sharpening_experiment_contract() -> None:
    launcher = (EXPERIMENT / "launch_local_v1.sh").read_text(encoding="utf-8")
    manifest = json.loads((EXPERIMENT / "design_manifest.json").read_text(encoding="utf-8"))

    required = (
        "--cell transformer_memory_2layer_softmax_modern",
        "--gamma 0.95",
        "--jepa-coef 0.6",
        "--actor-coef 0.01",
        "--value-coef 0.5",
        "--bc-alpha 0.0",
        "--jepa-tau-student 0.1",
        "--jepa-tau-teacher-start 0.03",
        "--jepa-tau-teacher-end 0.05",
        "--jepa-tau-warmup 300",
        "--jepa-ema-decay 0.996",
        "--jepa-sinkhorn-iters 3",
        "--jepa-var-coef 1.0",
        "--jepa-cov-coef 0.01",
        "--curr-window 1000",
        "--curr-threshold 0.85",
        "--curr-step 3.0",
        "--curr-floor 8.0",
        "--init-mode fresh",
    )
    for fragment in required:
        assert fragment in launcher

    assert manifest["controlled_delta"] == {
        "jepa_coefficient": {"from": 0.5, "to": 0.6},
        "teacher_temperature": {"from": [0.04, 0.07], "to": [0.03, 0.05]},
    }
    assert manifest["training"]["gamma"] == 0.95
    assert manifest["objective_weights"] == {
        "actor": 0.01,
        "critic": 0.5,
        "jepa": 0.6,
        "ordering": "actor < critic < JEPA",
        "behavior_cloning_alpha": 0.0,
    }
    assert manifest["jepa"]["coefficient_on_total"] == 0.6
    assert manifest["jepa"]["teacher_temperature_start"] == 0.03
    assert manifest["jepa"]["teacher_temperature_end"] == 0.05
    assert manifest["jepa"]["teacher_ema_decay"] == 0.996
    assert manifest["architecture"]["student_memory_output"] == "tokenwise_feature_softmax"
    assert manifest["curriculum"]["update"] == (
        "theta=max(theta_floor, theta-3deg) only when window correctness>=0.85"
    )
