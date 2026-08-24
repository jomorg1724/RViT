"""Audit run-registry provenance and artifact references."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "registry" / "run_manifest.schema.json"
PROVENANCE_FIELDS = (
    "source_tree_sha256",
    "command",
    "seed",
    "device",
    "start_time",
    "end_time",
)
PATH_FIELDS = ("metrics_path", "checkpoint_paths", "analysis_paths")
ALLOWED_COMPLETION_REASONS_BY_STATUS = {
    "active": {"unknown"},
    "partial": {
        "unknown",
        "early_success",
        "interrupted_infrastructure",
        "interrupted_manual",
        "numerical_failure",
        "policy_collapse",
    },
    "logged_phase_complete": {"budget_complete"},
}


def _issue(run_id: str, field: str, message: str) -> dict[str, str]:
    return {"run_id": run_id, "field": field, "message": message}


def _load_schema(schema_path: Path) -> dict[str, Any]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    required = schema.get("required")
    properties = schema.get("properties")
    if not isinstance(required, list) or not all(isinstance(field, str) for field in required):
        raise ValueError(f"schema has no valid required-field list: {schema_path}")
    if not isinstance(properties, dict):
        raise ValueError(f"schema has no valid properties map: {schema_path}")
    return schema


def _matches_type(value: Any, expected: str) -> bool:
    return {
        "null": value is None,
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "boolean": isinstance(value, bool),
    }.get(expected, True)


RFC3339_DATE_TIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


def _matches_date_time(value: str) -> bool:
    """Return whether a timestamp is syntactically and calendrically valid RFC 3339."""
    if RFC3339_DATE_TIME.fullmatch(value) is None:
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return True


def _schema_errors(record: dict[str, Any], schema: dict[str, Any]) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    for field in schema["required"]:
        if field not in record:
            errors.append((field, "required field is missing"))

    for field, value in record.items():
        rule = schema["properties"].get(field)
        if not isinstance(rule, dict):
            continue
        expected = rule.get("type")
        expected_types = [expected] if isinstance(expected, str) else expected
        if isinstance(expected_types, list) and not any(
            isinstance(item, str) and _matches_type(value, item) for item in expected_types
        ):
            errors.append((field, f"value has invalid type; expected {expected_types}"))
            continue
        if "enum" in rule and value not in rule["enum"]:
            errors.append((field, f"value is not one of the allowed values: {rule['enum']}"))
        if isinstance(value, str):
            if "minLength" in rule and len(value) < rule["minLength"]:
                errors.append((field, f"string is shorter than {rule['minLength']}"))
            if "pattern" in rule and re.fullmatch(rule["pattern"], value) is None:
                errors.append((field, f"string does not match required pattern {rule['pattern']}"))
            if rule.get("format") == "date-time" and not _matches_date_time(value):
                errors.append((field, "string is not a valid RFC 3339 date-time"))
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if not math.isfinite(value):
                errors.append((field, "numeric value must be finite"))
                continue
            if "minimum" in rule and value < rule["minimum"]:
                errors.append((field, f"value is below minimum {rule['minimum']}"))
        if isinstance(value, list):
            if rule.get("uniqueItems") and len({json.dumps(item, sort_keys=True) for item in value}) != len(value):
                errors.append((field, "array items must be unique"))
            item_rule = rule.get("items")
            if isinstance(item_rule, dict) and isinstance(item_rule.get("type"), str):
                for item in value:
                    if not _matches_type(item, item_rule["type"]):
                        errors.append((field, f"array item has invalid type; expected {item_rule['type']}"))
                        break
        if isinstance(value, dict) and isinstance(rule.get("additionalProperties"), dict):
            item_rule = rule["additionalProperties"]
            item_types = item_rule.get("type")
            item_types = [item_types] if isinstance(item_types, str) else item_types
            for item in value.values():
                if isinstance(item_types, list) and not any(
                    isinstance(expected_item, str) and _matches_type(item, expected_item)
                    for expected_item in item_types
                ):
                    errors.append((field, f"object value has invalid type; expected {item_types}"))
                    break
                if isinstance(item, str) and "pattern" in item_rule and re.fullmatch(item_rule["pattern"], item) is None:
                    errors.append((field, f"object value does not match required pattern {item_rule['pattern']}"))
                    break
    return errors


def _referenced_paths(record: dict[str, Any], field: str) -> list[str]:
    value = record.get(field)
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def audit_records(
    records: Iterable[dict[str, Any]],
    workspace: Path,
    *,
    strict_active: bool = False,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
) -> dict[str, list[dict[str, str]]]:
    """Classify schema, identity, path, and provenance problems."""
    workspace = workspace.resolve()
    schema = _load_schema(schema_path)
    records = list(records)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    seen_run_ids: set[str] = set()

    for record in records:
        run_id = str(record.get("run_id") or "<missing-run-id>")
        active = record.get("status") == "active"

        for field, message in _schema_errors(record, schema):
            errors.append(_issue(run_id, field, message))

        checkpoint_paths = record.get("checkpoint_paths")
        checkpoint_hashes = record.get("checkpoint_sha256")
        if isinstance(checkpoint_paths, list) and isinstance(checkpoint_hashes, dict):
            path_keys = {path for path in checkpoint_paths if isinstance(path, str)}
            hash_keys = {path for path in checkpoint_hashes if isinstance(path, str)}
            if path_keys != hash_keys:
                missing = sorted(path_keys - hash_keys)
                extra = sorted(hash_keys - path_keys)
                errors.append(
                    _issue(
                        run_id,
                        "checkpoint_sha256",
                        "keys must exactly match checkpoint_paths "
                        f"(missing={missing}, extra={extra})",
                    )
                )
            for path, value in checkpoint_hashes.items():
                if value is not None and (
                    not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None
                ):
                    errors.append(
                        _issue(
                            run_id,
                            "checkpoint_sha256",
                            f"digest for {path!r} must be null or 64 lowercase hexadecimal characters",
                        )
                    )

        start_time = record.get("start_time")
        end_time = record.get("end_time")
        if (
            isinstance(start_time, str)
            and isinstance(end_time, str)
            and _matches_date_time(start_time)
            and _matches_date_time(end_time)
        ):
            normalized_start = start_time[:-1] + "+00:00" if start_time.endswith("Z") else start_time
            normalized_end = end_time[:-1] + "+00:00" if end_time.endswith("Z") else end_time
            if datetime.fromisoformat(normalized_end) < datetime.fromisoformat(normalized_start):
                errors.append(_issue(run_id, "end_time", "end_time must not precede start_time"))

        status = record.get("status")
        completion_reason = record.get("completion_reason")
        if (
            isinstance(status, str)
            and isinstance(completion_reason, str)
            and status in ALLOWED_COMPLETION_REASONS_BY_STATUS
            and completion_reason not in ALLOWED_COMPLETION_REASONS_BY_STATUS[status]
        ):
            errors.append(
                _issue(
                    run_id,
                    "completion_reason",
                    f"completion_reason {completion_reason!r} is inconsistent with status {status!r}",
                )
            )

        if run_id in seen_run_ids:
            errors.append(_issue(run_id, "run_id", "duplicate run_id"))
        else:
            seen_run_ids.add(run_id)

        for field in PATH_FIELDS:
            for relative in _referenced_paths(record, field):
                path = Path(relative)
                if path.is_absolute() or ".." in path.parts:
                    errors.append(_issue(run_id, field, f"path must be workspace-relative: {relative}"))
                    continue
                candidate = workspace / path
                resolved = candidate.resolve()
                try:
                    resolved.relative_to(workspace)
                except ValueError:
                    errors.append(_issue(run_id, field, f"workspace-relative path escapes workspace: {relative}"))
                else:
                    if not candidate.exists():
                        errors.append(_issue(run_id, field, f"referenced path does not exist: {relative}"))

        for field in PROVENANCE_FIELDS:
            if record.get(field) is None or record.get(field) == "":
                issue = _issue(run_id, field, "provenance is unknown")
                if strict_active and active:
                    errors.append(issue)
                else:
                    warnings.append(issue)
    return {"errors": errors, "warnings": warnings}


def _parse_finite_json_float(raw: str) -> float:
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError(f"non-finite JSON number {raw!r} is not allowed")
    return value


def _reject_json_constant(raw: str):
    raise ValueError(f"non-finite JSON number {raw!r} is not allowed")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read non-empty JSON object lines from a registry."""
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(
                line,
                parse_float=_parse_finite_json_float,
                parse_constant=_reject_json_constant,
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{path}:{line_number}: malformed JSON: {exc.msg} at column {exc.colno}"
            ) from None
        except ValueError as exc:
            raise ValueError(f"{path}:{line_number}: {exc}") from None
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: registry line is not a JSON object")
        records.append(value)
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_workspace = Path(__file__).resolve().parents[2]
    parser.add_argument("--workspace", type=Path, default=default_workspace)
    parser.add_argument(
        "--registry",
        type=Path,
        default=default_workspace / "research_db" / "registry" / "artifacts.jsonl",
    )
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--strict-active", action="store_true")
    args = parser.parse_args(argv)

    try:
        records = load_jsonl(args.registry)
        report = audit_records(
            records,
            args.workspace,
            strict_active=args.strict_active,
            schema_path=args.schema,
        )
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    output = {
        "counts": {
            "records": len(records),
            "errors": len(report["errors"]),
            "warnings": len(report["warnings"]),
        },
        **report,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
