# Architecture

DriftProof is split into layers so each piece can be tested without hardware.

## Layers

1. **Acquisition**
   Timestamped EMG, IMU, device-state, and task-event records.

2. **Preprocessing**
   Band-pass or high-pass filtering, optional notch filtering, windowing,
   normalization, artifact detection, and signal-quality scoring.

3. **Intent Estimation**
   Classical baselines first: logistic regression, LDA, SVM, random forest, and
   ridge regression for proportional control.

4. **Drift And Uncertainty**
   Latent-distance scores, covariance shift, entropy trends, conformal sets, and
   calibration against real task failure.

5. **Adaptation**
   Normalization updates, profile retrieval, prototype updates, latent alignment,
   weak-label task adaptation, and rollback.

6. **Interface**
   Virtual gripper first, one-motor physical gripper later.

## Design Rule

The software should always support replay. Every online transform must have an
offline equivalent so an experiment can be regenerated from raw streams.
