from __future__ import annotations

import pytest

from driftproof.acquisition.replay import SessionFormatError
from driftproof.acquisition.simulated import generate_synthetic_session, read_jsonl, write_jsonl


def test_jsonl_round_trip(tmp_path) -> None:
    path = tmp_path / "session.jsonl"
    samples = generate_synthetic_session(seconds=1, sample_rate_hz=20)
    write_jsonl(samples, path)
    loaded = read_jsonl(path)
    assert len(loaded) == len(samples)
    assert loaded[0].session_id == samples[0].session_id
    assert loaded[0].label == samples[0].label
    assert loaded[0].channels.shape == (4,)


def test_read_jsonl_reports_line_number_for_bad_json(tmp_path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text('{"type":"session_metadata"}\n{"type":', encoding="utf-8")

    with pytest.raises(SessionFormatError, match=r"bad\.jsonl:2: invalid JSON"):
        read_jsonl(path)


def test_read_jsonl_rejects_missing_required_emg_field(tmp_path) -> None:
    path = tmp_path / "missing.jsonl"
    path.write_text(
        '{"type":"emg_sample","session_id":"demo","t":0,"channels":[0,1,2,3]}\n',
        encoding="utf-8",
    )

    with pytest.raises(SessionFormatError, match="field 'label'"):
        read_jsonl(path)


def test_read_jsonl_rejects_timestamp_regression(tmp_path) -> None:
    path = tmp_path / "time.jsonl"
    path.write_text(
        "\n".join(
            [
                (
                    '{"type":"emg_sample","session_id":"demo","t":1,'
                    '"channels":[0,1,2,3],"label":"rest"}'
                ),
                (
                    '{"type":"emg_sample","session_id":"demo","t":0.5,'
                    '"channels":[0,1,2,3],"label":"open"}'
                ),
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(SessionFormatError, match="timestamps must be monotonic"):
        read_jsonl(path)


def test_read_jsonl_rejects_channel_count_change(tmp_path) -> None:
    path = tmp_path / "channels.jsonl"
    path.write_text(
        "\n".join(
            [
                (
                    '{"type":"emg_sample","session_id":"demo","t":0,'
                    '"channels":[0,1,2,3],"label":"rest"}'
                ),
                (
                    '{"type":"emg_sample","session_id":"demo","t":1,'
                    '"channels":[0,1,2],"label":"open"}'
                ),
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(SessionFormatError, match="channel count changed"):
        read_jsonl(path)


def test_read_jsonl_skips_known_non_emg_records(tmp_path) -> None:
    path = tmp_path / "mixed.jsonl"
    path.write_text(
        "\n".join(
            [
                '{"type":"session_metadata","session_id":"demo"}',
                '{"type":"task_event","session_id":"demo","t":0,"name":"target_open"}',
                (
                    '{"type":"emg_sample","session_id":"demo","t":0,'
                    '"channels":[0,1,2,3],"label":"open"}'
                ),
            ]
        ),
        encoding="utf-8",
    )

    samples = read_jsonl(path)

    assert len(samples) == 1
    assert samples[0].label == "open"
