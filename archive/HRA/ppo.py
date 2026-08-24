"""
Recurrent PPO with distributional Q critic for HRA.

Combines:
    - Standard PPO (Schulman 2017) clipped-surrogate policy update.
    - GAE (Schulman 2016) advantage estimation.
    - Truncated BPTT across the three recurrent hidden states (C_1, C_2, C_3).
    - PRISM v2's action-conditional distributional Q critic loss (QR-Huber on
      the executed-action quantile slice — see ../Prism/docs/PRISM_V2/Q_CRITIC.md).
    - PRISM v1's PC auxiliary loss (the only environment-agnostic auxiliary).
    - PRISM v1's optional "PC-only pretrain" phase that forces action=0 in the
      rollout so the model can learn the env's visual structure before RL.

Adapted from Prism/ppo.py + PrismV2/ppo.py; cleaned up and re-targeted at
HRA's hidden-state tuple.

Pseudo-code per iteration:

    1. Rollout (no_grad)
        for each episode:
            states = model.init_states(1)
            for t in episode:
                step = model.forward_step(x_t, states)
                a_t ~ Categorical(step.action_logits)
                store (obs, a_t, r_t, done, logp, V, q_dist[a_t])
                states = step.layer_states_new

    2. Advantage / return (GAE) on stored V baselines.

    3. PPO update (with gradient)
        for each PPO epoch:
            states = model.init_states(B)
            for each BPTT chunk:
                states = detach(states)
                for t in chunk:
                    step = model.forward_step(x_t, states)
                    accumulate logits, q_dist, pc_loss
                    states = step.layer_states_new
                gather q_dist[a_t] → q_at_t  (B, T, N)
                loss = -clipped_surrogate(logits, actions, adv)
                     + value_coef * quantile_huber_loss(q_at_t, returns, mask)
                     + entropy_coef * (-H)
                     + pc_coef * loss_pc
                step optimizer
"""
from __future__ import annotations

import collections
import os
import time
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.distributions import Categorical

try:
    from .losses import quantile_huber_loss, slowness_loss
    from .model import HRAModel
except ImportError:  # pragma: no cover
    from losses import quantile_huber_loss, slowness_loss  # type: ignore[no-redef]
    from model import HRAModel  # type: ignore[no-redef]


# ─────────────────────────────────────────────────────────────────────────────
# Rollout storage
# ─────────────────────────────────────────────────────────────────────────────


def _model_kwargs_from(model) -> dict:
    """
    Snapshot the constructor kwargs needed to rebuild ``model`` from scratch.
    Saved alongside the state dict so that analysis tools can re-instantiate
    the same architecture without needing to know the config used at training
    time (especially important for the cross_layer_via flag, which adds /
    removes parameters in the cells' FeedbackTransformer projections).
    """
    actor_n_actions = int(model.actor.fc2.bias.numel())
    actor_logit_bias = model.actor.fc2.bias.detach().cpu().tolist()
    return {
        "in_channels": int(model.in_channels),
        "image_h": int(model.image_h),
        "image_w": int(model.image_w),
        "state_channels": tuple(int(c) for c in model.state_channels),
        "n_FR": int(model.n_FR),
        "n_heads": int(getattr(model.cell1, "n_heads", 4)),
        "n_actions": actor_n_actions,
        "init_action_logit_bias": actor_logit_bias,
        "critic_kind": str(model.critic_kind),
        "n_quantiles": int(getattr(model, "n_quantiles", 0)),
        "cross_layer_via": str(getattr(model, "cross_layer_via", "input")),
        "enable_skips": bool(getattr(model, "enable_skips", True)),
        "pc_coef": float(model.pc_coef),
    }


@dataclass
class RolloutBatch:
    """One batch of complete episodes collected on-policy."""

    observations: torch.Tensor   # (B, T, 3, 50, 50)
    actions: torch.Tensor        # (B, T)            long
    rewards: torch.Tensor        # (B, T)
    dones: torch.Tensor          # (B, T)            float 0/1
    valid_mask: torch.Tensor     # (B, T)            float 0/1 (1 if t < length)
    old_log_probs: torch.Tensor  # (B, T)
    old_values: torch.Tensor     # (B, T)            scalar V baseline at rollout
    last_values: torch.Tensor    # (B,)              bootstrap V at terminal step
    lengths: torch.Tensor        # (B,)              long


