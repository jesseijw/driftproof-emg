from __future__ import annotations

import numpy as np

from driftproof.acquisition.replay import read_jsonl, write_jsonl
from driftproof.types import EmgSample, IntentLabel

__all__ = ["generate_synthetic_session", "read_jsonl", "write_jsonl"]

LABELS: tuple[IntentLabel, ...] = ("rest", "open", "close")

BASE_PATTERNS = {
    "rest": np.array([0.08, 0.07, 0.06, 0.07]),
    "open": np.array([0.75, 0.28, 0.18, 0.35]),
    "close": np.array([0.22, 0.72, 0.45, 0.20]),
}


def generate_synthetic_session(
    *,
    session_id: str = "demo",
    seconds: float = 24.0,
    sample_rate_hz: int = 1_000,
    drift_after_s: float = 12.0,
    seed: int = 42,
) -> list[EmgSample]:
    """Generate EMG-like 4-channel samples with a controlled post-drift condition."""
    rng = np.random.default_rng(seed)
    n = int(seconds * sample_rate_hz)
    samples: list[EmgSample] = []

    # Rotate/mix channels after drift to mimic armband shift.
    drift_matrix = np.array(
        [
            [0.35, 0.55, 0.05, 0.05],
            [0.60, 0.20, 0.15, 0.05],
            [0.10, 0.20, 0.55, 0.15],
            [0.05, 0.10, 0.30, 0.55],
        ]
    )

    for i in range(n):
        t = i / sample_rate_hz
        label = LABELS[int(t // 2.0) % len(LABELS)]
        condition = "drifted" if t >= drift_after_s else "baseline"
        base = BASE_PATTERNS[label]
        envelope = 1.0 + 0.08 * np.sin(2 * np.pi * 0.7 * t)
        noise = rng.normal(0.0, 0.035, size=4)
        signal = base * envelope + noise
        if condition == "drifted":
            signal = drift_matrix @ signal
            signal += rng.normal(0.0, 0.02, size=4)
        samples.append(
            EmgSample(
                session_id=session_id,
                t=t,
                channels=signal.astype(float),
                label=label,
                condition=condition,
            )
        )
    return samples
