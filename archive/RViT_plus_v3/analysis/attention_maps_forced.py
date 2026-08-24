"""
Forced-trial attention analysis on the RViT+ V2 model.

V2 SPECIFIC: V2's attention block produces per-channel spatial saliency maps
(softmax over the H·W grid per channel), so `attn_per_iter[L]` has shape
(B, C, H, W) instead of V1's (B, C, 1, 1). This script visualizes the
attention maps directly as spatial saliencies per channel — each row is
one timestep, and each "channel" column shows the (H, W) softmax map for
that channel.

We pin the ChangeDetectionEnv to a specific deterministic configuration:

    cue_position = 'left'        # top-left
    cue_color    = 'red'         # 5-point reward when correct
    proportion   = 1.0           # full ring = high-validity cue
    change_true  = 1             # change WILL happen
    change_index = 0             # change is in the cued (top-left) gabor
    change_time  = <fixed>       # specified via --change-step

Then we roll the trained V2 model on this single trial and produce, per
encoder layer, a figure showing every timestep's attention signals.

For each layer we plot the SELECTED channels — i.e. the channels with the
most focused (peakiest) spatial softmax. Each such channel of A is a (H, W)
saliency tensor; we show it next to (a) the raw input, (b) the combined
spatial residual `A · V` RMS over channels, (c) the recurrent state
`C_ℓ` RMS.

The cued / changed quadrant is the TOP-LEFT 25×25 region of every input.
The first timestep with the change is `change_step` (0-indexed, equal to
`env.change_time - 1`).

Outputs (in --out-dir):
    attn_forced_layer{1,2,3}.png            — main figure per layer
    attn_forced_layer3_actor.png            — actor specialist (cell3_actor)
    attn_forced_layer3_critic.png           — critic specialist (cell3_critic)
    attn_forced_summary.csv                 — per-frame scalar diagnostics
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional, Tuple

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v3.env import ChangeDetectionEnv
from RViT_plus_v3.model import RViTPlusModel


# ─────────────────────────────────────────────────────────────────────────────
# Forced env wrapper
# ─────────────────────────────────────────────────────────────────────────────


def make_forced_env(
    *,
    change_time: int,
    cue_position: str = "left",
    cue_color: str = "red",
    proportion: float = 1.0,
    change_index: int = 0,
    change_true: int = 1,
    orientation_change: float = 64.0,
    seed: int = 0,
) -> ChangeDetectionEnv:
    """Return an env where the next reset() will deterministically produce
    the specified trial configuration.

    We monkey-patch reset() so that the sampling steps are skipped and the
    instance fields are overwritten with the fixed values immediately after
    the base reset has run.
    """
    np.random.seed(seed)
    env = ChangeDetectionEnv()
    base_reset = env.reset

    def fixed_reset():
        out = base_reset()
        # Override the random fields with the fixed trial config.
        env.change_time       = int(change_time)
        env.change_true       = int(change_true)
        env.cue_position      = str(cue_position)
        env.cue_color         = str(cue_color)
        env.proportion        = float(proportion)
        env.change_index      = int(change_index)
        env.orientation_change = float(orientation_change)
        env.t = 0
        # Regenerate observation at t=0 with the new config (the very first
        # _next_observation is "black" anyway, so this is a no-op for t=0).
        return env._next_observation()

    env.reset = fixed_reset
    return env


# ─────────────────────────────────────────────────────────────────────────────
# Rollout
# ─────────────────────────────────────────────────────────────────────────────


def rollout(model: RViTPlusModel, env: ChangeDetectionEnv, device: torch.device) -> dict:
    model.eval()
    obs = env.reset()
    if isinstance(obs, tuple):
        obs = obs[0]
    states = model.init_states(1, device=device)
    c3_spec = model.encoder.init_c3_specialists(1, device=device)

    obs_list, actions, rewards = [], [], []
    attn_pf, attn_sp_pf, specs_pf = [], [], []
    states_pf = []
    press_step: Optional[int] = None

    done = False
    t = 0
    with torch.no_grad():
        while not done and t < env.T:
            x = torch.from_numpy(np.asarray(obs, dtype=np.float32)).to(device)
            if x.dim() == 3 and x.shape[-1] == 3:
                x = x.permute(2, 0, 1).contiguous()
            x_step = x.unsqueeze(0)
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
            specs_pf.append(enc_out.get("attn_specialists_per_iter", []))
            states_pf.append(enc_out["state_per_iter"])

            if model.split_c3:
                C1, C2, _ = states
                states_for_actor  = (C1, C2, c3_spec["actor"])
            else:
                states_for_actor = states
            actor_logits = model.actor_head(states_for_actor)
            a = int(actor_logits.argmax(dim=-1).item())
            step_out = env.step(a)
            obs, r, done = step_out[0], step_out[1], step_out[2]
            actions.append(a)
            rewards.append(float(r))
            if a == 1 and press_step is None:
                press_step = t
            t += 1

    return {
        "observations":          torch.stack(obs_list, dim=0),
        "actions":               torch.tensor(actions, dtype=torch.long),
        "rewards":               torch.tensor(rewards, dtype=torch.float32),
        "attn_per_frame":        attn_pf,
        "attn_spatial_per_frame": attn_sp_pf,
        "specialists_per_frame": specs_pf,
        "state_per_frame":       states_pf,
        "change_step":           int(env.change_time) - 1,
        "press_step":            press_step,
        "episode_len":           t,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Plotting
# ─────────────────────────────────────────────────────────────────────────────


def _to_numpy(t: torch.Tensor) -> np.ndarray:
    return t.detach().cpu().numpy()


def _normalize_for_imshow(a: np.ndarray) -> np.ndarray:
    a = a.astype(np.float32)
    a_min, a_max = float(a.min()), float(a.max())
    if a_max > a_min:
        return (a - a_min) / (a_max - a_min)
    return np.zeros_like(a)


def _channel_rms(spatial: torch.Tensor) -> np.ndarray:
    return _to_numpy((spatial.pow(2).mean(dim=0) + 1e-8).sqrt())


def _spatial_entropy_per_channel(A: torch.Tensor) -> torch.Tensor:
    """Compute spatial softmax entropy per channel for V2's A ∈ (C, H, W).
    Returns a tensor of shape (C,) with entropy in nats."""
    C, H, W = A.shape
    A_flat = A.reshape(C, H * W).clamp(min=1e-12)
    # Renormalize defensively (A should already sum to 1 over (H,W) per channel)
    A_flat = A_flat / A_flat.sum(dim=-1, keepdim=True)
    ent = -(A_flat * A_flat.log()).sum(dim=-1)   # (C,)
    return ent


def _topk_channels_per_head_v2(
    A: torch.Tensor, n_heads: int, topk: int = 1
) -> Tuple[List[int], List[float]]:
    """V2 channel selection: split C channels into `n_heads` contiguous
    groups, then within each group pick the top-`topk` channels by FOCUS
    (= max(A[c]) across spatial positions — peakiest attention map).

    Returns (channel indices, focus values).
    """
    C, H, W = A.shape
    if C % n_heads != 0:
        # Fall back to ungrouped top-k.
        focus = A.reshape(C, -1).max(dim=-1).values
        idx = torch.topk(focus, topk * n_heads).indices.tolist()
        return idx, [float(focus[i]) for i in idx]
    d_head = C // n_heads
    focus = A.reshape(C, -1).max(dim=-1).values  # (C,)
    chosen: List[int] = []
    vals: List[float] = []
    for h in range(n_heads):
        block = focus[h * d_head:(h + 1) * d_head]
        idx_in_head = torch.topk(block, topk).indices.tolist()
        for i in idx_in_head:
            c = h * d_head + i
            chosen.append(c)
            vals.append(float(focus[c]))
    return chosen, vals


def plot_layer_full_episode(
    rollout: dict,
    layer_idx: int,
    *,
    out_path: str,
    title_prefix: str,
    spatial_seq_key: str = "attn_spatial_per_frame",
    state_seq_key: Optional[str] = "state_per_frame",
    n_heads: int = 4,
    topk_per_head: int = 1,
) -> None:
    """One figure for one layer, ALL timesteps as rows.

    Columns per row (V2 version):
        0          : input frame
        1..K       : per-channel spatial attention map A[c] for the top-k
                     focused channels per head-group (channels selected at
                     ref_t once so the column set is stable across rows).
        K+1        : full spatial residual `A·V` RMS over channels
        K+2        : (optional) recurrent state `|C_ℓ|` RMS over channels
    """
    import matplotlib.pyplot as plt
    from matplotlib import gridspec

    T = rollout["episode_len"]
    ref_t = T - 1
    A_ref = rollout["attn_per_frame"][ref_t][0][layer_idx].squeeze(0)  # (C, H, W)
    selected, focus_vals = _topk_channels_per_head_v2(A_ref, n_heads, topk_per_head)
    K = len(selected)
    d_head = A_ref.shape[0] // n_heads if A_ref.shape[0] % n_heads == 0 else A_ref.shape[0]

    n_cols = 1 + K + 1 + (1 if state_seq_key is not None else 0)
    fig = plt.figure(figsize=(2.2 * n_cols, 1.5 * T))
    gs = gridspec.GridSpec(T, n_cols, wspace=0.22, hspace=0.45)

    for t in range(T):
        # Col 0 — input
        ax = fig.add_subplot(gs[t, 0])
        frame = _to_numpy(rollout["observations"][t])
        if frame.shape[0] == 3:
            frame = frame.transpose(1, 2, 0)
        frame = _normalize_for_imshow(frame)
        ax.imshow(frame)
        title = f"t={t}"
        if t == rollout["change_step"]:
            title += "  CHG"
            ax.set_title(title, fontsize=8, color="orange")
        elif t == rollout["press_step"]:
            title += "  PRESS"
            ax.set_title(title, fontsize=8, color="red")
        else:
            ax.set_title(title, fontsize=8)
        ax.axis("off")

        # Columns 1..K — per-channel spatial attention maps A[c].
        # In V2, A[c] ∈ (H, W) is the channel's spatial softmax — it shows
        # WHERE the channel is attending. Probabilities ≥ 0, sum to 1 over
        # (H, W). We use a hot colormap [0, max] for legibility.
        A_t = rollout["attn_per_frame"][t][0][layer_idx].squeeze(0)      # (C, H, W)
        for k_idx, c in enumerate(selected):
            ax = fig.add_subplot(gs[t, 1 + k_idx])
            chan_map = _to_numpy(A_t[c])
            vmax = float(chan_map.max()) + 1e-12
            ax.imshow(chan_map, cmap="hot", vmin=0.0, vmax=vmax)
            if t == 0:
                head = c // d_head
                ax.set_title(
                    f"h{head} c{c}\nA_max={float(A_t[c].max()):.2f}",
                    fontsize=7,
                )
            ax.axis("off")

        # Penultimate col — full spatial residual RMS over channels.
        ax = fig.add_subplot(gs[t, 1 + K])
        spatial_t = rollout[spatial_seq_key][t][0][layer_idx].squeeze(0)   # (C, H, W)
        full_map = _channel_rms(spatial_t)
        ax.imshow(full_map, cmap="hot")
        if t == 0:
            ax.set_title("A·V RMS", fontsize=8)
        ax.axis("off")

        # Final col — recurrent state magnitude (optional).
        if state_seq_key is not None:
            ax = fig.add_subplot(gs[t, 2 + K])
            state_t = rollout[state_seq_key][t][0][layer_idx].squeeze(0)
            state_map = _channel_rms(state_t)
            ax.imshow(state_map, cmap="magma")
            if t == 0:
                ax.set_title(f"|C_{layer_idx+1}| RMS", fontsize=8)
            ax.axis("off")

    fig.suptitle(
        f"{title_prefix} layer {layer_idx+1}: "
        f"per-channel spatial attention A[c] (V2) + spatial residual + state\n"
        f"trial: cue=top-left red prop=1.0, change@t={rollout['change_step']}, "
        f"press@t={rollout['press_step']}",
        fontsize=10, y=1.0,
    )
    plt.tight_layout()
    plt.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {out_path}")


def plot_specialist_full_episode(
    rollout: dict,
    *,
    branch: str,                  # 'actor' or 'critic'
    out_path: str,
    n_heads: int = 4,
    topk_per_head: int = 1,
) -> None:
    """C₃ specialist (actor or critic) — all timesteps. V2 plotting."""
    import matplotlib.pyplot as plt
    from matplotlib import gridspec

    T = rollout["episode_len"]
    spec_seq = rollout["specialists_per_frame"]
    if len(spec_seq) == 0 or not isinstance(spec_seq[0], list) or len(spec_seq[0]) == 0:
        print(f"[skip] no specialist data for branch={branch}")
        return
    ref_t = T - 1
    A_ref = spec_seq[ref_t][0][branch].squeeze(0)                      # (C, H, W)
    selected, _ = _topk_channels_per_head_v2(A_ref, n_heads, topk_per_head)
    K = len(selected)
    d_head = A_ref.shape[0] // n_heads if A_ref.shape[0] % n_heads == 0 else A_ref.shape[0]

    n_cols = 1 + K + 1
    fig = plt.figure(figsize=(2.2 * n_cols, 1.5 * T))
    gs = gridspec.GridSpec(T, n_cols, wspace=0.22, hspace=0.45)

    for t in range(T):
        # Col 0 — input.
        ax = fig.add_subplot(gs[t, 0])
        frame = _to_numpy(rollout["observations"][t])
        if frame.shape[0] == 3:
            frame = frame.transpose(1, 2, 0)
        frame = _normalize_for_imshow(frame)
        ax.imshow(frame)
        title = f"t={t}"
        if t == rollout["change_step"]:
            ax.set_title(title + "  CHG", fontsize=8, color="orange")
        elif t == rollout["press_step"]:
            ax.set_title(title + "  PRESS", fontsize=8, color="red")
        else:
            ax.set_title(title, fontsize=8)
        ax.axis("off")

        # Selected channels' spatial attention maps A[c].
        A_t = spec_seq[t][0][branch].squeeze(0)                        # (C, H, W)
        for k_idx, c in enumerate(selected):
            ax = fig.add_subplot(gs[t, 1 + k_idx])
            chan_map = _to_numpy(A_t[c])
            vmax = float(chan_map.max()) + 1e-12
            ax.imshow(chan_map, cmap="hot", vmin=0.0, vmax=vmax)
            if t == 0:
                head = c // d_head
                ax.set_title(
                    f"h{head} c{c}\nA_max={float(A_t[c].max()):.2f}",
                    fontsize=7,
                )
            ax.axis("off")

        ax = fig.add_subplot(gs[t, 1 + K])
        spatial_t = spec_seq[t][0][f"{branch}_spatial"].squeeze(0)     # (C, H, W)
        full_map = _channel_rms(spatial_t)
        ax.imshow(full_map, cmap="hot")
        if t == 0:
            ax.set_title("A·V RMS", fontsize=8)
        ax.axis("off")

    fig.suptitle(
        f"{branch.upper()} specialist (cell3_{branch}) per-channel spatial attention — every timestep\n"
        f"trial: cue=top-left red prop=1.0, change@t={rollout['change_step']}, "
        f"press@t={rollout['press_step']}",
        fontsize=10, y=1.0,
    )
    plt.tight_layout()
    plt.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {out_path}")


def write_summary(rollout: dict, path: str) -> None:
    """V2 summary CSV.

    For each timestep:
      * action / reward / change-flag / press-flag
      * per-layer A·V spatial RMS (= L*_spatial_rms)
      * per-layer MEAN-per-channel spatial entropy (= L*_softmax_ent_nats).
        With per-channel spatial softmax over an N=H·W grid, max possible
        entropy is log(N). For state_channels=(64,96,128) at (12·12, 6·6, 3·3),
        max entropies are log(144)≈4.97, log(36)≈3.58, log(9)≈2.20.
      * per-layer mean A_max — peak attention probability averaged across channels.
        A converged-but-spread attention has A_max ≈ 1/N; a saturated channel
        has A_max ≈ 1.
    """
    import csv
    T = rollout["episode_len"]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "t", "action", "reward", "is_change", "is_press",
            "L1_spatial_rms", "L2_spatial_rms", "L3_spatial_rms",
            "L1_softmax_ent_nats", "L2_softmax_ent_nats", "L3_softmax_ent_nats",
            "L1_A_max_mean", "L2_A_max_mean", "L3_A_max_mean",
        ])
        for t in range(T):
            row = [t, int(rollout["actions"][t].item()), float(rollout["rewards"][t].item()),
                   int(t == rollout["change_step"]),
                   int(t == rollout["press_step"])]
            for L in range(3):
                spatial = rollout["attn_spatial_per_frame"][t][0][L].squeeze(0)
                rms = float((spatial.pow(2).mean()).sqrt().item())
                row.append(rms)
            for L in range(3):
                A = rollout["attn_per_frame"][t][0][L].squeeze(0)  # (C, H, W)
                ent_per_c = _spatial_entropy_per_channel(A)         # (C,)
                row.append(float(ent_per_c.mean().item()))
            for L in range(3):
                A = rollout["attn_per_frame"][t][0][L].squeeze(0)   # (C, H, W)
                a_max_per_c = A.reshape(A.shape[0], -1).max(dim=-1).values
                row.append(float(a_max_per_c.mean().item()))
            w.writerow(row)
    print(f"[saved] {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default="RViT_plus_v3/checkpoints/rvit_plus_rl_latest.pt")
    ap.add_argument("--out-dir",    default="RViT_plus_v3/analysis/figures")
    ap.add_argument("--device",     default="cpu")
    ap.add_argument("--seed",       type=int, default=0)
    ap.add_argument("--change-step", type=int, default=15,
                    help="0-indexed frame at which the change happens (env.change_time = this + 1).")
    ap.add_argument("--topk-per-head", type=int, default=2,
                    help="How many channels per head-group to show as separate columns.")
    ap.add_argument("--cue-position", default="left", choices=["left", "right"],
                    help="Cue location: 'left' = top-left, 'right' = bottom-right.")
    ap.add_argument("--cue-color", default="red", choices=["red", "green", "blue"],
                    help="Cue color (sets the reward magnitude on correct press).")
    ap.add_argument("--proportion", type=float, default=1.0,
                    help="Cue validity (0.25 / 0.5 / 0.75 / 1.0). 1.0 = full ring, high validity; "
                         "0.25 = quarter ring, low validity, model should be uncertain.")
    ap.add_argument("--change-index", type=int, default=0,
                    help="Which gabor is going to flip: 0=top-left, 1=bottom-left, 2=top-right, 3=bottom-right.")
    ap.add_argument("--out-suffix", default="",
                    help="Suffix appended to output filenames so multiple conditions can be compared.")
    args = ap.parse_args(argv)

    device = torch.device(args.device)
    os.makedirs(args.out_dir, exist_ok=True)

    ckpt = torch.load(args.checkpoint, map_location=device, weights_only=False)
    if "model_kwargs" in ckpt:
        kwargs = ckpt["model_kwargs"]
    else:
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

    env = make_forced_env(
        change_time=args.change_step + 1,
        cue_position=args.cue_position,
        cue_color=args.cue_color,
        proportion=args.proportion,
        change_index=args.change_index,
        change_true=1,
        seed=args.seed,
    )

    roll = rollout(model, env, device=device)
    print(f"[trial] len={roll['episode_len']}  change@{roll['change_step']}  "
          f"press@{roll['press_step']}  return={roll['rewards'].sum().item():.3f}")

    suf = (f"_{args.out_suffix}" if args.out_suffix else "")
    # Per-layer figures — AE/shared C₃ pathway.
    for L in range(3):
        plot_layer_full_episode(
            roll, layer_idx=L,
            out_path=os.path.join(args.out_dir, f"attn_forced{suf}_layer{L+1}.png"),
            title_prefix=f"V2 AE/shared (prop={args.proportion}, cue={args.cue_position}/{args.cue_color})",
            topk_per_head=args.topk_per_head,
        )

    # Specialist heads (actor and critic) — only at layer 3.
    plot_specialist_full_episode(
        roll, branch="actor",
        out_path=os.path.join(args.out_dir, f"attn_forced{suf}_layer3_actor.png"),
        topk_per_head=args.topk_per_head,
    )
    plot_specialist_full_episode(
        roll, branch="critic",
        out_path=os.path.join(args.out_dir, f"attn_forced{suf}_layer3_critic.png"),
        topk_per_head=args.topk_per_head,
    )

    write_summary(roll, os.path.join(args.out_dir, f"attn_forced{suf}_summary.csv"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
