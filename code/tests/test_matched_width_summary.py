from __future__ import annotations

from pathlib import Path

import numpy as np
import torch

from scripts import build_matched_width_summary as S


def test_width_difference_is_d256_minus_d128() -> None:
    d128 = np.array([0.2, 0.5, 0.9])
    d256 = np.array([0.1, 0.7, 1.0])
    np.testing.assert_allclose(S.width_difference(d128, d256), [-0.1, 0.2, 0.1])


def test_clamp_width_difference_in_differences_uses_zero_bias_baseline() -> None:
    d128 = np.array([0.2, 0.4, 0.7, 0.8, 0.9])
    d256 = np.array([0.1, 0.5, 0.6, 1.0, 0.8])
    np.testing.assert_allclose(
        S.clamp_width_difference_in_differences(d128, d256, baseline_index=2),
        [0.0, 0.2, 0.0, 0.3, 0.0],
        atol=1e-12,
    )


def test_competence_gate_excludes_only_the_registered_width_pair() -> None:
    flags = [
        {
            "task": "vda9",
            "feedback": "crossattn1",
            "width": 256,
            "status": "competence_gated",
        }
    ]
    assert S.width_pair_is_admissible(flags, "vda9", "crossattn1") is False
    assert S.width_pair_is_admissible(flags, "vda9", "affine_ew") is True
    assert S.width_pair_is_admissible(flags, "vda4", "crossattn1") is True


def test_final_decoder_difference_maps_undefined_nan_to_none() -> None:
    assert S.final_decoder_difference(np.array([0.5, np.nan]), np.array([0.5, np.nan])) is None
    np.testing.assert_allclose(
        S.final_decoder_difference(np.array([0.5, 0.6]), np.array([0.5, 0.8])),
        [0.2],
    )


def test_final_decoder_value_preserves_absolute_score_and_undefined_estimand() -> None:
    assert S.final_decoder_value(np.array([0.5, 0.875])) == 0.875
    assert S.final_decoder_value(np.array([0.5, np.nan])) is None


def test_manifest_records_accepts_a_relative_root(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "run"
    root.mkdir()
    artifact = root / "artifact.txt"
    artifact.write_text("value", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    records = S.manifest_records(Path("run"), S.regular_files(Path("run")))
    assert records[0]["path"] == "artifact.txt"


def test_uniform_histogram_total_requires_exact_conservation() -> None:
    histogram = np.array([[20, 30], [10, 40]])
    assert S.uniform_histogram_total(histogram) == 50
    with np.testing.assert_raises(ValueError):
        S.uniform_histogram_total(np.array([[20, 30], [10, 39]]))


def test_decoder_estimand_contract_distinguishes_stored_and_effective_support() -> None:
    source = Path(S.__file__).read_text(encoding="utf-8")
    assert '"stored_trials_per_shard": trials["decoder_samples_per_shard"]' in source
    assert '"effective_samples": trials["decoder_samples_per_shard"]' in source
    assert source.count('"effective_samples": trials["decoder_change_present_samples_per_shard"]') == 2
    assert '"cued versus uncued change location among change-present trials"' in source


def test_trial_contract_derives_balanced_change_present_support() -> None:
    shards = {
        ("vda4", "affine_ew", 128): {
            "psychometric_press_histogram_valid": np.array([[[150, 150]]]),
            "clamp_press_histogram_valid": np.array([[[125, 125]]]),
            "decoder_sample_label_change": np.concatenate(
                [np.zeros(450, dtype=np.int64), np.ones(450, dtype=np.int64)]
            ),
        }
    }
    assert S.trial_contract(shards) == {
        "psychometric_trials_per_point": 300,
        "decoder_samples_per_shard": 900,
        "decoder_change_present_samples_per_shard": 450,
        "clamp_trials_per_cell": 250,
    }


def test_decoder_support_contract_uses_target_specific_multiclass_chance() -> None:
    shards = {}
    for task in S.TASKS:
        for feedback in S.FEEDBACKS:
            for width in S.WIDTHS:
                if task == "vda4":
                    location = np.array([-1] * 450 + [0] * 225 + [1] * 75 + [2] * 75 + [3] * 75)
                elif task == "vda9":
                    location = np.array(
                        [-1] * 450 + [0] * 225 + [1] * 29 + sum(([index] * 28 for index in range(2, 9)), [])
                    )
                else:
                    location = np.array([-1] * 450 + [0] * 450)
                shards[(task, feedback, width)] = {
                    "decoder_sample_label_change": np.array([0] * 450 + [1] * 450),
                    "decoder_sample_label_change_location": location,
                    "decoder_sample_label_cued_change": np.array([-1] * 450 + [0] * 225 + [1] * 225),
                }
    contract = S.decoder_support_contract(shards)
    assert contract["vda1"]["change_location"]["defined"] is False
    assert contract["vda4"]["change_location"]["class_counts"] == {
        "0": 225,
        "1": 75,
        "2": 75,
        "3": 75,
    }
    assert contract["vda4"]["change_location"]["balanced_accuracy_chance"] == 0.25
    assert contract["vda9"]["change_location"]["class_count"] == 9
    assert contract["vda9"]["change_location"]["balanced_accuracy_chance"] == 1 / 9
    assert contract["vda9"]["cued_change"]["balanced_accuracy_chance"] == 0.5


def test_trainable_parameter_count_excludes_registered_buffers() -> None:
    state = {
        "weight": torch.zeros(11),
        "jepa_center": torch.zeros(7),
        "critic_head.taus": torch.zeros(5),
    }
    assert S.trainable_parameter_count(state) == 11


def test_audit_normalizes_relative_output_root() -> None:
    source = Path(S.__file__).read_text(encoding="utf-8")
    audit_body = source.split("def audit(output_root: Path) -> Path:", 1)[1].split("def parse_args", 1)[0]
    assert "output_root = Path(os.path.abspath(output_root))" in audit_body


def test_standalone_figure_labels_vda1_location_probes_undefined() -> None:
    source = Path(S.__file__).read_text(encoding="utf-8")
    assert "VDA1 location probes undefined" in source
    assert "singleton task · chance N/A" in source
