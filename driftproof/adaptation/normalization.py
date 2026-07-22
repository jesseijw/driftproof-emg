from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class RunningNormalizer:
    """Cautious normalization-only adaptation baseline."""

    momentum: float = 0.01
    mean: np.ndarray | None = None
    scale: np.ndarray | None = None

    def update(self, x: np.ndarray) -> None:
        batch_mean = x.mean(axis=0)
        batch_scale = np.maximum(x.std(axis=0), 1e-6)
        if self.mean is None:
            self.mean = batch_mean
            self.scale = batch_scale
            return
        self.mean = (1 - self.momentum) * self.mean + self.momentum * batch_mean
        self.scale = (1 - self.momentum) * self.scale + self.momentum * batch_scale

    def transform(self, x: np.ndarray) -> np.ndarray:
        if self.mean is None or self.scale is None:
            return x
        return (x - self.mean) / self.scale
