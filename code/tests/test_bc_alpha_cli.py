from __future__ import annotations

import pytest

from train_rl import build_arg_parser


def test_train_rl_accepts_explicit_zero_bc_alpha() -> None:
    args = build_arg_parser().parse_args(["--bc-alpha", "0.0"])

    assert args.bc_alpha == pytest.approx(0.0)
