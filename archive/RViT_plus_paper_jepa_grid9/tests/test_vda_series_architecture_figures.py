from __future__ import annotations

import json

import pytest


def test_architecture_inventory_is_explicit_and_limited_to_admitted_families():
    from vda_series.architecture_figures import ARCHITECTURE_FAMILIES

    assert ARCHITECTURE_FAMILIES == ("affine_ew", "crossattn1")


@pytest.mark.parametrize("family", ["affine_ew", "crossattn1"])
def test_architecture_spec_is_source_grounded_and_non_empirical(family):
    from vda_series.architecture_figures import architecture_spec

    spec = architecture_spec(family)
    assert spec.family == family
    assert spec.claim_class == "model specification"
    assert spec.is_model_result is False
    assert spec.shared_pipeline == (
        "RGB frame",
        "patch front end",
        "feedback routing",
        "spatial xLSTM",
        "actor and QR critic",
    )
    assert "model.py" in spec.source_paths
    assert "paper_encoder.py" in spec.source_paths
    assert "paper_heads.py" in spec.source_paths
    assert spec.routing_equations


def test_affine_and_cross_attention_specs_do_not_conflate_routing():
    from vda_series.architecture_figures import architecture_spec

    affine = architecture_spec("affine_ew")
    cross = architecture_spec("crossattn1")
    assert "gamma * X + beta" in affine.routing_equations
    assert "concat" not in affine.routing_equations
    assert "concat" in cross.routing_equations
    assert "gamma" not in cross.routing_equations


def test_architecture_spec_rejects_unadmitted_family():
    from vda_series.architecture_figures import architecture_spec

    with pytest.raises(ValueError, match="unknown architecture family"):
        architecture_spec("multiplicative")


def test_m2_builder_exports_vector_raster_and_metadata(tmp_path):
    from vda_series.architecture_figures import build_m2_architecture_figure

    outputs = build_m2_architecture_figure(tmp_path)
    assert outputs.pdf.is_file()
    assert outputs.svg.is_file()
    assert outputs.png.is_file()
    assert outputs.metadata.is_file()
    assert outputs.pdf.stat().st_size > 10_000
    assert outputs.svg.stat().st_size > 10_000
    assert outputs.png.stat().st_size > 100_000

    metadata = json.loads(outputs.metadata.read_text())
    assert metadata["schema_version"] == 1
    assert metadata["source_object"] == "M2"
    assert metadata["claim_class"] == "model specification"
    assert metadata["is_model_result"] is False
    assert metadata["families"] == ["affine_ew", "crossattn1"]
    assert metadata["panel_map"] == {
        "M2a": "patching and visual features",
        "M2b": "routing/allocation mechanism",
        "M2c": "recurrent memory update",
        "M2d": "actor and critic readouts",
    }
    assert set(metadata["source_sha256"]) == {
        "model.py",
        "paper_encoder.py",
        "paper_heads.py",
        "conv_frontend.py",
    }
