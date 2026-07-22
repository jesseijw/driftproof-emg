# Experiment Manifests

Experiment manifests make DriftProof runs repeatable. Instead of remembering a
terminal command, save the session path, evaluator settings, adaptation settings,
and report path in a small JSON file.

## Example

See [examples/demo_experiment.json](../examples/demo_experiment.json).

```json
{
  "name": "demo_synthetic_adaptation",
  "session_path": "../data/demo/session.jsonl",
  "report_path": "../reports/demo_manifest_scorecard.json",
  "evaluation": {
    "window_ms": 200,
    "step_ms": 100,
    "sample_rate_hz": 1000
  },
  "adaptation": {
    "enabled": true,
    "confidence_threshold": 0.6,
    "momentum": 0.02
  }
}
```

Run it:

```bash
driftproof run-manifest examples/demo_experiment.json
```

The output report embeds the manifest under `experiment`, so a saved scorecard
contains the configuration that produced it.

## Fields

- `name`: short run name.
- `session_path`: replayable DriftProof JSONL session.
- `report_path`: JSON scorecard output path.
- `evaluation.window_ms`: window length in milliseconds.
- `evaluation.step_ms`: window step in milliseconds.
- `evaluation.sample_rate_hz`: sample rate used for window sizing.
- `adaptation.enabled`: whether to compare normalization adaptation.
- `adaptation.confidence_threshold`: minimum confidence before adaptation update.
- `adaptation.momentum`: runtime normalization update rate.
- `notes`: optional free-text context.

Relative paths are resolved relative to the manifest file.

## Good Practice

- Commit manifests for important synthetic, replay, and pilot runs.
- Do not commit raw participant data.
- Keep generated reports under `reports/`; they are ignored by git by default.
- Use one manifest per experiment condition when comparing settings.
