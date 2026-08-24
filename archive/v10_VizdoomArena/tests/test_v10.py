"""
Unit + smoke tests for V10 (shapes, identities, trainer math, end-to-end).

    .venv/bin/python -m v10_VizdoomArena.tests.test_v10

Pure-model/trainer tests run on CPU with no ViZDoom; the env/collector/train
smoke tests run only if vizdoom imports cleanly.
"""
from __future__ import annotations

import copy
import os
import sys

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from v10_VizdoomArena.env import FEAT_DIM, FEAT_GROUPS, N_ACTIONS
from v10_VizdoomArena.model import V10ArenaModel
from v10_VizdoomArena.patch_embed import PatchEmbed
from v10_VizdoomArena.trainer import (
    PACConfig, SegmentBatch, SegmentReplayBuffer,
    compute_nstep_distributional_targets, ema_update, pac_update,
)

torch.manual_seed(0)
np.random.seed(0)

_PASS = 0


def _ok(name: str) -> None:
    global _PASS
    _PASS += 1
    print(f"  ✓ {name}")


def _tiny_model(**over) -> V10ArenaModel:
    kw = dict(
        image_h=60, image_w=80, patch_size=10, patch_hidden=32,
        d_model=32, d_mem=32, enc_heads=4, enc_layers=2,
        dec_heads=4, dec_layers=2, head_hidden=32, head_layers=2,
        n_actions=N_ACTIONS, n_quantiles=11,
        feat_dim=FEAT_DIM, state_groups=dict(FEAT_GROUPS), drop=0.1,
    )
    kw.update(over)
    return V10ArenaModel(**kw)


# ── 1. patch embed ───────────────────────────────────────────────────────────
def test_patch_embed():
    pe = PatchEmbed(image_h=60, image_w=80, patch_size=10, d_model=32, patch_hidden=32)
    assert pe.n_tokens == 48 and pe.grid_h == 6 and pe.grid_w == 8
    out = pe(torch.rand(2, 3, 60, 80))
    assert out.shape == (2, 48, 32)
    _ok("patch_embed shapes (6×8 grid = 48 tokens)")


# ── 2. encoder step: shapes, recurrence, attention, key layout ───────────────
def test_encoder_step():
    m = _tiny_model().eval()   # eval: MHA dropout off, so attn rows sum to 1
    enc = m.encoder
    B = 3
    tokens = torch.randn(B, 48, 32)
    feats = torch.rand(B, FEAT_DIM)
    st0 = enc.init_states(B)
    (Hs, Cs), rec, attn = enc.forward_step(tokens, feats, st0, return_attn=True)
    # 2 attention-layer memories + 1 readout memory; rec = [H3] only
    assert len(Hs) == 3 and Hs[0].shape == (B, 48, 32)
    assert len(rec) == 1 and torch.equal(rec[0], Hs[2])
    assert len(attn) == 2
    # layer 0 (perception): keys = [patch | H1 H2 | state]; layer 1
    # (consolidation): keys = [H1 H2] only.
    n_keys0 = (1 + 2) * 48 + 3
    assert enc.n_keys == enc.n_keys_for(0) == n_keys0
    assert enc.n_keys_for(1) == 2 * 48
    assert attn[0].shape == (B, 4, 48, n_keys0)
    assert attn[1].shape == (B, 4, 48, 2 * 48)
    layout = enc.key_layout()
    assert layout["patch"] == (0, 48) and layout["H1"] == (48, 96) and layout["H2"] == (96, 144)
    assert layout["vitals"] == (144, 145) and layout["last_action"] == (146, 147)
    layout1 = enc.key_layout(1)
    assert layout1 == {"H1": (0, 48), "H2": (48, 96)}
    # attention rows are proper distributions
    for a in attn:
        s = a.sum(dim=-1)
        assert torch.allclose(s, torch.ones_like(s), atol=1e-4)
    # recurrence: a second step changes the memory
    (Hs2, _), _ = enc.forward_step(tokens, feats, (Hs, Cs))
    assert not torch.allclose(Hs2[0], Hs[0])
    _ok("encoder step shapes / key layout / attention normalization")


