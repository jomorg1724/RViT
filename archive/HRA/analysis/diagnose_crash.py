"""
Post-crash diagnostic: load HRA/checkpoints/hra_latest.pt (the iter-499
auto-save from the run that crashed at iter ~888) and characterise:

  - Distributional Q range (any quantile far outside the reward scale?)
  - Actor logit magnitudes (drifted to extreme values?)
  - Per-module parameter L2 norms (any sub-module growing huge?)
  - PC reconstruction quality
  - dQ on fresh rollouts under the loaded weights
"""
from __future__ import annotations

import os
import sys

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from HRA.env import ChangeDetectionEnv
from HRA.model import HRAModel


def main():
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    ckpt_path = "HRA/checkpoints/hra_latest.pt"
    state = torch.load(ckpt_path, map_location=device, weights_only=False)

    model = HRAModel(
        state_channels=(32, 64, 128), n_FR=5, n_heads=4,
        init_action_logit_bias=[0.0, -2.0],
        critic_kind="distributional", n_quantiles=51,
    ).to(device)
    model.load_state_dict(state["model_state_dict"])
    model.eval()
    print(f"[load] {ckpt_path}   iter={state.get('iter', '?')}")
    print(f"       device={device}")
    print(f"       n_params={sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
    print()

    # ── Per-module parameter L2 norms ─────────────────────────────────────
    print("─" * 64)
    print("[A] Per-module parameter L2 norms (looking for runaway weights)")
    print("─" * 64)
    rows = []
    for name, p in model.named_parameters():
        if p.requires_grad:
            n = p.numel()
            l2 = p.detach().float().norm().item()
            per_param_l2 = l2 / (n ** 0.5)  # normalised so we can compare across module sizes
            rows.append((name, n, l2, per_param_l2))
    rows.sort(key=lambda r: -r[3])
    print(f"{'module':<60s}  {'#params':>9s}  {'L2':>10s}  {'L2/√n':>8s}")
    for name, n, l2, per in rows[:20]:
        print(f"{name:<60s}  {n:>9d}  {l2:>10.4f}  {per:>8.4f}")
    print(f"... (showing top 20 of {len(rows)} parameter tensors)")
    print()

    # ── Actor logits range on fresh rollouts ──────────────────────────────
    print("─" * 64)
    print("[B] Actor logits on 30 fresh rollouts (action=0 forced)")
    print("─" * 64)
    env = ChangeDetectionEnv()
    all_logits = []
    all_q_dist = []
    all_pc = []
    with torch.no_grad():
        for _ in range(30):
            obs = env.reset()
            if isinstance(obs, tuple):
                obs = obs[0]
            states = model.init_states(1, device=device)
            for t in range(29):
                x = torch.from_numpy(np.ascontiguousarray(np.asarray(obs, dtype=np.float32).transpose(2, 0, 1))).to(device).unsqueeze(0)
                step = model.forward_step(x, states)
                all_logits.append(step.action_logits[0].cpu().numpy())
                all_q_dist.append(step.q_dist[0].cpu().numpy())
                all_pc.append(float(step.pc_loss.cpu().item()))
                states = step.layer_states_new
                obs, _, _, _ = env.step(0)
    all_logits = np.array(all_logits)        # (T, |A|)
    all_q_dist = np.array(all_q_dist)        # (T, |A|, N)
    print(f"logits[wait]   : min={all_logits[:,0].min():+8.2f}  mean={all_logits[:,0].mean():+8.2f}  max={all_logits[:,0].max():+8.2f}")
    print(f"logits[press]  : min={all_logits[:,1].min():+8.2f}  mean={all_logits[:,1].mean():+8.2f}  max={all_logits[:,1].max():+8.2f}")
    diff = all_logits[:, 0] - all_logits[:, 1]
    print(f"Δlogits        : min={diff.min():+8.2f}  mean={diff.mean():+8.2f}  max={diff.max():+8.2f}")
    p_press = np.exp(all_logits[:,1]) / (np.exp(all_logits[:,0]) + np.exp(all_logits[:,1]))
    print(f"P(press)       : min={p_press.min():.2e}  mean={p_press.mean():.2e}  max={p_press.max():.2e}")
    print()

    # ── Q-distribution range ──────────────────────────────────────────────
    print("─" * 64)
    print("[C] Q-distribution range (rewards in env are at most 5)")
    print("─" * 64)
    # Mean over batch, look at quantile range per action.
    q_per_action = all_q_dist  # (T, |A|, N)
    for a, name in enumerate(["wait", "press"]):
        q_a = q_per_action[:, a, :]  # (T, N)
        q_min = q_a.min(axis=1)      # per-step min quantile
        q_max = q_a.max(axis=1)
        q_mean = q_a.mean(axis=1)
        print(f"Q({name})  : per-step q_min in [{q_min.min():+6.3f}, {q_min.max():+6.3f}]")
        print(f"         : per-step q_max in [{q_max.min():+6.3f}, {q_max.max():+6.3f}]")
        print(f"         : per-step q_mean in [{q_mean.min():+6.3f}, {q_mean.max():+6.3f}]")
        print(f"         : quantile spread (max-min) mean={float(np.mean(q_max - q_min)):.3f}")
    dQ = np.abs(q_per_action[:, 0, :].mean(axis=1) - q_per_action[:, 1, :].mean(axis=1))
    print(f"dQ (|Q(wait) - Q(press)|): mean={dQ.mean():.3f}  max={dQ.max():.3f}")
    print()

    # ── PC reconstruction MSE ─────────────────────────────────────────────
    print("─" * 64)
    print("[D] PC reconstruction MSE")
    print("─" * 64)
    print(f"L_PC: min={min(all_pc):.4f}  mean={float(np.mean(all_pc)):.4f}  max={max(all_pc):.4f}")
    print()

    # ── FT residual scales ────────────────────────────────────────────────
    print("─" * 64)
    print("[E] FeedbackTransformer residual scales (start at 0; lift if FT useful)")
    print("─" * 64)
    print(f"cell1.ft_residual_scale = {model.cell1.ft_residual_scale.item():+.4f}")
    print(f"cell2.ft_residual_scale = {model.cell2.ft_residual_scale.item():+.4f}")
    print(f"cell3.ft_residual_scale = {model.cell3.ft_residual_scale.item():+.4f}")


if __name__ == "__main__":
    main()
