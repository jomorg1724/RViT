#!/usr/bin/env python3
"""Export hash-verified constituent values behind matched-width difference plots."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
MANUSCRIPT_ROOT = Path(__file__).resolve().parent
UPSTREAM_ROOT = (
    REPO_ROOT
    / "RViT_plus_paper_jepa_grid9"
    / "vda_sweep"
    / "derived"
    / "2026-07-11_matched_width"
)
MANIFEST = (
    REPO_ROOT
    / "reports"
    / "vda_series"
    / "matched_width_20260712_production_v15"
    / "provenance"
    / "UPSTREAM_MANIFEST.json"
)
OUTPUT_ROOT = MANUSCRIPT_ROOT / "generated"
TASKS = ("vda1", "vda4", "vda9")
FEEDBACKS = ("affine_ew", "crossattn1")
WIDTHS = (128, 256)
ADMITTED_PAIRS = (
    ("vda1", "affine_ew"),
    ("vda1", "crossattn1"),
    ("vda4", "affine_ew"),
    ("vda4", "crossattn1"),
    ("vda9", "affine_ew"),
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def latex_feedback(feedback: str) -> str:
    labels = {"affine_ew": r"\texttt{affine}", "crossattn1": r"\texttt{cross-attn}"}
    return labels[feedback]


def load_shards() -> tuple[dict[tuple[str, str, int], dict[str, np.ndarray]], str]:
    manifest_bytes = MANIFEST.read_bytes()
    manifest_sha256 = sha256_bytes(manifest_bytes)
    manifest = json.loads(manifest_bytes)
    expected = {Path(item["path"]).name: item["sha256"] for item in manifest["shards"]}
    required = {f"{task}_{feedback}_d{width}.npz" for task in TASKS for feedback in FEEDBACKS for width in WIDTHS}
    if set(expected) != required:
        raise ValueError("upstream manifest does not declare the exact 12-shard inventory")

    shards: dict[tuple[str, str, int], dict[str, np.ndarray]] = {}
    for task in TASKS:
        for feedback in FEEDBACKS:
            for width in WIDTHS:
                name = f"{task}_{feedback}_d{width}.npz"
                path = UPSTREAM_ROOT / "shards" / name
                shard_bytes = path.read_bytes()
                actual = sha256_bytes(shard_bytes)
                if actual != expected[name]:
                    raise ValueError(f"shard hash mismatch for {name}: {actual} != {expected[name]}")
                with np.load(io.BytesIO(shard_bytes), allow_pickle=False) as payload:
                    shards[(task, feedback, width)] = {key: payload[key].copy() for key in payload.files}
    if MANIFEST.read_bytes() != manifest_bytes:
        raise RuntimeError("upstream manifest changed during constituent export")
    return shards, manifest_sha256


def extract_values(
    shards: dict[tuple[str, str, int], dict[str, np.ndarray]], manifest_sha256: str
) -> dict[str, Any]:
    behavior: list[dict[str, Any]] = []
    clamp: list[dict[str, Any]] = []
    common_magnitudes: list[float] | None = None
    common_biases: list[float] | None = None

    for task, feedback in ADMITTED_PAIRS:
        for width in WIDTHS:
            payload = shards[(task, feedback, width)]
            magnitudes = np.asarray(payload["change_magnitudes"], dtype=float)
            validities = np.asarray(payload["displayed_validities"], dtype=float)
            validity_indices = np.flatnonzero(np.isclose(validities, 0.75))
            if validity_indices.size != 1:
                raise ValueError(f"expected exactly one displayed-validity 0.75 row for {task}/{feedback}/d{width}")
            rates = np.asarray(payload["psychometric_response_rate_valid"], dtype=float)[validity_indices[0]]
            if rates.shape != magnitudes.shape or not np.all(np.isfinite(rates)):
                raise ValueError(f"invalid psychometric curve for {task}/{feedback}/d{width}")
            magnitude_list = magnitudes.tolist()
            if common_magnitudes is None:
                common_magnitudes = magnitude_list
            elif magnitude_list != common_magnitudes:
                raise ValueError("change magnitudes differ across admitted shards")
            behavior.append(
                {
                    "task": task,
                    "feedback": feedback,
                    "width": width,
                    "displayed_validity": 0.75,
                    "location": "valid",
                    "response_probability": rates.tolist(),
                }
            )

            biases = np.asarray(payload["clamp_key_logit_biases"], dtype=float)
            baseline_indices = np.flatnonzero(np.isclose(biases, 0.0))
            if baseline_indices.size != 1:
                raise ValueError(f"expected exactly one zero-bias cell for {task}/{feedback}/d{width}")
            baseline = int(baseline_indices[0])
            bias_list = biases.tolist()
            if common_biases is None:
                common_biases = bias_list
            elif bias_list != common_biases:
                raise ValueError("clamp biases differ across admitted shards")
            for condition in ("valid", "invalid"):
                if task == "vda1" and condition == "invalid":
                    continue
                dprime = np.asarray(payload[f"clamp_dprime_{condition}"], dtype=float)
                effect = dprime - dprime[baseline]
                if effect.shape != biases.shape or not np.all(np.isfinite(effect)):
                    raise ValueError(f"invalid clamp d-prime values for {task}/{feedback}/d{width}/{condition}")
                clamp.append(
                    {
                        "task": task,
                        "feedback": feedback,
                        "width": width,
                        "condition": condition,
                        "dprime_change_from_zero_bias": effect.tolist(),
                    }
                )

    return {
        "schema_version": 1,
        "artifact_class": "hash-verified constituent values behind matched-width difference plots",
        "upstream_manifest_path": str(MANIFEST.relative_to(REPO_ROOT)),
        "upstream_manifest_sha256": manifest_sha256,
        "contrast_boundary": "absolute checkpoint behavior and within-checkpoint D_w,x(b) values; no causal width estimand",
        "change_magnitudes_degrees": common_magnitudes,
        "clamp_key_logit_biases": common_biases,
        "behavior": behavior,
        "clamp": clamp,
    }


def behavior_tex(values: dict[str, Any]) -> str:
    headers = " & ".join(f"{value:g}" for value in values["change_magnitudes_degrees"])
    rows = []
    for record in values["behavior"]:
        scores = " & ".join(f"{value:.3f}" for value in record["response_probability"])
        rows.append(
            f"{record['task'].upper()} & {latex_feedback(record['feedback'])} & {record['width']} & {scores} \\\\"
        )
    return "\n".join(
        [
            r"\begingroup\scriptsize\setlength{\tabcolsep}{2.7pt}",
            r"\captionof{table}{\textbf{Absolute valid-location response probabilities.} Checkpoint-recomputed values at displayed validity 0.75; each cell uses 300 trials. These are the constituents behind Figure~\ref{fig:matched-width}A, not replicated estimates of a width effect.}\label{tab:absolute-behavior}",
            r"\begin{center}",
            r"\begin{tabular}{@{}llr*{10}{r}@{}}",
            r"\toprule",
            f"Task & Routing & Width & \\multicolumn{{10}}{{c}}{{Orientation change (degrees)}} \\\\\n\\cmidrule(lr){{4-13}}\n & & & {headers} \\\\ ",
            r"\midrule",
            *rows,
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{center}",
            r"\endgroup",
        ]
    ) + "\n"


def clamp_tex(values: dict[str, Any]) -> str:
    headers = " & ".join(f"{value:g}" for value in values["clamp_key_logit_biases"])
    rows = []
    for record in values["clamp"]:
        scores = " & ".join(f"{value:.3f}" for value in record["dprime_change_from_zero_bias"])
        rows.append(
            f"{record['task'].upper()} & {latex_feedback(record['feedback'])} & {record['condition']} & {record['width']} & {scores} \\\\"
        )
    return "\n".join(
        [
            r"\begingroup\scriptsize\setlength{\tabcolsep}{4.0pt}",
            r"\captionof{table}{\textbf{Within-checkpoint clamp constituents.} Each entry is $D_{w,x}(b)=d'_{w,x}(b)-d'_{w,x}(0)$ from 250 trials per bias, condition, and checkpoint. VDA1 invalid-location effects are undefined and therefore absent. Figure~\ref{fig:matched-width}C--D plots $W_x(b)=D_{256,x}(b)-D_{128,x}(b)$.}\label{tab:clamp-constituents}",
            r"\begin{center}",
            r"\begin{tabular}{@{}llll*{5}{r}@{}}",
            r"\toprule",
            f"Task & Routing & Condition & Width & \\multicolumn{{5}}{{c}}{{Assigned key-logit bias $b$}} \\\\\n\\cmidrule(lr){{5-9}}\n & & & & {headers} \\\\ ",
            r"\midrule",
            *rows,
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{center}",
            r"\endgroup",
        ]
    ) + "\n"


def main() -> None:
    shards, manifest_sha256 = load_shards()
    values = extract_values(shards, manifest_sha256)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "matched_width_constituents.json").write_text(
        json.dumps(values, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (OUTPUT_ROOT / "matched_width_absolute_behavior.tex").write_text(
        behavior_tex(values), encoding="utf-8"
    )
    (OUTPUT_ROOT / "matched_width_clamp_constituents.tex").write_text(
        clamp_tex(values), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "manifest_sha256": manifest_sha256,
                "behavior_rows": len(values["behavior"]),
                "clamp_rows": len(values["clamp"]),
                "outputs": [
                    str(OUTPUT_ROOT / "matched_width_constituents.json"),
                    str(OUTPUT_ROOT / "matched_width_absolute_behavior.tex"),
                    str(OUTPUT_ROOT / "matched_width_clamp_constituents.tex"),
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
