"""
PPO + distributional QR-DQN critic + reconstruction auxiliary loss for RViT+.

Three gradient sources flow back into the shared encoder:

  1. Policy gradient (clipped PPO surrogate on the actor's logits).
  2. Quantile-Huber loss on the executed action's Q distribution.
  3. Reconstruction loss (content-weighted MSE on decoder output) — the
     self-supervised signal that proved essential during the autoencoder
     development phase (run-15 onwards). Optional via `recon_coef`.

Mathematical formulation
------------------------
PPO clipped surrogate (Schulman et al., 2017):

    L_PPO(θ) = 𝔼_t [ min( r_t · A_t,  clip(r_t, 1−ε, 1+ε) · A_t ) ]

where r_t = π_θ(a_t|s_t) / π_old(a_t|s_t) and A_t are GAE advantages
(Schulman et al., 2016), computed from the SCALAR V baseline derived from
the distributional critic via expected SARSA with stop-grad on the policy:

    V_scalar(s) = mean over quantiles of [ Σ_a sg[π(a|s)] · Q(s, a, :) ]

Distributional value loss (Dabney et al. 2018, QR-DQN):

    L_QR(θ) = mean over (i, j) of  |τ_i − 𝟙(δ_ij < 0)| · L_κ(δ_ij)

where δ_ij = target_q_j − predicted_q_i, and predicted_q is the critic's
prediction for the EXECUTED action only: q_dist[arange(B), actions, :].
Target distribution: r_t + γ · V_dist(s_{t+1}) · (1−done_t).

The full loss:

    L = − L_PPO(θ)
        + c_qr  · L_QR(θ)
        − c_H   · 𝔼_t [ H[π_θ(·|s_t)] ]
        + c_rec · L_recon

Rollout dynamics
----------------
The recurrent state propagates within an episode via model.rl_step().
For PPO update we re-encode the full episode in batched form via
model.forward_rl_sequence() — no truncated BPTT needed because T=29.

Cross-references
----------------
- `Prism/ppo.py` (parent implementation; we depart from PRISM by using a
  distributional critic and dropping PRISM's PC loss in favor of our
  reconstruction auxiliary).
- `Prism/docs/PRISM_V2/Q_CRITIC.md` (the action-conditional Q derivation).
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
    from .model import RViTPlusModel
    from .rl_heads import quantile_huber_loss
except ImportError:  # pragma: no cover
    from model import RViTPlusModel  # type: ignore[no-redef]
    from rl_heads import quantile_huber_loss  # type: ignore[no-redef]


# ─────────────────────────────────────────────────────────────────────────────
# Rollout storage
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class RolloutBatch:
    """One batch of complete episodes — either freshly collected on-policy
    or assembled by concatenating fresh + replay episodes."""

    observations: torch.Tensor      # (B, T_max, 3, 50, 50) float32
    actions: torch.Tensor           # (B, T_max)            long
    rewards: torch.Tensor           # (B, T_max)            float32
    dones: torch.Tensor             # (B, T_max)            float32 (0/1)
    valid_mask: torch.Tensor        # (B, T_max)            float32 (1 where t < length)
    old_log_probs: torch.Tensor     # (B, T_max)            float32
    old_V_scalar: torch.Tensor      # (B, T_max)            float32  — scalar baseline
    old_V_dist: torch.Tensor        # (B, T_max, N)         float32  — distributional V (for target)
    last_V_dist: torch.Tensor       # (B, N)                float32  — bootstrap (zero if done)
    lengths: torch.Tensor           # (B,) long
    # Per-episode importance-sampling weight (defaults to ones). When this batch
    # mixes fresh and replay episodes, fresh entries get weight = 1 and replay
    # entries get the PER IS-correction weight (1 / (N · p_i))^β, normalized
    # by max. All masked-mean losses in ppo_update use (valid_mask · w) as the
    # effective weight to correct the prioritized-sampling bias.
    sample_weights: Optional[torch.Tensor] = None   # (B,) float32 or None → ones


# ─────────────────────────────────────────────────────────────────────────────
# Prioritized episode replay buffer
# ─────────────────────────────────────────────────────────────────────────────


class EpisodeReplayBuffer:
    """FIFO ring buffer of complete episodes with prioritized sampling.

    PER (Schaul et al. 2016) at episode granularity. Each entry's priority is
    the MEAN per-step quantile-Huber error over the episode's valid steps,
    refreshed every time the episode is sampled and contributes to an update
    (`update_priorities`).

    Sampling:
        p_i = (priority_i^α) / Σ_j (priority_j^α)
    IS weights (to unbias the prioritized expectation):
        w_i = (1 / (N · p_i))^β  /  max_j w_j

    The buffer also clamps priorities to `priority_clip · median(priority)`
    so a single outlier-error episode can't dominate sampling.

    Episodes are stored on CPU to keep GPU memory bounded; `sample()` moves
    the assembled batch to the requested device.
    """

    def __init__(self, capacity: int, priority_clip: float = 50.0) -> None:
        self.capacity = int(capacity)
        self.priority_clip = float(priority_clip)
        self._buffer: list[dict] = []
        self._priorities: list[float] = []
        self._next_idx = 0
        # Initial priority for never-sampled episodes — the max priority so far,
        # so new episodes get full chance to be drawn at least once.
        self._max_priority: float = 1.0

    def __len__(self) -> int:
        return len(self._buffer)

    def push(self, batch: RolloutBatch, priorities: Optional[torch.Tensor] = None) -> None:
        """Push every episode in `batch` into the buffer.

        priorities : (B,) tensor of per-episode priorities, OR None (then the
                     current max priority is used — standard "optimistic" init).
        """
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
        self,
        n: int,
        alpha: float,
        beta: float,
        device: torch.device,
    ) -> tuple[RolloutBatch, np.ndarray, torch.Tensor]:
        """Sample `n` episodes prioritized by priority^α, return IS weights.

        Returns (replay_batch, indices, is_weights):
            replay_batch : RolloutBatch on `device` with sample_weights = is_weights.
            indices      : (n,) np.ndarray of buffer positions (for later
                           `update_priorities` calls).
            is_weights   : (n,) tensor on `device`, normalised so max(w) = 1.
        """
        if len(self._buffer) == 0:
            raise RuntimeError("Cannot sample from empty buffer")

        priorities = np.array(self._priorities, dtype=np.float64)
        # Cap runaway outliers — at most `priority_clip` × the median of
        # POSITIVE priorities. This prevents one giant-error episode from
        # absorbing all sampling probability.
        if self.priority_clip > 0 and (priorities > 0).any():
            med = float(np.median(priorities[priorities > 0]))
            priorities = np.minimum(priorities, self.priority_clip * max(med, 1e-6))
        priorities = np.clip(priorities, a_min=1e-6, a_max=None)

        probs = priorities ** alpha
        probs /= probs.sum()
        idxs = np.random.choice(len(self._buffer), size=n, p=probs, replace=True)

        N = float(len(self._buffer))
        w = (1.0 / (N * probs[idxs])) ** beta
        w = w / max(float(w.max()), 1e-8)             # max-normalised IS weight

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
        """Refresh the stored priorities for the given indices.

        Standard PER: call this after the update step with the new |TD error|
        (here: mean per-step quantile-Huber error) computed during the update.
        """
        new_np = new_priorities.detach().cpu().numpy().astype(np.float64)
        for i, idx in enumerate(idxs):
            pri = max(float(new_np[i]), 1e-6)
            self._priorities[idx] = pri
            self._max_priority = max(self._max_priority, pri)


def concat_batches(batches: list[RolloutBatch]) -> RolloutBatch:
    """Concatenate multiple RolloutBatches along the batch dimension.

    Used to combine `fresh` and `replay` episodes into one batch for a single
    PPO update. Per-episode `sample_weights` are concatenated too; for any
    input batch with `sample_weights = None`, ones are filled in.
    """
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
    model: RViTPlusModel,
    env,
    n_episodes: int,
    device: torch.device,
    force_action: Optional[int] = None,
) -> tuple[RolloutBatch, dict]:
    """Roll out `n_episodes` episodes on `env`, store transitions for PPO update.

    Per-step: feed obs through model.rl_step() with the carried recurrent
    state, sample an action from the actor logits (or force a fixed action
    if force_action is given — useful for the pretraining phase), store the
    distributional V baseline.

    Returns (RolloutBatch, stats).
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
            # C₃ specialists state propagates across env steps within an
            # episode (same as C₁/C₂). Reset to zero between episodes.
            c3_spec = (model.encoder.init_c3_specialists(batch_size=1, device=device)
                       if model.split_c3 else None)
            obs_e: list[np.ndarray] = []
            act_e: list[int] = []
            rew_e: list[float] = []
            done_e: list[float] = []
            logp_e: list[float] = []
            Vs_e: list[float] = []
            Vd_e: list[np.ndarray] = []

            done = False
            ep_return = 0.0
            while not done:
                obs_e.append(obs.astype(np.float32, copy=False))
                # env emits HWC; model expects CHW.
                x_t = torch.from_numpy(obs.astype(np.float32, copy=False)).to(device)
                x_t = x_t.permute(2, 0, 1).unsqueeze(0).contiguous()  # (1, 3, 50, 50)
                step = model.rl_step(x_t, states, prev_c3_specialists=c3_spec)

                logits = step["actor_logits"][0]                          # (n_actions,)
                Vs = step["V_scalar"][0].item()
                Vd = step["V_dist"][0].cpu().numpy()                      # (N,)

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
                Vs_e.append(float(Vs))
                Vd_e.append(Vd)

                states = step["new_states"]
                c3_spec = step.get("new_c3_specialists", {}) or None
                obs = next_obs
                ep_return += float(r)

            # Bootstrap V_dist at terminal: env always terminates by T → use 0.
            last_Vd_list.append(np.zeros(N, dtype=np.float32))

            obs_list.append(obs_e); act_list.append(act_e); rew_list.append(rew_e)
            done_list.append(done_e); logp_list.append(logp_e)
            Vs_list.append(Vs_e); Vd_list.append(Vd_e)

            ep_returns.append(ep_return)
            ep_lengths.append(len(obs_e))
            ep_correct.append(1.0 if any(r > 0 for r in rew_e) else 0.0)

    # Pad to model.seq_len (NOT max actual length). The decoder produces
    # exactly seq_len frames, so the recon-aux loss requires the observations
    # to match. The valid_mask is 1 only for actually-collected timesteps,
    # so padding contributes zero loss regardless.
    T_max = int(model.seq_len)
    actual_max = max(len(seq) for seq in obs_list)
    if actual_max > T_max:
        raise RuntimeError(
            f"Collected episode of length {actual_max} > model.seq_len {T_max}. "
            f"Either bump seq_len or shorten episodes."
        )

    def _pad_obs(seq, T):
        # Pad with the LAST VALID observation, not zeros. The recurrent
        # encoder runs at every timestep — feeding it 28 steps of zero
        # input drives cell3_sigma / cell3_actor states into degenerate
        # regions over many gradient updates (NaN at t=28 was observed
        # in run-29). Repeating the final obs gives the encoder a stable
        # constant input it can settle on. The downstream loss is still
        # masked by valid_mask so padded steps contribute zero.
        out = np.zeros((T, 50, 50, 3), dtype=np.float32)
        for i, o in enumerate(seq):
            out[i] = o
        if len(seq) > 0 and len(seq) < T:
            last_obs = seq[-1]
            for i in range(len(seq), T):
                out[i] = last_obs
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
    obs_arr = np.stack([_pad_obs(seq, T_max) for seq in obs_list], axis=0)         # (B, T_max, 50, 50, 3)
    obs_arr = np.ascontiguousarray(np.transpose(obs_arr, (0, 1, 4, 2, 3)))           # → (B, T_max, 3, 50, 50)

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
# GAE advantages (scalar V) + distributional target
# ─────────────────────────────────────────────────────────────────────────────


