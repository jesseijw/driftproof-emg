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
