"""
Sanity tests for the FiLM battery. Construction + forward + FiLM-off-at-init +
env logic. The 2-iter train test is guarded by RUN_TRAIN_TEST=1 (keeps pytest free of
compute while live training jobs run).

    OMP_NUM_THREADS=1 .venv/bin/python -m pytest RViT_plus_battery/tests/test_film.py -q
"""
from __future__ import annotations

import os
import sys

import numpy as np
import torch

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
torch.set_num_threads(1)

from model import RViTPlusModel          # noqa: E402
from envs import make_env, task_grid, TASKS  # noqa: E402


def _build(task, encoder="filmblock"):
    # these tests target the filmblock encoder specifically (FiLM gate, single-stream Z
    # readout); pin it explicitly since the model default is now 'crosstalk'.
    gr, gc = task_grid(task)
    return RViTPlusModel(grid_rows=gr, grid_cols=gc, d_model=64, d_mem=64, encoder=encoder,
                             conv_channels=32, n_conv_layers=2, conv_kernel=3,
                             n_quantiles=11, seq_len=29)


def test_crosstalk_default_and_split_readout():
    """The model default is the cross-attention crosstalk encoder; rec has two streams."""
    m = RViTPlusModel(grid_rows=2, grid_cols=2)          # no encoder arg = default
    assert type(m.encoder).__name__ == "CrossTalkEncoder"
    s = m.init_states(2)
    out = m.rl_step(torch.randn(2, 3, 50, 50), s, return_attn=True)
    assert out["actor_logits"].shape == (2, m.n_actions)
    assert len(out["rec"]) == 2                          # split μ/q streams
    assert out["attn"][0].shape[-2:] == (m.n_tokens, 2 * m.n_tokens)   # μ attends 2N memory keys


def _build_broadcast(encoder):
    # broadcast encoders with the 25-token patch front-end (patch_size=10 → 5×5 grid)
    return RViTPlusModel(grid_rows=2, grid_cols=2, encoder=encoder,
                         front_end="patches", patch_size=10,
                         d_model=64, d_mem=64, conv_channels=32, n_conv_layers=2,
                         conv_kernel=3, n_quantiles=11, seq_len=7)


def test_broadcast_variants_build_and_split():
    """Both broadcast encoders build, give a 2-stream split, and SELF-attend over N (not 2N)."""
    for enc, mode in (("broadcast_film", "film"), ("broadcast", "add")):
        m = _build_broadcast(enc)
        assert type(m.encoder).__name__ == "BroadcastEncoder"
        assert m.encoder.mode == mode
        assert m.n_tokens == 25
        out = m.rl_step(torch.randn(2, 3, 50, 50), m.init_states(2), return_attn=True)
        assert len(out["rec"]) == 2
        assert not torch.allclose(out["rec"][0], out["rec"][1])
        # broadcast SELF-attention: μ attends over N content tokens (N keys, vs crosstalk's 2N)
        assert out["attn"][0].shape[-2:] == (m.n_tokens, m.n_tokens)


def test_broadcast_feedback_off_at_init():
    """Gate projections are zero-init ⇒ feedback off ⇒ plain self-attention at init."""
    for enc in ("broadcast_film", "broadcast"):
        m = _build_broadcast(enc)
        for blk in (m.encoder.mu_block, m.encoder.q_block):
            for w in (blk.W_GQ, blk.W_GK, blk.W_GV):
                assert torch.allclose(w.weight, torch.zeros_like(w.weight))
                assert torch.allclose(w.bias, torch.zeros_like(w.bias))


def test_broadcast_straight_has_norm_v_and_stays_bounded():
    """The straight (additive) variant LayerNorm's V (film does not); it stays finite under
    a large feedback gate + large memory — the normalization placement that prevents blow-up."""
    m = _build_broadcast("broadcast")
    assert isinstance(m.encoder.mu_block.norm_v, torch.nn.LayerNorm)
    mf = _build_broadcast("broadcast_film")
    assert isinstance(mf.encoder.mu_block.norm_v, torch.nn.Identity)
    with torch.no_grad():
        for blk in (m.encoder.mu_block, m.encoder.q_block):
            for w in (blk.W_GQ, blk.W_GK, blk.W_GV):
                w.weight.normal_(0, 5.0); w.bias.normal_(0, 5.0)
    s = m.init_states(1)
    s = ([h + 30.0 for h in s[0]], list(s[1]))
    out = m.rl_step(torch.randn(1, 3, 50, 50) * 8.0, s)
    assert torch.isfinite(out["actor_logits"]).all()
    assert torch.isfinite(out["critic_q_dist"]).all()


def test_token_count_matches_grid():
    for task in ("validity4", "setsize2", "setsize9", "krauzlis"):
        gr, gc = task_grid(task)
        m = _build(task)
        assert m.n_tokens == gr * gc


