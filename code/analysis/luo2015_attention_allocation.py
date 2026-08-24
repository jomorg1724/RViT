"""Source-resolved spatial-attention analysis for the Luo 2015 task analogue."""
from __future__ import annotations

from typing import Any

import numpy as np


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def quadrant_indices(grid_rows: int, grid_cols: int) -> tuple[tuple[int, ...], ...]:
    """Partition an even row-major patch grid into four physical quadrants."""
    require(grid_rows > 0 and grid_cols > 0, "grid dimensions must be positive")
    require(grid_rows % 2 == 0 and grid_cols % 2 == 0, "grid dimensions must be even")
    half_rows, half_cols = grid_rows // 2, grid_cols // 2
    regions = tuple(
        tuple(
            row * grid_cols + col
            for row in range(qr * half_rows, (qr + 1) * half_rows)
            for col in range(qc * half_cols, (qc + 1) * half_cols)
        )
        for qr in range(2)
        for qc in range(2)
    )
    flat = sorted(index for region in regions for index in region)
    require(flat == list(range(grid_rows * grid_cols)), "quadrants do not partition tokens")
    return regions


def query_averaged_source_mass(raw_attention: Any, n_tokens: int) -> np.ndarray:
    """Average queries and split visual/memory keys without source renormalization."""
    raw = np.asarray(raw_attention, dtype=np.float64)
    require(raw.ndim >= 2, f"attention lacks query/key axes: {raw.shape}")
    require(raw.shape[-2] == n_tokens, f"expected {n_tokens} queries, got {raw.shape[-2]}")
    require(raw.shape[-1] == 2 * n_tokens, f"expected {2*n_tokens} keys, got {raw.shape[-1]}")
    require(bool(np.all(raw >= 0.0)), "attention contains negative mass")
    require(bool(np.allclose(raw.sum(axis=-1), 1.0, atol=1e-6)), "attention rows are not normalized")
    separated = np.stack((raw[..., :n_tokens], raw[..., n_tokens:]), axis=-2)
    source = separated.mean(axis=-3)
    require(bool(np.allclose(source.sum(axis=(-2, -1)), 1.0, atol=1e-6)), "source mass is not normalized")
    return source


def query_quadrant_routing(raw_attention: Any, grid_rows: int, grid_cols: int) -> np.ndarray:
    """Reduce Q×2K attention to query-quadrant × source × key-quadrant routing."""
    raw = np.asarray(raw_attention, dtype=np.float64)
    n_tokens = grid_rows * grid_cols
    require(raw.ndim >= 2, f"attention lacks query/key axes: {raw.shape}")
    require(raw.shape[-2:] == (n_tokens, 2 * n_tokens), f"expected (...,{n_tokens},{2*n_tokens}), got {raw.shape}")
    require(bool(np.allclose(raw.sum(axis=-1), 1.0, atol=1e-6)), "attention rows are not normalized")
    regions = quadrant_indices(grid_rows, grid_cols)
    rows = []
    for query_region in regions:
        query_mean = raw[..., list(query_region), :].mean(axis=-2)
        source_blocks = (query_mean[..., :n_tokens], query_mean[..., n_tokens:])
        rows.append(
            np.stack(
                [
                    np.stack([block[..., list(key_region)].sum(axis=-1) for key_region in regions], axis=-1)
                    for block in source_blocks
                ],
                axis=-2,
            )
        )
    routing = np.stack(rows, axis=-3)
    require(bool(np.allclose(routing.sum(axis=(-2, -1)), 1.0, atol=1e-6)), "quadrant routing rows are not normalized")
    return routing


