"""Protocol-fidelity tests for the Luo & Maunsell (2015) task analogue."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
import torch

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from envs.luo2015 import LuoMaunsell2015Env  # noqa: E402
from luo2015_analysis.luo2015_core import classify_trial, load_model, summarize_sdt  # noqa: E402
from model import RViTPaperModel  # noqa: E402
from train_rl import _producer_hashes  # noqa: E402


def _mean_and_ratio(pair: tuple[float, float]) -> tuple[float, float]:
    hit, correct_rejection = pair
    return (hit + correct_rejection) / 2.0, hit / correct_rejection


def test_checkpoint_loader_preserves_cross_attention_and_memory_decay(tmp_path):
    model_kwargs = {
        "n_actions": 2,
        "n_quantiles": 5,
        "seq_len": 7,
        "feedback": "crossattn1",
        "cell": "xlstm",
        "jepa_n_heads": 4,
        "jepa_proto_dim": 256,
        "frame_repeat": 1,
        "d_mem": 128,
        "memory_decay": 0.5,
        "conv_frontend": True,
        "grid_rows": 2,
        "grid_cols": 2,
        "image_size": 50,
    }
    source = RViTPaperModel(**model_kwargs)
    checkpoint = tmp_path / "crossattn.pt"
    torch.save({
        "iter": 7,
        "model_kwargs": model_kwargs,
        "model_state_dict": source.state_dict(),
    }, checkpoint)

    loaded, iteration = load_model(checkpoint)

    assert iteration == 7
    assert loaded.encoder.feedback == "crossattn1"
    assert loaded.encoder.memory_decay == 0.5


def test_published_reward_schedules_are_spatially_counterphased():
    sensitivity = LuoMaunsell2015Env(session="sensitivity", condition_loc=0)
    high_mean, high_ratio = _mean_and_ratio(sensitivity.reward_table[0])
    low_mean, low_ratio = _mean_and_ratio(sensitivity.reward_table[3])
    assert high_mean == pytest.approx(5.0)
    assert low_mean == pytest.approx(1.0)
    assert high_ratio == pytest.approx(0.7)
    assert low_ratio == pytest.approx(1.1)

    sensitivity.set_condition(3)
    assert sensitivity.reward_table[3] == pytest.approx((
        2 * 5.0 * 0.7 / 1.7,
        2 * 5.0 / 1.7,
    ))
    assert sensitivity.reward_table[0] == pytest.approx((
        2 * 1.0 * 1.1 / 2.1,
        2 * 1.0 / 2.1,
    ))

    criterion = LuoMaunsell2015Env(session="criterion", condition_loc=0)
    low_c_mean, low_c_ratio = _mean_and_ratio(criterion.reward_table[0])
    high_c_mean, high_c_ratio = _mean_and_ratio(criterion.reward_table[3])
    assert low_c_mean == pytest.approx(0.9)
    assert high_c_mean == pytest.approx(1.0)
    assert low_c_ratio == pytest.approx(1.5)
    assert high_c_ratio == pytest.approx(0.5)


def test_no_change_trial_requires_response_to_changed_second_test_for_cr():
    env = LuoMaunsell2015Env(session="sensitivity", condition_loc=0, T=7)
    env.change_true = 0
    env.test_loc = 0
    env.test_ori = env.samp[0]
    env.second_test_ori = env.samp[0] + env.theta
    env.t = env.FIRST_TEST_ONSET

    for _ in range(2):
        _, reward, done, _ = env.step(0)
        assert not done
        assert reward == 0.0
    _, reward, done, _ = env.step(0)
    assert not done
    assert reward == 0.0

    _, reward, done, info = env.step(1)
    assert done
    assert reward == pytest.approx(env.reward_table[0][1])
    assert info["outcome"] == "correct_rejection"
    assert info["valid_sdt"] is True


@pytest.mark.parametrize(
    ("change", "time", "action", "outcome", "valid_sdt", "rewarded"),
    [
        (1, 3, 1, "hit", True, True),
        (0, 3, 1, "false_alarm", True, False),
        (1, 4, 0, "miss", True, False),
        (1, 1, 1, "fixation_break", False, False),
    ],
)
def test_first_test_actions_are_classified_like_the_published_sdt_task(
    change: int,
    time: int,
    action: int,
    outcome: str,
    valid_sdt: bool,
    rewarded: bool,
):
    env = LuoMaunsell2015Env(session="criterion", condition_loc=0, T=7)
    env.change_true = change
    env.test_loc = 0
    env.t = time

    _, reward, done, info = env.step(action)

    assert done
    assert info["outcome"] == outcome
    assert info["valid_sdt"] is valid_sdt
    assert (reward > 0) is rewarded


def test_each_session_uses_two_fixed_orientations_per_location():
    env = LuoMaunsell2015Env(
        theta=20.0,
        base_orientations={0: 10.0, 3: 80.0},
        noise_multiplier=0.0,
    )
    expected = {0: {10.0, 30.0}, 3: {80.0, 100.0}}

    for _ in range(40):
        env.reset()
        assert env.samp[0] in expected[0]
        assert env.samp[3] in expected[3]
        assert env.test_ori in expected[env.test_loc]
        assert env.second_test_ori in expected[env.test_loc]


def test_rendered_no_change_trial_has_fixation_first_test_gap_and_second_test():
    env = LuoMaunsell2015Env(noise_multiplier=0.0, T=7)
    env.change_true = 0
    env.test_loc = 0
    env.test_ori = env.samp[0]
    env.second_test_ori = env.samp[0] + env.theta

    frames = env.render_trial()

    assert frames.shape == (7, 50, 50, 3)
    center = env.S // 2
    fixation = frames[:, center - 1:center + 1, center - 1:center + 1]
    assert np.all(fixation.max(axis=(1, 2, 3)) > 0)
    energy = np.abs(frames).sum(axis=(1, 2, 3))
    assert energy[0] > energy[2]
    assert energy[3] > energy[5]
    assert energy[6] > energy[5]


def test_checkpoint_state_binds_session_condition_and_reward_schedule():
    source = LuoMaunsell2015Env(session="criterion", condition_loc=0)
    state = source.training_state_dict()

    assert state["environment_config"]["session"] == "criterion"
    assert state["environment_config"]["condition_loc"] == 0
    assert state["environment_config"]["reward_table"] == source.reward_table

    incompatible = LuoMaunsell2015Env(session="criterion", condition_loc=3)
    with pytest.raises(ValueError, match="environment configuration mismatch"):
        incompatible.load_training_state_dict(state)


@pytest.mark.parametrize(
    ("change", "press_time", "expected"),
    [
        (1, 3, "hit"),
        (1, 4, "hit"),
        (1, -1, "miss"),
        (1, 2, "fixation_break"),
        (0, 3, "false_alarm"),
        (0, 4, "false_alarm"),
        (0, 6, "correct_rejection"),
        (0, -1, "second_test_miss"),
        (0, 5, "fixation_break"),
    ],
)
def test_offline_sdt_classification_matches_live_trial_rules(
    change: int, press_time: int, expected: str
):
    assert classify_trial(change, press_time) == expected


def test_sdt_summary_excludes_fixation_breaks_and_second_test_failures():
    result = summarize_sdt(
        change_press=np.array([3, 4, -1, 1]),
        no_change_press=np.array([3, 6, -1, 5]),
        change_locations=np.array([0, 3, 0, 3]),
        no_change_locations=np.array([0, 3, 0, 3]),
    )

    assert result["n_change"] == 3
    assert result["n_no_change"] == 2
    assert result["excluded_change"] == 1
    assert result["excluded_no_change"] == 2
    assert result["fixation_break_change"] == 1
    assert result["fixation_break_no_change"] == 1
    assert result["second_test_miss_change"] == 0
    assert result["second_test_miss_no_change"] == 1
    assert result["HR"] == pytest.approx(2 / 3)
    assert result["FA"] == pytest.approx(1 / 2)
    assert result["loc0"]["fixation_break_change"] == 0
    assert result["loc0"]["fixation_break_no_change"] == 0
    assert result["loc0"]["second_test_miss_no_change"] == 1
    assert result["loc3"]["fixation_break_change"] == 1
    assert result["loc3"]["fixation_break_no_change"] == 1
    assert result["loc3"]["second_test_miss_no_change"] == 0


def test_training_provenance_hashes_the_luo_environment_source():
    assert "envs/luo2015.py" in _producer_hashes()


def test_protocol_defaults_to_fixed_difficulty_with_no_value_cue():
    env = LuoMaunsell2015Env()
    assert env.curriculum is False
    assert env.value_cues is False
