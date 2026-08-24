from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from analysis import vda4_spatial_scaling_endpoint_replication as endpoint


def _json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _metadata(label: str, rows: int, cols: int, checkpoint_sha: str, producer_sha: str) -> dict[str, np.ndarray]:
    return {
        "meta_label": np.asarray(label),
        "meta_task": np.asarray("vda4"),
        "meta_feedback": np.asarray("crossattn1"),
        "meta_grid_rows": np.asarray(rows),
        "meta_grid_cols": np.asarray(cols),
        "meta_n_tokens": np.asarray(rows * cols),
        "meta_checkpoint_iteration": np.asarray(19999),
        "meta_checkpoint_path": np.asarray(f"fixture/{label}/rvit_paper_vda4_final.pt"),
        "meta_checkpoint_sha256": np.asarray(checkpoint_sha),
        "meta_producer_path": np.asarray("analysis/vda4_spatial_scaling_evaluation.py"),
        "meta_producer_sha256": np.asarray(producer_sha),
    }


def _region_and_token_mass(rows: int, cols: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    n_tokens = rows * cols
    if n_tokens == 4:
        valid_tl = 0.40 + 0.01 * seed
        invalid_tl = 0.44 - 0.01 * seed
        invalid_br = 0.34 + 0.01 * seed
    else:
        valid_tl = 0.62 + 0.01 * seed
        invalid_tl = 0.24 - 0.01 * seed
        invalid_br = 0.56 + 0.01 * seed
    valid_regions = np.asarray([valid_tl] + [(1.0 - valid_tl) / 3.0] * 3, dtype=np.float64)
    invalid_regions = np.asarray(
        [invalid_tl, (1.0 - invalid_tl - invalid_br) / 2.0,
         (1.0 - invalid_tl - invalid_br) / 2.0, invalid_br],
        dtype=np.float64,
    )
    region_mass = np.empty((2, 128, 7, 4), dtype=np.float64)
    region_mass[0, ...] = valid_regions
    region_mass[1, ...] = invalid_regions
    token_mass = np.zeros((2, 128, 7, n_tokens), dtype=np.float64)
    for region_index, tokens in enumerate(endpoint.expected_region_tokens(rows, cols)):
        token_mass[..., tokens] = region_mass[..., region_index, None] / len(tokens)
    return region_mass, token_mass


def _write_source(root: Path, rows: int, cols: int, seed: int) -> None:
    label = endpoint.source_label(rows, cols, seed)
    directory = root / label
    (directory / "data").mkdir(parents=True)
    (directory / "tables").mkdir()
    (directory / "figures").mkdir()
    checkpoint_sha = hashlib.sha256(f"checkpoint/{label}".encode()).hexdigest()
    producer_sha = "a" * 64
    model = {
        "label": label,
        "task": "vda4",
        "feedback": "crossattn1",
        "grid_rows": rows,
        "grid_cols": cols,
        "n_tokens": rows * cols,
        "checkpoint_iteration": 19999,
        "checkpoint_path": f"fixture/{label}/rvit_paper_vda4_final.pt",
        "checkpoint_sha256": checkpoint_sha,
        "producer_path": "analysis/vda4_spatial_scaling_evaluation.py",
        "producer_sha256": producer_sha,
    }
    config = {
        **model,
        "device": "cpu",
        "threads": 1,
        "psychometric_trials": 300,
        "attention_trials": 128,
        "intervention_trials": 250,
        "validities": endpoint.VALIDITIES.tolist(),
        "magnitudes": endpoint.MAGNITUDES.tolist(),
        "focal_magnitude": 30.0,
        "focal_validity": 1.0,
        "qualifying_frames": [5, 6],
        "region_tokens": endpoint.expected_region_tokens(rows, cols),
        "regional_uniform_baseline": 0.25,
        "checkpoint_producer_sha256": {"train_rl.py": "b" * 64},
    }
    _json(directory / "analysis_config.json", config)
    _json(
        directory / "SUMMARY.json",
        {"schema_version": 1, "model": model, "training_is_not_scientific_validation": True},
    )

    valid_counts = np.asarray([0, 30, 90, 150, 210, 240, 270, 285, 297, 300])
    invalid_counts = (
        np.asarray([0, 0, 30, 60, 150, 210, 240, 270, 285, 300])
        if rows == 2
        else np.asarray([0, 0, 0, 15, 45, 90, 150, 225, 270, 300])
    )
    response_count = np.empty((4, 10, 2), dtype=np.int64)
    response_count[..., 0] = valid_counts
    response_count[..., 1] = invalid_counts
    response_rate = response_count / 300.0
    mean_rt = np.full((4, 10, 2), 5.0, dtype=np.float64)
    mean_rt[..., 1] += (0.1 if rows == 2 else 0.25) + 0.01 * seed
    press_histogram = np.zeros((4, 10, 2, 8), dtype=np.int64)
    press_histogram[..., 0] = 300
    np.savez(
        directory / "data" / "psychometrics.npz",
        response_count=response_count,
        response_rate=response_rate,
        mean_rt=mean_rt,
        press_histogram=press_histogram,
        false_alarm_count=np.zeros((4, 2), dtype=np.int64),
        false_alarm_rate=np.zeros((4, 2), dtype=np.float64),
        false_alarm_histogram=np.zeros((4, 2, 8), dtype=np.int64),
        dprime=np.zeros((4, 10, 2), dtype=np.float64),
        criterion=np.zeros((4, 10, 2), dtype=np.float64),
        **_metadata(label, rows, cols, checkpoint_sha, producer_sha),
    )

    region_mass, token_mass = _region_and_token_mass(rows, cols, seed)
    np.savez(
        directory / "data" / "event_attention.npz",
        press=np.zeros((2, 128), dtype=np.int64),
        token_mass=token_mass,
        region_mass=region_mass,
        raw_attention_mean=np.zeros((2, 7, rows * cols, 2 * rows * cols), dtype=np.float32),
        **_metadata(label, rows, cols, checkpoint_sha, producer_sha),
    )

    regional_count = np.full((3, 5, 3), 125, dtype=np.int64)
    explicit_count = np.full((4, 3), 125, dtype=np.int64)
    explicit_count[0, 1] = (200 + 5 * seed) if rows == 2 else (225 + 5 * seed)
    explicit_count[3, 1] = 175 if rows == 2 else 125
    regional_histogram = np.zeros((3, 5, 3, 8), dtype=np.int64)
    regional_histogram[..., 0] = 250
    explicit_histogram = np.zeros((4, 3, 8), dtype=np.int64)
    explicit_histogram[..., 0] = 250
    np.savez(
        directory / "data" / "interventions.npz",
        response_count=regional_count,
        response_rate=regional_count / 250.0,
        mean_rt=np.full((3, 5, 3), 5.0),
        press_histogram=regional_histogram,
        dprime=np.zeros((3, 5, 3)),
        criterion=np.zeros((3, 5, 3)),
        achieved_change_region_mass=np.zeros((3, 5, 3)),
        achieved_target_region_mass=np.zeros((3, 5, 3)),
        explicit_modes=np.asarray(endpoint.EXPLICIT_MODES),
        explicit_response_count=explicit_count,
        explicit_response_rate=explicit_count / 250.0,
        explicit_mean_rt=np.full((4, 3), 5.0),
        explicit_press_histogram=explicit_histogram,
        explicit_dprime=np.zeros((4, 3)),
        explicit_criterion=np.zeros((4, 3)),
        shuffle_permutation=np.arange(2 * rows * cols, dtype=np.int64),
        **_metadata(label, rows, cols, checkpoint_sha, producer_sha),
    )

    for relative in sorted(endpoint.REQUIRED_ARTIFACTS):
        path = directory.joinpath(*relative.split("/"))
        if not path.exists():
            path.write_bytes(f"fixture artifact: {label}/{relative}\n".encode())
    hashes = {
        relative: endpoint.sha256_file(directory.joinpath(*relative.split("/")))
        for relative in sorted(endpoint.REQUIRED_ARTIFACTS)
    }
    _json(
        directory / "MANIFEST.json",
        {
            "schema_version": 1,
            "status": "complete",
            "model": model,
            "config_path": "analysis_config.json",
            "summary_path": "SUMMARY.json",
            "artifact_hashes": hashes,
        },
    )


@pytest.fixture
def production_root(tmp_path: Path) -> Path:
    root = tmp_path / "production"
    root.mkdir()
    for seed in endpoint.SEEDS:
        for rows, cols in endpoint.GRIDS:
            _write_source(root, rows, cols, seed)
    return root


def test_builds_hash_bound_immutable_directional_bundle(
    production_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_plot(path_stem: Path, rows: list[dict]) -> None:
        assert len(rows) == 4
        path_stem.with_suffix(".png").write_bytes(b"fixture png")
        path_stem.with_suffix(".pdf").write_bytes(b"fixture pdf")

    monkeypatch.setattr(endpoint, "plot_summary", fake_plot)
    output = tmp_path / "endpoint_synthesis"
    assert endpoint.main(["--production-root", str(production_root), "--output-root", str(output)]) == 0

    expected_outputs = {
        endpoint.METRICS_FILENAME,
        f"{endpoint.FIGURE_BASENAME}.png",
        f"{endpoint.FIGURE_BASENAME}.pdf",
        "SUMMARY.json",
    }
    assert {path.name for path in output.iterdir()} == expected_outputs | {"MANIFEST.json"}
    with (output / endpoint.METRICS_FILENAME).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 4
    assert [(int(row["seed"]), row["grid"]) for row in rows] == [
        (0, "2x2"), (0, "10x10"), (1, "2x2"), (1, "10x10")
    ]

    summary = json.loads((output / "SUMMARY.json").read_text(encoding="utf-8"))
    assert summary["n_training_seeds"] == 2
    assert summary["training_accuracy_used_as_attention_evidence"] is False
    threshold = summary["descriptive_replication_summary"]["threshold_cost_invalid_minus_valid_deg"]
    assert threshold["directional_agreement"] is True
    assert threshold["shared_direction"] == "increase"
    assert threshold["evidence_class"] == "directional_and_dispersion_only_n_equals_2"
    assert "confidence intervals or p-values" in summary["evidence_boundary"]["not_supported"]

    manifest = json.loads((output / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["source_scope_guard"]["expected_labels"] == endpoint.expected_source_labels()
    assert manifest["overwrite_protection"] == "refuse-existing-output"
    assert manifest["seed0_synthesis_outputs_modified"] is False
    assert set(manifest["outputs"]) == expected_outputs
    for name, evidence in manifest["outputs"].items():
        path = output / name
        assert path.stat().st_size == evidence["bytes"]
        assert endpoint.sha256_file(path) == evidence["sha256"]

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        endpoint.main(["--production-root", str(production_root), "--output-root", str(output)])


def test_validate_only_rejects_tampered_source_without_creating_output(production_root: Path) -> None:
    tampered = production_root / endpoint.source_label(10, 10, 1) / "tables" / "psychometrics.csv"
    tampered.write_text("tampered\n", encoding="utf-8")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        endpoint.main(["--production-root", str(production_root), "--validate-only"])
    assert not (production_root / "synthesis_crossattn1_endpoint_replication_seed0_seed1").exists()


def test_dispersion_summary_never_upgrades_two_seed_direction_to_inference() -> None:
    rows = []
    for seed, lo, hi in ((0, 1.0, 2.0), (1, 3.0, 2.0)):
        for tokens, value in ((4, lo), (100, hi)):
            row = {field: 0.0 for field in endpoint.CSV_FIELDS}
            row.update({"feedback": "crossattn1", "model": "Cross-attention", "grid": "2x2" if tokens == 4 else "10x10",
                        "n_tokens": tokens, "seed": seed, "source_manifest_sha256": "c" * 64})
            for metric in endpoint.DELTA_METRICS:
                row[metric] = value
            rows.append(row)
    deltas = endpoint.compute_seedwise_deltas(rows)
    summary = endpoint.summarize_delta_dispersion(deltas)
    item = summary["threshold_cost_invalid_minus_valid_deg"]
    assert item["directional_agreement"] is False
    assert item["shared_direction"] == "discordant"
    assert item["n_training_seeds"] == 2
    assert "confidence" not in item
    assert "p_value" not in item


def test_metrics_csv_round_trips_binary64_values(tmp_path: Path) -> None:
    value = 0.7480713129043579
    row = {field: value for field in endpoint.CSV_FIELDS}
    row.update({
        "feedback": "crossattn1",
        "model": "Cross-attention",
        "grid": "2x2",
        "n_tokens": 4,
        "seed": 0,
        "source_manifest_sha256": "a" * 64,
    })
    path = tmp_path / "metrics.csv"
    endpoint.write_metrics(path, [row])
    with path.open(newline="", encoding="utf-8") as handle:
        written = next(csv.DictReader(handle))
    assert float(written["valid_tl_region0_mass_frames5_6"]) == value
