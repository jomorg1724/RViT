"""
Visualise the two distinct attention signals in the RViT+ encoder, on a
fresh rollout from the latest trained checkpoint.

The encoder's attention block produces (per layer, per frame):

  1. **Channel-attention softmax** `A ∈ (B, C, 1, 1)` — one scalar per
     channel per head; a per-head softmax distribution over channels.
  2. **Spatial attention residual** `A · V ∈ (B, C, H, W)` — the actual
     tensor added to Z in the first residual. Empirically the
     "look-here" map, since V carries spatial structure.
  3. **Z↔H fusion gates** `g_q, g_k, g_v ∈ (B, C, H, W)` — sigmoid maps
     mediating how the recurrent / cross-layer feedback enters Q, K, V.
  4. **Cell update gate** `u ∈ (B, C, H, W)` — per-(channel, position)
     write strength under the LSTM-style mix.

This script:
  - Loads the latest RL checkpoint (`rvit_plus_rl_latest.pt`).
  - Rolls out one episode in `ChangeDetectionEnv` with greedy actions.
  - Records, per frame, the actor/critic logits and full encoder attn
    diagnostics.
  - Saves a multi-panel figure per layer (default: figures/attn_layer{1,2,3}.png):
        rows  = frames (subsample for readability)
        cols  = input | per-head channel softmax | spatial residual norm
                | Z↔H V-gate magnitude | update-gate magnitude
  - Saves a summary CSV with per-frame scalar diagnostics.

Run:
    .venv/bin/python RViT_plus/analysis/attention_maps_rl.py \
        --checkpoint RViT_plus/checkpoints/rvit_plus_rl_latest.pt \
        --out-dir RViT_plus/analysis/figures \
        --device cpu
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v2.env import ChangeDetectionEnv
from RViT_plus_v2.model import RViTPlusModel


# ─────────────────────────────────────────────────────────────────────────────
# Rollout
# ─────────────────────────────────────────────────────────────────────────────


def rollout_one_episode(
    model: RViTPlusModel,
    env: ChangeDetectionEnv,
    *,
    device: torch.device,
    greedy: bool = True,
    seed: Optional[int] = None,
) -> dict:
    """Roll one episode and capture per-frame attention diagnostics.

    Returns a dict with:
        observations         : (T, 3, 50, 50) float32 — input frames
        actions              : (T,) long  — executed actions
        rewards              : (T,) float — env rewards
        attn_per_frame       : list of [[L1, L2, L3]] per frame — channel softmax
        attn_spatial_per_frame : list of [[L1, L2, L3]] per frame — spatial residuals
        gates_per_frame      : list of [{q, k, v}] per frame — Z↔H gates
        state_per_frame      : list of [[C₁, C₂, C₃]] per frame
        change_step          : int — when the change event happened in the env
        press_step           : int or None — when the actor pressed (if at all)
        episode_len          : int
    """
    if seed is not None:
        torch.manual_seed(seed)
        np.random.seed(seed)
    model.eval()
    obs = env.reset()
    if isinstance(obs, tuple):  # gym-style (obs, info)
        obs = obs[0]
    states = model.init_states(1, device=device)
    c3_spec = model.encoder.init_c3_specialists(1, device=device)

    obs_list: List[torch.Tensor] = []
    actions: List[int] = []
    rewards: List[float] = []
    attn_pf: List = []
    attn_sp_pf: List = []
    gates_pf: List = []
    states_pf: List = []
    change_step = -1
    press_step: Optional[int] = None

    done = False
    t = 0
    with torch.no_grad():
        while not done and t < env.T:
            x = torch.from_numpy(obs).float().to(device)
            if x.dim() == 3 and x.shape[-1] == 3:                    # (H, W, 3) → (3, H, W)
                x = x.permute(2, 0, 1).contiguous()
            x_step = x.unsqueeze(0)                                  # (1, 3, H, W)
            V = model.stem(x_step)
            enc_out = model.encoder.forward_step(
                V, states,
                prev_c3_specialists=c3_spec if model.split_c3 else None,
            )
            states = enc_out["layer_states_new"]
            c3_spec = enc_out["c3_specialists_new"]
            obs_list.append(x.cpu())
            attn_pf.append(enc_out["attn_per_iter"])
            attn_sp_pf.append(enc_out.get("attn_spatial_per_iter", []))
            gates_pf.append(enc_out.get("gates_per_iter", []))
            states_pf.append(enc_out["state_per_iter"])

            # Compute action under current actor + critic.
            if model.split_c3:
                C1, C2, _ = states
                states_for_actor = (C1, C2, c3_spec["actor"])
                states_for_critic = (C1, C2, c3_spec["critic"])
            else:
                states_for_actor = states_for_critic = states
            actor_logits = model.actor_head(states_for_actor)        # (1, 2)
            q_dist = model.critic_head(states_for_critic)            # (1, 2, N)
            if greedy:
                a = int(actor_logits.argmax(dim=-1).item())
            else:
                probs = torch.softmax(actor_logits, dim=-1)
                a = int(torch.multinomial(probs, 1).item())

            # Step env.
            step_out = env.step(a)
            if len(step_out) == 5:
                obs, r, terminated, truncated, info = step_out
                done = bool(terminated or truncated)
            else:
                obs, r, done, info = step_out
            actions.append(a)
            rewards.append(float(r))
            if a == 1 and press_step is None:
                press_step = t
            t += 1
        # The env stores its change time as `change_time` (when the Gabor flips).
        # Convert from env step (1-indexed in env.t) to our 0-indexed frame.
        change_step = int(getattr(env, "change_time", -1)) - 1

    return {
        "observations":          torch.stack(obs_list, dim=0),
        "actions":               torch.tensor(actions, dtype=torch.long),
        "rewards":               torch.tensor(rewards, dtype=torch.float32),
        "attn_per_frame":        attn_pf,
        "attn_spatial_per_frame": attn_sp_pf,
        "gates_per_frame":       gates_pf,
        "state_per_frame":       states_pf,
        "change_step":           change_step,
        "press_step":            press_step,
        "episode_len":           t,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Plotting helpers
# ─────────────────────────────────────────────────────────────────────────────


def _to_numpy(t: torch.Tensor) -> np.ndarray:
    return t.detach().cpu().numpy()


def _channel_norm(spatial: torch.Tensor) -> np.ndarray:
    """(C, H, W) → (H, W) — root-mean-square across channels.
    Use as a generic "where is attention firing" projection."""
    return _to_numpy((spatial.pow(2).mean(dim=0) + 1e-8).sqrt())


def _channel_max(spatial: torch.Tensor) -> np.ndarray:
    """(C, H, W) → (H, W) — max across channels.
    Captures the single strongest channel response per position."""
    return _to_numpy(spatial.abs().amax(dim=0))


def _channel_softmax_heatmap(A_flat: torch.Tensor, n_heads: int) -> np.ndarray:
    """(C, 1, 1) → (n_heads, d_head) — per-head channel softmax distribution."""
    C = A_flat.numel()
    return _to_numpy(A_flat.reshape(n_heads, C // n_heads))


def plot_layer_attention(
    rollout: dict,
    layer_idx: int,
    *,
    out_path: str,
    n_heads: int = 4,
    frame_stride: int = 3,
):
    """Save a multi-panel figure showing the two attention signals (and the
    Z↔H V-gate + update-gate) for one encoder layer across the episode.

    Columns per row (one row = one frame):
        col 0 : input frame (RGB)
        col 1 : per-head channel softmax (n_heads × d_head heatmap)
        col 2 : spatial attention residual norm (H_ℓ × W_ℓ)
        col 3 : V-gate magnitude (H_ℓ × W_ℓ) — mean over channels
        col 4 : update-gate magnitude (H_ℓ × W_ℓ) — mean over channels
                (taken from state_per_frame — strictly the cell's u_gate
                 is not in state_per_frame; we use the spatial-norm of the
                 state delta as a proxy)
    """
    import matplotlib.pyplot as plt
    from matplotlib import gridspec

    T = rollout["episode_len"]
    rows = list(range(0, T, frame_stride))
    if rows[-1] != T - 1:
        rows.append(T - 1)

    fig = plt.figure(figsize=(15, 2.4 * len(rows)))
    gs = gridspec.GridSpec(len(rows), 5, wspace=0.25, hspace=0.4)

    for r, t in enumerate(rows):
        # Column 0: input frame (normalised to [0, 1] for display).
        ax = fig.add_subplot(gs[r, 0])
        frame = _to_numpy(rollout["observations"][t])
        if frame.shape[0] == 3:
            frame = frame.transpose(1, 2, 0)
        f_min, f_max = float(frame.min()), float(frame.max())
        if f_max > f_min:
            frame = (frame - f_min) / (f_max - f_min)
        ax.imshow(frame, vmin=0, vmax=1)
        ax.set_title(f"t={t}", fontsize=9)
        if t == rollout["change_step"]:
            ax.set_title(f"t={t} CHANGE", fontsize=9, color="orange")
        if t == rollout["press_step"]:
            ax.set_title(f"t={t} PRESS", fontsize=9, color="red")
        ax.axis("off")

        # Column 1: per-head channel softmax.
        ax = fig.add_subplot(gs[r, 1])
        A_flat = rollout["attn_per_frame"][t][0][layer_idx].squeeze(0)   # (C, 1, 1)
        heat = _channel_softmax_heatmap(A_flat, n_heads)
        im = ax.imshow(heat, aspect="auto", cmap="viridis")
        ax.set_xlabel("channel index within head")
        ax.set_ylabel("head")
        ax.set_title("channel softmax A", fontsize=9)
        plt.colorbar(im, ax=ax, fraction=0.04)

        # Column 2: spatial attention residual (channel RMS).
        ax = fig.add_subplot(gs[r, 2])
        spatial = rollout["attn_spatial_per_frame"][t][0][layer_idx].squeeze(0)  # (C, H, W)
        spatial_map = _channel_norm(spatial)
        im = ax.imshow(spatial_map, cmap="hot")
        ax.set_title("spatial attn (A·V) RMS over C", fontsize=9)
        plt.colorbar(im, ax=ax, fraction=0.04)
        ax.axis("off")

        # Column 3: V-gate magnitude (mean over channels), if present.
        ax = fig.add_subplot(gs[r, 3])
        v_gate = rollout["gates_per_frame"][t][0]["v"][layer_idx]        # may be None
        if v_gate is not None:
            v_gate_map = _channel_norm(v_gate.squeeze(0))
            im = ax.imshow(v_gate_map, cmap="cividis")
            ax.set_title("V-gate magnitude", fontsize=9)
            plt.colorbar(im, ax=ax, fraction=0.04)
        else:
            ax.text(0.5, 0.5, "no V-gate\n(no feedback)", ha="center", va="center", fontsize=9)
            ax.set_xticks([]); ax.set_yticks([])
        ax.axis("off")

        # Column 4: state magnitude (post-step C_ℓ channel RMS).
        ax = fig.add_subplot(gs[r, 4])
        state = rollout["state_per_frame"][t][0][layer_idx].squeeze(0)
        state_map = _channel_norm(state)
        im = ax.imshow(state_map, cmap="magma")
        ax.set_title(f"|C_{layer_idx+1}| RMS over C", fontsize=9)
        plt.colorbar(im, ax=ax, fraction=0.04)
        ax.axis("off")

    fig.suptitle(
        f"Layer {layer_idx+1} attention signals — episode (change@{rollout['change_step']}, "
        f"press@{rollout['press_step']})",
        fontsize=11, y=1.001,
    )
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {out_path}")


def write_summary_csv(rollout: dict, out_path: str):
    """Per-frame scalar summary: action, reward, change/press markers, and
    per-layer spatial-attention RMS magnitude + softmax entropy."""
    import csv
    T = rollout["episode_len"]
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "action", "reward", "is_change", "is_press",
                    "spatial_rms_L1", "spatial_rms_L2", "spatial_rms_L3",
                    "softmax_entropy_L1", "softmax_entropy_L2", "softmax_entropy_L3"])
        for t in range(T):
            a = int(rollout["actions"][t].item())
            r = float(rollout["rewards"][t].item())
            row = [t, a, r,
                   int(t == rollout["change_step"]),
                   int(t == rollout["press_step"])]
            for L in range(3):
                spatial = rollout["attn_spatial_per_frame"][t][0][L].squeeze(0)
                rms = float((spatial.pow(2).mean()).sqrt().item())
                A_flat = rollout["attn_per_frame"][t][0][L].squeeze(0)
                # Per-head softmax entropy, averaged over heads.
                n_heads = 4
                C = A_flat.numel()
                A = A_flat.reshape(n_heads, C // n_heads).clamp(min=1e-12)
                ent = float((-A * A.log()).sum(dim=-1).mean().item())
                row.append(rms); row.append(ent if L < 0 else ent)
            # row currently has 6 numbers; need to interleave RMS then entropy
            # rebuild properly:
            row = [t, a, r,
                   int(t == rollout["change_step"]),
                   int(t == rollout["press_step"])]
            for L in range(3):
                spatial = rollout["attn_spatial_per_frame"][t][0][L].squeeze(0)
                rms = float((spatial.pow(2).mean()).sqrt().item())
                row.append(rms)
            for L in range(3):
                A_flat = rollout["attn_per_frame"][t][0][L].squeeze(0)
                n_heads = 4
                C = A_flat.numel()
                A = A_flat.reshape(n_heads, C // n_heads).clamp(min=1e-12)
                ent = float((-A * A.log()).sum(dim=-1).mean().item())
                row.append(ent)
            w.writerow(row)
    print(f"[saved] {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default="RViT_plus/checkpoints/rvit_plus_rl_latest.pt")
    ap.add_argument("--out-dir",    default="RViT_plus/analysis/figures")
    ap.add_argument("--device",     default="cpu")
    ap.add_argument("--seed",       type=int, default=0)
    ap.add_argument("--frame-stride", type=int, default=3,
                    help="Plot every Nth frame to keep the figure readable.")
    ap.add_argument("--n-episodes", type=int, default=1)
    args = ap.parse_args(argv)

    device = torch.device(args.device)
    os.makedirs(args.out_dir, exist_ok=True)

    # Load checkpoint.
    ckpt = torch.load(args.checkpoint, map_location=device, weights_only=False)
    if "model_kwargs" in ckpt:
        kwargs = ckpt["model_kwargs"]
    else:
        # Best-effort defaults matching the config.
        kwargs = dict(
            in_channels=3, image_h=50, image_w=50,
            stem_out_channels=64, state_channels=(64, 96, 128),
            n_FR=4, n_heads=4, seq_len=29,
            upsample_out_channels=32, cnn_hidden=64,
            enable_skips=True, skip_scale=0.3,
            enable_actor=True, enable_critic=True,
            n_actions=2, n_quantiles=51,
            split_c3=True,
        )
    model = RViTPlusModel(**kwargs).to(device)
    model.load_state_dict(ckpt["model_state_dict"], strict=False)
    model.eval()
    print(f"[loaded] {args.checkpoint} (iter={ckpt.get('iter', '?')})")

    env = ChangeDetectionEnv()

    for ep in range(args.n_episodes):
        rollout = rollout_one_episode(
            model, env, device=device, greedy=True, seed=args.seed + ep,
        )
        tag = f"ep{ep:02d}"
        for L in range(3):
            plot_layer_attention(
                rollout, layer_idx=L,
                out_path=os.path.join(args.out_dir, f"attn_{tag}_layer{L+1}.png"),
                frame_stride=args.frame_stride,
            )
        write_summary_csv(
            rollout, os.path.join(args.out_dir, f"summary_{tag}.csv"),
        )
        print(
            f"[ep {ep}] len={rollout['episode_len']}  "
            f"change@{rollout['change_step']}  press@{rollout['press_step']}  "
            f"return={rollout['rewards'].sum().item():.3f}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
