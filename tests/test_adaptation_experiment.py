from __future__ import annotations

import numpy as np

from driftproof.adaptation.experiment import (
    FeatureSpaceAdapter,
    adaptation_report,
    run_feature_normalization_adaptation,
)
from driftproof.models.baseline import train_baseline


def test_feature_space_adapter_maps_runtime_mean_toward_calibration() -> None:
    calibration = np.array([[0.0, 0.0], [2.0, 2.0]])
    adapter = FeatureSpaceAdapter.from_calibration(calibration)

    transformed = adapter.transform(np.array([1.0, 1.0]))

    assert np.allclose(transformed, np.array([1.0, 1.0]))


def test_feature_space_adapter_updates_runtime_state() -> None:
    calibration = np.array([[0.0, 0.0], [2.0, 2.0]])
    adapter = FeatureSpaceAdapter.from_calibration(calibration, momentum=0.5)

    adapter.update(np.array([3.0, 3.0]))

    assert adapter.runtime_mean is not None
    assert np.all(adapter.runtime_mean > adapter.calibration_mean)


def test_run_feature_normalization_adaptation_returns_predictions_and_events() -> None:
    x_calibration = np.array(
        [
            [0.0, 0.0],
            [0.1, 0.0],
            [2.0, 2.0],
            [2.1, 2.0],
        ]
    )
    y_calibration = np.array(["rest", "rest", "open", "open"], dtype=object)
    model = train_baseline(x_calibration, y_calibration)
    x_runtime = np.array([[0.0, 0.0], [2.0, 2.0]])

    result = run_feature_normalization_adaptation(
        model,
        x_calibration,
        x_runtime,
        confidence_threshold=0.0,
    )
    report = adaptation_report(result, confidence_threshold=0.0, momentum=0.02)

    assert result.predictions.shape == (2,)
    assert result.adapted_features.shape == x_runtime.shape
    assert report["update_count"] == 2
