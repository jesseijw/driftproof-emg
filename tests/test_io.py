from __future__ import annotations

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
