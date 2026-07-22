from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class DriftThresholdResult:
    threshold: float
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int
    precision: float
    recall: float
    f1: float


def threshold_sweep(
    drift_scores: np.ndarray,
    failures: np.ndarray,
    *,
    n_thresholds: int = 11,
) -> list[DriftThresholdResult]:
    """Sweep drift thresholds against a boolean failure signal."""
    scores = np.asarray(drift_scores, dtype=float)
    failure_mask = np.asarray(failures, dtype=bool)
    if scores.ndim != 1 or failure_mask.ndim != 1:
        raise ValueError("drift_scores and failures must be one-dimensional")
    if len(scores) != len(failure_mask):
        raise ValueError("drift_scores and failures must have the same length")
    if len(scores) == 0:
        return []
    if not np.all(np.isfinite(scores)):
        raise ValueError("drift_scores must be finite")
    if n_thresholds < 2:
        raise ValueError("n_thresholds must be at least 2")

    thresholds = np.linspace(float(scores.min()), float(scores.max()), n_thresholds)
    return [_score_threshold(scores, failure_mask, threshold) for threshold in thresholds]


def best_threshold(rows: list[DriftThresholdResult]) -> DriftThresholdResult | None:
    if not rows:
        return None
    return max(rows, key=lambda row: (row.f1, row.recall, -row.threshold))


def threshold_report(
    drift_scores: np.ndarray,
    failures: np.ndarray,
    *,
    n_thresholds: int = 11,
) -> dict[str, Any]:
    rows = threshold_sweep(drift_scores, failures, n_thresholds=n_thresholds)
    best = best_threshold(rows)
    return {
        "target": "prediction_failure",
        "n_thresholds": len(rows),
        "best": asdict(best) if best is not None else None,
        "sweep": [asdict(row) for row in rows],
    }


def _score_threshold(
    scores: np.ndarray,
    failures: np.ndarray,
    threshold: float,
) -> DriftThresholdResult:
    predicts_failure = scores >= threshold
    true_positive = int(np.sum(predicts_failure & failures))
    false_positive = int(np.sum(predicts_failure & ~failures))
    true_negative = int(np.sum(~predicts_failure & ~failures))
    false_negative = int(np.sum(~predicts_failure & failures))
    precision = _divide(true_positive, true_positive + false_positive)
    recall = _divide(true_positive, true_positive + false_negative)
    f1 = _divide(2 * precision * recall, precision + recall)
    return DriftThresholdResult(
        threshold=float(threshold),
        true_positive=true_positive,
        false_positive=false_positive,
        true_negative=true_negative,
        false_negative=false_negative,
        precision=precision,
        recall=recall,
        f1=f1,
    )


def _divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator / denominator)
