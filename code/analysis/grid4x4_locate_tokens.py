"""Empirically identify which of the 16 patch-token key indices correspond to VDA4's
4 task-level active locations, for the grid4x4 discretization checkpoint.

The environment still has exactly 4 active stimuli (task stimulus grid stays 2x2); only
the model's patch/memory tokenization was overridden to 4x4=16. ``make_video_batch``
and ``press_times_clamp`` operate in task-location space (0-3) and handle this
transparently, but the causal-clamp primitives need a literal key index into the
model's 16-slot attention arrays. This script cues each of the 4 task locations in turn
(no change, no clamp) and reports which of the 16 keys receives the most attention mass
at the cue frame -- that key index is the task location's real position in patch space.
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import torch

from vda_sweep import vda_core as core

CHECKPOINT = Path("/workspace/vda4_grid4x4_crossattn1_d128_nodecay_seed0/rvit_paper_vda4_final.pt")
EXPECTED_SHA256 = "306ce94d44461ea85cd0aced5a84eb210457f718d3f2e4ebf85e46ee1922e4bf"


def main() -> None:
    import hashlib
    actual = hashlib.sha256(CHECKPOINT.read_bytes()).hexdigest()
    assert actual == EXPECTED_SHA256, (actual, EXPECTED_SHA256)

    model, iteration = core.load(
        "vda4", "crossattn1", 128, checkpoint_path=str(CHECKPOINT), validate_metadata=False
    )
    print(f"loaded iteration {iteration}")

    for task_loc in range(4):
        videos = core.make_video_batch("vda4", task_loc, 1.0, "red", 0, -1, 0.0, B=64, seed=1000 + task_loc)
        state = model.init_states(64, device=core.DEVICE)
        for t in range(core.T):
            with torch.no_grad():
                step = model.rl_step(videos[:, t], state, return_attn=True, attn_clamp=None)
                state = step["new_states"]
                if t == 1:  # cue-onset frame
                    attn = step["attn"][0].detach().cpu().numpy()  # (queries, keys)
        keys = attn.shape[-1]
        n_locations = keys // 2 if keys == 32 else keys
        sliced = attn[..., :n_locations] if keys == 32 else attn
        image_mass = sliced.reshape(-1, n_locations).mean(axis=0)
        top = np.argsort(image_mass)[::-1][:3]
        print(f"task_loc={task_loc}: attn.shape={attn.shape} keys={keys} top image-key indices (t1, cue frame) = {top.tolist()}, masses={image_mass[top].round(4).tolist()}")


if __name__ == "__main__":
    main()
