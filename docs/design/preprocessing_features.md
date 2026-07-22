# Preprocessing and Features

The first feature pipeline should be boring and defensible. Classical EMG
features make early failures easy to understand before adding deep models.

## MVP Defaults

- Channels: 4
- Sampling rate: 1000 Hz
- Window length: 200 ms
- Window step: 100 ms
- Labels: `rest`, `open`, `close`

## Current Pipeline

1. Read timestamped samples.
2. Group samples into overlapping windows.
3. Normalize each channel with calibration statistics.
4. Extract per-channel features.
5. Concatenate features into one model vector.

## Feature Set

For each channel:

- Mean absolute value
- Root mean square
- Waveform length
- Zero crossings

This gives a compact vector that is fast enough for live control and transparent
enough for debugging.

## Signal Quality Checks

Each window should eventually include quality metadata:

- Missing sample ratio
- Saturation ratio
- Flatline detection
- Per-channel amplitude range

Quality metadata should not silently change labels. It should explain when a
window is excluded or marked low confidence.

## Acceptance Criteria

- Feature extraction is deterministic for a saved session.
- Window timestamps are derived from source sample timestamps.
- Tests cover feature shape, empty input behavior, and drifted replay behavior.
- Feature code is independent of hardware transport.
