from __future__ import annotations

import json
from pathlib import Path

from envs import make_env


EXPERIMENT = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "vda4_transformer_memory"
    / "grid2x2_crossattn1_2layer_softmax_modern_gamma1_seed0_v1"
)


def test_corrected_theta_curriculum_uses_nonoverlapping_subtractive_windows() -> None:
    env = make_env(
        "vda4",
        curriculum=True,
        theta=65.0,
        curr_window=4,
        curr_threshold=0.75,
        curr_step=3.0,
        theta_floor=8.0,
    )
    for correct in (True, True, True, False):
        env._update_curriculum(correct)
    assert env.theta == 62.0
    assert env._recent_correct == []

    for correct in (True, True, False, False):
        env._update_curriculum(correct)
    assert env.theta == 62.0
    assert env._recent_correct == []

    env.theta = 9.0
    for correct in (True, True, True, True):
        env._update_curriculum(correct)
    assert env.theta == 8.0


def test_registered_experiment_is_gamma_one_modern_softmax_jepa_contract() -> None:
    launcher = (EXPERIMENT / "launch_local_v1.sh").read_text(encoding="utf-8")
    manifest = json.loads((EXPERIMENT / "design_manifest.json").read_text(encoding="utf-8"))

    required_launcher_fragments = (
        "--cell transformer_memory_2layer_softmax_modern",
        "--feedback crossattn1",
        "--d-mem 128",
        "--mem-heads 4",
        "--gamma 1.0",
        "--jepa-coef 0.5",
        "--jepa-ema-decay 0.996",
        "--jepa-sinkhorn-iters 3",
        "--jepa-var-coef 1.0",
        "--jepa-cov-coef 0.01",
        "--ema-decay 0.995",
        "--curriculum",
        "--theta-start 65.0",
        "--curr-window 1000",
        "--curr-threshold 0.85",
        "--curr-step 3.0",
        "--curr-floor 8.0",
        "--init-mode fresh",
    )
    for fragment in required_launcher_fragments:
        assert fragment in launcher

    assert manifest["architecture"]["cell"] == "transformer_memory_2layer_softmax_modern"
    assert manifest["architecture"]["memory_heads_per_layer"] == 4
    assert manifest["architecture"]["student_memory_output"] == "tokenwise_feature_softmax"
    assert manifest["training"]["gamma"] == 1.0
    assert manifest["training"]["discounting"] == "none"
    assert manifest["jepa"]["teacher_ema_decay"] == 0.996
    assert manifest["curriculum"] == {
        "enabled": True,
        "theta_start_deg": 65.0,
        "window_trials": 1000,
        "correctness_threshold": 0.85,
        "theta_step_deg": 3.0,
        "theta_floor_deg": 8.0,
        "window_semantics": "non-overlapping valid completed trials",
        "update": "theta=max(theta_floor, theta-3deg) only when window correctness>=0.85",
    }
