"""Re-analyze VDA4 spatial-scaling attention on a common physical 2x2 grid.

This derived analysis consumes the hash-bound ``event_attention.npz``
artifacts produced by ``vda4_spatial_scaling_evaluation.py`` plus a focused,
source-resolved held-out refresh from the same terminal checkpoints.  The
source refresh is produced separately; this reducer itself does not import
Torch.

The native attention tensor is A[b, t, i, j], where i indexes query patches
and j indexes key patches.  Cross-attention has N visual keys followed by N
recurrent-memory keys.  Those two sources are split before any spatial
reduction.  The source-specific incoming attention score is

    p^s_j = (1 / N_query) * sum_i A^s_ij,  s in {visual, memory}.

The two source maps retain their mass under the model's joint 2N-key softmax
and are displayed on one shared raw scale.  Their sum is retained only as an
explicitly named paired-location diagnostic, never as the sole cross-attention
map or maximum.

Every native 2x2, 4x4, or 10x10 token grid is then partitioned into the same
four physical image quadrants.  The analysis deliberately reports several
non-interchangeable summaries:

* total_quadrant_mass: sum of p_j within a quadrant (combined-map uniform
  baseline 0.25; raw source-map baseline 0.125);
* peak_patch_raw: max p_j within a quadrant (combined-map uniform baseline
  1/N; raw source-map baseline 1/(2N));
* peak_patch_uniform_ratio: N * max p_j for a combined map or 2N * max p^s_j
  for a raw source map (uniform baseline 1);
* peak_patch_quadrant_share: each quadrant's maximum divided by the sum of
  the four quadrant maxima (uniform baseline 0.25);
* within_quadrant_peak_ratio: (N/4) * max(p_j) / sum(p_j in quadrant)
  (uniform-within-quadrant baseline 1; degenerate at exactly 2x2).

Measures are computed trial by trial.  Frame 5 (change onset) is the primary
event snapshot; frame 6 (the open-loop post-change continuation) and the mean
of frames 5-6 are reported as distinct companion summaries.  The retained
cache does not contain trial-level raw query-key matrices, so the alternative
``max_i A_ij`` strongest-query statistic cannot receive trialwise uncertainty
and is not substituted for the requested ``max_j mean_i A_ij`` peak-patch
measure.  Correlational attention summaries remain strictly separate from
causal intervention evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = (
    ROOT
    / "reports"
    / "vda_series"
    / "spatial_scaling_evaluation_production_20260727"
)
DEFAULT_OUTPUT_ROOT = (
    ROOT
    / "reports"
    / "vda_series"
    / "spatial_scaling_attention_measures_20260803_source_separated_v6"
)
DEFAULT_SOURCE_RESOLVED_ROOT = (
    ROOT
    / "reports"
    / "vda_series"
    / "spatial_scaling_crossattn_source_attention_20260803"
)
DEFAULT_MANUSCRIPT_FIGURES = (
    ROOT.parent / "reports" / "vda_series" / "figures" / "spatial_scaling"
)

SOURCE_RE = re.compile(
    r"^vda4_(?P<feedback>crossattn1|affine_ew)_grid"
    r"(?P<rows>2|4|10)x(?P<cols>2|4|10)_seed(?P<seed>[01])$"
)
CONDITIONS = ("valid", "invalid")
WINDOWS: dict[str, tuple[int, ...]] = {
    "frame5": (5,),
    "frame6": (6,),
    "frames5_6_mean": (5, 6),
}
TARGET_QUADRANT = {"valid": 0, "invalid": 3}
CUE_QUADRANT = 0
TRIALS_EXPECTED = 128
BOOTSTRAP_DRAWS = 10_000

FEEDBACK_STYLE = {
    "crossattn1": {
        "label": "Cross-attention",
        "color": "#1f6fb2",
        "marker": "o",
    },
    "affine_ew": {
        "label": "Affine EW",
        "color": "#8e44ad",
        "marker": "s",
    },
}
GRID_COLORS = {4: "#440154", 16: "#21918c", 100: "#fde725"}


@dataclass(frozen=True)
class Source:
    label: str
    feedback: str
    grid_rows: int
    grid_cols: int
    n_tokens: int
    seed: int
    root: Path
    event_path: Path
    manifest_path: Path
    event_sha256: str
    manifest_sha256: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def finite_array(value: Any, label: str) -> np.ndarray:
    array = np.asarray(value)
    require(bool(np.all(np.isfinite(array))), f"{label} contains non-finite values")
    return array


def stable_seed(*parts: Any) -> int:
    text = "|".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(text).digest()[:8], "little") % (2**32)


def bootstrap_interval(
    values: np.ndarray,
    *,
    seed_parts: Iterable[Any],
    draws: int = BOOTSTRAP_DRAWS,
) -> tuple[float, float, float]:
    vector = finite_array(values, "bootstrap values").astype(np.float64).reshape(-1)
    require(vector.size > 1, "bootstrap requires at least two observations")
    rng = np.random.default_rng(stable_seed(*seed_parts))
    indices = rng.integers(0, vector.size, size=(draws, vector.size))
    means = vector[indices].mean(axis=1)
    low, high = np.quantile(means, [0.025, 0.975])
    return float(vector.mean()), float(low), float(high)


def quadrant_indices(grid_rows: int, grid_cols: int) -> tuple[tuple[int, ...], ...]:
    """Partition an even native grid into the same four physical quadrants."""
    if grid_rows <= 0 or grid_cols <= 0 or grid_rows % 2 or grid_cols % 2:
        raise ValueError(f"expected positive even grid dimensions, got {grid_rows}x{grid_cols}")
    regions: list[tuple[int, ...]] = []
    half_rows, half_cols = grid_rows // 2, grid_cols // 2
    for quadrant_row in range(2):
        for quadrant_col in range(2):
            tokens = tuple(
                row * grid_cols + col
                for row in range(quadrant_row * half_rows, (quadrant_row + 1) * half_rows)
                for col in range(quadrant_col * half_cols, (quadrant_col + 1) * half_cols)
            )
            regions.append(tokens)
    flat = sorted(token for region in regions for token in region)
    require(flat == list(range(grid_rows * grid_cols)), "quadrants do not partition native tokens")
    return tuple(regions)


def patch_column_scores(raw_attention: np.ndarray, n_tokens: int) -> np.ndarray:
    """Average each key column over query rows; pair visual+memory locations."""
    raw = finite_array(raw_attention, "raw attention").astype(np.float64)
    require(raw.ndim >= 2, f"raw attention must have query/key axes, got {raw.shape}")
    require(raw.shape[-2] == n_tokens, f"expected {n_tokens} queries, got {raw.shape[-2]}")
    if raw.shape[-1] == n_tokens:
        combined = raw
    elif raw.shape[-1] == 2 * n_tokens:
        combined = raw[..., :n_tokens] + raw[..., n_tokens:]
    else:
        raise ValueError(f"expected N or 2N keys, got {raw.shape[-1]} for N={n_tokens}")
    scores = combined.mean(axis=-2)
    require(bool(np.allclose(scores.sum(axis=-1), 1.0, atol=2e-5)), "patch scores are not normalized")
    return scores


def source_patch_column_scores(
    raw_attention: np.ndarray,
    n_tokens: int,
) -> dict[str, np.ndarray]:
    """Return raw source-specific column means under the joint key softmax.

    Visual and recurrent-memory maps are deliberately *not* normalized within
    source.  Their total masses therefore preserve the model's allocation
    between the two key blocks, and both maps can be displayed on one absolute
    scale as in the established VDA4 figures.
    """
    raw = finite_array(raw_attention, "raw attention").astype(np.float64)
    require(raw.shape[-2] == n_tokens, f"expected {n_tokens} queries")
    if raw.shape[-1] == n_tokens:
        score = raw.mean(axis=-2)
        require(bool(np.allclose(score.sum(axis=-1), 1.0, atol=2e-5)), "self-attention score not normalized")
        return {"self": score}
    require(raw.shape[-1] == 2 * n_tokens, "cross-attention must expose 2N keys")
    result = {
        "visual": raw[..., :n_tokens].mean(axis=-2),
        "memory": raw[..., n_tokens:].mean(axis=-2),
    }
    require(
        bool(np.allclose(result["visual"].sum(axis=-1) + result["memory"].sum(axis=-1), 1.0, atol=2e-5)),
        "cross-attention source scores do not reconstruct the joint softmax mass",
    )
    return result


def source_conditional_patch_scores(
    raw_scores: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Normalize raw source maps conditionally for a secondary localization view."""
    result: dict[str, np.ndarray] = {}
    for name, score in raw_scores.items():
        array = finite_array(score, f"{name} source score").astype(np.float64)
        total = array.sum(axis=-1, keepdims=True)
        result[name] = array / np.maximum(total, 1e-15)
    return result


