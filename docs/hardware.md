# Hardware Plan

## Minimal Viable Research System

| Part | Qty | Purpose |
|---|---:|---|
| Teensy 4.1 | 1 | deterministic acquisition and control |
| MyoWare 2.0 EMG sensors | 4 | safe surface-EMG prototyping |
| Ag/AgCl electrodes and leads | 1 kit | repeatable sessions |
| BNO085 IMU breakout | 1 | forearm orientation and motion context |
| Dynamixel XL330 or similar servo | 1 | one-degree-of-freedom gripper |
| Load cell + HX711/ADC | 1 | grip force and task-success signal |
| 3D printed armband, armrest, gripper | 1 set | repeatable placement and tasks |
| Emergency stop and power hardware | 1 set | safety |

## Build Sequence

1. Software simulator and replay pipeline
2. EMG acquisition board and timestamp tests
3. Indexed armband or placement jig
4. Virtual gripper task
5. Physical one-motor gripper
6. Force/task-success logging

## Firmware Log Contract

Before live serial capture, firmware can be tested by dumping JSON lines:

```json
{"seq": 1, "channels": [0.02, -0.01, 0.04, 0.01]}
{"seq": 2, "channels": [0.03, -0.02, 0.05, 0.00]}
```

Then normalize the dump:

```bash
driftproof capture-file firmware_dump.jsonl --out data/raw/session.jsonl
```

This creates a replay-compatible DriftProof session. Sequence gaps are counted
as dropped samples, so firmware timing issues are visible before model work.
