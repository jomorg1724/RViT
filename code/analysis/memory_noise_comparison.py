"""Matched-condition comparison: VDA4 trained/evaluated with memory noise vs. without.

Compares two checkpoints:
  - no-noise:  standard VDA4 crossattn1 d128, memory_noise_std=0.0, terminal (iter 19999)
  - noise0p5:  VDA4 crossattn1 d128, memory_noise_std=0.5, interrupted at iter 16037
               (not terminal; treated as usable per explicit user direction)

This is the "matched trained-condition contrast" from the pre-registered pilot design:
the no-noise model evaluated with noise off, versus the noise-trained model evaluated
with its own registered noise on (inject_memory_noise=True). It does not run the full
2x2 train x eval noise factorial, and the two checkpoints are not a strictly paired
seed-0 run (different training duration, not launched under the shared-initialization
protocol) -- both caveats are carried into the written report, not hidden.

Produces, for both conditions:
  1. behavioral psychometrics (response rate, d', criterion) across a magnitude sweep
     at three displayed validities;
  2. attention allocation: image-key vs memory-key mass, cue period (t1-t4) vs
     change period (t5-t6), split by whether the query is at the cued location.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Compatibility shim: the noise0p5 checkpoint was pickled by a numpy>=2.0 process
# (numpy's internal module layout moved from numpy.core to numpy._core in 2.0);
# this local environment runs numpy 1.23.1, which lacks that module path. Alias
# it rather than changing the installed numpy version, to avoid any risk to the
# rest of this environment's proven-working torch/numpy pairing.
sys.modules.setdefault("numpy._core", np.core)
sys.modules.setdefault("numpy._core.numeric", np.core.numeric)
sys.modules.setdefault("numpy._core.multiarray", np.core.multiarray)

from vda_sweep import vda_core as core
from vda_sweep import matched_width as MW

MAGNITUDES = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 22.0, 26.0, 30.0]
VALIDITIES = [0.25, 0.5, 0.75]
TRIALS_PER_POINT = 300
CUE_INDEX = 0
VALID_CHANGE_INDEX = 0
INVALID_CHANGE_INDEX = 3
SEED_BASE = 20260804

CONDITIONS = {
    "no_noise": dict(
        path=Path(r"C:\Users\jomor\Documents\RViT_runs\vda4_crossattn1_d128_nodecay_seed0_pod\rvit_paper_vda4_final.pt"),
        sha256="ea671f9758551e06b39ef19c06e85e888ce3ee74dda8a534c1532251a69ee4ca",
        inject_noise=False,
        iteration_note="terminal, iteration 19999",
    ),
    "noise0p5": dict(
        path=Path(r"C:\Users\jomor\Documents\RViT_runs\vda4_memory_noise_noise0p5_interrupted_snapshot_20260804T055300Z\run\rvit_plus_rl_latest.pt"),
        sha256="be5e67f907e6603229c48ee54cc41e7075d62a4514f61f0f9da0d2e56d1de967",
        inject_noise=True,
        iteration_note="interrupted, checkpoint saved at iteration 15999/20000 (80%, not terminal; metrics.csv logged up to 16037 before the process stopped)",
    ),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rollout(model, videos, inject_noise: bool, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Run a batch through the model, returning press times and the attn array at
    every frame, matching the seed-driven determinism used everywhere else in this
    project for the RNG used by noise injection (torch global RNG)."""
    torch.manual_seed(seed)
    batch = int(videos.shape[0])
    state = model.init_states(batch, device=core.DEVICE)
    press = np.full(batch, -1, dtype=np.int64)
    attn_frames = []
    for t in range(core.T):
        with torch.no_grad():
            step = model.rl_step(videos[:, t], state, return_attn=True, inject_memory_noise=inject_noise)
            actions = step["actor_logits"].argmax(-1).cpu().numpy()
            state = step["new_states"]
            attn_frames.append(step["attn"][0].detach().cpu().numpy() if step["attn"] is not None else None)
        newly_pressed = (actions == 1) & (press < 0)
        press[newly_pressed] = t
    attn_seq = np.stack(attn_frames, axis=0)  # (T, queries, keys)
    return press, attn_seq


