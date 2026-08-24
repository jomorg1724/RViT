from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import torch

import ppo
from model import RViTPaperModel
from paper_encoder import CrossAttentionTransformerMemory, CrossAttentionXH, RecurrentViTxLSTM
from train_rl import build_arg_parser


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "vda4_transformer_memory"
    / "grid2x2_crossattn1_2layer_seed0_v1"
)
RESCUE_EXPERIMENT = (
    ROOT
    / "experiments"
    / "vda4_transformer_memory"
    / "grid2x2_crossattn1_2layer_frozen_trunk_head_rescue_seed0_v1"
)


def _encoder() -> RecurrentViTxLSTM:
    return RecurrentViTxLSTM(
        d_token=6,
        d_mem=8,
        n_patch=4,
        feedback="crossattn1",
        cell="transformer_memory_2layer",
        mem_heads=2,
    )


def test_cli_accepts_two_layer_transformer_memory() -> None:
    args = build_arg_parser().parse_args(
        [
            "--task",
            "vda4",
            "--cell",
            "transformer_memory_2layer",
            "--feedback",
            "crossattn1",
        ]
    )
    assert args.cell == "transformer_memory_2layer"


def test_cli_accepts_frozen_trunk_probe_initialization() -> None:
    args = build_arg_parser().parse_args(["--init-mode", "frozen_trunk_probe"])
    assert args.init_mode == "frozen_trunk_probe"


def test_frozen_trunk_probe_loads_only_trunk_and_freezes_it(tmp_path: Path) -> None:
    import hashlib

    from train_rl import load_frozen_trunk_probe_parent

    kwargs = dict(
        n_actions=2,
        n_quantiles=5,
        init_action_bias=[0.0, -1.5],
        seq_len=7,
        feedback="crossattn1",
        cell="transformer_memory_2layer",
        mem_heads=2,
        jepa_n_heads=0,
        d_mem=8,
        conv_frontend=True,
        grid_rows=2,
        grid_cols=2,
        image_size=50,
    )
    torch.manual_seed(11)
    parent = RViTPaperModel(**kwargs)
    with torch.no_grad():
        for name, parameter in parent.named_parameters():
            if name.startswith(("front.", "encoder.")):
                parameter.add_(0.25)
            elif name.startswith(("actor_head.", "critic_head.")):
                parameter.fill_(7.0)

    path = tmp_path / "parent.pt"
    torch.save(
        {
            "iter": 123,
            "task": "vda4",
            "model_kwargs": kwargs,
            "model_state_dict": parent.state_dict(),
        },
        path,
    )
    digest = hashlib.sha256(path.read_bytes()).hexdigest()

    torch.manual_seed(22)
    probe = RViTPaperModel(**kwargs)
    fresh_heads = {
        name: tensor.detach().clone()
        for name, tensor in probe.state_dict().items()
        if name.startswith(("actor_head.", "critic_head."))
    }

    info, contract = load_frozen_trunk_probe_parent(
        probe,
        str(path),
        expected_sha256=digest,
        device=torch.device("cpu"),
    )

    parent_state = parent.state_dict()
    probe_state = probe.state_dict()
    for name in probe_state:
        if name.startswith(("front.", "encoder.")):
            assert torch.equal(probe_state[name], parent_state[name]), name
        elif name.startswith(("actor_head.", "critic_head.")):
            assert torch.equal(probe_state[name], fresh_heads[name]), name
            if name != "critic_head.taus":
                assert not torch.equal(probe_state[name], parent_state[name]), name

    assert all(
        parameter.requires_grad == name.startswith(("actor_head.", "critic_head."))
        for name, parameter in probe.named_parameters()
    )
    assert info["checkpoint_iteration"] == 123
    assert contract["loaded_prefixes"] == ["front.", "encoder."]
    assert contract["fresh_trainable_prefixes"] == ["actor_head.", "critic_head."]


