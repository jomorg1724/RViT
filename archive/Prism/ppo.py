"""
Recurrent PPO with truncated BPTT, plus the joint PC auxiliary loss.

Architecture writeup: see `../docs/THESIS.md` §3 (Methods).

Mathematical formulation
------------------------
PPO (Schulman et al., 2017) optimises the clipped surrogate

    L_PPO(θ)  =  𝔼_t [ min( r_t(θ) · A_t,
                            clip( r_t(θ), 1 − ε, 1 + ε ) · A_t ) ]

where r_t(θ) = π_θ(a_t|s_t) / π_{θ_old}(a_t|s_t) is the importance-sampling
ratio between current and rollout policies, and A_t are GAE advantages
(Schulman et al., 2016):

    δ_t = r_t + γ V(s_{t+1}) − V(s_t)
    A_t = δ_t + (γλ) δ_{t+1} + (γλ)² δ_{t+2} + …

The full loss includes a value MSE and an entropy bonus:

    L = − L_PPO(θ)
        + c_v · 𝔼_t [ ( V_θ(s_t) − R_t )² ]
        − c_H · 𝔼_t [ H[ π_θ(·|s_t) ] ]
        + c_PC · 𝔼_t [ L_PC(t) ]

with R_t = A_t + V_old(s_t) the bootstrap returns.

Truncated BPTT
--------------
PRISM's recurrent state propagates within an episode but we cap gradient
flow at T_bptt steps. After T_bptt steps, M is detached from the graph and
the next chunk starts fresh (autograd-wise) from the detached carry. This:
    (1) bounds memory at ≈ T_bptt × per-step storage;
    (2) bounds graph depth so backward is fast;
    (3) costs us nothing on this env where T = 30 and T_bptt ≥ 30 covers a
        whole trial trivially.

For T = 30 and T_bptt = 16 we get two chunks per trial, which matches the
proposal's §9.4 spec.

Implementation notes
--------------------
- Rollout is done in eval mode with `torch.no_grad()`. We collect actions,
  log-probs, values, rewards, and the per-step memory carry M_t (detached so
  the rollout doesn't keep a graph).
- Update re-runs the forward pass *with* gradient on the collected
  observations and detached carry-from-rollout. We compute the loss against
  the stored old log-probs and the GAE returns/advantages.
- Multiple PPO epochs (K_epochs) over the same minibatch is standard.
"""
from __future__ import annotations

import math
import os
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical

try:
    from .losses import predictive_coding_loss, slowness_loss
    from .model import PrismModel
except ImportError:
    from losses import predictive_coding_loss, slowness_loss  # type: ignore[no-redef]
    from model import PrismModel  # type: ignore[no-redef]


# ─────────────────────────────────────────────────────────────────────────────
# Rollout storage
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class RolloutBatch:
    """
    One batch of complete episodes collected on-policy.

    Shapes: B = number of episodes, T_max = max episode length in the batch.
    """

    observations: torch.Tensor  # (B, T_max, 3, 50, 50)  float32
    actions: torch.Tensor  # (B, T_max)             long
    rewards: torch.Tensor  # (B, T_max)             float32
    dones: torch.Tensor  # (B, T_max)             float32 (0/1)
    valid_mask: torch.Tensor  # (B, T_max)             float32 (1 where t < length)
    old_log_probs: torch.Tensor  # (B, T_max)         float32
    old_values: torch.Tensor  # (B, T_max)            float32
    last_values: torch.Tensor  # (B,)                  float32 — V(s_T) bootstrap
    lengths: torch.Tensor  # (B,) long


# ─────────────────────────────────────────────────────────────────────────────
# Rollout collection (no_grad)
# ─────────────────────────────────────────────────────────────────────────────


