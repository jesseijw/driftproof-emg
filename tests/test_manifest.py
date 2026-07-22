from __future__ import annotations

import json

import pytest

from driftproof.acquisition.simulated import generate_synthetic_session, write_jsonl
from driftproof.experiments.manifest import (
    ManifestError,
    load_manifest,
    parse_manifest,
    run_manifest,
)


def test_parse_manifest_resolves_relative_paths(tmp_path) -> None:
    manifest = parse_manifest(
        {
            "name": "demo",
            "session_path": "data/session.jsonl",
            "report_path": "reports/scorecard.json",
        },
        base_dir=tmp_path,
    )

    assert manifest.session_path == tmp_path / "data/session.jsonl"
    assert manifest.report_path == tmp_path / "reports/scorecard.json"
    assert manifest.evaluation.window_ms == 200
    assert manifest.adaptation.enabled is True


def test_load_manifest_rejects_bad_config(tmp_path) -> None:
    path = tmp_path / "experiment.json"
    path.write_text(
        json.dumps(
            {
                "name": "bad",
                "session_path": "session.jsonl",
                "report_path": "report.json",
                "adaptation": {"confidence_threshold": 2.0},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ManifestError, match="confidence_threshold"):
        load_manifest(path)


def test_run_manifest_writes_report_with_manifest_provenance(tmp_path) -> None:
    session_path = tmp_path / "session.jsonl"
    report_path = tmp_path / "report.json"
    manifest_path = tmp_path / "experiment.json"
    samples = generate_synthetic_session(seconds=12, sample_rate_hz=100, drift_after_s=6)
    write_jsonl(samples, session_path)
    manifest_path.write_text(
        json.dumps(
            {
                "name": "synthetic_smoke",
                "session_path": "session.jsonl",
                "report_path": "report.json",
                "evaluation": {"sample_rate_hz": 100},
                "adaptation": {"enabled": False},
            }
        ),
        encoding="utf-8",
    )

    report = run_manifest(manifest_path)
    loaded = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["experiment"]["name"] == "synthetic_smoke"
    assert loaded["experiment"]["name"] == "synthetic_smoke"
    assert loaded["adaptation"] == {"enabled": False}
