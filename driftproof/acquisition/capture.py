from __future__ import annotations

import json
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from driftproof.acquisition.replay import SessionFormatError, read_jsonl
from driftproof.types import IntentLabel


@dataclass(frozen=True)
class CaptureConfig:
    session_id: str
    sample_rate_hz: int
    label: IntentLabel = "rest"
    condition: str = "baseline"
    sensor_status: str = "ok"


class CaptureFormatError(ValueError):
    """Raised when raw capture lines cannot be converted to session records."""


def normalize_capture_lines(
    lines: Iterable[str],
    config: CaptureConfig,
) -> Iterator[dict[str, Any]]:
    """Convert firmware JSON lines into DriftProof session records.

    Accepted firmware records may either be complete `emg_sample` records or
    compact records containing `channels` plus optional `t`, `seq`, and
    `sensor_status` fields.
    """
    if config.sample_rate_hz <= 0:
        raise ValueError("sample_rate_hz must be positive")

    previous_seq: int | None = None
    sample_index = 0
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        record = _parse_line(line, line_number)
        if record.get("type", "emg_sample") != "emg_sample":
            yield record
            continue

        channels = _channels(record, line_number)
        seq = _optional_int(record, "seq", line_number)
        dropped_samples = _dropped_samples(previous_seq, seq)
        if seq is not None:
            previous_seq = seq

        normalized = {
            "type": "emg_sample",
            "session_id": _optional_string(record, "session_id", config.session_id),
            "t": _timestamp(record, sample_index, config.sample_rate_hz, line_number),
            "channels": channels,
            "label": _optional_string(record, "label", config.label),
            "condition": _optional_string(record, "condition", config.condition),
            "dropped_samples": int(record.get("dropped_samples", 0)) + dropped_samples,
            "sensor_status": _optional_string(record, "sensor_status", config.sensor_status),
        }
        yield normalized
        sample_index += 1


def capture_lines_to_jsonl(
    lines: Iterable[str],
    out: str | Path,
    config: CaptureConfig,
) -> int:
    """Write normalized capture records to JSONL and validate replay compatibility."""
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for record in normalize_capture_lines(lines, config):
            f.write(json.dumps(record, separators=(",", ":")) + "\n")
            if record.get("type") == "emg_sample":
                count += 1

    try:
        read_jsonl(out_path)
    except SessionFormatError as exc:
        raise CaptureFormatError(f"captured file is not replay-compatible: {exc}") from exc
    return count


def _parse_line(line: str, line_number: int) -> dict[str, Any]:
    try:
        record = json.loads(line)
    except json.JSONDecodeError as exc:
        raise CaptureFormatError(f"capture line {line_number}: invalid JSON: {exc.msg}") from exc
    if not isinstance(record, dict):
        raise CaptureFormatError(f"capture line {line_number}: record must be a JSON object")
    return record


def _channels(record: Mapping[str, Any], line_number: int) -> list[float]:
    value = record.get("channels")
    if not isinstance(value, list) or not value:
        raise CaptureFormatError(
            f"capture line {line_number}: field 'channels' must be a non-empty numeric list"
        )
    try:
        channels = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise CaptureFormatError(
            f"capture line {line_number}: field 'channels' must contain only numbers"
        ) from exc
    if channels.ndim != 1 or not np.all(np.isfinite(channels)):
        raise CaptureFormatError(
            f"capture line {line_number}: field 'channels' must be a finite 1D numeric list"
        )
    return channels.tolist()


def _timestamp(
    record: Mapping[str, Any],
    sample_index: int,
    sample_rate_hz: int,
    line_number: int,
) -> float:
    value = record.get("t")
    if value is None:
        return sample_index / sample_rate_hz
    if not isinstance(value, int | float):
        raise CaptureFormatError(f"capture line {line_number}: field 't' must be numeric")
    timestamp = float(value)
    if not np.isfinite(timestamp) or timestamp < 0:
        raise CaptureFormatError(f"capture line {line_number}: field 't' must be finite and >= 0")
    return timestamp


def _optional_string(record: Mapping[str, Any], field_name: str, default: str) -> str:
    value = record.get(field_name, default)
    return value if isinstance(value, str) and value else default


def _optional_int(record: Mapping[str, Any], field_name: str, line_number: int) -> int | None:
    value = record.get(field_name)
    if value is None:
        return None
    if not isinstance(value, int):
        raise CaptureFormatError(f"capture line {line_number}: field '{field_name}' must be an int")
    return value


def _dropped_samples(previous_seq: int | None, seq: int | None) -> int:
    if previous_seq is None or seq is None:
        return 0
    gap = seq - previous_seq - 1
    return max(0, gap)
