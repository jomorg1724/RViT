"""
Recurrent PPO trainer for PRISM v2.

Same algorithm as PRISM v1's `Prism/ppo.py` (clipped surrogate, GAE,
truncated BPTT, joint PC auxiliary loss, PC-only pretrain phase, inner-K
warmup) — extended to handle PRISM v2's TWO recurrent memory states
(M_fast and M_slow) instead of one.

Specifically:
  - `collect_episodes` carries both memories in the no-grad rollout.
  - `ppo_update` and `pc_pretrain_update` initialize and propagate both
    memory states across the truncated-BPTT chunks, detaching at chunk
    boundaries.
  - `inner_K_warmup_iters` now caches and restores BOTH inner_K_fast
    and inner_K_slow.

See ../Prism/ppo.py for the algorithmic discussion (PPO equations, GAE,
masking, etc.); this file is a structural extension.
"""
from __future__ import annotations

import collections
import os
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical

try:
    from .losses import predictive_coding_loss, quantile_huber_loss, slowness_loss
    from .model import PrismV2Model
except ImportError:
    from losses import predictive_coding_loss, quantile_huber_loss, slowness_loss  # type: ignore[no-redef]
    from model import PrismV2Model  # type: ignore[no-redef]


# ─────────────────────────────────────────────────────────────────────────────
# Rollout storage
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class RolloutBatch:
    observations: torch.Tensor   # (B, T_max, 3, 50, 50)
    actions: torch.Tensor        # (B, T_max)         long
    rewards: torch.Tensor        # (B, T_max)         float32
    dones: torch.Tensor          # (B, T_max)         float32 (0/1)
    valid_mask: torch.Tensor     # (B, T_max)
    old_log_probs: torch.Tensor  # (B, T_max)
    old_values: torch.Tensor     # (B, T_max)
    last_values: torch.Tensor    # (B,)
    lengths: torch.Tensor        # (B,) long


# ─────────────────────────────────────────────────────────────────────────────
# Rollout collection (no_grad)
# ─────────────────────────────────────────────────────────────────────────────


def collect_episodes(
    model: PrismV2Model,
    env,
    n_episodes: int,
    device: torch.device,
    max_episode_steps: Optional[int] = None,
    force_action: Optional[int] = None,
) -> tuple[RolloutBatch, dict]:
    """Roll out n_episodes; return a padded RolloutBatch + summary stats.

    Carries BOTH memory states (fast and slow) across the env steps.
    """
    model.eval()

    obs_list, act_list, rew_list, done_list, logp_list, val_list = [], [], [], [], [], []
    last_val_list = []
    ep_returns, ep_lengths, ep_correct = [], [], []

    with torch.no_grad():
        for _ in range(n_episodes):
            obs = env.reset()
            M_fast, M_slow = model.init_memory(batch_size=1, device=device)
            obs_e, act_e, rew_e, done_e, logp_e, val_e = [], [], [], [], [], []
            done = False
            ep_return, ep_steps = 0.0, 0
            while not done:
                obs_e.append(obs.astype(np.float32, copy=False))
                x_t = torch.from_numpy(obs.astype(np.float32, copy=False)).to(device)
                x_t = x_t.permute(2, 0, 1).unsqueeze(0).contiguous()
                step_out = model.forward_step(x_t, M_fast, M_slow)

                logits = step_out.action_logits[0]
                # V(s) = Σ_a sg[π(a|s)] · Q(s,a) — already a scalar baseline,
                # computed inside CriticHead.state_value at forward time. Used
                # by GAE; the action-conditional Q tensor is recomputed (with
                # gradient) inside ppo_update so we don't need to store it here.
                value = step_out.value[0].item()

                dist = Categorical(logits=logits)
                if force_action is not None:
                    a = torch.tensor(force_action, device=device)
                else:
                    a = dist.sample()
                logp = dist.log_prob(a).item()

                next_obs, r, done, _ = env.step(int(a.item()))

                act_e.append(int(a.item()))
                rew_e.append(float(r))
                done_e.append(1.0 if done else 0.0)
                logp_e.append(float(logp))
                val_e.append(float(value))

                M_fast = step_out.M_fast_next
                M_slow = step_out.M_slow_next
                obs = next_obs
                ep_return += float(r)
                ep_steps += 1

                if max_episode_steps is not None and ep_steps >= max_episode_steps:
                    break

            last_val_list.append(0.0)  # ChangeDetectionEnv terminates fully

            obs_list.append(obs_e)
            act_list.append(act_e)
            rew_list.append(rew_e)
            done_list.append(done_e)
            logp_list.append(logp_e)
            val_list.append(val_e)

            ep_returns.append(ep_return)
            ep_lengths.append(ep_steps)
            ep_correct.append(1.0 if any(r > 0 for r in rew_e) else 0.0)

    T_max = max(len(seq) for seq in obs_list)

    def _pad_obs(seq, T):
        out = np.zeros((T, 50, 50, 3), dtype=np.float32)
        for i, o in enumerate(seq):
            out[i] = o
        return out

    def _pad_scalar(seq, T, dtype):
        out = np.zeros((T,), dtype=dtype)
        for i, v in enumerate(seq):
            out[i] = v
        return out

    B = len(obs_list)
    obs_arr = np.stack([_pad_obs(seq, T_max) for seq in obs_list], axis=0)
    obs_arr = np.ascontiguousarray(np.transpose(obs_arr, (0, 1, 4, 2, 3)))
    actions = np.stack([_pad_scalar(a, T_max, np.int64) for a in act_list], axis=0)
    rewards = np.stack([_pad_scalar(r, T_max, np.float32) for r in rew_list], axis=0)
    dones = np.stack([_pad_scalar(d, T_max, np.float32) for d in done_list], axis=0)
    logps = np.stack([_pad_scalar(l, T_max, np.float32) for l in logp_list], axis=0)
    vals = np.stack([_pad_scalar(v, T_max, np.float32) for v in val_list], axis=0)
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
        last_values=torch.tensor(last_val_list, dtype=torch.float32, device=device),
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
# GAE (unchanged from PRISM v1)
# ─────────────────────────────────────────────────────────────────────────────


