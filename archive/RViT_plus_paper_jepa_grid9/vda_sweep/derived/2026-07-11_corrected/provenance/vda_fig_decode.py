"""Temporal decoding from recurrent memory with reproducible, balanced sampling.

Decode cue colour/value, displayed validity, change presence, and realized change
location from vec(H) at each timestep. Sampling is deterministic and balances
cued versus uncued changes for VDA2/VDA4/VDA9. VDA1 has no uncued location, so
its change-location decode is explicitly undefined (NaN).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

try:
    from . import vda_core as C
except ImportError:  # direct script execution
    import vda_core as C  # type: ignore[no-redef]

COLORS = ("red", "green", "blue")
PROPS = (0.25, 0.5, 0.75, 1.0)
N = 900
SEED = 20250707
SAMPLING_VERSION = 1
CV_FOLDS = 4
TASK_MIN_N = {"vda1": 16, "vda2": 16, "vda4": 48, "vda9": 128}
DECODER_TASKS = tuple(TASK_MIN_N)
FEEDBACKS = ("crossattn1", "affine_ew")
DECODED_VARIABLES = ("colour", "validity", "change", "chg_loc")
ACTIVE_LOCATIONS = {
    task: tuple(C.vda_task_metadata(task)["active_locations"])
    for task in DECODER_TASKS
}
CUE_LOCATIONS = {
    task: int(C.vda_task_metadata(task)["cue_index"])
    for task in DECODER_TASKS
}
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LEGACY_OUTPUT = (Path(C.FIGS) / "decode.npz").resolve()
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent
    / "derived"
    / "2026-07-11_corrected"
    / "decode.npz"
).resolve()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None, help=f"output NPZ (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--seed", type=int, default=SEED, help="sampling seed")
    parser.add_argument("--n", type=int, default=N, help="samples per task/feedback run")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="allow overwriting an existing corrected output (never implies legacy permission)",
    )
    parser.add_argument(
        "--dangerously-overwrite-legacy",
        action="store_true",
        help="allow overwriting the preserved legacy figs/decode.npz artifact",
    )
    return parser.parse_args(argv)


def resolve_output_path(out=None, allow_legacy=False, overwrite=False):
    """Normalize output identity and reject unsafe or unintended replacement."""
    requested = DEFAULT_OUTPUT if out is None else Path(out).expanduser()
    if not str(requested).endswith(".npz"):
        requested = Path(f"{requested}.npz")
    output = requested.resolve()

    is_legacy = output == LEGACY_OUTPUT
    if output.exists() and LEGACY_OUTPUT.exists():
        is_legacy = is_legacy or os.path.samefile(output, LEGACY_OUTPUT)
    if is_legacy and not allow_legacy:
        raise ValueError(
            f"refusing to overwrite legacy decoder artifact {LEGACY_OUTPUT}; "
            "choose a corrected-run output under vda_sweep/derived"
        )
    if output.exists() and not overwrite:
        raise FileExistsError(
            f"refusing to overwrite existing decoder output {output}; pass --overwrite"
        )
    return output


def sha256_file(path, chunk_size=1024 * 1024):
    """Hash checkpoint bytes without deserializing or executing their contents."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checkpoint_provenance(
    task, feedback, dm, checkpoint_path, iteration, n, seed, config,
    checkpoint_sha256=None,
):
    checkpoint_path = Path(checkpoint_path).resolve()
    return {
        "checkpoint_path_absolute": str(checkpoint_path),
        "checkpoint_path_relative": os.path.relpath(checkpoint_path, PROJECT_ROOT),
        "checkpoint_sha256": checkpoint_sha256 or sha256_file(checkpoint_path),
        "loaded_iteration": int(iteration),
        "task": task,
        "feedback": feedback,
        "model_identity": f"{task}:{feedback}:d_mem={int(dm)}",
        "d_mem": int(dm),
        "seed": int(seed),
        "n": int(n),
        "replay_config": config,
    }


def _balanced_indices(n, n_classes, rng):
    values = np.resize(np.arange(n_classes, dtype=np.int64), int(n))
    rng.shuffle(values)
    return values


def validate_sample_n(task, n):
    """Enforce conservative task-specific support minima for four-fold CV."""
    try:
        minimum = TASK_MIN_N[task]
    except KeyError as exc:
        raise ValueError(f"unknown decoder task {task!r}") from exc
    n = int(n)
    if n < minimum:
        raise ValueError(
            f"{task} decoder n must be at least {minimum} for cv={CV_FOLDS}; got {n}"
        )
    return n