# ── 2b. the v10 H1-residual: NO raw-input bypass ─────────────────────────────
def test_no_bypass():
    """v10's defining property (inherited from RViT_plus_v8, strengthened by
    the consolidation-layer design): zeroing ONLY layer 0's attention output
    projection makes the ENTIRE recurrent update BIT-IDENTICAL across wildly
    different frames AND game-state features — impossible in v6, whose
    X-residual leaks the frame through. Layer 0 is the sole port of entry;
    layer 1 reads nothing but memories, so it goes blind automatically."""
    m = _tiny_model().eval()
    enc = m.encoder
    B = 2
    st0 = enc.init_states(B)
    x1, x2 = torch.rand(B, 3, 60, 80), torch.rand(B, 3, 60, 80)
    f1, f2 = torch.rand(B, FEAT_DIM), torch.rand(B, FEAT_DIM)
    with torch.no_grad():
        # sanity: attention intact → different inputs give different memory
        (Hs_a, _), _ = enc.forward_step(m.patch_embed(x1), f1, st0)
        (Hs_b, _), _ = enc.forward_step(m.patch_embed(x2), f2, st0)
        assert not torch.allclose(Hs_a[0], Hs_b[0])
        # cut layer 0's attention output ONLY → the whole encoder must go blind
        blk0 = enc.blocks[0]
        blk0.attn.out_proj.weight.zero_()
        if blk0.attn.out_proj.bias is not None:
            blk0.attn.out_proj.bias.zero_()
        (Hs_c, Cs_c), _ = enc.forward_step(m.patch_embed(x1), f1, st0)
        (Hs_d, Cs_d), _ = enc.forward_step(m.patch_embed(x2), f2, st0)
        for tc, td in zip(Hs_c + Cs_c, Hs_d + Cs_d):
            assert torch.equal(tc, td), "raw-input bypass detected!"
    _ok("no-bypass: layer-0 out_proj zeroed ⇒ ALL memory updates input-independent")


# ── 3. attention bias: zeros == identity; large bias steers attention ────────
def test_attn_bias():
    m = _tiny_model().eval()
    enc = m.encoder
    B = 2
    tokens = torch.randn(B, 48, 32)
    feats = torch.rand(B, FEAT_DIM)
    st0 = enc.init_states(B)
    with torch.no_grad():
        _, rec_a, attn_a = enc.forward_step(tokens, feats, st0, return_attn=True)
        zeros = [torch.zeros(48, enc.n_keys_for(0)), torch.zeros(48, enc.n_keys_for(1))]
        _, rec_b, attn_b = enc.forward_step(tokens, feats, st0, return_attn=True,
                                            attn_bias=zeros)
        assert torch.allclose(rec_a[0], rec_b[0], atol=1e-5)
        assert torch.allclose(attn_a[0], attn_b[0], atol=1e-5)
        assert torch.allclose(attn_a[1], attn_b[1], atol=1e-5)
        # +10 bias on key 0 should grab most of the attention mass
        push = torch.zeros(48, enc.n_keys)
        push[:, 0] = 10.0
        _, _, attn_c = enc.forward_step(tokens, feats, st0, return_attn=True,
                                        attn_bias=[push, None])
        assert float(attn_c[0][..., 0].mean()) > 0.5
        assert float(attn_c[0][..., 0].mean()) > 5 * float(attn_a[0][..., 0].mean())
    # decoder bias identity too (decoders read [CLS ++ H3] = 1 + 48 tokens)
    with torch.no_grad():
        logits_a = m.actor_head(rec_a)
        S = 1 + 48
        logits_b = m.actor_head(rec_a, attn_bias=[torch.zeros(S, S), None])
        assert torch.allclose(logits_a, logits_b, atol=1e-5)
    _ok("attn bias: zero ≡ identity (enc+dec); large bias steers attention")


# ── 4. decoders + derive_V ───────────────────────────────────────────────────
def test_decoders():
    m = _tiny_model().eval()
    B = 3
    rec = [torch.randn(B, 48, 32)]            # decoders read [H3] only
    with torch.no_grad():
        logits = m.actor_head(rec)
        q = m.critic_head(rec)
        assert logits.shape == (B, N_ACTIONS)
        assert q.shape == (B, N_ACTIONS, 11)
        V_dist, V_scalar = m.critic_head.derive_V(q, logits)
        pi = torch.softmax(logits, -1)
        V_ref = (pi.unsqueeze(-1) * q).sum(1)
        assert torch.allclose(V_dist, V_ref, atol=1e-5)
        assert torch.allclose(V_scalar, V_ref.mean(-1), atol=1e-5)
        _, attns = m.actor_head(rec, return_attn=True)
        assert attns[0].shape == (B, 4, 1 + 48, 1 + 48)
        assert m.actor_head.token_layout() == {"cls": (0, 1), "H3": (1, 49)}
    _ok("decoder shapes / derive_V / decoder attention (reads H3 only)")