def compute_gae(
    rewards, values, dones, valid, last_values, gamma, lam,
):
    B, T = rewards.shape
    advantages = torch.zeros_like(rewards)
    last_adv = torch.zeros(B, device=rewards.device, dtype=rewards.dtype)
    next_value = last_values
    for t in reversed(range(T)):
        m = valid[:, t]
        not_done = 1.0 - dones[:, t]
        delta = rewards[:, t] + gamma * next_value * not_done - values[:, t]
        last_adv = delta + gamma * lam * not_done * last_adv
        advantages[:, t] = last_adv * m
        next_value = values[:, t]
    returns = (advantages + values) * valid
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
    lr: float = 3e-4
    n_epochs: int = 4
    clip_range: float = 0.2
    value_coef: float = 0.5
    entropy_coef: float = 0.005
    pc_coef: float = 1.0
    slow_coef: float = 0.0
    grad_clip: float = 0.5
    gamma: float = 0.95
    gae_lambda: float = 0.95
    bptt_truncation: int = 16

    # Distributional value head.
    value_huber_kappa: float = 1.0

    # v2-specific: warmups for both inner loops + PC pretrain.
    inner_K_warmup_iters: int = 0
    pc_pretrain_iters: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# PC-only update (pretrain phase)
# ─────────────────────────────────────────────────────────────────────────────


def pc_pretrain_update(
    model: PrismV2Model,
    optimizer: torch.optim.Optimizer,
    batch: RolloutBatch,
    cfg: PPOConfig,
) -> dict:
    """PC-only update used during the pretrain phase.

    Forward through the collected observations with truncated BPTT, compute
    only the predictive-coding loss, backprop, step. No PPO surrogate.
    """
    model.train()
    B, T = batch.observations.shape[:2]
    device = batch.observations.device
    chunk = cfg.bptt_truncation if cfg.bptt_truncation > 0 else T
    starts = list(range(0, T, chunk))

    total_pc = 0.0
    n_updates = 0

    for _epoch in range(cfg.n_epochs):
        Mf, Ms = model.init_memory(B, device=device)
        for t0 in starts:
            t1 = min(t0 + chunk, T)
            x_chunk = batch.observations[:, t0:t1]
            valid_chunk = batch.valid_mask[:, t0:t1]

            Mf, Ms = Mf.detach(), Ms.detach()
            pc_steps = []
            for t in range(t1 - t0):
                step = model.forward_step(x_chunk[:, t].contiguous(), Mf, Ms)
                pc_steps.append(step.pc_loss)
                Mf, Ms = step.M_fast_next, step.M_slow_next

            pc_t = torch.stack(pc_steps, dim=0)
            valid_per_t = valid_chunk.sum(dim=0)
            valid_total = valid_per_t.sum().clamp(min=1.0)
            loss_pc = (pc_t * valid_per_t).sum() / valid_total
            loss = cfg.pc_coef * loss_pc

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=cfg.grad_clip)
            optimizer.step()

            total_pc += float(loss_pc.detach().item())
            n_updates += 1

    n = max(n_updates, 1)
    return {
        "loss_pc": total_pc / n,
        "loss_policy": 0.0, "loss_value": 0.0, "loss_entropy": 0.0,
        "loss_slow": 0.0, "loss_total": total_pc / n,
        "approx_kl": 0.0, "clip_frac": 0.0, "n_updates": float(n_updates),
    }