def compute_gae(
    rewards: torch.Tensor,    # (B, T)
    values: torch.Tensor,     # (B, T)  — V_scalar
    dones: torch.Tensor,      # (B, T)
    valid: torch.Tensor,      # (B, T)
    last_values: torch.Tensor,  # (B,)
    gamma: float,
    lam: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Generalised Advantage Estimation on the scalar V baseline.

    Returns (advantages, returns) — both (B, T). Advantages are normalised
    across valid entries.
    """
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

    # Normalise advantages across valid entries.
    valid_flat = valid.flatten()
    adv_flat = advantages.flatten()
    n_valid = valid_flat.sum().clamp(min=1.0)
    mean_adv = (adv_flat * valid_flat).sum() / n_valid
    var_adv = ((adv_flat - mean_adv).pow(2) * valid_flat).sum() / n_valid
    std_adv = (var_adv + 1e-8).sqrt()
    advantages = (advantages - mean_adv) / std_adv * valid

    return advantages, returns


def compute_distributional_targets(
    rewards: torch.Tensor,         # (B, T)
    V_dist_seq: torch.Tensor,      # (B, T, N) — current critic's V_dist at every step
    dones: torch.Tensor,           # (B, T)
    last_V_dist: torch.Tensor,     # (B, N) — bootstrap distribution at end
    gamma: float,
) -> torch.Tensor:
    """1-step TD targets for the distributional value loss.

        target_q(s_t, :) = r_t + γ · V_dist(s_{t+1}, :) · (1 − done_t)

    Returns (B, T, N) — the per-step target quantile distribution. These are
    the targets to be matched (via quantile-Huber loss) by the executed
    action's Q-distribution prediction.
    """
    B, T, N = V_dist_seq.shape
    # Build V_dist at t+1: shift left, append last_V_dist at the end.
    V_next = torch.cat([V_dist_seq[:, 1:], last_V_dist.unsqueeze(1)], dim=1)  # (B, T, N)
    not_done = (1.0 - dones).unsqueeze(-1)                                   # (B, T, 1)
    targets = rewards.unsqueeze(-1) + gamma * V_next * not_done              # (B, T, N)
    return targets


# ─────────────────────────────────────────────────────────────────────────────
# Reconstruction auxiliary loss (the run-15 setup, ported for RL)
# ─────────────────────────────────────────────────────────────────────────────


def content_weighted_recon_loss(
    recons: list[torch.Tensor],
    target_video: torch.Tensor,   # (B, T, 3, 50, 50)
    valid_mask: torch.Tensor,     # (B, T)
    *,
    recon_kind: str = "mse",
    content_weight: float = 100.0,
    content_threshold: float = 0.5,
) -> torch.Tensor:
    """Content-weighted reconstruction loss masked by episode validity.

    Mirrors the loss that broke the trivial-constant attractor in run-15.
    The mask is per-(h, w) at digit positions (any channel > threshold);
    bright pixels are weighted `content_weight`× over background.
    """
    recon = torch.stack(recons, dim=1)                  # (B, T, 3, H, W)
    with torch.no_grad():
        digit_mask = (target_video > content_threshold).any(dim=2, keepdim=True).float()
        weight = 1.0 + (content_weight - 1.0) * digit_mask
        weight = weight / weight.mean().clamp(min=1e-6)
        # Apply the per-timestep validity mask.
        weight = weight * valid_mask.view(*valid_mask.shape, 1, 1, 1)

    if recon_kind == "l1":
        err = (recon - target_video).abs()
    elif recon_kind == "mse":
        err = (recon - target_video).pow(2)
    else:
        raise ValueError(f"unknown recon_kind={recon_kind}")
    return (weight * err).mean()


# ─────────────────────────────────────────────────────────────────────────────
# PPO update with distributional critic
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PPOConfig:
    # Optimisation.
    lr: float = 3e-4
    n_epochs: int = 4
    clip_range: float = 0.2
    grad_clip: float = 0.5            # L2-norm clip threshold
    grad_value_clip: float = 1.0e6    # per-element clip BEFORE norm clip (prevents fp32 overflow)

    # ── Predictive-coding auxiliary ────────────────────────────────────
    # Per branch X ∈ {actor, critic}, train a small predictor `P_X` to map
    # the deep specialist state at time t−1 to a prediction of the shared
    # middle state at time t. Loss is the cosine distance between the
    # prediction and the (detached) C_2 at time t, averaged over valid
    # timesteps t ≥ 1:
    #
    #     L_PC_X = mean_{b, t ≥ 1} [ 1 − cos( P_X(C_{3, X, t-1}), C_{2, t}.detach() ) ]
    #
    # The target is detached so the gradient flows only into the predictor
    # `P_X` and the cell `cell3_X` (via C_{3, X, t-1}). C_2 is shared
    # between actor and critic so detaching it isolates the two branches.
    # This is a temporal-consistency constraint that operates on encoder
    # dynamics and does not depend on actor / reward labels — useful when
    # contrastive labels lose diversity.
    pc_actor_coef:  float = 0.1
    pc_critic_coef: float = 0.1

    # ── Discrete-JEPA variant of the PC auxiliary (run-19) ─────────────
    # When pc_kind == "discrete_jepa", the cosine objective above is
    # REPLACED by a categorical latent world-model loss (DreamerV3 discrete
    # latents + V-JEPA-style latent prediction). A tokenizer quantizes C₂ₜ
    # into K groups × V classes per spatial position; the predictor
    # P_X(C_{3,X,t-1}) emits a prior distribution over those codes. The
    # objective is KL-balanced cross-entropy in CODE space, plus an InfoMax
    # anchor that keeps the code informative (the discrete analog of SIGReg —
    # this is the collapse guard, so no EMA target encoder is needed):
    #
    #   L_dyn    = mean KL( sg(posterior) ‖ prior )        → trains P_X + cell3_X
    #   L_rep    = mean KL( posterior ‖ sg(prior) )         → trains the tokenizer
    #   L_anchor = −MI(C₂; code) = −( H(E[q]) − E[H(q)] )   → prevents code collapse
    #   L_PC_X   = pc_kl_dyn·L_dyn + pc_kl_rep·L_rep + pc_anchor_coef·L_anchor
    #
    # As in the cosine variant the prediction term stop-grads the target, so
    # the predictive gradient reaches only P_X and cell3_X — never the shared
    # C₂. With pc_detach_c2=True the tokenizer also reads a detached C₂, fully
    # isolating the actor/critic branches (the tokenizer still learns via
    # L_rep + L_anchor). Cross-entropy over discrete codes (vs. cosine/MSE
    # regression) lets the predictor place mass on MULTIPLE plausible
    # next-codes, so a stochastic event (the Posner change) is represented
    # multimodally instead of being blurred into a regress-to-the-mean guess.
    # pc_kind: "cosine" (legacy 1−cos) | "discrete_jepa" (discrete CODE TARGET
    # only; agent reads continuous C₂) | "discrete_latent" (the hard one-hot
    # code REPLACES C₂ as the latent the actor/critic read — DreamerV3-style,
    # so policy/value gradients anchor it; the predictors become the dynamics
    # model and this loss is the dynamics/JEPA term). pc_detach_c2 applies only
    # to discrete_jepa (in discrete_latent the posterior must carry gradient).
    pc_kind:         str   = "cosine"
    pc_groups:       int   = 8          # K categorical groups
    pc_classes:      int   = 16         # V classes per group
    pc_kl_dyn:       float = 0.5        # weight on KL(sg(post)‖prior)  (DreamerV3 β_dyn)
    pc_kl_rep:       float = 0.1        # weight on KL(post‖sg(prior))  (DreamerV3 β_rep)
    pc_anchor_coef:  float = 0.1        # weight on −MI InfoMax anchor (collapse guard)
    pc_free_bits:    float = 0.0        # per-group free bits (nats); KL below this is not penalized
    pc_detach_c2:    bool  = True       # detach C₂ into the tokenizer (isolates actor/critic)

    # ── PAC actor loss (replaces PPO surrogate) ────────────────────────
    # Per Springenberg, Abdolmaleki et al. (DeepMind 2024), the actor loss
    # is MPO + behavioral cloning, NOT PPO's clipped surrogate. For our
    # discrete-action setting the MPO E-step is closed-form: the improved
    # non-parametric target policy is
    #     q(a|s) = softmax_a [ log π_old(a|s) + Q̄(s, a) / η ]
    # where Q̄(s,a) is the scalar mean of the distributional critic over its
    # quantile axis. The M-step is a KL projection of π_θ onto q, which for
    # discrete actions reduces to a weighted cross-entropy. Adding the BC
    # term (PAC variant) gives:
    #     L_actor = (1−α)·(−Σ_a q(a|s)·log π_θ(a|s))  +  α·(−log π_θ(a_t|s))
    # The critic stays distributional and trained with the same quantile-
    # Huber loss we already have. Q now drives the actor DIRECTLY through
    # the MPO weights, rather than via a scalar V baseline + GAE.
    mpo_temperature: float = 1.0     # η in the MPO E-step
    bc_alpha:        float = 0.1     # α blend: 0 = pure MPO, 1 = pure BC

    # ── Prioritized episode replay buffer ──────────────────────────────
    # The fresh on-policy batch (size = `episodes_per_iter`) is augmented with
    # `per_n_replay` episodes sampled from `EpisodeReplayBuffer`. The combined
    # batch goes through one PPO update; PPO's ratio clip absorbs stale-policy
    # samples automatically, and per-episode IS weights correct the priority
    # bias in every masked-mean loss.
    #
    # priority   = mean per-step quantile-Huber error over the episode's
    #              valid timesteps (refreshed after every update where this
    #              episode contributes — standard PER convention).
    # sampling   = p_i ∝ priority_i^per_alpha  (clipped to per_priority_clip×median)
    # IS weights = (1 / (N · p_i))^β / max_w, with β linearly annealed
    #              from per_beta_start (early training) → per_beta_end
    #              (full correction by the end).
    # Set per_n_replay = 0 to disable replay entirely (pure on-policy PPO).
    buffer_capacity:    int   = 200
    per_n_replay:       int   = 4
    per_alpha:          float = 0.6
    per_beta_start:     float = 0.4
    per_beta_end:       float = 1.0
    per_priority_clip:  float = 50.0

    # Loss coefficients.
    value_coef: float = 0.5        # quantile-Huber on distributional Q
    entropy_coef: float = 0.01     # entropy bonus
    recon_coef: float = 0.5        # reconstruction auxiliary (run-15 weighted MSE)

    # Quantile-Huber.
    qr_kappa: float = 1.0

    # Recon-loss settings (must match the autoencoder training settings).
    recon_kind: str = "mse"
    content_weight: float = 100.0
    content_threshold: float = 0.5

    # Discounting.
    gamma: float = 0.95
    gae_lambda: float = 0.95

    # Reconstruction pretrain. For the first `recon_pretrain_iters`:
    # force action=0 (Posner: 'wait' — episodes always run the full 30 steps),
    # update ONLY the reconstruction loss. This is the run-15 setup running
    # online, letting the encoder learn the env's visual statistics before
    # any PPO signal. Set 0 to disable.
    recon_pretrain_iters: int = 0


def recon_pretrain_update(
    model: RViTPlusModel,
    optimizer: torch.optim.Optimizer,
    batch: RolloutBatch,
    cfg: PPOConfig,
) -> dict:
    """Reconstruction-only parameter update during the pretrain phase.

    No PPO surrogate, no value loss — just the content-weighted MSE
    backpropagated through the encoder+decoder. Actor and critic heads
    receive ZERO gradient here; they don't start moving until PPO kicks in.
    """
    model.train()
    total = 0.0
    n_updates = 0
    for _ in range(cfg.n_epochs):
        out = model.forward_rl_sequence(batch.observations, return_decoder=True)
        recon_loss = content_weighted_recon_loss(
            out["recons"], batch.observations, batch.valid_mask,
            recon_kind=cfg.recon_kind, content_weight=cfg.content_weight,
            content_threshold=cfg.content_threshold,
        )
        loss = cfg.recon_coef * recon_loss
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=cfg.grad_clip)
        optimizer.step()
        total += float(recon_loss.detach().item())
        n_updates += 1
    return {
        "loss_recon": total / max(n_updates, 1),
        "loss_policy": 0.0, "loss_value": 0.0, "loss_entropy": 0.0,
        "loss_total": total / max(n_updates, 1),
        "approx_kl": 0.0,
        "n_updates": float(n_updates),
    }


def _predictive_coding_loss(states_seq, head, valid_mask):
    """Predictive-coding auxiliary: C_{3, X, t-1} predicts C_{2, t}.

    states_seq : list of T tuples (C₁, C₂, C₃_X) per timestep, each tensor
                 (B, c_i, h_i, w_i). C_2 is element [1], C_3 is element [2].
    head       : PredictiveCodingHead mapping (B, c3, h3, w3) → (B, c2, h2, w2).
    valid_mask : (B, T) float — 1 for valid steps, 0 for padded.

    Returns (loss, mean_cos_sim):
        loss          : scalar (1 − mean cosine over valid t ≥ 1).
        mean_cos_sim  : python float, useful diagnostic.
    """
    T_len = len(states_seq)
    if T_len < 2 or head is None:
        return None, 0.0

    c3_stack = torch.stack([s[2] for s in states_seq], dim=1)                # (B, T, c3, h3, w3)
    c2_stack = torch.stack([s[1] for s in states_seq], dim=1).detach()       # (B, T, c2, h2, w2)

    B, T = c3_stack.shape[:2]
    prev_c3 = c3_stack[:, :-1]                                                # (B, T-1, c3, h3, w3)
    target  = c2_stack[:, 1:]                                                 # (B, T-1, c2, h2, w2) detached

    # Predictor sees (B·(T-1), c3, h3, w3) → (B·(T-1), c2, h2, w2).
    prev_flat = prev_c3.reshape(B * (T - 1), *prev_c3.shape[2:])
    pred_flat = head(prev_flat)
    pred = pred_flat.reshape(B, T - 1, *pred_flat.shape[1:])                  # (B, T-1, c2, h2, w2)

    # Cosine over the full (C, H, W) flatten per (b, t).
    pred_v   = pred.reshape(B, T - 1, -1)
    target_v = target.reshape(B, T - 1, -1)
    pred_n   = torch.nn.functional.normalize(pred_v,   dim=-1)
    target_n = torch.nn.functional.normalize(target_v, dim=-1)
    cos_sim  = (pred_n * target_n).sum(dim=-1)                                # (B, T-1)

    valid = valid_mask[:, 1:]                                                 # (B, T-1)
    denom = valid.sum().clamp(min=1.0)
    loss = ((1.0 - cos_sim) * valid).sum() / denom
    with torch.no_grad():
        mean_cs = (cos_sim * valid).sum().item() / denom.item()
    return loss, mean_cs


def _code_kl_anchor(post_logits, prior_logits, valid, cfg):
    """Shared code-space objective for both discrete PC variants.

    post_logits, prior_logits : (N, K, V, h, w) — posterior (from C₂ via the
                                tokenizer) and prior (from C₃ₜ₋₁ via the
                                predictor) categorical logits over V classes.
    valid                     : (N, 1, 1, 1) — 1 for valid (b, t ≥ 1) entries.

    Returns (loss, diag):
        loss = pc_kl_dyn·KL(sg(post)‖prior)          # trains the prior/dynamics
             + pc_kl_rep·KL(post‖sg(prior))          # trains the posterior
             + pc_anchor_coef·(−MI(input; code))     # InfoMax anti-collapse
    DreamerV3 KL-balancing + free bits. Whether the posterior carries gradient
    into the encoder is the caller's choice (it detaches C₂ before tokenizing,
    or not).
    """
    K = post_logits.shape[1]
    Hh, Ww = post_logits.shape[-2:]
    log_p = F.log_softmax(prior_logits, dim=2)                               # over V classes
    log_q = F.log_softmax(post_logits,  dim=2)
    q = log_q.exp()

    kl_dyn = (q.detach() * (log_q.detach() - log_p)).sum(dim=2)              # (N, K, h, w)
    kl_rep = (q * (log_q - log_p.detach())).sum(dim=2)                       # (N, K, h, w)
    fb = float(cfg.pc_free_bits)
    if fb > 0.0:
        kl_dyn = kl_dyn.clamp(min=fb)
        kl_rep = kl_rep.clamp(min=fb)

    denom = valid.sum().clamp(min=1.0) * K * Hh * Ww
    L_dyn = (kl_dyn * valid).sum() / denom
    L_rep = (kl_rep * valid).sum() / denom

    # InfoMax anchor: maximize MI(input ; code) = H(E[q]) − E[H(q)]. The first
    # term forbids "everyone picks the same code" (marginal collapse); the
    # second keeps each prediction confident. Discrete collapse guard (replaces
    # SIGReg / an EMA target encoder).
    valid_e = valid.unsqueeze(2)                                            # (N, 1, 1, 1, 1)
    marg_denom = valid.sum().clamp(min=1.0) * Hh * Ww
    q_marg = (q * valid_e).sum(dim=(0, 3, 4)) / marg_denom                  # (K, V)
    H_marg = -(q_marg * (q_marg + 1e-9).log()).sum(dim=-1)                  # (K,)
    H_cond = (-(q * (q + 1e-9).log()).sum(dim=2) * valid).sum() / denom
    mi = H_marg.mean() - H_cond
    loss = cfg.pc_kl_dyn * L_dyn + cfg.pc_kl_rep * L_rep + cfg.pc_anchor_coef * (-mi)

    with torch.no_grad():
        diag = {"pred": float(L_dyn.item()), "ppl": float(H_marg.mean().exp().item())}
    return loss, diag


def _discrete_jepa_loss(states_seq, predictor, tokenizer, valid_mask, cfg):
    """Discrete categorical latent JEPA — drop-in replacement for the cosine
    PC loss when ``cfg.pc_kind == "discrete_jepa"``.

    Instead of regressing C₂ₜ in continuous space (cosine), we DISCRETIZE the
    target into a per-spatial-position categorical code (K groups × V classes,
    DreamerV3-style) and have the deep specialist state at t-1 PREDICT that
    code (V-JEPA-style latent prediction, but classification rather than
    regression). The match is computed entirely in latent code space — no
    pixels — and cross-entropy lets the prediction stay MULTIMODAL under a
    stochastic future (the Posner change), where a regressor would collapse to
    the blurry mean.

    Data flow per (b, t ≥ 1) and per C₂ spatial position:
        posterior  q = softmax_V( tokenizer(C₂ₜ) )            # the realized code
        prior      p = softmax_V( predictor(C₃_{X,t-1}) )     # the predicted code
        L_dyn      = KL( sg(q) ‖ p )      → grad into predictor + cell3_X
        L_rep      = KL( q ‖ sg(p) )      → grad into tokenizer (+ C₂ if not detached)
        L_anchor   = −MI(input; code)     → anti-collapse (keeps codes informative)

    states_seq : list of T tuples (C₁, C₂, C₃_X). C₂ = element [1], C₃ = [2].
    predictor  : PredictiveCodingHead with c_out = K·V, (h3,w3) → (h2,w2).
    tokenizer  : Conv2d(c2, K·V, 1) producing per-position code logits.
    valid_mask : (B, T) float — 1 for valid steps, 0 for padded.

    Returns (loss, diag) where diag = {"pred": mean L_dyn (↓ = better),
    "ppl": code perplexity in [1, V] (↓ to 1 ⇒ collapse)}.
    """
    T_len = len(states_seq)
    if T_len < 2 or predictor is None or tokenizer is None:
        return None, {"pred": 0.0, "ppl": 0.0}

    K, Vc = int(cfg.pc_groups), int(cfg.pc_classes)
    c3_stack = torch.stack([s[2] for s in states_seq], dim=1)                # (B, T, c3, h3, w3)
    c2_stack = torch.stack([s[1] for s in states_seq], dim=1)                # (B, T, c2, h2, w2)
    B, T = c3_stack.shape[:2]

    prev_c3 = c3_stack[:, :-1]                                               # (B, T-1, c3, h3, w3)
    cur_c2  = c2_stack[:, 1:]                                                # (B, T-1, c2, h2, w2)
    if cfg.pc_detach_c2:
        cur_c2 = cur_c2.detach()

    N = B * (T - 1)
    prior_logits = predictor(prev_c3.reshape(N, *prev_c3.shape[2:]))         # (N, K·V, h2, w2)
    Hh, Ww = prior_logits.shape[-2:]
    post_logits  = tokenizer(cur_c2.reshape(N, *cur_c2.shape[2:]))           # (N, K·V, h2, w2)
    prior_logits = prior_logits.view(N, K, Vc, Hh, Ww)
    post_logits  = post_logits.view(N, K, Vc, Hh, Ww)
    valid = valid_mask[:, 1:].reshape(N, 1, 1, 1)
    return _code_kl_anchor(post_logits, prior_logits, valid, cfg)


def _discrete_latent_loss(states_seq, branch_states_seq, tokenizer, predictor, valid_mask, cfg):
    """World-model dynamics / JEPA loss for ``cfg.pc_kind == "discrete_latent"``.

    Here the categorical code is ALSO the latent the agent reads (see
    ``model._route_states_to_heads`` — the heads get embed(z) in the C₂ slot),
    so this term is the DYNAMICS loss: the per-branch predictor P_X(C₃ₜ₋₁)
    learns to predict the next shared posterior code. The posterior is NOT
    detached — its representation term + the InfoMax anchor shape the encoder,
    exactly as in DreamerV3 (the latent is additionally anchored by the policy /
    value gradient that flows through the straight-through z at the heads, so
    the code is forced to be informative to earn reward).

    states_seq        : raw per-step (C₁, C₂, C₃); the SHARED C₂ is element [1].
    branch_states_seq : head-routed per-step states; this branch's C₃_X is [2]
                        (element [1] is embed(z) and is not used here).
    tokenizer         : shared model.pc_tokenizer (C₂ → K·V code logits).
    predictor         : this branch's PredictiveCodingHead (C₃ₜ₋₁ → K·V).
    """
    T_len = len(states_seq)
    if T_len < 2 or predictor is None or tokenizer is None:
        return None, {"pred": 0.0, "ppl": 0.0}

    K, Vc = int(cfg.pc_groups), int(cfg.pc_classes)
    c2_stack = torch.stack([s[1] for s in states_seq], dim=1)                # (B, T, c2, h2, w2) shared C₂
    c3_stack = torch.stack([s[2] for s in branch_states_seq], dim=1)         # (B, T, c3, h3, w3) branch C₃_X
    B, T = c2_stack.shape[:2]

    cur_c2  = c2_stack[:, 1:]                                                # posterior target (NOT detached)
    prev_c3 = c3_stack[:, :-1]                                               # prior context
    N = B * (T - 1)
    post_logits  = tokenizer(cur_c2.reshape(N, *cur_c2.shape[2:]))           # (N, K·V, h2, w2)
    Hh, Ww = post_logits.shape[-2:]
    prior_logits = predictor(prev_c3.reshape(N, *prev_c3.shape[2:]))         # (N, K·V, h2, w2)
    post_logits  = post_logits.view(N, K, Vc, Hh, Ww)
    prior_logits = prior_logits.view(N, K, Vc, Hh, Ww)
    valid = valid_mask[:, 1:].reshape(N, 1, 1, 1)
    return _code_kl_anchor(post_logits, prior_logits, valid, cfg)


def _per_step_quantile_huber(
    pred: torch.Tensor,
    target: torch.Tensor,
    taus: torch.Tensor,
    kappa: float = 1.0,
) -> torch.Tensor:
    """Per-step quantile-Huber loss reduced over the (i, j) quantile-pair axes only.

    pred, target : (B, T, N) or (n, N)
    Returns      : (B, T) or (n,) scalar per-step loss.
    """
    *leading, N_pred = pred.shape
    *_,        N_tgt = target.shape
    # delta[..., i, j] = target[j] - pred[i]
    delta = target.unsqueeze(-2) - pred.unsqueeze(-1)                  # (..., N_pred, N_tgt)
    abs_delta = delta.abs()
    huber = torch.where(
        abs_delta <= kappa,
        0.5 * delta.pow(2),
        kappa * (abs_delta - 0.5 * kappa),
    )
    weight = (taus.view(*([1] * len(leading)), -1, 1) - (delta < 0).float()).abs()
    return (weight * huber).mean(dim=(-2, -1))                          # (..., )


def ppo_update(
    model: RViTPlusModel,
    optimizer: torch.optim.Optimizer,
    batch: RolloutBatch,
    cfg: PPOConfig,
    recon_enabled: bool = True,
) -> dict:
    """Run cfg.n_epochs PPO updates on the batch using a distributional critic.

    Loss = − L_PPO + value_coef · L_QR − entropy_coef · H + recon_coef · L_recon.
    """
    model.train()

    # GAE / advantages are no longer used by the actor — under the PAC
    # actor loss, Q drives the policy update directly via the MPO E-step.
    # We do keep `compute_distributional_targets` later for the critic's
    # quantile-Huber loss; it does not depend on GAE.

    accumulated = {
        "loss_policy": 0.0, "loss_value": 0.0, "loss_entropy": 0.0,
        "loss_recon": 0.0,  "loss_total": 0.0,
        "approx_kl": 0.0,
        "n_updates": 0.0,
        # Track skipped optimizer steps separately so we never silently swallow
        # gradient-norm overflow. n_loss_evals counts forward passes regardless
        # of whether the optimizer step fired.
        "n_loss_evals": 0.0,
        "n_skipped": 0.0,
        "max_grad_elem": 0.0,
        # Predictive-coding diagnostics. cosine mode: pc_cos_* is the mean
        # cosine sim between P_X(C_{3,X,t-1}) and C_{2,t}.detach() → ↑ toward 1.
        # discrete_jepa mode: pc_cos_* holds L_dyn (prediction KL, ↓ better) and
        # pc_ppl_* holds the code perplexity in [1, V] (↓ toward 1 ⇒ collapse).
        "pc_actor_loss":   0.0,
        "pc_critic_loss":  0.0,
        "pc_cos_actor":    0.0,
        "pc_cos_critic":   0.0,
        "pc_ppl_actor":    0.0,
        "pc_ppl_critic":   0.0,
        # Per-episode priorities (mean per-step quantile-Huber error over the
        # episode's valid timesteps), captured at the end of the final epoch
        # and used by the PER buffer for priority refresh.
        "per_episode_priority": None,
    }

    taus = model.critic_head.taus           # (N,)
    B, T = batch.actions.shape
    arange_BT = (
        torch.arange(B, device=batch.actions.device).view(B, 1).expand(B, T),
        torch.arange(T, device=batch.actions.device).view(1, T).expand(B, T),
    )

    for _epoch in range(cfg.n_epochs):
        # Re-encode the whole trajectory with gradient enabled.
        out = model.forward_rl_sequence(batch.observations, return_decoder=recon_enabled)
        logits_t = out["actor_logits_seq"]          # (B, T, A)
        q_dist_t = out["q_dist_seq"]                # (B, T, A, N)
        V_dist_t = out["V_dist_seq"]                # (B, T, N)

        m = batch.valid_mask
        # Per-episode IS weight (1 for fresh, PER-corrected for replay).
        if batch.sample_weights is not None:
            w_b = batch.sample_weights                     # (B,)
        else:
            w_b = torch.ones(m.shape[0], device=m.device, dtype=m.dtype)
        mw = m * w_b.unsqueeze(-1)                         # (B, T) — weighted mask
        denom_mw = mw.sum().clamp(min=1.0)
        denom = m.sum().clamp(min=1.0)                     # unweighted, kept for diagnostics
        actions = batch.actions.long()

        # ── Padded-step sanitization. Zero out forward outputs at masked
        # positions BEFORE anything else uses them. NaN * 0 = NaN in IEEE
        # floats, so `(loss * m).sum()` would otherwise propagate NaN
        # gradients even when m=0 at the offending step. Use torch.where
        # (NaN-safe) rather than `x * m`.
        mask_bta  = m.unsqueeze(-1)                                  # (B, T, 1)
        mask_btan = m.unsqueeze(-1).unsqueeze(-1)                    # (B, T, 1, 1)
        logits_t  = torch.where(mask_bta.bool(),  logits_t,  torch.zeros_like(logits_t))
        q_dist_t  = torch.where(mask_btan.bool(), q_dist_t,  torch.zeros_like(q_dist_t))
        V_dist_t  = torch.where(mask_bta.bool(),  V_dist_t,  torch.zeros_like(V_dist_t))

        # ── PAC actor loss (MPO + behavioral cloning) ──────────────────
        # Replaces PPO's clipped surrogate. Q drives the actor DIRECTLY
        # through the MPO E-step weights.
        if model.n_actions != 2:
            raise NotImplementedError(
                f"PAC actor loss currently assumes n_actions == 2 (we "
                f"reconstruct π_old(·|s) from the scalar log π_old(a_t|s)). "
                f"Got n_actions={model.n_actions}."
            )
        dist    = Categorical(logits=logits_t)
        entropy = dist.entropy()                                            # (B, T)

        # 1. Reconstruct π_old per-action from the stored scalar log π_old(a_t|s).
        # Valid only for binary action spaces.
        log_pi_old_at = batch.old_log_probs.clamp(max=-1e-6)                # (B, T)
        pi_old_at     = log_pi_old_at.exp().clamp(min=1e-6, max=1.0 - 1e-6) # (B, T)
        pi_old_other  = (1.0 - pi_old_at).clamp(min=1e-6)                   # (B, T)
        log_pi_old_other = pi_old_other.log()
        log_pi_old = torch.zeros(B, T, 2, device=logits_t.device, dtype=logits_t.dtype)
        log_pi_old.scatter_(-1, actions.unsqueeze(-1),       log_pi_old_at.unsqueeze(-1))
        log_pi_old.scatter_(-1, (1 - actions).unsqueeze(-1), log_pi_old_other.unsqueeze(-1))

        # 2. MPO E-step (closed-form for discrete actions, detached target):
        #    q(a|s) = softmax_a[ log π_old(a|s) + Q̄(s, a) / η ]
        q_per_action = q_dist_t.detach().mean(dim=-1)                       # (B, T, A)
        log_q_unnorm = log_pi_old + q_per_action / max(cfg.mpo_temperature, 1e-6)
        log_q_target = log_q_unnorm - log_q_unnorm.logsumexp(dim=-1, keepdim=True)
        q_target     = log_q_target.exp().detach()                          # (B, T, A)

        # 3. M-step + BC (weighted cross-entropy + executed-action log-prob):
        #    L_actor = (1−α) · (−Σ_a q(a|s)·log π_θ(a|s))  +  α · (−log π_θ(a_t|s))
        log_pi = torch.log_softmax(logits_t, dim=-1)                        # (B, T, A)
        L_mpo  = -(q_target * log_pi).sum(dim=-1)                           # (B, T)
        L_bc   = -log_pi.gather(-1, actions.unsqueeze(-1)).squeeze(-1)      # (B, T)
        loss_policy_per_step = (1.0 - cfg.bc_alpha) * L_mpo + cfg.bc_alpha * L_bc
        loss_policy  = (loss_policy_per_step * mw).sum() / denom_mw
        loss_entropy = -(entropy * mw).sum() / denom_mw

        # ── Distributional value loss (quantile-Huber) ───────────────────
        # Target: r_t + γ V_dist(s_{t+1}) · (1 − done_t).
        # Stop-grad on the target (standard).
        with torch.no_grad():
            target_q = compute_distributional_targets(
                rewards=batch.rewards, V_dist_seq=V_dist_t.detach(),
                dones=batch.dones, last_V_dist=batch.last_V_dist, gamma=cfg.gamma,
            )                                         # (B, T, N)

        # Gather predicted Q-dist for the executed action: q_dist_t[b, t, action[b,t], :]
        # → (B, T, N).
        b_idx, t_idx = arange_BT
        pred_q = q_dist_t[b_idx, t_idx, actions]      # (B, T, N)

        # Per-(B, T) quantile-Huber. Padded steps have q_dist sanitized to
        # zeros (above), so QH(0, 0) at padded positions is small and is
        # multiplied out by the mask anyway.
        per_bt_qh = _per_step_quantile_huber(
            pred_q, target_q, taus, kappa=cfg.qr_kappa,
        )                                                              # (B, T)
        # Weighted-mean value loss (weight = valid_mask · IS-weight).
        loss_value = (per_bt_qh * mw).sum() / denom_mw
        # Per-episode priority for PER (mean QH over valid steps, no IS).
        with torch.no_grad():
            ep_qh_sum  = (per_bt_qh * m).sum(dim=-1)
            ep_valid   = m.sum(dim=-1).clamp(min=1.0)
            ep_priority = (ep_qh_sum / ep_valid).detach()              # (B,)
            accumulated["per_episode_priority"] = ep_priority.cpu()

        # ── Reconstruction auxiliary ────────────────────────────────────
        if recon_enabled:
            loss_recon = content_weighted_recon_loss(
                out["recons"], batch.observations, batch.valid_mask,
                recon_kind=cfg.recon_kind, content_weight=cfg.content_weight,
                content_threshold=cfg.content_threshold,
            )
        else:
            loss_recon = torch.zeros((), device=logits_t.device, dtype=logits_t.dtype)

        # ── Predictive-coding / discrete-JEPA auxiliary ─────────────────────
        # P_X(C_{3, X, t-1}) predicts the next-step shared middle state C_{2, t}
        # — in continuous LATENT space (pc_kind="cosine") or in DISCRETE CODE
        # space (pc_kind="discrete_jepa"). The target is stop-gradded, so the
        # predictive gradient flows into the predictor + cell3_X only. Operates
        # on encoder dynamics — no (action, reward) labels — so it stays active
        # even when the actor collapses.
        loss_pc_actor  = torch.zeros((), device=logits_t.device, dtype=logits_t.dtype)
        loss_pc_critic = torch.zeros((), device=logits_t.device, dtype=logits_t.dtype)

        def _pc_branch(states_key, head_attr, tok_attr):
            head = getattr(model, head_attr, None)
            if head is None:
                return None, {"pred": 0.0, "ppl": 0.0}
            if cfg.pc_kind == "discrete_latent":
                # Shared posterior from raw C₂ (states_seq); per-branch prior
                # from C₃ₜ₋₁ (the routed branch states).
                return _discrete_latent_loss(
                    out.get("states_seq", []), out.get(states_key, []),
                    getattr(model, "pc_tokenizer", None), head, m, cfg,
                )
            if cfg.pc_kind == "discrete_jepa":
                return _discrete_jepa_loss(
                    out.get(states_key, []), head, getattr(model, tok_attr, None), m, cfg,
                )
            l, cos = _predictive_coding_loss(out.get(states_key, []), head, m)
            return l, {"pred": cos, "ppl": 0.0}

        def _accum_pc(prefix, l, diag):
            for key, val in (
                (f"pc_{prefix}_loss", float(l.detach().item())),
                (f"pc_cos_{prefix}", diag["pred"]),
                (f"pc_ppl_{prefix}", diag["ppl"]),
            ):
                accumulated[key] = (accumulated[key] * _epoch + val) / (_epoch + 1)

        if cfg.pc_actor_coef > 0.0:
            l_a, diag_a = _pc_branch("actor_states_seq", "pc_actor_head", "pc_actor_tokenizer")
            if l_a is not None:
                loss_pc_actor = l_a
                _accum_pc("actor", l_a, diag_a)
        if cfg.pc_critic_coef > 0.0:
            l_c, diag_c = _pc_branch("critic_states_seq", "pc_critic_head", "pc_critic_tokenizer")
            if l_c is not None:
                loss_pc_critic = l_c
                _accum_pc("critic", l_c, diag_c)

        loss = (
            loss_policy
            + cfg.value_coef * loss_value
            + cfg.entropy_coef * loss_entropy
            + cfg.recon_coef * loss_recon
            + cfg.pc_actor_coef * loss_pc_actor
            + cfg.pc_critic_coef * loss_pc_critic
        )

        # ── Accumulate loss VALUES first (always), so the report reflects what
        # the model actually produced — independent of whether the optimizer
        # step fired. Without this, a non-finite grad_norm silently zeroes
        # the reported losses, hiding both the model's true state and the
        # fact that updates aren't happening.
        with torch.no_grad():
            # Diagnostic: KL(π_old || π_θ). For the PAC actor loss this is
            # the natural drift measure between the stored behavior policy
            # and the current policy. Replaces PPO's `(ratio − 1) − log r`
            # estimator (which assumed PPO's ratio framework).
            pi_old_full = log_pi_old.exp()
            kl_per_step = (pi_old_full * (log_pi_old - log_pi)).sum(dim=-1)   # (B, T)
            approx_kl   = (kl_per_step * mw).sum() / denom_mw

        accumulated["loss_policy"]  += float(loss_policy.detach().item())
        accumulated["loss_value"]   += float(loss_value.detach().item())
        accumulated["loss_entropy"] += float(loss_entropy.detach().item())
        accumulated["loss_recon"]   += float(loss_recon.detach().item() if isinstance(loss_recon, torch.Tensor) else loss_recon)
        accumulated["loss_total"]   += float(loss.detach().item())
        accumulated["approx_kl"]    += float(approx_kl.detach().item())
        accumulated["n_loss_evals"] += 1

        # ── Now the backward + grad-clip + step. ───────────────────────────
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        # Diagnostic: max absolute gradient element across all params. If this
        # is huge (>1e10), the L2 norm computation will overflow even though
        # individual params still have "finite" gradients, and clip_grad_norm_
        # will return inf.
        max_grad_elem = 0.0
        for p in model.parameters():
            if p.grad is not None:
                m_p = p.grad.detach().abs().max().item()
                if m_p > max_grad_elem:
                    max_grad_elem = m_p
        accumulated["max_grad_elem"] = max(accumulated["max_grad_elem"], max_grad_elem)

        # Stage 1: per-element clip BEFORE computing L2 norm. Prevents any
        # single gradient element from being so large that squaring it
        # overflows fp32 (~3.4e38) → L2 norm = inf → silent skip. With
        # grad_value_clip=1e6, healthy O(1) gradients pass through untouched
        # and only catastrophic outliers (run-13 saw 2.65e21) get bounded.
        nn.utils.clip_grad_value_(model.parameters(), clip_value=cfg.grad_value_clip)

        # Stage 2: standard L2-norm clip — now safe from overflow.
        grad_norm = nn.utils.clip_grad_norm_(model.parameters(), max_norm=cfg.grad_clip)

        if not torch.isfinite(grad_norm):
            # Should be impossible after the per-element clip, but keep the
            # NaN guard as belt-and-suspenders.
            optimizer.zero_grad(set_to_none=True)
            accumulated["n_skipped"] += 1
            continue
        optimizer.step()
        accumulated["n_updates"] += 1

    # Divide loss values by the number of times they were COMPUTED (n_loss_evals),
    # not by n_updates. Otherwise skipped-due-to-grad-overflow epochs give 0/1=0
    # which hides genuine loss values.
    n_evals = max(accumulated["n_loss_evals"], 1.0)
    LOSS_KEYS = {"loss_policy", "loss_value", "loss_entropy", "loss_recon", "loss_total",
                 "approx_kl"}
    # UCB diagnostics are already epoch-averaged via EMA in the loop above;
    # they pass through here without further division.
    result = {}
    for k, v in accumulated.items():
        if k in LOSS_KEYS:
            result[k] = v / n_evals
        else:
            # n_updates, n_loss_evals, n_skipped, max_grad_elem — pass through as-is
            result[k] = v
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Outer training loop
# ─────────────────────────────────────────────────────────────────────────────


def train(
    model: RViTPlusModel,
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
    """Outer PPO-with-distributional-critic-and-recon-aux training loop."""
    if device is None:
        device = next(model.parameters()).device

    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr, eps=1e-5)
    history: list[dict] = []

    print(f"[setup] device={device}")
    print(f"[setup] n_actions={model.n_actions}, n_quantiles={model.n_quantiles}")
    print(f"[setup] PPO coefs: value={cfg.value_coef}, entropy={cfg.entropy_coef}, recon={cfg.recon_coef}")
    print(f"[setup] γ={cfg.gamma}, λ={cfg.gae_lambda}, clip={cfg.clip_range}, lr={cfg.lr}")
    print(f"[setup] pretrain: {cfg.recon_pretrain_iters} iters (action=0 forced, recon-only)")
    print(f"[setup] PER buffer: capacity={cfg.buffer_capacity}, n_replay={cfg.per_n_replay}, "
          f"α={cfg.per_alpha}, β={cfg.per_beta_start}→{cfg.per_beta_end}")

    # PER buffer. Filled by pushing fresh episodes after every PPO update;
    # sampled before every update (once enough episodes have accumulated).
    buffer = EpisodeReplayBuffer(
        capacity=cfg.buffer_capacity, priority_clip=cfg.per_priority_clip,
    )

    _correct_buf = collections.deque(maxlen=rolling_window)
    _return_buf = collections.deque(maxlen=rolling_window)

    t_start = time.time()
    for it in range(n_iterations):
        in_pretrain = it < cfg.recon_pretrain_iters

        fresh_batch, rollout_stats = collect_episodes(
            model=model, env=env, n_episodes=episodes_per_iter,
            device=device, force_action=0 if in_pretrain else None,
        )
        n_fresh = fresh_batch.observations.shape[0]

        if in_pretrain:
            # Pretrain: recon-only, no PPO + no PER. Buffer pushes still happen
            # so it's warm by the time real training starts.
            update_stats = recon_pretrain_update(model, optimizer, fresh_batch, cfg)
            buffer.push(fresh_batch, priorities=None)             # init with max priority
        else:
            # ── PER: sample replay episodes (linearly-annealed β). ──
            beta_frac = min(it / max(n_iterations - 1, 1), 1.0)
            beta_now  = cfg.per_beta_start + (cfg.per_beta_end - cfg.per_beta_start) * beta_frac
            sampled_idxs = None
            if cfg.per_n_replay > 0 and len(buffer) > 0:
                replay_batch, sampled_idxs, _ = buffer.sample(
                    n=cfg.per_n_replay, alpha=cfg.per_alpha, beta=beta_now, device=device,
                )
                combined_batch = concat_batches([fresh_batch, replay_batch])
            else:
                combined_batch = concat_batches([fresh_batch])    # fresh-only, weights=ones

            update_stats = ppo_update(
                model, optimizer, combined_batch, cfg,
                recon_enabled=(cfg.recon_coef > 0),
            )

            # ── PER: refresh priorities + push fresh into the buffer. ──
            ep_pri = update_stats.get("per_episode_priority", None)
            if ep_pri is not None:
                if sampled_idxs is not None:
                    buffer.update_priorities(sampled_idxs, ep_pri[n_fresh:])
                buffer.push(fresh_batch, priorities=ep_pri[:n_fresh])
            else:
                buffer.push(fresh_batch, priorities=None)
            update_stats["per_beta"] = beta_now
            update_stats["per_buffer_size"] = len(buffer)
            update_stats["per_n_replay_used"] = (
                cfg.per_n_replay if sampled_idxs is not None else 0
            )
            # Drop the priority tensor from update_stats so the log dict stays
            # JSON-serialisable / scalar-only downstream.
            update_stats.pop("per_episode_priority", None)
        batch = fresh_batch   # for compatibility with downstream rolling-stat logic

        _correct_buf.append(rollout_stats["rollout/correct_rate"])
        _return_buf.append(rollout_stats["rollout/mean_return"])
        roll_correct = sum(_correct_buf) / len(_correct_buf)
        roll_return = sum(_return_buf) / len(_return_buf)

        log = {"iter": it, **rollout_stats, **update_stats,
               "rolling/correct_rate": roll_correct,
               "rolling/mean_return": roll_return}
        history.append(log)

        if (it + 1) % log_every == 0:
            elapsed = time.time() - t_start
            phase = "pretrain" if in_pretrain else "ppo"
            n_upd = log.get("n_updates", 0)
            n_skip = log.get("n_skipped", 0)
            max_g = log.get("max_grad_elem", 0.0)
            skip_flag = f" ⚠ skip={int(n_skip)}" if n_skip > 0 else ""
            pca = log.get("pc_actor_loss", 0.0)
            pcc = log.get("pc_critic_loss", 0.0)
            pcca = log.get("pc_cos_actor", 0.0)
            pccc = log.get("pc_cos_critic", 0.0)
            if cfg.pc_actor_coef <= 0 and cfg.pc_critic_coef <= 0:
                pc_str = ""
            elif cfg.pc_kind in ("discrete_jepa", "discrete_latent"):
                ppla = log.get("pc_ppl_actor", 0.0)
                pplc = log.get("pc_ppl_critic", 0.0)
                pc_str = (f"  PC[a/c]=[{pca:.4f}/{pcc:.4f}]  klDyn[a/c]=[{pcca:.3f}/{pccc:.3f}]"
                          f"  ppl[a/c]=[{ppla:.1f}/{pplc:.1f}]")
            else:
                pc_str = f"  PC[a/c]=[{pca:.4f}/{pcc:.4f}]  pcCos[a/c]=[{pcca:+.3f}/{pccc:+.3f}]"
            buf_size = log.get("per_buffer_size", None)
            buf_str = (f"  buf={buf_size}/{cfg.buffer_capacity} "
                       f"β={log.get('per_beta', 0.0):.2f} +rep={log.get('per_n_replay_used', 0)}"
                       if buf_size is not None else "")
            print(
                f"[{phase} {it:5d} | {elapsed:6.1f}s] "
                f"correct={roll_correct:.3f}  return={roll_return:.3f}  "
                f"len={log['rollout/mean_length']:.1f}  "
                f"L_pol={log['loss_policy']:+.4f}  "
                f"L_val={log['loss_value']:.4f}  "
                f"L_rec={log['loss_recon']:.4f}  "
                f"H={-log['loss_entropy']:.3f}  "
                f"KL={log['approx_kl']:.4f}  "
                f"upd={int(n_upd)}  gmax={max_g:.2e}{pc_str}{buf_str}{skip_flag}"
            )

        if checkpoint_dir is not None and (it + 1) % save_every == 0:
            os.makedirs(checkpoint_dir, exist_ok=True)
            ckpt_path = os.path.join(checkpoint_dir, "rvit_plus_rl_latest.pt")
            torch.save({"iter": it, "model_state_dict": model.state_dict()}, ckpt_path)
            print(f"[checkpoint] saved to {ckpt_path}")

    return history