def collect_episodes(
    model: PrismModel,
    env,
    n_episodes: int,
    device: torch.device,
    max_episode_steps: Optional[int] = None,
    force_action: Optional[int] = None,
) -> tuple[RolloutBatch, dict]:
    """
    Roll out `n_episodes` episodes on `env` with the current `model`.

    The env is assumed to be a ChangeDetectionEnv-style gym environment with
    .reset() returning a (50,50,3) numpy float32 obs and .step(int) returning
    (next_obs, reward, done, info). One episode at a time (the env isn't
    vectorised); for n_episodes ≤ 32 on a 30-step trial this is fast enough.

    Returns (RolloutBatch, stats) where stats has rolling-window scalars for
    logging.
    """
    model.eval()

    # We'll collect ragged-length episodes then pad to T_max.
    obs_list: list[list[np.ndarray]] = []
    act_list: list[list[int]] = []
    rew_list: list[list[float]] = []
    done_list: list[list[float]] = []
    logp_list: list[list[float]] = []
    val_list: list[list[float]] = []
    last_val_list: list[float] = []

    ep_returns: list[float] = []
    ep_lengths: list[int] = []
    ep_correct: list[float] = []  # ChangeDetectionEnv: episode_correct = any(reward > 0)

    with torch.no_grad():
        for _ in range(n_episodes):
            obs = env.reset()
            M = model.init_memory(batch_size=1, device=device)
            obs_e: list[np.ndarray] = []
            act_e: list[int] = []
            rew_e: list[float] = []
            done_e: list[float] = []
            logp_e: list[float] = []
            val_e: list[float] = []

            done = False
            ep_return = 0.0
            ep_steps = 0
            while not done:
                obs_e.append(obs.astype(np.float32, copy=False))

                # Single-step forward.
                x_t = torch.from_numpy(obs.astype(np.float32, copy=False)).to(device)
                # env's observation is HWC; the V1 stem expects CHW.
                # .contiguous() required for MPS: permute produces a non-contiguous view.
                x_t = x_t.permute(2, 0, 1).unsqueeze(0).contiguous()  # (1, 3, 50, 50)
                step_out = model.forward_step(x_t, M)

                logits = step_out.action_logits[0]  # (n_actions,)
                value = step_out.value[0].item()

                # Categorical sampling for the on-policy action.
                dist = Categorical(logits=logits)
                if force_action is not None:
                    a = torch.tensor(force_action, device=device)
                else:
                    a = dist.sample()
                logp = dist.log_prob(a).item()

                # Step the env.
                next_obs, r, done, _ = env.step(int(a.item()))

                act_e.append(int(a.item()))
                rew_e.append(float(r))
                done_e.append(1.0 if done else 0.0)
                logp_e.append(float(logp))
                val_e.append(float(value))

                M = step_out.M_next  # detach not needed — no_grad block
                obs = next_obs
                ep_return += float(r)
                ep_steps += 1

                if max_episode_steps is not None and ep_steps >= max_episode_steps:
                    break

            # Bootstrap value at the (final, terminal) state. If episode is done
            # the bootstrap is 0; if we hit max_episode_steps the bootstrap is
            # V(s_T). For ChangeDetectionEnv done is always True at episode end,
            # so bootstrap is 0 in practice.
            last_val = 0.0 if done else 0.0  # placeholder — env always terminates
            last_val_list.append(last_val)

            obs_list.append(obs_e)
            act_list.append(act_e)
            rew_list.append(rew_e)
            done_list.append(done_e)
            logp_list.append(logp_e)
            val_list.append(val_e)

            ep_returns.append(ep_return)
            ep_lengths.append(ep_steps)
            ep_correct.append(1.0 if any(r > 0 for r in rew_e) else 0.0)

    # Pad to T_max.
    T_max = max(len(seq) for seq in obs_list)

    def _pad_obs(seq: list[np.ndarray], T: int) -> np.ndarray:
        out = np.zeros((T, 50, 50, 3), dtype=np.float32)
        for i, o in enumerate(seq):
            out[i] = o
        return out

    def _pad_scalar(seq: list[float], T: int, dtype) -> np.ndarray:
        out = np.zeros((T,), dtype=dtype)
        for i, v in enumerate(seq):
            out[i] = v
        return out

    B = len(obs_list)
    obs_arr = np.stack([_pad_obs(seq, T_max) for seq in obs_list], axis=0)  # (B, T_max, 50, 50, 3)
    # Convert to (B, T_max, 3, 50, 50) for the model.
    # ascontiguousarray is required: np.transpose returns a non-contiguous view, and
    # MPS rejects non-contiguous tensors in conv ops.
    obs_arr = np.ascontiguousarray(np.transpose(obs_arr, (0, 1, 4, 2, 3)))

    actions = np.stack([_pad_scalar(a, T_max, np.int64) for a in act_list], axis=0)
    rewards = np.stack([_pad_scalar(r, T_max, np.float32) for r in rew_list], axis=0)
    dones = np.stack([_pad_scalar(d, T_max, np.float32) for d in done_list], axis=0)
    logps = np.stack([_pad_scalar(l, T_max, np.float32) for l in logp_list], axis=0)
    vals = np.stack([_pad_scalar(v, T_max, np.float32) for v in val_list], axis=0)
    lengths = np.array([len(seq) for seq in obs_list], dtype=np.int64)

    # valid_mask[b, t] = 1 iff t < lengths[b]
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
# GAE advantages
# ─────────────────────────────────────────────────────────────────────────────


