# Adaptation Strategy

Adaptation is the risky part of the project. The first implementation should
adapt normalization statistics before adapting model weights.

## MVP Strategy

Normalization-only adaptation:

1. Keep calibration normalization statistics.
2. Track recent unlabeled feature statistics during confident operation.
3. Blend recent statistics slowly into runtime normalization.
4. Never overwrite the original calibration baseline.

This tests whether lightweight adaptation can recover performance under drift
without turning the system into an untraceable learner.

## Current Experiment

The evaluator now runs an optional normalization-only adaptation comparison on
the drifted replay split:

```bash
driftproof evaluate data/demo/session.jsonl --report reports/demo_scorecard.json
```

The report includes:

- `splits.drifted`: fixed baseline model without adaptation.
- `splits.drifted_adapted`: same model with runtime feature normalization.
- `functional.drifted_adapted`: virtual-gripper score for adapted predictions.
- `adaptation`: strategy name, confidence threshold, momentum, and update log.

The model weights are not changed. Runtime feature statistics are blended only
after confident predictions, and the original calibration statistics remain the
reference.

## Safety Rules

- Do not adapt during low-confidence predictions.
- Do not adapt during missing or saturated signal windows.
- Do not adapt while the task label is unknown in supervised experiments.
- Keep a replayable log of every adaptation update.
- Provide a switch to run the same session with adaptation disabled.

## Later Strategies

- Supervised recalibration prompts.
- Confidence-gated pseudo-label updates.
- Domain-adversarial feature alignment.
- Per-user personalization across sessions.

## Acceptance Criteria

- Evaluation can compare no-adaptation and adaptation runs on the same session.
- Adaptation state is serializable through the JSON report.
- Adaptation updates are visible in logs.
- The original calibration model remains recoverable.
