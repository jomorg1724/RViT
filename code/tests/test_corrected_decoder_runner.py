from __future__ import annotations

from pathlib import Path

from scripts import run_corrected_decoder as R


def test_runner_freezes_itself_builder_producer_and_full_dependency_graph():
    sources = R.capture_executable_sources()
    assert set(sources) == {
        "__runner__",
        "__builder__",
        "__producer__",
        *R.PRODUCER_DEPENDENCIES,
        *R.VALIDATION_SOURCES,
    }
    R.assert_executable_sources_unchanged(sources)


def test_runner_defaults_to_registered_versioned_production_scope():
    args = R.parse_args([])
    assert args.output_root == R.ROOT / "vda_sweep/derived/2026-07-11_corrected"
    assert args.n == 900
    assert args.seed == 20260711
    assert args.reuse_validated_run is False

    reuse = R.parse_args(["--reuse-validated-run"])
    assert reuse.reuse_validated_run is True


def test_runner_and_decoder_contracts_load_without_inline_scope_drift():
    sources = R.capture_executable_sources()
    builder, decoder = R._load_modules(sources)
    assert tuple(decoder.FEEDBACKS) == tuple(builder.FEEDBACKS)
