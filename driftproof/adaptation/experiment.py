from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class AdaptationEvent:
    index: int
    confidence: float


@dataclass(frozen=True)
class AdaptationResult:
    predictions: np.ndarray
    adapted_features: np.ndarray
    events: list[AdaptationEvent]


@dataclass
class FeatureSpaceAdapter:
    """Map runtime features back toward the calibration feature distribution."""

    calibration_mean: np.ndarray
    calibration_scale: np.ndarray
    momentum: float = 0.02
    runtime_mean: np.ndarray | None = None
    runtime_scale: np.ndarray | None = None

    @classmethod
    def from_calibration(cls, x: np.ndarray, *, momentum: float = 0.02) -> FeatureSpaceAdapter:
        if x.ndim != 2 or len(x) < 2:
            raise ValueError("calibration features must be a 2D matrix with at least two rows")
        scale = np.maximum(x.std(axis=0), 1e-6)
        mean = x.mean(axis=0)
        return cls(
            calibration_mean=mean,
            calibration_scale=scale,
            momentum=momentum,
            runtime_mean=mean.copy(),
            runtime_scale=scale.copy(),
        )

    def transform(self, x: np.ndarray) -> np.ndarray:
        if self.runtime_mean is None or self.runtime_scale is None:
            return x
        z = (x - self.runtime_mean) / self.runtime_scale
        return z * self.calibration_scale + self.calibration_mean

    def update(self, x: np.ndarray) -> None:
        if self.runtime_mean is None or self.runtime_scale is None:
            self.runtime_mean = x.copy()
            self.runtime_scale = np.ones_like(x)
            return
        delta = x - self.runtime_mean
        self.runtime_mean = (1 - self.momentum) * self.runtime_mean + self.momentum * x
        deviation = np.maximum(np.abs(delta), 1e-6)
        self.runtime_scale = (1 - self.momentum) * self.runtime_scale + self.momentum * deviation

    def state_dict(self) -> dict[str, Any]:
        return {
            "momentum": self.momentum,
            "calibration_mean": self.calibration_mean.tolist(),
            "calibration_scale": self.calibration_scale.tolist(),
            "runtime_mean": None if self.runtime_mean is None else self.runtime_mean.tolist(),
            "runtime_scale": None if self.runtime_scale is None else self.runtime_scale.tolist(),
        }


def run_feature_normalization_adaptation(
    model: Any,
    x_calibration: np.ndarray,
    x_runtime: np.ndarray,
    *,
    confidence_threshold: float = 0.6,
    momentum: float = 0.02,
) -> AdaptationResult:
    """Run a causal normalization-only adaptation replay."""
    if not 0 <= confidence_threshold <= 1:
        raise ValueError("confidence_threshold must be between 0 and 1")
    adapter = FeatureSpaceAdapter.from_calibration(x_calibration, momentum=momentum)
    predictions: list[str] = []
    adapted_rows: list[np.ndarray] = []
    events: list[AdaptationEvent] = []

    for index, row in enumerate(x_runtime):
        adapted = adapter.transform(row)
        adapted_rows.append(adapted)
        prediction = model.predict(adapted.reshape(1, -1))[0]
        confidence = _confidence(model, adapted)
        predictions.append(str(prediction))
        if confidence >= confidence_threshold:
            adapter.update(row)
            events.append(AdaptationEvent(index=index, confidence=confidence))

    adapted_features = (
        np.stack(adapted_rows) if adapted_rows else np.empty((0, x_calibration.shape[1]))
    )
    return AdaptationResult(
        predictions=np.asarray(predictions, dtype=object),
        adapted_features=adapted_features,
        events=events,
    )


def adaptation_report(
    result: AdaptationResult,
    *,
    confidence_threshold: float,
    momentum: float,
) -> dict[str, Any]:
    return {
        "strategy": "feature_normalization",
        "confidence_threshold": confidence_threshold,
        "momentum": momentum,
        "update_count": len(result.events),
        "events": [asdict(event) for event in result.events],
    }


def _confidence(model: Any, x: np.ndarray) -> float:
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(x.reshape(1, -1))[0]
        return float(np.max(probabilities))
    return 1.0
