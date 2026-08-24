#!/usr/bin/env python3
"""
Gradient audit for PRISM v2.

Goal
----
Diagnose why PRISM v2 is failing to learn after the architectural refactor
(per-channel gates, learned pools, head-compression backbone). User's
hypothesis: actor/critic gradients are tiny relative to backbone gradients,
so the policy/value heads barely move while the auxiliary PC objective
dominates parameter updates everywhere upstream.

What this script does
---------------------
1.  Load the latest checkpoint (`checkpoints/prism_v2_latest.pt`).
2.  Collect a small batch of episodes with the current model (no_grad).
3.  Run the *exact* `ppo_update` loss decomposition through ONE truncated
    BPTT chunk on this batch, and inspect gradients per module.
4.  Repeat with three different loss compositions to attribute who is
    pushing whom:
        (a) FULL  =  L_policy + value·L_value + entropy·L_entropy + pc·L_pc
        (b) RL   =  L_policy + value·L_value + entropy·L_entropy
        (c) PC   =  pc·L_pc
5.  For each pass, report per-module gradient summary stats:
        L1-norm, L2-norm, max |g|, fraction-zero, mean |g|/|θ|.
6.  Specifically print actor.fc1, actor.fc2, critic.fc1, critic.fc2
    versus gru_fast / gru_slow / head_backbone / stem_V1 / stem_V2.

Mathematical sanity check
-------------------------
For a deep recurrent net under joint PC + PPO training, we want the head
gradients (∂L_RL/∂θ_actor) to be comparable in magnitude to the upstream
backbone gradients (∂L_RL/∂θ_gru). If ‖g_actor‖ / ‖g_gru_fast‖ << 1, the
heads are starved and the PPO surrogate cannot improve.

Conversely, if ‖g_pc/θ_actor‖ ≈ 0 (PC does not flow into actor: correct,
since PC is computed before the heads), and ‖g_RL/θ_actor‖ is tiny too,
the heads are effectively frozen.

Usage
-----
    cd /Users/jonathanmorgan/AttentionManuscript/PrismV2
    python3 analysis/gradient_audit.py
    python3 analysis/gradient_audit.py --episodes 4 --bptt 16

References
----------
[1] Schulman et al. (2017) "PPO" — surrogate objective, value loss, entropy.
[2] Pascanu et al. (2013) "On the difficulty of training RNNs" — gradient
    norms across truncation chunks; we mimic the chunk-wise update.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass

import numpy as np
import torch
import torch.nn as nn
from torch.distributions import Categorical

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from env import ChangeDetectionEnv  # noqa: E402
from model import PrismV2Model  # noqa: E402
from ppo import PPOConfig, RolloutBatch, collect_episodes, compute_gae  # noqa: E402
from train import build_env, build_model, load_config  # noqa: E402


# ─── Module groups for grad reporting ──────────────────────────────────────────
# Order matters for the printed table.
MODULE_NAMES: tuple[str, ...] = (
    "stem_V1", "stem_V2",
    "film",
    "pixel_decoder", "feature_decoder_V1", "feature_decoder_V2",
    "gru_fast", "gru_slow",
    "inner_fast", "inner_slow",
    "cross_pool",
    "readout",
    "head_backbone",
    "actor", "critic",
)


def _module_owner(param_name: str) -> str:
    """Return the top-level submodule that owns this parameter."""
    return param_name.split(".", 1)[0]


def _device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


# ─── Per-module gradient stats container ──────────────────────────────────────


@dataclass
class ModuleGradStats:
    name: str
    n_params: int
    n_with_grad: int
    l1: float            # Σ |g|
    l2: float            # √Σ g²
    max_abs: float
    frac_zero: float     # fraction of param tensors with grad-norm == 0
    mean_abs_over_param: float  # E[|g|/|θ|], a scale-free signal


def _collect_module_stats(model: PrismV2Model) -> dict[str, ModuleGradStats]:
    """Walk model.named_parameters(); group by top-level module owner."""
    bucket: dict[str, dict] = {n: dict(
        n_params=0, n_with_grad=0,
        l1=0.0, sq=0.0, max_abs=0.0,
        frac_zero_num=0, frac_zero_den=0,
        ratio_sum=0.0, ratio_count=0,
    ) for n in MODULE_NAMES}

    for name, p in model.named_parameters():
        owner = _module_owner(name)
        if owner not in bucket:
            continue
        b = bucket[owner]
        b["n_params"] += p.numel()
        b["frac_zero_den"] += 1
        if p.grad is None:
            b["frac_zero_num"] += 1
            continue
        g = p.grad.detach()
        if torch.all(g == 0):
            b["frac_zero_num"] += 1
            continue
        b["n_with_grad"] += p.numel()
        b["l1"] += float(g.abs().sum().item())
        b["sq"] += float((g.float() ** 2).sum().item())
        b["max_abs"] = max(b["max_abs"], float(g.abs().max().item()))
        # Scale-free per-tensor ratio: ‖g‖₂ / max(‖θ‖₂, eps)
        gnorm = float(g.float().norm().item())
        pnorm = float(p.detach().float().norm().item())
        if pnorm > 1e-12:
            b["ratio_sum"] += gnorm / pnorm
            b["ratio_count"] += 1

    out: dict[str, ModuleGradStats] = {}
    for n in MODULE_NAMES:
        b = bucket[n]
        denom = max(b["frac_zero_den"], 1)
        ratio_n = max(b["ratio_count"], 1)
        out[n] = ModuleGradStats(
            name=n,
            n_params=b["n_params"],
            n_with_grad=b["n_with_grad"],
            l1=b["l1"],
            l2=b["sq"] ** 0.5,
            max_abs=b["max_abs"],
            frac_zero=b["frac_zero_num"] / denom,
            mean_abs_over_param=b["ratio_sum"] / ratio_n,
        )
    return out


def _print_grad_table(label: str, stats: dict[str, ModuleGradStats]) -> None:
    print(f"\n=== {label} ===")
    hdr = f"{'module':<20s} {'n_params':>10s} {'L1':>11s} {'L2':>11s} {'max|g|':>11s} {'frac0':>7s} {'|g|/|θ|':>11s}"
    print(hdr)
    print("-" * len(hdr))
    for name in MODULE_NAMES:
        s = stats[name]
        print(
            f"{s.name:<20s} {s.n_params:>10,d} "
            f"{s.l1:>11.3e} {s.l2:>11.3e} {s.max_abs:>11.3e} "
            f"{s.frac_zero:>7.2f} {s.mean_abs_over_param:>11.3e}"
        )


# ─── PPO forward + loss for one chunk, with selectable loss composition ──────


def _forward_chunk_losses(
    model: PrismV2Model,
    batch: RolloutBatch,
    cfg: PPOConfig,
    *,
    chunk_start: int = 0,
) -> dict[str, torch.Tensor]:
    """
    Forward through ONE truncated-BPTT chunk and return the four scalar losses
    (loss_policy, loss_value, loss_entropy, loss_pc). All differentiable.

    Mirrors ppo.ppo_update inner-chunk math exactly so gradients match
    the actual training step the user is running.
    """
    advantages, returns = compute_gae(
        rewards=batch.rewards, values=batch.old_values, dones=batch.dones,
        valid=batch.valid_mask, last_values=batch.last_values,
        gamma=cfg.gamma, lam=cfg.gae_lambda,
    )

    B, T = batch.observations.shape[:2]
    device = batch.observations.device
    chunk = cfg.bptt_truncation if cfg.bptt_truncation > 0 else T
    t0 = max(0, min(chunk_start, max(T - 1, 0)))
    t1 = min(t0 + chunk, T)

    Mf, Ms = model.init_memory(B, device=device)

    # Burn in any chunks before t0 with detach (cheap, but keeps memory state plausible).
    if t0 > 0:
        with torch.no_grad():
            for t in range(0, t0):
                step = model.forward_step(
                    batch.observations[:, t].contiguous(), Mf, Ms,
                )
                Mf, Ms = step.M_fast_next, step.M_slow_next

    Mf, Ms = Mf.detach(), Ms.detach()

    x_chunk = batch.observations[:, t0:t1]
    valid_chunk = batch.valid_mask[:, t0:t1]
    actions_chunk = batch.actions[:, t0:t1]
    old_logp_chunk = batch.old_log_probs[:, t0:t1]
    adv_chunk = advantages[:, t0:t1]
    ret_chunk = returns[:, t0:t1]

    logits_seq, values_seq, pc_steps = [], [], []
    for t in range(t1 - t0):
        step = model.forward_step(x_chunk[:, t].contiguous(), Mf, Ms)
        logits_seq.append(step.action_logits)
        values_seq.append(step.value)
        pc_steps.append(step.pc_loss)
        Mf, Ms = step.M_fast_next, step.M_slow_next

    logits_t = torch.stack(logits_seq, dim=1)
    values_t = torch.stack(values_seq, dim=1)
    pc_t = torch.stack(pc_steps, dim=0)

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
    loss_value = (((values_t - ret_chunk) ** 2) * m).sum() / denom
    loss_entropy = -(entropy * m).sum() / denom

    valid_per_t = valid_chunk.sum(dim=0)
    valid_total = valid_per_t.sum().clamp(min=1.0)
    loss_pc = (pc_t * valid_per_t).sum() / valid_total

    return {
        "policy": loss_policy,
        "value": loss_value,
        "entropy": loss_entropy,
        "pc": loss_pc,
    }


# ─── Main audit ───────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="PRISM v2 gradient audit.")
    parser.add_argument("--config", type=str, default=None)
    parser.add_argument("--episodes", type=int, default=8,
                        help="Number of episodes to roll out for the audit.")
    parser.add_argument("--bptt", type=int, default=None,
                        help="Override bptt_truncation for the audit chunk.")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    cfg = load_config(args.config)
    seed = int(args.seed)
    np.random.seed(seed); torch.manual_seed(seed)

    device = _device()
    print(f"[audit] device = {device}")

    env = build_env(cfg["environment"])
    model = build_model(cfg["model"], device)

    # Load latest checkpoint (mandatory for this audit).
    ckpt_dir = os.path.join(_BASE, cfg["run"].get("checkpoint_dir", "checkpoints"))
    ckpt_path = os.path.join(ckpt_dir, "prism_v2_latest.pt")
    if not os.path.isfile(ckpt_path):
        print(f"[audit] no checkpoint at {ckpt_path}; auditing from random init.")
    else:
        ckpt = torch.load(ckpt_path, map_location=device)
        model.load_state_dict(ckpt["model_state_dict"])
        print(f"[audit] loaded {ckpt_path} (iter {ckpt.get('iter','?')})")

    # PPO config from training config, with optional bptt override.
    pcfg_d = cfg["training"]
    pcfg = PPOConfig(
        lr=float(pcfg_d.get("lr", 3e-4)),
        n_epochs=int(pcfg_d.get("n_epochs", 4)),
        clip_range=float(pcfg_d.get("clip_range", 0.2)),
        value_coef=float(pcfg_d.get("value_coef", 0.5)),
        entropy_coef=float(pcfg_d.get("entropy_coef", 0.005)),
        pc_coef=float(pcfg_d.get("pc_coef", 1.0)),
        slow_coef=float(pcfg_d.get("slow_coef", 0.0)),
        grad_clip=float(pcfg_d.get("grad_clip", 0.5)),
        gamma=float(pcfg_d.get("gamma", 0.95)),
        gae_lambda=float(pcfg_d.get("gae_lambda", 0.95)),
        bptt_truncation=int(args.bptt if args.bptt is not None else pcfg_d.get("bptt_truncation", 16)),
        inner_K_warmup_iters=0,
        pc_pretrain_iters=0,
    )

    # Rollout (no_grad) to populate the batch.
    print(f"[audit] rolling out {args.episodes} episodes ...")
    batch, rstats = collect_episodes(
        model=model, env=env, n_episodes=args.episodes, device=device,
    )
    print(f"  rollout/correct_rate = {rstats['rollout/correct_rate']:.3f}")
    print(f"  rollout/mean_return  = {rstats['rollout/mean_return']:.3f}")
    print(f"  rollout/mean_length  = {rstats['rollout/mean_length']:.2f}")

    B, T = batch.observations.shape[:2]
    print(f"  batch B={B}, T_max={T}")

    # ── Pass 1: FULL loss (matches actual training) ────────────────────────────
    model.train()
    losses = _forward_chunk_losses(model, batch, pcfg, chunk_start=0)
    full_loss = (
        losses["policy"]
        + pcfg.value_coef * losses["value"]
        + pcfg.entropy_coef * losses["entropy"]
        + pcfg.pc_coef * losses["pc"]
    )
    print(
        f"\n[loss decomp at iter 0 chunk] "
        f"policy={float(losses['policy']):.4f}  "
        f"value={float(losses['value']):.4f}  "
        f"-entropy={float(losses['entropy']):.4f}  "
        f"pc={float(losses['pc']):.4f}  "
        f"TOTAL={float(full_loss):.4f}"
    )
    model.zero_grad(set_to_none=True)
    full_loss.backward()
    stats_full = _collect_module_stats(model)
    _print_grad_table("FULL  L = L_policy + 0.5·L_value + ε·L_entropy + 1.0·L_pc", stats_full)

    # ── Pass 2: RL-only loss ──────────────────────────────────────────────────
    losses = _forward_chunk_losses(model, batch, pcfg, chunk_start=0)
    rl_loss = (
        losses["policy"]
        + pcfg.value_coef * losses["value"]
        + pcfg.entropy_coef * losses["entropy"]
    )
    model.zero_grad(set_to_none=True)
    rl_loss.backward()
    stats_rl = _collect_module_stats(model)
    _print_grad_table("RL-ONLY  L = L_policy + 0.5·L_value + ε·L_entropy", stats_rl)

    # ── Pass 3: PC-only loss ──────────────────────────────────────────────────
    losses = _forward_chunk_losses(model, batch, pcfg, chunk_start=0)
    pc_loss = pcfg.pc_coef * losses["pc"]
    model.zero_grad(set_to_none=True)
    pc_loss.backward()
    stats_pc = _collect_module_stats(model)
    _print_grad_table("PC-ONLY  L = 1.0·L_pc", stats_pc)

    # ── Hypothesis test: actor/critic gradient magnitudes vs backbone ─────────
    print("\n" + "=" * 78)
    print("HYPOTHESIS CHECK: are actor/critic gradients tiny vs backbone?")
    print("=" * 78)

    def _ratio(a: float, b: float) -> str:
        if b <= 0:
            return "  (denom 0)"
        return f"{a / b:>10.3e}"

    backbones = ("gru_fast", "gru_slow", "stem_V1", "stem_V2", "head_backbone")
    heads = ("actor", "critic")

    print("\nL2-norm ratios under the FULL loss:")
    print(f"{'head/backbone':<28s} {'value':>12s}")
    for h in heads:
        for b in backbones:
            tag = f"||{h}|| / ||{b}||"
            print(f"  {tag:<28s} {_ratio(stats_full[h].l2, stats_full[b].l2)}")

    print("\nL2-norm ratios under RL-ONLY loss (this is what matters for the policy):")
    for h in heads:
        for b in backbones:
            tag = f"||{h}|| / ||{b}||"
            print(f"  {tag:<28s} {_ratio(stats_rl[h].l2, stats_rl[b].l2)}")

    print("\nScale-free per-tensor signal (E[||g||/||θ||], higher == bigger relative step):")
    print(f"{'module':<20s} {'FULL':>12s} {'RL-ONLY':>12s} {'PC-ONLY':>12s}")
    for n in MODULE_NAMES:
        print(
            f"  {n:<18s} "
            f"{stats_full[n].mean_abs_over_param:>12.3e} "
            f"{stats_rl[n].mean_abs_over_param:>12.3e} "
            f"{stats_pc[n].mean_abs_over_param:>12.3e}"
        )

    # ── Verdict ──────────────────────────────────────────────────────────────
    print("\nVERDICT")
    print("-------")
    actor_full_l2 = stats_full["actor"].l2
    critic_full_l2 = stats_full["critic"].l2
    grufast_full_l2 = stats_full["gru_fast"].l2
    head_backbone_full_l2 = stats_full["head_backbone"].l2

    actor_rl_l2 = stats_rl["actor"].l2
    critic_rl_l2 = stats_rl["critic"].l2
    grufast_rl_l2 = stats_rl["gru_fast"].l2

    print(
        f"actor.L2 (FULL) = {actor_full_l2:.3e}, "
        f"gru_fast.L2 (FULL) = {grufast_full_l2:.3e}, "
        f"ratio = {actor_full_l2 / max(grufast_full_l2, 1e-12):.3e}"
    )
    print(
        f"critic.L2 (FULL) = {critic_full_l2:.3e}, "
        f"head_backbone.L2 (FULL) = {head_backbone_full_l2:.3e}, "
        f"ratio = {critic_full_l2 / max(head_backbone_full_l2, 1e-12):.3e}"
    )
    print(
        f"actor.L2 (RL-only) = {actor_rl_l2:.3e}, "
        f"gru_fast.L2 (RL-only) = {grufast_rl_l2:.3e}, "
        f"ratio = {actor_rl_l2 / max(grufast_rl_l2, 1e-12):.3e}"
    )
    print(
        f"critic.L2 (RL-only) = {critic_rl_l2:.3e}, "
        f"gru_fast.L2 (RL-only) = {grufast_rl_l2:.3e}, "
        f"ratio = {critic_rl_l2 / max(grufast_rl_l2, 1e-12):.3e}"
    )

    # ── Dump a small JSON summary so we can plot/compare across runs ─────────
    out_dir = os.path.join(_BASE, "analysis", "out")
    os.makedirs(out_dir, exist_ok=True)
    summary = {
        "iter_loaded": int(ckpt.get("iter", -1)) if os.path.isfile(ckpt_path) else -1,
        "rollout": rstats,
        "stats_full": {n: vars(stats_full[n]) for n in MODULE_NAMES},
        "stats_rl": {n: vars(stats_rl[n]) for n in MODULE_NAMES},
        "stats_pc": {n: vars(stats_pc[n]) for n in MODULE_NAMES},
    }
    summary_path = os.path.join(out_dir, "gradient_audit_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[audit] summary → {summary_path}")


if __name__ == "__main__":
    main()
