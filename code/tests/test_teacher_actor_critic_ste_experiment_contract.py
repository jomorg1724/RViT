from __future__ import annotations

import json
from pathlib import Path


EXPERIMENT = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "vda4_transformer_memory"
    / "grid2x2_modern_teacherac_ste_c1_a01_j0001_s0_v1"
)


def test_teacher_actor_critic_ste_experiment_contract() -> None:
    launcher = (EXPERIMENT / "launch_local_v1.sh").read_text(encoding="utf-8")
    manifest = json.loads((EXPERIMENT / "design_manifest.json").read_text(encoding="utf-8"))

    for fragment in (
        "--cell transformer_memory_2layer_softmax_modern",
        "--teacher-actor-critic-ste",
        "--value-coef 1.0",
        "--actor-coef 0.1",
        "--jepa-coef 0.001",
        "--bc-alpha 0.0",
        "--jepa-heads 4",
        "--jepa-proto-dim 256",
        "--jepa-ema-decay 0.996",
        "--gamma 0.95",
        "--init-mode fresh",
    ):
        assert fragment in launcher

    assert manifest["representation_routing"] == {
        "actor_critic_forward": "detached JEPA EMA-teacher H2",
        "actor_critic_backward_representation": "online student H2 via straight-through estimator",
        "teacher_gradient": "blocked",
        "online_actor_critic_heads": "trainable",
        "rollout_representation": "JEPA EMA-teacher H2 decoded by online actor/critic heads",
    }
    assert manifest["jepa"]["temporal_targets"] == "student@t predicts EMA-teacher@t+1"
    assert manifest["jepa"]["teacher_ema_decay"] == 0.996
    assert manifest["objective_weights"] == {
        "critic": 1.0,
        "actor": 0.1,
        "jepa": 0.001,
        "behavior_cloning_alpha": 0.0,
    }
