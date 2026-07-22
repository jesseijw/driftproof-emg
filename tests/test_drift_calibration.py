from __future__ import annotations

import numpy as np
import pytest

from driftproof.drift.calibration import best_threshold, threshold_report, threshold_sweep


def test_threshold_sweep_scores_failure_detection() -> None:
    scores = np.array([0.1, 0.2, 2.0, 3.0])
    failures = np.array([False, False, True, True])

    rows = threshold_sweep(scores, failures, n_thresholds=4)
    best = best_threshold(rows)

    assert len(rows) == 4
    assert best is not None
    assert best.f1 > 0
    assert best.true_positive > 0


def test_threshold_report_is_json_ready() -> None:
    report = threshold_report(
        np.array([0.1, 0.2, 2.0, 3.0]),
        np.array([False, False, True, True]),
        n_thresholds=3,
    )

    assert report["target"] == "prediction_failure"
    assert report["n_thresholds"] == 3
    assert report["best"] is not None
    assert len(report["sweep"]) == 3


def test_threshold_sweep_rejects_misaligned_inputs() -> None:
    with pytest.raises(ValueError, match="same length"):
        threshold_sweep(np.array([1.0, 2.0]), np.array([True]))