def test_two_layer_memory_routes_h1_to_vision_and_h2_to_second_memory() -> None:
    encoder = _encoder()
    h1_prev, h2_prev = encoder.init_states(2)
    calls: dict[str, tuple[torch.Tensor, ...]] = {}

    handles = [
        encoder.attn.register_forward_pre_hook(
            lambda _module, args: calls.setdefault("vision", tuple(x.detach().clone() for x in args[:2]))
        ),
        encoder.memory_transformer1.register_forward_pre_hook(
            lambda _module, args: calls.setdefault("memory1", tuple(x.detach().clone() for x in args[:2]))
        ),
        encoder.memory_transformer2.register_forward_pre_hook(
            lambda _module, args: calls.setdefault("memory2", tuple(x.detach().clone() for x in args[:2]))
        ),
    ]
    try:
        next_state, readout, visual_attention = encoder.forward_step(
            torch.randn(2, 4, 6), (h1_prev, h2_prev), return_attn=True
        )
    finally:
        for handle in handles:
            handle.remove()

    h1, h2 = next_state
    assert isinstance(encoder.attn, CrossAttentionXH)
    assert isinstance(encoder.memory_transformer1, CrossAttentionTransformerMemory)
    assert isinstance(encoder.memory_transformer2, CrossAttentionTransformerMemory)
    torch.testing.assert_close(calls["vision"][1], h1_prev)
    torch.testing.assert_close(calls["memory1"][1], h1_prev)
    torch.testing.assert_close(calls["memory2"][0], h1)
    torch.testing.assert_close(calls["memory2"][1], h2_prev)
    torch.testing.assert_close(readout, h2)
    assert visual_attention.shape == (2, 4, 8)


def test_both_memory_layers_start_with_distinct_learned_slots() -> None:
    encoder = _encoder()
    h1, h2 = encoder.init_states(3)

    assert isinstance(encoder.initial_memory1, torch.nn.Parameter)
    assert isinstance(encoder.initial_memory2, torch.nn.Parameter)
    assert not torch.allclose(h1[:, 0], h1[:, 1])
    assert not torch.allclose(h2[:, 0], h2[:, 1])
    torch.testing.assert_close(h1[0], h1[1])
    torch.testing.assert_close(h2[0], h2[1])


def test_actor_critic_read_h2_and_sequence_exposes_h1_and_h2() -> None:
    model = RViTPaperModel(
        n_actions=2,
        n_quantiles=5,
        seq_len=3,
        feedback="crossattn1",
        cell="transformer_memory_2layer",
        mem_heads=2,
        d_mem=8,
        jepa_n_heads=2,
        jepa_proto_dim=4,
    )
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
            torch.randn(2, 3, 1, 50, 50), return_cell=True, return_attn=True
        )
    finally:
        actor_handle.remove()
        critic_handle.remove()

    assert sequence["cell_seq"].shape == (2, 3, 2, 4, 8)
    h2_flat = sequence["cell_seq"][:, :, 1].flatten(2)
    torch.testing.assert_close(torch.stack(actor_inputs, dim=1), h2_flat)
    torch.testing.assert_close(torch.stack(critic_inputs, dim=1), h2_flat)
    assert sequence["actor_logits_seq"].shape == (2, 3, 2)
    assert sequence["V_scalar_seq"].shape == (2, 3)
    assert sequence["attn_seq"].shape == (2, 3, 4, 8)


