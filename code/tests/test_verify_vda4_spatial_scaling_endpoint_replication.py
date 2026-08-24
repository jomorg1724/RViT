from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import pytest

from analysis import verify_vda4_spatial_scaling_endpoint_replication as V


matplotlib.use("Agg")


def metric_row(seed: int, grid: str, offset: float = 0.0) -> dict[str, object]:
    tokens = 4 if grid == "2x2" else 100
    numeric = {
        "displayed_validity": 1.0,
        "valid_threshold_deg": 10.0 + offset,
        "invalid_threshold_deg": 15.0 + offset,
        "threshold_cost_invalid_minus_valid_deg": 5.0 + offset,
        "normalized_response_auc_valid_minus_invalid": 0.1 + offset,
        "rt30_invalid_minus_valid_frames": 0.2 + offset,
        "valid_tl_region0_mass_frames5_6": 0.7 + offset,
        "invalid_br_region3_mass_frames5_6": 0.5 + offset,
        "invalid_tl_region0_mass_frames5_6": 0.3 + offset,
        "invalid_reorienting_br_minus_tl_mass_frames5_6": 0.2 + offset,
        "explicit_natural_invalid_response_rate": 0.9 + offset,
        "explicit_uniform_invalid_response_rate": 0.8 + offset,
        "explicit_shuffle_invalid_response_rate": 0.7 + offset,
        "explicit_disable_invalid_response_rate": 0.6 + offset,
        "causal_dependence_natural_minus_disable_pp": 30.0 + offset,
    }
    return {
        "feedback": "crossattn1",
        "model": "Cross-attention",
        "grid": grid,
        "n_tokens": tokens,
        "seed": seed,
        **numeric,
        "source_manifest_sha256": f"{seed + tokens:064x}",
    }


def test_source_scope_is_exactly_two_endpoints_by_two_seeds() -> None:
    assert V.expected_source_labels() == {
        "vda4_crossattn1_grid2x2_seed0",
        "vda4_crossattn1_grid10x10_seed0",
        "vda4_crossattn1_grid2x2_seed1",
        "vda4_crossattn1_grid10x10_seed1",
    }


def test_bundle_location_rejects_seed0_reuse_and_overwrite(tmp_path: Path) -> None:
    production = tmp_path / "production"
    production.mkdir()
    good = production / "synthesis_endpoint_replication"
    good.mkdir()
    V.validate_bundle_location(production.resolve(), good.resolve(), V.Audit())

    seed0 = production / "synthesis_seed0_v3"
    seed0.mkdir()
    with pytest.raises(V.VerificationError, match="seed-0 synthesis"):
        V.validate_bundle_location(production.resolve(), seed0.resolve(), V.Audit())

    with pytest.raises(V.VerificationError, match="must not overwrite"):
        V.validate_bundle_location(production.resolve(), production.resolve(), V.Audit())

    unrelated = production / "summary"
    unrelated.mkdir()
    with pytest.raises(V.VerificationError, match="endpoint-replication scoped"):
        V.validate_bundle_location(production.resolve(), unrelated.resolve(), V.Audit())


def test_hash_verification_recomputes_bytes_and_digest(tmp_path: Path) -> None:
    path = tmp_path / "artifact.bin"
    path.write_bytes(b"verified evidence")
    evidence = {"sha256": V.sha256_file(path), "bytes": path.stat().st_size}
    audit = V.Audit()
    assert V.verify_hash_and_bytes(path, evidence, audit, "fixture") == evidence
    assert audit.hashes_verified == 1

    path.write_bytes(b"tampered evidence")
    with pytest.raises(V.VerificationError, match="mismatch"):
        V.verify_hash_and_bytes(path, evidence, V.Audit(), "fixture")