# ─────────────────────────────────────────────────────────────────────────────
# Rollout collection
# ─────────────────────────────────────────────────────────────────────────────


def _detach_states(states: Tuple[torch.Tensor, ...]) -> Tuple[torch.Tensor, ...]:
    return tuple(s.detach() for s in states)


def collect_episodes(
    model: HRAModel,
    env,
    n_episodes: int,
    device: torch.device,
    force_action: Optional[int] = None,
) -> Tuple[RolloutBatch, dict]:
    """
    Roll out `n_episodes` episodes on `env` with the current `model`.

    The env is ChangeDetectionEnv (or compatible): .reset() returns a numpy
    (50,50,3) float obs in [-1, 1]; .step(int) returns (next_obs, r, done, ...).
    """
    model.eval()

    obs_list: list[list[np.ndarray]] = []
    act_list: list[list[int]] = []
    rew_list: list[list[float]] = []
    done_list: list[list[float]] = []
    logp_list: list[list[float]] = []
    val_list: list[list[float]] = []

    ep_returns: list[float] = []
    ep_lengths: list[int] = []
    ep_correct: list[float] = []

    with torch.no_grad():
        for _ in range(n_episodes):
            obs = env.reset()
            if isinstance(obs, tuple):  # gymnasium can return (obs, info)
                obs = obs[0]
            states = model.init_states(batch_size=1, device=device)

            obs_e: list[np.ndarray] = []
            act_e: list[int] = []
            rew_e: list[float] = []
            done_e: list[float] = []
            logp_e: list[float] = []
            val_e: list[float] = []

            done = False
            ep_return = 0.0
            while not done:
                obs_arr = np.asarray(obs, dtype=np.float32)
                obs_e.append(obs_arr)

                # (H, W, C) → (1, C, H, W) for the V1 stem.
                x_t = torch.from_numpy(np.ascontiguousarray(obs_arr.transpose(2, 0, 1))).to(device).unsqueeze(0)
                step = model.forward_step(x_t, states)

                logits = step.action_logits[0]  # (n_actions,)
                dist = Categorical(logits=logits)
                if force_action is not None:
                    a = torch.tensor(force_action, device=device, dtype=torch.long)
                else:
                    a = dist.sample()
                logp = dist.log_prob(a).item()
                value = step.value[0].item()

                step_result = env.step(int(a.item()))
                if len(step_result) == 5:  # gymnasium
                    next_obs, r, terminated, truncated, _ = step_result
                    done = bool(terminated or truncated)
                else:  # gym
                    next_obs, r, done, _ = step_result

                act_e.append(int(a.item()))
                rew_e.append(float(r))
                done_e.append(1.0 if done else 0.0)
                logp_e.append(float(logp))
                val_e.append(float(value))

                states = step.layer_states_new
                obs = next_obs
                ep_return += float(r)

            # Episode terminated; bootstrap V = 0 at terminal state.
            obs_list.append(obs_e)
            act_list.append(act_e)
            rew_list.append(rew_e)
            done_list.append(done_e)
            logp_list.append(logp_e)
            val_list.append(val_e)

            ep_returns.append(ep_return)
            ep_lengths.append(len(rew_e))
            ep_correct.append(1.0 if any(r > 0 for r in rew_e) else 0.0)

    T_max = max(len(seq) for seq in obs_list)
    B = len(obs_list)

    def _pad(seq, fill_shape, dtype):
        out = np.zeros((T_max, *fill_shape), dtype=dtype)
        for i, v in enumerate(seq):
            out[i] = v
        return out

    obs_arr = np.stack([_pad(seq, (50, 50, 3), np.float32) for seq in obs_list], axis=0)
    obs_arr = np.ascontiguousarray(np.transpose(obs_arr, (0, 1, 4, 2, 3)))  # (B, T, 3, 50, 50)
    actions = np.stack([_pad(seq, (), np.int64) for seq in act_list], axis=0)
    rewards = np.stack([_pad(seq, (), np.float32) for seq in rew_list], axis=0)
    dones = np.stack([_pad(seq, (), np.float32) for seq in done_list], axis=0)
    logps = np.stack([_pad(seq, (), np.float32) for seq in logp_list], axis=0)
    vals = np.stack([_pad(seq, (), np.float32) for seq in val_list], axis=0)
    lengths = np.array([len(seq) for seq in obs_list], dtype=np.int64)

    valid = np.zeros((B, T_max), dtype=np.float32)
    for b, L in enumerate(lengths):
        valid[b, :L] = 1.0

    batch = RolloutBatch(
        observations=torch.from_numpy(obs_arr).to(device),
        actions=torch.from_numpy(actions).to(device),
        rewards=torch.from_numpy(rewards).to(device),
        dones=torch.from_numpy(dones).to(device),
        valid_mask=torch.from_numpy(valid).to(device),
        old_log_probs=torch.from_numpy(logps).to(device),
        old_values=torch.from_numpy(vals).to(device),
        last_values=torch.zeros(B, dtype=torch.float32, device=device),  # env always terminates
        lengths=torch.from_numpy(lengths).to(device),
    )
    stats = {
        "rollout/mean_return": float(np.mean(ep_returns)),
        "rollout/mean_length": float(np.mean(ep_lengths)),
        "rollout/correct_rate": float(np.mean(ep_correct)),
        "rollout/n_episodes": float(n_episodes),
    }
    return batch, stats


