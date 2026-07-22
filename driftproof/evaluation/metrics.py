from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

from driftproof.types import Scorecard

INTENT_LABELS = ["rest", "open", "close"]


def classify_scorecard(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    drift_scores: np.ndarray | None = None,
) -> Scorecard:
    labels = _labels_for(y_true, y_pred)
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    matrix_by_label = {
        true_label: {
            predicted_label: int(matrix[true_idx, pred_idx])
            for pred_idx, predicted_label in enumerate(labels)
        }
        for true_idx, true_label in enumerate(labels)
    }
    per_intent_failure_rate = {
        label: _failure_rate(matrix, index) for index, label in enumerate(labels)
    }
    return Scorecard(
        accuracy=float(accuracy_score(y_true, y_pred)),
        macro_f1=float(f1_score(y_true, y_pred, average="macro")),
        drift_score_mean=float(np.mean(drift_scores)) if drift_scores is not None else None,
        n_windows=int(len(y_true)),
        confusion_matrix=matrix_by_label,
        per_intent_failure_rate=per_intent_failure_rate,
    )


def _labels_for(y_true: np.ndarray, y_pred: np.ndarray) -> list[str]:
    observed = {str(label) for label in np.concatenate([y_true, y_pred])}
    return [label for label in INTENT_LABELS if label in observed]


def _failure_rate(matrix: np.ndarray, index: int) -> float:
    total = int(matrix[index].sum())
    if total == 0:
        return 0.0
    correct = int(matrix[index, index])
    return float((total - correct) / total)
