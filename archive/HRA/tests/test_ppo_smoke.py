"""
PPO smoke test — verifies the training loop runs end-to-end.

Doesn't check learning, only that:
  - collect_episodes runs without error
  - compute_gae produces sensible-shaped tensors
  - ppo_update runs a backward pass with the distributional Q critic loss
  - pc_pretrain_update runs without error
  - the gradient routing through the distributional head is correct

Faster than test_shapes.py? No — runs actual rollouts. But it's still meant to
finish in under ~30 seconds with a small config.

Run:
    /usr/bin/python3 HRA/tests/test_ppo_smoke.py
"""
from __future__ import annotations

import os
import sys
import time
import traceback

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from HRA.env import ChangeDetectionEnv
from HRA.model import HRAModel
from HRA.ppo import PPOConfig, collect_episodes, compute_gae, pc_pretrain_update, ppo_update


_PASSED = 0
_FAILED = 0


def _check(name, condition, detail=""):
    global _PASSED, _FAILED
    if condition:
        _PASSED += 1
        print(f"  PASS  {name}")
    else:
        _FAILED += 1
        msg = f"  FAIL  {name}"
        if detail:
            msg += f"  ({detail})"
        print(msg)


def _build_small_model(critic_kind="distributional"):
    return HRAModel(
        in_channels=3, image_h=50, image_w=50,
        state_channels=(16, 32, 64),  # smaller for speed
        n_FR=3,
        n_heads=2,
        decision_dim=32,
        actor_hidden=32,
        critic_hidden=32,
        n_actions=2,
        init_action_logit_bias=[0.0, -4.0],
        critic_kind=critic_kind,
        n_quantiles=21,
    )


def test_rollout():
    print("\n[1] collect_episodes ---")
    device = torch.device("cpu")
    model = _build_small_model().to(device)
    env = ChangeDetectionEnv()
    t0 = time.time()
    batch, stats = collect_episodes(model, env, n_episodes=4, device=device)
    elapsed = time.time() - t0
    print(f"     elapsed: {elapsed:.2f}s for 4 episodes")

    _check("batch.observations is 5D", batch.observations.dim() == 5)
    _check("batch.observations channels=3, H=50, W=50",
           batch.observations.shape[-3:] == (3, 50, 50))
    B, T = batch.observations.shape[:2]
    _check("batch.actions shape (B, T)", tuple(batch.actions.shape) == (B, T))
    _check("batch.rewards shape (B, T)", tuple(batch.rewards.shape) == (B, T))
    _check("batch.valid_mask shape (B, T)", tuple(batch.valid_mask.shape) == (B, T))
    _check("batch.lengths shape (B,)", tuple(batch.lengths.shape) == (B,))
    _check("rollout stats present",
           "rollout/mean_return" in stats and "rollout/correct_rate" in stats)
    return batch


def test_gae(batch):
    print("\n[2] compute_gae ---")
    adv, ret = compute_gae(
        rewards=batch.rewards, values=batch.old_values, dones=batch.dones,
        valid=batch.valid_mask, last_values=batch.last_values,
        gamma=0.95, lam=0.95,
    )
    _check("adv shape matches rewards", tuple(adv.shape) == tuple(batch.rewards.shape))
    _check("ret shape matches rewards", tuple(ret.shape) == tuple(batch.rewards.shape))
    _check("adv has finite values", torch.isfinite(adv).all().item())
    _check("ret has finite values", torch.isfinite(ret).all().item())


def test_ppo_update_distributional():
    print("\n[3] ppo_update (distributional critic) ---")
    device = torch.device("cpu")
    model = _build_small_model(critic_kind="distributional").to(device)
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(model, env, n_episodes=4, device=device)

    cfg = PPOConfig(lr=3e-4, n_epochs=2, bptt_truncation=8)
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr, eps=1e-5)

    # Snapshot a parameter to verify it moves.
    p_critic_before = model.critic.fc2.weight.detach().clone()
    p_actor_before = model.actor.fc2.weight.detach().clone()

    stats = ppo_update(model, optimizer, batch, cfg)

    _check("ppo_update returns stats dict", isinstance(stats, dict))
    for k in ("loss_policy", "loss_value", "loss_entropy", "loss_pc",
              "loss_total", "approx_kl", "clip_frac", "critic_std", "dQ"):
        _check(f"stats has '{k}'", k in stats)
    _check("loss_total is finite", torch.isfinite(torch.tensor(stats["loss_total"])).item())
    _check("loss_value > 0 (distributional)", stats["loss_value"] > 0)

    moved_critic = not torch.allclose(model.critic.fc2.weight, p_critic_before)
    moved_actor = not torch.allclose(model.actor.fc2.weight, p_actor_before)
    _check("critic.fc2 weights moved", moved_critic)
    _check("actor.fc2 weights moved", moved_actor)


