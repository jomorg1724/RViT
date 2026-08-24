"""Independently verify a VDA16 affine three-location intervention artifact."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import norm


EXPECTED_CHECKPOINT_SHA256 = "52141da629e2c7f8f902826196067efbadb924608eecde7560559fdc0f813233"
EXPECTED_ADMISSION_SHA256 = "724cf10b92ead6f34772c28ff236169e54d39b500154cbc3305fb35bc1689239"
DOSES = np.asarray([0.0, 0.25, 0.5, 0.75, 1.0], dtype=np.float64)
ROLES = ("change", "cued", "control")
TARGETS = {"change": 15, "cued": 0, "control": 5}
MASS_FIELDS = {
    "change": "achieved_change_mass_t6",
    "cued": "achieved_cued_mass_t6",
    "control": "achieved_control_mass_t6",
}
TRIALS = 300
TIMESTEPS = 7
LOCATIONS = 16


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def finite_or_none(value: float) -> float | None:
    return value if math.isfinite(value) else None


def assert_close(actual: Any, expected: Any, label: str, atol: float = 1e-12) -> None:
    if expected is None:
        if actual is not None:
            raise AssertionError(f"{label}: expected null, got {actual!r}")
        return
    if actual is None or not math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=atol):
        raise AssertionError(f"{label}: {actual!r} != {expected!r}")


def sdt(hit_count: int, false_alarm_count: int) -> tuple[float, float]:
    lower, upper = 1.0 / (2 * TRIALS), 1.0 - 1.0 / (2 * TRIALS)
    hit = float(np.clip(hit_count / TRIALS, lower, upper))
    false_alarm = float(np.clip(false_alarm_count / TRIALS, lower, upper))
    z_hit, z_false_alarm = float(norm.ppf(hit)), float(norm.ppf(false_alarm))
    return z_hit - z_false_alarm, -0.5 * (z_hit + z_false_alarm)


def verify_pdf(path: Path) -> None:
    if path.stat().st_size < 1_000 or path.read_bytes()[:5] != b"%PDF-":
        raise AssertionError(f"invalid PDF artifact: {path}")
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    if len(reader.pages) != 1:
        raise AssertionError(f"expected one-page figure PDF: {path}")
    box = reader.pages[0].mediabox
    if float(box.width) <= 100 or float(box.height) <= 100:
        raise AssertionError(f"implausible PDF page dimensions: {path}")


def verify_png(path: Path) -> None:
    from PIL import Image

    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        if image.width < 1_000 or image.height < 800:
            raise AssertionError(f"figure PNG is unexpectedly small: {path} {image.size}")


def verify(output_root: Path) -> dict[str, Any]:
    manifest_path = output_root / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "complete_pending_independent_verification":
        raise AssertionError("producer manifest does not declare completed production")
    if manifest.get("checkpoint_sha256") != EXPECTED_CHECKPOINT_SHA256:
        raise AssertionError("manifest checkpoint hash mismatch")
    if manifest.get("checkpoint_admission_sha256") != EXPECTED_ADMISSION_SHA256:
        raise AssertionError("manifest admission hash mismatch")

    hashes = manifest.get("artifact_hashes")
    if not isinstance(hashes, dict) or not hashes:
        raise AssertionError("manifest lacks artifact hashes")
    for relative, expected_hash in hashes.items():
        path = output_root / relative
        if not path.is_file() or sha256_file(path) != expected_hash:
            raise AssertionError(f"artifact hash mismatch: {relative}")
    actual_files = {
        str(path.relative_to(output_root)).replace("\\", "/")
        for path in output_root.rglob("*")
        if path.is_file()
        and path.name not in ("MANIFEST.json", "VALIDATION_RESULT.json", "VERIFIED_MANIFEST.json")
    }
    if actual_files != set(hashes):
        raise AssertionError(f"artifact inventory mismatch: missing={set(hashes)-actual_files}, extra={actual_files-set(hashes)}")

    config = json.loads((output_root / "analysis_config.json").read_text(encoding="utf-8"))
    if config["device"] not in ("cpu", "cuda") or config["protocol"]["trials_per_condition"] != TRIALS:
        raise AssertionError("analysis configuration violates the registered protocol")
    admission_path = output_root / "provenance/CHECKPOINT_ADMISSION.json"
    if sha256_file(admission_path) != EXPECTED_ADMISSION_SHA256:
        raise AssertionError("frozen checkpoint admission differs from the registered file")
    admission = json.loads(admission_path.read_text(encoding="utf-8"))
    for key, value in {
        "checkpoint_sha256": EXPECTED_CHECKPOINT_SHA256,
        "checkpoint_iteration": 19999,
        "task": "vda16",
        "feedback": "affine_ew",
        "width": 128,
        "seed": 0,
        "grid": [4, 4],
    }.items():
        if admission.get(key) != value:
            raise AssertionError(f"frozen admission field mismatch: {key}")

    inner_summary = json.loads((output_root / "vda16/data/summary.json").read_text(encoding="utf-8"))
    if inner_summary.get("status") != "ok" or inner_summary.get("checkpoint_iteration") != 19999:
        raise AssertionError("inner result does not describe a terminal successful evaluation")
    if inner_summary.get("feedback") != "affine_ew" or inner_summary.get("trials_per_condition") != TRIALS:
        raise AssertionError("inner result architecture/protocol mismatch")
    npz_path = output_root / "vda16/data/change_location_intervention.npz"
    expected_npz_keys = {"doses", "metadata_json"}
    for role in ROLES:
        for dose in DOSES:
            prefix = f"{role}_dose{float(dose)}"
            expected_npz_keys.update(
                {f"{prefix}_invalid_press", f"{prefix}_nochange_press", f"{prefix}_invalid_mass"}
            )

    recomputed: dict[str, dict[str, list[float | None]]] = {}
    with np.load(npz_path, allow_pickle=False) as payload:
        if set(payload.files) != expected_npz_keys:
            raise AssertionError(f"NPZ key contract mismatch: {set(payload.files) ^ expected_npz_keys}")
        np.testing.assert_array_equal(payload["doses"], DOSES)
        archived_metadata = json.loads(str(payload["metadata_json"].item()))
        if archived_metadata.get("checkpoint_sha256") != EXPECTED_CHECKPOINT_SHA256:
            raise AssertionError("NPZ metadata is not checkpoint-bound")

        natural_reference: tuple[np.ndarray, np.ndarray, np.ndarray] | None = None
        for role in ROLES:
            metrics: dict[str, list[float | None]] = {
                "response_rate": [],
                "false_alarm_rate": [],
                "dprime": [],
                "criterion": [],
                "conditional_mean_response_frame": [],
                "achieved_change_mass_t6": [],
                "achieved_cued_mass_t6": [],
                "achieved_control_mass_t6": [],
            }
            target_mass = []
            for dose in DOSES:
                prefix = f"{role}_dose{float(dose)}"
                invalid_press = np.asarray(payload[f"{prefix}_invalid_press"])
                nochange_press = np.asarray(payload[f"{prefix}_nochange_press"])
                mass = np.asarray(payload[f"{prefix}_invalid_mass"], dtype=np.float64)
                if invalid_press.shape != (TRIALS,) or nochange_press.shape != (TRIALS,):
                    raise AssertionError(f"press-array shape mismatch: {prefix}")
                if not np.issubdtype(invalid_press.dtype, np.integer) or not np.issubdtype(nochange_press.dtype, np.integer):
                    raise AssertionError(f"press arrays are not integer: {prefix}")
                if np.any((invalid_press < -1) | (invalid_press >= TIMESTEPS)) or np.any(
                    (nochange_press < -1) | (nochange_press >= TIMESTEPS)
                ):
                    raise AssertionError(f"press frame outside -1..6: {prefix}")
                if mass.shape != (TRIALS, TIMESTEPS, LOCATIONS) or not np.isfinite(mass).all():
                    raise AssertionError(f"attention-mass contract mismatch: {prefix}")
                if np.any(mass < -1e-8):
                    raise AssertionError(f"negative attention mass: {prefix}")
                np.testing.assert_allclose(mass.sum(axis=-1), 1.0, rtol=0.0, atol=2e-6)

                hit_mask = np.isin(invalid_press, (5, 6))
                hit_count = int(hit_mask.sum())
                false_alarm_count = int((nochange_press >= 0).sum())
                dprime, criterion = sdt(hit_count, false_alarm_count)
                metrics["response_rate"].append(hit_count / TRIALS)
                metrics["false_alarm_rate"].append(false_alarm_count / TRIALS)
                metrics["dprime"].append(dprime)
                metrics["criterion"].append(criterion)
                metrics["conditional_mean_response_frame"].append(
                    finite_or_none(float(invalid_press[hit_mask].mean()) if hit_count else float("nan"))
                )
                mean_t6 = mass[:, 6, :].mean(axis=0)
                metrics["achieved_change_mass_t6"].append(float(mean_t6[15]))
                metrics["achieved_cued_mass_t6"].append(float(mean_t6[0]))
                metrics["achieved_control_mass_t6"].append(float(mean_t6[5]))
                target_mass.append(float(mean_t6[TARGETS[role]]))

                if dose == 0.5:
                    current = (invalid_press.copy(), nochange_press.copy(), mass.copy())
                    if natural_reference is None:
                        natural_reference = current
                    else:
                        for actual, expected in zip(current, natural_reference):
                            np.testing.assert_array_equal(actual, expected)
            if not np.all(np.diff(np.asarray(target_mass)) > 0.0):
                raise AssertionError(f"achieved target mass is not strictly dose-monotonic for {role}")
            recomputed[role] = metrics

    for role in ROLES:
        recorded = inner_summary["metrics"][role]
        for metric, values in recomputed[role].items():
            if len(recorded[metric]) != len(values):
                raise AssertionError(f"metric length mismatch: {role}/{metric}")
            for index, expected in enumerate(values):
                assert_close(recorded[metric][index], expected, f"{role}/{metric}/{index}", atol=2e-12)

    rows = list(csv.DictReader((output_root / "vda16/data/curves.csv").open(encoding="utf-8", newline="")))
    if len(rows) != len(ROLES) * len(DOSES):
        raise AssertionError("curve table must contain exactly 15 rows")
    for row in rows:
        role, dose = row["role"], float(row["dose"])
        index = int(np.flatnonzero(np.isclose(DOSES, dose))[0])
        for metric, values in recomputed[role].items():
            actual = float(row[metric])
            expected = values[index]
            if expected is None:
                if not math.isnan(actual):
                    raise AssertionError(f"CSV nonfinite mismatch: {role}/{dose}/{metric}")
            elif not math.isclose(actual, float(expected), rel_tol=0.0, abs_tol=2e-12):
                raise AssertionError(f"CSV metric mismatch: {role}/{dose}/{metric}")

    figure_root = output_root / "vda16/figures"
    for stem in ("vda16_change_location_intervention_summary", "vda16_change_location_attention_trajectory"):
        verify_pdf(figure_root / f"{stem}.pdf")
        verify_png(figure_root / f"{stem}.png")

    top_summary = json.loads((output_root / "SUMMARY.json").read_text(encoding="utf-8"))
    if top_summary.get("status") != "complete_pending_independent_verification":
        raise AssertionError("top summary status mismatch")
    for role in ROLES:
        effect = top_summary["effects"][role]
        values = recomputed[role]
        assert_close(effect["response_rate_suppress"], values["response_rate"][0], f"effect/{role}/suppress")
        assert_close(effect["response_rate_natural"], values["response_rate"][2], f"effect/{role}/natural")
        assert_close(effect["response_rate_boost"], values["response_rate"][4], f"effect/{role}/boost")
        assert_close(
            effect["response_rate_boost_minus_suppress"],
            float(values["response_rate"][4]) - float(values["response_rate"][0]),
            f"effect/{role}/response_delta",
        )

    return {
        "schema_version": 1,
        "status": "pass",
        "verifier_path": str(Path(__file__).resolve()),
        "verifier_sha256": sha256_file(Path(__file__).resolve()),
        "producer_manifest_path": str(manifest_path.resolve()),
        "producer_manifest_sha256": sha256_file(manifest_path),
        "artifact_hash_count": len(hashes),
        "semantic_checks": {
            "npz_exact_key_contract": True,
            "all_press_arrays_shape_dtype_range_valid": True,
            "all_attention_mass_arrays_finite_normalized": True,
            "natural_common_random_number_outputs_exact_across_roles": True,
            "all_120_recorded_metrics_recomputed": True,
            "all_15_csv_rows_recomputed": True,
            "all_role_target_masses_strictly_dose_monotonic": True,
            "two_pdf_figures_parse_as_single_pages": True,
            "two_png_figures_decode_at_expected_resolution": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_root", type=Path)
    args = parser.parse_args()
    output_root = args.output_root.expanduser().resolve()
    result = verify(output_root)
    validation_path = output_root / "VALIDATION_RESULT.json"
    validation_path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    verified_manifest = {
        "schema_version": 1,
        "status": "complete_verified",
        "producer_manifest_path": "MANIFEST.json",
        "producer_manifest_sha256": result["producer_manifest_sha256"],
        "validation_result_path": "VALIDATION_RESULT.json",
        "validation_result_sha256": sha256_file(validation_path),
        "checkpoint_sha256": EXPECTED_CHECKPOINT_SHA256,
        "artifact_hash_count": result["artifact_hash_count"],
    }
    (output_root / "VERIFIED_MANIFEST.json").write_text(
        json.dumps(verified_manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
