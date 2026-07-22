from __future__ import annotations

import numpy as np

from driftproof.acquisition.simulated import generate_synthetic_session
from driftproof.drift.mahalanobis import fit_reference, score
from driftproof.features.classical import extract_many, feature_matrix
from driftproof.preprocessing.windowing import make_windows, signal_quality


def test_synthetic_session_has_baseline_and_drift() -> None:
    samples = generate_synthetic_session(seconds=4, sample_rate_hz=100, drift_after_s=2)
    conditions = {sample.condition for sample in samples}
    assert conditions == {"baseline", "drifted"}
    assert all(sample.channels.shape == (4,) for sample in samples)


def test_windowing_and_feature_shape() -> None:
    samples = generate_synthetic_session(seconds=4, sample_rate_hz=100, drift_after_s=2)
    windows = make_windows(samples, window_ms=200, step_ms=100, sample_rate_hz=100)
    rows = extract_many(windows)
    x, y, condition = feature_matrix(rows)
    assert len(windows) == len(rows) == len(y) == len(condition)
    assert x.shape[1] == 20


def test_drift_score_increases_on_shifted_distribution() -> None:
    rng = np.random.default_rng(7)
    baseline = rng.normal(0, 1, size=(100, 4))
    shifted = rng.normal(2, 1, size=(100, 4))
    ref = fit_reference(baseline)
    assert score(ref, shifted).mean() > score(ref, baseline).mean()


def test_signal_quality_reports_flatline_fraction() -> None:
    signal = np.ones((100, 4))
    quality = signal_quality(signal)
    assert quality["flatline_fraction"] == 1.0
