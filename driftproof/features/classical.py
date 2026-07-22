from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from driftproof.types import FeatureWindow, Window


def extract_classical_features(window: Window) -> FeatureWindow:
    """Extract common classical EMG features from one window."""
    x = np.asarray(window.signal, dtype=float)
    diff = np.diff(x, axis=0)

    mav = np.mean(np.abs(x), axis=0)
    rms = np.sqrt(np.mean(x**2, axis=0))
    waveform_length = np.sum(np.abs(diff), axis=0)
    zero_crossings = np.sum(np.diff(np.signbit(x), axis=0), axis=0)
    slope_sign_changes = np.sum(np.diff(np.sign(diff), axis=0) != 0, axis=0)

    features = np.concatenate(
        [
            mav,
            rms,
            waveform_length,
            zero_crossings.astype(float),
            slope_sign_changes.astype(float),
        ]
    )
    return FeatureWindow(
        session_id=window.session_id,
        t_start=window.t_start,
        t_end=window.t_end,
        features=features,
        label=window.label,
        condition=window.condition,
    )


def extract_many(windows: Iterable[Window]) -> list[FeatureWindow]:
    return [extract_classical_features(window) for window in windows]


def feature_matrix(rows: Iterable[FeatureWindow]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows = list(rows)
    if not rows:
        return np.empty((0, 0)), np.empty((0,), dtype=object), np.empty((0,), dtype=object)
    x = np.stack([row.features for row in rows])
    y = np.asarray([row.label for row in rows], dtype=object)
    condition = np.asarray([row.condition for row in rows], dtype=object)
    return x, y, condition
