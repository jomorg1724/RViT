"""PAC/QR-DQN/PER trainer plus triplet-codebook anti-collapse regularizer."""
from __future__ import annotations

import collections
import copy
import importlib.util
import os
import sys
import time
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F

from model import TripletCodebookModel

_HERE = os.path.dirname(os.path.abspath(__file__))
_PAPER = os.path.join(os.path.dirname(_HERE), "RViT_plus_paper")
_PAPER_PPO = os.path.join(_PAPER, "ppo.py")

_spec = importlib.util.spec_from_file_location("paper_ppo_base_triplet", _PAPER_PPO)
base_ppo = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader

_old_path = list(sys.path)
_old_model = sys.modules.pop("model", None)
if _PAPER in sys.path:
    sys.path.remove(_PAPER)
sys.path.insert(0, _PAPER)
sys.modules["paper_ppo_base_triplet"] = base_ppo
_spec.loader.exec_module(base_ppo)
if _old_model is not None:
    sys.modules["model"] = _old_model
else:
    sys.modules.pop("model", None)
sys.path[:] = _old_path

RolloutBatch = base_ppo.RolloutBatch
EpisodeReplayBuffer = base_ppo.EpisodeReplayBuffer
collect_episodes = base_ppo.collect_episodes
ppo_update = base_ppo.ppo_update


@dataclass
class PPOConfig(base_ppo.PPOConfig):
    codebook_inter_coef: float = 0.05
    codebook_intra_coef: float = 0.005
    codebook_norm_coef: float = 0.0001
    codebook_temperature: float = 0.1


def codebook_contrastive_loss(
    model: TripletCodebookModel,
    cfg: PPOConfig,
) -> tuple[torch.Tensor, dict]:
    """Random-sampled codebook anti-collapse regularizer.

    Samples:
      * two different codebooks, one embedding from each -> strong repulsion
      * one codebook, two different embeddings within it -> weak repulsion
      * all codebook entries -> weak unit-ball drift penalty

    The implementation samples from the current codebook length (16 entries in
    the 4x4 variant); if this variant later uses 4 entries per book, the same
    code remains valid.
    """
    cb = model.encoder.attn.codebooks  # (3, N, D)
    n_books, n_entries, _ = cb.shape
    device = cb.device

    books = torch.randperm(n_books, device=device)[:2]
    i0 = torch.randint(n_entries, (1,), device=device).item()
    i1 = torch.randint(n_entries, (1,), device=device).item()
    a = F.normalize(cb[books[0], i0], dim=0)
    b = F.normalize(cb[books[1], i1], dim=0)
    inter_sim = torch.dot(a, b)
    inter_loss = F.softplus(inter_sim / max(cfg.codebook_temperature, 1e-6))

    book = torch.randint(n_books, (1,), device=device).item()
    pair = torch.randperm(n_entries, device=device)[:2]
    c = F.normalize(cb[book, pair[0]], dim=0)
    d = F.normalize(cb[book, pair[1]], dim=0)
    intra_sim = torch.dot(c, d)
    intra_loss = F.softplus(intra_sim / max(cfg.codebook_temperature, 1e-6))

    norms = cb.norm(dim=-1)
    # Weak "unit disc" regularizer: penalize entries drifting outside radius 1,
    # without forcing all entries onto the sphere.
    norm_loss = F.relu(norms - 1.0).pow(2).mean()

    total = (cfg.codebook_inter_coef * inter_loss
             + cfg.codebook_intra_coef * intra_loss
             + cfg.codebook_norm_coef * norm_loss)
    stats = {
        "loss_codebook_inter": float(inter_loss.detach().item()),
        "loss_codebook_intra": float(intra_loss.detach().item()),
        "loss_codebook_norm": float(norm_loss.detach().item()),
        "codebook_inter_sim": float(inter_sim.detach().item()),
        "codebook_intra_sim": float(intra_sim.detach().item()),
        "codebook_mean_norm": float(norms.detach().mean().item()),
    }
    return total, stats


