"""Render N luo2015_sensitivity trials as an animated GIF (what the agent sees).

20 trials, 4 columns. Each cell is one trial (T=7, 50x50). Epoch borders:
  green  = sample (t=0,1)     both Gabors, no cue
  none   = delay / gap (t=2,5)
  yellow = first test (t=3,4) declaration window
  red    = second test (t=6)  no-change trials only (guaranteed change)

Label under each cell is short: idx, C/N, test loc, dθ.
A starred loc is the high-reward location (high_loc=0 = S1 in this GIF).

Usage: python make_trials_gif_luo2015.py [out_gif] [n_trials]
"""
from __future__ import annotations

import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from envs import make_env  # noqa: E402

T = 7
SCALE = 3
COLS = 4
FPS_MS = 420
PAD = 6
LABEL_H = 16


def border_color(t, change_true):
    if t in (0, 1):
        return (50, 200, 70)
    if t in (3, 4):
        return (240, 210, 40)
    if t == 6 and change_true == 0:
        return (230, 50, 50)
    return None


def main() -> None:
    out_gif = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "luo2015_trials.gif")
    n_trials = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    rows = (n_trials + COLS - 1) // COLS

    env = make_env(
        "luo2015_sensitivity", T=T, frame_repeat=1,
        noise_multiplier=5.0, curriculum=False, theta=65.0, high_loc=0,
    )

    trials = []
    for _ in range(n_trials):
        env.reset()
        frames = env.render_trial()
        h_r, cr_r = env.reward_table[env.test_loc]
        trials.append({
            "frames": frames,
            "change_true": int(env.change_true),
            "test_loc": int(env.test_loc),
            "high_loc": int(env.high_loc),
            "dtheta": float(env.orientation_change),
            "h_r": float(h_r),
            "cr_r": float(cr_r),
        })

    cell = 50 * SCALE
    header = 22
    W = COLS * cell + (COLS + 1) * PAD
    H = header + rows * (cell + LABEL_H + PAD) + PAD
    font = ImageFont.load_default()

    gif_frames = []
    epoch = {
        0: "sample BOTH Gabors",
        1: "sample BOTH Gabors",
        2: "delay (blank)",
        3: "1st test  (hit / FA window)",
        4: "1st test  (hit / FA window)",
        5: "gap",
        6: "2nd test  (CR catch, no-change only)",
    }
    for t in range(T):
        canvas = Image.new("RGB", (W, H), (18, 18, 18))
        draw = ImageDraw.Draw(canvas)
        draw.text((PAD, 4), f"t={t}/6  {epoch[t]}   high_loc=S1*", fill=(255, 230, 80), font=font)
        for i, tr in enumerate(trials):
            r, c = divmod(i, COLS)
            x0 = PAD + c * (cell + PAD)
            y0 = header + PAD + r * (cell + LABEL_H + PAD)
            fr = np.clip(tr["frames"][t] * 255.0, 0, 255).astype(np.uint8)
            img = Image.fromarray(fr).resize((cell, cell), Image.NEAREST)
            canvas.paste(img, (x0, y0))
            bc = border_color(t, tr["change_true"])
            if bc is not None:
                draw.rectangle([x0, y0, x0 + cell - 1, y0 + cell - 1], outline=bc, width=2)
            loc_s = "S1" if tr["test_loc"] == 0 else "S4"
            star = "*" if tr["test_loc"] == tr["high_loc"] else " "
            kind = "C" if tr["change_true"] else "N"
            draw.text(
                (x0 + 2, y0 + cell + 2),
                f"{i:02d} {kind} {loc_s}{star} {tr['dtheta']:+.0f}",
                fill=(220, 220, 220),
                font=font,
            )
        gif_frames.append(canvas)

    gif_frames[0].save(
        out_gif, save_all=True, append_images=gif_frames[1:],
        duration=FPS_MS, loop=0,
    )
    print(f"saved {out_gif}  ({len(gif_frames)} frames, {n_trials} trials)")
    for i, tr in enumerate(trials):
        loc_s = "S1" if tr["test_loc"] == 0 else "S4"
        print(
            f"  trial {i:02d}: change={tr['change_true']} test={loc_s} "
            f"high_loc={tr['high_loc']} dtheta={tr['dtheta']:+.1f} "
            f"H={tr['h_r']:.2f} CR={tr['cr_r']:.2f}"
        )


if __name__ == "__main__":
    main()
