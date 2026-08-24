"""
Deep-dive diagnostic for a stuck HRA model.

When the headline metric is "never beat 50% accuracy" the question is *why*.
The model could be stuck for several distinct reasons:

  (1) Perception broken — hidden state doesn't change when the stimulus changes
      → can't possibly detect changes
  (2) Cue not encoded — hidden state at t > cue_offset doesn't depend on
      cue location → can't tell which patch is the target
  (3) Critic is confidently wrong — Q(press) < Q(wait) at every timestep,
      including the change-time → no advantage signal for pressing
  (4) Actor logits collapsed to deterministic-wait → no exploration of press
  (5) PPO update too weak (kl_early_stop / damped lr) → not enough learning
      per rollout to push out of the local minimum

This script tests each of these in turn against the saved checkpoint.

Run:
    /usr/bin/python3 HRA/analysis/deep_dive.py
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

from HRA.analysis._load import load_checkpoint, select_device
from HRA.env import ChangeDetectionEnv


def _obs_to_tensor(obs, device):
    arr = np.ascontiguousarray(np.asarray(obs, dtype=np.float32).transpose(2, 0, 1))
    return torch.from_numpy(arr).to(device).unsqueeze(0)


def run_one_trial(model, env, device, force_action=0, seed=None):
    """Run a single trial with action forced (default 0 = wait) and record
    everything per-timestep."""
    if seed is not None:
        env_seed = seed
        try:
            env.reset(seed=env_seed)
        except TypeError:
            np.random.seed(env_seed)
    obs = env.reset()
    if isinstance(obs, tuple):
        obs = obs[0]
    states = model.init_states(1, device=device)

    trial = {
        "frames": [],
        "C_1": [], "C_2": [], "C_3": [],
        "q_dist": [],
        "logits": [],
        "value": [],
        "attn_c1_final": [],
        "change_time": int(env.change_time),
        "cue_position": str(env.cue_position),
        "cue_color": str(env.cue_color),
    }

    done = False
    t = 0
    with torch.no_grad():
        while not done:
            trial["frames"].append(np.asarray(obs, dtype=np.float32).copy())
            x = _obs_to_tensor(obs, device)
            step = model.forward_step(x, states)

            trial["C_1"].append(step.layer_states_new[0][0].cpu().numpy())
            trial["C_2"].append(step.layer_states_new[1][0].cpu().numpy())
            trial["C_3"].append(step.layer_states_new[2][0].cpu().numpy())
            trial["q_dist"].append(step.q_dist[0].cpu().numpy())
            trial["logits"].append(step.action_logits[0].cpu().numpy())
            trial["value"].append(float(step.value[0].item()))
            # Final iteration's C_1 attention map (mean over heads, mean over queries).
            a = step.attn_per_layer[-1][0][0]  # (n_heads, N, N)
            a = a.mean(dim=0).mean(dim=0).cpu().numpy().reshape(12, 12)
            trial["attn_c1_final"].append(a)

            states = step.layer_states_new
            step_result = env.step(int(force_action))
            if len(step_result) == 5:
                obs, r, terminated, truncated, _ = step_result
                done = bool(terminated or truncated)
            else:
                obs, r, done, _ = step_result
            t += 1
    return trial


def hidden_state_change_at_change_time(model, env, device, n_trials=10):
    """
    Test (1): does the hidden state change when the stimulus changes?

    Compares the cosine distance of C_t pre-change vs post-change to the
    same distance for an arbitrary pair of pre-change timesteps. If they're
    the same, perception is *not* responsive to the change.
    """
    print("\n[1] Perception test — does C_t change at change_time?")
    pre_change_dists = []
    cross_change_dists = []
    for trial_i in range(n_trials):
        trial = run_one_trial(model, env, device, force_action=0, seed=100 + trial_i)
        ct = trial["change_time"]
        if ct < 4 or ct >= 27:
            continue  # need 3 frames pre and 2 post for the comparison

        # Use C_1 (closest to perception).
        states = np.stack(trial["C_1"])  # (T, c1, 12, 12)
        flat = states.reshape(states.shape[0], -1)

        def cos(a, b):
            return float((a * b).sum() / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))

        # Pre-change comparison: t=ct-3 vs t=ct-1 (3 frames apart, both pre-change).
        pre_change_dists.append(1.0 - cos(flat[ct - 3], flat[ct - 1]))
        # Cross-change comparison: t=ct-1 vs t=ct+1 (3 frames apart, straddling change).
        cross_change_dists.append(1.0 - cos(flat[ct - 1], flat[ct + 1]))

    if not pre_change_dists:
        print("  could not collect any valid trials")
        return
    p_mean = float(np.mean(pre_change_dists))
    c_mean = float(np.mean(cross_change_dists))
    p_std = float(np.std(pre_change_dists))
    c_std = float(np.std(cross_change_dists))
    print(f"  pre-change Δ (3 frames apart, both pre): mean={p_mean:.6f}  std={p_std:.6f}")
    print(f"  cross-change Δ (3 frames apart, around change): mean={c_mean:.6f}  std={c_std:.6f}")
    print(f"  ratio cross / pre = {c_mean / max(p_mean, 1e-12):.3f}")
    if c_mean > 2 * p_mean:
        print(f"  ✓ Perception responds to changes (ratio > 2)")
    elif c_mean > 1.2 * p_mean:
        print(f"  ~ Perception responds weakly (ratio 1.2-2.0)")
    else:
        print(f"  ✗ Perception does NOT differentially respond to the change (ratio ≤ 1.2)")
        print(f"     ⇒ This is the root cause. Even infinite RL training won't help.")


def cue_encoding_test(model, env, device, n_trials=24):
    """
    Test (2): does the hidden state encode the cue position?

    Runs trials with each cue position; checks whether hidden state at t = 10
    (well after cue but before change) separates by cue position. If a linear
    decoder can do this, perception encodes the cue.
    """
    print("\n[2] Cue encoding test — does C_t at t=10 separate by cue position?")
    cue_positions = []
    states_at_t10 = []
    for trial_i in range(n_trials):
        trial = run_one_trial(model, env, device, force_action=0, seed=200 + trial_i)
        if len(trial["C_1"]) < 11:
            continue
        cue_positions.append(trial["cue_position"])
        states_at_t10.append(trial["C_1"][10].flatten())

    if not states_at_t10:
        print("  could not collect any valid trials")
        return
    states_at_t10 = np.stack(states_at_t10)
    cue_positions = np.array(cue_positions)
    print(f"  cue position counts: {dict(zip(*np.unique(cue_positions, return_counts=True)))}")
    print(f"  state vec dim: {states_at_t10.shape[1]}")

    # Class separation: for each unique cue position, compare within-class to
    # cross-class mean distance.
    unique = np.unique(cue_positions)
    within = []
    cross = []
    for i in range(len(states_at_t10)):
        for j in range(i + 1, len(states_at_t10)):
            d = float(np.linalg.norm(states_at_t10[i] - states_at_t10[j]))
            if cue_positions[i] == cue_positions[j]:
                within.append(d)
            else:
                cross.append(d)
    if not within or not cross:
        print("  insufficient pairs")
        return
    print(f"  within-cue-class mean distance: {np.mean(within):.4f}  std={np.std(within):.4f}")
    print(f"  cross-cue-class mean distance:  {np.mean(cross):.4f}  std={np.std(cross):.4f}")
    print(f"  ratio cross / within = {np.mean(cross) / max(np.mean(within), 1e-12):.3f}")
    if np.mean(cross) > 1.3 * np.mean(within):
        print(f"  ✓ Hidden state encodes cue position")
    elif np.mean(cross) > 1.05 * np.mean(within):
        print(f"  ~ Hidden state weakly encodes cue position")
    else:
        print(f"  ✗ Hidden state does NOT encode cue position")


def q_dynamics_at_change_time(model, env, device, n_trials=20):
    """
    Test (3): does Q-distribution change around the change_time?

    A working critic should learn: Q(press, t = change_time) is HIGH (positive
    reward expected on press), Q(press, other t) is LOW (press is premature).
    A broken critic learns Q(press) is uniformly low everywhere.
    """
    print("\n[3] Critic test — does Q(press) peak at change_time?")
    q_press_pre = []
    q_press_at = []
    q_press_post = []
    q_wait_pre = []
    q_wait_at = []
    q_wait_post = []
    for trial_i in range(n_trials):
        trial = run_one_trial(model, env, device, force_action=0, seed=300 + trial_i)
        ct = trial["change_time"]
        if ct < 5 or ct >= len(trial["q_dist"]) - 2:
            continue
        q = np.stack(trial["q_dist"])  # (T, |A|, N)
        q_mean = q.mean(axis=-1)        # (T, |A|)
        # Average over 3-step windows.
        q_wait_pre.append(q_mean[ct - 4:ct - 1, 0].mean())
        q_press_pre.append(q_mean[ct - 4:ct - 1, 1].mean())
        q_wait_at.append(q_mean[ct, 0])
        q_press_at.append(q_mean[ct, 1])
        q_wait_post.append(q_mean[ct + 1:ct + 3, 0].mean())
        q_press_post.append(q_mean[ct + 1:ct + 3, 1].mean())

    if not q_press_at:
        print("  no valid trials")
        return
    print(f"  Q(press)  pre-change={np.mean(q_press_pre):+.4f}  AT change={np.mean(q_press_at):+.4f}  post-change={np.mean(q_press_post):+.4f}")
    print(f"  Q(wait)   pre-change={np.mean(q_wait_pre):+.4f}   AT change={np.mean(q_wait_at):+.4f}   post-change={np.mean(q_wait_post):+.4f}")
    print(f"  Δ Q(press) - Q(wait)  pre={np.mean(q_press_pre) - np.mean(q_wait_pre):+.4f}  "
          f"AT={np.mean(q_press_at) - np.mean(q_wait_at):+.4f}  post={np.mean(q_press_post) - np.mean(q_wait_post):+.4f}")
    rise_at_change = np.mean(q_press_at) - np.mean(q_press_pre)
    if rise_at_change > 0.05:
        print(f"  ✓ Q(press) DOES rise at change_time by {rise_at_change:+.3f}")
    elif rise_at_change > -0.02:
        print(f"  ~ Q(press) barely changes at change_time ({rise_at_change:+.3f})")
    else:
        print(f"  ✗ Q(press) does NOT respond to the change ({rise_at_change:+.3f})")
        print(f"     ⇒ Even with perfect perception, the critic can't tell the actor when to press.")


def attention_at_change_time(model, env, device, n_trials=12):
    """
    Test (4): does the attention map shift when the stimulus changes?

    If perception is responsive to the change AND attention is doing
    something, the attention map should re-organise at change_time.
    """
    print("\n[4] Attention dynamics test — does attention shift at change_time?")
    pre_change_attn = []
    cross_change_attn = []
    for trial_i in range(n_trials):
        trial = run_one_trial(model, env, device, force_action=0, seed=400 + trial_i)
        ct = trial["change_time"]
        if ct < 4 or ct >= len(trial["attn_c1_final"]) - 2:
            continue
        attns = np.stack(trial["attn_c1_final"])  # (T, 12, 12)

        def cos(a, b):
            a, b = a.flatten(), b.flatten()
            return float((a * b).sum() / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))

        pre_change_attn.append(1.0 - cos(attns[ct - 3], attns[ct - 1]))
        cross_change_attn.append(1.0 - cos(attns[ct - 1], attns[ct + 1]))

    if not pre_change_attn:
        print("  no valid trials")
        return
    p = float(np.mean(pre_change_attn))
    c = float(np.mean(cross_change_attn))
    print(f"  pre-change attention Δ  (cos-dist over 3-frame window): {p:.6f}")
    print(f"  cross-change attention Δ:                                {c:.6f}")
    print(f"  ratio = {c / max(p, 1e-12):.3f}")
    if c > 2 * p:
        print(f"  ✓ Attention responds to the change")
    elif c > 1.2 * p:
        print(f"  ~ Attention weakly responds")
    else:
        print(f"  ✗ Attention does NOT respond to the change")


def policy_decisiveness_test(model, env, device, n_trials=64):
    """
    Test (5): how decisive is the policy at change_time?

    Even if the model can't press correctly, if entropy spikes at the right
    time, the model "knows" something. If entropy is flat across the trial,
    the policy is task-blind.
    """
    print("\n[5] Policy decisiveness test — does entropy / Δlogit shift at change_time?")
    H_per_t = np.zeros(29)
    dlogit_per_t = np.zeros(29)
    n_per_t = np.zeros(29)
    cts = []
    for trial_i in range(n_trials):
        trial = run_one_trial(model, env, device, force_action=0, seed=500 + trial_i)
        ct = trial["change_time"]
        cts.append(ct)
        logits = np.stack(trial["logits"])  # (T, 2)
        from torch.distributions import Categorical
        H = Categorical(logits=torch.from_numpy(logits)).entropy().numpy()
        dlogit = logits[:, 0] - logits[:, 1]  # wait - press
        T = len(H)
        H_per_t[:T] += H
        dlogit_per_t[:T] += dlogit
        n_per_t[:T] += 1
    H_per_t /= np.maximum(n_per_t, 1)
    dlogit_per_t /= np.maximum(n_per_t, 1)
    print(f"  Entropy  at t=0 .. t=10 .. t=15 .. t=20 .. t=28: "
          f"{H_per_t[0]:.4f}  {H_per_t[10]:.4f}  {H_per_t[15]:.4f}  {H_per_t[20]:.4f}  {H_per_t[28]:.4f}")
    print(f"  Δlogit   at t=0 .. t=10 .. t=15 .. t=20 .. t=28: "
          f"{dlogit_per_t[0]:.2f}  {dlogit_per_t[10]:.2f}  {dlogit_per_t[15]:.2f}  {dlogit_per_t[20]:.2f}  {dlogit_per_t[28]:.2f}")
    H_var = np.std(H_per_t[3:28])
    print(f"  Entropy std across the trial: {H_var:.6f}")
    if H_var > 0.01:
        print(f"  ✓ Policy has timestep-dependent entropy structure")
    elif H_var > 0.001:
        print(f"  ~ Policy has tiny timestep variation")
    else:
        print(f"  ✗ Policy entropy is flat across the trial — task-blind")


def main():
    device = select_device()
    ckpt = os.path.join(_PROJECT_ROOT, "HRA", "checkpoints", "hra_latest.pt")
    print(f"[load] {ckpt}")
    model, kw, it = load_checkpoint(ckpt, device)
    print(f"[load] iter={it}  cross_layer_via={kw['cross_layer_via']}  device={device}")
    print(f"[load] n_params={sum(p.numel() for p in model.parameters() if p.requires_grad):,}")

    env = ChangeDetectionEnv()
    hidden_state_change_at_change_time(model, env, device, n_trials=12)
    cue_encoding_test(model, env, device, n_trials=32)
    q_dynamics_at_change_time(model, env, device, n_trials=24)
    attention_at_change_time(model, env, device, n_trials=16)
    policy_decisiveness_test(model, env, device, n_trials=64)


if __name__ == "__main__":
    main()
