# Drift Detection

Drift detection estimates whether the current EMG feature distribution has
moved away from calibration. It is separate from intent classification.

## MVP Detector

Use Mahalanobis distance from the calibration feature distribution:

```text
drift_score = sqrt((x - mean)^T covariance^-1 (x - mean))
```

The detector should produce a continuous score. Thresholds can be tuned later
against functional failure.

## Data Flow

1. Fit calibration feature mean and covariance.
2. Score each new feature vector.
3. Aggregate scores over a short rolling window.
4. Report the score alongside prediction confidence.

## Interpretation

- Low score: feature vector looks calibration-like.
- High score: feature vector is distributionally unusual.
- High score does not prove the model is wrong.
- Low score does not prove the model is right.

The score is useful because it can warn the operator or adaptation layer before
accuracy labels are available.

## Acceptance Criteria

- Calibration features have lower average drift score than drifted features in
  synthetic replay.
- Singular covariance cases are handled with regularization.
- Drift scores are logged with timestamps.
- Drift logic does not mutate classifier state.
