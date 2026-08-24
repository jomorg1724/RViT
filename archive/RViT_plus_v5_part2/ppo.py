"""
RL trainer for RViT+ v5 — PAC actor loss + distributional QR-DQN critic +
prioritized episode replay. RL ONLY: no reconstruction auxiliary, no
predictive-coding / JEPA terms, no recon pretrain phase (v5 has no decoder and
no self-supervised objective — the model learns purely from reward).

This is the v3 trainer with the recon and PC machinery removed; the RL
objectives are otherwise identical:

  • Actor — PAC (Springenberg, Abdolmaleki et al., DeepMind 2024): MPO + BC,
    replacing PPO's clipped surrogate. For discrete actions the MPO E-step is
    closed-form:
        q(a|s) = softmax_a[ log π_old(a|s) + Q̄(s,a) / η ]
    and the M-step + BC blend gives
        L_actor = (1−α)·(−Σ_a q(a|s)·log π_θ(a|s)) + α·(−log π_θ(a_t|s)).
    Q (the scalar mean over quantiles) drives the actor DIRECTLY — no GAE.

  • Critic — distributional QR-DQN (Dabney et al. 2018): quantile-Huber loss
    on the executed action's Q-distribution against the 1-step TD target
        target_q(s_t,:) = r_t + γ · V_dist(s_{t+1},:) · (1 − done_t).

  • Replay — prioritized episode replay (Schaul et al. 2016) at episode
    granularity: fresh on-policy episodes are augmented with replay episodes
    sampled ∝ priority^α (priority = mean per-step quantile-Huber error);
    per-episode IS weights (1/(N·p))^β correct the bias in every masked-mean
    loss.

The recurrent memory propagates within an episode via ``model.rl_step``; for the
update we re-encode the full episode via ``model.forward_rl_sequence`` (no
truncated BPTT — episodes are short, T=29).
"""
from __future__ import annotations

import collections
import copy
import os
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
from torch.distributions import Categorical

try:
    from .model import RViTPlusV5Part2Model
except ImportError:  # pragma: no cover
    from model import RViTPlusV5Part2Model  # type: ignore[no-redef]


# ─────────────────────────────────────────────────────────────────────────────
# Rollout storage
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class RolloutBatch:
    """One batch of complete episodes — fresh on-policy or fresh+replay."""

    observations: torch.Tensor      # (B, T, 3, 50, 50) float32
    actions: torch.Tensor           # (B, T)            long
    rewards: torch.Tensor           # (B, T)            float32
    dones: torch.Tensor             # (B, T)            float32 (0/1)
    valid_mask: torch.Tensor        # (B, T)            float32 (1 where t < length)
    old_log_probs: torch.Tensor     # (B, T)            float32
    old_V_scalar: torch.Tensor      # (B, T)            float32
    old_V_dist: torch.Tensor        # (B, T, N)         float32
    last_V_dist: torch.Tensor       # (B, N)            float32 (bootstrap; 0 if done)
    lengths: torch.Tensor           # (B,)              long
    sample_weights: Optional[torch.Tensor] = None   # (B,) float32 or None → ones


# ─────────────────────────────────────────────────────────────────────────────
# Prioritized episode replay buffer
# ─────────────────────────────────────────────────────────────────────────────


