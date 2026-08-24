"""
Render ONE episode as a PER-HEAD attention-overlay grid movie.

Every output frame is a (1 + n_heads) × n_enc_layers panel grid:

    [ HUD strip                                                        ]
    [ raw frame+boxes | L1·H1 | L1·H2 | … | L1·H8 ]     ← encoder layer 1
    [ actor CLS mean  | L2·H1 | L2·H2 | … | L2·H8 ]     ← encoder layer 2

Each head panel is the observation frame alpha-blended with THAT head's
attention over patch positions (mean over the 48 queries; patch-aligned key
groups — patch + H₁ + H₂ — summed per grid position; per-panel max-normalized
so the SHAPE of each head's map is visible regardless of its magnitude).
First column: the native frame with red monster boxes (row 1) and the actor
decoder's final-layer CLS attention averaged over heads (row 2) — "what the
decision reads".

    .venv/bin/python v10_VizdoomArena/analysis/render_attention_grid.py
    .venv/bin/python v10_VizdoomArena/analysis/render_attention_grid.py \
        --greedy --stride 2 --scale 1 --max-steps 400

Safe to run while training continues (own Doom instance, read-only load).
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np
import torch
from torch.distributions import Categorical

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from v10_VizdoomArena.env import ACTION_NAMES, VizdoomArenaEnv
from v10_VizdoomArena.model import V10ArenaModel

PANEL_W, PANEL_H = 160, 120


def _load_checkpoint(path: str, device: torch.device):
    """One retry — the trainer rewrites v10_latest.pt every few minutes."""
    for attempt in (0, 1):
        try:
            return torch.load(path, map_location=device, weights_only=False)
        except Exception:
            if attempt == 1:
                raise
            time.sleep(2.0)


def _patch_aligned_spans(layout: dict, n_grid: int) -> list:
    return [(lo, hi) for (lo, hi) in layout.values() if hi - lo == n_grid]


def _per_head_grids(attn_layer: torch.Tensor, spans: list, gh: int, gw: int) -> np.ndarray:
    """(1, heads, N_q, n_keys) → (heads, gh, gw): mean over queries, patch-
    aligned key groups summed per grid position."""
    a = attn_layer[0].mean(dim=1)                       # (heads, n_keys)
    g = torch.zeros(a.shape[0], gh * gw)
    for lo, hi in spans:
        g = g + a[:, lo:hi]
    return g.reshape(-1, gh, gw).numpy()


def _cls_mean_grid(actor_attn_last: torch.Tensor, token_layout: dict,
                   gh: int, gw: int) -> np.ndarray:
    """Final actor layer (1, heads, S, S) → (gh, gw): CLS row, mean over
    heads, H_k token spans summed per grid position."""
    row = actor_attn_last[0].mean(dim=0)[0]             # (S,)
    g = torch.zeros(gh * gw)
    for name, (lo, hi) in token_layout.items():
        if name.startswith("H"):
            g = g + row[lo:hi]
    return g.reshape(gh, gw).numpy()


def _overlay_panel(frame_img, grid: np.ndarray, label: str, cmap, scale: int,
                   font_fill=(255, 255, 255)):
    """Blend a (gh, gw) attention grid over the frame; returns a PIL panel."""
    from PIL import Image, ImageDraw
    g = grid / max(float(grid.max()), 1e-8)
    heat = (cmap(g)[..., :3] * 255).astype(np.uint8)
    heat_img = Image.fromarray(heat).resize((PANEL_W * scale, PANEL_H * scale), Image.NEAREST)
    blended = Image.blend(frame_img, heat_img, alpha=0.55)
    ImageDraw.Draw(blended).text((3, 2), label, fill=font_fill)
    return blended


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", default=os.path.expanduser(
        "~/rvit_plus_checkpoints/v10_vizdoom_arena/v10_latest.pt"))
    p.add_argument("--out", default=None, help="output GIF (default: alongside checkpoint)")
    p.add_argument("--device", default="cpu")
    p.add_argument("--greedy", action="store_true")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--max-steps", type=int, default=1100)
    p.add_argument("--scale", type=int, default=1, help="upscale per panel (1 → 160×120 panels)")
    p.add_argument("--fps", type=float, default=9.0, help="playback ≈ real time at 9")
    p.add_argument("--stride", type=int, default=1,
                   help="render every k-th step (GIF stays real-time-paced)")
    args = p.parse_args(argv)

    from PIL import Image, ImageDraw
    import matplotlib
    cmap = matplotlib.colormaps["inferno"]

    device = torch.device(args.device)
    ckpt = _load_checkpoint(args.checkpoint, device)
    model = V10ArenaModel(**ckpt["model_kwargs"]).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    it = ckpt.get("iter", -1)
    gh, gw = model.patch_embed.grid_h, model.patch_embed.grid_w
    n_heads = model.encoder.n_heads
    L = model.enc_layers
    enc_spans = [_patch_aligned_spans(model.encoder.key_layout(k), gh * gw)
                 for k in range(L)]
    dec_layout = model.actor_head.token_layout()
    print(f"[load] {args.checkpoint}  (iter={it}, env_steps={ckpt.get('env_steps')})")
    print(f"[grid] {L} layers × {n_heads} heads + frame/actor column → "
          f"{(1 + n_heads)} × {L} panels of {PANEL_W * args.scale}×{PANEL_H * args.scale}")

    env = VizdoomArenaEnv(enable_labels=True, seed=args.seed)
    obs, feats = env.reset()
    states = model.init_states(1, device=device)

    s = args.scale
    frames: list = []
    kills, shaped_return, n_steps, died = 0.0, 0.0, 0, False

    with torch.no_grad():
        for t in range(args.max_steps):
            raw = env.game.get_state().screen_buffer            # (3,120,160)
            frame_img = Image.fromarray(np.transpose(raw, (1, 2, 0))).resize(
                (PANEL_W * s, PANEL_H * s), Image.NEAREST)

            render_this = (t % max(args.stride, 1) == 0)
            out = model.rl_step(
                torch.from_numpy(obs).to(device).float().div_(255.0).unsqueeze(0),
                torch.from_numpy(feats).to(device).unsqueeze(0),
                states, return_attn=render_this)
            states = out["new_states"]
            logits = out["actor_logits"][0]
            a = int(logits.argmax().item()) if args.greedy else \
                int(Categorical(logits=logits).sample().item())

            if render_this:
                # First column, row 1: raw frame + monster boxes.
                base = frame_img.copy()
                d = ImageDraw.Draw(base)
                for lab in env.labels:
                    if not lab["is_monster"]:
                        continue
                    x0, y0 = lab["x"] * 2 * s, lab["y"] * 2 * s
                    d.rectangle([x0, y0, x0 + lab["w"] * 2 * s, y0 + lab["h"] * 2 * s],
                                outline=(255, 40, 40), width=max(1, 2 * s - 1))
                d.text((3, 2), "frame", fill=(255, 255, 160))
                # First column, row 2: actor CLS mean overlay.
                cls_panel = _overlay_panel(
                    frame_img, _cls_mean_grid(out["actor_attn"][-1].cpu(), dec_layout, gh, gw),
                    "actor CLS", cmap, s, font_fill=(160, 255, 160))
                first_col = [base, cls_panel]
                while len(first_col) < L:                       # L > 2: pad with frame
                    first_col.append(frame_img.copy())

                canvas = Image.new("RGB", ((1 + n_heads) * PANEL_W * s,
                                           L * PANEL_H * s + 14 + 2 * s))
                hud = (f"iter {it}  step {n_steps:4d}  kills {kills:.0f}  "
                       f"hp {feats[0]*100:.0f}  ammo {feats[2]*200:.0f}  {ACTION_NAMES[a]}")
                ImageDraw.Draw(canvas).text((4, 2), hud, fill=(255, 255, 160))
                y0 = 14 + 2 * s
                for li in range(L):
                    canvas.paste(first_col[li] if li < len(first_col) else frame_img,
                                 (0, y0 + li * PANEL_H * s))
                    grids = _per_head_grids(out["enc_attn"][li].cpu(), enc_spans[li], gh, gw)
                    for h in range(n_heads):
                        panel = _overlay_panel(frame_img, grids[h], f"L{li+1}·H{h+1}", cmap, s)
                        canvas.paste(panel, ((1 + h) * PANEL_W * s, y0 + li * PANEL_H * s))
                frames.append(canvas)

            obs, feats, r, done, info = env.step(a)
            shaped_return += r
            kills = info["kills"] if not done else info["episode"]["kills"]
            n_steps += 1
            if done:
                died = info["died"]
                break
    env.close()

    end = "died" if died else ("timeout" if n_steps < args.max_steps else "step cap")
    print(f"[episode] {n_steps} steps  kills={kills:.0f}  "
          f"shaped_return={shaped_return:+.2f}  end={end}")

    out_path = args.out or os.path.join(
        os.path.dirname(os.path.abspath(os.path.expanduser(args.checkpoint))),
        f"episode_attn_grid_iter{max(int(it), 0):05d}.gif")
    duration = int(round(1000.0 * args.stride / max(args.fps, 1e-3)))   # keep real-time pacing
    frames[0].save(out_path, save_all=True, append_images=frames[1:],
                   duration=duration, loop=0)
    print(f"[gif] {len(frames)} frames ({frames[0].size[0]}×{frames[0].size[1]}) "
          f"→ {out_path}  ({os.path.getsize(out_path) / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
