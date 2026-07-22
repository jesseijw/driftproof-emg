from __future__ import annotations

import json

import pytest

from driftproof.acquisition.capture import (
    CaptureConfig,
    CaptureFormatError,
    capture_lines_to_jsonl,
    normalize_capture_lines,
)
from driftproof.acquisition.replay import read_jsonl


def test_normalize_capture_lines_synthesizes_timestamps() -> None:
    records = list(
        normalize_capture_lines(
            [
                '{"channels":[0,1,2,3]}',
                '{"channels":[1,2,3,4]}',
            ],
            CaptureConfig(session_id="s1", sample_rate_hz=10, label="open"),
        )
    )

    assert records[0]["session_id"] == "s1"
    assert records[0]["t"] == 0.0
    assert records[1]["t"] == 0.1
    assert records[0]["label"] == "open"


def test_normalize_capture_lines_detects_sequence_gaps() -> None:
    records = list(
        normalize_capture_lines(
            [
                '{"seq":10,"channels":[0,1,2,3]}',
                '{"seq":13,"channels":[1,2,3,4]}',
            ],
            CaptureConfig(session_id="s1", sample_rate_hz=10),
        )
    )

    assert records[0]["dropped_samples"] == 0
    assert records[1]["dropped_samples"] == 2


def test_capture_lines_to_jsonl_writes_replayable_file(tmp_path) -> None:
    out = tmp_path / "capture.jsonl"

    count = capture_lines_to_jsonl(
        [
            '{"seq":1,"channels":[0,1,2,3],"label":"rest","condition":"baseline"}',
            '{"seq":2,"channels":[1,2,3,4],"label":"open","condition":"baseline"}',
        ],
        out,
        CaptureConfig(session_id="s1", sample_rate_hz=10),
    )
    samples = read_jsonl(out)

    assert count == 2
    assert len(samples) == 2
    assert samples[1].label == "open"


def test_capture_lines_to_jsonl_rejects_bad_raw_json(tmp_path) -> None:
    with pytest.raises(CaptureFormatError, match="invalid JSON"):
        capture_lines_to_jsonl(
            ['{"channels":'],
            tmp_path / "capture.jsonl",
            CaptureConfig(session_id="s1", sample_rate_hz=10),
        )


def test_capture_lines_to_jsonl_rejects_non_numeric_channels(tmp_path) -> None:
    with pytest.raises(CaptureFormatError, match="only numbers"):
        capture_lines_to_jsonl(
            ['{"channels":[0,"bad"]}'],
            tmp_path / "capture.jsonl",
            CaptureConfig(session_id="s1", sample_rate_hz=10),
        )


def test_capture_file_output_is_jsonl(tmp_path) -> None:
    out = tmp_path / "capture.jsonl"
    capture_lines_to_jsonl(
        ['{"channels":[0,1,2,3]}'],
        out,
        CaptureConfig(session_id="s1", sample_rate_hz=10),
    )

    lines = out.read_text(encoding="utf-8").splitlines()
    assert json.loads(lines[0])["type"] == "emg_sample"