class EpisodeReplayBuffer:
    """FIFO ring buffer of complete episodes with prioritized sampling.

    PER (Schaul et al. 2016) at episode granularity. Priority = mean per-step
    quantile-Huber error over the episode's valid steps, refreshed whenever the
    episode is sampled and contributes to an update. Sampling p_i ∝ priority_i^α;
    IS weights w_i = (1/(N·p_i))^β / max_j w_j. Priorities are clamped at
    ``priority_clip × median`` so one outlier-error episode can't dominate.
    Episodes live on CPU; ``sample`` moves the assembled batch to the device.
    """

    def __init__(self, capacity: int, priority_clip: float = 50.0) -> None:
        self.capacity = int(capacity)
        self.priority_clip = float(priority_clip)
        self._buffer: list[dict] = []
        self._priorities: list[float] = []
        self._next_idx = 0
        self._max_priority: float = 1.0

    def __len__(self) -> int:
        return len(self._buffer)

    def push(self, batch: RolloutBatch, priorities: Optional[torch.Tensor] = None) -> None:
        B = batch.observations.shape[0]
        if priorities is None:
            pri_np = np.full((B,), self._max_priority, dtype=np.float64)
        else:
            pri_np = priorities.detach().cpu().numpy().astype(np.float64)

        for b in range(B):
            ep = {
                "observations":  batch.observations[b].detach().cpu(),
                "actions":       batch.actions[b].detach().cpu(),
                "rewards":       batch.rewards[b].detach().cpu(),
                "dones":         batch.dones[b].detach().cpu(),
                "valid_mask":    batch.valid_mask[b].detach().cpu(),
                "old_log_probs": batch.old_log_probs[b].detach().cpu(),
                "old_V_scalar":  batch.old_V_scalar[b].detach().cpu(),
                "old_V_dist":    batch.old_V_dist[b].detach().cpu(),
                "last_V_dist":   batch.last_V_dist[b].detach().cpu(),
                "length":        int(batch.lengths[b].detach().cpu().item()),
            }
            pri = max(float(pri_np[b]), 1e-6)
            if len(self._buffer) < self.capacity:
                self._buffer.append(ep)
                self._priorities.append(pri)
            else:
                self._buffer[self._next_idx] = ep
                self._priorities[self._next_idx] = pri
                self._next_idx = (self._next_idx + 1) % self.capacity
            self._max_priority = max(self._max_priority, pri)

    def sample(
        self, n: int, alpha: float, beta: float, device: torch.device,
    ) -> tuple[RolloutBatch, np.ndarray, torch.Tensor]:
        if len(self._buffer) == 0:
            raise RuntimeError("Cannot sample from empty buffer")

        priorities = np.array(self._priorities, dtype=np.float64)
        if self.priority_clip > 0 and (priorities > 0).any():
            med = float(np.median(priorities[priorities > 0]))
            priorities = np.minimum(priorities, self.priority_clip * max(med, 1e-6))
        priorities = np.clip(priorities, a_min=1e-6, a_max=None)

        probs = priorities ** alpha
        probs /= probs.sum()
        idxs = np.random.choice(len(self._buffer), size=n, p=probs, replace=True)

        N = float(len(self._buffer))
        w = (1.0 / (N * probs[idxs])) ** beta
        w = w / max(float(w.max()), 1e-8)

        eps = [self._buffer[i] for i in idxs]
        replay_batch = RolloutBatch(
            observations  = torch.stack([e["observations"]  for e in eps]).to(device),
            actions       = torch.stack([e["actions"]       for e in eps]).to(device),
            rewards       = torch.stack([e["rewards"]       for e in eps]).to(device),
            dones         = torch.stack([e["dones"]         for e in eps]).to(device),
            valid_mask    = torch.stack([e["valid_mask"]    for e in eps]).to(device),
            old_log_probs = torch.stack([e["old_log_probs"] for e in eps]).to(device),
            old_V_scalar  = torch.stack([e["old_V_scalar"]  for e in eps]).to(device),
            old_V_dist    = torch.stack([e["old_V_dist"]    for e in eps]).to(device),
            last_V_dist   = torch.stack([e["last_V_dist"]   for e in eps]).to(device),
            lengths       = torch.tensor([e["length"] for e in eps], dtype=torch.long, device=device),
            sample_weights= torch.tensor(w, dtype=torch.float32, device=device),
        )
        return replay_batch, idxs, replay_batch.sample_weights

    def update_priorities(self, idxs: np.ndarray, new_priorities: torch.Tensor) -> None:
        new_np = new_priorities.detach().cpu().numpy().astype(np.float64)
        for i, idx in enumerate(idxs):
            pri = max(float(new_np[i]), 1e-6)
            self._priorities[idx] = pri
            self._max_priority = max(self._max_priority, pri)


def concat_batches(batches: list[RolloutBatch]) -> RolloutBatch:
    """Concatenate RolloutBatches along the batch dim; fill missing
    sample_weights with ones (fresh episodes get IS weight 1)."""
    if len(batches) == 1:
        b = batches[0]
        if b.sample_weights is None:
            B = b.observations.shape[0]
            b = RolloutBatch(
                **{k: getattr(b, k) for k in b.__dataclass_fields__ if k != "sample_weights"},
                sample_weights=torch.ones(B, device=b.observations.device, dtype=torch.float32),
            )
        return b

    fields = ["observations", "actions", "rewards", "dones", "valid_mask",
              "old_log_probs", "old_V_scalar", "old_V_dist", "last_V_dist", "lengths"]
    out = {f: torch.cat([getattr(b, f) for b in batches], dim=0) for f in fields}
    weights = []
    for b in batches:
        if b.sample_weights is None:
            B_b = b.observations.shape[0]
            weights.append(torch.ones(B_b, device=b.observations.device, dtype=torch.float32))
        else:
            weights.append(b.sample_weights)
    out["sample_weights"] = torch.cat(weights, dim=0)
    return RolloutBatch(**out)


# ─────────────────────────────────────────────────────────────────────────────
# Rollout collection — single env, multiple episodes, no_grad
# ─────────────────────────────────────────────────────────────────────────────


