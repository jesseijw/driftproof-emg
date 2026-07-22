# Contributing

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
```

## Checks

Run these before committing:

```bash
python3 -m pytest
python3 -m ruff check .
driftproof simulate --out data/demo/session.jsonl --seconds 24 --drift-after-s 12
driftproof evaluate data/demo/session.jsonl
```

## Branch Workflow

Use short feature branches:

```bash
git checkout -b feature/session-replay
```

Keep changes focused. Documentation updates are useful when they clarify a data
contract, experiment, or acceptance criterion.

## Coding Rules

- Keep hardware-specific code inside `driftproof/acquisition`.
- Keep replay and live paths compatible.
- Add tests for data contracts and metrics.
- Avoid hidden global state in models, drift detectors, and adaptation logic.
- Prefer explicit experiment outputs over notebook-only results.
