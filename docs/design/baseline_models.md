# Baseline Models

The first classifier is a baseline, not the final research contribution. Its
job is to make drift measurable.

## MVP Model

Use a classical supervised classifier trained on calibration windows:

- Logistic regression or linear SVM for the first reported baseline.
- Random forest as a secondary non-linear baseline.
- Majority-class predictor as a sanity check.

The current package uses a simple baseline path that can be swapped behind the
same train/predict interface.

## Training Data

Training windows come from the stable calibration phase. Evaluation must report
results separately for:

- Clean calibration-like data
- Drifted data
- Any adapted run

## Metrics

- Accuracy
- Macro F1
- Confusion matrix
- Per-intent failure rate
- Drift score distribution
- Latency per prediction later, once live prediction timing exists

Accuracy alone is not enough. A controller can have acceptable average accuracy
while still failing badly on one intent.

## Scorecard Artifact

The evaluator can write a JSON scorecard:

```bash
driftproof evaluate data/demo/session.jsonl --report reports/demo_scorecard.json
```

The JSON report includes:

- `schema_version`
- source session path
- evaluation config
- baseline and drifted splits
- accuracy and macro F1
- confusion matrix
- per-intent failure rate
- mean drift score for the drifted split

## Acceptance Criteria

- Baseline training is reproducible with a fixed seed.
- Evaluation reports clean and drifted performance separately.
- At least one test proves that synthetic drift lowers baseline performance.
- Evaluation can write a machine-readable scorecard.
- Model objects can be saved and reloaded without changing predictions later.