# ── 5. rl_step ≡ forward_segment (no dones) ──────────────────────────────────
def test_step_vs_segment():
    m = _tiny_model().eval()
    B, T = 2, 5
    obs = torch.rand(B, T, 3, 60, 80)
    feats = torch.rand(B, T, FEAT_DIM)
    with torch.no_grad():
        states = m.init_states(B)
        step_logits = []
        for t in range(T):
            out = m.rl_step(obs[:, t], feats[:, t], states)
            states = out["new_states"]
            step_logits.append(out["actor_logits"])
        step_logits = torch.stack(step_logits, 1)
        seg = m.forward_segment(obs, feats)
    assert torch.allclose(step_logits, seg["actor_logits_seq"], atol=1e-4)
    _ok("rl_step trajectory ≡ forward_segment re-encode")


# ── 6. done resets the recurrent state mid-segment ───────────────────────────
def test_done_reset():
    m = _tiny_model().eval()
    T = 6
    obs = torch.rand(1, T, 3, 60, 80)
    feats = torch.rand(1, T, FEAT_DIM)
    dones = torch.zeros(1, T)
    dones[0, 2] = 1.0                       # episode boundary after step 2
    with torch.no_grad():
        seg = m.forward_segment(obs, feats, dones=dones)
        # steps 3.. must equal a fresh forward on the suffix
        fresh = m.forward_segment(obs[:, 3:], feats[:, 3:])
    assert torch.allclose(seg["actor_logits_seq"][:, 3:],
                          fresh["actor_logits_seq"], atol=1e-4)
    _ok("done flag resets recurrent state inside forward_segment")


# ── 7. n-step distributional targets vs explicit reference ──────────────────
def test_nstep_targets():
    B, T, N = 3, 7, 5
    gamma = 0.9
    r = torch.randn(B, T)
    d = (torch.rand(B, T) < 0.25).float()
    V = torch.randn(B, T + 1, N)

    def ref(n):
        out = np.zeros((B, T, N))
        for b in range(B):
            for t in range(T):
                G = np.zeros(N)
                disc, k, terminated = 1.0, 0, False
                while k < n and t + k < T:
                    G += disc * r[b, t + k].item()
                    if d[b, t + k] > 0.5:
                        terminated = True
                        k += 1
                        break
                    disc *= gamma
                    k += 1
                if not terminated:
                    G = G + disc * V[b, t + k].numpy()
                out[b, t] = G
        return torch.from_numpy(out).float()

    for n in (1, 2, 3):
        got = compute_nstep_distributional_targets(r, d, V, gamma, n_step=n)
        assert torch.allclose(got, ref(n), atol=1e-4), f"n={n} mismatch"
    _ok("n-step distributional targets match explicit reference (n=1,2,3)")


