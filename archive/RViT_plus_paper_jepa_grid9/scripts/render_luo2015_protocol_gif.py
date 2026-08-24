#!/usr/bin/env python3
"""Render the paper-aligned Luo & Maunsell task conditions as an animated GIF."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from envs.luo2015 import LuoMaunsell2015Env  # noqa: E402

PANEL_SPECS = (
    ("Sensitivity · condition A", "sensitivity", 0),
    ("Sensitivity · condition B", "sensitivity", 3),
    ("Criterion · condition A", "criterion", 0),
    ("Criterion · condition B", "criterion", 3),
)
FRAME_LABELS = (
    "sample",
    "sample",
    "delay",
    "first test · unchanged",
    "first test · unchanged",
    "inter-test gap",
    "second test · changed",
)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/DejaVuSans-Bold.ttf" if bold
        else "/System/Library/Fonts/Supplemental/DejaVuSans.ttf",
    )
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def _prepared_env(session: str, condition_loc: int) -> LuoMaunsell2015Env:
    env = LuoMaunsell2015Env(
        session=session,
        condition_loc=condition_loc,
        T=7,
        theta=20.0,
        noise_multiplier=0.0,
        curriculum=False,
        base_orientations={0: 15.0, 3: 95.0},
    )
    # Use exactly the same no-change trial in every panel. The observation therefore
    # cannot reveal which reward condition is active.
    env.samp = {0: 15.0, 3: 115.0}
    env.test_loc = 0
    env.change_true = 0
    env.test_ori = env.samp[0]
    env.second_test_ori = env.samp[0] + env.theta
    env._frame_cache = None
    return env


def _reward_text(env: LuoMaunsell2015Env) -> tuple[str, str]:
    first = env.reward_table[0]
    second = env.reward_table[3]
    return (
        f"loc 0   H {first[0]:.2f}   CR {first[1]:.2f}",
        f"loc 3   H {second[0]:.2f}   CR {second[1]:.2f}",
    )


def build_gif(output: Path) -> None:
    envs = [_prepared_env(session, location) for _, session, location in PANEL_SPECS]
    videos = [env.render_trial() for env in envs]
    if any(video.shape != (7, 50, 50, 3) for video in videos):
        raise RuntimeError(f"unexpected rendered video shapes: {[video.shape for video in videos]}")

    canvas_size = (1280, 940)
    panel_xy = ((50, 185), (660, 185), (50, 550), (660, 550))
    title_font = _font(34, bold=True)
    subtitle_font = _font(20)
    panel_font = _font(23, bold=True)
    body_font = _font(18)
    footer_font = _font(17)
    frames: list[Image.Image] = []

    for timestep, label in enumerate(FRAME_LABELS):
        canvas = Image.new("RGB", canvas_size, "#f7f4ed")
        draw = ImageDraw.Draw(canvas)
        draw.text((50, 35), "Luo & Maunsell reward-dissociation environment", fill="#111827", font=title_font)
        draw.text(
            (50, 88),
            f"logical frame {timestep}/6 · {label}",
            fill="#155e75",
            font=subtitle_font,
        )
        draw.text(
            (50, 125),
            "The retinal input is identical across conditions; only the outcome-dependent reward table changes.",
            fill="#374151",
            font=subtitle_font,
        )

        for (panel_title, _, condition_loc), env, video, (x, y) in zip(
            PANEL_SPECS, envs, videos, panel_xy
        ):
            draw.rounded_rectangle((x, y, x + 570, y + 340), radius=16, fill="white", outline="#cbd5e1", width=2)
            condition_label = "high value" if env.session == "sensitivity" else "low criterion"
            draw.text((x + 18, y + 15), panel_title, fill="#111827", font=panel_font)
            draw.text(
                (x + 18, y + 51),
                f"condition location: {condition_loc} ({condition_label})",
                fill="#4b5563",
                font=body_font,
            )
            raw = video[timestep, :, :, 0]
            pixels = np.clip((raw + 1.0) * 127.5, 0, 255).astype(np.uint8)
            observation = Image.fromarray(pixels, mode="L").convert("RGB").resize((250, 250), Image.Resampling.NEAREST)
            observation = Image.merge(
                "RGB",
                (
                    observation.getchannel("R"),
                    observation.getchannel("G"),
                    observation.getchannel("B"),
                ),
            )
            canvas.paste(observation, (x + 18, y + 78))
            draw.rectangle((x + 18, y + 78, x + 268, y + 328), outline="#111827", width=2)
            reward_lines = _reward_text(env)
            draw.text((x + 292, y + 102), "reward if correct", fill="#111827", font=panel_font)
            draw.text((x + 292, y + 148), reward_lines[0], fill="#1f2937", font=body_font)
            draw.text((x + 292, y + 183), reward_lines[1], fill="#1f2937", font=body_font)
            draw.text((x + 292, y + 231), "H = hit", fill="#6b7280", font=body_font)
            draw.text((x + 292, y + 263), "CR = correct rejection", fill="#6b7280", font=body_font)

        draw.text(
            (50, 900),
            "No-change trials earn CR reward only after withholding at the first test and declaring the changed second test.",
            fill="#374151",
            font=footer_font,
        )
        frames.append(canvas)

    output.parent.mkdir(parents=True, exist_ok=True)
    durations = [700, 700, 900, 700, 700, 900, 1400]
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build_gif(args.output.resolve())
    print(args.output.resolve())


if __name__ == "__main__":
    main()
