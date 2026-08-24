from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pytest

from scripts import build_corrected_decoder as B


def _write_complete_archive(path: Path, *, n: int = 128, seed: int = 17) -> None:
    out: dict[str, np.ndarray] = {}
    for task in B.DECODER_TASKS:
        active = B.ACTIVE_LOCATIONS[task]
        change = np.zeros(n, dtype=np.int64)
        change[: n // 2] = 1
        change_index = np.full(n, -1, dtype=np.int64)
        changed = np.flatnonzero(change)
        if len(active) == 1:
            change_index[changed] = active[0]
        else:
            values = np.resize(np.asarray(active, dtype=np.int64), len(changed))
            change_index[changed] = values
        labels = {
            "colour": np.arange(n, dtype=np.int64) % 3,
            "validity": np.arange(n, dtype=np.int64) % 4,
            "change": change,
            "chg_loc": np.where(change == 1, change_index + 1, 0),
            "cued_change": np.where(change == 1, (change_index == active[0]).astype(np.int64), -1),
        }
        config = {
            "sampling_version": 1,
            "cv_folds": 4,
            "task": task,
            "n": n,
            "seed": seed,
            "cue_index": active[0],
            "active_locations": list(active),
            "location_decode_defined": len(active) > 1,
        }
        out[f"{task}_sample_config_json"] = np.asarray(json.dumps(config, sort_keys=True))
        for name, values in labels.items():
            out[f"{task}_sample_label_{name}"] = values
        out[f"{task}_sample_change_index"] = change_index
        for feedback in B.FEEDBACKS:
            for variable in B.DECODED_VARIABLES:
                values = np.full(7, 0.5, dtype=float)
                if task == "vda1" and variable == "chg_loc":
                    values[:] = np.nan
                out[f"{task}_{feedback}_{variable}"] = values
            provenance = {
                "task": task,
                "feedback": feedback,
                "n": n,
                "seed": seed,
                "d_mem": 128,
                "loaded_iteration": 19999,
                "checkpoint_path_absolute": f"/tmp/{task}_{feedback}.pt",
                "checkpoint_sha256": "a" * 64,
                "replay_config": config,
            }
            out[f"{task}_{feedback}_provenance_json"] = np.asarray(
                json.dumps(provenance, sort_keys=True)
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, **out)


def test_validate_archive_accepts_complete_schema_and_rejects_unmanifested_key(tmp_path):
    archive = tmp_path / "decode.npz"
    _write_complete_archive(archive)

    summary = B.validate_decode_archive(archive, expected_n=128, expected_seed=17)

    assert summary["key_count"] == 68
    assert summary["tasks"] == list(B.DECODER_TASKS)
    assert summary["feedbacks"] == list(B.FEEDBACKS)
    assert summary["location_class_counts"]["vda1"] == {"0": 64, "1": 64}
    assert min(summary["location_class_counts"]["vda9"].values()) >= 4

    with np.load(archive) as data:
        payload = {name: data[name] for name in data.files}
    payload["unmanifested"] = np.asarray([1])
    np.savez(archive, **payload)

    with pytest.raises(ValueError, match="exact key inventory"):
        B.validate_decode_archive(archive, expected_n=128, expected_seed=17)


def test_fresh_run_publication_requires_exact_regular_unique_inode_inventory(tmp_path):
    root = tmp_path / "corrected-run"
    manifest, temporary = B.prepare_fresh_run(root)
    data = root / "data" / "decode.npz"
    snapshot = root / "provenance" / "builder.py"
    data.parent.mkdir()
    snapshot.parent.mkdir()
    data.write_bytes(b"decode")
    snapshot.write_bytes(b"builder")
    temporary.write_text(json.dumps({"schema_version": 1}))

    extra = root / "extra.txt"
    extra.write_text("not admitted")
    with pytest.raises(RuntimeError, match="inventory mismatch"):
        B.publish_manifest_with_inventory(root, temporary, manifest, {data, snapshot})
    extra.unlink()

    B.publish_manifest_with_inventory(root, temporary, manifest, {data, snapshot})
    assert B.regular_run_files(root) == {data, snapshot, manifest}
    with pytest.raises(FileExistsError, match="fresh versioned root"):
        B.prepare_fresh_run(root)


def test_regular_inventory_rejects_symlink_and_hard_link_aliases(tmp_path):
    symlink_root = tmp_path / "symlink-run"
    symlink_root.mkdir()
    target = symlink_root / "target"
    target.write_bytes(b"same")
    (symlink_root / "alias").symlink_to(target)
    with pytest.raises(RuntimeError, match="symlink or special"):
        B.regular_run_files(symlink_root)

    hardlink_root = tmp_path / "hardlink-run"
    hardlink_root.mkdir()
    target = hardlink_root / "target"
    target.write_bytes(b"same")
    os.link(target, hardlink_root / "alias")
    with pytest.raises(RuntimeError, match="hard-link alias"):
        B.regular_run_files(hardlink_root)


def test_capture_executable_sources_freezes_the_complete_local_graph():
    sources = B.capture_executable_sources()
    assert set(sources) == {"__builder__", "__producer__", *B.PRODUCER_DEPENDENCIES}
    B.assert_executable_sources_unchanged(sources)

    tampered = dict(sources)
    tampered["__producer__"] += b"\n# tampered after startup\n"
    with pytest.raises(RuntimeError, match="changed after startup capture"):
        B.assert_executable_sources_unchanged(tampered)


def test_checkpoint_records_are_complete_distinct_and_rehashed(tmp_path):
    records = []
    for task in B.DECODER_TASKS:
        for feedback in B.FEEDBACKS:
            checkpoint = tmp_path / f"{task}_{feedback}.pt"
            checkpoint.write_bytes(f"{task}/{feedback}".encode())
            records.append(
                {
                    "task": task,
                    "feedback": feedback,
                    "checkpoint_path_absolute": str(checkpoint),
                    "checkpoint_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
                    "loaded_iteration": 19999,
                }
            )

    validated = B.validate_checkpoint_records(records)
    assert len(validated) == 8
    assert len({record["checkpoint_sha256"] for record in validated}) == 8

    Path(records[-1]["checkpoint_path_absolute"]).write_bytes(b"mutated")
    with pytest.raises(RuntimeError, match="changed during decoding"):
        B.validate_checkpoint_records(records)
