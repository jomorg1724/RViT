"""Computation primitives for provenance-closed matched-width VDA shards."""
from __future__ import annotations

import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from vda_sweep import matched_width as M
from vda_sweep import vda_fig_decode as decoder

CV_FOLDS = 4


def press_histogram(press: np.ndarray) -> np.ndarray:
    values = np.asarray(press)
    if values.ndim != 1 or not np.issubdtype(values.dtype, np.number):
        raise ValueError("press times must be a one-dimensional numeric array")
    if not np.isfinite(values).all() or np.any(values != np.floor(values)):
        raise ValueError("press times must be finite integers")
    values = values.astype(np.int64)
    if np.any((values < -1) | (values > 6)):
        raise ValueError("press times must lie in {-1, 0, ..., 6}")
    return np.bincount(values + 1, minlength=8).astype(np.int64)


def stratified_fold_ids(labels: np.ndarray, mask: np.ndarray, *, seed: int) -> np.ndarray:
    from sklearn.model_selection import StratifiedKFold

    labels = np.asarray(labels)
    mask = np.asarray(mask, dtype=bool)
    if labels.shape != (M.DECODER_N,) and labels.shape != mask.shape:
        raise ValueError("labels and mask must have the same one-dimensional shape")
    if labels.ndim != 1 or mask.shape != labels.shape:
        raise ValueError("labels and mask must have the same one-dimensional shape")
    fold_ids = np.full(len(labels), -1, dtype=np.int64)
    selected = np.flatnonzero(mask)
    if not len(selected):
        return fold_ids
    unique, counts = np.unique(labels[selected], return_counts=True)
    if len(unique) < 2 or int(counts.min()) < CV_FOLDS:
        raise ValueError("decoder contrast lacks four-fold class support")
    splitter = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=int(seed))
    for fold, (_, test_local) in enumerate(splitter.split(selected, labels[selected])):
        fold_ids[selected[test_local]] = fold
    return fold_ids


def decoder_design(task: str) -> dict[str, object]:
    conditions, legacy_labels, config = decoder.sample_conditions(
        task, n=M.DECODER_N, seed=M.DECODER_SEED
    )
    invalid_defined = bool(config["location_decode_defined"])
    change = np.asarray(legacy_labels["change"], dtype=np.int64)
    change_index = np.asarray(conditions["change_index"], dtype=np.int64)
    labels = {
        "colour": np.asarray(legacy_labels["colour"], dtype=np.int64),
        "validity": np.asarray(legacy_labels["validity"], dtype=np.int64),
        "change": change,
        "change_location": change_index,
        "cued_change": np.asarray(legacy_labels["cued_change"], dtype=np.int64),
    }
    fold_ids: dict[str, np.ndarray] = {}
    for offset, name in enumerate(M.DECODED_VARIABLES):
        conditional = name in ("change_location", "cued_change")
        mask = change.astype(bool) if conditional and invalid_defined else np.ones(M.DECODER_N, dtype=bool)
        if conditional and not invalid_defined:
            mask[:] = False
        fold_ids[name] = stratified_fold_ids(
            labels[name], mask, seed=M.DECODER_SEED + 1009 * (offset + 1)
        )
    return {
        "conditions": conditions,
        "labels": labels,
        "fold_ids": fold_ids,
        "config": config,
    }


def _classifier(*, matched_dimensions: int | None, seed: int) -> Pipeline:
    steps: list[tuple[str, object]] = [("scale", StandardScaler())]
    if matched_dimensions is not None:
        steps.append(
            (
                "pca",
                PCA(
                    n_components=int(matched_dimensions),
                    svd_solver="randomized",
                    random_state=int(seed),
                ),
            )
        )
    # The 16-token VDA16 native space has 2,048 recurrent features.  Six
    # hundred L-BFGS steps, adequate for the smaller archived tasks, can stop
    # before convergence in that space.  Raising only the numerical ceiling
    # leaves the objective, scaling, regularization, folds, and estimand
    # unchanged.
    steps.append(("logit", LogisticRegression(max_iter=4000, C=0.5)))
    return Pipeline(steps)


def decode_timecourses(
    cells: np.ndarray,
    labels: np.ndarray,
    fold_ids: np.ndarray,
    *,
    matched_dimensions: int | None,
) -> np.ndarray:
    cells = np.asarray(cells, dtype=float)
    labels = np.asarray(labels)
    fold_ids = np.asarray(fold_ids, dtype=np.int64)
    if cells.ndim < 3 or cells.shape[0] != len(labels) or fold_ids.shape != labels.shape:
        raise ValueError("decoder cells, labels, and fold IDs are inconsistent")
    selected = fold_ids >= 0
    if not np.any(selected):
        return np.full(cells.shape[1], np.nan)
    scores = []
    for timestep in range(cells.shape[1]):
        features = cells[:, timestep].reshape(len(cells), -1)
        selected_features = features[selected]
        # The recurrent state is deterministically zero before the first input.
        # PCA is undefined when total variance is exactly zero, while balanced
        # accuracy for any feature-independent prediction is exactly chance.
        # Declare that structural result directly instead of emitting a
        # zero-variance PCA warning or fitting an arbitrary intercept model.
        if np.all(np.ptp(selected_features, axis=0) == 0.0):
            scores.append(1.0 / len(np.unique(labels[selected])))
            continue
        fold_scores = []
        for fold in range(CV_FOLDS):
            train = selected & (fold_ids != fold)
            test = selected & (fold_ids == fold)
            if matched_dimensions is not None:
                maximum = min(int(train.sum()) - 1, features.shape[1])
                if int(matched_dimensions) > maximum:
                    raise ValueError(
                        f"matched decoder requires {matched_dimensions} dimensions but maximum is {maximum}"
                    )
            classifier = _classifier(
                matched_dimensions=matched_dimensions,
                seed=M.DECODER_SEED + timestep * 101 + fold,
            )
            classifier.fit(features[train], labels[train])
            estimator = classifier.named_steps["logit"]
            if np.any(np.asarray(estimator.n_iter_) >= int(estimator.max_iter)):
                raise RuntimeError(
                    f"decoder optimizer did not converge for timestep={timestep}, "
                    f"fold={fold}, matched_dimensions={matched_dimensions}"
                )
            prediction = classifier.predict(features[test])
            fold_scores.append(balanced_accuracy_score(labels[test], prediction))
        scores.append(float(np.mean(fold_scores)))
    return np.asarray(scores, dtype=float)
