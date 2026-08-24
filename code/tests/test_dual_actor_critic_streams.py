from __future__ import annotations

import torch

import ppo
from model import RViTPaperModel
from train_rl import build_arg_parser


def _model(*, jepa: bool = True) -> RViTPaperModel:
    return RViTPaperModel(
        n_actions=2,
        n_quantiles=5,
        seq_len=3,
        feedback="crossattn1",
        cell="xlstm",
        d_mem=8,
        jepa_n_heads=2 if jepa else 0,
        jepa_proto_dim=5,
        dual_actor_critic_streams=True,
    )


def _has_nonzero_grad(module: torch.nn.Module) -> bool:
    return any(
        parameter.grad is not None and torch.count_nonzero(parameter.grad) > 0
        for parameter in module.parameters()
    )


def _has_any_grad(module: torch.nn.Module) -> bool:
    return any(parameter.grad is not None for parameter in module.parameters())


def test_cli_accepts_dual_actor_critic_streams() -> None:
    args = build_arg_parser().parse_args(["--dual-actor-critic-streams"])

    assert args.dual_actor_critic_streams is True


def test_dual_streams_are_parameter_independent_and_route_separate_memories() -> None:
    model = _model()

    assert model.front is not model.critic_front
    assert model.encoder is not model.critic_encoder
    actor_parameter_ids = {id(parameter) for parameter in model.front.parameters()}
    actor_parameter_ids.update(id(parameter) for parameter in model.encoder.parameters())
    critic_parameter_ids = {id(parameter) for parameter in model.critic_front.parameters()}
    critic_parameter_ids.update(id(parameter) for parameter in model.critic_encoder.parameters())
    assert actor_parameter_ids.isdisjoint(critic_parameter_ids)

    actor_inputs: list[torch.Tensor] = []
    critic_inputs: list[torch.Tensor] = []
    actor_handle = model.actor_head.register_forward_pre_hook(
        lambda _module, args: actor_inputs.append(args[0].detach().clone())
    )
    critic_handle = model.critic_head.register_forward_pre_hook(
        lambda _module, args: critic_inputs.append(args[0].detach().clone())
    )
    try:
        sequence = model.forward_rl_sequence(
            torch.randn(2, 3, 1, 50, 50), return_cell=True
        )
    finally:
        actor_handle.remove()
        critic_handle.remove()

    assert sequence["cell_seq"].shape == (2, 3, 2, 4, 8)
    actor_memory = sequence["cell_seq"][:, :, 0].flatten(2)
    critic_memory = sequence["cell_seq"][:, :, 1].flatten(2)
    torch.testing.assert_close(torch.stack(actor_inputs, dim=1), actor_memory)
    torch.testing.assert_close(torch.stack(critic_inputs, dim=1), critic_memory)
    assert sequence["actor_logits_seq"].shape == (2, 3, 2)
    assert sequence["q_dist_seq"].shape == (2, 3, 2, 5)


def test_actor_and_critic_objectives_have_isolated_stream_gradients() -> None:
    model = _model(jepa=False)
    observations = torch.randn(2, 3, 1, 50, 50)

    actor_loss = model.forward_rl_sequence(observations)["actor_logits_seq"].square().mean()
    actor_loss.backward()
    assert _has_nonzero_grad(model.front)
    assert _has_nonzero_grad(model.encoder)
    assert _has_nonzero_grad(model.actor_head)
    assert not _has_any_grad(model.critic_front)
    assert not _has_any_grad(model.critic_encoder)
    assert not _has_any_grad(model.critic_head)

    model.zero_grad(set_to_none=True)
    critic_loss = model.forward_rl_sequence(observations)["q_dist_seq"].square().mean()
    critic_loss.backward()
    assert _has_nonzero_grad(model.critic_front)
    assert _has_nonzero_grad(model.critic_encoder)
    assert _has_nonzero_grad(model.critic_head)
    assert not _has_any_grad(model.front)
    assert not _has_any_grad(model.encoder)
    assert not _has_any_grad(model.actor_head)


def test_dual_streams_have_independent_jepa_heads_centers_and_gradients() -> None:
    model = _model()
    sequence = model.forward_rl_sequence(
        torch.randn(2, 3, 1, 50, 50), return_cell=True
    )
    student = model.jepa_logits(sequence["cell_seq"])

    assert len(model.jepa_branch_heads) == 2
    assert model.jepa_branch_names == ("actor", "critic")
    assert model.jepa_loss_multiplier == 2.0
    assert student.shape == (2, 3, 2, 4, 2, 5)
    assert model.jepa_center.shape == (2, 4, 2, 5)

    teacher = torch.randn_like(student)
    loss, branch_losses = ppo.structured_jepa_loss(
        teacher[:, 1:],
        student[:, :-1],
        model.jepa_center,
        torch.ones(2, 2),
        tau_teacher=0.07,
        tau_student=0.1,
    )
    assert branch_losses.shape == (2,)
    torch.testing.assert_close(loss, branch_losses.mean())
    loss.backward()
    assert all(_has_nonzero_grad(head) for head in model.jepa_branch_heads)