def codebook_update(
    model: TripletCodebookModel,
    optimizer: torch.optim.Optimizer,
    cfg: PPOConfig,
) -> dict:
    if (cfg.codebook_inter_coef <= 0.0
            and cfg.codebook_intra_coef <= 0.0
            and cfg.codebook_norm_coef <= 0.0):
        return {
            "loss_codebook": 0.0, "loss_codebook_inter": 0.0, "loss_codebook_intra": 0.0,
            "loss_codebook_norm": 0.0, "codebook_inter_sim": 0.0, "codebook_intra_sim": 0.0,
            "codebook_mean_norm": float(model.encoder.attn.codebooks.detach().norm(dim=-1).mean().item()),
        }
    loss, stats = codebook_contrastive_loss(model, cfg)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    nn.utils.clip_grad_value_(model.parameters(), clip_value=cfg.grad_value_clip)
    grad_norm = nn.utils.clip_grad_norm_(model.parameters(), max_norm=cfg.grad_clip)
    if torch.isfinite(grad_norm):
        optimizer.step()
    stats["loss_codebook"] = float(loss.detach().item())
    return stats


def _ema_update(target_model: torch.nn.Module, model: torch.nn.Module, decay: float) -> None:
    with torch.no_grad():
        for tp, p in zip(target_model.parameters(), model.parameters()):
            tp.mul_(decay).add_(p.detach(), alpha=1.0 - decay)
        for tb, b in zip(target_model.buffers(), model.buffers()):
            tb.copy_(b)


