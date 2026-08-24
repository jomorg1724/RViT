from __future__ import annotations

import json

import pytest


def test_m3_panel_status_separates_available_undefined_blocked_and_inapplicable():
    from vda_series.behavior_figures import m3_panel_status

    assert m3_panel_status("vda4", "M3B") == "available"
    assert m3_panel_status("vda1", "M3B") == "undefined"
    assert m3_panel_status("vda16", "M3A") == "blocked"
    assert m3_panel_status("vda_fixed16", "M3A") == "training"
    assert m3_panel_status("vda_excl", "M3A") == "inapplicable"


def test_m3_panel_status_rejects_unknown_panel():
    from vda_series.behavior_figures import m3_panel_status

    with pytest.raises(ValueError, match="unknown M3 panel"):
        m3_panel_status("vda4", "M3Z")


def test_archived_psychology_cache_has_required_axes_and_families():
    from vda_series.behavior_figures import load_archived_psychology

    cache = load_archived_psychology()
    assert cache.change_magnitudes.tolist() == [0, 3, 6, 9, 12, 15, 18, 22, 26, 30]
    assert cache.validities.tolist() == [0.25, 0.5, 0.75, 1.0]
    assert cache.source_sha256 == "e63f0b343254ce6fa8632305c831d33c03ee5b5d75116423f20393f6dadc25fd"
    for task in ("vda1", "vda2", "vda4", "vda9"):
        for family in ("affine_ew", "crossattn1"):
            assert cache.iteration(task, family) == 19999


def test_m3_builder_rejects_nonadmitted_behavior_result(tmp_path):
    from vda_series.behavior_figures import build_m3_behavior_figure

    with pytest.raises(ValueError, match="blocked"):
        build_m3_behavior_figure("vda16", "affine_ew", tmp_path)
    with pytest.raises(ValueError, match="inapplicable"):
        build_m3_behavior_figure("vda_excl", "affine_ew", tmp_path)


@pytest.mark.parametrize("task", ["vda1", "vda4"])
def test_m3_builder_exports_source_mapped_artifacts(task, tmp_path):
    from vda_series.behavior_figures import build_m3_behavior_figure

    outputs = build_m3_behavior_figure(task, "affine_ew", tmp_path)
    assert outputs.pdf.is_file()
    assert outputs.svg.is_file()
    assert outputs.png.is_file()
    assert outputs.metadata.is_file()
    assert outputs.pdf.stat().st_size > 10_000
    assert outputs.svg.stat().st_size > 10_000
    assert outputs.png.stat().st_size > 100_000

    metadata = json.loads(outputs.metadata.read_text())
    assert metadata["schema_version"] == 1
    assert metadata["source_object"] == "M3"
    assert metadata["evidence_class"] == "regenerated from archived NPZ"
    assert metadata["recomputed_from_checkpoint"] is False
    assert metadata["source_npz_sha256"] == "e63f0b343254ce6fa8632305c831d33c03ee5b5d75116423f20393f6dadc25fd"
    assert metadata["task"] == task
    assert metadata["feedback"] == "affine_ew"
    assert metadata["panel_status_axis"] == "publication_coverage"
    assert metadata["epistemic_status_axis"] == "claim_support"
    if task == "vda1":
        assert metadata["panel_status"] == {
            "M3A": "complete",
            "M3B": "undefined",
            "M3C": "undefined",
            "M3D": "complete",
            "M3E": "undefined",
            "M3F": "undefined",
        }
        assert metadata["epistemic_status"]["M3A"] == "cache-attributed-aggregate"
        assert metadata["epistemic_status"]["M3B"] == "undefined"
    else:
        assert set(metadata["panel_status"].values()) == {"complete"}
        assert set(metadata["epistemic_status"].values()) == {"cache-attributed-aggregate"}
        assert all("opposing" not in description for description in metadata["panel_map"].values())
        assert "does not embed the evaluated spatial index" in metadata["uncued_location_boundary"]
    assert "forced cued or uncued locations" in metadata["producer_semantics_boundary"]
