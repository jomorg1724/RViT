"""
Post-mortem diagnostic for a trained HRA checkpoint.

Loads HRA/checkpoints/hra_latest.pt, runs a batch of rollouts, and reports:
  - Action distribution across all timesteps (does it ever press?)
  - Mean entropy over the trial (has policy collapsed?)
  - Per-timestep mean Q values for each action (does dQ vary across the trial?)
  - Per-iteration attention-map sparsity (is attention doing anything?)
  - Hidden-state magnitude per layer (are recurrent states evolving?)
  - PC reconstruction error per timestep (is perception working?)

Run:
    /usr/bin/python3 HRA/analysis/diagnose_run.py
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


def load_model(ckpt_path: str, device: torch.device) -> HRAModel:
    state = torch.load(ckpt_path, map_location=device, weights_only=False)
    sd = state["model_state_dict"]
    # Infer state_channels from the saved weights: cell1.conv_reset.weight is
    # (state_C, in_C + state_C, 3, 3). For the default config in_C == state_C.
    # We just use the config defaults; if the user trained with different
    # state_channels, they should pass them in here.
    model = HRAModel(
        state_channels=(32, 64, 128),
        n_FR=5, n_heads=4,
        init_action_logit_bias=[0.0, -4.0],
        critic_kind="distributional",
        n_quantiles=51,
    ).to(device)
    model.load_state_dict(sd)
    print(f"[load] checkpoint iter = {state.get('iter', '?')}")
    print(f"[load] device          = {device}")
    print(f"[load] n_params        = {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
    return model


def collect_rollouts(model: HRAModel, env: ChangeDetectionEnv, n_episodes: int, device: torch.device) -> dict:
    """Run rollouts with the *learned* policy (sampling actions). Capture all
    relevant tensors for diagnostic analysis."""
    model.eval()
    from torch.distributions import Categorical

    all_obs = []
    all_actions = []
    all_rewards = []
    all_logits = []
    all_values = []
    all_q_dist = []
    all_attn_c1 = []  # take iteration-0 attention map of C_1
    all_state_mag = []  # |C_ell| per layer per step
    all_pc_pred = []
    all_pc_target = []
    all_lengths = []
    all_change_times = []
    all_correct = []
    all_pressed_at = []

    with torch.no_grad():
        for ep in range(n_episodes):
            obs = env.reset()
            if isinstance(obs, tuple):
                obs = obs[0]
            states = model.init_states(1, device=device)

            ep_obs, ep_act, ep_rew = [], [], []
            ep_logits, ep_vals, ep_qd = [], [], []
            ep_attn = []
            ep_smag = []
            ep_pc_pred = []
            ep_pc_target = []
            done = False
            pressed_at = None
            t = 0
            while not done:
                ep_obs.append(np.asarray(obs, dtype=np.float32))
                x_t = torch.from_numpy(np.ascontiguousarray(np.asarray(obs, dtype=np.float32).transpose(2, 0, 1))).to(device).unsqueeze(0)
                step = model.forward_step(x_t, states)

                logits = step.action_logits[0].cpu().numpy()
                dist = Categorical(logits=step.action_logits[0])
                a = int(dist.sample().item())
                if a == 1 and pressed_at is None:
                    pressed_at = t
                ep_logits.append(logits)
                ep_vals.append(float(step.value[0].item()))
                ep_qd.append(step.q_dist[0].cpu().numpy())  # (|A|, N)
                # Iteration-0 attention map of C_1 (most informative spatially).
                ep_attn.append(step.attn_per_layer[0][0][0].mean(dim=0).cpu().numpy())  # (N, N), mean over heads
                ep_smag.append([float(s.abs().mean().item()) for s in step.layer_states_new])
                ep_pc_pred.append(step.pc_pred[0].cpu().numpy())
                ep_pc_target.append(np.asarray(obs, dtype=np.float32).transpose(2, 0, 1))

                step_result = env.step(a)
                if len(step_result) == 5:
                    obs, r, terminated, truncated, _ = step_result
                    done = bool(terminated or truncated)
                else:
                    obs, r, done, _ = step_result
                ep_act.append(a)
                ep_rew.append(float(r))
                states = step.layer_states_new
                t += 1

            all_obs.append(ep_obs)
            all_actions.append(ep_act)
            all_rewards.append(ep_rew)
            all_logits.append(np.array(ep_logits))
            all_values.append(np.array(ep_vals))
            all_q_dist.append(np.array(ep_qd))
            all_attn_c1.append(np.array(ep_attn))
            all_state_mag.append(np.array(ep_smag))
            all_pc_pred.append(np.array(ep_pc_pred))
            all_pc_target.append(np.array(ep_pc_target))
            all_lengths.append(len(ep_act))
            all_change_times.append(env.change_time)
            all_correct.append(1 if sum(ep_rew) > 0 else 0)
            all_pressed_at.append(pressed_at if pressed_at is not None else -1)

    return {
        "obs": all_obs,
        "actions": all_actions,
        "rewards": all_rewards,
        "logits": all_logits,
        "values": all_values,
        "q_dist": all_q_dist,
        "attn_c1": all_attn_c1,
        "state_mag": all_state_mag,
        "pc_pred": all_pc_pred,
        "pc_target": all_pc_target,
        "lengths": all_lengths,
        "change_times": all_change_times,
        "correct": all_correct,
        "pressed_at": all_pressed_at,
    }


def report(rollouts: dict, n_episodes: int) -> None:
    print("\n" + "=" * 64)
    print(f"Diagnostic report — {n_episodes} rollouts")
    print("=" * 64)

    actions = rollouts["actions"]
    rewards = rollouts["rewards"]
    pressed_at = rollouts["pressed_at"]
    change_times = rollouts["change_times"]
    lengths = rollouts["lengths"]
    correct = rollouts["correct"]

    # ---- Behavioral summary ----
    mean_return = np.mean([sum(r) for r in rewards])
    mean_correct = np.mean(correct)
    n_pressed = sum(1 for p in pressed_at if p >= 0)
    n_terminated_naturally = sum(1 for L in lengths if L >= 29)

    print(f"\n[A] Behavior")
    print(f"    mean episodic return : {mean_return:.3f}  (oracle≈2.98, never-press≈1.47)")
    print(f"    correct rate         : {mean_correct:.3f}")
    print(f"    pressed at all       : {n_pressed:>3d} / {n_episodes:<3d}  ({100*n_pressed/n_episodes:.1f}%)")
    print(f"    timed-out (no press) : {n_terminated_naturally:>3d} / {n_episodes:<3d}")

    if n_pressed > 0:
        press_times = [p for p in pressed_at if p >= 0]
        change_at_press = [change_times[i] for i, p in enumerate(pressed_at) if p >= 0]
        print(f"    press time stats     : mean={np.mean(press_times):.2f}, median={np.median(press_times):.1f}, min={min(press_times)}, max={max(press_times)}")
        print(f"    change-time stats    : mean={np.mean(change_at_press):.2f}")

    # ---- Action distribution per timestep ----
    print(f"\n[B] Action distribution by timestep (counts of 'press' across episodes)")
    max_T = max(lengths)
    press_per_t = np.zeros(max_T)
    n_per_t = np.zeros(max_T)
    for ep in range(n_episodes):
        for t, a in enumerate(actions[ep]):
            n_per_t[t] += 1
            if a == 1:
                press_per_t[t] += 1
    press_rate_per_t = press_per_t / np.maximum(n_per_t, 1)
    # Print as histogram-style.
    bins = list(range(0, max_T, 2))
    for t in bins:
        bar = "#" * int(round(press_rate_per_t[t] * 40))
        print(f"    t={t:>2d}  press-rate={press_rate_per_t[t]:.3f}  {bar}")

    # ---- Policy entropy across the trial ----
    print(f"\n[C] Mean entropy across the trial")
    logits_all = []
    for ep in range(n_episodes):
        logits_all.append(rollouts["logits"][ep])
    max_T = max(L.shape[0] for L in logits_all)
    H_per_t = np.zeros(max_T)
    cnt_per_t = np.zeros(max_T)
    for L in logits_all:
        T = L.shape[0]
        # entropy of categorical from logits
        from torch.distributions import Categorical
        H = Categorical(logits=torch.from_numpy(L)).entropy().numpy()
        H_per_t[:T] += H
        cnt_per_t[:T] += 1
    H_per_t /= np.maximum(cnt_per_t, 1)
    print(f"    H at t=0     : {H_per_t[0]:.4f}")
    print(f"    H at t=5     : {H_per_t[min(5, max_T-1)]:.4f}")
    print(f"    H at t=15    : {H_per_t[min(15, max_T-1)]:.4f}")
    print(f"    H at t={max_T-1:<3d}    : {H_per_t[-1]:.4f}")
    print(f"    H_max (ln 2) : {np.log(2):.4f}")
    print(f"    H_min over trial: {H_per_t.min():.4f}")
    print(f"    H_max over trial: {H_per_t.max():.4f}")
    if H_per_t.max() < 0.05:
        print(f"    !!! Policy entropy is essentially zero — policy collapsed to deterministic action 0 (wait).")

    # ---- dQ analysis — does the critic ever distinguish actions? ----
    print(f"\n[D] Critic action-discrimination dQ = |Q(s,0) - Q(s,1)| per timestep")
    dQ_per_t = np.zeros(max_T)
    cnt_per_t = np.zeros(max_T)
    for ep in range(n_episodes):
        qd = rollouts["q_dist"][ep]  # (T, |A|, N)
        T = qd.shape[0]
        q_mean = qd.mean(axis=-1)  # (T, |A|)
        dq = np.abs(q_mean[:, 0] - q_mean[:, 1])  # (T,)
        dQ_per_t[:T] += dq
        cnt_per_t[:T] += 1
    dQ_per_t /= np.maximum(cnt_per_t, 1)
    print(f"    dQ at t=0    : {dQ_per_t[0]:.4f}")
    print(f"    dQ at t=5    : {dQ_per_t[min(5, max_T-1)]:.4f}")
    print(f"    dQ at t=15   : {dQ_per_t[min(15, max_T-1)]:.4f}")
    print(f"    dQ at t={max_T-1}    : {dQ_per_t[-1]:.4f}")
    print(f"    dQ_mean      : {dQ_per_t.mean():.4f}")
    print(f"    dQ_max       : {dQ_per_t.max():.4f}")
    if dQ_per_t.max() < 0.05:
        print(f"    !!! Critic does not discriminate actions anywhere — distributional advantage signal is dead.")

    # ---- Q(s, press) values — is press ever better than wait? ----
    print(f"\n[E] Mean Q(s, press) − Q(s, wait) per timestep (signed)")
    qdiff_per_t = np.zeros(max_T)
    cnt_per_t = np.zeros(max_T)
    for ep in range(n_episodes):
        qd = rollouts["q_dist"][ep]
        T = qd.shape[0]
        q_mean = qd.mean(axis=-1)  # (T, |A|)
        diff = q_mean[:, 1] - q_mean[:, 0]
        qdiff_per_t[:T] += diff
        cnt_per_t[:T] += 1
    qdiff_per_t /= np.maximum(cnt_per_t, 1)
    for t in [0, 5, 11, 15, 20, 25, 28]:
        if t < max_T:
            print(f"    t={t:>2d}: Q(press)−Q(wait) = {qdiff_per_t[t]:+.4f}")
    if qdiff_per_t.max() < 0:
        print(f"    !!! Q(press) is ALWAYS ≤ Q(wait). The model 'knows' wait is better at every t and will never press.")

    # ---- Attention map activity ----
    print(f"\n[F] Per-step attention-map sparsity (Gini coeff over C_1 attention)")
    attn = np.stack([a.mean(axis=0) for a in rollouts["attn_c1"][:1]])  # take ep 0
    # actually flatten across rollouts
    gini_per_t = np.zeros(max_T)
    cnt_per_t = np.zeros(max_T)
    for ep in range(n_episodes):
        att = rollouts["attn_c1"][ep]  # (T, N, N) where N = 144
        T = att.shape[0]
        for t in range(T):
            # Gini coefficient of the (mean-over-queries) attention map.
            a = att[t].mean(axis=0)
            a = np.sort(a)
            n = len(a)
            if a.sum() > 0:
                gini = (2 * (np.arange(1, n+1) * a).sum() / (n * a.sum()) - (n + 1) / n)
            else:
                gini = 0.0
            gini_per_t[t] += gini
            cnt_per_t[t] += 1
    gini_per_t /= np.maximum(cnt_per_t, 1)
    print(f"    Gini at t=0  : {gini_per_t[0]:.4f}   (0 = uniform, 1 = single-peak)")
    print(f"    Gini at t=15 : {gini_per_t[min(15, max_T-1)]:.4f}")
    print(f"    Gini at t={max_T-1}  : {gini_per_t[-1]:.4f}")
    print(f"    Gini mean    : {gini_per_t.mean():.4f}")
    if gini_per_t.mean() < 0.05:
        print(f"    !!! Attention is essentially uniform — FeedbackTransformer not differentiating tokens.")
    elif gini_per_t.mean() < 0.20:
        print(f"    Note: attention is mildly structured but not strongly focused.")

    # ---- Recurrent-state magnitudes ----
    print(f"\n[G] Per-layer hidden-state mean-absolute magnitudes (across trial)")
    smag = np.array([np.array(sm).mean(axis=0) for sm in rollouts["state_mag"]])  # (n_eps, 3)
    for i, name in enumerate(("C_1", "C_2", "C_3")):
        print(f"    {name} : mean={smag[:, i].mean():.4f}   std={smag[:, i].std():.4f}")
    if smag.mean() < 1e-3:
        print(f"    !!! Hidden states are essentially zero — recurrent dynamics aren't engaging.")

    # ---- PC loss per timestep ----
    print(f"\n[H] Per-timestep PC reconstruction MSE")
    pc_per_t = np.zeros(max_T)
    cnt_per_t = np.zeros(max_T)
    for ep in range(n_episodes):
        pred = rollouts["pc_pred"][ep]  # (T, 3, 50, 50)
        tgt = rollouts["pc_target"][ep]
        T = pred.shape[0]
        mse = ((pred - tgt) ** 2).mean(axis=(1, 2, 3))
        pc_per_t[:T] += mse
        cnt_per_t[:T] += 1
    pc_per_t /= np.maximum(cnt_per_t, 1)
    print(f"    L_PC at t=0   : {pc_per_t[0]:.4f}")
    print(f"    L_PC at t=5   : {pc_per_t[min(5, max_T-1)]:.4f}")
    print(f"    L_PC at t={max_T-1}  : {pc_per_t[-1]:.4f}")
    print(f"    L_PC mean     : {pc_per_t.mean():.4f}")

    print("\n" + "=" * 64)


def main():
    device = torch.device("mps" if (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()) else "cpu")
    ckpt = os.path.join(_PROJECT_ROOT, "HRA", "checkpoints", "hra_latest.pt")
    if not os.path.exists(ckpt):
        print(f"Checkpoint not found at {ckpt}")
        return 1

    model = load_model(ckpt, device)
    env = ChangeDetectionEnv()
    print("\n[diag] Collecting 64 rollouts with sampled actions (stochastic policy)...")
    rollouts = collect_rollouts(model, env, n_episodes=64, device=device)
    report(rollouts, n_episodes=64)

    # Also run a deterministic argmax policy for comparison.
    print("\n[diag] Sanity check: deterministic argmax policy reward over 32 episodes...")
    model.eval()
    returns_argmax = []
    pressed_argmax = 0
    with torch.no_grad():
        for _ in range(32):
            obs = env.reset()
            if isinstance(obs, tuple):
                obs = obs[0]
            states = model.init_states(1, device=device)
            done = False
            R = 0.0
            pressed = False
            while not done:
                x_t = torch.from_numpy(np.ascontiguousarray(np.asarray(obs, dtype=np.float32).transpose(2, 0, 1))).to(device).unsqueeze(0)
                step = model.forward_step(x_t, states)
                a = int(step.action_logits[0].argmax().item())
                if a == 1:
                    pressed = True
                step_result = env.step(a)
                if len(step_result) == 5:
                    obs, r, terminated, truncated, _ = step_result
                    done = bool(terminated or truncated)
                else:
                    obs, r, done, _ = step_result
                R += float(r)
                states = step.layer_states_new
            returns_argmax.append(R)
            if pressed:
                pressed_argmax += 1
    print(f"    argmax mean return : {np.mean(returns_argmax):.3f}")
    print(f"    argmax press count : {pressed_argmax}/32")
    return 0


if __name__ == "__main__":
    sys.exit(main())
