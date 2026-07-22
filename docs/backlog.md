# Backlog

This backlog is ordered for building a credible research platform before adding
hardware complexity.

## M0: Repo Foundation

- Package scaffold
- Tests and linting
- Synthetic session generator
- Evaluation CLI

Done when: `pytest`, `ruff`, simulation, and evaluation all run locally.

## M1: Session Replay

- Strict JSONL parser with line-numbered errors
- Replay reader for saved sessions
- Session metadata record
- Golden replay fixture

Done when: a saved session can be replayed into the same evaluation path as
synthetic generation.

## M2: Baseline Scorecard

- Macro F1: implemented
- Confusion matrix: implemented
- Per-intent failure rates: implemented
- Clean vs drifted split: implemented
- JSON report output: implemented
- CSV report output: later if needed

Done when: every experiment produces a machine-readable scorecard.

## M3: Virtual Gripper

- Gripper state simulator: implemented
- Intent-to-command controller: implemented as direct intent commands
- Trial target generator
- Functional score: implemented in evaluation reports

Done when: replayed predictions can drive the virtual gripper and produce task
success metrics.

## M4: Drift Detector Calibration

- Calibration distribution fitting
- Rolling drift scores
- Threshold sweep
- Failure correlation plots

Done when: drift threshold choices can be explained against functional failure,
not only against synthetic distribution shift.

## M5: Adaptation Experiments

- Normalization-only adaptation
- No-adaptation control runs
- Adaptation event logs
- Before/after scorecards

Done when: the same replay can be evaluated with adaptation enabled and
disabled.

## M6: Hardware Capture

- Serial acquisition adapter
- Device metadata
- Dropped-sample detection
- Raw session saving

Done when: a live hardware session creates a valid replay file.

## M7: Human Pilot Protocol

- Consent and safety review materials
- Calibration task script
- Perturbation protocol
- Analysis plan

Done when: pilot sessions can be run consistently and analyzed reproducibly.

## M8: Physical Gripper Demo

- Motor adapter
- Operator stop
- Conservative command limits
- Replay-compatible command logs

Done when: the physical gripper consumes the same command interface as the
virtual gripper.

## Issue Templates

Feature:

- Problem
- Proposed behavior
- Data contract impact
- Tests

Experiment:

- Hypothesis
- Dataset/session inputs
- Metrics
- Expected decision

Hardware:

- Device
- Firmware assumptions
- Safety considerations
- Replay artifact produced
