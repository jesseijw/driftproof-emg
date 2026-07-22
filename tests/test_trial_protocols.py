from __future__ import annotations

import json
from collections import Counter

import pytest

from driftproof.acquisition.replay import iter_jsonl_records
from driftproof.protocols.trials import (
    generate_trial_schedule,
    trials_to_task_events,
    write_trial_schedule_jsonl,
)


def test_generate_trial_schedule_is_balanced_and_deterministic() -> None:
    first = generate_trial_schedule(repetitions_per_label=3, seed=7)
    second = generate_trial_schedule(repetitions_per_label=3, seed=7)

    assert [trial.label for trial in first] == [trial.label for trial in second]
    assert Counter(trial.label for trial in first) == {"rest": 3, "open": 3, "close": 3}
    assert all(trial.t_end > trial.t_start for trial in first)


def test_generate_trial_schedule_rejects_bad_durations() -> None:
    with pytest.raises(ValueError, match="cue_s"):
        generate_trial_schedule(cue_s=0)


def test_trials_to_task_events_emits_start_and_rest_events() -> None:
    trials = generate_trial_schedule(repetitions_per_label=1, seed=1)
    events = trials_to_task_events("s1", trials)

    assert len(events) == 6
    assert events[0]["type"] == "task_event"
    assert str(events[0]["name"]).startswith("target_")
    assert events[1]["name"] == "target_rest"


def test_write_trial_schedule_jsonl_is_replay_known(tmp_path) -> None:
    out = tmp_path / "protocol.jsonl"
    trials = generate_trial_schedule(repetitions_per_label=1, seed=2)

    count = write_trial_schedule_jsonl(trials, out, session_id="s1")
    records = list(iter_jsonl_records(out))

    assert count == 3
    assert records[0]["type"] == "protocol_metadata"
    assert Counter(record["type"] for record in records) == {
        "protocol_metadata": 1,
        "trial_spec": 3,
        "task_event": 6,
    }
    assert json.loads(out.read_text(encoding="utf-8").splitlines()[0])["session_id"] == "s1"