def test_jepa_has_layer_specific_heads_centers_and_targets_both_memories() -> None:
    model = RViTPaperModel(
        n_actions=2,
        n_quantiles=5,
        seq_len=4,
        feedback="crossattn1",
        cell="transformer_memory_2layer",
        mem_heads=2,
        d_mem=8,
        jepa_n_heads=2,
        jepa_proto_dim=5,
    )
    sequence = model.forward_rl_sequence(torch.randn(2, 4, 1, 50, 50), return_cell=True)
    student_logits = model.jepa_logits(sequence["cell_seq"])

    assert len(model.jepa_layer_heads) == 2
    assert student_logits.shape == (2, 4, 2, 4, 2, 5)
    assert model.jepa_center.shape == (2, 4, 2, 5)

    teacher_logits = torch.randn_like(student_logits)
    valid = torch.ones(2, 3)
    loss, layer_losses = ppo.structured_jepa_loss(
        teacher_logits[:, 1:],
        student_logits[:, :-1],
        model.jepa_center,
        valid,
        tau_teacher=0.07,
        tau_student=0.1,
    )
    assert layer_losses.shape == (2,)
    torch.testing.assert_close(loss, layer_losses.mean())
    loss.backward()
    for head in model.jepa_layer_heads:
        assert any(parameter.grad is not None and torch.count_nonzero(parameter.grad) > 0 for parameter in head.parameters())


def test_jepa_center_ignores_padded_timesteps_for_both_layers() -> None:
    teacher = torch.zeros(2, 3, 2, 1, 1, 1)
    teacher[0, 0, :, 0, 0, 0] = torch.tensor([1.0, 10.0])
    teacher[0, 1, :, 0, 0, 0] = torch.tensor([2.0, 20.0])
    teacher[1, 0, :, 0, 0, 0] = torch.tensor([3.0, 30.0])
    teacher[:, 2, :, 0, 0, 0] = 10_000.0
    teacher[1, 1, :, 0, 0, 0] = 10_000.0
    valid = torch.tensor([[1.0, 1.0, 0.0], [1.0, 0.0, 0.0]])

    center = ppo.masked_jepa_center(teacher, valid)

    torch.testing.assert_close(center[:, 0, 0, 0], torch.tensor([2.0, 20.0]))


def test_ppo_update_logs_independent_h1_and_h2_jepa_losses() -> None:
    torch.manual_seed(0)
    model = RViTPaperModel(
        n_actions=2,
        n_quantiles=5,
        seq_len=3,
        feedback="crossattn1",
        cell="transformer_memory_2layer",
        mem_heads=2,
        d_mem=8,
        jepa_n_heads=2,
        jepa_proto_dim=5,
    )
    teacher = copy.deepcopy(model)
    for parameter in teacher.parameters():
        parameter.requires_grad_(False)
    batch_size, time_steps = 2, 3
    batch = ppo.RolloutBatch(
        observations=torch.randn(batch_size, time_steps, 1, 50, 50),
        actions=torch.zeros(batch_size, time_steps, dtype=torch.long),
        rewards=torch.randn(batch_size, time_steps),
        dones=torch.tensor([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]]),
        valid_mask=torch.ones(batch_size, time_steps),
        old_log_probs=torch.zeros(batch_size, time_steps),
        old_V_scalar=torch.zeros(batch_size, time_steps),
        old_V_dist=torch.zeros(batch_size, time_steps, 5),
        last_V_dist=torch.zeros(batch_size, 5),
        lengths=torch.full((batch_size,), time_steps, dtype=torch.long),
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    cfg = ppo.PPOConfig(n_epochs=1, jepa_coef=0.5, contrastive_coef=0.0)

    stats = ppo.ppo_update(
        model,
        optimizer,
        batch,
        cfg,
        train_actor=False,
        jepa_teacher=teacher,
        it=0,
    )

    assert stats["loss_jepa_h1"] > 0.0
    assert stats["loss_jepa_h2"] > 0.0
    torch.testing.assert_close(
        torch.tensor(stats["loss_jepa"]),
        torch.tensor((stats["loss_jepa_h1"] + stats["loss_jepa_h2"]) / 2.0),
    )


