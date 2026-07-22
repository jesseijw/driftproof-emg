# Data Schema

Each session is newline-delimited JSON. Records are append-only.

## Replay Rules

- Every non-empty line must be a JSON object.
- Every record must include a string `type`.
- Unknown record types are rejected.
- `emg_sample` records require `session_id`, `t`, `channels`, and `label`.
- `emg_sample.t` must be finite, non-negative, and monotonic within a replay.
- `emg_sample.channels` must be a one-dimensional numeric list.
- Channel count must stay fixed within a replay.
- Known non-EMG records are validated at the record-envelope level and skipped
  by EMG-only readers.

## Record Types

### `session_metadata`

```json
{
  "type": "session_metadata",
  "session_id": "demo",
  "participant_id": "p001",
  "device": "synthetic",
  "sample_rate_hz": 1000
}
```

### `emg_sample`

```json
{
  "type": "emg_sample",
  "session_id": "demo",
  "t": 0.123,
  "channels": [0.01, -0.02, 0.03, 0.00],
  "label": "open",
  "condition": "baseline",
  "dropped_samples": 0,
  "sensor_status": "ok"
}
```

### `imu_sample`

```json
{
  "type": "imu_sample",
  "session_id": "demo",
  "t": 0.123,
  "quat": [1, 0, 0, 0],
  "gyro": [0, 0, 0],
  "accel": [0, 0, 9.81]
}
```

### `task_event`

```json
{
  "type": "task_event",
  "session_id": "demo",
  "t": 1.5,
  "name": "target_open",
  "label": "open"
}
```

### `prediction`

```json
{
  "type": "prediction",
  "session_id": "demo",
  "t": 1.7,
  "intent": "open",
  "confidence": 0.82,
  "drift_score": 1.4
}
```

## Session Manifest

Every dataset release should include:

- participant anonymized id
- session id and date
- device hardware revision
- firmware version
- electrode placement metadata
- displacement condition
- preprocessing config hash
- model version id
- task protocol id
- exclusions and failure notes