def test_json_reader_rejects_duplicate_keys_and_nonfinite_values(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"status": "complete", "status": "failed"}', encoding="utf-8")
    with pytest.raises(V.VerificationError, match="duplicate JSON key"):
        V.read_json(duplicate, V.Audit())

    nonfinite = tmp_path / "nonfinite.json"
    nonfinite.write_text('{"metric": NaN}', encoding="utf-8")
    with pytest.raises(V.VerificationError, match="non-finite JSON"):
        V.read_json(nonfinite, V.Audit())


def test_metric_rows_and_seedwise_deltas_are_recomputed() -> None:
    expected = metric_row(1, "10x10", offset=0.25)
    csv_shaped = {key: str(value) for key, value in expected.items()}
    V.compare_metric_row(csv_shaped, expected, V.Audit(), "fixture")

    tampered = dict(csv_shaped)
    tampered["invalid_tl_region0_mass_frames5_6"] = "0.99"
    with pytest.raises(V.VerificationError, match="invalid_tl_region0_mass_frames5_6 mismatch"):
        V.compare_metric_row(tampered, expected, V.Audit(), "fixture")

    metrics = {
        (seed, grid): metric_row(seed, grid, offset=(0.5 if grid == "10x10" else 0.0) + seed)
        for seed in V.SEEDS
        for grid in ("2x2", "10x10")
    }
    deltas = V.expected_deltas(metrics)
    assert [row["seed"] for row in deltas] == [0, 1]
    for row in deltas:
        assert row["delta_10x10_minus_2x2_threshold_cost_invalid_minus_valid_deg"] == pytest.approx(0.5)
        V.compare_delta_row(row, row, V.Audit(), f"seed{row['seed']}")

    bad_delta = dict(deltas[0])
    bad_delta["delta_10x10_minus_2x2_rt30_invalid_minus_valid_frames"] += 0.1
    with pytest.raises(V.VerificationError, match="rt30_invalid_minus_valid_frames mismatch"):
        V.compare_delta_row(bad_delta, deltas[0], V.Audit(), "seed0")

    dispersion = V.expected_dispersion(deltas)
    V.compare_dispersion(dispersion, dispersion, V.Audit())
    tampered_dispersion = json.loads(json.dumps(dispersion))
    tampered_dispersion["normalized_response_auc_valid_minus_invalid"]["mean_delta_descriptive_only"] += 0.2
    with pytest.raises(V.VerificationError, match="mean_delta_descriptive_only mismatch"):
        V.compare_dispersion(tampered_dispersion, dispersion, V.Audit())


def test_png_and_pdf_are_decoded_not_merely_present(tmp_path: Path) -> None:
    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(7, 4))
    axis.plot([0, 1, 2], [0, 1, 0])
    axis.set_title("Endpoint replication verification figure")
    axis.set_xlabel("tokens")
    axis.set_ylabel("held-out metric")
    png = tmp_path / "figure.png"
    pdf = tmp_path / "figure.pdf"
    figure.savefig(png, dpi=120)
    figure.savefig(pdf)
    plt.close(figure)

    audit = V.Audit()
    V.validate_png(png, audit, "fixture PNG")
    V.validate_pdf(pdf, audit, "fixture PDF")
    assert audit.figures_decoded == 2

    corrupt_png = tmp_path / "corrupt.png"
    corrupt_png.write_bytes(png.read_bytes()[:100])
    with pytest.raises(V.VerificationError, match="unreadable PNG"):
        V.validate_png(corrupt_png, V.Audit(), "corrupt PNG")

    blank_pdf = tmp_path / "blank.pdf"
    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with blank_pdf.open("wb") as handle:
        writer.write(handle)
    with pytest.raises(V.VerificationError, match="no content stream|too little readable text"):
        V.validate_pdf(blank_pdf, V.Audit(), "blank PDF")


def test_cli_contract_has_no_write_or_output_argument() -> None:
    parser = V.build_parser()
    destinations = {action.dest for action in parser._actions}
    assert destinations == {"help", "production_root", "bundle_root"}