def collect_episodes(
    model: RViTPlusV5Part2Model,
    env,
    n_episodes: int,
    device: torch.device,
    force_action: Optional[int] = None,
) -> tuple[RolloutBatch, dict]:
    """Roll out ``n_episodes`` complete episodes, carrying the recurrent memory
    within each episode via ``model.rl_step``. Returns (RolloutBatch, stats).

    If ``force_action`` is given (e.g. 0 during the burn-in phase), that action
    is taken every step instead of sampling — so episodes run their full length.
    """
    model.eval()
    N = model.n_quantiles

    obs_list: list[list[np.ndarray]] = []
    act_list: list[list[int]] = []
    rew_list: list[list[float]] = []
    done_list: list[list[float]] = []
    logp_list: list[list[float]] = []
    Vs_list: list[list[float]] = []
    Vd_list: list[list[np.ndarray]] = []
    last_Vd_list: list[np.ndarray] = []

    ep_returns: list[float] = []
    ep_lengths: list[int] = []
    ep_correct: list[float] = []

    with torch.no_grad():
        for _ in range(n_episodes):
            obs = env.reset()
            states = model.init_states(batch_size=1, device=device)
            obs_e, act_e, rew_e, done_e, logp_e, Vs_e, Vd_e = [], [], [], [], [], [], []

            done = False
            ep_return = 0.0
            while not done:
                obs_e.append(obs.astype(np.float32, copy=False))
                x_t = torch.from_numpy(obs.astype(np.float32, copy=False)).to(device)
                x_t = x_t.permute(2, 0, 1).unsqueeze(0).contiguous()   # (1, 3, 50, 50)
                step = model.rl_step(x_t, states)

                logits = step["actor_logits"][0]                       # (n_actions,)
                Vs = step["V_scalar"][0].item()
                Vd = step["V_dist"][0].cpu().numpy()                   # (N,)

                dist = Categorical(logits=logits)
                a = dist.sample() if force_action is None else \
                    torch.tensor(int(force_action), device=device)
                logp = dist.log_prob(a).item()

                next_obs, r, done, _ = env.step(int(a.item()))

                act_e.append(int(a.item()))
                rew_e.append(float(r))
                done_e.append(1.0 if done else 0.0)
                logp_e.append(float(logp))
                Vs_e.append(float(Vs))
                Vd_e.append(Vd)

                states = step["new_states"]
                obs = next_obs
                ep_return += float(r)

            last_Vd_list.append(np.zeros(N, dtype=np.float32))   # env always terminates by T
            obs_list.append(obs_e); act_list.append(act_e); rew_list.append(rew_e)
            done_list.append(done_e); logp_list.append(logp_e)
            Vs_list.append(Vs_e); Vd_list.append(Vd_e)
            ep_returns.append(ep_return)
            ep_lengths.append(len(obs_e))
            ep_correct.append(1.0 if any(r > 0 for r in rew_e) else 0.0)

    # Pad to model.seq_len. valid_mask is 1 only for collected steps, so padded
    # steps contribute zero to every masked-mean loss. Pad obs with the LAST
    # valid frame (not zeros) so the recurrent encoder settles on a stable
    # constant rather than drifting on 28 steps of black input.
    T_max = int(model.seq_len)
    actual_max = max(len(seq) for seq in obs_list)
    if actual_max > T_max:
        raise RuntimeError(
            f"Collected episode of length {actual_max} > model.seq_len {T_max}."
        )

    def _pad_obs(seq, T):
        out = np.zeros((T, 50, 50, 3), dtype=np.float32)
        for i, o in enumerate(seq):
            out[i] = o
        if 0 < len(seq) < T:
            for i in range(len(seq), T):
                out[i] = seq[-1]
        return out

    def _pad_scalar(seq, T, dtype):
        out = np.zeros((T,), dtype=dtype)
        for i, v in enumerate(seq):
            out[i] = v
        return out

    def _pad_dist(seq, T, N):
        out = np.zeros((T, N), dtype=np.float32)
        for i, v in enumerate(seq):
            out[i] = v
        return out

    B = len(obs_list)
    obs_arr = np.stack([_pad_obs(seq, T_max) for seq in obs_list], axis=0)        # (B,T,50,50,3)
    obs_arr = np.ascontiguousarray(np.transpose(obs_arr, (0, 1, 4, 2, 3)))         # → (B,T,3,50,50)

    actions = np.stack([_pad_scalar(a, T_max, np.int64) for a in act_list])
    rewards = np.stack([_pad_scalar(r, T_max, np.float32) for r in rew_list])
    dones = np.stack([_pad_scalar(d, T_max, np.float32) for d in done_list])
    logps = np.stack([_pad_scalar(l, T_max, np.float32) for l in logp_list])
    Vs = np.stack([_pad_scalar(v, T_max, np.float32) for v in Vs_list])
    Vd = np.stack([_pad_dist(v, T_max, N) for v in Vd_list])
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
        old_V_scalar=torch.from_numpy(Vs).to(device),
        old_V_dist=torch.from_numpy(Vd).to(device),
        last_V_dist=torch.from_numpy(np.stack(last_Vd_list)).to(device),
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
# Distributional TD target + per-step quantile-Huber
# ─────────────────────────────────────────────────────────────────────────────


