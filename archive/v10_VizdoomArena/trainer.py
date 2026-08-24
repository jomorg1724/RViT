"""
RL trainer for V10 — PAC actor loss + distributional QR-DQN critic +
prioritized SEGMENT replay + EMA target network.

This is the v5 trainer (RViT_plus_v5/ppo.py) with three structural changes,
each forced by the arena's ~1050-step episodes (v5's episodes were 29 steps
and were re-encoded whole):

  1. SEGMENTS, not episodes (R2D2 stored-state strategy): one persistent env
     is rolled continuously; fixed-length segments are stored together with
     the recurrent state at their first step and re-encoded from it at update
     time. Episode boundaries inside a segment carry a done flag and reset
     the recurrent state to the learned H₀ (at collection AND re-encode).
     A `replay_burn_in` prefix of each segment is excluded from all losses
     and from priorities — it only warms the state from the (stale) stored
     init.

  2. n-STEP distributional targets (default n=3; n=1 recovers v5's exact
     1-step form):  G⁽ᵏ⁾_t = r_t + γ(1−d_t)·G⁽ᵏ⁻¹⁾_{t+1}, bootstrapped from
     the TARGET network's V_dist on the segment's T+1st frame.

  3. EMA target network (the user-attributed stabilizer): θ′ ← (1−τ)·θ′ + τ·θ
     after EVERY optimizer step (τ=0.01 ≈ v5's 100-step hard copy time
     constant). θ′ provides BOTH the critic's TD bootstrap and the MPO E-step
     reference policy π_θ′ — exactly PAC §3.2, smoother schedule.

Unchanged from v5 (verbatim where possible): the closed-form discrete MPO
E-step + BC blend, quantile-Huber on the executed action's Q-distribution,
expected-SARSA V with stop-grad π, PER priority = mean per-step
quantile-Huber (clipped at priority_clip×median, IS weights β→1), masked
weighted means, two-stage gradient clipping with non-finite skip.
"""
from __future__ import annotations

import collections
import copy
import json
import os
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
from torch.distributions import Categorical

try:
    from .model import V10ArenaModel
except ImportError:  # pragma: no cover
    from model import V10ArenaModel  # type: ignore[no-redef]


# ─────────────────────────────────────────────────────────────────────────────
# Segment storage
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class SegmentBatch:
    """A batch of fixed-length rollout segments (CPU until the update).

    obs holds T+1 frames: frame t is the input that PRODUCED action t; frame
    T is the bootstrap frame. Frames are uint8 to keep the buffer small —
    the update normalizes on-device.
    """

    obs: torch.Tensor          # (B, T+1, 3, H, W) uint8
    feats: torch.Tensor        # (B, T+1, F)       float32
    actions: torch.Tensor      # (B, T)            long
    rewards: torch.Tensor      # (B, T)            float32
    dones: torch.Tensor        # (B, T)            float32 (0/1)
    valid: torch.Tensor        # (B, T)            float32
    init_H: torch.Tensor       # (B, L, N, d)      float32 — stored recurrent state
    init_C: torch.Tensor       # (B, L, N, d)      float32
    sample_weights: Optional[torch.Tensor] = None  # (B,) or None → ones


def concat_segment_batches(batches: list[SegmentBatch]) -> SegmentBatch:
    fields = ["obs", "feats", "actions", "rewards", "dones", "valid", "init_H", "init_C"]
    out = {f: torch.cat([getattr(b, f) for b in batches], dim=0) for f in fields}
    weights = []
    for b in batches:
        if b.sample_weights is None:
            weights.append(torch.ones(b.obs.shape[0], dtype=torch.float32))
        else:
            weights.append(b.sample_weights.cpu())
    out["sample_weights"] = torch.cat(weights, dim=0)
    return SegmentBatch(**out)


# ─────────────────────────────────────────────────────────────────────────────
# Prioritized segment replay (v5's EpisodeReplayBuffer, segment-granular)
# ─────────────────────────────────────────────────────────────────────────────


