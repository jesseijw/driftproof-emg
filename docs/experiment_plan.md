# Experiment Plan

Use [experiment manifests](experiment_manifests.md) for any run that should be
repeatable. A manifest stores the session path, evaluator settings, adaptation
settings, and report path.

## Phase A: Instrument Validation

- Measure noise floor and saturation frequency.
- Verify timestamp jitter.
- Confirm online/offline preprocessing equivalence.
- Validate indexed armband displacement.
- Test emergency stop and command limits before motor experiments.

## Phase B: Pilot Characterization

Small pilot cohort. The goal is protocol design, not headline claims.

Candidate perturbations:

- 5 mm and 10 mm longitudinal displacement
- 10 and 20 degree rotation
- removal and re-donning
- altered forearm posture
- mild fatigue protocol
- separate-day session

## Phase C: Controlled Comparison

Repeated-measures design with 12-20 participants if collaboration and approval
allow it.

Algorithms:

- no adaptation
- full supervised recalibration
- normalization-only update
- profile retrieval
- prototype update
- weak-label task adaptation

Primary endpoint:

Functional-control score after fixed perturbation and fixed adaptation budget.
