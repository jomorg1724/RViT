from __future__ import annotations

import json
from pathlib import Path

import pytest
import torch

from ppo import PPOConfig, compose_total_loss


EXPERIMENT = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "vda4_transformer_memory"
    / "grid2x2_modern_c1_a01_j0001_t003005_nobc_s0_v1"
)


def test_critic_actor_jepa_weight_order_on_representative_raw_losses() -> None:
    cfg = PPOConfig(
        value_coef=1.0,
        actor_coef=0.1,
        jepa_coef=0.001,
        entropy_coef=0.0,
        contrastive_coef=0.0,
        bc_alpha=0.0,
    )
    actor = torch.tensor(0.27, requires_grad=True)
    critic = torch.tensor(0.08, requires_grad=True)
    jepa = torch.tensor(5.8, requires_grad=True)
    zero = torch.tensor(0.0)

    total = compose_total_loss(
        loss_policy=actor,
        loss_value=critic,
        loss_entropy=zero,
        loss_contrastive=zero,
        loss_jepa=jepa,
        cfg=cfg,
    )
    total.backward()

    actor_weighted = cfg.actor_coef * actor.item()
    critic_weighted = cfg.value_coef * critic.item()
    jepa_weighted = cfg.jepa_coef * jepa.item()
    assert critic_weighted > actor_weighted > jepa_weighted
    assert critic.grad.item() == pytest.approx(1.0)
    assert actor.grad.item() == pytest.approx(0.1)
    assert jepa.grad.item() == pytest.approx(0.001)
    assert cfg.bc_alpha == 0.0


def test_critic_dominant_experiment_contract() -> None:
    launcher = (EXPERIMENT / "launch_local_v1.sh").read_text(encoding="utf-8")
    manifest = json.loads((EXPERIMENT / "design_manifest.json").read_text(encoding="utf-8"))

    required = (
        "--cell transformer_memory_2layer_softmax_modern",
        "--gamma 0.95",
        "--value-coef 1.0",
        "--actor-coef 0.1",
        "--jepa-coef 0.001",
        "--bc-alpha 0.0",
        "--jepa-tau-student 0.1",
        "--jepa-tau-teacher-start 0.03",
        "--jepa-tau-teacher-end 0.05",
        "--jepa-ema-decay 0.996",
        "--curr-window 1000",
        "--curr-threshold 0.85",
        "--curr-step 3.0",
        "--curr-floor 8.0",
        "--init-mode fresh",
    )
    for fragment in required:
        assert fragment in launcher

    assert manifest["objective_weights"] == {
        "critic": 1.0,
        "actor": 0.1,
        "jepa": 0.001,
        "ordering": "critic > actor > JEPA",
        "behavior_cloning_alpha": 0.0,
    }
    assert manifest["controlled_delta"] == {
        "critic_coefficient": {"from": 0.5, "to": 1.0},
        "actor_coefficient": {"from": 0.01, "to": 0.1},
        "jepa_coefficient": {"from": 0.6, "to": 0.001},
    }
    assert manifest["training"]["gamma"] == 0.95
    assert manifest["architecture"]["student_memory_output"] == "tokenwise_feature_softmax"
    assert manifest["jepa"]["teacher_ema_decay"] == 0.996
