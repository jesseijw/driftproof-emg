# Glossary

EMG: Electrical activity measured from muscle activation.

Intent: The action the user is trying to command, such as `open`, `close`, or
`rest`.

Calibration: A short labeled session used to estimate normalization statistics
and train the baseline model.

Drift: A change in EMG signal statistics over time or across setup conditions.

Functional failure: A task-level failure of the controller, such as moving the
gripper in the wrong direction or failing to reach the target.

Window: A short time slice of samples used to compute features.

Feature: A numeric summary of a window, such as RMS or waveform length.

Drift score: A continuous measure of how unusual a feature vector looks relative
to calibration.

Adaptation: A controlled update to normalization or model state after
calibration.

Weak label: A noisy label inferred from context or confidence rather than a
direct ground-truth instruction.

Replay: Running saved session data through the pipeline again to reproduce an
experiment.

Virtual gripper: A one-degree-of-freedom simulated gripper with a scalar
position from `0.0` closed to `1.0` open.

Functional score: A task-control metric computed from gripper behavior, such as
target-position error or wrong-direction commands.
