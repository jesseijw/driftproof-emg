# Virtual Gripper

The virtual gripper is the first operator-facing demo. It lets the project test
control logic, latency, and task scoring before a physical prosthetic is built.

## Commands

The MVP supports three discrete commands:

- `rest`
- `open`
- `close`

The gripper state can be represented as a scalar from `0.0` closed to `1.0`
open. Commands update the scalar at a fixed velocity.

## Task Events

Trials should emit task events:

- `trial_start`
- `target_open`
- `target_close`
- `target_rest`
- `trial_success`
- `trial_failure`

These events make functional scoring possible without relying only on frame-by-
frame intent accuracy.

## Functional Score

The first functional score can measure:

- Time to target
- Wrong-direction command count
- Rest stability near target
- Failure rate per intent

## Acceptance Criteria

- The virtual gripper can run from a replayed session.
- The same control output can later drive a physical gripper adapter.
- Functional scores are saved alongside classifier metrics.
- The UI makes current intent, confidence, and drift score visible.
