from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

from scripts import recover_corrected_decoder_publication as recovery


def test_recovery_script_supports_direct_cli_execution():
    script = Path(recovery.__file__).resolve()
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=script.parents[1],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr


def test_validate_finder_metadata_accepts_only_empty_icon_carriage_return_files(tmp_path: Path):
    first = tmp_path / "Icon\r"
    nested = tmp_path / "nested" / "Icon\r"
    nested.parent.mkdir()
    first.write_bytes(b"")
    nested.write_bytes(b"")

    assert recovery.validate_finder_metadata_files({first, nested}) == [first, nested]


@pytest.mark.parametrize(
    ("relative", "content"),
    [("Icon\r", b"not empty"), ("untracked.txt", b"")],
)
def test_validate_finder_metadata_rejects_unexpected_content(
    tmp_path: Path, relative: str, content: bytes
):
    path = tmp_path / relative
    path.write_bytes(content)

    with pytest.raises(RuntimeError, match="unsafe unmanifested entry"):
        recovery.validate_finder_metadata_files({path})


def test_legacy_validation_tolerates_only_external_link_count_drift():
    recorded = {
        "path_absolute": "/tmp/decode.npz",
        "sha256": "abc",
        "bytes": 10,
        "device": 1,
        "inode": 2,
        "nlink": 4,
    }
    current = {**recorded, "nlink": 2}

    assert recovery.validate_legacy_identity(recorded, current) == {
        "recorded_nlink": 4,
        "current_nlink": 2,
    }

    with pytest.raises(RuntimeError, match="legacy artifact sha256 changed"):
        recovery.validate_legacy_identity(recorded, {**current, "sha256": "changed"})


def test_clear_finder_info_uses_the_host_xattr_interface(tmp_path: Path):
    finder_info = "00" * 8 + "0400" + "00" * 22
    set_result = subprocess.run(
        ["/usr/bin/xattr", "-wx", "com.apple.FinderInfo", finder_info, str(tmp_path)],
        text=True,
        capture_output=True,
    )
    assert set_result.returncode == 0, set_result.stderr

    recovery.clear_finder_info(tmp_path)

    read_result = subprocess.run(
        ["/usr/bin/xattr", "-px", "com.apple.FinderInfo", str(tmp_path)],
        text=True,
        capture_output=True,
    )
    assert read_result.returncode != 0
