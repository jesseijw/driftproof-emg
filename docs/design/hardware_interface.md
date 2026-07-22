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
- Dropped samples are detectable.
- Live acquisition can save a complete `.jsonl` session.
- Hardware-specific code is isolated inside `acquisition`.
