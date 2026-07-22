from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import numpy as np

from driftproof.types import IntentLabel

TrialPhase = Literal["calibration", "task", "perturbation"]


@dataclass(frozen=True)
class TrialSpec:
    index: int
    label: IntentLabel
    phase: TrialPhase
    t_start: float
    t_end: float
    rest_before_s: float
    cue_s: float


def generate_trial_schedule(
    *,
    phase: TrialPhase = "calibration",
    repetitions_per_label: int = 5,
    cue_s: float = 2.0,
    rest_s: float = 1.0,
    seed: int = 42,
    start_t: float = 0.0,
) -> list[TrialSpec]:
    if repetitions_per_label <= 0:
        raise ValueError("repetitions_per_label must be positive")
    if cue_s <= 0 or rest_s < 0:
        raise ValueError("cue_s must be positive and rest_s must be non-negative")
    labels: list[IntentLabel] = ["rest", "open", "close"] * repetitions_per_label
    rng = np.random.default_rng(seed)
    rng.shuffle(labels)

    trials: list[TrialSpec] = []
    t = start_t
    for index, label in enumerate(labels, start=1):
        t += rest_s
        t_start = t
        t_end = t_start + cue_s
        trials.append(
            TrialSpec(
                index=index,
                label=label,
                phase=phase,
                t_start=t_start,
                t_end=t_end,
                rest_before_s=rest_s,
                cue_s=cue_s,
            )
        )
        t = t_end
    return trials


def trials_to_task_events(session_id: str, trials: Iterable[TrialSpec]) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    for trial in trials:
        events.append(
            {
                "type": "task_event",
                "session_id": session_id,
                "t": trial.t_start,
                "name": f"target_{trial.label}",
                "label": trial.label,
                "trial_index": trial.index,
                "phase": trial.phase,
            }
        )
        events.append(
            {
                "type": "task_event",
                "session_id": session_id,
                "t": trial.t_end,
                "name": "target_rest",
                "label": "rest",
                "trial_index": trial.index,
                "phase": trial.phase,
            }
        )
    return events


def write_trial_schedule_jsonl(
    trials: Iterable[TrialSpec],
    out: str | Path,
    *,
    session_id: str,
) -> int:
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    trial_list = list(trials)
    records = [
        {
            "type": "protocol_metadata",
            "session_id": session_id,
            "trial_count": len(trial_list),
        }
    ]
    records.extend(
        {"type": "trial_spec", "session_id": session_id, **asdict(trial)}
        for trial in trial_list
    )
    records.extend(trials_to_task_events(session_id, trial_list))

    with out_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, separators=(",", ":")) + "\n")
    return len(trial_list)