def train(
    model: TripletCodebookModel,
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
    if device is None:
        device = next(model.parameters()).device

    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr, eps=1e-5)
    history: list[dict] = []

    import csv
    metrics_path = os.path.join(checkpoint_dir, "metrics.csv") if checkpoint_dir else None
    metrics_f = None
    metrics_w = None

    print(f"[setup] device={device}")
    print(f"[setup] n_actions={model.n_actions}, n_quantiles={model.n_quantiles}, "
          f"n_tokens={model.n_tokens}, enc_layers={model.enc_layers}")
    print(f"[setup] PAC: eta={cfg.mpo_temperature}, bc_alpha={cfg.bc_alpha}; "
          f"value={cfg.value_coef}, entropy={cfg.entropy_coef}, gamma={cfg.gamma}")
    print(f"[setup] codebook anti-collapse: inter={cfg.codebook_inter_coef}, "
          f"intra={cfg.codebook_intra_coef}, norm={cfg.codebook_norm_coef}, "
          f"temp={cfg.codebook_temperature}")
    print(f"[setup] PER buffer: capacity={cfg.buffer_capacity}, n_replay={cfg.per_n_replay}, "
          f"alpha={cfg.per_alpha}, beta={cfg.per_beta_start}->{cfg.per_beta_end}")

    target_model = None
    target_step = 0
    use_ema = bool(cfg.ema_decay and cfg.ema_decay > 0)
    if use_ema or (cfg.target_update_period and cfg.target_update_period > 0):
        target_model = copy.deepcopy(model)
        for p in target_model.parameters():
            p.requires_grad_(False)
        target_model.eval()
        print(f"[setup] PAC target {'EMA decay=' + str(cfg.ema_decay) if use_ema else 'hard-copy'}")

    buffer = EpisodeReplayBuffer(capacity=cfg.buffer_capacity, priority_clip=cfg.per_priority_clip)
    correct_buf = collections.deque(maxlen=rolling_window)
    return_buf = collections.deque(maxlen=rolling_window)

    t_start = time.time()
    for it in range(n_iterations):
        in_burn_in = it < cfg.burn_in_iters
        fresh_batch, rollout_stats = collect_episodes(
            model=model, env=env, n_episodes=episodes_per_iter, device=device,
            force_action=0 if in_burn_in else None,
        )
        n_fresh = fresh_batch.observations.shape[0]
        beta_frac = min(it / max(n_iterations - 1, 1), 1.0)
        beta_now = cfg.per_beta_start + (cfg.per_beta_end - cfg.per_beta_start) * beta_frac
        sampled_idxs = None
        if (not in_burn_in) and cfg.per_n_replay > 0 and len(buffer) > 0:
            replay_batch, sampled_idxs, _ = buffer.sample(
                n=cfg.per_n_replay, alpha=cfg.per_alpha, beta=beta_now, device=device,
            )
            combined_batch = base_ppo.concat_batches([fresh_batch, replay_batch])
        else:
            combined_batch = base_ppo.concat_batches([fresh_batch])

        update_stats = ppo_update(
            model, optimizer, combined_batch, cfg,
            target_model=target_model, train_actor=not in_burn_in,
        )
        update_stats.update(codebook_update(model, optimizer, cfg))
        update_stats["in_burn_in"] = 1.0 if in_burn_in else 0.0

        if target_model is not None:
            if use_ema:
                _ema_update(target_model, model, float(cfg.ema_decay))
            else:
                target_step += int(update_stats.get("n_updates", 0))
                if target_step >= cfg.target_update_period:
                    target_model.load_state_dict(model.state_dict())
                    target_step = 0

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

        correct_buf.append(rollout_stats["rollout/correct_rate"])
        return_buf.append(rollout_stats["rollout/mean_return"])
        roll_correct = sum(correct_buf) / len(correct_buf)
        roll_return = sum(return_buf) / len(return_buf)

        log = {"iter": it, **rollout_stats, **update_stats,
               "rolling/correct_rate": roll_correct, "rolling/mean_return": roll_return,
               "env/theta": float(getattr(env, "theta", float("nan")))}
        history.append(log)

        if metrics_path is not None:
            if metrics_w is None:
                os.makedirs(checkpoint_dir, exist_ok=True)
                metrics_f = open(metrics_path, "w", newline="")
                metrics_w = csv.DictWriter(metrics_f, fieldnames=list(log.keys()), extrasaction="ignore")
                metrics_w.writeheader()
            metrics_w.writerow(log)
            metrics_f.flush()

        if (it + 1) % log_every == 0:
            elapsed = time.time() - t_start
            phase = "burn" if log.get("in_burn_in", 0.0) > 0 else "ppo "
            buf_str = (f"  buf={log.get('per_buffer_size', 0)}/{cfg.buffer_capacity} "
                       f"beta={log.get('per_beta', 0.0):.2f} +rep={log.get('per_n_replay_used', 0)}")
            print(
                f"[{phase}{it:5d} | {elapsed:6.1f}s] "
                f"correct={roll_correct:.3f} return={roll_return:.3f} "
                f"len={log['rollout/mean_length']:.1f} "
                f"L_pol={log['loss_policy']:+.4f} L_val={log['loss_value']:.4f} "
                f"L_cb={log['loss_codebook']:.4f} cb_norm={log['codebook_mean_norm']:.3f} "
                f"H={-log['loss_entropy']:.3f} KL={log['approx_kl']:.4f} "
                f"theta={log['env/theta']:.1f} upd={int(log.get('n_updates', 0))}{buf_str}"
            )

        if checkpoint_dir is not None and (it + 1) % save_every == 0:
            os.makedirs(checkpoint_dir, exist_ok=True)
            ckpt_path = os.path.join(checkpoint_dir, "rvit_plus_rl_latest.pt")
            torch.save({"iter": it, "model_state_dict": model.state_dict()}, ckpt_path)
            print(f"[checkpoint] saved to {ckpt_path}")

    if metrics_f is not None:
        metrics_f.close()
        print(f"[metrics] per-iteration losses + codebook regularizer -> {metrics_path}")
    return history