def source_mean_rows_for_source(
    source: Source,
    payload: dict[str, np.ndarray],
) -> list[dict[str, Any]]:
    """Describe cross-attention source share and within-source localization.

    ``raw_attention_mean`` is already averaged over held-out trials.  These rows
    are therefore descriptive means only and intentionally contain no trial CI.
    """
    if source.feedback != "crossattn1":
        return []
    raw = finite_array(payload["raw_attention_mean"], f"{source.label}/raw_attention_mean").astype(np.float64)
    regions = quadrant_indices(source.grid_rows, source.grid_cols)
    rows: list[dict[str, Any]] = []
    for source_name, block in (
        ("visual", raw[..., : source.n_tokens]),
        ("memory", raw[..., source.n_tokens :]),
    ):
        unconditional = block.mean(axis=-2)
        source_share = unconditional.sum(axis=-1)
        conditional = unconditional / np.maximum(source_share[..., None], 1e-15)
        conditional_metrics = common_quadrant_metrics(conditional, regions)
        for condition_index, condition in enumerate(CONDITIONS):
            target = TARGET_QUADRANT[condition]
            cue = CUE_QUADRANT
            for window_name, frames in WINDOWS.items():
                frame_indices = list(frames)
                total = conditional_metrics["total_quadrant_mass"][condition_index, frame_indices].mean(axis=0)
                peak_share = conditional_metrics["peak_patch_quadrant_share"][condition_index, frame_indices].mean(axis=0)
                rows.append(
                    {
                        "label": source.label,
                        "feedback": source.feedback,
                        "grid": f"{source.grid_rows}x{source.grid_cols}",
                        "n_tokens": source.n_tokens,
                        "seed": source.seed,
                        "condition": condition,
                        "window": window_name,
                        "source": source_name,
                        "estimation_unit": "trial-averaged raw attention; descriptive mean only",
                        "source_total_share": float(source_share[condition_index, frame_indices].mean()),
                        "target_conditional_total_mass": float(total[target]),
                        "cue_conditional_total_mass": float(total[cue]),
                        "target_minus_cue_conditional_total_mass": float(total[target] - total[cue]),
                        "target_conditional_peak_share": float(peak_share[target]),
                        "cue_conditional_peak_share": float(peak_share[cue]),
                        "target_minus_cue_conditional_peak_share": float(peak_share[target] - peak_share[cue]),
                    }
                )
    return rows


def common_quadrant_metrics(
    patch_scores: np.ndarray,
    regions: tuple[tuple[int, ...], ...],
) -> dict[str, np.ndarray]:
    """Compute distinct common-grid summaries without collapsing their meaning."""
    scores = finite_array(patch_scores, "patch scores").astype(np.float64)
    n_tokens = scores.shape[-1]
    require(n_tokens == sum(len(region) for region in regions), "region/token mismatch")
    require(len(regions) == 4, "VDA4 comparison requires exactly four quadrants")
    require(len({len(region) for region in regions}) == 1, "quadrants must have equal area")

    total = np.stack([scores[..., list(region)].sum(axis=-1) for region in regions], axis=-1)
    peak = np.stack([scores[..., list(region)].max(axis=-1) for region in regions], axis=-1)
    peak_sum = peak.sum(axis=-1, keepdims=True)
    region_size = len(regions[0])
    result = {
        "total_quadrant_mass": total,
        "mean_patch_mass": total / float(region_size),
        "peak_patch_raw": peak,
        "peak_patch_uniform_ratio": peak * float(n_tokens),
        "peak_patch_quadrant_share": peak / np.maximum(peak_sum, 1e-15),
        "within_quadrant_peak_ratio": (
            float(region_size) * peak / np.maximum(total, 1e-15)
        ),
    }
    require(bool(np.allclose(total.sum(axis=-1), 1.0, atol=2e-5)), "quadrant totals are not normalized")
    require(
        bool(np.allclose(result["peak_patch_quadrant_share"].sum(axis=-1), 1.0, atol=2e-5)),
        "peak shares are not normalized",
    )
    return result


def source_quadrant_metrics(
    source_scores: np.ndarray,
    regions: tuple[tuple[int, ...], ...],
) -> dict[str, np.ndarray]:
    """Compute quadrant measures on one raw cross-attention source map.

    The input sums to that source's share rather than one.  Raw totals and
    peaks preserve the visual-versus-memory allocation.  Conditional fields
    are provided as explicitly secondary localization measures.
    """
    scores = finite_array(source_scores, "source patch scores").astype(np.float64)
    n_tokens = scores.shape[-1]
    require(n_tokens == sum(len(region) for region in regions), "source region/token mismatch")
    require(len(regions) == 4, "VDA4 comparison requires exactly four quadrants")
    require(len({len(region) for region in regions}) == 1, "quadrants must have equal area")
    share = scores.sum(axis=-1)
    require(bool(np.all(share >= -1e-12)), "source share is negative")
    total = np.stack([scores[..., list(region)].sum(axis=-1) for region in regions], axis=-1)
    peak = np.stack([scores[..., list(region)].max(axis=-1) for region in regions], axis=-1)
    conditional_total = total / np.maximum(share[..., None], 1e-15)
    conditional_peak = peak / np.maximum(share[..., None], 1e-15)
    peak_sum = peak.sum(axis=-1, keepdims=True)
    region_size = len(regions[0])
    result = {
        "source_total_share": share,
        "raw_total_quadrant_mass": total,
        "raw_peak_patch": peak,
        "raw_peak_patch_uniform_ratio": 2.0 * float(n_tokens) * peak,
        "conditional_total_quadrant_mass": conditional_total,
        "conditional_peak_patch": conditional_peak,
        "conditional_peak_patch_uniform_ratio": float(n_tokens) * conditional_peak,
        "peak_patch_quadrant_share": peak / np.maximum(peak_sum, 1e-15),
        "within_quadrant_peak_ratio": float(region_size) * peak / np.maximum(total, 1e-15),
    }
    require(bool(np.allclose(total.sum(axis=-1), share, atol=2e-5)), "source quadrant totals do not sum to source share")
    return result


