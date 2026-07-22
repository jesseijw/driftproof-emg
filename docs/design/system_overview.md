# System Overview

DriftProof is a research platform for testing whether EMG intent control can
remain usable when signal statistics drift from electrode shift, fatigue,
posture, sweat, or day-to-day setup differences.

## Data Flow

```text
EMG source
  -> timestamped samples
  -> windowing
  -> feature extraction
  -> intent model
  -> drift score
  -> optional adaptation
  -> virtual or physical gripper command
  -> evaluation metrics
```

The same flow must work for synthetic data, replayed study data, and live
hardware. That keeps experiments reproducible and prevents the hardware path
from becoming a separate one-off demo.

## Module Boundaries

- `acquisition`: reads live or replayed streams and emits timestamped records.
- `preprocessing`: windows samples and performs normalization or filtering.
- `features`: turns windows into compact model inputs.
- `models`: predicts user intent from features.
- `drift`: estimates whether the current feature distribution has shifted.
- `adaptation`: updates normalization or model state under explicit guards.
- `evaluation`: produces scorecards for accuracy, drift, latency, and failure.

## MVP Behavior

The MVP proves the research loop without physical hardware:

1. Generate or replay four-channel EMG-like data.
2. Train a baseline intent classifier on clean calibration windows.
3. Evaluate the classifier before and after drift.
4. Report intent accuracy and drift score.
5. Save session data in a format that can later be produced by hardware.

## Acceptance Criteria

- A new developer can run simulation, evaluation, linting, and tests locally.
- A session file can be replayed without needing live hardware.
- Evaluation reports separate classifier performance from drift magnitude.
- Hardware integration can follow the documented streaming contract.

## Non-goals

- Clinical claims.
- Closed-loop force control.
- Implantable or medical-grade hardware.
- Automatic model updates without observable safety guards.