# ─────────────────────────────────────────────────────────────────────────────
# GAE
# ─────────────────────────────────────────────────────────────────────────────


def compute_gae(
    rewards: torch.Tensor,
    values: torch.Tensor,
    dones: torch.Tensor,
    valid: torch.Tensor,
    last_values: torch.Tensor,
    gamma: float,
    lam: float,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Generalized Advantage Estimation. Same as Prism/ppo.py.
    """
    B, T = rewards.shape
    advantages = torch.zeros_like(rewards)
    last_adv = torch.zeros(B, device=rewards.device, dtype=rewards.dtype)
    next_value = last_values

    for t in reversed(range(T)):
        not_done = 1.0 - dones[:, t]
        m = valid[:, t]
        delta = rewards[:, t] + gamma * next_value * not_done - values[:, t]
        last_adv = delta + gamma * lam * not_done * last_adv
        advantages[:, t] = last_adv * m
        next_value = values[:, t]

    returns = (advantages + values) * valid

    # Normalize advantages over valid positions.
    valid_flat = valid.flatten()
    adv_flat = advantages.flatten()
    n_valid = valid_flat.sum().clamp(min=1.0)
    mean_adv = (adv_flat * valid_flat).sum() / n_valid
    var_adv = ((adv_flat - mean_adv).pow(2) * valid_flat).sum() / n_valid
    std_adv = (var_adv + 1e-8).sqrt()
    advantages = (advantages - mean_adv) / std_adv * valid

    return advantages, returns


# ─────────────────────────────────────────────────────────────────────────────
# PPO config
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PPOConfig:
    # Optimization.
    lr: float = 3e-4
    n_epochs: int = 4
    clip_range: float = 0.2
    value_coef: float = 0.5
    entropy_coef: float = 0.01
    pc_coef: float = 1.0
    slow_coef: float = 0.0
    grad_clip: float = 0.5

    # Distributional critic.
    value_huber_kappa: float = 1.0  # QR-Huber transition (Dabney 2018 default)

    # Discounting.
    gamma: float = 0.95
    gae_lambda: float = 0.95

    # Truncated BPTT (chunk length; 0 = no truncation).
    bptt_truncation: int = 16

    # PC-only pretrain: force action=0 for the first N iterations and skip
    # PPO surrogate/value/entropy losses. Lets the recurrent stack learn the
    # env's visual statistics before the actor starts thrashing.
    pc_pretrain_iters: int = 0

    # ─── Stability knobs (added after iter-888 crash post-mortem) ───
    #
    # return_clip: clip GAE return targets to [-return_clip, +return_clip]
    # before feeding them to the value loss. The env's reward magnitude is
    # bounded (max ~5 here), so undiscounted returns sit in [0, ~5]. Without
    # clipping, a transient large Q-distribution outlier can blow up the
    # QR-Huber linear-regime gradient → grad clip can't save it → NaN.
    # 0 disables.
    return_clip: float = 5.0
    #
    # kl_early_stop: if the PPO inner-loop approx-kl exceeds this after any
    # epoch's update, stop the remaining epochs early. Standard PPO trick
    # (Schulman et al. 2017 §6). 0 disables.
    kl_early_stop: float = 0.02
    #
    # Logit clamp on the actor output. Prevents Categorical(NaN) crashes from
    # extreme logits. The clamp range is one-sided (max-magnitude); pre-softmax
    # logits beyond ±20 are pathological anyway. 0 disables.
    actor_logit_clamp: float = 20.0


# ─────────────────────────────────────────────────────────────────────────────
# PC pretrain update
# ─────────────────────────────────────────────────────────────────────────────


def pc_pretrain_update(
    model: HRAModel,
    optimizer: torch.optim.Optimizer,
    batch: RolloutBatch,
    cfg: PPOConfig,
) -> dict:
    model.train()
    B, T = batch.observations.shape[:2]
    device = batch.observations.device
    chunk = cfg.bptt_truncation if cfg.bptt_truncation > 0 else T
    starts = list(range(0, T, chunk))

    total_pc = 0.0
    n_updates = 0
    for _epoch in range(cfg.n_epochs):
        states = model.init_states(B, device=device)
        for t0 in starts:
            t1 = min(t0 + chunk, T)
            states = _detach_states(states)
            pc_per_step = []
            for t in range(t1 - t0):
                step = model.forward_step(batch.observations[:, t0 + t].contiguous(), states)
                pc_per_step.append(step.pc_loss)
                states = step.layer_states_new

            loss = cfg.pc_coef * torch.stack(pc_per_step).mean()
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            grad_norm = nn.utils.clip_grad_norm_(model.parameters(), max_norm=cfg.grad_clip)
            # Same inf*0=NaN guard as the main ppo_update path (see comment there).
            if not torch.isfinite(grad_norm):
                optimizer.zero_grad(set_to_none=True)
                # No nan_skip counter in pretrain stats; just skip.
                continue
            optimizer.step()

            total_pc += float(loss.detach().item()) / max(cfg.pc_coef, 1e-9)
            n_updates += 1
    n = max(n_updates, 1)
    return {
        "loss_pc": total_pc / n,
        "loss_policy": 0.0, "loss_value": 0.0, "loss_entropy": 0.0,
        "loss_slow": 0.0, "loss_total": total_pc / n,
        "approx_kl": 0.0, "clip_frac": 0.0,
        "critic_std": 0.0, "dQ": 0.0,
        "n_updates": float(n_updates),
    }


# ─────────────────────────────────────────────────────────────────────────────
# PPO update with distributional Q critic
# ─────────────────────────────────────────────────────────────────────────────


def ppo_update(
    model: HRAModel,
    optimizer: torch.optim.Optimizer,
    batch: RolloutBatch,
    cfg: PPOConfig,
) -> dict:
    """Recurrent PPO update with distributional Q critic + PC auxiliary."""
    model.train()
    using_dist = model.critic_kind == "distributional"

    advantages, returns = compute_gae(
        rewards=batch.rewards,
        values=batch.old_values,
        dones=batch.dones,
        valid=batch.valid_mask,
        last_values=batch.last_values,
        gamma=cfg.gamma,
        lam=cfg.gae_lambda,
    )

    B, T = batch.observations.shape[:2]
    device = batch.observations.device
    chunk = cfg.bptt_truncation if cfg.bptt_truncation > 0 else T
    starts = list(range(0, T, chunk))

    # Apply return clipping (stability).
    if cfg.return_clip > 0:
        returns = returns.clamp(-cfg.return_clip, cfg.return_clip)

    accum = collections.defaultdict(float)
    early_stopped_at_epoch = -1

    for epoch_idx in range(cfg.n_epochs):
        states = model.init_states(B, device=device)
        epoch_kl_sum = 0.0
        epoch_kl_n = 0

        for t0 in starts:
            t1 = min(t0 + chunk, T)
            valid_chunk = batch.valid_mask[:, t0:t1]
            actions_chunk = batch.actions[:, t0:t1]
            old_logp_chunk = batch.old_log_probs[:, t0:t1]
            adv_chunk = advantages[:, t0:t1]
            ret_chunk = returns[:, t0:t1]

            states = _detach_states(states)

            logits_seq, values_seq, q_dist_seq, pc_steps = [], [], [], []
            for t in range(t1 - t0):
                step = model.forward_step(batch.observations[:, t0 + t].contiguous(), states)
                logits_seq.append(step.action_logits)
                values_seq.append(step.value)
                q_dist_seq.append(step.q_dist)
                pc_steps.append(step.pc_loss)
                states = step.layer_states_new

            logits_t = torch.stack(logits_seq, dim=1)              # (B, T, |A|)
            values_t = torch.stack(values_seq, dim=1)              # (B, T)
            q_dist_t = torch.stack(q_dist_seq, dim=1)              # (B, T, |A|, N)
            pc_t = torch.stack(pc_steps, dim=0)                    # (T,)

            # NaN guard: if the forward pass produced NaN somewhere, skip this
            # update step (logging a diagnostic). Keeps training from crashing.
            if not torch.isfinite(logits_t).all():
                accum["n_nan_skips"] += 1
                continue

            # Stability: clamp actor logits to a sane range pre-softmax.
            if cfg.actor_logit_clamp > 0:
                logits_t = logits_t.clamp(-cfg.actor_logit_clamp, cfg.actor_logit_clamp)

            # PPO surrogate.
            dist = Categorical(logits=logits_t)
            new_logp = dist.log_prob(actions_chunk)
            entropy = dist.entropy()
            ratio = (new_logp - old_logp_chunk).exp()
            unclipped = ratio * adv_chunk
            clipped = ratio.clamp(1.0 - cfg.clip_range, 1.0 + cfg.clip_range) * adv_chunk
            surrogate = -torch.min(unclipped, clipped)

            m = valid_chunk
            denom = m.sum().clamp(min=1.0)
            loss_policy = (surrogate * m).sum() / denom
            loss_entropy = -(entropy * m).sum() / denom

            # Value / Q loss.
            if using_dist:
                # Gather Q(s_t, a_t; ·) — the action-conditional distributional
                # critic is supervised only on the executed action's column.
                Bc, Tc, Ac, Nc = q_dist_t.shape
                act_idx = actions_chunk.view(Bc, Tc, 1, 1).expand(Bc, Tc, 1, Nc)
                q_at_t = q_dist_t.gather(2, act_idx).squeeze(2)  # (B, T, N)
                loss_value = quantile_huber_loss(q_at_t, ret_chunk, m, kappa=cfg.value_huber_kappa)
            else:
                # Scalar critic fallback (ablation).
                loss_value = (((values_t - ret_chunk) ** 2) * m).sum() / denom

            # PC loss — mask-weighted per timestep.
            valid_per_t = valid_chunk.sum(dim=0)
            valid_total = valid_per_t.sum().clamp(min=1.0)
            loss_pc = (pc_t * valid_per_t).sum() / valid_total

            # Slowness on C_1 (optional).
            loss_slow = torch.tensor(0.0, device=device)
            # (deferred to future work; HRA exposes 3 states which makes slowness
            # ambiguous about which layer's slowness to penalise.)

            loss = (
                loss_policy
                + cfg.value_coef * loss_value
                + cfg.entropy_coef * loss_entropy
                + cfg.pc_coef * loss_pc
                + cfg.slow_coef * loss_slow
            )

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            grad_norm = nn.utils.clip_grad_norm_(model.parameters(), max_norm=cfg.grad_clip)
            # Non-finite-gradient guard. `clip_grad_norm_` returns inf if any
            # parameter's grad is inf, then internally multiplies all grads by
            # (max_norm / inf) = 0 — but in IEEE-754 inf * 0 = NaN. So the
            # offending parameter ends up with NaN gradient, which Adam writes
            # into m/v moments, and the next forward pass produces NaN weights.
            # To break that cycle: explicitly zero the grads and skip the
            # optimizer step. (The grads have already been mul_'d by zero by
            # clip_grad_norm_ — except for the inf-grad params which are NaN.
            # `zero_grad(set_to_none=True)` is fastest and cleanest.)
            if not torch.isfinite(grad_norm):
                optimizer.zero_grad(set_to_none=True)
                accum["n_nan_skips"] += 1
                # Populate ALL diagnostic keys so the format string in train()
                # never sees a missing key — even if every chunked update in
                # the iteration takes this branch. Loss values are real (they
                # were just computed); diagnostics get zero sentinels.
                accum["loss_policy"] += float(loss_policy.detach().item())
                accum["loss_value"] += float(loss_value.detach().item())
                accum["loss_entropy"] += float(loss_entropy.detach().item())
                accum["loss_pc"] += float(loss_pc.detach().item())
                accum["loss_slow"] += float(loss_slow.detach().item())
                accum["loss_total"] += float(loss.detach().item())
                accum["approx_kl"] += 0.0
                accum["clip_frac"] += 0.0
                accum["critic_std"] += 0.0
                accum["dQ"] += 0.0
                accum["grad_norm"] += 0.0
                accum["q_max_abs"] += 0.0
                accum["n_updates"] += 1
                continue
            optimizer.step()

            with torch.no_grad():
                approx_kl = (((ratio - 1) - (new_logp - old_logp_chunk)) * m).sum() / denom
                clip_frac = (((ratio < 1 - cfg.clip_range) | (ratio > 1 + cfg.clip_range)).float() * m).sum() / denom
                if using_dist:
                    critic_std = q_at_t.std(dim=-1).mean()
                    q_mean_per_action = q_dist_t.mean(dim=-1)        # (B, T, |A|)
                    dQ = (q_mean_per_action.max(dim=-1).values - q_mean_per_action.min(dim=-1).values).mean()
                    # Max abs Q across the whole batch — early-warning for runaway quantiles.
                    q_max_abs = q_dist_t.abs().max()
                else:
                    critic_std = torch.tensor(0.0, device=device)
                    dQ = torch.tensor(0.0, device=device)
                    q_max_abs = torch.tensor(0.0, device=device)

            accum["loss_policy"] += float(loss_policy.detach().item())
            accum["loss_value"] += float(loss_value.detach().item())
            accum["loss_entropy"] += float(loss_entropy.detach().item())
            accum["loss_pc"] += float(loss_pc.detach().item())
            accum["loss_slow"] += float(loss_slow.detach().item())
            accum["loss_total"] += float(loss.detach().item())
            accum["approx_kl"] += float(approx_kl.detach().item())
            accum["clip_frac"] += float(clip_frac.detach().item())
            accum["critic_std"] += float(critic_std.detach().item())
            accum["dQ"] += float(dQ.detach().item())
            accum["grad_norm"] += float(grad_norm.detach().item() if hasattr(grad_norm, "detach") else float(grad_norm))
            accum["q_max_abs"] += float(q_max_abs.detach().item())
            accum["n_updates"] += 1

            epoch_kl_sum += float(approx_kl.detach().item())
            epoch_kl_n += 1

        # KL early stopping at end of each PPO epoch.
        if cfg.kl_early_stop > 0 and epoch_kl_n > 0:
            mean_kl_this_epoch = epoch_kl_sum / epoch_kl_n
            if mean_kl_this_epoch > cfg.kl_early_stop:
                early_stopped_at_epoch = epoch_idx
                break

    n = max(accum["n_updates"], 1.0)
    result = {k: v / n if k not in ("n_updates", "n_nan_skips") else v for k, v in accum.items()}
    result["early_stop_epoch"] = float(early_stopped_at_epoch)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Top-level train loop
# ─────────────────────────────────────────────────────────────────────────────


def train(
    model: HRAModel,
    env,
    *,
    n_iterations: int = 1000,
    episodes_per_iter: int = 8,
    cfg: PPOConfig = PPOConfig(),
    device: Optional[torch.device] = None,
    log_every: int = 1,
    rolling_window: int = 50,
    checkpoint_dir: Optional[str] = None,
    save_every: int = 500,
) -> list[dict]:
    """
    Outer training loop. Each iteration:
      1) collect_episodes (no_grad)
      2) PPO update (or PC-pretrain update if it < cfg.pc_pretrain_iters)
      3) log
    """
    if device is None:
        device = next(model.parameters()).device

    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr, eps=1e-5)
    history: list[dict] = []

    # Startup diagnostics.
    with torch.no_grad():
        actor_bias = model.actor.fc2.bias.detach().cpu().tolist()
    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[diag] params         : {n_params:,}")
    print(f"[diag] critic_kind    : {model.critic_kind} (n_quantiles={model.n_quantiles})")
    print(f"[diag] actor.fc2.bias : {actor_bias}")
    print(f"[diag] n_FR           : {model.n_FR}")
    print(f"[diag] state_channels : {model.state_channels}")
    print(f"[diag] PPO coefs      : value={cfg.value_coef}, entropy={cfg.entropy_coef}, pc={cfg.pc_coef}")
    print(f"[diag] pretrain       : pc_pretrain_iters={cfg.pc_pretrain_iters}")

    _correct_buf: collections.deque = collections.deque(maxlen=rolling_window)
    _return_buf: collections.deque = collections.deque(maxlen=rolling_window)

    if cfg.pc_pretrain_iters > 0:
        print(
            f"[PC pretrain] forcing action=0 for {cfg.pc_pretrain_iters} iters "
            f"({cfg.pc_pretrain_iters * episodes_per_iter} episodes); "
            f"PPO starts at iter {cfg.pc_pretrain_iters}."
        )

    t_start = time.time()
    for it in range(n_iterations):
        in_pretrain = it < cfg.pc_pretrain_iters
        if cfg.pc_pretrain_iters > 0 and it == cfg.pc_pretrain_iters:
            print(f"[PC pretrain] iter {it}: pretrain done — switching to PPO.")

        batch, rollout_stats = collect_episodes(
            model=model,
            env=env,
            n_episodes=episodes_per_iter,
            device=device,
            force_action=0 if in_pretrain else None,
        )
        update_stats = (
            pc_pretrain_update(model, optimizer, batch, cfg)
            if in_pretrain
            else ppo_update(model, optimizer, batch, cfg)
        )

        _correct_buf.append(rollout_stats["rollout/correct_rate"])
        _return_buf.append(rollout_stats["rollout/mean_return"])
        roll_correct = sum(_correct_buf) / len(_correct_buf)
        roll_return = sum(_return_buf) / len(_return_buf)

        log = {
            "iter": it,
            **rollout_stats,
            **update_stats,
            "rolling/correct_rate": roll_correct,
            "rolling/mean_return": roll_return,
        }
        history.append(log)

        if (it + 1) % log_every == 0:
            elapsed = time.time() - t_start
            phase = "pretrain" if in_pretrain else "ppo"
            n_eps = (it + 1) * episodes_per_iter
            # Extra stability diagnostics (only shown for PPO updates).
            extras = ""
            if not in_pretrain:
                extras = (
                    f" gn={log.get('grad_norm', 0):.3f} "
                    f"|Q|={log.get('q_max_abs', 0):.2f} "
                    f"earlystop@={int(log.get('early_stop_epoch', -1))} "
                    f"nan_skip={int(log.get('n_nan_skips', 0))}"
                )
            print(
                f"[{phase} {it:4d} | ep {n_eps:6d} | {elapsed:6.1f}s] "
                f"correct={roll_correct:.3f}({rolling_window}it) "
                f"return={roll_return:.3f} "
                f"len={log.get('rollout/mean_length', 0.0):.1f} "
                f"L_PC={log.get('loss_pc', 0.0):.4f} "
                f"H={-log.get('loss_entropy', 0.0):.3f} "
                f"L_V={log.get('loss_value', 0.0):.4f} "
                f"dQ={log.get('dQ', 0.0):.3f} "
                f"KL={log.get('approx_kl', 0.0):.4f}"
                f"{extras}"
            )

        if checkpoint_dir is not None and (it + 1) % save_every == 0:
            os.makedirs(checkpoint_dir, exist_ok=True)
            ckpt_path = os.path.join(checkpoint_dir, "hra_latest.pt")
            torch.save({
                "model_state_dict": model.state_dict(),
                "model_kwargs": _model_kwargs_from(model),
                "iter": it,
            }, ckpt_path)
            print(f"[checkpoint] saved to {ckpt_path}")

    return history
