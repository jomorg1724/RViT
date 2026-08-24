from __future__ import annotations

import torch
import numpy as np

from model import RViTPaperModel
from ppo import (
    PPOConfig,
    actor_critic_from_teacher_memory_ste,
    collect_episodes,
    straight_through_teacher_representation,
)
from train_rl import build_arg_parser


def _make_model() -> RViTPaperModel:
    return RViTPaperModel(
        n_actions=2,
        n_quantiles=5,
        seq_len=7,
        feedback="crossattn1",
        cell="transformer_memory_2layer_softmax_modern",
        mem_heads=4,
        jepa_n_heads=4,
        jepa_proto_dim=256,
        d_mem=128,
        conv_frontend=True,
        grid_rows=2,
        grid_cols=2,
        image_size=50,
    )


def test_teacher_forward_student_backward_ste_contract() -> None:
    student = torch.randn(2, 3, 4, 128, requires_grad=True)
    teacher = torch.randn_like(student, requires_grad=True)

    routed = straight_through_teacher_representation(student, teacher)

    assert torch.allclose(routed.detach(), teacher.detach(), atol=1e-6, rtol=0.0)
    routed.square().sum().backward()
    assert student.grad is not None
    assert torch.allclose(student.grad, 2.0 * teacher.detach(), atol=2e-6, rtol=0.0)
    assert teacher.grad is None


def test_actor_critic_heads_use_teacher_forward_and_train_student_backward() -> None:
    torch.manual_seed(7)
    model = _make_model()
    student = torch.randn(2, 3, 4, 128, requires_grad=True)
    teacher = torch.randn_like(student, requires_grad=True)

    routed = straight_through_teacher_representation(student, teacher)
    routed_out = model.heads_from_memory_sequence(routed)
    teacher_out = model.heads_from_memory_sequence(teacher.detach())

    for key in ("actor_logits_seq", "q_dist_seq", "V_dist_seq", "V_scalar_seq"):
        assert torch.allclose(
            routed_out[key].detach(), teacher_out[key].detach(), atol=2e-7, rtol=0.0
        )

    loss = routed_out["actor_logits_seq"].square().mean() + routed_out["q_dist_seq"].square().mean()
    loss.backward()

    assert student.grad is not None and student.grad.abs().sum() > 0
    assert teacher.grad is None
    assert any(p.grad is not None and p.grad.abs().sum() > 0 for p in model.actor_head.parameters())
    assert any(p.grad is not None and p.grad.abs().sum() > 0 for p in model.critic_head.parameters())


def test_teacher_actor_critic_ste_is_explicit_and_off_by_default() -> None:
    assert PPOConfig().teacher_actor_critic_ste is False
    parser = build_arg_parser()
    assert parser.parse_args([]).teacher_actor_critic_ste is False
    assert parser.parse_args(["--teacher-actor-critic-ste"]).teacher_actor_critic_ste is True


def test_two_level_route_uses_teacher_h2_forward_and_student_h2_backward() -> None:
    torch.manual_seed(11)
    model = _make_model()
    student_cells = torch.randn(2, 3, 2, 4, 128, requires_grad=True)
    teacher_cells = torch.randn_like(student_cells, requires_grad=True)

    routed = actor_critic_from_teacher_memory_ste(model, student_cells, teacher_cells)
    direct = model.heads_from_memory_sequence(teacher_cells[:, :, 1].detach())
    for key in direct:
        assert torch.allclose(routed[key].detach(), direct[key].detach(), atol=2e-7, rtol=0.0)

    (routed["actor_logits_seq"].square().mean() + routed["q_dist_seq"].square().mean()).backward()
    assert student_cells.grad is not None
    assert student_cells.grad[:, :, 0].abs().sum() == 0
    assert student_cells.grad[:, :, 1].abs().sum() > 0
    assert teacher_cells.grad is None


class _OneStepEnv:
    def reset(self):
        return np.zeros((2, 2, 3), dtype=np.float32)

    def step(self, action: int):
        return self.reset(), float(action == 1), True, {}


class _RolloutModel:
    n_quantiles = 1
    seq_len = 1

    def __init__(self, representation_value: float):
        self.representation_value = representation_value

    def eval(self):
        return self

    def init_states(self, batch_size: int, device=None):
        return 0

    def rl_step(self, x_t, states, **kwargs):
        rec = torch.full((x_t.shape[0], 1), self.representation_value, device=x_t.device)
        actor, q, vd, vs = self._run_heads(rec)
        return {
            "new_states": states + 1,
            "rec": rec,
            "actor_logits": actor,
            "critic_q_dist": q,
            "V_dist": vd,
            "V_scalar": vs,
        }

    def _run_heads(self, rec):
        score = rec.mean(dim=-1)
        actor = torch.stack((-100.0 * score, 100.0 * score), dim=-1)
        q = torch.zeros(rec.shape[0], 2, 1, device=rec.device)
        vd = torch.zeros(rec.shape[0], 1, device=rec.device)
        vs = torch.zeros(rec.shape[0], device=rec.device)
        return actor, q, vd, vs


def test_rollout_actions_use_teacher_representation_with_online_heads() -> None:
    student = _RolloutModel(representation_value=-1.0)
    teacher = _RolloutModel(representation_value=1.0)
    batch, stats = collect_episodes(
        student,
        _OneStepEnv(),
        n_episodes=4,
        device=torch.device("cpu"),
        representation_teacher=teacher,
    )
    assert torch.equal(batch.actions[:, 0], torch.ones(4, dtype=torch.long))
    assert stats["rollout/correct_rate"] == 1.0