def compute_distributional_targets(
    rewards: torch.Tensor,         # (B, T)
    V_dist_seq: torch.Tensor,      # (B, T, N)
    dones: torch.Tensor,           # (B, T)
    last_V_dist: torch.Tensor,     # (B, N)
    gamma: float,
) -> torch.Tensor:
    """1-step distributional TD target:
    target_q(s_t,:) = r_t + γ · V_dist(s_{t+1},:) · (1 − done_t). Returns (B,T,N)."""
    B, T, N = V_dist_seq.shape
    V_next = torch.cat([V_dist_seq[:, 1:], last_V_dist.unsqueeze(1)], dim=1)  # (B,T,N)
    not_done = (1.0 - dones).unsqueeze(-1)                                    # (B,T,1)
    return rewards.unsqueeze(-1) + gamma * V_next * not_done                  # (B,T,N)


def _per_step_quantile_huber(
    pred: torch.Tensor, target: torch.Tensor, taus: torch.Tensor, kappa: float = 1.0,
) -> torch.Tensor:
    """Quantile-Huber reduced over the (i,j) quantile-pair axes only.
    pred, target: (B,T,N) → returns (B,T)."""
    *leading, N_pred = pred.shape
    delta = target.unsqueeze(-2) - pred.unsqueeze(-1)                  # (...,N_pred,N_tgt)
    abs_delta = delta.abs()
    huber = torch.where(abs_delta <= kappa, 0.5 * delta.pow(2), kappa * (abs_delta - 0.5 * kappa))
    weight = (taus.view(*([1] * len(leading)), -1, 1) - (delta < 0).float()).abs()
    return (weight * huber).mean(dim=(-2, -1))


# ─────────────────────────────────────────────────────────────────────────────
# Supervised-contrastive auxiliary (experiential: action sequence + reward)
# ─────────────────────────────────────────────────────────────────────────────


def _experiential_labels(
    actions: torch.Tensor, rewards: torch.Tensor, lengths: torch.Tensor,
    *, use_reward_magnitude: bool = False,
) -> torch.Tensor:
    """Per-episode experiential OUTCOME label from the action sequence + reward.

    The trajectory's outcome is summarized by its terminal action (press/wait —
    which in ChangeDetectionEnv defines the action sequence: waits then an
    optional press) combined with the reward outcome. Default uses reward SIGN
    (got-reward vs not) → 4 canonical outcome classes (hit / miss / false-alarm /
    correct-reject). With use_reward_magnitude the distinct reward values
    {0,1,3,5} (cue colour) are kept → up to 8 classes. To fold the press LATENCY
    (a finer action-sequence signal) into the label, bucket `lengths` and mix it
    in here.

    actions (B,T) long, rewards (B,T) float, lengths (B,) long → labels (B,) long.
    """
    B = actions.shape[0]
    idx = (lengths.long() - 1).clamp(min=0)
    term_action = actions[torch.arange(B, device=actions.device), idx].long()   # (B,)
    total_reward = rewards.sum(dim=1)                                            # terminal reward
    if use_reward_magnitude:
        rb = torch.zeros(B, dtype=torch.long, device=actions.device)
        for k, v in enumerate((1.0, 3.0, 5.0), start=1):
            rb = torch.where(total_reward.round() == v, torch.full_like(rb, k), rb)
        n_rb = 4
    else:
        rb = (total_reward > 0).long()
        n_rb = 2
    return term_action * n_rb + rb                                              # (B,)


def supcon_loss(z: torch.Tensor, labels: torch.Tensor, temperature: float = 0.1) -> torch.Tensor:
    """Supervised Contrastive loss, L_out^sup (Khosla et al. 2020, Eq. 2 — the
    positives-normalization-OUTSIDE-the-log form they prove is best, 78.7 vs
    67.4 top-1):

        L = Σ_i (−1/|P(i)|) Σ_{p∈P(i)} log[ exp(z_i·z_p/τ) / Σ_{a≠i} exp(z_i·z_a/τ) ]

    z (B, D) MUST be L2-normalized; labels (B,). Positives P(i) = same-label
    samples (excluding self); the denominator sums over all other samples.
    Anchors with no in-batch positive are skipped; returns 0 if none have one.
    """
    B = z.shape[0]
    if B < 2:
        return z.new_zeros(())
    sim = (z @ z.t()) / temperature                                             # (B, B)
    sim = sim - sim.max(dim=1, keepdim=True).values.detach()                    # numerical stability
    eye = torch.eye(B, device=z.device, dtype=torch.bool)
    pos = (labels.unsqueeze(0) == labels.unsqueeze(1)) & ~eye                   # (B, B)
    exp_sim = torch.exp(sim).masked_fill(eye, 0.0)
    log_prob = sim - torch.log(exp_sim.sum(dim=1, keepdim=True) + 1e-12)        # (B, B)
    pos_count = pos.sum(dim=1)                                                  # |P(i)|
    has_pos = pos_count > 0
    if int(has_pos.sum()) == 0:
        return z.new_zeros(())
    loss_i = -(pos.float() * log_prob).sum(dim=1) / pos_count.clamp(min=1).float()
    return loss_i[has_pos].mean()


