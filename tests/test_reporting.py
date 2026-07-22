from __future__ import annotations

import json

from driftproof.acquisition.simulated import generate_synthetic_session, write_jsonl
from driftproof.evaluation.reporting import evaluate_session, write_scorecard_report


def test_evaluate_session_returns_machine_readable_scorecard(tmp_path) -> None:
    path = tmp_path / "session.jsonl"
    samples = generate_synthetic_session(seconds=12, sample_rate_hz=100, drift_after_s=6)
    write_jsonl(samples, path)

    report = evaluate_session(path, sample_rate_hz=100)

    assert report["schema_version"] == 1
    assert report["config"]["sample_rate_hz"] == 100
    assert set(report["splits"]) == {"baseline", "drifted", "drifted_adapted"}
    assert report["splits"]["baseline"]["n_windows"] > 0
    assert report["splits"]["drifted"]["n_windows"] > 0
    assert report["splits"]["drifted"]["drift_score_mean"] is not None
    assert "confusion_matrix" in report["splits"]["drifted"]
    assert "per_intent_failure_rate" in report["splits"]["drifted"]
    assert report["functional"]["baseline"]["n_steps"] > 0
    assert report["functional"]["drifted"]["wrong_direction_commands"] >= 0
    assert report["functional"]["drifted_adapted"]["n_steps"] > 0
    assert report["adaptation"]["enabled"] is True
    assert report["adaptation"]["update_count"] >= 0
    assert report["drift_calibration"]["target"] == "prediction_failure"
    assert report["drift_calibration"]["best"] is not None


def test_evaluate_session_can_disable_adaptation(tmp_path) -> None:
    path = tmp_path / "session.jsonl"
    samples = generate_synthetic_session(seconds=12, sample_rate_hz=100, drift_after_s=6)
    write_jsonl(samples, path)

    report = evaluate_session(path, sample_rate_hz=100, adaptation_enabled=False)

    assert set(report["splits"]) == {"baseline", "drifted"}
    assert report["adaptation"] == {"enabled": False}


def test_write_scorecard_report_creates_json(tmp_path) -> None:
    report = {
        "schema_version": 1,
        "source": "demo",
        "config": {"sample_rate_hz": 100},
        "splits": {},
    }
    path = tmp_path / "reports" / "scorecard.json"

    write_scorecard_report(report, path)

    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded == report