def test_ppo_update_scalar_ablation():
    print("\n[4] ppo_update (scalar critic ablation) ---")
    device = torch.device("cpu")
    model = _build_small_model(critic_kind="scalar").to(device)
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(model, env, n_episodes=4, device=device)

    cfg = PPOConfig(lr=3e-4, n_epochs=2, bptt_truncation=8)
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr, eps=1e-5)
    stats = ppo_update(model, optimizer, batch, cfg)

    _check("scalar critic ppo_update runs", isinstance(stats, dict))
    _check("scalar critic loss_value > 0", stats["loss_value"] > 0)
    _check("scalar critic dQ == 0 (sentinel)", stats["dQ"] == 0.0)


def test_pc_pretrain():
    print("\n[5] pc_pretrain_update ---")
    device = torch.device("cpu")
    model = _build_small_model().to(device)
    env = ChangeDetectionEnv()
    # Force action=0 for the rollout (analog of cfg.pc_pretrain_iters > 0).
    batch, _ = collect_episodes(model, env, n_episodes=4, device=device, force_action=0)

    cfg = PPOConfig(lr=3e-4, n_epochs=2, bptt_truncation=8)
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr, eps=1e-5)

    p_before = model.pixel_decoder_c1.conv_out.weight.detach().clone()
    stats = pc_pretrain_update(model, optimizer, batch, cfg)
    _check("pc_pretrain_update returns dict", isinstance(stats, dict))
    _check("pc_pretrain L_PC > 0", stats["loss_pc"] > 0)
    moved = not torch.allclose(model.pixel_decoder_c1.conv_out.weight, p_before)
    _check("PC pretrain moves the pixel decoder", moved)


def test_actor_protected_from_value_loss():
    """Verify that the value loss (alone) does NOT update the actor head.
    This is the Q_CRITIC.md §2.4 protection."""
    print("\n[6] Actor protected from value loss (Q_CRITIC §2.4) ---")
    device = torch.device("cpu")
    model = _build_small_model(critic_kind="distributional").to(device)
    env = ChangeDetectionEnv()
    batch, _ = collect_episodes(model, env, n_episodes=2, device=device)

    p_actor_before = model.actor.fc2.weight.detach().clone()

    # Manually run a forward pass and compute *only* the value loss.
    # If the stop-gradient is correct, the actor head should not be updated.
    optimizer = torch.optim.Adam(model.parameters(), lr=3e-4, eps=1e-5)
    states = model.init_states(batch.observations.shape[0], device=device)

    Bc, Tc = batch.observations.shape[:2]
    q_dist_list = []
    for t in range(Tc):
        step = model.forward_step(batch.observations[:, t].contiguous(), states)
        q_dist_list.append(step.q_dist)
        states = step.layer_states_new
    q_dist_t = torch.stack(q_dist_list, dim=1)
    act_idx = batch.actions.view(Bc, Tc, 1, 1).expand(Bc, Tc, 1, q_dist_t.shape[-1])
    q_at_t = q_dist_t.gather(2, act_idx).squeeze(2)

    from HRA.losses import quantile_huber_loss
    # Use the returns as the target — doesn't matter what specifically, just
    # need a real loss whose backward we can trace.
    fake_returns = batch.rewards
    loss = quantile_huber_loss(q_at_t, fake_returns, batch.valid_mask)

    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

    p_actor_after = model.actor.fc2.weight.detach().clone()
    _check("Actor fc2.weight unchanged after value-only update",
           torch.allclose(p_actor_before, p_actor_after))


def main():
    print("HRA Stage 1 — PPO smoke test")
    print("=" * 60)
    try:
        batch = test_rollout()
        test_gae(batch)
        test_ppo_update_distributional()
        test_ppo_update_scalar_ablation()
        test_pc_pretrain()
        test_actor_protected_from_value_loss()
    except Exception:
        traceback.print_exc()
        print("\nUNEXPECTED EXCEPTION — see traceback above.")
        return 2

    print("=" * 60)
    print(f"  passed: {_PASSED}    failed: {_FAILED}")
    if _FAILED == 0:
        print("  PPO SMOKE TEST: PASS")
        return 0
    print("  PPO SMOKE TEST: FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
