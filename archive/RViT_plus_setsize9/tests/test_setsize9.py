"""Smoke tests for the set-size-9 cued change-detection variant: the new env (nine
stimuli, five cue-reliability levels incl. the uninformative 0, uniform reward, no
distractor) + the reused v11_part2 cross-talk architecture.

Run:  .venv/bin/python -m RViT_plus_setsize9.tests.test_setsize9
"""
from __future__ import annotations
import os, sys
import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from RViT_plus_setsize9.env import ChangeDetectionEnv, STIM_CENTERS, N_STIMULI, PATCH
from RViT_plus_setsize9.model import RViTPlusSetsize9Model
from RViT_plus_setsize9.ppo import PPOConfig, collect_episodes, train

DEVICE = torch.device("cpu")
torch.manual_seed(0)


def _model(**over):
    kw = dict(patch_size=5, d_model=64, d_mem=64, tx_heads=1, n_lstm=2, conv_channels=32,
              n_conv_layers=3, conv_kernel=5, n_actions=2, n_quantiles=8, init_action_bias=[0.0, -1.5])
    kw.update(over)
    return RViTPlusSetsize9Model(**kw).to(DEVICE)


def test_env_grid_and_obs():
    env = ChangeDetectionEnv()
    assert N_STIMULI == 9 and len(STIM_CENTERS) == 9
    obs = env.reset()
    assert obs.shape == (50, 50, 3)
    assert env._next_observation().shape == (50, 50, 3)            # t=0 blank
    print("✓ env: nine 3×3 grid stimuli, (50,50,3) observations")


def test_env_five_reliabilities_incl_zero():
    env = ChangeDetectionEnv()
    seen = set()
    for _ in range(400):
        env.reset(); seen.add(env.proportion)
    assert seen == {0.0, 0.25, 0.5, 0.75, 1.0}, f"expected 5 levels incl 0; got {seen}"
    print("✓ env: five reliability levels {0, .25, .5, .75, 1.0} (0 = uninformative)")


def test_env_validity_ramps_with_proportion():
    """P(target at cued | change) ≈ proportion + (1-proportion)/9; ≈1/9 at 0, 1 at 1."""
    np.random.seed(1); env = ChangeDetectionEnv()
    by = {p: [] for p in env.proportions}
    for _ in range(6000):
        env.reset()
        if env.change_true:
            by[env.proportion].append(env.valid)
    v = {p: np.mean(by[p]) for p in env.proportions}
    assert v[0.0] < 0.25, f"proportion 0 must be ~uniform (1/9), got {v[0.0]:.3f}"
    assert v[1.0] > 0.95, f"proportion 1 must be ~always valid, got {v[1.0]:.3f}"
    assert v[0.0] < v[0.5] < v[1.0], "validity must increase monotonically with proportion"
    print(f"✓ env: validity ramps {v[0.0]:.2f}→{v[0.5]:.2f}→{v[1.0]:.2f} across reliability (0→1)")


def test_env_cue_marks_one_location():
    env = ChangeDetectionEnv()
    env.reset(); env.t = 1
    cue = env._next_observation()
    # cue pixels localised to the cued cell only
    cy, cx = STIM_CENTERS[env.cue_index]; h = PATCH // 2
    inside = (cue[cy-h:cy+h+1, cx-h:cx+h+1] != 0).any()
    total_nonzero = (cue.sum(-1) != 0).sum()
    assert inside and total_nonzero < 2 * PATCH * PATCH, "cue must mark exactly one location"
    print(f"✓ env: cue marks one of nine locations (index {env.cue_index})")


def test_env_uniform_reward_no_distractor():
    env = ChangeDetectionEnv()
    assert not hasattr(env, "distractor_true"), "set-size task has no distractor"
    # a hit (press at/after change on a change trial) pays 1 regardless of location/cue
    env.reset(); env.change_true = 1; env.change_time = 11
    env.t = 12
    _, r, done, _ = env.step(1)
    assert r == 1.0 and done, f"uniform hit reward should be 1.0; got {r}"
    print("✓ env: uniform reward (hit/correct-reject = 1.0), no distractor")


def test_model_unchanged_arch():
    m = RViTPlusSetsize9Model()  # full-size defaults
    n = sum(p.numel() for p in m.parameters())
    assert n == 1_015_656, f"v11_part2 cross-talk arch reused unchanged; got {n}"
    enc = m.encoder
    for nm in ("sal_block", "td_block", "sal_tag", "cell1", "cell2", "mem_pos_emb"):
        assert hasattr(enc, nm), f"cross-talk encoder missing {nm}"
    print(f"✓ model: v11_part2 cross-talk architecture reused unchanged ({n:,} params)")


def test_model_forward_and_split_readout():
    m = _model()
    out = m.rl_step(torch.randn(2, 3, 50, 50), m.init_states(2, device=DEVICE))
    assert out["actor_logits"].shape == (2, 2) and out["critic_q_dist"].shape == (2, 2, 8)
    seq = m.forward_rl_sequence(torch.randn(2, 29, 3, 50, 50))
    assert seq["actor_logits_seq"].shape == (2, 29, 2)
    print("✓ model: rl_step + forward_rl_sequence shapes correct (split readout)")


def test_collect_and_train():
    m = _model()
    batch, stats = collect_episodes(m, ChangeDetectionEnv(), n_episodes=4, device=DEVICE)
    assert batch is not None and stats is not None
    hist = train(m, ChangeDetectionEnv(), n_iterations=2, episodes_per_iter=4,
                 cfg=PPOConfig(n_epochs=2, per_n_replay=2, buffer_capacity=16, burn_in_iters=1),
                 device=DEVICE, log_every=1, save_every=999)
    assert len(hist) == 2 and "loss_total" in hist[-1]
    print("✓ ppo: collect_episodes + 2-iter train run on the set-size env")


if __name__ == "__main__":
    tests = [test_env_grid_and_obs, test_env_five_reliabilities_incl_zero,
             test_env_validity_ramps_with_proportion, test_env_cue_marks_one_location,
             test_env_uniform_reward_no_distractor, test_model_unchanged_arch,
             test_model_forward_and_split_readout, test_collect_and_train]
    for t in tests:
        t()
    print(f"\nAll {len(tests)} set-size-9 smoke tests passed.")