# ─────────────────────────────────────────────────────────────────────────────
# PAC + QR-DQN update
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PPOConfig:
    # Optimisation.
    lr: float = 3e-4
    n_epochs: int = 4
    grad_clip: float = 0.5            # L2-norm clip threshold
    grad_value_clip: float = 1.0e6    # per-element clip BEFORE norm clip (fp32 overflow guard)

    # PAC actor loss (MPO E-step + behavioral cloning) — replaces PPO surrogate.
    mpo_temperature: float = 0.1      # η in the MPO E-step
    bc_alpha:        float = 0.1      # α blend: 0 = pure MPO, 1 = pure BC

    # PAC target network θ' (Springenberg et al. 2024 "Offline Actor-Critic …
    # Scales", §3.2): the critic's distributional TD target AND the MPO E-step
    # reference policy π_θ' both come from a periodically hard-copied,
    # time-lagged version of θ. This was specified in PAC from the start and is
    # the main stabilizer for the bootstrapped actor-critic. 0 disables it.
    target_update_period: int = 100   # hard-copy θ → θ' every this many optimizer steps

    # Burn-in: for the first `burn_in_iters` iterations FORCE the agent to wait
    # (action=0) so episodes run full-length, and train ONLY the critic
    # (+ contrastive) with the actor frozen at init. Warms up the value function
    # and recurrent representation on clean full trajectories before the policy
    # acts. (This is v3's `recon_pretrain_iters`, re-pointed: v5 has no decoder,
    # so the critic/representation warm up instead of a reconstruction loss.)
    burn_in_iters: int = 20

    # Prioritized episode replay.
    buffer_capacity:    int   = 200
    per_n_replay:       int   = 4
    per_alpha:          float = 0.6
    per_beta_start:     float = 0.4
    per_beta_end:       float = 1.0
    per_priority_clip:  float = 50.0

    # Loss coefficients.
    value_coef: float = 0.5           # quantile-Huber on distributional Q
    entropy_coef: float = 0.1         # entropy bonus

    qr_kappa: float = 1.0             # Huber threshold
    gamma: float = 0.95               # discount for the 1-step TD target

    # Supervised-contrastive auxiliary. v5's model has NO contrastive heads
    # (that feature is scoped to v4), so this is kept OFF here. The guarded block
    # in ppo_update never runs for v5 (getattr(model,"contrastive_heads") is None).
    contrastive_coef: float = 0.0          # OFF for v5
    contrastive_temperature: float = 0.1   # SupCon τ (Khosla et al. use 0.1)
    contrastive_reward_magnitude: bool = False  # label by reward sign (False) or value {0,1,3,5} (True)