def run_condition(name: str, spec: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    path: Path = spec["path"]
    if not path.is_file():
        return {"status": "blocked", "label": name, "expected_path": str(path)}
    actual_sha = sha256_file(path)
    if actual_sha != spec["sha256"]:
        raise RuntimeError(f"{name}: checkpoint SHA-256 mismatch: {actual_sha} != {spec['sha256']}")

    model, iteration = core.load("vda4", "crossattn1", 128, checkpoint_path=str(path))
    print(f"[{name}] loaded checkpoint at logged iteration {iteration} ({spec['iteration_note']})")

    n_v, n_m = len(VALIDITIES), len(MAGNITUDES)
    response_count_valid = np.zeros((n_v, n_m), dtype=int)
    response_count_invalid = np.zeros((n_v, n_m), dtype=int)
    false_alarm_count = np.zeros(n_v, dtype=int)

    # cue-period (t1-t4) and change-period (t5-t6) attention mass, accumulated
    # over the valid-condition sweep, split image vs memory key, cued vs true-target
    cue_period_cued_image = []
    cue_period_cued_memory = []
    change_period_target_image = []
    change_period_target_memory = []

    seed_counter = 0
    for vi, validity in enumerate(VALIDITIES):
        videos_nochange = core.make_video_batch(
            "vda4", CUE_INDEX, validity, "red", 0, -1, 0.0, B=TRIALS_PER_POINT, seed=SEED_BASE + seed_counter
        )
        seed_counter += 1
        press_nc, _ = rollout(model, videos_nochange, spec["inject_noise"], SEED_BASE + seed_counter)
        seed_counter += 1
        false_alarm_count[vi] = int((press_nc >= 0).sum())

        for mi, mag in enumerate(MAGNITUDES):
            videos_valid = core.make_video_batch(
                "vda4", CUE_INDEX, validity, "red", 1, VALID_CHANGE_INDEX, mag,
                B=TRIALS_PER_POINT, seed=SEED_BASE + seed_counter,
            )
            seed_counter += 1
            press_v, attn_v = rollout(model, videos_valid, spec["inject_noise"], SEED_BASE + seed_counter)
            seed_counter += 1
            response_count_valid[vi, mi] = int(np.isin(press_v, (5, 6)).sum())

            videos_invalid = core.make_video_batch(
                "vda4", CUE_INDEX, validity, "red", 1, INVALID_CHANGE_INDEX, mag,
                B=TRIALS_PER_POINT, seed=SEED_BASE + seed_counter,
            )
            seed_counter += 1
            press_i, _ = rollout(model, videos_invalid, spec["inject_noise"], SEED_BASE + seed_counter)
            seed_counter += 1
            response_count_invalid[vi, mi] = int(np.isin(press_i, (5, 6)).sum())

            if np.isclose(mag, 18.0):
                # attn_v shape: (T, batch, queries, keys); keys = 8 (4 image + 4 memory)
                image_mass = attn_v[..., :4].mean(axis=(1, 2))  # (T, 4) averaged over batch and queries
                memory_mass = attn_v[..., 4:].mean(axis=(1, 2))
                cue_period_cued_image.append(image_mass[1:5, CUE_INDEX].mean())
                cue_period_cued_memory.append(memory_mass[1:5, CUE_INDEX].mean())
                change_period_target_image.append(image_mass[5:7, VALID_CHANGE_INDEX].mean())
                change_period_target_memory.append(memory_mass[5:7, VALID_CHANGE_INDEX].mean())

        print(f"[{name}] validity={validity:.2f} done")

    dprime = np.zeros((n_v, n_m))
    criterion = np.zeros((n_v, n_m))
    dprime_inv = np.zeros((n_v, n_m))
    criterion_inv = np.zeros((n_v, n_m))
    for vi in range(n_v):
        for mi in range(n_m):
            dprime[vi, mi], criterion[vi, mi] = MW._sdt_from_counts(
                np.asarray(response_count_valid[vi, mi]), np.asarray(false_alarm_count[vi]), TRIALS_PER_POINT
            )
            dprime_inv[vi, mi], criterion_inv[vi, mi] = MW._sdt_from_counts(
                np.asarray(response_count_invalid[vi, mi]), np.asarray(false_alarm_count[vi]), TRIALS_PER_POINT
            )

    result = {
        "label": name,
        "status": "ok",
        "checkpoint_path": str(path),
        "checkpoint_sha256": actual_sha,
        "checkpoint_iteration_logged": int(iteration),
        "iteration_note": spec["iteration_note"],
        "inject_memory_noise_at_eval": spec["inject_noise"],
        "validities": VALIDITIES,
        "magnitudes": MAGNITUDES,
        "response_rate_valid": (response_count_valid / TRIALS_PER_POINT).tolist(),
        "response_rate_invalid": (response_count_invalid / TRIALS_PER_POINT).tolist(),
        "false_alarm_rate": (false_alarm_count / TRIALS_PER_POINT).tolist(),
        "dprime_valid": dprime.tolist(),
        "criterion_valid": criterion.tolist(),
        "dprime_invalid": dprime_inv.tolist(),
        "criterion_invalid": criterion_inv.tolist(),
        "attention_near_18deg": {
            "cue_period_cued_image_mass": [float(x) for x in cue_period_cued_image],
            "cue_period_cued_memory_mass": [float(x) for x in cue_period_cued_memory],
            "change_period_target_image_mass": [float(x) for x in change_period_target_image],
            "change_period_target_memory_mass": [float(x) for x in change_period_target_memory],
            "note": "one value per displayed validity (0.25, 0.5, 0.75); uniform baseline = 0.25 per key",
        },
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"memory_noise_{name}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"[{name}] wrote {out_dir / f'memory_noise_{name}.json'}")
    return result


def main() -> None:
    out_dir = ROOT / "reports/vda_series/memory_noise_comparison_20260804"
    results = {name: run_condition(name, spec, out_dir) for name, spec in CONDITIONS.items()}
    (out_dir / "MANIFEST.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_dir / 'MANIFEST.json'}")


if __name__ == "__main__":
    main()
