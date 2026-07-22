from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from driftproof.acquisition.replay import read_jsonl
from driftproof.drift.mahalanobis import fit_reference, score
from driftproof.evaluation.metrics import classify_scorecard
from driftproof.features.classical import extract_many, feature_matrix
from driftproof.models.baseline import train_baseline
from driftproof.preprocessing.windowing import make_windows
from driftproof.types import Scorecard


def evaluate_session(
    path: str | Path,
    *,
    window_ms: int = 200,
    step_ms: int = 100,
    sample_rate_hz: int = 1_000,
) -> dict[str, Any]:
    samples = read_jsonl(path)
    windows = make_windows(
        samples,
        window_ms=window_ms,
        step_ms=step_ms,
        sample_rate_hz=sample_rate_hz,
    )
    rows = extract_many(windows)
    x, y, condition = feature_matrix(rows)
    train_mask = condition == "baseline"
    test_mask = condition == "drifted"
    if not train_mask.any() or not test_mask.any():
        raise ValueError("session must include both baseline and drifted windows")

    model = train_baseline(x[train_mask], y[train_mask])
    pred_baseline = model.predict(x[train_mask])
    pred_drifted = model.predict(x[test_mask])

    ref = fit_reference(x[train_mask])
    drift_scores = score(ref, x[test_mask])

    baseline_score = classify_scorecard(y[train_mask], pred_baseline)
    drifted_score = classify_scorecard(y[test_mask], pred_drifted, drift_scores=drift_scores)
    return {
        "schema_version": 1,
        "source": str(path),
        "config": {
            "window_ms": window_ms,
            "step_ms": step_ms,
            "sample_rate_hz": sample_rate_hz,
        },
        "splits": {
            "baseline": _scorecard_dict(baseline_score),
            "drifted": _scorecard_dict(drifted_score),
        },
    }


def write_scorecard_report(report: dict[str, Any], path: str | Path) -> None:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _scorecard_dict(scorecard: Scorecard) -> dict[str, Any]:
    return asdict(scorecard)
