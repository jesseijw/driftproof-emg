# Data Schema

Each session is newline-delimited JSON. Records are append-only.

## Record Types

### `emg_sample`

```json
{
  "type": "emg_sample",
  "session_id": "demo",
  "t": 0.123,
  "channels": [0.01, -0.02, 0.03, 0.00],
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