def test_film_feedback_off_at_init():
    """Zero-init H1 gate ⇒ (1 + W_H·H1) = 1 ⇒ Q/K depend only on X at init; V reads H2."""
    m = _build("validity4")
    blk = m.encoder.block
    for w in (blk.W_HQ, blk.W_HK):                # only Q/K are FiLM-gated by H1
        assert torch.allclose(w.weight, torch.zeros_like(w.weight))
        assert torch.allclose(w.bias, torch.zeros_like(w.bias))
    X = torch.randn(2, m.n_tokens, 64)
    Ha = torch.zeros(2, m.n_tokens, 64)
    Hb = torch.randn(2, m.n_tokens, 64)
    q0 = blk.W_XQ(X) * (1.0 + blk.W_HQ(Ha))
    q1 = blk.W_XQ(X) * (1.0 + blk.W_HQ(Hb))
    assert torch.allclose(q0, q1)                 # H1 has no effect on Q/K at init
    assert hasattr(blk, "W_V") and not hasattr(blk, "W_XV")   # values come from H2 now


def test_rl_step_shapes_and_keys():
    m = _build("validity4")
    s = m.init_states(3)
    x = torch.randn(3, 3, 50, 50)
    out = m.rl_step(x, s, return_attn=True)
    assert out["actor_logits"].shape == (3, m.n_actions)
    assert out["critic_q_dist"].shape == (3, m.n_actions, m.n_quantiles)
    assert out["V_scalar"].shape == (3,)
    assert out["attn"][0].shape[-2:] == (m.n_tokens, m.n_tokens)


def test_forward_rl_sequence_shapes():
    m = _build("setsize9")
    x = torch.randn(2, 7, 3, 50, 50)
    out = m.forward_rl_sequence(x, return_attn=True)
    assert out["actor_logits_seq"].shape == (2, 7, m.n_actions)
    assert out["q_dist_seq"].shape == (2, 7, m.n_actions, m.n_quantiles)
    assert out["attn_seq"].shape[1] == 7


def test_readout_is_Z_and_both_lstms_from_Z():
    """Two LSTMs both updated from Z; default readout is Z (the block output)."""
    m = _build("validity4")
    assert m.encoder.n_lstm == 2 and m.encoder.readout == "Z"
    s = m.init_states(2)
    x = torch.randn(2, 3, 50, 50)
    tokens = m.front(x)
    new_states, rec = m.encoder.forward_step(tokens, s)
    H1, H2 = new_states[0][0], new_states[0][1]
    assert not torch.allclose(rec[0], H1)        # readout Z is not a raw LSTM hidden
    assert not torch.allclose(rec[0], H2)
    # both LSTMs ingest the same Z but have distinct weights → distinct hiddens
    assert not torch.allclose(H1, H2)


def test_attn_clamp_changes_attention():
    m = _build("validity4")
    s = m.init_states(1)
    x = torch.randn(1, 3, 50, 50)
    base = m.rl_step(x, s, return_attn=True)["attn"][0]
    clamped = m.rl_step(x, s, return_attn=True, attn_clamp={0: 1.0})["attn"][0]
    # after clamp+renorm, token 0 should receive the most attention
    assert clamped[..., 0].mean() >= clamped.mean()
    assert not torch.allclose(base, clamped)


def test_envs_reset_step_and_reward_logic():
    for task in TASKS:
        env = make_env(task)
        obs = env.reset()
        assert obs.shape == (50, 50, 3)
        gr, gc = task_grid(task)
        assert env.n_stim == gr * gc
        # run a full wait-episode → correct rejection on no-change pays reward
        env.change_true = 0
        env.t = 0
        total = 0.0
        for _ in range(env.T):
            _, r, d, _ = env.step(0)
            total += r
            if d:
                break
        assert total >= 1.0                       # CR rewarded


def test_krauzlis_ignores_uncued_change():
    from envs.tasks import KrauzlisEnv
    env = KrauzlisEnv()
    env.reset()
    # force an UNCUED change trial; declaring after change must NOT pay
    env.change_true = 1
    env.cue_index = 0
    env.change_index = 1 if env.n_stim > 1 else 0
    env.change_time = 11
    assert env._is_reportable_change() is (env.change_index == env.cue_index)


def test_setsize_validity_ramp_present():
    env = make_env("setsize9")
    props = set()
    for _ in range(200):
        env.reset(); props.add(env.proportion)
    assert 0.0 in props and 1.0 in props          # includes uninformative + perfect cue


def test_train_two_iters_optional():
    if os.environ.get("RUN_TRAIN_TEST") != "1":
        return
    from ppo import PPOConfig, train
    m = _build("validity4")
    env = make_env("validity4")
    hist = train(model=m, env=env, n_iterations=2, episodes_per_iter=2,
                 cfg=PPOConfig(burn_in_iters=0, buffer_capacity=8, per_n_replay=0),
                 device=torch.device("cpu"), log_every=1, checkpoint_dir=None)
    assert len(hist) == 2