def ppo_update(
    model: RViTPlusV5Part2Model,
    optimizer: torch.optim.Optimizer,
    batch: RolloutBatch,
    cfg: PPOConfig,
    target_model: Optional[RViTPlusV5Part2Model] = None,
    train_actor: bool = True,
) -> dict:
    """One PAC + QR-DQN update (cfg.n_epochs passes over the batch).

        L = L_actor(PAC) + value_coef·L_QR − entropy_coef·H

    If `target_model` (θ') is given, the critic's distributional TD target and
    the MPO E-step reference policy are both computed from it (PAC, §3.2).
    If `train_actor` is False (burn-in), the actor is frozen: only the critic
    (+ contrastive) is trained — used during the force-wait burn-in phase.
    """
    model.train()

    accumulated = {
        "loss_policy": 0.0, "loss_value": 0.0, "loss_entropy": 0.0,
        "loss_contrastive": 0.0, "loss_total": 0.0,
        "approx_kl": 0.0,
        "n_updates": 0.0, "n_loss_evals": 0.0, "n_skipped": 0.0, "max_grad_elem": 0.0,
        "per_episode_priority": None,
    }

    taus = model.critic_head.taus           # (N,)
    B, T = batch.actions.shape
    arange_BT = (
        torch.arange(B, device=batch.actions.device).view(B, 1).expand(B, T),
        torch.arange(T, device=batch.actions.device).view(1, T).expand(B, T),
    )

    # ── PAC target network θ' (time-lagged copy) ───────────────────────────
    # θ' is fixed within this update (it is hard-copied periodically in train()),
    # so evaluate it ONCE on the trajectory and reuse the bootstrap V-dist and
    # the reference policy π_θ' across all epochs.
    use_target = target_model is not None
    tgt_V_dist = tgt_logits = None
    if use_target:
        target_model.eval()
        with torch.no_grad():
            tout = target_model.forward_rl_sequence(batch.observations)
            mvalid = batch.valid_mask.unsqueeze(-1)
            tgt_V_dist = torch.where(mvalid.bool(), tout["V_dist_seq"],
                                     torch.zeros_like(tout["V_dist_seq"]))   # (B,T,N) bootstrap
            tgt_logits = tout["actor_logits_seq"]                            # (B,T,A) → π_θ' reference

    for _epoch in range(cfg.n_epochs):
        out = model.forward_rl_sequence(batch.observations)
        logits_t = out["actor_logits_seq"]          # (B, T, A)
        q_dist_t = out["q_dist_seq"]                # (B, T, A, N)
        V_dist_t = out["V_dist_seq"]                # (B, T, N)

        m = batch.valid_mask
        w_b = batch.sample_weights if batch.sample_weights is not None else \
            torch.ones(m.shape[0], device=m.device, dtype=m.dtype)
        mw = m * w_b.unsqueeze(-1)                  # (B, T) — weighted mask
        denom_mw = mw.sum().clamp(min=1.0)
        actions = batch.actions.long()

        # NaN-safe sanitization of padded steps (NaN·0 = NaN, so use torch.where).
        mask_bta = m.unsqueeze(-1)
        mask_btan = m.unsqueeze(-1).unsqueeze(-1)
        logits_t = torch.where(mask_bta.bool(), logits_t, torch.zeros_like(logits_t))
        q_dist_t = torch.where(mask_btan.bool(), q_dist_t, torch.zeros_like(q_dist_t))
        V_dist_t = torch.where(mask_bta.bool(), V_dist_t, torch.zeros_like(V_dist_t))

        # ── PAC actor loss (MPO + BC), reference policy = target π_θ' ───────
        # During BURN-IN (train_actor=False) the actor is FROZEN: we skip the
        # policy + entropy terms and update only the critic (+ contrastive) on
        # the forced-wait full episodes, so the value function and the recurrent
        # representation warm up before the policy starts acting.
        if train_actor:
            dist = Categorical(logits=logits_t)
            entropy = dist.entropy()                                        # (B, T)

            # Reference (prior) policy for the E-step is the TARGET actor π_θ'
            # (PAC §3.2: "the target policy π_θ' which we use as the reference
            # policy"). With θ' as a stable, lagged reference the improved policy
            # no longer chases the online policy's own tail. Falls back to the
            # detached online policy when no target network is configured.
            ref_logits = tgt_logits if use_target else logits_t.detach()
            log_pi_ref = torch.log_softmax(ref_logits, dim=-1)              # (B, T, A)

            # MPO E-step (closed-form over the discrete actions, detached target):
            #   q(a|s) = softmax_a[ log π_θ'(a|s) + Q̄(s,a)/η ]
            # (general for any n_actions now — no scalar π_old reconstruction.)
            q_per_action = q_dist_t.detach().mean(dim=-1)                   # (B, T, A) online Q̄
            log_q_unnorm = log_pi_ref + q_per_action / max(cfg.mpo_temperature, 1e-6)
            log_q_target = log_q_unnorm - log_q_unnorm.logsumexp(dim=-1, keepdim=True)
            q_target = log_q_target.exp().detach()                         # (B, T, A)

            # M-step + BC:
            #   L_actor = (1−α)·(−Σ_a q·log π_θ) + α·(−log π_θ(a_t))
            log_pi = torch.log_softmax(logits_t, dim=-1)                    # (B, T, A)
            L_mpo = -(q_target * log_pi).sum(dim=-1)                        # (B, T)
            L_bc = -log_pi.gather(-1, actions.unsqueeze(-1)).squeeze(-1)    # (B, T)
            loss_policy_per_step = (1.0 - cfg.bc_alpha) * L_mpo + cfg.bc_alpha * L_bc
            loss_policy = (loss_policy_per_step * mw).sum() / denom_mw
            loss_entropy = -(entropy * mw).sum() / denom_mw
        else:
            loss_policy = logits_t.new_zeros(())
            loss_entropy = logits_t.new_zeros(())

        # ── Distributional value loss (quantile-Huber) ─────────────────────
        # Bootstrap the TD target from the TARGET critic θ' (PAC §3.2) — the
        # key stabilizer: the target distribution no longer moves every step.
        with torch.no_grad():
            boot_V_dist = tgt_V_dist if use_target else V_dist_t.detach()
            target_q = compute_distributional_targets(
                rewards=batch.rewards, V_dist_seq=boot_V_dist,
                dones=batch.dones, last_V_dist=batch.last_V_dist, gamma=cfg.gamma,
            )                                                              # (B, T, N)

        b_idx, t_idx = arange_BT
        pred_q = q_dist_t[b_idx, t_idx, actions]                           # (B, T, N)
        per_bt_qh = _per_step_quantile_huber(pred_q, target_q, taus, kappa=cfg.qr_kappa)  # (B, T)
        loss_value = (per_bt_qh * mw).sum() / denom_mw

        # Per-episode priority for PER (mean QH over valid steps, no IS weight).
        with torch.no_grad():
            ep_qh_sum = (per_bt_qh * m).sum(dim=-1)
            ep_valid = m.sum(dim=-1).clamp(min=1.0)
            accumulated["per_episode_priority"] = (ep_qh_sum / ep_valid).detach().cpu()

        # ── Supervised-contrastive auxiliary (experiential: action seq + reward) ──
        # Pull trials with the same (terminal action, reward) outcome together and
        # push different outcomes apart, on BOTH recurrent states' terminal Hℓ.
        # Gradient flows the experiential force into the encoder; the projection
        # heads are inference-time-discarded.
        loss_contrastive = logits_t.new_zeros(())
        if cfg.contrastive_coef > 0.0 and getattr(model, "contrastive_heads", None) is not None:
            embs = model.contrastive_embeddings(out["states_seq"], batch.lengths)
            con_labels = _experiential_labels(
                batch.actions, batch.rewards, batch.lengths,
                use_reward_magnitude=cfg.contrastive_reward_magnitude,
            )
            for z_layer in embs:                       # both H₁ and H₂
                loss_contrastive = loss_contrastive + supcon_loss(
                    z_layer, con_labels, cfg.contrastive_temperature)
            accumulated["loss_contrastive"] += float(loss_contrastive.detach().item())

        loss = (loss_policy + cfg.value_coef * loss_value + cfg.entropy_coef * loss_entropy
                + cfg.contrastive_coef * loss_contrastive)

        with torch.no_grad():
            if train_actor:
                pi_ref = log_pi_ref.exp()
                kl_per_step = (pi_ref * (log_pi_ref - log_pi)).sum(dim=-1)    # KL(π_θ' ‖ π_θ)
                approx_kl = (kl_per_step * mw).sum() / denom_mw
            else:
                approx_kl = logits_t.new_zeros(())

        accumulated["loss_policy"]  += float(loss_policy.detach().item())
        accumulated["loss_value"]   += float(loss_value.detach().item())
        accumulated["loss_entropy"] += float(loss_entropy.detach().item())
        accumulated["loss_total"]   += float(loss.detach().item())
        accumulated["approx_kl"]    += float(approx_kl.detach().item())
        accumulated["n_loss_evals"] += 1

        optimizer.zero_grad(set_to_none=True)
        loss.backward()

        max_grad_elem = 0.0
        for p in model.parameters():
            if p.grad is not None:
                m_p = p.grad.detach().abs().max().item()
                if m_p > max_grad_elem:
                    max_grad_elem = m_p
        accumulated["max_grad_elem"] = max(accumulated["max_grad_elem"], max_grad_elem)

        # Stage 1: per-element clip BEFORE the L2 norm (prevents fp32 overflow → inf norm).
        nn.utils.clip_grad_value_(model.parameters(), clip_value=cfg.grad_value_clip)
        # Stage 2: L2-norm clip.
        grad_norm = nn.utils.clip_grad_norm_(model.parameters(), max_norm=cfg.grad_clip)
        if not torch.isfinite(grad_norm):
            optimizer.zero_grad(set_to_none=True)
            accumulated["n_skipped"] += 1
            continue
        optimizer.step()
        accumulated["n_updates"] += 1

    n_evals = max(accumulated["n_loss_evals"], 1.0)
    LOSS_KEYS = {"loss_policy", "loss_value", "loss_entropy", "loss_contrastive",
                 "loss_total", "approx_kl"}
    result = {}
    for k, v in accumulated.items():
        result[k] = (v / n_evals) if k in LOSS_KEYS else v
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Outer training loop
# ─────────────────────────────────────────────────────────────────────────────


