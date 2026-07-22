from __future__ import annotations

import json
from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import Any

import numpy as np

from driftproof.types import EmgSample, IntentLabel

KNOWN_RECORD_TYPES = {"emg_sample", "imu_sample", "task_event", "prediction", "session_metadata"}
INTENT_LABELS: set[str] = {"rest", "open", "close"}


class SessionFormatError(ValueError):
    """Raised when a replay session file violates the JSONL data contract."""


def iter_jsonl_records(path: str | Path) -> Iterator[dict[str, Any]]:
    """Yield validated JSON objects from a session file with line-numbered errors."""
    session_path = Path(path)
    with session_path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise _error(session_path, line_number, f"invalid JSON: {exc.msg}") from exc

            if not isinstance(record, dict):
                raise _error(session_path, line_number, "record must be a JSON object")

            record_type = record.get("type")
            if not isinstance(record_type, str) or not record_type:
                raise _error(session_path, line_number, "record requires string field 'type'")
            if record_type not in KNOWN_RECORD_TYPES:
                raise _error(session_path, line_number, f"unknown record type '{record_type}'")

            yield record


def read_jsonl(path: str | Path) -> list[EmgSample]:
    """Read EMG samples from a replay session file.

    Non-EMG records are validated at the envelope level and skipped. EMG records
    are fully validated and converted to typed samples.
    """
    session_path = Path(path)
    samples: list[EmgSample] = []
    expected_channel_count: int | None = None
    previous_t: float | None = None

    for line_number, record in _iter_numbered_jsonl_records(session_path):
        if record["type"] != "emg_sample":
            continue

        sample = _parse_emg_sample(session_path, line_number, record)
        if expected_channel_count is None:
            expected_channel_count = len(sample.channels)
        elif len(sample.channels) != expected_channel_count:
            raise _error(
                session_path,
                line_number,
                f"channel count changed from {expected_channel_count} to {len(sample.channels)}",
            )

        if previous_t is not None and sample.t < previous_t:
            raise _error(session_path, line_number, "sample timestamps must be monotonic")
        previous_t = sample.t
        samples.append(sample)

    if not samples:
        raise SessionFormatError(f"{session_path}: no emg_sample records found")
    return samples


def write_jsonl(samples: Iterable[EmgSample], path: str | Path) -> None:
    """Write EMG samples as replayable newline-delimited JSON."""
    session_path = Path(path)
    session_path.parent.mkdir(parents=True, exist_ok=True)
    with session_path.open("w", encoding="utf-8") as f:
        for sample in samples:
            record = {
                "type": "emg_sample",
                "session_id": sample.session_id,
                "t": sample.t,
                "channels": sample.channels.tolist(),
                "label": sample.label,
                "condition": sample.condition,
                "dropped_samples": sample.dropped_samples,
                "sensor_status": sample.sensor_status,
            }
            f.write(json.dumps(record, separators=(",", ":")) + "\n")


def _iter_numbered_jsonl_records(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise _error(path, line_number, f"invalid JSON: {exc.msg}") from exc

            if not isinstance(record, dict):
                raise _error(path, line_number, "record must be a JSON object")

            record_type = record.get("type")
            if not isinstance(record_type, str) or not record_type:
                raise _error(path, line_number, "record requires string field 'type'")
            if record_type not in KNOWN_RECORD_TYPES:
                raise _error(path, line_number, f"unknown record type '{record_type}'")

            yield line_number, record


def _parse_emg_sample(path: Path, line_number: int, record: Mapping[str, Any]) -> EmgSample:
    session_id = _string_field(path, line_number, record, "session_id")
    t = _float_field(path, line_number, record, "t")
    channels = _channels_field(path, line_number, record)
    label = _label_field(path, line_number, record)
    condition = _optional_string_field(record, "condition", default="baseline")
    dropped_samples = _int_field(path, line_number, record, "dropped_samples", default=0)
    sensor_status = _optional_string_field(record, "sensor_status", default="ok")

    if t < 0:
        raise _error(path, line_number, "field 't' must be non-negative")
    if dropped_samples < 0:
        raise _error(path, line_number, "field 'dropped_samples' must be non-negative")

    return EmgSample(
        session_id=session_id,
        t=t,
        channels=channels,
        label=label,
        condition=condition,
        dropped_samples=dropped_samples,
        sensor_status=sensor_status,
    )


def _string_field(
    path: Path, line_number: int, record: Mapping[str, Any], field_name: str
) -> str:
    value = record.get(field_name)
    if not isinstance(value, str) or not value:
        raise _error(path, line_number, f"field '{field_name}' must be a non-empty string")
    return value


def _optional_string_field(record: Mapping[str, Any], field_name: str, *, default: str) -> str:
    value = record.get(field_name, default)
    if not isinstance(value, str) or not value:
        return default
    return value


def _float_field(
    path: Path, line_number: int, record: Mapping[str, Any], field_name: str
) -> float:
    value = record.get(field_name)
    if not isinstance(value, int | float):
        raise _error(path, line_number, f"field '{field_name}' must be numeric")
    numeric = float(value)
    if not np.isfinite(numeric):
        raise _error(path, line_number, f"field '{field_name}' must be finite")
    return numeric


def _int_field(
    path: Path, line_number: int, record: Mapping[str, Any], field_name: str, *, default: int
) -> int:
    value = record.get(field_name, default)
    if not isinstance(value, int):
        raise _error(path, line_number, f"field '{field_name}' must be an integer")
    return value


def _channels_field(path: Path, line_number: int, record: Mapping[str, Any]) -> np.ndarray:
    value = record.get("channels")
    if not isinstance(value, list) or not value:
        raise _error(path, line_number, "field 'channels' must be a non-empty numeric list")
    try:
        channels = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise _error(path, line_number, "field 'channels' must contain only numbers") from exc
    if channels.ndim != 1:
        raise _error(path, line_number, "field 'channels' must be one-dimensional")
    if not np.all(np.isfinite(channels)):
        raise _error(path, line_number, "field 'channels' must contain only finite numbers")
    return channels


def _label_field(path: Path, line_number: int, record: Mapping[str, Any]) -> IntentLabel:
    value = record.get("label")
    if value not in INTENT_LABELS:
        raise _error(path, line_number, "field 'label' must be one of: rest, open, close")
    return value  # type: ignore[return-value]


def _error(path: Path, line_number: int, message: str) -> SessionFormatError:
    return SessionFormatError(f"{path}:{line_number}: {message}")
