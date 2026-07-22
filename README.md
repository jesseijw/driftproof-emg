# DriftProof EMG Controller

A low-cost, self-adapting prosthetic-control research platform for studying
myoelectric drift.

The core research question is whether a prosthetic controller can keep reliable
intent control when electrode placement, fatigue, posture, and day-to-day EMG
statistics change.

## Prototype Scope

- Four-channel EMG armband
- Optional IMU context
- Virtual one-degree-of-freedom gripper first
- Physical one-motor gripper later
- Reproducible dataset and evaluation harness
- Baseline, drift-detection, and adaptation algorithms

## Repository Layout

```text
driftproof/
  acquisition/      streaming protocol and synthetic data sources
  preprocessing/    filtering, windowing, normalization, signal quality
  features/         classical EMG feature extraction
  models/           baseline intent estimators
  drift/            distribution shift and uncertainty metrics
  adaptation/       guarded model update strategies
  evaluation/       metrics and experiment scorecards
  cli.py            command-line entry point
docs/
  index.md
  architecture.md
  data_schema.md
  hardware.md
  experiment_plan.md
  roadmap.md
  backlog.md
  decision_log.md
  glossary.md
  design/          builder-facing component specs
tests/
```

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
driftproof simulate --out data/demo/session.jsonl --seconds 24 --drift-after-s 12
driftproof evaluate data/demo/session.jsonl --report reports/demo_scorecard.json
python3 -m pytest
```

The report compares the fixed baseline against a normalization-adapted drifted
run. Use `--no-adaptation` to write only the fixed-baseline evaluation.

Firmware JSONL dumps can be normalized into replayable sessions:

```bash
driftproof capture-file firmware_dump.jsonl --out data/raw/session.jsonl
```

Repeatable runs can be stored as experiment manifests:

```bash
driftproof run-manifest examples/demo_experiment.json
```

## Builder Docs

Start with [docs/index.md](docs/index.md). It links the design specs for the
streaming protocol, preprocessing, baseline models, drift detection, adaptation,
virtual gripper, and hardware interface.

## Current Build Strategy

This starts simulation-first. The first milestone is a reliable software
pipeline that can ingest timestamped EMG-like streams, preprocess them, extract
features, train baseline models, and report drift-sensitive metrics. Firmware
and gripper integration are intentionally deferred until the software contracts
are stable.

## Research Outputs

- Open-source software instrument
- Longitudinal EMG dataset schema
- Baseline classifiers and regressors
- Drift detector calibrated against functional failure
- Adaptation experiments with safety guards
- Study protocol and statistical analysis plan
