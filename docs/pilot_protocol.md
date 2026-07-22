# Pilot Protocol

This protocol is for early characterization sessions. It is not a clinical
protocol and should not be used for human-subject research without the required
review, consent process, and safety checks.

## Generated Task Schedule

Create a balanced rest/open/close schedule:

```bash
driftproof make-protocol \
  --out protocols/calibration.jsonl \
  --session-id pilot_001_calibration \
  --phase calibration \
  --repetitions-per-label 5 \
  --cue-s 2.0 \
  --rest-s 1.0 \
  --seed 42
```

The output is JSONL with:

- `protocol_metadata`
- `trial_spec`
- `task_event`

Each trial emits a target event at cue start and a `target_rest` event at cue
end. The schedule is deterministic for a fixed seed.

## Session Skeleton

1. Confirm participant code and session id.
2. Confirm hardware is disconnected from motors unless motor testing is planned.
3. Record a baseline calibration protocol.
4. Apply one perturbation condition.
5. Record the same task protocol after perturbation.
6. Save raw session JSONL and experiment manifest.
7. Run evaluation and store the report.

## Perturbation Notes

Track one perturbation per session where possible:

- `shift_5mm`
- `shift_10mm`
- `rotate_10deg`
- `rotate_20deg`
- `redon`
- `posture_change`
- `fatigue_light`

## Safety Notes

- Stop immediately if the participant reports discomfort.
- Do not connect the physical gripper until virtual replay behavior is stable.
- Keep raw identifiable metadata out of git.
- Store consent records outside this repository.
