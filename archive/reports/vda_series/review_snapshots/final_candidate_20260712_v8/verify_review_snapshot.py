from __future__ import annotations

import argparse
import hashlib
import json
import stat
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json_strict(path: Path) -> dict:
    def reject_constant(value: str) -> None:
        raise ValueError(f"Non-finite JSON constant {value!r} in {path}")

    def unique_object(pairs: list[tuple[str, object]]) -> dict:
        result: dict = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key {key!r} in {path}")
            result[key] = value
        return result

    return json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=reject_constant,
        object_pairs_hook=unique_object,
    )


def verify(snapshot: Path, render_root: Path) -> dict:
    snapshot = snapshot.resolve()
    render_root = render_root.resolve()
    manifest_path = snapshot / "SNAPSHOT_MANIFEST.json"
    manifest = load_json_strict(manifest_path)
    records = manifest.get("files")
    if not isinstance(records, list):
        raise RuntimeError("Snapshot manifest files must be a list")
    record_map = {record.get("path"): record for record in records}
    if None in record_map or len(record_map) != len(records):
        raise RuntimeError("Snapshot manifest paths are missing or duplicated")
    for name in record_map:
        candidate = Path(name)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise RuntimeError(f"Unsafe snapshot path: {name!r}")

    regular_files: dict[str, Path] = {}
    identities: set[tuple[int, int]] = set()
    immutable_flag = getattr(stat, "UF_IMMUTABLE", 0x00000002)
    for candidate in snapshot.rglob("*"):
        item_stat = candidate.lstat()
        if stat.S_ISLNK(item_stat.st_mode):
            raise RuntimeError(f"Symbolic link in snapshot: {candidate}")
        if candidate.stat().st_mode & stat.S_IWUSR:
            raise RuntimeError(f"Owner-writable snapshot entry: {candidate}")
        if not item_stat.st_flags & immutable_flag:
            raise RuntimeError(f"Snapshot entry lacks immutable flag: {candidate}")
        if stat.S_ISREG(item_stat.st_mode):
            if item_stat.st_nlink != 1:
                raise RuntimeError(f"Snapshot file has {item_stat.st_nlink} links: {candidate}")
            identity = (item_stat.st_dev, item_stat.st_ino)
            if identity in identities:
                raise RuntimeError(f"Duplicate file identity: {candidate}")
            identities.add(identity)
            if candidate != manifest_path:
                regular_files[str(candidate.relative_to(snapshot))] = candidate

    if set(record_map) != set(regular_files):
        missing = sorted(set(record_map) - set(regular_files))
        extra = sorted(set(regular_files) - set(record_map))
        raise RuntimeError(f"Exact inventory mismatch: missing={missing}, extra={extra}")
    if manifest.get("file_count_excluding_manifest") != len(regular_files):
        raise RuntimeError("Manifest file count does not match exact inventory")
    for name, candidate in regular_files.items():
        record = record_map[name]
        if record.get("bytes") != candidate.stat().st_size:
            raise RuntimeError(f"Byte-size mismatch: {name}")
        if record.get("sha256") != sha256(candidate):
            raise RuntimeError(f"SHA-256 mismatch: {name}")

    pages = sorted(render_root.glob("page-*.png"))
    expected_names = [f"page-{index:02d}.png" for index in range(1, 55)]
    if [page.name for page in pages] != expected_names:
        raise RuntimeError("Rendered pages are incomplete or non-canonical")
    render_digest = hashlib.sha256()
    for page in pages:
        render_digest.update(f"{sha256(page)}  rendered/{page.name}\n".encode("utf-8"))
    if render_digest.hexdigest() != manifest.get("ordered_render_set_sha256"):
        raise RuntimeError("Ordered render digest does not match snapshot manifest")

    identity_checks = {
        "main.tex": "source_sha256",
        "main.pdf": "pdf_sha256",
        "build_manifest.py": "build_manifest_sha256",
    }
    for name, key in identity_checks.items():
        if sha256(snapshot / name) != manifest.get(key):
            raise RuntimeError(f"Top-level identity mismatch: {name}")

    return {
        "verdict": "PASS",
        "candidate": manifest.get("candidate"),
        "snapshot_manifest_sha256": sha256(manifest_path),
        "source_sha256": manifest.get("source_sha256"),
        "pdf_sha256": manifest.get("pdf_sha256"),
        "build_manifest_sha256": manifest.get("build_manifest_sha256"),
        "ordered_render_set_sha256": render_digest.hexdigest(),
        "files_excluding_manifest": len(regular_files),
        "files_including_manifest": len(regular_files) + 1,
        "rendered_pages": len(pages),
        "all_regular_files_one_link": True,
        "all_file_identities_unique": True,
        "all_snapshot_entries_read_only_and_immutable": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only verification of a frozen manuscript review snapshot")
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--render-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.snapshot, args.render_root), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