def discover_sources(source_root: Path) -> list[Source]:
    sources: list[Source] = []
    for directory in sorted(source_root.glob("vda4_*_grid*x*_seed*")):
        if not directory.is_dir():
            continue
        match = SOURCE_RE.fullmatch(directory.name)
        if match is None:
            continue
        rows, cols = int(match.group("rows")), int(match.group("cols"))
        if rows != cols:
            continue
        manifest_path = directory / "MANIFEST.json"
        event_path = directory / "data" / "event_attention.npz"
        require(manifest_path.is_file(), f"missing {manifest_path}")
        require(event_path.is_file(), f"missing {event_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        require(manifest.get("status") == "complete", f"{directory.name}: manifest not complete")
        expected = manifest.get("artifact_hashes", {}).get("data/event_attention.npz")
        actual = sha256_file(event_path)
        require(expected == actual, f"{directory.name}: event-attention SHA-256 mismatch")
        model = manifest.get("model", {})
        require(model.get("label") == directory.name, f"{directory.name}: manifest label mismatch")
        require(int(model.get("checkpoint_iteration", -1)) == 19999, f"{directory.name}: nonterminal checkpoint")
        sources.append(
            Source(
                label=directory.name,
                feedback=match.group("feedback"),
                grid_rows=rows,
                grid_cols=cols,
                n_tokens=rows * cols,
                seed=int(match.group("seed")),
                root=directory,
                event_path=event_path,
                manifest_path=manifest_path,
                event_sha256=actual,
                manifest_sha256=sha256_file(manifest_path),
            )
        )
    expected_labels = {
        f"vda4_{feedback}_grid{grid}x{grid}_seed0"
        for feedback in ("crossattn1", "affine_ew")
        for grid in (2, 4, 10)
    } | {
        f"vda4_crossattn1_grid{grid}x{grid}_seed1"
        for grid in (2, 10)
    }
    found = {source.label for source in sources}
    require(expected_labels <= found, f"missing sources: {sorted(expected_labels - found)}")
    return [source for source in sources if source.label in expected_labels]


def load_source(source: Source) -> dict[str, np.ndarray]:
    with np.load(source.event_path, allow_pickle=False) as cache:
        payload = {key: cache[key] for key in cache.files}
    token_mass = finite_array(payload["token_mass"], f"{source.label}/token_mass").astype(np.float64)
    region_mass = finite_array(payload["region_mass"], f"{source.label}/region_mass").astype(np.float64)
    raw_mean = finite_array(payload["raw_attention_mean"], f"{source.label}/raw_attention_mean").astype(np.float64)
    require(token_mass.shape == (2, TRIALS_EXPECTED, 7, source.n_tokens), f"{source.label}: token-mass shape")
    require(region_mass.shape == (2, TRIALS_EXPECTED, 7, 4), f"{source.label}: region-mass shape")
    expected_keys = source.n_tokens * (2 if source.feedback == "crossattn1" else 1)
    require(raw_mean.shape == (2, 7, source.n_tokens, expected_keys), f"{source.label}: raw-mean shape")
    require(bool(np.allclose(token_mass.sum(axis=-1), 1.0, atol=2e-5)), f"{source.label}: token mass not normalized")
    regions = quadrant_indices(source.grid_rows, source.grid_cols)
    rebuilt = common_quadrant_metrics(token_mass, regions)["total_quadrant_mass"]
    require(bool(np.allclose(rebuilt, region_mass, atol=2e-5)), f"{source.label}: cached region mass mismatch")
    raw_scores = patch_column_scores(raw_mean, source.n_tokens)
    require(
        bool(np.allclose(raw_scores, token_mass.mean(axis=1), atol=2e-5)),
        f"{source.label}: raw attention column means do not reconstruct trial-mean token mass",
    )
    return {"token_mass": token_mass, "raw_attention_mean": raw_mean}


def load_source_resolved(
    source_root: Path,
    sources: list[Source],
) -> dict[str, dict[str, np.ndarray]]:
    """Load hash-bound trialwise visual/memory source caches.

    These caches are a held-out refresh from the same terminal checkpoints and
    common-random-number event bank.  They exist because the original admitted
    cache retained source identity only after averaging over trials.
    """
    require(source_root.is_dir(), f"source-resolved root not found: {source_root}")
    result: dict[str, dict[str, np.ndarray]] = {}
    cross_sources = [source for source in sources if source.feedback == "crossattn1"]
    for source in cross_sources:
        directory = source_root / source.label
        manifest_path = directory / "MANIFEST.json"
        candidates = (
            directory / "data" / "source_attention.npz",
            directory / "data" / "source_event_attention.npz",
            directory / "source_event_attention.npz",
        )
        event_path = next((path for path in candidates if path.is_file()), None)
        require(manifest_path.is_file(), f"missing source-resolved manifest: {manifest_path}")
        require(event_path is not None, f"missing source-resolved event cache under {directory}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        require(manifest.get("status") == "complete", f"{source.label}: source-resolved manifest not complete")
        relative_event = event_path.relative_to(directory).as_posix()
        expected_hash = manifest.get("artifact_hashes", {}).get(relative_event)
        require(expected_hash == sha256_file(event_path), f"{source.label}: source-resolved cache hash mismatch")
        require(
            manifest.get("checkpoint_sha256") == json.loads(source.manifest_path.read_text(encoding="utf-8"))["model"]["checkpoint_sha256"],
            f"{source.label}: source-resolved checkpoint hash mismatch",
        )
        with np.load(event_path, allow_pickle=False) as cache:
            payload = {key: cache[key] for key in cache.files}
        source_mass = finite_array(payload["source_token_mass"], f"{source.label}/source_token_mass").astype(np.float64)
        require(
            source_mass.shape == (2, TRIALS_EXPECTED, 7, 2, source.n_tokens),
            f"{source.label}: source-token-mass shape {source_mass.shape}",
        )
        require(bool(np.all(source_mass >= -1e-12)), f"{source.label}: negative source mass")
        combined = source_mass.sum(axis=-2)
        original = load_source(source)["token_mass"]
        require(
            bool(np.allclose(combined, original, atol=2e-5, rtol=2e-5)),
            f"{source.label}: visual+memory refresh does not reconstruct admitted combined cache",
        )
        shares = source_mass.sum(axis=-1)
        require(bool(np.allclose(shares.sum(axis=-1), 1.0, atol=2e-5)), f"{source.label}: source shares not normalized")
        result[source.label] = {
            "source_token_mass": source_mass,
            "source_share": shares,
        }
    require(
        set(result) == {source.label for source in cross_sources},
        "source-resolved cache does not cover every admitted cross-attention checkpoint",
    )
    return result


def trial_rows_for_source(
    source: Source,
    payload: dict[str, np.ndarray],
) -> tuple[list[dict[str, Any]], dict[str, np.ndarray]]:
    regions = quadrant_indices(source.grid_rows, source.grid_cols)
    metrics = common_quadrant_metrics(payload["token_mass"], regions)
    rows: list[dict[str, Any]] = []
    for condition_index, condition in enumerate(CONDITIONS):
        target = TARGET_QUADRANT[condition]
        cue = CUE_QUADRANT
        for window_name, frames in WINDOWS.items():
            window_metrics = {
                name: values[condition_index][:, list(frames), :].mean(axis=1)
                for name, values in metrics.items()
            }
            total = window_metrics["total_quadrant_mass"]
            peak_share = window_metrics["peak_patch_quadrant_share"]
            total_argmax = np.argmax(total, axis=-1)
            peak_argmax = np.argmax(peak_share, axis=-1)
            for trial_index in range(TRIALS_EXPECTED):
                other = [quadrant for quadrant in range(4) if quadrant != target]
                row = {
                    "label": source.label,
                    "feedback": source.feedback,
                    "grid": f"{source.grid_rows}x{source.grid_cols}",
                    "n_tokens": source.n_tokens,
                    "seed": source.seed,
                    "condition": condition,
                    "window": window_name,
                    "trial": trial_index,
                    "target_quadrant": target,
                    "cue_quadrant": cue,
                }
                for metric_name, values in window_metrics.items():
                    row[f"target_{metric_name}"] = float(values[trial_index, target])
                    row[f"cue_{metric_name}"] = float(values[trial_index, cue])
                row["target_minus_cue_total_mass"] = float(total[trial_index, target] - total[trial_index, cue])
                row["target_minus_other_total_mass"] = float(
                    total[trial_index, target] - total[trial_index, other].mean()
                )
                row["target_minus_cue_peak_share"] = float(
                    peak_share[trial_index, target] - peak_share[trial_index, cue]
                )
                row["target_minus_other_peak_share"] = float(
                    peak_share[trial_index, target] - peak_share[trial_index, other].mean()
                )
                row["target_argmax_total"] = int(total_argmax[trial_index] == target)
                row["target_argmax_peak"] = int(peak_argmax[trial_index] == target)
                rows.append(row)
    return rows, metrics


def source_trial_rows_for_source(
    source: Source,
    payload: dict[str, np.ndarray],
) -> list[dict[str, Any]]:
    """Compute source-specific metrics per held-out trial before averaging."""
    require(source.feedback == "crossattn1", "source trial rows require cross-attention")
    source_mass = finite_array(payload["source_token_mass"], f"{source.label}/source_token_mass").astype(np.float64)
    regions = quadrant_indices(source.grid_rows, source.grid_cols)
    rows: list[dict[str, Any]] = []
    for source_index, source_name in enumerate(("visual", "memory")):
        metrics = source_quadrant_metrics(source_mass[..., source_index, :], regions)
        for condition_index, condition in enumerate(CONDITIONS):
            target = TARGET_QUADRANT[condition]
            cue = CUE_QUADRANT
            other = [quadrant for quadrant in range(4) if quadrant != target]
            for window_name, frames in WINDOWS.items():
                frame_indices = list(frames)
                window_metrics = {
                    name: (
                        values[condition_index][:, frame_indices].mean(axis=1)
                        if values.ndim == 3
                        else values[condition_index][:, frame_indices, :].mean(axis=1)
                    )
                    for name, values in metrics.items()
                }
                total = window_metrics["raw_total_quadrant_mass"]
                peak = window_metrics["raw_peak_patch"]
                peak_share = window_metrics["peak_patch_quadrant_share"]
                for trial_index in range(TRIALS_EXPECTED):
                    row = {
                        "label": source.label,
                        "grid": f"{source.grid_rows}x{source.grid_cols}",
                        "n_tokens": source.n_tokens,
                        "seed": source.seed,
                        "condition": condition,
                        "window": window_name,
                        "source": source_name,
                        "trial": trial_index,
                        "target_quadrant": target,
                        "cue_quadrant": cue,
                        "source_total_share": float(window_metrics["source_total_share"][trial_index]),
                    }
                    for metric_name, values in window_metrics.items():
                        if metric_name == "source_total_share":
                            continue
                        row[f"target_{metric_name}"] = float(values[trial_index, target])
                        row[f"cue_{metric_name}"] = float(values[trial_index, cue])
                    row["target_minus_cue_raw_total_mass"] = float(total[trial_index, target] - total[trial_index, cue])
                    row["target_minus_other_raw_total_mass"] = float(total[trial_index, target] - total[trial_index, other].mean())
                    row["target_minus_cue_raw_peak"] = float(peak[trial_index, target] - peak[trial_index, cue])
                    row["target_minus_other_raw_peak"] = float(peak[trial_index, target] - peak[trial_index, other].mean())
                    row["target_minus_cue_peak_share"] = float(peak_share[trial_index, target] - peak_share[trial_index, cue])
                    row["target_minus_other_peak_share"] = float(peak_share[trial_index, target] - peak_share[trial_index, other].mean())
                    row["target_argmax_raw_total"] = int(np.argmax(total[trial_index]) == target)
                    row["target_argmax_raw_peak"] = int(np.argmax(peak[trial_index]) == target)
                    rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"no rows for {path}")
    fields = list(rows[0])
    require(all(list(row) == fields for row in rows), f"inconsistent fields for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def summarize_trials(trial_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = ("label", "feedback", "grid", "n_tokens", "seed", "condition", "window")
    metric_names = [
        key
        for key in trial_rows[0]
        if key not in set(keys) | {"trial", "target_quadrant", "cue_quadrant"}
    ]
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in trial_rows:
        groups.setdefault(tuple(row[key] for key in keys), []).append(row)
    summary: list[dict[str, Any]] = []
    for group_key, rows in sorted(groups.items()):
        base = dict(zip(keys, group_key))
        for metric_name in metric_names:
            values = np.asarray([row[metric_name] for row in rows], dtype=np.float64)
            mean, low, high = bootstrap_interval(
                values,
                seed_parts=group_key + (metric_name,),
            )
            summary.append(
                {
                    **base,
                    "metric": metric_name,
                    "n_trials": len(rows),
                    "mean": mean,
                    "ci95_low": low,
                    "ci95_high": high,
                    "interval_unit": "held-out trials",
                    "interval_method": f"percentile bootstrap ({BOOTSTRAP_DRAWS} draws)",
                }
            )
    return summary


def summarize_source_trials(trial_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = ("label", "grid", "n_tokens", "seed", "condition", "window", "source")
    excluded = set(keys) | {"trial", "target_quadrant", "cue_quadrant"}
    metric_names = [key for key in trial_rows[0] if key not in excluded]
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in trial_rows:
        groups.setdefault(tuple(row[key] for key in keys), []).append(row)
    summary: list[dict[str, Any]] = []
    for group_key, rows in sorted(groups.items()):
        base = dict(zip(keys, group_key))
        for metric_name in metric_names:
            values = np.asarray([row[metric_name] for row in rows], dtype=np.float64)
            mean, low, high = bootstrap_interval(values, seed_parts=("source",) + group_key + (metric_name,))
            summary.append(
                {
                    **base,
                    "metric": metric_name,
                    "n_trials": len(rows),
                    "mean": mean,
                    "ci95_low": low,
                    "ci95_high": high,
                    "interval_unit": "held-out trials",
                    "interval_method": f"percentile bootstrap ({BOOTSTRAP_DRAWS} draws)",
                }
            )
    return summary


def summarize_paired_grid_contrasts(trial_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Bootstrap within-trial grid contrasts from the common-random-number bank."""
    identity = ("feedback", "seed", "condition", "window", "n_tokens")
    excluded = set(identity) | {
        "label",
        "grid",
        "trial",
        "target_quadrant",
        "cue_quadrant",
    }
    metric_names = [key for key in trial_rows[0] if key not in excluded]
    cells: dict[tuple[Any, ...], dict[int, dict[str, Any]]] = {}
    for row in trial_rows:
        key = tuple(row[field] for field in identity)
        cells.setdefault(key, {})[int(row["trial"])] = row

    contrasts: list[dict[str, Any]] = []
    bases = sorted({key[:4] for key in cells})
    for feedback, seed, condition, window in bases:
        available = {
            int(key[4]): cells[key]
            for key in cells
            if key[:4] == (feedback, seed, condition, window)
        }
        for from_tokens, to_tokens in ((4, 16), (16, 100), (4, 100)):
            if from_tokens not in available or to_tokens not in available:
                continue
            from_trials = available[from_tokens]
            to_trials = available[to_tokens]
            trial_ids = sorted(set(from_trials) & set(to_trials))
            require(trial_ids == list(range(TRIALS_EXPECTED)), "paired grid contrast lost a common trial ID")
            for metric_name in metric_names:
                differences = np.asarray(
                    [
                        float(to_trials[trial_id][metric_name])
                        - float(from_trials[trial_id][metric_name])
                        for trial_id in trial_ids
                    ],
                    dtype=np.float64,
                )
                mean, low, high = bootstrap_interval(
                    differences,
                    seed_parts=(
                        "paired-grid",
                        feedback,
                        seed,
                        condition,
                        window,
                        from_tokens,
                        to_tokens,
                        metric_name,
                    ),
                )
                contrasts.append(
                    {
                        "feedback": feedback,
                        "seed": seed,
                        "condition": condition,
                        "window": window,
                        "from_n_tokens": from_tokens,
                        "to_n_tokens": to_tokens,
                        "contrast": f"{to_tokens}-{from_tokens}",
                        "metric": metric_name,
                        "n_paired_trials": len(trial_ids),
                        "mean_difference": mean,
                        "ci95_low": low,
                        "ci95_high": high,
                        "interval_unit": "paired held-out trial IDs",
                        "interval_method": f"paired percentile bootstrap ({BOOTSTRAP_DRAWS} draws)",
                    }
                )
    return contrasts


def metric_definitions() -> list[dict[str, str]]:
    return [
        {
            "metric": "paired_location_patch_column_score",
            "formula": "p_j = mean_i (A^visual_ij + A^memory_ij)",
            "uniform_baseline": "1/N",
            "interpretation": "secondary visual+memory paired-location total; never substituted for either source map or maximum",
        },
        {
            "metric": "source_patch_column_score",
            "formula": "p^s_j = mean_i A^s_ij, computed separately for visual and recurrent-memory keys",
            "uniform_baseline": "1/(2N) under globally uniform joint-key attention",
            "interpretation": "primary source-resolved mean incoming attention, retaining visual-versus-memory allocation",
        },
        {
            "metric": "total_quadrant_mass",
            "formula": "sum_{j in quadrant} p_j",
            "uniform_baseline": "0.25",
            "interpretation": "total routing allocated to one fixed physical quadrant",
        },
        {
            "metric": "peak_patch_raw",
            "formula": "max_{j in quadrant} p_j",
            "uniform_baseline": "1/N",
            "interpretation": "user-requested maximum patch score inside a quadrant",
        },
        {
            "metric": "peak_patch_uniform_ratio",
            "formula": "N * max_{j in quadrant} p_j",
            "uniform_baseline": "1",
            "interpretation": "peak patch strength relative to a uniform native map",
        },
        {
            "metric": "peak_patch_quadrant_share",
            "formula": "max_{j in q} p_j / sum_r max_{j in r} p_j",
            "uniform_baseline": "0.25",
            "interpretation": "common-four-quadrant normalization of the peak-patch statistic",
        },
        {
            "metric": "within_quadrant_peak_ratio",
            "formula": "(N/4) * max_{j in q} p_j / sum_{j in q} p_j",
            "uniform_baseline": "1",
            "interpretation": "within-quadrant focality; identically 1 at native 2x2",
        },
        {
            "metric": "source_total_share",
            "formula": "sum_k mean_i A_ik within one cross-attention source block",
            "uniform_baseline": "0.5 under globally uniform image+memory attention",
            "interpretation": "visual-key versus recurrent-memory-key allocation, computed per held-out trial in the source-resolved refresh",
        },
        {
            "metric": "source_raw_total_quadrant_mass",
            "formula": "sum_{j in quadrant} p^s_j",
            "uniform_baseline": "0.125 under globally uniform joint-key attention",
            "interpretation": "raw source-specific routing to one fixed physical quadrant",
        },
        {
            "metric": "source_raw_peak_patch",
            "formula": "max_{j in quadrant} p^s_j",
            "uniform_baseline": "1/(2N) under globally uniform joint-key attention",
            "interpretation": "source-specific maximum patch score, computed after splitting visual and memory keys",
        },
        {
            "metric": "source_raw_peak_patch_uniform_ratio",
            "formula": "2N * max_{j in quadrant} p^s_j",
            "uniform_baseline": "1",
            "interpretation": "source-specific peak strength relative to a globally uniform cross-attention key",
        },
        {
            "metric": "source_conditional_quadrant_mass",
            "formula": "source-specific quadrant mass / source_total_share",
            "uniform_baseline": "0.25",
            "interpretation": "spatial localization conditional on attending to that source; descriptive mean only in the retained cache",
        },
    ]


def configure_matplotlib() -> Any:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10.0,
            "axes.titlesize": 11.0,
            "axes.labelsize": 10.0,
            "xtick.labelsize": 9.0,
            "ytick.labelsize": 9.0,
            "legend.fontsize": 9.0,
            "figure.titlesize": 13.0,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    return plt


def save_figure(figure: Any, base: Path) -> None:
    figure.savefig(base.with_suffix(".pdf"), bbox_inches="tight")
    figure.savefig(base.with_suffix(".png"), dpi=320, bbox_inches="tight")


def lookup_summary(
    summary_rows: list[dict[str, Any]],
    *,
    feedback: str,
    n_tokens: int,
    seed: int,
    condition: str,
    window: str,
    metric: str,
) -> dict[str, Any]:
    matches = [
        row
        for row in summary_rows
        if row["feedback"] == feedback
        and int(row["n_tokens"]) == n_tokens
        and int(row["seed"]) == seed
        and row["condition"] == condition
        and row["window"] == window
        and row["metric"] == metric
    ]
    require(len(matches) == 1, f"summary lookup expected one row, found {len(matches)}")
    return matches[0]


def lookup_source_summary(
    summary_rows: list[dict[str, Any]],
    *,
    n_tokens: int,
    seed: int,
    condition: str,
    window: str,
    source: str,
    metric: str,
) -> dict[str, Any]:
    matches = [
        row
        for row in summary_rows
        if int(row["n_tokens"]) == n_tokens
        and int(row["seed"]) == seed
        and row["condition"] == condition
        and row["window"] == window
        and row["source"] == source
        and row["metric"] == metric
    ]
    require(len(matches) == 1, f"source summary lookup expected one row, found {len(matches)}")
    return matches[0]


def plot_seed0_measure_comparison(
    plt: Any,
    summary_rows: list[dict[str, Any]],
    output: Path,
) -> None:
    panels = [
        ("target_total_quadrant_mass", "A  Total target-quadrant mass", "mass", 0.25),
        ("target_peak_patch_raw", "B  Peak patch: raw column mean", "raw patch score", None),
        ("target_peak_patch_uniform_ratio", "C  Peak patch / uniform patch", "ratio", 1.0),
        ("target_peak_patch_quadrant_share", "D  Peak-patch quadrant share", "share", 0.25),
        ("target_minus_other_peak_share", "E  Peak-share target selectivity", "target - mean(other)", 0.0),
        ("target_within_quadrant_peak_ratio", "F  Within-quadrant peak focality", "ratio", 1.0),
    ]
    figure, axes = plt.subplots(2, 3, figsize=(12.4, 7.3), constrained_layout=True)
    x = np.arange(3)
    tokens = (4, 16, 100)
    for axis, (metric, title, ylabel, baseline) in zip(axes.ravel(), panels):
        for feedback in ("crossattn1", "affine_ew"):
            style = FEEDBACK_STYLE[feedback]
            for condition, linestyle, fill in (
                ("valid", "-", style["color"]),
                ("invalid", "--", "white"),
            ):
                records = [
                    lookup_summary(
                        summary_rows,
                        feedback=feedback,
                        n_tokens=n_tokens,
                        seed=0,
                        condition=condition,
                        window="frame5",
                        metric=metric,
                    )
                    for n_tokens in tokens
                ]
                means = np.asarray([record["mean"] for record in records])
                low = np.asarray([record["ci95_low"] for record in records])
                high = np.asarray([record["ci95_high"] for record in records])
                axis.errorbar(
                    x,
                    means,
                    yerr=np.vstack([means - low, high - means]),
                    color=style["color"],
                    linestyle=linestyle,
                    marker=style["marker"],
                    markerfacecolor=fill,
                    markeredgecolor=style["color"],
                    markeredgewidth=1.3,
                    linewidth=1.8,
                    capsize=2.5,
                    label=f"{style['label']} - {condition}",
                )
        if baseline is not None:
            axis.axhline(baseline, color="#6F6F6F", linestyle=":", linewidth=1.2)
        if metric == "target_peak_patch_raw":
            axis.plot(x, [1.0 / n for n in tokens], color="#6F6F6F", linestyle=":", linewidth=1.2)
            axis.text(1.06, 0.073, "uniform 1/N", color="#555555", fontsize=8.5)
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_ylabel(ylabel)
        axis.set_xticks(x, ["4\n(2x2)", "16\n(4x4)", "100\n(10x10)"])
        axis.set_xlabel("native sensory / memory tokens")
        axis.grid(axis="y", alpha=0.22)
    axes[0, 0].legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(1.65, 1.28))
    figure.suptitle(
        "VDA4 paired-location routing depends on the named common-grid measure (held-out seed 0)",
        fontweight="bold",
        y=1.04,
    )
    figure.text(
        0.5,
        -0.025,
        "Secondary paired-location diagnostic: cross-attention adds co-located visual+memory columns; it is not either source map or maximum. "
        "Points are 128 held-out trials at change-onset frame 5; bars are trial-bootstrap 95% CIs. "
        "Frame 6 and the frames 5-6 mean are reported separately in the companion figure and tables.",
        ha="center",
        va="top",
        fontsize=9.0,
        color="#444444",
    )
    save_figure(figure, output / "attention_measure_comparison_seed0")
    plt.close(figure)


def plot_framewise(
    plt: Any,
    summary_rows: list[dict[str, Any]],
    output: Path,
) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(11.2, 7.2), constrained_layout=False)
    figure.subplots_adjust(left=0.07, right=0.985, bottom=0.10, top=0.79, wspace=0.12, hspace=0.30)
    panel_specs = [
        ("crossattn1", "target_total_quadrant_mass", "A  Cross-attn V+M paired-location total", "mass"),
        ("crossattn1", "target_peak_patch_quadrant_share", "B  Cross-attn V+M paired-location peak share", "share"),
        ("affine_ew", "target_total_quadrant_mass", "C  Affine EW: total quadrant mass", "mass"),
        ("affine_ew", "target_peak_patch_quadrant_share", "D  Affine EW: peak-patch share", "share"),
    ]
    for axis, (feedback, metric, title, ylabel) in zip(axes.ravel(), panel_specs):
        for n_tokens, marker in ((4, "o"), (16, "s"), (100, "^")):
            if feedback == "crossattn1" or n_tokens in (4, 16, 100):
                color = GRID_COLORS[n_tokens]
                for condition, linestyle, fill in (
                    ("valid", "-", color),
                    ("invalid", "--", "white"),
                ):
                    records = [
                        lookup_summary(
                            summary_rows,
                            feedback=feedback,
                            n_tokens=n_tokens,
                            seed=0,
                            condition=condition,
                            window=window,
                            metric=metric,
                        )
                        for window in ("frame5", "frame6")
                    ]
                    means = np.asarray([record["mean"] for record in records])
                    low = np.asarray([record["ci95_low"] for record in records])
                    high = np.asarray([record["ci95_high"] for record in records])
                    axis.errorbar(
                        [5, 6],
                        means,
                        yerr=np.vstack([means - low, high - means]),
                        color=color,
                        linestyle=linestyle,
                        marker=marker,
                        markerfacecolor=fill,
                        markeredgecolor=color,
                        capsize=2.3,
                        linewidth=1.6,
                        label=f"{n_tokens} tokens - {condition}",
                    )
        axis.axhline(0.25, color="#6F6F6F", linestyle=":", linewidth=1.1)
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_ylabel(ylabel)
        axis.set_xticks([5, 6])
        axis.set_xlabel("event / response frame")
        axis.grid(axis="y", alpha=0.22)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    figure.legend(handles, labels, frameon=False, ncol=3, fontsize=8.3, loc="upper center", bbox_to_anchor=(0.5, 0.895))
    figure.suptitle("Frame 5 and frame 6 must not be treated as interchangeable", fontweight="bold", y=0.985)
    figure.text(
        0.5,
        0.015,
        "Target is TL on valid trials and BR on invalid trials; cue remains TL. "
        "Points are held-out trial means with trial-bootstrap 95% CIs (n=128 per condition).",
        ha="center",
        va="top",
        fontsize=9.0,
        color="#444444",
    )
    save_figure(figure, output / "attention_framewise_comparison_seed0")
    plt.close(figure)


def plot_projected_maps(
    plt: Any,
    sources: list[Source],
    payloads: dict[str, dict[str, np.ndarray]],
    output: Path,
) -> None:
    seed0 = sorted(
        [source for source in sources if source.seed == 0],
        key=lambda source: ((0 if source.feedback == "crossattn1" else 1), source.n_tokens),
    )
    figure, axes = plt.subplots(len(seed0), 4, figsize=(8.9, 11.7), constrained_layout=True)
    column_titles = (
        "Valid: total mass",
        "Valid: peak-patch share",
        "Invalid: total mass",
        "Invalid: peak-patch share",
    )
    image = None
    for row_index, source in enumerate(seed0):
        payload = payloads[source.label]
        metrics = common_quadrant_metrics(
            payload["token_mass"],
            quadrant_indices(source.grid_rows, source.grid_cols),
        )
        total = metrics["total_quadrant_mass"][:, :, 5, :].mean(axis=1)
        peak_share = metrics["peak_patch_quadrant_share"][:, :, 5, :].mean(axis=1)
        maps = (total[0], peak_share[0], total[1], peak_share[1])
        for column_index, vector in enumerate(maps):
            axis = axes[row_index, column_index]
            image = axis.imshow(vector.reshape(2, 2), cmap="viridis", vmin=0.0, vmax=1.0, interpolation="nearest")
            for quadrant, value in enumerate(vector):
                r, c = divmod(quadrant, 2)
                axis.text(c, r, f"{value:.2f}", ha="center", va="center", color="white" if value > 0.48 else "black", fontsize=8.5, fontweight="bold")
            axis.set_xticks([])
            axis.set_yticks([])
            if row_index == 0:
                axis.set_title(column_titles[column_index], fontsize=10.0, fontweight="bold")
            if column_index == 0:
                axis.set_ylabel(
                    f"{'Cross-attn V+M' if source.feedback == 'crossattn1' else FEEDBACK_STYLE[source.feedback]['label']}\n{source.grid_rows}x{source.grid_cols}",
                    fontsize=9.5,
                    fontweight="bold",
                )
            target = 0 if column_index < 2 else 3
            tr, tc = divmod(target, 2)
            axis.add_patch(plt.Rectangle((tc - 0.48, tr - 0.48), 0.96, 0.96, fill=False, edgecolor="#D55E00", linewidth=2.0))
            if column_index >= 2:
                axis.add_patch(plt.Rectangle((-0.45, -0.45), 0.9, 0.9, fill=False, edgecolor="white", linewidth=1.2, linestyle="--"))
    if image is not None:
        figure.colorbar(image, ax=axes.ravel().tolist(), fraction=0.022, pad=0.015, label="common 2x2 quadrant score")
    figure.suptitle(
        "Every native grid projected onto the same four physical VDA4 quadrants",
        fontweight="bold",
    )
    figure.text(
        0.5,
        -0.01,
        "Orange outline = true change quadrant; dashed white outline on invalid trials = TL cue. "
        "Values average 128 held-out trials at change-onset frame 5. Cross-attention rows are a secondary co-located V+M total; source maps are shown separately.",
        ha="center",
        va="top",
        fontsize=8.8,
        color="#444444",
    )
    save_figure(figure, output / "attention_common_2x2_maps_seed0")
    plt.close(figure)


def plot_native_maps(
    plt: Any,
    sources: list[Source],
    payloads: dict[str, dict[str, np.ndarray]],
    output: Path,
) -> None:
    seed0 = sorted(
        [source for source in sources if source.seed == 0],
        key=lambda source: ((0 if source.feedback == "crossattn1" else 1), source.n_tokens),
    )
    arrays: list[np.ndarray] = []
    for source in seed0:
        token_mass = payloads[source.label]["token_mass"][:, :, 5, :].mean(axis=1)
        arrays.extend([np.log2(np.maximum(source.n_tokens * token_mass[index], 1e-6)) for index in range(2)])
    limit = max(2.0, float(np.ceil(max(np.abs(array).max() for array in arrays))))
    figure, axes = plt.subplots(len(seed0), 2, figsize=(6.7, 12.0), constrained_layout=True)
    image = None
    for row_index, source in enumerate(seed0):
        token_mass = payloads[source.label]["token_mass"][:, :, 5, :].mean(axis=1)
        for condition_index, condition in enumerate(CONDITIONS):
            axis = axes[row_index, condition_index]
            native = np.log2(np.maximum(source.n_tokens * token_mass[condition_index], 1e-6)).reshape(source.grid_rows, source.grid_cols)
            image = axis.imshow(native, cmap="coolwarm", vmin=-limit, vmax=limit, interpolation="nearest")
            axis.axvline(source.grid_cols / 2 - 0.5, color="black", linewidth=1.0)
            axis.axhline(source.grid_rows / 2 - 0.5, color="black", linewidth=1.0)
            axis.set_xticks([])
            axis.set_yticks([])
            if row_index == 0:
                axis.set_title(f"{condition.capitalize()} change", fontweight="bold")
            if condition_index == 0:
                axis.set_ylabel(
                    f"{'Cross-attn V+M' if source.feedback == 'crossattn1' else FEEDBACK_STYLE[source.feedback]['label']}\n{source.grid_rows}x{source.grid_cols}",
                    fontweight="bold",
                    fontsize=9.5,
                )
    if image is not None:
        figure.colorbar(image, ax=axes.ravel().tolist(), fraction=0.025, pad=0.015, label="log2(patch score / uniform 1/N)")
    figure.suptitle("Native token maps expose within-quadrant peaks hidden by total mass", fontweight="bold")
    figure.text(
        0.5,
        -0.01,
        "Shared color scale across all native grids. Black lines are the fixed physical 2x2 quadrant boundaries. "
        "Maps average 128 held-out trials at change-onset frame 5. Cross-attention rows add co-located V+M only as a secondary diagnostic.",
        ha="center",
        va="top",
        fontsize=8.8,
        color="#444444",
    )
    save_figure(figure, output / "attention_native_patch_maps_seed0")
    plt.close(figure)


def plot_endpoint_replication(
    plt: Any,
    summary_rows: list[dict[str, Any]],
    output: Path,
) -> None:
    panels = [
        ("target_total_quadrant_mass", "A  Total target-quadrant mass", "mass"),
        ("target_peak_patch_quadrant_share", "B  Peak-patch quadrant share", "share"),
        ("target_minus_cue_total_mass", "C  Invalid target - cue: total mass", "contrast"),
        ("target_minus_cue_peak_share", "D  Invalid target - cue: peak share", "contrast"),
    ]
    figure, axes = plt.subplots(2, 2, figsize=(8.7, 7.2), constrained_layout=True)
    for axis, (metric, title, ylabel) in zip(axes.ravel(), panels):
        conditions = ("invalid",) if "minus_cue" in metric else CONDITIONS
        for seed, color, marker in ((0, "#1f6fb2", "o"), (1, "#D55E00", "s")):
            for condition, linestyle, fill in (
                [(condition, "-" if condition == "valid" else "--", color if condition == "valid" else "white") for condition in conditions]
            ):
                records = [
                    lookup_summary(
                        summary_rows,
                        feedback="crossattn1",
                        n_tokens=n_tokens,
                        seed=seed,
                        condition=condition,
                        window="frame5",
                        metric=metric,
                    )
                    for n_tokens in (4, 100)
                ]
                means = np.asarray([record["mean"] for record in records])
                low = np.asarray([record["ci95_low"] for record in records])
                high = np.asarray([record["ci95_high"] for record in records])
                axis.errorbar(
                    [0, 1],
                    means,
                    yerr=np.vstack([means - low, high - means]),
                    color=color,
                    linestyle=linestyle,
                    marker=marker,
                    markerfacecolor=fill,
                    markeredgecolor=color,
                    capsize=2.5,
                    linewidth=1.7,
                    label=f"seed {seed} - {condition}" if len(conditions) > 1 else f"seed {seed}",
                )
        axis.axhline(0.25 if "target_" in metric and "minus" not in metric else 0.0, color="#6F6F6F", linestyle=":", linewidth=1.1)
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_ylabel(ylabel)
        axis.set_xticks([0, 1], ["4\n(2x2)", "100\n(10x10)"])
        axis.set_xlabel("native sensory / memory tokens")
        axis.grid(axis="y", alpha=0.22)
    axes[0, 0].legend(frameon=False, ncol=2, fontsize=8.4)
    axes[1, 0].legend(frameon=False, ncol=2, fontsize=8.4)
    figure.suptitle("Cross-attention paired-location endpoint replication is estimand-dependent", fontweight="bold")
    figure.text(
        0.5,
        -0.02,
        "Each line is one independently trained checkpoint; V+M co-located totals are secondary, not source maps. Points average 128 held-out trials at frame 5; "
        "bars are trial-bootstrap 95% CIs, not training-population intervals.",
        ha="center",
        va="top",
        fontsize=8.8,
        color="#444444",
    )
    save_figure(figure, output / "attention_endpoint_replication_multimetric")
    plt.close(figure)


def plot_cross_attention_source_metrics(
    plt: Any,
    source_summary_rows: list[dict[str, Any]],
    output: Path,
) -> None:
    """Plot multiple named source-specific measures with trial intervals."""
    panels = (
        ("source_total_share", "A  Source share", "raw share", 0.5),
        ("target_raw_total_quadrant_mass", "B  Target-quadrant total", "raw mass", 0.125),
        ("target_raw_peak_patch", "C  Target-quadrant maximum patch", "raw patch mass", None),
        ("target_raw_peak_patch_uniform_ratio", "D  Maximum / global-uniform key", "ratio", 1.0),
        ("target_conditional_total_quadrant_mass", "E  Target total | source", "conditional mass", 0.25),
        ("target_peak_patch_quadrant_share", "F  Peak-quadrant share | source", "conditional share", 0.25),
    )
    source_style = {
        "visual": {"color": "#009E73", "marker": "o", "label": "Visual keys"},
        "memory": {"color": "#CC79A7", "marker": "s", "label": "Recurrent-memory keys"},
    }
    tokens = (4, 16, 100)
    x = np.arange(len(tokens))
    figure, axes = plt.subplots(2, 3, figsize=(12.2, 7.4), constrained_layout=True)
    for axis, (metric, title, ylabel, baseline) in zip(axes.ravel(), panels):
        for source_name in ("visual", "memory"):
            style = source_style[source_name]
            for condition, linestyle, fill in (("valid", "-", style["color"]), ("invalid", "--", "white")):
                records = [
                    lookup_source_summary(
                        source_summary_rows,
                        n_tokens=n_tokens,
                        seed=0,
                        condition=condition,
                        window="frame5",
                        source=source_name,
                        metric=metric,
                    )
                    for n_tokens in tokens
                ]
                means = np.asarray([record["mean"] for record in records])
                low = np.asarray([record["ci95_low"] for record in records])
                high = np.asarray([record["ci95_high"] for record in records])
                axis.errorbar(
                    x,
                    means,
                    yerr=np.vstack([means - low, high - means]),
                    color=style["color"],
                    linestyle=linestyle,
                    marker=style["marker"],
                    markerfacecolor=fill,
                    markeredgecolor=style["color"],
                    capsize=2.4,
                    linewidth=1.7,
                    label=f"{style['label']} - {condition}",
                )
        if baseline is not None:
            axis.axhline(baseline, color="#666666", linestyle=":", linewidth=1.1)
        if metric == "target_raw_peak_patch":
            axis.plot(x, [1.0 / (2.0 * n) for n in tokens], color="#666666", linestyle=":", linewidth=1.1)
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_ylabel(ylabel)
        axis.set_xticks(x, ["4\n(2x2)", "16\n(4x4)", "100\n(10x10)"])
        axis.set_xlabel("native visual / memory tokens")
        axis.grid(axis="y", alpha=0.22)
    axes[0, 0].legend(frameon=False, ncol=2, fontsize=8.0, loc="upper center", bbox_to_anchor=(1.65, 1.30))
    figure.suptitle("Cross-attention visual and recurrent-memory sources remain separate", fontweight="bold", y=1.04)
    figure.text(
        0.5,
        -0.025,
        "Each source is split before query averaging and before the quadrant maximum. Raw panels preserve joint-softmax source mass; "
        "conditional panels answer localization given that source. Points are means of 128 held-out trials at frame 5 with trial-bootstrap 95% CIs.",
        ha="center",
        va="top",
        fontsize=8.9,
        color="#444444",
    )
    save_figure(figure, output / "attention_crossattn_source_metrics_seed0")
    plt.close(figure)


def plot_cross_attention_source_common_grid(
    plt: Any,
    sources: list[Source],
    source_payloads: dict[str, dict[str, np.ndarray]],
    output: Path,
) -> None:
    """Display raw source-specific quadrant totals and maxima on a common grid."""
    cross_seed0 = sorted(
        [source for source in sources if source.feedback == "crossattn1" and source.seed == 0],
        key=lambda source: source.n_tokens,
    )
    rows: list[tuple[Source, str, dict[str, np.ndarray]]] = []
    total_arrays: list[np.ndarray] = []
    peak_arrays: list[np.ndarray] = []
    for source in cross_seed0:
        mass = source_payloads[source.label]["source_token_mass"]
        for source_index, source_name in enumerate(("visual", "memory")):
            metrics = source_quadrant_metrics(mass[..., source_index, :], quadrant_indices(source.grid_rows, source.grid_cols))
            rows.append((source, source_name, metrics))
            total_arrays.append(metrics["raw_total_quadrant_mass"][:, :, 5].mean(axis=1))
            peak_arrays.append(metrics["raw_peak_patch"][:, :, 5].mean(axis=1))
    total_vmax = float(max(array.max() for array in total_arrays))
    peak_vmax = float(max(array.max() for array in peak_arrays))
    figure, axes = plt.subplots(len(rows), 4, figsize=(8.5, 11.0), constrained_layout=False)
    figure.subplots_adjust(left=0.16, right=0.82, top=0.92, bottom=0.075, wspace=0.08, hspace=0.08)
    total_image = peak_image = None
    titles = (
        "Valid\nquadrant total",
        "Valid\nmaximum patch",
        "Invalid\nquadrant total",
        "Invalid\nmaximum patch",
    )
    for row_index, (source, source_name, metrics) in enumerate(rows):
        total = metrics["raw_total_quadrant_mass"][:, :, 5].mean(axis=1)
        peak = metrics["raw_peak_patch"][:, :, 5].mean(axis=1)
        shares = metrics["source_total_share"][:, :, 5].mean(axis=1)
        vectors = (total[0], peak[0], total[1], peak[1])
        for column_index, vector in enumerate(vectors):
            axis = axes[row_index, column_index]
            vmax = total_vmax if column_index % 2 == 0 else peak_vmax
            image = axis.imshow(vector.reshape(2, 2), cmap="magma", vmin=0.0, vmax=vmax, interpolation="nearest")
            if column_index % 2 == 0:
                total_image = image
            else:
                peak_image = image
            for quadrant, value in enumerate(vector):
                r, c = divmod(quadrant, 2)
                axis.text(c, r, f"{value:.3f}", ha="center", va="center", color="black" if value > 0.55 * vmax else "white", fontsize=7.8, fontweight="bold")
            axis.set_xticks([])
            axis.set_yticks([])
            if row_index == 0:
                axis.set_title(titles[column_index], fontsize=8.7, fontweight="bold", pad=4.0)
            if column_index == 0:
                axis.set_ylabel(
                    f"{source.grid_rows}x{source.grid_cols} {source_name}\n"
                    f"$w$={shares[0]:.3f}/{shares[1]:.3f}",
                    fontsize=8.1,
                    fontweight="bold",
                )
            condition = "valid" if column_index < 2 else "invalid"
            target = TARGET_QUADRANT[condition]
            tr, tc = divmod(target, 2)
            axis.add_patch(plt.Rectangle((tc - 0.48, tr - 0.48), 0.96, 0.96, fill=False, edgecolor="#E69F00", linewidth=2.0))
            if condition == "invalid":
                axis.add_patch(plt.Rectangle((-0.45, -0.45), 0.9, 0.9, fill=False, edgecolor="#56B4E9", linewidth=1.2, linestyle="--"))
    if total_image is not None:
        total_colorbar_axis = figure.add_axes([0.855, 0.56, 0.020, 0.25])
        figure.colorbar(total_image, cax=total_colorbar_axis, label="raw source quadrant total")
    if peak_image is not None:
        peak_colorbar_axis = figure.add_axes([0.855, 0.22, 0.020, 0.25])
        figure.colorbar(peak_image, cax=peak_colorbar_axis, label="raw source maximum patch")
    figure.suptitle(
        "Source-specific frame-5 totals and maxima on the same physical 2x2 grid",
        y=0.972,
        fontweight="bold",
    )
    figure.text(
        0.5,
        0.018,
        "Visual and recurrent-memory keys are never added before the maximum. Each measure uses one scale shared across both sources and all grids.\n"
        "Orange = true change, dashed blue = cue on forced-invalid trials, and $w$ is valid/invalid source share. "
        "Values are means of per-trial scores (n=128).",
        ha="center",
        va="top",
        fontsize=8.6,
        color="#444444",
    )
    save_figure(figure, output / "attention_crossattn_source_common_2x2_seed0")
    plt.close(figure)


def plot_cross_attention_source_timecourses(
    plt: Any,
    sources: list[Source],
    source_payloads: dict[str, dict[str, np.ndarray]],
    output: Path,
) -> None:
    """Repeat the established separate-source, seven-frame VDA4 display."""
    cross_seed0 = sorted(
        [source for source in sources if source.feedback == "crossattn1" and source.seed == 0],
        key=lambda source: source.n_tokens,
    )
    row_specs = ((0, 0, "Visual - valid"), (1, 0, "Visual - invalid"), (0, 1, "Memory - valid"), (1, 1, "Memory - invalid"))
    for source in cross_seed0:
        source_mass = source_payloads[source.label]["source_token_mass"]
        means = source_mass.mean(axis=1)
        shares = source_mass.sum(axis=-1).mean(axis=1)
        vmax = float(means.max())
        figure, axes = plt.subplots(4, 7, figsize=(11.3, 6.6), constrained_layout=True)
        image = None
        for row_index, (condition_index, source_index, row_label) in enumerate(row_specs):
            for frame in range(7):
                axis = axes[row_index, frame]
                native = means[condition_index, frame, source_index].reshape(source.grid_rows, source.grid_cols)
                image = axis.imshow(native, cmap="magma", vmin=0.0, vmax=vmax, interpolation="nearest")
                axis.axvline(source.grid_cols / 2 - 0.5, color="black", linewidth=0.75)
                axis.axhline(source.grid_rows / 2 - 0.5, color="black", linewidth=0.75)
                axis.set_xticks([])
                axis.set_yticks([])
                if row_index == 0:
                    axis.set_title(f"t{frame}", fontweight="bold")
                if frame == 0:
                    axis.set_ylabel(row_label, fontsize=9.0, fontweight="bold")
                # Cue is always the top-left physical quadrant.
                half_rows, half_cols = source.grid_rows // 2, source.grid_cols // 2
                axis.add_patch(plt.Rectangle((-0.48, -0.48), half_cols - 0.04, half_rows - 0.04, fill=False, edgecolor="#56B4E9", linewidth=1.2, linestyle="--"))
                if frame >= 5:
                    target = TARGET_QUADRANT[CONDITIONS[condition_index]]
                    tr, tc = divmod(target, 2)
                    axis.add_patch(plt.Rectangle((tc * half_cols - 0.48, tr * half_rows - 0.48), half_cols - 0.04, half_rows - 0.04, fill=False, edgecolor="#E69F00", linewidth=1.5))
                axis.text(
                    0.03,
                    0.96,
                    f"w={shares[condition_index, frame, source_index]:.2f}",
                    transform=axis.transAxes,
                    ha="left",
                    va="top",
                    fontsize=6.8,
                    bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.72, "pad": 1.0},
                )
        if image is not None:
            figure.colorbar(image, ax=axes.ravel().tolist(), fraction=0.016, pad=0.010, label="raw query-averaged source-key mass")
        figure.suptitle(
            f"VDA4 cross-attention {source.grid_rows}x{source.grid_cols}: visual and recurrent-memory keys, t0-t6",
            fontweight="bold",
        )
        figure.text(
            0.5,
            -0.012,
            "One raw zero-to-observed-maximum scale is shared by visual and memory rows. Dashed blue outlines the cue; orange outlines the true change from t5. "
            "Each map averages 128 held-out trials; w is the source's joint-softmax share.",
            ha="center",
            va="top",
            fontsize=8.5,
            color="#444444",
        )
        save_figure(figure, output / f"attention_crossattn_source_timecourse_grid{source.grid_rows}x{source.grid_cols}_seed0")
        plt.close(figure)


def plot_cross_attention_sources(
    plt: Any,
    sources: list[Source],
    payloads: dict[str, dict[str, np.ndarray]],
    output: Path,
) -> None:
    cross_seed0 = sorted(
        [source for source in sources if source.feedback == "crossattn1" and source.seed == 0],
        key=lambda source: source.n_tokens,
    )
    maps: dict[tuple[str, str, str], np.ndarray] = {}
    source_shares: dict[tuple[str, str, str], float] = {}
    all_arrays: list[np.ndarray] = []
    for source in cross_seed0:
        decomposed = source_patch_column_scores(payloads[source.label]["raw_attention_mean"], source.n_tokens)
        raw_mean = payloads[source.label]["raw_attention_mean"]
        for condition_index, condition in enumerate(CONDITIONS):
            for source_name in ("visual", "memory"):
                spatial = decomposed[source_name][condition_index, 5]
                maps[(source.label, condition, source_name)] = spatial
                all_arrays.append(spatial)
                block = raw_mean[condition_index, 5, :, : source.n_tokens]
                if source_name == "memory":
                    block = raw_mean[condition_index, 5, :, source.n_tokens :]
                source_shares[(source.label, condition, source_name)] = float(block.mean(axis=-2).sum())
    limit = float(max(array.max() for array in all_arrays))
    figure, axes = plt.subplots(3, 4, figsize=(8.2, 6.8), constrained_layout=True)
    titles = ("Valid visual keys", "Valid memory keys", "Invalid visual keys", "Invalid memory keys")
    image = None
    for row_index, source in enumerate(cross_seed0):
        specs = (("valid", "visual"), ("valid", "memory"), ("invalid", "visual"), ("invalid", "memory"))
        for column_index, (condition, source_name) in enumerate(specs):
            axis = axes[row_index, column_index]
            native = maps[(source.label, condition, source_name)].reshape(source.grid_rows, source.grid_cols)
            image = axis.imshow(native, cmap="magma", vmin=0.0, vmax=limit, interpolation="nearest")
            axis.axvline(source.grid_cols / 2 - 0.5, color="black", linewidth=0.9)
            axis.axhline(source.grid_rows / 2 - 0.5, color="black", linewidth=0.9)
            axis.set_xticks([])
            axis.set_yticks([])
            axis.text(
                0.03,
                0.96,
                f"source share={source_shares[(source.label, condition, source_name)]:.3f}",
                transform=axis.transAxes,
                ha="left",
                va="top",
                fontsize=8.2,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 1.8},
            )
            if row_index == 0:
                axis.set_title(titles[column_index], fontsize=9.5, fontweight="bold")
            if column_index == 0:
                axis.set_ylabel(f"{source.grid_rows}x{source.grid_cols}", fontweight="bold")
    if image is not None:
        figure.colorbar(image, ax=axes.ravel().tolist(), fraction=0.025, pad=0.015, label="raw query-averaged source-key mass")
    figure.suptitle("Cross-attention visual and recurrent-memory key maps must be shown separately", fontweight="bold")
    figure.text(
        0.5,
        -0.015,
        "Visual and memory blocks are split before query averaging and are not normalized within source. One raw scale is shared across all panels, "
        "so contrast preserves the source-share difference printed in each panel. This compact frame-5 view complements the trialwise seven-frame plates.",
        ha="center",
        va="top",
        fontsize=8.7,
        color="#444444",
    )
    save_figure(figure, output / "attention_crossattn_source_maps_seed0")
    plt.close(figure)


def build_summary_payload(
    sources: list[Source],
    summary_rows: list[dict[str, Any]],
    source_summary_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    def value(feedback: str, tokens: int, seed: int, condition: str, metric: str, window: str = "frame5") -> float:
        return float(
            lookup_summary(
                summary_rows,
                feedback=feedback,
                n_tokens=tokens,
                seed=seed,
                condition=condition,
                window=window,
                metric=metric,
            )["mean"]
        )

    selected: list[dict[str, Any]] = []
    for feedback in ("crossattn1", "affine_ew"):
        for tokens in (4, 16, 100):
            selected.append(
                {
                    "feedback": feedback,
                    "n_tokens": tokens,
                    "seed": 0,
                    "primary_window": "frame5",
                    "valid_target_total_mass_frame5": value(feedback, tokens, 0, "valid", "target_total_quadrant_mass"),
                    "valid_target_peak_share_frame5": value(feedback, tokens, 0, "valid", "target_peak_patch_quadrant_share"),
                    "invalid_target_total_mass_frame5": value(feedback, tokens, 0, "invalid", "target_total_quadrant_mass"),
                    "invalid_target_peak_share_frame5": value(feedback, tokens, 0, "invalid", "target_peak_patch_quadrant_share"),
                    "valid_target_total_mass_frame6": value(feedback, tokens, 0, "valid", "target_total_quadrant_mass", "frame6"),
                    "valid_target_peak_share_frame6": value(feedback, tokens, 0, "valid", "target_peak_patch_quadrant_share", "frame6"),
                    "valid_target_total_mass_frames5_6": value(feedback, tokens, 0, "valid", "target_total_quadrant_mass", "frames5_6_mean"),
                    "valid_target_peak_share_frames5_6": value(feedback, tokens, 0, "valid", "target_peak_patch_quadrant_share", "frames5_6_mean"),
                    "invalid_target_minus_cue_total_frame5": value(feedback, tokens, 0, "invalid", "target_minus_cue_total_mass", "frame5"),
                    "invalid_target_minus_cue_total_frame6": value(feedback, tokens, 0, "invalid", "target_minus_cue_total_mass", "frame6"),
                    "invalid_target_minus_cue_total_frames5_6": value(feedback, tokens, 0, "invalid", "target_minus_cue_total_mass", "frames5_6_mean"),
                    "invalid_target_minus_cue_peak_share_frames5_6": value(feedback, tokens, 0, "invalid", "target_minus_cue_peak_share", "frames5_6_mean"),
                }
            )
    selected_sources: list[dict[str, Any]] = []
    for tokens in (4, 16, 100):
        for source_name in ("visual", "memory"):
            selected_sources.append(
                {
                    "n_tokens": tokens,
                    "seed": 0,
                    "condition": "valid",
                    "window": "frame5",
                    "source": source_name,
                    "source_total_share": float(
                        lookup_source_summary(
                            source_summary_rows,
                            n_tokens=tokens,
                            seed=0,
                            condition="valid",
                            window="frame5",
                            source=source_name,
                            metric="source_total_share",
                        )["mean"]
                    ),
                    "target_raw_total_quadrant_mass": float(
                        lookup_source_summary(
                            source_summary_rows,
                            n_tokens=tokens,
                            seed=0,
                            condition="valid",
                            window="frame5",
                            source=source_name,
                            metric="target_raw_total_quadrant_mass",
                        )["mean"]
                    ),
                    "target_raw_peak_patch": float(
                        lookup_source_summary(
                            source_summary_rows,
                            n_tokens=tokens,
                            seed=0,
                            condition="valid",
                            window="frame5",
                            source=source_name,
                            metric="target_raw_peak_patch",
                        )["mean"]
                    ),
                }
            )
    return {
        "schema_version": 2,
        "status": "complete",
        "analysis_class": "derived reanalysis of verified held-out caches plus source-resolved held-out refresh from the same hash-matched terminal checkpoints",
        "scientific_evidence": "correlational attention geometry only; causal intervention evidence remains separate",
        "common_grid": "fixed physical 2x2 VDA4 quadrants for every native grid",
        "patch_score": "attention-map key-column mean over query patches; cross-attention visual and recurrent-memory blocks are split before reduction",
        "paired_location_diagnostic": "visual+memory columns may be added only as an explicitly labeled secondary total-routing diagnostic",
        "primary_event_window": "frame5 (change onset)",
        "frame6_status": "open-loop post-change continuation; reported separately",
        "event_windows": {name: list(frames) for name, frames in WINDOWS.items()},
        "trials_per_condition": TRIALS_EXPECTED,
        "interval": {
            "method": "percentile bootstrap",
            "draws": BOOTSTRAP_DRAWS,
            "unit": "held-out trials",
            "not_training_population_uncertainty": True,
        },
        "metric_definitions": metric_definitions(),
        "selected_seed0_results": selected,
        "selected_seed0_source_results": selected_sources,
        "sources": [
            {
                "label": source.label,
                "feedback": source.feedback,
                "grid": f"{source.grid_rows}x{source.grid_cols}",
                "n_tokens": source.n_tokens,
                "seed": source.seed,
                "event_attention_sha256": source.event_sha256,
                "source_manifest_sha256": source.manifest_sha256,
            }
            for source in sources
        ],
        "interpretation_limits": [
            "Total quadrant mass and peak-patch measures are distinct estimands and cannot be called a single attention score.",
            "Frame 5, frame 6, and their mean are reported separately because event reorientation can change sign across frames.",
            "The strongest-query max_i A_ij diagnostic is unavailable trialwise because the cache retained only the trial-mean raw matrix; it is not conflated with peak max_j mean_i A_ij.",
            "A common 2x2 projection measures allocation to fixed physical quadrants, not within-quadrant resolution or stream count.",
            "Cross-attention primary maps and maxima preserve visual and recurrent-memory sources; a source-resolved held-out refresh supplies per-trial intervals and reconstructs the previously admitted paired-location cache.",
            "Visual+memory paired-location totals remain a secondary spatial diagnostic and cannot be interpreted as either source's map or maximum.",
            "Attention geometry is correlational and is not itself behavioral or causal mechanism evidence.",
            "Seed 0 spans the six-cell factorial; seed 1 covers only cross-attention 2x2 and 10x10 endpoints.",
            "Token count still co-varies with parameter count and native discretization.",
        ],
    }


def build_manifest(
    output: Path,
    sources: list[Source],
    source_resolved_root: Path,
    copied_to_manuscript: list[Path],
) -> dict[str, Any]:
    hashes = {
        path.relative_to(output).as_posix(): sha256_file(path)
        for path in sorted(output.rglob("*"))
        if path.is_file() and path.name != "MANIFEST.json"
    }
    return {
        "schema_version": 1,
        "status": "complete",
        "producer": str(Path(__file__).resolve()),
        "producer_sha256": sha256_file(Path(__file__).resolve()),
        "source_artifacts": {
            source.event_path.relative_to(ROOT).as_posix(): source.event_sha256
            for source in sources
        },
        "source_resolved_artifacts": {
            path.relative_to(ROOT).as_posix(): sha256_file(path)
            for path in sorted(source_resolved_root.rglob("*"))
            if path.is_file() and path.suffix.lower() in {".npz", ".json"}
        },
        "artifact_hashes": hashes,
        "manuscript_copies": {
            str(path.resolve()): sha256_file(path)
            for path in copied_to_manuscript
        },
    }


def run(args: argparse.Namespace) -> None:
    source_root = Path(args.source_root).resolve()
    source_resolved_root = Path(args.source_resolved_root).resolve()
    output = Path(args.output_dir).resolve()
    manuscript_figures = Path(args.manuscript_figures).resolve() if args.manuscript_figures else None
    require(source_root.is_dir(), f"source root not found: {source_root}")
    require(output != source_root, "derived output must not replace the verified source cache")
    require(ROOT in output.parents, f"derived output must remain under repository root: {output}")
    require(output.name.startswith("spatial_scaling_attention_measures_"), f"refusing unexpected output directory: {output}")
    if output.exists():
        require(bool(args.overwrite), f"output exists; pass --overwrite: {output}")
        shutil.rmtree(output)
    output.mkdir(parents=True)
    (output / "figures").mkdir()
    (output / "tables").mkdir()

    sources = discover_sources(source_root)
    payloads = {source.label: load_source(source) for source in sources}
    source_payloads = load_source_resolved(source_resolved_root, sources)
    trial_rows: list[dict[str, Any]] = []
    for source in sources:
        source_rows, _ = trial_rows_for_source(source, payloads[source.label])
        trial_rows.extend(source_rows)
    summary_rows = summarize_trials(trial_rows)
    contrast_rows = summarize_paired_grid_contrasts(trial_rows)
    source_rows: list[dict[str, Any]] = []
    for source in sources:
        source_rows.extend(source_mean_rows_for_source(source, payloads[source.label]))
    source_trial_rows: list[dict[str, Any]] = []
    for source in sources:
        if source.feedback == "crossattn1":
            source_trial_rows.extend(source_trial_rows_for_source(source, source_payloads[source.label]))
    source_summary_rows = summarize_source_trials(source_trial_rows)
    write_csv(output / "tables" / "attention_metrics_trials.csv", trial_rows)
    write_csv(output / "tables" / "attention_metrics_summary.csv", summary_rows)
    write_csv(output / "tables" / "attention_paired_grid_contrasts.csv", contrast_rows)
    write_csv(output / "tables" / "cross_attention_source_decomposition.csv", source_rows)
    write_csv(output / "tables" / "cross_attention_source_metrics_trials.csv", source_trial_rows)
    write_csv(output / "tables" / "cross_attention_source_metrics_summary.csv", source_summary_rows)
    write_csv(output / "tables" / "metric_definitions.csv", metric_definitions())

    plt = configure_matplotlib()
    figure_root = output / "figures"
    plot_seed0_measure_comparison(plt, summary_rows, figure_root)
    plot_framewise(plt, summary_rows, figure_root)
    plot_projected_maps(plt, sources, payloads, figure_root)
    plot_native_maps(plt, sources, payloads, figure_root)
    plot_endpoint_replication(plt, summary_rows, figure_root)
    plot_cross_attention_sources(plt, sources, payloads, figure_root)
    plot_cross_attention_source_metrics(plt, source_summary_rows, figure_root)
    plot_cross_attention_source_common_grid(plt, sources, source_payloads, figure_root)
    plot_cross_attention_source_timecourses(plt, sources, source_payloads, figure_root)

    write_json(output / "SUMMARY.json", build_summary_payload(sources, summary_rows, source_summary_rows))

    copied: list[Path] = []
    if manuscript_figures is not None:
        manuscript_figures.mkdir(parents=True, exist_ok=True)
        for figure in sorted(figure_root.glob("*.pdf")):
            target = manuscript_figures / figure.name
            shutil.copy2(figure, target)
            require(sha256_file(figure) == sha256_file(target), f"manuscript copy mismatch: {target}")
            copied.append(target)
        for figure in sorted(figure_root.glob("*.png")):
            target = manuscript_figures / figure.name
            shutil.copy2(figure, target)
            require(sha256_file(figure) == sha256_file(target), f"manuscript copy mismatch: {target}")
            copied.append(target)

    write_json(output / "MANIFEST.json", build_manifest(output, sources, source_resolved_root, copied))
    print(json.dumps({"status": "complete", "output": str(output), "sources": len(sources), "trial_rows": len(trial_rows), "summary_rows": len(summary_rows), "figures": len(list(figure_root.glob("*.pdf")))}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", default=str(DEFAULT_SOURCE_ROOT))
    parser.add_argument("--source-resolved-root", default=str(DEFAULT_SOURCE_RESOLVED_ROOT))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--manuscript-figures", default=str(DEFAULT_MANUSCRIPT_FIGURES))
    parser.add_argument("--overwrite", action="store_true")
    return parser


if __name__ == "__main__":
    run(build_parser().parse_args())
