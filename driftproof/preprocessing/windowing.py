from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

import numpy as np

from driftproof.types import EmgSample, Window


def make_windows(
    samples: Sequence[EmgSample],
    *,
    window_ms: int = 200,
    step_ms: int = 100,
    sample_rate_hz: int = 1_000,
) -> list[Window]:
    """Turn samples into overlapping windows with majority labels."""
    if window_ms <= 0 or step_ms <= 0 or sample_rate_hz <= 0:
        raise ValueError("window_ms, step_ms, and sample_rate_hz must be positive")
    if not samples:
        return []

    win = int(round(window_ms * sample_rate_hz / 1_000))
    step = int(round(step_ms * sample_rate_hz / 1_000))
    windows: list[Window] = []

    for start in range(0, max(0, len(samples) - win + 1), step):
        chunk = samples[start : start + win]
        labels = Counter(s.label for s in chunk)
        conditions = Counter(s.condition for s in chunk)
        signal = np.stack([s.channels for s in chunk])
        windows.append(
            Window(
                session_id=chunk[0].session_id,
                t_start=chunk[0].t,
                t_end=chunk[-1].t,
                signal=signal,
                label=labels.most_common(1)[0][0],
                condition=conditions.most_common(1)[0][0],
            )
        )
    return windows


def robust_normalize(signal: np.ndarray, *, eps: float = 1e-6) -> np.ndarray:
    """Median/IQR normalize a window or batch of EMG samples."""
    median = np.median(signal, axis=0)
    q75 = np.percentile(signal, 75, axis=0)
    q25 = np.percentile(signal, 25, axis=0)
    iqr = np.maximum(q75 - q25, eps)
    return (signal - median) / iqr


def signal_quality(signal: np.ndarray) -> dict[str, float]:
    """Basic signal-quality diagnostics for saturation and flatlines."""
    return {
        "max_abs": float(np.max(np.abs(signal))),
        "mean_abs": float(np.mean(np.abs(signal))),
        "flatline_fraction": float(np.mean(np.std(signal, axis=0) < 1e-5)),
    }