def phase_contrasts(
    source_token_mass: Any,
    quadrant_routing: Any,
    *,
    test_locations: Any,
    change_status: Any,
    grid_rows: int,
    grid_cols: int,
) -> dict[str, np.ndarray]:
    """Return trialwise contrasts addressing sample, first-test, and second-test allocation."""
    source = np.asarray(source_token_mass, dtype=np.float64)
    routing = np.asarray(quadrant_routing, dtype=np.float64)
    locations = np.asarray(test_locations, dtype=np.int64).reshape(-1)
    status = np.asarray(change_status, dtype=np.int64).reshape(-1)
    n_trials, timesteps = source.shape[:2]
    n_tokens = grid_rows * grid_cols
    require(source.shape == (n_trials, timesteps, 2, n_tokens), f"unexpected source mass shape {source.shape}")
    require(routing.shape == (n_trials, timesteps, 4, 2, 4), f"unexpected routing shape {routing.shape}")
    require(timesteps == 7, "Luo phase contrasts require seven timesteps")
    require(locations.shape == (n_trials,), "test location count mismatch")
    require(status.shape == (n_trials,), "change status count mismatch")
    require(bool(np.isin(locations, (0, 3)).all()), "test locations must be 0 or 3")
    require(bool(np.isin(status, (0, 1)).all()), "change status must be 0 or 1")

    regions = quadrant_indices(grid_rows, grid_cols)
    source_quadrant = np.stack(
        [source[..., list(region)].sum(axis=-1) for region in regions], axis=-1
    )
    combined = source_quadrant.sum(axis=-2)
    target = locations
    other = 3 - locations
    trial = np.arange(n_trials)

    stimulus_sample = combined[:, 0:2, :][:, :, [0, 3]].mean(axis=(1, 2))
    blank_sample = combined[:, 0:2, :][:, :, [1, 2]].mean(axis=(1, 2))
    first_target = combined[trial[:, None], np.asarray([3, 4])[None, :], target[:, None]].mean(axis=1)
    first_other = combined[trial[:, None], np.asarray([3, 4])[None, :], other[:, None]].mean(axis=1)
    first_memory_same = routing[trial[:, None], np.asarray([3, 4])[None, :], target[:, None], 1, target[:, None]].mean(axis=1)
    first_memory_other = routing[trial[:, None], np.asarray([3, 4])[None, :], target[:, None], 1, other[:, None]].mean(axis=1)

    sample_query_rows = routing[:, 0:2, :, :, :][:, :, [0, 3], :, :]
    sample_query_stimulus = sample_query_rows[..., [0, 3]].sum(axis=(-2, -1)).mean(axis=(1, 2))
    sample_query_blank = sample_query_rows[..., [1, 2]].sum(axis=(-2, -1)).mean(axis=(1, 2))

    query_phase: dict[str, np.ndarray] = {}
    for frame in (3, 4):
        visual = routing[trial, frame, target, 0, target] - routing[trial, frame, target, 0, other]
        memory = routing[trial, frame, target, 1, target] - routing[trial, frame, target, 1, other]
        query_phase[f"first_test_t{frame}_query_same_minus_other_visual"] = visual
        query_phase[f"first_test_t{frame}_query_same_minus_other_memory"] = memory
        query_phase[f"first_test_t{frame}_query_same_minus_other_combined"] = visual + memory

    second_mask = status == 0
    second_target = combined[trial, 6, target]
    second_other = combined[trial, 6, other]
    gap_target = combined[trial, 5, target]
    second_memory_same = routing[trial, 6, target, 1, target]
    second_memory_other = routing[trial, 6, target, 1, other]
    second_visual_same = routing[trial, 6, target, 0, target]
    second_visual_other = routing[trial, 6, target, 0, other]

    def no_change_only(values: np.ndarray) -> np.ndarray:
        return np.where(second_mask, values, np.nan)

    second_visual_difference = second_visual_same - second_visual_other
    second_memory_difference = second_memory_same - second_memory_other
    return {
        "sample_stimulus_minus_blank_combined": stimulus_sample - blank_sample,
        "sample_query_stimulus_minus_blank_combined": sample_query_stimulus - sample_query_blank,
        "sample_loc0_minus_loc3_combined": combined[:, 0:2, 0].mean(axis=1) - combined[:, 0:2, 3].mean(axis=1),
        "first_test_target_minus_other_combined": first_target - first_other,
        "first_test_query_same_minus_other_memory": first_memory_same - first_memory_other,
        **query_phase,
        "second_test_target_minus_other_combined": no_change_only(second_target - second_other),
        "second_test_return_from_gap_combined": no_change_only(second_target - gap_target),
        "second_test_query_same_minus_other_visual": no_change_only(second_visual_difference),
        "second_test_query_same_minus_other_memory": no_change_only(second_memory_difference),
        "second_test_query_same_minus_other_combined": no_change_only(second_visual_difference + second_memory_difference),
    }


def summarize_contrasts(
    contrasts: dict[str, Any],
    *,
    bootstrap_draws: int = 5000,
    seed: int = 20260802,
) -> dict[str, dict[str, float | int | str]]:
    """Summarize finite trialwise contrasts with deterministic percentile bootstrap CIs."""
    require(bootstrap_draws > 0, "bootstrap_draws must be positive")
    rng = np.random.default_rng(int(seed))
    result: dict[str, dict[str, float | int | str]] = {}
    for name in sorted(contrasts):
        values = np.asarray(contrasts[name], dtype=np.float64).reshape(-1)
        values = values[np.isfinite(values)]
        require(values.size > 1, f"{name} requires at least two finite trials")
        indices = rng.integers(0, values.size, size=(bootstrap_draws, values.size))
        means = values[indices].mean(axis=1)
        low, high = np.quantile(means, (0.025, 0.975))
        direction = "positive" if low > 0.0 else "negative" if high < 0.0 else "uncertain"
        result[name] = {
            "n": int(values.size),
            "mean": float(values.mean()),
            "ci95_low": float(low),
            "ci95_high": float(high),
            "direction": direction,
        }
    return result
