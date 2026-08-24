"""
Render the most recent V6 checkpoint playing ONE arena episode.

Default: saves an animated GIF (native 160×120 frames upscaled, with a small
HUD line and red boxes around labeled monsters) next to the checkpoint:

    .venv/bin/python v6_VizdoomArena/analysis/render_episode.py
    .venv/bin/python v6_VizdoomArena/analysis/render_episode.py --greedy --scale 3
    .venv/bin/python v6_VizdoomArena/analysis/render_episode.py --attn      # + encoder attention panels
    .venv/bin/python v6_VizdoomArena/analysis/render_episode.py --window    # watch live instead

Safe to run while training continues — it opens its own Doom instance and
loads the checkpoint read-only.
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

from v6_VizdoomArena.env import ACTION_NAMES, VizdoomArenaEnv
from v6_VizdoomArena.model import V6ArenaModel


def _load_checkpoint(path: str, device: torch.device):
    """Load with one retry — the trainer rewrites v6_latest.pt every few minutes."""
    for attempt in (0, 1):
        try:
            return torch.load(path, map_location=device, weights_only=False)
        except Exception:
            if attempt == 1:
                raise
            time.sleep(2.0)


def _attn_grid(enc_attn_layer: torch.Tensor, layout: dict, gh: int, gw: int) -> np.ndarray:
    """(1, heads, N, n_keys) → (gh, gw) patch-position attention: mean over
    heads & queries, patch-aligned key groups (patch + H_k) summed per position."""
    a = enc_attn_layer[0].mean(dim=0).mean(dim=0)            # (n_keys,)
    grid = torch.zeros(gh * gw)
    for _name, (lo, hi) in layout.items():
        if hi - lo == gh * gw:
            grid = grid + a[lo:hi]
    return grid.reshape(gh, gw).numpy()


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", default=os.path.expanduser(
        "~/rvit_plus_checkpoints/v6_vizdoom_arena/v6_latest.pt"))
    p.add_argument("--out", default=None, help="output GIF path (default: alongside checkpoint)")
    p.add_argument("--device", default="cpu")
    p.add_argument("--greedy", action="store_true", help="argmax policy instead of sampling")
    p.add_argument("--seed", type=int, default=None, help="env seed (default: random)")
    p.add_argument("--max-steps", type=int, default=1100, help="safety cap (full episode ≈ 1050)")
    p.add_argument("--scale", type=int, default=2, help="upscale of the native 160×120 frame")
    p.add_argument("--fps", type=float, default=9.0, help="GIF playback fps (9 ≈ real time)")
    p.add_argument("--attn", action="store_true",
                   help="append per-encoder-layer attention panels to each frame")
    p.add_argument("--window", action="store_true",
                   help="show the live game window instead of (also) saving a GIF")
    args = p.parse_args(argv)

    from PIL import Image, ImageDraw

    device = torch.device(args.device)
    ckpt = _load_checkpoint(args.checkpoint, device)
    model = V6ArenaModel(**ckpt["model_kwargs"]).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    it = ckpt.get("iter", -1)
    gh, gw = model.patch_embed.grid_h, model.patch_embed.grid_w
    layout = model.encoder.key_layout()
    print(f"[load] {args.checkpoint}  (iter={it}, env_steps={ckpt.get('env_steps')})")

    env = VizdoomArenaEnv(enable_labels=True, seed=args.seed, visible=args.window)
    obs, feats = env.reset()
    states = model.init_states(1, device=device)

    cmap = None
    if args.attn:
        import matplotlib
        cmap = matplotlib.colormaps["inferno"]

    frames: list = []
    kills = 0.0
    shaped_return = 0.0
    n_steps = 0
    action_name = "—"
    died = False

    with torch.no_grad():
        for _t in range(args.max_steps):
            # Native 160×120 frame of the CURRENT (pre-action) state.
            raw = env.game.get_state().screen_buffer          # (3,120,160) uint8
            frame = np.transpose(raw, (1, 2, 0))              # → (120,160,3)

            x = torch.from_numpy(obs).to(device).float().div_(255.0).unsqueeze(0)
            f = torch.from_numpy(feats).to(device).unsqueeze(0)
            out = model.rl_step(x, f, states, return_attn=args.attn)
            states = out["new_states"]
            logits = out["actor_logits"][0]
            a = int(logits.argmax().item()) if args.greedy else \
                int(Categorical(logits=logits).sample().item())
            action_name = ACTION_NAMES[a]

            # ── compose the output frame ─────────────────────────────────────
            s = args.scale
            img = Image.fromarray(frame).resize((160 * s, 120 * s), Image.NEAREST)
            draw = ImageDraw.Draw(img)
            for lab in env.labels:                            # labels are in 80×60 coords
                if not lab["is_monster"]:
                    continue
                x0, y0 = lab["x"] * 2 * s, lab["y"] * 2 * s
                x1, y1 = x0 + lab["w"] * 2 * s, y0 + lab["h"] * 2 * s
                draw.rectangle([x0, y0, x1, y1], outline=(255, 40, 40), width=max(1, s - 1))
            hud = (f"iter {it}  step {n_steps:4d}  kills {kills:.0f}  "
                   f"hp {feats[0]*100:.0f}  ammo {feats[2]*200:.0f}  {action_name}")
            draw.rectangle([0, 0, 160 * s, 12 + 2 * s], fill=(0, 0, 0))
            draw.text((4, 2), hud, fill=(255, 255, 160))

            if args.attn:
                panels = [img]
                for k, aw in enumerate(out["enc_attn"]):
                    grid = _attn_grid(aw.cpu(), layout, gh, gw)
                    g = grid / max(float(grid.max()), 1e-8)
                    rgba = (cmap(g) * 255).astype(np.uint8)[..., :3]
                    pimg = Image.fromarray(rgba).resize((160 * s, 120 * s), Image.NEAREST)
                    ImageDraw.Draw(pimg).text((4, 2), f"enc L{k+1} attention", fill=(255, 255, 255))
                    panels.append(pimg)
                total_w = sum(im.width for im in panels)
                strip = Image.new("RGB", (total_w, 120 * s))
                xoff = 0
                for im in panels:
                    strip.paste(im, (xoff, 0))
                    xoff += im.width
                img = strip
            if not args.window:
                frames.append(img)

            # ── act ──────────────────────────────────────────────────────────
            obs, feats, r, done, info = env.step(a)
            shaped_return += r
            kills = info["kills"] if not done else info["episode"]["kills"]
            n_steps += 1
            if args.window:
                time.sleep(4.0 / 35.0)                        # ≈ real time at skip 4
            if done:
                died = info["died"]
                break
    env.close()

    end = "died" if died else ("timeout" if n_steps < args.max_steps else "step cap")
    print(f"[episode] {n_steps} steps ({n_steps*4} tics)  kills={kills:.0f}  "
          f"shaped_return={shaped_return:+.2f}  end={end}")

    if not args.window and frames:
        out_path = args.out or os.path.join(
            os.path.dirname(os.path.abspath(os.path.expanduser(args.checkpoint))),
            f"episode_iter{max(int(it), 0):05d}.gif")
        frames[0].save(
            out_path, save_all=True, append_images=frames[1:],
            duration=int(round(1000.0 / max(args.fps, 1e-3))), loop=0,
        )
        mb = os.path.getsize(out_path) / 1e6
        print(f"[gif] {len(frames)} frames @ {args.fps:g} fps → {out_path}  ({mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