# ─────────────────────────────────────────────────────────────────────────────
# PPO update
# ─────────────────────────────────────────────────────────────────────────────


def ppo_update(
    model: PrismV2Model,
    optimizer: torch.optim.Optimizer,
    batch: RolloutBatch,
    cfg: PPOConfig,
) -> dict:
    model.train()

    advantages, returns = compute_gae(
        rewards=batch.rewards, values=batch.old_values, dones=batch.dones,
        valid=batch.valid_mask, last_values=batch.last_values,
        gamma=cfg.gamma, lam=cfg.gae_lambda,
    )

    B, T = batch.observations.shape[:2]
    device = batch.observations.device
    chunk = cfg.bptt_truncation if cfg.bptt_truncation > 0 else T
    starts = list(range(0, T, chunk))

    accum = {
        "loss_policy": 0.0, "loss_value": 0.0, "loss_entropy": 0.0,
        "loss_pc": 0.0, "loss_slow": 0.0, "loss_total": 0.0,
        "approx_kl": 0.0, "clip_frac": 0.0,
        "critic_std": 0.0,           # spread over quantile axis of Q(s, a_t)
        "q_action_spread": 0.0,      # mean |Q(s,a=0) − Q(s,a=1)|: action discrim.
        "n_updates": 0.0,
    }

    for _epoch in range(cfg.n_epochs):
        Mf, Ms = model.init_memory(B, device=device)

        for t0 in starts:
            t1 = min(t0 + chunk, T)
            x_chunk = batch.observations[:, t0:t1]
            valid_chunk = batch.valid_mask[:, t0:t1]
            actions_chunk = batch.actions[:, t0:t1]
            old_logp_chunk = batch.old_log_probs[:, t0:t1]
            adv_chunk = advantages[:, t0:t1]
            ret_chunk = returns[:, t0:t1]

            Mf, Ms = Mf.detach(), Ms.detach()
            Mf_seq = [Mf]
            Ms_seq = [Ms]

            logits_seq, values_seq, q_dist_seq, pc_steps = [], [], [], []
            for t in range(t1 - t0):
                step = model.forward_step(x_chunk[:, t].contiguous(), Mf, Ms)
                logits_seq.append(step.action_logits)
                values_seq.append(step.value)        # V(s_t)            (B,)
                q_dist_seq.append(step.q_dist)       # Q dist            (B, |A|, N)
                pc_steps.append(step.pc_loss)
                Mf_seq.append(step.M_fast_next)
                Ms_seq.append(step.M_slow_next)
                Mf, Ms = step.M_fast_next, step.M_slow_next

            logits_t = torch.stack(logits_seq, dim=1)              # (B, T, |A|)
            values_t = torch.stack(values_seq, dim=1)              # (B, T)
            q_dist_t = torch.stack(q_dist_seq, dim=1)              # (B, T, |A|, N)
            pc_t = torch.stack(pc_steps, dim=0)

            # Gather Q(s_t, a_t; ·) — the distributional Q for the action
            # actually taken at each step. This is the column on which the
            # critic is supervised. Shape: (B, T, N).
            #
            # gather wants the index tensor to broadcast against the source.
            # q_dist_t is (B, T, |A|, N); index actions over dim=2.
            B_, T_, A_, N_ = q_dist_t.shape
            act_idx = actions_chunk.view(B_, T_, 1, 1).expand(B_, T_, 1, N_)
            q_at_t = q_dist_t.gather(2, act_idx).squeeze(2)        # (B, T, N)

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
            # Action-conditional distributional critic loss.
            # The QR-Huber pulls each quantile of Q(s_t, a_t; τ_i) toward the
            # GAE return G_t with the asymmetric weight |τ_i − 𝟙{δ<0}|. Only
            # the action-taken column is supervised — counterfactual Q values
            # at a' ≠ a_t are learned implicitly via the shared backbone /
            # shared `head_backbone` features and the shared `fc1` weights of
            # the critic MLP.
            loss_value = quantile_huber_loss(q_at_t, ret_chunk, m, kappa=cfg.value_huber_kappa)
            loss_entropy = -(entropy * m).sum() / denom

            valid_per_t = valid_chunk.sum(dim=0)
            valid_total = valid_per_t.sum().clamp(min=1.0)
            loss_pc = (pc_t * valid_per_t).sum() / valid_total

            loss_slow = torch.tensor(0.0, device=device)
            if cfg.slow_coef > 0:
                Mf_chunk = torch.stack(Mf_seq[1:], dim=1)
                Mf_lag = torch.stack(Mf_seq[:-1], dim=1)
                loss_slow = slowness_loss(Mf_chunk, Mf_lag)

            loss = (
                loss_policy
                + cfg.value_coef * loss_value
                + cfg.entropy_coef * loss_entropy
                + cfg.pc_coef * loss_pc
                + cfg.slow_coef * loss_slow
            )

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=cfg.grad_clip)
            optimizer.step()

            with torch.no_grad():
                approx_kl = (((ratio - 1) - (new_logp - old_logp_chunk)) * m).sum() / denom
                clip_frac = (((ratio < 1 - cfg.clip_range) | (ratio > 1 + cfg.clip_range)).float() * m).sum() / denom
                # Std over quantile axis of the action-taken Q distribution:
                # how spread out is the critic's return estimate for a_t?
                critic_std = q_at_t.std(dim=-1).mean()
                # Action-discrimination signal: how different is Q(s, a=0)
                # from Q(s, a=1) on average? If this stays near 0, the critic
                # has not learned to differentiate actions and the policy
                # gradient is starved of advantage signal.
                q_mean_per_action = q_dist_t.mean(dim=-1)        # (B, T, |A|)
                q_action_spread = (
                    q_mean_per_action.max(dim=-1).values - q_mean_per_action.min(dim=-1).values
                ).mean()

            accum["loss_policy"] += float(loss_policy.detach().item())
            accum["loss_value"] += float(loss_value.detach().item())
            accum["loss_entropy"] += float(loss_entropy.detach().item())
            accum["loss_pc"] += float(loss_pc.detach().item())
            accum["loss_slow"] += float(loss_slow.detach().item())
            accum["loss_total"] += float(loss.detach().item())
            accum["approx_kl"] += float(approx_kl.detach().item())
            accum["clip_frac"] += float(clip_frac.detach().item())
            accum["critic_std"] += float(critic_std.detach().item())
            accum["q_action_spread"] += float(q_action_spread.detach().item())
            accum["n_updates"] += 1

    n = max(accum["n_updates"], 1.0)
    return {k: v / n for k, v in accum.items() if k != "n_updates"} | {"n_updates": accum["n_updates"]}