def test_two_layer_experiment_manifest_freezes_routing_and_dual_jepa() -> None:
    manifest = json.loads((EXPERIMENT / "design_manifest.json").read_text(encoding="utf-8"))

    assert manifest["status"] == "local_seed0_experiment_registered"
    assert manifest["architecture"] == {
        "visual_feedback": "crossattn1: Q=X; K/V=[X,H1_prev]; residual=X",
        "memory1": "Q=H1_prev; K/V=[H1_prev,Z]; residual=H1_prev -> H1",
        "memory2": "Q=H2_prev; K/V=[H2_prev,H1]; residual=H2_prev -> H2",
        "initial_memory": "independent learned slot-distinct H1_0 and H2_0 tokens",
        "patch_grid": [2, 2],
        "tokens_per_layer": 4,
        "d_mem": 128,
        "memory_heads_per_layer": 4,
        "visual_feedback_source": "H1_prev",
        "actor_and_value_source": "H2",
        "jepa_teacher": "separate H1/H2 heads and centers; EMA teacher; temporal t-to-t+1 targets",
        "jepa_total": "mean(loss_jepa_h1, loss_jepa_h2)",
    }
    assert manifest["task_contract"]["task"] == "vda4"
    assert manifest["jepa"]["center_update"] == "EMA over valid timesteps only; padded tails excluded"
    assert manifest["training"]["iterations"] == 20_000
    assert manifest["training"]["seed"] == 0
    assert manifest["training"]["device"] == "local_cuda"


def test_two_layer_local_launcher_is_explicit_and_local_only() -> None:
    launcher = (EXPERIMENT / "launch_local_v1.sh").read_text(encoding="utf-8")
    normalized = re.sub(r"\\\s*\n\s*", " ", launcher)

    for required in (
        "--task vda4",
        "--cell transformer_memory_2layer",
        "--feedback crossattn1",
        "--d-mem 128",
        "--mem-heads 4",
        "--memory-noise-std 0.0",
        "--jepa-coef 0.5",
        "--jepa-heads 4",
        "--iters \"$ITERS\"",
        "--device \"$DEVICE\"",
    ):
        assert required in normalized
    assert "PY_PROJECT_ROOT" in launcher
    assert "cygpath -w" in launcher
    assert "RUN_ROOT" in launcher
    assert "runpod" not in launcher.lower()
    assert "/workspace" not in launcher


def test_frozen_trunk_head_rescue_manifest_is_a_clean_probe() -> None:
    manifest = json.loads((RESCUE_EXPERIMENT / "design_manifest.json").read_text(encoding="utf-8"))

    assert manifest["parent"]["checkpoint_iteration"] == 16_949
    assert manifest["parent"]["sha256"] == "d9539ef2c4cb0b337da4c87023f10b6507581d189392c2c99c93a624ada10898"
    assert manifest["parameter_scope"] == {
        "loaded_and_frozen": ["front.", "encoder."],
        "fresh_and_trainable": ["actor_head.", "critic_head."],
        "excluded_from_parent": ["actor_head", "critic_head", "jepa_heads_and_centers"],
    }
    assert manifest["training"]["jepa_coef"] == 0.0
    assert manifest["training"]["init_action_bias"] == [0.0, 0.0]
    assert manifest["training"]["entropy_coef"] == 0.1
    assert manifest["training"]["iterations"] == 5_000


def test_frozen_trunk_head_rescue_launcher_is_hash_bound_and_local_only() -> None:
    launcher = (RESCUE_EXPERIMENT / "launch_local_v1.sh").read_text(encoding="utf-8")
    normalized = re.sub(r"\\\s*\n\s*", " ", launcher)

    for required in (
        "--init-mode frozen_trunk_probe",
        "--cell transformer_memory_2layer",
        "--feedback crossattn1",
        "--expected-parent-sha256 \"$PARENT_SHA256\"",
        "--jepa-coef 0.0",
        "--init-action-bias 0.0 0.0",
        "--entropy-coef 0.1",
        "--iters \"$ITERS\"",
        "--device \"$DEVICE\"",
    ):
        assert required in normalized
    assert "trunk_parent_iter16949.pt" in launcher
    assert "runpod" not in launcher.lower()
    assert "/workspace" not in launcher
