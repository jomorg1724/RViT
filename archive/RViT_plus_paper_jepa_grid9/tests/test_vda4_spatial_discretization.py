"""VDA4 sensory-discretization experiment tests."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import torch

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
ROOT = Path(_ROOT)

from conv_frontend import ConvPatchFrontEnd  # noqa: E402
from envs import make_env  # noqa: E402
from model import RViTPaperModel  # noqa: E402
from train_rl import build_arg_parser, resolve_patch_grid  # noqa: E402


def test_vda4_patch_grid_override_changes_tokens_without_changing_task_geometry():
    args = build_arg_parser().parse_args(
        ["--task", "vda4", "--patch-grid-rows", "10", "--patch-grid-cols", "10"]
    )
    assert resolve_patch_grid(args.task, args.patch_grid_rows, args.patch_grid_cols) == (10, 10)

    env = make_env(args.task, curriculum=False)
    assert (env.grid_rows, env.grid_cols, env.n_stim, env.S) == (2, 2, 4, 50)


def test_patch_grid_override_requires_both_positive_dimensions():
    with pytest.raises(ValueError, match="provided together"):
        resolve_patch_grid("vda4", 10, None)
    with pytest.raises(ValueError, match="positive"):
        resolve_patch_grid("vda4", 0, 10)


def test_even_patch_grid_encodes_all_100_patches_in_one_shared_cnn_batch():
    front = ConvPatchFrontEnd(grid_rows=10, grid_cols=10, image_size=50)
    stem_inputs = []
    handle = front.stem.register_forward_pre_hook(
        lambda _module, args: stem_inputs.append(tuple(args[0].shape))
    )
    try:
        tokens = front(torch.randn(2, 3, 50, 50), t=3)
    finally:
        handle.remove()

    assert stem_inputs == [(200, 3, 5, 5)]
    assert tokens.shape == (2, 100, 128 + 100 + 8)


def test_grid10x10_experiment_launcher_is_isolated_and_fully_specified():
    experiment_dir = ROOT / "experiments" / "vda4_spatial_discretization" / "grid_10x10"
    launcher = experiment_dir / "launch_20k.sh"
    readme = experiment_dir / "README.md"

    content = launcher.read_text(encoding="utf-8")
    assert readme.is_file()
    assert 'source "$WORKSPACE_ROOT/.venv/bin/activate"' in content
    assert "python3 -u" in content
    assert 'mkdir "$CHECKPOINT_DIR"' in content
    assert '--checkpoint-dir "$CHECKPOINT_DIR"' in content
    assert "uuid.uuid4().hex" in content
    for expected in (
        "--task vda4",
        "--patch-grid-rows 10",
        "--patch-grid-cols 10",
        "--cell xlstm",
        "--feedback affine_ew",
        "--conv-frontend",
        "--jepa-coef 0.5",
        "--d-mem 128",
        "--curriculum",
        "--init-mode fresh",
        "--iters 20000",
        "--schedule-final-iteration 19999",
        "--episodes-per-iter 8",
        "--save-every 50",
        "--log-every 1",
        "--seed 0",
        "--device mps",
    ):
        assert expected in content


def test_grid10x10_model_has_100_aligned_visual_and_memory_tokens():
    model = RViTPaperModel(
        n_quantiles=5,
        seq_len=7,
        feedback="affine_ew",
        cell="xlstm",
        jepa_n_heads=4,
        jepa_proto_dim=256,
        d_mem=128,
        conv_frontend=True,
        grid_rows=10,
        grid_cols=10,
        image_size=50,
    )
    state = model.init_states(1)
    assert model.n_tokens == 100
    assert all(tensor.shape == (1, 100, 128) for tensor in state[0])

    output = model.rl_step(torch.randn(1, 3, 50, 50), state, return_attn=True)
    assert output["new_states"][0][0].shape == (1, 100, 128)
    assert output["attn"][0].shape == (1, 100, 100)
    assert output["actor_logits"].shape == (1, 2)
    assert output["critic_q_dist"].shape == (1, 2, 5)