# ─────────────────────────────────────────────────────────────────────────────
# Top-level train loop
# ─────────────────────────────────────────────────────────────────────────────


def train(
    model: PrismV2Model,
    env,
    *,
    n_iterations: int = 1000,
    episodes_per_iter: int = 8,
    cfg: PPOConfig = PPOConfig(),
    device: torch.device | None = None,
    log_every: int = 1,
    rolling_window: int = 50,
    checkpoint_dir: str | None = None,
    save_every: int = 500,
    callback=None,
) -> list[dict]:
    if device is None:
        device = next(model.parameters()).device

    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr, eps=1e-5)
    history: list[dict] = []

    # Startup diagnostics — verify Fix-1, inner-K targets, PC coefs, etc.
    with torch.no_grad():
        actor_bias = model.actor.fc2.bias.detach().cpu().tolist()
    print(f"[diagnostics] actor.fc2.bias = {actor_bias}")
    print(f"[diagnostics] inner_K_fast = {int(model.inner_fast.K)}, inner_K_slow = {int(model.inner_slow.K)}")
    print(f"[diagnostics] readout.output_dim = {model.readout.output_dim}")
    print(f"[diagnostics] PC coefs : pix={model.pc_pixel_coef} pix_auto={model.pc_pixel_autoenc_coef} "
          f"V1_feat={model.pc_V1_feat_coef} V2_feat={model.pc_V2_feat_coef} V2_auto={model.pc_V2_feat_autoenc_coef}")
    print(f"[diagnostics] PPO coefs: entropy={cfg.entropy_coef} value={cfg.value_coef} pc={cfg.pc_coef}")
    print(f"[diagnostics] critic   : n_quantiles={model.n_quantiles} huber_kappa={cfg.value_huber_kappa}")
    print(f"[diagnostics] pretrain : pc_pretrain={cfg.pc_pretrain_iters} K_warmup={cfg.inner_K_warmup_iters}")

    # Cache the inner-K targets for both loops; force to 0 during warmup.
    inner_K_fast_target = int(model.inner_fast.K)
    inner_K_slow_target = int(model.inner_slow.K)
    if cfg.inner_K_warmup_iters > 0:
        model.inner_fast.K = 0
        model.inner_slow.K = 0
        print(
            f"[inner-K warmup] holding both inner.K = 0 for {cfg.inner_K_warmup_iters} iters; "
            f"will restore to (fast={inner_K_fast_target}, slow={inner_K_slow_target})."
        )

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
        if cfg.inner_K_warmup_iters > 0 and it == cfg.inner_K_warmup_iters:
            model.inner_fast.K = inner_K_fast_target
            model.inner_slow.K = inner_K_slow_target
            print(f"[inner-K warmup] iter {it}: restored inner.K to (fast={inner_K_fast_target}, slow={inner_K_slow_target})")

        in_pretrain = it < cfg.pc_pretrain_iters
        if cfg.pc_pretrain_iters > 0 and it == cfg.pc_pretrain_iters:
            print(f"[PC pretrain] iter {it}: pretrain done — switching to PPO.")

        batch, rollout_stats = collect_episodes(
            model=model, env=env, n_episodes=episodes_per_iter, device=device,
            force_action=0 if in_pretrain else None,
        )
        if in_pretrain:
            update_stats = pc_pretrain_update(model, optimizer, batch, cfg)
        else:
            update_stats = ppo_update(model, optimizer, batch, cfg)

        _correct_buf.append(rollout_stats["rollout/correct_rate"])
        _return_buf.append(rollout_stats["rollout/mean_return"])
        roll_correct = sum(_correct_buf) / len(_correct_buf)
        roll_return = sum(_return_buf) / len(_return_buf)

        log = {
            "iter": it, **rollout_stats, **update_stats,
            "rolling/correct_rate": roll_correct, "rolling/mean_return": roll_return,
        }
        history.append(log)
        n_eps = (it + 1) * episodes_per_iter

        if (it + 1) % log_every == 0:
            elapsed = time.time() - t_start
            tag = "pretrain" if in_pretrain else "ppo"
            print(
                f"[{tag} {it:5d} | ep {n_eps:6d} | {elapsed:6.1f}s] "
                f"correct={roll_correct:.3f}({rolling_window}it) "
                f"return={roll_return:.3f} "
                f"len={log['rollout/mean_length']:.1f} "
                f"L_PC={log['loss_pc']:.4f} "
                f"H={-log['loss_entropy']:.3f} "
                f"L_V={log['loss_value']:.4f} "
                f"Zstd={log.get('critic_std', 0.0):.3f} "
                f"dQ={log.get('q_action_spread', 0.0):.3f} "
                f"KL={log['approx_kl']:.4f}"
            )

        if checkpoint_dir is not None and (it + 1) % save_every == 0:
            os.makedirs(checkpoint_dir, exist_ok=True)
            ckpt_path = os.path.join(checkpoint_dir, "prism_v2_latest.pt")
            torch.save({"model_state_dict": model.state_dict(), "iter": it}, ckpt_path)
            print(f"[checkpoint] saved to {ckpt_path} (iter {it})")

        if callback is not None:
            callback(it, log)

    return history
