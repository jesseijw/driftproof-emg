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

- Mean target-position error
- Final target-position error
- Wrong-direction command count
- Rest stability near target
- Failure rate per intent

In the current implementation, the evaluation report feeds predicted window
intents into the virtual gripper and compares the resulting scalar gripper
position against the target intent implied by the replay label. `open` maps to
position `1.0`, `close` maps to `0.0`, and `rest` maps to the neutral starting
position.

The JSON report includes a `functional` section with baseline and drifted
scores:

```json
{
  "functional": {
    "baseline": {
      "n_steps": 120,
      "mean_target_error": 0.12,
      "final_target_error": 0.0,
      "wrong_direction_commands": 0,
      "rest_motion": 0.0
    }
  }
}
```

## Acceptance Criteria

- The virtual gripper can run from a replayed session: implemented in reports.
- The same control output can later drive a physical gripper adapter.
- Functional scores are saved alongside classifier metrics: implemented.
- The UI makes current intent, confidence, and drift score visible.
