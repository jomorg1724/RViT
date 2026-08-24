from __future__ import annotations

import torch

from paper_encoder import RecurrentViTxLSTM
from train_rl import build_arg_parser


def _softmax_encoder() -> RecurrentViTxLSTM:
    return RecurrentViTxLSTM(
        d_token=6,
        d_mem=8,
        n_patch=4,
        feedback="crossattn1",
        cell="transformer_memory_2layer_softmax",
        mem_heads=2,
    )


def _assert_token_simplex(x: torch.Tensor) -> None:
    assert torch.all(x >= 0)
    torch.testing.assert_close(x.sum(dim=-1), torch.ones_like(x[..., 0]))


def test_cli_exposes_softmax_memory_and_anticollapse_controls() -> None:
    args = build_arg_parser().parse_args(
        [
            "--cell",
            "transformer_memory_2layer_softmax",
            "--jepa-sinkhorn-iters",
            "3",
            "--jepa-var-coef",
            "1.0",
            "--jepa-cov-coef",
            "0.01",
        ]
    )
    assert args.cell == "transformer_memory_2layer_softmax"
    assert args.jepa_sinkhorn_iters == 3
    assert args.jepa_var_coef == 1.0
    assert args.jepa_cov_coef == 0.01


def test_both_initial_and_updated_memories_are_tokenwise_probabilities() -> None:
    encoder = _softmax_encoder()
    h1_prev, h2_prev = encoder.init_states(2)
    _assert_token_simplex(h1_prev)
    _assert_token_simplex(h2_prev)

    calls: dict[str, torch.Tensor] = {}

    def capture_h1_to_layer2(_module, args) -> None:
        calls["h1_to_layer2"] = args[0].detach().clone()

    handle = encoder.memory_transformer2.register_forward_pre_hook(capture_h1_to_layer2)
    try:
        (h1, h2), readout, _ = encoder.forward_step(
            torch.randn(2, 4, 6), (h1_prev, h2_prev)
        )
    finally:
        handle.remove()

    _assert_token_simplex(h1)
    _assert_token_simplex(h2)
    torch.testing.assert_close(calls["h1_to_layer2"], h1)
    torch.testing.assert_close(readout, h2)


def test_softmax_h1_is_used_as_next_step_visual_feedback() -> None:
    encoder = _softmax_encoder()
    state0 = encoder.init_states(2)
    state1, _, _ = encoder.forward_step(torch.randn(2, 4, 6), state0)
    calls: dict[str, torch.Tensor] = {}

    def capture_feedback(_module, args) -> None:
        calls["feedback"] = args[1].detach().clone()

    handle = encoder.attn.register_forward_pre_hook(capture_feedback)
    try:
        encoder.forward_step(torch.randn(2, 4, 6), state1)
    finally:
        handle.remove()
    torch.testing.assert_close(calls["feedback"], state1[0])
    _assert_token_simplex(calls["feedback"])


def test_sinkhorn_balances_each_layer_token_head_over_valid_samples() -> None:
    from ppo import sinkhorn_teacher_assignments

    logits = torch.full((3, 4, 2, 2, 2, 5), -6.0)
    logits[..., 0] = 6.0
    valid = torch.tensor(
        [[1, 1, 1, 1], [1, 1, 0, 0], [1, 0, 0, 0]], dtype=torch.float32
    )
    assignments = sinkhorn_teacher_assignments(logits, valid, n_iters=5)
    valid_assignments = assignments[valid.bool()]  # (N,L,P,H,K)

    torch.testing.assert_close(
        valid_assignments.sum(dim=-1), torch.ones_like(valid_assignments[..., 0]),
        atol=1e-5, rtol=1e-5,
    )
    mean_usage = valid_assignments.mean(dim=0)
    torch.testing.assert_close(
        mean_usage,
        torch.full_like(mean_usage, 1.0 / logits.shape[-1]),
        atol=1e-4,
        rtol=1e-4,
    )
    assert torch.count_nonzero(assignments[~valid.bool()]) == 0


def test_projected_feature_regularizer_penalizes_collapse_and_has_gradients() -> None:
    from ppo import jepa_variance_covariance_loss

    valid = torch.ones(4, 3)
    collapsed = torch.zeros(4, 3, 2, 4, 16, requires_grad=True)
    var_collapsed, cov_collapsed = jepa_variance_covariance_loss(collapsed, valid)
    assert var_collapsed > 0.9
    assert cov_collapsed == 0

    torch.manual_seed(0)
    diverse = torch.randn(4, 3, 2, 4, 16, requires_grad=True)
    var_diverse, cov_diverse = jepa_variance_covariance_loss(diverse, valid)
    assert var_diverse < var_collapsed
    loss = var_diverse + 0.01 * cov_diverse
    loss.backward()
    assert diverse.grad is not None
    assert torch.isfinite(diverse.grad).all()


def test_ppo_update_integrates_balancing_and_feature_regularizers() -> None:
    import copy

    import ppo
    from model import RViTPaperModel

    torch.manual_seed(4)
    model = RViTPaperModel(
        n_actions=2,
        n_quantiles=5,
        seq_len=3,
        feedback="crossattn1",
        cell="transformer_memory_2layer_softmax",
        mem_heads=2,
        d_mem=8,
        jepa_n_heads=2,
        jepa_proto_dim=5,
    )
    teacher = copy.deepcopy(model)
    for parameter in teacher.parameters():
        parameter.requires_grad_(False)
    batch = ppo.RolloutBatch(
        observations=torch.randn(2, 3, 1, 50, 50),
        actions=torch.zeros(2, 3, dtype=torch.long),
        rewards=torch.randn(2, 3),
        dones=torch.tensor([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]]),
        valid_mask=torch.ones(2, 3),
        old_log_probs=torch.zeros(2, 3),
        old_V_scalar=torch.zeros(2, 3),
        old_V_dist=torch.zeros(2, 3, 5),
        last_V_dist=torch.zeros(2, 5),
        lengths=torch.full((2,), 3, dtype=torch.long),
    )
    cfg = ppo.PPOConfig(
        n_epochs=1,
        jepa_coef=0.5,
        jepa_sinkhorn_iters=3,
        jepa_var_coef=1.0,
        jepa_cov_coef=0.01,
    )
    stats = ppo.ppo_update(
        model,
        torch.optim.Adam(model.parameters(), lr=1e-4),
        batch,
        cfg,
        train_actor=False,
        jepa_teacher=teacher,
        it=0,
    )

    assert stats["loss_jepa_ce"] > 0
    assert stats["loss_jepa_var"] > 0
    assert stats["loss_jepa_cov"] >= 0
    expected = (
        stats["loss_jepa_ce"]
        + cfg.jepa_var_coef * stats["loss_jepa_var"]
        + cfg.jepa_cov_coef * stats["loss_jepa_cov"]
    )
    torch.testing.assert_close(torch.tensor(stats["loss_jepa"]), torch.tensor(expected))