class SegmentReplayBuffer:
    """FIFO ring buffer of segments with prioritized sampling (Schaul 2016).

    Priority = mean per-step quantile-Huber error over the segment's loss-mask
    steps, refreshed when sampled. p_i ∝ priority_i^α; IS weights
    w_i = (1/(N·p_i))^β / max_j w_j. Priorities clamped at
    priority_clip × median. Segments live on CPU (uint8 frames).
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

    def push(self, batch: SegmentBatch, priorities: Optional[torch.Tensor] = None) -> None:
        B = batch.obs.shape[0]
        if priorities is None:
            pri_np = np.full((B,), self._max_priority, dtype=np.float64)
        else:
            pri_np = priorities.detach().cpu().numpy().astype(np.float64)
        for b in range(B):
            seg = {
                "obs":     batch.obs[b].cpu(),
                "feats":   batch.feats[b].cpu(),
                "actions": batch.actions[b].cpu(),
                "rewards": batch.rewards[b].cpu(),
                "dones":   batch.dones[b].cpu(),
                "valid":   batch.valid[b].cpu(),
                "init_H":  batch.init_H[b].cpu(),
                "init_C":  batch.init_C[b].cpu(),
            }
            pri = max(float(pri_np[b]), 1e-6)
            if len(self._buffer) < self.capacity:
                self._buffer.append(seg)
                self._priorities.append(pri)
            else:
                self._buffer[self._next_idx] = seg
                self._priorities[self._next_idx] = pri
                self._next_idx = (self._next_idx + 1) % self.capacity
            self._max_priority = max(self._max_priority, pri)

    def sample(self, n: int, alpha: float, beta: float) -> tuple[SegmentBatch, np.ndarray]:
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
        Nb = float(len(self._buffer))
        w = (1.0 / (Nb * probs[idxs])) ** beta
        w = w / max(float(w.max()), 1e-8)

        segs = [self._buffer[i] for i in idxs]
        batch = SegmentBatch(
            obs     = torch.stack([s["obs"] for s in segs]),
            feats   = torch.stack([s["feats"] for s in segs]),
            actions = torch.stack([s["actions"] for s in segs]),
            rewards = torch.stack([s["rewards"] for s in segs]),
            dones   = torch.stack([s["dones"] for s in segs]),
            valid   = torch.stack([s["valid"] for s in segs]),
            init_H  = torch.stack([s["init_H"] for s in segs]),
            init_C  = torch.stack([s["init_C"] for s in segs]),
            sample_weights = torch.tensor(w, dtype=torch.float32),
        )
        return batch, idxs

    def update_priorities(self, idxs: np.ndarray, new_priorities: torch.Tensor) -> None:
        new_np = new_priorities.detach().cpu().numpy().astype(np.float64)
        for i, idx in enumerate(idxs):
            pri = max(float(new_np[i]), 1e-6)
            self._priorities[idx] = pri
            self._max_priority = max(self._max_priority, pri)


# ─────────────────────────────────────────────────────────────────────────────
# Segment collection — ONE persistent env, recurrent state carried across
# segments, stored at every segment start (R2D2 stored-state)
# ─────────────────────────────────────────────────────────────────────────────


class SegmentCollector:
    """Rolls a single env continuously and cuts the stream into fixed-length
    segments. The recurrent state is carried across segment boundaries and a
    copy is stored with each segment; on episode end the env auto-resets and
    the state is reset to the learned H₀ (matching forward_segment)."""

    def __init__(self, env, device: torch.device, seg_len: int, ep_window: int = 25) -> None:
        self.env = env
        self.device = device
        self.T = int(seg_len)
        self._obs, self._feats = env.reset()
        self._states = None
        self.episode_stats: collections.deque = collections.deque(maxlen=ep_window)
        self.total_env_steps = 0
        self.total_episodes = 0

    def _to_model_inputs(self, obs: np.ndarray, feats: np.ndarray):
        x = torch.from_numpy(obs).to(self.device).float().div_(255.0).unsqueeze(0)
        f = torch.from_numpy(feats).to(self.device).unsqueeze(0)
        return x, f

    def collect(
        self, model: V10ArenaModel, n_segments: int, random_actions: bool = False,
        explore_eps: float = 0.0,
    ) -> tuple[SegmentBatch, dict]:
        model.eval()
        T = self.T
        if self._states is None:
            self._states = model.init_states(1, device=self.device)

        seg_obs, seg_feats, seg_act, seg_rew, seg_done = [], [], [], [], []
        seg_iH, seg_iC = [], []

        with torch.no_grad():
            for _ in range(n_segments):
                iH, iC = model.states_to_tensors(self._states)
                seg_iH.append(iH[0].cpu())                    # (L, N, d)
                seg_iC.append(iC[0].cpu())
                obs_l = [self._obs]
                feats_l = [self._feats]
                act_l, rew_l, done_l = [], [], []

                for _t in range(T):
                    x, f = self._to_model_inputs(self._obs, self._feats)
                    step = model.rl_step(x, f, self._states)
                    self._states = step["new_states"]
                    if random_actions or (explore_eps > 0.0 and np.random.rand() < explore_eps):
                        a = int(np.random.randint(model.n_actions))
                    else:
                        a = int(Categorical(logits=step["actor_logits"][0]).sample().item())
                    obs2, feats2, r, done, info = self.env.step(a)

                    act_l.append(a)
                    rew_l.append(float(r))
                    done_l.append(1.0 if done else 0.0)
                    if done:
                        self._states = model.init_states(1, device=self.device)
                        self.total_episodes += 1
                        if "episode" in info:
                            self.episode_stats.append(info["episode"])
                    self._obs, self._feats = obs2, feats2
                    obs_l.append(obs2)
                    feats_l.append(feats2)
                    self.total_env_steps += 1

                seg_obs.append(torch.from_numpy(np.stack(obs_l)))           # (T+1,3,H,W) u8
                seg_feats.append(torch.from_numpy(np.stack(feats_l)))       # (T+1,F)
                seg_act.append(torch.tensor(act_l, dtype=torch.long))
                seg_rew.append(torch.tensor(rew_l, dtype=torch.float32))
                seg_done.append(torch.tensor(done_l, dtype=torch.float32))

        batch = SegmentBatch(
            obs=torch.stack(seg_obs),
            feats=torch.stack(seg_feats),
            actions=torch.stack(seg_act),
            rewards=torch.stack(seg_rew),
            dones=torch.stack(seg_done),
            valid=torch.ones(n_segments, T, dtype=torch.float32),
            init_H=torch.stack(seg_iH),
            init_C=torch.stack(seg_iC),
        )
        eps = list(self.episode_stats)
        stats = {
            "rollout/ep_return": float(np.mean([e["return"] for e in eps])) if eps else float("nan"),
            "rollout/ep_kills":  float(np.mean([e["kills"] for e in eps])) if eps else float("nan"),
            "rollout/ep_length": float(np.mean([e["length"] for e in eps])) if eps else float("nan"),
            "rollout/ep_damage": float(np.mean([e.get("damage", np.nan) for e in eps])) if eps else float("nan"),
            "rollout/ep_hits":   float(np.mean([e.get("hits", np.nan) for e in eps])) if eps else float("nan"),
            "rollout/episodes_done": float(self.total_episodes),
            "rollout/env_steps": float(self.total_env_steps),
        }
        return batch, stats


# ─────────────────────────────────────────────────────────────────────────────
# Distributional n-step target + per-step quantile-Huber (v5's, generalized)
# ─────────────────────────────────────────────────────────────────────────────


def compute_nstep_distributional_targets(
    rewards: torch.Tensor,        # (B, T)
    dones: torch.Tensor,          # (B, T)
    V_dist_tgt: torch.Tensor,     # (B, T+1, N) — TARGET network V-dist incl. bootstrap frame
    gamma: float,
    n_step: int = 1,
) -> torch.Tensor:
    """n-step distributional TD target with episode-boundary resets:

        G⁽¹⁾_t = r_t + γ(1−d_t)·V(s_{t+1})
        G⁽ᵏ⁾_t = r_t + γ(1−d_t)·G⁽ᵏ⁻¹⁾_{t+1}   (falls back to 1-step at the
                                                  segment's right edge)
    Returns (B, T, N). n_step=1 is exactly v5's compute_distributional_targets.
    """
    r = rewards.unsqueeze(-1)                                  # (B,T,1)
    nd = (1.0 - dones).unsqueeze(-1)                           # (B,T,1)
    V_next = V_dist_tgt[:, 1:]                                 # (B,T,N)
    G = r + gamma * nd * V_next
    for _ in range(max(1, int(n_step)) - 1):
        G_shift = torch.cat([G[:, 1:], V_next[:, -1:]], dim=1)  # G_{t+1}; edge → V
        G = r + gamma * nd * G_shift
    return G


def _per_step_quantile_huber(
    pred: torch.Tensor, target: torch.Tensor, taus: torch.Tensor, kappa: float = 1.0,
) -> torch.Tensor:
    """Quantile-Huber reduced over the (i,j) quantile-pair axes only.
    pred, target: (B,T,N) → (B,T). Verbatim from v5."""
    *leading, N_pred = pred.shape
    delta = target.unsqueeze(-2) - pred.unsqueeze(-1)
    abs_delta = delta.abs()
    huber = torch.where(abs_delta <= kappa, 0.5 * delta.pow(2), kappa * (abs_delta - 0.5 * kappa))
    weight = (taus.view(*([1] * len(leading)), -1, 1) - (delta < 0).float()).abs()
    return (weight * huber).mean(dim=(-2, -1))


# ─────────────────────────────────────────────────────────────────────────────
# EMA target network
# ─────────────────────────────────────────────────────────────────────────────


def ema_update(target_model: nn.Module, model: nn.Module, tau: float) -> None:
    """Polyak update θ′ ← (1−τ)·θ′ + τ·θ (parameters only; the lone buffer,
    the critic's constant `taus`, never changes)."""
    with torch.no_grad():
        for p_t, p in zip(target_model.parameters(), model.parameters()):
            p_t.lerp_(p, tau)


# ─────────────────────────────────────────────────────────────────────────────
# PAC + QR-DQN update
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PACConfig:
    # Optimisation.
    lr: float = 3e-4
    n_epochs: int = 1
    grad_clip: float = 0.5
    grad_value_clip: float = 1.0e6

    # PAC actor loss (MPO E-step + BC).
    # Run-1 postmortem (2026-06-10): the E-step reference π_θ′ is the EMA of
    # the SAME policy being trained, which forms a positive-feedback runaway —
    # simulation showed η=0.1 collapses entropy 2.64→0.003 on a 0.05 Q-edge
    # (even with bc_alpha=0) while η=1.0 is stable. Hence: η=1.0, the reference
    # mixed with `ref_uniform_mix` uniform so it can never zero-out an action,
    # entropy_coef 10×, bc_alpha halved (BC self-imitation amplifies collapse).
    mpo_temperature: float = 1.0
    bc_alpha: float = 0.05
    ref_uniform_mix: float = 0.05

    # Exploration floor during collection: with prob ε take a uniform-random
    # action, so the replay distribution never irreversibly collapses and the
    # critic keeps seeing data on all actions.
    explore_eps: float = 0.05

    # EMA target network θ′ (TD bootstrap + E-step reference π_θ′).
    ema_tau: float = 0.01

    # Warmup: collect with a uniform-random policy and train the critic only
    # (actor frozen) for the first N iterations — fills the buffer and settles
    # the value scale before the policy moves (v5's burn-in, re-pointed).
    warmup_iters: int = 50

    # Segments.
    seg_len: int = 64
    segments_per_iter: int = 4
    replay_burn_in: int = 8          # loss-masked state-warmup prefix per segment

    # Prioritized segment replay.
    buffer_capacity: int = 512
    per_n_replay: int = 4
    per_alpha: float = 0.6
    per_beta_start: float = 0.4
    per_beta_end: float = 1.0
    per_priority_clip: float = 50.0

    # Loss coefficients / discounting.
    value_coef: float = 0.5
    entropy_coef: float = 0.1
    qr_kappa: float = 1.0
    gamma: float = 0.99
    n_step: int = 3


def pac_update(
    model: V10ArenaModel,
    target_model: V10ArenaModel,
    optimizer: torch.optim.Optimizer,
    batch: SegmentBatch,
    cfg: PACConfig,
    device: torch.device,
    train_actor: bool = True,
) -> dict:
    """One PAC + QR-DQN update over a batch of segments.

        L = L_actor(MPO+BC) + value_coef·L_QR − entropy_coef·H

    The TD bootstrap distribution AND the MPO E-step reference policy come
    from the EMA target θ′ (evaluated once; θ′ is quasi-static within an
    update). train_actor=False (warmup) freezes the actor: critic-only."""
    model.train()

    B, T = batch.actions.shape
    obs = batch.obs.to(device).float().div_(255.0)             # (B,T+1,3,H,W)
    feats = batch.feats.to(device)
    actions = batch.actions.to(device).long()
    rewards = batch.rewards.to(device)
    dones = batch.dones.to(device)
    valid = batch.valid.to(device)
    init_states = V10ArenaModel.tensors_to_states(
        batch.init_H.to(device), batch.init_C.to(device))
    w_b = batch.sample_weights.to(device) if batch.sample_weights is not None \
        else torch.ones(B, device=device)

    # Loss mask: valid steps minus the replay burn-in prefix (state warm-up).
    loss_mask = valid.clone()
    k = min(max(int(cfg.replay_burn_in), 0), T - 1)
    if k > 0:
        loss_mask[:, :k] = 0.0
    mw = loss_mask * w_b.unsqueeze(-1)                          # (B,T)
    denom_mw = mw.sum().clamp(min=1.0)

    taus = model.critic_head.taus
    arange_B = torch.arange(B, device=device).view(B, 1).expand(B, T)
    arange_T = torch.arange(T, device=device).view(1, T).expand(B, T)

    # ── EMA target θ′: bootstrap V-dist + E-step reference policy (once) ─────
    target_model.eval()
    with torch.no_grad():
        tout = target_model.forward_segment(obs, feats, init_states=init_states, dones=dones)
        target_q = compute_nstep_distributional_targets(
            rewards=rewards, dones=dones, V_dist_tgt=tout["V_dist_seq"],
            gamma=cfg.gamma, n_step=cfg.n_step,
        )                                                       # (B,T,N)
        # E-step reference: EMA policy MIXED with uniform (run-1 postmortem) —
        # the reference can never assign ~0 probability to an action, which
        # breaks the π_ref-chases-π positive-feedback collapse at its source.
        pi_ref = torch.softmax(tout["actor_logits_seq"][:, :T], dim=-1)          # (B,T,A)
        m_mix = min(max(float(cfg.ref_uniform_mix), 0.0), 1.0)
        if m_mix > 0.0:
            pi_ref = (1.0 - m_mix) * pi_ref + m_mix / pi_ref.shape[-1]
        log_pi_ref = torch.log(pi_ref.clamp(min=1e-12))                          # (B,T,A)

    accumulated = {
        "loss_policy": 0.0, "loss_value": 0.0, "loss_entropy": 0.0,
        "loss_total": 0.0, "approx_kl": 0.0,
        "n_updates": 0.0, "n_loss_evals": 0.0, "n_skipped": 0.0, "max_grad_elem": 0.0,
        "per_segment_priority": None,
    }

    for _epoch in range(cfg.n_epochs):
        out = model.forward_segment(obs, feats, init_states=init_states, dones=dones)
        logits_t = out["actor_logits_seq"][:, :T]               # (B,T,A)
        q_dist_t = out["q_dist_seq"][:, :T]                     # (B,T,A,N)

        # ── PAC actor loss (MPO + BC), reference policy = EMA π_θ′ ──────────
        if train_actor:
            dist = Categorical(logits=logits_t)
            entropy = dist.entropy()                            # (B,T)

            # MPO E-step (closed-form, detached): q(a|s) = softmax[log π_θ′ + Q̄/η]
            q_per_action = q_dist_t.detach().mean(dim=-1)       # (B,T,A) online Q̄
            log_q_unnorm = log_pi_ref + q_per_action / max(cfg.mpo_temperature, 1e-6)
            log_q_target = log_q_unnorm - log_q_unnorm.logsumexp(dim=-1, keepdim=True)
            q_target_pi = log_q_target.exp().detach()           # (B,T,A)

            log_pi = torch.log_softmax(logits_t, dim=-1)
            L_mpo = -(q_target_pi * log_pi).sum(dim=-1)         # (B,T)
            L_bc = -log_pi.gather(-1, actions.unsqueeze(-1)).squeeze(-1)
            loss_policy_per_step = (1.0 - cfg.bc_alpha) * L_mpo + cfg.bc_alpha * L_bc
            loss_policy = (loss_policy_per_step * mw).sum() / denom_mw
            loss_entropy = -(entropy * mw).sum() / denom_mw
        else:
            loss_policy = logits_t.new_zeros(())
            loss_entropy = logits_t.new_zeros(())

        # ── Distributional value loss (quantile-Huber vs n-step EMA target) ──
        pred_q = q_dist_t[arange_B, arange_T, actions]          # (B,T,N)
        per_bt_qh = _per_step_quantile_huber(pred_q, target_q, taus, kappa=cfg.qr_kappa)
        loss_value = (per_bt_qh * mw).sum() / denom_mw

        # Per-segment priority for PER (mean QH over loss-mask steps, no IS).
        with torch.no_grad():
            seg_qh = (per_bt_qh * loss_mask).sum(dim=-1)
            seg_steps = loss_mask.sum(dim=-1).clamp(min=1.0)
            accumulated["per_segment_priority"] = (seg_qh / seg_steps).detach().cpu()

        loss = loss_policy + cfg.value_coef * loss_value + cfg.entropy_coef * loss_entropy

        with torch.no_grad():
            if train_actor:
                pi_ref = log_pi_ref.exp()
                kl_per_step = (pi_ref * (log_pi_ref - log_pi)).sum(dim=-1)
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

        # Two-stage clip: per-element (fp32 overflow guard) then L2 norm.
        nn.utils.clip_grad_value_(model.parameters(), clip_value=cfg.grad_value_clip)
        grad_norm = nn.utils.clip_grad_norm_(model.parameters(), max_norm=cfg.grad_clip)
        if not torch.isfinite(grad_norm):
            optimizer.zero_grad(set_to_none=True)
            accumulated["n_skipped"] += 1
            continue
        optimizer.step()
        accumulated["n_updates"] += 1

        # EMA target after every optimizer step.
        ema_update(target_model, model, cfg.ema_tau)

    n_evals = max(accumulated["n_loss_evals"], 1.0)
    LOSS_KEYS = {"loss_policy", "loss_value", "loss_entropy", "loss_total", "approx_kl"}
    return {k: (v / n_evals if k in LOSS_KEYS else v) for k, v in accumulated.items()}


# ─────────────────────────────────────────────────────────────────────────────
# Outer training loop
# ─────────────────────────────────────────────────────────────────────────────


def train(
    model: V10ArenaModel,
    env,
    *,
    n_iterations: int = 5000,
    cfg: PACConfig = PACConfig(),
    device: torch.device | None = None,
    log_every: int = 5,
    checkpoint_dir: str | None = None,
    save_every: int = 100,
    model_kwargs: Optional[dict] = None,
) -> list[dict]:
    """PAC + QR-DQN + segment-PER + EMA-target training loop."""
    if device is None:
        device = next(model.parameters()).device

    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr, eps=1e-5)
    history: list[dict] = []
    history_path = None
    if checkpoint_dir is not None:
        os.makedirs(checkpoint_dir, exist_ok=True)
        history_path = os.path.join(checkpoint_dir, "history.jsonl")

    print(f"[setup] device={device}")
    print(f"[setup] n_actions={model.n_actions}, n_quantiles={model.n_quantiles}, "
          f"n_tokens={model.n_tokens}, enc_layers={model.enc_layers}")
    print(f"[setup] PAC: η={cfg.mpo_temperature}, bc_α={cfg.bc_alpha}, "
          f"ref_mix={cfg.ref_uniform_mix}, ε_explore={cfg.explore_eps}; "
          f"value={cfg.value_coef}, entropy={cfg.entropy_coef}, γ={cfg.gamma}, n_step={cfg.n_step}")
    print(f"[setup] segments: T={cfg.seg_len} (+1 bootstrap frame), "
          f"{cfg.segments_per_iter}/iter fresh, burn_in={cfg.replay_burn_in}")
    print(f"[setup] PER: capacity={cfg.buffer_capacity}, n_replay={cfg.per_n_replay}, "
          f"α={cfg.per_alpha}, β={cfg.per_beta_start}→{cfg.per_beta_end}")
    print(f"[setup] EMA target: τ={cfg.ema_tau}/optimizer-step "
          f"(≈{int(round(1.0 / max(cfg.ema_tau, 1e-9)))}-step time constant); "
          f"warmup={cfg.warmup_iters} iters (random policy, critic only)")

    target_model = copy.deepcopy(model)
    for p in target_model.parameters():
        p.requires_grad_(False)
    target_model.eval()

    buffer = SegmentReplayBuffer(capacity=cfg.buffer_capacity,
                                 priority_clip=cfg.per_priority_clip)
    collector = SegmentCollector(env, device, seg_len=cfg.seg_len)

    t_start = time.time()
    for it in range(n_iterations):
        in_warmup = it < cfg.warmup_iters
        fresh_batch, rollout_stats = collector.collect(
            model, cfg.segments_per_iter, random_actions=in_warmup,
            explore_eps=cfg.explore_eps,
        )
        n_fresh = fresh_batch.obs.shape[0]

        beta_frac = min(it / max(n_iterations - 1, 1), 1.0)
        beta_now = cfg.per_beta_start + (cfg.per_beta_end - cfg.per_beta_start) * beta_frac
        sampled_idxs = None
        if (not in_warmup) and cfg.per_n_replay > 0 and len(buffer) > 0:
            replay_batch, sampled_idxs = buffer.sample(
                n=cfg.per_n_replay, alpha=cfg.per_alpha, beta=beta_now)
            combined = concat_segment_batches([fresh_batch, replay_batch])
        else:
            combined = concat_segment_batches([fresh_batch])

        update_stats = pac_update(model, target_model, optimizer, combined, cfg,
                                  device=device, train_actor=not in_warmup)
        update_stats["in_warmup"] = 1.0 if in_warmup else 0.0

        seg_pri = update_stats.pop("per_segment_priority", None)
        if seg_pri is not None:
            if sampled_idxs is not None:
                buffer.update_priorities(sampled_idxs, seg_pri[n_fresh:])
            buffer.push(fresh_batch, priorities=seg_pri[:n_fresh])
        else:
            buffer.push(fresh_batch, priorities=None)
        update_stats["per_beta"] = beta_now
        update_stats["per_buffer_size"] = len(buffer)

        log = {"iter": it, **rollout_stats, **update_stats}
        history.append(log)
        if history_path is not None:
            with open(history_path, "a") as f:
                f.write(json.dumps({k: v for k, v in log.items()}) + "\n")

        if (it + 1) % log_every == 0:
            elapsed = time.time() - t_start
            sps = collector.total_env_steps / max(elapsed, 1e-6)
            phase = "warm" if in_warmup else "pac "
            n_skip = log.get("n_skipped", 0)
            skip_flag = f" ⚠ skip={int(n_skip)}" if n_skip > 0 else ""
            print(
                f"[{phase}{it:5d} | {elapsed:7.1f}s] "
                f"kills={log['rollout/ep_kills']:.2f}  dmg={log['rollout/ep_damage']:.0f}  "
                f"hits={log['rollout/ep_hits']:.1f}  ret={log['rollout/ep_return']:.2f}  "
                f"len={log['rollout/ep_length']:.0f}  eps={int(log['rollout/episodes_done'])}  "
                f"L_pol={log['loss_policy']:+.4f}  L_val={log['loss_value']:.4f}  "
                f"H={-log['loss_entropy']:.3f}  KL={log['approx_kl']:.4f}  "
                f"buf={log['per_buffer_size']}/{cfg.buffer_capacity}  "
                f"env_sps={sps:.1f}{skip_flag}"
            )

        if checkpoint_dir is not None and (it + 1) % save_every == 0:
            ckpt_path = os.path.join(checkpoint_dir, "v10_latest.pt")
            torch.save({
                "iter": it,
                "model_state_dict": model.state_dict(),
                "target_state_dict": target_model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "model_kwargs": model_kwargs,
                "env_steps": collector.total_env_steps,
            }, ckpt_path)
            print(f"[checkpoint] saved to {ckpt_path}")

    return history