def sample_conditions(task, n=N, seed=SEED):
    """Return deterministic conditions, decoder labels, and replay config.

    Half the trials are change trials. For tasks with more than one active
    location, changed trials are split as evenly as possible between cued and
    uncued changes; uncued locations are themselves distributed round-robin
    before shuffling so every active location has support.
    """
    n, seed = validate_sample_n(task, n), int(seed)

    cue = CUE_LOCATIONS[task]
    active = ACTIVE_LOCATIONS[task]
    if cue not in active:
        raise ValueError("task metadata cue_index must be active")

    rng = np.random.default_rng(seed)
    colour = _balanced_indices(n, len(COLORS), rng)
    validity = _balanced_indices(n, len(PROPS), rng)

    change = np.zeros(n, dtype=np.int64)
    change[: n // 2] = 1
    rng.shuffle(change)
    changed_rows = np.flatnonzero(change)
    change_index = np.full(n, -1, dtype=np.int64)

    uncued = tuple(i for i in active if i != cue)
    if not uncued:
        change_index[changed_rows] = cue
    else:
        n_cued = len(changed_rows) // 2
        is_cued = np.zeros(len(changed_rows), dtype=bool)
        is_cued[:n_cued] = True
        rng.shuffle(is_cued)
        change_index[changed_rows[is_cued]] = cue
        uncued_rows = changed_rows[~is_cued]
        uncued_class = _balanced_indices(len(uncued_rows), len(uncued), rng)
        change_index[uncued_rows] = np.asarray(uncued, dtype=np.int64)[uncued_class]

    chg_loc = np.where(change.astype(bool), change_index + 1, 0).astype(np.int64)
    cued_change = np.full(n, -1, dtype=np.int64)
    cued_change[changed_rows] = (change_index[changed_rows] == cue).astype(np.int64)

    conditions = {
        "colour": np.asarray(COLORS)[colour],
        "proportion": np.asarray(PROPS, dtype=np.float64)[validity],
        "change_true": change.copy(),
        "change_index": change_index,
    }
    labels = {
        "colour": colour,
        "validity": validity,
        "change": change,
        "chg_loc": chg_loc,
        "cued_change": cued_change,
    }
    config = {
        "sampling_version": SAMPLING_VERSION,
        "cv_folds": CV_FOLDS,
        "minimum_n": TASK_MIN_N[task],
        "task": task,
        "n": n,
        "seed": seed,
        "cue_index": cue,
        "active_locations": active,
        "location_decode_defined": bool(uncued),
        "change_trials": int(len(changed_rows)),
        "balance": "half change; changed trials half cued/half uncued when defined",
    }
    return conditions, labels, config


def collect(m, task, n=N, seed=SEED):
    conditions, labels, config = sample_conditions(task, n=n, seed=seed)

    video_rng = np.random.default_rng(seed)
    vids = [
        C.make_video(
            task,
            config["cue_index"],
            float(conditions["proportion"][i]),
            str(conditions["colour"][i]),
            int(conditions["change_true"][i]),
            int(conditions["change_index"][i]),
            18.0,
            seed=int(video_rng.integers(0, 2**32, dtype=np.uint32)),
        )
        for i in range(n)
    ]
    with torch.no_grad():
        cell = m.forward_rl_sequence(
            C._tens(vids).to(C.DEVICE), return_cell=True
        )["cell_seq"].cpu().numpy()
    return cell, labels, conditions, config


def dec(cell, y, t):
    X = cell[:, t].reshape(len(y), -1)
    return float(
        cross_val_score(
            LogisticRegression(max_iter=400, C=0.5),
            X,
            y,
            cv=4,
            scoring="balanced_accuracy",
        ).mean()
    )


def decode_timecourse(cell, y, defined=True):
    """Decode one label over time, or return NaNs for an undefined contrast."""
    if not defined:
        return np.full(cell.shape[1], np.nan, dtype=float)
    return np.asarray([dec(cell, y, t) for t in range(cell.shape[1])], dtype=float)


def main(argv=None):
    args = parse_args(argv)
    for task in DECODER_TASKS:
        validate_sample_n(task, args.n)
    output_path = resolve_output_path(
        args.out,
        allow_legacy=args.dangerously_overwrite_legacy,
        overwrite=args.overwrite,
    )
    out = {}
    for task in DECODER_TASKS:
        for fb in FEEDBACKS:
            dm = 128
            checkpoint = C.ckpt(task, fb, dm)
            if not checkpoint:
                raise FileNotFoundError(f"no checkpoint for {task} {fb} d{dm}")
            checkpoint_path = Path(checkpoint).expanduser().resolve()
            checkpoint_sha256 = sha256_file(checkpoint_path)
            m, it = C.load(
                task, fb, dm, checkpoint_path=str(checkpoint_path)
            )
            cell, labels, conditions, config = collect(
                m, task, n=args.n, seed=args.seed
            )
            print(
                f"=== {task} {fb} — balanced-accuracy of decoding from memory H, "
                "per timestep (t0..t6) ==="
            )
            for var in DECODED_VARIABLES:
                defined = var != "chg_loc" or config["location_decode_defined"]
                accs = decode_timecourse(cell, labels[var], defined=defined)
                out[f"{task}_{fb}_{var}"] = accs
                if defined:
                    chance = 1.0 / len(np.unique(labels[var]))
                    chance_text = f"{chance:.2f}"
                else:
                    chance_text = "undefined"
                print(
                    f"  {var:9s} (chance {chance_text}): "
                    + " ".join("nan" if np.isnan(a) else f"{a:.2f}" for a in accs),
                    flush=True,
                )

            out[f"{task}_{fb}_provenance_json"] = np.asarray(
                json.dumps(
                    checkpoint_provenance(
                        task,
                        fb,
                        dm,
                        checkpoint_path,
                        it,
                        args.n,
                        args.seed,
                        config,
                        checkpoint_sha256=checkpoint_sha256,
                    ),
                    sort_keys=True,
                )
            )

            # Same seed/config is replayed for both feedback variants. setdefault
            # stores one provenance copy per task rather than redundant duplicates.
            out.setdefault(
                f"{task}_sample_config_json",
                np.asarray(json.dumps(config, sort_keys=True)),
            )
            for name, values in labels.items():
                out.setdefault(f"{task}_sample_label_{name}", values)
            out.setdefault(f"{task}_sample_change_index", conditions["change_index"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(output_path, **out)
    print(f"[decode] saved {output_path}", flush=True)
    return output_path


if __name__ == "__main__":
    main()
