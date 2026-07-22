# Product Requirements

## Primary Objective

Maintain reliable prosthetic intent control despite electrode movement,
re-donning, fatigue, and day-to-day physiological drift.

## MVP

The MVP is a software-first research instrument:

- Generate or ingest synchronized multi-channel EMG-like streams.
- Window and preprocess data reproducibly.
- Extract classical EMG features.
- Train baseline intent models.
- Compute signal-quality, uncertainty, and drift scores.
- Evaluate performance before and after simulated drift.
- Write reports that distinguish offline accuracy from functional control.

## Non-Goals For MVP

- Full robotic hand mechanics
- Human-subject study management
- Patent claims
- Clinical safety certification
- Real-time embedded firmware

## Success Criteria

- Reproducible sessions from raw records.
- At least three baseline algorithms.
- Drift detector evaluated against performance failure.
- Clear separation between development data and final evaluation data.
- Participant-level analysis plan ready before real study claims.