def compute_gae(
    rewards: torch.Tensor,  # (B, T)
    values: torch.Tensor,  # (B, T)
    dones: torch.Tensor,  # (B, T)
    valid: torch.Tensor,  # (B, T)
    last_values: torch.Tensor,  # (B,)
    gamma: float,
    lam: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Generalised Advantage Estimation (Schulman et al., 2016).

    Computes
        δ_t = r_t + γ · V(s_{t+1}) · (1 − done_t) − V(s_t)
        A_t = δ_t + (γλ) · A_{t+1} · (1 − done_t)
        R_t = A_t + V(s_t)              (bootstrap returns for the value loss)

    Boundary conditions:
        V(s_{T+1}) = last_values             (env terminated → 0; truncated → V_θ(s_T))
        Outside valid_mask, A_t = 0, R_t = 0 (these cells don't enter the loss)

    Returns
    -------
    advantages : (B, T)
    returns    : (B, T)
    """
    B, T = rewards.shape
    advantages = torch.zeros_like(rewards)
    last_adv = torch.zeros(B, device=rewards.device, dtype=rewards.dtype)
    next_value = last_values

    # Iterate backward in time.
    for t in reversed(range(T)):
        # Mask: zero out contributions beyond the valid sequence length.
        m = valid[:, t]

        # Bootstrap value at t+1: env-done → 0; otherwise the next stored value
        # (or the bootstrap last_values at the end of the sequence).
        not_done = 1.0 - dones[:, t]
        delta = rewards[:, t] + gamma * next_value * not_done - values[:, t]
        last_adv = delta + gamma * lam * not_done * last_adv

        # Mask the advantage at invalid positions.
        advantages[:, t] = last_adv * m

        # Update next_value for the next iteration (going backward).
        next_value = values[:, t]

    returns = advantages + values
    returns = returns * valid  # zero outside the episode

    # Advantage normalisation across the *valid* entries (standard PPO trick).
    valid_flat = valid.flatten()
    adv_flat = advantages.flatten()
    n_valid = valid_flat.sum().clamp(min=1.0)
    mean_adv = (adv_flat * valid_flat).sum() / n_valid
    var_adv = ((adv_flat - mean_adv).pow(2) * valid_flat).sum() / n_valid
    std_adv = (var_adv + 1e-8).sqrt()
    advantages = (advantages - mean_adv) / std_adv * valid

    return advantages, returns


# ─────────────────────────────────────────────────────────────────────────────
# PPO update
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PPOConfig:
    # Optimisation.
    lr: float = 3e-4
    n_epochs: int = 4
    clip_range: float = 0.2
    value_coef: float = 0.5
    entropy_coef: float = 0.01
    pc_coef: float = 1.0
    slow_coef: float = 0.0
    grad_clip: float = 0.5

    # Discounting.
    gamma: float = 0.95
    gae_lambda: float = 0.95

    # Truncated BPTT.
    bptt_truncation: int = 16  # 0 = no truncation

    # Inner-WM warmup. For the first `inner_K_warmup_iters` iterations, force
    # model.inner.K = 0 so the inner-loop variational-inference iterations don't
    # multiply gradients through an unconverged decoder. After warmup, restore
    # model.inner.K to its constructor-time target (cached as inner_K_target).
    # Set warmup to 0 to disable.
    inner_K_warmup_iters: int = 0

    # PC-only pretrain phase. For the first `pc_pretrain_iters` iterations,
    # force action=0 in the rollouts (so episodes always run the full trial)
    # and skip the PPO surrogate / value / entropy losses — train ONLY the PC
    # objective. This gives perception + memory a chance to learn the visual
    # structure of the env before the actor starts thrashing.
    # Generic technique: works on any env where action=0 ("no-op / wait") is a
    # safe default that yields complete trajectories. Set to 0 to disable.
    pc_pretrain_iters: int = 0

    # PC pretrain. For the first `pc_pretrain_iters` iterations: force action=0
    # during rollout (episodes always run full 30 steps), skip PPO, update only
    # the PC loss. This lets the perception/memory stack learn the env's visual
    # statistics before RL signal is added. Set to 0 to disable.
    pc_pretrain_iters: int = 0


def pc_pretrain_update(
    model: PrismModel,
    optimizer: torch.optim.Optimizer,
    batch: RolloutBatch,
    cfg: PPOConfig,
) -> dict:
    """PC-only parameter update used during the pretrain phase.

    No PPO surrogate, no value loss, no entropy bonus — just the predictive
    coding loss backpropagated through truncated BPTT. The policy and value
    heads receive zero gradient here; their weights move only when PPO starts.
    """
    model.train()
    B, T = batch.observations.shape[:2]
    device = batch.observations.device
    chunk = cfg.bptt_truncation if cfg.bptt_truncation > 0 else T
    starts = list(range(0, T, chunk))

    total_pc = 0.0
    n_updates = 0

    for _epoch in range(cfg.n_epochs):
        M = model.init_memory(B, device=device)
        for t0 in starts:
            t1 = min(t0 + chunk, T)
            x_chunk = batch.observations[:, t0:t1]

            M = M.detach()
            pc_steps = []
            for t in range(t1 - t0):
                step = model.forward_step(x_chunk[:, t].contiguous(), M, return_aux=False)
                pc_steps.append(step.pc_loss)
                M = step.M_next

            loss = cfg.pc_coef * torch.stack(pc_steps).mean()
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=cfg.grad_clip)
            optimizer.step()

            total_pc += float(loss.detach().item()) / max(cfg.pc_coef, 1e-9)
            n_updates += 1

    n = max(n_updates, 1)
    return {
        "loss_pc": total_pc / n,
        "loss_policy": 0.0, "loss_value": 0.0,
        "loss_entropy": 0.0, "loss_slow": 0.0, "loss_total": total_pc / n,
        "approx_kl": 0.0, "clip_frac": 0.0, "n_updates": float(n_updates),
    }


def ppo_update(
    model: PrismModel,
    optimizer: torch.optim.Optimizer,
    batch: RolloutBatch,
    cfg: PPOConfig,
) -> dict:
    """
    Run `cfg.n_epochs` PPO updates on the given batch, with truncated BPTT
    through the recurrent state.

    Returns a stats dict with mean per-loss values across the update.
    """
    model.train()

    advantages, returns = compute_gae(
        rewards=batch.rewards,
        values=batch.old_values,
        dones=batch.dones,
        valid=batch.valid_mask,
        last_values=batch.last_values,
        gamma=cfg.gamma,
        lam=cfg.gae_lambda,
    )  # (B, T) each

    B, T = batch.observations.shape[:2]
    device = batch.observations.device

    # Truncation chunks.
    chunk = cfg.bptt_truncation if cfg.bptt_truncation > 0 else T
    starts = list(range(0, T, chunk))

    accumulated = {
        "loss_policy": 0.0,
        "loss_value": 0.0,
        "loss_entropy": 0.0,
        "loss_pc": 0.0,
        "loss_slow": 0.0,
        "loss_total": 0.0,
        "approx_kl": 0.0,
        "clip_frac": 0.0,
        "n_updates": 0.0,
    }

    for _epoch in range(cfg.n_epochs):
        # Re-initialise memory at the start of every epoch.
        # Within an epoch, M propagates between truncation windows but is
        # detached at each window boundary.
        M = model.init_memory(batch_size=B, device=device)

        for t0 in starts:
            t1 = min(t0 + chunk, T)
            x_chunk = batch.observations[:, t0:t1]  # (B, t1-t0, 3, 50, 50)
            valid_chunk = batch.valid_mask[:, t0:t1]  # (B, t1-t0)
            actions_chunk = batch.actions[:, t0:t1]
            old_logp_chunk = batch.old_log_probs[:, t0:t1]
            adv_chunk = advantages[:, t0:t1]
            ret_chunk = returns[:, t0:t1]

            # Detach M at the truncation boundary so the previous chunk's
            # graph is not retained in this chunk's backward.
            M = M.detach()
            M_prev_seq = [M]

            # Forward through the chunk.
            logits_seq = []
            values_seq = []
            pc_loss_per_step = []

            for t in range(t1 - t0):
                step = model.forward_step(x_chunk[:, t].contiguous(), M, return_aux=False)
                logits_seq.append(step.action_logits)
                values_seq.append(step.value)
                pc_loss_per_step.append(step.pc_loss)
                M_prev_seq.append(step.M_next)
                M = step.M_next

            logits_t = torch.stack(logits_seq, dim=1)  # (B, t1-t0, n_actions)
            values_t = torch.stack(values_seq, dim=1)  # (B, t1-t0)
            pc_t = torch.stack(pc_loss_per_step, dim=0)  # (t1-t0,)

            # ── PPO surrogate ───────────────────────────────────────────────
            dist = Categorical(logits=logits_t)
            new_logp = dist.log_prob(actions_chunk)  # (B, t1-t0)
            entropy = dist.entropy()  # (B, t1-t0)

            ratio = (new_logp - old_logp_chunk).exp()
            unclipped = ratio * adv_chunk
            clipped = ratio.clamp(1.0 - cfg.clip_range, 1.0 + cfg.clip_range) * adv_chunk
            surrogate = -torch.min(unclipped, clipped)

            # Masked means.
            m = valid_chunk
            denom = m.sum().clamp(min=1.0)

            loss_policy = (surrogate * m).sum() / denom
            loss_value = (((values_t - ret_chunk) ** 2) * m).sum() / denom
            loss_entropy = -(entropy * m).sum() / denom

            # PC loss: weight each chunk timestep by the FRACTION of batch elements
            # for which that timestep is valid. The previous version averaged over
            # all chunk steps including padded-invalid ones, which made L_PC
            # artificially small precisely when episodes were short — exactly when
            # the diagnostic was most needed. The masked version reports the true
            # per-(valid-step) PC loss.
            valid_per_t = valid_chunk.sum(dim=0)  # (t1-t0,)
            valid_total = valid_per_t.sum().clamp(min=1.0)
            loss_pc = (pc_t * valid_per_t).sum() / valid_total

            # Slowness (off by default).
            loss_slow = torch.tensor(0.0, device=device)
            if cfg.slow_coef > 0:
                # Use stacked memory carries M_prev_seq for differences.
                M_chunk = torch.stack(M_prev_seq[1:], dim=1)  # (B, t1-t0, C, H, W)
                M_lag = torch.stack(M_prev_seq[:-1], dim=1)
                loss_slow = slowness_loss(M_chunk, M_lag)

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
            optimizer.step()

            # Diagnostics.
            with torch.no_grad():
                approx_kl = ((ratio - 1) - (new_logp - old_logp_chunk)) * m
                approx_kl = approx_kl.sum() / denom  # PPO's approximate KL diagnostic
                clip_frac = (
                    ((ratio < 1 - cfg.clip_range) | (ratio > 1 + cfg.clip_range)).float() * m
                ).sum() / denom

            accumulated["loss_policy"] += float(loss_policy.detach().item())
            accumulated["loss_value"] += float(loss_value.detach().item())
            accumulated["loss_entropy"] += float(loss_entropy.detach().item())
            accumulated["loss_pc"] += float(loss_pc.detach().item())
            accumulated["loss_slow"] += float(loss_slow.detach().item())
            accumulated["loss_total"] += float(loss.detach().item())
            accumulated["approx_kl"] += float(approx_kl.detach().item())
            accumulated["clip_frac"] += float(clip_frac.detach().item())
            accumulated["n_updates"] += 1

    n = max(accumulated["n_updates"], 1.0)
    return {k: v / n for k, v in accumulated.items() if k != "n_updates"} | {
        "n_updates": accumulated["n_updates"]
    }


# ─────────────────────────────────────────────────────────────────────────────
# Top-level training loop
# ─────────────────────────────────────────────────────────────────────────────


def train(
    model: PrismModel,
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
    """
    Outer training loop.

    Each iteration:
      1) Collect `episodes_per_iter` episodes (on-policy rollout, no_grad).
      2) Run PPO update with the joint PC aux loss.
      3) Log.

    Returns the full list of per-iteration logs.
    """
    import collections
    if device is None:
        device = next(model.parameters()).device

    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr, eps=1e-5)
    history: list[dict] = []

    # ── Startup diagnostics: print actor bias + module sizes so the user can
    #    visually confirm Fix-1 (init_action_logit_bias) and the architecture
    #    before each training session. Cheap; no performance impact.
    with torch.no_grad():
        actor_bias = model.actor.fc2.bias.detach().cpu().tolist()
    print(f"[diagnostics] actor.fc2.bias = {actor_bias}  (expect e.g. [0.0, -4.0] for ChangeDetectionEnv)")
    print(f"[diagnostics] inner.K        = {int(model.inner.K)}  (constructor-time target)")
    print(f"[diagnostics] readout.output_dim = {model.readout.output_dim}")
    print(f"[diagnostics] PC coefs        : pixel={model.pc_pixel_coef}, autoenc={model.pc_autoenc_coef}, feature={model.pc_feature_coef}")
    print(f"[diagnostics] PPO coefs       : entropy={cfg.entropy_coef}, value={cfg.value_coef}, pc={cfg.pc_coef}")
    print(f"[diagnostics] pretrain        : pc_pretrain_iters={cfg.pc_pretrain_iters}, inner_K_warmup_iters={cfg.inner_K_warmup_iters}")

    # Inner-K warmup bookkeeping. Cache the constructor-time K so we can restore
    # it after the warmup, then force K=0 for the warmup duration.
    inner_K_target = int(model.inner.K)
    if cfg.inner_K_warmup_iters > 0:
        model.inner.K = 0
        print(
            f"[inner-K warmup] holding inner.K = 0 for {cfg.inner_K_warmup_iters} iters; "
            f"will restore to inner.K = {inner_K_target} afterwards."
        )
    # Rolling windows for stable accuracy/return estimates.
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
        # Restore inner.K once we're past the warmup window.
        if cfg.inner_K_warmup_iters > 0 and it == cfg.inner_K_warmup_iters:
            model.inner.K = inner_K_target
            print(f"[inner-K warmup] iter {it}: restored inner.K = {inner_K_target}")

        in_pretrain = it < cfg.pc_pretrain_iters
        if cfg.pc_pretrain_iters > 0 and it == cfg.pc_pretrain_iters:
            print(f"[PC pretrain] iter {it}: pretrain done — switching to PPO.")

        # Rollout: force action=0 during pretrain so every episode runs 30 steps.
        batch, rollout_stats = collect_episodes(
            model=model,
            env=env,
            n_episodes=episodes_per_iter,
            device=device,
            force_action=0 if in_pretrain else None,
        )
        # Update: PC-only during pretrain, full PPO afterwards.
        if in_pretrain:
            update_stats = pc_pretrain_update(model, optimizer, batch, cfg)
        else:
            update_stats = ppo_update(model, optimizer, batch, cfg)

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
        n_eps = it * episodes_per_iter + episodes_per_iter

        if (it + 1) % log_every == 0:
            elapsed = time.time() - t_start
            phase = "pretrain" if in_pretrain else "ppo"
            print(
                f"[{phase} {it:4d} | ep {n_eps:6d} | {elapsed:6.1f}s] "
                f"correct={roll_correct:.3f}({rolling_window}it) "
                f"return={roll_return:.3f} "
                f"len={log['rollout/mean_length']:.1f} "
                f"L_PC={log['loss_pc']:.4f} "
                f"H={-log['loss_entropy']:.3f} "
                f"L_V={log['loss_value']:.4f} "
                f"KL={log['approx_kl']:.4f}"
            )

        if checkpoint_dir is not None and (it + 1) % save_every == 0:
            os.makedirs(checkpoint_dir, exist_ok=True)
            ckpt_path = os.path.join(checkpoint_dir, "prism_latest.pt")
            torch.save({"model_state_dict": model.state_dict(), "iter": it}, ckpt_path)
            print(f"[checkpoint] saved to {ckpt_path} (iter {it})")

        if callback is not None:
            callback(it, log)

    return history