# ── 8. PER buffer ────────────────────────────────────────────────────────────
def _fake_batch(model: V10ArenaModel, B: int, T: int) -> SegmentBatch:
    iH, iC = V10ArenaModel.states_to_tensors(model.init_states(B))
    dones = torch.zeros(B, T)
    dones[0, T // 2] = 1.0
    return SegmentBatch(
        obs=torch.randint(0, 255, (B, T + 1, 3, 60, 80), dtype=torch.uint8),
        feats=torch.rand(B, T + 1, FEAT_DIM),
        actions=torch.randint(0, N_ACTIONS, (B, T)),
        rewards=torch.randn(B, T) * 0.1,
        dones=dones,
        valid=torch.ones(B, T),
        init_H=iH, init_C=iC,
    )


def test_per_buffer():
    m = _tiny_model()
    buf = SegmentReplayBuffer(capacity=8)
    buf.push(_fake_batch(m, 4, 6), priorities=torch.tensor([1.0, 2.0, 3.0, 4.0]))
    assert len(buf) == 4
    batch, idxs = buf.sample(n=3, alpha=0.6, beta=0.4)
    assert batch.obs.shape == (3, 7, 3, 60, 80) and batch.obs.dtype == torch.uint8
    assert batch.sample_weights.shape == (3,)
    assert float(batch.sample_weights.max()) <= 1.0 + 1e-6
    buf.update_priorities(idxs, torch.ones(3) * 9.0)
    for i in idxs:
        assert abs(buf._priorities[i] - 9.0) < 1e-9
    buf.push(_fake_batch(m, 4, 6))   # wraps FIFO past capacity
    buf.push(_fake_batch(m, 4, 6))
    assert len(buf) == 8
    _ok("PER segment buffer push/sample/update/wrap")


# ── 9. EMA target update ─────────────────────────────────────────────────────
def test_ema():
    m = _tiny_model()
    tgt = copy.deepcopy(m)
    with torch.no_grad():
        for p in m.parameters():
            p.add_(1.0)
    p0 = next(iter(tgt.parameters())).clone()
    ema_update(tgt, m, tau=0.1)
    p1 = next(iter(tgt.parameters()))
    expected = p0 * 0.9 + (next(iter(m.parameters()))) * 0.1
    assert torch.allclose(p1, expected, atol=1e-6)
    _ok("EMA target: θ′ ← (1−τ)θ′ + τθ")


# ── 10. pac_update end-to-end on a fake batch (CPU) ──────────────────────────
def test_pac_update():
    m = _tiny_model()
    tgt = copy.deepcopy(m)
    for p in tgt.parameters():
        p.requires_grad_(False)
    opt = torch.optim.Adam(m.parameters(), lr=1e-4)
    cfg = PACConfig(seg_len=6, replay_burn_in=2, n_epochs=2, n_step=3,
                    warmup_iters=0, ema_tau=0.05)
    batch = _fake_batch(m, 3, 6)
    before = next(iter(tgt.parameters())).clone()
    stats = pac_update(m, tgt, opt, batch, cfg, device=torch.device("cpu"))
    assert stats["n_updates"] == 2
    for k in ("loss_policy", "loss_value", "loss_entropy", "loss_total", "approx_kl"):
        assert np.isfinite(stats[k]), f"{k} not finite"
    pri = stats["per_segment_priority"]
    assert pri.shape == (3,) and bool((pri > 0).all())
    assert not torch.allclose(before, next(iter(tgt.parameters())))  # EMA moved
    # critic-only mode runs too
    stats2 = pac_update(m, tgt, opt, batch, cfg, device=torch.device("cpu"),
                        train_actor=False)
    assert stats2["loss_policy"] == 0.0 and np.isfinite(stats2["loss_value"])
    _ok("pac_update: finite losses, priorities, EMA moves, critic-only mode")


# ── 11. env + collector + train smoke (needs vizdoom) ────────────────────────
def test_env_and_train_smoke():
    try:
        import vizdoom  # noqa: F401
    except Exception as e:  # pragma: no cover
        print(f"  ~ skipping env/train smoke (vizdoom unavailable: {e})")
        return
    from v10_VizdoomArena.env import VizdoomArenaEnv
    from v10_VizdoomArena.trainer import train

    env = VizdoomArenaEnv(seed=7)
    try:
        obs, feats = env.reset()
        assert obs.shape == (3, 60, 80) and obs.dtype == np.uint8
        assert feats.shape == (FEAT_DIM,) and abs(float(feats[3:11].sum()) - 1.0) < 1e-6
        obs2, feats2, r, done, info = env.step(2)
        assert obs2.shape == (3, 60, 80) and np.isfinite(r)
        _ok("env reset/step shapes + feature one-hots")

        m = _tiny_model()
        cfg = PACConfig(seg_len=8, segments_per_iter=1, replay_burn_in=2,
                        warmup_iters=1, buffer_capacity=8, per_n_replay=1,
                        n_epochs=1, n_step=3)
        hist = train(model=m, env=env, n_iterations=3, cfg=cfg,
                     device=torch.device("cpu"), log_every=1, checkpoint_dir=None)
        assert len(hist) == 3
        assert hist[0]["in_warmup"] == 1.0 and hist[2]["in_warmup"] == 0.0
        assert all(np.isfinite(h["loss_value"]) for h in hist)
        _ok("3-iteration end-to-end train smoke on the real arena env")
    finally:
        env.close()


if __name__ == "__main__":
    for fn in (test_patch_embed, test_encoder_step, test_no_bypass, test_attn_bias,
               test_decoders, test_step_vs_segment, test_done_reset, test_nstep_targets,
               test_per_buffer, test_ema, test_pac_update, test_env_and_train_smoke):
        fn()
    print(f"\nALL TESTS PASSED ({_PASS} checks)")