def train(
    model: RViTPlusV5Part2Model,
    env,
    *,
    n_iterations: int = 1000,
    episodes_per_iter: int = 8,
    cfg: PPOConfig = PPOConfig(),
    device: torch.device | None = None,
    log_every: int = 1,
    rolling_window: int = 50,
    checkpoint_dir: str | None = None,
    save_every: int = 200,
) -> list[dict]:
    """PAC + QR-DQN + PER training loop (RL only — no recon, no PC, no pretrain)."""
    if device is None:
        device = next(model.parameters()).device

    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr, eps=1e-5)
    history: list[dict] = []

    print(f"[setup] device={device}")
    print(f"[setup] n_actions={model.n_actions}, n_quantiles={model.n_quantiles}, "
          f"n_tokens={model.n_tokens}, enc_layers={model.enc_layers}")
    print(f"[setup] PAC: η={cfg.mpo_temperature}, bc_α={cfg.bc_alpha}; "
          f"value={cfg.value_coef}, entropy={cfg.entropy_coef}, γ={cfg.gamma}")
    print(f"[setup] PER buffer: capacity={cfg.buffer_capacity}, n_replay={cfg.per_n_replay}, "
          f"α={cfg.per_alpha}, β={cfg.per_beta_start}→{cfg.per_beta_end}")
    if cfg.contrastive_coef > 0:
        _lab = "action×reward-value" if cfg.contrastive_reward_magnitude else "action×reward-sign"
        print(f"[setup] contrastive (SupCon): coef={cfg.contrastive_coef}, τ={cfg.contrastive_temperature}, "
              f"label={_lab}, on both H₁,H₂")

    # PAC target network θ' (trainer-owned, like the optimizer; not saved in the
    # model state_dict). Periodically hard-copied from θ.
    target_model = None
    target_step = 0
    if cfg.target_update_period and cfg.target_update_period > 0:
        target_model = copy.deepcopy(model)
        for p in target_model.parameters():
            p.requires_grad_(False)
        target_model.eval()
        print(f"[setup] PAC target network: hard-copy θ→θ' every {cfg.target_update_period} optimizer steps "
              f"(critic TD target + E-step reference π_θ')")
    else:
        print("[setup] PAC target network: DISABLED (target_update_period=0) — online bootstrap")

    buffer = EpisodeReplayBuffer(capacity=cfg.buffer_capacity, priority_clip=cfg.per_priority_clip)
    _correct_buf = collections.deque(maxlen=rolling_window)
    _return_buf = collections.deque(maxlen=rolling_window)

    t_start = time.time()
    for it in range(n_iterations):
        in_burn_in = it < cfg.burn_in_iters
        fresh_batch, rollout_stats = collect_episodes(
            model=model, env=env, n_episodes=episodes_per_iter, device=device,
            force_action=0 if in_burn_in else None,
        )
        n_fresh = fresh_batch.observations.shape[0]

        # PER: sample replay episodes (skipped during burn-in — actor not training yet).
        beta_frac = min(it / max(n_iterations - 1, 1), 1.0)
        beta_now = cfg.per_beta_start + (cfg.per_beta_end - cfg.per_beta_start) * beta_frac
        sampled_idxs = None
        if (not in_burn_in) and cfg.per_n_replay > 0 and len(buffer) > 0:
            replay_batch, sampled_idxs, _ = buffer.sample(
                n=cfg.per_n_replay, alpha=cfg.per_alpha, beta=beta_now, device=device,
            )
            combined_batch = concat_batches([fresh_batch, replay_batch])
        else:
            combined_batch = concat_batches([fresh_batch])

        update_stats = ppo_update(model, optimizer, combined_batch, cfg,
                                  target_model=target_model, train_actor=not in_burn_in)
        update_stats["in_burn_in"] = 1.0 if in_burn_in else 0.0

        # PAC: periodically hard-copy θ → θ' (time-lagged target network).
        if target_model is not None:
            target_step += int(update_stats.get("n_updates", 0))
            if target_step >= cfg.target_update_period:
                target_model.load_state_dict(model.state_dict())
                target_step = 0

        # PER: refresh sampled priorities + push fresh into the buffer.
        ep_pri = update_stats.get("per_episode_priority", None)
        if ep_pri is not None:
            if sampled_idxs is not None:
                buffer.update_priorities(sampled_idxs, ep_pri[n_fresh:])
            buffer.push(fresh_batch, priorities=ep_pri[:n_fresh])
        else:
            buffer.push(fresh_batch, priorities=None)
        update_stats["per_beta"] = beta_now
        update_stats["per_buffer_size"] = len(buffer)
        update_stats["per_n_replay_used"] = cfg.per_n_replay if sampled_idxs is not None else 0
        update_stats.pop("per_episode_priority", None)

        _correct_buf.append(rollout_stats["rollout/correct_rate"])
        _return_buf.append(rollout_stats["rollout/mean_return"])
        roll_correct = sum(_correct_buf) / len(_correct_buf)
        roll_return = sum(_return_buf) / len(_return_buf)

        log = {"iter": it, **rollout_stats, **update_stats,
               "rolling/correct_rate": roll_correct, "rolling/mean_return": roll_return}
        history.append(log)

        if (it + 1) % log_every == 0:
            elapsed = time.time() - t_start
            n_upd = log.get("n_updates", 0)
            n_skip = log.get("n_skipped", 0)
            max_g = log.get("max_grad_elem", 0.0)
            skip_flag = f" ⚠ skip={int(n_skip)}" if n_skip > 0 else ""
            buf_size = log.get("per_buffer_size", None)
            buf_str = (f"  buf={buf_size}/{cfg.buffer_capacity} β={log.get('per_beta', 0.0):.2f} "
                       f"+rep={log.get('per_n_replay_used', 0)}" if buf_size is not None else "")
            phase = "burn" if log.get("in_burn_in", 0.0) > 0 else "ppo "
            print(
                f"[{phase}{it:5d} | {elapsed:6.1f}s] "
                f"correct={roll_correct:.3f}  return={roll_return:.3f}  "
                f"len={log['rollout/mean_length']:.1f}  "
                f"L_pol={log['loss_policy']:+.4f}  L_val={log['loss_value']:.4f}  "
                f"H={-log['loss_entropy']:.3f}  KL={log['approx_kl']:.4f}  "
                f"upd={int(n_upd)}  gmax={max_g:.2e}{buf_str}{skip_flag}"
            )

        if checkpoint_dir is not None and (it + 1) % save_every == 0:
            os.makedirs(checkpoint_dir, exist_ok=True)
            ckpt_path = os.path.join(checkpoint_dir, "rvit_plus_v5_part2_rl_latest.pt")
            torch.save({"iter": it, "model_state_dict": model.state_dict()}, ckpt_path)
            print(f"[checkpoint] saved to {ckpt_path}")

    return history
