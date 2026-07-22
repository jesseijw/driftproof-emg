# Decision Log

## 2026-07-22: Build Simulation First

Decision: implement synthetic generation, replay, and evaluation before live
hardware.

Reason: the research question needs repeatable drift experiments. Hardware is
valuable only after the pipeline can measure failure and recovery.

## 2026-07-22: Use JSONL Session Files

Decision: store sessions as newline-delimited JSON records.

Reason: JSONL is easy to stream, inspect, replay, and version in small fixtures.

## 2026-07-22: Start With Classical Baselines

Decision: begin with simple EMG features and classical classifiers.

Reason: early research value comes from measuring drift and adaptation, not from
maximizing model complexity.

## 2026-07-22: Keep Drift Score Separate From Accuracy

Decision: report distribution shift separately from intent correctness.

Reason: a high drift score is a warning signal, not a label that the prediction
is wrong.

## 2026-07-22: Build Virtual Gripper Before Physical Gripper

Decision: use a simulated one-degree-of-freedom gripper before motor hardware.

Reason: the virtual gripper exercises control and functional scoring without
physical safety risk.
