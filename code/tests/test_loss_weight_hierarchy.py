from __future__ import annotations

import pytest
import torch
import json
from pathlib import Path

from ppo import PPOConfig, compose_total_loss
from train_rl import build_arg_parser


def test_actor_critic_jepa_weight_order_and_no_behavior_cloning() -> None:
    cfg = PPOConfig(
        actor_coef=0.01,
        value_coef=0.5,
        jepa_coef=0.6,
        entropy_coef=0.0,
        contrastive_coef=0.0,
        bc_alpha=0.0,
    )
    actor = torch.tensor(2.0, requires_grad=True)
    critic = torch.tensor(3.0, requires_grad=True)
    jepa = torch.tensor(4.0, requires_grad=True)
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

    assert total.item() == pytest.approx(0.01 * 2.0 + 0.5 * 3.0 + 0.6 * 4.0)
    assert actor.grad.item() == pytest.approx(0.01)
    assert critic.grad.item() == pytest.approx(0.5)
    assert jepa.grad.item() == pytest.approx(0.6)
    assert cfg.actor_coef < cfg.value_coef < cfg.jepa_coef
    assert cfg.bc_alpha == 0.0


def test_cli_accepts_explicit_actor_weight_and_zero_behavior_cloning() -> None:
    args = build_arg_parser().parse_args(
        ["--actor-coef", "0.01", "--bc-alpha", "0.0"]
    )
    assert args.actor_coef == pytest.approx(0.01)
    assert args.bc_alpha == pytest.approx(0.0)


def test_behavior_cloning_is_off_by_default_in_ppo_config() -> None:
    assert PPOConfig().bc_alpha == 0.0
    config = json.loads(
        (Path(__file__).resolve().parents[1] / "config" / "default.json").read_text()
    )
    assert config["ppo"]["bc_alpha"] == 0.0
