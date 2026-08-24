"""Checkpoint-recomputed psychometric sweep for the VDA4-on-a-4x4-grid discretization checkpoint.

Produces an NPZ in the exact schema ``psychometric_fits.py`` already expects
(``response_rate_valid/invalid``, ``response_count_valid/invalid``, ``change_magnitudes``,
``displayed_validities``, ...), matching the standard-geometry VDA4 and VDA16 producers, so
the existing logistic-fit and plotting code can be reused unmodified. The only new logic is
loading a checkpoint whose embedded grid (4x4, 16 patch tokens) does not match this task's
registered default (2x2) -- ``vda_core.load``'s built-in metadata validator does not know
about that override, so it is bypassed for this one checkpoint after the SHA-256 is verified
independently first.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vda_sweep import vda_core as core

MAGNITUDES = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 22.0, 26.0, 30.0]
VALIDITIES = [0.25, 0.5, 0.75, 1.0]
TRIALS_PER_POINT = 300
CUE_INDEX = 0
VALID_CHANGE_INDEX = 0
INVALID_CHANGE_INDEX = 3
SEED_BASE = 20270726


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint-path", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    actual_sha = sha256_file(args.checkpoint_path)
    if actual_sha != args.expected_sha256:
        raise RuntimeError(f"checkpoint SHA-256 mismatch: {actual_sha} != {args.expected_sha256}")

    model, iteration = core.load(
        "vda4", "crossattn1", 128, checkpoint_path=str(args.checkpoint_path), validate_metadata=False
    )
    print(f"loaded checkpoint at iteration {iteration} (grid-override, metadata validation bypassed)")

    n_v, n_m = len(VALIDITIES), len(MAGNITUDES)
    response_count_valid = np.zeros((n_v, n_m), dtype=int)
    response_count_invalid = np.zeros((n_v, n_m), dtype=int)
    seed_counter = 0
    for vi, validity in enumerate(VALIDITIES):
        for mi, mag in enumerate(MAGNITUDES):
            press_valid = core.press_times_clamp(
                model, "vda4", CUE_INDEX, validity, "red", 1, VALID_CHANGE_INDEX, mag,
                clamp=None, B=TRIALS_PER_POINT, seed=SEED_BASE + seed_counter,
            )
            seed_counter += 1
            press_invalid = core.press_times_clamp(
                model, "vda4", CUE_INDEX, validity, "red", 1, INVALID_CHANGE_INDEX, mag,
                clamp=None, B=TRIALS_PER_POINT, seed=SEED_BASE + seed_counter,
            )
            seed_counter += 1
            response_count_valid[vi, mi] = int(np.isin(press_valid, (5, 6)).sum())
            response_count_invalid[vi, mi] = int(np.isin(press_invalid, (5, 6)).sum())
        print(f"validity={validity:.2f} done: valid_counts={response_count_valid[vi].tolist()} invalid_counts={response_count_invalid[vi].tolist()}")

    response_rate_valid = response_count_valid / TRIALS_PER_POINT
    response_rate_invalid = response_count_invalid / TRIALS_PER_POINT

    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.output,
        response_rate_valid=response_rate_valid,
        response_rate_invalid=response_rate_invalid,
        response_count_valid=response_count_valid,
        response_count_invalid=response_count_invalid,
        change_magnitudes=np.asarray(MAGNITUDES),
        displayed_validities=np.asarray(VALIDITIES),
        point_seeds=np.zeros((n_v, n_m)),
        task=np.asarray("vda4"),
        feedback=np.asarray("crossattn1"),
        checkpoint_iteration=np.asarray(iteration),
        checkpoint_path=np.asarray(str(args.checkpoint_path)),
        checkpoint_sha256=np.asarray(actual_sha),
        producer_path=np.asarray(str(Path(__file__).resolve())),
        producer_sha256=np.asarray(sha256_file(Path(__file__).resolve())),
        trials_per_point=np.asarray(TRIALS_PER_POINT),
        cue_index=np.asarray(CUE_INDEX),
        valid_change_index=np.asarray(VALID_CHANGE_INDEX),
        invalid_change_index=np.asarray(INVALID_CHANGE_INDEX),
        cue_color=np.asarray("red"),
        qualifying_response_frame=np.asarray(5),
        grid=np.asarray([4, 4]),
        note=np.asarray("vda4 task on a 4x4/16-token patch grid override (spatial-discretization test)"),
    )
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
