from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

IntentLabel = Literal["rest", "open", "close"]


@dataclass(frozen=True)
class EmgSample:
    session_id: str
    t: float
    channels: np.ndarray
    label: IntentLabel
    condition: str = "baseline"
    dropped_samples: int = 0
    sensor_status: str = "ok"


@dataclass(frozen=True)
class Window:
    session_id: str
    t_start: float
    t_end: float
    signal: np.ndarray
    label: IntentLabel
    condition: str


@dataclass(frozen=True)
class FeatureWindow:
    session_id: str
    t_start: float
    t_end: float
    features: np.ndarray
    label: IntentLabel
    condition: str


@dataclass(frozen=True)
class Scorecard:
    accuracy: float
    macro_f1: float
    drift_score_mean: float | None = None
    n_windows: int = 0
