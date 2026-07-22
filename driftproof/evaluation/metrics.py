from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, f1_score

from driftproof.types import Scorecard


def classify_scorecard(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    drift_scores: np.ndarray | None = None,
) -> Scorecard:
    return Scorecard(
        accuracy=float(accuracy_score(y_true, y_pred)),
        macro_f1=float(f1_score(y_true, y_pred, average="macro")),
        drift_score_mean=float(np.mean(drift_scores)) if drift_scores is not None else None,
        n_windows=int(len(y_true)),
    )
