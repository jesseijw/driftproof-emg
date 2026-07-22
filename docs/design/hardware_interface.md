# Hardware Interface

Hardware integration should implement the same session contract used by
simulation. The hardware is a data source, not a special pipeline.

## Candidate Devices

- Four-channel EMG front end
- Microcontroller with USB serial
- Optional IMU
- Optional one-motor gripper for late-stage demos

## Acquisition Contract

The hardware adapter must emit `emg_sample` records that match the streaming
protocol:

- Monotonic timestamps
- Fixed channel count
- Declared sample rate
- Declared units
- Raw or calibrated channel values

The current software can normalize compact firmware JSONL into replayable
session files:

```bash
driftproof capture-file firmware_dump.jsonl \
  --out data/raw/session.jsonl \
  --session-id bench_001 \
  --sample-rate-hz 1000 \
  --label rest \
  --condition baseline
```

Accepted compact firmware line:

```json
{"seq": 101, "channels": [0.02, -0.01, 0.04, 0.01]}
```

The adapter adds missing `type`, `session_id`, `t`, `label`, `condition`,
`dropped_samples`, and `sensor_status` fields. If `t` is missing, it synthesizes
timestamps from line order and `sample_rate_hz`. If `seq` jumps, it records the
gap in `dropped_samples`.

## Firmware Requirements

- Stable sample timing
- Sequence number or timestamp per sample
- Clear startup metadata
- Detectable disconnect behavior
- No hidden filtering that cannot be documented

## Safety

The physical gripper should not be connected until the virtual gripper path can
show stable behavior under replay. The first motor demo should include an
operator stop and conservative speed limits.

## Acceptance Criteria

- Hardware capture can be replayed through the same evaluator as synthetic data.
- Dropped samples are detectable from sequence gaps.
- File-based firmware capture can save a complete `.jsonl` session.
- Hardware-specific code is isolated inside `acquisition`.
