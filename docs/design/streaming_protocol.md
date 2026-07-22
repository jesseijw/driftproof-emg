# Streaming Protocol

The streaming protocol is intentionally simple: newline-delimited JSON records.
That makes sessions easy to inspect, replay, diff, and archive.

## Transport

The first live implementation can use serial USB. The same records can also be
written to a `.jsonl` file for replay.

Each line is one JSON object with:

- `type`: record type.
- `timestamp_s`: monotonic session time in seconds.
- `payload`: type-specific data.

## `emg_sample`

```json
{
  "type": "emg_sample",
  "timestamp_s": 12.345,
  "payload": {
    "channels": [0.02, -0.01, 0.04, 0.01],
    "sample_rate_hz": 1000,
    "units": "mV"
  }
}
```

Rules:

- Channel count must be fixed within a session.
- Samples must be emitted in timestamp order.
- Missing samples should be represented by a gap in timestamps, not fake zeros.

## `task_event`

```json
{
  "type": "task_event",
  "timestamp_s": 20.0,
  "payload": {
    "label": "open",
    "phase": "trial_start"
  }
}
```

Task events mark ground truth intent, calibration boundaries, perturbations,
and trial outcomes.

## `prediction`

```json
{
  "type": "prediction",
  "timestamp_s": 20.25,
  "payload": {
    "intent": "open",
    "confidence": 0.82,
    "drift_score": 1.7
  }
}
```

Prediction records are optional during acquisition and useful during replay or
interactive demos.

## Acceptance Criteria

- Session files can be parsed line by line without loading everything into RAM.
- Bad records fail with a clear message that includes the line number.
- Replay produces the same ordered records that live acquisition would emit.
- The protocol supports at least `rest`, `open`, and `close` intent labels.
